# Turborepo 技巧

JavaScript/TypeScript 单体仓库的构建系统。Turborepo 缓存任务输出，并根据依赖关系图并行运行任务。

## 重要提示：为包配置任务，而非根任务

**优先为包配置任务，而非根任务。**

在创建任务/脚本/管道时，你必须默认为包配置任务：

1. 将脚本添加到每个相关包的 `package.json`
2. 在根 `turbo.json` 中注册任务
3. 根 `package.json` 仅通过 `turbo run <task>` 进行委托

**不要**在包中可以存在的情况下，将任务逻辑放在根 `package.json` 中。这会破坏 Turborepo 的并行化。

```json
// 应该这样做：每个包中的脚本
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
// 根 package.json - 仅委托，无任务逻辑
{
  "scripts": {
    "build": "turbo run build",
    "lint": "turbo run lint",
    "test": "turbo run test"
  }
}
```

```json
// 不要这样做 - 这会破坏并行化
// 根 package.json
{
  "scripts": {
    "build": "cd apps/web && next build && cd ../api && tsc",
    "lint": "eslint apps/ packages/",
    "test": "vitest"
  }
}
```

根任务 (`//#taskname`) 仅用于那些确实无法存在于包中的任务，例如 Vitest 项目的 `//#test`、全仓库发布脚本或不会调用 `turbo` 的工具。

## 次要规则：`turbo run` vs `turbo`

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

**简写 `turbo <task>` 仅适用于一次性终端命令**，由人类或代理直接输入。永远不要将 `turbo build` 写入 package.json、CI 或脚本。

## 快速决策树

### "我需要配置一个任务"

```
需要配置任务？
├─ 定义任务依赖关系 → references/configuration/tasks.md
├─ Lint/检查类型 (并行 + 缓存) → 使用 Transit Nodes 模式 (见下文)
├─ 指定构建输出 → references/configuration/tasks.md#outputs
├─ 处理环境变量 → references/environment/RULE.md
├─ 设置开发/监视任务 → references/configuration/tasks.md#persistent
├─ 包特定配置 → references/configuration/RULE.md#package-configurations
└─ 全局设置 (cacheDir, daemon) → references/configuration/global-options.md
```

### "我的缓存不起作用"

```
缓存问题？
├─ 任务运行但输出未恢复 → 缺少 `outputs` 键
├─ 缓存意外未命中 → references/caching/gotchas.md
├─ 需要调试哈希输入 → 使用 --summarize 或 --dry
├─ 完全跳过缓存 → 使用 --force 或 cache: false
├─ 远程缓存未工作 → references/caching/remote-cache.md
└─ 环境导致未命中 → references/environment/gotchas.md
```

### "我只想要运行已更改的包"

```
只运行已更改的？
├─ 已更改的包 + 依赖项 (推荐) → turbo run build --affected
├─ 自定义基础分支 → TURBO_SCM_BASE=origin/develop turbo run build --affected
├─ 手动 git 比较 → --filter=...[origin/main]
└─ 查看所有过滤选项 → references/filtering/RULE.md
```

**`--affected` 是运行仅更改包的主要方式。** 它与 `main` (回退到 `master`) 比较 — 不是仓库配置的默认分支 — 并包括依赖项。设置 `TURBO_SCM_BASE` 用于任何其他基础分支。

### "我想过滤包"

```
过滤包？
├─ 仅更改的包 → --affected (见上文)
├─ 按包名 → --filter=web
├─ 按目录 → --filter=./apps/*
├─ 包 + 依赖项 → --filter=web...
├─ 包 + 依赖项 → --filter=...web
└─ 复杂组合 → references/filtering/patterns.md
```

### "环境变量不起作用"

```
环境问题？
├─ 运行时变量不可用 → 严格模式过滤 (默认)
├─ 缓存命中但环境不正确 → 变量不在 `env` 键中
├─ .env 变化未导致重建 → .env 不在 `inputs` 中
├─ CI 变量缺失 → references/environment/gotchas.md
└─ 框架变量 (NEXT_PUBLIC_*) → 通过推断自动包含
```

### "我需要设置 CI"

```
CI 设置？
├─ GitHub Actions → references/ci/github-actions.md
├─ Vercel 部署 → references/ci/vercel.md
├─ CI 中的远程缓存 → references/caching/remote-cache.md
├─ 只构建已更改的包 → --affected 标志
├─ 跳过不必要的构建 → turbo-ignore (references/cli/commands.md)
└─ 无更改时跳过容器设置 → turbo-ignore
```

### "我想要在开发期间监视更改"

```
监视模式？
├─ 更改时重新运行任务 → turbo watch (references/watch/RULE.md)
├─ 依赖项的开发服务器 → 使用 `with` 键 (references/configuration/tasks.md#with)
├─ 依赖项更改时重启开发服务器 → 使用 `interruptible: true`
└─ 持久化开发任务 → 使用 `persistent: true`
```

### "我需要创建/结构化一个包"

```
创建/结构化包？
├─ 创建内部包 → references/best-practices/packages.md
├─ 仓库结构 → references/best-practices/structure.md
├─ 依赖项管理 → references/best-practices/dependencies.md
├─ 最佳实践概述 → references/best-practices/RULE.md
├─ JIT vs 编译包 → references/best-practices/packages.md#compilation-strategies
└─ 在应用之间共享代码 → references/best-practices/RULE.md#package-types
```

### "我应该如何构建我的单体仓库？"

```
单体仓库结构？
├─ 标准布局 (apps/, packages/) → references/best-practices/RULE.md
├─ 包类型 (apps vs 库) → references/best-practices/RULE.md#package-types
├─ 创建内部包 → references/best-practices/packages.md
├─ TypeScript 配置 → references/best-practices/structure.md#typescript-configuration
├─ ESLint 配置 → references/best-practices/structure.md#eslint-configuration
├─ 依赖项管理 → references/best-practices/dependencies.md
└─ 强制包边界 → references/boundaries/RULE.md
```

### "我想强制执行架构边界"

```
强制边界？
├─ 检查违规 → turbo boundaries
├─ 标记包 → references/boundaries/RULE.md#tags
├─ 限制哪些包可以导入其他包 → references/boundaries/RULE.md#rule-types
└─ 防止跨包文件导入 → references/boundaries/RULE.md
```

## 严重反模式

### 在代码中使用 `turbo` 简写

**推荐在 package.json 脚本和 CI 工作流中使用 `turbo run`。** 简写 `turbo <task>` 仅适用于交互式终端使用。

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

根 `package.json` 脚本必须委托到 `turbo run`，而不是直接运行任务。

```json
// 错误 - 完全绕过 Turbo
{
  "scripts": {
    "build": "bun build",
    "dev": "bun dev"
  }
}

// 正确 - 委托到 turbo
{
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev"
  }
}
```

### 使用 `&&` 链接 Turbo 任务

不要使用 `&&` 链接 Turbo 任务。让 Turbo 进行编排。

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

### 手动构建依赖项的 `prebuild` 脚本

像 `prebuild` 这样的脚本手动构建其他包会绕过 Turborepo 的依赖关系图。

```json
// 错误 - 手动构建依赖项
{
  "scripts": {
    "prebuild": "cd ../../packages/types && bun run build && cd ../utils && bun run build",
    "build": "next build"
  }
}
```

**但是，修复方法取决于工作空间依赖项是否声明：**

1. **如果依赖项已声明** (例如，在 package.json 中 `"@repo/types": "workspace:*"`)，则删除 `prebuild` 脚本。Turbo 的 `dependsOn: ["^build"]` 会自动处理此情况。

2. **如果依赖项未声明**，`prebuild` 存在是因为没有依赖关系关系，`^build` 不会触发。修复方法是：
   - 将依赖项添加到 package.json: `"@repo/types": "workspace:*"`
   - 然后删除 `prebuild` 脚本

```json
// 正确 - 声明依赖项，让 turbo 处理构建顺序
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

**关键洞察：** `^build` 仅在列出的包中运行构建。没有依赖项声明 = 没有自动构建排序。

### 过于宽泛的 `globalDependencies`

`globalDependencies` 通过**全局哈希**影响所有包中的所有任务 — 任务无法选择特定文件，即使 `inputs` 中有否定通配符。要具体。

```json
// 错误 - 重拳出击，影响所有哈希
{
  "globalDependencies": ["**/.env.*local"]
}

// 更好 - 移动到任务级 inputs
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

使用 `futureFlags.globalConfiguration`，这个问题会减少，因为 `global.inputs` 文件被折叠到每个任务的输入中 (不是全局哈希)。任务可以排除特定文件：

```json
// 最佳 - global.inputs 与每个任务的排除
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

### 重复的任务配置

查找跨任务重复的配置，这些配置可以合并。Turborepo 支持共享配置模式。

```json
// 错误 - 跨任务重复 env 和 inputs
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

// 更好 - 使用 globalEnv 和 globalDependencies 进行共享配置
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

**何时使用全局 vs 任务级：**

- `globalEnv` / `globalDependencies` - 影响所有任务，用于真正共享的配置
- 任务级 `env` / `inputs` - 仅当特定任务需要时使用

### 不是反模式：大型 `env` 数组

一个大型 `env` 数组 (即使 50+ 个变量) **不是**问题。这通常意味着用户在声明构建的环境依赖项方面非常彻底。不要将此视为问题。

### 使用 `--parallel` 标志

`--parallel` 标志绕过 Turborepo 的依赖关系图。它将在未来的主要版本中删除 — 使用任务配置 (`persistent`, `with`) 代替。

```bash
# 错误 - 绕过依赖关系图
turbo run lint --parallel

# 正确 - 配置任务以允许并行执行
# 在 turbo.json 中设置 dependsOn 适当 (或使用 transit nodes)
turbo run lint
```

### 包特定任务覆盖在根 turbo.json 中

当多个包需要不同的任务配置时，使用**包配置** (`每个包中的 turbo.json`) 而不是在根 `turbo.json` 中堆砌 `package#task` 覆盖。

```json
// 错误 - 根 turbo.json 中有多个包特定覆盖
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
// 根 turbo.json - 仅基本配置
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

**包配置的优点：**

- 将配置保留在它影响的代码附近
- 根 turbo.json 保持干净，专注于基本模式
- 更容易理解每个包的特殊之处
- 使用 `$TURBO_EXTENDS$` 继承 + 扩展数组

**何时使用 `package#task` 在根中：**

- 单个包需要唯一依赖项 (例如，`"deploy": { "dependsOn": ["web#build"] }`)
- 迁移期间的临时覆盖

有关完整详细信息，请参阅 `references/configuration/RULE.md#package-configurations`。

### 在 `inputs` 中使用 `../` 遍历出包

不要使用 `../` 等相对路径引用包外的文件。使用 `$TURBO_ROOT$` 代替。

```json
// 错误 - 遍历出包
{
  "tasks": {
    "build": {
      "inputs": ["$TURBO_DEFAULT$", "../shared-config.json"]
    }
  }
}

// 正确 - 使用 $TURBO_ROOT$ 指向仓库根
{
  "tasks": {
    "build": {
      "inputs": ["$TURBO_DEFAULT$", "$TURBO_ROOT$/shared-config.json"]
    }
  }
}
```

### 产生文件的任务缺少 `outputs`

**在标记缺少 `outputs` 之前，检查任务实际产生的内容：**

1. 读取包的脚本 (例如，`"build": "tsc"`, `"test": "vitest"`)
2. 确定它是否将文件写入磁盘或仅输出到 stdout
3. 仅当任务产生应该缓存的文件时才标记

```json
// 错误: build 产生文件但它们没有被缓存
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"]
    }
  }
}

// 正确: build 输出被缓存
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    }
  }
}
```

框架的常见输出：

- Next.js: `[".next/**", "!.next/cache/**", "!.next/dev/**"]`
- Vite/Rollup: `["dist/**"]`
- tsc: `["dist/**"]` 或自定义 `outDir`

**TypeScript `--noEmit` 仍然可以产生缓存文件：**

当 `incremental: true` 在 tsconfig.json 中，`tsc --noEmit` 即使不输出 JS 也会写入 `.tsbuildinfo` 文件。在假设没有输出之前检查 tsconfig：

```json
// 如果 tsconfig 有 incremental: true, tsc --noEmit 产生缓存文件
{
  "tasks": {
    "typecheck": {
      "outputs": ["node_modules/.cache/tsbuildinfo.json"] // 或 wherever tsBuildInfoFile 指向的位置
    }
  }
}
```

要确定 TypeScript 任务的正确输出：

1. 检查 `incremental` 或 `composite` 是否在 tsconfig 中启用
2. 检查 `tsBuildInfoFile` 以获取自定义缓存位置 (默认：与 `outDir` 一起或位于项目根目录)
3. 如果没有增量模式，`tsc --noEmit` 产生没有文件

### `^build` vs `build` 混淆

```json
{
  "tasks": {
    // ^build = 在依赖项中首先运行构建 (此任务导入的其他包)
    "build": {
      "dependsOn": ["^build"]
    },
    // build (无 ^) = 在同一包中首先运行构建
    "test": {
      "dependsOn": ["build"]
    },
    // pkg#task = 特定包的任务
    "deploy": {
      "dependsOn": ["web#build"]
    }
  }
}
```

### 环境变量未哈希

```json
// 错误: API_URL 变化不会导致重建
{
  "tasks": {
    "build": {
      "outputs": ["dist/**"]
    }
  }

// 正确: API_URL 变化使缓存失效
{
  "tasks": {
    "build": {
      "outputs": ["dist/**"],
      "env": ["API_URL", "API_KEY"]
    }
  }
}
```

### `.env` 文件不在 Inputs 中

Turborepo 不加载 `.env` 文件 - 你的框架会加载。但 Turborepo 需要知道更改：

```json
// 错误: .env 变化不会导致重建
{
  "tasks": {
    "build": {
      "env": ["API_URL"]
    }
  }
}

// 正确: .env 文件变化使缓存失效
{
  "tasks": {
    "build": {
      "env": ["API_URL"],
      "inputs": ["$TURBO_DEFAULT$", ".env", ".env.*"]
    }
  }
}
```

### 单体仓库中的根 `.env` 文件

单体仓库中的根 `.env` 文件是一个反模式 — 即使对于小型单体仓库或启动模板也是如此。它创建了包之间的隐式耦合，并使它不明确哪些包依赖于哪些变量。

```
// 错误 - 根 .env 隐式影响所有包
my-monorepo/
├── .env              # 哪些包使用这个？
├── apps/
│   ├── web/
│   └── api/
└── packages/

// 正确 - 包中的 .env 文件
my-monorepo/
├── apps/
│   ├── web/
│   │   └── .env      # 清晰: web 需要 DATABASE_URL
│   └── api/
│       └── .env      # 清晰: api 需要 API_KEY
└── packages/
```

**根 `.env` 的问题：**

- 不清楚哪些包消耗哪些变量
- 所有包都会收到所有变量 (即使它们不需要)
- 缓存失效粒度粗略 (根 .env 变化使所有内容失效)
- 安全风险：包可能会意外访问其他包打算用于其他包的敏感变量
- 小错误会导致坏习惯 — 启动模板应该建模正确的模式

**如果你必须共享变量**，使用 `globalEnv` 来明确共享的内容，并记录原因。

**`--env-mode=loose` (不推荐用于生产)。**

### 应用中的共享代码 (应该是一个包)

```
// 错误: 应用内部的共享代码
apps/
  web/
    shared/          # 这会破坏单体仓库原则！
      utils.ts

// 正确: 提取到一个包
packages/
  utils/
    src/utils.ts
```

### 跨包边界访问文件

```typescript
// 错误: 访问另一个包的内部
import { Button } from "../../packages/ui/src/button";

// 正确: 正确安装和导入
import { Button } from "@repo/ui/button";
```

### 过多的根依赖项

```json
// 错误: 应用依赖项在根中
{
  "dependencies": {
    "react": "^18",
    "next": "^14"
  }
}

// 正确: 仅在根中包含仓库工具
{
  "devDependencies": {
    "turbo": "latest"
  }
}
```

## 常见任务配置

### 标准构建管道

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

添加一个 `transit` 任务如果你有需要并行执行和缓存失效的任务 (见下文)。

### 使用 `^dev` 模式的开发任务 (用于 `turbo watch`)

根 `turbo.json` 中的 `dev` 任务具有 `dependsOn: ["^dev"]` 和 `persistent: false` 可能看起来不寻常，但**正确用于 `turbo watch` 工作流**：

```json
// 根 turbo.json
{
  "tasks": {
    "dev": {
      "dependsOn": ["^dev"],
      "cache": false,
      "persistent": false  // 包有一个 Shot dev 脚本
    }
  }
}

// 包 turbo.json (apps/web/turbo.json)
{
  "extends": ["//"],
  "tasks": {
    "dev": {
      "persistent": true  // 应用运行长时间开发服务器
    }
  }
}
```

**为什么这样工作：**

- **包** (例如，`@acme/db`, `@acme/validators`) 有 `"dev": "tsc"` — 一次性生成类型，完成速度快
- **应用** 使用 `persistent: true` 运行实际的开发服务器 (Next.js 等)
- **`turbo watch`** 重新运行包的 `dev` 脚本，保持类型同步

**预期用法：** 运行 `turbo watch dev` (不要 `turbo run dev`)。监视模式在文件更改时重新执行一次性任务，同时保持持久化任务运行。

**替代模式：** 使用 `prepare` 或 `generate` 这样的单独任务名称，以便更清楚地表达意图：

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

### Transit Nodes for Parallel Tasks with Cache Invalidation

某些任务可以并行运行 (不需要依赖项的构建输出) 但必须在依赖项源代码更改时使缓存失效。

**`dependsOn: ["^taskname"]` 的问题：**

- 强制顺序执行 (慢)

**`dependsOn: []` (无依赖项) 的问题：**

- 允许并行执行 (快)
- 但缓存不正确 - 依赖项源代码更改不会使缓存失效

**Transit Nodes 解决了这两个问题：**

```json
{
  "tasks": {
    "transit": { "dependsOn": ["^transit"] },
    "my-task": { "dependsOn": ["transit"] }
  }
```

`transit` 任务创建依赖关系，但匹配任何实际脚本，因此任务可以并行运行并具有正确的缓存失效。

**如何识别需要此模式的任务：** 查找读取依赖项源文件但不需要其构建输出的任务。

### 使用环境变量

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

使用 `futureFlags.globalConfiguration`，相同的配置移动到 `global` 下 — `.env` 成为每个任务的输入而不是全局哈希输入：

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
      "outputs": ["dist/**"]
    },
    "lint": {
      "inputs": ["$TURBO_DEFAULT$", "!$TURBO_ROOT$/.env"]
    }
  }
}
```

## 参考索引

### 配置

| 文件                                                                            | 目的                                                                   |
| ------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| [configuration/RULE.md](./references/configuration/RULE.md)                     | turbo.json 概览，包配置                                                   |
| [configuration/tasks.md](./references/configuration/tasks.md)                   | dependsOn, outputs, inputs, env, cache, persistent                        |
| [configuration/global-options.md](./references/configuration/global-options.md) | globalEnv, globalDependencies, global key, futureFlags, cacheDir, envMode |
| [configuration/gotchas.md](./references/configuration/gotchas.md)               | 常见配置错误                                                         |

### 缓存

| 文件                                                            | 目的                                      |
| --------------------------------------------------------------- | -------------------------------------------- |
| [caching/RULE.md](./references/caching/RULE.md)                 | 缓存工作原理，哈希输入               |
| [caching/remote-cache.md](./references/caching/remote-cache.md) | Vercel 远程缓存，自托管，登录/链接 |
| [caching/gotchas.md](./references/caching/gotchas.md)           | 调试缓存未命中，--summarize, --dry   |

### 环境变量

| 文件                                                          | 目的                                   |
| ------------------------------------------------------------- | ----------------------------------------- |
| [environment/RULE.md](./references/environment/RULE.md)       | env, globalEnv, passThroughEnv            |
| [environment/modes.md](./references/environment/modes.md)     | 严格 vs Loose 模式，框架推断             |
| [environment/gotchas.md](./references/environment/gotchas.md) | .env 文件，CI 问题                     |

### 过滤

| 文件                                                        | 目的                  |
| ----------------------------------------------------------- | ------------------------ |
| [filtering/RULE.md](./references/filtering/RULE.md)         | --filter 语法概述   |
| [filtering/patterns.md](./references/filtering/patterns.md) | 常见过滤模式   |

### CI/CD

| 文件                                                      | 目的                         |
| --------------------------------------------------------- | ------------------------------- |
| [ci/RULE.md](./references/ci/RULE.md)                     | 一般 CI 原则           |
| [ci/github-actions.md](./references/ci/github-actions.md) | 完整 GitHub Actions 设置   |
| [ci/vercel.md](./references/ci/vercel.md)                 | Vercel 部署             |
| [ci/patterns.md](./references/ci/patterns.md)             | --affected, 缓存策略  |

### CLI

| 文件                                            | 目的                                       |
| ----------------------------------------------- | --------------------------------------------- |
| [cli/RULE.md](./references/cli/RULE.md)         | turbo run 基础知识                              |
| [cli/commands.md](./references/cli/commands.md) | turbo run 标志，turbo-ignore，其他命令 |

### 最佳实践

| 文件                                                                          | 目的                                                         |
| ----------------------------------------------------------------------------- | --------------------------------------------------------------- |
| [best-practices/RULE.md](./references/best-practices/RULE.md)                 | 单体仓库最佳实践概述                                |
| [best-practices/structure.md](./references/best-practices/structure.md)       | 仓库结构，工作空间配置，TypeScript/ESLint 设置                 |
| [best-practices/packages.md](./references/best-practices/packages.md)         | 创建内部包，JIT vs 编译包，导出            |
| [best-practices/dependencies.md](./references/best-practices/dependencies.md) | 依赖项管理，安装，版本同步                 |

### 监视模式

| 文件                                        | 目的                                         |
| ------------------------------------------- | ----------------------------------------------- |
| [watch/RULE.md](./references/watch/RULE.md) | turbo watch，可中断任务，开发工作流 |

### 边界 (实验性)

| 文件                                                  | 目的                                               |
| ----------------------------------------------------- | ----------------------------------------------------- |
| [boundaries/RULE.md](./references/boundaries/RULE.md) | 强制包隔离，基于标签的依赖关系规则               |

## 源文档

此技巧基于 Turborepo 官方文档：

- 源：`apps/docs/content/docs/` 在 Turborepo 仓库中
- 在线：https://turborepo.dev/docs
