# 配置 DevOps Center 管道测试基础设施

设置并配置 DevOps Center 管道的测试基础设施。此技能处理三个密切相关的“配置您的管道”操作，它们共享相同的组织上下文、先决条件和实体范围（管道级别）。选择与用户意图匹配的模式。

> **API 版本：** 所有 DevOps 测试系统调用都针对 Salesforce API **v67.0**（最低要求）。

**重要提示：** 所有 DevOps Center 数据（管道、阶段、提供程序、套件、门）都存储在 Salesforce 组织中——**不是**本地存储库中。切勿在文件系统中搜索管道配置。始终使用 `sf data query` 或 `sf api request rest` 查询组织。

---

## 第 1 步 — 先运行先决条件（始终）

在进行任何查询或系统调用之前，先在 `references/prerequisite-checks.md` 中运行先决条件检查。如果出现任何失败，请显示纯文本消息并停止——**切勿**向未验证的环境写入。

- **模式 A & B（提供程序配置/同步）：** 运行先决条件 1–4（组织登录、Agentforce DX 插件、DevOps Center 组织认证、管道标识）。先决条件 5（阶段）是**不**需要的——提供程序在管道级别进行配置。
- **模式 C（质量门）：** 运行先决条件 1–4 **并且**先决条件 5（阶段）。先决条件 5 仅提供 `DevopsPipelineStage`——目标 `DevopsTestSuiteStage` 记录 ID 在模式 C 的步骤 0（触发→套件阶段行）中单独解析。

传递解析后的 `doce-org-alias`、`pipelineId` 和（模式 C）`stageId` / `testSuiteStageId`。

---

## 第 2 步 — 选择模式

| 如果用户希望… | 模式 | 跟随 |
|---|---|---|
| 启用/设置/添加一个**尚未配置**的提供程序 | **A — 配置测试提供程序** | `references/configuring-test-provider.md` |
| 重新同步/刷新一个**已配置**的提供程序以拉取新套件 | **B — 同步已配置的提供程序** | `references/syncing-test-providers.md` |
| 在阶段上设置/配置质量门、覆盖率阈值或测试基准 | **C — 配置质量门** | `references/configuring-quality-gate.md` |

**区分 A 与 B（关键决策）：** 首先获取管道的提供程序（`GET .../testProviders?status=all`）——两个模式都从此开始。然后：

- 提供程序**可用**（未配置）→ **模式 A**（配置）。
- 提供程序**已配置**但套件过时/缺失 → **模式 B**（同步）。
- 提供程序**已配置**，但在将套件分配到阶段时用户看不到套件 → 这是一个**阶段分配差距，而不是配置差距**。重定向到 `dx-devops-test-suite-assignments-configure`。

**切勿**向已配置的提供程序的配置端点发送 POST 请求——它会创建重复的 `DevopsPipelineTestProvider` 记录。参见 `references/gotchas.md`。

---

## 第 3 步 — 确认门（每个模式都需要）

每个模式都会改变组织状态，并且**必须**在写入任何内容之前显示确认门。每个模式的参考文件都包含其确切的门措辞（模式 C 在门之前额外需要强制影响预览）。在用户给出肯定答复之前，不要调用任何写入 API。如果用户拒绝，则不写入并停止。

---

## 第 4 步 — 执行和报告

遵循所选参考文件以获取确切的 API 调用、成功消息和错误处理：

- `references/configuring-test-provider.md` — 模式 A
- `references/syncing-test-providers.md` — 模式 B
- `references/configuring-quality-gate.md` — 模式 C
- `references/error-handling.md` — 综合状态码→纯文本表格，适用于所有模式
- `references/gotchas.md` — 重复提供程序陷阱、API 名称差异、触发类型规则

**切勿**向用户暴露原始 API 错误、堆栈跟踪或 JSON 负载——始终翻译为纯文本。

---

## 相关技能

- **`dx-devops-test-suite-assignments-configure`** — 在配置/同步提供程序后，将它的套件分配或映射到阶段；还推荐提交要运行的套件。
- **`dx-devops-test-suite-run`** — 运行套件，或在修复满足阈值后重新触发质量门。
- **`dx-devops-test-failures-analyze`** — 解释运行中的失败，并可选择创建修复工作项。
