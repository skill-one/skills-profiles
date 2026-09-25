# Hugging Face 数据集查看器

使用此技能执行只读数据集查看器 API 调用以进行数据集探索和提取。

## 核心工作流程

1. 可选地使用 `/is-valid` 验证数据集可用性。
2. 使用 `/splits` 解析 `config` + `split`。
3. 使用 `/first-rows` 预览。
4. 使用 `/rows` 分页内容，使用 `offset` 和 `length`（最大 100）。
5. 使用 `/search` 进行文本匹配，使用 `/filter` 进行行谓词过滤。
6. 通过 `/parquet` 获取 parquet 链接，通过 `/size` 和 `/statistics` 获取总数/元数据。

## 默认设置

- 基础 URL：`https://datasets-server.huggingface.co`
- 默认 API 方法：`GET`
- 查询参数应进行 URL 编码。
- `offset` 是 0 基的。
- `length` 最大通常是 `100`（对于行类端点）。
- 受限的/私有的数据集需要 `Authorization: Bearer <HF_TOKEN>`。

## 数据集查看器

- `验证数据集`：`/is-valid?dataset=<namespace/repo>`
- `列出子集和分割`：`/splits?dataset=<namespace/repo>`
- `预览前几行`：`/first-rows?dataset=<namespace/repo>&config=<config>&split=<split>`
- `分页行`：`/rows?dataset=<namespace/repo>&config=<config>&split=<split>&offset=<int>&length=<int>`
- `搜索文本`：`/search?dataset=<namespace/repo>&config=<config>&split=<split>&query=<text>&offset=<int>&length=<int>`
- `使用谓词过滤`：`/filter?dataset=<namespace/repo>&config=<config>&split=<split>&where=<predicate>&orderby=<sort>&offset=<int>&length=<int>`
- `列出 parquet 分片`：`/parquet?dataset=<namespace/repo>`
- `获取大小总数`：`/size?dataset=<namespace/repo>`
- `获取列统计信息`：`/statistics?dataset=<namespace/repo>&config=<config>&split=<split>`
- `获取 Croissant 元数据（如果可用）`：`/croissant?dataset=<namespace/repo>`

分页模式：

```bash
curl "https://datasets-server.huggingface.co/rows?dataset=stanfordnlp/imdb&config=plain_text&split=train&offset=0&length=100"
curl "https://datasets-server.huggingface.co/rows?dataset=stanfordnlp/imdb&config=plain_text&split=train&offset=100&length=100"
```

当分页部分时，使用 `num_rows_total`、`num_rows_per_page` 和 `partial` 等响应字段来驱动继续逻辑。

搜索/过滤说明：

- `/search` 匹配字符串列（全文本样式的行为是 API 内部的）。
- `/filter` 要求 `where` 中的谓词语法，`orderby` 中可选排序。
- 保持过滤和搜索只读且无副作用。

对于基于 CLI 的 parquet URL 发现或 SQL，使用 `hf-cli` 技能，并使用 `hf datasets parquet` 和 `hf datasets sql`。

## 创建和上传数据集

根据依赖约束使用其中一种流程。

零本地依赖（Hub UI）：

- 在浏览器中创建数据集仓库：`https://huggingface.co/new-dataset`
- 在仓库的“文件和版本”页面上传 parquet 文件。
- 验证分片是否出现在数据集查看器中：

```bash
curl -s "https://datasets-server.huggingface.co/parquet?dataset=<namespace>/<repo>"
```

低依赖 CLI 流程（`npx @huggingface/hub` / `hfjs`）：

- 设置认证令牌：

```bash
export HF_TOKEN=<your_hf_token>
```

- 上传 parquet 文件夹到数据集仓库（如果缺失则自动创建仓库）：

```bash
npx -y @huggingface/hub upload datasets/<namespace>/<repo> ./local/parquet-folder data
```

- 在创建时上传为私有仓库：

```bash
npx -y @huggingface/hub upload datasets/<namespace>/<repo> ./local/parquet-folder data --private
```

上传后，调用 `/parquet` 以发现 `<config>/<split>/<shard>` 值，用于使用 `@~parquet` 进行查询。

## Agent 追踪

Hub 支持 Claude Code、Codex 和 Pi Agent 的原始 agent 会话追踪。将它们作为原始 JSONL 文件上传到 Hugging Face Datasets，Hub 可以自动检测追踪格式，将数据集标记为 `Traces`，并启用追踪查看器以浏览会话、回合、工具调用和模型响应。常见的本地会话目录：

- Claude Code：`~/.claude/projects`
- Codex：`~/.codex/sessions`
- Pi：`~/.pi/agent/sessions`

默认使用私有数据集仓库，因为追踪可能包含提示、文件路径、工具输出、秘密或 PII。保留原始 `.jsonl` 文件，并按项目/cwd 嵌套它们，而不是在数据集根目录上传每个会话。

```bash
hf repos create <namespace>/<repo> --type dataset --private --exist-ok
hf upload <namespace>/<repo> ~/.codex/sessions codex/<project-or-cwd> --type dataset
```
