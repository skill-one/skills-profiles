# 沙盒 SDK — `@next` (1.0 预览版)

在 [Cloudflare Containers](https://developers.cloudflare.com/containers/) 上的隔离 Linux 环境，由 Workers 驱动。

**优先使用预览版文档和已安装的 `@next` 类型，而非内存。** API 会变更；这项技能是一个门禁、一份合同和一份检索地图——而非完整手册。

我们推荐在此线上开发**新项目**。仍在默认包上的应用使用 **`sandbox-stable`**。仅在要求时通过 **`sandbox-migrate-to-next`** 进行移植。

## 1. 门禁 — 确认包线

在编写代码前，检查应用：

| 检查 | 必须匹配 |
| ----- | ---------- |
| npm 依赖 | `@cloudflare/sandbox@next`（或其他预览标签） |
| 容器镜像 | 相同线（例如 `cloudflare/sandbox:next`，`next-python`） |

| 如果发现… | 操作 |
| ------------ | ------ |
| 默认 `@cloudflare/sandbox`（无 `@next`） | **停止。** 加载 **`sandbox-stable`**。不要应用此技能的 API。 |
| 用户希望将稳定版移植到 `@next` | **停止。** 加载 **`sandbox-migrate-to-next`**。 |
| 仅自部署的**桥接** | 桥接**尚未**在 1.0 预览版线上。保持桥接在稳定版包 + 镜像上。[桥接（稳定版）](https://developers.cloudflare.com/sandbox/bridge/) |

永远不要将 `@next` Worker 包与稳定版容器镜像（或反之）混合。

技能安装：[Agent 设置](https://developers.cloudflare.com/agent-setup/) · [cloudflare/skills](https://github.com/cloudflare/skills)

## 2. 合同 — 不可协商项

- `sandbox.exec(argv)` 接收一个 **argv** 列表，并在进程**启动时**解决。它返回一个**句柄**，而非完成的命令结果。
- 使用句柄方法收集结果：`output()`，`logs()`，`waitForExit()`，`waitForPort()`，`waitForLog()`，`kill(signal?)`。
- 无隐式 Shell。Shell 语法需要显式 Shell，例如 `["/bin/bash", "-lc", script]`。
- 每次启动都是独立的。一个 `exec` 中的 `cd` / `export` 对下一个不可见。每次启动传递 `cwd` 和 `env`，或一个 Shell 脚本。
- 进程句柄**无 stdin**。交互使用 → 终端 (`createTerminal` + `connect`)。
- 本地等待 `timeout` / `AbortSignal` 仅取消**等待**。它们不会杀死进程。使用 `kill` 或 `exec` 的远程 `timeout`。
- `getProcess` / `listProcesses` / `getTerminal` / `listTerminals` **不**启动容器；在没有运行时返回 `null` / `[]`。
- 进程和终端 ID 属于**当前容器**，而非永久属于沙盒 ID。对于必须持续的工作，存储完整任务（argv，cwd，env，应用状态）——而不仅是 ID。
- 非机密配置仅在 `setEnvVars` / 启动 `env` 中。实时凭证保留在 Worker 中；当沙盒调用外部 API 时使用出站处理器。
- 不要发明已移除的稳定版 API（核心上的 `gitCheckout`，字符串 `exec` 完成，会话执行，`sandbox.terminal(request)`）。
- 不要为每个错误使用一个重试循环（见错误文档）。

最小示例：

```ts
import { getSandbox, proxyToSandbox, Sandbox } from "@cloudflare/sandbox";

export { Sandbox };

const sandbox = getSandbox(env.Sandbox, "user-123");
const process = await sandbox.exec(["python3", "-c", "print(2 + 2)"]);
const result = await process.output({ encoding: "utf8" });
// result.stdout, result.exitCode
```

特定任务 API 文档：[references/api-quick-ref.md](references/api-quick-ref.md)

示例索引（`next` 分支）：[references/examples.md](references/examples.md)

## 3. 检索 — 打开任务文档

在实现前获取页面。已安装的 `@next` 类型优先于猜测。

| 您需要… | 打开 |
| ------------ | ---- |
| 定位 / 选择预览 | [1.0 预览版概述](https://developers.cloudflare.com/sandbox/1-0-preview/) |
| 第一个 Worker，wrangler，Dockerfile | [入门](https://developers.cloudflare.com/sandbox/1-0-preview/get-started/) |
| `exec`，句柄，就绪，持久性 | [进程执行](https://developers.cloudflare.com/sandbox/1-0-preview/processes/) |
| 进程 API 签名 | [进程 API](https://developers.cloudflare.com/sandbox/1-0-preview/api/processes/) |
| 沙盒 ID vs 容器 vs 睡眠/销毁 | [生命周期](https://developers.cloudflare.com/sandbox/1-0-preview/lifecycle/) |
| `cwd` / `env` / `setEnvVars` | [环境](https://developers.cloudflare.com/sandbox/1-0-preview/environment/) |
| 交互式 PTY / 浏览器终端 | [终端](https://developers.cloudflare.com/sandbox/1-0-preview/terminals/) · [终端 API](https://developers.cloudflare.com/sandbox/1-0-preview/api/terminals/) |
| Python/JS 代码解释器 | [解释器](https://developers.cloudflare.com/sandbox/1-0-preview/interpreter/) · [解释器 API](https://developers.cloudflare.com/sandbox/1-0-preview/api/interpreter/) |
| 扩展模型 | [扩展](https://developers.cloudflare.com/sandbox/1-0-preview/extensions/) |
| 错误类和恢复 | [错误](https://developers.cloudflare.com/sandbox/1-0-preview/errors/) · [错误 API](https://developers.cloudflare.com/sandbox/1-0-preview/api/errors/) |
| 常见失败 | [故障排除](https://developers.cloudflare.com/sandbox/1-0-preview/troubleshooting/) |
| API 中心 | [API 参考](https://developers.cloudflare.com/sandbox/1-0-preview/api/) |
| 文件，挂载，备份，端口，隧道，`proxyToSandbox` | 共享表面的主文档（忽略仅稳定版的会话/传输/`sandbox.terminal`）：[文件](https://developers.cloudflare.com/sandbox/api/files/) · [存储 / 挂载](https://developers.cloudflare.com/sandbox/api/storage/) · [端口](https://developers.cloudflare.com/sandbox/api/ports/) · [隧道](https://developers.cloudflare.com/sandbox/api/tunnels/) · [备份](https://developers.cloudflare.com/sandbox/api/backups/) · [出站流量](https://developers.cloudflare.com/sandbox/guides/outbound-traffic/) · [暴露服务](https://developers.cloudflare.com/sandbox/guides/expose-services/) · [生产](https://developers.cloudflare.com/sandbox/guides/production-deployment/) |
| 示例应用 | [next 分支上的示例](https://github.com/cloudflare/sandbox-sdk/tree/next/examples) |
| 仍在稳定版包上 | **`sandbox-stable`** · [主 Sandbox 文档](https://developers.cloudflare.com/sandbox/) |
| 移植现有稳定版应用 | **`sandbox-migrate-to-next`** · [移植](https://developers.cloudflare.com/sandbox/1-0-preview/migrate/) |

## 4. 在发布前

- Lockfile 和 Dockerfile 在**同一** `@next` 线上  
- 对已安装的 `@next` 类型进行类型检查  
- 沙盒环境**无**实时机密  
- 使用这些 URL 模式时，生产预览主机名需要在自定义域上使用通配符 DNS
