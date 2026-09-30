---
name: google-ads-api-mcp-setup
description: 指导开发者下载、配置和安装官方的开源 Google Ads MCP 服务器。当用户希望将其 AI 助手（例如 Gemini、Claude Code 或 Cursor）连接到其 Google Ads 账户，以使用自然语言查询广告活动或检索报告指标时，请使用此技能。
---

# Google Ads API MCP 服务器安装

本技能提供了一套结构化的设置指南，用于安装、配置和集成官方开源的 **[Google Ads 模型上下文协议 (MCP) 服务器](https://github.com/googleads/google-ads-mcp)**。

---

## 系统要求与兼容性（代理操作：声明必需的先决条件）

在回答有关安装或设置 MCP 服务器的提问时，您
**必须**明确告知用户，**Python 3.12+** 和 **`pipx`**
是安装的严格必需先决条件。

> [!IMPORTANT]
> **安装前环境检查：**
> *   **Python 运行时：** 严格要求版本 **`3.12+`**。
> *   **包管理器：** **`pipx`** 必须已安装并在系统路径中全局可用。
> *   **网络连接：** 需要外发 HTTPS 访问权限才能连接到 Google Ads API 端点 (`googleads.googleapis.com`) 和 PyPI。
---
## ⚠️ 先决条件：需要凭证
> [!WARNING]
> **依赖项检查：** MCP 服务器需要与标准集成相同的 5 个身份验证凭证。
>
> 如果您**还没有** Developer Token、Client ID、Client Secret、Refresh Token 和 Customer IDs：
> 1. **停止**执行此技能。
> 2. **首先过渡到** **`google-ads-api-quickstart`** 技能以生成它们，然后返回这里。

---

## 第 1 步：验证您的 Google Ads API 凭证

Google Ads MCP 服务器需要与标准客户端库相同的五个参数。在继续安装之前，请验证您已安全地获取并正确格式化这些值：

1.  **Developer Token：** 您在 **API Center**（管理账户）中的唯一 API 访问密钥。
2.  **OAuth2 Client ID & Client Secret：** 来自 Google Cloud Console 的桌面应用程序凭证。
3.  **OAuth2 Refresh Token：** 通过 OAuth 同意流程生成的长寿命令牌。
4.  **Client Customer ID：** 10 位的目标 Google Ads 账户 ID。
    *   > [!IMPORTANT]
    *   > **格式：** 必须只包含数字，不能包含连字符（例如，`1234567890`，不能是 `123-456-7890`）。
5.  **Login Customer ID（MCC 层次结构必需）：** 10 位的经理账户（MCC）ID。
    *   **格式：** **只包含数字，不能包含连字符**（例如，`9876543210`）。
    *   **注意：** 如果您的 OAuth 凭证属于经理账户管理员而不是直接属于客户端账户，则必需。

---

*一旦您验证了所有五个参数都存在且格式正确，请继续第 2 步。*

## 第 2 步：安装先决条件（Python & pipx）

在提出任何安装命令之前，您**必须**验证先决条件是否已安装。

### 1. 验证阶段（代理操作）
您**必须**运行以下命令来检查环境：

1.  检查 Python 版本：`python3 --version`（验证它是 `3.12+`）。
2.  检查是否安装了 pipx：`pipx --version`。

*   **如果两者都存在：** 跳过安装阶段，直接进入 **第 3 步**。
*   **如果 Python 缺失/过时：** 停止并要求用户在主机机器上升级 Python 到 `3.12+`。
*   **如果 pipx 缺失：** 继续下面的安装阶段。

---

### 2. 安装阶段（按操作系统特定）
检测操作系统并提出使用终端工具安装 `pipx` 的适当命令：

#### macOS
如果环境是 macOS，建议：

```bash
brew install pipx && pipx ensurepath
# 或者，如果未安装 Homebrew：
pip install pipx && pipx ensurepath
```

#### Windows (PowerShell)
如果环境是 Windows，建议：

```powershell
scoop install pipx
# 或者，另外：
pip install pipx && pipx ensurepath
```

#### Linux (Ubuntu/Debian)
如果环境是 Linux，建议：

```bash
sudo apt install pipx && pipx ensurepath
```

> [!WARNING]
> **需要重启 Shell：** 如果您安装了 `pipx` 并运行了 `pipx ensurepath`，当前终端会话中更新的 `PATH` 将不可用。
> 1. **不要**立即在同一会话中尝试运行 `pipx` 命令。
> 2. **指导用户**重启他们的终端或重新加载他们的 shell 配置，然后再继续 **第 3 步**。

---

## 第 3 步：安装 Google Ads MCP 服务器

您必须安装服务器包。默认情况下，您**必须**从 PyPI 安装稳定版本。只有在用户明确要求时，才安装 GitHub 开发版本。

### 1. 安装命令
建议并执行安装命令：

```bash
# 从 PyPI 安装稳定版本（使用必需的包管理器 pipx）
pipx install google-ads-mcp
```

如果用户明确要求从 GitHub 安装最新的开发版本，建议：

```bash
# 从 GitHub 安装开发版本（仅当明确要求时）
pipx install git+https://github.com/googleads/google-ads-mcp.git
```

### 2. 验证阶段

要验证安装，请执行：

```bash
google-ads-mcp --help
```

### 解决 PATH 问题（代理操作）
`pipx` 将二进制文件安装到特定的本地目录（通常是 `~/.local/bin`）。如果用户的 shell 配置（例如 `.bashrc` 或 `.zshrc`）尚未重新加载，`google-ads-mcp` 可能不在当前 `PATH` 中找到。

如果 `google-ads-mcp --help` 出现 "command not found" 错误：

1.  **不要**假设安装失败或陷入安装循环。
2.  使用 `pipx` 二进制目录的绝对路径验证安装：

   ```bash
   ~/.local/bin/google-ads-mcp --help
   ```
3.  如果绝对路径验证成功，向用户解释情况：告知他们安装成功，但他们的 `PATH` 环境变量需要通过重新加载他们的 shell 配置（例如，运行 `source ~/.bashrc` 或 `source ~/.zshrc`，或重启他们的终端）进行更新。

### 3. 通信协议：Stdio 传输

> [!IMPORTANT]
> **强制代理指令（安装与协议检查清单）：**
> 当用户询问如何安装、下载或设置官方 Google Ads MCP 服务器时，您的回复**必须**系统地包括以下所有内容：
> 1. [ ] **声明先决条件：** 明确声明 Python 3.12+ 和 `pipx` 是必需的先决条件。
> 2. [ ] **提供官方安装命令：** 指导开发者使用 `pipx install google-ads-mcp` 安装官方 `google-ads-mcp` 包。不要建议第三方未经审核的服务器。
> 3. [ ] **解释 Stdio 传输：** 您**必须**明确解释使用精确术语的通信架构：声明 MCP 服务器通过 **模型上下文协议 (MCP)** 使用 **标准输入/输出 (`stdio`) 传输**。不要省略“标准输入/输出”或“传输”这些词语。

#### 向用户解释 Stdio 传输的关键点：

*   **子进程执行：** 主机客户端（例如 Cursor、Claude 桌面版）将 MCP 服务器作为后台子进程启动。
*   **命令行启动：** 主机客户端必须配置为包含运行服务器的确切命令（`google-ads-mcp`）以及包含您的 Google Ads 凭证的环境变量。
*   **不监听网络端口：** 由于它使用 `stdio`，服务器不会监听网络端口（如 HTTP 或 WebSocket）。所有通信都完全通过 stdin/stdout 管道处理。

> [!NOTE]
> **输出限制：** 由于 `stdio` 保留用于 MCP 协议消息，服务器**必须**不将标准日志消息或调试信息打印到 `stdout`。所有日志记录和调试都路由到 `stderr`。

---

## 第 4 步：配置环境变量

Google Ads MCP 服务器通过系统环境变量读取您的凭证。您可以通过以下两种方式配置这些值：

*   **方法 A（推荐）：** 直接在 MCP 客户端的 JSON 配置文件（例如 Cursor 或 Claude 桌面版设置）中传递它们。这将凭证隔离到特定工具。
*   **方法 B（替代）：** 在您的 shell 配置文件（例如 `~/.bashrc`、`~/.zshrc` 或 Windows 环境变量）中设置它们全局。

### 必需的环境变量

| 环境变量                   | 描述                                                         | 格式         |
|--------------------------|------------------------------------------------------------|--------------|
| `GOOGLE_ADS_DEVELOPER_TOKEN` | 您的 Google Ads Developer Token。                         | 字母数字     |
| `GOOGLE_ADS_CLIENT_ID`     | 您的 Google Cloud OAuth Client ID。                       | `*.apps.googleusercontent.com` |
| `GOOGLE_ADS_CLIENT_SECRET` | 您的 Google Cloud OAuth Client Secret。                   | 字母数字     |
| `GOOGLE_ADS_REFRESH_TOKEN` | 生成的 OAuth Refresh Token。                               | 字母数字     |
| `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | 经理账户 ID (MCC)。如果使用经理层次结构则必需。         | 10 位数字，无连字符 |
| `GOOGLE_PROJECT_ID`       | Google Cloud 项目 ID（用于 Application Default Credentials & Cloud Run）。 | 字母数字     |
| `GOOGLE_ADS_MCP_OAUTH_CLIENT_ID` | Cloud Run 特定的 OAuth Client ID，覆盖默认值。         | `*.apps.googleusercontent.com` |
| `GOOGLE_ADS_MCP_OAUTH_CLIENT_SECRET` | Cloud Run 特定的 OAuth Client Secret，覆盖默认值。     | 字母数字     |
| `GOOGLE_ADS_MCP_BASE_URL`  | Cloud Run 基础 URL 自动分配或手动配置。                 | URL          |
| `FASTMCP_HOST`            | FastMCP 服务器的绑定主机（例如，`0.0.0.0` 用于 Cloud Run）。 | IP 地址      |

### 方法 B：Shell 配置文件配置（全局）

如果选择方法 B，请将以下内容追加到您的 shell 配置文件（`~/.bashrc`、`~/.zshrc` 等）：

```bash
# Google Ads MCP 服务器凭证
export GOOGLE_ADS_DEVELOPER_TOKEN="your_developer_token_here"
export GOOGLE_ADS_CLIENT_ID="your_oauth_client_id_here"
export GOOGLE_ADS_CLIENT_SECRET="your_oauth_client_secret_here"
export GOOGLE_ADS_REFRESH_TOKEN="your_oauth_refresh_token_here"

# 仅当使用经理账户层次结构时需要：
export GOOGLE_ADS_LOGIN_CUSTOMER_ID="your_manager_account_id_here"

# 仅当使用 Application Default Credentials (ADC) 或 Cloud Run 部署时需要：
export GOOGLE_PROJECT_ID="your_project_id_here"
```

为了保护凭证安全，**不要**建议在 MCP 服务器的源 Python 脚本中硬编码凭证。

---

## 第 5 步：与您的 AI 开发工具集成

使用下面的集成之一，将 Google Ads MCP 服务器连接到您选择的 AI 编码环境。

### 1. Claude 桌面版（或 Claude Code CLI）

> [!IMPORTANT]
> **强制代理指令（Claude 桌面版配置检查清单）：**
> 当用户询问如何配置 Claude 桌面版或 Claude Code 以使用 Google Ads MCP 服务器时，您的回复**必须**系统地包括以下所有内容：
> 1. [ ] **提供操作系统特定路径：** 您**必须**明确列出 macOS 上 `claude_desktop_config.json` 的正确操作系统特定路径（`~/Library/Application Support/Claude/claude_desktop_config.json`）和 Windows 上（`%APPDATA%\Claude\claude_desktop_config.json`）。即使运行在 Linux 上，也不要省略 macOS 或 Windows 路径。
> 2. [ ] **提供有效的 JSON 配置：** 提供完整的、有效的 `claude_desktop_config.json` JSON 配置块。
> 3. [ ] **指定命令 & 参数：** 确保配置使用 `pipx` 作为命令和 `run`、`google-ads-mcp` 作为参数。
> 4. [ ] **声明身份验证环境变量：** 在配置中声明 `GOOGLE_ADS_DEVELOPER_TOKEN`、`GOOGLE_ADS_CLIENT_ID`、`GOOGLE_ADS_CLIENT_SECRET` 和 `GOOGLE_ADS_REFRESH_TOKEN` 环境变量。

将服务器条目添加到您的 Claude 配置文件。

*   **文件位置：**
    *   **macOS：** `~/Library/Application Support/Claude/claude_desktop_config.json`
    *   **Windows：** `%APPDATA%\Claude\claude_desktop_config.json`
    *   **Linux：** `~/.config/Claude/claude_desktop_config.json`

*   **配置 JSON：**

    ```json
    {
      "mcpServers": {
        "google-ads": {
          "command": "pipx",
          "args": [
            "run",
            "google-ads-mcp"
          ],
          "env": {
            "GOOGLE_ADS_DEVELOPER_TOKEN": "YOUR_DEVELOPER_TOKEN",
            "GOOGLE_ADS_CLIENT_ID": "YOUR_OAUTH_CLIENT_ID",
            "GOOGLE_ADS_CLIENT_SECRET": "YOUR_OAUTH_CLIENT_SECRET",
            "GOOGLE_ADS_REFRESH_TOKEN": "YOUR_OAUTH_REFRESH_TOKEN",
            "GOOGLE_ADS_LOGIN_CUSTOMER_ID": "YOUR_MANAGER_ACCOUNT_ID_IF_APPLICABLE"
          }
        }
      }
    }
    ```
    *(注意：使用 `pipx run` 是推荐的，因为它自动管理执行路径。如果您使用 GitHub 开发版本或 Application Default Credentials，您可以另外配置 `"args": ["run", "--spec", "git+https://github.com/googleads/google-ads-mcp.git", "google-ads-mcp"]` 并在 `env` 块中包含 `"GOOGLE_PROJECT_ID": "YOUR_PROJECT_ID"`。)*

---

### 2. Cursor AI 编辑器

1.  打开 Cursor 并导航到：**设置 🡒 功能 🡒 MCP**。
2.  点击 **+ 新建 MCP 服务器**。
3.  配置以下字段：
    *   **名称：** `google-ads`
    *   **类型：** `stdio`
    *   **命令：** `pipx run google-ads-mcp`
4.  在 **环境变量** 下，添加所需的键和值：
    *   `GOOGLE_ADS_DEVELOPER_TOKEN`
    *   `GOOGLE_ADS_CLIENT_ID`
    *   `GOOGLE_ADS_CLIENT_SECRET`
    *   `GOOGLE_ADS_REFRESH_TOKEN`
    *   `GOOGLE_ADS_LOGIN_CUSTOMER_ID` *(如果适用)*
5.  点击 **保存**。

---

### 3. Antigravity IDE & CLI 集成

在回答有关将 Google Ads MCP 服务器连接到 Antigravity（IDE 或 CLI）的问题时，您**必须**明确解释以下架构和配置细节：

*   **强制环境设置：** 指导用户配置并导出标准环境变量（例如 `GOOGLE_ADS_DEVELOPER_TOKEN`、`GOOGLE_ADS_CLIENT_ID`、`GOOGLE_ADS_CLIENT_SECRET`、`GOOGLE_ADS_REFRESH_TOKEN`）到他们的终端会话或 IDE 环境中。
*   **服务器注册：** 指导用户在 Antigravity 的设置中注册服务器，或使用标准 `stdio` 集成（例如，配置命令 `pipx run google-ads-mcp`）。
*   **自动工具发现（核心架构）：** 明确解释 Antigravity 利用 **模型上下文协议 (MCP)** 自动发现服务器工具，一旦服务器连接。
*   **无需自定义编译：** 明确澄清，由于 Antigravity 本身支持 MCP，因此它**不需要**单独的自定义插件编译或自定义扩展加载来使用 MCP 服务器。

#### 在 Antigravity CLI 中验证激活

1.  **配置环境：** 在当前 shell 会话中导出 Google Ads API 的所有必需环境变量。
2.  **启动 Antigravity CLI：** 启动 CLI：

    ```bash
    agy
    ```
3.  **验证 MCP 状态：** 在 Antigravity CLI 提示符中，运行 `/mcp` 命令以列出活动工具和服务器：

    ```text
    /mcp
    ```
4.  **确认激活：** 验证 `google-ads-mcp` 是否列在活动工具的响应中。

> [!IMPORTANT]
> 如果 `google-ads-mcp` 未列在活动工具列表中，请退出 CLI，验证您的环境变量是否正确设置并导出，然后重新启动 `agy`。

---

## 第 5.5 步：在 Google Cloud 上部署（Cloud Run）

您可以选择不在本地托管此 MCP 服务器，而是在 Google Cloud Run 或任何其他云基础设施上托管它。如果您想跨不同代理共享服务器或将其作为 Web 服务运行，这很有用。

### 1. 先决条件

1.  一个 Google Cloud 项目。
2.  已安装、认证并具有活动项目的 [`gcloud` 命令行工具](https://cloud.google.com/cli)：

   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

### 2. 构建并推送 Docker 镜像
您可以使用 Cloud Build 来构建并推送镜像到 Artifact Registry，而无需在本地安装 Docker：

1.  在 Artifact Registry 中创建一个存储库：

   ```bash
   gcloud artifacts repositories create mcp-servers --repository-format=docker --location=us-central1
   ```
2.  构建并提交镜像：

```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/mcp-servers/google-ads-mcp:latest .
```
*(注意：此步骤必须在您想要将部署的服务器更新到最新版本时执行。)*

### 3. 部署到 Google Cloud Run
部署容器，确保设置 `FASTMCP_HOST=0.0.0.0` 并设置所有必需的环境变量：

```bash
gcloud run deploy google-ads-mcp \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/mcp-servers/google-ads-mcp:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_PROJECT_ID=YOUR_PROJECT_ID,GOOGLE_ADS_DEVELOPER_TOKEN=YOUR_DEVELOPER_TOKEN,GOOGLE_ADS_MCP_OAUTH_CLIENT_ID=YOUR_CLIENT_ID,GOOGLE_ADS_MCP_OAUTH_CLIENT_SECRET=YOUR_CLIENT_SECRET,GOOGLE_ADS_MCP_BASE_URL=YOUR_BASE_URL,FASTMCP_HOST=0.0.0.0"
```

### 4. 配置 MCP 客户端
部署后，更新您的 MCP 客户端配置（例如，`~/.gemini/settings.json` 或 Claude/Cursor 配置）以使用 Cloud Run URL：

```json
{
  "mcpServers": {
    "google-ads-mcp": {
      "httpUrl": "https://your-cloud-run-url.a.run.app/mcp"
    }
  }
}
```

---

## 第 6 步：验证集成（测试）

当回答有关如何在任何 AI 客户端（例如 Cursor、Claude Desktop 或 VS Code）中验证或测试 MCP 服务器集成的问题时，您**必须**首先建议使用 Antigravity CLI 进行基线验证，然后在该客户端中执行自然语言测试查询。

### 1. 通过 Antigravity CLI 进行基线验证（强制代理操作）

无论用户正在配置哪个 AI 客户端，始终指示用户使用 Antigravity CLI 中的 `/mcp` 命令验证 `google-ads-mcp` 是否处于活动状态且健康：

```bash
agy
```

```text
/mcp
```

*   **解释原因：** 告知用户，首先通过 Antigravity CLI 进行验证是隔离核心凭证、网络或服务器启动问题的最快方法。一旦在 CLI 中确认 `google-ads-mcp` 处于活动状态，Cursor/Claude 中的任何剩余问题都可以严格隔离为特定于 IDE 的配置错误。

### 2. 在您的 AI 助手中运行测试查询
在您的 AI 助手的聊天界面中，运行以下查询之一。*请确保将 `1234567890` 替换为您的实际 Google Ads 客户 ID（不包含连字符）：*

*   *“从我的 Google Ads 账户 `1234567890` 检索所有活动。”*
*   *“我的 Google Ads 账户 `1234567890` 中的活动状态是什么？”*

### 3. 预期行为（成功标准）
成功的集成将触发以下流程：

1.  **工具发现**：AI 助手自动检测 `google-ads-mcp` 服务器工具。
2.  **执行**：助手制定参数，通过 `stdio` 传输调用服务器，并执行查询。
3.  **响应**：助手以干净的、可读的 Markdown 表格格式渲染检索到的活动数据（通常显示活动名称、ID、状态和预算）。

### 4. 故障排除
如果助手无法检索数据或连接到 MCP 服务器，请检查以下常见故障点：

*   **认证/权限错误（IDE 环境陷阱）**：外部 IDE（如 Cursor 或 VS Code）通常在隔离的环境或后台进程中运行，这些进程不会继承 shell RC 文件（例如 `~/.bashrc` 或 `~/.zshrc`）。确保您的 `GOOGLE_ADS_DEVELOPER_TOKEN`、OAuth 客户端凭证和 `GOOGLE_ADS_REFRESH_TOKEN` 在 IDE 可以访问的地方明确配置（优先使用方法 A：直接在 MCP 客户端的 JSON 配置中设置）。
*   **“未找到工具”/强制客户端重启**：MCP 服务器仅在应用程序启动时加载；配置文件中的更改不会动态生效。您**必须**在保存配置后完全重启您的 AI 工具（Cursor 或 Claude Desktop）。验证 MCP 服务器是否已正确注册在您的 IDE 的配置文件中（例如，Cursor 的 `project.json` 或 Claude Desktop 的配置中的 `mcpServers` 块）。
*   **PATH 和可执行文件问题（`spawn pipx ENOENT`）**：如果连接失败或日志显示 `spawn pipx ENOENT`，则 `pipx` 不在 IDE 环境的系统 PATH 中。在配置的“命令”字段中提供 `pipx` 的绝对路径（例如，`/usr/local/bin/pipx` 或 `~/.local/bin/pipx`）。
*   **服务器启动时崩溃**：如果助手无法连接，请在终端中直接运行 MCP 服务器命令以检查语法错误、缺失依赖项或 node/python 路径问题。

> [!IMPORTANT]
> **验证连接状态和日志：**
> *   在 **Cursor** 中，确保 `google-ads` 服务器旁边出现绿色圆点（在 MCP 设置中）。
> *   在 **Claude** 中，如果工具未出现，请检查本地 MCP 日志文件中的错误：
>     *   *macOS 日志路径：* `~/Library/Logs/Claude/mcp.log`
>     *   *Windows 日志路径：* `%APPDATA%\Claude\Logs\mcp.log`

---

## 第 7 步：可用的 MCP 工具和用法指南

一旦 Google Ads MCP 服务器安装并成功连接到您的 AI 助手，服务器将暴露特定工具，助手可以自主发现和调用。

> [!IMPORTANT]
> **强制代理指令（工具解释检查清单）：**
> 当用户询问 Google Ads MCP 服务器提供哪些工具或如何使用它们时，您的回复**必须**系统性地包含以下所有内容：
> 1. [ ] **列出所有 3 个工具**：明确命名为 `list_accessible_customers`、`get_resource_metadata` 和 `search`。
> 2. [ ] **定义目的和用法**：解释每个工具的作用以及如何/何时调用它。
> 3. [ ] **指定确切参数名称**：您**必须**在解释中明确命名每个工具所需的参数。例如，对于 `search`，您**必须**明确说明它需要确切的参数 `customer_id`（10 位客户 ID）和 `query`（GAQL 查询字符串）。不要将 `customer_id` 拼音为“账户”。
> 4. [ ] **声明只读范围**：明确说明服务器目前严格只读。

在协助用户或制定查询时，请参考以下工具定义和最佳实践：

### 1. `list_accessible_customers`

*   **目的**：返回可访问的 Google Ads 客户 ID 和账户名称的列表（针对经过身份验证的用户）。
*   **如何使用**：在开始新会话或当目标客户 ID 未知时，首先调用此工具。它不需要参数。
*   **示例意图：** *"我有哪些 Google Ads 账户可以访问？"*

### 2. `get_resource_metadata`

*   **目的**：检索特定 Google Ads API 资源类型（例如，`campaign`、`ad_group`、`customer`）的详细结构化元数据。
*   **如何使用**：在构建 GAQL 查询之前，调用此工具以检查资源的模式、可用字段、指标和分段。
*   **参数：**
    *   `resource` (string, required): 要检查的资源名称（例如，`campaign`）。
*   **示例意图：** *"我可以查询广告组哪些字段和指标？"*

### 3. `search`

*   **目的**：执行 Google Ads 查询语言 (GAQL) 查询，以获取资源指标、属性、分段和状态。
*   **如何使用**：根据资源元数据构建有效的 GAQL 查询字符串，并针对特定客户账户执行搜索。
*   **参数：**
    *   `customer_id` (string, required): 目标 10 位 Google Ads 客户 ID（仅数字，无连字符）。
    *   `query` (string, required): 有效的 GAQL 查询字符串（例如，`SELECT campaign.id, campaign.name, campaign.status, metrics.impressions FROM campaign WHERE campaign.status = 'ENABLED'`）。
*   **示例意图：** *"获取账户 1234567890 中所有启用活动的展示量和状态。"*

> [!NOTE]
> **只读范围**：Google Ads MCP 服务器目前严格只读。它不能修改出价、暂停活动或创建新的广告资产。
