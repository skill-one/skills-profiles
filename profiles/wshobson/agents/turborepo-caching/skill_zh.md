# Turborepo 缓存

Turborepo 构建优化的生产模式。

## 何时使用此功能

- 设置新的 Turborepo 项目
- 配置构建流水线
- 实现远程缓存
- 优化 CI/CD 性能
- 从其他单体库工具迁移
- 调试缓存未命中

## 核心概念

### 1. Turborepo 架构

```
Workspace Root/
├── apps/
│   ├── web/
│   │   └── package.json
│   └── docs/
│       └── package.json
├── packages/
│   ├── ui/
│   │   └── package.json
│   └── config/
│       └── package.json
├── turbo.json
└── package.json
```

### 2. 流水线概念

| 概念        | 描述                      |
| -------------- | -------------------------------- |
| **dependsOn**  | 必须先完成的任务           |
| **cache**      | 是否缓存输出               |
| **outputs**    | 要缓存的文件               |
| **inputs**     | 影响缓存键的文件           |
| **persistent** | 长运行任务（开发服务器） |

## 模板

### 模板 1：turbo.json 配置

```json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": [".env", ".env.local"],
  "globalEnv": ["NODE_ENV", "VERCEL_URL"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"],
      "env": ["API_URL", "NEXT_PUBLIC_*"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"],
      "inputs": ["src/**/*.tsx", "src/**/*.ts", "test/**/*.ts"]
    },
    "lint": {
      "outputs": [],
      "cache": true
    },
    "typecheck": {
      "dependsOn": ["^build"],
      "outputs": []
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "clean": {
      "cache": false
    }
  }
}
```

### 模板 2：特定包的流水线

```json
// apps/web/turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "extends": ["//"],
  "pipeline": {
    "build": {
      "outputs": [".next/**", "!.next/cache/**"],
      "env": ["NEXT_PUBLIC_API_URL", "NEXT_PUBLIC_ANALYTICS_ID"]
    },
    "test": {
      "outputs": ["coverage/**"],
      "inputs": ["src/**", "tests/**", "jest.config.js"]
    }
  }
}
```

### 模板 3：使用 Vercel 的远程缓存

```bash
# 登录 Vercel
npx turbo login

# 链接 Vercel 项目
npx turbo link

# 使用远程缓存运行
turbo build --remote-only

# CI 环境变量
TURBO_TOKEN=your-token
TURBO_TEAM=your-team
```

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:

env:
  TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
  TURBO_TEAM: ${{ vars.TURBO_TEAM }}

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: "npm"

      - name: 安装依赖
        run: npm ci

      - name: 构建
        run: npx turbo build --filter='...[origin/main]'

      - name: 测试
        run: npx turbo test --filter='...[origin/main]'
```

### 模板 4：自托管远程缓存

```typescript
// 自定义远程缓存服务器（Express）
import express from "express";
import { createReadStream, createWriteStream } from "fs";
import { mkdir } from "fs/promises";
import { join } from "path";

const app = express();
const CACHE_DIR = "./cache";

// 获取 artifact
app.get("/v8/artifacts/:hash", async (req, res) => {
  const { hash } = req.params;
  const team = req.query.teamId || "default";
  const filePath = join(CACHE_DIR, team, hash);

  try {
    const stream = createReadStream(filePath);
    stream.pipe(res);
  } catch {
    res.status(404).send("Not found");
  }
});

// 存储 artifact
app.put("/v8/artifacts/:hash", async (req, res) => {
  const { hash } = req.params;
  const team = req.query.teamId || "default";
  const dir = join(CACHE_DIR, team);
  const filePath = join(dir, hash);

  await mkdir(dir, { recursive: true });

  const stream = createWriteStream(filePath);
  req.pipe(stream);

  stream.on("finish", () => {
    res.json({
      urls: [`${req.protocol}://${req.get("host")}/v8/artifacts/${hash}`],
    });
  });
});

// 检查 artifact 是否存在
app.head("/v8/artifacts/:hash", async (req, res) => {
  const { hash } = req.params;
  const team = req.query.teamId || "default";
  const filePath = join(CACHE_DIR, team, hash);

  try {
    await fs.access(filePath);
    res.status(200).end();
  } catch {
    res.status(404).end();
  }
});

app.listen(3000);
```

```json
// 自托管缓存的 turbo.json
{
  "remoteCache": {
    "signature": false
  }
}
```

```bash
# 使用自托管缓存
turbo build --api="http://localhost:3000" --token="my-token" --team="my-team"
```

### 模板 5：过滤和作用域

```bash
# 构建特定包
turbo build --filter=@myorg/web

# 构建包及其依赖
turbo build --filter=@myorg/web...

# 构建包及其被依赖项
turbo build --filter=...@myorg/ui

# 自 main 以来变更的包
turbo build --filter='...[origin/main]'

# 构建目录中的包
turbo build --filter='./apps/*'

# 组合过滤器
turbo build --filter=@myorg/web --filter=@myorg/docs

# 排除包
turbo build --filter='!@myorg/docs'

# 包含变更的依赖
turbo build --filter='...[HEAD^1]...'
```

### 模板 6：高级流水线配置

```json
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"],
      "inputs": ["$TURBO_DEFAULT$", "!**/*.md", "!**/*.test.*"]
    },
    "test": {
      "dependsOn": ["^build"],
      "outputs": ["coverage/**"],
      "inputs": ["src/**", "tests/**", "*.config.*"],
      "env": ["CI", "NODE_ENV"]
    },
    "test:e2e": {
      "dependsOn": ["build"],
      "outputs": [],
      "cache": false
    },
    "deploy": {
      "dependsOn": ["build", "test", "lint"],
      "outputs": [],
      "cache": false
    },
    "db:generate": {
      "cache": false
    },
    "db:push": {
      "cache": false,
      "dependsOn": ["db:generate"]
    },
    "@myorg/web#build": {
      "dependsOn": ["^build", "@myorg/db#db:generate"],
      "outputs": [".next/**"],
      "env": ["NEXT_PUBLIC_*"]
    }
  }
}
```

### 模板 7：根 package.json 设置

```json
{
  "name": "my-turborepo",
  "private": true,
  "workspaces": ["apps/*", "packages/*"],
  "scripts": {
    "build": "turbo build",
    "dev": "turbo dev",
    "lint": "turbo lint",
    "test": "turbo test",
    "clean": "turbo clean && rm -rf node_modules",
    "format": "prettier --write \"**/*.{ts,tsx,md}\"",
    "changeset": "changeset",
    "version-packages": "changeset version",
    "release": "turbo build --filter=./packages/* && changeset publish"
  },
  "devDependencies": {
    "turbo": "^1.10.0",
    "prettier": "^3.0.0",
    "@changesets/cli": "^2.26.0"
  },
  "packageManager": "npm@10.0.0"
}
```

## 调试缓存

```bash
# 干运行以查看将要运行的内容
turbo build --dry-run

# 带哈希的详细输出
turbo build --verbosity=2

# 显示任务图
turbo build --graph

# 强制不缓存
turbo build --force

# 显示缓存状态
turbo build --summarize

# 调试特定任务
TURBO_LOG_VERBOSITY=debug turbo build --filter=@myorg/web
```

## 最佳实践

### 应该做

- **明确定义输入** - 避免缓存失效
- **使用工作区协议** - `"@myorg/ui": "workspace:*"`
- **启用远程缓存** - 跨 CI 和本地共享
- **在 CI 中过滤** - 仅构建受影响的包
- **缓存构建输出** - 不缓存源文件

### 不应该做

- **不要缓存开发服务器** - 使用 `persistent: true`
- **不要在 env 中包含密钥** - 使用运行时环境变量
- **不要忽略 dependsOn** - 导致竞争条件
- **不要过度过滤** - 可能遗漏依赖
