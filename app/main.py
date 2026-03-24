from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import agent, knowledge
from app.config import settings
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Customer Service Agent",
    version="3.0.0",
    description="LangGraph-based AI Agent for Customer Service"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由
app.include_router(agent.router, prefix="/api/v1/agent", tags=["agent"])
app.include_router(knowledge.router, prefix="/api/v1/agent/knowledge", tags=["knowledge"])


@app.on_event("startup")
async def startup_event():
    logger.info("🚀 AI Agent Service 启动中...")
    logger.info(f"📊 LLM Provider: {settings.LLM_PROVIDER}")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "3.0.0",
        "llm_provider": settings.LLM_PROVIDER
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
