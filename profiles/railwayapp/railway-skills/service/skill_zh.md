# 服务管理

检查状态、更新属性和高级服务创建。

## 使用场景

- 用户询问服务状态、健康或部署情况
- 用户询问"我的服务是否已部署？"
- 用户想要重命名服务或更改服务图标
- 用户想要链接其他服务
- 用户想要将 Docker 镜像作为新服务部署（高级）

**注意：** 对于创建本地代码的服务（常见情况），请优先使用 `new` 技能，该技能可一起处理项目设置、脚手架和服务创建。

**对于 GitHub 仓库源：** 使用 `new` 技能创建空服务，然后使用 `environment` 技能通过暂存更改 API 配置 `source.repo`。

## 创建服务

通过 GraphQL API 创建新服务。没有对应的 CLI 命令。

### 获取上下文

```bash
railway status --json
```

提取：
- `project.id` - 用于创建服务
- `environment.id` - 用于暂存实例配置

### 创建服务 Mutation

```graphql
mutation serviceCreate($input: ServiceCreateInput!) {
  serviceCreate(input: $input) {
    id
    name
  }
}
```

### ServiceCreateInput 字段

| 字段 | 类型 | 描述 |
|------|------|------|
| `projectId` | String! | 项目 ID（必填） |
| `name` | String | 服务名称（如果省略则自动生成） |
| `source.image` | String | Docker 镜像（例如，`nginx:latest`） |
| `source.repo` | String | GitHub 仓库（例如，`user/repo`） |
| `branch` | String | 仓库源的 Git 分支 |
| `environmentId` | String | 如果设置且为分支，则仅在该环境中创建 |

### 示例：创建空服务

```bash
bash <<'SCRIPT'
scripts/railway-api.sh \
  'mutation createService($input: ServiceCreateInput!) {
    serviceCreate(input: $input) { id name }
  }' \
  '{"input": {"projectId": "PROJECT_ID"}}'
SCRIPT
```

### 示例：创建带镜像的服务

```bash
bash <<'SCRIPT'
scripts/railway-api.sh \
  'mutation createService($input: ServiceCreateInput!) {
    serviceCreate(input: $input) { id name }
  }' \
  '{"input": {"projectId": "PROJECT_ID", "name": "my-service", "source": {"image": "nginx:latest"}}}'
SCRIPT
```

### 连接 GitHub 仓库

**不要使用 serviceCreate 与 source.repo** - 而应使用暂存更改 API。

流程：
1. 创建空服务：`serviceCreate(input: {projectId: "...", name: "my-service"})`
2. 使用 `environment` 技能通过暂存更改 API 配置源
3. 应用以触发部署

### 创建后：配置实例

使用 `environment` 技能配置服务实例：

```json
{
  "services": {
    "<serviceId>": {
      "isCreated": true,
      "source": { "image": "nginx:latest" },
      "variables": {
        "PORT": { "value": "8080" }
      }
    }
  }
}
```

**关键：** 对于新服务实例，始终包含 `isCreated: true`。

然后使用 `environment` 技能应用并部署。

有关变量引用，请参阅 [reference/variables.md](references/variables.md)。

## 检查服务状态

```bash
railway service status --json
```

返回链接服务的当前部署状态。

### 部署历史

```bash
railway deployment list --json --limit 5
```

### 显示状态

显示：
- **服务**：名称和当前状态
- **最新部署**：状态（SUCCESS、FAILED、DEPLOYING、CRASHED 等）
- **部署时间**：当前部署何时上线
- **最近部署**：最后 3-5 个状态和时间戳

### 部署状态

| 状态 | 含义 |
|------|------|
| SUCCESS | 部署并运行 |
| FAILED | 构建或部署失败 |
| DEPLOYING | 正在部署 |
| BUILDING | 构建中 |
| CRASHED | 运行时崩溃 |
| REMOVED | 部署已移除 |

## 更新服务

通过 GraphQL API 更新服务名称或图标。

### 获取服务 ID

```bash
railway status --json
```

从响应中提取 `service.id`。

### 更新名称

```bash
bash <<'SCRIPT'
scripts/railway-api.sh \
  'mutation updateService($id: String!, $input: ServiceUpdateInput!) {
    serviceUpdate(id: $id, input: $input) { id name }
  }' \
  '{"id": "SERVICE_ID", "input": {"name": "new-name"}}'
SCRIPT
```

### 更新图标

图标可以是图像 URL 或动画 GIF。

| 类型 | 示例 |
|------|------|
| 图像 URL | `"icon": "https://example.com/logo.png"` |
| 动画 GIF | `"icon": "https://example.com/animated.gif"` |
| Devicons | `"icon": "https://devicons.railway.app/github"` |

**Railway Devicons：** 查询 `https://devicons.railway.app/{query}` 获取常见开发者图标（例如，`github`、`postgres`、`redis`、`nodejs`）。全部浏览：https://devicons.railway.app

```bash
bash <<'SCRIPT'
scripts/railway-api.sh \
  'mutation updateService($id: String!, $input: ServiceUpdateInput!) {
    serviceUpdate(id: $id, input: $input) { id icon }
  }' \
  '{"id": "SERVICE_ID", "input": {"icon": "https://devicons.railway.app/github"}}'
SCRIPT
```

### ServiceUpdateInput 字段

| 字段 | 类型 | 描述 |
|------|------|------|
| `name` | String | 服务名称 |
| `icon` | String | Emoji 或图像 URL（包括动画 GIF） |

## 链接服务

切换当前目录的链接服务：

```bash
railway service link
```

或直接指定：

```bash
railway service link <service-name>
```

## 组合性

- **使用本地代码创建服务**：使用 `new` 技能（处理脚手架 + 创建）
- **配置服务**：使用 `environment` 技能（变量、命令、图像等）
- **删除服务**：使用 `environment` 技能并设置 `isDeleted: true`
- **应用更改**：使用 `environment` 技能
- **查看日志**：使用 `deployment` 技能
- **部署本地代码**：使用 `deploy` 技能

## 错误处理

### 未链接服务

```
未链接服务。运行 `railway service link` 链接服务。
```

### 无部署

```
服务存在但尚未有部署。使用 `railway up` 部署。
```

### 服务未找到

```
未找到服务 "foo"。使用 `railway status` 检查可用服务。
```

### 项目未找到

用户可能不在链接的项目中。检查 `railway status`。

### 权限被拒绝

用户需要至少 DEVELOPER 角色才能创建服务。

### 无效镜像

Docker 镜像必须是可访问的（公开或具有注册表凭证）。
