"""FAISS index 관리자."""
import os
import numpy as np
import faiss
from typing import List, Tuple, Optional
from app.core.config import settings


class FAISSManager:
    """Vector similarity search를 위한 FAISS index 관리."""
    
    def __init__(self, index_name: str, dimension: int):
        """FAISS manager 초기화."""
        self.index_name = index_name
        self.dimension = dimension
        self.index_path = os.path.join(settings.faiss_index_dir, f"{index_name}.index")
        self.index: Optional[faiss.Index] = None
        self.vector_count = 0
    
    def _validate_dimension(self):
        """Dimension이 설정된 dimension과 일치하는지 검증."""
        if self.dimension != settings.openai_embedding_dim:
            raise ValueError(
                f"Index dimension {self.dimension} does not match "
                f"configured dimension {settings.openai_embedding_dim}. "
                "This would cause silent corruption. Please reindex."
            )
    
    def create_index(self) -> None:
        """새 FAISS index 생성."""
        self._validate_dimension()
        
        self.index = faiss.IndexFlatIP(self.dimension)
        self.vector_count = 0
    
    def load_index(self) -> bool:
        """디스크에서 기존 index 로드."""
        if not os.path.exists(self.index_path):
            return False
        
        self.index = faiss.read_index(self.index_path)
        self.vector_count = self.index.ntotal
        
        if self.index.d != self.dimension:
            raise ValueError(
                f"Loaded index dimension {self.index.d} does not match "
                f"configured dimension {self.dimension}. Please reindex."
            )
        
        return True
    
    def _normalize_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """Cosine similarity를 위해 벡터를 단위 길이로 정규화."""
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        return vectors / norms
    
    def add_vectors(self, vectors: np.ndarray) -> List[int]:
        """Index에 vector 추가."""
        if self.index is None:
            raise RuntimeError("Index not initialized. Call create_index() or load_index() first.")
        
        if vectors.shape[1] != self.dimension:
            raise ValueError(
                f"Vector dimension {vectors.shape[1]} does not match index dimension {self.dimension}"
            )
        
        normalized = self._normalize_vectors(vectors)
        
        start_id = self.vector_count
        num_vectors = vectors.shape[0]
        vector_ids = list(range(start_id, start_id + num_vectors))
        
        self.index.add(normalized.astype(np.float32))
        self.vector_count += num_vectors
        
        return vector_ids
    
    def search(self, query_vector: np.ndarray, top_k: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: numpy array of shape (1, D) or (D,)
            top_k: Number of results to return
        
        Returns:
            Tuple of (distances, indices)
            - distances: numpy array of shape (1, top_k) - similarity scores
            - indices: numpy array of shape (1, top_k) - vector IDs
        """
        if self.index is None:
            raise RuntimeError("Index not initialized. Call create_index() or load_index() first.")
        
        if self.vector_count == 0:
            return np.array([[]], dtype=np.float32), np.array([[]], dtype=np.int64)
        
        # Reshape if needed
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        
        # Validate dimension
        if query_vector.shape[1] != self.dimension:
            raise ValueError(
                f"Query vector dimension {query_vector.shape[1]} does not match index dimension {self.dimension}"
            )
        
        normalized_query = self._normalize_vectors(query_vector)
        distances, indices = self.index.search(normalized_query.astype(np.float32), top_k)
        
        return distances, indices
    
    def save_index(self) -> None:
        """Index를 디스크에 저장."""
        if self.index is None:
            raise RuntimeError("Index not initialized. Cannot save.")
        
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
    
    def get_vector_count(self) -> int:
        """Index의 vector 개수 조회."""
        return self.vector_count
    
    def exists(self) -> bool:
        """Index 파일 존재 여부 확인."""
        return os.path.exists(self.index_path)
