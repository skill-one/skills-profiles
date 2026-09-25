# React Native 技能

React Native 和 Expo 应用的最佳实践综合指南。包含涵盖性能、动画、UI 模式和平台特定优化的多个类别的规则。

## 何时应用

在以下情况下参考这些指南：

- 构建 React Native 或 Expo 应用
- 优化列表和滚动性能
- 使用 Reanimated 实现动画
- 处理图像和媒体
- 配置原生模块或字体
- 构建具有原生依赖项的 monorepo 项目

## 按优先级分类的规则类别

| 优先级 | 类别         | 影响   | 前缀               |
| ------ | ------------ | ------ | ------------------ |
| 1      | 列表性能     | 关键   | `list-performance-` |
| 2      | 动画         | 高     | `animation-`       |
| 3      | 导航         | 高     | `navigation-`      |
| 4      | UI 模式      | 高     | `ui-`              |
| 5      | 状态管理     | 中     | `react-state-`     |
| 6      | 渲染         | 中     | `rendering-`       |
| 7      | Monorepo     | 中     | `monorepo-`        |
| 8      | 配置         | 低     | `fonts-`, `imports-` |

## 快速参考

### 1. 列表性能 (关键)

- `list-performance-virtualize` - 使用 FlashList 处理大型列表
- `list-performance-item-memo` - 保留列表项组件
- `list-performance-callbacks` - 稳定回调引用
- `list-performance-inline-objects` - 避免内联样式对象
- `list-performance-function-references` - 将函数提取到渲染外部
- `list-performance-images` - 优化列表中的图像
- `list-performance-item-expensive` - 将昂贵操作移出列表项
- `list-performance-item-types` - 使用列表项类型处理异构列表

### 2. 动画 (高)

- `animation-gpu-properties` - 仅对 transform 和 opacity 进行动画
- `animation-derived-value` - 使用 useDerivedValue 处理计算动画
- `animation-gesture-detector-press` - 使用 Gesture.Tap 而不是 Pressable

### 3. 导航 (高)

- `navigation-native-navigators` - 优先使用原生堆栈和原生标签页而非 JS 导航器

### 4. UI 模式 (高)

- `ui-expo-image` - 所有图像使用 expo-image
- `ui-image-gallery` - 使用 Galeria 处理图像灯箱
- `ui-pressable` - 使用 Pressable 而不是 TouchableOpacity
- `ui-safe-area-scroll` - 处理 ScrollViews 中的安全区域
- `ui-scrollview-content-inset` - 使用 contentInset 处理标题
- `ui-menus` - 使用原生上下文菜单
- `ui-native-modals` - 尽可能使用原生模态框
- `ui-measure-views` - 使用 onLayout 而不是 measure()
- `ui-styling` - 使用 StyleSheet.create 或 Nativewind

### 5. 状态管理 (中)

- `react-state-minimize` - 最小化状态订阅
- `react-state-dispatcher` - 使用 dispatcher 模式处理回调
- `react-state-fallback` - 首次渲染时显示回退内容
- `react-compiler-destructure-functions` - 为 React 编译器进行解构
- `react-compiler-reanimated-shared-values` - 使用编译器处理共享值

### 6. 渲染 (中)

- `rendering-text-in-text-component` - 将文本包裹在 Text 组件中
- `rendering-no-falsy-and` - 避免使用 falsy && 进行条件渲染

### 7. Monorepo (中)

- `monorepo-native-deps-in-app` - 将原生依赖保持在应用包中
- `monorepo-single-dependency-versions` - 在所有包中使用单一版本

### 8. 配置 (低)

- `fonts-config-plugin` - 使用配置插件处理自定义字体
- `imports-design-system-folder` - 组织设计系统导入
- `js-hoist-intl` - 提取 Intl 对象创建

## 如何使用

阅读单个规则文件获取详细说明和代码示例：

```
rules/list-performance-virtualize.md
rules/animation-gpu-properties.md
```

每个规则文件包含：

- 规则重要性的简要说明
- 带说明的错误代码示例
- 带说明的正确代码示例
- 额外上下文和参考

## 完整编译文档

获取包含所有规则展开的完整指南：`AGENTS.md`
