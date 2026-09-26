# CreateOS 平台技能

> **将任何内容部署到生产环境** — AI 代理、API、后端、机器人、MCP 服务器、前端、Webhooks、工作器等。

## ⚠️ 重要提示：认证

### 对于 AI 代理（MCP）- 使用此方法
当通过 MCP（OpenClaw、MoltBot、ClawdBot、Claude）连接时，**无需 API 密钥**。
MCP 服务器自动处理认证。

**MCP 端点：** `https://api-createos.nodeops.network/mcp`

直接调用工具：
```
CreateProject(...)
UploadDeploymentFiles(...)
ListProjects(...)
```

### 对于 REST API（脚本/外部）
当直接调用 REST 端点（curl、Python requests 等）时：

```
X-Api-Key: <your-api-key>
Base URL: https://api-createos.nodeops.network
```

通过 MCP 获取 API 密钥：`CreateAPIKey({name: "my-key", expiryAt: "2025-12-31T23:59:59Z"})`

## 🚀 MCP 代理快速入门

### 直接部署文件（最快）

```json
// 1. 创建上传项目
CreateProject({
  "uniqueName": "my-app",
  "displayName": "My App",
  "type": "upload",
  "source": {},
  "settings": {
    "runtime": "node:20",
    "port": 3000
  }
})

// 2. 上传文件并部署
UploadDeploymentFiles(project_id, {
  "files": [
    {"path": "package.json", "content": "{\"name\":\"app\",\"scripts\":{\"start\":\"node index.js\"}}"},
    {"path": "index.js", "content": "require('http').createServer((req,res)=>{res.end('Hello!')}).listen(3000)"}
  ]
})

// 结果：https://my-app.createos.nodeops.network 已上线！
```

### 从 GitHub 部署（推送自动部署）

```json
// 1. 获取 GitHub 安装 ID
ListConnectedGithubAccounts()
// 返回：[{installationId: "12345", ...}]

// 2. 查找仓库 ID
ListGithubRepositories("12345")
// 返回：[{id: "98765", fullName: "myorg/myrepo", ...}]

// 3. 创建 VCS 项目
CreateProject({
  "uniqueName": "my-app",
  "displayName": "My App", 
  "type": "vcs",
  "source": {
    "vcsName": "github",
    "vcsInstallationId": "12345",
    "vcsRepoId": "98765"
  },
  "settings": {
    "runtime": "node:20",
    "port": 3000,
    "installCommand": "npm install",
    "buildCommand": "npm run build",
    "runCommand": "npm start"
  }
})

// 每次 git 推送自动部署！
```

### 部署 Docker 镜像

```json
// 1. 创建镜像项目
CreateProject({
  "uniqueName": "my-service",
  "displayName": "My Service",
  "type": "image",
  "source": {},
  "settings": {
    "port": 8080
  }
})

// 2. 部署镜像
CreateDeployment(project_id, {
  "image": "nginx:latest"
})
```

## 目录

1. [简介](#简介)
2. [核心技能概述](#核心技能概述)
3. [项目管理技能](#项目管理技能)
4. [部署技能](#部署技能)
5. [环境管理技能](#环境管理技能)
6. [域名 & 路由技能](#域名--路由技能)
7. [GitHub 集成技能](#github-集成技能)
8. [分析 & 监控技能](#分析--监控技能)
9. [安全技能](#安全技能)
10. [组织技能（应用）](#组织技能-应用)
11. [API 密钥管理技能](#api-key管理技能)
12. [常见部署模式](#常见部署模式)
13. [最佳实践](#最佳实践)
14. [故障排除 & 边缘情况](#故障排除--边缘情况)
15. [API 快速参考](#api-快速参考)

---

## 简介

### 什么是 CreateOS？

CreateOS 是一个云部署平台，专为快速部署任何工作负载而设计——从简单的静态网站到复杂的多代理 AI 系统。它提供：

- **三种部署方法**：GitHub 自动部署、Docker 镜像、直接文件上传
- **多环境支持**：生产、测试、开发环境，具有隔离的配置
- **内置 CI/CD**：git 推送时自动构建和部署
- **自定义域名**：包含 SSL/TLS，DNS 验证
- **实时分析**：请求指标、错误跟踪、性能监控
- **安全扫描**：部署漏洞检测

### 目标用户

| 用户类型 | 主要用例 |
|-----------|-------------------|
| **AI/ML 工程师** | 部署代理、MCP 服务器、RAG 管道、LLM 服务 |
| **后端开发人员** | 部署 API、微服务、Webhooks、工作器 |
| **前端开发人员** | 部署 SPAs、SSR 应用、静态网站 |
| **DevOps 工程师** | 管理环境、域名、扩展、监控 |
| **机器人开发人员** | 主机 Discord、Slack、Telegram 机器人 |

### 支持的技术

**运行时**：`node:18`, `node:20`, `node:22`, `python:3.11`, `python:3.12`, `golang:1.22`, `golang:1.25`, `rust:1.75`, `bun:1.1`, `bun:1.3`, `static`

**框架**：`nextjs`, `reactjs-spa`, `reactjs-ssr`, `vuejs-spa`, `vuejs-ssr`, `nuxtjs`, `astro`, `remix`, `express`, `fastapi`, `flask`, `django`, `gin`, `fiber`, `actix`

---

## 核心技能概述

### 🔌 MCP 工具可用（直接调用 - 无需认证）

当通过 MCP（OpenClaw、Claude 等）使用 CreateOS 时，这些工具可直接调用：

**项目**：
- `CreateProject` - 创建新项目（vcs、image 或 upload 类型）
- `ListProjects` - 列出所有项目
- `GetProject` - 获取项目详情
- `UpdateProject` - 更新项目元数据
- `UpdateProjectSettings` - 更新构建/运行时设置
- `DeleteProject` - 删除项目

**部署**：
- `CreateDeployment` - 部署 Docker 镜像（image 项目）
- `TriggerLatestDeployment` - 从 GitHub 触发构建（vcs 项目）
- `UploadDeploymentFiles` - 上传文件以部署（upload 项目）
- `UploadDeploymentBase64Files` - 以 base64 上传二进制文件
- `UploadDeploymentZip` - 上传 zip 存档
- `ListDeployments` - 列出所有部署
- `GetDeployment` - 获取部署状态
- `GetBuildLogs` - 查看构建日志
- `GetDeploymentLogs` - 查看运行时日志
- `RetriggerDeployment` - 重试失败的部署
- `CancelDeployment` - 取消排队/正在构建的部署
- `WakeupDeployment` - 唤醒休眠的部署

**环境**：
- `CreateProjectEnvironment` - 创建环境（生产、测试等）
- `ListProjectEnvironments` - 列出环境
- `UpdateProjectEnvironment` - 更新环境配置
- `UpdateProjectEnvironmentEnvironmentVariables` - 设置环境变量
- `UpdateProjectEnvironmentResources` - 调整 CPU/内存/副本
- `AssignDeploymentToProjectEnvironment` - 将部署分配给环境
- `DeleteProjectEnvironment` - 删除环境

**域名**：
- `CreateDomain` - 添加自定义域名
- `ListDomains` - 列出域名
- `RefreshDomain` - 验证 DNS
- `UpdateDomainEnvironment` - 将域名分配给环境
- `DeleteDomain` - 删除域名

**GitHub**：
- `ListConnectedGithubAccounts` - 获取连接的 GitHub 账户
- `ListGithubRepositories` - 列出可访问的仓库
- `ListGithubRepositoryBranches` - 列出分支

**应用**：
- `CreateApp` - 创建应用以分组项目
- `ListApps` - 列出应用
- `AddProjectsToApp` - 将项目添加到应用

**用户**：
- `GetCurrentUser` - 获取用户信息
- `GetQuotas` - 检查使用限制
- `GetSupportedProjectTypes` - 列出运行时/框架

### 功能技能

| 技能类别 | 功能 |
|----------------|--------------|
| **项目管理** | 创建、配置、更新、删除、转移项目 |
| **部署** | 构建、部署、回滚、唤醒、取消部署 |
| **环境管理** | 多环境配置、环境变量、资源扩展 |
| **域名管理** | 自定义域名、SSL、DNS 验证 |
| **GitHub 集成** | 自动部署、分支管理、仓库访问 |
| **分析** | 请求指标、错误率、性能数据 |
| **安全** | 漏洞扫描、API 密钥管理 |
| **组织** | 将项目分组到应用、管理服务 |

### 技术技能

| 技能 | 描述 |
|-------|-------------|
| **认证** | 基于 API 密钥的认证，支持过期管理 |
| **Build AI** | 自动检测构建配置 |
| **Dockerfile 支持** | 支持自定义容器构建 |
| **环境隔离** | 每个环境具有独立的配置 |
| **资源管理** | CPU、内存、副本扩展 |

---

## 项目管理技能

### 技能：创建项目

使用完整配置创建新项目，用于构建和运行时设置。

#### 项目类型

| 类型 | 描述 | 适合 |
|------|-------------|----------|
| `vcs` | GitHub 连接的仓库 | 具有 CI/CD 的生产应用 |
| `image` | Docker 容器部署 | 预构建镜像、复杂依赖 |
| `upload` | 直接文件上传 | 快速原型、静态网站 |

#### VCS 项目创建

**作用**：链接 GitHub 仓库，用于推送自动部署。

**用途**：启用 GitOps 工作流——推送即部署，无需手动干预。

**实现方式**：

```json
CreateProject({
  "uniqueName": "my-nextjs-app",
  "displayName": "My Next.js 应用",
  "type": "vcs",
  "source": {
    "vcsName": "github",
    "vcsInstallationId": "12345678",
    "vcsRepoId": "98765432"
  },
  "settings": {
    "framework": "nextjs",
    "runtime": "node:20",
    "port": 3000,
    "directoryPath": ".",
    "installCommand": "npm install",
    "buildCommand": "npm run build",
    "runCommand": "npm start",
    "buildVars": {"NODE_ENV": "production", "NEXT_PUBLIC_API_URL": "https://api.example.com"}
  },
  "appId": "optional-app-uuid",
  "enabledSecurityScan": true
})
```

**前提条件**：
- GitHub 账户通过 `InstallGithubApp` 连接
- 仓库访问权限授予 CreateOS GitHub 应用

**潜在问题**：
- `vcsRepoId` 错误导致部署失败
- 缺少 `port` 设置导致健康检查失败
- `buildVars` 与 `runEnvs` 混淆（构建时 vs 运行时）

#### Image 项目创建

**作用**：部署预构建的 Docker 镜像，无需构建步骤。

**用途**：更快部署，复杂依赖，现有 CI 管道。

```json
CreateProject({
  "uniqueName": "my-api-service",
  "displayName": "My API Service",
  "type": "image",
  "source": {},
  "settings": {
    "port": 8080
  }
})
```

**影响**：
- 无构建日志（镜像已构建）
- 必须单独管理镜像注册中心
- 通过镜像标签进行版本控制

#### Upload 项目创建

**作用**：通过直接上传文件进行部署，无需 Git。

**用途**：快速原型、迁移、CI 生成的工件。

```json
CreateProject({
  "uniqueName": "quick-prototype",
  "displayName": "Quick Prototype",
  "type": "upload",
  "source": {},
  "settings": {
    "framework": "express",
    "runtime": "node:20",
    "port": 3000,
    "installCommand": "npm install",
    "buildCommand": "npm run build",
    "buildDir": "dist",
    "useBuildAI": true
  }
})
```

### 技能：更新项目设置

无需重新创建项目即可修改构建和运行时配置。

```json
UpdateProjectSettings(project_id, {
  "framework": "nextjs",
  "runtime": "node:22",
  "port": 3000,
  "installCommand": "npm ci",
  "buildCommand": "npm run build",
  "runCommand": "npm start",
  "buildDir": ".next",
  "buildVars": {"NODE_ENV": "production"},
  "runEnvs": {"NEW_VAR": "value"},
  "ignoreBranches": ["wip/*"],
  "hasDockerfile": false,
  "useBuildAI": false
})
```

**边缘情况**：
- 更改 `runtime` 触发下次部署的重建
- 更改 `port` 需要重新部署才能生效
- `ignoreBranches` 仅影响未来的推送

### 技能：项目生命周期管理

| 操作 | 工具 |
|-----------|------|
| 列出项目 | `ListProjects(limit?, offset?, name?, type?, status?, app?)` | 仪表板、搜索 |
| 获取详情 | `GetProject(project_id)` | 查看完整配置 |
| 更新元数据 | `UpdateProject(project_id, {displayName, description?, enabledSecurityScan?})` | 重命名、切换功能 |
| 删除 | `DeleteProject(project_id)` | 清理（异步删除） |
| 检查名称 | `CheckProjectUniqueName({uniqueName})` | 创建前验证 |
| 转移 | `TransferProject` | 接收者 |
| 查看转移历史 | `ListProjectTransferHistory(project_id)` |

### 技能：项目转移

在用户之间转移项目所有权。

```
1. 所有者: GetProjectTransferUri(project_id) → 返回 {uri, token} (有效 6 小时)
2. 所有者: 与接收者共享 URI
3. 接收者: TransferProject(project_id, token)
4. 审计: ListProjectTransferHistory(project_id)
```

**安全影响**：
- 令牌 6 小时后过期
- 转移不可逆
- 所有环境和部署都会转移

---

## 部署技能

### 技能：触发部署

#### 对于 VCS 项目

**自动**（推荐）：GitHub 推送触发自动部署。

**手动触发**：
```json
TriggerLatestDeployment(project_id, branch?)
// branch 默认为仓库的默认分支
```

#### 对于 Image 项目

```json
CreateDeployment(project_id, {
  "image": "nginx:latest"
})
// 支持任何有效的 Docker 镜像引用：
// - nginx:latest
// - myregistry.com/myapp:v1.2.3
// - ghcr.io/org/repo:sha-abc123
```

#### 对于 Upload 项目

**直接文件**：
```json
UploadDeploymentFiles(project_id, {
  "files": [
    {"path": "package.json", "content": "{\"name\":\"app\",...}"},
    {"path": "index.js", "content": "const express = require('express')..."},
    {"path": "public/style.css", "content": "body { margin: 0; }"}
  ]
})
```

**Base64 文件**（用于二进制内容）：
```json
UploadDeploymentBase64Files(project_id, {
  "files": [
    {"path": "assets/logo.png", "content": "iVBORw0KGgo..."}
  ]
})
```

**ZIP 上传**：
```json
UploadDeploymentZip(project_id, {file: zipBinaryData})
```

**限制**：
- 每次上传最多 100 个文件
- 使用 ZIP 上传较大项目

### 技能：部署生命周期

```
┌─────────┐    ┌──────────┐    ┌───────────┐    ┌──────────┐
│ 队列     │ →  │ 构建中   │ →  │ 部署中   │ →  │ 已部署   │
└─────────┘    └──────────┘    └───────────┘    └──────────┘
                    │                                 │
                    ↓                                 ↓
               ┌────────┐                       ┌──────────┐
               │ 失败   │                       │ 休眠   │
               └────────┘                       └──────────┘
```

| 状态 | 描述 | 可用操作 |
|-------|-------------|-------------------|
| `queued` | 等待构建槽位 | Cancel |
| `building` | 构建中 | Cancel, View logs |
| `deploying` | 推送到基础设施 | Wait |
| `deployed` | 在线服务流量 | Assign to env |
| `failed` | 构建或部署错误 | Retry, View logs |
| `sleeping` | 休眠超时 | Wake up |

### 技能：部署操作

| 操作 | 工具 |
|-----------|------|
| 列出 | `ListDeployments(project_id, limit?, offset?)` | 每页最多 20 个，分页获取更多 |
| 获取详情 | `GetDeployment(project_id, deployment_id)` | 完整状态、时间戳、URL |
| 重试 | `RetriggerDeployment(project_id, deployment_id, settings?)` | `settings`: "project" 或 "deployment |
| 取消 | `CancelDeployment(project_id, deployment_id)` | 仅 `queued`/`building` 状态 |
| 删除 | `DeleteDeployment(project_id, deployment_id)` | 异步删除 |
| 唤醒 | `WakeupDeployment(project_id, deployment_id)` | 重新启动休眠部署 |
| 下载 | `DownloadDeployment(project_id, deployment_id)` | Upload 项目仅 |

### 技能：使用日志调试

**构建日志** — 调试编译/构建失败：
```json
GetBuildLogs(project_id, deployment_id, skip?)
// skip: 跳过多少行（用于分页）
```

**运行时日志** — 调试应用程序错误：
```json
GetDeploymentLogs(project_id, deployment_id, since-seconds?)
// since-seconds: 查看窗口（默认：60 秒）
```

**环境日志** — 汇总环境的日志：
```json
GetProjectEnvironmentLogs(project_id, environment_id, since-seconds?)
```

---

## 环境管理技能

### 技能：创建环境

环境为相同代码库提供隔离的配置。

**典型设置**：
- `production` — 生产流量，最大资源
- `staging` — 测试生产环境
- `development` — 功能开发

#### VCS 项目环境（需要分支）

```json
CreateProjectEnvironment(project_id, {
  "displayName": "生产环境",
  "uniqueName": "production",
  "description": "生产环境",
  "branch": "main",
  "isAutoPromoteEnabled": true,
  "resources": {
    "cpu": 500,
    "memory": 1024,
    "replicas": 2
  },
  "settings": {
    "runEnvs": {
      "NODE_ENV": "production",
      "DATABASE_URL": "postgresql://prod-db:5432/app",
      "REDIS_URL": "redis://prod-cache:6379"
    }
  }
})
```

#### Image 项目环境（无需分支）

```json
CreateProjectEnvironment(project_id, {
  "displayName": "生产环境",
  "uniqueName": "production",
  "description": "生产环境",
  "resources": {
    "cpu": 500,
    "memory": 1024,
    "replicas": 2
  },
  "settings": {
    "runEnvs": {
      "NODE_ENV": "production"
    }
  }
})
```

### 技能：资源管理

| 资源 | 最小值 | 最大值 | 单位 | 影响 |
|----------|-----|-----|------|--------------|
| CPU | 200 | 500 | 毫核 | 更高 = 更快的处理 |
| 内存 | 500 | 1024 | MB | 更高 = 更多内存 |
| 副本 | 1 | 3 | 实例 | 更高 = 更高的可用性 |

```json
UpdateProjectEnvironmentResources(project_id, environment_id, {
  "cpu": 500,
  "memory": 1024,
  "replicas": 3
})
```

**扩展考虑**：
- 副本 > 1 需要无状态应用程序设计
- 内存限制导致 OOM 杀死
- CPU 限制会导致限制（不会杀死）

### 技能：环境变量

```json
UpdateProjectEnvironmentEnvironmentVariables(project_id, environment_id, {
  "runEnvs": {
    "DATABASE_URL": "postgresql://...",
    "API_KEY": "secret",
    "LOG_LEVEL": "info",
    "FEATURE_FLAG_X": "enabled"
  },
  "port": 8080  // Image 项目仅 |
```

**最佳实践**：
- 永远不要硬编码密钥 — 使用 `runEnvs` 存储所有敏感数据
- 启用安全扫描 — 早期发现漏洞
- 旋转 API 密钥 — 设置合理的过期日期
- 使用环境隔离 — 每个环境具有不同的密钥

### 技能：部署分配

手动控制哪个部署服务于环境：

```json
AssignDeploymentToProjectEnvironment(project_id, environment_id, {
  "deploymentId": "deployment-uuid"
})
```

**用例**：
- 回滚到以前的良好部署
- 蓝绿部署切换
- 金丝雀发布（使用多个环境）

---

## 域名 & 路由技能

### 技能：添加自定义域名

```json
CreateDomain(project_id, {
  "name": "api.mycompany.com",
  "environmentId": "optional-env-uuid"  // 立即分配 |
})
```

**响应包含 DNS 指令**：
```
添加 CNAME 记录:
  api.mycompany.com → <createos 提供的目标>
```

### 技能：域名验证流程

```
1. CreateDomain → 状态: pending
2. 在注册商处配置 DNS
3. 等待 DNS 传播（最多 48 小时）
4. RefreshDomain → 状态: active (如果验证通过)
```

```json
RefreshDomain(project_id, domain_id)
// 仅当状态为 "pending" 时可用 |
```

### 技能：域名-环境分配

将域名流量路由到特定环境：

```json
UpdateDomainEnvironment(project_id, domain_id, {
  "environmentId": "production-env-uuid"
})
// 设置为 null 以取消分配 |
```

**多域名设置示例**：
- `app.example.com` → 生产环境
- `staging.example.com` → 测试环境
- `dev.example.com` → 开发环境

### 技能：域名操作

| 操作 | 工具 |
|-----------|------|
| 列出 | `ListDomains(project_id)` |
| 验证 | `RefreshDomain(project_id, domain_id)` |
| 分配 | `UpdateDomainEnvironment(project_id, domain_id, {environmentId})` |
| 删除 | `DeleteDomain(project_id, domain_id)` |

---

## GitHub 集成技能

### 技能：连接 GitHub 账户

```json
InstallGithubApp({
  "installationId": 12345678,
  "code": "oauth-code-from-github-redirect"
})
```

**流程**：
1. 用户在 CreateOS 中点击 "连接 GitHub"
2. 重定向到 GitHub 进行授权
3. GitHub 重定向回带有 `code` 和 `installationId` 的 URI
4. 调用 `InstallGithubApp` 完成连接

### 技能：仓库发现

```json
// 1. 获取连接的账户
ListConnectedGithubAccounts()
// 返回: [{installationId, accountName, accountType}, ...]

// 2. 列出可访问的仓库
ListGithubRepositories("12345")
// 返回: [{id: "98765", fullName: "myorg/myrepo", ...}]

// 3. 列出 GitHub 仓库分支
ListGithubRepositoryBranches(installation_id, "owner/repo", page?, per-page?, protected?)
// 返回: [{name, protected}, ...]

// 4. 获取文件树（用于单仓库路径选择）
GetGithubRepositoryContent(installation_id, {
  "repository": "owner/repo",
  "branch": "main",
  "treeSha": "optional-tree-sha"
})
```

### 技能：自动部署配置

**分支过滤** — 忽略自动部署的分支：

```json
UpdateProjectSettings(project_id, {
  "ignoreBranches": ["develop", "feature/*", "wip/*"]
})
```

**自动提升** — 自动将部署分配给环境：

```json
CreateProjectEnvironment(project_id, {
  "branch": "main",
  "isAutoPromoteEnabled": true,
  // ... 其他设置
})
```

当 `isAutoPromoteEnabled: true` 时，从该分支的部署自动成为该环境的活动状态。

---

## 分析 & 监控技能

### 技能：综合分析

```json
GetProjectEnvironmentAnalytics(project_id, environment_id, {
  "start": 1704067200,  // Unix 时间戳 (默认：1 小时前)
  "end": 1704070800     // Unix 时间戳 (默认：现在)
})
```

**返回**：
- 总请求次数
- 状态码分布
- RPM (每分钟请求数)
- 成功百分比
- 顶级访问路径
- 顶级错误路径

### 技能：单个指标

| 指标 | 工具 | 返回 |
|--------|------|---------|
| 总请求 | `GetProjectEnvironmentAnalyticsOverallRequests` | 总数, 2xx, 4xx, 5xx 计数 |
| RPM | `GetProjectEnvironmentAnalyticsRPM` | 峰值和平均 RPM |
| 成功百分比 | `GetProjectEnvironmentAnalyticsSuccessPercentage` | (2xx + 3xx) / 总数 |
| 时间序列 | `GetProjectEnvironmentAnalyticsRequestsOverTime` | 按状态随时间请求 |
| 顶级路径 | `GetProjectEnvironmentAnalyticsTopHitPaths` | 最访问的 10 个 |
| 错误路径 | `GetProjectEnvironmentAnalyticsTopErrorPaths` | 10 个易出错的 |
| 分布 | `GetEnvAnalyticsReqDistribution` | 按状态码的分解 |

---

## 安全技能

### 技能：漏洞扫描

**启用扫描**:
```json
UpdateProject(project_id, {
  "enabledSecurityScan": true
})
```

**触发扫描**:
```json
TriggerSecurityScan(project_id, deployment_id)
```

**查看结果**:
```json
GetSecurityScan(project_id, deployment_id)
// 返回: {status, 漏洞, 摘要}
```

**下载完整报告**:
```json
GetSecurityScanDownloadUri(project_id, deployment_id)
// 仅当状态为 "successful" 时返回 |
// 返回带签名的报告下载 URL
```

**重试失败扫描**:
```json
RetriggerSecurityScan(project_id, deployment_id)
// 仅当状态为 "failed" 时返回 |
```

---

## 组织技能（应用）

### 技能：分组项目

应用提供逻辑分组，用于相关项目和服务。

```json
CreateApp({
  "name": "E-Commerce Platform",
  "description": "所有服务用于电子商务系统",
  "color": "#3B82F6"
})
```

### 技能：管理应用内容

```json
// 将项目添加到应用
AddProjectsToApp(app_id, {
  "projectIds": ["project-1-uuid", "project-2-uuid"]
})

// 移除项目
RemoveProjectsFromApp(app_id, {
  "projectIds": ["project-1-uuid"]
})

// 列出应用中的项目
ListProjectsByApp(app_id, limit?, offset?)

// 同样适用于服务
AddServicesToApp(app_id, {"serviceIds": [...]})
RemoveServicesFromApp(app_id, {"serviceIds": [...]})
ListServicesByApp(app_id, limit?, offset?)
```

### 技能：应用生命周期

| 操作 | 工具 |
|-----------|------|
| 列出 | `ListApps()` |
| 更新 | `UpdateApp(app_id, {name, description?, color?})` |
| 删除 | `DeleteApp(app_id)` |

**注意**：删除应用将设置 `appId: null` 在相关项目/服务上（不会删除它们）。

---

## API 密钥管理技能

### 技能：创建 API 密钥

```json
CreateAPIKey({
  "name": "production-key",
  "description": "生产环境的 API 密钥",
  "expiryAt": "2025-12-31T23:59:59Z"
})
// 返回: {id, name, key, expiryAt}
// 重要提示：密钥仅显示一次 |
```

### 技能：API 密钥操作

| 操作 | 工具 |
|-----------|------|
| 列出 | `ListAPIKeys()` |
| 更新 | `UpdateAPIKey(api_key_id, {name, description?})` |
| 撤销 | `RevokeAPIKey(api_key_id)` |
| 检查名称 | `CheckAPIKeyUniqueName({uniqueName})` |

### 技能：用户 & 配额管理

```json
GetCurrentUser()
// 返回: 用户资料信息

GetQuotas()
// 返回: {projects: {used, limit}, apiKeys: {used, limit}, ...}

GetSupportedProjectTypes()
// 返回: 当前的运行时/框架列表 |
```

---

## 常见部署模式

### 模式：AI 代理部署

```json
CreateProject({
  "uniqueName": "intelligent-agent",
  "displayName": "Intelligent Agent",
  "type": "vcs",
  "source": {"vcsName": "github", "vcsInstallationId": "...", "vcsRepoId": "..."
}
```

### 模式：MCP 服务器部署

```json
CreateProject({
  "uniqueName": "my-mcp-server",
  "displayName": "Custom MCP 服务器",
  "type": "vcs",
  "appId": app_id,
  "settings": {
    "runEnvs": {
      "MCP_TRANSPORT": "sse",
      "MCP_PATH": "/mcp"
    }
  }
})
```

**MCP 端点**：`https://api-createos.nodeops.network/mcp`

### 模式：RAG 管道

```json
CreateProject({
  "uniqueName": "rag-pipeline",
  "displayName": "RAG 管道服务",
  "type": "vcs",
  "settings": {
    "runtime": "python:3.12",
    "port": 8000,
    "runCommand": "uvicorn main:app --host 0.0.0.0 --port 8000",
    "runEnvs": {
      "PINECONE_API_KEY": "...",
      "PINECONE_ENVIRONMENT": "us-west1-gcp",
      "OPENAI_API_KEY": "...",
      "EMBEDDING_MODEL": "text-embedding-3-small",
      "CHUNK_SIZE": "512",
      "CHUNK_OVERLAP": "50"
    }
  }
})
```

### 模式：Discord/Slack 机器人

```json
CreateProject({
  "uniqueName": "discord-bot",
  "displayName": "Discord 机器人",
  "type": "image",
  "source": {},
  "settings": {
    "port": 8080,
    "runEnvs": {
      "DISCORD_TOKEN": "...",
      "DISCORD_CLIENT_ID": "...",
      "BOT_PREFIX": "!",
      "LOG_CHANNEL_ID": "..."
    }
  }
})

// 部署镜像：
CreateDeployment(project_id, {"image": "my-discord-bot:v1.0.0"})
```

### 模式：多代理系统

```
┌─────────────────────────────────────────────────┐
│ 应用：代理群组                          │
├─────────────────┬─────────────────┬─────────────┤
│ 编排器      │ 工作代理      │ 执行代理      │
└────────┬────────┬──────┬──────┘
         │                 │               │
         └────── HTTP/gRPC 通信 ──┘
```

```json
// 1. 创建应用
CreateApp({"name": "Agent Swarm"})

// 2. 创建编排器
CreateProject({
  "uniqueName": "orchestrator",
  "type": "vcs",
  "appId": app_id,
  "settings": {
    "runEnvs": {
      "WORKER_RESEARCHER_URL": "https://researcher.createos.nodeops.network",
      "WORKER_EXECUTOR_URL": "https://executor.createos.nodeops.network"
    }
  }
})
```

### 模式：蓝绿部署

```
1. 创建生产环境 "blue" 使用分支 "main"
2. 部署新版本到 "green"
3. 测试 via green 的环境 URL
4. 更新域名环境 → 切换到 "green"
5. "blue" 成为备用
```

### 模式：回滚

```json
// 1. 找到以前的良好部署
ListDeployments(project_id, {limit: 10})
// 识别 deployment_id of last known good

// 2. 分配到环境
AssignDeploymentToProjectEnvironment(project_id, environment_id, {
  "deploymentId": "previous-good-deployment-id"
})
```

---

## 最佳实践

### 安全

1. **永远不要硬编码密钥** — 使用 `runEnvs` 存储所有敏感数据
2. **启用安全扫描** — 早期发现漏洞
3. **旋转 API 密钥** — 设置合理的过期日期
4. **使用环境隔离** — 每个环境具有不同的密钥

### 性能

1. **合理设置资源** — 从小开始，根据指标扩展
2. **使用副本** — 至少 2 个副本用于生产
3. **监控指标** — 设置错误率突增的警报
4. **优化构建** — 使用 `npm ci` 考虑 `npm install`

### 可靠性

1. **谨慎启用自动提升** — 先在测试环境中测试
2. **保留以前的部署** — 启用快速回滚
3. **使用健康检查** — 确保 `port` 与应用程序的监听端口匹配
4. **处理休眠部署** — 唤醒或配置保持活动状态

### 组织

1. **使用应用** — 将相关项目分组
2. **命名约定** — `{app}-{service}-{env}` 模式
3. **文档化环境** — 为每个环境提供清晰的描述
4. **清理未使用的** — 删除旧项目和部署

---

## 故障排除 & 边缘情况

### 常见错误

| 错误 | 诊断 | 解决方案 |
|-------|-----------|----------|
| 构建失败 | `GetBuildLogs` | 修复代码错误，检查依赖 |
| 运行时崩溃 | `GetDeploymentLogs` | 检查启动错误，缺少环境变量 |
| 健康检查失败 | App 未在端口上响应 | 验证 `port` 设置是否与应用程序匹配 |
| 502 Bad Gateway | 应用崩溃后部署 | 检查日志，增加内存如果 OOM |
| 域名 pending | DNS 未传播 | 等待 24-48 小时，验证 CNAME 记录 |
| 配额超出 | `GetQuotas` | 升级计划或删除未使用的 |
| 部署休眠 | `WakeupDeployment` 或添加保持活动状态 |
```

### 边缘情况

**高负载场景**：
- 每个环境最多 3 个副本
- 考虑使用外部负载均衡器进行更高扩展
- 监控 RPM 和调整资源

**单仓库项目**：
- 设置 `directoryPath` 到子目录
- 使用 `GetGithubRepositoryContent` 探索结构

**私有 npm/pip 包**：
- 添加 auth 令牌到 `buildVars`
- 使用 `.npmrc` 或 `pip.conf` 在仓库中

**长时间构建**：
- 构建超时为 15 分钟
- 使用 `hasDockerfile: true` 对于复杂构建
- 预构建镜像对于 image 项目

---

## API 快速参考

### 项目生命周期

```
CreateProject → ListProjects → GetProject → UpdateProject → UpdateProjectSettings → DeleteProject
CheckProjectUniqueName | GetProjectTransferUri → TransferProject | ListProjectTransferHistory
```

### 部署生命周期

```
CreateDeployment | TriggerLatestDeployment | UploadDeploymentFiles | UploadDeploymentBase64Files | UploadDeploymentZip
ListDeployments → GetDeployment → AssignDeploymentToProjectEnvironment
RetriggerDeployment | CancelDeployment | DeleteDeployment | WakeupDeployment | DownloadDeployment
GetBuildLogs | GetDeploymentLogs
```

### 环境

```
CreateProjectEnvironment → ListProjectEnvironments → UpdateProjectEnvironment
DeleteProjectEnvironment
```

### 域名

```
CreateDomain → ListDomains → RefreshDomain → UpdateDomainEnvironment → DeleteDomain
```

### GitHub 集成

```
InstallGithubApp → ListConnectedGithubAccounts
ListGithubRepositories → ListGithubRepositoryBranches → GetGithubRepositoryContent
```

### 分析

```
GetProjectEnvironmentAnalytics (综合)
GetProjectEnvironmentAnalyticsOverallRequests | GetProjectEnvironmentAnalyticsRPM
GetProjectEnvironmentAnalyticsSuccessPercentage | GetProjectEnvironmentAnalyticsRequestsOverTime
GetProjectEnvironmentAnalyticsTopHitPaths | GetProjectEnvironmentAnalyticsTopErrorPaths
GetEnvAnalyticsReqDistribution
```

### 安全

```
TriggerSecurityScan → GetSecurityScan → GetSecurityScanDownloadUri
RetriggerSecurityScan
```

### 应用

```
CreateApp → ListApps → UpdateApp → DeleteApp
AddProjectsToApp | RemoveProjectsFromApp | ListProjectsByApp
AddServicesToApp | RemoveServicesFromApp | ListServicesByApp
```

### API 密钥 & 用户

```
CreateAPIKey → ListAPIKeys → UpdateAPIKey → RevokeAPIKey
CheckAPIKeyUniqueName | GetCurrentUser | GetQuotas | GetSupportedProjectTypes
```

### 命名约束

| 字段 | 最小值 | 最大值 | 模式 |
|-------|-----|-----|---------|
| 项目 uniqueName | 4 | 32 | `^[a-zA-Z0.0-9-]+$` |
| 项目 displayName | 4 | 48 | `^[a-zA-Z0-9 _-]+$` |
| 描述 | 4 | 2048 | 任意文本 |
| 环境 uniqueName | 4 | 32 | `^[a-zA-Z0-9-]+$` |
| 环境 displayName | 4 | 48 | `^[a-zA-Z0-9 _-]+$` |
| API 密钥名称 | 4 | 48 | `^[a-zA-Z0-9-]+$` |
| 域名 | 3 | 255 | 有效的域名 |

---

## 参考

如果用户正在将现有项目从其他云平台迁移而不是从零开始，请优先考虑迁移相关的技能，而不是一般的 `createos` 流程：

- **`vercel-to-createos`** — 当前已上线。当仓库包含 `vercel.json`、`.vercel/` 或 `@vercel/*` 依赖，或用户提到从 Vercel 迁移时，使用此技能。
- `netlify-to-createos`, `railway-to-createos`, `heroku-to-createos`, `render-to-createos`, `flyio-to-createos` — 保留占位符。直到它们发布，请将用户路由到 `mailto:business@nodeops.xyz` 的 concierge 迁移。

在仓库根目录的 [MIGRATIONS.md](../../MIGRATIONS.md) 中查看完整的迁移技能索引。

---

*最后更新：2025 年 1 月*
