from app.agent.state import AgentState
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
import logging

logger = logging.getLogger(__name__)


async def response_generation_node(state: AgentState) -> dict:
    """
    回复生成节点
    
    输入: 用户消息 + 情绪 + 分类 + RAG
    输出: 回复内容
    """
    llm_service = LLMService()
    rag_service = RAGService()
    
    last_message = state["messages"][-1].content
    emotion_type = state.get("emotion_type", "neutral")
    emotion_level = state.get("emotion_level", 1)
    classification_type = state.get("classification_type", "A")
    classification_category = state.get("classification_category", "inquiry")
    
    # RAG 检索相关知识
    try:
        relevant_docs = await rag_service.search(last_message, top_k=3)
        knowledge_context = "\n".join([doc["content"] for doc in relevant_docs])
    except Exception as e:
        logger.warning(f"[response] RAG 检索失败: {e}")
        knowledge_context = "暂无相关知识"
    
    # 根据情绪等级选择话术风格
    style_guide = {
        1: "专业简洁",
        2: "增加同理心",
        3: "道歉 + 升级处理",
        4: "立即转人工"
    }
    
    response_prompt = f"""你是电商客服助手，请根据以下信息生成回复：

用户消息：{last_message}

用户情绪：{emotion_type} Lv{emotion_level}
问题类型：{classification_type}类 - {classification_category}
话术风格：{style_guide.get(emotion_level, "专业简洁")}

相关知识：
{knowledge_context}

要求：
1. 根据情绪等级调整语气
2. 情绪Lv3以上必须道歉
3. 不要使用绝对化用语（一定、保证、绝对）
4. 提供具体解决方案
5. 结尾主动询问是否还有其他需要

直接输出回复内容，不要解释。"""
    
    response = await llm_service.generate(response_prompt)
    
    logger.info(f"[response] 生成完成: emotion={emotion_type}, classification={classification_type}")
    
    return {
        "response": response,
        "turn_count": state.get("turn_count", 0) + 1
    }