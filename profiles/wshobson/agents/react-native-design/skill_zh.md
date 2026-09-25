# React Native 设计

掌握 React Native 样式模式、React Navigation 和 Reanimated 3，以构建高性能、跨平台的移动应用程序，并提供原生质量的用户体验。

## 使用此技能的场景

- 使用 React Native 构建跨平台移动应用程序
- 使用 React Navigation 6+ 实现导航
- 使用 Reanimated 3 创建高性能动画
- 使用 StyleSheet 和 styled-components 样式化组件
- 为不同屏幕尺寸构建响应式布局
- 实现平台特定的设计（iOS/Android）
- 使用 Gesture Handler 创建手势驱动的交互
- 优化 React Native 性能

## 详细部分：核心概念

最初是此 SKILL.md 中 6471 字节的部分。已移动到 `references/details.md` 以适应 Codex 的 8 KB 技能主体限制。

## 快速入门组件

```typescript
import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  Image,
} from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
} from 'react-native-reanimated';

interface ItemCardProps {
  title: string;
  subtitle: string;
  imageUrl: string;
  onPress: () => void;
}

const AnimatedPressable = Animated.createAnimatedComponent(Pressable);

export function ItemCard({ title, subtitle, imageUrl, onPress }: ItemCardProps) {
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return (
    <AnimatedPressable
      style={[styles.card, animatedStyle]}
      onPress={onPress}
      onPressIn={() => { scale.value = withSpring(0.97); }}
      onPressOut={() => { scale.value = withSpring(1); }}
    >
      <Image source={{ uri: imageUrl }} style={styles.image} />
      <View style={styles.content}>
        <Text style={styles.title} numberOfLines={1}>
          {title}
        </Text>
        <Text style={styles.subtitle} numberOfLines={2}>
          {subtitle}
        </Text>
      </View>
    </AnimatedPressable>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  image: {
    width: '100%',
    height: 160,
    backgroundColor: '#f3f4f6',
  },
  content: {
    padding: 16,
    gap: 4,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
  },
  subtitle: {
    fontSize: 14,
    color: '#6b7280',
    lineHeight: 20,
  },
});
```

## 最佳实践

1. **使用 TypeScript**：定义导航和属性类型以实现类型安全
2. **缓存组件**：使用 `React.memo` 和 `useCallback` 防止不必要的重新渲染
3. **在 UI 线程上运行动画**：使用 Reanimated 工作集实现 60fps 动画
4. **避免内联样式**：使用 `StyleSheet.create` 以提高性能
5. **处理安全区域**：使用 `SafeAreaView` 或 `useSafeAreaInsets`
6. **在真实设备上测试**：模拟器/模拟器的性能与真实设备不同
7. **使用 FlatList 处理列表**：永远不要使用 ScrollView 与 map 结合用于长列表
8. **平台特定代码**：使用 `Platform.select` 处理 iOS/Android 差异

## 常见问题

- **手势冲突**：使用 `GestureDetector` 包裹手势并使用 `simultaneousHandlers`
- **导航类型错误**：为所有导航器定义 `ParamList` 类型
- **动画卡顿**：使用 `runOnUI` 工作集将动画移至 UI 线程
- **内存泄漏**：在 `useEffect` 中取消动画并进行清理
- **字体加载**：使用 `expo-font` 或 `react-native-asset` 加载自定义字体
- **安全区域问题**：在带凹口的设备（iPhone、带凹口的 Android）上测试
