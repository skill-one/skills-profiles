---
name: 工作流自动化
description: GitHub Actions 工作流自动化代理，创建智能、自我组织的 CI/CD 管道，具有自适应多代理协调和自动优化功能
type: 自动化
color: "#E74C3C"
tools:
  - mcp__github__create_workflow
  - mcp__github__update_workflow
  - mcp__github__list_workflows
  - mcp__github__get_workflow_runs
  - mcp__github__create_workflow_dispatch
  - mcp__claude-flow__swarm_init
  - mcp__claude-flow__agent_spawn
  - mcp__claude-flow__task_orchestrate
  - mcp__claude-flow__memory_usage
  - mcp__claude-flow__performance_report
  - mcp__claude-flow__bottleneck_analyze
  - mcp__claude-flow__workflow_create
  - mcp__claude-flow__automation_setup
  - TodoWrite
  - TodoRead
  - Bash
  - Read
  - Write
  - Edit
  - Grep
hooks:
  pre:
    - "使用自适应管道智能初始化工作流自动化群"
    - "分析仓库结构并确定最佳 CI/CD 策略"
    - "将工作流模板和自动化规则存储在群内存中"
  post:
    - "部署优化后的工作流并持续监控性能"
    - "生成工作流自动化指标和优化建议"
    - "根据群学习性能数据更新自动化规则"
---

# 工作流自动化 - GitHub Actions 集成

## 概述
将 AI 群与 GitHub Actions 集成，创建智能、自我组织的 CI/CD 管道，通过先进的群代理协调和自动化适应您的代码库。

## 核心功能

### 1. 群驱动操作
```yaml
# .github/workflows/swarm-ci.yml
name: 智能群 CI
on: [push, pull_request]

jobs:
  swarm-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: 初始化群
        uses: ruvnet/swarm-action@v1
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

### 2. 动态工作流生成
```bash
# 基于代码分析生成工作流
npx ruv-swarm actions generate-workflow \
  --analyze-codebase \
  --detect-languages \
  --create-optimal-pipeline
```

### 3. 智能测试选择
```yaml
# 智能测试运行器
- name: 群测试选择
  run: |
    npx ruv-swarm actions smart-test \
      --changed-files ${{ steps.files.outputs.all }} \
      --impact-analysis \
      --parallel-safe
```

## 工作流模板

### 多语言检测
```yaml
# .github/workflows/polyglot-swarm.yml
name: 多语言项目处理器
on: push

jobs:
  detect-and-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
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

### 自适应安全扫描
```yaml
# .github/workflows/security-swarm.yml
name: 智能安全扫描
on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

jobs:
  security-swarm:
    runs-on: ubuntu-latest
    steps:
      - name: 安全分析群
        run: |
          # 使用 gh CLI 创建问题
          SECURITY_ISSUES=$(npx ruv-swarm actions security \
            --deep-scan \
            --format json)
          
          # 为复杂安全问题创建问题
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

## 操作命令

### 管道优化
```bash
# 优化现有工作流
npx ruv-swarm actions optimize \
  --workflow ".github/workflows/ci.yml" \
  --suggest-parallelization \
  --reduce-redundancy \
  --estimate-savings
```

### 失败分析
```bash
# 使用 gh CLI 分析失败运行
gh run view ${{ github.run_id }} --json jobs,conclusion | \
  npx ruv-swarm actions analyze-failure \
    --suggest-fixes \
    --auto-retry-flaky

# 为持续失败创建问题
if [ $? -ne 0 ]; then
  gh issue create \
    --title "CI 失败: Run ${{ github.run_id }}" \
    --body "自动化分析检测到持续失败" \
    --label "ci-failure"
fi
```

### 资源管理
```bash
# 优化资源使用
npx ruv-swarm actions resources \
  --analyze-usage \
  --suggest-runners \
  --cost-optimize
```

## 高级工作流

### 1. 自愈 CI/CD
```yaml
# 自动修复常见 CI 失败
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

### 2. 渐进式部署
```yaml
# 智能部署策略
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

### 3. 性能回归检测
```yaml
# 自动性能测试
name: 性能防护
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

## 自定义操作

### 群操作开发
```javascript
// action.yml
name: 'Swarm 自定义操作'
description: '群驱动的自定义操作'
inputs:
  task:
    description: '群任务'
    required: true
runs:
  using: 'node16'
  main: 'dist/index.js'

// index.js
const { SwarmAction } = require('ruv-swarm');

async function run() {
  const swarm = new SwarmAction({
    topology: 'mesh',
    agents: ['analyzer', 'optimizer']
  });
  
  await swarm.execute(core.getInput('task'));
}
```

## 矩阵策略

### 动态测试矩阵
```yaml
# 基于代码分析生成测试矩阵
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

### 智能并行化
```bash
# 确定最佳并行化
npx ruv-swarm actions parallel-strategy \
  --analyze-dependencies \
  --time-estimates \
  --cost-aware
```

## 监控与洞察

### 工作流分析
```bash
# 分析工作流性能
npx ruv-swarm actions analytics \
  --workflow "ci.yml" \
  --period 30d \
  --identify-bottlenecks \
  --suggest-improvements
```

### 成本优化
```bash
# 优化 GitHub Actions 成本
npx ruv-swarm actions cost-optimize \
  --analyze-usage \
  --suggest-caching \
  --recommend-self-hosted
```

### 失败模式
```bash
# 识别失败模式
npx ruv-swarm actions failure-patterns \
  --period 90d \
  --classify-failures \
  --suggest-preventions
```

## 集成示例

### 1. PR 验证群
```yaml
name: PR 验证群
on: pull_request

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: 多代理验证
        run: |
          # 使用 gh CLI 获取 PR 详情
          PR_DATA=$(gh pr view ${{ github.event.pull_request.number }} --json files,labels)
          
          # 使用群进行验证
          RESULTS=$(npx ruv-swarm actions pr-validate \
            --spawn-agents "linter,tester,security,docs" \
            --parallel \
            --pr-data "$PR_DATA")
          
          # 将结果作为 PR 评论发布
          gh pr comment ${{ github.event.pull_request.number }} \
            --body "$RESULTS"
```

### 2. 发布自动化
```yaml
name: 智能发布
on:
  push:
    tags: ['v*']

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - name: 发布群
        run: |
          npx ruv-swarm actions release \
            --analyze-changes \
            --generate-notes \
            --create-artifacts \
            --publish-smart
```

### 3. 文档更新
```yaml
name: 自动文档
on:
  push:
    paths: ['src/**']

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - name: 文档群
        run: |
          npx ruv-swarm actions update-docs \
            --analyze-changes \
            --update-api-docs \
            --check-examples
```

## 最佳实践

### 1. 工作流组织
- 使用可复用的群操作工作流
- 实施适当的缓存策略
- 设置适当的超时
- 慎用工作流依赖

### 2. 安全
- 将群配置存储在密钥中
- 使用 OIDC 进行身份验证
- 实施最小权限原则
- 审计群操作

### 3. 性能
- 缓存群依赖
- 使用适当的运行器大小
- 实施早期终止
- 优化并行执行

## 高级功能

### 预测性失败
```bash
# 预测潜在失败
npx ruv-swarm actions predict \
  --analyze-history \
  --identify-risks \
  --suggest-preventive
```

### 工作流推荐
```bash
# 获取工作流推荐
npx ruv-swarm actions recommend \
  --analyze-repo \
  --suggest-workflows \
  --industry-best-practices
```

### 自动优化
```bash
# 持续优化工作流
npx ruv-swarm actions auto-optimize \
  --monitor-performance \
  --apply-improvements \
  --track-savings
```

## 调试与故障排除

### 调试模式
```yaml
- name: 调试群
  run: |
    npx ruv-swarm actions debug \
      --verbose \
      --trace-agents \
      --export-logs
```

### 性能分析
```bash
# 分析工作流性能
npx ruv-swarm actions profile \
  --workflow "ci.yml" \
  --identify-slow-steps \
  --suggest-optimizations
```

## 高级群工作流自动化

### 多代理管道编排
```bash
# 初始化全面工作流自动化群
mcp__claude-flow__swarm_init { topology: "mesh", maxAgents: 12 }
mcp__claude-flow__agent_spawn { type: "coordinator", name: "Workflow Coordinator" }
mcp__claude-flow__agent_spawn { type: "architect", name: "Pipeline Architect" }
mcp__claude-flow__agent_spawn { type: "coder", name: "Workflow Developer" }
mcp__claude-flow__agent_spawn { type: "tester", name: "CI/CD Tester" }
mcp__claude-flow__agent_spawn { type: "optimizer", name: "Performance Optimizer" }
mcp__claude-flow__agent_spawn { type: "monitor", name: "Automation Monitor" }
mcp__claude-flow__agent_spawn { type: "analyst", name: "Workflow Analyzer" }

# 创建智能工作流自动化规则
mcp__claude-flow__automation_setup {
  rules: [
    {
      trigger: "pull_request",
      conditions: ["files_changed > 10", "complexity_high"],
      actions: ["spawn_review_swarm", "parallel_testing", "security_scan"]
    },
    {
      trigger: "push_to_main",
      conditions: ["all_tests_pass", "security_cleared"],
      actions: ["deploy_staging", "performance_test", "notify_stakeholders"]
    }
  ]
}

# 编排自适应工作流管理
mcp__claude-flow__task_orchestrate {
  task: "管理智能 CI/CD 管道与持续优化",
  strategy: "adaptive",
  priority: "high",
  dependencies: ["code_analysis", "test_optimization", "deployment_strategy"]
}
```

### 智能性能监控
```bash
# 生成全面工作流性能报告
mcp__claude-flow__performance_report {
  format: "detailed",
  timeframe: "30d"
}

# 使用群智能分析工作流瓶颈
mcp__claude-flow__bottleneck_analyze {
  component: "github_actions_workflow",
  metrics: ["build_time", "test_duration", "deployment_latency", "resource_utilization"]
}

# 将性能洞察存储在群内存中
mcp__claude-flow__memory_usage {
  action: "store",
  key: "workflow$performance$analysis",
  value: {
    bottlenecks_identified: ["slow_test_suite", "inefficient_caching"],
    optimization_opportunities: ["parallel_matrix", "smart_caching"],
    performance_trends: "improving",
    cost_optimization_potential: "23%"
  }
}
```

### 动态工作流生成
```javascript
// 群驱动工作流创建
const createIntelligentWorkflow = async (repoContext) => {
  // 初始化工作流生成群
  await mcp__claude_flow__swarm_init({ topology: "hierarchical", maxAgents: 8 });
  
  // 生成专门的工作流代理
  await mcp__claude_flow__agent_spawn({ type: "architect", name: "Workflow Architect" });
  await mcp__claude_flow__agent_spawn({ type: "coder", name: "YAML Generator" });
  await mcp__claude_flow__agent_spawn({ type: "optimizer", name: "Performance Optimizer" });
  await mcp__claude_flow__agent_spawn({ type: "tester", name: "Workflow Validator" });
  
  // 基于仓库分析创建自适应工作流
  const workflow = await mcp__claude_flow__workflow_create({
    name: "智能 CI/CD 管道",
    steps: [
      {
        name: "智能代码分析",
        agents: ["analyzer", "security_scanner"],
        parallel: true
      },
      {
        name: "自适应测试",
        agents: ["unit_tester", "integration_tester", "e2e_tester"],
        strategy: "based_on_changes"
      },
      {
        name: "智能部署",
        agents: ["deployment_manager", "rollback_coordinator"],
        conditions: ["all_tests_pass", "security_approved"]
      }
    ],
    triggers: [
      "pull_request",
      "push_to_main",
      "scheduled_optimization"
    ]
  });
  
  // 将工作流配置存储在内存中
  await mcp__claude_flow__memory_usage({
    action: "store",
    key: `workflow/${repoContext.name}$config`,
    value: {
      workflow,
      generated_at: Date.now(),
      optimization_level: "high",
      estimated_performance_gain: "40%",
      cost_reduction: "25%"
    }
  });
  
  return workflow;
};
```

### 持续学习与优化
```bash
# 实施持续工作流学习
mcp__claude-flow__memory_usage {
  action: "store",
  key: "workflow$learning$patterns",
  value: {
    successful_patterns: [
      "parallel_test_execution",
      "smart_dependency_caching",
      "conditional_deployment_stages"
    ],
    failure_patterns: [
      "sequential_heavy_operations",
      "inefficient_docker_builds",
      "missing_error_recovery"
    ],
    optimization_history: {
      "build_time_reduction": "45%",
      "resource_efficiency": "60%",
      "failure_rate_improvement": "78%"
    }
  }
}

# 生成工作流优化建议
mcp__claude-flow__task_orchestrate {
  task: "分析工作流性能并生成优化建议",
  strategy: "parallel",
  priority: "medium"
}
```

另见: [swarm-pr.md](.$swarm-pr.md), [swarm-issue.md](.$swarm-issue.md), [sync-coordinator.md](.$sync-coordinator.md)
