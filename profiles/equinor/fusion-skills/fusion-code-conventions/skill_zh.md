# 代码规范

## 使用场景

当代码需要评审、编写或解释以符合项目规范时使用。适用于两个层面：

- **语言规范** — 命名、文件命名、类型系统、TSDoc/XML 文档标准、代码结构、错误处理、异步模式、死代码策略。每种语言都有专门的代理和权威参考文档。
- **跨领域规范** — 应用于每次评审：意图捕获（每个非显而易见的决策都必须足够详细地记录，以便代码仅从注释中即可再生）和宪法执行（ADRs 和贡献者文档是法律；偏离需要新的决策记录；过时的决策被标记）。

典型触发器：
- "这个项目的命名规范是什么？"
- "我应该为这个函数编写 TSDoc 吗？"
- "这个文件是否符合我们的代码风格？"
- "评审这个以查找规范违规"
- "我应该在这里使用哪种注释风格？"
- "这是否是 TypeScript / React / C# / Markdown 的惯用法？"
- "将代码规范应用于这个文件"
- "这些内联注释足够好吗？"
- "这违反了任何 ADR 吗？"
- "这个 ADR 是否仍然有效？"
- "我们有 CONTRIBUTING.md — 检查这个更改是否遵循它"

## 不使用场景

- 安全漏洞扫描（使用专门的安全评审技能）
- 性能分析或基准测试
- 高级架构或系统设计决策
- 没有评审目标的全新代码生成
- 没有明确用户确认的文件修改

## 优先级和应用范围

此技能提供 **组织级基础规范**。当安装在具有自身规范的环境中时，优先级（最高者胜出）：

1. **仓库级策略** — `CONTRIBUTING.md`、贡献者指南（`contribute/`）、ADRs、`.github/copilot-instructions.md`、`AGENTS.md` 或等效文件
2. **工具配置** — `biome.json`、`tsconfig.json`、`.editorconfig`、代码检查器配置文件
3. **此技能** — `references/*.conventions.md` 中的所有规则和代理模式

当仓库明确缩小、放宽或与该技能的规则相矛盾时，仓库策略优先。不要标记符合仓库文档规范的代码，即使它偏离了技能基准。

如果冲突未记录（没有 ADR、没有贡献者备注、没有配置），则将技能规则视为默认值，并建议团队记录他们的意图。

> **对于维护者：** 在 `CONTRIBUTING.md`、贡献者指南或 ADR 中记录规范覆盖，以便人类和代理都能一致地发现它们。

## 代理模式

| 代理 | 激活条件 |
|---|---|
| `agents/typescript.agent.md` | TypeScript 命名、TSDoc、类型系统、代码风格、错误处理 |
| `agents/react.agent.md` | React 组件结构、钩子规则、可访问性、键 |
| `agents/csharp.agent.md` | C# 命名、CQRS 模式、异步/等待、空安全、测试 |
| `agents/markdown.agent.md` | Markdown 结构、frontmatter、链接、引用、GitHub 特定语法 |
| `agents/intent.agent.md` | 意图捕获 — 每次代码评审时并行应用 |
| `agents/constitution.agent.md` | ADR 和贡献者文档执行 — 当项目有决策记录时并行应用 |

规范参考（每种语言的权威规则）：
- `references/typescript.conventions.md`
- `references/react.conventions.md`
- `references/csharp.conventions.md`
- `references/markdown.conventions.md`

## 必须输入

如果必须输入缺失或模糊，请在继续之前询问。

- 目标代码（内联片段或文件路径）或特定的规范问题
- 语言或文件类型（如果未提供，则从内容中推断）
- 对于宪法检查：ADRs 目录路径和/或贡献者文档（如果未提供，则从常见位置推断 — `docs/adr/`、`CONTRIBUTING.md`、`contribute/`）

当知道开发者的上下文或角色时，请咨询 `assets/` 中的匹配后续文件以进行有针对性的澄清问题。只问未回答的问题。

- `assets/framework-core-developer.follow-up.md` — Fusion 框架内部、共享库、框架 API
- `assets/react-app.follow-up.md` — Fusion React 应用开发
- `assets/core-service.follow-up.md` — Fusion Core 后端服务（C# / .NET）

## 指令

### 第一步 — 分类和路由

检测主要语言，然后激活匹配的语言代理：
- TypeScript（`.ts`，非组件 `.tsx`）→ `agents/typescript.agent.md`
- React（`.tsx` 带有 JSX 或钩子，组件文件）→ `agents/react.agent.md`
- 混合 `.tsx`（TypeScript 类型关注 + React 组件关注）→ 并行激活两个代理
- C#（`.cs`、`.csproj`）→ `agents/csharp.agent.md`
- Markdown（`.md`、`.mdx`）→ `agents/markdown.agent.md`

始终在每次代码评审时并行激活：
- `agents/intent.agent.md` — 每次评审，无论语言如何
- `agents/constitution.agent.md` — 当项目有 ADRs（`docs/adr/`、`adr/`）或贡献者文档（`CONTRIBUTING.md`、`contribute/`、`.github/copilot-instructions.md`）时

如果无法确定语言，请在继续之前询问。

### 第二步 — 应用或解释规范

每种语言代理首先读取其权威参考文件，然后：
- 对于规范问题：解释规则并提供修正的代码示例
- 对于代码评审：识别偏离，声明规则，显示修正版本
- 不标记项目在 `biome.json` 或 `.editorconfig` 中明确配置的模式

意图和宪法代理并行运行，并将发现结果贡献给综合报告。

### 第三步 — 呈现结果

将所有代理的所有发现组织成一个统一报告：
- **必须** — 必须修复：命名违规、导出缺少 TSDoc、`any` 类型、宪法违规
- **建议** — 应修复：弱意图注释、未记录的魔法值、不合理的抑制
- **建议** — 考虑：缺失的决策记录、过时的 ADRs、需要正式化的隐式例外

对于每个发现：声明规则、受影响的代码和修正版本或建议操作。

### 第四步 — 应用修正

仅应用用户明确批准的修正。使用工作区工具编辑文件。除非少于 50 行，否则不要重写整个文件。

## 预期输出

- 对于规范问题：带有修正代码或标记示例的规则解释
- 对于代码评审：涵盖语言规范、意图质量和宪法合规性的统一发现报告（必须 / 建议 / 建议）
- 在修改任何文件之前，提供用户明确批准的修正

## 安全性和限制

- 未经明确用户确认，永不修改文件。
- 不要标记项目通过 `biome.json` 或 `.editorconfig` 选择进入的风格选择。
- 不要编造 ADR 内容 — 仅执行和挑战实际记录的内容。
