# ApexGuru 性能扫描技能

## 关键：强制使用脚本

每个步骤——令牌解析、压缩打包、API 调用和报告解码——**必须**通过 `<skill_dir>/scripts/` 中的捆绑脚本执行。没有例外。

### 错误示范——绝对不要这样做：

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
# 推荐做法——一个命令运行所有三个步骤（打包 → 提交+轮询 → 解码+展示），并将准备好的报告作为其最终标准输出。
# 用于每个初始扫描：它不能半途而废。
bash "<skill_dir>/scripts/scan.sh" "<project-root>"

# 可选地，将展示的 markdown 持久化到文件中：
bash "<skill_dir>/scripts/scan.sh" "<project-root>" --out ./apexguru-report.md
```

这三个底层脚本仍然存在，`scan.sh` 按顺序调用它们。
仅当对已扫描结果进行**下钻分析**（步骤 5）或您故意需要检查中间产物时才单独调用它们：

```bash
# 等价的手动链（scan.sh 按此顺序运行这些脚本）：
bash "<skill_dir>/scripts/build-zip.sh" "<project-root>" "./apexguru-<TS>.zip"
bash "<skill_dir>/scripts/run-scan.sh"  "./apexguru-<TS>.zip" "./apexguru-raw-<TS>.json"
node "<skill_dir>/scripts/decode-report.js" "./apexguru-raw-<TS>.json" --present

# 对子集进行下钻，不重新扫描（重用 scan.sh 留下的原始文件，或将 --raw 传递给 scan.sh 以保持已知路径）：
node "<skill_dir>/scripts/decode-report.js" "./apexguru-raw-<TS>.json" --rule SOQL_IN_LOOP --full
node "<skill_dir>/scripts/decode-report.js" "./apexguru-raw-<TS>.json" --group file --top 5
```

`<skill_dir>` 是包含此 SKILL.md 的目录的绝对路径。
**绝对不要**使用 `./scripts/`——它针对的是用户的当前工作目录，而不是技能目录。

任何过滤/排序/分组问题（“哪个文件的问题最多？”、“仅显示 SOQL 在循环中”、“按严重程度细分”）都通过重新运行 `decode-report.js` 并对**相同的原始结果文件**使用标志来回答——**从不重新扫描**，**从不手动解析 JSON**。

---

## 关键：原样展示 `--present` 输出——绝对不要压缩

`decode-report.js --present`（步骤 4）已经生成了最终的、准备展示的 markdown：严重程度图例、每个违规项的详细卡片（消息、代码、修复建议、资源链接），以及一个总结表格。这个标准输出**就是**响应。
将其原样打印给用户——**不要**将其改写成更短的表格，**不要**将每个问题的卡片简化为仅总结表格，**不要**在用户询问“解释一个违规项”之前才包含消息/修复建议/资源。压缩它会使 `--present` 的整个目的失效。

归因**已经在那个标准输出中**——总结行是明确声明模式（例如“ApexGuru（静态分析）处于活动状态。要解锁运行时智能……”）的输出。**不要**在前面或后面添加您自己的归因句子（没有“归因：analysisMode: static…”、没有命名组织、没有重申“仅静态发现”）。脚本的行是完整、批准的措辞；添加您自己的内容会使输出变得非确定性且偏离主题。

### 错误示范——绝对不要这样做：

```text
主要问题（按严重程度降序排列）
#  严重程度   规则                      方法    行号
1  主要      使用测试方法关键字 legacy... 136
...
检测到的关键反模式：
- 循环中的 SOQL/DML (3 个违规项)
```
*(一个手动的总结，丢弃了每个消息/代码/修复——即使违规项有一个)*

```text
归因：analysisMode: static — 仅源代码分析。扫描的组织 (ag-skills-org) 未注册 ApexGuru 的完整运行时指标，因此这些是仅静态发现。
```
*(一个代理生成的归因行添加到报告中——脚本自己的总结行已经声明了模式；这个重复是非确定性的，并且命名了脚本从未访问过的组织)*

### 正确做法——始终这样做：

将 `decode-report.js --present` 的完整标准输出粘贴——每个 `### Issue N` 卡片和关闭的 `## Summary` 表格——未经编辑，在一个响应中。

---

## 概述

ApexGuru 检测 Apex 中的**性能反模式**（SOQL/DML 在循环中、`Schema.getGlobalDescribe()`、没有 `WHERE`/`LIMIT` 的 SOQL、未使用的 SOQL 字段）。
此技能驱动 ApexGuru 的 **SFAP 扫描 API**：它将用户的 Apex（项目根目录下的每个 `.cls`/`.trigger`，任何布局）打包成一个 zip，提交它，轮询直到扫描完成，解码 base64 编码的报告，并以按规则分组、严重程度、`文件:行号` 和建议修复建议的形式展示违规项。

**归因是强制性的。** API 返回 `analysisMode`：
- `static` → 仅源代码分析 → 标记结果 **“仅静态”**。
- `full` → 使用已注册到 ApexGuru 的组织的运行时指标进行丰富 → 标记结果 **“生产洞察”**。

`decode-report.js --present` 已经将其归因渲染到其总结行和标题（“仅静态” / “生产洞察”）中——这满足了强制归因要求。将其作为**精确输出**打印；**不要**编写您自己的归因句子或命名组织。如果用户期望 `full` 但得到 `static`，脚本中的静态模式行已经解释了组织未注册——指导用户，而不是重申它（见错误处理）。

**在范围内：** 打包项目的 Apex、提交/轮询扫描、解码+展示违规项、过滤/分组现有结果、解决 API 错误。

**超出范围：** 通用静态分析/安全/代码检查（→ `dx-code-analyzer-run`，它将 ApexGuru 列为引擎）、对代码应用修复、将组织注册到 ApexGuru、铸造 SFAP 令牌。

---

## 前提条件

- **一个经过身份验证的 `sf` CLI 组织** (`sf org login web ...`)。`resolve-token.sh` 通过 `<instanceUrl>/ide/auth` 从它派生 SFAP JWT——这是正常的 IDE 会话路径。或者，设置 `APEXGURU_SFAP_TOKEN` / `APEXGURU_SFAP_TOKEN_FILE` 以直接提供 JWT（CI/无头）。组织是从令牌的 `tnk` 声明中派生的——不需要传递组织 ID。传递 `--org <alias>` 以选择特定组织。参见 `<skill_dir>/references/authentication.md`。如果无法解析令牌，脚本会返回一个清晰的错误并附带提示。
- **`sf`、`bash`、`curl`、`zip`、`jq`、`node`** 在 PATH 上（macOS/Linux 开发箱的标准配置）。
- **一个包含 Apex 的文件夹**——一个 sfdx 项目、一个 `force-app/` 子树，或任何包含 `.cls`/`.trigger` 文件的文件夹。`build-zip.sh` 会收集它下面的所有 Apex（无论布局如何）；API 会遍历整个存档。

---

## 工作流程

### 步骤 1：确定项目根目录

项目根目录是任何**包含 Apex** 的文件夹（通常是一个位于 `sfdx-project.json` 旁边的 sfdx 项目根目录，但一个 `force-app/` 子树或一个松散的 `.cls` 文件夹也可以工作）。如果用户提供了路径，请使用它；否则使用当前工作目录。`build-zip.sh` 会收集它下面的所有 `.cls`/`.trigger`（任何布局），如果不存在任何文件则会明确失败。

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
- **端点遵循令牌的环境**——基础 URL 是从令牌的 `tnk` 声明派生的：生产组织会击中 `api.salesforce.com`，内部阶段/开发组织会击中 `stage.`/`dev.api.salesforce.com`。客户认证的是生产组织，因此他们始终击中生产；不需要额外的标志或配置。
- `--org <alias>` 选择从哪个经过身份验证的 `sf` 组织派生 JWT（省略以使用 CLI 的默认组织）。
- 进度（`QUEUED → RUNNING → SUCCEEDED`）流到 stderr；脚本大约每 15 秒轮询一次。默认上限是 10 分钟（`--max-polls`, `--interval` 调整）。
- 成功时，标准输出是一个单行 JSON 摘要，完整的原始正文写入到 `apexguru-raw-${TS}.json`。失败时，标准输出是 `{error, httpStatus, status, hint}`——传递提示。有关状态码的具体信息，请参阅 `<skill_dir>/references/error-handling.md`。
- **仅前台运行。** 不要后台运行这个；必须观察轮询输出。
- **成功的扫描不是终点。** 原始结果是 base64 拆分块，不是面向用户的答案。扫描成功后**不要**停止或报告“完成”——您**必须**继续步骤 4 以解码和展示报告。在步骤 3 结束回合会留下用户无法阅读的内容。

### 步骤 4：解码和展示

```bash
node "<skill_dir>/scripts/decode-report.js" "./apexguru-raw-${TS}.json" --present
```

`--present` 是解码以展示的默认方式：它隐含 `--full`（不静默覆盖）并直接打印准备好的 markdown——严重程度图例（次要 / 主要 / 严重，当 `analysisMode: full` 从生产指标丰富严重程度时会添加提示标记）、每个违规项的 `### Issue N` 卡片（消息、当前代码、建议修复、帮助文档链接）用于非热点规则——最多 `--top`（默认 10）最差优先，并在标题中说明上限——以及一个关闭的 `## Summary` 表格，列出**每个**违规项，无论卡片上限如何。`ExpensiveMethods`（来自 `full` 模式的每个方法的 CPU 热点排名，不是行级反模式）被折叠到它自己的排名“CPU 热点”表格中，而不是为每个方法重复几乎相同的卡片。将此输出原样打印给用户——**立即展示**——不要暂停以询问，也不要将其重新总结成更短的表格。

对于步骤 5 的下钻（过滤/分组现有结果），裸的（非 `--present`）JSON 形式即可——见下文的阅读规则，您在运行脚本而不带 `--present` 时始终适用。

**不要：** 编写脚本代码，使用裸 `./scripts/...` 路径，内联解码 base64，`jq` `report` 字段，或直接读取原始文件。

#### 阅读裸（非 `--present`）`decode-report.js` 输出的说明

命令将一个 JSON 对象打印到标准输出。在展示任何内容之前按字段读取它——不要将部分视图视为完整：

1. **首先检查 `truncated`**，在查看任何其他内容之前。如果 `true`，`groups` 被限制为最多 `--top`（默认 10）规则，每个组的 `sample` 被限制为最多 3 个项，`topViolations` 被限制为最多 `--top` 项。**永远不要将 `truncated:true` 的结果作为完整画面展示。** 如果用户明确要求快速/部分查看，可以跳过此步骤。重新运行相同的命令并使用 `--full` 作为输出。
2. **从 `analysisMode`/`attribution` 状态归因**——`static`/"仅静态"或 `full`/"生产洞察"。根据“归因是强制性的”部分，每个响应都必须这样做。
3. **`serverViolationBreakdown`** 是原始 API 的内部规则代码统计（例如 `SOQL_IN_LOOP_1HOP`、`GGD`）——它是一个 Sanity 检查总数（总和等于 `violationCount`），不是显示名称。**永远不要**向用户显示这些代码；使用人类可读的 `groups[].key` 名称（例如 `SoqlInALoopOneHop`、`SchemaGetGlobalDescribeNotEfficient`）。
4. **`severityCounts`**（顶层）是所有违规项的严重程度分布——用于总结表格。每个 `groups[]` 条目都有其自己的 `severityCounts`，仅限于该规则。
5. **从 `groups` 构建“按规则违规项”表格**，每条记录一行：
   `key` → 规则，`count` → 计数，`severityCounts` → 严重程度，以及一个 `sample[0]`（或 `items[0]` 当 `--full` 时）→ 示例 (`文件:行号`)。
6. **从 `topViolations` 构建“主要问题”表格**——已经按最严重程度排序。使用 `rule`、`severity`、`文件:行号` 和 `fixes` 的第一个条目（如果非空）作为建议修复。如果 `fixes` 为空，则省略该列的值，而不是编造一个修复。
7. **当用户要求解释特定违规项**（“这是什么意思”、“为什么被标记”）时，原样展示该违规项的 `message`（为什么的平语文本）和 `resources[0]`（帮助文档 URL）——两者都存在于每个违规项对象中，但有意排除在步骤 5/6 的总结表格中以保持可扫描性。只有在 `message` 为空时才回退到 `references/violation-catalog.md`。
8. **`fixes` 为 `[]`** 是预期的，不是错误——API 的 `suggestions` 字段（修复代码）并非为每个规则都填充（特别是 `ExpensiveMethods`，一个 CPU 排名，没有单行修复）；不要说“没有可用的修复”，只需省略该列。
9. 使用 `--full` 时，每个组还携带一个 `items` 数组（该规则的所有违规项，而不仅仅是 3 项的 `sample`）——当用户想要一个规则的所有完整列表（“显示我所有 SOQL 未使用字段的违规项”）时，使用 `items` 而不是 `sample`。

#### 展示模板（后备——仅当不使用 `--present` 时）

`--present`（如上步骤 4 中所述的默认值）已经渲染了“阅读裸输出说明”部分中描述的完整严重程度图例 + 问题卡片 + 总结表格输出——只需原样打印其标准输出。只有在 `--present` 真的无法使用时（例如在无法使用 markdown 渲染器的脚本/CI 环境中）才手动构建表格：

**填充 `<仅静态 | 生产洞察>` 标题占位符：** 从 `attribution` 字段（而不是单独的 `analysisMode`）派生标签——它已经编码了三种状态：
- "生产洞察" (`analysisMode: full` **与**生产运行时指标一起使用）——使用生产运行时指标进行丰富。
- "仅静态" + `analysisMode: full` (**没有**生产运行时指标）——组织已注册，但此代码目前没有运行时数据；在 Scale Center 生成运行时报告。
- "仅静态" + `analysisMode: static`——仅源代码。将组织注册到 ApexGuru 以获取生产洞察。

下面的 fenced block 是字面渲染的输出——替换真实值并打印；**不要**发出上述指导：

```text
## ApexGuru 扫描完成 — <仅静态 | 生产洞察>

**在 Y 个文件中找到 X 个性能违规项。**

| 严重程度 | 计数 |
|----------|-------|
| 严重 (1) | X |
| 高 (2) | X |
| 中等 (3) | X |

### 按规则违规项
| 规则 | 计数 | 严重程度 | 示例 |
|------|-------|----------|---------|
| SOQL_IN_LOOP | 15 | 高 (2) | AccountService.cls:42 |
| DML_IN_LOOP | 8 | 严重 (1) | AccountService.cls:60 |
| GGD | 2 | 中等 (3) | Utils.cls:12 |

### 主要问题
| # | 规则 | 严重程度 | 文件:行号 | 建议修复 |
|---|------|-----|-----------|---------------|
| 1 | DML_IN_LOOP | 1 | AccountService.cls:60 | 收集记录；循环后一次 DML |
| ... up to 10 |

原始结果：`./apexguru-raw-<TS>.json`
```

根据结果大小调整：
**0** → “未发现性能反模式”；**1–10** → 一个表格；**11+** → 严重程度计数 + 按规则表格 + 前 10 个。以原始结果路径结束。**不要**添加您自己的后续提议（没有“无需重新扫描即可下钻…”、没有“按规则过滤 / 按文件分组 / 解释一个违规项”菜单）——`--present` 已经打印了脚本的“全部展示”页脚；这是完整的、批准的结束行，添加您自己的内容会使输出变得非确定性。
规则目录详细信息：`<skill_dir>/references/violation-catalog.md`。

### 步骤 5：下钻结果（无需重新扫描）

使用**相同的原始文件**重新运行 `decode-report.js` 并使用标志：

| 用户说 | 标志 |
|-----------|-------|
| "仅显示 SOQL 在循环中" | `--rule SOQL_IN_LOOP --full` |
| "仅关键项" | `--severity 1` |
| "AccountService.cls 中有什么？" | `--file AccountService.cls --full` |
| "按文件分组" / "哪个文件最差？" | `--group file --top 5` |
| "按严重程度细分" | `--group severity` |
| "显示我所有内容" | `--present` (或 `--full` 以获取裸 JSON) |

---

## 限制和注意事项

| 项目 | 原因 / 修复 |
|------|-----------|
| 使用绝对 `<skill_dir>` 路径运行脚本 | `./scripts/` 针对的是用户的当前工作目录，而不是技能目录 |
| 任何项目布局都可以 | API 会遍历整个存档以查找 Apex；`build-zip.sh` 会收集根目录下的所有 `.cls`/`.trigger`（任何布局），不需要 `force-app/` |
| 绝对不要内联解码 `report` | 它是一个大型 base64 拆分块——始终使用 `decode-report.js` |
| 使用 `--present` 进行初始解码 | 隐含 `--full`（不静默覆盖）并直接打印准备好的 markdown——严重程度图例、每个问题的卡片、关闭的总结表格——镜像参考 MCP 工具的展示密度 |
| 绝对不要重新扫描以过滤 | 步骤 5 重新解码现有的原始文件，立即完成 |
| 归因是预渲染的 | `--present` 已经打印了模式行（“仅静态” / “生产洞察”）——将其作为精确输出打印；**不要**编写您自己的归因句子或命名组织 |
| `static` 当期望 `full` | 组织未注册到 ApexGuru —— 指导用户，不要将其视为错误 |
| 401 / 403 / 404 / 400 | 令牌 / 组织所有权 / 扫描 ID / zip 问题 —— 见参考/error-handling.md |
| 仅前台运行，~15 秒轮询 | 后台运行会丢失进度；扫描可能需要几分钟 |
| 令牌是一个秘密 | `resolve-token.sh` 从不回显它；**不要**打印它或写入结果文件 |
| 不是安全/代码检查器 | 对于 PMD/ESLint/安全，使用 `dx-code-analyzer-run` |

---

## 参考 & 脚本索引

**脚本**（通过 `bash`/`node` 使用绝对 `<skill_dir>/` 前缀执行，**不要**使用 Read）：

| 文件 | 使用时机 |
|------|-------------|
| `<skill_dir>/scripts/resolve-token.sh` | 解析 SFAP JWT + 基础 URL（由 run-scan.sh 调用） |
| `<skill_dir>/scripts/validate-token.js` | 本地（无网络）JWT 快速预检：环境/范围/过期（由 resolve-token.sh 调用） |
| `<skill_dir>/scripts/build-zip.sh` | 步骤 2 — 将项目的 Apex 收集到经过大小检查的 zip 中 |
| `<skill_dir>/scripts/run-scan.sh` | 步骤 3 — 提交 + 轮询至完成 |
| `<skill_dir>/scripts/decode-report.js` | 步骤 4–5 — 解码 base64 报告，分组/过滤违规项 |

**参考**（按需阅读）：

| 文件 | 阅读时机 |
|------|--------------|
| `references/authentication.md` | SFAP JWT 来自何方；环境变量/文件设置 |
| `references/api-reference.md` | 端点合同、请求/响应形状、限制 |
| `references/violation-catalog.md` | ApexGuru 规则含义和典型修复 |
| `references/error-handling.md` | 400/401/403/404，FAILED，超时，静态 vs full 诊断 |

`examples/` 包含一个成功的响应示例和一个解码摘要示例。
