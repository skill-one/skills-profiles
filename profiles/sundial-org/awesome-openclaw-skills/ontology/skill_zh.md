# 本体

一种带类型词汇表+约束系统的知识表示方法，以可验证的图形式呈现。

## 核心概念

所有事物都是一个具有**类型**、**属性**以及与其他实体**关系**的**实体**。每次变更都会在提交前进行类型约束验证。

```
实体: { id, 类型, 属性, 关系, 创建时间, 更新时间 }
关系: { 起始实体id, 关系类型, 目标实体id, 属性 }
```

## 使用场景

| 触发条件 | 操作 |
|---------|--------|
| "记住..." | 创建/更新实体 |
| "我知道X的哪些信息?" | 查询图 |
| "将X与Y关联" | 创建关系 |
| "显示Z项目的所有任务" | 图遍历 |
| "X的依赖项是什么?" | 依赖查询 |
| 规划多步工作 | 模型为图转换 |
| 技能需要共享状态 | 读写本体对象 |

## 核心类型

```yaml
# 代理与人员
Person: { name, email?, phone?, notes? }
Organization: { name, type?, members[] }

# 工作
Project: { name, status, goals[], owner? }
Task: { title, status, due?, priority?, assignee?, blockers[] }
Goal: { description, target_date?, metrics[] }

# 时间与地点
Event: { title, start, end?, location?, attendees[], recurrence? }
Location: { name, address?, coordinates? }

# 信息
Document: { title, path?, url?, summary? }
Message: { content, sender, recipients[], thread? }
Thread: { subject, participants[], messages[] }
Note: { content, tags[], refs[] }

# 资源
Account: { service, username, credential_ref? }
Device: { name, type, identifiers[] }
Credential: { service, secret_ref }  # 直接存储密钥

# 元数据
Action: { type, target, timestamp, outcome? }
Policy: { scope, rule, enforcement }
```

## 存储

默认: `memory/ontology/graph.jsonl`

```jsonl
{"op":"create","entity":{"id":"p_001","type":"Person","properties":{"name":"Alice"}}}
{"op":"create","entity":{"id":"proj_001","type":"Project","properties":{"name":"网站改版","status":"active"}}}
{"op":"relate","from":"proj_001","rel":"has_owner","to":"p_001"}
```

通过脚本或直接文件操作查询。对于复杂图，迁移到SQLite。

## 工作流

### 创建实体

```bash
python3 scripts/ontology.py create --type Person --props '{"name":"Alice","email":"alice@example.com"}'
```

### 查询

```bash
python3 scripts/ontology.py query --type Task --where '{"status":"open"}'
python3 scripts/ontology.py get --id task_001
python3 scripts/ontology.py related --id proj_001 --rel has_task
```

### 关联实体

```bash
python3 scripts/ontology.py relate --from proj_001 --rel has_task --to task_001
```

### 验证

```bash
python3 scripts/ontology.py validate  # 检查所有约束
```

## 约束

在 `memory/ontology/schema.yaml` 中定义：

```yaml
types:
  Task:
    required: [title, status]
    status_enum: [open, in_progress, blocked, done]
  
  Event:
    required: [title, start]
    validate: "end >= start if end exists"

  Credential:
    required: [service, secret_ref]
    forbidden_properties: [password, secret, token]  # 强制间接引用

relations:
  has_owner:
    from_types: [Project, Task]
    to_types: [Person]
    cardinality: many_to_one
  
  blocks:
    from_types: [Task]
    to_types: [Task]
    acyclic: true  # 无循环依赖
```

## 技能契约

使用本体的技能应声明：

```yaml
# 在SKILL.md的frontmatter或头部
ontology:
  reads: [Task, Project, Person]
  writes: [Task, Action]
  preconditions:
    - "Task.assignee must exist"
  postconditions:
    - "Created Task has status=open"
```

## 规划为图转换

将多步计划建模为一系列图操作：

```
计划: "安排团队会议并创建后续任务"

1. CREATE Event { title: "Team Sync", attendees: [p_001, p_002] }
2. RELATE Event -> has_project -> proj_001
3. CREATE Task { title: "Prepare agenda", assignee: p_001 }
4. RELATE Task -> for_event -> event_001
5. CREATE Task { title: "Send summary", assignee: p_001, blockers: [task_001] }
```

每一步在执行前都会进行验证。在约束违反时回滚。

## 集成模式

### 与因果推理

将本体变更记录为因果动作：

```python
# 创建/更新实体时，同时记录到因果动作日志
action = {
    "action": "create_entity",
    "domain": "ontology", 
    "context": {"type": "Task", "project": "proj_001"},
    "outcome": "created"
}
```

### 跨技能通信

```python
# 邮件技能创建承诺
commitment = ontology.create("Commitment", {
    "source_message": msg_id,
    "description": "周五前发送报告",
    "due": "2026-01-31"
})

# 任务技能接手
tasks = ontology.query("Commitment", {"status": "pending"})
for c in tasks:
    ontology.create("Task", {
        "title": c.description,
        "due": c.due,
        "source": c.id
    })
```

## 快速入门

```bash
# 初始化本体存储
mkdir -p memory/ontology
touch memory/ontology/graph.jsonl

# 创建模式（可选但推荐）
cat > memory/ontology/schema.yaml << 'EOF'
types:
  Task:
    required: [title, status]
  Project:
    required: [name]
  Person:
    required: [name]
EOF

# 开始使用
python3 scripts/ontology.py create --type Person --props '{"name":"Alice"}'
python3 scripts/ontology.py list --type Person
```

## 参考文献

- `references/schema.md` — 完整类型定义和约束模式
- `references/queries.md` — 查询语言和遍历示例
