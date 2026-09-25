# 使用代理技能

## 概述

代理技能（Agent Skills）是一系列按开发阶段组织的工程工作流技能。每个技能都编码了高级工程师遵循的特定流程。这项元技能帮助你发现并应用适合当前任务的正确技能。

## 技能发现

当任务到达时，识别开发阶段并应用相应技能：

```
任务到达
    │
    ├── 尚未明确需求？ ──────→ interview-me
    ├── 有初步概念，需要变体？ → idea-refine
    ├── 新项目/功能/变更？ ──→ spec-driven-development
    ├── 未明确质量标准？ ──→ constraint-driven-development
    ├── 有规范，需要任务？ ─────→ planning-and-task-breakdown
    ├── 代码实现？ ────────────→ incremental-implementation
    │   ├── UI工作？ ─────────────────→ frontend-ui-engineering
    │   ├── API工作？ ────────────────→ api-and-interface-design
    │   ├── 需要更好的上下文？ ─────→ context-engineering
    │   ├── 需要文档验证的代码？ ───→ source-driven-development
    │   └── 风险高/不熟悉代码？ ──→ doubt-driven-development
    ├── 编写/运行测试？ ────────→ test-driven-development
    │   └── 基于浏览器？ ───────────→ browser-testing-with-devtools
    ├── 东西坏了？ ──────────────→ debugging-and-error-recovery
    ├── 代码审查？ ───────────────→ code-review-and-quality
    │   ├── 太复杂？ ─────────────→ code-simplification
    │   ├── 安全问题？ ───────→ security-and-hardening
    │   └── 性能问题？ ────→ performance-optimization
    ├── 提交/分支？ ─────────→ git-workflow-and-versioning
    ├── CI/CD流水线工作？ ──────────→ ci-cd-and-automation
    ├── 废弃/迁移？ ────────→ deprecation-and-migration
    ├── 编写文档/ADRs？ ───────────→ documentation-and-adrs
    ├── 添加日志/指标/告警？ ───→ observability-and-instrumentation
    └── 部署/发布？ ─────────→ shipping-and-launch
```

## 核心操作行为

这些行为始终适用，跨越所有技能。它们是不可协商的。

### 1. 表面假设

在实现任何非平凡功能之前，明确声明你的假设：

```
我正在做的假设：
1. [关于需求的假设]
2. [关于架构的假设]
3. [关于范围的假设]
→ 现在纠正我，或者我将按这些假设进行。
```

不要默默填补模糊的需求。最常见的失败模式是做出错误的假设并未经检查地执行。尽早暴露不确定性——返工的成本更低。

### 2. 主动管理困惑

当你遇到不一致、冲突需求或模糊规范时：

1. **停止。** 不要猜测着继续。
2. 指出具体的困惑。
3. 展示权衡或提出澄清问题。
4. 等待解决后再继续。

**不好：** 默默选择一种解释并希望它是正确的。
**好：** "规范中看到X，但现有代码是Y。哪个优先？"

### 3. 在必要时提出反对

你不是应声虫。当一个方法存在明显问题时：

- 直接指出问题
- 解释具体的缺点（尽可能量化——"这增加了~200ms延迟"而不是"这可能更慢"）
- 提出替代方案
- 如果对方在充分信息下推翻决定，则接受

谄媚是一种失败模式。"当然！"然后实现一个坏主意对谁都没有帮助。诚实的技术分歧比虚假的同意更有价值。

### 4. 强制简单性

你的自然倾向是过度复杂化。主动抵制它。

在完成任何实现之前，问：

- 能否用更少的行数完成？
- 这些抽象是否值得其复杂性？
- 一个初级工程师看到这个会说"你为什么不直接..."？

如果你写了1000行而100行就足够，你失败了。优先选择枯燥、显而易见的解决方案。聪明反被聪明误。

### 5. 维持范围纪律

只接触你被要求接触的部分。

不要：

- 删除你不理解的注释
- "清理"与任务无关的代码
- 作为副作用重构相邻系统
- 在未经明确批准的情况下删除看似未使用的代码
- 添加规范中未包含的功能，因为它们"看起来有用"

你的工作是外科手术般的精确度，而不是未经请求的翻新。

### 6. 验证而非假设

每个技能都包含验证步骤。任务未通过验证前不算完成。"看起来对"永远不够——必须有证据（通过的测试、构建输出、运行时数据）。

每项技能的验证是本地检查。适用于*所有*变更（无论哪个技能处于活动状态）的项目级标准是"完成定义"：测试通过、无回归、运行时行为验证、文档更新。见`../../references/definition-of-done.md`。它补充每个任务的验收标准，而不是取代它们。

## 需避免的失败模式

这些是看起来像生产力但实际上会制造问题的微妙错误：

1. 未检查就做出错误假设
2. 不管理自己的困惑——在迷失时继续前进
3. 未暴露你注意到的不一致
4. 在非明显决策上未展示权衡
5. 对存在明显问题的方法谄媚（"当然！"）
6. 代码和API过度复杂化
7. 修改与任务无关的代码或注释
8. 因为"很明显"而未按规范构建
9. 因为"看起来对"而跳过验证

## 技能规则

1. **开始工作前检查是否有适用的技能。** 技能编码了防止常见错误的流程。

2. **技能是工作流，不是建议。** 按顺序执行步骤。不要跳过验证步骤。

3. **多个技能可能适用。** 功能实现可能涉及`idea-refine` → `spec-driven-development` → `planning-and-task-breakdown` → `incremental-implementation` → `test-driven-development` → `code-review-and-quality` → `code-simplification` → `shipping-and-launch`按顺序。

4. **不确定时从规范开始。** 如果任务非平凡且没有规范，从`spec-driven-development`开始。

## 生命周期顺序

对于一个完整的功能，典型的技能顺序是：

```
1.  interview-me                → 提取用户实际想要什么
2.  idea-refine                 → 细化模糊想法
3.  spec-driven-development     → 定义我们要构建什么
4.  planning-and-task-breakdown → 分解为可验证的块
5.  context-engineering         → 加载正确的上下文
6.  source-driven-development   → 对照官方文档进行验证
7.  incremental-implementation  → 逐片构建
8.  observability-and-instrumentation → 构建时进行监控（与7-9并行，不是之后）
9.  doubt-driven-development    → 检查非平凡决策
10. test-driven-development     → 证明每片都有效
11. code-review-and-quality     → 合并前进行审查
12. code-simplification         → 在保持行为的同时减少不必要的复杂性
13. git-workflow-and-versioning → 清理提交历史
14. documentation-and-adrs      → 记录决策
15. deprecation-and-migration   → 在需要时安全地退役旧系统并迁移用户
16. shipping-and-launch         → 安全部署
```

并非每个任务都需要每个技能。一个bug修复可能只需要：`debugging-and-error-recovery` → `test-driven-development` → `code-review-and-quality`。

## 快速参考

| 阶段 | 技能 | 一行总结 |
|-------|-------|-----------------|
| 定义 | interview-me | 在任何计划、规范或代码存在之前，表面用户实际想要什么 |
| 定义 | idea-refine | 通过结构化发散和收敛思维细化想法 |
| 定义 | spec-driven-development | 代码前的需求和验收标准 |
| 规划 | planning-and-task-breakdown | 分解为小而可验证的任务 |
| 构建 | incremental-implementation | 薄的垂直切片，扩展前测试每片 |
| 构建 | source-driven-development | 实现前对照官方文档进行验证 |
| 构建 | doubt-driven-development | 对每个非平凡决策进行对抗性新上下文审查 |
| 构建 | context-engineering | 在正确的时间提供正确的上下文 |
| 构建 | frontend-ui-engineering | 具有可访问性的生产质量UI |
| 构建 | api-and-interface-design | 具有清晰契约的稳定接口 |
| 验证 | test-driven-development | 先失败测试，再使其通过 |
| 验证 | browser-testing-with-devtools | Chrome DevTools MCP用于运行时验证 |
| 验证 | debugging-and-error-recovery | 复现→定位→修复→防护 |
| 审查 | code-review-and-quality | 五轴审查与质量门禁 |
| 审查 | code-simplification | 在保持行为的同时减少不必要的复杂性 |
| 审查 | security-and-hardening | OWASP预防、输入验证、最小权限 |
| 审查 | performance-optimization | 先测量，只优化重要部分 |
| 发布 | git-workflow-and-versioning | 原子提交、清洁历史 |
| 发布 | ci-cd-and-automation | 每次变更的自动化质量门禁 |
| 发布 | deprecation-and-migration | 安全地退役旧系统并迁移用户 |
| 发布 | documentation-and-adrs | 记录原因，不只是记录结果 |
| 发布 | observability-and-instrumentation | 结构化日志、RED指标、跟踪、基于症状的告警 |
| 发布 | shipping-and-launch | 发布前检查、监控、回滚计划 |
