# Agentforce 可观察性

使用会话跟踪数据和生活预览测试来改进 Agentforce 代理。

**三阶段工作流程：**
- **观察** -- 从 Data Cloud 查询 STDM 会话（如果可用），或运行测试套件 + 预览作为备用方案使用本地跟踪
- **重现** -- 使用 `sf agent preview` 实时模拟有问题的对话
- **改进** -- 直接编辑 `.agent` 文件，验证，发布，验证

---

## 平台说明

- 以下 Shell 示例使用 bash 语法。在 Windows 上，请使用 PowerShell 等效方案或 Git Bash。
- 在 Windows 上将 `python3` 替换为 `python`。
- 将 `/tmp/` 替换为 `$env:TEMP\`（PowerShell）或 `%TEMP%\`（cmd）。
- 如果未安装 jq，请将 `jq` 替换为 `python -c "import json,sys; ..."`。

---

## 路由

开始之前收集这些输入：

- **组织别名**（必需）
- **代理 API 名称**（必需用于预览和部署；如果未提供，请询问）
- **代理文件路径**（可选）-- `.agent` 文件的路径，通常为 `force-app/main/default/aiAuthoringBundles/<AgentName>/<AgentName>.agent`。如果未提供，则自动检测。
- **会话 ID**（可选）-- 分析特定会话；如果不存在，则查询过去 7 天的数据
- **回溯天数**（可选，默认为 7）

根据用户输入确定意图：

- **没有特定操作** -> 运行所有三个阶段：观察 -> 揭示问题 -> 询问用户是否要重现和/或改进
- **"analyze" / "sessions" / "what's wrong"** -> 仅第一阶段，然后建议下一步操作
- **"reproduce" / "test" / "preview"** -> 第二阶段（如果手头没有问题，则先运行第一阶段）
- **"fix" / "improve" / "update"** -> 第三阶段（如果手头没有问题，则先运行第一阶段）

### 解析代理名称

在任何 STDM 查询之前，将用户提供的代理名称与组织进行解析，以获取确切的 `MasterLabel` 和 `DeveloperName`：

```bash
sf data query --json \
  --query "SELECT Id, MasterLabel, DeveloperName FROM GenAiPlannerDefinition WHERE MasterLabel LIKE '%<user-provided-name>%' OR DeveloperName LIKE '%<user-provided-name>%'" \
  -o <org>
```

- `MasterLabel` = STDM `findSessions` 和 Agent Builder UI 使用的显示名称（例如 "Order Service"）
- `DeveloperName` = 在元数据中使用的 API 名称带版本后缀（例如 "OrderService_v9"）
- `--api-name` 标志用于 `sf agent preview/activate/publish` 的 `DeveloperName` **不带** `_vN` 后缀（例如 "OrderService"）

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

**步骤 2 -- 如果本地未找到，从组织中检索：**

```bash
sf project retrieve start --json --metadata "AiAuthoringBundle:<AGENT_API_NAME>" -o <org>
```

> **已知错误：** `sf project retrieve start` 创建一个双重嵌套路径：`force-app/main/default/main/default/aiAuthoringBundles/...`。立即修复检索后的路径：

```bash
if [ -d "force-app/main/default/main/default/aiAuthoringBundles" ]; then
  mkdir -p force-app/main/default/aiAuthoringBundles
  cp -r force-app/main/default/main/default/aiAuthoringBundles/* \
    force-app/main/default/aiAuthoringBundles/
  rm -rf force-app/main/default/main
fi
```

**步骤 3 -- 验证检索到的文件：**

读取 `.agent` 文件并验证其具有正确的代理脚本结构：
- `system:` 块带有 `instructions:`
- `config:` 块带有 `developer_name:`
- `start_agent` 或 `subagent` 块带有 `reasoning: instructions:`
- 每个子代理应具有不同的 `instructions:` 内容（子代理之间不应相同）

将解析的路径存储为 `AGENT_FILE` 以供第三阶段使用。

---

## 第一阶段 0：发现数据空间

在运行任何 STDM 查询之前，确定正确的 Data Cloud 数据空间 API 名称。

```bash
sf api request rest "/services/data/v63.0/ssot/data-spaces" -o <org>
```

注意：`sf api request rest` 是一个 beta 命令 -- 不要添加 `--json`（该标志不受支持，并会导致错误）。

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
- 过滤仅 `status: "Active"` 的条目。
- 如果存在一个活动的数据空间，则自动使用它并确认给用户： "使用数据空间: `<name>`"。
- 如果存在多个活动的数据空间，则显示列表（标签 + 名称）并询问用户要使用哪个。

将选择的 `name` 值存储为 `DATA_SPACE` 以供后续所有步骤使用。

### 先决条件检查：STDM DMO

在部署辅助类（步骤 1.0）后，运行快速探测以验证 STDM 数据模型对象是否存在于 Data Cloud 中：

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

> 此组织中不可用 STDM（会话跟踪数据模型）。要启用：设置 -> Data Cloud -> 数据流并验证 "Agentforce 活动" 是否处于活动状态。**使用备用方案：测试套件 + 本地跟踪。**

**如果 `STDM_CHECK:OK`**，则继续第一阶段（STDM 路径）。

---

## 第一阶段-ALT：无 STDM 的观察（备用路径）

当 STDM 不可用时，使用测试套件和 `sf agent preview --authoring-bundle` 以及本地跟踪分析。

| 数据源 | 使用场景 | 优点 | 缺点 |
|---|---|---|---|
| STDM（第一阶段） | 历史生产分析 | 真实用户数据，大量 | 需要 Data Cloud，15 分钟延迟 |
| 测试套件 + 本地跟踪（第一阶段-ALT） | 开发迭代，没有 STDM 的组织 | 即时，完整的 LLM 提示，可变状态 | 仅预览，没有真实用户数据 |

### 1-ALT.1 运行现有测试套件（如果可用）

```bash
sf agent test list --json -o <org>
sf agent test run --json --api-name <TestSuiteName> --wait 10 --result-format json -o <org> | tee /tmp/test_run.json
JOB_ID=$(python3 -c "import json; print(json.load(open('/tmp/test_run.json'))['result']['runId'])")
sf agent test results --json --job-id "$JOB_ID" --result-format json -o <org>
```

### 1-ALT.2 从 .agent 文件派生测试语句（如果没有测试套件）

如果不存在测试套件，则从 `.agent` 文件派生语句：每个非入口子代理一个（从 `description:` 关键字），每个关键操作一个，一个守卫测试，一个多轮测试。

### 1-ALT.3 使用 `--authoring-bundle` 进行预览（本地跟踪）

将每个测试语句通过预览以生成本地跟踪文件：

```bash
sf agent preview start --json --authoring-bundle <BundleName> -o <org> | tee /tmp/preview_start.json
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

**DefaultTopic 跟踪怪癖：** 使用 `--authoring-bundle` 时，即使路由正常，根 `.topic` 字段也经常显示为 `"DefaultTopic"`。始终使用 `NodeEntryStateStep.data.agent_name` 获取真实的子代理链。

**直接回答（SMALL_TALK 模式）：** 如果 `start_agent` 跟踪显示 `SMALL_TALK` 接地并且可见的转换工具未调用，请将 "您是一个路由器。不要直接回答问题。" 添加到 `start_agent` 指令中。

### 1-ALT.5 分类并呈现

使用 `references/issue-classification.md` 中的类别对问题进行分类。在呈现结果后，自动继续分析 `.agent` 文件以确认根本原因。

> 完整的结构分析检查、交叉参考程序和发布漂移检测：见 `references/issue-classification.md`

从组织中检索 `.agent` 文件，运行自动检查（子代理计数与操作块、死中心检测、孤儿操作、跨子代理变量依赖），并将 STDM 症状与文件结构进行交叉参考。

---

## 第一阶段：观察 -- 查询 STDM

> 完整的 STDM 查询细节、Apex 服务部署和响应解析：见 `references/stdm-queries.md`

### 1.0 部署辅助类（每个组织一次）

将 `AgentforceOptimizeService` Apex 类部署到组织中。首先检查是否已部署：

```bash
sf data query --json --query "SELECT Id, Name FROM ApexClass WHERE Name = 'AgentforceOptimizeService'" -o <org>
```

如果未部署，则从技能目录复制并部署。有关完整步骤，请参阅 `references/stdm-queries.md`。

### 1.1 查找会话

使用 `findSessions()` 查询最近的会话。解析 Apex 调试日志中的 `DEBUG|STDM_RESULT:`。如果 `findSessions` 返回空，则切换到第一阶段-ALT。

### 1.2 获取对话详细信息

使用 `getMultipleConversationDetails()` 获取最多 5 个会话（按最新顺序）。返回按回合的数据，包括消息、步骤、主题和操作结果。

### 1.2b 获取 LLM 提示/响应（可选）

当检测到低遵循度时，使用 `getLlmStepDetails()` 获取实际的 LLM 提示和响应。

### 1.2c 获取聚合指标（推荐的第一步）

使用 `getAggregatedMetrics()` 获取高级别的健康仪表板：会话速率、顶级意图、质量分布、RAG 平均值。

### 1.2d 获取时刻洞察（每个会话的详细信息）

使用 `getMomentInsights()` 获取每个会话的意图摘要、质量分数（1-5）和检索器指标。

### 1.2e 运行可观察性查询（RAG 深入分析）

使用 `runObservabilityQuery()` 进行有针对性的 RAG 分析：知识差距、幻觉、检索质量、答案相关性、排行榜。

### 1.3 重建对话

为每个会话渲染按回合的时间线。

### 1.4 识别问题

> 完整的问题模式表和分类类别：见 `references/issue-classification.md`

检查每个会话是否存在：操作错误、子代理误路由、缺失操作、错误输入、变量捕获失败、无转换、慢操作、低遵循度、放弃会话、死子代理、发布漂移、死中心反模式、入口直接回答以及安全问题。

优先级：P1 = 操作错误、误路由、低遵循度；P2 = 缺失操作、变量错误、知识差距；P3 = 性能、放弃会话。

### 1.5 呈现结果和代理配置证据

呈现分析的会话、按根本原因类别分组的问题，以及提升估计。然后自动继续分析 `.agent` 文件以确认根本原因。

> 完整的结构分析检查、交叉参考程序和发布漂移检测：见 `references/issue-classification.md`

从组织中检索 `.agent` 文件，运行自动检查（子代理计数与操作块、死中心检测、孤儿操作、跨子代理变量依赖），并将 STDM 症状与文件结构进行交叉参考。

---

## 第二阶段：重现 -- 实时预览

> 完整的预览程序、跟踪诊断命令和分类标准：见 `references/reproduce-reference.md`

为第一阶段确认的问题构建一个测试场景。通过 `sf agent preview` 运行每个场景，使用 `--authoring-bundle`（生成本地跟踪）。运行每个场景 **3 次** 并分类：

| 判定 | 标准 |
|---|---|
| `[CONFIRMED]` | 在 3/3 次运行中相同失败 |
| `[INTERMITTENT]` | 在 1-2 次运行中失败 |
| `[NOT REPRODUCED]` | 在 3/3 次运行中通过 |

只有 `[CONFIRMED]` 和 `[INTERMITTENT]` 的问题会继续到第三阶段。

**关键命令：**

```bash
sf agent preview start --json --authoring-bundle <Name> -o <org>
sf agent preview send --json --session-id "$SID" --utterance "<text>" --authoring-bundle <Name> -o <org>
sf agent preview end --json --session-id "$SID" --authoring-bundle <Name> -o <org>
```

**跟踪位置：** `.sfdx/agents/{Name}/sessions/{sessionId}/traces/{planId}.json`

---

## 第三阶段：改进 -- 直接编辑 .agent 文件

> 预飞行检查、修复映射、指令原则、回归预防、发布链、验证、安全重新验证和测试用例创建的完整程序：见 `references/improve-reference.md`

### 3.0 预飞行

在编辑之前验证所有操作目标是否存在并且已在组织中注册。如果目标缺失，则呈现选项：部署占位符、删除操作、通过 UI 注册，或继续仅路由修复。

### 3.1-3.3 映射问题、编辑和遵循指令原则

将每个确认的问题映射到 `.agent` 文件中的修复位置（描述、指令、操作、绑定、转换）。使用编辑工具进行有针对性的更改。遵循指令原则：明确命名操作，声明先决条件，范围紧密，仅在 `system:` 中保持角色。

### 3.4 回归预防

在编辑之前建立基线。进行最小化编辑。编辑后立即测试。每个发布周期一个修复。检查跨子代理依赖。测试相邻子代理。

### 3.5 应用修复

读取 `.agent` 文件，使用编辑工具（制表符用于缩进），显示差异。

### 3.6 验证、发布、发布、激活

```bash
# 验证（干运行）
sf agent validate authoring-bundle --json --api-name <AGENT_API_NAME> -o <org>

# 发布（编译 + 部署 + 激活）
sf agent publish authoring-bundle --json --api-name <AGENT_API_NAME> -o <org>
```

如果发布失败，请使用部署 + 激活回退（注意：不完整 -- 不会将 `reasoning: actions:` 传播到实时元数据）。

### 3.7 验证

运行修复后的第二阶段场景。检查跟踪以验证正确的路由、接地、工具和变量。24-48 小时后，重新运行第一阶段以与基线进行比较。

### 3.7b 安全重新验证（必需）

对修改后的 `.agent` 文件重新运行安全审查（`/developing-agentforce` 的第 15 节）。撤销引入 BLOCK 找到的任何更改。

### 3.8 更新测试中心测试用例

从测试中心中确认的问题创建回归测试用例（以测试中心 YAML 格式）。使用 `sf agent test create` 部署并验证所有之前损坏的场景通过。

---

## 参考文件

| 参考 | 内容 |
|---|---|
| `references/stdm-queries.md` | STDM 查询程序、Apex 服务部署、响应解析 |
| `references/issue-classification.md` | 问题模式表、根本原因类别、结构分析检查 |
| `references/reproduce-reference.md` | 第二阶段预览程序、跟踪诊断、分类标准 |
| `references/improve-reference.md` | 第三阶段编辑、发布链、验证、安全、测试用例 |
| `references/stdm-schema.md` | DMO 字段模式、数据层次结构、质量注释、代理名称解析 |
