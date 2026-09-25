# 编写 Flutter 组件测试

## 目录
- [设置与配置](#设置与配置)
- [核心组件](#核心组件)
- [工作流：实现组件测试](#工作流实现组件测试)
- [交互与状态管理](#交互与状态管理)
- [示例](#示例)

## 设置与配置

在编写组件测试之前，请确保测试环境已正确配置。

1. 将 `flutter_test` 依赖项添加到 `pubspec.yaml` 的 `dev_dependencies` 部分。
2. 将所有测试文件放置在项目根目录下的 `test/` 目录中。
3. 将所有测试文件名以 `_test.dart` 结尾（例如，`widget_test.dart`）。

## 核心组件

使用以下 `flutter_test` 组件与组件树进行交互和验证：

*   **`WidgetTester`**：测试环境中构建和交互组件的主要接口。由 `testWidgets()` 函数自动提供。
*   **`Finder`**：在测试环境中定位组件（例如，`find.text('Submit')`，`find.byType(TextField)`，`find.byKey(Key('submit_btn'))`）。
*   **`Matcher`**：验证由 `Finder` 定位的组件的存在或状态（例如，`findsOneWidget`，`findsNothing`，`findsNWidgets(2)`，`matchesGoldenFile`）。

## 工作流：实现组件测试

在实现新的组件测试时，复制以下检查清单以跟踪进度。

### 任务进度
- [ ] **步骤 1：定义测试**。使用 `testWidgets('description', (WidgetTester tester) async { ... })`。
- [ ] **步骤 2：构建组件**。调用 `await tester.pumpWidget(MyWidget())` 以渲染 UI。如果组件需要继承方向或主题数据，请将其包装在 `MaterialApp` 或 `Directionality` 组件中。
- [ ] **步骤 3：定位元素**。为目标组件实例化 `Finder` 对象。
- [ ] **步骤 4：验证初始状态**。使用 `expect(finder, matcher)` 验证初始渲染。
- [ ] **步骤 5：模拟交互**。执行手势或输入（例如，`await tester.tap(buttonFinder)`）。
- [ ] **步骤 6：重建树**。调用 `await tester.pump()` 或 `await tester.pumpAndSettle()` 以处理状态变化。
- [ ] **步骤 7：验证更新状态**。使用 `expect()` 验证交互后的 UI。
- [ ] **步骤 8：运行和验证**。执行 `flutter test test/your_test_file_test.dart`。
- [ ] **步骤 9：反馈循环**。查看测试输出 -> 识别失败的匹配器 -> 调整组件逻辑或测试断言 -> 重新运行直到通过。

## 交互与状态管理

根据要测试的交互类型或状态变化应用以下条件逻辑：

*   **如果测试静态渲染**：调用 `await tester.pumpWidget()` 一次，然后立即运行 `expect()` 断言。
*   **如果测试标准状态变化（例如，按钮点击）**：
    1. 调用 `await tester.tap(finder)`。
    2. 调用 `await tester.pump()` 以触发单个帧重建。
*   **如果测试动画、过渡或异步 UI 更新**：
    1. 触发操作（例如，`await tester.drag(finder, Offset(500, 0))`）。
    2. 调用 `await tester.pumpAndSettle()` 以重复泵送帧，直到没有更多帧被调度（动画完成）。
*   **如果测试文本输入**：调用 `await tester.enterText(textFieldFinder, 'Input string')`。
*   **如果测试动态或长列表中的项**：调用 `await tester.scrollUntilVisible(itemFinder, 500.0, scrollable: listFinder)` 以确保目标组件在交互前已渲染。

## 示例

### 高保真组件测试实现

**目标组件 (`lib/todo_list.dart`):**
```dart
import 'package:flutter/material.dart';

class TodoList extends StatefulWidget {
  const TodoList({super.key});

  @override
  State<TodoList> createState() => _TodoListState();
}

class _TodoListState extends State<TodoList> {
  final todos = <String>[];
  final controller = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        body: Column(
          children: [
            TextField(controller: controller),
            Expanded(
              child: ListView.builder(
                itemCount: todos.length,
                itemBuilder: (context, index) {
                  final todo = todos[index];
                  return Dismissible(
                    key: Key('$todo$index'),
                    onDismissed: (_) => setState(() => todos.removeAt(index)),
                    child: ListTile(title: Text(todo)),
                  );
                },
              ),
            ),
          ],
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: () {
            setState(() {
              todos.add(controller.text);
              controller.clear();
            });
          },
          child: const Icon(Icons.add),
        ),
      ),
    );
  }
}
```

**测试实现 (`test/todo_list_test.dart`):**
```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:my_app/todo_list.dart';

void main() {
  testWidgets('Add and remove a todo item', (WidgetTester tester) async {
    // 1. 构建组件
    await tester.pumpWidget(const TodoList());

    // 2. 验证初始状态
    expect(find.byType(ListTile), findsNothing);

    // 3. 在 TextField 中输入文本
    await tester.enterText(find.byType(TextField), 'Buy groceries');

    // 4. 点击添加按钮
    await tester.tap(find.byType(FloatingActionButton));

    // 5. 重建组件以反映新状态
    await tester.pump();

    // 6. 验证项已添加
    expect(find.text('Buy groceries'), findsOneWidget);

    // 7. 滑动项以将其移除
    await tester.drag(find.byType(Dismissible), const Offset(500, 0));

    // 8. 构建组件直到移除动画结束
    await tester.pumpAndSettle();

    // 9. 验证项已移除
    expect(find.text('Buy groceries'), findsNothing);
  });
}
```
