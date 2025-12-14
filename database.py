import os
import redis
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
#1. CONFIGURATION ---
REDIS_URL = os.getenv("REDIS_URL")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")
DB_NAME = os.getenv("DB_NAME", "shortener")

#2. REDIS CONNECTION
print("REDIS DEBUG INFO")
try:
    if REDIS_URL:
        # Production (Render): Connect using the full URL
        print(f"Found REDIS_URL. Connecting...")
        r = redis.from_url(REDIS_URL, decode_responses=True)
    else:
        # Local/Docker: Connect using host/port
        print(f"No REDIS_URL found. Connecting to host: {REDIS_HOST}")
        r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
    
    # Test the connection immediately
    r.ping()
    print("Successfully connected to Redis!")

except Exception as e:
    print(f"CRITICAL REDIS ERROR: {e}")

# --- 3. DATABASE CONNECTION ---

if DB_HOST == "db":
    # Production (Docker)
    print("✅ Using PostgreSQL (Docker)")
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"
    engine = create_engine(DATABASE_URL)
else:
    # Local Testing or Render (using SQLite file)
    print("Using SQLite (Local/Render)")
    DATABASE_URL = "sqlite:///./shortener.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#4. DATA MODEL ---
class URLItem(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String, unique=True, index=True)
    long_url = Column(String)

#5. DEPENDENCY ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()