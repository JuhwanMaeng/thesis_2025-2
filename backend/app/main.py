import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
from app.memory.mongo.client import MongoClientManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 lifespan 관리."""
    os.makedirs(settings.faiss_index_dir, exist_ok=True)
    os.makedirs(settings.faiss_meta_dir, exist_ok=True)
    
    from app.memory.vector.faiss_manager import FAISSManager
    for index_name in ['episodic', 'persona', 'world']:
        manager = FAISSManager(index_name, settings.openai_embedding_dim)
        if manager.exists():
            try:
                manager.load_index()
            except ValueError as e:
                import logging
                logging.error(f"FAISS index {index_name} dimension mismatch: {str(e)}")
    
    MongoClientManager.initialize()
    
    yield
    
    MongoClientManager.close()


app = FastAPI(
    title="AI NPC Framework",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",  # Vite dev server alternate port
        "http://localhost:3000",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def root_health():
    """Root health check."""
    return {"status": "ok"}
