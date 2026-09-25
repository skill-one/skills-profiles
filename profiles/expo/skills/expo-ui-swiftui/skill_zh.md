本技能中的说明仅适用于 SDK 55。对于其他 SDK 版本，请参考相应版本的 Expo UI SwiftUI 文档以获取最准确的信息。

## 安装

```bash
npx expo install @expo/ui
```

安装后需要执行原生重建 (`npx expo run:ios`)。

## 说明

- Expo UI 的 API 与 SwiftUI 的 API 相同。使用 SwiftUI 的知识来决定使用哪些组件或修饰符。
- 组件从 `@expo/ui/swift-ui` 中导入，修饰符从 `@expo/ui/swift-ui/modifiers` 中导入。
- 在使用某个组件之前，请查阅其文档以确认 API - https://docs.expo.dev/versions/v55.0.0/sdk/ui/swift-ui/{component-name}/index.md
- 对于不确定的修饰符 API，请参考文档 - https://docs.expo.dev/versions/v55.0.0/sdk/ui/swift-ui/modifiers/index.md
- 每个 SwiftUI 树都必须用 `Host` 包裹。
- `RNHostView` 专门用于在 SwiftUI 树中嵌入 RN 组件。示例：

```jsx
import { Host, VStack, RNHostView } from "@expo-ui/swift-ui";
import { Pressable } from "react-native";

<Host matchContents>
  <VStack>
    <RNHostView matchContents>
      // 在这里，`Pressable` 是一个 RN 组件，因此它被包裹在 `RNHostView` 中。
      <Pressable />
    </RNHostView>
  </VStack>
</Host>;
```

- 如果 Expo UI 中缺少某个必需的修饰符或视图，可以通过本地 Expo 模块进行扩展。参见：https://docs.expo.dev/guides/expo-ui-swift-ui/extending/index.md。在扩展之前请与用户确认。
