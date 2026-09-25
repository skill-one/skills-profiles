# Flutter 开发指南

一份实用的指南，用于使用 Flutter 3 和 Dart 构建跨平台应用程序。重点关注经过验证的模式、状态管理和性能优化。

## 快速参考

### Widget 模式

| 目的 | 组件 |
|------|------|
| 简单状态管理 | `StateProvider` + `ConsumerWidget` |
| 复杂状态管理 | `NotifierProvider` / `Bloc` |
| 异步数据 | `FutureProvider` / `AsyncNotifierProvider` |
| 实时流 | `StreamProvider` |
| 导航 | `GoRouter` + `context.go/push` |
| 响应式布局 | `LayoutBuilder` + 断点 |
| 列表显示 | `ListView.builder` |
| 复杂滚动 | `CustomScrollView` + Slivers |
| Hooks | `HookWidget` + `useState/useEffect` |
| 表单 | `Form` + `TextFormField` + 验证 |

### 性能模式

| 目的 | 解决方案 |
|------|--------|
| 防止重建 | `const` 构造函数 |
| 选择性更新 | `ref.watch(provider.select(...))` |
| 隔离重绘 | `RepaintBoundary` |
| 懒加载列表 | `ListView.builder` |
| 重计算 | `compute()` 隔离 |
| 图片缓存 | `cached_network_image` |

## 核心原则

### Widget 优化
- 尽可能使用 `const` 构造函数
- 将静态 Widget 提取到单独的 const 类中
- 使用 `Key` 对列表项（ValueKey, ObjectKey）
- 优先使用 `ConsumerWidget` 而不是 `StatefulWidget` 来管理状态

### 状态管理
- 使用 Riverpod 进行依赖注入和简单状态
- 使用 Bloc/Cubit 进行事件驱动的工作流程和复杂逻辑
- 不要直接修改状态（创建新实例）
- 使用 `select()` 来最小化重建

### 布局
- 8pt 间距增量（8, 16, 24, 32, 48）
- 响应式断点：移动端（<650），平板（650-1100），桌面（>1100）
- 使用灵活布局支持所有屏幕尺寸
- 遵循 Material 3 / Cupertino 设计指南

### 性能
- 在优化前使用 DevTools 进行分析
- 目标是 <16ms 帧时间以实现 60fps
- 使用 `RepaintBoundary` 处理复杂动画
- 使用 `compute()` 外包重计算任务

## 检查清单

### Widget 最佳实践
- [ ] 所有静态 Widget 使用 `const` 构造函数
- [ ] 列表项使用正确的 `Key`
- [ ] 使用 `ConsumerWidget` 处理依赖状态的 Widget
- [ ] 不要在 `build()` 方法中构建 Widget
- [ ] 将可重用的 Widget 提取到单独文件

### 状态管理
- [ ] 使用不可变状态对象
- [ ] 使用 `select()` 进行粒度化重建
- [ ] 正确的 Provider 范围
- [ ] 处理控制器和订阅的销毁
- [ ] 处理加载/错误状态

### 导航
- [ ] 使用 GoRouter 和类型化路由
- [ ] 通过重定向实现认证保护
- [ ] 支持深度链接
- [ ] 跨路由状态保留

### 性能
- [ ] 分析模式测试（`flutter run --profile`）
- [ ] <16ms 帧渲染时间
- [ ] 无不必要的重建（DevTools 检查）
- [ ] 图片缓存和缩放
- [ ] 重计算在隔离中进行

### 测试
- [ ] UI 组件的 Widget 测试
- [ ] 业务逻辑的单元测试
- [ ] 用户流程的集成测试
- [ ] 使用 `blocTest()` 的 Bloc 测试

## 参考

| 主题 | 参考 |
|------|------|
| Widget 模式，const 优化，响应式布局 | [Widget Patterns](references/widget-patterns.md) |
| Riverpod 提供者，通知器，异步状态 | [Riverpod State Management](references/riverpod-state.md) |
| Bloc，Cubit，事件驱动状态 | [Bloc State Management](references/bloc-state.md) |
| GoRouter 设置，路由，深度链接 | [GoRouter Navigation](references/gorouter-navigation.md) |
| 基于功能的结构，依赖项 | [Project Structure](references/project-structure.md) |
| 分析，const 优化，DevTools | [Performance Optimization](references/performance.md) |
| Widget 测试，集成测试，模拟 | [Testing Strategies](references/testing.md) |
| iOS/Android/Web 特定实现 | [Platform Integration](references/platform-specific.md) |
| 隐式/显式动画，Hero，过渡 | [Animations](references/animations.md) |
| Dio，拦截器，错误处理，缓存 | [Networking](references/networking.md) |
| 表单验证，FormField，输入格式化器 | [Forms](references/forms.md) |
| i18n，flutter_localizations，intl | [Localization](references/localization.md) |

---

Flutter、Dart、Material Design 和 Cupertino 分别是 Google LLC 和 Apple Inc. 的商标。Riverpod、Bloc 和 GoRouter 是其各自维护者的开源包。
