# memory-lancedb-pro OpenClaw 插件

> 技能由 [ara.so](https://ara.so) 提供 — 每日 2026 技能集合。

`memory-lancedb-pro` 是 [OpenClaw](https://github.com/openclaw/openclaw) 代理的一个生产级长期记忆插件。它将偏好设置、决策和项目上下文存储在本地 [LanceDB](https://lancedb.com) 向量数据库中，并在每个代理回复之前自动回忆相关的记忆。主要功能：混合检索（向量 + BM25 全文）、跨编码器重新排序、由 LLM 驱动的智能提取（6 个类别）、基于 Weibull 衰减的遗忘、多范围隔离（代理/用户/项目）以及完整的 CLI 管理工具。

---

## 安装

### 选项 A：一键设置脚本（推荐）

```bash
curl -fsSL https://raw.githubusercontent.com/CortexReach/toolbox/main/memory-lancedb-pro-setup/setup-memory.sh -o setup-memory.sh
bash setup-memory.sh
```

标志：

```bash
bash setup-memory.sh --dry-run       # 仅预览更改
bash setup-memory.sh --beta          # 包含预发布版本
bash setup-memory.sh --uninstall     # 恢复配置并移除插件
bash setup-memory.sh --selfcheck-only  # 健康检查，无更改
```

该脚本处理全新安装、从 git 克隆版本升级、无效配置字段、CLI 回退以及提供者预设（Jina、DashScope、SiliconFlow、OpenAI、Ollama）。

### 选项 B：OpenClaw CLI

```bash
openclaw plugins install memory-lancedb-pro@beta
```

### 选项 C：npm

```bash
npm i memory-lancedb-pro@beta
```

> **关键提示：** 通过 npm 安装时，您必须将插件的 **绝对** 安装路径添加到 `plugins.load.paths` 中 `openclaw.json`。这是最常见的设置问题。

---

## 最小配置 (`openclaw.json`)

```json
{
  "plugins": {
    "load": {
      "paths": ["/绝对路径/to/node_modules/memory-lancedb-pro"]
    },
    "slots": { "memory": "memory-lancedb-pro" },
    "entries": {
      "memory-lancedb-pro": {
        "enabled": true,
        "config": {
          "embedding": {
            "provider": "openai-compatible",
            "apiKey": "${OPENAI_API_KEY}",
            "model": "text-embedding-3-small"
          },
          "autoCapture": true,
          "autoRecall": true,
          "smartExtraction": true,
          "extractMinMessages": 2,
          "extractMaxChars": 8000,
          "sessionMemory": { "enabled": false }
        }
      }
    }
  }
}
```

**为什么这些默认值：**
- `autoCapture` + `smartExtraction` → 代理自动从对话中学习，无需手动调用
- `autoRecall` → 在每个回复之前注入记忆
- `extractMinMessages: 2` → 在正常两轮对话中触发
- `sessionMemory.enabled: false` → 避免在早期阶段用会话摘要污染检索

---

## 完整生产配置

```json
{
  "plugins": {
    "slots": { "memory": "memory-lancedb-pro" },
    "entries": {
      "memory-lancedb-pro": {
        "enabled": true,
        "config": {
          "embedding": {
            "provider": "openai-compatible",
            "apiKey": "${OPENAI_API_KEY}",
            "model": "text-embedding-3-small",
            "baseURL": "https://api.openai.com/v1"
          },
          "reranker": {
            "provider": "jina",
            "apiKey": "${JINA_API_KEY}",
            "model": "jina-reranker-v2-base-multilingual"
          },
          "extraction": {
            "provider": "openai-compatible",
            "apiKey": "${OPENAI_API_KEY}",
            "model": "gpt-4o-mini"
          },
          "autoCapture": true,
          "captureAssistant": false,
          "autoRecall": true,
          "smartExtraction": true,
          "extractMinMessages": 2,
          "extractMaxChars": 8000,
          "enableManagementTools": true,
          "retrieval": {
            "mode": "hybrid",
            "vectorWeight": 0.7,
            "bm25Weight": 0.3,
            "topK": 10
          },
          "rerank": {
            "enabled": true,
            "type": "cross-encoder",
            "candidatePoolSize": 12,
            "minScore": 0.6,
            "hardMinScore": 0.62
          },
          "decay": {
            "enabled": true,
            "model": "weibull",
            "halfLifeDays": 30
          },
          "sessionMemory": { "enabled": false },
          "scopes": {
            "agent": true,
            "user": true,
            "project": true
          }
        }
      }
    }
  }
}
```

### 嵌入提供者选项

| 提供者 | `provider` 值 | 备注 |
|---|---|---|
| OpenAI / 兼容 | `"openai-compatible"` | 需要 `apiKey`，可选 `baseURL` |
| Jina | `"jina"` | 需要 `apiKey` |
| Gemini | `"gemini"` | 需要 `apiKey` |
| Ollama | `"ollama"` | 本地，零 API 成本，设置 `baseURL` |
| DashScope | `"dashscope"` | 需要 `apiKey` |
| SiliconFlow | `"siliconflow"` | 需要 `apiKey`，免费重新排序层级 |

### 部署计划

**全功能（Jina + OpenAI）：**

```json
{
  "embedding": { "provider": "jina", "apiKey": "${JINA_API_KEY}", "model": "jina-embeddings-v3" },
  "reranker": { "provider": "jina", "apiKey": "${JINA_API_KEY}", "model": "jina-reranker-v2-base-multilingual" },
  "extraction": { "provider": "openai-compatible", "apiKey": "${OPENAI_API_KEY}", "model": "gpt-4o-mini" }
}
```

**预算（SiliconFlow 免费重新排序层级）：**

```json
{
  "embedding": { "provider": "openai-compatible", "apiKey": "${OPENAI_API_KEY}", "model": "text-embedding-3-small" },
  "reranker": { "provider": "siliconflow", "apiKey": "${SILICONFLOW_API_KEY}", "model": "BAAI/bge-reranker-v2-m3" },
  "extraction": { "provider": "openai-compatible", "apiKey": "${OPENAI_API_KEY}", "model": "gpt-4o-mini" }
}
```

**完全本地（Ollama，零 API 成本）：**

```json
{
  "embedding": { "provider": "ollama", "baseURL": "http://localhost:11434", "model": "nomic-embed-text" },
  "extraction": { "provider": "ollama", "baseURL": "http://localhost:11434", "model": "llama3" }
}
```

---

## CLI 参考

验证配置并在任何更改后重启：

```bash
openclaw config validate
openclaw gateway restart
openclaw logs --follow --plain | grep "memory-lancedb-pro"
```

预期的启动日志输出：

```
memory-lancedb-pro: 智能提取已启用
memory-lancedb-pro@1.x.x: 插件已注册
```

### 记忆管理 CLI

```bash
# 统计概览
openclaw memory-pro stats

# 列出记忆（可选范围/过滤）
openclaw memory-pro list
openclaw memory-pro list --scope user --limit 20
openclaw memory-pro list --filter "typescript"

# 搜索记忆
openclaw memory-pro search "编码偏好"
openclaw memory-pro search "数据库决策" --scope project

# 通过 ID 删除记忆
openclaw memory-pro forget <memory-id>

# 导出记忆（用于备份或迁移）
openclaw memory-pro export --scope global --output memories-backup.json
openclaw memory-pro export --scope user --output user-memories.json

# 导入记忆
openclaw memory-pro import --input memories-backup.json

# 升级模式（在升级插件版本时）
openclaw memory-pro upgrade --dry-run   # 预览首次
openclaw memory-pro upgrade             # 运行升级

# 插件信息
openclaw plugins info memory-lancedb-pro
```

---

## MCP 工具 API

该插件向代理暴露 MCP 工具。核心工具始终可用；管理工具需要 `enableManagementTools: true` 在配置中。

### 核心工具（始终可用）

#### `memory_recall`
检索与查询相关的记忆。

```typescript
// 代理使用模式
const results = await memory_recall({
  query: "用户的编码风格偏好",
  scope: "user",        // "agent" | "user" | "project" | "global"
  topK: 5
});
```

#### `memory_store`
手动存储记忆。

```typescript
await memory_store({
  content: "用户偏好制表符而非空格，始终需要错误处理",
  category: "preference",   // "profile" | "preference" | "entity" | "event" | "case" | "pattern"
  scope: "user",
  tags: ["编码风格", "typescript"]
});
```

#### `memory_forget`
通过 ID 删除特定记忆。

```typescript
await memory_forget({ id: "mem_abc123" });
```

#### `memory_update`
更新现有记忆。

```typescript
await memory_update({
  id: "mem_abc123",
  content: "用户现在偏好 2 空格缩进（2026-03-01 改自制表符）",
  category: "preference"
});
```

### 管理工具（需要 `enableManagementTools: true`）

#### `memory_stats`

```typescript
const stats = await memory_stats({ scope: "global" });
// 返回：总数、类别细分、衰减统计、数据库大小
```

#### `memory_list`

```typescript
const list = await memory_list({ scope: "user", limit: 20, offset: 0 });
```

#### `self_improvement_log`
记录代理学习事件以进行元改进跟踪。

```typescript
await self_improvement_log({
  event: "用户纠正了缩进偏好",
  context: "用户要求我切换从制表符到空格",
  improvement: "更新了编码风格偏好记忆"
});
```

#### `self_improvement_extract_skill`
从对话中提取可重用模式。

```typescript
await self_improvement_extract_skill({
  conversation: "...",
  domain: "代码审查",
  skillName: "typescript-strict-mode-setup"
});
```

#### `self_improvement_review`
审查并整合最近的自改进日志。

```typescript
await self_improvement_review({ days: 7 });
```

---

## 智能提取：6 个记忆类别

当 `smartExtraction: true` 时，LLM 自动将记忆分类到：

| 类别 | 存储的内容 | 示例 |
|---|---|---|
| `profile` | 用户身份、背景 | "用户是一名高级 TypeScript 开发者" |
| `preference` | 风格、工具、工作流选择 | "偏好函数式编程模式" |
| `entity` | 项目、人员、系统 | "项目 'Falcon' 使用 PostgreSQL + Redis" |
| `event` | 做出的决策、发生的事情 | "2026-02-15 选择 Vite 而非 webpack" |
| `case` | 特定问题的解决方案 | "通过在 vite.config.ts 中添加代理解决了 CORS 问题" |
| `pattern` | 重复行为、习惯 | "在实现前总是要求测试" |

---

## 混合检索内部机制

使用 `retrieval.mode: "hybrid"` 时，每次回忆都会运行：

1. **向量搜索** — 通过嵌入进行语义相似度（权重：`vectorWeight`，默认 0.7）
2. **BM25 全文搜索** — 关键字匹配（权重：`bm25Weight`，默认 0.3）
3. **分数融合** — 结果使用加权 RRF（Reciprocal Rank Fusion）合并
4. **跨编码器重新排序** — 重新排序前 `candidatePoolSize` 个候选
5. **分数过滤** — 低于 `hardMinScore` 的结果被丢弃

```json
"retrieval": {
  "mode": "hybrid",
  "vectorWeight": 0.7,
  "bm25Weight": 0.3,
  "topK": 10
},
"rerank": {
  "enabled": true,
  "type": "cross-encoder",
  "candidatePoolSize": 12,
  "minScore": 0.6,
  "hardMinScore": 0.62
}
```

检索模式选项：
- `"vector"` — 仅纯语义搜索
- `"bm25"` — 仅纯关键字搜索
- `"hybrid"` — 两者融合（推荐）

---

## 多范围隔离

范围允许您按上下文隔离记忆。启用所有三个范围可提供最大灵活性：

```json
"scopes": {
  "agent": true,    // 仅此代理实例特定的记忆
  "user": true,     // 与用户身份绑定的记忆
  "project": true   // 与项目/工作区绑定的记忆
}
```

回忆时指定范围以缩小结果：

```typescript
// 仅获取项目级记忆
await memory_recall({ query: "数据库选择", scope: "project" });

// 获取跨所有代理的用户偏好
await memory_recall({ query: "编码风格", scope: "user" });

// 跨所有范围的全球回忆
await memory_recall({ query: "错误处理模式", scope: "global" });
```

---

## Weibull 衰减模型

记忆会随时间自然衰减。衰减模型防止过时的记忆污染检索。

```json
"decay": {
  "enabled": true,
  "model": "weibull",
  "halfLifeDays": 30
}
```

- 频繁访问的记忆会重置其衰减时钟
- 重要、反复回忆的记忆实际上会变得永久
- 噪声和一次性提及会在约 30 天后自然衰减

---

## 升级

### 从 pre-v1.1.0

```bash
# 1. 首先备份 — 总是
openclaw memory-pro export --scope global --output memories-backup-$(date +%Y%m%d).json

# 2. 预览模式更改
openclaw memory-pro upgrade --dry-run

# 3. 运行升级
openclaw memory-pro upgrade

# 4. 验证
openclaw memory-pro stats
```

查看存储库中的 `CHANGELOG-v1.1.0.md` 以了解行为更改和升级理由。

---

## 故障排除

### 插件未加载

```bash
# 检查插件是否被识别
openclaw plugins info memory-lancedb-pro

# 验证配置（捕获 JSON 错误、未知字段）
openclaw config validate

# 检查注册日志
openclaw logs --follow --plain | grep "memory-lancedb-pro"
```

**常见原因：**
- 缺失或相对 `plugins.load.paths`（使用 npm install 时必须为绝对路径）
- `plugins.slots.memory` 未设置为 `"memory-lancedb-pro"`
- 插件未列在 `plugins.entries` 下

### `autoRecall` 未注入记忆

默认情况下，某些版本中的 `autoRecall` 为 `false` — 明确设置为 `true`：

```json
"autoRecall": true
```

还请确认插件绑定到 `memory` 插槽，而不仅仅是加载。

### 升级后 Jiti 缓存问题

```bash
# 清除 jiti 编译缓存
rm -rf ~/.openclaw/.cache/jiti
openclaw gateway restart
```

### 对话中未提取记忆

- 检查 `extractMinMessages` — 必须≥对话中的轮数（设置为 `2` 用于正常对话）
- 检查 `extractMaxChars` — 非常长的上下文可能会被截断；如有需要，增加至 `12000`
- 验证提取 LLM 配置具有有效的 `apiKey` 和可访问的端点
- 检查日志：`openclaw logs --follow --plain | grep "extraction"`

### 检索返回空或结果不佳

1. 确认 `retrieval.mode` 是 `"hybrid"` 而不是单独的 `"bm25"`（BM25 需要索引内容）
2. 暂时降低 `rerank.hardMinScore`（尝试 `0.4`）以查看是否存在但被过滤的结果
3. 检查嵌入模型在存储和回忆操作之间是否一致 — 更改模型需要重新嵌入

### 环境变量未解析

确保在运行 OpenClaw 的 shell 中导出环境变量，或使用进程管理器加载 `.env` 文件。`openclaw.json` 中的 `${VAR}` 语法在启动时解析。

```bash
export OPENAI_API_KEY="sk-..."
export JINA_API_KEY="jina_..."
openclaw gateway restart
```

---

## Telegram Bot 快速配置导入

如果使用 OpenClaw 的 Telegram 集成，向机器人发送以下内容以自动配置：

```
帮助我连接这个记忆插件与最用户友好的配置：
https://github.com/CortexReach/memory-lancedb-pro

要求：
1. 将其设置为唯一的活跃记忆插件
2. 使用 Jina 进行嵌入
3. 使用 Jina 进行重新排序
4. 使用 gpt-4o-mini 作为智能提取 LLM
5. 启用 autoCapture、autoRecall、smartExtraction
6. extractMinMessages=2
7. sessionMemory.enabled=false
8. captureAssistant=false
9. 检索模式=hybrid, vectorWeight=0.7, bm25Weight=0.3
10. rerank=cross-encoder, candidatePoolSize=12, minScore=0.6, hardMinScore=0.62
11. 直接生成 openclaw.json 配置，而不仅仅是解释
```

---

## 资源

- **GitHub:** https://github.com/CortexReach/memory-lancedb-pro
- **npm:** https://www.npmjs.com/package/memory-lancedb-pro
- **设置脚本:** https://github.com/CortexReach/toolbox/tree/main/memory-lancedb-pro-setup
- **代理技能:** https://github.com/CortexReach/memory-lancedb-pro-skill
- **视频演示（YouTube）:** https://youtu.be/MtukF1C8epQ
- **视频演示（Bilibili）:** https://www.bilibili.com/video/BV1zUf2BGEgn/
