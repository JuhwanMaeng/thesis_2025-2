"""Vector memory API 엔드포인트."""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from app.memory.vector.vectorizer import Vectorizer
from app.memory.vector.retriever import VectorRetriever
from app.memory.mongo.repository.npc_repo import NPCRepository
from app.memory.mongo.repository.memory_repo import MemoryRepository
from app.memory.mongo.repository.persona_repo import PersonaRepository
from app.memory.mongo.repository.world_repo import WorldRepository

router = APIRouter()


@router.post("/vector/reindex")
async def reindex(
    index_type: str = Query(..., description="Index type: episodic, persona, or world")
):
    """MongoDB에서 vector index 재구성."""
    if index_type not in ['episodic', 'persona', 'world']:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid index_type: {index_type}. Must be 'episodic', 'persona', or 'world'"
        )
    
    try:
        vectorizer = Vectorizer(index_type)
        vectorizer.reindex()
        
        count = 0
        
        if index_type == 'episodic':
            from app.memory.mongo.client import get_collection
            collection = get_collection('episodic_memory')
            memories = collection.find({"memory_type": "long_term"})
            
            for mem in memories:
                vectorizer.vectorize_episodic_memory(
                    memory_id=mem['memory_id'],
                    npc_id=mem['npc_id'],
                    content=mem['content'],
                    importance=mem.get('importance', 0.5),
                    created_at=mem.get('created_at', '').isoformat() if hasattr(mem.get('created_at'), 'isoformat') else str(mem.get('created_at', ''))
                )
                count += 1
        
        elif index_type == 'persona':
            from app.memory.mongo.client import get_collection
            collection = get_collection('persona_profiles')
            personas = collection.find()
            
            for persona in personas:
                persona_dict = {
                    'traits': persona.get('traits', []),
                    'habits': persona.get('habits', []),
                    'goals': persona.get('goals', []),
                    'background': persona.get('background', ''),
                    'speech_style': persona.get('speech_style', ''),
                    'constraints': persona.get('constraints', {}),
                    'created_at': persona.get('created_at', '').isoformat() if hasattr(persona.get('created_at'), 'isoformat') else str(persona.get('created_at', ''))
                }
                vector_ids = vectorizer.vectorize_persona_chunks(
                    persona_id=persona['persona_id'],
                    persona_data=persona_dict
                )
                count += len(vector_ids)
        
        elif index_type == 'world':
            from app.memory.mongo.client import get_collection
            collection = get_collection('world_knowledge')
            worlds = collection.find()
            
            for world in worlds:
                world_dict = {
                    'rules': world.get('rules', {}),
                    'locations': world.get('locations', {}),
                    'danger_levels': world.get('danger_levels', {}),
                    'global_constraints': world.get('global_constraints', {}),
                    'created_at': world.get('created_at', '').isoformat() if hasattr(world.get('created_at'), 'isoformat') else str(world.get('created_at', ''))
                }
                vector_ids = vectorizer.vectorize_world_chunks(
                    world_id=world['world_id'],
                    world_data=world_dict
                )
                count += len(vector_ids)
        
        return {
            "status": "success",
            "index_type": index_type,
            "vectors_indexed": count,
            "message": f"Reindexed {index_type} index with {count} vectors"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reindexing failed: {str(e)}")


@router.get("/npc/{npc_id}/vector_memories")
async def get_vector_memories(
    npc_id: str,
    query: Optional[str] = Query(None, description="Optional query text for retrieval"),
    top_k: int = Query(default=10, ge=1, le=50, description="Number of results to return")
):
    """NPC vector memory 조회 (메타데이터만 반환)."""
    npc = NPCRepository.get_npc_by_id(npc_id)
    if npc is None:
        raise HTTPException(status_code=404, detail=f"NPC {npc_id} not found")
    
    try:
        retriever = VectorRetriever()
        
        if query:
            results = retriever.retrieve_for_npc(npc_id, query, top_k)
            return {
                "npc_id": npc_id,
                "query": query,
                "results": results['retrieved_sources'],
                "similarity_scores": results['similarity_scores']
            }
        else:
            episodic_vectorizer = Vectorizer('episodic')
            episodic_vectorizer.metadata_store.load()
            
            all_metadata = episodic_vectorizer.metadata_store.get_all()
            npc_memories = [
                meta for meta in all_metadata
                if meta.get('source_type') == 'episodic' and meta.get('npc_id') == npc_id
            ]
            
            return {
                "npc_id": npc_id,
                "query": None,
                "results": npc_memories[:top_k],
                "total_count": len(npc_memories)
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve vector memories: {str(e)}")


@router.get("/vector/stats")
async def get_vector_stats():
    """Vector index 통계 조회."""
    try:
        episodic = Vectorizer('episodic')
        persona = Vectorizer('persona')
        world = Vectorizer('world')
        
        return {
            "episodic": {
                "vector_count": episodic.get_vector_count(),
                "index_exists": episodic.faiss_manager.exists(),
                "metadata_exists": episodic.metadata_store.exists()
            },
            "persona": {
                "vector_count": persona.get_vector_count(),
                "index_exists": persona.faiss_manager.exists(),
                "metadata_exists": persona.metadata_store.exists()
            },
            "world": {
                "vector_count": world.get_vector_count(),
                "index_exists": world.faiss_manager.exists(),
                "metadata_exists": world.metadata_store.exists()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
