"""Embedding 서비스 - OpenAI embeddings API 래퍼."""
from typing import List
import numpy as np
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings


class EmbeddingService:
    """OpenAI API를 사용한 embedding 생성 서비스."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_embedding_model
        self.dimension = settings.openai_embedding_dim
        self.batch_size = 100
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _embed_batch(self, texts: List[str]) -> np.ndarray:
        """텍스트 배치 embedding."""
        cleaned_texts = [text.strip() for text in texts]
        
        response = self.client.embeddings.create(
            model=self.model,
            input=cleaned_texts
        )
        
        embeddings = [item.embedding for item in response.data]
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        if embeddings_array.shape[1] != self.dimension:
            raise ValueError(
                f"Expected dimension {self.dimension}, got {embeddings_array.shape[1]}"
            )
        
        return embeddings_array
    
    def embed(self, texts: List[str]) -> np.ndarray:
        """텍스트 리스트 embedding (배치 처리 자동)."""
        if not texts:
            return np.array([], dtype=np.float32).reshape(0, self.dimension)
        
        all_embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_embeddings = self._embed_batch(batch)
            all_embeddings.append(batch_embeddings)
        
        if all_embeddings:
            return np.vstack(all_embeddings)
        else:
            return np.array([], dtype=np.float32).reshape(0, self.dimension)
    
    def embed_single(self, text: str) -> np.ndarray:
        """단일 텍스트 embedding."""
        return self.embed([text])


embedding_service = EmbeddingService()
