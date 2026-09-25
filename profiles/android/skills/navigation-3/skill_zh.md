*** ** * ** ***

## 迁移指南

- *[从导航 2 迁移到导航 3 的指南](references/android/guide/navigation/navigation-3/migration-guide.md)*: 从 Android 应用程序中从导航 2 迁移到导航 3 的分步指南，涵盖依赖项更新、路由更改、状态管理和 UI 组件替换。

### 要求

- *[指南：迁移到 Compose 中的类型安全导航](references/android/guide/navigation/type-safe-destinations.md)* : 从基于字符串的导航迁移到 Jetpack Compose 中的 **类型安全导航** 的分步指南，使用 Jetpack Navigation 2。

## 开发者文档

- *[导航 3](references/android/guide/navigation/navigation-3/index.md)*。 搜索文档以获取有关基础知识、保存和管理导航状态、模块化导航代码、使用 Scenes 创建自定义布局、在目的地之间动画或对目的地应用逻辑或包装器的更多信息。

## 方案

展示常见模式的代码示例。

### 基本API使用

- *[基本](references/android/guide/navigation/navigation-3/recipes/basic.md)*: 展示最基本的 API 使用。
- *[可保存的后退栈](references/android/guide/navigation/navigation-3/recipes/basicsaveable.md)*: 展示具有持久性后退栈的基本 API 使用。
- *[入口提供器DSL](references/android/guide/navigation/navigation-3/recipes/basicdsl.md)*: 使用 entryProvider DSL 展示基本 API 使用。

### 常见UI

- *[常见UI](references/android/guide/navigation/navigation-3/recipes/common-ui.md)*: 演示如何使用底部导航栏和多个后退栈实现常见的导航 UI 模式，其中导航栏中的每个标签都有自己的导航历史记录。

### 深链接

- *[静态URI](references/android/guide/navigation/navigation-3/recipes/deeplinks-staticuri.md)*: 展示如何处理简单的静态 URI 深链接。
- *[带参数的URI](https://developer.android.com/guide/navigation/navigation-3/recipes/deeplinks-uriarguments)*: 展示如何从深链接解析路径和查询参数。
- *[合成后退栈](references/android/guide/navigation/navigation-3/recipes/deeplinks-syntheticbackstack.md)*: 展示如何处理具有合成后退栈的深链接。
- *[自定义匹配器](references/android/guide/navigation/navigation-3/recipes/deeplinks-custommatcher.md)*: 展示如何实现自定义深链接匹配逻辑。

### Scenes

#### 使用内置的 Scenes

- *[对话框](references/android/guide/navigation/navigation-3/recipes/dialog.md)*: 展示如何创建对话框。

#### 创建自定义 Scenes

- *[底部面板](references/android/guide/navigation/navigation-3/recipes/bottomsheet.md)*: 展示如何创建底部面板目的地。
- *[列表-详情 Scenes](references/android/guide/navigation/navigation-3/recipes/scenes-listdetail.md)*: 演示如何使用导航 3 Scenes API 实现自适应列表-详情布局。
- *[双面板 Scenes](references/android/guide/navigation/navigation-3/recipes/scenes-twopane.md)*: 演示如何使用导航 3 Scenes API 实现自适应双面板布局。

### Material Adaptive

- *[Material 列表-详情](references/android/guide/navigation/navigation-3/recipes/material-listdetail.md)*: 演示如何使用 Material 3 Adaptive 实现自适应列表-详情布局。
- *[Material 支持面板](references/android/guide/navigation/navigation-3/recipes/material-supportingpane.md)*: 演示如何使用 Material 3 Adaptive 实现自适应支持面板布局。

### 动画

- *[动画](references/android/guide/navigation/navigation-3/recipes/animations.md)*: 展示如何覆盖所有目的地和单个目的地的默认动画。
- *[条件过渡](references/android/guide/navigation/navigation-3/recipes/conditional-transitions.md)*: 展示如何实现条件过渡动画。

### 常见后退栈行为

- *[多个后退栈](references/android/guide/navigation/navigation-3/recipes/multiple-backstacks.md)*: 展示如何创建多个顶级路由，每个路由都有自己的后退栈。顶级路由在导航栏中显示，允许用户在它们之间切换。每个顶级路由保留状态，导航状态持久化配置更改和进程死亡。

### 条件导航

- *[条件导航](references/android/guide/navigation/navigation-3/recipes/conditional.md)*: 当满足条件时切换到不同的导航流程。例如，用于身份验证或首次用户引导。

### 生命周期

- *[生命周期所有者](references/android/guide/navigation/navigation-3/recipes/lifecycle-owner.md)*: 展示如何在导航 3 中使用和观察生命周期。

### 架构

- *[模块化导航代码 (Hilt)](references/android/guide/navigation/navigation-3/recipes/modular-hilt.md)*: 演示如何使用 Hilt 或 Dagger for DI 将导航代码解耦到单独的模块中。
- *[模块化导航代码 (Koin)](references/android/guide/navigation/navigation-3/recipes/modular-koin.md)*: 演示如何使用 Koin for DI 将导航代码解耦到单独的模块中。

### 与ViewModel一起使用

#### 传递导航参数

- *[基本ViewModel](references/android/guide/navigation/navigation-3/recipes/passingarguments.md)* : 导航参数传递给使用 `viewModel()` 构建的 `ViewModel`

### 返回结果

- *[将结果作为事件返回](references/android/guide/navigation/navigation-3/recipes/results-event.md)* : 将结果作为事件返回到另一个 `NavEntry` 中的内容
- *[将结果作为状态返回](references/android/guide/navigation/navigation-3/recipes/results-state.md)* : 将结果作为存储在 `CompositionLocal` 中的状态返回
