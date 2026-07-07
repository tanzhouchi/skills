"""接口变更同步守卫。

支持 hook 的运行时在文件写入类工具运行后触发此脚本。脚本读取标准输入中的
工具事件 JSON，若发现接口相关文件发生变更，则写入同步标记文件。
代理在完成任务前必须读取该标记，并通过 Apifox MCP 同步接口文档。
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

API_RELATED_PREFIXES = (
    "app/api/",
    "app/schema/",
    "app/core/response.py",
    "app/core/exception_handlers.py",
)

API_RELATED_SUFFIXES = (
    "_api.py",
    "router.py",
)

MARKER_PATH = Path(".codex/apifox-sync-required.json")


def _extract_paths(payload: dict[str, Any]) -> set[str]:
    """从 hook 事件中尽量提取被修改文件路径。"""
    paths: set[str] = set()
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        for key in ("file_path", "path"):
            value = tool_input.get(key)
            if isinstance(value, str):
                paths.add(value)
        for key in ("edits", "files"):
            value = tool_input.get(key)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        nested = item.get("file_path") or item.get("path")
                        if isinstance(nested, str):
                            paths.add(nested)
    return {path.lstrip("./") for path in paths}


def _is_api_related(path: str) -> bool:
    """判断文件路径是否可能影响 API 文档。"""
    normalized = path.lstrip("./")
    return (
        normalized.startswith(API_RELATED_PREFIXES)
        or normalized.endswith(API_RELATED_SUFFIXES)
    )


def main() -> int:
    """入口：发现接口相关变更则写入同步标记。"""
    raw = sys.stdin.read().strip()
    if not raw:
        return 0
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0
    paths = sorted(path for path in _extract_paths(payload) if _is_api_related(path))
    if not paths:
        return 0

    MARKER_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing: dict[str, Any] = {}
    if MARKER_PATH.exists():
        try:
            existing = json.loads(MARKER_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}

    changed_paths = sorted(set(existing.get("changed_paths", [])) | set(paths))
    marker = {
        "required": True,
        "reason": "检测到 API 路径、请求方式、入参或响应可能发生变更，必须通过 Apifox MCP 同步接口文档。",
        "changed_paths": changed_paths,
        "updated_at": datetime.now(tz=timezone.utc).isoformat(),
    }
    MARKER_PATH.write_text(
        json.dumps(marker, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
