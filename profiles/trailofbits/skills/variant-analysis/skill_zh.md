# 变异分析

查找你已经发现的其他相同漏洞的实例。一个根本原因通常有多个表现形式，并且它们很少出现在你发现第一个漏洞的模块中。

## 使用场景

- 已发现漏洞，需要查找相似实例
- 构建或完善用于安全模式的 CodeQL/Semgrep 查询
- 在初步问题发现后进行系统代码审计
- 分析单个根本原因在不同代码路径中的表现形式

## 不适用场景

- 初步漏洞发现 — 使用 audit-context-building 或特定领域的审计
- 没有已知模式可搜索的常规代码审查
- 编写修复建议 — 使用 issue-writer
- 理解不熟悉的代码 — 首先使用 audit-context-building

## 五个步骤

当你到达某个步骤时，请阅读该步骤的参考文档。

**1. 理解原始问题。** 提取根本原因 — 代码为何错误，而不是它做什么 — 并列举变异可能隐藏的方向：相关标识符、相同错误的其它表现形式、数据类型的边界情况。
→ [references/root-cause.md](references/root-cause.md)

**2. 创建精确匹配。** 编写仅匹配已知实例的模式，并确认其有效。一个匹配不到任何内容的模式意味着你误解了漏洞，基于它的所有搜索都是针对错误代码的。

**3–4. 逐个元素泛化。** 从精确匹配开始，逐步向模式家族扩展，每次更改后运行并阅读所有匹配结果。当超过一半的匹配结果是噪音时停止。
→ [references/searching.md](references/searching.md) — 抽象阶梯、工具选择、误报过滤器

**5. 优先级排序。** 判断哪些候选者是真实的，并附上严重性等级。
→ [references/triage.md](references/triage.md)

**然后编写报告**，包括失败的模式和用于防止回归的 CI 规则。
→ [references/reporting.md](references/reporting.md)

## 作为工作流运行

该插件提供 `/variant-analysis:variants`，它会在并行子代理上运行五个步骤 — 每个扩展轴一个，循环直到扫描不再发现新内容。每个阶段会读取与其任务匹配的上方参考。

当代码库较大或根本原因有多个表现形式时使用工作流。当搜索范围较窄或你想控制每个泛化步骤时直接操作步骤。

## 导致搜索失败的原因

1. **范围过窄** — 仅搜索原始漏洞所在的模块
2. **模式过于具体** — 仅搜索一个属性而忽略了其周围的家族
3. **单一漏洞类别** — 追踪根本原因的单一表现形式
4. **常规路径测试** — 从不尝试空值、空字符串和边界情况
5. **泛化过快** — 同时抽象多个元素，导致噪音无法归因于任何一个

前三个在 root-cause.md 和 searching.md 中涵盖，第四个在 triage.md 中涵盖。

## 资源

**CodeQL** (`resources/codeql/`): `python.ql`, `javascript.ql`, `java.ql`, `go.ql`, `cpp.ql`

**Semgrep** (`resources/semgrep/`): `python.yaml`, `javascript.yaml`, `java.yaml`, `go.yaml`, `cpp.yaml`

**报告**: `resources/variant-report-template.md`
