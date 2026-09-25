Cavecrew = 三个发出原始人输出的子代理预设。与Anthropic默认设置（`Explore`，编辑式代理，审阅者）功能相同；区别在于它们返回的工具结果被压缩，因此每次委托时主上下文会缩小。

## 何时使用cavecrew与替代方案

| 任务 | 使用 |
|---|---|
| "X在哪里定义 / 哪些调用Y / 列出Z的使用情况" | `cavecrew-investigator` |
| 相同，但你还想获得建议/架构评论 | `Explore`（原味） |
| 手术式编辑，≤2个文件，范围明显 | `cavecrew-builder` |
| 新功能 / 3个以上文件 / 跨越重构 | 主线程或`feature-dev:code-architect` |
| 审阅差异、分支或文件的错误 | `cavecrew-reviewer` |
| 带有理由和替代方案的深度代码审阅 | `Code Reviewer`（原味） |
| 你已经知道的简短答案 | 主线程，无子代理 |

经验法则：**如果你希望子代理的输出减少1/3的token，请选择cavecrew。如果你希望获得散文，请选择原味。**

## 这样做的目的（真正的优势）

子代理的工具结果会原封不动地注入到主上下文中。一个返回2k token散文的`Explore`每次都会消耗2k token的主上下文预算。来自`cavecrew-investigator`的相同发现返回约700 token。在一个会话中进行20次委托，这将是上下文耗尽和完成任务之间的区别。

## 输出契约

每个代理主线程可以依赖的内容：

**`cavecrew-investigator`**
```
<Header>:
- path:line — `symbol` — 短评
totals: <计数>.
```
或者`No match.` 始终以文件路径优先，附带行号，反引号符号。可以用`path:\d+`安全地进行grep。

**`cavecrew-builder`**
```
<path:line范围> — <更改≤10个词>.
verified: <重新阅读OK | 不匹配 @ path:line>.
```
或者以下之一：`too-big.` / `needs-confirm.` / `ambiguous.` / `regressed.`（第一个词为终端）。

**`cavecrew-reviewer`**
```
path:line: <emoji> <严重性>: <问题>. <修复>.
totals: N🔴 N🟡 N🔵 N❓
```
或者`No issues.` 查找结果按文件→行升序排序。

## 链式模式

**定位→修复→验证**（最常见）：
1. `cavecrew-investigator`返回站点列表。
2. 主线程选择1-2个站点，将路径交给`cavecrew-builder`。
3. `cavecrew-reviewer`审计差异。

**并行侦察**（当调查范围较广时）：
在一个消息中启动2-3个`cavecrew-investigator`调用（不同角度：定义vs调用者vs测试）。在主线程中聚合。

**一次性编辑**（当站点已知时）：
跳过调查者。直接将确切的路径:行交给`cavecrew-builder`。

## 不要这样做

- 当你不知道文件时，不要使用`cavecrew-builder`。先启动调查者，否则主线程会消耗传递上下文的token。
- 不要将`cavecrew-investigator → cavecrew-builder`用于5个文件的重构。构建者将返回`too-big.`，并且你会浪费一回合。
- 不要要求`cavecrew-reviewer`提供“一般反馈”——它只返回查找结果，不提供架构意见。使用`Code Reviewer`来获取这些。
- 不要期望散文。Cavecrew输出是结构化的，有时简洁到近乎晦涩。如果人类将直接阅读它，请释义。

## 自动清晰（继承）

子代理将原始人语言转换为正常英语，用于安全警告、不可逆操作确认以及任何可能被误读的片段输出。之后恢复原始人语言。
