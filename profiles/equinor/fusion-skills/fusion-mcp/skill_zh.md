# Fusion MCP 设置指南

## 使用场景

在以下情况下使用：
- 用户询问：
  - Fusion MCP 是什么
  - 它能做什么
  - 如何安装/配置它
  - 如何验证其是否正常工作
  - 如何解决失败的 Fusion MCP 设置问题

典型触发词：
- "Fusion MCP 是什么"
- "帮我设置 Fusion MCP"
- "如何将 Fusion MCP 与 copilot 一起使用"

## 不适用场景

- 实现与 MCP 设置无关的产品功能
- 在未经用户确认的情况下进行破坏性环境更改
- 假设私有仓库的详细信息可见
- 回答关于 Fusion 框架 API、EDS 组件或技能目录的基于来源的问题——一旦 MCP 运行，请使用 `fusion-research` 来处理这些问题

## 必须输入的信息

在提出设置步骤之前收集：
- 用户环境（操作系统、编辑器/运行时）
- MCP 将运行的目标客户端（VS Code 是主要目标）
- 用户是否可以使用 Equinor Entra 账户

如果信息缺失，请先提出简洁的追问问题。

## 指令

1. 解释此 MCP 服务器提供的内容：
   - 面向 Fusion 的 MCP 功能，用于检索和工作流支持
   - 作为托管服务提供——大多数开发人员无需本地基础设施
   - 检索工具：`search`、`search_framework`、`search_docs`、`search_eds`、`search_indexes`、`search_backend_code`
   - 工具界面可能随时间演变
2. 指导用户设置**托管的正式服务器**——唯一推荐路径：
   - 无需 Docker、无 API 密钥、无需本地克隆
   - VS Code 通过 Microsoft Entra（Equinor 账户）进行身份验证
   - 使用正式环境的一键安装链接（参见 `references/vscode-mcp-config.md`）
   - 或使用 `"type": "http"` 和服务器 URL 进行手动配置（参见 `references/vscode-mcp-config.md`）
   - 除非用户有明确的运维需求，否则不要建议本地 Docker、GHCR 或自托管替代方案
3. 描述身份验证流程：
   - 首次调用工具时，VS Code 会提示使用 Equinor Entra 账户登录
   - 令牌自动管理；在可能的情况下静默续期，需要时交互式提示
   - 访问受现有 Fusion 角色分配控制
4. 提供轻量级的 MCP 检测测试：
   - 运行 `initialize` 并确认成功响应
   - 运行 `tools/list` 并确认至少返回了一个工具
   - 对一个可用的工具运行一个非破坏性的 `tools/call`
   - 通过标准：调用响应非空（`content` 或 `structuredContent` 包含数据）
   - 注意：不要硬编码固定的工具列表；工具清单可能在版本之间变化
5. 按文档顺序进行故障排除：
   - Entra 登录提示未出现 → 验证配置中的 `oauth.clientId` 并确认 VS Code 使用 Equinor 账户登录
   - `401 Unauthorized` → 通过 VS Code 账户设置重新认证；确保 Equinor Entra 账户处于活动状态
   - `tools/list` 返回空或工具调用失败 → 验证 VS Code 中是否选中/启用 MCP 服务器条目，并在重新加载后重试
   - 部分工具行为异常 → 检查 VS Code Output > Copilot 中的错误详情并重启 MCP 服务器
6. 当 MCP 设置失败或用户要求提交 Bug 时，从 `assets/bug-report-template.md` 生成 Bug 报告草稿。
   - 默认目标仓库：`equinor/fusion-mcp`
   - 包括具体的复现步骤、预期与实际行为、已尝试的故障排除步骤
   - 包括非敏感的环境信息（操作系统、VS Code 版本、MCP 服务器 URL、Entra 账户类型）
   - 绝不包含密钥、令牌或原始凭证值
7. 对于不确定性或仓库私有约束，明确说明假设并链接到权威文档，而不是猜测。

## 预期输出

返回：
- 简短的 Fusion MCP 解释及其使用场景
- 针对用户环境的托管正式服务器设置步骤
- 验证清单：运行 `initialize`（预期成功响应）、运行 `tools/list`（预期至少一个工具）、运行一个 `tools/call`（预期 `content` 或 `structuredContent` 非空）
- 与观察到的错误症状对应的故障排除步骤
- 使用 `assets/bug-report-template.md`（默认目标 `equinor/fusion-mcp`）的 Bug 报告草稿
- 用户要求时提供的脚本片段
- 明确指出的假设和缺失信息
- 链接到使用的上游文档

## 参考文献

- [references/README.md](references/README.md)
- [assets/bug-report-template.md](assets/bug-report-template.md)

## 安全与约束

永远不要：
- 请求或暴露密钥、令牌或凭证
- 编造项目文档不支持的设置命令
- 在未验证输出的情况下声称设置成功
- 在未经明确用户确认的情况下运行破坏性命令

始终：
- 优先将官方仓库文档作为事实来源
- 指导用户使用托管正式服务器；不要建议本地 Docker 或自托管替代方案
- 首先提供最低权限、最小变更的设置指导
- 将已确认的事实与假设区分开来
