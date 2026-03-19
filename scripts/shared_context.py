#!/usr/bin/env python3
"""三省六部共享上下文解析。

职责：
1. 统一共享 DATA 根路径（默认 workspace-taizi/data）
2. 严格 fail-closed：共享路径 / manifest 缺失直接阻断
3. 提供主验收仓 / 报告目录 / submit_guard 记录查询
4. 提供 git 证据采集，供 agent_dispatch / submit_guard 使用
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import time
from typing import Any, Dict, List

DEFAULT_SHARED_DATA_ROOT = pathlib.Path(
    os.environ.get('SANSHENG_SHARED_DATA_ROOT', '/root/.openclaw/workspace-taizi/data')
)
DEFAULT_MANIFEST_PATH = DEFAULT_SHARED_DATA_ROOT / 'shared_manifest.json'
DEFAULT_PRIMARY_ACCEPTANCE_REPO = '/root/.openclaw/workspace-zhongshu/bnMarket'
DEFAULT_EXPECTED_BRANCH = 'openclaw'
DEFAULT_REPORT_ROOT = '/root/.openclaw/workspace-taizi/reports'


class SharedGuardError(RuntimeError):
    pass


def fail_closed(message: str, code: int = 2) -> None:
    print(f'[FAIL-CLOSED] {message}', file=sys.stderr)
    print(f'[ESCALATE] 请升级太子/中书省：{message}', file=sys.stderr)
    raise SystemExit(code)


def read_json(path: pathlib.Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return default


def resolve_shared_data_root() -> pathlib.Path:
    root = DEFAULT_SHARED_DATA_ROOT
    if not root.exists() or not root.is_dir():
        fail_closed(f'共享 DATA 根路径缺失：{root}')
    return root


def load_shared_manifest() -> Dict[str, Any]:
    root = resolve_shared_data_root()
    path = DEFAULT_MANIFEST_PATH
    if not path.exists():
        fail_closed(f'共享 manifest 缺失：{path}')
    manifest = read_json(path, {})
    if not isinstance(manifest, dict):
        fail_closed(f'共享 manifest 非法：{path}')

    primary_repo = str(manifest.get('primaryAcceptanceRepo') or '').strip()
    if not primary_repo:
        fail_closed(f'共享 manifest 未声明 primaryAcceptanceRepo：{path}')

    report_root = str(manifest.get('reportRoot') or '').strip()
    if not report_root:
        fail_closed(f'共享 manifest 未声明 reportRoot：{path}')

    manifest['sharedDataRoot'] = str(root)
    manifest['primaryAcceptanceRepo'] = primary_repo
    manifest['reportRoot'] = report_root
    manifest.setdefault('expectedBranch', DEFAULT_EXPECTED_BRANCH)
    manifest.setdefault('readOnlyMirrorRepos', [])
    manifest.setdefault('evidence', {
        'required': ['gitHead', 'gitStatus', 'changedFiles', 'tests', 'reportPath']
    })
    return manifest


def resolve_primary_repo(manifest: Dict[str, Any] | None = None) -> pathlib.Path:
    manifest = manifest or load_shared_manifest()
    repo = pathlib.Path(manifest['primaryAcceptanceRepo'])
    if not repo.exists() or not repo.is_dir():
        fail_closed(f'主验收仓缺失：{repo}')
    if not (repo / '.git').exists():
        fail_closed(f'主验收仓不是 git 仓库：{repo}')
    return repo


def resolve_report_root(manifest: Dict[str, Any] | None = None) -> pathlib.Path:
    manifest = manifest or load_shared_manifest()
    path = pathlib.Path(manifest['reportRoot'])
    path.mkdir(parents=True, exist_ok=True)
    return path


def run_git(repo: pathlib.Path, args: List[str]) -> str:
    proc = subprocess.run(
        ['git', '-C', str(repo), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise SharedGuardError(proc.stderr.strip() or proc.stdout.strip() or f'git {args} failed')
    return (proc.stdout or '').strip()


def collect_git_evidence(repo: pathlib.Path) -> Dict[str, Any]:
    head = run_git(repo, ['rev-parse', 'HEAD'])
    branch = run_git(repo, ['rev-parse', '--abbrev-ref', 'HEAD'])
    status_short = run_git(repo, ['status', '--short'])
    status_branch = run_git(repo, ['status', '--short', '--branch'])
    changed_files = [line.strip() for line in status_short.splitlines() if line.strip()]
    return {
        'repoPath': str(repo),
        'gitHead': head,
        'branch': branch,
        'gitStatus': status_branch,
        'changedFiles': changed_files,
        'worktreeClean': len(changed_files) == 0,
    }


def preflight_repo(repo: pathlib.Path | None = None, require_clean: bool = True) -> Dict[str, Any]:
    manifest = load_shared_manifest()
    primary_repo = resolve_primary_repo(manifest)
    repo = pathlib.Path(repo) if repo else primary_repo

    if not repo.exists() or not repo.is_dir():
        fail_closed(f'目标仓库不存在：{repo}')
    if repo.resolve() != primary_repo.resolve():
        fail_closed(f'目标仓库未命中主验收仓：target={repo} primary={primary_repo}')

    evidence = collect_git_evidence(repo)
    expected_branch = str(manifest.get('expectedBranch') or DEFAULT_EXPECTED_BRANCH).strip()
    if expected_branch and evidence['branch'] != expected_branch:
        fail_closed(f'主验收仓分支不符：current={evidence["branch"]} expected={expected_branch}')
    if require_clean and not evidence['worktreeClean']:
        fail_closed('主验收仓工作树非干净状态，阻断派发')

    evidence['manifestPath'] = str(DEFAULT_MANIFEST_PATH)
    evidence['sharedDataRoot'] = str(resolve_shared_data_root())
    evidence['primaryAcceptanceRepo'] = str(primary_repo)
    return evidence


def submit_guard_dir(manifest: Dict[str, Any] | None = None) -> pathlib.Path:
    return resolve_report_root(manifest) / 'submit_guard'


def write_submit_guard_record(task_id: str, payload: Dict[str, Any], manifest: Dict[str, Any] | None = None) -> pathlib.Path:
    out_dir = submit_guard_dir(manifest)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime('%Y%m%d-%H%M%S')
    out_path = out_dir / f'{task_id}-{ts}.json'
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    latest = out_dir / f'{task_id}.latest.json'
    latest.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    return out_path


def load_submit_guard_record(task_id: str, manifest: Dict[str, Any] | None = None) -> Dict[str, Any]:
    path = submit_guard_dir(manifest) / f'{task_id}.latest.json'
    if not path.exists():
        fail_closed(f'缺少 submit_guard 证据：{path}')
    payload = read_json(path, {})
    if not isinstance(payload, dict):
        fail_closed(f'submit_guard 证据损坏：{path}')
    required = ['gitHead', 'gitStatus', 'changedFiles', 'tests', 'reportPath']
    missing = [key for key in required if key not in payload or payload.get(key) in (None, '', [])]
    if missing:
        fail_closed(f'submit_guard 证据缺字段：{missing} @ {path}')
    return payload
