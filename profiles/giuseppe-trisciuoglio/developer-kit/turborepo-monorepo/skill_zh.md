# Turborepo 单体仓库

## 概述

提供 Turborepo 单体仓库管理的指导：工作区创建、`turbo.json` 任务配置、Next.js/NestJS 集成、测试流程（Vitest/Jest）、CI/CD 设置以及构建性能优化。

## 何时使用

- 创建或初始化 Turborepo 工作区
- 配置具有依赖项和输出的 `turbo.json` 任务
- 在单体仓库结构中设置 Next.js/NestJS 应用
- 配置 Vitest/Jest 测试流程
- 构建 CI/CD 工作流（GitHub Actions, GitLab CI）
- 使用 Vercel Remote Cache 实现远程缓存
- 优化构建时间和缓存命中率
- 调试任务依赖或缓存问题
- 从其他单体仓库工具迁移到 Turborepo

## 说明

### 工作区创建

1. **创建新工作区：**
   ```bash
   pnpm create turbo@latest my-workspace
   cd my-workspace
   ```

2. **在现有项目中初始化：**
   ```bash
   pnpm add -D -w turbo
   ```

3. **在根目录创建 turbo.json**（最小配置）：
   ```json
   {
     "$schema": "https://turborepo.dev/schema.json",
     "pipeline": {
       "build": { "dependsOn": ["^build"], "outputs": ["dist/**", ".next/**"] },
       "lint": { "outputs": [] },
       "test": { "dependsOn": ["build"], "outputs": ["coverage/**"] }
     }
   }
   ```

4. **在根 `package.json` 中添加脚本：**
   ```json
   { "scripts": { "build": "turbo run build", "dev": "turbo run dev", "lint": "turbo run lint", "test": "turbo run test", "clean": "turbo run clean" } }
   ```

5. **在 CI 之前验证任务图：**
   ```bash
   turbo run build --dry-run --filter=...  # 验证任务执行顺序
   ```

### 任务配置

1. **在 `turbo.json` 中配置任务：**
   ```json
   { "pipeline": { "build": { "dependsOn": ["^build"], "outputs": ["dist/**"] }, "test": { "dependsOn": ["build"], "outputs": ["coverage/**"] }, "lint": { "outputs": [] } } }
   ```

2. **运行任务：**
   ```bash
   turbo run build                      # 所有包
   turbo run lint test build           # 多个任务
   turbo run build --filter=web       # 特定包
   ```

3. **并行类型检查**（使用 transit 节点以避免缓存问题）：
   ```json
   { "pipeline": { "transit": { "dependsOn": ["^transit"] }, "typecheck": { "dependsOn": ["transit"] } } }
   ```

4. **提交前验证：**
   ```bash
   turbo run build --dry-run  # 检查任务顺序和受影响的包
   ```

### 框架集成

**Next.js:** 输出 `".next/**"` 和环境变量 `["NEXT_PUBLIC_*"]` - 参考 [references/nextjs-config.md](references/nextjs-config.md)

**NestJS:** 输出 `"dist/**"`，开发任务使用 `cache: false, persistent: true` - 参考 [references/nestjs-config.md](references/nestjs-config.md)

### 测试设置

1. **Vitest 配置：**
   ```json
   {
     "pipeline": {
       "test": {
         "outputs": [],
         "inputs": ["$TURBO_DEFAULT$", "vitest.config.ts"]
       },
       "test:watch": {
         "cache": false,
         "persistent": true
       }
     }
   }
   ```

2. **运行受影响的测试：**
   ```bash
   turbo run test --filter=[HEAD^]
   ```
   参考 [references/testing-config.md](references/testing-config.md) 获取完整的测试设置。

### 包配置

1. **创建包特定的 turbo.json：**
   ```json
   {
     "extends": ["//"],
     "tasks": {
       "build": {
         "outputs": ["$TURBO_EXTENDS$", ".next/**"]
       }
     }
   }
   ```
   参考 [references/package-configs.md](references/package-configs.md) 获取详细的包配置模式。

### CI/CD 设置

1. **带有验证检查点的 GitHub Actions：**
   ```yaml
   - name: 安装依赖项
     run: pnpm install

   - name: 验证受影响的包（干运行）
     run: pnpm turbo run build --filter=[HEAD^] --dry-run
     # VALIDATE: 检查输出以确认只有预期的包会被构建

   - name: 运行测试
     run: pnpm run test --filter=[HEAD^]

   - name: 构建受影响的包
     run: pnpm run build --filter=[HEAD^]

   - name: 验证缓存命中
     run: pnpm turbo run build --filter=[HEAD^] --dry-run | grep "Cache"
     # VALIDATE: 确认未更改的包的缓存命中
   ```

2. **远程缓存设置：**
   ```bash
   # 登录 Vercel
   npx turbo login

   # 链接仓库
   npx turbo link
   ```
   参考 [references/ci-cd.md](references/ci-cd.md) 获取完整的 CI/CD 设置示例。

## 任务属性参考

| 属性 | 描述 | 示例 |
|----------|-------------|---------|
| `dependsOn` | 必须先完成的任务 | `["^build"]` - 依赖项优先 |
| `outputs` | 要缓存的文件/文件夹 | `["dist/**"]` |
| `inputs` | 用于缓存哈希的文件 | `["src/**/*.ts"]` |
| `env` | 影响哈希的环境变量 | `["DATABASE_URL"]` |
| `cache` | 启用/禁用缓存 | `true` 或 `false` |
| `persistent` | 长任务 | `true` 用于开发服务器 |
| `outputLogs` | 日志详细程度 | `"full"`, `"new-only"`, `"errors-only"` |

### 依赖模式

- `^task` - 在依赖项中首先运行任务（拓扑顺序）
- `task` - 在同一包中首先运行任务
- `package#task` - 运行特定包的任务

### 过滤语法

| 过滤器 | 描述 |
|--------|-------------|
| `web` | 仅 web 包 |
| `web...` | web + 所有依赖项 |
| `...web` | web + 所有依赖项 |
| `...web...` | web + 依赖项 + 依赖项 |
| `[HEAD^]` | 自上次提交以来更改的包 |
| `./apps/*` | apps/ 中的所有包 |

## 最佳实践

### 性能优化

1. **使用特定输出** - 仅缓存所需内容
2. **微调输入** - 排除不影响输出的文件
3. **Transit 节点** - 启用并行类型检查
4. **远程缓存** - 在团队/CI 之间共享缓存
5. **包配置** - 按包自定义行为

### 缓存策略

```json
{
  "pipeline": {
    "build": {
      "outputs": ["dist/**"],
      "inputs": ["$TURBO_DEFAULT$", "!README.md", "!**/*.md"]
    }
  }
}
```

### 任务组织

- **独立任务** - 无 `dependsOn`：lint, format, spellcheck
- **构建任务** - `dependsOn: ["^build"]`：build, compile
- **测试任务** - `dependsOn: ["build"]`：test, e2e
- **开发任务** - `cache: false, persistent: true`：dev, watch

## 常见问题

### 任务未按顺序运行

**问题：** 任务执行顺序错误

**解决方案：** 检查 `dependsOn` 配置

```json
{
  "build": {
    "dependsOn": ["^build"]
  }
}
```

### 未更改文件出现缓存未命中

**问题：** 缓存意外失效

**解决方案：** 查看 `globalDependencies` 和 `inputs`

```json
{
  "globalDependencies": ["tsconfig.json"],
  "pipeline": {
    "build": {
      "inputs": ["$TURBO_DEFAULT$", "!*.md"]
    }
  }
}
```

### 缓存命中后出现类型错误

**问题：** 由于缓存未捕获 TypeScript 错误

**解决方案：** 使用 transit 节点进行类型检查

```json
{
  "transit": { "dependsOn": ["^transit"] },
  "typecheck": { "dependsOn": ["transit"] }
}
```

## 示例

### 示例 1：创建新工作区

**输入：** "创建带有 Next.js 和 NestJS 的 Turborepo"

```bash
pnpm create turbo@latest my-workspace
cd my-workspace

# 添加 Next.js 应用
pnpm add next react react-dom -F apps/web

# 添加 NestJS API
pnpm add @nestjs/core @nestjs/common -F apps/api
```

### 示例 2：配置测试流程

**输入：** "为所有包设置 Vitest"

```json
{
  "pipeline": {
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"],
      "inputs": ["$TURBO_DEFAULT$", "vitest.config.ts"]
    },
    "test:watch": {
      "cache": false,
      "persistent": true
    }
  }
}
```

### 示例 3：在 CI 中运行受影响的测试

**输入：** "仅测试已更改的包"

```bash
pnpm run test --filter=[HEAD^]
```

### 示例 4：调试缓存问题

**输入：** "为什么我的缓存未命中？"

```bash
# 干运行以查看将要执行的内容
turbo run build --dry-run --filter=web

# 显示哈希输入
turbo run build --force --filter=web
```

## 限制和警告

- **Node.js 18+** 是 Turborepo 的要求
- **包管理器字段** 在根 `package.json` 中是必需的
- **输出必须指定** 缓存才能生效
- **持久任务** 不能有依赖项
- **Windows**：推荐使用 WSL 或 Git Bash
- **远程缓存** 需要Vercel账户或自托管解决方案
- **大型单体仓库** 可能需要增加 `concurrency` 设置

## 参考文件

有关特定主题的详细指导，请参阅：

| 主题 | 参考文件 |
|-------|----------------|
| turbo.json 模板 | [references/turbo.json](references/turbo.json) |
| Next.js 集成 | [references/nextjs-config.md](references/nextjs-config.md) |
| NestJS 集成 | [references/nestjs-config.md](references/nestjs-config.md) |
| Vitest/Jest/Playwright | [references/testing-config.md](references/testing-config.md) |
| GitHub/CircleCI/GitLab CI | [references/ci-cd.md](references/ci-cd.md) |
| 包配置 | [references/package-configs.md](references/package-configs.md) |
