# 实现Flutter集成测试

## 目录
- [项目设置和依赖项](#项目设置和依赖项)
- [通过MCP进行交互式探索](#通过mcp进行交互式探索)
- [测试编写指南](#测试编写指南)
- [执行和分析](#执行和分析)
- [工作流：端到端集成测试](#工作流端到端集成测试)
- [示例](#示例)

## 项目设置和依赖项

配置项目以支持集成测试和Flutter Driver扩展。

1. 在`pubspec.yaml`中添加必要的开发依赖项：
   ```bash
   flutter pub add 'dev:integration_test:{"sdk":"flutter"}'
   flutter pub add 'dev:flutter_test:{"sdk":"flutter"}'
   ```
2. 在应用程序入口点（通常是`lib/main.dart`或专门的`lib/main_test.dart`）中启用Flutter Driver扩展：
   - 导入`package:flutter_driver/driver_extension.dart`。
   - 在`runApp()`之前调用`enableFlutterDriverExtension();`。
3. 在应用程序代码中的关键组件上添加`Key`参数（例如，`ValueKey('login_button'）），以确保在测试期间可靠地定位。

## 通过MCP进行交互式探索

使用Dart/Flutter MCP服务器工具在编写静态测试之前交互式地探索和操作应用程序状态。

- **启动**：执行`launch_app`并使用`target: "lib/main_test.dart"`启动应用程序并获取DTD URI。
- **检查**：执行`get_widget_tree`以发现可用的`Key`、`Text`节点和组件`Type`。
- **交互**：执行`tap`、`enter_text`和`scroll`以模拟用户流程。
- **等待**：在导航或触发动画时，始终执行`waitFor`或使用`get_health`验证状态。
- **解决未挂载组件的问题**：如果组件在树中找不到，它可能是在`SliverList`或`ListView`中延迟加载的。执行`scroll`或`scrollIntoView`以强制组件挂载，然后再与之交互。

## 测试编写指南

使用`flutter_test` API范例来组织集成测试。

- 在项目根目录下创建一个专用的`integration_test/`目录。
- 使用`<name>_test.dart`约定命名所有测试文件。
- 在`main()`的开头调用`IntegrationTestWidgetsFlutterBinding.ensureInitialized();`来初始化绑定。
- 使用`await tester.pumpWidget(MyApp());`加载应用程序UI。
- 在交互（如`tester.tap()`）之后使用`await tester.pumpAndSettle();`触发帧并等待动画完成。
- 使用`expect(find.byKey(ValueKey('foo')), findsOneWidget);`或`findsNothing`断言组件可见性。
- 使用`await tester.scrollUntilVisible(itemFinder, 500.0, scrollable: listFinder);`滚动到特定的屏幕外组件。

**针对遗留`flutter_driver`的 条件逻辑**：
- 如果维护或迁移遗留的`flutter_driver`测试，请使用`driver.waitFor()`、`driver.waitForAbsent()`、`driver.tap()`和`driver.scroll()`而不是`WidgetTester` API。

## 执行和分析

使用`flutter drive`命令执行测试。需要一个位于`test_driver/integration_test.dart`的主驱动脚本，该脚本调用`integrationDriver()`。

**条件执行目标**：
- **如果要在Chrome上测试**：在一个单独的终端中启动`chromedriver --port=4444`，然后运行：
  `flutter drive --driver=test_driver/integration_test.dart --target=integration_test/app_test.dart -d chrome`
- **如果要在无头Web上测试**：使用`-d web-server`运行。
- **如果要在Android（本地）上测试**：运行`flutter drive --driver=test_driver/integration_test.dart --target=integration_test/app_test.dart`。
- **如果要在Firebase Test Lab（Android）上测试**：
  1. 构建调试APK：`flutter build apk --debug`
  2. 构建测试APK：`./gradlew app:assembleAndroidTest`
  3. 将两个APK上传到Firebase Test Lab控制台。

## 工作流：端到端集成测试

复制并遵循此清单来实施和验证集成测试。

- [ ] **任务进度：设置**
  - [ ] 将`integration_test`和`flutter_test`添加到`pubspec.yaml`。
  - [ ] 将`enableFlutterDriverExtension()`注入应用程序入口点。
  - [ ] 为目标组件分配`ValueKey`。
- [ ] **任务进度：探索**
  - [ ] 通过MCP运行`launch_app`。
  - [ ] 使用`get_widget_tree`映射组件树。
  - [ ] 使用MCP工具验证交互路径（`tap`、`enter_text`）。
- [ ] **任务进度：编写**
  - [ ] 创建`integration_test/app_test.dart`。
  - [ ] 使用`WidgetTester` API编写测试用例。
  - [ ] 创建`test_driver/integration_test.dart`并包含`integrationDriver()`。
- [ ] **任务进度：执行和反馈循环**
  - [ ] 运行`flutter drive --driver=test_driver/integration_test.dart --target=integration_test/app_test.dart`。
  - [ ] **反馈循环**：查看测试输出 -> 如果发生`PumpAndSettleTimedOutException`，请检查无限动画 -> 如果找不到组件，请添加`scrollUntilVisible` -> 重新运行测试直至通过。

## 示例

### 标准集成测试 (`integration_test/app_test.dart`)

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:my_app/main.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('端到端测试', () {
    testWidgets('点击浮动操作按钮，验证计数器', (tester) async {
      // 加载应用组件。
      await tester.pumpWidget(const MyApp());

      // 验证计数器从0开始。
      expect(find.text('0'), findsOneWidget);

      // 查找要点击的浮动操作按钮。
      final fab = find.byKey(const ValueKey('increment'));

      // 模拟点击浮动操作按钮。
      await tester.tap(fab);

      // 触发帧并等待动画完成。
      await tester.pumpAndSettle();

      // 验证计数器增加1。
      expect(find.text('1'), findsOneWidget);
    });
  });
}
```

### 主驱动脚本 (`test_driver/integration_test.dart`)

```dart
import 'package:integration_test/integration_test_driver.dart';

Future<void> main() => integrationDriver();
```

### 性能分析驱动脚本 (`test_driver/perf_driver.dart`)

如果您在测试操作中包装了`binding.traceAction()`以捕获性能指标，请使用此驱动脚本。

```dart
import 'package:flutter_driver/flutter_driver.dart' as driver;
import 'package:integration_test/integration_test_driver.dart';

Future<void> main() {
  return integrationDriver(
    responseDataCallback: (data) async {
      if (data != null) {
        final timeline = driver.Timeline.fromJson(
          data['scrolling_timeline'] as Map<String, dynamic>,
        );

        final summary = driver.TimelineSummary.summarize(timeline);

        await summary.writeTimelineToFile(
          'scrolling_timeline',
          pretty: true,
          includeSummary: true,
        );
      }
    },
  );
}
```
