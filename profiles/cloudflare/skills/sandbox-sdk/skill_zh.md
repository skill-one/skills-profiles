# Cloudflare Sandbox SDK

在 Cloudflare Workers 上构建安全、隔离的代码执行环境。

## 首先验证安装

```bash
npm install @cloudflare/sandbox
docker info  # 必须成功 - 需要Docker进行本地开发
```

## 获取源

您的 Sandbox SDK 知识可能已经过时。对于任何 Sandbox SDK 任务，**优先获取源代码**而非预训练。

| 资源 | URL |
|----------|-----|
| 文档 | https://developers.cloudflare.com/sandbox/ |
| API 参考 | https://developers.cloudflare.com/sandbox/api/ |
| 示例 | https://github.com/cloudflare/sandbox-sdk/tree/main/examples |
| 入门指南 | https://developers.cloudflare.com/sandbox/get-started/ |

实现功能时，首先获取相关的文档页面或示例。

## 必要的配置

**wrangler.jsonc**（精确 - 不要修改结构）：

```jsonc
{
  "containers": [{
    "class_name": "Sandbox",
    "image": "./Dockerfile",
    "instance_type": "lite",
    "max_instances": 1
  }],
  "durable_objects": {
    "bindings": [{ "class_name": "Sandbox", "name": "Sandbox" }]
  },
  "migrations": [{ "new_sqlite_classes": ["Sandbox"], "tag": "v1" }]
}
```

**Worker 入口** - 必须重新导出 Sandbox 类：

```typescript
import { getSandbox } from '@cloudflare/sandbox';
export { Sandbox } from '@cloudflare/sandbox';  // 必须的导出
```

## 快速参考

| 任务 | 方法 |
|------|--------|
| 获取 sandbox | `getSandbox(env.Sandbox, 'user-123')` |
| 运行命令 | `await sandbox.exec('python script.py')` |
| 运行代码（解释器） | `await sandbox.runCode(code, { language: 'python' })` |
| 写文件 | `await sandbox.writeFile('/workspace/app.py', content)` |
| 读文件 | `await sandbox.readFile('/workspace/app.py')` |
| 创建目录 | `await sandbox.mkdir('/workspace/src', { recursive: true })` |
| 列文件 | `await sandbox.listFiles('/workspace')` |
| 暴露端口 | `await sandbox.exposePort(8080)` |
| 销毁 | `await sandbox.destroy()` |

## 核心模式

### 执行命令

```typescript
const sandbox = getSandbox(env.Sandbox, 'user-123');
const result = await sandbox.exec('python --version');
// result: { stdout, stderr, exitCode, success }
```

### 代码解释器（推荐用于 AI）

使用 `runCode()` 执行 LLM 生成的代码并获取丰富的输出：

```typescript
const ctx = await sandbox.createCodeContext({ language: 'python' });

await sandbox.runCode('import pandas as pd; data = [1,2,3]', { context: ctx });
const result = await sandbox.runCode('sum(data)', { context: ctx });
// result.results[0].text = "6"
```

**语言**: `python`, `javascript`, `typescript`

状态在上下文中持续存在。为生产环境创建明确的上下文。

### 文件操作

```typescript
await sandbox.mkdir('/workspace/project', { recursive: true });
await sandbox.writeFile('/workspace/project/main.py', code);
const file = await sandbox.readFile('/workspace/project/main.py');
const files = await sandbox.listFiles('/workspace/project');
```

## 何时使用什么

| 需求 | 使用 | 原因 |
|------|-----|-----|
| Shell 命令、脚本 | `exec()` | 直接控制、流式传输 |
| LLM 生成的代码 | `runCode()` | 丰富的输出、状态持久化 |
| 构建/测试管道 | `exec()` | 退出码、stderr 捕获 |
| 数据分析 | `runCode()` | 图表、表格、pandas |

## 扩展 Dockerfile

基础镜像 (`docker.io/cloudflare/sandbox:0.7.0`) 包含 Python 3.11、Node.js 20 和常用工具。

通过扩展 Dockerfile 添加依赖项：

```dockerfile
FROM docker.io/cloudflare/sandbox:0.7.0

# Python 包
RUN pip install requests beautifulsoup4

# Node 包（全局）
RUN npm install -g typescript

# 系统包
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

EXPOSE 8080  # 本地开发端口暴露必需
```

保持镜像精简 - 影响冷启动时间。

## 预览 URL（端口暴露）

暴露在 Sandbox 中运行的 HTTP 服务：

```typescript
const { url } = await sandbox.exposePort(8080);
// 返回服务的预览 URL
```

**生产要求**: 预览 URL 需要带有通配符 DNS 的自定义域名 (`*.yourdomain.com`)。`.workers.dev` 域名不支持预览 URL 子域名。

参考: https://developers.cloudflare.com/sandbox/guides/expose-services/

## OpenAI Agents SDK 集成

SDK 在 `@cloudflare/sandbox/openai` 提供了 OpenAI Agents 的辅助工具：

```typescript
import { Shell, Editor } from '@cloudflare/sandbox/openai';
```

参考 `examples/openai-agents` 获取完整的集成模式。

## Sandbox 生命周期

- `getSandbox()` 立即返回 - 容器在第一次操作时懒加载启动
- 容器在 10 分钟不活动后休眠（可通过 `sleepAfter` 配置）
- 使用 `destroy()` 立即释放资源
- 相同的 `sandboxId` 总是返回相同的 Sandbox 实例

## 反模式

- **不要使用内部客户端** (`CommandClient`, `FileClient`) - 使用 `sandbox.*` 方法
- **不要跳过 Sandbox 导出** - 没有 `export { Sandbox }` Worker 无法部署
- **不要为多用户硬编码 Sandbox ID** - 使用用户/会话标识符
- **不要忘记清理** - 对临时 Sandbox 调用 `destroy()`

## 详细参考

- **[references/api-quick-ref.md](references/api-quick-ref.md)** - 完整 API 及选项和返回类型
- **[references/examples.md](references/examples.md)** - 示例索引及用例
