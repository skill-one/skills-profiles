---
name: antfu
description: 安东尼·傅为JavaScript/TypeScript项目提供的个人化工具和约定。在新建项目、配置ESLint/Prettier替代方案、单体仓库、库发布或用户提及安东尼·傅的偏好时使用。
---

## 编码规范

### 代码组织

- **单一职责原则**：每个源文件应有清晰、专注的范畴/目的
- **拆分大文件**：当文件过大或处理过多关注点时进行拆分
- **类型分离**：始终将类型和接口分离到 `types.ts` 或 `types/*.ts`
- **常量提取**：将常量移至专门的 `constants.ts` 文件

### 运行时环境

- **优先使用同构代码**：尽可能编写与运行时无关的代码，使其能在 Node、浏览器和 Worker 中运行
- **清晰的运行时标识**：当代码针对特定环境时，在文件顶部添加注释：

```ts
// @env node
// @env browser
```

### TypeScript

- **显式返回类型**：在可能的情况下显式声明返回类型
- **避免复杂的行内类型**：将复杂类型提取到专门的 `type` 或 `interface` 声明中

### 显式性

优先使用显式、可追踪的代码，而非隐式的"魔法"。读者（无论是人类还是代理）应能不依赖工具就能追踪每个名称的来源。

- **显式导入**：优先使用显式的 `import` 语句。避免自动导入——当框架提供自动导入功能时（例如 Nuxt/Nitro），为新项目禁用它们（参见 [app-development](references/app-development.md)）。
- **默认不使用路径别名**：使用相对导入（`./foo`，`../bar`）。仅在项目已配置路径别名时（`@/`，`~/`，`#imports` 等）使用它们；不要为绿地代码引入新的路径别名。

### 注释

- **避免不必要的注释**：代码应自解释
- **解释"为什么"而非"怎么做"**：注释应描述原因或意图，而非代码的功能

### 测试（Vitest）

- 测试文件：`foo.ts` → `foo.test.ts`（同一目录）
- 使用 `describe`/`it` API（而非 `test`）
- 使用 `toMatchSnapshot` 测试复杂输出
- 使用 `toMatchFileSnapshot` 并指定路径进行语言特定的快照

---

## 工具选择

### @antfu/ni 命令

| 命令 | 描述 |
|------|------|
| `ni` | 安装依赖 |
| `ni <pkg>` / `ni -D <pkg>` | 添加依赖 / 开发依赖 |
| `nr <script>` | 运行脚本 |
| `nu` | 升级依赖 |
| `nun <pkg>` | 卸载依赖 |
| `nci` | 清理安装 (`pnpm i --frozen-lockfile`) |
| `nlx <pkg>` | 执行包 (`npx`) |

### 检查 npm 包版本

使用 [`fast-npm-meta`](https://github.com/antfu/fast-npm-meta) 查询包的最新版本——它查询一个小型元数据端点，而非下载完整的注册表负载（每个包可能高达兆字节）。

```bash
nlx fast-npm-meta version vite              # 7.3.1
nlx fast-npm-meta version "nuxt@^3.5"       # 3.5.22 — 支持范围
nlx fast-npm-meta version vite nuxt vue     # 同时查询多个
nlx fast-npm-meta version vite --json       # 脚本用的 JSON
nlx fast-npm-meta full vite                 # 完整版本列表 + dist-tags
```

当仅需最新版本时，优先使用此方法，而非 `npm view <pkg> version`，也非直接从注册表读取 `package.json`。

### TypeScript 配置

```json
{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true
  }
}
```

### ESLint 设置

```js
// eslint.config.mjs
import antfu from '@antfu/eslint-config'

export default antfu()
```

完成任务时，运行 `pnpm run lint --fix` 格式化代码并修复编码风格。

详细配置选项：[antfu-eslint-config](references/antfu-eslint-config.md)

### Git 钩子

```json
{
  "simple-git-hooks": {
    "pre-commit": "pnpm i --frozen-lockfile --ignore-scripts --offline && npx lint-staged"
  },
  "lint-staged": { "*": "eslint --fix" },
  "scripts": {
    "prepare": "npx simple-git-hooks"
  }
}
```

### pnpm 目录

在 `pnpm-workspace.yaml` 中使用命名目录进行版本管理：

| 目录 | 目的 |
|------|------|
| `prod` | 生产依赖 |
| `inlined` | 打包内嵌依赖 |
| `dev` | 开发工具（格式化器、打包器、测试） |
| `frontend` | 前端库 |

避免使用默认目录。目录名称可根据项目需求调整。

---

## 参考

| 主题 | 描述 | 参考 |
|------|------|------|
| ESLint 配置 | 框架支持、格式化器、规则覆盖、VS Code 设置 | [antfu-eslint-config](references/antfu-eslint-config.md) |
| 项目设置 | .gitignore、GitHub Actions、VS Code 扩展 | [setting-up](references/setting-up.md) |
| 应用开发 | Vue/Nuxt/UnoCSS 规范、自动导入控制、Storybook 组件测试 | [app-development](references/app-development.md) |
| 库开发 | tsdown 打包、纯 ESM 发布 | [library-development](references/library-development.md) |
| 单一仓库 | pnpm 工作区、集中别名、Turborepo | [monorepo](references/monorepo.md) |
