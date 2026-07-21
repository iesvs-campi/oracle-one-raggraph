"""Configuración centralizada del proyecto RAG."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
POLICIES_DIR = PROJECT_ROOT / "data" / "policies"
FAISS_INDEX_DIR = PROJECT_ROOT / "data" / "faiss_index"

# LLM
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_MODEL = "gemini-3.1-flash-lite"
LLM_TEMPERATURE = 0.1

# Embeddings
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
EMBEDDING_MODEL = "voyage-4"

# RAG
CHUNK_SIZE = 800
CHUNK_OVERLAP = 200
RETRIEVER_K = 8
