#!/usr/bin/env python3
import argparse
import json
import pathlib
import subprocess
import sys
import time

from shared_context import fail_closed, load_shared_manifest, preflight_repo, resolve_primary_repo, resolve_report_root


def load_message(args):
    if args.message:
        return args.message
    if args.message_file:
        return pathlib.Path(args.message_file).read_text(encoding='utf-8')
    raise SystemExit('必须提供 --message 或 --message-file')


def build_cmd(agent_id, message, timeout, thinking):
    cmd = [
        'openclaw', 'agent',
        '--agent', agent_id,
        '--message', message,
        '--timeout', str(timeout),
    ]
    if thinking:
        cmd += ['--thinking', thinking]
    return cmd


def run_sync(cmd, retries, retry_delay, timeout):
    last = None
    for attempt in range(1, retries + 2):
        try:
            proc = subprocess.run(
                cmd,
                text=True,
                capture_output=True,
                timeout=timeout + 30,
            )
        except subprocess.TimeoutExpired as e:
            proc = None
            last = {
                'ok': False,
                'returncode': 124,
                'stdout': e.stdout or '',
                'stderr': e.stderr or f'派发超时（>{timeout + 30}s）',
                'attempt': attempt,
            }
        else:
            last = {
                'ok': proc.returncode == 0,
                'returncode': proc.returncode,
                'stdout': proc.stdout or '',
                'stderr': proc.stderr or '',
                'attempt': attempt,
            }
            if proc.returncode == 0:
                return last

        if attempt < retries + 1:
            time.sleep(retry_delay)
    return last


def run_background(cmd, agent_id):
    ts = time.strftime('%Y%m%d-%H%M%S')
    log_file = pathlib.Path('/tmp') / f'openclaw-agent-dispatch-{agent_id}-{ts}.log'
    with log_file.open('w', encoding='utf-8') as fh:
        proc = subprocess.Popen(
            cmd,
            text=True,
            stdout=fh,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    return {
        'ok': True,
        'status': 'started',
        'pid': proc.pid,
        'logFile': str(log_file),
    }


def mark_block(task_id: str, reason: str) -> None:
    if not task_id:
        return
    try:
        script = pathlib.Path(__file__).with_name('kanban_update.py')
        subprocess.run(
            ['python3', str(script), 'block', task_id, reason],
            text=True,
            capture_output=True,
            check=False,
        )
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser(description='通过 openclaw agent 向指定省部发起稳定派发，避免依赖临时 subagent session。')
    ap.add_argument('agent_id', help='目标 agent id，例如 zhongshu / menxia / shangshu / bingbu')
    ap.add_argument('--message', help='直接传入消息文本')
    ap.add_argument('--message-file', help='从文件读取消息文本')
    ap.add_argument('--task-id', default='', help='可选：任务ID，仅用于输出标识')
    ap.add_argument('--timeout', type=int, default=600, help='openclaw agent 超时秒数')
    ap.add_argument('--thinking', default='', help='可选 thinking 级别')
    ap.add_argument('--retries', type=int, default=1, help='失败后的重试次数')
    ap.add_argument('--retry-delay', type=int, default=3, help='重试间隔秒数')
    ap.add_argument('--background', action='store_true', help='后台派发，立即返回 pid/log 路径')
    ap.add_argument('--repo', default='', help='目标仓库；默认共享 manifest 中的主验收仓')
    ap.add_argument('--allow-dirty', action='store_true', help='允许主验收仓工作树非干净（默认阻断）')
    args = ap.parse_args()

    manifest = load_shared_manifest()
    target_repo = pathlib.Path(args.repo) if args.repo else resolve_primary_repo(manifest)
    try:
        preflight = preflight_repo(target_repo, require_clean=not args.allow_dirty)
    except SystemExit:
        mark_block(args.task_id, 'agent_dispatch preflight 失败，已 fail-closed')
        raise
    except Exception as exc:
        mark_block(args.task_id, f'agent_dispatch preflight 异常: {exc}')
        fail_closed(f'agent_dispatch preflight 异常：{exc}')

    message = load_message(args)
    cmd = build_cmd(args.agent_id, message, args.timeout, args.thinking)

    if args.background:
        result = run_background(cmd, args.agent_id)
        result.update({
            'agent': args.agent_id,
            'taskId': args.task_id,
            'preflight': preflight,
            'reportRoot': str(resolve_report_root(manifest)),
        })
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    result = run_sync(cmd, args.retries, args.retry_delay, args.timeout)
    ok = bool(result and result.get('ok'))
    prefix = f"[dispatch:{args.agent_id}]"
    if args.task_id:
        prefix += f"[{args.task_id}]"

    if ok:
        stdout = (result.get('stdout') or '').strip()
        stderr = (result.get('stderr') or '').strip()
        if stdout:
            print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)
        print(json.dumps({'preflight': preflight, 'reportRoot': str(resolve_report_root(manifest))}, ensure_ascii=False))
        return

    mark_block(args.task_id, f'派发失败 rc={result.get("returncode")}')
    print(f"{prefix} 派发失败（attempt={result.get('attempt')}, rc={result.get('returncode')}）", file=sys.stderr)
    if result.get('stdout'):
        print(result['stdout'].strip(), file=sys.stderr)
    if result.get('stderr'):
        print(result['stderr'].strip(), file=sys.stderr)
    sys.exit(result.get('returncode') or 1)


if __name__ == '__main__':
    main()
