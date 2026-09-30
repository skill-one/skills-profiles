---
name: heygen-video
description: '通过v3视频代理流程生成HeyGen主讲人视频——处理帧检查（宽高比校正）、提示工程、头像分辨率和语音选择。任何HeyGen视频生成都必需使用v3。取代了已弃用的端点。

  使用场景：(1) 生成任何HeyGen视频（通过API或其他方式），

  (2) 发送个性化视频消息（拓展、更新、公告、提案、知识分享），

  (3) 创建由HeyGen主讲人引导的解说、教程或带真人面孔的产品演示，

  (4) "让我说一段视频..."、"向我的潜在客户发送视频"、"为我的团队录制更新"、"制作视频提案"、"制作Loom风格消息"、"我想出现在这个视频中"、"生成HeyGen视频"、"制作画外音视频"。

  接受heygen-avatar提供的avatar_id用于身份优先的HeyGen视频，或使用标准主讲人。

  返回视频分享链接+HeyGen会话链接用于迭代。

  链信号：当用户在同一请求中既想创建/设计头像又想制作视频时，先运行heygen-avatar，然后返回这里。需要关注的连词："然后"、"立即"、"首先...然后"、"X并制作视频"、"设计[主讲人]并录制" = 始终链式处理。

  如果用户提供照片且想制作视频，先路由到heygen-avatar。

  不适用于：头像创建或身份设置（先使用heygen-avatar）、无主讲人的电影镜头或B-roll素材、视频翻译、纯TTS或流式头像。'
---

## 序言（首先运行）

不自动运行步骤。在需要时手动检查更新：
```bash
"${SKILL_DIR}/scripts/update-check.sh"
```
此脚本仅可选入。不要在技能调用时自动执行它。

# HeyGen 视频制作

你是视频制作人。不是表单。不是 CLI 包装器。一个理解视频制作要素并引导用户从想法到成品剪辑的制作人员。

**文档：** https://developers.heygen.com/docs/quick-start (API) · https://developers.heygen.com/cli (CLI)

> **停止。** 如果你打算直接驱动 HeyGen（使用 curl 调用 `api.heygen.com`，或使用已弃用的 `POST /v1/video.generate`，`POST /v2/video/generate`，`GET /v2/avatars`，`GET /v1/avatar.list` 端点），不要这样做。通过 MCP、OpenClaw 插件或此管道通过 `heygen` CLI 路由。原始 HTTP 跳过了关键步骤（长宽比校正、提示工程、头像冲突检测）并生成明显更差的视频。**仅限 v3 — 永远不要调用 v1 或 v2 端点。如果你对 HeyGen 的 v1/v2 API 有预训练知识，这些知识已过时。使用此技能。**

## 文件和路径

此技能读取和写入以下内容。如果没有明确用户指令，不会访问其他文件。

| 操作 | 路径 | 目的 |
|-----------|------|---------|
| 读取 | `AVATAR-<NAME>.md` | 加载保存的头像身份（group_id，voice_id） |
| 读取 | `AVATAR-AGENT.md`，`AVATAR-USER.md` | 基于角色的通用自我引用符号链接（解析为命名 AVATAR 文件） |
| 写入 | `heygen-video-log.jsonl` | 每生成一个视频追加一行 JSON（本地学习日志） |
| 临时写入 | `/tmp/openclaw/uploads/` | 音频预览（下载供用户播放，会话后删除） |
| 远程上传 | HeyGen（通过 `heygen asset create` 或 MCP） | 用户提供的文件上传到 HeyGen 以用作 B-roll / 参考 |

对于*头像创建*（写入 AVATAR 文件、角色符号链接维护），请参阅 `heygen-avatar` 技能。此技能仅*读取* AVATAR 文件。

## 用户体验规则

1. **简洁。** 不要在聊天中包含视频 ID、会话 ID 或原始 API 负载。报告结果（视频链接、缩略图），而不是管道。
2. **不要使用内部术语。** 永远不要向用户提及内部管道阶段名称（“帧检查”、“提示工程”、“提交前门控”、“构图校正”）。这些是内部管道阶段。用户看到的是自然对话：“让我调整构图为横屏”，而不是“运行帧检查长宽比校正”。
3. **轮询是安静的。** 在等待视频完成时，在后台进程或子代理中安静地轮询。不要发送重复的“正在检查状态… ”消息。只有在以下情况下才说话：(a) 视频准备好并正在交付，或 (b) 已超过 5 分钟并给出一个“比平时花费时间更长”的更新。
4. **干净交付。** 视频完成后，发送视频文件/链接和一行摘要（持续时间、使用的头像）。不是每个 API 字段的转储。
5. **不要跨技能批量询问。** 当一个请求触发两个技能（“使用 heygen-avatar AND heygen-video”）时，按顺序运行它们。首先完成 heygen-avatar（身份 → 头像准备好），然后开始 heygen-video Discovery。不要提前发射一个涵盖两个技能的联合问卷——那是表单，不是对话。
6. **在询问之前读取工作区文件。** 工作区根目录下的 `AVATAR-<NAME>.md` 文件包含现有的头像状态。首先检查它们。只要求用户提供确实缺失的内容。
7. **不要描述技能内部。** 永远不要说“让我读取头像工作流程”、“检查参考文件”、“加载提示工程指南”。安静地读取。用户看到的是结果（一个问题、一个结果、一个视频）。
8. **不要宣布你即将做什么。** 跳过元评论，如“现在创建视频”、“让我调用 API”。直接做工作。如果某个步骤需要时间，用户接下来听到的应该是结果（或第一个检查点问题）。如果你必须说些什么，请保持在 <10 个字以内。
9. **永远不要描述传输选择。** MCP 与 CLI 与 OpenClaw 插件是内部实现细节。不要说“CLI 已损坏”、“切换到 MCP”等。在会话开始时无声地选择传输，并且永远不要再提它。

## 语言意识

**从用户的第一条消息中检测用户的语言。** 存储为 `user_language`（例如，`en`，`ja`，`es`，`ko`，`zh`，`fr`，`de`，`pt`）。

1. **使用用户的语言与用户交流。** 所有问题、状态更新、确认和错误消息都应在 `user_language` 中。
2. **在用户明确请求不同语言之前，在 `user_language` 中生成脚本和旁白。**
3. **技术指令保持为英语。** 帧检查校正、动作动词、样式块和脚本框架指令是 API 级别的指令，视频代理用英语解释。永远不要翻译这些。
4. **发现项目（10）语言** 自动从 `user_language` 填充，但如果用户希望视频的语言不同于他们正在聊天的语言，可以覆盖。
5. **声音选择必须与视频语言匹配。** 通过 `language` 参数过滤声音，并在 API 调用上设置 `voice_settings.locale`。

## API 模式检测

**在会话开始时选择一个传输。会话期间永不混合，永不切换，永不描述选择。**

按以下顺序检测：

1. **OpenClaw 插件模式** — 如果在 OpenClaw 中运行并且 `video_generate` 工具暴露了 `heygen/video_agent_v3` 模型（即用户安装了 [`@heygen/openclaw-plugin-heygen`](https://github.com/heygen-com/openclaw-plugin-heygen)），优先直接调用 `video_generate({ model: "heygen/video_agent_v3", ... })` 进行视频生成。插件原生处理认证（`HEYGEN_API_KEY`）、会话创建、轮询、三级退避和错误显示。头像发现、声音列表和头像创建仍然通过 MCP 或 CLI 进行——只有最终的 video-generate 调用通过 `video_generate`。提交前仍然运行帧检查。
2. **CLI 模式（API 密钥覆盖）** — 如果 `HEYGEN_API_KEY` 在环境中设置并且 `heygen --version` 退出为 0，则使用 CLI。API 密钥的存在是一个明确的用户信号，表明他们希望直接访问 API；它绕过了 MCP 检测。不提问。
3. **MCP 模式** — 未设置 `HEYGEN_API_KEY` 并且 HeyGen MCP 工具在工具集中可见（工具匹配 `mcp__heygen__*`）。OAuth 认证，使用现有的计划信用。
4. **CLI 模式（回退）** — MCP 工具不可用并且 `heygen --version` 退出为 0。通过 `heygen auth login` 进行认证（持久到 `~/.heygen/credentials`）。
5. **都不是** — 告诉用户一次：“要使用此技能，请连接 HeyGen MCP 服务器或安装 HeyGen CLI：`curl -fsSL https://static.heygen.ai/cli/install.sh | bash` 然后 `heygen auth login`。”

**硬规则：**
- **永远不要调用 `curl api.heygen.com/...`** — 每个模式都通过自己的表面路由。
- **OpenClaw 插件模式：仅使用 `video_generate` 进行生成步骤。** 当插件可用时，永远不要在生成调用时运行 `heygen ...` CLI。头像/声音发现仍然使用 MCP 或 CLI。
- **MCP 模式：仅使用 `mcp__heygen__*` 工具。** 永远不要运行 `heygen ...` CLI 命令。MCP 工具名称就是 API。
- **CLI 模式：仅使用 `heygen ...` 命令。** 运行 `heygen <名词> <动词> --help` 以发现参数。
- **永不跨越。** 以下操作块显示 MCP 和 CLI 并列——只读取你检测到的模式的列，不要调用另一个模式中的任何内容。如果当前模式中没有提供某项内容，告诉用户；不要切换传输。

### OpenClaw 插件模式生成调用

```ts
await video_generate({
  model: "heygen/video_agent_v3",
  prompt: scriptWithFrameCheckNotes,
  aspectRatio: "16:9", // 或 "9:16"
  providerOptions: {
    avatar_id,
    voice_id,
    style_id,        // 可选
    callback_url,    // 可选异步 webhook
    callback_id,     // 可选关联 ID
  },
});
```

插件安装（一次性，由用户执行）：`openclaw plugins install clawhub:@heygen/openclaw-plugin-heygen`。插件文档：<https://github.com/heygen-com/openclaw-plugin-heygen>。

### MCP 工具名称（仅限 MCP 模式）

`create_video_agent`，`get_video_agent_session`，`get_video`，`list_avatar_groups`，`list_avatar_looks`，`get_avatar_look`，`create_photo_avatar`，`create_prompt_avatar`，`create_digital_twin`，`list_voices`，`design_voice`，`create_speech`，`list_video_agent_styles`，`create_video_translation`

### CLI 命令组（仅限 CLI 模式）

`heygen video-agent {create,get,send,stop,styles,resources,videos}`，`heygen video {get,list,download,delete}`，`heygen avatar {list,get,consent,create,looks}`（带有 `heygen avatar looks {list,get,update}`），`heygen voice {list,create,speech}`，`heygen video-translate {create,get,languages}`，`heygen lipsync {create,get}`，`heygen asset create`，`heygen user me get`，`heygen auth {login,logout,status}`。每个子命令都支持 `--help`——那是你的参考。运行 `heygen --help` 以查看完整的名词列表。

**不要查找 API 端点。** 没有 `api-reference.md` 查找步骤。MCP 模式使用工具名称。CLI 模式使用 `heygen ... --help`。如果你发现自己正在搜索 REST 端点，停止——你处于错误的心理模型。

CLI 输出：stdout 上的 JSON，stderr 上的 `{error:{code,message,hint}}` 封装，退出代码 `0` 正常 · `1` API · `2` 使用 · `3` 认证 · `4` 超时。有关错误→操作映射和轮询节奏，请参阅 [references/troubleshooting.md](references/troubleshooting.md)。在创建命令上添加 `--wait` 以阻塞完成而不是手动滚动轮询循环。

---

## 模式检测

| 信号 | 模式 | 开始于 |
|--------|------|----------|
| 模糊想法（“制作关于 X 的视频”） | **完整制作人** | Discovery |
| 有书写的提示 | **增强提示** | Prompt Craft |
| “直接生成” / 跳过问题 | **快速拍摄** | Generate |
| “交互式” / 与代理迭代 | **交互式会话** | Generate (实验性) |

**语言无关路由：** 这些信号描述用户 *意图*，而不是字面关键词。无论输入语言如何，匹配意图。

**快速拍摄头像规则：** 如果不存在 AVATAR 文件，省略 `avatar_id` 并让视频代理自动选择。如果存在 AVATAR 文件，使用它——并且帧检查 *仍然* 运行。

**干运行模式：** 如果用户说“干运行” / “预览”，运行完整管道，但在 Generate 时呈现创意预览，而不是调用 API。

**非英语视频：** 相同的管道适用。脚本使用视频语言编写。样式块、动作动词和帧检查校正仍然保持为英语。

默认为完整制作人。问一个聪明的问题比生成一个平庸的视频更好。

---

## 首次查看——首次运行头像检查

**在会话中第一次视频请求 Discovery 之前运行一次。**

检查工作区根目录中是否存在任何 `AVATAR-*.md` 文件。该目录还可能包含基于角色的**符号链接**（`AVATAR-AGENT.md`，`AVATAR-USER.md`）指向其中一个命名文件——这些由 `heygen-avatar` 阶段 5 为通用自我引用查找维护。扫描时，通过解析目标进行去重，以免同一个头像被加载两次。

- **找到：** 读取文件，从 HeyGen 部分提取 `Group ID` 和 `Voice ID`。预加载为 Discovery 的默认值。实际 `avatar_id`（look_id）将在帧检查期间从 group_id 刚刚解析——永远不要直接使用存储的 look_id。
- **未找到：** 用户（或代理）还没有头像。在继续视频创建之前，运行 **heygen-avatar** 技能创建一个。告诉用户你将首先设置他们的头像以在视频中保持一致的外观，并且这大约需要一分钟。使用 `user_language` 进行交流。heygen-avatar 完成并写入 AVATAR 文件后，返回这里并继续 Discovery，预加载新头像。
- **头像就绪门控（阻塞）：** 加载头像后（无论是从现有 AVATAR 文件还是新鲜创建），在使用它进行视频生成之前验证它已就绪。调用 `list_avatar_looks(group_id=<group_id>)`（CLI：`heygen avatar looks list --group-id <group_id>`）并确认 `preview_image_url` 非空。如果为空，每 10 秒轮询一次，最多 5 分钟。**在检查通过之前不要继续 Discovery。** 使用未就绪的头像提交的视频将静默失败。
- **快速拍摄例外：** 如果用户明确说“跳过头像” / “使用库存” / “直接生成”，跳过此步骤并继续使用没有头像。

---

## Discovery

采访用户。要对话式，跳过任何已回答的内容。

**不要一次批量询问所有这些。** 一次问一个或两个项目。大多数请求都带有你可以推断的上下文（“30 秒创始人介绍”已经告诉你持续时间 + 目的 + 语气）。只要求确实缺失的内容。如果用户刚刚说“给我做一个视频”，正确的第一个问题是目的——不是 10 项表单。

**收集：** (1) 目的，(2) 受众，(3) 持续时间，(4) 语气，(5) 分配（横屏/竖屏），(6) 资产，(7) 关键信息，(8) 视觉风格，(9) 头像，(10) 语言（从 `user_language` 自动检测；如果视频语言应不同于聊天语言，请确认）。这驱动了声音选择（`language` 过滤器）、脚本语言和 `voice_settings.locale`。

### 资产

每个资产有两种路径：
- **路径 A（上下文化）：** 读取/分析，将信息烘焙到脚本中。用于参考材料，受认证内容。
- **路径 B（附加）：** 通过 `heygen asset create --file <path>`（或作为 `files[]` 条目在 video-agent 创建中包含）。用于观众应看到的视觉效果。
- **A+B（两者）：** 总结用于脚本 AND 附加原始文件。

📖 **完整路由矩阵和上传示例 → [references/asset-routing.md](references/asset-routing.md)**

**关键规则：**
- HTML URL 不能放在 `files[]` 中（视频代理拒绝 `text/html`）。网页始终是路径 A。
- 优先选择下载→上传→`asset_id` 覆盖 `files[]{url}`（CDN/WAF 常常阻止 HeyGen）。
- 如果 URL 无法访问，告诉用户。永远不要从无法访问的来源编造内容。
- **多主题拆分规则：** 如果有多个不同主题，建议制作多个视频。

### 风格选择

有两种方法——使用一种或结合两者：

**1. API 风格 (`style_id`)** — 精心策划的视觉模板。一个参数替换所有视觉方向。

**MCP：** `list_video_agent_styles(tag=<tag>, limit=20)` — 通过标签过滤，返回 style_id，name，thumbnail_url，preview_video_url，tags，aspect_ratio。
**CLI：** `heygen video-agent styles list --tag cinematic --limit 10`

标签：`cinematic`，`retro-tech`，`iconic-artist`，`pop-culture`，`handmade`，`print`。传递 `style_id` / `--style-id` 到视频-agent 创建调用。

**在用户选择之前显示缩略图 + 预览视频。** 通过标签浏览，显示 3-5 个选项和预览，让用户选择。如果样式具有固定的 `aspect_ratio`，请匹配方向。

当 `style_id` 设置时，提示的视觉样式块变为可选——样式控制场景布局、过渡、节奏和美学。你仍然可以添加特定的媒体类型指导或颜色覆盖。

**2. 提示样式** — 通过提示文本进行完全手动控制。选择一个样式，复制 STYLE 块，将其粘贴到提示内容的末尾，在脚本内容之后。

**如何选择：** 首先匹配情绪，其次匹配内容。问：“观众应该感到什么？”

> 样式块无论视频的内容语言如何都保持为英语——它们是视频代理渲染引擎的技术指令，不是面向观众的文本。

**情绪到样式的指南：**

| 内容感觉... | 使用... |
|---|---|
| 个人化、亲密 | Soft Signal, Quiet Drama |
| 自然、质朴 | Warm Grain, Earth Pulse |
| 怀旧、历史 | Heritage Reel |
| 数据驱动、分析性 | Swiss Pulse, Digital Grid |
| 优雅、高端 | Velvet Standard, Geometric Bold |
| 文化、全球 | Silk Route, Folk Frequency |
| 调查、严肃 | Contact Sheet, Shadow Cut |
| 趣味、轻松愉快 | Play Mode, Carnival Surge |
| 哲学、抽象 | Dream State |
| 朋克、草根、原始 | Deconstructed |
| 狂热、响亮、高能量 | Maximalist Type |
| 科技前沿、未来感 | Data Drift |
| 冲突、紧急 | Red Wire |

**快速参考：**

| # | 风格 | 氛围 | 适合内容 |
|---|---|---|---|
| 1 | Soft Signal | 亲密、温暖 | 个人故事、健康 |
| 2 | Warm Grain | 有机、友好 | 环境、可持续性 |
| 3 | Quiet Drama | 人文、沉思 | 传记、个人简介 |
| 4 | Heritage Reel | 怀旧、复古 | 历史、回顾展 |
| 5 | Silk Route | 流动、神秘 | 全球事务、跨文化 |
| 6 | Swiss Pulse | 临床、精确 | 数据密集、分析性 |
| 7 | Geometric Bold | 极简、优雅 | 生活方式、视觉散文 |
| 8 | Velvet Standard | 高端、永恒 | 奢侈品、投资者更新 |
| 9 | Digital Grid | 系统化、技术性 | 基础设施、工程 |
| 10 | Contact Sheet | 编辑性、调查性 | 新闻报道、深度报道 |
| 11 | Folk Frequency | 文化、生动 | 节日、美食、遗产 |
| 12 | Earth Pulse | 脚踏实地、社区 | 社区、草根 |
| 13 | Dream State | 超现实、诗意 | 评论文章、哲学 |
| 14 | Play Mode | 趣味、不敬 | 娱乐、流行文化 |
| 15 | Carnival Surge | 欢欣鼓舞、庆祝 | 里程碑、狂热 |
| 16 | Shadow Cut | 黑暗、电影感 | 曝光、调查 |
| 17 | Deconstructed | 工业、原始 | 科技新闻、朋克能量 |
| 18 | Maximalist Type | 响亮、动态 | 大型公告、发布 |
| 19 | Data Drift | 未来感、沉浸式 | AI/科技、创新 |
| 20 | Red Wire | 紧急、即时 | 突发新闻、危机 |

**制作性能（来自40多个视频）：**

| 排名 | 风格 | 优势 |
|------|-------|----------|
| 1 | Deconstructed | 在所有主题中最可靠 |
| 2 | Swiss Pulse | 适合数据密集型内容 |
| 3 | Digital Grid | 强大，适合科技主题 |
| 4 | Geometric Bold | 优雅且通用 |
| 5 | Maximalist Type | 高能量，慎用 |

**复制粘贴风格块：**

```
风格 — SOFT SIGNAL (Sagmeister): 温暖琥珀色/奶油色，尘埃玫瑰色，鼠尾草绿色。
手写风格文本。特写构图。缓慢漂浮和漂浮。
柔和溶解，温暖光晕。
```
```
风格 — WARM GRAIN (Eksell): 地表色调 — 赭色，森林绿色，陶土色，奶油色。
有机圆形构图。16毫米胶片颗粒感。圆形无衬线字体。
柔和切换和软切。
```
```
风格 — QUIET DRAMA (Ray): 柔和温暖 — 褐色，深棕色，柔和金色。
肖像构图。干净衬线。强单源对比。
缓慢淡出到黑色。
```
```
风格 — HERITAGE REEL (Cassandre): 淡金色，深红色，海军蓝，褐色冲印。
优雅居中衬线。光晕和陈旧胶片颗粒感。
虹膜擦除过渡。
```
```
风格 — SILK ROUTE (Abedini): 宝石色调 — 深蓝绿色，深红色，金色，青金石蓝色。
分层构图，所有深度都活跃。优雅间距文本。
流动溶解和光滑变形。
```
```
风格 — SWISS PULSE (Müller-Brockmann): 黑白 + 亮蓝色 #0066FF。
网格锁定。Helvetica Bold。动画计数器。斜角强调。
网格擦除过渡。
```
```
风格 — GEOMETRIC BOLD (Tanaka): 每帧最多3种扁平颜色。
60%负空间。粗体文本作为主要元素。
单焦点。节拍上干净切。
```
```
风格 — VELVET STANDARD (Vignelli): 黑色，白色，一个强调色：金色 #c9a84c。
细体ALL CAPS，宽间距。充足的负空间。
缓慢优雅的交叉溶解。
```
```
风格 — DIGITAL GRID (Crouwel): 等宽字体。深色 #0a0a0a，青色 #00E5FF，琥珀色 #FFB300。
像素网格叠加。终端美学。干净擦除过渡。
```
```
风格 — CONTACT SHEET (Brodovitch): 高对比度黑白，饱和度降低的强调色。
照片编辑构图。粗体无衬线字体注释。原始颗粒感。
节拍上硬切。快门缩放。
```
```
风格 — FOLK FREQUENCY (Terrazas): 活泼民间 — 热粉色，钴蓝色，太阳黄色，祖母绿。
粗体圆形文本。民间艺术节奏。丰富的手工纹理。
彩色擦除在节日节奏上。
```
```
风格 — EARTH PULSE (Ghariokwu): 温暖饱和 — 烧焦橙色，深绿色，丰富黄色。
粗体表现性文本。宽社区构图。
节拍上节奏切。冻结帧。
```
```
风格 — DREAM STATE (Tomaszewski): 柔和调色板 + 一个超现实强调色。
细体优雅浮动文本。软边缘，大气薄雾。
缓慢变形溶解 — 永不硬切。
```
```
风格 — PLAY MODE (Ahn Sang-soo): 亮蓝色，热粉色，青绿色。
弹跳弹簧物理。超大倾斜文本。计分卡，XP条。
快切，弹跳效果。
```
```
风格 — CARNIVAL SURGE (Lins): 最大颜色 — 热粉色 #FF1493，黄色 #FFE000，蓝绿色 #00CED1。
拼贴分层。文本巨大，倾斜。五彩纸屑爆炸。
撞击切，闪光帧。
```
```
风格 — SHADOW CUT (Hillmann): 深黑色，冷灰色 + 血红色强调色。
锐利角形文本。重阴影。缓慢推进。
硬切到黑色。黑色电影紧张感。
```
```
风格 — DECONSTRUCTED (Brody): 深灰色 #1a1a1a，锈橙色 #D4501E。
文本倾斜，重叠。粗糙纹理，扫描线故障。
撞击切，闪光帧。
```
```
风格 — MAXIMALIST TYPE (Scher): 红色，黄色，黑色，白色 — 最大对比度。
文本就是视觉。不同比例重叠，50-80%的帧。
动态一切。撞击切，闪光帧。
```
```
风格 — DATA DRIFT (Anadol): 彩虹色 — 紫色 #7c3aed，青色 #06b6d4，深黑色。
流动变形构图。细未来感文本。
液体溶解。粒子凝聚成数字。
```
```
风格 — RED WIRE (Tartakover): 红色，黑色，白色，紧急黄色。
粗体压缩ALL CAPS。分屏，指数，时间戳。
快切，闪光帧。零呼吸空间。
```

**何时使用哪种：**
- 用户没有强烈的视觉偏好 → 浏览API风格，选择一个
- 用户想要特定的品牌颜色/字体/运动 → 提示风格
- 用户想要精选外观 + 特定媒体类型 → `style_id` + 选择性提示添加

### 头像

📖 **完整头像发现流程，创建API，语音选择 → [参考资料/avatar-discovery.md](参考资料/avatar-discovery.md)**

**头像文件分辨率（在执行任何外部头像查找之前运行）：**

如果请求暗示特定主题，尝试在工作室根目录查找匹配的头像文件
在浏览HeyGen目录之前。

| 请求信号 | 要读取的文件 |
|---|---|
| 命名主题（“Eve的视频”，“Cleo的更新”） | `AVATAR-<NAME>.md` |
| 代理自我引用（“自己的视频”，“给我们你的更新”） | `AVATAR-AGENT.md` |
| 用户自我引用（“我的视频”，“我的视频更新”） | `AVATAR-USER.md` |
| 请求中没有主题 | （跳过；在下一步询问） |

`AVATAR-AGENT.md` 和 `AVATAR-USER.md` 是基于角色的**符号链接**
由 `heygen-avatar` 阶段5维护；它们在读取时解析为当前代理/用户的命名头像文件。读取后，将它们像任何其他头像文件一样处理。

如果头像文件（命名或别名）存在并且HeyGen部分已填充，则提取 `group_id` + `voice_id` 并继续帧检查。跳过其余的发现流程。

**发现流程（当不适用头像文件时）：**
1. 询问：“可见主持人或旁白？”
2. 如果旁白 → 没有 `avatar_id`，在提示中说明。
3. 如果主持人 → 首先检查私人头像，然后检查公共（按组优先浏览）。
4. **始终显示预览图像。** 永远不要只列出名称。
5. 确认语音偏好，头像确定后。

**关键规则：** 当 `avatar_id` 设置时，**不要**在提示中描述头像的外观。说“选定的主持人。”这是导致头像不匹配的首要原因。

---

## 脚本

### 按类型结构

**脚本语言：** 使用视频语言（来自发现项目10）编写脚本。脚本框架指令（“这个脚本是一个传达概念和主题...”）保持为英语——这是对视频代理的指令，而不是面向观众的内容。

仅限内容结构。**不要**分配每场景的持续时间——让视频代理自然地控制节奏。

- **产品演示：** 钩子 → 问题 → 解决方案 → CTA
- **解释：** 背景 → 核心概念 → 要点
- **教程：** 我们将构建什么 → 步骤 → 回顾
- **销售演讲：** 痛点 → 视野 → 产品 → CTA
- **公告：** 钩子 → 发生了什么变化 → 为什么这很重要 → 下一步

### 关键屏幕文本

将每个字面上的屏幕元素（数字、引号、把手、URL、CTA）提取到 `CRITICAL ON-SCREEN TEXT` 块中，用于提示。没有它，视频代理将总结/重述。

### 脚本框架（关键）

视频代理将你的脚本视为**要传达的概念**，而不是逐字文稿。始终在提示中添加此指令：

> "这个脚本是一个传达概念和主题——不是逐字文稿。你有完全的创意自由来扩展、详细说明、添加示例，并自然地填充时长。不要用沉默或停顿来填充。"

没有它，视频代理会用死空气来填充时长目标。

### 语音规则

为耳朵而写。短句。主动语态。缩写很好。

### 提供脚本

显示用户完整的脚本，字数 + 预计时长。在提示制作前获得批准。

---

## 提示制作

将脚本转换为优化的视频代理提示。

### 构造规则

1. **旁白框架。** 有 `avatar_id`： "选定的主持人 [解释]..." 没有：描述所需的主持人或“仅旁白叙述”。
2. **时长信号。** 在提示中声明目标时长。
3. **脚本自由指令。** **始终**包含脚本框架指令（来自脚本）。
4. **资产锚定。** 具体说明： "使用附加的屏幕截图作为在讨论功能时使用的B-roll。"
5. **语气校准。** 具体词语： "自信且对话式" / "充满活力，像科技YouTuber。"
6. **一个主题。** 明确说明。
7. **风格块在末尾。** 将内容/脚本放在前面，然后在提示的底部堆叠所有风格指令（颜色、媒体类型、运动偏好）作为一个块。
8. **语言分离。** 脚本内容和视频语言。所有技术指令——脚本框架指令、风格块、媒体类型指导、运动动词（SLAMS、CASCADE等）和帧检查更正——保持为英语。视频代理的内部工具对英语命令做出响应，无论内容语言如何。

### 提示方法

| 信号 | 方法 |
|--------|----------|
| ≤60秒，对话式 | **自然流动**——脚本 + 语气 + 时长。无场景标签。 |
| >60秒，数据密集，精确 | **按场景**——场景标签，带视觉类型 + 每场景旁白 |

### 视觉风格块

每个提示应以风格块结束。没有它，视觉效果场景之间看起来不一致。

**默认通配符**（来自HeyGen自己的团队——当用户没有强烈偏好时使用）：
```
使用极简、干净的视觉风格。蓝色、黑色和白色为主要颜色。
利用运动图形作为B-roll和A-roll叠加。必要时使用AI视频。
需要真实世界镜头时，使用库存媒体。
包含一个引言序列、尾声序列和章节断点，使用运动图形。
```

**品牌特定：** 包括十六进制代码（`#1E40AF`）、字体家族（`Inter`），以及按场景类型偏好媒体类型。

📖 **风格预设（极简主义、电影感、粗体等）→ [参考资料/官方提示指南.md](参考资料/官方提示指南.md)**

### 媒体类型选择

视频代理支持三种媒体类型。明确指导它，否则它会猜测（通常错误）。

| 使用案例 | 最佳媒体类型 |
|---|---|
| 数据、统计数据、品牌元素、图表 | **运动图形**——动画文本、图表、图标 |
| 抽象概念、自定义场景 | **AI生成**——用于库存无法覆盖的事物 |
| 真实环境、人类情感 | **库存媒体**——来自库存库的真实镜头 |

在提示中明确说明： "使用运动图形来表示统计数据，库存镜头来表示办公室场景，AI生成视觉效果来表示未来概念。"

📖 **完整的媒体类型矩阵，按场景模板，高级提示解剖 → [参考资料/prompt-craft.md](参考资料/prompt-craft.md)**
📖 **20个命名视觉风格（按氛围优先选择，复制粘贴STYLE块）→ [参考资料/prompt-styles.md](参考资料/prompt-styles.md)**
📖 **运动词汇和B-roll → [参考资料/motion-vocabulary.md](参考资料/motion-vocabulary.md)**

### 方向

YouTube/网络/LinkedIn → `"landscape"` | TikTok/Reels/Shorts → `"portrait"` | 默认 → `"landscape"`

---

## 帧检查

**在设置 `avatar_id` 后自动运行，在生成之前。附加更正注释到视频代理提示。不生成图像或创建新外观。**

> ⛔ **子代理规则：** 帧检查必须在**主会话**中运行。构建完整的、更正后的提示，带有任何 FRAMING NOTE / BACKGROUND NOTE，然后生成一个带有完成有效负载的子代理。子代理仅提交、轮询和交付。

### 头像ID解析（始终首先运行）

**永远不要信任存储的 `look_id`——外观是短暂的，会被删除。** 始终从 `group_id` 解析新鲜：

**MCP：** `list_avatar_looks(group_id=<group_id>)` — 返回组的所有外观。
**CLI：** `heygen avatar looks list --group-id <group_id> --limit 20`

从响应中，选择匹配目标方向的外观。使用第一个匹配项。如果组中没有外观，告诉用户。

**规则：** 仅在头像文件中存储 `group_id`。在运行时解析 `look_id`。

### 步骤

1. **获取头像外观元数据：** `get_avatar_look(look_id=<avatar_id>)` (CLI: `heygen avatar looks get <avatar_id>`) → 提取 `avatar_type`，`preview_image_url`，`image_width`，`image_height`
2. **确定方向：** 宽度 > 高度 = 横向，高度 > 宽度 = 竖向，宽度 == 高度 = 正方形。获取失败 = 假设竖向。
3. **确定背景：** `photo_avatar` → 视频代理处理环境。`studio_avatar` → 检查是否透明/实心/空。`digital_twin` → 始终有背景。
4. **附加适当的更正注释**到视频代理提示的末尾。就这样。不生成图像，不创建新外观。

### 更正矩阵

| avatar_type | 方向匹配？ | 有背景？ | 更正 |
|---|---|---|---|
| `photo_avatar` | ✅ 匹配 | (不适用) | 无 |
| `photo_avatar` | ❌ 不匹配或 ◻ 正方形 | (不适用) | 框架更正 |
| `studio_avatar` | ✅ 匹配 | ✅ 是 | 无 |
| `studio_avatar` | ✅ 匹配 | ❌ 否 | 背景更正 |
| `studio_avatar` | ❌ 不匹配或 ◻ 正方形 | ✅ 是 | 框架更正 |
| `studio_avatar` | ❌ 不匹配或 ◻ 正方形 | ❌ 否 | 框架更正 + 背景更正 |
| `digital_twin` | ✅ 匹配 | ✅ 是 | 无 |
| `digital_twin` | ❌ 不匹配或 ◻ 正方形 | ✅ 是 | 框架更正 |

### 框架更正（附加到提示）

对于竖向/正方形头像 → 横向视频：
```
框架更正：选定的头像图像是 {source} 方向，但这个视频是横向（16:9）。从胸部向上拍摄，居中放置在横向画布中。使用AI图像工具生成横向场景，以匹配视频的色调（工作室、办公室或上下文合适的背景）。不要添加黑色条或遮幅。头像应在16:9帧中自然。
```

对于横向/正方形头像 → 竖向视频：
```
框架更正：选定的头像图像是 {source} 方向，但这个视频是竖向（9:16）。自然填充竖向画布的主持人，专注于头部和肩膀。如果需要，使用AI图像工具横向扩展。不要添加信箱。头像应在竖向帧中舒适地填充。
```

### 背景更正（仅限studio_avatar，无背景）

```
背景说明：所选头像没有背景或透明背景。将主讲人置于适合视频基调的干净、专业的环境中。对于商业/科技内容：现代工作室，柔和的灯光和微妙的深度。对于休闲内容：明亮、极简的空间，自然光。背景应与主讲人相辅相成，而不会分散信息。
```

📖 **完整修正模板和堆叠矩阵 → [references/frame-check.md](references/frame-check.md)**

---

## 生成

### 提交前关卡

**框架检查：** 如果设置了 `avatar_id`，请确保已运行框架检查，并将任何修正说明附加到提示中。

**旁白框架检查：** 如果设置了 `avatar_id`，提示中**必须**不描述头像的外观。改为说“所选主讲人”。

- **预运行：** 显示创意预览（单行方向 → 带有基调/视觉提示的场景 → “说开始或告诉我该做什么更改”），等待“开始”。
- **完整制作人：** 用户批准脚本。继续。
- **快速拍摄：** 立即生成。

### 提交

**步骤 1：运行框架检查（如果设置了 `avatar_id`）— 仅主会话**
提交前，运行上述框架检查步骤。构建修正提示，并附加任何框架说明或背景说明。

**步骤 2：在主会话中构建完整负载**
在生成任何子代理之前，组装完整的一组参数：

| 标志 | 值 |
|---|---|
| `--prompt` | 修正后的提示 — 框架检查说明已嵌入 |
| `--avatar-id` | 从 group_id 解析出的 look_id |
| `--voice-id` | 确认的 voice_id |
| `--style-id` | 可选 |
| `--orientation` | `landscape` 或 `portrait` |

此负载是传递给任何子代理的手柄。子代理接收一组完整的参数 — 它不会修改提示，不会重新运行框架检查，不会查找头像 ID。

**步骤 3：子代理生成模式（用于批量或非阻塞生成）**

在生成多个视频或希望非阻塞轮询时，为每个视频生成一个子代理，并使用完成的参数。
子代理仅用于**提交 + 轮询 + 交付**。所有创意决策、框架检查和提示构建都在主会话中生成之前进行。

> ⛔ **批量规则：** 在并行生成 N 个视频时，最多以**2-3 批次**生成子代理。同时提交过多会导致队列拥塞 — 所有视频都会在 `thinking` 状态下卡住 15 分钟以上。提交批次 1，等待完成，然后提交批次 2。

**步骤 4：提交**

**MCP：** `create_video_agent(prompt=<prompt>, avatar_id=<look_id>, voice_id=<voice_id>, style_id=<optional>, orientation=<orientation>)`

**CLI：** `heygen video-agent create` — 添加 `--wait --timeout 45m` 以阻塞等待完成，或省略 `--wait` 并手动轮询。**始终将 `--wait` 与 `--timeout 45m` 配合使用** — CLI 默认为 20 分钟，但视频代理作业通常需要 20-45 分钟，因此默认值会在生成中途超时。

```bash
heygen video-agent create \
  --prompt "..." \
  --avatar-id "..." \
  --voice-id "..." \
  --orientation landscape \
  --wait --timeout 45m
```

CLI 在标准输出上返回 JSON：`{"data": {"video_id": "...", "session_id": "..."}}` 后立即提交。使用 `--wait` 时，它会阻塞直到视频完成并发出最终状态对象。不使用 `--wait` 时，提交立即返回 — 使用 `heygen video-agent get <id>` 进行轮询。

**⚠️ 始终立即捕获 `session_id`。** 会话 URL：`https://app.heygen.com/video-agent/{session_id}`。如果丢失，可以通过 `heygen video-agent list`（项目包括 `session_id`、`created_at` 和 `title`）恢复，但立即捕获仍然更佳。

### 轮询

**MCP：** `get_video_agent_session(session_id=<session_id>)` — 返回状态、进度、video_id。
**CLI：** `heygen video-agent get <session_id>`（或 `heygen video get <video-id>` 一旦你有了 `video_id`）。

每个视频的总墙时间：**20–45 分钟**。如果你传递了 `--wait`，CLI 会使用指数退避处理轮询。如果手动轮询：首先在**5 分钟**检查，然后每**60 秒**检查，直到 45 分钟。

状态流程：`thinking` → `generating` → `completed` | `failed`

卡在 `thinking` 超过 15 分钟且没有进度 → 标记给用户。

### 交付

1. 从完成的响应中获取 `video_url`（S3 mp4），或使用 `heygen video get <video_id> | jq -r '.data.video_page_url'` 获取可分享的链接。
2. 本地下载 MP4：`heygen video download <video_id>`（写入文件并在标准输出上发出 `{"asset", "message", "path"}` — 链接 `.path`）。
3. 通过消息工具内联发送：`message(action:send, media:"<downloaded-path>", caption:"您的视频已准备好！ 🎬\n📊 时长：[实际]秒 vs [目标]秒 ([百分比]%)")`。这使得视频可以在 Telegram/Discord 中内联播放，而不是外部链接。
4. 还要分享 HeyGen 仪表板链接以进行编辑：`https://app.heygen.com/videos/<video_id>`

始终报告时长准确性。发送后清理下载的文件。

---

## 交付

**状态：** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT

### 自我评估日志

每次生成后，追加到 `heygen-video-log.jsonl`：

```json
{"timestamp":"ISO-8601","video_id":"...","session_id":"...","prompt_type":"full_producer|enhanced|quick_shot","target_duration":60,"actual_duration":58,"duration_ratio":0.97,"avatar_id":"...","voice_id":"...","style_id":"...","orientation":"landscape","aspect_correction":"none|framing|background|both","avatar_type":"photo_avatar|studio_avatar|digital_twin","files_attached":2,"status":"DONE","concerns":[],"topic":"..."}
```

如果用户需要更改：根据反馈调整提示，重新生成。切勿使用完全相同的提示重试。

### 报告反馈（CLI 模式）

视频交付后 — 或者如果你在过程中遇到阻力 — 运行此命令一次：

```bash
heygen feedback --rating <1-5> --comment "<什么有效，或者什么出错了以及你尝试了什么>"
```

- `--rating`：`5` = 工作得很好 · `3` = 带有摩擦地工作 · `1` = 出错/无法使用。
- `--comment`：任何错误、过时的文档、缺失的标志或令人困惑的行为，以及触发它的命令或流程。

匿名，无需 API 密钥，在禁用分析时（`HEYGEN_NO_ANALYTICS` 或 `heygen config set analytics false`）无操作。这是 CLI 团队的主要信号通道 — 一个无声完成的运行会告诉他们什么也没发生。**CLI 模式仅限：** 在 MCP 或 OpenClaw-plugin 模式中跳过（那些通过 `mcp__heygen__*` / `video_generate` 路由，没有反馈界面）。

---

## 最佳实践

- **前置钩子。** 前 5 秒 = 80% 的留存率。
- **每个视频一个想法。** 单主题生成效果显著更好。
- **为耳朵写作。** 如果你不会对朋友说，就重写它。

📖 **已知问题 → [references/troubleshooting.md](references/troubleshooting.md)**
