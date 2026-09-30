---
name: ios-design-guidelines
description: 苹果 iPhone 人类界面指南。在构建、审查或重构 SwiftUI/UIKit 接口以用于 iOS 时使用。在涉及 iPhone UI、iOS 组件、无障碍功能、动态类型、深色模式或 HIG 合规性的任务中触发。
---

# iPhone 设计指南

基于 Apple 人类界面指南的综合规则。在构建、审查或重构任何 iPhone 应用界面时，请应用这些规则。

---

## 1. 布局与安全区域
**影响：** 关键

### 规则 1.1：最小 44pt 触摸目标
所有交互元素必须具有至少 44x44 点的触摸目标。这包括按钮、链接、切换开关和自定义控件。

**正确：**
```swift
Button("保存") { save() }
    .frame(minWidth: 44, minHeight: 44)
```

**错误：**
```swift
// 20pt 图标，无填充——难以可靠地触摸
Button(action: save) {
    Image(systemName: "checkmark")
        .font(.system(size: 20))
}
// 缺少 .frame(minWidth: 44, minHeight: 44)
```

### 规则 1.2：尊重安全区域
切勿将交互或重要内容放置在状态栏、动态岛或主屏幕指示器下方。使用 SwiftUI 的自动安全区域处理或 UIKit 的 `safeAreaLayoutGuide`。

**正确：**
```swift
struct ContentView: View {
    var body: some View {
        VStack {
            Text("内容")
        }
        // SwiftUI 默认尊重安全区域
    }
}
```

**错误：**
```swift
struct ContentView: View {
    var body: some View {
        VStack {
            Text("内容")
        }
        .ignoresSafeArea() // 内容将被裁剪在缺口/动态岛下方
    }
}
```

仅用于背景填充、图像或装饰元素，切勿用于文本或交互控件。

### 规则 1.3：主要操作位于拇指区域
将主要操作放置在屏幕底部，这是用户拇指自然放置的位置。次要操作和导航应位于顶部。

**正确：**
```swift
VStack {
    ScrollView { /* 内容 */ }
    Button("继续") { next() }
        .buttonStyle(.borderedProminent)
        .padding()
}
```

**错误：**
```swift
VStack {
    Button("继续") { next() } // 屏幕顶部——单手难以触及
        .buttonStyle(.borderedProminent)
        .padding()
    ScrollView { /* 内容 */ }
}
```

### 规则 1.4：支持所有 iPhone 屏幕尺寸
为 iPhone SE（375pt 宽）至 iPhone Pro Max（430pt 宽）进行设计。使用灵活的布局，避免硬编码宽度。

**正确：**
```swift
HStack(spacing: 12) {
    ForEach(items) { item in
        CardView(item: item)
            .frame(maxWidth: .infinity) // 适应屏幕宽度
    }
}
```

**错误：**
```swift
HStack(spacing: 12) {
    ForEach(items) { item in
        CardView(item: item)
            .frame(width: 180) // 在 SE 上断开，在 Pro Max 上浪费空间
    }
}
```

### 规则 1.5：8pt 网格对齐
将间距、填充和元素大小对齐到 8 点的倍数（8、16、24、32、40、48）。使用 4pt 进行微调。

### 规则 1.6：支持横屏
除非应用是特定任务（例如相机），否则应支持横屏方向。使用 `ViewThatFits` 或 `GeometryReader` 进行自适应布局。

---

## 2. 导航
**影响：** 关键

### 规则 2.1：顶部级别的标签栏
在屏幕底部使用标签栏，用于 3 到 5 个顶部级别部分。每个标签应代表一个独特的内容或功能类别。

**正确：**
```swift
TabView {
    HomeView()
        .tabItem {
            Label("首页", systemImage: "house")
        }
    SearchView()
        .tabItem {
            Label("搜索", systemImage: "magnifyingglass")
        }
    ProfileView()
        .tabItem {
            Label("个人资料", systemImage: "person")
        }
}
```

**错误：**
```swift
// 三线隐藏汉堡菜单——可发现性几乎为零
NavigationView {
    Button(action: { showMenu.toggle() }) {
        Image(systemName: "line.horizontal.3")
    }
}
```

### 规则 2.2：切勿使用汉堡菜单
汉堡（抽屉）菜单隐藏导航，降低可发现性，并违反 iOS 习俗。使用标签栏代替。如果您有超过 5 个部分，请合并或使用“更多”标签。

### 规则 2.3：主要视图中的大标题
使用 `.navigationBarTitleDisplayMode(.large)` 对于顶级视图。当用户滚动时，标题会过渡到内联（`.inline`）。

**正确：**
```swift
NavigationStack {
    List(items) { item in
        ItemRow(item: item)
    }
    .navigationTitle("消息")
    .navigationBarTitleDisplayMode(.large)
}
```

### 规则 2.4：切勿覆盖返回滑动
从左侧边缘滑动的手势用于返回导航，这是系统级别的预期。切勿附加干扰它的自定义手势识别器。

**错误：**
```swift
.gesture(
    DragGesture()
        .onChanged { /* 自定义抽屉 */ } // 与系统返回滑动冲突
)
```

### 规则 2.5：使用 NavigationStack 进行层级内容
使用 `NavigationStack`（而不是已弃用的 `NavigationView`）用于 drill-down 内容。使用 `NavigationPath` 进行程序化导航。

**正确：**
```swift
NavigationStack(path: $path) {
    List(items) { item in
        NavigationLink(value: item) {
            ItemRow(item: item)
        }
    }
    .navigationDestination(for: Item.self) { item in
        ItemDetail(item: item)
    }
}
```

### 规则 2.6：跨导航保留状态
当用户返回并再次前进，或切换标签时，恢复先前的滚动位置和输入状态。使用 `@SceneStorage` 或 `@State` 来持久化视图状态。

### 规则 2.7：优先识别而非回忆
保持当前位置、最近的选择和可用目的地可见。恢复标签、滚动、过滤和选择状态，以便用户从识别继续，而不是从记忆中重建上下文。

---

## 3. 字体与动态类型
**影响：** 高

### 规则 3.1：使用内置文本样式
始终使用语义文本样式，而不是硬编码的尺寸。这些会随着动态类型自动缩放。

**正确：**
```swift
VStack(alignment: .leading, spacing: 4) {
    Text("部分标题")
        .font(.headline)
    Text("解释该部分的内容。")
        .font(.body)
    Text("最后更新 2 小时前")
        .font(.caption)
        .foregroundStyle(.secondary)
}
```

**错误：**
```swift
VStack(alignment: .leading, spacing: 4) {
    Text("部分标题")
        .font(.system(size: 17, weight: .semibold)) // 不会随着动态类型缩放
    Text("内容")
        .font(.system(size: 15)) // 不会随着动态类型缩放
}
```

### 规则 3.2：支持动态类型，包括无障碍尺寸
动态类型可以将文本缩放到大约 200% 的最大无障碍尺寸。布局必须重新流——切勿截断或裁剪重要文本。

**正确：**
```swift
HStack {
    Image(systemName: "star")
    Text("收藏")
        .font(.body)
}
// 在无障碍尺寸下，考虑使用 ViewThatFits 或
// AnyLayout 从 HStack 切换到 VStack
```

使用 `@Environment(\.dynamicTypeSize)` 来检测尺寸类别并调整布局：

```swift
@Environment(\.dynamicTypeSize) var dynamicTypeSize

var body: some View {
    if dynamicTypeSize.isAccessibilitySize {
        VStack { content }
    } else {
        HStack { content }
    }
}
```

### 规则 3.3：自定义字体必须与动态类型缩放
如果您使用自定义字体，请将其缩放以响应动态类型。API 因框架而异。

**正确（SwiftUI）：**
```swift
extension Font {
    static func scaledCustom(size: CGFloat, relativeTo textStyle: Font.TextStyle) -> Font {
        .custom("CustomFont-Regular", size: size, relativeTo: textStyle)
    }
}

// 使用
Text("你好")
    .font(.scaledCustom(size: 17, relativeTo: .body))
```

**正确（UIKit）：**
```swift
let metrics = UIFontMetrics(forTextStyle: .body)
let customFont = UIFont(name: "CustomFont-Regular", size: 17)!
label.font = metrics.scaledFont(for: customFont)
label.adjustsFontForContentSizeCategory = true
```

### 规则 3.4：系统字体为 SF Pro
除非品牌要求否则使用系统字体（SF Pro）。SF Pro 针对苹果显示屏进行了优化，以提高可读性。

### 规则 3.5：最小 11pt 文本
切勿显示小于 11pt 的文本。优先使用 17pt 作为正文文本。使用 `caption2` 样式（11pt）作为绝对最小值。

### 规则 3.6：通过字重和大小建立层级
通过字重和大小建立视觉层级。不要仅依赖颜色来区分文本级别。

---

## 4. 颜色与暗黑模式
**影响：** 高

### 规则 4.1：使用语义系统颜色
使用系统提供的语义颜色，这些颜色会自动适应亮色和暗色模式。

**正确：**
```swift
Text("主要文本")
    .foregroundStyle(.primary) // 适应亮色/暗色

Text("次要信息")
    .foregroundStyle(.secondary)

VStack { }
    .background(Color(.systemBackground)) // 亮色为白色，暗色为黑色
```

**错误：**
```swift
Text("主要文本")
    .foregroundColor(.black) // 在暗色背景下不可见

VStack { }
    .background(.white) // 暗色模式下刺眼
```

### 规则 4.2：为自定义颜色提供亮色和暗色变体
在资源库中定义自定义颜色，具有 Any Appearance 和 Dark Appearance 变体。

```swift
// 在 Assets.xcassets 中，定义“品牌蓝色”为：
// 任何外观：#0066CC
// 暗色外观：#4DA3FF

Text("品牌文本")
    .foregroundStyle(Color("BrandBlue")) // 自动切换
```

### 规则 4.3：切勿单独依赖颜色
始终将颜色与文本、图标或形状搭配使用以传达含义。大约 8% 的男性有某种形式的色觉缺陷。

**正确：**
```swift
HStack {
    Image(systemName: "exclamationmark.triangle.fill")
        .foregroundStyle(.red)
    Text("错误：无效的电子邮件地址")
        .foregroundStyle(.red)
}
```

**错误：**
```swift
// 仅颜色指示错误——色盲用户无法识别
TextField("电子邮件", text: $email)
    .border(isValid ? .green : .red)
```

### 规则 4.4：1:4.5 对比度比率最小值
所有文本必须满足 WCAG AA 对比度比率：正常文本为 1:4.5，大文本（18pt+ 或 14pt+ 粗体）为 1:3。

### 规则 4.5：支持显示 P3 广色域
使用显示 P3 色彩空间，在现代 iPhone 上呈现鲜艳、准确的颜色。在资源库中定义颜色时使用显示 P3 色域。

### 规则 4.6：背景层级
使用三级背景层级以创建深度：
- `systemBackground` — 主要表面
- `secondarySystemBackground` — 分组内容、卡片
- `tertiarySystemBackground` — 分组内容内的元素

### 规则 4.7：交互元素使用单一强调色
为所有交互元素（按钮、链接、切换开关）选择单一色调/强调色。这会创建一致的、可学习的视觉语言。

```swift
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .tint(.indigo) // 所有交互元素使用靛蓝色
        }
    }
}
```

---

## 5. 无障碍
**影响：** 关键

### 规则 5.1：所有交互元素上的 VoiceOver 标签
每个按钮、控件和交互元素都必须具有有意义的无障碍标签。

**正确：**
```swift
Button(action: addToCart) {
    Image(systemName: "cart.badge.plus")
}
.accessibilityLabel("添加到购物车")
```

**错误：**
```swift
Button(action: addToCart) {
    Image(systemName: "cart.badge.plus")
}
// VoiceOver 读取“cart.badge.plus”——对用户无意义
```

### 规则 5.2：逻辑 VoiceOver 导航顺序
确保 VoiceOver 按逻辑顺序读取元素。使用 `.accessibilitySortPriority()` 调整，当视觉布局与阅读顺序不匹配时。

```swift
VStack {
    Text("价格：$29.99")
        .accessibilitySortPriority(1) // 第二个读取（数字越小优先级越低）
    Text("产品名称")
        .accessibilitySortPriority(2) // 第一个读取（数字越大优先级越高）
}
```

### 规则 5.3：支持粗体文本
当用户在设置中启用粗体文本时，自定义渲染的文本必须适应。SwiftUI 文本样式会自动处理此问题。对于 SwiftUI 自定义渲染，使用 `@Environment(\.legibilityWeight)` 应用更重的权重。UIKit 代码必须检查 `UIAccessibility.isBoldTextEnabled` 并在 `UIAccessibility.boldTextStatusDidChangeNotification` 上重新查询。

**正确：**
```swift
// SwiftUI — 标准文本样式会自动适应
Text("部分标题")
    .font(.headline)

// SwiftUI — 自定义渲染尊重 legibilityWeight
@Environment(\.legibilityWeight) var legibilityWeight

var body: some View {
    Text("自定义标签")
        .fontWeight(legibilityWeight == .bold ? .bold : .regular)
}
```

**错误：**
```swift
// 硬编码权重忽略粗体文本偏好
label.font = UIFont.systemFont(ofSize: 17, weight: .regular)
// 缺少：当 UIAccessibility.boldTextStatusDidChangeNotification 触发时重新查询字体
```

### 规则 5.4：支持减少动画
当启用减少动画时，禁用装饰性动画和视差效果。使用 `@Environment(\.accessibilityReduceMotion)`。

**正确：**
```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion

var body: some View {
    CardView()
        .animation(reduceMotion ? nil : .spring(), value: isExpanded)
}
```

### 规则 5.5：支持增加对比度
当用户启用增加对比度时，确保自定义颜色具有更高对比度的变体。使用 `@Environment(\.colorSchemeContrast)` 检测。

### 规则 5.6：不要仅通过颜色、形状或位置传达信息
信息必须通过多个渠道提供。将视觉指示与文本或无障碍描述配对。

### 规则 5.7：所有手势的替代交互
每个自定义手势都必须为无法执行复杂手势的用户提供等效的基于点击或基于菜单的替代方案。

### 规则 5.8：支持开关控制和完整键盘访问
确保所有交互都与开关控制（外部开关）和完整键盘访问（蓝牙键盘）兼容。测试导航顺序和焦点行为。

---

## 6. 手势与输入
**影响：** 高

### 规则 6.1：使用标准手势
使用标准的 iOS 手势词汇：点击、长按、滑动、捏合、旋转。用户已经了解这些。

| 手势 | 标准用途 |
|------|---------|
| 点击 | 主要操作、选择 |
| 长按 | 上下文菜单、预览 |
| 水平滑动 | 删除、归档、导航后退 |
| 垂直滑动 | 滚动、关闭表单 |
| 捏合 | 放大/缩小 |
| 两指旋转 | 旋转内容 |

### 规则 6.2：切勿覆盖系统手势
这些手势由系统保留，不得拦截：
- 从左侧边缘滑动（返回导航）
- 从左上角向下滑动（通知中心）
- 从右上角向下滑动（控制中心）
- 从底部向上滑动（主屏幕/应用切换器）

### 规则 6.3：自定义手势必须可发现
如果您添加了自定义手势，请提供视觉提示（例如，抓取手柄），并确保该操作也通过可见的按钮或菜单项提供。

### 规则 6.4：支持所有输入方法
首先为触摸设计，但也支持：
- 硬件键盘（iPad 键盘附件、蓝牙键盘）
- 辅助设备（开关控制、头部跟踪）
- 指针输入（辅助触控）

---

## 7. 组件
**影响：** 高

### 规则 7.1：按钮样式
适当使用内置按钮样式：
- `.borderedProminent` — 主要操作
- `.bordered` — 次要操作
- `.borderless` — 次要或内联操作
- `.destructive` 角色 — 红色色调用于删除/移除

**正确：**
```swift
VStack(spacing: 16) {
    Button("购买") { buy() }
        .buttonStyle(.borderedProminent)

    Button("添加到愿望清单") { wishlist() }
        .buttonStyle(.bordered)

    Button("删除", role: .destructive) { delete() }
}
```

### 规则 7.2：警报——仅关键信息
仅在需要决策的关键信息时使用警报。优先使用 2 个按钮；最多 3 个。破坏性选项应使用 `.destructive` 角色。

**正确：**
```swift
.alert("删除照片?", isPresented: $showAlert) {
    Button("删除", role: .destructive) { deletePhoto() }
    Button("取消", role: .cancel) { }
} message: {
    Text("此照片将被永久删除。")
}
```

**错误：**
```swift
// 用于非关键信息的提示 — 应该使用横幅或轻提示
.alert("提示", isPresented: $showTip) {
    Button("确定") { }
} message: {
    Text("向左滑动删除项目。")
}
```

### 规则 7.3：用于范围任务的弹出面板
为自包含的任务显示弹出面板。始终提供一个关闭（关闭按钮或向下滑动）的方式。使用 `.presentationDetents()` 用于半高度弹出面板。

```swift
.sheet(isPresented: $showCompose) {
    NavigationStack {
        ComposeView()
            .navigationTitle("新消息")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("取消") { showCompose = false }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("发送") { send() }
                }
            }
    }
    .presentationDetents([.medium, .large])
}
```

### 规则 7.4：列表 — 插入分组默认样式
使用 `.insetGrouped` 列表样式作为默认样式。支持滑动操作以执行常见操作。最小行高为 44pt。

**正确：**
```swift
List {
    Section("最近") {
        ForEach(recentItems) { item in
            ItemRow(item: item)
                .swipeActions(edge: .trailing) {
                    Button(role: .destructive) { delete(item) } label: {
                        Label("删除", systemImage: "trash")
                    }
                    Button { archive(item) } label: {
                        Label("存档", systemImage: "archivebox")
                    }
                    .tint(.blue)
                }
        }
    }
}
.listStyle(.insetGrouped)
```

### 规则 7.5：标签栏行为
- 使用 SF Symbols 作为标签图标 — 选中标签使用填充样式，未选中使用轮廓样式
- 在标签内导航更深层次时，永远不要隐藏标签栏
- 使用 `.badge()` 重要计数

```swift
TabView {
    MessagesView()
        .tabItem {
            Label("消息", systemImage: "message")
        }
        .badge(unreadCount)
}
```

### 规则 7.6：搜索
使用 `.searchable()` 放置搜索。提供搜索建议并支持最近搜索。

```swift
NavigationStack {
    List(filteredItems) { item in
        ItemRow(item: item)
    }
    .searchable(text: $searchText, prompt: "搜索项目")
    .searchSuggestions {
        ForEach(suggestions) { suggestion in
            Text(suggestion.title)
                .searchCompletion(suggestion.title)
        }
    }
}
```

### 规则 7.7：上下文菜单
使用上下文菜单（长按）执行次要操作。永远不要将上下文菜单作为唯一访问操作的方式。

```swift
PhotoView(photo: photo)
    .contextMenu {
        Button { share(photo) } label: {
            Label("分享", systemImage: "square.and.arrow.up")
        }
        Button { favorite(photo) } label: {
            Label("收藏", systemImage: "heart")
        }
        Button(role: .destructive) { delete(photo) } label: {
            Label("删除", systemImage: "trash")
        }
    }
```

### 规则 7.8：进度指示器
- 确定型 (`ProgressView(value:total:)`) 用于具有已知持续时间的操作
- 不确定型 (`ProgressView()`) 用于未知持续时间的操作
- 永远不要使用旋转器阻塞整个屏幕

### 规则 7.9：SF Symbols — 渲染模式
为每个符号使用适当的渲染模式。单色是默认值；层次结构、调色板和多色在适当的情况下提供更丰富的表达。始终优先选择最佳传达意义的符号渲染模式 — 不要在多色传达关键状态时默认为单色。

**正确：**
```swift
// 层次结构：单一颜色，自动不透明层
Image(systemName: "person.crop.circle.fill")
    .symbolRenderingMode(.hierarchical)
    .foregroundStyle(.blue)

// 多色：每层系统定义颜色（例如，电池、天气）
Image(systemName: "battery.100percent.bolt")
    .symbolRenderingMode(.multicolor)

// 调色板：显式每层颜色
Image(systemName: "folder.badge.plus")
    .symbolRenderingMode(.palette)
    .foregroundStyle(.white, .blue)
```

**错误：**
```swift
// 单色在具有有意义多色层的符号上
Image(systemName: "battery.100percent.bolt")
    .foregroundColor(.gray) // 丢失上下文颜色意义
```

### 规则 7.10：SF Symbols — 重量和比例
将符号重量与相邻文本重量相匹配。使用比例变体（`.small`, `.medium`, `.large`）而不是调整大小。符号重量不应比相邻文本更重。

**正确：**
```swift
Label("下载", systemImage: "arrow.down.circle.fill")
    .font(.body.weight(.semibold))
    // 符号自动继承 .semibold 重量
```

**错误：**
```swift
HStack {
    Image(systemName: "arrow.down.circle.fill")
        .font(.system(size: 32)) // 显式大小忽略类型比例
    Text("下载")
        .font(.body)
}
```

### 规则 7.11：SF Symbols — 动画（iOS 17+）
使用 `symbolEffect` 用于符号状态转换。优先选择离散效果（`.bounce`, `.pulse`）用于操作，无限效果（`.variableColor`）用于持续状态。当 `contentTransition(.symbolEffect)` 可用时，不要在符号名称之间使用手动淡入淡出。

**正确：**
```swift
Image(systemName: isLoading ? "arrow.2.circlepath" : "checkmark.circle")
    .contentTransition(.symbolEffect(.replace))
    .symbolEffect(.pulse, isActive: isLoading)
```

**错误：**
```swift
// 手动不透明度淡入淡出在符号名称之间
if isLoading {
    Image(systemName: "arrow.2.circlepath")
} else {
    Image(systemName: "checkmark.circle")
}
```

---

## 8. 模式
**影响：中等**

### 规则 8.1：引导 — 最多 3 页，可跳过
将引导限制为 3 页或更少。始终提供一个跳过选项。将登录推迟到用户需要经过身份验证的功能时。

```swift
TabView {
    OnboardingPage(
        image: "wand.and.stars",
        title: "智能建议",
        subtitle: "根据您的偏好获取个性化推荐。"
    )
    OnboardingPage(
        image: "bell.badge",
        title: "保持更新",
        subtitle: "接收对您重要的事情的通知。"
    )
    OnboardingPage(
        image: "checkmark.shield",
        title: "私密和安全",
        subtitle: "您的数据保留在您的设备上。"
    )
}
.tabViewStyle(.page)
.overlay(alignment: .topTrailing) {
    Button("跳过") { completeOnboarding() }
        .padding()
}
```

### 规则 8.2：加载 — 骨架视图，无阻塞旋转器
使用与正在加载的内容布局匹配的骨架/占位符视图。永远不要显示全屏阻塞旋转器。

**正确：**
```swift
if isLoading {
    ForEach(0..<5) { _ in
        SkeletonRow() // 占位符匹配最终行布局
            .redacted(reason: .placeholder)
    }
} else {
    ForEach(items) { item in
        ItemRow(item: item)
    }
}
```

**错误：**
```swift
if isLoading {
    ProgressView("加载中...") // 阻塞整个视图
} else {
    List(items) { item in ItemRow(item: item) }
}
```

### 规则 8.3：启动屏幕 — 匹配第一屏幕
启动故事板必须视觉上匹配应用的第一屏幕。没有启动标志，没有品牌屏幕。这创造了即时启动的感知。

### 规则 8.4：模态 — 适度使用
仅在用户必须完成或放弃专注任务时显示模态视图。始终提供一个明确的关闭操作。永远不要将模态视图堆叠在模态视图之上。

### 规则 8.5：通知 — 高价值
仅对用户真正关心的内容发送通知。支持可操作的通知。对通知进行分类，以便用户可以细粒度地控制它们。

### 规则 8.6：设置位置
- **常用设置：** 从个人资料或齿轮图标可访问的应用内设置屏幕
- **隐私/权限设置：** 通过 URL 方案推迟到系统设置应用
- 永远不要在应用内重复系统级控件

### 规则 8.7：反馈 — 视觉 + 触觉
为每个用户操作提供即时反馈：
- 视觉状态变化（按钮高亮、动画）
- 使用 `UIImpactFeedbackGenerator`、`UINotificationFeedbackGenerator` 或 `UISelectionFeedbackGenerator` 对重要操作提供触觉反馈

```swift
Button("完成") {
    let generator = UINotificationFeedbackGenerator()
    generator.notificationOccurred(.success)
    completeTask()
}
```

### 规则 8.8：立即显示等待状态
如果操作无法立即完成，立即确认点击，然后显示行内进度、骨架或部分结果。永远不要在操作继续时让界面视觉上保持不变。

---

## 9. 隐私和权限
**影响：高**

### 规则 9.1：在上下文中请求权限
在用户执行需要权限的操作时请求权限 — 永远不要在应用启动时请求。

**正确：**
```swift
Button("拍照") {
    // 仅在用户点击此按钮时请求相机权限
    AVCaptureDevice.requestAccess(for: .video) { granted in
        if granted { showCamera = true }
    }
}
```

**错误：**
```swift
// 在 AppDelegate.didFinishLaunching — 太早，没有上下文
func application(_ application: UIApplication, didFinishLaunchingWithOptions ...) {
    AVCaptureDevice.requestAccess(for: .video) { _ in }
    CLLocationManager().requestWhenInUseAuthorization()
    UNUserNotificationCenter.current().requestAuthorization(options: [.alert]) { _, _ in }
}
```

### 规则 9.2：系统提示之前解释
在触发系统权限对话框之前显示自定义解释屏幕。系统对话框只出现一次 — 如果用户拒绝，应用必须将他们引导至设置。

```swift
struct LocationExplanation: View {
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "location.fill")
                .font(.largeTitle)
            Text("查找附近商店")
                .font(.headline)
            Text("我们使用您的位置来显示步行范围内的商店。您的位置永远不会被共享或存储。")
                .font(.body)
                .multilineTextAlignment(.center)
            Button("启用位置") {
                locationManager.requestWhenInUseAuthorization()
            }
            .buttonStyle(.borderedProminent)
            Button("稍后") { dismiss() }
                .foregroundStyle(.secondary)
        }
        .padding()
    }
}
```

### 规则 9.3：支持使用 Apple 登录
如果应用提供任何第三方登录（Google、Facebook），它也必须提供使用 Apple 登录。将其作为第一个选项显示。

### 规则 9.4：除非必要，不要要求账户
让用户在要求登录之前探索应用。仅限制真正需要身份验证的功能（购买、同步、社交功能）。

### 规则 9.5：应用跟踪透明度
如果您跨应用或网站跟踪用户，请显示 ATT 提示。尊重拒绝 — 不要因选择退出而降低用户体验。

### 规则 9.6：一次性访问的位置按钮
使用 `LocationButton` 用于需要一次性位置而不请求持续权限的操作。

```swift
import CoreLocationUI

LocationButton(.currentLocation) {
    fetchNearbyStores()
}
.labelStyle(.titleAndIcon)
```

---

## 10. 系统集成
**影响：中等**

### 规则 10.1：使用 WidgetKit 提供快速查看数据的小部件
使用 WidgetKit 提供用户频繁检查的信息。显示最有用的快照。自 iOS 17 起，小部件支持交互式控件：使用 `Button` 和 `Toggle` 背后由 App Intents 支持，用于用户可以直接从小部件执行而无需打开应用的操作。

```swift
// iOS 17+ 交互式小部件，带有 Button
struct TimerWidgetView: View {
    let entry: TimerEntry

    var body: some View {
        VStack {
            Text(entry.remaining, style: .timer)
                .font(.title2.bold())
            Button(intent: ToggleTimerIntent()) {
                Label(entry.isRunning ? "暂停" : "开始",
                      systemImage: entry.isRunning ? "pause.fill" : "play.fill")
            }
            .buttonStyle(.borderedProminent)
        }
    }
}
```

### 规则 10.2：使用 App Shortcuts 触发关键操作
定义 App Shortcuts，以便用户可以从 Siri、Spotlight 和快捷方式应用触发关键操作。

```swift
struct MyAppShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: StartWorkoutIntent(),
            phrases: ["在 \(.applicationName) 中开始锻炼"],
            shortTitle: "开始锻炼",
            systemImageName: "figure.run"
        )
    }
}
```

### 规则 10.3：Spotlight 索引
使用 `CSSearchableItem` 索引应用内容，以便用户可以通过 Spotlight 搜索找到它。

### 规则 10.4：分享面板集成
支持系统分享面板，以便用户可能想要将内容发送到其他地方。实现 `UIActivityItemSource` 或在 SwiftUI 中使用 `ShareLink`。

```swift
ShareLink(item: article.url) {
    Label("分享", systemImage: "square.and.arrow.up")
}
```

### 规则 10.5：实时活动
使用实时活动和动态岛处理实时、有时间限制的事件（送货跟踪、体育比分、锻炼）。

### 规则 10.6：优雅地处理中断
在中断时保存状态并优雅地暂停：
- 电话呼叫
- Siri 调用
- 通知
- 应用切换器
- FaceTime SharePlay

使用 `scenePhase` 检测转换：

```swift
@Environment(\.scenePhase) var scenePhase

.onChange(of: scenePhase) { _, newPhase in
    switch newPhase {
    case .active: resumeActivity()
    case .inactive: pauseActivity()
    case .background: saveState()
    @unknown default: break
    }
}
```

---

## 快速参考

| 需要 | 组件 | 备注 |
|------|-----------|-------|
| 顶级部分（3-5） | `TabView` with `.tabItem` | 底部标签栏，SF Symbols |
| 层次结构钻取 | `NavigationStack` | 根目录大标题，子级内联 |
| 自包含任务 | `.sheet` | 滑动关闭，取消/完成按钮 |
| 关键决策 | `.alert` | 2 个按钮优先，最多 3 个 |
| 次要操作 | `.contextMenu` | 长按；也必须在其他地方可访问 |
| 滚动内容 | `List` with `.insetGrouped` | 44pt 最小行，滑动操作 |
| 文本输入 | `TextField` / `TextEditor` | 标签在上方，验证在下方 |
| 选择（少量选项） | `Picker` | 分段式用于 2-5，轮子用于许多 |
| 选择（开/关） | `Toggle` | 列表行右对齐 |
| 搜索 | `.searchable` | 建议搜索，最近搜索 |
| 进度（已知） | `ProgressView(value:total:)` | 显示百分比或剩余时间 |
| 进度（未知） | `ProgressView()` | 行内，永远不要全屏阻塞 |
| 一次性位置 | `LocationButton` | 无需持久权限 |
| 分享内容 | `ShareLink` | 系统分享面板 |
| 触觉反馈 | `UIImpactFeedbackGenerator` | `.light`，`.medium`，`.heavy` |
| 销毁性操作 | `Button(role: .destructive)` | 红色色调，通过警报确认 |

---

## 评估检查清单

使用此检查清单审计 iPhone 应用以符合 HIG 合规性：

### 布局和安全区域
- [ ] 所有触摸目标至少为 44x44pt
- [ ] 没有内容被剪切在状态栏、动态岛或主指示器下方
- [ ] 主要操作位于屏幕下半部分（拇指区域）
- [ ] 布局从 iPhone SE 到 Pro Max 无需中断
- [ ] 间距对齐到 8pt 网格

### 导航
- [ ] 标签栏用于 3-5 顶级部分
- [ ] 不使用汉堡/抽屉菜单
- [ ] 主要视图使用大标题
- [ ] 从左边缘滑动返回导航在整个应用中有效
- [ ] 切换标签时状态保持

### 字体
- [ ] 所有文本使用内置文本样式或使用 Dynamic Type 缩放的自定义字体（SwiftUI 中的 `Font.custom(_:size:relativeTo:)` 或 UIKit 中的 `UIFontMetrics`）
- [ ] Dynamic Type 支持到可访问性大小
- [ ] 布局在大型文本尺寸下重新流（不截断重要文本）
- [ ] 最小文本大小为 11pt

### 颜色与深色模式
- [ ] 应用使用语义系统颜色或提供亮/暗资源变体
- [ ] 深色模式看起来是经过精心设计的（不只是反转）
- [ ] 仅通过颜色传递信息
- [ ] 文本对比度符合 4.5:1（正常）或 3:1（大）
- [ ] 交互元素使用单一强调色

### 可访问性
- [ ] VoiceOver 逻辑地读取所有屏幕，并使用有意义的标签
- [ ] 粗体文本偏好得到尊重
- [ ] Reduce Motion 禁用装饰性动画
- [ ] 增加对比度变体适用于自定义颜色
- [ ] 所有手势都有替代访问路径

### 组件
- [ ] 仅在需要做出关键决策时使用警告
- [ ] 底部弹出层有关闭路径（按钮和/或滑动）
- [ ] 列表行高度至少为 44pt
- [ ] 导航时标签栏始终可见
- [ ] 销毁性按钮使用 `.destructive` 角色

### 隐私
- [ ] 权限请求应在上下文中进行，而不是在启动时
- [ ] 每个系统权限对话框前都显示自定义说明
- [ ] 使用 Apple 登录与其他提供者并列
- [ ] 应用可在没有账户的情况下使用基本功能
- [ ] 如果跟踪，则显示 ATT 提示，并尊重拒绝

### 系统集成
- [ ] 小工具显示可快速浏览的实时信息
- [ ] 应用内容被 Spotlight 索引
- [ ] 分享菜单适用于可分享的内容
- [ ] 应用优雅地处理中断（电话、后台、Siri）

---

## 反模式

这些是违反 iOS 人类界面指南的常见错误。切勿这样做：

1. **汉堡菜单** — 使用标签栏。汉堡菜单隐藏导航，并减少功能发现性高达 50%。

2. **破坏滑动返回的自定义返回按钮** — 如果替换返回按钮，请确保通过 `NavigationStack` 仍然可以通过左边缘滑动进行操作。

3. **全屏阻塞式加载动画** — 使用骨架视图或内联进度指示器。阻塞式加载动画使应用感觉卡顿。

4. **带有标志的启动画面** — 启动屏幕必须与应用的第一个屏幕一致。品牌标识延迟感觉不自然。

5. **在启动时请求所有权限** — 在首次启动时请求相机、位置、通知和联系人，几乎肯定会遭到拒绝。

6. **硬编码的字体大小** — 使用文本样式。硬编码的大小忽略动态类型和可访问性偏好，使数百万用户的应用中断。

7. **仅使用颜色指示状态** — 红色/绿色表示有效/无效排除了色盲用户。始终与图标或文本配合使用。

8. **用于非关键信息的警告** — 警告中断流程并需要关闭。使用横幅、吐司或内联消息来提供提示和非关键信息。

9. **在推送时隐藏标签栏** — 标签栏应在标签内导航期间始终可见。隐藏它们会使用户感到困惑。

10. **忽略安全区域** — 在内容视图上使用 `.ignoresSafeArea()` 会导致文本和按钮消失在缺口、动态岛或主屏幕指示器下方。

11. **不可关闭的模态框** — 每个模态框都必须有一个明确的关闭路径（关闭按钮、取消、向下滑动）。将用户困在模态框中是敌对的。

12. **没有替代方案的自定义手势** — 三指滑动撤销对许多人来说无法使用。请提供可见的按钮或菜单项。

13. **微小的触摸目标** — 小于 44pt 的按钮和链接会导致误触，尤其是在列表和工具栏中。

14. **堆叠的模态框** — 在一个底部弹出层上再显示一个底部弹出层，再显示一个底部弹出层会创建导航混乱。改为在单个模态框内使用导航。

15. **深色模式作为事后考虑** — 使用硬编码颜色意味着应用要么在深色模式下损坏，要么在亮色模式下损坏。始终使用语义颜色。
