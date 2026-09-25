# 模板验证

这项技能有助于在发布前验证自定义的 `dotnet new` 模板是否正确。它编码了验证规则，以捕获常见的编写错误——这些问题会导致模板静默失败、生成损坏的项目或在 `dotnet new list` 中不显示。

## 使用场景

- 用户要求检查或验证一个 `template.json` 文件
- 用户报告“安装后我的模板没有显示”
- 用户希望在打包和发布到 NuGet 之前审查模板
- 用户遇到自定义模板的意外行为

## 不适用场景

- 用户想查找或使用现有模板——路由到 `template-discovery`
- 用户想创建项目——路由到 `template-instantiation`
- 用户想从现有项目创建模板——路由到 `template-authoring`

## 输入

| 输入 | 是否必需 | 描述 |
|------|----------|------|
| `template.json` 路径 | 是 | `template.json` 文件或包含 `.template.config/template.json` 的模板目录的路径 |

## 验证规则

在审查 `template.json` 时，系统性地检查以下所有类别。将每个发现报告为错误、警告或建议。

> **解析门禁——语法错误时停止。** 在应用任何语义规则之前解析 JSON。如果解析失败，报告解析器的行和列，仅显示最小的具体语法修正，然后停止。不要从未解析的文档中编造必需字段、符号、后操作或可发现性发现。在修正后重新解析，然后再做出任何语义声明。

格式不良的 JSON 最终响应正好有两部分：一行解析结果和显示精确编辑的修正片段。不要附加语义建议、可选元数据或完整的替换清单。

### 1. 必填字段

| 字段 | 严重程度 | 规则 |
|------|----------|------|
| `identity` | 错误 | 必须存在且非空 |
| `name` | 错误 | 必须存在且非空 |
| `shortName` | 错误 | 必须存在且非空 |
| `sourceName` | 警告 | 没有，`--name` 不会自定义生成的项目名称 |
| `author` | 警告 | 提高模板可发现性 |
| `description` | 建议 | 帮助用户理解模板创建的内容 |
| `classifications` | 建议 | 提高搜索和分类（例如，`["Web", "API"]`） |
| `defaultName` | 建议 | 当 `--name` 未指定时提供备用项目名称 |

### 2. 身份格式

- 如果身份包含空格，则报错——使用点或连字符（例如，`MyCompany.WebApi.CSharp`）
- 如果身份没有命名空间分隔符（`.` 或 `-`），则警告——使用反向 DNS 格式

### 3. 短名冲突

与 `dotnet new` 子命令匹配的短名冲突，因为 `dotnet new <name>` 会被解析为该子命令而不是实例化模板。从 `dotnet new --help` 的 `Commands:` 部分读取安装的 SDK 的保留集——这是权威来源，可以避免此规则过时。

根据当前 SDK，子命令包括（仅作说明——版本相关，不要硬编码此列表；`dotnet new --help` 的实时输出是权威的）：`install`、`uninstall`、`update`、`list`、`search`、`details`、`create`。请注意，顶级 `dotnet` 动词如 `build`、`run`、`test` 和 `publish` 不冲突——`dotnet new test` 不会与 `dotnet test` 冲突。

- 如果短名与 `dotnet new --help` 报告的任何子命令匹配（不区分大小写），则报错
- 如果短名只有 1 个字符，则警告——太短，不利于可发现性
- 注意：短名可以是字符串或字符串数组；检查所有值

### 4. 符号验证

对于 `symbols` 对象中的每个符号：

- 如果符号缺少 `type` 字段，则报错
- 对于 `type: "parameter"`：
  - 如果没有指定 `datatype`，则警告（默认为 `string`）
  - 如果没有 `description`，则建议（改进 `--help` 输出）
  - 如果 `datatype: "choice"`：
    - 如果没有定义 `choices`，则报错
    - 如果 `choices` 为空，则报错
    - 如果 `defaultValue` 不在 `choices` 列表中，则报错
    - 如果可选（不是 `isRequired`）且没有 `defaultValue`，则警告——用户会得到意外行为
  - 如果 `datatype: "bool"`：
    - 如果 `defaultValue` 不是一个有效的布尔值，则报错
  - 如果 `datatype: "int"`：
    - 如果 `defaultValue` 不是一个有效的整数，则报错
  - 有效的数据类型：`string`、`bool`、`choice`、`int`、`float`、`hex`、`text`
  - 如果数据类型不在有效列表中，则报错
- 对于 `type: "computed"`：
  - 如果缺少 `value` 表达式，则报错
- 对于 `type: "generated"`：
  - 如果缺少 `generator` 字段，则报错
  - 有效的生成器：`casing`、`coalesce`、`constant`、`port`、`guid`、`now`、`random`、`regex`、`regexMatch`、`switch`、`join`

自定义参数帮助是模板特定的：它出现在 `dotnet new <shortName> --help` 下，而不是全局的 `dotnet new --help`。在必要时纠正这一前提，然后解释哪些无效的符号定义导致参数无法可靠地显示。

一个有效的选择参数使用非空的 `choices` 对象，例如：

```json
"Color": {
  "type": "parameter",
  "datatype": "choice",
  "defaultValue": "Blue",
  "choices": {
    "Blue": { "displayName": "Blue" },
    "Green": { "displayName": "Green" }
  }
}
```

**参数前缀冲突**：如果任何参数名是另一个参数名的前缀（例如，`Auth` 和 `AuthMode`），则警告——这会在表达式上下文中创建歧义。

### 5. 源验证

对于源修饰符条件：

- 如果条件字符串不包含符号名周围的括号，则警告——预期格式是 `(symbolName)`，而不是裸 `symbolName`

### 6. 后操作验证

对于每个后操作：

- 如果缺少 `actionId`，则报错
- 如果缺少 `description`，则警告——当操作需要手动步骤时，会向用户显示此文本
- 如果缺少 `manualInstructions`，则建议——当操作无法自动运行时（例如，在 IDE 中）会显示这些内容

### 7. 约束验证

对于每个约束：

- 如果缺少 `type` 字段，则报错
- 如果缺少 `args`，则警告——大多数约束类型需要参数
- 对于 `type: "host"`，缺少 `args` 是报错。`args` 是一个必需的数组；每个条目需要 `hostname`。支持的内置标识符包括 `dotnetcli`、`vs`、`vs-mac`、`ide` 和 `dotnetcli-preview`。可选的 `version` 使用 NuGet 版本/范围语法，例如 `[10.0.100,)`。引擎不区分大小写地匹配参数键，因此文档中记录的 `hostName` 拼写也是有效的。拒绝无关字段，如 `pattern` 和 `value`。
- 对于 `type: "sdk-version"`，`args` 是一个使用相同语法的版本字符串或数组。

### 8. 标签验证

- 如果没有 `language` 标签，则建议——添加 `tags.language`（例如，`"C#"`）可以提高在 `dotnet new list --language` 中的过滤效果
- 如果没有 `type` 标签，则建议——添加 `tags.type`（例如，`"project"` 或 `"item"`）可以提高分类效果

## 工作流程

### 第 1 步：定位 `template.json`

文件可以位于：

- 直接路径：`path/to/template.json`
- 在模板目录中：`path/to/.template.config/template.json`
- 在 `.template.config` 目录中：`path/.template.config/template.json`

### 第 2 步：解析和验证

读取 JSON。如果它是格式不良的，报告 JSON 解析错误及其行和列。如果绝对路径读取失败，则从工作目录重试用户提供的相对路径，然后再得出文件不可用的结论。

只有在解析成功后，才运行上述 8 个验证类别。分别收集错误、警告和建议。对照安装的 SDK 或当前模板引擎的架构验证与架构相关的声明；不要仅凭字段名就推断运行时失败。

### 第 3 步：报告结果

**首先是一个简短的结论**，然后是一个单独的发现表格。这种决定性的形状是必需的——不要将发现分散在散文段落中。

结论标题（选择一个）：

- `❌ 未准备好 — N 个错误，M 个警告` —— 存在错误
- `⚠️ 可以发布，但 N 个警告` —— 没有错误，有警告
- `✅ 可以发布 — 0 个错误，0 个警告` —— 没有错误或警告（可选建议可能仍然适用）

然后一个表格，按错误 → 警告 → 建议 的顺序排序：

| 严重程度 | 位置（JSON 路径或 `line:col`） | 问题 | 修复 |
|----------|------------------------------------|------|------|
| 错误 | `shortName` | `"list"` 与 `dotnet new` 子命令冲突 | 重命名为一个独特的值，例如 `"my-list"` |
| 错误 | `symbols.maxRetries.defaultValue` | `"abc"` 不是一个有效的 `int` | 设置一个数字默认值，例如 `"3"` |
| 警告 | `sourceName` | 缺少替换标记 | 设置为源项目名称 |

**每个错误和警告都必须包含一个具体的修复**——修正后的值、JSON 片段或具体的编辑指令（例如，“删除尾随逗号”），而不仅仅是问题的重述。没有可操作的修复的发现是不完整的。这是区分有用验证和通用 linter 的最大区别。

最后是总数：“N 个错误，M 个警告，K 个建议。”

对于格式不良的 JSON，输出有意更小，并且正好有两部分：

`❌ 未准备好 — JSON 解析错误在第 N 行，第 M 列：<消息>。`

```json
<最小的修正片段，显示精确的编辑>
```

在修正后的文件解析之前，不要附加发现表格或语义总数。

## 常见陷阱

| 陷阱 | 影响 |
|------|------|
| `ShortName` = "list" 或 "search" | 模板永远无法创建——与 `dotnet new` 子命令冲突 |
| 缺少 `sourceName` | `--name MyProject` 不会在生成的文件中重命名任何内容 |
| 没有默认值的选项参数 | 可选选择参数的用户体验令人困惑 |
| 无效的 `datatype` 值 | 模板引擎忽略符号，导致静默失败 |
| 没有值的计算符号 | 模板引擎在实例化时抛出错误 |
| 参数前缀冲突（`Auth` vs `AuthMode`） | 表达式求值不明确 |
| 源条件没有括号 | 条件可能无法正确评估 |
| JSON 解析失败后继续语义验证 | 发现是推测性的。报告精确的解析修复并停止。 |
| 主机约束使用标量 `args`、无效的 `dotnet-cli` 主机 ID 或无关字段 | 使用 `args: [{ "hostname": "dotnetcli", "version": "[10.0.100,)" }]`；`hostName` 的大小写不敏感地也接受。 |

## 更多信息

- [template.json 参考](https://github.com/dotnet/templating/wiki/Reference-for-template.json) — 完整架构
- [可用的符号生成器](https://github.com/dotnet/templating/wiki/Available-Symbols-Generators) — 生成器类型
- [后操作注册表](https://github.com/dotnet/templating/wiki/Post-Action-Registry) — 操作 ID
- [约束](https://github.com/dotnet/templating/wiki/Constraints) — 约束类型
