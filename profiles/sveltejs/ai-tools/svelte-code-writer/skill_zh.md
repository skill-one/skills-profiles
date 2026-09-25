## 命令行工具

您可以使用 `@sveltejs/mcp` 命令行工具获取 Svelte 相关的帮助。通过 `npx` 使用这些命令：

### 列出文档章节

```bash
npx @sveltejs/mcp list-sections
```

列出所有可用的 Svelte 5 和 SvelteKit 文档章节及其标题和路径。

### 获取文档

```bash
npx @sveltejs/mcp get-documentation "<section1>,<section2>,..."
```

获取指定章节的完整文档。在 `list-sections` 之后使用，以获取相关文档。

**示例：**

```bash
npx @sveltejs/mcp get-documentation "$state,$derived,$effect"
```

### Svelte 自动修复工具

```bash
npx @sveltejs/mcp svelte-autofixer "<代码或路径>" [选项]
```

分析 Svelte 代码，并为常见问题提供修复建议。

**选项：**

- `--async` - 启用异步 Svelte 模式（默认：false）
- `--svelte-version` - 目标版本：4 或 5（默认：5）

**示例：**

```bash
# 分析内联代码（将 $ 转义为 \$）
npx @sveltejs/mcp svelte-autofixer '<script>let count = \$state(0);</script>'

# 分析文件
npx @sveltejs/mcp svelte-autofixer ./src/lib/Component.svelte

# 目标 Svelte 4
npx @sveltejs/mcp svelte-autofixer ./Component.svelte --svelte-version 4
```

**重要提示：** 当通过终端传递包含 runes（如 `$state`、`$derived` 等）的代码时，将 `$` 字符转义为 `\$`，以防止 shell 变量替换。

## 工作流程

1. **不确定语法？** 运行 `list-sections` 然后运行 `get-documentation` 获取相关主题
2. **审查/调试？** 运行 `svelte-autofixer` 在代码上检测问题
3. **始终验证** - 在最终确定任何 Svelte 组件之前运行 `svelte-autofixer`
