from app.agent.state import AgentState
from app.services.llm_service import LLMService
import json
import logging

logger = logging.getLogger(__name__)


async def emotion_detection_node(state: AgentState) -> dict:
    """
    情绪检测节点
    
    输入: 用户消息
    输出: 情绪类型、等级、置信度
    """
    llm_service = LLMService()
    
    last_message = state["messages"][-1].content
    
    # 调用 LLM 进行情绪检测
    emotion_prompt = f"""分析以下用户消息的情绪，返回 JSON 格式：

消息：{last_message}

返回格式（必须是有效的 JSON）：
{{
    "type": "anger|anxiety|frustration|confusion|neutral|positive",
    "level": 1-4,
    "confidence": 0.0-1.0
}}

情绪类型说明：
- anger: 愤怒（投诉、差评、气死了）
- anxiety: 焦虑（怎么办、急、什么时候）
- frustration: 沮丧（失望、太差了）
- confusion: 困惑（怎么弄、不会、不明白）
- neutral: 中性（查询、了解、请问）
- positive: 积极（谢谢、很好、满意）

情绪等级说明：
- Lv1: 轻微（语气词）
- Lv2: 中等（负面表达）
- Lv3: 强烈（明显不满）
- Lv4: 危险（威胁/投诉）

只返回 JSON，不要其他内容。"""
    
    result = await llm_service.generate(emotion_prompt)
    
    # 解析结果
    try:
        # 清理可能的 markdown 代码块
        result = result.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        
        emotion_data = json.loads(result)
        
        return {
            "emotion_type": emotion_data.get("type", "neutral"),
            "emotion_level": emotion_data.get("level", 1),
            "emotion_confidence": emotion_data.get("confidence", 0.8)
        }
    except Exception as e:
        logger.error(f"[emotion_detection] 解析失败: {e}, result={result}")
        # 默认值
        return {
            "emotion_type": "neutral",
            "emotion_level": 1,
            "emotion_confidence": 0.8
        }