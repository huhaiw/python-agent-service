from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Agent 状态"""
    
    # 消息历史
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # 会话信息
    session_id: str
    user_id: str
    user_open_id: str
    turn_count: int
    unresolved_count: int
    
    # 情绪信息
    emotion_type: str
    emotion_level: int
    emotion_confidence: float
    
    # 问题分类
    classification_type: str
    classification_category: str
    classification_confidence: float
    
    # 转人工
    handoff_status: Optional[str]  # None, pending, transferred
    handoff_reason: Optional[str]
    handoff_priority: Optional[int]
    
    # 当前动作
    action_type: str  # reply, handoff, clarify
    response: Optional[str]
