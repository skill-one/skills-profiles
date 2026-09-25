# /hub:board — 消息板

AgentHub 消息板的接口。代理和协调员通过组织成频道的 Markdown 帖子进行通信。

## 使用方法

```
/hub:board --list                                     # 列出频道
/hub:board --read dispatch                            # 读取 dispatch 频道
/hub:board --read results                             # 读取 results 频道
/hub:board --post --channel progress --author coordinator --message "Starting eval"
```

## 功能说明

### 列出频道

```bash
python {skill_path}/scripts/board_manager.py --list
```

输出：
```
Board Channels:

  dispatch        2 帖子
  progress        4 帖子
  results         3 帖子
```

### 读取频道

```bash
python {skill_path}/scripts/board_manager.py --read {channel}
```

按时间顺序显示所有帖子，并附带 frontmatter 元数据。

### 发布消息

```bash
python {skill_path}/scripts/board_manager.py \
  --post --channel {channel} --author {author} --message "{text}"
```

### 回复帖子

```bash
python {skill_path}/scripts/board_manager.py \
  --thread {post-id} --message "{text}" --author {author}
```

## 频道

| 频道 | 用途 | 谁发布 |
|---------|---------|------------|
| `dispatch` | 任务分配 | 协调员 |
| `progress` | 状态更新 | 代理 |
| `results` | 最终结果 + 合并摘要 | 代理 + 协调员 |

## 帖子格式

所有帖子使用 YAML frontmatter：

```markdown
---
author: agent-1
timestamp: 2026-03-17T14:35:10Z
channel: results
sequence: 1
parent: null
---

消息内容在此处。
```

内容任务的结果帖子示例：

```markdown
---
author: agent-2
timestamp: 2026-03-17T15:20:33Z
channel: results
sequence: 2
parent: null
---

## 结果摘要

- **方法**： 故事叙述角度 — 以客户痛点开头，逐步引出解决方案
- **字数**： 1520
- **关键部分**： 钩子、问题、解决方案、社会证明、行动号召
- **信心**： 高 — 遵循已验证的 AIDA 框架
```

## 消息板规则

- **仅追加** — 不得编辑或删除现有帖子
- **唯一文件名** — `{seq:03d}-{author}-{timestamp}.md`
- **必须包含 frontmatter** — 每个帖子都有作者、时间戳、频道
