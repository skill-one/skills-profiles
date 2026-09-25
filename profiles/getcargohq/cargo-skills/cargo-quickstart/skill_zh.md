# Cargo 快速入门——两分钟获取首个价值

一个引导式演示：拉取用户选择的买家画像匹配的约 25 条新鲜线索，展示费用收据，然后将其保存为周期性任务。重点不在于列表——关键在于第 3 分钟时用户拥有一个运行中的系统，而不是一次性结果。

**新账户初始包含 100 个免费额度——无需信用卡。** 此演示会消耗大约 **0.5** 个额度。在首次付费调用前大声说出这一点（“这大约消耗了你 100 个免费额度中的 0.5 个”）：这会将决策从 *购买决定* 转变为 *探索过程*，这正是快速入门的全部工作。切勿让新用户认为演示会导致他们用完额度。

## 快速启动

已登录（`cargo-ai whoami` 返回工作区）？跳至下一节。

```bash
npm install -g @cargo-ai/cli            # 没有全局安装？为每个命令前缀 `npx @cargo-ai/cli`
cargo-ai login --email you@company.com  # 发送验证码，无需浏览器；首次使用时创建账户
                                        # 替代方案：--oauth（浏览器） · --token <api-token>（CI）
cargo-ai whoami                         # 任何写入操作前确认活动工作区
```

每个命令将 JSON 打印到标准输出；失败时以非零状态退出并打印 `{"errorMessage": "..."}`。创建运行或批次的任何操作都是异步的——传递 `--wait-until-finished` 或轮询匹配的 `get`。当完整技能包安装后，[`../cargo/references/prerequisites.md`](../cargo/references/prerequisites.md) 会添加 CLI 版本固定、令牌范围和管理员专有界面。

## 一个问题

在执行任何操作前，仅问 **一个问题**：

> **“你向谁销售？”**（用几句话描述的画像——例如“中端 SaaS 的 RevOps 负责人”）

其他所有内容——提供者、过滤器、限制——你自行决定。不要询问输出格式、数量或提供者；下方为默认设置。

## 时间预算——硬性规则

演示从回答到交付成果的时间预算为两分钟。在快速路径上：

- **无发现性绕道。** 不要先运行 `cargo-ai --version`、`cargo-ai whoami`、`connection connector list` 或任何探索性命令。认证问题将在首次真实调用时作为错误出现——届时再处理。
- **每步一个命令块**，命令间无旁白。
- **付费工作总额度限制为约 1 个额度。** 演示使用目录中最便宜的拉取操作（`salesNavigator.searchLeads`，0.02/记录 → 25 记录 ≈ 0.5 额度）。未经询问，不得运行其他付费操作。
- **永不卡住。** 每步都有备用方案（下方梯子）。如果某级失败，静默降一级并继续。

## 快速路径

将画像翻译为 `searchLeads` 过滤器（在 `keywords` 中引用确切的标题短语；纯关键词匹配宽松且污染页面）并运行：

```bash
# 1. 执行——返回运行对象；注意 run.uuid 和 run.workflowUuid。
#    searchLeads 返回至少 25 行的页面（限制低于 25 仍计费 25 × 0.02 = 0.5 额度）。
cargo-ai orchestration action execute \
  --action '{"kind":"connector","integrationSlug":"salesNavigator","actionSlug":"searchLeads"}' \
  --data '{"keywords": "\"<persona title phrase>\"", "limit": 25}' \
  --wait-until-finished > /tmp/quickstart-run.json

# 2. 获取输出数据（不在 execute 标准输出中）——签名 URL，然后过滤为当前运行
RUN_UUID=$(jq -r '.run.uuid' /tmp/quickstart-run.json)
WF_UUID=$(jq -r '.run.workflowUuid' /tmp/quickstart-run.json)
curl -s "$(cargo-ai orchestration run download-outputs \
  --workflow-uuid "$WF_UUID" --output-node-slug action --format json | jq -r '.url')" \
  > /tmp/quickstart-outputs.json

# 3. 显示表格（文件包含工作流的所有运行——按 _uuid 过滤；
#    每行 .output 是直接返回的线索数组，字段为 snake_case）
jq -r --arg u "$RUN_UUID" \
  '[.[] | select(._uuid==$u)][0].output[] | [.full_name, .job_title, .company_name, (.recently_hired // false)] | @tsv' \
  /tmp/quickstart-outputs.json | head -25
```

显示表格（姓名 · 职位 · 公司 · 最近入职），而非原始 JSON。`recently_hired: true` 行是演示的亮点——这些线索（“25 条中 6 条刚入职——正是联系的最佳时机”）。

### 备用梯子（认证/错误时降级——不停顿）

1. `salesNavigator.searchLeads`（0.02/记录）——主要。
2. `theirStack.searchJobs`（0.5）——重新定义为“当前正在招聘你画像的公司”（针对画像职位的职位发布）。同样震撼，但角度不同。
3. `waterfall.searchProspects`（3/记录）——**超出约 1-额度演示上限，因此此级先询问**：“两个廉价来源未连接；我可以通过 waterfall 拉取 5 条匹配项，约 15 额度——运行它，或先连接 Sales Navigator（免费）？” 仅在明确同意时运行，且 `limit` 限制为 5。
4. 完全未连接任何来源 → 运行免费路径：`cargo-ai connection integration list | head`，展示可连接的内容，并提议连接一个（浏览器认证）——演示在之后继续。

## 收据（强制，逐字纪律）

演示本身是 [`../cargo-gtm/references/cost-discipline.md`](../cargo-gtm/references/cost-discipline.md) 的试点。以收据结束：

- 消耗额度 + 剩余额度（`cargo-ai billing subscription get` — 剩余 = `subscriptionAvailableCreditsCount − subscriptionCreditsUsedCount`）。对于全新账户，将其与 **100 个免费初始额度**对比，而非直接显示数字——“消耗 0.5，剩余你 100 个免费额度中的 99.5”与“剩余 99.5 额度”给人的感受截然不同。
- 击中率：“25/25 返回”（或实际返回的数量，以及哪些行看起来异常）。

## 第 3 分钟——保存为任务

立即提议将拉取设置为周期性——这是展示 Cargo 本质的关键步骤：

> “想让它自动运行？我可以将此精确搜索保存为任务，每周运行并将新匹配项写入模型——新的 `<persona>` 线索无需你询问即可到达。”

同意后，遵循 [`../cargo-gtm/recipes/save-as-play.md`](../cargo-gtm/recipes/save-as-play.md)，以演示的操作 + 过滤器作为工作流主体，并设置每周 cron。

## 演示后——引导后续

根据刚拉取的行，提出 2–3 个后续步骤，参考 [`../cargo-gtm/SKILL.md`](../cargo-gtm/SKILL.md)（§4）中的下一步规范：例如“用 firmographics 丰富这 25 条（每条约 0.5 额度）”、“为前 10 条验证邮箱（每条约 1.4 额度）”，或完全不同的内容。从此时起，真实的市场推广工作属于 [`cargo-gtm`](../cargo-gtm/SKILL.md) —— 在进行演示之外的任何操作前阅读它。
