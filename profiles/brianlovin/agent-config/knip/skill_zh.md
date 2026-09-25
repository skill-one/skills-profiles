# Knip 代码清理

运行 knip 来查找并删除此代码库中的未使用文件、依赖项和导出项。

## 安装

1. 检查 knip 是否可用：
   - 运行 `npx knip --version` 进行测试
   - 如果失败或非常慢，检查 `knip` 是否在 `package.json` 的 `devDependencies` 中
   - 如果本地未安装，使用 `npm install -D knip` 安装（或根据 lockfile 存在情况使用 pnpm/yarn/bun 等等效命令）

2. knip 不会删除文件内部的未使用导入/变量——那是 linter 的工作。knip 查找整个项目中的未使用文件、依赖项和导出项。

## 工作流程

始终遵循此配置优先的工作流程。即使是简单的“运行 knip”或“清理代码库”提示，在处理报告的问题之前，也请正确配置 knip。

### 第 1 步：理解项目

- 检查项目使用哪些框架和工具（查看 `package.json`）
- 检查是否存在 knip 配置（`knip.json`、`knip.jsonc` 或 `package.json` 中的 `knip` 键）
- 如果存在配置，请查看是否有改进空间（见配置最佳实践）

### 第 2 步：运行 knip 并首先阅读配置提示

```bash
npx knip
```

在处理任何其他事情之前，请关注 **配置提示**。这些提示出现在输出顶部，并建议调整配置以减少误报。

### 第 3 步：通过调整 knip.json 来解决提示

在处理报告的问题之前，先修复配置提示。常见的调整包括：
- 为检测到的框架启用/禁用插件
- 为非标准入口点添加入口模式
- 配置多项目工作区的设置

### 第 4 步：重复步骤 2-3

每次配置更改后重新运行 knip。重复操作，直到配置提示已解决且误报最小化。

### 第 5 步：处理实际问题

配置确定后，按以下顺序处理报告的问题：

1. **未使用文件** — 首先处理这些问题（“收件箱清零”方法可最大程度减少噪音）
2. **未使用依赖项** — 从 `package.json` 中移除
3. **未使用开发依赖项** — 从 `package.json` 中移除
4. **未使用导出项** — 移除或标记为内部
5. **未使用类型** — 移除，或配置 `ignoreExportsUsedInFile`（见下文）

### 第 6 步：重新运行并重复

每次批量修复后重新运行 knip。删除未使用文件通常会暴露新的未使用导出项和依赖项。

## 配置最佳实践

在查看或创建 knip 配置时，请遵循以下规则：

- **永远不要使用 `ignore` 模式** — `ignore` 会隐藏真实问题，几乎永远不应使用。始终优先选择具体解决方案。其他 `ignore*` 选项（如 `ignoreDependencies`、`ignoreExportsUsedInFile`）是可以的，因为它们针对特定问题类型。
- **许多未使用的导出类型？** 添加 `ignoreExportsUsedInFile: { interface: true, type: true }` — 这处理了类型仅在相同文件中使用的常见情况。优先选择此方案而非更广泛的忽略选项。
- **移除冗余模式** — Knip 已尊重 `.gitignore`，因此忽略 `node_modules`、`dist`、`build`、`.git` 是冗余的。
- **移除默认情况下已覆盖的入口模式** — 自动检测的插件已添加标准入口点。不要重复它们。
- **配置文件显示为未使用**（例如 `vite.config.ts`）— 明确启用或禁用相应的插件，而不是忽略文件。
- **依赖项匹配 Node.js 内建项**（例如 `buffer`、`process`）— 添加到 `ignoreDependencies`。
- **来自路径别名的未解析导入** — 向 knip 配置添加 `paths`（使用 tsconfig.json 语义）。

## 生产模式

使用 `--production` 仅关注生产代码：

```bash
npx knip --production
```

这会排除测试文件、配置文件和其他非生产入口点。**绝对不要**使用 `project` 或 `ignore` 模式来排除测试文件——请使用 `--production` 代替。

## 清理置信度等级

### 自动删除（高置信度）：
- 明确为内部且不属于公共 API 的未使用导出项
- 未使用的类型导出项
- 未使用依赖项（从 `package.json` 中移除）
- 明确为孤岛的未使用文件（非入口点、非配置文件）

### 需要确认（需要澄清）：
- 可能是入口点或动态导入的文件
- 可能属于公共 API 的导出项（`index.ts`、库导出）
- 可能通过 CLI 或伙伴依赖项使用的依赖项
- 位于 `src/index`、`lib/` 或文件名中包含“public”或“api”的路径中的任何内容

使用 `AskUserQuestion` 工具澄清后再删除这些内容。

## 自动修复

配置确定且您对结果有信心后：

```bash
# 自动修复安全的更改（删除未使用导出项和依赖项）
npx knip --fix

# 自动修复包括文件删除
npx knip --fix --allow-remove-files
```

只有在完成配置优先工作流程后才能使用 `--fix`。

## 错误处理

如果 knip 以代码 2 退出（例如“加载文件错误”等意外错误）：
- 检查是否存在配置文件——如果不存在，请在项目根目录创建 `knip.json`
- 检查 knip.dev 上的已知问题
- 查看配置参考以检查语法/选项错误
- 修复后重新运行 knip

## 常用命令

```bash
# 基本运行
npx knip

# 仅生产环境（排除测试/配置入口点）
npx knip --production

# 自动修复安全的更改
npx knip --fix

# 自动修复包括文件删除
npx knip --fix --allow-remove-files

# JSON 输出用于解析
npx knip --reporter json
```

## 注意事项

- 注意多项目工作区设置——可能需要 `--workspace` 标志
- 某些框架需要在配置中启用插件
- Knip 不会处理文件内部的未使用导入/变量——请使用 ESLint 或 Biome 处理
