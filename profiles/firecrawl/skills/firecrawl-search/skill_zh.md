# firecrawl 搜索

使用用户的实际问题进行自然搜索。默认搜索返回网络结果以及相关的 Alexandria 工具，并可选进行网络内容抓取。

对于结构化记录、可过滤列表、转录内容或数据集，首先检查 `firecrawl search alexandria '<需要的数据>'` 以查找合适的流程或数据提供者。对于已知网站，使用 `firecrawl find-tools <url>`。在通过 `scrape` 执行之前，使用 `firecrawl list <提供者> <功能> --pretty` 检查选定的合约。重用发现过程中已返回的完整合约。如果不存在合适的工具，则继续进行网络搜索或使用 Agent。使用普通 `search` 进行网络研究，使用 URL `scrape` 对已知页面进行抓取。

## 快速入门

```bash
# 基本搜索
firecrawl search "你的查询" -o .firecrawl/result.json --json

# 从结果中搜索并抓取完整页面内容
firecrawl search "你的查询" --scrape -o .firecrawl/scraped.json --json

# 过去一天的新闻
firecrawl search "你的查询" --sources news --tbs qdr:d -o .firecrawl/news.json --json
```

使用 `firecrawl search --help` 获取搜索选项，`firecrawl list --help` 获取合约浏览选项，以及 `firecrawl scrape --help` 获取执行选项。

`--categories developer` 搜索公共存储库索引、GitHub 问题、已合并的拉取请求、存储库 README 和精选文档网站。`--categories research` 是一个网站过滤器，不是论文索引。专用技能：[firecrawl-developer-index](../firecrawl-developer-index/SKILL.md) 和 [firecrawl-research-index](../firecrawl-research-index/SKILL.md)。

**完成时：** 检查了相关结果，检查了每次调用的错误和空结果，使用源链接回答了请求，并在时间窗口内发送了反馈（除非选择退出）。

## 使用 Alexandria 超越页面内容

Alexandria 是一个包含现成网站流程、API 提供者和专业索引的目录。根据工具的不同，它可以返回结构化记录、详细列表、财务数据、公司信息、研究或公共记录，这些内容搜索片段或单个抓取页面不包含。发现当前覆盖范围，而不是假设提供者或功能存在。

- **语义发现** 将用户的查询含义与工具功能相匹配，即使网络结果中没有出现相关的提供者网站。当您需要特定工具时，使用 `firecrawl search alexandria '<需要的数据>'`。
- **域名匹配** 显示与网络结果中网站相关联的工具。匹配的工具可以检索更丰富的细节、相关记录或结构化集合，而不仅仅是链接的页面。域名匹配表示相关性，而不是证明工具涵盖请求的字段或市场。
- **组合搜索** 默认情况下使用网络结果、域名匹配和语义工具：`firecrawl search '<用户问题>'`。当足够时使用网络结果；当它提供更直接的数据路径时，检查匹配的工具。

### 执行前检查

搜索默认为 `web,alexandria` 并开启域名-工具匹配。在查询中保留用户的位置、市场限制；不要将正常研究变成人为的工具发现查询。检查来自同一响应的 `data.web` 和 `data.tools`。

搜索默认返回紧凑的工具匹配：仅 `provider`、`capability` 和 `description`。匹配不是执行数据。选择候选者，然后运行 `firecrawl list <提供者> <功能> --pretty` 并使用其提供者和功能 ID 来读取合约的输入、覆盖范围和访问要求。

使用 `--tool-detail summary --json` 获取发现元数据和导航；在执行前使用 `list` 检查选定的合约。使用 `--tool-detail full --json` 在搜索结果中直接接收合约，而无需另一次检查调用。当需要立即获取多个相关合约时，优先使用完整模式。显示的定价是信息性的，不是额外的确认关卡。

检查合约后，使用 `firecrawl scrape <提供者/功能> --options '<输入 JSON>'` 执行（`--alexandria` 仍然受支持）。所有提供者执行都通过 Scrape；`search --scrape` 仅获取网络结果内容，不包括提供者工具。

使用 `list` 进行类别/提供者浏览和选定合约。对于已知网站，`find-tools <url>` 发现相关联的工具而不执行它们。运行 `firecrawl find-tools --help` 获取高级目录选择器；除非任务需要，否则避免广泛扩展。

如果返回的工具未涵盖国家/市场/细分或所需输入，则继续使用普通网络结果。不要耗尽目录或为探测覆盖范围而支付相邻工具。`--sources web` 明确选择退出 Alexandria；`--sources web --domain-tools` 仅保留域名匹配。

每当您查找或运行 Alexandria 工具时，完成时发送 `firecrawl alexandria feedback`，包括当网站未被覆盖时。它是免费的，在后台运行；模式和规则存在于 [firecrawl-alexandria](../firecrawl-alexandria/SKILL.md)。

## 渐进式发现和输出处理

```bash
# 网络 + 域名匹配 + 语义工具
firecrawl search '<用户问题>'

# 仅语义工具
firecrawl search alexandria '<用户问题>'

# 类别 → 提供者 → 工具 → 合约
firecrawl list
firecrawl list <类别ID> --category
firecrawl list <提供者ID>
firecrawl list <提供者ID> <功能ID> --pretty

# 执行工具
firecrawl scrape <提供者ID>/<功能ID> --options '<与选定合约匹配的 JSON>'
```

默认搜索结合网络结果、域名匹配和语义工具；`search alexandria` 仅返回语义工具匹配。读取选定的合约，而不是扩展整个目录。工具发现不是执行。

将大型搜索响应保存在 `--json -o` 输出中并选择相关结果。如果后续提供者执行或 URL 抓取超过代理的输出限制，使用其保留 ID 与 [远程 Bash 恢复说明](../firecrawl-scrape/references/large-results.md)。搜索请求 ID 不支持 Bash 输入。不要盲目重新运行成功的提供者，因为客户端可能无法显示其结果。

## 小贴士

- **`--highlights` 默认开启：** 结果是页面中与查询相关的摘录。使用 `--no-highlights` 获取原始片段。
- **`--scrape` 抓取完整内容** — 重用该内容而不是重新抓取结果 URL。这节省了积分并避免了重复抓取。
- 对于大型结果，当有可用文件系统时使用 `-o` 和有界本地读取。不要将完整响应转储到上下文中。
- 使用 `jq` 提取 URL 或标题：`jq -r '.data.web[].url' .firecrawl/search.json`
- 命名约定：`.firecrawl/search-{查询}.json` 或 `.firecrawl/search-{查询}-scraped.json`

## 每次搜索后发送反馈（退款 1 积分）

搜索成本 2 积分。在您实际使用结果（或决定它们无用）后，使用 `firecrawl search-feedback <id>` 发送结构化反馈。每次搜索的第一个反馈退款 1 积分并帮助我们提高搜索质量。**每次搜索执行一次**，在您处理结果完成后，在后台执行——它不会阻塞您的主任务。

**选择退出：** 如果 `FIRECRAWL_NO_SEARCH_FEEDBACK=1`（或 `FIRECRAWL_DISABLE_SEARCH_FEEDBACK=1`）被设置，CLI 将静默跳过调用并永远不会发送任何内容。尊重这一点——不要试图绕过它。（团队管理员也可以在服务器端禁用此功能；API 将返回 `feedbackErrorCode: "TEAM_OPTED_OUT"`，CLI 将静默退出 0。）

**调用此功能前需要了解的规则：**

- **时间窗口：** 必须在搜索后约 2 分钟内发送。迟到的反馈将被拒绝。
- **`--missing-content` 是最重要的字段。** 它是您期望但未找到的 _具体内容_ 的列表。每个条目一个主题，每个条目一个字符串。这些内容跨团队汇总，告诉我们下一步要索引什么。
- **需要实质性内容**（零努力反馈将被 HTTP 400 拒绝）：
  - `good` → 必须至少包含一个 `--valuable-sources` 条目。
  - `partial` → 必须包含 `--valuable-sources` 或 `--missing-content`。
  - `bad` → 必须包含 `--missing-content` 或 `--query-suggestions`。
- **每日退款上限（每个团队，每个 UTC 天，默认 100 积分）。** 当您的团队今天已获得 100 积分退款后，进一步的提交仍然记录反馈但不再退款积分。响应包括 `creditsRefundedToday` / `dailyRefundCap` / `dailyCapReached`。**当 `dailyCapReached: true` 时，停止在 UTC 当天剩余时间内调用 `search-feedback`**——它不会退款任何内容，您正在浪费带宽。
- **幂等性：** 重新提交相同的搜索 ID 返回成功但不会额外退款。
- **`--silent &`** 是正确的模式——即使失败也退出代码 0，因此被拒绝/过期的调用永远不会崩溃您的管道。

在读取其 `id` 之前验证搜索返回了结果。零结果搜索不写入输出文件，因此文件可能缺失——或者来自更早的搜索。下面的守卫在文件缺失或结果为零时跳过反馈；仅在它内部调用 `search-feedback`：

```bash
# 每次搜索发送一次。诚实地评级并替换为与实际发生匹配的评级。显示的两个字段满足每个评级的实质性内容规则。
if SEARCH_ID=$(jq -er 'select(any(.data[]; length > 0)) | .id' .firecrawl/search-react-hooks.json); then
  firecrawl search-feedback "$SEARCH_ID" \
    --rating "<good|partial|bad>" \
    --valuable-sources '[{"url":"https://react.dev/reference/react/hooks","reason":"最权威的"}]' \
    --missing-content '[{"topic":"useDeferredValue","description":"没有 Suspense 与 useDeferredValue 的示例"}]' \
    --silent &
fi
```

**`--missing-content` 接受：**

- JSON 数组 `{topic, description?}` 对象（最丰富，首选）
- `"topic: description"` 字符串（简称）
- 纯 `"topic1, topic2, topic3"`（当您只有主题名称时）
- 重复的 `--missing-content` 标志

`--silent` 抑制输出，`&` 在后台运行，因此反馈永远不会阻塞您。

## 参见

- [firecrawl-scrape](../firecrawl-scrape/SKILL.md) — 抓取特定 URL
- [firecrawl-map](../firecrawl-map/SKILL.md) — 发现网站内的 URL
- [firecrawl-crawl](../firecrawl-crawl/SKILL.md) — 从网站批量提取
- [firecrawl-developer-index](../firecrawl-developer-index/SKILL.md) — 问题、已合并的 PR、README 和文档
- [firecrawl-research-index](../firecrawl-research-index/SKILL.md) — 已发表论文，不是 `search --categories research`
- [firecrawl-build-search](https://github.com/firecrawl/skills/tree/main/skills/build/firecrawl-build-search) — 将搜索构建到应用程序中而不是在这里运行
