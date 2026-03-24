from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """LLM 服务"""
    
    def __init__(self):
        self.llm = self._init_llm()
    
    def _init_llm(self):
        """初始化 LLM"""
        if settings.LLM_PROVIDER == "openai":
            # 支持 OpenAI 兼容 API（如 Moonshot/Kimi）
            return ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
                temperature=1  # Moonshot API 只支持 temperature=1
            )
        elif settings.LLM_PROVIDER == "claude":
            return ChatAnthropic(
                model=settings.CLAUDE_MODEL,
                api_key=settings.CLAUDE_API_KEY,
                temperature=0.7
            )
        else:
            raise ValueError(f"不支持的 LLM Provider: {settings.LLM_PROVIDER}")
    
    async def generate(self, prompt: str) -> str:
        """生成回复"""
        try:
            response = await self.llm.ainvoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"[LLMService] 生成失败: {e}")
            raise