from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the database URL.
# For SQLite, it's "sqlite:///./your_database_name.db"
# Replace 'itsmbot.db' with your desired database file name.
DATABASE_URL = "sqlite:///./itsmbot.db"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) # check_same_thread is for SQLite

# Create a SessionLocal class to generate database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for declarative models
Base = declarative_base()