from app.agent.state import AgentState
from app.services.llm_service import LLMService
import json
import logging

logger = logging.getLogger(__name__)


async def intent_classification_node(state: AgentState) -> dict:
    """
    问题分类节点
    
    输入: 用户消息
    输出: 问题类型、分类、置信度
    """
    llm_service = LLMService()
    
    last_message = state["messages"][-1].content
    
    # 调用 LLM 进行问题分类
    classification_prompt = f"""分析以下用户消息的问题类型，返回 JSON 格式：

消息：{last_message}

返回格式（必须是有效的 JSON）：
{{
    "type": "A|B|C|D|E|F|H",
    "category": "分类名称",
    "confidence": 0.0-1.0
}}

问题类型说明：
- A: 通用咨询（问好、了解、一般问题）
- B: 物流相关（发货、配送、运费、到货时间）
- C: 价格相关（价格、优惠、折扣、活动）
- D: 产品相关（功能、质量、尺寸、型号）
- E: 售后相关（退款、退货、换货、维修）
- F: 账号相关（登录、注册、会员、积分）
- H: 转人工（用户要求转人工客服）

只返回 JSON，不要其他内容。"""
    
    result = await llm_service.generate(classification_prompt)
    
    # 解析结果
    try:
        # 清理可能的 markdown 代码块
        result = result.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        
        classification_data = json.loads(result)
        
        return {
            "classification_type": classification_data.get("type", "A"),
            "classification_category": classification_data.get("category", "inquiry"),
            "classification_confidence": classification_data.get("confidence", 0.8)
        }
    except Exception as e:
        logger.error(f"[classification] 解析失败: {e}, result={result}")
        # 默认值
        return {
            "classification_type": "A",
            "classification_category": "inquiry",
            "classification_confidence": 0.7
        }