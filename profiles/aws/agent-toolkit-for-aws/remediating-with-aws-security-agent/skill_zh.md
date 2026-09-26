# 安全代理修复

AWS 安全代理是一个前沿代理，它按需对客户的应用程序进行渗透测试和代码审查，并报告经过验证的安全风险。这项技能将您从“我在 AWS 中发现了问题”转变为“我正在积极修复最重要的问题”，同时将敏感的漏洞细节排除在源代码控制之外。

流程分为四个阶段，并且它们的顺序很重要：

1. **发现**哪些扫描存在以及账户如何配置（运行中、只读）。
2. **导出**问题到一个本地 git 忽略的目录。
3. **分诊**问题到一个优先级高、人类可读的计划。
4. **修复**通过提供修复最高风险问题。

## 顺序和约束条件的重要性

问题包含可运行的攻击脚本、复现步骤、文件路径，有时还包括泄露的密钥或环境细节。如果这些内容出现在 Git 仓库中，客户可能会意外地提交并发布针对其生产系统的逐步攻击步骤。因此，不可协商的规则是：**问题仅写入 `.security-agent/`，并且在写入任何内容之前，该路径会被 git 忽略。**

## 阶段 1：发现扫描（运行中、只读）

了解账户中有什么内容。所有命令都是只读的 `list-*` 操作。

AWS 安全代理按层次结构组织数据——沿着它工作：

```
应用程序（账户 + 区域）
└── 代理空间        （设计审查、代码审查和渗透测试的工作空间）
    ├── 渗透测试 → 渗透测试任务 → 问题
    └── 代码审查      → 代码审查任务 → 问题
```

运行这些命令来定位自己并向用户展示存在的内容：

```bash
aws securityagent list-agent-spaces
aws securityagent list-pentests          --agent-space-id <as-...>
aws securityagent list-code-reviews      --agent-space-id <as-...>
aws securityagent list-pentest-jobs-for-pentest         --agent-space-id <as-...> --pentest-id <pt-...>
aws securityagent list-code-review-jobs-for-code-review --agent-space-id <as-...> --code-review-id <cr-...>
```

任务 `status` 是 `IN_PROGRESS`、`STOPPING`、`STOPPED`、`FAILED`、`COMPLETED` 之一。只有 `COMPLETED` 任务才有稳定、完整的问题集。

### 将代码库与扫描匹配，然后确认

代理空间、渗透测试和代码审查都是按其目标应用程序命名的。在要求用户从原始列表中选择之前，先对哪个扫描对应于*此*存储库做出明智的猜测——用户在代码库中工作是有原因的，相关的问题几乎总是针对当前应用程序。

使用廉价、高信号源从工作空间推断应用程序身份：

- 存储库/根目录名称和 Git 远程 URL (`git remote -v`)。
- 项目清单及其 `name`/`description` (`package.json`、`pyproject.toml`、`*.csproj`、`go.mod`、`Cargo.toml`)。
- README 标题、产品/指导文档以及任何明显的产品或公司名称。
- 独特的框架或域名，与扫描标题匹配。

将这些信号与代理空间/扫描名称（不区分大小写，允许部分和模糊匹配）进行比较。
然后**在导出之前始终确认**——展示你的最佳猜测和你的推理，并允许用户更正它：

> "这个存储库看起来像 **`<product>`** (来自 `<signal>`)，与 **<name>** 代理空间匹配。使用它，或者选择另一个？ [其他代理空间名称，...]"
>
> 如果在合理置信度下没有任何匹配项，就明确地告诉用户，并显示完整列表，而不是强迫错误的猜测。从不未经用户确认就从猜测的扫描中导出。

## 阶段 2：将问题导出到 `.security-agent/`（git 忽略）

使用 AWS CLI 命令拉取问题。将所有内容写入存储库中的 `.security-agent/`——从不写入聊天或 stdout——因为问题包含可运行的攻击脚本、复现步骤，有时还包括泄露的密钥。

### 1. 在拉取任何内容之前锁定输出目录

```bash
mkdir -p .security-agent
echo '*' > .security-agent/.gitignore
```

### 2. 解析最新的 COMPLETED 任务

您应该已经从阶段 1 获得了 `agentSpaceId` 和选择的扫描的 pentest/代码审查 ID。列出所选扫描的任务：

```bash
# 渗透测试任务：
aws securityagent list-pentest-jobs-for-pentest \
  --agent-space-id <as-...> --pentest-id <pt-...>

# 代码审查任务：
aws securityagent list-code-review-jobs-for-code-review \
  --agent-space-id <as-...> --code-review-id <cr-...>
```

通过传递前一个响应中的 `--next-token` 来分页，直到不存在。过滤任务摘要以 `status == "COMPLETED"`。如果没有 COMPLETED 任务，停止并告诉用户“未找到完成的任务。请等待任务完成或检查任务状态。”否则，选择具有最大 `createdAt` 时间戳的 COMPLETED 任务。

### 3. 列出问题摘要并按置信度过滤

```bash
# 渗透测试问题：
aws securityagent list-findings \
  --agent-space-id <as-...> --pentest-job-id <pj-...>

# 代码审查问题：
aws securityagent list-findings \
  --agent-space-id <as-...> --code-review-job-id <cj-...>
```

通过 `--next-token` 分页，直到耗尽。置信度值从最弱到最强：`FALSE_POSITIVE`、`UNCONFIRMED`、`LOW`、`MEDIUM`、`HIGH`。
**默认情况下仅保留 `HIGH` 和 `MEDIUM`。** 只有当用户明确要求时才放宽。

### 4. 批量获取 25 个问题的详细信息

`batch-get-findings` 每次调用最多接受 25 个 ID。将过滤后的问题 ID 分成 25 个一组：

```bash
aws securityagent batch-get-findings \
  --agent-space-id <as-...> \
  --finding-ids <fid-1> <fid-2> ... <fid-25>
```

在写入之前，为每个返回的问题标记其来源（`pentest` 或 `code-review`），以便在阶段 3 中的分诊可以区分它们。

### 5. 将问题写入 `.security-agent/`

按任务 ID 对问题进行分组。对于每个任务，将完整的 markdown 报告写入 `.security-agent/findings_<jobId>.md`，包含 API 返回的所有字段（findingId、name、description、riskLevel、riskType、confidence、status、codeLocations、remediationCode，以及任何其他字段）。不要遗漏任何字段。

### 边缘情况

- **没有代理空间、扫描或 COMPLETED 任务**——停止并将此内容显示给用户，而不是重试。
- **凭证或服务不可用**——使用 `aws sts get-caller-identity` 进行确认并检查区域（默认 `us-east-1`；安全代理是区域性的）。
- **不要将问题内容粘贴到聊天中**，除了简短标题和计数。详细信息属于 git 忽略的文件。

## 阶段 3：分诊到优先级计划

按风险排序，因为修复时间有限，未身份验证的 RCE 严重问题总是比低风险信息性问题更紧急。阅读从 `.security-agent/` 导出的 `findings_*.md` 文件并确定性地排序。

### 排序规则

按此复合键排序（较低的优先级，即更紧急的优先）：

1. **风险级别**，按此顺序：
   `CRITICAL` (0) → `HIGH` (1) → `MEDIUM` (2) → `LOW` (3) → `INFORMATIONAL` (4) →
   `UNKNOWN` / 缺失 (5)。
2. **风险分数**，最高优先。`riskScore` 是渗透测试问题中的一个数字字符串（例如 `"10.0"`），代码审查问题中通常不存在——将缺失视为最低可能的分数，因此它排在相同级别的已评分问题之后。
3. **置信度**，按此顺序：
   `HIGH` (0) → `MEDIUM` (1) → `LOW` (2) → `UNCONFIRMED` (3) → `FALSE_POSITIVE` (4)。

还计算所有问题的严重性计数摘要（例如 `2 CRITICAL · 5 HIGH · 3 MEDIUM`）作为报告标题。

### 拉取代码位置

对于每个问题，派生一个简短的 `location` 字符串：

- 如果 `filePath` 设置，则直接使用它。
- 否则，使用 `codeLocations[0]`。从 `filePath` 中删除扫描的沙盒前缀（包括该标记），以便路径是相对于存储库的；如果没有该标记，则回退到 basename。当存在时，附加 `:<lineStart>`。
- 如果两者都不可用（典型的某些渗透测试问题），则留空，并在影响行中描述受影响的端点或攻击链。

### 摘要格式

为用户提供一个紧凑的摘要：

```
## 安全代理分诊 — <代理空间名称>

<N> 个问题导出 (<P 个渗透测试, C 个代码审查>) · 置信度: <级别> · 严重性: <计数>

### 优先级顺序
1. [CRITICAL · score 10.0 · HIGH 置信度] <问题名称>
   - 类型: <riskType> · 来源: <pentest|code-review>
   - 位置: <文件:行或端点，如果存在>
   - 影响: <一行简明的语言总结>
2. [HIGH · ...] ...

### 推荐的修复顺序
<简短的理由: 为什么要先修复第一个和第三个——例如 "1 和 3 都是针对互联网端点的未身份验证 RCE；在修复存储 XSS 问题时先修复这些。">
```

如果有 10 个以上问题，详细显示前 N 个，并在底部按严重性总结其余部分。

### 不要从聊天中排除的内容

完整的 `description`、`reasoning` 和 `attackScript` 保留在 git 忽略的文件中——它们包含可运行的漏洞细节。在聊天摘要中，每个影响行保持为一行，用普通语言。代码审查问题通常包含 `filePath`/位置和建议的修复；指出这些，因为它们直接映射到存储库更改。渗透测试问题描述端点和攻击链；将它们映射到负责的代码。寻找相互印证的问题（一个渗透测试和一个代码审查标记了相同的根本原因）——这些是修复第一个问题的强信号。

## 阶段 4：提供修复

在展示分诊后，提供开始修复——不要在无声中开始编辑代码。

询问用户类似的内容：“想要我开始修复最高优先级的问题吗？我建议从 #1 (<name>) 开始。” 如果他们同意，按优先级从上到下工作：

1. 从 git 忽略的导出文件中读取问题详细信息（位置、描述、建议的修复）。
2. 打开受影响的文件并通过编辑器应用修复。
3. 每个修复报告一行：“在 `{filePath}:{lineStart}` 修复了 {name}。”

如果用户想处理多个问题，一次修复一个（或一组相关的问题），以便每个更改保持可审查，并按阶段 3 的优先级顺序进行。

## 注意和边缘情况

- **没有完成的任务**：扫描可能仍然是 `IN_PROGRESS`。告诉用户；提供稍后重新检查，而不是导出部分任务。
- **重新运行**：每次运行都会覆盖该任务 ID 的文件。目录可以安全删除；它只包含导出的副本，不包含源数据。
- **多个账户/区域**：问题按区域范围。如果用户期望结果但没有得到，请确认区域与安全代理配置的区域匹配。
- **数据处理**：将导出的问题视为敏感信息。它们是针对用户自己系统的已验证漏洞副本。
