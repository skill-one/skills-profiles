# 远程浏览器

当代理在无法使用本地 Chrome 的机器上运行，并需要隔离浏览器时，使用此技能。当前的 Browser Use CLI 从标准输入运行 Python。不要使用已移除的 `open`、`state`、`click`、`input`、`tab`、`cloud connect` 或 `--connect` 命令。

## 检查 CLI

```bash
browser-use --doctor
browser-use skill show
```

如果设置失败，请遵循当前的 [Browser Use 技能](../browser-use/SKILL.md)。

## 启动隔离浏览器

进行一次认证：

```bash
browser-use auth login
```

选择一个简短且唯一的名称。下面的 `r7k2` 仅为例子。

```bash
browser-use <<'PY'
start_remote_daemon("r7k2")
PY
```

在此浏览器中的每个命令都使用相同的名称：

```bash
BU_NAME=r7k2 browser-use <<'PY'
new_tab("https://example.com")
wait_for_load()
print(page_info())
PY
```

每个远程守护进程是一个独立的 Browser Use Cloud 浏览器。为每个并行任务使用不同的名称。远程浏览器在停止或超时前会计费。

## 检查和交互

辅助函数已预先导入。在实用的情况下，将多步工作保存在一个 heredoc 中。

```bash
BU_NAME=r7k2 browser-use <<'PY'
print(page_info())
print(js("document.title"))

fill_input('input[name="q"]', "browser automation")
press_key("Enter")
wait_for_load()

print(page_info())
PY
```

有用的辅助函数：

- 导航：`new_tab(url)`、`goto_url(url)`、`wait_for_load()`
- 检查：`page_info()`、`js(code)`、`cdp(method, ...)`
- 交互：`click_at_xy(x, y)`、`type_text(text)`、`fill_input(selector, text)`、`press_key(key)`、`scroll(x, y)`
- 标签页：`list_tabs()`、`switch_tab(target)`、`close_tab(target)`
- 文件和证明：`capture_screenshot()`、`wait_for_element(selector)`

优先使用可访问性树进行元素发现：

```python
nodes = cdp("Accessibility.getFullAXTree")["nodes"]
```

当可访问性树缺少元素时，使用目标 `js(...)` 查询。使用 `page_info()`、聚焦的 DOM 检查或截图来验证每个操作。

## 停止浏览器

完成工作后，停止指定的浏览器：

```bash
browser-use <<'PY'
stop_remote_daemon("r7k2")
PY
```

不要让未使用的远程浏览器一直运行。
