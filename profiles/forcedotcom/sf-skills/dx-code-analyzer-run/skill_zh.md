# 运行代码分析技能

## 关键：强制脚本使用

所有与代码分析器交互的操作都必须通过 `<skill_dir>/scripts/` 中的捆绑脚本执行。没有例外。

### 错误做法——绝对不要这样做：

```bash
# 错误：内联 Python 解析结果
python3 -c "import json; data = json.load(open('results.json'))..."

# 错误：内联 Node.js 解析结果
node -e "const data = require('./results.json')..."

# 错误：使用 jq 过滤结果
cat results.json | jq '.violations[] | select(.engine=="pmd")'

# 错误：直接读取结果文件（可能为 10MB+）
Read tool → code-analyzer-results-*.json
```

同样禁止：`run_code_analyzer` 和任何 `mcp__*` 工具——仅限 Bash。

### 正确做法——始终这样做：

```bash
# 汇总扫描结果
node "<skill_dir>/scripts/parse-results.js" "./code-analyzer-results-TIMESTAMP.json"

# 过滤/排序/查询结果（按引擎、严重性、文件、规则、类别）
node "<skill_dir>/scripts/query-results.js" "./code-analyzer-results-TIMESTAMP.json" --engine pmd --summary

# 列出/浏览可用规则（按引擎、类别、语言、严重性）
node "<skill_dir>/scripts/list-rules.js" "Security" --top 10

# 查询规则含义
node "<skill_dir>/scripts/describe-rule.js" "ApexCRUDViolation" --engine pmd

# 发现可修复的违规
node "<skill_dir>/scripts/discover-fixes.js" "./code-analyzer-results-TIMESTAMP.json"

# 应用修复（用户确认后）
node "<skill_dir>/scripts/apply-fixes.js" "./code-analyzer-results-TIMESTAMP.json"

# 汇总已应用的修复
node "<skill_dir>/scripts/summarize-fixes.js" "./code-analyzer-results-TIMESTAMP.json"

# 在应用修复前过滤供应商文件（jQuery、Bootstrap、*.min.js）
node "<skill_dir>/scripts/filter-violations.js" "./code-analyzer-results-TIMESTAMP.json" "./code-analyzer-results-TIMESTAMP-filtered.json" --report
```

`<skill_dir>` 是包含此 SKILL.md 的目录的绝对路径。**绝对不要**使用 `./scripts/`——它针对的是用户的当前工作目录，而不是技能目录。

任何聚合、过滤或排序问题（“哪个文件有最多的违规？”“PMD 问题有多少？”“按数量排序的顶级规则？”“按严重性分解”）都由 `query-results.js` 回答——它的输出已经包含 `topRules`、`topFiles` 和 `severityCounts`。

---

## 概述

> **生态系统：** 此技能是 3 技能代码分析器套件的一部分——`dx-code-analyzer-run`（扫描和结果）· `dx-code-analyzer-configure`（设置、配置、CI/CD）· `dx-code-analyzer-custom-rule-create`（自定义规则编写）。

此技能将自然语言请求（“扫描安全问题”、“检查我的更改”）转换为正确的 `sf code-analyzer run` 命令，执行跨任何组合的引擎/目标/严重性的扫描，并呈现可操作的扫描结果。当引擎提供的修复可用时，它会发现它们，请求用户确认，安全地应用它们，并提供验证。用于静态分析、安全审查、AppExchange 认证、代码质量检查以及在 Salesforce 项目中查找重复项/漏洞。

**在范围内：** 执行扫描、解析/过滤/排序结果、应用引擎自动修复、基于差异的扫描、所有输出格式（JSON/HTML/SARIF/CSV/XML）、描述/列出规则、扫描故障排除。

**超出范围：** 安装/配置 `sf` 或插件（→ `dx-code-analyzer-configure`）、编写自定义规则/引擎（→ `dx-code-analyzer-custom-rule-create`）、超出引擎提供的 AI 生成修复、深度重构、CI/CD 设置（→ `dx-code-analyzer-configure`）。

**允许的工具：** Bash (`sf code-analyzer`, `node`, `git diff`, `date`), Read, Write, Edit。**禁止：** 任何 MCP 工具、Agent 工具、网络工具、其他技能、Python、`jq`、内联脚本/here docs。此技能拥有完整的扫描-修复-验证-查询-解释工作流端到端。

---

## 命令语法规则（首先阅读——绝对）

1. 命令是 **`sf code-analyzer run`** ——不是 `sf scanner run`（已弃用 v3）。
2. **没有 `--format` 标志。** 使用 `--output-file <path>.<ext>`；扩展名决定格式。
3. **始终**传递 `--output-file` 并使用带时间戳的名称（例如，`./code-analyzer-results-20260512-143022.json`）——不要依赖标准输出。
4. **仅前台**（不使用 `run_in_background`）；大型扫描的超时时间为 1200000ms。
5. **无效的 v3 标志**导致错误：`--format`、`--engine`、`--category`、`--json`。使用 `--rule-selector` + `--output-file` 代替。
6. **工具限制：** 仅限 Bash、Read、Write、Edit。没有 MCP 工具、没有 Agent 工具、没有网络工具、没有其他技能。

原因：v4+ CLI 重新设计了标志界面；v3 标志现在会报错。

完整标志/选择器文档：`<skill_dir>/references/flag-reference.md`。

---

## 前置条件

用户需要：**Salesforce CLI** (`sf`), **@salesforce/plugin-code-analyzer** (v5.x+), **Java 11+** (PMD/CPD/SFGE), **Node.js 18+** (ESLint/RetireJS), **Python 3** (Flow), **已认证的组织** (ApexGuru)。

预飞行检查：运行 `sf code-analyzer --help 2>&1 | head -1`。如果失败，或者如果扫描报告引擎启动错误（例如，“PMD 启动失败”、“java: 命令未找到”、“SFGE 失败”）：

1. **停止**——不要尝试自己安装/诊断前置条件。
2. **委托给 `dx-code-analyzer-configure`**——它处理所有设置。
3. 完成后，返回这里并重新运行扫描。

如果扫描因其他原因失败，请参阅 `<skill_dir>/references/error-handling.md`。

---

## 快速入门：常见模式

匹配以下请求；如果匹配，则跳转到步骤 3（构建命令）。否则，按步骤 1 操作。

| 用户说 | 规则选择器 | 备注 |
|--------|------------|------|
| "扫描我的代码" / "运行代码分析器" | `Recommended` | 精选集，所有文件类型 |
| "检查安全问题" / "安全审查" | `all:Security:(1,2)` | 所有引擎，关键+高 |
| "扫描我的更改" / "检查差异" | (见步骤 1.5) | 通过 `git diff` 获取文件，过滤到可扫描类型，通过 `--target` 传递 |
| "运行 PMD" / "检查我的 Apex" | `pmd` | Apex 类和触发器 |
| "LWC 代码风格检查" / "检查我的 JavaScript" | `eslint` | JavaScript/TypeScript/LWC |
| "查找重复项" / "检查代码复制粘贴" | `cpd` | 代码克隆 |
| "检查漏洞" / "扫描库" | `retire-js` | JavaScript 库 CVE |
| "深度分析" / "数据流分析" | `sfge` | Java 11+，10–20 分钟，使用 `--workspace "force-app"` |
| "性能分析" / "治理器限制" | `apexguru` | 需要认证的组织 |
| "分析我的流程" | `flow` | `--target **/*.flow-meta.xml`，Python 3 |
| "AppExchange 安全审查" | `all:Security:(1,2)` | 见 `<skill_dir>/references/special-behaviors.md` → AppExchange |

---

## 步骤 1：解析用户的意图

沿以下 7 个维度分析请求；任何维度都可以组合。

### 1.1 引擎
PMD/Apex → `pmd` · ESLint/JS/TS/代码风格检查 → `eslint` · 流程 → `flow` · 重复项/CPD → `cpd` · 漏洞/CVE/RetireJS → `retire-js` · SFGE/数据流 → `sfge` · 性能/ApexGuru → `apexguru` · 正则表达式 → `regex` · 所有 → `all` · 未指定 → `Recommended`。

### 1.2 类别
安全/OWASP → `Security` · 性能 → `Performance` · 最佳实践 → `BestPractices` · 代码风格/格式 → `CodeStyle` · 设计/复杂度 → `Design` · 错误易发 → `ErrorProne` · 文档 → `Documentation`。

### 1.3 严重性
1=关键 · 2=高 · 3=中等 · 4=低 · 5=信息。 "仅关键" → `1` · "关键+高" → `(1,2)` · "中等及以上" → `(1,2,3)`。

### 1.4 具体规则
如果用户指定了规则（例如，"ApexCRUDViolation"、"no-unused-vars"）：`--rule-selector <engine>:<ruleName>`，或者如果引擎不明确，则只写 `<ruleName>`。

**部分名称：** `--rule-selector` 要求**完全准确**的规则名称（例如，`@salesforce-ux/slds/no-hardcoded-values-slds2`，而不是 `no-hardcoded-values`）。不能使用通配符。如果您不确定 100%，请先查找——**不要猜测**：
```bash
sf code-analyzer rules --rule-selector all 2>&1 | grep -i "USER_KEYWORD"
```
多个匹配项 → 询问用户哪个。零个匹配项 → 告知用户没有匹配项。

### 1.5 目标
特定路径 → `--target <path>` · 通配符（“所有 Apex”）→ `--target **/*.cls,**/*.trigger` · "我的更改"/"差异" → `git diff --name-only [base]...HEAD`，过滤到可扫描类型，通过 `--target` 传递 · "LWC" → `--target **/lwc/**` · "流程" → `--target **/*.flow-meta.xml` · 未指定 → 省略（整个工作区）。

差异过滤细节：`<skill_dir>/references/special-behaviors.md`。

### 1.6 输出
**默认 JSON。** 只有在用户明确要求时才更改。名称：`./code-analyzer-results-<YYYYMMDD-HHmmss>.<ext>` 通过 `TIMESTAMP=$(date +%Y%m%d-%H%M%S)`。格式：`.json`（默认），`.html`，`.sarif`，`.csv`，`.xml`。

### 1.7 比较 / 差异
"自 main 以来" → `git diff --name-only main...HEAD` → 扫描这些 · "自上次提交以来" → `HEAD~1` · "与 develop 对比" → `develop...HEAD`。

---

## 步骤 2：构建规则选择器

语法：`:` = AND，`,` = OR，`()` = 分组。

- 仅引擎：`pmd`
- 引擎 + 类别：`pmd:Security`
- 引擎 + 严重性：`pmd:2`
- 复杂：`(pmd,eslint):Security:(1,2)` = (PMD 或 ESLint) AND Security AND 严重性 (1 或 2)
- 具体规则：`pmd:ApexCRUDViolation`
- 所有：`all`

更多：`<skill_dir>/references/command-examples.md`。

---

## 步骤 3：构建完整命令

```bash
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
sf code-analyzer run \
  --rule-selector <selector> \
  --target <targets> \                                              # 可选
  --output-file "./code-analyzer-results-${TIMESTAMP}.json" \       # 默认 JSON
  --include-fixes \                                                 # 始终
  --workspace <path>                                                # 可选
```

- 默认使用带时间戳的 JSON；只有在明确要求时才更改格式。
- 始终传递 `--include-fixes`（启用步骤 6 自动修复）。
- 省略 `--target` 以扫描整个工作区。
- 差异扫描：`git diff --name-only` → 过滤可扫描类型 → 作为 `--target` 传递。

特殊情况（SFGE/ApexGuru/AppExchange/差异）：`<skill_dir>/references/special-behaviors.md`。

---

## 步骤 4：执行扫描

仅使用 Bash 工具——**绝对不要**使用 `run_code_analyzer` MCP 工具。

1. 通过 Bash 生成时间戳：`date +%Y%m%d-%H%M%S` → 例如 `20260512-143022`。
2. 告知用户：
   ```text
   开始扫描...
   结果：./code-analyzer-results-20260512-143022.json
   日志：./code-analyzer-results-20260512-143022.log
   对于大型代码库，可能需要几分钟时间。
   ```
3. 使用**字面**时间戳运行（不要 `$TIMESTAMP`），前台，超时 1200000ms，使用 `tee` 到 `.log`：
   ```bash
   sf code-analyzer run --rule-selector Recommended \
     --output-file "./code-analyzer-results-20260512-143022.json" \
     --include-fixes 2>&1 | tee "./code-analyzer-results-20260512-143022.log"
   ```
4. 成功退出 0。出错时，请阅读日志文件和 `<skill_dir>/references/error-handling.md`。
5. **立即**解析结果（步骤 5）——不要暂停询问下一步该做什么。

---

## 步骤 5：解析并展示结果

扫描后立即运行解析脚本——不要暂停询问：

```bash
node "<skill_dir>/scripts/parse-results.js" "./code-analyzer-results-TIMESTAMP.json"
```

**绝对不要：**
- 自己发明或生成脚本代码
- 使用裸相对路径，如 `node scripts/parse-results.js`（不会从用户的 CWD 解析）
- 使用 heredocs 或内联脚本内容
- 使用 `jq` 作为解析脚本的替代（外壳引号会破坏）
- 直接读取 JSON 文件

### 展示模板

```text
## 扫描完成

在 Y 个文件中发现了 X 个违规。

| 严重性 | 数量 |
|--------|------|
| 关键 (1) | X |
| 高 (2) | X |
| 中等 (3) | X |
| 低 (4) | X |
| 信息 (5) | X |

### 顶级问题
| # | 规则 | 引擎 | 严重性 | 文件 | 行 |
|---|------|------|-------|------|------|
| 1 | ApexCRUDViolation | pmd | 2 | AccountService.cls | 42 |
| ... 最多 10 个最关键 |

### 按频率排序的顶级规则
| 规则 | 引擎 | 数量 |
|------|------|------|
| no-var | eslint | 170 |
| ... |

完整结果：`./code-analyzer-results-20260512-143022.json`
```

根据结果大小调整：
- **0** → "未发现违规"
- **1–10** → 所有显示在一个表格中
- **11–50** → 严重性统计 + 顶级 10
- **50–5000** → 统计 + 顶级 10 个违规 + 顶级 10 个规则 + 顶级 5 个文件
- **5000+** → 同上，并建议缩小范围（严重性/类别/文件夹）。始终在末尾提供输出路径并建议下一步操作：过滤/解释规则/应用修复。

大型结果处理：`<skill_dir>/references/special-behaviors.md`。

---

## 步骤 6：应用引擎提供的修复（扫描后）

引擎提供的修复是**确定性**的（不是 AI 生成的）。流程：供应商文件过滤（如果需要）→ 发现 → 展示 → **等待用户确认** → 应用 → 总结。

### 6.1 供应商文件过滤（当需要时）

如果用户说 "修复我的代码" / "项目源"，或者如果顶级违规文件是供应商库（jQuery、Bootstrap、`*.min.js`）：

```bash
node "<skill_dir>/scripts/filter-violations.js" \
  "./code-analyzer-results-TIMESTAMP.json" \
  "./code-analyzer-results-TIMESTAMP-filtered.json" \
  --report
```

报告："排除 X 个供应商文件（Y 个违规）—— jQuery、Bootstrap 等。仅对 Z 个项目文件应用修复。" 使用过滤后的文件进行 6.2+。

### 6.2 发现

```bash
node "<skill_dir>/scripts/discover-fixes.js" "./code-analyzer-results-TIMESTAMP.json"
```

### 6.3 展示 + 询问（然后停止）

```text
### 引擎提供的修复可用
**X 个 Y 个违规**由分析引擎提供自动修复：

| 规则 | 引擎 | 严重性 | 可修复数量 |
|------|------|-------|------------|
| no-var | eslint | 3 | 170 |
| ... |

这些都是由引擎安全生成的确定性修复（不是 AI 生成的）。

您希望我应用这些修复吗？(是 / 否 / 选择特定规则)
```

**停止并等待用户的回复，即使他们最初说 "扫描并修复所有内容"。** 仅在下一轮中接收到 "是" / "应用" / "继续" 时才应用。

### 6.4 应用

```bash
node "<skill_dir>/scripts/apply-fixes.js" "./code-analyzer-results-TIMESTAMP.json"
```
(如果 6.1 创建了过滤文件。)

### 6.5 总结（必须在 6.4 之后立即执行）

```bash
node "<skill_dir>/scripts/summarize-fixes.js" "./code-analyzer-results-TIMESTAMP.json"
```

然后展示：

```text
### 引擎提供的修复已成功应用
在 Y 个文件中应用了 X 个自动修复。

| 严重性 | 应用数量 |
|--------|----------|
| 关键 (1) | X |
| ... |

| 规则 | 应用数量 |
|------|----------|
| no-var | 169 |
| ... |

我重新运行扫描以验证修复是否解决了违规吗？
```

### 6.6 — 处理用户的选项
- **拒绝 / "否":** 跳过应用，跳过总结。不要重新扫描。
- **"选择规则":** 将发现列表过滤到这些规则，并将过滤后的文件传递给 `apply-fixes.js`。
- **"全部" / "是":** 对完整（或供应商过滤的）结果文件按原样运行 `apply-fixes.js`。

### 6.7 — 可选重新扫描以验证
如果用户在 6.5 中接受提议，使用新的时间戳重新运行相同的扫描（不要覆盖原始文件）。比较扫描前后的违规数量，并显示差异——干净的修复会消失；剩余的违规需要手动修复或与无关。

---

## 步骤 7：查询和过滤现有结果

在步骤 5 后，用户可能想要**深入特定子集**而无需重新运行整个扫描。本步骤处理所有结果探索请求。

### 触发条件
当用户要求切片、过滤、排序或探索现有结果时激活：
- "只显示安全问题"
- "AccountService.cls 中有什么？"
- "仅显示 PMD 问题" / "过滤到关键和高"
- "哪些 ESLint 规则被触发？" / "显示 lwc 文件夹中的违规"
- "最严重的 20 个" / "哪个文件有最多的违规？"
- "最常见的规则是什么？" / "每个引擎的违规数量是多少？" / "按严重性分解"

**重要：** 任何关于现有扫描结果的问题——过滤、排序、计数、聚合——**必须**使用 `query-results.js`。**绝对不要**使用内联 Python、`jq` 或临时脚本来解析结果 JSON。查询脚本已经在其输出中提供 `topRules`、`topFiles` 和 `severityCounts`。

### 执行方式
对来自步骤 4 的**相同结果文件**运行查询脚本（无需重新扫描）：

```bash
node "<skill_dir>/scripts/query-results.js" "./code-analyzer-results-TIMESTAMP.json" [选项]
```

| 用户说 | 选项 |
|--------|------|
| "安全问题" | `--category Security` |
| "PMD 问题仅" | `--engine pmd` |
| "关键和高" / "严重性 1-2" | `--severity 1,2` |
| "在 AccountService.cls 中" | `--file AccountService.cls` |
| "ApexCRUDViolation 规则" | `--rule ApexCRUDViolation` |
| "前 20 名" | `--top 20` |
| "按文件排序" | `--sort file` |
| "只给我计数" | `--summary` |
| "哪个文件有最多的违规？" | `--sort file --summary` (读取 `topFiles`) |
| "哪个文件有最多的 PMD 违规？" | `--engine pmd --summary` (读取 `topFiles`) |
| "最常见的规则？" | `--summary` (读取 `topRules`) |
| "每个引擎的计数？" | 使用步骤 5 的摘要，或针对每个引擎运行 `--engine X --summary` |
| 组合 | `--engine pmd --severity 1,2 --top 5` |

输出格式和展示模板：`<skill_dir>/references/post-scan-workflows.md`。

---

## 步骤 8：描述规则

当用户询问 "这个规则是什么意思？" 或 "如何修复这个？" 时，使用本步骤查找和解释特定规则。

### 触发条件
- "ApexCRUDViolation 是什么？"
- "解释这个规则" / "为什么被标记？"
- "no-var 是什么意思？"
- "如何修复 OperationWithLimitsInLoop？"
- "告诉我这个违规的信息"

### 执行方式

```bash
node "<skill_dir>/scripts/describe-rule.js" "<rule-name>" [--engine <engine>]
```

已知引擎时传递 `--engine`（从扫描上下文中）；否则省略，进行更广泛的搜索。返回状态为 `success` / `multiple_matches` / `not_found`。状态处理和模板：`<skill_dir>/references/post-scan-workflows.md`。

---

## 步骤 9：列出可用规则

触发条件： "有哪些安全规则可用？" / "列出所有 PMD 规则" / "JavaScript 规则" / "推荐规则" / "ESLint 规则有多少？" / "Apex 规则"

```bash
node "<skill_dir>/scripts/list-rules.js" "<selector>" [选项]
```

| 用户说 | 选择器 | 选项 |
|--------|--------|------|
| "安全规则" | `Security` | |
| "PMD 规则" | `pmd` | |
| "ESLint 安全规则" | `eslint:Security` | |
| "JavaScript 规则" | `JavaScript` | |
| "Apex 规则" | `Apex` | |
| "推荐规则" | `Recommended` | |
| "高严重性规则" | `(1,2)` | |
| "只给我计数" | `Recommended` | `--count-only` |
| "前 10 个安全规则" | `Security` | `--top 10` |

过滤器：`--engine`、`--severity`、`--top`（默认 100）、`--count-only`。脚本在调用 CLI 之前预先验证选择器标记（捕获拼写错误，如 `secruity`）。展示：`<skill_dir>/references/post-scan-workflows.md`.

---
## 跨技能集成

此技能是 3 技能代码分析器生态系统的一部分。干净地委托，而不是尝试属于其他技能的工作。

### 当此技能委托给 `dx-code-analyzer-configure` 时：

- 预飞行检查失败（CLI 缺失、插件未安装、引擎前置条件损坏）→ 停止，委托，修复后返回这里
- 用户要求设置 CI/CD、编辑 `code-analyzer.yml`、更改严重性、禁用引擎 → 完全委托

### 当此技能委托给 `dx-code-analyzer-custom-rule-create` 时：

- 用户要求创建新规则、编写 XPath、编写正则表达式规则或强制未包含在内置规则中的模式 → 完全委托。不要在这里尝试创建规则。

### 当其他技能委托给这里时：

- `dx-code-analyzer-configure` 完成设置 → 继续扫描（步骤 1–5）
- `dx-code-analyzer-custom-rule-create` 完成创建规则 → 继续扫描并针对新规则（例如，`--rule-selector pmd:<RuleName>`）以验证其是否正常工作

### 所有权边界

此技能拥有完整的**扫描→探索→修复**工作流端到端。它不拥有安装、配置文件管理或规则编写。

---

## 限制和注意事项

| 项目 | 原因 / 修复 |
|------|-------------|
| 使用带时间戳的 JSON + `.log` 通过 `tee` | 防止覆盖；与结果匹配 |
| `--format` 标志 | v4+ 中已移除；使用 `--output-file <path>.<ext>` |
| 前台，超时 1200000ms | SFGE 可能需要 10–20 分钟；后台会丢失输出 |
| 使用绝对 `<skill_dir>` 路径运行脚本 | `./scripts/` 针对的是用户的当前工作目录，而不是技能目录 |
| 不要在未经确认的情况下应用修复 | 用户必须批准代码修改 |
| 修复前进行供应商文件检查 | 如果 50%+ 供应商（jQuery/Bootstrap/`*.min.js`），则先过滤 |
| 修复脚本顺序：过滤（如果需要）→ 发现 → 应用 → 总结 | 跳过总结会使用户无法获得结果报告 |
| SFGE 需要显式 `--workspace` | 否则模板文件会导致编译错误 |
| 查找部分规则名称时先验证 | 猜测会返回 0 个结果；使用 `sf code-analyzer rules` |
| 仅使用 Bash 工具，不要 MCP | `run_code_analyzer` 和其他 MCP 工具绕过了脚本工作流 |
| 不要为修复调用其他技能 | 此技能拥有完整工作流端到端 |
| 查询现有结果，不要重新扫描 | 步骤 7 即时过滤现有 JSON |
| 扫描返回 0 结果 | 无效的规则选择器——验证 `sf code-analyzer rules --rule-selector <selector>` |
| `jq` 解析失败 | 外壳引号——使用 `parse-results.js` / `query-results.js` |
| 由 LLM 编写的内联脚本 | 不要编写脚本——使用 `<skill_dir>/scripts/` 中的现有脚本 |
| 使用 ad-hoc Python 进行排序/聚合 | 始终使用 `query-results.js`；输出中已经包含 `topFiles`/`topRules`/`severityCounts` |

---
## 参考文件索引

**脚本**（始终使用绝对 `<skill_dir>/` 前缀通过 `node` 执行，不要使用 Read）：

| 文件 | 使用时机 |
|------|----------|
| `<skill_dir>/scripts/parse-results.js` | 步骤 5 — 从扫描 JSON 中提取摘要 |
| `<skill_dir>/scripts/filter-violations.js` | 步骤 6.1 — 排除供应商文件（jQuery、Bootstrap）以供修复 |
| `<skill_dir>/scripts/discover-fixes.js` | 步骤 6.2 — 识别可修复的违规 |
| `<skill_dir>/scripts/apply-fixes.js` | 步骤 6.4 — 应用引擎修复（用户确认后） |
| `<skill_dir>/scripts/summarize-fixes.js` | 步骤 6.5 — 总结已应用的更改 |
| `<skill_dir>/scripts/query-results.js` | 步骤 7 — 无需重新扫描即可过滤/钻探现有结果的脚本 |
| `<skill_dir>/scripts/describe-rule.js` | 步骤 8 — 查找规则描述和文档 |
| `<skill_dir>/scripts/list-rules.js` | 步骤 9 — 通过选择器列出/浏览可用规则，并验证 |

**参考**（按需阅读）：

| 文件 | 阅读时机 |
|------|----------|
| `references/quick-start.md` | 命令语法模板 |
| `references/flag-reference.md` | 完整标志文档，规则选择器语法 |
| `references/error-handling.md` | 扫描失败诊断 |
| `references/engine-reference.md` | 引擎功能、文件类型、规则标签 |
| `references/command-examples.md` | 较少使用的命令场景 |
| `references/special-behaviors.md` | SFGE/ApexGuru/AppExchange/差异/大型扫描 |
| `references/vendor-file-handling.md` | 供应商文件检测和过滤 |
| `references/post-scan-workflows.md` | 步骤 7–9 — 查询、规则描述、规则列出 |

`examples/` 包含输出结构验证和命令模式（基本/大型/安全扫描，修复工作流）。
