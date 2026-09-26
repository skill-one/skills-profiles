# 构建图

构建或增量更新此存储库的知识图谱。

## 步骤

1. 调用 `list_graph_stats_tool`。如果 `last_updated` 为空，则表示图谱尚未构建。
2. 对于首次构建，或当参数为 `full` 时，调用 `build_or_update_graph_tool(full_rebuild=True)`。否则调用 `build_or_update_graph_tool()` 进行增量更新。
3. 报告响应：`status` (`ok`, `partial` 或 `error`) 和 `summary`。

## 使用场景

- 存储库的首次设置，或在分支切换或大型重构之后。
- 当图谱看起来过时时。`code-review-graph install` 安装的钩子在每次编辑后和每次提交前运行更新，因此很少需要手动构建。

## 注意事项

- 数据库位于存储库根目录下的 `.code-review-graph/graph.db`。
- 二进制文件、依赖和构建目录，以及 `.code-review-graphignore` 中的模式将被跳过。
- 要获取支持的语言列表，请调用 `get_docs_section_tool(section_name="languages")`。
