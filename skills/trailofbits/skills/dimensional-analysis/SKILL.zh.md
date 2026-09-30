---
name: dimensional-analysis
description: 为代码库添加维度分析注释，记录单位、维度和十进制缩放。当有人要求在代码库中标注单位、执行维度分析，或查找与DeFi协议、链下代码或其他与区块链相关的代码库中的算术漏洞时使用。可防止维度不匹配，并及早捕获公式错误。
---

# 量纲分析技能

这项技能为执行混合单位、精度或缩放因子的数值计算代码库编排一个量纲分析管道。主要技能上下文是一个工作流控制器：它将扫描、词汇发现、注释、传播和验证委托给专门的子代理，然后管理批处理、持久化、重试、覆盖率门禁和最终报告。

## 使用场景

- 使用单位/维度注释标注代码库（例如，`D18{tok}`、`D27{UoA/tok}`）
- 对去中心化金融协议、金融代码或科学计算执行量纲分析
- 搜索由单位不匹配、缺失缩放或精度损失引起的算术错误
- 审计具有混合十进制精度或定点算术的代码库

## 不应使用场景

- 没有数值算术或单位转换的代码库——没有需要标注的内容
- 纯整数计数逻辑（循环索引、数组长度）且没有物理或金融维度
- 当你只需要快速检查单个公式时——直接阅读代码而不是运行完整管道

## 执行模式

这项技能只运行一种模式：`full-auto`。
这是一个基于工作流的技术，它通过 `Task` 工具将特定步骤的工作委托给专门的代理。你编排整体流程，管理覆盖范围和状态持久化，并确保每个在范围内的文件都通过管道的每个步骤进行处理。

- 始终按以下顺序运行完整管道：步骤 1 -> 步骤 2 -> 步骤 3 -> 步骤 4。
- 当存在专门用于该步骤的子代理时，主要技能上下文不应自行执行仓库范围的量纲分析、注释、传播或错误验证。
- 主要技能上下文仅在需要时检查工件、清单和子代理输出，以路由工作、构建提示、持久化状态并确定完成。
- 调用者提供的任何模式参数都将被忽略。
- 在最后以单个摘要报告所有结果。

当你开始一个步骤时，报告它：

```text
开始步骤：步骤 {n}
```

## 范围和覆盖率保证

这项技能必须审计所有**在范围内的算术文件**，包括大型仓库。

- 在范围内的文件由步骤 1 扫描器输出（`files` 数组）定义，跨越**所有**优先级层级（CRITICAL、HIGH、MEDIUM、LOW）。
- 如果步骤 1 缩小输入以进行词汇发现（例如，仅 CRITICAL/HIGH），则该缩小仅适用于发现。它**永远不会**减少注释或验证范围。
- `arithmetic-scanner` 将在项目根目录的 `DIMENSIONAL_SCOPE.json` 中持久化在范围内的文件清单，该清单是步骤 2-4 的真实来源。
- 只有当所有三个状态都存在时，文件才被认为完全覆盖：
  - `step2`：锚点注释完成（或显式无锚点结果）
  - `step3`：传播完成（或显式无传播结果）
  - `step4`：验证完成
- `dimension-discoverer` 将发现的量纲词汇持久化到项目根目录的 `DIMENSIONAL_UNITS.md` 中，供后续步骤和未来运行重用。
- 当文件以终端 `BLOCKED` 状态结束时，将阻止原因和重试次数持久化到 `DIMENSIONAL_SCOPE.json` 中，并在 `coverage.unprocessed_files` 中反映相同的文件。
- 不要在任何步骤中存在任何在范围内的文件未处理时完成。

## 委托合同

- `arithmetic-scanner` 拥有仓库扫描、算术文件优先级排序和写入 `DIMENSIONAL_SCOPE.json`。
- `dimension-discoverer` 拥有量纲词汇发现、单位推断和写入 `DIMENSIONAL_UNITS.md`。
- `dimension-annotator` 拥有注释格式决策、锚点编辑和注释写入行为。
- `dimension-propagator` 拥有传播逻辑、推断注释和跟踪期间的错配报告。
- `dimension-validator` 拥有错误检测、红旗评估、合理化拒绝和确认或否认传播的错配。
- 主要技能上下文不应用其自己的量纲推理代替跳过或未启动的子代理。如果某个步骤需要专门推理，则启动相应的子代理。
- 使用参考文件作为子代理的支持材料。将它们传递给相关步骤的提示，而不是将它们视为主要技能上下文的指令。

## 工作流

按顺序遵循这些部分。不要前进，直到当前步骤满足其完成门禁。

### 共享编排规则

- `DIMENSIONAL_SCOPE.json` 和 `DIMENSIONAL_UNITS.md` 位于项目根目录。
- 主要技能上下文验证步骤 1 工件，但本身不写入任何步骤 1 工件。
- `DIMENSIONAL_SCOPE.json.in_scope_files` 是步骤 2-4 的真实来源。永远不要从仅用于发现的输入中派生后续范围。
- 当后续步骤达到终端 `BLOCKED` 时，在 `DIMENSIONAL_SCOPE.json` 中文件条目上持久化匹配的 `step*_reason` 和 `step*_retry_count` 字段。
- `coverage.unprocessed_files` 必须从 `DIMENSIONAL_SCOPE.json` 中的终端 `BLOCKED` 条目中派生，使用 `{ "path": "...", "blocked_step": "step2|step3|step4", "reason": "...", "retry_count": 1 }`。
- 一个步骤可以一次用聚焦提示重试 `BLOCKED` 文件。如果它仍然 `BLOCKED`，请保留记录的原因并继续。不要在任何文件保持 `PENDING` 时完成。

### 步骤 1：词汇和范围发现

如果无法重用缓存工件，将仓库扫描委托给 `arithmetic-scanner`，将词汇发现委托给 `dimension-discoverer`。不要在主要技能上下文中直接执行此步骤特定的分析。

1. 检查项目根目录中是否已存在 `DIMENSIONAL_UNITS.md` 和 `DIMENSIONAL_SCOPE.json`。
2. 如果两者都存在，读取它们并确认：
   - `DIMENSIONAL_SCOPE.json.project_root` 与当前仓库根匹配
   - `DIMENSIONAL_SCOPE.json` 包含 `in_scope_files`、`discoverer_focus_files`、`recommended_discovery_order` 和每个文件的 `step2`、`step3`、`step4` 字段
   - `DIMENSIONAL_UNITS.md` 是此仓库可用的量纲词汇
3. 如果任一工件已过时、格式错误、缺少所需结构或明显属于另一个仓库，则丢弃重用并重新运行步骤 1 的其余部分。
4. 如果两者都有效，则直接重用它们。如果 `in_scope_files` 为空，则跳过步骤 2-4 并以零发现结果生成最终输出。
5. 否则，使用 `Task` 工具生成 `arithmetic-scanner` 代理。其提示必须包括：
   - 项目根路径
   - `DIMENSIONAL_SCOPE.json` 的绝对输出路径
   - 指示将步骤 1 范围清单写入磁盘并在报告中返回相同范围数据的指令
6. 扫描器拥有步骤 1 范围持久化。它必须：
   - 识别量纲算术文件并按常规优先级排序
   - 写入 `DIMENSIONAL_SCOPE.json`，包含 `project_root`、`in_scope_files`、`discoverer_focus_files` 和 `recommended_discovery_order`
   - 使用 `step2: "PENDING"`、`step3: "PENDING"` 和 `step4: "PENDING"` 初始化每个在范围内的文件
   - 当未找到算术文件时，仍然写入空清单
   - 当找到 50 个以上算术文件时，仍然将 `discoverer_focus_files` 缩小到 CRITICAL/HIGH，同时保持 `in_scope_files` 中的所有优先级
7. 扫描器完成后，从磁盘读取 `DIMENSIONAL_SCOPE.json` 并确认其存在并包含所需的步骤 1 字段，然后继续。
8. 使用 `Task` 工具生成 `dimension-discoverer` 代理。其提示必须包括：
   - 项目根路径
   - `DIMENSIONAL_SCOPE.json` 的绝对路径
   - `DIMENSIONAL_UNITS.md` 的绝对输出路径
   - 优先级 `discoverer_focus_files`，包含每个文件的路径、优先级、分数和类别
   - `recommended_discovery_order`
9. 发现者拥有步骤 1 词汇持久化。它必须读取 `DIMENSIONAL_SCOPE.json` 作为步骤 1 真实来源并写入 `DIMENSIONAL_UNITS.md`，包含 `Base Units`、`Derived Units` 和 `Precision Prefixes` 部分。如果 `in_scope_files` 为空，它必须仍然写入相同的标题和空部分。
10. 只有当两个工件都存在于磁盘上、通过上述重用检查并正确表示零文件情况时，步骤 1 才算完成。如果发现者在写入 `DIMENSIONAL_UNITS.md` 后 `in_scope_files` 为空，则跳过步骤 2-4 并以零发现结果生成最终输出。

### 步骤 2：锚点注释

主要技能上下文不应自行添加注释。使用 `Task` 工具为所有锚点注释工作生成 `dimension-annotator` 代理。有关完整示例和注释格式详细信息，请参阅 `[{baseDir}/references/annotate.md]({baseDir}/references/annotate.md)`。

- 读取 `DIMENSIONAL_SCOPE.json` 并从 `in_scope_files` 构建批次。每个在范围内的文件，包括 MEDIUM 和 LOW 优先级文件，都必须接收步骤 2 结果。
- 批次文件而不是为每个文件生成一个代理：
  - `<= 10` 个文件：一个批次
  - `11-30` 个文件：每个类别一个批次
  - `> 30` 个文件：每个类别一个批次，将 10 个文件以上的类别分成大约 8 个文件的子批次
- 按步骤 1 推荐的发现顺序启动类别：数学库，然后预言机，然后核心逻辑，然后外围。同一类别内的批次可以并行运行。
- 在启动注释器之前，为每个在范围内的文件设置 `step2 = "PENDING"` 并持久化更新的 `DIMENSIONAL_SCOPE.json`。
- 每个注释器提示必须包括：
  - `DIMENSIONAL_UNITS.md` 的绝对路径
  - `DIMENSIONAL_SCOPE.json` 的绝对路径
  - 分配的文件路径按顺序
  - 每个文件的类别和扫描器输出中的匹配模式
  - 从先前批次中获取的先前注释接口或类型的摘要，当适用时
  - 每个文件所需的状态输出：`ANNOTATED`、`REVIEWED_NO_ANCHOR_CHANGES` 或 `BLOCKED` 加上一行理由
- 每个批次后，立即将每个分配的文件持久化为一个步骤 2 状态：
  - `ANNOTATED`
  - `REVIEWED_NO_ANCHOR_CHANGES`
  - `BLOCKED`
- 如果文件是 `BLOCKED`，还持久化 `step2_reason` 和 `step2_retry_count`。重试每个 `BLOCKED` 文件一次，使用聚焦提示。
- 不要在磁盘清单状态中任何文件保持 `PENDING` 时继续到步骤 3。

### 步骤 3：量纲传播

主要技能上下文不应自行执行传播推理。使用 `Task` 工具生成 `dimension-propagator` 代理，通过算术、函数调用和赋值扩展注释。有关代数详细信息，请参阅 `[{baseDir}/references/dimension-algebra.md]({baseDir}/references/dimension-algebra.md)`。

- 读取 `DIMENSIONAL_SCOPE.json` 并从 `in_scope_files` 构建传播批次。每个在范围内的文件都必须接收步骤 3 结果。
- 使用与步骤 2 相同的批处理规则和类别顺序。
- 在启动传播器之前，确认每个文件已经具有非挂起的步骤 2 状态。
- 然后，为每个在范围内的文件设置 `step3 = "PENDING"` 并持久化更新的清单。
- 每个传播器提示必须包括：
  - `DIMENSIONAL_UNITS.md` 的绝对路径
  - `DIMENSIONAL_SCOPE.json` 的绝对路径
  - 分配的文件路径按顺序
  - 每个文件的类别和匹配模式
  - 分配文件和它们依赖的上游接口的步骤 2 锚点注释摘要
  - 每个文件所需的状态输出：`PROPAGATED`、`REVIEWED_NO_PROPAGATION_CHANGES` 或 `BLOCKED` 加上一行理由
- 每个批次后，立即将每个分配的文件持久化为一个步骤 3 状态：
  - `PROPAGATED`
  - `REVIEWED_NO_PROPAGATION_CHANGES`
  - `BLOCKED`
- 如果文件是 `BLOCKED`，还持久化 `step3_reason` 和 `step3_retry_count`。重试每个 `BLOCKED` 文件一次，使用聚焦提示。
- 所有传播器完成后，聚合：
  - 由置信级别（`CERTAIN`、`INFERRED`、`UNCERTAIN`）添加的注释
  - 发现的错配，包括用于验证器去重的严重性
  - 无法推断的覆盖范围差距
- 不要在磁盘清单状态中任何文件保持 `PENDING` 时继续到步骤 4。

### 步骤 4：错误检测

主要技能上下文不应自行执行错误检测。使用 `Task` 工具生成 `dimension-validator` 代理，以检测注释代码中的量纲错误。有关示例、红旗、合理化检查和标准词汇，请参阅 `[{baseDir}/references/bug-patterns.md]({baseDir}/references/bug-patterns.md)`、`[{baseDir}/references/common-dimensions.md]({baseDir}/references/common-dimensions.md)` 和 `[{baseDir}/references/dimension-algebra.md]({baseDir}/references/dimension-algebra.md)`。**不要在任何其他步骤中检测错误**。

- 验证 `DIMENSIONAL_SCOPE.json.in_scope_files` 中的每个文件。
- 使用此优先级顺序，不要跳过较低层级：
  1. 具有CRITICAL或HIGH步骤 3 错配的文件
  2. 剩余的CRITICAL和HIGH扫描器优先级文件
  3. 剩余的MEDIUM和LOW文件
- 在启动验证器之前，确认每个文件已经具有非挂起的步骤 3 状态。
- 然后，为每个在范围内的文件设置 `step4 = "PENDING"` 并持久化更新的清单。
- 为每个文件生成一个 `dimension-validator` 代理。对于大型仓库，以大约 10-30 个文件为一波运行它们，以保持编排稳定。
- 每个验证器提示必须包括：
  - `DIMENSIONAL_UNITS.md` 的绝对路径
  - `DIMENSIONAL_SCOPE.json` 的绝对路径
  - 要验证的单个文件路径
  - 文件中锚点和传播注释的摘要
  - 文件的步骤 3 错配摘要，包括错配ID
  - 需要用于调用边界检查的跨文件函数签名或返回维度
  - 每个文件所需的状态输出：`VALIDATED` 或 `BLOCKED`
- 每波后，立即将每个文件持久化为一个步骤 4 状态：
  - `VALIDATED`
  - `BLOCKED`
- 如果文件是 `BLOCKED`，还持久化 `step4_reason` 和 `step4_retry_count`。重试每个 `BLOCKED` 文件一次，使用聚焦提示。
- 去重发现：
  - 确认的步骤 3 错配保留其原始ID和严重性
  - 被否认的步骤 3 错配被注明为误报并从最终计数中排除
  - 真正的新发现将获得新的 `DIM-XXX` ID
- 聚合确认发现、新发现、被否认发现、覆盖范围摘要和最终的 `coverage.unprocessed_files`。
- 只有当 `DIMENSIONAL_SCOPE.json.in_scope_files` 不包含 `step4: "PENDING"` 条目时，步骤 4 才算完成。

## 参考文档

当步骤需要它们时，将以下参考传递给相关子代理：
- `[{baseDir}/references/dimension-algebra.md]({baseDir}/references/dimension-algebra.md)` - 传播器和验证器代数规则
- `[{baseDir}/references/common-dimensions.md]({baseDir}/references/common-dimensions.md)` - 验证器词汇参考
- `[{baseDir}/references/bug-patterns.md]({baseDir}/references/bug-patterns.md)` - 验证器错误模式和红旗参考
- `[{baseDir}/references/annotate.md]({baseDir}/references/annotate.md)` - 注释器格式和示例参考

## 最终输出

在分析结束时，除非指定了其他输出格式，否则提供结构化摘要：

```json
{
  "mode": "full-auto",
  "project_root": "<path>",
  "vocabulary": {
    "base_units": ["..."],
    "derived_units": ["..."],
    "precision_prefixes": ["..."]
  },
  "annotations": {
    "total_added": 0,
    "by_file": {}
  },
  "findings": {
    "critical": 0,
    "high": 0,
    "medium": 0,
    "details": []
  },
  "uncertainties_resolved": 0,
  "coverage": {
    "in_scope_files": 0,
    "anchor_reviewed_files": "0/0",
    "propagation_reviewed_files": "0/0",
    "validation_reviewed_files": "0/0",
    "annotated_functions": "0/0",
    "annotated_variables": "0/0",
    "unprocessed_files": [
      {
        "path": "/path/to/repo/contracts/LegacyMath.sol",
        "blocked_step": "step3",
        "reason": "Parser could not process generated source",
        "retry_count": 1
      }
    ]
  }
}
```

## 完成清单

在所有这些都为真之前，你还没有完成：

### 文件覆盖门禁
- [ ] 项目根目录中存在 `DIMENSIONAL_UNITS.md`
- [ ] 项目根目录中存在 `DIMENSIONAL_SCOPE.json`，它是下游覆盖的权威来源
- [ ] 步骤1中发现的所有在范围内的算术文件都出现在 `DIMENSIONAL_SCOPE.json.in_scope_files` 中
- [ ] 所有在范围内的文件都具有非 `PENDING` 的步骤2状态（`ANNOTATED`、`REVIEWED_NO_ANCHOR_CHANGES` 或 `BLOCKED`）
- [ ] 所有在范围内的文件都具有非 `PENDING` 的步骤3状态（`PROPAGATED`、`REVIEWED_NO_PROPAGATION_CHANGES` 或 `BLOCKED`）
- [ ] 所有在范围内的文件都具有非 `PENDING` 的步骤4状态（`VALIDATED` 或 `BLOCKED`）
- [ ] 没有任何在范围内的文件在任何步骤中保持 `PENDING` 状态
- [ ] 任何 `BLOCKED` 文件在最终输出中都有记录的原因
- [ ] `coverage.unprocessed_files` 精确匹配重试后最终的一组终端 `BLOCKED` 文件，使用 `path`、`blocked_step`、`reason` 和 `retry_count`

### 摘要报告
- [ ] 提供了最终的摘要 JSON/报告
- [ ] 最终的覆盖计数器与 `DIMENSIONAL_SCOPE.json` 匹配
- [ ] 在进行编辑时提供了已修改文件列表
- [ ] 找到的任何维度不匹配或错误都进行了总结
- [ ] 任何剩余的已阻塞或未处理的文件都列出了原因

**如果 `DIMENSIONAL_SCOPE.json` 和最终报告不一致，请协调报告或继续处理直到它们匹配。**
**仅凭代理意图不要声称完成；完成由显式覆盖和最终报告状态决定。**
