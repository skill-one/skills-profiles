---
name: code-craft
description: 将 Jess 的工程规范应用于架构、边界类型、错误处理和抽象决策。
---

# 编程技艺

使用仓库当前的说明和既定的规范。在需要设计决策的请求变更中应用这些默认值；它们不授权无关的结构重组或新工具。

阅读范围内的决策参考：

| 决策 | 参考 |
| --- | --- |
| 表示状态和领域身份 | [非法状态](principles/illegal-states.md) |
| 将外部输入解码为有用类型 | [解析，而非验证](principles/parse-dont-validate.md) |
| 建模可恢复的错误和必需的关卡 | [错误作为值](principles/errors-as-values.md) |
| 选择抽象或调查性能 | [简洁性](principles/simplicity.md) |
| 维护模块边界及其文档 | [架构文档](principles/architecture-docs.md) |

仅在语言的习惯用法、并发或工具细节重要时才阅读语言参考：[TypeScript](languages/typescript.md)、[Rust](languages/rust.md)、[Go](languages/go.md) 或 [Python](languages/python.md)。

使用 [testing-craft](../testing-craft/SKILL.md) 进行测试设计决策。仓库设置属于 [project-bootstrap](../project-bootstrap/SKILL.md) 当请求该设置时。遵循项目要求的验证；评审不会自动要求完整的测试套件。

改编自 `leonardomso/rust-skills` (MIT)、Matklad 的 Rust100k 系列，以及 Alexis King 关于解析和类型安全的写作。
