import os
import json

from backend.llm_models.types import GraphState
from backend.llm_models.model import llm
from backend.prompts.schema import product_wip_monthly, raw_material_monthly
from .utils import load_prompt

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser
from rapidfuzz import process, fuzz


def nl2sql(state: GraphState) -> GraphState:
    user_question = state["user_question"]
    selected_table = state["selected_table"]
    nl2sql_answer = generate_nl2sql(user_question, selected_table)

    state.update({"nl2sql_answer": nl2sql_answer})
    return state


def generate_nl2sql(user_question: str, selected_table: str) -> str:
    output_parser = StrOutputParser()

    # 프로젝트 루트 기준으로 경로 구성
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

    if selected_table == "PRODUCT_WIP_MONTHLY":
        schema = product_wip_monthly
        prompt_path = os.path.join(project_root, "backend/prompts/product_wip_monthly_nl2sql.prompt")
        fewshot_path = os.path.join(project_root, "backend/prompts/nl2sql/product_wip_monthly.json")
    elif selected_table == "RAW_MATERIAL_MONTHLY":
        schema = raw_material_monthly
        prompt_path = os.path.join(project_root, "backend/prompts/raw_material_monthly_nl2sql.prompt")
        fewshot_path = os.path.join(project_root, "backend/prompts/nl2sql/raw_material_monthly.json")
    else:
        raise ValueError(f"알 수 없는 테이블: {selected_table}")

    few_shot_prompt = []
    try:
        with open(fewshot_path, 'r', encoding='utf-8') as f:
            shots_data = json.load(f)

        questions = [shot['question'] for shot in shots_data]
        matches = process.extract(
            user_question,
            questions,
            scorer=fuzz.token_sort_ratio,
            limit=3
        )

        similar_shot_indices = [questions.index(match[0]) for match in matches]
        similar_shots = [shots_data[idx] for idx in similar_shot_indices]

        for example in reversed(similar_shots):
            few_shot_prompt.append(("human", example["question"]))
            few_shot_prompt.append(("ai", example["answer"]))

    except Exception as e:
        print(f"Error loading or processing few-shot examples: {str(e)}")

    prompt_template = load_prompt(prompt_path)
    base_prompt = prompt_template.format(
        schema=schema
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=base_prompt),
            *few_shot_prompt,
            ("user", user_question)
        ]
    )

    chain = prompt | llm | output_parser

    output = chain.invoke({"user_question": user_question})

    return output