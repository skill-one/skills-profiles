# ast-grep 代码搜索

## 概述

这项技能能够将自然语言查询翻译成 ast-grep 规则，用于结构化代码搜索。ast-grep 使用抽象语法树（AST）模式来根据代码结构进行匹配，而不是仅仅基于文本，从而能够在大型代码库中进行强大而精确的代码搜索。

## 何时使用这项技能

当用户需要：

- 使用结构化匹配来搜索代码模式（例如，“查找所有没有错误处理的异步函数”）
- 定位特定的语言结构（例如，“查找所有具有特定参数的函数调用”）
- 执行需要理解代码结构而不是仅仅基于文本的搜索
- 查找具有特定 AST 特征的代码
- 执行传统文本搜索无法处理的复杂代码查询

时，使用这项技能。

## 一般工作流程

遵循以下流程来帮助用户编写有效的 ast-grep 规则：

### 第 1 步：理解查询

清楚地理解用户想要查找什么。如有必要，请提出澄清性问题：

- 他们正在寻找什么样的特定代码模式或结构？
- 哪种编程语言？
- 是否需要考虑特定的边缘情况或变化？
- 匹配中应该包含或排除哪些内容？

### 第 2 步：创建示例代码

编写一个简单的代码片段来表示用户想要匹配的内容。将此内容保存到一个临时文件中进行测试。

**示例：**

如果搜索“使用 await 的异步函数”，创建一个测试文件：

```javascript
// test_example.js
async function example() {
  const result = await fetchData();
  return result;
}
```

### 第 3 步：编写 ast-grep 规则

将模式翻译成 ast-grep 规则。从简单开始，根据需要增加复杂性。

**关键原则：**

- 对于关系规则（`inside`、`has`），始终使用 `stopBy: end` 以确保搜索到达方向的末尾
- 使用 `pattern` 匹配简单结构
- 使用 `kind` 与 `has`/`inside` 匹配复杂结构
- 使用 `all`、`any` 或 `not` 将复杂查询分解为更小的子规则

**示例规则文件（test_rule.yml）：**

```yaml
id: async-with-await
language: javascript
rule:
  kind: function_declaration
  has:
    pattern: await $EXPR
    stopBy: end
```

有关详细的规则文档，请参阅 `references/rule_reference.md`。

### 第 4 步：测试规则

使用 ast-grep CLI 来验证规则是否匹配示例代码。主要有两种方法：

**选项 A：使用内联规则（用于快速迭代）**

```bash
echo "async function test() { await fetch(); }" | ast-grep scan --inline-rules "id: test
language: javascript
rule:
  kind: function_declaration
  has:
    pattern: await \$EXPR
    stopBy: end" --stdin
```

**选项 B：使用规则文件（推荐用于复杂规则）**

```bash
ast-grep scan --rule test_rule.yml test_example.js
```

**如果没有匹配，进行调试：**

1. 简化规则（删除子规则）
2. 如果关系规则中未提供，添加 `stopBy: end`
3. 使用 `--debug-query` 来理解 AST 结构（见下文）
4. 检查语言对应的 `kind` 值是否正确
5. 对于 `run --pattern` 产生的零匹配（非规则），请参阅下文“零匹配？”提示

### 第 5 步：搜索代码库

一旦规则正确匹配示例代码，即可搜索实际的代码库：

**对于简单模式搜索：**

```bash
ast-grep run --pattern 'console.log($ARG)' --lang javascript /path/to/project
```

**对于基于规则的复杂搜索：**

```bash
ast-grep scan --rule my_rule.yml /path/to/project
```

**对于内联规则（无需创建文件）：**

```bash
ast-grep scan --inline-rules "id: my-rule
language: javascript
rule:
  pattern: \$PATTERN" /path/to/project
```

## ast-grep CLI 命令

### 检查代码结构（--debug-query）

将 AST 结构输出到理解代码是如何被解析的：

```bash
ast-grep run --pattern 'async function example() { await fetch(); }' \
  --lang javascript \
  --debug-query=cst
```

**可用格式：**

- `cst`：具体语法树（显示所有节点，包括标点符号）
- `ast`：抽象语法树（仅显示命名节点）
- `pattern`：显示 ast-grep 如何解释您的模式

**使用此功能的目的：**

- 找到节点的正确 `kind` 值
- 理解您想要匹配的代码结构
- 调试为什么模式不匹配

**示例：**

```bash
# 查看目标代码的结构
ast-grep run --pattern 'class User { constructor() {} }' \
  --lang javascript \
  --debug-query=cst

# 查看ast-grep如何解释您的模式
ast-grep run --pattern 'class $NAME { $$$BODY }' \
  --lang javascript \
  --debug-query=pattern
```

### 测试规则（使用 --stdin 扫描）

在不创建文件的情况下，使用规则对代码片段进行测试：

```bash
echo "const x = await fetch();" | ast-grep scan --inline-rules "id: test
language: javascript
rule:
  pattern: await \$EXPR" --stdin
```

**添加 --json 获取结构化输出：**

```bash
echo "const x = await fetch();" | ast-grep scan --inline-rules "..." --stdin --json
```

### 使用模式搜索（run）

基于模式的简单搜索，用于匹配单个 AST 节点：

```bash
# 基本模式搜索
ast-grep run --pattern 'console.log($ARG)' --lang javascript .

# 搜索特定文件
ast-grep run --pattern 'class $NAME' --lang python /path/to/project

# JSON 输出用于程序化使用
ast-grep run --pattern 'function $NAME($$$)' --lang javascript --json .
```

**何时使用：**

- 简单、单个节点的匹配
- 快速搜索，无需复杂逻辑
- 当您不需要关系规则（inside/has）时

### 读取 --json 输出

`--json` 打印一个裸 JSON **数组**的匹配项（没有 `matches` 包装）。对于模式 `foo($ARG, $$$REST)`：

```json
[{
  "text": "foo(\"value\", 1, 2)",
  "file": "src/app.js",
  "range": { "start": { "line": 41, "column": 10 }, "end": { "line": 41, "column": 27 } },
  "metaVariables": {
    "single": { "ARG": { "text": "\"value\"" } },
    "multi": { "REST": [ { "text": "1" }, { "text": "2" } ] }
  }
}]
```

`scan --json` 使用相同的模式。

（每个匹配项还包括 `lines` 和 `language`。）`range.start.line` 是 0-based。命名 metavariables（`$ARG`）位于 `single`，列表 metavariables（`$$$REST`）作为列表位于 `multi`（如果未捕获任何内容则为空）。使用 jq 提取：

```bash
ast-grep run --pattern 'foo($ARG)' --lang javascript --json . \
  | jq -r '.[] | "\(.file):\(.range.start.line + 1): \(.metaVariables.single.ARG.text)"'
```

### 使用规则搜索（scan）

基于 YAML 规则的搜索，用于复杂的结构化查询：

```bash
# 使用规则文件
ast-grep scan --rule my_rule.yml /path/to/project

# 使用内联规则
ast-grep scan --inline-rules "id: find-async
language: javascript
rule:
  kind: function_declaration
  has:
    pattern: await \$EXPR
    stopBy: end" /path/to/project

# JSON 输出
ast-grep scan --rule my_rule.yml --json /path/to/project
```

**何时使用：**

- 复杂的结构化搜索
- 关系规则（inside、has、precedes、follows）
- 组合逻辑（all、any、not）
- 当您需要完整 YAML 规则的强大功能时

**提示：** 对于关系规则（inside/has），始终添加 `stopBy: end` 以确保完整遍历。

## 编写有效规则的小技巧

### 始终使用 stopBy: end

对于关系规则，除非有特定原因不使用，否则始终使用 `stopBy: end`：

```yaml
has:
  pattern: await $EXPR
  stopBy: end
```

这确保搜索遍历整个子树，而不是在第一个不匹配的节点处停止。

### 从简单开始，然后增加复杂性

从最简单的可能规则开始：

1. 首先尝试 `pattern`
2. 如果不起作用，尝试 `kind` 匹配节点类型
3. 根据需要添加关系规则（`has`、`inside`）
4. 使用组合规则（`all`、`any`、`not`）进行复杂逻辑组合

### 使用正确的规则类型

- **Pattern**：用于简单、直接的代码匹配（例如，`console.log($ARG)`）
- **Kind + 关系**：用于复杂结构（例如，“包含 await 的函数”）
- **组合**：用于逻辑组合（例如，“具有 await 但不在 try-catch 中的函数”）

### 使用 AST 检查进行调试

当规则不匹配时：

1. 使用 `--debug-query=cst` 查看实际的 AST 结构
2. 检查 metavariables 是否被正确检测
3. 验证节点 `kind` 是否与预期一致
4. 确保关系规则在正确的方向上搜索

### 零匹配？模式匹配整个 AST 节点

`run --pattern` 匹配完整的 AST 节点，而不是文本子字符串，因此零匹配可能意味着“代码不存在”或“模式具有错误的节点形状”：

- 限定路径是整个节点：`env::var($ENV)` 不匹配 `std::env::var("X")`。尝试裸形式和完全限定形式，或使用 `$$$` 吸收额外的中间节点。
- 要区分它们：在已知包含代码的片段上测试模式，并使用 `--debug-query=pattern` 检查 ast-grep 如何解析它（适用于 `run`，不仅仅是 `scan`/rules）。对于来自规则的零匹配，请遵循第 4 步调试清单。

### 内联规则中的转义

在使用 `--inline-rules` 时，在 shell 命令中转义 metavariables：

- 使用 `\$VAR` 而不是 `$VAR`（shell 将 `$` 解释为变量）
- 或使用单引号：`'$VAR'` 在大多数 shell 中有效

**示例：**

```bash
# 正确：转义 $
ast-grep scan --inline-rules "rule: {pattern: 'console.log(\$ARG)'}" .

# 或使用单引号
ast-grep scan --inline-rules 'rule: {pattern: "console.log($ARG)"}' .
```

## 常见用例

### 查找具有特定内容的函数

查找使用 await 的异步函数：

```bash
ast-grep scan --inline-rules "id: async-await
language: javascript
rule:
  all:
    - kind: function_declaration
    - has:
        pattern: await \$EXPR
        stopBy: end" /path/to/project
```

### 在特定上下文中查找代码

在类方法中查找 console.log：

```bash
ast-grep scan --inline-rules "id: console-in-class
language: javascript
rule:
  pattern: console.log(\$\$\$)
  inside:
    kind: method_definition
    stopBy: end" /path/to/project
```

### 查找缺少预期模式的代码

查找没有 try-catch 的异步函数：

```bash
ast-grep scan --inline-rules "id: async-no-trycatch
language: javascript
rule:
  all:
    - kind: function_declaration
    - has:
        pattern: await \$EXPR
        stopBy: end
    - not:
        has:
          pattern: try { \$\$\$ } catch (\$E) { \$\$\$ }
          stopBy: end" /path/to/project
```

## 资源

### references/

包含 ast-grep 规则语法的详细文档：

- `rule_reference.md`：涵盖原子规则、关系规则、组合规则和 metavariables 的全面 ast-grep 规则文档

当需要详细的规则语法信息时，加载这些参考。
