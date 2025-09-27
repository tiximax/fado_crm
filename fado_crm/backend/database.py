# FADO CRM - Database Connection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os

# Database URL - SQLite for demo or PostgreSQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fado_crm.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get database session
def get_db():
    """Get database session for FastAPI dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database ready!")

# Drop all tables (use with caution!)
def drop_tables():
    """WARNING: Drop all tables"""
    print("WARNING: Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Database reset!")

if __name__ == "__main__":
    create_tables()