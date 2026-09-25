# 使用原生资源钩子将 C 代码编译为代码资源

使用构建和链接钩子将原生 C/C++ 源代码集成并自动打包到 Dart 的 **原生资源** 功能下的 **代码资源** 中。

## 目录
- [简介](#简介)
- [限制](#限制)
- [原生互操作包](#原生互操作包)
- [分步工作流程](#分步工作流程)
- [选择集成方法](#选择集成方法)
- [方法 1：使用链接器树摇进行本地编译（推荐）](#方法-1使用链接器树摇进行本地编译推荐)
  - [先决条件主机编译器工具链](#先决条件主机编译器工具链)
  - [C 源代码和绑定设置](#c源代码和绑定设置)
  - [定义 C 库构建规范](#定义C库构建规范)
  - [实现 hook/build.dart](#实现hookbuilddart)
  - [实现 hook/link.dart](#实现hooklinkdart)
- [方法 2：下载预编译的动态库](#方法-2下载预编译的动态库)
  - [为什么下载预编译的二进制文件？](#为什么下载预编译的二进制文件)
  - [实现预编译动态下载](#实现预编译动态下载)
- [验证检查清单](#验证检查清单)
  - [1. 本地执行沙盒](#1本地执行沙盒)
  - [2. 验证目标输出](#2验证目标输出)
  - [3. 验证树摇剥离](#3验证树摇剥离)
  - [4. 验证离线合规性（用户定义）](#4验证离线合规性用户定义)

---

## 简介

在 Dart 的 **原生资源** 功能下，包可以将原生代码（如 C/C++ 库）作为 **代码资源** 打包，并在标准开发周期（例如 `dart run`、`dart test`、`dart build` 和 `flutter run`）中自动将其捆绑。**代码资源** 的打包由放置在包的 `hook/` 文件夹内的两个程序钩脚脚本驱动：

1.  `hook/build.dart`：将本地 C 源代码编译为机器代码，或将预构建的原生二进制文件作为代码资源捆绑到特定的主机/目标架构。
2.  `hook/link.dart`：链接构建的代码资源，应用高级的树摇优化以剥离未使用的原生符号并压缩运行时二进制文件大小。

---

## 限制

> [!IMPORTANT]
> 保持所有文件解析平台无关。永远不要硬编码绝对目标路径、shell 脚本或系统命令变量。始终使用 `Platform.script.resolve()` 或基于 `Uri` 的解析，以确保脚本完全可移植。

*   **钩子位置**：编译和打包钩子必须严格位于包根目录下的 `hook/` 目录中：
    *   `hook/build.dart`（构建执行阶段）
    *   `hook/link.dart`（可选的打包/链接/树摇阶段）
*   **编译工具链标准**：使用 `package:native_toolchain_c` 的程序化 API（例如 `CBuilder` 和 `CLibrary`）来运行编译工具链。永远不要通过 shell 命令调用原始的 `gcc`、`clang` 或 `msvc`。
*   **前言和许可证头**：每个手工编写和生成的源文件（包括绑定、辅助程序和钩子）必须严格包含目标包的版权和许可证头。
*   **树摇映射**：如果使用编译器树摇，你必须使用 FFIgen 生成的记录使用映射将目标 Dart 方法名（例如 `Method.name`）映射回它们原始的原生 C 符号名。映射文件必须位于 `lib/src/third_party/` 下，并严格使用 `.g.dart` 扩展名（例如 `sqlite3.record_use_mapping.g.dart`）。
*   **预编译库的完整性保护**：如果采用动态下载模式：
    *   **加密验证**：下载的预构建二进制文件必须与包含 MD5 或 SHA-256 哈希的预配置查找表进行比对，以确保二进制完整性并防止篡改。
    *   **优雅恢复**：通过 `local_build` 等标志支持离线开发者，提供回退（例如通过本地编译器执行）。

---

## 原生互操作包

**代码资源** 的程序化构建和链接钩子利用了三个专门的原生互操作包：

| 依赖项 | 目的 | 关键 API 抽象 |
| :--- | :--- | :--- |
| **`package:hooks`** | 主要协调器，定义执行边界。 | `build(args, callback)`，`link(args, callback)` |
| **`package:native_toolchain_c`** | 检测本地编译器（MSVC、Xcode/Clang、GCC）并执行构建工具链。 | `CLibrary`，`CBuilder`，`LinkerOptions.treeshake` |
| **`package:code_assets`** | 模型传递给动态加载器的代码元数据记录。 | `CodeAsset`，`DynamicLoadingBundled` |

---

## 分步工作流程

### 第 1 步：添加依赖项

将代码资源钩子和工具链依赖项添加到您的包中。您必须直接从 **pub.dev** 获取这些依赖项。

您可以使用 CLI 自动添加：
```bash
dart pub add code_assets hooks native_toolchain_c record_use dev:ffigen
```

或者手动在目标包的 `pubspec.yaml` 中声明它们：
```yaml
dependencies:
  code_assets: ^1.0.0
  hooks: ^0.1.0
  native_toolchain_c: ^0.1.0
  record_use: ^0.6.0

dev_dependencies:
  ffigen: ^20.1.1
```

### 第 2 步：定义 C 规格

在 `lib/src/c_library.dart` 中定义您的目标 C 库编译元数据。这允许构建和链接钩子共享关于资源、名称和来源的单一事实来源。

### 第 3 步：实现构建和链接钩子脚本

在 `hook/build.dart` 中编写编译编排脚本，在 `hook/link.dart` 中编写死代码消除逻辑。

### 第 4 步：运行钩子周期

运行标准测试套件会动态地在后台启动构建和链接钩子生命周期：
```bash
dart test
```

---

## 选择集成方法

有两种主要方法可以在 Dart 中集成和交付 C/C++ 原生资源。选择与您的项目需求匹配的一种：

| 方面 | 方法 1：本地编译和树摇 | 方法 2：预编译下载 |
| :--- | :--- | :--- |
| **主要用例** | 当 C/C++ 源代码直接包含在包中，并且您希望最大程度地优化大小时。 | 当本地编译很慢/复杂，或者当避免开发者主机工具链要求时。 |
| **主机工具链要求** | 需要预先安装平台 C 编译器（Xcode 工具、MSVC、GCC）。 | 开发者/用户机器上不需要编译器设置。 |
| **二进制优化** | 高级。未使用的符号完全通过树摇，减小库大小。 | 标准。标准编译的二进制文件按原样打包。 |
| **离线设置** | 完全合规。可以完全离线工作。 | 需要网络访问下载库，具有离线回退。 |

---

## 方法 1：使用链接器树摇进行本地编译（推荐）

在此方法中，构建钩子调用本地工具链（GCC、Clang、MSVC）直接编译源文件。链接钩子随后使用编译器选项过滤输出符号，仅保留用户代码中调用的目标方法。这代表了 `pkgs/code_assets/example/sqlite` 下标准的 SQLite 模式。

### 先决条件主机编译器工具链

由于 `package:native_toolchain_c` 将实际动态编译委托给主机操作系统的默认工具链，开发机器**必须**预装以下之一编译器包：

*   **macOS**：Xcode 命令行工具。通过以下方式安装：
    ```bash
    xcode-select --install
    ```
*   **Linux**：GCC 或 Clang。通过以下方式安装：
    ```bash
    sudo apt install build-essential
    ```
*   **Windows**：MSVC（Microsoft Visual C++）。安装 **Visual Studio 安装程序** 并选择 **桌面开发 C++** 工作负载。

*注意：如果主机路径上没有兼容的工具链，构建钩子脚本将抛出编译执行异常。确保指定编译器约束或如果无法保证工具链，则采用方法 2。*

### C 源代码和绑定设置

假设一个定义了简单数学函数的 C 源代码位于 `third_party/sqlite/sqlite3.c`，其入口点头文件位于 `third_party/sqlite/sqlite3.h`：

```c
#ifndef SQLITE3_H_
#define SQLITE3_H_

const char *sqlite3_libversion(void);

#endif // SQLITE3_H_
```

我们使用一个程序化 FFIgen 脚本 (`tool/ffigen.dart`) 创建 FFI 绑定到 `lib/src/third_party/sqlite3.g.dart`，启用记录使用跟踪，并在 `lib/src/third_party/sqlite3.record_use_mapping.g.dart` 中生成查找元数据映射：

```dart
// AUTO-GENERATED FILE - DO NOT MODIFY.
// Generated via ffigen.

const recordUseMapping = {
  'sqlite3_libversion': 'sqlite3_libversion',
};
```

### 定义 C 库构建规范

在 `lib/src/c_library.dart` 中定义集中的库规范：

```dart
import 'package:native_toolchain_c/native_toolchain_c.dart';

/// SQLite 库的 C 构建规范。
final cLibrary = CLibrary(
  name: 'sqlite3',
  assetName: 'src/third_party/sqlite3.g.dart',
  sources: ['third_party/sqlite/sqlite3.c'],
);
```

### 实现 `hook/build.dart`

使用 `CLibrary.build` 实现 `hook/build.dart`。这会将库构建到动态库（例如 `.so`、`.dylib` 或 `.dll`）中，位于钩子的目标目录内：

```dart
import 'package:code_assets/code_assets.dart';
import 'package:hooks/hooks.dart';
import 'package:sqlite/src/c_library.dart';

void main(List<String> args) async {
  await build(args, (input, output) async {
    if (input.config.buildCodeAssets) {
      await cLibrary.build(
        input: input,
        output: output,
        defines: {
          if (input.config.code.targetOS == OS.windows)
            // 确保 C 函数在 Windows DLL 中显式导出
            'SQLITE_API': '__declspec(dllexport)',
        },
      );
    }
  });
}
```

### 实现 `hook/link.dart`

在 `hook/link.dart` 中实现链接优化阶段。这利用编译器树摇选项 (`LinkerOptions.treeshake`) 编译最小化、消除死代码的二进制文件，基于符号使用记录：

```dart
import 'package:hooks/hooks.dart';
import 'package:native_toolchain_c/native_toolchain_c.dart';
import 'package:record_use/record_use.dart';
import 'package:sqlite/src/c_library.dart';
import 'package:sqlite/src/third_party/sqlite3.record_use_mapping.g.dart';

void main(List<String> arguments) async {
  await link(arguments, (input, output) async {
    await cLibrary.link(
      input: input,
      output: output,
      linkerOptions: LinkerOptions.treeshake(
        // 将 Dart 方法引用映射回原始 C 符号名
        symbolsToKeep: input.recordedUses?.calls.keys.cast<Method>().map(
          (e) => recordUseMapping[e.name]!,
        ),
      ),
    );
  });
}
```

---

## 方法 2：下载预编译的动态库

另一种方法是在中央构建机器上预先编译二进制文件，将其存档，并在构建钩子执行期间下载目标二进制文件。这匹配了 `download_asset` 钩子包所展示的范例。

### 为什么下载预编译的二进制文件？

*   **主机约束**：本地编译大型 C/C++ 库需要完整的编译器设置（GCC、Xcode/SDKs、Visual Studio），而最终开发者的主机机器可能不具备这些。
*   **编译速度**：预编译下载执行速度快，以毫秒为单位，而编译过程可能需要长达数分钟。
*   **平台桥接**：允许避免跨编译约束，如果主机架构有限制。

---

### 实现预编译动态下载

我们配置我们的构建钩子以检测本地编译器标志（例如 `local_build`）。如果未指定，钩子将使用 `HttpClient` 拉取平台特定的库，计算 MD5 哈希以确认下载安全性，并注册二进制文件为 `CodeAsset`：

#### 1. 定义目标哈希 (`lib/src/hook_helpers/hashes.dart`)
在您的包源代码中定义每个平台文件的目标 MD5 哈希检查：

```dart
const assetHashes = {
  'libnative_add_macos_arm64.dylib': '4a88f50438a98402db2dbd47b59eb412',
  'libnative_add_linux_x64.so': '9f5e15043aa98402dcdbbd47b59ea520',
  'native_add_windows_x64.dll': 'a881e5043ba98402acdebd47b59fa321',
};
```

#### 2. 钩子下载辅助程序 (`lib/src/hook_helpers/download.dart`)
使用动态目标文件名匹配实现下载和完整性检查逻辑：

```dart
import 'dart:io';
import 'package:code_assets/code_assets.dart';
import 'package:crypto/crypto.dart';

const version = '1.0.0';

Uri downloadUri(String target) => Uri.parse(
  'https://github.com/my-org/my-native-repo/releases/download/$version/$target',
);

Future<File> downloadAsset(
  OS targetOS,
  Architecture targetArchitecture,
  Directory outputDir,
) async {
  final fileName = targetOS.dylibFileName('native_add_${targetOS.name}_${targetArchitecture.name}');
  final uri = downloadUri(fileName);
  
  final client = HttpClient()..findProxy = HttpClient.findProxyFromEnvironment;
  final request = await client.getUrl(uri);
  final response = await request.close();
  
  if (response.statusCode != 200) {
    throw ArgumentError('下载目标 $uri 失败：状态码 ${response.statusCode}');
  }
  
  final targetFile = File.fromUri(outputDir.uri.resolve(fileName));
  await targetFile.create(recursive: true);
  await response.pipe(targetFile.openWrite());
  
  return targetFile;
}

Future<String> hashAsset(File file) async {
  return md5.convert(await file.readAsBytes()).toString();
}
```

#### 3. 实现 `hook/build.dart`

编写包含本地编译回退的最终下载构建钩子：

```dart
import 'dart:io';
import 'package:code_assets/code_assets.dart';
import 'package:hooks/hooks.dart';
import 'package:my_download_package/src/hook_helpers/hashes.dart';
import 'package:my_download_package/src/hook_helpers/download.dart';
import 'package:native_toolchain_c/native_toolchain_c.dart';

void main(List<String> args) async {
  await build(args, (input, output) async {
    final localBuild = input.userDefines['local_build'] as bool? ?? false;

    if (localBuild) {
      final name = 'native_add_${input.config.code.targetOS.name}_${input.config.code.targetArchitecture.name}';
      final builder = CBuilder.library(
        name: name,
        assetName: 'native_add.dart',
        sources: ['src/native_add.c'],
      );
      await builder.run(input: input, output: output);
    } else {
      final targetOS = input.config.code.targetOS;
      final targetArch = input.config.code.targetArchitecture;
      final outputDir = Directory.fromUri(input.outputDirectory);

      final file = await downloadAsset(targetOS, targetArch, outputDir);

      final fileHash = await hashAsset(file);
      final expectedFileName = targetOS.dylibFileName('native_add_${targetOS.name}_${targetArch.name}');
      final expectedHash = assetHashes[expectedFileName];

      if (fileHash != expectedHash) {
        throw Exception(
          '安全不匹配：文件 $expectedFileName 哈希验证失败！ '
          '找到的哈希：$fileHash，期望的哈希：$expectedHash.'
        );
      }

      output.assets.code.add(
        CodeAsset(
          package: input.packageName,
          name: 'native_add.dart',
          linkMode: DynamicLoadingBundled(),
          file: file.uri,
        ),
      );
    }
  });
}
```

---

## 验证检查清单

在声明构建或链接钩子实现完成之前，始终执行以下检查：

### 1. 本地执行沙盒
运行单元测试并确认原生资源编译/链接过程完成，没有运行时或构建工具异常：
```bash
dart test
```

### 2. 验证目标输出
导航到您的包目标目录，并验证是否为主机系统创建了动态二进制资源：
*   **macOS**：验证 `.dart_tool/resources/` 或目标目录包含 `.dylib` 文件。
*   **Linux**：验证 `.dart_tool/resources/` 或目标目录包含 `.so` 文件。
*   **Windows**：验证 `.dart_tool/resources/` 或目标目录包含 `.dll` 文件。

### 3. 验证树摇剥离
为确保链接钩子实际上在剥离未使用的原生符号并压缩二进制打包大小，执行以下验证：

1. 编译 CLI/应用程序的生产捆绑包：
   ```bash
   dart build cli bin/main.dart
   ```
2. 导航到包含动态库的编译构建目录。
3. 查询导出的动态符号表：
   *   **macOS**:
       ```bash
       nm -gU build/cli/lib/libsqlite3.dylib
       ```
   *   **Linux**:
       ```bash
       nm -D build/cli/lib/libsqlite3.so
       ```
   *   **Windows**（使用 MSVC 开发者命令提示符）:
       ```cmd
       dumpbin /EXPORTS build\cli\lib\sqlite3.dll
       ```
4. **确认目标导出**：验证命令输出仅包含显式保留的入口点函数（例如 `sqlite3_libversion`），并且不输出任何未引用/剥离的符号。
5. **无捆绑场景**：如果应用程序没有导入或调用任何原生库的方法：
   - 验证链接钩子记录：`Skipping linking as no symbols are to be kept.`
   - 验证没有库被构建/放置在生产捆绑包中（没有生成 `.dylib`/`.so`/`.dll` 文件，从而节省捆绑包大小）。

### 4. 验证离线合规性（用户定义）
确认离线合规性完全激活，下载回退执行完美：

1. 在包的 `pubspec.yaml`（或工作区根 `pubspec.yaml`）中配置 `local_build: true` 定义：
   ```yaml
   hooks:
     user_defines:
       <your_package_name>:
         local_build: true
   ```
2. 禁用机器的网络适配器或在沙盒化的离线 shell 中运行。
3. 启动单元测试：
   ```bash
   dart test
   ```
4. 验证测试套件成功使用主机编译器编译本地源文件，没有编译错误，并且永远不会尝试网络下载请求。
