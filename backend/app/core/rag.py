import chromadb
from chromadb.utils import embedding_functions

# Initialize persistent ChromaDB storage inside the backend directory
chroma_client = chromadb.PersistentClient(path="./medigenie_rag_db")

# Local embedding model using Sentence Transformers
ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Get or create guidelines collection
collection = chroma_client.get_or_create_collection(
    name="clinical_guidelines", 
    embedding_function=ef
)

def seed_sample_guidelines():
    """Seeds sample clinical guidelines into ChromaDB if empty."""
    if collection.count() == 0:
        collection.add(
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

def query_knowledge_base(query_text: str, n_results: int = 2) -> list:
    """Retrieves relevant guideline snippets based on semantic similarity."""
    results = collection.query(query_texts=[query_text], n_results=n_results)
    if results and "documents" in results and len(results["documents"]) > 0:
        return results["documents"][0]
    return []