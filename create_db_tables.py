# create_db_tables.py
from database.session import engine, Base
from database.models import User, Ticket # Import all your models here

def create_tables():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully (if they didn't exist).")

if __name__ == "__main__":
    create_tables()