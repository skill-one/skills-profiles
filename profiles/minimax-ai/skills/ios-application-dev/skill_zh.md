# iOS 应用开发指南

一本使用 UIKit、SnapKit 和 SwiftUI 构建 iOS 应用的实用指南。重点关注经过验证的模式和 Apple 平台规范。

## 快速参考

### UIKit

| 目的 | 组件 |
|------|------|
| 主要部分 | `UITabBarController` |
| 下钻 | `UINavigationController` |
| 专注任务 | Sheet 弹出 |
| 关键选择 | `UIAlertController` |
| 次要操作 | `UIContextMenuInteraction` |
| 列表内容 | `UICollectionView` + `DiffableDataSource` |
| 分区列表 | `DiffableDataSource` + `headerMode` |
| 网格布局 | `UICollectionViewCompositionalLayout` |
| 搜索 | `UISearchController` |
| 分享 | `UIActivityViewController` |
| 位置（一次性） | `CLLocationButton` |
| 反馈 | `UIImpactFeedbackGenerator` |
| 线性布局 | `UIStackView` |
| 自定义形状 | `CAShapeLayer` + `UIBezierPath` |
| 渐变 | `CAGradientLayer` |
| 现代按钮 | `UIButton.Configuration` |
| 动态文本 | `UIFontMetrics` + `preferredFont` |
| 深色模式 | 语义颜色（`.systemBackground`, `.label`） |
| 权限 | 上下文请求 + `AVCaptureDevice` |
| 生命周期 | `UIApplication` 通知 |

### SwiftUI

| 目的 | 组件 |
|------|------|
| 主要部分 | `TabView` + `tabItem` |
| 下钻 | `NavigationStack` + `NavigationPath` |
| 专注任务 | `.sheet` + `presentationDetents` |
| 关键选择 | `.alert` |
| 次要操作 | `.contextMenu` |
| 列表内容 | `List` + `.insetGrouped` |
| 搜索 | `.searchable` |
| 分享 | `ShareLink` |
| 位置（一次性） | `LocationButton` |
| 反馈 | `UIImpactFeedbackGenerator` |
| 进度（已知） | `ProgressView(value:total:)` |
| 进度（未知） | `ProgressView()` |
| 动态文本 | `.font(.body)` 语义样式 |
| 深色模式 | `.primary`, `.secondary`, `Color(.systemBackground)` |
| 场景生命周期 | `@Environment(\.scenePhase)` |
| 减少动画 | `@Environment(\.accessibilityReduceMotion)` |
| 动态类型 | `@Environment(\.dynamicTypeSize)` |

## 核心原则

### 布局
- 触摸目标 >= 44pt
- 内容在安全区域内（SwiftUI 默认尊重，仅用于背景使用 `.ignoresSafeArea()`）
- 使用 8pt 间距增量（8、16、24、32、40、48）
- 主要操作在拇指区域
- 支持所有屏幕尺寸（iPhone SE 375pt 到 Pro Max 430pt）

### 字体
- UIKit: `preferredFont(forTextStyle:)` + `adjustsFontForContentSizeCategory = true`
- SwiftUI: 语义文本样式 `.headline`, `.body`, `.caption`
- 自定义字体: `UIFontMetrics` / `Font.custom(_:size:relativeTo:)`
- 在无障碍尺寸下调整布局（最小 11pt）

### 颜色
- 使用语义系统颜色（`.systemBackground`, `.label`, `.primary`, `.secondary`）
- 资源库变体用于自定义颜色（Any/Dark Appearance）
- 不使用纯颜色信息（与图标或文本配对）
- 对普通文本的对比度比例 >= 4.5:1，大文本 3:1

### 无障碍
- 图标按钮上的标签（`.accessibilityLabel()`）
- 尊重减少动画（`@Environment(\.accessibilityReduceMotion)`）
- 逻辑阅读顺序（`.accessibilitySortPriority()`）
- 支持粗体文本、增加对比度偏好

### 导航
- 标签栏（3-5 个部分）在导航期间保持可见
- 返回滑动有效（永远不要覆盖系统手势）
- 状态在标签之间保留（`@SceneStorage`, `@State`）
- 永远不要使用汉堡菜单

### 隐私与权限
- 在上下文中请求权限（不是在启动时）
- 系统对话框前的自定义说明
- 支持使用 Apple 登录
- 尊重 ATT 拒绝

## 检查清单

### 布局
- [ ] 触摸目标 >= 44pt
- [ ] 内容在安全区域内
- [ ] 主要操作在拇指区域（下半部分）
- [ ] 所有屏幕尺寸的灵活宽度（SE 到 Pro Max）
- [ ] 间距与 8pt 网格对齐

### 字体
- [ ] 语义文本样式或使用 UIFontMetrics 缩放的自定义字体
- [ ] 支持动态类型直至无障碍尺寸
- [ ] 布局在大尺寸下重新流式处理（无截断）
- [ ] 最小文本大小 11pt

### 颜色
- [ ] 语义系统颜色或亮/暗资源库变体
- [ ] 深色模式是故意的（不只是反转）
- [ ] 无纯颜色信息
- [ ] 文本对比度 >= 4.5:1（普通）/ 3:1（大）
- [ ] 交互元素使用单一强调色

### 无障碍
- [ ] 所有交互元素上的 VoiceOver 标签
- [ ] 逻辑阅读顺序
- [ ] 尊重粗体文本偏好
- [ ] 减少动画禁用装饰性动画
- [ ] 所有手势都有替代访问路径

### 导航
- [ ] 标签栏用于 3-5 个顶级部分
- [ ] 无汉堡/抽屉菜单
- [ ] 标签栏在导航期间保持可见
- [ ] 返回滑动在整个应用中有效
- [ ] 状态在标签之间保留

### 组件
- [ ] 仅对关键决策使用警报
- [ ] Sheet 有关闭路径（按钮和/或滑动）
- [ ] 列表行高度 >= 44pt
- [ ] 破坏性按钮使用 `.destructive` 角色

### 隐私
- [ ] 权限在上下文中请求（不是在启动时）
- [ ] 系统权限对话框前的自定义说明
- [ ] 提供其他提供者的 Apple 登录
- [ ] 无需账户即可使用基本功能
- [ ] 如果跟踪，显示 ATT 提示，尊重拒绝

### 系统集成
- [ ] 应用优雅地处理中断（电话、后台、Siri）
- [ ] 应用内容被索引用于 Spotlight
- [ ] 可分享内容有分享表单

## 参考

| 主题 | 参考 |
|------|------|
| 触摸目标、安全区域、CollectionView | [布局系统](references/layout-system.md) |
| TabBar、NavigationController、Modal | [导航模式](references/navigation-patterns.md) |
| StackView、Button、Alert、Search、ContextMenu | [UIKit 组件](references/uikit-components.md) |
| CAShapeLayer、CAGradientLayer、Core Animation | [图形与动画](references/graphics-animation.md) |
| 动态类型、语义颜色、VoiceOver | [无障碍](references/accessibility.md) |
| 权限、位置、分享、生命周期、触觉反馈 | [系统集成](references/system-integration.md) |
| Metal Shaders & GPU | [Metal Shader 参考](references/metal-shader.md) |
| SwiftUI HIG、组件、模式、反模式 | [SwiftUI 设计指南](references/swiftui-design-guidelines.md) |
| Optionals、Protocols、async/await、ARC、错误处理 | [Swift 编码标准](references/swift-coding-standards.md) |

---

Swift、SwiftUI、UIKit、SF Symbols、Metal 和 Apple 是 Apple Inc. 的商标。SnapKit 是其各自所有者的商标。
