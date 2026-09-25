# 碰撞分析

您帮助进行问题分类、优先级排序和减少应用崩溃，并了解崩溃率如何影响应用商店的发现性和评分。

## 崩溃率为何是ASO信号

- **应用商店排名** — 苹果的算法会惩罚崩溃率高的应用
- **应用商店推荐** — 高崩溃率会导致编辑推荐被取消
- **评分** — 崩溃是导致1星评价的首要原因
- **留存率** — 首次使用时崩溃会摧毁第1天留存率

**目标：** 无崩溃会话 > 99.5% | 无崩溃用户 > 99%

## 工具

| 工具 | 提供的功能 | 设置 |
|------|-----------------|-------|
| **Firebase Crashlytics** | 实时崩溃、ANRs、符号化堆栈跟踪 | 添加 `FirebaseCrashlytics` pod/SPM 包 |
| **App Store Connect** | 崩溃率趋势、每会话崩溃数 | 内置，无需代码 |
| **Xcode Organizer** | 来自TestFlight和应用商店的聚合崩溃日志 | Xcode → 窗口 → 组织器 → 崩溃 |
| **MetricKit** | 设备诊断、卡顿率、启动时间 | iOS 13+，自动 |

**推荐：** Crashlytics（实时警报+搜索）+ App Store Connect（趋势验证）

## Crashlytics设置

### iOS (Swift)

```swift
// AppDelegate或@main App结构体
import FirebaseCore
import FirebaseCrashlytics

@main
struct MyApp: App {
    init() {
        FirebaseApp.configure()
        // Crashlytics自动初始化
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

## 问题分类框架

并非所有崩溃都相同。按影响优先级排序：

**优先级分数 = 崩溃频率 × 影响用户数 × 用户群组权重**

| 优先级 | 标准 | 响应时间 |
|----------|---------|---------------|
| P0 — 严重 | 启动时崩溃/结账/核心功能崩溃；>1%的会话 | 今天修复 |
| P1 — 高 | 常见流程中的崩溃；>0.1%的会话 | 本次发布修复 |
| P2 — 中等 | 边缘案例崩溃；<0.1%的会话 | 下次发布修复 |
| P3 — 低 | 罕见、非阻塞崩溃；<0.01%的会话 | 积压 |

### Crashlytics仪表盘问题分类

1. 按**"影响"**（受影响的唯一用户数）排序，而不是频率
2. 分组：`引导流程`、`结账`、`核心功能`、`后台`、`启动`
3. 为前3-5个问题分配P0/P1
4. 为任何影响>0.5%用户的任何问题在Crashlytics中设置**速度警报**

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
1. 在Xcode中打开文件和行（`UserProfileVC.swift:87`）
2. 检查该点可能为nil的内容
3. 使用用户上下文（OS版本、设备、屏幕）重现
4. 在修复前编写失败的测试

## 符号化

如果上传了dSYMs，Crashlytics会自动符号化。如果您看到未符号化的跟踪：

```bash
# 手动上传dSYMs
./Pods/FirebaseCrashlytics/upload-symbols -gsp GoogleService-Info.plist -p ios MyApp.app.dSYM
```

对于启用Bitcode的构建，从App Store Connect → 活动 → 构建 → dSYMs下载dSYMs。

## App Store Connect崩溃数据

- **App Store Connect → 应用分析 → 崩溃** — 每个版本的崩溃率趋势
- 比较每次发布前后的崩溃率
- 特定版本上的峰值 = 该版本中的回归

**崩溃率公式：** 崩溃数 / 会话数 × 100

## 最大限度减少影响范围的发布策略

使用分阶段发布来在全面推广前捕获崩溃：

**iOS：** App Store Connect → 版本 → 分阶段发布（7天推广：1% → 2% → 5% → 10% → 20% → 50% → 100%）

**Android：** Play Console → 生产 → 管理发布 → 推广百分比

**规则：** 在每个阶段监控Crashlytics 24小时。如果崩溃率增加>0.2%，则暂停推广。

## 响应崩溃驱动的1星评价

1. 确定出现崩溃相关1星评价的应用版本
2. 修复崩溃
3. 回复每个崩溃相关的评价："已在版本X.X修复 — 请更新"
4. 更新发布后，使用`rating-prompt-strategy`恢复评分

## 输出格式

### 崩溃审计报告

```
稳定性报告 — [应用名称] v[版本] ([周期])

无崩溃会话：[X]%  (目标：>99.5%)
无崩溃用户：    [X]%  (目标：>99%)
主要崩溃问题：

P0问题（立即修复）：
  #1 [异常类型] — [X]用户，[X]%的会话
     文件：[文件名:行]
     原因：[假设]
     修复：[具体操作]

P1问题（本次发布）：
  #2 [异常类型] — [X]用户，[X]%的会话
     ...

行动计划：
  今天：     修复P0问题#1 → 发布热修复
  本周：     修复P1问题#2、#3 → 包含在v[X.X]中
  监控：     在0.5%会话阈值处设置速度警报
```

## 相关技能

- `app-analytics` — 完整分析栈；Crashlytics只是其中一部分
- `rating-prompt-strategy` — 修复崩溃驱动的1星评价后恢复评分
- `review-management` — 回复崩溃相关的评价
- `retention-optimization` — 第1天崩溃会摧毁留存指标
- `app-store-featured` — 崩溃率>2%会导致编辑推荐被取消
