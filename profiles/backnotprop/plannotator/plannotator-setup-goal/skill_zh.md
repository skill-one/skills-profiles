# 设置目标

通过结构化探索、用户访谈和代码库探索，将一个想法转化为 `goals/<slug>/` 中的目标包。

## 阶段

### 1. 重述

用自己的话陈述用户想要什么。如果对话已经具有丰富的上下文，请总结它。如果目标是简单的或模糊的，对代码库进行最小的浅层探索以建立你的理解。保持 2-3 句话。在继续之前，等待用户确认或纠正。

一旦明确了 slug，就创建目标目录：

```bash
mkdir -p goals/<slug>
```

使用 `goals/<slug>/` 作为工作 JSON 文件和最终文档的目录。JSON 文件是来源和迭代状态；Markdown 文件是人类可读的权威目标包。

**浏览器会话耐心规则**：Plannotator 目标设置是一个由用户驱动的浏览器会话。在启动访谈或事实命令后，要绝对耐心，并等待用户提交、关闭或明确要求你停止。不要因为 UI 空闲或用户花费时间而关闭、杀死、重启、刷新或打开第二个副本。永远不要关闭并重新打开会话作为更新状态的方式；如果先前会话结束后需要重新运行，请更新工作 JSON 文件并从该文件启动新命令。

**可选：先进行深度访谈（一次一个问题的深入访谈）。** 在构建紧凑的访谈包之前，每当目标是模糊的或包含许多相互依赖的决策时，*建议* 进行一次深度访谈，并在用户要求时运行（“先访谈我”）。这是可选的：对于清晰、范围明确的目标，直接跳到包，这样访谈就不会与包的“较少、更高杠杆的问题”理念相冲突。当你进行访谈时，逐字运行以下协议，然后将已解决的决策转发到更高质量访谈包（阶段 2）——或者，如果访谈完全解决了范围，则直接进入事实表（阶段 3）。

<!-- 以下访谈协议逐字改编自 Matt Pocock 的 /grill-me 技能（MIT 许可证）：
     https://github.com/mattpocock/skills/blob/main/skills/productivity/grill-me/SKILL.md -->

> 在我们达成共同理解之前，就这个计划的各个方面对我进行无情的访谈。逐步深入每个设计分支，逐一解决决策之间的依赖关系。对于每个问题，提供你的推荐答案。
>
> 一次只问一个问题。
>
> 如果一个问题可以通过探索代码库来回答，就探索代码库而不是提问。

### 2. 访谈包

构建一个紧凑的问题包，可以导出这个目标应该产生的每个“事实”。将问题打包在一起，以便用户可以在 Plannotator 目标设置 UI 中快速回答它们。对于每个问题，包括你的推荐答案，并在选项使回答更快时使用选项。

不要问明显的确认问题。如果答案可以从用户的请求、对话或浅层代码库探索中推断出来，请推断并继续。如果某个明显领域具有有意义的细微差别，请将推断的答案作为推荐选项或自定义“添加/纠正此内容”路径来呈现，而不是要求用户重新陈述明显的内容。

通常重要的问题领域：

- 功能/变更是什么
- 它是为谁准备的
- 它解决了什么问题
- 行为将如何改变
- 成功看起来像什么
- 范围内和范围外的内容（确定事实的最重要领域）
- 需要考虑哪些边缘情况
- 适用哪些约束或先例

**如果一个问题可以通过探索代码库来回答，就探索代码库而不是提问。** 只包括用户实际需要判断的问题。优先考虑较少、更高杠杆的问题，而不是详尽的明显问题。

在向用户展示之前编写访谈包：

`goals/<slug>/interview.json`

```json
{
  "stage": "interview",
  "title": "简短的人类可读标题",
  "goalSlug": "<slug>",
  "questions": [
    {
      "id": "scope",
      "prompt": "什么应该在范围内？",
      "description": "可选的澄清。",
      "answerMode": "multi-custom",
      "recommendedAnswer": "你的推荐答案。",
      "recommendedOptionIds": ["ui", "server"],
      "options": [
        { "id": "ui", "label": "UI" },
        { "id": "server", "label": "服务器" }
      ],
      "required": true
    }
  ]
}
```

支持的 `answerMode` 值：`text`、`single`、`multi`、`custom`、`single-custom`、`multi-custom`。

以监控的前台进程运行此命令，并耐心等待浏览器会话结束。当用户阅读、编辑或提问时，命令可能会出现空闲状态；保持运行：

```bash
plannotator setup-goal interview goals/<slug>/interview.json --json
```

命令在标准输出上返回提交的答案的 JSON。在继续之前，将确切的结果写入 `goals/<slug>/interview-result.json`。一个方便的模式是：

```bash
plannotator setup-goal interview goals/<slug>/interview.json --json | tee goals/<slug>/interview-result.json
```

如果用户在会话结束后进行修订，请更新 `interview.json` 并重新运行命令，而不是从记忆中重建整个包。如果会话被关闭，请停止并告诉用户目标设置已关闭。

在进入事实之前，仔细阅读每个答案并注意：

- 如果用户在答案或注释中写了问题、不确定性、“不确定”、“需要上下文”或类似的关注点，请在聊天中停止并解决这些问题。在用户有足够的上下文或你重新运行修订后的访谈包之前，不要继续进入事实。
- 如果用户在注释中跳过了一个问题，请将注释视为有意反馈，而不是空答案。回答注释，改进问题，或在继续前进行记录的假设。
- 如果用户没有注释就跳过了一个问题，只有在缺失的答案不会造成阻塞的情况下才继续；否则，在聊天中询问最小的可能后续问题。

### 3. 事实表

事实是对目标每个结果的简单描述。它应该是易于测试和验证的。事实可以描述特定功能的函数或系统的某个方面。事实可以确定特定的 UI 和 UX。再次强调，事实就是任何可以在自动化或手动测试中测试和验证的东西。保持事实语言简单。在某种意义上，事实表是一个设计规范，但更简洁，并使用人类用户可以轻松可视化和合理化的语言。

从 `goals/<slug>/interview-result.json` 准备事实审查包。每个事实都应包括是否推荐自动化验证以及预选。

在向用户展示之前编写事实审查包。如果在对先前事实进行修订后，从 `facts-review.json` 和 `facts-result.json` 开始，包括先前接受的事实（`"accepted": true`），并保留其状态。

`goals/<slug>/facts-review.json`

```json
{
  "stage": "facts",
  "title": "简短的人类可读标题",
  "goalSlug": "<slug>",
  "facts": [
    {
      "id": "fact-1",
      "text": "接受的事实文本。",
      "accepted": false,
      "removed": false,
      "recommendedAutomatedVerification": true,
      "automatedVerification": true
    }
  ]
}
```

以监控的前台进程运行此命令，并耐心等待浏览器会话结束。当用户审查、编辑或提问时，命令可能会出现空闲状态；保持运行：

```bash
plannotator setup-goal facts goals/<slug>/facts-review.json --json
```

命令在标准输出上返回接受的/编辑的/删除的事实以及自动化验证选择。在继续之前，将确切的结果写入 `goals/<slug>/facts-result.json`。一个方便的模式是：

```bash
plannotator setup-goal facts goals/<slug>/facts-review.json --json | tee goals/<slug>/facts-result.json
```

将 `goals/<slug>/facts.md` 作为接受事实的扁平可读列表编写。每个事实是一行；只有在事实本身无法清晰陈述时才添加最小的注释。还编写 `goals/<slug>/facts.meta.json`，保留每个接受事实的 `id`、最终 `text`、`comment`、`recommendedAutomatedVerification` 和 `automatedVerification` 值。

如果用户在 UI 中编辑或删除了事实，请直接应用该结果。如果会话被关闭，请停止并告诉用户事实审查已关闭。

### 4. 计划

探索代码库。发现并验证每个接受事实的实施路径。将 `automatedVerification: true` 的事实视为需要具体的自动化检查，除非你记录了障碍。跟踪代码，识别涉及的文件和系统，暴露风险和未知因素。直到你有了自信的操作顺序。

编写 `goals/<slug>/plan.md`：

- 解决方案方法（简要）
- 带有每个文件/系统触发的有序步骤
- 每个步骤的验证（具体的命令或检查）
- 值得标记的风险或开放问题

使用 Plannotator 管理计划：

```bash
plannotator annotate goals/<slug>/plan.md --gate
```

如果被拒绝，根据反馈进行修订并重新管理，直到获得批准。

### 5. 目标输出

编写 `goals/<slug>/goal.md`：

- 陈述的目标（1-3 句话）
- 引用 `facts.md` 作为共同理解
- 引用 `plan.md` 作为执行计划
- 完成条件

告诉用户：

```
完成！使用 `/goal goals/<slug>/goal.md` 启动目标
```
