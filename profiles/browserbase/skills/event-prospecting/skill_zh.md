# 事件潜在客户开发

输入会议URL → 获取一份按优先级排序的潜在客户名单，每个客户附带“联系理由”。

**必需**：`BROWSERBASE_API_KEY`环境变量和已安装的`browse` CLI (`npm install -g browse`)。使用`browse cloud ...`进行API调用，使用`browse open` / `browse get markdown`处理JS密集型演讲者页面。

**路径规则**：所有Bash命令中始终使用完整字面路径——**不要**使用`~`或`$HOME`（两者都会触发“shell扩展语法”审批提示）。一次性解析家目录并到处使用。在构建子代理提示时，将`{SKILL_DIR}`替换为完整字面路径（通常是`/Users/jay/skills/skills/event-prospecting`）。

**输出目录**：所有事件潜在客户开发输出都存放在`~/Desktop/{event_slug}_prospects_{YYYY-MM-DD-HHMM}/`。最终交付物是`index.html`（按公司分组的人员，按公司ICP排序），以及`companies.html`和`people.html`（可过滤）作为备用视图，以及`results.csv`用于冷触达导入。

**关键——工具限制（适用于主代理和所有子代理）**：
- 所有网络搜索：使用`browse cloud search`。**绝对不要**使用WebSearch。
- 所有页面内容提取：使用`node {SKILL_DIR}/scripts/extract_page.mjs "<url>"`。此脚本通过`browse cloud fetch --output`获取，解析标题+元标签+可见正文文本，并在获取失败或返回瘦JS渲染内容时自动回退到`browse get markdown`。**绝对不要**手动编写`browse cloud fetch | sed`管道。**绝对不要**使用WebFetch。
- 所有研究输出：子代理为每个公司或每个人编写**一个markdown文件**到`{OUTPUT_DIR}/companies/{slug}.md`或`{OUTPUT_DIR}/people/{slug}.md`，使用bash heredoc。**绝对不要**使用Write工具或`python3 -c`。参考`references/example-research.md`获取两种文件格式。
- 报告编译：使用`node {SKILL_DIR}/scripts/compile_report.mjs {OUTPUT_DIR} --open`。
- **子代理必须仅使用Bash工具。不允许使用其他工具。**
- **硬工具调用限制**：ICP筛选=每个公司1次调用；深入研究=每个公司5次调用；人员丰富=每人4次调用。参考`references/workflow.md`了解执行细节。

**关键——防止幻觉规则（适用于主代理和所有子代理）**：
- **绝对不要**从网站的字体、框架、设计系统或排版中推断`product_description`、`industry`或人员的`role_reason`。这些是装饰性的，并不能说明公司销售什么或人员做什么。
- **绝对不要**让用户的ICP泄露到目标的描述中。如果您不知道目标做什么，请写`Unknown`——不要将他们与ICP进行模式匹配。
- `product_description`必须引用或释义`extract_page.mjs`输出中的特定短语。如果标题/META/OG/HEADINGS/BODY中没有产生可识别的产品声明，请写`Unknown — homepage content not accessible`，并将`icp_fit_score`限制在3。
- 人员的`hook`必须引用或释义`browse cloud search`结果中的特定发现（播客标题、博客标题、GitHub仓库、演讲摘要）。如果过去6个月内没有公共信号，则回退到事件上下文（他们在本次会议的演讲标题）。

**关键——最小化权限提示**：
- 子代理必须将所有文件写入批量到一个单一的Bash调用中，使用链接的heredoc。一个Bash调用=一个权限提示。
- 将所有搜索和所有获取批量到一个单一的Bash调用中，使用`&&`链接。

## 管道概述

按顺序执行以下10个步骤。不要跳过步骤或重新排序。

0. **设置** — 输出目录+干净状态
1. **加载配置文件** — 读取`profiles/{user_slug}.json`
2. **侦察** — 检测事件平台
3. **提取人员** — `people.jsonl`
4. **按公司分组** — `seed_companies.txt`
5. **ICP筛选** — 快速公司级评分（每个公司1次调用）
6. **过滤** — ICP得分`>= --icp-threshold`的公司
7. **深入研究** — 对ICP匹配公司进行完整的计划→研究→综合
8. **丰富演讲者** — 询问用户：仅ICP匹配（默认）或所有演讲者
9. **编译报告** — HTML + CSV，在浏览器中打开

用户使用类似`/event-prospecting <URL>`的URL调用技能。从调用消息中解析`EVENT_URL`。默认值：`DEPTH=deep`，`ICP_THRESHOLD=6`。`USER_SLUG`（ICP配置文件）在步骤1中自动解析，从本地存在的任何配置文件中——没有内置默认配置文件。**不要**要求用户确认URL——他们已经给了你。

---

## 步骤 0：设置输出目录

根据用户给您的URL导出输出目录。**不要**硬编码任何事件名称。

```bash
# EVENT_URL来自调用消息（用户在/event-prospecting之后输入的任何内容）
EVENT_SLUG=$(node -e 'const h = new URL(process.argv[1]).hostname.replace(/^www\./,""); console.log(h.split(".")[0])' "$EVENT_URL")
TIMESTAMP=$(date +%Y-%m-%d-%H%M)
OUTPUT_DIR=/Users/jay/Desktop/${EVENT_SLUG}_prospects_${TIMESTAMP}
mkdir -p "$OUTPUT_DIR/companies" "$OUTPUT_DIR/people"
```

使用完整的字面家路径——**不要**使用`~`或`$HOME`。将`{OUTPUT_DIR}`作为完整的字面路径传递给所有子代理提示。

## 步骤 1：加载用户配置文件

配置文件定义了ICP，ICP筛选和深入研究评分。从`{SKILL_DIR}/profiles/{user_slug}.json`加载（在所有GTM技能中可互换——形状与公司研究相同）。`example.json`是一个模板，不是真实配置文件——**永远不要**使用它。

**不要**在`{SKILL_DIR}/profiles/`之外查找配置文件——**永远不要**深入到其他技能的目录中。如果需要在其他地方使用配置文件，请用户显式复制它。

**解析顺序**：
1. 如果用户使用`--user-company <slug>`调用，请使用该slug。
2. 否则，列出`profiles/*.json`（排除`example.json`）。如果恰好存在一个配置文件，请使用它（并告诉用户是哪一个）。如果存在多个，请通过纯聊天询问用户选择哪一个。
3. 如果一个配置文件都不存在，**大声失败**并指示用户创建一个（将`profiles/example.json`复制到`profiles/<your_slug>.json`并填写它，或运行公司研究技能自动构建一个）。

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
    echo "重新调用时使用 --user-company <slug> 来选择一个。"
    exit 1
  fi
fi

test -f {SKILL_DIR}/profiles/${USER_SLUG}.json || {
  echo "找不到配置文件：profiles/${USER_SLUG}.json"
  exit 1
}
cat {SKILL_DIR}/profiles/${USER_SLUG}.json
```

配置文件将产生：`company`、`product`、`icp_description`、`existing_customers`。这些将在下游的每个子代理提示中嵌入原样。

## 步骤 2：侦察

检测事件平台和提取策略。一个命令：

```bash
node {SKILL_DIR}/scripts/recon.mjs {EVENT_URL} {OUTPUT_DIR}
```

写入`{OUTPUT_DIR}/recon.json`，包含`platform`、`strategy`，以及（对于Next.js）`nextDataPaths`。参考`references/event-platforms.md`了解平台目录和检测优先级。

预期结果：
- Stripe Sessions类（Next.js）：`platform: "next-data"`，1-3个路径
- Sessionize：`platform: "sessionize"`
- Lu.ma / Eventbrite：`platform: "luma" | "eventbrite"`
- 其他任何内容：`platform: "custom"`，`strategy: "markdown"`（尽力回退）

## 步骤 3：提取人员

```bash
node {SKILL_DIR}/scripts/extract_event.mjs {OUTPUT_DIR} --user-company {USER_SLUG}
```

读取`recon.json`，分派到平台特定的提取器，写入`people.jsonl`（每行一个演讲者）和`seed_companies.txt`（去重公司）。

`--user-company`标志还会从演讲者列表中删除主机组织的员工（Stripe托管的会议会删除Stripe员工）和用户自己的员工——他们不是潜在客户。

检查输出：
```bash
wc -l {OUTPUT_DIR}/people.jsonl {OUTPUT_DIR}/seed_companies.txt
head -3 {OUTPUT_DIR}/people.jsonl
```

如果`people.jsonl`为空或少于~10行，侦察选择了错误的平台——参考`references/event-platforms.md`并使用调整后的策略重新运行。

## 步骤 4：按公司分组

`extract_event.mjs`已经发出`seed_companies.txt`（每行一个公司，去重，排序）。此步骤是信息性的——在扩展之前，请验证计数是否合理：

```bash
wc -l {OUTPUT_DIR}/seed_companies.txt
```

预期：大致为演讲者计数的0.4-0.6倍（大多数会议平均每个公司有2名演讲者，一些公司发送5+，许多公司发送1）。

## 步骤 5：ICP筛选

**快速通道——每个公司一次工具调用，无需深入研究。** 对`seed_companies.txt`中的每个公司进行用户ICP评分，并写入一个薄的筛选桩到`companies/{slug}.md`。ICP得分`>= --icp-threshold`（默认6）的公司将进入步骤7的深入研究；其余的将保留为筛选桩。

**分派模式**：将`seed_companies.txt`分成约10个一批，在一个单独的Agent批处理中分派N个子代理（最多每批6个Agent；后续批次在第一批返回后）。每个子代理运行来自`references/workflow.md` → "ICP筛选"部分的提示。硬限制：**每个公司1次工具调用**（仅对主页调用`extract_page.mjs`），通过`# browse call N/1`注释模式强制执行。

```bash
# 构建批量文件：每个批量行是 "name|guessed_homepage|slug"。
# extract_event.mjs 仅发出公司名称（没有URL），因此我们slugify并猜测
# https://{slug-without-spaces}.com 作为规范主页。筛选子代理
# 允许写 product_description: "Unknown — homepage content not accessible"
# 并如果猜测的URL 404，将得分限制在3——这是 workflow.md 中
# ICP筛选提示的文档化回退。使用真实的 browse cloud search 发现URL
# 将会破坏每个公司1次调用的硬限制。
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

# 分割成约10家公司一批
split -l 10 {OUTPUT_DIR}/_seed_with_urls.txt {OUTPUT_DIR}/_batch_triage_
ls {OUTPUT_DIR}/_batch_triage_* | wc -l
```

然后在一条消息中，分派一个Agent调用每个批量（最多并行6个；第一批返回后的后续批次）。每个Agent获得来自`references/workflow.md` → "ICP筛选"的提示，并在发送之前替换以下占位符：
- `{SKILL_DIR}` → 完整字面技能路径（例如`/Users/jay/skills/skills/event-prospecting`）
- `{OUTPUT_DIR}` → 完整字面输出路径
- `{USER_COMPANY}`、`{USER_PRODUCT}`、`{ICP_DESCRIPTION}` → 从加载的配置文件
- `{EVENT_NAME}` → `recon.json`的`.title`
- `{COMPANY_LIST}` → 批量文件的内容（例如`cat {OUTPUT_DIR}/_batch_triage_aa`）
- `{TOTAL}` → 此批次的行数（替换到`# browse call N/{TOTAL}`）

**Agent分派（骨架，在一个消息中重复每个批量）**：

```
Agent(
  description: "ICP筛选批量aa",
  prompt: <来自workflow.md的ICP筛选提示模板，所有占位符替换>,
  subagent_type: "general-purpose"
)
Agent(
  description: "ICP筛选批量ab",
  prompt: <相同的提示模板，COMPANY_LIST 替换为批量ab>,
  subagent_type: "general-purpose"
)
... 最多每批6个
```

所有子代理返回后，验证`seed_companies.txt`中的每个公司都有一个对应的`companies/{slug}.md`：

```bash
ls {OUTPUT_DIR}/companies/*.md | wc -l
# 应该等于 `wc -l {OUTPUT_DIR}/seed_companies.txt`
```

清理批量文件：`rm {OUTPUT_DIR}/_batch_triage_*`。

## 步骤 6：按ICP阈值过滤

读取每个`companies/*.md`的frontmatter，保留得分`>= 6`（或任何`--icp-threshold`）的。将幸存的公司slug写入`{OUTPUT_DIR}/icp_fits.txt`：

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

预期：`seed_companies.txt`的20-40%。如果存活率低于10%，阈值可能太高或ICP描述太窄——向用户显示警告。

## 步骤 7：深入研究

仅对ICP匹配公司进行完整的计划→研究→综合。硬限制：**每个公司5次工具调用**（主页提取 + 2-3个子问题搜索 + 1-2个补充获取）。子代理用更丰富的深入研究版本覆盖现有的`companies/{slug}.md`筛选桩（frontmatter `triage_only: false`）。

**分派模式**：将`icp_fits.txt`分成约5批（深入研究模式默认）并在一条消息中分派一个Agent每批（最多并行6个Agent；第一批返回后的后续批次）。每个Agent获得来自`references/workflow.md` → "深入研究"的提示，并替换以下占位符：
- `{SKILL_DIR}`、`{OUTPUT_DIR}`、`{USER_COMPANY}`、`{USER_PRODUCT}`、`{ICP_DESCRIPTION}`
- `{EVENT_NAME}`（来自`recon.json`的`.title`）、`{EVENT_CONTEXT}`（跟踪 / 主题，从事件主页手动推断）
- `{COMPANY_LIST}` → 批量文件的内容（每行`slug|website`）

```bash
# 构建公司slug|website对，通过读取每个筛选桩的frontmatter
while read slug; do
  website=$(awk '/^website:/{print $2; exit}' {OUTPUT_DIR}/companies/${slug}.md)
  echo "${slug}|${website}"
done < {OUTPUT_DIR}/icp_fits.txt > {OUTPUT_DIR}/_deep_targets.txt

# 分割成约5家公司一批（深入研究模式）
split -l 5 {OUTPUT_DIR}/_deep_targets.txt {OUTPUT_DIR}/_batch_deep_
ls {OUTPUT_DIR}/_batch_deep_* | wc -l
```

**Agent分派（骨架，在一个消息中重复每批）**：

```
Agent(
  description: "深入研究批量aa",
  prompt: <来自workflow.md的深入研究提示模板，所有占位符替换；COMPANY_LIST = cat _batch_deep_aa>,
  subagent_type: "general-purpose"
)
Agent(
  description: "深入研究批量ab",
  prompt: <相同的模板，COMPANY_LIST = cat _batch_deep_ab>,
  subagent_type: "general-purpose"
)
... 最多每批6个；第一批返回后的后续批次
```

所有子代理返回后，验证深入研究文件存在并具有`triage_only: false`：

```bash
grep -l "triage_only: false" {OUTPUT_DIR}/companies/*.md | wc -l
# 应该等于 wc -l icp_fits.txt
```

## 步骤 8：丰富演讲者

对每个人：收集LinkedIn URL、近期活动（播客 / 博客 / 演讲 / GitHub / X），并写入`people/{slug}.md`。硬限制：**每人4次工具调用**，三个通道：

1. `browse cloud search "{name} {company} linkedin"`（始终）
2. `browse cloud search "{name} podcast OR talk OR blog 2026"`（深入+）
3. `browse cloud search "{name} github"`（更深）
4. `browse cloud search "{name} site:x.com OR site:twitter.com"`（更深，尽力而为）

快速模式：完全跳过步骤8。深入模式：通道1-2。更深模式：通道1-4。

### 步骤 8a — 询问用户：丰富范围

在分派之前，根据`ENRICH_SCOPE`计算两个候选计数并询问用户选择。默认值是**仅ICP匹配**（更快、更便宜、大多数用户想要的）；丰富所有演讲者是可选的，因为成本与丰富的人数线性增长。

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
const wantNames = new Set(Object.values(slug2name).map(s => s.toLowerCase()));
const ppl = fs.readFileSync("{OUTPUT_DIR}/people.jsonl","utf-8").split("\n").filter(Boolean).map(JSON.parse);
console.log(ppl.filter(p => p.company && wantNames.has(p.company.toLowerCase())).length);
')

# 每人 lanes: 2（深入）或 4（更深）——匹配 {DEPTH}
LANES=2   # 或 4 for deeper
echo "ICP匹配：${ICP_FITS}演讲者 × ${LANES} = $((ICP_FITS * LANES)) 调用"
echo "全部：      ${TOTAL}演讲者 × ${LANES} = $((TOTAL * LANES)) 调用"
```

然后通过`AskUserQuestion`询问——选择两个选项的干净聊天，每个选项上量化成本：

```
AskUserQuestion(questions: [
  {
    question: "丰富哪些演讲者?",
    header: "丰富范围",
    multiSelect: false,
    options: [
      { label: "仅ICP匹配", description: "${ICP_FITS}演讲者, ~$((ICP_FITS * LANES)) 调用（推荐）" },
      { label: "所有演讲者", description: "${TOTAL}演讲者, ~$((TOTAL * LANES)) 调用" }
    ]
  }
])
```

将选择范围保存为`ENRICH_SCOPE=icp_fits`或`ENRICH_SCOPE=all`。如果用户选择“所有演讲者”且`TOTAL × LANES > 600`，打印警告并再次询问——这将是一个10多分钟的运行，涉及数百个工具调用。

### 步骤 8b — 过滤和批量

```bash
# 基于 ENRICH_SCOPE 构建 _people_to_enrich.jsonl
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
console.error(`丰富 ${keep.length} of ${lines.length} 演讲者`);
'
fi

# 分割成约5人一批
split -l 5 {OUTPUT_DIR}/_people_to_enrich.jsonl {OUTPUT_DIR}/_batch_people_
```

然后在一条消息中，分派一个Agent调用每批（最多每批6个）使用来自`references/workflow.md` → "人员丰富"的提示。每个子代理的提示应包括：
- `{SKILL_DIR}`、`{OUTPUT_DIR}`、`{DEPTH}` (`deep` | `deeper`)
- `{USER_COMPANY}`、`{USER_PRODUCT}`、`{ICP_DESCRIPTION}`
- `{EVENT_NAME}`（来自`recon.json`的`.title`）
- `{LANES}` → `2` for deep mode, `4` for deeper mode（替换到`# browse call N/{LANES}`）
- `{PEOPLE_BATCH}` → `_batch_people_aa`的内容（每行来自`people.jsonl`的JSON记录）

**Agent分派（骨架，在一个消息中重复每批）**：

```
Agent(
  description: "人员丰富批量aa",
  prompt: <来自workflow.md的人员丰富提示模板，所有占位符替换；PEOPLE_BATCH = cat _batch_people_aa>,
  subagent_type: "general-purpose"
)
Agent(
  description: "人员丰富批量ab",
  prompt: <相同的模板，PEOPLE_BATCH = cat _batch_people_ab>,
  subagent_type: "general-purpose"
)
... 最多每批6个
```

所有子代理返回后，验证人员文件存在：

```bash
ls {OUTPUT_DIR}/people/*.md | wc -l
# 应该等于 wc -l _people_to_enrich.jsonl
```

## 步骤 9：编译报告

使用一个命令生成按公司分组的HTML索引、备用视图和CSV：

```bash
node {SKILL_DIR}/scripts/compile_report.mjs {OUTPUT_DIR} --open
```

这将生成：
- `{OUTPUT_DIR}/index.html` — 按公司分组的人员，按公司ICP得分排序（在浏览器中打开）
- `{OUTPUT_DIR}/people.html` — 可过滤的演讲者列表（备用视图）
- `{OUTPUT_DIR}/companies.html` — ICP排序的公司表，包含参会者
- `{OUTPUT_DIR}/results.csv` — 冷触达就绪的电子表格

然后通过聊天显示摘要：

```
## 事件潜在客户开发完成 — {Event Name}

- **提取的演讲者总数**: {count}
- **唯一公司**: {count}
- **ICP匹配（得分 >= {threshold}）**: {count}
- **丰富演讲者**: {count}
- **得分分布**（公司）:
  - 强匹配 (8-10): {count}
  - 部分匹配 (5-7): {count}
  - 弱匹配 (1-4): {count}
- **报告已在浏览器中打开**: {OUTPUT_DIR}/index.html
```

显示**前5个人卡**作为Markdown表格，按公司ICP得分排序，并提供选择：
- 调整`--icp-threshold`并重新运行步骤6-9
- 将CSV导出到CRM
