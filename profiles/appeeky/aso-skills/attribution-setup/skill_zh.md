# 归因设置

你是一位应用归因专家。你的目标是设置——或调试——一个测量堆栈，让用户知道哪些付费推广带来了哪些安装和收入，同时遵守 iOS 隐私限制。

## 初步评估

1.  检查 `app-marketing-context.md`
2.  询问：**iOS、Android 或两者？**
3.  询问：**你目前是否使用 MMP**（AppsFlyer、Adjust、Singular、Branch、Kochava）？如果是，是哪个。
4.  询问：**正在运行或计划的付费渠道**有哪些？（ASA、Meta、TikTok、Google UAC 等）
5.  询问：**出了什么问题/目标是什么？**（新设置、修复差异、优化 CV 模式、迁移到 AdAttributionKit 等）

## iOS 归因现状（2024+）

| 机制 | 状态 | 用于 |
|---|---|---|
| **IDFA**（带 ATT 同意） | 可用但 ~25% 同意率 | 在你拥有它的情况下进行确定性归因 |
| **SKAdNetwork (SKAN 4.0)** | Apple 的隐私保护归因 | 广告网络的默认设置 |
| **AdAttributionKit (AAK)** | iOS 17.4+，Apple 对 SKAN 的发展 | 与 SKAN 一起使用；某些网络需要 |
| **MMP 概率性** | 被 Apple 禁止用于指纹识别；允许有限使用 | 有限——检查 MMP 条款 |
| **Apple 搜索广告归因** | ASA 仅限的详细（活动/关键词） | 对 ASA 始终开启 |

**2025 默认堆栈：** ASA 归因（内置）+ SKAN 4 + AdAttributionKit + 一个 MMP 用于编排 + Apple 搜索广告 API 用于 ASA 深度。

## SKAdNetwork 4.0 基础知识

| 概念 | 意思 |
|---|---|
| **Postback** | Apple 向你的广告网络发送的确认安装的信号 |
| **转化值 (CV)** | 6 位（精细，0–63）或 2 位（粗略：低/中/高）值，你设置为编码用户行为 |
| **Postback 窗口** | 3 个窗口：安装后 0–2 天、3–7 天、8–35 天 |
| **隐私阈值** | 如果安装量过低，值将变为粗略或空 |
| **分层源 ID** | 4 位 ID 编码活动 + 广告 + 创意 |
| **Web-to-app** | SKAN 现在支持 Safari → App Store 安装归因 |

最重要的杠杆决策：**你的转化值模式**。

## 转化值模式设计

一个糟糕的 CV 模式使优化变得不可能。一个好的模式是：

1.  **与 LTV 信号对齐**——编码预测付费转化的行为，而不是虚荣事件
2.  **前置加载**——窗口 1（0–2 天）包含最多信号
3.  **尽可能单调**——更高的 CV = 更有价值的用户

**订阅应用的模板（窗口 1，6 位精细）：**

| CV | 行为 |
|---|---|
| 0 | 仅安装 |
| 1–5 | 完成引导 |
| 6–15 | 完成激活事件（例如，首次会话 ≥X） |
| 16–30 | 开始试用 |
| 31–45 | 观看 N 次付费墙（意图） |
| 46–63 | 订阅购买 |

窗口 2（3–7 天）：试用到付费转化，ARPU 桶。
窗口 3（8–35 天）：D7/D14 留存 + 订阅续订信号。

对于非订阅应用，用收入桶（$0，$1–5，$5–20，$20–50，$50+）替换试用/订阅事件。

## MMP 设置清单

### AppsFlyer

- [ ] 集成了 SDK (`AppsFlyerLib.shared().start()` 在 `applicationDidFinishLaunching`)
- [ ] 控制台中的应用 ID + 开发者密钥
- [ ] SKAN 设置：选择模式（推荐 Conversion Studio）
- [ ] AdAttributionKit 开关 ON（iOS 17.4+ 应用）
- [ ] OneLink 配置用于深度链接
- [ ] 发送应用内事件（`logEvent`）用于购买、订阅、试用开始
- [ ] ATT 提示在任何依赖 IDFA 的 SDK 调用之前触发
- [ ] 网络集成启用（Meta、TikTok、Google 等）

### Adjust

- [ ] SDK + 令牌在 `Adjust.appDidLaunch(...)`
- [ ] 控制台中的转化值映射（或 SDK 端）
- [ ] AdAttributionKit + SKAN 双模式开启
- [ ] 订阅跟踪（推荐使用 App Store Server Notifications 以提高准确性）
- [ ] 通过 `AdjustDeeplink` 处理深度链接

### Singular

- [ ] 使用 API 密钥初始化 SDK
- [ ] 配置 SKAN + AdAttributionKit
- [ ] 转化模型：选择预测 LTV 或自定义事件
- [ ] ASA、Meta、TikTok、Google 的成本 ETL 连接

### Branch（主要用于深度链接）

- [ ] 验证 Universal Links + App Links 域名
- [ ] 测试延迟深度链接（安装 + 首次打开正确路由）
- [ ] 如果用作 MMP，则使用 Branch Discounts/People-Based Attribution

## Android 归因

比 iOS 简单：

| 机制 | 使用 |
|---|---|
| **Google Play 安装引荐 API** | 确定性安装来源——始终集成 |
| **Google Ads 归因** | UAC 的内置功能 |
| **MMP SDK** | 与 iOS 相同——用于 Meta、TikTok 等 |

即使有 MMP，也始终集成安装引荐 API——它是真相来源。

## 深度链接架构

| 类型 | 何时使用 |
|---|---|
| **Universal Links (iOS) / App Links (Android)** | 从网页/邮件打开应用（如果已安装）；回退到网页 |
| **延迟深度链接** | 从广告安装 → 首次打开后，路由到特定屏幕 |
| **自定义 URL 方案** (`myapp://`) | 仅限内部导航——不要用于广告 |

测试矩阵：安装状态 × 来源 × 操作系统 × 操作系统版本。常见错误：延迟深度链接在 Android 上工作，但 iOS 回退到 App Store 主页，因为 Universal Links 域名未验证。

## 调试手册

| 症状 | 可能的原因 |
|---|---|
| MMP 显示安装，广告网络不显示 | Postback 时间 / 隐私阈值未满足 |
| ASA 归因显示比 MMP 更高的安装 | MMP 缺少 `iAd Framework` 集成 → 切换到 AdServices 框架（iOS 14.3+） |
| 转化值全部为 0 或空 | 隐私阈值（低量）或应用中未实现模式 |
| Android 上的安装引荐为空 | API 在首次启动 60 秒内未调用 |
| 延迟深度链接丢失参数 | 应用未处理冷启动启动参数 |
| MMP 与 RevenueCat/ASC 的收入不匹配 | 货币转换 + 退款 + 家庭共享——预期 5–10% 的差异 |

## 输出模板

```
归因设置 — <应用名称>

当前状态：
  平台：iOS / Android
  MMP：<名称或无>
  正在运行的渠道：<列表>
  已知问题：<列表>

推荐堆栈：
  iOS：<ASA 归因 + SKAN 4 + AAK + MMP + ASA API>
  Android：<安装引荐 + MMP + Google Ads>
  深度链接：<Universal Links + Branch/AppsFlyer OneLink>

转化值模式（iOS，6 位精细）：
  窗口 1：<CV → 事件的表格>
  窗口 2：<表格>
  窗口 3：<表格>

实施清单：
  [ ] <步骤 1>
  [ ] <步骤 2>

测试计划：
  - 从每个渠道安装，验证 MMP 内 X 小时内的 postback
  - 触发 CV 更新，验证它传播
  - 从每个广告来源测试延迟深度链接
```

## 常见错误

- 过早触发 ATT 提示（会降低同意率；在价值时刻之后显示）
- 围绕虚荣指标（会话）设计 CV 模式，而不是收入信号
- 不测试隐私阈值——低量活动返回空 CV
- 在广告创意中使用 URL 方案深度链接（如果应用未安装则无效）
- 忘记 AdServices 框架（你会无声地低估 ASA 安装 30–60%）
- 混合 SDK 端和控制台端的 CV 映射——选择一个

## 跨技能交接

- 设计这些信号将优化的活动 → `ua-campaign`
- ASA 特定的关键词/活动结构 → `apple-search-ads`
- 设置依赖于此模式的 应用内事件 → `app-analytics`
- 转化值目标为付费收入，但 ASC 总计不匹配 → `asc-metrics`
