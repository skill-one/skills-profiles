## 何时使用此技能

用于任何引入或更改交互式 UI 的 VS Code 功能工作。默认情况下，在新功能和贡献中使用此技能，即使请求中没有明确提及可访问性。

触发示例：
- "添加新功能"
- "实现新的面板/视图/组件"
- "添加新命令或工作流"
- "工作区/编辑器/扩展中的新贡献"
- "更新现有 UI 交互"

即使提示中没有提及可访问性，也不要跳过此技能。

当向 VS Code 添加**新的交互式 UI 表面**（面板、视图、组件、编辑器覆盖、对话框或任何用户交互的富焦点组件）时，你必须提供三个可访问性组件（如果功能中不存在这些组件）：

1. **可访问性帮助对话框** — 当功能获得焦点时，通过可访问性帮助快捷键打开。
2. **可访问视图** — 一个纯文本只读编辑器，向屏幕阅读器用户展示功能的内容（当功能显示非平凡的视觉内容时）。
3. **可访问性详细程度设置** — 一个布尔设置，控制是否宣布“打开可访问性帮助”提示。

具有所有三个组件的现有功能示例：**终端**、**聊天面板**、**笔记本**、**差异编辑器**、**内联补全**、**评论**、**调试 REPL**、**悬停**和**通知**。仅具有帮助对话框（没有可访问视图）的功能包括**查找组件**、**源代码输入**、**快捷键编辑器**、**问题面板**和**向导**。

第 4-7 节（信号、ARIA 通知、键盘导航、ARIA 标签）更广泛地适用于**任何 UI 更改**，包括现有功能的修改。

当**更新现有功能**时（例如，添加新命令、键盘快捷键或交互功能），你必须更新功能的现有可访问性帮助对话框（`provideContent()`），以记录新功能。屏幕阅读器用户依赖帮助对话框作为发现可用操作的主要方式。

---

## 1. 可访问性帮助对话框

可访问性帮助对话框告诉用户该功能的作用、可用的键盘快捷键以及如何通过屏幕阅读器与之交互。

### 步骤

1. **创建一个实现 `IAccessibleViewImplementation` 的类**，其中 `type = AccessibleViewType.Help`。
   - 设置 `priority`（较高 = 当多个提供者匹配时，首先显示）。
   - 设置 `when` 为一个匹配功能获得焦点时的 `ContextKeyExpression`。
   - `getProvider(accessor)` 返回一个 `AccessibleContentProvider`。

2. **创建一个内容提供者类**，实现 `IAccessibleViewContentProvider`。
   - `id` — 在 `AccessibleViewProviderId` 枚举（位于 `src/vs/platform/accessibility/browser/accessibleView.ts`）中添加一个新条目。
   - `verbositySettingKey` — 引用新的 `AccessibilityVerbositySettingId` 条目（见 §3）。
   - `options` — `{ type: AccessibleViewType.Help }`。
   - `provideContent()` — 返回本地化的多行帮助文本。

3. **实现 `onClose()`** 以将焦点恢复到帮助对话框打开之前所在的元素。这确保了键盘用户和屏幕阅读器用户可以返回到他们之前的环境。

4. **在功能的 `*.contribution.ts` 文件中注册**：
   ```ts
   AccessibleViewRegistry.register(new MyFeatureAccessibilityHelp());
   ```

### 示例骨架

最简单的方法是从 `getProvider()` 直接返回一个 `AccessibleContentProvider`。这是代码库中最常见的模式（例如聊天、内联聊天、快速聊天等）：

```ts
import { AccessibleViewType, AccessibleContentProvider, AccessibleViewProviderId } from '../../../../platform/accessibility/browser/accessibleView.js';
import { IAccessibleViewImplementation } from '../../../../platform/accessibility/browser/accessibleViewRegistry.js';
import { AccessibilityVerbositySettingId } from '../../../../platform/accessibility/common/accessibilityConfiguration.js';

export class MyFeatureAccessibilityHelp implements IAccessibleViewImplementation {
	readonly priority = 100;
	readonly name = 'my-feature';
	readonly type = AccessibleViewType.Help;
	readonly when = MyFeatureContextKeys.isFocused;

	getProvider(accessor: ServicesAccessor) {
		const helpText = [
			localize('myFeature.help.overview', "您在 My Feature 中。…"),
			localize('myFeature.help.key1', "- {0}: 执行某操作", '<keybinding:myFeature.doSomething>'),
		].join('\n');
		return new AccessibleContentProvider(
			AccessibleViewProviderId.MyFeature,
			{ type: AccessibleViewType.Help },
			() => helpText,
			() => { /* onClose — 将焦点恢复到可访问性帮助对话框打开之前的元素 */ },
			AccessibilityVerbositySettingId.MyFeature,
		);
	}
}
```

或者，如果提供者需要注入服务或必须跟踪状态（例如，存储对先前焦点元素的引用），创建一个继承自 `Disposable` 并实现 `IAccessibleViewContentProvider` 的自定义类，然后通过 `IInstantiationService` 实例化它（有关示例，请参阅 `CommentsAccessibilityHelpProvider`）：

```ts
class MyFeatureAccessibilityHelpProvider extends Disposable implements IAccessibleViewContentProvider {
	readonly id = AccessibleViewProviderId.MyFeature;
	readonly verbositySettingKey = AccessibilityVerbositySettingId.MyFeature;
	readonly options: IAccessibleViewOptions = { type: AccessibleViewType.Help };

	provideContent(): string { /* … */ }
	onClose(): void { /* … */ }
}

// 在 getProvider() 中：
getProvider(accessor: ServicesAccessor) {
	return accessor.get(IInstantiationService).createInstance(MyFeatureAccessibilityHelpProvider);
}
```

---

## 2. 可访问视图

可访问视图以纯文本形式在只读编辑器中呈现功能的视觉内容。当功能渲染富或视觉内容时需要它（例如：聊天响应、悬停工具提示、通知、终端输出、内联补全），而屏幕阅读器无法直接读取这些内容。

如果功能是纯键盘驱动的，具有原生文本输入/输出（例如，一个简单的输入字段），则不需要可访问视图 — 只需要一个可访问性帮助对话框即可。

### 步骤

1. **创建一个实现 `IAccessibleViewImplementation` 的类**，其中 `type = AccessibleViewType.View`。
2. **创建一个内容提供者**，类似于帮助对话框，但：
   - `options` — `{ type: AccessibleViewType.View }`，可选地带有 `language` 以进行语法高亮。
   - `provideContent()` — 返回功能的当前内容作为纯文本。
   - 可选地实现 `provideNextContent()` / `providePreviousContent()` 以进行逐项导航。
   - 实现 `onClose()` 以将焦点恢复到可访问视图打开之前的元素。
   - 可选地提供 `actions` 以便用户可以从可访问视图中执行操作。
3. **与帮助对话框一起注册**：
   ```ts
   AccessibleViewRegistry.register(new MyFeatureAccessibleView());
   ```

### 示例骨架

```ts
export class MyFeatureAccessibleView implements IAccessibleViewImplementation {
	readonly priority = 100;
	readonly name = 'my-feature';
	readonly type = AccessibleViewType.View;
	readonly when = MyFeatureContextKeys.isFocused;

	getProvider(accessor: ServicesAccessor) {
		// 获取服务，从功能的当前状态构建内容
		const content = getMyFeatureContent();
		if (!content) {
			return undefined;
		}
		return new AccessibleContentProvider(
			AccessibleViewProviderId.MyFeature,
			{ type: AccessibleViewType.View },
			() => content,
			() => { /* onClose — 将焦点恢复到可访问视图打开之前的元素 */ },
			AccessibilityVerbositySettingId.MyFeature,
		);
	}
}
```

---

## 3. 可访问性详细程度设置

详细程度设置控制当功能获得焦点时是否宣布提示（例如，“按 Alt+F1 获取可访问性帮助”）。已经知道快捷键的用户可以禁用它。

### 步骤

1. **在 `AccessibilityVerbositySettingId` 中添加一个条目** 到 `src/vs/workbench/contrib/accessibility/browser/accessibilityConfiguration.ts`：
   ```ts
   export const enum AccessibilityVerbositySettingId {
       // … 现有条目 …
       MyFeature = 'accessibility.verbosity.myFeature'
   }
   ```

2. **在同一文件的 `configuration.properties` 对象中注册配置属性**：
   ```ts
   [AccessibilityVerbositySettingId.MyFeature]: {
       description: localize('verbosity.myFeature.description',
           '当 My Feature 获得焦点时，提供有关如何访问 My Feature 可访问性帮助菜单的信息。'),
       ...baseVerbosityProperty
   },
   ```
   `baseVerbosityProperty` 为其提供 `type: 'boolean'`、`default: true` 和 `tags: ['accessibility']`。

3. **在帮助对话框提供者和可访问视图提供者中引用设置键**，以便运行时可以检查是否显示提示。

---

## 4. 可访问性信号（声音和通知）

可访问性信号为视觉事件提供声音和语音反馈。使用 `IAccessibilitySignalService` 在重要事件发生时（例如，出现错误、任务完成、内容更改）播放信号。

### 何时使用

- **使用现有信号** 当事件已经有一个定义（见 `AccessibilitySignal.*` 静态成员 — 例如，`AccessibilitySignal.error`、`AccessibilitySignal.terminalQuickFix`、`AccessibilitySignal.clear`）。
- **如果没有现有信号适用**，请联系 @meganrogge 讨论添加新信号。在协调之前不要注册新信号。

### 信号如何工作

每个信号有两个受用户设置控制的模态：
- **声音** — 短音频提示，可配置为 `auto`（屏幕阅读器连接时开启）、`on` 或 `off`。
- **通知** — 通过 `aria-live` 的语音消息，可配置为 `auto` 或 `off`。

### 使用方法

```ts
// 通过构造函数参数注入服务
constructor(
	@IAccessibilitySignalService private readonly _accessibilitySignalService: IAccessibilitySignalService
) { }

// 播放信号
this._accessibilitySignalService.playSignal(AccessibilitySignal.terminalQuickFix);

// 带选项播放
this._accessibilitySignalService.playSignal(AccessibilitySignal.error, { userGesture: true });
```

---

## 5. ARIA 警报与状态消息

使用 `src/vs/base/browser/ui/aria/aria.ts` 中的 `alert()` 和 `status()` 函数向屏幕阅读器宣布动态变化。

### `alert(msg)` — 断言性活区域 (`role="alert"`)
- **用途**：紧急、重要的信息，用户必须立即知道。
- **示例**：错误、警告、关键状态变化、用户发起操作的结果。
- **行为**：中断屏幕阅读器的当前语音。

### `status(msg)` — 礼貌性活区域 (`aria-live="polite"`)
- **用途**：非紧急、信息性更新，应在屏幕阅读器空闲时宣布。
- **示例**：进度更新、搜索结果计数、后台状态变化。
- **行为**：排队并在屏幕阅读器完成当前输出后朗读。

### 指南

- **优先使用 `status()` 而不是 `alert()`** 除非信息是时间敏感的或用户直接操作的结果。过度使用 `alert()` 会导致嘈杂、干扰性体验。
- **保持消息简洁**。屏幕阅读器会朗读整个消息；长消息会延迟用户。
- **不要重复** — 如果可访问性信号已经宣布了事件，不要对相同信息也调用 `alert()` / `status()`。
- **本地化** 所有消息使用 `nls.localize()`。

---

## 6. 键盘导航

每个交互式 UI 元素都必须可以通过键盘完全操作。

### 要求

- **Tab 顺序**：所有交互式元素必须可以通过 `Tab` / `Shift+Tab` 以逻辑顺序访问。
- **箭头键导航**：列表、树、网格和工具栏必须支持遵循 WAI-ARIA 模式的箭头键导航。
- **焦点可见性**：获得焦点的元素必须有一个可见的焦点指示器（VS Code 的主题系统通过 `focusBorder` 提供此功能）。
- **无鼠标交互**：每个可通过点击或悬停访问的操作也必须可以通过键盘访问（上下文菜单、按钮、切换器等）。
- **按 Esc 关闭**：覆盖、对话框和弹出窗口必须可以通过 `Esc` 关闭，并将焦点返回到前一个元素。
- **焦点捕获**：模态对话框必须在关闭之前捕获焦点。

---

## 7. ARIA 标签和角色

所有交互式 UI 元素都必须具有适当的 ARIA 属性，以便屏幕阅读器可以识别和描述它们。

### 要求

- **`aria-label`**：每个没有可见文本的交互式元素（图标按钮、仅图标操作、自定义组件）必须有一个描述性的 `aria-label`。标签应本地化。
- **`aria-labelledby`** / **`aria-describedby`**：使用这些将元素与现有可见文本关联，而不是重复字符串。
- **`role`**：不使用原生 HTML 元素的自定义组件必须声明正确的 ARIA 角色（例如，`role="button"`、`role="tree"`、`role="tablist"`）。
- **`aria-expanded`**、**`aria-selected`**、**`aria-checked`**：切换和选择状态必须通过适当的 ARIA 状态属性传达。
- **`aria-hidden="true"`**：装饰性或冗余元素（文本标签旁边的图标、装饰性分隔符）必须从可访问性树中隐藏。

### 指南

- 避免使用通用标签如“按钮”或“图标” — 描述操作：“关闭面板”、“切换侧边栏”、“运行任务”。
- 使用屏幕阅读器（macOS 上的 VoiceOver、Windows 上的 NVDA）测试，以验证标签在上下文中是否正确朗读。
- 列表和树在虚拟化时应使用 `aria-setsize` 和 `aria-posinset`，以便屏幕阅读器报告正确的计数。

---

## 新功能检查清单

- [ ] 在 `accessibleView.ts` 中添加了新的 `AccessibleViewProviderId` 条目
- [ ] 在 `accessibilityConfiguration.ts` 中添加了新的 `AccessibilityVerbositySettingId` 条目
- [ ] 在同一文件的 `configuration.properties` 对象中注册了详细程度设置，并使用 `...baseVerbosityProperty`
- [ ] 创建了 `IAccessibleViewImplementation`（`type = Help`）并注册
- [ ] 内容提供者引用了正确的 `verbositySettingKey`
- [ ] 帮助文本使用 `nls.localize()` 完全本地化
- [ ] 帮助文本中的快捷键使用 `<keybinding:commandId>` 语法进行动态解析
- [ ] 设置了 `when` 上下文键，以便仅在功能获得焦点时显示对话框
- [ ] 如果功能具有富/视觉内容：创建了 `IAccessibleViewImplementation`（`type = View`）并注册
- [ ] 在功能的 `*.contribution.ts` 文件中进行了注册调用
- [ ] 对于重要事件播放了可访问性信号（使用现有的 `AccessibilitySignal.*` 或注册新的信号）
- [ ] 适当使用 `aria.alert()` 或 `aria.status()` 进行动态变化（优先使用 `status()` 除非紧急）
- [ ] 所有交互式元素都可以通过键盘访问和操作
- [ ] 所有没有可见文本的交互式元素都有一个本地化的 `aria-label`
- [ ] 自定义组件声明了正确的 ARIA `role` 和状态属性
- [ ] 装饰性元素使用 `aria-hidden="true"` 隐藏

## 关键文件

- `src/vs/platform/accessibility/browser/accessibleView.ts` — `AccessibleViewProviderId`、`AccessibleContentProvider`、`IAccessibleViewContentProvider`
- `src/vs/platform/accessibility/browser/accessibleViewRegistry.ts` — `AccessibleViewRegistry`、`IAccessibleViewImplementation`
- `src/vs/workbench/contrib/accessibility/browser/accessibilityConfiguration.ts` — `AccessibilityVerbositySettingId`、详细程度设置注册
- `src/vs/platform/accessibilitySignal/browser/accessibilitySignalService.ts` — `IAccessibilitySignalService`、`AccessibilitySignal`
- `src/vs/base/browser/ui/aria/aria.ts` — `alert()`、`status()` 用于 ARIA 活区域通知
