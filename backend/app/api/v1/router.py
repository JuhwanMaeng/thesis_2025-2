from fastapi import APIRouter
from app.api.v1.routes import health, npc, memory, action, vector, turn, persona, world, trace, tool

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(npc.router, tags=["npc"])
api_router.include_router(memory.router, tags=["memory"])
api_router.include_router(action.router, tags=["action"])
api_router.include_router(vector.router, tags=["vector"])
api_router.include_router(turn.router, tags=["turn"])
api_router.include_router(persona.router, tags=["persona"])
api_router.include_router(world.router, tags=["world"])
api_router.include_router(trace.router, tags=["trace"])
api_router.include_router(tool.router, tags=["tool"])
