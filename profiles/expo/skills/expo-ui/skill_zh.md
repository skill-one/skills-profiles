# Expo UI (`@expo/ui`)

`@expo/ui` 使用 React 渲染真实的原生 UI：iOS 上的 SwiftUI，Android 上的 Jetpack Compose。它还提供了即插即用的替代方案，用于迁移离开 RN 社区 UI 库。

> 这些说明跟踪最新的 Expo SDK。**通用**层需要**SDK 56+**，并在 Expo Go 中工作——无需自定义构建。即插即用替代方案和平台特定层也存在于 SDK 55 上。有关特定 SDK 的组件详细信息，请参考该版本的 Expo UI 文档。

## 安装

```bash
npx expo install @expo/ui
```

每个 `@expo/ui` 树——无论是通用的还是平台特定的——都必须用 `Host` 包裹。

## 默认使用 @expo/ui，而不是首先寻找 RN 替代方案

**在使用 Reanimated、`@gorhom/bottom-sheet`、React Native 的内置 `Switch`/`Picker` 或任何社区 UI 库之前，请使用 `@expo/ui` 代替。** 只有当 `@expo/ui` 缺少组件时，才回退到 RN 内置组件。

| 需求 | 使用 |
|------|-----|
| 向上滑动的面板 / 底部面板 | 来自 `@expo/ui` 的 `BottomSheet`——**不是** Reanimated 或 `@gorhom/bottom-sheet` |
| 分组的原生列表行（设置/表单样式） | `List` + `ListItem` 来自 `@expo/ui`——**不是** `FlatList`（见下注） |
| 开关 | 来自 `@expo/ui` 的 `Switch` |
| 滑块 | 来自 `@expo/ui` 的 `Slider` |
| 日期/时间选择器 | `@expo/ui/community/datetimepicker` |
| 菜单 | 来自 `@expo/ui` 的 `Menu` |
| 带标签的表单部分 | 来自 `@expo/ui` 的 `FieldGroup` |
| 可折叠部分 | 来自 `@expo/ui` 的 `Collapsible` |

> **`List` 不是一个虚拟化滚动列表。** 它渲染原生分组表格行——iOS 设置屏幕或表单部分的视觉效果，带有披露指示器和原生行样式。每个 `ListItem` 是 JS 线程上的一个原生节点；行不会被回收。对于任何具有大量或未知长度数据（信息流、搜索结果、目录）的列表，请使用 **`FlatList`** 或 **`FlashList`** 代替。`List` 是短、固定长度组的正确选择：设置屏幕、详情面板的行、固定菜单。

**`BottomSheet` 示例**（用于地图标记详情、操作面板、详情面板——**不是** Reanimated）：

```tsx
import { Host, BottomSheet, Column, Text } from '@expo/ui';
import { useState } from 'react';

export default function MapScreen() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <View style={{ flex: 1 }}>
      <MapView onMarkerPress={() => setIsOpen(true)} />
      <Host>
        <BottomSheet
          isPresented={isOpen}
          onDismiss={() => setIsOpen(false)}
          snapPoints={['half', 'full']}
        >
          <Column>
            <Text>Café name</Text>
            <Text>Address</Text>
          </Column>
        </BottomSheet>
      </Host>
    </View>
  );
}
```

`BottomSheet` 使用 `isPresented`/`onDismiss`——**不是** `isOpened`、`isOpen`、`onIsOpenedChange` 或 `onChange`（这些是 `@gorhom/bottom-sheet` 的属性，并且会静默无操作）。`snapPoints` 接受 `'half'`、`'full'`、`{ fraction: 0.5 }` 或 `{ height: 400 }`，并且是可选的（省略时自动调整为内容大小）。

## 选择方法

按此列表顺序进行，并在第一个满足需求的层停止：

1. **通用组件——从这里开始。** 从 `@expo/ui` 根目录导入。一个组件树在 iOS、Android 和 Web 上未经修改即可运行（Android 上的 Compose，iOS 上的 SwiftUI，Web 上的 `react-native-web`/`react-dom`）。没有平台文件拆分。→ `./references/universal.md`

2. **平台特定（SwiftUI / Jetpack Compose）。** 从 `@expo/ui/swift-ui` 或 `@expo/ui/jetpack-compose` 导入。仅在通用层缺少您需要的组件或修饰符，或者您需要平台特定行为或优化时使用。**缺点：** 您需要编写两个树，并将它们拆分为 `.ios.tsx` / `.android.tsx` 文件（或在 `Platform.OS` 上分支）——需要维护更多代码。

   > **`@expo/ui/swift-ui` 仅限 iOS。`@expo/ui/jetpack-compose` 仅限 Android。** 在在另一个平台上运行的文件中导入其中任何一个会导致运行时崩溃，错误信息为 "Unable to get view config"。将平台特定树隔离在 `components/` 中的 `.ios.tsx` / `.android.tsx` 文件中（永远不会在 `app/` 内部——Expo Router 不支持路由文件的平台扩展），或在常规路由文件中使用 `Platform.OS` 进行保护。`Host` 必须始终从 `@expo/ui`（通用包根目录）导入，而不是从平台特定的子包导入。→ `./references/swift-ui.md` 和 `./references/jetpack-compose.md`

**已经使用 RN 社区 UI 库？** `@expo/ui` 还提供了**即插即用替代方案**——与 API 兼容的流行库（`@gorhom/bottom-sheet`、`@react-native-community/datetimepicker` 等）的替换方案，从 `@expo/ui/community/<name>` 导入。这是一个替换现有依赖的迁移侧路径，而不是通用与平台决策中的步骤。→ `./references/drop-in-replacements.md`

## 参考

按需查阅这些资源：

```
references/
  universal.md             通用 @expo/ui 组件及其使用场景（SDK 56+）
  drop-in-replacements.md  与 RN 社区 UI 库 API 兼容的替代方案
  swift-ui.md              平台特定的 iOS UI：@expo/ui/swift-ui 组件、修饰符、RNHostView、useNativeState
  jetpack-compose.md       平台特定的 Android UI：@expo/ui/jetpack-compose 组件、修饰符、LazyColumn 注意事项、图标、useNativeState
```

## 提交反馈
如果您在技能中遇到错误、误导性或过时的信息，请报告它，以便 Expo 可以改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "expo-ui" "<可操作的反馈>"
```
仅在您有具体且可操作的内容时才提交。尽可能包含所有相关的上下文。
如果 AI 代理反复失败或用户不得不接管 Expo 任务，请加载 `expo-skill-feedback` 技能并遵循其 eval-candidate 流程，而不是重复使用上面的命令。
