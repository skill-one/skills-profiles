# Claude Automation 推荐器

分析代码库模式，跨所有可扩展选项推荐定制的 Claude Code 自动化方案。

**此技能为只读模式。** 它分析代码库并输出推荐。它**不会**创建或修改任何文件。用户自行实施推荐或单独请求 Claude 协助构建。

## 输出指南

- **每类推荐 1-2 个**：不要过度推荐 - 每个类别仅展示最值钱的 1-2 个自动化方案
- **如果用户请求特定类型**：仅关注该类型并提供更多选项（3-5 个推荐）
- **超越参考列表**：参考文件包含常见模式，但使用网络搜索查找针对代码库工具、框架和库的推荐
- **告知用户可以请求更多**：最后说明他们可以请求任何特定类别的更多推荐

## 自动化类型概述

| 类型 | 适用于 |
|------|----------|
| **钩子 (Hooks)** | 工具事件上的自动操作（保存时格式化、代码检查、阻止编辑） |
| **子代理 (Subagents)** | 并行运行的专门审查器/分析器 |
| **技能 (Skills)** | 打包的专业知识、工作流和可重复任务（由 Claude 或用户通过 `/skill-name` 调用） |
| **插件 (Plugins)** | 可安装的技能集合 |
| **MCP 服务器** | 外部工具集成（数据库、API、浏览器、文档） |

## 工作流程

### 第一阶段：代码库分析

收集项目上下文：

```bash
# 检测项目类型和工具
ls -la package.json pyproject.toml Cargo.toml go.mod pom.xml 2>/dev/null
cat package.json 2>/dev/null | head -50

# 检查依赖项以推荐 MCP 服务器
cat package.json 2>/dev/null | grep -E '"(react|vue|angular|next|express|fastapi|django|prisma|supabase|convex|stripe)"'

# 检查现有的 Claude Code 配置
ls -la .claude/ CLAUDE.md 2>/dev/null

# 分析项目结构
ls -la src/ app/ lib/ tests/ components/ pages/ api/ 2>/dev/null
```

**关键指标：**

| 类别 | 查找内容 | 告知推荐 |
|----------|------------------|----------------------------|
| 语言/框架 | package.json, pyproject.toml, import 模式 | 钩子, MCP 服务器 |
| 前端堆栈 | React, Vue, Angular, Next.js | Playwright MCP, 前端技能 |
| 后端堆栈 | Express, FastAPI, Django | API 文档工具 |
| 数据库 | Prisma, Supabase, Convex, 原生 SQL | 数据库 / 后端 MCP 服务器 |
| 外部 API | Stripe, OpenAI, AWS SDK | context7 MCP 用于文档 |
| 测试 | Jest, pytest, Playwright 配置 | 测试钩子, 子代理 |
| CI/CD | GitHub Actions, CircleCI | GitHub MCP 服务器 |
| 问题跟踪 | Linear, Jira 引用 | 问题跟踪器 MCP |
| 文档模式 | OpenAPI, JSDoc, 文档字符串 | 文档技能 |

### 第二阶段：生成推荐

根据分析结果，跨所有类别生成推荐：

#### A. MCP 服务器推荐

参考 [references/mcp-servers.md](references/mcp-servers.md) 获取详细模式。

| 代码库信号 | 推荐的 MCP 服务器 |
|-----------------|------------------------|
| 使用流行库 (React, Express 等) | **context7** - 实时文档查询 |
| 前端带 UI 测试需求 | **Playwright** - 浏览器自动化/测试 |
| 使用 Supabase | **Supabase MCP** - 直接数据库操作 |
| 使用 Convex | **Convex MCP** - 实时部署洞察、运行查询/变更、管理环境变量和日志 |
| PostgreSQL/MySQL 数据库 | **Database MCP** - 查询和模式工具 |
| GitHub 仓库 | **GitHub MCP** - 问题、PR、操作 |
| 使用 Linear 跟踪问题 | **Linear MCP** - 问题管理 |
| AWS 基础设施 | **AWS MCP** - 云资源管理 |
| Slack 工作区 | **Slack MCP** - 团队通知 |
| 内存/上下文持久化 | **Memory MCP** - 跨会话内存 |
| Sentry 错误跟踪 | **Sentry MCP** - 错误调查 |
| Docker 容器 | **Docker MCP** - 容器管理 |

#### B. 技能推荐

参考 [references/skills-reference.md](references/skills-reference.md) 获取详细信息。

在 `.claude/skills/<name>/SKILL.md` 中创建技能。一些技能也通过插件提供：

| 代码库信号 | 技能 | 插件 |
|-----------------|-------|--------|
| 构建插件 | skill-development | plugin-dev |
| Git 提交 | commit | commit-commands |
| React/Vue/Angular | frontend-design | frontend-design |
| 自动化规则 | writing-rules | hookify |
| 功能规划 | feature-dev | feature-dev |

**自定义技能创建**（带模板、脚本、示例）：

| 代码库信号 | 创建技能 | 调用方式 |
|-----------------|-----------------|------------|
| API 路由 | **api-doc**（带 OpenAPI 模板） | Both |
| 数据库项目 | **create-migration**（带验证脚本） | User-only |
| 测试套件 | **gen-test**（带示例测试） | User-only |
| 组件库 | **new-component**（带模板） | User-only |
| PR 工作流 | **pr-check**（带清单） | User-only |
| 发布 | **release-notes**（带 git 上下文） | User-only |
| 代码风格 | **project-conventions** | Claude-only |
| Onboarding | **setup-dev**（带前置脚本） | User-only |

#### C. 钩子推荐

参考 [references/hooks-patterns.md](references/hooks-patterns.md) 获取配置。

| 代码库信号 | 推荐的钩子 |
|-----------------|------------------|
| 配置了 Prettier | PostToolUse: 编辑时自动格式化 |
| 配置了 ESLint/Ruff | PostToolUse: 编辑时自动代码检查 |
| TypeScript 项目 | PostToolUse: 编辑时类型检查 |
| 测试目录存在 | PostToolUse: 运行相关测试 |
| 存在 `.env` 文件 | PreToolUse: 阻止 `.env` 文件编辑 |
| 存在锁定文件 | PreToolUse: 阻止锁定文件编辑 |
| 安全敏感代码 | PreToolUse: 需要确认 |

#### D. 子代理推荐

参考 [references/subagent-templates.md](references/subagent-templates.md) 获取模板。

| 代码库信号 | 推荐的子代理 |
|-----------------|---------------------|
| 大型代码库 (>500 个文件) | **code-reviewer** - 并行代码审查 |
| 认证/支付代码 | **security-reviewer** - 安全审计 |
| API 项目 | **api-documenter** - OpenAPI 生成 |
| 性能关键 | **performance-analyzer** - 瓶颈检测 |
| 前端密集型 | **ui-reviewer** - 可访问性审查 |
| 需要更多测试 | **test-writer** - 测试生成 |

#### E. 插件推荐

参考 [references/plugins-reference.md](references/plugins-reference.md) 获取可用插件。

| 代码库信号 | 推荐的插件 |
|-----------------|-------------------|
| 一般生产力 | **anthropic-agent-skills** - 核心技能包 |
| 文档工作流 | 安装 docx, xlsx, pdf 技能 |
| 前端开发 | **frontend-design** 插件 |
| 构建 AI 工具 | **mcp-builder** 用于 MCP 开发 |

### 第三阶段：输出推荐报告

清晰格式化推荐。**每个类别仅包含 1-2 个推荐** - 对此特定代码库最有价值的推荐。跳过与当前代码库不相关的类别。

```markdown
## Claude Code 自动化推荐

我分析了您的代码库，并确定了每个类别的顶级自动化方案。以下是每个类型最值钱的 1-2 个推荐：

### 代码库概况
- **类型**：[检测到的语言/运行时]
- **框架**：[检测到的框架]
- **关键库**：[检测到的相关库]

---

### 🔌 MCP 服务器

#### context7
**原因**：[基于检测到的库的具体原因]
**安装**：`claude mcp add context7`

---

### 🎯 技能

#### [技能名称]
**原因**：[具体原因]
**创建**：`.claude/skills/[name]/SKILL.md`
**调用方式**：User-only / Both / Claude-only
**也提供在**：[插件名称] 插件（如果适用）
```yaml
---
name: [技能名称]
description: [它做什么]
disable-model-invocation: true  # for user-only
---
```

---

### ⚡ 钩子

#### [钩子名称]
**原因**：[基于检测到的配置的具体原因]
**位置**：`.claude/settings.json`

---

### 🤖 子代理

#### [代理名称]
**原因**：[基于代码库模式的具体原因]
**位置**：`.claude/agents/[name].md`

---

**需要更多？** 请求任何特定类别的额外推荐（例如，“显示更多 MCP 服务器选项”或“其他钩子能帮助什么？”）。

**需要帮助实施这些？** 直接请求，我可以帮助您设置上述任何推荐。
```

## 决策框架

### 推荐 MCP 服务器时
- 需要外部服务集成（数据库、API）
- 库/SDK 的文档查询
- 浏览器自动化或测试
- 团队工具集成（GitHub, Linear, Slack）
- 云基础设施管理

### 推荐技能时

- 文档生成（docx, xlsx, pptx, pdf — 也提供在插件中）
- 频繁重复的提示或工作流
- 带参数的项目特定任务
- 将模板或脚本应用于任务（技能可以捆绑支持文件）
- 通过 `/skill-name` 快速执行操作
- 应该独立运行的工作流（`context: fork`）

**调用控制：**
- `disable-model-invocation: true` — 仅用户（用于副作用：部署、提交、发送）
- `user-invocable: false` — 仅 Claude（用于背景知识）
- 默认（省略两者） — Both 可以调用

### 推荐钩子时
- 重复的编辑后操作（格式化、代码检查）
- 保护规则（阻止敏感文件编辑）
- 验证检查（测试、类型检查）

### 推荐子代理时
- 需要专门知识（安全、性能）
- 并行审查工作流
- 背景质量检查

### 推荐插件时
- 需要多个相关技能
- 想要预打包的自动化包
- 团队标准化

---

## 配置技巧

### MCP 服务器设置

**团队共享**：将 `.mcp.json` 提交到仓库，以便整个团队获得相同的 MCP 服务器

**调试**：使用 `--mcp-debug` 标志识别配置问题

**推荐前提：**
- GitHub CLI (`gh`) - 启用原生 GitHub 操作
- Puppeteer/Playwright CLI - 用于浏览器 MCP 服务器

### 无头模式（用于 CI/自动化）

推荐无头 Claude 用于自动化管道：

```bash
# 预提交钩子示例
claude -p "fix lint errors in src/" --allowedTools Edit,Write

# CI 管道带结构化输出
claude -p "<prompt>" --output-format stream-json | your_command
```

### 钩子权限

在 `.claude/settings.json` 中配置允许的工具：

```json
{
  "permissions": {
    "allow": ["Edit", "Write", "Bash(npm test:*)", "Bash(git commit:*)"]
  }
}
```
