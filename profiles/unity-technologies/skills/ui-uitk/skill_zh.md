理解现有的 Unity UI Toolkit 代码，进行有针对性的修改，生成新的 UXML/USS 文件、Manipulators，并处理 UI 运行时绑定。

## 参考

按需阅读以下内容：
- `references/uss-guide.md` — USS 模式和示例
- `references/svg-icons.md` — SVG 图标生成（仅在生成图标时使用）
- `references/common-issues.md` — 常见错误避免方法
- `references/ui-runtime-binding.md` — 绑定数据到 UI 的模式指南（仅在请求或涉及绑定时使用）
- `references/painter2d.md` — Painter2D API 用于自定义视觉效果：渐变、形状、圆弧、程序化绘制（每当需要渐变、自定义形状、进度环、程序化绘制或任何 USS 无法表达的视觉效果时，都需要阅读此内容）
- `references/pointermanipulator-guide.md` — 创建和使用 Manipulators 的模式指南（仅在请求或涉及 Manipulators 时使用）。这有助于设置拖放功能或为 Visual Element 设置简单的事件处理。
- `references/custom-elements.md` — 自定义 UI 元素的模式指南，使用 UXML、USS 和 C# 创建可重用组件。这有助于为项目跨用创建复杂的 UI 组件。

路径相对于此技能的文件夹——直接阅读 `references/uss-guide.md`。

## 理解

在解释 UI 结构时，使用以下格式：
```
[ElementType] name="elementName" class="class1 class2"
├── [ChildType] name="childName"
│   └── [GrandchildType]
└── [ChildType] class="another-class"
```

## 编辑

**常见的编辑请求：**

| 请求 | 操作 |
|------|------|
| "更改按钮颜色" | 编辑该按钮的 USS 选择器 |
| "在这里添加一个标签" | 在指定位置将元素添加到 UXML |
| "让它变大" | 在 USS 中编辑宽度和高度 |
| "隐藏这个元素" | 在 USS 中添加 `display: none` 或从 UXML 中移除 |
| "重命名这个元素" | 更新 UXML 中的 `name` 属性 |

**不要过度编辑：**
- 仅更改请求的内容
- 保持格式和结构
- 不要"改进"无关代码
- 除非被要求，否则不要添加注释
- 对于有针对性的更改，优先修改特定元素或选择器，而不是重写整个文件——但要根据情况判断；如果更改涉及文件的大部分内容，重写可能更干净
- 在进行编辑时，小心不要意外删除现有的元素、样式或引用
- **当编辑 USS 时**，专注于与请求相关的属性和选择器——避免不必要的重新组织，但如果更改确实需要它，则重新组织

## 验证

没有办法从编辑器外部验证 UXML 或 USS——Unity 在导入时解析这些文件，并在控制台中报告问题。编写文件后，让用户检查结果。

**工作流程：**

1. 将完整文件写入项目中的目标路径。不要写入部分或草稿内容——一个半写的 UXML 文件在编辑器读取它时就会产生解析错误。
2. 要求用户将焦点放在 Unity 编辑器上。这会触发更改的资源的重新导入。
3. 要求他们报告控制台中的任何内容。UXML 解析错误会命名文件和行；USS 问题会显示为未知属性或选择器的警告。
4. 修复他们报告的问题，并重复从步骤 1 开始。

**因为反馈需要用户往返一次，所以第一次就要做对：**

- 在要求用户检查之前完成所有文件，以便一次重新导入涵盖所有内容，而不是每个文件一次。
- 在编写之前重新阅读 `references/uss-guide.md` 和 `references/common-issues.md`，而不是在错误返回后阅读。
- 注意那些在解析后仍然存在但渲染错误的错误——这些根本不会出现在控制台中，因此用户必须通过肉眼检查 UI。`references/common-issues.md` 列出了它们。

## 生成

在创建新的 UI 时：

**仅生成请求的内容：**

| 请求 | 输出 |
|------|------|
| 仅 USS | `.uss` 文件 |
| 仅 UXML | `.uxml` 文件 |
| UI 屏幕 / 菜单 / 面板 | `.uss` + `.uxml` |
| "带代码" / "带逻辑" / "功能" | `.uss` + `.uxml` + `.cs` |

**这些不意味着 C#：**
- "合适的按钮" → 风格良好的 Button 元素
- "货币显示" → Label 元素
- "工作 UI" → 有效的 UXML/USS 且可渲染
- "库存屏幕" → 仅视觉布局
- "库存系统" / "装备系统" / "合成系统" → 询问："玩家应该能够拖放物品吗？" 如果是，请参阅 `references/pointermanipulator-guide.md` 中的库存/合成特定模式

**生成工作流程：**
1. **分析**——确定确切需要哪些文件。不要有额外的文件。
2. **搜索**——查找现有的 USS、UXML、资源。不要假设路径。
3. **遵循项目模式**——匹配文件夹结构和命名约定。
4. **重用**——检查共享样式表。如果合适，请重用。
5. **首先编写 USS**——验证以下限制。
6. **编写 UXML**——引用 USS，验证结构。
7. **完整地编写文件**——不要部分内容；有关错误如何返回以及为什么一轮文件胜过几轮的原因，请参阅验证部分。
8. **场景设置**——如果添加 UI 到场景，请分配 PanelSettings。
9. **数据绑定**——如果请求，请添加具有运行时数据绑定模式的 C# 脚本（请参阅 `references/ui-runtime-binding.md`）。如果需要，生成脚本对象资源。将资源分配给 UXML 中的 UI 元素根或通过 C# 中的数据源分配。

**颜色、可见性和规范规则：**
- **确保文本默认情况下可读**：在选择颜色时，确保文本与其背景对比——但尊重有意使用的低对比度（禁用状态、占位符文本、装饰性元素）。在使用设计令牌时，检查文本和背景变量是否提供足够的对比度。
- **尊重确切值**：用户指定的十六进制颜色、像素尺寸、间距——使用给定的确切值。不要近似或替代。

**样式 / 主题**
在样式化 UI 或调整主题时，确保不仅应用于当前 UXML 中的直接元素，还应用于 UI Toolkit 的核心元素，这些核心元素通常由多个子元素组成。

## 规范

**首先遵循项目模式。** 在应用默认值之前搜索现有文件。

| 类型 | 规范 | 好 | 坏 |
|------|------|------|------|
| `name` 属性 | camelCase | `submitButton` | `submit-button` |
| `class` 属性 / USS | kebab-case | `.submit-button` | `.submitButton` |
| 文件路径 | 功能文件夹 | `Assets/UI/Inventory/` | `Assets/Scripts/UI/` |

**输出格式：**
```uxml Filename.uxml
<ui:UXML>...</ui:UXML>
```
```uss Filename.uss
.class { ... }
```

## USS 限制

Unity 的 USS 是 CSS 的子集。这些属性不存在——永远不要使用它们：

| 永远不要使用 | 使用替代 |
|-------------|----------|
| `border` 简写 | `border-width`、`border-color` 分别使用 |
| `gap` | 子元素的 `margin` |
| `z-index` | DOM 顺序或父级嵌套 |
| `pointer-events` | `picking-mode` UXML 属性 |
| `filter` | 不支持 |
| `outline` | `border-*` 属性 |
| `box-shadow` | 嵌套元素或背景图像 |
| `:first-child`、`:last-child`、`:nth-child` | 显式类 |
| `[attribute]` 选择器 | 显式类 |
| `transition-property: <value>` | 完全省略，或仅 `none`/`initial`/`inherit` |
| `linear-gradient()`、`radial-gradient()` | 使用 Painter2D 创建自定义 `VisualElement`（请参阅 `references/painter2d.md`） |

**内联样式**：永远不要在 UXML 中使用 `style="..."`。所有样式仅在 USS 中。

**外部 URL**：永远不要使用 `url()` 与外部路径。仅 `url("project://database/Assets/...")`。

**优先使用灵活布局而不是硬编码尺寸：**
- 使用 `flex-grow`、`flex-shrink` 或 `%` 而不是固定的 `width`/`height` 值
- 让元素自然流动，并由其父容器约束
- 仅在根容器上或当确实需要固定尺寸时设置明确像素尺寸
- 子元素应适应可用空间，而不是定义自己的尺寸

## USS 简洁性

- 没有默认值（`flex-direction: column` 是默认值）
- 没有默认字体
- 没有冗余约束（`width: 100px` 不需要 `min-width`/`max-width`）
- 没有重叠属性（`flex: 1` 已经设置了 grow/shrink）
- 最简单的能工作的选择器
- 永远不要重复选择器

## UXML

每个文件必须：
1. 声明命名空间：`<ui:UXML xmlns:ui="UnityEngine.UIElements">`
2. 链接样式表：`<ui:Style src="Screen.uss" />`
3. 恰好有一个顶层容器
4. **没有 `style="..."` 属性**——仅使用 USS

```uxml
<ui:UXML xmlns:ui="UnityEngine.UIElements">
  <ui:Style src="Panel.uss" />
  <ui:VisualElement name="root" class="panel">
    <!-- 内容 -->
  </ui:VisualElement>
</ui:UXML>
```

## 事件和交互性
- 使用 Pointer Manipulators 处理 VisualElement 上的事件和交互性（请参阅 `references/pointermanipulator-guide.md`）
- 如果请求拖放，则编写一个 pointer Manipulator 并将其附加到 UXML 中的相关 Visual Element 或通过 C# 附加。
- 对于简单的点击事件，您可以使用 UXML 中的 `clickable` manipulator
- 对于更高级的交互，请在 C# 中创建更传统的回调事件，并根据需要将它们附加到元素上

**对于库存和合成系统：**
- 当用户请求"库存系统"、"装备系统"或"合成系统"时，明确询问："玩家应该能够拖放物品吗？"
- 如果是，请阅读 `references/pointermanipulator-guide.md` 中的库存/合成特定模式
- 如果不是或不明确，请创建静态布局

## 资源

**不要引用 `UnityDefaultRuntimeTheme.tss`** 或 Unity 的内置主题图标。

**图标优先级：**
1. 重用现有项目图标
2. 生成 SVG（请参阅 `references/svg-icons.md`）
3. 图像生成器（最后手段）

**引用格式：**
```uss
background-image: url("project://database/Assets/UI/Textures/icon.png");
```

## 场景设置

**PanelSettings 是必需的**——没有它，UI 将无法渲染。

1. 搜索现有的 PanelSettings 资源
2. 如果没有，创建通用资源：`Assets/UI/PanelSettings.asset`
3. 将其分配给 UIDocument 的 `Panel Settings` 字段

为 Editor UI（EditorWindow、PropertyDrawer）跳过。

## C#（仅当请求时）

- 通过 USS 类 (`AddToClassList()`) 进行样式化——永远不要使用 `element.style.*`，因为内联样式比 USS 选择器具有更高的特异性，使得它们无法通过样式表覆盖，并且为每个元素增加了内存开销
- UITK 使用 TextCore 文本资源——使用 `FontAsset`、`TextStyleSheet` 和 `TextSettings`，而不是它们的 TextMeshPro 对应物（`TMP_FontAsset` 等）
- 将脚本放在与 UXML/USS 相同的文件夹中
