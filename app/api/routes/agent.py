from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    AgentRequest, AgentResponse, AgentResponseData,
    HandoffCheckRequest, HandoffCheckResponse,
    EmotionInfo, ClassificationInfo, ActionInfo, StateInfo
)
from app.agent.graph import agent_app, checkpointer
from app.agent.nodes.handoff import check_handoff_conditions
from langchain_core.messages import HumanMessage
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/process", response_model=AgentResponse)
async def process_message(request: AgentRequest):
    """处理用户消息"""
    try:
        logger.info(f"[process] sessionId={request.session_id}, message={request.message[:50]}...")
        
        # 构建消息列表
        messages = []
        for msg in request.conversation_history or []:
            messages.append(HumanMessage(content=msg.content))
        messages.append(HumanMessage(content=request.message))
        
        # 构建初始状态
        initial_state = {
            "messages": messages,
            "session_id": request.session_id,
            "user_id": request.user_id,
            "user_open_id": request.user_open_id,
            "turn_count": 0,
            "unresolved_count": 0,
        }
        
        # 运行 Agent
        config = {"configurable": {"thread_id": request.session_id}}
        result = await agent_app.ainvoke(initial_state, config)
        
        # 构建响应
        response_data = AgentResponseData(
            session_id=request.session_id,
            response=result.get("response"),
            emotion=EmotionInfo(
                type=result.get("emotion_type", "neutral"),
                level=result.get("emotion_level", 1),
                confidence=result.get("emotion_confidence", 0.8)
            ),
            classification=ClassificationInfo(
                type=result.get("classification_type", "A"),
                category=result.get("classification_category", "inquiry"),
                confidence=result.get("classification_confidence", 0.8)
            ),
            action=ActionInfo(
                type=result.get("action_type", "reply"),
                need_handoff=result.get("handoff_status") is not None,
                handoff_reason=result.get("handoff_reason")
            ),
            state=StateInfo(
                turn_count=result.get("turn_count", 1),
                unresolved_count=result.get("unresolved_count", 0)
            )
        )
        
        logger.info(f"[process] 完成: action={response_data.action.type}")
        
        return AgentResponse(code=0, message="success", data=response_data)
        
    except Exception as e:
        logger.error(f"[process] 失败: {e}", exc_info=True)
        return AgentResponse(code=5000, message=f"处理失败: {str(e)}")


@router.post("/check-handoff", response_model=HandoffCheckResponse)
async def check_handoff(request: HandoffCheckRequest):
    """检查是否需要转人工"""
    try:
        state = {
            "emotion_level": request.emotion_level or 1,
            "unresolved_count": request.unresolved_count or 0,
            "messages": [HumanMessage(content=request.last_message or "")]
        }
        
        need_handoff, reason, priority = check_handoff_conditions(state)
        
        from app.models.schemas import HandoffCheckData
        
        return HandoffCheckResponse(
            code=0,
            message="success",
            data=HandoffCheckData(
                need_handoff=need_handoff,
                reason=reason,
                priority=priority
            )
        )
    except Exception as e:
        logger.error(f"[check-handoff] 失败: {e}", exc_info=True)
        return HandoffCheckResponse(code=5000, message=f"检查失败: {str(e)}")


@router.get("/state/{session_id}")
async def get_session_state(session_id: str):
    """获取会话状态"""
    try:
        config = {"configurable": {"thread_id": session_id}}
        state = checkpointer.get(config)
        
        return {
            "code": 0,
            "message": "success",
            "data": state
        }
    except Exception as e:
        logger.error(f"[state] 失败: {e}", exc_info=True)
        return {
            "code": 1002,
            "message": f"会话不存在: {session_id}"
        }
