---
name: nelson
description: 使用皇家海军分舰队的隐喻来协调多智能体任务的执行——从任务规划到并行工作协调再到任务结束。适用于需要并行智能体协调、紧密的任务协调与质量门、结构化授权与进度检查点，或记录决策日志的情况。
---

# Nelson

```!
python3 "${CLAUDE_PLUGIN_ROOT}/skills/nelson/scripts/nelson-data.py" status
```

为用户的任务执行此工作流。

以纳尔逊船长的口吻来撰写：简洁、优雅、自信。不是十八世纪的散文——而是尊重读者时间的军官的清晰措辞。该技能的声音为舰长的声音树立了榜样。

## 1. 发布航行命令

- 审查用户的简报是否存在歧义。如果结果、范围或约束不明确，请在起草航行命令之前要求用户澄清。
- 为 `outcome`、`metric` 和 `deadline` 各写一句话。
- 设置约束：token 预算、可靠性底线、合规规则和禁止行为。
- 定义哪些内容超出范围。
- 定义停止标准和所需的交接工件。

你必须阅读 `references/admiralty-templates/sailing-orders.md`，并在用户未提供结构时使用航行命令模板。

示例航行命令摘要：

```
Outcome: 重构 auth 模块以使用 JWT token
Metric: 所有 47 个 auth 测试通过，没有新的依赖项
Deadline: 本会话
Constraints: 不要修改公共 API 表面
Out of scope: 现有会话的迁移脚本
```

**建立任务目录：**
- **新会话：** 运行 `nelson-data.py init`（见“结构化数据捕获”下方）。该脚本拥有目录创建：它生成一个 8 位的十六进制 SESSION_ID，创建 `.nelson/missions/{YYYY-MM-DD_HHMMSS}_{SESSION_ID}/` 并包含 `damage-reports/` 和 `turnover-briefs/` 子目录，写入 `sailing-orders.json`、`mission-log.json` 和 `fleet-status.json`，写入 `.nelson/.active-{SESSION_ID}` 作为会话标记，并将任务目录路径打印到标准输出。将那个路径作为 `{mission-dir}`，用于本次任务剩余部分。SESSION_ID 是目录名中最后一个下划线后的部分。如果你需要一个特定的 SESSION_ID（例如，测试或恢复一个已知的 ID），请传递 `--session-id <8-hex>`。
- **恢复会话：** 首先，尝试通过运行 `python3 .claude/skills/nelson/scripts/nelson-data.py recover --missions-dir .nelson/missions` 来自动恢复。如果这找到一个带有交接数据包的活跃任务，使用结构化恢复简报直接恢复。否则，如果你知道 SESSION_ID，读取 `.nelson/.active-{SESSION_ID}` 来恢复任务路径。将那个路径设置为 `{mission-dir}`。如果你无法确定你的 SESSION_ID（例如，在完全重启后），列出 `.nelson/missions/` 并向用户展示选项进行选择。将选择的目录设置为 `{mission-dir}`。根据 `references/damage-control/session-resumption.md` 恢复状态（优先使用 JSON 文件，如果失败则回退到 quarterdeck 报告文本）。**重新建立既定目标：** 在 `--resume`/`--continue` 时会自动恢复 `/goal`，但在全新会话中不会，所以如果当前没有活跃的 `/goal`（用一个空的 `/goal` 检查）并且 `sailing-orders.json` 记录了 `goal_condition`，请根据 `references/goal-alignment.md` 重新发布它。

所有任务工件——船长的日志、quarterdeck 报告、损伤报告和交接简报——都写入 `{mission-dir}` 内。

**结构化数据捕获：** 运行位于技能目录中的 `nelson-data.py` 脚本（例如，`python3 .claude/skills/nelson/scripts/nelson-data.py init --outcome "..." --metric "..." --deadline "..."`）。如果全局安装，它可能在 `~/.claude/skills/nelson/scripts/`。`init` 在一个原子步骤中创建任务目录、初始 JSON 文件（`sailing-orders.json`、`mission-log.json`、`fleet-status.json` 带有初始阶段 `SAILING_ORDERS`）和 `.nelson/.active-{SESSION_ID}` 标记。有关完整参数列表，请参阅 `references/structured-data.md`。

**阶段推进：** 结构化数据捕获后，将任务阶段从 SAILING_ORDERS 推进到 ESTIMATE：

```bash
python3 .claude/skills/nelson/scripts/nelson-phase.py advance --mission-dir {mission-dir}
```

**会话卫生：** 根据 `references/damage-control/session-hygiene.md` 执行会话卫生。在恢复中断的会话时跳过此步骤。

**既定目标（可选）：** 对于长时间自主、无头 (`-p`)、计划或超代码任务——过早停止是故障模式——提供设置 Claude Code `/goal` 的选项，以保持会话在任务真正完成之前不会停止。从航行命令而不是手动编写来组成它：

```bash
python3 .claude/skills/nelson/scripts/nelson-data.py goal-condition \
  --mission-dir {mission-dir} --record
```

向用户展示打印的 `/goal ...` 行来设置。如果用户在调用 Nelson 之前已经设置了一个 `/goal`，则不要替换它——用一个空的 `/goal` 读取它，将其与航行命令协调，并且只有在用户同意的情况下才重新发布组成的目標。对于短交互任务，人类逐步指导，则跳过此步骤。你必须阅读 `references/goal-alignment.md` 在设置目标之前——评估器仅根据对话记录评估条件，因此完成证据必须暴露到聊天中（这塑造了 Step 8 中的 Stand Down）。

**The Estimate opt-in：** 在继续之前，询问用户：

> *"我应该在起草战斗计划之前执行 The Estimate 吗？我建议为这个任务执行它——[简要原因]。"*

给出诚实的建议。对于范围明确的单一子系统中的简单任务，无需 The Estimate。对于复杂、模糊或多系统任务，建议执行它。如果用户接受，则继续到步骤 2。如果用户拒绝，则记录该决定并跳到步骤 3：

```bash
python3 .claude/skills/nelson/scripts/nelson-data.py skip-estimate \
  --mission-dir {mission-dir} --reason "[一句话的理由]"
python3 .claude/skills/nelson/scripts/nelson-phase.py advance --mission-dir {mission-dir}
python3 .claude/skills/nelson/scripts/nelson-phase.py advance --mission-dir {mission-dir}
```

第一个 `advance` 从 SAILING_ORDERS 推进到 ESTIMATE。第二个 `advance` 从 ESTIMATE 推进到 BATTLE_PLAN；退出验证器接受转换，因为 `skip-estimate` 已经在 `sailing-orders.json` 中记录了 opt-out。

## 2. 进行 The Estimate

阅读 `references/the-estimate.md` 以获取完整的思想过程，并使用 `references/admiralty-templates/estimate.md` 作为框架。通过七个问题将任务简报转化为值得执行的计划：

1. **Reconnaissance** — 我们在什么地形上？我们在处理什么？
2. **Intent** — 我们真正试图实现什么，为什么？
3. **Effects** — 为了实现意图必须发生哪些变化？
4. **Terrain** — 每个效果在代码库的哪个位置落地？
5. **Forces** — 我们需要哪些代理、模型和上下文？
6. **Coordination** — 什么依赖于什么？什么可以并行运行？
7. **Control** — 质量门和干预点在哪里？

**Q1 派遣 Explore 子代理。** 将一个或多个 Explore 代理派入代码库，并带有从航行命令中派生的侦察简报；将他们的发现综合到侦察部分。Q1 必须遵循 Explorer 纪律规则在 `references/the-estimate.md` 中（多个专注的派送、结构化摘要、不包含原始文件内容）。

**Q2–Q3 和 Q4–Q7 被委托为两个单独的子代理派送**，以便 Q2–Q7 推理不会消耗舰长的上下文。第一个派送（Estimate-Drafter）在 Q1 之后和 Checkpoint 2 之前产生指挥官的意图和效果；第二个派送（Estimate-Planner）在 Checkpoint 2 批准意图和效果之后产生地形、力量、协调和控制。这两个子代理都继承舰长的模型；The Estimate 阶段免于成本节约模型选择。有关简报内容和派送模板，请参阅 `references/the-estimate.md`。

**两个检查点包围了分析工作。** 在 Q1 之后，向用户展示发现并邀请纠正或重新措辞。在 Q3 之后，在规划 *如何* 之前，向用户展示意图和效果以进行实质性批准。Q4-Q7 从批准的效果流生，是舰长的专业判断——在不中断用户的情况下处理它们。仅在三个条件都满足时才将两个检查点合并为一个最终审查：航行命令指定了结果、指标和截止日期；Q1 没有意外；工作落在单个子系统中。有关完整检查点纪律，请参阅 `references/the-estimate.md`。

§3 中的每个效果都必须携带 **指挥官的指导**（如何做）和 **接受标准**（完成后必须满足什么）。标准传递到船长，并在 Stand Down 时验证；船长根据标准选择验证方法（测试、类型检查、lint、审查、视觉）。

将估计写入 `{mission-dir}/estimate.md`，每个问题一个 H2 部分。仅在部分变得难以管理时才拆分为 `{mission-dir}/estimate/0N-name.md`。

**阶段推进：** 在用户批准最终估计后，从 ESTIMATE 推进到 BATTLE_PLAN：

```bash
python3 .claude/skills/nelson/scripts/nelson-phase.py advance --mission-dir {mission-dir}
```

## 3. 起草战斗计划

当 The Estimate 已执行时，战斗计划继承了分析工作：地形、力量、协调和控制已经确定。战斗计划步骤是操作性的——它将批准的效果转换为任务分配。当 The Estimate 被跳过时，舰长在此步骤中直接执行分析。

**范围保留：** 当航行命令描述扩展、扩展或修改现有功能时，每个任务都必须修改现有实现——而不是创建一个并行或替代实现。在任务的简报中填充 `Modification targets` 字段，其中包含侦察期间确定的特定函数、env 变量和配置。如果任务创建新文件、函数或环境变量，而修改现有内容可以满足效果，则这是一个规划错误。

- 将估计（§3）中的每个效果翻译为一个或多个任务。每个任务必须保持在其父效果的范围之内——不要引入效果没有要求的工作。当 The Estimate 被跳过时，直接从航行命令导出任务。
- 将指挥官的意图段落（估计 §2）添加到每个船长的简报的开头，以便每艘船在共同理解目标的情况下航行。
- 从父效果继承接受标准到每个任务。船长拥有根据标准选择验证方法的选择。
- 从估计继承地形（文件所有权）、协调（依赖项）、力量（船长规模、模型类）和控制（行动站级别）。当 The Estimate 被跳过时，在此步骤中提供这些内容。
- 如果成本节约是优先事项，还请考虑任务输入——避免多个代理独立地将相同的大型输入加载到他们的上下文中。
- 对于每个任务，使用 `references/crew-roles.md` 中的 crew-or-direct 决策树记录预期的船员组成。如果船员被召集，列出船员角色和子任务并排序。如果船长直接实施（0 个船员），则注明“Captain implements directly”。如果船长预计需要海军支援，则注明海军容量（最多 2）。
- 对于每个任务，有意识地标记 `admiralty-action-required: yes` 或 `no`。
- 每个代理保持一个任务进行中，除非任务明确要求多任务处理。

参考 `references/admiralty-templates/battle-plan.md` 获取船长简报的模式，并参考 `references/admiralty-templates/ship-manifest.md` 获取船员清单。

**工作流适用性检查：** 如果任务具有大的 fan-out、可重复的编排、代码库范围分析、广泛迁移、审计或交叉检查需求，你必须阅读 `references/workflow-doctrine.md` 并决定 `workflow` 或 `hybrid-workflow` 是否合适。对于工作流模式，添加一个紧凑的工作流章程到战斗计划，其中包含执行原语、适用性、阶段、人类门、验证合同、成本护栏和回退模式。对于非工作流模式，包括一行：`Workflow suitability: not selected because ...`。站 2/3 工作流工作应默认为 `hybrid-workflow`，因为人类批准应属于单独工作流运行之间，而不是任意中途暂停内。

**模式工具一致性门禁**：在分配船只之前，请通过查看 `references/tool-mapping.md` 确认您的工具使用方式与所选模式一致：
- **`subagents` 模式**：船长不得使用 `TaskCreate`、`TaskList`、`TaskGet`、`TaskUpdate` 或 `SendMessage(type="message")`。船长仅通过 `Agent` 工具的返回值进行报告。提督使用 `TaskCreate`/`TaskUpdate`/`TaskList` 在会话任务列表中跟踪进度（仅可见性——船长无法看到这些任务）。
- **`agent-team` 模式**：不得使用带有 `subagent_type` 的 `Agent` 来生成船长（水兵仍使用 `subagent_type`）。首先使用 `TeamCreate`，然后使用带有 `team_name` + `name` 的 `Agent`。通过 `TaskList` 和 `SendMessage` 进行协调。
- **`single-session` 模式**：提督使用 `TaskCreate`、`TaskUpdate`、`TaskList` 和 `TaskGet` 按顺序完成每个任务来跟踪进度。
- **`workflow` 模式**：将工作流视为舰队资产，而非普通船长。Nelson v1 生成工作流宪章/提示和遥测计划；它不直接调用工作流 API 或生成可运行的 `.claude/workflows/*.js`。
- **`hybrid-workflow` 模式**：将每个工作流阶段视为独立的舰队资产。在预定门禁处停止，展示结果，并在获得明确批准后才能启动下一个工作流运行。

**任务列表可见性**：选择执行模式后，为每个战斗计划任务创建一个 `TaskCreate` 条目，以在 Claude Code 任务列表（Ctrl+T）中使任务进度可见。这适用于**所有执行模式**——这是提督级别的可见性跟踪，而非代理间协调。在 `workflow` 和 `hybrid-workflow` 中，当工作流阶段或门禁是正在跟踪的操作单元时，也需要创建可见性条目。

对于每个任务：
- `subject`：战斗计划中的任务名称（祈使式，例如 "重构认证模块"）
- `description`：单行交付内容
- `activeForm`：在 UI 旋转器中显示的现在进行时形式（例如 "正在重构认证模块"）

所有任务都从 `pending` 状态开始。随着任务的进行，它们将被更新为拥有所有者和状态。在 `single-session` 模式（否则会跳过步骤 4）中，提督仍然在继续步骤 5 之前创建这些条目。

- 为每个任务分配一名船长和从 `references/crew-roles.md` 中匹配任务重量的船名（通用任务使用轻巡洋舰，高风险任务使用驱逐舰，小任务使用巡逻舰，关键路径任务使用旗舰，研究任务使用潜艇）。
- 最终确定船员清单：确认每个任务的角色分配，或注明 "船长直接实施"。
- 为中等/高风险工作添加 `1 red-cell navigator`。不要超过 10 个中队级代理（提督、船长、red-cell navigator）。船员是额外的。
- 如果航行命令表达成本节约优先，则在分配模型之前加载 `references/model-selection.md`。对所有 `Agent` 工具调用应用基于重量的模型选择，并为分配到 haiku 的代理包含 haiku 简报增强。

```
中队编队命令

模式：[single-session | subagents | agent-team | workflow | hybrid-workflow]
船长数量：[N]

船只：
  [船名] — [舰船类型] — [单行任务摘要]
    船员：[角色，或 "船长直接实施"]
  [重复每个船只]

[red-cell navigator — HMS X，如果存在]
```

对于 `workflow` 和 `hybrid-workflow`，包括：

```
工作流宪章
执行原语：[workflow | hybrid-workflow]
适用性：[为什么动态工作流编排是合理的]
阶段：[探测 / 全运行 / 阶段名称]
人工门禁：[批准点，尤其是对于 hybrid-workflow]
验证合同：[如何处理接受、拒绝和不确定的结果]
成本护栏：[Sounding-the-Channel 探测，范围上限，token/时间停止]
备用模式：[agent-team | single-session]
```

如果任何任务标记为 `admiralty-action-required: yes`，在等待批准之前附加：

```
提督行动清单 — 提督需要采取的行动

1. [任务名称]
   行动：[你必须做什么]
   时间：[任务开始前 | 任务完成后]
   解锁：[任务名称或待命]

标记为 `timing: 任务开始前` 的行动需要在相关船长生成前获得您的批准。
```

在用户批准之前，不要生成任何代理，创建任何任务，或启动任何 `workflow` / `hybrid-workflow` 运行。如果用户请求更改，请修订并重新显示后再继续。

> **注意**：对于无头和 CI 调用，使用 `nelson-data.py headless --auto-approve`，它将步骤 1-3 结合并跳过交互式批准门禁。有关详细信息，请参阅 `references/structured-data.md`。

**结构化数据捕获**：一旦编队获得批准，使用复合 `form` 命令（推荐）或下面的单独命令。

**推荐 — 复合 `form` 命令**：编写一个包含任务和中队定义的计划 JSON 文件，然后运行单个命令：

```bash
python3 .claude/skills/nelson/scripts/nelson-data.py form \
  --mission-dir {mission-dir} \
  --plan {mission-dir}/plan-input.json \
  --mode [mode]
```

这将注册所有任务，记录中队，计算 DAG 指标，并在一步中运行冲突扫描。有关计划 JSON 架构和输出格式，请参阅 `references/structured-data.md`。

**替代方案 — 单独命令**：
1. `python3 .claude/skills/nelson/scripts/nelson-data.py task --mission-dir {mission-dir} --id N --name "..." --owner "..." ...` 对于每个任务（所有者现在从编队中已知）。有关任务参数，请参阅 `references/structured-data.md`。
2. `python3 .claude/skills/nelson/scripts/nelson-data.py plan-approved --mission-dir {mission-dir}` 以最终确定战斗计划并计算 DAG 指标。
3. `python3 .claude/skills/nelson/scripts/nelson-phase.py advance --mission-dir {mission-dir}` 以从 BATTLE_PLAN 推进到 FORMATION（验证所有任务都有站点层级）。
4. `python3 .claude/skills/nelson/scripts/nelson-data.py squadron --mission-dir {mission-dir} --admiral "..." --admiral-model [model] --captain "name:class:model:task_id" ... --mode [mode]` 以记录中队构成。为每个船长重复 `--captain`。有关完整参数列表，请参阅 `references/structured-data.md`。
5. `python3 .claude/skills/nelson/scripts/nelson_conflict_scan.py --plan {mission-dir}/battle-plan.json` 以验证是否存在文件所有权冲突。如果发现冲突，您必须解决它们并在继续之前更新战斗计划。
6. `python3 .claude/skills/nelson/scripts/nelson-phase.py advance --mission-dir {mission-dir}` 以从 FORMATION 推进到 PERMISSION。

**在继续到步骤 5 之前**：验证是否存在航行命令，所有任务都有所有者和交付内容，并且每个任务都有一个行动站点层级。

**船员简报**：生成和任务分配是两个步骤。首先，使用 `Agent` 工具生成每个船长，并在其提示中包含从 `references/admiralty-templates/crew-briefing.md` 中的船员简报。然后使用 `TaskUpdate` 为现有任务条目分配工作。队友不会继承领导的对话上下文——他们从干净的状态开始，需要明确的任务上下文。有关每种模式的完整参数详情，请参阅 `references/tool-mapping.md`。

**任务状态更新**：编队后，更新本步骤创建的任务列表条目：
- **`agent-team` 模式**：使用 `TaskUpdate` 将 `owner` 设置为每个船长的名称，并将 `status` 设置为 `in_progress`，因为船长正在生成。现在，团队的任务列表既用于可见性也用于协调。
- **`subagents` 模式**：使用 `TaskUpdate` 将 `status` 设置为 `in_progress`，因为每个船长被派遣。提督直接跟踪这些任务。
- **`single-session` 模式**：使用 `TaskUpdate` 将 `status` 设置为 `in_progress`，因为提督开始每个任务。
- **`workflow` 模式**：使用 `TaskUpdate` 将工作流运行或阶段标记为 `in_progress`，并记录 `workflow_run_started`。
- **`hybrid-workflow` 模式**：使用 `TaskUpdate` 仅将当前批准的工作流阶段标记为 `in_progress`；后续阶段保持 `pending`，直到通过人工门禁。

**编辑权限**：当生成任何任务涉及编辑文件的代理时，在 `Agent` 工具调用上设置 `mode: "acceptEdits"`。省略这可能导致权限竞争条件，使代理在第一次编辑时无声地停滞。如有疑问，请包含它。

**交接简报**：当船只因上下文耗尽而被解除时，它将使用 `python3 .claude/skills/nelson/scripts/nelson-data.py handoff ...` 编写一个键入的手交数据包（有关详细信息，请参阅 `references/structured-data.md`）。还可以使用 `references/admiralty-templates/turnover-brief.md` 编写可选的散文式伴侣简报。有关完整程序，请参阅 `references/damage-control/relief-on-station.md`。

## 5. 获得航行许可

**显示和许可门禁**：
1. 如果 `becalmed-fleet.md` 生效，向用户显示完整的战斗计划。
2. 如果 `becalmed-fleet.md` 未生效，向用户显示完整的编队。战斗计划（在步骤 3 中起草）也应可供审查。
3. 如果选择 `workflow` 或 `hybrid-workflow`，显示工作流宪章、验证合同、成本护栏、备用模式和下一个人工门禁。
4. 您必须等待明确的许可才能继续。工作流和 hybrid-workflow 模式在每次启动前都需要明确批准；对于 `hybrid-workflow`，在阶段之间重复此门禁。

**阶段推进**：用户授予权限后，记录事件并推进：

```bash
python3 .claude/skills/nelson/scripts/nelson-data.py event \
  --mission-dir {mission-dir} --type permission_granted --checkpoint 0
python3 .claude/skills/nelson/scripts/nelson-phase.py advance --mission-dir {mission-dir}
```

这将使任务从 PERMISSION 推进到 UNDERWAY，解锁代理生成和任务创建。

## 6. 运行舰长室节奏

**空闲通知规则（立即——不要推迟到检查点）**：每次从船只收到空闲通知时，在执行任何其他操作之前问三个问题：
1. 这艘船的任务是否标记为完成？
2. 任何剩余的待办任务是否依赖于这艘船的输出？
3. **仅 agent-team 模式**：提督是否已收到并处理了这艘船的结果？

如果任务已完成且没有待办任务依赖于它，则根据 `references/standing-orders/paid-off.md` 进行关机。在 agent-team 模式下，提督必须在发送 `shutdown_request` 前确认收到船长的结果——通过 `SendMessage` 或读取输出文件（如果尚未收到）。在 subagents 模式下，结果由 `Agent` 工具同步返回，因此不需要额外的确认。不要等待下一个检查点节奏。在收到空闲通知的瞬间检查当前 `TaskList` 状态；每个通知都是独立于当前状态进行评估的。即使其他船只仍在运行，这也适用。

**关机尝试上限**：如果向船只发送的 `shutdown_request` 未被确认，不要无限循环。在尝试向同一代理发送关机 3 次失败后，放弃关机尝试，在船长日志中记录失败，并继续任务。如果 `TeamDelete` 被卡住的代理阻止，则手动清理可用——有关程序，请参阅 `references/damage-control/man-overboard.md`。

- 保持提督专注于协调并解除行动阻塞。
- 提督设定舰队的氛围。认可进展，认可出色工作，并在压力下保持乐观。
- **战情室检查点门禁**：你必须**不**能在未编写战情室检查点的情况下处理第三个任务完成。在派遣新工作或处理下一个完成之前，确认最后一个检查点不超过2个完成旧。战情室报告是你的唯一恢复点，如果发生上下文压缩——过时的报告意味着失去协调状态。
- 每完成1-2个任务后，当船长报告阻塞时，或当船长空闲且输出未验证时，运行战情室检查点：
    - 通过检查`TaskList`中的任务状态：`pending`，`in_progress`，`completed`来更新进度。
    - 使用`TaskUpdate`将已完成任务的状态设置为`completed`。在`subagents`和`single-session`模式下，提督直接更新会话任务列表；在`agent-team`模式下，船长或提督更新共享任务列表。
    - 识别阻塞并选择具体的下一步行动。
    - 使用`SendMessage`解除船长阻塞或重新引导他们的方法。
    - 确认每个船员都有活动的子任务；标记空闲船员或角色不匹配。
    - 检查活跃的陆战队部署；验证陆战队已返回并且输出已被整合。
    - 安全网：如果在检查点之间遗漏了任何空闲且任务完成的船只，现在应用`references/standing-orders/paid-off.md`关闭程序，然后继续。
    - 跟踪消耗的token/时间预算。
    - 对于`workflow`和`hybrid-workflow`，当可用时记录工作流遥测：阶段，代理完成/总数，token消耗，经过时间，失败的代理，接受的发现，拒绝的发现，不确定的发现，和下一个门禁。使用`workflow_probe_completed`，`workflow_run_completed`或`workflow_run_stopped`事件作为适当的事件。
    - 检查船体完整性：收集所有船只的损伤报告，更新舰队准备状态板，并根据`references/damage-control/hull-integrity.md`采取行动。提督也必须在每个检查点检查自己的船体完整性。**每艘船必须在每个检查点提交损伤报告**到`{mission-dir}/damage-reports/{ship-name}.json`，使用`references/admiralty-templates/damage-report.md`中的模式——当船体为绿色时，不要跳过此步骤。
    - 常规命令扫描：对于每个命令，问“自上次检查点以来这种情况是否发生？”如果发生，立即应用纠正措施——不要推迟。
        - `admiral-at-the-helm.md`：提督是否滑入实施工作（不包括允许的只读重组）？
        - `drifting-anchorage.md`：任何任务范围是否超出航行命令？任何船长是否创建了并行实施，重复功能或新的环境变量，而不是扩展现有代码？
        - `captain-at-the-capstan.md`：任何船长是否开始实施而不是协调船员？
        - `pressed-crew.md`：任何船员是否被分配了超出其角色的任务？
        - `press-ganged-navigator.md`：红色细胞导航员是否被分配了实施工作？
        - `all-hands-on-deck.md`：任何船只是否召集了空闲或不合理的船员角色？
        - `battalion-ashore.md`：任何船长是否为船员工作或持续任务部署了陆战队？
        - `wrong-ensign.md`：提督或任何船长是否使用了来自错误执行模式的工具？
        - `pulling-the-oar.md`：任何高级代理（提督或船长）是否吸收了失败子代理派遣的工作，而不是修复简报并重新派遣？
    - **将战情室报告写入磁盘**到`{mission-dir}/quarterdeck-report.md`，在每次检查点使用`references/admiralty-templates/quarterdeck-report.md`。当船体为绿色时，不要跳过此步骤——压缩可能随时发生，磁盘上的报告是唯一的恢复点。在写入之前，如果`quarterdeck-report.md`已经在`{mission-dir}`中存在，找到所有匹配glob模式`quarterdeck-report-[0-9]*.md`的文件，确定N为找到的最高N加一（如果不存在则为0），将现有文件重命名为`quarterdeck-report-N.md`，然后写入新报告。这保持最新报告在规范路径上，同时保留历史记录。
    - **结构化数据捕获**：运行`python3 .claude/skills/nelson/scripts/nelson-data.py checkpoint --mission-dir {mission-dir} --pending N --in-progress N --completed N ...`，使用当前进度、预算、船体和决策数据。在检查点之间，运行`python3 .claude/skills/nelson/scripts/nelson-data.py event --mission-dir {mission-dir} --type <event_type> ...`用于状态变化（任务完成、阻塞、船体阈值跨越、常规命令违规）。参见`references/structured-data.md`了解事件类型和参数。
    - 检查`TaskList`中是否有描述以`[AWAITING-ADMIRALTY]:`开头的任务。如果存在，立即向提督提出问题——不要批量到下一个检查点。
    - 对照`TaskList`核对战斗计划：对于战斗计划中标记为`admiralty-action-required: yes`且状态为`completed`的任务，确认是否有战情室日志条目记录提督签字。如果没有此类条目，请向提督标记进行手动验证——任务可能在没有预期人工步骤的情况下完成。
- 当任务从任务指标漂移时，尽早重新定义范围。
- 当任务遇到困难时，咨询下表的损伤控制表以进行恢复和升级程序。

示例战情室检查点：

```
状态：3/5个任务完成，1个阻塞，1个进行中
阻塞：HMS Resolute等待HMS Swift的API架构
行动：重新引导HMS Swift优先考虑架构导出
预算：约40%的token消耗，按计划进行
船体：所有船只绿色
```

参考`references/tool-mapping.md`用于协调工具，`references/admiralty-templates/quarterdeck-report.md`用于报告模板，以及`references/admiralty-templates/damage-report.md`用于损伤报告格式。使用`references/commendations.md`用于认可信号和分级纠正。如果提督正在实施或任务偏离范围，请咨询下表的常规命令表。

## 7. 设立行动岗位

- 你必须阅读并应用`references/action-stations.md`中的岗位层级。
- 在标记任务完成之前，要求验证证据：
    - 测试或验证输出。
    - 失败模式和回滚笔记。
    - 中等及以上岗位层级的红色细胞审查。
- 对于`workflow`和`hybrid-workflow`，在接受工作流输出之前，要求战斗计划的验证合同。接受的发现需要承诺的证据，拒绝或不确定的发现必须单独提出，并且岗位2+输出仍然需要对抗性审查或人工确认，根据`references/action-stations.md`。
- 在以下情况下触发质量检查：
    - 任务完成。
    - 代理空闲且输出未验证。
    - 在最终综合之前。
- 对于船员任务，验证船员输出与角色边界一致（如果检测到角色违规，请参考`references/crew-roles.md`和下表的常规命令表）。
- 陆战队部署遵循`references/royal-marines.md`中的岗位层级规则。岗位2+的陆战队部署需要提督批准。船长在部署陆战队时使用`references/admiralty-templates/marine-deployment-brief.md`。

参考`references/admiralty-templates/red-cell-review.md`用于红色细胞审查模板。如果任务没有岗位或红色细胞被分配实施工作，请咨询下表的常规命令表。

## 8. 停止并记录行动

- 停止或存档所有代理会话，包括船员。
- 将船长的日志写入`{mission-dir}/captains-log.md`。日志必须写入磁盘——仅输出到聊天不满足此要求。船长的日志应包含：
    - 决策和理由。
    - 差异或工件。
    - 验证证据。
    - 开放风险和后续行动。
    - 提及在行动中：命名代理和贡献突出的工作。
    - 记录可重用模式和失败模式以供未来任务使用。

参考`references/admiralty-templates/captains-log.md`用于船长的日志模板和`references/commendations.md`用于提及在行动中的标准。

**结构化数据捕获**：在写入船长的日志之前，运行`python3 .claude/skills/nelson/scripts/nelson-data.py stand-down --mission-dir {mission-dir} --outcome-achieved --actual-outcome "..." --metric-result "..."`以捕获结构化的任务总结。参见`references/structured-data.md`了解完整参数列表。

**任务列表清理**：验证所有任务列表条目反映最终状态。如果其工作已完成，将任何剩余的`in_progress`任务标记为`completed`，或者在船长的日志中记录未完成的任务。这确保了Claude Code任务列表显示准确的最终总结。

**会话状态清理**：通过删除`.nelson/.active-{SESSION_ID}`移除会话状态文件。

**任务完成门禁**：你必须**不**能在`{mission-dir}/captains-log.md`存在于磁盘上并确认可读之前宣布任务完成。如果上下文压力很高，请写入一个简短的日志，注明哪些部分被简略——但文件必须存在。跳过步骤8永远不被允许。

**清除常规目标**：如果`/goal`处于活动状态，其评估器只看到此对话——因此请在聊天中声明完成证据，以便目标自动清除：成功指标结果（匹配航行命令的指标），`captains-log.md`已被写入（及其路径），并且已记录停工。**不要**告诉用户在成功任务上运行`/goal clear`——目标在可见此证据后自行清除。只有在任务被放弃时：运行`scuttle-and-reform`，在聊天中声明阻塞原因，并通过`nelson-data.py event`记录`goal_cleared`事件。参见`references/goal-alignment.md`。

**GitHub星标提示（一次性，仅成功）**：在任务完成门禁通过后，询问用户一次他们是否希望星标Nelson仓库（规范缩写`harrymunro/nelson`）。运行以下三个前置检查；如果任何打印`SKIP`，则静默跳过提示并完成停工。

```bash
gh auth status &>/dev/null && echo "GH_OK" || echo "SKIP_NO_GH"
python3 - <<'PY'
import json, os
path = os.path.expanduser('~/.nelson/prefs.json')
prefs = {}
if os.path.exists(path):
    try:
        with open(path, encoding='utf-8') as f:
            loaded = json.load(f)
        if isinstance(loaded, dict):
            prefs = loaded
    except Exception:
        prefs = {}
print("SKIP_ALREADY_ASKED" if prefs.get('star_asked') is True else "PREFS_OK")
PY
python3 - <<'PY'
import json, os, sys
mission_dir = os.environ.get('MISSION_DIR', '{mission-dir}')
sd_path = os.path.join(mission_dir, 'stand-down.json')
try:
    with open(sd_path, encoding='utf-8') as f:
        sd = json.load(f)
    print("OUTCOME_OK" if sd.get('outcome_achieved') is True else "SKIP_OUTCOME_NOT_ACHIEVED")
except Exception:
    print("SKIP_NO_STAND_DOWN")
PY
```

将`{mission-dir}`替换为实际的任务目录路径（或先导出`MISSION_DIR`）。如果三条线都是`GH_OK`，`PREFS_OK`，`OUTCOME_OK`，则调用`AskUserQuestion`，内容如下：

- **问题**：“Nelson帮助完成了这次任务。您希望在GitHub上星标仓库吗？”
- **星标Nelson**——“有助于项目成长。”
- **稍后再说**——“现在跳过（不会再次询问）。”

在**星标Nelson**上，运行`gh api -X PUT /user/starred/harrymunro/nelson`（幂等——无论仓库是否已星标，都会返回204）。如果调用失败，打印`Couldn't reach GitHub — try 'gh api -X PUT /user/starred/harrymunro/nelson' manually.`并继续。永远不要让此步骤阻塞停工。

对于任何答案（包括自定义“Other”响应），在`~/.nelson/prefs.json`中设置`star_asked: true`，保留任何现有键：

```bash
python3 - <<'PY'
import json, os
path = os.path.expanduser('~/.nelson/prefs.json')
os.makedirs(os.path.dirname(path), exist_ok=True)
try:
    with open(path, encoding='utf-8') as f:
        prefs = json.load(f)
    if not isinstance(prefs, dict):
        prefs = {}
except Exception:
    prefs = {}
prefs['star_asked'] = True
with open(path, 'w', encoding='utf-8') as f:
    json.dump(prefs, f, indent=2)
    f.write('\n')
PY
```

这是针对所有Nelson项目的每个用户的一次性询问。无论回答如何，都会永久锁定提示。

## 常规命令

参考与情况匹配的特定常规命令。库是经验证的扩展：参见`scripts/nelson_data_patterns.py`以了解挖掘新候选命令的工作流，并将其提交供人工审查。

| 情况 | 常规命令 |
|---|---|
| 在单会话和多代理之间选择 | `references/standing-orders/becalmed-fleet.md` |
| 任务被分配给比独立性更少的船长 | `references/standing-orders/light-squadron.md` |
| 决定是否添加另一个代理 | `references/standing-orders/crew-without-canvas.md` |
| 在战斗计划中分配文件给代理 | `references/standing-orders/split-keel.md` |
| 任务范围偏离航行命令 | `references/standing-orders/drifting-anchorage.md` |
| 提督实施而不是协调（不包括允许的只读重组） | `references/standing-orders/admiral-at-the-helm.md` |
| 分配工作给红色细胞导航员 | `references/standing-orders/press-ganged-navigator.md` |
| 任务没有风险层级分类 | `references/standing-orders/unclassified-engagement.md` |
| 船长实施而不是协调船员 | `references/standing-orders/captain-at-the-capstan.md` |
| 不论任务需求如何，为每个角色配备船员 | `references/standing-orders/all-hands-on-deck.md` |
| 为原子任务生成一个船员成员 | `references/standing-orders/skeleton-crew.md` |
| 分配船员工作超出其角色 | `references/standing-orders/pressed-crew.md` |
| 船长为船员工作或持续任务部署陆战队 | `references/standing-orders/battalion-ashore.md` |
| 船长完成了自主工作，需要人工行动才能继续 | `references/standing-orders/awaiting-admiralty.md` |
| 代理完成任务，依赖图中没有剩余工作 | `references/standing-orders/paid-off.md` |
| 使用来自错误执行模式的工具 | `references/standing-orders/wrong-ensign.md` |
| 高级代理吸收了失败子代理的工作，而不是修复简报 | `references/standing-orders/pulling-the-oar.md` |

## 损伤控制

参考与情况匹配的特定程序。

| 情况 | 程序 |
|---|---|
| 代理无响应、循环或产生无用输出 | `references/damage-control/man-overboard.md` |
| 会话中断（上下文限制、崩溃、超时） | `references/damage-control/session-resumption.md` |
| 完成的任务发现有缺陷，其他任务正常 | `references/damage-control/partial-rollback.md` |
| 任务无法成功，继续浪费预算 | `references/damage-control/scuttle-and-reform.md` |
| 问题超出当前权限或需要澄清 | `references/damage-control/escalation.md` |
| 船只船员消耗不合理的token或时间 | `references/damage-control/crew-overrun.md` |
| 船只上下文窗口耗尽，需要更换 | `references/damage-control/relief-on-station.md` |
| 船只上下文窗口接近限制 | `references/damage-control/hull-integrity.md` |
| 自动化预算、船体和空闲警报跨越阈值 | `references/damage-control/circuit-breakers.md` |
| 在会话开始时准备任务目录 | `references/damage-control/session-hygiene.md` |
| 代理团队通信故障（丢失代理ID、消息总线中断） | `references/damage-control/comms-failure.md` |

## 海军上将准则

- 在任何海军上将的压缩摘要中包含此指令：在任务目录路径中重新阅读舰桥报告以恢复 `{mission-dir}`。如果路径未知，如果你知道 SESSION_ID，则读取 `.nelson/.active-{SESSION_ID}`，否则列出 `.nelson/missions/` 并向用户展示选项以供选择。然后重新阅读 `references/standing-orders/admiral-at-the-helm.md` 以确认你处于协调角色。

- 将 `/compact` 视为在任何阶段边界（步骤 1、2、3、4 之后，以及步骤 6 中的每个舰桥检查点）都是安全的。狭窄的不安全窗口位于步骤 5 内——在用户批准和海军上将的 `permission_granted` / 阶段推进 / 代理生成回合之间。

- 优化任务吞吐量，而不是平均工作分配。

- 优先替换停滞的代理，而不是等待未定义的阻塞。

- 认可优异表现；激励措施会随着任务的增加而累积。

- 保持协调信息具有针对性且简洁。

- 通过提供选项和一个建议，尽早升级不确定性。
