---
name: expo-design-system
description: 框架（开源组件库）。在Expo应用内部构建和维护设计系统——一个可复用的设计令牌主题（颜色、间距、排版、圆角、阴影、动效），具有变体/尺寸/状态属性约定的可复用组件结构，以及何时将重复视图提取为共享组件的规则。适用于创建或组织主题文件和设计令牌（theme.ts / theme/），以自身方式扩展现有主题或样式库（NativeWind、Tamagui、Restyle、Unistyles），标准化样式以确保屏幕（包括AI生成的）看起来一致且精致，修复看起来像AI生成或通用的应用而非原生（native-slop命名提示），构建应用内组件库，或审计应用的设计系统漂移（硬编码颜色、间距、字体）。平台样式特定需求（语义颜色、HIG规则、原生控件）请使用expo-native-ui；新应用文件夹布局请使用expo-project-structure。
---

# Expo 设计系统

让应用中的每个屏幕都从单一的视觉真相中汲取：一个 token 主题和一组可重用的组件。这项技能定义了 token 的存放位置、覆盖范围、可重用组件的形状，以及何时一个重复的视图会晋升到系统中。

这项技能周围的层级由其他兄弟技能拥有：

- `expo-native-ui` - 平台样式规则（HIG、语义颜色、控件、阴影语法）。遵循它以获得**原生外观的值**；遵循这项技能以获得**值的存放位置和重用方式**。
- `expo-project-structure` - 新应用的文件夹骨架。

对于 Tailwind 项目，将 token 保存在 `global.css` 中作为 CSS 变量，并遵循样式库自己的设置指南。这个技能中的尺度和命名仍然适用；只有存储格式会改变。

## 参考

根据需要查阅这些资源：

```
references/
  audit.md        审计现有应用的设计系统漂移：grep 检查、评分标准、增量采用计划以及用于记录或扩展组件的模板
  native-slop.md  20 个命名反模式讲述了 AI 生成的应用（Web 模态、所有东西都是卡片等），对可 grep 的部分进行了 grep 检查
```

## 在构建之前采用

在一个已经拥有屏幕的应用中，第一步是检测，而不是构建。在编写任何 token 文件之前：

1. **寻找已声明的系统。** 检查 `package.json` 中的样式库 - NativeWind/Tailwind、Tamagui、Restyle、Unistyles、styled-components。然后寻找 token 文件：`theme.ts`、`src/theme/`、`constants/theme.ts` 或 `constants/Colors.ts`（create-expo-app 的默认值）。
2. **如果存在，它就是真相来源。** 用它自己的语言扩展它 - 它的名称、它的尺度、它的存储格式。根据该系统进行漂移审计，而不是根据下面的示例。
3. **如果只有实际存在的值** - 屏幕之间重复的相同灰色和填充、没有主题文件 - 那么还没有系统。这些值是尺度的输入，不是权威：从最频繁的值中派生 token，并 snapped 到 4 点网格（`references/audit.md` §5）。
4. **永远不要在现有的系统旁边引入第二个系统。** 旁边一个 Tamagui 配置的新 `src/theme/` 是设计系统漂移，不是采用。

只有在什么都没有的情况下，以下默认值才适用。

## 主题

在一个没有现有系统的应用中，所有设计 token 都位于 `src/theme/`。在一个没有 `src/` 文件夹的项目中（默认的 `create-expo-app` 模板在根目录有 `app/`、`components/` 和 `constants/`），使用等效的顶层位置 - 通常 `theme/` 或现有的 `constants/` - 并保持相同的文件布局。从小开始，并随着增长按 token 类别进行拆分：

```
src/theme/
  colors.ts       # 参考expo-native-ui "Colors"获取调色板模式
  spacing.ts
  typography.ts
  radius.ts
  shadows.ts
  motion.ts
  index.ts        # 重新导出所有内容：import { spacing, type } from "@/theme"
```

一个全新的应用可以从一个包含所有以下对象的 `src/theme.ts` 开始，然后在任何一个类别需要自己的文件时将其提升到文件夹形式（与组件的提升规则相同）。无论哪种方式，都**只有一个**主题入口点 - 永远不要有两个竞争的 token 文件。

使主题值得拥有的规则：

- **每个重复的视觉值都是 token。** 出现两次的字面量应该放在主题中。
- **组件导入 token；屏幕导入组件。** 一个导入 `spacing` 进行布局填充的屏幕文件是没问题的；一个重新定义按钮颜色的屏幕文件是漂移。
- **永远不要在 `src/theme/` 外部硬编码** 十六进制颜色、字体大小或间距倍数。真正本地的一时性值（一个图标的 17px 光学微调）可以保留为内联 - 并附上解释原因的注释。

### 颜色

从平台语义颜色构建调色板：`Color` 从 `expo-router` 包装在 `Platform.select` 中，集中存储在 `theme/colors.ts`。语义颜色在设备上解析并自动适应亮/暗模式 - 优先用于背景、标签和分隔符。（`expo-native-ui` "Colors" 涵盖了完整的调色板和原理；最小版本是：)

```tsx
// theme/colors.ts
import { Platform } from "react-native";
import { Color } from "expo-router";

export const colors = {
  label: Platform.select({
    ios: Color.ios.label,
    android: Color.android.dynamic.onSurface,
    default: "#000000",
  })!,
  secondaryLabel: Platform.select({
    ios: Color.ios.secondaryLabel,
    android: Color.android.dynamic.onSurfaceVariant,
    default: "#3c3c43",
  })!,
  separator: Platform.select({
    ios: Color.ios.separator,
    android: Color.android.dynamic.outlineVariant,
    default: "#c6c6c8",
  })!,
  systemBackground: Platform.select({
    ios: Color.ios.systemBackground,
    android: Color.android.dynamic.surface,
    default: "#ffffff",
  })!,
  systemBlue: Platform.select({
    ios: Color.ios.systemBlue,
    android: Color.android.dynamic.primary,
    default: "#007aff",
  })!,
  // 故意固定：在着色（强调）表面上文本保持白色。
  onTint: "#ffffff",
};
```

当品牌需要平台不提供的值时，才添加品牌颜色作为显式的亮/暗对：

```tsx
// theme/colors.ts (品牌添加)
import { useColorScheme } from "react-native";

const brandPalette = {
  light: { accent: "#5B21B6", accentContrast: "#FFFFFF" },
  dark: { accent: "#A78BFA", accentContrast: "#1E1B4B" },
} as const;

export function useBrandColors() {
  const scheme = useColorScheme();
  return brandPalette[scheme === "dark" ? "dark" : "light"];
}
```

保持品牌集很小（强调、强调对比，每个功能可能有一个着色）。其他所有内容都保持语义。

**静态安全与钩子。** 上述两种模式具有不同的覆盖范围 - 保持边界明确：

- 语义/平台颜色（上面的 `colors`）是**静态安全的**：它们在设备上解析，因此像 `theme/typography.ts` 这样的普通 token 文件可以在模块作用域导入它们。
- 品牌亮/暗对是**钩子式的**：`useBrandColors()` 在渲染时读取颜色方案，因此品牌颜色只能应用于组件内部。静态 token 文件不能调用钩子。
- 永远不要在一个文件中混合这两种模式。如果一个静态样式（一个 `type` 斜坡步骤、一个 `variants` 对象）需要品牌强调色，要么在组件中渲染时应用品牌颜色，要么将这对包装在静态动态颜色（iOS 上的 `DynamicColorIOS`）中，使其变为静态安全的。

### 间距

一个尺度，基于 4 点网格。按大小命名步骤，而不是按用途：

```tsx
// theme/spacing.ts
export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;
```

- 使用 `gap` 与间距 token 进行布局节奏（`expo-native-ui` 更喜欢 `gap` 而不是 `margin`）。
- 屏幕边缘填充是 `spacing.md`，除非设计另有说明 - 挑选一个并保持一致。
- 如果布局需要步骤之间的值，使用最近的步骤。网格就是要点。
- 如果在多个步骤之间相同的 4 的倍数重复出现（12 和 20 是常见的），将其作为命名步骤添加到尺度中，而不是分散字面量。然后，审计白名单也必须包含它。

### 字体

定义命名文本样式，而不是原始字体大小。镜像平台斜坡（Apple 文本样式），以便大小感觉原生：

```tsx
// theme/typography.ts
import { TextStyle } from "react-native";
import { colors } from "./colors";

export const type = {
  largeTitle: { fontSize: 34, fontWeight: "700", color: colors.label },
  title: { fontSize: 22, fontWeight: "600", color: colors.label },
  headline: { fontSize: 17, fontWeight: "600", color: colors.label },
  body: { fontSize: 17, fontWeight: "400", color: colors.label },
  subhead: { fontSize: 15, fontWeight: "400", color: colors.secondaryLabel },
  caption: { fontSize: 12, fontWeight: "400", color: colors.secondaryLabel },
} as const satisfies Record<string, TextStyle>;
```

如果项目捆绑静态字体文件（每个权重一个文件，使用 `expo-font` 或配置插件加载），则通过 `fontFamily` 名称设置权重，而不是省略 `fontWeight` - 否则 iOS 合成权重或回退到系统字体：

```tsx
headline: { fontSize: 17, fontFamily: "SFProRounded-Semibold", color: colors.label },
```

通过一个组件暴露它们，以便屏幕永远不会接触 `fontSize`：

```tsx
// components/themed-text.tsx
import { Text, TextProps } from "react-native";
import { type } from "@/theme";

export function ThemedText({
  variant = "body",
  style,
  ...props
}: TextProps & { variant?: keyof typeof type }) {
  return <Text style={[type[variant], style]} {...props} />;
}
```

屏幕标题仍然来自导航堆栈标题（`expo-native-ui` 规则），因此 `largeTitle` 主要用于非堆栈上下文。

**动态类型。** 文本随用户的系统文本大小设置缩放（`allowFontScaling` 默认为开启）。使用填充或 `minHeight` 围绕文本，以便行可以增长，并检查大可访问性文本大小。在考虑对受限的 chrome 应用元素使用每个元素的 `maxFontSizeMultiplier` 之前，让标签换行或重新流式化。永远不要用 `allowFontScaling={false}` 全局禁用缩放。

### 半径

```tsx
// theme/radius.ts
export const radius = {
  sm: 8,
  md: 12,
  lg: 16,
  full: 9999, // 胶囊
} as const;
```

将每个非胶囊半径与 `borderCurve: "continuous"` 配对（根据 `expo-native-ui`）。

### 阴影

阴影是 `boxShadow` 字符串（永远不要使用遗留阴影/提升属性 - 参考 `expo-native-ui`）。两个或三个提升级别就足够了：

```tsx
// theme/shadows.ts
export const shadows = {
  card: "0 1px 2px rgba(0, 0, 0, 0.05)",
  raised: "0 4px 12px rgba(0, 0, 0, 0.10)",
  overlay: "0 8px 24px rgba(0, 0, 0, 0.18)",
} as const;
```

### 动态

动画速度和共享的弹簧/缓动配置，以便应用中的动画感觉相关：

```tsx
// theme/motion.ts
export const motion = {
  fast: 150, // 状态反馈：按下、切换
  base: 250, // 元素过渡：进入/退出
  slow: 400, // 大表面：表单、屏幕
} as const;
```

Reanimated 注意事项：不要将 `Color`/`PlatformColor` token 值传递到 Reanimated 样式中 - 在那里使用静态颜色（参考 `expo-native-ui`）。

## 可重用组件

主题控制值；组件控制结构。共享原语位于 `src/components/`（参考 `expo-project-structure`）。

### 组件契约

每个设计系统原语明确定义：

- **变体** - 视觉意图：`primary`、`secondary`、`ghost`、`destructive`。只有在真实屏幕需要时才添加变体。
- **尺寸** - `sm`、`md`、`lg`。默认 `md`。尺寸映射到间距/字体样式 token，永远不会映射到新的数字。
- **状态** - 默认、**按下**（不是悬停 - 这是触摸）、禁用、加载。使用 `Pressable` 样式函数处理按下；永远不要在没有按下反馈的情况下留下可点击元素。
- **样式覆盖** - 接受一个 `style` 属性并**最后**合并它，以便调用者可以调整布局（边距、flex）。调用者可以覆盖布局，而不是身份 - 调用者改变按钮颜色是一个信号，表明变体集缺少某些内容。
- **可访问性** - 自定义交互原语将其角色和禁用/忙碌/选中状态作为适用内容公开。文本子元素可以提供标签；仅图标的控件和用旋转器替换文本的按钮需要一个明确的标签，该标签在加载时仍然可用。也验证原生控件的标签。

```tsx
// components/button.tsx
import { Pressable, ActivityIndicator, StyleProp } from "react-native";
import { colors, spacing, radius } from "@/theme";
import { ThemedText } from "./themed-text";

const variants = {
  primary: { backgroundColor: colors.systemBlue, color: colors.onTint },
  secondary: { backgroundColor: colors.separator, color: colors.label },
} as const;

const sizes = {
  sm: { paddingVertical: spacing.xs, paddingHorizontal: spacing.sm },
  md: { paddingVertical: spacing.sm, paddingHorizontal: spacing.md },
} as const;

export function Button({
  variant = "primary",
  size = "md",
  title,
  loading,
  disabled,
  style,
  onPress,
}: {
  variant?: keyof typeof variants;
  size?: keyof typeof sizes;
  title: string;
  loading?: boolean;
  disabled?: boolean;
  style?: StyleProp<ViewStyle>;
  onPress?: () => void;
}) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={title}
      accessibilityState={{ disabled: !!(disabled || loading), busy: !!loading }}
      disabled={disabled || loading}
      onPress={onPress}
      style={({ pressed }) => [
        {
          backgroundColor: variants[variant].backgroundColor,
          borderRadius: radius.md,
          borderCurve: "continuous",
          alignItems: "center",
          opacity: disabled ? 0.4 : pressed ? 0.7 : 1,
          ...sizes[size],
        },
        style, // 调用者覆盖合并到最后
      ]}
    >
      {loading ? (
        <ActivityIndicator color={variants[variant].color as string} />
      ) : (
        <ThemedText variant="headline" style={{ color: variants[variant].color }}>
          {title}
        </ThemedText>
      )}
    </Pressable>
  );
}
```

### 组合优于配置

当一个组件的属性开始描述*内容*（`leftIcon`、`subtitle`、`footerText`、`badgeCount`）时，停止添加属性并接受 `children` 而不是。一个渲染 `children` 并使用 token 填充的 `Card` 比具有十二个内容属性的 `Card` 更持久。为上述契约保留属性：变体、尺寸、状态、样式。

### 何时提取 - 以及何时不提取

当**所有**以下条件都满足时，将视图提取到 `src/components/`：

1. 它出现在（或即将出现）在**两个或更多屏幕**中。在此之前，它保持在 `screens/<name>/` 中（参考 `expo-project-structure`）。
2. 它有一个**可命名的角色**（“Card”、“EmptyState”、“Badge”） - 不是“个人资料屏幕上的东西”。
3. 它的 API 比**实现**更小。如果属性只是重新暴露每个内部样式，那么它还不是可重用组件 - 它是屏幕片段。

提升路径：内联 JSX → `screens/<name>/` 中的组件 → `src/components/`。一步一步移动，当触发器响起时 - 永远不要推测。错误的抽象比重复更贵；视图的第二个副本比具有不良 API 的原语更便宜。

**不要**包装已经携带设计语言的平台组件（`Switch`、`DateTimePicker`、堆栈标题、`@expo/ui` 视图），只是为了通过系统进行路由。原生样式就是这些组件的设计系统。

## 决策存放位置

| 决策 | 存放在 | 示例 |
|---|---|---|
| 任何地方重复使用的视觉值 | `src/theme/` | 品牌强调色、间距步骤 |
| 重用元素的 结构 + 变体 | `src/components/` | Button、Card、EmptyState |
| 一个屏幕的私有组合 | `screens/<name>/` | 个人资料标题布局 |
| 一时性本地调整 | 内联，带注释 | 图标上的光学微调 |
| 屏幕标题、顶层 chrome | 导航堆栈选项 | 标题、大标题 |

## 自我批评通过

在构建或更改屏幕后，截图并对照这些原则（来自 [Expo 的设计原则指南](https://expo.dev/blog/how-to-apply-professional-design-principles-in-ai-app-development)）。每个原则都映射到一个系统修复，而不是本地调整：

- **层次结构 / 对比** - 最重要元素是否明显首先？用 `type` 斜坡步骤修复，而不是临时的字体大小。
- **邻近 / 白色空间** - 相关项目是否比不相关的项目更近？用 `gap` + 间距 token 修复。
- **重复 / 统一** - 所有角落、阴影和强调色是否匹配？如果不匹配，一个值从主题中逃脱了 - 将其移入。
- **对齐** - 边缘是否共享轴？用一致的屏幕边缘填充修复。

在修复值之后重新检查渲染结果；将其移入主题本身并不能修复布局。如果相同的缺陷在多个屏幕上重复出现，请修复共享的令牌或组件。同时，在 `expo-native-ui` 的行为部分运行主要任务和内容检查；仅凭截图无法验证交互。

## 命名失败：原生滑稽

在构建和审查时，使用这些名称来识别常见错误：

- **网页模态框** - 用于编辑或选择的自定义居中对话框。优先使用原生表单 (`formSheet`, `@expo/ui` BottomSheet) 或菜单；原生确认警报仍然适用于有后果的操作。
- **所有都是卡片** - 每行和每个部分都在自己的白色圆角阴影框内。使用分组列表；使用背景和发丝线进行分组，而不是边框。
- **表情图标** - 🔥 ⚙️ ✨ 作为标签或按钮图标。iOS 上使用 SF Symbols，Android 上使用 Material 图标。
- **紫色渐变英雄** - 推动任务在折叠线以下的装饰性渐变介绍。以有用内容引导任务屏幕；当英雄符合请求体验时保留它。
- **旋转器闪烁** - 每个状态之间全屏旋转器，或在首次加载期间闪烁“尚无项目”。每个屏幕都有四个状态（参见 `expo-data-fetching`）。

将视觉提示视为审查提示，而不是对卡片、字体或品牌的全面禁止。修复可观察的问题，并尊重用户的要求和现有的设计系统。完整的 20 项列表和候选 grep 检查在 `./references/native-slop.md` 中；在审查屏幕时，使用它们来解释问题和替代方案。

## 审计现有应用

要衡量已有屏幕的应用中的漂移情况——硬编码的十六进制值、任意间距、不一致的组件 API——请遵循 `./references/audit.md`。它包含基于 grep 的检查、评分标准、修复漂移应用的逐步采用顺序，以及记录现有组件和提议新组件的模板。

## 提交反馈
如果您在本技能中遇到错误、误导性或过时的信息，请报告它，以便 Expo 可以改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "expo-design-system" "<可操作的反馈>"
```
仅在您有具体且可操作的内容要报告时才提交。尽可能包含尽可能多的相关上下文。
如果 AI 代理反复失败或用户不得不接管 Expo 任务，请加载 `expo-skill-feedback` 技能并遵循其 eval-candidate 流程，而不是重复使用上述命令。
