## 目的

操作 VSS 警报管道（模式检测、Alert-Bridge 订阅、Slack 通知、查询、相机上载、verifier-prompt 定制）。

## 前置条件

- 可达 `$HOST_IP` 上的活动 VSS 部署（参见 `vss-deploy-profile` 和 `references/`）。
- 任何图像拉取都需要 `$NGC_CLI_API_KEY` 和 `$NVIDIA_API_KEY` 中的 NGC 凭证。
- 调用者上可用 `curl`、`jq` 和 Docker。

## 说明

遵循下方的路由表和分步工作流程。以 *workflow*、*quick start* 或 *flow* 结尾的每个部分都旨在自上而下执行。详细参考材料位于 `references/`，辅助脚本位于 `scripts/` — 当技能指向一个脚本时，通过 `run_script` 调用它们。

## 示例

可运行的端到端场景位于 `evals/` 下（每个 `*.json` 清单）；每个工作流程下方都有内联 `curl` 块。使用 `nv-base validate <this-skill-dir> --agent-eval` 进行回放。

## 限制

需要部署且可到达的匹配 VSS 配置文件/微服务。NGC 托管的模型/NIM 受速率限制、GPU 内存需求和许可条款约束；并发性和存储限制取决于主机硬件和配置文件的 compose 文件。

## 故障排除

- **连接拒绝** → 微服务未运行：探测 `/docs` 或 `/health`，通过 `vss-deploy-profile` 重新部署。
- **NGC 拉取时出现 HTTP 401/403** → 缺失/过期 `NGC_CLI_API_KEY`：`docker login nvcr.io` 并重新导出密钥。
- **OOM / 模型加载失败** → GPU 内存不足：使用较小变体或 `docker compose down` 释放 GPU。

# VSS 警报管理

警报配置文件以两种模式之一运行（在 `/vss-deploy-profile -p alerts -m {verification,real-time}` 处选择）—— 详见下方的 **两种模式** 表格。此技能根据 **部署模式 + 用户意图**（监控 vs 订阅 CRUD vs Slack webhook）进行路由。

## 何时使用

- 在传感器上开始/停止实时警报（“为仓库样本上的箱子开始实时警报”）
- 在 Alert Bridge 上创建/列出/停止实时订阅规则
- 设置或管理 Slack 事件通知
- 列出或查询检测到的 incidents / 警报；检查裁决（确认/拒绝/未核实）
- 将新相机添加到警报管道；定制 VLM-verifier 提示（CV 模式）

---

## 部署前置条件

需要在 `$HOST_IP` 上的 VSS **alerts** 配置文件以 `verification`（CV）或 `real-time`（VLM）模式运行。

```bash
# 必须存在 vss-rtvi-cv (CV 模式) 或 vss-rtvi-vlm (VLM 模式) 之一。
curl -sf --max-time 5 "http://${HOST_IP}:8000/docs" >/dev/null \
  && docker ps --format '{{.Names}}' \
     | grep -qE '^(vss-rtvi-cv|vss-rtvi-vlm)$'
```

如果探测失败，询问要部署哪种模式并转交给 `/vss-deploy-profile -p alerts -m <mode>`（拒绝 → 停止；预授权自主部署 → 默认以 `verification` 直接运行）。如果通过，根据步骤 1 检测模式。

---

## 两种模式（部署时选择）

| 模式 | 部署标志 | 环境 (`.env`) | 运行内容 | 可用内容 |
|---|---|---|---|---|
| **CV (verification)** | `-m verification` | `MODE=2d_cv` | RT-CV (Grounding DINO) + 行为分析 + `alert-bridge` VLM verifier + **`rtvi-vlm`** | **同时**静态 CV 管道（工作流程 A）**和**动态 VLM 实时警报（工作流程 B/D） |
| **VLM (real-time)** | `-m real-time` | `MODE=2d_vlm` | `alert-bridge` + `rtvi-vlm` | **仅**动态 VLM 实时警报（工作流程 B/D）和 `alert-bridge` 后端。没有静态 CV 管道。 |

**切换模式** 使用 `vss-deploy-profile` 拆卸 + 部署流程，并使用另一个 `-m` 标志（VLM → CV 添加 CV 管道；CV → VLM 拆卸它）。`rtvi-vlm` 在两种模式下都运行。

---

## 步骤 1 — 检测当前部署的模式

在运行任何警报工作流程之前，检查哪个模式是活动的。使用 **仅 CV** 容器作为信号 — `vss-rtvi-vlm` **不是** 可靠的模式信号，因为它在两种模式下都运行。

```bash
# CV 验证模式（vss-behavior-analytics + vss-rtvi-cv 仅 CV）
docker ps --format '{{.Names}}' | grep -qx vss-behavior-analytics && echo "mode=CV"

# VLM 实时模式（没有 CV 管道；vss-rtvi-vlm 仍然运行）
docker ps --format '{{.Names}}' | grep -qx vss-behavior-analytics || \
  docker ps --format '{{.Names}}' | grep -qx vss-rtvi-vlm && echo "mode=VLM"
```

如果 `vss-behavior-analytics` 存在 → **CV 模式**（它也包含 `vss-rtvi-vlm`）。
如果仅存在 `vss-rtvi-vlm`（并且没有 CV 管道）→ **VLM 模式**。
如果都不匹配，则警报配置文件未部署 — 指导用户使用 `vss-deploy-profile` 技能。

替代信号（当无法访问 `docker ps` 时优先使用）：检查配置文件的 `generated.env`：

```bash
grep -E '^MODE=' deploy/docker/developer-profiles/dev-profile-alerts/generated.env
# MODE=2d_cv   → CV 模式（完整超集）
# MODE=2d_vlm  → VLM 实时模式（仅 vss-rtvi-vlm；没有 vss-rtvi-cv）
```

如果探测失败，询问要部署哪种模式并转交给 `/vss-deploy-profile -p alerts -m <mode>`（拒绝 → 停止；预授权自主部署 → 默认以 `verification` 直接运行）。如果通过，根据步骤 1 检测模式。

---

## 步骤 2 — 根据部署模式进行路由

| 部署模式 | 用户询问关于… | 操作 |
|---|---|---|
| **VLM 实时** | Slack webhook 设置/状态/测试/停止 | **工作流程 E** — `references/alert-notify.md` |
| **VLM 实时** | 规则 CRUD，或传感器上的实时警报具有检测条件，或停止/删除命名警报（通过 `alert_type`/条件或规则 ID） | **工作流程 D** — `references/alert-subscriptions.md`（包括两步停止/确认） |
| **CV 验证** | 订阅/规则 CRUD 或 Slack/通知设置 | 拒绝 — 详见下文的标准拒绝文本 |
| **CV 或 VLM** | 无检测条件的通用开始/停止监控 | **工作流程 B (VLM)** — 调用 VSS Agent；`rtvi-vlm` 在两种模式下都运行 |
| **CV 或 VLM** | 事件查询 / *发生了什么*（最近的警报、时间范围、非正式的“今天有警报吗？”） | **工作流程 C (查询)** — 适用于两种模式；**始终运行查询，切勿从内存中回答** |
| **CV** | 静态 CV 警报上载 / 裁决提示定制 | **工作流程 A (CV)** — 通过 `vss-manage-video-io-storage` 上载 RTSP；管道自动获取 |
| **VLM** | 需要静态 CV 管道的 CV/行为分析/PPE 规则警报 | **需要重新部署** — 首先确认，然后 `vss-deploy-profile -m verification` |

**始终在触发重新部署之前确认。** 模式切换会停止所有当前运行的监控并重新启动服务。

### 意图优先级（第一个匹配者胜出）

1. **工作流程 E (Slack)** — Slack 特定关键词（`slack`、`webhook` + `slack`、`bot token`、`slack channel`）。`notify` 单独**不**够。
2. **工作流程 D (订阅)** — 传感器**加上**检测条件，规则 CRUD 关键词（`rule`、`subscription`、规则 ID），**或停止/删除命名警报**（“停止 PPE 警报”、“删除碰撞规则”）。命名的 `alert_type`/条件 = 一个现有的**规则** → D 的两步停止协议（`GET /api/v1/realtime` → 是/否确认 → 删除），永远不会工作流程 B。
3. **工作流程 B (VLM 监控)** — 传感器上的通用开始/停止，**没有**检测条件和**没有**警报类型限定符（“为传感器 X 开始/停止实时警报”）。命名类型（“停止 **PPE** 警报”）是规则停止 → 工作流程 D。
4. **工作流程 C (查询)** — 事件查询 / *发生了什么*（`show/list incidents`、`recent alerts`、时间范围查询、**以及非正式的“今天有警报…？” / “今天有警报吗？” / “什么被触发？”短语**）。裸 `alerts` 问题始终是事件查询（工作流程 C），**不是**订阅规则列表（工作流程 D）。
5. **工作流程 A (CV)** — CV 部署处理任何未匹配的内容。

> **`alerts` vs `alert rules` (C vs D) — 恰好选择一个，切勿同时选择：**
> *发生了什么 / 被触发*（事件）→ **工作流程 C**
> (`POST /generate`)。*规则/订阅配置或活动* → **工作流程 D**（裸的
> `GET /api/v1/realtime`，没有 `/incidents`）。裸 `alerts` = 事件 (C)；`alert rules`
> / `subscriptions` / `active rules` = 清单 (D)。切勿从内存中回答；运行正确的调用 — 工作流程 C 下的完整端点详情。

**消除歧义 (B vs D):** 如果传感器使用开始/监控语言命名，但检测条件不明确，询问：
> *"您是想让我 (a) 在 Alert Bridge 上创建一个持续运行的警报规则，直到您删除它，还是 (b) 通过 VSS Agent 开始一次监控会话？"*

**停止路由 (B vs D):** "停止 **&lt;类型&gt;** 警报"（命名一个 `alert_type`/条件，如 PPE、碰撞、火灾）= 停止一个**订阅规则** → **工作流程 D**（通过 `GET /api/v1/realtime` 找到，然后在 `references/alert-subscriptions.md` 中执行 `POST /generate` 的两步停止/确认协议；**不要**调用 `POST /generate`)。一个裸的“停止实时警报 / 停止传感器监控”**没有**类型限定符 = 工作流程 B。

如果提示混合了工作流程（“开始监控并发送到 Slack”），问一个澄清问题以分离执行顺序。

### CV 模式拒绝文本（针对 D 和 E 意图）

当部署模式是 CV 验证，并且用户询问警报订阅或 Slack/通知意图时，使用以下文本原封不动地拒绝：

> "警报订阅和 Slack 通知仅在 VLM 实时模式下受支持。您的当前部署是 `<CV 验证 | 未部署>`。要使用这些功能，请使用 `/vss-deploy-profile -p alerts -m real-time` 重新部署（注意：切换会删除当前的 CV 监控）。"

不自动重新部署。用户决定是否切换模式。

---

## 两种模式的前置条件：传感器必须在 VIOS 中

两种模式都需要相机首先在 VIOS 中注册（通过 `vss-manage-video-io-storage` 技能）：

- RTSP URL / IP 相机 → 使用 `POST /sensor/add`（该技能的 6 节）添加它；记录 `sensorId` / 名称。
- 命名现有传感器 → 在继续之前确认它出现在 `GET /sensor/list` 中。

在 **CV** 中，添加 RTSP 是*整个*上载步骤（管道自动获取）。在 **VLM** 中，它是工作流程 B 的先决条件。

---

## Agent `/generate` 端点

所有 VLM 流程操作和所有查询操作都通过 VSS Agent 的自然语言端点：

```bash
AGENT="http://<AGENT_ENDPOINT>"   # 默认为警报配置文件上的 http://localhost:8000
curl -s -X POST "$AGENT/generate" \
  -H "Content-Type: application/json" \
  -d '{"input_message": "<自然语言请求>"}' | jq .
```

**端点解析：** 使用活动 VSS 部署上下文中的 agent 端点。如果不可用，询问用户。不要通过文件系统发现。

**可用性检查：** `curl -sf --connect-timeout 5 "$AGENT/docs"`。

不要直接调用 `rtvi-vlm` 微服务端点 — 始终通过 agent 调用。agent 内部将调度到 `rtvi_vlm_alert`、`rtvi_prompt_gen` 和 `video_analytics_mcp.get_incidents`。

---

## 工作流程 A — CV 模式 (`-m verification` / `MODE=2d_cv`)

CV 警报是**部署驱动的，不是请求驱动的** — 没有调用 agent 来“创建”一个。

1. 通过 `vss-manage-video-io-storage` 的 `GET /sensor/list` 检查传感器是否在 VIOS 中（幂等性 — 不要盲目 `POST /sensor/add`）。
2. 如果缺失，通过该技能的 `POST /sensor/add` 上载。CV 管道在注册并在线后自动获取流。
3. 确认在线：`curl -s "http://<VST_ENDPOINT>/vst/api/v1/sensor/<sensorId>/status" | jq .`
4. 警报会落入 Elasticsearch（行为分析 → `alert-bridge` 按照每个 `alert_type_config.json` 的验证）。使用 **工作流程 C** 查询。

在 VLM 仅部署上使用静态 CV 管道警报是一个模式不匹配 — 详见上方的路由表。

---

## 工作流程 B — VLM 实时监控（CV 或 VLM 模式）

通过 VSS Agent 为没有检测条件的命名传感器进行通用开始/停止意图（如果存在条件，则路由到工作流程 D）。`rtvi-vlm` 在两种模式下都运行。

```bash
# start: input_message = "Start real-time alert for sensor <id>"
# stop:  input_message = "Stop real-time alert for sensor <id>"
curl -s -X POST "$AGENT/generate" -H "Content-Type: application/json" \
  -d '{"input_message": "<start|stop> real-time alert for sensor <id>"}' | jq .
```

底层：`rtvi_prompt_gen` → `rtvi_vlm_alert action="start"`。
每个块都被加上了字幕；如果 VLM 响应包含 `yes`/`true`（不区分大小写），则将事件发布到 `mdx-vlm-incidents`。提示必须强制 Yes/No 答案。在 VLM 仅部署上使用静态 CV 管道请求是一个模式不匹配 — 详见路由表。

---

## 工作流程 D — 警报订阅（仅 VLM 实时模式）

在 Alert Bridge 上创建/列出/删除持久实时警报规则。
当提示包含规则关键词（`rule`、`subscription`、规则 ID）**或**将特定传感器与特定检测条件配对时（例如，“在仓库码头-1 上设置实时警报以检测 PPE 违规”、“监控 entrance-1 上的尾随行为”、“停止规则 496aebd1-…”）路由到这里。

**不在此处：** 无条件的开始/停止（→ 工作流程 B）或 Slack 操作（→ 工作流程 E）。

加载并遵循 `references/alert-subscriptions.md` 作为订阅 CRUD 的权威剧本。仅 VLM 实时模式；使用标准拒绝文本来拒绝 CV。

---

## 工作流程 E — Slack 通知（仅 VLM 实时模式）

当用户**明确提到 Slack 或 webhook 中继**（开始/停止 webhook 服务器、检查状态/健康、发送测试消息、设置 Slack channel/token）时使用。`notify` 单独**不**够。

> **`alert-notify` (端口 9090) ≠ `vss-alert-bridge` (`/api/v1/realtime`)。**
> 不要触碰 `vss-alert-bridge` 进行 Slack 操作。

路由到这里："设置 Slack 通知"、"检查 alert-notify 是否正在运行"、"向 Slack 发送测试警报"。不路由到这里："有人进入区域时通知我"（→ D/B）、"在我的手机上警报和通知"（模糊不清 — 询问）。

加载并遵循 `references/alert-notify.md`。代码位于 `scripts/alert-notify/`。仅 VLM 实时模式。

---

## 工作流程 C — 查询/列出警报（适用于两种模式）

CV 和 VLM 生成的警报都落入 Elasticsearch，可通过 agent 的 `video_analytics_mcp.get_incidents` 工具查询。向 `$AGENT/generate` 发送自然语言请求 — "显示传感器 X 的最近警报"、"列出过去一小时的确认警报"、"显示 Camera_02 在 `<ISO>` 和 `<ISO>` 之间的碰撞事件"。

**非正式短语也路由到这里。** 像这样的问题 "今天有警报吗？"、"今天有警报吗？"、"什么被触发？" 或 "最近检测到什么？" 都是事件查询 — 发出 `POST /generate`（例如 `{"input_message": "List alerts from today"}`）并总结结果。**切勿从内存中回答**，也**不要**在没有运行查询的情况下回复 "没有警报"。一个裸的 "alerts" 问题始终是事件查询（工作流程 C），**不是**订阅规则列表（工作流程 D）。

> **不要为事件查询列出订阅规则。** 裸的 `GET /api/v1/realtime`（没有 `/incidents`）列出 *规则*（工作流程 D），并且对于 "发生了什么" 是错误的 — 不要调用/探测它或加载工作流程 D 剧本。

**空结果是有效答案。** 如果没有匹配的事件（例如，一个新部署的系统还没有活动），请报告请求的期间**没有找到 / 计数是 0** 并停止 — 不要回退到列出规则或寻找其他端点。

对于更丰富/非自然语言的过滤（传感器级、时间序列、计数）使用 **`vss-query-analytics` 技能**（VA-MCP 在端口 9901 上）。

### 裁决解释 & CV verifier 提示（仅 CV 模式）

CV 警报带有 VLM 验证裁决（确认 / 拒绝 / 未核实）；VLM 实时事件没有单独的裁决（触发本身就是 Yes/No VLM 答案）。CV 路径 verifier 提示可通过 `alert_type_config.json` 定制（重新启动 `alert-bridge` 以应用）。有关裁决表、字段含义和提示定制规则的详细信息，请参阅 `references/cv-verifier-prompts.md`。

---

## 跨技能链接

| 任务 | 技能 |
|---|---|
| 部署、重新部署或切换警报模式 | **`vss-deploy-profile`** — `-p alerts -m {verification,real-time}` |
| 添加 RTSP/IP 相机、列出传感器、快照、片段 | **`vss-manage-video-io-storage`**（添加传感器的 6 节） |
| 从 Elasticsearch 获取时间范围事件 / 占用率 / PPE 指标 | **`vss-query-analytics`** (VA-MCP :9901) |
| 从警报获取详细事件报告 | **`vss-generate-video-report`** |
| 订阅 / Slack 子工作流程 | `references/alert-subscriptions.md`, `references/alert-notify.md` (代码在 `scripts/alert-notify/`) |

---

## 注意事项

- **`alert-notify` (端口 9090) ≠ `vss-alert-bridge`。** Slack 操作 → 工作流程 E (`alert-notify`)；切勿将 Slack 路由到 `vss-alert-bridge` 的 `/api/v1/realtime`。
- **工作流程范围按模式：** A 仅 CV；B 和 C 适用于两种模式；D 和 E 仅 VLM 实时（在 CV 上使用标准文本拒绝）。
- **不要使用 `vss-rtvi-vlm` 作为模式信号** — 它在两种模式下都运行。使用 `vss-behavior-analytics`（仅 CV）或 `MODE` 环境变量。
- **模式切换会删除当前部署** — 运行的 VLM 流和未保存的 CV 警报状态将丢失。
- **始终通过 `$AGENT/generate`** — 不要直接调用 `rtvi-vlm`。VLM 触发是一个 `"yes"`/`"true"` 令牌匹配（不区分大小写）；`rtvi_prompt_gen` 强制 Yes/No 模式，所以不要手工艺提示破坏它。
- **传感器必须已在 VIOS 中**，适用于两种模式（使用 `vss-manage-video-io-storage` 进行 RTSP 输入）。
