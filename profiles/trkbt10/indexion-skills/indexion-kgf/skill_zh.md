# indexion kgf

通过查看令牌、解析事件和提取的边来检查和调试 KGF 语言规范。

## 使用场景

- 用户想要调试 indexion 如何处理特定文件
- 用户正在开发或修改 KGF 规范
- 用户询问“indexion 如何解析这个文件？”
- 验证令牌化/解析是否正确工作
- **调试 grep 模式**：当 grep 模式不匹配时，使用 `kgf tokens` 查看实际令牌类型

## 子命令

### `indexion kgf list` — 列出已安装的规范

```bash
indexion kgf list
```

### `indexion kgf update` — 更新所有规范

从 GitHub 下载最新的规范。

```bash
indexion kgf update
```

### `indexion kgf add` — 安装单个规范

```bash
indexion kgf add <spec-name>
```

### `indexion kgf inspect` — 完整检查

一次显示令牌、事件和边。

```bash
indexion kgf inspect <file>
indexion kgf inspect --spec=typescript src/app.ts
```

### `indexion kgf tokens` — 仅令牌化

显示文件如何被令牌化。

```bash
indexion kgf tokens <file>
indexion kgf tokens --spec=go-mod go.mod
```

### `indexion kgf events` — 仅解析事件

显示从令牌生成的解析事件。

```bash
indexion kgf events <file>
```

### `indexion kgf edges` — 仅提取的边

显示从文件提取的依赖边。

```bash
indexion kgf edges <file>
indexion kgf edges fixtures/project/npm/package.json
```

## 选项

| 选项 | 默认值 | 描述 |
|------|--------|------|
| `--spec=NAME` | auto-detect | 要使用的 KGF 规范名称 |
| `--kgf-dir=PATH` | kgfs | KGF 规范目录 |

## 与 grep 的关系

`indexion grep` 在底层使用 KGF 令牌化。模式别名 (`pub` → `KW_pub`) 来自 KGF 规范的 `=== lex` 部分。

当 grep 模式不符合预期时：

```bash
# 1. 查看文件的实际令牌
indexion kgf tokens src/config/paths.mbt

# 2. 检查哪些令牌类型存在
indexion kgf tokens src/config/paths.mbt | head -20

# 3. 然后调整你的 grep 模式以匹配实际令牌类型
indexion grep "KW_pub KW_fn Ident" src/config/paths.mbt
```

常见的令牌类型（MoonBit）：
- `KW_pub`, `KW_fn`, `KW_struct`, `KW_enum`, `KW_type`, `KW_trait`, `KW_let`, `KW_for`
- `Ident`（小写标识符），`TypeIdent`（PascalCase 类型名称）
- `LPAREN`, `RPAREN`, `LBRACE`, `RBRACE`, `LBRACKET`, `RBRACKET`
- `NL`（换行），`SKIP`（空白——从 grep 模式中过滤）
- `DocComment`, `DocLine`, `DocSection`, `LineComment`, `BlockComment`
- `String`, `Number`, `Char`

## 工作流程

1. 运行 `indexion kgf inspect <file>` 查看完整处理流程
2. 如果看起来有问题，使用 `tokens`, `events` 或 `edges` 深入检查
3. 与 KGF 规范文件 (`kgfs/<lang>.kgf`) 对比以诊断问题

## KGF 开发陷阱

在编写或修改 KGF 规范时发现的常见错误：

### PEG 项顺序（first-match-wins）

KGF 使用 PEG 解析。在 `Item -> A / B / C` 中，如果 A 匹配，B 和 C 将不会被尝试。作为独立替代项的 `DocComment` **在**声明规则之前将消耗本应附加到声明的文档注释。

```
# BAD: FuncDecl 前面的 DocComment — 文档被作为独立项消耗
Item -> NL / DocComment / FuncDecl / Other

# GOOD: 声明之后 DocComment — FuncDecl 的 doc:DocComment? 获取它
Item -> NL / FuncDecl / DocComment / Other
```

### 文档和关键字之间的换行

源代码在文档注释和声明之间有换行。没有 `NL?` 或 `NL*`，可选文档捕获将静默失败：

```
# BAD: 立即跟在关键字后面的 DocComment — NL 打破了匹配
FuncDecl -> doc:DocComment? KW_fn id:Ident ...

# GOOD: NL? 允许文档和关键字之间的典型换行
FuncDecl -> doc:DocComment? NL? KW_fn id:Ident ...
```

### 自下而上的事件顺序（bind/scope）

事件自下而上触发：子规则在父规则之前。如果 `ExportDecl` 包裹 `FunctionDecl`，`FunctionDecl` 将首先触发。使用 `bind`/`$scope` 从子项传递数据到父项：

```
on FunctionDecl {
  bind ns "value" name "child_decl_id" to $id
  edge declares from $file to sym_id attrs obj(...)
}
on ExportDecl when $doc {
  let id = $scope("value", "child_decl_id")
  edge declares from $file to sym_id attrs obj("doc", $doc, ...)
}
```

### 令牌优先级冲突

先定义的令牌优先级更高。在通用 `Operator /[=+\-*]+/` 之前定义 `EQ /=/` 将会消耗 `=` 作为 `Operator`。首先定义特定令牌：

```
# BAD: Operator 在 EQ 之前匹配 =
TOKEN Operator /[!$%&*+\-.\/:<=>?@^|~]+/
TOKEN EQ       /=/

# GOOD: EQ 首先定义，优先级更高
TOKEN EQ       /=/
TOKEN Operator /[!$%&*+\-.\/:<=>?@^|~]+/
```

### 验证文档提取

修改 KGF 后，始终验证文档是否出现在声明边中：

```bash
# 必须在声明边中显示 doc="..."
indexion kgf edges test_file.ts --spec=typescript | grep declares

# 如果文档丢失，检查事件以查看 DocComment 去向
indexion kgf events test_file.ts --spec=typescript | grep DocComment
```
