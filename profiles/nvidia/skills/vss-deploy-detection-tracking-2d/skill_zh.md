## 目的

部署、调试和操作 RTVI-CV 检测/跟踪 2D 微服务，并驱动其 REST API。

## 前置条件

- 可达 `$HOST_IP` 上的活动 VSS 部署（参见 `vss-deploy-profile` 和 `references/`）。
- 任何图像拉取都需要 `$NGC_CLI_API_KEY` 和 `$NVIDIA_API_KEY` 中的 NGC 凭证。
- 调用者上可用 `curl`、`jq` 和 Docker。

## 说明

遵循下方的路由表和逐步工作流程。以 *workflow*、*quick start* 或 *flow* 结尾的每个部分都旨在自上而下执行。详细参考材料位于 `references/` 中，辅助脚本位于 `scripts/` 中——当技能指向一个脚本时，通过 `run_script` 调用它们。

## 示例

端到端的工作示例保存在 `evals/` 下（每个 `*.json` 清单包含一个可运行的场景），并在下方每个工作流程的 `curl` 块中内联提供。使用 `nv-base validate <this-skill-dir> --agent-eval` 运行 Tier-3 评估以重放它们。

## 限制

- 需要部署匹配的 VSS 配置文件 / 微服务，并且可以从调用者访问。
- NGC 托管的模型和 NIM 可能受速率限制、GPU 内存要求和许可证限制的影响。
- 并发性、GPU 内存和存储限制取决于主机硬件和配置文件的 compose 文件。

## 故障排除

- **错误**：REST 调用返回连接被拒绝。**原因**：目标微服务未运行。**解决方案**：探测 `/docs` 或 `/health`；通过 `vss-deploy-profile` 或匹配的 `vss-deploy-*` 技能重新部署。
- **错误**：从 NGC 拉取返回 HTTP 401/403。**原因**：缺少/过期 `NGC_CLI_API_KEY`。**解决方案**：`docker login nvcr.io` 并在重试之前重新导出密钥。
- **错误**：容器 OOM 或模型加载失败。**原因**：所选配置文件的 GPU 内存不足。**解决方案**：切换到较小的变体或通过 `docker compose down` 释放 GPU。

# RTVI-CV — 检测与跟踪（统一技能）

**实时视频智能 CV (RTVI-CV)** 微服务的统一技能。一个技能中有两个操作界面：

- **本地部署 / 操作 / 调试 / 拆除** RTVI-CV 容器 → 参见 [`references/deploy-vss-detection-tracking-2d.md`](references/deploy-vss-detection-tracking-2d.md)
- **在运行实例上调用 RTVI-CV REST API**（流、健康、指标、嵌入）→ 参见 [`references/usage-vss-detection-tracking-2d.md`](references/usage-vss-detection-tracking-2d.md)

> **服务**：`rtvi-cv` (`metropolis_perception_app`)
> **镜像**：`nvcr.io/<org>/<repo>:<tag>` — 在部署时由用户提供
> **REST 端口**：`9000` (`/api/v1` — `/live`、`/ready`、`/startup`、`/metrics`、`/stream/add`、`/stream/remove`、嵌入）
> **硬件**：x86/aarch64 dGPU（T4、A100、L40、H100、B200、RTX）、SBSA（Spark、Grace-Hopper）、Jetson（Thor、Orin、Xavier）

---

## 动作路由 — 每次调用选择一次

| 用户意图（示例短语） | 流程 | 加载此参考 |
|----------------------|------|-----------|
| `deploy rtvi-cv warehouse 2d`、`run rtvicv warehouse-3d with 4 streams`、`start smartcity gdino`、`launch perception app`、`bring up sparse4d` | **部署** | [`references/deploy-vss-detection-tracking-2d.md`](references/deploy-vss-detection-tracking-2d.md) |
| `stop rtvi-cv`、`tear down`、`kill the perception container`、`cleanup rtvicv-perception-docker` | **拆除**（由部署文档处理 → “模式选择”） | [`references/deploy-vss-detection-tracking-2d.md`](references/deploy-vss-detection-tracking-2d.md) + [`references/teardown-flow.md`](references/teardown-flow.md) |
| `check rtvi-cv logs`、`diagnose rtvi-cv crashing`、`troubleshoot healthcheck failing`、`rtvi-cv won't start` | **调试** | [`references/deploy-vss-detection-tracking-2d.md`](references/deploy-vss-detection-tracking-2d.md) + [`references/troubleshooting.md`](references/troubleshooting.md) |
| `add a stream`、`remove camera`、`list streams`、`health check`、`is rtvi-cv ready`、`get metrics`、`what's the FPS`、`check GPU usage`、`generate text embeddings`、`call rtvi-cv api` | **API 使用** | [`references/usage-vss-detection-tracking-2d.md`](references/usage-vss-detection-tracking-2d.md) + [`references/api-reference.md`](references/api-reference.md) |

**选择规则**：将用户的短语与上表匹配，并立即加载相应的参考文件。不要混合流程——部署假设没有正在运行的容器；API 使用假设容器已经在 `http://<host>:9000` 上运行。

如果意图确实模糊（例如，用户只说“我想使用 rtvi-cv”），请问一个 `AskQuestion`：部署一个新实例，还是调用一个已经运行的实例？

---

## 哪里有什么

```
vss-deploy-detection-tracking-2d/
├── SKILL.md          # 此文件（路由 + 合同）
├── assets/           # 数据文件（deploy-defaults.yml — 标签 / 引用 / 路径 / GPU 的单一来源）
├── evals/            # Tier-3 评估清单（deploy-evals.json、usage-evals.json）
├── scripts/          # 23 个 bash + python 辅助脚本（参见 `scripts/` 获取完整清单）
└── references/       # 工作流程运行手册（部署 / API 使用 / 拆除 / 故障排除 / …）
```

有关每个文件的完整清单以及每个参考涵盖的内容，请参阅
[`references/workflow-reference.md`](references/workflow-reference.md)。

所有脚本都通过 `$SKILL_DIR/scripts/<name>` 从技能根目录调用——部署参考文档中的路径保持原样，并且在代理从技能根目录运行时正确解析。

---

## 可用脚本

辅助脚本位于 `scripts/` 中，并通过名称从技能根目录调用——通过 `run_script("scripts/<name>")` 调用每个脚本，以便代理记录正确的工具调用。

| 脚本 | 目的 | 参数 |
| --- | --- | --- |
| `load_defaults.sh` | 检测平台（x86 dGPU / SBSA / Jetson）并从 `assets/deploy-defaults.yml` 解析 YAML 默认值。 | `--usecase <name>` |
| `fetch_resources.sh` | 下载 + 提取 NGC 资源，扫描布局。 | `--ngc-ref <ref>`（可选） |
| `apply_in_container.sh` | 主机端包装步骤 4（`apply_config.sh` 在运行容器内）。 | `<container_name>` |
| `apply_config.sh` | 容器内路径替换、批处理、汇点、源、引擎缓存。 | `<usecase> <stream_count> <sink_type>` |
| `start_app_in_container.sh` | 主机端包装步骤 5（`run_app_and_wait.sh`）。 | `<container_name>` |
| `run_app_and_wait.sh` | 容器内应用启动 + 就绪 + 指标 + 日志。 | `<config_path>` |
| `add_streams.sh` / `update_stream_sources.sh` | 步骤 6 的 REST 流生命周期。 | `<rtsp_or_file_uri>...` |
| `collect_metrics.sh` | 拉取 `/api/v1/metrics` 快照。 | 无 |
| `discover_streams.sh` | 通过 `/stream/get-stream-info` 枚举活动流。 | 无 |
| `synthesize_docker_run.sh` | 打印平台正确的 `docker run` 行以解析环境。 | 无 |
| `render_box.sh` | 渲染固定宽度的步骤收据。 | `<step_label>` |
| `calibration_manager.py` | 管理校准工件 + 每个用例引擎缓存失效。 | `--usecase <name> --reset` |

有关辅助脚本的完整清单（缓存、GPU 检查、设置）浏览
`scripts/`；每个脚本的 `--help` 描述其参数。

## 如何使用此技能

1. **首先阅读此文件。** 它仅路由——不包含工作流程。
2. **将用户的意图** 与上表中的路由表匹配。
3. **加载一个参考文档**（部署或 API 使用）。不要预加载两者——每个参考都是大型文件，并包含其自己的完整合同。
4. **准确遵循加载的参考。** 参考文档是来自前身技能 `vss-deploy-detection-tracking-2d`（部署/拆除/调试）和 `rtvicv-api`（REST API）的字节级保留合同——每个步骤顺序不变量、bash 批处理规则、框渲染规则和 `AskQuestion` 合同都保留。
5. **对于部署**，参考文档强制执行其自己的启动合同：单行确认 → 规划工具调用（`TodoWrite` 数组 5 个待办事项，或在新 Claude Code 上 5 次连续的 `TaskCreate` 调用）→ 步骤 1 问题。不要叙述，不要预飞行，永远不要打印“加载 TodoWrite/TaskCreate”或任何延迟工具解析的文本——规划工具静默加载。

---

## 输出合同 — 部署流程

在运行部署 / 拆除 / 调试流程时，代理必须对每个成功的部署都尊重以下四项。这是用户在步骤之间的唯一反馈渠道；跳过其中任何一项都是行为退化。

1. **渲染每个步骤的退出为固定宽度的框** — 步骤 1 *部署目标*、步骤 2 *管道配置*、步骤 3 *容器*、步骤 4 *应用配置*、步骤 5 *计划* + *结果*。不仅仅是最终摘要。框是用户的步骤收据。几何形状是固定的（见下文“通用框格式”）。每步的 **内容** 规则（每个框内哪些行）位于 [`references/deploy-vss-detection-tracking-2d.md`](references/deploy-vss-detection-tracking-2d.md) 下“步骤 N 框内容规则”。
2. **在步骤 5 结果框之后，从 [`references/next-steps.md`](references/next-steps.md) § "11.c" 发行步骤 6 `AskUserQuestion` — 永远不要用自由形式的 *下一步* 项目符号列表替换它。菜单是部署的退出处理程序：它允许用户通过单击运行指标、管理流、尾随日志或拆除，而不是记住 curl URL。
3. **在用户选择步骤 6 桶之后，发行后续 `AskUserQuestion`** 从 [`references/next-steps.md`](references/next-steps.md) § "11.d" — 永远不要用散文 + 准备好的 curl 示例 + 自由文本“我想运行 X？”问题来替代。每个桶都有自己的具体操作菜单；用户选择操作，然后技能发出 API 框并运行 curl。每个桶的后续：
   - **管理流** → 添加 / 删除 / 列出。**删除动态构建其选项** 从 `/stream/get-stream-info` — 每个活动流一个选项，标记为 `<camera_id> · <camera_url>`，并且在 `ACTIVE > 1` 时“删除所有”（完整规范：§ “`remove_streams` 子流程”）。
   - **停止部署** → 停止应用 / 停止容器 / 完全拆除。
   - **检查指标 & FPS** → 无后续；直接在打印 `/api/v1/metrics` API 框后运行 `collect_metrics.sh`。
   - **检查活动性 / 就绪** → 无后续；在打印它们的 API 框后探测所有三个健康端点。
4. **渲染完整的每步内容，而不是概览行** — 渲染框是必要的，但不是充分的。每个步骤都有一个行组成规范在
   [`references/deploy-vss-detection-tracking-2d.md`](references/deploy-vss-detection-tracking-2d.md)
   下“步骤 N 框内容规则”。**步骤 4（应用配置）是代理最常折叠的地方** — 其规范每个用例键列表位于
   [`references/apply-config.md`](references/apply-config.md)
   § “每个用例完整编辑列表”，代理必须为活动用例 + 设置发出一个 `✔ [section] key=value` 行表中的每个键。5 个键的章节 → 5 行；6 个键的章节 → 6 行。永远不要一个概览行每节。

禁止（这些是代理在压力下回退的快捷方式，并且它们破坏了用户的 UX）：

- ❌ **内部工具加载叙述。** 永远不要打印“我需要加载 TodoWrite（技能调用的延迟工具用于任务小部件）”、“加载 TaskCreate…”、“调用 ToolSearch for the planning tool…” 或任何关于解析/加载/获取延迟工具的文本。代理静默加载工具。用户永远只看到 `✔ <pinned-values>` 摘要行，然后是小部件——永远不会有任何工具解析的框架。
- ❌ **将所有 5 个部署步骤折叠成一个 `TaskCreate` 的 `description` 字段。** 当 `TaskCreate` 是可用的规划工具时，连续发出 **5 个 `TaskCreate` 调用**（每个步骤一个）。参见 `references/task-list.md` § "Initial `TaskCreate` calls" 获取字面模板。对于 `TodoWrite` — 一个调用，`todos:[…]` 数组中包含所有 5 个待办事项；永远不要一个待办事项，其 `content` 是多行列表。
- ❌ **静默选择 `dynamic` 流模式。** 技能默认是 `stream_mode=static` — 代理在应用启动之前将自动发现的 `file://` URL 烘焙到 DS 主配置的 `[source-list]` 块中。仅在用户明确要求（“通过 REST 添加流”、“使用动态流模式”）或当他们选择 Step 2 中的 `dynamic` 时切换到 `dynamic`。对于通用“部署 rtvi-cv with N streams”查询选择 `dynamic` 会破坏部署规范和用户的 `/metrics` 期望。参见
  [`references/pipeline-config.md`](references/pipeline-config.md)
  § “默认值 — 技能默认为静态模式” 获取完整理由。
- ❌ 一行 `✔ App ready in Ns, N streams, fps total Y` 代替步骤 5 结果框。
- ❌ ASCII 框绘制字符（`+`、`-`、`=`、`*`）而不是轻量级框绘制字符（`┌`、`─`、`┐`、`│`、`└`、`┘`）。
- ❌ 跳过步骤 6，假设“用户知道下一步该做什么”。
- ❌ 在步骤 6 之后，倾倒一堵 markdown 墙上的散文 + 多个 curl 块 + 一个关闭的“我想运行这些中的任何一个吗？”——那是代理回退的形状，它绕过了 11.d 菜单和每个 API 调用框。用户从菜单中选择；技能显示解析的 API 框；技能运行它。没有自由文本问题。
- ❌ 步骤 4 概览折叠——这些被部署文档的步骤 4 内容规则明确禁止：
    - `✔ Batch size 3 (tile grid: 1×3)` → 需要：5 个单独的行
      (`[streammux] batch-size=3`，`[primary-gie] batch-size=3`，
      `[source-list] max-batch-size=3`，`[tiled-display] rows=1`，
      `[tiled-display] columns=3`)。
    - `✔ Output sink eglsink` → 需要：每个汇点键一行
      (4 个键对于 eglsink，例如 `[sink0] enable=1`，`type=2`，
      `sync=0`，`qos=0` — 参考 apply-config.md 获取确切列表)。
    - `✔ Sources static (3 streams, http-port=9000)` → 需要：六个带注释的 `[source-list]` 行。
    - `✔ Tile grid 1 row × 3 cols`（单行）→ 需要：两行，`[tiled-display] rows=1` 和 `[tiled-display] columns=3`。

## 通用框格式

每个步骤退出框（步骤 1 到步骤 5 结果）的几何合同。每个框的形状都相同；只有 **标题** 和 **正文行** 每步更改。

- **宽度：128 个字符** 角到角 — `┌` 在列 1，`┐` 在列 128。更宽的终端将框左对齐；不要拉伸它。内部内容区域是 **124 个字符**（在 `│` 边框内部每侧有一个空格边距）。
- **仅使用轻量级框绘制字符**：`┌` `─` `┐` `│` `└` `┘`。没有 `+`、`-`、`=`、`*` ASCII 替代。
- **顶部边框 — 标题居中**：`┌` + N₁ 横线 + `␣` + 标题 + `␣` + N₂ 横线 + `┐`，其中 `N₁ + N₂ + len(title) + 2 = 126`。分配填充：`N₁ = floor((126 − len(title) − 2) / 2)`，
  `N₂ = 126 − len(title) − 2 − N₁`。N₁ 和 N₂ 的差值最多为 1。
- **正文**：每个事实行使用 `│ <内容填充到内部内容 124> │`。每行事实使用 `  ✔ <键填充到 13>  <值>` 形式（缩进两个空格，符号，键右填充到 13，两个空格，值）。
- **组之间空行**：在逻辑组之间（例如步骤 1 中的身份 / 模型 / 视频）渲染 `│ <124 个空格> │`，以便用户可以一目了然地扫描框。
- **底部边框**：`└` + 126 横线 + `┘` — 实线边框，无标题。

标准步骤标题（用于每个步骤框的顶部）：

```
┌─────────────────────────────────────────────────────── Deploy targets ───────────────────────────────────────────────────────┐
┌─────────────────────────────────────────────────── Pipeline configuration ───────────────────────────────────────────────────┐
┌───────────────────────────────────────────────────────── Container ──────────────────────────────────────────────────────────┐
┌──────────────────────────────────────────────────── Apply configuration ─────────────────────────────────────────────────────┐
┌──────────────────────────────────────────────── Perception Application — Plan ───────────────────────────────────────────────┐
┌────────────────────────────────────────────── Perception Application — Results ──────────────────────────────────────────────┐
```

每步内容规则（哪些行放入哪个框，模式感知行隐藏，apply-config 分节布局，步骤 5 PLAN-then-RESULT 模式，步骤 3 `docker run` 合成要求）位于
[`references/deploy-vss-detection-tracking-2d.md`](references/deploy-vss-detection-tracking-2d.md)
下“步骤 N 框内容规则” — 渲染相应步骤时阅读那些。

## 快速触发（助记符）

| 短语 | 流程 |
|------|------|
| `deploy rtvicv warehouse 2d with 4 streams and display` | 部署 |
| `run smartcity gdino on gpu 1` | 部署 |
| `stop the perception container` | 拆除（部署文档） |
| `rtvi-cv healthcheck failing` | 调试（部署文档 + 故障排除） |
| `add a stream to rtvi-cv` | API 使用 |
| `is rtvi-cv ready on localhost:9000` | API 使用 |
| `get rtvi-cv metrics` | API 使用 |
| `generate text embeddings via rtvi-cv` | API 使用 |
