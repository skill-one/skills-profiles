# React Native 技能

针对 React Native 和 Expo 应用的综合最佳实践。涵盖性能、动画、UI 模式以及平台特定优化等多个类别的规则。

## 适用场景

参考以下指南时：

- 构建 React Native 或 Expo 应用
- 优化列表和滚动性能
- 使用 Reanimated 实现动画
- 处理图像和媒体
- 配置原生模块或字体
- 构建设含原生依赖的 Monorepo 项目

## 按优先级划分的规则类别

| 优先级 | 类别         | 影响   | 前缀               |
| -------- | ---------------- | -------- | -------------------- |
| 1        | List Performance | CRITICAL | `list-performance-`  |
| 2        | Animation        | HIGH     | `animation-`         |
| 3        | Navigation       | HIGH     | `navigation-`        |
| 4        | UI Patterns      | HIGH     | `ui-`                |
| 5        | State Management | MEDIUM   | `react-state-`       |
| 6        | Rendering        | MEDIUM   | `rendering-`         |
| 7        | Monorepo         | MEDIUM   | `monorepo-`          |
| 8        | Configuration    | LOW      | `fonts-`, `imports-` |

## 快速参考

### 1. 列表性能（关键）

- `list-performance-virtualize` - 使用 FlashList 处理大列表
- `list-performance-item-memo` - 记忆化列表项组件
- `list-performance-callbacks` - 稳定回调引用
- `list-performance-inline-objects` - 避免使用行内样式对象
- `list-performance-function-references` - 将函数提取到渲染函数外部
- `list-performance-images` - 优化列表中的图像
- `list-performance-item-expensive` - 将昂贵的工作移出列表项
- `list-performance-item-types` - 为异构列表使用列表项类型

### 2. 动画（高）

- `animation-gpu-properties` - 仅动画 transform 和 opacity 属性
- `animation-derived-value` - 使用 useDerivedValue 进行计算动画
- `animation-gesture-detector-press` - 使用 Gesture.Tap 而非 Pressable

### 3. 导航（高）

- `navigation-native-navigators` - 使用原生栈和原生标签页，而非 JS 导航器

### 4. UI 模式（高）

- `ui-expo-image` - 所有图像均使用 expo-image
- `ui-image-gallery` - 使用 Galeria 实现图像灯箱
- `ui-pressable` - 使用 Pressable 替代 TouchableOpacity
- `ui-safe-area-scroll` - 在 ScrollView 中处理安全区域
- `ui-scrollview-content-inset` - 使用 contentInset 处理页眉
- `ui-menus` - 使用原生上下文菜单
- `ui-native-modals` - 尽可能使用原生模态框
- `ui-measure-views` - 使用 onLayout，而非 measure()
- `ui-styling` - 使用 StyleSheet.create 或 Nativewind

### 5. 状态管理（中）

- `react-state-minimize` - 最小化状态订阅
- `react-state-dispatcher` - 使用 dispatcher 模式处理回调
- `react-state-fallback` - 首次渲染时显示回退内容
- `react-compiler-destructure-functions` - 为 React Compiler 进行解构
- `react-compiler-reanimated-shared-values` - 使用编译器处理共享值

### 6. 渲染（中）

- `rendering-text-in-text-component` - 将文本包裹在 Text 组件中
- `rendering-no-falsy-and` - 避免使用 falsy 的 && 进行条件渲染

### 7. Monorepo（中）

- `monorepo-native-deps-in-app` - 将原生依赖保留在应用包内
- `monorepo-single-dependency-versions` - 跨包使用单一依赖版本

### 8. 配置（低）

- `fonts-config-plugin` - 为自定义字体使用配置插件
- `imports-design-system-folder` - 整理设计系统导入
- `js-hoist-intl` - 提升 Intl 对象的创建

## 使用方法

阅读单个规则文件，获取详细的解释和代码示例：

```
rules/list-performance-virtualize.md
rules/animation-gpu-properties.md
```

每个规则文件均包含：

- 简要说明其重要性
- 包含错误代码示例及解释
- 包含正确代码示例及解释
- 额外上下文及参考资料

## 完整编译文档

包含所有规则扩展的完整指南：`AGENTS.md`
