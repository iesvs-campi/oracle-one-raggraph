"""Inicialización de embeddings y retriever FAISS."""

from langchain_voyageai import VoyageAIEmbeddings
from langchain_community.vectorstores import FAISS
from src.config import FAISS_INDEX_DIR, VOYAGE_API_KEY, EMBEDDING_MODEL, RETRIEVER_K


def get_embeddings() -> VoyageAIEmbeddings:
    """Retorna el modelo de embeddings Voyage AI voyage-4."""
    return VoyageAIEmbeddings(
        model=EMBEDDING_MODEL,
        voyage_api_key=VOYAGE_API_KEY,
    )


def get_retriever():
    """Carga el índice FAISS desde disco y devuelve un retriever.

    El índice debe haber sido creado previamente con scripts/index_policies.py.

    Returns:
        Un retriever configurado para devolver los k documentos más similares.

    Raises:
        RuntimeError: Si el índice FAISS no existe en disco.
    """
    if not FAISS_INDEX_DIR.exists():
        raise RuntimeError(
            f"No se encontró el índice FAISS en '{FAISS_INDEX_DIR}'. "
            "Ejecuta primero: python scripts/index_policies.py"
        )

    embeddings = get_embeddings()
    vectorstore = FAISS.load_local(
        str(FAISS_INDEX_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )
    return vectorstore.as_retriever(
        search_kwargs={"k": RETRIEVER_K},
    )
