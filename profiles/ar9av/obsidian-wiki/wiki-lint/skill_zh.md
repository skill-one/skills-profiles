# Wiki Lint — 健康检查

您正在对 Obsidian 维基进行健康检查。您的目标是找出并修复会随着时间的推移降低维基价值的结构性问题。

**在扫描任何内容之前：** 遵循 `llm-wiki/SKILL.md` 中的检索原语表。优先使用作用域为 frontmatter 的 grep 和锚定于部分的读取，而不是全页读取。在一个大型保险库中，盲目地读取每一页以进行 lint 是这个框架旨在避免的。

## 开始之前

**写作配置文件：** 在起草或重写自然语言 Markdown 之前，请阅读并应用 `llm-wiki/SKILL.md` 中的 `Writing Profile Resolution` 部分。框架模式、来源、安全性和特定于操作的 requirements 优先。

仅将 `WRITING.md` 偏好应用于生成的合并报告；确定性发现和修复保留其现有格式。

1. **解决配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解决协议（内联 `@name` 覆盖 → 沿 CWD 搜索 `.env` → 全局配置 → 提示设置）。这会给出 `OBSIDIAN_VAULT_PATH` 以及任何 `OBSIDIAN_ALLOWED_LIFECYCLES`、`OBSIDIAN_ALLOWED_RELATIONSHIP_TYPES`、`OBSIDIAN_REQUIRED_TRUST_FIELDS` 和 `OBSIDIAN_SCHEMA_SOURCE` 值。
2. **读取所有者规则** — 如果 `$OBSIDIAN_VAULT_PATH/AGENTS.md` 存在，则在解释任何模式之前读取它。所有者规则优先于框架默认值。
3. **形成有效模式** — 记录模式源定位器以及有效的必需/可选 frontmatter、生命周期值、关系类型和来源标记。框架值是默认值；保留所有者扩展和放宽的必需性。永远不要将所有者类型强制转换为框架类型。
4. 读取 `index.md` 以获取完整页面清单
5. 读取 `log.md` 以获取最近活动的上下文

将有效模式显式传递给确定性检查。例如，添加每个所有者扩展，使用 `--allow-lifecycle` / `--allow-relationship-type`，用可重复的 `--required-trust-field` 替换信任必需性，并使用 `--schema-source "$OBSIDIAN_VAULT_PATH/AGENTS.md"` 识别权威。JSON 报告的 `schema` 块必须与您在发现被接受之前形成的模式匹配。

模式优先级是 CLI 标志 > 解析的环境/配置值 > 框架默认值；生命周期和关系扩展保持可加性。在使用之前删除每个覆盖。显式配置的空值或仅包含空格的值——以及任何空逗号分隔列表条目——都会导致失败；永远不要将其视为有效的生命周期、关系类型、必需字段或权威定位符。当默认值意图时，请删除该变量。

## Lint 检查

按顺序运行这些检查。边进行边报告发现的问题。

**范围：** 在每个检查中跳过 `_archives/`、`_raw/`、`_readouts/` 和 `.obsidian/`。这些地方保存着冻结的快照、未处理的暂存草稿和派生的读取输出（由 `wiki-narrate` 保存）——它们不是知识图谱页面，因此孤儿、frontmatter 和链接检查不适用于它们。

### 1. 孤儿页面

查找具有零入站 wikilink 的页面。这些是知识孤岛，没有任何内容连接到它们。

**如何检查：**
- Glob 保险库中的所有 `.md` 文件
- 对于每个页面，在保险库的其余部分中 Grep `[[page-name]]` 引用
- 除 `index.md` 和 `log.md` 外，具有零入站链接的页面是孤儿

**如何修复：**
- 确定哪些现有页面应该链接到孤儿
- 在适当的章节中添加 wikilink

### 2. 破坏的 Wikilink

查找指向不存在的页面的 `[[wikilinks]]`。

**如何检查：**
- 在所有页面中 Grep `\[\[.*?\]\]`
- 提取链接目标：删除从第一个 `|`（别名）或 `#`（标题/块锚点）开始的所有内容，并删除由表格单元格中转义的 `\|` 留下的尾随反斜杠
- 跳过扩展是附件类型（`.png`、`.jpg`、`.gif`、`.svg`、`.webp`、`.pdf`、`.canvas`、`.base`、音频和视频）的目标：它是一个嵌入，而不是页面链接，并且没有在 `.md` 清单中与这个检查进行比较的条目
- **不要** 将每个点视为扩展——`[[Node.js]]`、`[[Next.js]]` 和 `[[v1.2 release notes]]` 是页面链接，其名称碰巧包含点，删除它们会同时错过真正的损坏链接，并使目标页面看起来像孤儿
- 删除剩余内容中的显式 `.md` 后缀，然后检查是否存在相应的 `.md` 文件

**如何修复：**
- 如果目标被重命名，请更新链接
- 如果目标应该存在，请创建它
- 如果链接错误，请删除或更正它

### 3. 缺少 Frontmatter

每个页面都应该有：标题、分类、标签、来源、创建、更新。

**如何检查：**
- Grep frontmatter 块（范围到文件头部 `^---`）而不是读取每个页面的全文
- 标记缺少必需字段的页面

**如何修复：**
- 用合理的默认值添加缺少的字段

### 3a. 缺少摘要（软警告）

每个页面 *应该* 有一个 `summary:` frontmatter 字段——1-2 句话，≤200 个字符。这是廉价检索（例如 `wiki-query` 的索引仅模式）读取以避免打开页面正文的内容。

**如何检查：**
- 在保险库中 Grep frontmatter 中的 `^summary:`
- 标记没有它的页面，**但作为软警告而不是错误**——预日期此字段的旧页面是好的；检查的存在是为了推动摄取技能在新的写入中填写它。
- 还标记摘要超过 200 个字符的页面。

**如何修复：**
- 重新摄取页面，或手动编写简短的摘要（1-2 句页面内容）。

### 4. 过期内容

其 `updated` 时间戳相对于其来源过旧的页面。

**如何检查：**
- 比较页面的 `updated` 时间戳和来源文件的修改时间
- 标记来源在页面最后更新后被修改的页面

### 5. 矛盾

跨页面冲突的声明。

**如何检查：**
- 这需要读取相关页面并比较声明
- 专注于共享标签或大量交叉引用的页面
- 寻找可能表示现有公认矛盾与未公认矛盾之间的短语，如 "however"、"in contrast"、"despite"

**如何修复：**
- 添加一个 "Open Questions" 部分，注明矛盾
- 引用两个来源及其声明

### 6. 索引一致性

验证 `index.md` 是否与实际页面清单匹配。

**如何检查：**
- 比较 `index.md` 中列出的页面与磁盘上的实际文件
- 检查 `index.md` 中的摘要是否仍然与页面内容匹配

### 7. 来源漂移

检查页面是否诚实地说明其内容有多少是推断的而不是提取的。有关约定，请参阅 `llm-wiki` 中的来源标记部分。

**如何检查：**
- 对于每个具有 `provenance:` 块或任何 `^[inferred]`/`^[ambiguous]` 标记的页面：
  - 计算以每个标记结尾的句子/项目数量
  - 计算粗略分数（`extracted`、`inferred`、`ambiguous`）
- 应用这些阈值：
  - **AMBIGUOUS > 15%**: 标记为 "speculation-heavy"——即使 1/7 的声明确实是真正不确定的，这也是页面需要更严格的来源或应移动到 `synthesis/` 的信号
  - **INFERRED > 40% with no `sources:` in frontmatter**: 标记为 "unsourced synthesis"——页面正在建立连接，但没有可引用的内容
  - **Hub 页面**（前 10 个按入站 wikilink 计数）的 `INFERRED > 20%`: 标记为 "高流量页面具有可疑来源"——在 hub 页面上出现的错误会传播到每个链接到它们的页面
  - **漂移**: 如果页面具有 `provenance:` frontmatter 块，则当任何字段与重新计算的值超过 0.20 时，标记它
- **跳过** 没有来源标记和标记的页面——按约定，它们被视为完全提取

**如何修复：**
- 对于模糊重：从来源重新摄取，解决不确定的声明，或将推测性内容放入 `synthesis/` 页面
- 对于无来源的综合：在 frontmatter 中添加 `sources:` 或清楚地标记该页面为综合
- 对于 hub 页面的 `INFERRED > 20%`: 优先考虑重新摄取——这里的错误传播范围最广
- 对于漂移：更新 `provenance:` frontmatter 以匹配重新计算的值

### 8. 分裂的标签集群

检查共享标签的页面是否实际上相互链接。标签暗示主题集群；如果这些页面没有相互引用，则集群是分裂的——知识孤岛，本应交织在一起。

**如何检查：**
- 对于每个出现 ≥ 5 个页面的标签：
  - `n` = 具有此标签的页面计数
  - `actual_links` = 此标签组中任何两个页面之间的 wikilink 计数（检查两个方向）
  - `cohesion = actual_links / (n × (n−1) / 2)`
- 标记任何标签组，其中凝聚力 < 0.15 且 n ≥ 5

**如何修复：**
- 运行针对分裂标签的 `cross-linker` 技能——它将显示并插入缺失的链接
- 如果标签组很大（n > 15）仍然分裂，请考虑将其拆分为更具体的子标签

### 9. 可见性标签一致性

检查 `visibility/` 标签是否正确应用，并且在需要的地方没有默默地缺少。

**如何检查：**

- **未标记的 PII 模式：** 在页面正文 Grep 常见的指示敏感数据的模式——包含 `password`、`api_key`、`secret`、`token`、`ssn`、`email:` 后跟实际值（不是字段描述）。如果一个页面匹配并且缺少 `visibility/pii` 或 `visibility/internal`，则将其标记为可能的错误分类。
- **`visibility/pii` 而没有 `sources:`：** 标记为 `visibility/pii` 的页面始终应具有 `sources:` frontmatter 字段——如果没有可验证分类的来源，则无法验证分类。标记任何缺少 `sources:` 的 `visibility/pii` 页面。
- **分类法中的可见性标签：** `visibility/` 标签是系统标签，**不** 应该出现在 `_meta/taxonomy.md` 中。如果找到，则将其标记为配置错误——它们会计算到包含它们的页面的 5 标签限制。

**如何修复：**
- 对于未标记的 PII 模式：将 `visibility/pii`（如果是团队上下文而不是个人数据，则为 `visibility/internal`）添加到页面的 frontmatter 标签
- 对于缺少 `sources:`：添加来源或升级给用户——不要自动填充
- 对于分类法污染：从 `_meta/taxonomy.md` 中删除 `visibility/` 条目

### 10. 其他晋升候选者

查找 `misc/` 中的页面，它们积累了足够的项目亲和力，可以晋升。

**如何检查：**
- Glob `$OBSIDIAN_VAULT_PATH/misc/*.md`
- 对于每个页面，读取 `affinity` frontmatter 字段
- 标记任何单个项目的分数 ≥ 3 的页面

**如何修复：**
- 首先运行 `/wiki-synthesize`，如果亲和度分数看起来过时（例如，页面有大量 wikilink 的 `affinity: {}`）
- 要晋升：将页面移动到 `projects/<project-name>/references/`（或另一个适当的类别），更新其 `category` frontmatter，删除 `promotion_status`，并 Grep 保险库以更新它们

### 12. 确信度和生命周期模式

强制执行置信度 + 生命周期 frontmatter 模式（参见 `llm-wiki/SKILL.md`，置信度和生命周期部分）。

两种模式：
- **`--check`**（默认，只读）——报告错误和警告
- **`--consolidate`**——可能应用单独批准的结构维护，但 **永远不** 重新编写 `base_confidence`

置信度是语义判断。确定性工具无法仅从来源字符串中推断独立的证据谱系或整个页面的声明覆盖范围。因此，置信度自动化验证了明确批准的手动信任分类账；它永远不会用 URL 计数来替代审查。

#### 规则 12a — `lifecycle` 枚举验证

**如何检查：** 在所有页面的 frontmatter 中 Grep `^lifecycle:`。标记任何不在有效生命周期集（框架默认值：`{draft, reviewed, verified, disputed, archived}`）中的值。

**如何修复：** n/a（只有人类应该设置生命周期状态）

#### 规则 12b — `base_confidence` 范围

**如何检查：** 在所有页面的 frontmatter 中 Grep `^base_confidence:`。标记任何超出 `[0.0, 1.0]` 的值；仅当有效所有者模式要求该字段时，才标记缺失的值。

**如何修复：** n/a（错误的值意味着技能计算它错误——需要手动更正）

#### 规则 12c — 过期页面报告（计算覆盖层）

过期从未存储——它在读取时计算：`is_stale = (today − updated) > 90 days`。

**如何检查：** 对于每个页面，从 frontmatter 中读取 `updated:` 并计算 `is_stale`。如果过期，则还检查 `lifecycle:`。报告：
- `lifecycle: verified` 的过期页面带有更响亮的注释（这些是最危险的——高信任页面可能不正确）
- 所有其他过期页面作为标准警告

**如何修复：** `--fix` 不重新编写 `lifecycle`。过期会自动清除，当重新摄取将 `updated` 推高时

#### 规则 12c-2 — 非法生命周期转换

生命周期枚举是一个状态机，而不是自由形式的标签。`obsidian-wiki lint` 通过比较每个页面的当前 `lifecycle` 与其在 `_meta/trust-ledger.json` 中最后一次审查时记录的值来报告 `illegal_lifecycle_transitions`。

**标记：** 任何回退到 `draft` 的状态（只有摄取设置 `draft`），以及任何从 `archived` 的退出（终端——恢复是一个故意的、人类删除和重新创建的操作）。

**不标记：** `draft → verified`。分类账快照是稀疏的，因此两个审查之间可能发生了合法的中间 `reviewed`；标记它会在有效历史中触发警告。

默认情况下发出警告；在 `--strict-trust` 下失败。具有早于 `lifecycle` 字段的分类账条目的页面没有基线，将静默跳过。

**如何修复：** n/a——一个沿禁用边缘移动的页面意味着要么技能在不应设置 `lifecycle` 的情况下写入了 `lifecycle`，要么需要记录的人类转换。显示给人类解决。

#### 规则 12d — 超级使用完整性

**如何检查：** 对于每个具有 `superseded_by: "[[target]]"` 的页面：
- 验证目标页面是否存在
- 验证目标页面本身不是 `archived`（没有循环或链接链）
- 验证是否存在循环（A 继承 B，B 继承 A）
- 如果 `lifecycle != archived` 而 `superseded_by` 设置，则发出警告（状态不一致）

**如何修复：** n/a——标记供人类解决

#### 规则 12e — 置信度审查完整性

**如何检查：** 首先运行确定性分类账验证器：

```bash
obsidian-wiki trust-check "$OBSIDIAN_VAULT_PATH" --strict --json --pretty
```

使用 `--strict` 进行 CI 和计划门禁：过期的、未审查的或缺失页面的警告返回非零。如果没有 `--strict`，`trust-check` 保持只读报告命令，并且仅在硬分类账错误或分数不匹配时返回非零。

批准的分类账位于 `_meta/trust-ledger.json`。每个条目记录了人类审查的分数以及材料页面内容和证据元数据的 SHA-256 指纹。指纹不包括易变的管理 (`updated`, `base_confidence` 和生命周期转换字段)，因此时间戳仅编辑不会重新打开审查。

解释结果如下：

- `reviewed` — 当前材料指纹和存储的分数都与批准的审查匹配；不要从来源字符串重新计算。
- `stale` — 正文、摘要、来源、来源、标签或关系发生变化；执行新的手动谱系 + 声明覆盖审查。
- `unreviewed` — 页面没有批准的分类账条目；需要手动审查。
- `score_mismatches` — 材料内容仍然匹配，但存储的 `base_confidence` 与批准的值不同；lint 失败。
- `errors` — 分类账数据格式错误/缺失；lint 失败。

对于单独批准的完整保险库审查，请明确记录接受的状
