import os
import redis
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Get Config from Environment Variables (set in docker-compose)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PASS = os.getenv("DB_PASS", "password")

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

# Switch logic: If DB_HOST is 'db', use Postgres. Else use SQLite (local fallback)
if DB_HOST == "db":
    DATABASE_URL = f"postgresql://postgres:{DB_PASS}@{DB_HOST}:5432/shortener"
    engine = create_engine(DATABASE_URL)
else:
    DATABASE_URL = "sqlite:///./shortener.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Database Config
DATABASE_URL = "sqlite:///./shortener.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class URLItem(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String, unique=True, index=True)
    long_url = Column(String)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()