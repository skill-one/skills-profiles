# 高级全栈

全栈开发技能，包含项目脚手架和代码质量分析工具。

---

## 目录

- [触发短语](#触发短语)
- [工具](#工具)
- [工作流](#工作流)
- [参考指南](#参考指南)

---

## 触发短语

当您听到以下内容时，请使用此技能：
- "搭建一个新项目"
- "创建一个 Next.js 应用"
- "使用 React 设置 FastAPI"
- "分析代码质量"
- "检查代码库中的安全问题"
- "我应该使用什么技术栈"
- "搭建一个全栈项目"
- "生成项目样板"

---

## 工具

### 决策引擎

确定性配置文件选择器。根据四个假设（团队规模、开发周期、面向用户、预算）以及可选的流量/敏感性输入，对四个内置配置文件进行排序，并返回匹配的配置文件及其 SLO 底线和命名审批链。如果没有提供四个必需的输入，则拒绝推荐配置文件。

**使用方法：**

```bash
# 查看所有选项
python scripts/fullstack_decision_engine.py --help

# 使用示例输入运行
python scripts/fullstack_decision_engine.py --sample

# 从实际输入中选择配置文件
python scripts/fullstack_decision_engine.py \
    --team-size-12mo 8 --cadence daily --user-facing true --budget 5000 \
    --traffic-p99-rps 50 --data-sensitivity pii-only

# 为下游工具生成 JSON 输出
python scripts/fullstack_decision_engine.py --sample --output json
```

返回：匹配的配置文件名称、分数、匹配/违反的约束、技术栈推荐、反推荐、SLO 底线、命名审批链以及规范引用。

该引擎编码了对话式 grill 所处理的相同矩阵——当输入已知时，直接使用它；或通过 `cs-fullstack-engineer` 代理进行逐个问题的 grill。

---

### 项目脚手架生成器

生成全栈项目结构和样板代码。

**支持的模板：**
- `nextjs` - Next.js 14+ with App Router, TypeScript, Tailwind CSS
- `fastapi-react` - FastAPI 后端 + React 前端 + PostgreSQL
- `mern` - MongoDB, Express, React, Node.js with TypeScript
- `django-react` - Django REST Framework + React 前端

**使用方法：**

```bash
# 列出可用模板
python scripts/project_scaffolder.py --list-templates

# 创建 Next.js 项目
python scripts/project_scaffolder.py nextjs my-app

# 创建 FastAPI + React 项目
python scripts/project_scaffolder.py fastapi-react my-api

# 创建 MERN 技术栈项目
python scripts/project_scaffolder.py mern my-project

# 创建 Django + React 项目
python scripts/project_scaffolder.py django-react my-app

# 指定输出目录
python scripts/project_scaffolder.py nextjs my-app --output ./projects

# JSON 输出
python scripts/project_scaffolder.py nextjs my-app --json
```

**参数：**

| 参数 | 描述 |
|-----------|-------------|
| `template` | 模板名称 (nextjs, fastapi-react, mern, django-react) |
| `project_name` | 新项目目录的名称 |
| `--output, -o` | 输出目录 (默认：当前目录) |
| `--list-templates, -l` | 列出所有可用模板 |
| `--json` | 以 JSON 格式输出 |

**输出包括：**
- 项目结构以及所有必要的文件
- 包配置 (package.json, requirements.txt)
- TypeScript 配置
- Docker 和 docker-compose 设置
- 环境文件模板
- 运行项目的下一步操作

---

### 代码质量分析器

分析全栈代码库中的质量问题。

**分析类别：**
- 安全漏洞 (硬编码的密钥、注入风险)
- 代码复杂度指标 (圈复杂度、嵌套深度)
- 依赖健康度 (过时的包、已知的 CVE)
- 测试覆盖率估计
- 文档质量

**使用方法：**

```bash
# 分析当前目录
python scripts/code_quality_analyzer.py .

# 分析特定项目
python scripts/code_quality_analyzer.py /path/to/project

# 显示详细输出的分析
python scripts/code_quality_analyzer.py . --verbose

# JSON 输出
python scripts/code_quality_analyzer.py . --json

# 将报告保存到文件
python scripts/code_quality_analyzer.py . --output report.json
```

**参数：**

| 参数 | 描述 |
|-----------|-------------|
| `project_path` | 项目目录路径 (默认：当前目录) |
| `--verbose, -v` | 显示详细发现 |
| `--json` | 以 JSON 格式输出 |
| `--output, -o` | 将报告写入文件 |

**输出包括：**
- 总分 (0-100) 及字母等级
- 按严重性分类的安全问题 (关键、高、中、低)
- 复杂度高的文件
- 有漏洞的依赖项及 CVE 引用
- 测试覆盖率估计
- 文档完整性
- 优先级建议

**示例输出：**

```
============================================================
代码质量分析报告
============================================================

总分：75/100 (等级：C)
分析的文件数：45
总行数：12,500

--- 安全性 ---
  关键：1
  高：2
  中：5

--- 复杂度 ---
  平均复杂度：8.5
  复杂度高的文件：3

--- 建议 ---
1. [P0] 安全性
   问题：检测到潜在的硬编码密钥
   操作：在第 42 行删除或保护敏感数据
```

---

## 工作流

### 工作流 1：开始新项目

1. 根据需求选择合适的技术栈（参考技术栈决策矩阵）
2. 搭建项目结构
3. 验证搭建：确认 `package.json`（或 `requirements.txt`）存在
4. 运行初始质量检查——在继续之前解决任何 P0 问题
5. 设置开发环境

```bash
# 1. 搭建项目
python scripts/project_scaffolder.py nextjs my-saas-app

# 2. 验证搭建是否成功
ls my-saas-app/package.json

# 3. 导航并安装
cd my-saas-app
npm install

# 4. 配置环境
cp .env.example .env.local

# 5. 运行质量检查
python scripts/code_quality_analyzer.py .

# 6. 开始开发
npm run dev
```

### 工作流 2：审计现有代码库

1. 运行代码质量分析
2. 审查安全发现——立即修复所有 P0（关键）问题
3. 重新运行分析器以确认 P0 问题已解决
4. 创建 P1/P2 问题的工单

```bash
# 1. 全部分析
python scripts/code_quality_analyzer.py /path/to/project --verbose

# 2. 生成详细报告
python scripts/code_quality_analyzer.py /path/to/project --json --output audit.json

# 3. 修复 P0 问题后，重新运行以验证
python scripts/code_quality_analyzer.py /path/to/project --verbose
```

### 工作流 3：技术栈选择

使用技术栈指南评估选项：

1. **需要 SEO 吗？** → Next.js with SSR
2. **后端以 API 为主？** → 分离 FastAPI 或 NestJS
3. **需要实时功能？** → 添加 WebSocket 层
4. **团队专业知识** → 根据团队技能匹配技术栈

参考 `references/tech_stack_guide.md` 获取详细比较。

---

## 参考指南

### 架构模式 (`references/architecture_patterns.md`)

- 前端组件架构 (原子设计、容器/展示式)
- 后端模式 (清洁架构、仓库模式)
- API 设计 (REST 规范、GraphQL 模式设计)
- 数据库模式 (连接池、事务、读取副本)
- 缓存策略 (缓存旁路、HTTP 缓存头)
- 身份验证架构 (JWT + 刷新令牌、会话)

### 开发工作流 (`references/development_workflows.md`)

- 本地开发设置 (Docker Compose、环境配置)
- Git 工作流 (基于主干、常规提交)
- CI/CD 管道 (GitHub Actions 示例)
- 测试策略 (单元、集成、E2E)
- 代码审查流程 (PR 模板、清单)
- 部署策略 (蓝绿、金丝雀、功能标志)
- 监控和可观察性 (日志、指标、健康检查)

### 技术栈指南 (`references/tech_stack_guide.md`)

- 前端框架比较 (Next.js、React+Vite、Vue)
- 后端框架 (Express、Fastify、NestJS、FastAPI、Django)
- 数据库选择 (PostgreSQL、MongoDB、Redis)
- ORM (Prisma、Drizzle、SQLAlchemy)
- 身份验证解决方案 (Auth.js、Clerk、自定义 JWT)
- 部署平台 (Vercel、Railway、AWS)
- 根据用例推荐技术栈 (MVP、SaaS、企业)

---

## 快速参考

### 技术栈决策矩阵

| 需求 | 推荐 |
|-------------|---------------|
| SEO 关键网站 | Next.js with SSR |
| 内部仪表板 | React + Vite |
| API 首先的后端 | FastAPI 或 Fastify |
| 企业级规模 | NestJS + PostgreSQL |
| 快速原型 | Next.js API 路由 |
| 文档密集型数据 | MongoDB |
| 复杂查询 | PostgreSQL |

### 常见问题

| 问题 | 解决方案 |
|-------|----------|
| N+1 查询 | 使用 DataLoader 或急加载 |
| 构建缓慢 | 检查捆绑大小、懒加载 |
| 身份验证复杂性 | 使用 Auth.js 或 Clerk |
| 类型错误 | 在 tsconfig 中启用严格模式 |
| CORS 问题 | 正确配置中间件 |

---

## 假设和可验证的成功标准（Karpathy 纪律）

在使用此技能搭建、推荐或修改任何代码之前，必须暴露以下四个假设。如果任何假设未知，技能将停止并使用 [Forcing-question library](#forcing-question-library-matt-pocock-grill) 进行逐个问题的 grill。

1. **当前团队规模 + 12 个月人力** — 决定架构（单体 / 模块化 / 服务）。Sam Newman: "MonolithFirst."
2. **部署周期目标** — 决定 CI/CD 费用和功能标志投资。*加速* (Forsgren 等人，2018 年)。
3. **面向用户 vs. 内部 vs. 营销网站** — 决定技术栈选择和 a11y/性能预算。
4. **每月云 + SaaS 预算上限** — 决定构建 vs. 管理服务的分割。

**可验证的成功标准** (Karpathy #4) — 此技能发出的每个推荐都必须包含三个机器可检查的数字：

- API 延迟目标 (p50, p95, p99 in ms)
- 前端性能目标 (LCP, INP, CLS on mobile-4G)
- 正常运行时间 / SLO 目标

如果这三个数字中的任何一个未声明，则推荐不完整——返回 forcing-question library 的第 7 个问题。

`scripts/fullstack_decision_engine.py` 工具编码了这些检查：如果没有所有四个假设输入，则拒绝推荐配置文件，并打印匹配配置文件的验证阈值。

---

## 定制化配置文件

`profiles/` 中的四个内置配置文件校准了每个推荐：

| 配置文件 | 选择时机 | 云上限 | 模式 |
|---|---|---|---|
| `saas-startup` | < 10 工程师，面向客户，每日+开发周期 | $8K/月 | Next.js + Postgres 的模块化单体 |
| `enterprise-scale` | 50+ 工程师，受监管，每个 PR 带有门禁 | $250K/月 | 域限定的服务 + 平台团队 |
| `internal-tool` | ≤ 5 工程师，受身份验证保护，< 100 DAU | $500/月 | 首选 Retool；如果被迫，则使用自定义薄栈 |
| `marketing-site` | SEO 依赖，接近零写入 | $200/月 | 静态优先 (Astro / 11ty / Next-static) |

通过以下方式选择配置文件：

```bash
python scripts/fullstack_decision_engine.py \
  --team-size 6 --team-size-12mo 12 \
  --cadence daily --user-facing true --budget 5000 \
  --traffic-p99-rps 45 --data-sensitivity pii-only
```

该工具返回最佳匹配配置文件、与次优配置文件的权衡（如果差距在 15% 以内）、技术栈推荐、应避免的反模式以及命名审批链。**此工具从不自动批准。**

要添加自定义配置文件：将 `profiles/saas-startup.json` 复制到 `profiles/<your-org>.json`，调整 `constraints` 和 `stack_recommendations` 块，然后重新运行。JSON 是定制化表面——无需代码更改。

---

## 组合映射

此技能不会重新实现 POWERFUL 级别专家拥有的范围。它会分叉到他们那里。参考 `references/composition_map.md` 获取完整的路由表。关键分叉：

| 关注点 | 分叉到 |
|---|---|
| API 合同审查 | `engineering/skills/api-design-reviewer/` |
| 数据库模式设计 | `engineering/skills/database-designer/` |
| 可靠性 / SLO 架构设计 | `engineering/slo-architect/` |
| CI/CD 管道 | `engineering/skills/ci-cd-pipeline-builder/` |
| 性能分析 | `engineering/skills/performance-profiler/` |
| 预提交 Karpathy 审查 | `engineering/karpathy-coder/` |
| 预飞行架构 grill | `engineering/grill-me/` |

`cs-fullstack-engineer` 代理（在 `agents/engineering/cs-fullstack-engineer.md` 中）通过 `context: fork` 组合这些分叉。从另一个代理中调用它，使用 `Agent({subagent_type: "cs-fullstack-engineer", prompt: "..."})` 或通过斜杠命令 `/cs:fullstack-review <your problem>`。

---

## 强制问题库 (Matt Pocock grill)

在锁定任何架构或技术栈决策之前，请按照 `references/forcing_questions.md` 中的七个强制问题进行逐个问题的 grill。每个问题都有一个推荐答案、规范引用和终止标准。该纪律：

1. 每次一个问题。不要捆绑。
2. 始终推荐引用规范的答案。
3. 在工作文件（例如，`/tmp/fullstack-grill-<date>.md`）中跟踪答案。
4. 如果终止标准触发，则停止。不要围绕未解决的差距搭建。
5. 在 Q7 之后，使用七个答案作为输入运行 `fullstack_decision_engine.py`。

七个问题的总结（完整内容在参考中）：

1. 当前团队规模 + 12 个月人力？
2. 部署周期——每个 PR、每日、每周、每季度？
3. 面向客户、内部工具还是营销网站？
4. 一年 p50 / p99 流量预测？
5. 招聘对技术栈还是培训团队？
6. 一年云 + SaaS 每月上限？
7. 三个可验证的成功标准，带有数字目标？

---

## 从其他代理和技能的调用

此技能可通过三个表面被任何其他代理或技能调用：

1. **斜杠命令：** `/cs:fullstack-review <prompt>` — 运行完整的 grill + 决策引擎 + 组合路由。
2. **代理子代理：** `Agent({subagent_type: "cs-fullstack-engineer", prompt: "..."})` — 分叉上下文，返回 ≤ 200 字的摘要。
3. **直接工具调用：** `python scripts/fullstack_decision_engine.py ...` — 确定性配置文件匹配，无需对话式 grill（当输入已知时使用）。

参考 `agents/engineering/cs-fullstack-engineer.md` 获取完整的调用合同。
