"""Script para convertir documentos de políticas y crear el índice FAISS.

Pipeline: Docling (conversión multi-formato) → limpieza → chunking → embeddings → FAISS

Uso:
    python scripts/index_policies.py
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports de src.*
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import re
import unicodedata
from docling.document_converter import DocumentConverter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from src.utils.tools import get_embeddings
from src.config import POLICIES_DIR, FAISS_INDEX_DIR, CHUNK_SIZE, CHUNK_OVERLAP

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".html", ".htm", ".md", ".txt"}


def convert_documents(policies_dir: Path) -> list[dict]:
    """Convierte todos los documentos de políticas a texto plano con Docling.

    Args:
        policies_dir: Ruta al directorio con los documentos de políticas.

    Returns:
        Lista de dicts con 'content', 'source' y 'policy_type' por cada documento.
    """
    converter = DocumentConverter()
    results = []

    for file in sorted(policies_dir.iterdir()):
        if file.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        print(f"  Convirtiendo: {file.name}")
        result = converter.convert(str(file))
        text = result.document.export_to_markdown()

        results.append({
            "content": text,
            "source": file.name,
            "policy_type": _infer_policy_type(file.stem),
        })

    return results


def clean_text(text: str) -> str:
    """Limpia y normaliza el texto convertido por Docling.

    - Normaliza unicode (NFKC)
    - Elimina líneas vacías excesivas
    - Elimina números de página sueltos
    - Elimina headers/footers de paginación
    """
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^(Página|Page)\s+\d+.*$", "", text, flags=re.MULTILINE)
    return text.strip()


def _infer_policy_type(filename: str) -> str:
    """Infiere el tipo de política a partir del nombre del archivo.

    Args:
        filename: Nombre del archivo sin extensión (stem).

    Returns:
        Tipo de política: 'envio', 'reembolso', 'privacidad', 'terminos', o 'general'.
    """
    name = filename.lower().replace("_", " ").replace("-", " ")
    if "envio" in name or "envío" in name:
        return "envio"
    if "reembolso" in name or "devolucion" in name:
        return "reembolso"
    if "privacidad" in name:
        return "privacidad"
    if "terminos" in name or "términos" in name:
        return "terminos"
    return "general"


def index_policies():
    """Pipeline completo de ingestión de documentos de políticas.

    1. Convierte documentos multi-formato a texto plano con Docling
    2. Limpia y normaliza el texto
    3. Divide en chunks con RecursiveCharacterTextSplitter
    4. Genera embeddings con voyage-4
    5. Guarda el índice FAISS en disco
    """
    print("Paso 1: Convirtiendo documentos con Docling...")
    raw_docs = convert_documents(POLICIES_DIR)
    print(f"   {len(raw_docs)} documentos convertidos\n")

    print("Paso 2: Limpiando y creando chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    documents = []
    for doc in raw_docs:
        clean_content = clean_text(doc["content"])
        lc_doc = Document(
            page_content=clean_content,
            metadata={
                "source": doc["source"],
                "policy_type": doc["policy_type"],
            },
        )
        documents.append(lc_doc)

    splits = splitter.split_documents(documents)
    print(f"   {len(documents)} docs → {len(splits)} chunks\n")

    print("Paso 3: Generando embeddings y guardando índice FAISS...")
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(splits, embeddings)

    # Crear directorio si no existe
    FAISS_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(FAISS_INDEX_DIR))
    print(f"Índice FAISS guardado en {FAISS_INDEX_DIR}\n")

    print("Indexación completada exitosamente")
    print(f"   Total chunks indexados: {len(splits)}")


if __name__ == "__main__":
    index_policies()
