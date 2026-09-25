本技能的说明仅适用于 SDK 55。对于其他 SDK 版本，请参考相应版本的 Expo UI Jetpack Compose 文档以获取最准确的信息。

## 安装

```bash
npx expo install @expo/ui
```

安装后需要执行原生重建 (`npx expo run:android`)。

## 说明

- Expo UI 的 API 与 Jetpack Compose 的 API 相同。使用 Jetpack Compose 和 Material Design 3 的知识来决定使用哪些组件或修饰符。如果您需要更深入的 Jetpack Compose 或 Material 3 指导（例如，选择哪个组件、布局模式、主题），请启动子代理来研究 [Jetpack Compose](https://developer.android.com/develop/ui/compose/components) 和 [Material Design 3](https://m3.material.io/) 的最佳实践。
- 组件从 `@expo/ui/jetpack-compose` 导入，修饰符从 `@expo/ui/jetpack-compose/modifiers` 导入。
- **始终阅读 `.d.ts` 类型文件**，在使用组件或修饰符之前确认 API。运行 `node -e "console.log(path.dirname(require.resolve('@expo/ui/jetpack-compose')))"` 来定位包，然后阅读相关的 `{ComponentName}/index.d.ts` 文件。这是最可靠的来源。
- 在使用组件之前，请获取其文档以确认 API - https://docs.expo.dev/versions/v55.0.0/sdk/ui/jetpack-compose/{component-name}/index.md
- 当不确定修饰符的 API 时，请参考文档 - https://docs.expo.dev/versions/v55.0.0/sdk/ui/jetpack-compose/modifiers/index.md
- 每个 Jetpack Compose 树都必须用 `Host` 包裹。使用 `<Host matchContents>` 进行内联尺寸，或者当需要明确尺寸时（例如作为 `LazyColumn` 的父级）使用 `<Host style={{ flex: 1 }}>`。示例：

```jsx
import { Host, Column, Button, Text } from "@expo/ui/jetpack-compose";
import { fillMaxWidth, paddingAll } from "@expo/ui/jetpack-compose/modifiers";

<Host matchContents>
  <Column verticalArrangement={{ spacedBy: 8 }} modifiers={[fillMaxWidth(), paddingAll(16)]}>
    <Text style={{ typography: "titleLarge" }}>Hello</Text>
    <Button onPress={() => alert("Pressed!")}>Press me</Button>
  </Column>
</Host>;
```

## 关键组件

- **LazyColumn** — 用于可滚动列表，替代 react-native 的 `ScrollView`/`FlatList`。用 `<Host style={{ flex: 1 }}>` 包裹。
- **Icon** — 使用 `<Icon source={require('./icon.xml')} size={24} />` 与 Android XML 矢量绘制资源配合使用。获取图标：前往 [Material Symbols](https://fonts.google.com/icons)，选择一个图标，选择 Android 平台，并下载 XML 矢量绘制资源。将这些保存为 `.xml` 文件到项目的 `assets/` 目录（例如 `assets/icons/wifi.xml`）。Metro 会自动打包 `.xml` 资源——无需修改 metro 配置。
