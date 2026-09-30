---
name: month-end-prep
description: 与会计总账（MYOB、NetSuite、QuickBooks、Xero 或 Zoho Books）进行核对，对照 PayPal、Shopify、Square 和 Stripe 的结算记录，标记需要关注的事项、可疑重复交易以及缺失的收据，然后生成简体中文的损益表叙述，并导出关闭包（xlsx + 一页 PDF）。这是 /close-month 命令的第一步；请求关闭月份或账簿时会跳转至此，命令在刷新预测并分发包之前会先运行此技能。仅在所有者仅需要核对功能时直接使用此技能，无需刷新预测和分发包：例如“仅核对，不生成包”、“账簿缺失内容是什么”、“标记重复交易和缺失收据”或“为本月撰写损益表叙述”。
---

# 月末准备工作

## 快速入门

连接您的账簿和至少一个支付处理器，然后说“让我们结账这个月。”Claude 将引导您完成清单的每一步，在每个关卡暂停以获取您的输入，然后才能继续前进。

任何连接的账簿都可以进行结账。每个账簿都有一个参考文件用于读取，以及它的“需要关注”信号：[reference/quickbooks-reconcile.md](reference/quickbooks-reconcile.md)、[reference/xero-reconcile.md](reference/xero-reconcile.md)、[reference/zoho-books-reconcile.md](reference/zoho-books-reconcile.md)；NetSuite 和 MYOB 在 [reference/v2_sources.md](reference/v2_sources.md) 中。账簿是平等的 (`../../shared/connector-neutrality.md`)：如果两个账簿都连接了，请询问哪个持有要结账的账簿，只读取另一个独特持有的内容，并且永远不要在两个账簿之间汇总数字。

每个金额都是业务的本币 (`../../shared/currency-and-locale.md`)。下面的阈值（0.50、0.01、25）也是以该货币表示的。

如果缺少连接器，Claude 会回退到要求 CSV 导出——它不会在无声中跳过步骤。

## 工作流程

按顺序完成这些步骤。每个步骤都有一个完成状态；在当前步骤确定之前，不要继续前进。

### 第 1 步——确定目标月份

询问用户要结账的月份。如果他们没有指定，则默认为上一个月历月。在拉取任何数据之前进行确认。

### 第 2 步——拉取账簿的损益表和登记簿

获取：
- 目标月份的损益表（收入、销售成本、毛利、营业费用、净收入）
- 登记簿，如账簿的参考文件定义的那样。QuickBooks：交易列表，每条收入和费用行。Xero：账单、发票和银行交易队列，范围在数据包中说明。Zoho Books：发票、费用和采购订单，损益表来自导出，因为连接器没有报告端点。

立即使用账簿自己的“需要关注”信号进行标记：
- **QuickBooks** — 未分类的行（“未分类”、“空白”、“问我的会计师”）及其需要审查标志
- **Xero** — 月末仍未核对的银行行
- **Zoho Books** — 每个银行账户上的 `uncategorized_transactions` 计数

向用户显示计数（“14 笔交易需要关注”），并列出它们以供用户在账簿中解决，然后才能继续。除非用户明确说“暂时跳过”，否则不要在打开的项目上继续前进。

参见 [reference/quickbooks-reconcile.md](reference/quickbooks-reconcile.md)、[reference/xero-reconcile.md](reference/xero-reconcile.md) 和 [reference/zoho-books-reconcile.md](reference/zoho-books-reconcile.md) 以获取字段映射和 API 说明。

### 第 3 步——拉取支付处理器的结算

获取与连接的 PayPal、Square、Stripe 或 Shopify 的结算报告——对于同一个日历月。

**首先检查银行流水。** 当处理器通过银行流水付款时，付款已经是账簿行，问题是它是否已经匹配。找到命名处理器的未核银行行，并按处理器列出它们作为操作项，然后再进行任何 CSV 匹配。这适用于任何带有已核状态银行流水的账簿——Xero 中的常见情况，以及连接器暴露的 QuickBooks 银行流水行。MYOB 没有银行方面，Zoho Books 暴露余额但没有银行交易列表，因此 MYOB 或 Zoho Books 的结账直接进入下面的 CSV 匹配。

**净对净比较，否则每行都看起来是错误的。** 账簿记录净银行存款；处理器的报告显示毛销售额。直接匹配它们，并且每一行都显示与费用相同大小的差异。使用处理器的 **净付款**（毛额减去费用）——参见 [reference/gotchas.md](reference/gotchas.md)。

将每个结算存款与账簿的银行存款行进行匹配：
- **匹配** — 金额和日期在 2 天内一致 → 标记为已核对
- **差异 < 0.50** — 四舍五入/费用；记录但不要标记
- **差异 ≥ 0.50** — 带有差额金额标记
- **结算存在，账簿存款不存在** — 标记为“账簿中缺失”
- **账簿存款存在，结算不存在** — 标记为“处理器数据中不存在存款”

参见 [reference/paypal-settlements.md](reference/paypal-settlements.md) 以获取结算报告字段映射（PayPal、Square、Stripe）和
[reference/v2_sources.md](reference/v2_sources.md) 以获取 Shopify。

### 第 4 步——检测可疑重复项

扫描登记簿以查找可能的重复费用或存款。当 **所有三个** 匹配时，将交易标记为可疑重复：
- 金额相同（在 0.01 内）
- 供应商或客户名称相同
- 在彼此 5 个日历日内发布

扫描账簿实际持有的内容。在 QuickBooks 中，这是交易列表，将拆分行按交易 ID 首先分组。在 Xero 中，重复键入的账单会生成两个未付款文件，没有银行行，因此扫描账单和发票（相同联系人、相同总金额、在 5 天内、都未付款或其中一个在窗口内已付款）而不是银行行——映射在 [reference/xero-reconcile.md](reference/xero-reconcile.md) 中。Zoho Books 是相同的形状：扫描文档作为发票和费用 ([reference/zoho-books-reconcile.md](reference/zoho-books-reconcile.md))。

向用户显示标记的对。他们决定每个是否合法（例如，每周一次的重复订阅）或真实重复项以作废。

**5 天窗口是一个过滤器，不是一个保证。** 它可以捕获两次输入的相同费用，而不会让所有者淹没在每周的重复账单中，但三周前的真实双倍付款会溜走。说明扫描的内容（“5 天内重复”），如果他们对供应商有疑问，则放宽窗口，而不是将其称为干净。

参见 [reference/gotchas.md](reference/gotchas.md) 以获取常见误报模式以及如何区分它们。

### 第 5 步——收据检查

首先检查账簿：交易上的附件计为已存档的收据（QuickBooks 中的 `AttachmentCount`；Xero 中的 `has_attachments`，仅当 `include_line_items=true` 时返回；Zoho Books 发票和费用上的 `has_attachment`）。然后，如果桌面连接器可用，扫描目标月份的收据文件夹（询问用户路径；默认 `~/Documents/Receipts`）。

对于每笔金额超过 25 且没有附加文档的费用交易：
- 检查是否有匹配的收据文件（按金额 ± 0.50 和日期在 3 天内匹配）
- **匹配** → 记录为“已存档收据”
- **不匹配** → 标记为“缺少收据”

列出缺少的收据。用户可以提供文件或标记为“不需要收据”（例如，没有收据的重复自动付款）。

如果桌面连接器不可用，请询问用户他们是否有收据的哪些费用——不要在无声中跳过此步骤。

### 第 5a 步——工资交叉检查

仅在连接了工资连接器（Gusto 或 QuickBooks Payroll——平等，无论哪个连接）时运行。否则跳过它，并在数据包中说明没有工资列。

拉取本月实际支付的金额，仅汇总：

- **Gusto** — `list_payrolls` 使用 `include=totals`，保留 `check_date` 落在目标月份的工资。从每个 `totals`：`gross_pay`、`employer_taxes`、`employee_taxes`、`net_pay`。然后 `list_contractor_payments` 对于相同日期范围使用 `group_by_date=true`，获取 `total.wages` 和 `total.reimbursements`。承包商总额仅涵盖美国承包商——在数据包脚注中说明。
- **QuickBooks Payroll** — `qbo_payroll_get_company_last_payroll_run` 用于最新运行；月份内较早的运行来自工资摘要导出。（在第一次结账前确认。）

与账簿交叉检查：净工资加上雇主税费加上承包商工资应作为月份的工资费用行出现。差异超过 0.50 是核销项——通常是发布到错误月份的运行，或尚未发布的工资分录。

**仅汇总，从不重复个人信息。** 数据包包含月份的汇总和运行计数。没有员工姓名、税率或人均金额离开连接器——那是工资数据，并且 `payroll-prep` 是它所属的地方。参见
[reference/v2_sources.md](reference/v2_sources.md) 以获取字段映射。

### 第 6 步——所有者确认关卡

在继续之前显示摘要：

```
需要关注（未分类或未核对）： X of X 已解决
结算差异：                        X 标记，X 已解决
可疑重复项：                           X 标记，X 已清除
缺少收据：                                X 未解决
工资交叉检查：                             匹配 / X 差异 / 没有工资连接器
```

询问：“准备好编写损益表摘要并导出结账数据包吗？”

**在未明确确认的情况下，不要继续进行步骤 7–8。**

### 第 7 步——编写损益表说明

编写一个简体中文摘要，说明本月——所有者会与配偶或会计师分享，而不是 CFO 的备忘录。目标为 150–250 字。

结构：
1. **标题** — 一句话：“3 月净收入为 12,400 澳元，较 2 月增长 6%。” 货币代码，不要裸露符号。
2. **收入** — 推动数字的因素；如果数据显示集中，请命名产品、服务或客户。
3. **毛利** — 是否保持、上升或压缩，以及主要原因。
4. **主要费用** — 任何月份环比变动超过 10% 或超出正常范围的行；每行一句。
5. **底线** — 净收入与上一个月的比较；询问他们是否有目标进行比较。
6. **关注列表** — 下个月要监控 1–3 件事。

避免术语；定义任何不是简体中文的内容（“MoM” = 月环比）。

参见 [reference/examples/pl-narrative.md](reference/examples/pl-narrative.md) 以获取示例。

### 第 8 步——导出结账数据包

生成两个文件：

**`close-packet-[YYYY-MM].xlsx`** — 三张表，连接了工资连接器时为四张：
- `P&L` — 账簿的损益表数据，格式化
- `核销` — 匹配和标记的交易并排显示
- `待办事项` — 任何未解决的标记（未分类、缺少收据等）
- `工资` — 第 5a 步的汇总与账簿的工资费用并排显示，以及差异

**`close-packet-[YYYY-MM]-summary.pdf`** — 一页：
- 顶部是月份和公司名称
- 关键指标（收入、毛利率%、净收入）
- 第 7 步的损益表说明
- 如果有的话，未解决操作项的计数

将两个文件都保存到桌面（或用户指定的路径）。确认文件位置。

参见 [reference/close-packet-format.md](reference/close-packet-format.md) 以获取列规范和 PDF 布局详情。

还以页面形式交付结账，根据所有者存储的输出偏好——永远不会默认为 Markdown 文件。检查 `## 业务背景` 块的 `Output preference`（共享风格指南规则，`../../shared/artifact-style.md`）：

- **视觉工件（默认）**：以公司风格渲染结账为 HTML 页面——作为聊天摘要和文件的补充，永远不会取代。收入、毛利率百分比和净收入是带有其月环比变化的统计瓦片；核销结果是一个带有 tabular-nums 金额的表格；每个标记都带有状态药丸——用于已核销、警告用于缺少收据和未分类项、关键用于未解决的结算差距和重复项；损益表说明和待办事项清单每个都获得一个面板。
- **docx / md / notion / canva 偏好**：以该形式交付相同内容——DOCX 或 Markdown 文件、通过连接器创建的 Notion 页面（命名目的地，永远不会覆盖）、或通过 Canva 连接器创建的 Canva 文档（每次运行都是新设计，以日期命名；表格变为列表）；如果 Notion 或 Canva 未连接，则回退到视觉工件——并说明原因。数据包 xlsx 和 PDF 保持其格式。
- **最佳技能**：使用视觉工件——在将数据包发送给会计师之前，在屏幕上审查结账。

### 第 9 步——结账后

用一句话说明已结账和仍需打开的内容。然后提供最相关的下一步，以及最多两个其他步骤：

- “现金预测”使用 `cash-flow-snapshot` 基于 freshly 结账的数字运行。
- “为我创建报告”运行 `report-builder` 以发布和分发数据包。
- “税务”在季度或年度末运行 `/tax-prep`——仅在业务背景说明国家是美国时提供，因为该链的税务计算是美联邦。

最多三个提议。永远不会重复本会话中所有者拒绝的提议。

## 批准关卡

- **永远不要在已提交的月份上运行核销。** 在拉取数据之前确认账簿仍然打开。
- **永远不要直接在账簿交易中作废或修改。** 显示标记；所有者会在账簿中做出更改。
- **总是在步骤 6 暂停** 在生成输出之前。未解决的标记必须确认或明确跳过。
- **永远不要在结账包中重复个人信息、SSN 或银行号码** 超过日记汇总 (`../../shared/personal-data.md`)。

## 平滑退化

| 缺少连接器 | 回退 |
|---|---|
| QuickBooks | 要求 **两个单独的导出** — 损益表报告，以及交易按账户详细报告。一个文件不会包含两者；要求“一个 QB 导出”会得到其中一个，并需要第二轮行程 |
| Xero | 要求 **两个导出** — 损益表报告，以及带有所有账户选择的账户交易报告——加上银行核销屏幕上的未核行计数，导出不包含它 |
| NetSuite 或 MYOB | 要求月份的损益表和交易详细作为两个导出；MYOB 没有银行余额，因此银行方面来自报表 |
| Zoho Books | 即使连接了，也要求 **损益表** 导出（没有报告端点）和 **银行对账单**（没有银行交易流）；注册和未分类计数来自连接器。未连接：添加账户交易导出 |
| 支付处理器 | 要求从处理器网站获取结算 CSV。它必须包括费用列，而不仅仅是毛额，否则第 3 步中的净对净匹配无法完成 |
| 支付处理器连接但期间返回零付款 | 视为数据差距，而不是干净的零。说明连接器本月返回了什么，要求相同的结算 CSV（包括费用列），并在报告中命名差距，而不是与空集核销 |
| 工资连接器（Gusto、QuickBooks Payroll） | 跳过步骤 5a。数据包没有工资表，摘要说明“没有工资连接器”；账簿的工资费用行仍然出现在损益表未经检查 |
| 桌面（收据） | 询问用户他们是否有收据的哪些费用 |

## 更多来源

阅读 `reference/v2_sources.md` 以获取映射：

- **Shopify** — 结算对账作为首要环节。订单、付款和费用各自结算，且是常见未解释差额的来源
- **NetSuite** — 记录账簿，常见于高端市场；报表和SuiteQL提供损益表并记录
- **Xero** — 记录账簿，拥有独立的账簿结构（发票、账单、银行队列）和独立的关注信号（未对账银行行项）；映射在`reference/xero-reconcile.md`
- **MYOB** — 损益表和应收应付余额；无银行余额，因此结账的银行方来自报表
- **Zoho Books** — 记录账簿，拥有文档记录（发票、费用、采购订单），银行余额带有未分类计数作为关注信号，且无报表或银行数据端点，因此损益表和付款匹配来自导出；映射在`reference/zoho-books-reconcile.md`
- **Ramp, Expensify** — 卡片和费用明细，填补了实际支出与记录之间的差距
- **Gusto, QuickBooks Payroll** — 实际运行的工资：总工资、雇主税费、净工资和承包商付款按月总计，因此第5a步将账簿的工资费用与实际支付而非计划支付进行对账。仅提供总计；无个人数据进入数据包

相同的结账顺序，相同的数据包。更多来源完成对账。

**QuickBooks汇总字段存在误导。** 在引用QuickBooks汇总对象中的任何总计前，请阅读`../../shared/quickbooks-report-traps.md`：应付账款汇总将供应商信用计入其桶中，并可能显示负逾期金额，而损益表汇总可能将费用报告为零而实际行存在。对行求和，或使用明细调用。

## 参考文件

- [reference/quickbooks-reconcile.md](reference/quickbooks-reconcile.md) — QB字段
  映射、API分页、常见数据问题
- [reference/xero-reconcile.md](reference/xero-reconcile.md) — Xero账簿
  定义、未对账行信号、文档级重复扫描、附件
- [reference/zoho-books-reconcile.md](reference/zoho-books-reconcile.md) — Zoho Books
  账簿定义、未分类计数信号、需要导出的内容
- [reference/paypal-settlements.md](reference/paypal-settlements.md) — 结算
  PayPal、Square和Stripe的报表结构
- [reference/close-packet-format.md](reference/close-packet-format.md) — xlsx列
  规格、PDF布局、文件命名规范
- [reference/gotchas.md](reference/gotchas.md) — 重复误报、拆分交易、月度部分边缘案例
- [reference/examples/pl-narrative.md](reference/examples/pl-narrative.md) — 实际损益表叙述示例

## 使用未列出的工具

本技能中命名的连接器是测试路径，而非障碍。如果所有者希望此流程使用未连接或未列出的工具，提供`build-connector` — 它首先检查连接器目录，否则通过Zapier连接，从不直接针对原始API手动构建。连接建立后，该工具如同任何其他可选连接器一样加入此技能，遵循相同的审批门槛。
