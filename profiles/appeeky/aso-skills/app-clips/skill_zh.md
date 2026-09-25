# App Clips

您帮助规划、实施和优化 App Clips——轻量级的 iOS 体验（最大 15MB），用户无需安装完整应用即可即时启动。

## App Clips 是什么

App Clips 是您应用的小型、专注的部分，用户无需下载完整应用即可使用。它们出现在：

- **App Store 搜索结果**——与您的完整应用一起显示
- **网站上的智能应用横幅**
- **二维码**和 App Clip 代码（物理 NFC/QR）
- **Safari**——访问链接 URL 时
- **信息**——在 iMessages 中共享 URL 时
- **地图**——针对基于位置的企业
- **附近**——物理世界中的 NFC 和视觉代码
- **Siri 建议**

## 大小限制

| 目标 | 限制 |
|------|------|
| App Clip 二进制文件 | **15MB** 最大（精简，按需下载） |
| 应用本身 | 无变化 |

这迫使您仅发布核心体验。

## 最佳使用场景

| 应用类型 | App Clip 体验 |
|----------|---------------|
| 停车/交通 | 支付停车费或购买票务 |
| 餐厅 | 查看菜单、点餐或支付 |
| 零售 | 产品预览或会员卡 |
| 健身 | 尝试单个锻炼 |
| 游戏 | 玩演示关卡 |
| 金融 | 计算器或快速报价 |
| 活动 | 购买门票或签到 |
| 实用工具 | 一次性使用核心功能 |

**关键问题：** 什么是最小体验，可以展示您应用的核心价值？

## App Store 中的 App Clip 发现

App Clips 作为独立卡片出现在 **App Store 搜索**中，位于您的完整应用结果下方——标记为“App Clip”并带有“打开”按钮（不是“获取”）。

- 点击“打开”的用户可即时启动 App Clip
- 使用后，他们会看到横幅：“获取完整应用”
- 从 App Clip 用户到完整安装的转化率通常比冷启动自然流量高 **3–5 倍**

**ASO 影响：** App Clip 卡片继承您应用的标题和描述元数据。优化主列表也能提高 App Clip 的可发现性。

## 技术要求

### App Clip 中应包含的内容

- 仅核心体验
- 使用 Apple Pay 或 Apple Sign in 进行身份验证（无需完整账户创建）
- 无 App Clip 独占内容——卡片中的所有内容都应在完整应用中
- 仅请求必要权限（App Clips 中无推送通知）

### URL 方案

每个 App Clip 由一个 URL 触发：
```
https://yourdomain.com/clip/[体验]
```

在 App Store Connect → 您的应用 → App Clip 体验中配置。

### 转发到完整应用

始终包含清晰的升级提示：

```swift
// 在用户从卡片中获得价值后显示 SKOverlay
let config = SKOverlay.AppClipConfiguration(position: .bottom)
let overlay = SKOverlay(configuration: config)
overlay.present(in: windowScene)
```

在用户获得价值**之后**显示覆盖层——而不是立即显示。

## App Clip 体验

您可以配置多个 App Clip 体验（每个 URL 模式一个）：

| 体验 | URL | 使用场景 |
|------|-----|---------|
| 默认 | `yourdomain.com` | 一般 / App Store 搜索 |
| 位置 | `yourdomain.com/location/123` | 地图、特定位置的 NFC |
| 活动 | `yourdomain.com/promo/summer` | 营销活动 |
| 功能 | `yourdomain.com/feature/x` | 特定功能演示 |

每个体验可以有自己的：

- 标题（最多 18 个字符）
- 副标题（最多 13 个字符）
- 头部图片（3000×2000px）
- 操作按钮文本

## App Clip 卡片设计

卡片在 App Clip 启动前显示：

| 字段 | 限制 | 提示 |
|------|------|------|
| 标题 | 18 个字符 | 清晰行动：“点咖啡”而不是“应用名称” |
| 副标题 | 13 个字符 | 强化价值：“跳过排队” |
| 头部图片 | 3000×2000px | 显示结果，而不是 UI |
| 操作按钮 | — | 使用上下文特定文本：“点单”、“支付”、“玩” |

## 测量

在 App Store Connect → 应用分析 → App Clips 中跟踪：

- App Clip 会话
- App Clip 卡片显示次数
- App Clip → 完整应用的转化
- 独立 App Clip 用户

## App Clip 与完整应用安装的权衡

| | App Clip | 完整安装 |
|---|----------|----------|
| 用户摩擦 | 非常低 | 较高 |
| 承诺 | 低 | 高 |
| 留存率 | 低（一次性使用） | 高 |
| 从卡片到安装的转化 | — | 比冷流量高 3–5 倍 |
| 最佳用途 | 发现 + 转化 | 留存 + 盈利 |

## 实现检查清单

```
设置：
- [ ] Xcode 项目中添加 App Clip 目标
- [ ] App Clip < 15MB（使用 Xcode 中的大小报告）
- [ ] 配置关联域名权限
- [ ] 在 App Store Connect 中注册 App Clip 体验 URL

用户体验：
- [ ] 60 秒内传递核心价值
- [ ] 使用 Apple Sign in 或 Apple Pay（无自定义注册）
- [ ] 价值传递后显示 SKOverlay（不是立即显示）
- [ ] 用户安装完整应用时清晰的数据转发

App Store Connect：
- [ ] 配置默认 App Clip 体验
- [ ] 上传头部图片（3000×2000px）
- [ ] 标题 ≤ 18 个字符，副标题 ≤ 13 个字符
- [ ] 如适用，为位置/活动配置额外体验
```

## 相关技能

- `aso-audit` — App Clip 可发现性取决于主应用的 ASO
- `onboarding-optimization` — 对 App Clip 体验应用相同的“价值优先”原则
- `ua-campaign` — 在付费活动中将流量引导至 App Clip URL
- `app-store-featured` — App Clips 可支持特色展示资格
