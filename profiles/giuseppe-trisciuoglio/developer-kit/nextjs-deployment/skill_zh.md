# Next.js 部署

使用 Docker、CI/CD 管道和全面监控将 Next.js 应用部署到生产环境。

## 概述

本技能提供将 Next.js 应用部署到生产环境的模式和代码示例。它涵盖了使用 Docker 的容器化、使用 GitHub Actions 的 CI/CD 自动化、环境配置、健康检查和生产监控。使用独立输出模式进行容器部署，使用多阶段 Docker 构建优化镜像，并使用 OpenTelemetry 进行可观察性。

## 何时使用

在用户请求涉及以下内容时激活：

- "部署 Next.js"、"Dockerize Next.js"、"容器化"
- "GitHub Actions"、"CI/CD 管道"、"自动部署"
- "环境变量"、"运行时配置"、"NEXT_PUBLIC"
- "预览部署"、"测试环境"
- "监控"、"OpenTelemetry"、"跟踪"、"日志"
- "健康检查"、"就绪"、"存活"
- "生产构建"、"独立输出"
- "服务器动作加密密钥"、"NEXT_SERVER_ACTIONS_ENCRYPTION_KEY"

## 快速参考

### 输出模式

| 模式 | 用例 | 命令 |
|------|----------|---------|
| `standalone` | Docker/容器部署 | `output: 'standalone'` |
| `export` | 静态网站（无服务器） | `output: 'export'` |
| (默认) | Node.js 服务器部署 | `next start` |

### 环境变量类型

| 前缀 | 可用性 | 用例 |
|--------|--------------|----------|
| `NEXT_PUBLIC_` | 构建时 + 浏览器 | 公共 API 密钥、功能标志 |
| (无前缀) | 仅服务器 | 数据库 URL、密钥 |
| 运行时 | 仅服务器 | 每个环境不同的值 |

### 关键文件

| 文件 | 目的 |
|------|---------|
| `Dockerfile` | 多阶段容器构建 |
| `.github/workflows/deploy.yml` | CI/CD 管道 |
| `next.config.ts` | 构建配置 |
| `instrumentation.ts` | OpenTelemetry 设置 |
| `src/app/api/health/route.ts` | 健康检查端点 |

## 说明

### 1. 配置独立输出

```typescript
// next.config.ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  output: 'standalone',
  poweredByHeader: false,
  generateBuildId: async () => process.env.GIT_HASH || 'build',
}

export default nextConfig
```

### 2. 创建 Dockerfile

有关完整的多阶段构建、多架构支持和优化的参考，请参阅 [references/docker-patterns.md](references/docker-patterns.md)。

```dockerfile
# syntax=docker/dockerfile:1
FROM node:20-alpine AS base

FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1 NODE_ENV=production
ARG GIT_HASH NEXT_SERVER_ACTIONS_ENCRYPTION_KEY
ENV GIT_HASH=${GIT_HASH} NEXT_SERVER_ACTIONS_ENCRYPTION_KEY=${NEXT_SERVER_ACTIONS_ENCRYPTION_KEY}
RUN npm run build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 PORT=3000 HOSTNAME="0.0.0.0"
RUN addgroup --system --gid 1001 nodejs && adduser --system --uid 1001 nextjs
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
USER nextjs
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => r.statusCode === 200 ? process.exit(0) : process.exit(1))"
CMD ["node", "server.js"]
```

### 3. 设置 GitHub Actions

有关包含测试、安全扫描和部署策略的完整工作流的参考，请参阅 [references/github-actions.md](references/github-actions.md)。

```yaml
# .github/workflows/deploy.yml
name: 构建和部署
on:
  push:
    branches: [main, develop]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
      - id: generate-key
        run: echo "key=$(openssl rand -base64 32)" >> $GITHUB_OUTPUT
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            GIT_HASH=${{ github.sha }}
            NEXT_SERVER_ACTIONS_ENCRYPTION_KEY=${{ steps.generate-key.outputs.key }}
```

### 4. 配置环境变量

```typescript
// src/lib/env.ts
export function getEnv() {
  return {
    databaseUrl: process.env.DATABASE_URL!,
    apiKey: process.env.API_KEY!,
    publicApiUrl: process.env.NEXT_PUBLIC_API_URL!,
  }
}

export function validateEnv() {
  const required = ['DATABASE_URL', 'API_KEY', 'NEXT_PUBLIC_API_URL']
  const missing = required.filter((key) => !process.env[key])
  if (missing.length > 0) {
    throw new Error(`缺少必要的环境变量：${missing.join(', ')}`)
  }
}
```

### 5. 实现健康检查

```typescript
// src/app/api/health/route.ts
import { NextResponse } from 'next/server'

export const dynamic = 'force-dynamic'

export async function GET() {
  const checks = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || 'unknown',
    uptime: process.uptime(),
  }
  return NextResponse.json(checks)
}
```

### 6. 设置监控

有关 OpenTelemetry 配置、日志记录、告警和仪表板的参考，请参阅 [references/monitoring.md](references/monitoring.md)。

```typescript
// instrumentation.ts
import { registerOTel } from '@vercel/otel'

export function register() {
  registerOTel({
    serviceName: process.env.OTEL_SERVICE_NAME || 'next-app',
  })
}
```

### 7. 处理服务器动作加密

**关键**：为多服务器部署生成并设置一致的加密密钥：

```bash
# 生成密钥
openssl rand -base64 32

# 在 GitHub Actions 密钥中设置 NEXT_SERVER_ACTIONS_ENCRYPTION_KEY
```

如果没有此密钥，多服务器部署中的服务器动作会因 "Failed to find Server Action" 错误而失败。

## 最佳实践

- **Docker**：使用多阶段构建，启用独立输出，设置非根用户，包含健康检查
- **安全**：切勿提交 `.env.local`，仅使用 `NEXT_PUBLIC_` 公开值，设置 `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY`
- **性能**：使用 `output: 'standalone'`，为静态资源启用 CDN，使用 `next/image`
- **环境**：跨环境使用相同的 Docker 镜像，通过环境变量注入运行时配置

## 示例

```typescript
// next.config.ts
const nextConfig = {
  output: 'standalone',
  poweredByHeader: false,
  compress: true,
  generateBuildId: async () => process.env.GIT_HASH || 'build',
}
export default nextConfig
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://db:5432/myapp
      - NEXT_PUBLIC_API_URL=http://localhost:3000/api
```

## 限制和警告

### 限制

- 独立输出需要 Node.js 18+
- 服务器动作加密密钥必须在所有实例中一致
- 运行时环境变量仅在 `output: 'standalone'` 时有效
- OpenTelemetry 需要在项目根目录下有 instrumentation.ts

### 警告

- **切勿**使用 `NEXT_PUBLIC_` 前缀处理敏感值
- 始终为多服务器部署设置 `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY`
- 没有健康检查，编排器可能会将流量发送到不健康的实例
- 运行时环境变量不适用于静态导出 (`output: 'export'`)

## 参考

- **[references/docker-patterns.md](references/docker-patterns.md)** - 高级 Docker 配置、多架构构建、优化
- **[references/github-actions.md](references/github-actions.md)** - 完整 CI/CD 工作流、测试、安全扫描
- **[references/monitoring.md](references/monitoring.md)** - OpenTelemetry、日志记录、告警、仪表板
- **[references/deployment-platforms.md](references/deployment-platforms.md)** - 平台特定指南（Vercel、AWS、GCP、Azure）
