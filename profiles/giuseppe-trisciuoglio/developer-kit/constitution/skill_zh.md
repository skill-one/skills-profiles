## 概述

Constitution 技能通过两个共享文档管理项目的架构 DNA：

| 文件 | 目的 |
|------|------|
| `docs/specs/architecture.md` | 技术栈、基础设施、架构规则、安全约束、AI 边界 |
| `docs/specs/ontology.md` | 领域词汇表（通用语言）— 术语、定义、边界上下文 |

这些文件位于 `docs/specs/` 目录下，并在所有规范中共享。与一个整体的 `constitution.md` 不同，这些文件由 `brainstorm`（阶段 6.8.6）和 `spec-to-tasks`（阶段 1.5）创建/丰富。

## 指令

1. 从 `$ARGUMENTS` 或用户意图中识别操作：`create`、`update`、`check` 或 `show`。
2. 对于 **create**：询问要创建哪些文件（architecture.md、ontology.md 或两者），通过 `AskUserQuestion` 收集所需信息，然后使用以下模板编写文件。
3. 对于 **update**：识别目标文件和章节，进行手术式修改，更新 `Last Updated` 日期。
4. 对于 **check**：读取两个 constitution 文件，读取目标文件，根据架构规则和领域词汇表进行验证，输出 Constitution 检查报告。
5. 对于 **show**：读取并显示两个格式化的文件以增强可读性。
6. 在编写或覆盖文件之前，始终与用户确认。

## 示例

```bash
# 在第一次 brainstorm 之前创建 constitution
/developer-kit-specs:constitution create

# 验证规范是否符合架构和领域词汇表
/developer-kit-specs:constitution check --target=docs/specs/001/2024-01-15--user-auth.md

# 更新安全约束章节
/developer-kit-specs:constitution update --file=architecture --section=security

# 显示当前的 constitution
/developer-kit-specs:constitution show
```

## 何时使用

| 场景 | 操作 |
|------|------|
| 新项目 — 在第一次 brainstorm 之前定义技术栈和领域语言 | `create` |
| 技术栈或安全规则变更 | `update` |
| 验证规范、任务或文件是否符合架构和领域词汇表 | `check` |
| 审查当前的架构和领域词汇表 | `show` |

**触发短语：**
- "创建 constitution"、"设置项目架构"、"定义领域词汇表"
- "更新 constitution"、"更新架构"、"更新领域词汇表"
- "Constitution 检查"、"根据 constitution 进行验证"
- "显示 constitution"、"项目原则"、"架构边界"

## 操作

### create
1. 询问要创建哪些文件："Both"（推荐）、"architecture.md 仅"、"ontology.md 仅"
2. 检查文件是否存在 → 询问是否覆盖或跳过
3. 对于 **architecture.md**：通过 `AskUserQuestion` 收集（领域、基础设施、技术栈、数据、风格、规则）
4. 对于 **ontology.md**：询问术语或创建空框架
5. 在编写每个文件之前确认

模板查找顺序：
- 主要：`${CLAUDE_PLUGIN_ROOT}/templates/architecture.md`
- 备用：`skills/constitution/references/architecture.md`

### update
1. 解析 `--file=architecture|ontology` 和 `--section=<name>`
2. 读取目标文件，进行手术式修改
3. 更新 `Last Updated` 日期
4. 编写文件

### check
1. 读取两个 constitution 文件
2. 读取目标文件 (`--target=<path>`)
3. 根据架构规则、安全约束和领域词汇表进行验证
4. 输出 **Constitution 检查报告**

### show
1. 读取 `docs/specs/architecture.md` 和 `docs/specs/ontology.md`
2. 格式化显示以增强可读性

## 防止上下文退化

Constitution 通过基于文件的存储防止上下文退化：

- **会话开始时读取**：`docs/specs/architecture.md` 和 `docs/specs/ontology.md`
- **永远不要假设上下文**：在实现之前必须从文件中读取
- **验证工作**：与 constitution 对比，而不是内存

有关详细场景和恢复协议，请参阅 `references/context-rot-prevention.md`。

## 约束和警告

- **不修改源代码** — 仅创建/更新 constitution 文件
- **关键违规必须解决** — 警告是建议性的
- **每个项目一个 architecture.md 和一个 ontology.md** — 在所有规范中共享
- **每次变更更新 `Last Updated` 日期**
- **使用 ADRs** 进行重要的架构决策
- **上下文退化风险**：文件超过 30 天可能已偏离

## 最佳实践

- **在 brainstorm 之前创建**：早期建立 constitution 可确保一致性
- **库验证**：在使用任何外部库之前，验证其是否在架构的库验证部分
- **规范死亡原则**：将完成的规范存档到 `archived/` — 永远不要让规范变得陈旧
- **领域词汇表丰富**：由 `brainstorm`（阶段 6.8.6）和 `spec-to-tasks`（阶段 1.5）更新
- **报告格式**：安全章节优先，然后是 CWE 合规性、架构、库验证、领域词汇表

## Constitution 检查报告格式

```
## Constitution 检查报告
目标：<文件路径>
日期：YYYY-MM-DD

### 安全检查 (CWE/OWASP 合规性)
| 规则 | 级别 | 状态 | 位置 | CWE/OWASP |
|------|------|------|------|----------|
| 无 SQL 注入 | 关键 | ✅ OK | - | CWE-89 |

### CWE 合规性报告
| CWE | OWASP | 状态 | 位置 |
|-----|-------|------|------|
| CWE-89 | A03 | ✅ OK | - |

### 架构检查
| 规则 | 状态 | 详情 |
|------|------|------|
| 构造函数注入 | ✅ OK | - |

### 库验证检查
| 库 | 状态 | 详情 |
|----|------|------|
| bcrypt | ✅ OK | 使用 hash(password, 12) |

### 领域词汇表检查
| 术语 | 状态 | 详情 |
|------|------|------|
| "User" 一致使用 | ✅ OK | - |

### 摘要
- 关键违规：0
- 警告违规：0
- 合规规则：N
```

有关详细安全模式（CWE/OWASP 映射），请参阅 `references/security-patterns.md`。

## 与 SDD 工作流集成

```
[会话开始] → 读取 Constitution 文件
        ↓
[可选] constitution create        ← 此技能（brainstorm 前设置）
        ↓
brainstorm                            ← brainstorm 之前加载 Constitution
        ↓
spec-to-tasks                         ← Constitution 验证规范
        ↓
task-implementation                   ← Constitution 边界有效
        ↓
task-review                           ← Constitution 检查验证
        ↓
[会话结束] → Constitution 文件如有必要则更新
```

需要加载之前：
- `specs.brainstorm` — 验证需求与架构一致
- `specs.spec-to-tasks` — 检查技术栈兼容性
- `specs.task-implementation` — 应用 AI 边界
- `specs.task-review` — Constitution 检查

## 参考文件

| 文件 | 目的 |
|------|------|
| `references/architecture.md` | 完整架构模板 |
| `references/ontology.md` | 完整领域词汇表模板 |
| `references/security-patterns.md` | CWE/OWASP 模式、验证格式 |
| `references/context-rot-prevention.md` | 详细场景和恢复协议 |
| `references/constitution-check-report.md` | 完整报告示例 |

有关完整模板和详细参考材料，请参阅 `references/` 目录。
