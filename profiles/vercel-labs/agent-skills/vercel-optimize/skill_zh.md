# Vercel 优化

运行以可观察性为先的 Vercel 优化审计。在 `signals.json` 存在且确定性门控指向路由、文件或项目设置之前，不要检查源文件。

核心原则：如果任何规则不明确，请阅读 [参考资料/原则.md](references/doctrine.md)。

- 首要指标。建议从 Vercel 生产信号开始，而不是全仓库的 grep。
- 确定性门控。`scripts/gate-investigations.mjs` 决定哪些值得调查。
- 候选范围绑定。仅读取由候选者或路由本地导入链命名的文件。
- 版本感知引用。仅使用 `references/docs-library.json`；无效或版本不匹配的引用将被移除。
- 客户文案。在编写报告文本或聊天输出之前，请阅读 [参考资料/声音.md](references/voice.md)。

## 前置条件

- Vercel CLI v53+，包含 `vercel metrics`、`vercel usage`、`vercel contract` 和 `vercel api`。
- 经过身份验证的 CLI 会话：`vercel login`。
- 链接的应用目录：`vercel link`。`VERCEL_PROJECT_ID` 有助于解析项目配置，但 `vercel metrics` 仍然需要目录链接。链接或环境必须包含预期的项目组织/团队/用户范围，以便收集器可以解析 CLI 安全的 `--scope` 并保持 `vercel metrics`、`vercel usage` 和 `vercel contract` 在同一账户上。
- Node.js 20+。
- 可观察性 Plus，用于基于指标的路线级建议。

永远不要在 shell 命令中放入认证令牌。不要在可能会在聊天中回显的命令中输入 `VERCEL_TOKEN=...`、`--token ...` 或 `Authorization: Bearer ...`。

## 框架支持

在指标发散之前，preflight 会读取 `package.json` 并设定预期。

| 框架 | 状态 | 备注 |
|---|---|---|
| Next.js App Router | 支持 | 最强的路线映射、扫描器、剧本、引用 |
| Next.js Pages Router | 支持 | 检测到时限定于 Pages Router 习惯用法 |
| SvelteKit | 支持 | `src/routes` 文件的路线映射和 SvelteKit 扫描器 |
| Nuxt | 支持 | 路线映射加上通用/平台检查；框架特定建议较少 |
| Astro | 有限 | 路线映射加上通用检查；框架特定建议较少 |
| Hono / Remix / 未知 | 默认阻止 | 只有在用户接受有限的平台/代码审计时才继续 |

如果不受支持，请在扫描或门控之前停止并询问：

```text
此项目使用 <framework>。Vercel Optimize 支持基于指标的 Next.js、SvelteKit 和 Nuxt 代码建议。Astro 支持有限。对于 <framework>，我仍然可以运行有限的平台/扫描器审计，但路线级 Vercel 指标可能无法映射回源文件。

您想让我继续进行有限的审计，还是在这里停止？
```

如果用户继续，使用 `--continue-unsupported-framework` 重新运行收集。

## 运行目录

为每次审计使用一个全新的运行目录。不要跨运行重用简报、子代理输出或报告。

```bash
RUN_DIR="$(mktemp -d -t vercel-optimize-XXXXXX)"
```

## 管道

### 1. 收集、扫描和合并信号

从链接的应用目录运行，或者在支持 `--cwd` 的脚本中传递。保持 stdout JSON 与 stderr 日志分开。不要组合流。

```bash
node scripts/collect-signals.mjs [projectId] > "$RUN_DIR/vercel-signals.json" 2> "$RUN_DIR/collect.stderr"
node -e 'JSON.parse(require("fs").readFileSync(process.argv[1], "utf8"))' "$RUN_DIR/vercel-signals.json"

node scripts/scan-codebase.mjs <repo-root> > "$RUN_DIR/codebase.json"
node scripts/merge-signals.mjs "$RUN_DIR/vercel-signals.json" "$RUN_DIR/codebase.json" --out "$RUN_DIR/signals.json"
```

收集细节、模式、指标 ID 和退化行为位于 [参考资料/数据收集.md](references/data-collection.md)。指标注册表是 [lib/queries.mjs](lib/queries.mjs)；保持所有查询在共享的 14 天窗口内。

`collect-signals.mjs` 解析链接的项目所有者到 `commandScope.cliScope`，并在检查可观察性 Plus 之前验证解析的账户是否可以读取解析的项目。下游脚本重用该范围用于每个接受 `--scope` 的 Vercel CLI 命令。不要在没有相同范围的情况下手动运行 `vercel usage`、`vercel metrics` 或 `vercel contract`；无范围的用法可能会报告用户的个人组织，而路线指标来自团队项目。

如果项目或范围解析不明确，停止并询问用户他们想审计哪个 Vercel 项目和团队/个人范围。不要从当前的 `vercel whoami` 团队推断预期范围，并且在指标、使用量或合同收集之前，不要继续，直到链接、`.vercel/repo.json` 中的确切项目匹配或 `VERCEL_PROJECT_ID` + `VERCEL_ORG_ID` 确定预期账户。

使用此提示符用于 `PROJECT_SCOPE_UNRESOLVED`、`SCOPE_UNRESOLVED` 或 `PROJECT_SCOPE_MISMATCH`：

```text
我无法安全地识别此审计的 Vercel 项目和账户。

请确认 Vercel 项目名称或 ID 和团队别名/名称，或者告诉我它属于您的个人账户。确认后，我将在该确切范围内重新链接或重新运行收集，然后再检查指标。
```

### 1.1 在门控前检查阻止项

```bash
jq '{frameworkSupportBlocker, observabilityPlus, observabilityPlusUsable, observabilityPlusBlocker, observabilityPlusBlockerDetail}' "$RUN_DIR/signals.json"
```

必需操作：

- `frameworkSupportBlocker === "unsupported_framework"`：使用上述不支持框架的提示。
- `PROJECT_SCOPE_UNRESOLVED`、`SCOPE_UNRESOLVED` 或 `PROJECT_SCOPE_MISMATCH`：停止并询问用户他们想审计哪个 Vercel 项目和团队/个人范围。对于团队项目，在 `vercel link --yes --project <project-name-or-id> --team <team-slug>` 后重新运行；对于个人项目，在预期用户账户下链接或设置 `VERCEL_PROJECT_ID` 和 `VERCEL_ORG_ID` 后重新运行。
- `observabilityPlusBlocker === null`：继续。
- `no_traffic`：告诉用户路线指标稀疏；只有在他们接受有限输出时才继续。
- `payment_required` 或 `no_oplus_probe`：逐字显示 [参考资料/可观察性 Plus.md](references/observability-plus.md) 并询问。
- `project_disabled`：告诉用户为项目启用可观察性 Plus 或接受有限的审计。
- `daily_quota_exceeded`：停止并告诉用户可观察性查询配额已用尽；在下一个 UTC 午夜重置后重试，或询问是否继续进行有限的代码审计。
- `not_linked`：链接应用目录，然后重新运行步骤 1。如果已知应用路径和项目：

```bash
vercel link --yes --project <project-name-or-id> --cwd <app-dir>
# 知道时添加 --team <team-id-or-slug>
```

- `forbidden` 或 `project_not_found`：修复认证/团队范围。不要推销可观察性 Plus。
- `all_failed_other`：显示原始错误代码并询问是否以有限的代码模式继续。

不要无声地回退到代码模式。如果用户接受有限的审计，使用：

```bash
node scripts/collect-signals.mjs [projectId] --continue-without-observability > "$RUN_DIR/vercel-signals.json" 2> "$RUN_DIR/collect.stderr"
```

然后再次扫描和合并。

### 2. 门控候选者

```bash
node scripts/gate-investigations.mjs "$RUN_DIR/signals.json" > "$RUN_DIR/gate.json"
```

输出形状：

- `toLaunch`：代码范围候选者进行调查。
- `platform`：项目/账户范围建议。
- `gated`：必须仍然出现在报告中的跳过、覆盖或取消资格的候选者。
- `budget`：候选者预算和选择模式。

默认预算是 6 个代码范围候选者，带有多样性保护措施。要扩展：

```bash
node scripts/gate-investigations.mjs "$RUN_DIR/signals.json" --max-candidates 12 > "$RUN_DIR/gate.json"
node scripts/gate-investigations.mjs "$RUN_DIR/signals.json" --max-candidates all > "$RUN_DIR/gate.json"
```

生成的候选者文档：[参考资料/候选者.md](references/candidates.md)。

### 2.1 当需要时询问审计范围

在深入调查之前，运行：

```bash
node scripts/budget-summary.mjs "$RUN_DIR/gate.json" --format json > "$RUN_DIR/budget-summary.json"
```

如果 `shouldAsk` 为 false，继续。

如果 `shouldAsk` 为 true：

1. 精确打印 `exactChatMessage.body` 返回的内容。不要总结、截断、重新排序或重写它。
2. 然后使用 `questionPayload` 在主机支持结构化问题时询问 `questionText`。
3. 如果用户选择不同的数字，使用 `--max-candidates <choice>` 重新运行门控。

永远不要将长预览放在问题字段内。预览和问题是分开的表面。

### 2.2 深入调查和协调

```bash
node scripts/deep-dive.mjs "$RUN_DIR/signals.json" "$RUN_DIR/gate.json" --cwd <project-dir> > "$RUN_DIR/investigation-evidence.json"

node scripts/reconcile-candidates.mjs "$RUN_DIR/investigation-evidence.json" \
  --gate "$RUN_DIR/gate.json" \
  --out "$RUN_DIR/reconciled-investigation.json"
```

`--cwd` 必须是链接的项目目录，以便 `deep-dive.mjs` 可以验证相同的项目链接并重用 `signals.json.commandScope.cliScope` 用于任何后续的 `vercel metrics` 调用。

协调会在任何源调查之前将证伪的候选者确定性地转换为观察：

- `metric_mismatch`
- `error_storm`
- `deployment_regression`
- `scanner_only_no_metric`

### 2.3 生成简报并调查

列出工作：

```bash
node scripts/prepare-investigation-brief.mjs "$RUN_DIR/signals.json" "$RUN_DIR/reconciled-investigation.json" --list > "$RUN_DIR/briefs-manifest.json"
```

为 `briefs-manifest.json.briefs` 中的每个条目生成一个简报。`group` 可以是 `toLaunch` 或 `platform`；不要仅生成 `toLaunch` 简报。

```bash
mkdir -p "$RUN_DIR/briefs" "$RUN_DIR/sub-agent-outputs"
node scripts/prepare-investigation-brief.mjs "$RUN_DIR/signals.json" "$RUN_DIR/reconciled-investigation.json" \
  --group <brief.group> --index <brief.index> --out "$RUN_DIR/briefs/<brief.group>-<brief.index>.md"
```

使用 `briefs-manifest.json.briefs[].label` 作为可见的工作者名称，例如 `Low cache-hit route on /docs/llm-digest/[...slug]`，而不是 `toLaunch-7`。

发散规则：

- 1-2 简报：内联调查。
- 3+ 简报：当主机支持时，为每个简报生成一个子代理。
- 没有子代理的主机：串行内联运行。

子代理合同：

- 简报是整个提示。
- 仅读取简报中列出的文件，并在需要时读取路由本地导入。
- 使用 [参考资料/建议.md](references/recommendations.md) 发出一个 JSON 建议或一个 JSON 无变更发现。
- 不要引用提供的引用子集之外的 URL。
- 不要推荐检测版本中不可用的框架功能。

如果一个子代理试图进行全仓库 grep，候选者就是格式错误的；丢弃或 abstain 而不是扩大范围。

### 2.4 收集输出

将每个原始调查结果保存在 `$RUN_DIR/sub-agent-outputs/`，然后收集：

```bash
node scripts/collect-sub-agent-outputs.mjs \
  --manifest "$RUN_DIR/briefs-manifest.json" \
  --out "$RUN_DIR/recommendations.json" \
  "$RUN_DIR/sub-agent-outputs/"
```

收集器提取 JSON，预置预解析记录，执行清单顺序，并在 `candidateRef` 值缺失、重复、未知或匹配失败时失败。

### 3. 验证建议

```bash
node scripts/verify-and-regen.mjs "$RUN_DIR/recommendations.json" \
  --signals "$RUN_DIR/signals.json" \
  --repo-root <project-dir> \
  --out "$RUN_DIR/verify.json"
```

此脚本提取声明，验证文件/引用/版本匹配，评分质量，应用清理器，发出 `verifiedRecommendations`、`withheldRecommendations`、`renderableRecommendations`，并为失败或不安全的建议创建 `regenPlan`。

建议模式、编写规则、清理器顺序和评分规则：[参考资料/建议.md](references/recommendations.md)。验证规则：[参考资料/验证.md](references/verification.md)。

对于每个 `regenPlan` 条目，使用相同的简报，并在“之前的尝试失败这些检查”部分列出 `topFailures`。如果验证改进且不破坏引用，则保留重新生成的输出。

### 4. 渲染报告和最终消息

```bash
node scripts/render-report.mjs "$RUN_DIR/verify.json" "$RUN_DIR/gate.json" "$RUN_DIR/signals.json" \
  --project <name> \
  --out "$RUN_DIR/report.md" \
  --message-out "$RUN_DIR/final-message.json"
```

仅在开发技能时使用 `--debug-out "$RUN_DIR/debug.json"`。客户 Markdown 和聊天输出不得暴露 `passRate`、`quality`、清理器轨迹、原始子代理名称或其他实现字段。

渲染后，逐字打印 `final-message.json.body` 并停止。不要添加高亮、调试笔记、原始计数、子代理摘要或额外解释。由于渲染时去重、平台限制和硬安全降级可能会改变客户可见计数，因此永远不要从原始 `verify.json` 总结。

报告结构和影响框架：[参考资料/评分.md](references/scoring.md)。

## 建议规则

每个建议必须：

- 追溯到已发布的候选者、平台候选者、预解析观察或验证的流量无关扫描器发现。
- 包括来自 `signals.json` 或 `evidence.deepDive` 的观察指标证据。
- 涉及代码时，引用验证的文件并包含行号。
- 包含至少一个适用于检测框架/版本的允许引用。
- 使用精确的观察性能数字。
- 仅使用成本幅度短语；永远不要使用面向客户的 `$N` 节省。
- 不要为 Vercel Workflow 运行时端点（`/.well-known/workflow/v1/*`）推荐持续时间减少。这些是用于持久步骤/流程执行的生成编排路由，应在调查之前硬门控。
- Workflow 建议必须命名被改变的边界。有效示例：排队持久工作并返回运行 ID 而不是等待完成，修复流重播/关闭/锁，或减少验证的过量 Workflow 步骤/存储。不要从 Workflow 端点墙钟持续时间推断成本节省。
- 对于流、SSE、可恢复聊天或其他有意长生命周期的路由，不要单独将墙钟函数持续时间视为问题。需要证据证明可避免的预第一个字节工作、高活跃 CPU、重复调用或可以移出用户可见路径的响应后工作。
- 推荐缓存时指定特定缓存策略。
- 除非证据证明它们可以安全缓存，否则保持不安全响应动态：认证敏感路径、错误、后备响应、缺失内容、无效请求、地理位置/设备变化输出和未版本化的动态 URL。

永远不要建议“验证 X 是开启的”，因为事实已经存在于 `signals.project` 中，包括 Fluid 计算状态、内存层级、区域、函数内并发和超时。

## 扫描器规则

扫描器发现是补充的。除非扫描器声明 `metadata.trafficIndependent === true`，否则丢弃标记为 `COLD-PATH` 或 `NO-ROUTE-MAPPING` 的发现。

流量无关示例：中间件匹配器、源映射、React 编译器配置、构建设置。路线本地缓存或数据获取模式需要路线级流量证据。

扫描器文档：[参考资料/扫描器模式.md](references/scanner-patterns.md)。

## 最终客户术语

使用：

- `recommendations ready`
- `observations from investigation`
- `investigated, no change recommended`
- `not investigated in this run`

避免：

- `sub-agent`
- `abstention`
- `passRate`
- `quality score`
- `gate`
- `LLM`

## 失败文案

使用这些消息，不要添加销售文案或流程细节。

**过去 14 天没有流量：**

> 此项目在过去 14 天内没有有意义的流量，因此路线级指标稀疏。我仍然可以检查流量无关的扫描器发现和项目设置，但直到流量累积我才可能对路线修复进行排名。

**路线级指标不可用：**

> 使用 [参考资料/可观察性 Plus.md](references/observability-plus.md) 中的逐字选择模板。不要无声地回退到代码模式；提供两条路径的选择：启用可观察性 Plus 并重新运行基于指标的审计，或接受有限的代码运行。

**项目未链接：**

> 此工作区未链接到 Vercel 项目。运行 `vercel link --yes --project <project-name-or-id> --cwd <app-dir>` 并重新运行审计。如果团队已知，添加 `--team <team-id-or-slug>`。
