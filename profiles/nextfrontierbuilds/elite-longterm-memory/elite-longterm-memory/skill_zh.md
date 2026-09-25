# 精英长期记忆 🧠

**AI 代理的终极记忆系统。** 结合了 6 种经过验证的方法，形成了一个坚不可摧的架构。

永不断言上下文。永不忘记决策。永不重复错误。

## 架构概述

```
┌─────────────────────────────────────────────────────────────────┐
│                    精英长期记忆                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   热内存   │  │  温存储   │  │  冷存储   │             │
│  │             │  │             │  │             │             │
│  │ SESSION-    │  │  LanceDB    │  │  Git-Notes  │             │
│  │ STATE.md    │  │  向量    │  │  知识  │             │
│  │             │  │             │  │  图形      │             │
│  │ (在压缩中   │  │ (语义    │  │ (永久  │             │
│  │  存活)    │  │  搜索)    │  │  决策) │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│         │                │                │                     │
│         └────────────────┼────────────────┘                     │
│                          ▼                                      │
│                  ┌─────────────┐                                │
│                  │  MEMORY.md  │  ← 精心策划的长期           │
│                  │  + 每天/   │    (人类可读)            │
│                  └─────────────┘                                │
│                          │                                      │
│                          ▼                                      │
│                  ┌─────────────┐                                │
│                  │ SuperMemory │  ← 云备份 (可选)     │
│                  │    API      │                                │
│                  └─────────────┘                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 5 个记忆层

### 第 1 层：热内存 (SESSION-STATE.md)
**来源：bulletproof-memory**

在压缩中存活的主动工作内存。预写日志协议。

```markdown
# SESSION-STATE.md — 主动工作内存

## 当前任务
[我们正在处理的当前情况]

## 关键上下文
- 用户偏好：...
- 已做决策：...
- 阻塞点：...

## 待办事项
- [ ] ...
```

**规则：** 在响应之前写入。由用户输入触发，而不是代理内存。

### 第 2 层：温存储 (LanceDB 向量)
**来源：lancedb-memory**

跨所有记忆的语义搜索。自动召回注入相关上下文。

```bash
# 自动召回 (自动发生)
memory_recall query="项目状态" limit=5

# 手动存储
memory_store text="用户更喜欢暗黑模式" category="偏好" importance=0.9
```

### 第 3 层：冷存储 (Git-Notes 知识图)
**来源：git-notes-memory**

结构化的决策、学习上下文。分支感知。

```bash
# 存储一个决策 (静默 - 从不宣布)
python3 memory.py -p $DIR remember '{"type":"决策","content":"使用 React 进行前端开发"}' -t 技术 -i h

# 获取上下文
python3 memory.py -p $DIR get "前端"
```

### 第 4 层：精心策划的存档 (MEMORY.md + 每天/)
**来源：Clawdbot 原生**

人类可读的长期记忆。每日日志 + 提炼的智慧。

```
workspace/
├── MEMORY.md              # 精心策划的长期 (好东西)
└── memory/
    ├── 2026-01-30.md      # 每日日志
    ├── 2026-01-29.md
    └── topics/            # 主题特定文件
```

### 第 5 层：云备份 (SuperMemory) — 可选
**来源：supermemory**

跨设备同步。与你的知识库聊天。

```bash
export SUPERMEMORY_API_KEY="你的密钥"
# 添加到 ~/.zshrc 以持久化
```

### 第 6 层：自动提取 (Mem0) — 推荐
**新增：自动事实提取**

Mem0 自动从对话中提取事实。80% 的 token 减少。

```bash
npm install mem0ai
export MEM0_API_KEY="你的密钥"
```

```javascript
const { MemoryClient } = require('mem0ai');
const client = new MemoryClient({ apiKey: process.env.MEM0_API_KEY });

// 对话自动提取事实
await client.add([
  { role: "user", content: "我更喜欢 Tailwind 而不是原始 CSS" }
], { user_id: "ty" });

// 获取相关记忆
const memories = await client.search("CSS 偏好", { user_id: "ty" });
```

优点：
- 自动提取偏好、决策、事实
- 去重并更新现有记忆
- 与原始历史相比减少 80% 的 token
- 自动跨会话工作

## 快速设置

### 1. 创建 SESSION-STATE.md (热内存)

```bash
cat > SESSION-STATE.md << 'EOF'
# SESSION-STATE.md — 主动工作内存

此文件是代理的“内存” — 在压缩中存活，重启、分心时也能恢复。

## 当前任务
[无]

## 关键上下文
[无]

## 待办事项
- [ ] 无

## 最近决策
[无]

---
*最后更新：[时间戳]*
EOF
```

### 2. 启用 LanceDB (温存储)

在 `~/.clawdbot/clawdbot.json` 中：

```json
{
  "memorySearch": {
    "enabled": true,
    "provider": "openai",
    "sources": ["memory"],
    "minScore": 0.3,
    "maxResults": 10
  },
  "plugins": {
    "entries": {
      "memory-lancedb": {
        "enabled": true,
        "config": {
          "autoCapture": false,
          "autoRecall": true,
          "captureCategories": ["偏好", "决策", "事实"],
          "minImportance": 0.7
        }
      }
    }
  }
}
```

### 3. 初始化 Git-Notes (冷存储)

```bash
cd ~/clawd
git init  # 如果尚未初始化
python3 skills/git-notes-memory/memory.py -p . sync --start
```

### 4. 验证 MEMORY.md 结构

```bash
# 确保有：
# - workspace 根目录中的 MEMORY.md
# - 用于每日日志的 memory/ 文件夹
mkdir -p memory
```

### 5. (可选) 设置 SuperMemory

```bash
export SUPERMEMORY_API_KEY="你的密钥"
# 添加到 ~/.zshrc 以持久化
```

## 代理指令

### 会话开始时
1. 读取 SESSION-STATE.md — 这是你的热上下文
2. 运行 `memory_search` 以获取相关先前的上下文
3. 检查 memory/YYYY-MM-DD.md 以获取最近的活动

### 对话期间
1. **用户提供了具体细节？** → 在响应之前写入到 SESSION-STATE.md
2. **做出了重要决策？** → 静默存储到 Git-Notes
3. **表达了偏好？** → `memory_store` with importance=0.9

### 会话结束时
1. 更新 SESSION-STATE.md 以获取最终状态
2. 如果值得长期保留，将重要项目移动到 MEMORY.md
3. 在 memory/YYYY-MM-DD.md 中创建/更新每日日志

### 记忆卫生 (每周)
1. 审查 SESSION-STATE.md — 存档完成的任务
2. 检查 LanceDB 中的垃圾：`memory_recall query="*" limit=50`
3. 清理无关向量：`memory_forget id=<id>`
4. 将每日日志合并到 MEMORY.md

## WAL 协议 (关键)

**预写日志：** 在响应之前写入状态，而不是在响应之后。

| 触发器 | 操作 |
|-------|------|
| 用户声明偏好 | 写入 SESSION-STATE.md → 然后响应 |
| 用户做出决策 | 写入 SESSION-STATE.md → 然后响应 |
| 用户给出截止日期 | 写入 SESSION-STATE.md → 然后响应 |
| 用户纠正你 | 写入 SESSION-STATE.md → 然后响应 |

**为什么？** 如果你先响应然后崩溃/压缩之前没有保存，上下文就会丢失。WAL 确保持久性。

## 示例工作流程

```
用户： "让我们使用 Tailwind 来做这个项目，而不是原始 CSS"

代理 (内部)：
1. 写入到 SESSION-STATE.md: "决策：使用 Tailwind，而不是原始 CSS"
2. 存储到 Git-Notes：关于 CSS 框架的决策
3. memory_store: "用户更喜欢 Tailwind 而不是原始 CSS" importance=0.9
4. 然后响应： "好的 — 使用 Tailwind..."
```

## 维护命令

```bash
# 审计向量内存
memory_recall query="*" limit=50

# 清除所有向量 (核选项)
rm -rf ~/.clawdbot/memory/lancedb/
clawdbot gateway restart

# 导出 Git-Notes
python3 memory.py -p . export --format json > memories.json

# 检查记忆健康
du -sh ~/.clawdbot/memory/
wc -l MEMORY.md
ls -la memory/
```

## 为什么记忆会失败

理解根本原因有助于你修复它们：

| 失败模式 | 原因 | 修复 |
|----------|------|------|
| 什么都没记住 | `memory_search` 被禁用 | 启用 + 添加 OpenAI 密钥 |
| 文件未加载 | 代理跳过读取记忆 | 添加到 AGENTS.md 规则 |
| 事实未捕获 | 没有自动提取 | 使用 Mem0 或手动记录 |
| 子代理隔离 | 没有继承上下文 | 在任务提示中传递上下文 |
| 重复错误 | 经验教训未记录 | 写入 memory/lessons.md |

## 解决方案 (按努力程度排序)

### 1. 快速胜利：启用 memory_search

如果你有 OpenAI 密钥，启用语义搜索：

```bash
clawdbot configure --section web
```

这将启用对 MEMORY.md + memory/*.md 文件的向量搜索。

### 2. 推荐：Mem0 集成

自动从对话中提取事实。减少 80% 的 token。

```bash
npm install mem0ai
```

```javascript
const { MemoryClient } = require('mem0ai');

const client = new MemoryClient({ apiKey: process.env.MEM0_API_KEY });

// 自动提取并存储
await client.add([
  { role: "user", content: "我更喜欢 Tailwind 而不是原始 CSS" }
], { user_id: "ty" });

// 获取相关记忆
const memories = await client.search("CSS 偏好", { user_id: "ty" });
```

### 3. 更好的文件结构 (无依赖)

```
memory/
├── projects/
│   ├── strykr.md
│   └── taska.md
├── people/
│   └── contacts.md
├── decisions/
│   └── 2026-01.md
├── lessons/
│   └── mistakes.md
└── preferences.md
```

保持 MEMORY.md 作为摘要 (<5KB)，链接到详细文件。

## 立即修复清单

| 问题 | 修复 |
|------|------|
| 忘记偏好 | 在 MEMORY.md 中添加 `## 偏好` 部分 |
| 重复错误 | 每个错误记录到 `memory/lessons.md` |
| 子代理缺乏上下文 | 在生成任务提示中包含关键上下文 |
| 忘记最近的工作 | 严格的每日文件纪律 |
| 记忆搜索不工作 | 检查 `OPENAI_API_KEY` 是否已设置 |

## 故障排除

**代理在对话中不断忘记：**
→ SESSION-STATE.md 没有被更新。检查 WAL 协议。

**注入了无关的记忆：**
→ 禁用 autoCapture，增加 minImportance 阈值。

**记忆太大，召回慢：**
→ 运行卫生：清除旧向量，存档每日日志。

**Git-Notes 未持久化：**
→ 运行 `git notes push` 以同步到远程。

**memory_search 返回空：**
→ 检查 OpenAI API 密钥：`echo $OPENAI_API_KEY`
→ 验证 clawdbot.json 中的 memorySearch 是否启用

---

## 链接

- bulletproof-memory: https://clawdhub.com/skills/bulletproof-memory
- lancedb-memory: https://clawdhub.com/skills/lancedb-memory
- git-notes-memory: https://clawdhub.com/skills/git-notes-memory
- memory-hygiene: https://clawdhub.com/skills/memory-hygiene
- supermemory: https://clawdhub.com/skills/supermemory

---

*由 [@NextXFrontier](https://x.com/NextXFrontier) 构建 — Next Frontier AI 工具包的一部分*
