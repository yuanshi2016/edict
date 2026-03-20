# JJC-20260320-002 · 六部扩面执行进展

## 一、仓库基线
按皇上新旨，后续 Git 主仓库以：
- `origin = https://github.com/yuanshi2016/edict.git`

旧仓保留为：
- `upstream = https://github.com/cft0808/edict.git`

本轮执行基线：
- 本地仓库：`/www/wwwroot/edict`
- 当前基线 HEAD：`d9bad29`

---

## 二、六部扩面当前完成度
### 1. 存储层
六部工作区已全部具备固定持久化 memory 落点：
- `workspace-hubu/.memory-system-v2.conf`
- `workspace-libu/.memory-system-v2.conf`
- `workspace-bingbu/.memory-system-v2.conf`
- `workspace-xingbu/.memory-system-v2.conf`
- `workspace-gongbu/.memory-system-v2.conf`
- `workspace-libu_hr/.memory-system-v2.conf`

且均已具备固定入口：
- `workspace-*/scripts/memory_cli.sh`

### 2. 协议层
六部 `AGENTS.md` 已全部补齐“记忆协同补充协议”：
- 先查 `MEMORY.md` 与 `memory/*.md`
- 协作回奏同步写入 `memory/meta/pending-memories.md`
- 子执行方只提交提案，不改写他部核心记忆
- 回奏至少同步：当前结论、证据路径、建议记忆项

### 3. 记忆骨架层
六部缺失工作区已补齐最小记忆骨架：
- `memory/meta/pending-memories.md`
- `memory/meta/audit.log`
- `memory/meta/decay-scores.json`
- `memory/graph/index.md`

### 4. 复测层
已对六部逐个执行“新 shell / 无临时 HOME 覆盖”的持久化复测：
- hubu ✅
- libu ✅
- bingbu ✅
- xingbu ✅
- gongbu ✅
- libu_hr ✅

测试方式统一为：
- `env -i HOME=/root ... bash -lc 'cd workspace-xxx && scripts/memory_cli.sh capture/search ...'`

结果：
- 六部均成功写入各自固定目录 `workspace-xxx/clawd/memory/...`
- 说明当前扩面不依赖当前窗口、当前 shell、临时 HOME 覆盖

---

## 三、与皇上仓库同步的修改项
### 已在主源仓形成的本轮修改
1. `scripts/ensure_memory_protocol.py`
   - 用于把“记忆协同补充协议”稳定补入各部 `AGENTS.md`
2. `reports/JJC-20260320-002-six-bu-expansion.md`
   - 六部扩面执行进展报告

### 本轮在工作区落地的扩面修改
- 六部 `AGENTS.md` 已补齐记忆协同协议
- 六部 `.memory-system-v2.conf` 已固定化
- 六部 `scripts/memory_cli.sh` 已同步
- 六部最小记忆骨架已补齐

---

## 四、当前结论
### 六部扩面是否已进入可执行状态？
**是，已进入可执行状态。**

当前完成度判断：
- 存储层：6/6 完成
- 协议层：6/6 完成
- 记忆骨架层：6/6 完成
- 新 shell 持久化复测：6/6 通过

因此，本轮“扩展到六部”的基础能力已落地，不再停留在三省局部试点。

---

## 五、阻塞项
### 硬阻塞
- 无

### 软阻塞 / 下一步待办
1. 若要进一步进入“六部真实协作闭环”，需由尚书省按新协议实际派 1 轮任务，验证：
   - 六部回奏字段完整性
   - 六部 `pending-memories` 提案质量
   - 尚书省汇总质量
2. 若要做长期质量治理，可补一个统一扫描脚本，检查：
   - 重复提案
   - 空泛提案
   - 缺字段回奏

但上述两项属于增强项，不再是本轮扩面前置条件。

---

## 六、建议下一步
1. 以皇上 GitHub 仓库 `origin` 为唯一主仓继续推进
2. 将本轮六部扩面脚本与报告提交并 push 到 `origin/main`
3. 由尚书省按新协议启动 1 轮六部真实闭环试跑
4. 中书省负责汇总回奏，判断是否进入更大范围常态化运行
