# 代码检查与格式化

---

## 运行格式化工具

在打开 PR 之前运行：

```bash
# 检查模式（不应用更改）
BASE_REF=main CHECK_ONLY=true SKIP_DOCS=false bash tools/autoformat.sh

# 修复模式
BASE_REF=main CHECK_ONLY=false bash tools/autoformat.sh
```

调用的工具：`black`、`isort`、`pylint`、`ruff`、`mypy`。

---

## 导入排序

在任意 Python 文件中编辑导入后，提交前始终在这些文件上运行 `uv run isort`：

```bash
uv run isort <file1>.py <file2>.py
```

---

## 设置代码检查组

在容器内部：

```bash
uv sync --locked --only-group linting
```

这会安装 `ruff`、`black`、`isort`、`pylint` — 这些是与 `tools/autoformat.sh` 和 CI 的 `linting` 任务使用的相同工具。

---

## 代码风格规则

- **类型提示**：所有公共 API 函数都必须使用类型提示。使用 `X | None`，而不是 `Optional[X]`。
- **文档字符串**：所有公共类和函数使用 Google 风格。
- **命名**：遵循 Python 习惯 — 函数和变量使用 `snake_case`，类使用 `PascalCase`。
- **行长度**：119 个字符（在 `pyproject.toml` 中配置）。
- **避免裸 `except`**：始终捕获特定的异常类型。
