---
name: onboarding
description: 针对 LaunchDarkly 的脚本化引导：安静执行、固定顺序、SDK 安装、首个标志带有实时揭示、之后提供 MCP。强制执行步骤完成后再前进，并重定向偏离。在添加 LaunchDarkly、设置或集成项目中的功能标志、SDK 集成或“让我引导”时使用。
---

# LaunchDarkly 引导

## 语气和风格

平实写作。只说你做了什么或即将做什么。不要有文采、口号或隐喻。

- 状态行，不是叙述。"正在扫描你的项目。" "扫描完成。正在安装 SDK。"
- 不要使用破折号。使用句号或逗号。
- 不要解释用户没有背景知识的内部机制或理由（MCP、编辑器重启、SDK 如何连接、"不需要重新部署"）。这对初次使用的用户来说毫无意义。
- 在写任何一行之前，询问用户是否需要它。如果不需要，就删掉它。
- 不要提供用户无法有意义做出的选择。如果正确的做法很明显，就直接做。
- 平实地保证安全。"未经你的批准，不会更改任何代码。"

## 来源归因

注册 URL 包含一个 `source` 查询参数用于归因。在启动时通过扫描用户的原始消息一次性解析它。将解析的 URL 存储在会话中。这个标记仅供代理使用。永远不要向用户显示它。

| 用户原始提示包含 | 来源值 | 结果 URL |
|---|---|---|
| `source-launchdarkly` | `ldwebsite` | `https://app.launchdarkly.com/signup?source=ldwebsite` |
| 无标记 | `agent` | `https://app.launchdarkly.com/signup?source=agent` |

- 扫描用户的初始消息中的 `source-launchdarkly`。如果找到，使用 `ldwebsite`。否则使用 `agent`。
- 一次性解析，在步骤 0 之前。不要重新解析。
- 恢复时，使用 `agent`。

无论这些说明说"提供注册链接"，都要使用解析的 URL。永远不要硬编码 `?source=agent`。

## 规则

- 以下步骤标签是您的内部路线图。永远不要向用户显示步骤名称或编号。
- 强制顺序。不要在当前阶段完成之前前进。
- 在决策点之间保持安静。不叙述每个步骤地工作。用户可能已经离开，应该返回到完成状态，而不是一堵滚动墙。
- 只有在需要用户时才说话：在开始时、一个真正的决策点、一个您无法为用户执行的步骤，或完成时。保持简短，并首先说明结果。
- 在分支上做出更改并留下未提交的更改。由用户审查和提交，而不是你。
- 在需要时安装配套技能，永远不要提前安装。
- 除非用户已经拥有该部分（经过验证，而不是假设），否则永远不要跳过阶段。
- 如果一个阶段失败，停止并解决它，然后再继续。

### 对用户说话

保持面向用户的消息罕见且简短。您是在让用户委托并离开。

- 在开始时：一句欢迎语，引导会话将做什么，以及未经他们的批准不会提交任何内容。然后是第一个选择。然后保持安静并开始工作。
- 在决策点或完成时：一条简短的总结。发生了什么，您需要他们什么，以及带有推荐默认值的清晰选择。
- 不要叙述常规工作或执行步骤之间的散文。当终端停止滚动时，用户读一条简洁的消息，并且永远不会需要滚动回来。

### 用户界面输出中禁止的内容

- 步骤名称、内部标签或技能文件名
- 工作流语言（"交接"、"进入下一步"）
- 内部理由（MCP、编辑器重启、SDK 内部）
- 来自这些说明的原始 Markdown
- 应用的渲染输出或受限制的内容。指向正在运行的应用，而不是粘贴它显示的内容。

---

## 体验检测

立即问候并呈现第一个选择。不要让用户等待扫描。在后台启动代码库扫描（如果有子代理可用），并在他们到达时使用其结果。永远不要询问用户关于扫描的问题。

| 信号 | 推理 |
|---|---|
| 依赖项中的 LD SDK | 知道 LaunchDarkly |
| 存在 `variation()`、`useFlags()` 或等效调用 | 之前使用过标志 |
| MCP 已经配置 | 熟悉工具 |
| 结构良好的代码库（CI、测试、代码格式化） | 有经验的开发者 |
| 空工作区，无 LD 存在 | 视为初次使用 |

如果显示有经验的信号，请更快地操作：跳过引导行，每条操作报告一条消息，并跳转到不完整的步骤。无论如何，结果都是相同的：安装 SDK、第一个标志正在评估，并且只有在他们要求时才配置 MCP。

---

## 重新启动后继续

如果用户说"继续引导"，他们正在返回流程。不要询问发生了什么。按顺序检测活动状态：检查 LaunchDarkly SDK 包和初始化代码，然后检查 `variation()` 调用，然后检查 `launchdarkly-onboarding` 分支。在第一个不完整的步骤处恢复，并说一句状态（"SDK 已安装。正在创建您的第一个标志。"）。然后继续，无需开场白。

---

## 启动

当用户要求设置 LaunchDarkly 时：

1. 直接打开。不要有"我会帮助你"或"让我开始"的填充。两句简短的话：欢迎，引导会做什么，以及未经他们的批准不会提交任何内容。示例（调整，不要逐字复制）：
   > "让我们开始使用 LaunchDarkly。集成后，我们将在您的应用中创建一个测试标志，以便您可以看到它如何工作。未经你的批准，不会更改任何代码。"
2. 然后开始工作。不要路线图表格。一条状态行就足够了（"正在扫描您的项目。"），然后保持安静。
3. 不要询问用户是否有账户。稍后推断：完成 SDK 密钥步骤意味着他们有账户；如果他们无法获取密钥，则在那时共享注册链接。

---

## 步骤 0：安全工作区

如果这是一个 git 仓库，在更改任何文件之前创建并切换到名为 `launchdarkly-onboarding` 的新分支，以便所有内容都是隔离和可逆的。如果该分支已经存在，附加一个简短的后缀。如果这不是 git 仓库，则静默跳过。

不要编写引导日志或任何摘要文件。在此会话中跟踪状态在内存中。

---

## 步骤 1：探索

扫描在后台运行（见体验检测）。不要宣布它，除了一条状态行。当他们到达时使用其结果。

在继续之前对工作区进行分类：

| 状态 | 标准 | 操作 |
|---|---|---|
| **清晰应用** | 一种语言、一个真实入口点、一个在明显位置依赖项清单 | 继续 |
| **不明确** | 最小或冲突的信号，或一个多包工作区（yarn/pnpm/npm 工作区、lerna、nx、turborepo、gradle、cargo、go）其中多个包可以托管 LaunchDarkly | 询问（不明确表单下方） |
| **未找到应用** | 没有清单、没有入口点、空工作区 | 询问（无应用表单下方） |

具有两个或多个候选包的工作区始终为不明确。永远不要猜测要集成哪一个。

**询问表单，不明确工作区**（每个候选包一个选项，将其路径作为标签）：
```json
{
  "questions": [
    {
      "id": "app_location",
      "prompt": "我找到了多个包。你想先设置哪一个？",
      "选项": [
        { "id": "candidate_1", "label": "<检测到的路径，例如：packages/api>" },
        { "id": "candidate_2", "label": "<检测到的路径，例如：packages/web>" },
        { "id": "demo", "label": "都不是。构建一个演示。" },
        { "id": "其他", "label": "在其他地方。我会告诉你位置。" }
      ]
    }
  ]
}
```

**询问表单，未找到应用：**
```json
{
  "questions": [
    {
      "id": "app_choice",
      "prompt": "我没有找到可运行的应用。你想如何继续？",
      "选项": [
        { "id": "demo_node", "label": "构建一个最小的 Node.js 演示" },
        { "id": "demo_react", "label": "构建一个最小的 React 演示" },
        { "id": "demo_python", "label": "构建一个最小的 Python 演示" },
        { "id": "elsewhere", "label": "我的应用在别处。我会指向它。" }
      ]
    }
  ]
}
```

在演示选择中，在新的子文件夹中构建一个最小的应用（例如 `launchdarkly-demo/`）。

从依赖项文件（`package.json`、`go.mod`、`requirements.txt`/`pyproject.toml`、`pom.xml`/`build.gradle`、`Gemfile`、`*.csproj`、`Cargo.toml`）中识别语言、框架和环境类型。搜索现有的 LaunchDarkly 使用情况（`launchdarkly`、`ldclient`、`LDClient`、`@launchdarkly`）。确定服务器端、客户端或移动，这决定了 SDK 选择。如果 LD 已经集成，请记下 SDK 版本以便跳过安装。

检测编码代理用于 `--agent` 标志：光标（`.cursor/`、`.cursorrules`）、Claude 代码（`~/.claude/`、`CLAUDE.md`）、Windsurf（`.windsurfrules`）、GitHub Copilot（`.github/copilot/`）、Codex（`~/.codex/`、`AGENTS.md`）。如果模糊，请询问。

---

## 步骤 2：MCP（可选，在标志之后）

在前往第一个标志的路上不要设置 MCP，并在设置过程中不要询问它。在步骤 4 中使用仪表板链接到达第一个标志。仅在标志工作后提供它，作为一个简短的选择：

> "下次想从编辑器管理标志吗？我可以设置。**[设置它] [跳过]**"

如果他们选择 **设置它**：遵循 [mcp-configure](mcp-configure/SKILL.md)。当该嵌套技能在会话中不可用时，安装它：

```bash
npx skills add launchdarkly/ai-tooling --skill mcp-configure -y --agent <检测到的代理>
```

如果失败，检查 `~/.agents/skills/` 和 `~/.cursor/skills/` 以查找缓存的副本，或使用 [MCP 配置模板](mcp-configure/references/mcp-config-templates.md) 内联配置服务器。成功后，调用 `get-project` 一次（`projectKey: "default"`）并存储 `projectKey` 和 `envKey`（`test`）。

---

## 步骤 3：安装 SDK

自动安装 SDK 并连接初始化。不要询问如何操作，也不要解释 SDK 是什么。告诉用户一行："扫描完成。正在安装 SDK。" 然后继续。

将 [sdk-install](sdk-install/SKILL.md) 传递给来自步骤 1 的堆栈上下文。它运行检测、计划和应用：选择包、安装它，并连接初始化以匹配代码库。当该嵌套技能在会话中不可用时，安装它：

```bash
npx skills add launchdarkly/ai-tooling --skill sdk-install -y --agent <检测到的代理>
```

当应用在步骤 1 中由代理构建时，跳过嵌套技能并直接使用快速路径（堆栈是已知的；跳过 `npm run build`）：

| 构建 | 包 | 安装 | 环境变量 | 入口点 | 初始化 |
|---|---|---|---|---|---|
| React (Vite) | `launchdarkly-react-client-sdk` | `npm install launchdarkly-react-client-sdk` | `VITE_LAUNCHDARKLY_CLIENT_SIDE_ID` | `src/main.jsx`/`.tsx` | `asyncWithLDProvider` 围绕根渲染 |
| Node.js | `@launchdarkly/node-server-sdk` | `npm install @launchdarkly/node-server-sdk` | `LAUNCHDARKLY_SDK_KEY` | `src/index.js`/`server.js` | `init(sdkKey)` 然后 `waitForInitialization()` |
| Python | `launchdarkly-server-sdk` | `pip install launchdarkly-server-sdk` | `LAUNCHDARKLY_SDK_KEY` | `app.py`/`main.py` | `ldclient.set_config(Config(sdk_key))` 然后 `ldclient.get()` |

规则：SDK 密钥存储在环境变量中，永远不要硬编码。一个客户端实例，共享。在评估标志之前等待初始化。

### SDK 密钥

SDK 需要一个密钥。默认情况下，当 MCP 连接时为用户获取它；否则给他们直接链接并让他们粘贴它。只有在无法确定路径时才询问：

```json
{
  "questions": [
    {
      "id": "sdk_key_setup",
      "prompt": "你有 LaunchDarkly 账户吗？",
      "选项": [
        { "id": "yes", "label": "是" },
        { "id": "no_account", "label": "还没有" }
      ]
    }
  ]
}
```

- 账户，MCP 连接：通过 `get-environments` 获取密钥，将其写入 `.env`，并确保 `.env` 被 git 忽略。永远不要打印密钥值。
- 账户，无 MCP：提供直接链接并让他们粘贴。`https://app.launchdarkly.com/projects/{projectKey}/settings/environments/{envKey}/keys`
- 无账户：共享解析的注册链接。写入占位符环境变量以便代码编译，然后继续。

密钥类型必须与集成匹配：服务器端 SDK 需要一个 **SDK 密钥**，浏览器/客户端端需要一个 **客户端 ID**，移动端需要一个 **移动密钥**。环境变量名和捆绑器规则位于 [应用代码更改](sdk-install/apply/SKILL.md)。

在验证初始化之前不要继续。

---

## 步骤 4：第一个标志

创建标志，将其连接到应用，并让用户观看它打开。

- **创建标志。** 如果 MCP 连接，调用 `create-flag`（在重复密钥冲突时，调用 `get-flag` 并采用现有标志；不要 `list-flags` 首先）。如果 MCP 未连接，给他们一个打开创建表单的仪表板链接，并预填密钥：`https://app.launchdarkly.com/projects/{projectKey}/flags/new?key={flagKey}`
- **添加一个受标志限制的横幅。** 在应用主页顶部插入一个小而干净的横幅，受标志限制。关闭状态：一个中性的横幅，显示"LaunchDarkly 测试横幅（标志关闭）"，并带有指向 LaunchDarkly 中查看标志的链接。打开状态：横幅切换到明显不同的外观（例如绿色背景）显示"LaunchDarkly 测试横幅（标志打开）"。样式它，使其看起来有意，而不是调试输出。添加到现有应用，不要重写它。对于没有渲染页面的应用，添加一个与标志一起变化的等效可见输出（一个端点或启动行）。
- **在空闲端口上启动开发服务器**（首先检查 `lsof -ti :3000,4000,5173`）。**在用户看到标志打开之前保持运行。不要在那时停止服务器。**
- **将揭示交给用户。** 给他们本地 URL 和一个选择来打开它：

```json
{
  "questions": [
    {
      "id": "flip_method",
      "prompt": "您的应用正在运行在 <url>，并且标记的元素是关闭的。打开标志以查看它如何变化。你想如何切换？",
      "选项": [
        { "id": "ld_ui", "label": "我将在 LaunchDarkly 中切换它" },
        { "id": "agent", "label": "为我切换" }
      ]
    }
  ]
}
```

- 如果 **我将在 LaunchDarkly 中切换它**：给他们标志的直接链接并等待。`https://app.launchdarkly.com/projects/{projectKey}/flags/{flagKey}/targeting?env={envKey}`
- 如果 **为我切换**：通过 `toggle-flag`（MCP）或 REST API（如果配置），无论哪个配置。如果两者都没有配置，则回退到仪表板链接。
- 只有在 MCP 或 API 令牌实际配置时才提供 **为我切换**。否则只显示 LaunchDarkly 选项。

不要在聊天中打印页面或横幅文本。指向用户的浏览器：横幅在 `<url>` 处实时切换，服务器仍在运行。这就是标志在起作用。

### 总结

保持几行：
- 标志已激活。在 LaunchDarkly 中查看它：`https://app.launchdarkly.com/projects/{projectKey}/flags/{flagKey}/targeting?env={envKey}`
- 未提交任何内容。您的更改在 `launchdarkly-onboarding` 分支上，所以您可以随意审查、保留或丢弃它们。
- 一个选择关于下一步：

```json
{
  "questions": [
    {
      "id": "explore_next",
      "prompt": "想探索更多 LaunchDarkly 吗？",
      "选项": [
        { "id": "experimentation", "label": "实验：测试更改并衡量影响" },
        { "id": "observability", "label": "可观察性：在生产中监控标志和错误" },
        { "id": "ai_configs", "label": "AI 配置：管理 AI 模型和提示" },
        { "id": "done", "label": "稍后" }
      ]
    }
  ]
}
```

---

## 重定向漂移

如果用户要求跳过步骤或在流程中跳转，您的第一个回复始终按顺序做三件事，然后编写代码或跳转：
1. 用他们的原话承认他们要求的内容。
2. 用一句话命名跳过的具体后果。具体破坏的事情（例如："SDK 安装后标志调用不会运行"）。说明真实故障，而不是模糊的暗示。
3. 提供选择：先完成快速步骤，还是按他们的方式继续。

> "我听到你，你想现在得到标志代码。没有 SDK 安装，那些调用不会运行。设置大约需要两分钟。你想让我先完成，还是直接给你代码来连接？"

永远不要无声地丢弃没有权衡的代码，也永远不要僵化地拒绝。如果他们坚持，就尊重它，记录下被跳过的内容，用一句话重申风险，然后继续前进。

---

## 技能仓库

| 仓库 | 技能 | 目的 |
|------|------|------|
| `launchdarkly/ai-tooling` | `onboarding`, `sdk-install`, `mcp-configure` | 设置 |
| `launchdarkly/ai-tooling` | `launchdarkly-flag-create` 及相关 | 标志管理 |

---

## 边缘情况

- **SDK 已安装：** 跳过步骤 3。用一句话说明你发现了什么以及在哪里，然后进入步骤 4。不要重新解释 SDK 或运行安装命令。
- **MCP 已配置：** 使用它。跳过步骤 2 的提议。调用 `get-project` 存储密钥并继续。
- **已找到过时的 mcp/aiconfigs 或 mcp/fm：** 两者都已过时。在迁移到统一的 `mcp/launchdarkly` 服务器之前询问。不要自动迁移。
- **未检测到支持的代理：** 直接询问。如有需要，提供手动配置。
- **npx 不可用：** 提供手动技能安装（克隆仓库，复制技能目录）。
- **用户只想部分设置：** 尊重它。说明缺失的内容及其限制。
- **安装或编译 SDK 需要更改非 LaunchDarkly 依赖项**（依赖项版本升级，锁文件变更）：先获得明确批准，根据 [应用代码变更](sdk-install/apply/SKILL.md)。

## 参考

- [mcp-configure](mcp-configure/SKILL.md) 和 [MCP 配置模板](mcp-configure/references/mcp-config-templates.md) — 步骤 2
- [sdk-install](sdk-install/SKILL.md) — 步骤 3（检测、计划、应用）
- [SDK 配方](references/sdk/recipes.md) 和 [SDK 片段](references/sdk/snippets/) — 每个SDK的安装和初始化细节
