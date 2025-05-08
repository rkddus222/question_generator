import random
import json
import os

from backend.llm_models.types import GraphState
from .utils import load_prompt
from backend.llm_models.model import llm

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def generate(state: GraphState) -> GraphState:
    print("DEBUG - 질문 생성 시작", state)
    selected_table = state.get("selected_table", "")
    user_question_eval = generate_user_question(selected_table)
    print("DEBUG - 질문 생성 결과", user_question_eval)

    state.update({"user_question_eval": user_question_eval})
    return state

def generate_user_question(selected_table: str) -> str:
    # 1. 질문 예제 JSON 파일 경로 구성 및 로드
    file_path = f"backend/prompts/questions/{selected_table}.json"
    if not os.path.exists(file_path):
        return f"[ERROR] 해당 테이블에 대한 질의 샘플 파일이 없습니다: {file_path}"

    with open(file_path, "r", encoding="utf-8") as f:
        examples = json.load(f)

    question_list = [item["question"] for item in examples if "question" in item]
    if len(question_list) < 5:
        return "[ERROR] 예시 질문이 5개 미만입니다."

    selected_questions = random.sample(question_list, 5)
    print(f"selected_questions: {selected_questions}")
    examples_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(selected_questions)])

    # 2. 프롬프트 템플릿 로드
    prompt_template = load_prompt("backend/prompts/generate_question.prompt")
    base_prompt = prompt_template.format(
        examples=examples_text
    )
    prompt = ChatPromptTemplate.from_template(base_prompt)

    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser

    return chain.invoke({"examples": examples_text})