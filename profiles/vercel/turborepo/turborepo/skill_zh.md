# Turborepo Skill

面向 JavaScript/TypeScript 单仓库（Monorepo）的构建系统。Turborepo 通过依赖图缓存任务输出，并并行运行任务。

## 重要提示：打包任务，而非根任务

**优先使用打包（package）任务，而非根任务。**

在创建任务/脚本/流水线时，必须默认使用打包任务：

1. 将脚本添加到每个相关包 `package.json` 中
2. 在根目录的 `turbo.json` 中注册任务
3. 根目录 `package.json` 仅通过 `turbo run <task>` 进行委托

**不要**将任务逻辑放在根目录 `package.json` 中，即使该逻辑本可以放在包中。这会破坏 Turborepo 的并行化能力。

```json
// 正确做法：脚本在各自包中
// apps/web/package.json
{ "scripts": { "build": "next build", "lint": "eslint .", "test": "vitest" } }

// apps/api/package.json
{ "scripts": { "build": "tsc", "lint": "eslint .", "test": "vitest" } }

// packages/ui/package.json
{ "scripts": { "build": "tsc", "lint": "eslint .", "test": "vitest" } }
```

```json
// turbo.json - 注册任务
{
  "tasks": {
    "build": { "dependsOn": ["^build"], "outputs": ["dist/**"] },
    "lint": {},
    "test": { "dependsOn": ["build"] }
  }
}
```

```json
// Root package.json - 仅委托，无任务逻辑
{
  "scripts": {
    "build": "turbo run build",
    "lint": "turbo run lint",
    "test": "turbo run test"
  }
}
```

```json
// 错误做法：破坏并行化
// Root package.json
{
  "scripts": {
    "build": "cd apps/web && next build && cd ../api && tsc",
    "lint": "eslint apps/ packages/",
    "test": "vitest"
  }
}
```

根任务（`//#taskname`）仅用于真正无法在包中存在的任务，例如 Vitest Projects 的 `//#test`、仓库级别的发布脚本，或不调用 `turbo` 的工具。

## 次级规则：`turbo run` 与 `turbo`

**当命令写入代码时，始终使用 `turbo run`：**

```json
// package.json - 始终使用 "turbo run"
{
  "scripts": {
    "build": "turbo run build"
  }
}
```

```yaml
# CI 工作流 - 始终使用 "turbo run"
- run: turbo run build --affected
```

简写 `turbo <tasks>` 仅适用于手动或代理在终端中直接输入的一次性命令。切勿在 `package.json`、CI 或脚本中将 `turbo build` 写入其中。

## 快速决策树

### "我需要配置任务"

```
需要配置任务？
├─ 定义任务依赖 → references/configuration/tasks.md
├─ Lint/检查类型（并行 + 缓存）→ 使用 Transit Nodes 模式（见下文）
├─ 指定构建输出 → references/configuration/tasks.md#outputs
├─ 处理环境变量 → references/environment/RULE.md
├─ 设置开发/监听任务 → references/configuration/tasks.md#persistent
├─ 包特定的配置 → references/configuration/RULE.md#package-configurations
└─ 全局设置（cacheDir、daemon）→ references/configuration/global-options.md
```

### "缓存不工作"

```
缓存问题？
├─ 任务运行但输出未恢复 → 缺少 `outputs` 键
├─ 意外缓存未命中 → references/caching/gotchas.md
├─ 需要调试哈希输入 → 使用 --summarize 或 --dry
├─ 想完全跳过缓存 → 使用 --force 或 cache: false
├─ 远程缓存不工作 → references/caching/remote-cache.md
└─ 环境导致未命中 → references/environment/gotchas.md
```

### "只想运行已变更的包"

```
只运行已变更的部分？
├─ 已变更包及依赖方（推荐）→ turbo run build --affected
├─ 自定义基础分支 → TURBO_SCM_BASE=origin/develop turbo run build --affected
├─ 手动 Git 比对 → --filter=...[origin/main]
└─ 查看所有筛选选项 → references/filtering/RULE.md
```

**`--affected` 是仅运行已变更包的主要方式。** 它对比 `main`（回退至 `master`）——而不是仓库配置的回退分支——并包含依赖方。如需使用其他基础分支，请设置 `TURBO_SCM_BASE`。

### "我想筛选包"

```
筛选包？
├─ 仅已变更包 → --affected（见上文）
├─ 按包名 → --filter=web
├─ 按目录 → --filter=./apps/*
├─ 包 + 依赖 → --filter=web...
├─ 包 + 依赖方 → --filter=...web
└─ 复杂组合 → references/filtering/patterns.md
```

### "环境变量不生效"

```
环境问题？
├─ 运行时不可用变量 → 严格模式筛选（默认）
├─ 环境错误导致缓存命中 → 变量不在 `env` 键中
├─ .env 变更未触发重建 → .env 不在 `inputs` 中
├─ CI 变量缺失 → references/environment/gotchas.md
└─ 框架变量（NEXT_PUBLIC_*）→ 通过推理自动包含
```

### "我需要设置 CI"

```
设置 CI？
├─ GitHub Actions → references/ci/github-actions.md
├─ Vercel 部署 → references/ci/vercel.md
├─ CI 中的远程缓存 → references/caching/remote-cache.md
├─ 仅构建已变更包 → --affected 标志
├─ 跳过不必要的构建 → turbo-ignore（references/cli/commands.md）
└─ 无变更时跳过容器设置 → turbo-ignore
```

### "我想在开发过程中监听变更"

```
监听模式？
├─ 变更时重新运行任务 → turbo watch（references/watch/RULE.md）
├─ 依赖开发服务器 → 使用 `with` 键（references/configuration/tasks.md#with）
├─ 依赖变更时重启开发服务器 → 使用 `interruptible: true`
└─ 持久化开发任务 → 使用 `persistent: true`
```

### "我需要创建/组织包"

```
包创建/组织？
├─ 创建内部包 → references/best-practices/packages.md
├─ 仓库结构 → references/best-practices/structure.md
├─ 依赖管理 → references/best-practices/dependencies.md
├─ 最佳实践概览 → references/best-practices/RULE.md
├─ JIT 与编译包 → references/best-practices/packages.md#compilation-strategies
└─ 应用间共享代码 → references/best-practices/RULE.md#package-types
```

### "应该如何组织我的单仓库？"

```
单仓库结构？
├─ 标准布局（apps/、packages/）→ references/best-practices/RULE.md
├─ 包类型（apps 与库）→ references/best-practices/RULE.md#package-types
├─ 创建内部包 → references/best-practices/packages.md
├─ TypeScript 配置 → references/best-practices/structure.md#typescript-configuration
├─ ESLint 配置 → references/best-practices/structure.md#eslint-configuration
├─ 依赖管理 → references/best-practices/dependencies.md
└─ 强制包边界 → references/boundaries/RULE.md
```

### "我想强制执行架构边界"

```
强制执行边界？
├─ 检查违规 → turbo boundaries
├─ 标记包 → references/boundaries/RULE.md#tags
├─ 限制哪些包可以导入其他包 → references/boundaries/RULE.md#rule-types
└─ 防止跨包文件导入 → references/boundaries/RULE.md
```

## 关键反模式（Anti-Patterns）

### 在代码中使用 `turbo` 简写

**在 `package.json` 脚本和 CI 流水线中推荐使用 `turbo run`。** 简写 `turbo <task>` 旨在用于交互式终端使用场景。

```json
// 错误 - 在 package.json 中使用简写
{
  "scripts": {
    "build": "turbo build",
    "dev": "turbo dev"
  }
}

// 正确
{
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev"
  }
}
```

```yaml
# 错误 - 在 CI 中使用简写
- run: turbo build --affected

# 正确
- run: turbo run build --affected
```

### 根脚本绕过 Turbo

根目录 `package.json` 脚本必须委托给 `turbo run`，而非直接运行任务。

```json
// 错误 - 完全绕过 turbo
{
  "scripts": {
    "build": "bun build",
    "dev": "bun dev"
  }
}

// 正确 - 委托给 turbo
{
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev"
  }
}
```

### 使用 `&&` 串联 Turbo 任务

不要使用 `&&` 串联 Turbo 任务。由 Turbo 进行编排。

```json
// 错误 - Turbo 任务未使用 turbo run
{
  "scripts": {
    "changeset:publish": "bun build && changeset publish"
  }
}

// 正确
{
  "scripts": {
    "changeset:publish": "turbo run build && changeset publish"
  }
}
```

### 手动构建依赖的 `prebuild` 脚本

类似 `prebuild` 的脚本手动构建其他包，会绕过 Turborepo 的依赖图。

```json
// 错误 - 手动构建依赖
{
  "scripts": {
    "prebuild": "cd ../../packages/types && bun run build && cd ../utils && bun run build",
    "build": "next build"
  }
}
```

**不过，修复方案取决于是否声明了 workspace 依赖：**

1. **如果已声明依赖**（例如在 `package.json` 中声明 `"@repo/types": "workspace:*"`），请删除 `prebuild` 脚本。Turbo 的 `dependsOn: ["^build"]` 会自动处理此问题。

2. **如果未声明依赖**，则 `prebuild` 存在的原因是 `^build` 在没有依赖关系时不会触发。修复方法是：
   - 在 `package.json` 中添加依赖：`"@repo/types": "workspace:*"`
   - 然后删除 `prebuild` 脚本

```json
// 正确 - 声明依赖，由 turbo 处理构建顺序
// package.json
{
  "dependencies": {
    "@repo/types": "workspace:*",
    "@repo/utils": "workspace:*"
  },
  "scripts": {
    "build": "next build"
  }
}

// turbo.json
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"]
    }
  }
}
```

**关键洞察：** `^build` 仅在声明的依赖包中运行构建。无依赖声明 = 无自动构建顺序。

### `globalDependencies` 过于宽泛

`globalDependencies` 通过**全局哈希**影响所有包中的所有任务——任务无法仅通过 `inputs` 中的否定通配符来退出特定文件的配置。请具体明确。

```json
// 错误 - 大锤，影响所有哈希
{
  "globalDependencies": ["**/.env.*local"]
}

// 更好 - 移至任务级 inputs
{
  "globalDependencies": [".env"],
  "tasks": {
    "build": {
      "inputs": ["$TURBO_DEFAULT$", ".env*"],
      "outputs": ["dist/**"]
    }
  }
}
```

使用 `futureFlags.globalConfiguration` 时，此问题会得到缓解，因为 `global.inputs` 中的文件会被折叠到每个任务的 `inputs` 中（而非全局哈希）。任务可以排除特定文件：

```json
// 最佳 - 使用 global.inputs 并做每任务排除
{
  "futureFlags": { "globalConfiguration": true },
  "global": {
    "inputs": [".env"]
  },
  "tasks": {
    "build": { "outputs": ["dist/**"] },
    "lint": {
      "inputs": ["$TURBO_DEFAULT$", "!$TURBO_ROOT$/.env"]
    }
  }
}
```

### 任务配置重复

查找可在任务间合并的重复配置。Turborepo 支持共享配置模式。

```json
// 错误 - 任务间重复 env 和 inputs
{
  "tasks": {
    "build": {
      "env": ["API_URL", "DATABASE_URL"],
      "inputs": ["$TURBO_DEFAULT$", ".env*"]
    },
    "test": {
      "env": ["API_URL", "DATABASE_URL"],
      "inputs": ["$TURBO_DEFAULT$", ".env*"]
    },
    "dev": {
      "env": ["API_URL", "DATABASE_URL"],
      "inputs": ["$TURBO_DEFAULT$", ".env*"],
      "cache": false,
      "persistent": true
    }
  }
}

// 更好 - 使用 globalEnv 和 globalDependencies 共享配置
{
  "globalEnv": ["API_URL", "DATABASE_URL"],
  "globalDependencies": [".env*"],
  "tasks": {
    "build": {},
    "test": {},
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

**何时使用全局配置 vs 任务级配置：**

- `globalEnv` / `globalDependencies` - 影响所有任务，用于真正共享的配置
- 任务级 `env` / `inputs` - 仅当特定任务需要时使用

### 并非反模式：`env` 数组过大

`env` 数组很大（即使 50+ 个变量）**并非**问题。通常表明用户严谨地声明了其构建的环境依赖。请勿将此标记为问题。

### 使用 `--parallel` 标志

`--parallel` 标志会绕过 Turborepo 的依赖图。该标志已被弃用，将在未来的主版本中移除——请改用任务配置（`persistent`、`with`）代替。

```bash
# 错误 - 绕过依赖图
turbo run lint --parallel

# 正确 - 配置任务以允许并行执行
// 在 turbo.json 中设置适当的 dependsOn（或使用 transit nodes）
turbo run lint
```

### 根 `turbo.json` 中的包特定任务覆盖

当多个包需要不同的任务配置时，请使用**包配置**（包内 `turbo.json`）代替在根 `turbo.json` 中堆积 `package#task` 覆盖。

```json
// 错误 - 根 turbo.json 中大量包特定覆盖
{
  "tasks": {
    "test": { "dependsOn": ["build"] },
    "@repo/web#test": { "outputs": ["coverage/**"] },
    "@repo/api#test": { "outputs": ["coverage/**"] },
    "@repo/utils#test": { "outputs": [] },
    "@repo/cli#test": { "outputs": [] },
    "@repo/core#test": { "outputs": [] }
  }
}

// 正确 - 使用包配置
// 根 turbo.json - 仅基础配置
{
  "tasks": {
    "test": { "dependsOn": ["build"] }
  }
}

// packages/web/turbo.json - 包特定覆盖
{
  "extends": ["//"],
  "tasks": {
    "test": { "outputs": ["coverage/**"] }
  }
}

// packages/api/turbo.json
{
  "extends": ["//"],
  "tasks": {
    "test": { "outputs": ["coverage/**"] }
  }
}
```

**包配置的优势：**

- 将配置放在影响其对应的代码附近
- 根 `turbo.json` 保持简洁，专注于基础模式
- 更易理解每个包的独特之处
- 可与 `$TURBO_EXTENDS$` 配合使用，继承并扩展数组

**何时在根目录使用 `package#task`：**

- 单个包需要独特依赖（例如 `"deploy": { "dependsOn": ["web#build"] }`）
- 迁移期间临时覆盖

详见 `references/configuration/RULE.md#package-configurations` 了解完整细节。

### 在 `inputs` 中使用 `../` 跨越包边界

不要使用 `../` 等相对路径引用包外部的文件。请使用 `$TURBO_ROOT$` 代替。

```json
// 错误 - 跨越包边界遍历
{
  "tasks": {
    "build": {
      "inputs": ["$TURBO_DEFAULT$", "../shared-config.json"]
    }
  }
}

// 正确 - 使用 $TURBO_ROOT$ 指向仓库根目录
{
  "tasks": {
    "build": {
      "inputs": ["$TURBO_DEFAULT$", "$TURBO_ROOT$/shared-config.json"]
    }
  }
}
```

### 文件类任务缺少 `outputs`

**在标记缺少 `outputs` 之前，先检查任务实际产出的内容：**

1. 阅读包的脚本（例如 `"build": "tsc"`，`"test": "vitest"`）
2. 判断它是否向磁盘写入文件，或仅输出到标准输出
3. 仅在任务产出应被缓存的文件时才标记

```json
// 错误：build 产出文件但未缓存
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"]
    }
  }
}

// 正确：build 输出已缓存
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    }
  }
}
```

各框架常见输出：

- Next.js：`[".next/**", "!.next/cache/**", "!.next/dev/**"]`
- Vite/Rollup：`["dist/**"]`
- tsc：`["dist/**"]` 或自定义 `outDir`

**TypeScript 的 `--noEmit` 仍可产出缓存文件：**

当 `tsconfig.json` 中 `incremental: true` 时，即使不使用 `tsc --noEmit` 输出 JS，也会写入 `.tsbuildinfo` 文件。检查 `tsconfig` 后再假设无输出：

```json
// 若 tsconfig 有 incremental: true，tsc --noEmit 会产出缓存文件
{
  "tasks": {
    "typecheck": {
      "outputs": ["node_modules/.cache/tsbuildinfo.json"] // 或 tsBuildInfoFile 指向的位置
    }
  }
}
```

为 TypeScript 任务确定正确输出：

1. 检查 `tsconfig` 中是否启用 `incremental` 或 `composite`
2. 检查 `tsBuildInfoFile` 获取自定义缓存位置（默认：与 `outDir` 同级或项目根目录下）
3. 若无 incremental 模式，`tsc --noEmit` 不产出文件

### `^build` 与 `build` 混淆

```json
{
  "tasks": {
    // ^build = 先运行 DEPENDENCIES 中的 build（本包导入的其他包）
    "build": {
      "dependsOn": ["^build"]
    },
    // build（无 ^）= 先运行 SAME PACKAGE 中的 build
    "test": {
      "dependsOn": ["build"]
    },
    // pkg#task = 特定包的 task
    "deploy": {
      "dependsOn": ["web#build"]
    }
  }
}
```

### 环境变量未哈希（Not Hashed）

```json
// 错误：API_URL 变更不会导致重建
{
  "tasks": {
    "build": {
      "outputs": ["dist/**"]
    }
  }
}

// 正确：API_URL 变更使缓存失效
{
  "tasks": {
    "build": {
      "outputs": ["dist/**"],
      "env": ["API_URL", "API_KEY"]
    }
  }
}
```

### `.env` 文件不在 inputs 中

Turbo **不会**加载 `.env` 文件——由框架加载。但 Turbo 需要了解其变更：

```json
// 错误：.env 变更不会使缓存失效
{
  "tasks": {
    "build": {
      "env": ["API_URL"]
    }
  }
}

// 正确：.env 文件变更使缓存失效
{
  "tasks": {
    "build": {
      "env": ["API_URL"],
      "inputs": ["$TURBO_DEFAULT$", ".env", ".env.*"]
    }
  }
}
```

### 单仓库根目录的 `.env` 文件

仓库根目录的 `.env` 文件是反模式——即使是小型单仓库或启动模板也不应使用。它会建立包之间的隐式耦合，并使哪个包依赖哪个变量变得不明确。

```
// 错误 - 根 .env 隐式影响所有包
my-monorepo/
├── .env              # 哪个包使用这个？
├── apps/
│   ├── web/
│   └── api/
└── packages/

// 正确 - 需要 .env 的包内放置 .env
my-monorepo/
├── apps/
│   ├── web/
│   │   └── .env      # 明确：web 需要 DATABASE_URL
│   └── api/
│       └── .env      # 明确：api 需要 API_KEY
└── packages/
```

**根目录 `.env` 的问题：**

- 不明确哪个包消费哪个变量
- 所有包都获得所有变量（即使它们不需要）
- 缓存失效粒度粗（根 .env 变更使全部失效）
- 安全风险：包可能意外访问其他包专用的敏感变量
- 不良习惯从小处开始——启动模板应示范正确模式

**若必须共享变量**，请使用 `globalEnv` 明确共享内容，并说明原因。

### Strict Mode 过滤 CI 变量

默认情况下，Turborepo 仅筛选 `env`/`globalEnv` 中的环境变量。CI 变量可能缺失：

```json
// 若 CI 脚本需要 GITHUB_TOKEN 但未在 env 中：
{
  "globalPassThroughEnv": ["GITHUB_TOKEN", "CI"],
  "tasks": { ... }
}
```

或使用 `--env-mode=loose`（不推荐用于生产环境）。

### 应用中共享代码（应作为包）

```
// 错误：应用在内部共享代码
apps/
  web/
    shared/          # 这会破坏单仓库原则！
      utils.ts

// 正确：提取为包
packages/
  utils/
    src/utils.ts
```

### 跨包边界访问文件

```typescript
// 错误：访问其他包的内部
import { Button } from "../../packages/ui/src/button";

// 正确：正确安装并导入
import { Button } from "@repo/ui/button";
```

### 根目录依赖过多

```json
// 错误：应用在根目录
{
  "dependencies": {
    "react": "^18",
    "next": "^14"
  }
}

// 正确：根目录仅放仓库工具
{
  "devDependencies": {
    "turbo": "latest"
  }
}
```

## 常见任务配置

### 标准构建流水线

```json
{
  "$schema": "https://v2-11-3-canary-2.turborepo.dev/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**", "!.next/dev/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

如果存在需要并行执行且需失效缓存的任务，请添加 `transit` 任务（见下文）。

### 带有 `^dev` 模式的 `dev` 任务（用于 `turbo watch`）

根 `turbo.json` 中 `dependsOn: ["^dev"]` 且 `persistent: false` 的 `dev` 任务看似不寻常，但**对 `turbo watch` 工作流是正确的**：

```json
// 根 turbo.json
{
  "tasks": {
    "dev": {
      "dependsOn": ["^dev"],
      "cache": false,
      "persistent": false  // 包有一次性 dev 脚本
    }
  }
}

// 包 turbo.json（apps/web/turbo.json）
{
  "extends": ["//"],
  "tasks": {
    "dev": {
      "persistent": true  // 应用运行长时间运行的 dev 服务器
    }
  }
}
```

**为何如此有效：**

- **包**（如 `@acme/db`、`@acme/validators`）有 `"dev": "tsc"`——一次性类型生成，快速完成
- **应用**通过 `persistent: true` 覆盖，用于实际 dev 服务器（Next.js 等）
- **`turbo watch`** 在源文件变更时重新运行包的一次性 `dev` 脚本，保持类型同步

** intended 用法：** 运行 `turbo watch dev`（而非 `turbo run dev`）。监听模式会在文件变更时重新执行一次性任务，同时保持持久化任务持续运行。

**替代模式：** 使用独立的任务名如 `prepare` 或 `generate` 作为一次性依赖构建，使意图更清晰：

```json
{
  "tasks": {
    "prepare": {
      "dependsOn": ["^prepare"],
      "outputs": ["dist/**"]
    },
    "dev": {
      "dependsOn": ["prepare"],
      "cache": false,
      "persistent": true
    }
  }
}
```

### 用于并行任务且需失效缓存的 Transit Nodes

某些任务可以并行运行（不需要依赖的构建输出），但必须在依赖源代码变更时失效缓存。

**`dependsOn: ["^taskname"]` 的问题：**

- 强制顺序执行（慢）

**`dependsOn: []`（无依赖）的问题：**

- 允许并行执行（快）
- 但缓存**错误**——依赖源变更不会使缓存失效

**Transit Nodes 解决两者问题：**

```json
{
  "tasks": {
    "transit": { "dependsOn": ["^transit"] },
    "my-task": { "dependsOn": ["transit"] }
  }
}
```

`transit` 任务创建依赖关系，但不匹配任何实际脚本，因此任务并行执行，且缓存失效正确。

**如何识别需要此模式的任务：** 查找读取依赖源文件但不依赖其构建输出的任务。

### 带环境变量

```json
{
  "globalEnv": ["NODE_ENV"],
  "globalDependencies": [".env"],
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"],
      "env": ["API_URL", "DATABASE_URL"]
    }
  }
}
```

使用 `futureFlags.globalConfiguration` 时，相同配置会将全局设置在 `global` 下——`.env` 则变为每个任务级别的输入，而非全局哈希输入：

```json
{
  "futureFlags": { "globalConfiguration": true },
  "global": {
    "env": ["NODE_ENV"],
    "inputs": [".env"]
  },
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"],
      "env": ["API_URL", "DATABASE_URL"]
    }
  }
}
```

## 参考索引

### 配置

| 文件                                                                            | 用途                                     |
| ------------------------------------------------------------------------------- | ----------------------------------------- |
| [configuration/RULE.md](./references/configuration/RULE.md)                     | turbo.json 概览，包配置                                 |
| [configuration/tasks.md](./references/configuration/tasks.md)                   | dependsOn、outputs、inputs、env、cache、persistent |
| [configuration/global-options.md](./references/configuration/global-options.md) | globalEnv、globalDependencies、global 键、futureFlags、cacheDir、envMode |
| [configuration/gotchas.md](./references/configuration/gotchas.md)               | 常见配置错误                               |

### 缓存

| 文件                                                            | 用途                                       |
| --------------------------------------------------------------- | ------------------------------------------- |
| [caching/RULE.md](./references/caching/RULE.md)                 | 缓存工作原理，哈希输入                       |
| [caching/remote-cache.md](./references/caching/remote-cache.md) | Vercel 远程缓存、自托管、登录/链接             |
| [caching/gotchas.md](./references/caching/gotchas.md)           | 调试缓存未命中、--summarize、--dry           |

### 环境变量

| 文件                                                          | 用途                                     |
| ------------------------------------------------------------- | ----------------------------------------- |
| [environment/RULE.md](./references/environment/RULE.md)       | env、globalEnv、passThroughEnv             |
| [environment/modes.md](./references/environment/modes.md)     | 严格模式与宽松模式、框架推理               |
| [environment/gotchas.md](./references/environment/gotchas.md) | .env 文件、CI 问题                          |

### 筛选

| 文件                                                        | 用途                 |
| ----------------------------------------------------------- | -------------------- |
| [filtering/RULE.md](./references/filtering/RULE.md)         | --filter 语法概览     |
| [filtering/patterns.md](./references/filtering/patterns.md) | 常见筛选模式           |

### CI/CD

| 文件                                                      | 用途                         |
| --------------------------------------------------------- | ------------------------------- |
| [ci/RULE.md](./references/ci/RULE.md)                     | CI 通用原则                   |
| [ci/github-actions.md](./references/ci/github-actions.md) | 完整的 GitHub Actions 设置     |
| [ci/vercel.md](./references/ci/vercel.md)                 | Vercel 部署、turbo-ignore      |
| [ci/patterns.md](./references/ci/patterns.md)             | --affected、缓存策略            |

### CLI

| 文件                                            | 用途                                       |
| ----------------------------------------------- | ------------------------------------------- |
| [cli/RULE.md](./references/cli/RULE.md)         | turbo run 基础                            |
| [cli/commands.md](./references/cli/commands.md) | turbo run 标志、turbo-ignore、其他命令       |

### 最佳实践

| 文件                                                                          | 用途                                                         |
| ----------------------------------------------------------------------------- | --------------------------------------------------------------- |
| [best-practices/RULE.md](./references/best-practices/RULE.md)                 | 单仓库最佳实践概览                                |
| [best-practices/structure.md](./references/best-practices/structure.md)       | 仓库结构、工作区配置、TypeScript/ESLint 设置             |
| [best-practices/packages.md](./references/best-practices/packages.md)         | 创建内部包、JIT 与编译、导出                             |
| [best-practices/dependencies.md](./references/best-practices/dependencies.md) | 依赖管理、安装、版本同步                               |

### 监听模式

| 文件                                        | 用途                                         |
| ------------------------------------------- | ----------------------------------------------- |
| [watch/RULE.md](./references/watch/RULE.md) | turbo watch、可中断任务、开发工作流               |

### 边界（实验性）

| 文件                                                  | 用途                                               |
| ----------------------------------------------------- | ----------------------------------------------------- |
| [boundaries/RULE.md](./references/boundaries/RULE.md) | 强制包隔离、基于标签的依赖规则                           |

## 源文档说明

该技能基于 Turborepo 官方文档，地址：

- 源文件：Turborepo 仓库中的 `apps/docs/content/docs/`
- 实时链接：https://turborepo.dev/docs
