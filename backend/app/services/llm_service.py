"""LLM 서비스 - OpenAI Chat Completions 래퍼."""
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from app.agents.tools.registry import tool_registry


class LLMService:
    """LLM 상호작용 서비스."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_chat_model
        self.temperature = 0.3
        self.max_tokens = 2000
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _call_llm(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto"
    ) -> Dict[str, Any]:
        """OpenAI Chat Completions API 호출."""
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        if tools:
            params["tools"] = tools
            params["tool_choice"] = tool_choice
        
        response = self.client.chat.completions.create(**params)
        
        return {
            "raw_response": response,
            "message": response.choices[0].message,
            "usage": response.usage
        }
    
    def call_with_tools(
        self,
        messages: List[Dict[str, str]],
        use_tools: bool = True
    ) -> Dict[str, Any]:
        """Tool 지원 LLM 호출."""
        tools = None
        if use_tools:
            tools = tool_registry.get_all_tools()
        
        result = self._call_llm(messages, tools=tools, tool_choice="auto" if use_tools else "none")
        
        message = result["message"]
        tool_calls = []
        
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_calls.append({
                    "id": tool_call.id,
                    "type": tool_call.type,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                })
        
        return {
            "raw_output": message.content or "",
            "tool_calls": tool_calls,
            "finish_reason": result["raw_response"].choices[0].finish_reason,
            "usage": {
                "prompt_tokens": result["usage"].prompt_tokens,
                "completion_tokens": result["usage"].completion_tokens,
                "total_tokens": result["usage"].total_tokens
            }
        }
    
    def call_simple(
        self,
        messages: List[Dict[str, str]]
    ) -> str:
        """Tool 없이 간단한 LLM 호출 (reflection, importance scoring용)."""
        result = self._call_llm(messages, tools=None, tool_choice="none")
        return result["message"].content or ""
    
    def parse_tool_call(self, tool_call: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Tool call 파싱 및 검증."""
        try:
            function = tool_call.get("function", {})
            tool_name = function.get("name")
            arguments_str = function.get("arguments", "{}")
            
            if not tool_registry.is_valid_tool(tool_name):
                return None
            
            arguments = json.loads(arguments_str)
            
            return {
                "action_type": tool_name,
                "arguments": arguments
            }
        except (json.JSONDecodeError, KeyError, TypeError):
            return None


llm_service = LLMService()
