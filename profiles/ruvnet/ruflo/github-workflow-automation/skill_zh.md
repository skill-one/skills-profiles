# GitHub 工作流自动化技能

## 概述

该技能提供全面的 GitHub Actions 自动化，并具有 AI 群体协调功能。它集成了智能 CI/CD 管道、工作流编排和仓库管理，以创建自我组织、自适应的 GitHub 工作流。

## 快速入门

<details>
<summary>💡 基本用法 - 点击展开$summary>

### 初始化 GitHub 工作流自动化
```bash
# 从简单的流程开始
npx ruv-swarm actions generate-workflow \
  --analyze-codebase \
  --detect-languages \
  --create-optimal-pipeline
```

### 常用命令
```bash
# 优化现有工作流
npx ruv-swarm actions optimize \
  --workflow ".github$workflows$ci.yml" \
  --suggest-parallelization

# 分析失败运行
gh run view <run-id> --json jobs,conclusion | \
  npx ruv-swarm actions analyze-failure \
    --suggest-fixes
```

<$details>

## 核心功能

### 🤖 群体驱动的 GitHub 模式

<details>
<summary>可用的 GitHub 集成模式<$summary>

#### 1. gh-coordinator
**GitHub 工作流编排和协调**
- **协调模式**: 分层
- **最大并行操作**: 10
- **批量优化**: 是
- **适用场景**: 复杂的 GitHub 工作流、多仓库协调

```bash
# 使用示例
npx claude-flow@alpha github gh-coordinator \
  "协调 5 个仓库的跨仓库发布"
```

#### 2. pr-manager
**拉取请求管理和评审协调**
- **评审模式**: 自动化
- **多评审者**: 是
- **冲突解决**: 智能

```bash
# 创建带自动化评审的 PR
gh pr create --title "功能: 新功能" \
  --body "带群体评审的自动化 PR" | \
  npx ruv-swarm actions pr-validate \
    --spawn-agents "linter,tester,security,docs"
```

#### 3. issue-tracker
**问题管理和项目协调**
- **问题工作流**: 自动化
- **标签管理**: 智能
- **进度跟踪**: 实时

```bash
# 创建协调问题工作流
npx claude-flow@alpha github issue-tracker \
  "使用自动化跟踪管理冲刺问题"
```

#### 4. release-manager
**发布协调和部署**
- **发布管道**: 自动化
- **版本控制**: 语义化
- **部署**: 多阶段

```bash
# 自动化发布管理
npx claude-flow@alpha github release-manager \
  "创建 v2.0.0 发布，带变更日志和部署"
```

#### 5. repo-architect
**仓库结构和组织**
- **结构优化**: 是
- **多仓库支持**: 是
- **模板管理**: 高级

```bash
# 优化仓库结构
npx claude-flow@alpha github repo-architect \
  "使用最佳组织结构重构单体仓库"
```

#### 6. code-reviewer
**自动化代码评审和质量保证**
- **评审质量**: 深度
- **安全分析**: 是
- **性能检查**: 自动化

```bash
# 自动化代码评审
gh pr view 123 --json files | \
  npx ruv-swarm actions pr-validate \
    --deep-review \
    --security-scan
```

#### 7. ci-orchestrator
**CI/CD 管道协调**
- **管道管理**: 高级
- **测试协调**: 并行
- **部署**: 自动化

```bash
# 协调 CI/CD 管道
npx claude-flow@alpha github ci-orchestrator \
  "设置并行测试执行和智能缓存"
```

#### 8. security-guardian
**安全和合规管理**
- **安全扫描**: 自动化
- **合规检查**: 持续
- **漏洞管理**: 主动

```bash
# 安全审计
npx ruv-swarm actions security \
  --deep-scan \
  --compliance-check \
  --create-issues
```

<$details>

### 🔧 工作流模板

<details>
<summary>生产就绪的 GitHub Actions 模板<$summary>

#### 1. 智能群體 CI
```yaml
# .github$workflows$swarm-ci.yml
name: 智能群體 CI
on: [push, pull_request]

jobs:
  swarm-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions$checkout@v3

      - name: 初始化群體
        uses: ruvnet$swarm-action@v1
        with:
          topology: mesh
          max-agents: 6

      - name: 分析变更
        run: |
          npx ruv-swarm actions analyze \
            --commit ${{ github.sha }} \
            --suggest-tests \
            --optimize-pipeline
```

#### 2. 多语言检测
```yaml
# .github$workflows$polyglot-swarm.yml
name: 多语言项目处理器
on: push

jobs:
  detect-and-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions$checkout@v3

      - name: 检测语言
        id: detect
        run: |
          npx ruv-swarm actions detect-stack \
            --output json > stack.json

      - name: 动态构建矩阵
        run: |
          npx ruv-swarm actions create-matrix \
            --from stack.json \
            --parallel-builds
```

#### 3. 自适应安全扫描
```yaml
# .github$workflows$security-swarm.yml
name: 智能安全扫描
on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

jobs:
  security-swarm:
    runs-on: ubuntu-latest
    steps:
      - name: 安全分析群體
        run: |
          SECURITY_ISSUES=$(npx ruv-swarm actions security \
            --deep-scan \
            --format json)

          echo "$SECURITY_ISSUES" | jq -r '.issues[]? | @base64' | while read -r issue; do
            _jq() {
              echo ${issue} | base64 --decode | jq -r ${1}
            }
            gh issue create \
              --title "$(_jq '.title')" \
              --body "$(_jq '.body')" \
              --label "security,critical"
          done
```

#### 4. 自愈管道
```yaml
# .github$workflows$self-healing.yml
name: 自愈管道
on: workflow_run

jobs:
  heal-pipeline:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    runs-on: ubuntu-latest
    steps:
      - name: 诊断和修复
        run: |
          npx ruv-swarm actions self-heal \
            --run-id ${{ github.event.workflow_run.id }} \
            --auto-fix-common \
            --create-pr-complex
```

#### 5. 渐进式部署
```yaml
# .github$workflows$smart-deployment.yml
name: 智能部署
on:
  push:
    branches: [main]

jobs:
  progressive-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: 分析风险
        id: risk
        run: |
          npx ruv-swarm actions deploy-risk \
            --changes ${{ github.sha }} \
            --history 30d

      - name: 选择策略
        run: |
          npx ruv-swarm actions deploy-strategy \
            --risk ${{ steps.risk.outputs.level }} \
            --auto-execute
```

#### 6. 性能回归检测
```yaml
# .github$workflows$performance-guard.yml
name: 性能保护
on: pull_request

jobs:
  perf-swarm:
    runs-on: ubuntu-latest
    steps:
      - name: 性能分析
        run: |
          npx ruv-swarm actions perf-test \
            --baseline main \
            --threshold 10% \
            --auto-profile-regression
```

#### 7. PR 验证群體
```yaml
# .github$workflows$pr-validation.yml
name: PR 验证群體
on: pull_request

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: 多代理验证
        run: |
          PR_DATA=$(gh pr view ${{ github.event.pull_request.number }} --json files,labels)

          RESULTS=$(npx ruv-swarm actions pr-validate \
            --spawn-agents "linter,tester,security,docs" \
            --parallel \
            --pr-data "$PR_DATA")

          gh pr comment ${{ github.event.pull_request.number }} \
            --body "$RESULTS"
```

#### 8. 智能发布
```yaml
# .github$workflows$intelligent-release.yml
name: 智能发布
on:
  push:
    tags: ['v*']

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - name: 发布群體
        run: |
          npx ruv-swarm actions release \
            --analyze-changes \
            --generate-notes \
            --create-artifacts \
            --publish-smart
```

<$details>

### 📊 监控与分析

<details>
<summary>工作流分析与优化<$summary>

#### 工作流分析
```bash
# 分析工作流性能
npx ruv-swarm actions analytics \
  --workflow "ci.yml" \
  --period 30d \
  --identify-bottlenecks \
  --suggest-improvements
```

#### 成本优化
```bash
# 优化 GitHub Actions 成本
npx ruv-swarm actions cost-optimize \
  --analyze-usage \
  --suggest-caching \
  --recommend-self-hosted
```

#### 失败模式分析
```bash
# 识别失败模式
npx ruv-swarm actions failure-patterns \
  --period 90d \
  --classify-failures \
  --suggest-preventions
```

#### 资源管理
```bash
# 优化资源使用
npx ruv-swarm actions resources \
  --analyze-usage \
  --suggest-runners \
  --cost-optimize
```

<$details>

## 高级功能

### 🧪 动态测试策略

<details>
<summary>智能测试选择与执行<$summary>

#### 智能测试选择
```yaml
# 自动选择相关测试
- name: 群體测试选择
  run: |
    npx ruv-swarm actions smart-test \
      --changed-files ${{ steps.files.outputs.all }} \
      --impact-analysis \
      --parallel-safe
```

#### 动态测试矩阵
```yaml
# 从代码分析生成测试矩阵
jobs:
  generate-matrix:
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}
    steps:
      - id: set-matrix
        run: |
          MATRIX=$(npx ruv-swarm actions test-matrix \
            --detect-frameworks \
            --optimize-coverage)
          echo "matrix=${MATRIX}" >> $GITHUB_OUTPUT

  test:
    needs: generate-matrix
    strategy:
      matrix: ${{fromJson(needs.generate-matrix.outputs.matrix)}}
```

#### 智能并行化
```bash
# 确定最佳并行化
npx ruv-swarm actions parallel-strategy \
  --analyze-dependencies \
  --time-estimates \
  --cost-aware
```

<$details>

### 🔮 预测分析

<details>
<summary>AI 驱动的工 作流预测<$summary>

#### 预测失败
```bash
# 预测潜在失败
npx ruv-swarm actions predict \
  --analyze-history \
  --identify-risks \
  --suggest-preventive
```

#### 工作流建议
```bash
# 获取工作流建议
npx ruv-swarm actions recommend \
  --analyze-repo \
  --suggest-workflows \
  --industry-best-practices
```

#### 自动化优化
```bash
# 持续优化工作流
npx ruv-swarm actions auto-optimize \
  --monitor-performance \
  --apply-improvements \
  --track-savings
```

<$details>

### 🎯 自定义动作开发

<details>
<summary>构建您自己的群體动作<$summary>

#### 自定义群體动作模板
```javascript
// action.yml
name: '群體自定义动作'
description: '群體驱动的自定义动作'
inputs:
  task:
    description: '群體任务'
    required: true
runs:
  using: 'node16'
  main: 'dist$index.js'

// index.js
const { SwarmAction } = require('ruv-swarm');

async function run() {
  const swarm = new SwarmAction({
    topology: 'mesh',
    agents: ['analyzer', 'optimizer']
  });

  await swarm.execute(core.getInput('task'));
}

run().catch(error => core.setFailed(error.message));
```

<$details>

## 与 Claude-Flow 集成

### 🔄 群體协调模式

<details>
<summary>基于 MCP 的 GitHub 工作流协调<$summary>

#### 初始化 GitHub 群體
```javascript
// 第 1 步: 初始化群體协调
mcp__claude-flow__swarm_init {
  topology: "hierarchical",
  maxAgents: 8
}

// 第 2 步: 生成专用代理
mcp__claude-flow__agent_spawn { type: "coordinator", name: "GitHub 协调器" }
mcp__claude-flow__agent_spawn { type: "reviewer", name: "代码评审器" }
mcp__claude-flow__agent_spawn { type: "tester", name: "QA 代理" }
mcp__claude-flow__agent_spawn { type: "analyst", name: "安全分析师" }

// 第 3 步: 编排 GitHub 工作流
mcp__claude-flow__task_orchestrate {
  task: "完成 PR 评审和合并工作流",
  strategy: "parallel",
  priority: "high"
}
```

#### GitHub 钩子集成
```bash
# 任务前: 设置 GitHub 上下文
npx claude-flow@alpha hooks pre-task \
  --description "PR 评审工作流" \
  --context "pr-123"

# 任务中: 跟踪进度
npx claude-flow@alpha hooks notify \
  --message "完成安全扫描" \
  --type "github-action"

# 任务后: 导出结果
npx claude-flow@alpha hooks post-task \
  --task-id "pr-review-123" \
  --export-github-summary
```

<$details>

### 📦 批量操作

<details>
<summary>并发 GitHub 操作<$summary>

#### 并行 GitHub CLI 命令
```javascript
// 单个消息包含所有 GitHub 操作
[并发执行]:
  Bash("gh issue create --title '功能 A' --body '描述 A' --label 'enhancement'")
  Bash("gh issue create --title '功能 B' --body '描述 B' --label 'enhancement'")
  Bash("gh pr create --title 'PR 1' --head 'feature-a' --base 'main'")
  Bash("gh pr create --title 'PR 2' --head 'feature-b' --base 'main'")
  Bash("gh pr checks 123 --watch")
  TodoWrite { todos: [
    {content: "评审安全扫描结果", status: "pending"},
    {content: "合并已批准的 PR", status: "pending"},
    {content: "更新变更日志", status: "pending"}
  ]}
```

<$details>

## 最佳实践

### 🏗️ 工作流组织

<details>
<summary>组织您的 GitHub 工作流<$summary>

#### 1. 使用可重用工作流
```yaml
# .github$workflows$reusable-swarm.yml
name: 可重用群體工作流
on:
  workflow_call:
    inputs:
      topology:
        required: true
        type: string

jobs:
  swarm-task:
    runs-on: ubuntu-latest
    steps:
      - name: 初始化群體
        run: |
          npx ruv-swarm init --topology ${{ inputs.topology }}
```

#### 2. 实现适当的缓存
```yaml
- name: 缓存群體依赖
  uses: actions$cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-swarm-${{ hashFiles('**$package-lock.json') }}
```

#### 3. 设置适当的时间限制
```yaml
jobs:
  swarm-task:
    timeout-minutes: 30
    steps:
      - name: 群體操作
        timeout-minutes: 10
```

#### 4. 使用工作流依赖
```yaml
jobs:
  setup:
    runs-on: ubuntu-latest

  test:
    needs: setup
    runs-on: ubuntu-latest

  deploy:
    needs: [setup, test]
    runs-on: ubuntu-latest
```

<$details>

### 🔒 安全最佳实践

<details>
<summary>保护您的 GitHub 工作流<$summary>

#### 1. 安全存储配置
```yaml
- name: 设置群體
  env:
    SWARM_CONFIG: ${{ secrets.SWARM_CONFIG }}
    API_KEY: ${{ secrets.API_KEY }}
  run: |
    npx ruv-swarm init --config "$SWARM_CONFIG"
```

#### 2. 使用 OIDC 身份验证
```yaml
permissions:
  id-token: write
  contents: read

- name: 配置 AWS 凭证
  uses: aws-actions$configure-aws-credentials@v2
  with:
    role-to-assume: arn:aws:iam::123456789012:role/GitHubAction
    aws-region: us-east-1
```

#### 3. 实现最小权限
```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
```

#### 4. 审计群體操作
```yaml
- name: 审计群體动作
  run: |
    npx ruv-swarm actions audit \
      --export-logs \
      --compliance-report
```

<$details>

### ⚡ 性能优化

<details>
<summary>最大化工作流性能<$summary>

#### 1. 缓存群體依赖
```yaml
- uses: actions$cache@v3
  with:
    path: |
      ~/.npm
      node_modules
    key: ${{ runner.os }}-swarm-${{ hashFiles('**$package-lock.json') }}
```

#### 2. 使用适当的运行器大小
```yaml
jobs:
  heavy-task:
    runs-on: ubuntu-latest-4-cores
    steps:
      - name: 强烈群體操作
```

#### 3. 实现提前终止
```yaml
- name: 快速失败检查
  run: |
    if ! npx ruv-swarm actions pre-check; then
      echo "Pre-check failed, terminating early"
      exit 1
    fi
```

#### 4. 优化并行执行
```yaml
strategy:
  matrix:
    include:
      - runner: ubuntu-latest
        task: test
      - runner: ubuntu-latest
        task: lint
      - runner: ubuntu-latest
        task: security
  max-parallel: 3
```

<$details>

## 调试与故障排除

### 🐛 调试工具

<details>
<summary>调试 GitHub 工作流问题<$summary>

#### 调试模式
```yaml
- name: 调试群體
  run: |
    npx ruv-swarm actions debug \
      --verbose \
      --trace-agents \
      --export-logs
  env:
    ACTIONS_STEP_DEBUG: true
```

#### 性能分析
```bash
# 分析工作流性能
npx ruv-swarm actions profile \
  --workflow "ci.yml" \
  --identify-slow-steps \
  --suggest-optimizations
```

#### 失败分析
```bash
# 分析失败运行
gh run view <run-id> --json jobs,conclusion | \
  npx ruv-swarm actions analyze-failure \
    --suggest-fixes \
    --auto-retry-flaky
```

#### 日志分析
```bash
# 下载和分析日志
gh run download <run-id>
npx ruv-swarm actions analyze-logs \
  --directory .$logs \
  --identify-errors
```

<$details>

## 真实世界示例

### 🚀 完整工作流

<details>
<summary>生产就绪的集成示例<$summary>

#### 示例 1: 全栈应用 CI/CD
```yaml
name: 全栈 CI/CD 带群體
on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  initialize:
    runs-on: ubuntu-latest
    outputs:
      swarm-id: ${{ steps.init.outputs.swarm-id }}
    steps:
      - id: init
        run: |
          SWARM_ID=$(npx ruv-swarm init --topology mesh --output json | jq -r '.id')
          echo "swarm-id=${SWARM_ID}" >> $GITHUB_OUTPUT

  backend:
    needs: initialize
    runs-on: ubuntu-latest
    steps:
      - uses: actions$checkout@v3
      - name: 后端测试
        run: |
          npx ruv-swarm agents spawn --type tester \
            --task "运行后端测试套件" \
            --swarm-id ${{ needs.initialize.outputs.swarm-id }}

  frontend:
    needs: initialize
    runs-on: ubuntu-latest
    steps:
      - uses: actions$checkout@v3
      - name: 前端测试
        run: |
          npx ruv-swarm agents spawn --type tester \
            --task "运行前端测试套件" \
            --swarm-id ${{ needs.initialize.outputs.swarm-id }}

  security:
    needs: initialize
    runs-on: ubuntu-latest
    steps:
      - uses: actions$checkout@v3
      - name: 安全扫描
        run: |
          npx ruv-swarm agents spawn --type security \
            --task "安全审计" \
            --swarm-id ${{ needs.initialize.outputs.swarm-id }}

  deploy:
    needs: [backend, frontend, security]
    if: github.ref == 'refs$heads$main'
    runs-on: ubuntu-latest
    steps:
      - name: 部署
        run: |
          npx ruv-swarm actions deploy \
            --strategy progressive \
            --swarm-id ${{ needs.initialize.outputs.swarm-id }}
```

#### 示例 2: 单体仓库管理
```yaml
name: 单体仓库协调
on: push

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      packages: ${{ steps.detect.outputs.packages }}
    steps:
      - uses: actions$checkout@v3
        with:
          fetch-depth: 0

      - id: detect
        run: |
          PACKAGES=$(npx ruv-swarm actions detect-changes \
            --monorepo \
            --output json)
          echo "packages=${PACKAGES}" >> $GITHUB_OUTPUT

  build-packages:
    needs: detect-changes
    runs-on: ubuntu-latest
    strategy:
      matrix:
        package: ${{ fromJson(needs.detect-changes.outputs.packages) }}
    steps:
      - name: 构建包
        run: |
          npx ruv-swarm actions build \
            --package ${{ matrix.package }} \
            --parallel-deps
```

#### 示例 3: 多仓库同步
```bash
# 同步多个仓库
npx claude-flow@alpha github sync-coordinator \
  "同步版本更新跨:
   - github.com$org$repo-a
   - github.com$org$repo-b
   - github.com$org$repo-c

   更新依赖关系，对齐版本，创建 PRs"
```

<$details>

## 命令参考

### 📚 快速命令指南

<details>
<summary>所有可用命令<$summary>

#### 工作流生成
```bash
npx ruv-swarm actions generate-workflow [options]
  --analyze-codebase       分析仓库结构
  --detect-languages       检测编程语言
  --create-optimal-pipeline 生成优化工作流
```

#### 优化
```bash
npx ruv-swarm actions optimize [options]
  --workflow <path>        工作流文件路径
  --suggest-parallelization 建议并行执行
  --reduce-redundancy      移除冗余步骤
  --estimate-savings       估计时间和成本节省
```

#### 分析
```bash
npx ruv-swarm actions analyze [options]
  --commit <sha>           分析特定提交
  --suggest-tests          建议测试改进
  --optimize-pipeline      优化管道结构
```

#### 测试
```bash
npx ruv-swarm actions smart-test [options]
  --changed-files <files>  更改的文件
  --impact-analysis        分析测试影响
  --parallel-safe          仅并行安全的测试
```

#### 安全
```bash
npx ruv-swarm actions security [options]
  --deep-scan             深度安全分析
  --format <format>       输出格式 (json$text)
  --create-issues         自动创建 GitHub 问题
```

#### 部署
```bash
npx ruv-swarm actions deploy [options]
  --strategy <type>       部署策略
  --risk <level>          风险评估级别
  --auto-execute          自动执行
```

#### 监控
```bash
npx ruv-swarm actions analytics [options]
  --workflow <name>       要分析的工 作流
  --period <duration>     分析周期
  --identify-bottlenecks  找到瓶颈
  --suggest-improvements  建议改进
```

<$details>

## 集成检查清单

### ✅ 设置验证

<details>
<summary>验证您的设置<$summary>

- [ ] 安装 GitHub CLI (`gh`) 并认证
- [ ] 配置 Git 用户凭证
- [ ] 安装 Node.js v16+
- [ ] 可用 `claude-flow@alpha` 包
- [ ] 仓库具有 `.github$workflows` 目录
- [ ] 仓库启用了 GitHub Actions
- [ ] 配置了必要的密钥
- [ ] 验证运行器权限

#### 快速设置脚本
```bash
#!$bin$bash
# setup-github-automation.sh

# 安装依赖
npm install -g claude-flow@alpha

# 验证 GitHub CLI
gh auth status || gh auth login

# 创建工作流目录
mkdir -p .github$workflows

# 生成初始工作流
npx ruv-swarm actions generate-workflow \
  --analyze-codebase \
  --create-optimal-pipeline > .github$workflows$ci.yml

echo "✅ GitHub 工作流自动化设置完成"
```

<$details>

## 相关技能

- `github-pr-enhancement` - 高级 PR 管理
- `release-coordination` - 发布自动化
- `swarm-coordination` - 多代理编排
- `ci-cd-optimization` - 管道优化

## 支持 & 文档

- **GitHub CLI 文档**: https:/$cli.github.com$manual/
- **GitHub Actions**: https:/$docs.github.com$en$actions
- **Claude-Flow**: https:/$github.com$ruvnet$claude-flow
- **Ruv-Swarm**: https:/$github.com$ruvnet$ruv-swarm

## 版本历史

- **v1.0.0** (2025-01-19): 初始技能整合
  - 合并 workflow-automation.md (441 行)
  - 合并 github-modes.md (146 行)
  - 添加渐进式披露
  - 使用群體协调模式增强
  - 添加全面示例和最佳实践

---

**技能状态**: ✅ 生产就绪
**最后更新**: 2025-01-19
**维护者**: claude-flow 团队
