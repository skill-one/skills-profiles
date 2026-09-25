# 项目管理 — 领域协调器与交付循环

这个协调器有两个功能。**路由：** 分叉上下文，使用 `scripts/pm_goal_router.py` 对 PM 咨询进行分类，运行其中的一个子技能，并返回摘要。**循环：** 将交付目标转化为有边界的智能体循环 — 通过捆绑的 Atlassian MCP 拉取实时 Jira 数据，将其桥接至领域的确定性分析工具，通过机器运行的关卡验证每一步，并在所有内容验证或人工豁免之前拒绝关闭。捆绑的 `.mcp.json` 将 Atlassian 远程 MCP (`https://mcp.atlassian.com/v1/sse`) 连接起来（OAuth 由 Claude Code 处理）。

## 调用时机

| 症状 | 子技能 |
|---|---|
| "项目/组合健康状况、风险 EMV、容量" | `senior-pm` |
| "Sprint 速度、回顾跟进、仪式健康状况、何时完成" | `scrum-master` |
| "JQL、Jira 工作流、看板、自动化" | `jira-expert` |
| "Confluence 空间、页面树、内容审核" | `confluence-expert` |
| "用户、组、权限、SSO" | `atlassian-admin` |
| "可复用的 Jira/Confluence 模板" | `atlassian-templates` |
| "会议记录、谈话时长、行动项" | `meeting-analyzer` |
| "状态更新、3P 更新、利益相关者沟通" | `team-communications` |

## 路由逻辑（确定性）

运行路由器 — 当脚本可以决定时，不要肉眼查看表格：

```bash
python3 scripts/pm_goal_router.py --text "<目标>" --output json
```

退出 0 → `route_to` 指定子技能：加载其 SKILL.md 并遵循其工作流。退出 2 → 提问一个澄清问题，命名列出的候选者，并给出推荐答案。退出 3 → 无信号：要求用户用交付成果重新陈述目标。永远不要默默猜测；永远不要默默链式调用第二个子技能 — 先消化，再确认，然后链式调用。

## 交付循环（智能体）

对于目标（而非问题） — "将 Sprint 14 验证关闭"、"从实时 Jira 生成组合健康状况报告"、"每周使我们的流程指标可见" — 运行循环库合约（观察 → 选择 → 行动 → 验证 → 记录 → 重复或停止）：

1. **观察** — 拉取最新状态：`mcp__atlassian__searchJiraIssuesUsingJql`（先通过 `getAccessibleAtlassianResources` 获取 `cloudId`），保存结果 JSON，然后桥接：
   ```bash
   python3 scripts/jira_snapshot_bridge.py --input snapshot.json --to flow            # WIP，吞吐量、周期时间 p50/85/95、工作项年龄、SLE、老化警报
   python3 scripts/jira_snapshot_bridge.py --input snapshot.json --to sprint > s.json # scrum-master 模式
   python3 ../scrum-master/scripts/velocity_analyzer.py s.json                        # 速度 + 波动性 + 预测
   ```
   添加 `--forecast N` 以获取有初始值的蒙特卡洛 "N 个项目何时完成" 的答案（拒绝少于 10 个已完成项目的预测 — 薄历史预测是谎言）。
2. **选择** — 使用 `pm_goal_router.py` 路由下一个任务；一次一个任务。
3. **行动** — 根据路由的子技能的 SKILL.md 使用其自己的工具执行。
4. **验证** — 使用以下命令验证计划和每个关闭：
   ```bash
   python3 scripts/delivery_loop_gate.py --plan plan.json --mode plan    # 退出 2 = 阻塞
   python3 scripts/delivery_loop_gate.py --plan plan.json --mode close   # 退出 4 = 拒绝关闭
   ```
   加上每个子技能自己的关卡（scrum-master 的 ≥ 3-sprints 规则、atlassian-admin 的 VERIFY 步骤）。永远不要裁决你自己的验证。
5. **记录 / 重复或停止** — 对于多任务目标，运行状态通过仓库范围的 harness（它强制执行尝试限制、迭代预算和证据记录）：
   ```bash
   python3 engineering/agent-harness/skills/agent-harness/scripts/goal_compiler.py \
     --goal "<目标>" --manifest engineering/agent-harness/skills/agent-harness/assets/harnesses/project-management.json \
     --out .agent-harness/plan.json
   python3 engineering/agent-harness/skills/agent-harness/scripts/loop_controller.py init|next|record|verify|close ...
   ```
   终端状态：成功、干净的无操作、阻塞、需要批准、耗尽、停滞。耗尽的预算是升级 — 永远不是成功报告。

## 硬性规则（智能体委托治理）

1. **智能体是贡献者，永远不是所有者**（线性模型）：每个循环任务都有一个命名的负责人；由智能体执行的任务也带有一个命名的审查者。
   `delivery_loop_gate.py` 强制执行此规则（G1/G2）。
2. **接受必须是可以机器检查的** — 一个命令，或一个带有阈值的标准。 "看起来不错" 不是关卡（G3）。
3. **每个 Jira/Confluence 的写入都是可审计的，并且首先可撤销**（Rovo 纪律）：永远不要 `transitionJiraIssue` 到 Done 而没有验证证据；破坏性/不可逆操作（删除、权限更改、全局管理员）是需要批准的终端状态，而不是循环步骤。
4. **永远不要修改你被评判的关卡** — 与自研究智能体相同的锁定评估者不变量。
5. **预测是范围带置信度，而不是日期** — 蒙特卡洛百分位数（p50/p70/p85/p95），根据 Vacanti。单日期承诺是反模式。
6. **每个任务最多 3 次尝试，每个目标最多 12 次循环迭代** — 然后升级到命名的负责人，并附带证据日志。

## 强制性问题库（与文档对话模式）

每次一个，推荐答案，规范引用。在运行子技能或开始循环之前，直到定义决策被锁定：

- **SPRINT 轨道**： "你想测量流程（周期时间、WIP、吞吐量、年龄）还是预测交付？推荐：先测量 — 未测量流程的预测是噪音。规范：Kanban 指南（2025 年 5 月）四个强制流程测量；Vacanti，《可操作的敏捷指标》。"
- **HEALTH 轨道**： "你的项目状态是自我报告的 RAG 还是派生的？推荐：派生它（进度偏差、老化 WIP、范围波动）并与自我报告进行比较 — 那个差异会找到西瓜项目。规范：Kanban 指南 2025；DORA 2025（AI 放大，而不是修复，弱信号）。"
- **JIRA 轨道**： "这个配置更改可以首先部署到测试项目吗？推荐：始终在测试项目中阶段化；jira-expert 的工作流验证器必须在生产环境中退出 0。规范：jira-expert 验证工作流。"
- **ADMIN 轨道**： "这个操作是可逆的，谁批准它？推荐：在触摸权限之前命名批准者 — 管理员操作是在任何循环中需要批准的终端状态。规范：atlassian-admin VERIFY 纪律；循环库停止状态。"
- **循环输入**： "什么单一可观察结果意味着完成，哪个命令证明它？推荐：一个命名的工件 + 一个针对它的退出 0 的命令。规范：智能体引擎验证者的法律；Anthropic，《构建有效智能体》（评估者需要明确的标准）。"
- **会议/沟通轨道**： "这个会议可以是异步的书面更新吗？推荐：状态广播会议转换为异步 3P 更新；决策会议保持同步。规范：GitLab 异步优先手册。"

## 假设

1. 用户有（或正在为某人准备分析）交付权限。
2. Jira/Confluence 访问通过捆绑的 MCP；`project-management/references/atlassian-mcp-tools.md` 中未包含的功能（项目/ Sprint/看板/空间创建、管理员配置）在 Web UI 中完成 — 永远不要发明工具名称。
3. 输入可能是部分的 — 每个工具都提供 `--sample` 以首先可见形状。

## 非目标

- 不是子技能的替代品 — 协调器路由和循环；子技能做工作。
- 不是通用循环引擎 — 那是 `engineering/agent-harness`；这个协调器是 PM 领域适配器（数据桥接 + 治理关卡 + 轨道路由）。
- 不决定 *要构建什么* — 那是 `product-team`。

## 输出工件

| 模式 | 工件 |
|---|---|
| 路由 | 子技能自己的工件 + ≤ 200 字的摘要，包含一个规范引用的挑战 |
| 流报告 | `flow_metrics.json`（桥接输出）与 SLE 合规性 + 老化警报 |
| 交付循环 | `.agent-harness/plan.json` + `state.json` + 关卡裁决 + 关闭交接 |

## 反模式（不要）

- ❌ "为了全面起见" 运行所有 8 个子技能 — 路由到一个，消化，确认后链式调用
- ❌ 当可以通过一个 MCP 调用获取 Jira 快照时，从手动输入的数字报告 Sprint 健康或预测 — 桥接真实数据
- ❌ 在未验证的任务下关闭循环，或报告耗尽的预算为成功
- ❌ 让智能体成为记录的指派者 — 人类拥有，智能体贡献
- ❌ 在循环内自动转换 Jira 问题或触摸权限，而没有命名的批准者

## 参考文献

- [references/flow_forecasting_canon.md](references/flow_forecasting_canon.md) — Kanban 指南 2025、Vacanti 蒙特卡洛、DORA 2025、EBM、SPACE
- [references/agentic_delivery_governance.md](references/agentic_delivery_governance.md) — 线性/Rovo 委托模型、Anthropic 智能体模式、审计纪律
- [references/pm_loop_playbook.md](references/pm_loop_playbook.md) — 五个可重用的 PM 循环（Sprint、健康、回顾行动、RAID-卫生、沟通）映射到循环合约
- 规范 MCP 工具列表：`project-management/references/atlassian-mcp-tools.md`
- 循环引擎：`engineering/agent-harness` · 循环词汇：`loop-library`
