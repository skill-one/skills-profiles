---
name: agentmemory-mcp-tools
description: 每个agentmemory MCP工具的地图，每个工具的作用及其参数。在以下情况下使用：选择调用哪个内存工具时，工具名称或参数不明确时，或通过MCP回答agentmemory能做什么时。
---

agentmemory 将其全部功能集以 MCP 工具的形式展现。这项技能是索引：它告诉你该使用哪个工具以及如何找到精确的参数。

## 快速入门

保存后召回：

1. 使用 `memory_save` 命令，提供 `content`（洞察）、`concepts`（逗号分隔的关键词）和 `files`（逗号分隔的路径）。
2. 使用 `memory_smart_search` 命令，提供 `query` 和 `limit` 参数来稍后检索。这会运行混合 BM25、向量搜索和图扩展搜索。

## 工具家族

- 捕获：`memory_save`、`memory_observe` 流程、`memory_compress_file`。
- 检索：`memory_smart_search`、`memory_recall`、`memory_file_history`、`memory_timeline`、`memory_vision_search`。
- 会话和提交：`memory_sessions`、`memory_commits`、`memory_commit_lookup`。
- 知识和图谱：`memory_lesson_save`、`memory_lesson_recall`、`memory_graph_query`、`memory_relations`、`memory_patterns`、`memory_crystallize`。
- 结构化槽位：`memory_slot_create`、`memory_slot_append`、`memory_slot_get`、`memory_slot_list`、`memory_slot_replace`、`memory_slot_delete`。
- 管理和健康：`memory_governance_delete`、`memory_audit`、`memory_verify`、`memory_heal`、`memory_diagnose`。

## 工作流程

1. 为任务选择最精确的工具。对于开放召回，优先使用 `memory_smart_search`；当你已有聚焦查询时，使用 `memory_recall`；用于会话列表时，使用 `memory_sessions`。
2. 在调用前，在 REFERENCE.md 中查找确切的参数名称以及哪些是必需的。
3. 仅传递文档中记录的字段。REST 处理程序会白名单字段并丢弃未知的字段。

## 参见

- agentmemory-rest-api 用于 HTTP 对等物。
- agentmemory-config 用于工具可见性和功能标志。
- 用户可调用的动作技能（记住、召回、重述、交接、遗忘）封装了最常见的工具。

## 参考

完整的工具表及其参数和核心集标记位于 REFERENCE.md 中，该文件从源代码生成，因此永远不会漂移。
