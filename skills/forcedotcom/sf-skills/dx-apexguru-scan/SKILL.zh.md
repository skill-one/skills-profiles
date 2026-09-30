---
name: dx-apexguru-scan
description: 通过 ApexGuru SFAP 扫描 API 对 Salesforce Apex 项目运行 ApexGuru 性能扫描。压缩项目的 Apex（任何布局），提交它，轮询完成，解码 base64 报告，并按规则分组展示性能反模式违规（循环中的 SOQL、循环中的 DML、Schema.getGlobalDescribe()、无 WHERE/LIMIT 的 SOQL、未使用的 SOQL 字段），包含严重程度、文件:行号和建议修复方案——明确标注为“仅静态分析”或“生产洞察”。当用户说“运行 ApexGuru”、“ApexGuru 扫描”、“检查 Apex 性能”、“查找治理限制/性能反模式”、“循环中的 SOQL”、“扫描我的 Apex 以进行性能分析”或“ApexGuru 性能洞察”时触发。禁止用于一般静态分析或安全扫描（请使用 dx-code-analyzer-run），禁止在未扫描的情况下修复代码，或用于将组织引入 ApexGuru。
---

# ApexGuru 性能扫描技能

## 关键：强制使用脚本

每个步骤——令牌解析、压缩打包、API 调用和报告解码——**必须**通过 `<skill_dir>/scripts/` 中的捆绑脚本执行。没有例外。

### 错误示范——切勿这样做：

```bash
# 错误：手动使用 curl 调用 API
curl -X POST https://api.salesforce.com/... -F file=@x.zip

# 错误：内联 base64 + jq 读取报告
cat raw.json | jq -r .report | base64 -d | jq '.[]'

# 错误：直接读取原始结果文件（报告是一个大型 base64 拆分块）
Read tool → apexguru-raw-*.json

# 错误：内联 node/python 解析违规项
node -e "const r = require('./raw.json'); ..."
```

### 正确做法——始终这样做：

```bash
# 推荐做法——一个命令执行三个步骤（打包→提交+轮询→解码+展示），并将准备好的报告作为其最终标准输出打印。
# 用于每次初始扫描：它不能只完成一半。
bash "<skill_dir>/scripts/scan.sh" "<project-root>"

# 可选地，将展示的 markdown 持久化到文件中：
bash "<skill_dir>/scripts/scan.sh" "<project-root>" --out ./apexguru-report.md
```

这三个底层脚本仍然存在，`scan.sh` 按顺序调用它们。
仅当对**已扫描结果的深入分析**（步骤 5）或您故意需要检查中间产物时，才单独调用它们：

```bash
# 等效的手动链（scan.sh 按此顺序运行这些脚本）：
bash "<skill_dir>/scripts/build-zip.sh" "<project-root>" "./apexguru-<TS>.zip"
bash "<skill_dir>/scripts/run-scan.sh"  "./apexguru-<TS>.zip" "./apexguru-raw-<TS>.json"
node "<skill_dir>/scripts/decode-report.js" "./apexguru-raw-<TS>.json" --present

# 深入子集，不重新扫描（重用 scan.sh 留下的原始文件，或将 --raw 传递给 scan.sh 以保持已知路径）：
node "<skill_dir>/scripts/decode-report.js" "./apexguru-raw-<TS>.json" --rule SOQL_IN_LOOP --full
node "<skill_dir>/scripts/decode-report.js" "./apexguru-raw-<TS>.json" --group file --top 5
```

`<skill_dir>` 是包含此 SKILL.md 的目录的绝对路径。
**切勿**使用 `./scripts/`——它相对于用户的当前工作目录解析，而不是技能目录。

任何过滤/排序/分组问题（“哪个文件的问题最多？”、“仅显示 SOQL 在循环中”、“按严重程度分解”）都通过对**相同的原始结果文件**重新运行 `decode-report.js` 并使用标志来回答——**永不重新扫描**，**永不手动解析 JSON**。

---

## 关键：原样展示 `--present` 输出——切勿压缩

`decode-report.js --present`（步骤 4）已经生成了最终的、准备展示的 markdown：严重程度图例、每个违规项的详细卡片（消息、代码、修复建议、资源链接），以及一个总结表格。该标准输出**就是**响应。
将其原样打印给用户——**不要**将其重写为更短的表格，**不要**将每个问题的卡片简化为仅总结表格，**不要**在用户要求“解释一个违规项”之前才包含消息/修复建议/资源。压缩它会使 `--present` 的整个目的失效。

归因**已经在该标准输出中**——总结行是声明模式（例如“ApexGuru（静态分析）处于活动状态。要解锁运行时智能……”）的确切输出。**不要**添加或附加您自己的归因句子（没有“归因：analysisMode：静态……”，没有命名组织，没有重申“静态仅限发现”）。脚本的行是完整、批准的措辞；添加您自己的内容会使输出非确定性且偏离主题。

### 错误示范——切勿这样做：

```text
主要问题（按严重程度降序）
#  严重程度   规则                      方法    行号
1  主要      使用测试方法关键字 legacy... 136
...
检测到的关键反模式：
- 循环中的 SOQL/DML (3 个违规项)
```
*(一个手动构建的总结，丢弃了每个消息/代码/修复建议——即使违规项有一个)*

```text
归因：analysisMode：静态——仅源代码分析。扫描的组织（ag-skills-org）未注册 ApexGuru 的完整运行时指标，因此这些是静态仅限发现。
```
*(一个代理生成的归因行附加到报告中——脚本的自己的总结行已经声明了模式；这个重复是非确定性的，并且命名了脚本从未访问过的组织)*

### 正确做法——始终这样做：

粘贴 `decode-report.js --present` 的完整标准输出——每个 `### Issue N` 卡片和关闭的 `## Summary` 表格——未经编辑，在一个响应中。

---

## 概述

ApexGuru 检测 Apex 中的**性能反模式**（SOQL/DML 在循环中、`Schema.getGlobalDescribe()`、没有 `WHERE`/`LIMIT` 的 SOQL、未使用的 SOQL 字段）。
此技能驱动 ApexGuru 的 **SFAP 扫描 API**：它将用户的 Apex（项目根目录下的所有 `.cls`/`.trigger`，任何布局）打包成 zip，提交它，轮询直到扫描完成，解码 base64 编码的报告，并以按规则分组的违规项、严重程度、`文件:行号` 和建议修复建议的形式展示。

**归因是强制性的。** API 返回 `analysisMode`：
- `static` → 仅源代码分析 → 标记结果 **“静态仅限”**。
- `full` → 使用已注册 ApexGuru 的组织的运行时指标进行丰富 → 标记结果 **“生产洞察”**。

`decode-report.js --present` 已经将其归因渲染到其总结行和标题（“静态仅限” / “生产洞察”）中——这满足了强制归因要求。打印该行作为**确切输出**；**不要**编写您自己的归因句子或命名组织。如果用户期望 `full` 但得到 `static`，脚本的静态模式行已经解释了组织未注册——引导他们查看它，而不是重申它（见错误处理）。

**在范围内：** 打包项目的 Apex、提交/轮询扫描、解码+展示违规项、过滤/分组现有结果、解决 API 错误。

**超出范围：** 通用静态分析/安全/代码检查（→ `dx-code-analyzer-run`，它将 ApexGuru 列为引擎）、应用修复到代码、将组织注册到 ApexGuru、铸造 SFAP 令牌。

---

## 前提条件

- **一个经过身份验证的 `sf` CLI 组织**（`sf org login web ...`）。`resolve-token.sh` 通过 `<instanceUrl>/ide/auth` 从它派生 SFAP JWT——这是正常的 IDE 会话路径。或者，设置 `APEXGURU_SFAP_TOKEN` / `APEXGURU_SFAP_TOKEN_FILE` 以直接提供 JWT（CI/无头）。组织是从令牌的 `tnk` 声明中派生的——不传递组织 ID。传递 `--org <alias>` 以选择特定组织。
  查看 `<skill_dir>/references/authentication.md`。如果无法解析令牌，脚本将返回一个清晰的错误并附带提示。
- **PATH 上的 `sf`、`bash`、`curl`、`zip`、`jq`、`node`**（标准 macOS/Linux 开发箱上）。
- **包含 Apex 的文件夹**——一个 sfdx 项目、一个 `force-app/` 子树或任何包含 `.cls`/`.trigger` 文件的文件夹。`build-zip.sh` 会收集它下面的所有 Apex，无论布局如何；API 会遍历整个存档。

---

## 工作流程

### 步骤 1：确定项目根目录

项目根目录是任何**包含 Apex** 的文件夹（通常是一个位于 `sfdx-project.json` 旁边的 sfdx 项目根目录，但一个 `force-app/` 子树或一个松散的 `.cls` 文件夹也可以工作）。如果用户提供了一个路径，请使用它；否则使用当前工作目录。`build-zip.sh` 会收集它下面的所有 `.cls`/`.trigger`（任何布局），如果不存在任何文件，则会清晰地失败。

### 步骤 2：打包项目

```bash
TS=$(date +%Y%m%d-%H%M%S)
bash "<skill_dir>/scripts/build-zip.sh" "<project-root>" "./apexguru-${TS}.zip"
```

输出 JSON 提供了 `zip`、`bytes`、`humanSize`、`apexFileCount`、`scanRoot`。脚本强制执行**200MB 压缩**限制，如果超出则会快速失败。出错时（`error`/`hint` 字段），传递提示并停止。

### 步骤 3：提交和轮询

```bash
bash "<skill_dir>/scripts/run-scan.sh" "./apexguru-${TS}.zip" "./apexguru-raw-${TS}.json"
```

- 如果用户想要更快/更便宜的运行，请添加 `--fast`（跳过 LLM 重型修复生成）。
- **端点遵循令牌的环境**——基础 URL 是从令牌的 `tnk` 声明派生的：生产组织会击中 `api.salesforce.com`，内部阶段/开发组织会击中 `stage.`/`dev.api.salesforce.com`。客户认证一个生产组织，因此他们始终击中生产；不需要额外的标志或配置。
- `--org <alias>` 选择从哪个经过身份验证的 `sf` 组织派生 JWT（省略以使用 CLI 的默认组织）。
- 进度（`QUEUED → RUNNING → SUCCEEDED`）流到 stderr；脚本大约每 15 秒轮询一次。默认上限是 10 分钟（`--max-polls`，`--interval` 调整）。
- 成功时，标准输出是一个单行 JSON 摘要，完整的原始正文写入到 `apexguru-raw-${TS}.json`。失败时，标准输出是 `{error, httpStatus, status, hint}`——传递提示。有关状态码详细信息，请参阅 `<skill_dir>/references/error-handling.md`。
- **仅前台运行。** 不要后台运行此命令；必须观察轮询输出。
- **一个成功的扫描不是终点。** 原始结果是 base64 拆分块，不是面向用户的答案。扫描成功后**不要**停止或报告“完成”——您**必须**继续步骤 4 以解码和展示报告。在步骤 3 结束回合会留下用户无法阅读的内容。

### 步骤 4：解码和展示

```bash
node "<skill_dir>/scripts/decode-report.js" "./apexguru-raw-${TS}.json" --present
```

`--present` 是用于展示的解码默认方式：它隐含 `--full`（不沉默覆盖）并直接打印准备好的 markdown。一个严重程度图例（次要 / 主要 / 关键，当 `analysisMode: full` 从生产指标丰富严重程度时加上提示标记），每个违规项一个 `### Issue N` 卡片（消息、当前代码、建议修复、帮助文档链接）用于非热点规则——按最差优先级限制在 `--top`（默认 10）内，并在标题中声明限制——以及一个总结 `## Summary` 表格，列出**每个**违规项，无论卡片限制如何。`ExpensiveMethods`（来自 `full` 模式的每个方法 CPU 热点排名，不是行级反模式）被折叠到它自己的排名“CPU 热点”表格中，而不是重复每个方法几乎相同的卡片。将此输出原样打印给用户——**立即展示——不要暂停以询问，也不要重新总结它为更短的表格。**

对于步骤 5 的深入分析（过滤/分组现有结果），裸的（非 `--present`）JSON 形式即可——见下文的阅读规则，您在运行脚本而不带 `--present` 时始终适用。

**不要：** 编写脚本代码，使用裸 `./scripts/...` 路径，内联解码 base64，`jq` `report` 字段，或直接读取原始文件。

#### 阅读裸（非 `--present`）`decode-report.js` 输出的说明

命令将一个 JSON 对象打印到标准输出。在展示任何内容之前按字段读取它——不要将部分视图视为完整：

1. **首先检查 `truncated`**，在所有其他内容之前。如果为 `true`，`groups` 被限制到最顶端的 `--top`（默认 10）规则，每个组的 `sample` 被限制到 3 个项，`topViolations` 被限制到 `--top` 项。**永远不要将 `truncated:true` 结果作为完整画面展示。** 除非用户明确要求快速/部分查看，否则跳过此步骤。
2. **声明从 `analysisMode`/`attribution` 的归因**——`static`/"静态仅限"或 `full`/"生产洞察"。根据上面的“归因是强制性的”要求，每个响应都必须声明。
3. **`serverViolationBreakdown`** 是原始 API 的内部规则代码统计（例如 `SOQL_IN_LOOP_1HOP`、`GGD`）——它是一个合理性检查总数（总和等于 `violationCount`），不是显示名称。**永远不要**向用户显示这些代码；使用人类可读的 `groups[].key` 名称（例如 `SoqlInALoopOneHop`、`SchemaGetGlobalDescribeNotEfficient`）。
4. **`severityCounts`**（顶层）是所有违规项的严重程度分布——用于总结表格。每个 `groups[]` 条目都有自己的 `severityCounts`，仅限于该规则。
5. **从 `groups` 构建“按规则违规项”表格**，每个条目一行：
   `key` → 规则，`count` → 计数，`severityCounts` → 严重程度，以及一个 `sample[0]`（或 `items[0]` 当 `--full` 时）→ 示例（`文件:行号`）。
6. **从 `topViolations` 构建“主要问题”表格**——已经按最严重程度排序。使用 `rule`、`severity`、`file:line` 和 `fixes` 的第一个条目（如果非空）作为建议修复。如果 `fixes` 为空，则省略该列的值，而不是编造一个修复。
7. **当用户要求解释特定违规项**（“这是什么意思”、“为什么被标记”）时，原样展示该违规项的 `message`（为什么的平语言）和 `resources[0]`（帮助文档 URL）——它们都存在于每个违规项对象中，但有意从步骤 5/6 的总结表格中省略，以保持这些可扫描。如果 `message` 为空，则回退到 `references/violation-catalog.md`。
8. **`fixes` 为 `[]`** 是预期的，不是错误——API 的 `suggestions` 字段（修复代码）不会为每个规则填充（特别是 `ExpensiveMethods`，一个 CPU 排名，没有单行修复）；不要说“没有可用的修复”，只需省略该列。
9. 使用 `--full`，每个组还携带一个 `items` 数组（该规则的所有违规项，而不仅仅是 3 项的 `sample`）——当用户想要一个规则的所有完整列表（“显示我所有的 SOQL 未使用字段”）时，使用 `items` 而不是 `sample`。

#### 展示模板（后备——仅在未使用 `--present` 时使用）

`--present`（如上一步所述的默认值）已经渲染了“阅读裸输出说明”部分中描述的完整严重程度图例 + 问题卡片 + 总结表格输出——只需原样打印其标准输出。只有在 `--present` 真的无法使用时（例如脚本/CI 环境中没有 markdown 渲染器）才手动构建表格：

**填充 `<静态仅限 | 生产洞察>` 标题占位符：** 从 `attribution` 字段派生标签（而不是单独依赖 `analysisMode`）——它已经编码了三种状态：
- “生产洞察” (`analysisMode: full` **与**运行时指标一起）——使用生产运行时指标丰富。
- “静态仅限” + `analysisMode: full` (**没有**运行时指标）——组织已注册，但此代码目前没有运行时数据；在 Scale Center 生成运行时报告。
- “静态仅限” + `analysisMode: static`——仅源代码。将组织注册到 ApexGuru 以获取生产洞察。

下方的 fenced block 是字面渲染的输出——替换真实值并打印；**不要**发出上述指导：

```text
## ApexGuru 扫描完成 — <静态仅限 | 生产洞察>

**在 Y 个文件中找到 X 个性能违规项。**

| 严重程度 | 计数 |
|----------|-------|
| 关键 (1) | X |
| 高 (2) | X |
| 中等 (3) | X |

### 按规则违规项
| 规则 | 计数 | 严重程度 | 示例 |
|------|-------|----------|---------|
| SOQL_IN_LOOP | 15 | 高 (2) | AccountService.cls:42 |
| DML_IN_LOOP | 8 | 关键 (1) | AccountService.cls:60 |
| GGD | 2 | 中等 (3) | Utils.cls:12 |

### 主要问题
| # | 规则 | 严重程度 | 文件:行号 | 建议修复 |
|---|------|-----|-----------|---------------|
| 1 | DML_IN_LOOP | 1 | AccountService.cls:60 | 收集记录；循环后一次 DML |
| ... up to 10 |

原始结果：`./apexguru-raw-<TS>.json`
```

根据结果大小缩放：
**0** → “未发现性能反模式”；**1–10** → 一个表格；**11+** → 严重程度计数 + 按规则表格 + 前 10 个。以原始结果路径结束。**不要**附加您自己的后续提议（没有“我可以不重新扫描进行深入……”，没有“按规则过滤 / 按文件分组 / 解释一个违规项”菜单）——`--present` 已经打印了脚本的“全部展示”页脚；这是完整的、批准的结束行，添加您自己的内容会使输出非确定性。
规则目录详细信息：`<skill_dir>/references/violation-catalog.md`。

### 步骤 5：深入分析结果（不重新扫描）

对**相同的原始文件**重新运行 `decode-report.js` 并使用标志：

| 用户说 | 参数 |
|-----------|-------|
| “只展示 SOQL 循环中的查询” | `--rule SOQL_IN_LOOP --full` |
| “只看严重的” | `--severity 1` |
| “AccountService.cls 里有什么？” | `--file AccountService.cls --full` |
| “按文件分组” / “哪个文件问题最多？” | `--group file --top 5` |
| “按严重程度细分” | `--group severity` |
| “给我看全部” | `--present`（或 `--full` 以获取原始 JSON） |

---

## 约束与常见陷阱

| 条目 | 原因 / 解决方法 |
|------|-----------------|
| 使用绝对路径 `<skill_dir>` 运行脚本 | `./scripts/` 是相对于用户当前工作目录解析的，而非技能目录 |
| 任意项目结构均可 | API 会遍历整个归档以查找 Apex；`build-zip.sh` 会收集根目录下所有 `.cls`/`.trigger`，无需 `force-app/` 目录 |
| 切勿内联解码 `report` | 它是一个大型 base64 数据块——始终使用 `decode-report.js` |
| 初始解码使用 `--present` | 它隐含 `--full`（无静默截断），并直接渲染可展示的 Markdown——包括严重程度图例、逐问题卡片、末尾摘要表——与参考 MCP 工具的展示密度保持一致 |
| 切勿重新扫描以过滤 | 步骤 5 会立即重新解码现有原始文件 |
| 归属信息已预先渲染 | `--present` 已输出模式行（“仅静态” / “生产洞察”）——请原样输出；切勿自行编写归属句或命名组织 |
| 期望为 `full` 却得到 `static` | 组织未接入 ApexGuru——告知用户，不要视为错误 |
| 401 / 403 / 404 / 400 | 令牌 / 组织所有权 / scanId / zip 问题——参见 references/error-handling.md |
| 仅限前台，轮询间隔约 15 秒 | 后台运行会丢失进度；扫描可能需要几分钟 |
| 令牌是机密信息 | `resolve-token.sh` 从不回显它；不要打印它或将其写入结果文件 |
| 不是安全/代码风格扫描器 | 如需 PMD/ESLint/安全扫描，请使用 `dx-code-analyzer-run` |

---

## 参考与脚本索引

**脚本**（通过 `bash`/`node` 配合绝对路径前缀 `<skill_dir>/` 执行，切勿 Read）：

| 文件 | 使用时机 |
|------|---------|
| `<skill_dir>/scripts/resolve-token.sh` | 解析 SFAP JWT 和基础 URL（由 run-scan.sh 调用） |
| `<skill_dir>/scripts/validate-token.js` | 本地（无网络）JWT 预检：环境变量/权限范围/过期时间（由 resolve-token.sh 调用） |
| `<skill_dir>/scripts/build-zip.sh` | 步骤 2——将项目的 Apex 收集为经过大小检查的 zip |
| `<skill_dir>/scripts/run-scan.sh` | 步骤 3——提交并轮询直至完成 |
| `<skill_dir>/scripts/decode-report.js` | 步骤 4–5——解码 base64 报告，分组/过滤违规 |

**参考**（按需阅读）：

| 文件 | 阅读时机 |
|------|----------|
| `references/authentication.md` | SFAP JWT 的来源；环境变量/文件配置 |
| `references/api-reference.md` | 端点契约、请求/响应结构、限制 |
| `references/violation-catalog.md` | ApexGuru 规则含义及典型修复方法 |
| `references/error-handling.md` | 400/401/403/404、FAILED、超时、静态与完整模式诊断 |

`examples/` 包含一个示例 SUCCEEDED 响应和一个解码摘要样本。
