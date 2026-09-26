# /evolve — 以目标驱动的自主循环

> 衡量错误之处。修复最严重的问题。再次衡量。**修复措施是否复合成持久的知识护城河是一个被追踪的假设，而非承诺** — 已由 [ADR-0004](../../docs/adr/ADR-0004-corpus-moat-unproven-position-on-the-system.md) 和 [ADR-0011](../../docs/adr/ADR-0011-escape-corpus-compounding-unproven-structural-starvation.md) 降级为未经证实的地位。已证实的产物是每周期验证（**无结论=未完成**），而非复合。不要在尺子之前推销飞轮。
> **实验级别。** 自主长循环；在基座上运行（受监控或调度），永不作为仓库内的守护进程运行（ADR-0009）。

**周期反馈是明确的。** 每个完成的执行单元路由 `Validate -> Learn -> orchestrator`；既不由证明也不由账本控制重试或交付。

**循环作为此技能运行。** `evolve` 选择工作并调用完整的 `/rpi --auto` 周期——这就是循环。一个有实质内容的 Learn 数据包返回给 orchestrator，orchestrator 通过 Discovery 改变剩余计划，并通过 Premortem 仅发送该已更改的计划。`no_change` 允许显式的继续/重试/停止/升级决策；`terminal` 关闭周期。基座将整个循环作为一个单元进行调度；以前的 RPI CLI 包装器已退役（ADR-0009）。

**操作员节奏：** 衡量仓库状态 → 选择下一个最高价值的项目 → Discovery → Premortem → Crank → Validate → Learn → orchestrator 决策 → 重复直到关闭开关、最大周期上限、回归断路器或真实休眠停止。

## 约束

- 每个选定项目运行一个完整的 `rpi --auto` 周期，并在之后重新读取工作阶梯，因为部分阶段和固定待办事项会破坏反馈循环。
- 永远不要让 Validate 或 Learn 推送、关闭工作、变异计划或选择下一个周期；那些是独立的适配器/orchestrator 决策。
- 在升级之前，用一次有界的辅助传递处理断路器触发；只有判断、拒绝、已花费的预算或失败的辅助传递会到达人类，因为普通阻塞器会返回到最早失效的循环步骤。

## 工作选择阶梯

选择是一个从顶部重新读取的阶梯，每次有生产力的周期后都会重新读取——绝不是一次性检查。完整的每级程序（`ao loop next-work` 推荐建议、范围过滤器、生成器代码、`--quality` 级联、休眠硬门）：[references/work-selection-ladder.md](references/work-selection-ladder.md)。

1. **已收获** — `.agents/rpi/next-work.jsonl`，最新未消费的后续工作
2. **开放就绪珠子** — `ao beads exec ready`，最高优先级
3. **失败的目标 + 指令差距** — `ao goals measure`（如果 `--beads-only` 则跳过；跳过隔离的振荡器）
4. **生成器** — 覆盖率/安全性/性能/重构发现 → 珠子或队列项（下方）
5. **复杂性 / TODO / 漂移 / 代码/过时文档/过时研究挖掘**
6. **功能建议** 当没有更尖锐的内容时，基于仓库目的

`--quality` 会反转顶部（发现之前的目标）。节拍门会阻止会重复尾随周期的 `mode`（连续 ≥ 3）。**休眠是最后手段** — 空队列意味着“运行生成器”，而不是“停止”；只有在多个连续传递后队列和生成器层都为空时才休眠。

**工作生成器**（自动调用；使用 `--no-lifecycle` 跳过，它会回退到手动扫描）：
- `Skill(skill="test", args="coverage")` → 覆盖率低于 40% 的文件成为队列项
- `Skill(skill="refactor", args="--sweep all --dry-run")` → CC > 20 的函数成为队列项
- `Skill(skill="security", args="audit")` → CVSS ≥ 7.0 或 2+ 大型依赖项落后
- `Skill(skill="perf", args="profile --quick")` → 热路径性能发现

**实时技能编辑免疫系统：** 如果周期编辑了 `skills/<slug>/SKILL.md`，在交接前运行 `ao skills edit seal --skill <slug> --actor "${AGENT_NAME:-agent}"` — 封签会创建回滚提交并记录 `Skill-Edit` 尾迹，用于每日摘要。`docs/contracts/critical-skills.txt` 中的关键技能会拒绝未经监控的编辑；`--allow-critical` 仅在监督下使用。

## 标志

| 标志 | 默认值 | 描述 |
|------|---------|-------------|
| `--max-cycles=N` | 无限制 | 完成后 `N` 个周期后停止 |
| `--dry-run` | 关闭 | 显示计划的周期操作，但不执行 |
| `--beads-only` | 关闭 | 跳过目标测量并运行仅待办事项选择 |
| `--skip-baseline` | 关闭 | 跳过首次运行的基线快照 |
| `--quality` | 关闭 | 优先考虑收获后的事后发现 |
| `--compile` | 关闭 | 在第 1 个周期之前运行 `ao compile` 知识预热 |
| `--test-first` | 开启 | 严格质量默认值通过到 `rpi` |
| `--no-test-first` | 关闭 | 显式禁用 `rpi` 的测试优先传递 |
| `--no-lifecycle` | 关闭 | 跳过生命周期工作生成器（回退到手动扫描） |
| `--mode=burst\|loop` | burst | 操作员循环；STOP 拒绝 ([references/loop-mode.md](references/loop-mode.md)) |

## 执行步骤

**你必须执行这个工作流——不要只是描述它。** **完全自主：** 每个 `rpi` 使用 `--auto`；不要询问用户任何内容（阅读 `references/autonomous-execution.md` 了解狭窄的操作员形状切割））。每个周期 = 一个完整的 3 阶段 `rpi` 运行。对于广泛的 AgentOps 领域进化（技能、CLI、文档、测试、珠子、知识）首先阅读 [references/domain-evolution-bootstrap.md](references/domain-evolution-bootstrap.md) — BDD/DDD/六边形/TDD/XP 控制表面 + 干净房间技能工厂护栏。

### 步骤 0：设置

**陈旧检出调查护栏（第一个运行）：** `git fetch origin && git status -sb`。如果落后/分支且有一个没有未推送工作的抛弃式编排树，`git reset --hard origin/main`。**永远不要在调查路径上 `git pull --rebase`** — 它在分支的本地 `main` 面前静默无操作，因此合并的文件显示为“丢失”。

```bash
git fetch origin && git status -sb              # 调查护栏 — 此处永不 `git pull --rebase`
mkdir -p .agents/evolve
ao corpus inject --query "autonomous improvement cycle" --limit 5 2>/dev/null || true
# 会话状态（idle_streak + mode_repeat_streak 在 .agents/evolve/session-state.json）由循环内联刷新
```

从磁盘恢复周期状态（在压缩后存活）：`CYCLE`、`IDLE_STREAK`、`GENERATOR_EMPTY_STREAK`、`LAST_SELECTED_SOURCE`、`CLAIMED_WORK_REF` 从 `.agents/evolve/session-state.json`；规范周期账本是 `cycle-history.jsonl`（两者**仅本地** — 嵌套的 `.agents/.gitignore` 拒绝所有路径，因此也要在提交消息中记录持久的里程碑）。**先验失败注入（强制）：** 读取最后 3 个 `cycle-history.jsonl` 条目；对于任何包含 `FAIL|BLOCKED` 的 `gate`，在选择工作之前提取失败关键词并 grep `.agents/learnings/` — 没有这个，循环会每个周期重新推导相同的教训。详情：`references/cycle-history.md`，`references/convergence-mechanics.md`。

**仓库本地合同。** 如果存在 `docs/contracts/repo-execution-profile.md`，在选择工作之前读取其有序的 `startup_reads` 并从中启动；缓存 `validation_commands`、`tracker_commands`、`definition_of_done`。如果存在仓库本地的 `PROGRAM.md`（或 `AUTODEV.md` 别名 — `PROGRAM.md` 优先）合同，`rpi` 会自动加载它 — 缓存其 `mutable_scope`、`validation_commands`、`decision_policy`、`stop_conditions`；优先选择可变范围内的工件，永不围绕不可变文件静默扩大范围。PROGRAM.md 合同是遗留的 autodev 轨道（仅在 `-tags legacy` 下构建）；其规范 + 修复指导位于 [docs/contracts/autodev-program.md](../../docs/contracts/autodev-program.md)，可执行规范 `references/autodev.feature` 和 `references/autodev-cli.feature`。

**断路器（可调）：** 基于时间（60 分钟无生产性工作） · 最大周期/最大尝试上限 · 成本/配额预算 · 振荡。普通的 REFUTED 结果自动重做；触发断路器需要一次有界的全新上下文辅助传递，只有失败的辅助传递或跳过类别（拒绝、显式判断、已花费上限）会到达人类。阈值是可配置的（`EVOLVE_KILL_TTL_DAYS`、`--max-cycles`、最大尝试），不是硬编码的。**振荡隔离：** 从周期历史中预填充（3+ 改进→失败转换的目标）。见 `references/oscillation.md`。

### 步骤 0.2 / 0.5：预热 + 基线

**检查点：** 仅 `--compile`（在 `--dry-run` 上跳过）：在周期 1 之前运行 `ao compile`，根据 `references/knowledge-loop-integration.md`。在第一个符合条件的运行中，根据 `references/fitness-scoring.md` 捕获适应性基线。

### 步骤 1：关闭开关检查（每个周期的顶部）

```bash
CYCLE_START_SHA=$(git rev-parse HEAD)
# 机械预周期门：KILL/STOP/DORMANT/HANDOFF 标记（TTL + 非粘性）、目标回归、先验周期-FAIL。循环必须运行脚本，而不是可跳过的大纲。
if [ -x scripts/evolve/halt-check.sh ]; then
  if ! HALT_OUT=$(bash scripts/evolve/halt-check.sh --json); then
    REASON=$(printf '%s' "$HALT_OUT" | jq -r '.halt_reason // "unknown"')
    if [ "$REASON" = "prior_cycle_fail" ]; then
      export EVOLVE_RESTORATIVE=1   # 不是终端：步骤 1.5 限制范围为 CI-红色减少
    else
      echo "halt: $REASON"; exit 0  # kill/user_halt/目标回归 -> 停止此周期
    fi
  fi
fi
```

**敏捷优先休眠：** `DORMANT` 永远不会在就绪珠子存在时粘性——`halt-check.sh` 在 `ao beads exec ready` / 收获工作存在时自动清除它。KILL/STOP 尊重 `EVOLVE_KILL_TTL_DAYS`（默认 7）；过时的标记会暴露并绕过。

### 步骤 1.5：修复优先分类器

`ao ci recent --limit 1`（类型 BC2 `CIStatusPort`）→ 如果最后一次推送的 CI 是 `failure`，此周期是**修复性仅**：步骤 3 仅取 CI-红色减少的工作（收获的 Bug、门固定珠子、生成器 Bug 输出）——不进行晋升、功能或新形状工作，直到变绿。周期历史中的 `gate=FAIL` 自动触发此行为，用于周期 N+1。**收敛检查：** `ao loop converged --green-streak <n> --unconsumed-high-medium <n> [--fitness-baseline]`（类型 BC3 `ConvergenceCheckPort`）；基于 `.converged` 分支（默认：CI 绿色连续 ≥ 3，HIGH+MEDIUM 下一个工作 ≤ 1，基线捕获）——如果为真，发出拆除，不要重新启用。见 `references/convergence-mechanics.md`。

### 步骤 2：衡量适应性

如果 `--beads-only` 则跳过。运行 `ao goals measure` → `.agents/evolve/fitness-latest.json`。完整测量、基线捕获和周期后回归检测：`references/fitness-scoring.md`。

### 步骤 3：选择工作

运行上述阶梯；阅读 [references/work-selection-ladder.md](references/work-selection-ladder.md) 了解每级代码。**敏捷不变量：** `ao beads exec ready ≥ 1` ⇒ 循环永不写入 DORMANT 并永不退出——到达 DORMANT 的唯一路径是空的后台 + 干燥生成器（3 次传递）；上下文耗尽 → HANDOFF，不是 DORMANT。如果 `--dry-run`：报告将处理的工作，然后进入拆除。

### 步骤 4：执行

主要引擎：`/rpi`（所有 3 个阶段强制）。`/implement` 或 `/crank` 仅当珠子具有可执行范围时。

```
Invoke /rpi "{normalized work title}" --auto --max-cycles=1     # 收获 / 目标 / 缺口 / 测试 / Bug / 漂移 / 功能
Invoke /rpi "Complete {issue_id}: {title}" --auto --max-cycles=1 # 珠子（后备：/implement {issue_id})
Invoke /crank {epic_id}                                         # 带有子项的史诗
```

如果步骤 3 创建了持久工作而不是执行它，重新进入步骤 3，让新的珠子通过正常选择获胜。**机械批量提示：** > 20 统一的每个文件编辑 → 脚本（`awk`/`sed`/`for`），而不是 N 个编辑调用（`references/mechanical-batches.md`）。**起飞前模式检查：** 一个端口/适配器迁移，其消费者比目标端口投影多 > 20% 的字段 → 中止，转换为端口扩展周期（`references/pre-flight-schema-check.md`）。**操作员形状切割：** `AskUserQuestion` 仅当影响 > 50 个文件或模式/合同表面（`references/autonomous-execution.md`）时允许。

### 步骤 4.5：源表面同步（预门）

在门之前同步二进制和生成表面：CLI 变更需要构建/安装；Codex 技能变更需要哈希重新生成；技能清单变更需要一次性重新生成。使用 [门卫生](references/gate-hygiene.md) 和 [新技能着陆](references/new-skill-landing.md)，永不零碎重新生成。

### 步骤 5：回归门

**检查点：** 运行项目测试加上有序仓库配置 / PROGRAM.md `validation_commands` 和接线关闭。应用 `decision_policy`、不可变范围和 `stop_conditions`；重新测量到 `fitness-latest-post.json` 并撤销回归。保持声明的工件 `consumed: false`，直到周期成功，然后重新读取 `.agents/rpi/next-work.jsonl`。详情：[适应性评分](references/fitness-scoring.md)、[门卫生](references/gate-hygiene.md)、[知识集成](references/knowledge-loop-integration.md)。

### 步骤 6：记录周期 + 提交

**有生产力的**（改进 / 回归 / 收获）：将周期记录追加到 `.agents/evolve/cycle-history.jsonl`，提交真实更改。**空闲**（即使生成器后未找到任何内容）：追加一个带有 `result: "unchanged"` 的记录；不 git add，不提交。当周期处理产品或目标支持缺口（目标假设 → 缺口 → Gherkin → 失败证明 → 红/绿 → 重构 → 验证 → ratchet → 目标重塑）时，在周期记录的 `trace` 字段中记录 XP/BDD/TDD 追踪；简单一次性周期记录 `trace.exemption_reason`。追踪完整性是建议性的，不是门。见 `references/cycle-history.md`，`references/quality-mode.md`。

### 步骤 7：可选确定性交付

在不可变的 Validate 证明通过 Learn 和 orchestrator 接受周期后，仅在仓库策略或操作员授权交付时调用仓库选择的确定性 `/push` 适配器。传递确切的源 SHA、目的地和确定性检查结果。推送不能改变结论、关闭跟踪状态或完成生命周期；如果没有交付授权，返回准备好的 SHA 和证据。交付失败返回未更改的证明给 orchestrator。

### 步骤 7 循环 / 停止

在调用者记录交付或准备交接结果后，增加 `CYCLE` 并返回到步骤 1。

**仅当存在真实原因时停止**（所有都需要一个真实的原因——永不只是上下文大小）： (1) **KILL/STOP 标记** — 操作员覆盖； (2) **`--max-cycles` 上限**； (3) **真实停滞** — `ao beads exec ready=0 AND harvested=0 AND failing-goals=0 AND GENERATOR_EMPTY_STREAK ≥ 2 AND IDLE_STREAK ≥ 2` → 写入 DORMANT，它在 `ao beads exec create` 添加就绪珠子时自动清除； (4) **回归断路器在还原后**。**上下文耗尽不是停止** — 写入 `.agents/evolve/HANDOFF`（非粘性），记录 `result: "context-handoff"`，退出回合；下一次触发清除 HANDOFF 在步骤 1 中，并恢复（`references/context-budget.md`）。

**强制检查点——会话 PR 阈值（锁定下一个周期，不是终端）：** 在 `session_pr_count >= 5` 时，调用 `/postmortem --deep` 并等待结论文件。PASS → 继续；WARN → 在下一个周期的 `notes` 中继续带有警告；FAIL / 非收敛 → 写 STOP。代理必须不自我评分或自我写入 STOP — 没有结论的 STOP 是 2026-05-20 的反模式（`references/postmortem-checkpoint.md`）。

### 拆除

提交任何暂存的 `cycle-history.jsonl`，运行 `/postmortem "evolve session: N cycles"`（一个轻量级会话结束回顾——它不替代理事会门限检查），在授权时调用 `/push` 仅未推送的提交，并报告摘要（周期、有生产力/回归/空闲计数、停止原因）。完整程序：`references/knowledge-loop-integration.md`，`references/teardown.md`。永不写入 `.agents/evolve/STOP` 作为检查点结论文件的替代品。

形状为发布的分支必须遵循 [发布拆除合同](references/teardown.md#release-shaped-teardown)：永不从每个周期的 `--fast` 推荐使用 `/release`，将未检查的清单带入交接，并在标记之前要求完整的发布门。

## 输出规范

- **路径：** 将周期摘要输出到 stdout；追加 `.agents/evolve/cycle-history.jsonl`；写入 `.agents/evolve/{fitness-latest.json,session-state.json}` 和控制文件 `{STOP,DORMANT,HANDOFF}`。
- **文件名：** 周期历史是 `cycle-history.jsonl`；当前的适应性和可恢复状态使用上述固定文件名。
- **格式：** stdout 是 Markdown；状态和适应性使用 JSON；周期历史使用遵循 `references/cycle-history.md` 的 JSONL。
- **验证命令：** 运行仓库配置测试和 `ao gate check --fast --scope head`（它包含接线关闭）；如果选择交付，还要求 `bash skills/push/scripts/validate.sh`。
- **下游交接：** 返回周期计数、适应性差异、结果、停止原因、更改路径、不可变的 Validate 结论，以及任何确定性交付结果；下一个周期消费持久状态和未消费的工作。

## 质量清单

- 选定的工作遵循阶梯并保持在声明的可变范围内。
- 有生产力的周期具有确定性验证加上不可变的候选-当前 Validate 结论。
- 回归被撤销，队列项在授权交付成功或调用者释放之前保持未消费，并且断路器处理遵循辅助传递-人类政策。

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 循环立即退出 | 删除 `~/.config/evolve/KILL` 或 `.agents/evolve/STOP` |
| 重复空传递后停滞 | 队列 + 生产者层在多次传递后为空——休眠是后备结果 |
| `ao goals measure` 挂起 | 使用 `--timeout 30 --total-timeout 75`，或 `--beads-only` 跳过 |
| 回归门撤销 | 审查撤销的更改，缩小范围，重新运行；释放声明的工件 |

## 参考

- **循环机制** — [work-selection-ladder.md](references/work-selection-ladder.md)（每级选择）、[fitness-scoring.md](references/fitness-scoring.md)（基线 / 回归 / 还原）、[convergence-mechanics.md](references/convergence-mechanics.md)（修复优先分类器）、[cycle-history.md](references/cycle-history.md)（JSONL，恢复，追踪）、[oscillation.md](references/oscillation.md)、[metronome-gate.md](references/metronome-gate.md)、[scout-mode.md](references/scout-mode.md)、[long-loop-discipline.md](references/long-loop-discipline.md)
- **门限 + 交付准备** — [gate-hygiene.md](references/gate-hygiene.md)（源表面，红色筛选）、[new-skill-landing.md](references/new-skill-landing.md)（六个衍生表面）、[ao-command-landing.md](references/ao-command-landing.md)、[postmortem-checkpoint.md](references/postmortem-checkpoint.md)、[pre-flight-schema-check.md](references/pre-flight-schema-check.md)、[mechanical-batches.md](references/mechanical-batches.md)、[snapshot-pattern-for-long-cycle-gates.md](references/snapshot-pattern-for-long-cycle-gates.md)
- **自主 + 知识** — [autonomous-execution.md](references/autonomous-execution.md)（循环规则 + 操作员形状切割）、[context-budget.md](references/context-budget.md)、[knowledge-loop-integration.md](references/knowledge-loop-integration.md)（声明的/释放，拆除）、[compounding.md](references/compounding.md)（每个 ADR-0004/0011 的假设立场）、[domain-evolution-bootstrap.md](references/domain-evolution-bootstrap.md)、[quality-mode.md](references/quality-mode.md)、[parallel-execution.md](references/parallel-execution.md)、[teardown.md](references/teardown.md)、[artifacts.md](references/artifacts.md)
## 行为合同锚点（由 scripts/validate.sh 验证）

修剪已将过程移至 references/，但这些不变量保持内联——技能自己的验证器会 grep 它们，并且它们是循环的承重行为：

- **连续值，不是布尔值：** 每个适应性指标报告一个连续值相对于阈值（值/阈值），永远不会出现裸的通过/失败。
- **振荡扫描（始终开启，步骤 0）：** 从 `ao compile` 的振荡报告预填充隔离列表，在选择目标之前。
- **接线预起飞（步骤 5）：** `if ao gate check --fast --scope head; then proceed; else fix wiring first; fi` — 永远不要在接线损坏后发送周期（接线关闭已合并到门之后，因为 always.wiring-closure 元门已被退役）。
- **CLI 是必需的，用于适应性测量** — `ao goals measure` 是仪器；散文自我评分不是适应性。
- **收获优先选择顺序：** 收获的 `.agents/rpi/next-work.jsonl` 工作优先于生成候选；在收获干燥之前消耗它们。
- **生成器阶梯（当收获为空时）：** 测试改进 → 验证收紧和 Bug 猎取传递 → 具体的功能建议。
- **队列声明之前消费：** 首先声明它（设置声明的标记），保持 `consumed: false`，直到授权交付成功或调用者最终完成交接；声明和消费之间的崩溃必须留下可重新运行的行。
- **立即队列重读：** 在每个 /rpi 转换后，立即重新读取 `.agents/rpi/next-work.jsonl` — 转换可能已收获新工作。
- **仓库执行配置：** 存在 `docs/contracts/repo-execution-profile.md` (`startup_reads`, `validation_commands`) 时尊重。

- **规范 + 模式** — [evolve.feature](references/evolve.feature)（锁定周期、阶梯、永不自我停止）、[goals-schema.md](references/goals-schema.md)、[loop-mode.md](references/loop-mode.md)、[examples.md](references/examples.md)、[autodev.feature](references/autodev.feature) + [autodev-cli.feature](references/autodev-cli.feature)（遗留的 autodev 轨道，`-tags legacy`）

## 示例

`/evolve` 运行直到真实停止；`/evolve --max-cycles=3` 限制它；`/evolve --dry-run` 报告选择而不进行变异。完整演练：[references/examples.md](references/examples.md).
- `skills/rpi/SKILL.md` — 完整生命周期编排器（每个周期调用）
- `skills/crank/SKILL.md` — 史诗执行（珠子史诗调用）
- `skills/postmortem/SKILL.md` — 学习提取 + 挖掘表面；吸收了退役的 `/curate`, `/compile` 和 `/flywheel` 技能（机械表面是 `ao compile` 和 `ao flywheel status` CLI，不是技能）
- `docs/contracts/autodev-program.md` — 仓库本地 PROGRAM.md 合同（遗留 autodev 轨道）
- `GOALS.yaml` — 此仓库的适应性目标
- [test](../test/SKILL.md) · [refactor](../refactor/SKILL.md) · [security](../security/SKILL.md) · [validate](../validate/SKILL.md) — 工作生成器
