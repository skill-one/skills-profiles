# Vercel Optimize

执行以可观测性为首要导向的 Vercel 优化审计。在 `signals.json` 存在且确定性门控指向某条路由、文件或项目设置之前，不得检查源代码文件。

核心原则：若任何规则不明确，请阅读 [references/doctrine.md](references/doctrine.md)。

- **指标优先**：建议应基于 Vercel 生产环境中的信号，而非对代码库进行全范围搜索。
- **确定性门控**：由 `scripts/gate-investigations.mjs` 决定哪些值得开展调查。
- **候选边界范围**：仅读取由候选对象或路由本地导入链指定的文件。
- **版本感知引用**：仅使用 `references/docs-library.json`；无效的或版本不匹配的引用将被剔除。
- **客户文案**：在撰写报告文本或聊天输出之前，请阅读 [references/voice.md](references/voice.md)。

## 前置条件

- Vercel CLI v53+，支持 `vercel metrics`、`vercel usage`、`vercel contract` 和 `vercel api`。
- 已认证的 CLI 会话：`vercel login`。
- 已关联的应用目录：`vercel link`。`VERCEL_PROJECT_ID` 可帮助解析项目配置，但 `vercel metrics` 仍要求目录关联。链接或环境必须包含预期的项目组织/团队/用户范围，以便采集器能够解析 CLI 安全的 `--scope`，并让 `vercel metrics`、`vercel usage` 和 `vercel contract` 使用同一账户。
- Node.js 20+。
- 可观测性 Plus（Observability Plus），用于基于路由级指标的推荐。

切勿将认证令牌放入 shell 命令中。不要在任何可能被回显到聊天的命令中输入 `VERCEL_TOKEN=...`、`--token ...` 或 `Authorization: Bearer ...`。

## 框架支持

预检会读取 `package.json` 并在指标分发前设定预期。

| 框架 | 状态 | 备注 |
|---|---|---|
| Next.js App Router | 支持 | 最强的路由映射、扫描器、操作手册、引用 |
| Next.js Pages Router | 支持 | 检测到时为 Pages Router 惯用法限定范围 |
| SvelteKit | 支持 | 针对 `src/routes` 文件及 SvelteKit 扫描器进行路由映射 |
| Nuxt | 支持 | 路由映射及通用/平台检查；框架特定建议较少 |
| Astro | 有限 | 路由映射及通用检查；框架特定建议较少 |
| Hono / Remix / 未知 | 默认被阻止 | 仅在用户接受有限平台/仅代码审计时继续 |

若不受支持，在扫描或门控前停止并询问：

```text
该项目使用 <framework>。Vercel Optimize 支持为 Next.js、SvelteKit 和 Nuxt 提供基于指标的代码建议。Astro 支持有限。对于 <framework>，我仍可运行有限的平台/扫描器审计，但路由级 Vercel 指标可能无法映射回源代码文件。

您是否希望我继续以有限审计模式运行，还是在此处停止？
```

若用户继续，则使用 `--continue-unsupported-framework` 重新运行采集。

## 运行目录

每次审计都使用全新的运行目录。不得在不同运行间复用简报、子代理输出或报告。

```bash
RUN_DIR="$(mktemp -d -t vercel-optimize-XXXXXX)"
```

## 流水线

### 1. 采集、扫描并合并信号

从已关联的应用目录运行，或传入脚本支持的 `--cwd`。保持 stdout JSON 与 stderr 日志分离，不得合并流。

```bash
node scripts/collect-signals.mjs [projectId] > "$RUN_DIR/vercel-signals.json" 2> "$RUN_DIR/collect.stderr"
node -e 'JSON.parse(require("fs").readFileSync(process.argv[1], "utf8"))' "$RUN_DIR/vercel-signals.json"

node scripts/scan-codebase.mjs <repo-root> > "$RUN_DIR/codebase.json"
node scripts/merge-signals.mjs "$RUN_DIR/vercel-signals.json" "$RUN_DIR/codebase.json" --out "$RUN_DIR/signals.json"
```

采集详情、模式、指标 ID 及降级行为请参阅 [references/data-collection.md](references/data-collection.md)。指标注册表为 [lib/queries.mjs](lib/queries.mjs)；请保持所有查询在共享的 14 天窗口内。

`collect-signals.mjs` 会将关联的项目所有者解析为 `commandScope.cliScope`，并在检查 Observability Plus 之前验证解析出的账户是否可以读取解析出的项目。下游脚本会为每个接受 `--scope` 参数的 Vercel CLI 命令复用该范围。不要在不使用相同范围的情况下手动运行 `vercel usage`、`vercel metrics` 或 `vercel contract`；未加范围的 usage 可能报告用户的个人组织，而路由指标则来自团队项目。

若项目或范围解析存在歧义，请停止并询问用户希望审计哪个 Vercel 项目和团队/个人范围。不得根据当前 `vercel whoami` 团队推断预期的范围，且不得在链接、`.vercel/repo.json` 中的精确项目匹配，或 `VERCEL_PROJECT_ID` + `VERCEL_ORG_ID` 识别出预期账户之前，继续进行指标、usage 或 contract 采集。

针对 `PROJECT_SCOPE_UNRESOLVED`、`SCOPE_UNRESOLVED` 或 `PROJECT_SCOPE_MISMATCH`，使用以下提示：

```text
我目前无法安全地识别此审计所需的 Vercel 项目和账户。

请确认 Vercel 项目名称或 ID，以及团队 slug/名称，或告知该项目位于您的个人账户下。确认后，我将在检查指标前重新链接或针对该确切范围重新运行采集。
```

### 1.1 在受阻时停止

在门控前检查受阻情况：

```bash
jq '{frameworkSupportBlocker, observabilityPlus, observabilityPlusUsable, observabilityPlusBlocker, observabilityPlusBlockerDetail}' "$RUN_DIR/signals.json"
```

必要操作：

- `frameworkSupportBlocker === "unsupported_framework"`：使用上述不支持框架的提示。
- `PROJECT_SCOPE_UNRESOLVED`、`SCOPE_UNRESOLVED` 或 `PROJECT_SCOPE_MISMATCH`：停止并询问用户希望审计哪个 Vercel 项目和团队/个人范围。对于团队项目，在 `vercel link --yes --project <project-name-or-id> --team <team-slug>` 后重新运行；对于个人项目，在目标用户账户下重新链接后，或设置 `VERCEL_PROJECT_ID` 和 `VERCEL_ORG_ID` 后重新运行。
- `observabilityPlusBlocker === null`：继续。
- `no_traffic`：告知用户路由指标稀疏；仅在用户接受有限输出时继续。
- `payment_required` 或 `no_oplus_probe`：原样渲染 [references/observability-plus.md](references/observability-plus.md) 并询问。
- `project_disabled`：告知用户为该项目启用 Observability Plus，或接受有限审计。
- `daily_quota_exceeded`：停止并告知用户 Observability 查询配额已耗尽；在下一个 UTC 零点重置后重试，或询问是否以仅代码的有限审计模式继续。
- `not_linked`：关联应用目录，然后重新运行第 1 步。若已知应用路径和项目：

```bash
vercel link --yes --project <project-name-or-id> --cwd <app-dir>
# 已知团队时添加 --team <team-id-or-slug>
```

- `forbidden` 或 `project_not_found`：修复认证/团队范围。不得推销 Observability Plus。
- `all_failed_other`：显示原始错误码，并询问是否以仅代码的有限模式继续。

不得静默回退到仅代码模式。若用户接受有限审计，则使用以下命令重新运行采集：

```bash
node scripts/collect-signals.mjs [projectId] --continue-without-observability > "$RUN_DIR/vercel-signals.json" 2> "$RUN_DIR/collect.stderr"
```

然后再次进行扫描和合并。

### 2. 门控候选对象

```bash
node scripts/gate-investigations.mjs "$RUN_DIR/signals.json" > "$RUN_DIR/gate.json"
```

输出结构：

- `toLaunch`：需要调查的代码范围候选对象。
- `platform`：项目/账户范围建议。
- `gated`：必须仍出现在报告中的被跳过、已覆盖或不予采纳的候选对象。
- `budget`：候选对象预算和选择模式。

默认预算为 6 个代码范围候选对象，并设有多样性保障机制。如需扩展：

```bash
node scripts/gate-investigations.mjs "$RUN_DIR/signals.json" --max-candidates 12 > "$RUN_DIR/gate.json"
node scripts/gate-investigations.mjs "$RUN_DIR/signals.json" --max-candidates all > "$RUN_DIR/gate.json"
```

生成的候选对象文档：[references/candidates.md](references/candidates.md)。

### 2.1 需要时询问审计范围

深入分析前，运行：

```bash
node scripts/budget-summary.mjs "$RUN_DIR/gate.json" --format json > "$RUN_DIR/budget-summary.json"
```

若 `shouldAsk` 为 `false`，则继续。

若 `shouldAsk` 为 `true`：

1. 原样打印 `exactChatMessage.body`。不得总结、截断、调整顺序或改写。
2. 若宿主支持结构化问题，则使用 `questionPayload` 询问 `questionText`。
3. 若用户选择了不同的数量，则使用 `--max-candidates <choice>` 重新运行门控。

切勿将较长的预览内容放入问题字段中。预览与问题是独立的界面。

### 2.2 深入分析与协调

```bash
node scripts/deep-dive.mjs "$RUN_DIR/signals.json" "$RUN_DIR/gate.json" --cwd <project-dir> > "$RUN_DIR/investigation-evidence.json"

node scripts/reconcile-candidates.mjs "$RUN_DIR/investigation-evidence.json" \
  --gate "$RUN_DIR/gate.json" \
  --out "$RUN_DIR/reconciled-investigation.json"
```

`--cwd` 必须是已关联的项目目录，以便 `deep-dive.mjs` 能够验证相同的项目关联，并复用 `signals.json.commandScope.cliScope` 用于后续任何 `vercel metrics` 调用。

协调会确定性地将被推翻的候选对象转换为观察结果，在任何源代码调查之前：

- `metric_mismatch`
- `error_storm`
- `deployment_regression`
- `scanner_only_no_metric`

### 2.3 生成简报并开展调查

列出工作：

```bash
node scripts/prepare-investigation-brief.mjs "$RUN_DIR/signals.json" "$RUN_DIR/reconciled-investigation.json" --list > "$RUN_DIR/briefs-manifest.json"
```

根据 `briefs-manifest.json.briefs` 中的每一项生成一份简报。`group` 可以是 `toLaunch` 或 `platform`；不得仅生成 `toLaunch` 简报。

```bash
mkdir -p "$RUN_DIR/briefs" "$RUN_DIR/sub-agent-outputs"
node scripts/prepare-investigation-brief.mjs "$RUN_DIR/signals.json" "$RUN_DIR/reconciled-investigation.json" \
  --group <brief.group> --index <brief.index> --out "$RUN_DIR/briefs/<brief.group>-<brief.index>.md"
```

使用 `briefs-manifest.json.briefs[].label` 作为可见工作者的名称，例如 `Low cache-hit route on /docs/llm-digest/[...slug]`，而非 `toLaunch-7`。

分发规则：

- 1-2 份简报：内联进行调查。
- 3+ 份简报：若宿主支持，则每份简报生成一个子代理。
- 无子代理的宿主：串行内联执行。

子代理契约：

- 简报即完整提示。
- 仅读取简报中列出的文件，以及在需要时读取路由本地导入。
- 使用 [references/recommendations.md](references/recommendations.md) 发出一份 JSON 建议或一份 JSON 无变更发现。
- 不引用提供引用集合之外的 URL。
- 不推荐检测到的版本中不存在的框架功能。

若子代理试图进行全范围搜索，则候选对象格式有误；应丢弃或中止，而非扩大范围。

### 2.4 收集输出

将每个原始调查结果保存到 `$RUN_DIR/sub-agent-outputs/` 中，然后进行收集：

```bash
node scripts/collect-sub-agent-outputs.mjs \
  --manifest "$RUN_DIR/briefs-manifest.json" \
  --out "$RUN_DIR/recommendations.json" \
  "$RUN_DIR/sub-agent-outputs/"
```

收集器提取 JSON，前置已预解析的记录，强制执行清单顺序，并对于缺失、重复、未知或不匹配的 `candidateRef` 值报错。

### 3. 验证建议

```bash
node scripts/verify-and-regen.mjs "$RUN_DIR/recommendations.json" \
  --signals "$RUN_DIR/signals.json" \
  --repo-root <project-dir> \
  --out "$RUN_DIR/verify.json"
```

该脚本提取声明，验证文件/引用/版本是否相符，评估质量，应用清理器，输出 `verifiedRecommendations`、`withheldRecommendations`、`renderableRecommendations`，并为失败的或不安全的建议创建 `regenPlan`。

建议模式、写入规则、清理器顺序及评分规则：[references/recommendations.md](references/recommendations.md)。验证规则：[references/verification.md](references/verification.md)。

对于每个 `regenPlan` 条目，以 `Previous attempt failed these checks`（上次尝试未能通过以下检查）部分列出 `topFailures` 的方式，重新运行同一简报。仅当验证有所改善且未丢弃引用时才保留重新生成的输出。

### 4. 渲染报告与最终消息

```bash
node scripts/render-report.mjs "$RUN_DIR/verify.json" "$RUN_DIR/gate.json" "$RUN_DIR/signals.json" \
  --project <name> \
  --out "$RUN_DIR/report.md" \
  --message-out "$RUN_DIR/final-message.json"
```

仅当开发该技能时，才使用 `--debug-out "$RUN_DIR/debug.json"`。客户 Markdown 和聊天输出不得暴露 `passRate`、`quality`、清理器轨迹、原始子代理名称或其他实现字段。

渲染后，逐字打印 `final-message.json.body` 并停止。不得添加高亮、调试备注、原始计数、子代理摘要或额外说明。渲染时的去重、平台限制和硬性安全剔除可能会改变面向客户的可视计数，因此不得从原始 `verify.json` 进行总结。

报告结构与影响框架说明：[references/scoring.md](references/scoring.md)。

## 建议规则

每条建议必须：

- 追溯至已启动的候选对象、平台候选对象、预解析观察结果或已验证的流量无关扫描器发现。
- 包含来自 `signals.json` 或 `evidence.deepDive` 的观察指标证据。
- 涉及代码时，引用带行号且已验证的文件。
- 包含至少一条适用于检测到的框架/版本的允许引用。
- 使用精确的观察性能数值。
- 仅使用成本量级表述；绝不使用面向客户的 `$N` 节省。
- 不得为 Vercel Workflow 运行时端点（`/.well-known/workflow/v1/*`）建议减少持续时间。这些是生成持久步骤/流程执行的编排路由，应在调查前被硬性门控。
- Workflow 建议必须命名所变更的边界。有效示例：替代等待完成而批量入队持久任务并返回运行 ID，修复流回放/闭包/锁，或减少已验证的 Workflow Steps/Storage 超额。不得从 Workflow 端点墙钟持续时间推断成本节省。
- 对于流、SSE、可恢复聊天或其他有意长生命周期路由，不得将墙钟函数持续时间本身框定为问题。需有可避免的首字节前工作、高活跃 CPU、重复调用或可移至用户可见路径之外的后响应工作的证据。
- 建议缓存时命名具体的缓存策略。
- 除非有证据证明其可安全缓存，否则保持不安全的响应保持动态：涉及认证的路径、错误、回退响应、缺失内容、无效请求、随地理位置/设备变化的输出以及无版本化的动态 URL。

不得建议“验证 X 处于启用状态”来为 `signals.project` 中已存在的既定事实背书，包括 Fluid 计算状态、内存层级、区域、函数内并发以及超时。

## 扫描器规则

扫描器发现为补充性。除非扫描器声明 `metadata.trafficIndependent === true`，否则丢弃标注为 `COLD-PATH` 或 `NO-ROUTE-MAPPING` 的发现。

流量无关示例：中间件匹配器、源映射、React Compiler 配置、构建设置。路由本地缓存或数据获取模式需要路由级流量证据。

扫描器文档：[references/scanner-patterns.md](references/scanner-patterns.md)。

## 最终客户条款

使用：

- `recommendations ready`
- `observations from investigation`
- `investigated, no change recommended`
- `not investigated in this run`

避免使用：

- `sub-agent`
- `abstention`
- `passRate`
- `quality score`
- `gate`
- `LLM`

## 故障文案

使用以下消息，不得添加销售文案或流程细节。

**最近 14 天无流量：**

> 该项目在最近 14 天无有效流量，因此路由级指标稀疏。我仍可检查流量无关的扫描器发现和项目设置，但在流量积累之前无法对路由修复进行排序。

**路由级指标不可用：**

> 请原样使用 [references/observability-plus.md](references/observability-plus.md) 中的选择模板。不得静默回退到仅代码模式；需呈现两条路径的选择：启用 Observability Plus 并重新运行基于指标的审计，或接受仅代码的有限运行。

**项目未关联：**

> 此工作树未与 Vercel 项目关联。请运行 `vercel link --yes --project <project-name-or-id> --cwd <app-dir>` 并重新运行审计。若已知团队，请添加 `--team <team-id-or-slug>`。

**大多数路由到文件映射失败：**

> 路由清单匹配的数量低于我们观测到的路由数量的一半。这在具有自定义路由的 monorepo 中很常见。我已列出能够匹配的内容；其余内容出现在“本次运行未调查”部分中。
