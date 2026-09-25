# Tavily 动态搜索

将大型原始网页数据保存在磁盘上，并仅返回任务所需的证据。这在使用 `--include-raw-content`、组合多个查询或提取多个长页面时很有用。不要使用此工作流程来处理一个普通 `tvly search --json` 可以直接回答的简单查询。

## 运行前准备

搜索和提取支持无密钥访问。当 `tvly` 可用时直接运行它们。如果 `tvly` 缺失，请按照
[tavily-cli setup](../tavily-cli/SKILL.md#setup) 进行设置。在第一次请求之前不要寻找 API 密钥或进行身份验证。如果在交互式会话中达到无密钥访问限制，请运行 `tvly login` 打开浏览器 OAuth，然后重试被阻止的请求一次。在不被管理的环境中，报告访问限制和身份验证选项，而不是启动交互式流程。

## 工作流程

1. 不带原始内容进行广泛搜索，并检查标题、URL、分数和片段。
2. 仅获取最佳来源的完整内容。
3. 当原始输出可能很大时，使用 `-o` 保存它，并在将任何内容打印到模型上下文之前过滤文件。
4. 在每个提取的事实旁边保留源 URL。

当用户将证据限制为官方或命名域时，在本地过滤期间验证每个选定 URL 的主机名。`--include-domains` 会缩小搜索范围，但并不能证明返回的每个结果都属于允许的主机。如果无法进行全页提取，则将结论标记为搜索片段证据，而不是暗示页面主体已被验证。

当相关来源和过滤器已知时，保持一个回合内的流程。只有在第一次搜索改变了应提取的内容时，才使用另一个回合。

在保存证据之前创建一个唯一的临时任务目录，以防止并发代理相互覆盖。当不允许使用 `mktemp` 时，可以使用 Python 的 `tempfile.mkdtemp()`。将此目录用于任务的所有原始和过滤后的工件。

## 小型结果：过滤直接 JSON 响应

对于小型搜索响应，管道就足够了：

```bash
tvly search "query" --max-results 5 --json | python3 -c '
import json, sys
data = json.load(sys.stdin)
for result in data.get("results", []):
    score = result.get("score") or 0
    title = result.get("title") or ""
    print(f"[{score:.2f}] {title}")
    print(result.get("url", ""))
    print(result.get("content", "")[:300])
'
```

不要丢弃标准错误。身份验证失败、无密钥访问限制消息和 API 错误都是可操作的，必须保持可见。

## 大型结果：先保存，再过滤

使用 CLI 的文件输出，以防止原始页面内容通过工具响应：

```bash
tvly search "query" \
  --include-raw-content markdown \
  --max-results 8 \
  --json \
  -o /tmp/tavily-search-results.json
```

然后仅打印有限的证据：

```bash
python3 -c '
import json
from pathlib import Path

data = json.loads(Path("/tmp/tavily-search-results.json").read_text())
for result in data.get("results", []):
    title = result.get("title") or ""
    url = result.get("url") or ""
    print(f"## {title}")
    print(f"URL: {url}")
    print((result.get("raw_content") or result.get("content") or "")[:1200])
    print()
'
```

根据问题调整过滤逻辑。当目标信息已知时，优先选择相关段落或字段，而不是固定的字符切片。除非表格或代码块确实需要更多，否则每个来源的目标大约为 150-600 个标记。

## 针对性提取

当搜索识别出正确的 URL 时，仅提取这些页面：

```bash
tvly extract "https://example.com/article" \
  --json \
  -o /tmp/tavily-extract-results.json
```

对于主题聚焦的页面，让 Tavily 在本地过滤之前减少响应：

```bash
tvly extract "https://example.com/docs" \
  --query "authentication API" \
  --chunks-per-source 3 \
  --json \
  -o /tmp/tavily-extract-results.json
```

## 多个查询

对于多角度研究，运行一小组聚焦搜索，按 URL 去重，然后排序再提取。在 Python 中编排命令时使用 `subprocess.run(..., capture_output=True, text=True)`。检查 `returncode`；如果命令失败，则显示其标准错误并有意停止或重试。永远不要使用隐藏缺失证据的通用 `except Exception: continue`。

## 响应格式

`tvly search --json` 返回 `query`、可选的 `answer`、`results` 和 `response_time`。每个结果通常包含 `url`、`title`、`content`、`score` 和可选的 `raw_content`。

`tvly extract --json` 返回 `results`、`failed_results` 和 `response_time`。每个成功的结果通常包含 `url`、`raw_content` 和可选的图像。

将字段视为可选的，并在过滤时使用 `.get()`。检查 `failed_results` 而不是假设每个请求的 URL 都成功。

## 有用的选项

| 选项 | 目的 |
|------|------|
| `--max-results` | 限制搜索结果数量；默认为 5，最大为 20 |
| `--depth` | 选择 `ultra-fast`、`fast`、`basic` 或 `advanced` |
| `--time-range` | 将结果限制为 `day`、`week`、`month` 或 `year` |
| `--include-domains` | 将结果限制为逗号分隔的受信任域列表 |
| `--exclude-domains` | 排除逗号分隔的域列表 |
| `--include-raw-content` | 包含完整内容为 `markdown` 或 `text` |
| `-o, --output` | 将完整响应保存到文件 |

当 Python 不可用时，仅使用 `jq` 进行简短过滤：

```bash
tvly search "query" --json | jq '[.results[] | {title, url, score, content}]'
```
