# HeyGen 头像设计器

为任何人创建和管理 HeyGen 头像：代理、用户或命名角色。处理身份提取、头像生成、语音选择，并将所有内容保存到 `AVATAR-<NAME>.md` 以便一致地重复使用。

## 文件和路径

此技能读取和写入以下内容。未经明确用户指令，不会访问其他文件。

| 操作 | 路径 | 目的 |
|------|------|------|
| 读取 | `SOUL.md`, `IDENTITY.md` | 创建代理头像时提取身份详情 |
| 读取 | `AVATAR-<NAME>.md` | 加载现有头像身份（用于变体外观、语音更新） |
| 写入 | `AVATAR-<NAME>.md` | 创建后保存新的头像身份 |
| 写入 | `AVATAR-AGENT.md`, `AVATAR-USER.md` (符号链接) | 角色别名，见第 5 步 |
| 临时写入 | `/tmp/openclaw/uploads/` | 语音预览音频（下载供用户播放，会话后删除） |
| 远程上传 | HeyGen (通过 `heygen asset create` 或 MCP) | 用户提供的照片上传到 HeyGen 以创建数字孪生 |

只有在用户明确提供它们时，资产才会上传到 HeyGen。

## 语言感知

**从用户的第一条消息中检测用户的语言。** 存储为 `user_language`（例如，`en`, `ja`, `es`, `ko`, `zh`, `fr`, `de`, `pt`）。

1. **使用用户的语言与用户沟通。** 所有问题、状态更新、确认和错误消息都应在 `user_language` 中。
2. **语音设计提示和选择尊重 `user_language`。** 在设计或选择语音时，指定目标语言，以便语音库返回匹配的语音。
3. **技术指令保持为英语** — 枚举值（`Young Adult`, `Realistic`, `landscape` 等）是 API 级别的，不进行翻译。

## 用户体验规则

1. **保持简洁。** 不要在聊天中包含头像 ID、组 ID 或原始 API 负载。报告结果（头像已创建，准备使用），而不是管道细节。
2. **不要使用内部术语。** 不要向用户提及内部步骤名称（“步骤 0”，“步骤 5 符号链接维护”）。用户看到的是自然对话：“正在设置您的头像…”而不是“正在运行步骤 2 头像创建”。
3. **每个步骤一个或两个问题。** 不要批量提问。按顺序进行步骤，询问进行下一步所需的最小问题集。
4. **在提问之前读取工作区文件。** `SOUL.md`, `IDENTITY.md`, 工作区根目录下的 `AVATAR-*.md` 包含身份信息。首先检查它们。只要求用户提供确实缺失的内容。
5. **不要描述技能内部。** 不要说“让我读取工作流程”，“检查参考文件”，“加载头像发现指南”。默默读取。用户看到的是问题和结果，而不是内部导航。
6. **不要宣布您即将做什么。** 跳过元评论，如“现在正在创建头像”。直接执行工作。如果某个步骤需要时间，用户接下来听到的应该是结果（或一个检查点问题）。
7. **永远不要描述传输选择。** MCP 与 CLI 是内部的。默默选择传输方式，永远不要提及它。如果两者都不可用，请要求用户配置其中一种，而无需解释原因。

## 从这里开始（关键）

**默认目标 = 代理。** 此技能的主要用途是为代理提供一个头像和语音，以便它可以展示视频。仅在明确使用“我的头像”/“我”/“我的照片”语言时才路由到“用户”。当不确定时，创建代理的头像。

**不要批量提问。** 不要一次提供照片、语音偏好、持续时间、目标平台、语调、关键信息。按顺序进行步骤。每个步骤一次最多问一两个问题。

**对于代理头像：首先读取 SOUL.md 和 IDENTITY.md，然后直接进行基于提示的创作。** 不要先询问用户照片或外观细节。代理的身份存在于这些工作区文件中。只有当用户确实缺少特征时，才要求用户提供特征。

**基于提示的创作是默认的创建路径。** 照片是可选的，仅在用户明确希望创建他们本人的真实人物数字孪生时才相关。代理和命名角色几乎总是使用基于提示的创作。

## 开始之前（环境检测）

尝试从工作区根目录读取 `SOUL.md`。

- **找到** → OpenClaw 环境。跳过此整个部分，直接进入第 0 步。工作区本地身份（SOUL.md, IDENTITY.md）将驱动代理引导。
- **未找到** → Claude Code 环境，没有工作区身份文件。仍然进入第 0 步——不要跳过列出用户头像或询问用户照片。

**⚠️ AVATAR 文件注意事项：** 忽略工作区中属于*不同*人或代理的任何 AVATAR-*.md 文件（例如，创建 Claude 的头像时出现 AVATAR-Eve.md）。只有当其名称与您当前正在创建的主题匹配时，才使用 AVATAR 文件。

**⚠️ 不要在此时获取 HeyGen 头像。** 那是第 0 步的子步骤（仅在目标检测之后）。在第 0 步之前获取会导致代理将对话围绕“您现有的头像”展开，而默认应该是为代理创建一个。

## API 模式检测

**模式选择是默默进行的。** 在会话开始时检测一次，选择一个模式，然后继续。永远不要描述传输选择（“CLI 已损坏”，“切换到 MCP”）——用户不关心调用方式。

**MCP（首选）：** 如果 HeyGen MCP 工具可用（工具匹配 `mcp__heygen__*`），则使用它们。MCP 通过 OAuth 进行身份验证——不需要 API 密钥——并针对用户的现有 HeyGen 计划信用额度运行。

**CLI 备用：** 如果 MCP 工具不可用并且 `heygen` 二进制文件运行正常（`heygen --version` 退出码为 0），则使用它。身份验证：`HEYGEN_API_KEY` 环境变量或 `heygen auth login`（持久化到 `~/.heygen/credentials`）。如果 CLI 缺失、`--version` 出错或身份验证未设置，则默默跳过——不要重试 MCP。

**两者都不可用：** 只有当 MCP 不可用并且 CLI 不工作时，才向用户报告一次：“要使用此技能，请连接 HeyGen MCP 服务器或安装 HeyGen CLI：`curl -fsSL https://static.heygen.ai/cli/install.sh | bash` 然后 `heygen auth login`。”

**API：** 仅限 v3。永远不要调用 v1 或 v2 端点。

**文档优先规则：** 在调用任何您不确定的端点之前：
- **索引：** `GET https://developers.heygen.com/llms.txt` — 完整站点地图
- **任何页面：** 将 `.md` 添加到 URL 以获取干净的 Markdown
- 或者运行 `heygen <名词> <动词> --help`
- 阅读规范，然后构建您的请求。永远不要猜测字段名称。

## 头像文件约定

每个头像都有一个文件：工作区根目录下的 `AVATAR-<NAME>.md`。

```
AVATAR-EVE.md      ← 代理      (命名，规范)
AVATAR-KEN.md      ← 用户       (命名，规范)
AVATAR-CLEO.md     ← 角色  (命名，规范)
```

该技能还维护两个**基于角色的符号链接**，与命名文件一起存在，以便消费技能（例如，heygen-video）在没有特定名称的请求时进行通用查找（“为我制作一个视频”→ 读取代理别名；“为我制作一个视频”→ 读取用户别名）：

```
AVATAR-AGENT.md → AVATAR-<CURRENT-AGENT-NAME>.md   (符号链接)
AVATAR-USER.md  → AVATAR-<CURRENT-USER-NAME>.md    (符号链接)
```

命名文件是唯一的信息来源；别名是指针，永远不会漂移。工作流的第 5 步维护它们。命名角色没有角色别名——它们仅通过名称引用。

格式：
```markdown
# 头像： <名称>

## 外观
- 年龄： <自然语言>
- 性别： <自然语言>
- 种族： <自然语言>
- 头发： <自然语言>
- 体型： <自然语言>
- 特征： <自然语言>
- 风格： <自然语言>
- 参考： <可选的工作区相对路径或 URL>

## 语音
- 语调： <自然语言>
- 口音： <自然语言>
- 能量： <自然语言>
- 思考： <一句话类比>

## HeyGen
- 组 ID： <角色身份锚点——稳定参考，永远不会改变>
- 语音 ID： <匹配或设计的语音>
- 语音名称： <人类可读>
- 语音设计： <如果自定义设计则为 true，如果从目录中选择则为 false>
- 语音种子： <使用的种子值，如果设计>
- 外观： landscape=<外观 ID>, portrait=<外观 ID>, square=<外观 ID>
- 最后同步： <ISO 时间戳>

⚠️ look_ids 是短暂的——始终在工作时通过 `heygen avatar looks list --group-id <id>`（或 MCP `list_avatar_looks`）从组 ID 中解析。永远不要将 look_id 作为主要头像参考。
```

**顶部部分**（外观，语音）是可移植的自然语言。任何平台都可以使用它们。
**HeyGen 部分**是运行时配置，包含 API ID。技能读取此内容以进行 API 调用。

## 技能公告

开始每个调用：

> 🎭 **使用：heygen-avatar** — 为 [名称] 创建头像

## 工作流

**不要在开始时批量提问。** 按顺序进行步骤。每个步骤一次最多问一两个问题，并且只有在需要时才提问。

### 第 0 步 — 我们在为谁创建？

见上面的“从这里开始”部分中的默认到代理规则。仅在措辞明确时才路由到“用户”或“命名角色”。

路由信号（按优先级排序）：

1. **用户**（仅明确）— “创建**我的**头像”，“为我制作一个头像”，“我想我的脸出现在视频中”，“**我**的数字孪生”，“基于**我**的照片”。需要指代用户的限定词 OR 明确提及他们的照片。如果名称不明显，请询问他们的名称。
2. **命名角色**（仅明确）— “创建一个名为 Cleo 的头像”，“设计一个名为 X 的角色”，“构建一个名为 Y 的主持人” → 使用给定的名称。
3. **代理**（默认）— 所有其他内容： “创建你的头像”，“让自己活过来”，“设置一个头像”，“让我们制作一个头像”，“创建一个头像”，“设计一个主持人”，“我想你出现在视频中”，或任何模糊的措辞。读取 `IDENTITY.md` 获取名称。

**不确定时，默认为代理。** 不要在模糊请求中询问用户他们的名称、外观或语音——这是错误的第一次动作。如果在读取 IDENTITY.md + SOUL.md 后意图仍然模糊，请问一个简短的澄清问题以消除歧义（自然地表达——例如，“快速检查：这个头像是为你，还是为我？”）。

然后检查工作区根目录下的 `AVATAR-<NAME>.md`：

- **AVATAR 文件存在 + HeyGen 部分已填写** → “您已经设置了一个头像。想要添加一个新的外观，更新它，还是重新开始？” 等待答案。
- **AVATAR 文件存在但 HeyGen 部分为空** → 跳到第 2 步。
- **没有 AVATAR 文件** → 进入第 1 步。

**角色别名陈旧性检查。** 在继续之前，还要检查此目标的角色别名是否已经指向正确的命名文件：

- 对于**代理目标**：读取 `AVATAR-AGENT.md`（跟随符号链接）并与 `AVATAR-<CURRENT-AGENT-NAME>.md` 比较。如果它们不同（例如，`AVATAR-AGENT.md` → `AVATAR-OLD-NAME.md` 因为代理身份自上次运行以来已更改），即使在未进行其他更改的情况下，第 5 步也要重新链接。命名文件是规范的，但别名必须匹配*当前*身份，而不是历史身份。
- 对于**用户目标**：对 `AVATAR-USER.md` 进行相同的检查。
- 对于**命名角色**：没有别名要检查。

**可选的现有头像检查**（仅当用户可能已经在他们的 HeyGen 账户中拥有头像时对用户路径有用）。如果第 0 步目标 = **用户** 并且没有 `AVATAR-<USER>.md`，则首先列出他们的 HeyGen 头像：

**MCP:** `list_avatar_groups(ownership=private)`
**CLI:** `heygen avatar list --ownership private`

如果列表非空，则提供选项并询问是要使用哪个头像，还是要创建新的。如果为空，则进入第 1 步。对于代理和命名角色目标，完全跳过此检查——它们存在于 AVATAR-*.md 中，而不是 HeyGen 目录中。

### 第 1 步 — 身份提取

**顺序很重要。文件优先，问题其次。基于提示的创作是默认路径——照片是可选的升级。**

**对于代理**（第 0 步目标 = 代理）：
1. 从工作区根目录读取 `SOUL.md`、`IDENTITY.md` 和任何现有的 `AVATAR-<NAME>.md`。
2. 如果找到 SOUL.md 或 IDENTITY.md → 默默提取外观和语音特征。不要询问用户“描述你的外观”——代理是主题，其身份存在于这些文件中。**如果文件仅描述个性/价值观而没有物理描述，则不要进行幻觉特征。** 仅对话式地询问用户缺失的外观特征（一次或两次）。
3. 如果两个文件都未找到（例如，没有工作区身份的 Claude Code 环境）→ 对话式引导用户描述代理的外观和语音。
4. 直接进入 **类型 A（提示）创作** 在第 2 步默认。不要询问照片，除非用户自愿提供或明确要求照片真实性——代理几乎总是使用基于提示的创作。

**对于用户/命名角色**（第 0 步目标 = 用户或命名）：
- 对话式引导。自然地询问外观和语音——一次或两次问题，而不是表格。使用 `user_language` 进行沟通。
- **仅用户路径：** 在引导问答后，运行下方的参考照片提示。
- **命名角色路径：** 跳过提示，直接进入类型 A（提示）创作。

写入 `AVATAR-<NAME>.md` 并填写外观和语音部分。直到第 2 步成功，HeyGen 部分保持为空。

### 参考照片提示（仅用户路径）

仅在以下情况下运行此步骤：第 0 步目标 = **用户**（真实人物数字孪生）或用户明确要求照片真实性。

- 首先检查 AVATAR 文件的“参考”字段。如果已有照片，则跳过询问并使用它。
- 否则，问一句话：*"有头像照吗？它为您的视频提供更好的面部一致性。我可以根据您的描述生成——只需说'跳过'。*

分支：
- **提供照片** → 通过 MCP `upload_asset` 或 `heygen asset create --file <路径>` 上传，然后进入第 2 步的类型 B（照片）创作。
- **跳过** → 第 2 步的类型 A（提示）创作。

对于代理和命名角色，跳过整个步骤——直接进入类型 A（提示）创作。

### 第 2 步 — 头像创作

📖 **完整的创作 API 表面（照片 / 提示 / 数字孪生）、文件输入格式、身份字段 → 枚举映射、响应形状 → [参考资料/avatar-creation.md](references/avatar-creation.md)**

两种模式：

**模式 1 — 新角色**（省略 `avatar_group_id`）：
创建一个全新的角色，拥有自己的组。

**模式 2 — 新外观**（包含 `avatar_group_id`）：
向现有角色添加一个变体。从 AVATAR 文件中读取组 ID。

两种创作类型：

**类型 A — 基于提示（AI 生成外观）：**

**MCP:** `create_prompt_avatar(name=<name>, prompt=<appearance>, avatar_group_id=<可选>)`
**CLI:** `heygen avatar create -d '{"type":"prompt","name":"...","prompt":"...","avatar_group_id":"..."}'`（接受内联 JSON、文件路径或 `-` 作为 stdin）

提示限制为 1000 个字符。描述要详细——包括风格、特征、表情、光照。API 规范说 200，但实际强制限制是 1000。

**类型 B — 基于参考图像：**

**MCP:** `create_photo_avatar(name=<name>, file=<file_object>, avatar_group_id=<可选>)`
**CLI:** `heygen avatar create -d '{"type":"photo","name":"...","file":{"type":"url","url":"..."},"avatar_group_id":"..."}'`

类型 B 的文件选项：
- `{ "type": "url", "url": "https://..." }` — 公共图像 URL
- `{ "type": "asset_id", "asset_id": "<id>" }` — 来自 `heygen asset create --file <路径>`
- `{ "type": "base64", "media_type": "image/png", "data": "<base64>" }` — 内联

📖 **何时使用每个（URL vs asset_id vs base64）、上传路由和边缘情况 → [参考资料/asset-routing.md](references/asset-routing.md)**

**响应：** 返回 `.data.avatar_item.id`（外观 ID）和 `.data.avatar_item.group_id`（角色身份）。

将身份字段映射到 HeyGen 枚举以用于提示：
- **年龄**：Young Adult | Early Middle Age | Late Middle Age | Senior | 未指定
- **性别**：Man | Woman | 未指定
- **种族**：White | Black | Asian American | East Asian | South East Asian | South Asian | Middle Eastern | Pacific | Hispanic | 未指定
- **风格**：Realistic | Pixar | Cinematic | Vintage | Noir | Cyberpunk | 未指定
- **方向**：square | horizontal | vertical
- **姿势**：half_body | close_up | full_body

在创建之前向用户显示提示：
> **外观：** "[提示]"
> **设置：** Young Adult | Woman | East Asian | Realistic
> 看起来不错吗？(是 / 调整 / 完全不同)

⛔ **停止。等待用户批准或调整。** 在调用头像创作 API 之前。

### 第 3 步 — 语音

两条路径：**设计**（描述您想要的内容，获取匹配的语音）或**浏览**（手动过滤目录）。

询问他们是否想要语音设计（描述他们想要的内容）或目录浏览。使用 `user_language` 进行沟通。

默认为 **设计**，如果 AVATAR 文件具有语音部分并具有人格特征。

#### 路径 A — 语音设计（首选）

使用来自 AVATAR 文件的语音部分进行语义搜索以找到匹配的语音。这会搜索 HeyGen 的完整语音库。不会生成新语音，也不会消耗配额。

**语言匹配：** 语音设计提示应指定目标语言从 `user_language`。例如，对于日语：`"一个平静、温暖的女性声音。专业但易于接近。日语说话者。"` 这确保语义搜索返回的语音说正确的语言。

**MCP:** `design_voice(prompt=<voice description>, seed=0)`
**CLI:** `heygen voice create --prompt "..." --seed 0`（也接受 `--gender`, `--locale`）

每个种子返回 3 个语音选项。显示所有 3 个选项，并附带内联音频预览：
- 将每个 `preview_audio_url` 下载到临时路径（任何标准下载方法都行——不需要 HeyGen 身份验证，这些是公共 S3 URL）
- 作为音频附件发送：`message(action:send, media:"<path>", caption:"选项 <n>: <voice_name> — <gender>, <language>")` 以便在 Telegram/Discord 中内联播放
- 在发送所有预览后，显示选择按钮

⛔ **停止。等待用户通过按钮或文本选择语音。** 不要自己选择语音或继续到第 4 步，直到用户明确选择。

如果都不匹配：
> "没有一个符合要求？我可以尝试不同的设置（相同的描述，不同的变体）或您可以调整描述。"

增加 `seed` 并再次调用。不同的种子会给出完全不同的语音选项，来自相同的提示。

- 用户选择后清理 /tmp 文件

#### 路径 B — 语音浏览（备用）

浏览 HeyGen 的现有语音库：

**MCP:** `list_voices(type=private)` 然后 `list_voices(type=public, language=<lang>, gender=<gender>)`
**CLI:** `heygen voice list --type private` / `heygen voice list --type public --language <lang> --gender <gender>`

1. 读取 AVATAR 文件的语音部分
2. 按性别和语言过滤
3. 基于人格匹配选择前 3 个候选者
4. 显示内联音频预览（与路径 A 中的下载 + 发送模式相同）
5. ⛔ **停止。等待用户选择。** 不要自动选择。

### 第 4 步 — 保存到 AVATAR 文件

更新 `AVATAR-<NAME>.md` 的 HeyGen 部分，以匹配规范格式：

```markdown
## HeyGen
- 组 ID: <.data.avatar_item.group_id — 稳定参考，永远不会改变>
- 语音 ID: <chosen voice_id>
- 语音名称: <voice name>
- 语音设计: <如果自定义设计则为 true，如果从目录中选择则为 false>
- 语音种子: <使用的种子值，如果设计>
- 外观: <orientation>=<.data.avatar_item.id> (例如，landscape=<look_id>, portrait=<look_id>)
- 最后同步: <ISO 时间戳>

⚠️ look_ids 是短暂的——始终在工作时通过 `heygen avatar looks list --group-id <id>`（或 MCP `list_avatar_looks`）从组 ID 中解析。永远不要将 look_id 作为主要头像参考。
```

确认头像已保存，其他技能（如 heygen-video）将自动获取它。使用 `user_language` 进行沟通。

### 第 5 步 — 维护角色别名

在写入命名 `AVATAR-<NAME>.md` 后，在工作区旁边创建或更新一个基于角色的符号链接，以便其他技能可以在没有特定名称的请求时进行通用查找。

根据第 0 步目标：

- **代理目标** → 符号链接 `AVATAR-AGENT.md` → `AVATAR-<NAME>.md`
- **用户目标** → 符号链接 `AVATAR-USER.md` → `AVATAR-<NAME>.md`
- **命名角色** → 没有角色别名。命名角色仅通过名称引用（例如，`AVATAR-CLEO.md`）；它们不是代理或用户。

**实现（从工作区根目录运行，使用 fs-fallback）**

`cd` 到工作区根目录是强制性的——在 `ln -s` 中的裸相对路径从代理的当前工作目录解析，而不是 SOUL.md 的位置。`|| echo` 子句处理拒绝符号链接的文件系统（没有 dev 模式的 Windows，一些云挂载存储）而不会中止第 5 步。

```bash
# 代理
cd "$WORKSPACE_ROOT" && ln -sf AVATAR-<NAME>.md AVATAR-AGENT.md \
  || echo "role alias skipped: fs doesn't support symlinks"

# 用户
cd "$WORKSPACE_ROOT" && ln -sf AVATAR-<NAME>.md AVATAR-USER.md \
  || echo "role alias skipped: fs doesn't support symlinks"
```

使用相对链接目标（仅文件名，不带路径前缀），以便别名在工作区移动或复制时仍然存在。

`ln -sf` 是在底层执行 unlink-then-symlink，不是严格原子性的。对于单用户工作区足够好；如果多个代理同时写入相同的别名，预期会出现交错，然后添加显式锁定。

**为什么使用符号链接而不是复制：** 移除重复文件漂移类别（内容永远不会在命名文件和别名之间发生分歧）。它不会移除陈旧性漂移——如果 `IDENTITY.md` 更改代理名称而未重新运行 heygen-avatar，`AVATAR-AGENT.md` 仍然指向*旧*命名文件。第 0 步不匹配并重新别名化将在下一次调用中处理；在此之前，别名是陈旧但指向有效的地方，不是损坏的。

**多代理工作区注意事项：** 每个工作区只有一个角色别名是最后写入者获胜。如果两个代理同时共享一个工作区并运行 heygen-avatar，只有最近运行的 identity 可以通过 `AVATAR-AGENT.md` 访问。两个代理的命名文件仍然存在。我们接受这个限制——多代理共享工作区不在 v1 范围内。

### 第 1 步 — 测试（可选）

如果用户想要看到他们的头像效果：

**MCP:** `create_video_agent(avatar_id=<avatar_id>, voice_id=<voice_id>, prompt=<greeting>)`
**CLI:** `heygen video-agent create --avatar-id <id> --voice-id <id> --prompt "..." --wait`

生成一个自然问候的视频（使用 `user_language`）。示例：英语 "Hi, I'm [name]. Nice to meet you!", 日语 "[name]です。はじめまして！", 西班牙语 "Hola, soy [name]. ¡Mucho gusto!", 韩语 "안녕하세요, [name]입니다. 만나서 반갑습니다!"

## 提供反馈（CLI 模式）

一旦头像和语音保存——或者如果您在过程中遇到阻力——运行一次每个任务：

```bash
heygen feedback --rating <1-5> --comment "<工作正常的内容，或者损坏了什么以及您尝试了什么>"
```

- `--rating`: `5` = 工作得很好 · `3` = 工作时有阻力 · `1` = 损坏/无法使用.
- `--comment`: 任何错误、过时的文档、缺失的标志或令人困惑的行为，加上触发它的命令或流程。

匿名，不需要 API 密钥，当分析被禁用 (`HEYGEN_NO_ANALYTICS` 或 `heygen config set analytics false`) 时不执行。这是 CLI 团队的主要信号通道——一个无声完成的运行告诉他们什么。**仅 CLI 模式：** 在 MCP 或 OpenClaw-plugin 模式中跳过（那些通过 MCP/plugin 表面路由，该表面没有反馈命令）。

## 迭代流程

当用户想要改进：

- **"调整提示"** → 模式 2 使用现有的 group_id (保留角色，添加新外观)。只有在他们说“完全重新开始”时才使用模式 1。
- **"添加新外观"** / **"不同的服装"** → 模式 2 使用现有的 group_id。将添加到 AVATAR 文件中的 Looks。
- **"尝试不同的语音"** → 返回到第 3 步
- **"完全重新开始"** → 模式 1，新角色。覆盖 HeyGen 部分。

**默认使用模式 2（在相同组下添加新外观）。** 只有当用户明确想要不同角色的身份时，才创建一个新的组。这可以保持账户整洁，并使外观可以在不同技能中重复使用。

每个迭代更新 AVATAR 文件。文件始终是信息的来源。

## 用户体验规则

**在检查点处交互，其他地方保持默默。** 在头像批准和语音选择处停止并等待。在检查点之间，默默工作——不要叙述推理或解释下一步。在语音选择后：保存 + 确认在一个消息中。

## 视频制作人员集成

`heygen-video` 读取 AVATAR 文件以获取 group_id 和 voice_id。解析顺序：

1. **命名请求** (“制作一个 Eve 的视频”) → 读取 `AVATAR-EVE.md`。
2. **代理自我引用** (“制作一个关于自己的视频”，“给我们一个视频更新”) → 读取 `AVATAR-AGENT.md`（符号链接到当前代理的命名文件）。
3. **用户自我引用** (“制作一个关于我的视频”，“我的视频更新”) → 读取 `AVATAR-USER.md`（符号链接到当前用户的命名文件）。
4. **没有 AVATAR 文件或符号链接** → 回退到默认头像或询问用户。

别名目标是解析时由操作系统解析的，因此消费技能只需 `cat AVATAR-AGENT.md` 就可以获取当前代理的头像。

## 错误处理

- 缺少 SOUL.md/IDENTITY.md → 对话式引导，从答案写入 AVATAR 文件
- API 失败 → 重试一次，然后要求用户检查 API 密钥
- 语音匹配不佳 → 显示所有可用语音，让用户浏览
- 资产上传失败 → 跳过参考图像，尝试仅基于提示创作
- 现有头像文件具有陈旧的 HeyGen ID → 提供重新生成或保留

📖 **已知问题、重试模式、损坏的语音预览、错误 → 操作映射 → [参考资料/troubleshooting.md](references/troubleshooting.md)**
