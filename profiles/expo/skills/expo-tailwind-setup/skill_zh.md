# 使用 react-native-css 在 Expo 中设置 Tailwind CSS v4 与 NativeWind v5

本指南介绍了如何使用 react-native-css 和 NativeWind v5 在 Expo 中设置 Tailwind CSS v4，以实现 iOS、Android 和 Web 的通用样式。

## 概述

此设置使用：

- **Tailwind CSS v4** - 现代 CSS 首选配置
- **react-native-css** - React Native 的 CSS 运行时
- **NativeWind v5** - React Native 中 Tailwind 的 Metro 转换器
- **@tailwindcss/postcss** - Tailwind v4 的 PostCSS 插件

## 安装

```bash
# 安装依赖项
npx expo install tailwindcss@^4 nativewind@5.0.0-preview.2 react-native-css@0.0.0-nightly.5ce6396 @tailwindcss/postcss tailwind-merge clsx
```

添加 lightningcss 兼容性解析：

```json
// package.json
{
  "resolutions": {
    "lightningcss": "1.30.1"
  }
}
```

- 由于 lightningcss，Expo 中不需要 autoprefixer
- postcss 在 Expo 中默认包含

## 配置文件

### Metro 配置

创建或更新 `metro.config.js`：

```js
// metro.config.js
const { getDefaultConfig } = require("expo/metro-config");
const { withNativewind } = require("nativewind/metro");

/** @type {import('expo/metro-config').MetroConfig} */
const config = getDefaultConfig(__dirname);

module.exports = withNativewind(config, {
  // 内联变量会破坏 CSS 变量中的 PlatformColor
  inlineVariables: false,
  // 我们手动添加了 className 支持
  globalClassNamePolyfill: false,
});
```

### PostCSS 配置

创建 `postcss.config.mjs`：

```js
// postcss.config.mjs
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};
```

### 全局 CSS

创建 `src/global.css`：

```css
@import "tailwindcss/theme.css" layer(theme);
@import "tailwindcss/preflight.css" layer(base);
@import "tailwindcss/utilities.css";

/* 平台特定的字体家族 */
@media android {
  :root {
    --font-mono: monospace;
    --font-rounded: normal;
    --font-serif: serif;
    --font-sans: normal;
  }
}

@media ios {
  :root {
    --font-mono: ui-monospace;
    --font-serif: ui-serif;
    --font-sans: system-ui;
    --font-rounded: ui-rounded;
  }
}
```

## 重要提示：不需要 Babel 配置

使用 Tailwind v4 和 NativeWind v5，您**不需要**为 Tailwind 创建 `babel.config.js`。如果存在任何仅包含 NativeWind 配置的 `babel.config.js`，请删除它：

```js
// 如果 babel.config.js 仅包含 NativeWind 配置，则删除它
// 以下不再需要：
// module.exports = function (api) {
//   api.cache(true);
//   return {
//     presets: [
//       ["babel-preset-expo", { jsxImportSource: "nativewind" }],
//       "nativewind/babel",
//     ],
//   };
// };
```

## CSS 组件包装器

由于 react-native-css 需要显式 CSS 元素包装，因此请创建可重用的组件：

### 主要组件 (`src/tw/index.tsx`)

```tsx
import {
  useCssElement,
  useNativeVariable as useFunctionalVariable,
} from "react-native-css";

import { Link as RouterLink } from "expo-router";
import Animated from "react-native-reanimated";
import React from "react";
import {
  View as RNView,
  Text as RNText,
  Pressable as RNPressable,
  ScrollView as RNScrollView,
  TouchableHighlight as RNTouchableHighlight,
  TextInput as RNTextInput,
  StyleSheet,
} from "react-native";

// CSS 支持的 Link
export const Link = (
  props: React.ComponentProps<typeof RouterLink> & { className?: string }
) => {
  return useCssElement(RouterLink, props, { className: "style" });
};

Link.Trigger = RouterLink.Trigger;
Link.Menu = RouterLink.Menu;
Link.MenuAction = RouterLink.MenuAction;
Link.Preview = RouterLink.Preview;

// CSS 变量钩子
export const useCSSVariable =
  process.env.EXPO_OS !== "web"
    ? useFunctionalVariable
    : (variable: string) => `var(${variable})`;

// View
export type ViewProps = React.ComponentProps<typeof RNView> & {
  className?: string;
};

export const View = (props: ViewProps) => {
  return useCssElement(RNView, props, { className: "style" });
};
View.displayName = "CSS(View)";

// Text
export const Text = (
  props: React.ComponentProps<typeof RNText> & { className?: string }
) => {
  return useCssElement(RNText, props, { className: "style" });
};
Text.displayName = "CSS(Text)";

// ScrollView
export const ScrollView = (
  props: React.ComponentProps<typeof RNScrollView> & {
    className?: string;
    contentContainerClassName?: string;
  }
) => {
  return useCssElement(RNScrollView, props, {
    className: "style",
    contentContainerClassName: "contentContainerStyle",
  });
};
ScrollView.displayName = "CSS(ScrollView)";

// Pressable
export const Pressable = (
  props: React.ComponentProps<typeof RNPressable> & { className?: string }
) => {
  return useCssElement(RNPressable, props, { className: "style" });
};
Pressable.displayName = "CSS(Pressable)";

// TextInput
export const TextInput = (
  props: React.ComponentProps<typeof RNTextInput> & { className?: string }
) => {
  return useCssElement(RNTextInput, props, { className: "style" });
};
TextInput.displayName = "CSS(TextInput)";

// AnimatedScrollView
export const AnimatedScrollView = (
  props: React.ComponentProps<typeof Animated.ScrollView> & {
    className?: string;
    contentClassName?: string;
    contentContainerClassName?: string;
  }
) => {
  return useCssElement(Animated.ScrollView, props, {
    className: "style",
    contentClassName: "contentContainerStyle",
    contentContainerClassName: "contentContainerStyle",
  });
};

// TouchableHighlight with underlayColor 提取
function XXTouchableHighlight(
  props: React.ComponentProps<typeof RNTouchableHighlight>
) {
  const { underlayColor, ...style } = StyleSheet.flatten(props.style) || {};
  return (
    <RNTouchableHighlight
      underlayColor={underlayColor}
      {...props}
      style={style}
    />
  );
}

export const TouchableHighlight = (
  props: React.ComponentProps<typeof RNTouchableHighlight>
) => {
  return useCssElement(XXTouchableHighlight, props, { className: "style" });
};
TouchableHighlight.displayName = "CSS(TouchableHighlight)";
```

### 图片组件 (`src/tw/image.tsx`)

```tsx
import { useCssElement } from "react-native-css";
import React from "react";
import { StyleSheet } from "react-native";
import Animated from "react-native-reanimated";
import { Image as RNImage } from "expo-image";

const AnimatedExpoImage = Animated.createAnimatedComponent(RNImage);

export type ImageProps = React.ComponentProps<typeof Image>;

function CSSImage(props: React.ComponentProps<typeof AnimatedExpoImage>) {
  // @ts-expect-error: Remap objectFit style to contentFit property
  const { objectFit, objectPosition, ...style } =
    StyleSheet.flatten(props.style) || {};

  return (
    <AnimatedExpoImage
      contentFit={objectFit}
      contentPosition={objectPosition}
      {...props}
      source={
        typeof props.source === "string" ? { uri: props.source } : props.source
      }
      // @ts-expect-error: Style is remapped above
      style={style}
    />
  );
}

export const Image = (
  props: React.ComponentProps<typeof CSSImage> & { className?: string }
) => {
  return useCssElement(CSSImage, props, { className: "style" });
};

Image.displayName = "CSS(Image)";
```

### 动画组件 (`src/tw/animated.tsx`)

```tsx
import * as TW from "./index";
import RNAnimated from "react-native-reanimated";

export const Animated = {
  ...RNAnimated,
  View: RNAnimated.createAnimatedComponent(TW.View),
};
```

## 使用方法

从您的 tw 目录中导入 CSS 包装的组件：

```tsx
import { View, Text, ScrollView, Image } from "@/tw";

export default function MyScreen() {
  return (
    <ScrollView className="flex-1 bg-white">
      <View className="p-4 gap-4">
        <Text className="text-xl font-bold text-gray-900">Hello Tailwind!</Text>
        <Image
          className="w-full h-48 rounded-lg object-cover"
          source={{ uri: "https://example.com/image.jpg" }}
        />
      </View>
    </ScrollView>
  );
}
```

## 自定义主题变量

在您的 global.css 中使用 `@theme` 添加自定义主题变量：

```css
@layer theme {
  @theme {
    /* 自定义字体 */
    --font-rounded: "SF Pro Rounded", sans-serif;

    /* 自定义行高 */
    --text-xs--line-height: calc(1em / 0.75);
    --text-sm--line-height: calc(1.25em / 0.875);
    --text-base--line-height: calc(1.5em / 1);

    /* 自定义行间距 */
    --leading-tight: 1.25em;
    --leading-snug: 1.375em;
    --leading-normal: 1.5em;
  }
}
```

## 平台特定样式

使用平台媒体查询进行平台特定样式：

```css
@media ios {
  :root {
    --font-sans: system-ui;
    --font-rounded: ui-rounded;
  }
}

@media android {
  :root {
    --font-sans: normal;
    --font-rounded: normal;
  }
}
```

## 使用 CSS 变量实现 Apple 系统颜色

创建一个 CSS 文件用于 Apple 语义颜色：

```css
/* src/css/sf.css */
@layer base {
  html {
    color-scheme: light;
  }
}

:root {
  /* 强调色（亮/暗模式） */
  --sf-blue: light-dark(rgb(0 122 255), rgb(10 132 255));
  --sf-green: light-dark(rgb(52 199 89), rgb(48 209 89));
  --sf-red: light-dark(rgb(255 59 48), rgb(255 69 58));

  /* 灰度 */
  --sf-gray: light-dark(rgb(142 142 147), rgb(142 142 147));
  --sf-gray-2: light-dark(rgb(174 174 178), rgb(99 99 102));

  /* 文本颜色 */
  --sf-text: light-dark(rgb(0 0 0), rgb(255 255 255));
  --sf-text-2: light-dark(rgb(60 60 67 / 0.6), rgb(235 235 245 / 0.6));

  /* 背景颜色 */
  --sf-bg: light-dark(rgb(255 255 255), rgb(0 0 0));
  --sf-bg-2: light-dark(rgb(242 242 247), rgb(28 28 30));
}

/* iOS 原生颜色通过 platformColor */
@media ios {
  :root {
    --sf-blue: platformColor(systemBlue);
    --sf-green: platformColor(systemGreen);
    --sf-red: platformColor(systemRed);
    --sf-gray: platformColor(systemGray);
    --sf-text: platformColor(label);
    --sf-text-2: platformColor(secondaryLabel);
    --sf-bg: platformColor(systemBackground);
    --sf-bg-2: platformColor(secondarySystemBackground);
  }
}

/* 注册为 Tailwind 主题颜色 */
@layer theme {
  @theme {
    --color-sf-blue: var(--sf-blue);
    --color-sf-green: var(--sf-green);
    --color-sf-red: var(--sf-red);
    --color-sf-gray: var(--sf-gray);
    --color-sf-text: var(--sf-text);
    --color-sf-text-2: var(--sf-text-2);
    --color-sf-bg: var(--sf-bg);
    --color-sf-bg-2: var(--sf-bg-2);
  }
}
```

然后在组件中使用：

```tsx
<Text className="text-sf-text">Primary text</Text>
<Text className="text-sf-text-2">Secondary text</Text>
<View className="bg-sf-bg">...</View>
```

## 在 JavaScript 中使用 CSS 变量

使用 `useCSSVariable` 钩子：

```tsx
import { useCSSVariable } from "@/tw";

function MyComponent() {
  const blue = useCSSVariable("--sf-blue");

  return <View style={{ borderColor: blue }} />;
}
```

## 与 NativeWind v4 / Tailwind v3 的主要区别

1. **不需要 babel.config.js** - 配置现在是 CSS 首选
2. **PostCSS 插件** - 使用 `@tailwindcss/postcss` 而不是 `tailwindcss`
3. **CSS 导入** - 使用 `@import "tailwindcss/..."` 而不是 `@tailwind` 指令
4. **主题配置** - 在 CSS 中使用 `@theme` 而不是 `tailwind.config.js`
5. **组件包装器** - 必须使用 `useCssElement` 包装组件以支持 className
6. **Metro 配置** - 使用 `withNativewind` 并使用不同的选项 (`inlineVariables: false`)

## 故障排除

### 样式未应用

1. 确保在应用程序入口处导入了 CSS 文件
2. 检查组件是否使用 `useCssElement` 包装
3. 确认 Metro 配置已应用 `withNativewind`

### 平台颜色不工作

1. 在 `@media ios` 块中使用 `platformColor()`
2. 对于 Web/Android 使用 `light-dark()` 作为后备

### TypeScript 错误

在组件属性中添加 className：

```tsx
type Props = React.ComponentProps<typeof RNView> & { className?: string };
```

## 提交反馈

如果您遇到错误、误导性或过时的信息，请报告给 Expo 以改进：

```bash
npx --yes submit-expo-feedback@latest --category skills --subject "expo-tailwind-setup" "<actionable feedback>"
```

仅在有具体且可操作的反馈时提交。尽可能提供相关上下文。
如果 AI 代理反复失败或用户不得不接管 Expo 任务，请加载 `expo-skill-feedback` 技能并遵循其 eval-candidate 流程，而不是重复使用上述命令。
