---
name: crash-analytics
description: 当用户希望监控、处理或降低其应用的崩溃率时——包括设置 Crashlytics、确定优先修复哪些崩溃、解读崩溃数据以及了解崩溃如何影响 App Store 排名。在用户提及“崩溃”、“Crashlytics”、“崩溃率”、“ANR”、“应用无响应”、“无崩溃会话”、“无崩溃用户”、“符号化”、“稳定性”、“Firebase 崩溃”、“应用崩溃”或“崩溃报告”时使用。关于整体分析设置，请参阅 app-analytics。
---

# 碰撞分析

您帮助进行分类、优先排序并减少应用程序崩溃，并了解崩溃率如何影响 App Store 的发现能力和评分。

## 崩溃率为何是 ASO 信号

- **App Store 排名** — Apple 的算法会惩罚崩溃率高的应用程序
- **App Store 推荐** — 高崩溃率会导致编辑考虑排除
- **评分** — 崩溃是导致 1 星评价的首要原因
- **留存率** — 首次会话中的崩溃会摧毁第 1 天的留存率

**目标：** 无崩溃会话 > 99.5% | 无崩溃用户 > 99%

## 工具

| 工具 | 提供内容 | 设置 |
|------|--------|------|
| **Firebase Crashlytics** | 实时崩溃、ANRs、符号化堆栈跟踪 | 添加 `FirebaseCrashlytics` pod/SPM 包 |
| **App Store Connect** | 崩溃率趋势、每会话崩溃数 | 内置，无需代码 |
| **Xcode Organizer** | 来自 TestFlight + App Store 的聚合崩溃日志 | Xcode → 窗口 → Organizer → 崩溃 |
| **MetricKit** | 设备诊断、卡顿率、启动时间 | iOS 13+，自动 |

**推荐：** Crashlytics（实时警报 + 搜索）+ App Store Connect（趋势验证）

## Crashlytics 设置

### iOS (Swift)

```swift
// AppDelegate 或 @main App 结构体
import FirebaseCore
import FirebaseCrashlytics

@main
struct MyApp: App {
    init() {
        FirebaseApp.configure()
        // Crashlytics 会自动初始化
    }
}
```

### 非致命错误（不崩溃时跟踪）

```swift
// 记录非致命错误
Crashlytics.crashlytics().record(error: error)

// 记录用于调试上下文的自定义键
Crashlytics.crashlytics().setCustomValue(userId, forKey: "user_id")
Crashlytics.crashlytics().setCustomValue(screenName, forKey: "current_screen")
```

### Android (Kotlin)

```kotlin
// build.gradle (app)
implementation("com.google.firebase:firebase-crashlytics:18.x.x")

// 无需额外代码 — 自动捕获未处理的异常
// 对于非致命：
FirebaseCrashlytics.getInstance().recordException(throwable)
```

## 分类框架

并非所有崩溃都相同。按影响优先排序：

**优先级分数 = 崩溃频率 × 影响用户数 × 用户群组权重**

| 优先级 | 标准 | 响应时间 |
|------|------|----------|
| P0 — 严重 | 启动时崩溃 / 结账 / 核心功能；>1% 的会话 | 今天修复 |
| P1 — 高 | 常见流程中的崩溃；>0.1% 的会话 | 本次发布修复 |
| P2 — 中等 | 边缘案例崩溃；<0.1% 的会话 | 下次发布修复 |
| P3 — 低 | 罕见、非阻塞崩溃；<0.01% 的会话 | 积压 |

### Crashlytics 仪表板分类

1. 按 **"影响"**（受影响的唯一用户数）排序，而不是频率
2. 分组：`引导流程`、`结账`、`核心功能`、`后台`、`启动`
3. 为前 3-5 个问题分配 P0/P1
4. 为任何影响 >0.5% 用户的问题在 Crashlytics 中设置 **速度警报**

## 阅读崩溃报告

```
致命异常：com.example.NullPointerException
  at com.example.UserProfileVC.loadData:87
  at com.example.HomeVC.viewDidLoad:45

键：
  user_id: 12345
  current_screen: "home"
  app_version: "2.3.1"
  os_version: "iOS 17.3"
```

**调试步骤：**
1. 在 Xcode 中打开文件和行 (`UserProfileVC.swift:87`)
2. 检查该点可能为空的值
3. 使用用户上下文（OS 版本、设备、屏幕）重现
4. 在修复前编写失败的测试

## 符号化

如果上传了 dSYMs，Crashlytics 会自动符号化。如果您看到未符号化的跟踪：

```bash
# 手动上传 dSYMs
./Pods/FirebaseCrashlytics/upload-symbols -gsp GoogleService-Info.plist -p ios MyApp.app.dSYM
```

对于启用 Bitcode 的构建，从 App Store Connect → 活动 → 构建 → dSYMs 下载 dSYMs。

## App Store Connect 崩溃数据

- **App Store Connect → 应用分析 → 崩溃** — 每个版本的崩溃率趋势
- 比较每次发布前后的崩溃率
- 特定版本上的峰值 = 该发布的回归

**崩溃率公式：** 崩溃数 / 会话数 × 100

## 最大限度减少影响范围的发布策略

使用分阶段发布来在全面推广前捕获崩溃：

**iOS：** App Store Connect → 版本 → 分阶段发布（7 天推广：1% → 2% → 5% → 10% → 20% → 50% → 100%）

**Android：** Play Console → 生产 → 管理发布 → 推广百分比

**规则：** 在每个阶段监控 Crashlytics 24 小时。如果崩溃率增加 >0.2%，则暂停推广。

## 响应崩溃驱动的 1 星评价

1. 确定出现崩溃相关 1 星评价的应用版本
2. 修复崩溃
3. 回复每个崩溃相关的评价："已在版本 X.X 修复 — 请更新"
4. 更新发布后，使用 `rating-prompt-strategy` 恢复评分

## 输出格式

### 崩溃审计报告

```
稳定性报告 — [应用名称] v[版本] ([周期])

无崩溃会话：[X]%  (目标：>99.5%)
无崩溃用户：    [X]%  (目标：>99%)
顶级崩溃问题：

P0 问题（立即修复）：
  #1 [异常类型] — [X] 用户，[X]% 的会话
     文件：[文件名:行]
     原因：[假设]
     修复：[具体操作]

P1 问题（本次发布）：
  #2 [异常类型] — [X] 用户，[X]% 的会话
     ...

行动计划：
  今天：     修复 P0 问题 #1 → 发布热修复
  本周：     修复 P1 问题 #2、#3 → 包含在 v[X.X] 中
  监控：     在 0.5% 会话阈值处设置速度警报
```

## 相关技能

- `app-analytics` — 完整的分析堆栈；Crashlytics 只是其中一部分
- `rating-prompt-strategy` — 修复崩溃驱动的 1 星评价后恢复评分
- `review-management` — 回复崩溃相关的评价
- `retention-optimization` — 第 1 天的崩溃会摧毁留存指标
- `app-store-featured` — 崩溃率 > 2% 会排除编辑推荐
