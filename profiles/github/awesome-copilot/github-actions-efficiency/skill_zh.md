# GitHub Actions 效率

将此技能用作 GitHub Actions 效率工作的精简入口。检查仓库，识别浪费源，并仅加载当前任务所需的参考材料。

如果尚未存在工作流，请加载 [`references/actions.md`](./references/actions.md) 并在继续以下步骤之前定义基线。

**如果无法访问 shell 或 `gh` 命令行界面：** 请求用户粘贴 `.github/workflows/` 内容和 `gh run list --limit 10` 输出。如果只提供了部分文件，请注明： "基于提供的文件进行审计；某些见解可能不完整。" 从文件开始回答时，请以 "**仅静态分析**（未与实际运行确认）" 开头。"

## 使用此技能的场景

- 用户希望减少 GitHub Actions 运行时间、CI 成本或浪费的工作流运行。
- 仓库在 `.github/workflows/` 中存在现有工作流或明确的 GitHub Actions 配置问题。
- 用户询问缓存、并发、路径过滤器、矩阵缩减、作业优化或特定工作流修复。
- 用户需要帮助从头创建新的 GitHub Actions 工作流或 CI 基线。

## 仅加载所需内容

- [`references/actions.md`](./references/actions.md) — 审计、作业门禁、矩阵缩减、实时验证和特定工作流修复。
- [`references/reporting.md`](./references/reporting.md) — 当用户请求前后效率报告时。
- [`references/patterns.md`](./references/patterns.md) — 当内联审计命令不足以提供完整 YAML 示例时。

## 核心工作流

### 1. 首先测量

```bash
rg -n "on:|concurrency:|paths:|paths-ignore:|strategy:|matrix:|cache:" .github/workflows
gh run list --limit 10
run_id=$(gh run list --limit 1 --json databaseId --jq '.[0].databaseId')
gh run view "$run_id" --log-failed
```

查找：缺少依赖缓存、缺少 `concurrency` 取消、过于宽泛的触发器、重复工作流覆盖以及无论范围如何都在每次更改时运行的高成本作业。

### 2. 应用护栏

在推荐每个修复建议之前，请根据以下规则进行检查：

1. 不会隐藏必要的验证 — 丢弃任何移除发布、模式、迁移或共享库检查的修复。
2. 不会无理由减少并行性 — 除非用户优先考虑成本而非延迟 *且* 新的关键路径保持在原始值的 1.25 倍以内，否则丢弃。
3. 仅保留已记录的矩阵分支 — 丢弃没有明确版本或平台承诺的矩阵分支。
4. 写回作业使用可选触发器 — 标记（不要丢弃）自动运行的格式化器或机器人作业；建议使用可选触发器。
5. 仓库更改与组织设置保持分离 — 将任何混合仓库可编辑 YAML 与组织级或 GitHub 账户设置的修复建议拆分为两个独立的建议。

### 3. 选择前 3 个修复建议

从以下 6 个候选方案中，仅保留那些支持步骤 1 的审计证据 *且* 通过步骤 2 所有护栏的方案。按估计每日 CI 分钟节省量（每次运行节省量 × 每日运行次数）对幸存者进行排序。选择满足两个条件的所有候选方案，最多 3 个。

1. 添加基于锁文件的依赖缓存
2. 添加或修正 `concurrency` 取消
3. 在合并作业之前移除重复工作流覆盖
4. 安全地缩小工作流或作业触发器
5. 将矩阵宽度缩减至与风险和事件类型匹配
6. 在关键路径上并行化独立作业

### 4. 验证

- 如果 `gh` 命令行界面可用，请在非受保护分支上进行实时测试推送，以验证路径门禁和并发取消。
- 如果无法进行实时验证，请在输出中明确说明。
- 即使 YAML 看起来正确，也要将意外的实时行为视为真实错误。

## 必须输出的内容

1. **浪费源** — 步骤 1 中发现的最高成本或延迟驱动因素
2. **建议的修复** — 前 3 个（或所有剩余的）带有支持审计证据
3. **验证** — 已验证的实时内容、仅本地检查的内容以及任何剩余风险
4. **影响** — 预期节省与实际节省；将 PR 墙上时间与总运行者时间分开

## 参考文献

- [`references/actions.md`](./references/actions.md)
- [`references/reporting.md`](./references/reporting.md)
- [`references/patterns.md`](./references/patterns.md)
- [`references/review-rubric.md`](./references/review-rubric.md) — 在审查完成的效率工作时加载
