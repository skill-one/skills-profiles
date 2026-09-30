---
name: github-project-management
description: 全面的 GitHub 项目管理，包括集群协调的问题跟踪、项目看板自动化和冲刺计划
---

# GitHub 项目管理

## 概述

一种使用 AI 群体协调管理 GitHub 项目的综合技能。该技能结合了智能问题管理、自动化的项目看板同步以及基于群体的协调，以实现高效的项目交付。

## 快速入门

### 基于群体协调的基本问题创建

```bash
# 创建一个协调问题
gh issue create \
  --title "功能：高级认证" \
  --body "实现 OAuth2 与社交登录..." \
  --label "增强功能,swarm-ready"

# 初始化群体用于问题
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

#### 单个问题与群体协调

```javascript
// 初始化问题管理群体
mcp__claude-flow__swarm_init { topology: "星型", maxAgents: 3 }
mcp__claude-flow__agent_spawn { type: "协调器", name: "问题协调器" }
mcp__claude-flow__agent_spawn { type: "研究员", name: "需求分析师" }
mcp__claude-flow__agent_spawn { type: "编码器", name: "实现规划器" }

// 创建全面的问题
mcp__github__create_issue {
  owner: "org",
  repo: "repository",
  title: "集成审查：完成系统集成",
  body: `## 🔄 集成审查

  ### 概述
  组件之间的综合审查和集成。

  ### 目标
  - [ ] 验证依赖项和导入
  - [ ] 确保API集成
  - [ ] 检查钩子系统集成
  - [ ] 验证数据系统一致性

  ### 群体协调
  此问题将由协调的群体代理管理，以实现最佳进度跟踪。`,
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
<summary><strong>问题到群体的转换<$strong><$summary>

#### 将问题转换为群体任务

```bash
# 获取问题详情
ISSUE_DATA=$(gh issue view 456 --json title,body,labels,assignees,comments)

# 从问题创建群体
npx ruv-swarm github issue-to-swarm 456 \
  --issue-data "$ISSUE_DATA" \
  --auto-decompose \
  --assign-agents

# 批量处理多个问题
ISSUES=$(gh issue list --label "swarm-ready" --json number,title,body,labels)
npx ruv-swarm github issues-batch \
  --issues "$ISSUES" \
  --parallel

# 使用群体状态更新问题
echo "$ISSUES" | jq -r '.[].number' | while read -r num; do
  gh issue edit $num --add-label "swarm-processing"
done
```

#### 问题评论命令

通过问题评论执行群体操作：

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

#### 基于内容自动添加标签

```javascript
// .github$swarm-labels.json
{
  "rules": [
    {
      "keywords": ["bug", "error", "broken"],
      "labels": ["bug", "swarm-debugger"],
      "agents": ["debugger", "tester"]
    },
    {
      "keywords": ["feature", "implement", "add"],
      "labels": ["增强功能", "swarm-feature"],
      "agents": ["architect", "coder", "tester"]
    },
    {
      "keywords": ["slow", "performance", "optimize"],
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

# 使用清单更新问题
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

# 获取群体进度
PROGRESS=$(npx ruv-swarm github issue-progress 456)

# 在问题正文中更新清单
UPDATED_BODY=$(echo "$CURRENT" | jq -r '.body' | \
  npx ruv-swarm github update-checklist --progress "$PROGRESS")

# 使用更新后的正文编辑问题
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

### 剩余
\(.remaining | map("- ⏳ " + .) | join("\n"))

---
🤖 由群体代理自动更新"')

gh issue comment 456 --body "$SUMMARY"

# 根据进度更新标签
if [[ $(echo "$PROGRESS" | jq -r '.completion') -eq 100 ]]; then
  gh issue edit 456 --add-label "ready-for-review" --remove-label "in-progress"
fi
```

<$details>

<details>
<summary><strong>过期问题管理<$strong><$summary>

#### 使用群体分析自动关闭过期问题

```bash
# 查找过期问题
STALE_DATE=$(date -d '30 天前' --iso-8601)
STALE_ISSUES=$(gh issue list --state open --json number,title,updatedAt,labels \
  --jq ".[] | select(.updatedAt < \"$STALE_DATE\")")

# 分析每个过期问题
echo "$STALE_ISSUES" | jq -r '.number' | while read -r num; do
  # 获取完整问题上下文
  ISSUE=$(gh issue view $num --json title,body,comments,labels)

  # 使用群体分析
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
      gh issue comment $num --body "此问题需要更多信息。请提供更多上下文，否则可能被标记为过期。"
      gh issue edit $num --add-label "需要信息"
      ;;
  esac
done

# 关闭 37 天以上过期的问

```bash
# 跨多个看板同步
npx ruv-swarm github multi-board-sync \
  --boards "开发,测试,发布" \
  --sync-rules '{
    "开发->测试": "when:ready-for-test",
    "测试->发布": "when:tests-pass"
  }'

# 跨组织同步
npx ruv-swarm github cross-org-sync \
  --source "org1/项目-A" \
  --target "org2/项目-B" \
  --field-mapping "自定义" \
  --conflict-resolution "source-wins"
```

<$details>

<details>
<summary><strong>问题依赖关系与史诗管理<$strong><$summary>

#### 依赖关系解决

```bash
# 处理问题依赖关系
npx ruv-swarm github issue-deps 456 \
  --resolve-order \
  --parallel-safe \
  --update-blocking
```

#### 史诗协调

```bash
# 协调史诗级别的swarms
npx ruv-swarm github epic-swarm \
  --epic 123 \
  --child-issues "456,457,458" \
  --orchestrate
```

<$details>

<details>
<summary><strong>跨仓库协调<$strong><$summary>

#### 多仓库问题管理

```bash
# 处理跨仓库的问题
npx ruv-swarm github cross-repo \
  --issue "org$repo#456" \
  --related "org$other-repo#123" \
  --coordinate
```

<$details>

<details>
<summary><strong>团队协作<$strong><$summary>

#### 工作分配

```bash
# 在团队间分配工作
npx ruv-swarm github board-distribute \
  --strategy "技能型" \
  --balance-workload \
  --respect-preferences \
  --notify-assignments
```

#### 站会自动化

```bash
# 生成站会报告
npx ruv-swarm github standup-report \
  --team "前端" \
  --include "昨天,今天,阻碍" \
  --format "slack" \
  --schedule "每日9点"
```

#### 审查协调

```bash
# 通过看板协调审查
npx ruv-swarm github review-coordinate \
  --board "代码审查" \
  --assign-reviewers \
  --track-feedback \
  --ensure-coverage
```

<$details>

---

## 问题模板

### 集成问题模板

```markdown
## 🔄 集成任务

### 概述
[集成需求的简要描述]

### 目标
- [ ] 组件A集成
- [ ] 组件B验证
- [ ] 测试和验证
- [ ] 文档更新

### 集成区域
#### 依赖关系
- [ ] package.json更新
- [ ] 版本兼容性
- [ ] 导入语句

#### 功能
- [ ] 核心功能集成
- [ ] API兼容性
- [ ] 性能验证

#### 测试
- [ ] 单元测试
- [ ] 集成测试
- [ ] 端到端验证

### Swarm协调
- **协调员**: 跟踪整体进度
- **分析师**: 技术验证
- **测试员**: 质量保证
- **文档员**: 文档更新

### 进度跟踪
在实施过程中，swarm代理将自动发布更新。

---
🤖 由Claude Code生成
```

### 缺陷报告模板

```markdown
## 🐛 缺陷报告

### 问题描述
[清晰的问题描述]

### 预期行为
[应该发生什么]

### 实际行为
[实际发生什么]

### 复现步骤
1. [步骤1]
2. [步骤2]
3. [步骤3]

### 环境
- 包: [包名和版本]
- Node.js: [版本]
- 操作系统: [操作系统]

### 调查计划
- [ ] 根本原因分析
- [ ] 修复实施
- [ ] 测试和验证
- [ ] 回归测试

### Swarm分配
- **调试器**: 问题调查
- **编码器**: 修复实施
- **测试员**: 验证和测试

---
🤖 由Claude Code生成
```

### 功能请求模板

```markdown
## ✨ 功能请求

### 功能描述
[提出的功能的清晰描述]

### 用例
1. [用例1]
2. [用例2]
3. [用例3]

### 接受标准
- [ ] 标准1
- [ ] 标准2
- [ ] 标准3

### 实施方法
#### 设计
- [ ] 架构设计
- [ ] API设计
- [ ] UI/UX原型

#### 开发
- [ ] 核心实现
- [ ] 与现有功能的集成
- [ ] 性能优化

#### 测试
- [ ] 单元测试
- [ ] 集成测试
- [ ] 用户验收测试

### Swarm协调
- **架构师**: 设计和规划
- **编码器**: 实施
- **测试员**: 质量保证
- **文档员**: 文档

---
🤖 由Claude Code生成
```

### Swarm任务模板

```markdown
<!-- .github/ISSUE_TEMPLATE$swarm-task.yml -->
name: Swarm任务
description: 为AI swarm处理创建任务
body:
  - type: dropdown
    id: topology
    attributes:
      label: Swarm拓扑
      options:
        - 网格
        - 分层
        - 环形
        - 星形
  - type: input
    id: agents
    attributes:
      label: 所需代理
      placeholder: "编码器,测试员,分析师"
  - type: textarea
    id: tasks
    attributes:
      label: 任务分解
      placeholder: |
        1. 任务一描述
        2. 任务二描述
```

---

## 工作流集成

### GitHub Actions用于问题管理

```yaml
# .github$workflows$issue-swarm.yml
name: 问题Swarm处理器
on:
  issues:
    types: [打开,标记,评论]

jobs:
  swarm-process:
    runs-on: ubuntu-latest
    steps:
      - name: 处理问题
        uses: ruvnet$swarm-action@v1
        with:
          command: |
            if [[ "${{ github.event.label.name }}" == "swarm-ready" ]]; then
              npx ruv-swarm github issue-init ${{ github.event.issue.number }}
            fi
```

### 看板集成工作流

```bash
# 与项目看板同步
npx ruv-swarm github issue-board-sync \
  --项目 "开发" \
  --列映射 '{
    "待办": "pending",
    "进行中": "active",
    "已完成": "completed"
  }'
```

---

## 专用问题策略

### 缺陷调查Swarm

```bash
# 专用缺陷处理
npx ruv-swarm github bug-swarm 456 \
  --reproduce \
  --隔离 \
  --修复 \
  --测试
```

### 功能实施Swarm

```bash
# 功能实施swarm
npx ruv-swarm github feature-swarm 456 \
  --设计 \
  --实施 \
  --文档 \
  --演示
```

### 技术债务重构

```bash
# 重构swarm
npx ruv-swarm github debt-swarm 456 \
  --分析影响 \
  --计划迁移 \
  --执行 \
  --验证
```

---

## 最佳实践

### 1. Swarm协调问题管理
- 始终为复杂问题初始化swarm
- 根据问题类型分配专业代理
- 使用内存进行进度协调
- 定期自动进度更新

### 2. 看板组织
- 清晰的列定义和一致的命名
- 跨仓库的系统标签策略
- 定期看板整理和维护
- 定义明确的自动化规则

### 3. 数据完整性
- 双向同步验证
- 冲突解决策略
- 完整的审计跟踪
- 定期备份项目数据

### 4. 团队采用
- 全面培训材料
- 清晰的文档化工作流
- 定期团队评审和回顾
- 积极的改进反馈循环

### 5. 智能标签和组织
- 跨仓库一致的标签策略
- 基于优先级的问题排序和分配
- 里程碑集成用于项目协调
- 代理类型到标签的映射

### 6. 自动化进度跟踪
- 定期自动更新与swarm协调
- 进度指标和完成跟踪
- 跨问题依赖管理
- 实时状态同步

---

## 故障排除

### 同步问题

```bash
# 诊断同步问题
npx ruv-swarm github board-diagnose \
  --check "权限,webhooks,速率限制" \
  --test-sync \
  --显示冲突
```

### 性能优化

```bash
# 优化看板性能
npx ruv-swarm github board-optimize \
  --分析大小 \
  --归档已完成 \
  --索引字段 \
  --缓存视图
```

### 数据恢复

```bash
# 恢复看板数据
npx ruv-swarm github board-recover \
  --备份ID "2024-01-15" \
  --恢复卡片 \
  --保留当前 \
  --合并冲突
```

---

## 指标和分析

### 性能指标

自动跟踪:
- 问题创建和解决时间
- 代理生产力指标
- 项目里程碑进度
- 跨仓库协调效率
- 赛道速度和燃尽
- 周期时间和吞吐量
- 在进行中限制

### 报告功能

- 每周进度摘要
- 代理性能分析
- 项目健康指标
- 集成成功率
- 团队协作指标
- 质量和缺陷跟踪

### 问题解决时间

```bash
# 分析swarm性能
npx ruv-swarm github issue-metrics \
  --问题 456 \
  --指标 "关闭时间,代理效率,子任务完成"
```

### Swarm有效性

```bash
# 生成有效性报告
npx ruv-swarm github effectiveness \
  --问题 "关闭:>2024-01-01" \
  --比较 "with-swarm,without-swarm"
```

---

## 安全和权限

1. **命令授权**: 在执行命令前验证用户权限
2. **速率限制**: 防止垃圾邮件和滥用问题命令
3. **审计日志**: 跟踪所有swarm在问题和看板上的操作
4. **数据隐私**: 尊重私有仓库设置
5. **访问控制**: 看板操作的适当GitHub权限
6. **Webhook安全**: 为实时更新安全地保护webhook端点

---

## 与其他技能的集成

### 无缝集成:
- `github-pr-workflow` - 自动将问题链接到拉取请求
- `github-release-management` - 协调发布问题和里程碑
- `sparc-orchestrator` - 复杂项目协调工作流
- `sparc-tester` - 问题的自动化测试工作流

---

## 完整工作流示例

### 全栈功能开发

```bash
# 1. 创建带swarm协调的功能问题
gh issue create \
  --title "功能: 实时协作" \
  --body "$(cat <<EOF
## 功能: 实时协作

### 概述
使用WebSockets实现实时协作功能。

### 目标
- [ ] WebSocket服务器设置
- [ ] 客户端集成
- [ ] 存在跟踪
- [ ] 冲突解决
- [ ] 测试和文档

### Swarm协调
此功能将使用网格拓扑进行并行开发。
EOF
)" \
  --label "增强,swarm-ready,高优先级"

# 2. 初始化swarm并分解任务
ISSUE_NUM=$(gh issue list --label "swarm-ready" --limit 1 --json number --jq '.[0].number')
npx ruv-swarm github issue-init $ISSUE_NUM \
  --topology mesh \
  --auto-decompose \
  --assign-agents "架构师,编码器,测试员"

# 3. 添加到项目看板
PROJECT_ID=$(gh project list --owner @me --format json | jq -r '.projects[0].id')
gh project item-add $PROJECT_ID --owner @me \
  --url "https:/$github.com/$GITHUB_REPOSITORY$issues/$ISSUE_NUM"

# 4. 设置自动跟踪
npx ruv-swarm github board-sync \
  --auto-move-cards \
  --update-metadata

# 5. 监控进度
npx ruv-swarm github issue-progress $ISSUE_NUM \
  --auto-update-comments \
  --notify-on-completion
```

---

## 快速参考命令

```bash
# 问题管理
gh issue create --title "..." --body "..." --label "..."
npx ruv-swarm github issue-init <number>
npx ruv-swarm github issue-decompose <number>
npx ruv-swarm github triage --unlabeled

# 项目看板
npx ruv-swarm github board-init --project-id <id>
npx ruv-swarm github board-sync
npx ruv-swarm github board-analytics

# 赛道管理
npx ruv-swarm github sprint-manage --sprint "赛道X"
npx ruv-swarm github milestone-track --milestone "vX.X"

# 分析
npx ruv-swarm github issue-metrics --issue <number>
npx ruv-swarm github board-kpis
```

---

## 其他资源

- [GitHub CLI文档](https:/$cli.github.com$manual/)
- [GitHub项目文档](https:/$docs.github.com$en$issues$planning-and-tracking-with-projects)
- [Swarm协调指南](https:/$github.com$ruvnet$ruv-swarm)
- [Claude Flow文档](https:/$github.com$ruvnet$claude-flow)

---

**最后更新**: 2025-10-19
**版本**: 2.0.0
**维护者**: Claude Code
