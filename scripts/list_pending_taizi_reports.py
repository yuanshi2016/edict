#!/usr/bin/env python3
"""扫描“已完成但尚未由太子回奏皇上”的任务。

用途：
1. 作为“待回奏提醒”兜底机制的数据源
2. 只提醒太子，不直接替太子向皇上回奏

输出默认给出 pending 任务清单；
加 --reminder 可输出适合发给太子的提醒文本。
"""
from __future__ import annotations

import argparse
import pathlib
from typing import Any, Dict, List

from shared_context import read_json, resolve_shared_data_root


def load_tasks() -> List[Dict[str, Any]]:
    root = resolve_shared_data_root()
    path = pathlib.Path(root) / 'tasks_source.json'
    data = read_json(path, [])
    return data if isinstance(data, list) else []


def is_reported_to_emperor(task: Dict[str, Any]) -> bool:
    for item in reversed(task.get('flow_log', []) or []):
        if not isinstance(item, dict):
            continue
        if item.get('from') == '太子' and item.get('to') == '皇上':
            return True
    return False


def is_pending(task: Dict[str, Any]) -> bool:
    task_id = str(task.get('id') or '').strip()
    if not task_id.startswith('JJC-'):
        return False
    state = str(task.get('state') or '').strip()
    if state not in {'Done', 'Assigned', 'Doing'}:
        return False
    if is_reported_to_emperor(task):
        return False
    # 若最近一条流转已到太子，或任务已 done 但仍未见太子→皇上，也应提醒
    flows = task.get('flow_log', []) or []
    last_to = ''
    if flows and isinstance(flows[-1], dict):
        last_to = str(flows[-1].get('to') or '').strip()
    return state == 'Done' or last_to == '太子'


def build_rows(tasks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for task in tasks:
        if not is_pending(task):
            continue
        rows.append({
            'task_id': str(task.get('id') or '').strip(),
            'title': str(task.get('title') or '').strip(),
            'state': str(task.get('state') or '').strip(),
            'now': str(task.get('now') or '').strip(),
            'output': str(task.get('output') or '').strip(),
        })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description='扫描待太子回奏任务')
    ap.add_argument('--task-id', default='', help='仅检查指定任务ID')
    ap.add_argument('--reminder', action='store_true', help='输出提醒太子的消息模板')
    args = ap.parse_args()

    rows = build_rows(load_tasks())
    if args.task_id:
        rows = [row for row in rows if row['task_id'] == args.task_id]

    if args.reminder:
        if not rows:
            print('NO_PENDING_TAIZI_REPORTS')
            return
        print('🔔 待回奏提醒')
        for row in rows:
            print(f"任务ID: {row['task_id']}")
            print(f"标题: {row['title']}")
            print(f"当前状态: {row['state']}")
            if row['now']:
                print(f"当前进展: {row['now']}")
            if row['output']:
                print(f"产出路径: {row['output']}")
            print('请太子核对是否已在皇上原对话回奏；若未回奏，请按正式模板回奏。')
            print('---')
        return

    if not rows:
        print('NO_PENDING_TAIZI_REPORTS')
        return

    for row in rows:
        print(f"{row['task_id']}\t{row['state']}\t{row['title']}\t{row['output']}")


if __name__ == '__main__':
    main()
