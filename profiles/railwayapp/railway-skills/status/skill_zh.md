# 铁路状态

检查此目录下铁路项目的当前状态。

## 使用场景

- 用户询问铁路状态、项目、服务或部署情况
- 用户提到要部署或推送到铁路
- 任何铁路操作（部署、更新服务、添加变量）之前
- 用户询问环境或域名

## 不适用场景

当用户需要以下信息时，请使用 `environment` 技能：
- 详细的服务配置（构建类型、Dockerfile 路径、构建命令、根目录）
- 部署配置（启动命令、重启策略、健康检查、预部署命令）
- 服务源（仓库、分支、镜像）
- 比较服务配置
- 查询或修改环境变量

## 检查状态

运行：
```bash
railway status --json
```

首先验证 CLI 是否已安装：
```bash
command -v railway
```

## 错误处理

### CLI 未安装
如果 `command -v railway` 失败：

> Railway CLI 未安装。使用以下命令安装：
> ```
> npm install -g @railway/cli
> ```
> 或
> ```
> brew install railway
> ```
> 然后，进行身份验证：`railway login`

### 未认证
如果 `railway whoami` 失败：

> 未登录到 Railway。运行：
> ```
> railway login
> ```

### 未关联项目
如果状态返回 "No linked project"：

> 此目录未关联铁路项目。
>
> 要关联现有项目：`railway link`
> 要创建新项目：`railway init`

## 展示状态

解析 JSON 并展示：
- **项目**：名称和工作区
- **环境**：当前环境（生产、预发布等）
- **服务**：带部署状态的列表
- **活跃部署**：任何进行中的部署（来自 `activeDeployments` 字段）
- **域名**：任何配置的域名

示例输出格式：
```
项目：my-app (工作区：my-team)
环境：生产

服务：
- web：已部署 (https://my-app.up.railway.app)
- api：正在部署（构建中）
- postgres：运行中
```

每个服务的 `activeDeployments` 数组显示当前正在运行的部署及其状态（构建中、部署中等）。
