---
name: konsistent-config
description: 创建或修改一个 `konsistent.json` 配置文件，以强制执行 TypeScript 代码库中的结构规范。当用户希望强制代码结构一致性、验证跨文件导出/导入、确保目录包含所需文件、强制命名规范、添加/删除/更新规范规则、配置缩写或特殊大小写的用例映射（`kebabToPascalMap`、`kebabToCamelMap`），或排查 `konsistent` 报告的违规问题时使用。触发条件包括："konsistent"、"konsistent.json"、"强制规范"、"结构一致性"、"一致导出"、"一致结构"、"代码规范配置"、"添加规范"、"更新规范"、"修复 konsistent 错误"、"用例映射"、"大小写覆盖"、"缩写大小写"。
---

# konsistent 配置

创建或修改一个 `konsistent.json` 文件，以强制执行项目的结构规范。`konsistent` 命令行工具检查文件系统结构和 TypeScript 导出/导入——它不是一个样式检查器。

## 核心目标

**重要提醒：** 不要编写一个 `konsistent.json` 文件，在运行 `konsistent` 检查时不会导致任何错误。那样会适得其反。目标是创建一个 `konsistent.json` 文件，以识别代码库中使用的模式违规行为，即使它们没有完全遵守。根据代码库中占主导地位的模式添加规范，即使其他实例违反了这些模式。

将现有代码库视为推断规范的证据，而不是必须接受所有规范的规范。不符合主导模式的现有文件是预期发现，而不是证明规范是错误的证据。

一个成功的配置可以让 `konsistent` 带有违规行为退出。违规行为是预期的审计输出。只有 `konsistent validate` 才预期无错误通过。

## 工作流程

### 1. 设置 `konsistent` 命令行工具（如果尚未设置）

检查 `konsistent` 包是否已安装：

- 根目录 `package.json` 中有 `konsistent`
- 存在 `node_modules/konsistent` 目录
- `package.json` 中存在 `konsistent` 脚本

如果没有，必须先安装 `konsistent` 命令行工具。使用项目的包管理器。例如，使用 PNPM：

```bash
pnpm add konsistent --save-dev
```

然后，确保 `package.json` 中有一个 `konsistent` 脚本，它调用 `konsistent` 命令行工具。至少需要：

```
  "scripts": {
    "konsistent": "konsistent"
  }
```

如果所有这些都已准备好，请继续第 2 部分。

### 2. 根据 `konsistent.json` 文件是否存在确定操作模式

1. 检查项目根目录下是否已存在 `konsistent.json`。
2. 读取 `node_modules/konsistent/konsistent.schema.json` 以确认权威形状。
3. 在进行更改之前，阅读 `node_modules/konsistent/docs/` 中的相关文档（见下文“参考资料”）。
4. 如果 `konsistent.json` 存在：读取它，然后根据用户的要求添加/删除/更新规范。
5. 如果 `konsistent.json` 不存在：在项目根目录下创建它。

### 3. 创建或编辑 `konsistent.json` 文件

探索用户的代码库，了解现有的结构和命名模式。参考 `node_modules/konsistent/docs/guides/exploring-codebases.md` 了解需要注意的事项。

确保您从整体上审查代码库的结构规范。对于具有多层嵌套子目录的大型代码库，考虑使用子代理来处理代码库的各个部分。使每个子代理都了解以下小节中概述的所有分析要求，并使用子代理收集原始证据，而不是做出最终的主导决策。

当子代理探索单独的部分时，确保它们的发现可以合并为完整的相关群体。每个子代理必须报告其检查的范围、该范围内的总数、遵守和非遵守的数量、竞争模式以及代表性示例。主代理必须合并这些发现，重建每个完整的群体，并使用合并的证据进行主导决策。在一个委托部分中占主导地位的模式不一定是整个群体中的主导模式。

考虑相关文件之间的规范，而不仅限于单个文件。使用 `haveFiles` 谓词来确保基于匹配文件存在特定的其他文件，并使用 `for.files` 来基于匹配文件强制执行特定相关文件内的规范。

#### 必要的模式证据

在记录每个候选规范的证据之前，不要编写配置。对于每个候选规范：

1. 定义完整的相关群体，例如所有兄弟包、适配器、路由或条形文件。考虑相关文件之间的规范，而不仅限于单个文件。
   - 例如，使用 `haveFiles` 谓词来确保基于匹配文件存在特定的其他文件，并使用 `for.files` 来基于匹配文件强制执行特定相关文件内的规范。
2. 计算总数群体、遵守实例和非遵守实例。始终包括分母；仅几个匹配的示例不足以建立主导地位。
3. 与搜索支持性示例一样故意地搜索反例。检查代表性的遵守和非遵守实例。
4. 比较竞争模式。默认情况下，候选规范只有在至少出现三次并占相关群体的三分之二以上时才被认为是主导的。
5. 当遇到没有主导“获胜者”的竞争模式时，暂停并询问用户要强制执行哪种模式（或是否不强制执行任何模式）。
6. 对于每个建立的规范（无论是通过主导候选规范还是通过用户决策），决定非遵守实例是违规行为还是属于一个真正不同的语义群体。现有的变化本身并不能建立合法的例外。

在探索时使用证据表：

| 候选规范 | 群体 | 遵守 | 违规 | 竞争模式 | 决策 |
| --- | --- | ---: | ---: | --- | --- |
| 每个包都有 `src/index.ts` | 12 个包 | 10 | 2 | 无 | 强制执行 |
| 服务文件使用 `-service` 后缀 | 9 个服务文件 | 5 | 4 | `-service` vs. `-svc` | 模糊；询问用户 |

不要编造使所有竞争变体都有效的条件。如果证据是模糊的，暂停并询问用户要强制执行哪种规范或是否不强制执行任何规范。

#### 对抗性审查

在将候选规范转换为配置之前，尝试证伪它：

- 搜索整个群体，而不是在找到几个支持性示例后停止。
- 寻找一个更强的竞争规范或一个改变群体的语义边界。
- 检查是否已有其他工具强制执行该行为。
- 优先选择一个暴露真实异常的规则，而不是一个解释所有现有文件的规则。

此审查的目的是拒绝薄弱或编造的模式。它不是要消除对强模式的违规行为。

当修改现有配置时：

- 保留与用户请求无关的所有规范。
- 保留现有的 `name`、`description` 和 `severity` 值，除非要求更改它们。
- 添加规范时，追加到 `conventions` 数组。
- 当用户报告违规行为时，读取现有配置和违规文件以确定是修复配置还是建议修复代码。

#### 禁止优化

永远不要为了以下结果优化配置：

- 报告零违规行为。
- 使每个现有文件都有效。
- 适应所有观察到的变化。
- 运行 CLI 后减少违规计数。
- 仅为了使 CLI 以退出代码 0 通过而将规范标记为“警告”严重性。

不要因为现有代码违反规范而削弱、缩小、条件化或排除规范。

#### 验证

通过 `package.json` 脚本运行 `konsistent validate` 来验证生成的配置（例如 `pnpm konsistent validate`）。

验证成功后，冻结基于证据的配置，并通过 `package.json` 脚本不带参数运行 `konsistent` 来审计实际代码库。将报告的违规行为视为审计发现，而不是配置失败。

只有在以下情况下才允许审计后的配置更改：

- 配置没有编码证据表中记录的模式。
- 路径模式意外地包含了一个独立的语义群体。
- 配置错误地使用了 `konsistent` 模式或谓词 API。
- 新发现的代码改变了记录的证据，使得候选规范不再占主导地位。

“现有文件不符合此规则”永远不足以更改配置。对于每个审计后更改，说明适用的允许原因，并在相关时更新记录的证据。

## 参考资料

所有规范文档都位于 `node_modules/konsistent/docs/`（随包发布）。在编写配置之前阅读这些文档：

- `node_modules/konsistent/docs/reference/configuration.md` — 顶层 `konsistent.json` 形状（版本、规范、严重性、excludeFiles）。
- `node_modules/konsistent/docs/reference/predicates.md` — 每个 `must` 谓词（`haveType`、`haveFiles`、`export`、`exportTypes`、`exportConstants`、`exportFunctions`、`exportInterfaces`、`exportClasses`、`import`、`importTypes`）。
- `node_modules/konsistent/docs/reference/path-patterns.md` — 通配符、占位符、大小写转换（`toPascalCase`、`toCamelCase`、`toFlatCase`、`toNthSegment`、`extract`、…）、否定。
- `node_modules/konsistent/docs/reference/constraints.md` — `matches`、`segments` 用于内联路径约束和 `if.placeholderSatisfies`。
- `node_modules/konsistent/docs/reference/conditional-rules.md` — `if` / `for` / `excludeFiles` 块，当 `must` 是数组时。
- `node_modules/konsistent/docs/reference/case-maps.md` — `kebabToPascalMap`、`kebabToCamelMap` 用于缩写和特殊大小写。
- `node_modules/konsistent/docs/guides/examples.md` — 可复制粘贴的常见模式（提供包、工厂、适配器、条件规则、…）。
- `node_modules/konsistent/docs/guides/exploring-codebases.md` — 在编写规则之前识别模式的策略。

## 配置语法建议

- 在规范上使用 `name` 以提供可识别的 ID（必须是小写破折号分隔）。
- 当规范名称本身不明确时使用 `description`。
- 优先使用带大小写转换的模板而不是硬编码名称——这是 `konsistent` 的关键优势。
- 当相关谓词应用于相同路径时，将它们组合在一个规范中。
- 当需要不同严重性时，使用相同的路径使用单独的规范。
- 使用路径否定来排除已知例外，但仅当它是规范预期群体之外的一个语义类别时，例如生成文件、固定文件、托管的代码或一个明显不同的包类别。

## 配置语法陷阱

- 不要尝试在声明或导出名称中使用 `*`。这些通配符仅在路径段中允许。

## 完成报告

在交接配置时报告：

- 每个推断的规范及其证据比率，例如 10 个中的 12 个实例。
- 代表性的遵守示例。
- 审计中发现的代表性违规行为，或明确声明未发现。
- 故意跳过的模糊候选模式。
- 每个排除项及其为规范预期群体之外的原因。

不要描述成功为“`konsistent` 通过”。区分模式验证成功与代码库审计发现。
