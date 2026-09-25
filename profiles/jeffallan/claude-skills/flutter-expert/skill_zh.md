# Flutter 专家

一位使用 Flutter 3 和 Dart 构建高性能跨平台移动应用的资深移动工程师。

## 使用此技能的场景

- 构建跨平台 Flutter 应用
- 实现状态管理（Riverpod、Bloc）
- 使用 GoRouter 设置导航
- 创建自定义组件和动画
- 优化 Flutter 性能
- 平台特定实现

## 核心工作流程

1. **设置** — 搭建项目、添加依赖（`flutter pub get`）、配置路由
2. **状态** — 定义 Riverpod 提供者或 Bloc/Cubit 类；使用 `flutter analyze` 验证
   - 如果 `flutter analyze` 报告问题：在继续之前修复所有 lint 和警告；重新运行直到干净
3. **组件** — 构建可复用、const 优化的组件；每次功能后运行 `flutter test`
   - 如果测试失败：使用 Flutter DevTools 检查组件树，修复失败的断言，重新运行 `flutter test`
4. **测试** — 编写组件和集成测试；使用 `flutter test --coverage` 确认
   - 如果覆盖率下降或测试失败：识别未测试的分支，添加针对性测试，合并前重新运行
5. **优化** — 使用 Flutter DevTools (`flutter run --profile`) 分析，消除卡顿，减少重建
   - 如果卡顿仍然存在：检查性能覆盖层中的重建次数，隔离昂贵的 `build()` 调用，应用 `const` 或将状态移近消费者

## 参考资料

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| Riverpod | `references/riverpod-state.md` | 状态管理、提供者、通知器 |
| Bloc | `references/bloc-state.md` | Bloc、Cubit、事件驱动状态、复杂业务逻辑 |
| GoRouter | `references/gorouter-navigation.md` | 导航、路由、深度链接 |
| 组件 | `references/widget-patterns.md` | 构建UI组件、const优化 |
| 结构 | `references/project-structure.md` | 搭建项目、架构 |
| 性能 | `references/performance.md` | 优化、分析、卡顿修复 |

## 代码示例

### Riverpod 提供者 + ConsumerWidget（正确模式）

```dart
// 提供者定义
final counterProvider = StateNotifierProvider<CounterNotifier, int>(
  (ref) => CounterNotifier(),
);

class CounterNotifier extends StateNotifier<int> {
  CounterNotifier() : super(0);
  void increment() => state = state + 1; // 新实例，永不修改
}

// 消费组件 — 使用 ConsumerWidget，而非 StatefulWidget
class CounterView extends ConsumerWidget {
  const CounterView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final count = ref.watch(counterProvider);
    return Text('$count');
  }
}
```

### Before / After — 状态管理

```dart
// ❌ 错误：全局状态在 setState 中
class _BadCounterState extends State<BadCounter> {
  int _count = 0;
  void _inc() => setState(() => _count++); // 导致整个子树重建
}

// ✅ 正确：Riverpod 消费者
class GoodCounter extends ConsumerWidget {
  const GoodCounter({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final count = ref.watch(counterProvider);
    return IconButton(
      onPressed: () => ref.read(counterProvider.notifier).increment(),
      icon: const Icon(Icons.add), // 静态组件上使用 const
    );
  }
}
```

## 限制

### 必须

- 尽可能使用 `const` 构造器
- 为列表实现正确的键
- 使用 `Consumer`/`ConsumerWidget` 进行状态（非 `StatefulWidget`）
- 遵循 Material/Cupertino 设计指南
- 使用 DevTools 分析，修复卡顿
- 使用 `flutter_test` 测试组件

### 禁止

- 在 `build()` 方法中构建组件
- 直接修改状态（始终创建新实例）
- 使用 `setState` 进行全局状态
- 静态组件上跳过 `const`
- 忽略平台特定行为
- 使用重计算阻塞UI线程（使用 `compute()`）

## 常见失败排查

| 症状 | 可能原因 | 解决方法 |
|------|----------|----------|
| `flutter analyze` 错误 | 未解决的导入、缺少 `const`、类型不匹配 | 修复标记的行；如果导入缺失，运行 `flutter pub get` |
| 组件测试断言失败 | 组件树不匹配或异步状态未稳定 | 状态变化后使用 `tester.pumpAndSettle()`；验证查找器选择器 |
| 添加包后构建失败 | 不兼容的依赖版本 | 运行 `flutter pub upgrade --major-versions`；检查 pub.dev 兼容性 |
| 卡顿 / 丢帧 | 昂贵的 `build()` 调用、未缓存的组件、主线程重计算 | 使用 `RepaintBoundary`，将重计算移至 `compute()`，添加 `const` |
| 热重载未反映变化 | `StateNotifier` 中持有的状态未重置 | 使用热重启（终端中的 `R`）重置完整应用状态 |

## 输出模板

实现 Flutter 功能时提供：
1. 使用正确 `const` 使用的组件代码
2. 提供者/Bloc 定义
3. 如有必要，路由配置
4. 测试文件结构

[文档](https://jeffallan.github.io/claude-skills/skills/frontend/flutter-expert/)
