# tsdown - 简洁的库捆绑器

基于Rolldown和Oxc的TypeScript/JavaScript库的极速捆绑器。

## 运行时要求

`tsdown` 需要 **Node.js 22.18.0 或更高版本运行**（仅构建时）。然而，通过 [`target`](references/option-target.md) 选项，捆绑输出可以针对更低版本的 Node.js，因此使用 tsdown 构建的库 **在运行时不受 Node.js 22+ 的限制**。

如果你的包需要支持 Node.js 18 / 20：

- **在 CI 中使用 Node.js 22+ 构建**（例如，设置 `target: 'node18'` 或 `target: 'node20'`）。
- **在打算支持的较低 Node.js 版本上测试构建输出（或打包的 tarball）** — 例如，使用矩阵作业在 Node.js 18 / 20 / 22 上运行已发布包的测试。

## 使用场景

- 为 npm 构建 TypeScript/JavaScript 库
- 生成 TypeScript 声明文件 (.d.ts)
- 捆绑多种格式（ESM、CJS、IIFE、UMD）
- 通过树摇和压缩优化捆绑包
- 从 tsup 迁移时最小化改动
- 构建 React、Vue、Solid 或 Svelte 组件库

## 快速入门

```bash
# 安装
pnpm add -D tsdown

# 基本用法
npx tsdown

# 使用配置文件
npx tsdown --config tsdown.config.ts

# 监视模式
npx tsdown --watch

# 从 tsup 迁移
npx tsdown-migrate
```

## 基本配置

```ts
import { defineConfig } from 'tsdown'

export default defineConfig({
  entry: ['./src/index.ts'],
  format: ['esm', 'cjs'],
  dts: true,
  clean: true,
})
```

## 核心参考

| 主题 | 描述 | 参考 |
|-------|-------------|-----------|
| 入门指南 | 安装、首次捆绑、CLI 基础 | [guide-getting-started](references/guide-getting-started.md) |
| 配置文件 | 配置文件格式、多个配置、工作区 | [option-config-file](references/option-config-file.md) |
| CLI 参考 | 所有 CLI 命令和选项 | [reference-cli](references/reference-cli.md) |
| 从 tsup 迁移 | 迁移指南和兼容性说明 | [guide-migrate-from-tsup](references/guide-migrate-from-tsup.md) |
| 插件 | Rolldown、Rollup、Unplugin 支持 | [advanced-plugins](references/advanced-plugins.md) |

> 对于完整的迁移辅助和完整的选项映射，安装专门的 [`tsdown-migrate`](../tsdown-migrate/SKILL.md) 技能：`npx skills add rolldown/tsdown --skill tsdown-migrate`
| 钩子 | 用于自定义逻辑的生命周期钩子 | [advanced-hooks](references/advanced-hooks.md) |
| 程序化 API | 从 Node.js 脚本构建 | [advanced-programmatic](references/advanced-programmatic.md) |
| Rolldown 选项 | 直接将选项传递给 Rolldown | [advanced-rolldown-options](references/advanced-rolldown-options.md) |
| CI 环境 | CI 检测、`'ci-only'` / `'local-only'` 值 | [advanced-ci](references/advanced-ci.md) |

## 构建选项

| 选项 | 用法 | 参考 |
|--------|-------|-----------|
| 入口点 | `entry: ['src/*.ts', '!**/*.test.ts']` | [option-entry](references/option-entry.md) |
| 输出格式 | `format: ['esm', 'cjs', 'iife', 'umd']` | [option-output-format](references/option-output-format.md) |
| 输出目录 | `outDir: 'dist'`, `outExtensions` | [option-output-directory](references/option-output-directory.md) |
| 类型声明 | `dts: true`, `dts: { sourcemap, compilerOptions, vue }` | [option-dts](references/option-dts.md) |
| 目标环境 | `target: 'es2020'`, `target: 'esnext'` | [option-target](references/option-target.md) |
| 平台 | `platform: 'node'`, `platform: 'browser'` | [option-platform](references/option-platform.md) |
| 树摇 | `treeshake: true`, 自定义选项 | [option-tree-shaking](references/option-tree-shaking.md) |
| 压缩 | `minify: true`, `minify: 'dce-only'` | [option-minification](references/option-minification.md) |
| 源映射 | `sourcemap: true`, `'inline'`, `'hidden'` | [option-sourcemap](references/option-sourcemap.md) |
| 监视模式 | `watch: true`, 监视选项 | [option-watch-mode](references/option-watch-mode.md) |
| 清理 | `clean: true`, 清理模式 | [option-cleaning](references/option-cleaning.md) |
| 日志级别 | `logLevel: 'silent'`, `failOnWarn: false` | [option-log-level](references/option-log-level.md) |

## 依赖处理

| 功能 | 用法 | 参考 |
|---------|-------|-----------|
| 从不捆绑 | `deps: { neverBundle: ['react', /^@myorg\//] }` | [option-dependencies](references/option-dependencies.md) |
| 总是捆绑 | `deps: { alwaysBundle: ['dep-to-bundle'] }` | [option-dependencies](references/option-dependencies.md) |
| 仅捆绑 | `deps: { onlyBundle: ['cac', 'bumpp'] }` - 白名单 | [option-dependencies](references/option-dependencies.md) |
| 跳过 node_modules | `deps: { skipNodeModulesBundle: true }` | [option-dependencies](references/option-dependencies.md) |
| 自动外部化 | 自动依赖/同伴/可选外部化 | [option-dependencies](references/option-dependencies.md) |

## 输出增强

| 功能 | 用法 | 参考 |
|---------|-------|-----------|
| 补丁 | `shims: true` - 添加 ESM/CJS 兼容性 | [option-shims](references/option-shims.md) |
| CJS 默认 | `cjsDefault: true`（默认）/ `false` | [option-cjs-default](references/option-cjs-default.md) |
| 包含导出 | `exports: true` - 生成导出字段 | [option-package-exports](references/option-package-exports.md) |
| CSS 处理 | **[实验性]** `css: { ... }` — 完整的预处理程序、Lightning CSS、PostCSS、CSS 模块、代码拆分；需要 `@tsdown/css` | [option-css](references/option-css.md) |
| CSS 模块 | `css: { modules: { localsConvention: 'camelCase' } }` — `.module.css` 文件的范围类名 | [option-css](references/option-css.md) |
| CSS 注入 | `css: { inject: true }` — 在 JS 输出中保留 CSS 导入 | [option-css](references/option-css.md) |
| 解包模式 | `unbundle: true` - 保留目录结构 | [option-unbundle](references/option-unbundle.md) |
| 根目录 | `root: 'src'` - 控制输出目录映射 | [option-root](references/option-root.md) |
| 可执行文件 | **[实验性]** `exe: true` - 捆绑为独立的可执行文件，跨平台通过 `@tsdown/exe` | [option-exe](references/option-exe.md) |
| 包含验证 | `publint: true`, `attw: true` - 验证包含 | [option-lint](references/option-lint.md) |

## 框架与运行时支持

| 框架 | 指南 | 参考 |
|-----------|-------|-----------|
| React | JSX 转换、React 编译器 | [recipe-react](references/recipe-react.md) |
| Vue | SFC 支持、JSX | [recipe-vue](references/recipe-vue.md) |
| Solid | SolidJS JSX 转换 | [recipe-solid](references/recipe-solid.md) |
| Svelte | Svelte 组件库（推荐源代码分发） | [recipe-svelte](references/recipe-svelte.md) |
| WASM | 通过 `rolldown-plugin-wasm` 的 WebAssembly 模块 | [recipe-wasm](references/recipe-wasm.md) |

## 常见模式

### 基本库捆绑

```ts
export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  dts: true,
  clean: true,
})
```

### 多入口点

```ts
export default defineConfig({
  entry: {
    index: 'src/index.ts',
    utils: 'src/utils.ts',
    cli: 'src/cli.ts',
  },
  format: ['esm', 'cjs'],
  dts: true,
})
```

### 浏览器库（IIFE/UMD）

```ts
export default defineConfig({
  entry: ['src/index.ts'],
  format: ['iife'],
  globalName: 'MyLib',
  platform: 'browser',
  minify: true,
})
```

### React 组件库

```ts
export default defineConfig({
  entry: ['src/index.tsx'],
  format: ['esm', 'cjs'],
  dts: true,
  deps: {
    neverBundle: ['react', 'react-dom'],
  },
  inputOptions: {
    jsx: { runtime: 'automatic' },
  },
})
```

### 保留目录结构

```ts
export default defineConfig({
  entry: ['src/**/*.ts', '!**/*.test.ts'],
  unbundle: true, // 保留文件结构
  format: ['esm'],
  dts: true,
})
```

### CI 感知配置

```ts
export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  dts: true,
  failOnWarn: 'ci-only',  // 选择性：在 CI 中失败于警告
  publint: 'ci-only',
  attw: 'ci-only',
})
```

### WASM 支持

```ts
import { wasm } from 'rolldown-plugin-wasm'
import { defineConfig } from 'tsdown'

export default defineConfig({
  entry: ['src/index.ts'],
  plugins: [wasm()],
})
```

### 包含 CSS 和 Sass 的库

```ts
export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  dts: true,
  target: 'chrome100',
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@use "src/styles/variables" as *;`,
      },
    },
  },
})
```

### 独立可执行文件

```ts
export default defineConfig({
  entry: ['src/cli.ts'],
  exe: true,
})
```

### 跨平台可执行文件（需要 `@tsdown/exe`）

```ts
export default defineConfig({
  entry: ['src/cli.ts'],
  exe: {
    targets: [
      { platform: 'linux', arch: 'x64', nodeVersion: '25.7.0' },
      { platform: 'darwin', arch: 'arm64', nodeVersion: '25.7.0' },
      { platform: 'win', arch: 'x64', nodeVersion: '25.7.0' },
    ],
  },
})
```

### 高级钩子

```ts
export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  dts: true,
  hooks: {
    'build:before': async (context) => {
      console.log('Building...')
    },
    'build:done': async (context) => {
      console.log('Build complete!')
    },
  },
})
```

## 配置功能

### 多配置

导出数组以进行多个构建配置：

```ts
export default defineConfig([
  {
    entry: ['src/index.ts'],
    format: ['esm', 'cjs'],
    dts: true,
  },
  {
    entry: ['src/cli.ts'],
    format: ['esm'],
    platform: 'node',
  },
])
```

### 条件配置

使用函数进行动态配置：

```ts
export default defineConfig((options) => {
  const isDev = options.watch
  return {
    entry: ['src/index.ts'],
    format: ['esm', 'cjs'],
    minify: !isDev,
    sourcemap: isDev,
  }
})
```

### 工作区/单仓库

使用通配符模式构建多个包：

```ts
export default defineConfig({
  workspace: 'packages/*',
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  dts: true,
})
```

## CLI 快速参考

```bash
# 基本命令
tsdown                          # 单次构建
tsdown --watch                  # 监视模式
tsdown --config custom.ts       # 自定义配置
npx tsdown-migrate              # 从 tsup 迁移

# 输出选项
tsdown --format esm,cjs        # 多种格式
tsdown -d lib                  # 自定义输出目录（--out-dir）
tsdown --minify                # 启用压缩
tsdown --dts                   # 生成声明
tsdown --exe                   # 捆绑为独立可执行文件
tsdown --unbundle              # 无捆绑模式

# 入口选项
tsdown src/index.ts            # 单入口
tsdown src/*.ts                # 通配符模式
tsdown src/a.ts src/b.ts       # 多入口

# 工作区 / 单仓库
tsdown -W                      # 启用工作区模式
tsdown -W -F my-package        # 筛选特定包
tsdown --filter /^pkg-/        # 正则表达式筛选

# 开发
tsdown --watch                 # 监视模式
tsdown --sourcemap             # 生成源映射
tsdown --clean                 # 清理输出目录
tsdown --from-vite             # 重用 Vite 配置
tsdown --tsconfig tsconfig.build.json  # 自定义 tsconfig
```

## 最佳实践

1. **始终为 TypeScript 库生成类型声明**：
   ```ts
   { dts: true }
   ```

2. **外部化依赖**以避免捆绑不必要的代码：
   ```ts
   { deps: { neverBundle: [/^react/, /^@myorg\//] } }
   ```

3. **使用树摇**以获得最佳捆绑大小：
   ```ts
   { treeshake: true }
   ```

4. **为生产构建启用压缩**：
   ```ts
   { minify: true }
   ```

5. **添加补丁**以获得更好的 ESM/CJS 兼容性：
   ```ts
   { shims: true }  // 添加 __dirname、__filename 等
   ```

6. **自动生成 package.json exports**：
   ```ts
   { exports: true }  // 创建正确的 exports 字段
   ```

7. **在开发期间使用监视模式**：
   ```bash
   tsdown --watch
   ```

8. **为具有许多文件的工具保留结构**：
   ```ts
   { unbundle: true }  // 保留目录结构
   ```

9. **在发布前在 CI 中验证包**：
   ```ts
   { publint: 'ci-only', attw: 'ci-only' }
   ```

## 资源

- 文档：https://tsdown.dev
- GitHub：https://github.com/rolldown/tsdown
- Rolldown：https://rolldown.rs
- 迁移指南：https://tsdown.dev/guide/migrate-from-tsup
