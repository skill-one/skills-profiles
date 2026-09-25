# 工程高级技能（强力级）

37项高级工程技能，用于复杂架构、自动化、可靠性和平台运维。

## 快速入门

### Claude代码
```
/read engineering/skills/agent-designer/SKILL.md
```

### Codex CLI
```bash
npx agent-skills-cli add alirezarezvani/claude-skills/engineering
```

## 技能概览

| 技能 | 文件夹 | 重点 |
|------|--------|------|
| 代理设计器 | `agent-designer/` | 多代理架构：规划、模式生成、评估 |
| 代理工作流设计器 | `agent-workflow-designer/` | 工作流编排脚手架 |
| API设计审查器 | `api-design-reviewer/` | REST/GraphQL校验、破坏性变更 |
| API测试套件构建器 | `api-test-suite-builder/` | API测试生成 |
| 浏览器自动化 | `browser-automation/` | Playwright/Selenium自动化模式 |
| 变更日志生成器 | `changelog-generator/` | 变更日志、语义版本提升、热修复/回滚规范 |
| 混沌工程 | `chaos-engineering/` | 实验设计、影响范围、事后分析 |
| CI/CD流水线构建器 | `ci-cd-pipeline-builder/` | 流水线生成 |
| 代码库入职 | `codebase-onboarding/` | 新开发者入职指南 |
| 数据库设计器 | `database-designer/` | 模式分析、索引优化、迁移 |
| 数据库模式设计器 | `database-schema-designer/` | ER图、范式化 |
| 依赖审计器 | `dependency-auditor/` | 依赖安全扫描 |
| 环境密钥管理器 | `env-secrets-manager/` | 密钥轮换、保险库 |
| 功能标志架构师 | `feature-flags-architect/` | 标志债务、发布计划、关闭开关 |
| 聚焦修复 | `focused-fix/` | 系统性功能/模块修复 |
| 全页截图 | `full-page-screenshot/` | 全页捕获工具 |
| Git工作树管理器 | `git-worktree-manager/` | 并行分支工作流 |
| 面试系统设计器 | `interview-system-designer/` | 招聘流程设计 |
| Kubernetes操作器 | `kubernetes-operator/` | CRD验证、reconcile校验 |
| MCP服务器构建器 | `mcp-server-builder/` | MCP工具创建 |
| 迁移架构师 | `migration-architect/` | 系统迁移规划 |
| 单一仓库导航器 | `monorepo-navigator/` | 单一仓库工具 |
| 可观测性设计器 | `observability-designer/` | 仪表盘、告警噪音（SLOs → slo-architect） |
| 性能分析器 | `performance-profiler/` | CPU、内存、负载分析 |
| PR审查专家 | `pr-review-expert/` | 拉取请求分析 |
| RAG架构师 | `rag-architect/` | RAG设计、分块、检索评估 |
| 运维手册生成器 | `runbook-generator/` | 运维手册 |
| 密钥保险库管理器 | `secrets-vault-manager/` | 保险库模式、HCL |
| 自我评估 | `self-eval/` | 诚实工作质量评分 |
| 发版门禁 | `ship-gate/` | 预生产审计（89项检查） |
| 技能安全审计器 | `skill-security-auditor/` | 技能漏洞扫描 |
| 技能测试器 | `skill-tester/` | 技能质量评估 |
| SLO架构师 | `slo-architect/` | SLO/SLI设计、错误预算、消耗率告警 |
| 规范驱动工作流 | `spec-driven-workflow/` | 规范优先开发门禁 |
| SQL数据库助手 | `sql-database-assistant/` | 查询优化、4种方言 |
| TC追踪器 | `tc-tracker/` | 任务上下文生命周期+交接 |
| 技术债务追踪器 | `tech-debt-tracker/` | 债务扫描→优先级→仪表盘 |

注意：发布管理已合并到`changelog-generator/`（版本提升+热修复/回滚流程现在都在那里）。

## 规则

- 仅加载您需要的特定技能SKILL.md
- 这些是高级技能——根据需要与`engineering-team/`核心技能结合使用
