from fastapi import APIRouter
from app.models.schemas import (
    KnowledgeSyncRequest, KnowledgeSyncResponse, KnowledgeSyncData
)
from app.services.rag_service import RAGService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/sync", response_model=KnowledgeSyncResponse)
async def sync_knowledge(request: KnowledgeSyncRequest):
    """同步知识库"""
    try:
        logger.info(f"[sync] action={request.action}, count={len(request.items)}")
        
        rag_service = RAGService()
        
        synced_count = 0
        failed_count = 0
        
        if request.action == "upsert":
            # 插入或更新
            for item in request.items:
                try:
                    await rag_service.upsert([{
                        "id": item.id,
                        "question": item.question,
                        "answer": item.answer,
                        "metadata": item.metadata
                    }])
                    synced_count += 1
                except Exception as e:
                    logger.error(f"[sync] 同步失败: id={item.id}, error={e}")
                    failed_count += 1
        
        elif request.action == "delete":
            # 删除
            ids = [item.id for item in request.items]
            try:
                await rag_service.delete(ids)
                synced_count = len(ids)
            except Exception as e:
                logger.error(f"[sync] 删除失败: {e}")
                failed_count = len(ids)
        
        else:
            return KnowledgeSyncResponse(
                code=1001,
                message=f"不支持的操作: {request.action}"
            )
        
        logger.info(f"[sync] 完成: synced={synced_count}, failed={failed_count}")
        
        return KnowledgeSyncResponse(
            code=0,
            message="success",
            data=KnowledgeSyncData(
                synced_count=synced_count,
                failed_count=failed_count
            )
        )
        
    except Exception as e:
        logger.error(f"[sync] 失败: {e}", exc_info=True)
        return KnowledgeSyncResponse(code=5000, message=f"同步失败: {str(e)}")
