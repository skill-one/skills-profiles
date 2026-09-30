---
name: loop-factory
description: 运行一个以规范驱动的代理循环，其中编码任务以 Markdown 规范的形式存在，并通过收件箱 → 活动状态 → 归档的流程移动，由 Claude Code 或 Codex 实现，并在通过评审门禁后才被视为完成。当用户提到“循环工厂”、“规范驱动循环”、“代理工厂”，需要可重复/可评审的代理工作，或当代码库包含 factory/specs/inbox 或 factory/specs/active 目录时使用。此外，还涵盖将 loop-factory CLI 框架安装到项目中的操作。
---

# 循环工厂

循环工厂将"让代理构建某物"转化为可见的装配线。每个任务都是一个 markdown **规格**。规格所在的文件夹*就是*它的状态。代理负责实现和验证；它们从不决定要构建什么。

```
   📥 收件箱/          🔧 活动中/           📦 归档/
   未开始的任务        ──► 代理正在构建      ──► 完成的作品,
   尚未开始        ──► 正在构建中        ──► 已审核 + 接受
```

统治一切的唯一规则：**自动化实现和验证，而非产品决策。** 如果规格缺少决策，记录悬而未决的问题——不要编造产品方向。

通过输入 `/loop-factory` (一次手动操作) 来按需调用此技能，或让 cron 自动执行——参见 [自主模式](#自主模式-cron)。

## 使用此技能的场景

- 在仓库中设置循环工厂（安装 CLI，运行 `init`）。
- 从收件箱中挑选规格并将其派发给 Claude Code 或 Codex。
- 根据其验收标准实现规格。
- 审核已完成的工作并将接受的规格归档。
- 将实现经验反向传播到活着的规格/文档中。

## 设置（仓库中的首次操作）

`loop-factory` CLI 是状态引擎。安装一次，然后为任何 git 仓库创建脚手架：

```bash
# 获取 CLI（克隆源代码仓库，安装可编辑的）
git clone https://github.com/JuliusBrussee/Loop-Factory.git
python3 -m pip install -e ./Loop-Factory

# 在目标项目中创建工厂/ 文件夹
cd your-project
loop-factory init
loop-factory doctor      # 确认 git + 代理 CLIs 已配置
```

除了 Python 3.10+ 之外没有其他运行时依赖。如果您已经在 Loop-Factory 仓库中，可以跳过安装并直接运行 `python3 bin/loop-factory <command>`。完整的安装说明、代理-CLI 设置以及如何复制原生代理适配器：**[参考资料/install.md](references/install.md)**。

## 循环流程

1. **检查队列。** 运行 `loop-factory scan` 查看收件箱和活动规格。
2. **先审阅新规格。** 在派发一个新鲜规格之前，逐个问题地审阅它（谁拥有这个决策，什么超出范围，风险最大的假设，最小可接受版本）。在 `# 审阅门` 部分记录答案。模糊的规格会产生模糊的代码。
3. **派发。** 生成实现提示并将规格移动到 `active/`：
   ```bash
   loop-factory dispatch --agent claude --limit 1 --stage
   ```
   这会向 `factory/prompts/` 写入提示，向 `factory/runs/` 写入运行记录。它**不会**运行 AI，除非您添加 `--execute`。
4. **实现。** 仅构建验收标准。匹配现有代码风格。保持范围内。
5. **验证。** 运行规格 `verification:` 前置部分中列出的每个命令。将输出作为证据捕获。
6. **审阅。** 生成审阅提示并检查与标准的差异：
   ```bash
   loop-factory review <spec-id> --agent claude
   ```
   通过 → 归档。失败 → 将规格留在 `active/` 以供再次处理。
7. **归档接受的作品。**
   ```bash
   loop-factory archive <spec-id> --accepted
   ```
   `--accepted` 是有意设置的——没有确认通过，任何东西都不会离开 `active/`。
8. **反向传播。** 如果构建功能改变了系统实际的工作方式，请在不改变产品意图的情况下将此同步到规格/文档中：
   ```bash
   loop-factory backprop --agent claude
   ```

## 自主模式

运行一个自包含的通过，在没有人为干预的情况下耗尽收件箱。在"自主" / "耗尽收件箱"被调用时触发，通过计划的 cron，或通过 `/loop` 重复触发（例如 `/loop 30m /loop-factory`）。

一个通过正好执行以下操作：

1. **扫描** `factory/specs/inbox/`。
2. **仅过滤就绪的规格。** 当规格的审阅门完成时，规格就绪——`grill: completed` 在前置部分，或填写了 `# 审阅门` 部分。跳过任何其他内容并将其记录为"需要审阅"。永远不要自主审阅：审阅门需要人类答案，而编造它们将是决定产品方向。
3. 对于每个就绪的规格：**阶段 → 根据验收标准实现 → 运行验证。**
4. **在审阅门处停止。** 将构建的规格留在 `active/`。**不要**归档——接受仍然是人类决策。
5. 如果验证失败，将规格留在 `active/` 并在 `factory/runs/` 中添加注释。不要在循环中重试或在使其通过的情况下削弱标准。
6. **报告**：已构建，跳过（需要审阅），验证失败——然后停止。

这保持了边界完整：循环是一个不知疲倦的*构建者*，永远不会是一个沉默的*决策者*。

有两种方法可以定期触发它：

- **`/loop`（本地，推荐用于活动工作）** — `/loop 30m /loop-factory` 在任何间隔内重新运行此技能针对您的本地工作树。构建的规格会落在 `active/`；不需要 git 推送或 PR。仅在 Claude Code 会话打开时运行。
- **Cron（云端，无人值守）** — 一个计划的例程，无论您是否在线（最小间隔 1 小时）都会运行，并将工作作为拉取请求返回。

这两者以及安全旋钮都在 **[参考资料/autonomous.md](references/autonomous.md)** 中。

## 核心命令

```bash
loop-factory scan                              # 列出收件箱 + 活动规格
loop-factory dispatch --agent <claude|codex> --stage   # 提示 + 移动到活动中
loop-factory review <spec-id> --agent <claude|codex>   # 生成审阅提示
loop-factory archive <spec-id> --accepted      # 归档通过的规格
loop-factory backprop --agent <claude|codex>   # 与代码同步文档/规格
loop-factory doctor                            # 设置健康检查
```

任何地方都可以将 `--agent claude` 交换为 `--agent codex`——循环是相同的。默认行为是写入提示文件；仅在本地 `codex`/`claude` CLI 安装且用户要求实时执行时才添加 `--execute`。完整的标志参考：**[参考资料/commands.md](references/commands.md)**。

## 编写规格

规格是带有前置部分（`id`，`title`，`agent`，`risk`，`verification`）和涵盖上下文、验收标准、约束和审阅笔记的 markdown。验收标准是合同——它们是代理构建的目标，也是审阅者检查的依据，因此使它们具体且可测试。格式、示例和审阅门问题：**[参考资料/spec-authoring.md](references/spec-authoring.md)**。

## 边界

- 只有人类或显式 CLI 命令才能将规格从 `inbox` 移动到 `active`。
- 只有接受的审阅才能将规格从 `active` 移动到 `archive`。
- 失败的审阅将规格留在 `active`——它不会被删除或无声地重新派发。
- 反向传播可以更新规格/文档，但绝不能自行改变产品意图。
- `factory/prompts/`，`factory/runs/` 和 `factory/reviews/` 下生成的文件是工件和审计追踪——阅读它们，不要将它们视为真相来源。规格才是真相来源。

## 与子代理合作

当隔离有助于时，将阶段交给专门的子代理，而不是在一个上下文中做所有事情：

- 一个 **规格实现者** 来编写一个活动规格的代码，
- 一个 **规格审阅者**（上下文隔离）来评判差异，
- 一个 **规格反向传播者** 来将经验反馈到规格/文档中。

当工作按顺序执行，触摸同一文件或高风险时使用一个代理。仅在规格独立或审阅应保持上下文隔离时才扩展到多个。
