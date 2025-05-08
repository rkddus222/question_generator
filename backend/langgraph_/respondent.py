from backend.llm_models.types import GraphState
from backend.llm_models.model import llm
from .utils import load_prompt

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def respondent(state: GraphState) -> GraphState:
    user_question = state["user_question"]
    nl2sql_answer = state["nl2sql_answer"]
    final_answer = generate_respondent(user_question, nl2sql_answer)

    state.update({"final_answer": final_answer})
    print("DEBUG - question_analyze: 시작", state)
    return state


def generate_respondent(user_question: str, nl2sql_answer: str) -> str:
    output_parser = StrOutputParser()

    # 2. 프롬프트 템플릿 로드
    prompt_template = load_prompt("backend/prompts/generate_respondent.prompt")
    base_prompt = prompt_template.format(
        nl2sql_answer=nl2sql_answer
    )

    prompt = ChatPromptTemplate.from_template(base_prompt)
    chain = prompt | llm | output_parser
    final_answer = chain.invoke({"user_question": user_question})

    return final_answer