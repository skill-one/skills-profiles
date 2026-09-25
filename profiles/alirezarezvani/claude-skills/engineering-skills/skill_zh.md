# 工程团队技能

32项生产就绪的工程技能，分为核心工程、安全、AI/ML/数据和专业工具。

## 快速入门

### Claude代码
```
/read engineering-team/skills/senior-fullstack/SKILL.md
```

### Codex CLI
```bash
npx agent-skills-cli add alirezarezvani/claude-skills/engineering-team
```

## 技能概览

### 核心工程 (13项技能)

| 技能 | 文件夹 | 重点 |
|-------|--------|-------|
| 高级架构师 | `senior-architect/` | 系统设计、架构模式 |
| 高级前端 | `senior-frontend/` | React、Next.js、TypeScript、Tailwind |
| 高级后端 | `senior-backend/` | API设计、数据库优化 |
| 高级全栈 | `senior-fullstack/` | 项目脚手架、代码质量 |
| 高级QA | `senior-qa/` | 测试生成、覆盖率分析 |
| 高级DevOps | `senior-devops/` | CI/CD、基础设施、容器 |
| 高级SecOps | `senior-secops/` | 安全运营、漏洞管理 |
| 代码审查员 | `code-reviewer/` | PR审查、代码质量分析 |
| 高级安全 | `senior-security/` | 威胁建模、STRIDE、渗透测试 |
| AWS解决方案架构师 | `aws-solution-architect/` | 无服务器、CloudFormation、成本优化 |
| MS365租户管理员 | `ms365-tenant-manager/` | Microsoft 365管理 |
| TDD指南 | `tdd-guide/` | 测试驱动开发工作流 |
| 技术栈评估员 | `tech-stack-evaluator/` | 技术比较、TCO分析 |

### AI/ML/数据 (5项技能)

| 技能 | 文件夹 | 重点 |
|-------|--------|-------|
| 高级数据科学家 | `senior-data-scientist/` | 统计建模、实验 |
| 高级数据工程师 | `senior-data-engineer/` | 管道、ETL、数据质量 |
| 高级ML工程师 | `senior-ml-engineer/` | 模型部署、MLOps、LLM集成 |
| 高级提示工程师 | `senior-prompt-engineer/` | 提示优化、RAG、代理 |
| 高级计算机视觉 | `senior-computer-vision/` | 物体检测、分割 |

### 专业工具 (5项技能)

| 技能 | 文件夹 | 重点 |
|-------|--------|-------|
| Playwright Pro | `playwright-pro/` | E2E测试 (9个子技能) |
| 自我改进代理 | `self-improving-agent/` | 记忆管理 (5个子技能) |
| Stripe集成 | `stripe-integration-expert/` | 支付集成、webhooks |
| 事件指挥官 | `incident-commander/` | 事件响应工作流 |
| 邮件模板构建器 | `email-template-builder/` | HTML邮件生成 |

## Python工具

30多个脚本，全部仅使用标准库。直接运行：

```bash
python3 <skill>/scripts/<tool>.py --help
```

无需pip安装。脚本包含嵌入式示例用于演示模式。

## 规则

- 仅加载您需要的特定技能SKILL.md，不要批量加载所有32项
- 使用Python工具进行分析和脚手架，而不是人工判断
- 查看CLAUDE.md获取工具使用示例和工作流程
