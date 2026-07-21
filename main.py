"""CLI de chat interactivo para consultar políticas del e-commerce.

Uso:
    python main.py

Requisito previo:
    python scripts/index_policies.py  (crear el índice FAISS)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from src.graph import build_graph


def main():
    """Bucle principal del chat: input → grafo RAG → respuesta."""
    graph = build_graph()

    print("=" * 60)
    print("🛒  GamaSupra — Asistente de Políticas")
    print("=" * 60)
    print("Pregunta sobre nuestras políticas de envío, reembolso,")
    print("privacidad o términos de servicio.")
    print("Escribe 'salir' para terminar.\n")

    while True:
        try:
            user_input = input("Tú: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 ¡Hasta luego!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("salir", "exit", "quit"):
            print("\n👋 ¡Hasta luego! Gracias por contactarnos.")
            break

        result = graph.invoke({
            "messages": [{"role": "user", "content": user_input}],
            "retrieved_docs": [],
        })

        ai_message = result["messages"][-1]
        print(f"\n🤖 Bot: {ai_message.content}\n")


if __name__ == "__main__":
    main()
