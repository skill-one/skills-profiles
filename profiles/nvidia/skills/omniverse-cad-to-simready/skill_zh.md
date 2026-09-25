# CAD to SimReady

## 使用场景

使用此工作流技能，从源资产到 SimReady 资产或包，实现端到端的工作流程。它直接协调现有的转换、创作、验证、一致性、渲染和打包参考；不要用单个整体的运行器命令来替代它。

此技能由文档驱动，不包含 `scripts/run.py`；它不能依赖于代码库检出。声明 `Shell` 是因为此工作流直接调用已安装的阶段参考脚本，从每个参考的已安装目录，并且它仍然不能变成一个整体的运行器。

## 前置条件

- 优先使用 `preflight` 进行确定性设置：它安装/验证本地上游检出，写入 `cad-to-simready-preflight.json` 元数据文件，并导出 `PHYSICAL_AI_PREFLIGHT_MANIFEST` 以及 `PHYSICAL_AI_REQUIRE_PREFLIGHT=1` 以供下游参考。
- Python 3.12 和 `uv`（根据每个代码库的 `README.md`）。
- 当本地部署将运行时，需要一个内容代理模型提供密钥，或者对于已经运行的端点，需要明确的端点变量和使用令牌；请参阅 `references/preflight/README.md` 获取完整列表。
- Docker、NVIDIA 容器工具包和一个 NVIDIA GPU，用于内容代理和 OVRTX 阶段。
- 当阶段需要上游脚本或规范时，在 `${OMNIVERSE_CAD_TO_SIMREADY_UPSTREAM_ROOT:-$HOME/.omniverse-cad-to-simready/upstreams}` 下进行本地上游检出。

## 首次操作

对于任何广泛的 CAD/源资产到 SimReady 的请求，除非用户明确要求仅转换、仅验证或不进行材料/物理分配，否则假设 `property_assignment_intent=run`。对于仅转换请求，设置 `property_assignment_intent=skip`，不要部署内容代理，运行 `convert-to-usd`，然后在转换成功后，对生成的 USD 运行 `validate-usd-minimum`。对于仅验证请求，设置 `property_assignment_intent=skip` 并验证用户提供的 USD，而无需重新运行转换。

在任何转换器、验证、内容代理、OVRTX、打包或 FET 阶段之前，运行 `preflight`（或验证现有的 `PHYSICAL_AI_PREFLIGHT_MANIFEST`）；将其视为依赖项引导，而不是工作流路由。对于仅转换/仅验证请求，使用 `--skip-content-agents`。

当 `property_assignment_intent=run` 时，在确认源路径并解决意图后，立即验证或部署内容代理服务，在资产上下文检查、转换器依赖项检查、转换、验证、一致性、渲染、打包或上游源构建之前。将明确提供的健康端点视为用户拥有的；否则运行 `deploy-content-agents`，部署独立的 OVRTX 渲染器，然后按顺序部署材料、物理和可选纹理服务容器。

## 操作说明

1. 确认源资产路径存在，解析 `output_root`，并将请求分类为端到端、仅转换、仅验证或打包。
2. 在运行任何资产检查、转换器探测、转换、验证、一致性、渲染或打包步骤之前，解析 `property_assignment_intent`。
3. 为选定的工作流目标运行 `preflight`，除非已经配置了可用的 `PHYSICAL_AI_PREFLIGHT_MANIFEST`。在运行下游脚本之前，加载生成的环境文件。将预检视为依赖项设置：它可能使用提供的 `--source-asset`、`--source-format` 或 `--conversion-tools` 值来限定依赖项检查，但 `convert-to-usd` 和上游转换器参考仍然决定实际转换支持。
4. 当 `property_assignment_intent=run` 时，首先验证或部署内容代理服务；在缺少身份验证或不健康的服务的阻塞情况下继续。
5. 阅读 `references/workflow.md` 和 `references/commands.md`，然后仅运行当前请求所需的阶段参考。
6. 当可以使用网络搜索或将要运行属性分配时，在原始源资产上运行 `identify-asset-context`。
7. 将源通过 `convert-to-usd`，或对于现有的 USD 输入跳过转换，并将源路径视为当前的 USD 路径。
8. 在进行昂贵的下游工作之前运行 `validate-usd-minimum`。将其视为可行性门控：记录单元/配置问题，例如 `metersPerUnit != 1.0`，但在内容代理分配之前不运行 `simready-conform-profile`、FET001 或任何其他 FET 修复。
9. 在请求或需要时，在转换/最小有效的 USD 上运行内容代理材料、物理和可选纹理分配。
10. 在属性分配后，在最新的模拟 USD 路径上运行 `simready-conform-profile` 并保留所有选定的 FET 修复报告。
11. 按顺序运行验证门控：`omni-asset-validate`、`omni-asset-validate-geometry`、`omni-asset-validate-physics` 和 `simready-validate`。
12. 当 `simready-validate` 报告可修复的要求时，重新运行 `simready-conform-profile`，然后在最新创作的 USD 上重新运行配置验证。
13. 当请求预览、缩略图或检查图像时，运行 `ovrtx-render-service`。当请求包输出时，在最终 USD 和缩略图旁边运行 `assemble-package-source` 以创建干净的 `deliverable/` 包源，然后在该 deliverable 文件夹上运行 `nv-core-package-sample` 和 `nv-core-package-sample-validation`。
14. 使用最终 USD 路径、所有阶段报告、验证结果、重新运行原因和下一步工作，发出整合的工作流报告。

## 输出格式

以 Markdown 格式发出整合的工作流报告，并在工作流写入结构化工件时包含 JSON。报告整体状态为 `passed`、`blocked`、`failed` 或 `needs_rerun`。请参阅 `references/workflow.md` 以获取所需的 Markdown 和 JSON 报告字段。

## 详细参考

仅阅读当前请求所需的参考：

- `references/preflight/README.md`：确定性本地设置、元数据/环境合同、包装器、部署禁用和护栏行为。
- `references/workflow.md`：输入、源路由、详细工作流、验证策略、输出报告字段和下一步。
- `references/commands.md`：具体的可移植脚本命令模式。
- `references/assemble-package-source/README.md`：两区包源组装、根 USD 命名、缩略图放置和 deliverable 检查。
- `references/troubleshooting.md`：症状/原因/修复表以及 FET (`GSP.001`/`RB.MB.001`) 修复路由细节。
- `references/publishing-layout.md`：此技能自己的文件树的前置字段注释和布局原因。

## 发布布局说明

使用 `skills/omniverse-cad-to-simready/` 作为此产品代码库技能的权威来源。`.agents/skills` 符号链接是用于本地 agentskills.io 风格发现的兼容性别名，嵌套的 `references/` 树是故意的。请参阅 `references/publishing-layout.md` 以获取别名列表、前置字段位置和平坦化规则。

## 限制

- 此工作流协调现有的转换、属性分配、一致性、验证、渲染和打包技能；它不会用单个整体的运行器命令来替代它们。

## 故障排除

仅在特定阶段或验证门控失败时，阅读 `references/troubleshooting.md`；它拥有症状/原因/修复表和 FET 修复路由。

## 严格规则

- 优先使用预检元数据文件进行本地上游根、转换器可执行文件、SimReady 验证运行时、OVRTX 端点和内容代理服务 URL。当 `PHYSICAL_AI_REQUIRE_PREFLIGHT=1` 被设置时，不要通过直接上游发现绕过元数据文件。
- 在内容代理准备就绪之前，不要运行资产检查、转换器探测、本地上游构建、转换、验证、一致性、渲染或打包。
- 直接使用特定阶段的已安装参考脚本。不要添加或调用单个 `omniverse-cad-to-simready` 运行器命令。
- 对于源转换，委托给 `convert-to-usd` 参考项；不要用其他转换器替代 CAD 或网格格式。
- 对于属性分配，使用内容代理参考作为单独的原子步骤：首先材料，然后物理，然后在请求时才纹理。
- 当属性分配将运行时，不要在内容代理之前运行 `simready-conform-profile` 或任何 FET 辅助工具。首先验证最小 USD，然后在转换/最小有效的 USD 上运行内容代理，然后对最新服务编写的 USD 应用 FET 修复。
- 当属性分配将运行时，不要在内容代理之前运行 `simready-validate` 或任何 SimReady 配置验证。允许在服务调用之前进行的唯一验证门控是 `validate-usd-minimum`，它是一个基本的 USD 可行性检查。
- 在第一个失败的部署、转换、属性分配或一致性创作门控处停止，除非用户明确要求尽力继续。
- 在存在有意义的 USD 工件后，不要在验证结果后停止。继续剩余的诊断门控并标记结果为 `needs_rerun`。
- 不要将 `GSP.001` 配置失败作为未分类的最终发现。将其路由到上游 `simready-foundation-conform-fet-005-simulate-grasp-physics`；如果当前代理无法检查渲染或没有明确的抓取点，报告一个受阻的 FET005 修复，并提供视觉证据路径或缺少输入的原因。
- 保留每个阶段报告，并将每个报告中的具体输出 USD 路径传递到下一个阶段。
