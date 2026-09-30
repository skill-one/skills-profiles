---
name: debug-my-harness
description: 通过读取本地飞行记录账本（.vigiles/runs.jsonl）来诊断代理套件为何行为异常——哪些技能被触发或被劫持，哪些钩子被阻止或错误允许，哪些子代理工具合约违规发生，以及某个技能的触发率如何变化。当被问及为何技能停止触发、钩子未阻止、错误技能运行时，或用于调试/调查套件实际执行情况时使用。不用于编写新规则（使用strengthen）或编辑规范（使用edit-spec）。
---

从**飞行记录器**中诊断 harness 的异常行为——vigiles 在 harness 运行时写入的本地、仅追加的账本 `.vigiles/runs.jsonl`。它记录了实际发生的情况，因此你可以基于证据进行调试，而不是猜测。

## 账本中包含的内容

每行一个 JSON 记录，每个记录都有一个 `kind`：

- `hook` — 编译钩子门的决策：`{event, decision: allow|deny|ask, mode: enforce|observe, rule, cmd, reason}`。
- `agent` — 子代理工具合同决策：`{name, tool, allowed, reason}`（`false` = 代理越界了）。
- `skill` — 技能激活：`{name, fired}`。
- `eval` — 测量的指标：`{name, metric, value}`（例如触发率召回/精确率）。
- `capability-diff` — 爆炸半径变化：`{pr, added, removed, widened}`。

## 指令

### 第一步：读取账本

读取 `.vigiles/runs.jsonl`（JSONL — 每行一个记录；容忍最后一行撕裂）。如果它不存在或为空，请说明——目前还没有记录；建议先运行 harness（或 `vigiles audit`）。不要编造记录。

### 第二步：基于证据回答具体问题

将用户的问题与账本匹配：

- **"为什么技能 X 停止触发 / 为什么运行了错误的技能？"** — 按名称随时间统计 `skill` 触发次数。如果 X 的触发率下降，寻找在同一类型提示上触发的兄弟技能（**选择冲突**），并检查它们的描述是否有重叠。建议区分或合并描述。
- **"为什么我的钩子没有阻止？"** — 查找该事件的 `hook` 记录。在应该被拒绝的事情上出现 `decision: allow`，或者 `mode: observe`（阴影，从不阻止），或者没有任何记录，都会告诉你原因。建议将 `observe`→`enforce` 或修复门逻辑。
- **"子代理是否行为不当？"** — 列出 `agent` 记录中 `allowed: false`：代理试图使用其声明的合同之外的工具。指向合同以收紧或放宽。
- **"情况是否在恶化？"** — 比较不同运行中的 `eval` 指标值（召回/精确率）；下降趋势是漂移（通常在 harness/模型升级后）。

### 第三步：基于证据推荐修复方案

优先**将忽略但可决策的规则从文本提升为确定性门**：重复的 `agent` 违规或代理不断破坏的规则 → 编译钩子或更紧的工具合同（`strengthen` 技能可以帮助）。描述冲突 → 区分技能描述。始终引用你基于诊断的具体记录。

### 第四步：提供下一步操作

如果修复方案是规范变更，则转交给 `edit-spec`。如果是将指导提升为 linter 规则，则转交给 `strengthen`。如果行为声明需要测量（技能现在是否触发？），则转交给 `test-harness`（`measureTriggerRate`）。
