# MagicPath

一个通过 AI 构建共享和安装 UI 组件的平台。组件作为源代码通过 `magicpath-ai` CLI 添加到用户的项目中。

MagicPath 画布组件也可以直接从本地代码通过 `npx -y magicpath-ai code ...` 子命令创建和编辑 — 见 [从代码编辑或创建画布组件](#edit-or-create-canvas-components-from-code)。该路径是严格的：只有 `src/App.tsx`、`src/index.css` 文件，`src/components/generated/` 下的文件，以及代码工作目录中 `assets/` 下的临时图像资源是可编辑的。

当此技能在具有嵌入式浏览器的代理主机中运行时，在适当的时候使用 MagicPath 项目作为代理旁边的持久视觉画布。如果您为画布创作创建了项目，请在创建后立即在嵌入式浏览器中打开该项目，然后在 `code start` 之前 — 见 [使用嵌入式浏览器](references/working-with-embedded-browsers.md)。

> **术语：** 用户通常将 MagicPath 组件称为“设计”——这两个术语可以互换。当用户说“设计”、“我的设计”或“那个设计”时，将其视为指 MagicPath 组件。相应地搜索、检查和安装。

> 用户还称 MagicPath 设计系统为“主题”。当用户说“主题”、“我的主题”或“使用 X 主题”时，他们指的是 MagicPath 设计系统——一组 CSS 变量、字体和样式说明。使用 `list-themes` 和 `get-theme` 来处理它们。

> 用户可能属于 **团队**（也称为“工作区”）。当用户说“团队的设计”、“我们团队组件”或提到团队名称（如“Acme Inc”）时，他们指的是该团队拥有的项目和组件。使用 `list-teams`、`--team` 和 `--personal` 标志在个人和工作区之间导航。

> 用户还可能询问他们在 MagicPath 中创建的 **技能**。这些是可重用的指令包，可以从 MagicPath 聊天中调用，并使用 `npx -y magicpath-ai skills ...` 管理它们。个人技能位于用户的个人工作区中；团队技能位于 MagicPath 团队中。公共 MagicPath 技能除非平台另有说明，否则是只读的。

## 第一步

运行 `npx -y magicpath-ai info -o json` 以检查授权状态和项目上下文。第一次调用可能需要几秒钟，因为 `npx` 下载了软件包；后续调用很快。

- 如果 `auth.authenticated` 为 `false`，请运行 `npx -y magicpath-ai login`，等待浏览器授权完成，然后使用 `npx -y magicpath-ai whoami -o json` 进行验证。

## 访客会话

如果用户给您一个 **配对代码**（一个简短的代码，如 `gst_…`，通常是因为他们正在尝试没有帐户的 MagicPath），连接一次：

```bash
npx -y magicpath-ai login --guest-code <code>
```

然后运行 `npx -y magicpath-ai whoami -o json` — 它报告 `guest: true`、您可以工作的 `projectId` 和 `canvasUrl`。使用正常的 `code start --project <projectId>` → `code submit` 流程在画布上构建该项目；每个提交都会在画布上实时显示。

访客会话仅限于单个项目，并且会过期。在此范围内：

- 使用 `code start` / `code submit` 在项目上创建和编辑设计——这是会话的整个目的。
- 在具有嵌入式浏览器的主机中，打开 `canvasUrl`（来自 `whoami`），以便用户可以观看您旁边的画布更新。`canvasUrl` 是打开访客画布的唯一方法——不要使用 `share` 或 `view`，这些需要完整的帐户。

> 其他工作区功能（团队、附加项目、主题）属于完整帐户。如果命令报告需要帐户，请告诉用户从他们在浏览器中打开的画布上注册——这会将该项目保存到他们的帐户并解锁所有其他内容。（如果他们的会话已经过期，则无法保存该项目，他们会重新开始。）永远不要告诉访客在没有配对代码的情况下运行 `login`。

## 与团队一起工作

用户可能属于拥有共享项目和主题的团队。默认情况下，`list-projects` 和 `search` 返回来自 **所有** 工作区的结果（个人 + 每个用户所属的每个团队）。使用过滤标志来缩小范围。

### 发现团队

运行 `npx -y magicpath-ai list-teams -o json` 查看用户所属的团队：

```json
{ "teams": [{ "id": "123", "name": "Acme Inc", "role": "ADMIN" }] }
```

### 按团队进行过滤

- **默认（没有标志）**：`list-projects`、`search` 包括个人和所有团队项目——无需额外的标志即可进行广泛发现。
- **`--team "Acme Inc"` 或 `--team <teamId>`**：过滤到特定团队。适用于 `list-projects`、`search`、`list-themes` 和 `get-theme`。
- **`--personal`**：仅显示用户的个人项目/组件。适用于 `list-projects` 和 `search`。

### JSON 输出

项目和搜索结果包括 `ownerType` (`"personal"` 或 `"team"`）和 `ownerName`（用户电子邮件或团队名称）。使用这些信息来告诉用户组件的位置。

### 发现人员

运行 `npx -y magicpath-ai list-members --team "Acme Inc" -o json` 查看团队中的成员：

```json
{ "team": { "id": "123", "name": "Acme Inc" }, "members": [{ "id": "456", "displayName": "Chloe Smith", "email": "chloe@acme.com", "role": "MEMBER" }] }
```

### 按人员进行过滤

- **`--created-by <userId>`** 在 `list-components` 上：过滤到特定用户创建或编辑的组件。使用 `list-members` 解析人员姓名及其用户 ID。
- **`createdBy`** 字段在项目上：`list-projects` 中的每个项目都包括 `createdBy: { id, displayName }`，显示谁创建了它。
- **`lastEditedBy`** 字段在组件上：`list-components` 中的每个组件都包括 `lastEditedBy: { id, displayName }`，显示谁最后编辑了它。

**重要提示：**您只能看到经过身份验证的用户可以访问的项目——您自己的个人项目以及您是团队成员的团队项目。您 **不能** 访问另一个用户的个人项目。当您查找另一个人的工作时，仅搜索 **团队项目** (`--team`)，而不是个人项目。个人项目对其所有者保密，除非有人明确被邀请作为成员。

### 常见模式

- **“Chloe 上次在做什么？”** → `list-members --team "Acme Inc" -o json` 查找 Chloe 的用户 ID → `list-projects --team "Acme Inc" -o json` 仅获取 **团队项目** → `list-components <projectId> --created-by <chloeId> --sort-by createdAt --order desc -o json` 对于每个项目。报告最新的组件。**不要** 搜索另一个用户的个人项目——个人项目对其所有者保密。
- **“显示团队的设计”** 或 **“Acme Inc 创建了什么？”** → `list-teams` 查找团队，然后 `list-projects --team "Acme Inc" -o json`，然后 `list-components <projectId> -o json`。
- **“显示团队最新的设计”** → 与上面相同，但在 `list-components` 上使用 `--sort-by createdAt --order desc --limit 1`。
- **“谁创建了此项目/组件？”** → 检查项目上的 `createdBy` 字段或组件的 `lastEditedBy` 字段从相应的列表命令中获取。
- **“我的设计”** 没有提到团队 → 默认（所有项目）通常正确。只有在用户明确希望排除团队项目时才使用 `--personal`。
- **“使用团队的主题”** → `list-themes --team "Acme Inc" -o json`，然后 `get-theme <name> --team "Acme Inc" -o json`。

## 管理 MagicPath 技能

当用户要求创建、列出、检查、更新、导入、删除、启用/禁用或本地安装存储在 MagicPath 中的技能时，请使用此流程。对于返回数据返回的每个命令，请优先使用 JSON 模式：

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
- 不使用 `--team` 对于个人技能。
- `skills list` 默认包括公共 MagicPath 技能，因为它们是用户在聊天中可用的。当用户想要他们可以编辑的技能时，请传递 `--owned-only`。
- 公共技能是只读的。除非命令输出明确标识它们为拥有的/可编辑的，否则不要尝试更新或删除公共技能。
- 导入的 `.zip` 或 `.skill` 包在 MagicPath 中是内容不可变的；它们仍然可以使用 `skills update <id> --enable/--disable` 启用或禁用。

### 创建或更新技能

- 对于超过简短的一行指令，将指令写入本地文件并使用 `--instructions-file`。这避免了 shell 引用问题并保留了 Markdown。
- MagicPath 技能需要一个非空的名称、描述和指令。描述应该说明何时使用技能；指令应该说明如何执行工作。
- 如果用户正在将观察到的工作流程转换为可重用的技能，请总结触发器、约束、步骤、示例以及未来代理应读取的任何文件或参考。

### 在本地安装 MagicPath 技能

当用户希望将来自 MagicPath 的技能安装到他们外部编码代理中时，首先检索它，然后重新创建它为本地 Agent Skills 文件夹：

1. 运行 `npx -y magicpath-ai skills get <skillIdOrSlug> -o json`。
2. 创建一个以技能 slug 命名的文件夹。
3. 使用包含至少 `name` 和 `description` 的 frontmatter 编写 `SKILL.md`，后跟检索到的 `instructions`：

```markdown
---
name: example-skill
description: Use when ...
---

...来自 MagicPath 的指令...
```

4. 如果技能包含捆绑的包文件，运行 `npx -y magicpath-ai skills get <skillIdOrSlug> --files -o json`，然后使用 `--file <path>` 获取每个文件，并在本地技能文件夹中重新创建相同的相对路径。
5. 使用当前代理主机的地方性本地技能工作流程安装或注册该文件夹。如果主机支持 Agent Skills CLI，则使用该工具从本地文件夹安装；否则，将文件夹放置在主机文档化的本地技能目录中。

在写入用户当前项目之外或全局代理配置目录之前，请先询问。

## 工作流程

> **始终使用 `-o json`** 对于所有返回数据的命令 (`search`, `list-projects`, `list-components`, `list-teams`, `list-themes`, `get-theme`, `skills`, `selection`, `active-project`, `info`, `add`, `inspect`, `code`)。这为您提供了结构化输出以供您使用，而不是人类可读的表格。

### 第一阶段：发现

1. **检查授权** — 运行 `npx -y magicpath-ai whoami -o json` 以验证身份验证。
2. **检查当前选择** — 如果用户引用“选定的组件”、“选定的图像”、“我选中的设计”或以其他方式指向一个 *特定* 画布选择，运行 `npx -y magicpath-ai selection -o json`。如果它返回组件，则直接使用它们——跳过搜索/确认流程并继续使用返回的 `generatedName`(s)。每个返回的组件还包括 `selectedRevisionId`，这是当前在画布上显示的组件的修订版本。响应还可以包括选定的 `images`；当您随后运行 `code start` 时，这些选定的图像将作为 `assets/selected/**` 可用，如下所述。当下游命令接受修订（例如 `code context --revision`），请通过，以便操作针对用户正在查看的版本，而不是数据库中 canonical 的修订版本。
3. **检查活动项目** — 如果用户引用“我当前打开的项目”、“这个项目”、“我正在处理的工作”或以其他方式暗示工作项目上下文而未命名特定组件，运行 `npx -y magicpath-ai active-project -o json`。它返回用户当前在浏览器中打开的项目，即使没有选择任何内容。如果它返回一个项目，将其视为活动项目并跳过项目选择器。如果它返回多个，列出它们并询问哪个。如果它返回空列表，则用户没有打开画布——使用 `list-projects` 并询问用户。根据用户所说选择正确的命令：`selection` 对于引用的组件，`active-project` 对于引用的项目，`list-projects` + 询问如果两者都不是。 （注意：`selection` 还返回活动项目，所以当用户引用组件时，您已经获得了项目——不需要单独的 `active-project` 调用。）
4. **查找组件** — 使用 `npx -y magicpath-ai search <query> -o json` 搜索所有项目，或 `list-projects -o json` 然后浏览。如果 `active-project` 已经给您一个项目，请通过 `list-components <projectId> -o json` 将搜索范围限定为该项目，而不是搜索每个工作区。
5. **查看项目的图像** — 要知道哪些独立的图像已经存在于项目的画布上（要引用它们，避免重复，或向用户描述它们），运行 `npx -y magicpath-ai image list <projectId> -o json` 并下载每个 `url` 以查看它——与您使用 `previewImageUrl` 引用组件相同的方式使用。 （这些是画布图像，与 `code` 流中的 `assets/` 构建输入分开。）
   对于 **独立的位图请求**——照片、插图、纹理或透明切割——使用 `npx -y magicpath-ai image generate --prompt "..." -o json` 考虑使用 `npx -y magicpath-ai image generate` 而不是构建画布设计；将 `--ref <path>` 传递给编辑或重风格现有照片。使用 `image add` 将其放置在画布上，或将其复制到代码会话的 `assets/` 文件夹中，以便在设计中使用。见 [image generate](references/cli-reference.md) 以获取标志。
6. **从视觉上理解组件** — `search` 和 `list-components` 结果包括 `previewImageUrl` 字段。下载并分析这些图像，以了解每个组件看起来像什么，然后再推荐它。预览图像仅用于您自己的理解——除非用户明确要求在嵌入式项目画布上查看该设计，否则不要导航到单个设计预览。

7. **确认用户（停止并等待）**——除非用户指定了确切的 `generatedName`，否则请告诉用户您发现了什么（名称、`generatedName`、项目），并询问是否正确。当嵌入式项目画布处于活动状态时，保持它在项目上，并且只有在用户明确要求时才打开或共享单个设计。如果没有嵌入式项目画布，则使用 `npx -y magicpath-ai view <generatedName>` 作为正常的确认后备。如果多个匹配项，列出所有内容并询问是哪一个。 **这是一个停止点——结束您的响应并等待用户回复。不要继续，直到用户明确确认。** 不要运行 `add` 或 `inspect`。

### 编辑现有组件

1. 运行 `npx -y magicpath-ai code start --component <componentId> --dir <workdir> -o json`。这会创建或重用挂起的编辑修订，在画布上显示代理存在，写入可编辑文件，并写入 `<workdir>/magicpath-code.json`。默认情况下，CLI 从组件的当前选定修订开始。要从一个特定修订开始，请传递 `--revision <revisionId>`——当用户正在查看或引用非当前修订（例如从 `npx -y magicpath-ai selection` 传递的值）时，这很有用。
2. 在 `<workdir>` 中编辑、添加或删除允许的文件（见上面的边界）。将任何新图像放在 `<workdir>/assets/` 中，并从生成的组件或 CSS 中引用它们。当您删除使用子组件文件的最后一个用法时，也删除其源文件——不要留下遗孤文件。重命名是删除加写入。
3. 运行 `npx -y magicpath-ai code submit --dir <workdir> --wait -o json`。如果您的编辑更改了您在开始时选择的画布大小，请在提交时传递 `--width <px>` 和 `--height <px>`。
4. 如果作业结果为 `failed`，请阅读返回的清理诊断，仅修复允许的文件，然后再次提交。不要创建一个新的组件来绕过构建失败。
5. 如果提交报告冲突或陈旧基础，请再次运行 `npx -y magicpath-ai code start --component <componentId> --dir <workdir> -o json` 以刷新状态会话，然后再应用您的编辑。

### 创建新组件

**重要的体验规则：**始终在写入组件文件之前运行 `code start`。这将在画布上注册挂起的组件，以便用户可以看到您的工作进度，而不是在文件仍然被写入时无声的代理。 `code start` 生成的文件结构如下：MagicPath 组件有一个精简的 `src/App.tsx`，它导入并渲染顶级组件来自 `src/components/generated/`。实际实现位于 `src/components/generated/<ComponentName>.tsx`（PascalCase 文件名，命名导出）。较大的组件应拆分为 `src/components/generated/` 下的其他兄弟文件，每个文件导入它需要的组件。这是每个现有 MagicPath 组件的结构——比较 `code context` 返回的任何现有组件的源修订。组件文件名与 `--name` 的 PascalCase 形式匹配（例如 `--name "Hero Card"` → `HeroCard.tsx`）。您的任务是填写占位符——**不要** 重写 `App.tsx`，它已经是正确的。唯一需要编辑 `App.tsx` 的原因是更改顶部的 `theme` (`'light'`/`'dark'`) 值。

步骤：
1. 运行 `npx -y magicpath-ai code start --project <projectId> --dir <workdir> --name "Component Name" --width <px> --height <px> -o json`。选择适合您计划构建的尺寸，而不是依赖默认画布大小。创建挂起的组件，生成精简的 `App.tsx` + 占位符，并写入 `magicpath-code.json`。 **提醒：** 组件必须是对应的，包括响应式的、居中的、没有设备模拟的、单个屏幕的、完全交互式的（具有真实处理程序、受控输入、状态驱动视图、悬停/焦点/活动状态）。见上面的 [设计默认值](#super-important--design-defaults)。
2. 使用 `<workdir>/src/components/generated/<ComponentName>.tsx` 填写组件实现。如果组件很大，请将它们拆分为同一目录中的其他文件。
3. 可选地编辑 `<workdir>/src/index.css` 以进行自定义样式。将图像文件放在 `<workdir>/assets/` 中，并从 TSX 或 CSS 中引用它们，而不是嵌入 base64。
4. 运行 `npx -y magicpath-ai code submit --dir <workdir> --width <px> --height <px> --wait -o json`。如果最终实现需要与开始时选择的画布大小不同的尺寸，请在此处传递 `--width <px>` 和 `--height <px>`。
5. 如果构建失败，请修复组件文件并重新运行 `code submit --wait`。除非用户明确要求开始第二个组件，否则不要。

> `code create` 命令是一个方便的功能，将 `start` 和 `submit` 合并为一行调用。优先使用明确的两步流程——它使您的进度在文件仍然被写入时在画布上可见，并为您提供要从中工作的脚手架起点。

### 单独轮询作业

如果您需要在事后检查作业状态（例如，在提交但没有 `--wait` 的情况下），使用 `npx -y magicpath-ai code status <jobId> -o json`。它返回 `pending`、`processing`、`completed`、`failed` 或 `cancelled` 之一。
