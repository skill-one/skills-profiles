# Expo React Native 性能最佳实践

Expo React Native 应用程序的全面性能优化指南。包含 8 个类别中的 42 条规则，按影响程度优先级排序，以指导自动化重构和代码生成。

## 应用时机

在以下情况参考这些指南：
- 编写新的 React Native 组件或屏幕
- 使用 FlatList 或 FlashList 实现列表
- 添加动画或过渡效果
- 优化图像和资源加载
- 审查存在性能问题的代码

## 按优先级划分的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 应用启动与包体积 | 关键 | `startup-` |
| 2 | 列表虚拟化 | 关键 | `list-` |
| 3 | 重新渲染优化 | 高 | `rerender-` |
| 4 | 动画性能 | 高 | `anim-` |
| 5 | 图像与资源加载 | 中高 | `asset-` |
| 6 | 内存管理 | 中 | `mem-` |
| 7 | 异步与数据获取 | 中 | `async-` |
| 8 | 平台优化 | 低中 | `platform-` |

## 快速参考

### 1. 应用启动与包体积 (关键)

- [`startup-enable-hermes`](references/startup-enable-hermes.md) - 启用 Hermes JavaScript 引擎
- [`startup-remove-console-logs`](references/startup-remove-console-logs.md) - 移除生产环境中的控制台日志
- [`startup-splash-screen-control`](references/startup-splash-screen-control.md) - 控制启动画面可见性
- [`startup-preload-assets`](references/startup-preload-assets.md) - 在启动画面期间预加载关键资源
- [`startup-async-routes`](references/startup-async-routes.md) - 使用异步路由进行代码拆分
- [`startup-cherry-pick-imports`](references/startup-cherry-pick-imports.md) - 使用直接导入而非包文件

### 2. 列表虚拟化 (关键)

- [`list-use-flashlist`](references/list-use-flashlist.md) - 使用 FlashList 而非 FlatList
- [`list-estimated-item-size`](references/list-estimated-item-size.md) - 提供准确的 estimatedItemSize
- [`list-get-item-type`](references/list-get-item-type.md) - 使用 getItemType 实现混合列表
- [`list-stable-render-item`](references/list-stable-render-item.md) - 使用 useCallback 稳定 renderItem
- [`list-get-item-layout`](references/list-get-item-layout.md) - 提供getItemLayout用于固定高度
- [`list-memoize-items`](references/list-memoize-items.md) - 保存列表项组件

### 3. 重新渲染优化 (高)

- [`rerender-use-memo-expensive`](references/rerender-use-memo-expensive.md) - 保存昂贵计算
- [`rerender-use-callback-handlers`](references/rerender-use-callback-handlers.md) - 使用 useCallback 稳定回调
- [`rerender-functional-setstate`](references/rerender-functional-setstate.md) - 使用函数式 setState 更新
- [`rerender-lazy-state-init`](references/rerender-lazy-state-init.md) - 使用懒加载状态初始化
- [`rerender-split-context`](references/rerender-split-context.md) - 按更新频率拆分上下文
- [`rerender-derive-state`](references/rerender-derive-state.md) - 推导状态而非同步

### 4. 动画性能 (高)

- [`anim-use-native-driver`](references/anim-use-native-driver.md) - 启用动画原生驱动
- [`anim-use-reanimated`](references/anim-use-reanimated.md) - 使用 Reanimated 实现复杂动画
- [`anim-layout-animation`](references/anim-layout-animation.md) - 使用 LayoutAnimation 实现简单过渡
- [`anim-transform-not-dimensions`](references/anim-transform-not-dimensions.md) - 动画 transform 而非尺寸
- [`anim-interaction-manager`](references/anim-interaction-manager.md) - 动画期间延迟重工作

### 5. 图像与资源加载 (中高)

- [`asset-use-expo-image`](references/asset-use-expo-image.md) - 使用 expo-image 加载图像
- [`asset-prefetch-images`](references/asset-prefetch-images.md) - 显示前预取图像
- [`asset-optimize-image-size`](references/asset-optimize-image-size.md) - 请求适当尺寸的图像
- [`asset-use-webp-format`](references/asset-use-webp-format.md) - 图像使用 WebP 格式
- [`asset-recycling-key`](references/asset-recycling-key.md) - FlashList 图像使用 recyclingKey

### 6. 内存管理 (中)

- [`mem-cleanup-subscriptions`](references/mem-cleanup-subscriptions.md) - useEffect 中清理订阅
- [`mem-clear-timers`](references/mem-clear-timers.md) - 卸载时清除计时器
- [`mem-abort-fetch`](references/mem-abort-fetch.md) - 卸载时中止获取请求
- [`mem-avoid-inline-objects`](references/mem-avoid-inline-objects.md) - 属性中避免内联对象
- [`mem-limit-list-data`](references/mem-limit-list-data.md) - 限制列表数据内存占用

### 7. 异步与数据获取 (中)

- [`async-parallel-fetching`](references/async-parallel-fetching.md) - 并行获取独立数据
- [`async-defer-await`](references/async-defer-await.md) - 需要时再 await
- [`async-batch-api-calls`](references/async-batch-api-calls.md) - 批量 API 调用
- [`async-cache-responses`](references/async-cache-responses.md) - 本地缓存 API 响应
- [`async-refetch-on-focus`](references/async-refetch-on-focus.md) - 屏幕聚焦时重新获取数据

### 8. 平台优化 (低中)

- [`platform-android-overdraw`](references/platform-android-overdraw.md) - 减少 Android 重绘
- [`platform-ios-text-rendering`](references/platform-ios-text-rendering.md) - 优化 iOS 文本渲染
- [`platform-android-proguard`](references/platform-android-proguard.md) - Android 发布版启用 ProGuard
- [`platform-conditional-render`](references/platform-conditional-render.md) - 平台特定优化

## 使用方法

阅读单个参考文件获取详细说明和代码示例：

- [部分定义](references/_sections.md) - 类别结构和影响等级
- [规则模板](assets/templates/_template.md) - 新增规则的模板

## 完整编译文档

完整指南（含所有规则）请参阅 [AGENTS.md](AGENTS.md)。

## 参考文件

| 文件 | 描述 |
|------|------|
| [AGENTS.md](AGENTS.md) | 包含所有规则的完整编译指南 |
| [references/_sections.md](references/_sections.md) | 类别定义和排序 |
| [assets/templates/_template.md](assets/templates/_template.md) | 新增规则的模板 |
| [metadata.json](metadata.json) | 版本和参考信息 |
