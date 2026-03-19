#!/usr/bin/env python3
"""回奏前证据护栏。

用法示例：
  python3 scripts/submit_guard.py JJC-20260319-003 \
    --repo /root/.openclaw/workspace-zhongshu/bnMarket \
    --report-path /root/.openclaw/workspace-taizi/reports/JJC-20260319-003.md \
    --test "go test ./... => pass" \
    --test "npm run build => pass" \
    --summary "机制整改首批落地"

要求：
- 强制采集 git HEAD / git status / changed files / tests / reportPath
- 缺任一关键证据直接 fail-closed
- 证据写入共享 reports/submit_guard
"""
from __future__ import annotations

import argparse
import pathlib
import sys
import time

from shared_context import (
    fail_closed,
    load_shared_manifest,
    preflight_repo,
    resolve_report_root,
    write_submit_guard_record,
)


def main() -> None:
    ap = argparse.ArgumentParser(description='回奏前证据护栏')
    ap.add_argument('task_id', help='任务ID')
    ap.add_argument('--repo', default='', help='待验收仓库，默认主验收仓')
    ap.add_argument('--report-path', required=True, help='本次回奏对应的报告/产物路径')
    ap.add_argument('--test', action='append', default=[], help='测试/构建结果，可多次传入')
    ap.add_argument('--summary', default='', help='摘要')
    ap.add_argument('--artifact', action='append', default=[], help='补充产物路径，可多次传入')
    args = ap.parse_args()

    if not args.test:
        fail_closed('submit_guard 缺少测试/构建结果（--test）')

    report_path = pathlib.Path(args.report_path)
    if not report_path.exists():
        fail_closed(f'submit_guard 报告路径不存在：{report_path}')

    manifest = load_shared_manifest()
    evidence = preflight_repo(pathlib.Path(args.repo) if args.repo else None, require_clean=False)
    if not evidence.get('gitHead'):
        fail_closed('submit_guard 未采集到 git HEAD')
    if not evidence.get('gitStatus'):
        fail_closed('submit_guard 未采集到 git status')

    payload = {
        'taskId': args.task_id,
        'summary': args.summary,
        'reportPath': str(report_path),
        'tests': args.test,
        'artifacts': args.artifact,
        'submittedAt': time.strftime('%Y-%m-%d %H:%M:%S'),
        **evidence,
    }
    out_path = write_submit_guard_record(args.task_id, payload, manifest)
    print(f'[submit_guard] ok: {out_path}')
    print(f'[submit_guard] report: {report_path}')
    print(f'[submit_guard] gitHead: {payload["gitHead"]}')


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        fail_closed(f'submit_guard 异常：{exc}')
