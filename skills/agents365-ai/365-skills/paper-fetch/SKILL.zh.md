---
name: paper-fetch
description: 在用户希望获取、下载或获取论文的PDF时使用——根据DOI、arXiv ID、论文标题、引用信息或DOI列表。在类似“下载这篇论文”、“查找[DOI]的PDF”、“获取关于X的[Nature/bioRxiv/arXiv]论文”、“获取开放获取版本”、“我需要这篇文章”或任何批量/批量论文下载请求时触发，即使用户没有明确说“PDF”或“DOI”。通过Unpaywall → Semantic Scholar → arXiv → PubMed Central → bioRxiv/medRxiv → 出版社直接（机构选择加入）→ Sci-Hub镜像作为最后的备用方案解决。
---

# paper-fetch

给定一个DOI（或标题），获取论文的PDF。按优先级顺序尝试多个来源，并在第一个命中时停止。

## 解析顺序

1. **Unpaywall** — `https://api.unpaywall.org/v2/{doi}?email=$UNPAYWALL_EMAIL`，读取 `best_oa_location.url_for_pdf`（如果未设置 `UNPAYWALL_EMAIL` 则跳过）
2. **Semantic Scholar** — `https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=openAccessPdf,externalIds`
3. **arXiv** — 如果存在 `externalIds.ArXiv`，`https://arxiv.org/pdf/{arxiv_id}.pdf`
4. **PubMed Central OA** — 如果存在 PMCID，`https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/`
5. **bioRxiv / medRxiv** — 如果 DOI 前缀是 `10.1101`，查询 `https://api.biorxiv.org/details/{server}/{doi}` 获取最新版本 PDF URL
6. **出版社直接** *(仅限机构模式 — `PAPER_FETCH_INSTITUTIONAL=1`)* — DOI 前缀 → 出版社 PDF 模板（Nature / Science / Wiley / Springer / ACS / PNAS / NEJM / Sage / T&F / Elsevier）。调用者的订阅 IP / cookies / EZproxy 用于授权获取；未授权的响应会失败 `%PDF` 检查并跳转到步骤 7。
7. **Sci-Hub 镜像** *(默认开启；使用 `PAPER_FETCH_NO_SCIHUB=1` 禁用)* — 最后手段回退。按顺序尝试 `PAPER_FETCH_SCIHUB_MIRRORS` 中的镜像列表（或内置默认镜像 `sci-hub.ru`、`sci-hub.st`、`sci-hub.su`、`sci-hub.box`、`sci-hub.red`、`sci-hub.al`、`sci-hub.mk`、`sci-hub.ee`）；完全失败时，每个进程只抓取一次 `https://www.sci-hub.pub/` 获取新鲜镜像。CAPTCHA / 缺失论文页面没有 PDF iframe 并静默跳过。
8. 其他情况 → 报告失败并附带标题/作者，以便用户通过 ILL 请求

**CloakBrowser 回退（下载层，可选 — `PAPER_FETCH_CLOAK=1`）。** 这不是一个独立的来源：它位于下载瓶颈，因此适用于上述所有来源。当解析的 PDF URL 被 Cloudflare 阻挡 — HTTP 403/429，或文件被 "Just a moment…" HTML 插入页面替代时 — 并且操作员已选择启用，URL 会通过 [CloakBrowser](https://github.com/CloakHQ/CloakBrowser)（一个能通过 JS 挑战的隐蔽 Chromium）通过 `cloak_pdf.py` 伴侣重试。它返回的字节会通过相同的 `%PDF` 魔数字节 + 50 MB 检查重新验证；成功时结果会携带 `via: "cloak"`。默认关闭，失败时静默回退（缺少 CloakBrowser → 静默回退），代理无法选择启用 — 见下文 *CloakBrowser 访问*。

如果只给定标题，直接通过 `--title "<title>"` 传递。解析链：

1. **Crossref** `query.title` — 主要；涵盖所有主要期刊/会议 DOI
2. **Semantic Scholar `/paper/search/match`** — 当 Crossref 的最佳匹配置信度低 (`match_score < 40`) 或与第二名差距小于 `< 3` 时回退。关键地，S2 涵盖仅 arXiv 的预印本（没有 Crossref DOI）。当 S2 提交只有 arXiv ID 的论文时，会合成规范 `10.48550/arXiv.<id>`，以保持下载链的一致性。
3. **Crossref 的最佳猜测（低置信度）** — 仅在两个解析器都遇到困难时使用。结果包会设置 `meta.title_resolution.low_confidence: true` 加上 `low_confidence_reason` (`score_below_threshold` / `ambiguous_runner_up`)，以便代理可以放弃或通过 `--dry-run` 确认。

无论如何，解析的 DOI、获胜的解析器、完整的 `resolvers_tried` 列表和顶级候选匹配都会在 `meta.title_resolution` 下显示。

**如果 `semanticscholar-skill` 已注册**，它可以作为更丰富的标题 → DOI 解析预步骤 — 当你还需要相关性排名、片段搜索或引用上下文时，而不仅仅是 DOI。代理使用技能的 `match_title()` 读取 `externalIds.DOI`，然后运行 `paper-fetch <doi>`。当结果只有 `ArXiv` ID（没有 DOI）时，合成 `10.48550/arXiv.<ArXiv>` 并传递给 paper-fetch。

当只需要 DOI 时，`--title` 是单命令路径 — paper-fetch 的内置 Crossref → S2 链处理大多数情况。

## 使用方法

```bash
python scripts/fetch.py <DOI> [options]
python scripts/fetch.py --title "<paper title>" [options]
python scripts/fetch.py --batch <FILE|-> [options]
python scripts/fetch.py schema           # 机器可读的自我描述
```

### 标志

以下是代理在正常使用中组合的标志。要获取完整合同 — 包括 `--dry-run`、`--pretty`、`--stream`、`--overwrite`、`--timeout`、`--version`，以及参数类型和退出码映射 — 运行 `python scripts/fetch.py schema`（机器可读，通过 `schema_version` 检查漂移）。

| 标志 | 默认 | 描述 |
| ------ | --------- | ------------- |
| `doi` | — | 要获取的 DOI（位置参数）。使用 `-` 从 stdin 读取单个 DOI |
| `--title TITLE` | — | 论文标题；通过 Crossref 解析为 DOI 后下载。与位置参数 DOI / `--batch` 互斥 |
| `--batch FILE` | — | 每行一个 DOI 的文件，用于批量下载。使用 `-` 从 stdin 读取 |
| `--out DIR` | `pdfs` | 输出目录 |
| `--format` | auto | `json` 用于代理，`text` 用于人类。自动检测：`json` 当 stdout 不是 TTY 时，`text` 当它是时 |
| `--idempotency-key KEY` | — | 安全重试密钥。使用相同密钥重新运行会重放 `<out>/.paper-fetch-idem/` 中的原始包，无需网络 I/O |

### 代理发现：`schema` 子命令

```bash
python scripts/fetch.py schema
```

在 stdout 发出 CLI 的完整机器可读描述（无网络）。包括 `cli_version`、`schema_version`、参数类型、退出码、错误码、包形状和环境变量。代理应读取一次，针对 `schema_version` 缓存，并在缓存的版本漂移时重新读取。

### 输出合同

**stdout** 发出一个 JSON 包。每个包都带有 `meta` 字段。

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
        "file": "pdfs/Jumper_2021_Highly_accurate_protein_structure_pred.pdf",
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

`next` 字段是一个建议的后续命令数组：重新调用它们会重试失败的子集。结合 `--idempotency-key` 使整个批量安全重试，无需重新下载已成功的项。

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

缓存的包会原样返回，但 `meta.request_id` 和 `meta.latency_ms` 会为当前调用重新标记，`meta.replayed_from_idempotency_key` 会被设置。不会发生网络 I/O。

### Stderr 进度（NDJSON）

当 `--format json` 时，stderr 每行发出一个 JSON 对象以显示活动状态：

```
{"event": "session",     "request_id": "req_...", "elapsed_ms": 0,    "cli_version": "0.13.1", "schema_version": "1.9.0"}
{"event": "start",       "request_id": "req_...", "elapsed_ms": 2,    "doi": "10.1038/..."}
{"event": "source_try",  "request_id": "req_...", "elapsed_ms": 2,    "doi": "...", "source": "unpaywall"}
{"event": "source_hit",  "request_id": "req_...", "elapsed_ms": 2036, "doi": "...", "source": "unpaywall", "pdf_url": "..."}
{"event": "download_ok", "request_id": "req_...", "elapsed_ms": 4120, "doi": "...", "file": "..."}
```

事件类型：`session`、`start`、`source_try`、`source_hit`、`source_miss`、`source_skip`、`source_enrich`、`source_enrich_failed`、`download_ok`、`download_error`、`download_skip`、`dry_run`、`not_found`、`resolve_error`。所有事件共享 `request_id` 和 `elapsed_ms`，让协调器可以跨 stderr 和最终 stdout 包关联进度。`session` 事件在每个调用中只触发一次，在任何 DOI 工作或网络 I/O 之前，并携带 `cli_version` / `schema_version`，以便代理可以在缓存副本上检测 schema 漂移，而无需等待最终包。

`source_enrich` 在 Semantic Scholar 被纯用于在另一个来源已提供 PDF URL 后填充缺失的 `author` / `title` 时触发；其 `fields` 数组列出了确切的已填充字段。`source_enrich_failed` 在该增强调用失败时触发 — Unpaywall PDF URL 仍然使用，文件名回退到 `unknown_<year>_…`。

当 `--format text` 时，stderr 发出人类可读的散文。

### 退出码

| 代码 | 含义 | 可重试类别 |
| ------ | --------- | ----------------- |
| `0` | 所有 DOI 解析 / 预览 | — |
| `1` | 未解析 — 一个或多个 DOI 没有开放获取副本；没有传输失败 | 不现在（等待 `retry_after_hours` 后重试） |
| `2` | 保留用于认证错误（目前未使用） | — |
| `3` | 验证错误（参数错误，输入缺失） | 否 |
| `4` | 传输错误（网络 / 下载 / IO 失败） | 是 |

分类允许协调器确定性地路由失败：退出 4 值得立即重试，退出 1 不值得，退出 3 是调用者的错误。

### JSON 中的错误码

每个可重试错误都带有 `retry_after_hours` 提示，以便协调器可以安排重试，而无需猜测。

| 代码 | 含义 | 可重试 | `retry_after_hours` |
| ------ | --------- | ----------- | --------------------- |
| `validation_error` | 参数错误或空输入 | 否 | — |
| `title_resolve_failed` | Crossref 对给定的 `--title` 查询返回了无项（尝试更长 / 更干净的标题，或直接传递 DOI） | 否 | — |
| `not_found` | 未找到开放获取 PDF | 是 | `168`（一周 — OA 在禁令 / 预印本时间尺度上出现） |
| `resolve_network_error` | 元数据解析器因传输错误（超时 / 5xx / 403）失败；OA 可用性未知 — 重试而不是视为 `not_found`。映射到退出 `4`。 | 是 | `1` |
| `download_network_error` | 下载期间网络失败 | 是 | `1` |
| `download_not_a_pdf` | 响应不是 PDF（HTML 登录页面） | 否 | — |
| `download_host_not_allowed` | PDF URL 失败 SSRF 安全检查（私有 IP / 非 http(s) / 非 80,443 / 被阻挡的元数据主机 / 域名解析到私有空间 / 不安全的重定向跳转） | 否 | — |
| `download_size_exceeded` | 响应超过 50 MB 限制 | 是 | `24` |
| `download_io_error` | 本地文件系统写入失败 | 是 | `1` |
| `internal_error` | 未预期的错误 | 否 | — |

规范映射存在于 `scripts/fetch.py` 中的 `RETRY_AFTER_HOURS`，并在 `schema.error_codes` 中显示。

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

# 强制 JSON（即使在终端内为代理）
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

# 流式模式 — 每个解析的 DOI 每行一个结果
python scripts/fetch.py --batch dois.txt --stream

# 无需 UNPAYWALL_EMAIL（跳过 Unpaywall，使用剩余 4 个来源）
python scripts/fetch.py 10.1038/s41586-020-2649-2
```

## 环境

| 变量 | 默认 | 目的 |
| --- | --- | --- |
| `UNPAYWALL_EMAIL` | unset | Unpaywall API 的联系邮箱。可选但推荐。没有它，会跳过 Unpaywall（剩余来源仍然工作）。 |
| `PAPER_FETCH_INSTITUTIONAL` | unset | 设置任何值（例如 `1`）以选择启用 **机构模式** — 激活 1 req/s 速率限制器和出版社直接回退。见下文。 |
| `PAPER_FETCH_NO_SCIHUB` | unset | 设置任何值以禁用 Sci-Hub 回退（步骤 7）。 |
| `PAPER_FETCH_SCIHUB_MIRRORS` | unset | 优先顺序尝试的逗号分隔镜像主机名（例如 `sci-hub.ru,sci-hub.st,sci-hub.su`）。覆盖内置默认值。 |
| `PAPER_FETCH_CLOAK` | unset | 设置任何值以启用 **CloakBrowser 回退** — Cloudflare 阻挡的 PDF（HTTP 403/429 或非 PDF 插入页面）通过隐蔽 Chromium 重试。见下文 *CloakBrowser 访问*。 |
| `CLOAKBROWSER_PYTHON` | auto | 可以 `import cloakbrowser` 的 Python 路径，用于 cloak 回退。自动检测顺序：此变量 → `~/github/CloakBrowser/.venv/bin/python` → 当前解释器。 |
| `PAPER_FETCH_CLOAK_HEADED` | unset | 设置任何值以启动一个 **带 GUI**（可见）浏览器而不是无头模式。更难的 Cloudflare 挑战（例如 `science.org`）击败无头模式，并且只在真实窗口中清除 — 设置此选项时 cloak 回退持续返回 HTTP 403 / "Just a moment…"。需要显示器。 |

## CloakBrowser 访问（可选）

一些出版社（例如 `science.org`）位于 Cloudflare 后面，Cloudflare 对纯 HTTP 客户端回答 `403`/`429` 或一个 "Just a moment…" JS 挑战页面，而不是 PDF — 所以默认的 `urllib` 下载即使在 URL 从浏览器中可以合法访问时也无法通过。[CloakBrowser](https://github.com/CloakHQ/CloakBrowser) 是一个能通过这些挑战的隐蔽 Chromium。这项技能借鉴了 `cloakFetch` 的方法。

**选择启用**：`export PAPER_FETCH_CLOAK=1`（加上一个 `cloakbrowser`-可导入的 Python — 见 `CLOAKBROWSER_PYTHON`）。

**工作原理：** 降级方案位于**下载层**，并非作为新的来源——因此它适用于任何解析后的URL（Unpaywall、出版社直连、Sci-Hub等）。在Cloudflare封锁的情况下，`fetch.py`通过解析后的Python调用`cloak_pdf.py`这个辅助程序；CloakBrowser加载PDF主机的原点以解决JS挑战，然后使用页面内的**`fetch()`**（因此请求携带了浏览器的真实指纹和`cf_clearance` cookie）获取PDF，并将字节输出到stdout。`fetch.py`本身仅使用标准库——它从不导入`cloakbrowser`。

**无头模式与有头模式。** 辅助程序默认以无头模式运行。某些挑战（例如`science.org`）会击败无头Chromium并卡在“请稍候…”状态——设置`PAPER_FETCH_CLOAK_HEADED=1`以使用可见窗口，这可以清除它们。已验证：一个返回403给普通客户端的`www.science.org/doi/pdf/…` PDF可以通过有头模式的降级方案干净下载。

**仅同源。** 页面内fetch是同源的，因此当解析后的URL是封锁主机上的直接PDF链接（例如`www.science.org/doi/pdf/…`）时，降级方案可以生效。一个跨源重定向的URL（例如一个裸的`doi.org/…`链接）或一个挑战永远无法清除的旧主机将关闭失败并传递到下一个来源。

**保持不变的内容：**

- 返回的字节通过相同的`%PDF`魔数字节检查和50 MB大小上限进行重新验证。SSRF防御在浏览器启动之前就封锁了URL。
- **不解决CAPTCHA。** CloakBrowser通过自动JS挑战，而不是交互式挑战；交互式Turnstile仍然关闭失败并传递。
- **关闭失败。** 没有`cloakbrowser`可导入的Python、辅助程序缺失或任何错误→静默传递到下一个来源。代理永远不会被告知封锁的获取成功。
- 代理不能自行选择加入——`PAPER_FETCH_CLOAK`必须由人工操作员在shell环境中设置。与机构模式具有相同的信任边界。
- 成功时，每个结果对象携带`via: "cloak"`，以便协调器可以看到降级方案被使用。

**成本：** 触发降级方案会启动一个真实浏览器（约20-40秒，首次下载时~200 MB Chromium）。它只在正常下载被封锁后才启动，因此快乐路径不受影响。

## 机构访问（选择加入）

许多研究人员通过其机构的IP范围（校园内或VPN）拥有合法的订阅访问权限。Paper-fetch可以通过让出版社自身的认证（您的IP、您的会话cookie）决定是否提供PDF来使用该访问权限。

主机可达性在模式之间没有区别——公共模式已经信任OA API返回的URL（Unpaywall、Semantic Scholar、bioRxiv、PMC），并获取任何通过SSRF防御的HTTPS主机。机构模式增加了两项内容：（1）一个**出版社直连降级方案**（上述步骤6）在所有OA来源都失败时，通过DOI前缀构造出版社侧PDF URL，以便您的机构IP/cookies可以授权获取，以及（2）一个**每秒1个请求的速率限制器**以防止批量作业因“系统化下载”而被您的IP限速或封禁。

**选择加入：** `export PAPER_FETCH_INSTITUTIONAL=1`

**机构模式下变化的内容：**

| 方面 | 公共（默认） | 机构 |
| --- | --- | --- |
| 主机可达性 | 任何通过SSRF防御的公共HTTPS主机 | 相同 |
| SSRF防御 | 强制执行（私有IP / 非http(s) / 非80,443 / 云元数据全部封锁） | 强制执行——相同规则 |
| 出版社直连降级方案 | 关闭 | 开启——DOI前缀→出版社PDF URL，所有OA来源都失败后的最后手段 |
| 速率限制 | 无 | 每秒1个请求的令牌桶（所有出站） |
| `meta.auth_mode` | `"public"` | `"institutional"` |

**保持不变的内容：**

- `%PDF`魔数字节检查和50 MB大小上限（防止HTML着陆页和过大的响应滑入）
- 永远不解决CAPTCHA。如果出版社显示挑战，响应将不会以`%PDF`开头，paper-fetch会传递到下一个来源。
- 机构模式本身不使用浏览器自动化，不使用Playwright，不使用隐身——它是对出版社直连URL的普通HTTP获取。（浏览器自动化是一个*单独*的选择加入：上述CloakBrowser降级方案，由`PAPER_FETCH_CLOAK`控制。）
- 代理不能自行选择加入——`PAPER_FETCH_INSTITUTIONAL`必须由人工操作员在shell环境中设置。这是信任边界。

**当paper-fetch找不到OA副本且您处于公共模式时**，错误包中包含`suggest_institutional: true`以及提示用户设置环境变量的提示。代理可以原样显示而不是沉默失败。

**服务条款通知：** 几乎所有出版社订阅都禁止“系统化下载”。每秒1个请求的速率限制加上现有的每个文件幂等性旨在将个人研究使用保持在可接受范围内。运行多个并行paper-fetch进程或提高速率限制可能会触发影响整个机构的出版社级IP封禁。不要这样做。

## 注意事项

- **认证是委托的。** 代理永远不会运行登录子命令。人工或协调器在环境中设置`UNPAYWALL_EMAIL`；代理继承它。缺少电子邮件会优雅地降级到剩余的4个来源。
- **信任是单向的。** CLI参数在入口点验证一次。SSRF防御、`%PDF`魔数字节检查和50 MB大小上限在环境层强制执行，而不是在代理的请求中。代理不能通过传递标志来放宽安全性——选择加入机构模式（及其速率限制风险）是操作员通过环境变量执行的操作。
- **下载天生是幂等的。** 对相同的`--out`重新运行会跳过已存在的文件（确定性文件名：`{first_author}_{year}_{journal_abbrev}_{short_title}.pdf`；如果元数据缺少期刊/场所，则省略期刊部分）。与`--idempotency-key`配合使用，以重新播放确切的包而无需任何网络I/O。
- **默认输出目录：** `./pdfs/`。
