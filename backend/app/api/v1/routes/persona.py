"""Persona API 엔드포인트."""
from fastapi import APIRouter, HTTPException
from app.schemas.persona import PersonaProfile, PersonaCreate, PersonaUpdate
from app.memory.mongo.repository.persona_repo import PersonaRepository

router = APIRouter()


@router.post("/persona/create", response_model=PersonaProfile, status_code=201)
async def create_persona(persona_data: PersonaCreate):
    """Persona 생성."""
    try:
        persona = PersonaRepository.create_persona(persona_data)
        return persona
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create persona: {str(e)}")


@router.get("/persona/{persona_id}", response_model=PersonaProfile)
async def get_persona(persona_id: str):
    """Persona 조회."""
    persona = PersonaRepository.get_persona_by_id(persona_id)
    
    if persona is None:
        raise HTTPException(status_code=404, detail=f"Persona {persona_id} not found")
    
    return persona


@router.put("/persona/{persona_id}", response_model=PersonaProfile)
async def update_persona(persona_id: str, update_data: PersonaUpdate):
    """Persona 수정."""
    update_dict = update_data.model_dump(exclude_unset=True)
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    persona = PersonaRepository.update_persona(persona_id, update_dict)
    
    if persona is None:
        raise HTTPException(status_code=404, detail=f"Persona {persona_id} not found")
    
    return persona
