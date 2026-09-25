# Recoup — 构建标签操作系统

**重点不在于文件夹——而是要搭建一个既能自我管理又能自我改进的系统。** 它能保持自身状态最新（永不陈旧），并且随着时间的推移，在自己的工作中变得越来越好：累积知识，将重复性工作转化为新技能，并改进自身的机制。将此作为以下每个阶段的最终目标；结构的存在只是为了服务于这个目标。

具体来说，将启动输入转化为一个活生生的操作系统：一个文件夹+文件结构，一个自我管理的 `CLAUDE.md`（镜像到 `AGENTS.md`），一个 `plugin/` 目录（一个可就地安装的插件，其中包含技能），一个永不陈旧的清洁工，由一个只读的医生支持，一个复合学习循环，以及一个自我改进循环。插件默认命名为 `{DOMAIN_SLUG}-os`，并包含用于 Claude、Cursor 和 Codex 的清单/适配器。

这个构建技能是为运行它的代理。按顺序遵循这些阶段。不要半途而废——驱动到一个可工作的操作系统，然后报告。在达到每个阶段时，阅读参考资料。

## Recoup 专业化——这是一个音乐公司操作系统 [在进入阶段 0 之前阅读]

这个技能是 `workspace-os`（由 Sidney Swift 提供）锁定到一个特定领域——**一个音乐公司/独立厂牌**——并连接到 Recoup。下面的阶段保持不变；将 Recoup 规则叠加在上面进行应用。

- **领域是固定的——不要重新推断。** 核心单元：**艺术家**（以及他们的 **发行物**）。实体文件夹：顶层 `artists/`。发行生命周期（`demo -> A&R -> 签约 -> 制作 -> 发行 -> 推广 -> 目录`）按每个发行物在 `artists/{slug}/releases/` 下跟踪（阶段在 `RELEASE.md` 中）——没有单独的顶层 `pipeline/`；未签约的候选者住在 `prospects/`。将阶段 0 的努力用于理解 *这个特定的厂牌*（阵容、流派、交易立场、内容运动、团队），而不是它的原型是什么。

- **仓库是一个组织/厂牌。** 这在单个组织的 git 仓库内运行，因此艺术家住在顶层 `artists/{artist-slug}/`——没有 `orgs/` 嵌套（仓库本身就是组织）。

- **精确地使用 Recoup 的约定——其他 Recoup 技能依赖于它们：**
  - `artists/{artist-slug}/RECOUP.md` — 身份文件，前文 `artistName` / `artistSlug` / `artistId`（artistId = Recoup 的 `account_id`）。相同的形状 `recoup-roster-list-artists`，`recoup-roster-add-artist` 读写。

  - `releases/{release-slug}/RELEASE.md` 和 `releases/top-tracks.md` 按每个艺术家。

  - `slugify` = 小写连字符；永远不要将 ID 添加到文件夹名称中。

- **秘密始终保持在共享仓库之外。** 始终播种 `.env.example`（记录 `RECOUP_API_KEY` 或 `RECOUP_ACCESS_TOKEN`，`RECOUP_ORG_ID`，可选的 `RECOUP_API_URL`）和一个 `.gitignore` 忽略 `.env`。真实的凭证存在于仓库之外（环境变量 / `~/.claude/recoup.env`）；永远不要提交它们——仓库在厂牌的团队中共享。

- **Recoup API 是系统记录；仓库是大脑。** 从实时账户获取 *真实的* 队伍——永远不要编造一个：
  1. 首先通过链接 **`recoup-platform-connect-account`** 连接机器（铸造/加载凭证：`RECOUP_API_KEY` 或 `RECOUP_ACCESS_TOKEN`，可选的 `RECOUP_ORG_ID`）。
  2. **如果队伍为空（0 位艺术家），则将任务交给 `recoup-roster-onboard`** 以启动它（它将 `recoup-roster-add-artist` 分发到并行子代理）；否则，您自己将现有的队伍实体化到 `artists/` 中：`GET /api/organizations`（或使用 `RECOUP_ORG_ID`）-> `GET /api/artists?org_id=…` -> `mkdir -p artists/{slugify(name)}` 并为每位艺术家编写 `RECOUP.md`（`artistName`/`artistSlug`/`artistId` 来自 `account_id`）；跳过现有的。使用 **`recoup-roster-list-artists`** 进行清单，并使用 **`recoup-platform-api-access`** 进行调用形状。

  3. 写入 `operations/sync.md` 并附带合同：**DB 拥有结构化实体**（队伍、社交、指标、发行物作为记录、账单）；**仓库拥有非结构化大脑**（知识、研究、计划、草稿）。实体创建是 **API 优先**——使用 **`recoup-roster-add-artist`**（8 调用创建->丰富链）加入新艺术家，然后其文件夹出现；永远不要通过 `mkdir` 单独创建艺术家。使用 **`recoup-platform-api-access`** 进行原始 REST / 连接器调用。空的 org+艺术家通常意味着一个可丢弃的密钥，而不是一个空白的厂牌——揭示它，不要编造一个队伍。

- **重用平台；不要重新发明它。** 在阶段 4 中，**不要** 编写 `plugin/skills/` 重复 Recoup 功能——连接到已安装的 `recoup-*` 技能：队伍（`recoup-roster-*`），研究（`recoup-research-*`），内容（`recoup-content-*`），发行（`recoup-release-*`），歌曲（`recoup-song-*`），目录（`recoup-catalog-*`）。操作系统的 `plugin/skills/` 应该是 **厂牌特定的粘合剂**（这个厂牌的例程/编排）加上标准的维护器官（医生/清洁工/学习/反思/技能化/摄入）。将插件名称默认设置为 `{label-slug}-os`。

- **仍然搭建音乐公司需要的所有其他东西。** 除了核心（`artists/`，`knowledge/`，`library/`，`work/`，`artifacts/`，`plugin/`，`operations/`），仅当有真实材料时才添加可选文件夹：`content/`（飞轮），`deals/`（目录收购），`contacts/`（行业网络），`proof/`（媒体/里程碑），`business/`（分成/版税/合同），`prospects/`（A&R 阶梯），`reference/`（厂牌圣经）。将推断的项目标记为“草稿——确认”。有关完整树形结构的详细信息，请参阅 `references/blueprint.md`。

- **填充通用模板（医生/仪表板/清洁工）。** 当您从 `assets/` 生成它们时，实体是 `artists/`，并且没有管道文件夹——将 `{PIPELINE}` 留空，或者如果厂牌进行 A&R，则将其设置为 `prospects/`。医生从每个 `artists/{slug}/releases/`（`RELEASE.md` 中的阶段）读取发行状态，而不是顶层漏斗。

## 运行信念（适用于您构建的每个操作系统）

以下每个信念都服务于一个目标：一个**自我管理**（保持最新）和**自我改进**（累积其知识、其能力和其自身机制）的系统。

1. **将复合物与流动物分开。** 复合物 = 每次改进的可重用资产（模板、知识库、技能、证据）。流动物 = 通过阶段移动的实例（交易、票证、发行物、实验）。将反馈连接起来，以便每个流动实例都存入复合资产。

2. **永不陈旧。** 代理的工作是管理状态。任何时候收到新输入或用户在 OS 中工作，都应该在同一轮中触摸应该更改的每个文件/文件夹。清洁工技能+计划任务是安全网。

3. **复合学习。** 每次会议都使系统更智能——将决策、重复性答案和模式捕获到知识库中。永远不要两次解决同样的问题。

4. **将已证明的重复性工作技能化。** 完成工作后，询问它是否会再次执行或维护。如果是，请在它落入 `plugin/skills/` 之前，将已证明的过程提升为经过验证的阶段技能。一次性工作属于 `work/`，而不是一个可丢弃的技能。对于从已完成工作中创建的技能，请遵循技能化循环：证明来源，提取可重复的过程，在 `work/` 中阶段化，使用最合适的领域检查进行验证，在移动到 `plugin/skills/` 之前询问，然后重新打包。

5. **自我描述。** 每个文件夹都解释其自己的目的；`CLAUDE.md` 编码新事物去哪里以及如何保持系统最新。

6. **证据胜过自信。** "完成"、"一致" 和 "可到达" 由可检查的表面决定——一个 `{domain}-doctor` 运行、一个技能的验证、一个可到达的触发器——而不是代理的感觉。并且 OS 在 *它自身* 上随着时间的推移而改进（`{domain}-reflect`），而不仅仅是其内容。

## 阶段 0 — 深入理解项目（始终是第一步）

阅读 `references/domain-inference.md`。

- 摄入所有启动输入（文件、转录、提示）。如果文件存在，请完全读取它们。

- 确定领域原型和**工作核心单元**（例如，咨询 -> 交易/客户，产品 -> 功能/发行物，唱片厂牌 -> 艺术家/发行物，研究 -> 问题/实验）。

- 如果输入**丰富**，则从材料中推导出结构。如果输入**稀疏**（只是一个提示），请使用最佳判断：推断领域，预测实体、阶段、资产、例程和项目所需的指标，并预测它们，而不是等待——但将这种准备作为在苗条根（见阶段 1）内的桩和子文件夹表示，而不是作为额外的顶层目录。

- 生成一个简短的**理解摘要**：领域、核心单元、生命周期阶段、关键实体、复合资产、重复性任务（技能候选者）、指标和可能的外部工具。

- 仅当有实质性内容不明确时才与用户确认摘要；否则继续。

## 阶段 1 — 设计分类法

阅读 `references/blueprint.md`。

- 从循环维护的小核心开始：流动存储（一个阶段管道文件夹 + 一个实体文件夹，如 `clients/` / `artists/` / `features/`），复合存储 `knowledge/` 和 `library/`，`work/`（非重复性输出，按项目），`artifacts/`（最终化的重复性输出，如仪表板），`plugin/`（就地插件），`operations/`（例程、同步、健康、改进）。

- 只有当领域现在有真实材料时才添加一个**可选**的顶层文件夹——`reference/`（规范/来源），`proof/`（结果），`content/`（真实的.content 运动），`business/`（法律/财务/指标）。不确定时，请省略它；稍后添加是一个 `mkdir`。

- **将每个顶层文件夹名称限制为一个单词**（`operations`，而不是 `operating-system`；`knowledge`，而不是 `knowledge-base`）。使用领域的语言重命名，但保持它为一个单词。（`plugin/skills/` 内部的技能文件夹保持连字符小写——不同的约定。）

- 不要反射性地复制整个解剖结构，并且**不要将一次性工作提升为顶层文件夹**——临时任务住在 `work/`；只有重复性或需要维护的工作才会成为 `plugin/` 中的技能。将过度准备推入子文件夹和桩，而不是一排空白的顶层目录。

## 阶段 2 — 搭建结构+大脑

- 仅创建分类法要求的文件夹（苗条根）。为每个非明显文件夹编写一个简短的 `README.md` 桩，说明这里应该有什么。

- 从 `assets/dashboard.html.tmpl` 写入 `artifacts/dashboard.html`（HTML，不是 md）。播种 `operations/health.md`（空——`{domain}-doctor` 填充它）和 `operations/improvements.md`（`{domain}-reflect` 账本的头）。

- 从 `assets/CLAUDE.md.tmpl` 写入自我管理的 `CLAUDE.md`，根据领域进行定制（文件决策树、自动管理循环、永不陈旧合同、重复性到技能规则）。阅读 `references/self-management.md` 了解合同必须包含的内容。

- 创建 `AGENTS.md` 作为 `CLAUDE.md` 的符号链接（`ln -s CLAUDE.md AGENTS.md`），以便代理运行器查找 `CLAUDE.md` 或 `AGENTS.md` 都得到相同的大脑。如果符号链接不受支持，请编写一个 `AGENTS.md`，其中说明“查看 CLAUDE.md”——但优先选择符号链接。

## 阶段 3 — 播种复合资产

- 填充 `library/`（您会重复使用的空白乐器——模板、脚本、清单）和 `knowledge/`（您会回顾的已解决答案——常见问题解答、见解、决策、标准操作程序）。经验法则：如果您会 *使用* 它来制作某物，则为 `library/`；如果您会 *参考* 它来决定某事，则为 `knowledge/`。

- 从输入中提取这些材料。对于稀疏输入，播种领域合理的启动模板，并将它们标记为“草稿——确认”。

## 阶段 4 — 编写技能（就地 `plugin/`）

阅读 `references/skill-authoring.md` 和 `references/skillifying-work.md`（提升工作流程）。

- 从领域派生插件名称为 `{DOMAIN_SLUG}-os`（连字符小写），除非用户明确给出了名称。在所有清单中使用该名称。

- 搭建 `plugin/` 作为就地真实插件：`plugin/.claude-plugin/plugin.json` 从 `assets/claude-plugin.json.tmpl`，`plugin/.codex-plugin/plugin.json` 从 `assets/codex-plugin.json.tmpl`，以及一个 `plugin/skills/` 目录。Codex 清单必须包括 `"skills": "./skills/"`；请参阅 `references/packaging.md`。

- 创建 `.agents/skills` 作为指向 `../plugin/skills` 的符号链接，以便 Cursor 和 Codex 可以发现相同的项目技能。如果符号链接不受支持，请复制 `plugin/skills/` 到那里，并注意它是一个兼容性镜像。

- 对于摘要中的每个重复性任务，编写 `plugin/skills/{name}/SKILL.md`（前文 `name` + 描述带有真实触发短语，然后是引用工作空间路径的祈使步骤）。

- 始终包括维护技能（OS 的反馈器官），从模板生成：
  - 一个**医生**（`assets/doctor-SKILL.md.tmpl`）——只读验证表面（健康分数 + 拳头列表到 `operations/health.md`）；清洁工和构建报告都依赖于它。还生成 `operations/doctor.py` 从 `assets/doctor.py.tmpl`（填写 `PIPELINE`/`ENTITY`/slug）作为其确定性快速路径——因此机械检查随构建一起交付，而不是以后重新发明。

  - 一个**清洁工**（`assets/janitor-SKILL.md.tmpl`）——运行医生，然后安全地协调和修复。

  - 一个**复合学习**技能（`assets/compound-learn-SKILL.md.tmpl`）——在每次工作会话后，将决策/答案/模式捕获到 `knowledge/`。

  - 一个**反思**技能（`assets/reflect-SKILL.md.tmpl`）——改进 OS 本身（技能、路由、检查、模板）到 `operations/improvements.md`；50/50 预算。

  - 一个**技能化**技能（`assets/skillify-SKILL.md.tmpl`）——将已证明的重复性工作提升为经过验证的阶段技能。

- 还包括一个编排器技能（自动管理循环作为一个触发器），命名为 `{domain}-intake`。

- **路由保持苗条：** 在包很小的情况下，依赖每个技能的 `description` 进行路由；只有当技能增长到描述重叠或医生的可达性检查标记歧义时，才添加 `plugin/skills/RESOLVER.md`（触发器->技能表）。

- 仅对重复性或需要维护的工作编写技能——一次性构建属于 `work/`，而不是一个可丢弃的技能。对于从已完成工作中创建的技能，请遵循技能化循环：证明来源，提取可重复的过程，在 `work/` 中阶段化，使用最合适的领域检查进行验证，在移动到 `plugin/skills/` 之前询问，然后重新打包。

## 阶段 5 — 打包插件

阅读 `references/packaging.md`。

- 首先运行 `{domain}-doctor`——打包受一个干净（或解释）的报告控制。

- 工作区 `plugin/` 目录已经是可安装的插件——不需要复制。验证它：每个 `plugin/skills/*/` 都有一个 `SKILL.md`；两个插件清单都是有效的 JSON，并共享 `{DOMAIN_SLUG}-os` 名称；Codex 清单指向 `./skills/`；**任何描述中都没有尖括号**；`plugin/skills/` 中没有散乱的非技能文件夹；`.agents/skills` 指向或镜像 `plugin/skills/`。在打包之前修复。

- 首先将 `plugin/` 的内容 `zip` 到 `/tmp`，然后复制 `.plugin` 到输出文件夹并呈现它以供安装。

## 阶段 6 — 连接永不陈旧的计划

- 尝试创建一个计划任务来运行清洁工技能（默认每周），以便即使用户不在，工作空间也能自我协调。

- **如果没有可用的调度工具，或者用户拒绝：** 这不是一个失败。在 `operations/routines.md` 中记录预期的频率，并且从 `assets/janitor-schedule.tmpl`（GitHub Actions / cron / launchd / agent-runner 任务）中放置一个准备就绪的计划，以便稍后启用它是一个简单的复制，而不是一个研究项目。OS 仍然是完整的——清洁工也按需运行——但直到计划被启用，医生会保持一个持续的“计划已启用”发现，因为“在无人看管时自我协调”只有在它实际上运行不attended 时才为真。

- 不要阻塞或让构建“未完成”由于调度；将其视为一个可选步骤。

## 阶段 7 — 报告

运行 `{domain}-doctor` 并报告其分数作为构建的验证表面——“完成”是一个干净的（或解释的）医生运行，而不是感觉。总结：创建的结构、编写的技能、生成的插件、设置的计划以及健康分数。列出推断与确认的内容，以便用户可以纠正任何假设。

## 安全网

- 不要编造用户必须拥有的领域事实——将推断的项目标记为“草稿——确认”。

- 确保没有任何东西陈旧：如果您触摸了项目，请在同一轮中更新仪表板、看板和任何受影响的 README。

- 优先改进模板/技能，而不是一次性实例。
