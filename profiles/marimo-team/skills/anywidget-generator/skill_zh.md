在编写 anywidget 时，请在 `_esm` 中使用原味 JavaScript，并不要忘记 `_css`。CSS 应该在亮色模式和暗色模式下都看起来定制化。除非明确要求，否则保持 CSS 简小。当您显示小部件时，必须通过 `widget = mo.ui.anywidget(OriginalAnywidget())` 进行包装。如果需要，您也可以使用 pathlib 将 `_esm` 和 `_css` 指向外部文件。如果小部件执行大量复杂的 JavaScript 或 CSS，这样做是有意义的。

<example title="简单 anywidget 实现示例">
import anywidget
import traitlets


class CounterWidget(anywidget.AnyWidget):
    _esm = """
    // 定义主要渲染函数
    function render({ model, el }) {
      let count = () => model.get("number");
      let btn = document.createElement("button");
      btn.innerHTML = `count is ${count()}`;
      btn.addEventListener("click", () => {
        model.set("number", count() + 1);
        model.save_changes();
      });
      model.on("change:number", () => {
        btn.innerHTML = `count is ${count()}`;
      });
      el.appendChild(btn);
    }
    // 重要！我们必须在这里底部导出！
    export default { render };
    """
    _css = """button{
      font-size: 14px;
    }"""
    number = traitlets.Int(0).tag(sync=True)

widget = mo.ui.anywidget(CounterWidget())
widget

# 从另一个单元格获取小部件，`.value` 是一个字典。
print(widget.value["number"])
</example>

以上是一个可以用于简单计数器小部件的最小示例。通常，由于所需的 JavaScript 和 CSS 很多，小部件可以变得更大。除非小部件非常简单，否则您应该考虑使用 pathlib 为 `_esm` 和 `_css` 使用外部文件。

在共享 anywidget 时，保持示例最小。除非明确说明，否则无需将其与 marimo UI 元素结合使用。

## 最佳实践

除非特别说明，请假设以下内容：

1. **在 `_esm` 中使用原味 JavaScript**：
   - 定义一个 `render` 函数，该函数将 `{ model, el }` 作为参数
   - 使用 `model.get()` 读取特征值
   - 使用 `model.set()` 和 `model.save_changes()` 更新特征值
   - 使用 `model.on("change:traitname", callback)` 监听变化
   - 在底部使用 `export default { render };` 导出默认值
   - 所有小部件都继承自 `anywidget.AnyWidget`，因此 `widget.observe(handler)` 仍然是响应状态变化的标准方法。
   - Python 构造函数通常会验证边界、长度或选择计数；让引发的 `ValueError/TraitError` 指导您，而不是重复逻辑。

2. **包含 `_css` 样式**：
   - 除非明确要求更多，否则保持 CSS 简小
   - 在亮色模式和暗色模式下都使其看起来定制化
   - 使用 CSS 媒体查询为暗色模式：`@media (prefers-color-scheme: dark) { ... }`

3. **用于显示小部件的包装**：
   - 始终使用 marimo 包装：`widget = mo.ui.anywidget(OriginalAnywidget())`
   - 通过 `widget.value` 访问值，它返回一个字典

4. **保持示例最小**：
   - 添加一个突出核心功能的 marimo 笔记本
   - 仅显示基本用法
   - 除非明确要求，否则不要将其他 marimo UI 元素结合使用

5. **外部文件路径**：当使用 pathlib 为外部 `_esm`/`_css` 文件时，将路径相对于项目目录保持相对，考虑使用 `Path(__file__)`。不要读取项目外部的文件（例如，`~/.ssh`、`~/.env`、`/etc/`）或将其内容嵌入小部件输出中。

简单更好。优先选择明显直接的代码，而不是巧妙的抽象——新加入项目的人应该能够从上到下阅读代码并理解它，而无需查找框架魔法或跟踪间接引用。
