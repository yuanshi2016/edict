# JJC-20260320-001 · 三省六部 Agent-to-Agent 通信与记忆协同增强方案

## 一、任务目标
基于 `cft0808/edict` 当前已落地能力，在**不直接大改生产链路、先验证再扩展**的前提下，增强三省六部体系的：
1. Agent-to-Agent 通信稳定性
2. 跨会话信息可见性
3. 记忆沉淀与协同提案机制
4. 中书省、门下省、尚书省之间的稳定协作口径

---

## 二、当前已生效项清单（已复核）
### 1. 配置能力
- `tools.sessions.visibility = all`
- `tools.agentToAgent.enabled = true`
- `tools.agentToAgent.allow = [main, taizi, zhongshu, menxia, shangshu, hubu, libu, bingbu, xingbu, gongbu, libu_hr, zaochao]`

### 2. 共享技能目录
- `~/.openclaw/skills/memory-system-v2`
- `~/.openclaw/skills/cognitive-memory`

### 3. 核心工作区记忆骨架
已在以下工作区初始化：
- `workspace-taizi`
- `workspace-zhongshu`
- `workspace-menxia`
- `workspace-shangshu`

且四者均存在：
- `memory/meta/pending-memories.md`
- `memory/meta/audit.log`
- `memory/graph/index.md`
- `memory/meta/decay-scores.json`

### 4. AGENTS 协同口径
四个核心工作区 `AGENTS.md` 已加入“记忆协同补充协议”，核心要求包括：
- 涉及既往决策/偏好/阻塞先查 `MEMORY.md` 与 `memory/*.md`
- 协作回奏时同步写入 `memory/meta/pending-memories.md`
- 子执行方只提记忆提案，不直接改写他部核心记忆

### 5. 跨会话可见性已实测
已能从中书省直接看到：
- 太子当前会话
- 门下省既往审议会话
- 尚书省主会话

说明 `sessions_list / sessions_history` 已具备跨 Agent 可见能力，不再局限于单 Agent 树内。

---

## 三、设计原则
### 原则 1：控制面与记忆面分离
- **控制面**：任务流转、派发、状态推进，以 `kanban_update.py + agent_dispatch.py` 为准
- **记忆面**：经验、阻塞、决策、偏好、验收口径，以 `MEMORY.md + memory/* + pending-memories.md` 为准

### 原则 2：共享读，门控写
遵循 `cognitive-memory` 的多 Agent 口径：
- 各 Agent 可读共享记忆与相关会话
- 非主责 Agent 不直接改写他部核心记忆
- 子执行方只写**提案**到 `pending-memories.md`
- 主责方或太子负责核准与沉淀

### 原则 3：快记忆与深记忆分层
- **memory-system-v2**：用于快速记录“事件 / 决策 / insight / interaction”，适合日常检索与快速召回
- **cognitive-memory**：用于长期结构化记忆、图谱、衰减、审计、反思与跨 Agent 协同框架

### 原则 4：先补协作口径，再做链路增强
优先补齐三省固定协作协议、回奏模板、记忆提案模板；只有在协议跑通后，再考虑更深层自动化增强。

---

## 四、三省稳定协作口径（建议定稿）
## 4.1 中书省
职责：
- 接旨、拆解、起草方案
- 审核当前已生效项与待验证项
- 向门下省提交审议稿
- 准奏后向尚书省派发执行清单

通信口径：
- 任务派发：`agent_dispatch.py`
- 状态推进：`kanban_update.py`
- 查询其他省实时上下文：`sessions_list / sessions_history`
- 必要定向补问：`sessions_send`

记忆口径：
- 把“方案结论 / 已确认事实 / 未决争议 / 实施顺序”写入 `memory/meta/pending-memories.md`
- 不直接写门下/尚书核心记忆

## 4.2 门下省
职责：
- 审议方案是否闭环、是否越权、是否缺验证
- 明确封驳点或准奏条件

通信口径：
- 以“准奏 / 封驳 + 条件”形式反馈中书省
- 可通过 `sessions_history` 读取中书/太子上文，不再只依赖太子转述

记忆口径：
- 把“审议意见 / 风险点 / 附加约束”写入本部 `pending-memories.md`
- 只提案，不越权代写中书省结论

## 4.3 尚书省
职责：
- 接收准奏方案并形成执行清单
- 视需要再派六部
- 回收执行证据与阻塞项

通信口径：
- 以“执行清单 / 已完成项 / 阻塞项 / 下一节点”格式回中书省
- 对主验收仓与共享 DATA 这类基础设施能力，先查 manifest / preflight / shared context，再回奏

记忆口径：
- 把“执行经验 / 重复阻塞 / 下游职责边界 / 证据路径”写入本部 `pending-memories.md`
- 避免让关键信息只留在太子会话内

---

## 五、建议增强清单（先验证、后扩展）
## P0：先做协作协议增强（低风险、立即可执行）
1. 统一三省回奏模板
   - 固定字段：任务ID / 结果 / 证据路径 / 阻塞项 / 建议记忆项
2. 统一记忆提案模板
   - 固定字段：来源 / 时间 / 建议 store / 内容 / 置信度 / 状态
3. 统一跨会话取证口径
   - 中书/门下/尚书在回奏前，允许使用 `sessions_list / sessions_history` 补齐实时上下文
4. 统一 memory-cli 最小使用法
   - 用于快速 capture/search 当日 learnings、decisions、events、interactions

## P1：再做轻量自动化增强（中低风险）
1. 给三省补一个 `memory_capture.sh` 或等效轻脚本
   - 把回奏中的建议记忆项自动转成 memory-system-v2 capture 命令
2. 给中书省补一个“审议前检查清单”
   - 是否已查 sessions
   - 是否已查 pending-memories
   - 是否已写建议记忆项
3. 给尚书省补一个“执行后回收清单”
   - 是否形成证据路径
   - 是否写阻塞
   - 是否提交记忆提案

## P2：最后做更深层自动化（需验证后再动）
1. 研究是否引入跨省共享 memory 索引或汇总器
2. 研究是否让太子定期审核并合并三省 pending-memories
3. 研究是否给门下/尚书增加更细粒度 A2A allowlist，而不是全开放使用

---

## 六、当前剩余待验证项
1. `sessions_send` 在三省之间的定向补问链路是否稳定
2. `memory-system-v2` 的 capture/search 是否已在 menxia/shangshu 工作区完成首轮实测
3. `cognitive-memory` 的“共享读、门控写”口径是否被三省长期遵守
4. 太子是否需要一个定期“记忆提案收敛”流程，避免 pending-memories 长期堆积
5. 是否需要给六部也补最小版记忆协同协议（建议先不扩，待三省跑稳后再推广）

## 六点五、门下省审议后补充的流程风险
1. `sessions_list/history` 共享读范围偏宽，需补“最小必要取证”边界，避免跨 Agent 过度取数
2. `pending-memories.md` 若无人定期收敛，会堆积失真，需明确收敛责任人与节奏
3. 跨会话取证必须在回奏中标注 `sessionKey + 时间点`，否则不同 Agent 引用不同上下文会漂移
4. `memory-system-v2` 与 `cognitive-memory` 的职责边界必须写入模板，否则容易重复记录、双份维护

---

## 七、建议下一步实施顺序
### 第一步（本轮即可）
- 中书省、门下省、尚书省先确认并固化协作口径
- 形成统一模板，不动生产主链路

### 第二步（小范围验证）
- 用一个真实任务跑通：
  - 中书起草
  - 门下审议
  - 尚书执行清单
  - 三省各写一条 `pending-memories.md` 提案
  - 中书或太子回收校验

### 第三步（验证后增强）
- 如果三省协作提质明显，再考虑把 memory-system-v2 capture/search 封装成更顺手的脚本
- 再考虑是否向六部推广最小协同协议

---

## 八、结论
当前底座已经具备：
- 跨 Agent 会话可见
- Agent-to-Agent 已启用
- 共享记忆技能已安装
- 三省核心记忆骨架已初始化

本轮最该做的不是再改底层开关，而是：
**把三省固定协作口径、记忆提案口径、跨会话取证口径跑顺。**

这样才能真正减少“信息只滞留在太子一处”的问题，并在不扰动生产链路的前提下，先拿到可验证的通信增强收益。
