# iPhone 应用设计指南

基于 Apple 人类界面指南的全面规则。在构建、审查或重构任何 iPhone 应用界面时，请应用这些规则。

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
// 20pt 图标，无填充 — 难以可靠地触摸
Button(action: save) {
    Image(systemName: "checkmark")
        .font(.system(size: 20))
}
// 缺少 .frame(minWidth: 44, minHeight: 44)
```

### 规则 1.2：尊重安全区域
切勿将交互或重要内容放置在状态栏、动态岛或主指示器下方。使用 SwiftUI 的自动安全区域处理或 UIKit 的 `safeAreaLayoutGuide`。

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
        .ignoresSafeArea() // 内容将在缺口/动态岛下方被裁剪
    }
}
```

仅在背景填充、图像或装饰元素中使用 `.ignoresSafeArea()`，切勿用于文本或交互控件。

### 规则 1.3：主要操作在拇指区域
将主要操作放置在屏幕底部，这是用户拇指自然停留的位置。次要操作和导航应位于顶部。

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
    Button("继续") { next() } // 屏幕顶部 — 单手难以触及
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
            .frame(width: 180) // 在 SE 上会中断，在 Pro Max 上浪费空间
    }
}
```

### 规则 1.5：8pt 网格对齐
将间距、填充和元素大小对齐到 8 点的倍数（8、16、24、32、40、48）。使用 4pt 进行精细调整。

### 规则 1.6：支持横屏
除非应用是特定任务（例如相机），否则应支持横屏方向。使用 `ViewThatFits` 或 `GeometryReader` 进行自适应布局。

---

## 2. 导航
**影响：** 关键

### 规则 2.1：用于顶级部分的标签栏
在屏幕底部使用标签栏用于 3 到 5 个顶级部分。每个标签应代表一个独特的内容或功能类别。

**正确：**
```swift
TabView {
    HomeView()
        .tabItem {
            Label("主页", systemImage: "house")
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
// 灰色菜单隐藏在三条线后面 — 可发现性几乎为零
NavigationView {
    Button(action: { showMenu.toggle() }) {
        Image(systemName: "line.horizontal.3")
    }
}
```

### 规则 2.2：切勿使用汉堡菜单
汉堡（抽屉）菜单隐藏导航，降低可发现性，并违反 iOS 习俗。使用标签栏代替。如果您有超过 5 个部分，请合并或使用“更多”标签。

### 规则 2.3：主要视图使用大标题
对于顶级视图使用 `.navigationBarTitleDisplayMode(.large)`。当用户滚动时，标题将过渡到内联（`.inline`）。

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
从左侧边缘滑动的手势用于返回导航是系统级别的预期。切勿附加干扰它的自定义手势识别器。

**错误：**
```swift
.gesture(
    DragGesture()
        .onChanged { /* 自定义抽屉 */ } // 与系统返回滑动冲突
)
```

### 规则 2.5：使用 NavigationStack 进行分层内容
使用 `NavigationStack`（而不是已弃用的 `NavigationView`）进行钻取内容。使用 `NavigationPath` 进行程序化导航。

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
当用户返回并然后前进，或切换标签时，恢复先前的滚动位置和输入状态。使用 `@SceneStorage` 或 `@State` 来持久化视图状态。

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
    Text("正文内容，解释该部分。")
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
    Text("正文内容")
        .font(.system(size: 15)) // 不会随着动态类型缩放
}
```

### 规则 3.2：支持动态类型，包括无障碍尺寸
动态类型可以将文本缩放到大约 200% 的最大无障碍尺寸。布局必须重新流式化——切勿截断或裁剪重要文本。

**正确：**
```swift
HStack {
    Image(systemName: "star")
    Text("收藏")
        .font(.body)
}
// 在无障碍尺寸下，考虑使用 ViewThatFits 或
// AnyLayout 切换从 HStack 到 VStack
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

// 使用方式
Text("Hello")
    .font(.scaledCustom(size: 17, relativeTo: .body))
```

**正确（UIKit）：**
```swift
let metrics = UIFontMetrics(forTextStyle: .body)
let customFont = UIFont(name: "CustomFont-Regular", size: 17)!
label.font = metrics.scaledFont(for: customFont)
label.adjustsFontForContentSizeCategory = true
```

### 规则 3.4：SF Pro 作为系统字体
除非品牌要求否则使用系统字体（SF Pro）。SF Pro 针对苹果显示屏进行了优化，可读性最佳。

### 规则 3.5：最小 11pt 文本
切勿显示小于 11pt 的文本。优先使用 17pt 作为正文文本。使用 `caption2` 样式（11pt）作为绝对最小值。

### 规则 3.6：通过权重和大小建立层次结构
通过字体权重和大小建立视觉层次结构。不要仅依赖颜色来区分文本级别。

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
    .background(Color(.systemBackground)) // 亮色模式下为白色，暗色模式下为黑色
```

**错误：**
```swift
Text("主要文本")
    .foregroundColor(.black) // 在暗色背景下不可见

VStack { }
    .background(.white) // 暗色模式下刺眼
```

### 规则 4.2：为自定义颜色提供亮色和暗色变体
在资源库中定义自定义颜色时，使用 Any Appearance 和 Dark Appearance 变体。

```swift
// 在 Assets.xcassets 中定义 "BrandBlue" 时：
// Any Appearance: #0066CC
// Dark Appearance: #4DA3FF

Text("品牌文本")
    .foregroundStyle(Color("BrandBlue")) // 自动切换
```

### 规则 4.3：切勿仅依赖颜色
始终将颜色与文本、图标或形状配对以传达含义。大约 8% 的男性有某种形式的色觉缺陷。

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
// 仅颜色指示错误 — 色盲用户无法识别
TextField("Email", text: $email)
    .border(isValid ? .green : .red)
```

### 规则 4.4：4.5:1 对比度比例最小值
所有文本必须满足 WCAG AA 对比度比例：正常文本为 4.5:1，大文本（18pt+ 或 14pt+ 粗体）为 3:1。

### 规则 4.5：支持显示 P3 广色域
使用 Display P3 色彩空间以获得鲜艳、准确的颜色。在资源库中定义颜色时使用 Display P3 广色域。

### 规则 4.6：背景层次结构
使用三个级别的背景层次结构以创建深度：
- `systemBackground` — 主要表面
- `secondarySystemBackground` — 分组内容、卡片
- `tertiarySystemBackground` — 分组内容中的元素

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

### 规则 5.1：所有交互元素都有 VoiceOver 标签
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
// VoiceOver 读取 "cart.badge.plus" — 对用户无意义
```

### 规则 5.2：逻辑 VoiceOver 导航顺序
确保 VoiceOver 按逻辑顺序读取元素。使用 `.accessibilitySortPriority()` 调整当视觉布局与阅读顺序不匹配时。

```swift
VStack {
    Text("价格: $29.99")
        .accessibilitySortPriority(1) // 第二个读取（数字越小优先级越低）
    Text("产品名称")
        .accessibilitySortPriority(2) // 第一个读取（数字越大优先级越高）
}
```

### 规则 5.3：支持粗体文本
当用户在设置中启用粗体文本时，自定义渲染的文本必须适应。SwiftUI 文本样式会自动处理此问题。对于 SwiftUI 自定义渲染，使用 `@Environment(\.legibilityWeight)` 来应用更重的权重。UIKit 代码必须检查 `UIAccessibility.isBoldTextEnabled` 并在 `UIAccessibility.boldTextStatusDidChangeNotification` 上重新查询。

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
// 硬编码的权重忽略了粗体文本偏好
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
当用户启用增加对比度时，确保自定义颜色具有更高对比度的变体。使用 `@Environment(\.colorSchemeContrast)` 来检测。

### 规则 5.6：不要仅通过颜色、形状或位置传达信息
信息必须通过多个渠道提供。将视觉指示符与文本或无障碍描述配对。

### 规则 5.7：所有手势都有替代交互
每个自定义手势都必须具有基于触摸或基于菜单的等效替代方案，以便无法执行复杂手势的用户使用。

### 规则 5.8：支持开关控制和完整键盘访问
确保所有交互都与开关控制（外部开关）和完整键盘访问（蓝牙键盘）兼容。测试导航顺序和焦点行为。

---

## 6. 手势与输入
**影响：** 高

### 规则 6.1：使用标准手势
使用标准的 iOS 手势词汇：轻点、长按、滑动、捏合、旋转。用户已经了解这些。

| 手势 | 标准用法 |
|------|-------------|
| 轻点 | 主要操作、选择 |
| 长按 | 上下文菜单、预览 |
| 水平滑动 | 删除、归档、导航后退 |
| 垂直滑动 | 滚动、关闭表单 |
| 捏合 | 放大/缩小 |
| 两指旋转 | 旋转内容 |

### 规则 6.2：切勿覆盖系统手势
这些手势由系统保留，不得拦截：
- 从左侧边缘滑动（后退导航）
- 从左上角向下滑动（通知中心）
- 从右上角向下滑动（控制中心）
- 从底部向上滑动（主屏幕/应用切换器）

### 规则 6.3：自定义手势必须可发现
如果您添加了自定义手势，请提供视觉提示（例如，抓取手柄），并确保该操作也通过可见按钮或菜单项可用。

### 规则 6.4：支持所有输入方法
首先为触摸设计，但也要支持：
- 硬件键盘（iPad 键盘附件、蓝牙键盘）
- 辅助设备（开关控制、头部跟踪）
- 指针输入（辅助触控）

---

## 7. 组件
**影响：** 高

### 规则 7.1：按钮样式
适当使用内置按钮样式：
- `.borderedProminent` — 主要调用操作
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

### 规则 7.2：警告 — 仅限关键信息
仅在需要决策的关键信息时使用警告。优先使用 2 个按钮；最多 3 个。破坏性选项应使用 `.destructive` 角色。

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
// 非关键信息的警告 — 应该使用横幅或提示
.alert("提示", isPresented: $showTip) {
    Button("确定") { }
} message: {
    Text("向左滑动以删除项目。")
}
```

### 规则 7.3：用于范围任务的面板
为自包含任务显示面板。始终提供取消方式（关闭按钮或滑动取消）。使用 `.presentationDetents()` 用于半高度面板。

```swift
.sheet(isPresented: $showCompose) {
    NavigationStack {
        ComposeView()
            .navigationTitle("新建消息")
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

### 规则 7.4：列表 — 插入分组默认
使用 `.insetGrouped` 列表样式作为默认样式。支持滑动操作以执行常用操作。最小行高为 44pt。

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
                        Label("归档", systemImage: "archivebox")
                    }
                    .tint(.blue)
                }
        }
    }
}
.listStyle(.insetGrouped)
```

### 规则 7.5：标签栏行为
- 使用 SF Symbols 作为标签图标 — 选中标签使用填充变体，未选中标签使用轮廓变体
- 切换标签时切勿隐藏标签栏
- 使用 `.badge()` 标注重要计数

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
使用上下文菜单（长按）执行次要操作。切勿将上下文菜单作为唯一访问操作的方式。

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
- 切勿使用全屏阻塞式旋转动画

### 规则 7.9：SF Symbols — 渲染模式
为每个符号使用适当的渲染模式。单色是默认值；层次结构、调色板和多色在适当的地方提供更丰富的表达。始终优先选择最佳传达意义的符号渲染模式——不要在多色传达关键状态时默认为单色。

**正确：**
```swift
// 层次结构：单个颜色，自动不透明层
Image(systemName: "person.crop.circle.fill")
    .symbolRenderingMode(.hierarchical)
    .foregroundStyle(.blue)

// 多色：系统定义的每层颜色（例如，电池、天气）
Image(systemName: "battery.100percent.bolt")
    .symbolRenderingMode(.multicolor)

// 调色板：明确每层颜色
Image(systemName: "folder.badge.plus")
    .symbolRenderingMode(.palette)
    .foregroundStyle(.white, .blue)
```

**错误：**
```swift
// 单色符号具有有意义的多层
Image(systemName: "battery.100percent.bolt")
    .foregroundColor(.gray) // 丢失了上下文颜色意义
```

### 规则 7.10：SF Symbols — 重量和比例
将符号重量与相邻文本重量匹配。使用比例变体（`.small`, `.medium`, `.large`）而不是调整大小。符号重量不应比相邻文本更重。

**正确：**
```swift
Label("下载", systemImage: "arrow.down.circle.fill")
    .font(.body.weight(.semibold))
    // 符号自动继承 .semibold 权重通过 Label
```

**错误：**
```swift
HStack {
    Image(systemName: "arrow.down.circle.fill")
        .font(.system(size: 32)) // 显式大小忽略类型缩放
    Text("下载")
        .font(.body)
}
```

### 规则 7.11：SF Symbols — 动画（iOS 17+）
使用 `symbolEffect` 进行符号状态转换。优先使用离散效果（`.bounce`, `.pulse`）用于操作，使用无限效果（`.variableColor`) 用于持续状态。当 `contentTransition(.symbolEffect)` 可用时，不要在符号名称之间使用手动淡入淡出

**正确：**
```swift
Image(systemName: isLoading ? "arrow.2.circlepath" : "checkmark.circle")
    .contentTransition(.symbolEffect(.replace))
    .symbolEffect(.pulse, isActive: isLoading)
```

**错误：**
```swift
// 符号名称之间的手动不透明度淡入淡出
if isLoading {
    Image(systemName: "arrow.2.circlepath")
} else {
    Image(systemName: "checkmark.circle")
}
```

---

## 快速参考

| 需要 | 组件 | 备注 |
|------|-----------|-------|
| 顶级部分（3-5） | `TabView` with `.tabItem` | 底部标签栏，SF Symbols |
| 分层钻取 | `NavigationStack` | 根视图使用大标题，子视图使用内联标题 |
| 自包含任务 | `.sheet` | 滑动取消，取消/完成按钮 |
| 关键决策 | `.alert` | 优先使用 2 个按钮；最多 3 个。破坏性选项使用 `.destructive` 角色 |
| 次要操作 | `.contextMenu` | 长按；也必须在其他地方可用 |
| 滚动内容 | `List` with `.insetGrouped` | 最小行高 44pt，滑动操作 |
| 文本输入 | `TextField` / `TextEditor` | 标题在上方，验证在下方 |
| 选择（选项较少） | `Picker` | 分段用于 2-5，轮盘用于许多 |
| 选择（开/关） | `Toggle` | 列表行右侧对齐 |
| 搜索 | `.searchable` | 建议搜索，最近搜索 |
| 进度指示器（已知） | `ProgressView(value:total:)` | 显示百分比或剩余时间 |
| 进度指示器（未知） | `ProgressView()` | 内联，切勿全屏阻塞式 |
| 单次位置 | `LocationButton` | 无需持久权限 |
| 分享内容 | `ShareLink` | 系统分享表单 |
| 触觉反馈 | `UIImpactFeedbackGenerator` | `.light`, `.medium`, `.heavy` |
| 破坏性操作 | `Button(role: .destructive)` | 红色色调，通过警告确认 |

---

## 评估清单

使用此清单审计 iPhone 应用是否符合 HIG 合规性：

### 布局与安全区域
- [ ] 所有触摸目标至少为 44x44pt
- [ ] 无内容被裁剪在状态栏、动态岛或主指示器下方
- [ ] 主要操作位于屏幕底部（拇指区域）
- [ ] 布局从 iPhone SE（375pt 宽）到 iPhone Pro Max（430pt 宽）自适应，不会中断
- [ ] 间距、填充和元素大小对齐到 8pt 网格

### 导航
- [ ] 顶级部分使用底部标签栏（3-5）
- [ ] 切勿使用汉堡菜单
- [ ] 主要视图使用大标题
- [ ] 返回滑动始终工作
- [ ] 切换标签时保留状态

### 字体
- [ ] 所有文本使用内置文本样式或自定义字体，使其响应动态类型
- [ ] 支持动态类型，包括无障碍尺寸
- [ ] 布局在大文本尺寸下重新流式化（不截断重要文本）
- [ ] 最小文本大小为 11pt

### 颜色与暗黑模式
- [ ] 使用语义系统颜色或提供亮色/暗色资源库变体
- [ ] 暗黑模式看起来是经过深思熟虑的（而不仅仅是反转）
- [ ] 切勿仅依赖颜色
- [ ] 文本对比度满足 WCAG AA 对比度比例：正常文本为 4.5:1，大文本（18pt+ 或 14pt+ 粗体）为 3:1
- [ ] 支持显示 P3 广色域
- [ ] 背景层次结构使用三个级别以创建深度
- [ ] 交互元素使用单一强调色
- [ ] 所有交互元素使用单一强调色

### 无障碍
- [ ] VoiceOver 读取所有屏幕逻辑
- [ ] 粗体文本偏好得到尊重
- [ ] 减少动画禁用装饰性动画
- [ ] 增加对比度时，自定义颜色具有更高对比度的变体
- [ ] 信息必须通过多个渠道提供
- [ ] 所有手势都有替代交互
- [ ] 支持开关控制和完整键盘访问

### 手势与输入
- [ ] 使用标准手势
- [ ] 切勿覆盖系统手势
- [ ] 自定义手势必须可发现
- [ ] 支持所有输入方法

### 组件
- [ ] 按钮样式
- [ ] 警告仅用于关键信息
- [ ] 使用面板执行自包含任务
- [ ] 列表行至少 44pt 高
- [ ] 切换标签时标签栏始终可见
- [ ] 删除操作使用 `.destructive` 角色

### 模式
- [ ] Onboarding — 最大 3 页，可跳过
- [ ] 加载 — 骨架视图，无阻塞旋转动画
- [ ] 启动屏幕 — 与第一屏幕匹配
- [ ] 模态 — 仅在用户必须专注于特定任务时使用
- [ ] 通知 — 仅发送高价值内容
- [ ] 设置位置
- [ ] 反馈 — 视觉 + 触觉
- [ ] 显示等待状态立即
- [ ] 优先识别而非回忆

---

## 反模式

这些是违反 iOS 人类界面指南的常见错误。切勿这样做：

1. **汉堡菜单** — 使用标签栏。汉堡菜单隐藏导航，降低可发现性，最多可降低 50%。

2. **覆盖系统返回按钮** — 如果您替换返回按钮，请确保从左侧边缘滑动的手势仍然工作，通过 `NavigationStack`。

3. **全屏阻塞式旋转动画** — 使用骨架视图或内联进度指示器。阻塞式旋转动画使应用感觉冻结。

4. **启动屏幕带有标志** — 启动屏幕必须与应用的第一个屏幕匹配。品牌标识延迟会让人感觉不自然。

5. **在启动时请求所有权限** — 在启动时请求相机、位置、通知和联系人权限，大多数都会被拒绝。

6. **硬编码字体大小** — 使用文本样式。硬编码的尺寸不会随着动态类型缩放，会破坏数百万用户的应用。

7. **仅通过颜色传达信息** — 红色/绿色表示有效/无效会排除色盲用户。始终与图标或文本配对。

8. **警告用于非关键信息** — 警告中断流程并需要取消。使用横幅、提示或内联消息显示提示和非关键信息。

9. **切换标签时隐藏标签栏** — 切换标签时标签栏应始终可见。隐藏标签栏会使用户感到困惑。

10. **忽略安全区域** — 使用 `.ignoresSafeArea()` 在缺口/动态岛或主指示器下方会导致文本和按钮消失。

11. **非可取消模态** — 每个模态都必须有一个明确的取消方式（关闭按钮、取消、滑动取消）。将用户困在模态中是敌对的。

12. **自定义手势没有替代方案** — 三指滑动用于撤销是不可用的。提供可见按钮或菜单项作为替代方案。

13. **触摸目标太小** — 按钮和链接小于 44pt 会导致误触，尤其是在列表和工具栏中。

14. **堆叠模态** — 使用模态内的导航而不是堆叠多个模态。

15. **暗黑模式是事后思考** — 使用硬编码颜色意味着应用要么在暗色模式下损坏，要么在亮色模式下损坏。始终使用语义颜色。
