from typing import TypedDict

class GraphState(TypedDict):
    selected_table: str
    user_question: str
    user_question_eval: str
    nl2sql_answer: str
    final_answer: str