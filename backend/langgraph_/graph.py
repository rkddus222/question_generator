from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from backend.llm_models.types import GraphState
from backend.langgraph_.nl2sql import nl2sql
from backend.langgraph_.respondent import respondent

def make_graph() -> CompiledStateGraph:
    workflow = StateGraph(GraphState)

    workflow.add_node("nl2sql", nl2sql)
    workflow.add_node("respondent", respondent)

    workflow.add_edge("nl2sql", "respondent")
    workflow.add_edge("respondent", END)

    workflow.set_entry_point("nl2sql")

    return workflow.compile()