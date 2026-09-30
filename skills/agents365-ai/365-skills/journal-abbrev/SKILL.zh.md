---
name: journal-abbrev
description: 在查找期刊或杂志名称缩写、在完整名称和ISO 4/MEDLINE缩写之间进行转换、处理BibTeX文件以进行期刊名称标准化，或回答关于期刊缩写/杂志缩写的问题时使用。当用户提到引文格式、参考文献列表准备或向特定期刊投稿时，应主动使用。触发条件包括："journal abbreviation"、"abbreviate journal"、"journal name"、"期刊缩写"、"杂志缩写"、"ISO 4"、"LTWA"、"BibTeX journal"。
---

# 期刊缩写查询

使用多源级联查询期刊/杂志名称缩写：JabRef 数据库（约 25K 期刊）→ AbbrevISO API（ISO 4）→ NLM 目录（MEDLINE）。

**关键规则**：始终使用 `jabbrv.py` 进行查询。切勿猜测缩写——即使是常见期刊也有不明显的缩写。

## 快速参考

| 用户期望... | 级别 | 命令 |
| --------------- | ------ | --------- |
| 缩写期刊名称 | 读取 | `python3 jabbrv.py abbrev "Nature Medicine"` |
| 展开缩写 | 读取 | `python3 jabbrv.py expand "Nat. Med."` |
| 自动检测方向 | 读取 | `python3 jabbrv.py lookup "J. Am. Chem. Soc."` |
| 模糊搜索（分页） | 读取 | `python3 jabbrv.py search "biolog chem" --limit 10 --offset 0` |
| 处理 .bib 文件 | 写入 | `python3 jabbrv.py bib refs.bib` |
| 预览 .bib 变化（不写入） | 读取 | `python3 jabbrv.py bib refs.bib --dry-run` |
| 显式 .bib 输出路径 | 写入 | `python3 jabbrv.py bib refs.bib --output out.bib` |
| 展开文件中的缩写 | 写入 | `python3 jabbrv.py bib refs.bib --expand` |
| 安全重放 .bib（重试返回缓存） | 写入 | `python3 jabbrv.py bib refs.bib --idempotency-key run-001` |
| 批量文本列表 | 读取 | `python3 jabbrv.py batch journals.txt` |
| 批量作为 NDJSON 流 | 读取 | `python3 jabbrv.py batch journals.txt --stream` |
| 检查缓存状态 | 读取 | `python3 jabbrv.py cache status` |
| 下载缺失的缓存文件 | 写入 | `python3 jabbrv.py cache update` |
| 预览更新内容 | 读取 | `python3 jabbrv.py cache update --dry-run` |
| 原子重建 | ⚠️ 破坏性 | `python3 jabbrv.py cache rebuild --yes` |
| 预览重建（不删除） | 读取 | `python3 jabbrv.py cache rebuild --dry-run` |
| 抑制 stderr 进度 | 读取 | `python3 jabbrv.py --quiet cache update` |
| 机器可读的 CLI 协议 | 读取 | `python3 jabbrv.py schema` |
| 单个子命令的架构 | 读取 | `python3 jabbrv.py schema lookup` |

### 输出格式

当 CLI 未连接到终端（管道或被代理捕获）时，stdout 是稳定的 JSON 封装；在 TTY 上运行时显示人类可读的表格/缩进视图。要强制格式：`--format json|table|human|auto`。`--json` 作为向后兼容的别名保留 `--format json`。标志可以出现在子命令之前或之后。

封装结构（每个子命令始终相同字段）：

- 成功：`{ "ok": true, "data": ..., "meta": { "schema_version", "cli_version", "cache", "latency_ms" } }`
- 部分成功（批量）：`{ "ok": "partial", "data": { "succeeded": [...], "failed": [...] }, "meta": {...} }`
- 错误：`{ "ok": false, "error": { "code", "message", "retryable", ... }, "meta": {...} }`

### 退出代码

| 代码 | 含义 |
|------|---------|
| `0`  | 成功（包括部分成功） |
| `1`  | 运行时/上游错误 |
| `2`  | 验证/输入错误（缺失文件，无效标志） |
| `3`  | 未找到（查询的期刊不存在） |

### 错误代码（在 `error.code` 内）

| 代码 | 可重试 | 退出 | 含义 |
| ------ | ----------- | ------ | --------- |
| `not_found` | 否 | 3 | 查询完成但无源匹配 |
| `upstream_unavailable` | **是** | 1 | 一个或多个上游 API 暂时失败；无法完成查询。包含 `error.sources[]` 列出每个失败。稍后重试。 |
| `file_not_found` | 否 | 2 | 输入文件路径不存在 |
| `validation_error` | 否 | 2 | 无效的参数或标志组合 |
| `runtime_error` | 是 | 1 | 预期之外的内部错误 |

根据 `error.code` + `error.retryable` 分支，而不是仅根据退出代码——退出 `1` 覆盖 `upstream_unavailable` 和 `runtime_error`。完整机器可读列表：`python3 jabbrv.py schema` → `data.error_codes`。

### 环境变量（由主机设置，非代理 argv 设置）

| 变量 | 效果 |
| ---------- | -------- |
| `JABBRV_CACHE_DIR` | 覆盖缓存目录（默认：`<安装>/cache`）。在沙盒中很有用，安装树是只读的。 |
| `JABBRV_OFFLINE` | 真值（`1`/`true`/`yes`/`on`）跳过 AbbrevISO 和 NLM；仅查询本地 JabRef 缓存。缺失变为确定的 `not_found`（不可重试），因为主机已声明上游受限。`meta.offline: true` 出现在每个封装中，以便调用者了解策略。 |
| `NO_COLOR` | <https://no-color.org> 规范。任何非空值禁用颜色。目前不输出 ANSI；设置时 `meta.no_color: true` 出现，以便调用者了解策略。 |

信任边界：这些从进程环境读取，而非参数。主机或沙盒设置它们；代理无法通过 argv 覆盖。架构内省：`python3 jabbrv.py schema` → `data.global_env`。

### 重试、幂等性和破坏性意图

- **根据 `error.code` + `error.retryable` 分支**，而非仅根据退出代码。退出 `1` 覆盖 `upstream_unavailable`（重试）和 `runtime_error`（重试一次，然后升级）。
- **`bib --idempotency-key <token>`** 将成功封装保存在输出文件旁边，作为 `<输出>.<token>.envelope.json`。使用相同密钥的重试返回带有 `meta.idempotent_replay: true` 的封装，而不是重新运行重写。密钥必须匹配 `[A-Za-z0-9._-]{1,64}`。
- **`cache rebuild`** 是原子的——下载到兄弟目录，只有在所有文件成功时才交换。如果任何失败，保留现有缓存，响应为 `upstream_unavailable`（可重试）。添加 `--yes` 记录 `meta.confirmed: true` 用于审计策略；CLI 本身从不提示，因此 `--yes` 不是门控。

## 工作流程

### 第 1 步：检测意图

| 意图 | 操作 |
| -------- | -------- |
| 单个期刊名称/缩写 | 使用 `lookup`（自动检测）或 `abbrev`/`expand`（明确方向） |
| "X 的缩写是什么？" | 使用 `abbrev` |
| "X 是哪个期刊？" | 使用 `expand` |
| 部分或不确定名称 | 使用 `search` 进行模糊匹配 |
| 修复 .bib 文件中的期刊名称 | 使用 `bib` |
| 要处理的期刊列表 | 使用 `batch` |

### 第 2 步：执行

运行适当的 `jabbrv.py` 命令。脚本处理：

1. **本地缓存查询**（即时，来自 JabRef 的约 25K 期刊）
2. **AbbrevISO API** 降级（算法 ISO 4 缩写，单向）
3. **NLM 目录** 降级（生物医学期刊，双向）

首次运行自动下载 JabRef CSV 缓存文件（约 2-5 MB）。

### 第 3 步：展示结果

- 显示全名、缩写和来源
- 当相关时，注明标准（ISO 4 vs MEDLINE）
- 对于 .bib 处理：确认前显示变更摘要

## ISO 4 vs MEDLINE

存在两种常见的缩写标准：

| 标准 | 时期 | 示例 | 使用者 |
|----------|---------|---------|---------|
| **ISO 4** | 是 | Nat. Med. | 大多数出版商、BibTeX |
| **MEDLINE** | 否 | Nat Med | PubMed、NLM 数据库 |

JabRef 提供 ISO 4 风格。NLM 目录提供 MEDLINE 风格。AbbrevISO 从 LTWA（标题词缩写列表）算法计算 ISO 4。

## 常见缩写模式

| 单词 | 缩写 | 单词 | 缩写 |
| ------ | ------------- | ------ | ------------- |
| 期刊 | J. | 国际 | Int. |
| 美国 | Am. | 欧洲 | Eur. |
| 科学/科学 | Sci. | 医学/医学 | Med. |
| 生物/生物 | Biol. | 化学/化学 | Chem. |
| 物理/物理 | Phys. | 工程 | Eng. |
| 研究 | Res. | 评论/评论 | Rev. |
| 协会 | Soc. | 国家 | Natl. |
| 会议录 | Proc. | 交易 | Trans. |
| 信件 | Lett. | 通信 | Commun. |
| 应用 | Appl. | 计算 | Comput. |

**注意**：单词标题（例如 "Nature"、"Science"、"Cell"）根据 ISO 4 规则不缩写。

## 集成示例

### 与 Zotero

```bash
# 从 Zotero 导出 BibTeX，然后标准化期刊名称
zot export COLLECTION_KEY --format bibtex > refs.bib
python3 jabbrv.py bib refs.bib
```

### 与 LaTeX

```bash
# 编译前确保所有期刊名称都已缩写
python3 jabbrv.py bib references.bib
# 将输出文件（references_abbrev.bib）用于您的 LaTeX 文档
```

### 批量处理

创建一个每行一个期刊名称的文本文件：

```
Nature Medicine
Journal of Biological Chemistry
Proceedings of the National Academy of Sciences
```

然后运行：

```bash
python3 jabbrv.py batch journals.txt
```

## 故障排除

| 问题 | 解决方案 |
| ------- | --------- |
| "未找到结果" | 尝试使用 `search` 对部分名称进行模糊匹配 |
| 缓存下载失败 | 检查网络连接，重试 `cache update`（或 `cache rebuild` 强制） |
| 缩写风格错误 | JabRef = ISO 4（带点），NLM = MEDLINE（不带点） |
| BibTeX 字段未检测到 | 确保 `journal = {Name}`（花括号）格式 |
