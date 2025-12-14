"""Dynamic tool API 엔드포인트."""
from fastapi import APIRouter, HTTPException, Body
from typing import List
from app.schemas.tool import DynamicTool, DynamicToolCreate, DynamicToolUpdate
from app.memory.mongo.repository.dynamic_tool_repo import DynamicToolRepository
from app.agents.tools.registry import tool_registry

router = APIRouter()


@router.post("/tool/create", response_model=DynamicTool, status_code=201)
async def create_tool(tool_data: DynamicToolCreate):
    """동적 도구 생성."""
    # 이름 중복 확인
    existing = DynamicToolRepository.get_tool_by_name(tool_data.name)
    if existing:
        raise HTTPException(status_code=400, detail=f"Tool with name '{tool_data.name}' already exists")
    
    # 기본 도구와의 이름 충돌 확인
    if tool_registry.is_valid_tool(tool_data.name):
        raise HTTPException(status_code=400, detail=f"Tool name '{tool_data.name}' conflicts with built-in tool")
    
    try:
        tool = DynamicToolRepository.create_tool(tool_data)
        # 레지스트리 재로드
        tool_registry.reload_dynamic_tools()
        return tool
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create tool: {str(e)}")


@router.get("/tool", response_model=List[DynamicTool])
async def list_tools():
    """모든 동적 도구 목록 조회."""
    try:
        tools = DynamicToolRepository.list_tools()
        return tools
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")


@router.get("/tool/{tool_id}", response_model=DynamicTool)
async def get_tool(tool_id: str):
    """동적 도구 조회."""
    tool = DynamicToolRepository.get_tool_by_id(tool_id)
    if tool is None:
        raise HTTPException(status_code=404, detail=f"Tool {tool_id} not found")
    return tool


@router.put("/tool/{tool_id}", response_model=DynamicTool)
async def update_tool(tool_id: str, updates: DynamicToolUpdate):
    """동적 도구 업데이트."""
    tool = DynamicToolRepository.get_tool_by_id(tool_id)
    if tool is None:
        raise HTTPException(status_code=404, detail=f"Tool {tool_id} not found")
    
    try:
        updated_tool = DynamicToolRepository.update_tool(tool_id, updates)
        if updated_tool is None:
            raise HTTPException(status_code=404, detail=f"Tool {tool_id} not found")
        # 레지스트리 재로드
        tool_registry.reload_dynamic_tools()
        return updated_tool
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update tool: {str(e)}")


@router.delete("/tool/{tool_id}")
async def delete_tool(tool_id: str):
    """동적 도구 삭제."""
    tool = DynamicToolRepository.get_tool_by_id(tool_id)
    if tool is None:
        raise HTTPException(status_code=404, detail=f"Tool {tool_id} not found")
    
    try:
        success = DynamicToolRepository.delete_tool(tool_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Tool {tool_id} not found")
        # 레지스트리 재로드
        tool_registry.reload_dynamic_tools()
        return {"status": "deleted", "tool_id": tool_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete tool: {str(e)}")
