import chromadb
from chromadb.utils import embedding_functions
from typing import Any
from pathlib import Path

from app.core.config import settings


chroma_client = None
collection = None
embedding_function = None


def _get_collection():
    """Lazily initialize the Chroma collection to avoid blocking startup."""
    global chroma_client, collection, embedding_function

    if collection is not None:
        return collection

    chroma_client = chromadb.PersistentClient(path=str(Path(getattr(settings, "RAG_DB_DIRECTORY", "medigenie_rag_db"))))

    try:
        if embedding_function is None:
            embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
    except Exception:
        embedding_function = None

    if embedding_function is None:
        collection = chroma_client.get_or_create_collection(name="clinical_guidelines")
    else:
        collection = chroma_client.get_or_create_collection(
            name="clinical_guidelines",
            embedding_function=embedding_function,
        )

    return collection


def seed_sample_guidelines():
    """Seed sample clinical guidelines into ChromaDB if empty."""
    current_collection = _get_collection()
    if current_collection.count() == 0:
        current_collection.add(
            documents=[
                "IDSA/ATS CAP Guidelines: First-line outpatient treatment for Community-Acquired Pneumonia without comorbidities is Amoxicillin 1g TID or Doxycycline 100mg BID. With comorbidities, use Amoxicillin/clavulanate plus a macrolide or Respiratory Fluoroquinolone.",
                "ACC/AHA Hypertension Guidelines: First-line pharmacotherapy includes thiazide diuretics, CCBs, and ACE inhibitors or ARBs. Monitor potassium and renal function.",
                "FDA Safety Warning: Fluoroquinolones carry black box warnings for tendonitis and tendon rupture. Avoid as first-line in uncomplicated infections if alternatives exist.",
                "WHO Diabetes Management Guidelines: Target HbA1c is below 7.0% for most non-pregnant adults. First-line glucose-lowering therapy is Metformin along with lifestyle interventions."
            ],
            metadatas=[
                {"source": "IDSA/ATS Guidelines", "category": "Pneumonia"},
                {"source": "ACC/AHA Guidelines", "category": "Hypertension"},
                {"source": "FDA Safety Alerts", "category": "Drug Safety"},
                {"source": "WHO Guidelines", "category": "Diabetes"}
            ],
            ids=["guideline_cap_01", "guideline_htn_01", "guideline_fda_01", "guideline_dia_01"]
        )
        from app.core.logging import get_logger
        get_logger(__name__).info("Vector DB initialized with clinical practice guidelines")


def query_knowledge_base(query_text: str, n_results: int = 2) -> list[dict[str, Any]]:
    """Retrieve relevant guideline snippets and metadata based on semantic similarity."""
    current_collection = _get_collection()
    results = current_collection.query(
        query_texts=[query_text],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    if not results or "documents" not in results or len(results["documents"]) == 0:
        return []

    unique_items: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str]] = set()
    documents = results["documents"][0]
    metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []
    distances = results.get("distances", [[]])[0] if results.get("distances") else []

    for idx, document in enumerate(documents):
        metadata = metadatas[idx] if idx < len(metadatas) else {}
        distance = distances[idx] if idx < len(distances) else None
        similarity_score = None

        if isinstance(distance, (int, float)):
            similarity_score = 1.0 / (1.0 + distance)

        document_text = str(document or "").strip()
        identifier = metadata.get("id") or metadata.get("source") or ""
        key = (str(identifier), document_text)
        if not document_text or key in seen_keys:
            continue

        seen_keys.add(key)
        unique_items.append({
            "document": document_text,
            "metadata": metadata or {},
            "distance": distance,
            "similarity_score": similarity_score,
        })

    unique_items.sort(
        key=lambda item: item.get("similarity_score") if isinstance(item.get("similarity_score"), (int, float)) else -1.0,
        reverse=True,
    )

    return unique_items


def ingest_documents(documents: list[str], metadatas: list[dict] | None = None, ids: list[str] | None = None) -> dict:
    """Add documents to the clinical_guidelines collection.

    documents: list of document text
    metadatas: optional list of metadata dicts matching documents
    ids: optional list of ids for the documents

    Returns a summary dict with counts and any errors.
    """
    current_collection = _get_collection()
    try:
        if metadatas is None:
            metadatas = [{} for _ in documents]
        if ids is None:
            # create generated ids
            ids = [f"doc_{i}_{abs(hash(doc)) % 100000}" for i, doc in enumerate(documents)]

        current_collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

        return {
            "added": len(documents),
            "ids": ids,
        }
    except Exception as exc:
        return {
            "added": 0,
            "error": str(exc),
        }