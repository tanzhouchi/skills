---
name: fastapi-project-builder
description: 当用户要搭建、初始化、重构或规范化 FastAPI 后端项目、Python 接口服务、REST 服务、数据库接口项目、API 骨架或后台服务目录结构时使用。
---

# FastAPI 项目搭建器

## 核心原则

使用此技能搭建一个干净、可运行、可测试、可迁移的 `FastAPI` 后端项目。技能自带工程骨架、公共模板和质量规则，禁止依赖任何外部业务项目路径，禁止从业务项目复制代码或领域概念。

## 内置工程约定

本技能已经把通用工程经验沉淀为以下固定约定。执行时直接按本技能和 `assets/` 模板生成项目，不再读取外部业务项目作为参考。

| 约定 | 必须保留的做法 | 禁止偏离 |
| --- | --- | --- |
| 应用入口 | `create_app()` 保持纯工厂函数，启动日志和资源初始化放到 `lifespan` 或模块级幂等初始化 | 禁止在 `create_app()` 中启动后台任务、写大量日志或连接外部系统 |
| 路由聚合 | `app/api/v1/router.py` 只聚合业务路由，健康检查可独立挂载 | 禁止在路由聚合文件写业务逻辑 |
| 请求追踪 | 默认注入 `X-Request-ID`，响应返回 `x-request-id` 和 `x-process-time` | 禁止使用会吞异常链路的中间件写法 |
| 配置分层 | `config-local.yaml` 覆盖 `config.yaml`，敏感值只走本地配置或环境变量 | 禁止把真实凭据写入模板、示例或仓库 |
| 数据库会话 | 每个请求使用独立 `Session`，启用 `pool_pre_ping=True`，禁止业务层创建引擎 | 禁止跨请求复用会话或在路由层直接提交事务 |
| 迁移一致性 | 修改模型后同步迁移文件，并用测试验证模型字段、迁移字段和字段说明一致 | 禁止只有模型变更没有迁移验证 |
| 测试隔离 | 测试夹具使用独立应用实例、独立数据库连接和自动回滚事务 | 禁止测试依赖真实外部服务或生产配置 |
| 外部适配 | 外部系统放入 `app/integration/<provider>/`，先转内部 DTO 再进入 `service` | 禁止 `repository` 调用外部系统 |
| 文档交接 | 方案、计划、契约、运行手册、参考资料分目录存放 | 禁止只在对话中记录架构决策 |

## 适用场景

- 用户要求“搭一个 `FastAPI` 项目”“初始化后端服务”“创建接口服务骨架”。
- 用户要求把现有散乱后端整理成分层 `FastAPI` 项目。
- 用户要求加入 `SQLAlchemy`、`Alembic`、统一响应、统一异常、健康检查、配置文件、测试和代码检查。
- 用户没有明确技术细节，但目标明显是 `Python` 后端接口服务。

## 不适用场景

- 只修改单个已有接口，且不涉及项目骨架。
- 用户明确要求使用其他框架。
- 用户要求复制模板项目完整业务功能。

## 执行前检查

先检查当前目录环境：

```bash
pwd
find . -maxdepth 2 -type d \( -name ".venv" -o -name "venv" -o -name "env" \)
```

如果当前目录有 `.venv`、`venv` 或 `env`，后续 `Python` 命令优先使用其中的解释器。若不存在，默认使用 `/Users/tansir/.venv`。

解释器解析顺序：

```bash
if [ -x .venv/bin/python ]; then
  PY=.venv/bin/python
elif [ -x venv/bin/python ]; then
  PY=venv/bin/python
elif [ -x env/bin/python ]; then
  PY=env/bin/python
else
  PY=/Users/tansir/.venv/bin/python
fi
```

## 🔴 CHECKPOINT：需求决策

生成或重构文件前，必须先得到以下决策；已有用户输入可直接采用，缺失项按默认值执行，涉及凭据或外部连接时必须暂停补齐。

| 决策项 | 默认值 | 缺失时动作 |
| --- | --- | --- |
| 项目标识 | 当前目录名转小写连字符 | 写入 README 并用于日志标识 |
| 服务端口 | `8000` | 写入 `config.yaml` 与启动命令 |
| 数据库 | 启用 | 用户明确要求轻量项目时关闭 |
| 异步任务 | 关闭 | 用户明确要求后才加入 `Celery` 和 `Redis` |
| MCP | 关闭 | 用户明确选择且配置完整后才生成 |
| 现有代码处理 | 保留业务逻辑 | 先盘点入口，再迁移到分层结构 |

如果用户要求启用 Apifox、PostgreSQL 或 MySQL MCP，但缺少 token、项目编号、主机、账号、密码或数据库名，停止生成 `.mcp.json` 和 hook，只继续基础项目骨架；交付说明中列出缺失项。

## 默认目录结构

新项目默认生成以下结构：

```text
app/
  api/
    v1/
      __init__.py
      health_api.py
      router.py
  core/
    __init__.py
    config.py
    database.py
    exceptions.py
    exception_handlers.py
    logger.py
    middleware.py
    response.py
  integration/
    __init__.py
    README.md
  model/
    __init__.py
    base.py
  repository/
    __init__.py
  schema/
    __init__.py
  service/
    __init__.py
  common/
    __init__.py
    datetime.py
  __init__.py
  lifespan.py
  main.py
migrations/
  versions/
  env.py
  script.py.mako
config/
  config.yaml
  config-local.yaml
docs/
  README.md
  specs/
  plans/
  contracts/
  runbooks/
  reference/
tests/
  integration/
    test_health.py
  unit/
CLAUDE.md
AGENTS.md
pyproject.toml
README.md
alembic.ini
```

如果用户要求轻量项目，省略 `repository`、`model`、`migrations` 和数据库依赖；否则默认包含数据库骨架。

可选启用 Apifox 与数据库 MCP 时，额外生成：

```text
.mcp.json
.claude/settings.json
scripts/hooks/apifox_sync_guard.py
scripts/hooks/README.md
```

## 分层规则

按以下依赖方向组织代码：

```text
api -> service -> repository -> model
service -> integration
```

职责约定：

| 层 | 目录 | 职责 | 禁止事项 |
| --- | --- | --- | --- |
| 路由 | `app/api/v1` | 请求解析、参数校验、响应封装 | 禁止写业务逻辑，禁止直接操作数据库 |
| 业务 | `app/service` | 业务编排和规则判断 | 禁止直接创建数据库连接 |
| 数据 | `app/repository` | 数据库访问 | 禁止调用外部系统，禁止写业务判断 |
| 模型 | `app/model` | `SQLAlchemy` 模型定义 | 禁止写业务方法 |
| 契约 | `app/schema` | `Pydantic` 请求和响应模型 | 禁止访问数据库 |
| 基础设施 | `app/core` | 配置、数据库、日志、异常、响应、中间件 | 禁止混入业务域逻辑 |

## 默认依赖

默认 `pyproject.toml` 包含：

```toml
[project]
requires-python = ">=3.12"
dependencies = [
  "fastapi>=0.115.0",
  "uvicorn[standard]>=0.30.0",
  "pydantic>=2.8.0",
  "sqlalchemy>=2.0.30",
  "alembic>=1.13.0",
  "psycopg[binary]>=3.2.0",
  "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.2.0",
  "pytest-asyncio>=0.23.0",
  "ruff>=0.5.0",
  "mypy>=1.10.0",
  "types-PyYAML>=6.0",
]
```

只有用户明确需要异步任务时，才加入：

```toml
"celery[redis]>=5.4.0"
```

只有用户明确需要缓存、队列或分布式锁时，才加入 `Redis` 相关配置。

## 搭建步骤

1. 完成“需求决策”检查点，记录项目名称、端口、数据库、异步任务、MCP 与现有代码处理方式。
2. 创建目录结构和空包文件。
3. 从本技能的 `assets/CLAUDE.md` 和 `assets/AGENTS.md` 生成目标项目根目录的 `CLAUDE.md` 与 `AGENTS.md`。
4. 从 `assets/templates/config/` 生成 `config.yaml` 与 `config-local.yaml`，只替换项目名、端口和数据库名等占位符。
5. 从 `assets/templates/docs/` 生成 `docs/` 目录结构和文档规则。
6. 创建 `pyproject.toml`，写入依赖、`pytest`、`ruff`、`mypy` 配置。
7. 创建配置文件读取逻辑，使用 `config-local.yaml` 优先、`config.yaml` 兜底。
8. 从 `assets/templates/app/main.py` 生成应用入口，只替换项目描述占位符。
9. 创建 `/health` 健康检查。
10. 从 `assets/templates/app/core/exceptions.py` 和 `assets/templates/app/core/exception_handlers.py` 生成业务异常与异常处理器，禁止按描述重新实现。
11. 从 `assets/templates/app/core/response.py` 和 `assets/templates/app/common/datetime.py` 生成统一响应模块和时间工具，禁止按描述重新实现。
12. 从 `assets/templates/app/core/logger.py` 生成日志模块，只允许把 `__PROJECT_SLUG__` 替换为目标项目标识。
13. 从 `assets/templates/app/integration/` 生成外部系统适配层入口和规则文档。
14. 如需要数据库，创建 `SQLAlchemy` 引擎、会话依赖、模型基类和 `Alembic` 骨架；所有 ORM 字段必须带字段说明。
15. 如启用 MCP，从 `assets/templates/optional/mcp/` 与 `assets/templates/optional/hooks/` 生成 `.mcp.json`、运行时 hook 和同步守卫脚本；配置缺失时执行“失败分支与兜底”表中的 MCP 分支。
16. 创建最小集成测试，至少覆盖 `/health`。
17. 写入 `README.md`，包含安装、配置、启动、迁移和校验命令。
18. 运行校验命令，修复直到通过。

## 失败分支与兜底

| 触发条件 | 一线修复 | 仍失败兜底 |
| --- | --- | --- |
| 当前目录已有项目文件 | 先列出现有入口、配置、测试和依赖文件 | 新建前缀目录 `<项目名>/`，不覆盖用户文件 |
| 本地虚拟环境不存在 | 使用 `/Users/tansir/.venv/bin/python` | 若该解释器也不存在，停止执行 Python 命令并汇报缺失路径 |
| 固定模板文件缺失 | 用 `rg --files fastapi-project-builder/assets` 定位同名模板 | 停止生成对应文件，记录缺失模板，禁止自由仿写固定模板 |
| 用户要求轻量项目 | 关闭数据库、模型、仓储、迁移和数据库依赖 | README 写明后续启用数据库所需文件 |
| 现有业务代码结构混乱 | 先建立 `api/service/schema/integration` 边界，再逐步迁移 | 保留原文件，新增适配层，交付说明列出未迁移项 |
| MCP 配置不完整 | 只生成基础项目，不生成 `.mcp.json`、hook 和真实连接配置 | 在 README 的待配置段落列出缺失变量 |
| 依赖安装失败 | 记录失败包名、解释器路径和完整命令 | 跳过后续校验，完成汇报中标记校验未通过 |
| `pytest` 失败 | 先修健康检查、配置读取和导入路径 | 保留失败输出摘要，禁止声称项目可运行 |
| `ruff` 或 `mypy` 失败 | 修复格式、类型和导入问题后重跑 | 交付说明列出剩余错误文件和命令 |
| Apifox 同步失败 | 保留导出的 OpenAPI 和差异说明 | 不删除 `.codex/apifox-sync-required.json`，汇报同步未完成 |

## 🔴 CHECKPOINT：生成前复核

写入文件前必须确认：

- 固定模板路径存在，且模板生成文件只替换允许的占位符。
- 目标目录中已有同名文件时，先读取内容，再决定合并、跳过或创建备份。
- 启用数据库时，`pyproject.toml`、`app/core/database.py`、`app/model/base.py`、`migrations/` 和测试说明同时出现。
- 关闭数据库时，不生成数据库依赖、迁移目录和仓储层空壳。
- 启用 MCP 时，凭据使用用户提供值或环境变量占位符，禁止使用任何现有项目真实值。

## 代理指令文件

每个由本技能搭建的项目根目录都必须生成：

```text
CLAUDE.md
AGENTS.md
```

生成规则：

- `CLAUDE.md` 只保留最小引导内容，指向并遵守 `AGENTS.md`，不要写重复规则。
- `AGENTS.md` 是目标项目的唯一事实来源，必须保留通用开发硬约束和 `FastAPI` 项目工程规则。
- 若目标项目有特殊业务约束，只追加到 `AGENTS.md` 的对应章节，不要改写 `CLAUDE.md` 的职责。
- 默认模板来自本技能目录的 `assets/CLAUDE.md` 与 `assets/AGENTS.md`。
- 如果用户明确要求不同规则，以用户项目约束为准，但仍保持 `CLAUDE.md -> AGENTS.md` 的引导结构。

## 统一响应格式

统一响应模块必须来自固定模板：

```text
assets/templates/app/core/response.py -> app/core/response.py
assets/templates/app/common/datetime.py -> app/common/datetime.py
```

禁止仅根据下列 JSON 结构自由生成实现。允许改动的范围只有项目确有业务需要时追加辅助函数；不得改变已有类名、函数名、字段名、时间格式和递归序列化行为。

成功响应：

```json
{
  "code": 200,
  "data": {},
  "message": "请求成功",
  "timestamp": "2026-07-07 12:00:00"
}
```

分页响应：

```json
{
  "code": 200,
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5,
    "items": []
  },
  "message": "请求成功",
  "timestamp": "2026-07-07 12:00:00"
}
```

错误响应：

```json
{
  "code": 400,
  "data": null,
  "message": "错误消息",
  "timestamp": "2026-07-07 12:00:00"
}
```

## 业务异常和入口模板

业务异常、异常处理器和应用入口必须来自固定模板：

```text
assets/templates/app/core/exceptions.py -> app/core/exceptions.py
assets/templates/app/core/exception_handlers.py -> app/core/exception_handlers.py
assets/templates/app/main.py -> app/main.py
```

生成目标项目文件时：

- `app/core/exceptions.py` 的异常类结构固定，默认包含 `AppBaseError`、`NotFoundError`、`ConflictError`、`ForbiddenError`、`ValidationError`。
- `app/core/exception_handlers.py` 必须统一捕获业务异常、请求校验异常、标准 HTTP 异常和未捕获异常。
- `app/main.py` 必须保留 `create_app()` 工厂函数、模块级 `init_log()`、`RequestIDMiddleware`、统一异常处理器注册、健康检查路由和业务路由聚合。
- `app/main.py` 唯一允许替换 `__PROJECT_DESCRIPTION__`。

## 配置策略

配置文件必须来自固定模板：

```text
assets/templates/config/config.yaml -> config/config.yaml
assets/templates/config/config-local.yaml -> config/config-local.yaml
```

模板必须包含 `app`、`database`、`redis`、`log` 4 组配置。禁止默认加入具体业务系统配置，例如第三方平台、内部系统、邮件平台、支付平台等。

允许替换的占位符：

- `__PROJECT_DISPLAY_NAME__`
- `__PROJECT_SLUG_UNDERSCORE__`

读取顺序：

1. `config/config-local.yaml`
2. `config/config.yaml`
3. 测试环境可用环境变量覆盖数据库地址。

配置对象至少包含：

- `app.name`
- `app.version`
- `app.debug`
- `app.host`
- `app.port`
- `app.api_prefix`
- `database.host`
- `database.port`
- `database.user`
- `database.password`
- `database.database`
- `database.pool_size`
- `database.max_overflow`
- `database.pool_timeout`
- `database.pool_recycle`
- `database.echo`
- `log.console`
- `log.path`

## 外部系统适配层

外部系统适配层必须生成固定入口和规则文档：

```text
assets/templates/app/integration/__init__.py -> app/integration/__init__.py
assets/templates/app/integration/README.md -> app/integration/README.md
```

适配层规则：

- 每个外部系统使用独立子目录，例如 `app/integration/<provider>/`。
- 适配层只处理协议、认证、请求、响应解析和错误映射。
- 业务判断放在 `service`，禁止写入 `integration`。
- `repository` 禁止调用 `integration`。
- 外部响应必须先转成内部 DTO，再交给 `service`。

## 文档结构规则

文档目录必须来自固定模板：

```text
assets/templates/docs/README.md -> docs/README.md
assets/templates/docs/specs/ -> docs/specs/
assets/templates/docs/plans/ -> docs/plans/
assets/templates/docs/contracts/ -> docs/contracts/
assets/templates/docs/runbooks/ -> docs/runbooks/
assets/templates/docs/reference/ -> docs/reference/
```

目录职责：

- `docs/specs/`：方案、架构设计、关键决策。
- `docs/plans/`：分阶段实施计划和任务拆解。
- `docs/contracts/`：API、外部系统、数据结构契约。
- `docs/runbooks/`：本地开发、部署、排障、运维手册。
- `docs/reference/`：易踩陷阱、调研资料、长期参考。

## 日志和中间件

日志模块必须来自固定模板：

```text
assets/templates/app/core/logger.py -> app/core/logger.py
```

生成目标项目文件时，唯一允许替换的是 `__PROJECT_SLUG__`，替换为小写连字符项目标识，例如 `inventory-api`。日志结构必须保留：

- `ErrorOnlyFilter` 和 `BelowErrorFilter`。
- `init_log()` 幂等初始化。
- `get_business_logger()` 统一入口。
- 正常日志与错误日志双文件分离。
- 按日期切割，保留 `30` 天。
- `uvicorn.access`、`uvicorn.error`、`uvicorn.asgi` 纳入同一 handler 体系。

默认加入请求编号中间件：

- 读取或生成 `X-Request-ID`。
- 响应头写入 `x-request-id`。
- 响应头写入 `x-process-time`。
- 请求开始、请求完成、异常路径写日志。

优先使用纯 `ASGI` 中间件，避免使用 `BaseHTTPMiddleware` 处理异常传播。

## 数据库规则

需要数据库时：

- 使用 `SQLAlchemy 2.0`。
- 使用 `sessionmaker` 管理每个请求的会话。
- 使用 `pool_pre_ping=True`。
- 测试夹具必须使用独立连接和事务回滚，保证测试之间数据隔离。
- 数据库迁移使用 `Alembic`。
- 模型集中继承 `app/model/base.py` 中的统一基类。
- 所有 ORM 模型字段必须有字段说明：
  - `Column` 风格字段必须设置 `comment="中文字段说明"`。
  - `mapped_column` 风格字段必须设置 `comment="中文字段说明"`。
  - 外键、索引字段、状态字段、时间字段也必须写明业务含义。
  - 迁移文件必须保留字段说明，禁止模型有说明但数据库迁移丢失说明。
  - 生成模型后必须检查 `app/model/`、迁移文件和数据库实际字段说明是否一致。

## 可选 MCP 和接口同步钩子

默认不启用 MCP。只有用户明确选择后才生成 `.mcp.json` 和 hook。

启用前必须询问以下配置，不得使用现有项目中的真实 token、账号、密码或地址：

Apifox：

- `APIFOX_TOKEN`
- `APIFOX_PROJECT_ID`

PostgreSQL：

- `PG_HOST`
- `PG_PORT`
- `PG_USER`
- `PG_PASSWORD`
- `PG_DATABASE`
- `PG_MCP_MODE`，默认值 `readwrite`

MySQL：

- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DATABASE`

生成规则：

- 选择 Apifox + PostgreSQL 时，使用 `assets/templates/optional/mcp/apifox-postgres.mcp.json` 生成 `.mcp.json`。
- 选择 Apifox + MySQL 时，使用 `assets/templates/optional/mcp/apifox-mysql.mcp.json` 生成 `.mcp.json`。
- 选择 Apifox 但不选择数据库时，只保留 `.mcp.json` 中的 `apifox` server。
- 选择数据库但不选择 Apifox 时，只保留 `.mcp.json` 中对应数据库 server，且不生成 Apifox 同步 hook。
- 启用 Apifox 时，必须同时从 `assets/templates/optional/hooks/` 生成 `.claude/settings.json` 和 `scripts/hooks/apifox_sync_guard.py`。

接口同步硬规则：

- 当新增、变更或删除 API 的路径、请求方式、入参、响应结构、响应示例、统一响应格式时，必须触发 Apifox 同步流程。
- hook 检测到相关文件变更后会写入 `.codex/apifox-sync-required.json`。
- 任务结束前若该标记存在且 `required=true`，必须通过 Apifox MCP 执行同步。
- 同步流程必须先导出 Apifox 当前 OpenAPI，再对比代码生成的新 OpenAPI，最后导入更新。
- 同步完成后删除 `.codex/apifox-sync-required.json` 或将 `required` 改为 `false`，并在交付说明中写明同步结果。

## 测试规则

至少创建：

```text
tests/conftest.py
tests/integration/test_health.py
tests/unit/test_migration_schema_alignment.py
tests/unit/
```

健康检查测试应验证：

- `GET /health` 返回 `200`。
- 响应体包含 `{"status": "ok"}`。

数据库启用时，`tests/conftest.py` 必须提供独立应用实例、独立数据库连接和事务回滚夹具；`tests/unit/test_migration_schema_alignment.py` 必须验证核心模型字段、迁移脚本字段和字段说明保持一致。

## 校验命令

每次搭建或修改后执行：

```bash
$PY -m pytest tests/ -q
$PY -m ruff check .
$PY -m mypy app
```

如果没有安装依赖，先执行：

```bash
$PY -m pip install -e ".[dev]"
```

## 可选模块

仅在用户明确要求时加入：

- 异步任务：`Celery`、`Redis`、`app/task`。
- 定时任务：`app/scheduler`。
- 外部系统适配：`app/integration`。
- 用户权限：`app/api/v1/system`、`app/service/system`。
- MCP：Apifox、PostgreSQL、MySQL 和接口同步 hook。

加入可选模块时，必须同时添加最小测试和运行说明。

## 禁止事项

- 禁止读取或复制任何本地业务项目作为模板来源；只能使用本技能目录内的 `assets/`。
- 禁止引入第三方平台、内部系统、支付、订单、文件处理、报表、权限等模板业务概念，除非用户明确要求。
- 禁止把任何现有项目 `.mcp.json` 中的真实 token、项目编号、数据库账号、密码或地址复制到新项目。
- 禁止自由生成 `app/main.py`、`app/core/logger.py`、`app/core/response.py`、`app/core/exceptions.py`、`app/core/exception_handlers.py`、`app/common/datetime.py`、`config/config.yaml`、`config/config-local.yaml` 和 `docs/README.md`；必须使用本技能固定模板。
- 禁止创建没有字段说明的 ORM 模型字段。
- 禁止接口变更后跳过 Apifox MCP 同步。
- 禁止把路由写成业务逻辑集中地。
- 禁止在生产代码中导入测试假件。
- 禁止在代码中硬编码密钥、密码、令牌。
- 禁止使用 `print` 调试，统一使用日志。
- 禁止裸 `except`，必须捕获明确异常并记录日志。
- 禁止只创建文件不运行校验。

## 🔴 CHECKPOINT：完成前硬检查

交付前必须逐项确认：

- 已按解释器解析顺序设置 `$PY`，并在汇报中写明实际路径。
- 已执行 `$PY -m pytest tests/ -q`、`$PY -m ruff check .`、`$PY -m mypy app`，或写明未执行原因。
- 数据库启用状态、异步任务启用状态、MCP 启用状态与用户需求一致。
- 固定模板文件未被自由重写，所有允许替换的占位符已完成替换。
- 存在未迁移代码、未完成同步或未通过校验时，完成汇报必须把它们列为未完成项。

## 完成汇报

完成时汇报：

- 创建或修改了哪些关键文件。
- 项目默认端口和启动命令。
- 数据库和异步任务是否启用。
- 已运行的校验命令及结果。
- 如有未运行校验，说明原因。
