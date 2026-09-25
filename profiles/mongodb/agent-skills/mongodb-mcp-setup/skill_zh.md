# MongoDB MCP 服务器设置

本指南将指导用户如何配置 MongoDB MCP 服务器以配合智能代理客户端使用。

## 概述

MongoDB MCP 服务器需要身份验证。用户有三个选项：

1. **连接字符串**（选项 A）：直接连接到特定集群
   - 单个集群的快速设置
   - 需要 `MDB_MCP_CONNECTION_STRING` 环境变量

2. **服务账户凭证**（选项 B）：MongoDB Atlas 管理员 API 访问
   - **推荐用于 Atlas 用户** - 简化身份验证和数据访问
   - 访问 Atlas 管理员 API 和通过 `atlas-connect-cluster` 动态连接集群
   - 无需手动管理数据库用户凭证
   - 需要 `MDB_MCP_API_CLIENT_ID` 和 `MDB_MCP_API_CLIENT_SECRET` 环境变量

3. **Atlas 本地**（选项 C）：使用 Docker 进行本地开发
   - **最适合本地测试** - 无需配置
   - 在 Docker 中本地运行 Atlas，需要安装 Docker
   - 无需凭证或云集群访问

这是一个交互式分步指南。代理会检测用户的运行环境并提供定制化说明，但**永远不会请求或处理凭证** — 用户需要在第 5 步中将这些凭证直接添加到他们的 shell 配置文件或智能代理客户端配置中。每当在第 3a 和 3b 步中提到凭证时，都要向用户明确这一点。

## 第 0 步：检测客户端

在其他任何操作之前，确定用户正在运行哪个智能代理客户端。这控制了第 1 步和第 5 步中凭证的配置方式。

运行：

```bash
env | grep "^CODEX_"
```

- **如果不存在 `CODEX_*` 变量** → 用户正在运行基于 shell 的客户端（Claude、Cursor、Gemini CLI、Copilot CLI 等）。凭证通过 shell 配置文件环境变量配置。
- **如果存在任何 `CODEX_*` 变量** → 用户正在运行 **Codex**。凭证存储在 `~/.codex/config.toml`（macOS/Linux）或 `%USERPROFILE%\.codex\config.toml`（Windows）中，而不是在 shell 环境变量中。桌面应用程序在从 Finder、Launchpad 或 Windows 开始菜单启动时不会继承 shell 环境变量。

将此**客户端类型**（Codex 与基于 shell）传递到所有后续步骤。

## 第 1 步：检查现有配置

检查凭证是否已经配置。

**对于基于 shell 的客户端** — 检查当前环境：

```bash
env | grep "^MDB_MCP" | sed '/^MDB_MCP_READ_ONLY=/!s/=.*/=[set]/'
```

**对于 Codex** — 搜索 `~/.codex/config.toml`（macOS/Linux）或 `%USERPROFILE%\.codex\config.toml`（Windows）：

```bash
grep -E 'MDB_MCP_(CONNECTION_STRING|API_CLIENT_ID|API_CLIENT_SECRET|READ_ONLY)' ~/.codex/config.toml 2>/dev/null | sed '/MDB_MCP_READ_ONLY/!s/[[:space:]]*=[[:space:]].*/ = "[set]"/'
```

**解释（两者）**：

- 如果出现 `MDB_MCP_CONNECTION_STRING` → 连接字符串认证已配置
- 如果 `MDB_MCP_API_CLIENT_ID` 和 `MDB_MCP_API_CLIENT_SECRET` 都出现 → 服务账户认证已配置。如果只有一个出现，则视为不完整。
- 如果出现 `MDB_MCP_READ_ONLY` → 只读模式已启用

**部分配置处理**：

- 用户希望向现有设置添加只读权限（已有认证，没有只读标志）→ 跳转到第 4 步
- 用户希望切换认证方法 → 解释他们应该先删除旧的凭证（Codex 的 `config.toml`，基于 shell 客户端的 shell 配置文件），然后继续第 2-5 步
- 用户希望更新凭证 → 跳转到第 5 步

**重要**：如果用户希望执行 Atlas 管理员 API 操作（管理集群、创建用户、性能顾问）但只有 `MDB_MCP_CONNECTION_STRING`，解释他们需要服务账户凭证，并引导他们完成设置。

## 第 2 步：展示配置选项

如果不存在有效配置，则展示选项：

**连接字符串（选项 A）** — 最适合：

- 单个集群访问
- 现有数据库凭证
- 自托管 MongoDB 或无需 Atlas 管理员 API

**服务账户凭证（选项 B）** — 最适合：

- MongoDB Atlas 用户（推荐）
- 多集群切换
- Atlas 管理员 API 访问（集群管理、用户创建、性能监控）

**Atlas 本地（选项 C）** — 最适合：

- 无需云设置的本地开发/测试
- 使用 Docker 最快设置，无需凭证

询问用户他们希望选择哪个选项继续。

## 第 3a 步：连接字符串设置

如果用户选择选项 A：

### 3a.1：解释如何找到连接字符串

解释如何获取他们的连接字符串：

**对于 MongoDB Atlas**：

1. 前往 [cloud.mongodb.com](https://cloud.mongodb.com)
2. 选择您的集群 → 点击 **连接**
3. 选择 **驱动程序** 或 **Shell** → 复制连接字符串
4. 将 `<username>` 和 `<password>` 替换为您的数据库用户凭证

**对于自托管 MongoDB**：

- 连接字符串通常由您的 DBA 配置或在应用程序配置中配置
- 格式：`mongodb://username:password@host:port/database`

**预期格式**：

- `mongodb://username:password@host:port/database`
- `mongodb+srv://username:password@cluster.mongodb.net/database`
- `mongodb://host:port`（本地，无认证）

继续到第 4 步（确定只读访问）。

## 第 3b 步：服务账户设置

如果用户选择选项 B：

### 3b.1：引导 Atlas 服务账户创建

引导用户创建 MongoDB Atlas 服务账户：

**完整文档**：https://www.mongodb.com/docs/mcp-server/prerequisites/

引导他们完成关键步骤：

1. **导航到 MongoDB Atlas** — [cloud.mongodb.com](https://cloud.mongodb.com)
2. **从 ORGANIZATION 部分选择您的组织** — 页面顶部靠近 ORGANIZATION 区域
3. **转到左侧边栏的“项目身份和访问”** → **应用程序** → **创建服务账户**
4. **设置权限** — 授予组织成员或项目所有者权限（请参阅文档中的确切权限映射）
5. **生成凭证** — 创建客户端 ID 和密钥
   - ⚠️ **客户端密钥只显示一次** — 立即保存它，在离开页面之前
5. **记下两个值** — 您将需要客户端 ID 和客户端密钥用于第 5 步

### 3b.2：API 访问列表配置

⚠️ **关键**：用户**必须**将他们的 IP 地址添加到服务账户的 API 访问列表中，否则所有 Atlas 管理员 API 操作都会失败。

步骤：

1. 在服务账户详情页面，找到 **API 访问列表**
2. 点击 **添加访问列表条目**
3. 添加您当前的 IP 地址。尽可能使用特定 IP 或 CIDR 范围。
   - ⚠️ **`0.0.0.0/0` 允许来自任何 IP 的访问 — 这是一个重大的安全风险。** 仅在临时测试时作为最后手段使用，并立即移除。它永远不应在生产环境中使用。
4. 保存更改

这比全局网络访问设置更安全，因为它仅影响 API 访问，而不影响数据库连接。

继续到第 4 步（确定只读访问）。

## 第 3c 步：Atlas 本地设置

如果用户选择选项 C：

### 3c.1：检查 Docker 安装

验证 Docker 是否已安装：

```bash
docker info
```

如果未安装，引导他们到：https://www.docker.com/get-started

### 3c.2：确认设置完成

Atlas 本地无需凭证 — 用户可以立即使用：

- 创建部署：`atlas-local-create-deployment`
- 列出部署：`atlas-local-list-deployments`
- 所有操作都可以直接使用 Docker 完成

**跳过第 4 步和第 5 步**（无需配置）并继续到第 6 步（下一步）。

## 第 4 步：确定只读与读写访问

**仅适用于选项 A 和 B。选项 C 跳过。**

询问他们是否希望只读或读写访问：

- **读写**（默认）：完全数据访问，允许修改
  - 最适合：开发、测试、管理任务

- **只读**：仅数据读取，不允许修改
  - 最适合：生产数据安全、报告、合规

**如果只读**：在步骤 5 中的凭证片段中包含只读标志。
**如果读写**：省略它（默认为读写）。

继续到第 5 步（配置凭证）。

## 第 5 步：配置凭证

**不要请求或处理凭证** — 提供确切说明，让用户直接添加。

### 5.1：添加凭证

**对于基于 shell 的客户端** — 将凭证存储在专门的 `~/.mcp-env` 文件中（不在 shell 配置文件中直接存储），然后从配置文件中加载它。这可以保持凭证不在通常默认为组/世界可读的文件中，并防止意外提交到 git。

**对于 Codex** — 添加到 `~/.codex/config.toml`（macOS/Linux）或 `%USERPROFILE%\.codex\config.toml`（Windows）。

向用户展示适当的片段：

**对于连接字符串（选项 A）**：

基于 shell 的客户端（`~/.mcp-env`）：

```bash
export MDB_MCP_CONNECTION_STRING="<粘贴您的连接字符串>"
```

Codex（`config.toml`）：

```toml
[mcp_servers.mongodb.env]
MDB_MCP_CONNECTION_STRING = "<粘贴您的连接字符串>"
```

**对于服务账户（选项 B）**：

基于 shell 的客户端（`~/.mcp-env`）：

```bash
export MDB_MCP_API_CLIENT_ID="<粘贴您的客户端 ID>"
export MDB_MCP_API_CLIENT_SECRET="<粘贴您的客户端密钥>"
```

Codex（`config.toml`）：

```toml
[mcp_servers.mongodb.env]
MDB_MCP_API_CLIENT_ID = "<粘贴您的客户端 ID>"
MDB_MCP_API_CLIENT_SECRET = "<粘贴您的客户端密钥>"
```

**如果选择了只读（第 4 步），也添加：**

基于 shell：在 `~/.mcp-env` 中添加 `export MDB_MCP_READ_ONLY="true"`。

Codex：在相同的 `[mcp_servers.mongodb.env]` 部分下添加 `MDB_MCP_READ_ONLY = "true"`。

⚠️ 两者 `config.toml` 和 `~/.mcp-env` 都以明文存储。不要将它们提交到版本控制。

### 5.2：完成（仅基于 shell 的客户端）

对 `~/.mcp-env` 限制权限：

```bash
# 调整 Windows 版本
chmod 600 ~/.mcp-env
```

将 `source ~/.mcp-env` 添加到 shell 配置文件（例如 `~/.zshrc`）。根据检测到的 shell 调整（例如，对于 fish：`bass source ~/.mcp-env` 或 `set -x`；对于 PowerShell：使用 `.ps1` 文件进行点源）。

通过运行 `echo $SHELL` 如果需要检测 shell 和配置文件。

### 5.3：验证

**基于 shell 的客户端** — 首先重新加载配置，然后验证：

```bash
source ~/.zshrc  # 调整以匹配配置文件
env | grep "^MDB_MCP" | sed '/^MDB_MCP_READ_ONLY=/!s/=.*/=[set]/'
```

**Codex**：

```bash
# 调整 Windows 路径
grep -E 'MDB_MCP_(CONNECTION_STRING|API_CLIENT_ID|API_CLIENT_SECRET|READ_ONLY)' ~/.codex/config.toml 2>/dev/null | sed '/MDB_MCP_READ_ONLY/!s/[[:space:]]*=[[:space:]].*/ = "[set]"/'
```

预期输出显示配置的键被省略为 `[set]`。如果什么也没有出现，请检查凭证是否已保存，并且（对于基于 shell 的客户端）配置文件是否已重新加载。

继续到第 6 步（下一步）。

## 第 6 步：下一步

### 对于选项 A & B（连接字符串 / 服务账户）：

1. **重启智能代理客户端**：
   - **基于 shell 的客户端**：完全退出客户端，然后运行 `source <profile-file>` 加载新变量，并从同一终端会话重新打开客户端，以便它继承环境。
   - **Codex**：完全退出并重新启动应用程序。不需要终端会话 — 凭证来自 `config.toml`。

2. **验证 MCP 服务器**：重启后，执行 MongoDB 操作进行测试。

3. **使用工具**：
   - 选项 A：直接数据库访问工具可用
   - 选项 B：此外还有 Atlas 管理员 API 工具和 `atlas-connect-cluster`
   - **重要（选项 B）**：确保您的 IP 在服务账户的 API 访问列表中，否则所有 API 调用都会失败

### 对于选项 C（Atlas 本地）：

1. **准备使用**：无需重启或配置！

2. **下一步**：
   - 创建部署：`atlas-local-create-deployment`
   - 列出部署：`atlas-local-list-deployments`
   - 连接后使用标准数据库操作

## 故障排除

- **`source` 后变量未出现**（基于 shell 的客户端）：检查配置文件路径并确认文件已保存
- **客户端未获取变量**：确保完全重启（退出 + 重新打开），而不仅仅是重新加载
- **Codex 桌面应用程序未获取凭证**：如果从 Finder、Launchpad 或 Windows 开始菜单启动，Codex 不会从 `.zshrc`/`.zprofile`/PowerShell 配置文件继承 shell 环境变量。使用 `~/.codex/config.toml`（macOS/Linux）或 `%USERPROFILE%\.codex\config.toml`（Windows）代替（见第 5 步）
- **无效的连接字符串格式**：重新检查格式；必须以 `mongodb://` 或 `mongodb+srv://` 开头
- **Atlas 管理员 API 错误（选项 B）**：验证您的 IP 是否在服务账户的 API 访问列表中
- **只读模式未工作**：检查是否设置了 `MDB_MCP_READ_ONLY` — Codex 的 `config.toml` 下 `[mcp_servers.mongodb.env]`，或基于 shell 客户端的 `env | grep ^MDB_MCP_READ_ONLY`
- **fish/PowerShell**：语法不同 — 使用 `set -x`（fish）或 `$env:`（PowerShell）而不是 `export`
