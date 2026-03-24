# AI Customer Service Agent

> LangGraph-based AI Agent for Customer Service

## 项目说明

Python Agent 服务，负责 AI 客服的核心能力：
- 情绪检测
- 问题分类
- 智能转人工
- RAG 知识检索
- 回复生成

## 技术栈

- Python 3.11
- FastAPI
- LangChain + LangGraph
- ChromaDB
- OpenAI API

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入 OPENAI_API_KEY
```

### 3. 启动服务

```bash
uvicorn app.main:app --reload --port 8000
```

### 4. 访问文档

打开浏览器访问：http://localhost:8000/docs

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/v1/agent/process | POST | 处理用户消息 |
| /api/v1/agent/check-handoff | POST | 检查是否需要转人工 |
| /api/v1/agent/state/{session_id} | GET | 获取会话状态 |
| /api/v1/agent/knowledge/sync | POST | 同步知识库 |
| /health | GET | 健康检查 |

## 项目结构

```
python-agent-service/
├── app/
│   ├── main.py                 # FastAPI 入口
│   ├── config.py               # 配置
│   ├── api/routes/             # API 路由
│   ├── agent/                  # Agent 相关
│   │   ├── graph.py            # LangGraph 定义
│   │   ├── state.py            # 状态定义
│   │   └── nodes/              # 节点实现
│   ├── services/               # 服务层
│   └── models/                 # 数据模型
├── tests/                      # 测试
├── requirements.txt
├── Dockerfile
└── README.md
```

## 环境变量

| 变量 | 说明 | 必填 |
|------|------|------|
| LLM_PROVIDER | LLM 提供商 (openai/claude) | 是 |
| OPENAI_API_KEY | OpenAI API Key | 是 |
| JAVA_SERVICE_URL | Java 服务地址 | 否 |

## Docker 部署

```bash
# 构建镜像
docker build -t python-agent-service .

# 运行容器
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-xxx python-agent-service
```

## 关联项目

- Java 服务：`/Users/xiaohuzhuanshu/java/projects/backend/ai-customer-service1`

---

**版本**: v3.0.0
**创建时间**: 2026-03-23