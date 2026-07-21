"""Nodos del grafo RAG: retrieve y generate."""

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage
from src.utils.state import State
from src.utils.tools import get_retriever
from src.config import LLM_MODEL, LLM_TEMPERATURE

SYSTEM_PROMPT = """Eres un asistente virtual de soporte al cliente de GamaSupra, una tienda e-commerce.
Respondes EXCLUSIVAMENTE en español con tono profesional pero cercano.

Tu ÚNICA función es responder preguntas sobre las políticas de la tienda usando el contexto proporcionado.

Reglas:
- Responde SOLO con información del contexto proporcionado.
- Si el contexto no contiene la respuesta, di: "No encontré información sobre eso en nuestras políticas. ¿Puedo ayudarte con algo más?"
- NO inventes información.
- Sé conciso y directo.
- Si la pregunta no tiene relación con las políticas de la tienda, indica amablemente que solo puedes responder sobre políticas."""


def retrieve(state: State) -> dict:
    """Recupera los documentos más relevantes de FAISS para la consulta del usuario.

    Extrae el último mensaje del usuario, busca en el índice FAISS,
    y retorna los contenidos de los documentos encontrados.
    """
    last_message = state["messages"][-1]
    query = last_message.content

    retriever = get_retriever()
    docs = retriever.invoke(query)

    retrieved_docs = [{"content": doc.page_content, "source": doc.metadata.get("source", "Desconocido")} for doc in docs]
    return {"retrieved_docs": retrieved_docs}


def generate(state: State) -> dict:
    """Genera una respuesta usando Gemini con los documentos recuperados como contexto.

    Construye el prompt con el contexto de los documentos y el historial
    de mensajes, e invoca el LLM para generar la respuesta.
    """
    docs = state.get("retrieved_docs", [])
    context_parts = []
    for doc in docs:
        context_parts.append(f"Fuente: {doc['source']}\nContenido:\n{doc['content']}")
    context = "\n\n---\n\n".join(context_parts) if docs else "No se encontraron documentos relevantes."

    llm = init_chat_model(
        LLM_MODEL,
        model_provider="google_genai",
        temperature=LLM_TEMPERATURE,
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        SystemMessage(content=f"Contexto de las políticas de la tienda:\n\n{context}"),
        *state["messages"],
    ]

    response = llm.invoke(messages)
    return {"messages": [response]}
