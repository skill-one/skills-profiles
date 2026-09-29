---
name: cargo-gtm
description: 在 Cargo 上进行 B2B 市场推广工作——研究客户和采购委员会，从授权数据提供商处丰富和验证 B2B 联系记录，对潜在客户进行评分和资格认证，为用户自己的序列器起草基于许可的推广内容，与 CRM 同步，并监控采购信号。基于同意原则、屏蔽列表和数量限制来管理所有涉及个人的步骤（`references/acceptable-use.md`）；批量非请自来的信息、购买的或爬取的列表以及消费者定向将被拒绝。触发条件： "为我创建一个列表"、"在 <segment> 中找到 50 个 <title>"、"谁在那里工作"、"为这些账户找到工作邮箱"、"丰富这个 CSV"、"验证这些邮箱"、"创建一个 TAM"、"谁符合我们的 ICP"、"谁实际从我们购买"、"我们应该在账户上收集哪些数据点"、"我们的外联正在接触错误的人"、"对这批潜在客户进行评分"、"写一封首次接触邮件"、"将这些推送到我的 CRM"、"谁换了工作"、"谁刚刚融资"、"使用 <tech> 的公司"、"谁在招聘 <角色>"、"找到采购委员会"、"<investor> 的投资组合公司"、"将这个受众上传到 Google/Meta/LinkedIn 广告"。提供商：aiArk、anthropic、apolloio、bouncer、brightData、builtwith、cleon1、companyEnrich、contactOut、datagma、dropcontact、enrichCrm、enrichley、enrowio、exa、findyMail、firecrawl、forager、FullEnrich、g2、gemini、hunter、icypeas、kitt、leadMagic、linkedin、linkup、mixrank、neverBounce、oceanio、openAi、parallel、peopleDataLabs、perplexity、piloterr、prospeo、proxycurl、reverseContact、rocketreach、salesNavigator、serper、sillage、snitcher、societeInfo、theirStack、theSwarm、waterfall、x、zeroBounce。在付费呼叫之前，先阅读阶段指南、配方和每个提供商的剧本。当运行已经发生且行为不当时跳过——使用 cargo-diagnostics。
---

# Cargo GTM — Meta技能

使用此技能进行潜在客户开发、账户研究、联系人丰富、验证、线索评分、个性化、信号监控和活动激活。

## 可接受的使用 — 强制性，在任何接触个人的操作之前

完整规范：[`references/acceptable-use.md`](references/acceptable-use.md)。简短版本，适用于此处的每个配方：

- **仅限B2B专业身份**，来自[`provider-playbooks/`](provider-playbooks/)中的授权提供者——绝不进行消费者定位、购买列表或从违反其条款的平台获取数据。
- **在每一步接触之前进行三次检查**——*基础*（客户、已选择联系的联系人、活动参与者或已记录的合法利益案件）、*屏蔽*（在丰富或发送之前根据退订/DNC/硬反弹进行过滤）、*相关性*（姓名、按接收人、为什么此消息是发给他们的）。任何失败的检查都是停止并询问，而不是警告。
- **拒绝并说明原因**：无差别的扩散（“向`<行业>`中的所有人发送电子邮件”）、联系被屏蔽的记录、过滤规避或伪装的发送者身份、自动拨号和短信轰炸、批量轰炸LinkedIn互动操作。提供合规版本一次——说明它，不要说教。
- **此技能从不发送。** 接触配方在发送就绪变量处停止，并交由用户自己的序列器，在该序列器的限制、域和身份下。复制草稿必须包含诚实的发送者和主题、可工作的退订方式以及在该司法管辖区需要邮政地址。

## 初始化

已经登录（`cargo-ai whoami`返回工作区）？跳到下一节。

```bash
npm install -g @cargo-ai/cli            # 没有全局安装？为每个命令前缀`npx @cargo-ai/cli`
cargo-ai login --email you@company.com  # 发送代码，无需浏览器；在首次使用时创建账户
                                        # 替代方案：--oauth（浏览器）· --token <api-token>（CI）
cargo-ai whoami                         # 在任何写入之前确认活动工作区
```

每个命令将JSON打印到stdout；失败时以非零退出并带有`{"errorMessage": "..."}`。创建运行或批次的任何内容都是异步的——传递`--wait-until-finished`或轮询匹配的`get`。当完整技能包安装时，[`../cargo/references/prerequisites.md`](../cargo/references/prerequisites.md)添加了CLI版本固定、令牌范围和仅管理员界面。

## 1) 此技能管辖的内容

- 在执行之前路由GTM决策、安全门和提供者/质量默认值。
- 将长命令链和工具细节保留在子文档中；提供者特定实现细节在`provider-playbooks/*.md`中。
- 将配方锚定在**基于积分的操作**（高价值操作调用）。免费的CRUD（createLead、getLead、deleteRecords）不需要此技能——代理可以临时组合这些。

### 流程 / 目标

用户通常试图从“我有ICP”到“这里是一份经过验证的电子邮件和个性化信号的潜在客户列表”。他们可能处于此过程的任何阶段——引导他们沿此方向进行。

**发现顺序：公司优先，然后是人员。** 当任务需要找到符合标准（投资组合、ICP、招聘信号）的公司中的联系人时，首先发现公司集，然后在每个公司中找到人员。不要从广泛的搜索查询开始。

### 文档层次结构

- **级别1** — `SKILL.md`（此文件）：决策模型、护栏、路由表、链接到子文档。
- **级别2** — 阶段文档：[`guides/finding-companies-and-contacts.md`](guides/finding-companies-and-contacts.md)、[`guides/enriching-and-researching.md`](guides/enriching-and-researching.md)、[`guides/writing-outreach.md`](guides/writing-outreach.md)。
- **级别2.5** — 配方：[`recipes/*.md`](recipes/)——针对特定场景的逐步操作手册。
- **级别3** — 提供者操作手册：[`provider-playbooks/<slug>.md`](provider-playbooks/)——提供者特定怪癖、成本和回退行为。

## 2) 读取行为 — 执行任何操作之前必须阅读

**停止。在打开正确的任务子文档之前，不要调用任何提供者、运行任何`cargo-ai orchestration action execute`命令或编写任何搜索查询。**

这些文档编码了什么有效、什么失败以及为什么。它们包含经过验证的参数模式、最便宜提供者映射、并行执行模式、样本有效负载和已知陷阱。阅读正确的文档10秒钟可以节省10次失败的调用、浪费的积分和垃圾输出。

### 路由规则 — 将您的任务与文档匹配并阅读它

| 任务涉及…时 | 您必须首先阅读此文档 | 它为您提供什么 |
|---|---|---|
| **寻找公司、寻找人员、建立线索列表、潜在客户开发、投资组合/VC采购、在已知公司中寻找联系人** | [`guides/finding-companies-and-contacts.md`](guides/finding-companies-and-contacts.md) | 提供者过滤模式、最便宜来源决策树、并行模式、基于角色的搜索规则、投资组合/VC捷径、联系人查找模式。 |
| **丰富公司或联系人、查找电子邮件/电话/LinkedIn、级联丰富、信号查找（工作变更、融资、技术栈）、数据合并** | [`guides/enriching-and-researching.md`](guides/enriching-and-researching.md) | 级联模式与回退链、何时使用aiArk vs 级联 vs FullEnrich vs peopleDataLabs、电子邮件/电话/LinkedIn回退顺序、信号段、通过`run download-outputs`检索输出。 |
| **编写首次接触的接触、个性化消息、线索评分、资格、序列设计、活动文案** | [`guides/writing-outreach.md`](guides/writing-outreach.md) + [`references/acceptable-use.md`](references/acceptable-use.md) (§3检查、阻止) | LLM提供者路由（openAi/anthropic/perplexity/gemini）、提示模板、评分标准、电子邮件长度/语气规则、个性化模式——基于基础、屏蔽和按接收人相关性进行限制。 |
| **实际上从Cargo拥有的邮箱发送草稿副本**（而不是交给用户自己的序列器） | [`../cargo-mailbox-management/SKILL.md`](../cargo-mailbox-management/SKILL.md) + [`references/acceptable-use.md`](references/acceptable-use.md) (§3检查、阻止) | 配置和预热、每天5→40的发送斜坡限制数量、`sendEmail`操作（0.1积分/发送）、工作区屏蔽列表、回复/打开/点击作为事件。 |
| **构建或修改定期工作流**（cron / webhook / 定时工具 / 操作）、设计步骤序列、触发器、部署/验证周期 | [`../cargo-orchestration/SKILL.md`](../cargo-orchestration/SKILL.md) (功能) + 应用模式从此技能的配方 + 每个付费节点的[提供者操作手册](provider-playbooks/)（§11，尤其是其**定期使用**部分） | 工具/操作工作流模式、节点图语法、轮询策略、输出检索；按提供者节奏默认值和重新计费门。 |

### 配方：逐步操作手册（执行前检查）

扫描此列表并阅读与您的任务匹配的配方。**当配方匹配时：按执行计划逐步遵循它。**

| 配方 | 使用时… |
|---|---|
| [`recipes/source-planning.md`](recipes/source-planning.md) | **在来源不明显时首先阅读。** 将问题转换为字段，在5-10行上探测2-3个候选来源，呈现每个*命中*的成本——在任何扩散之前 |
| [`recipes/prospecting.md`](recipes/prospecting.md) | 端到端查找→丰富→验证→同步（P1/P2/P3变体） |
| [`recipes/build-tam.md`](recipes/build-tam.md) | 大规模构建可扩展的总地址市场列表（100-10,000家公司） |
| [`recipes/linkedin-url-lookup.md`](recipes/linkedin-url-lookup.md) | 从姓名+公司解析LinkedIn个人资料URL，严格验证身份 |
| [`recipes/portfolio-prospecting.md`](recipes/portfolio-prospecting.md) | 投资者/加速器→投资组合公司→联系人 |
| [`recipes/job-change-monitoring.md`](recipes/job-change-monitoring.md) | `waterfall.detectJobChange`（cargo独有）在联系人段上 |
| [`recipes/funding-watch.md`](recipes/funding-watch.md) | 跟踪最近融资的公司 |
| [`recipes/tech-intent.md`](recipes/tech-intent.md) | 通过技术栈或招聘信号查找公司 |
| [`recipes/icp-discovery.md`](recipes/icp-discovery.md) | 比较已关闭的胜利vs已关闭的损失段以显示ICP信号 |
| [`recipes/custom-datapoints.md`](recipes/custom-datapoints.md) | 设计要为卖方ICP收集*哪些*自定义属性和实时信号——对目录进行可行性限制，然后连接到列、评分、段和刷新节奏 |
| [`recipes/outreach-activation.md`](recipes/outreach-activation.md) | 将信号段转换为就绪的接触（丰富→验证→个性化→序列器交接） |
| [`recipes/ads-audience-activation.md`](recipes/ads-audience-activation.md) | 将段推送到付费媒体——Google Ads Customer Match或LinkedIn Matched Audiences——并读取匹配率 |
| [`recipes/review-and-iterate.md`](recipes/review-and-iterate.md) | 人类必须审查的判断输出——表格交接、分组更正、永久性修复、作为评估集保留 |
| [`recipes/re-engagement.md`](recipes/re-engagement.md) | 仅在新鲜信号触发时唤醒陈旧联系人（工作变更、融资、技术意图） |
| [`recipes/lost-deal-revival.md`](recipes/lost-deal-revival.md) | 通过分支`lost_reason`（冠军离开、预算、时机）恢复已关闭的CRM交易 |
| [`recipes/account-expansion.md`](recipes/account-expansion.md) | 多线程现有客户账户——净新买家、与工作区联系人模型去重 |
| [`recipes/save-as-play.md`](recipes/save-as-play.md) | 将成功的临时运行转换为持久的计划或cron工具——在重复拉动之后提供 |
| [`recipes/import-gtm-data.md`](recipes/import-gtm-data.md) | 将现有GTM数据（任何工具的CSV/CRM导出）导入模型、QA审计它，并选择性地重建定期逻辑作为具有一致性检查的配方 |
| [`recipes/clay-to-cargo.md`](recipes/clay-to-cargo.md) | **Clay特定**：获取列*配置*（不是CSV）、列族→操作映射、Clay的四个概念不一一对应（级联、运行条件、自动更新、部分运行），以及与Clay自身输出的对比检查 |

如果没有匹配，扫描上述阶段文档以查找最接近的模式并调整——或者调用[`agents/execution-plan-creator.md`](agents/execution-plan-creator.md)以使用提供者/操作缩写和成本估计组合自定义链。对于广泛的采购扫描（按行业、按地理区域），将批准的切片委托给[`agents/list-builder.md`](agents/list-builder.md)——它执行每个预批准切片的精确一个操作并返回行到文件，将行数据保留在主上下文中。（在带有插件的Claude Code上，两者都作为原生子代理安装：`cargo-execution-planner`和`cargo-list-builder`。）

## 3) 成本纪律 — 强制性门

完整规范：[`references/cost-discipline.md`](references/cost-discipline.md)。每个任务必须遵守的简短版本：

1. **样本→批准→完整运行，按此顺序。** 首先运行输入的确切切片——1-3行以证明一个操作的配置，**在运行任何批次之前10-20条记录**（一行不能显示命中率）。然后显示4部分批准消息（假设·样本结果逐字·积分/范围/上限——始终说明完整运行注册的**记录数**和**成本**，与实际余额进行核对·3形状选择）；保持在AWAIT_APPROVAL状态，直到用户选择。绝不扩散未经批准或成本未知的操作，并且永不将样本的批准视为完整注册的批准。
2. **每次付费操作后接收收据**：花费的积分+剩余余额+命中率（“找到40个电子邮件中的34个”）+估计与实际差异的原因，当它们出现差异时。优先选择`billing usage get-metrics`而不是您自己的算术。
3. **先超额提供1.4×N，然后过滤**——覆盖是公司的一个属性；丢弃不完整的行，而不是用更多提供者追逐它们。
4. **先计数，后付款**——搜索按返回的行计费；保持`limit`严格，并在任何完整拉动之前用1行探测来调整池大小。
5. **电话是受保护的杠杆**——仅限明确用户请求，仅限合格线索。在廉价端仍然适用：`aiArk.findMobilePhone`（0.5，移动-only）是第一个级别，在失败时不计费，但背后的升级是3-7积分（~10×电子邮件），因此完整列表的电话扫描需要与其他付费扩散相同的批准。

## 4) 每次运行后 — 收据，然后基于数据的下一步行动

以收据（上述）结束每个完成的运行，然后建议**最多2-3个下一步行动，从刚刚产生的数据计算——绝不提供通用菜单**。所需形状：

1. **连续性**——基于此会话的工件（“70家公司中有67家有RevOps团队——寻找线索？”），而不是一个新鲜的一般想法。
2. **预算感知**——针对剩余余额（“在您剩余的~9积分中，~5个验证电子邮件适合”）。
3. **单位成本声明**——“电子邮件级联运行~1.4积分。”
4. **默认选择启发式**，以便回答只需一个词（“我默认选择：有融资数据 + RevOps ≥ 2 + 发布是最近的”）。
5. **逃生舱口**——始终以“或者完全是另一回事”结束。

当运行产生持久、可重复的结果时，建议之一应该是**使其系统化**——参见[`recipes/save-as-play.md`](recipes/save-as-play.md)。

当运行或批次**行为不当**——错误、缺少下游值、成本意外——将交由`cargo-diagnostics`技能（`../cargo-diagnostics/SKILL.md`）：在重新运行任何付费操作之前，扫描批次以查找根本原因。计划门、形状选择和实时呈现结果的交互默认值在`../cargo/references/interaction.md`中。

## 5) 优先提供者堆栈（配方以此7个为引导）

这七个基于积分的提供者涵盖了从潜在客户开发→丰富→验证→信号管道的完整流程，在目录中具有最低积分成本。此技能`recipes/`中的每个配方都以此堆栈为引导：

| 提供者 | 角色 | 关键操作（成本以积分计） |
|---|---|---|
| **salesNavigator** | 源头 | `searchLeads` (0.02)、`searchAccounts` (0.05)、`findCompanyInsights/Metrics/EmployeesCount/Distribution` (0.25每个) |
| **aiArk** | 基于LinkedIn的丰富+最便宜搜索 | `enrichCompany` (0.01——目录中最便宜的企情)，`searchCompanies` (0.01/记录，相似种子)、`searchPeople` / `reverseLookup` / `analyzePersonality` (0.05)、`enrichPerson` (0.1——个人资料**+验证电子邮件**)、`findMobilePhone` (0.5) |
| **waterfall** | 多源丰富+信号 | `enrichContact` (2)、`enrichCompany` (1)、`verifyEmail` (0.1)、`detectJobChange` (3)、`searchProspects` (3)、`findPhone` (7) |
| **FullEnrich** | 高级联系人查找 | `findEmail` (1)、`findPhone` (6)、`findPhoneAndEmail` (7)、`reverseEmailLookup` (2) |
| **apolloio** | 专业化覆盖丰富 | `enrichPerson` (1, **3**使用`revealPhoneNumber`)、`enrichOrganization` (1)——**仅有的两个**基于积分的操作；其其他九个需要您自己的Apollo API密钥 |
| **theirStack** | 技术栈+招聘意图 | `searchTechnologies` (0.5)、`searchJobs` (0.5)、`searchCompanies` (0.5) |
| **peopleDataLabs** | 重型回填 | `enrichPerson` (3)、`enrichCompany` (3)、`searchPeople` (3)、`searchCompanies` (3)、`queryPeople/Companies` (3) |

`aiArk`和`apolloio`位于丰富层级的两端，其选择取决于你持有的内容，而非偏好：当手中有**LinkedIn URL**时（个人资料+验证邮箱为0.1，手机为0.5，两者都未命中时计为0），`aiArk`会获胜；`apolloio`是当你推广每个批次时，在试点显示Apollo命中了`aiArk`（0.1）和`waterfall`（2）所遗漏的领域时，**1信用细分覆盖层级**——尤其是投资者支持和投资组合细分领域。它们都不会取代`salesNavigator`用于普通大规模采购（0.02/线索）。

三种信号家族位于堆栈之外，根据任务从[`references/stage-action-map.md`](references/stage-action-map.md)中选择：**公司概况深度**超出`aiArk.enrichCompany` → `companyEnrich.enrichByDomain`（0.25）；**资金/收购** → `enrichCrm.getFunding`（1，目录中唯一的基于信用的资金操作）；**已知域上的技术栈** → 在`builtwith.enrichDomain`（1）之前使用`builtwith.getDomainSummary`（免费）。

有关每个提供商的深入分析，请参阅[`provider-playbooks/`](provider-playbooks/)——包括每个提供商的**重复使用**部分，当任务为监控、执行或计划拉取，而非一次性时。有关完整每个阶段最便宜操作表，请参阅`[references/stage-action-map.md](references/stage-action-map.md)`，涵盖全部136个集成的目录。

> **已持有标识符（非采购）？** 上述堆栈引导*采购优先*的主干。当你已经拥有**LinkedIn URL**时，最便宜的丰富是`[aiArk.enrichPerson](provider-playbooks/aiArk.md)`（0.1——完整个人资料**加上**一个验证邮箱，当未找到邮箱时不计费）；当你不需要邮箱时，降至`[linkedin.enrichProfile` / `enrichCompany`](provider-playbooks/linkedin.md)`（0.25），并完全跳过`waterfall.enrichContact`（它基于邮箱或姓名+公司，而非URL）。需要**电话**？`aiArk.findMobilePhone`（0.5）是第一层级，而非3-7层级。有**LinkedIn活动URL**？`linkedin.extractEventAttendees`直接获取与会者列表。有**邮箱**？`aiArk.reverseLookup`（0.05），然后是`leadMagic` / `contactOut`。有关完整输入类型→最便宜操作映射，请参阅`references/stage-action-map.md`。

## 6) 配方主干（默认链）

```
1. 采购   → salesNavigator.searchLeads / searchAccounts            (0.02–0.05/记录)
              lookalike种子，或SN无法表达的过滤器（技能、教育、任期）？ aiArk.searchCompanies / searchPeople (0.01–0.05/记录)
2. 去重   → 与工作区自己的Companies / Contacts模型匹配
              域 / linkedin_url（存储SQL或分段过滤器）               (免费)
3. 丰富   → 手中有LinkedIn URL？aiArk.enrichPerson (0.1) 首选——一次调用返回个人资料**加上**验证邮箱；如果不需要邮箱，则使用`linkedin.enrichProfile/enrichCompany` (0.25)
              aiArk.enrichCompany (0.01) 用于公司概况；对返回的瘦行使用`companyEnrich.enrichByDomain` (0.25)
              + waterfall.enrichContact / enrichCompany              (1–2/记录)
              + apolloio.enrichPerson / enrichOrganization 在细分残留上 (1/记录)
4. 信号   → enrichCrm.getFunding                                   (1/记录)
              + theirStack.searchJobs / builtwith.getDomainSummary   (0–0.5/记录)
              + waterfall.detectJobChange                            (3/记录)
5. 联系   → FullEnrich.findEmail — 仅在步骤3未留下邮箱的行上（后备peopleDataLabs）                     (1–3/记录)
6. 验证   → waterfall.verifyEmail                                  (0.1/记录)
7. 填充   → peopleDataLabs.enrichPerson (仅当步骤5遗漏时)    (3/记录)
8. QA       → scripts/contact-accuracy-audit.ts                      (免费，本地)
```

来自8个提供商堆栈的两个主干注释：步骤3的`aiArk.enrichPerson`**已返回一个验证邮箱**，因此步骤5仅在残差上运行——不要在已经有一个邮箱的行后支付`FullEnrich.findEmail`（1）。并且当目标达到**电话**时，`aiArk.findMobilePhone`（0.5，仅限手机，未命中时不计费）是`prospeo`（3）/ `FullEnrich`（6）/ `waterfall`（7）之前的第一个层级——§3中的受保护杠杆规则仍然适用于所有四个。

按阶段调整：删除与用户目标不相关的步骤。对于纯采购，仅运行步骤1。对于“丰富我已有的列表”，运行步骤2-7。

## 7) 输出检索——使用`run download-outputs`，而非`run download`

当代理需要操作产生的实际数据（丰富字段、找到的邮箱、搜索结果）时，使用：

```bash
cargo-ai orchestration run download-outputs \
  --workflow-uuid <uuid> \
  --output-node-slug <slug> \
  --format json
```

（不要传递`--is-finished`——CLI帮助仍然列出了它，但API当前使用`unrecognized_keys`拒绝它；已报告。）

返回`{"url": "..."}`——一个指向包含仅输出节点数据的CSV/JSON的签名URL。比`run download`（它拉取完整的运行记录）更快、更便宜。有关`[references/output-retrieval.md](references/output-retrieval.md)`和`[`../cargo-analytics/SKILL.md`](../cargo-analytics/SKILL.md)`。

## 8) 联系准确性——运行QA脚本，不要肉眼

四个确定性TypeScript脚本位于`[scripts/](scripts/)`（Node ≥ 22.18，零依赖，CI中测试的固定装置）取代上下文行检查。**运行脚本——不要通过推理行重新推导其逻辑。** 完整教义、管道顺序和SEND/VERIFY/REVIEW/REMOVE裁决语义：`[references/contact-accuracy.md](references/contact-accuracy.md)`。

- `scripts/validate-emails.ts` — 免费语法/风险/重复删除**在**付费`verifyEmail`之前。
- `scripts/select-current-role.ts` — 从经验数组中选择真实当前角色（捕获换工作者）。
- `scripts/validate-linkedin-names.ts` — 名称↔个人资料匹配（捕获同名诱饵）；与`[recipes/linkedin-url-lookup.md](recipes/linkedin-url-lookup.md)`配对。
- `scripts/contact-accuracy-audit.ts` — 在合并输出上对每行添加`audit_action`戳；在收据中引用其摘要计数。直接读取文件或完成的运行（`--workflow-uuid`，通过`@cargo-ai/api`）。

## 9) 操作形状规则（每个配方）

此技能中的每个操作JSON遵循`[../cargo-orchestration/references/examples/actions.md](../cargo-orchestration/references/examples/actions.md)`中的规则：

- `kind: "connector"`操作形状：`{"kind":"connector","integrationSlug":"<slug>","actionSlug":"<slug>"}`。**`connectorUuid`不在`config`中**——平台自动从`integrationSlug`解析工作区的认证连接器。
- **顶层操作没有`config`——省略它。** 输入在`--data` / `--records`中，并且本配方中的每个操作都写入不带键的操作。这适用于`action execute`、`execute-batch`和`get-output-schema`——操作列表返回的对象粘贴到所有三个中。输入错误地放入`config`中不会被拒绝，它们会被**丢弃**，并且操作会无输入运行，因此当调用因明显原因返回空时，请首先检查这一点。
- **不要手写你不确定的slug，也不要翻阅目录寻找它。** `cargo-ai orchestration action list <keywords> [--integration-slug <slug>]`是免费的，搜索每个集成加原生操作、工具和代理，并返回准备粘贴的操作对象**以及操作的信用成本**——在付费调用之前对slug和价格进行廉价的合理性检查。当问题是*哪些付费操作存在于此*时，`cargo-ai connection action search <keywords> --credits-only`是过滤它的那个。两者都不取代提供商剧本：剧本是输入怪癖、命中率和重复使用陷阱所在的地方。
- 对于多步骤节点图：`connectorUuid`位于节点的顶层，而不是在`config`中。跨节点插值使用`{{nodes.<slug>.<field>}}`。代理节点输出包装在`.answer`下（读取为`{{nodes.<slug>.answer.<field>}}`）。

## 10) 遇到困难时——提交工作区报告

如果配方反复失败且原因不明显，通过`cargo-ai workspaceManagement report create`升级。有关`[../cargo-workspace-management/SKILL.md](../cargo-workspace-management/SKILL.md)`（报告部分）。

## 11) 提供商剧本——调用前阅读（一次性或重复使用）

**停止——在调用以下任何提供商的付费操作之前，并且不要将提供商连接到重复使用的工作流或工具节点图中，直到你已经打开了它的剧本。** 每个剧本都包含确切的操作slug、配置形状、输入怪癖和成本陷阱；阅读它五秒钟比一次失败的付费调用更便宜，并且失败的批次是100次失败的付费调用。当提供商进入**重复使用**工作流时，风险更高，而不是更低：一个错误的配置会在每个计划运行中重复，一个错误的节奏会永远重新计费相同的行——每个剧本都以**重复使用**部分（计划适配、节奏默认、重新计费门、提取器）结束，就是为了这个。**现在每个基于信用的可调用操作提供商都有一个剧本，唯一的例外是`openRouter`，它暴露了一个模型列表器，而不是基于信用的操作，所以没有文档记录。`brightData`和`proxycurl`获得了剧本，而不是保持未列出——隐式地留下可接受使用框架是较弱的选择：`[provider-playbooks/brightData.md](provider-playbooks/brightData.md)` upfront声明了拒绝消费者目标。自有密钥集成回退到`[references/alternatives.md](references/alternatives.md)`和`[references/stage-action-map.md](references/stage-action-map.md)`。

**优先级堆栈（配方以此开头）：**
- [`provider-playbooks/salesNavigator.md`](provider-playbooks/salesNavigator.md) — 目录中最便宜的采购（0.02–0.05/记录）。
- [`provider-playbooks/aiArk.md`](provider-playbooks/aiArk.md) — LinkedIn锚定的人/公司数据：`enrichPerson`返回个人资料**加上**验证邮箱（0.1），`findMobilePhone`（0.5）是最低价的电话层级，`searchCompanies`（0.01/记录）执行lookalikes，`analyzePersonality`（0.05）是目录唯一的。所有操作都在管理连接上运行。
- [`provider-playbooks/waterfall.md`](provider-playbooks/waterfall.md) — 万能瑞士军刀：丰富、验证和货运独特的`detectJobChange`信号。
- [`provider-playbooks/FullEnrich.md`](provider-playbooks/FullEnrich.md) — 高级联系人查找；`reverseEmailLookup`是唯一的。
- [`provider-playbooks/apolloio.md`](provider-playbooks/apolloio.md) — 1信用细分覆盖丰富层级（个人+组织）；**在假设Apollo可用之前阅读它**——它的11个操作中只有两个是基于信用的，其余需要你自己的Apollo API密钥。
- [`provider-playbooks/theirStack.md`](provider-playbooks/theirStack.md) — 技术栈+招聘意图信号。
- [`provider-playbooks/peopleDataLabs.md`](provider-playbooks/peopleDataLabs.md) — 重型回填，固定3信用层级。

**采购和公司数据专家：**
- [`provider-playbooks/linkedin.md`](provider-playbooks/linkedin.md) — 原生LinkedIn集成的操作集（个人资料、公司、帖子、工作）。
- [`provider-playbooks/oceanio.md`](provider-playbooks/oceanio.md) — 从种子域发现lookalike公司，带有技术图形/网络流量过滤器`aiArk.searchCompanies`（0.01）无法表达的。
- [`provider-playbooks/datagma.md`](provider-playbooks/datagma.md) — 轻量级人/公司丰富替代方案。
- [`provider-playbooks/companyEnrich.md`](provider-playbooks/companyEnrich.md) — 最便宜按域公司（0.25）+按项计费lookalikes。
- [`provider-playbooks/enrichCrm.md`](provider-playbooks/enrichCrm.md) — CRM记录丰富；`getFunding`是资金信号回退。
- [`provider-playbooks/societeInfo.md`](provider-playbooks/societeInfo.md) — 法国注册公司/联系人数据（SIREN/SIRET）。
- [`provider-playbooks/snitcher.md`](provider-playbooks/snitcher.md) — 网站访客识别；重复提取器是成本陷阱。
- [`provider-playbooks/piloterr.md`](provider-playbooks/piloterr.md) — 超低价批量公司提取器+G2产品信息。
- [`provider-playbooks/g2.md`](provider-playbooks/g2.md) — 软件评论&类别信号数据。
- [`provider-playbooks/theSwarm.md`](provider-playbooks/theSwarm.md) — 温暖介绍网络映射到目标公司/人员。
- [`provider-playbooks/mixrank.md`](provider-playbooks/mixrank.md) — 高级人/公司回填（4/查找，仅限电话反向查找）。

**邮箱和联系人专家**（所有都为VERIFY步骤提供输入——见`[references/waterfall-strategy.md](references/waterfall-strategy.md)`）：
- [`provider-playbooks/hunter.md`](provider-playbooks/hunter.md) — 域搜索邮箱查找+验证。
- [`provider-playbooks/prospeo.md`](provider-playbooks/prospeo.md) — 邮箱/电话查找，LinkedIn-URL输入路径。
- [`provider-playbooks/icypeas.md`](provider-playbooks/icypeas.md) — 预算邮箱查找/验证。
- [`provider-playbooks/findyMail.md`](provider-playbooks/findyMail.md) — 邮箱查找替代方案。
- [`provider-playbooks/leadMagic.md`](provider-playbooks/leadMagic.md) — 邮箱+手机查找替代方案。
- [`provider-playbooks/contactOut.md`](provider-playbooks/contactOut.md) — 来自LinkedIn个人资料的联系人信息。
- [`provider-playbooks/zeroBounce.md`](provider-playbooks/zeroBounce.md) — `waterfall.verifyEmail`的邮箱验证第二意见。
- [`provider-playbooks/bouncer.md`](provider-playbooks/bouncer.md) / [`neverBounce.md`](provider-playbooks/neverBounce.md) / [`kitt.md`](provider-playbooks/kitt.md) / [`enrichley.md`](provider-playbooks/enrichley.md) — 验证长尾（0.3 / 0.2 / 0.05 / 0.1；enrichley的slug是`verify`，不是`verifyEmail`）。
- [`provider-playbooks/dropcontact.md`](provider-playbooks/dropcontact.md) — 带有法国/欧盟注册深度邮箱查找；`email`输出是一个数组。
- [`provider-playbooks/enrowio.md`](provider-playbooks/enrowio.md) — 邮箱查找（1）+验证（0.1）；仅接受`fullName`。
- [`provider-playbooks/reverseContact.md`](provider-playbooks/reverseContact.md) — 来自LinkedIn的公司（基于信用）；个人资料查找是自有密钥。
- [`provider-playbooks/rocketreach.md`](provider-playbooks/rocketreach.md) — 个人查找（1）；医疗保健/NPI细分；注意`currrentEmployer`模式键。
- [`provider-playbooks/forager.md`](provider-playbooks/forager.md) — 来自LinkedIn URL的个人邮箱+电话。
- [`provider-playbooks/cleon1.md`](provider-playbooks/cleon1.md) — 终端电话查找（15/查找）——仅明确用户请求。

**研究与数据抓取：**
- [`provider-playbooks/firecrawl.md`](provider-playbooks/firecrawl.md) — 用于研究/个性化阶段的网页抓取。
- [`provider-playbooks/serper.md`](provider-playbooks/serper.md) — 用于研究和URL发现的Google SERP查询。
- [`provider-playbooks/linkup.md`](provider-playbooks/linkup.md) — 网页搜索（0.5标准/2深度）+ 来源/结构化答案。
- [`provider-playbooks/parallel.md`](provider-playbooks/parallel.md) — 目录中最便宜的页面读取（`extract`，0.025/URL）加上`createTask`，这是唯一能填充调用者提供的输出模式的操作。
- [`provider-playbooks/exa.md`](provider-playbooks/exa.md) — 带有文档类型`category`过滤器和发布日期界限的语义搜索。
- [`provider-playbooks/builtwith.md`](provider-playbooks/builtwith.md) — 一个域的技术栈；`getDomainSummary`是**免费**的，在付费层级之前运行。
- [`provider-playbooks/x.md`](provider-playbooks/x.md) — 公开的X帖子和个人资料，每操作0.02；一个信号层级，由可接受的使用限制控制。
- [`provider-playbooks/sillage.md`](provider-playbooks/sillage.md) — 从模型中读取的入站信号检测，**免费**，因此在任何信号问题上首先运行。
- [`provider-playbooks/brightData.md`](provider-playbooks/brightData.md) — 通过URL获取Instagram / TikTok / Facebook / YouTube个人资料，每操作0.1；目录中唯一的非LinkedIn、非X社交覆盖，并且该剧本以消费者定位拒绝为入口，控制其运行。
- [`provider-playbooks/proxycurl.md`](provider-playbooks/proxycurl.md) — 使用自己的密钥进行LinkedIn个人资料/公司查询。

**LLM提供者**（全部：一个`instruct`操作，每1,000个token套餐的成本，按模型层级——提示来自[`references/prompt-library/index.md`](references/prompt-library/index.md)）：
- [`provider-playbooks/anthropic.md`](provider-playbooks/anthropic.md) — 判断级默认（Haiku/Sonnet 0.2，Opus 2）；温度嵌套在`advancedSettings`下，需要`maxTokens`。
- [`provider-playbooks/openAi.md`](provider-playbooks/openAi.md) — 最便宜的批量层级（`gpt-5-nano` 0.006）+ 原生JSON-schema输出。
- [`provider-playbooks/gemini.md`](provider-playbooks/gemini.md) — 便宜的高吞吐量（Flash 0.01，每分钟15,000）+ 搜索基础。
- [`provider-playbooks/perplexity.md`](provider-playbooks/perplexity.md) — 基于网络的调研答案；默认模型是昂贵的`sonar-deep-research` — 始终明确设置`model`。

## 12) 参考文献

- [`references/cost-discipline.md`](references/cost-discipline.md) — 强制性支出规则：试点→批准门槛，每次运行的收据，1.4×N超额配置，计数优先尺寸，提供者计费规则。
- [`references/contact-accuracy.md`](references/contact-accuracy.md) — 确定性QA脚本（电子邮件筛选、当前角色、姓名匹配、最终审核）和SEND/VERIFY/REVIEW/REMOVE裁决。
- [`references/prompt-library/index.md`](references/prompt-library/index.md) — 约40个命名、参数化的LLM提示（个性化、评分、研究、资格、信号分析、提取）。**在从头编写任何丰富/评分提示之前，请搜索此索引**——重用胜于重新发明，每个条目都带有经过测试的输出合同。仅加载您需要的分片，永远不要全部加载。
- [`references/stage-action-map.md`](references/stage-action-map.md) — 全136个集成目录中每个阶段最便宜的基于积分的操作。
- [`references/credits-cost-table.md`](references/credits-cost-table.md) — 所有176个基于积分的操作的自动生成成本表。
- [`references/waterfall-strategy.md`](references/waterfall-strategy.md) — 按丰富目标划分的经典瀑布链（每个食谱的“回退”都遵循这些）。
- [`references/alternatives.md`](references/alternatives.md) — 优先级堆栈无法服务时的长尾提供者替换。
- [`references/output-retrieval.md`](references/output-retrieval.md) — `run download-outputs`模式用于获取操作数据。
