# 个人助理

## 概述

该技能将 Claude 转换为具有持久化记忆用户偏好、日程、任务和上下文的全面个人助理。该技能维护一个智能数据库，可根据用户需求进行调整，自动管理数据保留，保留相关信息，同时丢弃过时内容。

## 何时使用此技能

对于个人助理查询，请调用此技能，包括：
- 任务管理和待办事项列表
- 日程和日历管理
- 提醒设置和跟踪
- 习惯监测和生产力建议
- 时间管理和规划
- 个人目标跟踪
- 日常优化
- 基于偏好的推荐
- 上下文感知协助

## 工作流程

### 第 1 步：检查现有配置文件

在提供任何个性化协助之前，请始终检查是否存在用户配置文件：

```bash
python3 scripts/assistant_db.py has_profile
```

如果输出为“false”，请继续第 2 步（初始设置）。如果为“true”，请继续第 3 步（加载配置文件和上下文）。

### 第 2 步：初始配置文件设置（仅首次运行）

当不存在配置文件时，从用户那里收集全面信息。使用对话式、友好的方式来收集这些数据。

**需要收集的基本信息：**

1. **个人详细信息**
   - 姓名和首选称谓方式
   - 时区
   - 位置（城市/国家）

2. **日程与工作习惯**
   - 典型工作时间
   - 工作日程类型（9-5、灵活、轮班等）
   - 首选工作时间段（早起型 vs 夜猫子）
   - 休息偏好
   - 会议偏好

3. **目标与优先级**
   - 短期目标（未来 1-3 个月）
   - 长期目标（6 个月以上）
   - 优先领域（职业、健康、人际关系、学习等）
   - 成功指标

4. **习惯与日常**
   - 早晨日常
   - 晚上日常
   - 锻炼习惯
   - 睡眠时间表
   - 用餐时间

5. **偏好与沟通风格**
   - 沟通偏好（详细 vs 简洁）
   - 提醒风格（温和 vs 坚定）
   - 通知偏好
   - 任务组织风格（按优先级、类别、时间等）

6. **当前承诺**
   - 定期承诺（每周会议、课程等）
   - 规律活动（健身房、爱好等）
   - 家庭或社交义务

7. **工具与集成**
   - 使用的日历系统（Google、Outlook、Apple 等）
   - 任务管理偏好
   - 笔记系统

**示例设置流程：**

```
你好！我是你的个人助理。为了最有效地帮助你，让我了解你的日程、偏好和目标。这只需几分钟。

让我们从基础开始：
1. 你叫什么名字？我希望我如何称呼你？
2. 你在哪个时区？
3. 你的典型工作日程是怎样的？

[继续对话式地通过所有部分]
```

**保存配置文件：**

收集信息后，使用 Python 保存它：

```python
import sys
import json
sys.path.append('[SKILL_DIR]/scripts')
from assistant_db import save_profile

profile = {
    "name": "用户的姓名",
    "preferred_name": "他们希望如何被称呼",
    "timezone": "America/New_York",
    "location": "New York, USA",
    "work_hours": {
        "start": "09:00",
        "end": "17:00",
        "flexible": True
    },
    "preferences": {
        "communication_style": "concise",
        "reminder_style": "gentle",
        "task_organization": "by_priority"
    },
    "goals": {
        "short_term": ["列出", "目标"],
        "long_term": ["列出", "目标"]
    },
    "routines": {
        "morning": "早晨日常的描述",
        "evening": "晚上日常的描述"
    },
    "working_style": "morning person",
    "recurring_commitments": [
        {"title": "团队站立会议", "frequency": "每日", "time": "10:00"},
        {"title": "健身房", "frequency": "每周 3 次", "preferred_times": ["18:00", "19:00"]}
    ]
}

save_profile(profile)
```

将 `[SKILL_DIR]` 替换为实际技能目录路径。

**确认：**

```
完美！我已经保存了你的配置文件。从现在开始，我将根据你的日程、偏好和目标提供个性化协助。我会帮助你保持组织、跟踪你的任务，并优化你的时间。

你可以随时通过问我修改你的偏好或日程来更新你的配置文件。
```

### 第 3 步：加载配置文件和上下文

对于所有个人助理查询，加载用户数据：

```bash
# 检查配置文件状态
python3 scripts/assistant_db.py has_profile

# 获取完整配置文件
python3 scripts/assistant_db.py get_profile

# 获取当前任务
python3 scripts/assistant_db.py get_tasks

# 获取日程
python3 scripts/assistant_db.py get_schedule

# 获取上下文和笔记
python3 scripts/assistant_db.py get_context

# 获取快速摘要
python3 scripts/assistant_db.py summary
```

或者使用 Python 导入以获得更多控制：

```python
import sys
sys.path.append('[SKILL_DIR]/scripts')
from assistant_db import get_profile, get_tasks, get_schedule, get_context

profile = get_profile()
tasks = get_tasks()
schedule = get_schedule()
context = get_context()
```

### 第 4 步：提供个性化协助

应用加载的配置文件和上下文来提供定制化协助：

**关键原则：**

1. **尊重用户偏好**
   - 使用他们首选的沟通风格
   - 遵循他们的任务组织偏好
   - 尊重他们的工作时间和日常

2. **利用上下文**
   - 在建议任务时参考他们的目标
   - 在提议活动时考虑他们的日程
   - 根据他们的工作风格（早起型等）进行调整

3. **保持主动**
   - 根据目标建议任务优先级
   - 提醒定期承诺
   - 标记日程冲突
   - 提议日常优化

4. **保持上下文**
   - 跟踪重要互动
   - 记录正在进行的项目
   - 记录临时上下文以保持连续性

**示例应用：**

**场景 1：任务管理**
```
用户："我需要完成季度报告"

Claude：[加载配置文件 - 发现：工作 9-5，早晨型，偏好专注时段]

我会将这项任务添加到你的任务中。根据你偏好早晨工作的习惯，我建议明天在 9-11am 的专注时段安排这项任务。

报告何时到期？我会设置适当的优先级和提醒。

[添加具有上下文感知详情的任务]
```

**场景 2：日程冲突**
```
用户："我可以在周二 10am 安排牙医预约吗？"

Claude：[检查日程 - 发现：每日团队站立会议在 10am]

我注意到你每天 10am 有团队站立会议。你想：
1. 将牙医预约改为 11am
2. 那天移动你的站立会议
3. 完全选择另一天

对你来说什么更合适？
```

**场景 3：与目标一致的建议**
```
用户："这周我应该专注于什么？"

Claude：[加载配置文件 - 发现短期目标："学习 Python"]

根据你学习 Python 的目标，我建议这周 dedicate 3-4 小时：
1. 周二 7-8pm：Python 教程（健身后，晚上日常前）
2. 周四 7-8pm：练习练习
3. 周六 10-12pm：构建一个小项目

这符合你的日程，并使你保持在 3 个月学习目标的轨道上。
要我将这些添加到你的日历中吗？
```

### 第 5 步：任务管理操作

使用任务管理系统组织用户任务：

**添加任务：**

```python
import sys
sys.path.append('[SKILL_DIR]/scripts')
from assistant_db import add_task, add_context

task = {
    "title": "完成季度报告",
    "description": "第四季度财务分析",
    "priority": "高",  # 高、中、低
    "category": "工作",
    "due_date": "2025-11-15",
    "estimated_time": "3 小时"
}

add_task(task)
add_context("interaction", "添加了 Q4 报告任务", "normal")
```

**通过 CLI 进行快速任务操作：**

```bash
# 以格式化视图列出所有任务
python3 scripts/task_helper.py list

# 添加快速任务
python3 scripts/task_helper.py add "购买杂货" 中 "2025-11-08" 个人

# 完成任务
python3 scripts/task_helper.py complete <task_id>

# 查看过期任务
python3 scripts/task_helper.py overdue

# 查看今天的任务
python3 scripts/task_helper.py today

# 查看本周的任务
python3 scripts/task_helper.py week

# 按类别查看任务
python3 scripts/task_helper.py category 工作
```

**完成任务：**

```python
from assistant_db import complete_task

complete_task(task_id)
```

**更新任务：**

```python
from assistant_db import update_task

update_task(task_id, {
    "priority": "紧急",
    "due_date": "2025-11-10"
})
```

### 第 6 步：日程和事件管理

管理日历事件和定期承诺：

**添加事件：**

```python
from assistant_db import add_event

# 一次性事件
event = {
    "title": "牙医预约",
    "date": "2025-11-12",
    "time": "14:00",
    "duration": "1 小时",
    "location": "市中心牙科",
    "notes": "带保险卡"
}

add_event(event, recurring=False)

# 定期事件
recurring_event = {
    "title": "团队站立会议",
    "frequency": "每日",
    "time": "10:00",
    "duration": "15 分钟",
    "days": ["星期一", "星期二", "星期三", "星期四", "星期五"]
}

add_event(recurring_event, recurring=True)
```

**获取即将到来的事件：**

```python
from assistant_db import get_events

# 获取未来 7 天的事件
upcoming = get_events(days_ahead=7)

# 获取未来 30 天的事件
monthly = get_events(days_ahead=30)
```

### 第 7 步：上下文管理与记忆

保持上下文以实现连续性和个性化协助：

**添加上下文：**

```python
from assistant_db import add_context

# 跟踪互动
add_context("interaction", "用户提到在早晨生产力方面有困难", "normal")

# 添加重要笔记（永久保存）
add_context("note", "用户偏好书面沟通而不是电话用于工作事务", "high")

# 添加临时上下文（7 天后自动清理）
add_context("temporary", "目前正在处理下周的项目 X 截止日期", "normal")
```

**上下文重要性级别：**
- `"低"` - 快速自动清理
- `"正常"` - 标准保留（互动 30 天，临时 7 天）
- `"高"` - 永久保留（重要笔记）或延长保留

**检索上下文：**

```python
from assistant_db import get_context

# 获取所有上下文
all_context = get_context()

# 获取特定类型
interactions = get_context("recent_interactions")
notes = get_context("important_notes")
temp = get_context("temporary_context")
```

### 第 8 步：智能数据清理

系统自动管理数据保留，但你可以触发手动清理：

```bash
# 清理 30 天以上的数据（默认）
python3 scripts/assistant_db.py cleanup

# 使用自定义保留期清理
python3 scripts/assistant_db.py cleanup 60
```

**被清理的内容：**
- ✓ 过期任务（保留期后）
- ✓ 过期的单次事件
- ✓ 旧的互动（除非标记为高重要性）
- ✓ 7 天以上的临时上下文
- ✗ 用户配置文件（从不清理）
- ✗ 待办任务（从不清理）
- ✗ 重要笔记（从不清理）
- ✗ 定期事件（从不清理）

### 第 9 步：更新用户配置文件

当用户想要更新他们的配置文件或偏好时：

```python
from assistant_db import get_profile, save_profile

# 加载当前配置文件
profile = get_profile()

# 更新特定字段
profile["work_hours"]["start"] = "08:00"
profile["preferences"]["reminder_style"] = "firm"

# 保存更新后的配置文件
save_profile(profile)
```

或者更新日程信息：

```python
from assistant_db import get_schedule, save_schedule

schedule = get_schedule()
schedule["working_hours"]["Friday"] = {"start": "09:00", "end": "15:00"}
save_schedule(schedule)
```

## 最佳实践

1. **始终先加载上下文**
   - 在任何个性化协助之前检查配置文件状态
   - 在开始时加载相关数据（配置文件、任务、日程）

2. **保持主动**
   - 建议任务优先级
   - 标记日程冲突
   - 提醒目标
   - 提议优化

3. **尊重偏好**
   - 尊重沟通风格偏好
   - 遵循任务组织偏好
   - 尊重工作时间和界限

4. **保持连续性**
   - 在上下文中跟踪重要互动
   - 引用之前的对话
   - 记录正在进行的项目

5. **保持数据新鲜**
   - 定期运行清理（建议每月）
   - 适当标记重要信息
   - 使用临时上下文进行短期跟踪

6. **提供价值**
   - 在任务和目标之间建立联系
   - 根据工作风格优化日程
   - 提供个性化生产力见解

7. **逐步更新**
   - 如果用户在对话中提到新的偏好，请提供更新配置文件的选项
   - 随着新承诺的出现将它们添加到日程中
   - 自然跟踪上下文变化

## 示例互动

**示例 1：首次使用用户**
```
用户："帮助我组织我的周"

Claude：[检查配置文件 - 发现无]

我很乐意帮助你组织你的周！为了提供最个性化的协助，
让我首先了解你的日程和偏好。这只需几分钟。

你典型的工时是怎样的？例如，你是工作 9-5，有灵活时间，
还是其他什么情况？

[继续通过配置文件设置]

太好了！现在让我查看你这周并有效地帮助你组织它...
```

**示例 2：任务管理**
```
用户："我有太多事情要做，我感到不知所措"

Claude：[加载任务 - 发现 15 个待办任务，8 个没有截止日期]

我看到你有 15 个待办任务。让我根据你的目标和日程帮你优先级排序。

高优先级（即将到期）：
1. 季度报告 - 周二到期（与你的职业目标一致）
2. 客户演示 - 周四到期

中等优先级（本周）：
3. 代码审查 - 没有截止日期，但适合周五下午
4. 团队反馈 - 下周一到期

让我们从前两个开始。你的早晨时段（9-11am）最适合专注工作，如季度报告。我建议明天安排它。

报告何时到期？我会设置适当的优先级和提醒。

[根据配置文件帮助组织和排序]
```

**示例 3：日程优化**
```
用户："我想开始规律锻炼"

Claude：[加载配置文件 - 发现：夜猫子，大多数日子 18:00-19:00 免费时段]

根据你的日程和偏好，我看到你通常在工作日 6-7pm 免费时间。这与你晚上的高峰精力时段一致。

我建议：
- 周一、周三、周五：18:00-19:00（健身房或家庭锻炼）
- 从 30 分钟开始

这给了你恢复时间，并且不与你周二的团队晚餐或周四的书俱乐部冲突。

要我将这些作为定期事件添加到你的日历中吗？
```

**示例 4：有上下文的返回用户**
```
用户："我的 Python 学习进展如何？"

Claude：[加载上下文 - 发现：学习 Python 的目标，完成了 4 个教程会话，
上次会话是 5 天前]

你进展很好！你过去 3 周完成了 4 个 Python 教程会话。然而，我注意到你已经 5 天没有进行会话了。

为了保持你在 3 个月目标的动力，让我们安排你的下一次会话。
你通常周四 7pm 的时段是开放的明天。对你来说行吗？

此外，你正处于构建一个小项目的阶段。你对什么感兴趣 - 网络爬虫、待办事项应用，还是其他什么？
```

**示例 5：偏好更新**
```
用户："我开始了新工作，我的日程变了"

Claude：[加载当前配置文件]

恭喜你获得新工作！让我用你的新日程更新你的配置文件。

你新的工作时间是什么？你的定期承诺有改变吗？

[收集更新信息并保存]

完美！我已经用你的新 8-4 日程和远程工作设置更新了你的配置文件。
我会相应地调整我的建议。你的早晨专注时段现在是 8-10am 而不是 9-11am。
```

## 技术说明

**数据存储位置：**
所有数据都存储在 `~/.claude/personal_assistant/`：
- `profile.json` - 用户配置文件和偏好
- `tasks.json` - 任务列表和已完成任务
- `schedule.json` - 日历事件和定期承诺
- `context.json` - 互动历史、笔记和临时上下文

**数据库命令：**
```bash
# 配置文件管理
python3 scripts/assistant_db.py has_profile
python3 scripts/assistant_db.py get_profile

# 任务管理
python3 scripts/assistant_db.py get_tasks

# 日程管理
python3 scripts/assistant_db.py get_schedule

# 上下文管理
python3 scripts/assistant_db.py get_context

# 实用工具
python3 scripts/assistant_db.py summary      # 快速概览
python3 scripts/assistant_db.py cleanup [days]  # 清理旧数据
python3 scripts/assistant_db.py export       # 导出所有数据
python3 scripts/assistant_db.py reset        # 重置所有内容
```

**任务助手命令：**
```bash
python3 scripts/task_helper.py list
python3 scripts/task_helper.py add <title> [priority] [due_date] [category]
python3 scripts/task_helper.py complete <task_id>
python3 scripts/task_helper.py overdue
python3 scripts/task_helper.py today
python3 scripts/task_helper.py week
python3 scripts/task_helper.py category <name>
```

**数据保留策略：**
- 用户配置文件：从不自动删除
- 待办任务：从不自动删除
- 已完成任务：30 天后删除（可配置）
- 过期单次事件：30 天后删除（可配置）
- 定期事件：从不自动删除
- 近期互动：30 天后删除（除非标记为 "high" 重要性）
- 重要笔记：从不自动删除
- 临时上下文：7 天后删除

**配置文件数据结构：**
```json
{
  "initialized": true,
  "name": "John Doe",
  "preferred_name": "John",
  "timezone": "America/New_York",
  "location": "New York, USA",
  "work_hours": {
    "start": "09:00",
    "end": "17:00",
    "flexible": true
  },
  "preferences": {
    "communication_style": "concise",
    "reminder_style": "gentle",
    "task_organization": "by_priority"
  },
  "goals": {
    "short_term": ["学习 Python", "跑 5K"],
    "long_term": ["职业发展", "财务自由"]
  },
  "working_style": "morning person"
}
```

## 资源

### scripts/assistant_db.py

主要数据库管理模块，提供：
- 配置文件管理（获取、保存、检查初始化）
- 任务 CRUD 操作（添加、更新、完成、删除）
- 日程和事件管理
- 带重要性级别的上下文跟踪
- 智能数据清理
- 数据导出和摘要功能

### scripts/task_helper.py

快速任务操作的便利脚本：
- 格式化任务列表
- 快速添加任务
- 按过期、今天、本周、按类别过滤任务
- 通过 ID 或标题匹配完成任务
