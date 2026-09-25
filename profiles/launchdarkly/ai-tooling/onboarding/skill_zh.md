# LaunchDarkly 引导

## 语气和风格

平实写作。只说你做了什么或即将做什么。不要有花哨的语句、口号或隐喻。

- 状态行，不是叙述。"正在扫描你的项目。" "扫描完成。正在安装 SDK。"
- 不要使用破折号。使用句号或逗号。
- 不要解释用户没有背景知识的内部机制或理由（MCP、编辑器重启、SDK 如何连接、"不需要重新部署"）。这对新用户来说毫无意义。
- 在写任何一行之前，询问用户是否需要。如果不需要，就删掉它。
- 不要提供用户无法有意义选择的选项。如果正确的做法很明显，就直接做。
- 平实地保证安全。"未经你的批准，不会更改任何代码。"

## 来源归因

注册 URL 包含一个 `source` 查询参数用于归因。在启动时通过扫描用户的原始消息一次性解析它。将解析的 URL 存储在会话中。这个标记仅供代理使用。永远不要展示给用户。

| 用户原始提示包含 | 来源值 | 结果 URL |
|---|---|---|
| `source-launchdarkly` | `ldwebsite` | `https://app.launchdarkly.com/signup?source=ldwebsite` |
| 无标记 | `agent` | `https://app.launchdarkly.com/signup?source=agent` |

- 扫描用户的初始消息中的 `source-launchdarkly`。如果找到，使用 `ldwebsite`。否则使用 `agent`。
- 一次性解析，在步骤 0 之前。不要重新解析。
- 在恢复时，使用 `agent`。

无论这些说明说"提供注册链接"，都要使用解析的 URL。永远不要硬编码 `?source=agent`。

## 规则

- 以下步骤标签是你们的内部路线图。永远不要向用户展示步骤名称或编号。
- 强制顺序。不要在当前阶段完成之前前进。
- 在决策点之间保持安静。不叙述每个步骤地工作。用户可能已经离开，应该返回到一个完成的状态，而不是一堵滚动墙。
- 只有在需要用户时才说话：在开始时、一个真正的决策点、一个你不能为他们执行的手动步骤，或完成时。保持简短，并首先说明结果。
- 在一个分支上做出更改并留下未提交的更改。用户审查并提交，而不是你。
- 在需要时安装配套技能，永远不要提前安装。
- 除非用户已经拥有该部分（验证，而不是假设），否则永远不要跳过阶段。
- 如果一个阶段失败，停止并解决它，然后再继续。

### 对用户说话

保持面向用户的消息罕见且简短。你是在让用户委托并离开。

- 在开始时：一条欢迎语，引导会做什么，以及没有他们的批准不会提交任何内容。然后是第一个选择。然后保持安静并开始工作。
- 在一个决策点或完成时：一条简短的总结。发生了什么，你需要什么，以及带有推荐默认值的清晰选择。
- 不要叙述例行工作或执行步骤之间的散文。当终端停止滚动时，用户读一条简洁的消息，并且永远不会需要滚动回来。

### 用户界面输出中的禁止项

- 步骤名称、内部标签或技能文件名
- 工作流语言（"交接"、"进入下一步"）
- 内部理由（MCP、编辑器重启、SDK 内部）
- 来自这些说明的原始 Markdown
- 应用的渲染输出或受限制的内容。指向正在运行的应用，而不是粘贴它显示的内容。

---

## 体验检测

立即问候并展示第一个选择。不要让用户等待扫描。在后台开始代码库扫描（如果有可用的子代理），并在他们到达时使用其结果。永远不要询问用户关于扫描的情况。

| 信号 | 推理 |
|---|---|
| 依赖项中的 LD SDK | 知道 LaunchDarkly |
| 存在 `variation()`、`useFlags()` 或等效调用 | 之前使用过标志 |
| MCP 已经配置 | 熟悉工具 |
| 结构良好的代码库（CI、测试、代码检查） | 经验丰富的开发者 |
| 空工作区，没有 LD 存在 | 视为首次使用 |

如果显示经验信号，就更快：跳过指导行，每条行动并报告它，然后跳到不完整的步骤。无论如何，结果都是相同的：安装 SDK、第一个标志正在评估，以及只有在他们要求时才配置 MCP。

---

## 重新启动后继续

如果用户说"继续引导"，他们正在返回流程。不要询问发生了什么。按顺序检测活动状态：检查 LaunchDarkly SDK 包和初始化代码，然后是 `variation()` 调用，然后是 `launchdarkly-onboarding` 分支。在第一个不完整的步骤处恢复，并说一句状态（"SDK 已安装。正在创建你的第一个标志。"）。然后继续，不要铺垫。

---

## 启动

当用户要求设置 LaunchDarkly 时：

1. 直接打开。不要有"我会帮助你"或"让我开始"的填充。两句简短的话：一个欢迎，引导会做什么，以及没有他们的批准不会提交任何内容。示例（适应，不要逐字复制）：
   > "让我们开始使用 LaunchDarkly。集成后，我们将在你的应用中创建一个测试标志，以便你了解它是如何工作的。未经你的批准，不会更改任何代码。"
2. 然后开始工作。不要路线图表格。一条状态行就足够了（"正在扫描你的项目。"），然后保持安静。
3. 不要询问用户是否有账户。稍后推断：完成 SDK 密钥步骤意味着他们有账户；如果他们无法获取密钥，则在那时分享注册链接。

---

## 步骤 0：安全工作区

如果这是一个 git 仓库，在更改任何文件之前创建并切换到名为 `launchdarkly-onboarding` 的新分支，以便一切都被隔离和可逆。如果该分支已经存在，追加一个简短的后缀。如果这不是一个 git 仓库，就安静地跳过。

不要编写引导日志或任何摘要文件。在本次会话中，将状态保存在内存中。

---

## 步骤 1：探索

扫描在后台运行（见体验检测）。不要宣布它，除了一条状态行。当他们到达时使用其结果。

在继续之前对工作区进行分类：

| 状态 | 标准 | 操作 |
|---|---|---|
| **清晰应用** | 一种语言，一个真实的入口点，一个在明显位置的单个依赖项清单 | 继续 |
| **不明确** | 最小或冲突的信号，或一个多包工作区（yarn/pnpm/npm 工作区、lerna、nx、turborepo、gradle、cargo、go）其中多个包可以托管 LaunchDarkly | 询问（不明确形式下方） |
| **未找到应用** | 没有清单，没有入口点，空工作区 | 询问（无应用形式下方） |

具有两个或多个候选包的工作区始终为不明确。永远不要猜测要集成哪一个。

**询问形式，不明确工作区**（每个候选包一个选项，将其路径作为标签）：
```json
{
  "questions": [
    {
      "id": "app_location",
      "prompt": "我找到了多个包。你想先设置哪一个？",
      "options": [
        { "id": "candidate_1", "label": "<检测到的路径，例如：packages/api>" },
        { "id": "candidate_2", "label": "<检测到的路径，例如：packages/web>" },
        { "id": "demo", "label": "都不是。构建一个演示。" },
        { "id": "other", "label": "其他地方。我会告诉你在哪里。" }
      ]
    }
  ]
}
```

**询问形式，未找到应用：**
```json
{
  "questions": [
    {
      "id": "app_choice",
      "prompt": "我没有找到可运行的应用。你想如何继续？",
      "options": [
        { "id": "demo_node", "label": "构建一个最小的 Node.js 演示" },
        { "id": "demo_react", "label": "构建一个最小的 React 演示" },
        { "id": "demo_python", "label": "构建一个最小的 Python 演示" },
        { "id": "elsewhere", "label": "我的应用在别处。我会指向它。" }
      ]
    }
  ]
}
```

在选择演示时，在新的子文件夹中构建一个最小的应用（例如 `launchdarkly-demo/`）。

从依赖项文件（`package.json`、`go.mod`、`requirements.txt`/`pyproject.toml`、`pom.xml`/`build.gradle`、`Gemfile`、`*.csproj`、`Cargo.toml`）中识别语言、框架和环境类型。搜索现有的 LaunchDarkly 使用情况（`launchdarkly`、`ldclient`、`LDClient`、`@launchdarkly`）。确定是服务器端、客户端还是移动端，这决定了 SDK 选择。如果 LD 已经集成，请注意 SDK 版本以便跳过安装。

检测编码代理用于 `--agent` 标志：光标（`.cursor/`、`.cursorrules`）、克劳德代码（`~/.claude/`、`CLAUDE.md`）、风帆（`.windsurfrules`）、GitHub Copilot（`.github/copilot/`）、Codex（`~/.codex/`、`AGENTS.md`）。如果模糊，请询问。

---

## 步骤 2：MCP（可选，在标志之后）

在前往第一个标志的路上不要设置 MCP，在设置过程中也不要询问它。在没有 MCP 的情况下达到第一个标志（步骤 4 使用仪表板链接）。只在标志工作后提供它，作为一个简短的选择：

> "下次想从编辑器管理标志吗？我可以设置它。**[设置它] [跳过]**"

如果他们选择 **设置它**：遵循 [mcp-configure](mcp-configure/SKILL.md)。当该嵌套技能在会话中不可用时，安装它：

```bash
npx skills add launchdarkly/ai-tooling --skill mcp-configure -y --agent <检测到的代理>
```

如果失败，检查 `~/.agents/skills/` 和 `~/.cursor/skills/` 以查找缓存的副本，或使用 [MCP 配置模板](mcp-configure/references/mcp-config-templates.md) 内联配置服务器。成功后，调用 `get-project` 一次（`projectKey: "default"`）并存储 `projectKey` 和 `envKey`（`test`）。

---

## 步骤 3：安装 SDK

自动安装 SDK 并连接初始化。不要询问如何，也不要解释 SDK 是什么。告诉用户一行："扫描完成。正在安装 SDK。" 然后继续。

将 [sdk-install](sdk-install/SKILL.md) 传递给来自步骤 1 的堆栈上下文。它运行检测、计划和应用：选择包、安装它，并连接初始化以匹配代码库。当该嵌套技能在会话中不可用时，安装它：

```bash
npx skills add launchdarkly/ai-tooling --skill sdk-install -y --agent <检测到的代理>
```

当应用由代理在步骤 1 中构建时，跳过嵌套技能并直接使用快速路径（堆栈是已知的；跳过 `npm run build`）：

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
      "options": [
        { "id": "yes", "label": "是" },
        { "id": "no_account", "label": "还没有" }
      ]
    }
  ]
}
```

- 账户，MCP 连接：通过 `get-environments` 获取密钥，将其写入 `.env`，并确保 `.env` 被 git 忽略。永远不要打印密钥值。
- 账户，没有 MCP：提供直接链接并让他们粘贴。`https://app.launchdarkly.com/projects/{projectKey}/settings/environments/{envKey}/keys`
- 没有账户：分享解析的注册链接。写入占位符环境变量以便代码编译，然后继续。

密钥类型必须与集成匹配：服务器端 SDK 需要一个 **SDK 密钥**，浏览器/客户端端需要一个 **客户端 ID**，移动端需要一个 **移动密钥**。环境变量名称和捆绑器规则位于 [应用代码更改](sdk-install/apply/SKILL.md)。

直到初始化验证完成才继续。

---

## 步骤 4：第一个标志

创建标志，将其连接到应用，并让用户观看它打开。

- **创建标志。** 如果 MCP 连接，调用 `create-flag`（在重复键冲突时，调用 `get-flag` 并采用现有标志；不要 `list-flags` 首先）。如果 MCP 没有连接，给他们一个打开创建表单的仪表板链接，并预填密钥：`https://app.launchdarkly.com/projects/{projectKey}/flags/new?key={flagKey}`
- **添加一个标志门控横幅。** 在应用的主页顶部插入一个小而干净的横幅，门控在标志上。关闭状态：一个中性的横幅阅读"LaunchDarkly 测试横幅（标志关闭）"，并带有查看 LaunchDarkly 中标志的链接。开启状态：横幅切换到明显不同的外观（例如绿色背景）阅读"LaunchDarkly 测试横幅（标志开启）"。将其样式设置为看起来有意，而不是调试输出。添加到现有应用，不要重写它。对于一个没有渲染页面的应用，添加一个与标志一起变化的等效可见输出（一个端点或启动行）。
- **在空闲端口上启动开发服务器**（首先检查 `lsof -ti :3000,4000,5173`）。**在用户看到标志打开之前保持运行。不要在那时停止服务器。**
- **将揭示交给用户。** 给他们本地 URL 和一个选择来打开它：

```json
{
  "questions": [
    {
      "id": "flip_method",
      "prompt": "你的应用正在运行在 <url>，并且标记的元素是关闭的。打开标志以查看它变化。你想如何翻转它？",
      "options": [
        { "id": "ld_ui", "label": "我将在 LaunchDarkly 中翻转它" },
        { "id": "agent", "label": "为我翻转" }
      ]
    }
  ]
}
```

- 如果 **我将在 LaunchDarkly 中翻转它**：给他们标志的直接链接并等待。`https://app.launchdarkly.com/projects/{projectKey}/flags/{flagKey}/targeting?env={envKey}`
- 如果 **为我翻转**：通过 MCP 或 REST API（ whichever is configured）翻转它。如果两者都没有配置，则回退到仪表板链接。
- 只有在 MCP 或 API 令牌实际配置时才提供 **为我翻转**。否则只显示 LaunchDarkly 选项。

不要在聊天中打印页面或横幅文本。指向用户的浏览器：`<url>` 中的横幅与服务器一起运行时实时翻转。这就是标志在起作用。

### 总结

保持几行：
- 标志已激活。在 LaunchDarkly 中查看它：`https://app.launchdarkly.com/projects/{projectKey}/flags/{flagKey}/targeting?env={envKey}`
- 没有提交。你的更改在 `launchdarkly-onboarding` 分支上，所以你可以根据自己的喜好审查、保留或丢弃它们。
- 一个选择关于下一步是什么：

```json
{
  "questions": [
    {
      "id": "explore_next",
      "prompt": "想探索更多 LaunchDarkly 的功能吗？",
      "options": [
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

如果用户要求跳过步骤或在流程中中途跳转，你的第一个回复总是按顺序做三件事，然后才写代码或跳转：
1. 用他们的话承认他们要求什么。
2. 用一句话命名跳过的具体后果。具体会出什么问题（例如："标志调用直到 SDK 安装才会运行"）。陈述真正的失败，而不是模糊的暗示。
3. 提供选择：先完成快速步骤，还是按他们的方式继续。

> "我听到你，你想现在得到标志代码。没有 SDK 安装，那些调用不会运行。设置大约需要两分钟。你想让我先完成它，还是直接给你代码来连接？"

永远不要无声地抛出代码而没有权衡，也永远不要僵化地拒绝。如果他们坚持，尊重它，记录跳过了什么，用一句话重申风险，然后继续前进。

---

## 技能存储库

| 存储库 | 技能 | 目的 |
|---|---|---|
| `launchdarkly/ai-tooling` | `onboarding`、`sdk-install`、`mcp-configure` | 设置 |
| `launchdarkly/ai-tooling` | `launchdarkly-flag-create` 和相关 | 标志管理 |

---

## 边缘情况

- **SDK 已安装**：跳过步骤 3。用一行说你在哪里发现了什么，然后转到步骤 4。不要重新解释 SDK 或运行安装命令。
- **MCP 已配置**：使用它。跳过步骤 2 的提议。调用 `get-project` 存储密钥并继续。
- **已找到过时的 mcp/aiconfigs 或 mcp/fm**：两者都已过时。在迁移到统一的 `mcp/launchdarkly` 服务器之前询问。不要自动迁移。
- **未检测到支持的代理**：直接询问。如果需要，提供手动配置。
- **npx 不可用**：提供手动技能安装（克隆存储库，复制技能目录）。
- **用户只想部分设置**：尊重它。说明缺失什么以及限制。
- **非 LaunchDarkly 依赖项必须更改**（依赖项升级、锁文件变化）才能安装或编译 SDK：首先获取明确批准，按照 [应用代码更改](sdk-install/apply/SKILL.md)。

## 参考

- [mcp-configure](mcp-configure/SKILL.md) 和 [MCP 配置模板](mcp-configure/references/mcp-config-templates.md) — 步骤 2
- [sdk-install](sdk-install/SKILL.md) — 步骤 3（检测、计划、应用）
- [SDK 配方](references/sdk/recipes.md) 和 [SDK 片段](references/sdk/snippets/) — 每个SDK 安装和初始化的详细信息
