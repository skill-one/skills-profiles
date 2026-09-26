# Obsidian Wiki Ingest — 自动化技能

你是将文档导入 Obsidian 维基项目的自动化层。此技能协调导入工作流程，确保去重、正确的元数据以及与现有页面的交叉链接。

## 触发条件
- 用户说："导入到维基"、"添加到维基" 或任何针对 obsidian-wiki 仓库的措辞。
- 上下文：在 /home/ubuntu/projects/obsidian-wiki 工作区中激活。

## 职责
- 从环境变量和清单状态中验证目标仓库路径。
- 根据用户输入或源的变化，在追加、完整或原始导入模式之间进行选择。
- 调用维基导入工作流程处理新/修改的源。
- 使用导入元数据更新清单和日志文件。
- 根据需要创建或更新项目概览页面和交叉链接。

## 输入
- 来自 OBSIDIAN_SOURCES_DIR 或 _raw/ 的源文档（Markdown、PDF、文本、图像）
- 来自 OBSIDIAN_VAULT_PATH 的仓库路径
- 可选：导入模式（追加|完整|原始）

## 输出
- 更新后的维基页面，包含提炼的知识
- 更新的 .manifest.json 和日志条目
- 可选：新/更新的项目概览页面

## 探测与安全
- 不要导入秘密或敏感数据。
- 尊重现有页面结构，避免重复内容。
- 使用来源注释标记推断/模糊的知识。

## 示例工作流程（高级概述）
1) 确定导入模式和目标路径
2) 以选定的模式运行 wiki-ingest
3) 更新清单/日志并刷新维基索引
4) 返回变更的简要摘要

## 下一步
- 如果您批准，我将创建一个小的包装脚本（scripts/ingest-wiki.sh），用于启动当前项目的导入并更新清单。然后为从 CLI 触发此技能设置一个简单的命令别名。

## 清单写入后刷新

QMD 是一个搜索索引，不是真相来源。如果 `$QMD_WIKI_COLLECTION` 为空或未设置，则跳过此步骤。仅在当前技能写入或重写仓库 Markdown 后运行它。如果 QMD 刷新失败，不要回滚仓库更改；单独报告 QMD 状态。

如果设置了 `$QMD_CLI`，则使用它；否则使用 `qmd`。

```bash
${QMD_CLI:-qmd} update
```

如果输出表示需要向量或嵌入可能已过时，运行：

```bash
${QMD_CLI:-qmd} embed
```

使用以下任一方式验证集合：

```bash
${QMD_CLI:-qmd} ls "$QMD_WIKI_COLLECTION"
```

或，当知道特定页面路径时：

```bash
${QMD_CLI:-qmd} get "qmd://$QMD_WIKI_COLLECTION/<page>.md" -l 5
```

记录以下之一：
- `QMD 刷新：更新 + 嵌入 + 验证`
- `QMD 刷新：仅更新 + 验证`
- `QMD 跳过：QMD_WIKI_COLLECTION 未设置`
- `QMD 跳过：qmd CLI 不可用`
- `QMD 失败：<简短错误摘要>`
