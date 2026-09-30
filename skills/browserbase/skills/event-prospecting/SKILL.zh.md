---
name: event-prospecting
description: '事件开发技能。输入一个会议/活动演讲者URL，提取人员信息，根据用户的ICP（行业分类）筛选其公司，然后深入调研ICP匹配公司的演讲者。输出以人为中心的HTML报告，每张卡片回答“为什么AE（客户经理）应该与这个人交谈？”并提供所有公开链接和一键私信开启器。


  使用场景：

  (1) 在特定会议上寻找潜在客户；

  (2) 为活动做准备；

  (3) 调研活动演讲者；

  (4) 从赞助商/参展商页面构建目标名单；

  (5) 抓取会议演讲者并按ICP匹配度排序。


  触发词：

  "在{会议}中寻找潜在客户"、"调研{会议}演讲者"、"开发这个会议"、"stripe会议潜在客户"、"AI工程师峰会潜在客户"、"事件开发"、"抓取会议演讲者"、"我应该与谁会面"。'
---

# 事件潜在客户开发

输入会议网址 → 获取一份按排名排列的潜在客户列表，每人附有“为何联系”的理由。

**要求**：`BROWSERBASE_API_KEY` 环境变量和已安装的 `browse` CLI (`npm install -g browse`)。使用 `browse cloud ...` 进行 API 调用，使用 `browse open` / `browse get markdown` 处理 JS 重的演讲者页面。

**路径规则**：所有 Bash 命令中始终使用完整的字面路径——不要使用 `~` 或 `$HOME`（两者都会触发“shell 扩展语法”批准提示）。一次性解析家目录并到处使用。构建子代理提示时，将 `{SKILL_DIR}` 替换为完整的字面路径（通常为 `/Users/jay/skills/skills/event-prospecting`）。

**输出目录**：所有事件潜在客户开发输出都存放在 `~/Desktop/{event_slug}_prospects_{YYYY-MM-DD-HHMM}/`。最终交付物是 `index.html`（按公司分组、按公司 ICP 排名），以及 `companies.html` 和 `people.html`（可过滤）作为备用视图，以及 `results.csv` 用于冷触达导入。

**关键——工具限制（适用于主代理和所有子代理）**：
- 所有网络搜索：使用 `browse cloud search`。绝对不要使用 WebSearch。
- 所有页面内容提取：使用 `node {SKILL_DIR}/scripts/extract_page.mjs "<url>"`。此脚本通过 `browse cloud fetch --output` 获取，解析标题 + 元标签 + 可见正文文本，并在获取失败或返回瘦 JS 渲染内容时自动回退到 `browse get markdown`。绝对不要手动编写 `browse cloud fetch | sed` 管道。绝对不要使用 WebFetch。
- 所有研究输出：子代理为每个公司或每人编写**一个 markdown 文件**到 `{OUTPUT_DIR}/companies/{slug}.md` 或 `{OUTPUT_DIR}/people/{slug}.md`，使用 bash heredoc。绝对不要使用 Write 工具或 `python3 -c`。参考 `references/example-research.md` 获取两种文件格式。
- 报告编译：使用 `node {SKILL_DIR}/scripts/compile_report.mjs {OUTPUT_DIR} --open`。
- **子代理必须仅使用 Bash 工具。不允许使用其他工具。**
- **硬工具调用限制**：ICP 筛选 = 每公司 1 次调用；深度研究 = 每公司 5 次调用；人员丰富 = 每人 4 次调用。参考 `references/workflow.md` 获取执行细节。

**关键——防止幻觉规则（适用于主代理和所有子代理）**：
- 绝对不要从网站的字体、框架、设计系统或排版中推断 `product_description`、`industry` 或人员的 `role_reason`。这些是装饰性的，并不能说明公司销售什么或人员做什么。
- 绝对不要让用户的 ICP 泄露到目标的描述中。如果你不知道目标做什么，请写 `Unknown`——不要将他们与 ICP 模式匹配。
- `product_description` 必须引用或转述 `extract_page.mjs` 输出中的特定短语。如果标题/META/OG/HEADINGS/BODY 没有产生可识别的产品声明，请写 `Unknown — 主页内容无法访问`，并将 `icp_fit_score` 限制在 3。
- 人员的 `hook` 必须引用或转述 `browse cloud search` 结果中的特定发现（播客标题、博客标题、GitHub 仓库、演讲摘要）。如果过去 6 个月内没有公共信号，则回退到事件上下文（他们在此次会议的演讲标题）。

**关键——最小化权限提示**：
- 子代理必须将所有文件写入批处理到单个 Bash 调用中，使用链接的 heredoc。一个 Bash 调用 = 一个权限提示。
- 将所有搜索和所有获取批处理到单个 Bash 调用中，使用 `&&` 链接。

## 管道概述

按顺序执行以下 10 个步骤。不要跳过步骤或重新排序。

0. **设置** — 输出目录 + 清理空白页
1. **加载配置文件** — 读取 `profiles/{user_slug}.json`
2. **侦察** — 检测事件平台
3. **提取人员** — `people.jsonl`
4. **按公司分组** — `seed_companies.txt`
5. **ICP 筛选** — 快速公司级评分（每公司 1 次调用）
6. **过滤** — ICP-fit_score >= --icp-threshold 的公司
7. **深度研究** — 在 ICP 匹配公司上进行 Plan→研究→综合
8. **丰富演讲者** — 询问用户：仅 ICP 匹配（默认）或所有演讲者
9. **编译报告** — HTML + CSV，在浏览器中打开

用户使用类似 `/event-prospecting <URL>` 的 URL 调用技能。从该调用消息中解析 `EVENT_URL`。默认值：`DEPTH=deep`，`ICP_THRESHOLD=6`。`USER_SLUG`（ICP 配置文件）在步骤 1 中自动解析为本地存在的任何配置文件——没有内置默认配置文件。不要要求用户确认 URL——他们已经给了你。

---

## 步骤 0：设置输出目录

从用户给您的 URL 推导输出目录。不要硬编码任何事件名称。

```bash
# EVENT_URL 来自调用消息（用户在 /event-prospecting 后输入的任何内容）
EVENT_SLUG=$(node -e 'const h = new URL(process.argv[1]).hostname.replace(/^www\./,""); console.log(h.split(".")[0])' "$EVENT_URL")
TIMESTAMP=$(date +%Y-%m-%d-%H%M)
OUTPUT_DIR=/Users/jay/Desktop/${EVENT_SLUG}_prospects_${TIMESTAMP}
mkdir -p "$OUTPUT_DIR/companies" "$OUTPUT_DIR/people"
```

使用完整的字面家路径——永远不要 `~` 或 `$HOME`。将 `{OUTPUT_DIR}` 作为完整的字面路径传递给所有子代理提示。

## 步骤 1：加载用户配置文件

配置文件定义了 ICP，ICP 筛选和深度研究将对其进行评分。从 `{SKILL_DIR}/profiles/{user_slug}.json` 加载（在所有 GTM 技能中可互换——形状与公司研究相同）。`example.json` 是一个模板，不是真实的配置文件——永远不要使用它。

**不要在 `{SKILL_DIR}/profiles/` 外查找配置文件**——永远不要深入其他技能的目录。如果需要在其他地方使用配置文件，用户显式复制它。

**解析顺序**：
1. 如果用户使用 `--user-company <slug>` 调用，则使用该 slug。
2. 否则，列出 `profiles/*.json`（排除 `example.json`）。如果只有一个配置文件存在，则使用它（并告诉用户是哪个）。如果有多个，请用户（纯聊天）选择哪个。
3. 如果没有配置文件存在，**大声失败**并指示用户创建一个（将 `profiles/example.json` 复制到 `profiles/<your_slug>.json` 并填写它，或运行公司研究技能自动构建一个）。

```bash
PROFILES=$(ls {SKILL_DIR}/profiles/*.json 2>/dev/null | xargs -n1 basename | sed 's/\.json$//' | grep -v '^example$')
COUNT=$(echo "$PROFILES" | grep -c .)

if [ -z "$USER_SLUG" ]; then
  if [ "$COUNT" -eq 0 ]; then
    echo "未在 {SKILL_DIR}/profiles/ 中找到配置文件。复制 profiles/example.json 到 profiles/<your_slug>.json 并填写它，或运行公司研究技能自动构建一个。"
    exit 1
  elif [ "$COUNT" -eq 1 ]; then
    USER_SLUG=$PROFILES
    echo "使用唯一可用的配置文件：${USER_SLUG}"
  else
    echo "找到多个配置文件："
    echo "$PROFILES" | sed 's/^/  - /'
    echo "重新调用时使用 --user-company <slug> 选择一个。"
    exit 1
  fi
fi

test -f {SKILL_DIR}/profiles/${USER_SLUG}.json || {
  echo "找不到配置文件：profiles/${USER_SLUG}.json"
  exit 1
}
cat {SKILL_DIR}/profiles/${USER_SLUG}.json
```

配置文件提供：`company`、`product`、`icp_description`、`existing_customers`。这些将原封不动地嵌入到下游每个子代理提示中。

## 步骤 2：侦察

检测事件平台和提取策略。一个命令：

```bash
node {SKILL_DIR}/scripts/recon.mjs {EVENT_URL} {OUTPUT_DIR}
```

写入 `{OUTPUT_DIR}/recon.json`，包含 `platform`、`strategy` 和（对于 Next.js）`nextDataPaths`。参考 `references/event-platforms.md` 获取平台目录和检测优先级。

预期结果：
- Stripe Sessions 类（Next.js）：`platform: "next-data"`，1-3 个路径
- Sessionize：`platform: "sessionize"`
- Lu.ma / Eventbrite：`platform: "luma" | "eventbrite"`
- 其他任何内容：`platform: "custom"`，`strategy: "markdown"`（尽力回退）

## 步骤 3：提取人员

```bash
node {SKILL_DIR}/scripts/extract_event.mjs {OUTPUT_DIR} --user-company {USER_SLUG}
```

读取 `recon.json`，分发到平台特定的提取器，写入 `people.jsonl`（每行一个演讲者）和 `seed_companies.txt`（去重公司）。

`--user-company` 标志还会从演讲者列表中删除主机组织的员工（Stripe 主办的事件会删除 Stripe 员工）和用户的员工——他们不是潜在客户。

检查输出：
```bash
wc -l {OUTPUT_DIR}/people.jsonl {OUTPUT_DIR}/seed_companies.txt
head -3 {OUTPUT_DIR}/people.jsonl
```

如果 `people.jsonl` 为空或少于 ~10 行，侦察选择了错误平台——参考 `references/event-platforms.md` 并使用调整后的策略重新运行。

## 步骤 4：按公司分组

`extract_event.mjs` 已经发出 `seed_companies.txt`（每行一个公司，去重，排序）。此步骤是信息性的——在扩展之前验证计数是否合理：

```bash
wc -l {OUTPUT_DIR}/seed_companies.txt
```

预期：演讲者数量的 0.4-0.6 倍（大多数活动平均每个公司有 2 名演讲者，一些公司发送 5+，许多公司发送 1）。

## 步骤 5：ICP 筛选

**快速通道——每个公司一次工具调用，无需深度研究。** 对 `seed_companies.txt` 中的每个公司进行用户 ICP 评分，并写入一个薄的筛选草稿到 `companies/{slug}.md`。ICP-fit_score >= --icp-threshold（默认 6）的公司将进入步骤 7 的深度研究；其余的将作为筛选草稿保留。

**分发模式**：将 `seed_companies.txt` 分批为 ~10 批，并在单个 Agent 批次中扩展 N 个子代理（一条消息中的多个 Agent 工具调用）。每个子代理运行来自 `references/workflow.md` → "ICP 筛选" 部分的提示。硬限制：**每个公司 1 次工具调用**（仅对主页执行 `extract_page.mjs`），通过 `# browse call N/1` 注释模式强制执行。

```bash
# 构建 batch 文件：每个 batch 行是 "name|guessed_homepage|slug"。
# extract_event.mjs 仅发出公司名称（没有 URL），因此我们 slugify 并猜测
# https://{slug-without-spaces}.com 作为规范主页。筛选子代理
# 允许写 product_description: "Unknown — 主页内容无法访问"，如果猜测的 URL 404，将分数限制在 3——
# 这是在 workflow.md 中定义的 ICP 筛选提示的规则 3。使用真实的 browse cloud search 发现 URL
# 会破坏每公司 1 次调用的硬限制。
node -e '
const fs = require("fs");
const slugify = (s) => (s || "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
const seed = fs.readFileSync("{OUTPUT_DIR}/seed_companies.txt", "utf-8").split("\n").filter(Boolean);
const lines = seed.map(c => {
  const slug = slugify(c);
  const guessedHost = c.toLowerCase().replace(/[^a-z0-9]/g, "");
  return `${c}|https://${guessedHost}.com|${slug}`;
});
fs.writeFileSync("{OUTPUT_DIR}/_seed_with_urls.txt", lines.join("\n") + "\n");
'

# 分批为 ~10 个公司
split -l 10 {OUTPUT_DIR}/_seed_with_urls.txt {OUTPUT_DIR}/_batch_triage_

# 计算批次数量 → 要分发的子代理数量（最多每条消息 6 个；第二波用于剩余的）
ls {OUTPUT_DIR}/_batch_triage_* | wc -l
```

然后在一条消息中，为每个批次分发一个 Agent 调用（最多并行 6 个；第一波返回后的第二波）。每个 Agent 获取来自 `references/workflow.md` → "ICP 筛选" 的提示，并在发送前进行以下替换：
- `{SKILL_DIR}` → 完整的字面技能路径（例如 `/Users/jay/skills/skills/event-prospecting`）
- `{OUTPUT_DIR}` → 完整的字面输出路径
- `{USER_COMPANY}`、`{USER_PRODUCT}`、`{ICP_DESCRIPTION}` → 从加载的配置文件
- `{EVENT_NAME}`（来自 `recon.json` `.title`）、`{EVENT_CONTEXT}`（跟踪 / 主题，从事件主页手动推断）
- `{COMPANY_LIST}` → 批次文件的内容（例如 `cat {OUTPUT_DIR}/_batch_triage_aa`）
- `{TOTAL}` → 此批次中的行数（替换到 `# browse call N/{TOTAL}`）

**Agent 分发（骨架，在一个消息中重复每个批次）**：

```
Agent(
  description: "ICP 筛选批次 aa",
  prompt: <来自 workflow.md 的 ICP 筛选提示模板，所有占位符替换>,
  subagent_type: "general-purpose"
)
Agent(
  description: "ICP 筛选批次 ab",
  prompt: <相同的提示模板，COMPANY_LIST 替换为批次 ab>,
  subagent_type: "general-purpose"
)
... 最多每条消息 6 个
```

所有子代理返回后，验证 `seed_companies.txt` 中的每个公司都有一个对应的 `companies/{slug}.md`：

```bash
ls {OUTPUT_DIR}/companies/*.md | wc -l
# 应该等于 `wc -l {OUTPUT_DIR}/seed_companies.txt`
```

清理批处理文件：`rm {OUTPUT_DIR}/_batch_triage_*`。

## 步骤 6：按 ICP 阈值过滤

读取每个 `companies/*.md` 的 frontmatter，保留 `icp_fit_score >= 6`（或 whatever `--icp-threshold` 是）。将幸存的公司 slugs 写入 `{OUTPUT_DIR}/icp_fits.txt`：

```bash
THRESHOLD=6   # 来自 --icp-threshold 标志
for f in {OUTPUT_DIR}/companies/*.md; do
  score=$(awk '/^icp_fit_score:/{print $2; exit}' "$f")
  if [ -n "$score" ] && [ "$score" -ge "$THRESHOLD" ]; then
    basename "$f" .md
  fi
done > {OUTPUT_DIR}/icp_fits.txt

wc -l {OUTPUT_DIR}/icp_fits.txt
```

预期：`seed_companies.txt` 的 20-40%。如果存活率 < 10%，阈值可能太高或 ICP 描述太窄——向用户显示警告。

## 步骤 7：深度研究

仅对 ICP 匹配公司进行 Plan→研究→综合。硬限制：**每公司 5 次工具调用**（主页提取 + 2-3 个子问题搜索 + 1-2 个补充获取）。子代理用更丰富的深度研究版本**覆盖**现有的 `companies/{slug}.md` 筛选草稿（frontmatter `triage_only: false`）。

**分发模式**：将 `icp_fits.txt` 分批为 ~5 批（深度模式默认），并在一条消息中分发一个 Agent 每个批次（最多并行 6 个 Agent；第一波返回后的第二波）。每个 Agent 获取来自 `references/workflow.md` → "深度研究" 的提示，并进行以下替换：
- `{SKILL_DIR}`、`{OUTPUT_DIR}`、`{USER_COMPANY}`、`{USER_PRODUCT}`、`{ICP_DESCRIPTION}`
- `{EVENT_NAME}`（来自 `recon.json` `.title`）、`{EVENT_CONTEXT}`（跟踪 / 主题，从事件主页手动推断）
- `{COMPANY_LIST}` → 批次文件的内容（每行 `slug|website`）

```bash
# 构建 {company-slug|website} 对，通过读取每个筛选草稿的 frontmatter
while read slug; do
  website=$(awk '/^website:/{print $2; exit}' {OUTPUT_DIR}/companies/${slug}.md)
  echo "${slug}|${website}"
done < {OUTPUT_DIR}/icp_fits.txt > {OUTPUT_DIR}/_deep_targets.txt

# 分批为 ~5 个公司（深度模式）
split -l 5 {OUTPUT_DIR}/_deep_targets.txt {OUTPUT_DIR}/_batch_deep_
ls {OUTPUT_DIR}/_batch_deep_* | wc -l
```

**Agent 分发（骨架，在一个消息中重复每个批次）**：

```
Agent(
  description: "深度研究批次 aa",
  prompt: <来自 workflow.md 的深度研究提示模板，所有占位符替换；COMPANY_LIST = cat _batch_deep_aa>,
  subagent_type: "general-purpose"
)
Agent(
  description: "深度研究批次 ab",
  prompt: <相同的模板，COMPANY_LIST = cat _batch_deep_ab>,
  subagent_type: "general-purpose"
)
... 最多每条消息 6 个；第一波返回后的第二波
```

所有子代理返回后，验证深度研究文件是否存在并具有 `triage_only: false`：

```bash
grep -l "triage_only: false" {OUTPUT_DIR}/companies/*.md | wc -l
# 应该等于 wc -l icp_fits.txt
```

## 步骤 8：丰富演讲者

每人：收集 LinkedIn URL、近期活动（播客 / 博客 / 演讲 / GitHub / X），并写入 `people/{slug}.md`。硬限制：**每人 4 次工具调用**，三个通道：

1. `browse cloud search "{name} {company} linkedin"`（始终）
2. `browse cloud search "{name} podcast OR talk OR blog 2026"`（深度+）
3. `browse cloud search "{name} github"`（更深）
4. `browse cloud search "{name} site:x.com OR site:twitter.com"`（更深，尽力而为）

快速模式：完全跳过步骤 8。深度模式：通道 1-2。更深模式：通道 1-4。

### 步骤 8a — 询问用户：丰富范围

在分发之前，计算两个候选数量并要求用户选择。默认值是**仅 ICP 匹配**（更快、更便宜、大多数用户想要的）；丰富每个演讲者是可选的，因为成本随丰富人数线性增长。

```bash
TOTAL=$(wc -l < {OUTPUT_DIR}/people.jsonl)
ICP_FITS=$(node -e '
const fs = require("fs");
const fits = new Set(fs.readFileSync("{OUTPUT_DIR}/icp_fits.txt", "utf-8").split("\n").filter(Boolean));
const slug2name = {};
for (const slug of fits) {
  const md = fs.readFileSync(`{OUTPUT_DIR}/companies/${slug}.md`, "utf-8");
  const m = md.match(/^company_name:\s*(.+)$/m);
  if (m) slug2name[slug] = m[1].trim();
}
const want = new Set(Object.values(slug2name).map(s => s.toLowerCase()));
const ppl = fs.readFileSync("{OUTPUT_DIR}/people.jsonl","utf-8").split("\n").filter(Boolean).map(JSON.parse);
console.log(ppl.filter(p => p.company && want.has(p.company.toLowerCase())).length);
')

# 每人通道数：2（较深）或 4（更深）— 匹配 {DEPTH}
LANES=2   # 或 4 用于更深
echo "ICP 匹配：${ICP_FITS} 位发言人 × ${LANES} = $((ICP_FITS * LANES)) 个通话"
echo "全部：      ${TOTAL} 位发言人 × ${LANES} = $((TOTAL * LANES)) 个通话"
```

然后通过 `AskUserQuestion` — 清晰的两选项选择，每个选项附带量化成本：

```
AskUserQuestion(questions: [
  {
    question: "要丰富哪些发言人？",
    header: "丰富范围",
    multiSelect: false,
    options: [
      { label: "仅 ICP 匹配", description: "${ICP_FITS} 位发言人，~$((ICP_FITS * LANES)) 个通话（推荐）" },
      { label: "所有发言人", description: "${TOTAL} 位发言人，~$((TOTAL * LANES)) 个通话" }
    ]
  }
])
```

将选择的范围保存为 `ENRICH_SCOPE=icp_fits` 或 `ENRICH_SCOPE=all`。如果用户选择 "所有发言人" 且 `TOTAL × LANES > 600`，则打印警告并再次询问——这将是一个 10 分钟以上的运行，涉及数百个工具调用。

### 第 8b 步 — 筛选和批量

```bash
# 根据 ENRICH_SCOPE 构建 _people_to_enrich.jsonl
if [ "$ENRICH_SCOPE" = "all" ]; then
  cp {OUTPUT_DIR}/people.jsonl {OUTPUT_DIR}/_people_to_enrich.jsonl
else
  node -e '
const fs = require("fs");
const fits = new Set(fs.readFileSync("{OUTPUT_DIR}/icp_fits.txt", "utf-8").split("\n").filter(Boolean));
const slug2name = {};
for (const slug of fits) {
  const md = fs.readFileSync(`{OUTPUT_DIR}/companies/${slug}.md`, "utf-8");
  const m = md.match(/^company_name:\s*(.+)$/m);
  if (m) slug2name[slug] = m[1].trim();
}
const wantNames = new Set(Object.values(slug2name).map(s => s.toLowerCase()));
const lines = fs.readFileSync("{OUTPUT_DIR}/people.jsonl", "utf-8").split("\n").filter(Boolean);
const keep = lines.filter(l => {
  const p = JSON.parse(l);
  return p.company && wantNames.has(p.company.toLowerCase());
});
fs.writeFileSync("{OUTPUT_DIR}/_people_to_enrich.jsonl", keep.join("\n") + "\n");
console.error(`丰富 ${keep.length} 位发言人中的 ${lines.length} 位`);
'
fi

# 分成约 5 人一批
split -l 5 {OUTPUT_DIR}/_people_to_enrich.jsonl {OUTPUT_DIR}/_batch_people_
```

然后在一条消息中，为每个批次（最多 6 个）发送一个 Agent 调用，使用 `references/workflow.md` 中的提示 → "Person 丰富"。每个子 Agent 的提示应包括：
- `{SKILL_DIR}`, `{OUTPUT_DIR}`, `{DEPTH}` (`deep` | `deeper`)
- `{USER_COMPANY}`, `{USER_PRODUCT}`, `{ICP_DESCRIPTION}`
- `{EVENT_NAME}`（来自 `recon.json` 的 `.title`）
- `{LANES}` → `2` 用于 deep 模式，`4` 用于 deeper 模式（替换到 `# browse call N/{LANES}`）
- `{PEOPLE_BATCH}` → `_batch_people_aa` 的内容（每行是 `people.jsonl` 的 JSON 记录）

**Agent 调用（骨架，每个批次在一条消息中重复）**：

```
Agent(
  description: "Person 丰富批次 aa",
  prompt: <Person 丰富提示，来自 workflow.md，所有占位符替换；PEOPLE_BATCH = cat _batch_people_aa>,
  subagent_type: "general-purpose"
)
Agent(
  description: "Person 丰富批次 ab",
  prompt: <相同模板，PEOPLE_BATCH = cat _batch_people_ab>,
  subagent_type: "general-purpose"
)
... 最多每条消息 6 个
```

所有子 Agent 返回后，验证人员文件是否存在：

```bash
ls {OUTPUT_DIR}/people/*.md | wc -l
# 应等于 wc -l _people_to_enrich.jsonl
```

## 第 9 步：编译报告

使用一条命令生成按公司分组、交替视图和 CSV：

```bash
node {SKILL_DIR}/scripts/compile_report.mjs {OUTPUT_DIR} --open
```

这将生成：
- `{OUTPUT_DIR}/index.html` — 按公司分组的人员，按公司 ICP 分数排序（在浏览器中打开）
- `{OUTPUT_DIR}/people.html` — 可筛选的发言人列表（交替视图）
- `{OUTPUT_DIR}/companies.html` — ICP 排序的公司表，包含参会者
- `{OUTPUT_DIR}/results.csv` — 可用于冷外呼的电子表格

然后以摘要形式在聊天中呈现：

```
## 活动潜在客户完成 — {Event Name}

- **提取的总发言人数**：{count}
- **唯一公司数**：{count}
- **ICP 匹配（分数 ≥ {threshold}）**：{count}
- **丰富发言人数**：{count}
- **分数分布**（公司）：
  - 强匹配（8-10）：{count}
  - 部分匹配（5-7）：{count}
  - 弱匹配（1-4）：{count}
- **浏览器中打开的报告**：{OUTPUT_DIR}/index.html
```

以 Markdown 表格形式显示**前 5 张人员卡片**，按公司 ICP 分数排序，并提供以下选项：
- 调整 `--icp-threshold` 并重新运行步骤 6-9
- 将 CSV 导出到 CRM
