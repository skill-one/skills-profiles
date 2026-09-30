---
name: magicpath
description: 通过 magicpath-ai 命令行界面（CLI）使用 MagicPath 来查找、预览、检查、安装、导出、创建和编辑 UI 组件，以及管理 MagicPath 技能。适用于 MagicPath 设计/组件；个人或团队项目；活动画布和选定的组件/图像/修订版本；主题/设计系统；团队、成员、所有权、归因、已安装组件审计以及分享/查看链接。在将精确的 MagicPath 组件或修订版本导出到本地文件夹/应用程序时使用；用 1:1 精度并明确请求的更改来替换、适配或翻译本地 UI；通过检查/添加来安装 React/TypeScript 组件；使用代码开始/提交来编写响应式交互式画布组件；从本地路径或 GitHub/GitLab/Bitbucket 仓库导入或重新创建 UI 到 MagicPath；或创建、检索、更新、导入、启用、禁用或删除 MagicPath 技能。在具有嵌入式浏览器的托管环境中，通过分享 URL 保持项目画布打开，以便进行可视化工作。
---

# MagicPath

一个通过 AI 构建、共享和安装 UI 组件的平台。组件作为源代码通过 `magicpath-ai` CLI 添加到用户的项目中。

MagicPath 画布组件也可以通过 `npx -y magicpath-ai code ...` 子命令直接从本地代码创建和编辑——参见 [从代码编辑或创建画布组件](#edit-or-create-canvas-components-from-code)。该路径是严格的：只有 `src/App.tsx`、`src/index.css`、`src/components/generated/` 下的文件以及在代码工作目录 `assets/` 下临时图像资源是可编辑的。

当此技能在具有嵌入式浏览器的代理主机中运行时，在适当的情况下，将 MagicPath 项目用作代理旁边的持久视觉画布。如果您为画布创作创建了项目，请在创建后立即在嵌入式浏览器中打开该项目，然后再执行 `code start`；参见 [使用嵌入式浏览器](references/working-with-embedded-browsers.md)。

> **术语：** 用户通常将 MagicPath 组件称为“设计”——这两个术语可以互换。当用户说“设计”、“我的设计”或“那个设计”时，将其视为指 MagicPath 组件。相应地进行搜索、检查和安装。
>
> 用户还将 MagicPath 设计系统称为“主题”。当用户说“主题”、“我的主题”或“使用 X 主题”时，他们指的是 MagicPath 设计系统——一组 CSS 变量、字体和样式说明。使用 `list-themes` 和 `get-theme` 来处理它们。
>
> 用户可能属于 **团队**（也称为“工作区”）。当用户说“团队的 设计”、“我们团队的组件”或提及团队名称（如“Acme Inc”）时，他们指的是该团队拥有的项目和组件。使用 `list-teams`、`--team` 和 `--personal` 标志在个人和工作区之间导航。
>
> 用户还可能询问他们在 MagicPath 中创建的 **技能**。这些是可重用的指令包，可以从 MagicPath 聊天中调用，并使用 `npx -y magicpath-ai skills ...` 进行管理。个人技能位于用户的工区；团队技能位于 MagicPath 团队中。公共 MagicPath 技能除非平台另有说明，否则是只读的。

## 第一步

运行 `npx -y magicpath-ai info -o json` 来检查认证状态和项目上下文。第一次调用可能需要几秒钟，因为 `npx` 下载了包；后续调用很快。

- 如果 `auth.authenticated` 为 false，运行 `npx -y magicpath-ai login`，等待浏览器认证完成，然后用 `npx -y magicpath-ai whoami -o json` 进行验证。

## 访客会话

如果用户给您一个 **配对码**（一个简短的代码，如 `gst_…`，通常是因为他们正在尝试没有账户的 MagicPath），连接一次：

```bash
npx -y magicpath-ai login --guest-code <code>
```

然后运行 `npx -y magicpath-ai whoami -o json`——它报告 `guest: true`、您可以使用的 `projectId` 以及 `canvasUrl`。使用正常的 `code start --project <projectId>` → `code submit` 流量在该项目上构建；每次提交都会在画布上实时显示。

访客会话仅限于该项目，并且会过期。在其范围内：

- 使用 `code start` / `code submit` 在项目上创建和编辑设计——这是会话的整个目的。
- 在具有嵌入式浏览器的代理主机中，打开 `canvasUrl`（来自 `whoami`），以便用户可以观看他们的画布在您旁边更新。`canvasUrl` 是打开访客画布的唯一方法——不要使用 `share` 或 `view`，这些需要完整的账户。
- 其他工作区功能（团队、附加项目、主题）属于完整账户。如果命令报告需要账户，请告诉用户从他们在浏览器中打开的画布上注册——这是将该项目保存到他们的账户并解锁其他一切的方法。（如果他们的会话已经过期，项目无法保存，他们会重新开始。）永远不要告诉访客在没有配对码的情况下运行 `login`。

## 与团队合作

用户可能属于拥有共享项目和主题的团队。默认情况下，`list-projects` 和 `search` 返回来自 **所有** 工作空间（个人 + 用户所属的每个团队）的结果。使用过滤标志来缩小范围。

### 发现团队

运行 `npx -y magicpath-ai list-teams -o json` 查看用户的团队：

```json
{ "teams": [{ "id": "123", "name": "Acme Inc", "role": "ADMIN" }] }
```

### 按团队过滤

- **默认（无标志）**：`list-projects`、`search` 包括个人和所有团队项目——无需额外标志即可进行广泛发现。
- **`--team "Acme Inc"` 或 `--team <teamId>`**：过滤到特定团队。适用于 `list-projects`、`search`、`list-themes` 和 `get-theme`。
- **`--personal`**：仅显示用户的个人项目/组件。适用于 `list-projects` 和 `search`。

### JSON 输出

项目和搜索结果包括 `ownerType`（`"personal"` 或 `"team"`）和 `ownerName`（用户邮箱或团队名称）。使用这些来告诉用户组件的位置。

### 发现人员

运行 `npx -y magicpath-ai list-members --team "Acme Inc" -o json` 查看团队中的成员：

```json
{ "team": { "id": "123", "name": "Acme Inc" }, "members": [{ "id": "456", "displayName": "Chloe Smith", "email": "chloe@acme.com", "role": "MEMBER" }] }
```

### 按人员过滤

- **`--created-by <userId>`** 在 `list-components` 上：过滤到特定用户创建或编辑的组件。在通过 `list-members` 解析出人员的用户 ID 后使用此功能。
- **`createdBy`** 字段在项目上：`list-projects` 中的每个项目都包括 `createdBy: { id, displayName }`，显示谁创建了它。
- **`lastEditedBy`** 字段在组件上：`list-components` 中的每个组件都包括 `lastEditedBy: { id, displayName }`，显示谁最后编辑了它。

**重要：** 您只能看到经过认证的用户可以访问的项目——您自己的个人项目以及您是成员的团队项目。您 **无法** 访问另一个用户的个人项目。在查找另一个人的工作时，仅搜索 **团队项目**（`--team`），而不是个人项目。个人项目属于其所有者，除非有人明确被邀请为成员。

### 常见模式

- **“Chloe 上次在做什么？”** → `list-members --team "Acme Inc" -o json` 找到 Chloe 的用户 ID → `list-projects --team "Acme Inc" -o json` 获取 **团队项目** → 对每个项目运行 `list-components <projectId> --created-by <chloeId> --sort-by createdAt --order desc -o json`。报告最新的组件。**不要搜索另一个用户的个人项目**——个人项目属于其所有者。
- **“显示团队的设计”** 或 **“Acme Inc 创建了什么？”** → `list-teams` 找到团队，然后 `list-projects --team "Acme Inc" -o json`，然后 `list-components <projectId> -o json`。
- **“显示团队最新的设计”** → 与上述相同，但在 `list-components` 上使用 `--sort-by createdAt --order desc --limit 1`。
- **“谁创建了此项目/组件？”** → 检查项目的 `createdBy` 字段或组件的 `lastEditedBy` 字段（从相应的列表命令获取）。
- **“我的设计”** 而未提及团队 → 默认（所有项目）通常是正确的。仅在用户明确希望排除团队项目时才使用 `--personal`。
- **“使用团队的主题”** → `list-themes --team "Acme Inc" -o json`，然后 `get-theme <name> --team "Acme Inc" -o json`。

## 管理 MagicPath 技能

当用户询问创建、列出、检查、更新、导入、删除、启用/禁用或本地安装存储在 MagicPath 中的技能时，使用此流程。对于所有返回数据的命令，请优先使用 JSON 模式：

```bash
npx -y magicpath-ai skills list -o json
npx -y magicpath-ai skills list --team "Acme Inc" -o json
npx -y magicpath-ai skills get <skillIdOrSlug> -o json
npx -y magicpath-ai skills create --name "Skill name" --description "When to use it" --instructions-file ./SKILL.md -o json
npx -y magicpath-ai skills import ./skill-package.skill -o json
npx -y magicpath-ai skills update <skillIdOrSlug> --disable -o json
npx -y magicpath-ai skills delete <skillIdOrSlug> -y -o json
```

### 范围和所有权

- 当用户说技能属于团队/工作区时，使用 `--team <nameOrId>`。
- 为个人技能省略 `--team`。
- `skills list` 默认包括公共 MagicPath 技能，因为这些技能在聊天中可供用户使用。当用户想要可以编辑的技能时，传递 `--owned-only`。
- 公共技能是只读的。除非命令输出明确表明它们是拥有的/可编辑的，否则不要尝试更新或删除公共技能。
- 导入的 `.zip` 或 `.skill` 包在 MagicPath 中内容不可变；它们仍然可以使用 `skills update <id> --enable/--disable` 启用或禁用。

### 创建或更新技能

- 对于超过简短的一行指令，将指令写入本地文件并使用 `--instructions-file`。这避免了 shell 引用问题并保留了 Markdown。
- MagicPath 技能需要一个非空的名称、描述和指令。描述应说明何时使用技能；指令应说明如何执行工作。
- 如果用户正在将观察到的工作流程转换为可重用的技能，请总结触发器、约束、步骤、示例以及未来代理应读取的任何文件或参考。

### 本地安装 MagicPath 技能

当用户希望将 MagicPath 中的技能安装到他们外部编码代理中时，首先检索它，然后将其重新创建为本地 Agent Skills 文件夹：

1. 运行 `npx -y magicpath-ai skills get <skillIdOrSlug> -o json`。
2. 创建一个以技能 slug 命名的文件夹。
3. 写入 `SKILL.md`，其中包含至少 `name` 和 `description` 的 frontmatter，然后是检索到的 `instructions`：

```markdown
---
name: example-skill
description: Use when ...
---

...instructions from MagicPath...
```

4. 如果技能有捆绑的包文件，运行 `npx -y magicpath-ai skills get <skillIdOrSlug> --files -o json`，然后使用 `--file <path>` 获取每个文件，并在本地技能文件夹中重建相同的相对路径。
5. 使用当前代理主机本地的技能工作流程安装或注册该文件夹。如果主机支持 Agent Skills CLI，使用该工具从本地文件夹安装；否则将文件夹放置在主机文档化的本地技能目录中。

在写入用户当前项目之外或写入全局代理配置目录之前询问。

## 工作流程

> **始终使用 `-o json`** 对于所有返回数据的命令（`search`、`list-projects`、`list-components`、`list-teams`、`list-themes`、`get-theme`、`skills`、`selection`、`active-project`、`info`、`add`、`inspect`、`code`）。这为您提供了结构化的输出，以便您可以使用它而不是人类可读的表格。

### 第一阶段：发现

1. **检查认证**——运行 `npx -y magicpath-ai whoami -o json` 以验证认证。
2. **检查当前选择**——如果用户引用“选定的组件”、“选定的图像”、“我选中的设计”或以其他方式指向一个 *特定的画布选择*，运行 `npx -y magicpath-ai selection -o json`。如果它返回组件，直接使用它们——跳过搜索/确认流程并继续使用返回的 `generatedName`(s)。每个返回的组件还包括 `selectedRevisionId`，该修订版当前在画布上显示为该组件。响应还可以包括选定的 `images`；当您随后运行 `code start` 时，这些选定的图像在 `assets/selected/**` 下可用，如下所述。当下游命令接受修订版（例如 `code context --revision`）时，传递此值，以便操作针对用户正在查看的版本，而不是数据库中碰巧 canonical 的版本。
3. **检查活动项目**——如果用户引用“我打开的项目”、“这个项目”、“我正在处理的工作”或以其他方式暗示工作项目上下文而未指定特定组件，运行 `npx -y magicpath-ai active-project -o json`。它返回用户当前在浏览器中打开的项目，即使没有选中。如果返回一个项目，将其视为工作项目并跳过项目选择器。如果返回多个，列出它们并询问哪个。如果返回空列表，用户没有打开画布——使用 `list-projects` 并询问用户。为用户所说选择正确的命令：`selection` 对于引用的组件，`active-project` 对于引用的项目，`list-projects` + 询问如果两者都不是。 (注意 `selection` 还在其输出中返回活动项目，因此当用户引用组件时，您已经获得了项目——无需单独的 `active-project` 调用。)
4. **查找组件**——使用 `npx -y magicpath-ai search <query> -o json` 在所有项目中搜索，或 `list-projects -o json` 然后 `list-components <projectId> -o json` 浏览。如果 `active-project` 已经给您一个项目，通过 `list-components <projectId> -o json` 而不是搜索每个工作区来缩小您的搜索范围。
5. **查看项目的图像**——要知道哪些独立的图像已经存在于项目的画布上（以引用它们、避免重复或向用户描述它们），运行 `npx -y magicpath-ai image list <projectId> -o json` 并下载每个 `url` 以查看它——您使用 `previewImageUrl` 的方式与组件相同。（这些是画布图像，与 `code` 流量中的 `assets/` 构建输入分开。）
   对于 **独立的栅格请求**——照片、插图、纹理或透明切割——使用 `npx -y magicpath-ai image generate --prompt "..." -o json` 而不是构建画布设计；传递 `--ref <path>` 以编辑或重式现有照片。使用 `image add` 将结果放置在画布上，或将其复制到代码会话的 `assets/` 文件夹中以在设计中使用它。参见 [image generate](references/cli-reference.md) 以获取标志。
6. **视觉上理解组件**——`search` 和 `list-components` 结果包括 `previewImageUrl` 字段。下载并分析这些图像，以了解每个组件的外观，然后再推荐它。预览图像是您自己的理解——除非用户明确要求在嵌入式项目画布上查看该设计，否则不要导航到单个设计预览。
7. **与用户确认（停止并等待）**——除非用户指定了确切的 `generatedName`，否则告诉用户您找到了什么（名称、`generatedName`、项目）并询问是否是正确的组件。当嵌入式项目画布处于活动状态时，保持它在项目上，并且仅在用户明确要求时才打开或共享单个设计。在没有嵌入式项目画布的情况下，使用 `npx -y magicpath-ai view <generatedName>` 作为正常的确认回退。如果有多个匹配项，列出所有匹配项并询问哪个。**这是一个停止点——在此结束您的响应并等待用户回复。直到用户明确确认之前，不要继续。** 不要运行 `add` 或 `inspect`。

### 第二阶段：理解目标上下文

> **这一阶段至关重要。** 在安装任何内容之前，您必须了解组件将去哪里以及它在那里需要做什么。跳过这一点会导致看起来正确但行为不正确的组件。
>
> **将设计从 MagicPath 中导出：** 在导出到文件夹、安装到应用程序、替换本地 UI 或翻译到另一个框架之前，阅读并遵循 [在本地代码中使用 MagicPath 设计](references/using-magicpath-designs-in-local-code.md)。它定义了如何锁定确切的修订版、在适应之前建立 1:1 对等、保留本地行为、验证渲染结果，并限制差异为用户明确请求的更改。

7. **检查 MagicPath 组件源代码** — 使用 `npx -y magicpath-ai inspect <generatedName> -o json` 读取源代码。识别它渲染了什么，它期望哪些属性，以及它对布局（固定宽度、绝对定位等）做了哪些假设。
8. **阅读目标代码库上下文** — 在安装之前，阅读组件将要存放的文件。理解：
   - **现有功能**：如果替换组件，当前组件做什么？它处理哪些回调、状态、API 调用、导航、验证或副作用？必须保留或有意处理现有行为的每一部分。
   - **布局上下文**：父布局是什么？它是 flex/Grid 容器吗？响应式断点是什么？间距如何工作？如果组件在隔离状态下看起来完美，但如果其尺寸假设与布局不匹配，它可能会破坏布局。
   - **数据流**：周围代码提供了哪些属性、上下文或状态？它期望返回什么（回调、表单数据、事件）？
   - **设计系统**：项目使用哪些样式模式（Tailwind、CSS 模块、主题令牌）？MagicPath 组件的样式需要协调，而不是冲突。

### 应用主题（如果适用）

如果用户想要应用主题，或按名称引用品牌/设计系统：

1. **列出可用主题** — 运行 `npx -y magicpath-ai list-themes -o json` 查看所有主题。
2. **获取主题定义** — 运行 `npx -y magicpath-ai get-theme <id-or-name> -o json` 获取完整定义。
3. **读取 `prompt` 字段** — 如果存在，它包含设计师的自然语言样式指令（例如，“使用圆角，优先使用阴影而不是边框，使用品牌蓝色为 CTA”）。在调整组件时遵循这些指令。
4. **应用 CSS 变量** — 主题的 `light` 和 `dark` 对象将 CSS 变量名称映射到值（例如，`--background: #ffffff`，`--primary: #3b82f6`）。在调整 MagicPath 组件时，使用这些 CSS 变量而不是硬编码颜色：`bg-[var(--background)]`，`text-[var(--primary)]` 等。确保组件尊重 `defaultTheme`（亮色或暗色）。
5. **处理字体** — 如果主题包含 `fonts`，请确保项目加载这些字体（Google Fonts 链接或自定义字体的 `@font-face` 声明），并确保组件通过主题的字体 CSS 变量引用它们（例如，`font-family: var(--font-body)`）。
6. **非 React/JS 项目** — 主题数据是引用，不是样式表。将 CSS 变量转换为目标平台的等效项：SwiftUI `Color` 资产、Android 主题 XML、Python 模板上下文等。`prompt` 字段和颜色/字体值表示平台无关的设计意图——将它们映射到原生模式，而不是直接使用 CSS。

### 从代码创建或编辑画布组件

仅当用户想要直接编写 MagicPath 画布组件时使用此流程：

```bash
npx -y magicpath-ai code start --project <projectId> --dir . --name "Component Name" -o json
npx -y magicpath-ai code start --component <componentId> --dir . -o json
npx -y magicpath-ai code context <componentId> --dir . -o json  # 只读
npx -y magicpath-ai code submit --dir . --wait -o json
```

`code start` 是唯一开始有状态编码会话的命令。使用 `--project` 创建新组件，或使用 `--component` 编辑现有组件。它写入可编辑文件，在画布上创建或重用待处理的修订，并显示代理存在。

`code context` 是只读的。使用它来检查或导出现有组件的确切源修订；它不能用作提交路径。

仅编辑这些表面：`src/App.tsx`，`src/index.css`，`src/components/generated/**`，以及 `assets/**` 下临时图像资产。

`src/App.tsx` 预先配置为渲染生成的组件。仅编辑它以更改顶级主题值。

如果在运行 `code start` 时在画布上选择了图像形状，JSON 响应可能包括 `selectedImages`。CLI 下载这些短时效图像 URL 到 `assets/selected/**`。使用响应中的本地 `assetPath` 在 TSX/CSS 中，永远不要将临时 `accessUrl` 粘贴到组件源中，因为它会过期。

#### Tailwind v4 规则

MagicPath 模板使用 Tailwind v4。按以下方式样式化：

- `src/index.css` 必须包含 `@import 'tailwindcss';`，而不是 `@tailwind base;`，`@tailwind components;` 或 `@tailwind utilities;`。
- 主题令牌（`bg-background`，`text-foreground`，`border-border`，`bg-primary` 等）通过 `index.css` 中的 `@theme inline { ... }` 块连接。不要删除它。
- `:root` 和 `.dark` 块定义实际令牌值。不要删除它们。
- 要添加自定义实用类，将它们附加到 `index.css` 而不是替换现有内容。
- 没有 `tailwind.config.js`。配置通过 Tailwind v4 的 `@theme` 指令在 `index.css` 中。

### 第三阶段：安装和适配

9. **添加到项目** — 使用 `npx -y magicpath-ai add <generatedName> -y` 安装组件文件。在非交互式上下文中始终传递 `-y`。如果这是一个 **非 React 项目**（Swift、Python 等），**不要运行 `add**` — 使用 `npx -y magicpath-ai inspect <generatedName> -o json` 读取源代码作为参考，然后在目标语言和框架中重新创建组件。
10. **为生产使用适配组件** — MagicPath 组件是设计工件：它们捕获视觉意图和结构，但它们通常不是开箱即用的生产就绪。添加后，你必须编辑组件文件以：
    - **使其响应式**：用响应式实用工具替换任何硬编码的宽度和高度（例如，`w-[300px]`）（`w-full max-w-sm`，响应式断点如 `md:w-64 lg:w-80`）。设计可能只显示单个视口——你的工作是为所有视口使其工作。
    - **添加真实的交互性**：用实际属性、状态和事件处理程序替换静态/占位符内容。MagicPath 按钮上显示“提交”需要一个 `onClick` 属性和加载状态。表单需要验证和 `onSubmit`。
    - **连接数据流**：将组件连接到应用的实际数据——来自父级的属性、上下文提供者、API 调用、路由状态。不要保留模拟数据。
    - **保留现有功能**：当替换现有组件时，审核旧组件提供的每个功能（表单提交、错误处理、加载状态、可访问性、键盘导航、分析事件），并确保新组件处理所有这些功能。
    - **在不重新设计的情况下匹配项目的模式**：使用相同的状态管理和错误处理方法。仅当计算输出保留 MagicPath 设计时才重用样式抽象；不要用相似的本地令牌或原始值替换确切值。

### 第四阶段：集成到页面

11. **导入和渲染** — 使用 `add` 输出中的 `importStatement` 导入组件。传递你定义的属性。
12. **验证布局适配** — 放置组件后，检查父布局以确保它干净地集成。检查组件不会溢出、创建意外间隙或破坏页面的响应式流程。

## 设计到生产的思维

**MagicPath 是一个设计工具。** MagicPath 的组件代表某物应该看起来像什么以及如何结构化——它们是作为代码表达的设计规范。但设计稿和生产组件是不同的东西：

| 设计工件 | 你作为代理的工作 |
|---|---|
| 固定宽度 `w-[400px]` | 使其响应式：`w-full max-w-md` 或断点基于 |
| 静态文本 "John Doe" | 替换为动态属性：`{user.name}` |
| 占位符 `onClick={() => {}}` | 连接到真实处理程序：`onClick={handleSubmit}` |
| 硬编码的 3 个项目列表 | 遍历真实数据：`{items.map(…)}` |
| 没有错误/加载状态 | 添加加载旋转器、错误边界、空状态 |
| 没有可访问性属性 | 添加 `aria-label`，`role`，键盘处理程序，焦点管理 |
| 仅桌面布局 | 添加响应式断点，移动导航模式 |
| 装饰性图像 `src="/photo.jpg"` | 使用真实资产或项目的适当占位符 |

**黄金法则：MagicPath 组件告诉你什么要构建。你的工作是使其工作——响应式、可访问，并完全连接到应用程序。**

### 常见场景

**替换现有组件**（例如，用 MagicPath 设计交换旧登录表单）：
1. 彻底阅读旧组件——列出每个属性、回调、验证规则和副作用
2. 使用 `npx -y magicpath-ai inspect <generatedName> -o json` 检查 MagicPath 组件源代码
3. 使用 `npx -y magicpath-ai add <generatedName> -y` 安装 MagicPath 组件
4. 编辑 MagicPath 组件以接受所有相同的属性/回调
5. 确保旧组件的所有功能都存在于新组件中
6. 交换父级的导入——父级代码几乎不应改变

**从 MagicPath 设计库构建新页面**：
1. 使用 `list-components` 浏览项目的组件
2. 首先规划页面布局——确定哪些 MagicPath 组件映射到哪些部分
3. 使用 `npx -y magicpath-ai add <generatedName> -y` 逐个安装需要的组件
4. 构建页面布局，导入每个组件
5. 适配每个组件：响应式尺寸、真实数据、适当的路由、状态管理
6. 确保所有组件之间保持一致的间距、排版和颜色使用

**使用单个 MagicPath 组件作为灵感**：
1. 使用 `npx -y magicpath-ai inspect <generatedName> -o json` 检查源代码
2. 理解设计意图——颜色、间距、布局结构、排版
3. 安装并适配它，或使用它作为参考来构建遵循相同设计语言的定制内容

## 严格规则

- **`add` 表示安装以使用。** 仅当你打算导入和渲染安装的组件时才运行 `add`。如果你只是想读取源代码，请使用 `inspect` 而不是 `add`。
- **`add` 后，始终导入组件。** `add` 的整个目的是获取你然后导入的源文件。永远不要添加一个组件，然后将其样式/标记复制到另一个文件——直接导入并渲染组件。
- **MagicPath 组件是你拥有的源代码。** `add` 后，组件文件位于你的项目中的 `src/components/magicpath/<name>/`。你可以并且应该直接编辑它们以添加属性、更改行为、调整样式或与你的应用状态集成。
- **当组件需要集成时**：（1）`add` 组件，（2）编辑组件文件以接受你需要的属性（例如，`onSubmit`，`placeholder`，`className`），（3）从父级导入并传递这些属性。**不要**将组件的 JSX/样式复制到父级文件中。
- **永远不要直接放置组件。** 始终阅读周围代码，理解布局约束，并调整组件以适应。未经适配放置的 MagicPath 组件是错误，而不是功能。
- **`inspect` 是只读的。** 显示完整的源代码而不写入任何文件。在决定组件是否适合你的需求之前使用它，然后再提交。
- **`add` 仅适用于 React/TypeScript 项目。** `add` 命令将 `.tsx` 文件写入 `src/components/magicpath/` 并安装 npm 依赖项。仅在 JavaScript/TypeScript 项目中使用 `add`。对于非 JS 项目（Swift、Python 等），使用 `inspect` 读取组件源，然后将设计和行为转换为项目的语言和框架。
- **永远不要并行运行 `view` 命令。** `view` 命令为用户打开一个浏览器窗口。一次只打开一个目标。
- **在项目画布上保持嵌入式浏览器。** 除非用户明确要求，否则不要将其导航到单个设计预览；当这足够时，返回设计共享链接。
- **在创建新项目之前打开它。** 当嵌入式浏览器可用，并且请求包含在新建项目中工作时，在 `create-project` 返回 `id` 后立即显示项目画布，然后在 `code start` 或 `code submit` 之前开始。在出现工作内容时保持该项目画布可见；除非用户明确要求查看单独的设计，否则不要在提交后导航到生成的设计。

## 创建项目

**项目**是保存设计/组件的工作区。当用户明确要求创建项目（“创建一个名为……的新项目”，“为……创建一个项目”），或当他们要求新设计但当前没有项目上下文，而一个新项目是它的合适家园时，使用此功能。

### 选择工作区

创建之前，决定项目是 **个人** 还是属于 **团队**：

- 如果用户命名一个团队（“在 Acme Inc 中创建项目”），解析该团队并通过。
- 如果用户说“创建个人项目”或没有提及团队且没有团队，默认为个人。
- 如果用户不明确并且属于一个或多个团队，运行 `npx -y magicpath-ai list-teams -o json` 并询问哪个工作区——个人或团队之一。不要猜测。**停止并等待用户回复。**

### 运行命令

```bash
npx -y magicpath-ai create-project --name "My Stuff" -o json                       # 个人
npx -y magicpath-ai create-project --name "My Stuff" --team "Acme Inc" -o json     # 团队
```

- `--name` 是可选的。如果省略，项目将获得自动生成的占位符名称。当用户告诉你项目名称时，始终传递 `--name`。
- `--team` 接受团队名称或团队 ID。解析用户的意图为 `list-teams` 返回的团队之一。
- JSON 输出：`{ project: { id, name, ownerType, ownerName, ... } }`。`id` 是后续命令需要的。

### 项目存在后

如果用户还要求在新项目中创建设计，从响应中获取 `id` 并继续画布组件创建流程（`code start --project <id> --name "..."`，填写脚手架文件，`code submit --wait`）。不要重新创建项目每个设计——一个项目包含许多组件。

当任务包括在新建项目中创建或编辑设计时，将该项目视为画布。在嵌入式浏览器主机中，顺序是强制的：`create-project` 返回 `id` 后立即运行 `npx -y magicpath-ai share <projectId> -o json`，在返回的项目 URL 中打开嵌入式浏览器，然后才开始 `code start` 或 `code submit`。在出现工作内容时保持该项目画布可见；如果用户明确要求查看单独的设计，则不要在提交后导航到生成的设计。如果没有嵌入式浏览器，当需要用户面导航时，使用 `npx -y magicpath-ai view <projectId>`。

CLI身份验证和嵌入式浏览器身份验证是分开的。成功的`whoami`或`create-project`命令并不意味着可见的浏览器面板已登录到MagicPath。如果打开返回的`/files/<projectId>` URL重定向到主页或登录体验，请保持任务专注于该项目：告诉用户在嵌入式浏览器中登录MagicPath，然后登录后导航回相同的项目URL。不要因为项目画布会话未加载就替换公共的个体设计预览。

不要自动打开项目进行背景工作，例如`info`、`whoami`、列出/搜索数据、检索主题、检查源代码或将组件安装到应用程序中。完整的决策指南和配方位于[使用嵌入式浏览器](references/working-with-embedded-browsers.md)。

## 将现有存储库导入MagicPath

当用户希望将Git存储库中已存在的UI（本地或在线）在他们的MagicPath画布上重现时（例如，“将我的应用程序的侧边栏导入MagicPath”、“在MagicPath中渲染此项目”、“在此处重新创建我的着陆页”），请通过`code start` → `code submit`流程将其重新创建为画布组件。

这是`add`/`inspect`的**逆操作**：真实来源是用户的存储库，目的地是画布。**不要**使用`add`、`inspect`或`code context`进行此操作。简而言之：

1. **获取代码** — 直接读取本地路径，或`git clone --depth 1 <url>`将在线存储库克隆到临时目录（与你的`--dir`分开）。私有存储库需要用户的凭证——询问，不要猜测。
2. **首先读取设计基础** — 全局CSS（`globals.css`/`index.css`/`app.css`）、设计令牌（`tailwind.config.*`、CSS变量、令牌文件）、字体、主题策略和共享UI原语。这是使重现忠实而不是近似的关键。
3. **确定目标** — 对于单个元素（例如侧边栏），打开其文件并遵循所有其导入（子组件、图标、样式、数据）以及赋予其大小和位置的布局父级。对于整个页面/项目，识别入口并决定一个交互式框架与每个屏幕的单独框架（设计默认规则5）——如果模糊不清，请**停止并等待**。
4. **在画布上重新创建** — `code start --project <id> --dir <workdir> --name "..." --width <px> --height <px>`，忠实地填写`src/components/generated/<Name>.tsx`（将存储库的框架和样式转换为React + Tailwind v4），精确匹配颜色/间距/排版，连接真实的交互性，本地模拟数据，然后`code submit --wait`。尊重设计默认值（响应式、居中、无设备模拟、单个屏幕、完全交互）。
5. **使用`view`与源应用程序验证结果**。

完整的分步指南——样式转换表、边缘情况（单体存储库、非React来源、服务器组件、Tailwind v3→v4），以及“将我的应用程序的侧边栏”和“渲染此项目”的快速配方——位于[使用存储库](references/working-with-repositories.md)。

## 从代码编辑或创建画布组件

当用户希望您为他们自己编写或修改MagicPath画布组件本身时，而不是将现有组件安装到单独的应用程序中，请使用此工作流程。`code`子命令操作工作目录和一个小型清单文件（`magicpath-code.json`），该文件跟踪目录属于哪个组件和修订版本。

> **在MagicPath画布上编写时，您是一位专家级设计工程师，构建美观、*功能齐全、交互式*的React组件。** 您在画布上（通过`code start` / `code submit`）生成的组件应该是真实可运行的迷你应用程序，而不是静态设计图稿：状态驱动、悬停/焦点/激活状态连接、按钮执行操作、表单验证、过渡感觉刻意。一个漂亮但无生命的组件是一个失败的组件。（此角色仅适用于`code`流程——当您使用`add`/`inspect`将组件安装到用户的项目中时，请遵循[设计到生产的心态](#设计到生产的心态)）。

### 非常重要——设计默认值

这些规则适用于您使用`code`子命令创建或编辑的每个画布组件，除非用户在请求中**明确**覆盖它们。它们**不**适用于`add`/`inspect`安装流程——为此，请参阅[设计到生产的心态](#设计到生产的心态)。这些规则覆盖此技能中关于画布编写的任何其他内容。

#### 1. 永远不要添加设备模拟

不要将组件包装在iPhone / Android / 笔记本电脑 / 台式机 / 浏览器框架、状态栏、缺口、主屏幕指示器、地址栏或任何其他设备Chrome中。如果用户**明确**要求添加设备模拟（“在手机框架内显示此内容”、“用iPhone模拟包装它”、“使其看起来像Mac窗口”），则才添加设备模拟。为移动视口设计**不是**请求模拟——画布本身就是设备框架。永远不要在它里面绘制第二个设备。

#### 2. 一切都是响应式的——始终如此

每个组件都必须在任何宽度下工作，包括小的原语，如按钮、输入、徽章和卡片。使用`w-full`、`max-w-*`、百分比宽度、flex/grid尺寸和断点实用程序（`sm:`、`md:`、`lg:`）。不要在外部容器上硬编码像素宽度和高度。唯一的例外是本质上固定的元素（头像、图标、固定尺寸的媒体）。

#### 3. 始终在画布中居中

组件的根应将其自身居中在其框架内——水平方向，当设计较短时垂直方向。使用`min-h-screen flex items-center justify-center`、`mx-auto`或在根上使用网格居中。设计绝不能在画布大于内容时粘在角落上，也不能在它较小时溢出。

#### 4. 画布尺寸≠设备模拟

您可以（也应该）向`code start` / `code submit`传递`--width`/`--height`以反映目标设备——例如，对于移动设计`--width 390 --height 844`，对于台式机`--width 1440 --height 900`。这就是如何表示“这是一个移动设计”。但是，内部内容必须保持流体：如果相同的组件稍后被放入更宽或更窄的容器中，它应该适应——而不是锁定到原始像素大小。

#### 5. 永远不要在单个框架内堆叠多个屏幕

MagicPath组件是**一个**框架。不要绘制“屏幕1 / 屏幕2 / 屏幕3”并排、垂直堆叠或作为幻灯片嵌入单个画布中。此输出是损坏的——它不会渲染，它不会导航，并且浪费了用户的画布。

当用户希望获得跨越多个视图的内容时，选择以下两种模式中的一种，并**坚持**：

**A. 在一个框架中自包含的应用程序（当视图属于同一流程时优先）。** 一个组件可以通过使用React状态、条件渲染、标签组件、客户端路由或`useState`驱动的视图切换来包含许多视图、屏幕、模态、标签、步骤或路由。登录→注册→忘记密码流程、多步骤向导、带标签导航的设置页面、带滑出详情面板的仪表板——所有这些都应该在一个具有内部状态的组件中，而不是粘在一起的多框架。

**B. 当屏幕真正独立时使用多个框架（每个屏幕一个组件）。** 如果用户正在要求不同的交付成果——“设计登录屏幕、仪表板和设置页面”——每个都是它自己的MagicPath组件。将它们作为单独的`code start --name "..."`会话创建，**每个会话都有自己的`--dir**”（并行会话共享工作目录将互相覆盖`magicpath-code.json`）。并发构建它们——如果您的环境支持并行子代理，为每个框架生成一个；否则，根据您的运行程序允许的方式并行运行会话。不要尝试将它们全部渲染在单个画布中以“节省时间”——这将产生损坏的工件。

如果您不确定哪种模式适用，请询问用户：“这应该是具有内部导航的一个交互式组件，还是每个屏幕的单独框架？”——并**停止并等待**答案。

#### 6. 构建交互式组件，而不是静态标记

您是一位工程师，而不是截图生成器。每个画布组件必须是**完全交互式**的——按钮触发实际操作、输入受控、表单提交并验证、悬停/焦点/激活/禁用状态进行样式设置、模态框打开和关闭、标签切换、抽屉滑出、下拉菜单展开、切换器翻转、手风琴折叠。使用`useState` / `useReducer`进行本地状态、实际事件处理程序（`onClick`、`onChange`、`onSubmit`、`onKeyDown`、`onBlur`）、`aria-*`属性进行无障碍访问，以及有意义过渡（Tailwind `transition-*`、Framer Motion或CSS动画）在它们添加光泽时。一个留下占位符`onClick={() => {}}`或交互表面静态标记的组件是**未完成的**——在`code submit`之前连接它。如果组件表示多视图流程，请通过状态（见规则5.A）使视图之间的导航工作。

**可编辑文件边界。** `code` API仅接受以下完整文件替换：

- `src/App.tsx`
- `src/index.css`
- `src/components/generated/**`
- `assets/**`仅用于临时图像资产

永远不要编辑或提交`package.json`、`vite.config.*`、`src/main.tsx`、锁文件或任何其他文件——它们将被拒绝。

**图像资产。** 将本地图像文件放在`<workdir>/assets/`中，并从代码或CSS中引用它们，例如`../../../assets/hero.png`、`/assets/hero.png`或`url("../../assets/hero.png")`。MagicPath上传这些临时资产，重写对稳定公共资产URL的引用，并在构建前删除`assets/`暂存文件夹。不要内联`data:image/...;base64,...`；如果您遇到base64图像数据，请将其移动到资产文件中。

**选定的画布图像。** 当用户在`code start`之前选择了画布上的图像形状时，CLI将它们包含在`selectedImages`中，并使用短时效访问URL将每个图像下载到`assets/selected/**`。在导入或CSS中使用下载的`assetPath`。不要直接使用`accessUrl`，因为它会过期。

**删除和重命名源文件在编辑模式下受支持。** 要删除可编辑的源文件，只需从`<workdir>`中删除它——`code submit`检测到删除并传播它。重命名是删除+在相同提交中写入。资产是临时暂存输入，通过删除本地文件不会从服务器中删除。在创建模式下，没有要删除的；只需不要写入文件。

**不要使用`add`或`inspect`进行此工作流程。** `add`/`inspect`用于将可重用的注册组件安装到另一个应用程序中。`code ...`用于在用户的MagicPath画布上编辑组件——它们是分离的流程，不得混合。

### 编辑现有组件

1. 运行`npx -y magicpath-ai code start --component <componentId> --dir <workdir> -o json`。这将创建或重用待处理的编辑修订版本，在画布上显示代理存在，写入可编辑文件，并将`magicpath-code.json`写入`<workdir>`。默认情况下，CLI从组件当前选定的修订版本开始。要改为从特定修订版本开始，请传递`--revision <revisionId>`——当用户正在查看或参考非当前修订版本时（例如，从`npx -y magicpath-ai selection`传递的值）很有用。
2. 在`<workdir>`内部编辑、添加或删除允许的文件（见上面的边界）。将任何新图像放在`<workdir>/assets/`下，并从生成的组件或CSS中引用它们。当您删除子组件文件的最后一个使用时，也删除其源文件——不要在修订版本中留下孤儿文件。重命名是删除+写入。
3. 运行`npx -y magicpath-ai code submit --dir <workdir> --wait -o json`。如果您的编辑更改了预期的画布尺寸，请在提交时传递`--width <px>`和`--height <px>`。
4. 如果作业结果是`failed`，请读取返回的清理诊断，仅修复允许的文件，并再次提交。不要创建新组件以绕过构建失败。
5. 如果提交报告冲突或陈旧基础，请再次运行`npx -y magicpath-ai code start --component <componentId> --dir <workdir> -o json`以刷新状态ful编辑会话，然后再应用您的编辑。

### 创建新组件

**重要体验规则：** 始终在编写组件文件之前运行`code start`。这将向画布注册待处理的组件，以便用户看到您的工作进度，而不是沉默的代理。

**预期文件结构。** MagicPath组件有一个精简的`src/App.tsx`，它导入并渲染来自`src/components/generated/`的顶层组件。实际实现位于`src/components/generated/<ComponentName>.tsx`（PascalCase文件名、命名导出）。较大的组件应拆分为`src/components/generated/`下的额外兄弟文件，每个文件导入它需要的内容。这是每个现有MagicPath组件的结构——比较`code context`返回的任何现有组件的内容。

**CLI在`code start`时为您搭建此结构。** `code start`返回后，工作目录已经包含预连接的`src/App.tsx`和桩`src/components/generated/<ComponentName>.tsx`。组件文件名与`--name`的PascalCase形式匹配（例如，`--name "Hero Card"` → `HeroCard.tsx`）。您的工作是填写桩——**不要重写`App.tsx`**，它已经是正确的。编辑`App.tsx`的唯一原因是更改顶部的`theme`（`'light'`/`'dark'`）值。

步骤：
1. 运行`npx -y magicpath-ai code start --project <projectId> --dir <workdir> --name "Component Name" --width <px> --height <px> -o json`。选择适合您计划构建的组件的尺寸，而不是依赖默认画布尺寸。创建待处理的组件，搭建精简的`App.tsx` + 桩，并写入`magicpath-code.json`。**提醒：** 组件必须是响应式的、居中的、没有设备模拟、**单个屏幕**（使用内部状态进行多视图流程，或使用并行`code start`会话为每个屏幕），并且**完全交互式**（真实处理程序、受控输入、状态驱动视图、悬停/焦点/激活状态）。请参阅上面的[设计默认值](#super-important--design-defaults)。
2. 填写`<workdir>/src/components/generated/<ComponentName>.tsx`中的组件实现。如果组件很大，请在同一目录中拆分为额外文件。
3. 可选地编辑`<workdir>/src/index.css`以进行自定义样式。将图像文件放在`<workdir>/assets/`下，并从TSX或CSS中引用它们，而不是嵌入base64。
4. 运行`npx -y magicpath-ai code submit --dir <workdir> --wait -o json`。如果最终实现需要与启动时选择的画布尺寸不同的尺寸，请在此处传递`--width <px>`和`--height <px>`。
5. 如果构建失败，修复组件文件并重新运行`code submit --wait`。除非用户明确要求，否则不要启动第二个组件。

> `code create`命令是一个方便的组合，将`start`和`submit`合并为一次调用。优先使用显式的两步流程——它在文件仍在编写时使您的进度在画布上可见，并且它为您提供了从它开始的工作起点。

### 单独轮询作业

如果您需要在事后检查作业状态（例如，在提交而没有`--wait`之后），请使用`npx -y magicpath-ai code status <jobId> -o json`。它返回`pending`、`processing`、`completed`、`failed`或`cancelled`之一。

## 快速参考

```bash
# 认证
npx -y magicpath-ai login                    # 一键浏览器登录
npx -y magicpath-ai whoami -o json           # 检查认证状态
npx -y magicpath-ai info -o json             # 完整项目上下文

# 团队和人员
npx -y magicpath-ai list-teams -o json                  # 列出你所属的团队
npx -y magicpath-ai list-members --team "Acme" -o json  # 列出团队的成员

# 创建新项目
npx -y magicpath-ai create-project --name "My Stuff" -o json                    # 个人
npx -y magicpath-ai create-project --name "My Stuff" --team "Acme" -o json      # 团队

# 查找组件（始终使用 -o json）
npx -y magicpath-ai search "input box" -o json          # 在所有工作区中搜索
npx -y magicpath-ai search "button" --team "Acme" -o json   # 在团队内搜索
npx -y magicpath-ai list-projects -o json               # 列出所有项目（个人 + 团队）
npx -y magicpath-ai list-projects --team "Acme" -o json     # 仅列出团队项目
npx -y magicpath-ai list-projects --personal -o json        # 仅列出个人项目
npx -y magicpath-ai list-components <id> -o json      # 列出项目中的组件
npx -y magicpath-ai list-components <id> --created-by <userId> -o json  # 按人员筛选

# 检查/打开组件和项目
npx -y magicpath-ai view <generatedName>              # 在浏览器中打开组件预览
npx -y magicpath-ai view <projectId>                  # 在浏览器中打开项目
npx -y magicpath-ai share <generatedName> -o json     # 为组件打印可分享的 URL（不打开浏览器）
npx -y magicpath-ai share <projectId> -o json         # 为项目打印可分享的 URL（不打开浏览器）
npx -y magicpath-ai inspect <generatedName> -o json   # 显示源代码（无需安装）
npx -y magicpath-ai add <generatedName> --dry-run     # 显示将要安装的内容

# 安装和使用组件
npx -y magicpath-ai add <generatedName> -y         # 添加到项目（不提示）

# 主题（设计系统）
npx -y magicpath-ai list-themes -o json                 # 列出个人主题
npx -y magicpath-ai list-themes --team "Acme" -o json   # 列出团队主题
npx -y magicpath-ai get-theme <id-or-name> -o json    # 获取主题的 CSS 变量、字体、提示

# 当前画布上下文
npx -y magicpath-ai selection -o json                 # 获取当前选中的组件
npx -y magicpath-ai active-project -o json            # 获取用户打开的项目

# 项目画布图片
npx -y magicpath-ai image list <projectId> -o json            # 列出项目画布上的图片（下载每个 `url` 查看图片）
npx -y magicpath-ai image add <projectId> ./hero.png -o json  # 将本地图片（或 http(s) URL）添加到画布
npx -y magicpath-ai image generate --prompt "..." [--aspect-ratio 16:9] [--ref ./photo.jpg] [--out ./img.png] -o json  # AI 生成（或通过 --ref 编辑）位图；返回本地路径 + 托管的 URL

# 从代码中作者/编辑画布组件（外部代理）
npx -y magicpath-ai code start --project <projectId> --dir <workdir> --name "Name" --width <px> --height <px> -o json # 使用选择的画布大小启动新的待处理组件
npx -y magicpath-ai code start --component <componentId> --dir <workdir> -o json                 # 编辑现有组件
npx -y magicpath-ai code start --component <componentId> --revision <revisionId> --dir <workdir> -o json # 编辑特定版本
npx -y magicpath-ai code context <componentId> --dir <workdir> -o json                           # 只读源代码获取/导出；不用于提交
npx -y magicpath-ai code submit --dir <workdir> --width <px> --height <px> --wait -o json         # 提交编辑/大小 + 等待构建
npx -y magicpath-ai code status <jobId> -o json                                                  # 汇报构建任务

## 关键概念

- 每个组件都有一个 **generatedName**（例如，`wispy-river-5234`）—— 这是所有操作的标识符
- 组件作为源代码添加到 `src/components/magicpath/<name>/`
- `add` 命令返回 `importStatement` 和 `usage` —— 在代码中使用这些
- 使用 `inspect` 检查源代码而不安装 —— 不要仅为了阅读代码而使用 `add`
- MagicPath 组件是 React/TypeScript 源代码 —— 在 JS/TS 项目中使用 `add`，在其它语言中使用 `inspect` + 翻译
- **主题**（设计系统）包含 CSS 变量（`light`/`dark` 映射）、可选的 `fonts` 和可选的 `prompt`，其中包含用于代理的样式说明。 "Theme" 和 "design system" 可以互换。使用 `list-themes` 浏览，`get-theme` 获取完整定义
- 使用 `code start` + `code submit` 将源代码编辑发布回 MagicPath 画布。`code context` 是只读的精确版本检索，也可以提供用于外向导出的源代码快照。`add`/`inspect` 始终是组件注册安装和检查路径。

## 当前项目上下文

```json
!`npx -y magicpath-ai info -o json 2>/dev/null || echo '{"error": "Could not run magicpath-ai via npx. Ensure Node.js is installed and the registry is reachable."}'`
```

上面的 JSON 包含认证状态、项目和 CLI 版本。如果 auth.authenticated 为 false，用户需要登录才能执行任何其他操作。

## 参考

- [CLI 参考](references/cli-reference.md)
- [在本地代码中使用 MagicPath 设计](references/using-magicpath-designs-in-local-code.md) — 导出精确的组件或版本，替换本地 UI，或翻译 MagicPath 设计，同时保留 1:1 精度和明确请求的差异
- [使用存储库](references/working-with-repositories.md) — 将现有本地或在线 Git 存储库的 UI 带到 MagicPath 画布上（例如，“在 MagicPath 中渲染此项目”，“将我的应用的侧边栏带到 MagicPath”）
- [使用嵌入式浏览器](references/working-with-embedded-browsers.md) — 在 Codex、Cursor 或其他带有应用内浏览器的宿主中使用 MagicPath 项目作为持久画布
