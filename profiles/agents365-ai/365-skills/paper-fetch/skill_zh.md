# paper-fetch

给定一个DOI（或标题），获取该论文的PDF。按优先级顺序尝试多个来源，并在第一个命中时停止。

## 解析顺序

1. **Unpaywall** — `https://api.unpaywall.org/v2/{doi}?email=$UNPAYWALL_EMAIL`，读取 `best_oa_location.url_for_pdf`（如果未设置 `UNPAYWALL_EMAIL` 则跳过）
2. **Semantic Scholar** — `https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=openAccessPdf,externalIds`
3. **arXiv** — 如果存在 `externalIds.ArXiv`，`https://arxiv.org/pdf/{arxiv_id}.pdf`
4. **PubMed Central OA** — 如果存在 PMCID，`https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/`
5. **bioRxiv / medRxiv** — 如果 DOI 前缀是 `10.1101`，查询 `https://api.biorxiv.org/details/{server}/{doi}` 获取最新版本 PDF URL
6. **出版社直接** *(仅限机构模式 — `PAPER_FETCH_INSTITUTIONAL=1`)* — DOI 前缀 → 出版社 PDF 模板（Nature / Science / Wiley / Springer / ACS / PNAS / NEJM / Sage / T&F / Elsevier）。调用者的订阅 IP / cookies / EZproxy 用于授权获取；未授权的响应会失败 `%PDF` 检查并跳转到步骤 7。
7. **Sci-Hub 镜像** *(默认开启；使用 `PAPER_FETCH_NO_SCIHUB=1` 禁用)* — 最后手段回退。按顺序尝试 `PAPER_FETCH_SCIHUB_MIRRORS` 中的镜像列表（或内置默认镜像 `sci-hub.ru`、`sci-hub.st`、`sci-hub.su`、`sci-hub.box`、`sci-hub.red`、`sci-hub.al`、`sci-hub.mk`、`sci-hub.ee`）；如果完全失败，则每次进程仅抓取一次 `https://www.sci-hub.pub/` 获取新鲜镜像。CAPTCHA / 缺失论文页面没有 PDF iframe 并静默跳过。
8. 其他情况 → 报告失败并附带标题/作者，以便用户通过 ILL 请求

**CloakBrowser 回退（下载层，可选 — `PAPER_FETCH_CLOAK=1`）。** 这不是一个独立的来源：它位于下载瓶颈处，因此适用于上述所有来源。当解析的 PDF URL 被 Cloudflare 阻止时 — HTTP 403/429，或文件位置处提供“请稍候…”的 HTML 插入页面 — 并且操作员已选择启用，URL 会通过 [CloakBrowser](https://github.com/CloakHQ/CloakBrowser)（一个隐身 Chromium，可通过 JS 挑战）重试（通过 `cloak_pdf.py` 伴侣）。返回的字节会通过相同的 `%PDF` 魔术字节 + 50 MB 检查进行重新验证；成功时结果会携带 `via: "cloak"`。默认关闭，失败时静默回退（缺少 CloakBrowser → 静默回退），代理无法自行选择启用 — 见下文 *CloakBrowser 访问*。

如果只给定标题，直接通过 `--title "<title>"` 传递。解析链：

1. **Crossref** `query.title` — 主要；涵盖所有主要期刊/会议 DOI
2. **Semantic Scholar `/paper/search/match`** — 当 Crossref 的最佳匹配置信度低 (`match_score < 40`) 或与第二名之间的差距 `< 3` 时作为回退。关键的是 S2 涵盖仅 arXiv 预印本（没有 Crossref DOI）。当 S2 揭示只有 arXiv ID 的论文时，会合成规范 `10.48550/arXiv.<id>`，以保持下载链的一致性。
3. **Crossref 的最佳猜测（低置信度）** — 仅在两个解析器都遇到困难时使用。结果包会设置 `meta.title_resolution.low_confidence: true` 加上 `low_confidence_reason` (`score_below_threshold` / `ambiguous_runner_up`)，以便代理可以放弃或通过 `--dry-run` 确认。

无论如何，解析的 DOI、获胜的解析器、完整的 `resolvers_tried` 列表以及顶级候选匹配都会在 `meta.title_resolution` 下显示。

**如果 `semanticscholar-skill` 已注册**，它可以作为标题 → DOI 解析的更丰富的预步骤 — 当您还需要相关性排名、片段搜索或引用上下文时，而不仅仅是 DOI。代理会使用技能的 `match_title()` 编写一个 Python 脚本来读取 `externalIds.DOI`，然后运行 `paper-fetch <doi>`。当结果只有 `ArXiv` ID（没有 DOI）时，会合成 `10.48550/arXiv.<ArXiv>` 并传递给 paper-fetch。

当只需要 DOI 时，`--title` 是单命令路径 — paper-fetch 的内置 Crossref → S2 链处理大多数情况。

## 使用方法

```bash
python scripts/fetch.py <DOI> [options]
python scripts/fetch.py --title "<paper title>" [options]
python scripts/fetch.py --batch <FILE|-> [options]
python scripts/fetch.py schema           # 机器可读的自我描述
```

### 标志

下面是代理在正常使用中组合的标志。要获取完整合同 — 包括 `--dry-run`、`--pretty`、`--stream`、`--overwrite`、`--timeout`、`--version`，以及参数类型和退出码映射 — 运行 `python scripts/fetch.py schema`（机器可读，通过 `schema_version` 进行漂移检查）。

| 标志 | 默认 | 描述 |
| ------ | --------- | ------------- |
| `doi` | — | 要获取的 DOI（位置参数）。使用 `-` 从标准输入读取单个 DOI |
| `--title TITLE` | — | 论文标题；通过 Crossref 解析为 DOI，然后下载。与位置参数 DOI / `--batch` 互斥 |
| `--batch FILE` | — | 包含每行一个 DOI 的文件，用于批量下载。使用 `-` 从标准输入读取 |
| `--out DIR` | `pdfs` | 输出目录 |
| `--format` | auto | `json` 用于代理，`text` 用于人类。自动检测：`json` 当 stdout 不是一个 TTY 时，`text` 当它是时 |
| `--idempotency-key KEY` | — | 安全重试密钥。使用相同的密钥重新运行会从 `<out>/.paper-fetch-idem/` 重放原始包，而无需网络 I/O |

### 代理发现：`schema` 子命令

```bash
python scripts/fetch.py schema
```

向 stdout 发射 CLI 的完整机器可读描述（无需网络）。包括 `cli_version`、`schema_version`、参数类型、退出码、错误码、包形状和环境变量。代理应该只读取一次，针对 `schema_version` 缓存，并在缓存的版本漂移时重新读取。

### 输出合同

**stdout** 发射一个 JSON 包。每个包都携带一个 `meta` 字段。

**成功**（所有 DOI 解析）：

```json
{
  "ok": true,
  "data": {
    "results": [
      {
        "doi": "10.1038/s41586-021-03819-2",
        "success": true,
        "source": "unpaywall",
        "pdf_url": "https://www.nature.com/articles/s41586-021-03819-2.pdf",
        "file": "pdfs/Jumper_2021_Highly_accurate_protein_structure_predic.pdf",
        "meta": {"title": "Highly accurate protein structure prediction with AlphaFold", "year": 2021, "author": "Jumper"},
        "sources_tried": ["unpaywall"]
      }
    ],
    "summary": {"total": 1, "succeeded": 1, "failed": 0},
    "next": []
  },
  "meta": {
    "request_id": "req_a908f5156fc1",
    "latency_ms": 2036,
    "schema_version": "1.9.0",
    "cli_version": "0.13.1",
    "sources_tried": ["unpaywall"]
  }
}
```

**部分**（批量模式 — 一些 DOI 失败，退出码反映失败类别）：

```json
{
  "ok": "partial",
  "data": {
    "results": [
      { "doi": "10.1038/s41586-021-03819-2", "success": true, "source": "unpaywall", ... },
      {
        "doi": "10.1234/nonexistent",
        "success": false,
        "source": null,
        "pdf_url": null,
        "file": null,
        "meta": {},
        "sources_tried": ["unpaywall", "semantic_scholar"],
        "error": {
          "code": "not_found",
          "message": "No open-access PDF found",
          "retryable": true,
          "retry_after_hours": 168,
          "reason": "OA availability changes over time; retry after embargo lifts or preprint appears"
        }
      }
    ],
    "summary": {"total": 2, "succeeded": 1, "failed": 1},
    "next": ["paper-fetch 10.1234/nonexistent --out pdfs"]
  },
  "meta": { ... }
}
```

`next` 字段是一个建议的后续命令数组：重新调用它们会重试失败的子集。结合 `--idempotency-key` 可以安全地重试整个批量，而无需重新下载已成功的项。

**失败**（参数错误，退出码 3）：

```json
{
  "ok": false,
  "error": {
    "code": "validation_error",
    "message": "Provide a DOI or --batch file",
    "retryable": false
  },
  "meta": { ... }
}
```

**单个项跳过**（目标已存在，没有 `--overwrite`）：

```json
{
  "doi": "10.1038/s41586-021-03819-2",
  "success": true,
  "source": "unpaywall",
  "pdf_url": "https://...",
  "file": "pdfs/Jumper_2021_...pdf",
  "skipped": true,
  "skip_reason": "file_exists",
  "sources_tried": ["unpaywall"]
}
```

**幂等重放**（使用相同的 `--idempotency-key` 重新运行）：

缓存的包会原样返回，但 `meta.request_id` 和 `meta.latency_ms` 会为当前调用重新标记，并且 `meta.replayed_from_idempotency_key` 会被设置。不会发生网络 I/O。

### 错误进度（NDJSON）

当 `--format json` 时，stderr 每行发射一个 JSON 对象以显示活动状态：

```
{"event": "session",     "request_id": "req_...", "elapsed_ms": 0,    "cli_version": "0.13.1", "schema_version": "1.9.0"}
{"event": "start",       "request_id": "req_...", "elapsed_ms": 2,    "doi": "10.1038/..."}
{"event": "source_try",  "request_id": "req_...", "elapsed_ms": 2,    "doi": "...", "source": "unpaywall"}
{"event": "source_hit",  "request_id": "req_...", "elapsed_ms": 2036, "doi": "...", "source": "unpaywall", "pdf_url": "..."}
{"event": "download_ok", "request_id": "req_...", "elapsed_ms": 4120, "doi": "...", "file": "..."}
```

事件类型：`session`、`start`、`source_try`、`source_hit`、`source_miss`、`source_skip`、`source_enrich`、`source_enrich_failed`、`download_ok`、`download_error`、`download_skip`、`dry_run`、`not_found`、`resolve_error`。所有事件共享 `request_id` 和 `elapsed_ms`，允许编排器跨 stderr 和最终 stdout 包关联进度。`session` 事件在每个调用中只触发一次，在任何 DOI 工作或网络 I/O 之前，并携带 `cli_version` / `schema_version`，以便代理可以在缓存副本上检测到架构漂移，而无需等待最终包。

`source_enrich` 在调用 Semantic Scholar 仅为填充缺失的 `author` / `title` 后触发，另一个来源已经提供 PDF URL；其 `fields` 数组列出了确切的已填充字段。`source_enrich_failed` 在该增强调用失败时触发 — Unpaywall PDF URL 仍然使用，文件名回退到 `unknown_<year>_…`。

当 `--format text` 时，stderr 发射人类可读的文本。

### 退出码

| 代码 | 含义 | 可重试类别 |
| ------ | --------- | ----------------- |
| `0` | 所有 DOI 解析 / 预览 | — |
| `1` | 未解析 — 一个或多个 DOI 没有开放获取副本；没有传输失败 | 不现在（在 `retry_after_hours` 后重试） |
| `2` | 为 auth 错误保留（目前未使用） | — |
| `3` | 验证错误（参数错误，缺少输入） | 否 |
| `4` | 传输错误（网络 / 下载 / IO 失败） | 是 |

分类允许编排器确定性路由失败：退出 4 值得立即重试，退出 1 不值得，退出 3 是调用者的错误。

### JSON 中的错误码

每个可重试错误都在错误对象中携带 `retry_after_hours` 提示，以便编排器可以安排重试，而无需猜测。

| 代码 | 含义 | 可重试 | `retry_after_hours` |
| ------ | --------- | ----------- | --------------------- |
| `validation_error` | 参数错误或空输入 | 否 | — |
| `title_resolve_failed` | Crossref 返回给定 `--title` 查询的项为空（尝试更长 / 更干净的标题，或直接传递 DOI） | 否 | — |
| `not_found` | 未找到开放获取 PDF | 是 | `168`（一周 — OA 在禁令 / 预印本时间尺度上出现） |
| `resolve_network_error` | 元数据解析器因传输错误（超时 / 5xx / 403）失败；OA 可用性未知 — 重试而不是视为 `not_found`。映射到退出 `4`。 | 是 | `1` |
| `download_network_error` | 下载期间网络失败 | 是 | `1` |
| `download_not_a_pdf` | 响应不是 PDF（HTML 登录页面） | 否 | — |
| `download_host_not_allowed` | PDF URL 失败 SSRF 安全检查（私有 IP / 非 http(s) / 非 80,443 / 被阻止的元数据主机 / 域名解析到私有空间 / 不安全的重定向跳转） | 否 | — |
| `download_size_exceeded` | 响应超过 50 MB 限制 | 是 | `24` |
| `download_io_error` | 本地文件系统写入失败 | 是 | `1` |
| `internal_error` | 预期之外的错误 | 否 | — |

规范映射存在于 `scripts/fetch.py` 中的 `RETRY_AFTER_HOURS` 中，并在 `schema.error_codes` 中显示。

### 示例

```bash
# 单个 DOI（管道时为 JSON；终端时为文本）
python scripts/fetch.py 10.1038/s41586-020-2649-2

# 单个标题（通过 Crossref 解析为 DOI，然后下载）
python scripts/fetch.py --title "Highly accurate protein structure prediction with AlphaFold"

# 干预预览（解析而不下载）
python scripts/fetch.py 10.1038/s41586-020-2649-2 --dry-run

# 标题 + 干预 — 预览解析的 DOI 和候选匹配
python scripts/fetch.py --title "Attention Is All You Need" --dry-run

# 强制 JSON（即使在终端内也用于代理）
python scripts/fetch.py 10.1038/s41586-020-2649-2 --format json

# 人类可读，带颜色管道
python scripts/fetch.py 10.1038/s41586-020-2649-2 --format text

# 批量下载，安全可重试
python scripts/fetch.py --batch dois.txt --out ./papers \
    --idempotency-key monday-review-batch

# 从其他工具管道 DOI
zot -F ids.json query ... | jq -r '.[].doi' | python scripts/fetch.py --batch -

# 代理发现
python scripts/fetch.py schema --pretty

# 流式模式 — 每个DOI解析一个结果，每行一个
python scripts/fetch.py --batch dois.txt --stream

# 无需 UNPAYWALL_EMAIL 即可工作（跳过 Unpaywall，使用剩余 4 个来源）
python scripts/fetch.py 10.1038/s41586-020-2649-2
```

## 环境

| 变量 | 默认 | 目的 |
| --- | --- | --- |
| `UNPAYWALL_EMAIL` | 未设置 | Unpaywall API 的联系邮箱。可选但推荐。没有它，Unpaywall 会跳过（剩余来源仍然工作）。 |
| `PAPER_FETCH_INSTITUTIONAL` | 未设置 | 设置为任何值（例如 `1`）以选择启用 **机构模式** — 激活 1 req/s 速率限制器和出版社直接回退。见下文。 |
| `PAPER_FETCH_NO_SCIHUB` | 未设置 | 设置为任何值以禁用 Sci-Hub 回退（步骤 7）。 |
| `PAPER_FETCH_SCIHUB_MIRRORS` | 未设置 | 优先顺序尝试的逗号分隔镜像主机名（例如 `sci-hub.ru,sci-hub.st,sci-hub.su`）。覆盖内置默认值。 |
| `PAPER_FETCH_CLOAK` | 未设置 | 设置为任何值以启用 **CloakBrowser 回退** — Cloudflare 阻止的 PDF（HTTP 403/429 或非 PDF 插入页面）通过隐身 Chromium 重试。见下文 *CloakBrowser 访问*。 |
| `CLOAKBROWSER_PYTHON` | auto | 可以 `import cloakbrowser` 的 Python 路径，用于 cloak 回退。自动检测顺序：此变量 → `~/github/CloakBrowser/.venv/bin/python` → 当前解释器。 |
| `PAPER_FETCH_CLOAK_HEADED` | 未设置 | 设置为任何值以启动 **带窗口** 的浏览器而不是无头浏览器。更难的 Cloudflare 挑战（例如 `science.org`）击败无头模式，并且只有在真实窗口中才能清除 — 设置此选项时 cloak 回退会返回 HTTP 403 / "请稍候…"。需要显示器。 |

## CloakBrowser 访问（可选）

一些出版社（例如 `science.org`）位于 Cloudflare 后面，Cloudflare 会用 `403`/`429` 或一个“请稍候…”的 JS 挑战页面来响应纯 HTTP 客户端，而不是 PDF — 因此默认的 `urllib` 下载即使在 URL 确实可以从浏览器访问时也无法通过。[CloakBrowser](https://github.com/CloakHQ/CloakBrowser) 是一个隐身 Chromium，可以通过这些挑战。此技能借鉴了 `cloakFetch` 的方法。

**选择启用：** `export PAPER_FETCH_CLOAK=1`（加上一个可导入 `cloakbrowser` 的 Python — 见 `CLOAKBROWSER_PYTHON`）。

**工作原理：** 回退位于 **下载层**，而不是作为新来源 — 因此它适用于任何解析的 URL（Unpaywall、出版社直接、Sci-Hub、…）。在 Cloudflare 阻止时，`fetch.py` 通过解析的 Python 将 `cloak_pdf.py` 伴侣外壳到 `fetch()`。CloakBrowser 加载 PDF 主机的 origin 以解决 JS 挑战，然后使用页面内的 `fetch()` 获取 PDF（因此请求携带浏览器的真实指纹和 `cf_clearance` cookie），并将字节返回到 stdout。`fetch.py` 本身保持 stdlib 仅 — 它从不导入 `cloakbrowser`。

**无头与带窗口。** 伴侣默认以无头方式运行。一些挑战（例如 `science.org`）击败无头 Chromium 并停留在“请稍候…” — 设置 `PAPER_FETCH_CLOAK_HEADED=1` 以使用可见窗口，这可以清除它们。验证：一个 `www.science.org/doi/pdf/…` PDF 对纯客户端返回 403 会通过带窗口的 cloak 回退干净下载。

**仅同源。** 在页内 fetch 是同源的，因此回退在解析的 URL 是被阻止主机上的直接 PDF 链接时（例如 `www.science.org/doi/pdf/…`）起作用。一个跨源重定向的 URL（例如裸 `doi.org/…` 链接）或一个挑战永远不会清除的旧主机将失败并回退到下一个来源。

**保持不变：**

- 返回的字节会通过相同的 `%PDF` 魔术字节 + 50 MB 检查进行重新验证。SSRF 防御在浏览器启动之前会阻止 URL。
- **不解决 CAPTCHA。** CloakBrowser 通过自动 JS 挑战，而不是交互式挑战；交互式 Turnstile 仍然失败并回退。
- **失败时静默。** 没有 `cloakbrowser` 可导入的 Python、助手缺失或任何错误 → 静默回退到下一个来源。代理永远不会被告知被阻止的获取成功。
- 代理不能自行选择启用 — `PAPER_FETCH_CLOAK` 必须由操作员在 shell 环境中设置。与机构模式的信任边界相同。
- 成功时每个结果对象会携带 `via: "cloak"`，以便编排器可以看到回退已被使用。

**成本：** 触发回退会启动一个真实浏览器（~20–40 s，第一次下载 ~200 MB Chromium）。它只在正常下载被阻止后才会触发，因此快乐路径不受影响。

## 机构访问（可选）

许多研究人员通过他们所在机构的 IP 范围（校园内或 VPN）拥有合法的订阅访问权限。Paper-fetch 可以通过允许出版社自己的 auth（您的 IP、您的会话 cookies）来决定是否提供 PDF 使用该访问权限。

主机可达性在两种模式之间没有区别 — 公共模式已经信任 OA API（Unpaywall、Semantic Scholar、bioRxiv、PMC）返回的 URL，并获取任何通过 SSRF 防御的 HTTPS 主机。机构模式添加了两个东西：（1）一个 **出版社直接回退**（上述步骤 6）在所有 OA 来源都失败时构造 DOI 前缀的出版社侧 PDF URL，以便您的机构 IP/cookies 可以授权获取，以及（2）一个 **1 req/s 速率限制器** 以防止批量作业因“系统化下载”而被您的 IP 限速或禁止。

**选择启用：** `export PAPER_FETCH_INSTITUTIONAL=1`

**机构模式下变化：**

| 方面 | 公共（默认） | 机构 |
| --- | --- | --- |
| 主机可达性 | 任何通过 SSRF 防御的公共 HTTPS 主机 | 相同 |
| SSRF 防御 | 强制执行（私有 IP / 非 http(s) / 非 80,443 / 云元数据全部被阻止） | 强制执行 — 相同规则 |
| 出版社直接回退 | 关闭 | 开启 — DOI 前缀 → 出版社 PDF URL，所有 OA 来源失败后的最后手段 |
| 速率限制 | 无 | 1 req/s 令牌桶（所有出站） |
| `meta.auth_mode` | `"public"` | `"institutional"` |

**保持不变：**

- `%PDF` 魔术字节检查和 50 MB 大小限制（防止 HTML 登录页面和超大小响应滑过）
- 从不解决 CAPTCHA，永远。如果出版社显示挑战，响应不会以 `%PDF` 开头，paper-fetch 会回退到下一个来源。
- 机构模式本身不使用浏览器自动化，不使用 Playwright，不使用隐身 — 它是对出版社直接 URL 的普通 HTTP 获取。浏览器自动化是 *单独的* 可选：上述 CloakBrowser 回退，由 `PAPER_FETCH_CLOAK` 控制。 |
- 代理不能自行选择启用 — `PAPER_FETCH_INSTITUTIONAL` 必须由操作员在 shell 环境中设置。这是信任边界。

**当 paper-fetch 无法找到 OA 副本并且您处于公共模式时**，错误包会包括 `suggest_institutional: true` 和一个提示用户设置环境变量的信息。代理可以原样显示而不是静默失败。

**ToS 通知：** 几乎每个出版社订阅都禁止“系统化下载”。1 req/s 速率限制加上现有的每个文件的幂等性旨在将单个研究使用保持在可接受的范围内。运行许多并行 paper-fetch 进程，或提高速率限制，可能会触发影响您整个机构的出版社级 IP 禁止。不要这样做。

## 注意事项

- **授权是委托的。** 代理不会运行登录子命令。人或编排器在环境中设置 `UNPAYWALL_EMAIL`；代理继承它。缺少邮箱会优雅地降级到剩余的 4 个来源。
- **信任是单向的。** CLI 参数在入口点验证一次。SSRF 防御、`%PDF` 魔术字节检查和 50 MB 大小限制在环境层强制执行，而不是在代理请求中。代理不能通过传递标志来降低安全性 — 选择启用机构模式（及其速率限制风险配置文件）是操作员通过环境变量执行的操作。
- **下载是天生幂等的。** 重新运行针对相同的 `--out` 会跳过已存在的文件（确定性文件名：`{first_author}_{year}_{journal_abbrev}_{short_title}.pdf`；如果元数据缺少期刊/会议，则省略期刊部分）。与 `--idempotency-key` 配合使用以重新播放确切的包而无需任何网络 I/O。
- **默认输出目录：** `./pdfs/`.
