---
name: engineering-advanced-skills
description: 37项高级工程智能体技能索引，适用于 Claude Code、Codex、Gemini CLI、Cursor 和 OpenClaw。在浏览或从“强力”（POWERFUL）级别的工程技能中进行选择时使用：包括智能体设计、RAG、MCP 服务器、CI/CD、数据库设计、可观测性、安全审计、变更日志/发布自动化、可靠性（SLO/混沌工程/特性开关/Operator）以及平台运维。
---

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
|-------|--------|-------|
| Agent Designer | `agent-designer/` | 多智能体架构：规划、模式生成、评估 |
| Agent Workflow Designer | `agent-workflow-designer/` | 工作流编排脚手架 |
| API Design Reviewer | `api-design-reviewer/` | REST/GraphQL检查、破坏性变更 |
| API Test Suite Builder | `api-test-suite-builder/` | API测试生成 |
| Browser Automation | `browser-automation/` | Playwright/Selenium自动化模式 |
| Changelog Generator | `changelog-generator/` | 更改日志、语义版本提升、热修复/回滚规范 |
| Chaos Engineering | `chaos-engineering/` | 实验设计、影响范围、事后分析 |
| CI/CD Pipeline Builder | `ci-cd-pipeline-builder/` | 管道生成 |
| Codebase Onboarding | `codebase-onboarding/` | 新开发者入职指南 |
| Database Designer | `database-designer/` | 模式分析、索引优化、迁移 |
| Database Schema Designer | `database-schema-designer/` | ERD、规范化 |
| Dependency Auditor | `dependency-auditor/` | 依赖安全扫描 |
| Env Secrets Manager | `env-secrets-manager/` | 密钥轮换、保险库 |
| Feature Flags Architect | `feature-flags-architect/` | 标志债务、发布计划、紧急停止开关 |
| Focused Fix | `focused-fix/` | 系统性功能/模块修复 |
| Full Page Screenshot | `full-page-screenshot/` | 全页截图工具 |
| Git Worktree Manager | `git-worktree-manager/` | 并行分支工作流 |
| Interview System Designer | `interview-system-designer/` | 招聘流程设计 |
| Kubernetes Operator | `kubernetes-operator/` | CRD验证、reconcile检查 |
| MCP Server Builder | `mcp-server-builder/` | MCP工具创建 |
| Migration Architect | `migration-architect/` | 系统迁移规划 |
| Monorepo Navigator | `monorepo-navigator/` | 单一代码库工具 |
| Observability Designer | `observability-designer/` | 仪表盘、告警噪音（SLOs → slo-architect） |
| Performance Profiler | `performance-profiler/` | CPU、内存、负载分析 |
| PR Review Expert | `pr-review-expert/` | 拉取请求分析 |
| RAG Architect | `rag-architect/` | RAG设计、分块、检索评估 |
| Runbook Generator | `runbook-generator/` | 运维手册 |
| Secrets Vault Manager | `secrets-vault-manager/` | 保险库模式、HCL |
| Self-Eval | `self-eval/` | 诚实工作质量评分 |
| Ship Gate | `ship-gate/` | 生产前审计（89项检查） |
| Skill Security Auditor | `skill-security-auditor/` | 技能漏洞扫描 |
| Skill Tester | `skill-tester/` | 技能质量评估 |
| SLO Architect | `slo-architect/` | SLO/SLI设计、错误预算、消耗率警报 |
| Spec-Driven Workflow | `spec-driven-workflow/` | 规格优先开发门禁 |
| SQL Database Assistant | `sql-database-assistant/` | 查询优化、4种方言 |
| TC Tracker | `tc-tracker/` | 任务上下文生命周期+交接 |
| Tech Debt Tracker | `tech-debt-tracker/` | 债务扫描→优先级→仪表盘 |

注意：发布管理已合并到`changelog-generator/`（版本提升+热修复/回滚流程现在都在那里）。

## 规则

- 仅加载您需要的特定技能SKILL.md
- 这些是高级技能——根据需要与`engineering-team/`核心技能结合使用
