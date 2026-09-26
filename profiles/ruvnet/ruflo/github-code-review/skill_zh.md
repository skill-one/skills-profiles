# GitHub 代码审查技能

> **AI 驱动的代码审查**：部署专门的审查代理，执行全面、智能的代码审查，超越传统的静态分析。

## 🎯 快速入门

### 简单审查
```bash
# 初始化 PR 的审查群
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

- [多代理审查系统](#多代理审查系统)
- [专门的审查代理](#专门的审查代理)
- [基于 PR 的群管理](#基于-pr 的群管理)
- [自动化工作流](#自动化工作流)
- [质量门禁和检查](#质量门禁--检查)

<$details>

<details>
<summary><strong>审查代理<$strong><$summary>

- [安全审查代理](#安全审查代理)
- [性能审查代理](#性能审查代理)
- [架构审查代理](#架构审查代理)
- [风格和规范代理](#风格--规范代理)
- [无障碍代理](#无障碍代理)

<$details>

<details>
<summary><strong>高级功能<$strong><$summary>

- [上下文感知审查](#上下文感知审查)
- [从历史中学习](#从历史中学习)
- [跨 PR 分析](#跨-pr 分析)
- [自定义审查代理](#自定义审查代理)

<$details>

<details>
<summary><strong>集成和自动化<$strong><$summary>

- [CI/CD 集成](#cicd集成)
- [Webhook 处理器](#webhook处理器)
- [PR 评论命令](#pr评论命令)
- [自动化修复](#自动化修复)

<$details>

---

## 🚀 核心功能

### 多代理审查系统

部署专门的 AI 代理进行全面的代码审查：

```bash
# 使用 GitHub CLI 集成初始化审查群
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

**优势**：
- ✅ 由专门的代理并行审查
- ✅ 跨多个领域进行全面覆盖
- ✅ 通过协调分析加快审查周期
- ✅ 执行一致的质量标准

---

## 🤖 专门的审查代理

### 安全审查代理

**重点**：识别安全漏洞并提出修复建议

```bash
# 从 PR 获取已更改的文件
CHANGED_FILES=$(gh pr view 123 --json files --jq '.files[].path')

# 运行以安全为重点的审查
SECURITY_RESULTS=$(npx ruv-swarm github review-security \
  --pr 123 \
  --files "$CHANGED_FILES" \
  --check "owasp,cve,secrets,permissions" \
  --suggest-fixes)

# 根据严重性发布发现结果
if echo "$SECURITY_RESULTS" | grep -q "critical"; then
  # 请求对严重问题的更改
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
    "依赖项漏洞",
    "秘密暴露",
    "CORS 配置错误"
  ],
  "actions": [
    "在严重问题上阻止 PR",
    "建议安全的替代方案",
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
[清晰解释安全问题]

**影响**：
[如果不解决可能产生的后果]

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

**重点**：分析性能影响和优化机会

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

**重点**：评估设计模式和架构决策

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
    "设计模式遵循",
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

**重点**：执行编码规范和最佳实践

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
    "简单的命名问题"
  ]
}
```

<$details>

---

## 🔄 基于 PR 的群管理

### 从 PR 创建群

```bash
# 使用 gh CLI 从 PR 描述创建群
gh pr view 123 --json body,title,labels,files | npx ruv-swarm swarm create-from-pr

# 基于PR标签自动生成代理
gh pr view 123 --json labels | npx ruv-swarm swarm auto-spawn

# 使用完整的 PR 上下文创建群
gh pr view 123 --json body,labels,author,assignees | \
  npx ruv-swarm swarm init --from-pr-data
```

### 基于标签的代理分配

将 PR 标签映射到专门的代理：

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

### 基于 PR 大小选择拓扑

```bash
# 基于PR复杂度自动选择拓扑
# 小 PR (< 100 行)：环形拓扑
# 中等 PR (100-500 行)：网状拓扑
# 大 PR (> 500 行)：分层拓扑
npx ruv-swarm github pr-topology --pr 123
```

---

## 🎬 PR 评论命令

直接从 PR 评论中执行群命令：

```markdown
<!-- 在 PR 评论中 -->
$swarm init mesh 6
$swarm spawn coder "实现身份验证"
$swarm spawn tester "编写单元测试"
$swarm status
$swarm review --agents security,performance
```

<details>
<summary><strong>用于评论命令的 Webhook 处理器<$strong><$summary>

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

  thresholds:
    security: block      # 在安全问题上阻止合并
    performance: warn    # 在性能问题上发出警告
    style: suggest       # 建议风格改进

  rules:
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

      - name: 运行审查群
        run: |
          # 使用 gh CLI 获取 PR 上下文
          PR_NUM=${{ github.event.pull_request.number }}
          PR_DATA=$(gh pr view $PR_NUM --json files,title,body,labels)
          PR_DIFF=$(gh pr diff $PR_NUM)

          # 运行群审查
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
            gh pr review $PR_NUM --request-changes -b "请参阅上述审查评论"
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

  # 创建内联审查评论
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
# 分支保护中所需的状态检查
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
# 使用全面上下文审查
npx ruv-swarm github review-context \
  --pr 123 \
  --load-related-prs \
  --analyze-impact \
  --check-breaking-changes \
  --dependency-analysis
```

### 从历史中学习

在您的代码库模式上训练审查代理：

```bash
# 从过去的审查中学习
npx ruv-swarm github review-learn \
  --analyze-past-reviews \
  --identify-patterns \
  --improve-suggestions \
  --reduce-false-positives

# 在您的代码库中训练
npx ruv-swarm github review-train \
  --learn-patterns \
  --adapt-to-style \
  --improve-accuracy
```

### 跨 PR 分析

协调跨相关 pull 请求的审查：

```bash
# 一起分析相关的 PR
npx ruv-swarm github review-batch \
  --prs "123,124,125" \
  --check-consistency \
  --verify-integration \
  --combined-impact
```

### 多 PR 群协调

```bash
# 跨相关 PR 协调群
npx ruv-swarm github multi-pr \
  --prs "123,124,125" \
  --strategy "parallel" \
  --share-memory
```

---

## 🔐 安全注意事项

### 最佳实践

1. **令牌权限**：确保 GitHub 令牌具有最小必需范围
2. **命令验证**：在执行之前验证所有 PR 评论
3. **速率限制**：为 PR 操作实施速率限制
4. **审计跟踪**：记录所有群操作以符合合规性
5. **秘密管理**：绝不在 PR 评论或日志中暴露 API 密钥

### 安全检查清单

- [ ] GitHub 令牌仅限于存储库
- [ ] 验证 Webhook 签名
- [ ] 启用命令注入保护
- [ ] 配置速率限制
- [ ] 启用审计日志
- [ ] 活动的秘密扫描
- [ ] 强制执行分支保护规则

---

## 📚 最佳实践

### 1. 审查配置
- ✅ 提前定义清晰的审查标准
- ✅ 设置适当的严重性阈值
- ✅ 配置针对您的技术栈的代理专业化
- ✅ 建立紧急情况下的覆盖程序

### 2. 评论质量
- ✅ 提供具体、可操作的反馈
- ✅ 在建议中包含代码示例
- ✅ 引用文档和最佳实践
- ✅ 保持尊重、建设性的语气

### 3. 性能优化
- ✅ 缓存分析结果以避免重复工作
- ✅ 对大型 PR 使用增量审查
- ✅ 启用并行代理执行
- ✅ 高效地批量评论操作

### 4. PR 模板

```markdown
<!-- .github$pull_request_template.md -->
## 群配置
- 拓扑：[mesh$hierarchical$ring$star]
- 最大代理：[数字]
- 自动生成：[是$否]
- 优先级：[高$中$低]

## 群任务
- [ ] 任务 1 描述
- [ ] 任务 2 描述
- [ ] 任务 3 描述

## 审查重点区域
- [ ] 安全审查
- [ ] 性能分析
- [ ] 架构验证
- [ ] 无障碍检查
```

### 5. 准备自动合并

```bash
# 群完成并通过检查后自动合并
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
2. **群** 根据PR类型协调审查方法
3. **代理** 并行处理不同的审查方面
4. **进度** 自动发布到 PR
5. **最终审查** 在标记为准备就绪之前执行

### 示例：完整的 PR 管理流程

```javascript
[单消息 - 并行执行]:
  // 初始化协调
  mcp__claude-flow__swarm_init { topology: "hierarchical", maxAgents: 5 }
  mcp__claude-flow__agent_spawn { type: "reviewer", name: "高级审查员" }
  mcp__claude-flow__agent_spawn { type: "tester", name: "测试工程师" }
  mcp__claude-flow__agent_spawn { type: "coordinator", name: "合并协调员" }

  // 使用 gh CLI 创建和管理工作流
  Bash("gh pr create --title '功能：添加身份验证' --base main")
  Bash("gh pr view 54 --json files,diff")
  Bash("gh pr review 54 --approve --body 'LGTM after automated review'")

  // 执行测试和验证
  Bash("npm test")
  Bash("npm run lint")
  Bash("npm run build")

  // 跟踪进度
  TodoWrite { todos: [
    { content: "完成代码审查", status: "completed", activeForm: "正在完成代码审查" },
    { content: "运行测试套件", status: "completed", activeForm: "正在运行测试套件" },
    { content: "验证安全", status: "completed", activeForm: "正在验证安全" },
    { content: "准备合并", status: "pending", activeForm: "准备合并" }
  ]}
```

---

## 🆘 故障排除

### 常见问题

<details>
<summary><strong>问题：审查代理未生成<$strong><$summary>

**解决方案**:
```bash
# 检查群状态
npx ruv-swarm swarm-status

# 验证 GitHub CLI 认证
gh auth status

# 强制重新初始化群
npx ruv-swarm github review-init --pr 123 --force
```

<$details>

<details>
<summary><strong>问题：评论未发布到 PR<$strong><$summary>

**解决方案**:
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

**解决方案**:
```bash
# 对大型 PR 使用增量审查
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
- `github-pr-manager` - 综合的 PR 生命周期管理
- `github-workflow-automation` - 自动化 GitHub 工作流
- `swarm-coordination` - 高级群编排

### 文档
- [GitHub CLI 文档](https:/$cli.github.com$manual/)
- [RUV Swarm 指南](https:/$github.com$ruvnet$ruv-swarm)
- [Claude Flow 集成](https:/$github.com$ruvnet$claude-flow)

### 支持
- GitHub 问题：报告错误和请求功能
- 社区：加入讨论并分享经验
- 示例：浏览示例配置和工作流

---

## 📄 许可证

此技能是 Claude Code Flow 项目的一部分，并遵循 MIT 许可证。

---

**最后更新**：2025-10-19
**版本**：1.0.0
**维护者**：Claude Code Flow 团队
