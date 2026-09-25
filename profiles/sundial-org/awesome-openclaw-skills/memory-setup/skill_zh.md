# 记忆设置技能

将你的智能体从金鱼转变为大象。此技能有助于为 Moltbot/Clawdbot 配置持久记忆。

## 快速设置

### 1. 在配置中启用记忆搜索

在 `~/.clawdbot/clawdbot.json`（或 `moltbot.json`）中添加：

```json
{
  "memorySearch": {
    "enabled": true,
    "provider": "voyage",
    "sources": ["memory", "sessions"],
    "indexMode": "hot",
    "minScore": 0.3,
    "maxResults": 20
  }
}
```

### 2. 创建记忆结构

在你的工作区中创建：

```
workspace/
├── MEMORY.md              # 长期整理的记忆
└── memory/
    ├── logs/              # 每日日志 (YYYY-MM-DD.md)
    ├── projects/          # 项目特定上下文
    ├── groups/            # 群聊上下文
    └── system/            # 偏好设置、配置笔记
```

### 3. 初始化 MEMORY.md

在工作区根目录中创建 `MEMORY.md`：

```markdown
# MEMORY.md — 长期记忆

## 关于 [用户名]
- 关键事实、偏好、上下文

## 活动项目
- 项目摘要和状态

## 决策与经验教训
- 做出的重要选择
- 学到的经验教训

## 偏好设置
- 沟通风格
- 工具和工作流程
```

## 配置选项说明

| 设置 | 目的 | 推荐 |
|---------|---------|-------------|
| `enabled` | 开启记忆搜索 | `true` |
| `provider` | 嵌入提供者 | `"voyage"` |
| `sources` | 要索引的内容 | `["memory", "sessions"]` |
| `indexMode` | 索引时机 | `"hot"`（实时） |
| `minScore` | 相关性阈值 | `0.3`（越低结果越多） |
| `maxResults` | 返回的最大片段数 | `20` |

### 提供者选项
- `voyage` — Voyage AI 嵌入（推荐）
- `openai` — OpenAI 嵌入
- `local` — 本地嵌入（无需 API）

### 源选项
- `memory` — MEMORY.md + memory/*.md 文件
- `sessions` — 过去的对话记录
- `both` — 完整上下文（推荐）

## 每日日志格式

每日创建 `memory/logs/YYYY-MM-DD.md`：

```markdown
# YYYY-MM-DD — 每日日志

## [时间] — [事件/任务]
- 发生了什么
- 做出的决策
- 需要跟进的事项

## [时间] — [另一个事件]
- 详情
```

## 智能体指令 (AGENTS.md)

添加到你的 AGENTS.md 以控制智能体行为：

```markdown
## 记忆召回
在回答关于先前工作、决策、日期、人物、偏好或待办事项的问题前：
1. 使用相关查询运行 memory_search
2. 如需，使用 memory_get 拉取特定行
3. 搜索后若信心不足，说明已检查
```

## 故障排除

### 记忆搜索不工作？
1. 检查配置中的 `memorySearch.enabled: true`
2. 确认工作区根目录存在 MEMORY.md
3. 重启网关：`clawdbot gateway restart`

### 结果不相关？
- 将 `minScore` 降至 `0.2` 以获取更多结果
- 将 `maxResults` 增至 `30`
- 检查记忆文件是否包含有意义的内容

### 提供者错误？
- Voyage: 在环境中设置 `VOYAGE_API_KEY`
- OpenAI: 在环境中设置 `OPENAI_API_KEY`
- 如无 API 密钥，使用 `local` 提供者

## 验证

测试记忆是否正常工作：

```
用户: "关于 [过去主题] 你记得什么？"
智能体: [应搜索记忆并返回相关上下文]
```

如果智能体没有记忆，则配置未生效。重启网关。

## 完整配置示例

```json
{
  "memorySearch": {
    "enabled": true,
    "provider": "voyage",
    "sources": ["memory", "sessions"],
    "indexMode": "hot",
    "minScore": 0.3,
    "maxResults": 20
  },
  "workspace": "/path/to/your/workspace"
}
```

## 这为何重要

没有记忆时：
- 智能体会在会话间忘记所有内容
- 重复问题，丢失上下文
- 项目缺乏连贯性

有记忆时：
- 回忆过去的对话
- 了解你的偏好
- 跟踪项目历史
- 随时间建立关系

金鱼 → 大象。 🐘
