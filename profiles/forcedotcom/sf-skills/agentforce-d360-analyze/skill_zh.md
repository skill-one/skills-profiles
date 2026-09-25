# agentforce-d360-analyze — 数据云 360° 会话视图

从数据云 STDM + GenAI DMOs 对单个 Agentforce 会话进行分层会话重建。三个阶段 — 获取 → 组装 → 渲染。典型时间：~10–30秒用于~15轮的会话。

该流程是 **仅数据云 (DC)**：它读取数据云已物化的运行时审计行。它 **不是** 运行时可用性工具 — 下方“数据云盲区”说明了该技能无法回答的问题。

## 如果用户未提供足够信息继续

当使用无会话ID且无发现标准时，打印此块 **原文** — 不要释义，不要预运行任何脚本。触发条件：输入为空 或 不包含会话ID形状（既不是UUID也不是 `0Mw…` 消息ID）且无发现表达式（无时间短语 / `--agent` / `--channel` / `--outcome` / `--grep` / 动词如“查找” / “列出”）。

> 我应该从数据云拉取哪个会话，以及哪个组织？
>
> 我需要：
> - **会话ID** — 无论是 Agent Session UUID (`019db7f6-…`) 还是 MessagingSession ID (`0Mw…`，15/18个字符)。
>   - **无会话ID？** — 告诉我你记得什么，我会找到它：多近（例如“过去2小时”、“今天”、“日期”）、哪个代理、哪个渠道（Messaging / Builder / Voice）、如何结束（升级、用户结束、转移、超时）或对话中的短语。我会显示匹配的会话作为编号列表 — 你选一个，我拉取。
> - **组织别名** — 用于 `sf` CLI 认证（你用 `sf org login` 配置的别名）。
>
> 产物位于 `~/.vibe/data/agentforce-d360-analyze/<org_id15>/<agent>__<ver>/<session_id>/`（每个脚本可使用 `--data-dir <path>` 覆盖）。

## 会话ID形式 — UUID 或 MessagingSession ID

在 `--session` 上两者都接受：

| 形式 | 示例 | 解析 |
|---|---|---|
| Agent Session UUID | `019dface-0000-7000-8000-000000000002` | 直接传递 |
| MessagingSession ID (`0Mw` 前缀) | `0MwTESTMSG12345AAA` | 通过 `resolve_session.py` 解析 — 第一次获取时进行实时数据云查找，之后优先从磁盘查找 |

**多匹配是真实的。** 一个 MessagingSession ID 可以映射到多个 Agent Session UUID。在多匹配时，解析器会打印每个候选者并退出非零状态；用户重新调用并指定一个UUID。

产物始终位于 `~/.vibe/data/agentforce-d360-analyze/<org_id15>/<agent>__<ver>/<session_id>/`（默认；可使用 `--data-dir <path>` 每个脚本覆盖）— 消息ID只是一个查找键，永远不会是目录名。主要代理（`sorted(agents_observed)` 中的第一个）命名 `<agent>__<ver>/` 段。

## 解析脚本前缀

默认安装将技能置于运行时插件根目录下。如果技能被克隆到其他地方（例如直接从 `forcedotcom/sf-skills` 仓库到自定义路径），设置 `PLUGIN_ROOT` 指向运行时的技能目录。

```bash
prefix="${SKILL_ROOT:-${PLUGIN_ROOT:-$HOME/.vibe/skills}/agentforce-d360-analyze}/scripts"
```

本文档中的后续调用使用 `"$prefix/..."`。

## 会话发现（尚未有ID）

当用户没有会话ID时，对 STDM 会话 DMO 运行 `discover_sessions.py`。打印编号选择器；用户选择一个；使用所选UUID继续。

```bash
python3 "$prefix/discover_sessions.py" --org <alias> [过滤器...]
```

**过滤器**（除 `--org` 外均为可选）：`--since <expr>`（默认最后24小时；接受“过去2小时”、“今天”、ISO日期）、`--agent <api-name>`、`--channel <Messaging|Builder|Voice>`、`--outcome <USER_ENDED|ESCALATED|TRANSFERRED|TIMEOUT|NOT_SET>`、`--grep <substring>`（对话文本）、`--tz <IANA>`、`--limit <N>`（默认20）。

**输出**：带 `#` 的 markdown 表格，包含 `UUID`、`开始 (UTC)`、`代理`、`渠道`、`持续时间`、`结果`。用户回复一个数字；使用该UUID继续。

## 流程 — 三个阶段

```text
fetch_dc.py     →  24 dc.<name>.json + dc._session_manifest.json     (DC 查询 REST 瀑布，5波)
assemble_dc.py  →  dc._session_tree.json                             (纯内存分层连接)
render_dc.py    →  dc._session_summary.md                            (人类摘要，多节)
```

每个阶段都可以独立运行。`fetch_dc.py --session <sid> --org <alias>` 默认链式执行所有三个阶段。

### 调用

```bash
python3 "$prefix/fetch_dc.py" --session <session-id-or-messaging-id> --org <alias>
```

标志：`--verbose` 用于每个 DMO 行计数；`--no-assemble` / `--no-render` 以提前停止。所有入口脚本 (`fetch_dc.py`, `assemble_dc.py`, `render_dc.py`, `resolve_session.py`, `discover_sessions.py`) 接受 `--data-dir <path>` 和 `--cache-dir <path>` 以覆盖默认的 `~/.vibe/{data,cache}/agentforce-d360-analyze/` 根目录 — 当主机运行时需要在不同的分布式布局下生成产物时，请传递这些参数。

### 输出产物

所有内容都位于 `~/.vibe/data/agentforce-d360-analyze/<org_id15>/<agent>__<ver>/<session_id>/`（默认；可使用 `--data-dir <path>` 覆盖）：

```text
dc.sessions.json              dc.steps.json                dc.gateway_requests.json
dc.interactions.json          dc.messages.json             dc.gateway_responses.json
dc.participants.json          dc.generations.json          dc.gateway_request_llm.json
dc.content_quality.json       dc.content_category.json     dc.gateway_request_metadata.json
dc.tags.json                  dc.tag_definitions.json      dc.gateway_request_tags.json
dc.tag_associations.json      dc.tag_definition_associations.json
dc.feedback.json              dc.feedback_details.json     dc.gateway_records.json
dc.moments.json               dc.moment_interactions.json
dc.telemetry_spans.json       dc.app_generation.json

dc._session_manifest.json     (每个 DMO 行计数 + 空值)
dc._session_tree.json         (分层连接 — 会话 → 交互 → 步骤 → 消息 → 生成 → gateway)
dc._session_summary.md        (渲染的人类摘要)
```

零行查询在清单中记录为 `status: empty`；不会写入文件。`assemble_dc` 可容忍缺失文件。参见 `references/artifacts.md` 了解完整的读取顺序。

## 数据云盲区 — 在提交根本原因之前阅读

数据云单独回答 **发生了什么** — 运行的步骤、触发的生成、记录的 gateway 请求。它不回答 **本可以发生但未发生什么**：

- 哪些 **主题** 在特定回合对分类器有资格（这存在于运行时规划器遥测中，而不是数据云）。
- 哪些 **动作** 在主题上被声明，哪些 **存活规则表达式** 被实际提供给 LLM。
- LLM 为什么选择一个主题/动作而不是另一个（完整的提示 + 响应文本仅存在于规划器运行时遥测中）。

如果用户的问题是关于 *某个特定主题或动作被使用或未被使用的原因*，数据云单独几乎从不足够。**告诉用户**：“可用性问题需要该回合的运行时规划器跟踪 — 这超出了此技能数据云界面的范围。检查镜像规划器记录决策的平台遥测。” 不要从运行时证据中编造根本原因。

### 数据云擅长什么

- **发生了什么** — 每个步骤、每个 LLM 调用、每个 gateway 请求 + 响应，按顺序，带时间戳和持续时间。适用于“带我走一遍会话”。
- **用户看到了什么** — 完整消息转录（用户 + 代理），按顺序。
- **LLM 产生了什么** — 生成、令牌计数、信任分数（毒性、指令依从性、来自 `content_quality` + `content_category` 的内容类别分解）。
- **工具调用** — 动作调用、输入、输出、错误（来自 `gateway_request_metadata` + `gateway_records`）。
- **反馈 + 标记** — 用户反馈、升级标记、会话结束类型。
- **审计完整性** — GatewayRequest 和 GatewayResponse 之间的 1:1 不变性会被检查；漂移会在 `counts.audit_chain_1to1_ok` 中标记。

## 前置条件

| 工具 | 需要 |
|---|---|
| `sf` CLI（针对目标组织进行认证） | 是 — `sf org login web --alias <alias>` |
| 目标组织上已启用数据云 | 是 — STDM + GenAI DMOs 必须为会话物化 |
| Python 3.10+ | 是 — 流程脚本 |

## 典型提示 — 它们映射到什么

| 用户说 | 技能做 |
|---|---|
| *"跟踪 my-org 中的会话 `<uuid>`"* | `fetch_dc.py --session <uuid> --org my-org` → 组装 → 渲染 |
| *"总结 `0Mw…` 中发生了什么"* | 解析 `0Mw…` → UUID，然后执行完整数据云流程 |
| *"查找今天 my-org 中 Messaging 升级的会话"* | 运行 `discover_sessions.py --since today --outcome ESCALATED --channel Messaging`，打印选择器，用户选择，然后数据云流程 |
| *"带我走一遍这个会话"* | 与跟踪相同 — 从渲染的摘要顶部到底部阅读 |

## 返回给用户的

流程完成后，渲染的 `dc._session_summary.md` 包含这些顶级部分：

1. **会话身份** — UUID、开始/结束、持续时间、代理、渠道、结束类型、参与者计数
2. **会话引导** — 渠道模式 + 引导变量 (`identity.mode`, `identity.bootstrap_variables`)
3. **ID 参考** — 分层跟踪中截断的所有内容的完整 UUID
4. **转录** — 用户 ↔ 代理按回合交互的叙事
5. **完整分层跟踪** — 交互 → 步骤 → 生成 → GatewayRequest，带 `+开始 + 持续时间 = +结束` 数学
6. **按回合摘要** — 每个交互一行
7. **规划器 LLM 调用（完整提示 + 响应）** — 通过 `--show-prompts` 选择性提供；默认抑制
8. **可视化分析** — gantt + LLM 调用覆盖
9. **会话计数** — 工程师面对的清单计数表
10. **空值诊断** — 每个DMO一行，`rows == 0` 且 `_unavailable_reason` 已填充
11. **目录（会话过滤）** — TagDefinitions / TagDefinitionAssociations / Tags 过滤到会话中观察到的代理

进行深入分析，打开 `dc._session_tree.json` — 这是摘要渲染的单一事实来源。参见 `references/dc_pipeline_contract.md` 了解完整流程合同和 `references/dc_dmo_fields.md` 了解每个DMO的字段参考。

## 注意事项

- **`gateway_requests_dropped_by_stdm`** — 当数据云报告零 `gateway_requests` 行但运行时遥测显示 LLM 调用确实发生时，此技能无法明确区分“STDM 导出者丢弃了写入”与“源处禁用了记录”。会话报告为 `planner_ran_no_gateway_logs`；操作员可以检查平台遥测以消除歧义。参见 `references/dc_pipeline_contract.md` §2.8。
- **延迟** — 生成和 GatewayRequest 带有单写时间戳，而不是开始/结束对。渲染器不会计算它们之间的“延迟”——这个差值反映数据云的序列化顺序，而不是 LLM 调用花费的时间。
- **数据云物化延迟** — 新鲜会话可能显示 `interactions_not_materialized_yet`，如果 STDM 还未赶上。稍等一分钟左右再重跑。
