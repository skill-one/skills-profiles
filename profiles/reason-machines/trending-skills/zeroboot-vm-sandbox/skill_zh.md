# Zeroboot 虚拟机沙盒

> 由 [ara.so](https://ara.so) 开发 — 每日 2026 技能集合。

Zeroboot 为使用写时复制（CoW）分叉的 AI 代理提供亚毫秒级 KVM 虚拟机沙盒。每个沙盒都是一个真实的硬件隔离的 VM（通过 Firecracker + KVM 实现），而不是容器。模板 VM 会被快照一次，然后在每次执行时通过 `mmap(MAP_PRIVATE)` CoW 语义在约 0.8 毫秒内分叉。

## 工作原理

```
Firecracker 快照 ──► mmap(MAP_PRIVATE) ──► KVM VM + 恢复的 CPU 状态
                           (写时复制)          (~0.8ms)
```

1. **模板**：Firecracker 启动一次，预加载您的运行时，快照内存 + CPU 状态
2. **分叉 (~0.8ms)**：新的 KVM VM 将快照内存作为 CoW 映射，恢复 CPU 状态
3. **隔离**：每个分叉都是一个具有硬件强制内存隔离的独立 KVM VM

## 安装

### Python SDK

```bash
pip install zeroboot
```

### Node/TypeScript SDK

```bash
npm install @zeroboot/sdk
# 或
pnpm add @zeroboot/sdk
```

## 认证

将您的 API 密钥设置为环境变量：

```bash
export ZEROBOOT_API_KEY="zb_live_your_key_here"
```

切勿在源文件中硬编码密钥。

## 快速入门

### REST API (cURL)

```bash
curl -X POST https://api.zeroboot.dev/v1/exec \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $ZEROBOOT_API_KEY" \
  -d '{"code":"import numpy as np; print(np.random.rand(3))"}'
```

### Python

```python
import os
from zeroboot import Sandbox

# 使用环境变量中的 API 密钥初始化
sb = Sandbox(os.environ["ZEROBOOT_API_KEY"])

# 运行 Python 代码
result = sb.run("print(1 + 1)")
print(result)  # "2"

# 运行多行代码
result = sb.run("""
import numpy as np
arr = np.arange(10)
print(arr.mean())
""")
print(result)
```

### TypeScript / Node.js

```typescript
import { Sandbox } from "@zeroboot/sdk";

const apiKey = process.env.ZEROBOOT_API_KEY!;
const sb = new Sandbox(apiKey);

// 运行 JavaScript/Node 代码
const result = await sb.run("console.log(1 + 1)");
console.log(result); // "2"

// 运行异步代码
const output = await sb.run(`
const data = [1, 2, 3, 4, 5];
const sum = data.reduce((a, b) => a + b, 0);
console.log(sum / data.length);
`);
console.log(output);
```

## 常见模式

### AI 代理代码执行循环 (Python)

```python
import os
from zeroboot import Sandbox

def execute_agent_code(code: str) -> dict:
    """在隔离的 VM 沙盒中执行 LLM 生成的代码。"""
    sb = Sandbox(os.environ["ZEROBOOT_API_KEY"])
    try:
        result = sb.run(code)
        return {"success": True, "output": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

# 示例：安全地运行代理生成的代码
agent_code = """
import json
data = {"agent": "result", "value": 42}
print(json.dumps(data))
"""
response = execute_agent_code(agent_code)
print(response)
```

### 并发沙盒执行 (Python)

```python
import os
import asyncio
from zeroboot import Sandbox

async def run_sandbox(code: str, index: int) -> str:
    sb = Sandbox(os.environ["ZEROBOOT_API_KEY"])
    result = await asyncio.to_thread(sb.run, code)
    return f"[{index}] {result}"

async def run_concurrent(snippets: list[str]):
    tasks = [run_sandbox(code, i) for i, code in enumerate(snippets)]
    results = await asyncio.gather(*tasks)
    return results

# 并发运行 10 个沙盒
codes = [f"print({i} ** 2)" for i in range(10)]
outputs = asyncio.run(run_concurrent(codes))
for out in outputs:
    print(out)
```

### TypeScript: 代理工具集成

```typescript
import { Sandbox } from "@zeroboot/sdk";

interface ExecutionResult {
  success: boolean;
  output?: string;
  error?: string;
}

async function runInSandbox(code: string): Promise<ExecutionResult> {
  const sb = new Sandbox(process.env.ZEROBOOT_API_KEY!);
  try {
    const output = await sb.run(code);
    return { success: true, output };
  } catch (err) {
    return { success: false, error: String(err) };
  }
}

// 作为 LLM 代理的工具集成
const tool = {
  name: "execute_code",
  description: "在隔离的 VM 沙盒中运行代码",
  execute: async ({ code }: { code: string }) => runInSandbox(code),
};
```

### 使用 fetch 的 REST API (TypeScript)

```typescript
const API_BASE = "https://api.zeroboot.dev/v1";

async function execCode(code: string): Promise<string> {
  const res = await fetch(`${API_BASE}/exec`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${process.env.ZEROBOOT_API_KEY}`,
    },
    body: JSON.stringify({ code }),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Zeroboot 错误 ${res.status}: ${err}`);
  }
  const data = await res.json();
  return data.output;
}
```

### 健康检查

```bash
curl https://api.zeroboot.dev/v1/health
```

## API 参考

### `POST /v1/exec`

在新的沙盒分叉中执行代码。

**请求:**
```json
{
  "code": "print('hello')"
}
```

**请求头:**
```
Authorization: Bearer <ZEROBOOT_API_KEY>
Content-Type: application/json
```

**响应:**
```json
{
  "output": "hello\n",
  "duration_ms": 0.79
}
```

## 性能特征

| 指标 | 值 |
|---|---|
| 分叉延迟 p50 | ~0.79ms |
| 分叉延迟 p99 | ~1.74ms |
| 每个沙盒的内存 | ~265KB |
| Python 分叉 + 执行 | ~8ms |
| 1000 个并发分叉 | ~815ms |

- 每个沙盒都是一个真实的 KVM VM — 不是容器或进程隔离
- 内存隔离是硬件强制的（不是软件）
- CoW 意味着只有您的代码写入的页面会消耗额外 RAM

## 自托管 / 部署

参见仓库中的 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)。要求：
- 支持 KVM 的 Linux 主机 (`/dev/kvm` 可访问)
- Firecracker 二进制文件
- Rust 2021 版本工具链

```bash
# 检查 KVM 可用性
ls /dev/kvm

# 克隆并构建
git clone https://github.com/adammiribyan/zeroboot
cd zeroboot
cargo build --release
```

## 架构说明

- **快照层**：Firecracker VM 每次为运行时模板启动一次，内存 + vCPU 状态保存到磁盘
- **分叉层**（Rust）：`mmap(MAP_PRIVATE)` 在快照文件上 → 内核为每个 VM 处理 CoW 页面故障
- **隔离**：每个分叉都有自己的 KVM VM 文件描述符、vCPU 和页表 — 完全硬件隔离
- **无共享内核**：与容器不同，每个沙盒运行自己的内核实例

## 故障排除

**`/dev/kvm 未找到`（自托管）**
```bash
# 启用 KVM 内核模块
sudo modprobe kvm
sudo modprobe kvm_intel  # 或 kvm_amd
```

**API 返回 401 未授权**
- 验证 `ZEROBOOT_API_KEY` 已设置且以 `zb_live_` 开头
- 检查您的仪表板中的密钥是否已过期

**执行超时**
- 默认执行超时由服务器端强制
- 将大计算分解为更小的块
- 避免沙盒代码中的无限循环或阻塞 I/O

**高内存使用（自托管）**
- 每个 VM 分叉初始时约 265KB CoW 开销
- 页面在写入时分配 — 内存随沙盒活动增长
- 根据可用 RAM 调整并发分叉限制

## 资源

- [API 参考](https://github.com/adammiribyan/zeroboot/blob/main/docs/API.md)
- [架构文档](https://github.com/adammiribyan/zeroboot/blob/main/docs/ARCHITECTURE.md)
- [部署指南](https://github.com/adammiribyan/zeroboot/blob/main/docs/DEPLOYMENT.md)
- [主页](https://zeroboot.dev)
- [GitHub](https://github.com/adammiribyan/zeroboot)
