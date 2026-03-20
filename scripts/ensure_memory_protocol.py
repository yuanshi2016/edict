#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import sys

BLOCK = '''
## 记忆协同补充协议
1. 涉及既往决策、偏好、日期、阻塞、待办、交付标准，先查 `MEMORY.md` 与 `memory/*.md`。
2. 协作时，除正常回奏外，把值得长期记住的事实/决策/偏好/阻塞写入 `memory/meta/pending-memories.md`。
3. 子执行方只提交记忆提案，不擅自改写他部 `MEMORY.md`。
4. 回奏至少同步：当前结论、证据路径、建议记忆项。
5. 不确定时明确写“待主责确认”，禁止臆造历史。
'''.strip()


def ensure_block(path: pathlib.Path) -> bool:
    if not path.exists():
        raise FileNotFoundError(path)
    text = path.read_text(encoding='utf-8')
    if '## 记忆协同补充协议' in text:
        return False
    new_text = text.rstrip() + '\n\n' + BLOCK + '\n'
    path.write_text(new_text, encoding='utf-8')
    return True


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print('Usage: ensure_memory_protocol.py <AGENTS.md> [<AGENTS.md> ...]', file=sys.stderr)
        return 2
    changed = 0
    for arg in argv[1:]:
        p = pathlib.Path(arg)
        if ensure_block(p):
            changed += 1
            print(f'UPDATED {p}')
        else:
            print(f'SKIP {p}')
    print(f'changed={changed}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
