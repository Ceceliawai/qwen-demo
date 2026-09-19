# qwen-demo 开发进度

> 最后更新：2026-09-19  
> 当前阶段：第一阶段进行中，工程骨架已建立  
> 当前里程碑：第一阶段——文本会话最小闭环

## 1. 当前结论

需求、架构边界、代码归属规则和技术栈已经确认，可以开始工程初始化与第一阶段开发。

当前仓库仍是文档型仓库：尚无前后端源码、依赖文件、数据库或测试配置。

## 2. 已确认事项

- [x] 产品定位与功能范围
- [x] 五阶段演进计划
- [x] 模块化单体方案
- [x] 轻量 DDD 与端口适配器边界
- [x] 稳定业务模块：`project`、`conversation`、`resource`、`execution`
- [x] 技术能力边界：`model`、`retrieval`、`document`、`vision`、`storage`
- [x] 新增代码归属规则
- [x] 第一阶段不引入 LangGraph
- [x] Python + FastAPI 后端
- [x] React + TypeScript + Vite 前端
- [x] SQLite + SQLAlchemy Async + Alembic
- [x] 百炼 OpenAI-compatible API + Qwen
- [x] uv + pnpm 包管理方案
- [x] 后端与前端基础测试工具

## 3. 总体里程碑

| 阶段 | 目标 | 状态 |
|---|---|---|
| 0. 设计与准备 | 需求、架构、归属规则、技术选型 | 已完成 |
| 1. 文本会话 | Project、Conversation、多轮问答、历史、流式输出 | 进行中 |
| 2. 上下文管理 | Token 预算、摘要和长会话压缩 | 未开始 |
| 3. 联网搜索 | LangGraph、网页搜索、Citation | 未开始 |
| 4. 多模态资源 | 文件上传、文档解析、图片理解 | 未开始 |
| 5. 项目知识库 | 切块、Embedding、索引、RAG、长期记忆 | 未开始 |

状态只允许使用：`未开始`、`进行中`、`阻塞`、`已完成`。只有代码实现、相应测试和文档同步都完成后，阶段才可标记为已完成。

## 4. 第一阶段范围

### 4.1 工程基础

- [x] 初始化根目录工程配置
- [x] 初始化 `apps/server`
- [x] 初始化 `apps/web`
- [x] 配置 uv、`pyproject.toml` 和 `uv.lock`
- [x] 配置 pnpm、前端 `package.json` 和 `pnpm-lock.yaml`
- [x] 配置 Ruff、Pyright、pytest
- [x] 配置 ESLint、Prettier、Vitest
- [x] 添加 `.gitignore` 和 `.env.example`
- [x] 添加本地启动说明

### 4.2 后端基础设施

- [x] 建立 FastAPI 应用和 `/health` 接口
- [x] 建立 `bootstrap/config` 配置读取
- [x] 建立 `bootstrap/container` 手工依赖装配位置
- [ ] 建立 SQLAlchemy Async Session
- [ ] 建立 Alembic 迁移
- [ ] 建立统一错误响应
- [x] 建立 API v1 Router

### 4.3 Project 模块

- [ ] 定义 Project 聚合和 Repository
- [ ] 实现 CreateProject
- [ ] 实现 ListProjects
- [ ] 实现基础持久化
- [ ] 实现 Project HTTP API
- [ ] 增加领域和集成测试

### 4.4 Conversation 模块

- [ ] 定义 Conversation、Message 和 Citation
- [ ] 定义 ConversationRepository
- [ ] 实现 CreateConversation
- [ ] 实现 ListConversations
- [ ] 实现 GetConversation
- [ ] 实现 SendMessage
- [ ] 实现消息和会话持久化
- [ ] 实现 Conversation HTTP API
- [ ] 增加领域和应用测试

### 4.5 Execution 与 Model

- [ ] 定义 `ResponseExecutor`
- [ ] 定义 `ExecutionRequest` 和 `ExecutionResult`
- [ ] 定义 `ModelGateway` 和标准模型类型
- [ ] 实现 `DirectResponseExecutor`
- [ ] 实现 `BailianQwenAdapter`
- [ ] 实现 Qwen 流式事件转换
- [ ] 使用 Fake Model 完成应用测试
- [ ] 使用受控方式完成百炼连通性验证

### 4.6 前端

- [ ] 建立应用路由和整体工作台布局
- [ ] 实现项目列表和项目切换
- [ ] 实现会话列表和会话切换
- [ ] 实现消息列表
- [ ] 实现 Composer
- [ ] 实现 SSE 流式消息展示
- [ ] 实现 Loading、Empty 和 Error 状态
- [ ] 实现 Markdown 渲染
- [ ] 增加关键组件测试

### 4.7 第一阶段验收

- [ ] 可以本地创建项目
- [ ] 可以在项目下创建会话
- [ ] 可以发送文本并获得 Qwen 流式回答
- [ ] 可以围绕同一会话连续追问
- [ ] 刷新页面后历史仍存在
- [ ] API Key 不进入前端、不写入仓库
- [ ] 后端单元和集成测试通过
- [ ] 前端测试和构建通过
- [ ] README 本地启动步骤有效
- [ ] 架构测试或静态检查能发现关键越界依赖

## 5. 当前工作项

| 字段 | 当前值 |
|---|---|
| 工作项 | Conversation 前端页面与百炼接入前的收尾 |
| 状态 | 待开始 |
| 前置条件 | 已满足 |
| 下一动作 | 根据 Conversation API 实现会话列表、消息列表和发送消息页面 |
| 阻塞项 | 无 |
| 最近验证 | Conversation 后端测试/Lint/类型检查及前端测试/Lint/构建全部通过 |

一次只把一个可验证的工作项标记为“进行中”。如果开发中发现新的任务，先加入第一阶段清单，再决定是否属于当前工作项。

## 6. 已知延期项

以下内容不属于第一阶段，不应在初始化时顺带实现：

- LangGraph 和 AgentRun 持久化
- 联网搜索
- 上下文压缩
- 文件上传
- PDF、DOCX 和图片解析
- Embedding 和向量数据库
- RAG 与项目知识库
- Redis、Celery 或消息队列
- 用户系统和权限
- 在线部署

可以定义稳定接口，但不得为了这些能力提前引入依赖或空实现。

## 7. 开发记录

### 2026-09-19：建立工程骨架与 Conversation 后端闭环

完成：

- 创建根 `pyproject.toml`、pnpm workspace、版本声明和环境变量模板
- 创建 FastAPI 应用、API v1 Router、配置读取和健康检查
- 创建四个业务模块与五个 capability 的稳定顶层包
- 创建 React/Vite 页面、后端健康查询和基础测试
- 配置 pytest、Ruff、Pyright、ESLint、Prettier 和 Vitest
- 补充本地安装、启动和验证命令
- 实现 `Conversation`、`Message` 领域模型
- 实现 SQLite/SQLAlchemy Async Repository 和 Alembic 初始迁移
- 实现创建、列表、详情和发送消息 API
- 接入 `FakeResponseExecutor`，完成用户消息和助手消息持久化
- 增加领域、API 和配置测试

验证：

- Python 源码已通过 `python3 -m compileall -q apps/server/src tests`
- `pyproject.toml`、JSON 和 JavaScript 配置已通过离线语法解析
- 已使用项目 `.venv` 中的 Python 3.12.12 和已安装依赖完成验证
- `pytest`：4 passed
- `ruff check .`：通过
- `pyright`：0 errors
- ESLint：通过
- Vitest：1 passed
- TypeScript 编译与 Vite 生产构建：通过
- `/api/v1/health` 已通过 HTTPX ASGI 集成测试；当前沙箱禁止绑定本地监听端口，因此未在沙箱中执行真实端口访问

修复：

- 配置 Pyright 使用 `.venv` 和 `apps/server/src`
- 修复 Python import 排序
- 将 jest-dom 测试入口切换为 Vitest 版本
- 拆分 Vite 与 Vitest 配置，解决 Vite 5/6 类型冲突
- 保持项目 pnpm 9.15 锁定版本，与现有 `node_modules` 元数据一致
- 修复 Repository 类型注解与 Ruff Python 3.12 规则

下一步：

- 实现 Conversation 前端页面，并将 Fake 回复替换为百炼 Qwen

### 2026-09-17：设计阶段完成

完成：

- 整理产品需求和五阶段范围
- 确认模块化单体、轻量 DDD 和端口适配器架构
- 固定 `project`、`conversation`、`resource`、`execution` 边界
- 定义工具、压缩、检索、流式输出等代码归属规则
- 确认 Python/FastAPI、React/Vite、SQLite/SQLAlchemy 技术栈
- 确认通过百炼 OpenAI-compatible API 调用 Qwen

验证：

- README、需求、架构和技术选型口径已人工检查
- 当前没有源代码，因此没有执行构建或自动化测试

下一步：

- 初始化第一阶段工程骨架和质量工具

## 8. 后续继续开发的更新规则

每次开发开始时：

1. 阅读本文件的“当前工作项”和最近一条开发记录
2. 查看工作区现状，确认是否有未提交或未完成的修改
3. 将当前工作项状态改为“进行中”
4. 不顺带实现“已知延期项”

每次开发结束时：

1. 更新相关 checklist
2. 记录实际修改内容
3. 记录执行过的测试、构建或手工验证命令及结果
4. 写明未解决问题和阻塞原因
5. 指定唯一、具体的下一动作
6. 如果产生新架构决策，同步更新架构或技术选型文档

进度记录必须反映真实状态：代码已写但尚未验证，应保持“进行中”，不能标记为“已完成”。

## 9. 文档索引

- 产品需求：[requirements.md](./requirements.md)
- 最终架构：[architecture.md](./architecture.md)
- 技术选型：[technology-stack.md](./technology-stack.md)
- 开发进度：当前文件
