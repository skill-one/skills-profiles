# 将 Streamlit 应用转换为 Marimo

有关 Marimo 笔记本的一般规范（单元格结构、PEP 723 元数据、输出渲染、`marimo check`、变量命名等），请参考 `marimo-notebook` 技能。此技能专注于将 Streamlit 概念映射到 Marimo 的等效功能。

## 步骤

1. **读取 Streamlit 应用**以了解其小部件、布局和状态管理。

2. **创建一个新的 Marimo 笔记本**，遵循 `marimo-notebook` 技能的规范。添加 Streamlit 应用使用的所有依赖项（pandas、plotly、altair 等）——但将 `streamlit` 替换为 `marimo`。您不应覆盖原始文件。

3. **使用下表中的参考表将 Streamlit 组件映射到 Marimo 的等效功能**。主要原则：
   - UI 元素被**分配给变量**，并通过 `.value` 访问其当前值。
   - 引用 UI 元素的单元格在用户与其交互时自动重新运行——无需回调。

4. **处理执行模型、状态和缓存中的概念差异**（见下文）。

5. **对结果运行 `uvx marimo check` 并修复任何问题**。

## 小部件映射参考

### 输入小部件

| Streamlit | marimo | 备注 |
|-----------|--------|-------|
| `st.slider()` | `mo.ui.slider()` | |
| `st.select_slider()` | `mo.ui.slider(steps=[...])` | 通过 `steps` 传递离散值 |
| `st.text_input()` | `mo.ui.text()` | |
| `st.text_area()` | `mo.ui.text_area()` | |
| `st.number_input()` | `mo.ui.number()` | |
| `st.checkbox()` | `mo.ui.checkbox()` | |
| `st.toggle()` | `mo.ui.switch()` | |
| `st.radio()` | `mo.ui.radio()` | |
| `st.selectbox()` | `mo.ui.dropdown()` | |
| `st.multiselect()` | `mo.ui.multiselect()` | |
| `st.date_input()` | `mo.ui.date()` | |
| `st.time_input()` | `mo.ui.text()` | 没有专用的时间小部件 |
| `st.file_uploader()` | `mo.ui.file()` | 使用 `.contents()` 读取字节 |
| `st.color_picker()` | `mo.ui.text(value="#000000")` | 没有专用的颜色选择器 |
| `st.button()` | `mo.ui.button()` 或 `mo.ui.run_button()` | 使用 `run_button` 触发昂贵的计算 |
| `st.download_button()` | `mo.download()` | 返回下载链接元素 |
| `st.form()` + `st.form_submit_button()` | `mo.ui.form(element)` | 将任何元素包装起来，使其值仅在提交时更新 |

### 显示元素

| Streamlit | marimo | 备注 |
|-----------|--------|-------|
| `st.write()` | `mo.md()` 或最后一个表达式 | |
| `st.markdown()` | `mo.md()` | 支持格式化字符串：`mo.md(f"Value: {x.value}")` |
| `st.latex()` | `mo.md(r"$...$")` | marimo 使用 KaTeX；参见 `references/latex.md` |
| `st.code()` | `mo.md("```python\n...\n```")` | |
| `st.dataframe()` | `df` (最后一个表达式) | 数据框原生作为交互式 marimo 小部件渲染；仅用于无代码转换时使用 `mo.ui.dataframe(df)` |
| `st.table()` | `df` (最后一个表达式) | 如果需要行选择，使用 `mo.ui.table(df)` |
| `st.metric()` | `mo.stat()` | |
| `st.json()` | `mo.json()` 或 `mo.tree()` | `mo.tree()` 用于交互式可折叠视图 |
| `st.image()` | `mo.image()` | |
| `st.audio()` | `mo.audio()` | |
| `st.video()` | `mo.video()` | |

### 图表

| Streamlit | marimo | 备注 |
|-----------|--------|-------|
| `st.plotly_chart(fig)` | `fig` (最后一个表达式) | 使用 `mo.ui.plotly(fig)` 进行选择 |
| `st.altair_chart(chart)` | `chart` (最后一个表达式) | 使用 `mo.ui.altair_chart(chart)` 进行选择 |
| `st.pyplot(fig)` | `fig` (最后一个表达式) | 使用 `mo.ui.matplotlib(fig)` 进行交互式 matplotlib |

### 布局

| Streamlit | marimo | 备注 |
|-----------|--------|-------|
| `st.sidebar` | `mo.sidebar([...])` | 传递元素列表 |
| `st.columns()` | `mo.hstack([...])` | 使用 `widths=[...]` 设置列比例 |
| `st.tabs()` | `mo.ui.tabs({...})` | 字典形式 `{"Tab Name": content}` |
| `st.expander()` | `mo.accordion({...})` | 字典形式 `{"Title": content}` |
| `st.container()` | `mo.vstack([...])` | |
| `st.empty()` | `mo.output.replace()` | |
| `st.progress()` | `mo.status.progress_bar()` | |
| `st.spinner()` | `mo.status.spinner()` | 上下文管理器 |

## 关键概念差异

### 执行模型

Streamlit 在每次交互时**从头到尾重新运行整个脚本**。Marimo 使用**反应式单元格 DAG**——只有依赖已更改变量的单元格会重新执行。

- 无需 `st.rerun()` —— 反应性是自动的。
- 无需 `st.stop()` —— 结构化单元格，使下游单元格自然依赖于上游值。

### 状态管理

| Streamlit | marimo |
|-----------|--------|
| `st.session_state["key"]` | 单元格之间的常规 Python 变量 |
| 回调函数 (`on_change`) | 引用 `widget.value` 的单元格会自动重新运行 |
| `st.query_params` | `mo.query_params` |

### 缓存

| Streamlit | marimo |
|-----------|--------|
| `@st.cache_data` | `@mo.cache` | 基于函数参数进行缓存；marimo 感知 |
| `@st.cache_resource` | `@mo.persistent_cache` | 跨笔记本重启持久化（序列化到磁盘） |

`@mo.cache` 是主要的缓存装饰器——它像 `functools.cache` 一样工作，但感知 marimo 的反应性。`@mo.persistent_cache` 通过将结果持久化到磁盘来跨会话更进一步，适用于昂贵的计算，如模型训练。

### 多页面应用

Marimo 为多页 Streamlit 应用提供两种方法：

- **单个笔记本带路由**：使用 `mo.routes` 与 `mo.nav_menu` 或 `mo.sidebar` 构建一个笔记本内的多个“页面”（标签/路由）。
- **多个笔记本作为画廊**：使用 `marimo run folder/` 运行笔记本文件夹，将它们作为带导航的画廊提供。

### 部署

marimo 特性 molab 用于托管 marimo 应用，而不是 Streamlit 社区云。您可以通过 `add-molab-badge` 技能生成一个“在 molab 中打开”按钮。

### 自定义组件

streamlit 具有自定义组件的功能。这些与 marimo 不兼容。您可能可以通过 `marimo-anywidget` 技能生成等效的 anywidget，但在开始之前请与用户讨论。
