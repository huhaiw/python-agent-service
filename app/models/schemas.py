from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class EmotionType(str, Enum):
    """情绪类型"""
    ANGER = "anger"
    ANXIETY = "anxiety"
    FRUSTRATION = "frustration"
    CONFUSION = "confusion"
    NEUTRAL = "neutral"
    POSITIVE = "positive"


class ClassificationType(str, Enum):
    """问题分类类型"""
    A = "A"  # 可直接回答
    B = "B"  # 需要澄清
    C = "C"  # 超范围
    D = "D"  # 危险敏感


class ActionType(str, Enum):
    """动作类型"""
    REPLY = "reply"
    HANDOFF = "handoff"
    CLARIFY = "clarify"


# ===== 请求模型 =====

class MessageItem(BaseModel):
    """消息项"""
    role: str = Field(..., description="角色: user / assistant")
    content: str = Field(..., description="消息内容")


class AgentRequest(BaseModel):
    """Agent 请求"""
    session_id: str = Field(..., description="会话ID")
    user_id: str = Field(..., description="用户ID")
    user_open_id: str = Field(..., description="用户飞书open_id")
    message: str = Field(..., description="用户消息")
    conversation_history: Optional[List[MessageItem]] = Field(default=[], description="对话历史")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="元数据")


class HandoffCheckRequest(BaseModel):
    """转人工检查请求"""
    session_id: str
    emotion_level: Optional[int] = 1
    unresolved_count: Optional[int] = 0
    user_request_handoff: Optional[bool] = False
    last_message: Optional[str] = None


class KnowledgeItem(BaseModel):
    """知识项"""
    id: str
    category: str
    question: str
    answer: str
    metadata: Optional[Dict[str, Any]] = {}


class KnowledgeSyncRequest(BaseModel):
    """知识库同步请求"""
    action: str = Field(..., description="操作: upsert / delete")
    items: List[KnowledgeItem]


# ===== 响应模型 =====

class EmotionInfo(BaseModel):
    """情绪信息"""
    type: str
    level: int
    confidence: float


class ClassificationInfo(BaseModel):
    """问题分类信息"""
    type: str
    category: str
    confidence: float


class ActionInfo(BaseModel):
    """动作信息"""
    type: str
    need_handoff: bool
    handoff_reason: Optional[str] = None


class StateInfo(BaseModel):
    """状态信息"""
    turn_count: int
    unresolved_count: int


class AgentResponseData(BaseModel):
    """Agent 响应数据"""
    session_id: str
    response: Optional[str] = None
    emotion: EmotionInfo
    classification: ClassificationInfo
    action: ActionInfo
    state: StateInfo


class AgentResponse(BaseModel):
    """Agent 响应"""
    code: int = 0
    message: str = "success"
    data: Optional[AgentResponseData] = None


class HandoffCheckData(BaseModel):
    """转人工检查数据"""
    need_handoff: bool
    reason: str
    priority: int


class HandoffCheckResponse(BaseModel):
    """转人工检查响应"""
    code: int = 0
    message: str = "success"
    data: Optional[HandoffCheckData] = None


class KnowledgeSyncData(BaseModel):
    """知识库同步数据"""
    synced_count: int
    failed_count: int


class KnowledgeSyncResponse(BaseModel):
    """知识库同步响应"""
    code: int = 0
    message: str = "success"
    data: Optional[KnowledgeSyncData] = None


# ===== 回调模型 =====

class HandoffCallbackRequest(BaseModel):
    """转人工回调请求"""
    session_id: str
    user_open_id: str
    reason: str
    emotion_type: str
    emotion_level: int
    classification_type: str
    classification_category: str
    conversation_summary: str
    priority: int
    timestamp: str
