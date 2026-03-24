from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.agent.state import AgentState
from app.agent.nodes.emotion import emotion_detection_node
from app.agent.nodes.classification import intent_classification_node
from app.agent.nodes.handoff import human_handoff_check_node
from app.agent.nodes.response import response_generation_node
from typing import Literal
import logging

logger = logging.getLogger(__name__)


def should_handoff(state: AgentState) -> Literal["handoff", "continue"]:
    """判断是否转人工"""
    if state.get("handoff_status") == "pending":
        return "handoff"
    return "continue"


def create_agent_graph():
    """创建 Agent 图"""
    # 创建图
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("emotion_detection", emotion_detection_node)
    workflow.add_node("intent_classification", intent_classification_node)
    workflow.add_node("human_handoff_check", human_handoff_check_node)
    workflow.add_node("response_generation", response_generation_node)
    
    # 设置入口
    workflow.set_entry_point("emotion_detection")
    
    # 添加边
    workflow.add_edge("emotion_detection", "intent_classification")
    workflow.add_edge("intent_classification", "human_handoff_check")
    
    # 条件路由
    workflow.add_conditional_edges(
        "human_handoff_check",
        should_handoff,
        {
            "handoff": END,
            "continue": "response_generation"
        }
    )
    
    workflow.add_edge("response_generation", END)
    
    # 编译图（带状态持久化）
    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)
    
    return app, checkpointer


# 全局实例
agent_app, checkpointer = create_agent_graph()
