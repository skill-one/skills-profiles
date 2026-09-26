# Wiki 阶段提交 — 阶段性写入提升

你正在审核等待在 `_staging/` 中等待人工批准的由 LLM 编写的页面，这些页面将在批准后进入线上维基。这项技能仅在 vault 配置中 `WIKI_STAGED_WRITES=true` 时有用。

## 开始前

1. **解析配置** — 按照 `llm-wiki/SKILL.md` 中的配置解析协议进行操作。这将提供 `OBSIDIAN_VAULT_PATH` 和 `WIKI_STAGED_WRITES`。
2. 如果 `WIKI_STAGED_WRITES` 未设置或为 `false`，请告知用户："阶段性写入模式未启用。请在 `.env` 中设置 `WIKI_STAGED_WRITES=true` 以使用此功能。" 然后停止。
3. 读取 `_staging/` 目录的清单。

## 调用形式

```
/wiki-stage-commit               # 交互式审核：显示每个文件并询问接受/拒绝
/wiki-stage-commit --all         # 无需逐文件审核即接受所有阶段性文件
/wiki-stage-commit --reject-all  # 拒绝所有阶段性文件（移动到 _raw/ 以供手动编辑）
/wiki-stage-commit --list        # 列出阶段性文件并显示摘要，无更改
```

## 第 1 步：清单阶段文件

CLI 拥有清单 — 不要自己 glob `_staging/`：

```bash
obsidian-wiki staging list --json
```

每个条目包含：

| 字段 | 含义 |
|---|---|
| `staged_path` | 阶段性文件的 vault 相对路径 |
| `live_path` | 将要放置的位置（`.patch.md` 针对其命名的页面） |
| `kind` | `new`、`update` 或 `patch` |
| `staged_revision` | 阶段性文件的内容哈希，即你现在看到的 |
| `live_revision` | 线上页面的内容哈希，或 `null`（如果尚未存在） |
| `staged_mtime` | 阶段性文件被阶段化时的日期 |

**为每个向用户展示的文件保留 `staged_revision` 和 `live_revision`。** 正是它们使得第 3 步拒绝覆盖代理的并发写入，而不是默默覆盖它。

报告清单：

```
阶段文件：4 个新页面，2 次更新

新页面：
  _staging/concepts/attention-mechanism.md        (阶段化于 2026-09-08)
  _staging/entities/andrej-karpathy.md            (阶段化于 2026-09-08)

更新：
  _staging/concepts/transformer-architecture.md   (目标：concepts/transformer-architecture.md)

补丁：
  _staging/skills/prompt-engineering.patch.md     (目标：skills/prompt-engineering.md)
```

如果列表为空，报告："无文件阶段化。所有写入已提交或尚未生成阶段化写入。"

## 第 2 步：逐文件审核（交互模式）

对于每个阶段文件（首先新页面，然后更新）：

### 对于新页面：

显示摘要：

```
--- 新页面：concepts/attention-mechanism.md ---
标题：    注意力机制
标签：     #ml #architecture
摘要：  变换器的核心构建块 — 基于查询-键相似性计算加权值和。
级别：     支持性
置信度：  0.72
来源：  papers/attention.pdf

[预览正文前 20 行]
...

接受 [a]、拒绝 [r]、跳过 [s]、预览全部 [p]？
```

### 对于补丁文件：

显示结构化差异：

```
--- 更新：concepts/transformer-architecture.md ---
来源：_staging/concepts/transformer-architecture.patch.md

建议添加 (+):
+ 变换器在需要长距离依赖的任务上优于 RNNs。 ^[推断]
+ 新来源：papers/survey-2026.pdf

建议删除 (-):
- 注意力机制最早由 [Bahdanau 2015] 描述。  (将被更新的声明替换)

⚠️  冲突检查：live_revision 不再匹配你阶段化时对比的内容。仔细审核。

接受 [a]、拒绝 [r]、跳过 [s]、预览全部差异 [p]？
```

如果设置了 `--all` 标志，则跳过提示并接受每个文件。
如果设置了 `--reject-all` 标志，则跳过提示并拒绝每个文件。
如果设置了 `--list` 标志，则在打印清单（第 1 步）后停止。

## 第 3 步：应用决策

移动操作是机械的，CLI 以原子方式执行它们。传递第 1 步的修订版本，以便在基于过时信息做出的决策时大声失败。

### 接受新页面

```bash
obsidian-wiki staging promote <staged_path> \
  --expect-staged <staged_revision> --expect-new
```

`--expect-new` 如果自你列出以来出现了线上页面，则会拒绝 — 别人先一步到达。

### 接受更新

```bash
obsidian-wiki staging promote <staged_path> \
  --expect-staged <staged_revision> --expect-live <live_revision>
```

### 拒绝文件

```bash
obsidian-wiki staging discard <staged_path>
```

它将移动到 `_raw/rejected-<category>-<page>.md` 以供手动编辑。对同一页面的先前拒绝永远不会被覆盖 — 第二个变为 `-2`。

### 接受补丁

`promote` 拒绝 `.patch.md` 文件，因为将人类可读的差异合并到其周围文本可能已移动的页面中是判断，而不是重命名。自己动手：

1. 读取目标页面和补丁。
2. 将 `+` 添加和 `-` 删除**作为合并**应用 — 永远不要整体覆盖页面。
3. 提升目标的 `updated` 前置元数据。
4. `obsidian-wiki staging discard <patch staged_path>` 以清除队列中的补丁。

### 当 CLI 报告冲突时

退出码 **9** 并在标准错误输出上显示 `conflict: ...` 表示自你列出后阶段化或线上文件已更改。没有文件被移动。不要盲目地用新修订版本重试 — 重新运行 `staging list`，向用户展示发生了什么，并再次询问。检查的整个目的是他们批准的内容不再是要落地的内容。

`index.md` 由阶段化页面的摄取更新，因此提升不会触及它。`log.md` 每次调用都会添加一条 `STAGE_COMMIT` 行，由 CLI 写入。

## 第 4 步：更新跟踪文件

CLI 本身将 `STAGE_COMMIT` 行追加到 `log.md`。处理所有阶段文件后，重新协调索引和热缓存，以便提升的页面出现：

```bash
obsidian-wiki memory sync --takeaways "已提交 N 个阶段化页面；拒绝 M 个。"
```

(没有 `--verb`：日志行已由 `staging promote` 写入。) 永远不要手动编辑 `index.md`、`log.md` 或 `hot.md` — 命令会获取锁，以防止并行写入者丢失你的更新。

## 第 5 步：报告

```
阶段提交完成。

✅  接受 (N):
  concepts/attention-mechanism.md     → 现在已上线
  entities/andrej-karpathy.md         → 现在已上线
  concepts/transformer-architecture.md → 更新（已应用补丁）

❌  拒绝 (M):
  skills/fine-tuning-llms.md          → 移动到 _raw/rejected-skills-fine-tuning-llms.md

⏭️  跳过 (K):
  references/attention-is-all-you-need.md → 仍在 _staging/

阶段队列：K 个文件剩余
```

## 注意事项

- 阶段化文件使用与线上页面相同的页面模板 — 它们已准备好落地，只需等待批准
- 补丁文件使用人类可读的差异格式：以 `+` 开头的行是添加，以 `-` 开头的行是删除。`staging promote` 拒绝它们 — 自己合并（第 3 步）
- `index.md` 和 `log.md` 总是在摄取时立即更新（它们是低风险的跟踪文件） — 只有分类页面会经过阶段化
- 移动操作位于 `obsidian_wiki/staging.py` 中；这项技能提供判断，而不是文件处理
- `_staging/` 目录不被 Obsidian 的图视图跟踪 — 页面仅在提升后才出现在维基中
