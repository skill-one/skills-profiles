---
name: app-store-review
description: 评估代码是否符合苹果App Store审核指南。在审查iOS、macOS、tvOS、watchOS或visionOS应用代码（Swift、Objective-C、React Native或Expo）时使用此技能，以便在提交前识别潜在的App Store拒绝问题。在涉及应用审核准备、合规性检查或App Store提交准备就绪的任务中触发。
---

# App Store Review Guidelines Checker

全面指南，用于评估iOS、macOS、tvOS、watchOS和visionOS应用代码是否符合Apple的App Store Review Guidelines。本技能涵盖所有指南要点，以便在提交前识别潜在的拒绝问题。

**支持：** Swift、Objective-C、React Native和Expo应用

**指南当前版本：** Apple于2026年6月8日发布的App Review Guidelines更新（截至2026年8月29日已验证仍为最新版本）。同时纳入了6月后的政策公告：社交媒体年龄分级问题（强制执行时间为2026年9月）、韩国年龄分级变化（2026年8月/10月）、巴西/欧盟替代支付和分发条款。

## 何时使用

在以下情况下使用此技能：
- 准备应用提交到App Store
- 审查代码以解决合规性问题
- 实现可能引发审核关注的功能
- 审计现有应用以查找指南违规行为
- 构建涉及支付、用户数据或敏感内容的功能

## 指南章节

阅读单个规则文件以获取详细说明、清单和代码示例：

| 章节 | 文件 | 关键主题 |
|------|------|----------|
| **1. 安全** | [rules/1-safety.md](rules/1-safety.md) | 令人反感的內容、UGC审核、儿童类别、身体伤害、数据安全 |
| **2. 性能** | [rules/2-performance.md](rules/2-performance.md) | 应用完整性、元数据准确性、硬件兼容性、软件要求 |
| **3. 商业** | [rules/3-business.md](rules/3-business.md) | 应用内购买、订阅、加密货币、其他商业模式 |
| **4. 设计** | [rules/4-design.md](rules/4-design.md) | 仿冒品、最低功能、垃圾邮件、扩展、Apple服务、登录 |
| **5. 法律** | [rules/5-legal.md](rules/5-legal.md) | 隐私、数据收集、知识产权、赌博、VPN、MDM、开发者行为准则 |

## 按类别划分的风险等级

| 风险等级 | 类别 | 章节 | 常见拒绝原因 |
|----------|------|------|--------------|
| 严重 | 隐私 & 数据 | 5.1 | 缺少隐私政策、未经授权的数据收集 |
| 严重 | 支付 | 3.1 | 绕过应用内购买、价格不明确 |
| 高 | 安全 | 1.x | 令人反感的內容、UGC审核不足 |
| 高 | 性能 | 2.x | 崩溃、功能不完整、已弃用的API |
| 中 | 设计 | 4.x | 仿冒应用、最低功能问题 |
| 中 | 法律 | 5.x | 知识产权违规、无许可的赌博 |

---

## 高风险拒绝模式快速参考

对于ATT发现，请验证SDK的配置和实际数据使用情况。对于账户删除，请验证目的地和流程。对于日志记录，请检查暴露的数据和任何编辑。如果证据不可用，请报告需要验证的内容，而不是仅基于API调用、SDK导入或URL声明拒绝。

### 严重问题（立即拒绝）

**Swift:**
```swift
// 🔴 使用私有API
let selector = NSSelectorFromString("_privateMethod")

// 🔴 硬编码的密钥
let apiKey = "sk_live_xxxxx"

// 🔴 数字商品的第三方支付
func purchaseDigitalContent() {
    openStripeCheckout() // 使用StoreKit代替
}
```

**React Native / Expo:**
```typescript
// 🔴 JS bundle中的硬编码密钥
const API_KEY = 'sk_live_xxxxx'; // REJECTION

// 🔴 数字商品的第三方支付
Linking.openURL('https://stripe.com/checkout'); // 使用react-native-iap

// 🔴 动态代码执行
eval(downloadedCode); // REJECTION

// 🔴 通过CodePush/expo-updates进行主要功能更改
// 仅用于修复错误的OTA更新，不能用于新功能！
```

### 高风险问题

**Swift:**
```swift
// 🟡 在未获得ATT授权的情况下启动Apple定义的跟踪
// 说明性辅助：跨公司链接用户数据用于广告定位
enableCrossCompanyAdTracking() // 在ATT授权之前调用

// 🟡 账户创建而没有删除
func createAccount() { } // 但应用内没有删除流程
```

**React Native / Expo:**
```typescript
// 🟡 在未获得ATT授权的情况下启动Apple定义的跟踪
// 说明性辅助：SDK跨公司链接用户数据用于广告定位
initializeTrackingAdSDK(); // 在ATT授权之前调用

// ✅ 第一方分析不需要ATT
// 假设没有IDFA访问、跨公司广告使用或数据中介共享
import analytics from '@react-native-firebase/analytics';
analytics().logEvent('event');

// 🟡 删除账户按钮打开的是说明页面，没有删除流程
Linking.openURL('https://example.com/help'); // 验证为仅说明页面
// ✅ 应用内按钮可以链接到完成删除的页面
Linking.openURL('https://example.com/delete-account');

// 🟡 生产日志中暴露敏感数据 (1.6 / 5.1)
console.log('Access token:', accessToken); // 删除密钥或编辑它

// 🟡 没有隐私保护替代方案的社会登录 (4.8)
<GoogleSigninButton /> // 也提供符合4.8标准的登录选项
                       // (使用Apple登录是最简单的选项)

// 🟡 自定义审核提示 (5.6.1)
showCustomAlert('Rate us 5 stars!'); // 使用StoreReview.requestReview()
```

### 中风险问题

```typescript
// 🟠 Info.plist中的模糊目的字符串
"This app needs camera access" // 请具体说明！

// 🟠 仅WebView应用（原生功能不足）
const App = () => <WebView source={{ uri: 'https://site.com' }} />;

// 🟠 iOS应用中引用Android
const text = "Also available on Android"; // REJECTION
```

---

## 提交前检查清单

### 隐私（章节5.1）
- [ ] App Store Connect中的隐私政策链接
- [ ] 应用内可访问的隐私政策链接
- [ ] 所有目的字符串都具体且准确
- [ ] App Store Connect中完成的App隐私详细信息
- [ ] 在Apple定义的跟踪或IDFA访问之前获得ATT授权（见[5.1.2](rules/5-legal.md#512-data-use-and-sharing)）；第一方分析不需要ATT
- [ ] 如果应用支持账户创建，可以在应用内启动删除；允许直接链接到完成删除的网页
- [ ] 数据最小化 - 仅请求必要的权限
- [ ] 在数据收集之前获得用户同意

### 支付（章节3.1）
- [ ] 使用StoreKit进行所有数字购买
- [ ] 实现了恢复购买
- [ ] 清晰显示订阅条款
- [ ] 如果适用，披露宝箱几率
- [ ] 除非有资格，否则不使用第三方支付数字商品
- [ ] 信用/货币不会过期

### 安全（章节1.x）
- [ ] 没有令人反感的內容
- [ ] 实现了UGC审核（过滤、报告、阻止、联系）
- [ ] UGC违规行为可以快速删除，并有补救计划支持
- [ ] 儿童和青少年在应用内获得适合其年龄的体验
- [ ] 儿童类别应用的家长控制
- [ ] 没有虚假信息或恶作剧功能
- [ ] 如适用，提供医疗免责声明
- [ ] 没有宣传物质

### 性能（章节2.x）
- [ ] 社交媒体能力问题的年龄分级问卷的答案（从2026年9月开始提交强制要求；具有社交动态的应用将获得“社交媒体”描述符和Time Allowances类别）
- [ ] 没有崩溃或错误
- [ ] 在iPhone和iPad上测试——App Review目前使用iPad Air 11英寸（M3）和iPhone 17 Pro Max进行审核（截至2026年8月）
- [ ] 所有功能完整且功能正常
- [ ] 没有占位符内容
- [ ] 测试并启用IPv6
- [ ] 如有必要，提供演示账户
- [ ] 仅使用公共API
- [ ] 没有已弃用的API
- [ ] 正确使用后台模式

### 设计（章节4.x）
- [ ] 具有足够的原生功能（不仅仅是WebView包装器）
- [ ] 没有仿冒问题
- [ ] 原始应用名称和品牌
- [ ] 没有重复的Bundle ID垃圾邮件或低效的饱和类别克隆
- [ ] Live Activities、推送通知和Game Center不用于垃圾邮件、网络钓鱼或未经请求的消息
- [ ] 扩展符合指南
- [ ] 如果使用社交登录，提供登录替代方案
- [ ] 不利用内置功能进行盈利

### 法律（章节5.x）
- [ ] 没有未经许可的第三方内容
- [ ] 正确使用Apple商标
- [ ] 如适用，提供赌博许可（具有基于真实位置的区域限制）
- [ ] VPN使用NEVPNManager API
- [ ] 儿童的COPPA/GDPR合规性
- [ ] 审核提示仅使用系统API（不允许自定义提示）
- [ ] 没有审核、图表、搜索或推荐操纵（5.6）

---

## 报告技能问题（反馈）

此技能通过用户报告得到改进。如果在会话期间观察到此技能未能满足用户需求，可以——每次会话一次——向维护者报告。

**在观察到以下任何情况时提供反馈。** 使用类别名称进行分类——它将作为问题标题的一部分，格式为`[Feedback] <category>: <简短描述>`。

*准确性*
- **误报**——技能标记了实际上合规的代码（指南过于激进）
- **漏报**——用户的App因技能已审核但未标记的问题被拒绝
- **错误引用**——真实问题，但归因于错误的指南章节或给出错误的风险等级
- **过时**——本处的规则与Apple当前发布的指南相矛盾

*有用性*
- **过于嘈杂**——大量低价值或重复的发现淹没了重要发现
- **不可操作**——发现缺乏详细信息、代码引用或具体的修复建议
- **错误修复**——建议的补救措施是错误的、已弃用、无效或本身将被拒绝（包括Swift与React Native/Expo的具体差异）

*覆盖范围*
- **遗漏规则**——技能不涵盖的审核场景、API或特定商店要求（EU、巴西、韩国、美国、...）
- **矛盾**——此技能的两个部分相互矛盾

*行为*
- **触发/权重**——技能在无关紧要时激活、应该激活时未激活或消耗过多上下文
- **不明确**——用户发现指南令人困惑、模糊或难以应用

软信号也很重要：如果用户反复忽略同类型的发现，覆盖技能的建议结果正确，或明显绕过检查清单项，这些都是值得提交的反馈——微摩擦与错误规则一样有价值。

**同意规则——所有强制执行，无例外：**
1. **先询问。** 说法如："这看起来像是app-store-review技能本身的差距。想让我起草一个GitHub问题，以便维护者可以修复它？" 如果用户拒绝，则会在会话剩余时间内放弃。
2. **显示完整的草稿**（确切的标题和正文）在发送之前。
3. **永远不包含用户的代码、应用名称、bundle IDs、文件路径、凭证或专有细节。** 报告是关于此技能的规则，而不是用户的App。只有在用户明确将此类细节写入草稿时才包含它们。
4. **仅在用户批准确切文本后发送**，使用`gh issue create --repo safaiyeh/app-store-review-skill --title "..." --body "..."`。如果`gh`不可用或未认证，请提供此链接让用户自行提交：https://github.com/safaiyeh/app-store-review-skill/issues/new?template=skill-feedback.yml
5. **永远不要无声、自动或作为另一项任务的副作用发送反馈。** 拒绝的权限提示意味着不——不要重试或寻找其他路线。

**问题内容：** 技能版本（来自上面的frontmatter）、反馈类别、涉及的规则章节（例如"3.1.1"）、技能所说的或所做的内容、应该发生的情况、以及今天的日期。除非用户添加，否则不要添加其他内容。

---

## 参考文献

- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [Apple Developer Program License Agreement](https://developer.apple.com/support/terms/apple-developer-program-license-agreement/)
- [June 8, 2026 App Review Guidelines update](https://developer.apple.com/news/?id=a233fmpw)
- [Age rating questionnaire: social media questions (July 2026)](https://developer.apple.com/news/?id=tlur8uvi)
- [Age rating updates for the Republic of Korea (August 2026)](https://developer.apple.com/news/?id=oj3r9pvw)
- [Changes for apps in the European Union (August 2026)](https://developer.apple.com/news/?id=gmws0jgp)
- [Changes to iOS in Brazil (June 2026)](https://developer.apple.com/news/?id=dhwadr2x)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [App Store Connect Help](https://developer.apple.com/help/app-store-connect/)
- [Apple Developer Documentation](https://developer.apple.com/documentation/)
