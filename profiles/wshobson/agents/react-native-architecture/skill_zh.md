# React Native 架构

使用 Expo 进行 React Native 开发的生产就绪模式，包括导航、状态管理、原生模块和离线优先架构。

## 何时使用此技能

- 开始新的 React Native 或 Expo 项目
- 实现复杂的导航模式
- 集成原生模块和平台 API
- 构建离线优先移动应用
- 优化 React Native 性能
- 为移动发布设置 CI/CD

## 核心概念

### 1. 项目结构

```
src/
├── app/                    # Expo Router 屏幕
│   ├── (auth)/            # 认证组
│   ├── (tabs)/            # 标签导航
│   └── _layout.tsx        # 根布局
├── components/
│   ├── ui/                # 可重用 UI 组件
│   └── features/          # 特定功能的组件
├── hooks/                 # 自定义钩子
├── services/              # API 和原生服务
├── stores/                # 状态管理
├── utils/                 # 工具
└── types/                 # TypeScript 类型
```

### 2. Expo 与原生 React Native

| 功能            | Expo           | 原生 RN        |
| -------------- | -------------- | -------------- |
| 设置复杂度   | 低            | 高           |
| 原生模块     | EAS 构建      | 手动链接      |
| OTA 更新        | 内置          | 手动设置      |
| 构建服务      | EAS            | 自定义 CI      |
| 自定义原生代码 | 配置插件      | 直接访问      |

## 快速入门

```bash
# 创建新的 Expo 项目
npx create-expo-app@latest my-app -t expo-template-blank-typescript

# 安装必要的依赖
npx expo install expo-router expo-status-bar react-native-safe-area-context
npx expo install @react-native-async-storage/async-storage
npx expo install expo-secure-store expo-haptics
```

```typescript
// app/_layout.tsx
import { Stack } from 'expo-router'
import { ThemeProvider } from '@/providers/ThemeProvider'
import { QueryProvider } from '@/providers/QueryProvider'

export default function RootLayout() {
  return (
    <QueryProvider>
      <ThemeProvider>
        <Stack screenOptions={{ headerShown: false }}>
          <Stack.Screen name="(tabs)" />
          <Stack.Screen name="(auth)" />
          <Stack.Screen name="modal" options={{ presentation: 'modal' }} />
        </Stack>
      </ThemeProvider>
    </QueryProvider>
  )
}
```

## 详细模式和实例

详细模式文档位于 `references/details.md`。当上层的导航层级不足时，请阅读该文件。

## 最佳实践

### 应该做

- **使用 Expo** - 更快的开发速度、OTA 更新、管理的原生代码
- **FlashList 而不是 FlatList** - 长列表更好的性能
- **缓存组件** - 防止不必要的重新渲染
- **使用 Reanimated** - 在原生线程上实现 60fps 动画
- **在真实设备上测试** - 模拟器会遗漏现实世界的问题

### 不应该做

- **不要内联样式** - 使用 StyleSheet.create 以提高性能
- **不要在渲染中获取数据** - 使用 useEffect 或 React Query
- **不要忽略平台差异** - 在 iOS 和 Android 上进行测试
- **不要在代码中存储密钥** - 使用环境变量
- **不要跳过错误边界** - 移动端崩溃是不可原谅的
