# 构建Dart CLI应用程序

## 目录
* [1. 核心架构与进程生命周期](#1-核心架构--进程生命周期)
* [2. 流、诊断与格式化](#2-流-诊断--格式化)
* [3. 项目配置与打包](#3-项目配置--打包)
* [4. 参数解析与命令路由](#4-参数解析--命令路由)
* [5. 本地异步与现代化堆栈跟踪](#5-本地异步--现代化堆栈跟踪)
* [6. 子进程启动与AOT健壮性](#6-子进程启动--aot-健壮性)
* [7. 信号处理与终端清理](#7-信号处理--终端清理)
* [8. 测试CLI应用程序](#8-测试cli应用程序)
* [9. 现代编译与分发](#9-现代编译--分发)
* [10. 工作流与审计清单](#10-工作流--审计清单)
* [参考文献与示例](#参考文献--示例)

---

## 1. 核心架构与进程生命周期

### 避免破坏性退出(`exit(N)`)
调用`dart:io`的`exit(int code)`会在C++运行时中调用`Platform::Exit(code)`。它会立即终止操作系统进程，而不会展开Dart栈：
* **调试器断开连接**：当使用`--pause-isolates-on-exit`启动时，虚拟机服务会在关闭前暂停隔离体以允许IDE检查。`exit()`会终止操作系统进程，而虚拟机服务无法暂停或检查状态。
* **覆盖率丢失**：`package:coverage`在暂停退出状态下通过虚拟机服务RPC查询执行行。`exit()`会销毁进程，导致0%的覆盖率。
* **缓冲区截断**：`stdout`和`stderr`是异步的`IOSink`流缓冲区。`exit()`会丢弃未刷新的字节。
* **资源泄漏**：`finally`块（关闭锁、删除临时目录）会被绕过。

**规则**：在正常执行期间避免直接调用`exit(code)`；设置`exitCode = code`或从`CommandRunner<int>`（来自`package:args`）返回一个整数退出码，并允许异步的`main()`函数自然返回。不要在未处理的错误上调用`exit()`；抛出一个未处理的`Error`或异常，以便运行时可以干净地展开并退出，并返回非零状态码。

标准POSIX退出码（`/usr/include/sysexits.h`）：
* `0`：成功（`EX_OK` / `ExitCode.success.code`)
* `64`：命令行使用错误（`EX_USAGE` / `ExitCode.usage.code`)
* `65`：数据格式错误（`EX_DATAERR` / `ExitCode.data.code`)
* `70`：内部软件崩溃（`EX_SOFTWARE` / `ExitCode.software.code`)
* `78`：配置错误（`EX_CONFIG` / `ExitCode.config.code`）

*注意*：优先导入`package:io/io.dart`并使用`ExitCode`常量（例如，`ExitCode.usage.code`，`ExitCode.software.code`）而不是魔法整数字面量。对于没有包依赖的最小独立脚本，可以使用标准的POSIX整数字面量（`0`，`64`，`70`）。

```dart
import 'dart:io';
import 'package:args/command_runner.dart';
import 'package:io/io.dart' show ExitCode; // 提供标准的POSIX ExitCode常量

Future<void> main(List<String> args) async {
  final runner = CommandRunner<int>('tool', 'CLI工具描述。');
  try {
    final status = await runner.run(args);
    exitCode = status ?? ExitCode.success.code;
  } on UsageException catch (e) {
    stderr
      ..writeln(e.message)
      ..writeln(e.usage);
    exitCode = ExitCode.usage.code;
  }
}
```

### 薄的入口点模式(`bin/` vs. `lib/src/`)
将`bin/*.dart`文件严格保留为最小的入口点跳板（实例化运行器，传递`args`，等待退出码）。将所有命令定义、参数解析器、格式化器和业务逻辑放在`lib/src/`中。

* **理由**：`bin/`中的代码无法通过`package:` URI干净地导入。将逻辑移入`lib/src/`允许在内存中快速（毫秒级`< 2ms`）对整个命令运行器、子命令层次结构和业务逻辑进行单元测试，而无需启动操作系统子进程。

```dart
// bin/my_cli.dart — 薄的入口点跳板
import 'dart:io';
import 'package:my_cli/src/cli.dart';

Future<void> main(List<String> args) async {
  exitCode = await runCli(args);
}
```

---

## 2. 输出、诊断与格式化

* **数据与诊断**：将预期的程序结果和机器可读数据专用于`stdout`。将警告、错误消息和调试日志专用于`stderr`。
* **错误使用规则**：当发生参数解析或强制选项错误时（`FormatException`，`UsageException`或当通过`results.option(...)`访问缺少`mandatory: true`选项时抛出`ArgumentError`），**错误消息和使用文本必须同时写入`stderr`**，并且必须返回退出码`64`（`EX_USAGE` / `ExitCode.usage.code`）。`stdout`应该**仅在用户明确通过`--help`或`-h`请求时**接收使用帮助。
* **错误处理中不要使用`print()`**：`print()`路由到`stdout`。对所有失败通知使用`stderr.writeln()`。对于标准输出，优先使用`stdout.writeln()`而不是`print()`，以符合[`avoid_print`](https://dart.dev/tools/linter-rules/avoid_print) lint规则（除非`analysis_options.yaml`明确配置`avoid_print: false`）。
* **终端功能检测与`NO_COLOR`**：在发出ANSI颜色或光标转义代码之前，验证`stdout.hasTerminal`，`stdout.supportsAnsiEscapes`，以及`!Platform.environment.containsKey('NO_COLOR')`：
  ```dart
  bool get useAnsi =>
      stdout.hasTerminal &&
      stdout.supportsAnsiEscapes &&
      !Platform.environment.containsKey('NO_COLOR');
  ```
* **机器可读模式**：当传递`--json`或`--machine`标志时，将数据格式化为JSON并输出到`stdout`，并将日志路由到`stderr`。

---

## 3. 项目配置与打包

### 模板与Pubspec可执行文件映射(`executables:`)
使用`dart create -t console <package_name>`构建新的命令行项目，它会初始化标准的`bin/`和`lib/`布局。始终在`pubspec.yaml`的`executables:`下声明可执行文件，以将命令名称映射到`bin/`中的脚本，从而允许通过`dart run <command>`（不指定`bin/...dart`）进行干净的调用，并为`dart install`配置全局二进制符号链接：

```yaml
name: my_cli
description: 高性能CLI工具。
version: 1.0.0

executables:
  my_cli: # 映射到 bin/my_cli.dart
  secondary_cmd: helper # 映射到 bin/helper.dart
```

### 单源版本控制(`package:build_version`)
避免在`bin/*.dart`或手动同步常量文件中硬编码`--version`字符串。使用`package:build_version`在构建期间直接从`pubspec.yaml`生成包含`const packageVersion = 'x.y.z';`的`lib/src/version.dart`。

### 缓存约定
将瞬态缓存文件存储在`.dart_tool/<package_name>/`中。切勿将持久缓存文件直接写入项目根目录。

---

## 4. 参数解析与命令路由

导入`package:args`以管理命令行参数：

* **简单脚本**：直接使用`ArgParser`与`addFlag()`和`addOption()`。
* **多命令工具**：实现`CommandRunner<int>`并为每个子命令扩展`Command<int>`，直接返回POSIX退出码。
* **类型安全访问器**：使用`results.flag('name')`，`results.option('name')`和`results.multiOption('name')`（在`package:args` 2.5+中可用），而不是使用映射索引`operator []`，以消除手动类型转换（`as bool`，`as String?`）。
* **复杂选项模型**：对于具有大量标志的应用程序，使用`package:build_cli`生成强类型选项类。利用命名默认覆盖（例如`{String? hostDefaultOverride}`）以干净地合并配置文件与CLI标志。

---

## 5. 本地异步与现代化堆栈跟踪

* **避免`Chain.capture()`**：Dart虚拟机原生保留异步堆栈帧跨`await`挂起点。`Chain.capture`将事件循环包装在自定义Zone中，导致大量分配开销并在Zone边界处捕获错误。
* **使用`Trace.from(st).terse`进行清理**：在未捕获的错误上使用`package:stack_trace`的静态实用工具，而无需捕获Zone：

```dart
import 'dart:io';
import 'package:io/io.dart' show ExitCode;
import 'package:stack_trace/stack_trace.dart';

Future<void> runMain(List<String> args) async {
  try {
    await executeLogic(args);
    exitCode = ExitCode.success.code;
  } catch (e, st) {
    stderr.writeln('致命错误：$e');
    if (args.contains('-v') || args.contains('--verbose')) {
      stderr.writeln(Trace.from(st).terse);
    }
    exitCode = ExitCode.software.code;
  }
}
```

---

## 6. 子进程启动与AOT健壮性

当启动Dart SDK子进程或执行其他Dart工具（例如，`dart format`，`dart test`，`build_runner`）时：

* **不要假设`Platform.resolvedExecutable`或`Platform.executable`指向`dart`命令行可执行文件**：在独立的AOT编译二进制文件（`dart install` / `dart compile exe`）中，`resolvedExecutable`指向编译的应用程序二进制文件本身，导致递归自我调用循环或标志拒绝崩溃。
* **使用`package:cli_util`**：使用`cli_util.dartExecutable`或`cli_util.sdkPath`解析Dart SDK可执行文件，而不是编写自定义PATH或目录刮取器。
* 参考版本要求和详细技术指南，请参阅[参考文献/aot_sdk_discovery.md](references/aot_sdk_discovery.md)。

---

## 7. 信号处理与终端清理

如果您的CLI更改终端模式、显示旋转器或打开监听套接字：

* **Windows信号守卫**：在Windows上，`ProcessSignal.sigterm.watch()`会抛出`UnsupportedError`。用`if (!Platform.isWindows)`守卫`sigterm`。
* **回显与行模式清理**：如果设置`stdin.echoMode = false`或`stdin.lineMode = false`，首先检查`if (!stdin.hasTerminal) return;`，然后安装`SIGINT`监听器和`finally`块以恢复它们，以便用户按键在退出后仍然可见。
* **光标可见性**：如果发出ANSI隐藏光标（`\x1B[?25l`），则在退出或取消时始终恢复光标可见性（`\x1B[?25h`）。
* **套接字清理**：在终止信号上显式关闭监听的`HttpServer`或`ServerSocket`实例（`server.close(force: true)`），以立即释放操作系统端口。
* 参考详细模式，请参阅[参考文献/signals_and_terminal.md](references/signals_and_terminal.md)。

---

## 8. 测试CLI应用程序

跨两个不同的层结构测试：

1. **单元测试（内存中，`< 5ms`）**：直接通过在`test/`中导入`package:<pkg>/src/...`来测试命令类、选项解析和业务逻辑。
2. **集成测试（子进程）**：使用`package:test_process`和`package:test_descriptor`验证端到端二进制执行、进程I/O流和操作系统退出码：

```dart
import 'package:test/test.dart';
import 'package:test_descriptor/test_descriptor.dart' as d;
import 'package:test_process/test_process.dart';

void main() {
  test('CLI进程输入并干净退出', () async {
    await d.file('input.txt', 'hello').create();

    final process = await TestProcess.start('dart', [
      'run',
      'bin/my_cli.dart',
      '--input',
      d.path('input.txt'),
    ]);

    await expectLater(process.stdout, emitsThrough('处理完成。'));
    await process.shouldExit(0);
  });
}
```

---

## 9. 现代编译与分发

Dart 3.12+ 标准化了CLI分发的目标为`dart run`和`dart install`（不再使用`dart pub global activate`）：

* **临时执行（JIT）**：`dart run <package>@<version> [args]`按需下载并运行CLI。
* **全局安装（原生AOT）**：`dart install <package>`将包入口点编译为快速的原生独立二进制文件，存储在`~/.dart/install/bin/`。
* **本地开发**：使用`dart run <command>`（通过`pubspec.yaml`中的`executables:`解析）或`dart run bin/cli.dart`。
* **捆绑动态库与代码资源**：使用`dart build cli`。输出捆绑到`build/cli/_/bundle/`。
* **独立可执行文件编译**：使用`dart compile exe bin/cli.dart -o <output_path>`。

---

## 10. 工作流与审计清单

### 实现工作流
- [ ] 在`pubspec.yaml`的`executables:`下声明入口点。
- [ ] 将`bin/*.dart`保留为薄的入口点；将命令逻辑放在`lib/src/`。
- [ ] 返回整数退出码或设置`exitCode = N`；避免原始`exit(N)`。
- [ ] 将解析失败时的错误、警告和使用文本路由到`stderr`。
- [ ] 使用`results.flag()`，`results.option()`和`results.multiOption()`以实现类型安全。
- [ ] 在发出ANSI代码之前验证`useAnsi`（检查`stdout.hasTerminal`，`supportsAnsiEscapes`，以及`NO_COLOR`）。
- [ ] 使用`cli_util.dartExecutable`启动子工具，绝不要使用`Platform.resolvedExecutable`。
- [ ] 在内存中单元测试命令运行器；使用`test_process`测试端到端二进制执行。

---

## 参考文献 & 示例

* **单命令工具模板**：[examples/single_command_tool.dart](examples/single_command_tool.dart)
* **多命令运行器模板**：[examples/multi_command_runner.dart](examples/multi_command_runner.dart)
* **AOT SDK发现与子进程启动**：[references/aot_sdk_discovery.md](references/aot_sdk_discovery.md)
* **信号处理与终端清理**：[references/signals_and_terminal.md](references/signals_and_terminal.md)
