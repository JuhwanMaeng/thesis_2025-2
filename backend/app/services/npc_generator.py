"""LLM 기반 NPC 생성 서비스."""
import json
import logging
from typing import Dict, Any, Optional
from app.services.llm_service import llm_service
from app.schemas.persona import PersonaProfile, PersonaCreate
from app.schemas.world import WorldKnowledge, WorldCreate
from app.schemas.npc import NPCCreate, NPCConfig
from app.memory.mongo.repository.persona_repo import PersonaRepository
from app.memory.mongo.repository.world_repo import WorldRepository

logger = logging.getLogger(__name__)


class NPCGenerator:
    """LLM을 사용한 NPC 생성 서비스."""
    
    @staticmethod
    def _load_generation_prompt() -> str:
        """NPC 생성 프롬프트 로드."""
        return """You are an expert game character designer. Generate a complete NPC profile based on the user's description.

The user will provide a brief description of the NPC they want to create. You must generate:
1. A PersonaProfile (personality, traits, habits, goals, background, speech style)
2. A WorldKnowledge (world setting, rules, locations)
3. An initial NPC state (emotion, location, goal)

Return ONLY valid JSON in this exact format:
{
  "persona": {
    "name": "Character Name",
    "traits": ["trait1", "trait2", ...],
    "habits": ["habit1", "habit2", ...],
    "goals": ["goal1", "goal2", ...],
    "background": "Detailed background story...",
    "speech_style": "How the character speaks...",
    "relationships": {},
    "constraints": {
      "taboos": [],
      "moral_rules": []
    }
  },
  "world": {
    "title": "World Name",
    "rules": {
      "laws": [],
      "factions": {},
      "social_norms": []
    },
    "locations": {},
    "danger_levels": {},
    "global_constraints": {}
  },
  "initial_state": {
    "emotion": "calm",
    "location": "starting_location",
    "goal": "initial_goal"
  }
}

Be creative but consistent. Make sure the persona matches the world setting."""

    @staticmethod
    def generate_npc(description: str) -> Dict[str, Any]:
        """
        LLM을 사용하여 NPC 생성.
        
        Args:
            description: NPC에 대한 간단한 설명
        
        Returns:
            생성된 NPC 데이터 (persona, world, initial_state 포함)
        """
        prompt = NPCGenerator._load_generation_prompt()
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Create an NPC with this description: {description}"}
        ]
        
        try:
            response = llm_service.call_simple(messages)
            
            # JSON 파싱
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            data = json.loads(response)
            
            # 검증 및 기본값 설정
            persona_data = data.get("persona", {})
            world_data = data.get("world", {})
            initial_state = data.get("initial_state", {})
            
            # Persona 기본값
            if "name" not in persona_data:
                persona_data["name"] = "Unknown Character"
            if "traits" not in persona_data:
                persona_data["traits"] = []
            if "habits" not in persona_data:
                persona_data["habits"] = []
            if "goals" not in persona_data:
                persona_data["goals"] = []
            if "background" not in persona_data:
                persona_data["background"] = ""
            if "speech_style" not in persona_data:
                persona_data["speech_style"] = ""
            if "relationships" not in persona_data:
                persona_data["relationships"] = {}
            if "constraints" not in persona_data:
                persona_data["constraints"] = {}
            
            # World 기본값
            if "title" not in world_data:
                world_data["title"] = "Generated World"
            if "rules" not in world_data:
                world_data["rules"] = {}
            if "locations" not in world_data:
                world_data["locations"] = {}
            if "danger_levels" not in world_data:
                world_data["danger_levels"] = {}
            if "global_constraints" not in world_data:
                world_data["global_constraints"] = {}
            
            # Initial state 기본값
            if "emotion" not in initial_state:
                initial_state["emotion"] = "neutral"
            if "location" not in initial_state:
                initial_state["location"] = "unknown"
            if "goal" not in initial_state:
                initial_state["goal"] = ""
            
            return {
                "persona": persona_data,
                "world": world_data,
                "initial_state": initial_state
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            raise ValueError(f"Failed to parse LLM response: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to generate NPC: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to generate NPC: {str(e)}")

    @staticmethod
    def create_npc_from_description(
        description: str,
        role: Optional[str] = None,
        config: Optional[NPCConfig] = None
    ) -> Dict[str, Any]:
        """
        설명으로부터 NPC, Persona, World를 생성하고 저장.
        
        Returns:
            생성된 NPC 정보
        """
        # LLM으로 생성
        generated = NPCGenerator.generate_npc(description)
        
        # Persona 생성 및 저장
        persona_data = PersonaCreate(**generated["persona"])
        persona = PersonaRepository.create_persona(persona_data)
        
        # World 생성 및 저장
        world_data = WorldCreate(**generated["world"])
        world = WorldRepository.create_world(world_data)
        
        # NPC 생성
        npc_data = NPCCreate(
            name=generated["persona"]["name"],
            role=role or generated["persona"].get("role", "NPC"),
            persona_id=persona.persona_id,
            world_id=world.world_id,
            current_state=generated["initial_state"],
            config=config
        )
        
        from app.memory.mongo.repository.npc_repo import NPCRepository
        npc = NPCRepository.create_npc(npc_data)
        
        return {
            "npc": npc,
            "persona": persona,
            "world": world
        }
