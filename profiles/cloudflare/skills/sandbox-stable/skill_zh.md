# Sandbox SDK — 稳定版包

在 [Cloudflare Containers](https://developers.cloudflare.com/containers/) 上的隔离 Linux 环境，由 Workers 驱动。

**优先使用主 Sandbox 文档和已安装的稳定类型，而非内存。** 这项技能是一个门禁、一份合同和一张检索地图——而不是一份完整的手册。

这一行是**当前稳定的**默认 npm 包。主 [Sandbox 文档](https://developers.cloudflare.com/sandbox/) 描述了它。现有应用可以保留在此并继续发布。

我们推荐新项目使用 `@cloudflare/sandbox@next` 和 **`sandbox-next`**。当你准备好时，计划使用 **`sandbox-migrate-to-next`** 进行迁移，以便在 1.0 成为稳定版本时做好准备。除非用户要求，否则不要强制进行端口切换。

## 1. 门禁 — 确认包行

在编写代码之前，检查应用：

| 检查项 | 必须匹配 |
| ----- | ---------- |
| npm 依赖 | 默认 `@cloudflare/sandbox` (**不是** `@next` / 预览标签) |
| 容器镜像 | 匹配的**稳定**镜像（不是 `cloudflare/sandbox:next`） |

| 如果你发现… | 操作 |
| ------------ | ------ |
| `@cloudflare/sandbox@next` 或 `next` 镜像 | **停止。** 加载 **`sandbox-next`**。 |
| 用户希望迁移到 1.0 / `@next` | **停止。** 加载 **`sandbox-migrate-to-next`**。不要在稳定包上半途而废地应用预览 API。 |
| 仅清理已弃用的稳定 API | 保留在此；使用 [2026 弃用指南](https://developers.cloudflare.com/sandbox/guides/2026-deprecation/)。这**不是**迁移到 `@next`。 |

永远不要将稳定的 Worker 包与 `@next` 容器镜像（或反之）混合。

技能安装：[Agent 设置](https://developers.cloudflare.com/agent-setup/) · [cloudflare/skills](https://github.com/cloudflare/skills)

## 2. 合同 — 不可协商项

- `await sandbox.exec(command)` 接收一个**命令字符串**，并在命令**完成**时解析，带有缓存的 `stdout` / `stderr` / `exitCode`（及相关字段）。
- 长运行和流式工作使用**稳定**的命令 API (`startProcess`, `execStream` 和相关辅助函数)—而不是 `@next` 的单手模型。打开命令文档；不要在稳定版上发明 `@next` 的 `output()` 处理器。
- **会话**可以在命令之间保留工作目录和环境（默认会话 / `enableDefaultSession`, `createSession`）。当状态必须在调用之间传递时，请查看会话文档。
- 交互式浏览器终端通常使用**`sandbox.terminal(request)`** 和稳定版的会话/xterm 辅助函数—not 预览 `createTerminal` 除非包是 `@next`。
- 使用隧道或大型/二进制流时，优先使用**RPC** 传输。HTTP/WebSocket 传输已弃用（下方清理指南）。
- 文件、挂载、端口、隧道、备份、生命周期和解释器：使用主文档查看签名；信任已安装的**稳定**类型。
- 非机密配置在 Sandbox 环境中；实时凭证在 Worker 中。当进程调用外部 API 时，使用出站处理器。
- 生产预览主机名在使用这些 URL 模式时，需要在自定义域上配置通配符 DNS。
- 在依赖项仍然是稳定的情况下，**不要**应用 `@next` 的 argv/`process.output()` API。
- 自部署的**桥接**保留在稳定包和镜像上。[桥接](https://developers.cloudflare.com/sandbox/bridge/)

最小示例：

```ts
import { getSandbox, proxyToSandbox, Sandbox } from "@cloudflare/sandbox";

export { Sandbox };

const sandbox = getSandbox(env.Sandbox, "user-123");
const result = await sandbox.exec('python3 -c "print(2 + 2)"');
// result.stdout, result.exitCode, result.success
```

## 3. 检索 — 为任务打开文档

在实现之前获取页面。已安装的稳定类型优先于猜测。

| 你需要… | 打开 |
| ------------ | ---- |
| 指南 | [Sandbox 概述](https://developers.cloudflare.com/sandbox/) |
| 首个 Worker、模板、Docker | [入门](https://developers.cloudflare.com/sandbox/get-started/) |
| `exec`、流式、后台进程 | [命令 API](https://developers.cloudflare.com/sandbox/api/commands/) · [执行命令](https://developers.cloudflare.com/sandbox/guides/execute-commands/) · [后台进程](https://developers.cloudflare.com/sandbox/guides/background-processes/) · [流式输出](https://developers.cloudflare.com/sandbox/guides/streaming-output/) |
| 会话 / 命令间的 shell 状态 | [会话概念](https://developers.cloudflare.com/sandbox/concepts/sessions/) · [会话 API](https://developers.cloudflare.com/sandbox/api/sessions/) |
| `getSandbox` 选项、睡眠、销毁 | [生命周期 API](https://developers.cloudflare.com/sandbox/api/lifecycle/) · [Sandbox 选项](https://developers.cloudflare.com/sandbox/configuration/sandbox-options/) |
| 环境变量 | [环境变量](https://developers.cloudflare.com/sandbox/configuration/environment-variables/) |
| 文件 | [文件 API](https://developers.cloudflare.com/sandbox/api/files/) · [管理文件](https://developers.cloudflare.com/sandbox/guides/manage-files/) · [文件监视](https://developers.cloudflare.com/sandbox/api/file-watching/) |
| 桶 / 挂载 | [存储 API](https://developers.cloudflare.com/sandbox/api/storage/) · [挂载桶](https://developers.cloudflare.com/sandbox/guides/mount-buckets/) |
| 备份 | [备份 API](https://developers.cloudflare.com/sandbox/api/backups/) · [备份和恢复](https://developers.cloudflare.com/sandbox/guides/backup-restore/) |
| 端口、预览 URL、暴露 | [端口 API](https://developers.cloudflare.com/sandbox/api/ports/) · [暴露服务](https://developers.cloudflare.com/sandbox/guides/expose-services/) |
| 隧道 | [隧道 API](https://developers.cloudflare.com/sandbox/api/tunnels/) |
| 代理 / Worker 连接 | [代理请求](https://developers.cloudflare.com/sandbox/guides/proxy-requests/) · [Worker 连接](https://developers.cloudflare.com/sandbox/guides/workers-connections/) |
| 浏览器 / PTY 终端 | [终端 API](https://developers.cloudflare.com/sandbox/api/terminal/) · [终端概念](https://developers.cloudflare.com/sandbox/concepts/terminal/) · [浏览器终端](https://developers.cloudflare.com/sandbox/guides/browser-terminals/) |
| 代码解释器 | [解释器 API](https://developers.cloudflare.com/sandbox/api/interpreter/) · [代码执行](https://developers.cloudflare.com/sandbox/guides/code-execution/) |
| Sandbox 中的 Git | [Git 工作流](https://developers.cloudflare.com/sandbox/guides/git-workflows/) |
| 密码 / 出站 | [出站流量](https://developers.cloudflare.com/sandbox/guides/outbound-traffic/) |
| WebSocket | [WebSocket 连接](https://developers.cloudflare.com/sandbox/guides/websocket-connections/) |
| Docker-in-Docker | [Docker in Docker](https://developers.cloudflare.com/sandbox/guides/docker-in-docker/) |
| 生产部署 | [生产部署](https://developers.cloudflare.com/sandbox/guides/production-deployment/) |
| 容器概念 | [容器](https://developers.cloudflare.com/sandbox/concepts/containers/) |
| 如何索引 | [指南](https://developers.cloudflare.com/sandbox/guides/) |
| API 索引 | [API 参考](https://developers.cloudflare.com/sandbox/api/) |
| 在稳定版上弃用的 API | [2026 弃用指南](https://developers.cloudflare.com/sandbox/guides/2026-deprecation/) |
| 自部署桥接 | [桥接](https://developers.cloudflare.com/sandbox/bridge/) · [桥接 HTTP API](https://developers.cloudflare.com/sandbox/bridge/http-api/) |
| 示例（稳定版/`main`） | [GitHub 上的示例](https://github.com/cloudflare/sandbox-sdk/tree/main/examples) |
| 1.0 预览上的新工作 | **`sandbox-next`** · [1.0 预览](https://developers.cloudflare.com/sandbox/1-0-preview/) |
| 将现有应用迁移到 `@next` | **`sandbox-migrate-to-next`** · [迁移](https://developers.cloudflare.com/sandbox/1-0-preview/migrate/) |

### 弃用 API 清理（保留在稳定版上）

首先更新包和匹配的镜像，然后遵循指南。典型搜索：

```sh
rg 'SANDBOX_TRANSPORT|transport:|exposePort\(|enableDefaultSession|execStream\(|readFileStream|writeFileStream'
```

这条路径**不会**让你切换到 `@next`。

## 4. 在发布前

- Worker 包和容器镜像在**同一稳定**行  
- 对已安装的稳定类型进行类型检查  
- Sandbox 环境中无实时密码  
- 如果使用已弃用的传输/辅助函数，完成或跟踪 [2026 弃用](https://developers.cloudflare.com/sandbox/guides/2026-deprecation/) 清理  
- 当团队准备好 1.0 时，使用 **`sandbox-migrate-to-next`**—不要未经提示就强制切换
