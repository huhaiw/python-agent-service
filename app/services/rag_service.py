import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_openai import OpenAIEmbeddings
from app.config import settings
from typing import List, Dict
import logging
import os

logger = logging.getLogger(__name__)


class RAGService:
    """RAG 检索服务"""
    
    def __init__(self):
        # 确保数据目录存在
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
        
        # 初始化 ChromaDB
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR
        )
        
        # 初始化 Embedding
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY
        )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name="customer_service_knowledge"
        )
    
    async def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """搜索相关知识"""
        try:
            # 生成查询向量
            query_embedding = await self.embeddings.aembed_query(query)
            
            # 搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # 格式化结果
            documents = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    documents.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {}
                    })
            
            logger.info(f"[RAGService] 搜索完成: query={query[:30]}, results={len(documents)}")
            return documents
            
        except Exception as e:
            logger.error(f"[RAGService] 搜索失败: {e}")
            return []
    
    async def upsert(self, items: List[Dict]):
        """插入或更新知识"""
        try:
            for item in items:
                # 生成 Embedding
                text = f"{item['question']}\n{item['answer']}"
                embedding = await self.embeddings.aembed_query(text)
                
                # 插入
                self.collection.upsert(
                    ids=[item['id']],
                    embeddings=[embedding],
                    documents=[text],
                    metadatas=[item.get('metadata', {})]
                )
            
            logger.info(f"[RAGService] 同步完成: count={len(items)}")
            
        except Exception as e:
            logger.error(f"[RAGService] 同步失败: {e}")
            raise
    
    async def delete(self, ids: List[str]):
        """删除知识"""
        try:
            self.collection.delete(ids=ids)
            logger.info(f"[RAGService] 删除完成: count={len(ids)}")
        except Exception as e:
            logger.error(f"[RAGService] 删除失败: {e}")
            raise