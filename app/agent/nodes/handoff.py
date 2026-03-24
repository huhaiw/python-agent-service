from app.agent.state import AgentState
from app.services.llm_service import LLMService
import json
import logging

logger = logging.getLogger(__name__)


async def human_handoff_check_node(state: AgentState) -> dict:
    """
    转人工检查节点
    
    输入: 用户消息 + 情绪 + 分类 + 历史状态
    输出: 是否转人工、原因、优先级
    """
    llm_service = LLMService()
    
    last_message = state["messages"][-1].content
    emotion_type = state.get("emotion_type", "neutral")
    emotion_level = state.get("emotion_level", 1)
    classification_type = state.get("classification_type", "A")
    classification_category = state.get("classification_category", "inquiry")
    turn_count = state.get("turn_count", 0)
    unresolved_count = state.get("unresolved_count", 0)
    
    # 调用 LLM 进行转人工判断
    handoff_prompt = f"""根据以下信息判断是否需要转人工客服，返回 JSON 格式：

用户消息：{last_message}
情绪类型：{emotion_type}（等级 {emotion_level}/4）
问题类型：{classification_type}类 - {classification_category}
对话轮数：{turn_count}
未解决次数：{unresolved_count}

返回格式（必须是有效的 JSON）：
{{
    "need_handoff": true/false,
    "reason": "转人工原因",
    "priority": 1-4
}}

转人工规则：
1. 用户明确要求转人工 → need_handoff: true, priority: 2
2. 情绪等级4级（危险）→ need_handoff: true, priority: 4
3. 情绪等级3级且问题复杂 → need_handoff: true, priority: 3
4. 对话10轮以上仍未解决 → need_handoff: true, priority: 3
5. 其他情况 → need_handoff: false, priority: 0

优先级说明：
- 1: 低
- 2: 中
- 3: 高
- 4: 紧急

只返回 JSON，不要其他内容。"""
    
    result = await llm_service.generate(handoff_prompt)
    
    # 解析结果
    try:
        # 清理可能的 markdown 代码块
        result = result.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        
        handoff_data = json.loads(result)
        
        need_handoff = handoff_data.get("need_handoff", False)
        
        if need_handoff:
            return {
                "handoff_status": "pending",
                "handoff_reason": handoff_data.get("reason", "需要人工介入"),
                "handoff_priority": handoff_data.get("priority", 2)
            }
        else:
            return {
                "handoff_status": "none",
                "handoff_reason": None,
                "handoff_priority": 0
            }
    except Exception as e:
        logger.error(f"[handoff_check] 解析失败: {e}, result={result}")
        # 默认不转人工
        return {
            "handoff_status": "none",
            "handoff_reason": None,
            "handoff_priority": 0
        }