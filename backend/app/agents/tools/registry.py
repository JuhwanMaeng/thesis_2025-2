"""Tool registry - 모든 tool 정의 수집."""
from typing import Dict, List
from app.agents.tools.base import Tool
from app.agents.tools.talk import TalkTool
from app.agents.tools.move import MoveToTool
from app.agents.tools.combat import AttackTool, DefendTool
from app.agents.tools.quest import StartQuestTool, UpdateQuestTool
from app.agents.tools.trade import GiveItemTool, TradeTool
from app.agents.tools.wait import WaitTool


class ToolRegistry:
    """사용 가능한 모든 tool 레지스트리."""
    
    _instance = None
    _tools: Dict[str, Tool] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """모든 tool 초기화."""
        tools = [
            TalkTool(),
            MoveToTool(),
            AttackTool(),
            DefendTool(),
            StartQuestTool(),
            UpdateQuestTool(),
            GiveItemTool(),
            TradeTool(),
            WaitTool(),
        ]
        
        for tool in tools:
            self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Tool:
        """이름으로 tool 조회."""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found")
        return self._tools[name]
    
    def is_valid_tool(self, name: str) -> bool:
        """Tool 이름 유효성 검사."""
        return name in self._tools
    
    def get_all_tools(self) -> List[Dict]:
        """OpenAI function calling 형식으로 모든 tool 반환."""
        return [tool.to_openai_format() for tool in self._tools.values()]
    
    def get_all_tool_names(self) -> List[str]:
        """모든 tool 이름 목록 반환."""
        return list(self._tools.keys())


tool_registry = ToolRegistry()
