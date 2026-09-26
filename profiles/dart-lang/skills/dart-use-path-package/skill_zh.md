# Dart中安全的跨平台路径操作

## 目录
* [1. 核心原则与跨平台规则](#1-核心原则与跨平台规则)
* [2. 推荐的package:path惯用语与字符串反模式](#2-推荐的package:path惯用语与字符串反模式)
* [3. 本地路径与POSIX、Git及URL上下文的桥接](#3-本地路径与POSIX、Git及URL上下文的桥接)
* [4. 可模拟的文件系统(`package:file`与全局`p.*`)](#4-可模拟的文件系统packagefile与全局p)
* [5. 扩展、复合扩展与词干提取](#5-扩展复合扩展与词干提取)
* [6. 工作流与审计清单](#6-工作流与审计清单)
* [参考文献与示例](#参考文献与示例)

---

## 1. 核心原则与跨平台规则

### 避免将文件路径视为原始字符串
* Windows上的本地文件路径使用反斜杠(`\`)，而macOS和Linux使用正斜杠(`/`)。
* 字符串操作如`.contains('foo/')`、`.startsWith('foo/')`或`.split('/')`在Windows的本地路径上会静默失败。
* 字符串插值如`'$dir/$file'`在Windows上会注入正斜杠，并且当`$dir`以尾随斜杠结尾时会产生重复斜杠(`//`)。

**规则**：在使用前，始终使用`p.split(path)`将路径分解为段，以检查目录层次结构或段名称，并始终使用`p.join(...)`连接路径组件。

### 实用边界连接与多段分解(`p.join`)
* **跨平台库（Windows + POSIX）**：将单个路径段传递给`p.join(dir, 'sub', 'file.json')`，以便`package:path`在每个组件之间插入操作系统原生的分隔符（Windows上的`\`，POSIX上的`/`）。
* **仅POSIX工具与静态子路径可搜索性**：在仅针对Linux/macOS（或当将动态基础路径连接到已知静态子路径）的代码库中，将5-6个静态段分解为单独参数（`p.join(home, '.local', 'share', 'app', 'bin', 'config.json')`）会导致`dart format`跨6-8行垂直换行，并**破坏子字符串可搜索性**（`grep` / `code_search`用于`.local/share/app/bin`）。
* **POSIX目标的规则**：优先选择**2参数边界连接**（`p.join(home, '.local/share/app/bin/config.json')`）。这可以防止在变量边界处出现重复斜杠错误（`//`），同时保持单行可读性和精确字符串可搜索性。

### 规范化与规范化(`p.normalize`与`p.canonicalize`)
* `p.normalize(path)`纯粹按词法解析`.`和`..`段，而无需查询文件系统或标准化大小写。
* 当去重目录路径或跨符号链接、相对根或大小写不敏感文件系统比较物理文件身份时，使用`p.canonicalize(path)`。

### 移除位置指定符与安全转换URI
* 格式化为`<路径>:<行>-<列>`或`<路径>:<行>`的字符串不是纯文件路径。直接将它们传递给`p.normalize`或`Uri.parse`会导致错误（在Windows上，`Uri.parse`将`C:`误认为是URI方案，将`:行`误认为是端口号）。
* 通过正则表达式（`RegExp(r'^(.*?):(\d+(?:-\d+)?)$')`）在将文件路径传递给`package:path`之前提取尾随的`:行-列`后缀。
* **URI边界转换**：在文件路径和`Uri`对象之间转换时，始终使用`p.toUri(path)`和`p.fromUri(uri)`，而不是`Uri.parse(path)`或手动字符串连接。

---

## 2. 推荐的package:path惯用语与字符串反模式

### 路径连接
* **推荐**：`p.join(dir, file)`
* **避免**：`'$dir/$file'`或`'a/$b'`
* **原因**：字符串插值在Windows上注入`/`，并在`$dir`以尾随分隔符结尾时产生重复斜杠（`//`）。

### 段匹配
* **推荐**：`p.split(path).contains('foo')`
* **避免**：`path.contains('foo/')`
* **原因**：字符串匹配在Windows反斜杠（`foo\bar`）上失败，并在部分子字符串名称（例如`barfoo/`）上产生误报。

### 根和目录前缀
* **推荐**：`p.split(path).first == 'foo'`或`p.isWithin('foo', path)`
* **避免**：`path.startsWith('foo/')`
* **原因**：在Windows分隔符上失败，并遗漏相对前缀变体，例如`./foo/`。

### 文件扩展名
* **推荐**：`p.extension(path) == '.wasm'`
* **避免**：`path.endsWith('.wasm')`
* **原因**：子字符串后缀匹配错误地匹配目录（`foo.wasm/`）或非扩展后缀。

### 扩展切片和复合扩展
* **推荐**：`p.withoutExtension(path)`和`p.extension(path, 2)`
* **避免**：`path.lastIndexOf('.')`和手动`substring`切片
* **原因**：手动算术在隐藏点文件（`.gitignore`）和复合扩展（`.js.map`，`.tar.gz`）上失效。

### POSIX和URL路径转换
* **推荐**：`p.posix.joinAll(p.split(path))`或`p.url.joinAll(p.split(path))`
* **避免**：`path.replaceAll(r'\', '/')`
* **原因**：临时分隔符替换在根驱动器上失败，并将操作系统上下文与POSIX或URL目标混合。

### URI转换
* **推荐**：`p.toUri(path)`和`p.fromUri(uri)`
* **避免**：`Uri.parse(path)`和`uri.path`
* **原因**：直接URI解析在Windows驱动器字母（`C:`）上失败，并泄露百分比编码（例如`%20`用于空格）。

### 目录基本名辅助函数
* **推荐**：
  ```dart
  String canonicalDirName(Directory d) => p.basename(p.normalize(d.absolute.path));
  ```
* **避免**：跨文件重复`p.basename(p.normalize(dir.absolute.path))`的内联
* **原因**：集中化规范目录命名逻辑，减少样板代码。

---

## 3. 本地路径与POSIX、Git及URL上下文的桥接

避免调用`.replaceAll('\\', '/')`或`.replaceAll(r'\', '/')`将操作系统原生路径转换为POSIX路径（用于Git、YAML、存档清单）或URL段。

**规则**：使用`p.split(...)`分割相对原生路径，使用**Dart 3列表模式匹配**检查段，并使用`p.posix.joinAll(...)`或`p.url.joinAll(...)`连接。始终先调用`p.relative(filePath, from: root)`，以防止领先的根段（POSIX上的`'/'`或Windows上的`r'C:\'`）干扰相对前缀模式：

```dart
import 'package:path/path.dart' as p;

String computeWebAssetKey(String filePath, String projectRoot) {
  final relative = p.relative(filePath, from: projectRoot);
  final segments = p.split(relative);
  return switch (segments) {
    ['assets', ...] => p.posix.joinAll(segments),
    _ => p.posix.joinAll(['assets', ...segments]),
  };
}
```

### Git路径与仓库元数据
* Git仓库树对象、`.gitignore`模式规则、`.gitattributes`和git跟踪的符号链接严格使用POSIX正斜杠（`/`），即使在Windows上也是如此。
* 将原生Windows反斜杠（`\`）插入`.gitignore`或git命令会导致Git将`\`视为转义字符而不是目录分隔符，从而静默破坏模式匹配。
* 当从原生文件路径程序生成`.gitignore`条目、仓库清单或符号链接目标时，使用`p.posix.joinAll(p.split(relativePath))`或`p.posix.join(...)`转换相对原生路径。

---

## 4. 可模拟的文件系统(`package:file`与全局`p.*`)

在使用`package:file`（例如CLI应用程序或使用`MemoryFileSystem`测试的服务）的代码库中，避免在`File`或`Directory`路径上调用顶级`p.*`函数。

* 顶级`p.*`函数绑定到运行测试的*主机操作系统*。
* 如果单元测试在Linux或macOS运行器上创建了一个`MemoryFileSystem(style: FileSystemStyle.windows)`，全局`p.split(file.path)`将按`/`分割而不是`\`，导致测试失败。

**规则**：始终使用附加到`FileSystem`的`Context`（`file.fileSystem.path`）：

```dart
import 'package:file/file.dart';

List<String> listSubdirectoryNames(Directory dir) {
  final pathContext = dir.fileSystem.path;
  return dir
      .listSync()
      .whereType<Directory>()
      .map((d) => pathContext.basename(d.path))
      .toList();
}
```

---

## 5. 扩展、复合扩展与词干提取

避免使用`.lastIndexOf('.')`和`.substring()`算术提取文件扩展名或插入内容哈希。`p.extension`原生支持通过其可选`level`参数进行多级扩展。

* **多点词干细微差别**：调用`p.extension('main.dart.wasm', 2)`返回`'.dart.wasm'`，因为它盲目捕获最后两个点分隔的段。当对可能具有多级词干（例如`main.dart.wasm`与`main.dart.js.map`）的文件哈希或移除扩展时，检查`p.extension(filename, 2)`是否匹配已知的复合扩展（或`.endsWith('.map')`）再回退到单级`p.extension(filename)`：

```dart
import 'package:path/path.dart' as p;

String insertContentHash(String filename, String hash) {
  final compoundExt = p.extension(filename, 2);
  // 仅用于真正的复合后缀（例如'.js.map'）
  final ext = compoundExt.endsWith('.map')
      ? compoundExt
      : p.extension(filename);
  final stem = filename.substring(0, filename.length - ext.length);
  return '$stem.$hash$ext';
}
```

---

## 6. 工作流与审计清单

### 路径重构清单
- [ ] 将字符串插值（`'$dir/$file'`）替换为`p.join(dir, file)`。
- [ ] 将`.contains('dir/')`和`.startsWith('dir/')`替换为`p.split(path)`段检查或`p.isWithin(parent, child)`。
- [ ] 将`.replaceAll(r'\', '/')`替换为`p.posix.joinAll(p.split(path))`（或`p.url.joinAll`）。
- [ ] 将文件路径上的`.endsWith('.ext')`替换为`p.extension(path) == '.ext'`。
- [ ] 将手动点索引切片替换为`p.withoutExtension(path)`和`p.extension(path, [level])`。
- [ ] 确保使用`package:file`的代码访问`fileSystem.path`而不是全局`p.*`。
- [ ] 确保Git路径、`.gitignore`条目和符号链接目标使用`p.posix`正斜杠。

---

## 参考文献与示例

* **跨平台路径与POSIX转换示例**：[examples/cross_platform_paths.dart](examples/cross_platform_paths.dart)
* **可模拟FileSystem路径上下文示例**：[examples/file_system_context.dart](examples/file_system_context.dart)
