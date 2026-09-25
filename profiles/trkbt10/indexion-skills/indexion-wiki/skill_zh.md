# indexion wiki

indexion 的 wiki 系统在 `.indexion/wiki/` 目录维护一个知识库，它是一个由 Markdown 文件组成的集合，并由 `wiki.json` 元数据文件管理。

## wiki 页面不仅仅是 `.md` 文件

一个 wiki 页面由 **四个同步的组件** 组成：

| 组件 | 文件 | 更新方式 |
|------|------|----------|
| 页面内容 | `<id>.md` | `wiki pages add`, `wiki pages update` |
| 元数据条目 | `wiki.json` | `wiki pages add`, `wiki pages update` |
| 搜索索引 | `vectors.db`, `search-sections.json`, `tfidf-vocabulary.json` | `wiki pages update`, `wiki index build --full` |
| 审计日志 | `log.json` | 每个修改 wiki 的命令 |

**`wiki pages update` 会一次性更新所有四个组件。** 直接编辑 `.md` 文件只会更新第一个组件。其他三个组件会变得过时——搜索会返回旧的结果，元数据会携带错误的来源信息，而日志中没有记录变更。

如果你直接编辑 `.md` 文件（例如通过 `Edit` 工具），你必须立即跟进：

```bash
indexion wiki pages update \
  --id=<页面ID> \
  --content=.indexion/wiki/<页面ID>.md \
  --sources="<wiki.json 中的逗号分隔来源>" \
  --provenance=synthesized \
  --actor="agent:claude" \
  --wiki-dir=.indexion/wiki
```

每个 wiki 页面在元数据中还有两个字段记录来源信息：
- `provenance`: `"extracted"` | `"synthesized"` | `"manual"`
- `last_actor`: `"indexion"` | `"agent:<名称>"` | `"user"`

## 命令结构

```
indexion wiki
  ├── pages
  │   ├── plan    -- 提出页面结构（类似初始化）
  │   ├── add     -- 创建新页面（写入 .md + 元数据 + 索引 + 日志）
  │   ├── update  -- 更新现有页面（写入 .md + 元数据 + 索引 + 日志）
  │   └── ingest  -- 通过哈希来源检测过时的页面
  ├── index
  │   └── build   -- 重建 index.md（以及可选的 vectors.db）
  ├── lint        -- 结构完整性检查（无需 LLM）
  ├── export      -- 导出为 GitHub/GitLab wiki 格式
  ├── import      -- 从 GitHub/GitLab wiki 格式导入
  └── log         -- 操作审计记录
```

## 浏览 wiki（作为代理）

在阅读单个页面之前，先从索引开始：

```bash
# 生成或重新生成 index.md —— 导航的入口
indexion wiki index build --wiki-dir=.indexion/wiki

# 然后阅读它
cat .indexion/wiki/index.md
```

`index.md` 按类别列出页面，并标识 **中心页面**（链接最多的页面）。中心页面是理解不熟悉代码库的最佳起点。

## 创建新页面

```bash
# 1. 将内容写入临时文件
cat > /tmp/my-page.md << 'EOF'
# 我的页面标题
...内容...
EOF

# 2. 注册它——这将写入 .md, 更新 wiki.json, 更新搜索索引, 追加日志
indexion wiki pages add \
  --id=my-page \
  --title="我的页面标题" \
  --content=/tmp/my-page.md \
  --sources="src/my-module/" \
  --provenance=synthesized \
  --actor="agent:claude" \
  --wiki-dir=.indexion/wiki
```

`--sources` 字段将页面链接到源文件以进行变更跟踪。始终指定它——没有来源的页面对 `wiki pages ingest` 不可见。

## 更新现有页面

```bash
# 1. 将新内容写入临时文件
cat > /tmp/updated.md << 'EOF'
# 更新页面
...新内容...
EOF

# 2. 更新——这将覆盖 .md, 更新 wiki.json 元数据,
#    逐步更新搜索索引, 并追加到 log.json
indexion wiki pages update \
  --id=existing-page \
  --content=/tmp/updated.md \
  --sources="src/my-module/,src/other/" \
  --provenance=synthesized \
  --actor="agent:claude" \
  --wiki-dir=.indexion/wiki
```

预期输出：`更新页面 'existing-page'（搜索索引已更新）`

## 检测需要更新的内容

```bash
# 查找自上次运行以来源文件已更改的页面
indexion wiki pages ingest --wiki-dir=.indexion/wiki

# 不记录新哈希状态预览
indexion wiki pages ingest --dry-run --wiki-dir=.indexion/wiki
```

`ingest` 哈希 `wiki.json` 中列出的每个源文件，并与 `.indexion/wiki/ingest-manifest.json` 对比。它输出更新任务列表，但**不会**重写页面——那是代理的责任。

工作流程：
1. 运行 `wiki pages ingest` 获取任务列表。
2. 对于每个任务，阅读已更改的源文件。
3. 使用 `wiki pages update` 更新 wiki 页面。
4. 重新运行 `ingest` —— 它应该报告 0 个需要关注的页面。

## 验证结构完整性

```bash
# 运行所有 6 个结构检查
indexion wiki lint --wiki-dir=.indexion/wiki
```

| 检查 | 检查内容 |
|------|----------|
| 破坏链接 | `wiki://page-id` 引用不存在的页面 |
| 孤立页面 | 无法从导航树访问且未被任何其他页面链接的页面 |
| 缺失交叉引用 | 共享源文件的页面之间没有相互链接 |
| 过期来源 | `sources` 路径在磁盘上已不存在 |
| 空页面 | 内容接近零的页面 |
| 元数据文件不匹配 | `wiki.json` 条目没有 `.md` 文件（反之亦然） |

写入新页面后，始终运行 `wiki lint` 并在完成前修复任何问题。

交叉引用警告在相关概念分散在多个页面时很常见。通过添加 `## See Also` 部分并使用 `wiki://page-id` 链接来修复它们。

## 验证内容准确性 (`plan reconcile`)

`wiki lint` 捕获 **结构** 问题。`plan reconcile` 捕获 **语义** 走势——wiki 页面中描述的代码符号是否仍然存在，以及代码自上次写入页面以来是否已更改。

**始终针对项目根目录（`.`）。** `--doc` 标志限制参与文档，但目标目录决定了代码符号宇宙。针对子目录会缩小符号集并生成零碎片报告。

```bash
indexion plan reconcile \
  --doc='.indexion/wiki/*.md' \
  --doc-spec=markdown \
  --format=md \
  .
```

### 阅读报告

**摘要**——关键指标是 `New logical reviews`（自上次运行以来的新鲜走动）。

**建议的审查组**——可操作的核心理心：

| 类别 | 含义 | 操作 |
|------|------|------|
| `stale_doc` | 代码在 wiki 页面最后一次更新后已更改 | 通过 `wiki pages update` 更新页面 |
| `missing_doc` | 没有匹配 wiki 覆盖的代码符号 | 添加覆盖或通过 `wiki pages add` 创建新页面 |
| `review_both` | wiki 比代码更新 | 验证 wiki 内容是否正确；这是维护周期后的预期状态 |

每个组列出了受影响的符号和相关的 `Docs:` wiki 页面。没有 `Docs:` 行的组意味着没有 wiki 页面覆盖该模块。

### 维护后仍然存在的残余候选者

Reconcile 候选者永远不会达到零。有三个持续的候选者来源：

1. **没有 wiki 页面的模块** 产生 `missing_doc`。如果需要覆盖，请创建页面。
2. **限定方法名称** (`Type::method` 在 wiki 中) 与裸符号名称 (`method` 在代码中) 不匹配。通过在添加条目前在 wiki 中搜索符号名称来验证。
3. **跨模块的同名符号** (`get`, `tokenize`, `to_json_string`) 导致跨模块误报。检查 wiki 页面实际描述的模块。

跟踪 `New logical reviews` 作为收敛指标。当它达到零时，所有可操作的走动都已被解决。

## 完整的 wiki 维护周期

```bash
# 1. 检测过时的页面（源文件已更改）
indexion wiki pages ingest --wiki-dir=.indexion/wiki

# 2. 阅读索引以了解 wiki 结构
cat .indexion/wiki/index.md

# 3. 对于每个过时页面：阅读更改的源文件，将新内容写入临时文件，
#    然后通过命令更新（不要直接编辑 .md）
indexion wiki pages update --id=<页面ID> --content=/tmp/updated.md \
  --sources="..." --provenance=synthesized --actor="agent:<名称>" \
  --wiki-dir=.indexion/wiki

# 4. 验证结构完整性
indexion wiki lint --wiki-dir=.indexion/wiki

# 5. 验证内容准确性——针对项目根目录，迭代直到 NLR=0
indexion plan reconcile \
  --doc='.indexion/wiki/*.md' \
  --doc-spec=markdown \
  --format=md \
  .
# → 首先修复 stale_doc 组。重新运行。预期 2-3 轮。
# → 对于每个修复，使用 `wiki pages update`，而不是直接 .md 编辑。

# 6. 重新生成导航索引
indexion wiki index build --wiki-dir=.indexion/wiki

# 7. 确认所有内容都是最新的
indexion wiki pages ingest --dry-run --wiki-dir=.indexion/wiki
```

## 从零开始规划 wiki

当 wiki 不存在或需要结构重整时：

```bash
# 分析项目并生成页面结构提案
indexion wiki pages plan --format=md <项目目录>

# 然后执行提案：添加每个建议的页面
indexion wiki pages add --id=<ID> --title="..." --content=/tmp/page.md \
  --sources="..." --provenance=synthesized --actor="agent:<名称>"
```

**不需要初始化步骤。** 第一个 `wiki pages add` 调用会自动创建 `.indexion/wiki/` 和空的 `wiki.json` 元数据文件。没有单独的 `wiki init` 命令。

`wiki pages plan` 使用 CodeGraph 提出基于概念的页面，而不是基于文件的页面。优先选择概念页面（例如，"KGF System"）而不是文件页面（例如，"src/kgf/lexer/lexer.mbt"）。

## 构建搜索索引

```bash
# 仅构建导航索引（index.md）
indexion wiki index build --wiki-dir=.indexion/wiki

# 构建导航 + 向量搜索索引（vectors.db）
indexion wiki index build --full --wiki-dir=.indexion/wiki

# 不写入预览 index.md
indexion wiki index build --dry-run --wiki-dir=.indexion/wiki
```

使用 `--full` 时，`indexion search .indexion/wiki/` 将使用预构建的向量，而不是每次查询时从零开始重建。

## 检查审计记录

```bash
# 最近操作
indexion wiki log --wiki-dir=.indexion/wiki --tail=20

# 完整的 JSON 日志
indexion wiki log --wiki-dir=.indexion/wiki --json
```

每个 `pages add`, `pages update`, `lint`, `pages ingest`, 和 `index build` 调用都会追加到 `.indexion/wiki/log.json`。使用日志来验证之前的代理运行是否正确完成，或了解页面最后一次修改的原因。

## 关键陷阱

**反引号引用的 `wiki://` 参考不是链接。** Lint 检查器正确地忽略了代码跨度中的 ``wiki://``。使用裸 `wiki://page-id` 或 Markdown 链接 `[标题](wiki://page-id)` 来创建真正的交叉引用。

**`wiki pages ingest` 的元数据在最后一次运行时呈现状态。** 如果你通过 `pages update` 向页面的 `sources` 列表添加新的源文件，下一个 `ingest` 运行将显示该页面需要关注（因为新来源没有记录的哈希）。这是预期行为——更新后再次运行 `ingest` 以记录基线。
