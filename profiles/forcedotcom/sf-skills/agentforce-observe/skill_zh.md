# Agentforce 可观察性

使用会话跟踪数据和生活预览测试来改进 Agentforce 代理。

**三阶段工作流程：**
- **观察** -- 从数据云查询 STDM 会话（如果可用），或者运行测试套件 + 预览本地跟踪作为备用
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
- **代理文件路径**（可选） -- `.agent` 文件的路径，通常是 `force-app/main/default/aiAuthoringBundles/<AgentName>/<AgentName>.agent`。如果未提供，则自动检测。
- **会话 ID**（可选） -- 分析特定会话；如果不存在，则查询最后 7 天
- **回溯天数**（可选，默认为 7）
- **警报所有者用户**（可选，仅警报） -- 要列出/管理的用户警报；默认为当前用户

根据用户输入确定意图：

- **没有特定操作** -> 运行所有三个分析阶段：观察 -> 揭示问题 -> 询问用户是否要重现和/或改进
- **"analyze" / "sessions" / "what's wrong"** -> 仅阶段 1，然后建议下一步操作
- **"reproduce" / "test" / "preview"** -> 阶段 2（如果没有手头的问题，则先运行阶段 1）
- **"fix" / "improve" / "update"** -> 阶段 3（如果没有手头的问题，则先运行阶段 1）
- **"create alert" / "set up monitoring" / "alert me when"** -> AHM（创建）
- **"list alerts" / "show my alerts" / "update alert" / "delete alert"** -> AHM（列出 / 通过 PUT 更新 / 删除）
- **"get / list notifications" / "notifications for a specific alert" / "have my alerts fired" / "why isn't my alert firing"** -> AHM：使用标头 `X-UNS-Type-Filter: all` 获取通知，报告状态 + 列表；对于特定警报，按 `targetPageRef.state.c__alertId`（15/18 字符安全）过滤，而不是 metricId（与 Incidents 视图冲突 + metric 验证）

### 解析代理名称

在任何 STDM 查询之前，将用户提供的代理名称与组织进行解析，以获取确切的 `MasterLabel` 和 `DeveloperName`：

```bash
sf data query --json \
  --query "SELECT Id, MasterLabel, DeveloperName FROM GenAiPlannerDefinition WHERE MasterLabel LIKE '%<user-provided-name>%' OR DeveloperName LIKE '%<user-provided-name>%'" \
  -o <org>
```

- `MasterLabel` = STDM `findSessions` 和 Agent Builder UI 使用的显示名称（例如 "Order Service"）
- `DeveloperName` = 使用的 API 名称带有版本后缀，用于元数据（例如 "OrderService_v9"）
- `--api-name` 标志用于 `sf agent preview/activate/publish` 使用 `DeveloperName` **不带** `_vN` 后缀（例如 "OrderService"）

存储这些值：
- `AGENT_MASTER_LABEL` -- 用于 `findSessions()` 代理过滤器
- `AGENT_API_NAME` -- `DeveloperName` 不带 `_vN` 后缀，用于 `sf agent` CLI 命令
- `PLANNER_ID` -- 此代理的 Salesforce 记录 ID

### 定位 .agent 文件

**步骤 1 -- 本地搜索：**

```bash
find <project-root>/force-app/main/default/aiAuthoringBundles -name "*.agent" 2>/dev/null
```

如果用户提供了代理文件路径，则直接使用该路径。否则，搜索匹配 `AGENT_API_NAME` 的文件。

**步骤 2 -- 如果本地未找到，从组织检索：**

```bash
sf project retrieve start --json --metadata "AiAuthoringBundle:<AGENT_API_NAME>" -o <org>
```

> **已知错误：** `sf project retrieve start` 创建一个双重嵌套路径：`force-app/main/default/main/default/aiAuthoringBundles/...`。立即修复它：

```bash
if [ -d "force-app/main/default/main/default/aiAuthoringBundles" ]; then
  mkdir -p force-app/main/default/aiAuthoringBundles
  cp -r force-app/main/default/main/default/aiAuthoringBundles/* \
    force-app/main/default/aiAuthoringBundles/
  rm -rf force-app/main/default/main
fi
```

**步骤 3 -- 验证检索到的文件：**

读取 `.agent` 文件并验证它具有正确的代理脚本结构：
- `system:` 块带有 `instructions:`
- `config:` 块带有 `developer_name:`
- `start_agent` 或 `subagent` 块带有 `reasoning: instructions:`
- 每个子代理应具有不同的 `instructions:` 内容（子代理之间不应相同）

将解析的路径存储为 `AGENT_FILE` 用于阶段 3。

---

## 阶段 0：发现数据空间

在运行任何 STDM 查询之前，确定正确的 Data Cloud 数据空间 API 名称。

```bash
sf api request rest "/services/data/v63.0/ssot/data-spaces" -o <org>
```

注意：`sf api request rest` 是一个 beta 命令 -- 不要添加 `--json`（该标志不受支持并会导致错误）。

响应的形状是：
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
- 仅过滤 `status: "Active"` 条目。
- 如果存在一个活动的数据空间，则自动使用它并向用户确认： "使用数据空间：`<name>`"。
- 如果存在多个活动的数据空间，则显示列表（标签 + 名称）并询问用户要使用哪个。

将选择的 `name` 值存储为 `DATA_SPACE` 用于所有后续步骤。

### 前置条件检查：STDM DMOs

在部署辅助类（步骤 1.0）后，运行快速探测以验证 STDM 数据模型对象存在于数据云中：

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

**如果 `STDM_CHECK:FAIL`：** STDM 未激活。通知用户并切换到 **阶段 1-ALT**：

> STDM（会话跟踪数据模型）在此组织中不可用。要启用：设置 -> 数据云 -> 数据流并验证 "Agentforce 活动" 是否处于活动状态。**正在使用备用：测试套件 + 本地跟踪。**

**如果 `STDM_CHECK:OK`**，则继续到阶段 1（STDM 路径）。

---

## 阶段 1-ALT：无 STDM 观察（备用路径）

当 STDM 不可用时，使用测试套件和 `sf agent preview --authoring-bundle` 以及本地跟踪分析。

| 数据源 | 使用场景 | 优点 | 缺点 |
|---|---|---|---|
| STDM（阶段 1） | 历史生产分析 | 真实用户数据，数量 | 需要 Data Cloud，15 分钟延迟 |
| 测试套件 + 本地跟踪（阶段 1-ALT） | 开发迭代，没有 STDM 的组织 | 即时，完整的 LLM 提示，可变状态 | 仅预览，没有真实用户数据 |

### 1-ALT.1 运行现有测试套件（如果可用）

```bash
sf agent test list --json -o <org>
sf agent test run --json --api-name <TestSuiteName> --wait 10 --result-format json -o <org> | tee /tmp/test_run.json
JOB_ID=$(python3 -c "import json; print(json.load(open('/tmp/test_run.json'))['result']['runId'])")
sf agent test results --json --job-id "$JOB_ID" --result-format json -o <org>
```

### 1-ALT.2 从 .agent 文件派生测试话语（如果没有测试套件）

如果不存在测试套件，则从 `.agent` 文件派生话语：每个非入口子代理（从 `description:` 关键字），每个关键操作，每个护栏测试，每个多轮测试。

### 1-ALT.3 使用 `--authoring-bundle` 预览（本地跟踪）

运行每个测试话语通过预览以生成本地跟踪文件：

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

**直接回答（SMALL_TALK 模式）：** 如果 `start_agent` 跟踪显示 `SMALL_TALK` 接地并且可见的转换工具未调用，请将 "你是一个路由器。不要直接回答问题。" 添加到 `start_agent` 指令中。

### 1-ALT.5 分类并呈现

使用 `references/issue-classification.md` 中的类别对问题进行分类。在呈现结果后，自动继续分析代理配置证据。

---

## 阶段 1：观察 -- 查询 STDM

> 完整 STDM 查询细节，Apex 服务部署和响应解析：见 `references/stdm-queries.md`

### 1.0 部署辅助类（每个组织一次）

将 `AgentforceOptimizeService` Apex 类部署到组织中。首先检查是否已部署：

```bash
sf data query --json --query "SELECT Id, Name FROM ApexClass WHERE Name = 'AgentforceOptimizeService'" -o <org>
```

如果未部署，则从技能目录复制并部署。有关完整步骤，请参阅 `references/stdm-queries.md`。

### 1.1 查找会话

使用 `findSessions()` 查询最近的会话。解析 Apex 调试日志中的 `DEBUG|STDM_RESULT:`。如果 `findSessions` 返回空，则切换到阶段 1-ALT。

### 1.2 获取对话详细信息

使用 `getMultipleConversationDetails()` 最多 5 个会话（按最新顺序）。返回按回合的数据，包括消息、步骤、主题和操作结果。

### 1.2b 获取 LLM 提示/响应（可选）

当检测到低遵循度时，使用 `getLlmStepDetails()` 获取实际的 LLM 提示和响应。

### 1.2c 获取聚合指标（推荐的第一步）

使用 `getAggregatedMetrics()` 获取高级别的健康仪表板：会话速率、顶级意图、质量分布、RAG 平均值。

### 1.2d 获取时刻洞察（每个会话的详细信息）

使用 `getMomentInsights()` 获取每个会话的意图摘要、质量分数（1-5）和检索器指标。

### 1.2e 运行可观察性查询（RAG 深入分析）

使用 `runObservabilityQuery()` 进行有针对性的 RAG 分析：知识差距、幻觉、检索质量、答案相关性、排行榜。

### 1.3 重建对话

为每个会话从 `ConversationData` JSON 渲染按回合的时间线。

### 1.4 识别问题

> 完整问题模式表和分类类别：见 `references/issue-classification.md`

检查每个会话是否存在：操作错误、子代理误路由、缺少操作、错误输入、变量捕获失败、没有转换、慢操作、低遵循度、放弃会话、死子代理、发布漂移、死中心反模式、入口直接回答，以及安全问题。

**语音代理（具有 `modality voice:` 块）：** 还检查：
- 响应冗长 — 任何超过 3 句话的代理响应（语音 UX 反模式；也是一个静默/提示计时器触发器）
- 响应中的视觉格式 — 不在语音中显示的列表、链接、Markdown
- 缺少确认模式 — 修改数据的操作没有重复关键细节
- 缺少语音接线 — 语音代理缺少链接变量 `@VoiceCall.Id` 或 `connection customer_web_client:` 块，或者有人添加了一个不存在的 `connection voice:` 块
- **延迟反模式** — 将跟踪步骤持续时间与 `/agentforce-generate` [`references/voice-latency-heuristics.md`](../agentforce-generate/references/voice-latency-heuristics.md) 中字段验证的模式进行交叉引用：同步写入实时呼叫路径、返回原始的庞大检索、链式外部调用、过度分解的子代理路由、以及没有确认短语的慢操作。延迟修复是**仅标记**的，除非纯粹是指导性的（确认短语、回合长度、口语形式规则）。
- **TTS 杂音 / 缺少口语形式规则** — 操作输出或响应在未提供口语形式指令规则的情况下显示价格、电话号码或 ID。

优先级：P1 = 操作错误、误路由、低遵循度；P2 = 缺少操作、变量错误、知识差距；P3 = 性能、放弃会话、语音 UX 问题、语音延迟反模式。

### 1.5 呈现发现和代理配置证据

呈现分析的会话、按根本原因类别分组的问题，以及提升估计。然后自动继续分析 `.agent` 文件以确认根本原因。

> 完整结构分析检查、交叉参考程序、发布漂移检测：见 `references/issue-classification.md`

从组织中检索 `.agent` 文件，运行自动检查（子代理计数与操作块、死中心检测、孤儿操作、跨子代理变量依赖），并将 STDM 症状与文件结构进行交叉参考。

---

## 阶段 2：重现 -- 实时预览

> 完整预览程序、跟踪诊断命令和分类标准：见 `references/reproduce-reference.md`

为阶段 1 确认的每个问题构建一个测试场景。通过 `sf agent preview` 运行每个场景，使用 `--authoring-bundle`（生成本地跟踪）。运行每个场景**3 次**并分类：

| 判定 | 标准 |
|---|---|
| `[确认]` | 在 3/3 运行中相同失败 |
| `[间歇性]` | 在 1-2 个 3 运行中失败 |
| `[未重现]` | 在 3/3 运行中通过 |

只有 `[确认]` 和 `[间歇性]` 的问题继续到阶段 3。

**关键命令：**

```bash
sf agent preview start --json --authoring-bundle <Name> --simulate-actions -o <org>
sf agent preview send --json --session-id "$SID" --utterance "<text>" --authoring-bundle <Name> -o <org>
sf agent preview end --json --session-id "$SID" --authoring-bundle <Name> -o <org>
```

从 Salesforce 项目目录运行这些命令。`start` 需要一个带有 `--authoring-bundle` 的操作模式（`--simulate-actions` 或 `--use-live-actions`）；该标志会被 `send` 和 `end` 拒绝。

**跟踪位置：** `.sfdx/agents/{Name}/sessions/{sessionId}/traces/{planId}.json`

---

## 阶段 3：改进 -- 直接编辑 .agent 文件

> 预飞行检查、修复映射、指令原则、回归预防、发布链、验证、安全重新验证和测试用例创建的完整程序：见 `references/improve-reference.md`

### 3.0 预飞行

在编辑之前验证所有操作目标是否存在并且已在组织中注册。如果目标缺失，则呈现选项：部署占位符、删除操作、通过 UI 注册，或继续仅路由修复。

### 3.1-3.3 映射问题、编辑和遵循指令原则

将每个确认的问题映射到 `.agent` 文件中的修复位置（描述、指令、操作、绑定、转换）。使用编辑工具进行有针对性的更改。遵循指令原则：明确命名操作，声明先决条件，范围紧密，仅在 `system:` 中保持角色。

### 3.4 回归预防

在编辑之前建立基线。进行最小化编辑。立即在每次编辑后测试。每个发布周期一个修复。检查跨子代理依赖关系。测试相邻子代理。

### 3.5 应用修复

读取 `.agent` 文件，使用编辑工具编辑，并显示差异。保留文件现有的结构缩进以进行外科手术式编辑，这样你不会创建一个混合风格的文件。使用 4 个空格生成新文件。如果需要规范化，则将整个结构缩进作为单独的更改进行转换并验证；不要部分转换一个制表符缩进的文件。

### 3.6 验证、发布、激活

```bash
# 验证（干运行）
sf agent validate authoring-bundle --json --api-name <AGENT_API_NAME> -o <org>

# 发布（编译 + 部署 + 激活）
sf agent publish authoring-bundle --json --api-name <AGENT_API_NAME> -o <org>
```

如果发布失败，则使用部署 + 激活备用方案（注意：不完整 -- 不传播 `reasoning: actions:` 到实时元数据）。

### 3.7 验证

运行修复后的阶段 2 场景。检查跟踪以验证正确的路由、接地、工具和变量。在 24-48 小时后，重新运行阶段 1 以与基线进行比较。

### 3.7b 安全重新验证（必需）

在修改的 `.agent` 文件上重新运行安全审查（`/agentforce-generate` 的第 15 节）。将引入 BLOCK 找到的任何更改还原。

### 3.8 更新测试中心测试用例

从测试中心中的确认问题创建回归测试用例，格式为测试中心 YAML。使用 `sf agent test create` 部署，并验证所有之前损坏的场景都通过。

---

## 代理健康监控 (AHM)

> 完整 AHM 警报程序 -- POST 模式、枚举、SDM/metric/代理发现、阈值、metric 验证：见 `references/ahm-alerts.md`

作为反应性观察阶段的主动补充：**AHM 数据警报** 在代理指标（升级、转嫁等）跨越阈值时触发。通过 `sf api request rest` 对 `tableau/dataAlerts` (`dataAlertType: "agenthealthmonitoring"`) 进行驱动——目前还没有 `sf agent alert` 子命令。首先构建 POST 正文并发现 SDM、其 `_mtc` metric ID 和代理过滤器值**按照参考文件**，然后：

```bash
# 列出/描述 -- 首先解析所有者 ID（必需）；单个警报 GET 返回 405 => 客户端端侧过滤
USER_ID=$(sf org display user --target-org <org> --json | python3 -c 'import sys,json;print(json.load(sys.stdin)["result"]["id"])')
sf api request rest "/services/data/v66.0/tableau/dataAlerts?ownerId=$USER_ID" -o <org>
# 创建 / PUT 更新（原地更新）/ 删除 (204)。PUT & DELETE 都通过路径中的 $ALERT_ID 处理；PUT 接受完整的 POST 风格正文。正文参考文件到一个 0600 mktemp 文件。
sf api request rest "/services/data/v66.0/tableau/dataAlerts" -X POST -H "Content-Type: application/json" -b "@$body" -o <org>
sf api request rest "/services/data/v66.0/tableau/dataAlerts/$ALERT_ID" -X PUT -H "Content-Type: application/json" -b "@$body" -o <org>
sf api request rest "/services/data/v66.0/tableau/dataAlerts/$ALERT_ID" -X DELETE -o <org> --include
# 通知需要标头 X-UNS-Type-Filter: all（否则仅自定义类型 => AHM 空白 = 假阴性）. 报告状态 + 列表。
sf api request rest "/services/data/v66.0/connect/notifications/status" -H "X-UNS-Type-Filter: all" -o <org>
sf api request rest "/services/data/v66.0/connect/notifications"        -H "X-UNS-Type-Filter: all" -o <org>
# AHM 通知：类型=templatized_data_alert; 没有每个警报端点。通过 alertId 在 targetPageRef.state.c__alertId（15/18 字符安全）属性，而不是 metricId（冲突）。

**三个静默失败陷阱：**
- **阈值是原始 0-1 比率**，不是显示百分比——5% 是 `"0.05"`，`"1"` 表示 100%
- **POST 字段名称/大小写与 GET 不同**——POST 使用 `utterance`（不是 `alertName`）和 PascalCase `type` 判别符，因此将 GET 响应复制回 POST 会失败。
- **通知需要 `X-UNS-Type-Filter: all`**——没有它 `connect/notifications*` 返回自定义类型，所以 AHM 通知（类型 `templatized_data_alert`）会返回空；空列表是假阴性，不是 "从未触发"。
