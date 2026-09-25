## 快速入门

- `nx import` 将代码从源代码库或文件夹导入当前工作区，同时保留提交历史记录。
- 在 nx `22.6.0` 之后，`nx import` 会响应 .ndjson 输出并附带后续问题。对于早期版本，始终使用 `--no-interactive` 并直接指定所有标志。
- 运行 `nx import --help` 查看可用选项。
- 导入之前，请确保目标目录为空。
  示例：目标包含 `libs/utils` 和 `libs/models`；源包含 `libs/ui` 和 `libs/data-access` — 你不能直接将 `libs/` 导入 `libs/`。分别导入每个源库。

主要文档：

- https://nx.dev/docs/guides/adopting-nx/import-project
- https://nx.dev/docs/guides/adopting-nx/preserving-git-histories

如果你有使用 nx 的工具，请阅读 nx 文档。

## 导入策略

**逐子目录导入** (`nx import <source> apps --source=apps`)：

- **推荐用于单代码库源** — 文件位于顶层，没有冗余配置
- 注意事项：多个导入命令（每个合并提交分离）；目标目录不能有冲突目录；根配置（依赖项、插件、目标默认值）不会导入
- **目录冲突**：导入到重命名的目录（例如 `imported-apps/`），然后重命名

**整个代码库导入** (`nx import <source> imported --source=.`)：

- **仅用于非单代码库源**（单个项目代码库）
- 对于单代码库，会创建混乱的嵌套配置（`imported/nx.json`、`imported/tsconfig.base.json` 等）
- 如果必须：保留导入的 `tsconfig.base.json`（项目会扩展它），前缀工作区全局和执行器路径

### 目录约定

- **始终优先考虑目标目录的现有约定。** 源使用 `libs/` 但目标使用 `packages/`？导入到 `packages/` (`nx import <source> packages/foo --source=libs/foo`)。
- 如果目标没有约定（空工作区），则询问用户。

### 应用程序与库检测

导入之前，识别源是**应用程序**还是**库**：

- **应用程序**：可部署的最终产品。常见指示器：
  - _前端_：`next.config.*`、`vite.config.*` 具有构建入口点，特定于框架的应用程序脚手架（CRA、Angular CLI 应用程序等）
  - _后端（Node.js）_：Express/Fastify/NestJS 服务器入口点，`package.json` 中没有 `"exports"` 字段
  - _JVM_：Maven `pom.xml` 具有 `<packaging>jar</packaging>` 或 `<packaging>war</packaging>` 和 `main` 类；Gradle `application` 插件或 `mainClass` 设置
  - _.NET_：`.csproj`/`.fsproj` 具有 `<OutputType>Exe</OutputType>` 或 `<OutputType>WinExe</OutputType>`
  - _通用_：Dockerfile、可运行的入口点、没有公共 API 表面供其他项目导入
- **库**：其他项目可消费的包。常见指示器：`package.json` 中的 `"main"`/`"exports"`、Maven/Gradle 打包为库 jar、.NET `<OutputType>Library</OutputType>`、供其他包导入的命名导出

**目标目录规则**：

- 应用程序 → `apps/<name>`。检查工作区全局（例如 `pnpm-workspace.yaml`、根 `package.json` 中的 `workspaces`）中是否已存在 `apps/*` 条目。
  - 如果 `apps/*` **不存在**，导入之前添加它：更新工作区全局配置并提交（或暂存）更改。
  - 示例：`nx import <source> apps/my-app --source=packages/my-app`
- 库 → 遵循目标的现有约定（`packages/`、`libs/` 等）。

## 常见问题

### pnpm 工作区全局（关键）

`nx import` 将导入的目录本身（例如 `apps`）添加到 `pnpm-workspace.yaml`，**不是**其内部包的 glob 模式。跨包导入会因 `Cannot find module` 失败。

**修复**：用源配置中的适当 glob 替换（例如 `apps/*`、`libs/shared/*`），然后 `pnpm install`。

### 根依赖项和配置未导入（关键）

`nx import` **不会** 从源合并：

- `package.json` 中的 `dependencies`/`devDependencies`
- `nx.json` 中的 `targetDefaults`（例如 `"@nx/esbuild:esbuild": { "dependsOn": ["^build"] }` — 对构建顺序至关重要）
- `nx.json` 中的 `namedInputs`（例如测试文件的 `production` 排除模式）
- `nx.json` 中的插件配置

**修复**：比较源和目标的 `package.json` + `nx.json`。添加缺失的依赖项，合并相关的 `targetDefaults` 和 `namedInputs`。

### TypeScript 项目引用

导入后，运行 `nx sync --yes`。如果它报告无内容但类型检查仍然失败，请先运行 `nx reset`，然后再次运行 `nx sync --yes`。

### 显式执行器路径修复

推断目标（通过 Nx 插件）相对于项目根解析配置 — 无需更改。显式执行器目标（例如 `@nx/esbuild:esbuild`）具有相对于工作区根的路径（`main`、`outputPath`、`tsConfig`、`assets`、`sourceRoot`），必须以导入目标目录为前缀。

### 插件检测

- **整个代码库导入**：`nx import` 检测并建议安装插件。接受它们。
- **子目录导入**：插件**不会**自动检测。手动添加，使用 `npx nx add @nx/PLUGIN`。检查 `include`/`exclude` 模式 — 默认值不会匹配备用目录（例如 `apps-beta/`）。
- 任何插件配置更改后，运行 `npx nx reset`。

### 冗余根文件（仅限整个代码库）

整个代码库导入会将所有源根文件带入目标子目录。清理：

- `pnpm-lock.yaml` — 过期；目标有自己的锁文件
- `pnpm-workspace.yaml` — 源工作区配置；与目标冲突
- `node_modules/` — 过期符号链接指向源文件系统
- `.gitignore` — 与目标根 `.gitignore` 冗余
- `nx.json` — 源 Nx 配置；目标有自己的
- `README.md` — 可选；保留或删除

**不要盲目删除** `tsconfig.base.json` — 导入的项目可能通过相对路径扩展它。

### 根 ESLint 配置缺失（子目录导入）

子目录导入**不会**带来源的根 `eslint.config.mjs`，但项目配置引用 `../../eslint.config.mjs`。

**修复顺序**：

1. 首先安装 ESLint 依赖项：`pnpm add -wD eslint@^9 @nx/eslint-plugin typescript-eslint`（加上特定于框架的插件）
2. 创建根 `eslint.config.mjs`（从源复制或使用 `@nx/eslint-plugin` 基本规则创建）
3. 然后 `npx nx add @nx/eslint` 将插件注册到 `nx.json`

显式安装 `typescript-eslint` — pnpm 的严格提升不会自动解析 `@nx/eslint-plugin` 的传递依赖项。

### ESLint 版本锁定（关键）

**将 ESLint 锁定到 v9** (`eslint@^9.0.0`)。ESLint 10 会破坏 `@nx/eslint` 和许多插件，并导致类似 `Cannot read properties of undefined (reading 'version')` 的错误。

`@nx/eslint` 可能依赖 ESLint 8，导致解析错误版本。如果 lint 失败并显示 `Cannot read properties of undefined (reading 'allow')`，请添加 `pnpm.overrides`：

```json
{ "pnpm": { "overrides": { "eslint": "^9.0.0" } } }
```

### 依赖项版本冲突

导入后，比较关键依赖项（`typescript`、`eslint`、特定于框架的）。如果目标使用较新版本，请将导入的包升级以匹配（通常安全）。如果源版本较新，可能需要先升级目标。如有必要，使用 `pnpm.overrides` 强制单版本策略。

### 模块边界

导入的项目可能缺少 `tags`。添加标签或更新 `@nx/enforce-module-boundaries` 规则。

### 项目名称冲突（多导入）

源和目标 `package.json` 中相同的 `name` 导致 `MultipleProjectsWithSameNameError`。**修复**：重命名冲突名称（例如 `@org/api` → `@org/teama-api`），更新所有依赖项引用和导入语句，`pnpm install`。每个导入代码库的根 `package.json` 也成为项目 — 重命名它们。

### 工作区依赖项导入顺序

`pnpm install` 在 `nx import` 期间失败，如果尚未导入 `"workspace:*"` 依赖项。文件操作仍然成功。**修复**：首先导入所有项目，然后 `pnpm install --no-frozen-lockfile`。

### `.gitkeep` 阻止子目录导入

TS 预设创建 `packages/.gitkeep`。删除它并提交，然后导入。

### 前端 tsconfig 基本设置（关键）

TS 预设默认值（`module: "nodenext"`、`moduleResolution: "nodenext"`、`lib: ["es2022"]`）与前端框架（React、Next.js、Vue、Vite）不兼容。导入前端项目后，验证目标根 `tsconfig.base.json`：

- **`moduleResolution`**：必须是 `"bundler"`（不是 `"nodenext"`）
- **`module`**：必须是 `"esnext"`（不是 `"nodenext"`）
- **`lib`**：必须包含 `"dom"` 和 `"dom.iterable"`（前端项目需要这些）
- **`jsx`**：对于仅 React 工作区，使用 `"react-jsx"`；对于混合框架，按项目设置

对于**子目录导入**，目标根 tsconfig 是权威的 — 更新它。对于**整个代码库导入**，导入的项目可能扩展自己的嵌套 `tsconfig.base.json`，因此这个问题不太关键。

如果目标也有需要 `nodenext` 的后端项目，请使用按项目覆盖而不是更改根。

**注意**：TypeScript 不会合并 `lib` 数组 — 项目级覆盖**完全替换**基础数组。始终在项目级 `lib` 中包含所有需要的条目（例如 `es2022`、`dom`、`dom.iterable`）。

### `@nx/react` 库类型定义

使用 `@nx/react:library` 生成的 React 库在其 tsconfig `types` 中引用 `@nx/react/typings/cssmodule.d.ts` 和 `@nx/react/typings/image.d.ts`。如果没有安装 `@nx/react`，这些会因 `Cannot find type definition file` 失败。

**修复**：`pnpm add -wD @nx/react`

### Jest 预设缺失（子目录导入）

Nx 预设在工作区根创建 `jest.preset.js`，项目 jest 配置引用它（例如 `../../jest.preset.js`）。子目录导入**不会**带来源文件。

**修复**：

1. 运行 `npx nx add @nx/jest` — 注册 `@nx/jest/plugin` 到 `nx.json` 并更新 `namedInputs`
2. 在工作区根创建 `jest.preset.js`（见 `references/JEST.md` 内容）— `nx add` 仅在生成器运行时创建，而不是在裸 `nx add` 时
3. 安装测试运行器依赖项：`pnpm add -wD jest jest-environment-jsdom ts-jest @types/jest`
4. 根据需要安装特定于框架的测试依赖项（见 `references/JEST.md`）

对于更深的 Jest 问题（`tsconfig.spec.json`、Babel 转换、CI 原子化、Jest 与 Vitest 共存），请参阅 `references/JEST.md`。

### 目标名称前缀（整个代码库导入）

导入具有现有 npm 脚本（`build`、`dev`、`start`、`lint`）的项目时，Nx 插件会自动前缀推断的目标名称以避免冲突：例如 `next:build`、`vite:build`、`eslint:lint`。

**修复**：从导入的 `package.json` 中删除 Nx 重写的 npm 脚本，然后：

- 接受前缀名称（例如 `nx run app:next:build`）
- 在 `nx.json` 中重命名插件目标名称以使用未前缀名称
