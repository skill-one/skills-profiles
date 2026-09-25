# Sosumi 技能

使用此技能在编写代理时可靠地获取 Apple 文档作为 Markdown 格式，以便需要精确 API 细节。

## 使用场景

在以下情况之一出现时使用 Sosumi：

- Apple 平台 API (`Swift`, `SwiftUI`, `UIKit`, `AppKit`, `Foundation` 等)
- API 签名、可用性、参数行为或返回语义
- 人机界面指南问题
- WWDC 会议记录查询
- 外部 Swift-DocC 文档（例如 GitHub Pages 或 Swift Package Index 主机）

## 核心工作流程

1. 如果您已经有一个 `developer.apple.com` URL，请将主机替换为 `sosumi.ai` 并保持相同的路径。
2. 如果您不知道确切的页面路径，请先搜索，然后获取最佳匹配结果。
3. 在回答实现问题时，优先选择特定符号页面而不是宽泛的顶层页面。

### 可选的 CLI 预检

如果 Sosumi CLI 可用，请在深入调试之前快速验证本地访问权限：

- `sosumi --version` 确认 CLI 已安装并在 `PATH` 中。
- `sosumi --help` 显示顶层用法。
- `sosumi <命令> --help` 是特定命令行为的手册。

## HTTP 使用

将 `developer.apple.com` 替换为 `sosumi.ai`：

- 原始：`https://developer.apple.com/documentation/swift/array`
- AI 可读：`https://sosumi.ai/documentation/swift/array`

## 内容类型

### Apple API 参考

- 模式：`https://sosumi.ai/documentation/{framework}/{symbol}`
- 示例：
  - `https://sosumi.ai/documentation/swift/array`
  - `https://sosumi.ai/documentation/swiftui/view`

### 人机界面指南

- 模式：`https://sosumi.ai/design/human-interface-guidelines/{topic}`
- 示例：
  - `https://sosumi.ai/design/human-interface-guidelines`
  - `https://sosumi.ai/design/human-interface-guidelines/foundations/color`

### Apple 视频记录

- 模式：`https://sosumi.ai/videos/play/{collection}/{id}`
- 示例：
  - `https://sosumi.ai/videos/play/wwdc2021/10133`
  - `https://sosumi.ai/videos/play/meet-with-apple/208`

### 外部 Swift-DocC

- 模式：`https://sosumi.ai/external/{full-https-url}`
- 示例：
  - `https://sosumi.ai/external/https://apple.github.io/swift-argument-parser/documentation/argumentparser/`
  - `https://sosumi.ai/external/https://swiftpackageindex.com/pointfreeco/swift-composable-architecture/1.23.1/documentation/composablearchitecture`

## MCP 工具快速参考

当 Sosumi 配置为 MCP 服务器 (`https://sosumi.ai/mcp`) 时使用这些工具：

| 工具 | 参数 | 使用 |
|---|---|---|
| `searchAppleDocumentation` | `query: string` | 搜索 Apple 文档并返回结构化结果 |
| `fetchAppleDocumentation` | `path: string` | 通过路径获取 Apple 文档或 HIG 内容作为 Markdown |
| `fetchAppleVideoTranscript` | `path: string` | 通过 `/videos/play/...` 路径获取 Apple 视频记录 |
| `fetchExternalDocumentation` | `url: string` | 通过绝对 HTTPS URL 获取外部 Swift-DocC 页面 |

## 最佳实践

- 如果未知确切路径，请先搜索。
- 为编码问题获取目标符号页面。
- 在回答中保留源链接，以便用户快速验证详细信息。
- 在引用 Apple 文档页面时，直接在响应中使用 Sosumi 路径。

## 故障排除

### 404 或稀疏输出

- 路径可能不正确或过于宽泛。
- 先运行搜索查询，然后获取特定结果路径。

### 外部页面无法获取

- 主机可能通过 `robots.txt` 或 `X-Robots-Tag` 指令阻止访问。
- 尝试为同一符号使用另一个规范页面 URL。
