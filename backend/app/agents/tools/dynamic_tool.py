"""동적 도구 실행기."""
from typing import Dict, Any
import logging
import traceback

logger = logging.getLogger(__name__)


class DynamicToolExecutor:
    """동적 도구 실행기."""
    
    @staticmethod
    def execute(code: str, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        동적 도구 코드 실행.
        
        Args:
            code: 실행할 Python 코드 (execute 함수 정의 포함)
            arguments: 도구 인자
            context: 실행 컨텍스트 (npc_id, world_id 등)
        
        Returns:
            실행 결과 딕셔너리
        """
        try:
            # 안전한 실행 환경 생성
            safe_globals = {
                '__builtins__': {
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'dict': dict,
                    'list': list,
                    'tuple': tuple,
                    'set': set,
                    'min': min,
                    'max': max,
                    'sum': sum,
                    'abs': abs,
                    'round': round,
                    'range': range,
                    'enumerate': enumerate,
                    'zip': zip,
                    'isinstance': isinstance,
                    'hasattr': hasattr,
                    'getattr': getattr,
                    'setattr': setattr,
                },
                'arguments': arguments,
                'context': context,
            }
            
            # 코드 실행 (execute 함수 정의)
            exec(code, safe_globals)
            
            # execute 함수 호출
            if 'execute' not in safe_globals:
                return {
                    "success": False,
                    "effect": {},
                    "error": "Code must define an 'execute' function"
                }
            
            execute_func = safe_globals['execute']
            result = execute_func(arguments, context)
            
            # 결과 검증
            if not isinstance(result, dict):
                return {
                    "success": False,
                    "effect": {},
                    "error": f"execute function must return a dict, got {type(result)}"
                }
            
            # success 필드가 없으면 기본값 설정
            if "success" not in result:
                result["success"] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Dynamic tool execution failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "effect": {},
                "error": f"Execution error: {str(e)}"
            }
