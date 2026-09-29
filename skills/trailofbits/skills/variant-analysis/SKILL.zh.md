---
name: variant-analysis
description: 寻找已发现的其他实例——即代码库中一个根本原因的变体。在特定文件中发现漏洞、逻辑错误或不良模式后立即使用，问题变成它还出现在其他地方，包括口语形式（“还有其他类似的吗？”、“这是同一个错误吗？”）。也用于将一个已知实例推广到 CodeQL 或 Semgrep 查询，以查找其整个模式家族，以及将一组看似相似的候选方案与已知根本原因进行分类。不适用于在没有具体错误的情况下进行初始发现。
---

# 变异分析

查找你已经发现的其他相同漏洞的实例。一个根本原因通常有多个表现，并且它们很少出现在你发现第一个漏洞的模块中。

## 使用场景

- 已发现漏洞，需要搜索类似实例
- 构建或完善用于安全模式的 CodeQL/Semgrep 查询
- 在初步问题发现后进行系统代码审计
- 分析单个根本原因在不同代码路径中的表现方式

## 不适用场景

- 初步漏洞发现 — 使用 audit-context-building 或特定领域的审计
- 没有已知搜索模式的代码审查
- 编写修复建议 — 使用 issue-writer
- 理解不熟悉的代码 — 首先使用 audit-context-building

## 五个步骤

当你到达某个步骤时，请阅读该步骤的参考。

**1. 理解原始问题。** 提取根本原因 — 代码错误的原因，而不是它做什么 — 并列举变异可能隐藏的方向：相关标识符、相同错误的其它表现、数据类型的边缘情况。
→ [references/root-cause.md](references/root-cause.md)

**2. 创建精确匹配。** 编写仅匹配已知实例的模式，并确认其有效。一个匹配不到任何内容的模式意味着你误解了漏洞，基于它的所有搜索都是针对错误代码的校准。

**3–4. 逐个元素泛化。** 从精确匹配开始，逐步向模式家族扩展，每次更改后运行并阅读所有匹配结果。当超过一半的匹配结果是噪音时停止。
→ [references/searching.md](references/searching.md) — 抽象阶梯、工具选择、误报过滤器

**5. 优先级排序。** 判断哪些候选者是真实的，并附上严重性说明。
→ [references/triage.md](references/triage.md)

**然后编写报告**，包括失败的模式和一个防止回归的 CI 规则。
→ [references/reporting.md](references/reporting.md)

## 作为工作流运行

该插件提供 `/variant-analysis:variants`，它跨并行子代理运行五个步骤 — 每个扩展轴一个，循环直到扫描不再发现新内容。每个阶段读取与其任务匹配的上方参考。

当代码库较大或根本原因有多个表现时使用工作流。当搜索范围较窄或你想控制每个泛化时直接操作步骤。

## 导致搜索失败的原因

1. **范围过窄** — 仅搜索原始漏洞所在的模块
2. **模式过于具体** — 仅搜索一个属性而忽略其周围的家族
3. **单一漏洞类别** — 追踪根本原因的单一表现
4. **正常路径测试** — 从不尝试空值、空字符串和边界情况
5. **泛化过快** — 同时抽象多个元素，导致噪音无法归因于任何一个

前三个在 root-cause.md 和 searching.md 中涵盖，第四个在 triage.md 中涵盖。

## 资源

**CodeQL** (`resources/codeql/`): `python.ql`, `javascript.ql`, `java.ql`, `go.ql`, `cpp.ql`

**Semgrep** (`resources/semgrep/`): `python.yaml`, `javascript.yaml`, `java.yaml`, `go.yaml`, `cpp.yaml`

**报告**: `resources/variant-report-template.md`
