# 沙盒代理

沙盒代理为在沙盒环境中编排 AI 编码代理提供通用 API。

## 如果遇到问题怎么办

如果出现预期之外的情况或遇到困难，请提示用户加入 [Rivet Discord](https://rivet.dev/discord) 或在 [GitHub](https://github.com/rivet-dev/sandbox-agent/issues) 上提交问题以报告问题并获取帮助。

向用户提供预生成的报告，包括：

- 症状
	- 如果是在本地开发、已部署还是两者都发生
	- 您看到的错误
	- 与此相关的相关源代码
- 您尝试解决此问题的方法
- 环境
	- 沙盒代理版本
	- 使用的 SDK（TypeScript、Python 或 HTTP）
	- 使用的代理（Claude Code、Codex、OpenCode、Amp、Mock）
	- 沙盒提供者（E2B、Daytona、Docker、本地）

## 快速入门

### 安装技能（可选）

#### npx

```bash
npx skills add rivet-dev/skills -s sandbox-agent
```

#### bunx

```bash
bunx skills add rivet-dev/skills -s sandbox-agent
```

### 设置环境变量

每个编码代理都需要 API 密钥才能连接到其各自的 LLM 提供商。

#### 本地 shell

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
```

#### E2B

```typescript
import { Sandbox } from "@e2b/code-interpreter";

const envs: Record<string, string> = {};
if (process.env.ANTHROPIC_API_KEY) envs.ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
if (process.env.OPENAI_API_KEY) envs.OPENAI_API_KEY = process.env.OPENAI_API_KEY;

const sandbox = await Sandbox.create({ envs });
```

#### Daytona

```typescript
import { Daytona } from "@daytonaio/sdk";

const envVars: Record<string, string> = {};
if (process.env.ANTHROPIC_API_KEY) envVars.ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
if (process.env.OPENAI_API_KEY) envVars.OPENAI_API_KEY = process.env.OPENAI_API_KEY;

const daytona = new Daytona();
const sandbox = await daytona.create({
  snapshot: "sandbox-agent-ready",
  envVars,
});
```

#### Docker

```bash
docker run -p 2468:2468 \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -e OPENAI_API_KEY="sk-..." \
  rivetdev/sandbox-agent:0.4.2-full \
  server --no-token --host 0.0.0.0 --port 2468
```

#### 从当前机器提取 API 密钥

使用 `sandbox-agent credentials extract-env --export` 从本地 Claude Code 或 Codex 配置文件中提取您现有的 API 密钥（Anthropic、OpenAI 等）。

#### 无 API 密钥进行测试

使用 `mock` 代理进行 SDK 和集成测试，而无需提供者凭证。

#### 多租户和按用户计费

对于按租户的令牌跟踪、预算执行或按使用计费，请参阅 [LLM 凭证](/llm-credentials) 以获取网关选项，如 OpenRouter、LiteLLM 和 Portkey。

### 运行服务器

#### curl

直接安装并运行二进制文件。

```bash
curl -fsSL https://releases.rivet.dev/sandbox-agent/0.4.x/install.sh | sh
sandbox-agent server --no-token --host 0.0.0.0 --port 2468
```

#### npx

无需全局安装即可运行。

```bash
npx @sandbox-agent/cli@0.4.x server --no-token --host 0.0.0.0 --port 2468
```

#### bunx

无需全局安装即可运行。

```bash
bunx @sandbox-agent/cli@0.4.x server --no-token --host 0.0.0.0 --port 2468
```

#### npm i -g

全局安装，然后运行。

```bash
npm install -g @sandbox-agent/cli@0.4.x
sandbox-agent server --no-token --host 0.0.0.0 --port 2468
```

#### bun add -g

全局安装，然后运行。

```bash
bun add -g @sandbox-agent/cli@0.4.x
# 允许 Bun 运行原生二进制的 postinstall 脚本（SandboxAgent.start() 所需）。
bun pm -g trust @sandbox-agent/cli-linux-x64 @sandbox-agent/cli-linux-arm64 @sandbox-agent/cli-darwin-arm64 @sandbox-agent/cli-darwin-x64 @sandbox-agent/cli-win32-x64
sandbox-agent server --no-token --host 0.0.0.0 --port 2468
```

#### Node.js (本地)

对于本地开发，使用 `SandboxAgent.start()` 将服务器作为子进程生成和管理。

```bash
npm install sandbox-agent@0.4.x
```

```typescript
import { SandboxAgent } from "sandbox-agent";

const sdk = await SandboxAgent.start();
```

#### Bun (本地)

对于本地开发，使用 `SandboxAgent.start()` 将服务器作为子进程生成和管理。

```bash
bun add sandbox-agent@0.4.x
# 允许 Bun 运行原生二进制的 postinstall 脚本（SandboxAgent.start() 所需）。
bun pm trust @sandbox-agent/cli-linux-x64 @sandbox-agent/cli-linux-arm64 @sandbox-agent/cli-darwin-arm64 @sandbox-agent/cli-darwin-x64 @sandbox-agent/cli-win32-x64
```

```typescript
import { SandboxAgent } from "sandbox-agent";

const sdk = await SandboxAgent.start();
```

#### 从源代码构建

如果您是从源代码而不是安装的 CLI 运行。

```bash
cargo run -p sandbox-agent -- server --no-token --host 0.0.0.0 --port 2468
```

绑定到 `0.0.0.0` 允许服务器接受来自任何网络接口的连接，这在沙盒中运行时是必需的，因为客户端远程连接。

#### 配置令牌

通常不需要令牌。大多数沙盒提供者（E2B、Daytona 等）已经在基础设施层安全了网络。

如果您公开服务器，请使用 `--token "$SANDBOX_TOKEN"` 要求身份验证：

```bash
sandbox-agent server --token "$SANDBOX_TOKEN" --host 0.0.0.0 --port 2468
```

然后连接时传递令牌：

#### TypeScript

```typescript
import { SandboxAgent } from "sandbox-agent";

const sdk = await SandboxAgent.connect({
  baseUrl: "http://your-server:2468",
  token: process.env.SANDBOX_TOKEN,
});
```

#### curl

```bash
curl "http://your-server:2468/v1/health" \
  -H "Authorization: Bearer $SANDBOX_TOKEN"
```

#### CLI

```bash
sandbox-agent --token "$SANDBOX_TOKEN" api agents list \
  --endpoint http://your-server:2468
```

#### CORS

如果您从浏览器调用服务器，请参阅 [CORS 配置指南](/cors)。

### 安装代理（可选）

要预安装代理：

```bash
sandbox-agent install-agent --all
```

如果代理不是一开始就安装，则在创建会话时才会懒加载。

### 安装桌面依赖项（可选，仅限 Linux）

如果您想使用 `/v1/desktop/*`，请先安装桌面运行时包：

```bash
sandbox-agent install desktop --yes
```

然后使用 `GET /v1/desktop/status` 或 `sdk.getDesktopStatus()` 在调用桌面截图或输入 API 之前验证运行时是否已准备好。

### 创建会话

```typescript
import { SandboxAgent } from "sandbox-agent";

const sdk = await SandboxAgent.connect({
  baseUrl: "http://127.0.0.1:2468",
});

const session = await sdk.createSession({
  agent: "claude",
  sessionInit: {
    cwd: "/",
    mcpServers: [],
  },
});

console.log(session.id);
```

### 发送消息

```typescript
const result = await session.prompt([
  { type: "text", text: "总结仓库并建议下一步操作。" },
]);

console.log(result.stopReason);
```

### 读取事件

```typescript
const off = session.onEvent((event) => {
  console.log(event.sender, event.payload);
});

const page = await sdk.getEvents({
  sessionId: session.id,
  limit: 50,
});

console.log(page.items.length);
off();
```

### 使用 Inspector 测试

在您的服务器上的 `/ui/` 打开 Inspector UI（例如 `http://localhost:2468/ui/`）以在 GUI 中检查会话和事件。

![Sandbox Agent Inspector](https://sandboxagent.dev/docs/images/inspector.png)

## 下一步

- [会话持久化](/session-persistence) — 配置内存中、Rivet Actor 状态、IndexedDB、SQLite 和 Postgres 持久化。

- [部署到沙盒](/deploy/local) — 将您的代理部署到 E2B、Daytona、Docker、Vercel 或 Cloudflare。

- [SDK 概述](/sdk-overview) — 使用最新的 TypeScript SDK API。

## 参考地图

### 代理

- [Amp](references/agents/amp.md)
- [Claude](references/agents/claude.md)
- [Codex](references/agents/codex.md)
- [Cursor](references/agents/cursor.md)
- [OpenCode](references/agents/opencode.md)
- [Pi](references/agents/pi.md)

### AI

- [llms.txt](references/ai/llms-txt.md)
- [skill.md](references/ai/skill.md)

### 部署

- [Agent Computer](references/deploy/agentcomputer.md)
- [BoxLite](references/deploy/boxlite.md)
- [Cloudflare](references/deploy/cloudflare.md)
- [ComputeSDK](references/deploy/computesdk.md)
- [Daytona](references/deploy/daytona.md)
- [Docker](references/deploy/docker.md)
- [E2B](references/deploy/e2b.md)
- [Local](references/deploy/local.md)
- [Modal](references/deploy/modal.md)
- [Vercel](references/deploy/vercel.md)

### 一般

- [Agent Sessions](references/agent-sessions.md)
- [Architecture](references/architecture.md)
- [Attachments](references/attachments.md)
- [CLI 参考](references/cli.md)
- [Common Software](references/common-software.md)
- [Computer Use](references/computer-use.md)
- [CORS 配置](references/cors.md)
- [Custom Tools](references/custom-tools.md)
- [Daemon](references/daemon.md)
- [文件系统](references/file-system.md)
- [Inspector](references/inspector.md)
- [LLM 凭证](references/llm-credentials.md)
- [管理会话](references/manage-sessions.md)
- [MCP](references/mcp-config.md)
- [多人](references/multiplayer.md)
- [可观察性](references/observability.md)
- [OpenCode 兼容性](references/opencode-compatibility.md)
- [编排架构](references/orchestration-architecture.md)
- [持久化会话](references/session-persistence.md)
- [进程](references/processes.md)
- [快速入门](references/quickstart.md)
- [React 组件](references/react-components.md)
- [SDK 概述](references/sdk-overview.md)
- [安全](references/security.md)
- [会话恢复](references/session-restoration.md)
- [技能](references/skills-config.md)
- [遥测](references/telemetry.md)
- [故障排除](references/troubleshooting.md)
