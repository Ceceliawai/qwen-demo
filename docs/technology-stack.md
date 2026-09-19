# qwen-demo 技术栈选型

> 状态：已确认  
> 最后更新：2026-09-17  
> 适用范围：第一阶段及后续搜索、多模态、RAG 增量

## 1. 选型目标

技术栈需要满足：

- 第一版能够快速完成本地文本会话闭环
- 对异步模型调用和流式输出有良好支持
- 适合后续接入 LangGraph、文档解析和 RAG
- 框架类型不泄漏到 Domain 和 Application
- 更换模型、数据库或搜索供应商时，只增加或替换 Adapter
- 依赖尽量少，未进入开发阶段的能力不提前安装

## 2. 技术栈总览

| 范围 | 选型 | 状态 |
|---|---|---|
| 后端语言 | Python 3.12+ | 已确认 |
| API 框架 | FastAPI | 已确认 |
| ASGI Server | Uvicorn | 已确认 |
| 数据校验 | Pydantic v2 | 已确认 |
| 配置管理 | pydantic-settings | 已确认 |
| ORM | SQLAlchemy 2.x Async | 已确认 |
| 数据迁移 | Alembic | 已确认 |
| 第一阶段数据库 | SQLite + aiosqlite | 已确认 |
| 后续生产型数据库 | PostgreSQL + asyncpg | 需要时增加 Adapter |
| Qwen 平台 | 阿里云百炼 | 已确认 |
| Qwen 调用方式 | OpenAI-compatible API | 已确认 |
| 模型客户端 | openai Python SDK，使用 `AsyncOpenAI` | 已确认 |
| 通用 HTTP 客户端 | HTTPX | 已确认 |
| 流式协议 | 第一阶段 HTTP SSE | 已确认 |
| Python 包管理 | uv | 已确认 |
| 前端语言 | TypeScript | 已确认 |
| 前端框架 | React | 已确认 |
| 前端构建工具 | Vite | 已确认 |
| 服务端状态 | TanStack Query | 已确认 |
| 前端局部状态 | Zustand | 已确认 |
| 前端路由 | React Router | 已确认 |
| Markdown 渲染 | react-markdown + remark-gfm | 已确认 |
| 前端包管理 | pnpm 9+ | 已确认 |
| 后端测试 | pytest + pytest-asyncio | 已确认 |
| Python 质量工具 | Ruff + Pyright | 已确认 |
| 前端测试 | Vitest + React Testing Library | 已确认 |
| 端到端测试 | Playwright | 完整展示版按需加入 |
| Agent Runtime | LangGraph | 搜索阶段按需加入 |

具体依赖版本在初始化工程时使用当前兼容稳定版本，并由 `uv.lock` 和 `pnpm-lock.yaml` 锁定。升级依赖不能顺带改变架构边界。

## 3. 后端选型

### 3.1 Python 与 FastAPI

后端采用 Python，主要原因是 Qwen、LangGraph、文档解析和向量检索生态完整。FastAPI 负责：

- HTTP Router 和请求响应 DTO
- OpenAPI 文档
- 异步请求处理
- SSE 流式响应入口
- 生命周期管理

FastAPI 只能出现在 `presentation` 和 `bootstrap`，Domain 与 Application 不得依赖 FastAPI 类型。

### 3.2 Pydantic

Pydantic 用于：

- HTTP 请求和响应 DTO
- 环境变量和配置校验
- 外部能力 Adapter 的边界数据校验

Pydantic Model 不直接充当领域实体或 SQLAlchemy ORM Model。

### 3.3 SQLAlchemy 与 Alembic

SQLAlchemy 2.x 使用异步模式。第一阶段采用 SQLite 和 `aiosqlite`，以降低本地运行成本。

约束：

- ORM Model 放在所属模块的 `infrastructure/persistence`
- Repository 接口放在所属模块的 `domain/repositories`
- Repository 实现放在所属模块的 `infrastructure/persistence`
- Alembic 负责 Schema 版本管理
- 领域实体、ORM Model、HTTP DTO 三者分离
- SQL 尽量保持 SQLite/PostgreSQL 可移植性

未来增加 PostgreSQL 时使用 `asyncpg`，通过配置和基础设施 Adapter 切换，不改变 Use Case 与领域模型。

### 3.4 异步与依赖注入

- API、模型、数据库和外部 HTTP 调用统一采用 `async/await`
- 第一阶段不引入第三方依赖注入框架
- 对象装配统一放在 `bootstrap/container`
- FastAPI Depends 只负责取得已经装配好的应用服务
- Domain 不感知事件循环和异步框架

## 4. 百炼与 Qwen 接入

项目使用阿里云百炼 API Key，通过百炼的 OpenAI-compatible API 调用 Qwen。

默认调用链：

```text
ModelGateway
→ BailianQwenAdapter
→ openai.AsyncOpenAI
→ 百炼 OpenAI-compatible API
```

国内区域默认配置形式：

```env
MODEL_PROVIDER=bailian
BAILIAN_API_KEY=
BAILIAN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
BAILIAN_CHAT_MODEL=qwen-plus
```

规则：

- Secret 只存在于本地 `.env` 或部署环境变量
- `.env` 必须加入 `.gitignore`
- 仓库只提交不含真实 Key 的 `.env.example`
- 国内站和国际站使用各自区域的 Base URL 与 API Key
- 模型名称必须通过配置传入，不硬编码在 Use Case 中
- 百炼或 OpenAI SDK 类型不得越过 `BailianQwenAdapter`
- 第一阶段不安装 `dashscope` SDK
- 如果未来只有原生 DashScope SDK 才支持某项能力，则新增 Adapter，不修改 `ModelGateway`

第一阶段默认模型建议使用 `qwen-plus`。实际模型是否可用以百炼账号、区域和控制台授权为准。

### 4.1 流式输出

第一阶段使用百炼流式响应，并通过 FastAPI SSE 返回前端：

```text
BailianQwenAdapter stream
→ ModelStreamEvent
→ ResponseExecutor
→ SendMessage
→ SSE presentation adapter
→ Web client
```

第一阶段优先使用 FastAPI `StreamingResponse`。只有需要标准 SSE 重连、event ID 等能力时，再增加 `sse-starlette`。

## 5. 第一阶段 Python 依赖

生产依赖：

```toml
dependencies = [
    "fastapi",
    "uvicorn[standard]",
    "pydantic",
    "pydantic-settings",
    "sqlalchemy[asyncio]",
    "alembic",
    "aiosqlite",
    "openai",
    "httpx",
]
```

开发依赖：

```toml
[dependency-groups]
dev = [
    "pytest",
    "pytest-asyncio",
    "pytest-cov",
    "ruff",
    "pyright",
]
```

`httpx` 同时用于外部 HTTP 调用和 FastAPI 集成测试。

## 6. 前端选型

前端使用 React + TypeScript + Vite，实现项目列表、会话列表和聊天工作区。

核心依赖：

```text
react
react-dom
react-router-dom
@tanstack/react-query
zustand
react-markdown
remark-gfm
```

职责划分：

- TanStack Query：项目、会话、历史消息等服务端状态
- Zustand：当前选择、输入草稿、流式 UI 等局部跨组件状态
- React Router：页面和项目/会话路由
- react-markdown：模型回答渲染
- `services`：HTTP/SSE 客户端和 DTO 转换
- `features`：用户功能和界面状态

前端质量工具：

- TypeScript 严格模式
- ESLint
- Prettier
- Vitest
- React Testing Library

视觉组件库和 CSS 方案在实现第一个页面前确认。它们不会改变 feature 边界；未确认前不提前引入 UI 组件库。

## 7. API 与数据约定

- 普通接口使用 REST + JSON
- 模型回答使用 SSE 流式传输
- API 路径统一带版本前缀，例如 `/api/v1`
- 外部使用字符串 ID，不暴露数据库自增语义
- 时间统一使用 UTC 存储和 ISO 8601 传输
- API DTO 使用明确的请求/响应类型，不直接返回 ORM Model
- 错误响应使用统一错误码、消息和可选详情结构

第一阶段不引入 GraphQL、gRPC、WebSocket 或消息队列。

## 8. 分阶段增加的依赖

### 搜索与 Agent 阶段

- `langgraph`
- 搜索供应商需要的 HTTP Adapter；优先使用 HTTPX

不默认引入完整 LangChain 依赖集合。

### 文档与图片阶段

- `python-multipart`：文件上传
- `pypdf`：基础 PDF 文本提取
- `python-docx`：DOCX 提取
- 图片处理库仅在真实需求出现后添加

如果 PDF 版面或表格处理要求提高，再评估 `pymupdf` 或 `pdfplumber`。

### PostgreSQL 与 RAG 阶段

- `asyncpg`：PostgreSQL 异步驱动
- `pgvector` 或最终选定向量数据库客户端
- Embedding 继续通过项目内部 `EmbeddingGateway` 调用

向量数据库在 RAG 阶段通过实际数据规模和部署成本选择，现在不锁定具体产品。

## 9. 明确不使用或暂缓的技术

第一阶段不引入：

- Streamlit 或 Gradio：不符合完整前后端工作台定位
- Django：当前 API 与 AI 流式场景使用 FastAPI 更轻
- Celery、Redis、消息队列：暂无后台分布式任务需求
- 第三方依赖注入框架：手工装配足够清晰
- LangGraph：在搜索或多步工具阶段再加入
- LangChain 全家桶：只引入确实需要的独立能力
- DashScope SDK：OpenAI-compatible 接口已经满足第一阶段
- Elasticsearch 或独立向量数据库：RAG 阶段再决策

## 10. 锁文件与开发环境

工程初始化后必须提交：

- `pyproject.toml`
- `uv.lock`
- `package.json`
- `pnpm-lock.yaml`
- Python 与 Node 版本声明
- `.env.example`

不得提交：

- `.env`
- 百炼 API Key
- 本地数据库文件
- 上传文件和生成内容
- Python/Node 构建缓存

## 11. 选型结论

第一阶段的正式技术组合是：

```text
Backend:
Python + FastAPI + Pydantic + SQLAlchemy Async + Alembic
SQLite + OpenAI SDK + 百炼 Qwen + uv

Frontend:
React + TypeScript + Vite
TanStack Query + Zustand + React Router

Quality:
pytest + Ruff + Pyright
Vitest + React Testing Library
```

后续 LangGraph、PostgreSQL、文档解析和 RAG 依赖在对应阶段按需添加，不能提前侵入第一阶段代码。
