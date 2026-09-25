# Ultracite

为 JS/TS 项目提供零配置的代码检查和格式化工具。支持三种代码检查器后端：**Oxlint** + Oxfmt（推荐）、**Biome**，以及 **ESLint** + Prettier + Stylelint。

## 检测 Ultracite

检查 `package.json` 依赖项或开发依赖项中是否包含 `ultracite`。通过从当前目录向上查找来检测活动的代码检查器：

- `biome.json` / `biome.jsonc` → Biome
- `eslint.config.*` (`.mjs`, `.js`, `.cjs`, `.ts`, `.mts`, `.cts`) → ESLint（格式化使用 Prettier）
- `oxlint.config.ts` → Oxlint（格式化使用 `oxfmt.config.ts`）

## CLI 命令

```bash
# 检查问题（只读）
bunx ultracite check

# 自动修复问题
bunx ultracite fix

# 诊断配置问题
bunx ultracite doctor

# 在新项目中初始化
bunx ultracite init
```

根据包管理器将 `bunx` 替换为 `npx`、`pnpx` 或 `yarn dlx`。

`check` 和 `fix` 接受可选的文件路径：`bunx ultracite check src/index.ts`。未知的选项会被传递给底层的代码检查器（例如 `bunx ultracite check --max-warnings 0`）。

## 初始化

`bunx ultracite init` 运行交互式设置。对于非交互式（CI）使用，请传递标志：

```bash
bunx ultracite init \
  --pm bun \
  --linter biome \
  --editors universal \
  --agents claude copilot \
  --frameworks react next \
  --integrations husky lint-staged \
  --quiet
```

**标志：**

- `--pm` — `npm` | `yarn` | `pnpm` | `bun` | `deno` | `nub` | `aube`
- `--linter` — `oxlint`（推荐）| `biome` | `eslint`
- `--editors` — `universal`（为每个基于 VS Code 的编辑器写入 `.vscode/settings.json`）| `vscode` | `cursor` | `windsurf` | `codebuddy` | `antigravity` | `bob` | `kiro` | `trae` | `void` | `zed`
- `--agents` — `universal`（写入 `AGENTS.md`）| `claude` | `codex` | `copilot` | `cline` | `amp` | `gemini` | `cursor-cli` + 34 更多（支持 41 个代理）
- `--frameworks` — `react` | `next` | `solid` | `vue` | `svelte` | `qwik` | `remix` | `tanstack` | `angular` | `astro` | `nestjs` | `jest` | `vitest`
- `--integrations` — `husky` | `lefthook` | `lint-staged` | `pre-commit`
- `--hooks` — 启用自动修复钩子：`claude` | `copilot` | `cursor` | `windsurf` | `codebuddy`
- `--type-aware` — 启用类型感知代码检查（Biome：扩展 `type-aware` 预设；Oxlint：安装 `oxlint-tsgolint`）
- `--install-skill` — 设置后安装可重用的 Ultracite 技能
- `--skip-install` — 跳过依赖项安装
- `--quiet` — 抑制提示（当 `CI=true` 时自动检测）；当 `--linter` 被省略时默认为 `oxlint`

初始化会创建扩展 Ultracite 预设的配置：

```jsonc
// biome.jsonc
{ "extends": ["ultracite/biome/core", "ultracite/biome/react"] }
```

```ts
// eslint.config.mjs — 数组形式的扁平配置，合并在一起
import core from "ultracite/eslint/core";
import react from "ultracite/eslint/react";
export default [...core, ...react];
```

```ts
// oxlint.config.ts — 传递给 `extends` 的导入
import { defineConfig } from "oxlint";
import core from "ultracite/oxlint/core";
export default defineConfig({
  extends: [core],
  ignorePatterns: core.ignorePatterns,
});
```

每个代码检查器可用的预设 (`ultracite/<linter>/<preset>`)：`core`、`react`、`next`、`solid`、`vue`、`svelte`、`qwik`、`remix`、`tanstack`、`angular`、`astro`、`nestjs`、`jest`、`vitest`。Biome 还具有 `type-aware`；Oxlint 还具有 `github` 和 `sonarjs`（通过 Oxlint 的 JS 插件支持运行 ESLint 插件，初始化时默认包含）。

## 代码规范

在 Ultracite 项目中编写代码时，请遵循以下规范。有关完整规则参考，请参阅 [references/code-standards.md](references/code-standards.md)。

关键规则概览：

格式化由项目配置的代码检查器/格式化器处理。请尊重仓库现有的格式化设置，而不是强制固定的行宽、引号样式或尾随逗号策略。

**类型安全：** 当类型清晰时使用显式类型。优先使用 `unknown` 而不是 `any`。使用 `as const` 表示不可变值，并依赖类型缩小而不是生硬的断言。

**现代 JavaScript/TypeScript：** 优先使用 `const`、解构、可选链、空值合并、模板字符串、`for...of` 和简洁的箭头函数。

**异步和正确性：** 在异步函数中始终使用 `await` 承诺。优先使用 `async/await` 而不是承诺链。从生产代码中移除 `console.log`、`debugger` 和 `alert`。

**React 和可访问性：** 使用函数组件，将钩子置于顶层并正确依赖，避免嵌套组件定义，并使用语义 HTML，包括正确的标签、标题、alt 文本和键盘提示。

**组织、安全、性能和测试：** 保持函数专注，优先使用早期返回，避免 `dangerouslySetInnerHTML` 和 `eval()`，优先使用特定导入和顶层正则表达式，并保持测试中不使用 `.only` 和 `.skip`。

## 故障排除

运行 `bunx ultracite doctor` 进行诊断。它会检查：

1. 代码检查器和格式化器的安装（Biome；或 ESLint + Prettier + Stylelint；或 Oxlint + oxfmt）
2. 配置有效性（正确扩展 Ultracite 预设）
3. `package.json` 依赖项中的 Ultracite
4. 冲突工具（遗留的 `.eslintrc.*` 文件；当不使用 ESLint 后端时，`.prettierrc.*`/`prettier.config.*`）

常见修复：

- **冲突配置**：迁移到 Ultracite 后删除遗留的 `.eslintrc.*` 和 `.prettierrc.*` 文件
- **缺失依赖项**：再次运行 `bunx ultracite init` 或手动将 `ultracite` 添加到开发依赖项
- **规则未应用**：确保配置文件扩展了适用于您框架的正确预设
