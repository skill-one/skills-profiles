# STRING 数据库技能

此技能允许您使用捆绑的 Python CLI 包装器以编程方式查询 STRING 数据库。

## 前置条件

1.  **`uv`**: 阅读 `uv` 技能并遵循其安装说明，确保 `uv` 已安装并在 PATH 中。
2.  **用户通知**: 如果工作区根目录中不存在 `.licenses/string_database_LICENSE.txt`，则 (1) 醒目地通知用户检查 https://string-db.org/cgi/access 中的条款，然后 (2) 创建记录通知文本和时间戳的文件。

## 核心规则

1.  **必须：首先询问物种**：STRING API 需要 NCBI 税号 ID。**您绝对不能猜测或假设物种**。如果用户没有明确说明物种或 Taxon ID，您必须停止并询问："您对哪个物种感兴趣？我需要 NCBI 税号 ID 才能继续。" 即使对于像 TP53、BRCA1 或 MDM2 这样通常与人类研究相关联的著名蛋白质，您也必须询问——不要默认为人类。
2.  **永远不要将输出打印到 stdout**：必须使用 `--output <file.tsv>`。永远不要将大型输出读入上下文。相反，使用 jq、python 或文件操作 (`grep`、`head`) 来处理大型输出。
3.  **首先映射标识符**：如果您只有常见基因名称（例如，'TP53'），请首先将它们映射到 STRING ID，因为这可以保证服务器响应速度更快。使用 `map` 命令进行此操作。
4.  **通知**：如果使用此技能，请确保在输出中提及。

## 工具执行

CLI 位于 `scripts/string_cli.py`，应使用 `uv run` 运行：

```bash
uv run scripts/string_cli.py <command> [options] --output /tmp/out.tsv
```

## 功能域（渐进式披露）

根据用户请求读取以下参考文件：

*   **[映射标识符](references/mapping.md)** - 将常见蛋白质名称映射到 STRING ID。
*   **[相互作用 & 网络](references/interactions.md)** - 查找相互作用蛋白、网络拓扑、中介物、同源性以及可视化网络图像。
*   **[富集 & 功能注释](references/enrichment.md)** - 分析通路富集（GO、KEGG、Pfam）、PPI 显著性或查找与特定术语（例如 Melanoma）相关的所有蛋白质。
*   **[值/排名富集](references/valuesranks.md)** - 提交完整的实验数据集（例如 logFC、p-values）以使用异步后台 API 进行基于排名的富集分析。

开始时，读取与当前任务最相关的参考文件以发现正确的 CLI 命令。
