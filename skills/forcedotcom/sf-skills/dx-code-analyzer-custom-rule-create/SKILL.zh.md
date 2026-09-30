---
name: dx-code-analyzer-custom-rule-create
description: 创建自定义代码分析器规则，支持正则表达式（模式匹配）、PMD（XPath/AST用于Apex和元数据XML）以及ESLint（LWC/JavaScript/TypeScript）。在用户需要强制执行编码规范、禁止特定模式、检测硬编码值、管理元数据或添加内置规则集之外的规则时使用。触发条件：当用户说“创建规则”、“禁止System.debug”、“强制命名规范”、“检测硬编码ID”、“自定义规则”、“XPath规则”、“正则规则”、“添加PMD规则”、“强制策略”、“创建检查”、“标记此模式”、“创建捕获规则的指令”、“元数据规则”、“检查权限”、“强制API版本”、“ESLint规则”、“LWC规则”、“覆盖规则阈值”、“自定义复杂度”或描述需要强制的模式时。不触发条件：当用户需要运行扫描（使用dx-code-analyzer-run）、配置引擎（使用dx-code-analyzer-configure）或解释现有规则（使用dx-code-analyzer-run）时。
---

# dx-code-analyzer-custom-rule-create: 自定义代码分析器规则创建

> **生态系统：** 此技能是 3 技能代码分析器套件的一部分 — `dx-code-analyzer-run`（扫描与结果）· `dx-code-analyzer-configure`（设置、配置、CI/CD）· `dx-code-analyzer-custom-rule-create`（自定义规则创建）。

当用户需要创建一个自定义规则，以强制执行代码分析器内置规则未涵盖的模式时，请使用此技能。支持正则表达式引擎（文本模式匹配）和 PMD 引擎（针对抽象语法树的结构化 XPath 查询）。

## 此技能负责任务的条件

当工作涉及以下内容时，请使用 `dx-code-analyzer-custom-rule-create`：

- 为代码分析器创建新的自定义规则（任何引擎）
- 通过静态分析强制执行团队特定的编码标准
- 禁用特定模式（System.debug、硬编码的 ID、TODO）
- 为 PMD 规则编写 XPath 表达式（Apex 或元数据 XML）
- 为正则表达式引擎编写正则表达式模式
- 为 LWC/JavaScript 设置自定义 ESLint 规则/插件
- 强制执行元数据治理（API 版本、字段描述、危险权限）
- 覆盖内置规则阈值（CyclomaticComplexity、ExcessiveParameterList 等）
- 将多个规则组织成共享规则集
- 迭代一个无法正确匹配的自定义规则

当用户处于以下情况时，请将任务委托给其他技能：

- 运行针对现有规则的扫描 → `dx-code-analyzer-run` 技能
- 配置引擎、先决条件、CI/CD → `dx-code-analyzer-configure` 技能
- 解释现有内置规则的含义 → `dx-code-analyzer-run` 技能
- 编写 Apex 代码或测试 → `generating-apex` / `running-apex-tests` 技能

---

## 首先收集所需的上下文

询问或推断：

- **要捕获的模式** — 应该标记哪些代码？（如果用户在 IDE 中选择了代码，选择的内容就是答案 — 不要重新询问。）
- **允许的内容** — 任何例外吗？（测试类、特定上下文）
- **文件范围** — 哪些文件类型？（.cls、.trigger、.js、全部？）
- **严重性** — 多么关键？（默认：3/中等）

如果用户**选择了代码**（IDE 选择上下文存在），将其视为模式定义。除非对选择要针对的方面确实存在歧义，否则跳过澄清。

如果请求模糊且没有选择（“添加最佳实践规则”），请问一个澄清问题：

> “此规则应标记哪些具体模式？”

---

## 严格约束

这些是不可协商的规则。违反其中任何一条都是技能失败，无论输出是否恰好工作。

1. **在编写 XPath 之前，始终运行 `ast-dump`。** 没有例外。不要使用内存中的节点名称、引用或先前的对话。抽象语法树是真相来源 — 运行 `sf code-analyzer ast-dump`，阅读输出，然后编写与您所见匹配的 XPath。即使是“众所周知”的模式（如 SOQL-in-loop），也要先运行 ast-dump。如果您跳过这一步，规则即使工作，也是流程失败。

2. **始终使用脚本创建规则。** 对于正则表达式规则，始终使用 `create-regex-rule.js`。对于 PMD 规则，始终使用 `create-pmd-rule.js`。不要手动编辑 `code-analyzer.yml` 添加规则定义 — YAML 中的正则表达式模式会导致转义失败（嵌套引号、反斜杠被消耗）。脚本每次都能正确处理 YAML 序列化。

3. **脚本写入后，永远不要手动编辑 `code-analyzer.yml` — 即使要修复一个错误值。** 脚本生成的 YAML 转义正确。如果您然后重写或重新结构化文件，您会破坏转义。如果用户添加了顶层配置（如 `ignores.files`），也保持原样 — 只修改您写入的内容。

   **如果脚本输出看起来不正确（规则无法验证、YAML 解析错误、正则表达式中出现随机字符）：**
   - 不要手动修补 YAML。这正是此约束存在的原因。
   - **始终** 删除损坏规则的整个 YAML 块，然后使用修正后的参数重新调用脚本。删除您刚刚写入的块不违反此规则；在内部重写字段会违反。
   - 如果脚本接受了错误输入并生成了错误输出，输入是错误的（例如 `--regex "/.../ g"` 中有一个随机空格 — 标志必须精确为 `/g`，不能有空格）。使用修正后的参数重新调用。
   - 如果您确实认为脚本存在错误，停止并向用户报告。不要手动编辑作为解决方案。

4. **`--regex` 必须是 `/pattern/flags`，且不能有空格。** 脚本严格修剪和验证标志 — 仅 `g`、`i`、`m`、`s`、`u`、`y`。`/pat/ g`（有空格）被拒绝；`/pat/x`（无效标志）和 `/pat/`（无标志）也被拒绝。全局标志 `g` 是必需的。如果验证失败，请修正参数 — 不要通过直接编写 YAML 来绕过。

5. **创建后始终验证。** 运行 `sf code-analyzer rules --rule-selector <engine>:<name>` 之前测试。如果 `Found 0 rules`，则 YAML 未解析 — 删除块，修正参数，重新调用脚本。

6. **始终针对样本文件进行测试。** 确认至少一个真阳性和一个真阴性。

   对于正则表达式规则，负样本绝对不能在任何地方包含模式文本 — 包括在注释和字符串字面量中。正则表达式引擎扫描原始文本；`// no System.debug here` 对于 `/System\.debug/g` 是匹配的。在运行它之前，在脑海中跟踪您的模式与负样本。

7. **一次创建一个规则，按顺序。** 当用户请求多个规则时，通过完整的工作流程（创建 → 验证 → 测试阳性 → 测试阴性）单独创建每个规则，然后再开始下一个。不要批量创建规则 — 如果一个失败，它会破坏后续所有规则的配置。完成每个规则端到端，确认它工作正常，然后移动到下一个。

8. **对于正则表达式规则，通过 `ignores.files` 排除测试类 — `regex_ignore` 不起作用。** `regex_ignore` 是按行过滤（行必须同时匹配规则和忽略模式）；它不能排除整个测试类。如果用户的意图是“跳过测试类”，请添加一个顶层 `ignores.files` 块，包含像 `"**/*Test.cls"` 这样的通配符，在所有规则创建后 — 不要在脚本调用中交错配置编辑。

---

## 引擎选择

| 模式类型 | 引擎 | 原因 |
|---|---|---|
| 文本/字符串模式（TODO、硬编码的 ID、关键字） | **正则** | 简单、快速、无需 Java |
| Apex 代码结构（方法调用、嵌套、循环中的 SOQL） | **PMD/XPath**（语言=apex） | 理解抽象语法树，不会被注释/字符串欺骗 |
| 元数据 XML 治理（API 版本、权限、描述） | **PMD/XPath**（语言=xml） | 结构化 XML 匹配，支持命名空间处理 |
| LWC/JavaScript/TypeScript 模式 | **ESLint*** | 标准 JS 工具，插件生态系统 |
| 两者都适用（仅 Apex/元数据） | **正则优先** | 创建和维护更简单 |

\* **对于 ESLint：** 始终在创建自定义插件之前检查 Tier 1（内置规则）和 Tier 2（可配置规则）。参见 `references/eslint-rules-discovery.md`。

**“两者都适用 → 正则优先”永远不会适用于 JavaScript/LWC/TypeScript 文件。** JS/LWC/TS 模式必须使用 ESLint — 正则表达式无法区分 JS 中的代码和注释/字符串，会产生误报。不要基于“简单”或“无需 npm 依赖”为 JS 文件合理化正则表达式。

告诉用户您选择的引擎及其原因。如果他们不同意，请尊重他们的偏好。

### 排除测试类的策略（按引擎）

当规则不应适用于测试类时，方法因引擎而异：

| 引擎 | 如何排除测试类 | 备注 |
|---|----------------|-------|
| **PMD (Apex)** | 在 XPath 中添加 `[not(ancestor::UserClass[ModifierNode[@Test = true()]])]` | 结构化排除 — 完美工作，无需配置更改 |
| **正则** | 在 `code-analyzer.yml` 中使用 `ignores.files` 并包含像 `**/*Test.cls` 这样的通配符 | `regex_ignore` 是按行，不是按文件 — 它不能排除整个测试类。仅用于按行模式，如 `// NOPMD` |
| **ESLint** | 在 `eslint.config.js` 中使用 `ignores` 数组 | 标准 ESLint 文件级忽略 |

**`regex_ignore` 不是按文件排除。** 它仅跳过同时匹配忽略模式的行的匹配。示例：`regex_ignore: "/@isTest/i"` 仅抑制包含 `@isTest` 的行的违规 — 测试类第 50 行上的 SOQL 查询仍然标记，因为第 50 行不包含 `@isTest`。要完全排除正则表达式规则中的测试文件，请使用：
```yaml
ignores:
  files:
    - "**/*Test.cls"
    - "**/*_Test.cls"
```

**`ignores.files` 是全局的** — 它影响所有引擎和所有规则。如果您需要为某些规则排除测试类，但其他规则不需要（例如，排除测试类 SOQL 规则，但仍扫描测试类中的 @AuraEnabled），请使用 **PMD 与 XPath** 为需要选择性排除的规则。PMD 的 XPath 可以按方法或按类结构化检查 `@Test = true()` — 正则表达式无法做到。

**Apex 规则应跳过测试类的决策指南：**
- 如果模式是结构化的（方法调用、注解、嵌套）→ 使用 PMD。XPath 原生处理测试类排除。
- 如果模式是纯文本，并且所有正则表达式规则都应跳过测试 → 使用正则 + `ignores.files`。
- 如果您有混合（一些规则跳过测试，其他不跳）→ 使用 PMD 进行测试敏感的规则，正则表达式用于其他规则。

---

## 工作流程

### 当用户选择代码（IDE 选择）

当用户在编辑器中突出显示代码块并要求“捕获这个”、“标记此模式”、“为这个创建规则”或类似操作时：

1. **选择就是您的阳性样本。** 不要问“此规则应标记什么模式？” — 用户已经展示了。不要从零开始编写新的样本。
2. **识别选择中的结构化内容与偶然性内容**：
   - 结构化（值得规则）：方法调用、循环模式、缺失的关键字、嵌套
   - 偶然性（忽略）：特定的变量名、字符串值、参数数量
   - 如果有歧义，问一个问题： “规则应捕获所有 `System.debug` 调用，还是仅捕获没有 LoggingLevel 参数的调用？”
3. **实际文件 ast-dump** 用户打开的文件（不是新的样本文件）：
   ```bash
   sf code-analyzer ast-dump --file <the-open-file.cls> --output-file <ast.xml>
   ```
4. **在 AST 输出中找到选择** — 定位与突出显示行对应的节点。这些是您的目标节点。
5. **泛化 XPath** — 编写匹配结构化模式而不是特定实例的 XPath。用通配符替换特定变量名，保留结构化节点和区分属性。
6. **继续标准工作流程**（负样本、创建规则、验证、测试阳性 + 负面）。

**示例流程：**
- 用户选择： `Database.query('SELECT Id FROM ' + objectName)`
- 结构化模式： `Database.query` 调用（动态 SOQL）
- 偶然性：特定字符串连接内部
- 引擎：PMD（结构化调用检测）
- XPath：`//MethodCallExpression[@FullMethodName='Database.query']`
- 不是：正则表达式匹配 `Database.query`（会遗漏多行，匹配注释）

**示例流程（块选择）：**
- 用户选择一个包含循环内 SOQL 的 5 行块
- 结构化：SOQL 查询作为循环体的后代
- 偶然性：特定查询字段、变量名
- 引擎：PMD
- ast-dump 打开文件 → 查找 ForEachStatement + SoqlExpression 在体内
- XPath：`//ForEachStatement/BlockStatement//SoqlExpression`

---

### 对于正则表达式规则

1. **编写阳性样本**（5-10 行）展示违规。在项目工作区内编写样本文件（例如，在项目根目录的临时 `samples/` 目录中），以便代码分析器可以定位它们。
2. **编写一个单独的负样本文件** — 看起来相似但绝不能被标记的代码。在创建规则之前，在脑海中测试您的正则表达式对此文件的匹配。
3. **构建和创建规则** — 阅读 `references/regex-rule-schema.md` 获取完整模式，然后运行脚本：
   ```bash
   node "<skill_dir>/scripts/create-regex-rule.js" \
     --name "<RuleName>" --regex "<pattern>" --description "<desc>" \
     --severity <1-5> --file-extensions ".cls,.trigger"
   ```
   **始终使用脚本。** 不要手动将正则表达式模式写入 `code-analyzer.yml` — YAML 中的正则表达式字符（引号、反斜杠、大括号）会导致解析失败。脚本正确处理序列化。
4. **验证** — `sf code-analyzer rules --rule-selector regex:<RuleName>`
5. **测试阳性** — `sf code-analyzer run --rule-selector regex:<RuleName> --target <violation-sample>` — 必须找到违规
6. **测试负面** — `sf code-analyzer run --rule-selector regex:<RuleName> --target <clean-sample>` — 必须找到 0 个违规。如果它标记了干净代码，则您的正则表达式过于宽泛 — 回去收紧模式。
7. **迭代** 如果测试失败（调整正则表达式、添加 `regex_ignore`、缩小扩展名）
8. **清理** — 删除您创建的所有样本文件。不要在用户的项目中留下临时测试 fixture。

### 对于 PMD/XPath 规则（Apex）

1. **编写一个最小的示例**（5-10行）来演示违规行为。在项目工作区中编写示例文件（例如，在项目根目录下创建一个临时的 `samples/` 目录），以便代码分析器可以定位它们。**在正负测试都通过后，删除您创建的所有示例文件**——包括原始示例文件和测试过程中生成的任何副本。不要在用户的项目的留临时测试设置。对于基于循环的规则，正例示例必须包含所有3种Apex循环类型（`for-each`、传统 `for` 和 `while`）——省略任何循环类型意味着XPath不会针对它进行验证，并且可能会无声地遗漏违规行为。

2. **强制执行：转储AST**——`sf code-analyzer ast-dump --file <sample.cls> --output-file <ast.xml>`——这一步不是可选的。即使您“已经知道”节点名称，也不要跳过它。运行它，阅读输出，确认确切的节点名称和属性。

3. **阅读AST输出**——从实际的ast-dump输出中识别目标节点及其属性（而不是从内存中）。使用 `references/apex-ast-reference.md` 和 `references/xpath-patterns.md` 作为补充上下文。

4. **编写XPath**——定位具有区分属性的最小稳定节点。您XPath中的每个节点名称都必须与您刚刚阅读的ast-dump输出完全一致。故意使用 `/Child`（直接子节点）与 `//Descendant`——检查ast-dump以了解哪些节点是兄弟节点与嵌套。

5. **在创建规则之前：编写一个单独的负例示例文件**（5-10行）显示正确的代码，并且不得被标记。这必须是一个与正例示例不同的文件——不要将正例和负例案例合并到一个文件中。对于基于循环的规则，包括 `for (x : [SELECT...])` 习语。对负例示例文件也运行 `sf code-analyzer ast-dump`。阅读输出并跟踪您的XPath——确认它不匹配负例AST中的任何节点。如果它会匹配，请返回第4步并收紧XPath，然后再继续。不要跳过这一步或将其推迟到规则创建之后。负例文件将在第9步用于明确的零违规确认。

6. **创建规则**——运行脚本：
   ```bash
   node "<skill_dir>/scripts/create-pmd-rule.js" \
     --name "<RuleName>" --xpath "<expression>" --message "<msg>" \
     --language apex --priority <1-5>
   ```

7. **验证**——`sf code-analyzer rules --rule-selector pmd:<RuleName>`

8. **测试正例**——`sf code-analyzer run --rule-selector pmd:<RuleName> --target <violation-sample.cls>`——必须找到违规行为

9. **测试负例**——`sf code-analyzer run --rule-selector pmd:<RuleName> --target <clean-sample.cls>`——必须找到0个违规行为。如果它标记了干净的代码，则您的XPath过于宽泛——返回第4步。

10. **如果测试失败，则迭代**（重新检查AST、调整XPath、检查节点名称）

11. **清理**——删除您创建的所有示例文件（正例和负例示例，以及任何为测试生成的ast-dump输出文件）。不要在用户的项目的留临时测试设置。

### 对于PMD/XPath规则（元数据XML）

1. **确定元数据文件类型**（字段、权限集、配置文件、流程等）

2. **转储XML AST**——`sf code-analyzer ast-dump --file <file>-meta.xml --language xml --output-file <ast.xml>`。如果ast-dump因错误而失败（例如，`"XmlEncoding is not a valid XML name"`），则回退到直接读取原始XML文件——XML DOM结构是元数据文件的AST（您在文件中看到的内容是PMD看到的）。阅读文件，注意元素名称、嵌套和文本内容。

3. **阅读DOM结构**——从ast-dump输出或原始文件确认元素名称、嵌套和文本内容。仅使用 `references/metadata-xml-rules.md` 作为补充上下文。

4. **为PMD 7编写XPath**——元数据XML XPath的关键规则：
   - 所有元素匹配必须使用 `local-name()='ElementName'`（命名空间块裸名称）
   - **文本内容匹配必须使用 `@Text` 属性**（不是 `text()`——`text()` 函数在PMD 7的XML语言中不起作用）。示例：`//*[@Text='ModifyAllData']`
   - 使用 `../..` 从文本节点向上导航到父元素（文本节点→元素→父元素）
   - 通过父节点的 `.//*[@Text='value']` 检查兄弟条件
   - 参考 `references/metadata-xml-rules.md` 获取完整的PMD 7 XPath模式

5. **配置文件扩展名**——PMD的XML语言默认仅处理 `.xml`。Salesforce元数据文件使用复合扩展名（`.permissionset-meta.xml`、`.field-meta.xml` 等），但 `path.extname()` 从这些文件返回 `.xml`，所以 `.xml` 足够：
   ```yaml
   engines:
     pmd:
       file_extensions:
         xml: [".xml"]
   ```
   不要添加复合扩展名，如 `.permissionset-meta.xml`——代码分析器的验证器拒绝它们（`/^[.][a-zA-Z0-9]+$/` 模式）。只需 `.xml` 自动涵盖所有Salesforce元数据文件。

6. **编写一个单独的负例示例文件**——与Apex规则相同：创建一个正确的元数据文件，并且不得被标记。在创建规则之前验证XPath是否不匹配它。正例和负例示例应该是工作区中的 `.xml` 扩展名文件，以便PMD可以直接扫描它们。

7. **创建规则**——运行脚本：
   ```bash
   node "<skill_dir>/scripts/create-pmd-rule.js" \
     --name "<RuleName>" --xpath "<expression>" --message "<msg>" \
     --language xml --priority <1-5>
   ```

8. **验证**——`sf code-analyzer rules --rule-selector pmd:<RuleName>`

9. **测试正例**——`sf code-analyzer run --rule-selector pmd:<RuleName> --target <violation-sample>.xml`——必须找到违规行为

10. **测试负例**——`sf code-analyzer run --rule-selector pmd:<RuleName> --target <clean-sample>.xml`——必须找到0个违规行为

11. **如果测试失败，则迭代**（检查 `@Text` vs `text()`，验证 `local-name()` 使用，检查文件扩展名配置）

12. **清理**——删除您创建的所有示例文件（正例和负例示例，以及为测试生成的任何 `.xml` 副本）。不要在用户的项目的留临时测试设置。

### 对于ESLint规则（LWC/JavaScript/TypeScript）

#### ESLint发现工作流（首先阅读）

ESLint有200多个内置规则，还有来自插件的数千个更多规则。在尝试创建自定义插件之前，请检查是否存在内置规则。发现工作流是：

1. **第一级（内置规则）**——70%的请求
   - 运行：`sf code-analyzer rules --rule-selector eslint`
   - 搜索关键字（例如，“console”、“未使用”、“相等”）
   - 检查LWC插件规则（`@lwc/lwc/*`）
   - 如果找到：配置并停止

2. **第二级（可配置规则）**——20%的请求
   - 模式是“禁止函数X”？→ `no-restricted-globals`
   - 模式是“禁止语法Y”？→ `no-restricted-syntax`
   - 模式是“禁止属性Z”？→ `no-restricted-properties`
   - 如果适用：配置并停止

3. **第三级（自定义插件）**——10%的请求
   - 仅用于特定领域的多节点模式
   - 需要Node.js代码、测试、`meta.docs`元数据
   - 参考：`references/eslint-custom-plugins.md`

**参考：** `references/eslint-rules-discovery.md` 获取完整的发现指南和示例。

---

0. **强制执行：首先运行ESLint发现工作流。** 90%的ESLint请求通过内置规则（第一级）或可配置规则（如 `no-restricted-syntax`，第二级）解决。创建自定义插件（第三级）是最后的选择。在继续之前：

   a) **运行：** `sf code-analyzer rules --rule-selector eslint`
   b) **搜索** 输出中的用户请求的关键字（例如，“console”、“相等”、“未使用”）
   c) **检查LWC插件规则：** 在输出中grep `@lwc/lwc/`
   d) **如果找到：** 配置它（参考 `references/eslint-rules-discovery.md`）并停止。不要创建自定义插件。
   e) **如果没有找到：** 检查是否可以使用 `no-restricted-globals`、`no-restricted-syntax` 或 `no-restricted-properties` 表达模式（第二级）。
   f) **只有在第一级或第二级解决方案不存在时：** 才继续自定义插件创建。

   **验证：** 配置后，运行 `sf code-analyzer rules --rule-selector eslint:<ruleName>` 确认它出现。如果它没有出现，配置是错误的。

   **跳过此发现工作流并创建自定义插件时内置规则存在是技能失败**，无论自定义插件是否工作。

   **内置ESLint规则与可配置ESLint规则：** 代码分析器在其基本配置中捆绑了ESLint规则的子集。像 `no-restricted-globals`、`no-restricted-syntax` 和 `no-restricted-properties` 这样的规则是核心ESLint规则，但除非您在 `eslint.config.js` 中启用它们，否则它们不会激活。它们仅在您配置它们之后才会出现在 `sf code-analyzer rules` 输出中。**始终验证**（第4步）以确认规则实际加载——不要假设一个规则存在，仅仅因为它是一个核心ESLint规则。

1. **安装ESLint插件**（如果使用内置/核心ESLint规则则跳过）——`npm install --save-dev eslint-plugin-<name>`
2. **创建/更新 `eslint.config.js`** —— 添加插件和规则配置（或仅用 `"error"` 严重性启用内置规则）。**文件必须在配置 `engines.eslint.eslint_config_file` 在 `code-analyzer.yml` 之前存在**——代码分析器验证路径，如果文件缺失则失败。
3. **配置代码分析器** —— 在 `code-analyzer.yml` 中设置 `engines.eslint.eslint_config_file`。在文件存在后执行此操作。
4. **验证** —— `sf code-analyzer rules --rule-selector eslint:<ruleName>`。如果规则不出现，配置是错误的——不要继续测试。检查：(a) `eslint.config.js` 文件是否在正确位置？(b) 插件是否有 `meta.docs.description` 和 `meta.docs.url`？(c) 规则是否已弃用？代码分析器会无声地排除已弃用的规则。
5. **编写一个测试示例文件** 在工作区中（例如，`lwc/testSample/testSample.js`）演示违规行为
6. **测试正例** —— `sf code-analyzer run --rule-selector eslint:<ruleName> --target <test-sample>`——必须找到违规行为
7. **测试负例** —— 运行针对现有的干净LWC文件——必须找到0个违规行为
8. **清理** —— 删除所有示例文件及其父目录（LWC需要每个组件一个文件夹）。使用 `rm -rf <directory>`，而不是 `rm <file>`。不要在用户的项目的留空目录或临时测试设置。
9. 参考 `references/eslint-custom-plugins.md` 获取完整指南

### 没有自定义插件的常见ESLint模式

对于 `no-restricted-globals`、`no-restricted-syntax` 和 `no-restricted-properties` 的配置示例，请参阅 `<skill_dir>/references/eslint-custom-plugins.md`——“没有自定义插件禁止API”部分。

### ESLint发现示例

**示例1：内置规则（第一级）**
- 用户：“在LWC中禁止console.log”
- 发现：`sf code-analyzer rules --rule-selector eslint | grep console` → 找到 `no-console`
- 操作：在 eslint.config.js 中启用 `no-console`
- 结果：2分钟内完成（不需要自定义插件）

**示例2：可配置规则（第二级）**
- 用户：“在LWC中禁止setTimeout”
- 发现：没有内置的 `no-setTimeout` 规则
- 操作：使用 `no-restricted-globals` 并使用自定义消息
- 结果：5分钟内完成（不需要自定义插件）

**示例3：LWC插件规则（第一级）**
- 用户：“禁止innerHTML以防止XSS”
- 发现：`@lwc/lwc/no-inner-html` 已存在
- 操作：在配置中启用 `@lwc/lwc/no-inner-html`
- 结果：2分钟内完成（不需要自定义插件）

**示例4：自定义插件合理（第三级）**
- 用户：“标记没有错误处理的命令式Apex调用”
- 发现：没有此模式的内置规则
- 分析：模式需要检查 `import` + `.then()` 而没有 `.catch()` —— 多节点遍历
- 操作：创建具有访问者模式的自定义插件
- 结果：自定义插件是合理的（20+分钟工作）

参考 `references/eslint-rules-discovery.md` 获取完整的发现工作流。

---

### 覆盖内置规则阈值

要自定义现有规则的严重性或属性，而无需编写新规则：

1. **创建自定义规则集**——引用内置规则并覆盖
2. **添加到配置**——`engines.pmd.custom_rulesets` 在 `code-analyzer.yml` 中
3. 参考 `references/advanced-pmd-patterns.md` 获取覆盖语法和常见示例

---

## 多规则请求

当用户一次请求多个规则（例如，“为AppExchange审查创建5个规则”）时，请遵循此协议：

### 第一步：首先规划引擎分配

在创建任何规则之前，列出所有请求的规则及其引擎分配。向用户展示此计划：

```text
规则计划：
1. RequireUserMode → PMD/XPath（需要通过AST排除测试类）
2. NoHardcodedIds → Regex（文本模式，不需要结构上下文）
3. AuraEnabledCacheable → PMD/XPath（需要注解+DML结构检查）
4. CustomFieldDescription → PMD/XML（元数据治理）
5. NoSetTimeout → ESLint（JavaScript模式）
```

引擎分配的关键决策因素：
- 规则是否需要**选择性地排除测试类**？→ PMD（XPath可以检查 `@Test = true()`）
- 它是否是一个**纯文本模式**，没有结构上下文？→ Regex
- 它是否需要**理解代码结构**（注解、嵌套、DML）？→ PMD
- 它是否是**JavaScript/LWC**？→ ESLint（永远不会Regex）
- 它是否是**元数据XML**？→ PMD with `language="xml"`

### 第二步：一次创建一个规则，按顺序

通过完整的创建流程（创建→验证→测试正例→测试负例→确认工作）创建每个规则，然后再开始下一个规则。不要批量创建规则——如果有一个失败，它会破坏后续所有规则的配置。

**创建顺序：**
1. Regex规则首先（最快，依赖最少）
2. PMD Apex规则（每个规则需要ast-dump）
3. PMD XML规则（可能共享一个规则集文件）
4. ESLint规则最后（需要npm/config设置）

### 第三步：多个PMD规则可以共享一个规则集文件

在创建多个PMD规则时，使用 `create-pmd-rule.js` 脚本为第一个规则（它创建规则集XML文件）。对于进入同一规则集文件的后续PMD规则，您可以手动将它们添加到现有的XML文件——这是“永远不要手动编辑”规则的唯一例外。脚本始终创建一个新文件；将规则添加到现有文件需要直接编辑XML。

### 不要做的事情

- 不要重写整个 `code-analyzer.yml` 来重新组织它
- 不要并行创建所有规则，然后一次验证所有规则
- 不要创建一个XPath未经验证的PMD规则（来自参考文档）——每个模式ast-dump
- 不要在一步中混合引擎类型（例如，同时创建regex和PMD规则）
- 不要在文件存在之前将 `engines.eslint.eslint_config_file` 添加到 `code-analyzer.yml`

| 规则 | 理由 |
|------|-----------|
| 规则名称必须匹配 `/^[A-Za-z@][A-Za-z_0-9@\-/]*$/` | 代码分析器验证拒绝其他规则 |
| 正则表达式必须为 `/pattern/flags` 格式 | 需要JavaScript的正则字面量表示法 |
| 文件扩展名必须以 `.` 开头 | 验证强制 `/^([.][a-zA-Z0-9-_]+)+$/` |
| 创建后始终验证 | `sf code-analyzer rules --rule-selector <engine>:<name>` 捕获配置错误 |
| 始终针对示例代码测试 | 在完整扫描前捕获XPath/正则表达式不匹配 |
| 在XPath中使用 `@FullMethodName` 进行方法调用 | 比单独使用 `@Image` 或 `@MethodName` 更可靠 |
| **绝对不要跳过 `ast-dump`** | 运行 `ast-dump`，阅读输出，然后编写XPath。没有例外——即使是“明显”的模式。在没有ast-dump验证的情况下从内存中使用节点名称是技能失败的。 |
| **PMD 7 布尔属性：使用 `= false()` XPath函数** | 在PMD 7中，布尔属性如 `@WithSharing`、`@Abstract`、`@Final` 始终存在于节点上（永远不会缺失）。与 `= false()`（XPath布尔函数）进行比较，而不是字符串 `'false'`。`@WithSharing = false()` 有效。`@WithSharing='false'`（字符串）无效。`not(@WithSharing)` 无效（属性始终存在）。 |
| 项目根目录下的 `code-analyzer.yml` | CLI自动发现——将其放置在其他位置会导致规则作者的静默失败 |
| **XML规则必须使用 `local-name()`** | Salesforce元数据命名空间会破坏裸元素名称 |
| **XML文本匹配必须使用 `@Text` 属性** | `text()` 在PMD 7的XML语言中无效。使用 `//*[@Text='value']` 匹配文本内容，然后使用 `../..` 向上导航以到达父元素。 |
| **`@Text` 存在于子文本节点上，而不是元素上** | `//*[local-name()='apiVersion'][@Text < 60]` → 错误（0个匹配）。`//*[local-name()='apiVersion']/*[number(@Text) < 60]` → 正确。`/*` 导航到子文本节点。对于精确匹配模式，`//*[@Text='value']` 有效，因为它会搜索所有节点包括文本节点。但当你首先通过 `local-name()` 针对特定元素时，必须使用 `/*[@Text...]` 来到达其文本子节点。 |
| **XML规则需要 `file_extensions` 配置** | PMD 默认仅扫描 `.xml`——在 `engines.pmd` 下添加 `file_extensions: { xml: [".xml"] }`。不要添加复合扩展名（`.permissionset-meta.xml`）——验证器会拒绝它们，而 `.xml` 单独已经涵盖了所有Salesforce元数据文件。 |
| 正则表达式中的命名捕获组 `(?<target>...)` | 将违规高亮限制在仅捕获的部分 |
| **Salesforce ID 以 `0` 开头，长度为15或18个字符** | 使用 `/['"](?<target>0[a-zA-Z0-9]{14}(?:[a-zA-Z0-9]{3})?)['\"]/g` — 不要使用 `{15,18}`，它还会匹配16/17个字符的字符串，并在普通单词如 `'BusinessAccount'` 上产生误报 |
| **`regex_ignore` 是按行，不是按文件** | 它仅跳过匹配忽略模式的行。它不会排除整个文件或类。测试类第10行上的硬编码ID仍然会报错，除非该特定行包含忽略模式（例如 `@isTest`）。 |
| **始终使用脚本创建规则** | 不要手动编辑 `code-analyzer.yml` 中的正则表达式规则——YAML中的正则表达式中的引号/反斜杠会导致解析失败。`create-regex-rule.js` 脚本正确处理序列化。 |
| 通过 `<rule ref="...">` 覆盖内置规则 | 修改阈值而不编写新规则 |
| **绝对不要使用正则表达式处理 JS/LWC/TS 文件** | 正则表达式无法区分代码和注释/字符串——始终使用ESLint处理JavaScript模式 |
| **在编写自定义规则前检查内置ESLint规则** | `no-console`、`no-debugger`、`no-alert`、`eqeqeq`、`no-eval` 等规则已存在——只需在配置中启用它们 |

---

## 注意事项

| 问题 | 解决方案 |
|-------|------------|
| 未运行 ast-dump 编写XPath | **始终先运行 ast-dump。** 即使规则有效，跳过 ast-dump 也是流程失败。节点名在不同PMD版本之间会变化，无法猜测。 |
| SOQL循环规则标记 `for (x : [SELECT...])` | 使用 `//ForEachStatement/BlockStatement//SoqlExpression`（范围到主体）。可迭代SOQL是 `ForEachStatement` 的直接子代，与 `BlockStatement` 一起出现——`//ForEachStatement//SoqlExpression` 会将其作为误报匹配。 |
| 用于JS/LWC/TS模式的正则表达式 | **绝对不要使用正则表达式处理JavaScript文件。** 正则表达式无法区分代码和JS中的注释/字符串。始终使用ESLint——首先检查是否存在内置规则（例如 `no-console`）。 |
| XPath返回0个匹配（XML元数据） | 三个常见原因：(1) 忘记 `local-name()`——命名空间会阻止裸元素名称。(2) 使用 `text()='value'`——在PMD 7中无效。使用 `@Text='value'` 代替。(3) 将 `[@Text]` 谓词放在元素上——`@Text` 存在于子文本节点上。使用 `/*[@Text...]` 到达它们。 |
| 将正则表达式规则内联写入 `code-analyzer.yml` — YAML解析错误 | **始终使用 `create-regex-rule.js`**——YAML中的引号和反斜杠会导致转义失败。不要手动将正则表达式写入配置文件。 |
| `regex_ignore` 不会排除测试类 | `regex_ignore` 是**按行**的。测试类第50行上的SOQL查询会报错，因为第50行不包含 `@isTest`。对于文件级排除：使用 `ignores.files`（全局）或 PMD XPath `[not(ancestor::UserClass[ModifierNode[@Test = true()]])]`（按规则）。 |
| XPath `@WithSharing='false'` 或 `not(@WithSharing)` 不工作 | PMD 7 布尔属性（`@WithSharing`、`@Abstract`、`@Final`）始终存在。字符串 `='false'` 不匹配（它是布尔值）。`not(@attr)` 不工作（属性始终存在）。使用XPath布尔函数：`@WithSharing = false()`。 |
| 基于循环的规则仅覆盖 `ForEachStatement` | Apex有三种循环类型：`ForEachStatement`、`ForLoopStatement`、`WhileLoopStatement`。所有三种都必须在XPath中——遗漏任何一种都会造成静默覆盖缺口。 |
| 脚本运行后重写 `code-analyzer.yml` — YAML解析错误 | **绝对不要手动重写文件**。仅作为新条目添加顶级配置块（如 `ignores.files`）——不要触碰脚本生成的 `engines.regex.custom_rules` 部分。 |
| 一次性创建多个规则——一个失败会中断所有后续规则 | **逐个顺序创建规则**。完成每个规则的完整工作流（创建 → 验证 → 测试）后，再开始下一个。 |

有关更多诊断信息（错误严重性、Java未找到、ESLint配置路径、元数据文件类型范围等），请参阅 `<skill_dir>/references/troubleshooting.md`。

---

## 跨技能集成

| 需要 | 委托给 | 原因 |
|------|-------------|--------|
| 创建规则后运行完整扫描 | `dx-code-analyzer-run` | 扫描执行和结果呈现 |
| 安装代码分析器/修复先决条件 | `dx-code-analyzer-configure` | 设置和故障排除 |
| 解释现有内置规则 | `dx-code-analyzer-run` | 规则描述和文档查找 |
| 编辑 `code-analyzer.yml` 以设置引擎配置 | `dx-code-analyzer-configure` | 配置管理 |

---

## 脚本执行

`<skill_dir>` 是包含此 `SKILL.md` 文件的目录的绝对路径。

所有脚本都捆绑在包含此 `SKILL.md` 文件的目录的 `scripts/` 子目录中。使用该目录的绝对路径——不要使用 `./scripts/`，因为它相对于当前工作目录解析，而不是技能目录。

```bash
node "<skill_dir>/scripts/create-regex-rule.js" \
  --name "RuleName" --regex "/pattern/flags" ...
```

**不要：**
- 自己编造或生成脚本代码
- 使用裸相对路径，如 `node scripts/create-regex-rule.js`（不会从用户CWD解析）
- 使用heredocs或内联脚本内容
- 跳过解析 `<skill_dir>`——首先找到绝对路径

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `references/regex-rule-schema.md` | 构建正则表达式规则——完整字段参考、验证规则、多规则示例 |
| `references/xpath-patterns.md` | 为Apex编写XPath——模式类别索引、语法参考和AST节点词汇表 |
| `references/xpath-patterns-governor-limits.md` | 循环中的SOQL/DML、循环中的数据库方法 |
| `references/xpath-patterns-method-calls.md` | 禁止方法和注解模式（@AuraEnabled、@future、@IsTest）的XPath模式 |
| `references/xpath-patterns-security.md` | 分享声明、SOQL安全、硬编码ID的XPath模式 |
| `references/xpath-patterns-structure.md` | 代码结构、测试质量、命名约定的XPath模式 |
| `references/apex-ast-reference.md` | 阅读Apex AST转储——节点层次结构、修饰符属性、关键节点类型 |
| `references/metadata-xml-rules.md` | 为元数据XML编写规则——命名空间解决方案、常见结构、XPath模式 |
| `references/advanced-pmd-patterns.md` | 多规则规则集、覆盖内置规则、排除模式、Java规则、跨项目共享 |
| `references/eslint-rules-discovery.md` | **任何ESLint请求前首先阅读**——发现工作流、内置规则、Tier 1-3索引 |
| `references/eslint-tier2-configurable.md` | ESLint Tier 2：no-restricted-globals、no-restricted-syntax、no-restricted-properties模式 |
| `references/eslint-tier3-custom-plugins.md` | ESLint Tier 3：何时创建自定义插件 + 所有级别的完整示例 |
| `references/eslint-custom-plugins.md` | 创建自定义ESLint插件——仅在使用发现工作流确认不存在内置或可配置规则（Tier 3）后 |
| `references/troubleshooting.md` | 验证或测试失败时——按引擎类型进行错误诊断 |
| `assets/pmd-ruleset-template.xml` | PMD XML骨架，带有 `create-pmd-rule` 脚本的占位符 |
| `examples/regex-examples.md` | 6个解决社区报告问题的真实世界正则表达式规则 |
| `examples/xpath-examples.md` | 6个Apex真实世界XPath规则，带AST上下文和逐步创建步骤 |
| `examples/metadata-xml-examples.md` | 6个真实世界元数据XML规则的索引（权限、描述、API版本、流程） |
| `examples/metadata-xml-example-permissions.md` | 元数据示例：ModifyAllData/ViewAllData、配置文件中的字段权限 |
| `examples/metadata-xml-example-fields-api.md` | 元数据示例：自定义字段描述、最低API版本 |
| `examples/metadata-xml-example-flows.md` | 元数据示例：流程自动布局、流程错误处理 |
