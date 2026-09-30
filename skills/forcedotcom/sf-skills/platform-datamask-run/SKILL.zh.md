---
name: platform-datamask-run
description: "在沙盒中对 Data Mask 进行端到端操作：配置对个人身份信息（PII）的掩码策略，运行掩码作业，轮询直至完成，报告掩码记录结果，并中止正在进行的运行。当用户需要运行、监控或取消 Salesforce Data Mask 作业、掩码沙盒 PII 数据，或与 DataMaskPolicy / DataMaskPolicyJobRun 协作时使用。  \n\n触发条件：用户运行数据掩码作业、掩码沙盒 PII、轮询掩码状态、报告掩码记录，或中止正在进行的掩码操作。  \n\n不触发条件：手动编写匿名化 Apex（使用 platform-apex-generate）、生成测试数据（使用 platform-data-manage），或部署无关元数据（使用 platform-metadata-deploy）。"
---

# platform-datamask-run：Salesforce 数据脱敏端到端操作

使用此技能在 **沙盒** 上 **操作** Salesforce 数据脱敏功能：配置 PII 字段的脱敏策略，启动脱敏作业，轮询至终端状态，报告哪些记录被脱敏，以及中止正在进行的运行。

数据脱敏是 **沙盒专用** — 在生产环境中运行/中止 REST 端点会返回 `403`（运行时沙盒保护）。在开始之前确认目标组织是沙盒。

## 此技能何时拥有任务

- 对配置的策略运行数据脱敏作业
- 轮询脱敏作业状态至完成
- 报告脱敏记录计数/按对象结果
- 中止（取消）正在进行的脱敏运行
- 创建或识别作业所针对的策略

当用户执行以下操作时，将任务委派给其他技能：
- 手写匿名化 Apex → `platform-apex-generate`
- 种子或生成测试数据 → `platform-data-manage`
- 部署无关元数据 → `platform-metadata-deploy`

---

## 首先要正确理解的一件事：API 表面映射

最大的失败模式是假设数据脱敏实体是普通的数据 API 对象。
**它们不是，且每个实体的表面都不同。** 在运行任何操作之前，请记住此表格——在这里猜测会导致 3 秒的作业变成 30 分钟的死胡同。

| 实体 | 它是什么 | 你如何访问它 |
|------|----------|--------------|
| `DataMaskPolicy` | 脱敏策略外壳（配置） | **工具 API** 或 **元数据 API**（薄外壳：`<label>`/`<description>`/`<runOnRefresh>` 仅）— **不是**标准 SOQL/`sobject describe` |
| `DataMaskPolicyObject` | 策略针对的对象（包含可选的行过滤器） | **工具 API 仅** — 查询和插入；行子集“样本”运行设置 `FilterEnabled`+`WhereCriteria`（策略上没有 `sampleSize`） |
| `DataMaskPolicyField` | 字段及其脱敏处理 | **工具 API 仅** — 查询和插入；处理列是 `MaskingCategory` + `MaskValue` |
| `DataMaskPolicyJobRun` | **作业**（一次脱敏运行） | **标准 SOQL** — `sf data query` 可用 |
| `DataMaskPolicyJobRunDtl` | 按对象的 **作业详细信息**（子项，外键 `DataMaskPolicyJobRunId`） | **标准 SOQL** |
| 启动运行 | — | **REST 运行 API** `POST /services/data/v67.0/platform/data-resilience/data-mask/policies/{policyId}/run` |
| 中止运行 | — | **REST 运行 API** `POST /services/data/v67.0/platform/data-resilience/data-mask/jobs/{jobRunId}/abort` |

具体来说：
- `sf sobject describe --sobject DataMaskPolicy` → **`NOT_FOUND`**（不要对标准 API 重试它）
- `SELECT ... FROM DataMaskPolicy` 通过 `sf data query` → **`INVALID_TYPE`**
- 通过工具 API 查询 **策略**：`sf data query --use-tooling-api --query "SELECT Id, MasterLabel FROM DataMaskPolicy"`
- 通过标准 API 查询 **作业 / 作业详细信息**：`sf data query --query "SELECT Id, Status FROM DataMaskPolicyJobRun"`

完整命令参考：`references/api-surface.md`。

---

## 选择与请求匹配的工作流

此技能有两个 **不同的工作流**。根据用户请求， upfront 选择其中一个，然后运行该工作流的 **每个** 步骤——两者都没有可选步骤：

| 用户想要… | 运行 | 结束时 |
|----------|-----|-------|
| 配置/编辑策略并 **脱敏** 记录；报告脱敏了多少条记录 | **工作流 A — 脱敏和报告**（下方） | 从详细信息行报告脱敏计数 |
| **取消 / 中止** 脱敏运行 | **工作流 B — 取消运行**（下方） | 确认作业状态为 `canceled` |

根据请求中的动词进行选择。"创建/编辑策略并运行它"、"脱敏 PII"、"多少条记录被脱敏" → **仅工作流 A**。"中止"、"取消"、"停止运行" → **工作流 B**。一个脱敏和报告请求 **不包括** 中止：不要启动第二个作业来“展示”取消——一个未请求的运行会浪费一个完整的 ~5–10 分钟作业（见 A4 中的池底），并且是这个任务在完成它所请求的脱敏计数之前超时的主要原因。

---

## 工作流 A — 脱敏和报告

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
如果没有针对您需要的 Contact PII 的策略，请使用 **两步** 配方编写一个（`DataMaskPolicy` 元数据形状是一个薄外壳；成员是工具插入的）：
1. **以 mdapi 格式元数据部署薄外壳**（`--metadata-dir` + `package.xml`；源格式 `--source-dir` 部署会失败“无法推断元数据类型”）。外壳仅携带 `<label>`、`<description>`、`<runOnRefresh>`。这会创建一个具有活动修订版的策略，A2 需要。
2. **工具插入** `DataMaskPolicyObject`（每个对象一个），然后是其 `DataMaskPolicyField` 行。每个字段行的处理是 `MaskingCategory`（`library`）+ `MaskValue`（一个 snake_case 令牌，如 `first_name`、`email`、`phone`）。**没有** `MaskingRuleType` 列。

> 插入顺序很重要：一个工具创建的父项（没有活动修订版）会导致子项插入失败 `INSUFFICIENT_ACCESS_ON_CROSS_REFERENCE_ENTITY`。首先元数据部署外壳。

有关完整配方和 `MaskValue` 令牌表的详细信息，请参阅 `references/policy-authoring.md`。为每个字段选择适当的 `MaskValue`；**不要** 一刀切替换。

### A3. 启动脱敏运行（REST 运行 API）
```bash
printf '{}' > ./empty-body.json
sf api request rest \
  "/services/data/v67.0/platform/data-resilience/data-mask/policies/{policyId}/run" \
  --method POST --body @./empty-body.json --target-org <alias>
```
端点需要一个 **空的 JSON 正文** (`{}`) — `sf api request rest` 即使 API 不需要负载也需要 `--body` 在 POST 上。**使用 `@` 前缀传递文件** (`--body @./empty-body.json`)；否则，字面路径会被发送为正文，API 会返回 `JSON_PARSER_ERROR`。返回 `200` 会返回 `jobRunId`、`policyId`、`status`（运行-API 状态是大写的，例如 `RUNNING`）和 `message: "Job started successfully"`。`409`/`CONFLICT` 表示该策略已经有正在进行的运行。

> **现在立即编写 `report.md`，在轮询之前——不要等到最后。** 脱敏作业需要几分钟（见下文），而这个任务得分为零的最常见方式是在轮询期间 **根本没有输出文件**。一旦你有了 `jobRunId`，请用目前已知的一切编写 `report.md`（策略 ID/标签、运行命令、`jobRunId`、状态 `RUNNING`，以及“轮询至完成…”的占位符用于脱敏计数）。然后 **更新** 同一个文件。一个存在并说明“仍在运行”的报告比没有文件更好；一个编造的计数比任何东西都糟——只有从 A5 的详细信息行填充计数。

### A4. 轮询至终端状态（标准 SOQL）
轮询 `DataMaskPolicyJobRun.Status` 直至它达到 **终端** 值。**不要** 报告运行中的状态作为最终状态。
- 运行中（预处理）：`pending`、`scheduled` — 作业已排队，但 **尚未可中止**
- 运行中（工作）：`running` — 这是 **唯一** 可以中止的状态
- 终端：`completed`、`completed_with_errors`、`failed`
- 中止目标：`canceled`（单一“l”）

**`pending` 不是 `running`。** 在 `pending`/`scheduled` 作业上中止返回 `409 CONFLICT`（“作业不在运行状态 ... status=PENDING”）。你必须轮询直至状态确实是 `running` 才能中止——见工作流 B。

**作业很慢——预期几分钟，并使用捆绑脚本轮询。** 数据脱敏在后台池/调度器上运行，具有 **~5–10 分钟的底部**：即使一个很小的（20 行）作业通常在运行开始后几分钟内才能达到终端状态或发出详细信息行。这是固定的开销，**不是** 与行数成正比。围绕它计划运行——最大的失败模式是将作业视为即时，以紧密的间隔轮询，或者超时或编写“仍在等待”报告。

以单个命令运行 `scripts/poll-job.sh` — **不要** 手动编写 SOQL 轮询循环：
```bash
bash scripts/poll-job.sh <alias> <jobRunId>        # 默认：限制 600s (10 分钟)，20s 间隔
```
它在低频间隔上睡眠，一旦出现真实的确切详细信息行就会短路，在 stdout 上打印终端信号（`completed`/`failed`/`canceled`），并退出 `0`（超时为 `1`）。**调用一次并读取其结果——不要将其包装在自己的重试循环** 中，并且不要在 10 秒以下的时间间隔轮询（它只是在无法更快完成作业的工具调用上燃烧）。

**真实情况是详细信息行，而不是父级状态。** 父级 `DataMaskPolicyJobRun.Status` 可能 **滞后** — 它可能在实际脱敏完成后一段时间内读取 `pending`/`running`。一旦存在 `total_records_masked`（或 `completed`）`DataMaskPolicyJobRunDtl` 行，脱敏就完成了。`poll-job.sh` 已经编码了所有这些——有界间隔和超时，真实情况详细信息行的短路，以及终端信号退出代码——所以你 **不需要** 在行内重新实现任何内容。运行轮询器一次，读取其退出信号，然后更新 `report.md`（你在轮询前编写的占位符文件）以包含终端状态和来自 A5 的脱敏计数。

### A5. 从作业详细信息对象报告结果
父作业携带整体状态；**按对象的脱敏计数存在于子对象**
`DataMaskPolicyJobRunDtl`（通过 `DataMaskPolicyJobRunId` 链接）。报告具体计数，而不是编造的计数：
```bash
sf data query --target-org <alias> \
  --query "SELECT Id, DataMaskPolicyJobRunId, Status FROM DataMaskPolicyJobRunDtl WHERE DataMaskPolicyJobRunId = '<jobRunId>'"
```

**只报告行字面显示的内容——不要夸大粒度。** 详细信息行是 **按对象** 状态_update 条目（例如 Contact 的 `loaded`、`completed`、`total_records_masked`）。它们不是按字段行。所以将按对象成功作为观察到的事实陈述（“Contact：27/27 条记录被脱敏，0 错误行”），但将字段级成功表述为 **推断**，而不是直接观察——说“没有返回按字段错误行，所以没有字段报告失败”，**而不是**“所有 5 个字段都成功”（数据没有携带支持该声明的按字段成功行）。将推断作为观察结果夸大是最常见的真实性错误。

---

## 工作流 B — 取消运行

当请求是 **中止/取消** 脱敏运行时，使用此工作流。它针对正在 **进行中的运行** — 中止是对一个实时作业的按需操作；没有人只是为了取消而启动作业。步骤 B1–B4 都是必需的。

### B1. 确认沙盒 + 识别要取消的运行
确认组织是沙盒（`sf org display`）并获取要中止的运行的 `jobRunId` — 用户要求取消的那个。**也要捕获其 `DataMaskPolicyId`** — 你需要它来在错过中止窗口时（B2 退出 3 / 退出 1）启动一个替代运行。如果他们刚启动它，就使用那个 ID；否则查询活动运行：
```bash
sf data query --target-org <alias> \
  --query "SELECT Id, Status, DataMaskPolicyId FROM DataMaskPolicyJobRun ORDER BY CreatedDate DESC LIMIT 5"
```
注意您选择的运行的 `DataMaskPolicyId`（`8dm` 前缀）— 那就是A3需要的 `<policyId>`。

### B2. 等待作业变为 `running`（唯一可中止的状态）
只有在 `DataMaskPolicyJobRun.Status` 是 `running` 时才能中止。一个 `pending`/`scheduled` 作业会 `409`；一个终端作业已经完成了。使用捆绑轮询器在其 **`running` 模式** 下轮询 `running` 窗口——它会立即退出，因为状态读取 `running`（与默认模式不同，该模式等待终端状态），所以它不会阻止中止窗口过去：
```bash
POLL_MODE=running bash scripts/poll-job.sh <alias> <jobRunId> 900 15
```
限制是 **900s (15 分钟)**，高于 ~5–10 分钟的调度底部，以便慢速启动的作业仍然被捕获。处理每个退出：
- **退出 `0`**（打印 `running`）→ 直接转到 B3。
- **退出 `3`** → 作业在捕获 `running` 之前竞赛到终端状态；中止窗口已过去。针对 B1 中捕获的策略（A3 使用 `<policyId>`）启动一个新运行，然后返回这里并轮询新的 `jobRunId`。
- **退出 `1`**（超时——限制到期）→ 重新查询作业状态：
  ```bash
  sf data query --target-org <alias> \
    --query "SELECT Id, Status FROM DataMaskPolicyJobRun WHERE Id = '<jobRunId>'"
  ```
  如果它仍然是非终端（`pending`/`scheduled`/`running`），重新运行轮询器 **一次**（相同的命令）以继续等待。如果它是终端的，像退出 3 一样处理——使用 B1 的 `<policyId>` 启动一个新运行，并轮询新作业。

由于 ~5–10 分钟的池底部，`running` 窗口通常很宽，所以通常有时间捕获它；不要无延迟地轮询。

> **如果没有运行当前正在进行**（作业已完成，或者您必须端到端重现运行→取消流程），首先使用 A3 启动一个，然后返回这里——轮询它至 `running` 并中止 **该** 活动作业。永远不要用已经终端的旧作业来“展示”取消；中止必须针对实际活动的运行。

### B3. 通过运行 API 中止
通过运行 API 中止——**不是**通过 DML/delete 作业记录：
```bash
sf api request rest \
  "/services/data/v67.0/platform/data-resilience/data-mask/jobs/{jobRunId}/abort" \
  --method POST --body @./empty-body.json --target-org <alias>
```
空的 JSON 正文（`{}`）通过上述 `@` 前缀文件，如前所述。返回 `200` 会返回 `status: "CANCELED"`（大写，来自运行 API）和 `message: "Job abort requested"`。`409` 表示作业不在 `running` 状态（通常仍然是 `pending`/`scheduled`）——返回 B2 并继续轮询。

### B4. 确认并报告取消
取消是异步的。**重新查询** `DataMaskPolicyJobRun` 并确认 `Status = canceled`（小写，来自 SOQL）之前报告中止成功。验证：
- [ ] 确认中止针对的是活动作业，而其查询状态为 `running`。
- [ ] 中止后重新查询 `DataMaskPolicyJobRun` 并看到 `Status = canceled`。

---

## 高信号规则

| 规则 | 理由 |
|------|-----------|
| 每个执行 `sf` 命令时必须**直接执行**——不要添加任何管道或重定向（`\|`、`\| python3`、`\| grep`、`2>&1`、`2>/dev/null`、`> file`） | `sf ... --json` 已经在标准输出上打印干净的 JSON；直接读取。重定向/管道会触发无法绕过的 shell 安全性保护机制，导致整个运行过程被静默挂起超时。不要使用 `python3`/`grep`/`jq` 进行后处理，也不要抑制标准错误——即使命令打印了警告，`--json` 负载在标准输出上仍然是有效的；直接按原样解析 |
| 不要在 `DataMaskPolicy*` 配置对象上使用标准 SOQL / `sobject describe` | 它们会返回 `INVALID_TYPE` / `NOT_FOUND` — 使用 Tooling API 或 MDAPI |
| 从 `DataMaskPolicyJobRunDtl` 读取掩码计数，不要自行编造 | 子详细信息是每个对象结果的来源 |
| 只有 `completed` / `completed_with_errors` / `failed` 是最终状态 | 报告 `running`/`scheduled` 作为最终状态是错误的 |
| 仅通过运行-API 的中止端点中止 | 对作业记录执行 DML/删除不是真正的中止，会破坏状态 |
| 中止后始终重新查询状态并确认 `canceled` | 返回 200 的中止调用不是作业已停止的证明 |
| 数据掩码仅在沙盒上运行 | 运行/中止端点在生产环境中返回 403 |
| 使用 API 版本 `v67.0` 或更高版本，且不包含 `/connect/` 段 | 运行/中止端点是 `/services/data/v67.0/platform/data-resilience/data-mask/...` — 包含 `connect` 段或预 v67 版本会返回 `NOT_FOUND` |
| 通过 `scripts/poll-job.sh`（一次调用）轮询，不要手动编写 SOQL 循环 | 脚本会限制尝试次数并在真实详细信息行上短路；手动针对滞后父状态进行循环是运行超时且无报告的首要原因 |

---

## 注意事项

| 问题 | 解决方案 |
|-------|------------|
| `sf sobject describe DataMaskPolicy` → `NOT_FOUND` | 它是 Tooling/MDAPI 实体——使用 `--use-tooling-api` 查询，不要重试标准 API |
| `SELECT ... FROM DataMaskPolicy` → `INVALID_TYPE` | 相同原因——使用 Tooling API 查询策略；标准 API 仅用于 `DataMaskPolicyJobRun`/`Dtl` |
| 运行开始返回 `409` | 该策略已有一个正在进行的运行——轮询现有运行或等待其完成 |
| 中止返回 `409` "status=PENDING" | 作业仍然是 `pending`/`scheduled`，尚未 `running` — 继续轮询并在读取 `running` 后中止；不要放弃中止 |
| 小作业在你能够中止它之前完成 | 在小沙盒上，`running` 窗口只有几秒钟——启动新的运行并紧密轮询；不要用之前中止的作业来伪造流程 |
| 中止返回 `200` 但 SOQL 状态仍然是 `running` | 取消是异步的——继续轮询 SOQL 状态直到 `canceled`；不要过早报告成功 |
| 运行 API 说 `CANCELED` 但 SOQL 说 `running` | 案例和表面不同：运行 API 是大写，SOQL 挑单是小写。信任 SOQL 值以确定最终状态 |
| 作业“立即完成” | 重新检查：`scheduled` 不是最终状态。轮询直到实际出现最终值 |
| 运行/中止端点 `NOT_FOUND` | 路径必须是 `/services/data/v67.0/platform/data-resilience/data-mask/...` — 没有 `/connect/` 段，且版本 `v67.0`+（核心 262）。参见 `references/api-surface.md` |

---

## 输出格式

报告你运行的**工作流**的章节——不要为其他工作流添加章节。**保持紧凑——在每个步骤中显示每个命令一次；不要附加一个重复已显示调用的“完整命令日志”**。优先使用紧凑表格而不是散文；读者应在第一屏显示中找到关键结果。

**工作流 A（掩码和报告）：**
1. **使用的策略**（Id + 标签，以及是否重复使用或创建）
2. **运行** — 作业 Id、最终最终状态、掩码记录计数（来自详细信息对象）。将轮询循环压缩为一行（例如 "轮询 5 次，`running`→`completed`"）；不要为每次轮询打印一行。
3. **每个对象的结果** — 来自 `DataMaskPolicyJobRunDtl`。报告行实际携带的对象级计数；如果没有字段级错误行，则说明“未报告字段级错误”，而不是声称每个字段成功。参见 A5 以获取确切的措辞。
4. **运行的命令** — 已在上文中内联显示；此处只需列出尚未显示的命令。**不要**再次粘贴完整序列。

**工作流 B（取消运行）：**
1. **作业已取消** — 作业 Id、中止时它是 `running`、中止是通过运行-API 的中止端点发出的、重新查询的 `canceled` 状态。
2. **运行的命令** — 如上所述，不要再次粘贴。

**保持事实性的准确性注意事项：**
- 运行/中止 REST 响应返回一个**15 个字符**的 `jobRunId`（例如 `1aGXK0000000uob`）；SOQL 返回相同记录的**18 个字符**形式（例如 `1aGXK0000000uob2AA`）。它们是**同一个作业**——当两者都出现时，注意这一点，而不是将它们呈现为两个 ID。
- 不要断言你没有实际查询的掩码计数、每个字段的结果或最终状态。报告中每个数字都必须追溯到命令日志中显示的查询结果。

---

## 跨技能集成

| 需要 | 委托给 | 原因 |
|------|-------------|--------|
| 种植逼真的 PII 记录以进行掩码 | [platform-data-manage](../platform-data-manage/SKILL.md) | 测试数据创建 |
| 编写自定义匿名化 Apex | [platform-apex-generate](../platform-apex-generate/SKILL.md) | Apex 编写 |
| 将策略元数据部署到组织 | [platform-metadata-deploy](../platform-metadata-deploy/SKILL.md) | 元数据部署 |

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `references/api-surface.md` | 精确的每个实体 API 表面、所有 CLI 命令、运行/中止 REST 端点以及状态挑单值 |
| `references/policy-authoring.md` | 两步编写配方（MDAPI 薄壳 → Tooling 对象/字段插入）以及 `MaskingCategory`/`MaskValue` 处理表 |
| `references/run-and-abort.md` | 完整的运行 → 轮询 → 报告 → 重新运行 → 中止序列，以及示例响应 |
| `scripts/poll-job.sh` | 有界轮询器：等待最终状态（默认）或，使用 `POLL_MODE=running`，等待可中止的 `running` 窗口 |
