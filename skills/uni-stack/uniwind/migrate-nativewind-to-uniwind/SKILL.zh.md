---
name: migrate-nativewind-to-uniwind
description: 将 React Native 项目从 NativeWind 迁移到 Uniwind。当用户希望用 Uniwind 替换 NativeWind、从 NativeWind 升级、切换到 Uniwind，或提及 NativeWind 到 Uniwind 的迁移时使用。处理包移除、配置迁移、Tailwind 4 升级、cssInterop 移除、主题转换以及所有破坏性变更。
---

# 将 NativeWind 迁移到 Uniwind

Uniwind 以更好的性能和稳定性取代了 NativeWind。它需要 **Tailwind CSS 4**，并使用基于 CSS 的主题设置，而不是 JS 配置。

## 迁移前检查清单

开始之前，请阅读项目的现有配置文件，了解当前设置：
- `package.json`（NativeWind 版本，依赖项）
- `tailwind.config.js` / `tailwind.config.ts`
- `metro.config.js`
- `babel.config.js`
- `global.css` 或等效的 CSS 入口文件
- `nativewind-env.d.ts` 或 `nativewind.d.ts`
- 任何使用 `cssInterop` 或 `remapProps` 从 `nativewind` 中获取的文件
- 任何从 `react-native-css-interop` 导入的文件
- 任何 NativeWind 的 `ThemeProvider`（`vars()` 使用）

## 第 1 步：移除 NativeWind 和相关包

卸载所有这些包（如果存在）：
```bash
npm uninstall nativewind react-native-css-interop
# 或
yarn remove nativewind react-native-css-interop
# 或
bun remove nativewind react-native-css-interop
```

**关键**：`react-native-css-interop` 是 NativeWind 的依赖项，必须移除。在迁移过程中，这通常会被遗漏。在整个代码库中搜索任何来自它的导入：
```bash
rg "react-native-css-interop" -g "*.{ts,tsx,js,jsx}"
```

移除找到的每个导入和使用。

## 第 2 步：安装 Uniwind 和 Tailwind 4

```bash
npm install uniwind tailwindcss@latest
# 或
yarn add uniwind tailwindcss@latest
# 或
bun add uniwind tailwindcss@latest
```

确保 `tailwindcss` 版本为 4+。

## 第 3 步：更新 babel.config.js

移除 NativeWind 的 babel 插件：
```js
// 从 presets 数组中移除这一行：
// 'nativewind/babel'
```

不需要 Uniwind 的 babel 插件。

## 第 4 步：更新 metro.config.js

用 Uniwind 的配置替换 NativeWind 的配置。`withUniwindConfig` 必须是**最外层的包装**。

**之前（NativeWind）**：
```js
const { withNativeWind } = require('nativewind/metro');
module.exports = withNativeWind(config, { input: './global.css' });
```

**之后（Uniwind）**：
```js
const { getDefaultConfig } = require('expo/metro-config');
// 对于纯 RN 项目：const { getDefaultConfig } = require('@react-native/metro-config');
const { withUniwindConfig } = require('uniwind/metro');

const config = getDefaultConfig(__dirname);

module.exports = withUniwindConfig(config, {
  cssEntryFile: './global.css',
  polyfills: { rem: 14 },
});
```

`cssEntryFile` 必须是**相对于项目根目录的字符串路径**（例如 `./global.css` 或 `./app/global.css`）。
**不要**使用绝对路径或 `path.resolve(...)` / `path.join(...)` 来设置此选项。

```js
// ❌ 错误
cssEntryFile: path.resolve(__dirname, 'app', 'global.css')

// ✅ 正确
cssEntryFile: './app/global.css'
```

**始终设置 `polyfills.rem` 为 14**，以匹配 NativeWind 的默认 rem 值，并在迁移后防止间距/尺寸差异。

如果项目使用自定义主题（超出 `light`/`dark`，例如通过 NativeWind 的 `vars()` 或自定义 `ThemeProvider` 定义），请使用 `extraThemes` 注册它们。**不要**包含 `light` 或 `dark` — 它们会自动添加：

```js
module.exports = withUniwindConfig(config, {
  cssEntryFile: './global.css',
  polyfills: { rem: 14 },
  extraThemes: ['ocean', 'sunset', 'premium'],
});
```

选项：
- `cssEntryFile`（必需）：相对于项目根目录的 CSS 入口文件路径
- `polyfills.rem`（迁移必需）：设置为 `14` 以匹配 NativeWind 的 rem 基础
- `extraThemes`（如果项目有自定义主题则必需）：自定义主题名称的数组 — **不要**包含 `light`/`dark`
- `dtsFile`（可选）：生成的 TypeScript 类型的路径，默认为 `./uniwind-types.d.ts`
- `debug`（可选）：在开发期间记录不受支持的 CSS 属性

## 第 5 步：更新 global.css

用 Tailwind 4 的导入替换 NativeWind 的 Tailwind 3 指令：

**之前**：
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**之后**：
```css
@import 'tailwindcss';
@import 'uniwind';
```

## 第 6 步：更新 CSS 入口导入

确保 `global.css` 在主 App 组件（例如 `App.tsx`）中导入，**而不是**在注册应用的根 `index.ts`/`index.js` 中导入 — 在那里导入会破坏热重载。

## 第 7 步：删除 NativeWind 类型定义

删除 `nativewind-env.d.ts` 或 `nativewind.d.ts`。Uniwind 会自动生成自己的类型，路径由 `dtsFile` 指定。

## 第 8 步：删除 tailwind.config.js

完全删除 `tailwind.config.js` / `tailwind.config.ts`。所有主题配置都移至使用 Tailwind 4 的 CSS 中的 `@theme` 指令。

将自定义主题值迁移到 `global.css`：

**之前（tailwind.config.js）**：
```js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#00a8ff',
        secondary: '#273c75',
      },
      fontFamily: {
        normal: ['Roboto-Regular'],
        bold: ['Roboto-Bold'],
      },
    },
  },
};
```

**之后（global.css）**：
```css
@import 'tailwindcss';
@import 'uniwind';

@theme {
  --color-primary: #00a8ff;
  --color-secondary: #273c75;
  --font-normal: 'Roboto-Regular';
  --font-bold: 'Roboto-Bold';
}
```

字体必须指定**单个字体** — React Native 不支持字体回退。

## 第 9 步：移除所有 cssInterop 和 remapProps 使用

**这是最常被遗漏的步骤。** 在整个代码库中搜索：

```bash
rg "cssInterop|remapProps" -g "*.{ts,tsx,js,jsx}"
```

将每个 `cssInterop()` / `remapProps()` 调用替换为 Uniwind 的 `withUniwind()`：

**之前（NativeWind）**：
```tsx
import { cssInterop } from 'react-native-css-interop';
import { Image } from 'expo-image';

cssInterop(Image, { className: 'style' });
```

**之后（Uniwind）**：
```tsx
import { withUniwind } from 'uniwind';
import { Image as ExpoImage } from 'expo-image';

export const Image = withUniwind(ExpoImage);
```

`withUniwind` 自动映射 `className` → `style` 和其他常见属性。对于自定义属性映射：

```tsx
const StyledProgressBar = withUniwind(ProgressBar, {
  width: {
    fromClassName: 'widthClassName',
    styleProperty: 'width',
  },
});
```

在**模块级别**（而不是在渲染函数内部）定义包装组件。每个组件只应包装一次：

- **仅在一个文件中使用** — 在该文件中定义包装组件：
  ```tsx
  // screens/ProfileScreen.tsx
  import { withUniwind } from 'uniwind';
  import { BlurView as RNBlurView } from '@react-native-community/blur';

  const BlurView = withUniwind(RNBlurView);

  export function ProfileScreen() {
    return <BlurView className="flex-1" />;
  }
  ```

- **在多个文件中使用** — 在共享模块中包装一次，并重新导出：
  ```tsx
  // components/styled.ts
  import { withUniwind } from 'uniwind';
  import { Image as ExpoImage } from 'expo-image';
  import { LinearGradient as RNLinearGradient } from 'expo-linear-gradient';

  export const Image = withUniwind(ExpoImage);
  export const LinearGradient = withUniwind(RNLinearGradient);
  ```
  然后在所有地方从共享模块导入：
  ```tsx
  import { Image, LinearGradient } from '@/components/styled';
  ```

**永远不要在多个文件中对同一个组件调用 `withUniwind`** — 包装一次，到处导入。

**重要**：**不要**用 `withUniwind` 包装来自 `react-native` 或 `react-native-reanimated` 的组件 — 它们已经支持 `className`。这包括 `View`、`Text`、`Image`、`ScrollView`、`FlatList`、`Pressable`、`TextInput`、`Animated.View` 等。仅对**第三方**组件使用 `withUniwind`（例如 `expo-image`、`expo-linear-gradient`、`@react-native-community/blur`）。

**重要 — 非样式属性的前缀 `accent-`**：React Native 组件有如 `color`、`tintColor`、`backgroundColor` 等不是 `style` 对象一部分的属性。要使用 Tailwind 类设置这些属性，请使用相应的 `*ClassName` 属性与 `accent-` 前缀：

```tsx
// color 属性 → colorClassName 使用 accent- 前缀
<ActivityIndicator
    className="m-4"
    size="large"
    colorClassName="accent-blue-500 dark:accent-blue-400"
/>

// Button 的 color 属性
<Button
    colorClassName="accent-background"
    title="Press me"
/>

// tintColor 属性 → tintColorClassName 使用 accent- 前缀
<Image
    className="w-6 h-6"
    tintColorClassName="accent-red-500"
    source={icon}
/>
```

规则：`className` 接受任何 Tailwind 工具用于基于样式的属性。对于非样式属性（color、tintColor 等），使用 `{propName}ClassName` 并添加 `accent-` 前缀。这适用于所有内置的 React Native 组件。

## 第 10 步：迁移 NativeWind 主题变量

**之前（NativeWind JS 主题使用 `vars()`）**：
```tsx
import { vars } from 'nativewind';

export const themes = {
  light: vars({
    '--color-primary': '#00a8ff',
    '--color-typography': '#000',
  }),
  dark: vars({
    '--color-primary': '#273c75',
    '--color-typography': '#fff',
  }),
};

// 在 JSX 中：
<View style={themes[colorScheme]}>
```

**之后（Uniwind CSS 主题）**：
```css
@layer theme {
  :root {
    @variant light {
      --color-primary: #00a8ff;
      --color-typography: #000;
    }
    @variant dark {
      --color-primary: #273c75;
      --color-typography: #fff;
    }
  }
}
```

**重要**：所有主题变体必须定义相同的一组 CSS 变量。如果 `light` 定义了 `--color-primary` 和 `--color-typography`，那么 `dark`（和任何自定义主题）也必须定义这两个。变量不匹配会导致 Uniwind 运行时错误。

不需要 `ThemeProvider` 包装器。从 JSX 中移除 NativeWind 的 `<ThemeProvider>` 或 `vars()` 包装器。如果使用 React Navigation 的 `<ThemeProvider>`，请保留。

如果项目使用嵌套主题包装器来预览或强制特定子树的主题（例如一个演示卡片、设置预览或并排主题比较），请使用 Uniwind Pro 的 `ScopedTheme` 而不是更改全局主题：
```tsx
import { ScopedTheme } from 'uniwind';

<ScopedTheme theme="dark">
  <PreviewCard />
</ScopedTheme>
```

如果项目有**超出 light/dark 的自定义主题**（例如 `ocean`、`premium`），你必须：
1. 在 CSS 中使用 `@variant` 定义它们：
```css
@layer theme {
  :root {
    @variant ocean {
      --color-primary: #0ea5e9;
      --color-background: #0c4a6e;
    }
  }
}
```
2. 通过 `extraThemes` 在 metro.config.js 中注册它们（跳过 `light`/`dark` — 它们会自动添加）：
```js
module.exports = withUniwindConfig(config, {
  cssEntryFile: './global.css',
  polyfills: { rem: 14 },
  extraThemes: ['ocean', 'premium'],
});
```

## 第 11 步：迁移 Safe Area 工具

NativeWind 的 Safe Area 类需要在 Uniwind 中显式设置：

```tsx
import { SafeAreaProvider, SafeAreaListener } from 'react-native-safe-area-context';
import { Uniwind } from 'uniwind';

export default function App() {
  return (
    <SafeAreaProvider>
      <SafeAreaListener
        onChange={({ insets }) => {
          Uniwind.updateInsets(insets);
        }}
      >
        <View className="pt-safe px-safe">
          {/* content */}
        </View>
      </SafeAreaListener>
    </SafeAreaProvider>
  );
}
```

## 第 12 步：验证 rem 值

NativeWind 使用 14px 作为基础 rem，Uniwind 默认为 16px。第 4 步已经设置 `polyfills: { rem: 14 }` 在 metro config 中以保留 NativeWind 的间距。如果用户显式想要 Uniwind 的默认值（16px），他们可以移除多边形填充 — 但警告他们所有间距/尺寸都会改变。

## 第 13 步：处理 className 去重

Uniwind **不会**自动去重冲突的 classNames（NativeWind 会）。如果您的代码库依赖于覆盖模式，如 ``className={`p-4 ${overrideClass}`}`，请设置一个 `cn` 工具。

首先，检查项目是否已经有一个 `cn` 辅助工具（在 shadcn/ui 项目中很常见）：
```bash
rg "export function cn|export const cn" -g "*.{ts,tsx,js}"
```

如果存在，保持原样。如果不存在，安装依赖项并创建它：

```bash
npm install tailwind-merge clsx
```

创建 `lib/cn.ts`（或项目中的工具所在位置）：
```ts
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}
```

使用：
```tsx
import { cn } from '@/lib/cn';

<View className={cn('p-4 bg-white', props.className)} />
<Text className={cn('text-base', isActive && 'text-blue-500', disabled && 'opacity-50')} />
```

使用 `cn` 而不是原始 `twMerge` — 它通过 `clsx` 处理条件类、数组和空值，然后使用 `tailwind-merge` 进行去重。

也支持重要工具。如果迁移的 NativeWind 代码有意使用 Tailwind 的重要修饰符强制覆盖，请保留：

```tsx
<View className="bg-blue-500 !bg-red-500" />
<Pressable className="bg-blue-500 active:!bg-red-500" />
```

重要工具会覆盖同一样式属性的普通工具。内联 `style` 仍然具有最高优先级，即使超过重要 className 工具。

## 第 14 步：更新 Animated 类名

如果项目使用 NativeWind `animated-*` / 过渡类模式，请迁移到显式的 `react-native-reanimated` 使用。Uniwind OSS 不提供 NativeWind 风格的动画类行为。

使用此迁移指南部分作为事实来源：
- https://docs.uniwind.dev/migration-from-nativewind

## 第 15 步：清理剩余的 NativeWind 引用

最终清理 — 搜索并删除任何剩余引用：

```bash
rg "nativewind|NativeWind|native-wind" -g "*.{ts,tsx,js,jsx,json,css}"
```

检查：
- 任何文件中的 NativeWind 导入
- `package.json` 中的 `nativewind`（开发依赖项也）
- `package.json` 中的 `react-native-css-interop`
- `babel.config.js` 中的 NativeWind babel 插件
- `metro.config.js` 中的 NativeWind metro 包装器
- `nativewind-env.d.ts` 或 `nativewind.d.ts` 文件
- 任何 `cssInterop()` 或 `remapProps()` 调用
- 任何 `vars()` 从 `nativewind` 的导入

使用设备感知的 CSS 函数（如 `hairlineWidth()`、`fontScale()`、`pixelRatio()`）定义自定义工具。这些函数可以用在所有地方（自定义 CSS 类、`@utility` 等）—— 但不能在 `@theme {}` 内部使用（`@theme {}` 只接受静态值）。使用 `@utility` 创建可重用的 Tailwind 风格类：

```css
@utility w-hairline { width: hairlineWidth(); }
@utility h-hairline { height: hairlineWidth(); }
@utility border-hairline { border-width: hairlineWidth(); }
@utility text-scaled { font-size: fontScale(); }
```

然后使用方式：`<View className="w-hairline h-hairline" />`

### 平台选择器

文档：https://docs.uniwind.dev/api/platform-select

使用 `ios:`, `android:`, `web:`, `native:` 前缀按平台条件性地应用样式：

```tsx
<View className="ios:bg-red-500 android:bg-blue-500 web:bg-green-500">
  <Text className="ios:text-white android:text-white web:text-black">
    Platform-specific styles
  </Text>
</View>
```

### 主题切换

文档：https://docs.uniwind.dev/theming/basics

默认情况下，Uniwind 遵循系统配色方案（自适应主题）。要程序化地切换主题：

```tsx
import { Uniwind } from 'uniwind';

Uniwind.setTheme('dark');     // 强制暗色
Uniwind.setTheme('light');    // 强制亮色
Uniwind.setTheme('system');   // 遵循系统（默认）
Uniwind.setTheme('ocean');    // 自定义主题（必须在 extraThemes 中）
```

### ScopedTheme — 仅对子树进行主题设置

文档：https://docs.uniwind.dev/api/scoped-themes

当项目需要为 UI 的部分区域使用不同主题（组件预览、主题化区域、嵌套演示）而不更改全局主题时，使用 `ScopedTheme`：

```tsx
import { ScopedTheme } from 'uniwind';

<View className="gap-3">
  <PreviewCard />

  <ScopedTheme theme="light">
    <PreviewCard />
  </ScopedTheme>

  <ScopedTheme theme="dark">
    <PreviewCard />
  </ScopedTheme>
</View>
```

重要行为：
- 最接近的 `ScopedTheme` 优先（支持嵌套作用域）
- `useUniwind`, `useResolveClassNames`, `useCSSVariable` 等钩子针对最近的作用域解析
- `withUniwind` 包裹的第三方组件在作用域内也从这个作用域解析主题值
- `ScopedTheme` 中可以使用自定义主题名称（必须在 `extraThemes` 中定义）

### 基于主题的样式 — 优先使用 CSS 变量

文档：https://docs.uniwind.dev/theming/style-based-on-themes

**优先使用基于 CSS 变量的类而不是显式的 dark:/light: 变体**。而不是：
```tsx
// 避免 这种模式
<View className="light:bg-white dark:bg-black" />
```

定义 CSS 变量并直接使用：
```css
@layer theme {
  :root {
    @variant light { --color-background: #ffffff; }
    @variant dark { --color-background: #000000; }
  }
}
```
```tsx
// 优先使用 — 自动适应主题
<View className="bg-background" />
```

这样更简洁、更容易维护，并且也能自动与自定义主题配合使用。

### 运行时 CSS 变量更新

文档：https://docs.uniwind.dev/theming/update-css-variables

在运行时更新主题变量，例如根据用户偏好或 API 响应：

```tsx
import { Uniwind } from 'uniwind';

// 根据用户输入或 API 响应预配置主题
Uniwind.updateCSSVariables('light', {
  '--color-primary': '#ff6600',
  '--color-background': '#1a1a2e',
});
```

这种模式仅在应用有真实的运行时主题需求时使用（例如用户选择的品牌颜色或 API 驱动的主题）。

### 使用 tailwind-variants 的变体

文档：https://docs.uniwind.dev/tailwind-basics#advanced-pattern-variants-and-compound-variants

对于组件变体和复合变体，使用 `tailwind-variants` 库：

```tsx
import { tv } from 'tailwind-variants';

const button = tv({
  base: 'px-4 py-2 rounded-lg',
  variants: {
    color: {
      primary: 'bg-primary text-white',
      secondary: 'bg-secondary text-white',
    },
    size: {
      sm: 'text-sm',
      lg: 'text-lg px-6 py-3',
    },
  },
});

<Pressable className={button({ color: 'primary', size: 'lg' })} />
```

### 单一仓库支持

文档：https://docs.uniwind.dev/monorepos

如果项目是单一仓库，在 `global.css` 中添加 `@source` 指令，以便 Tailwind 扫描 CSS 入口文件目录外的包（仅当该目录包含具有 Tailwind 类的组件时）：

```css
@import 'tailwindcss';
@import 'uniwind';
@source "../../packages/ui/src";
@source "../../packages/shared/src";
```

### 常见问题解答

文档：https://docs.uniwind.dev/faq

**自定义字体**：Uniwind 仅将 className 映射到 font-family — 字体文件必须单独加载（`app.json` 中的 expo-font 插件或 `react-native-asset` 用于裸 RN）。`@theme` 中的字体名称必须与文件名完全匹配（不带扩展名）。使用 `@variant` 为平台特定字体（必须位于 `@layer theme { :root { } }` 内）：
```css
@layer theme {
  :root {
    @variant ios { --font-sans: 'SF Pro Text'; }
    @variant android { --font-sans: 'Roboto-Regular'; }
    @variant web { --font-sans: 'system-ui'; }
  }
}
```

**数据选择器**：使用 `data-[prop=value]:utility` 进行基于属性的样式。仅支持等值检查：
```tsx
<View data-state={isOpen ? 'open' : 'closed'} className="data-[state=open]:bg-muted/50" />
```

**Expo Router 中的 global.css 位置**：放置在项目根目录并在根布局 (`app/_layout.tsx`) 中导入。如果放置在 `app/` 中，则外部组件需要 `@source` 指令。Tailwind 从 `global.css` 位置扫描。

**CSS 变更时的全应用刷新**：Metro 无法热重载具有多个提供者的文件。将 `global.css` 导入移到组件树更深的位置（例如导航根或主屏幕）以修复。

**渐变**：内置支持，无需额外依赖。使用 `bg-gradient-to-r from-red-500 via-yellow-500 to-green-500`。对于 `expo-linear-gradient`，使用 `useCSSVariable` 获取颜色 — `withUniwind` 不适用，因为渐变属性是数组。

**样式特异性**：内联 `style` 总是覆盖 `className`。使用 `className` 用于静态样式，仅内联用于真正动态的值。避免对同一属性混合两者。

**序列化错误** (`Failed to serialize javascript object`)：清除缓存：`watchman watch-del-all 2>/dev/null; rm -rf node_modules/.cache && npx expo start --clear`。常见原因：复杂的 `@theme` 配置、CSS 变量循环引用。

**Metro unstable_enablePackageExports 冲突**：某些应用（如加密等）禁用此功能，导致 Uniwind 出错。使用选择性解析器：
```js
config.resolver.unstable_enablePackageExports = false;
config.resolver.resolveRequest = (context, moduleName, platform) => {
  if (['uniwind', 'culori'].some((prefix) => moduleName.startsWith(prefix))) {
    return context.resolveRequest({ ...context, unstable_enablePackageExports: true }, moduleName, platform);
  }
  return context.resolveRequest(context, moduleName, platform);
};
```

**安全区域类**：`p-safe`, `pt-safe`, `pb-safe`, `px-safe`, `py-safe`, `m-safe`, `mt-safe`, 等。也支持 `-or-{value}`（最小间距）和 `-offset-{value}`（额外间距）变体。

**Next.js**：不官方支持。Uniwind 适用于 Metro 和 Vite。社区插件：`uniwind-plugin-next`。对于 Next.js，使用标准 Tailwind CSS 并共享设计令牌。

**Vite**：自 v1.2.0 起支持。使用 `uniwind/vite` 插件与 `@tailwindcss/vite` 一起使用。

**UI 套件**：HeroUI Native、react-native-reusables 和 Gluestack 4.1+ 与 Uniwind 配合良好

## 已知问题和注意事项

1. **data-* 属性**：Uniwind 支持 `data-[prop=value]:utility` 语法用于条件样式，类似于 NativeWind。
2. **动画样式**：将 NativeWind 动画类迁移到 `react-native-reanimated` 直接。Uniwind Pro 具有内置 Reanimated 支持。

## 验证

迁移后验证：
1. `npx react-native start --reset-cache`（清除 Metro 缓存）或使用 expo `npx expo start -c`
2. 所有屏幕在 iOS 和 Android 上正确渲染
3. 主题切换正常（亮/暗）
4. 自定义字体加载正确
5. 安全区域偏移应用正确
6. 没有关于缺少样式的控制台警告
7. 没有 `nativewind` 或 `react-native-css-interop` 的剩余导入

**重要提示**：不要猜测 Uniwind API。如果你对任何 Uniwind API、钩子、组件或配置选项不确定，请参考官方文档：[https://docs.uniwind.dev/llms-full.txt](https://docs.uniwind.dev/llms-full.txt)
