# 测试 Dart 和 Flutter 应用

## 目录
- [组织测试文件](#组织测试文件)
- [编写测试](#编写测试)
- [执行测试](#执行测试)
- [测试实现工作流](#测试实现工作流)
- [示例](#示例)

## 组织测试文件
组织测试文件以镜像 `lib` 目录结构，以保持可预测性。

* 将所有测试代码放置在包根目录下的 `test` 目录中。
* 将所有测试文件名末尾添加 `_test.dart`（例如，`lib/src/utils.dart` 应在 `test/src/utils_test.dart` 中进行测试）。
* 如果编写集成测试，请将它们放置在包根目录下的 `integration_test` 目录中。

## 编写测试
使用 `package:test` 作为 Dart 应用的标准测试库。

* 导入 `package:test/test.dart`（对于 Flutter，导入 `package:flutter_test/flutter_test.dart`）。
* 使用 `group()` 函数按功能分组相关测试，以提供共享上下文。
* 使用 `test()` 函数定义单个测试用例。
* 使用 `expect()` 函数和匹配器（例如 `equals()`、`isTrue`、`throwsA()`）验证结果。
* 使用标准的 `async`/`await` 语法编写异步测试。测试运行器会自动等待 `Future` 完成。
* 使用 `setUp()` 和 `tearDown()` 回调管理测试设置和清理。
* 如果测试依赖注入的代码，请使用 `package:mockito` 与 `package:test` 一起生成模拟对象、配置固定场景并验证交互。

## 执行测试
根据项目类型和测试位置选择合适的测试运行器。

* 如果在纯 Dart 项目上工作，请使用 `dart test` 命令执行测试。
* 如果在 Flutter 项目上工作，请使用 `flutter test` 命令执行测试。
* 如果运行集成测试，请显式指定目录路径，因为默认运行器会忽略它：`dart test integration_test` 或 `flutter test integration_test`。

## 测试实现工作流

在实现新的测试套件时，请遵循此顺序工作流。将检查清单复制到跟踪进度。

### 任务进度
- [ ] 1. 在 `test/` 目录中创建测试文件，确保带有 `_test.dart` 后缀。
- [ ] 2. 导入 `package:test/test.dart` 和目标库。
- [ ] 3. 定义 `main()` 函数。
- [ ] 4. 使用 `setUp()` 初始化共享资源或模拟对象。
- [ ] 5. 使用 `group()` 按功能分组编写 `test()` 用例。
- [ ] 6. 使用适当的 CLI 命令执行测试套件。
- [ ] 7. **反馈循环**：运行测试 -> 查看失败时的堆栈跟踪 -> 修复实现或断言 -> 重新运行直到通过。

## 示例

### 标准单元测试套件
演示分组、设置、同步和异步测试。

```dart
import 'package:test/test.dart';
import 'package:my_package/calculator.dart';

void main() {
  group('Calculator', () {
    late Calculator calc;

    setUp(() {
      calc = Calculator();
    });

    test('adds two numbers correctly', () {
      expect(calc.add(2, 3), equals(5));
    });

    test('handles asynchronous operations', () async {
      final result = await calc.fetchRemoteValue();
      expect(result, isNotNull);
      expect(result, greaterThan(0));
    });
  });
}
```

### 使用 Mockito 进行模拟
演示配置模拟对象以进行依赖注入测试。

```dart
import 'package:test/test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:my_package/api_client.dart';
import 'package:my_package/data_service.dart';

// 使用 build_runner 生成模拟：dart run build_runner build
@GenerateNiceMocks([MockSpec<ApiClient>()])
import 'data_service_test.mocks.dart';

void main() {
  group('DataService', () {
    late MockApiClient mockApiClient;
    late DataService dataService;

    setUp(() {
      mockApiClient = MockApiClient();
      dataService = DataService(apiClient: mockApiClient);
    });

    test('returns parsed data on successful API call', () async {
      // 配置模拟
      when(mockApiClient.get('/data')).thenAnswer((_) async => '{"id": 1}');

      // 执行待测试系统
      final result = await dataService.fetchData();

      // 验证结果和交互
      expect(result.id, equals(1));
      verify(mockApiClient.get('/data')).called(1);
    });
  });
}
```
