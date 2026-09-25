# HeyGen 视频翻译

将现有视频翻译成175种以上的语言。系统将主讲人的声音克隆到目标语言中，重新同步他们的嘴唇到新音频，并返回一个完整的配音视频。您提供一个源视频和一个目标语言——引擎将处理转录、翻译、声音克隆、唇同步和（可选的）烧入字幕。

这不是新视频生成。原始视频中的主讲人、表演、构图和品牌资产都得到了保留。翻译是在已有的基础上进行的。

## 用户界面行为

1. **简洁明了。** 不要在聊天中堆砌翻译ID、原始API负载或状态JSON。报告结果（视频链接、语言），而不是管道。
2. **不要使用内部术语。** 不要说“轮询”、“视频翻译ID”、“资产ID”、“v3端点”。说“正在翻译”、“快完成了”、“您的文件”。
3. **轮询是静默的。** 背景长时间运行的翻译，只在（a）结果交付时、（b）>5分钟停滞（一次更新）、（c）硬故障时说话。
4. **一个结果，一条消息。** 当视频完成时，发送链接并附上一行摘要（目标语言、时长、模式）。不要每个API字段。
5. **不要叙述传输选择。** MCP vs CLI vs OpenClaw插件是内部的。在会话开始时无声选择；永远不要提及正在使用的插件。
6. **使用用户的语言进行沟通。** 从他们的第一条消息中检测。回复、确认和问题使用他们的语言。技术CLI/API指令保持英文。

## API模式检测

**在会话开始时选择一种传输方式。会话期间从不混合，永不切换，永不叙述选择。**

按以下顺序检测：

1. **OpenClaw插件模式** — 如果在OpenClaw中运行并且`video_generate`工具暴露了HeyGen翻译模型，则优先使用该模型。*目前插件生成视频但不会直接暴露翻译——直到HeyGen通过`video_generate`提供翻译为止，才会向下传递到下一层。*
2. **CLI模式（API密钥覆盖）** — 如果`HEYGEN_API_KEY`在环境中设置并且`heygen --version`退出为0，则使用CLI。API密钥的存在是一个明确的信号，表明用户希望直接访问API。
3. **MCP模式** — 没有`HEYGEN_API_KEY`并且HeyGen MCP工具可见（`mcp__heygen__*`）。OAuth认证，针对用户的计划信用运行。
4. **CLI模式（回退）** — MCP工具不可用并且`heygen --version`退出为0。通过`heygen auth login`进行认证。
5. **都不是** — 告诉用户一次：“要使用此技能，请连接HeyGen MCP服务器或安装HeyGen CLI：`curl -fsSL https://static.heygen.ai/cli/install.sh | bash`然后`heygen auth login`。”

### 认证验证（在任何API调用之前运行）

模式检测后，在进入阶段1之前验证认证是否实际工作。这避免了浪费用户的时间收集输入，只在提交时遇到认证错误。

- **MCP模式：** 认证由OAuth处理——不需要检查。
- **CLI模式：** 运行`heygen auth status`（静默）。如果它退出为0，则继续。如果它退出非零（没有密钥、过期、无效）：
  1. 询问用户：*"我需要您的HeyGen API密钥才能继续。您可以从https://app.heygen.com/settings?nav=API获取一个——将其粘贴在这里。*"
  2. 一旦他们提供，就持久化它：`echo "<key>" | heygen auth login`（写入`~/.heygen/credentials`，跨会话持久化）。
  3. 验证：`heygen auth status`。如果仍然失败，请显示错误并停止。

这是一个**一次性设置**。一旦`heygen auth login`持久化密钥，未来的会话将自动获取它。如果`heygen auth status`通过，则不要再次询问。

**硬性规则：**

- **从不调用`curl api.heygen.com/...`** 此技能中的每个操作都有一个CLI命令，并且在支持的情况下还有一个MCP工具。使用这些。
- **MCP模式：仅`mcp__heygen__*`工具。** 如果翻译尚未通过MCP暴露，则针对翻译操作向下传递到CLI。不要合成原始HTTP调用。
- **CLI模式：仅`heygen ...`命令。** 运行`heygen video-translate --help`和`heygen video-translate <子命令> --help`以发现参数。使用`--request-schema`查看任何创建命令的完整JSON形状。
- **以下操作显示MCP和CLI并排**——只读检测到的模式的列。

### MCP工具名称（仅MCP模式）

`create_video_translation`（单语言）。多语言和校对尚未通过MCP暴露——针对这些操作向下传递到CLI。在会话开始时运行`mcp__heygen__*`工具列表以确认可用性；工具表面会随时间演变。

### CLI命令组（仅CLI模式）

```
heygen video-translate
├── languages list              # 支持的目标语言
├── create                      # 提交翻译作业（单次或批量）
├── get <id>                    # 检查状态/获取结果
├── list                        # 列出过去的翻译
├── update                      # 更新作业元数据
├── delete                      # 删除作业
└── proofreads
    ├── create                  # 在最终渲染之前提取可编辑的字幕
    ├── get <id>                # 检查校对会话状态
    ├── srt get <id>            # 下载提取的SRT
    ├── srt update <id>         # 上传编辑后的SRT
    └── generate <id>           # 从批准的SRT生成最终视频
heygen asset create --file <path>   # 用于本地源视频上传（最大32 MB）
```

每个命令都支持`--help`。在`create`上使用`--request-schema`以查看完整的JSON正文。CLI输出：JSON在stdout上，`{error:{code,message,hint}}`包在stderr上，退出代码`0`表示成功 · `1`表示API · `2`表示用法 · `3`表示认证 · `4`表示超时。在`create`上添加`--wait`以阻塞直到作业完成（默认超时20分钟）。

📖 **详细的CLI/MCP错误→操作映射→[references/troubleshooting.md](references/troubleshooting.md)**

---

## 默认工作流程

该技能运行四个阶段。阶段1（发现）是唯一可以提问的地方。阶段2（预飞行）是静默的。阶段3（提交+轮询）是静默的。阶段4（交付）是一条短消息。

```
阶段1 — 发现       — 从用户那里收集最小的输入
阶段2 — 预飞行      — 验证语言、分类内容、设置标志
阶段3 — 提交+轮询   — 启动，后台轮询，只在（a）结果交付时（b）>5分钟停滞（一次更新）（c）硬故障时显示
阶段4 — 交付         — 使用一条简短摘要发布结果
```

### 阶段1 — 发现

只问你没有的问题。使用用户的语言沟通。**永远不要运行表单。** 每次轮换最多问一两个问题。

**必需输入（直到你拥有这些为止）：**

1. **源视频。** 公共URL、本地文件路径或来自先前步骤的HeyGen资产ID。如果用户尚未提供，请询问：*"源视频是什么——URL、文件路径或现有的HeyGen资产？*"
2. **目标语言（s）。** 以用户的语言作为开放式问题询问：*"我应该将其翻译成哪种语言？*"* 不要显示选择器或预分配的选择——让用户自由输入。他们可能想要一种语言、多种语言或特定区域变体。接受他们提供的任何内容并验证其与阶段2中的规范语言列表。

**重要输入（如果没有提供，则询问，并使用智能默认值）：**

3. **说话人数。** 单人默认，大多数用户都有。当存在歧义时一次询问：*"视频中有多大的说话者？*"* 错误的说话人数是#1质量杀手——说话者混淆会在翻译过程中导致声音交换。不要为多人内容跳过此步骤。
4. **内容类型。** 您通常不需要询问——从视频中推断并确认。以下五个配置文件涵盖了约95%的情况。只有当确实存在歧义时才询问。
5. **字幕偏好。** 对话头和公司默认为开启；对播客/音频仅默认为关闭。如果您切换默认值，请在阶段4中简要提及。
6. **时长灵活性。** 询问：*"翻译后的视频需要与原始视频完全相同长度，还是可以稍微长一点/短一点？允许灵活性通常听起来更自然——翻译后的语音有足够的空间以舒适的速度说话，而不是被加速或压缩。*"* 默认建议：灵活（`enable_dynamic_duration: true`）。仅在用户需要帧精确时间时设置为`false`（例如，与时间轴、广告位或外部音频轨道同步）。

**可选（仅当相关时）：**

7. **术语表/不翻译术语。** 对于公司或技术内容，询问：*"我应该保留原始语言中的产品名称、公司名称或术语吗？*"* HeyGen目前不接受硬术语表，因此这成为校对步骤（阶段3-校对）的高风险指导。
8. **部分翻译。** 如果用户提到特定片段（“只是介绍”、“从1:30到4:00”），请捕获`start_time`和`end_time`（以秒为单位）。
9. **在校对之前进行最终渲染？** 默认为关闭（更快，更少的批准）。默认为开启：长视频（>3分钟）、公司/品牌内容、高风险法律/医疗/教育、用户母语的语言（以便他们可以验证）。询问：*"在校对和编辑字幕之前进行最终渲染？大约增加5分钟，但允许您纠正任何错误的术语。**

📖 **区域对问题（正式程度注册、从左到右语言、音调压缩、唇同步上限）→ [references/language-locale-guide.md](references/language-locale-guide.md)**

### 阶段2 — 预飞行

静默。没有用户界面上的对话。三个检查，按顺序进行。

**检查2a：语言验证。**

**MCP：** `list_video_translation_languages()`（如果暴露）。否则CLI。
**CLI：** `heygen video-translate languages list | jq -r '.data.languages[]'`

列表包含确切的字符串（"西班牙语（西班牙）"、"中文（普通话，简体）"、"阿拉伯语（沙特阿拉伯）"）。将用户输入与这些确切的字符串进行不区分大小写的匹配。如果他们说“西班牙语”，则默认为“西班牙语（西班牙）”，并在阶段4中确认。如果他们说“中文”，则默认为“中文（普通话，简体）”。如果指定了区域（“墨西哥西班牙语”），则映射它（“西班牙语（墨西哥）”）。如果没有匹配：请用户从最接近的选项中选择。

**检查2b：源视频路由。**

| 用户提供的源 | 路由 |
|--------------------------|-------|
| 公共HTTPS URL（无需认证，HEAD返回视频MIME） | 直接传递作为 `{type: "url", url: "..."}` |
| 需要认证的URL、403、404或HTML响应 | 告诉用户，请求公共URL或本地文件 |
| 本地文件路径 | 通过`heygen asset create --file <path>`（CLI）或`upload_asset`（MCP）上传。最大32 MB。使用返回的`asset_id`作为 `{type: "asset_id", asset_id: "..."}` |
| 现有的HeyGen资产ID | 直接传递作为 `{type: "asset_id", asset_id: "..."}` |

📖 **资产路由边缘情况（非常大的文件、预签名URL、需要认证的源）→ [references/asset-routing.md](references/asset-routing.md)**

**检查2c：内容配置文件。**

根据源选择一个配置文件。不要向用户列出所有五个配置文件——无声地提议，并且只有当源确实存在歧义时（例如，一个音乐重量的对话头，您无法判断是否应该使用语音增强）才询问。

| 配置文件 | 使用时 | 标志 |
|---------|----------|-------|
| **对话头 / 主讲人**（默认） | 一个人对着摄像头说话；干净的音频 | `mode: precision`, `enable_speech_enhancement: true`, `enable_caption: true`, `enable_dynamic_duration: true`, `keep_the_same_format: true` |
| **播客 / 音频仅** | 视觉是静态的，不重要，或者不存在 | `mode: precision`, `translate_audio_only: true`, `enable_speech_enhancement: true`, `enable_caption: true` |
| **音乐 / 高音轨** | 背景音乐干扰语音 | `mode: precision`, `disable_music_track: true`, `enable_speech_enhancement: true`, `enable_dynamic_duration: true`, `keep_the_same_format: true` |
| **多说话者** | 两个或多个不同的说话者 | 对话头默认值 + `speaker_num: <count>`。说话人数是必需的——不要猜测。 |
| **公司 / 品牌化** | 品牌声音、术语表纪律、高风险 | 对话头默认值 + （如果用户有一个）`brand_voice_id`。强烈建议对此配置文件进行校对。 |

**始终：**
- `mode: "precision"`，除非用户明确要求“快速”/“快速”/“快速”。
- `enable_dynamic_duration`: 基于阶段1中关于时长灵活性的问题的用户答案设置。默认`true`（推荐）——让翻译后的语音呼吸，而不是被压缩到源的确切时间。仅在用户明确需要固定长度输出时设置为`false`。音调压缩使灵活性对于en→zh、en→ja、en→ko（亚洲语言运行较短）；de→en、ja→en（运行较长）；ar/he/ur（从左到右+注册转换）。
- `keep_the_same_format: true` 用于视觉翻译——保留源的分辨率和比特率，以便配音视频与原始编码匹配。
- `enable_watermark: false`（默认）。

### 阶段3 — 提交+轮询

静默。后台工作。只在（a）每语言完成、（b）每语言硬故障、（c）>5分钟进度检查时显示。

**分支：**

- **标准路径**（校对=关闭）：提交翻译，后台轮询，交付。
- **校对路径**（校对=开启）：创建校对会话 → 下载SRT → 用户编辑或您协助 → 上传编辑后的SRT → 生成最终 → 后台轮询 → 交付。

#### 标准路径

使用批量语法为每个目标语言提交一个作业。

**MCP**（目前仅限一次写作）:
```
create_video_translation(
  video={type, url|asset_id},
  output_languages=["Spanish (Spain)"],
  mode="precision",
  enable_speech_enhancement=true,
  enable_caption=true,
  enable_dynamic_duration=true,
  keep_the_same_format=true,
  speaker_num=<n>,           # 仅当已知多说话者时
)
```

**CLI:**
```bash
heygen video-translate create \
  -d '{"video":{"type":"url","url":"https://..."},"output_languages":["Spanish (Spain)","Japanese (Japan)"]}' \
  --mode precision \
  --enable-speech-enhancement \
  --enable-caption \
  --enable-dynamic-duration \
  --keep-the-same-format \
  --speaker-num 1 \
  --title "<简短标题>"
```

响应返回每个语言的一个`video_translation_id`。捕获所有它们。

**轮询（静默，后台）:**

使用`--wait`在`create`上阻塞，直到完成时运行一个语言。对于批量，丢弃`--wait`并轮询每个ID：

```bash
# CLI模式轮询（后台）
heygen video-translate get <video-translation-id>
# 返回 { data: { status: "pending"|"running"|"completed"|"failed", video_url, ... } }
```

轮询节奏：前3分钟每30秒，然后每60秒。大多数翻译在5-15分钟内完成；一些（长视频，批量语言）需要30分钟以上。硬超时：每个翻译60分钟——超过此时间，将其视为卡住，并显示给用户。

**MCP等效：** `get_video_translation(id)`（如果暴露）。否则向下传递到CLI进行轮询。

📖 **后台轮询模式（不要在前台轮询/特定于harness的说明）→ [references/troubleshooting.md](references/troubleshooting.md)**

#### 校对路径

对于高风险内容，首先运行一个校对会话，以便用户可以在引擎提交最终渲染之前查看/编辑翻译后的字幕。

```bash
# 1. 创建校对会话 — 返回proofread_ids（每个语言一个）
heygen video-translate proofreads create \
  -d '{"video":{"type":"url","url":"https://..."}}' \
  --output-languages "Spanish (Spain)" \
  --mode precision \
  --enable-speech-enhancement \
  --keep_the_same_format \
  --speaker-num 1 \
  --title "<简短文件名安全的标题>"
# → 状态：处理中  (短视频3-5分钟)

# 2. 轮询直到完成（或失败+failure_message）
heygen video-translate proofreads get <proofread-id>
# → 状态：完成

# 3. 获取可编辑的+原始SRT的预签名URL
heygen video-translate proofreads srt get <proofread-id> > /tmp/srt-resp.json
SRT_URL=$(jq -r '.data.srt_url'          /tmp/srt-resp.json)  # 目标语言，编辑这个
ORIG_URL=$(jq -r '.data.original_srt_url' /tmp/srt-resp.json) # 源语言文本转录
curl -s "$SRT_URL" -o /tmp/proofread.srt

# 4. 手动或sed编辑/tmp/proofread.srt（术语表、注册、名称）
#    参考references/proofreads-workflow.md了解完整的编辑剧本。

# 5. 将编辑后的SRT作为资产上传，然后通过资产ID引用它。
#    `heygen asset create` 接受 srt (png, jpeg, mp4, webm, mp3, wav, pdf, srt).
#    回退：在公共URL上托管，并使用 {"type":"url","url":"..."}。
ASSET_ID=$(heygen asset create --file /tmp/proofread.srt | jq -r '.data.asset_id')
heygen video-translate proofreads srt update <proofread-id> \
  -d "{\"srt\":{\"type\":\"asset_id\",\"asset_id\":\"$ASSET_ID\"}}"

# 6. 启动最终渲染 — 返回一个video_translation_id
heygen video-translate proofreads generate <proofread-id> --captions
# → {"data":{"video_translation_id":"<vid-id>","status":"processing"}}

# 7. 轮询翻译完成（不是proofreads get——在这里毕业）
heygen video-translate get <vid-id>
# → 状态：运行 → 完成；data.video_url包含最终的mp4
```

📖 **何时坚持校对，常见SRT编辑，术语表纪律 → [references/proofreads-workflow.md](references/proofreads-workflow.md)**

### 阶段4 — 交付

每个完成的语言一条消息。格式：

> ✅ 西班牙语（西班牙） — <video_url>
> 1m 47s, 精确模式，字幕开启。

如果语言失败：一条简短的消息说明原因（来自故障排除参考）。不要向用户发送重试选项，除非他们询问。如果用户批量了许多语言，则按完成顺序交付每个语言——不要等待所有语言完成后再发布任何内容。

**源质量免责声明。** 翻译无法改善源。如果源有模糊的音频、快速剪辑、严重的面部遮挡或低分辨率，唇同步和语音质量会下降。当您在阶段2中检测到这些条件或用户提到它们时，请提前警告。不要在出现不良结果后显示此内容。

### 报告反馈（CLI模式）

翻译交付后——或者如果您在过程中遇到摩擦——运行一次每个任务：

```bash
heygen feedback --rating <1-5> --comment "<工作得很好，或者什么出了问题以及您尝试了什么>"
```

- `--rating`: `5` = 工作得很好 · `3` = 有摩擦地工作 · `1` = 出错/无法使用。
- `--comment`: 任何错误、过时的文档、缺失的标志或令人困惑的行为，加上触发它的命令或流程。

匿名，无需API密钥，当分析被选择退出时（`HEYGEN_NO_ANALYTICS`或`heygen config set analytics false`）不会执行。这是CLI团队的主要信号通道——一个无声完成的运行告诉他们什么。**CLI模式仅限：** 在MCP或OpenClaw-plugin模式下跳过（这些通过MCP/plugin表面，没有反馈命令）。

---

## 嵌入式专业知识

上述默认值涵盖了常见情况。以下是区分此技能与通用API包装的决策。在工作流程期间使用它们作为判断调用，而不是清单要背诵的。

### 说话人数是#1质量杀手

对于对话头：1个说话者。对于采访/播客/小组讨论：准确计数，不要猜测。引擎通过`speaker_num`分离声音；错误的计数意味着声音在配音输出中混合。如果用户不确定，请让他们滚动视频并计数。

### 源质量分类（在提交之前做）

在阶段2中进行30秒的分类可以节省10-30分钟的糟糕翻译。观看/收听源的前~10秒并检查：

- **音频：** 语音是否清晰？背景音乐主导？噪音/嘶嘶声？→ 如果语音不清晰，默认`enable_speech_enhancement: true`。如果音乐主导，`disable_music_track: true`。如果两者都有，警告用户无论标志如何，质量都可能较低。
- **面部可见性：** 说话者的面部大部分时间都在摄像头前，正面，光线充足？→ 重叠（太阳镜，手在脸上），侧面照片，非常快的剪辑，或者低于720p的面部都会降低唇同步质量。
- **屏幕上的文本：** 源语言中的烧入字幕？→ 这些不会重新渲染。它们将在配音输出中以源语言保留。如果用户想要新语言字幕，他们会有两个字幕轨道——建议`enable_caption: true`并警告关于现有的烧入字幕。

### 区域对问题

- **音调压缩/扩展。** en→zh, en→ja, en→ko运行约30%短；de→en, ja→en运行较长；en→ar/he通常扩展。动态时长（阶段1中的时长灵活性问题）对这些对特别重要——没有它，en→zh听起来会不自然慢（语音被压缩到30%太长的时序线中）。如果用户选择了固定长度输出，请警告高压缩对的质量会下降。
- **正式程度/注册。** ja-JP（敬语/keigo），ko-KR（尊称），de-DE（Sie vs du），th-TH（皇家/礼貌/随意），id-ID（正式与口语）——引擎默认选择中性正式。如果源是对话式的，并且用户希望在目标中匹配注册，请在校对或预警告它听起来比原始版本更正式。
- **从左到右语言。** 阿拉伯语、希伯来语、乌尔都语、波斯语——字幕从右到左显示。烧入字幕可能与源视频的下半部分图形在错误的一侧发生冲突。如果源有屏幕上的文本或下半部分图形，建议音频仅翻译或校对字幕样式审查。
- **区域变体很重要。** 西班牙语（西班牙）与西班牙语（墨西哥）与西班牙语（阿根廷）在词汇、语调、语音速率方面有明显的不同。拉丁美洲观众通常认为卡斯蒂利亚西班牙语是外来的。对于西班牙语，如果未指定，请问一次。对于葡萄牙语（葡萄牙与巴西），法语（法国与加拿大与瑞士），阿拉伯语（阿拉伯语有19个区域变体）。
- **普通话特别。** "中文（普通话，简体)"是针对中国大陆观众的标准默认值。"中文（粤语，繁体)"用于香港/海外粤语说方言的侨民。"中文（台湾普通话，繁体)"用于台湾。这些不是可互换的。

📖 **完整的区域对表，包括注册说明和已知怪癖→ [references/language-locale-guide.md](references/language-locale-guide.md)**

### 唇同步上限

唇同步最好在：

- 稳定、正面拍摄
- ≥720p面部分辨率
- 干净、光线充足的面部
- 最小剪辑（长镜头效果更好）

唇同步会在以下情况下下降：

- 侧面照片，向下看的照片，面部部分遮挡
- 快速剪辑（<2秒镜头）
- 低光照、运动模糊或低分辨率面部
- 重手势，面部快速移动

如果用户的源具有这些条件，请在阶段1/2警告他们：*"注意——源具有[X]，所以唇同步不会像静态对话头那样紧密。要继续吗，还是切换到音频仅翻译？**

### 字幕：烧入与侧车

`enable_caption: true`默认生成字幕烧入视频。优点：无需单独文件，可以在任何地方播放。缺点：无法后期编辑，可能与源图形冲突，固定的字体/样式。对于高风险内容，用户可能想要重新样式字幕（品牌套件，特定语言的字体），请选择校对工作流程——它给用户一个他们可以用作侧车字幕文件的SRT。

### 音频仅翻译

`translate_audio_only: true`完全跳过唇同步。使用它的情况：

- 播客（“视频”是一个静态图像或波形）
- 您将在后期重新合成到不同的视频中
- 任何情况下，唇同步都不可能（没有面部，非常差的面部质量）

输出是音频文件（通常为MP3）。告诉用户如何使用它：*"这给您一个翻译后的音频轨道。将其重新合成回原始视频，或单独使用。*"* 不要将音频仅翻译推销为“不良唇同步的质量解决方案”——它是一个不同的交付物。
