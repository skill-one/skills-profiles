# 将 Stitch 网页设计转换为 React Native 组件

你是一位专注于将 Stitch 网页设计转换为干净、可生产使用的 React Native 代码的移动工程师，或者同步/更新现有的原生组件以与最新的 Stitch 设计保持一致。你使用 React Native 基本组件和 `StyleSheet` 将 HTML/CSS 布局转换为原生移动组件。

> **关键：** 此技能的每一步都是**强制执行**的。**不要跳过任何步骤或走捷径**。每个部分都包含一个**门禁**，必须满足才能继续进行。

## 第一阶段：检索和网络

> **门禁：** 仅当所有屏幕都通过 `scripts/fetch-stitch.sh` 下载并**进行视觉审核**时，第一阶段才完成。**禁止**直接读取本地文件而不经过此阶段。

1. **命名空间发现**：运行 `list_tools` 找到 Stitch MCP 前缀。使用此前缀（例如，`stitch:`）进行所有后续调用。
2. **元数据获取**：对项目中的**每个屏幕**调用 `[prefix]:get_screen` 以检索设计 JSON 和下载 URL。**不要跳过任何屏幕**。
3. **检查现有设计**：在下载之前，检查 `.stitch/designs/{page}.html` 和 `.stitch/designs/{page}.png` 是否已存在：
   - **如果文件存在**：询问用户是否要使用 MCP 从 Stitch 项目刷新设计，还是重用现有的本地文件。**你必须询问——不要假设**。只有在用户确认的情况下才重新下载。
   - **如果文件不存在**：继续步骤 4。
4. **高可靠性下载**：内部 AI 获取工具在 Google Cloud Storage 域名上可能会失败。你必须使用提供的脚本。
   - **HTML**：`bash scripts/fetch-stitch.sh "[htmlCode.downloadUrl]" ".stitch/designs/{page}.html"`
   - **截图**：首先将 `=w{width}` 追加到截图 URL 中，其中 `{width}` 是屏幕元数据中的 `width` 值（Google CDN 默认提供低分辨率缩略图）。然后运行：`bash scripts/fetch-stitch.sh "[screenshot.downloadUrl]=w{width}" ".stitch/designs/{page}.png"`
   - 此脚本处理必要的重定向和安全握手。
5. **视觉审核**：查看下载的截图（`.stitch/designs/{page}.png`）以确认设计意图和布局细节。**你必须查看每个截图**——不要基于对设计的假设继续进行。
6. **项目元数据跟踪**：使用 `[prefix]:get_project` 检索项目配置并将其保存到 `.stitch/metadata.json`（在应用文件夹内，并在工作区根目录中镜像）。确保它包含：
   - `projectId`, `title`, `deviceType`
   - 一个 `Last Sync Time` 字段，与当前同步 ISO 执行时间匹配
   - 一个 `screens` 映射，详细说明每个屏幕的 ID、标签、sourceScreen 引用、尺寸和 canvasPosition。

### 第一阶段的反模式
- ❌ 在调用 MCP `get_screen` 之前直接读取 `.stitch/designs/*.html`。
- ❌ 跳过 `fetch-stitch.sh` 下载脚本。
- ❌ 在找到现有文件时没有询问用户。
- ❌ 跳过 `.png` 截图的视觉审核。
- ❌ 在同步时未能生成或更新 `.stitch/metadata.json` 及其 `Last Sync Time` 字段。

## 第二阶段：主题提取

> **门禁：** 仅当 `src/theme.ts` 已创建或更新，并包含从当前项目的 HTML `<head>` 中提取的令牌时，第二阶段才完成。**不允许**硬编码十六进制颜色代码或使用来自不同项目的主题。

1. **提取 `tailwind.config`**：打开每个下载的 HTML 文件，并在 `<head>` `<script>` 块中找到 `tailwind.config` 对象。提取：
   - 所有颜色令牌
   - 字体家族
   - 间距值
   - 边框半径值
   - 字体大小/排版令牌
2. **创建/同步 `src/theme.ts`**：将提取的令牌写入 `src/theme.ts` 作为 TypeScript 常量。确保每个颜色、间距和排版值都有一个对应的令牌。
3. **验证主题**：确认 `src/theme.ts` 中的主题颜色和字体与从 HTML 设计中提取的内容匹配。

### 第二阶段的反模式
- ❌ 直接在组件 `StyleSheet` 声明中硬编码十六进制颜色代码或 rgba 字符串。
- ❌ 在未从新设计中提取主题令牌的情况下使用来自先前项目的主题令牌。
- ❌ 跳过 `src/theme.ts` 的创建/更新。

## 第三阶段：架构规则和 HTML 映射

> **门禁：** 每个组件必须满足以下所有规则。违反规定会导致 `npm run validate` 失败。

### 元素映射
使用以下规则将 HTML 元素映射到 React Native 组件：

| HTML | React Native | 备注 |
|------|-------------|-------|
| `<div>` | `View` | 默认容器 |
| `<span>`, `<p>`, `<h1>`-`<h6>` | `Text` | 所有文本必须包裹在 `Text` 中。嵌套 `Text` 以进行内联样式。 |
| `<img>` | `Image` | 使用 `source={{ uri }}` 用于远程图像，`require()` 用于本地资源。 |
| `<button>`, `<a>` | `Pressable` | 优先使用 `Pressable` 而不是 `TouchableOpacity`。使用 `onPress` 而不是 `onClick`。 |
| `<input>` | `TextInput` | 映射 `placeholder`, `value`, `onChangeText`。 |
| `<scroll container>` | `ScrollView` | 仅用于短列表。使用 `FlatList` 用于长或动态列表。 |
| `<ul>`/`<ol>` 包含许多项目 | `FlatList` | 需要 `data`, `renderItem`, `keyExtractor`。 |
| `<section>` 包含分组数据 | `SectionList` | 用于带标题的分组数据。使用标签导航器用于基于标签的布局。 |
| `<select>` | 第三方选择器或自定义模态 | React Native 没有内置的选择器。 |
| `<svg>` | `react-native-svg` | 将 SVG 标记转换为 `Svg`, `Path`, `Circle` 等。 |
| 根包装器 | `SafeAreaView` | 包装顶层屏幕以避免缺口/状态栏重叠。 |

### 样式映射
CSS 和 Tailwind 类在 React Native 中不起作用。将所有样式转换为 `StyleSheet.create()`：

* **布局**：Flexbox 是默认的布局系统。`flexDirection` 默认为 `'column'`（与网页 CSS 中的 `'row'` 不同）。
  - `display: flex` 在每个 `View` 上是隐式的。
  - `justify-content` 映射到 `justifyContent`。
  - `align-items` 映射到 `alignItems`。
  - `gap` 映射到 `gap`（React Native 0.71+）。对于旧版本，在子元素上使用 `marginBottom`。
* **尺寸**：使用数字（而不是字符串）。`width: 100` 表示 100 密度无关像素。
  - 百分比字符串受支持：`width: '100%'`。
  - 对于响应式尺寸，使用 `useWindowDimensions()` 从 `react-native`。
  - 没有 `vw`/`vh`。从 `Dimensions.get('window')` 计算。
* **排版**：所有文本样式必须在 `Text` 组件上，绝不能在 `View` 上。
  - `font-size` 映射到 `fontSize`（数字，不是字符串）。
  - `font-weight` 映射到 `fontWeight`（字符串：`'400'`, `'700'`, `'bold'`）。
  - `line-height` 映射到 `lineHeight`（数字）。
  - `letter-spacing` 映射到 `letterSpacing`。
  - `text-transform` 映射到 `textTransform`。
  - `color` 仅适用于 `Text`。
* **边框和阴影**：
  - `border-radius` 映射到 `borderRadius`。
  - `box-shadow` 不存在。使用 `elevation`（Android）和 `shadowColor`/`shadowOffset`/`shadowOpacity`/`shadowRadius`（iOS）。使用 `Platform.select()` 应用平台特定的阴影样式。
* **不支持的 CSS 属性**：不要使用 `hover`、`transition`、`animation`（使用 `react-native-reanimated` 进行动画），或 `position: fixed`（使用绝对定位代替）。

### 架构规则
* **模块化组件（原子设计）**：将设计分解为独立文件。将组件组织为原子（按钮、标签、图标）、分子（输入组、卡片）和有机体（标题、列表、表单）。将它们放置在 `src/components/atoms/`、`src/components/molecules/` 和 `src/components/organisms/`。**禁止**使用单体页面/屏幕文件。
* **逻辑隔离**：将事件处理程序、API 调用和业务逻辑移到 `src/hooks/` 中的自定义钩子中。组件应仅处理渲染。
* **数据解耦**：将所有静态文本、图像 URL 和列表移到 `src/data/mockData.ts`。组件中**没有**硬编码内容。
* **类型安全**：**每个**组件文件（包括屏幕）必须导出一个名为 `[ComponentName]Props` 的 TypeScript 接口，并使用 `readonly` 属性修饰符。验证器要求接口**导出**——没有导出 Props 接口的文件将**失败**验证。
* **没有硬编码样式**：将颜色、间距和字体大小提取到 `src/theme.ts`。在 `StyleSheet.create()` 中引用它们。组件文件中**绝对没有**原始十六进制颜色代码或 rgba 字符串。
* **导航**：使用 React Navigation 进行屏幕过渡。使用 `NativeStackScreenProps` 或 `BottomTabScreenProps` 定义屏幕类型。
* **可访问性**：每个交互式元素必须有 `accessibilityLabel` 和 `accessibilityRole`。图像需要 `accessibilityLabel`。使用 `accessibilityState` 用于切换和复选框。
* **安全区域**：使用 `react-native-safe-area-context` 中的 `SafeAreaView` 包装顶层屏幕组件（不是 `react-native` 默认提供的那个）。
* **项目特定**：专注于目标项目的需求和限制。不要在工作生成的组件中包含 Google 许可头。

### 平台特定代码
当设计需要在 iOS 和 Android 上具有不同行为时：
```typescript
import { Platform } from 'react-native';

const styles = StyleSheet.create({
  shadow: Platform.select({
    ios: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
    },
    android: {
      elevation: 4,
    },
  }),
});
```

### 第三阶段的反模式
- ❌ 将所有 UI 放在一个单体屏幕文件中。
- ❌ 使用 HTML 标签（如 `div`、`span`、`p`）而不是 React Native 组件。
- ❌ 没有自定义钩子而使用内联事件处理程序或业务逻辑。
- ❌ 在组件文件中硬编码文本、URL 或颜色。
- ❌ 组件没有**导出**的 `[Name]Props` 接口。
- ❌ 在 `StyleSheet.create()` 中使用原始十六进制颜色值或 rgba 字符串。

## 第四阶段：执行步骤

> **门禁：** 第四阶段验证、审核和模拟器/打包器测试是可选的。你必须询问用户的许可才能继续使用验证脚本、启动打包器或进行模拟器审核。

1. **环境设置**：如果 `node_modules` 缺失，运行 `npm install` 以启用验证工具。
2. **主题层**：从提取的 Tailwind 配置创建 `src/theme.ts`。
3. **数据层**：根据设计内容创建 `src/data/mockData.ts`。
4. **组件草稿**：使用 `resources/component-template.tsx` 作为基础。查找并替换所有 `StitchComponent` 实例为实际组件名称。将 HTML 元素映射到 React Native 基本组件。
5. **导航连接**：如果设计有多个屏幕，在 `App.tsx` 中设置一个带有堆栈或标签导航器的 `NavigationContainer`。
6. **质量检查（可选——先询问用户）**：
    * 对组件和屏幕中的**每个** `.tsx` 文件运行 `npm run validate <file_path>` 以报告组件有效性。
    * 运行 `tsc --noEmit` 以验证 TypeScript 编译状态。
    * 对照 `resources/architecture-checklist.md` 检查输出。
    * 在启动打包器（`npx react-native start` 或 `npx expo start`）或启动视觉模拟器审核以验证应用在模拟器/设备上正确渲染之前，获得许可。

### 第四阶段的反模式
- ❌ 在未经用户许可的情况下启动打包器或模拟器。
- ❌ 声明任务“完成”而未验证代码编译。
