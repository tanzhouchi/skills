# 个人定制技能仓库

这个仓库用于存放个人定制的 Agent Skills。每个技能使用独立目录维护，目录内以 `SKILL.md` 为入口，并按需附带模板、脚本、参考资料和测试提示。

## 仓库结构

```text
.
├── README.md
├── .gitignore
└── fastapi-project-builder/
    ├── SKILL.md
    ├── test-prompts.json
    └── assets/
```

## 当前技能

| 技能 | 用途 | 关键文件 |
| --- | --- | --- |
| `fastapi-project-builder` | 搭建、初始化、重构或规范化 `FastAPI` 后端项目骨架 | `fastapi-project-builder/SKILL.md` |

## 技能目录约定

每个技能目录推荐保留以下结构：

```text
skill-name/
  SKILL.md
  test-prompts.json
  assets/
  references/
  scripts/
```

- `SKILL.md`：技能入口，包含触发条件、执行流程、失败分支、检查点和禁止事项。
- `test-prompts.json`：典型使用场景，用于评估技能效果。
- `assets/`：可复用模板、默认配置、文档骨架和生成素材。
- `references/`：较长参考资料，避免把主技能写得过重。
- `scripts/`：技能执行或验证所需脚本。

不存在对应内容时，不需要强行创建空目录。

## 维护规则

1. 修改技能前先阅读对应 `SKILL.md`，确认不改变技能的核心用途。
2. 新增模板、脚本或参考资料时，优先放入对应技能目录，不放到仓库根目录。
3. 技能说明应保持运行时中立，避免绑定单一工具或本地业务项目路径。
4. 禁止提交真实 token、密码、私有地址、本地环境文件和运行日志。
5. 修改技能后同步更新 `test-prompts.json`，保证常见使用场景仍被覆盖。
6. 若技能包含生成模板，模板内不得混入无关业务领域概念。

## 本地忽略策略

`.gitignore` 会忽略本地缓存、虚拟环境、依赖目录、构建产物、日志、密钥文件、`.claude/`、`.codex/` 和 `docs/superpowers/` 等运行或规划产物。

以下内容应提交：

- `SKILL.md`
- `test-prompts.json`
- `assets/`
- `templates/`
- `scripts/`
- `references/`
- 技能目录内的正式文档

## 快速检查

提交前运行：

```bash
git status --short
git check-ignore -v path/to/file
```

如果涉及 `Python` 脚本，先按仓库规则检测本地虚拟环境；当前目录无 `.venv`、`venv`、`env` 时，使用：

```bash
/Users/tansir/.venv/bin/python
```
