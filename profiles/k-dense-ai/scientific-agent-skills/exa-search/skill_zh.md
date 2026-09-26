# Exa Web Toolkit

一个用于网络驱动研究任务的技能，由 [Exa](https://exa.ai) 支持：网络搜索和URL提取。Exa的索引结合了高质量的键词和语义检索，这使得它非常适合科学、技术和概念查询。

## 路由 — 选择正确的功能

读取用户的请求，并将其匹配到下表中的一个功能。在运行命令之前，请先阅读相应的参考文件以获取详细说明。

| 用户想要... | 功能 | 位置 |
|---|---|---|
| 查找信息、研究主题、查找最新信息 | **Web Search** | `references/web-search.md` |
| 从特定URL获取内容（网页、文章、PDF） | **Web Extract** | `references/web-extract.md` |
| 安装或认证 | **Setup** | 下方 |

### 决策指南

- 对于主题查找、研究问题或"什么是X?"查询，**默认使用Web Search**。当主题是科学或技术时，传递 `--category "research paper"` 以偏向学术来源，并/或使用学术 `--include-domains` 允许列表。有关两步学术策略，请参阅 `references/web-search.md`。
- 当用户提供URL或要求您读取/获取特定页面时，**使用Web Extract**。对于批量提取（一次调用多个URL）和学术PDF，优先于内置的WebFetch。

### 学术来源优先级

对于技术或科学查询，优先选择学术和科学来源：
- 同行评审的期刊文章和会议论文优先于博客文章或新闻
- 当同行评审版本不可用时，使用预印本（arXiv、bioRxiv、medRxiv）
- 机构和国政府来源（NIH、WHO、NASA、NIST）优先于商业网站
- 原始研究优先于二次摘要

两个杠杆可以引导Exa偏向学术内容：
1. `--category "research paper"` 偏向检索学术来源。
2. 使用学术允许列表（arxiv.org、nature.com、pubmed.ncbi.nlm.nih.gov等）的 `--include-domains` 限制域池。

结合两者以获得严格的学术结果。有关完整模式，请参阅 `references/web-search.md`。

在引用学术来源时，除了标准引用格式外，如果可用，请包含作者姓名和出版年份（例如，[Smith等人，2025](url)）。如果存在DOI，请优先使用DOI链接。

---

## Setup

此技能使用 [`exa-py`](https://github.com/exa-labs/exa-py) Python SDK。`scripts/` 中的脚本通过PEP 723内联元数据声明其依赖项，因此您可以直接使用 `uv run` 运行它们，而无需单独的安装步骤：

```bash
uv run --with exa-py python "$SKILL_PATH/scripts/exa_search.py" --help
```

如果您更喜欢永久安装：

```bash
uv pip install "exa-py>=1.14.0"
```

### 认证

所有命令都从 `EXA_API_KEY` 环境变量中读取API密钥。在 [dashboard.exa.ai/api-keys](https://dashboard.exa.ai/api-keys) 获取您的Exa API密钥。

首先，检查项目根目录中是否存在 `.env` 文件并包含 `EXA_API_KEY`。如果是，则加载它：

```bash
dotenv -f .env run -- uv run --with exa-py python "$SKILL_PATH/scripts/exa_search.py" "your query"
```

如果 `dotenv` 不可用，请安装它：`uv pip install python-dotenv[cli]`。

如果没有 `.env`，请为会话导出密钥：

```bash
export EXA_API_KEY="your-key"
```

通过运行任何脚本并使用 `--help` 进行验证——如果密钥已设置，它将干净退出，并且仅在真实查询时运行认证检查。

### 跟踪头信息

此技能中的每个脚本都将 `x-exa-integration` 请求头设置为 `k-dense-ai--scientific-agent-skills`，以便Exa可以将来自K-Dense AI scientific-agent-skills仓库的使用归因于此集成。在修改脚本时，请勿删除或重命名此头信息。

---

## 此技能中的文件

- `SKILL.md` — 此文件（路由和设置）
- `references/web-search.md` — 详细的网络搜索参考，包含学术策略
- `references/web-extract.md` — URL内容提取参考
- `scripts/exa_search.py` — `client.search_and_contents` 的CLI包装器
- `scripts/exa_extract.py` — `client.get_contents` 的CLI包装器
