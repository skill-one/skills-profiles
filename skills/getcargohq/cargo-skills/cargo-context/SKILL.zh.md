---
name: cargo-context
description: 读取和写入工作区 GTM 知识库——即以 Git 支持的 Markdown 存储库，描述 ICP、用户画像、策略、证明点、异议、竞争对手和信号——及其运行时沙盒和类型化知识图谱。触发器："记录我们的 ICP"、"撰写这个用户画像"、"我们的定位是什么"、"添加一张战斗卡"、"捕捉这个异议"、"关于 <细分市场> 我们知道什么"、"更新我们的背景"、"背景库中有什么"、"我们向谁销售"。跳过情况：通过分析赢得/失去数据来发现实际购买者——即 cargo-gtm（这项技能记录结论，但不推导结论）；存储结构化记录而非散文——使用 cargo-storage；将文档附加到代理以用于 RAG——使用 cargo-content。
---

# Cargo CLI — 上下文

**上下文** 是一个基于 git 的存储库，包含有类型的 markdown/MDX 文件，它捕获了工作区 GTM 知识（公司叙事、ICP、人物、策略、证据、异议等），并由人类和代理共同读取/写入。`cargo-ai context` 域有两个子域供你使用：

- **runtime** — 浏览、读取、写入、编辑和执行工作区的运行时沙盒（上下文存储库的检出副本）。`write`/`edit` 会推送到默认分支；`execute` 运行**不会**被推送到。
- **graph** — 构建/加载从上下文存储库中每个 markdown/MDX 文件派生的知识图谱。

> 上下文存储库的规范示例是 [`getcargohq/cargo-workspaces`](https://github.com/getcargohq/cargo-workspaces)。在编写新条目之前，请先阅读其 `README.md` 以了解域布局和文件约定。
> 对于上传与运行时无关的文件（CSV、PDF）用于批量运行，请使用 [`cargo-workspace-management`](../cargo-workspace-management/SKILL.md) (`cargo-ai workspaceManagement file upload`)。
> 对于 RAG 文件附件到代理，请使用 [`cargo-ai`](../cargo-ai/SKILL.md) (`cargo-ai content file upload`)。

> 参考 `references/conventions.md` 了解完整的上下文存储库结构和每个域的模板。
> 参考 `references/response-shapes.md` 了解每个 `cargo-ai context` 命令返回的 JSON 结构。
> 参考 `references/troubleshooting.md` 了解常见错误及其解决方法。
> 参考 `references/examples/authoring.md` 了解端到端的添加/编辑/删除配方。
> 参考 `references/examples/lifecycle.md` 了解引导 + 从调用中刷新的剧本。
> 参考 `references/examples/graph-queries.md` 了解检查知识图谱。

## 引导

如果已经登录（`cargo-ai whoami` 返回工作区）？跳到下一节。

```bash
npm install -g @cargo-ai/cli            # 没有全局安装？为每个命令前缀 `npx @cargo-ai/cli`
cargo-ai login --email you@company.com  # 通过邮件验证，无需浏览器；首次使用时创建账户
                                        # 替代方案：--oauth（浏览器） · --token <api-token>（CI）
cargo-ai whoami                         # 在任何写入之前确认活动工作区
```

每个命令都会将 JSON 打印到标准输出；失败时以非零状态退出并打印 `{"errorMessage": "..."}`。任何创建运行或批量的操作都是异步的 — 传递 `--wait-until-finished` 或轮询匹配的 `get`。`runtime write` 和 `runtime edit` 提交并推送到工作区的上下文存储库，因此首先确认 `workspace.name` 是非协商的。当完整技能包安装完成后，[`../cargo/references/prerequisites.md`](../cargo/references/prerequisites.md) 会添加 CLI 版本固定、令牌作用域和仅管理员界面。

## 首先发现上下文

在编辑任何内容之前，查看上下文存储库中有什么内容：

```bash
cargo-ai context runtime browse                 # 列出运行时沙盒根目录下的条目
cargo-ai context graph get                      # 从存储库的 md/mdx 文件派生的完整知识图谱
```

## 快速参考

```bash
# 运行时沙盒（存储库的检出副本）
cargo-ai context runtime browse [--path <path>]
cargo-ai context runtime read --path <path> [--start-line <n>] [--end-line <n>]
cargo-ai context runtime write --path <path> --content <content> [--commit-message <message>]
cargo-ai context runtime edit --path <path> --old-string <old> --new-string <new> [--commit-message <message>]
cargo-ai context runtime execute --command <command> [--args <json>]

# 知识图谱
cargo-ai context graph get
```

## 运行时沙盒

**运行时沙盒** 是上下文存储库的可执行检出副本。它是你读取和修改上下文文件以及对其运行命令的界面。

需要记住的两个重要行为：

- **`write` 和 `edit` 推送到上下文存储库的默认分支**。它们不是仅本地。
- **`execute` 不会推送到**。通过 `execute` 运行的 shell 命令对文件所做的更改保留在沙盒中并会被丢弃 — 使用 `execute` 进行构建、测试或检查，而不是提交编辑。

**上传的内容文件以只读方式位于 `.files/` 下**。工作区的 `content file` 上传（PDF、CSV、文本 — 参考 [`cargo-content`](../cargo-content/SKILL.md)）会出现在沙盒的 `.files/` 目录下，因此通过 `execute`（或 `read`/`browse`）运行的命令可以消费它们 — 例如 `cargo-ai context runtime execute --command ls --args '["-1",".files"]'`。它位于**提交的上下文树之外**：沙盒的自动提交会跳过它，因此 `.files/` 下没有任何内容会被推送到上下文存储库，并且你无法从这里添加或更改内容文件（请使用 `cargo-ai content file …` 代替）。

由于写入会立即推送，**在第一次 `write`/`edit` 之前确认目标工作区**：

```bash
cargo-ai whoami   # → workspace.uuid, workspace.name
```

将工作区名称反馈给用户。如果会话是针对特定客户的，请确保 `workspace.name` 匹配后再进行任何创作 — 没有干运行模式。如果 `workspace.name` 是通用的或模糊的（例如 "Main"、"Test"、一个人的名字、内部代号），不要猜测 — 请求用户的公司名称和规范域名（`example.com`），并在第一次写入前确认两者。如果你没有固定工作区就登录，请重新运行 `cargo-ai login --oauth --workspace-uuid <uuid>`（或 `--token <workspace-scoped-token>` 用于非交互式使用）。

从销售呼叫分析派生的编辑应**逐个进行人工审查**，而不是批量处理。让代理循环处理许多呼叫往往会过度加权最响亮的信号并错过细微差别 — 参考 `references/examples/lifecycle.md` 中的呼叫刷新剧本。

### 浏览和读取

```bash
# 列出运行时沙盒根目录下的条目
cargo-ai context runtime browse

# 列出子路径下的条目（例如像 persona/ 或 play/ 这样的域文件夹）
cargo-ai context runtime browse --path persona

# 读取完整文件
cargo-ai context runtime read --path persona/vp-sales-mid-market.md

# 只读取行范围（1 索引，两端都包含）
cargo-ai context runtime read --path play/inbound-trial-to-paid.md --start-line 1 --end-line 40
```

### 写入新文件

`write` 创建（或覆盖）文件并将提交推送到默认分支。

每个 `.md`/`.mdx` 文件应以设置 `title` 和 `description` 的 YAML 前置块开头。前置块**不会**被验证 — 缺少、为空或格式不正确的前置块的文件仍然会被写入和提交；它只是索引不佳（缺少 `title` 会回退到文件名，节点摘要会回退到第一段）。`write` 可能因其他原因失败 — `repositoryNotFound`、`syncConflict`、`syncFailed`、`failedToWrite` 或 `deniedPath`（例如在 `.files/` 下写入）；参考 `references/response-shapes.md`。

```bash
cargo-ai context runtime write \
  --path persona/vp-sales-mid-market.md \
  --content "$(cat <<'EOF'
---
title: 销售副总裁，中市场
description: 负责拥有 200-2000 人的公司的管道、配额和代表生产力。
---

## 角色
- 标题：销售副总裁
- 资历：高管
- 职能：收入
- 向谁汇报：CRO 或 CEO

## KPI
- 新 ARR、获胜率、管道覆盖率、代表加速时间

## 痛点
- 管道差距、加速慢、代表活动低、预测偏差

## 动机
- 达到目标、建立可重复的动作、获得可见性

## 日常工作
预测呼叫、交易审查、管道审查、与一线经理的一对一。

## 偏好的渠道
- medium/linkedin-outbound
- medium/exec-warm-intro

## 常见异议
- objection/we-already-have-an-ai-sdr

## 我们如何落地
以管道覆盖率数学为切入点，而不是以功能为切入点。
EOF
)" \
  --commit-message "添加销售副总裁中市场人物"
```

### 编辑现有文件

`edit` 替换单个精确子字符串。`--old-string` 必须在文件中**出现一次**；传递空的 `--new-string` 以删除匹配项。

`edit` 不会验证前置块 — 删除或清空 `title`/`description` 的编辑仍然适用，因此请保持块完整以保持节点可发现。`edit` 可能因其他原因失败：`stringNotFound` / `stringNotUnique`（`--old-string` 匹配）、`fileNotFound`、`noOp`（新字符串等于旧）、`syncConflict` / `syncFailed`、`failedToEdit` 或 `deniedPath`。

```bash
# 替换一个特定句子
cargo-ai context runtime edit \
  --path global/positioning.md \
  --old-string "We help RevOps automate workflows." \
  --new-string "We help RevOps run AI-native GTM motions." \
  --commit-message "刷新定位一句话"

# 删除一行（传递空的 --new-string）
cargo-ai context runtime edit \
  --path persona/vp-sales-mid-market.md \
  --old-string "\n- 过时的统计数据：4.2x 管道\n" \
  --new-string ""
```

对于较大的重构，请优先选择 `write`（完整文件覆盖）而不是多个连续的 `edit` 调用。

### 在沙盒中执行命令

`execute` 在沙盒中运行 shell 命令。用于检查结构或运行检查；**更改不会被推送**。

```bash
# 查找每个交叉引用特定 slugs 的文件
cargo-ai context runtime execute \
  --command grep \
  --args '["-r","-l","persona/vp-sales-mid-market","."]'

# 计算每个域的条目数
cargo-ai context runtime execute --command ls --args '["-1","persona"]'

# 运行一次性脚本（命令内部不需要引号/转义）
cargo-ai context runtime execute --command pwd
```

`--args` 是一个 JSON 数组字符串参数。省略它用于无参数命令。

## 上下文存储库结构和约定

Cargo 上下文存储库是一个有类型的知识库。规范示例（也是以下约定的来源）是 [`getcargohq/cargo-workspaces`](https://github.com/getcargohq/cargo-workspaces)；在编写新条目之前，请阅读其 `README.md` 和每个域中的 `_template.md` 文件。有关完整域参考，请参阅 `references/conventions.md`。

### 域

| 域 | 目的 |
|---|---|
| `global/` | 公司级上下文：使命、声音、定位、叙事、定价 |
| `icp/` | 理想客户画像段 |
| `persona/` | 买家画像（ICP 内部的角色） |
| `jtbd/` | 工作待完成框架 |
| `alternative/` | 竞争对手、替代品、现状 |
| `client/` | 客户画像、案例研究、参考账户 |
| `insight/` | 市场洞察和观察 |
| `medium/` | 渠道剧本（电子邮件、LinkedIn、冷呼叫等） |
| `objection/` | 异议 + 响应 + 证据 |
| `play/` | GTM 策略（信号 → 受众 → 渠道 → 序列 → 结果） |
| `proof/` | 原子证据点（指标、引言、案例数据） |
| `signal/` | 购买信号和意图触发器 |

### 文件约定

- **文件名**：`kebab-case.md`（例如 `vp-sales-mid-market.md`）。
- **前置块**：为每个 `.md`/`.mdx` 文件以 YAML 前置块开头，设置 `title` 和 `description`。这是一个**强约定，未强制执行** — 缺少、为空或格式不正确的前置块的写入仍然会被创建和提交；它只是索引不佳。图读取 `title`（回退：文件名）和 `summary`（回退：文件的第一段）；它**不会**读取 `description`，因此如果你想控制节点摘要，请添加 `summary:`。参考 [源参考和图边](#source-references-and-graph-edges)。
- **交叉引用**：使用 `domain/slug` 形式，**没有 `.md` 扩展名**（例如 `persona/vp-sales-mid-market`）。要注册为图**边**，引用必须使用以下三种链接形式之一 — 在普通文本中出现的裸 `domain/slug`（或文件路径）不会创建边。
- **模板**：每个域都附带一个 `_template.md`。在创作新条目之前阅读它 (`cargo-ai context runtime read --path persona/_template.md`)。`_template.*` 文件会被排除在图之外 — 永远不要引用它们。

### 源参考和图边

知识图谱是从存储库中每个 `.md`、`.mdx`、`.yaml` 和 `.yml` 文件（任何文件夹；只有 `.git/` 被排除）构建的。每个文件都是一个节点，但**边只从三种形式创建** — 任何其他内容对图都是不可见的：

1. **前置块 `references:` 列表**（用于源引用的首选形式 — 保持文本干净）：
   ```yaml
   ---
   title: AgoraPulse 扩张理论
   description: 为什么 AgoraPulse 准备好进行多线程扩张策略。
   references:
     - outputs/sales-notes/2026-06-05-agorapulse-build-session-1-outcomes.md
   ---
   ```
2. **正文中的一个 Markdown 链接** — 标准的 `[标签]` 后面立即跟着 `(路径)` 语法，其中目标是文件路径，例如锚点链接到 `outputs/sales-notes/2026-06-05-agorapulse-build-session-1-outcomes.md`。
3. **正文中的 Wikilinks**（扩展可选）：`[[outputs/sales-notes/2026-06-05-agorapulse-build-session-1-outcomes]]`。

主要约束：

- **永远不要在文本中引用源作为裸路径**（例如一个 `Source:` 行只是将 `outputs/sales-notes/foo.md` 作为文本提及） — 它不会被解析，并且不会创建**边**。
- **优先使用根相对路径**（首先从存储库根解析，然后相对于引用文件解析），以便无论文档位于何处，链接都能工作。
- **扩展是可选的** — 解析器按顺序自动尝试 `.md`、`.mdx`、`.yaml`、`.yml`。包含扩展是没问题的。
- **目标必须存在**，否则边**会断裂**（图 UI 中的死链接）。在引用前用 `runtime browse` 验证。
- 对于具有 **源**/**证据** 部分的文档，请在前置块 `references:` 中引用文件；当引用需要在周围文本中时，使用内联 Markdown 链接。完整规则：`references/conventions.md`。

### 工作流：添加新条目

1. 确认目标域并复制其模板：
   ```bash
   cargo-ai context runtime read --path persona/_template.md
   ```
2. 在 `<domain>/<slug>.md` 处使用 `write` 创建一个新文件，填写 `title` + `description` 和正文部分。
3. 添加交叉引用（`domain/slug`）以供使用 — 当双向有意义时，请保持它们双向。
4. 重建知识图谱以验证新条目及其链接：
   ```bash
   cargo-ai context graph get
   ```

有关完整的每个域模板和工作示例，请参阅 `references/conventions.md` 和 `references/examples/authoring.md`。

### 工作流：引导和刷新

要从头开始在新工作区设置上下文存储库，或定期刷新现有存储库，请遵循 `references/examples/lifecycle.md` 中的两阶段生命周期：

1. **引导（一次性）**：从公共源填充 `global/`、`persona/`、`client/`、`proof/`、`objection/`、`signal/`，然后对填充的存储库打开一个新的代理会话。对于规范、可自动化的版本（域入 → 文件出，幂等，具有信用预算），请使用 `references/examples/bootstrap-from-domain.md`。
2. **刷新（每 2-4 周）**：拉取最后 3 个月的销售呼叫记录 → 逐个分析，人工参与 → 在达到重复阈值之前将任何声明添加到上下文 → 通过生成序列排列进行验证 → 在刷新前/后比较图并淘汰过时的条目。

重复阈值（声明必须出现在多少次呼叫中才能进入上下文）在 `references/conventions.md` 中有记录。

## 知识图谱

`context graph get` 构建（或从缓存加载）覆盖上下文存储库中每个 markdown/MDX 文件的知识图谱。用它来：

- 审计域之间的交叉引用（例如，查找链接到没有附加证据的策略的人物）。
- 在编写新条目之前发现已存在的内容（避免重复）。
- 为需要工作区上下文的类型结构的下游代理提供支持。

```bash
cargo-ai context graph get
```

响应包括每个节点的解析前置块和出站 `domain/slug` 引用 — 通过 `jq` 管道它进行切片。参考 `references/examples/graph-queries.md` 了解现成的查询。

## 帮助

每个命令都支持 `--help`：

```bash
cargo-ai 上下文 --help
cargo-ai 上下文 运行时 浏览 --help
cargo-ai 上下文 运行时 读取 --help
cargo-ai 上下文 运行时 写入 --help
cargo-ai 上下文 运行时 编辑 --help
cargo-ai 上下文 运行时 执行 --help
cargo-ai 上下文 图形 获取 --help
```
