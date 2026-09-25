# printing-press-output-review (内部)

审查打印CLI的样本输出，查找那些常规测试、验证和基于规则的`scorecard --live-check`规则无法捕获的合理性错误。Wave B策略：所有发现均以警告形式呈现，永不以错误形式呈现。

这项技能是**仅限内部使用**的（`user-invocable: false`）。它由父级技能调用——主打印机技能在其shipcheck阶段4.85，以及打印机抛光技能在其诊断循环期间。单独运行它会产生无ship判定、未应用修复、无发布提议的浮动发现文本；可操作的包装器是`/printing-press`和`/printing-press-polish`。该技能携带`context: fork`，以便审查代理的诊断闲聊与调用技能的上下文保持隔离。

## 输入

调用者将`$CLI_DIR`作为参数传递：指向打印CLI工作目录的绝对路径。

## 捕获的内容

常规检查遗漏的错误，通常通过5分钟的动手测试暴露，但被dogfood、verify和`scorecard --live-check`规则遗漏：

- 偶然包含查询但语义上不匹配的子串匹配结果（例如，查询匹配较大无关术语的子串）
- 聚合命令在仅部分请求的N条返回时静默丢弃源
- 排名或排序命令返回的Top-N结果并非查询的最佳合理性结果（损坏的权重、提取器回退）
- 输出中的URL指向分类索引页面、馈送端点或随机选择路由，而非规范内容永久链接
- 规则层无法捕获的格式错误（摩斯密码、不一致的复数形式、截断/换行的单元格内容）

## 程序

### 第1步：收集样本数据

```bash
# 定位research.json。相邻二进制文件覆盖了后推广布局（独立抛光，针对库副本进行shipcheck）。祖父回退覆盖了管道中段的调用，其中$CLI_DIR是$PRESS_RUNSTATE/runs/<id>/working/<cli>，而research.json位于$PRESS_RUNSTATE/runs/<id>/research.json。没有回退，scorecard在管道中段报告`unable: true`，我们将跳过最有信息的审查。使用bash数组，以便标志在包含空格的路径中存活。
RESEARCH_ARGS=()
if [ ! -f "$CLI_DIR/research.json" ]; then
  _grandparent="$(dirname "$(dirname "$CLI_DIR")")"
  if [ -f "$_grandparent/research.json" ]; then
    RESEARCH_ARGS=(--research-dir "$_grandparent")
  fi
fi

cli-printing-press scorecard --dir "$CLI_DIR" "${RESEARCH_ARGS[@]}" --live-check --json > /tmp/output-review-livecheck.json 2>&1 || true
```

如果scorecard调用失败或`/tmp/output-review-livecheck.json`为空，则无需派发审查代理，直接返回SKIP结果（第3步）。

派发前，计算`live_check.features[]`中状态为`pass`的条目数量。如果为零，则返回`SKIP`并附带原因`无符合条件的通过样本；未评估合理性`。不要派发审查代理，并且永远不会因为所有样本命令失败或被排除在审查之外而报告干净的`PASS`。

### 第2步：派发审查代理

使用通用Agent工具（通用）和此提示合同：

> 审查已发布的CLI在`$CLI_DIR`的样本输出。您拥有以下真实来源：
>
> - 样本命令输出：读取`/tmp/output-review-livecheck.json`并检查`live_check.features[]`数组。每个条目包含命令、示例调用、已编辑的stdout证据（在`output_sample`中，限制在~4 KiB），已编辑的通过/失败原因，以及由基于规则的检查（如原始HTML实体检测器）填充的`warnings`数组。将`<redacted>`标记视为隐私清理值，而非格式错误。
> - **仅审查`status: pass`条目。** 状态为`fail`的条目要么崩溃，要么超时，要么具有占位符参数（`<id>`、`<url>`），这些参数从未产生实际输出——其样本为空，您没有可评判的内容。
> - `$CLI_DIR/research.json`的`novel_features`（按功能计划的行为）和`novel_features_built`（验证构建的命令）。
> - `$CLI_DIR/<cli-name>-pp-cli`处的CLI二进制文件——当发现需要验证时，您可能需要调用附加命令以收集更多输出。
>
> 对于这些检查，每个发现用50字以内的报告。仅报告人类用户在5分钟动手测试中会注意到的问题——而不是彻底的QA测试可能发现的每个边缘情况：
>
> 1. **输出在语义上匹配查询意图。** 对于带有查询参数的样本新功能，判断相关性应超越live-check中机械查询标记检查强制的范围。通过live-check的`outputMentionsQuery`测试的功能仍然包含*某些*查询标记——但"buttermilk"作为"butter"子串出现的结果，或"brownies"返回辣椒食谱，因为提取器回退到相邻内容，这两种情况都通过了机械检查。仅在人类用户查看顶部结果并说"这不是我想要的"时才标记。当示例没有查询参数时跳过此检查。
> 2. **无明显格式错误。** 输出是否包含原始HTML实体、摩斯密码（标题中的问号或替换字符）或格式错误的URL（指向分类索引页面、馈送端点或随机选择路由，而非规范内容永久链接）？基于规则的live-check捕获数字实体；这一层捕获更广泛的类别。
> 3. **聚合命令显示所有请求的源。** 对于带有`--source`/`--site`/`--region` CSV标志的命令：如果用户请求N个源，输出是否显示N个，或者stderr解释了缺失的源？对fan-out命令，失败的源静默丢失是顶级失败模式。
> 4. **结果排序/排名合理。** 对于声称要排名或排序的命令，顶部结果在给定查询的情况下是否看起来合理？注意损坏的分数权重、排序错误和相关性计算失败时静默回退到最新日期。
>
> 学习循环命令样本的校准（`recall`、`learnings`、`playbook`）：在新鲜打印时，本地学习存储为空，因此空候选列表、零计数的`learnings stats`和"未记录学习"输出是合理的正确。不要将其标记为静默失败或缺失数据。
>
> 返回发现列表。对于每个发现：检查名称、严重性（Wave B中的`warning`；Wave C保留`error`）、单行描述、单句修复建议。如果CLI通过所有四个检查，则返回"PASS — 无发现"。

### 第3步：发出结构化结果块

以`---OUTPUT-REVIEW-RESULT---`块结束技能响应，父级解析此块：

**干净通过：**

仅在使用审查代理评估至少一个符合条件的`status: pass`样本时使用此结果。

```
---OUTPUT-REVIEW-RESULT---
status: PASS
findings: []
---END-OUTPUT-REVIEW-RESULT---
```

**警告：**

```
---OUTPUT-REVIEW-RESULT---
status: WARN
findings:
- check: <check-name>
  severity: warning
  description: <单行>
  suggestion: <单句>
- ...
---END-OUTPUT-REVIEW-RESULT---
```

**审查代理失败或无可评估输出（超时、代理预算耗尽、缺少live-check数据或零符合条件的`status: pass`样本）：**

```
---OUTPUT-REVIEW-RESULT---
status: SKIP
reason: <单行描述>
findings: []
---END-OUTPUT-REVIEW-RESULT---
```

## Wave B策略（当前）

- 所有发现均以`warning`形式呈现——永不以`error`形式呈现。shipcheck继续进行。
- 调用者将发现记录到运行的艺术品目录（例如，`manuscripts/<api>/<run>/proofs/phase-4.85-findings.md`）并暴露给用户。发现不会持久化到`scorecard.json`——该路径保留给Wave C。
- 用户决定在发货前是否修复。

**非交互式合同（CI、cron、批量再生）：**

- 如果stdout不是TTY，调用者遵循故障开放记录日志：记录发现，shipcheck在不提示的情况下继续。
- `status: SKIP`（审查代理崩溃、超时、缺失数据）是信息性的——shipcheck不会因此阻塞。
- 尚无`--auto-approve-warnings`标志。策略已经是Wave B中"警告不阻塞"，因此该标志没有效果来控制。

Wave C（单独的未来PR）将在库的校准数据显示误报率低于10%后，将`error`严重性发现转换为阻塞。

## 为什么选择代理而非模板

输出合理性问题无法通过源进行模式匹配。基于规则的live-check规则覆盖了正则表达式可以覆盖的内容（数字HTML实体、查询标记缺失）。其他所有内容——"这些替换结果对查询而言在语义上是否正确？"、"顶部搜索结果看起来相关吗？"——是LLM形状的问题。标记成本是有限的（每次运行一次，而不是每个命令），并且针对这一阶段动机的bug类捕获率证明了派发。

## 已知的盲点

- 无法验证数字准确性（价格、评分、排名与真实情况）。如果CLI说一个食谱有4.8星，而实际上有4.2星，这项技能不会捕获它。
- 无法检测数据新鲜度问题（2019年发布的食谱与2024年）。这些问题需要与权威来源进行实时比较。
- 无法判断主观偏好（"这是巧克力曲奇的最佳食谱吗？"）。
- 仅样本输出——覆盖`live_check.features[]`中的命令。完整命令树覆盖属于主打印机技能的Phase 5 dogfood，而非此审查。
- 非英语输出：审查代理的查询意图检查假设英语语言的查询/输出。对于非英语CLI，请单独校准提示。
