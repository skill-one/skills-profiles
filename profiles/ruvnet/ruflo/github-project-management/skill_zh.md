# GitHub 项目管理

## 概述

一种使用 AI 群组协调管理 GitHub 项目的综合技能。该技能结合了智能问题管理、自动化的项目看板同步以及基于群组的协调，以实现高效的项目交付。

## 快速入门

### 基于群组协调的基本问题创建

```bash
# 创建一个协调问题
gh issue create \
  --title "功能：高级认证" \
  --body "实现 OAuth2 与社交登录..." \
  --label "增强功能,swarm-ready"

# 初始化群组用于问题
npx claude-flow@alpha hooks pre-task --description "功能实现"
```

### 项目看板快速设置

```bash
# 获取项目 ID
PROJECT_ID=$(gh project list --owner @me --format json | \
  jq -r '.projects[0].id')

# 初始化看板同步
npx ruv-swarm github board-init \
  --project-id "$PROJECT_ID" \
  --sync-mode "双向"
```

---

## 核心功能

### 1. 问题管理与筛选

<details>
<summary><strong>自动创建问题<$strong><$summary>

#### 单个问题与群组协调

```javascript
// 初始化问题管理群组
mcp__claude-flow__swarm_init { topology: "星型", maxAgents: 3 }
mcp__claude-flow__agent_spawn { type: "协调器", name: "问题协调器" }
mcp__claude-flow__agent_spawn { type: "研究员", name: "需求分析师" }
mcp__claude-flow__agent_spawn { type: "编码器", name: "实施规划器" }

// 创建综合问题
mcp__github__create_issue {
  owner: "org",
  repo: "repository",
  title: "集成审查：完整系统集成",
  body: `## 🔄 集成审查

  ### 概述
  组件之间的综合审查和集成。

  ### 目标
  - [ ] 验证依赖项和导入
  - [ ] 确保API集成
  - [ ] 检查挂钩系统集成
  - [ ] 验证数据系统一致性

  ### 群组协调
  此问题将由协调群组代理进行管理，以实现最佳进度跟踪。`,
  labels: ["集成", "审查", "增强功能"],
  assignees: ["username"]
}

// 设置自动跟踪
mcp__claude-flow__task_orchestrate {
  task: "使用自动更新监控和协调问题进度",
  strategy: "自适应",
  priority: "中等"
}
```

#### 批量创建问题

```bash
# 使用 gh CLI 创建多个相关问题
gh issue create \
  --title "功能：高级 GitHub 集成" \
  --body "实现全面的 GitHub 工作流自动化..." \
  --label "功能,github,高优先级"

gh issue create \
  --title "错误：集成分支中的合并冲突" \
  --body "解决合并冲突..." \
  --label "错误,集成,紧急"

gh issue create \
  --title "文档：更新集成指南" \
  --body "更新所有文档..." \
  --label "文档,集成"
```

<$details>

<details>
<summary><strong>问题到群组转换<$strong><$summary>

#### 将问题转换为群组任务

```bash
# 获取问题详情
ISSUE_DATA=$(gh issue view 456 --json title,body,labels,assignees,comments)

# 从问题创建群组
npx ruv-swarm github issue-to-swarm 456 \
  --issue-data "$ISSUE_DATA" \
  --auto-decompose \
  --assign-agents

# 批量处理多个问题
ISSUES=$(gh issue list --label "swarm-ready" --json number,title,body,labels)
npx ruv-swarm github issues-batch \
  --issues "$ISSUES" \
  --parallel

# 使用群组状态更新问题
echo "$ISSUES" | jq -r '.[].number' | while read -r num; do
  gh issue edit $num --add-label "swarm-processing"
done
```

#### 问题评论命令

执行群组操作通过问题评论：

```markdown
<!-- 在问题评论中 -->
$swarm analyze
$swarm decompose 5
$swarm assign @agent-coder
$swarm estimate
$swarm start
```

<$details>

<details>
<summary><strong>自动问题筛选<$strong><$summary>

#### 基于内容自动标记

```javascript
// .github$swarm-labels.json
{
  "rules": [
    {
      "keywords": ["错误", "问题", "损坏"],
      "labels": ["错误", "swarm-debugger"],
      "agents": ["debugger", "tester"]
    },
    {
      "keywords": ["功能", "实现", "添加"],
      "labels": ["增强功能", "swarm-feature"],
      "agents": ["architect", "coder", "tester"]
    },
    {
      "keywords": ["慢", "性能", "优化"],
      "labels": ["性能", "swarm-optimizer"],
      "agents": ["analyst", "optimizer"]
    }
  ]
}
```

#### 自动筛选系统

```bash
# 分析和筛选未标记的问题
npx ruv-swarm github triage \
  --unlabeled \
  --analyze-content \
  --suggest-labels \
  --assign-priority

# 查找并链接重复问题
npx ruv-swarm github find-duplicates \
  --threshold 0.8 \
  --link-related \
  --close-duplicates
```

<$details>

<details>
<summary><strong>任务分解与进度跟踪<$strong><$summary>

#### 将问题分解为子任务

```bash
# 获取问题正文
ISSUE_BODY=$(gh issue view 456 --json body --jq '.body')

# 分解为子任务
SUBTASKS=$(npx ruv-swarm github issue-decompose 456 \
  --body "$ISSUE_BODY" \
  --max-subtasks 10 \
  --assign-priorities)

# 更新问题为清单
CHECKLIST=$(echo "$SUBTASKS" | jq -r '.tasks[] | "- [ ] " + .description')
UPDATED_BODY="$ISSUE_BODY

## 子任务
$CHECKLIST"

gh issue edit 456 --body "$UPDATED_BODY"

# 为主要子任务创建链接问题
echo "$SUBTASKS" | jq -r '.tasks[] | select(.priority == "high")' | while read -r task; do
  TITLE=$(echo "$task" | jq -r '.title')
  BODY=$(echo "$task" | jq -r '.description')

  gh issue create \
    --title "$TITLE" \
    --body "$BODY

父问题: #456" \
    --label "子任务"
done
```

#### 自动进度更新

```bash
# 获取当前问题状态
CURRENT=$(gh issue view 456 --json body,labels)

# 获取群组进度
PROGRESS=$(npx ruv-swarm github issue-progress 456)

# 在问题正文中更新清单
UPDATED_BODY=$(echo "$CURRENT" | jq -r '.body' | \
  npx ruv-swarm github update-checklist --progress "$PROGRESS")

# 编辑问题更新正文
gh issue edit 456 --body "$UPDATED_BODY"

# 作为评论发布进度摘要
SUMMARY=$(echo "$PROGRESS" | jq -r '
"## 📊 进度更新

**完成率**: \(.completion)%
**预计完成时间**: \(.eta)

### 已完成任务
\(.completed | map("- ✅ " + .) | join("\n"))

### 进行中
\(.in_progress | map("- 🔄 " + .) | join("\n"))

### 剩余任务
\(.remaining | map("- ⏳ " + .) | join("\n"))

---
🤖 由群组代理自动更新"')

gh issue comment 456 --body "$SUMMARY"

# 根据进度更新标签
if [[ $(echo "$PROGRESS" | jq -r '.completion') -eq 100 ]]; then
  gh issue edit 456 --add-label "ready-for-review" --remove-label "in-progress"
fi
```

<$details>

<details>
<summary><strong>过期问题管理<$strong><$summary>

#### 使用群组分析自动关闭过期问题

```bash
# 查找过期问题
STALE_DATE=$(date -d '30 天前' --iso-8601)
STALE_ISSUES=$(gh issue list --state open --json number,title,updatedAt,labels \
  --jq ".[] | select(.updatedAt < \"$STALE_DATE\")")

# 分析每个过期问题
echo "$STALE_ISSUES" | jq -r '.number' | while read -r num; do
  # 获取完整问题上下文
  ISSUE=$(gh issue view $num --json title,body,comments,labels)

  # 使用群组分析
  ACTION=$(npx ruv-swarm github analyze-stale \
    --issue "$ISSUE" \
    --suggest-action)

  case "$ACTION" in
    "close")
      gh issue comment $num --body "此问题已 30 天未活跃，将在 7 天内关闭，如果没有进一步活动。"
      gh issue edit $num --add-label "过期"
      ;;
    "keep")
      gh issue edit $num --remove-label "过期" 2>$dev$null || true
      ;;
    "needs-info")
      gh issue comment $num --body "此问题需要更多信息。请提供更多上下文，否则可能会被标记为过期。"
      gh issue edit $num --add-label "需要信息"
      ;;
  esac
done

# 关闭 37 天以上过期的问
