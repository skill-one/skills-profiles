# 产品团队 — 领域协调器与发现循环

这个协调器有两个工作职责。**路由：** 分叉上下文，使用 `scripts/product_goal_router.py` 对所有 16 个产品团队通道（12 个捆绑插件 + 4 个独立插件）进行产品查询分类，运行其中之一，并返回摘要。**循环：** 以机器可验证的关卡作为边界智能体循环运行产品工作——持续发现循环（由 `discovery_cadence_tracker.py` 评估的每周节奏，由 `ost_linter.py` 强制的树状结构）和通过仓库级代理套件进行目标规模运行。

## 调用时机

| 症状 | 子技能 |
|---|---|
| "优先级排序功能 / RICE / PRD" | `product-manager-toolkit` |
| "OKRs、战略级联" | `product-strategist` |
| "用户画像、可用性、研究综合" | `ux-researcher-designer` |
| "设计令牌、WCAG 对比度" | `ui-design-system` |
| "竞争对手矩阵、拆解" | `competitive-teardown` |
| "留存率、用户群组、漏斗、KPI" | `product-analytics` |
| "A/B 测试、样本量、假设" | `experiment-designer` |
| "发现、假设、机会树" | `product-discovery` |
| "路线图沟通、发布说明、变更日志" | `roadmap-communicator` |
| "规范 → 可运行仓库" | `spec-to-repo` |
| "着陆页 (Next.js/Tailwind)" | `landing-page-generator` |
| "SaaS 模板" | `saas-scaffolder` |
| "用户故事、冲刺容量" | `agile-product-owner` (独立) |
| "Apple HIG 审计" | `apple-hig-expert` (独立) |
| "从现有代码库生成 PRD" | `code-to-prd` (独立) |
| "总结论文/文章" | `research-summarizer` (独立) |

## 路由逻辑（确定性）

```bash
python3 scripts/product_goal_router.py --text "<目标>" --output json
```

退出码 0 → `route_to` 指定技能（包括 `skill_path`，包括独立插件）：加载其 SKILL.md 并遵循其工作流。退出码 2 → 提问一个澄清问题，列出候选技能，并推荐答案。退出码 3 → 无信号：要求用户用指定的可交付成果重新陈述目标。永远不要无声猜测；永远不要无声链式调用——先生成摘要，再确认，然后链式调用。

## 发现循环（领域的循环智能体）

现代发现是一个每周习惯，而不是一个项目阶段（Torres）。以两个机器关卡作为边界循环运行它：

1. **观察** — 维护 `discovery_log.json`（访谈、假设测试；形状在 `assets/sample_discovery_log.json` 中）并评分节奏：
   ```bash
   python3 scripts/discovery_cadence_tracker.py --input discovery_log.json
   ```
   在少于 2 次访谈时拒绝（退出码 5）——还没有可测量的节奏。输出：健康度 0–100、判断结果 HEALTHY/AT-RISK/DORMANT、命名差距和 `next_loop_action`。
2. **选择** — 追踪器的 `next_loop_action` 就是选择：安排接触点、重新锚定指南在结果上，或测试未测试的顶级假设（路由到 `product-discovery` 的 `assumption_mapper` 进行优先级排序）。
3. **行动** — 使用路由的子技能的工具运行访谈 / 假设测试。
4. **验证** — 在它可以驱动路线图之前保持树状结构的完整性：
   ```bash
   python3 scripts/ost_linter.py --input ost.json    # 退出码 2 = NEEDS-REWORK，在引用树之前修复
   ```
   规则：一个可衡量的结果根 (O1)、机会是需求而不是功能 (O2)、目标机会比较 ≥ 2 个解决方案 (O3)、每个解决方案都有一个假设测试 (O4)、没有孤儿解决方案 (O5 — 特征工厂的指示)。
5. **记录 / 重复或停止** — 更新日志，保持每周连续性。停止状态：HEALTHY + 验证的假设 → 升级到 `experiment-designer`（构建 A/B 关卡）或 `product-manager-toolkit`（PRD）；DORMANT 持续 4 周以上 → 升级到产品负责人（姓名）——不要无声地让发现死亡。

对于构建规模的目标（“将这个验证的规范转换为仓库并验证它”），通过仓库级套件编译：

```bash
python3 engineering/agent-harness/skills/agent-harness/scripts/goal_compiler.py \
  --goal "<目标>" --manifest engineering/agent-harness/skills/agent-harness/assets/harnesses/product-team.json \
  --out .agent-harness/plan.json
```

领域的三个最强关闭关卡作为任务验证插入：
`../spec-to-repo/scripts/validate_project.py`（退出码 0）、`code-to-prd` 的黄金 `expected_outputs/` 和 `research-summarizer` 的引用计数检查。

## 硬性规则

1. **证据先于信念**：除非 `ost_linter.py` 退出码为 0，否则路线图项目不会引用 OST；不要从单个参与者那里断言洞察（轶事而不是洞察）。
2. **结果优先**：每个循环都挂在一个可衡量的结果上——lint 的 O1 规则是输入关卡。
3. **实验由数学控制**：样本量来自 `../experiment-designer/scripts/sample_size_calculator.py`，永远不要凭感觉；报告 MDE 与判断结果一起。
4. **优先级展示其框架**：稳定状态使用 RICE，时间敏感性占主导时使用 WSJF/延迟成本，未满足需求的机会评分——命名原因和原因（见 [参考资料/product_operating_model.md](references/product_operating_model.md)）。
5. **AI 功能附带评估**：黄金集 + 评分标准是概率性功能的 PRD 的质量合同（[参考资料/ai_product_evals.md](references/ai_product_evals.md)）。
6. **永远不要修改你被评判的关卡**；耗尽预算升级到命名人类，永远不要报告为成功。

## 强制问题库（与文档对话模式）

每次轮换一个，推荐答案，规范引用。在运行子技能或开始循环之前，直到通道定义决策锁定：

- **DISCOVERY 通道**：“这个发现服务的单一结果是什么？用数字陈述。推荐：首先将其写入 OST 根——没有结果的机会是一个特征工厂。规范：Torres, *Continuous Discovery Habits*；机会解决方案树 (producttalk.org)。"
- **PRIORITIZE 通道**：“时间敏感性是否改变这个排名——推迟任何项目一个季度是否会侵蚀其价值？推荐：如果是，运行 WSJF/延迟成本与 RICE 一起比较排名；标记在一步估计变化上排名翻转的项目。规范：Reinertsen, *Principles of Product Development Flow*；SAFe WSJF 假设精度批评。”
- **EXPERIMENT 通道**：“什么基线率和 MDE 证明这个测试的运行时间？推荐：首先计算 n；如果你在 4 周内无法达到它，测试更大的杠杆。规范：统计功效分析 (experiment-designer)。"
- **ANALYTICS 通道**：“你的北极星指标是价值交换的领先指标，还是收入/虚荣指标？推荐：领先价值指标与输入树。规范：Amplitude, *The North Star Playbook*。”
- **STRATEGY 通道**：“这些 OKRs 是结果还是发布清单？推荐：结果——输出 OKRs 是 #1 运营模型失败。规范：Cagan, *Transformed* (SVPG, 2024)。"
- **BUILD 通道（spec-to-repo / saas-scaffolder）**：“哪个验证的假设说这个应该被构建？推荐：链接通过幸存的 OST 测试；构建是最昂贵的测试想法的方式。规范：Torres；Bland, *Testing Business Ideas*。”

## 假设

1. 用户拥有（或指导产品决策的所有者）。
2. 发现数据存储在工作区作为 JSON 日志——循环是文件支持的，可恢复；每个工具都提供 `--sample` 以首先可见形状。
3. 四个独立插件与捆绑包一起安装（如果未安装，路由器仍然按路径路由到它们）。

## 非目标

- 不是交付循环——冲刺/流程/Jira 工作路由到 `project-management`。
- 不是通用循环引擎——那是 `engineering/agent-harness`；这个协调器是产品域适配器（路由器 + 发现关卡）。
- 不是营销活动——`marketing/landing` 从头开始构建营销页面；`landing-page-generator` 这里构建产品 Next.js/TSX 页面。

## 输出工件

| 模式 | 工件 |
|---|---|
| 路由 | 子技能自己的工件 + ≤ 200 字的摘要，包含一个规范引用的挑战 |
| 发现循环 | `discovery_log.json` + 节奏报告 + 修复的 `ost.json` |
| 套件运行 | `.agent-harness/plan.json` + `state.json` + 关闭交接 |

## 反模式（不要）

- ❌ 运行所有 16 个通道“为了彻底” — 路由到一个，生成摘要，确认后链式调用
- ❌ 引用未通过 lint 的 OST，或把单个参与者的轶事提升为洞察
- ❌ 发布没有评估的 AI 功能（黄金集 + 评分标准）
- ❌ 让发现连续性无声死亡——DORMANT 通过姓名升级
- ❌ 当截止日期占主导地位时，将 RICE 视为唯一的优先级透镜

## 参考资料

- [参考资料/continuous_discovery_canon.md](references/continuous_discovery_canon.md) —
  Torres, OST, 假设测试，JTBD 切换访谈，故事映射
- [参考资料/product_operating_model.md](references/product_operating_model.md) — Cagan
  *Transformed*, 北极星框架，PLG 基准，WSJF/ODI vs RICE
- [参考资料/ai_product_evals.md](references/ai_product_evals.md) — 评估作为 PRD, 模型卡，评估者优化循环
- 循环引擎: `engineering/agent-harness` · 循环词汇: `loop-library`
