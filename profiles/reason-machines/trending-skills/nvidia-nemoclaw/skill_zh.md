# NVIDIA NemoClaw

> 技能来自 [ara.so](https://ara.so) — 每日 2026 技能集合。

NVIDIA NemoClaw 是一个开源的 TypeScript CLI 插件，可安全地简化运行 [OpenClaw](https://openclaw.ai) 的常驻 AI 助手。它安装并协调 [NVIDIA OpenShell](https://github.com/NVIDIA/OpenShell) 运行时，创建受策略强制的沙盒，并将所有推理通过 NVIDIA 云（Nemotron 模型）进行路由。网络出口、文件系统访问、系统调用和模型 API 调用均受声明式策略管理。

**状态：** Alpha — 接口和 API 可能未经通知而更改。

---

## 安装

### 前置条件

- Linux Ubuntu 22.04 LTS 或更高版本
- Node.js 20+ 和 npm 10+（推荐 Node.js 22）
- 已安装并运行的 Docker
- 已安装 [NVIDIA OpenShell](https://github.com/NVIDIA/OpenShell)

### 一行安装器

```bash
curl -fsSL https://nvidia.com/nemoclaw.sh | bash
```

此命令会安装 Node.js（如果不存在），运行引导式配置向导，创建沙盒，配置推理，并应用安全策略。

### 手动安装（从源代码）

```bash
git clone https://github.com/NVIDIA/NemoClaw.git
cd NemoClaw
npm install
npm run build
npm link  # 使 `nemoclaw` 可全局使用
```

---

## 环境变量

```bash
# 必要：NVIDIA 云 API 密钥用于 Nemotron 推理
export NVIDIA_API_KEY="nvapi-xxxxxxxxxxxx"

# 可选：覆盖默认模型
export NEMOCLAW_MODEL="nvidia/nemotron-3-super-120b-a12b"

# 可选：自定义沙盒数据目录
export NEMOCLAW_SANDBOX_DIR="/var/nemoclaw/sandboxes"
```

在 [build.nvidia.com](https://build.nvidia.com) 获取 API 密钥。

---

## 快速入门

### 1. 引导新代理

```bash
nemoclaw onboard
```

交互式向导会提示输入：
- 沙盒名称（例如 `my-assistant`）
- NVIDIA API 密钥（`$NVIDIA_API_KEY`）
- 推理模型选择
- 网络和文件系统策略配置

成功时的预期输出：

```
──────────────────────────────────────────────────
沙盒      my-assistant (Landlock + seccomp + netns)
模型      nvidia/nemotron-3-super-120b-a12b (NVIDIA 云 API)
──────────────────────────────────────────────────
运行:     nemoclaw my-assistant connect
状态:     nemoclaw my-assistant status
日志:     nemoclaw my-assistant logs --follow
──────────────────────────────────────────────────
[INFO]  === 安装完成 ===
```

### 2. 连接到沙盒

```bash
nemoclaw my-assistant connect
```

### 3. 与代理聊天（在沙盒内）

**TUI（交互式聊天）：**
```bash
sandbox@my-assistant:~$ openclaw tui
```

**CLI（单条消息）：**
```bash
sandbox@my-assistant:~$ openclaw agent --agent main --local -m "hello" --session-id test
```

---

## 主要 CLI 命令

### 主机命令 (`nemoclaw`)

| 命令 | 描述 |
|---|---|
| `nemoclaw onboard` | 交互式设置：网关、提供者、沙盒 |
| `nemoclaw <名称> connect` | 在沙盒内打开交互式 Shell |
| `nemoclaw <名称> status` | 显示 NemoClaw 级别的沙盒健康状态 |
| `nemoclaw <名称> logs --follow` | 流式传输沙盒日志 |
| `nemoclaw start` | 启动辅助服务（Telegram 桥接器、隧道） |
| `nemoclaw stop` | 停止辅助服务 |
| `nemoclaw deploy <实例>` | 通过 Brev 部署到远程 GPU 实例 |
| `openshell term` | 启动 OpenShell TUI 进行监控和批准 |

### 插件命令 (`openclaw nemoclaw`，在沙盒内运行）

> 注意：这些命令正在积极开发中 — 请使用 `nemoclaw` 主机 CLI 作为主要界面。

| 命令 | 描述 |
|---|---|
| `openclaw nemoclaw launch [--profile ...]` | 在 OpenShell 沙盒内引导 OpenClaw |
| `openclaw nemoclaw status` | 显示沙盒健康状态、蓝图状态和推理 |
| `openclaw nemoclaw logs [-f]` | 流式传输蓝图执行和沙盒日志 |

### OpenShell 检查

```bash
# 列出 OpenShell 层的所有沙盒
openshell sandbox list

# 检查特定沙盒
openshell sandbox inspect my-assistant
```

---

## 架构

NemoClaw 协调四个组件：

| 组件 | 角色 |
|---|---|
| **插件** | TypeScript CLI：启动、连接、状态、日志 |
| **蓝图** | 版本化 Python 资产：沙盒创建、策略、推理设置 |
| **沙盒** | 隔离的 OpenShell 容器，运行 OpenClaw 并具有受策略强制的出口/文件系统 |
| **推理** | 通过 OpenShell 网关路由的 NVIDIA 云模型调用 |

**蓝图生命周期：**
1. 解析资产
2. 验证摘要
3. 规划资源
4. 通过 OpenShell CLI 应用

---

## TypeScript 插件使用

NemoClaw 提供了一个程序化的 TypeScript API，用于构建自定义集成。

### 导入和初始化

```typescript
import { NemoClawClient } from '@nvidia/nemoclaw';

const client = new NemoClawClient({
  apiKey: process.env.NVIDIA_API_KEY!,
  model: process.env.NEMOCLAW_MODEL ?? 'nvidia/nemotron-3-super-120b-a12b',
});
```

### 程序化创建沙盒

```typescript
import { NemoClawClient, SandboxConfig } from '@nvidia/nemoclaw';

async function createSandbox() {
  const client = new NemoClawClient({
    apiKey: process.env.NVIDIA_API_KEY!,
  });

  const config: SandboxConfig = {
    name: 'my-assistant',
    model: 'nvidia/nemotron-3-super-120b-a12b',
    policy: {
      network: {
        allowedEgressHosts: ['build.nvidia.com'],
        blockUnlisted: true,
      },
      filesystem: {
        allowedPaths: ['/sandbox', '/tmp'],
        readOnly: false,
      },
    },
  };

  const sandbox = await client.sandbox.create(config);
  console.log(`沙盒创建：${sandbox.id}`);
  return sandbox;
}
```

### 连接并发送消息

```typescript
import { NemoClawClient } from '@nvidia/nemoclaw';

async function chatWithAgent(sandboxName: string, message: string) {
  const client = new NemoClawClient({
    apiKey: process.env.NVIDIA_API_KEY!,
  });

  const sandbox = await client.sandbox.get(sandboxName);
  const session = await sandbox.connect();

  const response = await session.agent.send({
    agentId: 'main',
    message,
    sessionId: `session-${Date.now()}`,
  });

  console.log('代理响应：', response.content);
  await session.disconnect();
}

chatWithAgent('my-assistant', '总结最新的 NVIDIA 收益报告。');
```

### 检查沙盒状态

```typescript
import { NemoClawClient } from '@nvidia/nemoclaw';

async function checkStatus(sandboxName: string) {
  const client = new NemoClawClient({
    apiKey: process.env.NVIDIA_API_KEY!,
  });

  const status = await client.sandbox.status(sandboxName);

  console.log({
    sandbox: status.name,
    healthy: status.healthy,
    blueprint: status.blueprintState,
    inference: status.inferenceProvider,
    policyVersion: status.policyVersion,
  });
}
```

### 流式传输日志

```typescript
import { NemoClawClient } from '@nvidia/nemoclaw';

async function streamLogs(sandboxName: string) {
  const client = new NemoClawClient({
    apiKey: process.env.NVIDIA_API_KEY!,
  });

  const logStream = client.sandbox.logs(sandboxName, { follow: true });

  for await (const entry of logStream) {
    console.log(`[${entry.timestamp}] ${entry.level}: ${entry.message}`);
  }
}
```

### 应用网络策略更新（热重载）

```typescript
import { NemoClawClient, NetworkPolicy } from '@nvidia/nemoclaw';

async function updateNetworkPolicy(sandboxName: string) {
  const client = new NemoClawClient({
    apiKey: process.env.NVIDIA_API_KEY!,
  });

  // 网络策略在运行时可热重载
  const updatedPolicy: NetworkPolicy = {
    allowedEgressHosts: [
      'build.nvidia.com',
      'api.github.com',
    ],
    blockUnlisted: true,
  };

  await client.sandbox.updatePolicy(sandboxName, {
    network: updatedPolicy,
  });

  console.log('网络策略更新（已应用热重载）。');
}
```

---

## 安全/保护层

| 层级 | 保护内容 | 可热重载？ |
|---|---|---|
| **网络** | 阻止未授权的出站连接 | ✅ 是 |
| **文件系统** | 防止在 `/sandbox` 和 `/tmp` 外进行读写 | ❌ 创建时锁定 |
| **进程** | 阻止权限提升和危险系统调用 | ❌ 创建时锁定 |
| **推理** | 将模型 API 调用重定向到受控后端 | ✅ 是 |

当代理尝试连接未列出的主机时，OpenShell 会阻止请求，并在 TUI 中显示供操作员批准。

---

## 常见模式

### 模式：开发用最小沙盒

```typescript
const config: SandboxConfig = {
  name: 'dev-sandbox',
  model: 'nvidia/nemotron-3-super-120b-a12b',
  policy: {
    network: { blockUnlisted: false },   // 开发时允许
    filesystem: { allowedPaths: ['/sandbox', '/tmp', '/home/dev'] },
  },
};
```

### 模式：生产严格沙盒

```typescript
const config: SandboxConfig = {
  name: 'prod-assistant',
  model: 'nvidia/nemotron-3-super-120b-a12b',
  policy: {
    network: {
      allowedEgressHosts: ['build.nvidia.com'],
      blockUnlisted: true,
    },
    filesystem: {
      allowedPaths: ['/sandbox', '/tmp'],
      readOnly: false,
    },
  },
};
```

### 模式：部署到远程 GPU（Brev）

```bash
nemoclaw deploy my-gpu-instance --sandbox my-assistant
```

```typescript
await client.deploy({
  instance: 'my-gpu-instance',
  sandboxName: 'my-assistant',
  provider: 'brev',
});
```

---

## 故障排除

### 错误：沙盒未找到

```
Error: Sandbox 'my-assistant' not found
```

**解决方法：** 在 OpenShell 层级检查 — NemoClaw 错误和 OpenShell 错误是分开的：

```bash
openshell sandbox list
nemoclaw my-assistant status
```

### 错误：NVIDIA API 密钥缺失或无效

```
Error: Inference provider authentication failed
```

**解决方法：**
```bash
export NVIDIA_API_KEY="nvapi-xxxxxxxxxxxx"
nemoclaw onboard  # 重新运行以重新配置
```

### 错误：Docker 未运行

```
Error: Cannot connect to Docker daemon
```

**解决方法：**
```bash
sudo systemctl start docker
sudo usermod -aG docker $USER  # 将当前用户添加到 docker 组
newgrp docker
```

### 错误：OpenShell 未安装

```
Error: 'openshell' command not found
```

**解决方法：** 先安装 [NVIDIA OpenShell](https://github.com/NVIDIA/OpenShell)，然后重新运行 NemoClaw 安装器。

### 代理阻止出站请求

当你在 TUI 中看到阻止请求通知时：

```bash
openshell term        # 打开 TUI 以批准/拒绝请求
# 或更新策略以允许主机：
nemoclaw my-assistant policy update --allow-host api.example.com
```

### 查看完整调试日志

```bash
nemoclaw my-assistant logs --follow
# 或使用详细标志
nemoclaw my-assistant logs --follow --level debug
```

---

## 文档链接

- [概述](https://docs.nvidia.com/nemoclaw/latest/about/overview.html)
- [工作原理](https://docs.nvidia.com/nemoclaw/latest/about/how-it-works.html)
- [架构](https://docs.nvidia.com/nemoclaw/latest/reference/architecture.html)
- [推理配置文件](https://docs.nvidia.com/nemoclaw/latest/reference/inference-profiles.html)
- [网络策略](https://docs.nvidia.com/nemoclaw/latest/reference/network-policies.html)
- [CLI 命令](https://docs.nvidia.com/nemoclaw/latest/reference/commands.html)
