---
name: dx-project-create
description: 为任何模板（标准、空、分析、代理或 React/Angular UI-bundle 应用）搭建一个新的 Salesforce DX 项目，并端到端配置：迁移会话、连接组织、设置默认值、启用源跟踪。当用户要求创建或搭建新的 Salesforce/SFDX 项目、启动新的 React/Angular Salesforce 应用，或运行 'sf template generate project' 时使用。**禁止触发**以下场景：构建/编辑/样式化现有的 UI-bundle 应用（experience-ui-bundle-frontend-generate）；仅作为构建步骤搭建 UI bundle（experience-ui-bundle-project-generate, experience-ui-bundle-app-coordinate）；工具验证（platform-environment-validate）；组织认证（login）；项目统计；沙盒组织（dx-org-manage）。
---

# 创建新的 Salesforce 项目

引导用户通过向导来构建新的 Salesforce DX 项目，将此会话移动到新项目中，连接到组织，并为其配置开发环境。按顺序运行每个步骤，并在任何更改环境的行为之前确认用户。

`salesforce-development` 插件的 MCP 服务器（`salesforce-api-context`、`salesforce-metadata-experts`、`salesforce-lsp`）由**已安装的插件**提供，而不是由项目提供——因此，一旦会话重新定位，它们就会自动在新项目中保持可用。没有每个项目的 `.mcp.json` 文件需要复制。

## 第 1 步：选择项目模板

此技能构建 CLI 提供的**所有**模板，包括 React/Angular UI-bundle 应用程序——创建项目是一项核心功能，不应要求单独安装插件来选择模板。（一旦项目存在，`experience-ui-bundle-*` 技能将*构建它*——页面、组件、样式、部署——但初始构建在这里发生，无论该插件是否已安装。）

从 CLI **实时读取**模板集——永远不要硬编码它，因为 Salesforce 会随着时间的推移添加模板，嵌入的列表会过时：

```bash
sf template generate project --help
```

解析 `-t, --template=<option>` 行的 `<options: a|b|c|…>` 列表——这些用管道分隔的名称是权威的模板集。截至撰写 CLI 提供八个，都在这里构建：`standard`、`empty`、`analytics`、`agent`，以及 UI-bundle 集合 `reactinternalapp`、`reactexternalapp`、`angularinternalapp`、`angularexternalapp`（React/Angular × 内部/外部受众）。将实时解析视为权威来源；这里的列表只是一个解析失败时的回退。

**意图快捷方式优先。** 仅当请求完全解析为**恰好一个模板**时，才使用快捷方式。任何缺失选项的内容都会进入选择器，以便它可以询问——永远不要猜测。当请求直接解析 `{template}` 时：

- 请求**命名非 UI 模板**："empty/minimal project" → `empty`；"analytics project" → `analytics`；"agent project" → `agent`；"standard project" → `standard`。
- 请求是具有**框架和受众都明确的 UI-bundle 应用程序** → 匹配的 UI 模板（例如，"internal React app" → `reactinternalapp`，"customer-facing Angular portal" → `angularexternalapp`）。内部 = 员工端/已认证；外部 = 客户/合作伙伴端，带有登录流程。

**应用程序的描述不是模板名称。** "为我构建一个个人待办事项应用程序"、"一个库存跟踪器"、"一个用于我团队的 CRM"描述要构建的内容，而不是要选择的模板——它们**不**解析为模板，因此**不**符合快捷方式的条件。不要根据应用程序的用途推断 `standard`（或任何模板），无论它看起来多么明显：`standard` 作为选择器的默认值并不允许跳过选择器。当用户没有命名模板或框架时，**你必须显示选择器并让他们选择**——默默假设模板是此步骤存在的目的，以防止这种情况发生。

其他所有内容都会进入选择器，包括：
- 一个**不带模板命名的简单 "new project" / "create a Salesforce project"**（选择器默认为 **Standard**），
- 一个**描述的应用程序**，没有命名模板或框架（"a todo app"、"an inventory tracker"）——显示选择器；永远不要假设应用程序的用途映射到模板，
- 一个**部分指定的 UI 应用程序**——例如，"create a React app" 没有受众。永远不要假设受众。当框架已知但受众未知时，跳过顶级选择器，直接进入下面的框架/受众后续步骤以收集缺失的部分。

**否则问一个 `AskUserQuestion`——"你想创建什么类型的项目？"**（单选，四个选项）。`AskUserQuestion` 最多四个选项，因此选择器会显示最常见的四种类型；**`empty` 是故意从选择器中省略的**，只能通过上述意图快捷方式（"empty/minimal project"）访问。这是有意为之的——`empty` 是很少选择的空项目模板，如果在一个稀缺的槽中花费一个槽位，会挤占一个常见的选择。想要它的用户会直接命名它，快捷方式会直接解析它。

- **Standard** → `standard`（默认）——通用 `force-app` 元数据项目（Apex、LWC、对象、流程）。
- **Agentforce agent** → `agent`——附带一个示例 Local Info Agent。
- **CRM Analytics** → `analytics`（Tableau CRM）——添加 `waveTemplates` 目录。
- **React / Angular UI 应用程序** → 一个 UI-bundle 启动器。这需要一个框架 + 受众，因此问**一个后续的 `AskUserQuestion`**（"Which UI framework and audience?"，四个选项），它直接映射到 `{template}`：
  - **React — internal** → `reactinternalapp` · **React — external** → `reactexternalapp`
  - **Angular — internal** → `angularinternalapp` · **Angular — external** → `angularexternalapp`
  - 内部 = 员工端/已认证；外部 = 客户/合作伙伴端，带有登录流程。

解析的模板是 `{template}`，它将输入第 3 步。如果实时 CLI 添加了新模板，请在此处添加它（或者，如果它是另一个很少选择的模板，将其作为意图快捷方式关键字连接，而不是第五个选择器槽位）。

## 第 2 步：选择项目名称

提示用户输入项目名称。它将成为新的目录名称**并在下面的 shell 命令中插值**，因此必须在任何命令使用它之前严格验证——永远不要通过原始名称传递。

**允许列表，然后拒绝并重新提示。** 只接受匹配 `^[A-Za-z0-9][A-Za-z0-9_-]*$` 的名称——字母、数字、`_` 和 `-`，以字母或数字开头。任何其他内容（空格、路径分隔符（如 `/`）、开头为 `.` 或 `..`，或 shell 保留字符，如 `; | & $ > < ( ) \` " '`）都是无效的：解释原因并再次询问。像 `proj;rm -rf ~` 这样的名称永远不应该达到命令。作为纵深防御，下面的命令也引用 `"{name}"`——但验证才是真正的保护，而不是引用。

## 第 3 步：生成项目

**生成前验证**——在运行命令之前，必须能够检查以下内容：

- ☐ 即将被插值的 `{name}` 是通过第 2 步允许列表的**确切值**（`^[A-Za-z0-9][A-Za-z0-9_-]*$`）——不是原始的、重新编辑的或用户回显的字符串。如果从未通过验证，请返回第 2 步。
- ☐ `{template}` 是第 1 步中 CLI 广告的选项之一。
- ☐ 当前工作目录中不存在 `{name}/` 目录——如果存在，生成会失败（或风险覆盖现有项目）。先用 `[ -e "{name}" ]` 检查；如果存在，不要覆盖：告诉用户并返回第 2 步以使用不同的名称。

在当前工作目录中运行：

```bash
sf template generate project -t {template} -n "{name}"
```

这将创建一个新 `{name}/` 目录在当前工作目录下。（`sf project generate` 是此命令的已弃用别名——优先使用 `template generate project`。）不需要扁平化步骤——与生成到现有目录的流程不同，这会创建一个全新的 `{name}/`，其 `sfdx-project.json` 已经位于会话将重新定位到的根目录。

**UI-bundle 模板带有 npm 依赖项——但不要为用户安装它们。** React/Angular 启动器在 npm 依赖项存在之前无法运行（预览/构建/检查失败），并且有**多个** `package.json` 文件——项目根目录和每个 UI bundle——每个都需要自己的安装。首次运行安装是重负载（多分钟），通过延迟明显，因此这是开发者应该明确做出的决定——不是这个技能未经询问就运行。不要自己运行 `npm install`。相反，当 `{template}` 是 UI-bundle 时（`react*`/`angular*`），在结束语告诉用户依赖项尚未安装，并让他们在准备好时运行命令（见 UI-bundle 指针在结束语中）。

## 第 4 步：将会话重新定位到新项目

现代 Claude Code（v2.1.169+）可以将当前会话直接移动到新目录中——无需新终端，无需重新启动，对话历史记录保留。告诉用户运行：

```text
/cd {name}
```

这将重新定位会话：新目录的 `CLAUDE.md` 被加载，项目存储移动到那里（因此 `--resume`/`--continue` 找到它），cwd 成为项目根目录，因此所有剩余的 `sf` 命令作为 `sf ...` 运行，没有任何路径前缀。

`/cd` 是客户端移动：它不会触发挂钩，也不会给你任何回合，因此会话在运行它时**立即安静**——这是预期的，不是挂起。但这也意味着你在其中传递 `/cd` 的消息是你最后的话，直到他们再次说话，所以那条消息必须以告诉他们如何继续的 affordance 结尾。用类似下面的行关闭它：

> 进入后，只需说 **"what's next"**（或 "connect an org"），我会从那里继续。

说 "what's next" 会重新激活此会话并绘制旅程 nudge，它指向下一步（验证组织）。永远不要暗示 `/cd` 后会话会自行继续——它不会。

当他们重新激活时，用一句话确认移动（例如，"你现在在 {name} 中。"），然后继续第 5 步。不要运行 `sf-context detect` 或 `check-tools` 来“重新显示”横幅：`detect` 作为工具调用会打印原始挂钩 JSON（不是渲染的横幅），并且插件已经自行显示横幅——它在每个会话中显示 HEADLESS 身份一次（在用户第一次 Salesforce 询问时、会话开始时或在他们第一次定向问题时），并在他们问 "where am I" / "what's next" 时绘制旅程 nudge。开发环境健康检查可以通过 `/salesforce-development:setup` 按需获取。

**对于较旧版本的 Claude Code（v2.1.169 之前）：** `/cd` 报告 `Unknown command`。在这种情况下，用户必须在新目录中重新启动：

```bash
cd "{name}" && claude
```

`salesforce-development` 插件是全局安装的（通过市场），因此在新目录中的新会话会自动加载它并触发 SessionStart——横幅和健康检查会自行显示，无需手动 `sf-context` 调用。下面的剩余步骤然后从项目内部运行。

## 第 5 步：验证到组织

验证此项目将要部署到的组织：

```bash
sf org login web --alias {alias}
```

- 提示用户输入 `--alias`，以便后续步骤可以通过名称引用组织。
- 对于**沙盒**，添加 `--instance-url https://test.salesforce.com`。
- 对于**生产环境**，省略 `--instance-url`（默认为 login.salesforce.com）。

如果用户已经验证了组织，请跳过登录，只需收集现有的别名。

## 第 6 步：设置为默认组织

将新验证的组织设置为项目的默认目标：

```bash
sf config set target-org {alias}
```

## 第 7 步：确保源跟踪已启用

使用部署预览（最轻量级的只读源跟踪探测）检查是否针对组织工作源跟踪：

```bash
sf project deploy preview --target-org {alias} --json
```

如果此操作失败并出现提及源跟踪不受支持或未启用的错误，请提供启用它的选项：

```bash
sf org enable tracking --target-org {alias}
```

在运行启用命令之前确认用户。

## 结束消息

一旦所有步骤完成，告诉用户：

```text
您的项目已准备好！以下是已设置的内容：

  ✅ 项目生成：{name}/
  ✅ 会话重新定位到 {name}/（通过 /cd）
  ✅ 默认组织：{alias}
  ✅ 源跟踪：启用（或状态）

您已经在新项目中工作——这个会话通过 /cd 移动到这里，所以只需继续。随时运行 /salesforce-development:setup 重新检查您的开发环境。
```

如果用户选择了旧版本回退（使用 `cd {name} && claude` 而不是 `/cd`），他们现在处于项目中的新会话，SessionStart 横幅已经引导他们完成了环境——指向 `/salesforce-development:setup` 重新检查工具。

对于**UI-bundle**项目，构建已完成，但其 npm 依赖项**尚未安装**——这是开发者的决定，不是这个技能运行（首次运行安装是重负载、多分钟的步骤）。告诉用户他们的应用程序需要其依赖项才能预览/构建/检查，并让他们在准备好时从项目内部运行命令：

```bash
npm install                                        # 项目根目录
for b in force-app/main/default/uiBundles/*/; do   # 每个 UI bundle
  [ -f "$b/package.json" ] && ( cd "$b" && npm install )
done
```

然后添加一行指向后续开发技能。**使指针特定于框架**，因为前端构建技能仅限 React：

- **React**（`react*` 模板）→ `experience-ui-bundle-frontend-generate` 构建页面/组件（它是 React/TypeScript 特定的——shadcn/ui、react-router、`appLayout.tsx`/`routes.tsx`/`src/components/ui/`），并且 `experience-ui-bundle-deploy` 发送应用程序。
- **Angular**（`angular*` 模板）→ 没有 Angular 前端技能，因此**不要**指向 `experience-ui-bundle-frontend-generate`：它的先决条件需要一个 React `appLayout.tsx`/`routes.tsx`/`src/components/ui/`，并且会拒绝 Angular bundle。从 Angular 启动器的 `README`/工具链构建它；`experience-ui-bundle-deploy` 仍然发送它（部署与框架无关）。

无论如何，这些技能都存在于 `experience-react`/`experience-lwc` 插件中；如果用户没有它们，那是用于构建应用程序，而不是构建框架——他们现在拥有的项目是完整且可部署的。

## 规则

- 按顺序执行步骤；在执行任何会改变环境的操作（登录、设置默认值、启用跟踪）之前进行确认。
- 插件的 MCP 服务器来自已安装的插件，而不是项目 — 请不要在新项目中创建或复制一个 `.mcp.json` 文件（插件的配置使用 `${CLAUDE_PLUGIN_ROOT}`，这在项目级别的文件中无法解析）。
- 优先使用 `/cd {name}` 在原地重新定位会话（Claude Code v2.1.169+） — 技能无法代表用户重新定位会话，因此需要指导用户运行它。只有在 `/cd` 在较旧版本上报告 `Unknown command` 时，才回退到 `cd {name} && claude`（重新启动）。
- 向用户传达 `/cd {name}` 的消息是您在他们再次说话之前（`/cd` 不触发钩子），因此它必须以恢复操作提示结束 — 例如 '进入后，只需说 "下一步是什么".'。永远不要承诺 `/cd` 后会连接组织或自行继续；它保持静默，直到用户重新参与。
- 在 `/cd` 之后，请勿运行 `sf-context detect` 或 `check-tools` 来“显示”横幅 — `detect` 作为工具打印原始 JSON，并且插件本身会显示横幅（每会话一次；在方向问题的提示中）。只需用一行确认移动并继续。健康状态可通过 `/salesforce-development:setup` 按需获取。
- 对于沙盒登录，`--instance-url https://test.salesforce.com` 是必需的（CLI 默认指向生产环境）。
- 绝不存储或显示访问令牌。
- 项目名称是用户输入的，并流入 shell 命令。在使用它之前，请将其与 `^[A-Za-z0-9][A-Za-z0-9_-]*$` 进行验证，并在任何其他情况下拒绝并重新提示，然后在每个命令中引用 `"{name}"`（包括 `cd {name} && claude` 的回退）。像 `proj;rm -rf ~` 这样的名称绝不能直接插值 — 验证是守门人，引用是后备。
- 对于只需要验证工具的现有项目，请使用 `platform-environment-validate`（或 `/salesforce-development:setup`）；对于现有项目上的组织认证，请使用 `/salesforce-development:login`。
- 此技能拥有**绿色字段项目创建**的职责，适用于每个模板，包括 React/Angular — 从头开始的“创建新项目”请求，端到端设置（脚手架、重新定位、连接组织、启用跟踪）。请勿将初始脚手架交给另一个插件。在这里进行脚手架搭建 — 但永远不要为用户运行 `npm install`；安装 UI 包的依赖是开发人员的明确调用（在结束语中将命令交给他们）。然后引导用户使用 `experience-ui-bundle-*` 技能来 *构建和部署* UI 应用。唯一的界限：当 UI-bundle 脚手架只是构建 UI-bundle 应用的一个**组合步骤**（由 `experience-ui-bundle-app-coordinate` 驱动，不需要完整的项目设置）时，那是 `experience-ui-bundle-project-generate` 的工作，而不是我们的 — 两个技能的描述包含互斥的“不要触发”。构建/编辑现有的 UI-bundle 应用始终是它们的工作；绿色字段项目创建是我们的工作。
