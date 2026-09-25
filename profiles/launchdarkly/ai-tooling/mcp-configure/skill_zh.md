# LaunchDarkly MCP 服务器配置（引导）

配置 LaunchDarkly 托管的 MCP 服务器，以便标志管理技能和引导可以使用 MCP 工具。使用 OAuth 进行身份验证——托管服务器不需要 API 密钥。

此技能嵌套在 [LaunchDarkly 引导](../SKILL.md) 下；父技能在第一个标志工作后将其移交给这里。

## 前置条件

- 一个 LaunchDarkly 账户（当引导用户注册时，使用来自父技能 [来源归因](../SKILL.md#source-attribution) 的解析注册 URL；默认：`https://app.launchdarkly.com/signup?source=agent`）
- 一个兼容 MCP 的编码代理

## 托管的 MCP 服务器

LaunchDarkly 为所有功能提供了一个统一的托管 MCP 服务器：

| 服务器      | URL                                             | 目的                       |
| ----------- | ----------------------------------------------- | ----------------------------- |
| LaunchDarkly (统一) | `https://mcp.launchdarkly.com/mcp/launchdarkly` | 功能标志和 AgentControl |

传统的 `mcp/fm` 和 `mcp/aiconfigs` URL 已**弃用**——将任何现有用法迁移到统一服务器（见 [边缘情况](#edge-cases)）。

对于引导，只需要统一服务器。

## 工作流程

### 第 1 步：检测代理

如果父引导技能已经识别了代理，请使用该上下文。否则，从代理特定的目录、配置文件以及您在运行时可用的工具中推断。不要询问用户——选择最匹配的选项。

### 第 2 步：尝试快速安装

最快的路径是快速安装链接。向用户展示它：

**LaunchDarkly MCP:** [https://mcp.launchdarkly.com/mcp/launchdarkly/install](https://mcp.launchdarkly.com/mcp/launchdarkly/install)

**重要：告诉用户点击链接后会发生什么。** 安装链接可能会在浏览器中打开，但授权或“添加服务器”提示通常出现在**编码环境**中（代理运行的编辑器或主机应用程序），而不是在浏览器中。在展示链接后，立即包含类似以下指导：

- 点击链接后，在您的编码环境（此对话运行的编辑器）中观察批准对话框、“添加 MCP 服务器”提示或工具/集成面板通知。
- 浏览器可能会启动 OAuth 流，但您可能需要在编辑器本身中确认或批准服务器。
- **如果没有提示出现：**检查编辑器的 MCP、集成或工具设置区域，查看服务器是否已添加但需要启用。如果根本找不到，则回退到手动设置（第 3 步以下）。

如果快速安装链接不起作用（代理不支持它，或用户更喜欢手动设置），请继续到第 3 步。

### 第 3 步：手动配置

定位检测到的代理的 MCP 配置文件并添加托管服务器条目。参见 [MCP 配置模板](references/mcp-config-templates.md) 获取每个代理的确切 JSON。

| 代理          | 配置文件位置                                       |
| -------------- | ---------------------------------------------------------- |
| Cursor         | `.cursor/mcp.json` (项目) 或全局 Cursor 设置     |
| Claude Code    | `.mcp.json` (项目) 或 `~/.claude.json` (全局)         |
| GitHub Copilot | GitHub.com 上的 **设置** → Copilot → 云代理 → MCP (见 [MCP UI 链接](references/mcp-ui-links.md)) |
| Windsurf       | 代理特定的 MCP 配置                                  |

**添加用于引导的统一 LaunchDarkly 服务器。** 此单个服务器处理功能标志和 AgentControl。

### 第 4 步：代理特定的授权

写入配置后，某些代理需要额外步骤。**不要**仅通过长手动菜单路径发送用户——使用 [MCP UI 链接](references/mcp-ui-links.md)（HTTPS 文档 + `command:` 快捷方式用于 VS Code / Cursor）。

**Cursor:**

1. 使用 [Cursor MCP 文档链接和应用程序内快捷方式](references/mcp-ui-links.md#clients) 在 Cursor 中打开 MCP（例如，当可点击时通过 `command:` 链接进行设置搜索）。
2. 切换 **LaunchDarkly**（或配置中的名称）。
3. 点击 **连接** 以使用 LaunchDarkly 账户进行授权。

**VS Code (当适用时):**

- 使用 [VS Code MCP 文档 + `mcp.json` / 设置链接](references/mcp-ui-links.md#clients)；如果提示，请信任或启动服务器。

**Claude Code:**

- 授权在第一次 MCP 工具调用时通过 OAuth 提示自动发生。基于文件的设置：[Claude Code MCP 文档](https://docs.claude.com/en/docs/claude-code/mcp)。

**GitHub Copilot:**

- 在仓库设置中添加 MCP 配置后点击 **保存**。使用 [GitHub Copilot MCP 文档](https://docs.github.com/en/copilot/customizing-copilot/extending-copilot-coding-agent-with-mcp) 获取 github.com 上的确切 **设置** 路径。

### 第 5 步：验证 MCP 工具（无需强制重启）

Cursor 或 Claude Code 启用 MCP 服务器后不再需要重启。立即探测工具，用户确认已启用并授权服务器后。

1. **告诉用户启用和授权服务器。** 在 Cursor 中：在 MCP 设置中切换 LaunchDarkly 服务器并点击 **连接**。在 Claude Code 中：第一次工具调用时会出现 OAuth 提示。**不要**告诉他们重启。

2. **立即探测。** 用户确认服务器已启用后，调用轻量级 MCP 工具（例如，使用用户项目密钥的 `list-feature-flags`）。不要询问用户 MCP 是否正常工作——只需尝试。
   - **成功**（正常响应，即使空标志列表）：MCP 已启用。继续。
   - **授权错误**（401、403、“未授权”、“禁止”或 OAuth 相关消息）：服务器被找到但授权失败。转到第 3a 步。
   - **工具未找到或超时**（工具未识别、连接拒绝、无响应）：编辑器尚未拾取服务器。转到第 3b 步。

3a. **授权失败路径。** MCP 服务器可访问，但 OAuth 不完整或过期——重启编辑器不会帮助。
   - 告诉用户：“MCP 服务器响应，但授权失败。在 Cursor 中：打开 MCP 设置，找到 LaunchDarkly 服务器，并点击 **连接** 以重新授权。在 Claude Code 中：下一个 MCP 工具调用应重新触发 OAuth 提示。”
   - 使用 [MCP UI 链接](references/mcp-ui-links.md) 给用户一个直接快捷方式到其代理的 MCP 设置。
   - 用户确认重新授权后重新探测。
   - 如果重新探测成功：继续引导。
   - 如果再次失败：提供重试简短提示（见第 4 步以下）。对于持久的授权问题**不要**建议重启。

3b. **服务器未找到路径。** 编辑器可能尚未加载新的 MCP 配置。
   - 告诉用户：“MCP 工具尚未可见。某些编辑器需要重启才能拾取新的 MCP 服务器。重启您的编辑器，当您回来时说 **'继续 LaunchDarkly 引导'**——我会从这里继续。”
   - 具体说明如何重启：“重启 Cursor” / “重新加载 Claude Code” / “刷新 Copilot 代理” 取决于第 1 步检测到的内容。

4. **重启后继续：** 父引导技能检测到活动状态，因此不需要日志文件。当下一个回合开始时：
   - 沉默地重新探测 MCP 工具。
   - 如果工具现在可用：“MCP 已连接。” 继续引导。
   - 如果工具仍然缺失：**不要**阻塞引导的其余部分——剩余步骤必须在没有 MCP 的情况下仍然可以完成。提供一条简短提示以供稍后重试：“您随时可以通过点击 [快速安装链接] 并重启来设置 MCP。”

5. 如果失败看起来像配置问题（错误的文件路径、服务器未启用），请提及可能的原因，以便用户自行修复——但不要阻止进度。

## 边缘情况

- **用户已经配置了 MCP：** 通过检查配置中的现有 LD MCP 条目来验证。如果统一服务器 (`mcp/launchdarkly`) 存在且正常工作，请跳过配置。如果存在弃用的 `mcp/fm` 或 `mcp/aiconfigs`，见下文。
- **用户有弃用的 `mcp/aiconfigs` 或 `mcp/fm` 服务器：** 这些 URL 已弃用。**不要**自动迁移。使用阻塞问题：

```json
{
  "questions": [
    {
      "id": "legacy_migration",
      "prompt": "我在您的配置中找到一个弃用的 LaunchDarkly MCP URL (mcp/fm 或 mcp/aiconfigs)。它应该被替换为统一的 LaunchDarkly 服务器 (mcp/launchdarkly)，该服务器处理功能标志和 AgentControl。您想让我迁移吗？",
      "options": [
        { "id": "yes", "label": "是，删除旧服务器并添加统一服务器" },
        { "id": "no", "label": "否，暂时保持原样" }
      ]
    }
  ]
}
```

  - 如果 **是**：删除弃用的条目，确保存在统一的 `mcp/launchdarkly` 服务器（如果已存在，则不要重复），然后继续。
  - 如果 **否**：保持配置不变并继续引导——弃用服务器可能目前仍然可以工作。

- **用户有旧的基于 npx 的本地服务器：** 将他们迁移到托管服务器。删除旧的 `npx @launchdarkly/mcp-server` 条目和任何 `LD_ACCESS_TOKEN` 环境变量。替换为托管服务器配置。
- **代理不在已知列表中：** 提供通用模式：用户需要添加一个指向 `https://mcp.launchdarkly.com/mcp/launchdarkly` 的 MCP 服务器条目，使用其代理期望的格式。
- **用户在引导期间选择退出 MCP：** 记录该选择并继续；不要阻塞 SDK 工作。

## 不要做的事情

- 不要配置基于 npx 的本地服务器。始终使用托管服务器。
- 不要询问或存储 API 密钥。托管服务器使用 OAuth。
- 不要自动从弃用的 `mcp/aiconfigs` 迁移——始终通过阻塞问题询问。
- 不要建议重启作为第一步——在用户启用服务器后立即探测工具。
- 不要建议重启用于授权错误（401/403）——服务器已被找到，重启不会帮助。指导用户重新授权而不是重启。

## 参考

- [MCP UI 链接](references/mcp-ui-links.md) — HTTPS + `command:` 链接，用于打开 MCP 设置（Cursor、VS Code、Claude Code、Windsurf、GitHub）
- [MCP 配置模板](references/mcp-config-templates.md) — 每个代理的托管 OAuth JSON；从弃用配置迁移
- [官方 MCP 文档](https://launchdarkly.com/docs/home/getting-started/mcp-hosted) — 完整托管设置指南
