from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles  # NEW
from fastapi.middleware.cors import CORSMiddleware # NEW
from sqlalchemy.orm import Session
from database import r, get_db, URLItem, engine, Base
import base62

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 1. ENABLE CORS (Allows frontend to talk to backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In real production, specify your domain e.g., ["https://mysite.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. MOUNT STATIC FILES (Serves the Frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- INITIALIZATION ---
@app.on_event("startup")
def startup_event():
    if not r.exists("global_url_id"):
        r.set("global_url_id", 10000)

# --- ROUTES ---

# Root route serves the UI
@app.get("/")
def read_root():
    return RedirectResponse(url="/static/index.html")

# ... (Keep your existing /shorten and redirect endpoints exactly the same) ...
# ... COPY PASTE YOUR EXISTING SHORTEN AND REDIRECT FUNCTIONS HERE ...
@app.post("/shorten")
def shorten_url(long_url: str, db: Session = Depends(get_db)):
    unique_id = r.incr("global_url_id")
    short_code = base62.encode(unique_id)
    db_item = URLItem(id=unique_id, short_code=short_code, long_url=long_url)
    db.add(db_item)
    db.commit()
    r.set(short_code, long_url)
    # Note: We use relative URL here so it works on any domain
    return {"short_url": f"/s/{short_code}", "original": long_url}

# CHANGED: Added /s/ prefix to avoid conflict with static files
@app.get("/s/{short_code}")
def redirect_url(short_code: str, db: Session = Depends(get_db)):
    cached_url = r.get(short_code)
    if cached_url:
        return RedirectResponse(url=cached_url)
    
    db_item = db.query(URLItem).filter(URLItem.short_code == short_code).first()
    if db_item:
        r.set(short_code, db_item.long_url)
        return RedirectResponse(url=db_item.long_url)
        
    raise HTTPException(status_code=404, detail="URL not found")