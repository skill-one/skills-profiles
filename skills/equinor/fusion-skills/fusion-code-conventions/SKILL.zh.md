---
name: fusion-code-conventions
description: "适用于 TypeScript、React、C# 和 Markdown 的代码规范应用与解释。强制执行命名规则、文件命名模式、TSDoc 和 XML 文档标准、内联注释意图（即 *为什么* 而非 *什么*）、代码结构、错误处理、异步模式以及死代码策略。同时强制执行 ADR 和贡献者文档决策，并标记看似过时或与当前工具不匹配的决策。  \n**适用场景**：  \n- 规范问题咨询  \n- 项目标准代码审查  \n- 应用命名规则  \n- 审核意图注释  \n- 检查 TSDoc 完整性  \n- 强制执行已记录的 ADR 决策  \n- 标记过时的架构决策  \n**不适用场景**：  \n- 安全漏洞扫描  \n- 性能分析  \n- 运行时调试  \n- 未经审查目标生成全新代码"
---

# 代码规范

## 使用场景

当代码需要评审、编写或解释以符合项目规范时使用。适用于两个层面：

- **语言规范** — 命名、文件命名、类型系统、TSDoc/XML文档标准、代码结构、错误处理、异步模式、死代码策略。每种语言都有专门的代理和权威参考文档。
- **跨领域规范** — 每次评审都应用：意图捕获（每个非显而易见的决策都必须足够详细地记录，以便代码仅从注释中即可再生）和宪法执行（ADRs和贡献者文档是法律；偏离需要新的决策记录；过时的决策被标记）。

典型触发器：
- "这个项目的命名规范是什么？"
- "这个函数应该如何编写TSDoc？"
- "这个文件是否符合我们的代码风格？"
- "评审这个以查找规范违规"
- "这里应该使用哪种注释风格？"
- "这个TypeScript / React / C# / Markdown是否地道？"
- "将代码规范应用于这个文件"
- "这些内联注释足够好吗？"
- "这个是否违反任何ADRs？"
- "这个ADRs是否仍然有效？"
- "我们有CONTRIBUTING.md — 检查这个变更是否遵循它"

## 不适用场景

- 安全漏洞扫描（使用专门的安全评审技能）
- 性能分析或基准测试
- 高级架构或系统设计决策
- 没有评审目标的全新代码生成
- 没有明确用户确认的文件修改

## 优先级和适用范围

此技能提供**组织级基础规范**。当安装在具有自身规范的环境中时，优先级（最高者胜出）：

1. **仓库级策略** — CONTRIBUTING.md、贡献者指南（contribute/）、ADRs、.github/copilot-instructions.md、AGENTS.md或等效文件
2. **工具配置** — biome.json、tsconfig.json、.editorconfig、代码检查器配置
3. **此技能** — references/*.conventions.md中的所有规则和代理模式

当仓库明确缩小、放宽或与该技能的规则相矛盾时，仓库策略优先。不要标记符合仓库文档规范的代码，即使它偏离了技能基准。

如果冲突未记录（没有ADRs、没有贡献者说明、没有配置），将技能规则视为默认值并建议团队记录他们的意图。

> **对于维护者**：在CONTRIBUTING.md、贡献者指南或ADRs中记录规范覆盖，以便人类和代理都能一致地发现它们。

## 代理模式

| 代理 | 激活条件 |
|---|---|
| `agents/typescript.agent.md` | TypeScript命名、TSDoc、类型系统、代码风格、错误处理 |
| `agents/react.agent.md` | React组件结构、钩子规则、可访问性、键 |
| `agents/csharp.agent.md` | C#命名、CQRS模式、异步/等待、空安全、测试 |
| `agents/markdown.agent.md` | Markdown结构、frontmatter、链接、引用、GitHub特定语法 |
| `agents/intent.agent.md` | 意图捕获 — 每次代码评审时并行应用 |
| `agents/constitution.agent.md` | ADR和贡献者文档执行 — 当项目有决策记录时并行应用 |

规范参考（每种语言的权威规则）：
- `references/typescript.conventions.md`
- `references/react.conventions.md`
- `references/csharp.conventions.md`
- `references/markdown.conventions.md`

## 必需输入

如果必需输入缺失或模糊，请在继续之前询问。

- 目标代码（内联片段或文件路径）或特定规范问题
- 语言或文件类型（如果未提供，则从内容中推断）
- 对于宪法检查：ADRs目录路径和/或贡献者文档（如果未提供，则从常见位置推断 — `docs/adr/`、`CONTRIBUTING.md`、`contribute/`）

当知道开发者的上下文或角色时，请咨询`assets/`中的匹配后续文件以获取有针对性的澄清问题。只问未回答的问题。

- `assets/framework-core-developer.follow-up.md` — Fusion框架内部、共享库、框架API
- `assets/react-app.follow-up.md` — Fusion React应用开发
- `assets/core-service.follow-up.md` — Fusion Core后端服务（C# / .NET）

## 指令

### 第一步 — 分类和路由

检测主要语言，然后激活匹配的语言代理：
- TypeScript（`.ts`，非组件`.tsx`）→ `agents/typescript.agent.md`
- React（`.tsx`带JSX或钩子，组件文件）→ `agents/react.agent.md`
- 混合`.tsx`（TypeScript类型关注点+React组件关注点）→ 并行激活两个代理
- C#（`.cs`，`.csproj`）→ `agents/csharp.agent.md`
- Markdown（`.md`，`.mdx`）→ `agents/markdown.agent.md`

在任何代码评审中始终并行激活：
- `agents/intent.agent.md` — 每次评审，无论语言如何
- `agents/constitution.agent.md` — 当项目有ADRs（`docs/adr/`，`adr/`）或贡献者文档（`CONTRIBUTING.md`，`contribute/`，`.github/copilot-instructions.md`）时

如果无法确定语言，请在继续之前询问。

### 第二步 — 应用或解释规范

每种语言代理首先读取其权威参考文件，然后：
- 对于规范问题：解释规则并提供修正的代码示例
- 对于代码评审：识别偏离，声明规则，显示修正版本
- 不标记项目在`biome.json`或`.editorconfig`中明确配置的模式

意图和宪法代理并行运行，并将发现结果贡献给综合报告。

### 第三步 — 呈现结果

将所有代理的所有发现组织成一个统一报告：
- **必需** — 必须修复：命名违规、导出缺少TSDoc、`any`类型、宪法违规
- **推荐** — 应该修复：弱意图注释、未记录的魔法值、不合理的抑制
- **建议** — 考虑：缺失决策记录、过时的ADRs、需要正式化的隐式例外

对于每个发现：声明规则、受影响的代码，以及修正版本或建议的操作。

### 第四步 — 应用修正

仅应用用户明确批准的修正。使用工作区工具编辑文件。除非少于50行，否则不要重写整个文件。

## 预期输出

- 对于规范问题：带有修正代码或标记示例的规则解释
- 对于代码评审：涵盖语言规范、意图质量和宪法合规性的统一发现报告（必需 / 推荐 / 建议）
- 在修改任何文件之前，提供修正并要求用户明确批准

## 安全性与限制

- 未经明确用户确认，永不修改文件。
- 不要标记项目通过`biome.json`或`.editorconfig`选择采用的风格选择。
- 不要编造ADRs内容 — 仅执行和挑战实际记录的内容。
