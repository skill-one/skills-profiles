# 创建新的 Salesforce 项目

引导用户通过向导来构建新的 Salesforce DX 项目，将此会话迁移到新项目中，连接到组织，并为其配置开发环境。按顺序运行每个步骤，并在执行任何会话更改操作之前确认用户的操作。

`salesforce-development` 插件的 MCP 服务器（`salesforce-api-context`、`salesforce-metadata-experts`、`salesforce-lsp`）由**已安装的插件**提供，而不是由项目提供——因此，一旦会话迁移到新项目，它们将自动在新项目中保持可用。没有每个项目的 `.mcp.json` 文件需要复制。

## 第 1 步：选择项目模板

此技能构建 CLI 提供的**所有**模板，包括 React/Angular UI-bundle 应用程序——创建项目是一项核心功能，不应要求单独安装插件来选择模板。（一旦项目存在，`experience-ui-bundle-*` 技能将负责构建它——页面、组件、样式、部署——但初始构建在这里进行，无论是否安装了该插件。）

从 CLI **实时读取**模板集——永远不要硬编码它，因为 Salesforce 会随着时间的推移添加模板，嵌入的列表会过时：

```bash
sf template generate project --help
```

解析 `-t, --template=<option>` 行的 `<options: a|b|c|…>` 列表——这些用管道分隔的名称是权威的模板集。截至撰写本文时，CLI 提供八个模板，都在这里构建：`standard`、`empty`、`analytics`、`agent`，以及 UI-bundle 集合 `reactinternalapp`、`reactexternalapp`、`angularinternalapp`、`angularexternalapp`（React/Angular × 内部/外部受众）。将实时解析视为权威来源；这里的列表仅在解析失败时作为后备选项。

**意图快捷方式优先。** 仅当请求完全解析为**恰好一个模板**时，才使用快捷方式。任何带有缺失选项的内容都将进入选择器，以便它可以询问——永远不要猜测。当请求直接解析 `{template}` 时：

- 请求**命名非 UI 模板**："empty/minimal project" → `empty`；"analytics project" → `analytics`；"agent project" → `agent`；"standard project" → `standard`。
- 请求是具有**框架和受众都明确的 UI-bundle 应用程序** → 匹配的 UI 模板（例如 "internal React app" → `reactinternalapp`，"customer-facing Angular portal" → `angularexternalapp`）。内部 = 员工端/已认证；外部 = 客户/合作伙伴端，带有登录流程。

**应用程序的描述不是模板名称。** "为我构建一个个人待办事项应用程序"、"一个库存跟踪器"、"一个用于我团队的 CRM" 描述要构建的内容，而不是要选择的模板——它们**不**解析为模板，因此**不**符合快捷方式的条件。不要根据应用程序的用途推断 `standard`（或任何模板），无论它看起来多么明显：`standard` 是选择器的默认值，这并不允许跳过选择器。当用户没有命名模板或框架时，**你必须显示选择器并让他们选择**——默默假设模板是此步骤存在的目的，以防止这种情况发生。

其他所有内容都将进入选择器，包括：
- 一个**不带模板名称的新项目** / "创建一个 Salesforce 项目"（选择器默认为 **Standard**），
- 一个**描述的应用程序**，没有模板或框架命名（"a todo app"，"an inventory tracker"）——显示选择器；永远不要假设应用程序的用途映射到模板，
- 一个**部分指定的 UI 应用程序**——例如，"创建一个 React 应用程序"而没有受众。永远不要假设受众。当框架已知但受众未知时，跳过顶级选择器，直接进入下面的框架/受众后续步骤以收集缺失的部分。

**否则，询问一个 `AskUserQuestion`——"你想创建什么类型的项目？"**（单选，四个选项）。`AskUserQuestion` 最多四个选项，因此选择器会显示四个最常请求的类型；**`empty` 是故意从选择器中省略的**，只能通过上述 "empty/minimal project" 快捷方式访问。这是有意为之——`empty` 是很少选择的空项目模板，在四个稀缺插槽中花费一个会挤占常见选择。想要它的用户会直接命名它，快捷方式会直接解析它。

- **Standard** → `standard`（默认）——通用 `force-app` 元数据项目（Apex、LWC、对象、流程）。
- **Agentforce agent** → `agent`——附带一个示例 Local Info Agent。
- **CRM Analytics** → `analytics`（Tableau CRM）——添加 `waveTemplates` 目录。
- **React / Angular UI 应用程序** → 一个 UI-bundle 启动器。这需要一个框架 + 受众，因此询问**一个后续的 `AskUserQuestion`**（"选择 UI 框架和受众？"，四个选项），它直接映射到 `{template}`：
  - **React — 内部** → `reactinternalapp` · **React — 外部** → `reactexternalapp`
  - **Angular — 内部** → `angularinternalapp` · **Angular — 外部** → `angularexternalapp`
  - 内部 = 员工端/已认证；外部 = 客户/合作伙伴端，带有登录、注册和配置文件。

解析的模板是 `{template}`，它将输入第 3 步。如果实时 CLI 添加了新模板，请在此处添加它（或者，如果它是另一个很少选择的模板，则将其作为意图快捷方式关键字连接，而不是第五个选择器插槽）。

## 第 2 步：选择项目名称

提示用户输入项目名称。它将成为新的目录名称**并将其插值到下面的 shell 命令中**，因此在使用它之前**必须严格验证**——永远不要通过原始名称传递。

**先允许，然后拒绝并重新提示。** 仅接受符合 `^[A-Za-z0-9][A-Za-z0-9_-]*$` 的名称——字母、数字、`_` 和 `-`，以字母或数字开头。任何其他内容（空格、路径分隔符（如 `/`）、开头为 `.` 或 `..`，或 shell 保留字符，如 `; | & $ > < ( ) \` " '`）都是无效的：解释原因并再次询问。像 `proj;rm -rf ~` 这样的名称永远不能达到命令。作为纵深防御，下面的命令也引用了 `"{name}"`——但验证才是真正的保护，引用只是后备。

## 第 3 步：生成项目

**在生成之前验证**——不要运行命令，直到你可以检查以下内容：

- ☐ 即将被插值的 `{name}` 是通过第 2 步允许列表的**确切值**（`^[A-Za-z0-9][A-Za-z0-9_-]*$`）——不是原始的、重新编辑的或用户回显的字符串。如果它从未通过验证，请返回第 2 步。
- ☐ `{template}` 是第 1 步中 CLI 广告的选项之一。
- ☐ 当前工作目录中**不存在** `{name}/` 目录——如果存在，生成将失败（或风险覆盖现有项目）。首先使用 `[ -e "{name}" ]` 检查；如果存在，则不要覆盖：告诉用户并返回第 2 步以使用不同的名称。

在当前工作目录中运行：

```bash
sf template generate project -t {template} -n "{name}"
```

这将创建一个新 `{name}/` 目录在当前工作目录下。（`sf project generate` 是此命令的已弃用别名——优先使用 `template generate project`。）不需要扁平化步骤——与生成到现有目录的流程不同，这会创建一个新鲜的 `{name}/`，其 `sfdx-project.json` 已经位于会话将迁移到的根目录。

**UI-bundle 模板带有 npm 依赖项——但不要为用户安装它们。** React/Angular 启动器在 npm 依赖项存在之前无法运行（预览/构建/检查失败），并且有**多个** `package.json` 文件——项目根目录和每个 UI bundle——每个都需要自己的安装。首次运行安装是重量的（多分钟），通过延迟明显，因此这是开发者应该明确做出的决定——不要未经询问就运行它。**不要**自己运行 `npm install`。相反，当 `{template}` 是 UI-bundle 时（`react*`/`angular*`），在结束消息中告诉用户依赖项尚未安装，并在他们准备好时提供要运行的命令（见 UI-bundle 指针在结束消息中）。

## 第 4 步：将会话迁移到新项目

现代 Claude Code（v2.1.169+）可以将当前会话直接迁移到新目录中——无需新终端，无需重新启动，对话历史记录保留。告诉用户运行：

```text
/cd {name}
```

这将迁移会话：新目录的 `CLAUDE.md` 被加载，项目存储移动到那里（因此 `--resume`/`--continue` 可以找到它），cwd 成为项目根目录，因此所有剩余的 `sf` 命令作为 `sf ...` 运行，没有任何路径前缀。

`/cd` 是客户端移动：它不会触发任何挂钩，也不会给你任何回合，因此会话在用户运行它后**立即**变得**安静**——这是预期的，而不是挂起。但这也意味着你在其中传递 `/cd` 的消息是你最后一次发言，直到他们再次说话，所以该消息必须以告诉他们如何继续的**可供性**结束。用类似下面的行关闭它：

> 进入后，只需说 **"下一步是什么"**（或 "连接一个组织"），我会从那里继续。

说 "下一步是什么" 会重新激活此会话并绘制旅程提示，该提示指向下一步（验证组织）。永远不要暗示 `/cd` 后会话会自行连接组织或继续——它将保持安静，直到用户重新激活。

当他们重新激活时，用一句话确认移动（例如 "你现在在 {name} 中。"），然后继续第 5 步。**不要**运行 `sf-context detect` 或 `check-tools` 来“显示”横幅——`detect` 作为工具打印原始 JSON，插件已经自行显示横幅（每个会话一次；在定向问题的回答时显示旅程提示）。只需确认移动，然后继续。健康状况可以通过 `/salesforce-development:setup` 按需获取。

**对于较旧版本的 Claude Code（在 v2.1.169 之前）：** `/cd` 报告 `Unknown command`。在这种情况下，用户必须在新目录中重新启动：

```bash
cd "{name}" && claude
```

`salesforce-development` 插件是全局安装的（通过市场），因此在新目录中的新会话会自动加载它并触发 SessionStart——横幅和健康检查会自行出现，无需手动 `sf-context` 调用。下面的剩余步骤然后从项目内部运行。

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

如果此操作因提及源跟踪不支持或未启用而失败，请提供启用它的选项：

```bash
sf org enable tracking --target-org {alias}
```

在运行启用命令之前确认用户的操作。

## 结束消息

一旦所有步骤完成，告诉用户：

```text
您的项目已准备好！以下是已设置的内容：

  ✅ 项目生成：{name}/
  ✅ 会话迁移到 {name}/（通过 /cd）
  ✅ 默认组织：{alias}
  ✅ 源跟踪：已启用（或状态）

您已经在新项目中工作——此会话使用 /cd 移动到这里，所以只需继续。随时运行 /salesforce-development:setup 重新检查您的开发环境。
```

如果用户选择了旧版本的后备方案（使用 `cd {name} && claude` 而不是 `/cd` 重新启动），他们现在处于项目中的新会话中，SessionStart 横幅已经引导他们完成了环境设置——指向 `/salesforce-development:setup` 重新检查工具。

对于**UI-bundle**项目，构建已完成，但其 npm 依赖项**尚未安装**——这是开发者的决定，不是此技能运行的（首次运行安装是重量的，多分钟）。告诉用户他们的应用程序需要其依赖项才能预览/构建/检查，并在他们准备好时提供要从项目内部运行的命令：

```bash
npm install                                        # 项目根目录
for b in force-app/main/default/uiBundles/*/; do   # 每个 UI bundle
  [ -f "$b/package.json" ] && ( cd "$b" && npm install )
done
```

然后添加一行指向后续的开发技能。**使指针特定于框架**，因为前端构建技能仅限 React：

- **React**（`react*` 模板）→ `experience-ui-bundle-frontend-generate` 构建页面/组件（它是 React/TypeScript 特定的——shadcn/ui，react-router，`appLayout.tsx`/`routes.tsx`），并且 `experience-ui-bundle-deploy` 发送应用程序。
- **Angular**（`angular*` 模板）→ 没有 Angular 前端技能，因此**不要**指向 `experience-ui-bundle-frontend-generate`：它的先决条件需要 React `appLayout.tsx`/`routes.tsx`/`src/components/ui/`，并且会拒绝 Angular bundle。从 Angular 起始器的 `README`/工具链构建它；`experience-ui-bundle-deploy` 仍然发送它（部署与框架无关）。

无论如何，这些技能都存在于 `experience-react`/`experience-lwc` 插件中；如果用户没有它们，那是用于构建应用程序，而不是构建的——他们现在拥有的项目可以按原样部署。

## 规则

- 按顺序运行步骤；在登录、设置默认值、启用跟踪等任何会话更改操作之前确认。
- 插件的 MCP 服务器来自已安装的插件，而不是项目——不要在新项目中创建或复制 `.mcp.json`（插件的配置使用 `${CLAUDE_PLUGIN_ROOT}`，这在项目级文件中无法解析）。
- 优先使用 `/cd {name}` 将会话原位迁移（Claude Code v2.1.169+）——技能不能代表用户迁移会话，因此指示用户运行它。仅在 `/cd` 在较旧版本上报告 `Unknown command` 时才回退到 `cd {name} && claude`（重新启动）。
- 传递 `/cd {name}` 的消息是直到用户再次说话前的最后一次发言，因此它必须以指示如何继续的**可供性**结束——例如 '进入后，只需说 "下一步是什么".' 永远不要承诺 `/cd` 后会话将自行连接组织或继续；它将保持安静，直到用户重新激活。
- 在 `/cd` 后，**不要**运行 `sf-context detect` 或 `check-tools` 来“显示”横幅——`detect` 作为工具打印原始 JSON，插件已经自行显示横幅（每个会话一次；在定向问题的回答时显示旅程提示）。只需确认移动，然后继续。健康状况可以通过 `/salesforce-development:setup` 按需获取。
- 对于沙盒登录，`--instance-url https://test.salesforce.com` 是必需的（CLI 默认指向生产环境）。
- **永远不要**存储或显示访问令牌。
- 项目名称是用户输入，它将流入 shell 命令。在将其用于任何命令之前，验证它是否符合 `^[A-Za-z0-9][A-Za-z0-9_-]*$`，并在任何其他内容上拒绝并重新提示，然后在每个命令中引用 `"{name}"`（包括 `cd {name} && claude` 的回退）。像 `proj;rm -rf ~` 这样的名称永远不能原始插值——验证是保护，引用是后备。
- 对于只需要验证工具的**现有项目**，使用 `platform-environment-validate`（或 `/salesforce-development:setup`）；对于现有项目上的组织验证，使用 `/salesforce-development:login`。
- 此技能拥有**全新项目创建**，适用于每个模板，包括 React/Angular——一个从零开始的“创建新项目”请求，端到端设置（构建、迁移、连接组织、启用跟踪）。不要将初始构建移交给另一个插件。在此处构建——但永远不要为用户运行 `npm install`；安装 UI bundle 的依赖项是开发者的明确调用（在结束消息中提供要运行的命令）。然后指向 `experience-ui-bundle-*` 技能以*构建和部署*UI 应用程序。唯一的边界：当 UI-bundle 构建只是一个**构建 UI-bundle 应用程序的组合步骤**（由 `experience-ui-bundle-app-coordinate` 驱动，不需要完整的项目设置）时，那是 `experience-ui-bundle-project-generate` 的工作，不是我们的——这两个技能的描述包含互惠的“不要触发”。构建/编辑现有的 UI-bundle 应用程序总是他们的；全新项目创建是我们的。
