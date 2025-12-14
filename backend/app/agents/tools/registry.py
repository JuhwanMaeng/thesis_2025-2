"""Tool registry - 모든 tool 정의 수집."""
from typing import Dict, List, Optional
from app.agents.tools.base import Tool
from app.agents.tools.talk import TalkTool
from app.agents.tools.move import MoveToTool
from app.agents.tools.combat import AttackTool, DefendTool
from app.agents.tools.quest import StartQuestTool, UpdateQuestTool
from app.agents.tools.trade import GiveItemTool, TradeTool
from app.agents.tools.wait import WaitTool
from app.agents.tools.dynamic_tool import DynamicToolExecutor
from app.memory.mongo.repository.dynamic_tool_repo import DynamicToolRepository


class DynamicToolWrapper(Tool):
    """동적 도구를 Tool 인터페이스로 래핑."""
    
    def __init__(self, dynamic_tool):
        self._dynamic_tool = dynamic_tool
        self._executor = DynamicToolExecutor()
    
    @property
    def name(self) -> str:
        return self._dynamic_tool.name
    
    @property
    def description(self) -> str:
        return self._dynamic_tool.description
    
    @property
    def parameters_schema(self) -> Dict:
        return self._dynamic_tool.parameters_schema
    
    def execute(self, arguments: Dict, context: Dict) -> Dict:
        return self._executor.execute(self._dynamic_tool.code, arguments, context)


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
        
        # 동적 도구 로드
        self._load_dynamic_tools()
    
    def _load_dynamic_tools(self):
        """동적 도구 로드."""
        try:
            dynamic_tools = DynamicToolRepository.list_tools()
            for dt in dynamic_tools:
                wrapper = DynamicToolWrapper(dt)
                self._tools[dt.name] = wrapper
        except Exception as e:
            import logging
            logging.warning(f"Failed to load dynamic tools: {str(e)}")
    
    def reload_dynamic_tools(self):
        """동적 도구 재로드."""
        # 기존 동적 도구 제거
        tool_names_to_remove = [
            name for name, tool in self._tools.items()
            if isinstance(tool, DynamicToolWrapper)
        ]
        for name in tool_names_to_remove:
            del self._tools[name]
        
        # 동적 도구 다시 로드
        self._load_dynamic_tools()
    
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
