# /dotnet-init

## 什么是

交互式地初始化一个 .NET 项目，用于与 dotnet-claude-kit 一起使用。检测项目类型，询问有关架构和技术栈的针对性问题，然后在项目根目录中生成一个完全自定义的 `CLAUDE.md`。

**无需手动复制模板。**

## 何时使用

- 使用 Claude Code 开始一个新的 .NET 项目
- 将 dotnet-claude-kit 添加到现有项目中
- "初始化项目"、"设置项目"、"生成 CLAUDE.md"、"为 dotnet-claude-kit 配置"

## 如何使用

### 第 1 步：检测或询问项目类型

分析当前目录以确定这是现有项目还是绿野项目：

```
→ 查找 .slnx / .sln 文件
→ 如果找到，扫描 .csproj 文件以检测 SDK 类型：
  - Microsoft.NET.Sdk.Web → web-api 或 blazor-app
  - Microsoft.NET.Sdk.Worker → worker-service
  - Microsoft.NET.Sdk → class-library
  - 多个项目具有模块间引用 → modular-monolith
  - 如果不明确，询问用户

→ 如果没有找到解决方案/项目（绿野项目）：
  - 询问："你在构建什么？"
    - REST API / 微服务 → web-api
    - Blazor 应用程序 → blazor-app
    - 后台工作程序 / 队列处理器 → worker-service
    - NuGet 包 / 共享库 → class-library
    - 多模块系统 → modular-monolith
  - 询问："项目名称？"
  - 搭建解决方案结构：
    - dotnet new sln -n ProjectName --format slnx   (现代 XML 解决方案格式)
    - 根据需要创建 webapi / worker / classlib
    - 使用 .NET 10 默认值设置 Directory.Build.props
    - 创建 src/ 和 tests/ 文件夹结构
```

### 第 2 步：架构问卷

加载 `architecture-advisor` 技能并询问针对性问题：

1. **领域复杂性** — CRUD 密集型、中等业务规则或丰富的领域？
2. **团队规模** — 个人、小团队或大团队？
3. **模块边界** — 单个可部署或多个限界上下文？
4. **现有模式** — (仅限现有项目) 通过 `convention-learner` 技能检测约定

→ 推荐：VSA、Clean Architecture、DDD 或模块化单体，并说明理由。

### 第 3 步：技术栈选择

询问具体的技术选择：

- **数据库**：PostgreSQL、SQL Server、SQLite 或尚未选择
- **认证**：JWT、OIDC、Cookie 或尚未选择
- **缓存**：HybridCache、Redis 或尚未选择
- **消息传递**：Wolverine、MassTransit 或尚未选择
- **测试**：确认 xUnit + Testcontainers 默认值

### 第 4 步：生成 CLAUDE.md

从 `templates/` 加载适当的模板作为基础，然后进行自定义：

- 将 `[ProjectName]` 替换为实际的项目/解决方案名称
- 设置选择的架构
- 配置技术栈部分
- 对于现有项目：添加在第 2 步中检测到的项目特定约定
- 对于绿野项目：根据架构选择添加推荐的约定

**在写入之前，检查是否存在现有的 `CLAUDE.md`。切勿无声覆盖它。**

```
→ 如果 ./CLAUDE.md 不存在：
  - 将生成的内容写入 ./CLAUDE.md

→ 如果 ./CLAUDE.md 已存在：
  - 读取它并识别手写/自定义部分
    (任何不是由工具模板生成的部分)
  - 询问："你已经有一个 CLAUDE.md。我应该如何继续？"
    - 合并（推荐）→ 保留用户的自定义部分，在原地添加或刷新工具的架构、技术栈和约定部分
    - 覆盖 → 完全用新文件替换它
    - 保留 → 不更改文件并打印生成的内容，以便用户可以手动复制他们想要的部分
  - 对于合并和覆盖：首先将原始文件备份到 ./CLAUDE.md.bak。
    切勿在没有 .bak 备份的情况下丢弃用户内容。
```

### 第 5 步：验证设置

```
→ 确认 .mcp.json 存在或创建它（用于 Roslyn MCP 服务器）
→ 对于现有项目：
  - 验证解决方案文件是否可发现
  - 运行快速健康检查以建立基线
  - 报告："项目已初始化。运行 /health-check 查看你的基线。"
→ 对于绿野项目：
  - 验证在搭建的解决方案上 dotnet build 是否成功
  - 报告："项目已创建。运行 /scaffold 添加你的第一个功能。"
```

**调用的技能**：`project-setup`、`architecture-advisor`、`convention-learner`
**代理**：`dotnet-architect`

## 示例 — 现有项目

```
用户：/dotnet-init

Claude：检测到：
  - 解决方案：MyApp.slnx (3 个项目)
  - SDK：Microsoft.NET.Sdk.Web → Web API
  - 数据库：PostgreSQL (从连接字符串)
  - 认证：JWT (从 appsettings)

  1. 领域复杂性？ [CRUD 密集型 / 中等 / 丰富领域]
  > 中等

  2. 团队规模？ [个人 / 小 / 大]
  > 小

  推荐：垂直切片架构
  生成：./CLAUDE.md (MyApp + VSA + PostgreSQL + JWT)
  运行 /health-check 查看你的基线。
```

## 示例 — 绿野项目

```
用户：/dotnet-init

Claude：未找到 .sln 或 .csproj。让我们设置一个新项目。

  1. 你在构建什么？ [REST API / Blazor / Worker / Library / Modular Monolith]
  > REST API

  2. 项目名称？
  > OrderService

  3. 领域复杂性？ [CRUD 密集型 / 中等 / 丰富领域]
  > CRUD 密集型

  推荐：垂直切片架构

  创建解决方案...
  → dotnet new sln -n OrderService --format slnx
  → dotnet new webapi -n OrderService.Api -o src/OrderService.Api
  → dotnet new xunit3 -n OrderService.Tests -o tests/OrderService.Tests
  → Directory.Build.props 使用 .NET 10 默认值
  → 生成：./CLAUDE.md (OrderService + VSA + scaffold-ready)

  运行 /scaffold 添加你的第一个功能。
```

## 示例 — 现有项目带有 CLAUDE.md

```
用户：/dotnet-init

Claude：检测到：
  - 解决方案：MyApp.slnx (3 个项目) → Web API
  - 找到现有的 CLAUDE.md (自定义 "部署" 和 "团队约定" 部分)

  你已经有一个 CLAUDE.md。我应该如何继续？
  [合并（推荐） / 覆盖 / 保留]
  > 合并

  → 将原始文件备份到 ./CLAUDE.md.bak
  → 保留你的部署 + 团队约定部分
  → 刷新架构 (VSA)、技术栈 (PostgreSQL + JWT) 和约定部分
  生成：./CLAUDE.md
  运行 /health-check 查看你的基线。
```

## 相关

- `/plan` — 在构建功能之前进行规划
- `/health-check` — 初始化后评估项目健康状况
- `/scaffold` — 使用选择的架构搭建功能
