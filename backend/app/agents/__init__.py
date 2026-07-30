from app.db.session import engine
from app.models.models import Base
from app.core.rag import seed_sample_guidelines

def init_db():
    print("Creating relational database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Relational Database tables ready!")
    
    print("Initializing RAG Vector Storage...")
    seed_sample_guidelines()

if __name__ == "__main__":
    init_db()