#!/usr/bin/env python3
from __future__ import annotations
import pathlib, sys

BLOCK = """
## 六部通讯执行补充协议
1. **职责路由固定**：工部=开发/架构/代码；兵部=基础设施/部署/安全；户部=数据分析/报表/成本；礼部=文档/UI/对外沟通；刑部=审查/测试/合规；吏部=人事/Agent管理/培训。
2. **统一接令口径**：仅接收尚书省转派；若任务超出本部职责，回复“请尚书省转派至 X 部”，不得跨部直连。
3. **统一回奏模板**：回奏必须包含 `任务ID / 结果 / 证据/文件路径 / 阻塞项 / 建议记忆项`。
4. **统一取证边界**：若使用跨会话取证，必须记录 `Purpose / Minimum Scope / Maximum Range / SessionKey / Timestamp / Quoted Summary / Follow-up`，禁止无边界扫全量历史。
5. **统一记忆提案口径**：本部只写本部 `memory/meta/pending-memories.md`；执行经验、阻塞、职责边界必须形成提案；由尚书省汇总，中书省周度收敛，太子月度抽检。
6. **不确定时**：明确写“待主责确认”，禁止臆造其他部门结论或越权代答。
""".strip()

def ensure(path: pathlib.Path) -> bool:
    txt = path.read_text(encoding='utf-8')
    if '## 六部通讯执行补充协议' in txt:
        return False
    path.write_text(txt.rstrip() + '

' + BLOCK + '
', encoding='utf-8')
    return True

if __name__ == '__main__':
    changed = 0
    for arg in sys.argv[1:]:
        p = pathlib.Path(arg)
        if ensure(p):
            print(f'UPDATED {p}')
            changed += 1
        else:
            print(f'SKIP {p}')
    print(f'changed={changed}')
