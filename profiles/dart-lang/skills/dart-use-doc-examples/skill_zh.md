# 在 Dartdoc 中使用示例

## 目录
*   [1. `{@example}` 指令](#1-the-example-directive)
*   [2. 使用区域](#2-using-regions)
*   [3. 隐藏设置代码](#3-hiding-setup-code)
*   [4. 标记过滤规则](#4-marker-filtering-rules)
*   [5. 位置和路径解析](#5-placement-and-path-resolution)
*   [6. 验证](#6-verification)

当编写需要多行代码示例的文档时，通常应将示例提取到独立的 `.dart` 文件中，并使用 `{@example}` 指令注入，而不是在 `///` 注释中内联编写。这确保示例可以被分析、检查并执行。

## 1. `{@example}` 指令
`{@example}` 指令解析外部文件，并将其解析为生成的文档中的围栏 Markdown 代码块。

**语法：** `{@example <路径>[#<区域>] [lang=语言] [indent=keep|strip]}`

*   **`<路径>`**：文件的路径。以 `/` 开头的路径从包根目录解析。否则，相对于当前文件。
*   **`lang`**：Markdown 围栏的语言。从文件扩展名自动检测（例如，`dart`），但也可以显式指定（例如，`lang=text`）。
*   **`indent`**：`strip`（默认值）会从代码块中激进地移除共享的前导缩进。

*错误（内联 Markdown）*：
```dart
/// 向后端发起客户端服务请求。
///
/// ```dart
/// final client = Client();
/// client.send();
/// ```
```

*正确（外部文件注入）*：
```dart
/// 向后端发起客户端服务请求。
///
/// {@example /example/client_request.dart}
```

## 2. 使用区域
通常，外部示例文件包含导入、设置或 `void main()` 包装器，您不希望在文档中显示这些内容。您可以通过在 `{@example}` 指令路径中附加 `#<区域>` 来提取特定代码块，并在目标文件中用 `#region` 和 `#endregion` 注释将该代码包裹起来。

**Dart 代码（例如，`/example/client.dart`）**：
```dart
import 'package:http/http.dart';

void main() {
  // #region request_snippet
  final client = Client();
  client.send();
  // #endregion request_snippet
}
```

**Dartdoc 使用**：
```dart
/// 将客户端连接到服务器并发送请求。
///
/// {@example /example/client.dart#request_snippet}
```

## 3. 隐藏设置代码
如果您的提取区域中的特定代码行对编译器/分析器是必要的，但对文档阅读者无关紧要（或分散注意力），则在该行附加 `#hide`。

**Dart 代码**：
```dart
final mockServer = startServer(); // #hide
final data = await fetch(mockServer.url);
```
在生成的文档中，仅会显示 `final data = await fetch(mockServer.url);`。带有 `#hide` 的行会被完全丢弃。

## 4. 标记过滤规则
在使用 `#hide`、`#region` 和 `#endregion` 标记时，您必须遵循以下两个技术约束：

*   **区域必需**：只有在您针对特定区域后缀（例如，`{@example file.dart#region_name}`）时，标记才会被处理和移除。如果您注入整个文件而没有区域后缀，文件将按源代码中的样子嵌入，包括任何标记文本（如 `// #hide`）。
*   **格式无关性**：标记系统完全是格式无关的。Dartdoc 只是运行正则表达式来移除包含标记字符串的行，这意味着它在非 Dart 文件中（例如，在 YAML 注释 `# #region` 或 HTML 注释 `<!-- #region -->` 中）工作方式完全相同。

## 5. 位置和路径解析
`{@example}` 指令是一个块级指令。它必须单独成行，并以 `///` 开头。其内部 `<路径>` 解析器遵循严格的 URI 引用规则：

*   **包根路径（`/`）**：以 `/` 开头的路径会直接解析到 Dart 包的根目录。当目标文件位于较深的目录时使用此方法。
    *   *示例*：`{@example /test/data/sample.txt}` 精确映射到 `<package_root>/test/data/sample.txt`。
*   **相对路径**：不带 `/` 开头的路径相对于包含文档注释的文件的目录解析。
    *   *示例*：`{@example ../utils/demo.dart}`
*   **边界强制**：使用 `..` 段向上遍历是完全可以接受的，但 dartdoc 会原生地在包根目录停止目录遍历（它永远不会离开包）。
*   **无网络 URL**：绝对 URI（例如，以 `https://` 开头的）绝对不被支持。示例文件必须原生地位于本地文件系统的某个位置。
*   **分隔符和编码**：因为 dartdoc 将路径解析为 URI，所以您必须始终使用正斜杠（`/`）作为文件夹分隔符（即使在 Windows 上也是如此）。您可以原生地包含 URI 编码字符（如 `%20` 用于空格），只要它们符合 URI 引用规则。

## 6. 验证
注入示例后：
1.  运行 `dart analyze` 在示例文件上，确保隐藏的设置代码可以编译。
2.  （可选）运行 `dart doc` 以验证 dartdoc 是否成功解析指令，而未抛出“读取文件失败”或“缺少区域”的警告。
