# 实现Dart和Flutter测试覆盖率

## 目录
- [测试基础](#测试基础)
- [覆盖率指令](#覆盖率指令)
- [工作流：配置和生成覆盖率报告](#工作流配置和生成覆盖率报告)
- [工作流：高级手动覆盖率收集](#工作流高级手动覆盖率收集)
- [示例](#示例)

## 测试基础

使用标准的Dart测试范式来组织你的测试套件。对于Dart项目使用`package:test`，对于Flutter项目使用`flutter_test`。

- **单元测试**：验证单个函数、方法或类。
- **组件/组件测试**：使用模拟对象(`package:mockito`)验证组件行为、布局和交互。
- **集成测试**：在模拟或真实设备上验证整个应用流程。

## 覆盖率指令

使用内联注释从覆盖率指标中排除特定的行、块或整个文件。在格式化时传递`--check-ignore`标志来强制执行这些指令。

- 忽略单行：`// coverage:ignore-line`
- 忽略代码块：`// coverage:ignore-start` 和 `// coverage:ignore-end`
- 忽略整个文件：`// coverage:ignore-file`

## 工作流：配置和生成覆盖率报告

按照此顺序工作流程添加覆盖率包、执行测试并生成LCOV报告。

**任务进度清单：**
- [ ] 1. 将`coverage`作为`dev_dependency`添加。
- [ ] 2. 执行自动覆盖率脚本。
- [ ] 3. 验证LCOV输出。

### 1. 添加依赖项
将`coverage`包作为`dev_dependency`添加到你的项目中。不要将其添加到标准依赖项中。

如果在一个标准的Dart项目中工作：
```bash
dart pub add dev:coverage
```

如果在一个Flutter项目中工作：
```bash
flutter pub add dev:coverage
```

### 2. 收集覆盖率并生成LCOV
使用捆绑的`test_with_coverage`脚本。此脚本自动运行所有测试，从Dart VM收集JSON覆盖率数据，并将其格式化为LCOV报告。

```bash
dart run coverage:test_with_coverage
```
*注意：如果在一个Dart工作区（单体仓库）中工作，请明确指定测试目录（例如，`dart run coverage:test_with_coverage -- pkgs/foo/test pkgs/bar/test`）。*

### 3. 反馈循环：验证输出
**运行验证器 -> 审查错误 -> 修复：**
1. 验证在项目根目录下是否创建了`coverage/`目录。
2. 确保`coverage/coverage.json`（原始数据）和`coverage/lcov.info`（格式化报告）存在。
3. 如果特定文件的覆盖率缺失，请确保它们被你的测试文件导入和执行，或者如果它们有意排除，请添加`// coverage:ignore-file`。

## 工作流：高级手动覆盖率收集

如果你需要VM服务的粒度控制、隔离暂停或需要分支/函数级别的覆盖率，请使用手动收集工作流。

**任务进度清单：**
- [ ] 1. 运行带有VM服务启用的测试。
- [ ] 2. 收集原始JSON覆盖率。
- [ ] 3. 将JSON格式化为LCOV。

### 1. 运行带有VM服务的测试
执行测试时暂停隔离退出，并在特定端口（例如，8181）上暴露VM服务。

```bash
dart run --pause-isolates-on-exit --disable-service-auth-codes --enable-vm-service=8181 test &
```

### 2. 收集原始覆盖率
从运行的VM服务中提取覆盖率数据，并将其输出到JSON文件。

```bash
dart run coverage:collect_coverage --wait-paused --uri=http://127.0.0.1:8181/ -o coverage/coverage.json --resume-isolates
```
*可选：追加`--function-coverage`和`--branch-coverage`以收集更深层次的指标（需要Dart VM 2.17.0+）。*

### 3. 格式化为LCOV
将原始JSON数据转换为标准的LCOV格式。

```bash
dart run coverage:format_coverage --packages=.dart_tool/package_config.json --lcov -i coverage/coverage.json -o coverage/lcov.info --check-ignore
```

## 示例

### 示例：`pubspec.yaml`配置
确保你的`pubspec.yaml`严格地将`coverage`包放在`dev_dependencies`下。

```yaml
name: my_dart_app
environment:
  sdk: ^3.0.0

dependencies:
  path: ^1.8.0

dev_dependencies:
  test: ^1.24.0
  coverage: ^1.15.0
```

### 示例：应用忽略指令
使用忽略指令来防止生成的代码或不测试的边缘情况降低覆盖率分数。

```dart
// coverage:ignore-file
import 'package:meta/meta.dart';

class SystemConfig {
  final String env;

  SystemConfig(this.env);

  // coverage:ignore-start
  void legacyInit() {
    print('Deprecated initialization');
  }
  // coverage:ignore-end

  bool isProduction() {
    if (env == 'prod') return true;
    return false; // coverage:ignore-line
  }
}
```
