# 更新 SwiftUI API

通过 Sosumi MCP 系统扫描 Apple 的开发者文档，识别已弃用的 SwiftUI API 及其现代替代方案，并更新 `skills/swiftui-expert-skill/references/latest-apis.md`。

## 前置条件

- **Sosumi MCP** 必须已启用且可用（提供 `searchAppleDocumentation`、`fetchAppleDocumentation`、`fetchAppleVideoTranscript`、`fetchExternalDocumentation`）
- 对此仓库有写入权限（或其分支）

## 工作流程

### 1. 了解当前覆盖范围

阅读 `skills/swiftui-expert-skill/references/latest-apis.md` 以了解：
- 已文档化的弃用到现代的过渡
- 所使用的版本片段（iOS 15+、16+、17+、18+、26+）
- 底部的快速查找表

### 2. 加载扫描清单

读取 `references/scan-manifest.md`（相对于此技能）。它包含 API 区域的分类列表、文档路径、搜索查询和 WWDC 视频路径以供扫描。

### 3. 扫描 Apple 文档

针对清单中的每个类别：

1. 使用列出的查询调用 `searchAppleDocumentation` 以发现相关页面。
2. 使用特定的文档路径调用 `fetchAppleDocumentation` 以获取完整的 API 详细信息。
3. 查找弃用声明、"已弃用"标签和"使用...替代"的指导。
4. 记录现代替代方案何时开始可用。
5. 可选地调用 `fetchAppleVideoTranscript` 以获取宣布 API 变更的 WWDC 会议的文本记录。

将相关的搜索批量处理以提高效率。专注于查找 `latest-apis.md` 中尚未记录的**新**弃用情况。

### 4. 比较并识别变更

将发现结果与现有条目进行比较。将结果分类：
- **新弃用**：在 `latest-apis.md` 中尚未文档化的 API
- **修正**：需要更新的现有条目（版本错误、有更好的替代方案）
- **新版本片段**：如果新的 iOS 版本引入了弃用情况，则添加新部分

### 5. 更新 latest-apis.md

严格遵循既定格式。每个条目必须包含：

**部分位置** -- 放在正确的版本片段下：
- "始终使用 `modernAPI()` 替代 `deprecatedAPI()`" 用于长期弃用的 API
- "针对 iOS 16+" / "17+" / "18+" / "26+" 用于版本限制的变更

**条目格式：**

```markdown
**始终使用 `modernAPI()` 替代 `deprecatedAPI()`。**

\```swift
// 现代
View()
    .modernAPI()

// 已弃用
View()
    .deprecatedAPI()
\```
```

**快速查找表** -- 在文件底部添加一行：

```markdown
| `deprecatedAPI()` | `modernAPI()` | iOS XX+ |
```

保留文件顶部的归因行：
> 基于 Sosumi MCP 对 Apple 文档的比较，我们发现最新的推荐 API。

### 6. 打开拉取请求

1. 从 `main` 创建一个名为 `update/latest-apis-YYYY-MM` 的分支（使用当前年份和月份）。
2. 将更改提交到 `skills/swiftui-expert-skill/references/latest-apis.md`。
3. 通过 `gh pr create` 打开 PR，并包含：
   - **标题**：`Update latest SwiftUI APIs (Month Year)`
   - **正文**：新/变更条目的摘要，归因于 Sosumi MCP

## Sosumi MCP 工具参考

| 工具 | 参数 | 返回 |
|------|-----------|---------|
| `searchAppleDocumentation` | `query` (string) | 包含 `results[]` 的 JSON，其中包含 `title`、`url`、`description`、`breadcrumbs`、`tags`、`type` |
| `fetchAppleDocumentation` | `path` (string, 例如 `/documentation/swiftui/view/foregroundstyle(_:)`) | Markdown 文档内容 |
| `fetchAppleVideoTranscript` | `path` (string, 例如 `/videos/play/wwdc2025/10133`) | Markdown 文本记录 |
| `fetchExternalDocumentation` | `url` (string, 完整的 https URL) | Markdown 文档内容 |

## 小贴士

- 使用 `searchAppleDocumentation` 进行广泛的查询，然后使用 `fetchAppleDocumentation` 钻入特定路径。
- Apple 的弃用文档通常会在页面中注明"已弃用"并链接到替代方案。
- WWDC "SwiftUI 新功能"会议是引入新替代方案的最佳来源。
- 当不确定弃用的确切 iOS 版本时，通过检查获取文档中的"可用性"部分进行验证。
- 如果 API 已弃用但没有直接替代方案，请记录这一点，而不是建议不正确的替代方案。
