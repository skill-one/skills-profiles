# Bright Data — 爬取

通过 Bright Data CLI 从一个或多个 URL 获取干净的内容（markdown、HTML、JSON、截图）。这项技能拥有“获取原始或轻度结构化内容”的任务。对于平台特定的结构化数据（亚马逊、领英、抖音等），**停止并使用 `data-feeds`** —— 你将获得干净的 JSON 而无需选择器逻辑。

## 设置网关（首先运行）

在进行任何爬取之前，验证 CLI 是否已安装并认证：

```bash
if ! command -v bdata >/dev/null 2>&1; then
    echo "bdata CLI 未安装 — 请参阅 bright-data-best-practices/references/cli-setup.md"
elif ! bdata zones >/dev/null 2>&1; then
    echo "bdata 未认证 — 运行: bdata login  (或: bdata login --device 用于 SSH)"
fi
```

如果任何检查失败，停止并引导用户到 `skills/bright-data-best-practices/references/cli-setup.md`。不要在静默模式下尝试遗留的 `curl` 降级方案 —— 先询问用户。

## 选择你的路径

| 情况 | 操作 |
|---|---|
| 单个 URL | `bdata scrape <url> -f markdown` |
| 小列表（≤ ~20 个 URL） | shell 循环，一次一个（见 `references/patterns.md`） |
| 较大的列表（几十个以上） | 使用并行限制的 `xargs -P 4`（见 `references/patterns.md`） |
| 分页列表 | 爬取第 1 页 → 提取下一页 URL → 追加 → 重复（见 `references/examples.md`） |
| JS 重度 / 登录受保护 / 需要交互 | 升级到 `bdata browser`（见 `brightdata-cli` 技能） |
| 亚马逊、领英、抖音、Instagram、YouTube、Reddit、… | **停止 — 交由 `data-feeds` 处理** |
| 尚无 URL，仅是主题 | **交由 `search` 处理** |

## 操作

核心命令：

```bash
# 清理 markdown（默认）
bdata scrape "https://example.com/article" -f markdown -o article.md

# 原始 HTML（当你需要 DOM 时）
bdata scrape "https://example.com" -f html -o page.html

# 结构化 JSON（当解锁器返回解析字段时）
bdata scrape "https://example.com" -f json --pretty -o page.json

# 视觉快照（保存 PNG）
bdata scrape "https://example.com" -f screenshot -o page.png

# 地区定向（覆盖退出国家）
bdata scrape "https://example.com" --country de -f markdown

```

完整标志参考：[`references/flags.md`](references/flags.md)。

## 验证网关（成功前运行）

1. **非空输出：** `test -s "$out_path"` — 或者，对于标准输出，至少 200 字节的内容。
2. **不是拦截页面** — 在输出中搜索以下任何签名（不区分大小写）：
   - `Access Denied`
   - `Just a moment`
   - `Attention Required`
   - `Checking your browser`
   - `captcha`
   - `cf-browser-verification`
   - `cloudflare` *(总正文 < 2KB)*
3. **任务预期的标记存在**：例如，产品页面应包含价格模式（`\$\d`）；文章应至少包含一个 `<h1>` 或 `# ` 标题。
4. **失败时的升级步骤：**
   - 使用不同的 `--country` 重试（例如，如果原始站点是美国的 `--country de`）
   - 升级到 `bdata browser` 进行完整 JS 渲染（交由 `brightdata-cli` 技能处理）

在所有检查通过之前不要报告成功。

## 警示标志

- 在未检查输出的情况下声称成功。
- 使用 `2>/dev/null` 静默处理错误 —— 你会错过认证失败和速率限制错误。
- 在亚马逊/领英/抖音/Instagram/YouTube/Reddit URL 上运行 `bdata scrape` —— 这些由 `data-feeds` 支持，并直接返回结构化数据。爬取会丢失结构。
- 在同一任务中重复爬取相同的 URL —— 缓存第一个结果。
- 使用 `bdata scrape` 顺序循环大型列表，而不是使用 `xargs -P 4`（或类似）与并行限制（见 `references/patterns.md`）。
- 直接对 `api.brightdata.com` 使用 `curl` —— 遗留路径；仅在 CLI 不可用时使用。

## 参考

- [`references/flags.md`](references/flags.md) — 每个标志的何时使用说明。
- [`references/patterns.md`](references/patterns.md) — shell-loop 批量处理、`xargs` 并行、分页配方、重试/退避、拦截页面恢复链、遗留 `curl` 降级。
- [`references/examples.md`](references/examples.md) — (1) 单页 → markdown， (2) 带并行限制批量 URL 列表， (3) 分页列表， (4) 拦截页面恢复。
