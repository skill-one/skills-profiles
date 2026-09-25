# Expo Router 导航

Expo Router 应用的导航和路由。屏幕样式、颜色、控件、媒体和视觉效果方面，请使用 `expo-native-ui` 技能；运动和手势方面，请使用 `expo-animation`。

## 参考

根据需要查阅以下资源：

```
references/
  route-structure.md     路由约定、动态路由、分组、文件夹组织
  tabs.md                NativeTabs、从 JS tabs 迁移、iOS 26 功能
  toolbar-and-headers.md 栈式标题栏和工具栏按钮、菜单、搜索（仅限 iOS）
  form-sheet.md          expo-router 中的表单面板：配置、页脚和背景交互。
  search.md              带标题栏的搜索栏、useSearch 钩子、过滤模式
  zoom-transitions.md    Apple Zoom：使用 Link.AppleZoom 的流畅缩放过渡（iOS 18+）
```

## 代码风格

- 文件名始终使用连字符命名法，例如 `comment-card.tsx`
- 移动或重构导航时，始终删除旧的路线文件
- 文件名中不要使用特殊字符
- 使用 `tsconfig.json` 配置路径别名，并在重构时优先使用别名而不是相对导入。

## 路线

详细路线约定请参阅 `./references/route-structure.md`。

- 路线应位于 `app` 目录中。
- 不要在应用目录中混合组件、类型或工具。这是一种反模式。
- 确保应用始终有一个与 "/" 匹配的路由，它可以在分组路由内部。

## 库偏好

- 使用 `expo-router` 的 `Color` 获取原生语义颜色，而不是原始 `PlatformColor`（类型安全，自动适应亮/暗）。有关完整颜色调色板模式，请参阅 `expo-native-ui`。
- 在 SDK 56+ 中，不要直接从 `@react-navigation/*` 导入 — 而是使用 `expo-router/react-navigation`（涵盖 `@react-navigation/native`、`/core`、`/elements`、`/routers`）

## 行为

- 优先使用 `Stack.SearchBar` 为屏幕添加搜索栏

# 导航

## Link

使用 `expo-router` 的 `<Link href="/path" />` 在路由之间进行导航。

```tsx
import { Link } from 'expo-router';

// 基本链接
<Link href="/path" />

// 包裹自定义组件
<Link href="/path" asChild>
  <Pressable>...</Pressable>
</Link>
```

尽可能包含 `<Link.Preview>` 以遵循 iOS 约定。频繁添加上下文菜单和预览以增强导航。

## Stack

- 始终使用 `_layout.tsx` 文件定义栈
- 使用 `expo-router/stack` 的 `Stack` 进行原生导航栈

### 页面标题

使用 `Stack.Title` 设置页面标题：

```tsx
<Stack.Title>Home</Stack.Title>
```

## 上下文菜单

为 Link 组件添加长按上下文菜单：

```tsx
import { Link } from "expo-router";

<Link href="/settings" asChild>
  <Link.Trigger>
    <Pressable>
      <Card />
    </Pressable>
  </Link.Trigger>
  <Link.Menu>
    <Link.MenuAction
      title="分享"
      icon="square.and.arrow.up"
      onPress={handleSharePress}
    />
    <Link.MenuAction
      title="屏蔽"
      icon="nosign"
      destructive
      onPress={handleBlockPress}
    />
    <Link.Menu title="更多" icon="ellipsis">
      <Link.MenuAction title="复制" icon="doc.on.doc" onPress={() => {}} />
      <Link.MenuAction
        title="删除"
        icon="trash"
        destructive
        onPress={() => {}}
      />
    </Link.Menu>
  </Link.Menu>
</Link>;
```

## Link 预览

频繁使用链接预览以增强导航：

```tsx
<Link href="/settings">
  <Link.Trigger>
    <Pressable>
      <Card />
    </Pressable>
  </Link.Trigger>
  <Link.Preview />
</Link>
```

链接预览可与上下文菜单一起使用。

## Modal

将屏幕作为模态显示：

```tsx
<Stack.Screen name="modal" options={{ presentation: "modal" }} />
```

优先使用此方法而不是构建自定义模态组件。

## Sheet

将屏幕作为动态表单面板显示：

```tsx
<Stack.Screen
  name="sheet"
  options={{
    presentation: "formSheet",
    sheetGrabberVisible: true,
    sheetAllowedDetents: [0.5, 1.0],
    contentStyle: { backgroundColor: "transparent" },
  }}
/>
```

- 使用 `contentStyle: { backgroundColor: "transparent" }` 可使背景在 iOS 26+ 上呈现为液态玻璃效果。

## 常见路线结构

带有标签和每个标签内栈的标准应用布局：

```
app/
  _layout.tsx — <NativeTabs />
  (index,search)/
    _layout.tsx — <Stack />
    index.tsx — 主列表
    search.tsx — 搜索视图
```

```tsx
// app/_layout.tsx
import { NativeTabs } from "expo-router/unstable-native-tabs";
import { ThemeProvider, DarkTheme, DefaultTheme } from "expo-router/react-navigation";
import { useColorScheme } from "react-native";

export default function Layout() {
  const colorScheme = useColorScheme();
  return (
    <ThemeProvider value={colorScheme === "dark" ? DarkTheme : DefaultTheme}>
      <NativeTabs>
        <NativeTabs.Trigger name="(index)">
          <NativeTabs.Trigger.Icon sf="list.dash" md="list" />
          <NativeTabs.Trigger.Label>项目</NativeTabs.Trigger.Label>
        </NativeTabs.Trigger>
        <NativeTabs.Trigger name="(search)" role="search" />
      </NativeTabs>
    </ThemeProvider>
  );
}
```

创建一个共享的分组路由，以便两个标签都可以推送公共屏幕：

```tsx
// app/(index,search)/_layout.tsx
import { Stack } from "expo-router/stack";
import { colors } from "@/theme/colors";

export default function Layout({ segment }) {
  const screen = segment.match(/\((.*)\)/)?.[1]!;
  const titles: Record<string, string> = { index: "项目", search: "搜索" };

  return (
    <Stack
      screenOptions={{
        headerTransparent: true,
        headerShadowVisible: false,
        headerLargeTitleShadowVisible: false,
        headerLargeStyle: { backgroundColor: "transparent" },
        headerTitleStyle: { color: colors.label },
        headerLargeTitleEnabled: true,
        headerBlurEffect: "none",
        headerBackButtonDisplayMode: "minimal",
      }}
    >
      <Stack.Screen name={screen} options={{ title: titles[screen] }} />
      <Stack.Screen name="i/[id]" options={{ headerLargeTitleEnabled: false }} />
    </Stack>
  );
}
```

`headerLargeTitleEnabled` 是 SDK 56+ 的选项名称；较旧的 SDK 使用 `headerLargeTitle`，该选项已在上游弃用。

## 提交反馈
如果您在 `expo-router` 技能中遇到错误、误导性或过时的信息，请报告以便 Expo 改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "expo-router" "<可操作的反馈>"
```
仅在您有具体且可操作的内容时才提交。尽可能包含所有相关上下文。
如果 AI 代理反复失败或用户必须接管 Expo 任务，请加载 `expo-skill-feedback` 技能并遵循其 eval-candidate 流程，而不是重复使用上述命令。
