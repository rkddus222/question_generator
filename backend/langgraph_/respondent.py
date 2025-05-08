from backend.llm_models.types import GraphState
from backend.llm_models.model import llm
from .utils import load_prompt

import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser
from rapidfuzz import process, fuzz

def respondent(state: GraphState) -> GraphState:
    user_question = state["user_question"]
    nl2sql_answer = state["nl2sql_answer"]
    final_answer = generate_respondent(user_question, nl2sql_answer)

    state.update({"final_answer": final_answer})
    print("DEBUG - question_analyze: 시작", state)
    return state


def generate_respondent(user_question: str, nl2sql_answer: str) -> str:
    output_parser = StrOutputParser()

    fewshot_path = "backend/prompts/respondent/respondent.json"
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

    # 2. 프롬프트 템플릿 로드
    prompt_template = load_prompt("backend/prompts/generate_respondent.prompt")
    base_prompt = prompt_template.format(
        nl2sql_answer=nl2sql_answer
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=base_prompt),
            *few_shot_prompt,
            ("user", user_question)
        ]
    )
    chain = prompt | llm | output_parser
    final_answer = chain.invoke({"user_question": user_question})

    return final_answer