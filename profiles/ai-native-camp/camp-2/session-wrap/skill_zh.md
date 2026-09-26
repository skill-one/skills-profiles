# 会话总结技能

具有多智能体分析的全面会话总结工作流。

## 执行流程

```
┌─────────────────────────────────────────────────────┐
│  1. 检查 Git 状态                                │
├─────────────────────────────────────────────────────┤
│  2. 第一阶段：4 个分析智能体（并行）           │
│     ┌─────────────────┬─────────────────┐           │
│     │  doc-updater    │  automation-    │           │
│     │  (文档更新)  │  scout          │           │
│     ├─────────────────┼─────────────────┤           │
│     │  learning-      │  followup-      │           │
│     │  extractor      │  suggester      │           │
│     └─────────────────┴─────────────────┘           │
├─────────────────────────────────────────────────────┤
│  3. 第二阶段：验证智能体（串行）          │
│     ┌───────────────────────────────────┐           │
│     │       duplicate-checker           │           │
│     │  (验证第一阶段提案)     │           │
│     └───────────────────────────────────┘           │
├─────────────────────────────────────────────────────┤
│  4. 整合结果 & AskUserQuestion             │
├─────────────────────────────────────────────────────┤
│  5. 执行选定操作                        │
└─────────────────────────────────────────────────────┘
```

## 第 1 步：检查 Git 状态

```bash
git status --short
git diff --stat HEAD~3 2>/dev/null || git diff --stat
```

## 第 2 步：第一阶段 - 分析智能体（并行）

并行执行 4 个智能体（单条消息包含 4 个 Task 调用）。

### 会话摘要（提供给所有智能体）

```
会话摘要：
- 工作：[会话中执行的主要任务]
- 文件：[创建/修改的文件]
- 决策：[做出的关键决策]
```

### 并行执行

```
Task(
    subagent_type="doc-updater",
    description="文档更新分析",
    prompt="[会话摘要]\n\n分析是否需要更新 CLAUDE.md, context.md。"
)

Task(
    subagent_type="automation-scout",
    description="自动化模式分析",
    prompt="[会话摘要]\n\n分析重复模式或自动化机会。"
)

Task(
    subagent_type="learning-extractor",
    description="学习要点提取",
    prompt="[会话摘要]\n\n提取学习内容、错误和新的发现。"
)

Task(
    subagent_type="followup-suggester",
    description="后续任务建议",
    prompt="[会话摘要]\n\n建议未完成的任务和下一会话的优先级。"
)
```

### 智能体角色

| 智能体 | 角色 | 输出 |
|-------|------|--------|
| **doc-updater** | 分析 CLAUDE.md/context.md 更新 | 具体内容添加 |
| **automation-scout** | 检测自动化模式 | 技能/命令/智能体建议 |
| **learning-extractor** | 提取学习要点 | TIL 格式摘要 |
| **followup-suggester** | 建议后续任务 | 优先级任务列表 |

## 第 3 步：第二阶段 - 验证智能体（串行）

在第一阶段完成后运行（依赖第一阶段结果）。

```
Task(
    subagent_type="duplicate-checker",
    description="第一阶段提案验证",
    prompt="""
验证第一阶段分析结果。

## doc-updater 提案：
[doc-updater 结果]

## automation-scout 提案：
[automation-scout 结果]

检查提案是否与现有文档/自动化重复：
1. 完全重复：建议跳过
2. 部分重复：建议合并方法
3. 无重复：批准添加
"""
)
```

## 第 4 步：整合结果

```markdown
## 总结分析结果

### 文档更新
[doc-updater 摘要]
- 重复检查：[duplicate-checker 反馈]

### 自动化建议
[automation-scout 摘要]
- 重复检查：[duplicate-checker 反馈]

### 学习要点
[learning-extractor 摘要]

### 后续任务
[followup-suggester 摘要]
```

## 第 5 步：操作选择

```
AskUserQuestion(
    questions=[{
        "question": "您希望执行哪些操作？",
        "header": "总结选项",
        "multiSelect": true,
        "options": [
            {"label": "创建提交（推荐）", "description": "提交更改"},
            {"label": "更新 CLAUDE.md", "description": "记录新知识/工作流"},
            {"label": "创建自动化", "description": "生成技能/命令/智能体"},
            {"label": "跳过", "description": "无操作结束"}
        ]
    }]
)
```

## 第 6 步：执行选定操作

仅执行用户选择的操作。

---

## 快速参考

### 使用场景

- 重大工作会话结束
- 切换到不同项目前
- 完成功能或修复 Bug 后

### 跳过场景

- 非常短的会话，更改微不足道
- 仅阅读/探索代码
- 快速回答一次性问题

### 参数

- 空参数：交互式执行（完整工作流）
- 提供消息：用作提交信息并直接提交

## 额外资源

参考 `references/multi-agent-patterns.md` 获取详细的编排模式。
