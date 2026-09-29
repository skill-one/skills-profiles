---
name: archify
description: 创建经过润色、验证的架构、工作流、时序、数据流和生命周期/状态图，以可探索的独立HTML格式呈现，支持内联SVG、明暗主题、可选的轨迹动画，并支持PNG/JPEG/WebP/SVG/WebM导出。可接受自然语言需求或粘贴的Mermaid flowchart、sequenceDiagram和stateDiagram输入；当图需要反映实际代码时，可检查代码库证据。适用于用户要求可视化系统架构、基础设施、云/安全/网络拓扑、技术工作流、API调用序列、请求生命周期、数据管道、ETL/ELT、数据溯源、状态机，或用于转换/美化Mermaid的场景。
---

# Archify

从输入的 JSON 创建交互式 HTML 图表。静态输出是默认设置；仅在请求时启用动画效果。

从您的工作目录运行命令。除非用户指定其他位置，否则为每个新的图表请求在其所在位置创建一个 `.archify/<type>-<slug>-<YYYYMMDD-HHMMSS>/` 文件夹（本地时间，在请求开始时选择一次）：在该文件夹中保留 `candidate.json` 和 `<slug>.html`，将 `meta.output` 设置为该相对 HTML 路径，并重复使用该文件夹进行每次修复重新运行。后续请求将获得新的文件夹，因此早期版本将保持完整。在下面的命令中，将 `bin/archify.mjs` 替换为已安装包的绝对路径，或相对于您的工作目录的路径；输入和输出路径从此工作目录解析。

对于实际代码库，在跟踪请求的行为时，请阅读 [Repository authoring](references/repository-authoring.md)。系统描述使用以下步骤；现有 JSON 使用交接路径。

## 现有候选交接

当用户提供一个冻结的候选时，首先作为单个 CLI 调用运行 `finalize`。其通过收据完成自动化门禁；在交付之前遵循任何视觉审查建议，然后才能声称视觉质量。对于修复，请遵循步骤 5。

`finalize` 在其交付收据中包含有界更新检查；参见 Update awareness。

## 快速编写路径

用于普通生成。仅在声明的触发条件适用时读取分支引用。

1. 从问题中选择 `architecture`、`workflow`、`sequence`、`dataflow` 或 `lifecycle`。
2. 使用 Type router 中的确切模式和示例路径，而无需列出其目录。阅读 [Authoring defaults](references/authoring-defaults.md) 和模式示例，在独立的有界批次中读取，与项目文档和完整模式分开，以免两者被截断；在编写之前恢复任何缺失的部分。对于 Architecture，使用匹配的展示示例。对于 Sequence、Dataflow 和 Lifecycle，还请阅读模式和常见模式。在选择任何新字段、枚举或约束文本之前，请先阅读相关的模式定义，特别是边界类型。示例用于教学形状，而不是事实。使用新的 ID、措辞和布局。直接进入候选，无需初步帮助、医生、启动验证、临时图表或输出路径列表。仅当用户明确请求标志时才查询品牌；对于未知标志，请阅读 [Brand marks](references/brand-marks.md) 并使用用户提供的 URL。
3. 一旦覆盖了请求的范围，对于实际代码库，请阅读 [source evidence](references/repository-authoring.md)，直接编写完整的候选，而无需在文本中规划坐标。在坐标之前，使用 Authoring defaults 选择 Architecture 抽象和连接放置：显示主要用户旅程和必要的分支，保留控制角色和行为更改条件，并留出足够的空间用于实际关系标签。没有节点、关系、源、视图、卡片或边界计数是目标或上限。首先使用自动路由；仅对于必要的分支、返回、提供的几何形状或测量修复才添加显式路由。除非用户请求密集的 `standard`，否则将 `meta.quality_profile` 设置为 `"showcase"`。
4. 一旦编写了完整的第一个候选，直接运行 `finalize`。其第一个门禁是展示验证；成功的初稿无需单独预验证。在命令运行期间保持候选不变：

   ```bash
   node bin/archify.mjs finalize <type> <candidate.json> <output.html> --quality showcase --json
   ```

   对于基于存储库的候选，在第一个草稿中包含证据，并使用完整的第一个命令：`node bin/archify.mjs finalize <type> <candidate.json> <output.html> --repo-root <repo-root> --quality showcase --json`。

   通过的收据证明包含的 `validate`、`deliver`、严格的 `check` 和真实浏览器 `browser-check` 门禁已通过。使用其紧凑摘要；仅对于单独请求或专注故障诊断才运行独立命令。

5. 非零退出永远不会成功。阅读紧凑的 stdout 或 `evidence.summaryReceipt`，然后 [repair the failed gate](references/delivery-contract.md#failed-finalize-and-candidate-repair)，包括其修复限制。保留请求的含义和源证据。对于多个缠绕的 Architecture 路径，请阅读 [Architecture layout repair](references/architecture-layout-repair.md)；对于测量的字段或几何形状故障，请阅读 [Authoring contract](references/authoring-contract.md)。编辑连接的邻域并从步骤 4 重新运行完整的 `finalize` 命令。

## Update awareness

`finalize` 和独立的 `deliver` 在其收据中包含 `update`。不要为相同的交付运行单独检查。如果 `update.noticeRequired` 为 true，请阅读 `references/update-awareness.md` 并在最终用户响应中保留一条更新行，即使质量门禁失败也是如此。对于具有多个图表的任务，请在最终响应中提及一次更新。仅在用户明确要求时才忽略或暂停提醒；切勿自行安装或更新。

在第一个候选之前，使用编写参考和相关的存储库源，而不是 Archify 实现或测试。如果专注修复后诊断仍然无法解决，请检查 Archify 实现。

## Type router

| Type | Use for | Schema | Example |
|---|---|---|---|
| `architecture` | Components, services, cloud/security boundaries, infrastructure | `schemas/architecture.schema.json` | System descriptions, services, libraries, and CLI repos: `examples/web-app.architecture.json`; deployment repos: `examples/production-deployment.architecture.json` |
| `workflow` | Processes, approval gates, tool calls, runbooks, CI/CD | `schemas/workflow.schema.json` | `examples/agent-tool-call.workflow.json` |
| `sequence` | API call chains, request lifecycles, async traces, returns | `schemas/sequence.schema.json` | `examples/cache-miss-request.sequence.json` |
| `dataflow` | Pipelines, ETL/ELT, lineage, governance, consumers | `schemas/dataflow.schema.json` | `examples/product-analytics.dataflow.json` |
| `lifecycle` | State/status transitions, retries, waiting and terminal states | `schemas/lifecycle.schema.json` | `examples/deployment-release.lifecycle.json` |

当存在歧义时，运行 `node bin/archify.mjs guide "<scenario>" --json`。场景证明示例是结构参考，不是要复制的事实。

## Mermaid input

阅读 Mermaid 以了解拓扑和含义，然后编写新的 Archify JSON；不要机械地渲染 Mermaid 样式。

- `flowchart` / `graph` → `workflow`，或 `architecture` 用于组件地图。
- `sequenceDiagram` → `sequence`；参与者成为语义参与者，箭头成为消息。
- `stateDiagram` → `lifecycle`；状态和转换保留含义，而不是 Mermaid 样式。

## Delivery

使用上述 `finalize` 命令进行第一个候选和修复后。

`finalize` 在第一个未通过的门禁处停止。其紧凑的 stdout 和 `<output-stem>.finalize-summary.json` 是普通证据。通过运行不会创建屏幕截图，并报告 `visualReview: "not-requested"`。

当通过 Architecture 收据报告 `visualReviewRecommendation.signals.resolvedCrossovers` 时，将候选复制到一边，并在一次编辑中仅更改节点位置和大小来应用提示：每个节点、关系（包括其 `from` 和 `to`）、标签和源保持不变。重新运行完整的 `finalize` 一次，使用 `--out-dir <folder>/review-2`，因为之前的 HTML 已经拥有其浏览器证据。如果该运行失败或报告更多交叉，请恢复副本并使用 `--out-dir <folder>/review-3` 进行最终化。不要开始第二个放置轮次。仅当提示关于额外的弯曲时，提示是可选的。

当 `layoutReviewRecommendation.action` 是 `inspect-sequence-width` 时，请遵循 [Sequence width review](references/delivery-contract.md#sequence-width-review) 之前才交付新编写的 Sequence。

对于普通生成，包括重新定位的 Architecture，感知审查是可选的。当用户请求视觉审查、开发审计或具体路由/浏览器问题时，使用 [Optional capture evidence](references/delivery-contract.md#optional-capture-evidence)，使用 `--out-dir <folder>/visual-check`。`visualReviewRecommendation` 是建议性的。在声称视觉质量之前检查捕获；否则仅报告自动化检查。

阅读 [Delivery contract](references/delivery-contract.md) 以了解失败的门禁、独立命令、来源/恢复、重复交付、导出或打开。恢复遵循 `deliver` → 严格的来源 `check` → `browser-check`；捕获需要严格的来源。

对于工作流视口溢出，请在下一个布局编辑之前阅读 [Workflow viewport repair](references/authoring-contract.md#workflow-viewport-repair)。

报告工件检查、浏览器证据、捕获和实际感知审查作为不同的结果。对于明确请求的立即预览或活动桌面循环，请参阅 [Optional opening](references/delivery-contract.md#optional-opening)。

## Optional viewer capabilities

`meta.animation: "trace"` 是可选的。

仅当用户明确要求 Share Cards、Route/Reach cards、动画、深度链接、演示、搜索/聚焦或另一个 Viewer Runtime 功能时，请阅读 `references/viewer-runtime.md`。

## Setup and fallback

无需在技能包内安装。对于设置诊断，请验证：

```bash
node bin/archify.mjs doctor
node bin/archify.mjs demo <output-directory>
```

当无法访问 shell 时，将架构 SVG 手动放置到 `assets/template.html`，使用 CSS 语义类而不是内联颜色，并遵循 `references/delivery-contract.md` 中的视觉审查合同。

## Output

将检查的 HTML 作为绝对路径、图表类型、验证摘要、规范/工件收据、浏览器证据状态和真实的视觉审查状态返回。不要为非零命令或未执行的视觉检查声称成功。
