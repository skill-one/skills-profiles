# Autoresearch — 自主目标导向迭代

## 安全不变量（所有子命令）
- 未经明确用户批准，不得推送、发布或部署。
- 默认有界。使用 `Iterations: unlimited` 覆盖。
- 所有结果记录到 `autoresearch/{subcommand}-{YYMMDD}-{HHMM}/` 目录。
- 通过 `handoff.json` 进行链式交接。评估读取 `*-results.tsv`。

## 分发（裸 `$autoresearch`）

按以下顺序解析调用：

| 条件 | 模式 |
|---|---|
| 存在 `Metric:` 或 `Verify:` | **经典** — 现有指标循环，不变 |
| 自由形式的自然语言目标，无指标/验证 | **编排器** — 见编排器部分 |
| 什么都没有 | **设置向导** — 交互式配置构建器 |
| `--classic` 标志 | 无论目标文本如何，强制经典模式 |
| `--auto` 标志 | 无论目标文本如何，强制编排器模式 |

每次调用时打印横幅：`[autoresearch] 模式：经典 | 编排器 | 向导`。

## 子命令

| 命令 | 功能 | 默认迭代次数 |
|---|---|---|
| `$autoresearch` | 针对指标迭代：修改 → 验证 → 保留/丢弃 | 25 |
| `$autoresearch plan` | 将目标转换为验证的 Scope、Metric、Verify 配置 | N/A |
| `$autoresearch debug` | 查找错误：假设 → 测试 → 证伪 → 重复 | 15 |
| `$autoresearch fix` | 逐一击破错误，直到全部消失 | 20 |
| `$autoresearch security` | STRIDE + OWASP 审计，配合红队角色 | 15 |
| `$autoresearch ship` | 通过 8 个阶段：清单 → 模拟运行 → 部署 → 验证 | N/A |
| `$autoresearch scenario` | 生成跨越 12 个维度的边界情况 | 20 |
| `$autoresearch predict` | 5 个专家角色在实施前进行辩论 | N/A |
| `$autoresearch learn` | 探索代码库 → 生成文档或维基 → 验证 → 修复循环 | 10 |
| `$autoresearch reason` | 与盲判员进行对抗辩论，直到收敛 | 8 |
| `$autoresearch probe` | 8 个角色询问需求，直到饱和 | 15 |
| `$autoresearch improve` | 研究 ICP 挑战，发现改进，生成 PRDs | 15 |
| `$autoresearch evals` | 分析迭代结果：趋势、平台期、回归 | N/A |
| `$autoresearch regression` | 回归稳定性门禁：基线与候选对比，判定 STABLE/UNSTABLE | N/A |

## 通用标志

| 标志 | 适用范围 | 目的 |
|---|---|---|
| `Iterations: N` | 所有循环 | 设置迭代次数 |
| `Iterations: unlimited` | 所有循环 | 选择无界模式 |
| `--evals` | 所有循环 | 循环中途检查点 + 最终总结 |
| `--evals-interval N` | 所有循环 | 覆盖检查点频率 |
| `--chain <targets>` | 所有 | 完成后顺序交接 |
| `--<subcommand>` | 所有 | `--chain <subcommand>` 的简写 |
| `--dry-run` | 编排器 | 打印推导的配置 + 计划的管道；不执行 |
| `--max-cycles N` | 编排器 | 编排周期的硬上限（默认 50） |
| `--classic` | 裸 `$autoresearch` | 强制经典指标循环模式 |
| `--auto` | 裸 `$autoresearch` | 强制编排器模式 |

## 编排器

当给出纯语言目标且无 `Metric:`/`Verify:` 时激活。将目标分类为 **目标原型** — 见 `references/orchestrator-routing.md` 的原型表和路由决策表。

相对于此安装技能目录解析所有 `scripts/...` 路径，永不相对于调用者的工作目录解析。

**基于原型的两种模式：**
- **编排循环** — 带谓词的原型（ship-ready、optimize-metric、fix-broken、harden、build-feature、explore）。目标具有机械成功谓词；循环运行直到谓词满足。
- **单次分发** — 主观/终端原型（document、what-to-build、decide-design）。路由一次到合适的子命令（learn / improve / reason），让其自终止，然后报告。无循环、无平台、无 ship 门禁。

### 编排循环步骤

由 `scripts/orchestrate.sh` 支持（确定性接口 — 所有路由逻辑都在那里）。暴露的子命令：`classify`、`next-hop`、`units`、`plateau`、`screen-cmd`、`verdict`、`validate-state`、`screen-state-predicate`。

1. **分类** — `scripts/orchestrate.sh classify "<goal>"` → 原型标签 + 模式。
2. **推导谓词** — 重用 `plan` 逻辑生成具体的成功谓词：确切的 shell 命令 + 预期输出。对于 `optimize-metric`，内部运行完整的 plan/wizard 推导。
3. **确认** — 一个 `request_user_input` 显示：原型、模式、具体谓词（命令 + 预期输出）、终端选择（stop-at-verified vs proceed-to-ship）。错误分类在此处捕获，而非运行中途。
4. **Round-0 干预运行** — 证明谓词命令运行并返回值；通过 `screen-cmd` 每个推导的命令进行安全检查；打印预期的周期预算。如果 `--dry-run` 则在此处停止。
5. **循环直到谓词满足**：
   a. 通过廉价信号（最后的 `handoff.json`、回归判定、错误计数）+ 影响测试验证评估状态。
   b. `scripts/orchestrate.sh next-hop orchestrator-state.json` → 下一个子命令。
   c. 运行子命令（其自身的有界内部循环）。
   d. 记录每个跳转的结果 ∈ {progressed、no-op、failed、blocked}。
   e. 将跳转的 `handoff.json` 折叠到 `orchestrator-state.json`。
   f. `scripts/orchestrate.sh units` → 重新计算 **剩余单元**。
6. **停止条件**（每次跳转后检查）：
   - 谓词满足 → ship 门禁（仅当 ship 在管道中）否则 `CONVERGED`。
   - `scripts/orchestrate.sh plateau orchestrator-state.json` → true → 停止 + 报告 `PLATEAU`。
   - 周期 > 上限（默认 50，覆盖 `--max-cycles N`）→ 停止 + 报告 `CEILING`。
   - 跳转结果 `blocked`/`failed` 且无替代路线 → 检查点 + 停止 + 报告 `BLOCKED`。

### 编排器状态

`orchestrator-state.json` — 编排器所有，可加性。跟踪：目标、原型、谓词、终端选择、`units_remaining` 历史记录、周期计数、每个跳转的管道日志与结果、当前占位者。每个跳转的 `handoff.json` 保持不变（单跳桥接）；编排器读取并折叠它。两个明确拥有的状态对象，无重叠。

### 编排器安全不变量

- **永不自动批准 ship/deploy/push。** 编排器从不将 `--auto` 传递给 `ship`；部署始终需要明确用户批准。
- **锚定 DB-URL 允许列表后的数据迁移。** 重用回归的允许列表 — 主机必须是 `localhost`/`127.0.0.1`/容器主机名，或数据库名包含 `_test`/`_ci` 后缀。纯子串匹配不符合条件。任何其他情况都将被拒绝。
- **对每个推导的命令执行 `screen-cmd`** — 在循环开始前 AND 在恢复时从持久化状态文件读取的命令前运行。持久化命令永不被信任；恢复通过 `screen-state-predicate` 重新检查固定的谓词并拒绝 `refuse`。
- **循环中途无未筛选的命令。** 自主循环不能引入绕过 `screen-cmd` 的新 shell 命令。
- **谓词固定，不重新推导。** Round-0 将推导的成功谓词原封不动地写入 `orchestrator-state.json`；每个周期和每次恢复都重用该确切字符串，以便跨运行重现“完成”。
- **在路由前验证账本。** `validate-state` 门禁 `orchestrator-state.json`（必需字段 + 粗糙类型）；一个格式错误的账本不被信任进行路由。
- **收敛前独立验证。** 高影响变更在 `pending_verify` 工作信号集上接受；`next-hop` 路由到 `verify` 跳转（保留/对抗检查）在 `DONE` 或 ship 之前。验证跳转永不自动批准 ship。
- **未知单元周期不计入平台计数器。** 一个 `units` 返回 `unknown`（例如运行者崩溃）的周期不被计为零进度；重复的 `unknown` 路由到 `BLOCKED`。
