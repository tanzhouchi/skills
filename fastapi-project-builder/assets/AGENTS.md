# FastAPI 项目代理工作基准

本文件用于约束代理在本项目中的开发行为。所有代理必须优先遵守本文件。

---

## 1. 最高优先级硬约束

1. **全中文输出**：回复正文、文档说明、代码注释和交接说明必须使用简体中文。专有名词、文件名、路径、代码关键字、命令、配置字段除外。
2. **静默自主执行**：读取文件、搜索目录、检查环境、查看状态时直接执行，禁止反复询问是否继续。
3. **数字书写规则**：版本号、数量、容量、时长、端口、并发数、进程数、连接数、行数、日期、时间、百分比等可量化信息必须使用阿拉伯数字。
4. **Python 环境**：执行任何 Python 命令前，先检测当前目录是否存在 `.venv`、`venv`、`env`。若不存在，停止执行 Python 命令并提示先创建项目本地虚拟环境。禁止写入个人机器上的固定解释器路径。
5. **保护用户改动**：不得回滚、覆盖或删除自己未创建的改动。遇到无关脏文件时忽略；遇到相关脏文件时先读懂再增量修改。

---

## 2. 项目结构

默认后端结构：

```text
app/
  api/v1/
  common/
  core/
  integration/
  model/
  repository/
  schema/
  service/
  lifespan.py
  main.py
config/
  config.yaml
  config-local.yaml
migrations/
tests/
docs/
.mcp.json
```

职责边界：

| 目录 | 职责 |
|------|------|
| `app/api/v1` | 路由、请求解析、响应封装 |
| `app/service` | 业务逻辑编排 |
| `app/repository` | 数据库访问 |
| `app/model` | `SQLAlchemy` 模型 |
| `app/schema` | `Pydantic` 请求和响应模型 |
| `app/core` | 配置、数据库、日志、异常、响应、中间件 |
| `app/common` | 通用工具 |
| `app/integration` | 外部系统适配层 |

依赖方向：

```text
api -> service -> repository -> model
```

禁止跨层调用。新增模块时优先延续既有目录和命名模式。

---

## 3. 代码质量规则

1. 所有函数与方法必须尽量标注类型注解。
2. 禁止裸 `except`，捕获异常必须指定类型并记录日志。
3. 禁止在生产代码中导入测试假件。
4. 注释解释为什么这样设计，不解释代码字面含义。
5. 禁止使用 `print` 调试，统一使用日志。
6. 禁止硬编码密钥、密码、令牌和私有地址。
7. SQL 操作必须使用 ORM 或参数化查询，禁止字符串拼接 SQL。
8. 禁止提交调试代码、临时注释或无关格式化变更。
9. `app/main.py`、`app/lifespan.py`、`app/api/v1/health_api.py`、`app/api/v1/router.py`、`app/core/config.py`、`app/core/database.py`、`app/core/middleware.py`、`app/core/logger.py`、`app/core/response.py`、`app/core/exceptions.py`、`app/core/exception_handlers.py`、`app/common/datetime.py`、`app/model/base.py`、`migrations/env.py`、`tests/conftest.py`、`tests/integration/test_health.py` 和 `pyproject.toml` 必须沿用项目初始模板，禁止随意重写公共入口和基础设施。
10. 所有 ORM 模型字段必须有中文字段说明，`Column` 或 `mapped_column` 必须设置 `comment`。

---

## 4. API 与响应规则

1. API 默认使用 `app.core.response` 的辅助函数构建统一响应；`GET /health` 是唯一例外，固定裸返回 `{"status": "ok"}`，不使用统一响应包装。
2. 路由文件只做请求解析、依赖注入和响应封装，禁止写业务逻辑。
3. 新增路由应提供清晰的 `summary`。
4. 请求和响应模型集中放在 `app/schema`。
5. 错误通过统一异常处理器返回，不在路由中拼接错误响应。
6. 禁止改变统一响应字段名、时间格式和递归序列化行为，除非有明确迁移方案和测试覆盖。
7. 新增、变更或删除 API 路径、请求方式、入参、响应结构或响应示例后，必须通过 Apifox MCP 同步接口文档。

默认成功响应：

```json
{
  "code": 200,
  "data": {},
  "message": "请求成功",
  "timestamp": "2026-07-07 12:00:00"
}
```

---

## 5. 配置、日志与数据库

1. 配置加载顺序为 `config/config-local.yaml` 优先，回退到 `config/config.yaml`。
2. 实际加载顺序为 `config/config.yaml`、`config/config-local.yaml`、`DATABASE_URL`、`DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME`，右侧覆盖左侧。
3. 本地敏感配置写入 `config-local.yaml`，禁止提交真实凭据。
4. 应用代码通过统一日志模块获取日志实例。
5. HTTP 请求追踪默认使用纯 `ASGI` 请求编号中间件，禁止改写为 `BaseHTTPMiddleware`。
6. 需要数据库时使用 `SQLAlchemy 2.0` 和 `Alembic`。
7. 修改 ORM 模型后，必须同步迁移文件并执行迁移验证。
8. 日志模块必须保留正常日志与错误日志双文件分离、按日期切割、`init_log()` 幂等初始化和 `get_business_logger()` 统一入口。

---

## 6. 外部系统适配层

1. 每个外部系统必须放入 `app/integration/<provider>/` 独立子目录。
2. `integration` 只处理协议、认证、请求、响应解析和错误映射。
3. 业务判断放在 `service`，禁止写入 `integration`。
4. `repository` 禁止调用 `integration`。
5. 外部响应必须先转换为内部 DTO，再交给 `service`。
6. 禁止在适配层硬编码密钥、令牌、私有地址。

---

## 7. MCP 与 Apifox 同步

MCP 是可选能力，只有项目创建时明确启用才应存在 `.mcp.json`。

启用规则：

- 启用 Apifox 时必须配置 `APIFOX_TOKEN` 和 `APIFOX_PROJECT_ID`。
- 启用 PostgreSQL MCP 时必须配置主机、端口、用户、密码、数据库和访问模式。
- 启用 MySQL MCP 时必须配置主机、端口、用户、密码和数据库。
- 禁止提交真实 token、密码和私有地址；如需提交配置，只能使用占位符或本地私有配置。

接口同步规则：

1. 修改 `app/api/`、`app/schema/`、`app/core/response.py` 或 `app/core/exception_handlers.py` 后，检查 `.codex/apifox-sync-required.json`。
2. 若该标记存在且 `required=true`，任务完成前必须通过 Apifox MCP 同步接口文档。
3. 同步必须覆盖路径、请求方式、入参、响应、响应示例和废弃接口状态。
4. 同步完成后删除标记文件或将 `required` 改为 `false`。
5. 交付时必须说明 Apifox 同步结果。

---

## 8. Model 字段说明

新增或修改 ORM 模型时：

- 每个字段必须设置中文 `comment`。
- 主键、外键、枚举、状态、金额、时间、软删除字段都必须说明业务含义。
- 迁移文件必须保留字段说明。
- 迁移后必须确认数据库真实字段说明与模型一致。

---

## 9. 文档规则

文档目录结构固定为：

```text
docs/
  specs/
  plans/
  contracts/
  runbooks/
  reference/
```

目录职责：

- `specs/`：方案、架构设计、关键决策。
- `plans/`：分阶段实施计划和任务拆解。
- `contracts/`：API、外部系统、数据结构契约。
- `runbooks/`：本地开发、部署、排障、运维手册。
- `reference/`：易踩陷阱、调研资料、长期参考。

接口、配置、部署或外部系统契约变化时，必须同步更新对应文档。

---

## 10. 验证命令

每次代码变更后至少执行：

```bash
$PY -m pytest tests/ -q
$PY -m ruff check .
$PY -m mypy app
```

若只修改文档，可不运行 Python 测试，但必须检查差异，确认未误改生产代码。

---

## 11. Git 规则

提交类型：

| 类型 | 用途 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修复 |
| `refactor` | 重构 |
| `docs` | 文档 |
| `test` | 测试 |
| `chore` | 配置或维护 |

每次提交只做一类变更，提交前确认 `git status --short` 中没有意外文件。

---

## 12. 交付规则

完成任务时汇报：

- 创建或修改的文件。
- 关键行为变化。
- 已执行的验证命令。
- Apifox MCP 是否已同步，若未同步必须说明原因。
- 未执行验证的原因。
- 当前是否还有未提交改动。
