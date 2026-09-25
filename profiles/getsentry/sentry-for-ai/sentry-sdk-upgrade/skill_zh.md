> [所有技能](../../SKILL_TREE.md) > [工作流](../sentry-workflow/SKILL.md) > SDK 升级

# Sentry JavaScript SDK 升级

使用 AI 指导的迁移，跨主要版本升级 Sentry JavaScript SDK。

## 在以下情况下调用此技能

- 用户询问“升级 Sentry”或“迁移 Sentry SDK”
- 用户在版本更新后提到已弃用的 Sentry API 或破坏性变更
- 用户想从 v7 迁移到 v8，v8 迁移到 v9，或任何主要版本跳跃
- 用户在更新 `@sentry/*` 包版本后遇到错误
- 用户询问 Sentry 迁移指南或变更日志

## 第一阶段：检测

识别当前 Sentry SDK 版本、目标版本和框架。

### 1.1 读取 package.json

```bash
cat package.json | grep -E '"@sentry/' | head -20
```

提取：
- 所有 `@sentry/*` 包及其当前版本
- 当前主版本（例如，`7.x`、`8.x`、`9.x`）

### 1.2 检测框架

检查 `package.json` 依赖项中的框架指示符：

| 依赖项 | 框架 | Sentry 包 |
|---|---|---|
| `next` | Next.js | `@sentry/nextjs` |
| `nuxt` 或 `@nuxt/kit` | Nuxt | `@sentry/nuxt` |
| `@sveltejs/kit` | SvelteKit | `@sentry/sveltekit` |
| `@remix-run/node` | Remix | `@sentry/remix` |
| `react`（无 Next/Remix） | React SPA | `@sentry/react` |
| `@angular/core` | Angular | `@sentry/angular` |
| `vue`（无 Nuxt） | Vue | `@sentry/vue` |
| `express` | Express | `@sentry/node` |
| `@nestjs/core` | NestJS | `@sentry/nestjs` |
| `@solidjs/start` | SolidStart | `@sentry/solidstart` |
| `astro` | Astro | `@sentry/astro` |
| `bun` 类型或运行时 | Bun | `@sentry/bun` |
| `@cloudflare/workers-types` | Cloudflare | `@sentry/cloudflare` |
| 以上均无（Node.js） | Node.js | `@sentry/node` |

### 1.3 查找 Sentry 配置文件

```bash
grep -rn "from '@sentry/\|require('@sentry/" --include="*.ts" --include="*.js" --include="*.tsx" --include="*.jsx" --include="*.mjs" --include="*.cjs" -l
```

```bash
find . -name "sentry.*" -o -name "*.sentry.*" -o -name "instrumentation.*" | grep -v node_modules | grep -v .next | grep -v .nuxt
```

### 1.4 检测已弃用模式

扫描指示需要哪些迁移步骤的模式：

```bash
# v7 模式（需要 v7→v8 迁移）
grep -rn "from '@sentry/hub'\|from '@sentry/tracing'\|from '@sentry/integrations'\|from '@sentry/serverless'\|from '@sentry/replay'" --include="*.ts" --include="*.js" --include="*.tsx" --include="*.jsx" -l
grep -rn "new BrowserTracing\|new Replay\|startTransaction\|configureScope\|Handlers\.requestHandler\|Handlers\.errorHandler" --include="*.ts" --include="*.js" --include="*.tsx" --include="*.jsx" -l

# v8 模式（需要 v8→v9 迁移）
grep -rn "from '@sentry/utils'\|from '@sentry/types'" --include="*.ts" --include="*.js" --include="*.tsx" --include="*.jsx" -l
grep -rn "getCurrentHub\|enableTracing\|captureUserFeedback\|@WithSentry\|autoSessionTracking" --include="*.ts" --include="*.js" --include="*.tsx" --include="*.jsx" -l
```

### 1.5 确定目标版本

如果用户未指定目标版本，建议最新主版本（截至本文写作时为 v9）。如果用户已更新包版本但代码已损坏，则从 `package.json` 检测目标版本。

## 第二阶段：建议

根据检测到的状态，提供迁移摘要。

### 2.1 计算迁移路径

- **单跳**：例如，v8 到 v9
- **多跳**：例如，v7 到 v9（先应用 v7→v8 变更，然后 v8→v9）

对于多跳迁移，逐步应用代码变更，但一次更新包版本到最终目标。

### 2.2 展示破坏性变更摘要

加载相应的版本特定参考：
- v7→v8: [references/v7-to-v8.md](references/v7-to-v8.md)
- v8→v9: [references/v8-to-v9.md](references/v8-to-v9.md)
- v9→v10: [references/v9-to-v10.md](references/v9-to-v10.md)

按复杂度分类，提供具体的变更摘要：

**可自动修复**（直接应用）：
- 包导入重命名（例如，`@sentry/utils` 到 `@sentry/core`）
- 简单方法重命名（例如，`@WithSentry` 到 `@SentryExceptionCaptured`）
- 配置选项替换（例如，`enableTracing` 到 `tracesSampleRate`）

**AI 辅助**（解释并建议）：
- Hub 移除与变量存储模式
- 性能 API 迁移（事务到跨度）
- 复杂配置重构（Vue 追踪选项，Next.js 配置合并）
- Sampler `transactionContext` 平坦化

**手动审查**（标记给用户）：
- 无等效的已移除 API
- 行为变更（采样，源映射默认值）
- 自定义传输修改

### 2.3 确认范围

询问用户：
- 确认迁移路径（例如，“v8 到 v9”）
- 确认是否要执行所有变更或特定类别
- 注意：`npx @sentry/wizard -i upgrade` 存在作为 v8→v9 的 CLI 替代方案，但可能无法处理所有模式

## 第三阶段：指导

逐文件逐步进行变更。

### 3.1 处理每个 Sentry 导入的文件

对于第一阶段 1.3 中识别的每个文件：

1. **读取文件**以了解当前 Sentry 使用情况
2. **直接应用可自动修复的变更**：
   - 包导入重命名
   - 方法/函数重命名
   - 简单配置选项替换
3. **对于 AI 辅助的变更**，解释需要变更的内容及原因，然后建议具体编辑
4. **对于不确定的变更**，显示代码并要求用户确认

### 3.2 按类别应用变更

按以下顺序处理变更：

#### 第一步：包导入更新
替换已移除/重命名的包导入。参考版本特定的迁移文件以获取完整映射。

#### 第二步：API 重命名
应用机械方法和方法重命名。

#### 第三步：配置变更
更新 `Sentry.init()` 选项和构建配置。

#### 第四步：复杂模式迁移
处理需要理解上下文的模式：
- 存储在变量中的 Hub 使用
- 基于事务的性能代码
- 自定义集成类
- 框架特定包装器

#### 第五步：更新 package.json 版本

将所有 `@sentry/*` 包更新为目标版本。所有包必须位于同一主版本。

```bash
# 检测包管理器
if [ -f "yarn.lock" ]; then
  echo "yarn"
elif [ -f "pnpm-lock.yaml" ]; then
  echo "pnpm"
else
  echo "npm"
fi
```

使用检测到的包管理器安装更新后的依赖项。

#### 第六步：验证构建

```bash
# 检查类型错误
npx tsc --noEmit 2>&1 | head -50

# 运行构建
npm run build 2>&1 | tail -20
```

修复任何剩余的类型错误或构建失败。

### 3.3 框架特定步骤

参考 [references/upgrade-patterns.md](references/upgrade-patterns.md) 以获取框架特定配置文件位置和验证步骤。

**Next.js**：检查 `instrumentation.ts`、`next.config.ts` 包装器，客户端和服务器配置。
**Nuxt**：检查 Nuxt 模块配置和两个插件文件。
**SvelteKit**：检查钩子文件和 Vite 配置。
**Express/Node**：验证早期初始化顺序。
**NestJS**：检查装饰器和过滤器重命名。

## 第四阶段：交叉链接

### 4.1 验证

- [ ] 所有 `@sentry/*` 包位于同一版本
- [ ] 无来自已移除包的导入错误
- [ ] TypeScript 编译通过
- [ ] 构建成功
- [ ] 测试通过（如果存在）

建议添加一个测试错误：

```js
// 暂时添加以验证升级后 Sentry 是否正常工作
setTimeout(() => {
  throw new Error('Sentry 升级验证 - 安全删除');
}, 3000);
```

### 4.2 目标版本中的新功能

提及新版本中用户可能想启用的新功能：

**v8 新功能**：基于 OpenTelemetry 的 Node 追踪、自动数据库/HTTP 仪器、函数集成、新的跨度 API

**v9 新功能**：结构化日志 (`Sentry.logger.*`)、改进的源映射处理、简化配置

### 4.3 相关资源

- [官方迁移指南（v7→v8）](https://docs.sentry.io/platforms/javascript/migration/v7-to-v8/)
- [官方迁移指南（v8→v9）](https://docs.sentry.io/platforms/javascript/migration/v8-to-v9/)
- [Sentry JavaScript SDK 变更日志](https://github.com/getsentry/sentry-javascript/blob/develop/CHANGELOG.md)

如果用户有其他 Sentry SDK（Python、Ruby、Go 等）也需要升级，请注意此技能仅涵盖 JavaScript SDK。
