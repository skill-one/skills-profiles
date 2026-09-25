# 测试和模拟 Dart 应用

## 目录
- [为可测试性重构代码](#为可测试性重构代码)
- [管理依赖项](#管理依赖项)
- [生成模拟对象](#生成模拟对象)
- [实现单元测试](#实现单元测试)
- [工作流：创建和运行模拟测试](#工作流创建和运行模拟测试)
- [示例](#示例)

## 为可测试性重构代码
设计 Dart 类以支持依赖注入。隔离复杂的外部依赖项（例如 API 客户端或数据库），以便在测试期间可以用模拟对象替换它们。

- 通过类构造函数注入外部服务（例如 `http.Client`）。
- 使用 `Uri.parse(string)` 严格将 URL 表示为 `Uri` 对象。
- 利用 Dart 的面向对象特性（类、混入）定义清晰的外部交互接口。

## 管理依赖项
使用 `pubspec.yaml` 文件配置必要的测试和代码生成包。

- 使用 `dart pub add http` 添加运行时依赖项（例如 `package:http`）。
- 使用 `dart pub add dev:test dev:mockito dev:build_runner` 添加测试依赖项。
- 使用前缀导入 HTTP 库以避免命名空间冲突：`import 'package:http/http.dart' as http;`。

## 生成模拟对象
使用 `package:mockito` 和 `build_runner` 自动生成模拟类以用于固定场景和行为验证。

- 始终使用 `@GenerateNiceMocks` 注解（相对于 `@GenerateMocks` 更好，以避免遗漏存根异常）。
- 将注解放置在测试文件中，传递 `MockSpec<Type>()` 对象的列表。
- 使用 `.mocks.dart` 扩展名导入生成的文件。
- 执行 `build_runner` 生成模拟文件：`dart run build_runner build`。

## 实现单元测试
使用生成的模拟对象隔离待测系统。使用 `package:test` 构建测试套件。

- **存根：** 在与待测系统交互之前配置模拟行为。
  - 使用 `when(mock.method()).thenReturn(value)` 用于同步方法。
  - **关键：** 始终使用 `thenAnswer((_) async => value)` 用于返回 `Future` 或 `Stream` 的方法。永远不要使用 `thenReturn` 用于异步返回。
- **验证：** 断言待测系统是否正确与模拟对象交互。
  - 使用 `verify(mock.method()).called(1)` 检查确切的调用次数。
  - 使用参数匹配器（如 `any`、`anyNamed` 或 `captureAny`）进行灵活的验证。

## 工作流：创建和运行模拟测试

使用以下清单来实施和验证模拟单元测试。

### 任务进度
- [ ] 1. 确定要模拟的外部依赖项（例如 `http.Client`）。
- [ ] 2. 将依赖项注入目标类构造函数。
- [ ] 3. 创建测试文件（例如 `target_test.dart`）并添加 `@GenerateNiceMocks([MockSpec<Dependency>()])`。
- [ ] 4. 添加 `part` 或 `import` 指令以导入生成的 `.mocks.dart` 文件。
- [ ] 5. 运行 `dart run build_runner build` 以生成模拟类。
- [ ] 6. 使用 `group()` 和 `test()` 编写测试用例。
- [ ] 7. 使用 `when()` 存根所需行为。
- [ ] 8. 执行目标方法。
- [ ] 9. 使用 `verify()` 验证交互，使用 `expect()` 断言结果。
- [ ] 10. 使用 `dart test` 运行测试套件。

### 反馈循环：测试失败
如果测试失败或 `build_runner` 遇到错误：
1. **运行验证器：** 执行 `dart test` 或 `dart run build_runner build`。
2. **审查错误：** 检查是否有遗漏的存根、不匹配的参数匹配器或生成的文件中的语法错误。
3. **修复：**
   - 如果模拟方法抛出意外的 null 错误，请确保使用了 `@GenerateNiceMocks`。
   - 如果异步存根抛出 `ArgumentError`，请将 `thenReturn` 更改为 `thenAnswer`。
   - 如果 `build_runner` 失败，请确保 `.mocks.dart` 导入与文件名完全匹配。
4. 重复操作，直到所有测试通过。

## 示例

### 高保真模拟和测试示例

**1. 待测系统 (`lib/api_service.dart`)**
```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  final http.Client client;

  ApiService(this.client);

  Future<String> fetchData(String urlString) async {
    final uri = Uri.parse(urlString);
    final response = await client.get(uri);

    if (response.statusCode == 200) {
      return jsonDecode(response.body)['data'];
    } else {
      throw Exception('Failed to load data');
    }
  }
}
```

**2. 测试实现 (`test/api_service_test.dart`)**
```dart
import 'package:test/test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:http/http.dart' as http;
import 'package:my_app/api_service.dart';

// 生成 http.Client 的模拟类
@GenerateNiceMocks([MockSpec<http.Client>()])
import 'api_service_test.mocks.dart';

void main() {
  group('ApiService', () {
    late ApiService apiService;
    late MockClient mockHttpClient;

    setUp(() {
      mockHttpClient = MockClient();
      apiService = ApiService(mockHttpClient);
    });

    test('returns data if the http call completes successfully', () async {
      // Arrange: 使用 thenAnswer 存根异步 HTTP GET 请求
      when(mockHttpClient.get(any)).thenAnswer(
        (_) async => http.Response('{"data": "Success"}', 200),
      );

      // Act
      final result = await apiService.fetchData('https://api.example.com/data');

      // Assert
      expect(result, 'Success');

      // 验证模拟是否被正确调用
      verify(mockHttpClient.get(Uri.parse('https://api.example.com/data'))).called(1);
    });

    test('throws an exception if the http call completes with an error', () {
      // Arrange
      when(mockHttpClient.get(any)).thenAnswer(
        (_) async => http.Response('Not Found', 404),
      );

      // Act & Assert
      expect(
        apiService.fetchData('https://api.example.com/data'),
        throwsException,
      );
    });
  });
}
```
