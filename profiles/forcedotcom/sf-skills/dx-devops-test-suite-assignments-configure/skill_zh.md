# 配置 DevOps Center Suite 分配

推荐针对变更应运行的现有测试套件，并管理套件如何分配和映射到流水线阶段。这些操作共享相同的套件-阶段元数据：推荐会显示相关套件并标记空白，而这些空白会直接进入分配。

> **API 版本：** 所有 DevOps 测试系统调用都针对 Salesforce API **v67.0**（最低要求）。

**重要提示：** 所有 DevOps Center 数据都存储在 Salesforce 组织中——**不是**本地存储库。切勿在文件系统中搜索套件配置。始终使用 `sf data query` 或 `sf api request rest` 查询组织。

---

## 第 1 步 — 先运行先决条件（始终）

在执行任何查询或系统调用之前，先在 `references/prerequisite-checks.md` 中运行先决条件检查。出现任何失败时，显示纯文本消息并停止。

- **模式 A（推荐）：** 先决条件 1–4（组织登录、插件、DevOps Center 组织认证、识别流水线）。无需指定阶段——推荐会读取流水线级别的 Review 触发器。
- **模式 B–D（分配/映射/类）：** 先决条件 1–4 **以及** 先决条件 5（阶段）。需要 `doce-org-alias`、`pipelineId` 和 `stageId`。

---

## 第 2 步 — 选择模式

| 如果用户希望…… | 模式 | 跟随 |
|---|---|---|
| 了解提交/差异应运行**哪些套件**，或哪些内容覆盖了他们的变更 | **A — 推荐套件** | `references/recommendation-logic.md` |
| 将**一个**套件一次性分配到阶段 | **B — 分配单个套件** | `references/suite-assignment-modes.md` |
| 将多个套件**批量映射**到阶段作为测试策略 | **C — 映射多个套件** | `references/suite-assignment-modes.md` |
| 在套件分配中**添加/删除**单个测试类 | **D — 添加/删除类** | `references/suite-assignment-modes.md` |

模式 A 是纯粹的推理（无写入）。模式 B–D 通过相同的 `testSuiteStages` 端点（`references/api-endpoint.md`）修改组织状态。

**A 如何为 B–D 提供输入：** 当推荐标记一个相关的套件且**未分配**到阶段时，该空白是模式 B/C 的输入。当它标记一个*新方法且无套件覆盖*时，直接引导开发人员手动编写测试（v1 限制——此处永不建议生成测试）。

---

## 第 3 步 — 管理与确认（模式 B–D）

模式 B–D **必须**在写入前确认：

- **模式 B** — 单一确认提示，命名套件、阶段和事件。
- **模式 C** — 确认门禁前的**强制影响预览表**（套件 / 阶段 / 事件 / 操作）。
- **模式 D** — 确认前重新显示最终测试列表。**拒绝的测试必须从负载中排除。** 如果在审核期间修改了测试，确认前重新显示最终列表，然后请求确认。未经明确批准，切勿调用 API。

用户给出肯定答复前，不要调用 API。如果用户拒绝，停止且不写入。每个门禁的完整措辞在 `references/suite-assignment-modes.md` 中。

模式 A（推荐）不写入，无需确认门禁。

---

## 第 4 步 — 执行与报告

遵循所选参考文件：

- `references/recommendation-logic.md` — 模式 A：差异分类、提供者匹配、排序、空白标记、输出格式。
- `references/suite-assignment-modes.md` — 模式 B–D：输入、确认措辞、成功消息。
- `references/api-endpoint.md` — 共享的 `testSuiteStages` POST 负载模式（模式 B–D）。
- `references/error-handling.md` — 状态码 → 纯文本表。

切勿向用户暴露原始 API 错误、堆栈跟踪或 JSON。

---

## 相关技能

- **`dx-devops-test-pipeline-configure`** — 如果您要分配的套件尚未出现，请配置或重新同步提供者；还配置映射后阶段的品质门禁。
- **`dx-devops-test-suite-run`** — 在阶段上执行推荐的/分配的套件。
- **`dx-devops-test-failures-analyze`** — 分析套件内测试的失败情况及改进建议。
