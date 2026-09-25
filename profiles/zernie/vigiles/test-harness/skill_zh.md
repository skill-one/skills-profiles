测试 Claude 代码 **测试框架** — 包括钩子、技能、设置以及 CLAUDE.md 文件，这些文件指导代理的行为 — 以其作为组装机器的形式进行测试。vigiles 提供三个层级，从最便宜的开始；这个技能会选择正确的层级，编写测试，并运行它。

指导原则：**从能够回答问题的最便宜层级开始，只有在确实无法回答时才升级。** 三个层级中的两个不需要模型和 API 密钥，因此它们在每次提交时都可以免费运行 — 只有当问题实际上需要真实模型时，才使用付费的真实模型层级。

## 第 0 步 — 选择层级（判断调用）

将你要测试的内容与能够回答它的最便宜层级进行匹配：

| 你要测试的内容                                                                                                                    | 层级              | 成本                                             | API                                                                                           |
| -------------------------------------------------------------------------------------------------------------------------------------- | ----------------- | ------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| "这个钩子是否阻止/允许事件 X？" — 纯粹的钩子逻辑，**所有**事件类型（包括编辑/写入、预压缩、会话结束、子代理停止） | **单元测试**      | 免费，毫秒，不需要 `claude`                  | `runHook`                                                                                     |
| "钩子是否实际**连接到**组装好的插件，并且在真实会话中是否触发？"                                         | **确定性测试**    | 免费，不需要 API 密钥（真实 `claude` + 脚本模拟） | `runHarnessTest` + `scriptModel`                                                              |
| "注入的上下文（会话开始钩子、`/command`）是否实际**到达模型**？"                                           | **确定性测试**    | 免费，不需要 API 密钥                                 | `runHarnessTest` → `trace.modelRequests` / `assertRequestContains`                            |
| "这个技能的**描述**在应该触发时是否触发（召回），在不应该触发时是否保持安静（精确）？"                  | **评估测试**      | **付费**（真实模型）                            | `measureTriggerRate` (+ `irrelevantPrompts`) → `assertTriggerRate({ min, maxFalsePositive })` |
| "我能否在**更便宜的模型**上测量触发，并信任它作为底线？"                                                             | **评估测试**      | **付费**（两次运行）                              | `compareContainment(weak, strong)` → `formatContainment`                                      |
| "这个技能的**输出是否良好**？" — 绝对质量，没有开/关基线（测试单个技能的默认情况）                | **评估测试**      | **付费**（真实模型）                            | `measure({ checks: [judged(rubric)] })` → `assertRates({ min })`                              |
| "这个测试框架是否改变**代理的行为**，相对于关闭状态？" — A/B 提升、回归、信号与噪音                    | **评估测试**      | **付费**（真实模型）                            | `runEval` (arm) + `assertSignificant`                                                        |

大多数测试框架问题 — 阻止/允许、连接、上下文到达 — 从来不需要模型。只有 "模型是否触发/行为不同" 需要评估层级。

⚠️ **在所有提示上触发率为 0% 是一个接线错误，除非另有证明。**
它看起来像是对描述的裁决，并且三个独立的设置错误会导致它：在 `fired` 中使用**裸** ID，而命名空间 `<plugin>:<skill>` 是必需的；在 `pluginDir` 中使用松散的 `.claude/skills` 需要 **`skillsDir`**；以及缺少 **`fixture`**，因为运行开始于一个空目录，并且关于不存在的文件的提示是模型正确拒绝的。在报告之前排除所有这三个问题。（部分率是一个真实数字 — 不要怀疑它。）

**在检查到它实际上是底线之前，不要针对更便宜的模型进行调优。**
`compareContainment(weak, strong)` 回答了这个问题：它报告在弱模型上触发但在强模型上未触发的提示，并且每个提示都意味着弱模型不是一个下限，而是一个 _不同的路由器_。只在强模型上触发的提示是预期的，并且不是失败。测量一次（21 个技能，84 个提示，haiku 对 sonnet）：**3 个仅弱模型，并且一个技能在 haiku 上更高** — 所以包含性没有建立，这就是底线保持的原因。

如果单元测试和确定性测试层级都能回答它，**优先选择单元测试**：它更快，并且可以触发确定性模拟无法驱动的事件。

## 第 0.4 步 — 观察运行，以及它的成本

有两个问题有自己的参考 — 打开你需要的一个，不要猜测：

- **"运行实际做了什么？"** — 它调用了哪些工具，是否保持在它声明的 `allowed-tools` 内部，它写了什么，如何记录一个调用而不执行它 → [`references/observing-a-run.md`](references/observing-a-run.md)
- **"这是免费的、子定价的，还是需要容器？"** — 三个桶，以及在付费运行后告诉用户什么 →
  [`references/cost-and-expectations.md`](references/cost-and-expectations.md)

在确定第二个问题之前，永远不要说 "我们会测试它"。

## 第 1 步 — 确保 vigiles 已安装

检查 `vigiles` 是否是一个依赖项（`package.json`），如果不是，则将其作为开发依赖项安装：

```bash
npm i -D vigiles    # 或者： pnpm add -D vigiles / yarn add -D vigiles
```

确定性测试层级还需要 PATH 上的 `claude` CLI（不需要 API 密钥）：`npm i -g @anthropic-ai/claude-code`。评估测试层级需要模型授权。如果 `claude` CLI 缺失，您仍然可以编写和运行 **单元测试** 层级的测试。

## 第 2 步 — 定位要测试的测试框架表面

按顺序找到项目实际交付的内容：

1. `.claude/settings.json` / `.claude/settings.local.json` — 内联 `hooks`。
2. `.claude-plugin/plugin.json` — 一个插件清单（`hooks`、`skills`、`agents`、`mcpServers`）。
3. `hooks/hooks.json` — 插件钩子约定（例如 obra/superpowers）。
4. `skills/<name>/SKILL.md`，`agents/<name>.md`，`commands/<name>.md`。

选择一个具体的东西来确定 — 一个特定的 `PreToolUse` 钩子，一个特定的 `SessionStart` 注入，一个特定的技能。

## 第 3 步 — 为所选层级编写测试

每个层级的骨架，以及一个静默地吞噬失败的错误（一个手滚的运行器吃 stderr）→
[`references/writing-tests.md`](references/writing-tests.md)

在编写文件之前阅读它 — 骨架因层级而异，运行器警告花费了真实的调试时间。

## 第 4 步 — 运行它

在一个运行器（node:test / vitest / jest）中，测试是普通的异步函数。或者使用零配置的 CLI，它发现并运行文件：

```bash
npx vigiles test                 # *.harness.{mjs,ts} — 单元测试 + 确定性测试，不需要 API 密钥
npx vigiles eval --trials=6      # *.eval.{mjs,ts} — 真实模型（本地 / 夜间，不是 CI）
```

单元测试层级的 `runHook` 测试不需要 `claude`，并且**总是运行** — 即使没有安装 `claude`，也要编写和运行它们。一个确实无法运行的层级报告一个响亮的 `⊘ SKIPPED`（单独统计，永远不会是假的 `✓`）；一个独立脚本通过 `vigiles` 的 `skip(reason)` 发出一个。跳过默认通过，但在 CI 工作中断言功能存在，运行 **`vigiles test --no-skip`** 以确保跳过的层级失败 — 一个带跳过的绿色是未测试的表面。在 CI 中保持单元测试 + 确定性测试；在本地或按计划运行评估，使用授权。

## CI — 不要手写步骤

这些层级属于 CI，并且有一个发布的 Action。运行 `vigiles init`：它写入 `.github/workflows/vigiles.yml`，为可以使用它的作业连接 Action (`zernie/vigiles@v1`)，以及一个普通的 `npx vigiles test` 作业为本层级 — 那个作业需要本地 `node_modules`，Action 不会安装它，所以它故意保持手写。

如果存储库已经有一个工作流，Action 的输入在 [docs/github-action.md](../../docs/github-action.md) 中有说明。在那里阅读它们，而不是猜测：输入列表在 `action.yml` 中定义，并且在这里的副本是第二个来源的真实信息，如果没有注意到就会过时 — 这正是这个文件自己的兄弟文档和消费者 CI 评论发生的情况，这两个都在 2026-08-18 测量。

## 第 5 步 — 锁定评估，使 CI 保持诚实（你将自动这样做）

真实模型的评估在用户的订阅上运行 — 本地，永远不会在 CI 中。所以 **作为编写评估的一部分，你保持其结果对它们新鲜。** 做这两件事，不要被要求：

1. **给每个评估一个 `name`。** 那是锁键的。
2. **运行后，提交锁：**

   ```bash
   vigiles eval --update      # 记录结果 → .vigiles/eval-locks/<name>.lock.json
   ```

   然后提交那个文件。CI 运行 `vigiles eval --check`（没有模型）来验证它是否仍然与输入匹配 — 所以一个后来的编辑忘记重新评估会响亮地失败，而不是交付过时的数字。

**当你后来更改一个技能的描述或提示时，重新运行 `vigiles eval --update` 并提交更新的锁** — 变更改变了评估测量的内容。（vigiles 也会提醒你：当锁存在时，`SKILL.md` 编辑会触发一个非阻塞提醒。）

为什么它很便宜：`--check` 只散列输入（技能文本、提示、模型）。一个**阈值**变化的测试会重用保存的数字（没有模型）；只有**输入**变化需要新的 `--update`。完整机制：
[`docs/harness-testing.md`](../../docs/harness-testing.md#keep-eval-results-fresh-in-ci-the-lock)。

## 当用户没有说明要测试什么

不要让他们指定 — **选择一些真实的东西并展示。** 扫描测试框架表面（第 2 步），选择最便宜的具有意义的测试，编写它，运行它，并显示结果。好的默认选择，按顺序：

1. 一个 `PreToolUse` 钩子 → **单元测试**，它阻止它应该阻止的东西（并允许一个安全的兄弟）。
2. 一个注入上下文的 `SessionStart` 钩子 → **确定性测试**，文本实际到达模型 (`assertRequestContains`)。
3. 一个技能 → **确定性测试**，它通过 `pluginDir` 解析，然后提供付费的 `measureTriggerRate` 评估作为后续。

然后说明你使用了哪个层级以及原因，并提议升级层级，如果更便宜的测试不能完全回答他们的问题。

## 参考

完整指南 — 每个层级，为真实模型测试技能，"fired ≠ landed"，默认安全的沙盒，覆盖矩阵，以及它如何与 promptfoo 比较 — 在 [`docs/harness-testing.md`](../../docs/harness-testing.md) 中。
