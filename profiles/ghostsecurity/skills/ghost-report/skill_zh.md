# 综合安全报告

您将所有扫描技能（scan-deps、scan-secrets、scan-code）的发现结果汇总到一个优先级排序的报告文件中。所有工作由您自行完成 — 不要生成子代理或委托。

$ARGUMENTS

---

## 第 0 步：设置

运行以下 Bash 命令来计算路径：
```bash
repo_name=$(basename "$(pwd)") && remote_url=$(git remote get-url origin 2>/dev/null || pwd) && short_hash=$(printf '%s' "$remote_url" | git hash-object --stdin | cut -c1-8) && repo_id="${repo_name}-${short_hash}" && short_sha=$(git rev-parse --short HEAD 2>/dev/null || date +%Y%m%d) && ghost_repo_dir="$HOME/.ghost/repos/${repo_id}" && scans_dir="${ghost_repo_dir}/scans/${short_sha}" && cache_dir="${ghost_repo_dir}/cache" && skill_dir=$(find . -path '*/skills/report/SKILL.md' 2>/dev/null | head -1 | xargs dirname) && echo "scans_dir=$scans_dir cache_dir=$cache_dir skill_dir=$skill_dir"
```

存储 `scans_dir`（提交级别的扫描目录）、`cache_dir` 和 `skill_dir`。

---

## 缓存检查

如果 `<scans_dir>/report.md` 已经存在，显示：

```
综合安全报告位于：<scans_dir>/report.md
```

然后停止。不要重新生成它。

---

## 第 1 步：读取仓库上下文

如果存在 `<cache_dir>/repo.md`，则读取。提取：
- 业务关键性
- 敏感数据类型
- 组件映射

如果不存在，则继续而不使用它 — 这不是错误。

---

## 第 2 步：发现扫描结果

列出 `<scans_dir>` 的内容，以查看哪些扫描类型目录存在。已识别的类型：
- `deps/` — 依赖项漏洞扫描（SCA）
- `secrets/` — 密钥和凭证扫描
- `code/` — 代码安全扫描（SAST）

如果这些目录都不存在，报告错误：

```
在 <scans_dir> 中未找到扫描结果。请先运行一个或多个扫描技能：
  /ghost-scan-deps
  /ghost-scan-secrets
  /ghost-scan-code
```

然后停止。

---

## 第 3 步：收集发现结果

对于每个存在的扫描类型，使用 glob 命令 `<scans_dir>/<type>/findings/*.md` 并**完整读取**每个发现文件。保留每个发现的完整 Markdown 正文 — 报告将直接内联此内容，因此读者无需打开单个发现文件。

从每个发现中，还提取以下元数据字段用于过滤和排序：

- **ID** — 从 `## 元数据` → `ID`
- **类型** — 扫描类型（`deps`、`secrets` 或 `code`）
- **严重性** — 从 `## 元数据` → `严重性`（高、中、低）
- **状态** — 从 `## 元数据` → `状态`（例如，可利用、未验证、已验证、已拒绝、干净）

---

## 第 4 步：过滤和排序

**过滤**：仅保留高置信度的发现：
- 对于 `deps` 发现：状态为 `confirmed-exploitable`
- 对于 `secrets` 发现：状态不是 `clean` 且不是 `rejected`
- 对于 `code` 发现：状态为 `verified` 或 `unverified`（不是 `rejected`）

**排除**任何状态为 `clean`、`rejected` 或 `false-positive` 的发现。

**排序**剩余的发现：
1. 按严重性排序：高优先，然后中，然后低
2. 在相同严重性内：`deps` 优先于 `secrets` 优先于 `code`

---

## 第 5 步：读取每个扫描报告

对于 `deps` 和 `secrets` 扫描类型，如果存在 `<scans_dir>/<type>/report.md`，则读取。提取：
- 统计数据（扫描的候选项、已确认的发现、过滤的误报）
- 执行摘要要点

注意：`code` 不会生成 `report.md`。对于代码扫描覆盖率，直接计算 `<scans_dir>/code/findings/` 中的发现文件数量。 "扫描的候选项" 计数是发现文件的总数（所有状态）。"已确认的发现" 是状态为 `verified`、`confirmed` 或 `unverified` 的计数。"过滤的误报" 是状态为 `rejected` 的计数。**不要**计算提名/分析流程中的干净文件分析 — 这些从未成为发现。

如果 `deps` 或 `secrets` 的每个扫描报告不存在，则记为不可用。

---

## 第 6 步：生成报告

1. 读取 `<skill_dir>/report-template.md`
2. 使用收集的数据填充模板：
   - 用仓库名称、提交 SHA、日期以及运行的扫描填充扫描信息
   - 使用仓库上下文和汇总的发现结果编写执行摘要
   - 对于此安全报告中的所有写作元素，使用中性、人类化的语气，平衡专业性和易读性。不要使用表情符号、破折号等
   - 对于严重性为高的关键和高发现：将每个发现文件中的实质性内容直接内联到报告中 — 包括代码片段、评估表格、修复命令和所有相关细节，使报告完全自包含
   - 对于中等严重性的发现：为每个发现编写完整的小节，包括描述、位置、代码上下文和修复（不是精简表格）
   - 忽略低严重性的发现（它们仅保留在每个扫描的发现文件中）
   - 从每个扫描报告的统计数据填充扫描覆盖率表格（对于代码，使用第 5 步中的发现文件计数）
   - 为每个运行的扫描类型添加简短的方法说明（从每个扫描报告中提取 1-2 句话）
   - **不要**包含指向每个扫描报告或单个发现文件的链接 — 所有内容都已内联
3. 将报告写入 `<scans_dir>/report.md`

---

## 第 7 步：显示输出

```
综合安全报告位于：<scans_dir>/report.md
```
