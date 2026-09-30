---
name: wiki-capture
description: 将当前对话保存为永久、结构化的维基笔记。当用户说“保存这个”、“/wiki-capture”、“捕捉这个”、“归档此对话”、“保留这个”、“将这个添加到我的维基”或希望将刚刚讨论的内容转化为持久知识时，使用此技能。该技能对内容进行分类，将其改写为陈述性知识（而非聊天记录），并将其放置在正确的保险库类别中。此外，还支持快速QUICK模式（`/wiki-capture --quick`、“快速捕捉”、“捕捉这个发现”、“保存这个bug修复”、“保存这个gotcha”、“丢弃到原始数据”、“快速保存到维基”），该模式在60秒内将发现内容丢弃到`_raw/`暂存区，无需写入清单或索引——由会话结束的Stop钩子自动保留发现内容。支持通过共享的配置解析协议进行内联命名保险库路由，例如“@research 保存这个”。
---

# Wiki Capture — 对话转换为维基笔记

你正在将当前对话中的知识保存为永久的维基笔记。目标是提取*实质*——即知识本身——而不是谈话内容的摘要。

**写作配置文件：** 在任何模式下起草或重写自然语言 Markdown 之前，请阅读并应用 `llm-wiki/SKILL.md` 中的 `Writing Profile Resolution` 部分。框架模式、来源、安全性和特定操作要求优先。
`WRITING.md` 的偏好仅适用于新起草或重写的自然语言 Markdown；保留源内容和结构化记录。

这项技能有三种模式：

- **完整模式（默认）** — 对内容进行分类，并直接写入正确的类别中，生成一个完成的、交叉链接的维基页面。这是本文档的其余部分（步骤 1–7）。
- **快速模式 (`--quick`)** — 无摩擦的暂存：在 60 秒内将发现结果放入 `_raw/` 中，不进行任何 manifest/index/log/QMD 写入。用于会话中的中间捕获，并由会话结束的停止钩子使用。见下文，然后停止——**不要**运行完整模式的步骤。
- **修正模式 (`--correction`)** — 将一个原子性修正捕获为衍生知识，同时保持不可变对话/来源不变。使用下面的模板，然后仅更新衍生消费者和跟踪链接。

## 快速模式 (`--quick`)

在作为 `/wiki-capture --quick` 调用时触发，通过“快速捕获”、“捕获此发现”、“保存此错误修复”、“保存此陷阱”、“放入原始文件夹”、“快速保存到维基”或自动由会话结束的停止钩子触发。

**速度合同：** 仅限内联。没有子代理。没有 QMD。没有 manifest/`index.md`/`log.md`/`hot.md` 写入。目标：<60 秒。提升为完整维基页面稍后通过 `/wiki-ingest` 完成。

1. **解析配置**（`llm-wiki/SKILL.md` 中的配置解析协议）：获取 `OBSIDIAN_VAULT_PATH` 和 `OBSIDIAN_RAW_DIR`（默认：`$OBSIDIAN_VAULT_PATH/_raw`）。确保 `$OBSIDIAN_RAW_DIR` 存在；如果不存在，则创建它。

   捕获不会独立地重新解释验证器模式输入。当 `OBSIDIAN_ALLOWED_LIFECYCLES`、`OBSIDIAN_ALLOWED_RELATIONSHIP_TYPES`、`OBSIDIAN_REQUIRED_TRUST_FIELDS` 或 `OBSIDIAN_SCHEMA_SOURCE` 存在时，保留它以供下游的 lint/trust 消费者使用：CLI 值优先于环境/配置值，环境/配置值优先于框架默认值，显式的空值或仅包含空白的值会失败。省略变量以使用默认值。

2. **门控——保留还是跳过？** 在提取之前，判断此会话是否有捕获价值。这使技能在自动调用时保持安全，而不会向 `_raw/` 发送垃圾信息。
   - **跳过**（退出并显示“此会话中没有值得捕获的内容。”）如果所有以下情况都为真：对话纯粹是谈话性的（计划/问答/解释），没有实施；没有错误、调试或问题解决；没有令人惊讶或不文档化的内容；每个发现都已经在文档中显而易见。
   - **保留**（继续）如果以下任何一项为真：通过调查发现了修复或解决方案；确认了非显而易见的库/API/框架行为（边缘情况、未记录的约束、耗时陷阱）；调试会话达到了具体结论；出现了一个可重用的模式。
   - 当通过停止钩子调用时，**倾向于跳过**——只有在有明确证据的情况下才保留。当手动调用时，**倾向于保留**——用户调用它是有原因的。

3. **扫描可重用发现**——非显而易见的错误和根本原因、框架/库陷阱、令人惊讶的 API 行为、调查中的解决方案、环境/工具链怪癖、调试中的模式。跳过 PM 更新、已存在于 CLAUDE.md 中的配置、不明确的来回交流、从文档中显而易见的内容和客套话。如果没有任何实质性内容出现，请说明并停止。

4. **按主题聚类**——每个主题聚类一个 `_raw/` 文件，而不是每个发现一个。将每个文件命名为 kebab-case slugs（例如 `swift-actor-reentrancy`、`nextjs-hydration-mismatch`）。

5. **从仓库名称、文件路径、框架提及、错误消息中推断项目上下文**。使用你可以可靠推断的最具体名称；否则为 `null`。

6. **写入原始文件**——对于每个聚类，写入 `$OBSIDIAN_RAW_DIR/<ISO-date>-<slug>.md`。阅读 `references/RAW-FORMAT.md` 获取完整的 frontmatter 规范、finding-block 身体结构和来源/信心校准。每个聚类的可变字段：`title`、`tags`（来自分类的 2–4 个）、`summary`（≤200 字符）、`project`（推断或 `null`）、`base_confidence`（0.6 讨论 → 0.75 修复应用 → 0.9 测试确认）、`provenance.extracted`/`provenance.inferred`（总和为 1.0）、`lifecycle_changed`（今天）、`sources`（`"<project> session (<YYYY-MM-DD>)"`）。

7. **确认**——列出暂存文件并告诉用户运行 `/wiki-ingest` 来提升它们：
   ```
   暂存到 _raw/：
     _raw/2026-05-27-swift-actor-reentrancy.md   — "Actor reentrancy causes deadlock in async forEach"
   运行 /wiki-ingest 来将这些提升为完整的维基页面。
   ```
   快速模式故意**不**写入 manifest、`index.md`、`log.md`、`hot.md` 或刷新 QMD——提升通过 `/wiki-ingest` 处理所有这些。**在此停止；不要运行下面的完整模式步骤。**

---

## 修正模式 (`--correction`)

当用户或更强权威修正了从不可变对话、工具结果或其他原始来源派生的声明时，使用此模式。永远不要编辑或复制原始来源。解析配置，阅读保险库 `AGENTS.md`，并在拥有声明时更新现有的衍生页面；否则创建最小的符合所有者要求的衍生修正页面。

记录恰好一个原子性声明对。`speaker_type` 是语义的，必须独立于序列化的消息 `role`（工具结果可能序列化为 `role=user`）进行评估。不要包含原始转录摘录。

```yaml
correction_id: <稳定 ID>
source_locator: <不可变文件:行或频道/线程/时间戳>
source_text_sha256: <64 小写字符十六进制>
serialized_role: <来源角色，如果存在>
speaker_type: user | assistant | teammate | tool_result | slack_member
original_claim:
  subject: <精确实体或功能>
  assertion: <单个原子值>
corrected_claim:
  subject: <相同的精确实体或功能>
  assertion: <单个原子值或 null>
authority_class: contract | decision | code | test | deploy | runtime | db | narrative
verification_state: verified | inferred | unverified | contradicted
asserted_at: <ISO-8601 时间戳>
effective_at: <ISO-8601 时间戳或 null>
as_of: <ISO-8601 时间戳>
supersedes: [<原始声明 ID>]
consumer_propagation:
  kw: open | not_applicable | complete
  ob: open | not_applicable | complete
  requirements: open | not_applicable | complete
  code: open | not_applicable | complete
  tests: open | not_applicable | complete
  ai_memory: open | not_applicable | complete
corrected_at: <ISO-8601 时间戳>
```

在任何衍生写入之前，直接从不可变来源计算 `source_pre_sha256`，并要求它等于 `source_text_sha256`。在写入修正并更新衍生消费者后，从相同的定位器重新计算 `source_post_sha256`。如果 `source_pre_sha256 == source_post_sha256 == source_text_sha256` 不成立，则中止并报告不可变性违规。即使修正写入成功，此验证也是强制性的。

在写入衍生修正后，通过 `.manifest.json` 将不可变来源链接到创建/更新的页面，仅将修正 ID 和受影响页面计数追加到 `log.md`，并独立地将原子性修正传播到每个消费者。只有在验证了该消费者后，才将其标记为 `complete`；不要将混合结果合并为单个聚合状态。将秘密、原始摘录和来源副本排除在修正记录之外。

---

## 完整模式

## 开始之前

1. **解析配置**——遵循 `llm-wiki/SKILL.md` 中的配置解析协议（内联 `@name` 覆盖 → 沿 CWD 向上查找 `.env` → 全局配置 → 提示设置）。这提供了 `OBSIDIAN_VAULT_PATH` 和 `OBSIDIAN_LINK_FORMAT`（默认：`wikilink`）。
2. 阅读 `$OBSIDIAN_VAULT_PATH/index.md` 以了解现有的维基内容（避免重复）
3. 如果存在，阅读 `$OBSIDIAN_VAULT_PATH/hot.md`——它提供了关于最近活动的上下文

在步骤 5 中编写内部链接时，使用 `llm-wiki/SKILL.md`（链接格式部分）中的链接格式，使用 `OBSIDIAN_LINK_FORMAT` 值。

## 步骤 1：识别值得保留的内容

扫描对话。问：在这里出现了哪些知识，即使没有记住这次聊天，3 个月后也仍然有价值？

值得保留：
- 做出的决定及其原因
- 分析、框架、心智模型
- 技术发现、模式或程序
- 对主题的综合理解
- 清晰解释的概念，这些概念需要付出努力才能得出
- 讨论中讨论的外部来源的关键事实

跳过：
- 物流、日程安排、客套话
- 探索性的来回交流，没有达成结论
- 已经在维基中的内容

如果没有任何实质性内容出现，告诉用户并停止。

## 步骤 2：对内容类型进行分类

分配五种类型之一——这决定了目标文件夹和语气：

| 类型 | 描述 | 目标文件夹 |
|---|---|---|
| `synthesis` | 多步骤分析或需要推理的特定问题的答案 | `synthesis/` |
| `concept` | 定义、框架或心智模型（某物*是什么*） | `concepts/` |
| `source` | 讨论的外部文档、文章或资源的摘要 | `references/` |
| `decision` | 战略、架构或设计选择及其理由 | `synthesis/` |
| `session` | 当对话跨越多个主题时的完整讨论摘要 | `journal/` |

如果内容明显属于特定项目（从上下文或用户提及中检测到），则将其放在 `projects/<project-name>/<category>/` 下。

## 步骤 3：重写为声明性知识

**不要**编写对话摘要。编写知识本身，使用现在时态的声明性语言：

- 不是：“用户询问了 X，Claude 解释说……”
- 是：“X 通过……工作。”
- 不是：“我们决定使用 Y，因为……”
- 是：“Y 优先于 Z，因为 [原因]。 [^[inferred] 如果推理是暗示的，而不是明确陈述的]”

应用 `llm-wiki` 的来源标记：
- *提取*——在对话中明确陈述（无标记）
- *推断*——从对话中泛化或综合 → `^[inferred]`
- *模糊*——有争议、不确定或矛盾 → `^[ambiguous]`

## 步骤 4：生成 Slugs 和标题

从内容中推导出清晰的、描述性的标题，并将其 slugs 化：
- 全小写，单词之间用连字符分隔
- 最大 50 个字符
- 避免在 slugs 中包含日期（frontmatter 有 `created`）

## 步骤 5：编写维基笔记

在目标路径创建文件并包含所需的 frontmatter：

```yaml
---
title: >-
  <标题>
category: <synthesis|concepts|references|journal|skills>
tags: [<2-5 来自分类的领域标签>]
sources:
  - conversation:<ISO-日期>
created: <ISO-8601 时间戳>
updated: <ISO-8601 时间戳>
summary: >-
  <1-2 句话，≤200 字符，回答“此页面包含哪些知识？”>
provenance:
  extracted: 0.X
  inferred: 0.X
  ambiguous: 0.X
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: <今天 ISO 日期>
---
```

按类型划分的正文结构：

**synthesis / decision:**
```markdown
# 标题

## 背景
<是什么促使了这一点——正在解决的问题或问题>

## 发现 / 决定
<核心知识或结论>

## 推理
<为什么这是事实或为什么做出了这个选择>

## 影响
<随之而来的——要关注的、下一步、权衡>

## 相关
<[[维基链接]]到相关页面>
```

**concept:**
```markdown
# 标题

<用一句话清晰定义。>

## 它是什么
<概念的解释>

## 它如何工作
<机制或结构>

## 何时使用
<适用性、条件、权衡>

## 相关
<[[维基链接]]>
```

**source:**
```markdown
# 标题

> 来源：<标题或 URL>

## 它涵盖什么
<来源是关于什么的>

## 关键点
<带来源标记的编号声明>

## 开放性问题
<它提出但没有回答的问题——如果没有，则省略>

## 相关
<[[维基链接]]>
```

**session:**
```markdown
# 标题

*会话捕获：<日期>*

## 涵盖的主题
<简要列表>

## 关键要点
<最重要的 3-5 件出现的事情>

## 做出的决定
<任何明确的决定，附带理由>

## 开放性问题
<尚未解决的问题>

## 相关
<[[维基链接]]>
```

每个笔记必须至少链接到 2 个现有的维基页面。在编写之前搜索 `index.md`。如果少于 2 个相关页面，请为最重要的参考概念创建最小的占位符。

## 步骤 5b：更新所有者配置文件和待办事项索引

记忆表面只有写得进去才够好。这是保持其活力的步骤——没有它，配置文件将保持为空，会话回顾将没有内容可以注入。

**关于个人的持久事实。** 如果对话揭示了一些关于用户如何工作的稳定信息——他们的技术栈、他们的约定、他们的限制、他们的时区——请记录它：

```bash
obsidian-wiki memory profile set <key> "<value>" --confidence 0.85 --source "session:<日期>"
```

应用与步骤 1 相同的 KEEP/SKIP 纪律，并应用一个更重要的规则：

- **仅用户实际告诉你的内容**，直接或通过清晰的演示。
  永远不要从已导入的文档中推断关于个人的持久事实——那是文档的内容，不属于他们的配置文件，而应出现在页面中。
- **稳定，而不是偶然。** “使用 Postgres”是一个事实。“今天运行了迁移”是一个事件；那属于日志。
- **校准信心。** 明确陈述的是 ~0.9。反复演示的是 ~0.75。从一个会话的行为中推断的是 ~0.5——如果你低于 0.5，就不要写它。
- **修正，不要重复。** `profile set` 替换现有的键，因此更新已更改的事实是相同的命令。

**开放性线索。** 如果对话留下了未完成的工作，请记录它，以便下次会话接手：

```bash
obsidian-wiki memory todo add "<开放的线索>" --origin "<页面或项目>"
```

用相同的文本重新添加开放的线索会更新它而不是重复，所以当你不确定它是否已经存在时，这是安全的。如果对话*关闭*了一个已列出的线索，请关闭它：

```bash
obsidian-wiki memory todo list --vault "$OBSIDIAN_VAULT_PATH"
obsidian-wiki memory todo done <id>
```

永远不要关闭用户没有实际完成的线索。陈旧性由工具报告；这不是你的工作来整理列表。

**在快速模式中**，执行此步骤，但跳过步骤 6——配置文件和待办事项写入是廉价的、锁定的，并且是捕获的整个目的。

## 步骤 6：更新跟踪文件

一个锁定的调用会更新所有三个：

```bash
obsidian-wiki memory sync CAPTURE \
  type=<类型> page="<路径>" title="<标题>" \
  --takeaways "<这次捕获改变了整体画面，如果有的话>"
```

永远不要手动编辑 `index.md`、`log.md` 或 `hot.md`——见 `.skills/llm-wiki/references/MEMORY.md`。当捕获不会改变整体画面时，省略 `--takeaways`；之前的 takeaways 会继续。

## 步骤 7：向用户确认

报告保存的路径和标题：
```
保存到：projects/<名称>/synthesis/<slugs>.md
标题：<标题>
类型：synthesis
```

## 质量检查清单

- [ ] 内容重写为声明性知识（不是聊天记录）
- [ ] 类型分类正确；目标路径在正确的文件夹中
- [ ] frontmatter 完整，包括标题、类别、标签、来源、摘要、来源
- [ ] 至少有 2 个链接到现有页面
- [ ] `index.md`、`log.md` 和 `hot.md` 已更新
- [ ] 向用户确认保存路径

## QMD 刷新后保险库写入

QMD 是一个搜索索引，而非事实来源。如果 `$QMD_WIKI_COLLECTION` 为空或未设置，则跳过此步骤。仅在当前技能写入或重写仓库名字标记后运行。如果 QMD 刷新失败，不要回滚仓库更改；单独报告 QMD 状态。

如果设置了 `$QMD_CLI`，则使用 `$QMD_CLI`；否则使用 `qmd`。

```bash
${QMD_CLI:-qmd} update
```

如果输出提示需要向量或嵌入可能已过期，请运行：

```bash
${QMD_CLI:-qmd} embed
```

使用以下任一方式验证集合：

```bash
${QMD_CLI:-qmd} ls "$QMD_WIKI_COLLECTION"
```

或者，当已知特定页面路径时：

```bash
${QMD_CLI:-qmd} get "qmd://$QMD_WIKI_COLLECTION/<page>.md" -l 5
```

记录以下之一：
- `QMD 刷新：update + embed + verified`
- `QMD 刷新：仅 update + verified`
- `QMD 跳过：QMD_WIKI_COLLECTION 未设置`
- `QMD 跳过：qmd CLI 不可用`
- `QMD 失败：<简短错误摘要>`
