# agentforce-architecture-analyze — 声明的架构快照

一个 Agentforce 代理的设计时元数据树：planner → topics → actions → flows → Apex → prompts → NGA 插件。仅读取声明的元数据 — `BotDefinition`, `GenAiPlanner*`, `GenAiPlugin*`, `GenAiFunction*`, `Flow`, `ApexClass`, `GenAiPromptTemplate`。**不**读取运行时审计行。

**运行时预算：** 参考配置的典型时间为 30–45 秒，硬上限 ≤60 秒。顺序基线时间为 90–220 秒；并行工具 SOQL 扇出可提供 3–5 倍的速度提升。具有许多流的较大代理近似线性扩展 — 每个流元数据检索是一次往返。

**内联运行** — 无子代理。每个阶段都是确定性文件处理。

## 如果用户未提供足够信息继续

当使用没有 `agent_api_name` 且没有组织别名时，打印以下块**逐字** — 不要释义，不要预运行任何脚本。触发条件：`$ARGUMENTS` 为空 OR 未命名代理（没有 `--agent` 标志且没有文本中已知的代理 API 名称）OR 未命名组织（没有 `--org` 标志且没有已知的别名）。

> 我应该为哪个代理文档化，以及哪个组织？
>
> 我需要：
> - **代理 API 名称** — `BotDefinition` 的 `DeveloperName`（例如 `MyAgent`, `MySalesAgent`）。不是标签。
> - **组织别名** — 用于 `sf` CLI 认证（您使用 `sf org login` 配置的别名）
>
> 可选：
> - **版本** — 类似 `v5` 的 `agent_version_api_name`。如果省略，我将解析活动的 `BotVersion`。
> - `--force` — 忽略缓存树；重新获取所有内容。
> - `--reprobe` — 重新运行 7 天的通道探测缓存（仅在 Salesforce 发布后需要）。
>
> 我将内联运行元数据管道。工件位于 `~/.vibe/data/agentforce-architecture-analyze/<org_id15>/<agent_api_name>__<agent_version>/`（可使用 `--data-dir` 覆盖）。

## 管道调用

当用户提供了 `--org <alias>` + `--agent <api_name>`（以及任何可选标志）时，运行此块。一个 `python3` 调用驱动整个管道。`main.py` 写入 `.emit_ctx.json`；`emit_result.py` 读取它并最后将最终的 `=== RESULT ===` 块打印到 stdout。

```bash
set -euo pipefail

# zsh 数组默认为 1 索引；bash 数组为 0 索引。
# 此块在整个过程中使用 0 索引语义（_args[$i] 从 i=0 开始），
# 因此在 zsh + `set -u` 下，_args[0] 的第一个读取会触发
# `parameter not set`。KSH_ARRAYS 使 zsh 将数组视为 0 索引，
# 匹配 bash shebang 的预期。在 bash 下无操作。
[ -n "${ZSH_VERSION:-}" ] && setopt KSH_ARRAYS

SKILL_ROOT="${SKILL_ROOT:-${PLUGIN_ROOT:-$HOME/.vibe/skills}/agentforce-architecture-analyze}"

# 参数解析器。接受 `--org foo` 和 `--org=foo`。
# `$ARGUMENTS` 是 Claude Code 替换的原始用户输入。
ARG_ORG=""
ARG_AGENT=""
ARG_VERSION=""
ARG_FORCE=""
ARG_REPROBE=""
ARG_PARALLELISM=""
ARG_MAX_MERMAID=""

# shellcheck disable=SC2206
_args=($ARGUMENTS)
i=0
while [ $i -lt ${#_args[@]} ]; do
 tok="${_args[$i]}"
 case "$tok" in
 --org=*) ARG_ORG="${tok#--org=}" ;;
 --org) i=$((i+1)); ARG_ORG="${_args[$i]:-}" ;;
 --agent=*) ARG_AGENT="${tok#--agent=}" ;;
 --agent) i=$((i+1)); ARG_AGENT="${_args[$i]:-}" ;;
 --version=*) ARG_VERSION="${tok#--version=}" ;;
 --version) i=$((i+1)); ARG_VERSION="${args[$i]:-}" ;;
 --parallelism=*) ARG_PARALLELISM="${tok#--parallelism=}" ;;
 --parallelism) i=$((i+1)); ARG_PARALLELISM="${args[$i]:-}" ;;
 --max-mermaid-nodes=*) ARG_MAX_MERMAID="${tok#--max-mermaid-nodes=}" ;;
 --max-mermaid-nodes) i=$((i+1)); ARG_MAX_MERMAID="${args[$i]:-}" ;;
 --force) ARG_FORCE="1" ;;
 --reprobe) ARG_REPROBE="1" ;;
 esac
 i=$((i+1))
done

# 如果需要，则显示使用块。代理读取 stderr，
# 逐字打印并停止 — **不**预运行 main.py。
if [ -z "$ARG_ORG" ] || [ -z "$ARG_AGENT" ]; then
 cat >&2 <<'USAGE'
> 我应该为哪个代理文档化，以及哪个组织？
>
> 我需要：
> - **代理 API 名称** — BotDefinition.DeveloperName（例如 `MyAgent`）
> - **组织别名** — 用于 `sf` CLI 认证（您使用 `sf org login` 配置的别名）
>
> 可选标志：
> - `--version v5` — 固定特定的 BotVersion（默认：Active+最高）
> - `--force` — 跳过缓存
> - `--reprobe` — 强制通道探测刷新
> - `--parallelism N` — ThreadPoolExecutor 大小（默认 5）
> - `--max-mermaid-nodes N` — 限制 Mermaid 节点数量（默认 80）
USAGE
 exit 2
fi

# 每次调用创建新的工作目录。Epoch + 随机后缀避免同一主机上并发运行的冲突。
WORK_DIR="/tmp/agentforce-architecture-analyze-$(date +%s)-$RANDOM"
mkdir -p "$WORK_DIR"

# 边界处的输入验证，在任何 python3 调用之前。
# fs_guard 失败时退出 1 并打印 INVALID_INPUT RESULT 块；
# `|| exit 1` 是必需的 — 空调用在失败后静默继续。
python3 "$SKILL_ROOT/scripts/_shared/fs_guard.py" "$ARG_AGENT" agent_api_name api_name || exit 1
python3 "$SKILL_ROOT/scripts/_shared/fs_guard.py" "$ARG_ORG" org_alias not_empty || exit 1
python3 "$SKILL_ROOT/scripts/_shared/fs_guard.py" "$WORK_DIR" WORK_DIR symlink || exit 1
python3 "$SKILL_ROOT/scripts/_shared/fs_guard.py" "$WORK_DIR" WORK_DIR owned || exit 1
if [ -n "$ARG_VERSION" ]; then
 python3 "$SKILL_ROOT/scripts/_shared/fs_guard.py" "$ARG_VERSION" agent_version api_name || exit 1
fi

# 单个 python3 调用驱动所有管道阶段。main.py 将
# `.emit_ctx.json` 写入 $WORK_DIR — emit_result.py 然后从该 ctx 渲染
# RESULT 块。每个阶段不使用子进程。
_main_args=(--org-alias "$ARG_ORG" --agent "$ARG_AGENT" --work-dir "$WORK_DIR")
[ -n "$ARG_VERSION" ] && _main_args+=(--version "$ARG_VERSION")
[ -n "$ARG_FORCE" ] && _main_args+=(--force)
[ -n "$ARG_REPROBE" ] && _main_args+=(--reprobe)
[ -n "$ARG_PARALLELISM" ] && _main_args+=(--parallelism "$ARG_PARALLELISM")
[ -n "$ARG_MAX_MERMAID" ] && _main_args+=(--max-mermaid-nodes "$ARG_MAX_MERMAID")

# 如果需要，则显示使用块。代理读取 stderr，
# 逐字打印并停止 — **不**预运行 main.py。
if [ -z "$ARG_ORG" ] || [ -z "$ARG_AGENT" ]; then
 cat >&2 <<'USAGE'
> 我应该为哪个代理文档化，以及哪个组织？
>
> 我需要：
> - **代理 API 名称** — BotDefinition.DeveloperName（例如 `MyAgent`）
> - **组织别名** — 用于 `sf` CLI 认证（您使用 `sf org login` 配置的别名）
>
> 可选标志：
> - `--version v5` — 固定特定的 BotVersion（默认：Active+最高）
> - `--force` — 跳过缓存
> - `--reprobe` — 强制通道探测刷新
> - `--parallelism N` — ThreadPoolExecutor 大小（默认 5）
> - `--max-mermaid-nodes N` — 限制 Mermaid 节点数量（默认 80）
USAGE
 exit 2
fi

# 每次调用创建新的工作目录。Epoch + 随机后缀避免同一主机上并发运行的冲突。
WORK_DIR="/tmp/agentforce-architecture-analyze-$(date +%s)-$RANDOM"
mkdir -p "$WORK_DIR"

# 边界处的输入验证，在任何 python3 调用之前。
# fs_guard 失败时退出 1 并打印 INVALID_INPUT RESULT 块；
# `|| exit 1` 是必需的 — 空调用在失败后静默继续。
python3 "$SKILL_ROOT/scripts/_shared/fs_guard.py" "$ARG_AGENT" agent_api_name api_name || exit 1
python3 "$SKILL_ROOT/scripts/_shared/fs_guard.py" "$ARG_ORG" org_alias not_empty || exit 1
python3 "$SKILL_ROOT/scripts/_shared/fs_guard.py" "$WORK_DIR" WORK_DIR symlink || exit 1
python3 "$SKILL_ROOT/scripts/_shared/fs_guard.py" "$WORK_DIR" WORK_DIR owned || exit 1
if [ -n "$ARG_VERSION" ]; then
 python3 "$SKILL_ROOT/scripts/_shared/fs_guard.py" "$ARG_VERSION" agent_version api_name || exit 1
fi

# 单个 python3 调用驱动所有管道阶段。main.py 将
# `.emit_ctx.json` 写入 $WORK_DIR — emit_result.py 然后从该 ctx 渲染
# RESULT 块。每个阶段不使用子进程。
_main_args=(--org-alias "$ARG_ORG" --agent "$ARG_AGENT" --work-dir "$WORK_DIR")
[ -n "$ARG_VERSION" ] && _main_args+=(--version "$ARG_VERSION")
[ -n "$ARG_FORCE" ] && _main_args+=(--force)
[ -n "$ARG_REPROBE" ] && _main_args+=(--reprobe)
[ -n "$ARG_PARALLELISM" ] && _main_args+=(--parallelism "$ARG_PARALLELISM")
[ -n "$ARG_MAX_MERMAID" ] && _main_args+=(--max-mermaid-nodes "$ARG_MAX_MERMAID")

# main.py 在终端失败时返回非零值；我们**不**短路 —
# emit_result 仍然发布失败 RESULT 块。`set -e` 在此单个调用周围暂时放宽。
set +e
python3 "$SKILL_ROOT/scripts/main.py" "${_main_args[@]}"
_rc=$?
set -e

# 最终 RESULT 块是 emit_result.py 的 stdout —
# 必须是 stdout 最后看到的东西。emit_result 在渲染成功时退出 0；
# bash 容器传播 main.py 的 rc 作为代理的退出状态。
WORK_DIR="$WORK_DIR" python3 "$SKILL_ROOT/scripts/emit_result.py"
exit "$_rc"
```

## 输入

| 输入 | 标志 | 必需 | 默认 |
|---|---|---|---|
| `org_alias` | `--org` | 是 | — |
| `agent_api_name` | `--agent` | 是 | — |
| `agent_version_api_name` | `--version` | 否 | 活动的 BotVersion |
| `force_refresh` | `--force` | 否 | false（尊重缓存） |
| `reprobe` | `--reprobe` | 否 | false（尊重 7 天通道探测缓存） |
| `parallelism` | `--parallelism` | 否 | 5 |
| `max_mermaid_nodes` | `--max-mermaid-nodes` | 否 | 80 |
| `data_dir` | `--data-dir` | 否 | `~/.vibe/data/agentforce-architecture-analyze` |
| `cache_dir` | `--cache-dir` | 否 | `~/.vibe/cache/agentforce-architecture-analyze` |

## 输出

所有工件位于 `~/.vibe/data/agentforce-architecture-analyze/<org_id15>/<agent_api_name>__<agent_version>/`（默认；使用 `--data-dir <path>` 覆盖）：

```xml
<agent>_<ver>_metadata_tree.json   主要工件 — 标准化的 planner/topic/action/flow/apex/prompt/plugin 树
<agent>_<ver>_architecture.md      人类可读的逐节渲染（H1 + 7 个编号节，以及一个条件依赖图附录）。Mermaid 图表嵌入在相关节中（Action 树，数据流，以及依赖图）
```

## 管道 — 内联，无子代理

```text
resolve_bot.py        → BotDefinition + BotVersion + planner 名称查找
retrieve_planner.py   → Metadata API zip 检索 GenAiPlannerBundle (+ NGA 插件如果存在)
parallel_retrieve.py  → 6 个并行工具 SOQL 通道从 planner id 扇出
                          （由 `planner_definition_by_agent_chain` 种子查询解析）：
                          - plugins_by_planner (GenAiPluginDefinition)
                          - planner_bundle_functions (GenAiPlannerFunctionDef 连接)
                          - functions_by_plugins (GenAiFunctionDefinition)
                          - planner_attrs_by_parent_ids (GenAiPlannerAttrDefinition)
                          - plugin_functions_by_plugin_ids (GenAiPluginFunctionDef 连接)
                          - plugin_instructions_by_plugin_ids (GenAiPluginInstructionDef)
parse_bundle.py       → 解析检索到的 XML 为标准化节点形状
parse_wave.py         → BFS 扩展：在节点中发现 flow/apex/prompt 引用
                          → SOQL 检索 Flow/Apex 正文（按 id 列表分批）
                          → 仅检索 GenAiPromptTemplate 的 Metadata（NGA 外部插件按需条件性）
finalize.py           → 合并波浪到 metadata_tree.json
render_architecture.py → <agent>_<ver>_architecture.md + Mermaid 调用图（最多 --max-mermaid-nodes）
```

**通道策略 — SOQL 优先。**
- **工具 SOQL** 每个标准化树节点（planner, plugins, functions, plugin-functions, plugin-instructions, planner-functions, planner-attrs）— 6 个并行通道键入 planner id，加上解析 planner id 的 `planner_definition_by_agent_chain` 种子查询。
- **数据 API SOQL** 用于 Flow（按 id）和 Apex（按 id 或名称）正文 — 分批。
- **Metadata 检索** 仅在两种情况下： (a) `GenAiPromptTemplate`（提示正文未通过工具 SOQL 清晰暴露），以及 (b) NGA **外部插件** 当 planner 是 Native Generative Agent 形状时（经典 ReAct 跳过）。

这是 3–5 倍速度提升的来源。朴素实现会通过 Metadata API zips 顺序检索所有内容；并行工具 SOQL 在单次扇出中覆盖了约 80% 的树。

## Planner 形状 — 经典 ReAct vs NGA

技能将两个 planner 家族标准化为单个树形状：

| 形状 | `GenAiPlannerDefinition.PlannerType` | 调用目标样式 | NGA 插件？ |
|---|---|---|---|
| **经典 ReAct** | `ReactAiPlannerV1` / `SequentialPlannerIntentClassifier` / 等. | DeveloperName 字符串 | 否 |
| **NGA** | `ConcurrentMultiAgentOrchestration` / `AnthropicCompatibleV1` / 等. | 有时 15/18 字符 Ids (ID 前缀路由) | 是（通过 Metadata 检索外部插件） |

`resolve_invocation_target.py` 中的 ID 前缀路由区分两种：看起来像 ids 的 NGA 调用目标（`01p…` = ApexClass, `301…` = Flow, 等.）通过 id 范围 SOQL 解析；DeveloperName 目标通过名称范围 SOQL。未知前缀显示为 `_unresolved[]` 并带有 `reason="unknown-id-prefix:<prefix>"` — 永不静默丢弃。

## 缓存

- **树缓存**：`metadata_tree.json` 除非传递 `--force` 否则重用。缓存键包括技能捆绑的每个 `.soql` / `.yaml` / `.mmd` 模板的资产哈希 — 更改模板，缓存自动失效。
- **通道探测缓存**：每个组织的 7 天 TTL 的 `sf sobject describe` 结果，验证 SOQL 资产参考的每个字段名称。Salesforce 季度发布重命名/删除字段会触发 `status: PROBE_FAILED`；`--reprobe` 强制刷新。

## 前置条件

| 工具 | 必需 |
|---|---|
| `sf` CLI（针对目标组织进行认证） | 是 — `sf org login web --alias <alias>` |
| Python 3.10+ | 是 |

## 需要时加载的参考文档

不要急切加载。当用户的问题需要时加载：

- `references/soql_fields.md` — 技能触及的 13 个 sObject 的每个对象字段参考（2 个 Data API + 11 个 Tooling），带有 `[mandatory]` vs `[optional]` 标签。当用户询问特定字段，或调试 `INVALID_FIELD` SOQL 错误时加载。
- `references/contract.json` — `metadata_tree.json` 的机器可读模式。当编写消耗树的下游工具时加载。
- `references/architecture_sections.md` — 渲染的 `<agent>_<ver>_architecture.md` 的逐节结构。

## 值得事先了解的不变量

- **管道是确定性的。** 相同的 `(org, agent, version)` + 静态组织元数据 → 字节相同的 `<agent>_<ver>_metadata_tree.json` 和 `<agent>_<ver>_architecture.md`。只有显示时间戳在重新运行时漂移。
- **仅向前遍历。** 每个发现的引用都是从 planner 向子项。没有向后查找。
- **部分结果是显示的，而不是被抑制的。** 任何未解决的引用都会落在 `_unresolved[]` 并带有 `reason=...`。`STATUS=PARTIAL_OK` 如果任何通道失败；`STATUS=OK` 仅在干净运行时。
- **循环检测是按分支进行的。** 沿自己的祖先链访问的相同流会发出 `_cycle_back_to:<path>` 而不是递归。防御性的 `MAX_BFS_DEPTH=20` 堵护每个分支的祖先集；现实中的代理在触发任何限制之前都会很好地底部结束。（早期文档声称 5 的硬上限；这是历史限制，后来放弃，因为像 `handleFlowFault` 这样的共享实用程序流在每次嵌套树中都会触发它 — 请参阅 `config.MAX_BFS_DEPTH` 的理由。）
- **子项按 `api_name`（不区分大小写）字母顺序排序。** Topics 在根级别之前出现在 plannerActions。Flow-actionCall 顺序**未**排序 — 那是流作者的执行序列。
