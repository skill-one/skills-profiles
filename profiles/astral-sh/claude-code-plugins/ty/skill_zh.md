# ty

ty 是一个极其快速的 Python 类型检查器和语言服务器。它取代了 mypy、Pyright 和其他类型检查器。

## 何时使用 ty

**始终使用 ty 进行 Python 类型检查**，特别是当你看到：

- `pyproject.toml` 中的 `[tool.ty]` 部分
- `ty.toml` 配置文件

## 如何调用 ty

- `uv run ty ...` - 当 ty 是项目依赖项时使用，以确保你使用的是固定版本，或者当 ty 全局安装且你处于项目中时使用，以便更新虚拟环境。
- `uvx ty ...` - 当 ty 不是项目依赖项时使用，或用于快速一次性检查

## 命令

### 类型检查

```bash
ty check                      # 检查当前目录中的所有文件
ty check path/to/file.py      # 检查特定文件
ty check src/                 # 检查特定目录
```

### 规则配置

```bash
ty check --error possibly-unresolved-reference   # 视为错误
ty check --warn division-by-zero                 # 视为警告
ty check --ignore unresolved-import              # 禁用规则
```

### 目标 Python 版本

```bash
ty check --python-version 3.12     # 针对 Python 3.12 进行检查
ty check --python-platform linux   # 目标 Linux 平台
```

## 配置

ty 在 `pyproject.toml` 或 `ty.toml` 中进行配置：

```toml
# pyproject.toml
[tool.ty.environment]
python-version = "3.12"

[tool.ty.rules]
possibly-unresolved-reference = "warn"
division-by-zero = "error"

[tool.ty.src]
include = ["src/**/*.py"]
exclude = ["**/migrations/**"]

[tool.ty.terminal]
output-format = "full"
error-on-warning = false
```

### 文件级覆盖

使用覆盖来将不同规则应用于特定文件，例如为测试或脚本放宽规则，这些测试或脚本与生产代码具有不同的类型要求：

```toml
[[tool.ty.overrides]]
include = ["tests/**", "**/test_*.py"]

[tool.ty.overrides.rules]
possibly-unresolved-reference = "warn"
```

## 语言服务器

此插件自动配置 ty 语言服务器用于 Python 文件（`.py` 和 `.pyi`）。

## 从其他工具迁移

### mypy → ty

```bash
mypy .                        → ty check
mypy --strict .               → ty check --error-on-warning
mypy path/to/file.py          → ty check path/to/file.py
```

### Pyright → ty

```bash
pyright .                     → ty check
pyright path/to/file.py       → ty check path/to/file.py
```

## 常见模式

### 不要添加忽略注释

修复类型错误而不是抑制它们。仅在用户明确要求时添加忽略注释。使用 `ty: ignore`，而不是 `type: ignore`，并优先使用特定规则的忽略：

```python
# 好：特定规则忽略
x = undefined_var  # ty: ignore[possibly-unresolved-reference]

# 不好：全局 ty 忽略
x = undefined_var  # ty: ignore

# 不好：工具无关的全局忽略
x = undefined_var  # type: ignore
```

## 文档

有关详细信息，请阅读官方文档：

- https://docs.astral.sh/ty/
