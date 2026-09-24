Cavecrew = 三个以 Caveman 风格输出结果的工作子代理预设。与 Anthropic 默认配置（`Explore`、编辑类工作子代理、评审员）职责相同；区别在于它们返回的工具结果经过压缩，因此每次委派时主上下文都会缩减。

## Cavecrew 与替代方案的使用时机

 | 任务 | 使用 |
 |---|---|
 | "X 的定义位置 / Y 被哪些调用 / Z 的使用列表" | `cavecrew-investigator` |
 | 除了上述内容，还希望获得建议/架构点评 | `Explore`（原生） |
 | 精确修改，≤2 个文件，范围明确 | `cavecrew-builder` |
 | 新功能 / 3 个及以上文件 / 跨模块重构 | 主线程或 `feature-dev:code-architect` |
 | 评审差异、分支或文件中的 bug | `cavecrew-reviewer` |
 | 深度代码评审，需结合理由与替代方案 | `Code Reviewer`（原生） |
 | 你已经知道的一行式答案 | 主线程，无需子代理 |

**经验法则：** **若希望子代理的输出占用 1/3 的 token 即可，选择 cavecrew。若需要散文风格，选择原生方案。**

## 此功能的存在意义（真正的优势）

子代理的工具结果会以原文形式注入主上下文。原生 `Explore` 返回 2k token 的散文，每次都会消耗 2k token 的主上下文预算。`cavecrew-investigator` 返回相同结论仅需约 700 token。在一次会话的 20 次委派中，这决定了任务能否完成（而非上下文耗尽）。

## 输出契约

每个工作子代理，主线程可依赖的输出如下：

**`cavecrew-investigator`**
```
Header:
- path:line — `symbol` — 简短说明
totals: <计数>.
```
或 `No match.` 始终采用"先路径、附行号、加反引号标注符号"的格式。可使用 `path:\d+` 安全地执行 grep。

**`cavecrew-builder`**
```
path:line-range — <不超过 10 词的修改>.
verified: <重读确认 OK | 不一致 @ path:line>.
```
或以下之一：`too-big.` / `needs-confirm.` / `ambiguous.` / `regressed.`（首 token 为终端状态）。

**`cavecrew-reviewer`**
```
path:line: <emoji > <severity>: <problem>. <fix>.
totals: N🔴 N🟡 N🔵 N❓
```
或 `No issues.` 发现按文件 → 行号升序排列。

## 链式调用模式

**定位 → 修改 → 验证**（最常见）：
1. `cavecrew-investigator` 返回位置列表。
2. 主线程选取 1-2 个位置，将路径传递给 `cavecrew-builder`。
3. `cavecrew-reviewer` 审查差异。

**并行侦察**（当调查范围较广时）：
在同一消息中生成 2-3 次 `cavecrew-investigator` 调用（不同角度：定义 vs 调用者 vs 测试）。在主线程中汇总。

**单次修改**（当位置已知时）：
跳过调查员。直接将确切的 `path:line` 交给 `cavecrew-builder`。

## 不应做的事项

- 若你还不清楚文件，不要使用 `cavecrew-builder`。先生成调查结果，否则主线程在传递上下文时会消耗大量 token。
- 不要将 `cavecrew-investigator` 与 `cavecrew-builder` 串联用于 5 文件的重构。Builder 会返回 `too-big.`，导致你浪费了一轮。
- 不要要求 `cavecrew-reviewer` 提供"一般性反馈"——它仅返回发现项，不包含架构意见。此类需求请使用 `Code Reviewer`。
- 不要期待散文。Cavecrew 输出是结构化的，有时简洁到晦涩。若需人工直接阅读，请进行转述。

## 自动清晰度（继承）

子代理在涉及安全警告、不可逆操作确认，以及任何可能因片段歧义被误读的输出时，会将 Caveman 风格转为普通英文。处理完毕后恢复 Caveman 风格。
