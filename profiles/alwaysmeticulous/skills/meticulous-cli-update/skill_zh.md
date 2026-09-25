# 安装或更新 Meticulous CLI

`@alwaysmeticulous/cli` 包处于积极开发中，经常发布变更和改进。其他 Meticulous 技能假定 `meticulous` 命令位于 `PATH` 中且是最新的，因此请在任何 Meticulous 工作流程开始时运行此技能一次。

这只需要在**每次对话**中运行一次。如果你已经在本次对话中较早运行过它，请跳过它——没有必要在每次调用 Meticulous 技能时都重新检查版本或重新更新。

**使用 MCP 服务器而不是 CLI？** 步骤 1-4 是关于安装/更新 `meticulous` CLI 二进制文件及其本地认证——当在托管的 [Meticulous MCP 服务器](https://app.meticulous.ai/api/mcp) 上调用工具时，这两者都不适用，该服务器已经是最新的版本，并通过 MCP 连接本身进行认证，而不是 `meticulous auth login`。直接跳到 **步骤 5**：已安装的 **技能**（本文档集）是与 CLI/MCP 工具本身是分开的，无论你通过哪个工具调用工具，都需要保持最新。

完整的设置说明——安装 CLI、连接 MCP 服务器以及安装这些技能——位于 [app.meticulous.ai/docs/agents/setup](https://app.meticulous.ai/docs/agents/setup)。

## 如何处理安装/更新命令

此技能通常作为另一个 Meticulous 技能的子步骤运行。下面的安装/更新命令（步骤 1、3 和 5）涉及安全——它们安装软件包并连接到网络——因此应将其视为 **尽力而为且非阻塞**：

- 你通常无法提前判断命令是否被白名单。如果被白名单，它将静默运行；如果没有，尝试运行它将显示权限提示。任何结果都是可以接受的——让这种情况来告诉你。
- **如果命令需要你没有的权限**（出现提示，或用户拒绝），将其视为建议而不是强制的信号。告诉用户建议执行 XYZ——例如“建议通过运行 `npm install --global @alwaysmeticulous/cli@latest` 更新 Meticulous CLI”——然后继续。拒绝提示**不是**失败；它只是意味着“稍后执行”。
- **如果用户现在不想运行它，继续进行。** 不要停止工作流程；继续执行剩余步骤，然后返回调用技能。唯一硬性要求是 `meticulous` 命令必须存在（步骤 1）——如果它确实没有安装且用户拒绝安装，则没有任何 Meticulous 技能可以继续，所以停止。

只读检查（`meticulous --version`、`npm view …`、`meticulous auth whoami`）可以直接运行。

## 步骤 1 — 检查已安装的版本

```bash
meticulous --version
```

**如果找不到命令**，则 CLI 未安装。全局安装它（最佳尝试，见上述说明）：

```bash
npm install --global @alwaysmeticulous/cli@latest
```

如果安装不被白名单，建议用户自行运行该命令。因为没有任何 Meticulous 技能可以在没有 CLI 的情况下运行，所以这是你应该停止并等待的唯一情况——如果用户拒绝，则没有其他可以继续的。安装后，重新运行 `meticulous --version` 以确认它位于 `PATH` 上，然后跳到步骤 4。

## 步骤 2 — 检查最新发布的版本

```bash
npm view @alwaysmeticulous/cli version
```

## 步骤 3 — 如果过时则更新 CLI

如果已安装的版本与最新版本匹配，则跳到步骤 4。

否则，根据 CLI 的安装方式更新（最佳尝试，见上述说明——如果更新不被白名单，建议用户运行适当的命令并继续，无论结果如何）：

- **全局安装**（典型——`which meticulous` 解析到当前项目之外的路径）：

  ```bash
  npm install --global @alwaysmeticulous/cli@latest
  ```

- **在项目中本地安装**（`@alwaysmeticulous/cli` 出现在项目的 `package.json` 中，并且 `which meticulous` 在 `node_modules/.bin` 内解析）：
  ```bash
  npm install --save-dev @alwaysmeticulous/cli@latest
  # 或者，如果项目使用 pnpm：
  pnpm add --save-dev @alwaysmeticulous/cli@latest
  # 或者 yarn：
  yarn add --dev @alwaysmeticulous/cli@latest
  ```

如果更新运行了，重新运行 `meticulous --version` 并确认它匹配最新版本后再继续。

## 步骤 4 — 检查认证和项目选择

验证用户是否已使用 Meticulous 进行认证并选择了项目：

```bash
meticulous auth whoami
```

如果你更喜欢基于结构化输出进行分支，可以添加 `--json`——它打印 `authenticatedVia` 和 `selectedProject`。

有四种结果：

### (a) 通过 OAuth 登录，并选择了项目

```
Authenticated via: OAuth
Logged in as: Jane Smith (jane@example.com)
Organizations: acme-corp (member)
Selected project: acme-corp/Web App
```

无需操作——继续到步骤 5。

### (b) 通过 API 令牌或注入的凭证进行认证

```
Authenticated via: project API token (METICULOUS_API_TOKEN 环境变量)
Pinned project: acme-corp/Web App
```

也视为 `project API token (~/.meticulous/config.json)`、`test-run API token` 或在请求时注入的凭证（附加了 bearer 凭证到 `app.meticulous.ai` 的出站请求的代理平台）。这些凭证针对单个项目，并且已经固定，因此无需选择——**不要**运行 `meticulous auth set-project`：使用 API 令牌会导致错误（令牌绑定到一个项目），使用注入的凭证同样如此。继续到步骤 5。

### (c) “未登录”

命令退出并显示：

> Not logged in. Run `meticulous auth login`, or set METICULOUS_API_TOKEN. In terminals without a browser, use `meticulous auth login --non-interactive`.

登录是浏览器 SSO，因此人类必须始终在浏览器中完成它；使用哪个登录命令取决于你在哪里运行：

- **在用户自己的机器上**（那里的浏览器可以访问此机器的 localhost）：

  ```bash
  meticulous auth login --non-interactive
  ```

  这会打印一个登录 URL，然后等待本地回调服务器，因此请在后台运行它，然后将打印的 URL 显示给用户，并让他们打开它并完成登录。完成后，命令结束并存储令牌，然后你可以继续。

  或者，要求用户自己运行 `meticulous auth login`——在自己的终端上，它将直接打开浏览器。

- **在远程或沙盒化机器上**（云代理、SSH 会话、容器）——那里的浏览器无法访问此机器的 localhost：

  ```bash
  meticulous auth login --device
  ```

  这使用 OAuth 设备流程：它打印一个 URL 和一个简短的代码，而不是等待本地回调。在后台运行它，然后将 URL 和代码显示给用户，并让他们在任何设备上打开 URL 并输入代码。确认后，命令结束并存储令牌。

两种形式都跳过了交互式项目选择器，因此当你已经知道要使用哪个项目时，添加 `--project "Organization/Project"`——这可以在一步中登录并固定项目。如果没有 `--project`，具有访问多个项目权限的帐户将进入下面的情况 (d)，因此登录完成后重新运行 `meticulous auth whoami` 并处理它报告的情况，然后继续到步骤 5。

在完全没有人类的环境中，替代方案是 API 令牌：设置 `METICULOUS_API_TOKEN`（或传递 `--apiToken`）而不是登录。

### (d) 通过 OAuth 登录，但没有默认项目

`whoami` 成功，并且额外在 stderr 上记录：

> No default project set. Run `meticulous auth set-project` to choose one.

在此状态下，项目范围的命令无法解析项目。这发生在具有访问多个项目的帐户上——包括在 `--non-interactive` 或 `--device` 登录后，它跳过了选择器。列出选项，然后固定一个：

```bash
meticulous auth list-projects   # 每行一个 "organization/project" slug
meticulous auth set-project --project "Organization/Project"
```

除非只有一个选项（例如只有一个项目被列出，或者存储库明显对应于其中之一），否则请要求用户选择哪一个。或者，要求用户自己运行 `meticulous auth set-project`——如果没有 `--project`，它会显示交互式选择器。

选择保存在帐户中而不是机器上，因此它也适用于 MCP 服务器以及用户的其他机器。`meticulous auth get-project` 单独打印当前解析的项目。

## 步骤 5 — 更新已安装的 Meticulous 技能

技能本身也在积极开发中。如何更新它们取决于它们的安装方式（最佳尝试，见上述说明）：

- **使用 `npx skills` 安装**——默认。技能文件位于 `.claude/skills/`、`.cursor/skills/` 或代理的等效位置，旁边是 `skills-lock.json`：

  ```bash
  # 安装或更新所有技能，针对指定的代理
  npx skills add alwaysmeticulous/skills --skill "*" --agent claude-code --agent codex --agent cursor -y
  ```

  只有在你看到项目中存在 `skills-lock.json`（或技能文件本身）后，才运行此命令，否则它会在插件安装旁边安装第二个副本。

- **作为 Claude Code 插件安装**——技能以命名空间 `/meticulous:<skill-name>` 的形式显示，并且 `claude plugin list` 列出 `meticulous@meticulous`。`npx skills` 不会触及这些；更新插件而不是：

  ```bash
  claude plugin update meticulous@meticulous
  ```

  告诉用户更新仅在重新启动 Claude Code 后才生效（他们也可以从 `/plugin` 菜单自行完成）。一个例外：如果 `claude plugin list` 报告插件的范围是 `managed`，则它由其组织的管理设置固定——不要尝试更新它，只需告知用户。

- **从 Cursor 插件市场安装**——没有要运行的命令；建议用户从 Cursor 的 **Customize → Plugins** 更新它。

如果适用的命令不被白名单，建议用户自行运行它。无论如何——无论它是否运行，或者用户拒绝——继续执行调用技能。
