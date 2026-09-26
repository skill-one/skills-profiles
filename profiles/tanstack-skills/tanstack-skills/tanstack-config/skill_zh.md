## 概述

TanStack Config 为 JavaScript/TypeScript 包开发提供了一个主观的、最小化配置的工具包。它包括基于 Vite 的构建配置、ESLint 预设、使用语义版本控制的发布自动化，以及与 TypeScript、Prettier、Changesets 和 GitHub Actions 的集成。专为使用 pnpm 和 Nx 的单体仓库工作流程而设计。

**包名：** `@tanstack/config`
**状态：** 稳定

## 安装

```bash
npm install @tanstack/config --save-dev
# 或者
pnpm add @tanstack/config -D
```

## Vite 构建配置

### 基本设置

```typescript
// vite.config.ts
import { defineConfig, mergeConfig } from 'vitest/config'
import { tanstackViteConfig } from '@tanstack/config/vite'

const config = defineConfig({
  // 您的自定义 Vite 配置
})

export default mergeConfig(
  config,
  tanstackViteConfig({
    entry: './src/index.ts',
    srcDir: './src',
    exclude: ['./src/__tests__'],
  })
)
```

### 多入口点

```typescript
import { tanstackViteConfig } from '@tanstack/config/vite'

export default tanstackViteConfig({
  entry: [
    './src/index.ts',
    './src/adapters.ts',
    './src/utils.ts',
  ],
  srcDir: './src',
})
```

### 构建选项

```typescript
tanstackViteConfig({
  entry: './src/index.ts',
  srcDir: './src',
  exclude: ['./src/__tests__', './src/**/*.test.ts'],
  // 生成 ESM 和 CJS 输出
  // 生成 .d.ts 声明文件
  // 处理 tree-shaking 配置
})
```

## ESLint 配置

### 基本设置

```javascript
// eslint.config.js
import { tanstackEslintConfig } from '@tanstack/config/eslint'

export default tanstackEslintConfig
```

### 扩展配置

```javascript
// eslint.config.js
import { tanstackEslintConfig } from '@tanstack/config/eslint'

export default [
  ...tanstackEslintConfig,
  {
    rules: {
      // 自定义覆盖
      '@typescript-eslint/no-explicit-any': 'warn',
    },
  },
]
```

## 发布

### 发布配置

```typescript
// publish.config.ts 或通过 CLI 使用
import { tanstackPublishConfig } from '@tanstack/config/publish'

export default tanstackPublishConfig({
  // Publint 合规的默认值
  // 语义版本控制自动化
  // 更改日志生成
})
```

### package.json 设置

```json
{
  "name": "@myorg/my-package",
  "version": "0.0.0",
  "type": "module",
  "main": "dist/cjs/index.cjs",
  "module": "dist/esm/index.js",
  "types": "dist/esm/index.d.ts",
  "exports": {
    ".": {
      "import": {
        "types": "./dist/esm/index.d.ts",
        "default": "./dist/esm/index.js"
      },
      "require": {
        "types": "./dist/cjs/index.d.cts",
        "default": "./dist/cjs/index.cjs"
      }
    }
  },
  "files": ["dist", "src"],
  "scripts": {
    "build": "vite build",
    "lint": "eslint .",
    "test": "vitest"
  }
}
```

## TypeScript 配置

### tsconfig.json

```json
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

## Changesets 集成

### 设置

```bash
npx changeset init
```

### 创建 Changeset

```bash
npx changeset
# 交互式提示：选择包、提升版本类型、摘要
```

### Changeset 配置

```json
// .changeset/config.json
{
  "$schema": "https://unpkg.com/@changesets/config@3.0.0/schema.json",
  "changelog": "@changesets/cli/changelog",
  "commit": false,
  "fixed": [],
  "linked": [],
  "access": "public",
  "baseBranch": "main",
  "updateInternalDependencies": "patch"
}
```

## GitHub Actions 工作流

### CI/CD 管道

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
      - run: pnpm install
      - run: pnpm build
      - run: pnpm lint
      - run: pnpm test
```

### 发布工作流

```yaml
# .github/workflows/publish.yml
name: Publish

on:
  push:
    branches: [main]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          registry-url: 'https://registry.npmjs.org'
      - run: pnpm install
      - run: pnpm build
      - name: 创建发布 Pull Request 或发布
        uses: changesets/action@v1
        with:
          publish: pnpm publish -r
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## 单体仓库设置 (pnpm + Nx)

### 工作区配置

```yaml
# pnpm-workspace.yaml
packages:
  - 'packages/*'
  - 'examples/*'
```

### Nx 配置

```json
// nx.json
{
  "tasksRunnerOptions": {
    "default": {
      "runner": "nx/tasks-runners/default",
      "options": {
        "cacheableOperations": ["build", "lint", "test"]
      }
    }
  },
  "targetDefaults": {
    "build": {
      "dependsOn": ["^build"]
    }
  }
}
```

## Prettier 配置

```json
// .prettierrc
{
  "semi": false,
  "singleQuote": true,
  "trailingComma": "all",
  "printWidth": 80
}
```

## EditorConfig

```ini
# .editorconfig
root = true

[*]
indent_style = space
indent_size = 2
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true
```

## 最佳实践

1. **使用 Vite 配置进行构建** - 处理 ESM/CJS 双输出和声明
2. **在 package.json 中使用 publint 合规的导出** 以确保兼容性
3. **使用 Changesets** 在单体仓库中进行版本管理
4. **在 package.json 中设置 `"type": "module"`** 用于 ESM 优先的包
5. **在 `files` 中包含 `src` 和 `dist`** 以便源码映射调试
6. **使用 Nx 缓存** 以加快单体仓库的构建速度
7. **始终生成声明文件** (`.d.ts`) 以供 TypeScript 消费者使用
8. **使用 ESLint 配置** 作为跨包的一致基线
9. **使用 GitHub Actions 和 Changesets 自动化发布**

## 常见陷阱

- package.json 中缺少 `exports` 字段（会破坏现代打包器）
- 未设置 `"type": "module"`（会导致 ESM 导入问题）
- 忘记在构建输出中包含声明文件
- 未从构建中排除测试文件
- 在运行 publint 验证之前发布
- 未在 tsconfig 中配置 `moduleResolution: "bundler"`
- 单体仓库包之间版本不一致（使用 Changesets `linked`）
