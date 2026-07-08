# 接口同步钩子

启用 Apifox MCP 后，项目会生成：

```text
.claude/settings.json
scripts/hooks/apifox_sync_guard.py
```

当代理修改 `app/api/`、`app/schema/`、`app/core/response.py` 或 `app/core/exception_handlers.py` 时，钩子会写入：

```text
.codex/apifox-sync-required.json
```

该文件表示本次任务完成前必须通过 Apifox MCP 同步接口文档。

钩子命令会从当前工作目录向上查找 `scripts/hooks/apifox_sync_guard.py` 和 `.venv`、`venv`、`env`。找不到项目虚拟环境或同步守卫脚本时给出明确错误。因此会话从仓库根目录或子服务目录启动时，都应能定位项目虚拟环境和同步守卫脚本。

同步完成后，代理必须删除该标记文件或将 `required` 改为 `false`，并在交付说明中写明已执行的 Apifox 同步动作。
