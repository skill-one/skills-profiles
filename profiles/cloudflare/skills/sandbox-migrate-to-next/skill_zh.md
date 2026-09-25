# 从稳定版迁移至 Sandbox SDK 1.0 预览版（`@next`）

**执行**迁移。请按顺序执行步骤。深度信息存在于文档中——当某个步骤需要详细信息时，请查阅相关链接的页面。

人类指南：[迁移](https://developers.cloudflare.com/sandbox/1-0-preview/migrate/) · [1.0 预览版](https://developers.cloudflare.com/sandbox/1-0-preview/)

**新项目**应从 `@next`（**`sandbox-next`**）开始，而不是这个版本。**日常稳定版工作** → **`sandbox-stable`**。清理已弃用的 API **而不迁移至 `@next`** → 如有需要，请先查阅[2026 年弃用指南](https://developers.cloudflare.com/sandbox/guides/2026-deprecation/)。

现有应用应在**您方便时**进行迁移，以便在 1.0 成为稳定版时做好准备。**不要**在用户未同意的情况下强制切换生产环境。

**优先使用已安装的 `@next` 类型以及迁移文档，而不是内存。**

## 工作流程

1. **审查**硬性规则和替换映射
2. **审计**代码库；列出匹配项和目标形状
3. **与用户沟通**（切换、桥接、Python 镜像、不明确的站点）
4. **升级**包、镜像和代码
5. **验证**

任何需要用户决策的步骤后停止。

## 硬性规则

- Worker 包和容器镜像必须是**相同**的 `@next` 分支。
- 生产环境切换使用**立即**的容器部署。稳定版和 `@next` 的控制协议双向不兼容；渐进式部署会导致混合窗口损坏。正在进行的容器工作可以停止。
- 切换后，`await sandbox.exec(...)` 表示进程**已启动**，而不是命令**已结束**。
- Argv 保持原样（无隐式 Shell）。需要 Shell 语法时，需要一个明确的 Shell 二进制文件。
- 进程句柄**没有**标准输入 → 使用终端进行交互式输入。
- 观察 `timeout` / `AbortSignal` 仅取消**等待**，不取消进程。
- 每个错误**不**使用单个重试循环。
- **不要**发明 API（`gitCheckout` 在核心上、处理标准输入、字符串执行完成辅助工具）。
- 自部署的桥接程序保持在**稳定版**（尚未成为预览分支的一部分）。

## 替换映射

| 稳定版 | `@next` |
| ------ | ------- |
| `SANDBOX_TRANSPORT` / `transport` / `setTransport` | 移除 — 仅支持 RPC |
| `await sandbox.exec("cmd")` → 缓冲结果 | `await sandbox.exec(argv)` → 句柄，然后 `output` / 等待 |
| `execStream` / `startProcess` | 相同句柄：`logs`，`waitFor*`，`kill` |
| 默认 / 命名会话 | 已移除 — 每次启动的 `cwd`/`env`，或一个 Shell 脚本 |
| `sandbox.terminal(request)` / 会话终端 | `createTerminal` + `terminal.connect(request)` |
| xterm `sessionId` | `terminalId` |
| `Sandbox` 上的解释器方法 | `withInterpreter` → `sandbox.interpreter.*` |
| `gitCheckout` | 通过 `exec` 的 `argv` `git` |
| 字符串终止信号 | 仅支持数字 |
| 文件、挂载、备份、端口、隧道、`proxyToSandbox` | 基本不变（忽略稳定版页面上的会话/传输部分） |

深度：[迁移](https://developers.cloudflare.com/sandbox/1-0-preview/migrate/) · 迁移后，日常工作 → **`sandbox-next`**

## 审计

```sh
rg 'SANDBOX_TRANSPORT|transport:|setTransport|enableDefaultSession|createSession|getSession|deleteSession|execStream\(|startProcess\(|killProcess\(|sandbox\.terminal\(|sessionId|gitCheckout\(|SandboxTransport|ExecutionSession'
```

此外：字符串 `exec(`，`cd` 然后稍后的 `exec`，`Sandbox` 上的裸 `createCodeContext` / `runCode`。

## 沟通（需要时）

- 可以使用 `--containers-rollout=immediate` 切换生产环境（可能停止正在运行的进程/终端/流）？
- 自部署桥接程序？保持在稳定版。
- Python 解释器 → **`-python`** 镜像变体？
- 未映射的调用点？

## 升级

### 包和镜像

```sh
npm install @cloudflare/sandbox@next
```

```dockerfile
FROM cloudflare/sandbox:next
# Python: cloudflare/sandbox:next-python
```

当不在浮动 `next` 时，Worker 和镜像使用相同的预发布标签。

### 按区域升级代码

应用替换映射中的内容。对于每个区域，根据文档实施，而不是依赖稳定版习惯：

| 区域 | 文档 |
| ---- | --- |
| 命令 / 句柄 / 等待 | [进程](https://developers.cloudflare.com/sandbox/1-0-preview/processes/) · [进程 API](https://developers.cloudflare.com/sandbox/1-0-preview/api/processes/) |
| `cwd` / `env` / 密钥 | [环境](https://developers.cloudflare.com/sandbox/1-0-preview/environment/) · [出站流量](https://developers.cloudflare.com/sandbox/guides/outbound-traffic/) |
| 删除会话 | [迁移](https://developers.cloudflare.com/sandbox/1-0-preview/migrate/) · [生命周期](https://developers.cloudflare.com/sandbox/1-0-preview/lifecycle/) |
| 终端 | [终端](https://developers.cloudflare.com/sandbox/1-0-preview/terminals/) |
| 解释器 | [解释器](https://developers.cloudflare.com/sandbox/1-0-preview/interpreter/) |
| 错误 | [错误](https://developers.cloudflare.com/sandbox/1-0-preview/errors/) |
| 跨请求的持久任务 | [进程执行 — 生命周期 / 持久性](https://developers.cloudflare.com/sandbox/1-0-preview/processes/) |

**命令（形状）：**

```ts
// 之前（稳定版）
const result = await sandbox.exec("npm test");

// 之后（@next）
const process = await sandbox.exec(["/bin/bash", "-lc", "npm test"]);
const result = await process.output({ encoding: "utf8" });
```

```ts
const server = await sandbox.exec(["/bin/bash", "-lc", "npm run dev"], {
  cwd: "/workspace/app",
});
await server.waitForPort(3000, { timeout: 60_000 });
await server.kill(); // 数字；默认 15
```

**终端（形状）：**

```ts
const terminal = await sandbox.createTerminal({ command: ["bash"], cwd: "/workspace" });
const t = await sandbox.getTerminal(terminal.id);
if (!t) return new Response("terminal gone", { status: 410 });
return t.connect(request, { cursor, cols, rows });
```

**解释器（形状）：**

```ts
import { Sandbox as BaseSandbox } from "@cloudflare/sandbox";
import { withInterpreter } from "@cloudflare/sandbox/interpreter";

export class Sandbox extends BaseSandbox<Env> {
  interpreter = withInterpreter(this);
}
```

**Git（形状）：**

```ts
const clone = await sandbox.exec(
  ["git", "clone", "--depth", "1", "--", repoUrl, "/workspace/repo"],
  { cwd: "/workspace" },
);
const result = await clone.output({ encoding: "utf8" });
```

完全删除传输设置。移除会话 API。使用**独立的 sandbox ID**隔离用户。

### 部署切换

先在 Staging/分支部署。生产环境是**一次**匹配的 Worker + 镜像的部署：

```sh
npx wrangler deploy --containers-rollout=immediate
```

保持 `rollout_active_grace_period` 默认 `0`（如果已提高，则设置为 `0`）。切换后，预部署的进程/终端 ID 无效。详情：[迁移](https://developers.cloudflare.com/sandbox/1-0-preview/migrate/) · [容器部署](https://developers.cloudflare.com/containers/platform-details/rollouts/)

## 验证

1. Lockfile + Dockerfile 在同一 `@next` 分支
2. 对 `@next` 进行类型检查
3. 烟雾测试 `exec` + `output({ encoding: "utf8" })`
4. 烟雾测试长进程 / 终端 / 解释器（如果使用）
5. 错误区分：不可用 / 中断 RPC / 过期 / 本地等待
6. 沙盒环境中**没有**活态密钥
7. 再次使用 Grep 查找已移除的 API
8. 生产环境使用 `--containers-rollout=immediate`

然后日常工作使用 **`sandbox-next`**。

## 严重警告 — 停止并修复

- 混合 `@next` Worker 和稳定版镜像（反之亦然）
- 对此切换使用渐进式容器部署
- 将 `await exec` 视为命令完成
- 假设 `cd` / 导出跨 `exec` 调用持久
- 每个错误使用一个重试包装器
- 发明 `gitCheckout`、处理标准输入或未记录的 API
- 部署后保留切换前的进程/终端 ID
- 未获用户同意强制切换生产环境
- 在 `setEnvVars` / 启动 `env` 中放置活态密钥
