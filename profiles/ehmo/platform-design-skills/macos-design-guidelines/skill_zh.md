# macOS Human Interface Guidelines

Mac应用程序服务于期望深度键盘控制、持久菜单栏、可调整大小多窗口布局和紧密系统集成的高级用户。这些指南将Apple的HIG转化为可操作的规则，并附带SwiftUI和AppKit示例。

---

## 1. 菜单栏（关键）

每个Mac应用程序都必须有一个菜单栏。它是命令的主要发现机制。无法找到功能的用户会在菜单栏中查找，而不是其他任何地方。

### 规则1.1 — 提供标准菜单

每个应用程序至少必须包含：**应用程序**、**文件**、**编辑**、**视图**、**窗口**、**帮助**。如果应用程序不是基于文档的，则可以省略文件。在编辑和视图之间或视图和窗口之间添加特定于应用程序的菜单。

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
// AppKit — 逐行构建菜单
let editMenu = NSMenu(title: "编辑")
let undoItem = NSMenuItem(title: "撤销", action: #selector(UndoManager.undo), keyEquivalent: "z")
let redoItem = NSMenuItem(title: "重做", action: #selector(UndoManager.redo), keyEquivalent: "Z")
editMenu.addItem(undoItem)
editMenu.addItem(redoItem)
editMenu.addItem(.separator())
```

### 规则1.2 — 所有菜单项都有键盘快捷键

执行操作的每个菜单项都必须有键盘快捷键。使用标准快捷键执行标准操作（Cmd+C、Cmd+V、Cmd+Z等）。自定义快捷键应使用Cmd加一个字母。保留Cmd+Shift、Cmd+Option和Cmd+Ctrl组合键用于次要操作。

**标准快捷键参考:**

| 操作 | 快捷键 |
|------|--------|
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
| 查找 | Cmd+F |
| 查找下一个 | Cmd+G |
| 偏好设置 | Cmd+, |
| 隐藏应用程序 | Cmd+H |
| 退出 | Cmd+Q |
| 最小化 | Cmd+M |
| 全屏 | Cmd+Ctrl+F |

### 规则1.3 — 动态菜单更新

菜单项必须反映当前状态。禁用不适用的项。更新标题以匹配上下文（例如，“撤销输入”而不是“撤销”）。切换复选标记以表示开/关状态。

```swift
// SwiftUI — 在现有工具栏菜单命令旁边添加侧边栏切换
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
        menuItem.title = selectedItems.count > 1 ? "删除 \(selectedItems.count) 个项目" : "删除"
        return !selectedItems.isEmpty
    }
    return super.validateMenuItem(menuItem)
}
```

### 规则1.4 — 上下文菜单

在所有交互元素上提供右键单击上下文菜单。上下文菜单应包含与单击元素最相关的菜单栏操作子集，以及特定于元素的操作。

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

### 规则1.5 — 应用程序菜单结构

应用程序菜单（最左侧，粗体应用程序名称）必须包含：关于、偏好设置/设置（Cmd+）、服务子菜单、隐藏应用程序（Cmd+H）、隐藏其他（Cmd+Option+H）、显示全部、退出（Cmd+Q）。永远不要重命名或删除这些标准项。

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

### 规则1.6 — 稳定的命令名称和位置

将菜单栏视为应用程序的命令内存。将常用操作保留在具有稳定名称和快捷键的菜单中，以便用户可以快速识别它们，而不是搜索特定于上下文的变体。

---

## 2. 窗口（关键）

Mac用户期望对窗口大小、位置和生命周期有完全的控制。与窗口管理作斗争的应用程序在Mac上感觉根本上是损坏的。

### 规则2.1 — 可调整大小，具有合理的最小值

所有主窗口必须可以自由调整大小。设置一个最小尺寸，以保持UI可用。永远不要设置最大尺寸，除非内容确实无法缩放（很少）。

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

### 规则2.2 — 支持全屏和分屏视图

通过设置适当的风窗集行为来选择原生全屏。绿色交通灯按钮必须要么进入全屏，要么显示磁贴选择器。

```swift
// AppKit
window.collectionBehavior.insert(.fullScreenPrimary)
```

SwiftUI窗口自动获得全屏支持。

### 规则2.3 — 多个窗口

除非您的应用程序是单一用途的工具，请支持多个窗口。基于文档的应用程序必须允许同时打开多个文档。使用`WindowGroup`或`DocumentGroup`在SwiftUI中。

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

### 规则2.4 — 标题栏显示文档信息

对于基于文档的应用程序，标题栏必须显示文档名称。支持代理图标拖动。显示编辑状态（关闭按钮中的点）。支持单击标题栏重命名。

```swift
// AppKit
window.representedURL = document.fileURL
window.title = document.displayName
window.isDocumentEdited = document.hasUnsavedChanges
```

```swift
// SwiftUI — 导航分割视图标题
NavigationSplitView {
    SidebarView()
} detail: {
    DetailView()
        .navigationTitle(document.name)
}
```

### 规则2.5 — 记住窗口状态

跨启动持久化窗口位置、大小和状态。使用`NSWindow.setFrameAutosaveName`或SwiftUI的内置状态恢复。

```swift
// AppKit
window.setFrameAutosaveName("MainWindow")

// SwiftUI — 自动通过WindowGroup
WindowGroup(id: "main") {
    ContentView()
}
.defaultPosition(.center)
```

### 规则2.6 — 交通灯按钮

永远不要隐藏或重新定位关闭（红色）、最小化（黄色）或缩放（绿色）按钮。它们必须保留在左上角。如果使用自定义标题栏，则按钮必须仍然可见且功能正常。

```swift
// AppKit — 自定义标题栏保留交通灯
window.titlebarAppearsTransparent = true
window.styleMask.insert(.fullSizeContentView)
// 交通灯仍然功能正常且可见
```

---

## 3. 工具栏（高）

工具栏是菜单栏之后的次要命令表面。它们提供对频繁操作的快速访问，并且应该是可定制的。

### 规则3.1 — 统一标题栏和工具栏

使用统一标题栏+工具栏样式以获得现代外观。工具栏位于标题栏区域，节省垂直空间。

```swift
// SwiftUI
WindowGroup {
    ContentView()
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button(action: compose) {
                    Label("撰写", systemImage: "square.and.pencil")
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

### 规则3.2 — 用户可定制的工具栏

允许用户添加、删除和重新排列工具栏项。提供默认集和可用项的超集。

```swift
// SwiftUI — 可定制的工具栏
.toolbar(id: "main") {
    ToolbarItem(id: "compose", placement: .primaryAction) {
        Button(action: compose) {
            Label("撰写", systemImage: "square.and.pencil")
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

### 规则3.3 — 用于视图切换的分段控件

在工具栏中使用分段控件或选择器来切换内容视图（例如，列表/网格/列）。这是一个工具栏模式，而不是标签栏。

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

### 规则3.4 — 工具栏中的搜索字段

将搜索字段放置在工具栏的 trailing 区域。在SwiftUI中使用`.searchable()`以获得标准搜索行为，带有建议和标记。

```swift
// SwiftUI
NavigationSplitView {
    SidebarView()
} detail: {
    ContentListView()
        .searchable(text: $searchText, placement: .toolbar, prompt: "搜索项目")
        .searchSuggestions {
            ForEach(suggestions) { suggestion in
                Text(suggestion.title).searchCompletion(suggestion.title)
            }
        }
}
```

### 规则3.5 — 工具栏标签和图标

工具栏项应同时具有一个图标（SF Symbol）和一个文本标签。在紧凑模式下，仅显示图标。优先使用带标签的图标以提高可发现性。使用`Label`提供两者。

---

## 4. 侧边栏（高）

侧边栏是Mac应用程序的主要导航表面。它们出现在主导边缘，并提供对顶级部分和内容库的持久访问。

### 规则4.1 — 主导边缘，可折叠

将侧边栏放置在左侧（主导）。通过工具栏按钮或键盘快捷键使其可折叠。Apple没有定义通用的侧边栏快捷键——选择适合您应用程序的快捷键（例如，Cmd+Ctrl+S很常见，但并不保证在所有应用程序中都是免费的）。保留折叠状态。

```swift
// SwiftUI
NavigationSplitView(columnVisibility: $columnVisibility) {
    List(selection: $selection) {
        Section("库") {
            Label("所有项目", systemImage: "tray.full")
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

### 规则4.2 — 源列表样式

使用源列表样式（`.listStyle(.sidebar)`）进行内容库导航。源列表具有半透明背景，可以看到它们后面的桌面或窗口，并带有活力效果。

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

### 规则4.3 — 用于层次结构的轮廓视图

当内容是层次结构时（例如，文件夹树、项目结构），使用 disclosure 组或轮廓视图让用户可以展开和折叠级别。

```swift
// SwiftUI — 递归轮廓
List(selection: $selection) {
    OutlineGroup(rootNodes, children: \.children) { node in
        Label(node.name, systemImage: node.icon)
    }
}
```

### 规则4.4 — 拖动以重新排序

可以重新排序的侧边栏项（书签、收藏、自定义部分）必须支持拖动以重新排序。实现`onMove`或`NSOutlineView`拖动代理。

```swift
// SwiftUI
ForEach(favorites) { item in
    Label(item.name, systemImage: item.icon)
}
.onMove { source, destination in
    favorites.move(fromOffsets: source, toOffset: destination)
}
```

### 规则4.5 — 徽章计数

在侧边栏项上显示徽章计数，用于未读计数、待处理项目或通知。使用`.badge()`修饰符。

```swift
// SwiftUI
Label("收件箱", systemImage: "tray")
    .badge(unreadCount)
```

---

## 5. 键盘（关键）

Mac用户比任何其他平台都更依赖键盘快捷键。没有全面键盘支持的应用程序是一个损坏的Mac应用程序。

### 规则5.1 — Cmd快捷键用于所有操作

通过鼠标可执行的每个操作都必须有一个键盘等效项。主要操作使用Cmd+字母。次要操作使用Cmd+Shift或Cmd+Option。三级操作使用Cmd+Ctrl。

**键盘快捷键约定:**

| 修饰符模式 | 使用 |
|-------------|-------|
| Cmd+字母 | 主要操作（新建、打开、保存等） |
| Cmd+Shift+字母 | 主要操作的变体（另存为、查找上一个） |
| Cmd+Option+字母 | 替代模式（粘贴并匹配样式） |
| Cmd+Ctrl+字母 | 窗口/视图控制（全屏、侧边栏） |
| Ctrl+字母 | Emacs风格的文本导航（可接受） |
| Fn+键 | 系统功能（F11 显示桌面等） |

### 规则5.2 — 全键盘导航

支持Tab在控件之间移动。支持箭头键在列表、网格和表格中导航。支持Shift+Tab进行反向导航。使用`focusable()`和`@FocusState`在SwiftUI中。

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

### 规则5.3 — Escape用于取消或关闭

Esc必须关闭弹出窗口、表单、对话框并取消正在进行操作。在文本字段中，Esc恢复到上一个值。在模态对话框中，Esc相当于单击取消。

```swift
// SwiftUI — 带有Esc支持的表单（自动）
.sheet(isPresented: $showingSheet) {
    SheetView()  // Esc自动关闭
}

// AppKit — 自定义响应者
override func cancelOperation(_ sender: Any?) {
    dismiss(nil)
}
```

### 规则5.4 — Return用于默认操作

在对话框和表单中，Return/Enter激活默认按钮（在蓝色中视觉强调）。默认按钮始终是最安全的默认操作。

```swift
// SwiftUI
Button("保存") { save() }
    .keyboardShortcut(.defaultAction)  // Enter键

Button("取消") { cancel() }
    .keyboardShortcut(.cancelAction)   // Esc键
```

### 规则5.5 — Delete用于删除

Delete键（Backspace）必须删除列表、表格和集合中的选定项目。Cmd+Delete用于更破坏性的删除（移至废纸篓）。始终支持Cmd+Z撤消删除。

### 规则5.6 — Space用于快速预览

当项目支持预览时，Space键应调用快速预览。使用AppKit中的`QLPreviewPanel` API或SwiftUI中的`.quickLookPreview()`。

```swift
// SwiftUI
List(selection: $selection) {
    ForEach(files) { file in
        FileRow(file: file)
    }
}
.quickLookPreview($quickLookItem, in: files)
```

### 规则5.7 — 箭头键导航

在列表和网格中，上/下箭头键移动选择。左/右折叠/展开 disclosure 组或导航列。Cmd+上键转到开头，Cmd+下键转到末尾。

---

## 6. 指针和鼠标（高）

Mac是一个指针驱动的平台。每个交互元素都必须响应悬停、单击、右键单击和拖动。

### 规则6.1 — 悬停状态

所有交互元素都必须有一个可见的悬停状态。按钮高亮显示，行显示选择指示器，链接更改光标。使用`.onHover`在SwiftUI中。

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

### 规则6.2 — 右键单击上下文菜单

每个交互元素都必须响应右键单击以显示上下文菜单。上下文菜单应包含与单击元素最相关的菜单栏操作子集，以及特定于元素的操
