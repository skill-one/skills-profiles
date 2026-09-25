# Hugging Face 论文页面

Hugging Face 论文页面 (hf.co/papers) 是一个基于 arXiv (arxiv.org) 构建的平台，专门用于人工智能 (AI) 和计算机科学领域的研究论文。Hugging Face 用户可以在 hf.co/papers/submit 提交他们的论文，并在 Daily Papers 汇报 (hf.co/papers) 中展示它。每天，用户可以对论文进行点赞和评论。每个论文页面允许作者：

- 声明他们的论文（通过点击 `作者` 字段中的他们的名字）。这会使论文页面出现在他们的 Hugging Face 个人资料中。
- 通过在模型卡、数据集卡或 Space 的 README 中包含 HF 论文或 arXiv URL 来链接相关的模型检查点、数据集和 Spaces。
- 链接 Github 仓库和/或项目页面 URL
- 链接 HF 组织。这也使论文页面出现在 Hugging Face 组织页面。

每当有人在 Space 仓库的模型卡、数据集卡或 README 中提及一个 HF 论文或 arXiv 摘要/PDF URL 时，该论文将自动被索引。请注意，并非所有在 Hugging Face 上索引的论文都提交到了每日论文中。后者更像是一种推广研究论文的方式。论文只能提交到每日论文，直到它们在 arXiv 上发布后的 14 天内。

Hugging Face 团队构建了一个易于使用的 API 来与论文页面进行交互。论文的内容可以作为 markdown 获取，或者返回结构化的元数据，例如作者姓名、链接的模型/数据集/Spaces、链接的 Github 仓库和项目页面。

## 使用场景

- 用户分享了一个 Hugging Face 论文页面 URL（例如 `https://huggingface.co/papers/2602.08025`）
- 用户分享了一个 Hugging Face markdown 论文页面 URL（例如 `https://huggingface.co/papers/2602.08025.md`）
- 用户分享了一个 arXiv URL（例如 `https://arxiv.org/abs/2602.08025` 或 `https://arxiv.org/pdf/2602.08025`）
- 用户提及了一个 arXiv ID（例如 `2602.08025`）
- 用户要求你总结、解释或分析一篇 AI 研究论文

## 解析论文 ID

建议从用户提供的任何内容中解析论文 ID（arXiv ID）：

| 输入 | 论文 ID |
| --- | --- |
| `https://huggingface.co/papers/2602.08025` | `2602.08025` |
| `https://huggingface.co/papers/2602.08025.md` | `2602.08025` |
| `https://arxiv.org/abs/2602.08025` | `2602.08025` |
| `https://arxiv.org/pdf/2602.08025` | `2602.08025` |
| `2602.08025v1` | `2602.08025v1` |
| `2602.08025` | `2602.08025` |

这允许你将论文 ID 提供给下面提到的任何 hub API 端点。

### 以 markdown 格式获取论文页面

论文的内容可以作为 markdown 获取，如下所示：

```bash
curl -s "https://huggingface.co/papers/{PAPER_ID}.md"
```

这应该返回 Hugging Face 论文页面作为 markdown。这依赖于 arxiv.org/html/{PAPER_ID} 处的论文 HTML 版本。

有两个例外：

- 并非所有 arXiv 论文都有 HTML 版本。如果论文的 HTML 版本不存在，则内容会回退到 Hugging Face 论文页面的 HTML。
- 如果导致 404，则表示该论文尚未在 hf.co/papers 上被索引。有关信息，请参阅 [错误处理](#error-handling)。

或者，你可以从正常的论文页面 URL 请求 markdown，如下所示：

```bash
curl -s -H "Accept: text/markdown" "https://huggingface.co/papers/{PAPER_ID}"
```

### 论文页面 API 端点

所有端点都使用基础 URL `https://huggingface.co`。

#### 获取结构化元数据

使用 Hugging Face REST API 按 JSON 格式获取论文元数据：

```bash
curl -s "https://huggingface.co/api/papers/{PAPER_ID}"
```

这返回结构化的元数据，可以包括：

- 作者（姓名和 Hugging Face 用户名，如果他们已经声明了论文）
- 媒体 URL（提交论文到 Daily Papers 时上传的）
- 摘要和 AI 生成的摘要
- 项目页面和 Github 仓库
- 组织和参与元数据（点赞数）

要查找与论文链接的模型，请使用：

```bash
curl https://huggingface.co/api/models?filter=arxiv:{PAPER_ID}
```

要查找与论文链接的数据集，请使用：

```bash
curl https://huggingface.co/api/datasets?filter=arxiv:{PAPER_ID}
```

要查找与论文链接的 Space，请使用：

```bash
curl https://huggingface.co/api/spaces?filter=arxiv:{PAPER_ID}
```

#### 声明论文作者身份

为 Hugging Face 用户声明论文作者身份：

```bash
curl "https://huggingface.co/api/settings/papers/claim" \
  --request POST \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer $HF_TOKEN" \
  --data '{
    "paperId": "{PAPER_ID}",
    "claimAuthorId": "{AUTHOR_ENTRY_ID}",
    "targetUserId": "{USER_ID}"
  }'
```

- 端点：`POST /api/settings/papers/claim`
- 请求体：
  - `paperId` (字符串，必需)：被声明的 arXiv 论文标识符
  - `claimAuthorId` (字符串)：被声明的论文上的作者条目，24 位十六进制 ID
  - `targetUserId` (字符串)：应收到声明的 HF 用户，24 位十六进制 ID
- 响应：论文作者身份声明结果，包括被声明的论文 ID

#### 获取每日论文

获取 Daily Papers 汇报：

```bash
curl -s -H "Authorization: Bearer $HF_TOKEN" \
  "https://huggingface.co/api/daily_papers?p=0&limit=20&date=2017-07-21&sort=publishedAt"
```

- 端点：`GET /api/daily_papers`
- 查询参数：
  - `p` (整数)：页码
  - `limit` (整数)：结果数量，介于 1 和 100 之间
  - `date` (字符串)：RFC 3339 完整日期，例如 `2017-07-21`
  - `week` (字符串)：ISO 周期，例如 `2024-W03`
  - `month` (字符串)：月份值，例如 `2024-01`
  - `submitter` (字符串)：按提交者筛选
  - `sort` (枚举)：`publishedAt` 或 `trending`
- 响应：每日论文列表

#### 列出论文

按发布日期排序列出 arXiv 论文：

```bash
curl -s -H "Authorization: Bearer $HF_TOKEN" \
  "https://huggingface.co/api/papers?cursor={CURSOR}&limit=20"
```

- 端点：`GET /api/papers`
- 查询参数：
  - `cursor` (字符串)：分页游标
  - `limit` (整数)：结果数量，介于 1 和 100 之间
- 响应：论文列表

#### 搜索论文

对论文执行混合语义和全文搜索：

```bash
curl -s -H "Authorization: Bearer $HF_TOKEN" \
  "https://huggingface.co/api/papers/search?q=vision+language&limit=20"
```

这会在论文标题、作者和内容中进行搜索。

- 端点：`GET /api/papers/search`
- 查询参数：
  - `q` (字符串)：搜索查询，最大长度 250
  - `limit` (整数)：结果数量，介于 1 和 120 之间
- 响应：匹配的论文

#### 索引论文

通过 ID 从 arXiv 插入论文。如果论文已经被索引，只有其作者才能重新索引它：

```bash
curl "https://huggingface.co/api/papers/index" \
  --request POST \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer $HF_TOKEN" \
  --data '{
    "arxivId": "{ARXIV_ID}"
  }'
```

- 端点：`POST /api/papers/index`
- 请求体：
  - `arxivId` (字符串，必需)：要索引的 arXiv ID，例如 `2301.00001`
- 模式：`^\d{4}\.\d{4,5}$`
- 响应：成功时返回空 JSON 对象

#### 更新论文链接

更新论文的项目页面、Github 仓库或提交组织。请求者必须是论文作者、每日论文提交者或论文管理员：

```bash
curl "https://huggingface.co/api/papers/{PAPER_OBJECT_ID}/links" \
  --request POST \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer $HF_TOKEN" \
  --data '{
    "projectPage": "https://example.com",
    "githubRepo": "https://github.com/org/repo",
    "organizationId": "{ORGANIZATION_ID}"
  }'
```

- 端点：`POST /api/papers/{paperId}/links`
- 路径参数：
  - `paperId` (字符串，必需)：Hugging Face 论文对象 ID
- 请求体：
  - `githubRepo` (字符串，可选)：Github 仓库 URL
  - `organizationId` (字符串，可选)：组织 ID，24 位十六进制 ID
  - `projectPage` (字符串，可选)：项目页面 URL
- 响应：成功时返回空 JSON 对象

## 错误处理

- 在 `https://huggingface.co/papers/{PAPER_ID}` 或 `md` 端点上出现 404：该论文尚未在 Hugging Face 论文页面上被索引。
- 在 `/api/papers/{PAPER_ID}` 上出现 404：该论文可能尚未在 Hugging Face 论文页面上被索引。
- 论文 ID 未找到：验证提取的 arXiv ID，包括任何版本后缀

### 回退

如果 Hugging Face 论文页面不包含足够的信息来回答用户的问题：

- 检查常规论文页面 `https://huggingface.co/papers/{PAPER_ID}`
- 回退到原始来源的 arXiv 页面或 PDF：
  - `https://arxiv.org/abs/{PAPER_ID}`
  - `https://arxiv.org/pdf/{PAPER_ID}`

## 注意事项

- 公共论文页面不需要身份验证。
- 声明作者身份、索引论文和更新论文链接等端点需要 `Authorization: Bearer $HF_TOKEN`。
- 优先选择 `.md` 端点以获得可靠的机器可读输出。
- 当你需要结构化的 JSON 字段而不是页面 markdown 时，优先选择 `/api/papers/{PAPER_ID}`。
