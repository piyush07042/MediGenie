import chromadb
from chromadb.utils import embedding_functions
from typing import Any


chroma_client = None
collection = None
embedding_function = None


def _get_collection():
    """Lazily initialize the Chroma collection to avoid blocking startup."""
    global chroma_client, collection, embedding_function

    if collection is not None:
        return collection

    chroma_client = chromadb.PersistentClient(path="./medigenie_rag_db")

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
        print("✅ Vector DB initialized with clinical practice guidelines!")


def query_knowledge_base(query_text: str, n_results: int = 2) -> list[dict[str, Any]]:
    """Retrieve relevant guideline snippets and metadata based on semantic similarity."""
    current_collection = _get_collection()
    results = current_collection.query(
        query_texts=[query_text],
        n_results=n_results,
        include=["documents", "metadatas"],
    )
    if results and "documents" in results and len(results["documents"]) > 0:
        documents = []
        for idx, document in enumerate(results["documents"][0]):
            metadata = {}
            if "metadatas" in results and len(results["metadatas"]) > 0:
                metadata = results["metadatas"][0][idx] if idx < len(results["metadatas"][0]) else {}
            documents.append({
                "document": document,
                "metadata": metadata,
            })
        return documents
    return []


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