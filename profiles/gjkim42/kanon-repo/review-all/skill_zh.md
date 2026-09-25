# 全部审查 - 两个 clean-agent 代码审查

## 这是什么，以及为什么它有这样的形状

两个独立的审查者审查同一个变更，然后他们的发现将被协调。价值不在于"两次审查"；它在于**一致信号**：当两个 clean-agent 独立地标记出同一个问题时，信心很高。当只有一个标记某事时，它值得审查。

四个属性使该信号有用，并且该程序存在以保护它们：

1. **每个审查者一个干净的上下文。** 每个审查者必须从零开始，没有对该编排的记忆或对彼此的记忆，否则他们不再独立。生成两个具有干净上下文的代理；如果代理 API 支持一个 `fork_context` 标志，将其设置为 `false`。不要将任何一个审查者的输出粘贴到另一个审查者中。
2. **同一个目标。** 一致性只有在两个都查看了完全相同的 diff 时才有意义。一次性解决目标，并将相同的 `base...HEAD` 范围交给两个。
3. **两个互补的审查路径。** 一个 clean-agent 运行 Codex 的原生 `codex review --base "$base"` 命令。另一个 clean-agent 使用 `references/review-guide.md` 进行直接审查，该文件基于 Google 的 "代码审查中需要查找的内容"：
   https://google.github.io/eng-practices/review/reviewer/looking-for.html
4. **真实的并行性。** 在等待任何结果之前生成两个代理。不要串行化审查。

这项技能是**仅用于审查**的。永远不要传递 `--fix` / `--comment`，永远不要应用补丁，并且永远不要告诉用户你即将更改代码。

## 不是 PR 完成循环

这项技能应该在批量修复后运行一次，或者在第二次批量修复后最多再运行一次，如果仍然存在有效的 P0-P2 发现。不要在每次单个修复后重新运行 `review-all`。

## 程序

### 第 1 步 — 解决共享目标（一个基础，一个范围）

目标是 `base...HEAD`（当前分支的合并基 diff），因此两个审查者都看到该分支添加的确切提交。

```bash
current=$(git rev-parse --abbrev-ref HEAD)

# 基础优先级：用户提供的 --base > origin 的默认分支 > main > master
base="$ARG_BASE"   # 用户传递的任何内容，可能为空
if [ -z "$base" ]; then
  base=$(git symbolic-ref --quiet refs/remotes/origin/HEAD 2>/dev/null \
         | sed 's@^refs/remotes/origin/@@')
fi
[ -z "$base" ] && git show-ref --verify --quiet refs/heads/main   && base=main
[ -z "$base" ] && git show-ref --verify --quiet refs/heads/master && base=master

echo "current=$current base=$base"
git diff --shortstat "$base"...HEAD
git diff --name-only "$base"...HEAD
```

### 第 2 步 — 预飞行（快速失败，不要浪费审查）

如果任何以下情况成立，就停止并明确告诉用户：

- 不在 git 仓库内。
- 无法解析基础分支 → 询问用户要 diff 的基础分支。
- `current` *是* 基础分支 → 没有可比较的内容；请求一个基础。
- diff 为空 (`git diff --shortstat "$base"...HEAD` 输出为空) → 没有要审查的已提交变更。提醒用户此模式仅审查**已提交**的变更；如果他们的工作未提交，他们应该先提交。
- Codex 未准备就绪：`codex login status` 没有报告已登录的账户。报告它并提议单独运行 Google-rubric 审查。

### 第 3 步 - 并行生成两个干净的代理

使用当前环境中可用的代理/子代理设施。在等待任何结果之前启动两个审查代理。如果 API 暴露 `fork_context`，将每个代理的该标志设置为 `false`。给每个代理仅提供仓库路径、解析的基础及其任务。

**代理 A：Codex 审查命令代理**

任务提示：

> 你是一个干净上下文的审查命令运行者。在 `<repo path>` 中的仓库中，对已提交分支 diff 运行 Codex 的原生审查命令：
>
> `codex review --base <base>`
>
> 这是仅用于审查。不要传递 `--fix` 或 `--comment`，不要向 GitHub 发布任何内容，也不要修改文件。返回原生命令输出，如果可能，返回一个归一化的 JSON 数组中的发现：
> `{"file":"...","line":<int or null>,"priority":"P0|P1|P2|P3","category":"design|functionality|complexity|tests|naming|comments|consistency|documentation|security|other","title":"<one line>","description":"<evidence and impact>"}`。
> 如果命令未发现任何问题，在原始输出摘要后返回 `[]`。如果命令失败，返回确切的失败信息并停止。

**代理 B：Google-rubric 审查代理**

阅读此 `SKILL.md` 旁边的 `references/review-guide.md`，然后给代理此任务，并将完整的 rubric 粘贴进来：

> 你是一个具有干净上下文的独立代码审查者。在 `<repo path>` 中的仓库中，仅审查 `git diff <base>...HEAD` 中的已提交变更。应用此审查 rubric，基于 Google 的 "代码审查中需要查找的内容"：
>
> <粘贴 `references/review-guide.md` 的全部内容到这里>
>
> 限制：这是仅用于审查。不要传递 `--comment` 或 `--fix`，不要向 GitHub 发布任何内容，也不要修改任何文件。使用系统上下文作为判断已更改行的透镜，但将每个发现锚定到 diff（已更改的行，或变更本应触及但未触及的内容，如缺失的测试）。跳过 linter、格式化程序、类型检查器或编译器会捕获的琐碎问题。
>
> 将你的发现以 JSON 数组的形式返回给我，别无其他。每个发现：
> `{"file": "...", "line": <int or null>, "priority": "P0|1|2|3",
> "category": "design|functionality|complexity|tests|naming|comments|consistency|documentation|security|other",
> "title": "<one line>", "description": "<为什么这是一个问题，附带证据>"}`。
> 根据 rubric 的 P0–P3 标度分配 `priority`。如果你未发现任何问题，返回 `[]`。如果变更做得很好，你可以添加一个优先级为 `P3` 且类别为 `other` 的发现，标题为 "良好：…"。

在两个代理都已生成后，等待它们的结果。

### 第 4 步 — 收集两个结果

- 等待 Google-rubric 审查代理的 JSON。
- 等待 Codex 审查命令代理的原始输出和/或归一化 JSON。
  **语义地解析原生 Codex 输出**；不要依赖严格的正则表达式。
  原生审查者的输出通常如下所示：
  - 一个前言块（Codex 版本、工作目录、模型，以及 diff 和它运行的 shell 命令的转储）—**跳过所有内容**。
  - 发现出现在 `codex` 标记后，作为摘要行，后跟 `Full review comments:` 和一个列表，其中条目形状如 `- [P2] <title> — <path>:<start>-<end>`，每个条目下方有一个描述段落。每个条目是一个发现。
  - 发现块通常打印两次（流式传输，然后作为最终消息重复）。去重 — 它是相同的发现，不是新的。
  - Codex 已经为每个发现标记 `[P0]`–`[P3]`；保留这些标签 — 它是 Google-rubric 审查者使用的相同标度，因此不需要重新映射。
  - 无害的 `git: warning: confstr()` / `xcrun_db` 行来自只读沙盒；忽略它们。

如果一个方面失败（Codex 出错，一个代理返回了不可用的内容），继续使用你拥有的内容并明确在报告中说明 — 半个审查清楚地标记比沉默的空白更好。

### 第 5 步 — 合并、去重、排序

将双方归一化为相同的发现形状，然后进行协调：

- **去重**：通过相同的文件 + 重叠/相邻的行 + 相同的底层问题（语义匹配，不是字符串匹配 — 两个代理会用不同的措辞描述）。
- **标记每个发现的来源**：`both`、`google` 或 `codex`。
- **解决优先级**：对于每个合并的发现，如果两个审查者都标记了它但分配了不同的优先级，取**较高**（更严重）的，并注明分歧。
- **排序**：主要按优先级（P0 → P3）。在同一优先级级别内，首先列出两个代理都同意的发现 — 独立同意是这个技能产生的最强信心信号。
- **暴露分歧**：如果两个代理在某个东西是否是错误上存在分歧，简要显示两个立场。这种张力往往是报告中最有用的部分。

### 第 6 步 — 提交一个统一的报告

首先是一个结论，然后是一个优先级概述表，然后按优先级级别分组列出发现。为每个发现标记其优先级、来源（`both` / `google` / `codex`）及其 rubric 维度。

```
## Review-all: <current> vs <base>  (<N> 文件，+<adds>/-<dels>)

**结论：** APPROVE / REQUEST CHANGES / COMMENT
**整体正确性：** patch 是正确的 / patch 是错误的
Codex 审查和 Google-rubric 审查独立地审查了相同的 diff；<X> 发现被同意。

### 发现概述
| 优先级 | 计数 | 来源 | 摘要 |
| ------ | ---- | ---- | ---- |
| P0 | <n> | <file:line 或 —> | <简短或 "无"> |
| P1 | <n> | … | … |
| P2 | <n> | … | … |
| P3 | <n> | … | … |

### P0      ← 仅显示有发现的级别
1. [P0] **<标题>** — `file:line` · _both_ · 功能性
   <合并的描述>

### P1
...

### P2
...

### P3
...
```

根据优先级推导结论（与 kelos 审查者使用的逻辑相同）：

- **整体正确性** 如果有任何 P0 或 P1 发现；否则 "patch 是正确的"。忽略 P2/P3 的琐碎问题，以供此调用使用。
- **REQUEST CHANGES** 当存在 P0/P1 时；**APPROVE** 当只有 P2/P3（或无）；**COMMENT** 当你确实需要作者的输入才能决定时。

保持简洁：没有表情符号，引用 `file:line`，明确标记同意的 (`both`) 发现，因为这是最高信心的信号，不要将单模型发现填充起来以看起来像共识。如果两个代理都未发现任何问题，请说明并停止。一个显著的优势可能是在最低级别下有一条 "良好：" 注释 — 事实验证，不是奉承。

## 注意和边缘情况

- **仅审查已提交变更。** `codex review --base` 和 `base...HEAD` 都忽略未提交/未跟踪文件。如果用户希望审查这些文件，他们必须先提交（未来的 `--working-tree` 模式可以覆盖这种情况）。
- **大 diff。** Codex 可能需要较长时间；这正是它在自己的干净代理中运行的原因。不要过早终止它。
- **参数。** 接受一个可选的基础覆盖（例如 `review-all --base develop` 或 `review-all develop`）。如果没有给出，则根据第 1 步自动解析。
- **不要双重审查。** 两个审查者必须获得相同的范围；永远不要让一个漂移到工作树，另一个漂移到分支范围。
