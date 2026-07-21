"""Grafo LangGraph para el sistema RAG simple."""

from langgraph.graph import StateGraph, START, END
from src.utils.state import State
from src.utils.nodes import retrieve, generate


def build_graph():
    """Construye y compila el grafo RAG simple.

    Flujo: START → retrieve → generate → END
    Cada invocación es independiente.
    """
    builder = StateGraph(State)

    builder.add_node("retrieve", retrieve)
    builder.add_node("generate", generate)

    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "generate")
    builder.add_edge("generate", END)

    return builder.compile()
