# AWS Blocks 应用开发

> **包命名:** 所有包均在 `@aws-blocks` 命名空间下发布（例如，`@aws-blocks/core`、`@aws-blocks/blocks`、`@aws-blocks/bb-kv-store`）。

## 概述

AWS Blocks 是一个代码构建基础设施的框架，其中 Building Blocks 将 CDK、SDK 和本地模拟整合为单个 API。它提供 18 个以上的 Building Blocks，涵盖存储、认证、实时通信、后台任务、文件管理、AI/搜索、电子邮件和可观察性——所有功能均可在本地运行，无需 AWS 凭证。

**主要特点：**

- 一个 `aws-blocks/` 目录定义整个后端
- 前端导入完全类型化——无需客户端生成
- 所有 Building Blocks 在本地运行，无需 AWS（模拟数据持久化到 `.bb-data/`）
- 使用 `npm run sandbox` 部署短暂的、独立的测试环境，使用 `npm run deploy` 部署长期环境，并使用最小权限凭证

## 创建新项目

```bash
npx @aws-blocks/create-blocks-app my-app
cd my-app
```

### 将 AWS Blocks 添加到现有项目：

```bash
npx @aws-blocks/create-blocks-app .
```

这将检测现有项目并在您的代码旁边添加一个 `aws-blocks/` 工作区。

### 将 AWS Blocks 添加到 Amplify Gen 2 项目：

```bash
npx @aws-blocks/create-blocks-app .
```

当 CLI 检测到 `amplify/backend.ts` 时，它会自动将 AWS Blocks 与您的 Amplify 后端集成。

### 使用特定模板：

```bash
npx @aws-blocks/create-blocks-app my-app --template demo
cd my-app
```

### 可用模板

| 模板 | 描述 |
|------|------|
| `default` | Vite + lit-html 启动应用，包含基本认证、数据持久化和实时通信，用于演示基本应用架构和模式（当省略 --template 时使用） |
| `bare` | Vite + lit-html 启动应用，包含一个 "hello world" API 方法和极简的前端 |
| `react` | React + Vite 启动应用，包含一个 API 端点和类型化的 React 前端 |
| `backend` | 仅后端——没有前端，只有 AWS Blocks API 和一个端点 |
| `demo` | 订单应用，包含 AuthBasic、KVStore、DistributedTable、Zod 模式、索引和受认证保护的 CRUD |
| `auth-cognito` | 完整的 AuthCognito 密码验证电子邮件-OTP，包含角色、设备管理 Authenticator UI |
| `nextjs` | Next.js + React 启动应用，包含 AWS Blocks 后端集成（SSR + 服务器组件） |

## 开发工作流

创建项目后，参考 **node_modules/@aws-blocks/blocks/README.md** 了解完整开发工作流，包括：

- 核心概念（架构、Building Block 选择）
- 项目结构和 Scope 组织
- 错误处理模式
- 模式验证
- 本地开发
- 最佳实践和常见错误
- 部署 IAM 角色设置和安全指南

在实现特定 Building Block 时，请阅读其包的 README 获取详细 API 参考（例如，`node_modules/@aws-blocks/bb-kv-store/README.md`）。这些是您已安装版本的权威文档。

## 安全注意事项

- 在所有不应公开的方法中使用 `await auth.requireAuth(context)`——ApiNamespace 方法默认**未认证**
- 使用 `new AppSetting(scope, id, { secret: true })` 处理 API 密钥和凭证——不要硬编码或使用 `.env` 文件
- 始终将模式附加到 KVStore/AppSetting，以接受用户数据——RPC 层验证结构但不验证业务逻辑
- 不要添加广泛的 `*` IAM 策略——每个 Building Block 已授予针对其自身资源的最小权限
- 不要更改 FileBucket 的 `blockPublicAccess`——通过 CloudFront 代替提供公共文件
- 明确配置 `CORS_ALLOWED_ORIGINS` 用于生产环境——避免使用通配符
- 对于跨域部署，将 `crossDomain: true` 传递给认证构造函数（启用 `SameSite=None; Secure; Partitioned`）
- 在 Hosting 上启用 `monitoring: { enabled: true, snsTopicArn: '...' }` 以获取生产警报
- 通过 CDK 为面向公众的应用添加 WAF 和 API Gateway 速率限制——默认不包含
- Logger 提供序列化安全（循环引用、类型强制）但**不**脱敏敏感内容——不要将原始凭证、令牌或密钥传递给 Logger 方法；在记录前清理上下文对象
