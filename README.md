# qwen-demo

一个用于面试展示和 GitHub 展示的 Qwen 全栈 Demo。

完整文档：

- [需求设计文档](./docs/requirements.md)
- [架构设计文档](./docs/architecture.md)
- [技术栈选型](./docs/technology-stack.md)
- [开发进度](./docs/development-progress.md)

## 项目简介

这个项目不只是演示一次模型调用，而是希望做出一个相对完整的 AI 应用 Demo：

- 前后端分离
- 多轮会话
- 联网搜索增强
- 图片和文档输入
- 后续扩展到项目级上下文与知识库

它的产品形态是一个本地部署的多模态 AI 工作台。

## 架构口径

当前架构采用：

- 模块化单体
- 轻量 DDD
- 端口适配器架构
- `LangGraph` 按需承载轻量 Agent 编排

可以把系统简单理解成三层：

- 业务模块：`project`、`conversation`、`resource`、`execution`
- 执行入口：`ResponseExecutor` 隔离直接问答与 Agent 工作流
- 技术能力：`model`、`retrieval`、`document`、`vision`、`storage`

第一版使用直接模型执行器，不强制引入 LangGraph；后续搜索、多模态和 RAG 都在既有边界内增量扩展，不迁移已有模块。

## 核心能力

- 文本问答
- 多轮对话与会话历史
- 上下文压缩
- 联网搜索开关与来源链接展示
- 图片附件输入与理解
- 文档附件输入与理解
- 项目维度组织会话

## 输入类型

- 文本
- 图片
- 文档：`md`、`pdf`、`docx`

图片和文档默认作为当前消息附件使用，后续再按需要扩展为项目级资源。

## 阶段规划

1. 基础框架 + 文本问答最小闭环
2. 会话管理 + 上下文压缩
3. 联网搜索 + 来源链接
4. 图片 / 文档上传、理解、问答
5. RAG / 项目级上下文

## 当前状态

需求、最终架构、代码归属规则和技术栈已经确认。

Monorepo、FastAPI 后端和 React/Vite 前端骨架已经建立。当前正在完成依赖锁定与自动化验证，详细状态以[开发进度文档](./docs/development-progress.md)为准。

## 本地开发

环境要求：

- Python 3.12+
- uv
- Node.js 22+
- pnpm 9+

首次安装：

```bash
cp .env.example .env
uv sync --python 3.12
pnpm install
```

分别启动后端和前端：

```bash
pnpm dev:server
pnpm dev:web
```

- Web：http://localhost:5173
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/v1/health

验证命令：

```bash
uv run pytest
uv run ruff check .
uv run pyright
pnpm lint
pnpm test
pnpm build
```

## 暂不包含

- 用户系统
- 在线部署
- 多用户隔离
- 复杂权限设计
- 多 Agent 协作
