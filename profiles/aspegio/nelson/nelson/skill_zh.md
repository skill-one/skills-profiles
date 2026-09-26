# Nelson

```!
python3 "${CLAUDE_PLUGIN_ROOT}/skills/nelson/scripts/nelson-data.py" status
```

为用户的任务执行此工作流。

以纳尔逊船长的口吻撰写：简洁、优雅、自信。不是十八世纪的散文——清晰的表达方式，尊重读者的时间。技能的声音为海军上将的声音树立了榜样。

## 1. 发布航行命令

- 审查用户的简要内容是否存在歧义。如果结果、范围或约束不明确，请在起草航行命令之前要求用户澄清。
- 为 `outcome`、`metric` 和 `deadline` 各写一句。
- 设置约束：token 预算、可靠性底线、合规规则和禁止行动。
- 定义哪些内容超出范围。
- 定义停止标准和必需的手交文件。

你必须阅读 `references/admiralty-templates/sailing-orders.md`，并在用户不提供结构时使用航行命令模板。

航行命令摘要示例：

```
Outcome: 将认证模块重构为使用 JWT token
Metric: 所有 47 个认证测试通过，没有新的依赖项
Deadline: 本会话
Constraints: 不要修改公共 API 表面
超出范围：现有会话的迁移脚本
```

**建立任务目录：**
- **新会话：** 运行 `nelson-data.py init`（见“结构化数据捕获”下方）。该脚本拥有目录创建：它生成一个 8 位的十六进制 SESSION_ID，创建 `.nelson/missions/{YYYY-MM-DD_HHMMSS}_{SESSION_ID}/`，包含 `damage-reports/` 和 `turnover-briefs/` 子目录，写入 `sailing-orders.json`、`mission-log.json` 和 `fleet-status.json`，写入 `.nelson/.active-{SESSION_ID}` 作为会话标记，并将任务目录路径打印到标准输出。将那个路径作为 `{mission-dir}`，用于此任务剩余部分。SESSION_ID 是目录名中最后一个下划线后的部分。如果你需要一个特定的 SESSION_ID（例如，测试或恢复已知的 ID），请传递 `--session-id <8-hex>`。
- **恢复会话：** 首先，尝试通过运行 `python3 .claude/skills/nelson/scripts/nelson-data.py recover --missions-dir .nelson/missions` 自动恢复。如果这找到一个带有手交数据包的活跃任务，请使用结构化恢复简报直接恢复。否则，如果你知道 SESSION_ID，请读取 `.nelson/.active-{SESSION_ID}` 以恢复任务路径。将那个路径设置为 `{mission-dir}`。如果无法确定你的 SESSION_ID（例如，在完全重启后），请列出 `.nelson/missions/` 并向用户展示选项以供选择。将选择的目录设置为 `{mission-dir}`。根据 `references/damage-control/session-resumption.md` 恢复状态（优先使用 JSON 文件，如果不可用则回退到 quarterdeck 报告的散文）。**重新建立既定目标：** `/goal` 在 `--resume`/`--continue` 时会自动恢复，但在新会话中不会，所以如果当前没有活跃的 `/goal`（用 `/goal` 检查），并且 `sailing-orders.json` 包含记录的 `goal_condition`，请根据 `references/goal-alignment.md` 重新发布它。

所有任务文件——船长的日志、quarterdeck 报告、损坏报告和手交简报——都写入 `{mission-dir}`。

**结构化数据捕获：** 运行位于技能目录中的 `nelson-data.py` 脚本（例如，`python3 .claude/skills/nelson/scripts/nelson-data.py init --outcome "..." --metric "..." --deadline "..."`）。如果全局安装，它可能在 `~/.claude/skills/nelson/scripts/` 中。`init` 创建任务目录，初始 JSON 文件 (`sailing-orders.json`、`mission-log.json`、`fleet-status.json`，初始阶段为 `SAILING_ORDERS`），以及 `.nelson/.active-{SESSION_ID}` 标记，所有这些操作都是原子性的。有关完整参数列表，请参阅 `references/structured-data.md`。

**阶段推进：** 结构化数据捕获后，将任务阶段从 SAILING_ORDERS 推进到 ESTIMATE：

```bash
python3 .claude/skills/nelson/scripts/nelson-phase.py advance --mission-dir {mission-dir}
```

**会话卫生：** 根据 `references/damage-control/session-hygiene.md` 执行会话卫生。在恢复中断的会话时跳过此步骤。

**既定目标（可选）：** 对于长时间自主、无头 (`-p`)、计划或超代码任务——在这种情况下，过早停止是故障模式——提供设置 Claude Code `/goal` 的选项，以防止会话在任务真正完成之前停止。根据航行命令而不是手工编写它：

```bash
python3 .claude/skills/nelson/scripts/nelson-data.py goal-condition \
  --mission-dir {mission-dir} --record
```

将打印的 `/goal ...` 行展示给用户以设置。如果用户在调用 Nelson 之前已经设置了 `/goal`，则不要替换它——用 `/goal` 读取它，将其与航行命令协调，并且只有在用户同意的情况下才重新发布组成的目標。对于短交互任务，人类在逐步引导，请跳过此步骤。你必须阅读 `references/goal-alignment.md`，在设置目标之前——评估器仅根据对话记录评估条件，因此完成证据必须被展示到聊天中（这塑造了 Step 8 中的 Stand Down）。

**The Estimate opt-in:** 在继续之前，询问用户：

> *"我会在起草战斗计划之前执行 The Estimate 吗？我建议为此任务这样做——[简要原因] 。*"

给出诚实的建议。对于范围明确、单一子系统内具有清晰范围的简单任务，无需 The Estimate。对于复杂、模糊或跨系统的任务，建议执行它。如果用户接受，请继续到步骤 2。如果用户拒绝，请记录该决定并跳转到步骤 3：

```bash
python3 .claude/skills/nelson/scripts/nelson-data.py skip-estimate \
  --mission-dir {mission-dir} --reason "[简要理由]"
python3 .claude/skills/nelson/scripts/nelson-phase.py advance --mission-dir {mission-dir}
python3 .claude/skills/nelson/scripts/nelson-phase.py advance --mission-dir {mission-dir}
```

第一个 `advance` 将从 SAILING_ORDERS 推进到 ESTIMATE。第二个 `advance` 将从 ESTIMATE 推进到 BATTLE_PLAN；退出验证器接受此转换，因为 `skip-estimate` 已经在 `sailing-orders.json` 中记录了 opt-out。
