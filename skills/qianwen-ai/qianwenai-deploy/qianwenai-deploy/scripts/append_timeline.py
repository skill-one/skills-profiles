#!/usr/bin/env python3
"""向项目目录的 app_timeline.jsonl 追加一条应用事件。详见 reference/deploy/14_app_timeline.md"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

EVENTS = ("deploy", "hotfix", "observe", "operate")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", required=True,
                    help="写入方：qianwenai-deploy / qianwenai-observe / qianwenai-operate")
    ap.add_argument("--event", required=True, choices=EVENTS)
    ap.add_argument("--summary", required=True, help="一行人类可读摘要")
    ap.add_argument("--data-json", default=None,
                    help="事件专属字段的 JSON 对象，合并进记录（不得含密码/签名 URL）")
    ap.add_argument("--project-root", default=".")
    args = ap.parse_args()

    entry = {
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "skill": args.skill,
        "event": args.event,
        "summary": args.summary,
    }
    if args.data_json:
        extra = json.loads(args.data_json)
        if not isinstance(extra, dict):
            sys.exit("--data-json 必须是 JSON 对象")
        entry.update(extra)

    path = Path(args.project_root).resolve() / "app_timeline.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    os.chmod(path, 0o600)
    print(str(path))


if __name__ == "__main__":
    main()
