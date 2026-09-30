---
name: k6-test-maintenance
description: 维护和改进现有的k6测试脚本。包括基于趋势数据的阈值收紧、k6版本之间的迁移、在底层服务变更时自动修复测试、为简洁性进行重构，以及根据文档中的最佳实践审计脚本。当用户要求修复失败的k6测试、收紧阈值、将脚本迁移到新的k6版本、重构测试、在服务变更后更新脚本，或使用最佳实践改进脚本时使用。在以下短语触发：如"修复我的k6测试"、"收紧我的阈值"、"迁移到k6 v2"、"更新我的测试脚本"、"重构这个k6测试"、"部署后我的测试失败了"、"将最佳实践应用于我的脚本"、"使我的k6测试现代化"、"服务变更导致我的测试失效"。此外，当其他技能（k6-trend-analysis或k6-cloud-investigate-test）推荐编辑脚本时也会触发。
---

# k6 测试维护

维护、修复和改进现有的 k6 测试脚本。五项维护任务，每个任务都有详细的步骤说明，请参考 [`references/workflows.md`](references/workflows.md)：

1. **阈值收紧** -- 根据观察到的指标调整阈值
2. **版本迁移** -- 更新脚本以适应新的 k6 版本
3. **服务变更适配** -- 在底层服务变更时修复测试
4. **重构** -- 清理和现代化测试代码
5. **最佳实践审核** -- 对照当前的 k6 最佳实践检查脚本

## 核心原则：行为感知变更控制

根据是否改变测试的运行时行为来分类每项建议的变更：

- **语法性**（行为未改变）：k6 运行时产生相同的指标、通过/失败结果和端点。例如：重命名变量、`let` → `const`、移除未使用的导入、更新注释、重新格式化。**直接应用。**
- **行为性**（行为不同）：任何影响指标、通过/失败、时间、请求目标或负载形状的变更。例如：阈值值变更、添加 `sleep()`、端点 URL 更新、检查重写、场景变更、新阈值。**始终以差异形式呈现，附带理由并要求确认。**

"行为性"的阈值是故意设置较低的。如有疑问，将其视为行为性并询问——看似微不足道的阈值变更可能级联到 CI 闸、SLO 计算和告警。

## 依赖项

- **`k6-manage`** -- 安全地获取和编辑 GCk6 托管的脚本（§5：GET、备份、编辑、验证、PUT、sha256 验证）。在触摸任何云托管脚本之前，请先阅读它。
- **`gcx`** -- Grafana Cloud API 的唯一访问工具。
- **mcp-k6** 工具 -- `validate_script` 和 `get_documentation`。先检查可用性；如果缺失，则回退到 `k6 x docs`。
- **`k6 x docs`** CLI -- 当 mcp-k6 未配置时的文档查询。
- **`k6` CLI** -- 本地验证 (`k6 inspect`, `k6 run`)。

## 验证循环（每次编辑）

每个工作流都会生成一个修改后的脚本。切勿提交或 PUT 未验证的脚本——运行此循环，修复并重新运行，直到通过：

1. **解析检查**：`k6 inspect <script>` -- 捕获语法错误、无效选项、损坏的导入。适用于所有类型，包括浏览器测试（无需浏览器）。如果 mcp-k6 可用，也运行 `validate_script`。
2. **本地冒烟测试**（非浏览器，服务可达）：
   `k6 run --vus 1 --iterations 1 <script>`。
3. **分类变更**（下文）并**根据矩阵验证** -- 请参考 [`references/verification.md`](references/verification.md) 中的配方。
4. **云托管脚本**：通过 k6-manage §5 的安全编辑配方应用（GET → 备份 → 编辑 → 验证 → PUT 作为 `application/octet-stream` → sha256 验证）。

### 变更分类

- **A 类 -- 仅声明式配置**。差异仅限于 `options.thresholds` 或类似的声明式字段，这些字段不会改变 k6 运行时执行的内容；`default function` 内部的字节、导入的模块和检查谓词的字节是相同的。例如：`p(95)<500` → `p(95)<420`。
- **B 类 -- 运行时逻辑变更**。对 `default function`、导入、辅助模块、请求 URL、检查谓词或 `scenarios.*.vus`/`iterations`/`duration`/`executor`（这些会改变负载形状和指标分布）的任何变更。例如：更改 URL、添加检查、重写认证、切换执行器。

如有疑问，视为 B 类。

### 验证矩阵

| 类别 | 测试持续时间 | 验证 |
|-------|---------------|------|
| **A** | 任何 | sha256 + `k6 inspect` + **历史通过/失败预测**。无需云运行。 |
| **B** | 短 (< 5 分钟) | sha256 + `k6 inspect` + **完整云运行**（k6-manage §11）。 |
| **B** | 长 (≥ 5 分钟) | sha256 + `k6 inspect` + **本地 1 次迭代冒烟测试** + **本地副本的 `k6 cloud run`，使用 `--vus 1 --iterations 1`**。仅在云冒烟测试通过后，才将保存的测试 PUT 到云端。 |

验证深度取决于变更类别，而不是测试的持续时间——大多数编辑不需要完整运行，生产测试可能运行数小时。每类配方（A 类预测表、B 类短/长、场景变更和放宽等边缘情况）请参考 [`references/verification.md`](references/verification.md)。

## 文档查询

在提议任何触及 k6 API、导入或模式的变更之前，请对照当前文档进行确认，并在报告中**引用来源**——这使建议基于真实的 API，而不是过时的模型知识。按顺序查询：

1. **mcp-k6**（首选）：`get_documentation("best_practices")`、`get_documentation("javascript-api/k6-browser")`、`validate_script(...)`。
2. **`k6 x docs`** CLI（始终可用）：
   ```bash
   k6 x docs using-k6 thresholds
   k6 x docs javascript-api k6-http
   k6 x docs search "websocket migration"
   ```
   2 调用策略：先尝试直接路径；如果返回主题列表，则选择子主题并再次调用。需要完整的父路径（`using-k6 thresholds`，而不是 `thresholds`）。`k6 x docs` 提供安装的 k6 版本的文档——在迁移时，它可能滞后于目标版本。
3. **网络获取**（最后手段）：`https://grafana.com/docs/k6/latest/`。

## 异步检查模式

浏览器测试的常见 Bug：使用 `k6` 的 `check()` 与异步谓词。内置的 `check()` 不会等待 Promise，因此 `check(page, { 'title': p => p.locator('h1').textContent() === 'Foo' })` 因 Promise 对象为真而静默通过。两个有效的修复方法：

- **来自 jslib 的异步感知检查**：
  `import { check } from 'https://jslib.k6.io/k6-utils/1.5.0/index.js'`——然后谓词可以是 `async` 和 `await`。
- **在检查之前解析值**：
  `const text = await page.locator('h1').textContent(); check(text, { ... })`——保持来自 `k6` 的标准同步 `check`。

在任何工作流（迁移、重构、审核）中遇到此问题，将其标记为行为性 Bug，并提出其中一种修复方法。

## 脚本来源

- **GCk6 托管** -- 通过 `k6-manage` §5 获取和推送（GET → 备份 → 编辑 → 验证 → PUT → sha256 验证）。
- **本地磁盘** -- 直接读取和编辑。验证后再提交。

在开始之前确定来源：GCk6 测试 URL 或 ID 是云托管的；文件路径是本地的。

## 工作流

完整步骤请参考 [`references/workflows.md`](references/workflows.md)：

- **[阈值收紧](references/workflows.md#threshold-tightening)** -- 提出基于观察指标的值，差异，应用，A 类验证。
- **[版本迁移](references/workflows.md#version-migration)** -- 查找弃用/重命名的 API，分类语法性 vs 行为性，应用，B 类验证。
- **[服务变更适配](references/workflows.md#service-change-adaptation)** -- 将每个服务变更映射到脚本变更，提出修复，B 类验证。
- **[重构](references/workflows.md#refactoring)** -- 查找问题，自动应用语法性，提出行为性，确认后 B 类验证。
- **[最佳实践审核](references/workflows.md#best-practices-audit)** -- 跨阈值、负载设计、资源管理、代码质量和浏览器特定内容的文档驱动审核。

所有五项都遵循行为感知变更控制：自动应用语法性变更，将行为性变更作为差异呈现以供确认。

## 注意事项

| 问题 | 详情 |
|------|------|
| **云脚本格式** | GCk6 脚本可以是单个文件或 tar 存档。在编辑前使用 `file(1)` 检测（见 k6-manage §5）。 |
| **零观察阈值** | 在没有观察到的指标上的阈值默认通过。添加新阈值时，请确保指标实际上由测试发出。 |
| **abortOnFail 级联** | 如果阈值为 `abortOnFail: true`，收紧它意味着运行提前终止。警告用户。 |
| **浏览器脚本验证** | 浏览器脚本无法使用 `k6 run --iterations 1` 进行验证，除非有浏览器。使用 `k6 inspect` 进行仅解析验证，或通过 mcp-k6 使用 `validate_script`。 |
| **k6 x docs 版本对齐** | `k6 x docs` 提供安装的 k6 版本的文档；在迁移到新版本时，本地文档可能无法反映目标 API。在迁移查询中注意这一点。 |
| **编辑后的脚本漂移** | 推送云托管脚本后，下一次运行使用新版本，但历史运行保持其捆绑的快照。要调查过去的失败，请比较运行捆绑的脚本（只读），而不是当前脚本。 |

## 参考

- [`references/workflows.md`](references/workflows.md) -- 五项维护任务的逐步步骤
- [`references/verification.md`](references/verification.md) -- 每类编辑后验证配方
