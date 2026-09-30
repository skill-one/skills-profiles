---
name: faster-whisper
description: 本地使用faster-whisper进行语音转文本。与OpenAI Whisper相比，在相同准确率下速度提升4-6倍；GPU加速支持约20倍实时转录。支持SRT/VTT/TTML/CSV字幕格式，说话人分割，URL/YouTube输入，批量处理带预计完成时间(ETA)，转录文本搜索，章节检测，按文件的语言映射。
---

# 更快的Whisper

本地语音转文本使用faster-whisper——OpenAI的Whisper的CTranslate2重实现，速度比**快4-6倍**，但准确率完全相同。使用GPU加速，预期转录速度可达**约20倍实时**（10分钟的音频文件可在约30秒内完成）。

## 使用场景

当你需要以下功能时，请使用此技能：

- **转录音频/视频文件**——会议、采访、播客、讲座、YouTube视频
- **生成字幕**——SRT、VTT、ASS、LRC或TTML广播标准字幕
- **识别说话人**——通过`--diarize`参数进行说话人分割，标注谁说了什么
- **从URL转录**——YouTube链接和直接音频URL（通过yt-dlp自动下载）
- **转录播客源**——`--rss <feed-url>`获取并转录节目
- **批量处理文件**——支持通配符模式、目录、跳过已存在文件；自动显示预计完成时间
- **本地将语音转换为文本**——无需API成本，离线工作（模型下载后）
- **翻译成英语**——使用`--translate`参数将任何语言翻译成英语
- **多语言转录**——支持99+种语言，自动检测
- **不同语言文件的批量转录**——使用`--language-map`为每个文件分配不同语言
- **多语言音频转录**——使用`--multilingual`参数处理混合语言音频
- **特定术语的音频转录**——使用`--initial-prompt`参数处理专业术语或需要特别关注的词汇
- **转录前预处理嘈杂音频**——使用`--normalize`和`--denoise`参数
- **流式输出**——使用`--stream`参数实时显示转录内容
- **剪辑时间范围**——使用`--clip-timestamps`参数转录特定时间段
- **搜索转录内容**——使用`--search "term"`参数查找单词/短语出现的所有时间戳
- **检测章节**——使用`--detect-chapters`参数从静音间隙中检测章节分割
- **导出说话人音频**——使用`--export-speakers DIR`参数将每个说话人的发言保存为独立的WAV文件
- **电子表格输出**——使用`--format csv`参数生成带时间戳的CSV文件

**触发短语：**
"转录这个音频"、"将语音转换为文本"、"他们说了什么"、"制作转录文本",
"音频转文本"、"为这个视频制作字幕"、"谁在说话"、"翻译这个音频"、"翻译成英语",
"在哪里提到X"、"搜索转录内容"、"他们什么时候说的"、"在什么时间戳",
"添加章节"、"检测章节"、"查找音频中的断点"、"这个录音的目录",
"TTML字幕"、"DFXP字幕"、"广播格式字幕"、"Netflix格式",
"ASS字幕"、"Aegisub格式"、"高级Substation Alpha"、"mpv字幕",
"LRC字幕"、"定时歌词"、"卡拉OK字幕"、"音乐播放器歌词",
"HTML转录文本"、"带置信度颜色的转录文本"、"彩色编码转录文本",
"每个说话人单独的音频"、"导出说话人音频"、"按说话人分割",
"转录文本为CSV"、"电子表格输出"、"转录播客"、"播客RSS源",
"批量处理不同语言"、"每文件语言",
"多格式转录"、"同时生成srt和txt"、"输出srt和文本",
"去除填充词"、"清理ums和uhs"、"去除犹豫声音"、"去除you know和I mean",
"转录左声道"、"转录右声道"、"立体声道"、"仅左声道",
"包裹字幕行"、"每行字符限制"、"字幕每行最大字符数",
"检测段落"、"段落断点"、"分组为段落"、"添加段落间距"

**⚠️ 代理指导——保持调用最小化：**

_CORE规则：默认命令（`./scripts/transcribe audio.mp3`）是最快的方式——只有在用户明确要求该功能时才添加标志。_

**转录：**

- 只有在用户要求"谁说了什么" / "识别说话人" / "标注说话人"时，才添加`--diarize`
- 只有在用户要求特定格式的字幕/字幕时，才添加`--format srt/vtt/ass/lrc/ttml`
- 只有在用户要求CSV或电子表格输出时，才添加`--format csv`
- 只有在用户需要单词级时间戳时，才添加`--word-timestamps`
- 只有在有特定领域术语需要预提示时，才添加`--initial-prompt`
- 只有在用户需要将非英语音频翻译成英语时，才添加`--translate`
- 只有在用户提到音频质量差或噪音时，才添加`--normalize`/`--denoise`
- 只有在用户需要长文件的实时/渐进输出时，才添加`--stream`
- 只有在用户需要特定时间范围时，才添加`--clip-timestamps`
- 只有在模型在音乐/静音上出现幻觉时，才添加`--temperature 0.0`
- 只有在VAD过于激进地切割语音或包含噪音时，才添加`--vad-threshold`
- 只有在知道说话人数时，才添加`--min-speakers`/`--max-speakers`
- 只有在token未缓存于`~/.cache/huggingface/token`时，才添加`--hf-token`
- 只有在需要为长段字幕提高可读性时，才添加`--max-words-per-line`
- 只有在转录内容包含明显伪影（音乐标记、重复）时，才添加`--filter-hallucinations`
- 只有在用户要求句子级字幕提示时，才添加`--merge-sentences`
- 只有在用户要求去除填充词（um、uh、you know、I mean、犹豫声音）时，才添加`--clean-filler`
- 只有在用户提到立体轨道、双通道录音或需要特定声道时，才添加`--channel left|right`
- 只有在用户指定每行字幕的字符限制（例如："Netflix格式"、"42个字符每行"）时，才添加`--max-chars-per-line N`；优先级高于`--max-words-per-line`
- 只有在用户要求段落断点或结构化文本输出时，才添加`--detect-paragraphs`；`--paragraph-gap`（默认3.0秒）只有在需要自定义间隙时才添加
- 只有在用户提供真实姓名以替换SPEAKER_1/2时，才添加`--speaker-names "Alice,Bob"`——始终需要`--diarize`
- 只有在用户命名`--initial-prompt`无法良好服务的特定罕见术语时，才添加`--hotwords WORDS`；优先使用`--initial-prompt`处理通用领域术语
- 只有在用户知道音频起始的确切单词时，才添加`--prefix TEXT`
- 只有在用户只想识别语言而不转录时，才添加`--detect-language-only`
- 只有在用户要求性能统计、RTF或基准信息时，才添加`--stats-file PATH`
- 只有在处理大型CPU批量任务时，才添加`--parallel N`；GPU可高效处理单个文件——不要为单个文件或小批量添加
- 只有在输入不可靠（URL、网络文件）且预期存在暂时性故障时，才添加`--retries N`
- 只有在用户明确要求将字幕嵌入/烧录到视频中时，才添加`--burn-in OUTPUT`；需要ffmpeg和视频文件输入
- 只有在用户可能重新处理相同URL以避免重新下载时，才添加`--keep-temp`
- 只有在用户在批量模式下指定自定义命名模式时，才添加`--output-template`
- **多格式输出**（`--format srt,text`）：只有在用户明确要求一次处理多种格式时才添加；始终与`-o <dir>`配合使用
- 任何单词级功能自动运行wav2vec2对齐（额外开销约5-10秒）
- `--diarize`在上述基础上增加约20-30秒

**搜索：**

- 只有在用户要求在音频中查找/定位/搜索特定单词或短语时，才添加`--search "term"`
- `--search`**替换**正常转录输出——它只打印匹配的片段和时间戳
- 只有在用户提到近似/部分匹配或拼写错误时，才添加`--search-fuzzy`
- 要将搜索结果保存到文件，使用`-o results.txt`

**章节检测：**

- 只有在用户要求章节、段落、目录或"主题何时变化"时，才添加`--detect-chapters`
- 默认`--chapter-gap 8`（8秒静音=新章节）适用于大多数播客/讲座；密集内容可调低
- `--chapter-format youtube`（默认）输出YouTube兼容的时间戳；使用`json`用于程序化使用
- **始终使用`--chapters-file PATH`**当结合章节和转录输出时——避免章节标记混合到转录文本中
- 如果用户只想章节（不转录），将stdout重定向到文件`-o /dev/null`并使用`--chapters-file`
- **批量模式限制：** `--chapters-file`接受单个路径——在批量模式下，每个文件的章节会覆盖前一个。对于批量章节检测，省略`--chapters-file`（章节在`=== CHAPTERS (N) ===`下打印到stdout）或为每个文件单独运行

**说话人音频导出：**

- 只有在用户明确要求将每个说话人的音频单独保存时，才添加`--export-speakers DIR`
- 始终与`--diarize`配合使用——如果没有说话人标签，将静默跳过
- 需要ffmpeg；输出`SPEAKER_1.wav`、`SPEAKER_2.wav`等（如果设置了`--speaker-names`，则为真实姓名）

**语言映射：**

- 只有在用户确认文件间语言不同时，在批量模式下才添加`--language-map`
- 内联格式：`"interview*.mp3=en,lecture*.mp3=fr"`——基于文件名进行fnmatch通配符匹配
- JSON文件格式：`@/path/to/map.json`，其中文件内容为`{"pattern": "lang_code"}`

**RSS / 播客：**

- 只有在用户提供播客RSS源URL时，才添加`--rss URL`
- 默认获取5个最新节目；`--rss-latest 0`获取全部；`--skip-existing`安全续传
- **始终使用`-o <dir>`**与`--rss`配合使用——否则所有节目转录内容会打印到stdout并连接，难以使用；设置`-o <dir>`时，每个节目将获得独立文件

**代理传递的输出格式：**

- **搜索结果**（`--search`）→ 直接打印给用户；输出为人类可读
- **章节输出** → 如果没有`--chapters-file`，章节在转录后的stdout中以`=== CHAPTERS (N) ===`标题显示；使用`--format json`时，章节也嵌入JSON的`"chapters"`键下
- **字幕格式**（SRT、VTT、ASS、LRC、TTML）→ 始终写入`-o`文件；告诉用户输出路径，不要粘贴原始字幕内容
- **数据格式**（CSV、HTML、TTML、JSON）→ 始终写入`-o`文件；告诉用户输出路径，不要粘贴原始XML/CSV/HTML
- **ASS格式** → 用于Aegisub、VLC、mpv；写入文件并告诉用户可以在Aegisub中打开或在VLC/mpv中播放
- **LRC格式** → 音乐播放器（Foobar2000、AIMP、VLC）的定时歌词；写入文件
- **多格式**（`--format srt,text`）→ 需要`-o <dir>`；每种格式写入独立文件；告诉用户所有路径
- **JSON格式** → 适用于程序化后处理；不适合完整粘贴给用户
- **文本/转录** → 对于短文件安全显示给用户；长文件进行总结
- **统计输出**（`--stats-file`）→ 为用户总结关键字段（时长、处理时间、RTF），而不是粘贴原始JSON
- **语言检测**（`--detect-language-only`）→ 直接打印结果；为单行
- **ETA**会自动打印到stderr，用于批量任务；无需操作

**不使用场景：**

- 仅云环境且无本地计算
- 文件<10秒，API调用延迟不重要

**faster-whisper vs whisperx：**
此技能涵盖whisperx的所有功能——说话人分割（`--diarize`）、单词级时间戳（`--word-timestamps`）、SRT/VTT字幕——因此不需要whisperx。只有在需要whisperx的pyannote管道或这里未涵盖的批量GPU功能时，才使用whisperx。

## 快速参考

| 任务                           | 命令                                                                                | 备注                                               |
| ------------------------------ | -------------------------------------------------------------------------------------- | --------------------------------------------------- |
| **基本转录**        | `./scripts/transcribe audio.mp3`                                                       | 批量推理，VAD开启，distil-large-v3.5        |
| **SRT字幕**              | `./scripts/transcribe audio.mp3 --format srt -o subs.srt`                              | 自动启用单词时间戳                        |
| **VTT字幕**              | `./scripts/transcribe audio.mp3 --format vtt -o subs.vtt`                              | WebVTT格式                                       |
| **单词时间戳**            | `./scripts/transcribe audio.mp3 --word-timestamps --format srt`                        | wav2vec2对齐 (~10ms)                            |
| **说话人分割**        | `./scripts/transcribe audio.mp3 --diarize`                                             | 需要 pyannote.audio                             |
| **翻译→英语**        | `./scripts/transcribe audio.mp3 --translate`                                           | 任何语言→英语                              |
| **流式输出**              | `./scripts/transcribe audio.mp3 --stream`                                              | 实时分段转录                        |
| **片段时间范围**            | `./scripts/transcribe audio.mp3 --clip-timestamps "30,60"`                             | 仅30s–60s                                        |
| **降噪+标准化**        | `./scripts/transcribe audio.mp3 --denoise --normalize`                                 | 先清理嘈杂音频                          |
| **减少幻觉**       | `./scripts/transcribe audio.mp3 --hallucination-silence-threshold 1.0`                 | 跳过幻觉的静音                           |
| **YouTube/URL**                | `./scripts/transcribe https://youtube.com/watch?v=...`                                 | 自动通过yt-dlp下载                           |
| **批量处理**              | `./scripts/transcribe *.mp3 -o ./transcripts/`                                         | 输出到目录                                 |
| **批量跳过已存在**            | `./scripts/transcribe *.mp3 --skip-existing -o ./out/`                                 | 继续中断的批量                          |
| **领域术语**               | `./scripts/transcribe audio.mp3 --initial-prompt 'Kubernetes gRPC'`                    | 提升罕见术语                              |
| **关键词增强**             | `./scripts/transcribe audio.mp3 --hotwords 'JIRA Kubernetes'`                          | 偏向特定词汇解码器                  |
| **前缀条件**        | `./scripts/transcribe audio.mp3 --prefix 'Good morning,'`                              | 用已知开头词初始化第一段                 |
| **固定模型版本**          | `./scripts/transcribe audio.mp3 --revision v1.2.0`                                     | 可重复的转录与固定版本   |
| **调试库日志**         | `./scripts/transcribe audio.mp3 --log-level debug`                                     | 显示 faster_whisper内部日志                   |
| **Turbo模型**                | `./scripts/transcribe audio.mp3 -m turbo`                                              | large-v3-turbo的别名                            |
| **更快英语**             | `./scripts/transcribe audio.mp3 --model distil-medium.en -l en`                        | 英语专用，6.8x更快                           |
| **最大准确率**           | `./scripts/transcribe audio.mp3 --model large-v3 --beam-size 10`                       | 全模型                                          |
| **JSON输出**                | `./scripts/transcribe audio.mp3 --format json -o out.json`                             | 带统计信息的程序化访问                      |
| **过滤噪声**               | `./scripts/transcribe audio.mp3 --min-confidence 0.6`                                  | 丢弃低置信度片段                        |
| **混合量化**        | `./scripts/transcribe audio.mp3 --compute-type int8_float16`                           | 节省VRAM，最小质量损失                     |
| **减少批量大小**          | `./scripts/transcribe audio.mp3 --batch-size 4`                                        | GPU内存不足时                               |
| **TSV输出**                 | `./scripts/transcribe audio.mp3 --format tsv -o out.tsv`                               | OpenAI Whisper兼容TSV                       |
| **修正幻觉**         | `./scripts/transcribe audio.mp3 --temperature 0.0 --no-speech-threshold 0.8`           | 锁定温度+跳过静音                     |
| **调整VAD灵敏度**       | `./scripts/transcribe audio.mp3 --vad-threshold 0.6 --min-silence-duration 500`        | 更严格的语音检测                            |
| **已知说话人数量**        | `./scripts/transcribe meeting.wav --diarize --min-speakers 2 --max-speakers 3`         | 限制说话人分割                               |
| **字幕单词换行**     | `./scripts/transcribe audio.mp3 --format srt --word-timestamps --max-words-per-line 8` | 分割长字幕提示                                     |
| **私有/门禁模型**        | `./scripts/transcribe audio.mp3 --hf-token hf_xxx`                                     | 直接传递token                                 |
| **显示版本**               | `./scripts/transcribe --version`                                                       | 打印faster-whisper版本                        |
| **原地升级**           | `./setup.sh --update`                                                                  | 无需完整重装升级                      |
| **系统检查**               | `./setup.sh --check`                                                                   | 验证GPU、Python、ffmpeg、venv、yt-dlp、pyannote  |
| **仅检测语言**       | `./scripts/transcribe audio.mp3 --detect-language-only`                                | 快速语言检测，无转录                  |
| **检测语言JSON**       | `./scripts/transcribe audio.mp3 --detect-language-only --format json`                  | 机器可读语言检测                 |
| **LRC字幕**              | `./scripts/transcribe audio.mp3 --format lrc -o lyrics.lrc`                            | 音乐播放器用的带时间戳歌词格式               |
| **ASS字幕**              | `./scripts/transcribe audio.mp3 --format ass -o subtitles.ass`                         | Advanced SubStation Alpha (Aegisub、mpv、VLC)       |
| **合并句子**            | `./scripts/transcribe audio.mp3 --format srt --merge-sentences`                        | 将片段合并为句子块                 |
| **统计信息文件**              | `./scripts/transcribe audio.mp3 --stats-file stats.json`                               | 转录后写入性能统计JSON           |
| **批量统计**                | `./scripts/transcribe *.mp3 --stats-file ./stats/`                                     | 目录中每个输入一个统计文件                     |
| **模板命名**            | `./scripts/transcribe audio.mp3 -o ./out/ --output-template "{stem}_{lang}.{ext}"`     | 自定义批量输出文件名                       |
| **标准输入**                | `ffmpeg -i input.mp4 -f wav - \| ./scripts/transcribe -`                               | 直接从标准输入管道音频                      |
| **自定义模型目录**           | `./scripts/transcribe audio.mp3 --model-dir ~/my-models`                               | 自定义HuggingFace缓存目录                        |
| **本地模型**                | `./scripts/transcribe audio.mp3 -m ./my-model-ct2`                                     | CTranslate2模型目录                               |
| **HTML转录**            | `./scripts/transcribe audio.mp3 --format html -o out.html`                             | 带置信度着色的HTML                     |
| **烧录字幕**             | `./scripts/transcribe video.mp4 --burn-in output.mp4`                                  | 需要ffmpeg+视频输入                       |
| **命名说话人**              | `./scripts/transcribe audio.mp3 --diarize --speaker-names "Alice,Bob"`                 | 替换SPEAKER_1/2                                |
| **过滤幻觉**      | `./scripts/transcribe audio.mp3 --filter-hallucinations`                               | 移除伪影                                   |
| **保留临时文件**            | `./scripts/transcribe https://... --keep-temp`                                         | 用于URL重新处理                               |
| **并行批量**             | `./scripts/transcribe *.mp3 --parallel 4 -o ./out/`                                    | CPU多文件处理                                  |
| **推荐RTX 3070**       | `./scripts/transcribe audio.mp3 --compute-type int8_float16`                           | 节省~1GB VRAM，最小质量损失               |
| **CPU线程数**           | `./scripts/transcribe audio.mp3 --threads 8`                                           | 强制CPU线程数（默认：自动）              |
| **播客RSS（最新5集）**     | `./scripts/transcribe --rss https://feeds.example.com/podcast.xml`                     | 下载并转录最新5集播客                     |
| **播客RSS（所有集）**     | `./scripts/transcribe --rss https://... --rss-latest 0 -o ./episodes/`                 | 所有集，每个文件一个                     |
| **播客+SRT字幕**    | `./scripts/transcribe --rss https://... --format srt -o ./subs/`                       | 字幕所有集                               |
| **失败重试**           | `./scripts/transcribe *.mp3 --retries 3 -o ./out/`                                     | 错误时最多重试3次，带退避                |
| **CSV输出**                 | `./scripts/transcribe audio.mp3 --format csv -o out.csv`                               | 电子表格格式，带表头；正确引号             |
| **带说话人的CSV**          | `./scripts/transcribe audio.mp3 --diarize --format csv -o out.csv`                     | 添加说话人列                                 |
| **语言映射（内联）**      | `./scripts/transcribe *.mp3 --language-map "interview*.mp3=en,lecture.wav=fr"`         | 批量中每文件语言映射                          |
| **语言映射（JSON）**        | `./scripts/transcribe *.mp3 --language-map @langs.json`                                | JSON文件：{"pattern": "lang"}                      |
| **批量显示ETA**             | `./scripts/transcribe *.mp3 -o ./out/`                                                 | 自动显示每个文件的ETA                     |
| **TTML字幕**             | `./scripts/transcribe audio.mp3 --format ttml -o subtitles.ttml`                       | 广播标准DFXP/TTML（Netflix、BBC、Amazon） |
| **带说话人标签的TTML**     | `./scripts/transcribe audio.mp3 --diarize --format ttml -o subtitles.ttml`             | 带说话人标签的TTML                                |
| **搜索转录**          | `./scripts/transcribe audio.mp3 --search "keyword"`                                    | 查找关键词出现的时间戳               |
| **搜索到文件**             | `./scripts/transcribe audio.mp3 --search "keyword" -o results.txt`                     | 保存搜索结果                                 |
| **模糊搜索**               | `./scripts/transcribe audio.mp3 --search "aproximate" --search-fuzzy`                  | 近似/部分匹配                        |
| **检测章节**            | `./scripts/transcribe audio.mp3 --detect-chapters`                                     | 自动从静音间隙检测章节                  |
| **章节间隙调整**         | `./scripts/transcribe audio.mp3 --detect-chapters --chapter-gap 5`                     | 间隙≥5s（默认：8s）生成章节                  |
| **章节到文件**           | `./scripts/transcribe audio.mp3 --detect-chapters --chapters-file ch.txt`              | 保存YouTube格式章节列表                    |
| **章节JSON**              | `./scripts/transcribe audio.mp3 --detect-chapters --chapter-format json`               | 机器可读章节列表                       |
| **导出说话人音频**       | `./scripts/transcribe audio.mp3 --diarize --export-speakers ./speakers/`               | 将每个说话人的音频保存为单独WAV文件     |
| **多格式输出**        | `./scripts/transcribe audio.mp3 --format srt,text -o ./out/`                           | 一次写入SRT+TXT                          |
| **移除填充词**        | `./scripts/transcribe audio.mp3 --clean-filler`                                        | 移除um/uh/er/ah/hmm和话语标记             |
| **仅左声道**          | `./scripts/transcribe audio.mp3 --channel left`                                        | 转录前提取立体声左声道                   |
| **仅右声道**          | `./scripts/transcribe audio.mp3 --channel right`                                       | 提取立体声右声道                        |
| **每行最大字符数**         | `./scripts/transcribe audio.mp3 --format srt --max-chars-per-line 42`                  | 基于字符的字幕换行                   |
| **检测段落**          | `./scripts/transcribe audio.mp3 --detect-paragraphs`                                   | 在文本输出中插入段落分隔符              |
| **段落间隙调整**       | `./scripts/transcribe audio.mp3 --detect-paragraphs --paragraph-gap 5.0`               | 调整间隙阈值（默认3.0s）                   |

## 模型选择

根据需求选择合适的模型：

```dot
digraph model_selection {
    rankdir=LR;
    node [shape=box, style=rounded];

    start [label="开始", shape=doublecircle];
    need_accuracy [label="需要最大\n准确率?", shape=diamond];
    multilingual [label="多语言\n内容?", shape=diamond];
    resource_constrained [label="资源\n限制?", shape=diamond];

    large_v3 [label="large-v3\n或\nlarge-v3-turbo", style="rounded,filled", fillcolor=lightblue];
    large_turbo [label="large-v3-turbo", style="rounded,filled", fillcolor=lightblue];
    distil_large [label="distil-large-v3.5\n(默认)", style="rounded,filled", fillcolor=lightgreen];
    distil_medium [label="distil-medium.en", style="rounded,filled", fillcolor=lightyellow];
    distil_small [label="distil-small.en", style="rounded,filled", fillcolor=lightyellow];

    start -> need_accuracy;
    need_accuracy -> large_v3 [label="是"];
    need_accuracy -> multilingual [label="否"];
    multilingual -> large_turbo [label="是"];
    multilingual -> resource_constrained [label="否 (英语)"];
    resource_constrained -> distil_small [label="移动/边缘"];
    resource_constrained -> distil_medium [label="有限制"];
    resource_constrained -> distil_large [label="否"];
}
```

### 模型表

#### 标准模型（完整Whisper）

| 模型                  | 大小  | 速度     | 准确率  | 应用场景                           |
| ---------------------- | ----- | --------- | --------- | ---------------------------------- |
| `tiny` / `tiny.en`     | 39M   | 最快     | 基础     | 快速草稿                           |
| `base` / `base.en`     | 74M   | 非常快   | 良好      | 通用使用                           |
| `small` / `small.en`   | 244M  | 快       | 更好    | 大多数任务                         |
| `medium` / `medium.en` | 769M  | 中等     | 高      | 高质量语音转录                      |
| `large-v1/v2/v3`       | 1.5GB | 较慢     | 最佳      | 最大准确率                           |
| `large-v3-turbo`       | 809M  | 快       | 优秀    | 高准确率（比distil慢）             |

#### 精简模型 (~6倍更快，WER差异~1%)

| 模型                   | 大小 | 与标准速度对比 | 准确率  | 应用场景                           |
| ----------------------- | ---- | -------------- | --------- | ---------------------------------- |
| **`distil-large-v3.5`** | 756M | ~6.3倍更快      | 7.08% WER | **默认，最佳平衡**          |
| `distil-large-v3`       | 756M | ~6.3倍更快      | 7.53% WER | 之前的默认值                   |
| `distil-large-v2`       | 756M | ~5.8倍更快      | 10.1% WER | 备用                           |
| `distil-medium.en`      | 394M | ~6.8倍更快      | 11.1% WER | 仅英语，资源受限               |
| `distil-small.en`       | 166M | ~5.6倍更快      | 12.1% WER | 移动/边缘设备                |

`.en` 模型仅支持英语，对英语内容稍快/稍好。

> **精简模型的注意**：HuggingFace 建议禁用所有精简模型的 `condition_on_previous_text` 以防止重复循环。脚本**自动应用** `--no-condition-on-previous-text` 当检测到 `distil-*` 模型时。如需覆盖，请传递 `--condition-on-previous-text`。

## 自定义和微调模型

WhisperModel 接受本地 CTranslate2 模型目录和 HuggingFace 仓库名称 — 无需代码更改。

### 加载本地 CTranslate2 模型

```bash
./scripts/transcribe audio.mp3 --model /path/to/my-model-ct2
```

### 将 HuggingFace 模型转换为 CTranslate2

```bash
pip install ctranslate2
ct2-transformers-converter \
  --model openai/whisper-large-v3 \
  --output_dir whisper-large-v3-ct2 \
  --copy_files tokenizer.json preprocessor_config.json \
  --quantization float16
./scripts/transcribe audio.mp3 --model ./whisper-large-v3-ct2
```

### 通过 HuggingFace 仓库名称加载模型（自动下载）

```bash
./scripts/transcribe audio.mp3 --model username/whisper-large-v3-ct2
```

### 自定义模型缓存目录

默认情况下，模型缓存于 `~/.cache/huggingface/`。使用 `--model-dir` 覆盖：

```bash
./scripts/transcribe audio.mp3 --model-dir ~/my-models
```

## 配置

### Linux / macOS / WSL2

```bash
# 基础安装（创建虚拟环境，安装依赖，自动检测GPU）
./setup.sh

# 带说话人分割支持
./setup.sh --diarize
```

要求：

- Python 3.10+
- ffmpeg 不是基本转录所必需的 — PyAV（与 faster-whisper 一起捆绑）处理音频解码。ffmpeg 仅在 `--burn-in`、`--normalize` 和 `--denoise` 时需要。
- 可选：yt-dlp（用于 URL/YouTube 输入）
- 可选：pyannote.audio（用于 `--diarize`，通过 `setup.sh --diarize` 安装）

### 平台支持

| 平台               | 加速 | 速度            |
| ---------------------- | ------------ | ---------------- |
| **Linux + NVIDIA GPU** | CUDA         | ~20倍实时 🚀 |
| **WSL2 + NVIDIA GPU**  | CUDA         | ~20倍实时 🚀 |
| macOS Apple Silicon    | CPU\*        | ~3-5倍实时   |
| macOS Intel            | CPU          | ~1-2倍实时   |
| Linux (无GPU)         | CPU          | ~1倍实时     |

\*faster-whisper 使用 CTranslate2，在 macOS 上仅支持 CPU，但 Apple Silicon 足够快，可用于实际使用。

### GPU 支持（重要！）

设置脚本自动检测您的 GPU 并安装带 CUDA 的 PyTorch。**如果可用，始终使用 GPU** — CPU 转录非常慢。

| 硬件       | 速度          | 9分钟视频 |
| -------------- | -------------- | ----------- |
| RTX 3070 (GPU) | ~20倍实时  | ~27秒     |
| CPU (int8)     | ~0.3倍实时 | ~30分钟     |

> **RTX 3070 小贴士**：使用 `--compute-type int8_float16` 进行混合量化 — 节省 ~1GB VRAM，质量损失最小。非常适合在转录的同时运行说话人分割。

如果设置未检测到您的 GPU，手动安装带 CUDA 的 PyTorch：

```bash
# 对于 CUDA 12.x
uv pip install --python .venv/bin/python torch --index-url https://download.pytorch.org/whl/cu121

# 对于 CUDA 11.x
uv pip install --python .venv/bin/python torch --index-url https://download.pytorch.org/whl/cu118
```

- **WSL2 用户**：确保您在 Windows 上安装了 [NVIDIA CUDA 驱动程序 for WSL](https://docs.nvidia.com/cuda/wsl-user-guide/)。

## 使用

```bash
# 基本转录
./scripts/transcribe audio.mp3

# SRT 字幕
./scripts/transcribe audio.mp3 --format srt -o subtitles.srt

# WebVTT 字幕
./scripts/transcribe audio.mp3 --format vtt -o subtitles.vtt

# 从 YouTube URL 转录
./scripts/transcribe https://youtube.com/watch?v=dQw4w9WgXcQ --language en

# 说话人分割
./scripts/transcribe meeting.wav --diarize

# 分割的 VTT 字幕
./scripts/transcribe meeting.wav --diarize --format vtt -o meeting.vtt

# 使用领域术语初始化
./scripts/transcribe lecture.mp3 --initial-prompt "Kubernetes, gRPC, PostgreSQL, NGINX"

# 批量处理目录
./scripts/transcribe ./recordings/ -o ./transcripts/

# 批量处理，跳过已完成的文件
./scripts/transcribe *.mp3 --skip-existing -o ./transcripts/

# 过滤低置信度片段
./scripts/transcribe noisy-audio.mp3 --min-confidence 0.6

# 带完整元数据的 JSON 输出
./scripts/transcribe audio.mp3 --format json -o result.json

# 指定语言（比自动检测快）
./scripts/transcribe audio.mp3 --language en
```

## 选项

输入：
AUDIO                 音频文件、目录、通配符模式或 URL
                        接受：mp3、wav、m4a、flac、ogg、webm、mp4、mkv、avi、wma、aac
                        URL 通过 yt-dlp 自动下载（YouTube、直接链接等）

模型与语言：
  -m, --model NAME      Whisper 模型（默认：distil-large-v3.5；“turbo” = large-v3-turbo）
  --revision REV        模型修订版（git 分支/标签/提交）以锁定特定版本
  -l, --language CODE   语言代码，例如 en、es、fr（省略时自动检测）
  --initial-prompt TEXT  用于条件化模型的提示（术语、格式风格）
  --prefix TEXT         用于条件化第一段的前缀（例如已知的起始单词）
  --hotwords WORDS      空格分隔的热词以增强识别
  --translate           将任何语言翻译成英语（而不是转录）
  --multilingual        启用多语言/代码转换模式（有助于较小的模型）
  --hf-token TOKEN      HuggingFace 令牌用于私有/受保护模型和说话人分割
  --model-dir PATH      自定义模型缓存目录（默认：~/.cache/huggingface/）

输出格式：
  -f, --format FMT      text | json | srt | vtt | tsv | lrc | html | ass | ttml (默认：text)
                        接受逗号分隔列表：--format srt,text 一次性写入两者
                        多格式需要 -o <dir> 保存到文件时
  --word-timestamps     包含单词级时间戳（wav2vec2 自动对齐）
  --stream              输出段随着转录实时输出（禁用说话人分割/对齐）
  --max-words-per-line N  对于 SRT/VTT，将段分割为最多 N 个单词的子条目
  --max-chars-per-line N  对于 SRT/VTT/ASS/TTML，分割行以便每行不超过 N 个字符
                        当两者都设置时优先于 --max-words-per-line
  --clean-filler        从转录文本中删除犹豫填充词（um、uh、er、ah、hmm、hm）和话语标记
                        （你知道、我是说、你看）默认关闭。
  --detect-paragraphs   在文本输出中在自然边界处插入段落分隔符（空行）。
                        当：静音间隔 ≥ --paragraph-gap，或前一段结束句子且间隔 ≥ 1.5 秒时开始新段落
  --paragraph-gap SEC   开始新段落的最低静音间隔（秒）（默认：3.0）。
                        与 --detect-paragraphs 一起使用。
  --channel {left,right,mix}
                        要转录的立体声通道：左（c0）、右（c1）或混合（默认：混合）。
                        通过 ffmpeg 在转录前提取通道。需要 ffmpeg。
  --merge-sentences     将连续段合并为句子级块
                        （提高 SRT/VTT 可读性；按终止标点或 >2 秒间隔分组）
  -o, --output PATH     输出文件或目录（目录用于批量模式）
  --output-template TEMPLATE
                        批量输出文件名模板。变量：{stem}、{lang}、{ext}、{model}
                        示例："{stem}_{lang}.{ext}" → "interview_en.srt"

推理调优：
  --beam-size N         并行搜索大小；越高 = 更准确但越慢（默认：5）
  --temperature T       采样温度或逗号分隔的备用列表，例如
                        '0.0' 或 '0.0,0.2,0.4'（默认：faster-whisper 的调度）
  --no-speech-threshold PROB
                        标记段为静音的概率阈值（默认：0.6）
  --batch-size N        批量推理批处理大小（默认：8；OOM 时减小）
  --no-vad              禁用语音活动检测（默认开启）
  --vad-threshold T     VAD 语音概率阈值（默认：0.5）
  --vad-neg-threshold T VAD 结束语音的负阈值（默认：自动）
  --vad-onset T         --vad-threshold 的别名（遗留）
  --vad-offset T        --vad-neg-threshold 的别名（遗留）
  --min-speech-duration MS  最小语音段持续时间（毫秒）（默认：0）
  --max-speech-duration SEC 最大语音段持续时间（秒）（默认：无限制）
  --min-silence-duration MS 最小静音间隔分割段（毫秒）（默认：2000）
  --speech-pad MS       语音段周围的填充（毫秒）（默认：400）
  --no-batch            禁用批量推理（使用标准 WhisperModel）
  --hallucination-silence-threshold SEC
                        跳过模型幻觉的静音部分（例如 1.0）
  --no-condition-on-previous-text
                        不要基于前文进行条件化（减少重复/幻觉循环；
                        根据 HuggingFace 建议，distil 模型自动启用）
  --condition-on-previous-text
                        强制启用基于前文的条件化（覆盖 distil 模型的自动禁用）
  --compression-ratio-threshold RATIO
                        过滤高于此压缩比的分段（默认：2.4）
  --log-prob-threshold PROB
                        过滤低于此平均对数概率的分段（默认：-1.0）
  --max-new-tokens N    每个段的最大令牌数（防止失控生成）
  --clip-timestamps RANGE
                        转录特定时间范围：'30,60' 或 '0,30;60,90'（秒）
  --progress            显示转录进度条
  --best-of N           非零温度采样时的候选项（默认：5）
  --patience F          并行搜索耐心因子（默认：1.0）
  --repetition-penalty F  重复令牌的惩罚（默认：1.0）
  --no-repeat-ngram-size N  防止此大小的 n-gram 重复（默认：0 = 关闭）

高级推理：
  --no-timestamps       输出文本不带时间信息（更快；与
                        --word-timestamps、--format srt/vtt/tsv、--diarize 不兼容）
  --chunk-length N      批量推理的音频块长度（秒）（默认：自动）
  --language-detection-threshold T
                        语言自动检测的置信度阈值（默认：0.5）
  --language-detection-segments N
                        用于语言检测的音频段数（默认：1）
  --length-penalty F    并行搜索长度惩罚；>1 倾向于更长，<1 倾向于更短（默认：1.0）
  --prompt-reset-on-temperature T
                        当温度备用达到阈值时重置初始提示（默认：0.5）
  --no-suppress-blank   禁用空白令牌抑制（可能有助于软/安静语音）
  --suppress-tokens IDS 逗号分隔的额外要抑制的令牌 ID（默认 -1）
  --max-initial-timestamp T
                        第一个段的最大时间戳（秒）（默认：1.0）
  --prepend-punctuations CHARS
                        合并到前一个单词的标点字符（默认："'¿([{-)
  --append-punctuations CHARS
                        合并到下一个单词的标点字符（默认： "'.。,，!！?？:：")]}、")

预处理：
  --normalize           转录前归一化音频音量（EBU R128 loudnorm）
  --denoise             转录前应用降噪（高通 + FFT 降噪）

高级：
  --diarize             说话人分割（需要 pyannote.audio）
  --min-speakers N      为分割提示的最小说话人数
  --max-speakers N      为分割提示的最大说话人数
  --speaker-names NAMES 逗号分隔的名称用于替换 SPEAKER_1、SPEAKER_2（例如 'Alice,Bob'）
                        需要 --diarize
  --min-confidence PROB 过滤低于此平均单词置信度的段（0.0–1.0）
  --skip-existing       跳过输出已存在的文件（批量模式）
  --detect-language-only
                        检测语言并退出（不转录）。输出："Language: en (probability: 0.984)"
                        使用 --format json：{"language": "en", "language_probability": 0.984}
  --stats-file PATH     转录后写入 JSON 统计文件（处理时间、RTF、单词数等）
                        目录路径 → 在内部写入 {stem}.stats.json；文件路径 → 精确路径
  --burn-in OUTPUT      将字幕烧录到原始视频（仅单文件模式；需要 ffmpeg）
  --filter-hallucinations
                        过滤常见的 Whisper 幻觉：音乐/掌声标记、重复段、
                        '感谢观看'、孤立标点等。
  --keep-temp           保留 URL 下载的临时文件（用于重新处理而无需重新下载）
  --parallel N          批量处理的并行工作线程数（默认：顺序）
  --retries N           重试失败文件最多 N 次，指数退避（默认：0；
                        与 --parallel 不兼容）

批量 ETA：
自动显示在顺序批量作业中（无需标志）。每个文件完成后，
下一个文件的进度行包括：[当前/总数] 文件名 | ETA: Xm Ys
ETA 根据平均每个文件时间 × 剩余文件计算。
显示到 stderr（通过 OpenClaw/Clawdbot 输出给用户）。

语言映射（每个文件语言覆盖）：
  --language-map MAP    批量模式下的每个文件语言覆盖。两种形式：
                          内联："interview*.mp3=en,lecture.wav=fr,keynote.wav=de"
                          JSON 文件： "@/path/to/map.json"  （必须是 {pattern: lang} 字典）
                        模式支持对文件名或 stem 进行 fnmatch 通配符。
                        优先级：精确文件名 > 精确 stem > 文件名 glob > stem glob > 落后。
                        未匹配的文件会落后到 --language（或未设置时自动检测）。

转录搜索：
  --search TERM         在转录中搜索 TERM 并打印带时间戳的匹配段。
                        替代正常转录输出（使用 -o 保存结果到文件）。
                        默认为不区分大小写的精确子字符串匹配。
  --search-fuzzy        启用 --search 的模糊/近似匹配（适用于拼写错误、发音近似
                        或部分单词；使用 SequenceMatcher 比率 ≥ 0.6）

章节检测：
  --detect-chapters     从静音间隔自动检测章节/段落分割并打印章节标记。
                        输出打印在转录后（或到 --chapters-file）。
  --chapter-gap SEC     连续段之间开始新章节的最低静音间隔（秒）（默认：8.0）。
                        调整密度较高的语音下调，稀疏内容上调。
  --chapters-file PATH  将章节标记写入此文件（默认：转录后 stdout）
  --chapter-format FMT  youtube | text | json — 章节输出格式：
                          youtube: "0:00 Chapter 1"（YouTube 描述准备）
                          text:    "Chapter 1: 00:00:00"
                          json:    包含章节、开始、标题字段的 JSON 数组
                        （默认：youtube）

说话人音频导出：
  --export-speakers DIR  分割后，将每个说话人的音频转轮导出为 DIR 中的
                        单独 WAV 文件。需要 --diarize 和 ffmpeg。
                        输出：SPEAKER_1.wav、SPEAKER_2.wav、…（如果设置了 --speaker-names 则为真实姓名）

RSS / Podcast：
  --rss URL             Podcast RSS 提供程序 URL — 提取音频封装并转录。
                        AUDIO 位置在 --rss 使用时可选。
  --rss-latest N        要处理的最新节目数量（默认：5；0 = 所有节目）

设备：
  --device DEV          auto | cpu | cuda (默认：auto)
  --compute-type TYPE   auto | int8 | int8_float16 | float16 | float32 (默认：auto)
                        int8_float16 = GPU 的混合模式（节省 VRAM，最小质量损失）
  --threads N           CTranslate2 的 CPU 线程数（默认：auto）
  -q, --quiet           抑制进度和状态消息
  --log-level LEVEL     设置 faster_whisper 库的日志级别：debug | info | warning | error
                        （默认：warning；使用 debug 查看CTranslate2/VAD 内部）

工具：
  --version             打印已安装的 faster-whisper 版本并退出
  --update              在技能 venv 中升级 faster-whisper 并退出

## 输出格式

### 文本（默认）

纯文本转录。使用 --diarize 时插入说话人标签：

```
[SPEAKER_1]
 你好，欢迎参加会议。
[SPEAKER_2]
 谢谢邀请我。
```

### JSON (`--format json`)

包含分段、时间戳、语言检测和性能统计的完整元数据：

```json
{
  "file": "audio.mp3",
  "text": "你好，欢迎...",
  "language": "en",
  "language_probability": 0.98,
  "duration": 600.5,
  "segments": [...],
  "speakers": ["SPEAKER_1", "SPEAKER_2"],
  "stats": {
    "processing_time": 28.3,
    "realtime_factor": 21.2
  }
}
```

### SRT (`--format srt`)

视频播放器使用的标准字幕格式：

```
1
00:00:00,000 --> 00:00:02,500
[SPEAKER_1] 你好，欢迎参加会议。

2
00:00:02,800 --> 00:00:04,200
[SPEAKER_2] 谢谢邀请我。
```

### VTT (`--format vtt`)

Web 视频播放器使用的 WebVTT 格式：

```
WEBVTT

1
00:00:00.000 --> 00:00:02.500
[SPEAKER_1] 你好，欢迎参加会议。

2
00:00:02.800 --> 00:00:04.200
[SPEAKER_2] 谢谢邀请我。
```

### TSV (`--format tsv`)

制表符分隔值，OpenAI Whisper 兼容。列：`start_ms`、`end_ms`、`text`：

```
0	2500	你好，欢迎参加会议。
2800	4200	谢谢邀请我。
```

适用于将内容管道传输到其他工具或电子表格。无标题行。

### ASS/SSA (`--format ass`)

高级 SubStation Alpha 格式 — 被 Aegisub、VLC、mpv、MPC-HC 和大多数视频编辑器支持。比 SRT 提供更丰富的样式（字体、大小、颜色、位置）通过 `[V4+ Styles]` 部分：

```
[Script Info]
ScriptType: v4.00+
...

[V4+ Styles]
Style: Default,Arial,20,&H00FFFFFF,...

[Events]
Format: Layer, Start, End, Style, Name, ..., Text
Dialogue: 0,0:00:00.00,0:00:02.50,Default,,[SPEAKER_1] 你好，欢迎。
Dialogue: 0,0:00:02.80,0:00:04.20,Default,,[SPEAKER_2] 谢谢邀请我。
```

时间戳使用 `H:MM:SS.cc`（百分之一秒）。在 Aegisub 中编辑 `[V4+ Styles]` 块以自定义字体、颜色和位置，而无需重新转录。

### LRC (`--format lrc`)

音乐播放器（例如 Foobar2000、VLC、AIMP）使用的定时歌词格式。时间戳使用 `[mm:ss.xx]`，其中 `xx` = 百分之一秒：

```
[00:00.50]你好，欢迎参加会议。
[00:02.80]谢谢邀请我。
```

使用 --diarize 时包含说话人标签：

```
[00:00.50][SPEAKER_1] 你好，欢迎参加会议。
[00:02.80][SPEAKER_2] 谢谢邀请我。
```

默认文件扩展名：`.lrc`。适用于音乐转录、卡拉OK和任何需要与音乐播放器兼容的定时文本的工作流程。

## 说话人分割

使用 [pyannote.audio](https://github.com/pyannote/pyannote-audio) 识别谁在何时说话。

**设置：**

```bash
./setup.sh --diarize
```

**要求：**

- HuggingFace 令牌位于 `~/.cache/huggingface/token` (`huggingface-cli login`)
- 接受模型协议：
  - https://hf.co/pyannote/speaker-diarization-3.1
  - https://hf.co/pyannote/segmentation-3.0

**使用：**

```bash
# 基本分割（文本输出）
./scripts/transcribe meeting.wav --diarize

# 分割字幕
./scripts/transcribe meeting.wav --diarize --format srt -o meeting.srt

# 分割 JSON（包含说话人列表）
./scripts/transcribe meeting.wav --diarize --format json
```

说话人按首次出现顺序标记为 `SPEAKER_1`、`SPEAKER_2` 等。如果 CUDA 可用，分割自动在 GPU 上运行。

## 精确单词时间戳

每当计算单词级时间戳（`--word-timestamps`、`--diarize` 或 `--min-confidence`）时，
wav2vec2 强制对齐会自动将其从 Whisper 的 ~100-200ms 精度优化到 ~10ms。
无需额外标志。

# 使用自动 wav2vec2 对齐的单词时间戳
./scripts/transcribe audio.mp3 --word-timestamps --format json

# 聚合也自动获得精确对齐
./scripts/transcribe meeting.wav --diarize

# 精确的字幕
./scripts/transcribe audio.mp3 --word-timestamps --format srt -o subtitles.srt
```

使用 torchaudio 的 MMS（多语言语音）模型——支持 1000 多种语言。模型在首次加载后会被缓存，因此批量处理仍然快速。

## URL 和 YouTube 输入

将任何 URL 作为输入——音频会自动通过 yt-dlp 下载：

```bash
# YouTube 视频
./scripts/transcribe https://youtube.com/watch?v=dQw4w9WgXcQ

# 直接音频 URL
./scripts/transcribe https://example.com/podcast.mp3

# 带选项
./scripts/transcribe https://youtube.com/watch?v=... --language en --format srt -o subs.srt
```

需要 `yt-dlp`（检查 PATH 和 `~/.local/share/pipx/venvs/yt-dlp/bin/yt-dlp`）。

## 批量处理

使用通配符模式、目录或多个路径一次性处理多个文件：

```bash
# 当前目录中的所有 MP3
./scripts/transcribe *.mp3

# 整个目录（自动过滤音频文件）
./scripts/transcribe ./recordings/

# 输出到目录（每个输入一个文件）
./scripts/transcribe *.mp3 -o ./transcripts/

# 跳过已翻译的文件（恢复中断的批量）
./scripts/transcribe *.mp3 --skip-existing -o ./transcripts/

# 混合输入
./scripts/transcribe file1.mp3 file2.wav ./more-recordings/

# 批量 SRT 字幕
./scripts/transcribe *.mp3 --format srt -o ./subtitles/
```

当输出到目录时，文件名格式为 `{input-stem}.{ext}`（例如，`audio.mp3` → `audio.srt`）。

批量模式在所有文件完成后会打印摘要：

```
📊 完成：12 个文件，3h24m 音频在 10m15s 内（19.9× 实时）
```

## 工作流

针对常见用例的端到端管道。

### 播客转录管道

从任何播客 RSS 提取最新的 5 期内容并转录：

```bash
# 转录最新 5 期 → 每期一个 .txt 文件
./scripts/transcribe --rss https://feeds.megaphone.fm/mypodcast -o ./transcripts/

# 所有期数，作为 SRT 字幕
./scripts/transcribe --rss https://... --rss-latest 0 --format srt -o ./subtitles/

# 跳过已完成的期数（安全地重新运行）
./scripts/transcribe --rss https://... --skip-existing -o ./transcripts/

# 带聚合（谁说的什么）+ 不稳定网络重试
./scripts/transcribe --rss https://... --diarize --retries 2 -o ./transcripts/
```

### 会议笔记管道

转录会议录音并添加说话者标签，然后输出干净的文本：

```bash
# 聚合 + 标记说话者（将 SPEAKER_1/2 替换为真实姓名）
./scripts/transcribe meeting.wav --diarize --speaker-names "Alice,Bob" -o meeting.txt

# 聚合的 JSON 用于后处理（摘要、行动项）
./scripts/transcribe meeting.wav --diarize --format json -o meeting.json

# 边转录边流式传输（长会议）
./scripts/transcribe meeting.wav --stream
```

### 视频字幕管道

为视频文件生成可直接使用的字幕：

```bash
# SRT 字幕带句子合并（更好的可读性）
./scripts/transcribe video.mp4 --format srt --merge-sentences -o subtitles.srt

# 将字幕直接烧录到视频中
./scripts/transcribe video.mp4 --format srt --burn-in video_subtitled.mp4

# 字幕级 SRT（卡拉OK 风格），每条提示最多 8 个词
./scripts/transcribe video.mp4 --format srt --word-timestamps --max-words-per-line 8 -o subs.srt
```

### YouTube 批量管道

一次性转录多个 YouTube 视频：

```bash
# 一行命令：转录播放列表视频 + 输出 SRT
./scripts/transcribe "https://youtube.com/watch?v=abc123" --format srt -o subs.srt

# 从 URL 文本文件批量（每行一个 URL）
cat urls.txt | xargs ./scripts/transcribe -o ./transcripts/

# 先下载音频，再转录（用于重复使用而无需重新下载）
./scripts/transcribe https://youtube.com/watch?v=abc123 --keep-temp
```

### 噪声音频管道

在转录前清理音质差的录音：

```bash
# 去噪 + 归一化，然后转录
./scripts/transcribe interview.mp3 --denoise --normalize -o interview.txt

# 噪声批量处理，使用激进的幻觉过滤
./scripts/transcribe *.mp3 --denoise --filter-hallucinations -o ./out/
```

### 批量恢复管道

使用重试处理大文件夹——失败后可安全重新运行：

```bash
# 每个失败文件最多重试 3 次，跳过已完成的
./scripts/transcribe ./recordings/ --skip-existing --retries 3 -o ./transcripts/

# 查看失败情况（打印在批量摘要末尾）
# 重新运行相同命令——跳过成功项，重试失败项
```

## 服务器模式（兼容 OpenAI API）

[speches](https://github.com/speches-ai/speches) 以 OpenAI 兼容的 `/v1/audio/transcriptions` 端点运行更快-whisper——是 OpenAI Whisper API 的即插即用替代品，支持流式传输、Docker 支持和实时转录。

### 快速启动（Docker）

```bash
docker run --gpus all -p 8000:8000 ghcr.io/speches-ai/speches:latest-cuda
```

### 测试

```bash
# 通过 API 转录文件（与 OpenAI 格式相同）
curl http://localhost:8000/v1/audio/transcriptions \
  -F file=@audio.mp3 \
  -F model=Systran/faster-whisper-large-v3
```

### 与任何 OpenAI SDK 一起使用

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000", api_key="none")
with open("audio.mp3", "rb") as f:
    result = client.audio.transcriptions.create(model="Systran/faster-whisper-large-v3", file=f)
print(result.text)
```

当你想将转录作为本地 API 为其他工具（Home Assistant、n8n、自定义应用程序）提供时，这很有用。

## 常见错误

| 错误                                                         | 问题                                     | 解决方案                                                                 |
| ------------------------------------------------------------ | ------------------------------------------- | -------------------------------------------------------------------------------- |
| **使用 CPU 而不是 GPU**                                      | 转录速度慢 10-20 倍                       | 检查 `nvidia-smi`；验证 CUDA 安装                                         |
| **未指定语言**                                              | 在已知内容上浪费时间自动检测             | 当你知道语言时使用 `--language en`                                        |
| **使用错误的模型**                                          | 不必要的速度慢或准确性差                 | 默认 `distil-large-v3.5` 非常出色；只有准确性有问题时才使用 `large-v3`       |
| **忽略蒸馏模型**                                            | 错过 6 倍速度提升，准确性损失 <1%         | 在使用标准模型之前尝试 `distil-large-v3.5`                              |
| **忘记 ffmpeg**                                             | 设置失败或无法处理音频                   | 设置脚本会处理；手动安装需要单独安装 ffmpeg                              |
| **内存错误**                                                | 模型太大无法适应可用的 VRAM/RAM          | 使用较小模型、`--compute-type int8` 或 `--batch-size 4`                    |
| **过度设计 beam size**                                     | 超过 beam-size 5-7 后收益递减             | 默认 5 很好；对关键转录尝试 10                                             |
| **--diarize 而没有 pyannote**                               | 运行时导入错误                           | 首先运行 `setup.sh --diarize`                                             |
| **--diarize 而没有 HuggingFace 令牌**                       | 模型下载失败                             | 运行 `huggingface-cli login` 并接受模型协议                              |
| **URL 输入而没有 yt-dlp**                                   | 下载失败                                | 安装：`pipx install yt-dlp`                                               |
| **--min-confidence 太高**                                   | 滑落带有自然停顿的好片段                   | 从 0.5 开始，向上调整；检查 JSON 输出中的概率                           |
| **使用 --word-timestamps 进行基本转录**                     | 添加 ~5-10s 开销，但收益微乎其微         | 只有在需要单词级精度时才使用                                               |
| **批量处理而没有 -o 目录**                                  | 所有输出混合在 stdout 中                  | 使用 `-o ./transcripts/` 将每个输入写入一个文件                            |

## 性能说明

- **首次运行**：模型下载到 `~/.cache/huggingface/`（一次性）
- **批量推理**：默认通过 `BatchedInferencePipeline` 启用——比标准模式快 3 倍；VAD 默认开启
- **GPU**：如果可用，自动使用 CUDA
- **量化**：CPU 上使用 INT8，速度提升 4 倍，准确性损失最小
- **性能统计**：每次转录都显示音频时长、处理时间和实时因子
- **基准**（RTX 3070，21 分钟文件）：**~24s** 使用批量推理（distil-large-v3 和 v3.5） vs ~69s 不使用
- **--precise 开销**：添加 ~5-10s 用于 wav2vec2 模型加载和对齐（模型在批量中缓存）
- **聚合开销**：根据音频长度增加 ~10-30s（如果可用则在 GPU 上运行）
- **内存**：
  - `distil-large-v3`：~2GB RAM / ~1GB VRAM
  - `large-v3-turbo`：~4GB RAM / ~2GB VRAM
  - `tiny/base`：<1GB RAM
  - 聚合：额外 ~1-2GB VRAM
- **OOM**：如果遇到内存错误，降低 `--batch-size`（尝试 4）
- **预转换为 WAV**（可选）：`ffmpeg -i input.mp3 -ar 16000 -ac 1 input.wav` 转换为 16kHz 单声道 WAV 之前转录。对于一次性使用，收益很小（~5%），因为 PyAV 高效解码——当多次重新处理同一文件（研究/实验）或格式导致 PyAV 解码问题时最有用。注意：`--normalize` 和 `--denoise` 已经自动执行此转换。
- **Silero VAD V6**：faster-whisper 1.2.1 升级到 Silero VAD V6（改进的语音检测）。运行 `./setup.sh --update` 获取它。
- **批量静音去除**：faster-whisper 1.2.0+ 在 `BatchedInferencePipeline`（默认使用）中自动去除静音。如果 2024 年 8 月之前安装，请使用 `./setup.sh --update` 获取此功能。

## 为什么使用 faster-whisper？

- **速度**：比 OpenAI 的原始 Whisper 快 4-6 倍
- **准确性**：相同（使用相同的模型权重）
- **效率**：通过量化降低内存使用
- **生产就绪**：稳定的 C++ 后端（CTranslate2）
- **蒸馏模型**：~6 倍速度提升，准确性损失 <1%
- **字幕**：原生 SRT/VTT/HTML 输出
- **精确对齐**：自动 wav2vec2 精炼（~10ms 单词边界）
- **聚合**：可选的说话者识别 via pyannote；`--speaker-names` 映射到真实姓名
- **URL**：直接 YouTube/URL 输入；`--keep-temp` 保留下载的音频以供重新使用
- **自定义模型**：加载本地 CTranslate2 目录或 HuggingFace 仓库；`--model-dir` 控制缓存
- **质量控制**：`--filter-hallucinations` 删除音乐/掌声标记和重复项
- **并行批量**：`--parallel N` 用于多线程批量处理
- **字幕烧录**：`--burn-in` 通过 ffmpeg 将字幕直接烧录到视频中

### v1.5.0 新功能

**多格式输出：**

- `--format srt,text` — 一次通过同时写入多种格式（例如 SRT + 纯文本）
- 接受逗号分隔列表：`srt,vtt,json`, `srt,text`, 等
- 写入多种格式时需要 `-o <dir>`；单个格式不变

**填充词去除：**

- `--clean-filler` — 从转录文本中删除犹豫音（um, uh, er, ah, hmm, hm）和话语标记（you know, I mean, you see）；默认关闭
- 在单词边界进行保守的正则表达式匹配以避免误报
- 清理后变为空的片段会自动删除

**立体声道选择：**

- `--channel left|right|mix` — 转录前提取特定的立体声道（默认：mix）
- 用于双轨录音（采访者左声道，受访者右声道）
- 使用 ffmpeg pan 滤波器；如果找不到 ffmpeg 会优雅回退到完整混音

**基于字符的字幕换行：**

- `--max-chars-per-line N` — 将字幕提示分成每行最多 N 个字符
- 适用于 SRT、VTT、ASS 和 TTML 格式；优先于 `--max-words-per-line`
- 需要单词级时间戳；如果没有单词数据，回退到完整片段

**段落检测：**

- `--detect-paragraphs` — 在文本输出中在自然边界处插入 `\n\n` 段落分隔符
- `--paragraph-gap SEC` — 段落的最小静音间隔（默认：3.0s）
- 还会在前一个片段结束句子且间隔 ≥ 1.5s 时检测段落分隔符

**字幕格式：**

- `--format ass` — 高级字幕（Aegisub、VLC、mpv、MPC-HC）
- `--format lrc` — 音乐播放器的时间歌词格式
- `--format html` — 置信度着色的 HTML 转录（每个单词绿色/黄色/红色）
- `--format ttml` — W3C TTML 1.0（DFXP）广播标准（Netflix、Amazon Prime、BBC）
- `--format csv` — 电子表格友好的 CSV，带标题行；RFC 4180 引号；`speaker` 列在聚合时使用

**转录工具：**

- `--search TERM` — 查找单词/短语出现的时间戳；替换正常输出；`-o` 保存
- `--search-fuzzy` — `--search` 的近似/部分匹配
- `--detect-chapters` — 自动检测静音间隔中的章节；`--chapter-gap SEC`（默认 8s）
- `--chapters-file PATH` — 将章节写入文件而不是 stdout；`--chapter-format youtube|text|json`
- `--export-speakers DIR` — 在 `--diarize` 后，将每个说话者的发言保存为单独的 WAV 文件 via ffmpeg

**批量改进：**

- **ETA** — `[N/total] filename | ETA: Xm Ys` 在顺序批量中每个文件之前显示；不需要标志
- `--language-map "pat=lang,..."` — 每个文件的语言覆盖；fnmatch 通配符模式；`@file.json` 形式
- `--retries N` — 指数退避重试失败文件；末尾显示失败文件摘要
- `--rss URL` — 转录播客 RSS 源；`--rss-latest N` 用于期数
- `--skip-existing` / `--parallel N` / `--output-template` / `--stats-file` / `--merge-sentences`

**模型与推理：**

- 默认 `distil-large-v3.5`（替换了 distil-large-v3）
- 自动禁用 distil 模型的 `condition_on_previous_text`（防止重复循环）
- `--condition-on-previous-text` 覆盖；`--log-level` 用于库调试输出
- `--model-dir PATH` — 自定义 HuggingFace 缓存目录；支持本地 CTranslate2 模型
- `--no-timestamps`, `--chunk-length`, `--length-penalty`, `--repetition-penalty`, `--no-repeat-ngram-size`
- `--clip-timestamps`, `--stream`, `--progress`, `--best-of`, `--patience`, `--max-new-tokens`
- `--hotwords`, `--prefix`, `--revision`, `--suppress-tokens`, `--max-initial-timestamp`

**说话者与质量：**

- `--speaker-names "Alice,Bob"` — 将 SPEAKER_1/2 替换为真实姓名（需要 `--diarize`）
- `--filter-hallucinations` — 删除音乐/掌声标记、重复项、"Thank you for watching"
- `--burn-in OUTPUT` — 通过 ffmpeg 将字幕烧录到视频中
- `--keep-temp` — 保留 URL 下载的音频以供重新处理

**设置：**

- `setup.sh --check` — 系统诊断：GPU、CUDA、Python、ffmpeg、pyannote、HuggingFace 令牌（约 12s 完成）
- ffmpeg 不再需要基本转录（PyAV 处理解码）；`skill.json` 已更新以反映这一点（`ffmpeg` 现在是 `optionalBins`）

## 故障排除

**"CUDA不可用 — 使用CPU"**: 安装带有CUDA的PyTorch（见上方GPU支持）
**设置失败**: 确保已安装Python 3.10+
**内存不足**: 使用较小的模型、`--compute-type int8` 或 `--batch-size 4`
**CPU运行缓慢**: 预期如此 — 使用GPU进行实际转录
**模型下载失败**: 检查 `~/.cache/huggingface/` 的权限
**语音分割模型失败**: 确保存在HuggingFace token并接受模型协议；
或直接使用 `--hf-token hf_xxx` 传递token
**URL下载失败**: 检查是否已安装yt-dlp (`pipx install yt-dlp`)
**批处理中无音频文件**: 检查文件扩展名是否匹配支持的格式
**检查已安装版本**: 运行 `./scripts/transcribe --version`
**升级faster-whisper**: 运行 `./setup.sh --update`（原地升级，无需完整重装）
**静音/音乐中出现幻觉**: 尝试 `--temperature 0.0 --no-speech-threshold 0.8`
**VAD错误分割语音**: 使用 `--vad-threshold 0.3`（降低）或 `--min-silence-duration 300` 调整
**提高语音检测**: 运行 `./setup.sh --update` 升级faster-whisper到最新版本（包含Silero VAD V6）。

## 参考文献

- [faster-whisper GitHub](https://github.com/SYSTRAN/faster-whisper)
- [Distil-Whisper 论文](https://arxiv.org/abs/2311.00430)
- [HuggingFace模型](https://huggingface.co/collections/Systran/faster-whisper)
- [pyannote.audio](https://github.com/pyannote/pyannote-audio)（语音分割）
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)（URL/YouTube下载）
