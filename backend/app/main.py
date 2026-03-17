from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    laws_router,
    articles_router,
    amendments_router,
    enriched_router,
    misc_router,
)

app = FastAPI(
    title="Laws Management Platform",
    description="Aggregation layer: Laws API + Wikipedia + NewsAPI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(laws_router.router,       prefix="/api/laws",       tags=["Laws"])
app.include_router(articles_router.router,   prefix="/api/articles",   tags=["Articles"])
app.include_router(amendments_router.router, prefix="/api/amendments", tags=["Amendments"])
app.include_router(enriched_router.router,   prefix="/api/enriched",   tags=["Enriched"])
app.include_router(misc_router.router,       prefix="/api",            tags=["Misc"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}