# 标签分类法 — Wiki标签的受控词汇

您通过将标签规范化为受控词汇，来确保Wiki中标签的一致性。

## 开始前

1. **解决配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解析协议（内联 `@name` 覆盖 → 向上遍历当前工作目录查找 `.env` → 全局配置 → 提示设置）。这会提供 `OBSIDIAN_VAULT_PATH`
2. 阅读 `$OBSIDIAN_VAULT_PATH/_meta/taxonomy.md` — 这是标准的标签列表
3. 阅读 `index.md` 以了解Wiki的范围

## 分类法文件

标准的标签词汇位于 `$OBSIDIAN_VAULT_PATH/_meta/taxonomy.md`。它定义了：

- **标准标签** — 应该使用的标签
- **别名** — 常见的替代标签，应该映射到标准形式
- **规则** — 每页最多5个标签，小写/连字符，优先选择宽泛的标签而非狭窄的标签
- **迁移指南** — 已知不一致性的特定重命名

**在标签之前始终阅读此文件。** 它是事实来源。

## 保留的系统标签

`visibility/` 是一个具有特殊规则的保留标签组。这些标签**不是**域或类型标签，并且与分类法词汇分开管理：

| 标签 | 目的 |
|---|---|
| `visibility/public` | 明确公开 — 在所有模式下显示（与无标签相同） |
| `visibility/internal` | 仅限团队 — 在过滤查询/导出模式下排除 |
| `visibility/pii` | 敏感数据 — 在过滤查询/导出模式下排除 |

**`visibility/` 标签的规则：**
- 它们**不**计入5个标签的限制
- 每页**仅**有一个 `visibility/` 标签
- 当内容明显为公开时，完全省略 — 无需标签
- 不要因为内容是技术性的就添加 `visibility/internal`；仅用于真正仅限团队的知识
- 在运行标签审计时，单独报告 `visibility/` 标签的使用情况 — 不要将其标记为未知或非标准

在规范化标签时，保留 `visibility/` 标签 — 它们不适用于别名映射。

## 模式1：标签审计

当用户想要查看当前标签状态时：

### 第1步：扫描所有页面

```
Glob: $VAULT_PATH/**/*.md（排除 _archives/, .obsidian/, _meta/）
提取：来自YAML前导的标签字段
```

### 第2步：构建标签频率表

对于找到的每个标签，计算使用它的页面数量。标记：

- **未知标签** — 不在分类法标准列表中
- **别名标签** — 使用别名而不是标准形式（例如，`nextjs` 而不是 `react`）
- **过度标记的页面** — 标签超过5个的页面
- **未标记的页面** — 没有标签或空标签字段的页面

### 第3步：报告

```markdown
## 标签审计报告

### 摘要

- 总唯一标签：47
- 使用标准标签：32
- 发现非标准标签：15
- 超过标签限制（5）的页面：3
- 未标记的页面：2

### 发现的非标准标签

| 当前标签 | → 标准形式 | 影响页面 |
| ----------- | ----------- | -------------- |
| `nextjs`    | `react`     | 4              |
| `next-js`   | `react`     | 2              |
| `robotics`  | `ml`        | 1              |
| `windows98` | `retro`     | 3              |

### 未知标签（不在分类法中）

| 标签          | 页面 | 建议                   |
| ------------ | ----- | -------------------------------- |
| `flutter`    | 1     | 添加到分类法下的 Frameworks |
| `kubernetes` | 2     | 添加到分类法下的 DevOps     |

### 过度标记的页面

| 页面                   | 标签数量 | 标签                 |
| ---------------------- | --------- | -------------------- |
| `entities/jane-doe.md` | 8         | ai, ml, founder, ... |
```

## 模式2：标签规范化

当用户想要修复标签时：

### 第1步：运行审计（上述）

### 第2步：应用修复

对于每个具有非标准标签的页面：

1. 阅读页面
2. 将别名标签替换为分类法中的标准形式
3. 如果页面标签超过5个，建议删除哪些标签（保留最具体/相关的标签）
4. 写入更新的前导

**示例：**

```yaml
# 之前
tags: [nextjs, ai, ml-engineer, windows98, creative-coding, game, 8-bit, portfolio]

# 之后
tags: [react, ai, ml, retro, generative-art]
```

### 第3步：处理未知标签

对于不在分类法中且不是别名的标签：

- 如果标签在2个或更多页面上使用，建议将其添加到分类法
- 如果标签仅在一个页面上使用，建议用最接近的标准标签替换
- 在对未知标签进行更改之前询问用户

### 第4步：更新分类法

如果同意添加新的标准标签，请将其追加到 `_meta/taxonomy.md` 中的正确部分。

## 模式3：标记新页面

当您创建Wiki页面并需要选择标签时：

1. 阅读 `_meta/taxonomy.md`
2. 选择最多5个最能描述页面的标签：
   - 1-2 **域标签**（什么主题领域）
   - 1 **类型标签**（什么类型的东西）
   - 0-1 **项目标签**（如果项目特定）
   - 0-1 额外的描述性标签
3. 仅使用标准标签 — 永远不要使用别名
4. 如果没有现有标签适用，检查是否值得添加到分类法

## 模式4：添加新标签

当用户想要将标签添加到词汇表时：

1. 检查是否已有现有标签涵盖该概念（如果是，建议使用它）
2. 如果确实新，确定它属于哪个部分（域、类型、项目）
3. 将其添加到 `_meta/taxonomy.md`，包括：
   - 标准标签名称
   - 它的用途
   - 任何重定向的别名

## 任何标签操作后

一个锁定调用更新日志、索引（标签出现在索引条目中）和热缓存：

```bash
# 审计
obsidian-wiki memory sync TAG_AUDIT \
  tags_normalized=<N> unknown_tags=<M> pages_modified=<P> \
  --takeaways "标签审计：在28页中规范化了14个标签；添加了2个新的标准标签。"

# 规范化
obsidian-wiki memory sync TAG_NORMALIZE \
  tags_renamed=<N> pages_modified=<M> new_tags_added=<P>
```

永远不要手动编辑 `index.md`、`log.md` 或 `hot.md` — 命令会锁定，防止并行写入者丢弃您的更新。

有关完整过程，请参阅 `.skills/llm-wiki/references/MEMORY.md`。

## Vault写入后的QMD刷新

QMD是一个搜索索引，不是事实来源。如果 `$QMD_WIKI_COLLECTION` 为空或未设置，跳过此步骤。仅在此技能写入或重写Vault Markdown后运行它。如果QMD刷新失败，不要回滚Vault更改；单独报告QMD状态。

如果设置了 `$QMD_CLI`，请使用它；否则使用 `qmd`。

```bash
${QMD_CLI:-qmd} update
```

如果输出表示需要向量或嵌入可能已过时，运行：

```bash
${QMD_CLI:-qmd} embed
```

使用以下任一方式验证集合：

```bash
${QMD_CLI:-qmd} ls "$QMD_WIKI_COLLECTION"
```

或者，当知道特定页面路径时：

```bash
${QMD_CLI:-qmd} get "qmd://$QMD_WIKI_COLLECTION/<page>.md" -l 5
```

记录以下之一：
- `QMD refreshed: update + embed + verified`
- `QMD refreshed: update only + verified`
- `QMD skipped: QMD_WIKI_COLLECTION unset`
- `QMD skipped: qmd CLI unavailable`
- `QMD failed: <简短错误摘要>`
