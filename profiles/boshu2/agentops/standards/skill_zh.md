# 标准 — 聚焦于工程指导

加载调用者文件、语言和风险所证明的最小标准集。不要预加载整个参考语料库。

## 提示

```text
检查 fleet-router PR #214 中更改的文件 cli/internal/auth/token.go 和 cli/internal/auth/token_test.go 的标准：Go，一个安全敏感的更改。仅加载匹配的参考，并报告引用的发现，包括路径和行号，以及检查和未检查的范围。
```

## 如果它有效

- 报告加载 `common-standards.md` 加上仅匹配的 Go 参考，永远不会加载完整的参考语料库。
- 每个发现都引用路径和行号，例如 `cli/internal/auth/token.go:18`。
- 响应明确披露 `checked` 和 `not_checked` 范围，即使 `not_checked` 为空。
- `git diff --stat` 显示没有测试、门禁或固定文件更改；标准报告仅发现。

## 程序

1. 记录提供的路径、语言、更改类型和风险提示。
2. 加载 `common-standards.md` 加上仅匹配的语言或清单参考。
3. 将提供的工件与这些来源进行比较。
4. 在可能的情况下，返回引用的发现，包括路径和行号，以及检查和未检查的范围。
5. 停止。

这项技能提供上下文和发现。它不会编辑、验证、重试、批准、提交、发布、交付或决定继续。

## 生成的代码的承重约定（MEASURED）

当调用者即将编写代码（而不仅仅是审查它）时，在工作上下文中以内联方式显示匹配的语言规则——链接后的参考不会改变行为；内联命令会。Go 核心：

- 用上下文包装每个传播的错误：`fmt.Errorf("执行 X: %w", err)` — 永远不要返回裸的内部错误。
- 多例函数获得表驱动测试（`[]struct` 用例 + 每个用例的 `t.Run`），断言精确的预期值，包括错误用例。

对于其他语言，拉取匹配的参考并在下方内联其顶部规则。

> 测量 2026-08-04，探测 `standards-go-conventions` (gpt-5.6-luna, N=2, 方向性)：控制生成的 `%w`-包装 + 表驱动形状在 1/2 运行中；使用这些规则内联，2/2。内联命令优于参考链接——图化探测测量了链接文档指令遵守 0/2。账本：`evals/skill-probes/LEDGER.md`。

## 变异安全性标准

当提供的更改批量重写现有文件时——格式化器、代码修改、迁移脚本、指向手写源的生成器——检查它针对三个标准，并在缺失时报告每个为发现：

- **单一审计变异瓶颈。** 所有重写都通过一个命名的命令或脚本，其输入、输出和干运行模式可以检查。跨 ad-hoc 单行和手动修改的编辑是 **分散变异** 失败模式：没有单个点可以审计、重跑或归咎。发现：命名瓶颈之外的每个变异路径。
- **哈希见证的更改前备份。** 在瓶颈运行之前，原始文件被保留，并记录内容哈希（提交的基线计算），以便“重写仅更改了它声称更改的内容”是可检查的字节对字节，而不是断言。发现：没有可验证的前状态的大批量重写。
- **自我管理的野心门禁。** 更改声明它故意不触及的内容，并且差异尊重它。运行时也重命名的格式化器，运行时也重构的代码修改是 **范围蔓延重写** 失败模式。发现：差异中更改自身声明范围之外的任何文件类别。

此检查的停止条件：三个标准都有明确的通过或发现；报告风格小问题但跳过这些的大批量重写审查是不完整的。

## 参考

- [通用标准](references/common-standards.md)
- [Go](references/go.md)
- [Python](references/python.md)
- [Rust](references/rust.md)
- [TypeScript](references/typescript.md)
- [JavaScript](references/javascript.md)
- [Shell](references/shell.md)
- [JSON](references/json.md)
- [YAML](references/yaml.md)
- [Markdown](references/markdown.md)
- [SQL 安全性](references/sql-safety-checklist.md)
- [竞态条件](references/race-condition-checklist.md)
- [LLM 信任边界](references/llm-trust-boundary-checklist.md)
- [技能结构](references/skill-structure.md)
- [测试策略](references/test-pyramid.md)
