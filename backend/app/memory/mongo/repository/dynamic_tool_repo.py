"""Dynamic tool repository."""
from typing import Optional, List
from datetime import datetime
import uuid
from app.memory.mongo.client import get_collection
from app.schemas.tool import DynamicTool, DynamicToolCreate, DynamicToolUpdate


class DynamicToolRepository:
    """동적 도구 저장소."""
    
    @staticmethod
    def _get_collection():
        return get_collection("dynamic_tools")
    
    @staticmethod
    def create_tool(tool_data: DynamicToolCreate) -> DynamicTool:
        """동적 도구 생성."""
        tool_id = f"tool_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()
        
        tool_doc = {
            "tool_id": tool_id,
            "name": tool_data.name,
            "description": tool_data.description,
            "parameters_schema": tool_data.parameters_schema,
            "code": tool_data.code,
            "created_at": now,
            "updated_at": now
        }
        
        collection = DynamicToolRepository._get_collection()
        collection.insert_one(tool_doc)
        
        return DynamicTool(**tool_doc)
    
    @staticmethod
    def get_tool_by_id(tool_id: str) -> Optional[DynamicTool]:
        """ID로 도구 조회."""
        collection = DynamicToolRepository._get_collection()
        doc = collection.find_one({"tool_id": tool_id})
        
        if doc is None:
            return None
        
        if "_id" in doc:
            del doc["_id"]
        
        return DynamicTool(**doc)
    
    @staticmethod
    def get_tool_by_name(name: str) -> Optional[DynamicTool]:
        """이름으로 도구 조회."""
        collection = DynamicToolRepository._get_collection()
        doc = collection.find_one({"name": name})
        
        if doc is None:
            return None
        
        if "_id" in doc:
            del doc["_id"]
        
        return DynamicTool(**doc)
    
    @staticmethod
    def list_tools(limit: int = 100) -> List[DynamicTool]:
        """모든 동적 도구 목록 조회."""
        collection = DynamicToolRepository._get_collection()
        docs = collection.find().limit(limit)
        
        tools = []
        for doc in docs:
            if "_id" in doc:
                del doc["_id"]
            tools.append(DynamicTool(**doc))
        
        return tools
    
    @staticmethod
    def update_tool(tool_id: str, updates: DynamicToolUpdate) -> Optional[DynamicTool]:
        """동적 도구 업데이트."""
        collection = DynamicToolRepository._get_collection()
        
        update_dict = {}
        if updates.description is not None:
            update_dict["description"] = updates.description
        if updates.parameters_schema is not None:
            update_dict["parameters_schema"] = updates.parameters_schema
        if updates.code is not None:
            update_dict["code"] = updates.code
        
        if not update_dict:
            return DynamicToolRepository.get_tool_by_id(tool_id)
        
        update_dict["updated_at"] = datetime.utcnow()
        
        result = collection.update_one(
            {"tool_id": tool_id},
            {"$set": update_dict}
        )
        
        if result.matched_count == 0:
            return None
        
        return DynamicToolRepository.get_tool_by_id(tool_id)
    
    @staticmethod
    def delete_tool(tool_id: str) -> bool:
        """동적 도구 삭제."""
        collection = DynamicToolRepository._get_collection()
        result = collection.delete_one({"tool_id": tool_id})
        return result.deleted_count > 0
