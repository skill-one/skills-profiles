---
name: project-overview
description: 用于OSS仓库地图、代码层查找、应用/包/源所有权以及业务占位符。
---

# LobeHub 项目概述

> 下面的目录列表是一个**精选的关键位置地图**，而不是一个详尽的树状结构。`packages/`、`src/store/`、路由组等会随着时间的推移而增长——对真实目录运行`ls`以获取当前版本。

## 项目描述

开源、现代设计的 AI 代理工作空间：**LobeHub**（曾用名 LobeChat）。
此代码库是**开源的根目录**（`github.com/lobehub/lobehub`，包名`@lobehub/lobehub`）。

**支持的平台：**

- 网页桌面/移动端
- 桌面端（Electron）—— `apps/desktop`
- 移动应用（React Native）—— **独立的代码库，已发布**（不在本单体代码库中）

**Logo 表情符号：** 🤯

## 完整技术栈

| 类别      | 技术                                 |
| --------- | ------------------------------------ |
| 框架      | Next.js 16 + React 19                |
| 路由      | Next.js 内部的 SPA，使用`react-router-dom` |
| 语言      | TypeScript                           |
| UI 组件  | `@lobehub/ui`，antd                  |
| CSS-in-JS | antd-style                          |
| 图标      | lucide-react，`@ant-design/icons`     |
| 国际化    | react-i18next                       |
| 状态管理  | zustand                             |
| URL 参数  | nuqs                                 |
| 数据获取  | SWR                                 |
| React 钩子 | aHooks                              |
| 日期/时间 | dayjs                               |
| 工具      | es-toolkit                          |
| API       | TRPC (类型安全)                     |
| 数据库    | Neon PostgreSQL + Drizzle ORM        |
| 测试      | Vitest                              |

> 精确版本位于根目录的`package.json`中——请在那里查看，而不是在这里。

## 单体代码库布局

扁平布局——`apps/`、`packages/`和`src/`都位于代码库根目录。没有 git 子模块。

```
(代码库根目录)
├── apps/
│   ├── cli/                  # LobeHub CLI
│   ├── desktop/              # Electron 桌面应用
│   └── server/               # 基于 Next.js 的服务器（`@/server/*`别名）
│       └── src/
│           ├── router-hono/  # Hono 端点路由器和独立运行时
│           └── ...           # featureFlags，globalConfig，modules，routers，services，workflows
├── docs/                     # changelog，开发，自托管，使用说明
├── locales/                  # en-US，zh-CN，...
├── packages/                 # ~80 @lobechat/* 工作区包——`ls`获取完整列表。关键包：
│   ├── agent-runtime/        # 代理运行时核心
│   ├── agent-signal/         # 代理信号管道
│   ├── agent-tracing/        # 跟踪 / 快照
│   ├── builtin-tool-*/       # 每个工具的包（计算器，网络浏览，claude-code，...）
│   ├── builtin-tools/        # 组成builtin-tool-*的中心注册表
│   ├── context-engine/
│   ├── database/             # src/{models,schemas,repositories}
│   ├── model-bank/           # 模型定义 & 提供者卡片
│   ├── model-runtime/        # src/{core,providers}
│   ├── locales/              # i18n 真实来源：packages/locales/src/default/
│   ├── env/                  # 环境配置模式 (@/envs/* → packages/env/src/*)
│   ├── app-config/
│   ├── business/             # 开源桩（config，const，model-bank，model-runtime）——被云端覆盖
│   ├── types/
│   └── utils/
└── src/
    ├── app/
    │   ├── (backend)/        # api，f，market，中间件，oidc，trpc，webapi
    │   ├── spa/              # SPA HTML 模板服务
    │   └── spa-auth/         # 认证 HTML 容器（SSR）
    ├── routes/               # SPA 页面片段（瘦——委托给features/
    │   └── (main)/ (mobile)/ (desktop)/ (popup)/ auth/ onboarding/ share/
    ├── spa/                  # SPA 入口 + 路由配置
    │   ├── entry.{web,mobile,desktop,popup}.tsx
    │   └── router/
    ├── business/             # 开源桩（客户端/服务器）——云端代码库提供真实实现
    ├── features/             # 领域业务组件
    ├── store/                # ~30 zustand 存储器——`ls`获取完整列表
    └── ...                   # components，hooks，layout，libs，services，types，utils
```

## 架构图

| 层级            | 位置                                                 |
| --------------- | ---------------------------------------------------- |
| UI 组件        | `src/components`，`src/features`                     |
| SPA 页面        | `src/routes/`                                        |
| React 路由      | `src/spa/router/`                                    |
| 全局提供者      | `src/layout`                                         |
| Zustand 存储器  | `src/store`                                          |
| 客户端服务      | `src/services/`                                      |
| REST API        | `src/app/(backend)/webapi`                          |
| tRPC 路由器     | `apps/server/src/routers/{async\|lambda\|mobile\|tools}` |
| 服务器服务      | `apps/server/src/services`（可以访问数据库）          |
| 服务器模块      | `apps/server/src/modules`（不能访问数据库）          |
| 功能标志        | `apps/server/src/featureFlags`                      |
| 全局配置        | `apps/server/src/globalConfig`                      |
| 数据库模式      | `packages/database/src/schemas`                      |
| 数据库模型      | `packages/database/src/models`                       |
| 数据库仓库      | `packages/database/src/repositories`                 |
| 第三方         | `src/libs`（分析，oidc 等）                         |
| 内建工具        | `packages/builtin-tool-*`，`packages/builtin-tools`  |
| 开源桩         | `src/business/*`，`packages/business/*`（此代码库） |

## 数据流

```
React UI → 存储器操作 → 客户端服务 → TRPC Lambda → 服务器服务 → 数据库模型 → PostgreSQL
```

## 注意：与云端代码库的关系

这个开源代码库被一个**独立的私有云（SaaS）代码库**作为 git 子模块挂载在`lobehub/`处消费。
云端代码库提供：

- **`src/business/{client,server}`**和**`packages/business/*`**实现，
  它们会覆盖这里发送的桩。
- 仅云路由（例如`（cloud）/`，`embed/`），仅云存储器（例如`subscription/`），仅云 tRPC 路由器（计费，预算，风险控制，...），
  以及`src/app/(backend)/cron/`下的 Vercel 定时路由。
- 云端文件解析顺序：`@/store/x` → 云`src/store/x`首先，然后`lobehub/packages/store/src/x`，然后`lobehub/src/store/x`。**云端覆盖优先。**

当单独在这个代码库中工作时，忽略云层——`src/business/`和`packages/business/`中的桩是这里的真实来源。
