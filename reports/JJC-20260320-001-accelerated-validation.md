# JJC-20260320-001 · 加速补测报告

## 一、补测目标
根据皇上加旨，本轮不等待周度/月度观察期，直接对当前方案做当日加速验证，重点补测：
1. `sessions_send` 定向补问稳定性
2. 三省 `memory capture/search` 实测
3. 重复提案 / 空泛提案检查
4. 跨会话取证边界执行一致性

---

## 二、补测结果

### 1. sessions_send 定向补问稳定性
**结果：通过。**

本轮向门下省、尚书省各发起 1 次定向补问，均在超时窗口内收到结构化回复：
- `agent:menxia:main` → 回复：`ack-menxia-ok / yes / no + 三省真实小闭环未跑通`
- `agent:shangshu:main` → 回复：`ack-shangshu-ok / yes / no + 中书省完成三省汇总验收`

结论：
- `sessions_send` 链路本身稳定，可用于三省之间的定向补问
- 两次回复都能在限制格式内返回，说明最小交互协议可行
- 当前问题不在链路稳定性，而在“业务结论是否已同步到所有省”的状态一致性

### 2. 三省 memory capture/search 实测
**结果：功能通过，但暴露 1 个结构性缺口。**

在三省分别完成一轮 `memory-system-v2` 的 capture + search dry-run：
- zhongshu：capture 成功，search 命中
- menxia：capture 成功，search 命中
- shangshu：capture 成功，search 命中

实测写入路径：
- `/root/.openclaw/workspace-zhongshu/clawd/memory/...`
- `/root/.openclaw/workspace-menxia/clawd/memory/...`
- `/root/.openclaw/workspace-shangshu/clawd/memory/...`

但同时核对到 `memory-cli.sh` 当前默认实现为：
- `MEMORY_DIR="$HOME/clawd/memory"`
- 当前默认 `HOME=/root`

这意味着：
- 若不显式覆盖 `HOME`，当前默认会写到共享路径 `/root/clawd/memory`
- 本轮三省独立实测之所以成立，是因为测试时人为按工作区覆盖了 `HOME`

结论：
- **memory capture/search 本身可用**
- 但**默认落点策略尚未与三省按工作区分治的现行记忆架构完全对齐**
- 这是当前最关键的扩面前缺口之一

### 3. 重复提案 / 空泛提案检查
**结果：真实提案未见空泛或实质重复，但检测会被示例文本误伤。**

检查对象：
- `/root/.openclaw/workspace-zhongshu/memory/meta/pending-memories.md`
- `/root/.openclaw/workspace-menxia/memory/meta/pending-memories.md`
- `/root/.openclaw/workspace-shangshu/memory/meta/pending-memories.md`

检查结果：
- 真实 proposal 共 4 条（另有 3 处示例 `#1`）
- `Content` 长度均大于最小阈值，无空泛空壳提案
- 未发现真实业务提案之间的实质重复

但三省文件都保留了模板示例：
- `## Proposal #1`

这会导致：
- 若后续做自动重复检测，`#1` 示例会被误判成三省重复提案
- 自动质量检查需要显式排除示例段，或直接移除示例

结论：
- 当前**真实提案质量可接受**
- 但**示例残留会干扰自动化检查**，这是第二个扩面前应当天修正的缺口

### 4. 跨会话取证边界执行一致性
**结果：通过。**

本轮使用最小范围读取方式复核：
- 对 `agent:menxia:main` 仅取最近 1 条
- 对 `agent:shangshu:main` 仅取最近 1 条

结果：
- `sessions_history(limit=1)` 能稳定返回单条目标消息
- 能够满足模板中 `Minimum Scope + SessionKey + Timestamp` 的边界要求
- 尚书省上一轮回奏中也已按模板给出一次完整取证记录

结论：
- 当前跨会话取证边界模板在三省内**可执行且一致**
- 该项不再构成立即扩面前的主阻塞

---

## 三、综合判断
### 能否立即推广到六部？
**当前结论：仍不建议立即推广六部。**

但原因已不再是“还要等一周/一月观察”，而是**只剩 2 个当天可继续收敛的具体缺口**：

#### 缺口 1：memory-system-v2 默认落点未与三省工作区架构对齐
- 当前默认写入依赖 `HOME=/root`，即 `/root/clawd/memory`
- 三省独立验证成立，依赖的是测试时显式覆盖 `HOME`
- 若立即扩到六部而不先定口径，可能出现：
  - 所有 Agent 共写同一 memory 目录
  - 与 `workspace-*/memory/*` 的现行骨架并行分叉
  - 后续收敛/审计边界混乱

#### 缺口 2：pending-memories 文件中的 `## Proposal #1` 示例会误伤自动检测
- 真实提案没问题
- 但示例文本若不清理或不在检测时排除，将导致重复提案/质量扫描失真
- 六部一扩面，误报会放大

---

## 四、最短剩余验证/修正清单（可当天完成）
### 最短只差 2 项
1. **明确并落地 memory-system-v2 的正式存储口径**
   - 二选一：
     - A. 明确按 Agent/workspace 分目录存储，并给脚本或 wrapper 固化
     - B. 明确允许共享 `/root/clawd/memory`，并同步修正文档与收敛逻辑
   - 完成后再做一次三省 capture/search 复测即可

2. **移除或排除 `pending-memories` 中的示例 `## Proposal #1`**
   - 方式：删示例，或在检测脚本中忽略 example block
   - 完成后再跑一次重复/空泛提案扫描即可

若上述两项在当日完成并复测通过，则可进入“是否向六部推广”的再判定，不必再等待一周或一个月。

---

## 五、当前建议
### 建议结论
- **可立即继续加速整改**
- **暂不立即推广六部**
- **最短还差 2 项，当日可补齐并复测**

### 推荐顺序
1. 先定 `memory-system-v2` 存储口径
2. 再清理/排除 `pending-memories` 示例噪声
3. 立即复测
4. 复测通过后，再向皇上请示是否扩至六部
