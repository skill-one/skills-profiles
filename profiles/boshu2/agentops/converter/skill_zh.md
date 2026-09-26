# 转换器 — 跨平台技能转换器

将 AgentOps 技能解析为通用 SkillBundle 格式，然后转换为目标代理平台。

中间的 SkillBundle 是保证转换过程透明的基础：每个目标平台都读取相同的解析合同，因此渲染错误是目标适配器的问题，而不是源代码的静默重解释。如果两个目标平台对技能内容存在分歧，则由 bundle（而不是输出）进行仲裁。

这不是托运的 `skills-codex/**` 投影的所有者：该路径由 `scripts/codex-sync.sh` 通过 `scripts/regen-all.sh` 生成和锁定。这个转换器是一个临时的、树外的导出器（Codex，Cursor），它写入 `.agents/projections/converter/` 下；它永远不会修改 `skills-codex/**`。当托运的 Codex 双胞胎和这个导出器不一致时，托运的路径将获胜。

命名的失败模式 — **投影编辑**：通过手动编辑转换后的输出来修复渲染问题，而下一个转换会将其清理覆盖。

反模式：将新输出合并到现有的目标目录中以保留本地修改。纠正方法：修复源技能或适配器，然后重新运行清理写入转换。

## 约束条件

- 将规范源技能视为只读，因为转换不能修改它正在转换的合同。
- 仅清理写入明确的目标目录，以防止过时的资源在转换后幸存或无关的路径被删除。
- 当复制资源一致性或目标格式验证失败时失败，因为部分 bundle 不是一个可用的转换。

## 管道

转换器运行一个三阶段管道：

```
解析 --> 转换 --> 写入
```

### 阶段 1：解析

读取源技能目录并生成一个 SkillBundle：

- 从 SKILL.md 中提取 YAML 前置文本（在 `---` 标记之间）
- 收集 Markdown 正文（在关闭的 `---` 之后）
- 枚举 `references/` 和 `scripts/` 中的所有文件
- 组装成一个 SkillBundle（参见 `references/skill-bundle-schema.md`）

### 阶段 2：转换

将 SkillBundle 转换为目标平台的格式：

| 目标 | 输出格式 | 状态 |
|------|----------|------|
| `codex` | Codex SKILL.md + prompt.md | 已实现 |
| `cursor` | Cursor .mdc 规则 + 可选的 mcp.json | 已实现 |

Codex 适配器生成一个 `SKILL.md`，其中包含 YAML 前置文本（`name`，`description`）以及重写的正文内容和 `prompt.md`。默认模式是 **模块化**：引用文档、脚本和资源作为文件复制，`SKILL.md` 包含本地资源索引而不是内联所有内容。可选的 **内联** 模式通过追加内联引用和脚本代码块保留旧行为。Codex 输出规范化了外运行时调用语法和路径，将不支持的原始标签重写为运行时中立的措辞，并保留当前的扁平 `ao` CLI 命令。它还去除了重复的运行时标题，同时保留部分内容。非生成的资源文件和目录会进行一致性检查。如果需要，描述会被截断到 1024 个字符，以词边界为准。

Cursor 适配器生成一个 `<name>.mdc` 规则文件，其中包含 YAML 前置文本（`description`，`globs`，`alwaysApply: false`）和正文内容。引用被内联到正文中，脚本作为代码块包含。输出被预算适配到最大 100KB — 如果总大小超过限制，引用会按从大到小的顺序被省略。如果技能引用 MCP 服务器，还会生成一个 `mcp.json` 桩。

### 阶段 3：写入

将转换后的输出写入磁盘。

- **默认输出目录**：`.agents/projections/converter/<目标>/<技能名>/`
- **写入语义**：清理写入。在写入之前会删除目标目录。不与现有内容合并。
- **拒绝保护**：写入阶段会拒绝 — 它不会静默重定向 — 当解析后的输出目录等于源包、包含它（一个祖先）或为仓库根目录时，因为清理写入否则会删除转换必须读取的文件。

## CLI 使用

```bash
# 转换单个技能
bash skills/converter/scripts/convert.sh <技能目录> <目标> [输出目录]
bash skills/converter/scripts/convert.sh --codex-layout inline <技能目录> codex [输出目录]

# 转换所有技能
bash skills/converter/scripts/convert.sh --all <目标> [输出目录]
```

### 参数

| 参数 | 必填 | 描述 |
|------|------|------|
| `skill-dir` | 是（或 `--all`） | 技能目录路径（例如 `skills/council`） |
| `target` | 是 | 目标平台：`codex`，`cursor` 或 `test` |
| `output-dir` | 否 | 覆盖输出位置。默认：`.agents/projections/converter/<目标>/<技能名>/` |
| `--all` | 否 | 转换 `skills/` 目录中的所有技能 |
| `--codex-layout` | 否 | Codex 仅布局模式：`modular`（默认）或 `inline`（旧版内联引用/脚本） |

## 支持的目标

- **codex** — 转换为 OpenAI Codex 格式（`SKILL.md` + `prompt.md`）并带有运行时中立的重写和扁平 `ao` CLI 保留。默认是模块化输出，带有复制的资源和本地资源索引；传递 `--codex-layout inline` 以获取旧版内联引用/脚本。缺少复制的资源会快速失败。
- **cursor** — 转换为 Cursor 规则格式（`.mdc` 规则文件 + 可选的 `mcp.json`）。输出：`<目录>/<名>.mdc` 和可选的 `<目录>/mcp.json`。
- **test** — 以结构化 Markdown 发出原始 SkillBundle。用于调试解析阶段。

## 扩展

要添加新的目标平台：

1. 在 `scripts/convert.sh` 中添加一个转换函数（模式：`convert_<目标>`）
2. 更新上表中的目标表格
3. 如果目标格式需要文档，则添加参考文档到 `references/`

## 示例

### 将单个技能转换为 Codex 格式

**调用者请求**：将 `skills/council` 转换为 Codex 格式。

**发生的事情**：
1. 转换器解析 `skills/council/SKILL.md` 的前置文本、Markdown 正文以及任何 `references/` 和 `scripts/` 文件，生成一个 SkillBundle。
2. Codex 适配器将 bundle 转换为一个 `SKILL.md`（正文 + 内联引用 + 脚本作为代码块）和一个 `prompt.md`（Codex 提示引用技能）。
3. 输出写入到 `.agents/projections/converter/codex/council/`。

**结果**：一个 Codex 兼容的技能包，准备好与 OpenAI Codex CLI 一起使用。

### 批量转换为 Cursor 规则

**调用者请求**：将所有规范技能转换为 Cursor 格式。

**发生的事情**：
1. 转换器扫描 `skills/` 下每个目录并将每个解析为 SkillBundle。
2. Cursor 适配器将每个 bundle 转换为带有 YAML 前置文本和正文内容的 `.mdc` 规则文件，预算适配到最大 100KB。引用 MCP 服务器的技能还会生成一个 `mcp.json` 桩。
3. 每个技能的输出写入到 `.agents/projections/converter/cursor/<技能名>/`。

**结果**：所有技能都作为 Cursor 规则可用，准备好放入 `.cursor/rules/` 目录。

## 故障排除

| 问题 | 原因 | 解决方案 |
|------|------|------|
| `解析错误：未找到前置文本` | SKILL.md 缺少 `---` 分隔的 YAML 前置文本块 | 添加至少包含 `name:` 和 `description:` 字段的前置文本，或先对源包运行 Heal Skill |
| Cursor `.mdc` 输出缺少引用 | bundle 总大小超过了 100KB 预算限制 | 转换器按从大到小的顺序省略引用以适应预算。拆分大型引用文件或将非必要内容移至外部文档 |
| 输出目录已存在旧文件 | 以前的转换遗留物仍然存在 | 这是预期的 — 转换器通过在写入前删除目标目录进行清理写入。如果旧文件仍然存在，手动删除 `.agents/projections/converter/<目标>/<技能>/` |
| `--all` 跳过了一个技能目录 | 该目录没有 `SKILL.md` 文件 | 确保每个技能目录包含一个有效的 `SKILL.md`。运行 Heal Skill 以检测空目录 |
| Codex `prompt.md` 描述被截断 | 技能描述超过 1024 个字符 | 这是设计的。转换器在词边界处截断以适应 Codex 限制。如果截断点不理想，请在 SKILL.md 前置文本中缩短描述 |
| 转换因传递一致性检查失败 | 源技能中的一个资源条目没有被复制到输出 | 确保源条目可读且可复制（包括嵌套文件）。重新运行转换；失败是故意的，以防止 `skills/` 和转换输出之间的漂移 |

## 输出规范

- **路径**：默认为 `.agents/projections/converter/<目标>/<技能名>/`，或调用者提供的确切输出目录。
- **文件名**：Codex 发出 `SKILL.md`，`prompt.md` 和复制的资源；Cursor 发出 `<技能名>.mdc` 和可选的 `mcp.json`；`test` 发出原始 bundle 表示。
- **格式**：目标有效的 UTF-8 文本，包含必需的前置文本、重写的运行时引用和字节存在的传递资源；Cursor 输出保持在 100KB 内。
- **退出代码**：运行 `bash skills/converter/scripts/convert.sh <技能目录> <目标> <输出目录>` 并要求零；将解析、预算、写入或传递一致性失败视为非零和不完整。
- **下游交接**：向安装程序或投影门报告源技能、目标、输出目录、布局、如果有 Cursor 省略的引用，以及验证结果。

## 质量检查清单

- 源树未更改，输出树不包含来自早期转换的任何遗留文件。
- 每个必需的目标文件都使用其目标前置文本/模式解析，并且每个符合条件的源资源都存在。
- 运行时特定重写保留了源含义，而没有重新引入已弃用的命令形式或外运行时路径。

## 参考

- `references/skill-bundle-schema.md` — SkillBundle 交换格式规范

## 参考文档

- [references/skill-bundle-schema.md](references/skill-bundle-schema.md)
