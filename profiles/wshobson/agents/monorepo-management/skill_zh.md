# 单一代码库管理

构建高效、可扩展的单一代码库，实现代码共享、一致的工具链以及跨多个包和应用程序的原子化变更。

## 使用此技能的场景

- 设置新的单一代码库项目
- 从多代码库迁移到单一代码库
- 优化构建和测试性能
- 管理共享依赖项
- 实现代码共享策略
- 为单一代码库设置 CI/CD
- 版本控制和发布包
- 调试单一代码库特定问题

## 核心概念

### 1. 为什么使用单一代码库？

**优势：**

- 共享代码和依赖项
- 跨项目的原子化提交
- 一致的工具链和标准
- 更容易重构
- 简化依赖项管理
- 更好的代码可见性

**挑战：**

- 大规模下的构建性能
- CI/CD 复杂性
- 访问控制
- 大型 Git 仓库

### 2. 单一代码库工具

**包管理器：**

- pnpm workspaces（推荐）
- npm workspaces
- Yarn workspaces

**构建系统：**

- Turborepo（大多数场景推荐）
- Nx（功能丰富，复杂）
- Lerna（较旧，已进入维护模式）

## Turborepo 设置

### 初始设置

```bash
# 创建新的单一代码库
npx create-turbo@latest my-monorepo
cd my-monorepo

# 结构：
# apps/
#   web/          - Next.js 应用
#   docs/         - 文档站点
# packages/
#   ui/           - 共享 UI 组件
#   config/       - 共享配置
#   tsconfig/     - 共享 TypeScript 配置
# turbo.json      - Turborepo 配置
# package.json    - 根 package.json
```

### 配置

```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    },
    "lint": {
      "outputs": []
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "type-check": {
      "dependsOn": ["^build"],
      "outputs": []
    }
  }
}
```

```json
// package.json (根)
{
  "name": "my-monorepo",
  "private": true,
  "workspaces": ["apps/*", "packages/*"],
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "format": "prettier --write \"**/*.{ts,tsx,md}\"",
    "clean": "turbo run clean && rm -rf node_modules"
  },
  "devDependencies": {
    "turbo": "^1.10.0",
    "prettier": "^3.0.0",
    "typescript": "^5.0.0"
  },
  "packageManager": "pnpm@8.0.0"
}
```

### 包结构

```json
// packages/ui/package.json
{
  "name": "@repo/ui",
  "version": "0.0.0",
  "private": true,
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "types": "./dist/index.d.ts"
    },
    "./button": {
      "import": "./dist/button.js",
      "types": "./dist/button.d.ts"
    }
  },
  "scripts": {
    "build": "tsup src/index.ts --format esm,cjs --dts",
    "dev": "tsup src/index.ts --format esm,cjs --dts --watch",
    "lint": "eslint src/",
    "type-check": "tsc --noEmit"
  },
  "devDependencies": {
    "@repo/tsconfig": "workspace:*",
    "tsup": "^7.0.0",
    "typescript": "^5.0.0"
  },
  "dependencies": {
    "react": "^18.2.0"
  }
}
```

## 详细模式和实例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。

## 最佳实践

1. **一致的版本控制**：跨工作区锁定依赖项版本
2. **共享配置**：集中管理 ESLint、TypeScript、Prettier 配置
3. **依赖项图**：保持无环，避免循环依赖
4. **有效缓存**：正确配置输入/输出
5. **类型安全**：前后端共享类型
6. **测试策略**：包中单元测试，应用中端到端测试
7. **文档**：每个包中包含 README
8. **发布策略**：使用 changesets 进行版本控制

## 常见陷阱

- **循环依赖**：A 依赖 B，B 依赖 A
- **幽灵依赖**：使用不在 package.json 中的依赖项
- **缓存输入错误**：Turborepo 输入中缺少文件
- **过度共享**：共享本应独立的代码
- **共享不足**：跨包重复代码
- **大型单一代码库**：没有适当工具，构建变慢

## 发布包

```bash
# 使用 Changesets
pnpm add -Dw @changesets/cli
pnpm changeset init

# 创建 changeset
pnpm changeset

# 版本化包
pnpm changeset version

# 发布
pnpm changeset publish
```

```yaml
# .github/workflows/release.yml
- name: 创建发布 Pull Request 或发布
  uses: changesets/action@v1
  with:
    publish: pnpm release
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```
