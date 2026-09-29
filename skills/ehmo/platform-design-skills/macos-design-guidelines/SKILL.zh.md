---
name: macos-design-guidelines
description: 苹果Mac人类界面指南。在用SwiftUI或AppKit构建macOS应用程序时使用，用于实现菜单栏、工具栏、窗口管理或键盘快捷键。涉及Mac UI、桌面应用程序或Mac Catalyst的任务时触发。
---

# macOS Human Interface Guidelines

Mac 应用程序服务于需要深度键盘控制、持久菜单栏、可调整大小的多窗口布局和紧密系统集成的专业用户。这些指南将 Apple 的 HIG 转化为可操作的 SwiftUI 和 AppKit 示例规则。

---

## 1. 菜单栏（关键）

每个 Mac 应用程序都必须有一个菜单栏。它是命令的主要发现机制。无法找到功能的用户会在菜单栏中查找，而不是其他任何地方。

### 规则 1.1 — 提供标准菜单

每个应用程序至少必须包含：**应用程序**、**文件**、**编辑**、**视图**、**窗口**、**帮助**。如果应用程序不是基于文档的，则可以省略“文件”。在“编辑”和“视图”之间或“视图”和“窗口”之间添加特定于应用程序的菜单。

```swift
// SwiftUI — 标准菜单结构
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .commands {
            // 添加到现有的标准菜单
            CommandGroup(after: .newItem) {
                Button("从模板新建...") { newFromTemplate() }
                    .keyboardShortcut("T", modifiers: [.command, .shift])
            }
            CommandMenu("画布") {
                Button("适应缩放") { zoomToFit() }
                    .keyboardShortcut("0", modifiers: .command)
                Divider()
                Button("添加画板") { addArtboard() }
                    .keyboardShortcut("A", modifiers: [.command, .shift])
            }
        }
    }
}
```

```swift
// AppKit — 程序设计方式构建菜单
let editMenu = NSMenu(title: "编辑")
let undoItem = NSMenuItem(title: "撤销", action: #selector(UndoManager.undo), keyEquivalent: "z")
let redoItem = NSMenuItem(title: "重做", action: #selector(UndoManager.redo), keyEquivalent: "Z")
editMenu.addItem(undoItem)
editMenu.addItem(redoItem)
editMenu.addItem(.separator())
```

### 规则 1.2 — 所有菜单项的键盘快捷键

执行操作的每个菜单项都必须有一个键盘快捷键。使用标准快捷键执行标准操作（Cmd+C、Cmd+V、Cmd+Z 等）。自定义快捷键应使用 Cmd 加字母。保留 Cmd+Shift、Cmd+Option 和 Cmd+Ctrl 组合键用于次要操作。

**标准快捷键参考：**

| 操作 | 快捷键 |
|------|----------|
| 新建 | Cmd+N |
| 打开 | Cmd+O |
| 关闭 | Cmd+W |
| 保存 | Cmd+S |
| 另存为 | Cmd+Shift+S |
| 打印 | Cmd+P |
| 撤销 | Cmd+Z |
| 重做 | Cmd+Shift+Z |
| 剪切 | Cmd+X |
| 复制 | Cmd+C |
| 粘贴 | Cmd+V |
| 全选 | Cmd+A |
| 搜索 | Cmd+F |
| 搜索下一个 | Cmd+G |
| 首选项/设置 | Cmd+, |
| 隐藏应用程序 | Cmd+H |
| 退出 | Cmd+Q |
| 最小化 | Cmd+M |
| 全屏 | Cmd+Ctrl+F |

### 规则 1.3 — 动态菜单更新

菜单项必须反映当前状态。禁用不相关的项。更新标题以匹配上下文（例如，“撤销输入”而不是“撤销”）。切换复选标记以表示开/关状态。

```swift
// SwiftUI — 在现有的工具栏菜单命令旁边添加侧边栏切换
CommandGroup(after: .toolbar) {
    Button(showingSidebar ? "隐藏侧边栏" : "显示侧边栏") {
        showingSidebar.toggle()
    }
    .keyboardShortcut("S", modifiers: [.command, .control])
}
```

```swift
// AppKit — 验证菜单项
override func validateMenuItem(_ menuItem: NSMenuItem) -> Bool {
    if menuItem.action == #selector(delete(_:)) {
        menuItem.title = selectedItems.count > 1 ? "删除 \(selectedItems.count) 项" : "删除"
        return !selectedItems.isEmpty
    }
    return super.validateMenuItem(menuItem)
}
```

### 规则 1.4 — 上下文菜单

在所有交互元素上提供右键单击上下文菜单。上下文菜单应包含与被单击元素最相关的菜单栏操作子集，以及特定于元素的操作。

```swift
// SwiftUI
Text(item.name)
    .contextMenu {
        Button("重命名...") { rename(item) }
        Button("复制") { duplicate(item) }
        Divider()
        Button("删除", role: .destructive) { delete(item) }
    }
```

### 规则 1.5 — 应用程序菜单结构

应用程序菜单（最左侧、粗体应用程序名称）必须包含：关于、首选项/设置（Cmd+,）、服务子菜单、隐藏应用程序（Cmd+H）、隐藏其他（Cmd+Option+H）、显示全部、退出（Cmd+Q）。永远不要重命名或删除这些标准项。

```swift
// SwiftUI — 设置场景
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup { ContentView() }
        Settings { SettingsView() }  // 自动连接到 Cmd+,
    }
}
```

### 规则 1.6 — 稳定的命令名称和位置

将菜单栏视为应用程序的命令内存。将常用操作保持在具有稳定名称和快捷键的始终一致的菜单中，以便用户可以快速识别它们，而不是搜索特定于上下文的变体。

---

## 2. 窗口（关键）

Mac 用户期望对窗口大小、位置和生命周期有完全的控制。与窗口管理作斗争的应用程序在 Mac 上感觉基本上是损坏的。

### 规则 2.1 — 可调整大小，具有合理的最小值

所有主窗口必须可以自由调整大小。设置一个最小尺寸，以保持 UI 可用。除非内容确实无法缩放（很少见），否则永远不要设置最大尺寸。

```swift
// SwiftUI
WindowGroup {
    ContentView()
        .frame(minWidth: 600, minHeight: 400)
}
.defaultSize(width: 900, height: 600)
```

```swift
// AppKit
window.minSize = NSSize(width: 600, height: 400)
window.setContentSize(NSSize(width: 900, height: 600))
```

### 规则 2.2 — 支持全屏和分屏视图

通过设置适当的风窗集行为来选择进入原生全屏。绿色交通灯按钮必须进入全屏或显示磁贴选择器。

```swift
// AppKit
window.collectionBehavior.insert(.fullScreenPrimary)
```

SwiftUI 窗口自动获得全屏支持。

### 规则 2.3 — 多个窗口

除非您的应用程序是单一用途的工具，否则请支持多个窗口。基于文档的应用程序必须允许同时打开多个文档。在 SwiftUI 中使用 `WindowGroup` 或 `DocumentGroup`。

```swift
// SwiftUI — 基于文档的应用程序
@main
struct TextEditorApp: App {
    var body: some Scene {
        DocumentGroup(newDocument: TextDocument()) { file in
            TextEditorView(document: file.$document)
        }
    }
}
```

### 规则 2.4 — 标题栏显示文档信息

对于基于文档的应用程序，标题栏必须显示文档名称。支持代理图标拖动。显示编辑状态（关闭按钮中的点）。支持单击标题栏重命名。

```swift
// AppKit
window.representedURL = document.fileURL
window.title = document.displayName
window.isDocumentEdited = document.hasUnsavedChanges
```

```swift
// SwiftUI — NavigationSplitView 标题
NavigationSplitView {
    SidebarView()
} detail: {
    DetailView()
        .navigationTitle(document.name)
}
```

### 规则 2.5 — 记忆窗口状态

跨启动持久化窗口位置、大小和状态。使用 `NSWindow.setFrameAutosaveName` 或 SwiftUI 的内置状态恢复。

```swift
// AppKit
window.setFrameAutosaveName("MainWindow")

// SwiftUI — 自动使用 WindowGroup
WindowGroup(id: "main") {
    ContentView()
}
.defaultPosition(.center)
```

### 规则 2.6 — 交通灯按钮

永远不要隐藏或重新定位关闭（红色）、最小化（黄色）或缩放（绿色）按钮。它们必须保持在左上角。如果使用自定义标题栏，按钮仍然必须可见且功能正常。

```swift
// AppKit — 自定义标题栏保留交通灯
window.titlebarAppearsTransparent = true
window.styleMask.insert(.fullSizeContentView)
// 交通灯仍然功能正常且可见
```

---

## 3. 工具栏（高）

工具栏是菜单栏之后的次要命令表面。它们提供对频繁操作的快速访问，并且应该是可定制的。

### 规则 3.1 — 统一标题栏和工具栏

使用统一标题栏+工具栏样式以获得现代外观。工具栏位于标题栏区域，节省垂直空间。

```swift
// SwiftUI
WindowGroup {
    ContentView()
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button(action: compose) {
                    Label("新建", systemImage: "square.and.pencil")
                }
            }
        }
}
.windowToolbarStyle(.unified)
```

```swift
// AppKit
window.titleVisibility = .hidden
window.toolbarStyle = .unified
```

### 规则 3.2 — 用户可定制的工具栏

允许用户添加、删除和重新排列工具栏项。提供默认集和可用项的超集。

```swift
// SwiftUI — 可定制的工具栏
.toolbar(id: "main") {
    ToolbarItem(id: "compose", placement: .primaryAction) {
        Button(action: compose) {
            Label("新建", systemImage: "square.and.pencil")
        }
    }
    ToolbarItem(id: "filter", placement: .secondaryAction) {
        Button(action: toggleFilter) {
            Label("筛选", systemImage: "line.3.horizontal.decrease")
        }
    }
}
.toolbarRole(.editor)
```

### 规则 3.3 — 分段控件用于视图切换

在工具栏中使用分段控件或选择器在内容视图之间切换（例如，列表/网格/列）。这是一个工具栏模式，而不是标签栏。

```swift
// SwiftUI
ToolbarItem(placement: .principal) {
    Picker("视图模式", selection: $viewMode) {
        Label("列表", systemImage: "list.bullet").tag(ViewMode.list)
        Label("网格", systemImage: "square.grid.2x2").tag(ViewMode.grid)
        Label("列", systemImage: "rectangle.split.3x1").tag(ViewMode.column)
    }
    .pickerStyle(.segmented)
}
```

### 规则 3.4 — 工具栏中的搜索字段

在工具栏的尾部区域放置搜索字段。在 SwiftUI 中使用 `.searchable()` 以获得带有建议和标记的标准搜索行为。

```swift
// SwiftUI
NavigationSplitView {
    SidebarView()
} detail: {
    ContentListView()
        .searchable(text: $searchText, placement: .toolbar, prompt: "搜索项")
        .searchSuggestions {
            ForEach(suggestions) { suggestion in
                Text(suggestion.title).searchCompletion(suggestion.title)
            }
        }
}
```

### 规则 3.5 — 工具栏标签和图标

工具栏项应同时具有图标（SF Symbol）和文本标签。在紧凑模式下，仅显示图标。优先使用带标签的图标以提高可发现性。使用 `Label` 提供两者。

---

## 4. 侧边栏（高）

侧边栏是 Mac 应用程序的主要导航表面。它们出现在主导边缘，并提供对顶级部分和内容库的持久访问。

### 规则 4.1 — 主导边缘，可折叠

将侧边栏放在左侧（主导）边缘。通过工具栏按钮或键盘快捷键使其可折叠。Apple 没有定义通用的侧边栏快捷键——选择一个适合您应用程序的快捷键（例如，Cmd+Ctrl+S 是常见的，但并非所有应用程序中都保证是空闲的）。持久化折叠状态。

```swift
// SwiftUI
NavigationSplitView(columnVisibility: $columnVisibility) {
    List(selection: $selection) {
        Section("库") {
            Label("所有项", systemImage: "tray.full")
            Label("收藏", systemImage: "star")
            Label("最近", systemImage: "clock")
        }
        Section("标签") {
            ForEach(tags) { tag in
                Label(tag.name, systemImage: "tag")
            }
        }
    }
    .navigationSplitViewColumnWidth(min: 180, ideal: 220, max: 320)
} detail: {
    DetailView(selection: selection)
}
.navigationSplitViewStyle(.prominentDetail)
```

### 规则 4.2 — 源列表样式

使用源列表样式（`.listStyle(.sidebar)`）进行内容库导航。源列表具有半透明背景，可以看到它们后面的桌面或窗口，并具有活力效果。

```swift
// SwiftUI
List(selection: $selection) {
    ForEach(sections) { section in
        Section(section.name) {
            ForEach(section.items) { item in
                NavigationLink(value: item) {
                    Label(item.name, systemImage: item.icon)
                }
            }
        }
    }
}
.listStyle(.sidebar)
```

### 规则 4.3 — 用于层次结构的轮廓视图

当内容是层次结构（例如，文件夹树、项目结构）时，使用展开组或轮廓视图以允许用户展开和折叠级别。

```swift
// SwiftUI — 递归轮廓
List(selection: $selection) {
    OutlineGroup(rootNodes, children: \.children) { node in
        Label(node.name, systemImage: node.icon)
    }
}
```

### 规则 4.4 — 拖动以重新排序

可重新排序的侧边栏项（书签、收藏、自定义部分）必须支持拖动以重新排序。实现 `onMove` 或 `NSOutlineView` 拖动代理。

```swift
// SwiftUI
ForEach(favorites) { item in
    Label(item.name, systemImage: item.icon)
}
.onMove { source, destination in
    favorites.move(fromOffsets: source, toOffset: destination)
}
```

### 规则 4.5 — 带徽章计数的项

在侧边栏项上显示徽章计数，用于未读计数、待处理项或通知。使用 `.badge()` 修饰符。

```swift
// SwiftUI
Label("收件箱", systemImage: "tray")
    .badge(unreadCount)
```

---

## 5. 键盘（关键）

Mac 用户比任何其他平台都更依赖键盘快捷键。没有全面键盘支持的应用程序是损坏的 Mac 应用程序。

### 规则 5.1 — 所有操作的 Cmd 快捷键

通过鼠标可达的每个操作都必须有一个键盘等效项。主要操作使用 Cmd+字母。次要操作使用 Cmd+Shift 或 Cmd+Option。三级操作使用 Cmd+Ctrl。

**键盘快捷键约定：**

| 修饰符模式 | 使用 |
|-----------------|-------|
| Cmd+字母 | 主要操作（新建、打开、保存等） |
| Cmd+Shift+字母 | 主要变体（另存为、查找上一个） |
| Cmd+Option+字母 | 替代模式（粘贴并匹配样式） |
| Cmd+Ctrl+字母 | 窗口/视图控制（全屏、侧边栏） |
| Ctrl+字母 | Emacs 风格的文本导航（可接受） |
| Fn+键 | 系统功能（F11 显示桌面等） |

### 规则 5.2 — 全键盘导航

支持 Tab 在控件之间移动。支持箭头键在列表、网格和表格内移动。支持 Shift+Tab 进行反向导航。使用 `focusable()` 和 `@FocusState` 在 SwiftUI 中。

```swift
// SwiftUI — 聚焦管理
struct ContentView: View {
    @FocusState private var focusedField: Field?

    var body: some View {
        VStack {
            TextField("名称", text: $name)
                .focused($focusedField, equals: .name)
            TextField("电子邮件", text: $email)
                .focused($focusedField, equals: .email)
        }
        .onSubmit { advanceFocus() }
    }
}
```

### 规则 5.3 — Escape 取消或关闭

Escape 必须关闭弹出窗口、表单、对话框和取消进行中的操作。在文本字段中，Escape 恢复到上一个值。在模态对话框中，Escape 等同于单击取消。

```swift
// SwiftUI — 支持 Escape 的表单（自动）
.sheet(isPresented: $showingSheet) {
    SheetView()  // Escape 自动关闭
}

// AppKit — 自定义响应者
override func cancelOperation(_ sender: Any?) {
    dismiss(nil)
}
```

### 规则 5.4 — Return 默认操作

在对话框和表单中，Return/Enter 激活默认按钮（在蓝色中视觉强调）。默认按钮始终是最安全的默认操作。

```swift
// SwiftUI
Button("保存") { save() }
    .keyboardShortcut(.defaultAction)  // Enter 键

Button("取消") { cancel() }
    .keyboardShortcut(.cancelAction)   // Escape 键
```

### 规则 5.5 — Delete 删除

Delete 键（Backspace）必须从列表、表格和集合中删除选定项。Cmd+Delete 用于更破坏性的删除（移动到废纸篓）。始终支持 Cmd+Z 以撤销删除。

### 规则 5.6 — Space 快速预览

当项支持预览时，Space 键应调用快速预览。在 AppKit 中使用 `QLPreviewPanel` API 或 SwiftUI 中的 `.quickLookPreview()`。

```swift
// SwiftUI
List(selection: $selection) {
    ForEach(files) { file in
        FileRow(file: file)
    }
}
.quickLookPreview($quickLookItem, in: files)
```

### 规则 5.7 — 箭头键导航

在列表和网格中，上/下箭头键移动选择。左/右箭头键折叠/展开显示组或导航列。Cmd+上箭头键跳转到开头，Cmd+下箭头键跳转到结尾。

---

## 6. 指针和鼠标（高优先级）

Mac 是一个指针驱动平台。每个交互元素必须响应悬停、点击、右键点击和拖动。

### 规则 6.1 — 悬停状态

所有交互元素必须具有可见的悬停状态。按钮高亮显示，行显示选择指示器，链接改变光标。在 SwiftUI 中使用 `.onHover`。

```swift
// SwiftUI — 悬停效果
struct HoverableRow: View {
    @State private var isHovered = false

    var body: some View {
        HStack {
            Text(item.name)
            Spacer()
            if isHovered {
                Button("编辑") { edit() }
                    .buttonStyle(.borderless)
            }
        }
        .padding(8)
        .background(isHovered ? Color.primary.opacity(0.05) : .clear)
        .cornerRadius(6)
        .onHover { hovering in isHovered = hovering }
    }
}
```

### 规则 6.2 — 右键点击上下文菜单

每个交互元素必须响应右键点击并显示上下文菜单。上下文菜单应包含与点击项最相关的操作。

### 规则 6.3 — 拖放

支持拖放以进行内容操作：重新排序项目、在容器之间移动、从访达导入文件、导出内容。

```swift
// SwiftUI — 拖放
ForEach(items) { item in
    ItemView(item: item)
        .draggable(item)
}
.dropDestination(for: Item.self) { items, location in
    handleDrop(items, at: location)
    return true
}
```

```swift
// 从访达接受文件拖放
.dropDestination(for: URL.self) { urls, location in
    importFiles(urls)
    return true
}
```

### 规则 6.4 — 滚动行为

支持触控板（平滑/惯性）和鼠标滚轮（离散）滚动。在内容边界使用弹性/弹跳滚动。在适当的地方支持水平滚动。

### 规则 6.5 — 光标变化

改变光标以指示可操作性：指针用于可点击元素，I 形光标用于文本，十字光标用于绘图，窗口/分隔器边缘的调整大小手柄，拖动内容的抓手光标。

```swift
// AppKit — 自定义光标
override func resetCursorRects() {
    addCursorRect(bounds, cursor: .crosshair)
}
```

### 规则 6.6 — 多选

在列表、表格和网格中支持 Cmd+点击进行非连续选择，Shift+点击进行范围选择。这是一个根深蒂固的 Mac 交互模式。

```swift
// SwiftUI — 带多选的表格
Table(items, selection: $selectedItems) {
    TableColumn("名称", value: \.name)
    TableColumn("日期", value: \.dateFormatted)
    TableColumn("大小", value: \.sizeFormatted)
}
```

---

## 7. 通知和警报（中优先级）

Mac 用户对自己的注意力很保护。只有在真正必要时才中断。

### 规则 7.1 — 适当使用通知中心

仅对应用程序外部发生的事件或需要用户操作的事件发送通知。切勿为常规操作发送通知。通知必须是可操作的。

```swift
// UserNotifications
let content = UNMutableNotificationContent()
content.title = "下载完成"
content.body = "project-assets.zip 已准备好"
content.categoryIdentifier = "DOWNLOAD"
content.sound = .default

let request = UNNotificationRequest(identifier: UUID().uuidString, content: content, trigger: nil)
UNUserNotificationCenter.current().add(request)
```

### 规则 7.2 — 带抑制选项的警报

对于重复警报，提供一个“不再显示”复选框。尊重用户的选择并持久化它。

```swift
// AppKit — 带抑制的警报
let alert = NSAlert()
alert.messageText = "从库中删除？"
alert.informativeText = "文件将被移动到废纸篓。"
alert.alertStyle = .warning
alert.addButton(withTitle: "删除")
alert.addButton(withTitle: "取消")
alert.showsSuppressionButton = true
alert.suppressionButton?.title = "不再询问"

let response = alert.runModal()
if alert.suppressionButton?.state == .on {
    UserDefaults.standard.set(true, forKey: "suppressRemoveAlert")
}
```

### 规则 7.3 — 切勿不必要的打断

切勿为成功操作显示警报。使用内联状态指示器、工具栏徽章或微妙动画代替。仅将模态警报保留用于破坏性或不可逆操作。

### 规则 7.4 — Dock 徽章

在 Dock 图标上显示通知计数的徽章。当用户处理通知时立即清除它。

```swift
// AppKit
NSApp.dockTile.badgeLabel = unreadCount > 0 ? "\(unreadCount)" : nil
```

### 规则 7.5 — 与认知成本匹配的反馈

常规操作应使用内联状态、工具栏状态或微妙动画来确认完成。仅在用户必须停止、评估后果并选择时使用模态警报。

---

## 8. 系统集成（中优先级）

Mac 应用程序存在于丰富的生态系统中。深度集成使应用程序感觉原生。

### 规则 8.1 — Dock 图标和菜单

提供一个高质量的 1024x1024 应用程序图标。支持 Dock 右键点击菜单以快速执行操作。在 Dock 菜单中显示最近文档。

```swift
// AppKit — Dock 菜单
override func applicationDockMenu(_ sender: NSApplication) -> NSMenu? {
    let menu = NSMenu()
    menu.addItem(withTitle: "新建窗口", action: #selector(newWindow(_:)), keyEquivalent: "")
    menu.addItem(withTitle: "新建文档", action: #selector(newDocument(_:)), keyEquivalent: "")
    menu.addItem(.separator())
    for doc in recentDocuments.prefix(5) {
        menu.addItem(withTitle: doc.name, action: #selector(openRecent(_:)), keyEquivalent: "")
    }
    return menu
}
```

### 规则 8.2 — Spotlight 集成

使用 `CSSearchableItem` 和 Core Spotlight 为 Spotlight 搜索索引应用程序内容。用户期望通过 Cmd+空格找到应用程序内容。

```swift
import CoreSpotlight

let attributeSet = CSSearchableItemAttributeSet(contentType: .text)
attributeSet.title = document.title
attributeSet.contentDescription = document.summary
attributeSet.thumbnailData = document.thumbnail?.pngData()

let item = CSSearchableItem(uniqueIdentifier: document.id, domainIdentifier: "documents", attributeSet: attributeSet)
CSSearchableIndex.default().indexSearchableItems([item])
```

### 规则 8.3 — 支持 Quick Look

通过 Quick Look 预览扩展为自定义文件类型提供 Quick Look 预览。用户期望通过空格键在访达中预览任何文件。

### 规则 8.4 — 分享扩展

实现分享菜单，以便用户可以将内容从您的应用程序分享到消息、邮件、笔记等。还接受来自其他应用程序的共享内容。

```swift
// SwiftUI
ShareLink(item: document.url) {
    Label("分享", systemImage: "square.and.arrow.up")
}
```

### 规则 8.5 — 服务菜单

注册服务菜单以接收来自其他应用程序的文本、URL 或文件。这是 Mac 独有的集成点，高级用户依赖于此。

### 规则 8.6 — 快捷方式和 AppleScript

通过提供 App Intents 支持快捷方式应用程序。对于高级自动化，通过 `.sdef` 脚本字典添加 AppleScript/JXA 脚本支持。

```swift
// App Intents for Shortcuts
struct CreateDocumentIntent: AppIntent {
    static var title: LocalizedStringResource = "创建文档"
    static var description = IntentDescription("使用给定标题创建新文档。")

    @Parameter(title: "标题")
    var title: String

    func perform() async throws -> some IntentResult {
        let doc = DocumentManager.shared.create(title: title)
        return .result(value: doc.title)
    }
}
```

---

## 9. 视觉设计（高优先级）

Mac 应用程序应看起来和感觉像是它们属于该平台。使用系统提供的材料、字体和颜色。

### 规则 9.1 — 使用系统字体

使用 SF Pro（系统字体）在标准动态类型大小下。使用 SF Mono 用于代码。切勿硬编码字体大小；使用语义样式。

```swift
// SwiftUI — 语义字体样式
Text("标题").font(.title)
Text("标题行").font(.headline)
Text("正文").font(.body)
Text("说明").font(.caption)
Text("let x = 42").font(.system(.body, design: .monospaced))
```

### 规则 9.2 — Vibrancy 和材料

使用系统材料作为侧边栏和工具栏背景。Vibrancy 使桌面或底层内容显示出来，将应用程序锚定到 Mac 视觉语言。

```swift
// SwiftUI
List { ... }
    .listStyle(.sidebar)  // 自动 vibrancy

// 自定义 vibrancy
ZStack {
    VisualEffectView(material: .sidebar, blendingMode: .behindWindow)
    Text("侧边栏内容")
}
```

```swift
// AppKit — 视觉效果视图
let visualEffect = NSVisualEffectView()
visualEffect.material = .sidebar
visualEffect.blendingMode = .behindWindow
visualEffect.state = .followsWindowActiveState
```

### 规则 9.3 — 尊重系统强调色

使用系统强调色进行选择、强调和交互元素。切勿使用固定的品牌颜色覆盖标准控件。仅在自定义视图上适当使用 `.accentColor` 或 `.tint`。

```swift
// SwiftUI — 自动跟随系统强调色
Button("操作") { doSomething() }
    .buttonStyle(.borderedProminent)  // 使用系统强调色

Toggle("启用功能", isOn: $isEnabled)  // Toggle tint 跟随强调色
```

### 规则 9.4 — 支持暗黑模式

每个视图都必须支持亮色和暗色外观。使用语义颜色（`Color.primary`、`Color.secondary`、`.background`）而不是硬编码颜色。在两种模式下进行测试。

```swift
// SwiftUI — 语义颜色
Text("标题").foregroundStyle(.primary)
Text("副标题").foregroundStyle(.secondary)

RoundedRectangle(cornerRadius: 8)
    .fill(Color(nsColor: .controlBackgroundColor))

// 资源库：为两种外观定义颜色
// 切勿使用 Color.white 或 Color.black 用于 UI 表面
```

### 规则 9.5 — 透明度

尊重“减少透明度”的可访问性设置。当透明度减少时，用实心背景替换半透明材料。

```swift
// SwiftUI
@Environment(\.accessibilityReduceTransparency) var reduceTransparency

var body: some View {
    if reduceTransparency {
        Color(nsColor: .windowBackgroundColor)
    } else {
        VisualEffectView(material: .sidebar, blendingMode: .behindWindow)
    }
}
```

### 规则 9.6 — 一致的间距和布局

使用 20pt 标准边距，相关控件之间使用 8pt 间距，组之间使用 20pt 间距。将控件对齐到网格。使用 SwiftUI 的内置间距或 AppKit 的 Auto Layout 与系统间距约束。

---

## 10. Popover（中优先级）

Popover 显示锚定到控件的上下文内容。它们在 Mac 应用程序中很常见，用于选项面板、颜色选择器和上下文设置。

### 规则 10.1 — 使用 Popover 显示暂时的上下文敏感内容

Popover 锚定到源视图，并通过点击外部或按 Esc 关闭。使用它们来设置特定元素的应用程序或选项。不要使用 Popover 显示主要工作流程或多步骤操作。

```swift
// SwiftUI
Button("格式化...") { showingFormatPopover = true }
    .popover(isPresented: $showingFormatPopover, arrowEdge: .bottom) {
        FormatOptionsView()
            .frame(width: 280)
            .padding()
    }
```

### 规则 10.2 — 使用 Esc 关闭 Popover

当用户按 Esc 时，Popover 必须关闭。SwiftUI 会自动为 `.popover` 处理此操作。AppKit 的 `NSPopover` 在 `behavior` 设置为 `.transient` 或 `.semitransient` 时也会在 Esc 时关闭。

### 规则 10.3 — 调整 Popover 以适应其内容

为 Popover 内容设置一个合理的宽度。不要让 Popover 比必要时更宽。内容不应需要滚动，除非列表本身很长（例如，字体选择器）。

---

## 11. 可访问性（关键）

Mac 应用程序必须支持 VoiceOver、全键盘访问、切换控制和相关辅助技术。

### 规则 11.1 — 所有交互元素上的 VoiceOver 标签

每个按钮、控件和交互元素都必须具有有意义的可访问性标签。仅包含图标的工具栏项和图像按钮必须提供标签。

**正确：**
```swift
Button(action: deleteSelected) {
    Image(systemName: "trash")
}
.accessibilityLabel("删除选定项")
```

**不正确：**
```swift
Button(action: deleteSelected) {
    Image(systemName: "trash")
}
// VoiceOver 读取 "trash" — 在没有上下文的情况下含义不明确
```

### 规则 11.2 — 全键盘访问

通过鼠标可达的每个操作都必须通过键盘也可达。Tab 必须在所有控件之间移动焦点。箭头键必须在列表、表格和网格中导航。没有键盘陷阱。

```swift
// SwiftUI — 确保所有自定义视图都是可聚焦的
MyCustomControl()
    .focusable()
    .onKeyPress(.return) { handleActivation(); return .handled }
```

### 规则 11.3 — 尊重减少动画

当用户启用减少动画时，禁用或替换装饰性动画。

```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion

var body: some View {
    ContentView()
        .animation(reduceMotion ? nil : .spring(), value: isExpanded)
}
```

### 规则 11.4 — 尊重减少透明度

当启用减少透明度时（见规则 9.5），用实心背景替换半透明材料。

### 规则 11.5 — 逻辑焦点顺序

VoiceOver 必须按逻辑阅读顺序遍历元素（从左上到右下，对于从左到右的文本）。当视觉布局与逻辑顺序不一致时，使用 `.accessibilitySortPriority()` 或 `accessibilityElement(children:)` 来纠正顺序。

### 规则 11.6 — 响应粗体文本

当用户在系统设置中启用粗体文本时，自定义渲染的文本必须适应。SwiftUI 文本样式会自动处理此操作。对于 AppKit，检查 `NSWorkspace.shared.accessibilityDisplayShouldUseBoldText`，或使用 SwiftUI 中的 `@Environment(\.legibilityWeight)` 来将较重的权重应用于自定义文本。

**正确：**
```swift
// SwiftUI — 环境自动处理标准样式的粗体文本
Text("部分标题")
    .font(.headline)

// SwiftUI — 自定义渲染响应 legibilityWeight
@Environment(\.legibilityWeight) var legibilityWeight

var body: some View {
    Text("自定义标签")
        .fontWeight(legibilityWeight == .bold ? .bold : .regular)
}
```

**不正确：**
```swift
// 硬编码权重忽略粗体文本设置
Text("自定义标签")
    .fontWeight(.regular) // 从不适应粗体文本设置
```

### 规则 11.7 — 响应增加对比度

当用户在系统设置中启用增加对比度时，自定义颜色必须提供更高对比度的变体。使用 `NSWorkspace.shared.accessibilityDisplayShouldIncreaseContrast` 在 AppKit 中，或使用 SwiftUI 中的 `@Environment(\.colorSchemeContrast)` 来检测并应用适当的值。

**正确：**
```swift
// SwiftUI
@Environment(\.colorSchemeContrast) var contrast

var borderColor: Color {
    contrast == .increased ? Color.primary : Color.secondary
}

// AppKit
let shouldIncrease = NSWorkspace.shared.accessibilityDisplayShouldIncreaseContrast
let borderColor: NSColor = shouldIncrease ? .labelColor : .separatorColor
```

**不正确：**
```swift
// 静态颜色忽略增加对比度设置
let borderColor = NSColor.separatorColor // 始终低对比度；忽略用户偏好
```

---

## 键盘快捷键快速参考

### 导航
| 快捷键 | 操作 |
|----------|--------|
| Cmd+N | 新建窗口/文档 |
| Cmd+O | 打开 |
| Cmd+W | 关闭窗口/标签 |
| Cmd+Q | 退出应用程序 |
| Cmd+, | 设置/偏好设置 |
| Cmd+Tab | 切换应用程序 |
| Cmd+` | 在应用程序内切换窗口 |
| Cmd+T | 新建标签 |

### 编辑
| 快捷键 | 操作 |
|----------|--------|
| Cmd+Z | 撤销 |
| Cmd+Shift+Z | 重做 |
| Cmd+X / C / V | 剪切 / 复制 / 粘贴 |
| Cmd+A | 全选 |
| Cmd+D | 复制 |
| Cmd+F | 查找 |
| Cmd+G | 查找下一个 |
| Cmd+Shift+G | 查找上一个 |
| Cmd+E | 使用选定内容进行查找 |

### 查看
| 快捷键 | 操作 |
|----------|--------|
| Cmd+Ctrl+F | 切换全屏 |
| Cmd+Ctrl+S | 切换侧边栏（应用程序定义；不是通用的 HIG 标准） |
| Cmd++ / Cmd+- | 放大/缩小 |
| Cmd+0 | 实际大小 |

## 评估清单

在发货 Mac 应用程序之前，请验证：

### 菜单栏
- [ ] 应用程序具有完整的菜单栏，包含标准菜单
- [ ] 所有操作都有键盘快捷键
- [ ] 菜单项动态更新（启用/禁用、标题更改）
- [ ] 所有交互元素都有上下文菜单
- [ ] 应用程序菜单包含“关于”、“设置”、“隐藏”、“退出”

### 窗口
- [ ] 窗口可以自由调整大小，并具有合理的最小尺寸
- [ ] 全屏和分屏视图功能正常
- [ ] 支持多个窗口（如果适用）
- [ ] 窗口位置和大小在启动之间保持不变
- [ ] 交通灯按钮可见且功能正常
- [ ] 显示文档标题和编辑状态（如果基于文档）

### 工具栏
- [ ] 工具栏包含常用操作
- [ ] 工具栏是用户可自定义的
- [ ] 工具栏中提供搜索框

### 侧边栏
- [ ] 导航侧边栏（如果应用程序具有多个部分）
- [ ] 侧边栏可折叠
- [ ] 带有活力的源列表样式

### 键盘
- [ ] 完整的键盘导航（Tab、箭头、Enter、Esc）
- [ ] Cmd+Z 撤销所有破坏性操作
- [ ] 空格键用于快速预览
- [ ] 删除键删除选定项
- [ ] 无键盘陷阱（用户始终可以 Tab 退出）

### 指针
- [ ] 交互元素上的悬停状态
- [ ] 所有地方都有右键上下文菜单
- [ ] 拖放用于内容操作
- [ ] Cmd+点击用于多选
- [ ] 适当的鼠标指针变化

### 通知
- [ ] 仅对重要事件进行通知
- [ ] 警报对重复事件具有抑制选项
- [ ] 常规操作不使用模态警报

### 系统集成
- [ ] 高质量的 Dock 图标
- [ ] 内容在 Spotlight 中索引（如果适用）
- [ ] 分享菜单功能正常
- [ ] 应用程序意图用于快捷方式

### 视觉设计
- [ ] 语义大小的系统字体
- [ ] 完全支持深色模式
- [ ] 尊重系统强调色
- [ ] 透明度尊重无障碍设置
- [ ] 在 8pt 网格上保持一致的间距

### 弹出窗口
- [ ] 弹出窗口与其源元素对齐，并带有指向它的箭头
- [ ] 按下 Esc 键关闭弹出窗口
- [ ] 弹出窗口根据其内容调整大小，无需不必要的滚动

### 无障碍性
- [ ] 所有仅图标工具栏项和图像按钮都具有无障碍标签
- [ ] 每个鼠标可访问的操作也通过键盘可访问（完整键盘访问）
- [ ] 当启用减少运动时，装饰性动画被禁用
- [ ] 当启用减少透明度时，半透明表面被替换为实心背景
- [ ] VoiceOver 遍历顺序是逻辑的（从左上到右下）
- [ ] 尊重粗体文本偏好（SwiftUI 自动处理；AppKit 检查 `accessibilityDisplayShouldUseBoldText`）
- [ ] 尊重增加对比度偏好（自定义颜色通过 `colorSchemeContrast` 或 `accessibilityDisplayShouldIncreaseContrast` 提供更高对比度的变体）

---

## 反模式

在 Mac 应用程序中不要做这些事情：

1. **没有菜单栏** — 每个 Mac 应用程序都需要菜单栏。毫无疑问。没有菜单的 Mac 应用程序就像没有方向盘的汽车。

2. **汉堡菜单** — 在 Mac 上永远不要使用汉堡菜单。菜单栏为此目的而存在。汉堡菜单表明是懒惰的 iOS 移植。

3. **底部标签栏** — Mac 应用程序使用侧边栏和工具栏，而不是 iOS 风格的标签栏。如果您需要标签，请在标签栏中使用实际的文档标签（如 Safari 或 Finder）。

4. **大尺寸触摸目标** — Mac 控件应紧凑（高度 22-28pt）。用户具有精确的指针输入。巨大的按钮浪费空间且看起来不合适。

5. **浮动操作按钮** — FAB 是 Material Design 模式。在 Mac 上，将主要操作放置在工具栏、菜单栏或作为内联按钮。

6. **每个操作都使用弹窗** — 不要使用模态弹窗进行简单操作。使用弹出窗口、内联编辑或直接操作。弹窗应保留用于多步骤工作流程或重要决策。

7. **自定义窗口装饰** — 不要用自定义实现替换标准标题栏、交通灯或窗口控件。用户期望所有应用程序中这些功能的一致性。

8. **忽略键盘** — 如果高级用户必须使用鼠标执行常用操作，则键盘支持不足。

9. **仅单窗口** — 除非您的应用程序确实是单用途的（计算器、计时器），请支持多个窗口。用户期望使用 Cmd+N 新建窗口。

10. **固定窗口大小** — 非可调整大小的窗口在 Mac 上感觉不完整。用户具有从 13 英寸笔记本电脑到 32 英寸外部的显示器，并期望使用这些空间。

11. **没有 Cmd+Z 撤销** — 每个破坏性或修改操作都必须可撤销。用户围绕 Cmd+Z 建立了肌肉记忆，将其作为安全网。

12. **通知泛滥** — 发送过多通知的 Mac 应用程序会吊销其权限。仅对真正需要关注的事件进行通知。

13. **忽略深色模式** — 在深色模式下看起来不正确的 Mac 应用程序显得被遗弃。始终测试两种外观。

14. **硬编码颜色** — 使用语义系统颜色，而不是硬编码的十六进制值。您的颜色应自动适应亮/暗模式和无障碍设置。

15. **没有拖放** — Mac 是一个拖放平台。如果用户可以看到内容，他们期望将其拖到某个地方。
