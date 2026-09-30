---
name: github-code-review
description: AI驱动的群组协作进行全面的GitHub代码审查
---

# GitHub 代码审查技能

> **AI 驱动的代码审查**：部署专业审查代理，执行全面、智能的代码审查，超越传统静态分析。

## 🎯 快速入门

### 简单审查
```bash
# 初始化 PR 审查集群
gh pr view 123 --json files,diff | npx ruv-swarm github review-init --pr 123

# 发布审查状态
gh pr comment 123 --body "🔍 多代理代码审查已启动"
```

### 完整审查工作流
```bash
# 使用 gh CLI 获取 PR 上下文
PR_DATA=$(gh pr view 123 --json files,additions,deletions,title,body)
PR_DIFF=$(gh pr diff 123)

# 初始化全面审查
npx ruv-swarm github review-init \
  --pr 123 \
  --pr-data "$PR_DATA" \
  --diff "$PR_DIFF" \
  --agents "security,performance,style,architecture,accessibility" \
  --depth comprehensive
```

---

## 📚 目录

<details>
<summary><strong>核心功能<$strong><$summary>

- [多代理审查系统](#multi-agent-review-system)
- [专业审查代理](#specialized-review-agents)
- [基于 PR 的集群管理](#pr-based-swarm-management)
- [自动化工作流](#automated-workflows)
- [质量门禁和检查](#quality-gates--checks)

<$details>

<details>
<summary><strong>审查代理<$strong><$summary>

- [安全审查代理](#security-review-agent)
- [性能审查代理](#performance-review-agent)
- [架构审查代理](#architecture-review-agent)
- [风格和规范代理](#style--convention-agent)
- [无障碍审查代理](#accessibility-agent)

<$details>

<details>
<summary><strong>高级功能<$strong><$summary>

- [上下文感知审查](#context-aware-reviews)
- [从历史中学习](#learning-from-history)
- [跨 PR 分析](#cross-pr-analysis)
- [自定义审查代理](#custom-review-agents)

<$details>

<details>
<summary><strong>集成与自动化<$strong><$summary>

- [CI/CD 集成](#cicd-integration)
- [Webhook 处理器](#webhook-handlers)
- [PR 评论命令](#pr-comment-commands)
- [自动修复](#automated-fixes)

<$details>

---

## 🚀 核心功能

### 多代理审查系统

部署专业 AI 代理进行全面代码审查：

```bash
# 使用 GitHub CLI 集成初始化审查集群
PR_DATA=$(gh pr view 123 --json files,additions,deletions,title,body)
PR_DIFF=$(gh pr diff 123)

# 启动多代理审查
npx ruv-swarm github review-init \
  --pr 123 \
  --pr-data "$PR_DATA" \
  --diff "$PR_DIFF" \
  --agents "security,performance,style,architecture,accessibility" \
  --depth comprehensive

# 发布初始审查状态
gh pr comment 123 --body "🔍 多代理代码审查已启动"
```

**优势：**
- ✅ 专业代理并行审查
- ✅ 跨多个领域的全面覆盖
- ✅ 通过协调分析加快审查周期
- ✅ 执行一致的质量标准

---

## 🤖 专业审查代理

### 安全审查代理

**重点：** 识别安全漏洞并建议修复

```bash
# 从 PR 获取已修改文件
CHANGED_FILES=$(gh pr view 123 --json files --jq '.files[].path')

# 运行安全聚焦审查
SECURITY_RESULTS=$(npx ruv-swarm github review-security \
  --pr 123 \
  --files "$CHANGED_FILES" \
  --check "owasp,cve,secrets,permissions" \
  --suggest-fixes)

# 根据严重性发布发现结果
if echo "$SECURITY_RESULTS" | grep -q "critical"; then
  # 对严重问题请求变更
  gh pr review 123 --request-changes --body "$SECURITY_RESULTS"
  gh pr edit 123 --add-label "security-review-required"
else
  # 对非严重问题发布评论
  gh pr comment 123 --body "$SECURITY_RESULTS"
fi
```

<details>
<summary><strong>执行的安全检查<$strong><$summary>

```javascript
{
  "checks": [
    "SQL 注入漏洞",
    "XSS 攻击向量",
    "身份验证绕过",
    "授权缺陷",
    "加密弱点",
    "依赖漏洞",
    "秘密暴露",
    "CORS 配置错误"
  ],
  "actions": [
    "在严重问题上阻止 PR",
    "建议安全替代方案",
    "添加安全测试用例",
    "更新安全文档"
  ]
}
```

<$details>

<details>
<summary><strong>安全问题评论模板<$strong><$summary>

```markdown
🔒 **安全问题：[类型]**

**严重性**： 🔴 严重 / 🟡 高 / 🟢 低

**描述**：
[清晰解释安全问题的内容]

**影响**：
[未解决时可能产生的后果]

**建议修复**：
```language
[修复代码示例]
```

**参考**：
- [OWASP 指南](link)
- [安全最佳实践](link)
```

<$details>

---

### 性能审查代理

**重点：** 分析性能影响和优化机会

```bash
# 运行性能分析
npx ruv-swarm github review-performance \
  --pr 123 \
  --profile "cpu,memory,io" \
  --benchmark-against main \
  --suggest-optimizations
```

<details>
<summary><strong>分析的性能指标<$strong><$summary>

```javascript
{
  "metrics": [
    "算法复杂度（大 O 分析）",
    "数据库查询效率",
    "内存分配模式",
    "缓存利用率",
    "网络请求优化",
    "包大小影响",
    "渲染性能"
  ],
  "基准测试": [
    "与基线比较",
    "负载测试模拟",
    "内存泄漏检测",
    "瓶颈识别"
  ]
}
```

<$details>

---

### 架构审查代理

**重点：** 评估设计模式和架构决策

```bash
# 架构审查
npx ruv-swarm github review-architecture \
  --pr 123 \
  --check "patterns,coupling,cohesion,solid" \
  --visualize-impact \
  --suggest-refactoring
```

<details>
<summary><strong>架构分析<$strong><$summary>

```javascript
{
  "patterns": [
    "设计模式遵循情况",
    "SOLID 原则",
    "DRY 违规",
    "关注点分离",
    "依赖注入",
    "层违规",
    "循环依赖"
  ],
  "指标": [
    "耦合指标",
    "内聚分数",
    "复杂度度量",
    "可维护性指数"
  ]
}
```

<$details>

---

### 风格和规范代理

**重点：** 强制执行编码标准和最佳实践

```bash
# 使用自动修复执行风格强制
npx ruv-swarm github review-style \
  --pr 123 \
  --check "formatting,naming,docs,tests" \
  --auto-fix "formatting,imports,whitespace"
```

<details>
<summary><strong>风格检查<$strong><$summary>

```javascript
{
  "checks": [
    "代码格式化",
    "命名规范",
    "文档标准",
    "注释质量",
    "测试覆盖率",
    "错误处理模式",
    "日志标准"
  ],
  "自动修复": [
    "格式化问题",
    "导入组织",
    "尾随空格",
    "简单命名问题"
  ]
}
```

<$details>

---

## 🔄 基于 PR 的集群管理

### 从 PR 创建集群

```bash
# 使用 gh CLI 从 PR 描述创建集群
gh pr view 123 --json body,title,labels,files | npx ruv-swarm swarm create-from-pr

# 基于PR标签自动生成代理
gh pr view 123 --json labels | npx ruv-swarm swarm auto-spawn

# 使用完整 PR 上下文创建集群
gh pr view 123 --json body,labels,author,assignees | \
  npx ruv-swarm swarm init --from-pr-data
```

### 基于标签的代理分配

将 PR 标签映射到专业代理：

```json
{
  "label-mapping": {
    "bug": ["debugger", "tester"],
    "feature": ["architect", "coder", "tester"],
    "refactor": ["analyst", "coder"],
    "docs": ["researcher", "writer"],
    "performance": ["analyst", "optimizer"],
    "security": ["security", "authentication", "audit"]
  }
}
```

### 基于 PR 大小的拓扑选择

```bash
# 基于PR复杂度自动选择拓扑
# 小 PR (< 100 行)：环形拓扑
# 中等 PR (100-500 行)：网状拓扑
# 大 PR (> 500 行)：分层拓扑
npx ruv-swarm github pr-topology --pr 123
```

---

## 🎬 PR 评论命令

直接从 PR 评论中执行集群命令：

```markdown
<!-- 在 PR 评论中 -->
$swarm init mesh 6
$swarm spawn coder "实现身份验证"
$swarm spawn tester "编写单元测试"
$swarm status
$swarm review --agents security,performance
```

<details>
<summary><strong>评论命令的 Webhook 处理器<$strong><$summary>

```javascript
// webhook-handler.js
const { createServer } = require('http');
const { execSync } = require('child_process');

createServer((req, res) => {
  if (req.url === '$github-webhook') {
    const event = JSON.parse(body);

    if (event.action === 'opened' && event.pull_request) {
      execSync(`npx ruv-swarm github pr-init ${event.pull_request.number}`);
    }

    if (event.comment && event.comment.body.startsWith('$swarm')) {
      const command = event.comment.body;
      execSync(`npx ruv-swarm github handle-comment --pr ${event.issue.number} --command "${command}"`);
    }

    res.writeHead(200);
    res.end('OK');
  }
}).listen(3000);
```

<$details>

---

## ⚙️ 审查配置

### 配置文件

```yaml
# .github$review-swarm.yml
version: 1
review:
  auto-trigger: true
  required-agents:
    - security
    - performance
    - style
  optional-agents:
    - architecture
    - accessibility
    - i18n

  阈值:
    security: block      # 在发现安全问题时阻止合并
    performance: warn    # 在发现性能问题时警告
    style: suggest       # 建议风格改进

  规则:
    security:
      - no-eval
      - no-hardcoded-secrets
      - proper-auth-checks
      - validate-input
    performance:
      - no-n-plus-one
      - efficient-queries
      - proper-caching
      - optimize-loops
    architecture:
      - max-coupling: 5
      - min-cohesion: 0.7
      - follow-patterns
      - avoid-circular-deps
```

### 自定义审查触发器

```javascript
{
  "triggers": {
    "high-risk-files": {
      "paths": ["**$auth/**", "**$payment/**", "**$admin/**"],
      "agents": ["security", "architecture"],
      "depth": "comprehensive",
      "require-approval": true
    },
    "performance-critical": {
      "paths": ["**$api/**", "**$database/**", "**$cache/**"],
      "agents": ["performance", "database"],
      "benchmarks": true,
      "regression-threshold": "5%"
    },
    "ui-changes": {
      "paths": ["**$components/**", "**$styles/**", "**$pages/**"],
      "agents": ["accessibility", "style", "i18n"],
      "visual-tests": true,
      "responsive-check": true
    }
  }
}
```

---

## 🤖 自动化工作流

### PR 创建时自动审查

```yaml
# .github$workflows$auto-review.yml
name: 自动化代码审查
on:
  pull_request:
    types: [opened, synchronize]
  issue_comment:
    types: [created]

jobs:
  swarm-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions$checkout@v3
        with:
          fetch-depth: 0

      - name: 设置 GitHub CLI
        run: echo "${{ secrets.GITHUB_TOKEN }}" | gh auth login --with-token

      - name: 运行审查集群
        run: |
          # 使用 gh CLI 获取 PR 上下文
          PR_NUM=${{ github.event.pull_request.number }}
          PR_DATA=$(gh pr view $PR_NUM --json files,title,body,labels)
          PR_DIFF=$(gh pr diff $PR_NUM)

          # 运行集群审查
          REVIEW_OUTPUT=$(npx ruv-swarm github review-all \
            --pr $PR_NUM \
            --pr-data "$PR_DATA" \
            --diff "$PR_DIFF" \
            --agents "security,performance,style,architecture")

          # 发布审查结果
          echo "$REVIEW_OUTPUT" | gh pr review $PR_NUM --comment -F -

          # 更新 PR 状态
          if echo "$REVIEW_OUTPUT" | grep -q "approved"; then
            gh pr review $PR_NUM --approve
          elif echo "$REVIEW_OUTPUT" | grep -q "changes-requested"; then
            gh pr review $PR_NUM --request-changes -b "请查看评论中的审查结果"
          fi

      - name: 更新标签
        run: |
          # 基于审查结果添加标签
          if echo "$REVIEW_OUTPUT" | grep -q "security"; then
            gh pr edit $PR_NUM --add-label "security-review"
          fi
          if echo "$REVIEW_OUTPUT" | grep -q "performance"; then
            gh pr edit $PR_NUM --add-label "performance-review"
          fi
```

---

## 💬 智能评论生成

### 生成上下文感知的审查评论

```bash
# 获取带上下文的 PR 差异
PR_DIFF=$(gh pr diff 123 --color never)
PR_FILES=$(gh pr view 123 --json files)

# 生成审查评论
COMMENTS=$(npx ruv-swarm github review-comment \
  --pr 123 \
  --diff "$PR_DIFF" \
  --files "$PR_FILES" \
  --style "constructive" \
  --include-examples \
  --suggest-fixes)

# 使用 gh CLI 发布评论
echo "$COMMENTS" | jq -c '.[]' | while read -r comment; do
  FILE=$(echo "$comment" | jq -r '.path')
  LINE=$(echo "$comment" | jq -r '.line')
  BODY=$(echo "$comment" | jq -r '.body')
  COMMIT_ID=$(gh pr view 123 --json headRefOid -q .headRefOid)

  # 创建行内审查评论
  gh api \
    --method POST \
    $repos/:owner/:repo$pulls/123$comments \
    -f path="$FILE" \
    -f line="$LINE" \
    -f body="$BODY" \
    -f commit_id="$COMMIT_ID"
done
```

### 批量评论管理

```bash
# 高效管理审查评论
npx ruv-swarm github review-comments \
  --pr 123 \
  --group-by "agent,severity" \
  --summarize \
  --resolve-outdated
```

---

## 🚪 质量门禁和检查

### 状态检查

```yaml
# 分支保护中的必需状态检查
protection_rules:
  required_status_checks:
    strict: true
    contexts:
      - "review-swarm$security"
      - "review-swarm$performance"
      - "review-swarm$architecture"
      - "review-swarm$tests"
```

### 定义质量门禁

```bash
# 设置质量门禁阈值
npx ruv-swarm github quality-gates \
  --define '{
    "security": {"threshold": "no-critical"},
    "performance": {"regression": "<5%"},
    "coverage": {"minimum": "80%"},
    "architecture": {"complexity": "<10"},
    "duplication": {"maximum": "5%"}
  }'
```

### 跟踪审查指标

```bash
# 监控审查效果
npx ruv-swarm github review-metrics \
  --period 30d \
  --metrics "issues-found,false-positives,fix-rate,time-to-review" \
  --export-dashboard \
  --format json
```

---

## 🎓 高级功能

### 上下文感知审查

使用完整项目上下文分析 PR：

```bash
# 带全面上下文的审查
npx ruv-swarm github review-context \
  --pr 123 \
  --load-related-prs \
  --analyze-impact \
  --check-breaking-changes \
  --dependency-analysis
```

### 从历史中学习

在代码库模式上训练审查代理：

```bash
# 从过去的审查中学习
npx ruv-swarm github review-learn \
  --analyze-past-reviews \
  --identify-patterns \
  --improve-suggestions \
  --reduce-false-positives

# 在您的代码库上训练
npx ruv-swarm github review-train \
  --learn-patterns \
  --adapt-to-style \
  --improve-accuracy
```

### 跨 PR 分析

协调跨相关 pull 请求的审查：

```bash
# 一起分析相关 PR
npx ruv-swarm github review-batch \
  --prs "123,124,125" \
  --check-consistency \
  --verify-integration \
  --combined-impact
```

### 多 PR 集群协调

```bash
# 跨相关 PR 协调集群
npx ruv-swarm github multi-pr \
  --prs "123,124,125" \
  --strategy "parallel" \
  --share-memory
```

---

## 🛠️ 自定义审查代理

### 创建自定义代理

```javascript
// custom-review-agent.js
class CustomReviewAgent {
  constructor(config) {
    this.config = config;
    this.rules = config.rules || [];
  }

  async review(pr) {
    const issues = [];

    // 自定义逻辑：检查生产代码中的 TODO 注释
    if (await this.checkTodoComments(pr)) {
      issues.push({
        severity: 'warning',
        file: pr.file,
        line: pr.line,
        message: '生产代码中发现了 TODO 注释',
        suggestion: '解决 TODO 或创建问题来跟踪它'
      });
    }

    // 自定义逻辑：验证 API 版本控制
    if (await this.checkApiVersioning(pr)) {
      issues.push({
        severity: 'error',
        file: pr.file,
        line: pr.line,
        message: 'API 端点缺少版本控制',
        suggestion: '为 API 路径添加 $v1/,$v2/ 前缀'
      });
    }

    return issues;
  }

  async checkTodoComments(pr) {
    // 实现
    const todoRegex = /\/\/\s*TODO|\/\*\s*TODO$gi;
    return todoRegex.test(pr.diff);
  }

  async checkApiVersioning(pr) {
    // 实现
    const apiRegex = $app\.(get|post|put|delete)\(['"]\$api\/(?!v\d+)/;
    return apiRegex.test(pr.diff);
  }
}

module.exports = CustomReviewAgent;
```

### 注册自定义代理

```bash
# 注册自定义审查代理
npx ruv-swarm github register-agent \
  --name "custom-reviewer" \
  --file ".$custom-review-agent.js" \
  --category "standards"
```

---

## 🔧 CI/CD 集成

### 与构建管道集成

```yaml
# .github$workflows$build-and-review.yml
name: 构建和审查
on: [pull_request]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions$checkout@v3
      - run: npm install
      - run: npm test
      - run: npm run build

  swarm-review:
    needs: build-and-test
    runs-on: ubuntu-latest
    steps:
      - name: 运行 Swarm 审查
        run: |
          npx ruv-swarm github review-all \
            --pr ${{ github.event.pull_request.number }} \
            --include-build-results
```

### 自动化 PR 修复

```bash
# 自动修复常见问题
npx ruv-swarm github pr-fix 123 \
  --issues "lint,test-failures,formatting" \
  --commit-fixes \
  --push-changes
```

### PR 进度更新

```bash
# 使用 gh CLI 将 Swarm 进度发布到 PR
PROGRESS=$(npx ruv-swarm github pr-progress 123 --format markdown)

gh pr comment 123 --body "$PROGRESS"

# 根据 进度更新 PR 标签
if [[ $(echo "$PROGRESS" | grep -o '[0-9]\+%' | sed 's/%//') -gt 90 ]]; then
  gh pr edit 123 --add-label "ready-for-review"
fi
```

---

## 📋 完整工作流示例

### 示例 1：安全关键 PR

```bash
# 审查身份验证系统更改
npx ruv-swarm github review-init \
  --pr 456 \
  --agents "security,authentication,audit" \
  --depth "maximum" \
  --require-security-approval \
  --penetration-test
```

### 示例 2：性能敏感 PR

```bash
# 审查数据库优化
npx ruv-swarm github review-init \
  --pr 789 \
  --agents "performance,database,caching" \
  --benchmark \
  --profile \
  --load-test
```

### 示例 3：UI 组件 PR

```bash
# 审查新的组件库
npx ruv-swarm github review-init \
  --pr 321 \
  --agents "accessibility,style,i18n,docs" \
  --visual-regression \
  --component-tests \
  --responsive-check
```

### 示例 4：功能开发 PR

```bash
# 审查新功能实现
gh pr view 456 --json body,labels,files | \
  npx ruv-swarm github pr-init 456 \
    --topology hierarchical \
    --agents "architect,coder,tester,security" \
    --auto-assign-tasks
```

### 示例 5：错误修复 PR

```bash
# 审查带有调试重点的错误修复
npx ruv-swarm github pr-init 789 \
  --topology mesh \
  --agents "debugger,analyst,tester" \
  --priority high \
  --regression-test
```

---

## 📊 监控与分析

### 审查仪表板

```bash
# 启动实时审查仪表板
npx ruv-swarm github review-dashboard \
  --real-time \
  --show "agent-activity,issue-trends,fix-rates,coverage"
```

### 生成审查报告

```bash
# 创建全面的审查报告
npx ruv-swarm github review-report \
  --format "markdown" \
  --include "summary,details,trends,recommendations" \
  --email-stakeholders \
  --export-pdf
```

### PR Swarm 分析

```bash
# 生成特定 PR 的分析
npx ruv-swarm github pr-report 123 \
  --metrics "completion-time,agent-efficiency,token-usage,issue-density" \
  --format markdown \
  --compare-baseline
```

### 导出到 GitHub Insights

```bash
# 将指标导出到 GitHub Insights
npx ruv-swarm github export-metrics \
  --pr 123 \
  --to-insights \
  --dashboard-url
```

---

## 🔐 安全注意事项

### 最佳实践

1. **令牌权限**：确保 GitHub 令牌具有最小必需范围
2. **命令验证**：在执行前验证所有 PR 评论
3. **速率限制**：为 PR 操作实现速率限制
4. **审计跟踪**：记录所有 Swarm 操作以符合合规性
5. **密钥管理**：切勿在 PR 评论或日志中暴露 API 密钥

### 安全检查清单

- [ ] GitHub 令牌仅限于仓库
- [ ] 验证 webhook 签名
- [ ] 启用命令注入保护
- [ ] 配置速率限制
- [ ] 启用审计日志
- [ ] 激活密钥扫描
- [ ] 强制执行分支保护规则

---

## 📚 最佳实践

### 1. 审查配置
- ✅ 提前定义清晰的审查标准
- ✅ 设置适当的严重性阈值
- ✅ 为您的技术栈配置代理专业化
- ✅ 建立紧急情况下的覆盖程序

### 2. 评论质量
- ✅ 提供可操作的、具体的反馈
- ✅ 在建议中包含代码示例
- ✅ 引用文档和最佳实践
- ✅ 保持尊重、建设性的语气

### 3. 性能优化
- ✅ 缓存分析结果以避免重复工作
- ✅ 为大型 PR 使用增量审查
- ✅ 启用并行代理执行
- ✅ 高效地批量评论操作

### 4. PR 模板

```markdown
<!-- .github$pull_request_template.md -->
## Swarm 配置
- Topology: [mesh$hierarchical$ring$star]
- Max Agents: [number]
- Auto-spawn: [yes$no]
- Priority: [high$medium$low]

## Swarm 任务
- [ ] 任务 1 描述
- [ ] 任务 2 描述
- [ ] 任务 3 描述

## 审查重点区域
- [ ] 安全审查
- [ ] 性能分析
- [ ] 架构验证
- [ ] 可访问性检查
```

### 5. 准备自动合并

```bash
# 当 Swarm 完成并通过检查时自动合并
SWARM_STATUS=$(npx ruv-swarm github pr-status 123)

if [[ "$SWARM_STATUS" == "complete" ]]; then
  # 检查审查要求
  REVIEWS=$(gh pr view 123 --json reviews --jq '.reviews | length')

  if [[ $REVIEWS -ge 2 ]]; then
    # 启用自动合并
    gh pr merge 123 --auto --squash
  fi
fi
```

---

## 🔗 与 Claude Code 集成

### 工作流模式

1. **Claude Code** 读取 PR 差异和上下文
2. **Swarm** 根据PR类型协调审查方法
3. **代理** 并行处理不同的审查方面
4. **进度** 自动发布到 PR
5. **最终审查** 在标记为准备就绪之前执行

### 示例：完整的 PR 管理

```javascript
[单消息 - 并行执行]:
  // 初始化协调
  mcp__claude-flow__swarm_init { topology: "hierarchical", maxAgents: 5 }
  mcp__claude-flow__agent_spawn { type: "reviewer", name: "Senior Reviewer" }
  mcp__claude-flow__agent_spawn { type: "tester", name: "QA Engineer" }
  mcp__claude-flow__agent_spawn { type: "coordinator", name: "Merge Coordinator" }

  // 使用 gh CLI 创建和管理 PR
  Bash("gh pr create --title '功能：添加身份验证' --base main")
  Bash("gh pr view 54 --json files,diff")
  Bash("gh pr review 54 --approve --body 'LGTM after automated review'")

  // 执行测试和验证
  Bash("npm test")
  Bash("npm run lint")
  Bash("npm run build")

  // 跟踪进度
  TodoWrite { todos: [
    { content: "完成代码审查", status: "completed", activeForm: "Completing code review" },
    { content: "运行测试套件", status: "completed", activeForm: "Running test suite" },
    { content: "验证安全", status: "completed", activeForm: "Validating security" },
    { content: "准备合并", status: "pending", activeForm: "Merging when ready" }
  ]}
```

---

## 🆘 故障排除

### 常见问题

<details>
<summary><strong>问题：审查代理未启动<$strong><$summary>

**解决方案:**
```bash
# 检查 Swarm 状态
npx ruv-swarm swarm-status

# 验证 GitHub CLI 身份验证
gh auth status

# 重新初始化 Swarm
npx ruv-swarm github review-init --pr 123 --force
```

<$details>

<details>
<summary><strong>问题：评论未发布到 PR<$strong><$summary>

**解决方案:**
```bash
# 验证 GitHub 令牌权限
gh auth status

# 检查 API 速率限制
gh api rate_limit

# 使用批量评论发布
npx ruv-swarm github review-comments --pr 123 --batch
```

<$details>

<details>
<summary><strong>问题：审查时间过长<$strong><$summary>

**解决方案:**
```bash
# 使用增量审查大型 PR
npx ruv-swarm github review-init --pr 123 --incremental

# 减少代理数量
npx ruv-swarm github review-init --pr 123 --agents "security,style" --max-agents 3

# 启用并行处理
npx ruv-swarm github review-init --pr 123 --parallel --cache-results
```

<$details>

---

## 📖 其他资源

### 相关技能
- `github-pr-manager` - 全面管理 PR 生命周期
- `github-workflow-automation` - 自动化 GitHub 工作流
- `swarm-coordination` - 高级 Swarm 协调

### 文档
- [GitHub CLI 文档](https:/$cli.github.com$manual/)
- [RUV Swarm 指南](https:/$github.com$ruvnet$ruv-swarm)
- [Claude Flow 集成](https:/$github.com$ruvnet$claude-flow)

### 支持
- GitHub 问题：报告错误并请求功能
- 社区：加入讨论并分享经验
- 示例：浏览示例配置和工作流

---

## 📄 许可证

此技能是 Claude Code Flow 项目的一部分，并根据 MIT 许可证授权。

---

**最后更新:** 2025-10-19
**版本:** 1.0.0
**维护者:** Claude Code Flow 团队
