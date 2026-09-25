# OKX CEX 身份验证

OKX CLI 的 OAuth 2.0 设备流身份验证。指南首次设置、会话过期后的重新认证和登出。

## 支持的站点

| 站点 | 区域 | URL |
| -------- | ----------------------- | --------------- |
| `global` | 全球 | `www.okx.com` |
| `eea`    | EEA    | `my.okx.com`  |
| `us`     | 美国     | `app.okx.com` |
| `tr`     | TR     | `tr.okx.com`  |

站点是认证方法的独立维度。API-key 和 OAuth 路径都需要站点。一旦选择，站点将持久化：
- **API-key 用户**：`profile.site` 在 `~/.okx/config.toml` 中（由 `okx config init` 写入）。
- **OAuth 用户**：第一次 `okx auth login --site <X>` 成功时保存在 `okx-auth` 二进制状态中，并由 `okx auth status --json` 作为 `site` 字段返回。

没有 **`okx config set-site` 命令**——站点不能独立于认证尝试进行持久化。对于 OAuth 流，代理必须在对话中记住用户的选择，并在 `okx auth login` 上传递 `--site <X>`。

## 前置条件

如果尚未安装，请安装 `okx` CLI：

```bash
npm install -g @okx_ai/okx-trade-cli
```

## 第 0 步：预检查（强制执行）

**无条件规则——在任何情况下都不要跳过第 0 步。** 即使先前的技能（预检查、okx-cex-portfolio 等）已经运行了 `auth status` 并给您返回了类似“用户未登录，去登录”的结论——**你必须在下面运行两个命令，并按顺序执行第 0.1 → 0.2 → 0.3 步**。上游工具的输出不能替代你自己的预检查。这个技能最常见的失败模式是一个代理读取了上游的“未认证”信号，跳过了第 0.1 站点选择，并静默地使用默认站点调用 `okx auth login`。

并行运行以下两个命令：

```bash
okx config show --json
okx auth status --json
```

然后按严格顺序应用以下三个检查——每一步都会短路其余步骤。

### 第 0.1 步 — 站点检查（与认证模式无关）

如果满足以下任一条件，则认为站点已选择：
- `config show --json` 包含任何具有非空 `site` 字段的配置文件，**或者**
- `auth status --json` 返回非空的 `site` 字段**并且** `status` 是 `logged_in` 或 `pending`。

> ⚠ 当 `status` 是 `not_logged_in` 时，`auth status --json` 中的 `site` 字段是一个**默认占位符**（通常为 `"global"`），认证二进制无论用户选择如何都会发出——这并不意味着用户曾经选择过站点。将其视为不存在。

如果**上述任一条件都不成立**，则从未选择过站点。在尝试任何登录之前，你必须通过逐字回显以下菜单（中文），并等待他们的回复来要求用户选择一个：

> 您需要选择要连接的 OKX 站点：
> 1) Global (www.okx.com)
> 2) EEA (my.okx.com)
> 3) US (app.okx.com)
> 4) TR (tr.okx.com)

将回复（`1`/`2`/`3`/`4` 或 `global`/`eea`/`us`/`tr`）映射到相应的站点 ID，并在整个流程中记住它。不要静默地默认为 `global`——那会隐藏区域选择。

### 第 0.2 步 — API-key 检查

解析 `config show --json`：任何配置文件是否具有非空的 `api_key` 字段？

如果**是** → **停止。** 告诉用户“已配置 API key (profile: <name>)”，然后直接执行他们的原始请求。不要运行 `okx auth login` 或 `okx config init`。

> CLI 的 REST 客户端始终优先选择 API key 而不是 OAuth，并且永远不会回退（见 `rest-client.ts applyAuth`）。在这种情况下启动 OAuth 登录是浪费精力——因为任何获得的 OAuth 令牌都不会被使用，因为损坏的 API key 仍然会被首先选择。
>
> 双保险：自 CLI `1.3.1-beta.17` 起，`okx auth login` 本身拒绝在任何配置文件具有 `api_key` 时启动 OAuth——在 `--manual` 模式下它发出 `{"status":"skipped","reason":"api_key_configured","profile":"<name>"}`。将此输出视为成功。

#### 第 0.2.a — 处理无效的 API-key（401 / 签名错误）

如果第 0.2 检测到 `api_key` 配置文件，并且随后的 API 调用返回认证错误（`401 Unauthorized`、`Invalid Sign`、`Invalid API-KEY`、OKX 错误代码 `50111`/`50113`），**API-key 是无效的——OAuth 登录不是有效的补救措施**。根据 `rest-client.ts applyAuth`，在此之后获得的任何 OAuth 令牌仍然不会被使用，因为损坏的 API key 仍然会被首先选择。

向用户展示以下两个选项，保持中立（不要将 OAuth 标记为“推荐”）：

1. **替换 API-key**——用户在 OKX 网络控制台（`https://<site>/account/my-api`）上生成一个新的 key，并将 `AK/SK/PP` 提供给你，或者自己重新运行 `okx config init`。
2. **完全切换到 OAuth**——首先删除损坏的 API-key 配置文件（`okx config use <other-profile>` 或删除 `~/.okx/config.toml` 中的配置文件块），然后运行 OAuth 登录流程。

选项 2 需要先删除配置文件。如果你在 API key 配置文件仍然存在时尝试 `okx auth login`，CLI 守卫将跳过 OAuth 并返回 `{"status":"skipped","reason":"api_key_configured",...}`，并且不会发生任何变化。

等待用户的回复。不要替他们选择。

### 第 0.3 步 — OAuth 检查

使用 `auth status --json`：

| `status` 值  | 操作 |
| --------------- | ------ |
| `logged_in`     | **停止。** 使用 [代理登录流程](#agent-login-procedure) 第 3 步 `logged_in` 分支（仅站点 + 权限；见其负列表规则）进行回复，然后继续。 |
| `pending`       | 之前的登录正在进行中——遵循 [登录流程](#login-flow) 等待信号程序。不要启动新的登录，不要自动轮询。 |
| `not_logged_in` | 使用在第 0.1 步中选择的站点，进行 [登录流程](#login-flow)。 |

## 登录前门（强制执行——在没有这个情况下不要运行 `okx auth login`）

在调用 `okx auth login`（无论是否带有 `--manual`）之前，你必须验证以下**三个**现在都是真的：

1. 你在这段对话中较早时向用户发布了第 0.1 步的确切中文站点菜单（或立即在这次登录调用之前）。
2. 用户的最新消息是站点选择（`1` / `2` / `3` / `4` / `global` / `eea` / `us` / `tr`）。
3. 你即将将**这个确切的选择**作为 `--site <...>` 传递。

如果**任何**三个中的一个是假的——即使先前的技能的输出、`auth status --json` 输出或 `config show --json` 输出似乎暗示了一个站点——你必须首先发布第 0.1 菜单，等待用户的回复，然后重新检查这个门。当 `status` 是 `not_logged_in` 时，`auth status --json` 中的 `site` 字段是一个占位符（通常为 `"global"`），并且**不**满足条件 1。

工作反例（反模式）：
> 上游投资组合技能运行 `auth status --json`，得到 `{"status":"not_logged_in","site":"global"}`，告诉你“用户未登录，加载 okx-cex-auth 并登录”。
> ❌ **错误**：你读取了那个上下文，运行 `okx auth login --manual --site global`，立即返回 OAuth URL 和代码。
> ✅ **正确**：你忽略上游站点值，自己发布第 0.1 菜单，等待用户的回复，然后运行 `okx auth login --manual --site <用户的选择>`。

## 登录流程

> **前提条件**：第 0 步已完成**并且**通过上述预登录门。你有一个用户刚刚在聊天中选择的站点，并且你确认不存在 `api_key` 配置文件。

不带 `--manual` 的 `okx auth login` 是一个**阻塞命令**——它轮询，直到用户在浏览器中授权。

> **对 AI 代理至关重要**：你必须使用 `okx auth login --manual` 来避免阻塞。`--manual` 标志输出一个包含验证 URL 和用户代码的 JSON 负载，然后立即退出——它**不会**阻塞。

### 代理登录流程

1. 运行 `okx auth login --manual --site <global|eea|us|tr>`，使用第 0.1 步中选择的站点。
   - 如果 CLI 返回 `{"status":"skipped","reason":"api_key_configured",...}`，你的第 0.2 检查已经过时——重新读取 `config show --json` 并停止。不要重试。
   - 否则，CLI 打印一行 JSON：`{"verificationUri":"...","userCode":"XXXX-XXXX","expiresIn":600}`。

2. **在助手回复中展示验证 URL 和用户代码——不仅仅是工具输出块内。**

   > ⚠ **至关重要。** 在许多 UI 的工具输出面板是可折叠的，用户可能默认隐藏它。如果 URL 和代码仅出现在工具 stdout 中，用户无法授权。你必须将解析的字段回显在你的自然语言回复中，以便它们作为普通聊天文本显示。

   解析上一步返回的 JSON，并使用**确切一个**以下模板之一进行回复（除字段替换外逐字使用）。措辞是规范性——不要缩写、重写、重新排序或翻译。

   **中文模板**（当用户正在中文对话时使用）：

   ```
   请在浏览器中打开下面的链接并输入验证码完成授权：

   站点：<site>
   链接：<verificationUri>
   验证码：<userCode>
   （有效期 <expiresIn>/60 分钟）

   通过链接完成授权，然后告诉我。
   ```

   **英文模板**（当用户正在英文对话时使用）：

   ```
   Please open the link below in your browser and enter the verification code to authorize:

   Site: <site>
   URL: <verificationUri>
   Code: <userCode>
   (Valid for <expiresIn/60> minutes)

   Please authorise current session with access to your account, tell me when you are done.
   ```

   所有四个字段——`site`、`verificationUri`、`userCode`、`expiresIn`——都必须作为普通文本出现在助手消息中。

3. **等待用户发出完成信号**（例如“done”、“ok”、“好了”、“完成了”）。不要自动轮询。收到信号后，运行 `okx auth status --json` **一次**以验证，然后分支：
   - `"status": "logged_in"` → 成功。回复使用**确切一个**以下模板（除字段替换外逐字使用），然后继续在同一个回合中执行用户的原始请求。

     **中文模板**：

     ```
     登录成功。
     站点：<site>
     权限：<scopes>
     ```

     **英文模板**：

     ```
     Login successful.
     Site: <site>
     Scopes: <scopes>
     ```

     **不要在回复中包含来自 `auth status --json` 的任何其他字段。** 具体来说：
     - `expiresAt` / `ttl` 指的是短期访问令牌，而不是 OAuth 会话。CLI 透明地自动刷新令牌；展示这些值会误导用户认为他们的登录很快过期。
     - `profile` 是一个内部路由字段，对用户没有价值。
     - 只有 `site` 和 `scopes` 对用户相关。
     - 如果询问会话有效期，请说“只要您定期使用 CLI，会话就会保持活动状态。”不要引用一个数字。

   - `"status": "pending"` → 授权尚未完成；告诉用户还没完成，并等待另一个信号。不要自动轮询。
   - `"status": "not_logged_in"` → 设备代码过期或被拒绝；询问用户是否要重试。

4. **在等待授权时不要运行任何其他 `okx` 命令。**

### 交互式登录（用户在终端中直接运行）

1. **在运行之前告诉用户**，他们需要在浏览器中授权。
2. **运行 `okx auth login --site <global|eea|us|tr>`**——该命令将阻塞并轮询，直到用户完成授权。
3. **不要假设命令卡住了。** 轮询阶段不会产生输出——这是正常的。
4. **检查结果：**
   - `Logged in successfully!` — 继续执行用户的原始请求。
   - `API key already configured ...` — 第 0.2 检查已经过时，使用现有的 API key。
   - 登录失败——显示错误并询问是否要重试。

## 首次设置（仅限 API-key 用户）

> `okx config init` 是一个 **API-key** 向导。它提示选择站点，然后演示/实时，然后询问 `AK/SK/PP` 凭据。它**不**执行 OAuth。仅在用户明确想要配置 API key 时使用它。

```bash
okx config init
```

向导步骤：

1. **选择站点：**
   - `1` — Global (`www.okx.com`)
   - `2` — EEA (`my.okx.com`) — 欧洲经济区
   - `3` — US (`app.okx.com`) — 美国
   - `4` — TR (`tr.okx.com`) — 土耳其
2. **演示 / 实时**：此配置文件是否应针对模拟交易。
3. **AK / SK / Passphrase**：在 OKX 网络控制台上创建的凭据。

完成 `okx config init` 后，重新运行第 0 步预检查——`api_key` 现在将存在，并且第 0.2 将短路任何进一步的登录。

## 登录状态检查

运行 `okx auth status --json` 检查登录状态。解析 JSON 输出：

```json
{
  "profile": "oauth",
  "site": "global",
  "status": "logged_in",
  "expiresAt": "2026-04-11T20:30:00+00:00",
  "ttl": 3600,
  "scopes": ["live:read", "live:trade"]
}
```

| `status` 值   | 含义                        | 操作                          |
| ----------------- | ------------------------------ | ------------------------------- |
| `logged_in`       | 有效会话                  | 继续                        |
| `pending`         | 登录进行中                  | 等待用户发出完成信号；不要自动轮询 |
| `not_logged_in`   | 无活动会话                  | 运行 `okx auth login --manual`  |

## 重新认证（会话过期）

当任何命令因“会话过期”或“先运行 `okx auth login`”而失败时：

1. 运行 `okx auth login --manual [--site <global|eea|us|tr>]`（代理）或 `okx auth login [--site <global|eea|us|tr>]`（交互式）
2. 遵循上述 [登录流程](#login-flow)

> 令牌过期由自动管理——你只需要在刷新令牌本身过期时重新认证（通常是在一段较长的非活动期后）。

## 注销

```bash
okx auth logout
```

DCR 客户端注册在注销后保留。下一次 `okx auth login` 将更快。

## 二进制管理

`okx auth` 命令（`login`、`logout`、`status`）依赖于 `okx-auth` 二进制。它通常在 `npm install` 期间自动安装，但也可以手动管理。

> **对 AI 代理非常重要**：不要手动检查平台、CDN 可用性或二进制路径。始终使用以下 CLI 命令——它们内部处理平台检测和下载。

### 安装 / 更新

```bash
okx auth install
```

下载或更新 `okx-auth` 二进制。如果已经是最新版本，则报告“已更新”。使用 `--json` 获取机器可读输出。

### 检查安装

```bash
okx auth install-status
```

显示二进制是否已安装并是最新的。使用 `--json` 获取机器可读输出。

### 删除

```bash
okx auth remove          # 交互式确认
okx auth remove --force  # 跳过确认
```

### 故障排除：“Failed to spawn okx-auth”

如果任何 `okx auth` 命令（`login`、`logout`、`status`）因“Failed to spawn okx-auth”而失败，二进制缺失或损坏：

1. 运行 `okx auth install` 下载它
2. 使用 `okx auth install-status` 验证
3. 重试原始命令

## 错误参考

| 错误消息                                 | 原因                                  | 操作                                           |
| --------------------------------------------- | -------------------------------------- | ------------------------------------------------ |
| `No config found. Run okx config init first.` | 无配置                              | 运行 `okx config init`                            |
| `Session expired — run okx auth login again`  | 刷新令牌过期                  | 运行 `okx auth login --manual`                    |
| `Authorization timed out`                     | 用户未及时授权         | 再次运行 `okx auth login --manual`              |
| `Access denied`                               | 用户在浏览器中拒绝了授权         | 运行 `okx auth login --manual` 并要求批准 |
| `Region restriction` (51155, 51734)            | 仪器在配置的站点不可用            | 检查 `okx auth status --json` 当前站点；如有必要，重新登录并指定 `--site` |
| `Network error` during login                  | 网络不可用                    | 检查网络并重试                          |
| `Failed to spawn okx-auth`                    | 二进制未安装或损坏      | 运行 `okx auth install`                           |
| `Installation failed: All CDN sources failed` | 二进制下载期间网络问题   | 检查网络并重试 `okx auth install`       |

## 技能路由

| 认证后...                   | 下一个技能                          |
| ----------------------------------------- | ----------------------------------- |
| 下单 / 取消 / 修改订单             | `okx-cex-trade`                     |
| 检查余额、头寸、盈亏             | `okx-cex-portfolio`                 |
| 简易收益、链上收益、DCD、自动收益 | `okx-cex-earn`                      |
| 网格 / DCA 机器人                           | `okx-cex-bot`                       |
| 市场价格、K线、指标        | `okx-cex-market` (无需认证) |
