# openclaw-control-center

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能集合

OpenClaw Control Center 将 OpenClaw 从一个黑盒转变为本地可审计的控制中心。它提供了对代理活动、令牌消耗、任务执行链、跨会话协作、内存状态和文档来源的可见性，同时具有安全优先的默认设置，默认情况下禁用所有变更。

## 功能概述

- **概览**：系统健康、待处理项、风险信号和操作摘要
- **使用情况**：每日/7天/30天令牌消耗、配额、上下文压力、订阅窗口
- **人员**：谁正在执行与排队 — 不仅仅是“有任务”
- **协作**：父子会话交接和经过验证的跨会话消息（例如 `Main ⇄ Pandas`）
- **任务**：任务看板、审批、执行链、运行证据
- **内存**：每个代理的内存健康、可搜索性和源文件编辑
- **文档**：共享和代理核心文档，从实际源文件打开
- **设置**：连接器接线状态、安全风险摘要、更新状态

## 安装

```bash
git clone https://github.com/TianyiDataScience/openclaw-control-center.git
cd openclaw-control-center
npm install
cp .env.example .env
npm run build
npm test
npm run smoke:ui
npm run dev:ui
```

打开：
- `http://127.0.0.1:4310/?section=overview&lang=zh`
- `http://127.0.0.1:4310/?section=overview&lang=en`

> 使用 `npm run dev:ui` 而不是 `UI_MODE=true npm run dev` — 更稳定，尤其是在 Windows 命令行中。

## 项目结构

```
openclaw-control-center/
├── control-center/          # 所有修改必须保留在此目录内
│   ├── src/
│   │   ├── runtime/         # 核心运行时、连接器、监控器
│   │   └── ui/              # 前端 UI 组件
│   ├── .env.example
│   └── package.json
├── docs/
│   └── assets/              # 截图和文档图片
├── README.md
└── README.en.md
```

> **关键约束**：仅修改 `control-center/` 内的文件。切勿修改 `~/.openclaw/openclaw.json`。

## 环境配置

将 `.env.example` 复制到 `.env` 并进行配置：

```env
# 安全默认值 — 未经理解后果不得更改
READONLY_MODE=true
LOCAL_TOKEN_AUTH_REQUIRED=true
IMPORT_MUTATION_ENABLED=false
IMPORT_MUTATION_DRY_RUN=false
APPROVAL_ACTIONS_ENABLED=false
APPROVAL_ACTIONS_DRY_RUN=true

# 连接
OPENCLAW_GATEWAY_URL=http://127.0.0.1:PORT
OPENCLAW_HOME=~/.openclaw

# UI
PORT=4310
DEFAULT_LANG=zh
```

### 安全标志含义

| 标志 | 默认值 | 效果 |
|------|---------|--------|
| `READONLY_MODE` | `true` | 禁用所有状态变更端点 |
| `LOCAL_TOKEN_AUTH_REQUIRED` | `true` | 导入/导出和写入 API 需要本地令牌 |
| `IMPORT_MUTATION_ENABLED` | `false` | 完全阻止导入变更 |
| `IMPORT_MUTATION_DRY_RUN` | `false` | 启用时导入的干运行模式 |
| `APPROVAL_ACTIONS_ENABLED` | `false` | 硬禁用审批操作 |
| `APPROVAL_ACTIONS_DRY_RUN` | `true` | 启用时审批操作作为干运行执行 |

## 关键命令

```bash
# 开发
npm run dev:ui          # 启动 UI 服务器（推荐）
npm run dev             # 单次运行监控，无 HTTP UI

# 构建 & 测试
npm run build           # TypeScript 编译
npm test                # 运行测试套件
npm run smoke:ui        # UI 端点烟雾测试

# 代码检查
npm run lint            # ESLint 检查
npm run lint:fix        # 自动修复代码检查问题
```

## TypeScript 代码示例

### 连接到运行时监控器

```typescript
import { createMonitor } from './src/runtime/monitor';

const monitor = createMonitor({
  gatewayUrl: process.env.OPENCLAW_GATEWAY_URL ?? 'http://127.0.0.1:4310',
  readonlyMode: process.env.READONLY_MODE !== 'false',
  localTokenAuthRequired: process.env.LOCAL_TOKEN_AUTH_REQUIRED !== 'false',
});

// 获取当前系统概览
const overview = await monitor.getOverview();
console.log(overview.systemStatus);      // 'healthy' | 'degraded' | 'critical'
console.log(overview.pendingItems);      // number
console.log(overview.activeAgents);      // Agent[]
```

### 读取代理人员状态

```typescript
import { StaffConnector } from './src/runtime/connectors/staff';

const staff = new StaffConnector({ gatewayUrl: process.env.OPENCLAW_GATEWAY_URL });

// 获取正在执行的代理（不仅仅是排队）
const activeAgents = await staff.getActiveAgents();
activeAgents.forEach(agent => {
  console.log(`${agent.name}: ${agent.status}`);
  // 'executing' | 'queued' | 'idle' | 'blocked'
  console.log(`当前任务: ${agent.currentTask?.title ?? '无'}`);
  console.log(`最后输出: ${agent.lastOutput}`);
});

// 获取完整人员名单，包括排队深度
const roster = await staff.getRoster();
```

### 追踪跨会话协作

```typescript
import { CollaborationTracer } from './src/runtime/connectors/collaboration';

const tracer = new CollaborationTracer({ gatewayUrl: process.env.OPENCLAW_GATEWAY_URL });

// 获取父子会话交接
const handoffs = await tracer.getSessionHandoffs();
handoffs.forEach(handoff => {
  console.log(`${handoff.parentSession} → ${handoff.childSession}`);
  console.log(`委派任务: ${handoff.taskTitle}`);
  console.log(`状态: ${handoff.status}`);
});

// 获取经过验证的跨会话消息（例如 `Main ⇄ Pandas`）
const crossSessionMessages = await tracer.getCrossSessionMessages();
crossSessionMessages.forEach(msg => {
  console.log(`${msg.fromAgent} ⇄ ${msg.toAgent}: ${msg.messageType}`);
  // messageType: 'sessions_send' | 'inter-session message'
});
```

### 获取令牌使用和消耗

```typescript
import { UsageConnector } from './src/runtime/connectors/usage';

const usage = new UsageConnector({ gatewayUrl: process.env.OPENCLAW_GATEWAY_URL });

// 今日使用情况
const today = await usage.getUsageSummary('today');
console.log(`使用令牌: ${today.tokensUsed}`);
console.log(`成本: $${today.costUsd.toFixed(4)}`);
console.log(`上下文压力: ${today.contextPressure}`);
// contextPressure: 'low' | 'medium' | 'high' | 'critical'

// 7天使用趋势
const trend = await usage.getUsageTrend(7);
trend.forEach(day => {
  console.log(`${day.date}: ${day.tokensUsed} 令牌, $${day.costUsd.toFixed(4)}`);
});

// 按任务分配令牌（谁消耗了计划任务的令牌）
const attribution = await usage.getTokenAttribution();
attribution.tasks.forEach(task => {
  console.log(`${task.title}: ${task.tokensUsed} (${task.percentOfTotal}%)`);
});
```

### 读取内存状态

```typescript
import { MemoryConnector } from './src/runtime/connectors/memory';

const memory = new MemoryConnector({
  openclawHome: process.env.OPENCLAW_HOME ?? '~/.openclaw',
});

// 获取每个活跃代理的内存健康（限定于 openclaw.json）
const memoryState = await memory.getMemoryState();
memoryState.agents.forEach(agent => {
  console.log(`${agent.name}:`);
  console.log(`  可用: ${agent.memoryAvailable}`);
  console.log(`  可搜索: ${agent.memorySearchable}`);
  console.log(`  需要审核: ${agent.needsReview}`);
});

// 读取代理的每日内存
const dailyMemory = await memory.readDailyMemory('main-agent');
console.log(dailyMemory.content);

// 编辑内存（需要 `READONLY_MODE=false` 和有效的本地令牌）
await memory.writeDailyMemory('main-agent', updatedContent, { token: localToken });
```

### 检查接线状态

```typescript
import { WiringChecker } from './src/runtime/connectors/wiring';

const wiring = new WiringChecker({ gatewayUrl: process.env.OPENCLAW_GATEWAY_URL });

const status = await wiring.getWiringStatus();
status.connectors.forEach(connector => {
  console.log(`${connector.name}: ${connector.status}`);
  // status: 'connected' | 'partial' | 'disconnected'
  if (connector.status !== 'connected') {
    console.log(`修复: ${connector.nextStep}`);
  }
});
```

### 审批任务（受保护端点）

```typescript
import { TaskConnector } from './src/runtime/connectors/tasks';

const tasks = new TaskConnector({
  gatewayUrl: process.env.OPENCLAW_GATEWAY_URL,
  approvalActionsEnabled: process.env.APPROVAL_ACTIONS_ENABLED === 'true',
  approvalActionsDryRun: process.env.APPROVAL_ACTIONS_DRY_RUN !== 'false',
});

// 如果 `APPROVAL_ACTIONS_ENABLED=false`（默认），这将抛出错误
try {
  const result = await tasks.approveTask('task-id-123', { token: localToken });
  if (result.dryRun) {
    console.log('干运行 — 无实际状态变更');
  }
} catch (err) {
  if (err.code === 'APPROVAL_ACTIONS_DISABLED') {
    console.log('设置 `APPROVAL_ACTIONS_ENABLED=true` 以启用审批');
  }
}
```

## UI 章节导航

通过查询参数导航：

```
http://127.0.0.1:4310/?section=overview&lang=zh
http://127.0.0.1:4310/?section=usage&lang=en
http://127.0.0.1:4310/?section=staff&lang=zh
http://127.0.0.1:4310/?section=collaboration&lang=en
http://127.0.0.1:4310/?section=tasks&lang=zh
http://127.0.0.1:4310/?section=memory&lang=en
http://127.0.0.1:4310/?section=documents&lang=zh
http://127.0.0.1:4310/?section=settings&lang=en
```

章节：`overview` | `usage` | `staff` | `collaboration` | `tasks` | `memory` | `documents` | `settings`

语言：`zh`（中文，默认）| `en`（英文）

## 集成模式

### 在现有 OpenClaw 工作流中嵌入

如果您的 OpenClaw 代理需要将指令交接给控制中心进行设置，请使用文档中记录的安装块：

```typescript
// 在您的 OpenClaw 代理任务中
const installInstructions = `
cd openclaw-control-center
npm install
cp .env.example .env
# 编辑 .env: 设置 OPENCLAW_GATEWAY_URL 和 OPENCLAW_HOME
npm run build && npm test && npm run dev:ui
`;
```

### 添加自定义连接器

所有连接器都位于 `control-center/src/runtime/connectors/`。遵循此模式：

```typescript
// control-center/src/runtime/connectors/my-connector.ts
import { BaseConnector, ConnectorOptions } from './base';

export interface MyData {
  id: string;
  value: string;
}

export class MyConnector extends BaseConnector {
  constructor(options: ConnectorOptions) {
    super(options);
  }

  async getData(): Promise<MyData[]> {
    // 始终检查只读模式，任何写入操作
    this.assertNotReadonly('getData 是只读安全的');

    const response = await this.fetch('/api/my-endpoint');
    return response.json() as Promise<MyData[]>;
  }
}
```

### 自定义 UI 章节

```typescript
// control-center/src/ui/sections/MySection.tsx
import React from 'react';
import { useConnector } from '../hooks/useConnector';
import { MyConnector } from '../../runtime/connectors/my-connector';

export const MySection: React.FC = () => {
  const { data, loading, error } = useConnector(MyConnector, 'getData');

  if (loading) return <div>加载中...</div>;
  if (error) return <div>错误: {error.message}</div>;

  return (
    <ul>
      {data?.map(item => (
        <li key={item.id}>{item.value}</li>
      ))}
    </ul>
  );
};
```

## 故障排除

### "缺少 src/runtime" 或 "缺少核心源"

这几乎总是意味着工作目录不正确：

```bash
# 确保您在仓库根目录
pwd  # 应该以 /openclaw-control-center 结尾
ls control-center/src/runtime  # 应该存在
```

如果克隆正确但仍然缺少：克隆不完整。重新克隆：

```bash
git clone https://github.com/TianyiDataScience/openclaw-control-center.git
```

### UI 无法启动 / 端口冲突

```bash
# 检查端口 4310 是否被占用
lsof -i :4310
# 或者在 Windows 上
netstat -ano | findstr :4310

# 更改 .env 中的端口
PORT=4311
```

### 数据未显示（部分或为空章节）

1. 打开 `设置` → **接线状态** — 它列出了哪些连接器已连接、部分连接或缺失。
2. 常见原因：
   - `OPENCLAW_GATEWAY_URL` 未设置或端口错误
   - `OPENCLAW_HOME` 指向实际的 `~/.openclaw`
   - OpenClaw 订阅快照不在默认路径

### 令牌认证失败

```bash
# 生成本地令牌（参见 openclaw 文档获取令牌位置）
cat ~/.openclaw/local-token

# 在 API 调用中通过头部传递
curl -H "X-Local-Token: <token>" http://127.0.0.1:4310/api/tasks/approve
```

### 审批操作静默无效果

检查您的 `.env`：

```env
APPROVAL_ACTIONS_ENABLED=true   # 必须为 true
APPROVAL_ACTIONS_DRY_RUN=false  # 必须为 false 以进行实际执行
```

两者都必须明确设置。默认情况下是禁用 + 干运行。

### 内存章节显示非活跃代理

内存章节限定于 `openclaw.json` 中列出的代理。如果已删除的代理仍然出现：

```bash
# 检查活跃代理
cat ~/.openclaw/openclaw.json | grep -A5 '"agents"'
```

从 `openclaw.json` 中删除过时的条目 — 内存章节将在下次加载时更新。

### Windows 命令行问题

优先使用 `npm run dev:ui` 而不是 `UI_MODE=true npm run dev`。跨环境变量设置在 PowerShell/CMD 中表现不同。`dev:ui` 脚本内部处理此问题。

## 前置条件

- Node.js + npm
- 正在运行的 OpenClaw 安装，可访问网关
- 本地机器上对 `~/.openclaw` 的读取权限
- （可选）`~/.codex` 和 OpenClaw 订阅快照以获取完整使用数据
