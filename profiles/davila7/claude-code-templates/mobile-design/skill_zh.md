# 移动设计系统

> **理念：** 触摸优先。注重电池续航。尊重平台。离线可用。
> **核心原则：** 移动设备不是小型的桌面。思考移动设备的限制，询问平台选择。

---

## 🔧 运行时脚本

执行这些脚本进行验证（不要读取，直接运行）：

| 脚本 | 目的 | 使用方式 |
|------|---------|-------|
| `scripts/mobile_audit.py` | 移动用户体验与触摸审核 | `python scripts/mobile_audit.py <项目路径>` |

---

## 🔴 强制要求：工作前必须阅读参考文件！

**⛔ 在阅读相关文件之前，请勿开始开发：**

### 通用（必须阅读）

| 文件 | 内容 | 状态 |
|------|---------|--------|
| **[mobile-design-thinking.md](mobile-design-thinking.md)** | **⚠️ 反记忆化：强制思考，防止AI默认设置** | **⬜ 关键第一步** |
| **[touch-psychology.md](touch-psychology.md)** | **Fitts定律、手势、触觉反馈、拇指区域** | **⬜ 关键** |
| **[mobile-performance.md](mobile-performance.md)** | **RN/Flutter性能、60fps、内存** | **⬜ 关键** |
| **[mobile-backend.md](mobile-backend.md)** | **推送通知、离线同步、移动API** | **⬜ 关键** |
| **[mobile-testing.md](mobile-testing.md)** | **测试金字塔、端到端、平台特定** | **⬜ 关键** |
| **[mobile-debugging.md](mobile-debugging.md)** | **原生与JS调试、Flipper、Logcat** | **⬜ 关键** |
| [mobile-navigation.md](mobile-navigation.md) | Tab/Stack/Drawer、深度链接 | ⬜ 阅读 |
| [mobile-typography.md](mobile-typography.md) | 系统字体、动态类型、无障碍访问 | ⬜ 阅读 |
| [mobile-color-system.md](mobile-color-system.md) | OLED、深色模式、电池感知 | ⬜ 阅读 |
| [decision-trees.md](decision-trees.md) | 框架/状态/存储选择 | ⬜ 阅读 |

> 🧠 **mobile-design-thinking.md是优先级最高的！** 此文件确保AI进行思考，而不是使用记忆模式。

### 平台特定（根据目标阅读）

| 平台 | 文件 | 内容 | 阅读时间 |
|----------|------|---------|--------------|
| **iOS** | [platform-ios.md](platform-ios.md) | 人机界面指南、SF Pro、SwiftUI模式 | 为iPhone/iPad构建 |
| **Android** | [platform-android.md](platform-android.md) | Material Design 3、Roboto、Compose模式 | 为Android构建 |
| **跨平台** | 上述两者 | 平台差异点 | React Native / Flutter |

> 🔴 **为iOS构建 → 首先阅读platform-ios.md！**
> 🔴 **为Android构建 → 首先阅读platform-android.md！**
> 🔴 **跨平台构建 → 两者都阅读并应用条件平台逻辑！**

---

## ⚠️ 关键：假设前必须询问（强制要求）

> **停止！如果用户的请求是开放式的，不要默认使用你喜欢的方案。**

### 如果未指定，你必须询问：

| 方面 | 询问 | 原因 |
|--------|-----|-----|
| **平台** | "iOS、Android还是两者？" | 影响所有设计决策 |
| **框架** | "React Native、Flutter还是原生？" | 决定模式和工具 |
| **导航** | "Tab栏、抽屉还是基于栈？" | 核心用户体验决策 |
| **状态** | "状态管理是什么？（Zustand/Redux/Riverpod/BLoC？）" | 架构基础 |
| **离线** | "这需要离线工作吗？" | 影响数据策略 |
| **目标设备** | "仅手机还是支持平板电脑？" | 布局复杂度 |

### ⛔ AI移动反模式（禁止列表）

> 🚫 **这些都是AI默认倾向，必须避免！**

#### 性能罪过

| ❌ 永远不要做 | 为什么不对 | ✅ 永远要 |
|-------------|----------------|--------------|
| **使用ScrollView处理长列表** | 渲染所有项，内存爆炸 | 使用`FlatList` / `FlashList` / `ListView.builder` |
| **内联renderItem函数** | 每次渲染创建新函数，所有项重新渲染 | `useCallback` + `React.memo` |
| **缺少keyExtractor** | 基于索引的键在重新排序时会导致错误 | 来自数据的唯一、稳定的ID |
| **跳过getItemLayout** | 异步布局导致滚动卡顿 | 当项具有固定高度时提供 |
| **到处使用setState()** | 不必要的组件重建 | 针对性状态，`const`构造函数 |
| **原生驱动：false** | 动画被JS线程阻塞 | `useNativeDriver: true`始终 |
| **生产环境中使用console.log** | 严重阻塞JS线程 | 发布构建前移除 |
| **跳过React.memo/const** | 每个项在任何变化时都会重新渲染 | 始终记忆列表项 |

#### 触摸/用户体验罪过

| ❌ 永远不要做 | 为什么不对 | ✅ 永远要 |
|-------------|----------------|--------------|
| **触摸目标<44px** | 难以准确点击，令人沮丧 | 最小44pt（iOS）/48dp（Android） |
| **目标之间间距<8px** | 容易误触相邻项 | 最小8-12px间隙 |
| **仅手势交互** | 排除运动障碍用户 | 始终提供按钮替代方案 |
| **没有加载状态** | 用户认为应用崩溃 | 始终显示加载反馈 |
| **没有错误状态** | 用户卡住，没有恢复路径 | 显示错误并提供重试选项 |
| **没有离线处理** | 网络丢失时崩溃/阻塞 | 平滑降级，缓存数据 |
| **忽略平台惯例** | 用户困惑，肌肉记忆断裂 | iOS感觉像iOS，Android感觉像Android |

#### 安全罪过

| ❌ 永远不要做 | 为什么不对 | ✅ 永远要 |
|-------------|----------------|--------------|
| **Token在AsyncStorage** | 容易访问，在Root设备上被盗 | `SecureStore` / `Keychain` / `EncryptedSharedPreferences` |
| **硬编码API密钥** | 从APK/IPA逆向工程 | 环境变量，安全存储 |
| **跳过SSL证书绑定** | 可能存在中间人攻击 | 在生产中绑定证书 |
| **记录敏感数据** | 日志可能被提取 | 永远不要记录Token、密码、PII |

#### 架构罪过

| ❌ 永远不要做 | 为什么不对 | ✅ 永远要 |
|-------------|----------------|--------------|
| **UI中包含业务逻辑** | 难以测试、难以维护 | 服务层分离 |
| **所有内容使用全局状态** | 不必要的重新渲染、复杂性 | 默认本地状态，需要时提升 |
| **深度链接作为事后想法** | 通知、分享失效 | 从第一天就规划深度链接 |
| **跳过dispose/清理** | 内存泄漏、僵尸监听器 | 清理订阅、定时器 |

---

## 📱 平台决策矩阵

### 何时统一 vs 分离

```
                    统一（两平台相同）          分离（平台特定）
                    ───────────────────           ──────────────────────────
业务逻辑      ✅ 始终                     -
数据层        ✅ 始终                     -
核心功能      ✅ 始终                     -

导航          -                             ✅ iOS: 边缘滑动，Android: 返回按钮
手势            -                             ✅ 平台原生感觉
图标               -                             ✅ SF符号 vs Material图标
日期选择器        -                             ✅ 原生选择器感觉正确
模态/Sheet       -                             ✅ iOS: 底部Sheet vs Android: 对话框
字体             -                             ✅ SF Pro vs Roboto（或自定义）
错误对话框        -                             ✅ 平台惯例的警报
```

### 快速参考：平台默认值

| 元素 | iOS | Android |
|---------|-----|---------|
| **主要字体** | SF Pro / SF Compact | Roboto |
| **最小触摸目标** | 44pt × 44pt | 48dp × 48dp |
| **返回导航** | 边缘滑动左 | 系统返回按钮/手势 |
| **底部Tab图标** | SF符号 | Material符号 |
| **操作表** | 从底部UIActionSheet | 底部Sheet / 对话框 |
| **进度** | 旋转器 | 线性进度（Material） |
| **下拉刷新** | Native UIRefreshControl | SwipeRefreshLayout |

---

## 🧠 移动用户体验心理学（快速参考）

### Fitts定律用于触摸

```
桌面：光标精确（1px）
移动：手指不精确（~7mm接触区域）

→ 触摸目标必须≥44-48px最小
→ 重要操作在拇指区域（屏幕底部）
→ 破坏性操作远离容易触及的位置
```

### 拇指区域（单手使用）

```
┌─────────────────────────────┐
│      难以触及              │ ← 导航、菜单、返回
│        (拉伸)              │
├─────────────────────────────┤
│      可以触及              │ ← 次要操作
│       (自然)             │
├─────────────────────────────┤
│      容易触及              │ ← 主要CTA、Tab栏
│    (拇指自然弧度)    │ ← 主要内容交互
└─────────────────────────────┘
        [  HOME  ]
```

### 移动特定认知负荷

| 桌面 | 移动差异 |
|---------|-------------------|
| 多个窗口 | 一次一个任务 |
| 键盘快捷键 | 触摸手势 |
| 悬停状态 | 无悬停（点击或无） |
| 大视口 | 有限空间，垂直滚动 |
| 稳定注意力 | 不断被中断 |

深入指南：[touch-psychology.md](touch-psychology.md)

---

## ⚡ 性能原则（快速参考）

### React Native关键规则

```typescript
// ✅ 正确：记忆化的renderItem + React.memo包装
const ListItem = React.memo(({ item }: { item: Item }) => (
  <View style={styles.item}>
    <Text>{item.title}</Text>
  </View>
));

const renderItem = useCallback(
  ({ item }: { item: Item }) => <ListItem item={item} />,
  []
);

// ✅ 正确：带有所有优化的FlatList
<FlatList
  data={items}
  renderItem={renderItem}
  keyExtractor={(item) => item.id}  // 来自数据的稳定ID，不是索引
  getItemLayout={(data, index) => ({
    length: ITEM_HEIGHT,
    offset: ITEM_HEIGHT * index,
    index,
  })}
  removeClippedSubviews={true}
  maxToRenderPerBatch={10}
  windowSize={5}
/>
```

### Flutter关键规则

```dart
// ✅ 正确：const构造函数防止重建
class MyWidget extends StatelessWidget {
  const MyWidget({super.key}); // CONST!

  @override
  Widget build(BuildContext context) {
    return const Column( // CONST!
      children: [
        Text('静态内容'),
        MyConstantWidget(),
      ],
    );
  }
}

// ✅ 正确：针对性状态使用ValueListenableBuilder
ValueListenableBuilder<int>(
  valueListenable: counter,
  builder: (context, value, child) => Text('$value'),
  child: const ExpensiveWidget(), // 不会重建!
)
```

### 动画性能

```
GPU加速（快）：     CPU限制（慢）:
├── transform               ├── width, height
├── opacity                 ├── top, left, right, bottom
└── (仅使用这些)        ├── margin, padding
                            └── (避免动画这些)
```

完整指南：[mobile-performance.md](mobile-performance.md)

---

## 📝 检查点（任何移动工作前强制要求）

> **在编写任何移动代码之前，你必须完成此检查点：**

```
🧠 检查点:

平台:   [ iOS / Android / 两者 ]
框架:  [ React Native / Flutter / SwiftUI / Kotlin ]
已阅读文件: [ 列出你已阅读的技能文件 ]

3原则我将应用:
1. _______________
2. _______________
3. _______________

我将避免的反模式:
1. _______________
2. _______________
```

**示例:**
```
🧠 检查点:

平台:   iOS + Android (跨平台)
框架:  React Native + Expo
已阅读文件: touch-psychology.md, mobile-performance.md, platform-ios.md, platform-android.md

3原则我将应用:
1. FlatList与React.memo + useCallback用于所有列表
2. 48px触摸目标，拇指区域为主要CTA
3. 平台特定导航（iOS边缘滑动，Android返回按钮）

我将避免的反模式:
1. 列表使用ScrollView → FlatList
2. 内联renderItem → 记忆化
3. AsyncStorage用于Token → SecureStore
```

> 🔴 **无法填写检查点？→ 回去阅读技能文件。**

---

## 🔧 框架决策树

```
你在构建什么？
        │
        ├── 需要OTA更新+快速迭代+网页团队
        │   └── ✅ React Native + Expo
        │
        ├── 需要像素级自定义UI+性能关键
        │   └── ✅ Flutter
        │
        ├── 深度原生功能+单平台专注
        │   ├── iOS仅 → SwiftUI
        │   └── Android仅 → Kotlin + Jetpack Compose
        │
        ├── 现有RN代码库+新功能
        │   └── ✅ React Native (裸流程)
        │
        └── 企业+现有Flutter代码库
            └── ✅ Flutter
```

完整决策树：[decision-trees.md](decision-trees.md)

---

## 📋 开发前检查清单

### 开始任何移动项目前

- [ ] **平台确认？** (iOS / Android / 两者)
- [ ] **框架选择？** (RN / Flutter / 原生)
- [ ] **导航模式确定？** (Tabs / Stack / Drawer)
- [ ] **状态管理选择？** (Zustand / Redux / Riverpod / BLoC)
- [ ] **离线需求已知？**
- [ ] **从第一天就规划深度链接？**
- [ ] **目标设备定义？** (手机 / 平板 / 两者)

### 每个屏幕前

- [ ] **触摸目标 ≥ 44-48px？**
- [ ] **主要CTA在拇指区域？**
- [ ] **存在加载状态？**
- [ ] **存在错误状态并带重试选项？**
- [ ] **考虑离线处理？**
- [ ] **遵循平台惯例？**

### 发布前

- [ ] **移除console.log？**
- [ ] **使用SecureStore处理敏感数据？**
- [ ] **启用SSL证书绑定？**
- [ ] **列表优化（记忆化、keyExtractor）？**
- [ ] **卸载时进行内存清理？**
- [ ] **在低端设备上测试？**
- [ ] **所有交互元素都有无障碍标签？**

---

## 📚 参考文件

针对特定领域进行更深入的指导：

| 文件 | 使用时间 |
|------|-------------|
| [mobile-design-thinking.md](mobile-design-thinking.md) | **首先！反记忆化，强制基于上下文的思考** |
| [touch-psychology.md](touch-psychology.md) | 理解触摸交互、Fitts定律、手势设计 |
| [mobile-performance.md](mobile-performance.md) | 优化RN/Flutter、60fps、内存/电池 |
| [platform-ios.md](platform-ios.md) | iOS特定设计、HIG合规 |
| [platform-android.md](platform-android.md) | Android特定设计、Material Design 3 |
| [mobile-navigation.md](mobile-navigation.md) | 导航模式、深度链接 |
| [mobile-typography.md](mobile-typography.md) | 字体比例、系统字体、无障碍访问 |
| [mobile-color-system.md](mobile-color-system.md) | OLED优化、深色模式、电池 |
| [decision-trees.md](decision-trees.md) | 框架、状态、存储决策 |

---

> **记住：** 移动用户不耐烦、被中断、在小屏幕上使用不精确的手指。为最差条件设计：坏网络、单手、强光、低电量。如果它在这些条件下工作，它就在任何地方都能工作。
