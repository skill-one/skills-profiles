从**飞行记录器**中诊断 harness 的异常行为——vigiles 在 harness 运行时写入的本地、仅追加的账本 `.vigiles/runs.jsonl`。它记录了实际发生的情况，因此你可以基于证据进行调试，而不是猜测。

## 账本中包含的内容

每行一个 JSON 记录，每个记录都有一个 `kind`：

- `hook` — 编译钩门的决策：`{event, decision: allow|deny|ask, mode: enforce|observe, rule, cmd, reason}`。
- `agent` — 子代理工具合约的决策：`{name, tool, allowed, reason}`（`false` = 代理越界了）。
- `skill` — 技能激活：`{name, fired}`。
- `eval` — 测量的指标：`{name, metric, value}`（例如触发率召回/精确率）。
- `capability-diff` — 爆炸半径的变化：`{pr, added, removed, widened}`。

## 指令

### 第一步：读取账本

读取 `.vigiles/runs.jsonl`（JSONL — 每行一个记录；容忍最后一行破损）。如果它不存在或为空，请说明——目前还没有记录；建议先运行 harness（或 `vigiles audit`）。不要编造记录。

### 第二步：基于证据回答具体问题

将用户的问题与账本匹配：

- **"为什么技能 X 停止触发 / 为什么运行了错误的技能？"** — 按名称随时间统计 `skill` 触发次数。如果 X 的触发率下降，寻找在同一类型提示上触发的兄弟技能（**选择冲突**），并检查它们的描述是否有重叠。建议区分或合并描述。
- **"为什么我的钩门没有阻止？"** — 查找该事件的 `hook` 记录。在应该被拒绝的事情上出现 `decision: allow`，或者 `mode: observe`（影子，从不阻止），或者没有任何记录，都会告诉你原因。建议将 `observe`→`enforce` 或修复门逻辑。
- **"子代理是否行为不当？"** — 列出 `agent` 记录中 `allowed: false`：代理试图使用其声明的合约之外的工具。指向合约以收紧或放宽。
- **"情况是否在恶化？"** — 比较不同运行中的 `eval` 指标值（召回/精确率）；下降趋势是漂移（通常在 harness/模型升级后）。

### 第三步：基于证据推荐修复方案

优先**将忽略但可决策的规则从文本提升为确定性门**：重复的 `agent` 违规或代理不断破坏的规则 → 编译钩门或更紧密的工具合约（`strengthen` 技能可以帮助）。描述冲突 → 区分技能描述。始终引用你基于诊断的具体记录。

### 第四步：提供下一步操作

如果修复是规范变更，转交给 `edit-spec`。如果是将指导提升为 linter 规则，转交给 `strengthen`。如果行为声明需要测量（技能现在是否触发？），转交给 `test-harness` (`measureTriggerRate`)。
