"""API REST para exponer el asistente RAG usando FastAPI."""

import os
import sys

# Agregar la raíz del proyecto al PYTHONPATH para que pueda encontrar el módulo 'src'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.graph import build_graph
from langchain_core.messages import HumanMessage, AIMessage

app = FastAPI(title="GamaSupra Policy RAG API")

# Inicializamos el grafo una sola vez al arrancar la app
rag_graph = build_graph()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Endpoint para enviar el historial de conversación al asistente RAG."""
    
    # Convertir el historial al formato de LangChain
    langchain_messages = []
    for msg in request.messages:
        if msg.role == "user":
            langchain_messages.append(HumanMessage(content=msg.content))
        else:
            langchain_messages.append(AIMessage(content=msg.content))

    initial_state = {"messages": langchain_messages}
    
    # Ejecutar el grafo
    final_state = rag_graph.invoke(initial_state)
    
    # Extraer la respuesta del bot (Gemini puede devolver listas o strings)
    ai_content = final_state["messages"][-1].content
    if isinstance(ai_content, list):
        ai_response = "\n".join([block.get("text", "") for block in ai_content if block.get("type") == "text" or isinstance(block, dict) and "text" in block])
    else:
        ai_response = str(ai_content)
    
    # Extraer las fuentes utilizadas
    # Limpiamos las rutas para que solo muestren el nombre del archivo
    sources = []
    if "retrieved_docs" in final_state:
        for doc in final_state["retrieved_docs"]:
            raw_source = doc.get("source", "Desconocido")
            clean_source = os.path.basename(raw_source) if raw_source else "Desconocido"
            
            # Evitar fuentes duplicadas en la vista final
            if clean_source not in sources:
                sources.append(clean_source)

    return {
        "response": ai_response,
        "sources": sources
    }

# Montar y servir la interfaz HTML en la raíz
# Asumimos que index.html estará en la carpeta 'static'
os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)
