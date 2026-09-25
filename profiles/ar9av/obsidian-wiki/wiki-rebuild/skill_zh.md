# Wiki Rebuild — Archive, Rebuild, Restore

你正在对维基执行破坏性操作。始终先进行归档，并在继续操作前始终与用户确认。

## 开始前

1. **解决配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解析协议（内联 `@name` 覆盖 → 向上遍历 CWD 查找 `.env` → 全局配置 → 提示设置）。这会提供 `OBSIDIAN_VAULT_PATH` 和可选的 QMD 设置，例如 `QMD_WIKI_COLLECTION`
2. 阅读 `.manifest.json` 以了解当前状态
3. **确认用户的意图。** 此技能支持三种模式：
   - **仅归档** — 快照当前维基，不重建
   - **归档 + 重建** — 快照，然后从零重新处理所有来源
   - **恢复** — 恢复之前的归档

## 归档系统

归档位于 `$OBSIDIAN_VAULT_PATH/_archives/`。每个归档是一个带时间戳的目录，其中包含该时间点维基状态的完整副本。

```
$OBSIDIAN_VAULT_PATH/
├── _archives/
│   ├── 2026-04-01T10-30-00Z/
│   │   ├── archive-meta.json
│   │   ├── concepts/
│   │   ├── entities/
│   │   ├── skills/
│   │   ├── references/
│   │   ├── synthesis/
│   │   ├── journal/
│   │   ├── projects/
│   │   ├── index.md
│   │   ├── log.md
│   │   └── .manifest.json
│   └── 2026-03-15T08-00-00Z/
│       └── ...
├── concepts/          ← 活维基
├── entities/
└── ...
```

### archive-meta.json

```json
{
  "archived_at": "2026-04-06T10:30:00Z",
  "reason": "rebuild",
  "total_pages": 87,
  "total_sources": 42,
  "total_projects": 6,
  "vault_path": "$OBSIDIAN_VAULT_PATH",
  "manifest_snapshot": ".manifest.json"
}
```

## 模式 1：仅归档

当用户想要快照当前状态而不重建时。

### 步骤：

1. 创建归档目录：`_archives/YYYY-MM-DDTHH-MM-SSZ/`
2. 将所有分类目录、`index.md`、`log.md`、`.manifest.json` 和 `projects/` 复制到归档中
3. 写入 `archive-meta.json`，原因设置为 `"snapshot"`
4. 追加到 `log.md`：
   ```
   - [TIMESTAMP] ARCHIVE reason="snapshot" pages=87 destination="_archives/2026-04-06T10-30-00Z"
   ```
5. 可选地刷新 QMD，如果 `log.md` 被索引且配置了 `QMD_WIKI_COLLECTION`（见“维基实时更改后的 QMD 刷新”）。
6. 报告： "归档了 87 页。当前维基未受影响。"

## 模式 2：归档 + 重建

当用户想要从零开始时。这是完整序列：

### 第 1 步：归档当前状态

与模式 1 相同，但原因设置为 `"rebuild"`。

### 第 2 步：清除实时维基

删除分类目录（`concepts/`、`entities/`、`skills/` 等）和 `projects/` 目录中的所有内容。保留：
- `_archives/`（显然）
- `.obsidian/`（Obsidian 配置）
- `.env`（如果存在于 vault 中）

将 `index.md` 重置为空模板。将 `log.md` 仅重置为重建条目。删除 `.manifest.json`（它将在摄取过程中重新创建）。

### 第 3 步：重建

告知用户 vault 已清除并准备好进行完整重新摄取。现在他们可以运行：

1. `wiki-status` — 查看所有来源均为 "new"
2. `claude-history-ingest` — 重新处理 Claude 历史记录
3. `codex-history-ingest` — 重新处理 Codex 会话历史记录
4. `wiki-ingest` — 重新处理文档和任何其他原始数据

这些将逐一重建清单。

**重要提示：** 不要自动运行摄取。用户应选择要重新摄取的内容和顺序。某些来源可能不再相关。

### 第 4 步：记录重建

追加到 `log.md`：
```
- [TIMESTAMP] REBUILD archived_to="_archives/2026-04-06T10-30-00Z" previous_pages=87
```

在清除和记录实时维基后刷新 QMD（见“维基实时更改后的 QMD 刷新”），然后报告 vault 已准备好进行选定的重新摄取技能。

## 模式 3：从归档恢复

当用户想要回到先前状态时。

### 第 1 步：列出可用归档

读取 `_archives/` 目录。对于每个归档，读取 `archive-meta.json` 并呈现：

```markdown
## 可用归档

| 日期 | 原因 | 页面 | 来源 |
|---|---|---|---|
| 2026-04-06 10:30 | rebuild | 87 | 42 |
| 2026-03-15 08:00 | snapshot | 65 | 31 |
```

### 第 2 步：确认要恢复哪个归档

询问用户他们想要哪个归档。警告他们恢复将覆盖当前实时维基。

### 第 3 步：首先归档当前状态

在恢复之前，先归档当前状态（原因：`"pre-restore"`），这样就不会丢失任何内容。

### 第 4 步：恢复

1. 清除实时维基（与模式 2，第 2 步相同）
2. 将所选归档的所有内容复制回实时维基目录
3. 从归档恢复 `index.md`、`log.md` 和 `.manifest.json`
4. 追加到 `log.md`：
   ```
   - [TIMESTAMP] RESTORE from="_archives/2026-03-15T08-00-00Z" pages_restored=65
   ```

### 第 5 步：报告

恢复后刷新 QMD（见“维基实时更改后的 QMD 刷新”），然后告诉用户已恢复的内容，并建议运行 `wiki-lint` 检查恢复状态是否存在任何问题。

## 维基实时更改后的 QMD 刷新

QMD 是一个搜索索引，不是真相来源。如果 QMD 刷新失败，不要回滚归档、重建或恢复工作；报告失败并保留 markdown vault 完好无损。

**GUARD：如果 `$QMD_WIKI_COLLECTION` 为空或未设置，跳过此步骤。**

何时运行：

| 模式 | 刷新 QMD？ | 原因 |
|---|---|---|
| 仅归档 | 可选 | 实时维基内容除 `log.md` 外未更改；如果 `log.md` 被索引且 QMD 已配置，则刷新 |
| 归档 + 重建 | 清除实时维基后必需 | QMD 必须忘记已删除的页面，否则它将返回过时的搜索结果。稍后的摄取技能将在重新处理来源时再次刷新 |
| 恢复 | 恢复后必需 | 实时维基已被归档内容替换，因此 QMD 必须与恢复状态匹配 |

当前刷新需要本地 QMD CLI。如果设置了 `$QMD_CLI`，则使用 `$QMD_CLI`；否则使用 `qmd`。如果 CLI 不可用，报告 `QMD skipped: qmd CLI unavailable`。

对于 CLI 刷新：

```bash
${QMD_CLI:-qmd} update
```

如果输出表示需要新哈希的向量，或者如果恢复替换了实时页面且嵌入可能已过时，运行：

```bash
${QMD_CLI:-qmd} embed
```

验证维基集合是否反映了操作：

```bash
${QMD_CLI:-qmd} ls "$QMD_WIKI_COLLECTION"
```

对于恢复，如果归档有已知页面路径，也验证一个恢复的页面：

```bash
${QMD_CLI:-qmd} get "qmd://$QMD_WIKI_COLLECTION/<restored-page>.md" -l 5
```

在最终报告中记录 QMD 刷新为以下之一：
- `QMD refreshed: update + embed + verified`
- `QMD refreshed: update only + verified`
- `QMD skipped: QMD_WIKI_COLLECTION unset`
- `QMD skipped: archive-only live content unchanged`
- `QMD skipped: qmd CLI unavailable`
- `QMD failed: <short error summary>`

## 安全规则

1. **在破坏性操作前始终归档。** 没有例外。
2. **在清除实时维基前始终与用户确认。**
3. **除非用户明确要求，否则永不删除归档。** 归档是廉价的保险。
4. **`.obsidian/` 目录是神圣的。** 在归档/重建/恢复期间切勿触碰它——它包含用户的 Obsidian 设置、插件和主题。
5. 如果在重建过程中出问题，归档就在那里。告诉用户他们可以恢复。
