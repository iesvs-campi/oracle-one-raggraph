"""Estado del grafo RAG simple."""

from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage


class State(TypedDict):
    """Estado global compartido por los nodos del grafo.

    Attributes:
        messages: Historial de mensajes (user + AI) con reducer add_messages.
        retrieved_docs: Contenido de los documentos recuperados por FAISS.
    """

    messages: Annotated[list[AnyMessage], add_messages]
    retrieved_docs: list[dict]
