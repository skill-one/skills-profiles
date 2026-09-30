---
name: agentforce-observe
description: 使用会话跟踪和数据云分析生产 Agentforce 代理行为，并管理代理健康监控（AHM）警报。触发条件如下：当用户查询 STDM 会话数据或数据云跟踪记录；调查生产代理故障、回归或性能问题时；询问会话跟踪、对话日志或代理指标；希望在预览环境中重现报告的生产问题；运行 findSessions 或跟踪分析查询；在代理指标（如升级率、分流等）上创建、列出、更新或删除 AHM 数据警报；询问为何警报未触发或希望检查警报是否已触发（通知计数或每个警报的事件视图）。不触发条件如下：当用户在开发过程中创建、修改或调试 .agent 文件（使用 agentforce-generate）；编写或运行测试规范（使用 agentforce-test）；使用 sf agent preview 进行本地开发迭代；部署或发布代理时。
---

# Agentforce 可观察性

使用会话跟踪数据和生活预览测试来改进 Agentforce 代理。

**三阶段工作流程：**
- **观察** -- 从数据云查询 STDM 会话（如果可用），或者运行测试套件 + 预览本地跟踪作为后备
- **重现** -- 使用 `sf agent preview` 实时模拟有问题的对话
- **改进** -- 直接编辑 `.agent` 文件，验证，发布，验证

---

## 平台说明

- 以下 Shell 示例使用 bash 语法。在 Windows 上，使用 PowerShell 对应命令或 Git Bash。
- 在 Windows 上将 `python3` 替换为 `python`。
- 将 `/tmp/` 替换为 `$env:TEMP\`（PowerShell）或 `%TEMP%\`（cmd）。
- 如果未安装 jq，将 `jq` 替换为 `python -c "import json,sys; ..."`。

---

## 路由

开始之前收集这些输入：

- **组织别名**（必需） -- 必须经过身份验证（否则 `sf org login web`）
- **代理 API 名称**（必需用于预览和部署；如果未提供，请询问）
- **代理文件路径**（可选） -- `.agent` 文件路径，通常为 `force-app/main/default/aiAuthoringBundles/<AgentName>/<AgentName>.agent`。如果未提供，则自动检测。
- **会话 ID**（可选） -- 分析特定会话；如果不存在，则查询最近 7 天
- **回溯天数**（可选，默认为 7）
- **警报所有者用户**（可选，仅警报） -- 要列出/管理的用户；默认为当前用户

从用户输入中确定意图：

- **没有特定操作** -> 运行所有三个分析阶段：观察 -> 揭示问题 -> 询问用户是否要重现和/或改进
- **"analyze" / "sessions" / "what's wrong"** -> 仅第一阶段，然后建议下一步操作
- **"reproduce" / "test" / "preview"** -> 第二阶段（如果手头没有问题，则先运行第一阶段）
- **"fix" / "improve" / "update"** -> 第三阶段（如果手头没有问题，则先运行第一阶段）
- **"create alert" / "set up monitoring" / "alert me when"** -> AHM（创建）
- **"list alerts" / "show my alerts" / "update alert" / "delete alert"** -> AHM（列出 / 通过 PUT 更新 / 删除）
- **"get / list notifications" / "notifications for a specific alert" / "have my alerts fired" / "why isn't my alert firing"** -> AHM：使用头部 `X-UNS-Type-Filter: all` 获取通知，报告状态 + 列表；对于特定警报，根据 `targetPageRef.state.c__alertId`（15/18 字符安全）过滤，而不是 metricId（+ 事件视图 + metric 验证）

### 解析代理名称

在任何 STDM 查询之前，将用户提供的代理名称与组织进行解析，以获取确切的 `MasterLabel` 和 `DeveloperName`：

```bash
sf data query --json \
  --query "SELECT Id, MasterLabel, DeveloperName FROM GenAiPlannerDefinition WHERE MasterLabel LIKE '%<user-provided-name>%' OR DeveloperName LIKE '%<user-provided-name>%'" \
  -o <org>
```

- `MasterLabel` = STDM `findSessions` 和 Agent Builder UI 使用的显示名称（例如 "Order Service"）
- `DeveloperName` = 使用的 API 名称带版本后缀，用于元数据（例如 "OrderService_v9"）
- `sf agent preview/activate/publish` 的 `--api-name` 标志使用 `DeveloperName` **不带** `_vN` 后缀（例如 "OrderService"）

存储这些值：
- `AGENT_MASTER_LABEL` -- 用于 `findSessions()` 代理过滤器
- `AGENT_API_NAME` -- `DeveloperName` 不带 `_vN` 后缀，用于 `sf agent` CLI 命令
- `PLANNER_ID` -- 此代理的 Salesforce 记录 ID

### 定位 .agent 文件

**步骤 1 -- 本地搜索：**

```bash
find <project-root>/force-app/main/default/aiAuthoringBundles -name "*.agent" 2>/dev/null
```

如果用户提供了代理文件路径，则直接使用。否则，搜索匹配 `AGENT_API_NAME` 的文件。

**步骤 2 -- 如果本地未找到，从组织检索：**

```bash
sf project retrieve start --json --metadata "AiAuthoringBundle:<AGENT_API_NAME>" -o <org>
```

> **已知错误：** `sf project retrieve start` 创建一个双重嵌套路径：`force-app/main/default/main/default/aiAuthoringBundles/...`。立即修复检索后：

```bash
if [ -d "force-app/main/default/main/default/aiAuthoringBundles" ]; then
  mkdir -p force-app/main/default/aiAuthoringBundles
  cp -r force-app/main/default/main/default/aiAuthoringBundles/* \
    force-app/main/default/aiAuthoringBundles/
  rm -rf force-app/main/default/main
fi
```

**步骤 3 -- 验证检索的文件：**

读取 `.agent` 文件并验证它具有正确的 Agent Script 结构：
- `system:` 块带 `instructions:`
- `config:` 块带 `developer_name:`
- `start_agent` 或 `subagent` 块带 `reasoning: instructions:`
- 每个子代理应具有不同的 `instructions:` 内容（子代理之间不应相同）

将解析的路径存储为 `AGENT_FILE` 以供第三阶段使用。

---

## 第一阶段 0：发现数据空间

在运行任何 STDM 查询之前，确定正确的 Data Cloud Data Space API 名称。

```bash
sf api request rest "/services/data/v63.0/ssot/data-spaces" -o <org>
```

注意：`sf api request rest` 是一个 beta 命令 -- 不要添加 `--json`（该标志不受支持且会导致错误）。

响应形状是：
```json
{
  "dataSpaces": [
    {
      "id": "0vhKh000000g3DjIAI",
      "label": "default",
      "name": "default",
      "status": "Active",
      "description": "您组织的默认数据空间。"
    }
  ],
  "totalSize": 1
}
```

`name` 字段是传递给 `AgentforceOptimizeService` 的 API 名称。

**决策逻辑：**
- 如果命令失败（例如 404 或权限错误），则回退到 `'default'` 并将其记录为假设。
- 过滤仅 `status: "Active"` 的条目。
- 如果存在一个活动的 Data Space，则自动使用它并确认给用户： "使用数据空间: `<name>`"。
- 如果存在多个活动的 Data Space，则显示列表（标签 + 名称）并询问用户要使用哪个。

将选择的 `name` 值存储为 `DATA_SPACE` 以供后续所有步骤使用。

### 前置条件检查：STDM DMO

在部署辅助类（步骤 1.0）后，运行快速探测以验证 STDM Data Model Objects 是否存在于数据云中：

```bash
sf apex run -o <org> -f /dev/stdin << 'APEX'
ConnectApi.CdpQueryInput qi = new ConnectApi.CdpQueryInput();
qi.sql = 'SELECT ssot__Id__c FROM "ssot__AiAgentSession__dlm" LIMIT 1';
try {
    ConnectApi.CdpQueryOutputV2 out = ConnectApi.CdpQuery.queryAnsiSqlV2(qi, '<DATA_SPACE>');
    System.debug('STDM_CHECK:OK rows=' + (out.data != null ? out.data.size() : 0));
} catch (Exception e) {
    System.debug('STDM_CHECK:FAIL ' + e.getMessage());
}
APEX
```

**如果 `STDM_CHECK:FAIL`：** STDM 未激活。通知用户并切换到 **第一阶段-ALT**：

> STDM（会话跟踪数据模型）在此组织中不可用。要启用：设置 -> 数据云 -> 数据流并验证 "Agentforce 活动" 是否处于活动状态。**使用后备方案：测试套件 + 本地跟踪。**

**如果 `STDM_CHECK:OK`**，则继续第一阶段（STDM 路径）。

---

## 第一阶段-ALT：无 STDM 观察（后备路径）

当 STDM 不可用时，使用测试套件和 `sf agent preview --authoring-bundle` 以及本地跟踪分析。

| 数据源 | 使用场景 | 优点 | 缺点 |
|---|---|---|---|
| STDM（第一阶段） | 历史生产分析 | 真实用户数据，数量 | 需要 Data Cloud，15 分钟延迟 |
| 测试套件 + 本地跟踪（第一阶段-ALT） | 开发迭代，没有 STDM 的组织 | 即时，完整的 LLM 提示，可变状态 | 仅预览，没有真实用户数据 |

### 1-ALT.1 运行现有测试套件（如果可用）

```bash
sf agent test list --json -o <org>
sf agent test run --json --api-name <TestSuiteName> --wait 10 --result-format json -o <org> | tee /tmp/test_run.json
JOB_ID=$(python3 -c "import json; print(json.load(open('/tmp/test_run.json'))['result']['runId'])")
sf agent test results --json --job-id "$JOB_ID" --result-format json -o <org>
```

### 1-ALT.2 从 .agent 文件派生测试话语（如果没有测试套件）

如果不存在测试套件，则从 `.agent` 文件派生话语：每个非入口子代理一个（从 `description:` 关键字），每个关键操作一个，一个护栏测试，一个多轮测试。

### 1-ALT.3 使用 `--authoring-bundle` 预览（本地跟踪）

将每个测试话语通过预览以生成本地跟踪文件：

```bash
sf agent preview start --json --authoring-bundle <BundleName> --simulate-actions -o <org> | tee /tmp/preview_start.json
SESSION_ID=$(python3 -c "import json; print(json.load(open('/tmp/preview_start.json'))['result']['sessionId'])")

sf agent preview send --json --session-id "$SESSION_ID" --authoring-bundle <BundleName> \
  --utterance "$UTT" -o <org> | tee /tmp/preview_response.json

sf agent preview end --json --session-id "$SESSION_ID" --authoring-bundle <BundleName> -o <org>
```

**跟踪文件位置：** `.sfdx/agents/{BundleName}/sessions/{sessionId}/traces/{planId}.json`

### 1-ALT.4 本地跟踪诊断

| 问题类型 | 跟踪命令 |
|---|---|
| 子代理误路由 | `jq -r '.plan[] \| select(.type=="NodeEntryStateStep") \| .data.agent_name' "$TRACE"` |
| 操作未调用 | `jq -r '.plan[] \| select(.type=="EnabledToolsStep") \| .data.enabled_tools[]' "$TRACE"` |
| 低遵循度 | `jq -r '.plan[] \| select(.type=="ReasoningStep") \| {category, reason}' "$TRACE"` |
| 变量捕获失败 | `jq -r '.plan[] \| select(.type=="VariableUpdateStep") \| .data.variable_updates[]' "$TRACE"` |
| 模糊指令 | `jq -r '.plan[] \| select(.type=="LLMStep") \| .data.messages_sent[0].content' "$TRACE"` |

**DefaultTopic 跟踪怪癖：** 使用 `--authoring-bundle` 时，即使路由正常，根 `.topic` 字段也经常显示 `"DefaultTopic"`。始终使用 `NodeEntryStateStep.data.agent_name` 获取真实的子代理链。

**直接回答（SMALL_TALK 模式）：** 如果 `start_agent` 跟踪显示 `SMALL_TALK` 接地并且可见转换工具但未调用，请将 "您是一个路由器。不要直接回答问题。" 添加到 `start_agent` 指令中。

### 1-ALT.5 分类并展示

使用 `references/issue-classification.md` 中的类别对问题进行分类。展示结果后，自动进行代理配置证据分析。

---

## 第一阶段：观察 -- 查询 STDM

> 完整 STDM 查询详细信息、Apex 服务部署和响应解析：见 `references/stdm-queries.md`

### 1.0 部署辅助类（每个组织一次）

将 `AgentforceOptimizeService` Apex 类部署到组织。首先检查是否已部署：

```bash
sf data query --json --query "SELECT Id, Name FROM ApexClass WHERE Name = 'AgentforceOptimizeService'" -o <org>
```

如果未部署，则从技能目录复制并部署。有关完整步骤，请参阅 `references/stdm-queries.md`。

### 1.1 查找会话

使用 `findSessions()` 查询最近会话。解析 Apex 调试日志中的 `DEBUG|STDM_RESULT:`。如果 `findSessions` 返回空，则切换到第一阶段-ALT。

### 1.2 获取对话详细信息

使用 `getMultipleConversationDetails()` 最多 5 个会话（按最新顺序）。返回按回合的数据，包括消息、步骤、主题和操作结果。

### 1.2b 获取 LLM 提示/响应（可选）

当检测到低遵循度时，使用 `getLlmStepDetails()` 获取实际的 LLM 提示和响应。

### 1.2c 获取聚合指标（推荐第一步）

使用 `getAggregatedMetrics()` 获取高级别的健康仪表板：会话率、顶级意图、质量分布、RAG 平均值。

### 1.2d 获取时刻洞察（每个会话的详细信息）

使用 `getMomentInsights()` 获取每个会话的意图摘要、质量分数（1-5）和检索器指标。

### 1.2e 运行可观察性查询（RAG 深入分析）

使用 `runObservabilityQuery()` 进行有针对性的 RAG 分析：知识差距、幻觉、检索质量、答案相关性、排行榜。

### 1.3 重建对话

从每个会话的 `ConversationData` JSON 渲染按回合的时间线。

### 1.4 识别问题

> 完整问题模式表和分类类别：见 `references/issue-classification.md`

检查每个会话是否存在：操作错误、子代理误路由、缺少操作、错误输入、变量捕获失败、无转换、慢操作、低遵循度、放弃会话、死子代理、发布漂移、死中心反模式、入口直接回答，以及安全问题。

**语音代理（具有 `modality voice:` 块）：** 还检查：
- 响应冗长 — 任何超过 3 句话的代理响应（语音 UX 反模式；也是静音/提示计时器触发）
- 响应中的视觉格式 — 不在语音中渲染的列表、链接、Markdown
- 缺少确认模式 — 修改数据的操作不重复关键细节
- 缺少语音接线 — 语音代理缺少链接变量 `@VoiceCall.Id` 或 `connection customer_web_client:` 块，或者有人添加了一个不存在的 `connection voice:` 块
- **延迟反模式** — 将跟踪步骤持续时间与 `/agentforce-generate` [`references/voice-latency-heuristics.md`](../agentforce-generate/references/voice-latency-heuristics.md) 中字段验证的模式进行交叉引用：同步写入实时呼叫路径、返回原始给推理 LLM 的庞大检索、链式外部调用、过度分解的子代理路由、以及没有确认短语但操作缓慢的慢操作。延迟修复是**仅标记**的，除非纯粹是指导性的（确认短语、回合长度、口语形式规则）。
- **TTS 杂音 / 缺少口语形式规则** — 操作输出或响应中显示价格、电话号码或 ID 而没有口语形式指令规则

优先级：P1 = 操作错误、误路由、低遵循度；P2 = 缺少操作、变量错误、知识差距；P3 = 性能、放弃会话、语音 UX 问题、语音延迟反模式。

### 1.5 展示发现和代理配置证据

展示分析的会话、按根本原因类别分组的问题，以及提升估计。然后自动进行 `.agent` 文件分析以确认根本原因。

> 完整结构分析检查、交叉参考程序和发布漂移检测：见 `references/issue-classification.md`

从组织检索 `.agent` 文件，运行自动检查（子代理数量与操作块对比、死中心检测、孤儿操作、跨子代理变量依赖），并将 STDM 症状与文件结构进行交叉参考。

---

## 第二阶段：重现 -- 实时预览

> 完整预览程序、跟踪诊断命令和分类标准：见 `references/reproduce-reference.md`

为第一阶段确认的每个问题构建一个测试场景。通过 `sf agent preview` 运行每个场景，使用 `--authoring-bundle`（生成本地跟踪）。运行每个场景 **3 次** 并分类：

| 判定 | 标准 |
|---|---|
| `[CONFIRMED]` | 在 3/3 运行中相同失败 |
| `[INTERMITTENT]` | 在 1-2 运行中失败 |
| `[NOT REPRODUCED]` | 在 3/3 运行中通过 |

仅 `[CONFIRMED]` 和 `[INTERMITTENT]` 的问题继续到第三阶段。

**关键命令：**

```bash
sf agent preview start --json --authoring-bundle <Name> --simulate-actions -o <org>
sf agent preview send --json --session-id "$SID" --utterance "<text>" --authoring-bundle <Name> -o <org>
sf agent preview end --json --session-id "$SID" --authoring-bundle <Name> -o <org>
```

从 Salesforce 项目目录运行这些命令。`start` 需要一个带有 `--authoring-bundle` 的操作模式（`--simulate-actions` 或 `--use-live-actions`）；该标志被 `send` 和 `end` 拒绝。

**跟踪位置：** `.sfdx/agents/{Name}/sessions/{sessionId}/traces/{planId}.json`

---

## 第三阶段：改进 -- 直接编辑 .agent 文件

> 预飞行检查、修复映射、指令原则、回归预防、部署链、验证、安全重新验证和测试用例创建的完整程序：见 `references/improve-reference.md`

### 3.0 预飞行

在编辑之前验证所有操作目标是否存在并已在组织中注册。如果目标缺失，则展示选项：部署占位符、删除操作、通过 UI 注册，或仅进行路由修复。

### 3.1-3.3 映射问题、编辑和遵循指令原则

将每个已确认的问题映射到 `.agent` 文件中的修复位置（描述、说明、操作、绑定、转换）。使用编辑工具进行针对性修改。遵循说明原则：明确命名操作、声明前置条件、范围严格、将角色保留在 `system:` 中。

### 3.4 防止回归

编辑前建立基线。进行最小化编辑。每次编辑后立即测试。每个发布周期修复一个。检查跨子代理依赖关系。测试相邻子代理。

### 3.5 应用修复

阅读 `.agent` 文件，使用编辑工具编辑并显示差异。保留文件现有的结构缩进以进行手术式编辑，避免创建混合风格文件。使用 4 个空格生成新文件。如果需要规范化，将整个结构缩进作为单独的更改进行转换并验证；不要部分转换制表符缩进文件。

### 3.6 验证、部署、发布、激活

```bash
# 验证（干运行）
sf agent validate authoring-bundle --json --api-name <AGENT_API_NAME> -o <org>

# 发布（编译 + 部署 + 激活）
sf agent publish authoring-bundle --json --api-name <AGENT_API_NAME> -o <org>
```

如果发布失败，使用部署 + 激活回退（注意：不完整 -- 不会将 `reasoning: actions:` 传播到实时元数据）。

### 3.7 验证

修复后运行第 2 阶段场景。检查跟踪以确认路由、接地、工具和变量正确。24-48 小时后，重新运行第 1 阶段与基线进行比较。

### 3.7b 安全重新验证（必需）

对修改后的 `.agent` 文件重新运行安全审查（`/agentforce-generate 的第 15 节`）。撤销引入 BLOCK 查找的任何更改。

### 3.8 更新测试中心测试用例

从测试中心 YAML 格式的已确认问题中创建回归测试用例。使用 `sf agent test create` 部署并验证所有之前损坏的场景通过。

---

## 代理健康监控 (AHM)

> 完整 AHM 警报程序 -- POST 模式、枚举、SDM/指标/代理发现、阈值、指标验证、故障排除：参见 `references/ahm-alerts.md`

作为反应性观察阶段的主动补充：**AHM 数据警报** 在代理指标（升级、偏转等）跨越阈值时触发。通过 `sf api request rest` 对 `tableau/dataAlerts` (`dataAlertType: "agenthealthmonitoring"`) 发起请求驱动 -- 目前还没有 `sf agent alert` 子命令。重用 **第 0 阶段** 用于 `dataspace`。根据参考文件首先构建 POST 正文并发现 SDM、其 `_mtc` 指标 ID 和代理过滤器值，然后：

```bash
# 列表/描述 -- 首先解析所有者 ID（必需）；单个警报 GET 返回 405 => 客户端端过滤列表
USER_ID=$(sf org display user --target-org <org> --json | python3 -c 'import sys,json;print(json.load(sys.stdin)["result"]["id"])')
sf api request rest "/services/data/v66.0/tableau/dataAlerts?ownerId=$USER_ID" -o <org>
# 创建 / PUT 替换本地 / 删除（204）。PUT 和 DELETE 由路径中的 $ALERT_ID 处理；PUT 接收完整的 POST 风格正文。正文根据参考文件放入 0600 mktemp 文件。
sf api request rest "/services/data/v66.0/tableau/dataAlerts" -X POST -H "Content-Type: application/json" -b "@$body" -o <org>
sf api request rest "/services/data/v66.0/tableau/dataAlerts/$ALERT_ID" -X PUT -H "Content-Type: application/json" -b "@$body" -o <org>
sf api request rest "/services/data/v66.0/tableau/dataAlerts/$ALERT_ID" -X DELETE -o <org> --include
# 通知需要头部 X-UNS-Type-Filter: all（否则仅自定义类型 => AHM 空为假 0）。报告状态 + 列表。
sf api request rest "/services/data/v66.0/connect/notifications/status" -H "X-UNS-Type-Filter: all" -o <org>
sf api request rest "/services/data/v66.0/connect/notifications"        -H "X-UNS-Type-Filter: all" -o <org>
# AHM 通知：类型=templatized_data_alert；没有每个警报端点。通过 alertId 在 targetPageRef.state.c__alertId（15/18 字符安全）属性，不是 metricId（冲突）。
```

**三个可能导致静默失败的陷阱，需引入任何警报工作：**
- **阈值是原始 0-1 比率**，不是显示百分比 -- 5% 是 `"0.05"`，`"1"` 表示 100%。
- **POST 字段名/大小写与 GET 不同** -- POST 使用 `utterance`（不是 `alertName`）和 PascalCase `type` 判定器，因此将 GET 响应复制回 POST 会失败。
- **通知需要 `X-UNS-Type-Filter: all`** -- 没有 `connect/notifications*` 返回仅自定义类型，因此 AHM 通知（类型 `templatized_data_alert`）返回为空；空列表是假阴性，不是“从未触发”。

---

## 参考文件

| 参考 | 内容 |
|---|---|
| `references/stdm-queries.md` | STDM 查询程序、Apex 服务部署、响应解析 |
| `references/ahm-alerts.md` | AHM 数据警报创建/列表/更新/删除、触发历史、SDM/指标/代理发现、阈值模式、指标验证 |
| `references/issue-classification.md` | 问题模式表、根本原因类别、结构分析检查 |
| `references/reproduce-reference.md` | 第 2 阶段预览程序、跟踪诊断、分类标准 |
| `references/improve-reference.md` | 第 3 阶段编辑、部署链、验证、安全、测试用例 |
| `references/stdm-schema.md` | DMO 字段模式、数据层次结构、质量说明、代理名称解析 |
