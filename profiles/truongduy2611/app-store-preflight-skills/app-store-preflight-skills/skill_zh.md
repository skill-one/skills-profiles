# App Store 预提交检查技能

对您的 iOS/macOS 项目运行预提交检查，以捕获常见的 App Store 拒绝模式。

## 前置条件

- **asc CLI** — 通过 Homebrew 安装：`brew install asc` ([App-Store-Connect-CLI](https://github.com/rudrankriyam/App-Store-Connect-CLI))
- **ASC CLI Skills** — [app-store-connect-cli-skills](https://github.com/rudrankriyam/app-store-connect-cli-skills) 用于 `asc` 使用模式
- **jq** — 可选，但规则文档中的一些 JSON 检查示例会使用它

## 第 1 步：识别应用类型 → 加载检查清单

通过从 `references/guidelines/by-app-type/` 加载相关检查清单来确定适用哪些指南。始终从 `all_apps.md` 开始，然后添加特定于应用类型的清单：

| 应用类型 | 检查清单 |
|----------|-----------|
| 每个应用 | `references/guidelines/by-app-type/all_apps.md` |
| 订阅 / IAP | `references/guidelines/by-app-type/subscription_iap.md` |
| 社交 / UGC | `references/guidelines/by-app-type/social_ugc.md` |
| 儿童类别 | `references/guidelines/by-app-type/kids.md` |
| 健康 & 健身 | `references/guidelines/by-app-type/health_fitness.md` |
| 游戏 | `references/guidelines/by-app-type/games.md` |
| macOS | `references/guidelines/by-app-type/macos.md` |
| AI / 生成式 AI | `references/guidelines/by-app-type/ai_apps.md` |
| 加密货币 & 金融 | `references/guidelines/by-app-type/crypto_finance.md` |
| VPN | `references/guidelines/by-app-type/vpn.md` |

完整指南索引：`references/guidelines/README.md`

## 第 2 步：拉取元数据进行检查

使用 `asc` CLI 拉取最新的 App Store 元数据：

```bash
# 拉取您要审查版本的规范元数据 JSON
asc metadata pull --app "<APP_ID>" --version "<VERSION>" --dir ./metadata
```

`asc metadata pull` 将应用信息文件写入 `./metadata/app-info/*.json`，并将版本本地化文件写入 `./metadata/version/<VERSION>/*.json`。

下面的大多数规则示例假设 `asc metadata pull` 写入的规范 JSON 布局。

如果您已经有其他布局的元数据（例如 fastlane `metadata/`），则可以调整文件路径示例以适应该结构，或者首先拉取规范的 `asc` 布局。

## 第 3 步：运行拒绝规则检查

对于每个类别，从 `references/rules/` 加载相关规则文件进行检查。每个规则包含：**要检查的内容**、**如何检测**、**解决方案** 和 **拒绝示例**。

| 类别 | 规则文件 |
|----------|------------|
| 元数据 | `references/rules/metadata/*.md` |
| 订阅 | `references/rules/subscription/*.md` |
| 隐私 | `references/rules/privacy/*.md` |
| 设计 | `references/rules/design/*.md` |
| 授权 | `references/rules/entitlements/*.md` |

## 第 4 步：报告发现结果

使用此模板生成摘要报告：

```markdown
## 预提交报告

### ❌ 拒绝发现 (N)
- [GUIDELINE X.X.X] 问题描述
  - 文件: path/to/offending/file
  - 修复: 要做什么

### ⚠️ 警告 (N)
- [GUIDELINE X.X.X] 潜在问题

### ✅ 通过 (N)
- [类别] 所有检查通过
```

按严重性排序：拒绝优先，然后警告，最后通过。

## 第 5 步：自动修复 + 验证

某些问题可以自动修复：
- **竞争对手术语** → 建议替换文本，移除竞争对手名称
- **元数据字符限制** → 显示当前长度与最大长度
- **缺失链接** → 生成模板 ToS/PP URL

应用任何自动修复后，**重新运行受影响的检查**以确认修复解决了违规问题。只有重新扫描通过后才能标记为已解决。

对于需要手动干预的问题（截图、UI 重新设计），请提供清晰说明，但不要自动修复。

## 注意事项

- **中国商店** — 禁止的 AI 术语（ChatGPT、Gemini 等）会检查所有区域，而不仅仅是 `zh-Hans`。Apple 会检查中国商店中可见的所有区域。
- **隐私清单** — 即使您的应用不直接调用 Required Reason API，也需要 `PrivacyInfo.xcprivacy`。使用 `UserDefaults` 或 `NSFileManager` 的第三方 SDK（Firebase、Amplitude 等）会触发此要求。
- **asc auth** — `asc metadata pull` 需要 App Store Connect 认证。首先运行 `asc auth login`，或设置 `ASC_KEY_ID`、`ASC_ISSUER_ID` 以及 `ASC_PRIVATE_KEY_PATH` / `ASC_PRIVATE_KEY` / `ASC_PRIVATE_KEY_B64` 之一。如果您不确定 `asc` 捕获了什么，请运行 `asc auth doctor`。
- **订阅元数据** — Apple 要求在 App Store 描述和应用内订阅购买屏幕中都提供 ToS/PP 链接。缺少任何一个都是单独的拒绝。
- **macOS 授权** — Apple 会要求您为每个临时例外授权 (`com.apple.security.temporary-exception.*`) 提供理由。移除您未主动使用的授权。

## 添加新规则

在适当的 `references/rules/` 子目录中创建一个 `.md` 文件：

```markdown
# 规则: [简短标题]
- **指南**: [Apple 指南编号]
- **严重性**: REJECTION | WARNING
- **类别**: metadata | subscription | privacy | design | entitlements

## 要检查的内容
## 如何检测
## 解决方案
## 拒绝示例
```
