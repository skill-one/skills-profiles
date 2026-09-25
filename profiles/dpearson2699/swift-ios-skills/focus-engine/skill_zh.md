# Focus Engine

Focus行为适用于目标为iOS 26+、iPadOS、macOS、tvOS和visionOS连接输入路径的SwiftUI和UIKit应用。涵盖键盘焦点、方向焦点、场景焦点值、焦点恢复以及UIKit焦点引导。本技能中的`focusSection()`引导适用于macOS和tvOS。visionOS注视驱动悬停是输入提示，而非焦点。特定于无障碍的焦点（用于VoiceOver和Switch Control）位于`ios-accessibility`技能中。

当请求混合焦点与无障碍性或空间输入时，请保持边界明确：
- 使用此技能处理键盘、遥控器、游戏控制器和场景焦点行为。
- 对于visionOS，将注视、直接触摸和指针定位描述为悬停/输入提示，而非焦点。
- 对于VoiceOver、Switch Control、Voice Control或无障碍元素排序，仅向`ios-accessibility`提供简要交接。

## 内容

- [SwiftUI FocusState](#swiftui-focusstate)
- [默认焦点](#default-focus)
- [焦点值和场景值](#focused-values-and-scene-values)
- [可聚焦交互](#focusable-interactions)
- [焦点区域](#focus-sections)
- [焦点恢复](#focus-restoration)
- [UIKit焦点引导](#uikit-focus-guides)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## SwiftUI FocusState

使用`@FocusState`在场景内读取和写入焦点位置。使用`Bool`表示单个目标，或使用可选的`Hashable`枚举表示多个目标。

```swift
struct LoginView: View {
    enum Field: Hashable { case email, password }

    @State private var email = ""
    @State private var password = ""
    @FocusState private var focusedField: Field?

    var body: some View {
        Form {
            TextField("Email", text: $email)
                .focused($focusedField, equals: .email)

            SecureField("Password", text: $password)
                .focused($focusedField, equals: .password)
        }
        .onAppear { focusedField = .email }
        .onSubmit {
            switch focusedField {
            case .email: focusedField = .password
            case .password, nil: submit()
            }
        }
    }
}
```

将焦点状态保持为拥有焦点控制组件的视图的局部状态。

## 默认焦点

使用`.defaultFocus`设置视图出现时或焦点自动重新分配时的首选初始焦点区域或控件。

```swift
struct SidebarView: View {
    enum Target: Hashable { case library, settings }
    @FocusState private var focusedTarget: Target?

    var body: some View {
        VStack {
            Button("Library") { }
                .focused($focusedTarget, equals: .library)

            Button("Settings") { }
                .focused($focusedTarget, equals: .settings)
        }
        .defaultFocus($focusedTarget, .library)
    }
}
```

每屏或焦点区域最好只有一个清晰的默认目标。

## 焦点值和场景值

使用焦点值暴露当前焦点视图的状态。使用场景焦点值，当命令或场景级UI需要在焦点移动到该场景内时仍能访问该值。

```swift
struct SelectedRecipeKey: FocusedValueKey {
    typealias Value = Binding<Recipe>
}

extension FocusedValues {
    var selectedRecipe: Binding<Recipe>? {
        get { self[SelectedRecipeKey.self] }
        set { self[SelectedRecipeKey.self] = newValue }
    }
}

struct RecipeDetailView: View {
    @Binding var recipe: Recipe

    var body: some View {
        Text(recipe.title)
            .focusedSceneValue(\.selectedRecipe, $recipe)
    }
}
```

使用此模式为需要操作当前场景内容的菜单、命令和工具栏。

## 可聚焦交互

在应参与键盘或方向焦点的自定义SwiftUI视图中使用`.focusable(_:interactions:)`。

```swift
struct SelectableCard: View {
    let title: String
    let action: () -> Void
    @FocusState private var isFocused: Bool

    var body: some View {
        Button(action: action) {
            RoundedRectangle(cornerRadius: 12)
                .fill(isFocused ? Color.accentColor.opacity(0.15) : .clear)
                .overlay { Text(title) }
        }
        .buttonStyle(.plain)
        .focusable(interactions: .activate)
        .focused($isFocused)
    }
}
```

在创建任意手势驱动的可聚焦视图之前，优先使用语义`Button`、`Toggle`、`TextField`和其他系统控件。仅在语义控件无法表达UI时，才使用`.focusable(interactions: .activate)`为自定义按钮式控件添加焦点。为真正需要编辑或多个焦点驱动的行为的视图保留更广泛的交互。

## 焦点区域

在macOS 13+和tvOS 15+上使用`focusSection()`引导方向移动，跨越不均匀布局中的可聚焦子视图。

```swift
struct TVLibraryView: View {
    var body: some View {
        HStack {
            VStack {
                Button("Recent") { }
                Button("Favorites") { }
                Button("Downloaded") { }
            }
            .focusSection()

            VStack {
                Button("Featured") { }
                Button("Top Picks") { }
                Button("Continue Watching") { }
            }
            .focusSection()
        }
    }
}
```

在macOS和tvOS上，当默认的左/右或上/下移动跳过了预期组时，使用焦点区域。

## 焦点恢复

在关闭sheet、popover或临时覆盖层后，返回焦点到一个稳定的触发器或逻辑上的下一个目标。

```swift
struct FiltersView: View {
    @State private var showSheet = false
    @FocusState private var isFilterButtonFocused: Bool

    var body: some View {
        Button("Filters") { showSheet = true }
            .focused($isFilterButtonFocused)
            .sheet(isPresented: $showSheet) {
                FilterEditor()
                    .onDisappear {
                        Task { @MainActor in
                            isFilterButtonFocused = true
                        }
                    }
            }
    }
}
```

在呈现方式可能让用户感到困惑时，有意地恢复焦点。

## UIKit焦点引导

当UIKit或tvOS布局需要在空白区域或尴尬的几何形状中自定义路由时，使用`UIFocusGuide`。

```swift
final class DashboardViewController: UIViewController {
    private let focusGuide = UIFocusGuide()
    @IBOutlet private weak var leadingButton: UIButton!
    @IBOutlet private weak var trailingButton: UIButton!

    override func viewDidLoad() {
        super.viewDidLoad()

        view.addLayoutGuide(focusGuide)
        focusGuide.preferredFocusEnvironments = [trailingButton]

        NSLayoutConstraint.activate([
            focusGuide.leadingAnchor.constraint(equalTo: leadingButton.trailingAnchor),
            focusGuide.trailingAnchor.constraint(equalTo: trailingButton.leadingAnchor),
            focusGuide.topAnchor.constraint(equalTo: leadingButton.topAnchor),
            focusGuide.bottomAnchor.constraint(equalTo: leadingButton.bottomAnchor)
        ])
    }
}
```

`UIFocusGuide`是透明的，不是视图。使用它来重定向焦点，而无需添加装饰性UI。

## 常见错误

1. 在同一心智模型中混合无障碍焦点和键盘或方向焦点。
2. 将`@FocusState`存储在共享模型中，而不是拥有视图。
3. 在同一屏上设置多个竞争的默认焦点目标。
4. 在装饰性视图上使用`.focusable()`。
5. 在关闭sheets、popovers或自定义覆盖层后忘记焦点恢复。
6. 在尝试macOS或tvOS上的`focusSection()`或SwiftUI中的更好布局分组之前，就使用`UIFocusGuide`。
7. 在可能的情况下，使用手势处理程序而不是语义`Button`作为自定义可聚焦控件的 PRIMARY 操作。
8. 将visionOS注视悬停视为焦点；为键盘和游戏控制器等连接输入保留焦点引导。

## 审查清单

- [ ] `@FocusState`属于拥有控件的视图
- [ ] 屏幕需要时，初始焦点目标是明确的
- [ ] 焦点在字段或组之间的移动是确定的
- [ ] 使用`focusedSceneValue`或相关焦点值API，当命令需要当前场景状态时
- [ ] 自定义控件仅在它们真正交互时才加入焦点
- [ ] 在降级到UIKit之前，在macOS或tvOS上使用`focusSection()`处理不均匀的方向布局
- [ ] 临时呈现关闭后，焦点返回到稳定元素
- [ ] `UIFocusGuide`的几何形状和首选目标与预期路线匹配
- [ ] visionOS引导区分连接设备焦点与注视驱动悬停或RealityKit输入目标
- [ ] 无障碍焦点问题在`ios-accessibility`中处理，而不是与键盘方向焦点逻辑混合

## 参考资料

- 详细模式：[references/focus-patterns.md](references/focus-patterns.md)
- 多平台焦点（tvOS、watchOS、visionOS、macOS）：[references/multi-platform-focus.md](references/multi-platform-focus.md)
- 焦点调试和反模式：[references/focus-debugging.md](references/focus-debugging.md)
