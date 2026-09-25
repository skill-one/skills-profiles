# 代理开发工作流与指南

**agents-cli** 是一个用于在 Google Cloud 上构建、评估和部署代理的命令行工具和技能工具包。它适用于任何编码代理——Antigravity CLI、Claude Code、Codex 或其他——以及您选择的代理框架（默认为 [代理开发工具包 (ADK)](https://adk.dev/)）。使用 `uvx google-agents-cli setup` 安装。

> **在编写代理代码之前，请确保存在一个脚手架项目（见第 2 步）。** 跳过脚手架会丢失评估样板、CI/CD 配置和项目约定。

> 需要：google-agents-cli ~= 1.7.0
> 如果版本落后，请运行：uv tool install "google-agents-cli~=1.7.0"

> 检查版本：agents-cli info
> 如果需要，请先安装 [uv](https://docs.astral.sh/uv/getting-started/installation/index.md)。

## 会话连续性与技能交叉引用

在每个阶段之前重新阅读相关技能——而不是在你已经开始并遇到问题之后。上下文压缩可能会丢弃早期的技能内容。如果技能不可用，请运行 `uvx google-agents-cli setup` 来安装它们。

| 阶段 | 技能 | 加载时间 |
|------|-------|--------------|
| 0 — 理解 | — | 无需技能——如果存在，请阅读 `.agents-cli-spec.md`，否则请与用户澄清目标 |
| 1 — 学习配方 | `/google-agents-cli-adk-code` | 在设计期间加载它，在脚手架之前。Python：`references/samples.md` 主题索引将需求映射到实现它的配方。Go：上游 [示例/](https://github.com/google/adk-go/tree/main/examples) 是等效的。是的，要尽早加载这个。 |
| 2 — 脚手架 | `/google-agents-cli-scaffold` | 在创建或增强项目之前 |
| 3 — 构建 | `/google-agents-cli-adk-code` | 在编写代理代码之前——API 模式、工具、回调、状态 |
| 4 — 评估 | `/google-agents-cli-eval` | 在运行任何评估之前——数据集模式、指标、评估-修复循环 |
| 5 — 部署 | `/google-agents-cli-deploy` | 在部署之前——目标选择、故障排除 403/超时 |
| 6 — 发布 | `/google-agents-cli-publish` | 部署后，如果注册到 Gemini Enterprise（可选） |
| 7 — 观察 | `/google-agents-cli-observability` | 部署后——跟踪、日志记录、监控设置 |

---

## 设置

如果未安装 `agents-cli`：
```bash
uv tool install google-agents-cli
```

### `uv` 命令未找到

按照 [官方安装指南](https://docs.astral.sh/uv/getting-started/installation/index.md) 安装 `uv`。

### 产品名称映射

用户不一致地命名产品（Vertex AI → Agent Platform、Agent Engine → Agent Runtime 等）。使用 `references/terminology.md` 将用户术语映射到 CLI 值。

---

## 第 0 步：理解

在编写或脚手架任何东西之前，了解你要构建什么——通过 **设计对话**，而不是清单。加载 `references/brainstorming.md` 并遵循它：一次问 **一个问题**，为非平凡代理提出 2-3 种架构方法，并在任何脚手架之前验证设计。

如果在当前目录中存在 `.agents-cli-spec.md`，请阅读它——它是你的主要事实来源。否则：

在用户批准规范之前，不要继续进行计划、脚手架或编码。不要假设、研究或自己填写空白——用户的意图驱动一切。

**根据复杂性调整仪式：** 一个简单的代理（单个工具、固定角色）只需要几个问题、一个 2-3 句的规范和一个批准；一个复杂的代理（多代理、RAG、外部 API/认证、安全关键）在 `references/brainstorming.md` 中获得全面处理。

**要涵盖的主题**（一次一个问题，根据用户进行调整——见剧本）：

1. **代理将解决什么问题？** — 核心目的和能力
2. **需要外部 API 或数据源吗？** — 工具、集成、认证要求
3. **安全约束吗？** — 代理必须不做什么，护栏
4. **部署偏好？** — 首先进行原型（推荐）还是完整部署？如果部署：Agent Runtime、Cloud Run 或 GKE？

**根据上下文提问：**

- 如果代理需要一个 **脚手架没有提供的功能**——检索您的数据、沙盒代码执行、跨会话的内存、OAuth 同意、安全护栏、事件驱动触发器——这个功能来自一个 **克隆并学习配方**，而不是脚手架标志。在 `/google-agents-cli-adk-code` → `references/samples.md` 中的主题索引中查找需求，并学习第 1 步中匹配的配方。
- 如果代理是 **实时或语音代理**（Live API、语音对话、打断、电话）→ 在编写规范之前加载 `/google-agents-cli-adk-code` (`references/adk-python-live.md`)。实时规则排除了 A2A、Gemini Enterprise 和默认模型。
- 如果代理应该 **对其他代理可用** → **A2A 协议** 内置于由 agents-cli 脚手架的每个 Python 代理中；无需单独选择——正常脚手架即可。
- 如果选择 **完整部署** → **CI/CD 运行器？** GitHub Actions（默认）或 Google Cloud Build？
- 如果代理应该 **跨会话记住用户偏好或事实** → 长期记忆跨对话。加载 `/google-agents-cli-adk-code`——它包含配方（在 `references/samples.md`）和 ADK 内存 API 详细信息。
- 如果选择 **Cloud Run** 或 **GKE** → **会话存储？** 内存（默认）、Cloud SQL（持久）或 Agent Platform Sessions（托管）。
- 如果选择 **带有 CI/CD 的部署** → **Git 仓库？** 已经存在一个吗，或者应该创建一个？如果创建，公共的还是私有的？

一旦设计达成一致，使用 `references/spec-template.md` 中的模板将规范写入 `.agents-cli-spec.md`，进行自我审查，然后获得用户的批准。有关这些选择如何映射到 CLI 标志，请参阅 `/google-agents-cli-scaffold`。

一旦有了清晰的理解，请继续进行 **第 1 步**。

## 第 1 步：学习参考配方

> **触发器。** 如果请求涉及任何：搜索您自己的文档 · 在用户代表下运行 shell 或 Python 代码 · 一个沙盒或隔离的每个用户环境 · 代理在运行时加载的技能 · 跨越数天、恢复或运行未受管理的任务 · 跨对话记忆 · 在执行之前批准有风险的操作 · 阻止有害内容或 moderating 代理说什么 · 使用用户自己的 API 密钥或凭证 · OAuth 同意在达到用户自己的数据 · 将任务委托给具有隔离上下文的子代理 · 对其他代理进行 A2A 交流 · 对事件或时间表做出反应 · 在网上研究主题并附带引用报告 · 生成图像或视频——那么已经有配方实现了它。在您承诺实现之前查找它。
>
> 此列表涵盖了与 `/google-agents-cli-adk-code` → `references/samples.md` 中的主题索引相同的特性。如果您扩展了其中一个，请扩展另一个。

**现在加载 `/google-agents-cli-adk-code`。** 即使没有脚手架，您还没有编写代码也要加载它；“代码技能不适合当前阶段”是使代理跳过此步骤的合理化，该技能的“编写代码的先决条件”不适用于您。

查找设计要求每个功能。**ADK Python：** **`references/samples.md` 中的主题索引**将需求（检索、沙盒执行、内存、批准门、护栏、每个用户的凭证、计划）映射到教它们并显示如何克隆的配方。**ADK Go：** 没有参考目录——请阅读 `references/adk-go.md` 获取 API 和上游 [`examples/`](https://github.com/google/adk-go/tree/main/examples)。

可以匹配多个配方——克隆并学习所有相关的配方，从每个配方的 `AGENTS.md` 开始。

如果没有匹配的配方，请继续第 2 步。但首先——您确定吗？重新阅读用户的请求并重新检查您的语言的主题索引。跳过匹配的配方意味着重建已经存在的模式，通常更糟。

> **重要——退出标准：** 在学习配方后，问自己：我可以应用它的任何内容来帮助我交付设计吗？在继续之前记下您将重用的内容。在回答这个问题之前不要继续。

> **此目录在任何阶段都很有用**——当您遇到部署、发布或基础设施问题时，请重新访问它。一个配方的 Terraform 或注册模式可能是您后来需要的东西。

## 第 2 步：脚手架（如果需要）

首先检查项目是否已存在：从项目根目录运行 `agents-cli info`。如果已经创建或由 agents-cli 增强了项目，请跳过此阶段。

否则，在编写任何代码之前进行脚手架：
- **还没有项目** → `agents-cli scaffold create <name>`
- **要导入现有代码** → `agents-cli scaffold enhance .`（添加 agents-cli 结构）

使用 `/google-agents-cli-scaffold` 进行完整工作流——它涵盖了架构选择（部署目标、代理类型、会话存储）和项目创建或增强。

## 第 3 步：构建和实现

实现代理逻辑：

1. 在代理目录中编写/修改代码（检查 `GEMINI.md` / `CLAUDE.md` 获取目录名称）
2. **快速冒烟测试**：使用 `agents-cli run "your prompt"` 来验证更改后的代理是否正常工作——这是最快的方法，无需离开终端即可检查行为
3. 根据用户反馈迭代实现

如果用户要求交互式测试，建议 `agents-cli playground`——它打开一个基于 Web 的游乐场，用于与代理进行手动对话。

对于 ADK API 模式和代码示例，请使用 `/google-agents-cli-adk-code`。

> **此处仅进行冒烟测试——不要编写行为单元测试。** LLM 输出是非确定性的；行为检查属于评估（第 4 步），而不是 `pytest` 或 `go test`。使用 `agents-cli run "prompt"` 进行快速检查。

### 提供配方基础设施（如果您修改了它）

需要支持基础设施（数据存储、索引、沙盒、队列）的配方会自带其自己的提供：遵循其 `Makefile`（例如 `make setup-infra`，`make data-ingestion`）及其 `AGENTS.md` / `README.md`，将配方的 `infra/terraform/` 和 `.env` 适应到您的项目中。`agents-cli` 没有此命令。

## 第 4 步：评估

**这是最重要的阶段。** 评估验证代理端到端的行为。

**强制要求：** 在运行评估之前激活 `/google-agents-cli-eval`。它包含数据集模式、配置格式和关键陷阱。不要跳过它。

**不要跳过此阶段。** 在构建代理后，您必须继续进行评估。

**单元测试与 `agents-cli eval` 的区别：**
- **单元测试** (`uv run pytest` 对于 Python，`go test ./...` 对于 Go) — 测试 *代码正确性*：导入是否工作、函数是否返回预期类型、API 合同是否有效。它不测试代理行为是否良好。
- **`agents-cli eval`** — 测试 *代理行为*：响应质量、工具使用、角色一致性、安全合规性。这是验证代理实际工作的东西。
- **`agents-cli run "prompt"`** — 开发期间的快速一次性冒烟测试。如果测试多个提示，请使用 `--start-server` 选项以持久化本地服务器，这减少了重复调用的开销，并允许通过 `--session-id` 恢复本地会话。用于快速迭代，而不是单元测试。

**永远不要编写检查 LLM 响应内容的单元测试**（例如，断言出现海盗关键词、检查代理是否提到过敏）。LLM 输出是非确定性的。改用带有 LLM 作为法官标准的评估。

1. **从小处着手**：从 1-2 个样本评估用例开始，而不是完整套件
2. 运行评估：`agents-cli eval run`（链式 `generate` + `grade`）。对于调试或自定义跟踪位置，使用两步形式：`agents-cli eval generate` 然后 `agents-cli eval grade`。
3. 与用户讨论结果
4. 修复问题并首先迭代核心用例
5. 只有在核心用例通过后，才添加边缘用例和新场景
6. 重复直到每个用例都达到您与用户商定的标准（`eval run` 退出 0 无论分数如何，所以请阅读它们）

**这里可能需要 5-10 次以上的迭代。**

## 第 5 步：部署

一旦用户同意评估分数足够好：

1. 检查项目是否配置了部署目标——运行 `agents-cli info` 查看当前配置
2. 如果项目是原型（没有部署目标），请先添加部署支持：
   ```bash
   agents-cli scaffold enhance . --deployment-target <target>
   ```
   查看 `/google-agents-cli-deploy` 获取部署目标决策矩阵（Agent Runtime vs Cloud Run vs GKE）。
3. 准备好后部署：`agents-cli deploy`

**重要**：未经明确的人类批准，永远不要部署。

## 第 6 步：发布（可选）

并非所有代理都需要此功能——目前支持 Gemini Enterprise。请参阅 `/google-agents-cli-publish` 获取注册模式、标志和故障排除。

## 第 7 步：观察

部署后，使用可观察性工具监控代理在生产中的行为。请参阅 `/google-agents-cli-observability` 获取 Cloud Trace、提示-响应日志记录、BigQuery Analytics 和第三方集成。

---

# 编码代理的运维指南

## 常见捷径要抵制

代理例行跳过带有看似合理的借口。识别这些并抵制：

| 短-cut | 为什么它失败了 |
|----------|-------------|
| "用户的请求足够清晰，无需澄清" | 你在猜测需求。第 0 步存在于在脚手架之前确认意图——即使一个问题也可以防止全面返工。 |
| "在 `agents-cli run` 中代理响应正确，所以不需要评估" | 一个提示不是一个测试套件。评估会捕获回归、边缘情况和工具轨迹问题，而单个运行永远不会。 |
| "我会使用一个更新/更好的模型" | 脚手架的模型是经过精心选择的。在没有被要求更改的情况下更改它违反了代码保留（原则 1）并经常导致问题——错误的位置、已弃用的版本或 404。你的训练数据可能过时了——依赖技能和模型列出命令，而不是你对模型名称的了解。 |
| "我已经知道如何构建这个——沙盒、内存、批准门" | 你即将重新发明一个配方，更糟。这些功能已经实现并经过实战检验在 `/google-agents-cli-adk-code` → `references/samples.md`；在设计任何自定义内容之前检查主题索引并打开匹配配方的 `AGENTS.md`。 |
| "我可以跳过脚手架并手动设置" | 手动设置会遗漏评估样板、CI/CD 配置和项目配置约定。即使对于快速实验，也请使用 `agents-cli create`。 |

## 原则 1：代码保留与隔离

代码修改需要外科手术般的精确度——仅修改用户请求直接针对的代码段，并严格保留所有周围和不相关的代码。

**强制执行前的验证：**

在最终确定任何代码替换之前，验证以下内容：

1. **目标识别：** 基于用户明确的指示，明确定义要更改的确切行或表达式。
2. **保留检查：** 确认所有代码、配置值（例如，`model`、`version`、`api_key`）、注释和格式化*在*识别的目标之外保持完全相同。

**示例：**

- **用户请求：** "更改代理的指令为配方建议者。"
- **不正确（违反）：**
  ```python
  root_agent = Agent(
      name="recipe_suggester",
      model="gemini-1.5-flash",  # 未打算更改 - 模型没有被要求更改
      instruction="You are a recipe suggester."
  )
  ```
- **正确（遵守）：**
  ```python
  root_agent = Agent(
      name="recipe_suggester",  # OK，与新的目的相关
      model="gemini-3.8-flash",  # 保留
      instruction="You are a recipe suggester."  # OK，直接目标
  )
  ```

## 原则 2：执行最佳实践

- **模型选择——关键：**
  - **永远不要更改模型，除非明确要求。**
  - 在创建新代理时（不是修改现有代理），使用最新的 Gemini 模型。列出您的代理实际使用的位置上的可用模型（`GOOGLE_CLOUD_LOCATION`；默认为 `global`）——不是每个模型都从每个位置提供：
    ```bash
    uv run --with google-genai python -c "
    from google import genai
    # 使用您的 GOOGLE_CLOUD_LOCATION ('global', 或一个区域，例如 'us-east1')
    client = genai.Client(vertexai=True, location='global')
    for m in client.models.list(): print(m.name)
    "
    ```
  - 不要使用旧模型，除非明确要求。对于模型文档，获取 `https://adk.dev/agents/models/google-gemini/index.md`。另请参阅 [稳定模型版本](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versions) 和 [模型端点位置](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/locations#google-models)。

- **运行 Python 命令：**
  - 始终使用 `uv` 执行 Python 命令（例如，`uv run python script.py`）
  - 在执行脚本之前运行 `uv sync`

- **中断无限循环：**
  - 如果你连续 3 次以上看到相同的错误，请**立即停止**。
  - **红旗**：锁 ID 递增、名称追加 v5→v6→v7、"我会再试一次"重复
  - **状态冲突**（错误 409）：使用 `terraform import` 而不是重试创建
  - **卡住时**：直接运行底层命令（例如，`terraform` CLI）

- **故障排除：**
  - 首先检查 `/google-agents-cli-adk-code`——它涵盖了大多数常见模式
  - 使用 WebFetch 对来自 ADK 文档索引的 URL（`curl https://adk.dev/llms.txt`）进行深入探讨
  - 当遇到持久错误时，有针对性的网络搜索通常能更快找到解决方案
  - **CLI 命令失败：** 运行 `agents-cli <command> --help`——输出以指向实现该命令的确切源文件的 `Source:` 行结束。阅读它以了解逻辑并诊断故障。如果您需要浏览多个文件，请使用 `agents-cli info` 获取完整的 CLI 安装路径。

### 系统性调试

当某事出错时，请按照此顺序操作——不要跳过步骤或进行扫射修复：

1. **重现**——运行导致失败的 exact 命令。保存完整错误输出。如果您无法重现它，您就无法修复它。
2. **定位**——缩小原因：是代理代码、工具、配置还是环境？使用 `agents-cli run "prompt"` 将代理行为与部署问题隔离开。添加 `-v` (`--verbose`) 来打印完整的 JSON 事件有效负载——这对于检查工具调用、中间步骤和静默失败很有用。
3. **一次修复一件事**——一次改变一个变量。如果你同时更改指令、工具和配置，你将不知道是什么修复了它（或者是什么破坏了其他东西）。
4. **验证**——重新运行 exact 重现命令。不要假设修复了它。
5. **保护**——如果这是一个非明显的错误，请添加一个评估用例来捕获回归。

**停线规则：** 如果更改破坏了原本正常工作的东西，请停止功能工作并首先修复回归。不要推进希望以后再回来——回归会累积。

- **环境变量：**
  - `.env` 文件和环境变量分配（例如，`GOOGLE_CLOUD_PROJECT`、`GOOGLE_CLOUD_LOCATION`）通常是代理正常运行的必要条件——除非用户明确要求，否则永远不要删除或修改它们
  - 如果项目根目录中存在 `.env` 文件，将其视为重要配置
  - 对于密钥和 API 密钥，请优先使用 GCP Secret Manager 而不是纯 `.env` 条目——有关密钥管理指南，请参阅 `/google-agents-cli-deploy`。

---

## 使用临时脚手架作为参考

当您需要特定的基础设施文件（Terraform、CI/CD、Dockerfile）但不想修改当前项目时，使用 `/google-agents-cli-scaffold` 创建一个 `/tmp/` 中的临时项目并将您需要的内容复制过来。

---

## 参考文件

| 文件 | 内容 |
|------|----------|
| `references/internals.md` | `agents-cli` 包装的底层工具和命令，按语言（Python：adk、uv、ruff；Go：adk-go、go、golangci-lint） |
| `references/spec-template.md` | `.agents-cli-spec.md` 模板和可选部分 |
| `references/brainstorming.md` | 第 0 步设计对话剧本（一次一个问题、方法、门） |
| `references/terminology.md` | 产品名称 → CLI 值映射 |
| `references/commands.md` | 每个阶段的 `agents-cli` 命令索引 |
| `references/extension.md` | 编写一个 ad-hoc 扩展或采用现有的扩展（覆盖或添加命令） |

## 开发命令

运行 `agents-cli --help` 或 `agents-cli <command> --help` 获取权威标志列表。每个阶段的命令索引位于 `references/commands.md`；每个阶段的用法在上述各阶段部分中。

要**覆盖**一个内置命令（例如，用合规性检查包装 `deploy`）或**添加一个新命令**，agents-cli 有一个扩展系统。要为这个仓库编写一个 ad-hoc 扩展，或采用现有的扩展，请加载 `references/extension.md`。

---

## 技能版本

> **故障排除提示：** 如果技能似乎过时或不完整，请重新安装：
> ```
> agents-cli setup --skip-auth
> ```
> 只有当您怀疑过时的技能导致问题时才这样做。
