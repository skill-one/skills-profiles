# marimo 笔记本的注意事项

marimo 使用 Python 创建笔记本，而 Jupyter 使用 JSON。以下是一个示例笔记本：

```python
# /// script
# 依赖项 = [
#     "marimo",
#     "numpy==2.4.3",
# ]
# requires-python = ">=3.14"
# ///

import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np

    return mo, np


@app.cell
def _():
    print("hello world")
    return


@app.cell
def _(np, slider):
    np.array([1,2,3]) + slider.value
    return


@app.cell
def _(mo):
    slider = mo.ui.slider(1, 10, 1, label="要添加的数字")
    slider
    return (slider,)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()

```

注意笔记本如何通过函数来表示单元格内容。每个单元格都使用 `@app.cell` 装饰器定义，函数的输入/输出就是单元格的输入/输出。marimo 通常会自动处理单元格之间的依赖关系。

## 运行 Marimo 笔记本

```bash
# 作为脚本运行（非交互式，用于测试）
uv run <notebook.py>

# 在浏览器中交互式运行
uv run marimo run <notebook.py>

# 交互式编辑
uv run marimo edit <notebook.py>
```

## 脚本模式检测

使用 `mo.app_meta().mode == "script"` 来检测命令行界面（CLI）与交互式模式：

```python
@app.cell
def _(mo):
    is_script_mode = mo.app_meta().mode == "script"
    return (is_script_mode,)
```

## 关键原则：保持简单

**始终显示所有 UI 元素。** 在脚本模式下只更改数据源。

- 滑块、按钮、小部件应始终创建并显示
- 在脚本模式下，使用合成/默认数据而不是等待用户输入
- 不要用 `if not is_script_mode` 条件包裹所有代码
- 不要使用 try/except 处理常规控制流

### 良好模式

```python
# 始终显示小部件
@app.cell
def _(ScatterWidget, mo):
    scatter_widget = mo.ui.anywidget(ScatterWidget())
    scatter_widget
    return (scatter_widget,)

# 仅根据模式更改数据源
@app.cell
def _(is_script_mode, make_moons, scatter_widget, np, torch):
    if is_script_mode:
        # 使用合成数据进行测试
        X, y = make_moons(n_samples=200, noise=0.2)
        X_data = torch.tensor(X, dtype=torch.float32)
        y_data = torch.tensor(y)
        data_error = None
    else:
        # 在交互模式下使用小部件数据
        X, y = scatter_widget.widget.data_as_X_y
        # ... 处理数据 ...
    return X_data, y_data, data_error

# 始终显示滑块 - 在两种模式下使用其 .value
@app.cell
def _(mo):
    lr_slider = mo.ui.slider(start=0.001, stop=0.1, value=0.01)
    lr_slider
    return (lr_slider,)

# 脚本模式下自动运行，交互模式下等待按钮
@app.cell
def _(is_script_mode, train_button, lr_slider, run_training, X_data, y_data):
    if is_script_mode:
        # 使用滑块默认值自动运行
        results = run_training(X_data, y_data, lr=lr_slider.value)
    else:
        # 等待按钮点击
        if train_button.value:
            results = run_training(X_data, y_data, lr=lr_slider.value)
    return (results,)
```

## 状态和响应性

单元格之间的变量定义了笔记本在 99% 的用例中的响应性。不需要特殊的状态管理。不要跨单元格修改对象（例如，`my_list.append()`）；创建新对象。除非需要双向 UI 同步或累积回调状态，否则避免使用 `mo.state()`。有关详细信息，请参阅 [STATE.md](references/STATE.md)。

## 不要用 `if` 语句保护单元格

Marimo 的响应性意味着单元格只有在它们的依赖关系准备好时才会运行。不要添加不必要的保护：

```python
# BAD - if 语句阻止图表显示
@app.cell
def _(plt, training_results):
    if training_results:  # WRONG - 不要这样做
        fig, ax = plt.subplots()
        ax.plot(training_results['losses'])
        fig
    return

# GOOD - 让 marimo 处理依赖关系
@app.cell
def _(plt, training_results):
    fig, ax = plt.subplots()
    ax.plot(training_results['losses'])
    fig
    return
```

无论如何，单元格都不会在 `training_results` 有值之前运行。

## 不要用 try/except 处理控制流

除非你在处理特定的、预期的异常，否则不要用 try/except 块包裹代码。让错误自然暴露。

```python
# BAD - 用 try/except 隐藏错误
@app.cell
def _(scatter_widget, np, torch):
    try:
        X, y = scatter_widget.widget.data_as_X_y
        X = np.array(X, dtype=np.float32)
        # ...
    except Exception as e:
        return None, None, f"错误: {e}"

# GOOD - 如果有问题就让它失败
@app.cell
def _(scatter_widget, np, torch):
    X, y = scatter_widget.widget.data_as_X_y
    X = np.array(X, dtype=np.float32)
    # ...
```

仅在以下情况下使用 try/except：
- 你在处理特定的、已知的异常类型
- 异常在正常操作中是预期的（例如，文件未找到）
- 你有有意义的恢复操作

## 单元格输出渲染

Marimo 只渲染单元格的**最终表达式**。缩进或条件表达式不会渲染：

```python
# BAD - 缩进表达式不会渲染
@app.cell
def _(mo, condition):
    if condition:
        mo.md("这不会显示！")  # WRONG - 缩进
    return

# GOOD - 最终表达式会渲染
@app.cell
def _(mo, condition):
    result = mo.md("显示！") if condition else mo.md("也显示！")
    result  # 这会渲染，因为它是最终表达式
    return
```

## PEP 723 依赖项

通过 `marimo edit --sandbox` 创建的笔记本会自动将以下依赖项添加到文件顶部，但在创建笔记本时也建议确保这些依赖项存在：

```python
# /// script
# requires-python = ">=3.12"
# 依赖项 = [
#     "marimo",
#     "torch>=2.0.0",
# ]
# ///
```

## marimo check

在处理笔记本时，检查笔记本是否可以运行非常重要。这就是为什么 marimo 提供了一个 `check` 命令，它充当一个检查器来查找常见的错误。

```bash
uvx marimo check <notebook.py>
```

在将笔记本交给用户之前，请确保这些检查已完成。

**重要**：你倾向于用下划线前缀过度使用变量。你最多只应将其应用于一个或两个变量。考虑创建一个新变量，而不是在 marimo 中为整个单元格添加前缀。

## api 文档

如果用户特别要求你使用 marimo 函数，你可以通过以下方式在本地检查文档：

```
uv --with marimo run python -c "import marimo as mo; help(mo.ui.form)"
```

## 测试

默认情况下，marimo 会发现并执行笔记本中的测试。
当可选的 `pytest` 依赖项存在时，marimo 会针对仅包含测试代码的单元格运行 `pytest` - 即名称以 `test_` 开头的函数。
如果用户要求你添加测试，请确保添加了 `pytest` 依赖项，并且有一个只包含测试代码的单元格。

有关使用 pytest 进行测试的更多信息，请参阅 [PYTEST.md](references/PYTEST.md)

添加测试后，你可以从命令行运行 pytest 来测试笔记本。

```
pytest <notebook.py>
```

## 额外资源

- 对于在 width=columns 模式下运行的 marimo 笔记本 [SQL.md](references/COLUMNS.md)
- 对于 marimo 中的 SQL 使用，请参阅 [SQL.md](references/SQL.md)
- 对于 marimo 中的 UI 元素 [UI.md](references/UI.md)
- 对于将函数/类作为顶级导入暴露 [TOP-LEVEL-IMPORTS.md](references/TOP-LEVEL-IMPORTS.md)
- 对于导出笔记本（PDF、HTML、markdown 等） [EXPORTS.md](references/EXPORTS.md)
- 对于状态管理和响应性 [STATE.md](references/STATE.md)
- 对于 marimo 笔记本的部署 [DEPLOYMENT.md](references/DEPLOYMENT.md)
- 对于使用 anywidget 创建自定义交互式小部件 [ANYWIDGET.md](references/ANYWIDGET.md)
- 对于外部编辑和 `--watch` 模式 [WATCHING.md](references/WATCHING.md)
- 对于昂贵的笔记本（缓存、延迟评估、mo.stop） [EXPENSIVE.md](references/EXPENSIVE.md)
- 对于配置（pyproject.toml、marimo.toml） [CONFIGURATION.md](references/CONFIGURATION.md)
- 对于响应性模型（DAG、变量作用域、突变） [REACTIVITY.md](references/REACTIVITY.md)
