# KeyID Agent Kit — MCP 电子邮件工具用于 AI 代理

> 技能由 [ara.so](https://ara.so) 提供 — 2026 每日技能集合。

KeyID Agent Kit 通过模型上下文协议为 AI 代理（Claude、Cursor 或任何 MCP 客户端）提供一个真实、可用的电子邮件地址和 27 种工具。无需注册，无需手动获取 API 密钥，免费使用。由 [KeyID.ai](https://keyid.ai) 提供支持。

## 功能

- 自动为您的 AI 代理配置一个真实电子邮件地址
- 提供 27 种 MCP 工具：发送、接收、回复、转发、搜索、联系人、草稿、Webhook、自动回复、签名、转发规则、指标
- 作为 stdio MCP 服务器运行 — 兼容 Claude Desktop、Cursor 和任何 MCP 客户端
- 使用 Ed25519 密钥对进行身份验证 — 如果未提供，则自动生成

## 安装

```bash
npm install @keyid/agent-kit
# 或
yarn add @keyid/agent-kit
# 或直接运行，无需安装
npx @keyid/agent-kit
```

## 配置

### 环境变量

| 变量               | 描述                                                         | 默认值                       |
|--------------------|--------------------------------------------------------------|-----------------------------|
| `KEYID_PUBLIC_KEY` | Ed25519 公钥（十六进制）                                     | 首次运行时自动生成           |
| `KEYID_PRIVATE_KEY` | Ed25519 私钥（十六进制）                                     | 首次运行时自动生成           |
| `KEYID_BASE_URL`   | API 基础 URL                                                 | `https://keyid.ai`          |

**重要提示**：首次运行后保存自动生成的密钥，以便您的代理在会话之间保持相同的电子邮件地址。密钥在首次启动时打印到 stderr。

### Claude Desktop 设置

编辑 macOS 的 `~/Library/Application Support/Claude/claude_desktop_config.json` 或 Windows 的 `%APPDATA%\Claude\claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "keyid": {
      "command": "npx",
      "args": ["@keyid/agent-kit"],
      "env": {
        "KEYID_PUBLIC_KEY": "$KEYID_PUBLIC_KEY",
        "KEYID_PRIVATE_KEY": "$KEYID_PRIVATE_KEY"
      }
    }
  }
}
```

### Cursor 设置

在项目根目录的 `.cursor/mcp.json` 或全局 Cursor 设置中：

```json
{
  "mcpServers": {
    "keyid": {
      "command": "npx",
      "args": ["@keyid/agent-kit"],
      "env": {
        "KEYID_PUBLIC_KEY": "$KEYID_PUBLIC_KEY",
        "KEYID_PRIVATE_KEY": "$KEYID_PRIVATE_KEY"
      }
    }
  }
}
```

### 首次运行 — 获取您的电子邮件地址

```bash
# 运行一次以生成密钥并注册代理
npx @keyid/agent-kit
# 密钥打印到 stderr — 保存它们！
# 然后在您的环境或配置中设置它们
export KEYID_PUBLIC_KEY=<十六进制值从输出>
export KEYID_PRIVATE_KEY=<十六进制值从输出>
```

## 所有 27 种工具参考

### 身份与认证

```
keyid_provision     — 注册代理，获取分配的电子邮件地址
keyid_get_email     — 获取当前活动的电子邮件地址
```

### 消息

```
keyid_get_inbox          — 获取收件箱；支持搜索查询、过滤、分页
keyid_send               — 发送电子邮件（收件人、主题、正文、HTML、计划时间、显示名称）
keyid_reply              — 通过消息 ID 回复消息
keyid_forward            — 将消息转发到另一个地址
keyid_update_message     — 标记已读/未读、星标/取消星标
keyid_get_unread_count   — 获取未读消息数量
```

### 线程与草稿

```
keyid_list_threads   — 列出对话线程
keyid_get_thread     — 获取包含所有消息的线程
keyid_create_draft   — 保存草稿
keyid_send_draft     — 发送之前保存的草稿
```

### 设置

```
keyid_get_auto_reply   — 获取当前自动回复/休假回复配置
keyid_set_auto_reply   — 启用/禁用自动回复并使用自定义消息
keyid_get_signature    — 获取电子邮件签名
keyid_set_signature    — 设置电子邮件签名文本/HTML
keyid_get_forwarding   — 获取转发规则
keyid_set_forwarding   — 添加或更新转发到另一个地址
```

### 联系人

```
keyid_list_contacts    — 列出所有保存的联系人
keyid_create_contact   — 创建联系人（姓名、电子邮件、备注）
keyid_delete_contact   — 通过 ID 删除联系人
```

### Webhook

```
keyid_list_webhooks           — 列出配置的 Webhook
keyid_create_webhook          — 注册用于传入事件的 Webhook URL
keyid_get_webhook_deliveries  — 查看交付历史和失败记录
```

### 列表与指标

```
keyid_manage_list   — 将地址添加或从允许或阻止列表中移除
keyid_get_metrics   — 查询使用指标（发送、接收、退回）
```

## 实际代码示例

### 程序化 MCP 客户端（Node.js）

```javascript
import { spawn } from 'child_process';
import { createInterface } from 'readline';

// 以子进程方式启动 MCP 服务器
const server = spawn('npx', ['@keyid/agent-kit'], {
  env: {
    ...process.env,
    KEYID_PUBLIC_KEY: process.env.KEYID_PUBLIC_KEY,
    KEYID_PRIVATE_KEY: process.env.KEYID_PRIVATE_KEY,
  },
  stdio: ['pipe', 'pipe', 'inherit'],
});

// 发送 JSON-RPC 请求
function sendRequest(method, params = {}) {
  const request = {
    jsonrpc: '2.0',
    id: Date.now(),
    method,
    params,
  };
  server.stdin.write(JSON.stringify(request) + '\n');
}

// 读取响应
const rl = createInterface({ input: server.stdout });
rl.on('line', (line) => {
  const response = JSON.parse(line);
  console.log('Response:', JSON.stringify(response, null, 2));
});

// 初始化 MCP 会话
sendRequest('initialize', {
  protocolVersion: '2024-11-05',
  capabilities: {},
  clientInfo: { name: 'my-app', version: '1.0.0' },
});
```

### 通过 MCP JSON-RPC 调用工具

```javascript
// 初始化后，调用 tools/call
function callTool(toolName, toolArgs) {
  const request = {
    jsonrpc: '2.0',
    id: Date.now(),
    method: 'tools/call',
    params: {
      name: toolName,
      arguments: toolArgs,
    },
  };
  server.stdin.write(JSON.stringify(request) + '\n');
}

// 获取收件箱
callTool('keyid_get_inbox', { limit: 10 });

// 发送电子邮件
callTool('keyid_send', {
  to: 'colleague@example.com',
  subject: '来自我的 AI 代理的问候',
  body: '这封电子邮件是由使用 KeyID 的 AI 代理发送的。',
});

// 回复消息
callTool('keyid_reply', {
  message_id: 'msg_abc123',
  body: '谢谢，我今天会处理这个。',
});

// 搜索收件箱
callTool('keyid_get_inbox', {
  query: 'from:alice@company.com subject:report',
  unread_only: true,
});

// 设置自动回复
callTool('keyid_set_auto_reply', {
  enabled: true,
  subject: '外出办公',
  body: '我目前无法回复。我的 AI 代理将很快回复。',
});

// 创建联系人
callTool('keyid_create_contact', {
  name: 'Alice Smith',
  email: 'alice@company.com',
  notes: 'Q1 项目的负责人',
});

// 安排发送电子邮件
callTool('keyid_send', {
  to: 'team@company.com',
  subject: '每周更新',
  body: '以下是每周状态...',
  scheduled_at: '2026-03-25T09:00:00Z',
});

// 设置电子邮件签名
callTool('keyid_set_signature', {
  signature: '此致,\nAI 代理\n由 KeyID.ai 支持',
});

// 获取指标
callTool('keyid_get_metrics', {
  period: '7d',
});
```

### 使用 MCP SDK（如果正在构建自定义客户端）

```javascript
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

const transport = new StdioClientTransport({
  command: 'npx',
  args: ['@keyid/agent-kit'],
  env: {
    KEYID_PUBLIC_KEY: process.env.KEYID_PUBLIC_KEY,
    KEYID_PRIVATE_KEY: process.env.KEYID_PRIVATE_KEY,
  },
});

const client = new Client(
  { name: 'my-email-agent', version: '1.0.0' },
  { capabilities: {} }
);

await client.connect(transport);

// 列出可用工具
const tools = await client.listTools();
console.log('可用工具:', tools.tools.map(t => t.name));

// 获取电子邮件地址
const emailResult = await client.callTool({
  name: 'keyid_get_email',
  arguments: {},
});
console.log('代理电子邮件:', emailResult.content[0].text);

// 检查未读
const unread = await client.callTool({
  name: 'keyid_get_unread_count',
  arguments: {},
});
console.log('未读数量:', unread.content[0].text);

// 发送电子邮件
await client.callTool({
  name: 'keyid_send',
  arguments: {
    to: 'recipient@example.com',
    subject: '自动报告',
    body: '您的每日报告已附上。',
    html: '<p>您的 <strong>每日报告</strong> 已附上。</p>',
  },
});

await client.close();
```

### Webhook 集成

```javascript
import express from 'express';

const app = express();
app.use(express.json());

// 接收 KeyID Webhook 事件的端点
app.post('/keyid-webhook', (req, res) => {
  const event = req.body;

  if (event.type === 'message.received') {
    const { from, subject, body, message_id } = event.data;
    console.log(`收到新电子邮件来自 ${from}: ${subject}`);
    
    // 在此处触发您的代理逻辑
    handleIncomingEmail({ from, subject, body, message_id });
  }

  res.json({ ok: true });
});

app.listen(3000);

// 通过 MCP 工具注册 Webhook
// （通过您的代理调用一次）
// callTool('keyid_create_webhook', {
//   url: 'https://您的服务器.com/keyid-webhook',
//   events: ['message.received'],
// });
```

## 常见模式

### 模式：具有持久身份的代理

```javascript
// 生成并保存密钥一次，永久重用
import { writeFileSync, readFileSync, existsSync } from 'fs';
import { generateKeyPairSync } from 'crypto'; // 或使用 @noble/ed25519

const KEY_FILE = '.keyid-keys.json';

function loadOrCreateKeys() {
  if (existsSync(KEY_FILE)) {
    return JSON.parse(readFileSync(KEY_FILE, 'utf8'));
  }
  // 让 @keyid/agent-kit 在首次运行时自动生成，
  // 然后保存它打印到 stderr 的内容
  // 或使用 @noble/ed25519 预先生成：
  // const privKey = randomBytes(32);
  // const pubKey = await ed.getPublicKeyAsync(privKey);
  return null; // 将自动生成
}
```

### 模式：电子邮件触发的代理循环

```javascript
// 轮询收件箱并处理新消息
async function agentEmailLoop(client) {
  while (true) {
    const result = await client.callTool({
      name: 'keyid_get_inbox',
      arguments: { unread_only: true, limit: 5 },
    });

    const messages = JSON.parse(result.content[0].text);

    for (const msg of messages) {
      // 使用您的 LLM/代理逻辑处理
      const agentResponse = await processWithAgent(msg);

      // 回复
      await client.callTool({
        name: 'keyid_reply',
        arguments: {
          message_id: msg.id,
          body: agentResponse,
        },
      });

      // 标记为已读
      await client.callTool({
        name: 'keyid_update_message',
        arguments: { message_id: msg.id, read: true },
      });
    }

    // 等待 60 秒后进行下一次轮询
    await new Promise(r => setTimeout(r, 60_000));
  }
}
```

### 模式：草稿-审核-发送工作流

```javascript
// 创建草稿，审核，然后发送
const draft = await client.callTool({
  name: 'keyid_create_draft',
  arguments: {
    to: 'client@example.com',
    subject: '提案',
    body: draftBody,
  },
});

const draftId = JSON.parse(draft.content[0].text).id;

// 人类或代理审核...
// 然后发送：
await client.callTool({
  name: 'keyid_send_draft',
  arguments: { draft_id: draftId },
});
```

## 故障排除

### 代理每次运行都获得新的电子邮件地址
**原因**：密钥在运行之间未持久化。  
**解决方法**：保存首次运行输出中的 `KEYID_PUBLIC_KEY` 和 `KEYID_PRIVATE_KEY`，并在您的配置或环境中设置它们。

### MCP 服务器未出现在 Claude Desktop 中
**解决方法**：编辑配置后重启 Claude Desktop。验证 JSON 是否有效（没有尾随逗号）。检查 `npx` 是否在您的 PATH 中。

### 工具调用返回错误
**解决方法**：确保代理已配置 — 在调用其他工具之前调用 `keyid_provision`，或调用 `keyid_get_email` 以确认代理具有地址。

### 未收到电子邮件
**解决方法**：检查 `keyid_manage_list` 以确保发件人未被阻止列表。检查 `keyid_get_metrics` 以获取退回数据。

### 连接断开/服务器崩溃
**解决方法**：服务器使用 stdio — 确保同一进程中没有其他内容写入 stdout。重启 MCP 服务器进程。

### 密钥自动生成但未显示
**原因**：stderr 可能被您的 MCP 客户端抑制。  
**解决方法**：首先在终端中直接运行 `npx @keyid/agent-kit` 以捕获密钥输出，然后再将其添加到您的 MCP 配置中。

## 协议详情

- **传输**：stdio（JSON-RPC over stdin/stdout）
- **MCP 协议版本**：`2024-11-05`
- **认证**：Ed25519 密钥对 — 公钥成为代理身份，私钥签名请求
- **兼容性**：Claude Desktop、Cursor、任何 MCP 兼容客户端
