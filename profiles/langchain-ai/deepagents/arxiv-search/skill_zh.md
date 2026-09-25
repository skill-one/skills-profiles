# arXiv 搜索技能

## 使用方法

使用系统提示符中的绝对技能目录路径运行捆绑的 Python 脚本：

```bash
.venv/bin/python [您的技能目录]/arxiv-search/arxiv_search.py "您的搜索查询" [--max-papers N]
```

- `query` (必需): 搜索查询字符串
- `--max-papers` (可选): 要检索的最大结果数量（默认：10）

### 示例

```bash
.venv/bin/python ~/.deepagents/agent/skills/arxiv-search/arxiv_search.py "深度学习药物发现" --max-papers 5
```

返回每个匹配论文的标题和摘要，按相关性排序。

## 依赖项

需要 `arxiv` Python 包。如果缺失，使用以下命令安装：

```bash
.venv/bin/python -m pip install arxiv
```
