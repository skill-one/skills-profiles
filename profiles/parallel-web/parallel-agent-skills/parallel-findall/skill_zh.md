# FindAll：实体发现

Find：$ARGUMENTS

> 需要 `parallel-cli` ≥ 0.6.0（`findall entity-search` 命令是在 0.6.0 中添加的；更广泛的 `findall` 命令是在 0.3.0 中添加的）。如果其中任何一个出现 `no such command` 或类似的错误，请提示用户运行 `parallel-cli update`（如果通过 pipx 安装，则运行 `pipx upgrade parallel-web-tools`），然后重试。

## 何时使用此技能

当用户需要一个符合描述的**结构化实体列表**，而不是网页或叙述性答案时，使用 FindAll。

| 用户请求… | 使用 |
|---|---|
| "查找所有 X…" / "列出每个 Y…" | **parallel-findall**（此技能） |
| 网页结果 / 快速答案 / 当前信息 | parallel-web-search |
| 叙述报告 / 分析 / "研究 X" | parallel-deep-research |
| 向已有的列表添加字段 | parallel-data-enrichment |

如果用户已经有一个列表，只是想添加字段，这个技能是不合适的——使用 parallel-data-enrichment。

FindAll 有两条路径：全面的异步 `findall run`（步骤 1-2）和快速同步的 `entity-search`（最后一部分）。

- **`entity-search`** — 非常快（几秒钟），仅支持人或公司搜索。支持更有限的查询参数集。针对召回率而非精确度进行优化；结果不会逐个验证。
- **`findall run`** — 提供全面覆盖，复杂匹配条件、排除项、丰富、引用或除人/公司之外的其他类型。

如果存在歧义，询问用户他们更喜欢哪种，并提供默认选项。记住实体搜索的限制：仅支持公司/人，没有排除项/生成器/丰富，且 `entity_set_id` 不能与 `enrich`/`extend`（如有需要，通过 `findall run` 重新运行）一起使用。

仅在用户明确表示他们需要一个快速、一次性列表时，才切换到 `entity-search`。`entity-search` 也有严格的限制：它仅支持 `companies` 或 `people` 实体类型，没有排除项，没有生成器选择，没有丰富，并且返回的 `entity_set_id` **不**可用于 `findall enrich`/`extend`。如果你从这里开始，而用户后来要求丰富或扩展，你将不得不通过 `findall run` 重新运行。

## 步骤 1：开始运行

```bash
parallel-cli findall run "$ARGUMENTS" --no-wait --json
```

默认值：生成器 `core`，匹配限制 `10`。除非用户有理由升级，否则坚持使用 `core`：

- `-g pro` — 最全面的生成器（较慢，成本更高）。当用户要求“全面”覆盖或 `core` 上的匹配稀疏时使用
- `-g base` — 最快，但**明显质量较低**。通常返回查询回声实体（例如，目录页面、字面查询字符串），没有 URL 的条目或类别占位符。仅在用户明确要求快速扫描并接受噪音时使用；否则优先使用 `core`
- `-n 50` — 返回最多 50 个匹配实体（允许 5-1000）

如果用户想排除已知实体（例如，“查找竞争对手，但不是 Google 或 OpenAI”）：

```bash
parallel-cli findall run "$ARGUMENTS" --no-wait --json \
    --exclude '[{"name":"Google","url":"google.com"},{"name":"OpenAI","url":"openai.com"}]'
```

提示——如果目标不明确，首先预览架构：`parallel-cli findall ingest "$ARGUMENTS" --json` 显示 API 推断的实体类型和匹配条件，以便在付费运行之前调整措辞。

解析 JSON 输出以提取 `findall_id` 和任何监控 URL。告诉用户：

- 已开始 FindAll 运行
- 大致频率（`core` 为分钟，`pro` 更长）
- 他们可以在运行时继续工作

## 步骤 2：轮询结果

选择一个描述性的文件名（例如，`series-a-ai-2026`，`charlotte-roofers`）。使用小写字母和连字符，不要有空格。

```bash
parallel-cli findall poll "$FINDALL_ID" -o "/tmp/$FILENAME.json" --timeout 540
```

重要：

- 使用 `--timeout 540`（9 分钟）以保持在工具执行限制内
- 不要为大型结果集传递 `--json`——它将淹没上下文。`-o` 将完整结果保存到磁盘

### 如果轮询超时

重新运行相同的 `parallel-cli findall poll` 命令以继续等待。服务器端运行继续进行，无论是否超时。

## 响应格式

在展示匹配项之前，**过滤结果**以去除明显的噪音：

- 删除 `url` 为空/缺失的条目
- 删除 `name` 与用户查询回声的条目（例如，字面量 "YC W25 批次开发工具公司”）——这些是搜索结果占位符，不是真实实体
- 删除 `url` 是第三方目录或个人资料页面，而不是实体自己的域的条目。URL 应该是实体自己拥有的（其产品网站、文档或营销网站）

如果过滤掉了一部分有意义的匹配项，请告知用户并建议使用 `-g pro` 或更高的 `-n` 重新运行。

**检查 `-g base` 结果。** 基础生成器可能会虚构分类属性（例如，将一个 YC S22 公司作为 YC W25 匹配项返回）。上述过滤规则仅检测 URL/名称形状，而不是事实正确性。如果用户的查询具有可证伪的属性（特定的批次、年份、地理区域等），请对照源 URL 检查保留的条目，并标记任何不符合的条目。如果**任何**保留的条目未通过抽查，**或者**噪音过滤掉了一部分有意义的匹配集（例如，≥40%），建议使用 `-g core`（或更高）重新运行——这都表明 `base` 对此查询没有产生可靠的结果。

将剩余的（真实的）实体以 Markdown 表格或列表的形式呈现。先显示数量，然后列出每个实体的名称、URL 和如果有的话，一句话描述。每个实体都应引用其源 URL。

告诉用户：

- 匹配了多少个实体（如果有，还过滤了多少个噪音实体）
- 完整结果路径（`/tmp/$FILENAME.json`）
- 他们可以：
  - 向这些结果添加字段，例如：

    ```bash
    parallel-cli findall enrich $FINDALL_ID '{"properties":{"ceo":{"type":"string"},"employee_count":{"type":"number"}}}'
    ```

    模式是一个 JSON Schema 风格的对象，`properties` 映射字段名 → `{type, description?}`。
  - 获取更多匹配项：`parallel-cli findall extend $FINDALL_ID 50`

## 快速实体搜索

**仅在用户明确表示他们需要一个快速/粗略/预览列表时使用**——不要仅仅因为实体类型恰好是 `companies` 或 `people` 就选择它。

同步调用。没有轮询，没有 `findall_id`。选择描述性的 `$FILENAME`（小写字母、连字符、无空格），如步骤 2 中所述。

```bash
parallel-cli findall entity-search "$ARGUMENTS" -t companies -n 100 -o "/tmp/$FILENAME.json"
```

标志：

- `-t companies|people` — 实体类型（必需）。该端点仅支持这两个；对于其他任何类型，请使用 `findall run`
- `-n 5..1000` — 匹配限制（默认 `10`）。在可能的情况下，请求比用户需要的更多（例如 `-n 100`），然后进行过滤——结果按相关性排序，但不会逐个验证，低限制可能会遗漏相关实体
- 不要为大型结果集传递 `--json`——它将淹没上下文。`-o` 将完整结果保存到磁盘

避免在此路径上设置过于严格的目標：API 会向限制填充，因此相关性在尾部会下降。保留核心标准在目标中，并在下游过滤其余部分，或使用 `findall run`。

响应形状：

```json
{ "entity_set_id": "entity_set_…", "entities": [ {"name": "...", "url": "...", "description": "..."},
… ] }
```

与完整路径不同，`entity-search` 返回的 `url` 通常是目录/个人资料链接——这是预期的，不是噪音。不要删除它们；仅过滤掉 `url` 为空或 `name` 与查询回声的条目。

将保留的实体以 Markdown 表格或列表的形式呈现，先显示数量，并引用每个实体的源 URL。告诉用户：

- 返回了多少个实体（以及过滤掉了多少个噪音实体）
- 如果使用了 `-o`，则提供完整结果路径（`/tmp/$FILENAME.json`）

## 设置

需要 `parallel-cli`（已安装并认证）。如果 `parallel-cli --version` 失败，或者如果后续命令因认证错误而失败，请告诉用户查看 <https://docs.parallel.ai/integrations/cli> 并停止。
