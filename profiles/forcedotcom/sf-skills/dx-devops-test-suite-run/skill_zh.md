# 运行 DevOps Center 测试套件

触发 DevOps Center 测试套件的执行并监视其完成。运行和轮询是同一操作的 halves — 在轮询之前必须先获取（或被分配）`runId`。

> **API 版本：** 所有 DevOps 测试系统调用都针对 Salesforce API **v67.0**（最低要求）。

**重要提示：** 所有 DevOps Center 数据都存储在 Salesforce 组织中 — **不是**本地存储库。始终使用 `sf data query` 或 `sf api request rest` 查询组织。

---

## 前置条件

在 `references/prerequisite-checks.md` 中运行前置条件检查 — 前置条件 1–4 **和** 前置条件 5（阶段），因为此技能针对特定阶段操作。您需要确认的 `doce-org-alias`、`pipelineId` 和 `stageId`。

## 需要的输入

| 输入 | 获取方式 |
|---|---|
| `pipelineId` | 前置条件 4（管道选择） |
| `stageId` | 前置条件 5（管道阶段确认） |
| `event` | 与用户确认：`Pre-Promote`、`Post-Promote` 或 `Review` |
| `testSuiteIds` | 从选择或推荐中确认的套件 ID |
| `doce-org-alias` | 前置条件 1 |

---

## 第 1 步 — 触发执行

### 确认关卡

**此调用会修改组织状态 — 在未获得明确用户确认的情况下不要继续。** 在调用 API 之前，显示：

> "我将使用以下配置运行测试：
> - 管道：`<pipelineName>`
> - 阶段：`<stageName>`
> - 事件：`<event>`
> - 套件：`<suiteName(s)>`
> - 组织：`<doce-org-alias>`
>
> 是否继续？"

在用户确认之前不要进行 API 调用。

### API 调用

```bash
sf api request rest \
  "/services/data/v67.0/connect/devopstesting/pipeline/<pipelineId>/stage/execute" \
  --method POST \
  --body '{
    "stageId": "<stageId>",
    "event": "<event>",
    "testSuiteIds": ["<suiteId1>", "<suiteId2>"]
  }' \
  --target-org <doce-org-alias>
```

| 字段 | 类型 | 描述 |
|---|---|---|
| `stageId` | string | 要在管道阶段上执行测试的 ID |
| `event` | string | `Pre-Promote`、`Post-Promote` 或 `Review` |
| `testSuiteIds` | string[] | 要执行的 一个或多个 测试套件 ID |

### 成功时

从响应中提取 `runId`（执行 ID）。通知用户：

> "正在 `<doce-org-alias>` 中运行测试。结果准备好时我会通知您。"

然后立即进行第 2 步（轮询）并使用 `runId`。

### 出错时

参见 `references/error-handling.md`。如果组织拒绝执行（例如 `environmentId: null`，或 `classIdList 为 null 或空 — 没有要执行的测试`），请读取实际错误，用平实的语言解释根本原因和所需修复，并干净地结束。**不要在循环中重试，也不要编造 `runId` 或结果。**

---

## 第 2 步 — 轮询直至完成

**无需确认：** 否 — 轮询是自动且只读的。

按提供者适当的间隔通过 `runId` 轮询执行记录。完整间隔、超时行为和轮询查询在 `references/polling-configuration.md` 中。

轮询循环的摘要（`runId` 是一个 `DevopsTestSuiteExecution` ID — 轮询该对象，而不是 `DevopsTestExecution`）：
- 每个间隔通过 `runId` 查询 `DevopsTestSuiteExecution` 的 `Status、Coverage、SuccessCount、FailureCount、QualityGateStatus`。
- `InProgress` → 等待并再次轮询。
- `Passed` / `Failed` → 直接显示 `Coverage`、`SuccessCount`、`FailureCount` 和 `QualityGateStatus`（无需原始 JSON）。如果 `FailureCount > 0`，请获取子 `DevopsTestExecution` 的失败行并传递给 **`dx-devops-test-failures-analyze`**。
- `Error` → 执行本身出错（不是测试失败）；用平实的语言显示 `ResultDetails`/`Message` 并提供重试或跳过选项。
- **超时** → 显示 `runId`，不要自动重试，等待用户指令。

---

## 重触发模式（重新运行质量关卡）

在因关卡失败而阻止发布且覆盖差距已解决时使用。**所有前置条件、关卡和重触发 API 调用都在 `references/retrigger-mode.md` 中。** 关键规则：除非最新的 `Coverage` 满足或超过 `DevopsQualityGateRule` 阈值，否则**不要**重触发。重触发返回新的 `runId` 后，将其传递给第 2 步（轮询）。

---

## 相关技能

- **`dx-devops-test-failures-analyze`** — 接收完成时的失败负载；还可以创建修复工作项。
- **`dx-devops-test-suite-assignments-configure`** — 推荐要运行的套件，或如果尚未链接，将套件分配给阶段。
- **`dx-devops-test-pipeline-configure`** — 配置新的质量关卡或阈值（此技能仅重新运行现有关卡）。
