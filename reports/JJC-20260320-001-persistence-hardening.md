# JJC-20260320-001 · 记忆协同持久化固化报告

## 一、目标
按皇上新旨，本轮目标不是“当前窗口临时可用”，而是把三省六部记忆协同机制改为**新开会话、新开窗口后仍稳定生效**的持久化机制。

重点修正两项：
1. `memory-system-v2` 正式存储口径落地，禁止依赖手工临时 `HOME` 覆盖
2. 清理 `pending-memories.md` 中会污染质量检测的 `Proposal #1` 模板噪声

---

## 二、持久化固化方案
### 1. openclaw.json 负责的内容（配置层）
本轮不新增 memory 路径字段到 `openclaw.json`，原因是：
- 当前 schema 已有稳定配置职责的是：
  - `agents.list[].workspace`：定义每个 Agent 的固定工作区
  - `tools.sessions.visibility`：定义跨会话可见范围
  - `tools.agentToAgent.enabled / allow`：定义 A2A 是否开启、允许哪些 Agent 通信
- 当前 schema 中**没有专用的 memory-system-v2 存储路径字段**
- 因此，memory 的持久落点应固化在“共享技能脚本 + 工作区固定配置 + 固定入口脚本”三层，而不是伪造不存在的 config 字段

### 2. 工作区固定脚本/固定模板负责的内容（执行层）
在每个 `workspace-*` 下固定两类持久件：
1. `.memory-system-v2.conf`
   - 固定定义：`MEMORY_DIR=/root/.openclaw/workspace-xxx/clawd/memory`
   - 作用：给每个 Agent/workspace 一个**固定、可重启后复用**的 memory-system-v2 存储目录
2. `scripts/memory_cli.sh`
   - 固定入口脚本，不依赖人工临时 export
   - 作用：自动以当前 workspace 为根，调用共享技能目录中的 `memory-cli.sh`

### 3. 共享技能目录负责的内容（能力层）
在共享技能目录 `~/.openclaw/skills/memory-system-v2/` 中，正式固化：
- `memory-cli.sh` 不再默认只看 `$HOME/clawd/memory`
- 新逻辑：优先解析
  1. `OPENCLAW_WORKSPACE_ROOT`
  2. `OPENCLAW_WORKSPACE`
  3. 当前目录向上查找 `.memory-system-v2.conf / MEMORY.md / AGENTS.md`
- 然后读取 `.memory-system-v2.conf` 中的固定 `MEMORY_DIR`

这意味着：
- 不需要依赖当前 shell 人工临时 export
- 新开窗口、新 shell，只要位于工作区内，或使用固定入口脚本，都会落到既定目录

### 4. pending-memories 模板持久化修正
在 `cognitive-memory` 模板源头中，已移除会被误识别为真实 proposal 的：
- `## Proposal #1`

现改为纯注释示例文本，不再带真实 proposal 标题格式。
同时已清理现有三省六部工作区中的同类噪声。

---

## 三、实际修改项清单
### A. 共享技能目录
- `~/.openclaw/skills/memory-system-v2/memory-cli.sh`
- `~/.openclaw/skills/cognitive-memory/assets/templates/pending-memories.md`

### B. 主源仓
- `/www/wwwroot/edict/scripts/memory_cli.sh`
- `/www/wwwroot/edict/reports/JJC-20260320-001-persistence-hardening.md`

### C. 工作区持久配置
- `/root/.openclaw/workspace-*/.memory-system-v2.conf`
  - 已覆盖：太子、中书、省门下、省尚书、六部、早朝

### D. 工作区固定入口
- `/root/.openclaw/workspace-*/scripts/memory_cli.sh`
  - 由主源 `sync_agent_config.py` 同步到各 workspace
- `/root/.openclaw/workspace-{taizi,zhongshu,menxia,shangshu}/memory/memory-cli.sh`
  - 已改为 shim，统一转发到 `scripts/memory_cli.sh`
  - 作用：消除旧入口继续写回 `$HOME/clawd/memory` 的分叉风险

### E. 工作区模板噪声清理
- `/root/.openclaw/workspace-*/memory/meta/pending-memories.md`
  - 已清理 `Proposal #1` 示例噪声

### F. 六部最小记忆骨架补齐
对此前缺失的六部/早朝工作区，补齐了：
- `memory/meta/pending-memories.md`
- `memory/meta/audit.log`
- `memory/meta/decay-scores.json`
- `memory/graph/index.md`

---

## 四、复测结果
### 复测 1：新 shell + 固定入口脚本（中书省）
测试方式：
- `env -i HOME=/root ... bash -lc 'cd workspace-zhongshu && scripts/memory_cli.sh capture/search ...'`

结果：
- 成功写入 `/root/.openclaw/workspace-zhongshu/clawd/memory/...`
- 无需人工临时 `HOME` 覆盖
- 新 shell 内仍按既定路径生效

### 复测 2：新 shell + 直接调用共享技能脚本（门下省）
测试方式：
- `env -i HOME=/root ... bash -lc 'cd workspace-menxia && ~/.openclaw/skills/memory-system-v2/memory-cli.sh capture/search ...'`

结果：
- 成功写入 `/root/.openclaw/workspace-menxia/clawd/memory/...`
- 说明即使不用 wrapper，只要进入 workspace，shared skill 也能自动解析固定配置

### 复测 3：新 shell + 从子目录调用（户部，模拟扩面六部）
测试方式：
- `env -i HOME=/root ... bash -lc 'cd workspace-hubu/memory/meta && ~/.openclaw/skills/memory-system-v2/memory-cli.sh capture/search ...'`

结果：
- 成功写入 `/root/.openclaw/workspace-hubu/clawd/memory/...`
- 说明即便从子目录、新 shell 启动，也能向上解析 workspace/config 并稳定落到固定目录

### 复测 4：Proposal 模板噪声检查
检查范围：三省 + 六部 + 早朝的 `pending-memories.md`

结果：
- `proposal_noise_files = []`
- 即：`## Proposal #1` 模板噪声已清零

### 复测 5：旧入口兼容性（门下省封驳点修复验证）
测试方式：
- `env -i HOME=/root ... bash -lc 'cd workspace-zhongshu && memory/memory-cli.sh capture/search ...'`
- `env -i HOME=/root ... bash -lc 'cd workspace-menxia && memory/memory-cli.sh capture/search ...'`

结果：
- 旧入口 `memory/memory-cli.sh` 已不再写入 `$HOME/clawd/memory`
- 现统一转发到 `scripts/memory_cli.sh`
- 中书省、门下省均成功写入各自 workspace 的固定目录 `workspace-*/clawd/memory/...`

---

## 五、是否已满足六部扩面条件
### 当前结论：**已满足。**

原因：
1. 先前最后两项硬门槛均已持久化修正
   - `memory-system-v2` 正式存储口径已落地
   - `Proposal #1` 噪声已从模板源头与现有工作区清除
2. 复测证明：
   - 新 shell / 新窗口语境下仍生效
   - 不依赖临时 `HOME` 覆盖
   - 六部工作区也已具备最小记忆骨架与固定入口
3. 因此当前方案已从“临时可用”升级为“可持久复用”

---

## 六、直接回答皇上关切
### 新开会话是否仍保持有效？
**是。**

本轮已经用“新 shell + 清空环境 + 默认 HOME=/root”的方式复测通过；
无论通过：
- `scripts/memory_cli.sh` 固定入口，还是
- 直接调用共享技能 `memory-cli.sh`

只要在对应 workspace 内启动，就会稳定落到该 workspace 的固定 memory 目录，不再依赖人工临时环境变量。

---

## 七、建议
- 现可进入“向六部扩面”的下一步执行，不再需要以“记忆机制不持久”为由延后
- 后续如需统一质量扫描，可在此基础上补一个固定检测脚本，但已不再是扩面前置条件
