"""PeaCoK 데이터 파서 - JSON을 PersonaFact로 변환."""
import json
import logging
from typing import List, Dict, Optional
from app.schemas.persona import PersonaFactCreate, PersonaFactDimension

logger = logging.getLogger(__name__)


def map_dimension(peacok_dimension: str) -> Optional[PersonaFactDimension]:
    """
    PeaCoK dimension 값을 PersonaFactDimension enum으로 매핑.
    
    Args:
        peacok_dimension: PeaCoK에서 온 dimension 값 (예: "characteristic", "routine_habit")
    
    Returns:
        PersonaFactDimension enum 값 또는 None (매핑 불가능한 경우)
    """
    dimension_map = {
        "characteristic": PersonaFactDimension.CHARACTERISTIC,
        "routine_habit": PersonaFactDimension.ROUTINE_HABIT,
        "goal_plan": PersonaFactDimension.GOAL_PLAN,
        "experience": PersonaFactDimension.EXPERIENCE,
        "relationship": PersonaFactDimension.RELATIONSHIP,
    }
    
    # 정확한 매칭
    if peacok_dimension in dimension_map:
        return dimension_map[peacok_dimension]
    
    # 소문자 변환 후 매칭
    peacok_dimension_lower = peacok_dimension.lower()
    if peacok_dimension_lower in dimension_map:
        return dimension_map[peacok_dimension_lower]
    
    # 부분 매칭 (예: "routine" -> "routine_habit")
    for key, value in dimension_map.items():
        if key.replace("_", "") in peacok_dimension_lower.replace("_", ""):
            return value
    
    return None


def parse_peacok_attribute(
    persona_key: str,
    attr_key: str,
    attr_data: Dict,
    persona_id_mapping: Optional[Dict[str, str]] = None
) -> Optional[PersonaFactCreate]:
    """
    PeaCoK attribute를 PersonaFactCreate로 변환.
    
    Args:
        persona_key: 페르소나 설명 (예: "i am an actor who play my part")
        attr_key: 속성 키 (예: "complicent")
        attr_data: 속성 데이터 딕셔너리
        persona_id_mapping: persona_key -> persona_id 매핑 (선택사항)
    
    Returns:
        PersonaFactCreate 또는 None (변환 불가능한 경우)
    """
    # relation_labels에서 dimension 추출
    relation_labels = attr_data.get("relation_labels", {})
    majority = relation_labels.get("majority", [])
    
    if not majority or len(majority) == 0:
        return None
    
    # 첫 번째 값이 dimension
    peacok_dimension = majority[0]
    
    # "controversial", "not" 같은 값은 필터링
    if peacok_dimension in ["controversial", "not"]:
        return None
    
    # dimension 매핑
    dimension = map_dimension(peacok_dimension)
    if dimension is None:
        return None
    
    # content 추출 (attr_person 우선, 없으면 attr_third, 없으면 attr_key)
    content = attr_data.get("attr_person") or attr_data.get("attr_third") or attr_key
    
    if not content or not content.strip():
        return None
    
    # persona_id 결정 (매핑이 있으면 사용, 없으면 persona_key를 그대로 사용)
    persona_id = persona_id_mapping.get(persona_key, persona_key) if persona_id_mapping else persona_key
    
    return PersonaFactCreate(
        persona_id=persona_id,
        npc_id=None,  # NPC 생성 시 할당됨
        dimension=dimension,
        content=content.strip(),
        source="PeaCoK",
        is_static=True
    )


def parse_peacok_data(
    file_path: str,
    persona_id_mapping: Optional[Dict[str, str]] = None,
    filter_dimensions: Optional[List[str]] = None
) -> List[PersonaFactCreate]:
    """
    PeaCoK JSON 파일을 파싱하여 PersonaFactCreate 리스트로 변환.
    
    Args:
        file_path: PeaCoK JSON 파일 경로
        persona_id_mapping: persona_key -> persona_id 매핑 (선택사항)
        filter_dimensions: 포함할 dimension 리스트 (None이면 모두 포함)
    
    Returns:
        PersonaFactCreate 리스트
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    facts = []
    skipped_count = 0
    
    for persona_key, persona_data in data.items():
        if "attributes" not in persona_data:
            continue
        
        for attr_key, attr_data in persona_data["attributes"].items():
            fact = parse_peacok_attribute(
                persona_key=persona_key,
                attr_key=attr_key,
                attr_data=attr_data,
                persona_id_mapping=persona_id_mapping
            )
            
            if fact is None:
                skipped_count += 1
                continue
            
            # dimension 필터링
            if filter_dimensions and fact.dimension.value not in filter_dimensions:
                skipped_count += 1
                continue
            
            facts.append(fact)
    
    logger.info(f"Parsed {len(facts)} facts from PeaCoK data")
    if skipped_count > 0:
        logger.debug(f"Skipped {skipped_count} attributes (invalid dimension or missing data)")
    
    return facts


def get_dimension_statistics(facts: List[PersonaFactCreate]) -> Dict[str, int]:
    """
    PersonaFactCreate 리스트에서 dimension별 통계를 반환.
    
    Args:
        facts: PersonaFactCreate 리스트
    
    Returns:
        dimension별 개수 딕셔너리
    """
    stats = {}
    for fact in facts:
        dim = fact.dimension.value
        stats[dim] = stats.get(dim, 0) + 1
    return stats
