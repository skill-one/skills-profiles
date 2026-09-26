# OpenHanako 个人AI代理

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能集合。

OpenHanako是一个基于Electron构建的桌面AI代理平台，为每个代理提供持久化内存、独特的个性，并能够自主操作您的计算机 — 读取/写入文件、运行终端命令、浏览网页、执行JavaScript以及管理日程。多个代理可以通过频道群聊或任务委托进行协作。

---

## 安装

### 下载并运行

```bash
# macOS Apple Silicon — 从发布页面下载
# https://github.com/liliMozi/openhanako/releases
# 挂载.dmg文件并拖拽到应用程序

# 首次启动 — 一次性绕过Gatekeeper：
# 右键点击应用 → 打开 → 打开
```

```powershell
# Windows — 从发布页面运行.exe安装程序
# SmartScreen警告：点击"更多信息" → "无论如何运行"
```

### 从源代码构建

```bash
git clone https://github.com/liliMozi/openhanako.git
cd openhanako
npm install

# 开发模式
npm run dev

# 生产构建
npm run build

# 运行测试
npm test
```

---

## 首次运行引导

首次启动时，向导会要求提供：

1. **语言** — UI语言偏好
2. **您的姓名** — 代理在称呼您时会使用
3. **模型提供者** — 任何OpenAI兼容的端点
4. **三个模型**：
   - `聊天模型` — 主要对话（例如 `gpt-4o`, `deepseek-chat`）
   - `实用模型` — 轻量级任务、摘要（例如 `gpt-4o-mini`）
   - `实用大型模型` — 内存编译、深度分析（例如 `gpt-4o`）

### 提供者配置示例

```json
// OpenAI
{
  "baseURL": "https://api.openai.com/v1",
  "apiKey": "process.env.OPENAI_API_KEY"
}

// DeepSeek
{
  "baseURL": "https://api.deepseek.com/v1",
  "apiKey": "process.env.DEEPSEEK_API_KEY"
}

// 本地Ollama
{
  "baseURL": "http://localhost:11434/v1",
  "apiKey": "ollama"
}

// Qwen（阿里云）
{
  "baseURL": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "apiKey": "process.env.DASHSCOPE_API_KEY"
}
```

---

## 项目架构

```
openhanako/
├── core/           # 引擎编排 + 管理器（代理、会话、模型、偏好设置、技能）
├── lib/            # 核心库
│   ├── memory/     # 自定义内存系统（近期衰减）
│   ├── tools/      # 内置工具（文件、终端、浏览器、截图、画布）
│   ├── sandbox/    # PathGuard + OS级隔离（Seatbelt/Bubblewrap）
│   └── bridge/     # 多平台适配器（Telegram、飞书、QQ）
├── server/         # Fastify 5 HTTP + WebSocket服务器
├── hub/            # 调度器、频道路由器、事件总线
├── desktop/        # Electron 38 主进程 + React 19 前端
├── tests/          # Vitest测试套件
└── skills2set/     # 内置技能定义
```

### 关键管理器（通过统一引擎接口）

| 管理器 | 职责 |
|---------|---------------|
| `AgentManager` | 创建、加载、删除代理 |
| `SessionManager` | 每个代理的对话会话 |
| `ModelManager` | 将请求路由到配置的提供者 |
| `PreferencesManager` | 用户/全局设置 |
| `SkillManager` | 安装、启用、禁用、沙盒技能 |

---

## 代理配置

每个代理是一个可备份的自包含文件夹：

```
~/.openhanako/agents/<agent-id>/
├── personality.md      # 个性模板（自由文本或结构化）
├── memory/
│   ├── working.db      # 近期事件（SQLite WAL）
│   └── compiled.md     # 长期编译内存
├── desk/               # 代理的文件工作区
│   └── notes/          # Jian笔记
└── skills/             # 代理本地安装的技能
```

### 个性模板示例

```markdown
# Hanako

你是Hanako，一个冷静且周到的助手，你倾向于直接而不是啰嗦。
你记得过去的对话，并自然地引用它们。
在开始大型任务之前，你会询问澄清问题。
在写代码时，你总是添加简短的行内注释。

## 语气
- 温暖但专业
- 偶尔使用冷幽默
- 从不使用空洞的肯定（“好问题！”）

## 限制
- 删除文件前始终确认
- 摘要长终端输出而不是原始输出
```

---

## 技能系统

技能扩展代理的功能。它们存在于 `skills2set/`（内置）或按代理安装。

### 从GitHub安装技能

```javascript
// 通过应用的技能UI或编程方式：
const { skillManager } = engine;

await skillManager.installFromGitHub({
  repo: 'some-user/hanako-skill-weather',
  agentId: 'agent-abc123',
  safetyReview: true   // 默认启用严格审查
});
```

### 技能定义格式（SKILL.md → skills2set）

```markdown
---
name: web-scraper
version: 1.0.0
description: 从网页抓取结构化数据
tools:
  - browser
  - javascript
permissions:
  - network
---

## 对代理的说明

当要求抓取页面时：
1. 使用 `browser` 工具导航到URL
2. 使用 `executeJavaScript` 提取结构化数据
3. 将结果保存到工作区为JSON
```

### 编写自定义技能（JavaScript）

```javascript
// skills/my-skill/index.js
export default {
  name: 'my-skill',
  version: '1.0.0',
  description: '做一些有用的事',

  // 该技能为代理添加的工具
  tools: [
    {
      name: 'fetch_weather',
      description: '获取城市的当前天气',
      parameters: {
        type: 'object',
        properties: {
          city: { type: 'string', description: '城市名称' }
        },
        required: ['city']
      },
      async execute({ city }) {
        const res = await fetch(
          `https://wttr.in/${encodeURIComponent(city)}?format=j1`
        );
        const data = await res.json();
        return {
          temp_c: data.current_condition[0].temp_C,
          description: data.current_condition[0].weatherDesc[0].value
        };
      }
    }
  ]
};
```

---

## 内存系统

OpenHanako使用近期衰减内存模型：近期事件保持清晰，旧事件逐渐淡化。

```javascript
// 以编程方式访问内存（core/lib/memory）
import { MemoryManager } from './lib/memory/index.js';

const memory = new MemoryManager({ agentId: 'agent-abc123' });

// 存储一个内存事件
await memory.store({
  type: 'conversation',
  content: '用户喜欢暗黑模式和简洁的回复',
  importance: 0.8   // 0.0–1.0；越高衰减越慢
});

// 检索相关记忆
const relevant = await memory.query({
  query: '用户偏好',
  limit: 10,
  minRelevance: 0.5
});

// 手动触发编译（通常自动运行）
await memory.compile();
```

### 内存层级

| 层级 | 存储 | 衰减 |
|------|---------|-------|
| 工作内存 | `working.db` (SQLite) | 快速 — 近期N轮 |
| 编译内存 | `compiled.md` | 缓慢 — 由实用大型模型摘要 |
| 工作区笔记（Jian） | 工作区文件 | 手动 / 无衰减 |

---

## 内置工具

代理开箱即用的工具：

```javascript
// 文件操作
{ tool: 'read_file',   args: { path: '/Users/me/notes.txt' } }
{ tool: 'write_file',  args: { path: '/Users/me/out.txt', content: '...' } }

// 终端
{ tool: 'run_command', args: { command: 'ls -la', cwd: '/Users/me' } }

// 浏览器和网页
{ tool: 'browse',      args: { url: 'https://example.com' } }
{ tool: 'web_search',  args: { query: 'OpenHanako最新发布' } }

// 屏幕
{ tool: 'screenshot',  args: {} }

// 画布
{ tool: 'draw',        args: { instructions: '...' } }

// 代码执行
{ tool: 'execute_js',  args: { code: 'return 2 + 2' } }
```

### 沙盒访问层级（PathGuard）

```
层级0 — 拒绝：     系统路径（/System, /usr, 注册表 hive）
层级1 — 只读：  家目录文件（工作区外）
层级2 — 读写：  仅工作区文件夹
层级3 — 全权：  明确授权的路径（用户确认）
```

OS级沙盒：**macOS Seatbelt** / **Linux Bubblewrap** 包装技能进程。

---

## 多代理设置

```javascript
// core/AgentManager使用示例
import { createEngine } from './core/engine.js';

const engine = await createEngine();

// 创建第二个代理
const researchAgent = await engine.agentManager.create({
  name: '研究者',
  personalityTemplate: 'researcher.md',
  models: {
    chat: 'deepseek-chat',
    utility: 'gpt-4o-mini',
    utilityLarge: 'gpt-4o'
  }
});

// 通过频道从一个代理委托任务到另一个代理
await engine.hub.channelRouter.delegate({
  fromAgent: 'agent-abc123',
  toAgent: researchAgent.id,
  task: '查找2025年发表的关于专家混合的顶级5篇论文',
  returnTo: 'agent-abc123'   // 结果自动路由回
});
```

---

## 定时任务（Cron & Heartbeat）

```javascript
// hub/scheduler使用
import { Scheduler } from './hub/scheduler.js';

const scheduler = new Scheduler({ agentId: 'agent-abc123' });

// 每天早上9点运行任务
scheduler.cron('daily-briefing', '0 9 * * *', async () => {
  await agent.run('总结我昨天的笔记并发布到#briefing频道');
});

// Heartbeat — 每5分钟检查工作区是否有新文件
scheduler.heartbeat('desk-watch', 300_000, async () => {
  const changed = await agent.desk.checkChanges();
  if (changed.length > 0) {
    await agent.run(`工作区有新文件：${changed.join(', ')} — 摘要并通知我`);
  }
});

scheduler.start();
```

---

## 多平台桥接

同时连接一个代理到Telegram、飞书和QQ：

```javascript
// lib/bridge配置
const bridgeConfig = {
  telegram: {
    enabled: true,
    token: process.env.TELEGRAM_BOT_TOKEN,
    allowedUsers: [process.env.TELEGRAM_ALLOWED_USER_ID]
  },
  feishu: {
    enabled: true,
    appId: process.env.FEISHU_APP_ID,
    appSecret: process.env.FEISHU_APP_SECRET
  },
  qq: {
    enabled: false
  }
};

await engine.agentManager.setBridges('agent-abc123', bridgeConfig);
```

---

## 服务器API（Fastify + WebSocket）

嵌入式Fastify服务器在本地运行，Electron主进程通过stdio桥接通信。

```javascript
// WebSocket — 实时聊天流
const ws = new WebSocket('ws://localhost:PORT/ws/agent-abc123');

ws.send(JSON.stringify({
  type: 'chat',
  content: '总结我的项目文件夹'
}));

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  // msg.type: 'chunk' | 'tool_call' | 'tool_result' | 'done'
  console.log(msg);
};

// HTTP — 一次性任务
const res = await fetch('http://localhost:PORT/api/agent/agent-abc123/run', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ task: '列出我工作区所有.md文件' })
});
const result = await res.json();
```

---

## 测试

```bash
# 运行所有测试
npm test

# 运行特定测试文件
npx vitest run tests/memory.test.js

# 监视模式
npx vitest
```

```javascript
// tests/memory.test.js示例模式
import { describe, it, expect, beforeEach } from 'vitest';
import { MemoryManager } from '../lib/memory/index.js';

describe('MemoryManager', () => {
  let memory;

  beforeEach(async () => {
    memory = new MemoryManager({ agentId: 'test-agent', inMemory: true });
    await memory.init();
  });

  it('存储和检索记忆', async () => {
    await memory.store({ type: 'fact', content: '用户喜欢暗黑模式', importance: 0.9 });
    const results = await memory.query({ query: '暗黑模式', limit: 5 });
    expect(results[0].content).toContain('暗黑模式');
  });
});
```

---

## 故障排除

### macOS上应用无法打开
```bash
# 如果右键点击 → 打开无效，则移除隔离属性
xattr -dr com.apple.quarantine /Applications/OpenHanako.app
```

### 代理无响应
- 确认API密钥环境变量已设置且基础URL可访问
- 打开开发者工具（`Cmd+Option+I` / `Ctrl+Shift+I`）→ 控制台查看错误
- 验证模型名称与您的提供者支持的一致

### 内存编译未触发
```javascript
// 强制手动编译
await engine.agentManager.getAgent('agent-abc123').memory.compile({ force: true });
```

### 技能安装因安全审查被阻止
```javascript
// 仅对受信任的本地技能暂时禁用安全审查
await skillManager.installLocal({
  path: './my-skill',
  agentId: 'agent-abc123',
  safetyReview: false   // ⚠️ 仅限本地开发，绝不用于不受信任的来源
});
```

### 沙盒权限被拒绝
- 检查PathGuard层级访问的路径
- 使用桌面UI：代理设置 → 沙盒 → 授权路径访问
- 或编程方式请求提升到层级3（提示用户确认）

### Windows Defender对内置.exe产生误报
- 安装程序未签名；在SmartScreen中点击**更多信息 → 无论如何运行**
- 如有必要，在开发期间在Windows安全设置中添加排除项

---

## 关键链接

- **发布版:** https://github.com/liliMozi/openhanako/releases
- **问题:** https://github.com/liliMozi/openhanako/issues
- **主页:** https://openhanako.com
- **贡献:** https://github.com/liliMozi/openhanako/blob/main/CONTRIBUTING.md
- **安全策略:** https://github.com/liliMozi/openhanako/blob/main/SECURITY.md
- **许可证:** Apache 2.0
