from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, entries, summaries

app = FastAPI(title="LifeTracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(entries.router)
app.include_router(summaries.router)

@app.get("/api/health")
def health():
    return {"status": "ok"}
