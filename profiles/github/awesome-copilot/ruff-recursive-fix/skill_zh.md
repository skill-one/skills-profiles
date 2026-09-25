# Ruff 递归修复

## 概述

使用此功能以受控的迭代工作流程使用 Ruff 强制代码质量。
它支持：

- 可选的范围限制到特定文件夹。
- 默认项目设置来自 `pyproject.toml`。
- 灵活的 Ruff 调用（`uv`、直接 `ruff`、`python -m ruff` 或等效）。
- 可选的每次运行规则覆盖（`--select`、`--ignore`、`--extend-select`、`--extend-ignore`）。
- 自动安全然后不安全的自动修复。
- 每次修复后进行差异审查。
- 递归重复，直到问题解决或需要决策。
- 在抑制有理时谨慎使用内联 `# noqa`。

## 输入

运行之前收集这些输入：

- `target_path` (可选)：要检查的文件夹或文件。空值表示整个仓库。
- `ruff_runner` (可选)：显式的 Ruff 命令前缀（例如 `uv run`、`ruff`、`python -m ruff`、`pipx run ruff`）。
- `rules_select` (可选)：要强制的逗号分隔的规则代码。
- `rules_ignore` (可选)：要忽略的逗号分隔的规则代码。
- `extend_select` (可选)：在不替换配置默认值的情况下添加的额外规则。
- `extend_ignore` (可选)：在不替换配置默认值的情况下忽略的额外规则。
- `allow_unsafe_fixes` (默认：true)：是否运行 Ruff 不安全修复。
- `ask_on_ambiguity` (默认：true)：当存在多个有效选择时始终询问用户。

## 命令构建

根据输入构建 Ruff 命令。

### 0. 解析 Ruff 运行器

在构建命令之前确定可重用的 `ruff_cmd` 前缀。

解析顺序：

1. 如果提供了 `ruff_runner`，则直接使用它。
2. 否则如果 `uv` 可用且 Ruff 通过 `uv` 管理，则使用 `uv run ruff`。
3. 否则如果 `ruff` 在 `PATH` 上可用，则使用 `ruff`。
4. 否则如果 Python 可用且 Ruff 安装在该环境中，则使用 `python -m ruff`。
5. 否则使用任何调用已安装 Ruff 的项目特定等效项（例如 `pipx run ruff`），或停止并询问用户。

在流程中的所有 `check` 和 `format` 命令中使用相同的解析 `ruff_cmd`。

基本命令：

```bash
<ruff_cmd> check
```

格式化命令：

```bash
<ruff_cmd> format
```

带可选目标：

```bash
<ruff_cmd> format <target_path>
```

添加可选目标：

```bash
<ruff_cmd> check <target_path>
```

根据需要添加可选覆盖：

```bash
--select <codes>
--ignore <codes>
--extend-select <codes>
--extend-ignore <codes>
```

示例：

```bash
# 使用来自 pyproject.toml 的默认设置检查整个项目
ruff check

# 检查一个文件夹并使用默认设置
python -m ruff check src/models

# 本次运行跳过文档和类似 TODO 的规则
uv run ruff check src --extend-ignore D,TD

# 仅在文件夹中检查选定的规则
ruff check src/data --select F,E9,I
```

## 工作流程

### 1. 基线分析

1. 使用选定的范围和选项运行 `<ruff_cmd> check`。
2. 按类型对发现进行分类：
	- 可自动修复的安全。
	- 可自动修复的不安全。
	- 不可自动修复。
3. 如果没有剩余发现，停止。

### 2. 安全自动修复轮次

1. 使用 `--fix` 和相同的范围/选项运行 Ruff。
2. 仔细审查生成的差异，确保语义正确和风格一致。
3. 对相同的范围运行 `<ruff_cmd> format`。
4. 重新运行 `<ruff_cmd> check` 以刷新剩余发现。

### 3. 不安全自动修复轮次

仅当存在剩余发现且 `allow_unsafe_fixes=true` 时运行。

1. 使用相同的范围/选项和 `--fix --unsafe-fixes` 运行 Ruff。
2. 仔细审查生成的差异，优先考虑行为敏感的编辑。
3. 对相同的范围运行 `<ruff_cmd> format`。
4. 重新运行 `<ruff_cmd> check`。

### 4. 手动修复轮次

对于剩余发现：

1. 当有明确的、安全的修正时直接在代码中修复。
2. 保持编辑最小化和本地化。
3. 对相同的范围运行 `<ruff_cmd> format`。
4. 重新运行 `<ruff_cmd> check`。

### 5. 模糊政策

在任何步骤中如果有多个有效解决方案，始终在继续之前询问用户。
不要在等效选项之间无声地选择。

### 6. 抑制决策（`# noqa`）

仅在所有条件都满足时使用抑制：

- 规则与所需行为、公共 API、框架约定或可读性目标冲突。
- 重构与规则的值不成比例。
- 抑制是狭窄和具体的（单行，在可能的情况下显式代码）。

指南：

- 优先选择 `# noqa: <RULE>` 覆盖广泛的 `# noqa`。
- 对非明显的抑制添加简短的原因注释。
- 如果存在两个或多个有效结果，始终询问用户要优先选择哪个选项。

### 7. 递归循环和停止标准

重复步骤 2 到 6，直到出现以下结果之一：

- `<ruff_cmd> check` 返回干净。
- 剩余发现需要架构/产品决策。
- 剩余发现有意使用并记录了理由的抑制。
- 重复循环没有进展。

每个循环迭代必须在下一个 `<ruff_cmd> check` 之前包含 `<ruff_cmd> format`。

当检测到没有进展时：

1. 总结受阻的规则和受影响的文件。
2. 提供有效选项和权衡。
3. 询问用户选择。

## 质量门禁

在声明完成之前：

- Ruff 对于选定的范围/选项没有返回意外的发现。
- 所有自动修复的差异都经过审查以确保正确性。
- 没有在没有明确理由的情况下添加抑制。
- 任何可能影响行为的危险修复都突出显示给用户。
- Ruff 格式化在每次迭代中都执行。

## 输出契约

执行结束后报告：

- 使用的范围和 Ruff 选项。
- 执行的迭代次数。
- 修复发现的摘要。
- 手动修复列表。
- 抑制列表及其理由。
- 剩余发现（如果有），以及需要用户决策的事项。

## 建议的提示启动器

- "在完整仓库上使用默认配置运行 ruff-recursive-fix。"
- "仅在 src/models 上运行 ruff-recursive-fix，忽略 DOC 规则。"
- "在测试上运行 ruff-recursive-fix，选择 F,E9,I 并且不进行不安全的修复。"
- "在 src/data 上运行 ruff-recursive-fix，并在添加任何 noqa 之前询问我。"
