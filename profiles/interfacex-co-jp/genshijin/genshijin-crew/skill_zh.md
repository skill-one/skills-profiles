genshijin-crew = 以原始人形式输出的3个子代理预设。角色与Anthropic默认 (`Explore`、编辑系代理、reviewer) 相同。区别在于返回的tool-result已压缩 → 主上下文消耗在每次委派时减少。

## genshijin-crew 与替代方案的选择

| 任务 | 使用 |
|---|---|
| 「X的定义在哪里 / 调用Y的位置 / Z的所有用法」 | `genshijin-investigator` |
| 同上 + 需要架构说明/建议 | `Explore` (vanilla) |
| 手术式编辑、≤2文件、范围明确 | `genshijin-builder` |
| 新功能 / 3+文件 / cross-cutting重构 | 主线程 or `feature-dev:code-architect` |
| Diff/分支/文件的bug评审 | `genshijin-reviewer` |
| 附有rationale + alternatives的深度代码评审 | `Code Reviewer` (vanilla) |
| 1行回答且内容确定的 | 主线程、无需子代理 |

判断标准: **需要子代理输出1/3 tokens则选genshijin-crew、需要散文则选vanilla**。

## 存在的原因 (实用价值)

Subagent的tool-result会逐字注入主上下文。Vanilla `Explore`返回散文2k tokens时，每次会消耗主上下文2k。相同发现用`genshijin-investigator`约需700 tokens。1会话20次委派，context exhaustion与任务完成差距。

## 输出契约

主线程可依赖的子代理输出格式:

**`genshijin-investigator`**
```
<Header>:
- path:line — `symbol` — 简短说明
统计: <counts>。
```
或`No match.` 必须以文件路径开头、带行号、符号用反引号。`path:\d+`可grep。

**`genshijin-builder`**
```
<path:line-range> — <修改≤10词>。
验证: <重读OK | 不符@path:line>。
```
或以下之一: `too-big.` / `needs-confirm.` / `ambiguous.` / `regressed.` (首词为终端状态)。

**`genshijin-reviewer`**
```
path:line: <emoji> <严重性>: <问题>. <修正>.
总计: N🔴 N🟡 N🔵 N❓
```
或`No issues.` 按文件→行排序。

## 链式模式

**定位→修改→验证** (最频):
1. `genshijin-investigator`获取site列表
2. 主线程选择1-2 site并将路径传给`genshijin-builder`
3. `genshijin-reviewer`进行diff审查

**并行探索** (调查范围广时):
1消息并行启动2-3个`genshijin-investigator` (不同角度: 定义vs调用vs测试)。主线程汇总。

**单次编辑** (sit已知时):
跳过investigator。直接将`path:line`传给`genshijin-builder`。

## 禁止事项

- 禁止未确定文件时使用`genshijin-builder`。必须先启动investigator → 否则主线程通过context传递会消耗tokens。
- 禁止5文件重构时使用`genshijin-investigator → genshijin-builder`链。Builder会返回`too-big.` → 浪费回合。
- 禁止向`genshijin-reviewer`请求"总体反馈" → 仅返回findings、无架构意见。此用途请用`Code Reviewer`。
- 禁止期待散文输出。genshijin-crew输出结构化、有时晦涩。若需人类直读，主线程需进行转译。

## 自动切换 (继承)

子代理在安全警告/取消不可操作确认/fragment模糊易误读输出时，会从原始人切换至正常日语。对应部分后恢复。
