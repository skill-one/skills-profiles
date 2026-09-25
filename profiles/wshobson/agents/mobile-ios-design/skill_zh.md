# iOS移动端设计

掌握iOS人机界面指南（HIG）和SwiftUI模式，构建精致的原生iOS应用，使其在苹果平台上如鱼得水。

## 何时使用这项技能

- 按照苹果HIG设计iOS应用界面
- 构建SwiftUI视图和布局
- 实现iOS导航模式（NavigationStack、TabView、弹出层）
- 为iPhone和iPad创建自适应布局
- 使用SF Symbols和系统字体
- 构建可访问的iOS界面
- 实现iOS特有的手势和交互
- 针对Dynamic Type和暗黑模式进行设计

## 核心概念

### 1. 人机界面指南原则

**清晰度**：内容易于阅读，图标精确，装饰简洁
**让位**：UI帮助用户理解内容，但不与其竞争
**层次感**：视觉层和动画传达层级关系并支持导航

**平台考量**：

- **iOS**：触控优先，紧凑显示屏，竖屏方向
- **iPadOS**：更大的画布，多任务处理，指针支持
- **visionOS**：空间计算，眼/手输入

### 2. SwiftUI布局系统

**基于栈的布局**：

```swift
// 垂直布局并指定对齐方式
VStack(alignment: .leading, spacing: 12) {
    Text("标题")
        .font(.headline)
    Text("副标题")
        .font(.subheadline)
        .foregroundStyle(.secondary)
}

// 水平布局并设置弹性间距
HStack {
    Image(systemName: "star.fill")
    Text("精选")
    Spacer()
    Text("全部查看")
        .foregroundStyle(.blue)
}
```

**网格布局**：

```swift
// 自适应网格，填满可用宽度
LazyVGrid(columns: [
    GridItem(.adaptive(minimum: 150, maximum: 200))
], spacing: 16) {
    ForEach(items) { item in
        ItemCard(item: item)
    }
}

// 固定列网格
LazyVGrid(columns: [
    GridItem(.flexible()),
    GridItem(.flexible()),
    GridItem(.flexible())
], spacing: 12) {
    ForEach(items) { item in
        ItemThumbnail(item: item)
    }
}
```

### 3. 导航模式

**NavigationStack（iOS 16+）**：

```swift
struct ContentView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            List(items) { item in
                NavigationLink(value: item) {
                    ItemRow(item: item)
                }
            }
            .navigationTitle("项目")
            .navigationDestination(for: Item.self) { item in
                ItemDetailView(item: item)
            }
        }
    }
}
```

**TabView（iOS 18+）**：

```swift
struct MainTabView: View {
    @State private var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            Tab("首页", systemImage: "house", value: 0) {
                HomeView()
            }

            Tab("搜索", systemImage: "magnifyinglass", value: 1) {
                SearchView()
            }

            Tab("个人", systemImage: "person", value: 2) {
                ProfileView()
            }
        }
    }
}
```

### 4. 系统集成

**SF Symbols**：

```swift
// 基本符号
Image(systemName: "heart.fill")
    .foregroundStyle(.red)

// 符号渲染模式
Image(systemName: "cloud.sun.fill")
    .symbolRenderingMode(.multicolor)

// 变量符号（iOS 16+）
Image(systemName: "speaker.wave.3.fill", variableValue: volume)

// 符号效果（iOS 17+）
Image(systemName: "bell.fill")
    .symbolEffect(.bounce, value: notificationCount)
```

**Dynamic Type**：

```swift
// 使用语义字体
Text("标题")
    .font(.headline)

Text("正文文本，随用户偏好缩放")
    .font(.body)

// 尊重Dynamic Type的自定义字体
Text("自定义")
    .font(.custom("Avenir", size: 17, relativeTo: .body))
```

### 5. 视觉设计

**颜色和材质**：

```swift
// 适应亮/暗模式的语义颜色
Text("主要")
    .foregroundStyle(.primary)
Text("次要")
    .foregroundStyle(.secondary)

// 系统材质用于模糊效果
Rectangle()
    .fill(.ultraThinMaterial)
    .frame(height: 100)

// 鲜艳材质用于叠加层
Text("叠加")
    .padding()
    .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 12))
```

**阴影和深度**：

```swift
// 标准卡片阴影
RoundedRectangle(cornerRadius: 16)
    .fill(.background)
    .shadow(color: .black.opacity(0.1), radius: 8, y: 4)

// 提升外观
.shadow(radius: 2, y: 1)
.shadow(radius: 8, y: 4)
```

## 快速入门组件

```swift
import SwiftUI

struct FeatureCard: View {
    let title: String
    let description: String
    let systemImage: String

    var body: some View {
        HStack(spacing: 16) {
            Image(systemName: systemImage)
                .font(.title)
                .foregroundStyle(.blue)
                .frame(width: 44, height: 44)
                .background(.blue.opacity(0.1), in: Circle())

            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.headline)
                Text(description)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
            }

            Spacer()

            Image(systemName: "chevron.right")
                .foregroundStyle(.tertiary)
        }
        .padding()
        .background(.background, in: RoundedRectangle(cornerRadius: 12))
        .shadow(color: .black.opacity(0.05), radius: 4, y: 2)
    }
}
```

## 最佳实践

1. **使用语义颜色**：始终使用`.primary`、`.secondary`、`.background`以支持自动亮/暗模式
2. **拥抱SF Symbols**：使用系统符号以保持一致性并支持自动可访问性
3. **支持Dynamic Type**：使用语义字体（`.body`、`.headline`）而非固定尺寸
4. **添加可访问性**：包含`.accessibilityLabel()`和`.accessibilityHint()`修饰符
5. **使用安全区域**：尊重`safeAreaInset`，避免在屏幕边缘使用硬编码的填充
6. **实现状态恢复**：使用`@SceneStorage`以保存用户状态
7. **支持iPad多任务处理**：设计以适应分屏和滑动覆盖
8. **在设备上测试**：模拟器无法完全捕捉触觉和性能体验

## 常见问题

- **布局失效**：谨慎使用`.fixedSize()`；优先选择弹性布局
- **性能问题**：使用`LazyVStack`/`LazyHStack`用于长滚动列表
- **导航错误**：确保`NavigationLink`的值是`Hashable`
- **暗黑模式问题**：避免硬编码颜色；使用语义或资源库颜色
- **可访问性失败**：使用VoiceOver进行测试
- **内存泄漏**：注意闭包中的强引用循环
