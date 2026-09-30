---
name: vss-deploy-detection-tracking-2d
description: 当用户想要部署、运行、调试、拆除或调用RTVI-CV 2D检测/跟踪微服务的REST API时，请使用此技能。当用户说出类似“部署rtvi-cv”、“启动仓库2D”、“添加一个流”、“检查rtvi-cv健康”或“停止感知容器”等语句时触发。不适用于VLM、嵌入或分析——请使用匹配的vss-*技能。
---

## 目的

部署、调试和运维 RTVI-CV 检测 / 跟踪 2D 微服务，并驱动其 REST API。

## 先决条件

- 在 `$HOST_IP` 上可访问的处于活动状态的 VSS 部署（参见 `vss-deploy-profile` 和 `references/`）。
- 用于任何镜像拉取，需要在 `$NGC_CLI_API_KEY` 和 `$NVIDIA_API_KEY` 中配置 NGC 凭据。
- 调用方上需有可用的 `curl`、`jq` 和 Docker。

## 说明

遵循以下路由表及逐步工作流程。每个以 *workflow*（工作流程）、*quick start*（快速开始）或 *flow*（流程）结尾的章节都旨在从上到下执行。详细的参考材料位于 `references/`，辅助脚本位于 `scripts/` — 当技能通过名称指向脚本时，通过 `run_script` 调用它们。

## 示例

完整的端到端示例保存在 `evals/` 目录下（每个 `*.json` 清单包含一个可运行的场景）以及下方每个工作流程的内联 `curl` 代码块中。使用 `nv-base validate <this-skill-dir> --agent-eval` 运行 Tier-3 评估以重放它们。

## 限制

- 需要匹配对应的 VSS 配置文件 / 微服务已部署并可通过调用方访问。
- 由 NGC 托管的模型和 NIM 可能受速率限制、GPU 内存要求以及许可证限制的影响。
- 并发、GPU 内存和存储限制取决于主机硬件及配置文件的 compose 文件。

## 故障排查

- **错误**：REST 调用返回连接被拒绝。**原因**：目标微服务未运行。**解决方案**：探测 `/docs` 或 `/health`；通过 `vss-deploy-profile` 或匹配的 `vss-deploy-*` 技能重新部署。
- **错误**：来自 NGC 拉取的 HTTP 401/403。**原因**：缺失/过期的 `NGC_CLI_API_KEY`。**解决方案**：`docker login nvcr.io` 并在重试前重新导出密钥。
- **错误**：容器内存溢出 (OOM) 或模型加载失败。**原因**：所选配置的 GPU 内存不足。**解决方案**：切换到较小的变体或通过 `docker compose down` 释放 GPU。

# RTVI-CV — 检测与跟踪（统一技能）

**实时视频智能 CV (RTVI-CV)** 微服务的统一技能。在一个技能中包含两个操作面：

- **部署 / 运维 / 调试 / 拆除** 本地的 RTVI-CV 容器 → 参见 [`references/deploy-vss-detection-tracking-2d.md`](references/deploy-vss-detection-tracking-2d.md)
- **调用 RTVI-CV REST API**（流、健康检查、指标、嵌入）在运行中的实例上 → 参见 [`references/usage-vss-detection-tracking-2d.md`](references/usage-vss-detection-tracking-2d.md)

> **服务**：`rtvi-cv` (`metropolis_perception_app`)
> **镜像**：`nvcr.io/<org>/<repo>:<tag>` — 由用户在部署时提供
> **REST 端口**：`9000` (`/api/v1` — `/live`, `/ready`, `/startup`, `/metrics`, `/stream/add`, `/stream/remove`, 嵌入)
> **硬件**：x86/aarch64 dGPU (T4, A100, L40, H100, B200, RTX), SBSA (Spark, Grace-Hopper), Jetson (Thor, Orin, Xavier)

---

## 动作路由 — 每次调用选择一次

| 用户意图 (示例措辞) | 流程 | 加载此参考 |
|-------------------------------|------|---------------------|
| `deploy rtvi-cv warehouse 2d`, `run rtvicv warehouse-3d with 4 streams`, `start smartcity gdino`, `launch perception app`, `bring up sparse4d` | **部署** | [`references/deploy-vss-detection-tracking-2d.md`](references/deploy-vss-detection-tracking-2d.md) |
| `stop rtvi-cv`, `tear down`, `kill the perception container`, `cleanup rtvicv-perception-docker` | **拆除** (由部署文档处理 → “模式选择”) | [`references/deploy-vss-detection-tracking-2d.md`](references/deploy-vss-detection-tracking-2d.md) + [`references/teardown-flow.md`](references/teardown-flow.md) |
| `check rtvi-cv logs`, `diagnose rtvi-cv crashing`, `troubleshoot healthcheck failing`, `rtvi-cv won't start` | **调试** | [`references/deploy-vss-detection-tracking-2d.md`](references/deploy-vss-detection-tracking-2d.md) + [`references/troubleshooting.md`](references/troubleshooting.md) |
| `add a stream`, `remove camera`, `list streams`, `health check`, `is rtvi-cv ready`, `get metrics`, `what's the FPS`, `check GPU usage`, `generate text embeddings`, `call rtvi-cv api` | **API 使用** | [`references/usage-vss-detection-tracking-2d.md`](references/usage-vss-detection-tracking-2d.md) + [`references/api-reference.md`](references/api-reference.md) |

**选择规则**：将用户的措辞与上表匹配并立即加载相应的参考文件。不要混合流程 — 部署假设尚未运行容器；API 使用假设容器已在 `http://<host>:9000` 上运行。

如果意图确实存在歧义（例如，用户仅说“我想使用 rtvi-cv”），请提出一个 `AskQuestion`：部署一个新实例，还是调用一个已经运行的实例？

---

## 内容位置

```
vss-deploy-detection-tracking-2d/
├── SKILL.md          # 此文件 (路由 + 契约)
├── assets/           # 数据文件 (deploy-defaults.yml — 标签 / 引用 / 路径 / GPU 的单一事实来源)
├── evals/            # Tier-3 评估清单 (deploy-evals.json, usage-evals.json)
├── scripts/          # 23 个 bash + python 辅助程序 (完整清单见 `scripts/`)
└── references/       # 工作流程运行手册 (部署 / api 使用 / 拆除 / 故障排查 / …)
```

完整的逐文件清单以及每个参考覆盖的内容，请参见
[`references/workflow-reference.md`](references/workflow-reference.md)。

所有脚本均从技能根目录通过 `$SKILL_DIR/scripts/<name>` 调用 — 部署参考文档中的路径逐字保留，当代理从技能根目录运行时能正确解析。

---

## 可用脚本

辅助程序位于 `scripts/` 中，并通过名称从技能根目录调用 —
通过 `run_script("scripts/<name>")` 调用每个脚本，以便代理记录
正确的工具调用。

| 脚本 | 目的 | 参数 |
| --- | --- | --- |
| `load_defaults.sh` | 检测平台 (x86 dGPU / SBSA / Jetson) 并从 `assets/deploy-defaults.yml` 解析 YAML 默认值。 | `--usecase <name>` |
| `fetch_resources.sh` | 下载 + 解压 NGC 资源，扫描布局。 | `--ngc-ref <ref>` (可选) |
| `apply_in_container.sh` | 步骤 4 的主机端包装器（运行中容器内的 `apply_config.sh`）。 | `<container_name>` |
| `apply_config.sh` | 容器内的路径替换、批处理、接收器、源、引擎缓存。 | `<usecase> <stream_count> <sink_type>` |
| `start_app_in_container.sh` | 步骤 5 的主机端包装器（`run_app_and_wait.sh`）。 | `<container_name>` |
| `run_app_and_wait.sh` | 容器内应用启动 + 就绪 + 指标 + 日志。 | `<config_path>` |
| `add_streams.sh` / `update_stream_sources.sh` | 步骤 6 的 REST 流生命周期。 | `<rtsp_or_file_uri>...` |
| `collect_metrics.sh` | 拉取 `/api/v1/metrics` 快照。 | 无 |
| `discover_streams.sh` | 通过 `/stream/get-stream-info` 枚举活动流。 | 无 |
| `synthesize_docker_run.sh` | 打印针对解析后环境的平台正确的 `docker run` 行。 | 无 |
| `render_box.sh` | 渲染固定宽度的步骤回执。 | `<step_label>` |
| `calibration_manager.py` | 管理校准工件 + 按用例的引擎缓存失效。 | `--usecase <name> --reset` |

辅助程序的完整清单（缓存、GPU 检查、设置）请浏览
`scripts/`；每个脚本的 `--help` 描述其参数。

## 如何使用此技能

1. **首先阅读此文件。** 它仅进行路由 — 不包含工作流程。
2. **将用户意图** 与上方的路由表匹配。
3. **加载恰好一个参考文档**（部署或 API 使用）。不要预加载两者 — 每个参考文档体积较大并包含其自身完整的契约。
4. **精确遵循加载的参考文档。** 参考文档是从前置技能 `vss-deploy-detection-tracking-2d`（部署/拆除/调试）和 `rtvicv-api`（REST API）逐字保留的契约 — 保留了所有步骤顺序不变量、bash 批处理规则、盒子渲染规则和 `AskQuestion` 契约。
5. **对于部署**，参考文档强制执行其自身的启动契约：一行确认 → 规划工具调用（`TodoWrite` 的 5 个待办事项数组，或在新版 Claude Code 上连续的 5 个 `TaskCreate` 调用）→ 步骤 1 问题。不要叙述，不要预飞行，切勿打印“正在加载 TodoWrite/TaskCreate”或任何关于延迟工具解析的散文 — 规划工具是静默加载的。

---

## 输出契约 — 部署流程

在运行部署 / 拆除 / 调试流程时，代理必须在每次成功部署时遵守
以下四项。这些是用户在步骤之间的唯一反馈渠道；跳过其中任何一项都是
行为回归。

1. **在固定宽度盒子中渲染每个步骤的退出** — 步骤 1 *部署
   目标*，步骤 2 *管道配置*，步骤 3 *容器*，步骤 4
   *应用配置*，步骤 5 *计划* + *结果*。不仅仅是最终
   摘要。盒子是用户的步骤回执。几何形状是固定的（参见
   下方 § “通用盒子格式”）。每个步骤的**内容**规则（每个
   盒子内包含哪些行）位于
   [`references/deploy-vss-detection-tracking-2d.md`](references/deploy-vss-detection-tracking-2d.md)
   的 “Step N box content rule” 下。
2. **在步骤 5 结果盒子之后，发布步骤 6 `AskUserQuestion`**
   来自 [`references/next-steps.md`](references/next-steps.md) § “11.c”
   — 切勿用自由格式的 *后续步骤* 项目符号列表替代。
   菜单是部署的退出句柄：它允许用户一键运行指标、
   管理流、尾部日志或拆除，而无需记住 curl URL。
3. **在用户选择步骤 6 桶之后，发布后续
   `AskUserQuestion`** 来自 [`references/next-steps.md`](references/next-steps.md)
   § “11.d” — 切勿用散文 + 可直接复制的 curl 示例 +
   自由文本“要我做 X 吗？”问题替代。每个桶都有其自己的
   具体操作菜单；用户选择操作，然后技能
   发出 API 盒子并运行 curl。每桶后续操作：
   - **管理流** → 添加 / 移除 / 列出。**移除动态构建其
     选项来自 `/stream/get-stream-info`** — 每个活动流
     一个选项，标记为 `<camera_id> · <camera_url>` 以及
     当 `ACTIVE > 1` 时的“移除所有”（完整规范：§ “`remove_streams`
     子流程”）。
   - **停止部署** → 停止应用 / 停止容器 / 完全拆除。
   - **检查指标 & FPS** → 无后续操作；在打印
     `/api/v1/metrics` API 盒子后直接运行 `collect_metrics.sh`。
   - **检查存活 / 就绪** → 无后续操作；在打印它们的 API 盒子后探测所有三个
     健康端点。
4. **渲染完整的逐步骤内容，而非概览行** —
   渲染盒子是必要但不充分的。每个步骤都有一个行
   组合规范，位于
   [`references/deploy-vss-detection-tracking-2d.md`](references/deploy-vss-detection-tracking-2d.md)
   的 “Step N box content rule” 下。**步骤 4（应用配置）是
   代理最常坍缩的地方** — 其规范的
   按用例关键列表位于
   [`references/apply-config.md`](references/apply-config.md)
   的 § “Per-use-case complete edit list”，代理必须为该
   活动用例 + 设置发出该表中每个关键的一行
   `✔ [section] key=value  — annotation`。一个包含 5 个关键的章节 → 5 行；一个
   包含 6 个关键的章节 → 6 行。切勿每个章节仅一行概览。

禁止事项（这些是代理在压力下退回到捷径，并破坏用户体验）：

- ❌ **内部工具加载叙述。** 切勿打印“我需要加载
  TodoWrite（一个延迟工具，技能为任务部件调用它）”，
  “正在加载 TaskCreate…”，“正在调用 ToolSearch 用于规划工具…”，
  或任何其他关于解析 / 加载 / 获取延迟工具的文本。
  代理静默加载工具。用户永远只看到 `✔
  <pinned-values>` 摘要行，随后是部件 — 永远看不到
  围绕工具解析的脚手架。
- ❌ **将所有 5 个部署步骤坍缩到单个 `TaskCreate` 的
  `description` 字段中。** 当 `TaskCreate` 是可用的规划
  工具时，背靠背发出 **5 个单独的 `TaskCreate` 调用**（每个
  步骤一个）。参见 `references/task-list.md` § “Initial `TaskCreate` calls”
  的逐字模板。对 `TodoWrite` 同理 — 一次调用，在 `todos:[…]` 数组中包含所有 5 个待办事项；
  切勿一个待办事项的 `content` 是多行列表。
- ❌ **静默选择 `dynamic` 流模式。** 技能默认是
  `stream_mode=static` — 代理在应用启动前将自动发现的 `file://` URL
  烘焙到 DS 主配置的 `[source-list]` 块中。
  仅当用户明确要求（“稍后通过 REST 添加流”，“使用动态流模式”）或他们在步骤 2 AskQuestion 中选择 `dynamic` 时
  切换到 `dynamic`。对于通用的“部署
  rtvi-cv 带有 N 个流”查询选择 `dynamic` 会破坏部署评分标准以及
  用户的 `/metrics` 期望。参见
  [`references/pipeline-config.md`](references/pipeline-config.md)
  的 § “Defaults — the skill is static-mode by default” 以获取完整的
  理由。
- ❌ 用一行 `✔ App ready in Ns, N streams, fps total Y` 替代
  步骤 5 结果盒子。
- ❌ 使用 ASCII 框线字符（`+`, `-`, `=`, `*`）而非轻型
  框线字符（`┌ ─ ┐ │ └ ┘`）。
- ❌ 假设“用户知道下一步该做什么”而跳过步骤 6。
- ❌ 在步骤 6 之后，倾倒一堵散文墙 + 多个 curl
  块 + 结尾“要我做其中任何一个吗？” — 这是
  代理退回到形状，它绕过了 11.d 菜单
  和每 API 调用盒子。用户从菜单中选择；技能
  显示解析后的 API 盒子；技能运行它。无自由文本 Q。
- ❌ 步骤 4 概览坍缩 — 这些被部署文档的步骤 4 内容规则明确禁止：
    - `✔ Batch size 3 (tile grid: 1×3)` → 必需：5 个单独的行
      （`[streammux] batch-size=3`，`[primary-gie] batch-size=3`，
      `[source-list] max-batch-size=3`，`[tiled-display] rows=1`，
      `[tiled-display] columns=3`）。
    - `✔ Output sink eglsink` → 必需：每个接收器关键一行
      （eglsink 的 4 个关键，例如 `[sink0] enable=1`，`type=2`，
      `sync=0`，`qos=0` — 阅读 apply-config.md 获取精确列表）。
    - `✔ Sources static (3 streams, http-port=9000)` → 必需：六个
      带注释的 `[source-list]` 行。
    - `✔ Tile grid 1 row × 3 cols`（单行）→ 必需：两个
      行，`[tiled-display] rows=1` 和 `[tiled-display] columns=3`。

## 通用盒子格式

每个步骤退出盒子（从步骤 1 到步骤 5
结果）的几何契约。所有盒子具有相同形状；仅**标题**和
**正文行**随步骤变化。

- **宽度：128 字符** 从角到角 — `┌` 在第 1 列，`┐` 在
  第 128 列。更宽的终端使盒子左对齐；不要拉伸
  它。内部内容区域为 **124 字符**（在 `│` 边界内部每侧有一个空格边距）。
- **仅使用轻型框线字符**：`┌ ─ ┐ │ └ ┘`。无 `+`、`-`、`=`、
  `*` ASCII 回退。
- **顶边框 — 标题居中**：`┌` + N₁ 个破折号 + `␣` + 标题 + `␣`
  + N₂ 个破折号 + `┐`，其中 `N₁ + N₂ + len(title) + 2 = 126`。分配
  填充：`N₁ = floor((126 − len(title) − 2) / 2)`，
  `N₂ = 126 − len(title) − 2 − N₁`。N₁ 和 N₂ 最多相差 1。
- **正文**：每个事实一行 `│ <content padded to inner-content 124> │`。
  每个事实行使用 `  ✔ <key-padded-to-13>  <value>` 形式（两个
  空格进入，字形，关键右填充至 13，两个空格，值）。
- **组之间的空行**：在逻辑组之间渲染 `│ <124 spaces> │`
  （例如步骤 1 中的 Identity / Model / Videos）以便用户
  可一眼扫描盒子。
- **底边框**：`└` + 126 个破折号 + `┘` — 实心边框，无标题。

标准步骤标题（用于每个步骤盒子的顶部）：

```
┌────────────────────────────────────────────────────────────── 部署目标 ───────────────────────────────────────────────────────────────┐
┌─────────────────────────────────────────────────────── 管道配置 ───────────────────────────────────────────────────────────┐
┌───────────────────────────────────────────────────────── 容器 ──────────────────────────────────────────────────────────┐
┌──────────────────────────────────────────────────── 应用配置 ─────────────────────────────────────────────────────────────┐
┌──────────────────────────────────────────────────── 感知应用 — 计划 ───────────────────────────────────────────────────────┐
┌──────────────────────────────────────────────────── 感知应用 — 结果 ──────────────────────────────────────────────────────┐
```

每步内容规则（哪些行进入哪个框、模式感知的行隐藏、应用配置的分段布局、第5步计划-然后-结果的模式、第3步 `docker run` 综合要求）存在于 [`references/deploy-vss-detection-tracking-2d.md`](references/deploy-vss-detection-tracking-2d.md) 下 "第N步框内容规则" — 渲染相应步骤时请阅读这些内容。

## 快速触发（助记符）

| 短语 | 流程 |
|------|------|
| `deploy rtvicv 仓库 2d 使用 4 个流并显示` | DEPLOY |
| `run smartcity gdino 在 gpu 1` | DEPLOY |
| `停止感知容器` | TEARDOWN (部署文档) |
| `rtvi-cv 健康检查失败` | DEBUG (部署文档 + 故障排除) |
| `为 rtvi-cv 添加一个流` | API 使用 |
| `rtvi-cv 在 localhost:9000 上是否就绪` | API 使用 |
| `获取 rtvi-cv 指标` | API 使用 |
| `通过 rtvi-cv 生成文本嵌入` | API 使用 |

bump:1
