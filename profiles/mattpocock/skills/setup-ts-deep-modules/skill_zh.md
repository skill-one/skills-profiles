# 设置 TS 深层模块

使本仓库中的每个包都是一个**深层模块**：在一个小接口背后隐藏大量行为。一个包的公开界面是其**入口点**（即包根目录下的文件），其子文件夹中的所有内容均为隐藏内容。本技能将安装 [dependency-cruiser](https://github.com/sverweij/dependency-cruiser)，并配置使入口点成为唯一入口的规则，随后验证这些规则是否切实生效。

对于词汇（深层模块、接口、接缝、深度），请通过 "codebase-design" 调用 Skill 工具，并在全文中采用其语言。

## 本技能所强制的形态

```
src/packages/
  <name>/
    index.ts        ← 入口点（公开）。在外部导入此文件。
    client.ts       ← 另一个入口点。包可以暴露多个。
    lib/            ← 实现：对外隐藏，内部自由相互导入。
    tests/          ← 同目录测试 + 测试数据（属于子文件夹，因此为私有）。
```

包的公开界面是包的**根文件**，而非某个特定的 `index.ts`。按惯例，实现代码位于 `lib/`，测试位于 `tests/`，使每个包都具有相同的双文件夹结构。不过，该规则本身是通用的：任何子文件夹中的**任何**内容均为私有，因此永远无需扩展配置以添加文件夹。

四条规则，均设为 `error`：

1. **入口点边界**：包外部的代码（应用代码或其他包）仅能导入该包的入口点（其根文件），绝不能导入其子文件夹中的任何内容。
2. **包内自由**：包自身的文件可自由相互导入。
3. **通过入口点进行测试**：` <pkg>/tests/` 下的文件可以导入任何包的入口点及其自身的 `tests/` 测试数据，但绝不能导入任何包的子文件夹内部（包括自身）。跨包的集成测试是允许的；深层导入则不允许。
4. **无循环依赖**：不存在依赖循环。

**入口点，而非 barrel。** 由于公开界面是每一个根文件，因此包可以暴露多个小型入口点（`index.ts`、`client.ts`、`server.ts`），而非将所有内容汇聚到一个巨大的 `index.ts` 中。不建议使用重新导出整个子树的 barrel 文件；保持入口点小巧，并将实现隐藏在子文件夹中。

（层级的）依赖关系（即各包可以依赖哪些包）是另一个独立的问题，在本仓库的配置中作为带注释的占位符保留，以供后续补充。

## 步骤

### 1. 检测环境

- **包管理器**：`pnpm-lock.yaml` → pnpm，`yarn.lock` → yarn，`bun.lockb` → bun，否则为 npm。在以下每个命令中使用它（`pnpm`/`yarn`/`npm run`/`bunx`）。
- **包根目录**：若存在 `src/` 则使用 `src/packages`，否则使用 `packages`。若仓库已有明显不同的惯例，请与用户确认此选择。
- **现有配置**：检查是否存在 `.dependency-cruiser.*` 文件。若存在，切勿覆盖：将四条规则和选项合并进去，并告知用户你添加的内容。

**完成条件：** 已明确包管理器、包根目录以及现有配置的 status。

### 2. 安装 dependency-cruiser

安装 `dependency-cruiser` 作为开发依赖，并使用检测到的包管理器进行安装。

**完成条件：** `dependency-cruiser` 已包含在 `devDependencies` 中。

### 3. 编写配置

将 [`dependency-cruiser.config.cjs`](./dependency-cruiser.config.cjs) 复制到仓库根目录，命名为 `.dependency-cruiser.cjs`。将 `PACKAGES_ROOT` 设置为第 1 步检测到的根目录。这些规则基于路径深度且不区分扩展名，因此无需对其他内容进行调整。

**完成条件：** 已创建包含正确 `PACKAGES_ROOT` 的 `.dependency-cruiser.cjs`，且四条禁用规则均已存在。

### 4. 将其集成到检查中

- 添加 `lint:boundaries` 脚本：`depcruise <packages-root>`（或 `depcruise src`）。
- 将其整合到仓库的全面检查命令中，即已包含类型检查的命令（例如 `check` / `ci` / `validate` 脚本）。**切勿**修改 `tsconfig` 或添加路径别名。
- 若无全面检查脚本，则添加 `lint:boundaries`，并告知用户将其纳入 CI。

**完成条件：** `lint:boundaries` 已存在，并与类型检查命令在同一命令中执行。

### 5. 搭建示例包

创建一个已提交的 `<packages-root>/example/` 作为可复制的模板：

- `index.ts` 是一个入口点。导出一个函数，将其委托给内部文件（以便该包明显是**深层模块**，而非透传）。
- `lib/impl.ts`：位于**子文件夹**中的内部文件，由 `index.ts` 导入，外部无法访问。
- `tests/example.test.ts` 仅导入 `../index`（一个入口点），并针对该公开函数进行断言。

告知用户，这是一个可供复制或删除的入门模板。

**完成条件：** 示例包已创建，通过根入口点暴露其行为，并将 `impl` 隐藏在子文件夹中。

### 6. 验证规则是否切实生效

这是整个技能的完成标准：如果配置在违规时无法报错，那么该配置毫无价值。

1. 运行 `lint:boundaries`。在干净的示例上必须**通过**。
2. 暂时向 `tests/example.test.ts` 添加一个深层导入（例如 `import { thing } from "../lib/impl"`）。再次运行 `lint:boundaries`；必须**报错**并出现 `tests-through-entrypoints`。
3. 撤销该深层导入。再次运行，必须**通过**。

**完成条件：** 已观察到在深度导入的情况下先通过、后失败（报 `tests-through-entrypoints`），随后再次通过。若第 2 步未失败，则说明规则未正确接入，需修复后方可结束。

### 7. 记录约定

在包文件夹中编写 `README.md`（` <packages-root>/README.md`，位于其所管辖的包旁），内容包括：`src/packages/<name>/` 的布局（入口点在根目录，`lib/` 用于实现，`tests/` 用于测试）、“仅通过包的入口点（其根文件）进行导入”，以及如何运行 `lint:boundaries`。**明确不建议使用 barrel 文件**：应暴露多个小型入口点，而非通过一个 index 重新导出整个子树。篇幅上，每个要点包含一份可复制的示例片段以及各一条规则的说明。

从仓库的 agent 指令文件中为该文件添加**上下文指引**（若存在则使用 `CLAUDE.md`，否则使用 `AGENTS.md`，若两者均不存在则创建 `AGENTS.md`）。只需一行即可，例如：`Packages are deep modules: see [src/packages/README.md](./src/packages/README.md) before adding or importing one.` 这正是能让 Agent 发现边界规则，而非被其绊倒的原因。

**完成条件：** `<packages-root>/README.md` 已存在且明确不建议使用 barrel 文件，且仓库的 `CLAUDE.md`/`AGENTS.md` 已将其链接。

## 注意事项

- 配置中的 `$1` 反向引用（dependency-cruiser 的组匹配）正是允许包访问自身内部、而外部无法访问的原因。切勿将其扁平化为针对每个包的独立规则。
- 公开与私有由**深度**决定：包的根文件为入口点；子文件夹中的任何内容均为私有。常规的子文件夹为 `lib/`（实现）和 `tests/`，但该规则并不将其硬编码：任何子文件夹均为私有，因此新增文件夹无需任何配置变更。添加入口点只需添加一个根文件（无需 barrel）。
- 包为**扁平结构**：根目录下只有一层直接子级。包的内部可以嵌套任意深；但一个包不能包含另一个包。
- 使用 `.cjs`（而非 `.js`），以确保配置中的 `module.exports` 即使在 `"type": "module"` 的仓库中也能正常工作。
