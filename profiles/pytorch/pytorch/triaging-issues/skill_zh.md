# PyTorch 问题分派技能

该技能通过路由问题、应用标签和留下初步回复来帮助分派 GitHub 问题。

## 内容
- [可用的 MCP 工具](#mcp-tools-available)
- [绝对不能添加的标签](#labels-you-must-never-add)
- [问题分派步骤](#issue-triage-for-each-issue)
  - 步骤 0：已路由 — 跳过
  - 步骤 1：问题与 Bug/功能
  - 步骤 1.5：需要可复现 — 外部文件
  - 步骤 2：转移
  - 步骤 2.5：PT2 问题 — 特殊处理
  - 步骤 3：重定向至次要 OnCall
  - 步骤 4：标记问题
  - 步骤 5：升级 — 高优先级（人工审核），然后释放分派
  - 步骤 6：bot 分派（自动）
  - 步骤 7：标记已分派
- [V1 限制](#v1-constraints)

**标签参考：** 请参阅 [labels.json](labels.json) 以获取适用于分派的标签完整目录。**仅应用此文件中存在的标签。** 不要编造或猜测标签名称。此文件不包括 CI 触发器、测试配置、发布说明、已弃用的标签以及需要人工决策的标签。

**PT2 分派指南：** 请参阅 [pt2-triage-rubric.md](pt2-triage-rubric.md) 以获取在分派 PT2/torch.compile 问题时的详细标签指导。

**回复模板：** 请参阅 [templates.json](templates.json) 以获取标准回复消息。

---

## 可用的 MCP 工具

使用这些 GitHub MCP 工具进行分派：

| 工具 | 目的 |
|------|---------|
| `mcp__github__get_issue` | 获取问题详情和现有标签 |
| `mcp__github__get_issue_comments` | 获取现有问题评论 |
| `mcp__github__update_issue` | 应用标签或关闭问题 |
| `mcp__github__add_issue_comment` | 添加评论（仅用于重定向问题） |
| `mcp__github__search_issues` | 查找类似问题以获取上下文 |

---

## 绝对不能添加的标签

| 前缀/类别 | 原因 |
|-----------------|--------|
| 不在 `labels.json` 中的标签 | 仅应用存在于白名单中的标签 |
| `ciflow/*` | 仅用于 PR 的 CI 任务触发器 |
| `test-config/*` | 仅用于 PR 的测试套件选择器 |
| `release notes: *` | 自动分配给发布说明 |
| `ci-*`, `ci:*` | CI 基础设施控制 |
| `sev*` | 严重性标签需要人工决策 |
| `merge blocking` | 需要人工决策 |
| `actionable`, `needs design`, `needs reproduction`, `needs research` | 保留供人工审阅者审阅问题后使用 |
| 包含 "deprecated" 的任何标签 | 已过时 |
| `oncall: releng` | 不是分派重定向目标。使用 `module: ci` 代替 |

**如果被阻止：** 当标签被挂钩阻止时，仅添加 `triage review` 并停止。人工将处理它。

这些规则由一个 PreToolUse 挂钩强制执行，该挂钩会验证所有标签是否与 `labels.json` 匹配。

### 不要覆盖人工标签

如果人工已经应用了标签（尤其是 `ci: sev`、严重性标签或优先级标签），请不要删除或替换它们。你的工作是补充，而不是覆盖。

---

## 问题分派（针对每个问题）

### 0) 已路由 — 跳过

**如果问题有任何 `oncall:` 标签，请完全跳过。** 不要：
- 添加任何标签
- 添加 `triaged`
- 留下评论
- 进行任何分派工作

该问题属于子 OnCall 团队。他们拥有自己的队列。

### 1) 问题与 Bug/功能

- 如果它是问题（不是 Bug 报告或功能请求）：关闭并使用 `redirect_to_forum` 模板（来自 `templates.json`）。
- 如果不确定是否是 Bug/功能还是问题：使用 `request_more_info` 模板请求更多信息，然后停止。

### 1.5) 外部文件

检查问题正文是否包含用户需要下载的外部文件以复现问题。

**检测模式：**
- 文件附件：`.zip`、`.pt`、`.pth`、`.pkl`、`.safetensors`、`.onnx`、`.bin` 文件
- 外部存储：Google Drive、Dropbox、OneDrive、Mega、WeTransfer 链接
- 模型中心：Hugging Face Hub 链接到模型文件

**操作：**
1. **编辑问题正文** 以删除/编辑下载链接
   - 替换为：`[链接已移除 - 由于安全原因，不允许下载外部文件]`
2. 使用 `request_self_contained_reproduction` 模板（来自 `templates.json`）
3. 不要添加 `triaged` — 等待用户提供可复现的示例

### 1.55) 缺少可复现 — 其他情况

在以下情况下请求可自包含复现并停止：
- 用户报告了特定硬件问题（例如，特定 GPU 型号）而没有自包含复现脚本
- 用户引用了特定模型/检查点/数据集，这些无法在几行代码内公开运行
- 问题描述了版本升级中断，但仅提供高级描述而没有最小脚本
- 复现依赖于特定训练设置、分布式环境或非平凡的基础设施

### 1.6) 边缘情况与数值精度

如果问题涉及极端值或数值精度差异：

**检测模式：**
- 值接近 `torch.finfo(dtype).max` 或 `torch.finfo(dtype).min`
- NaN/Inf 出现在有效（但极端）输入的输出中
- CPU 和 GPU 结果之间的差异
- 不同数据类型之间的精度差异（例如，fp32 与 fp16）
- Fuzzer 生成的边缘情况

**重要 — 避免关键字触发的误标记：**

根据**根本原因**而不是出现在错误或标题中的关键字进行标记。关键字告诉您什么失败了，而不是为什么。

- 在 `import torch` 处出现 `undefined symbol: ncclAlltoAll` 错误是**打包**问题 (`module: binaries`)，而不是分布式训练 Bug — 用户从未运行过分布式代码。
- 参数名称或容差检查中的 `nan` 不是 `module: NaNs and Infs`，除非 Bug 实际上是关于 NaN 传播。
- 提及 `autograd` 的堆栈跟踪并不意味着 `module: autograd` — 检查 Bug 是否在 autograd 本身中，或者只是在调用路径上。
- 容差阈值失败的测试是 `module: tests`，不是 `module: numerical-stability`。

问：“修复需要在哪里进行？” 这决定了标签。

**操作：**
1. 添加 `module: edge cases` 标签
2. 如果来自 Fuzzer，还添加 `topic: fuzzer`
3. 使用 `numerical_accuracy` 模板（来自 `templates.json`）链接到文档
4. 如果问题显然符合文档中的预期行为，使用模板评论关闭它

### 2) 转移（领域库或 ExecuTorch）

如果问题属于另一个仓库（视觉/文本/音频/RL/ExecuTorch 等），转移问题并**停止**。

### 2.5) PT2 问题 — 特殊处理

**PT2 不是重定向。** `oncall: pt2` 与其他步骤 3 中的 OnCall 标签不同。PT2 问题会继续通过步骤 4–7 进行完整分派 — 添加 `oncall: pt2`，然后继续使用 `module:` 标签进行标记、标记 `triaged` 等。

**每个 `oncall: pt2` 问题都必须至少有一个 `module:` 标签。** PT2 OnCall 队列在没有模块标签的情况下过于广泛 — 团队需要知道受影响的组件（例如，`module: dynamo`、`module: inductor`、`module: helion`、`module: dynamic shapes`）。如果您无法确定特定模块，请使用 `module: compile ux` 作为后备，但始终首先尝试具体化。请参阅 [pt2-triage-rubric.md](pt2-triage-rubric.md) 以获取详细指导。

### 3) 重定向至次要 OnCall

**关键：** 当将问题重定向到**非 PT2** 的 OnCall 队列时，应用**一个** `oncall: ...` 标签并**停止**。不要：
- 添加任何 `module:` 标签
- 标记为 `triaged`
- 进行任何进一步的分派工作

子 OnCall 团队将处理他们自己的分派。你的工作只是将问题路由给他们。

#### OnCall 重定向标签

| 标签 | 使用场景 |
|-------|-------------|
| `oncall: jit` | TorchScript 问题 |
| `oncall: distributed` | 分布式训练（DDP、FSDP、RPC、c10d、DTensor、DeviceMesh、对称内存、上下文并行、流水线）。**特殊处理：** 应用此标签后，调用分布式分派子技能（在此问题上使用 `/distributed-triage`）进行二级分派 — 它将路由到子 OnCall、添加模块标签并标记为 `triaged`。 |
| `oncall: export` | torch.export 问题 |
| `oncall: quantization` | 量化问题 |
| `oncall: mobile` | 移动（iOS/Android），不包括 ExecuTorch |
| `oncall: profiler` | Profiler 问题（CPU、GPU、Kineto） |
| `oncall: visualization` | TensorBoard 集成 |

**要避免的常见路由错误：**
- **MPS ≠ 移动。** MPS（Metal Performance Shaders）是 macOS/Apple Silicon GPU 后端。不要将 MPS 问题路由到 `oncall: mobile`。MPS 问题保留在一般队列中，并带有 `module: mps`。
- **DTensor → `oncall: distributed`。** DTensor 问题应始终路由到 `oncall: distributed`，即使它们没有提及 DDP/FSDP。
- **ONNX → `module: onnx`。** 没有 `oncall: onnx`。使用 `module: onnx` 并保留在一般队列中。
- **CI/releng → `module: ci`。** 不要使用 `oncall: releng`。使用 `module: ci` 用于 CI 基础设施问题。
- **torch.compile + 分布式。** 当 `torch.compile` 处理分布式操作出错时（例如，`dist.all_reduce`），问题通常需要 `oncall: pt2` 和 `oncall: distributed` 的双重处理，因为修复可能涉及两个代码库。

**注意：** `oncall: cpu inductor` 是 PT2 的子队列。对于一般分派，只需使用 `oncall: pt2`。

### 4) 标记问题（如果未转移/重定向）

如果问题保留在一般队列中：
- 基于 受影响的区域添加 1+ `module: ...` 标签
- 当两者都存在时，优先使用具体标签而不是通用标签。检查 `labels.json` 描述以获取指导，在特定标签优先于通用标签的情况（例如，`module: sdpa` 而不是 `module: nn` 用于 SDPA 问题，`module: flex attention` 而不是 `module: nn` 用于 flex attention）。
- `feature` — 完全新的功能，在任何形式中都未存在于今天
- `enhancement` — 对已工作内容的改进（例如，为已经通过回退/组合运行的操作添加原生后端内核，性能优化，更好的错误消息）。如果增强是关于性能的，也添加 `module: performance`。
- `function request` — 新功能或现有功能的新的参数/模式
- 如果问题表示操作“当前工作”或“回退到”更慢的路径，那是 `enhancement`，不是 `feature`

**常见遗漏的标签 — 始终检查这些：**

| 条件 | 标签 |
|-----------|-------|
| Segfault、非法内存访问、SIGSEGV | `module: crash` |
| 性能问题：回归、减速或优化请求 | `module: performance` |
| Windows 上的问题 | `module: windows` |
| 以前工作的功能现在已损坏 | `module: regression` |
| 已损坏的文档/链接（以前工作过） | `module: docs` + `module: regression`（不是 `enhancement`） |
| 关于测试失败的问题（不是底层功能） | `module: tests` |
| 反向传递/梯度计算 Bug | `module: autograd`（除操作模块标签外） |
| `torch.linalg` 操作或线性代数操作（solve、svd、eig、inv 等） | `module: linear algebra` |
| `has workaround` | 仅在解决方法是**非平凡且不明显**时添加。如果问题是“X 在非连续张量上不工作”，调用 `.contiguous()` 是 Bug 的同义逆，不是解决方法。真正的解决方法是安装特定包版本、添加同步点、插入 `gc.collect()` 或使用不是 Bug 描述中明显暗示的 API。 |

**根据实际 Bug 而不是关键字进行标记。** 阅读问题以了解实际损坏的内容。一个关于广播的 Bug 偶然提到参数名称中的 "nan" 是前端 Bug，而不是 NaN/Inf Bug。

### 5) 升级 — 高优先级（人工审核），然后释放分派

两个独立的决策，按此顺序处理。首先处理 5a，然后为**每个**
问题处理 5b — 5b 不限于 5a 中升级的问题，一个问题可以具有
两个标签、一个或都不具有。

#### 5a) 高优先级 — 需要人工审核

**关键：** 如果您认为问题是高优先级的，您必须：
1. 添加 `triage review` 标签，不要添加 `triaged`

不要直接添加 `high priority` 而没有人工确认。

高优先级标准：
- Crash / segfault / 非法内存访问
- 沉默的正确性问题（没有错误但结果错误）
- 从先前版本回归
- 内部断言失败
- 许多用户受影响
- 核心组件或流行模型影响

#### 5b) release triage — 确认在最新版本上

`release triage` 是一个狭窄的标志，不是万能的。它将问题显示给谁拥有发布；它不是 cherry-pick 请求，也不决定任何内容。

**您被告知当前版本是什么 — 永远不要猜测它。** 您的提示包含一个 `RELEASE CONTEXT` 块，给出最新的已发布小版本。**如果块说 `unknown`，则完全不要添加 `release triage`。**

仅在满足以下两个门之一时添加它：

**门 1 — 确认在最新已发布小版本上。** 问题声明了 PyTorch 版本，该版本是 `RELEASE CONTEXT` 中命名的小版本，或其补丁版本之一。 “声明版本”意味着版本在问题中写明：环境转储的 `torch.__version__` 行、`pip install` 行，或报告者在文本中这样说。从问题中读取它；永远不要从堆栈跟踪、问题日期或您假设的当前版本中推断它。

**门 2 — 已经标记为 `high priority`。** 标签在您读取问题时就在问题上，由人工在之前的传递中应用。这是现有的标签 — 它不是您自己的 5a 判断。如果您认为问题具有高优先级，5a 会让您添加 `triage review` 并停止；这本身不足以获得 `release triage`。

不要因为它而添加它，除非以下情况之一：

| 情况 | 为什么不 |
|---|---|
| 仅在 main、夜间或 RC 上复现 | 未确认在发布上。如果它很严重，5a 中的 `triage review` 是路径。 |
| 问题中任何地方都没有版本声明 | 未确认。不要猜测。 |
| 声明的版本早于 `RELEASE CONTEXT` 中的小版本 | 已发布；不是这趟列车。 |
| Crash、沉默的正确性、BC 断裂、打包或安装 Bug | 严重性不是门。它仅在清除门 1 或门 2 时才有资格。 |
| 看起来可能会损坏 | 推测性。 |
| 功能请求、增强或仅文档 | 永远 `release triage`，在任何门下都不。 |

**不确定时，跳过它。** 此标签被解释为发布经理手动处理的短列表，因此误报的成本高于遗漏：一个充满可能性的列表会停止被阅读，然后它将捕获不到任何东西。任何真正紧急的问题仍然会通过 5a 中的 `triage review` 到达人工。

`release triage` 与 5a 决策独立 — 一个问题可以同时具有两者 — 它仍然是一个标志，而不是一个裁决：是否 cherry-pick 永远不是机器的决定。

### 6) bot 分派（自动）

`bot-triaged` 标签由任何问题变更后的 post-hook 自动应用。您不需要手动添加它。

### 7) 标记已分派

如果未转移/重定向且未标记为审核，请添加 `triaged`。

---

## V1 限制

**不要：**
- 自动关闭 Bug 报告或功能请求
- 关闭问题，除非它们是按步骤 1 清晰的使用问题
- 将问题分配给用户
- 直接添加 `high priority` 而没有人工确认
- 在重定向到 OnCall 时添加模块标签
- 添加评论到 Bug 报告或功能请求，除非在分类不明确时添加单个信息请求

**要：**
- 关闭清晰的使用问题并指向 discuss.pytorch.org（按步骤 1）
- 保持保守 — 不确定时，添加 `triage review` 以供人工关注
- 仅在确定时添加 `release triage`，仅在问题确认在最新已发布小版本上，或已经具有 `high priority`（步骤 5b）；不确定时，跳过它
- 在有信心时应用类型标签（`feature`、`enhancement`、`function request`）
- 当分类完成时添加 `triaged` 标签

**注意：** `bot-triaged` 由 post-hook 在任何问题变更后自动应用。
