# Cargo GTM — Meta技能

使用此技能进行潜在客户开发、账户研究、联系人丰富、验证、线索评分、个性化、信号监控和活动激活。

## 可接受的用途 — 强制性，任何接触个人的操作之前

完整规范：`[references/acceptable-use.md](references/acceptable-use.md)`。简短版本，适用于此处的每个配方：

- **仅限B2B专业身份**，来自`[provider-playbooks/](provider-playbooks/)`中的授权提供者 — 绝不进行消费者定位、购买列表或从违反其条款的平台获取数据。
- **在任何外联步骤之前进行三次检查** — *基础*（客户、已选择联系的联系人、活动参与者或记录在案的合法利益案件）、*抑制*（在丰富或发送之前过滤掉退订/DNC/硬退回）、*相关性*（姓名、按接收人、此消息为何适合他们）。任何失败的检查都是停止并询问，而不是警告。
- **拒绝并说明原因**：无差别的扩散（“向`<行业>`中的所有人发送电子邮件”）、联系被抑制的记录、过滤规避或伪装的发送者身份、自动拨号和短信轰炸、批量轰炸LinkedIn互动操作。提供合规版本一次 — 陈述它，不要说教。
- **此技能从不发送**。外联配方在发送就绪变量处停止，并交由用户自己的序列器，在序列器的限制、域和身份下。复制草稿必须包含诚实的发送者和主题、可工作的退订方式以及司法管辖区要求的邮政地址。

## 引导

如果已经登录（`cargo-ai whoami`返回工作区）？跳到下一节。

```bash
npm install -g @cargo-ai/cli            # 没有全局安装？为每个命令添加`npx @cargo-ai/cli`
cargo-ai login --email you@company.com  # 发送代码，无需浏览器；首次使用时创建账户
                                        # 替代方案：--oauth（浏览器）· --token <api-token>（CI）
cargo-ai whoami                         # 在任何写入之前确认活动工作区
```

每个命令都打印JSON到stdout；失败时以非零退出并带有`{"errorMessage": "..."}`。创建运行或批次的任何内容都是异步的 — 传递`--wait-until-finished`或轮询匹配的`get`。当完整技能包安装时，`[../cargo/references/prerequisites.md](../cargo/references/prerequisites.md)`添加了CLI版本固定、令牌范围和管理员专用界面。

## 1) 此技能管辖范围

- 在执行之前，路由GTM决策、安全门和提供者/质量默认值。
- 将长命令链和工具细节保留在子文档中；提供者特定实现细节在`provider-playbooks/*.md`中。
- 将配方锚定在**基于积分的操作**（高价值操作调用）。免费的CRUD（createLead、getLead、deleteRecords）不需要此技能 — 代理可以临时组合这些。

### 流程 / 目标

用户通常试图从“我有目标客户群”到“这里是一份经过验证的电子邮件和个性化信号的潜在客户列表”。他们可能处于此流程的任何位置 — 引导他们沿此方向进行。

**发现顺序：公司优先，然后是个人。** 当任务需要找到符合标准的公司中的联系人（投资组合、目标客户群、招聘信号）时，首先发现公司集，然后在每个公司中找到联系人。不要从广泛的个人搜索查询开始。

### 文档层次结构

- **级别1** — `SKILL.md`（此文件）：决策模型、护栏、路由表、链接到子文档。
- **级别2** — 阶段文档：`[guides/finding-companies-and-contacts.md](guides/finding-companies-and-contacts.md)`、`[guides/enriching-and-researching.md](guides/enriching-and-researching.md)`、`[guides/writing-outreach.md](guides/writing-outreach.md)`。
- **级别2.5** — 配方：`[recipes/*.md](recipes/)` — 针对特定场景的逐步操作手册。
- **级别3** — 提供者操作手册：`[provider-playbooks/<slug>.md](provider-playbooks/)` — 提供者特定怪癖、成本和回退行为。

## 2) 阅读行为 — 任何执行之前都必须强制执行

**停止。在您为您的任务打开了正确的子文档之前，不要调用任何提供者、运行任何`cargo-ai orchestration action execute`命令或编写任何搜索查询。**

这些文档编码了什么有效、什么失败以及原因。它们包含经过验证的参数模式、最便宜提供者映射、并行执行模式、样本有效负载和已知陷阱。为您的任务阅读正确的文档10秒钟可以节省10次失败的调用、浪费的积分和垃圾输出。

### 路由规则 — 将您的任务与文档匹配并阅读它

| 任务涉及…时 | 您必须首先阅读此文档 | 它给您什么 |
|---|---|---|
| **寻找公司、寻找个人、构建线索列表、潜在客户开发、投资组合/VC采购、在已知公司中寻找联系人** | `[guides/finding-companies-and-contacts.md](guides/finding-companies-and-contacts.md)` | 提供者过滤模式、最便宜来源决策树、并行模式、基于角色的搜索规则、投资组合/VC捷径、联系人查找模式。 |
| **丰富公司或联系人、查找电子邮件/电话/LinkedIn、级联丰富、信号查找（工作变更、资金、技术栈）、数据合并** | `[guides/enriching-and-researching.md](guides/enriching-and-researching.md)` | 级联模式带有回退链，何时使用aiArk vs 级联 vs FullEnrich vs peopleDataLabs，电子邮件/电话/LinkedIn回退顺序，信号段，通过`run download-outputs`检索输出。 |
| **编写首次接触外联、个性化消息、线索评分、资格认证、序列设计、活动文案** | `[guides/writing-outreach.md](guides/writing-outreach.md)` + `[references/acceptable-use.md](references/acceptable-use.md)`（§3检查、阻止） | LLM提供者路由（openAi/anthropic/perplexity/gemini），提示模板，评分标准，电子邮件长度/语气规则，个性化模式 — 受基础、抑制和按接收人相关性限制。 |
| **实际上从Cargo拥有的邮箱发送草稿副本**（而不是交给用户自己的序列器） | `[../cargo-mailbox-management/SKILL.md](../cargo-mailbox-management/SKILL.md)` + `[references/acceptable-use.md](references/acceptable-use.md)`（§3检查、阻止） | 配置和预热，每天5→40的发送斜坡限制数量，`sendEmail`操作（0.1积分/发送），工作区抑制列表，回复/打开/点击作为事件。 |
| **构建或修改定期工作流**（cron / webhook / 定时工具 / play），设计步骤序列、触发器、部署/验证周期 | `[../cargo-orchestration/SKILL.md](../cargo-orchestration/SKILL.md)`（功能）+ 应用模式从此技能的配方 + 每个付费节点的[提供者操作手册](provider-playbooks/)（§11，尤其是其**定期使用**部分） | 工具/工作流模式架构，节点图语法，轮询策略，输出检索；每个提供者的默认频率和重新计费门限。 |

### 配方：逐步操作手册（执行之前检查）

扫描此列表并阅读与您的任务匹配的配方。**当配方匹配时：按步骤作为您的执行计划。**

| 配方 | 使用场景… |
|---|---|
| `[recipes/source-planning.md](recipes/source-planning.md)` | **首先读取当来源不明显时。** 将问题转换为字段，在5-10行上探测2-3个候选来源，呈现每个*命中*的成本 — 在任何扩散之前 |
| `[recipes/prospecting.md](recipes/prospecting.md)` | 端到端查找→丰富→验证→同步（P1/P2/P3变体） |
| `[recipes/build-tam.md](recipes/build-tam.md)` | 大规模构建总地址市场列表（100-10,000家公司） |
| `[recipes/linkedin-url-lookup.md](recipes/linkedin-url-lookup.md)` | 从姓名+公司解析个人LinkedIn个人资料URL，并严格进行身份验证 |
| `[recipes/portfolio-prospecting.md](recipes/portfolio-prospecting.md)` | 投资者 / 加速器→投资组合公司→联系人 |
| `[recipes/job-change-monitoring.md](recipes/job-change-monitoring.md)` | `waterfall.detectJobChange`（cargo-unique）在联系人分段上 |
| `[recipes/funding-watch.md](recipes/funding-watch.md)` | 跟踪最近获得资金的公司 |
| `[recipes/tech-intent.md](recipes/tech-intent.md)` | 通过技术栈或招聘意图信号查找公司 |
| `[recipes/icp-discovery.md](recipes/icp-discovery.md)` | 差异化Closed-Won vs Closed-Lost分段以显示ICP信号 |
| `[recipes/custom-datapoints.md](recipes/custom-datapoints.md)` | 设计要收集哪些自定义属性和实时信号以供卖家ICP使用 — 对目录进行可行性限制，然后将其连接到列、评分、分段和刷新频率 |
| `[recipes/outreach-activation.md](recipes/outreach-activation.md)` | 将信号分段转换为就绪的外联（丰富→验证→个性化→序列器交接） |
| `[recipes/ads-audience-activation.md](recipes/ads-audience-activation.md)` | 将分段推送到付费媒体 — Google Ads Customer Match或LinkedIn Matched Audiences — 并读取匹配率 |
| `[recipes/review-and-iterate.md](recipes/review-and-iterate.md)` | 人类必须审查的判断输出 — 表格交接、分组更正、永久修复、保留为评估集 |
| `[recipes/re-engagement.md](recipes/re-engagement.md)` | 仅在新鲜信号触发时唤醒陈旧联系人（工作变更、资金、技术意图） |
| `[recipes/lost-deal-revival.md](recipes/lost-deal-revival.md)` | 通过分支`lost_reason`（冠军离职、预算、时机）恢复Closed-Lost CRM交易 |
| `[recipes/account-expansion.md](recipes/account-expansion.md)` | 多线程现有客户账户 — 新买家，与工作区的联系人模型去重 |
| `[recipes/save-as-play.md](recipes/save-as-play.md)` | 将成功的临时运行转换为持久的定期play或cron工具 — 在任何可重复拉动之后提供 |
| `[recipes/import-gtm-data.md](recipes/import-gtm-data.md)` | 将现有GTM数据（任何工具的CSV/CRM导出）导入模型、QA审计，并选择性地重建定期逻辑为play，并进行一致性检查 |
| `[recipes/clay-to-cargo.md](recipes/clay-to-cargo.md)` | **Clay特定**：获取列*配置*（不是CSV），列族→操作映射，Clay的四个概念不一一对应（waterfalls、运行条件、自动更新、部分运行），以及与Clay自身输出的并行检查 |

如果都不匹配，请扫描上述阶段文档以查找最接近的模式并进行调整 — 或者调用`[agents/execution-plan-creator.md](agents/execution-plan-creator.md)`以使用提供者/操作符缩写和成本估计组合自定义链。对于广泛来源扫掠（按行业、按地理区域），将批准的切片委托给`[agents/list-builder.md](agents/list-builder.md)` — 它对每个切片执行恰好一个预批准的操作并返回行到文件，从而将行数据保留在主上下文之外。（在Claude Code插件中，两者都作为原生子代理安装：`cargo-execution-planner`和`cargo-list-builder`。）

## 3) 成本纪律 — 强制性门限

完整规范：`[references/cost-discipline.md](references/cost-discipline.md)`。简短版本，每个任务都必须遵守：

1. **样本→批准→完整运行，按此顺序。** 首先运行输入的确切切片 — 1-3行以证明一个操作的配置，**在运行任何批量之前10-20条记录**（一行无法显示命中率）。然后显示4部分批准消息（假设·样本结果逐字·积分/范围/上限 — 始终说明完整运行注册的**记录数**以及**成本**，与实际余额进行对账·3个形状选择）；停留在AWAIT_APPROVAL，直到用户选择。永远不要在外联未经批准或成本未知的操作上扩散，并且永远不要将样本的批准视为完整注册的批准。
2. **每次付费操作后都有收据**：花费的积分+剩余余额+命中率（“找到40封电子邮件中的34封”）+估计与实际值的差异以及它们差异的原因。更喜欢`billing usage get-metrics`而不是您自己的算术。
3. **过度配置1.4×N，然后过滤** — 覆盖率是公司的一个属性；删除不完整的行，而不是用更多提供者追逐它们。
4. **先计数，后付款** — 搜索按返回的行计费；保持`limit`严格，并在任何完整拉动之前用1行探测来调整池大小。
5. **电话是受保护的杠杆** — 仅在明确用户请求时，仅限合格线索。在廉价端仍然适用：`aiArk.findMobilePhone`（0.5，仅限移动）在未找到时计费为0，但背后的升级需要3-7积分（约10倍电子邮件），因此任何完整列表的电话扫掠都需要与任何其他付费扩散相同的批准。

## 4) 每次运行后 — 收据，然后是具体的下一步

每个完成的运行都以收据（上述）结束，然后提出**最多2-3个下一步，这些步骤由刚刚产生的数据计算得出 — 永远不是通用菜单**。所需形状：

1. **连续性** — 基于此会话的工件（“70家公司中有67家拥有RevOps团队 — 找线索？”），而不是一个新鲜通用的想法。
2. **预算感知** — 针对剩余余额（“用你剩下的~9积分，~5封验证电子邮件适合”）。
3. **单位成本声明** — “电子邮件级联运行~1.4积分。”
4. **默认选择启发式算法**，以便回答只需一个词（“我默认选择：有资金数据 + RevOps ≥ 2 + 发布是最近的”）。
5. **逃生舱** — 始终以“或者完全是其他东西”结束。

当运行产生持久、可重复的结果时，建议之一应该是**使其系统化** — 见`[recipes/save-as-play.md](recipes/save-as-play.md)`。

当运行或批量**行为异常** — 错误、缺少下游值、成本意外 — 将其交给`cargo-diagnostics`技能（`../cargo-diagnostics/SKILL.md`）：在重新运行任何付费操作之前，扫描批次以查找根本原因。计划门限的交互默认值、形状选择以及实时呈现结果的`../cargo-references/interaction.md`。

## 5) 优先提供者堆栈（配方以此堆栈开头）

这七个基于积分的提供者涵盖了从潜在客户开发→丰富→验证→信号管道的完整流程，并且在目录中具有最低积分成本。此技能的`recipes/`中的每个配方都以此堆栈开头：

| 提供者 | 角色 | 关键操作（成本以积分计） |
|---|---|---|
| **salesNavigator** | 源头 | `searchLeads`（0.02）、`searchAccounts`（0.05）、`findCompanyInsights/Metrics/EmployeesCount/Distribution`（每个0.25）
| **aiArk** | 基于LinkedIn的丰富+最便宜搜索 | `enrichCompany`（0.01 — 目录中最便宜的企划信息）、`searchCompanies`（0.01/记录，相似种子）、`searchPeople` / `reverseLookup` / `analyzePersonality`（0.05）、`enrichPerson`（0.1 — 个人资料**+验证电子邮件**）、`findMobilePhone`（0.5）
| **waterfall** | 多源丰富+信号 | `enrichContact`（2）、`enrichCompany`（1）、`verifyEmail`（0.1）、`detectJobChange`（3）、`searchProspects`（3）、`findPhone`（7）
| **FullEnrich** | 高级联系人查找 | `findEmail`（1）、`findPhone`（6）、`findPhoneAndEmail`（7）、`reverseEmailLookup`（2）
| **apolloio** | 专用覆盖丰富 | `enrichPerson`（1, **3**使用`revealPhoneNumber`）、`enrichOrganization`（1） — 唯一的**两个**基于积分的操作；其余九个需要您自己的Apollo API密钥
| **theirStack** | 技术栈+招聘意图 | `searchTechnologies`（0.5）、`searchJobs`（0.5）、`searchCompanies`（0.5）
| **peopleDataLabs** | 重型回填 | `enrichPerson`（3）、`enrichCompany`（3）、`searchPeople`（3）、`searchCompanies`（3）、`queryPeople/Companies`（3）
|

`aiArk`和`apolloio`位于丰富层级的两端，并且是**根据您持有的内容**选择，而不是偏好：`aiArk`在手中**LinkedIn URL**时获胜（个人资料**+验证电子邮件**在0.1，移动在0.5，在未找到时计费为0），`apolloio`是**1-积分的专用覆盖运行**，在批次中推广每个批次时，当试点显示Apollo命中而`aiArk`（0.1）和`waterfall`（2）错过时 — 投资者支持和投资组合领域尤其。它们不会取代`salesNavigator`用于大规模源头（0.02/线索）。

三个信号系列位于堆栈之外，并且根据任务从`[references/stage-action-map.md](references/stage-action-map.md)`中选择：**超出`aiArk.enrichCompany`的企划深度** → `companyEnrich.enrichByDomain`（0.25）；**资金/收购** → `enrichCrm.getFunding`（1，目录中唯一的基于积分的资金操作）；**已知域上的技术栈** → `builtwith.getDomainSummary`（免费）在使用付费运行之前`builtwith.enrichDomain`（1）。

参见`[provider-playbooks/](provider-playbooks/)`以获取每个提供者的深入探讨 — 包括每个提供者的**定期使用**部分，当任务是一个监控、play或计划拉动而不是一次性操作时：**每个基于积分的可调用操作现在都有一个操作手册，有一个例外**：`openRouter`，它公开模型列表器而不是基于积分的操作，因此没有任何文档。`brightData`和`proxycurl`获得了操作手册而不是保留未列出 — 未记录的提供者仍然出现在成本表中，并且隐含可接受的用途框架是较弱的选择：`[provider-playbooks/brightData.md](provider-playbooks/brightData.md)`在前面声明了拒绝消费者定位。拥有密钥的集成回退到`[references/alternatives.md](references/alternatives.md)`和`[references/stage-action-map.md](references/stage-action-map.md)`.
