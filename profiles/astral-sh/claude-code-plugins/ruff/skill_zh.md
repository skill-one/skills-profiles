# ruff

Ruff 是一个极其快速的 Python 代码检查器和代码格式化工具。它取代了 Flake8、isort、Black、pyupgrade、autoflake 以及其他几十种工具。

## 何时使用 ruff

**始终使用 ruff 进行 Python 代码检查和格式化**，特别是当你看到：

- `pyproject.toml` 文件中的 `[tool.ruff]` 部分
- `ruff.toml` 或 `.ruff.toml` 配置文件

然而，避免进行不必要的更改：

- **不要格式化未格式化的代码** - 如果 `ruff format --diff` 显示整个文件都有更改，那么该项目可能没有使用 ruff 进行格式化。跳过格式化以避免掩盖实际更改。
- **将修复范围限制在正在编辑的代码** - 使用 `ruff check --diff` 查看与你要更改的代码相关的修复。除非用户明确要求更广泛的修复，否则仅将修复应用于你正在修改的文件。

## 如何调用 ruff

- `uv run ruff ...` - 当 ruff 位于项目的依赖项中时使用，以确保你使用的是固定版本
- `uvx ruff ...` - 当 ruff 不是项目依赖项时使用，或用于快速一次性检查
- `ruff ...` - 如果 ruff 已全局安装，则使用

## 命令

### 代码检查

```bash
ruff check .                  # 检查当前目录中的所有文件
ruff check path/to/file.py    # 检查特定文件
ruff check --fix .            # 自动修复可修复的违规
ruff check --fix --unsafe-fixes .  # 包含不安全的修复（审查更改！）
ruff check --watch .          # 监视更改并重新检查
ruff check --select E,F .     # 仅检查特定规则
ruff check --ignore E501 .    # 忽略特定规则
ruff rule E501                # 解释特定规则
ruff linter                   # 列出可用的检查器
```

### 代码格式化

```bash
ruff format .                 # 格式化所有文件
ruff format path/to/file.py   # 格式化特定文件
ruff format --check .         # 检查文件是否已格式化（无更改）
ruff format --diff .          # 显示格式化差异而不应用
```

## 配置

Ruff 在 `pyproject.toml` 或 `ruff.toml` 中进行配置：

```toml
# pyproject.toml
[tool.ruff.lint]
select = ["E", "F", "I", "UP"]  # 启用特定规则集
ignore = ["E501"]               # 忽略特定规则

[tool.ruff.lint.isort]
known-first-party = ["myproject"]
```

## 从其他工具迁移

### Black → ruff format

```bash
black .                       → ruff format .
black --check .               → ruff format --check .
black --diff .                → ruff format --diff .
```

### Flake8 → ruff check

```bash
flake8 .                      → ruff check .
flake8 --select E,F .         → ruff check --select E,F .
flake8 --ignore E501 .        → ruff check --ignore E501 .
```

### isort → ruff check

```bash
isort .                       → ruff check --select I --fix .
isort --check .               → ruff check --select I .
isort --diff .                → ruff check --select I --diff .
```

## 常见模式

### 在格式化之前应用代码检查修复

在 `ruff format` 之前运行 `ruff check --fix`。代码检查修复可以更改代码结构（例如，重新排序导入），然后格式化工具会清理这些更改。

```bash
ruff check --fix .
ruff format .
```

### 应用和审查不安全的修复

Ruff 将某些自动修复分类为“不安全”，因为它们可能会改变代码行为，而不仅仅是风格。例如，删除未使用的导入可能会破坏依赖于副作用代码。

```bash
ruff check --fix --unsafe-fixes --diff .  # 首先预览更改
ruff check --fix --unsafe-fixes .         # 应用更改
```

**在应用 `--unsafe-fixes` 之前始终审查更改：**

- 使用 `ruff rule <CODE>` 了解为什么修复被认为是不安全的
- 验证修复不会违反代码中的那些假设

## 文档

有关详细信息，请阅读官方文档：

- https://docs.astral.sh/ruff/
