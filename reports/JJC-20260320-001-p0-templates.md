# JJC-20260320-001 · 三省记忆协同 P0 模板（执行稿）

## 适用范围
适用于中书省、门下省、尚书省在三省真实小闭环试点中的统一回奏、记忆提案、跨会话取证。

---

## 模板一：三省统一回奏模板
> 必填字段：任务ID、结果、证据路径、阻塞项、建议记忆项

```markdown
已接旨

任务ID：JJC-XXXXXX

结果：
- [本省本轮完成了什么]
- [是否准奏/执行完成/需补件]
- [本轮结论]

证据路径：
- [文件/日志/报告路径 1]
- [文件/日志/报告路径 2]

阻塞项：
- [无 / 具体阻塞 1]
- [待主责确认事项]

建议记忆项：
- store: [memory-system-v2 / cognitive-memory / pending-memories]
- content: [建议沉淀的事实/决策/风险]
- confidence: [high/medium/low]
```

### 使用规则
1. `结果` 先写结论，再写动作
2. `证据路径` 必须可落到文件、日志或会话证据
3. `阻塞项` 没有就写“无”
4. `建议记忆项` 至少 1 条，禁止省略

---

## 模板二：记忆提案模板
> 用于写入 `memory/meta/pending-memories.md`

```markdown
## Proposal <TASK-ID>-<AGENT>-<YYYYMMDDHHMM>
- **From**: [中书省 / 门下省 / 尚书省]
- **Timestamp**: [ISO-8601 时间]
- **Suggested store**: [memory-system-v2 / cognitive-memory / pending-memories]
- **Content**: [建议沉淀的事实、决策、风险、职责边界、阻塞经验]
- **Confidence**: [high / medium / low]
- **Status**: pending
- **Consolidation Owner**: [默认：中书省周度收敛，太子月度抽检]
- **Evidence**:
  - [证据路径 1]
  - [证据路径 2]
```

### store 选择规则
- `memory-system-v2`：当日事件、简短决策、interaction、快速 recall
- `cognitive-memory`：长期结构化规则、协作机制、反复复用的流程约束
- `pending-memories`：待主责确认、待收敛的跨省提案

---

## 模板三：跨会话取证模板
> 用于使用 `sessions_list / sessions_history / sessions_send` 后，在回奏中固化取证边界

```markdown
### 跨会话取证记录
- **Purpose**: [为什么要取证]
- **Minimum Scope**: [最小必要范围，例如“仅查门下省最近 1 条审议结果”]
- **Maximum Range**: [最大消息范围/条数，例如“最多最近 3 条消息”]
- **SessionKey**: [实际引用的 sessionKey]
- **Timestamp**: [引用消息时间点]
- **Quoted Summary**: [引用摘要，不贴整段无关历史]
- **Follow-up**: [是否需要 sessions_send 定向补问]
```

### 使用规则
1. 严禁无边界扫全量历史
2. 必须写 `SessionKey + Timestamp`
3. `Quoted Summary` 只保留与当前任务直接相关内容
4. 若补问，优先使用 `sessions_send`，并在回奏中记录是否收到回复

---

## 三省真实小闭环试点步骤（本轮）
1. **中书省**：用模板一提交试点方案与模板定稿稿
2. **门下省**：按模板一回“准奏/封驳”，并写 1 条记忆提案
3. **尚书省**：按模板一回“执行完成/阻塞”，并写 1 条记忆提案
4. **中书省**：汇总三省结果，补 1 条记忆提案，形成试点结论
5. **太子**：按批准口径月度抽检；本轮仅看三省闭环是否成立，不扩六部

---

## 本轮试点验收标准
1. 三省回奏均包含：`任务ID / 结果 / 证据路径 / 阻塞项 / 建议记忆项`
2. 三省至少各形成 1 条 `pending-memories` 提案
3. 至少 1 次跨会话取证记录按模板完整落地
4. 中书省能汇总形成“是否适合推广六部”的明确结论
5. 任一省漏填强制字段、未落 1 条提案、或跨会话取证缺 `SessionKey + Timestamp`，即不得算闭环完成

---

## 推广建议判定口径
### 可以建议推广到六部
- 三省模板执行成本低
- 取证口径清楚
- 记忆提案不重复、不空泛
- 没有明显新增流程阻塞

### 暂不建议推广到六部
- 三省回奏仍漏字段
- pending-memories 积压无收敛
- 跨会话取证仍无边界
- 双记忆系统职责混淆
