# App Store Review Guidelines Checker

全面指南，用于评估iOS、macOS、tvOS、watchOS和visionOS应用代码是否符合Apple的App Store Review Guidelines。本技能涵盖所有指南要点，以便在提交前识别潜在的拒绝问题。

**支持：** Swift、Objective-C、React Native和Expo应用

**指南当前版本：** Apple于2026年6月8日发布的App Review Guidelines更新（截至2026年8月29日已验证仍为最新版本）。同时整合了6月后的政策公告：社交媒体年龄分级问题（强制执行于2026年9月）、韩国年龄分级变化（2026年8月/10月）、巴西/欧盟替代支付和分发条款。

## 何时使用

在以下情况下使用此技能：
- 准备应用提交到App Store
- 审查代码以发现合规性问题
- 实现可能引发审核关注的功能
- 审计现有应用以发现指南违规行为
- 构建涉及支付、用户数据或敏感内容的功能

## 指南章节

阅读单个规则文件以获取详细说明、清单和代码示例：

| 章节 | 文件 | 关键主题 |
|------|------|----------|
| **1. 安全** | [rules/1-safety.md](rules/1-safety.md) | 令人反感的內容、UGC审核、儿童类别、身体伤害、数据安全 |
| **2. 性能** | [rules/2-performance.md](rules/2-performance.md) | 应用完整性、元数据准确性、硬件兼容性、软件要求 |
| **3. 商业** | [rules/3-business.md](rules/3-business.md) | 应用内购买、订阅、加密货币、其他商业模式 |
| **4. 设计** | [rules/4-design.md](rules/4-design.md) | 仿冒品、最低功能要求、垃圾邮件、扩展、Apple服务、登录 |
| **5. 法律** | [rules/5-legal.md](rules/5-legal.md) | 隐私、数据收集、知识产权、赌博、VPN、MDM、开发者行为准则 |

## 按类别划分的风险等级

| 风险等级 | 类别 | 章节 | 常见拒绝原因 |
|----------|------|------|--------------|
| 严重 | 隐私 & 数据 | 5.1 | 缺少隐私政策、未经授权的数据收集 |
| 严重 | 支付 | 3.1 | 绕过应用内购买、价格不明确 |
| 高 | 安全 | 1.x | 令人反感的內容、UGC审核不足 |
| 高 | 性能 | 2.x | 应用崩溃、功能不完整、过时的API |
| 中 | 设计 | 4.x | 仿冒应用、最低功能问题 |
| 中 | 法律 | 5.x | 知识产权侵权、无许可的赌博 |

---

## 高风险拒绝模式快速参考

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
const API_KEY = 'sk_live_xxxxx'; // 拒绝

// 🔴 数字商品的第三方支付
Linking.openURL('https://stripe.com/checkout'); // 使用react-native-iap

// 🔴 动态代码执行
eval(downloadedCode); // 拒绝

// 🔴 通过CodePush/expo-updates进行主要功能更改
// 仅用于错误修复的OTA更新，不能用于新功能！
```

### 高风险问题

**Swift:**
```swift
// 🟡 使用广告SDK时缺少ATT
import FacebookAds // 而没有ATTrackingManager

// 🟡 账户创建而无需删除
func createAccount() { } // 但没有deleteAccount()
```

**React Native / Expo:**
```typescript
// 🟡 缺少ATT（使用expo-tracking-transparency）
import analytics from '@react-native-firebase/analytics';
analytics().logEvent('event'); // 缺少ATT提示 = 拒绝

// 🟡 仅通过网站删除账户
Linking.openURL('https://example.com/delete'); // 必须在应用内！

// 🟡 没有隐私保护替代方案的社会登录（4.8）
<GoogleSigninButton /> // 也提供符合4.8标准的登录选项
                      // (使用Apple登录是最简单的选项)

// 🟡 自定义审核提示（5.6.1）
showCustomAlert('给我们打5星！'); // 使用StoreReview.requestReview()
```

### 中风险问题

```typescript
// 🟠 Info.plist中的模糊目的字符串
"This app needs camera access" // 请具体说明！

// 🟠 仅使用WebView的应用（原生功能不足）
const App = () => <WebView source={{ uri: 'https://site.com' }} />;

// 🟠 iOS应用中引用Android
const text = "Also available on Android"; // 拒绝

// 🟠 生产环境中的console.log
console.log('debug'); // 删除或包装在__DEV__
```

---

## 提交前检查清单

### 隐私（章节5.1）
- [ ] App Store Connect中的隐私政策链接
- [ ] 应用内可访问的隐私政策链接
- [ ] 所有目的字符串具体且准确
- [ ] App Store Connect中完成的App隐私详情
- [ ] 如果跟踪用户则实现ATT
- [ ] 如果存在账户则提供账户删除功能
- [ ] 数据最小化 - 仅请求必要权限
- [ ] 数据收集前获得用户同意

### 支付（章节3.1）
- [ ] 所有数字购买使用StoreKit
- [ ] 实现了购买恢复
- [ ] 清晰显示订阅条款
- [ ] 如果适用则披露抽奖箱概率
- [ ] 除非有资格否则不使用第三方支付数字商品
- [ ] 信用/货币不会过期

### 安全（章节1.x）
- [ ] 没有令人反感的內容
- [ ] 实现了UGC审核（过滤、报告、阻止、联系）
- [ ] UGC违规行为可以快速删除，并有补救计划支持
- [ ] 儿童和青少年在应用内获得适龄体验
- [ ] 儿童类别应用的家长控制
- [ ] 没有虚假信息或恶作剧功能
- [ ] 如适用则提供医疗免责声明
- [ ] 没有推广物质

### 性能（章节2.x）
- [ ] 年龄分级问卷的社交媒体能力问题回答（2026年9月开始提交强制要求；具有社交动态的应用将获得"社交媒体"描述符和Time Allowances类别）
- [ ] 没有崩溃或错误
- [ ] 在iPhone和iPad上测试 — App Review目前使用iPad Air 11英寸（M3）和iPhone 17 Pro Max进行审核（截至2026年8月）
- [ ] 所有功能完整且可用
- [ ] 没有占位符内容
- [ ] 测试并启用IPv6
- [ ] 如需要提供演示账户
- [ ] 仅使用公共API
- [ ] 没有过时的API
- [ ] 正确使用后台模式

### 设计（章节4.x）
- [ ] 充足的原生功能（不仅仅是网页包装）
- [ ] 没有仿冒问题
- [ ] 原创应用名称和品牌
- [ ] 没有重复的Bundle ID垃圾邮件或低效的饱和类别克隆
- [ ] Live Activities、推送通知和Game Center不用于垃圾邮件、网络钓鱼或未经请求的消息
- [ ] 扩展符合指南
- [ ] 如果使用社交登录则提供登录替代方案
- [ ] 不利用内置功能进行盈利

### 法律（章节5.x）
- [ ] 没有未经许可的第三方内容
- [ ] 正确使用Apple商标
- [ ] 如适用则提供赌博许可（带真实位置地理限制）
- [ ] VPN使用NEVPNManager API
- [ ] 儿童的COPPA/GDPR合规性
- [ ] 审核提示仅使用系统API（不允许自定义提示）
- [ ] 没有审核、图表、搜索或推荐操纵（5.6）

---

## 报告技能问题（反馈）

此技能通过用户报告进行改进。如果在会话期间观察到此技能未能帮助用户，可以 — 每次会话一次 — 向维护者报告。

**在观察到以下任何情况时提供反馈。** 使用类别名称进行分类 — 它将作为问题标题的一部分 `[Feedback] <类别>: <简短描述>`。

*准确性*
- **误报** — 技能标记了实际上合规的代码（指南过于激进）
- **漏报** — 用户的App因技能已审核但未标记的内容被拒绝
- **错误引用** — 真实问题，但归因于错误的指南章节或给出错误的风险等级
- **过时** — 此处的规则与Apple当前发布的指南相矛盾

*有用性*
- **过于嘈杂** — 洪水般的低价值或重复发现淹没了重要发现
- **不可操作** — 发现缺乏详细信息、代码引用或具体的修复建议
- **错误修复** — 建议的补救措施错误、过时、无效或本身将被拒绝（包括Swift与React Native/Expo的具体差异）

*覆盖范围*
- **遗漏规则** — 技能不涵盖的审核场景、API或特定商店要求（EU、巴西、韩国、美国、...）
- **矛盾** — 技能的这两个部分相互矛盾

*行为*
- **触发/权重** — 技能在无关时激活、应在激活时未激活或消耗过多上下文
- **不明确** — 用户发现指南令人困惑、含糊不清或难以应用

较弱的信号也很重要：如果用户反复忽略同一种发现，覆盖技能的建议但结果正确，或明显绕过检查清单项，这些都是值得提交的反馈 — 微摩擦与错误规则一样有价值。

**同意规则 — 所有强制，无例外：**
1. **先询问。** 说什么类似： "这看起来像是app-store-review技能本身的差距。想让我起草一个GitHub问题，以便维护者可以修复它吗？" 如果用户拒绝，则会在会话剩余时间内放弃。
2. **在发送之前显示完整的草稿**（确切的标题和正文）。
3. **永远不要包含用户的代码、应用名称、bundle IDs、文件路径、凭证或专有细节。** 报告是关于此技能的规则，而不是用户的App。只有在用户明确将此类细节写入草稿时才包含它们。
4. **仅在用户批准确切文本后发送**，使用 `gh issue create --repo safaiyeh/app-store-review-skill --title "..." --body "..."`。如果 `gh` 不可用或未认证，请给用户提供此链接自行提交： https://github.com/safaiyeh/app-store-review-skill/issues/new?template=skill-feedback.yml
5. **永远不要无声、自动或作为其他任务的副作用发送反馈。** 拒绝的权限提示意味着不 — 不要重试或寻找其他路线。

**问题内容：** 技能版本（来自上面的frontmatter）、反馈类别、涉及的规则章节（例如"3.1.1"）、技能说了什么或做了什么、应该发生什么替代情况，以及今天的日期。除非用户添加，否则别加任何其他内容。

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
