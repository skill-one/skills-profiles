---
name: wiki-lint
description: 审计和维护Obsidian维基的健康状态。当用户想要检查其维基是否存在问题、查找遗弃页面、检测矛盾、识别过时内容、修复损坏的维基链接，或对其知识库进行一般维护时，使用此技能。同时，在“清理维基”、“哪些需要修复”、“审计我的笔记”或“维基健康检查”时也会触发。添加`--consolidate`参数可从仅报告模式切换到行动并报告模式（“梦想周期”）：修复损坏的链接、为遗弃页面添加缺失的交叉引用、修正生命周期状态、降级过时的边缘页面、规范化标签别名，并添加矛盾提示——所有操作都会在写入前进行干跑预览并要求用户明确确认。
---

# Wiki Lint — 健康审计

您正在对 Obsidian 维基进行健康检查。您的目标是查找并修复随着时间的推移会降低维基价值的结构性问题。

**在扫描任何内容之前：** 遵循 `llm-wiki/SKILL.md` 中的检索原语表。优先使用作用域为 frontmatter 的 grep 和锚定于部分的读取，而不是全页读取。在一个大型保险库中，盲目地读取每一页以进行 lint 是这个框架旨在避免的。

## 开始之前

**写作配置文件：** 在起草或重写自然语言 Markdown 之前，请阅读并应用 `llm-wiki/SKILL.md` 中的 `Writing Profile Resolution` 部分。框架模式、来源、安全性和特定于操作的 requirements 优先。
仅将 `WRITING.md` 偏好应用于生成的整合报告；确定性发现和修复保留其现有格式。

1. **解决配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解决协议（内联 `@name` 覆盖 → 沿 CWD 向上查找 `.env` → 全局配置 → 提示设置）。这会提供 `OBSIDIAN_VAULT_PATH` 以及任何 `OBSIDIAN_ALLOWED_LIFECYCLES`、`OBSIDIAN_ALLOWED_RELATIONSHIP_TYPES`、`OBSIDIAN_REQUIRED_TRUST_FIELDS` 和 `OBSIDIAN_SCHEMA_SOURCE` 值。
2. **读取所有者规则** — 如果 `$OBSIDIAN_VAULT_PATH/AGENTS.md` 存在，则在解释任何模式之前读取它。所有者规则优先于框架默认值。
3. **形成有效模式** — 记录模式来源定位器以及有效的必需/可选 frontmatter、生命周期值、关系类型和来源标记。框架值是默认值；保留所有者扩展和放宽必需性。永远不要将所有者类型强制转换为框架类型。
4. 读取 `index.md` 以获取完整页面清单
5. 读取 `log.md` 以获取最近活动的上下文

将有效模式显式传递给确定性检查。例如，使用 `--allow-lifecycle` / `--allow-relationship-type` 添加每个所有者扩展，使用重复的 `--required-trust-field` 替换信任必需性，并使用 `--schema-source "$OBSIDIAN_VAULT_PATH/AGENTS.md"` 识别权威性。JSON 报告的 `schema` 块必须与您形成模式匹配，然后才能接受发现。

模式优先级为 CLI 标志 > 解析的环境/配置值 > 框架默认值；生命周期和关系扩展保持可加性。在使用之前删除所有覆盖。显式配置的空值或仅包含空格的值——以及任何空逗号分隔列表条目——会失败；永远不要将其视为有效的生命周期、关系类型、必需字段或权威定位器。当意图为默认值时，请删除该变量。

## Lint 检查

按顺序运行这些检查。边进行边报告发现。

**范围：** 在每个检查中跳过 `_archives/`、`_raw/`、`_readouts/` 和 `.obsidian/`。这些包含冻结的快照、未处理的暂存草稿和派生的读取输出（由 `wiki-narrate` 保存）——它们不是知识图谱页面，因此孤儿、frontmatter 和链接检查不适用于它们。

### 1. 孤儿页面

查找具有零入站维基链接的页面。这些是知识孤岛，没有任何内容连接到它们。

**如何检查：**
- 在保险库中 glob 所有 `.md` 文件
- 对于每个页面，在保险库中 grep `[[page-name]]` 引用
- 除 `index.md` 和 `log.md` 外，具有零入站链接的页面是孤儿的

**如何修复：**
- 确定哪些现有页面应该链接到孤儿
- 在适当的章节中添加维基链接

### 2. 破坏的维基链接

查找指向不存在的页面的 `[[wikilinks]]`。

**如何检查：**
- 在所有页面中 grep `\[\[.*?\]\]`
- 提取链接目标：丢弃从第一个 `|`（别名）或 `#`（标题/块锚点）开始的所有内容，并删除由表格单元格中转义的 `\|` 留下的尾随反斜杠
- 跳过目标扩展为附件类型（`.png`、`.jpg`、`.gif`、`.svg`、`.webp`、`.pdf`、`.canvas`、`.base`、音频和视频）：它是一个嵌入，而不是页面链接，并且没有条目在与此检查比较的 `.md` 清单中
- **不要** 将每个点视为扩展——`[[Node.js]]`、`[[Next.js]]` 和 `[[v1.2 release notes]]` 是页面链接，其名称碰巧包含点，并且丢弃它们会同时错过真实的破坏链接并使目标页面看起来像孤儿
- 从剩余内容中删除显式的 `.md` 后缀，然后检查是否存在相应的 `.md` 文件

**如何修复：**
- 如果目标被重命名，请更新链接
- 如果目标应该存在，请创建它
- 如果链接错误，请删除或更正它

### 3. 缺失 Frontmatter

每个页面都应该有：标题、类别、标签、来源、创建、更新。

**如何检查：**
- 读取 frontmatter 块（将范围限制为文件头部 `^---`）而不是读取每个页面的全文
- 标记缺少必需字段的页面

**如何修复：**
- 使用合理的默认值添加缺失的字段

### 3a. 缺失摘要（软警告）

每个页面*应该*有一个 `summary:` frontmatter 字段——1-2 句话，≤200 个字符。这是廉价检索（例如 `wiki-query` 的索引仅模式）读取以避免打开页面正文的内容。

**如何检查：**
- 在保险库中 grep frontmatter 中的 `^summary:`
- 标记没有它的页面，**但作为软警告而不是错误**——预先生成的页面是好的；此检查存在的目的是推动摄取技能在新的写入中填写它。
- 还标记摘要超过 200 个字符的页面。

**如何修复：**
- 重新摄取页面，或手动编写简短的摘要（1-2 句话的页面内容）。

### 4. 过期内容

其 `updated` 时间戳相对于其来源过时的页面。

**如何检查：**
- 比较页面 `updated` 时间戳和来源文件修改时间
- 标记来源在页面最后更新后被修改的页面

### 5. 矛盾

跨页面冲突的声明。

**如何检查：**
- 这需要读取相关页面并比较声明
- 专注于共享标签或 heavily cross-referenced 的页面
- 寻找可能表示现有公认矛盾与未公认矛盾之间的短语，如 "however"、"in contrast"、"despite"

**如何修复：**
- 添加一个 "Open Questions" 部分，注明矛盾
- 引用两个来源及其声明

### 6. 索引一致性

验证 `index.md` 是否与实际页面清单匹配。

**如何检查：**
- 比较在 `index.md` 中列出的页面与磁盘上的实际文件
- 检查 `index.md` 中的摘要是否仍然与页面内容匹配

### 7. 来源漂移

检查页面是否诚实地说明了其内容有多少是推断的而不是提取的。有关约定，请参阅 `llm-wiki` 中的来源标记部分。

**如何检查：**
- 对于每个具有 `provenance:` 块或任何 `^[inferred]`/`^[ambiguous]` 标记的页面，计算句子/项目数量以及以每个标记结尾的数量
- 计算大致分数（`extracted`、`inferred`、`ambiguous`）
- 应用这些阈值：
  - **AMBIGUOUS > 15%**：标记为 "speculation-heavy"——即使 1/7 的声明确实是不可确定的，也是一个信号，表明页面需要更严格的来源或应移动到 `synthesis/`
  - **INFERRED > 40% 且 frontmatter 中没有 `sources:`**：标记为 "unsourced synthesis"——页面正在建立联系，但没有可以引用的东西
  - **Hub 页面**（按入站维基链接计数前 10 名）的 `INFERRED > 20%`：标记为 "具有可疑来源的高流量页面"——在 hub 页面上出现的错误会传播到它们链接的每个页面
  - **漂移**：如果页面具有 `provenance:` frontmatter 块，则在任何字段与重新计算的值偏差超过 0.20 时标记它
- **跳过** 没有来源 frontmatter 和没有标记的页面——按约定，它们被视为完全提取

**如何修复：**
- 对于 ambiguous-heavy：从来源重新摄取，解决不确定的声明，或将推测性内容移动到 `synthesis/` 页面
- 对于 unsourced synthesis：在 frontmatter 中添加 `sources:` 或清楚地标记该页面为合成
- 对于 hub 页面的 `INFERRED > 20%`：优先重新摄取——这里的错误具有最广泛的传播范围
- 对于漂移：更新 `provenance:` frontmatter 以匹配重新计算的值

### 8. 分裂的标签集群

检查共享标签的页面是否实际相互链接。标签暗示主题集群；如果这些页面不引用彼此，则集群是分裂的——应该交织在一起的知识孤岛。

**如何检查：**
- 对于每个在 ≥ 5 个页面上出现的标签：
  - `n` = 具有此标签的页面计数
  - `actual_links` = 此标签组中任意两个页面之间的维基链接计数（检查两个方向）
  - `cohesion = actual_links / (n × (n−1) / 2)`
- 标记任何 `cohesion < 0.15` 且 `n ≥ 5` 的标签组

**如何修复：**
- 运行针对分裂标签的 `cross-linker` 技能——它将显示并插入缺失的链接
- 如果标签组很大（n > 15）并且仍然分裂，请考虑将其拆分为更具体的子标签

### 9. 可见性标签一致性

检查 `visibility/` 标签是否正确应用，并且它们在重要位置不会无声地丢失。

**如何检查：**

- **未标记的 PII 模式：** 在页面正文中 grep 常见指示敏感数据的模式——包含 `password`、`api_key`、`secret`、`token`、`ssn`、`email:` 后跟实际值（不是字段描述）的行。如果页面匹配并且缺少 `visibility/pii` 或 `visibility/internal`，则将其标记为可能的错误分类。
- **`visibility/pii` 而没有 `sources:`**：标记为 `visibility/pii` 的页面始终应该具有 `sources:` frontmatter 字段——如果没有来源，就没有办法验证分类。标记任何缺少 `sources:` 的 `visibility/pii` 页面。
- **分类法中的可见性标签：** `visibility/` 标签是系统标签，**不能** 出现在 `_meta/taxonomy.md` 中。如果找到它们，则标记为配置错误——它们会计入包含它们的页面的 5 标签限制。

**如何修复：**
- 对于未标记的 PII 模式：将 `visibility/pii`（如果是团队上下文而不是个人数据，则使用 `visibility/internal`）添加到页面的 frontmatter 标签中
- 对于缺少 `sources:`：添加来源或升级给用户——不要自动填充
- 对于分类法污染：从 `_meta/taxonomy.md` 中删除 `visibility/` 条目

### 10. 其他晋升候选者

查找 `misc/` 中的页面，它们积累了足够的项目亲和力以供晋升。

**如何检查：**
- Glob `$OBSIDIAN_VAULT_PATH/misc/*.md`
- 对于每个页面，读取 `affinity` frontmatter 字段
- 标记任何单个项目的分数 ≥ 3 的页面

**如何修复：**
- 如果亲和度分数看起来过时（例如，具有许多维基链接的页面上有 `affinity: {}`），请首先运行 `cross-linker` 技能
- 要晋升：将页面移动到 `projects/<project-name>/references/`（或另一个适当的类别），更新其 `category` frontmatter，删除 `promotion_status`，并 grep 保险库以更新它们

### 12. 置信度和生命周期模式

强制执行 confidence + lifecycle frontmatter 模式（请参阅 `llm-wiki/SKILL.md`，置信度和生命周期部分）。

两种模式：
- **`--check`**（默认，只读）——报告错误和警告
- **`--consolidate`**——可能应用单独批准的结构性维护，但**永远不会重写 `base_confidence`**

置信度是语义判断。确定性工具无法仅从来源字符串中推断独立的证据谱系或整个页面的声明覆盖率。因此，置信度自动化验证了明确批准的手动信任账本；它永远不会用 URL 计数代替审查。

#### 规则 12a — `lifecycle` 枚举验证

**如何检查：** 在所有页面的 frontmatter 中 grep `^lifecycle:`。标记任何不在有效生命周期集（框架默认值：`{draft, reviewed, verified, disputed, archived}`）中的值。

**如何修复：** n/a（只有人类应该设置生命周期状态）

#### 规则 12b — `base_confidence` 范围

**如何检查：** 在所有页面的 frontmatter 中 grep `^base_confidence:`。标记任何超出 `[0.0, 1.0]` 的值；仅在有效所有者模式要求该字段时标记缺失。

**如何修复：** n/a（错误值意味着技能计算错误——显示以供手动更正）

#### 规则 12c — 过期页面报告（计算覆盖）

过期永远不会存储——它在读取时计算：`is_stale = (today − updated) > 90 days`。

**如何检查：** 对于每个页面，从 frontmatter 中读取 `updated:` 并计算 `is_stale`。如果过期，则还检查 `lifecycle:`。报告：
- 过期且 `lifecycle: verified` 的页面，使用更响亮的注释（这些是最危险的——高信任页面可能不正确）
- 所有其他过期页面作为标准警告

**如何修复：** `--fix` **不会** 重写 `lifecycle`。过期会在重新摄取将 `updated` 推高时自动清除。

#### 规则 12c-2 — 非法生命周期转换

生命周期枚举是状态机，而不是自由形式的标签。`obsidian-wiki lint` 通过比较每个页面的当前 `lifecycle` 与 `_meta/trust-ledger.json` 中最后一次审查记录的值来报告 `illegal_lifecycle_transitions`。

**标记：** 任何回退到 `draft` 的状态（只有摄取设置 `draft`），以及任何从 `archived` 的退出（终端——恢复是一个故意的删除和重新创建）。

**未标记：** `draft → verified`。账本快照是稀疏的，因此两个审查之间可能发生了合法的中间 `reviewed`；标记它会在有效历史记录上触发。

默认情况下发出警告；在 `--strict-trust` 下失败。账本条目早于 `lifecycle` 字段的页面没有基线，并静默跳过。

**如何修复：** n/a——移动到禁止边缘的页面意味着要么技能在不应设置 `lifecycle` 时写了它，要么人类需要记录转换。显示以供人类解决。

#### 规则 12d — 超级使用完整性

**如何检查：** 对于每个具有 `superseded_by: "[[target]]"` 的页面：
- 验证目标页面是否存在
- 验证目标页面不是 `archived`（没有循环或链接超级使用）
- 验证没有循环（A 超级使用 B，B 超级使用 A）
- 如果 `lifecycle != archived` 而 `superseded_by` 设置，则发出警告（状态不一致）

**如何修复：** n/a——标记以供人类解决

#### 规则 12e — 置信度审查完整性

**如何检查：** 首先运行确定性账本验证器：

```bash
obsidian-wiki trust-check "$OBSIDIAN_VAULT_PATH" --strict --json --pretty
```

使用 `--strict` 进行 CI 和计划门：过期、未审查或缺失页面的警告将返回非零。如果没有 `--strict`，`trust-check` 保持为只读报告命令，并且仅在硬账本错误或分数不匹配时返回非零。

批准的账本位于 `_meta/trust-ledger.json`。每个条目记录了人类审查的分数以及材料页面内容和证据元数据的 SHA-256 指纹。指纹不包括易变账本 (`updated`、`base_confidence` 和生命周期转换字段)，因此仅时间戳编辑不会重新打开审查。

解释结果如下：

- `reviewed` — 当前材料指纹和存储的分数都与批准的审查匹配；**不要** 从来源字符串重新计算。
- `stale` — 正文、摘要、来源、来源、标签或关系发生变化；执行新的手动谱系 + 声明覆盖率审查。
- `unreviewed` — 页面没有批准的账本条目；需要手动审查。
- `score_mismatches` — 材料内容仍然匹配，但存储的 `base_confidence` 与批准的值不同；lint 失败。
- `errors` — 格式错误/缺失账本数据；lint 失败。

对于单独批准的完整保险库审查，显式记录接受状态：

```bash
obsidian-wiki trust-record "$OBSIDIAN_VAULT_PATH" \
  --all --reviewed-at "<ISO-8601 timestamp>" --approved --json --pretty
```

在单独批准仅针对特定过期/未审查页面的审查后，仅更新这些条目：

```bash
obsidian-wiki trust-record "$OBSIDIAN_VAULT_PATH" \
  --page "concepts/example.md" --page "skills/example.md" \
  --reviewed-at "<ISO-8601 timestamp>" --approved --json --pretty
```

`--approved` 表示每一条记录的分数都经过人工批准。这是一个工作流断言，而不是密码学签名：将 `_meta/trust-ledger.json` 放在版本控制下，并在合并账本更改之前要求人工差异审查。
`--all` 仅在完成全库审查后有效；对于部分审查，请使用可重复的 `--page`，以便保留与无关的过期页面。
永远不要仅仅为了消除警告而运行 `trust-record`。

**过期/未审查页面的手动重新计算协议：**

1. 将页面分解为材料声明，并将每个声明映射到证据。
2. 将依赖证据合并为独立谱系：来自一个存储库的文件/提交、一个任务链中的重试、快照及其捕获的源、重复记忆以及父子任务各计一次。
3. 使用 `llm-wiki` 桶为每个独立谱系分配已审查的质量。
4. 计算原始基础分数，然后评估整个页面的声明覆盖率。公式只是一个起点，不是一个自动目标。
5. 将结果分类为 `raise`、`keep`、`lower` 或 `repair first`；更改 `base_confidence` 或刷新账本之前需要批准。

**如何修复：** 没有自动置信度修复。仅应用明确批准的精确补丁，验证其范围，然后仅刷新已审查的账本状态。`--consolidate` 绝不能重写 `base_confidence`。

#### 当前执行情况

在框架默认情况下，每个非保留内容页面都必须包含一个有限的 `base_confidence` 在 `[0.0, 1.0]` 范围内，并有一个记录在案的生存周期值。
所有者模式可以放宽这两个字段；当前值仍然会进行验证。
缺少或格式错误的信任字段、格式错误的账本数据以及缺少必需的账本都是严重错误。具有有效信任字段但没有批准账本条目的新页面是 `unreviewed`；已批准页面的材料更改是 `stale`。

#### 输出添加

添加到 Wiki Health Report：

```markdown
### 置信度/生存周期问题 (N 个发现)
- `concepts/foo.md` — 缺少 `lifecycle` 字段 (警告：阶段 1)
- `entities/bar.md` — `lifecycle: stalestate` 不是有效的枚举值
- `concepts/scaling.md` — `base_confidence: 1.4` 超出范围 [0.0, 1.0]
- `synthesis/old-analysis.md` — STALE (最后更新 2025-10-01，182 天前) 生存周期=verified ⚠️ 高优先级
- `concepts/outdated.md` — STALE (最后更新 2025-11-15，137 天前) 生存周期=draft
- `entities/tool-v1.md` — `superseded_by: [[entities/tool-v2]]` 但生存周期=draft (预期存档)
- `concepts/drift-example.md` — 置信度审查过期：材料指纹已更改；需要手动谱系 + 覆盖率审查
- `entities/mismatch.md` — 置信度不匹配：存储=0.80，批准=0.59
```

追加到 `LINT` 日志条目：
```
- [TIMESTAMP] LINT ... lifecycle_issues=N
```

### 13. 类型关系有效性

验证 `relationships:` 前置块。跳过没有 `relationships:` 块的页面——该字段是可选的。

**框架默认类型：** `extends`、`implements`、`contradicts`、`derived_from`、`uses`、`replaces`、`related_to`。应用所有者扩展后，根据有效集进行验证。

**如何检查：**
- 在所有存储库页面中搜索前置 `^relationships:`
- 对于每个具有 `relationships:` 块的页面，读取其前置（不是完整的页面正文）
- 对于块中的每个条目：
  1. **类型验证**——标记任何不在上述允许集中 `type:` 值
  2. **损坏的目标**——从 `target:` 字符串中删除 `[[` 和 `]]`，规范化（小写，空格→连字符，删除 `.md`），并检查在存储库中是否存在该路径的 `.md` 文件。标记未解析的目标。
     在规范化之前，删除第一个 `|`（别名）或 `#`（标题/块锚点）之后的所有内容：管道别名或标题锚点目标并不是因为字面括号内容与文件名不匹配而损坏。
  3. **自我引用**——标记任何已解析目标等于页面自身节点 ID 的条目

**如何修复：**
- 无效类型：报告该值和有效模式源。仅在它既不在框架默认值中也不在所有者扩展中时才更正；永远不要用 `related_to` 替换有效的所有者类型。
- 损坏的目标：更新或删除该条目；如果目标页面应该存在，请先创建它
- 自我引用：删除该条目

**输出添加：**

```markdown
### 类型关系问题 (N 个发现)
- `concepts/foo.md` — relationships[1]: 类型 "contradication" 不是允许的类型（你是否意味着 "contradicts"？）
- `concepts/bar.md` — relationships[0]: 目标 "[[skills/nonexistent-skill]]" 在存储库中没有解析到页面
- `entities/baz.md` — relationships[2]: 自引用（目标解析到此页面的自身 ID）
```

追加到 `LINT` 日志条目：
```
... relationship_issues=N
```

### 14. 事件时间有效性

验证 `valid_from` / `valid_until` / `superseded_by` 前置。这三个都是可选的——跳过没有它们的页面。

`created`/`updated` 是摄取时间；这三个是事件时间，即声明本身为真时的时间。一个 `valid_until` 已过期的页面是 **历史** 的，而不是错误的：它仍然保留在存储库和图中，并且仅在默认检索中消失。

**如何检查：**
- 在所有存储库页面中搜索前置 `^valid_from:`, `^valid_until:`, `^superseded_by:`
- 对于每个具有其中之一的页面：
  1. **日期可解析性**——每个值必须是 `YYYY-MM-DD` 或完整的 ISO 8601 时间戳。标记任何其他内容。
  2. **窗口顺序**——标记任何 `valid_until` 早于 `valid_from` 的页面
  3. **悬空后继者**——从 `superseded_by` 中删除 `[[`/`]]`，删除第一个 `|` 或 `#` 之后的所有内容，删除 `.md`，规范化，并检查页面是否存在。标记未解析的目标和自我引用。

`obsidian-wiki lint` 将这三个报告为 `temporal_errors`（日期、窗口）和 `superseded_dangling`（后继者）。带括号的悬空后继者也会出现在 `broken_links` 中。

**为什么日期失败而不是警告：** 检索将无法解析的窗口视为当前，因此一个未报告的拼写错误会让过期的声明回答事实——这是字段存在的目的来防止的精确失败。

**如何修复：**
- 无法解析的日期：重写为 `YYYY-MM-DD`；如果真实日期未知，请删除该字段而不是猜测
- 顺序颠倒：使用页面的来源确认哪个日期是错误的；永远不要无声地交换它们
- 悬空后继者：创建替换页面，更正指针，或者如果没有替换声明则删除它
- 永远不要通过重写当前来“修复”历史页面——这将破坏窗口存在的记录

**输出添加：**

```markdown
### 事件时间问题 (N 个发现)
- `references/gateway-nginx.md` — valid_until (2026-04-01) 早于 valid_from (2026-05-01)
- `references/old-limits.md` — valid_until "soon" 不是一个日期
- `references/legacy-auth.md` — superseded_by "[[oauth-rollout]]" 在存储库中没有解析到页面
```

追加到 `LINT` 日志条目：
```
... temporal_issues=N
```

### 11. 合成差距

识别维基遗漏的高价值合成机会——在许多页面中共同出现的概念对，但没有 `synthesis/` 页面将它们连接起来。

**如何检查：**
- 列出 `synthesis/` 中的所有页面——收集每个页面已经涵盖的概念对（从其 `[[wikilinks]]` 或标题）
- 从 `concepts/` 和 `entities/` 中选择 10-15 个频繁链接的概念
- 对于每一对，运行快速 grep 来计算链接到两者的页面数量：
  ```bash
  rg -l --glob '*.md' "\[\[ConceptA\]\]" "$OBSIDIAN_VAULT_PATH" > /tmp/a.txt
  rg -l --glob '*.md' "\[\[ConceptB\]\]" "$OBSIDIAN_VAULT_PATH" > /tmp/b.txt
  comm -12 <(sort /tmp/a.txt) <(sort /tmp/b.txt) | wc -l
  ```
- 标记出现次数 ≥ 3 且没有现有合成页面的对

**如何修复：**
- 运行 `/wiki-synthesize` 自动发现并填充顶级差距

## 输出格式

以结构化列表的形式报告发现：

```markdown
## 维基健康报告

### 孤立页面 (N 个发现)
- `concepts/foo.md` — 没有入站链接

### 损坏的维基链接 (N 个发现)
- `entities/bar.md:15` — 链接到 [[nonexistent-page]]

### 缺少前置 (N 个发现)
- `skills/baz.md` — 缺少：标签，来源

### 过期内容 (N 个发现)
- `references/paper-x.md` — 来源修改 2024-03-10，页面最后更新 2024-01-05

### 矛盾 (N 个发现)
- `concepts/scaling.md` 声称 "X"，但 `synthesis/efficiency.md` 声称 "not X"

### 索引问题 (N 个发现)
- `concepts/new-page.md` 存在于磁盘上，但不在 index.md 中

### 缺少摘要 (N 个发现 — 软)
- `concepts/foo.md` — 没有 `summary:` 字段
- `entities/bar.md` — 摘要超过 200 个字符

### 起源问题 (N 个发现)
- `concepts/scaling.md` — AMBIGUOUS > 15%：22% 的声明是模糊的（重新溯源或移动到合成/）
- `entities/some-tool.md` — drift：前置声明 inferred=0.10，重新计算=0.45
- `concepts/transformers.md` — 中心页面（31 个入站链接）有 INFERRED=28%：错误会广泛传播
- `synthesis/speculation.md` — 无来源合成：没有 `sources:` 字段，55% 推断

### 分裂的标签集群 (N 个发现)
- **#systems** — 7 个页面，cohesion=0.06 ⚠️ — 对此标签运行跨链接器
- **#databases** — 5 个页面，cohesion=0.10 ⚠️

### 可见性问题 (N 个发现)
- `entities/user-records.md` — 包含 `email:` 值模式但没有 `visibility/pii` 标签
- `concepts/auth-flow.md` — 标签 `visibility/pii` 但缺少 `sources:` 前置
- `_meta/taxonomy.md` — 包含 `visibility/internal` 条目（系统标签不能在分类中）

### 其他晋升候选 (N 个发现)
misc/ 中的页面与单个项目有 ≥ 3 个连接，并且可以晋升：

| 页面 | 顶级项目 | 亲密度分数 |
|---|---|---|
| `misc/web-martinfowler-articles-microservices.md` | `obsidian-wiki` | 4 |

### 类型关系问题 (N 个发现)
- `concepts/foo.md` — relationships[1]: 类型 "contradication" 不是允许的类型
- `concepts/bar.md` — relationships[0]: 目标 "[[skills/nonexistent]]" 解析到没有页面

### 合成差距 (N 个发现)
频繁出现但没有合成页面的概念对：

| 对 | 出现次数 | 建议操作 |
|---|---|---|
| [[Caching]] × [[Consistency]] | 5 个页面 | 运行 `/wiki-synthesize` |
| [[Testing]] × [[Observability]] | 3 个页面 | 运行 `/wiki-synthesize` |
```

## Linting 后

追加到 `log.md`：
```
- [TIMESTAMP] LINT issues_found=N orphans=X broken_links=Y stale=Z contradictions=W prov_issues=P missing_summary=S fragmented_clusters=F visibility_issues=V promotion_candidates=C synthesis_gaps=G relationship_issues=R
```

提供自动修复问题或让用户决定要处理哪些问题。

---

## 合并模式 (`--consolidate`)

由 `wiki-lint --consolidate` 触发。从仅报告切换到 **执行并报告**——运行周期性以使维基自我修复的“梦想周期”。

### 安全协议

**始终先运行干运行。** 在写入任何内容之前：

1. 运行所有 12 个 lint 检查（上述步骤 1–12）。
2. 以结构化列表的形式打印计划的合并操作（见干运行输出）。
3. 询问用户：`"应用这些 N 个更改？[是 / 否 / 选择]"`。
4. 在明确确认后才能继续写入。如果用户选择单个操作，请仅应用那些操作。
5. 永远不要合并页面——使用 `wiki-dedup`。仅链接、晋升、降级和标记。

### 合并操作（确认后按顺序）

**写入前快照**——在第一个文件写入之前，检查存储库本身是否是 Git 存储库的根。仅仅是作为较大存储库的子目录并不符合：在 đó 运行 `git add -A` 可能会捕获无关的文件。如果存储库不是独立的 Git 存储库，则静默跳过此步骤——不烦扰，不建议 `git init`。

```bash
VAULT_REAL_PATH=$(cd "$OBSIDIAN_VAULT_PATH" && pwd -P)
VAULT_GIT_ROOT=$(git -C "$OBSIDIAN_VAULT_PATH" rev-parse --show-toplevel 2>/dev/null || true)
SNAPSHOT_SHA=""

if [ -n "$VAULT_GIT_ROOT" ] && [ "$VAULT_GIT_ROOT" = "$VAULT_REAL_PATH" ]; then
  if git -C "$OBSIDIAN_VAULT_PATH" diff --quiet \
    && git -C "$OBSIDIAN_VAULT_PATH" diff --cached --quiet \
    && [ -z "$(git -C "$OBSIDIAN_VAULT_PATH" ls-files --others --exclude-standard)" ]; then
    SNAPSHOT_SHA=$(git -C "$OBSIDIAN_VAULT_PATH" rev-parse HEAD)
  else
    if ! git -C "$OBSIDIAN_VAULT_PATH" add -A; then
      echo "写入前快照失败；放弃不写入任何存储库文件。" >&2
      exit 1
    fi
    if ! git -C "$OBSIDIAN_VAULT_PATH" commit -m "pre-wiki-lint 快照" --quiet; then
      echo "写入前快照失败；放弃不写入任何存储库文件。" >&2
      exit 1
    fi
    SNAPSHOT_SHA=$(git -C "$OBSIDIAN_VAULT_PATH" rev-parse HEAD)
  fi
fi
```

干净存储库分支故意避免调用 `git commit`，因此“没有要提交的”不被视为错误。如果 `git add` 或 `git commit` 失败，在编辑存储库之前停止；永远不要在没有承诺的快照的情况下继续。

如果 `SNAPSHOT_SHA` 非空并且技能写入文件，则在最终报告中包含 SHA。要丢弃整个运行，在确认没有值得保留的后续更改后，用户可以运行：

```bash
git -C "$OBSIDIAN_VAULT_PATH" reset --hard "$SNAPSHOT_SHA"
git -C "$OBSIDIAN_VAULT_PATH" clean -fd
```

#### 操作 1：修复损坏的维基链接

对于 Check 2 中发现的每个损坏的 `[[Target]]`：
- 在存储库中搜索标题或文件名与最接近的模糊匹配的页面（使用 `Grep` 跨 `index.md` 标题）
- 如果存在唯一的最佳匹配（编辑距离 ≤ 2 个字符或相同的根词）：重写链接。注意重写：`[[Oringal]] → [[corrected-page]]`。
- 如果没有匹配或模糊：转换为纯文本 (`~~[[Target]]~~` → `Target`) 并添加注释 `<!-- 损坏的链接：未找到匹配 -->`。
- 永远不要为了满足损坏的链接而创建新页面。

#### 操作 2：为孤立页面添加缺失的交叉引用

对于 Check 1 中发现的每个孤立页面（零入站链接）：
- 在存储库正文文本中搜索页面的标题或别名（不区分大小写）。
- 对于在另一个页面中找到的每个提及，添加一个 `[[wikilink]]` 替换纯文本提及。
- 每个孤立页面限制为 3 次插入——不要用链接淹没页面。
- 这仅限于孤立页面（与运行广泛的 `cross-linker` 不同）。

#### 操作 3：纠正生存周期状态

自动应用这些规则（它们不需要人工判断——它们执行记录在案的状态机）：
- **晋升 `draft` → `reviewed`：** `lifecycle: draft` AND `created` > 30 天 ago AND `base_confidence > 0.7` 的页面。设置 `lifecycle: reviewed`，`lifecycle_changed: <today>`，`lifecycle_reason: "自动晋升由 wiki-lint --consolidate：年龄>30d, 置信度>0.7"`。
- **降级 `verified` → `stale`：** 不是状态转换——`stale` 是计算叠加，不是生命周期值。相反：对于已验证页面，其中 `is_stale = (today − updated) > 180 days`，在页面正文顶部添加一个调用框：`> ⚠️ **Stale**：此页面最后更新 <date>。在依赖它之前请验证。**` 只有当调用框不存在时才添加。
- **不要更改 `reviewed` → `verified` 或任何其他转换**——那些是仅由人类处理的。

#### 操作 4：分级降级

对于具有 `tier: supporting`（或未设置）且 0 个入站链接且 90 多天未更新的页面：
- 设置 `tier: peripheral`。
- 发出一个列表供用户审查降级。
- 不要自动降级 `tier: core` 页面——那些是手动设置的。

#### 操作 5：标签规范化

读取 `_meta/taxonomy.md` 中的别名映射（例如，`ml → machine-learning`）。对于每个页面，在 `tags:` 前置字段中用已知别名替换其规范形式。这是 `tag-taxonomy` 工作的一个子集——仅别名修复，没有完整审计。

#### 操作 6：矛盾调用框

对于每对被标记为相互矛盾页面（通过 frontmatter 中的 `relationships: contradicts` 或 Check 5 标记）：
- 检查是否已在相关主张附近存在 `> ⚠️ 与 [[其他页面]] 标记的矛盾` 提示框。
- 如果不存在，将其添加到“关键点”部分的末尾（如果没有“关键点”部分，则添加到“开放问题”之前）。保持简洁——一行即可。
- 不要解决矛盾；只需进行视觉标记。

### 行动 7：编写整合报告

在所有操作完成后，将报告写入 `synthesis/consolidation-<YYYY-MM-DD>.md`：

```markdown
---
title: 整合报告 <YYYY-MM-DD>
category: synthesis
tags: [维护, 整合]
sources: []
summary: 从 wiki-lint --consolidate 运行生成的自动整合报告 <日期>。
lifecycle: 草稿
lifecycle_changed: <日期>
tier: 外围
created: <ISO 时间戳>
updated: <ISO 时间戳>
---

# 整合报告 — <YYYY-MM-DD>

## 摘要
- 修复的链接：N
- 添加的交叉引用：M
- 更新的生命周期状态：K
- 等级降级：D
- 标签规范化：T
- 添加的矛盾提示框：C

## 链接修复
- `concepts/foo.md:12` — [[旧目标]] → [[正确目标]]
- `entities/bar.md:8` — [[缺失]] → `缺失`（未找到匹配项）

## 添加交叉引用（孤儿救援）
- `concepts/baz.md` — 现在链接自：[[concepts/alpha]], [[skills/beta]]

## 生命周期更新
- `concepts/old-draft.md` — 草稿 → 已审核（年龄 45d，置信度 0.74）
- `synthesis/stale-verified.md` — 添加了过时提示框（最后更新 2025-10-01）

## 等级降级
- `concepts/unused-concept.md` — 支持性 → 外围（0 链接，120 天过时）

## 标签规范化
- `entities/some-tool.md` — `ml` → `machine-learning`

## 矛盾提示框
- `concepts/scaling.md` — 标记了与 [[synthesis/efficiency]] 的矛盾
```

### 干运行输出（在执行任何写入之前显示）

```
wiki-lint --consolidate — 干运行

计划操作（N 总计）：
[1] 修复链接：concepts/foo.md:12 [[旧目标]] → [[正确目标]]
[2] 添加交叉引用：concepts/baz.md ← [[concepts/alpha]]（孤儿救援）
[3] 生命周期：concepts/old-draft.md → 已审核（年龄 45d，置信度 0.74）
[4] 等级降级：concepts/unused.md → 外围（0 链接，112 天过时）
[5] 标签别名：entities/some-tool.md: ml → machine-learning
[6] 矛盾提示框：concepts/scaling.md ↔ [[synthesis/efficiency]]

应用这些 6 个更改？ [是 / 否 / 通过编号选择]
```

### 整合模式的日志条目

```
- [时间戳] LINT_CONSOLIDATE links_fixed=N orphans_rescued=M lifecycle_updates=K tier_demotions=D tag_fixes=T contradiction_callouts=C report=synthesis/consolidation-YYYY-MM-DD.md
```

## 整合写入后的 QMD 刷新

QMD 是一个搜索索引，不是事实来源。如果 `$QMD_WIKI_COLLECTION` 为空或未设置，跳过此步骤。仅在当前技能写入或重写仓室 Markdown 后运行。如果 QMD 刷新失败，不要回滚仓室更改；单独报告 QMD 状态。

如果设置了 `$QMD_CLI`，则使用 `$QMD_CLI`；否则使用 `qmd`。

```bash
${QMD_CLI:-qmd} update
```

如果输出表示需要向量或嵌入可能已过时，运行：

```bash
${QMD_CLI:-qmd} embed
```

使用以下任一方法验证集合：

```bash
${QMD_CLI:-qmd} ls "$QMD_WIKI_COLLECTION"
```

或，当知道特定页面路径时：

```bash
${QMD_CLI:-qmd} get "qmd://$QMD_WIKI_COLLECTION/<page>.md" -l 5
```

记录以下之一：
- `QMD 刷新：update + embed + verified`
- `QMD 刷新：仅 update + verified`
- `QMD 跳过：QMD_WIKI_COLLECTION 未设置`
- `QMD 跳过：qmd CLI 不可用`
- `QMD 失败：<简短错误摘要>`
