# 筛选

通过一组小型筛选角色状态机，在项目问题追踪器中移动问题。

如果这个仓库将外部拉取请求视为请求表面（见问题追踪器配置），筛选也覆盖它们：**PR 是带附加代码的问题**——相同的角色、相同的状态、相同的机，只有下面标记为“针对 PR”的几处差异。按追踪器配置将裸 `#42` 解析为问题或 PR。

筛选期间发布到问题追踪器的每条评论或问题**必须**以此免责声明开头：

```
> *这是在筛选期间由 AI 生成的。*
```

## 参考文档

- [AGENT-BRIEF.md](AGENT-BRIEF.md) — 如何编写持久可用的 agent brief
- [OUT-OF-SCOPE.md](OUT-OF-SCOPE.md) — `.out-of-scope/` 知识库如何工作

## 角色

两个 **类别** 角色：

- `bug` — 某个东西坏了
- `enhancement` — 新功能或改进

五个 **状态** 角色：

- `needs-triage` — 维护者需要评估
- `needs-info` — 等待报告者提供更多信息
- `ready-for-agent` — 已完整说明，准备给 AFK agent 接手
- `ready-for-human` — 需要人工实现
- `wontfix` — 不会处理

对 PR 而言，相同的状态对照附加代码来解读：`ready-for-agent` 表示已附加 brief、agent 应对 diff 采取下一步；`ready-for-human` 表示已准备好由人类 merge。

每个已筛选的问题应该刚好携带一个类别角色和一个状态角色。如果状态角色冲突，标记出来并先询问维护者，再做其他事。

这些是规范角色名称；问题追踪器中实际使用的标签字符串可能不同。映射应该已经提供给你；如果没有，请让用户运行 `/setup-matt-pocock-skills`。

状态转换：未标记的问题通常先进入 `needs-triage`；之后移动到 `needs-info`、`ready-for-agent`、`ready-for-human` 或 `wontfix`。`needs-info` 在报告者回复后回到 `needs-triage`。维护者可以随时 override；对看起来异常的转换标记并在继续前询问。

## 调用

维护者调用 `/triage`，并用自然语言描述想要什么。解释请求并行动。示例：

- "Show me anything that needs my attention"
- "Let's look at #42"（问题或 PR）
- "Move #42 to ready-for-agent"
- "What's ready for agents to pick up?"

## 显示需要关注的内容

查询问题追踪器，并按最旧优先展示三个 bucket：

1. **未标记** — 从未筛选。
2. **`needs-triage`** — 评估正在进行中。
3. **`needs-info` with reporter activity since the last triage notes** — 需要重新评估。

当 PRs 在范围内时，把外部 PRs 纳入这些 bucket，并为每行标注 `[PR]` 或 `[issue]`。Discovery 只浮现 *外部* PRs（tracker 配置定义了谁算外部）——collaborator 正在进行的 PR 不是筛选工作。这个过滤仅用于 discovery；被明确点名的 PR 无论作者是谁都会被筛选。

显示每个 bucket 的数量，以及每个问题的一行摘要。让维护者选择。

## 筛选特定的问题或 PR

1. **收集上下文。** 读取完整问题或 PR（body、comments、labels、author、dates；对 PR 还包括 diff）。解析任何之前的筛选笔记，避免重新询问已解决的问题。使用项目 domain glossary 探索 codebase，并遵守相关 ADRs。对照 codebase 运行两项检查：(a) **冗余**——按 domain concept（而不仅是请求的措辞）搜索所请求 behavior 的现有实现，并报告你查找过的地方。如果找到，那就是一个已实现的 `wontfix`（步骤 5）。(b) **先前的拒绝**——读取 `.out-of-scope/*.md`，并浮现任何与此请求相似的既往拒绝。

2. **建议。** 告诉维护者你的类别和状态建议及理由，并给出与请求相关的简短 codebase summary——包括它是否已经实现。等待指示。

3. **验证声明。** 在任何 grilling 前，检查该声明是否成立。对 bug，从报告者的步骤复现。对 PR，确认 diff 做到了它所声称的——checkout 它，运行相关 tests 或 commands。报告发生了什么：已确认（附 code path）、失败，或细节不足（强烈的 `needs-info` 信号）。已确认的验证会让 agent brief 更有力。

4. **Grill（如果需要）。** 如果请求需要进一步充实，调用两次 Skill 工具，分别指定 `grilling` 和 `domain-modeling`——一轮一轮地把它 grill 成形，在 decisions 落定时打磨 domain terms 并内联更新 `CONTEXT.md`/ADRs。

5. **应用结果：**
   - `ready-for-agent` — 发布 agent brief comment（[AGENT-BRIEF.md](AGENT-BRIEF.md)）。
   - `ready-for-human` — 使用与 agent brief 相同的结构，但说明为什么不能委托（judgment calls、external access、design decisions、manual testing）。
   - `needs-info` — 发布筛选笔记（见下方 template）。
   - `wontfix` — close，comment 取决于*原因*：
     - **已实现** — change 已存在于 codebase 中。指向它所在的位置；**不要**写入 `.out-of-scope/`（那个 KB 是为*被拒绝*的请求准备的，不是为已构建的）。
     - **拒绝（bug）** — 礼貌解释，然后 close。
     - **拒绝（enhancement）** — 写入 `.out-of-scope/`，从 comment 链接到它，然后 close（[OUT-OF-SCOPE.md](OUT-OF-SCOPE.md)）。
   - `needs-triage` — 应用角色。如果有部分进展，可选择 comment。

## 快速状态覆盖

如果维护者说 “move #42 to ready-for-agent”，相信他们并直接应用角色。确认你即将做什么（role changes、comment、close），然后执行。跳过 grilling。如果在没有 grilling session 的情况下移动到 `ready-for-agent`，询问他们是否想写 agent brief。

## Needs-info template

```markdown
## 筛选笔记

**我们已经确定的：**

- 点 1
- 点 2

**我们需要你 (@reporter) 提供的：**

- 问题 1
- 问题 2
```

把 grilling 期间已经解决的所有内容都捕获到 “已确定的” 下，避免工作丢失。问题必须具体且可执行，而不是 “please provide more info”。

## 恢复之前的会话

如果问题或 PR 上已有筛选笔记，读取它们，检查报告者是否回答了任何未解决的问题，并在继续前展示更新后的情况。不要重复询问已解决的问题。
