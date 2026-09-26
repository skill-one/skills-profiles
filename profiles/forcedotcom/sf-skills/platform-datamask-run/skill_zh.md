# platform-datamask-run：Salesforce 数据掩码端到端操作

使用此技能在 **沙盒** 上 **操作** Salesforce 数据掩码功能：配置 PII 字段的掩码策略，启动掩码作业，轮询至终端状态，报告已掩码的记录，以及中止仍在进行的运行。

数据掩码是 **沙盒专用** — 在生产环境中运行/中止 REST 端点会返回 `403`（运行时沙盒保护）。在开始之前确认目标组织是沙盒。

## 此技能何时拥有任务

- 对配置的策略运行数据掩码作业
- 轮询掩码作业状态至完成
- 报告掩码记录计数 / 按对象结果
- 中止（取消）正在进行的掩码运行
- 创建或识别作业所针对的策略

当用户处于以下情况时，将任务委托给其他技能：
- 手写匿名化 Apex → `platform-apex-generate`
- 种子或生成测试数据 → `platform-data-manage`
- 部署无关元数据 → `platform-metadata-deploy`

---

## 首要注意事项：API 表面映射

最大的失败模式是假设数据掩码实体是普通的数据 API 对象。
**它们不是，且每个实体的表面都不同。** 在运行任何操作之前，请记住此表格——在此猜测会将 3 秒的作业变成 30 分钟的死胡同。

| 实体 | 它是什么 | 如何访问它 |
|------|-----------|------------------|
| `DataMaskPolicy` | 掩码策略外壳（配置） | **工具 API** 或 **元数据 API**（薄外壳：`<label>`/`<description>`/`<runOnRefresh>` 仅）— **不是**标准 SOQL/`sobject describe` |
| `DataMaskPolicyObject` | 策略目标的对象（包含可选的行过滤器） | **工具 API 仅** — 查询和插入；行子集“样本”运行设置 `FilterEnabled`+`WhereCriteria`（策略上没有 `sampleSize`） |
| `DataMaskPolicyField` | 字段及其掩码处理 | **工具 API 仅** — 查询和插入；处理列是 `MaskingCategory` + `MaskValue` |
| `DataMaskPolicyJobRun` | **作业**（一次掩码运行） | **标准 SOQL** — `sf data query` 适用 |
| `DataMaskPolicyJobRunDtl` | 按对象 **作业详细信息**（子项，外键 `DataMaskPolicyJobRunId`） | **标准 SOQL** |
| 启动运行 | — | **REST 运行 API** `POST /services/data/v67.0/platform/data-resilience/data-mask/policies/{policyId}/run` |
| 中止运行 | — | **REST 运行 API** `POST /services/data/v67.0/platform/data-resilience/data-mask/jobs/{jobRunId}/abort` |

具体来说：
- `sf sobject describe --sobject DataMaskPolicy` → **`NOT_FOUND`**（不要对标准 API 重试它）
- `SELECT ... FROM DataMaskPolicy` 通过 `sf data query` → **`INVALID_TYPE`**
- 通过工具 API 查询策略：`sf data query --use-tooling-api --query "SELECT Id, MasterLabel FROM DataMaskPolicy"`
- 通过标准 API 查询作业/作业详细信息：`sf data query --query "SELECT Id, Status FROM DataMaskPolicyJobRun"`

完整命令参考：`references/api-surface.md`。

---

## 选择与请求匹配的工作流

此技能有两个 **不同的工作流**。从用户请求中 upfront 选择一个，然后运行该工作流的 **每个** 步骤——两者都没有可选步骤：

| 用户想要... | 运行 | 结束时 |
|--------------------|-----|-----------|
| 配置/编辑策略并 **掩码** 记录；报告掩码了多少条记录 | **工作流 A — 掩码和报告**（下方） | 从详细信息行报告掩码计数 |
| **取消/中止** 掩码运行 | **工作流 B — 取消运行**（下方） | 作业状态确认 `canceled` |

通过请求中的动词选择。 "创建/编辑策略并运行它"、"掩码 PII"、"多少条记录被掩码了" → **仅工作流 A**。 "取消"、"中止"、"停止运行" → **工作流 B**。掩码和报告请求不包括取消：不要启动第二个作业来"演示"取消——未请求的运行会浪费一个完整的 ~5–10 分钟作业（见 A4 中的池底），并且是此任务运行超时且未完成它所请求的掩码计数的主要原因。

---

## 工作流 A — 掩码和报告

### A1. 确认沙盒 + 捕获组织上下文
验证组织是沙盒并获取运行 API 调用所需的实例 URL + 会话令牌：
```bash
sf org display --target-org <alias> --json
```

### A2. 识别或创建策略
优先重用现有策略（最快，无需部署）：
```bash
sf data query --use-tooling-api --target-org <alias> \
  --query "SELECT Id, DeveloperName, MasterLabel FROM DataMaskPolicy"
```
如果没有针对您需要的 Contact PII 的策略，请使用两步法编写一个（`DataMaskPolicy` 元数据形状是一个薄外壳；成员资格是工具插入的）：
1. **以 mdapi 格式元数据部署薄外壳**（`--metadata-dir` + `package.xml`；源格式 `--source-dir` 部署会失败 "Could not infer a metadata type"）。外壳仅携带 `<label>`、`<description>`、`<runOnRefresh>`。这会创建一个具有活动修订版的策略，A2 需要。
2. **工具插入** `DataMaskPolicyObject`（每个对象一个），然后是其 `DataMaskPolicyField` 行。每个字段行的处理是 `MaskingCategory`（`library`）+ `MaskValue`（一个 snake_case 令牌，如 `first_name`、`email`、`phone`）。没有 **`MaskingRuleType` 列**。

> 插入顺序很重要：一个工具创建的父项（没有活动修订版）会导致子项插入失败 `INSUFFICIENT_ACCESS_ON_CROSS_REFERENCE_ENTITY`。先元数据部署外壳。

见 `references/policy-authoring.md` 获取完整配方和 `MaskValue` 令牌表。为每个字段选择适当的 `MaskValue`；**不要** 一刀切替换。

### A3. 启动掩码运行（REST 运行 API）
```bash
printf '{}' > ./empty-body.json
sf api request rest \
  "/services/data/v67.0/platform/data-resilience/data-mask/policies/{policyId}/run" \
  --method POST --body @./empty-body.json --target-org <alias>
```
端点需要一个 **空的 JSON 正文**（`{}`）— `sf api request rest` 即使 API 不需要负载也需要 `--body`。**使用 `@` 前缀传递文件**（`--body @./empty-body.json`）；否则 API 会将字面路径作为正文发送并返回 `JSON_PARSER_ERROR`。`200` 返回 `jobRunId`、`policyId`、`status`（运行-API 状态是大写的，例如 `RUNNING`）和 `message: "Job started successfully"`。`409`/`CONFLICT` 表示该策略已经有正在进行的运行。

> **现在立即编写 `report.md`，在轮询之前——不要等到最后。** 掩码作业需要几分钟（见下文），最常见的任务得分为零的方式是在轮询期间没有输出文件写入。一旦您有了 `jobRunId`，请用已知的一切编写 `report.md`（策略 Id/标签、运行命令、`jobRunId`、状态 `RUNNING`，以及掩码计数的“轮询至完成…”占位符）。然后 **更新相同的文件**，一旦作业完成。一个存在并说明“仍在运行”的报告比没有文件更好；一个编造的计数比任何都糟——仅从详细信息行（A5）填写计数。

### A4. 轮询至终端状态（标准 SOQL）
轮询 `DataMaskPolicyJobRun.Status` 直至它达到一个 **终端** 值。不要报告运行中的状态作为最终状态。
- 运行中（预处理）：`pending`、`scheduled` — 作业已排队但 **尚未可中止**
- 运行中（工作）：`running` — 这是 **唯一** 可以中止的状态
- 终端：`completed`、`completed_with_errors`、`failed`
- 取消目标：`canceled`（单个 "l"）

**`pending` 不是 `running`。** 在 `pending`/`scheduled` 作业上取消返回 `409 CONFLICT`（"Job is not in a running state ... status=PENDING"）。您必须轮询直至状态确实是 `running` 才能取消——见工作流 B。

**作业很慢——预期几分钟，并使用捆绑脚本轮询。** 数据掩码在后台池/调度器上运行，具有一个 **~5–10 分钟的底部**：即使是 20 行的小作业通常在运行开始后几分钟内才能达到终端状态或发出详细信息行。这是固定的开销，**不是** 与行数成正比。围绕它计划运行——最大的失败模式是将作业视为即时，以紧密的间隔轮询，或者超时或编写“仍在等待”报告。

以单个命令运行 `scripts/poll-job.sh` — 不要手动编写 SOQL 轮询循环：
```bash
bash scripts/poll-job.sh <alias> <jobRunId>        # 默认：限制 600s (10 分钟)，20s 间隔
```
它在低频间隔上休眠，一旦出现真实的详细信息行就会短路，在标准输出上打印终端信号（`completed`/`failed`/`canceled`），并退出 `0`（超时为 `1`）。**调用一次并读取其结果——不要将其包装在自己的重试循环中**，并且不要以小于 10 秒的间隔轮询（它只是在无法更快完成作业的作业上消耗工具调用）。

**真实情况是详细信息行，而不是父项状态。** 父项 `DataMaskPolicyJobRun.Status` 可能 **滞后** — 它可能在掩码实际完成后一段时间内读取 `pending`/`running`。一旦存在 `total_records_masked`（或 `completed`）的 `DataMaskPolicyJobRunDtl` 行，掩码就完成了。`poll-job.sh` 已经包含了所有这些——有界间隔和超时，对真实详细信息行的短路，以及终端信号退出代码——因此您 **不需要** 在行内重新实现任何内容。运行轮询器一次，读取其退出信号，然后更新 `report.md`（您在轮询前编写的占位符），其中包含终端状态和来自 A5 的掩码计数。

### A5. 从作业详细信息对象报告结果
父项作业携带整体状态；**每个对象的掩码计数都存在于子项**
`DataMaskPolicyJobRunDtl`（通过 `DataMaskPolicyJobRunId` 链接）。报告具体计数，而不是编造的计数：
```bash
sf data query --target-org <alias> \
  --query "SELECT Id, DataMaskPolicyJobRunId, Status FROM DataMaskPolicyJobRunDtl WHERE DataMaskPolicyJobRunId = '<jobRunId>'"
```

**仅报告行字面上显示的内容——不要夸大粒度。** 详细信息行是 **对象级** 状态_update 条目（`loaded`、`completed`、`total_records_masked` 对于对象，例如 Contact）。它们不是 **按字段** 的行。因此，将按对象成功表述为观察到的事实（"Contact: 27/27 条记录被掩码，0 错误行"），但将字段级成功表述为 **推断**，而不是直接观察——说“没有返回按字段错误行，因此没有字段报告失败”，**而不是**“所有 5 个字段都成功”（数据没有携带支持此声明的按字段成功行）。将推断表述为观察是最常见的真实性错误。

---

## 工作流 B — 取消运行

当请求是 **取消/中止** 掩码运行时，使用此工作流。它针对的是 **当前正在进行的运行** — 取消是一个针对实时作业的按需操作；没有人只是为了取消而启动作业。步骤 B1–B4 都是必需的。

### B1. 确认沙盒 + 识别要取消的运行
确认组织是沙盒（`sf org display`）并获取要中止的运行的 `jobRunId` — 用户要求取消的那个。**也要捕获其 `DataMaskPolicyId`** — 如果您刚启动它，请使用该 ID；否则查询活动运行：
```bash
sf data query --target-org <alias> \
  --query "SELECT Id, Status, DataMaskPolicyId FROM DataMaskPolicyJobRun ORDER BY CreatedDate DESC LIMIT 5"
```
注意您选择的运行的 `DataMaskPolicyId`（`8dm` 前缀）— 这就是 A3 需要的 `<policyId>`。

### B2. 等待作业变为 `running`（唯一可取消状态）
只有在 `DataMaskPolicyJobRun.Status` 是 `running` 时才能取消。`pending`/`scheduled` 作业会 `409`；终端状态的一个已经完成了。使用捆绑脚本在其 **`running` 模式** 下轮询 `running` 窗口——它会立即退出，一旦状态读取 `running`（与默认模式不同，该模式等待终端状态），因此它不会阻止超过可取消窗口：
```bash
POLL_MODE=running bash scripts/poll-job.sh <alias> <jobRunId> 900 15
```
限制是 **900s (15 分钟)**，高于 ~5–10 分钟的调度底部，以便慢启动的作业仍然能被捕获。处理每个退出：
- **退出 `0`**（打印 `running`）→ 直接转到 B3。
- **退出 `3`** → 作业在捕获到 `running` 之前就达到了终端状态；取消窗口已过。针对 B1 中捕获的策略（A3 使用该 `<policyId>`）启动一个新运行，然后返回这里并轮询新的 `jobRunId`。
- **退出 `1`**（超时——限制到期）→ 重新查询作业状态：
  ```bash
  sf data query --target-org <alias> \
    --query "SELECT Id, Status FROM DataMaskPolicyJobRun WHERE Id = '<jobRunId>'"
  ```
  如果它仍然是非终端（`pending`/`scheduled`/`running`），重新运行轮询器 **一次**（相同的命令）以继续等待。如果它是终端的，将其视为退出 3 — 启动一个新运行（A3 使用 B1 的 `<policyId>`）并轮询新作业。

由于 ~5–10 分钟的池底部，`running` 窗口通常很宽，因此通常有时间捕获它；不要无延迟轮询。

> **如果没有运行当前正在进行**（作业已经完成，或者您必须端到端重现运行→取消流程），先用 A3 启动一个，然后返回这里——轮询它至 `running` 并取消 **那个** 活动作业。永远不要用已经终端的旧作业来“展示”取消；取消必须针对正在进行的运行。

### B3. 通过运行 API 取消
通过运行 API 取消——**不是**通过 DML/delete 作业记录：
```bash
sf api request rest \
  "/services/data/v67.0/platform/data-resilience/data-mask/jobs/{jobRunId}/abort" \
  --method POST --body @./empty-body.json --target-org <alias>
```
空的 JSON 正文（`{}`）通过带 `@` 前缀的文件，如上所示。`200` 返回 `status: "CANCELED"`（大写，来自运行 API）和 `message: "Job abort requested"`。`409` 表示作业不在 `running` 状态（通常仍然是 `pending`/`scheduled`）——返回 B2 并继续轮询。

### B4. 确认并报告取消
取消是异步的。**重新查询** `DataMaskPolicyJobRun` 并确认 `Status = canceled`（小写，来自 SOQL）之前报告取消成功。验证：
- [ ] 确认取消针对的是在查询状态为 `running` 时正在进行的作业。
- [ ] 取消后重新查询 `DataMaskPolicyJobRun` 并看到 `Status = canceled`。

---

## 高信号规则

| 规则 | 理由 |
|------|-----------|
| 每个 `sf` 命令 **裸** 运行——永远不要添加任何管道或重定向（`\|`、`\| python3`、`\| grep`、`2>&1`、`2>/dev/null`、`> file`） | `sf ... --json` 已经在标准输出上打印干净的 JSON；直接读取它。重定向/管道会触发一个无法绕过的 shell 安全性保护，导致整个运行无声地停滞以超时。永远不要用 `python3`/`grep`/`jq` 进行后处理，永远不要抑制 stderr——即使命令打印警告，`--json` 负载在标准输出上仍然是有效的；直接按原样解析它 |
| 永远不要在 `DataMaskPolicy*` 配置对象上使用标准 SOQL / `sobject describe` | 它们返回 `INVALID_TYPE` / `NOT_FOUND` — 使用工具 API 或 MDAPI |
| 从 `DataMaskPolicyJobRunDtl` 读取掩码计数，永远不要编造它们 | 子项详细信息是每个对象结果的来源 |
| 只有 `completed` / `completed_with_errors` / `failed` 才是终端 | 报告 `running`/`scheduled` 作为最终状态是错误的 |
| 仅通过运行-API 取消端点取消 | DML/delete 作业记录不是一个真正的取消，并且会破坏状态 |
| 始终在取消后重新查询状态并确认 `canceled` | 返回 200 的取消调用不是作业停止的证明 |
| 数据掩码仅在沙盒中运行 | 运行/取消端点在生产环境中返回 `403` |
| 使用 API 版本 `v67.0` 或更高版本，并且没有 `/connect/` 段 | 运行/取消端点是 `/services/data/v67.0/platform/data-resilience/data-mask/...` — 一个 `connect` 段或预 v67 版本会返回 `NOT_FOUND` |
| 通过 `scripts/poll-job.sh` 轮询（一次调用），永远不要手动编写 SOQL 循环 | 捆绑脚本有尝试限制并在出现真实详细信息行时短路；手动针对滞后父项状态的轮询是运行超时且没有报告的首要原因 |

---

## 易错点

| 问题 | 解决方案 |
|-------|------------|
| `sf sobject describe DataMaskPolicy` → `NOT_FOUND` | 它是工具/MDAPI 实体——使用 `--use-tooling-api` 查询，不要重试标准 API |
| `SELECT ... FROM DataMaskPolicy` → `INVALID_TYPE` | 相同原因——使用工具 API 查询策略；标准 API 仅适用于 `DataMaskPolicyJobRun`/`Dtl` |
| 运行启动返回 `409` | 该策略已经有正在进行的运行——轮询现有运行或等待它完成 |
| 取消返回 `409` "status=PENDING" | 作业仍然是 `pending`/`scheduled`，尚未 `running` — 继续轮询并在状态读取 `running` 时取消；不要放弃取消 |
| 小作业在您可以取消它之前完成 | 小沙盒上的 `running` 窗口是秒级的——启动一个新运行并紧密轮询；永远不要用之前取消的作业来伪造流程 |
| 取消返回 `200` 但 SOQL 状态仍然是 `running` | 取消是异步的——继续轮询 SOQL 状态直至 `canceled`；不要过早报告成功 |
| 运行 API 说 `CANCELED` 但 SOQL 说 `running` | 案例和表面不同：运行 API 是大写的，SOQL 选择列表是小写的。信任 SOQL 值以确定终端状态 |
| 作业“立即完成” | 重新检查：`scheduled` 不是终端的。轮询直至实际出现终端值 |
| 运行/取消端点 `NOT_FOUND` | 路径必须是 `/services/data/v67.0/platform/data-resilience/data-mask/...` — 没有 `/connect/` 段，并且版本 `v67.0`+（核心 262）。见 `references/api-surface.md` |

---

## 输出格式

报告您运行的工作流的 **部分** —— 不要为另一个工作流添加部分。**保持紧凑——在每个步骤中显示每个命令一次；不要附加一个重复已显示调用的“完整命令日志”。** 优先紧凑表格而不是散文；读者应该在第一屏内看到关键结果。

**工作流 A（掩码和报告）：**
1. **使用的策略**（Id + 标签，以及是否重用或创建）
2. **运行** — 作业 Id、最终终端状态、掩码记录计数（来自详细信息对象）。将轮询循环压缩为单行（例如 "polled 5×, `running`→`completed`"）；不要打印每行轮询。
3. **按对象结果** — 来自 `DataMaskPolicyJobRunDtl`。报告行实际携带的对象级计数；如果没有字段级错误行，请将其作为推断（“没有报告字段级错误”），而不是作为声称的字段级成功。见 A5 获取确切措辞。
4. **运行的命令** — 已经在上文中内联显示；这里只需列出尚未显示的任何命令。不要第二次粘贴完整序列。

**工作流 B（取消运行）：**
1. **已取消作业** — 作业 Id、它是在 `running` 时被取消的、它是通过运行-API 取消端点取消的，以及重新查询的 `canceled` 状态。
2. **运行的命令** — 如上所示，不要重复粘贴。

**确保高真实性的准确性说明：**
- 运行/取消 REST 响应返回一个 **15 个字符** 的 `jobRunId`（例如 `1aGXK0000000uob`）；SOQL 返回相同记录的 **18 个字符** 形式（例如 `1aGXK0000000uob2AA`）。它们是 **同一个作业** — 当两者都出现时，请注意这一点，而不是将它们作为两个 ID 呈现。
- 不要断言掩码计数、按字段结果或终端状态，您没有实际查询。报告中每个数字都必须追溯到命令日志中的查询结果。
