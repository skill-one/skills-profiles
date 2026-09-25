# OpenMAIC — 多智能体交互课堂

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能集合。

OpenMAIC（Open Multi-Agent Interactive Classroom，开放多智能体交互课堂）是一个基于Next.js 16 / React 19 / TypeScript的平台，能够将任何主题或文档转化为完整的交互式课程。一个多智能体管道（LangGraph 1.1）生成幻灯片、测验、HTML模拟和基于项目的学习活动，由具有语音（TTS）和电子白板支持的AI教师和AI同学进行交付。

---

## 项目技术栈

| 层级 | 技术 |
|---|---|
| 框架 | Next.js 16 (App Router) |
| UI | React 19, Tailwind CSS 4 |
| 智能体编排 | LangGraph 1.1 |
| 语言 | TypeScript 5 |
| 包管理器 | pnpm >= 10 |
| 运行时 | Node.js >= 20 |

---

## 安装

```bash
git clone https://github.com/THU-MAIC/OpenMAIC.git
cd OpenMAIC
pnpm install
```

### 环境配置

```bash
cp .env.example .env.local
```

编辑 `.env.local` — 至少需要一个LLM提供者密钥：

```env
# LLM 提供者（至少配置一个）
OPENAI_API_KEY=$OPENAI_API_KEY
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
GOOGLE_API_KEY=$GOOGLE_API_KEY

# 推荐默认模型（Gemini 3 Flash = 最佳速度/质量平衡）
DEFAULT_MODEL=google:gemini-3-flash-preview

# 可选：MinerU用于高级PDF/表格/公式解析
PDF_MINERU_BASE_URL=https://mineru.net
PDF_MINERU_API_KEY=$MINERU_API_KEY

# 可选：托管模式访问码
ACCESS_CODE=$OPENMAIC_ACCESS_CODE
```

### 通过YAML配置提供者（环境变量的替代方案）

在项目根目录创建 `server-providers.yml`：

```yaml
providers:
  openai:
    apiKey: $OPENAI_API_KEY
  anthropic:
    apiKey: $ANTHROPIC_API_KEY
  google:
    apiKey: $GOOGLE_API_KEY
  deepseek:
    apiKey: $DEEPSEEK_API_KEY
  # 任何兼容OpenAI的端点
  custom:
    baseURL: https://your-proxy.example.com/v1
    apiKey: $CUSTOM_API_KEY
```

---

## 运行应用

```bash
# 开发模式
pnpm dev
# → http://localhost:3000

# 生产构建
pnpm build && pnpm start

# 类型检查
pnpm tsc --noEmit

# 代码检查
pnpm lint
```

---

## Docker部署

```bash
cp .env.example .env.local
# 编辑 .env.local 使用你的API密钥

docker compose up --build
# → http://localhost:3000
```

---

## Vercel部署

```bash
# Fork仓库，然后在新窗口导入 https://vercel.com/new
# 在Vercel控制台设置环境变量：
#   OPENAI_API_KEY 或 ANTHROPIC_API_KEY 或 GOOGLE_API_KEY
#   DEFAULT_MODEL (可选，例如 google:gemini-3-flash-preview)
```

README中提供了一键部署按钮，它会自动预填环境变量描述。

---

## 课程生成管道

OpenMAIC使用两阶段管道：

| 阶段 | 描述 |
|---|---|
| **大纲** | AI分析主题/文档并生成结构化的课程大纲 |
| **场景** | 每个大纲项被扩展为类型化的场景：`slides`、`quiz`、`interactive` 或 `pbl` |

### 场景类型

| 类型 | 描述 |
|---|---|
| `slides` | AI教师使用TTS旁白进行讲座，聚光灯，激光笔 |
| `quiz` | 单选/多选或简答题，AI自动评分 |
| `interactive` | 基于HTML的模拟（物理，流程图等） |
| `pbl` | 基于项目的学习 — 选择角色，与智能体协作 |

---

## API使用 — 生成课堂

### REST：启动生成任务

```typescript
// POST /api/generate
const response = await fetch('/api/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    topic: '量子纠缠',
    // 可选：附加文档内容
    document: markdownString,
    // 可选：模型覆盖
    model: 'google:gemini-3-flash-preview',
  }),
});

const { jobId } = await response.json();
```

### REST：轮询任务状态

```typescript
// GET /api/generate/status?jobId=<jobId>
const poll = async (jobId: string) => {
  while (true) {
    const res = await fetch(`/api/generate/status?jobId=${jobId}`);
    const data = await res.json();

    if (data.status === 'completed') {
      console.log('课堂URL:', data.classroomUrl);
      break;
    }
    if (data.status === 'failed') {
      throw new Error(data.error);
    }
    // status === 'pending' | 'running'
    await new Promise(r => setTimeout(r, 3000));
  }
};
```

### REST：导出幻灯片

```typescript
// GET /api/export/pptx?classroomId=<id>
const exportPptx = async (classroomId: string) => {
  const res = await fetch(`/api/export/pptx?classroomId=${classroomId}`);
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  // 触发下载
  const a = document.createElement('a');
  a.href = url;
  a.download = 'lesson.pptx';
  a.click();
};

// GET /api/export/html?classroomId=<id>
const exportHtml = async (classroomId: string) => {
  const res = await fetch(`/api/export/html?classroomId=${classroomId}`);
  const html = await res.text();
  return html;
};
```

---

## OpenClaw集成

OpenMAIC提供针对[OpenClaw](https://github.com/openclaw/openclaw)的技能，支持从飞书、Slack、Discord、Telegram等平台生成课堂。

### 安装技能

```bash
# 通过ClawHub（推荐）
clawhub install openmaic

# 手动安装
mkdir -p ~/.openclaw/skills
cp -R /path/to/OpenMAIC/skills/openmaic ~/.openclaw/skills/openmaic
```

### 配置OpenClaw

编辑 `~/.openclaw/openclaw.json`：

```jsonc
{
  "skills": {
    "entries": {
      "openmaic": {
        "config": {
          // 托管模式 — 从 https://open.maic.chat/ 获取访问码
          "accessCode": "$OPENMAIC_ACCESS_CODE",

          // 自托管模式 — 本地仓库 + 服务器URL
          "repoDir": "/path/to/OpenMAIC",
          "url": "http://localhost:3000"
        }
      }
    }
  }
}
```

### OpenClaw技能生命周期

| 阶段 | 发生什么 |
|---|---|
| 克隆 | 检测现有检出或克隆新仓库 |
| 启动 | 选择 `pnpm dev`、`pnpm build && pnpm start` 或 Docker |
| 提供者密钥 | 指导用户编辑 `.env.local` |
| 生成 | 提交异步任务，轮询，返回课堂链接 |

---

## 自定义场景开发模式

场景是类型化的React组件。要添加新的场景类型：

```typescript
// types/scene.ts
export type SceneType = 'slides' | 'quiz' | 'interactive' | 'pbl' | 'custom';

export interface CustomScene {
  type: 'custom';
  title: string;
  content: string;
  // 你的字段
  metadata: Record<string, unknown>;
}
```

```typescript
// components/scenes/CustomScene.tsx
'use client';

import { type CustomScene } from '@/types/scene';

interface Props {
  scene: CustomScene;
  onComplete: () => void;
}

export function CustomSceneComponent({ scene, onComplete }: Props) {
  return (
    <div className="flex flex-col gap-4 p-6">
      <h2 className="text-2xl font-bold">{scene.title}</h2>
      <div dangerouslySetInnerHTML={{ __html: scene.content }} />
      <button
        className="mt-4 rounded-lg bg-blue-600 px-6 py-2 text-white"
        onClick={onComplete}
      >
        继续
      </button>
    </div>
  );
}
```

---

## 多智能体交互模式

| 模式 | 触发方式 | 描述 |
|---|---|---|
| 课堂讨论 | 自动 | 智能体主动发起讨论；用户可以加入或被点名 |
| 圆桌辩论 | 场景配置 | 多个智能体角色就某个主题进行辩论，并配有电子白板插图 |
| 问答 | 用户提问 | AI教师使用幻灯片、图表或电子白板绘图进行回答 |
| 电子白板 | 任何场景中 | 智能体实时绘制方程式、流程图或概念图 |

---

## MinerU高级文档解析

对于包含表格、公式或扫描图像的复杂PDF：

```env
# 使用MinerU托管API
PDF_MINERU_BASE_URL=https://mineru.net
PDF_MINERU_API_KEY=$MINERU_API_KEY

# 或自托管MinerU实例（Docker）
PDF_MINERU_BASE_URL=http://localhost:8888
```

没有MinerU时，OpenMAIC会回退到标准的PDF文本提取。

---

## 支持的LLM提供者及模型字符串

```typescript
// 模型字符串格式： "提供者:模型名称"
const models = {
  // Google（推荐）
  geminiFlash: 'google:gemini-3-flash-preview',   // 最佳速度/质量
  geminiPro: 'google:gemini-3.1-pro',             // 最高质量

  // OpenAI
  gpt4o: 'openai:gpt-4o',
  gpt4oMini: 'openai:gpt-4o-mini',

  // Anthropic
  claude4Sonnet: 'anthropic:claude-sonnet-4-5',
  claude4Haiku: 'anthropic:claude-haiku-4-5',

  // DeepSeek
  deepseekChat: 'deepseek:deepseek-chat',

  // 兼容OpenAI的（自定义基础URL）
  custom: 'custom:your-model-name',
};
```

---

## 导出格式

| 格式 | 端点 | 备注 |
|---|---|---|
| PowerPoint `.pptx` | `GET /api/export/pptx?classroomId=` | 可编辑的幻灯片 |
| 交互式 `.html` | `GET /api/export/html?classroomId=` | 自包含的HTML页面 |

---

## 常见模式

### 从文档字符串生成课堂

```typescript
const generateFromDocument = async (markdownContent: string, topic: string) => {
  const res = await fetch('/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      topic,
      document: markdownContent,
      model: process.env.DEFAULT_MODEL ?? 'google:gemini-3-flash-preview',
    }),
  });

  const { jobId } = await res.json();

  // 轮询直到完成
  let classroomUrl: string | null = null;
  while (!classroomUrl) {
    await new Promise(r => setTimeout(r, 4000));
    const status = await fetch(`/api/generate/status?jobId=${jobId}`).then(r => r.json());
    if (status.status === 'completed') classroomUrl = status.classroomUrl;
    if (status.status === 'failed') throw new Error(status.error);
  }

  return classroomUrl;
};
```

### 检查提供者健康状态

```typescript
// GET /api/providers
const checkProviders = async () => {
  const res = await fetch('/api/providers');
  const { providers } = await res.json();
  // providers: Array<{ name: string; available: boolean; models: string[] }>
  return providers.filter((p: { available: boolean }) => p.available);
};
```

---

## 故障排除

| 问题 | 解决方案 |
|---|---|
| `没有配置LLM提供者` | 在 `.env.local` 中设置至少一个 `OPENAI_API_KEY`、`ANTHROPIC_API_KEY` 或 `GOOGLE_API_KEY` |
| 生成在大纲阶段卡住 | 检查API密钥配额；尝试切换到 `google:gemini-3-flash-preview` 获取更高的速率限制 |
| TTS不工作 | TTS需要支持Web Speech API的浏览器；检查浏览器控制台错误信息 |
| PDF解析产生乱码文本 | 启用MinerU，在 `.env.local` 中设置 `PDF_MINERU_BASE_URL` |
| Vercel生成过程中超时 | 增加 `vercel.json` 中的函数超时时间；生成是异步的，API应立即返回 `jobId` |
| Docker构建失败 | 确保 `DOCKER_BUILDKIT=1` 且在运行 `docker compose up --build` 前存在 `.env.local` |
| OpenClaw技能未找到 | 运行 `clawhub install openmaic` 或手动将 `skills/openmaic` 复制到 `~/.openclaw/skills/` |
| `pnpm install` 在Node < 20时失败 | 升级Node.js至 >= 20 (`nvm use 20`) |
| 端口3000已被占用 | 在 `.env.local` 中设置 `PORT=3001` 或运行 `PORT=3001 pnpm dev` |

---

## 关键文件结构

```
OpenMAIC/
├── app/                    # Next.js App Router页面及API路由
│   ├── api/
│   │   ├── generate/       # POST生成课堂，GET状态
│   │   ├── export/         # pptx / html导出端点
│   │   └── providers/      # LLM提供者健康检查
│   └── classroom/          # 课堂查看页面
├── components/
│   ├── scenes/             # 幻灯片、测验、交互、PBL组件
│   ├── whiteboard/         # 实时电子白板渲染
│   └── agents/             # 智能体头像及TTS组件
├── lib/
│   ├── agents/             # LangGraph智能体图定义
│   ├── providers/          # LLM提供者抽象
│   └── generation/         # 大纲+场景生成管道
├── skills/
│   └── openmaic/           # OpenClaw技能定义
├── server-providers.yml    # 可选的YAML提供者配置
├── .env.example            # 环境变量模板
└── docker-compose.yml      # Docker部署配置
```
