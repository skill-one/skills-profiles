# Cargo CLI — 上下文

**上下文**是一个基于git的、包含类型化markdown/MDX文件的仓库，它捕获了工作区中GTM知识（公司叙事、ICP、用户画像、策略、证据、异议等），并由人类和智能体共同读写。`cargo-ai context`域包含两个子域供你使用：

- **runtime** — 浏览、读取、写入、编辑和执行工作区的运行时沙盒（上下文仓库的检出副本）。`write`/`edit`会推送到默认分支；`execute`运行不会推送到仓库。
- **graph** — 构建或加载从上下文仓库中每个markdown/MDX文件衍生出的知识图谱。

> 上下文仓库的规范示例是 [`getcargohq/cargo-workspaces`](https://github.com/getcargohq/cargo-workspaces)。在编写新条目之前，请先阅读其`README.md`以了解域布局和文件约定。
> 用于上传与运行时无关的文件（CSV、PDF）以用于批量运行，请使用[`cargo-workspace-management`](../cargo-workspace-management/SKILL.md) (`cargo-ai workspaceManagement file upload`)。
> 用于智能体的RAG文件附件，请使用[`cargo-ai`](../cargo-ai/SKILL.md) (`cargo-ai content file upload`)。

> 参考`references/conventions.md`了解完整的上下文仓库结构和每个域的模板。
> 参考`references/response-shapes.md`了解每个`cargo-ai context`命令返回的JSON形状。
> 参考`references/troubleshooting.md`了解常见错误及其解决方法。
> 参考`references/examples/authoring.md`了解端到端的添加/编辑/删除配方。
> 参考`references/examples/lifecycle.md`了解引导和从调用中刷新的剧本。
> 参考`references/examples/graph-queries.md`了解检查知识图谱。

## 引导

如果已经登录（`cargo-ai whoami`返回工作区）？跳到下一节。

```bash
npm install -g @cargo-ai/cli            # 没有全局安装？为每个命令前缀`npx @cargo-ai/cli`
cargo-ai login --email you@company.com  # 通过邮件验证，无需浏览器；首次使用时创建账户
                                        # 替代方案：--oauth（浏览器）· --token <api-token>（CI）
cargo-ai whoami                         # 在任何写入操作前确认活动工作区
```

每个命令都会将JSON打印到标准输出；失败时以非零状态退出，并返回`{"errorMessage": "..."}`。任何创建运行或批量的操作都是异步的——传递`--wait-until-finished`或轮询匹配的`get`。`runtime write`和`runtime edit`会提交并推送到工作区的上下文仓库，因此首次确认`workspace.name`是必不可少的。当完整技能包安装完成后，`[`../cargo/references/prerequisites.md`](../cargo/references/prerequisites.md)`会添加CLI版本固定、令牌范围和管理员专用的界面。

## 首先探索上下文

在编辑任何内容之前，查看上下文仓库中包含的内容：

```bash
cargo-ai context runtime browse                 # 列出运行时沙盒根目录下的条目
cargo-ai context graph get                      # 从仓库的md/mdx文件中派生的完整知识图谱
```

## 快速参考

```bash
# 运行时沙盒（上下文仓库的检出副本）
cargo-ai context runtime browse [--path <path>]
cargo-ai context runtime read --path <path> [--start-line <n>] [--end-line <n>]
cargo-ai context runtime write --path <path> --content <content> [--commit-message <message>]
cargo-ai context runtime edit --path <path> --old-string <old> --new-string <new> [--commit-message <message>]
cargo-ai context runtime execute --command <command> [--args <json>]

# 知识图谱
cargo-ai context graph get
```

## 运行时沙盒

**运行时沙盒**是上下文仓库的可执行检出副本。它是你用于读取和修改上下文文件以及对其运行命令的界面。

需要记住的两个重要行为：

- **`write`和`edit`推送到上下文仓库的默认分支**。它们不是仅本地操作。
- **`execute`不会推送到仓库**。通过`execute`运行的shell命令对文件所做的更改将保留在沙盒中并会被丢弃——使用`execute`进行构建、测试或检查，而不是提交编辑。

**上传的内容文件以只读方式存储在`.files/`下**。工作区的`content file`上传（PDF、CSV、文本——参见[`cargo-content`](../cargo-content/SKILL.md)）会出现在沙盒的`.files/`目录下，因此通过`execute`（或`read`/`browse`）运行的命令可以消费它们——例如`cargo-ai context runtime execute --command ls --args '["-1",".files"]'`。它位于**提交的上下文树之外**：沙盒的自动提交会跳过它，因此`.files/`下的任何内容都不会推送到上下文仓库，并且你无法从这里添加或更改内容文件（请使用`cargo-ai content file …`）。

由于写入操作会立即推送，**在首次`write`/`edit`之前确认目标工作区**：

```bash
cargo-ai whoami   # → workspace.uuid, workspace.name
```

将工作区名称反馈给用户。如果会话是针对特定客户的，请确保`workspace.name`匹配后再进行任何创作——没有干运行模式。如果`workspace.name`是通用的或模糊的（例如"Main"、"Test"、某个人名、内部代号），不要猜测——请要求用户提供公司名称和规范域名（`example.com`），并在首次写入前确认两者。如果你未固定工作区登录，请重新运行`cargo-ai login --oauth --workspace-uuid <uuid>`（或`--token <workspace-scoped-token>`用于非交互式使用）。

从销售呼叫分析派生的编辑应**逐个进行人工审核**，而不是批量处理。让智能体循环处理多个呼叫往往会过度加权最响亮的信号并忽略细微差别——请参考`references/examples/lifecycle.md`中的呼叫刷新剧本。

### 浏览和读取

```bash
# 列出运行时沙盒根目录下的条目
cargo-ai context runtime browse

# 列出子路径下的条目（例如像domain文件夹一样的`persona/`或`play/`）
cargo-ai context runtime browse --path persona

# 读取完整文件
cargo-ai context runtime read --path persona/vp-sales-mid-market.md

# 只读取行范围（1索引，两端都包含）
cargo-ai context runtime read --path play/inbound-trial-to-paid.md --start-line 1 --end-line 40
```

### 写入新文件

`write`会创建（或覆盖）文件并将提交推送到默认分支。

每个`.md`/`.mdx`文件应以设置`title`和`description`的YAML前matter块开头。前matter**不会进行验证**——一个缺少、为空或格式不正确的前matter的文件仍然会被写入和提交；它只是索引效果不佳（缺少`title`会回退到文件名，节点摘要会回退到第一段）。`write`仍可能因其他原因失败——`repositoryNotFound`、`syncConflict`、`syncFailed`、`failedToWrite`或`deniedPath`（例如在`.files/`下写入）；参见`references/response-shapes.md`。

```bash
cargo-ai context runtime write \
  --path persona/vp-sales-mid-market.md \
  --content "$(cat <<'EOF'
---
title: 销售副总裁，中市场
description: 负责拥有200-2000人公司的管道、配额和代表生产力。
---

## 角色
- 标题：销售副总裁
- 资历：高管
- 职能：收入
- 向谁汇报：CRO或CEO

## KPI
- 新ARR、获胜率、管道覆盖率、代表加速时间

## 痛点
- 管道差距、加速慢、代表活动低、预测偏差

## 动机
- 达到目标、建立可重复的动作、获得可见性

## 日常工作
预测呼叫、交易审查、管道审查、与一线经理的一对一交流。

## 优先渠道
- medium/linkedin-outbound
- medium/exec-warm-intro

## 常见异议
- objection/we-already-have-an-ai-sdr

## 我们如何落地
以管道覆盖率数学为切入点，而不是以功能为切入点。
EOF
)" \
  --commit-message "添加销售副总裁中市场用户画像"
```

### 编辑现有文件

`edit`会替换单个精确子字符串。`--old-string`必须在文件中**出现一次**；传递空的`--new-string`以删除匹配项。

`edit`不会验证前matter——一个移除或清空`title`/`description`的编辑仍然有效，因此请保持该块以保持节点可发现。`edit`可能因其他原因失败：`stringNotFound` / `stringNotUnique`（`--old-string`匹配）、`fileNotFound`、`noOp`（新字符串等于旧）、`syncConflict` / `syncFailed`、`failedToEdit`或`deniedPath`。

```bash
# 替换一个特定句子
cargo-ai context runtime edit \
  --path global/positioning.md \
  --old-string "We help RevOps automate workflows." \
  --new-string "We help RevOps run AI-native GTM motions." \
  --commit-message "刷新定位一句话"

# 删除一行（传递空的--new-string）
cargo-ai context runtime edit \
  --path persona/vp-sales-mid-market.md \
  --old-string "\n- 过时的数据：4.2x管道\n" \
  --new-string ""
```

对于较大的重构，请优先选择`write`（完整文件覆盖）而不是多个连续的`edit`调用。

### 在沙盒中执行命令

`execute`会在沙盒中运行一个shell命令。用于检查结构或运行检查；**更改不会被推送到仓库**。

```bash
# 查找所有交叉引用特定slug的文件
cargo-ai context runtime execute \
  --command grep \
  --args '["-r","-l","persona/vp-sales-mid-market","."]'

# 统计每个域的条目数量
cargo-ai context runtime execute --command ls --args '["-1","persona"]'

# 运行一次性脚本（在--command内部不需要引号/转义）
cargo-ai context runtime execute --command pwd
```

`--args`是一个JSON数组字符串参数。省略它用于无参数命令。

## 上下文仓库结构和约定

Cargo上下文仓库是一个类型化知识库。规范示例——以及以下约定的来源——是[`getcargohq/cargo-workspaces`](https://github.com/getcargohq/cargo-workspaces)；在编写新条目之前，请阅读其`README.md`和每个域中的`_template.md`文件。有关完整域参考，请参阅`references/conventions.md`。

### 域

| 域       | 目的         |
|----------|--------------|
| `global/` | 公司级上下文：使命、声音、定位、叙事、定价 |
| `icp/`   | 理想客户画像段 |
| `persona/` | 买家画像（ICP内的角色） |
| `jtbd/`  | 工作待完成框架 |
| `alternative/` | 竞争对手、替代品、现状 |
| `client/` | 客户画像、案例研究、参考账户 |
| `insight/` | 市场洞察和观察 |
| `medium/` | 渠道剧本（电子邮件、LinkedIn、冷呼叫等） |
| `objection/` | 异议+回应+证据 |
| `play/`  | GTM策略（信号→受众→渠道→序列→结果） |
| `proof/`  | 原子证据点（指标、引言、案例数据） |
| `signal/` | 购买信号和意图触发器 |

### 文件约定

- **文件名**：`kebab-case.md`（例如`vp-sales-mid-market.md`）。
- **前matter**：每个`.md`/`.mdx`文件应以设置`title`和`description`的YAML前matter块开头。这是一个**强约定，未强制执行**——带有缺失、为空或格式不正确的frontmatter的写入仍然会被创建和提交；它只是索引效果不佳。图谱读取`title`（回退：文件名）和`summary`（回退：文件的第一段）；它**不会**读取`description`，因此如果你想控制节点摘要，请添加`summary:`。参见[源参考和图谱边](#source-references-and-graph-edges)。
- **交叉引用**：使用`domain/slug`形式，**不带`.md`扩展名**（例如`persona/vp-sales-mid-market`）。要注册为图谱**边**，引用必须使用以下三种链接形式之一——在普通文本中出现的裸`domain/slug`（或文件路径）不会创建边。
- **模板**：每个域都附带一个`_template.md`。在创作新条目之前阅读它（`cargo-ai context runtime read --path persona/_template.md`）。`_template.*`文件不会包含在图谱中——永远不要引用它们。

### 源参考和图谱边

知识图谱是从仓库中每个`.md`、`.mdx`、`.yaml`和`.yml`文件构建的（任何文件夹；仅排除`.git/`）。每个文件都是一个节点，但**只有三种形式会创建边**——其他任何内容对图谱都是不可见的：

1. **前matter `references:` 列表**（用于源引用的首选形式——保持文本清洁）：
   ```yaml
   ---
   title: AgoraPulse扩张理论
   description: 为什么AgoraPulse准备好进行多线程扩张策略。
   references:
     - outputs/sales-notes/2026-06-05-agorapulse-build-session-1-outcomes.md
   ---
   ```
2. **正文中的Markdown链接**——标准的`[标签]`后立即跟随`(路径)`语法，其中目标是文件路径，例如锚点链接到`outputs/sales-notes/2026-06-05-agorapulse-build-session-1-outcomes.md`。
3. **正文中的Wikilinks**（扩展名可选）：`[[outputs/sales-notes/2026-06-05-agorapulse-build-session-1-outcomes]]`。

关键约束：

- **永远不要在文本中引用源作为裸路径**（例如一个`Source:`行仅提及`outputs/sales-notes/foo.md`作为文本）——它不会被解析，并且不会创建边。
- **优先使用根相对路径**（首先从仓库根解析，然后相对于引用文件解析），以便无论文档位于何处，链接都能正常工作。
- **扩展名是可选的**——解析器会按顺序自动尝试`.md`、`.mdx`、`.yaml`、`.yml`。包含扩展名是没问题的。
- **目标必须存在**，否则边会**断裂**（图谱UI中的死链接）。在引用前使用`runtime browse`进行验证。
- 对于具有**源**/**证据**部分的文档，请在frontmatter `references:`中引用文件；当引用需要在周围文本中时，使用内联Markdown链接。完整规则：`references/conventions.md`。

### 工作流：添加新条目

1. 确认目标域并复制其模板：
   ```bash
   cargo-ai context runtime read --path persona/_template.md
   ```
2. 在`<domain>/<slug>.md`处`write`一个新文件，填写`title` + `description`和正文部分。
3. 在有用处的地方添加交叉引用（`domain/slug`），当有道理时保持它们双向。
4. 重建知识图谱以验证新条目及其链接：
   ```bash
   cargo-ai context graph get
   ```

有关完整的每个域模板和工作示例，请参阅`references/conventions.md`和`references/examples/authoring.md`。

### 工作流：引导和刷新

要从零创建新工作区的上下文仓库，或定期刷新现有仓库，请遵循`references/examples/lifecycle.md`中的两阶段生命周期：

1. **引导（一次性）**：从公共源填充`global/`、`persona/`、`client/`、`proof/`、`objection/`、`signal/`，然后对填充的仓库打开一个新的智能体会话。对于规范、可自动化的版本（域入→文件出，幂等，带有信用预算），请使用`references/examples/bootstrap-from-domain.md`。
2. **刷新（每2-4周）**：拉取最后3个月的销售呼叫转录稿→逐个分析，人工参与→在达到重复阈值之前将任何声明添加到上下文中→通过生成序列排列进行验证→在刷新前/后比较图谱并淘汰过时的条目。

重复阈值（声明必须出现在多少次呼叫中才能进入上下文）在`references/conventions.md`中有记录。

## 知识图谱

`context graph get`会构建（或从缓存加载）覆盖上下文仓库中每个markdown/MDX文件的知识图谱。使用它来：

- 审计域之间的交叉引用（例如，查找链接到没有附加证据的策略的用户画像）。
- 在编写新条目之前发现已有内容（避免重复）。
- 为需要工作区上下文类型化结构的下游智能体提供支持。

```bash
cargo-ai context graph get
```

响应包括每个节点的解析前matter和出站`domain/slug`引用——通过`jq`管道处理它。参见`references/examples/graph-queries.md`了解现成的查询。

## 帮助

每个命令都支持`--help`：

```bash
cargo-ai context --help
cargo-ai context runtime browse --help
cargo-ai context runtime read --help
cargo-ai context runtime write --help
cargo-ai context runtime edit --help
cargo-ai context runtime execute --help
cargo-ai context graph get --help
```
