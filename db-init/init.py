import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configurations
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"  # Connect to default database first
NEW_DB_NAME = "ssd_1b"
Base = declarative_base()

# Define the ImageRecord model (as previously described)
class ImageRecord(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String, index=True)
    negative_prompt = Column(String, index=True)
    image_path = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

def create_database(engine, db_name):
    """
    Creates a new database.
    """
    conn = engine.connect()
    conn.execute(f"COMMIT")  # Commit any pending transaction
    conn.execute(f"CREATE DATABASE {db_name}")
    conn.close()
    print(f"Database {db_name} created successfully!")

def init_db():
    """
    Initializes the database by creating the new database and necessary tables.
    """
    # Connect to the default PostgreSQL database
    engine = create_engine(DATABASE_URL)
    
    # Create the new database
    try:
        create_database(engine, NEW_DB_NAME)
    except Exception as e:
        print(f"Error creating database: {str(e)}")
        return

    # Connect to the new database and create tables
    new_engine = create_engine(f"postgresql://postgres:postgres@localhost:5432/{NEW_DB_NAME}")
    Base.metadata.create_all(bind=new_engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()

