"""FAISS vector 메타데이터 저장소 (JSONL 형식)."""
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.core.config import settings


class MetadataStore:
    """JSONL 형식으로 FAISS vector 메타데이터 관리."""
    
    def __init__(self, index_name: str):
        """메타데이터 저장소 초기화."""
        self.index_name = index_name
        self.meta_path = os.path.join(settings.faiss_meta_dir, f"{index_name}.jsonl")
        self.metadata: List[Dict[str, Any]] = []
    
    def load(self) -> None:
        """JSONL 파일에서 메타데이터 로드."""
        self.metadata = []
        
        if not os.path.exists(self.meta_path):
            return
        
        with open(self.meta_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    self.metadata.append(json.loads(line))
    
    def save(self) -> None:
        """메타데이터를 JSONL 파일에 저장."""
        os.makedirs(os.path.dirname(self.meta_path), exist_ok=True)
        
        with open(self.meta_path, 'w', encoding='utf-8') as f:
            for record in self.metadata:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    def add(self, record: Dict[str, Any]) -> int:
        """메타데이터 레코드 추가."""
        if 'created_at' not in record:
            record['created_at'] = datetime.utcnow().isoformat()
        
        vector_id = len(self.metadata)
        record['vector_id'] = vector_id
        self.metadata.append(record)
        
        return vector_id
    
    def get(self, vector_id: int) -> Optional[Dict[str, Any]]:
        """vector_id로 메타데이터 조회."""
        if 0 <= vector_id < len(self.metadata):
            return self.metadata[vector_id]
        return None
    
    def get_by_source_id(self, source_type: str, source_id: str) -> List[Dict[str, Any]]:
        """Source의 모든 메타데이터 레코드 조회."""
        return [
            record for record in self.metadata
            if record.get('source_type') == source_type and record.get('source_id') == source_id
        ]
    
    def get_all(self) -> List[Dict[str, Any]]:
        """모든 메타데이터 레코드 조회."""
        return self.metadata.copy()
    
    def count(self) -> int:
        """메타데이터 레코드 개수 조회."""
        return len(self.metadata)
    
    def clear(self) -> None:
        """모든 메타데이터 초기화 (재인덱싱용)."""
        self.metadata = []
    
    def exists(self) -> bool:
        """메타데이터 파일 존재 여부 확인."""
        return os.path.exists(self.meta_path)
