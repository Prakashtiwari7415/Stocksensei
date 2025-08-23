"""
Initialize the database with required tables
"""

from database.database import engine, Base, create_tables
from models.models import StockData, SentimentData, AlertData, User, NewsArticle, MarketIndex

def init_database():
    """Create all database tables"""
    try:
        print("Creating database tables...")
        create_tables()
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")

if __name__ == "__main__":
    init_database()