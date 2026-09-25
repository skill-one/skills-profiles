# dx-code-analyzer-custom-rule-create: 自定义代码分析规则创建

> **生态系统:** 此技能是3技能代码分析套件的一部分 — `dx-code-analyzer-run`（扫描与结果）· `dx-code-analyzer-configure`（设置、配置、CI/CD）· `dx-code-analyzer-custom-rule-create`（自定义规则编写）。

当用户需要创建一个自定义规则，以强制执行代码分析器内置规则未涵盖的模式时，请使用此技能。支持正则表达式引擎（文本模式匹配）和PMD引擎（针对抽象语法树的结构XPath查询）。

## 此技能适用任务场景

当工作涉及以下内容时，请使用`dx-code-analyzer-custom-rule-create`：

- 为代码分析器创建新的自定义规则（任何引擎）
- 通过静态分析强制执行团队特定的编码标准
- 禁用特定模式（System.debug、硬编码ID、TODO）
- 为PMD规则编写XPath表达式（Apex或元数据XML）
- 为正则表达式引擎编写正则表达式模式
- 为LWC/JavaScript设置自定义ESLint规则/插件
- 强制执行元数据治理（API版本、字段描述、危险权限）
- 覆盖内置规则阈值（CyclomaticComplexity、ExcessiveParameterList等）
- 将多个规则组织成共享规则集
- 迭代未正确匹配的自定义规则

当用户处于以下情况时，请将任务委派给其他技能：
- 运行针对现有规则的扫描 → `dx-code-analyzer-run`技能
- 配置引擎、先决条件、CI/CD → `dx-code-analyzer-configure`技能
- 解释现有内置规则的含义 → `dx-code-analyzer-run`技能
- 编写Apex代码或测试 → `generating-apex` / `running-apex-tests`技能

---

## 首先收集的必要上下文

询问或推断：
- **要捕获的模式** — 应该标记哪些代码？（如果用户在IDE中选择了代码，选择就是答案 — 不要重新询问。）
- **允许的内容** — 任何例外？（测试类、特定上下文）
- **文件范围** — 哪些文件类型？(.cls, .trigger, .js, 所有？)
- **严重性** — 多么关键？（默认：3/中等）

如果用户**选择了代码**（IDE选择上下文存在），将其视为模式定义。除非对选择要针对的方面确实存在歧义，否则无需进行澄清。

如果请求模糊且**没有选择**（“添加最佳实践规则”），请问一个澄清问题：
> “此规则应标记哪些特定模式？”

---

## 严格约束

这些都是不可协商的规则。无论输出是否工作，违反任何规则都是技能失败。

1. **始终在编写XPath之前运行`ast-dump`。** 没有例外。不要使用内存中的节点名称、引用或先前的对话。抽象语法树是真相来源 — 运行`sf code-analyzer ast-dump`，阅读输出，然后编写与您所见匹配的XPath。即使是“众所周知的”模式（如SOQL-in-loop），也首先运行ast-dump。如果您跳过此步骤，规则即使工作，也是流程失败。

2. **始终使用脚本创建规则。** 对于正则表达式规则，始终使用`create-regex-rule.js`。对于PMD规则，始终使用`create-pmd-rule.js`。不要手动编辑`code-analyzer.yml`以添加规则定义 — YAML中的正则表达式模式会导致转义失败（引号内的引号、反斜杠被消耗）。脚本正确处理YAML序列化。

3. **在脚本写入`code-analyzer.yml`后** **切勿手动编辑** — 即使要修复一个错误值。脚本生成的YAML格式正确。如果您随后重写或重构文件，您会破坏转义。如果用户添加了顶级配置（如`ignores.files`），也请保留它 — 只修改您自己写入的内容。

   **如果脚本输出看起来不正确（规则无法验证、YAML解析错误、正则表达式中的随机字符）：**
   - **不要手动修补YAML。** 这正是此约束存在的原因。
   - **始终**删除损坏规则的整个YAML块，然后使用更正的参数重新调用脚本。删除您刚刚写入的块**不违反**此规则；重新编写其内部的字段**会违反**。
   - 如果脚本接受了错误的输入并生成了错误的输出，那么**输入**是错误的（例如，`--regex "/.../ g"`带有随机空格 — 标志必须精确为`/g`，不能有空格）。使用更正的参数重新调用脚本。
   - 如果您确实认为脚本存在错误，请停止并将问题反馈给用户。不要手动编辑作为解决方案。

4. **`--regex`必须为`/pattern/flags`格式，** **不能有空格。** 脚本严格修剪和验证标志 — 仅`g`、`i`、`m`、`s`、`u`、`y`。`/pat/ g`（带有空格）被拒绝；`/pat/x`（无效标志）和`/pat/`（没有标志）也被拒绝。全局标志`g`是必需的。如果验证失败，请修复参数 — 不要通过直接编写YAML来绕过。

5. **创建后始终验证。** 运行`sf code-analyzer rules --rule-selector <engine>:<name>`。如果`Found 0 rules`，则YAML无法解析 — 删除该块，修复参数，重新调用脚本。

6. **始终使用样本代码进行测试。** 确认至少一个真阳性和一个真阴性。

   对于正则表达式规则，负样本**必须**不包含任何模式文本 — 包括在注释和字符串字面量中。正则表达式引擎扫描原始文本；`// no System.debug here`是`/System\.debug/g`的匹配。在运行它之前，在负样本上 mentally 追踪您的模式。

7. **一次创建一条规则，按顺序。** 当用户请求多个规则时，通过完整的工作流程（创建 → 验证 → 测试阳性 → 测试阴性）单独创建每个规则，然后再开始下一个规则。**不要批量创建规则** — 如果一个失败，它会破坏后续所有规则配置。完成每个规则的端到端，确认它正常工作，然后再移动到下一个。

8. **对于正则表达式规则，通过`ignores.files`排除测试类 — `regex_ignore`** **不**这样做。`regex_ignore`是按行过滤（行必须同时匹配规则和忽略模式）；它不能排除整个测试类。如果用户的意图是“跳过测试类”，请添加顶级`ignores.files`块，带有像`"**/*Test.cls"`这样的通配符，在所有规则创建完成后 — 不要在脚本调用和脚本调用之间混合配置编辑。

---

## 引擎选择

| 模式类型 | 引擎 | 原因 |
|---|---|---|
| 文本/字符串模式（TODO、硬编码ID、关键字） | **正则表达式** | 简单、快速、无需Java |
| Apex代码结构（方法调用、嵌套、循环中的SOQL） | **PMD/XPath**（语言=apex） | 理解抽象语法树，不被注释/字符串欺骗 |
| 元数据XML治理（API版本、权限、描述） | **PMD/XPath**（语言=xml） | 结构化XML匹配，支持命名空间处理 |
| LWC/JavaScript/TypeScript模式 | **ESLint*** | 标准JS工具，插件生态系统 |
| 两者都可以工作（仅Apex/元数据） | **正则表达式优先** | 更简单易创建和维护 |

\* **对于ESLint:** 始终在Tier 1（内置规则）和Tier 2（可配置规则）中检查之前创建自定义插件。请参阅`references/eslint-rules-discovery.md`。

**“两者都可以工作 → 正则表达式优先”** **绝不适用于JavaScript/LWC/TypeScript文件。** JS/LWC/TS模式**必须**使用ESLint — 正则表达式无法区分JS中的代码与注释/字符串。始终使用ESLint。不要基于“简单”或“无需npm依赖”为JS文件合理化正则表达式。

告诉用户您选择的原因，如果他们不同意，请尊重他们的偏好。

### 按引擎排除测试类策略

当规则不应应用于测试类时，方法因引擎而异：

| 引擎 | 如何排除测试类 | 备注 |
|--------|---------------------------|-------|
| **PMD (Apex)** | 在XPath中添加`[not(ancestor::UserClass[ModifierNode[@Test = true()]])]` | 结构化排除 — 完美工作，无需配置更改 |
| **正则表达式** | 在`code-analyzer.yml`中使用`ignores.files`并带有像`**/*Test.cls`这样的通配符 | `regex_ignore`是按行过滤，不是按文件 — 它**不能**排除整个测试类。仅用于按行模式，如`// NOPMD` |
| **ESLint** | 在`eslint.config.js`中的`ignores`数组中 | 标准ESLint文件级忽略 |

**`regex_ignore`不是文件级排除。** 它只跳过与忽略模式匹配的行。它**不**排除整个文件或类。测试类第10行的硬编码ID仍然会标记，除非该特定行包含忽略模式（例如，`@isTest`）。

**始终使用脚本创建规则。** 不要手动编辑`code-analyzer.yml`用于正则表达式规则 — YAML中的正则表达式字符（引号、反斜杠、大括号）会导致解析失败。`create-regex-rule.js`脚本正确处理序列化。

**通过`<rule ref="..."`覆盖内置规则** | 改变阈值而无需编写新规则 |

**绝不要使用正则表达式处理JS/LWC/TS文件。** 正则表达式无法区分JS中的代码与注释/字符串 — 始终使用ESLint处理JavaScript模式。

**在编写自定义规则之前始终检查内置ESLint规则。** `no-console`、`no-debugger`、`no-alert`、`eqeqeq`、`no-eval`等规则已经存在 — 只需在配置中启用它们。

---

## 常见陷阱

| 问题 | 解决方案 |
|-------|------------|
| 编写未运行ast-dump的XPath | **始终在编写XPath之前运行ast-dump。** 即使规则工作，跳过ast-dump也是流程失败。节点名称在不同PMD版本之间会发生变化，无法猜测。 |
| SOQL-in-loop规则标记`for (x : [SELECT...])` | 使用`//ForEachStatement/BlockStatement//SoqlExpression`（限制在主体内）。可迭代SOQL是`ForEachStatement`的直接子代，与`BlockStatement`一起出现 — `//ForEachStatement//SoqlExpression`将其作为误报匹配。 |
| 使用正则表达式处理JS/LWC/TS模式 | **绝不要使用正则表达式处理JavaScript文件。** 正则表达式无法区分JS中的代码与注释/字符串。始终使用ESLint — 首先检查是否存在内置规则（例如，`no-console`）。 |
| XPath返回0匹配（XML元数据） | 三个常见原因： (1) 忘记`local-name()` — 命名空间块中的元素名。 (2) 使用`text()='value'` — 在PMD 7中不起作用。使用`@Text='value'`。 (3) 将`[@Text]`谓词放在元素上 — `@Text`存在于子文本节点上。使用`/*[@Text...]`来到达它们。 |
| 在`code-analyzer.yml`中内联编写的正则表达式规则 — YAML解析错误 | **始终使用`create-regex-rule.js`** — YAML中的引号和反斜杠会导致转义失败。不要手动将正则表达式写入配置文件。 |
| `regex_ignore`无法排除测试类 | `regex_ignore`是**按行**。测试类第50行的SOQL查询标记，因为第50行不包含`@isTest`。对于文件级排除：使用`ignores.files`（全局）或PMD XPath `[not(ancestor::UserClass[ModifierNode[@Test = true()]])]`（按规则）。 |
| XPath `@WithSharing='false'`或`not(@WithSharing)`不起作用 | PMD 7布尔属性（`@WithSharing`、`@Abstract`、`@Final`）**始终**存在。字符串`='false'`不匹配（它是布尔值）。`not(@attr)`不起作用（属性始终存在）。使用XPath布尔函数：`@WithSharing = false()`。 |
| 基于循环的规则仅覆盖`ForEachStatement` | Apex有3种循环类型：`ForEachStatement`、`ForLoopStatement`、`WhileLoopStatement`。所有3种都必须在XPath中 — 忽略任何一种类型都会导致XPath无法验证并可能无声地遗漏违规。 |
| 重写`code-analyzer.yml`后脚本写入 — YAML解析错误 | **绝不要手动重写**脚本写入后的文件。将顶级配置块（如`ignores.files`）作为新条目添加 — 不要触摸脚本生成的`engines.regex.custom_rules`部分。 |
| 同时创建多个规则 — 一个失败会破坏所有后续规则 | **一次创建一条规则，按顺序。** 在开始下一个规则之前，通过完整的工作流程（创建 → 验证 → 测试）完成每个规则。不要批量创建规则 — 如果一个失败，它会破坏后续所有规则配置。 |

对于额外的诊断（错误严重性、Java未找到、ESLint配置路径、元数据文件类型范围等），请参阅`<skill_dir>/references/troubleshooting.md`。

---

## 跨技能集成

| 需求 | 委托给 | 原因 |
|------|-------------|--------|
| 运行完整扫描后创建规则 | `dx-code-analyzer-run` | 扫描执行和结果呈现 |
| 安装代码分析器 / 修复先决条件 | `dx-code-analyzer-configure` | 设置和故障排除 |
| 解释现有内置规则 | `dx-code-analyzer-run` | 规则描述和文档查找 |
| 编辑`code-analyzer.yml`以配置引擎设置 | `dx-code-analyzer-configure` | 配置管理 |

---

## 脚本执行

`<skill_dir>`是包含此`SKILL.md`文件的绝对路径。

所有脚本都捆绑在包含此`SKILL.md`文件的`scripts/`子目录中。使用该目录的绝对路径 — 不要使用`./scripts/`，因为它们相对于当前工作目录解析，而不是技能目录。

```bash
node "<skill_dir>/scripts/create-regex-rule.js" \
  --name "RuleName" --regex "/pattern/flags" ...
```

**不要：**
- 自己发明或生成脚本代码
- 使用裸相对路径，如`node scripts/create-regex-rule.js`（无法从用户的CWD解析）
- 使用heredocs或内联脚本内容
- 跳过解析`<skill_dir>` — 首先找到绝对路径

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `references/regex-rule-schema.md` | 构建正则表达式规则 — 完整字段参考、验证规则、多规则示例 |
| `references/xpath-patterns.md` | 为Apex编写XPath — 模式类别索引、语法参考和抽象语法树节点词汇表 |
| `references/xpath-patterns-governor-limits.md` | 循环中的SOQL/DML、循环中的Database方法 |
| `references/xpath-patterns-method-calls.md` | 禁用方法和注解模式 (@AuraEnabled、@future、@IsTest)的XPath模式 |
| `references/xpath-patterns-security.md` | 分享声明、SOQL安全、硬编码ID的XPath模式 |
| `references/xpath-patterns-structure.md` | 代码结构、测试质量、命名约定 |
| `references/apex-ast-reference.md` | 读取Apex AST转储 — 节点层次结构、修饰符属性、关键节点类型 |
| `references/metadata-xml-rules.md` | 为元数据XML编写规则 — 命名空间工作绕过、常见结构、XPath模式 |
| `references/advanced-pmd-patterns.md` | 多规则规则集、覆盖内置规则、排除模式、Java规则、跨项目共享 |
| `references/eslint-rules-discovery.md` | **对于任何ESLint请求首先阅读** — 发现工作流程、内置规则、Tier 1-3索引 |
| `references/eslint-tier2-configurable.md` | ESLint Tier 2: no-restricted-globals、no-restricted-syntax、no-restricted-properties模式 |
| `references/eslint-tier3-custom-plugins.md` | ESLint Tier 3: 何时创建自定义插件 + 所有层级的完整示例 |
| `references/eslint-custom-plugins.md` | 创建自定义ESLint插件 — **仅在**发现工作流程确认不存在内置或可配置规则（Tier 3）时才这样做 |
| `references/troubleshooting.md` | 验证或测试失败时 — 按引擎类型进行错误诊断 |
| `assets/pmd-ruleset-template.xml` | PMD XML骨架，带有create-pmd-rule脚本的占位符 |
| `examples/regex-examples.md` | 6个解决社区报告问题的真实世界正则表达式规则 |
| `examples/xpath-examples.md` | 6个Apex真实世界的XPath规则，带有AST上下文和逐步创建 |
| `examples/metadata-xml-examples.md` | 6个真实世界元数据XML规则的索引（权限、描述、API版本、流程） |
| `examples/metadata-xml-example-permissions.md` | 元数据示例：ModifyAllData/ViewAllData、字段权限（配置文件） |
| `examples/metadata-xml-example-fields-api.md` | 元数据示例：自定义字段描述、最低API版本 |
| `examples/metadata-xml-example-flows.md` | 元数据示例：流程自动布局、流程错误处理 |
