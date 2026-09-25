# 编写 Dart API 文档

## 目录
*   [1. 范围和结构](#1-scope-and-structure)
*   [2. 语气和开头](#2-tone-and-openers)
*   [3. 严格禁止的反模式（禁止）](#3-strict-anti-patterns-banned)
*   [4. 技术位置和解析](#4-technical-placement--resolution)
*   [5. 链接和 Markdown](#5-linking-and-markdown)
*   [6. 验证](#6-verification)
*   [示例](#examples)

当被要求编写或更新 Dart 代码的文档时，你必须严格遵循基于“Effective Dart: Documentation”指南的格式规则。

## 1. 范围和结构
*   **针对公共 API：** 将你的文档工作重点放在公共声明上。不要记录私有成员（以下划线 `_` 开头的成员），除非明确指示，因为它们不会出现在生成的 API 参考网站上。
*   **始终使用 `///`：** 使用 `///` 连续行注释来记录所有 API 文档。永远不要使用 `/** ... */` 块注释。
*   **正确的句子：** 将所有注释格式化为正确的句子。首字母大写（除非它是小写标识符）并以句号结尾。
*   **第一段：** 文档注释的第一段必须是一个简洁的句子，总结该元素。以句号结尾。Dartdoc 会逐字提取这段内容用于列表视图。
*   **分隔：** 始终使用一个包含 `///` 的空行来分隔第一句摘要和其余文档。永远不要输出一个完全空的换行符（例如，一个没有 `///` 的 `\n`），因为这会终止文档注释块。

## 2. 语气和开头
*   **属性使用名词短语：** 变量、getter 或 setter 的描述以名词短语开头。
    `/// 球体的半径。`（而不是“获取半径...”）
*   **布尔值使用“Whether”：** 布尔属性的文档以“Whether”开头。
    `/// 连接是否活跃。`
*   **方法使用第三人称动词：** 方法或函数的描述以描述其作用的第三人称动词开头。
    `/// 初始化数据库。`（而不是“初始化”或“此方法初始化”）
*   **避免冗余：** 不要重述签名或元素名称。不要说“这个类是...”或“foo 方法做什么...”。

## 3. 严格禁止的反模式（禁止）
*   **禁止使用 Javadoc/TSDoc 标签（`@param`、`@return`、`@throws` 等）：** 永远不要使用 Javadoc 风格的标签（`@param`、`@return`、`@returns`、`@throws`、`@exception`、`@see`、`@type`）。相反，应将参数名称、返回行为和异常编织到正文中。

## 4. 技术位置和解析
*   **注解（`@override` 等）：** 文档注释必须放在元数据注解之前。
*   **继承文档：** 如果 `@override` 成员的行为与超类或接口没有区别，避免在 `@override` 成员上重复文档注释。Dartdoc 会自动继承基本文档。
*   **getter/setter 对：** 如果一个属性既有 getter 又有 setter，将文档只放在 getter 上。如果两者都记录了，工具会发出警告。
*   **默认构造函数：** 要在文档注释中链接到默认的、未命名的构造函数，你必须使用 `.new` 语法（例如，`[ClassName.new]`）。

## 5. 链接和 Markdown
*   **方括号（`[identifier]`）用于作用域内的符号：** 使用方括号链接到任何作用域内的标识符（参数、类、方法、字段和顶级函数），以便 dartdoc 可以解析它们。永远不要用反引号表示参数。
*   **方法链接中避免括号：** 避免链接中使用括号（例如，使用 `[String.contains]`，而不是 `[String.contains()]`）。
*   **反引号用于关键字和字面量：** 使用反引号表示关键字、字面量和任意表达式（例如 `` `null` ``、`` `true` ``、`` `void` ``）。永远不要将关键字放在方括号中（避免 `[null]` 或 `[true]`）。
*   **作用域外的链接（`@docImport`）：** 如果你需要链接到当前库没有导入的符号，请在文件的顶部（在 `library;` 声明上）使用 `@docImport` 指令，而不是添加标准 `import`。
*   **代码块：** 对于代码示例，始终标记语言围栏。使用 ```` ```dart ```` 表示 Dart，或 ```` ```sh ```` 表示 shell 命令。不要留下未标记的代码块，因为 Dartdoc 会尝试自动检测语言，并且经常猜错。
*   **格式化：** 在第一段之后使用标准 Markdown（粗体、列表等）来充分解释边缘情况、抛出的异常以及调用者无法看到的内部行为。

## 6. 验证
编写或更新文档注释后：
1.  运行 `dart analyze` 以确保所有括号引用正确解析，不会触发 `comment_references` 警告。
2.  （可选）运行 `dart doc` 以验证生成的文档是否干净地渲染。

## 示例

### 1. 禁止的标签与正文的对比
**错误：**
```dart
/// 此方法获取数据。
/// @param force true 强制重新加载。
/// @return 数据
/// @throws NetworkException 如果主机无法访问。
Data load(bool force) { ... }
```
**正确：**
```dart
/// 获取远程数据。
///
/// 如果 [force] 为 true，此方法会绕过本地缓存并强制执行网络请求。
///
/// 如果主机无法访问，则抛出 [NetworkException]。
Data load(bool force) { ... }
```

### 2. 注解位置陷阱
**错误：**
```dart
@override
/// 将小部件渲染到屏幕上。
Widget build(BuildContext context) { ... }
```
**正确：**
```dart
/// 将小部件渲染到屏幕上。
@override
Widget build(BuildContext context) { ... }
```

### 3. 开头和语气
**错误：**
```dart
/// 获取连接是否活跃。
bool get isActive => _active;

/// 此方法初始化连接。
void init() { ... }
```
**正确：**
```dart
/// 连接是否活跃。
bool get isActive => _active;

/// 初始化连接。
void init() { ... }
```

### 4. 构造函数链接
**错误：**
```dart
/// 创建新用户。类似于调用 [User()]。
User.create() { ... }
```
**正确：**
```dart
/// 创建新用户。类似于调用 [User.new]。
User.create() { ... }
```

### 5. 作用域外的链接（`@docImport`）
**错误：**
```dart
import 'package:http/http.dart'; // 仅为了文档添加不必要的运行时依赖

/// 使用此方法时，你必须传递一个 [Client]。
```
**正确：**
```dart
/// @docImport 'package:http/http.dart';
library;

/// 使用此方法时，你必须传递一个 [Client]。
```
