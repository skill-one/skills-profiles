# 视频翻译

将视频中的语音翻译成另一种语言，使用 TTS 生成配音音频并替换原始音频轨道。

## 触发条件

- 翻译这个视频
- 为这个视频配音成英语
- 将视频从 X 语翻译成 Y 语
- 视频翻译

## 应用场景

- 用户想观看外语 YouTube 视频，但希望用母语收听。
- 用户提供视频链接并明确要求更改音频语言。

## 工作流程

当用户请求翻译视频时：

1. **下载视频与字幕**：
   使用 `youtube-downloader` 技能下载视频及其字幕为 SRT 格式。确保指定源语言以获取正确的字幕。
   ```bash
   python path/to/youtube-downloader/scripts/download_video.py "VIDEO_URL" --subtitles --sub-lang <source_lang_code> -o /tmp/video-translation
   ```

2. **翻译字幕**：
   读取下载的 `.srt` 文件。使用以下固定提示将字幕内容逐句翻译成目标语言。保持完全相同的 SRT 索引和时间戳格式！

   **翻译提示**：
   > 将以下字幕文本从 <源语言> 翻译成 <目标语言>。
   > 仅提供翻译后的文本。不要解释，不要添加注释，不要添加索引号。
   > 翻译必须口语化、自然，适合视频配音。

   将翻译后的文本保存到新文件 `translated.srt`。

3. **生成配音音频**：
   使用 `tts` 技能根据翻译的 SRT 生成时间轴精确的音频。Noiz 后端自动将每个句子的持续时间与原始视频的字幕时间戳对齐。

   为确保克隆的语音与原始说话者完全匹配每个句子的语气和情感，将原始视频文件传递给 `--ref-audio-track`。TTS 引擎将自动在每个字幕的精确时间戳处切割原始音频，并将其用作该特定片段的参考。

   创建基本的 `voice_map.json`：
   ```json
   {
     "default": {
       "target_lang": "<target_lang_code>"
     }
   }
   ```
   渲染时间轴精确的音频：
   ```bash
   bash skills/tts/scripts/tts.sh render --srt translated.srt --voice-map voice_map.json --backend noiz --auto-emotion --ref-audio-track original_video.mp4 -o dubbed.wav
   ```

4. **替换视频中的音频**：
   使用 `replace_audio.sh` 脚本将原始视频与新配音音频合并。为保持原始视频在翻译片段外的非语音音频背景，传递 `--srt` 文件。
   ```bash
   bash skills/video-translation/scripts/replace_audio.sh --video original_video.mp4 --audio dubbed.wav --output final_video.mp4 --srt translated.srt
   ```

5. **展示结果**：
   向用户返回 `final_video.mp4` 文件路径。

## 输入

- **必需输入**：
  - `VIDEO_URL`：要翻译的视频的 URL。
  - `target_language`：要翻译音频的语言。
- **可选输入**：
  - `source_language`：原始视频的语言（如果未自动检测或指定）。
  - `reference_audio`：用于语音克隆的特定音频文件/URL，而不是动态原始视频轨道。

## 输出

- 成功：替换音频的最终视频文件路径。
- 失败：清晰的错误消息，说明下载、TTS 或音频替换是否失败。

## 要求

- **依赖项（其他技能）**  
  - **youtube-downloader** ([crazynomad/skills](https://github.com/crazynomad/skills)) — [SKILL.md](https://github.com/crazynomad/skills/blob/master/youtube-downloader/SKILL.md)  
    安装：将 `skills/youtube-downloader` 目录从 [crazynomad/skills](https://github.com/crazynomad/skills) 克隆或复制到你的 `skills/` 文件夹中，以便 `skills/youtube-downloader/scripts/download_video.py` 可用。
  - **tts** ([NoizAI/skills](https://github.com/NoizAI/skills)) — [SKILL.md](https://github.com/NoizAI/skills/blob/main/skills/tts/SKILL.md)  
    如果不在本仓库中：将 `skills/tts` 目录从 [NoizAI/skills](https://github.com/NoizAI/skills) 克隆或复制到你的 `skills/` 文件夹中。确保 `skills/tts/scripts/tts.sh` 及相关脚本存在。
- `NOIZ_API_KEY` 配置用于 Noiz 后端。如果未设置，首先指导用户从 `https://developers.noiz.ai/api-keys` 获取 API 密钥。用户提供密钥后，询问是否要持久化；如果同意，则将 `NOIZ_API_KEY=...` 写入/更新到项目的 `.env` 文件中，或运行 `bash skills/tts/scripts/tts.sh config --set-api-key YOUR_KEY` 存储它。
- 安装 `ffmpeg`。

## 限制

- 源视频必须在平台上为源语言提供字幕（或自动生成的字幕）。
- 非常长的视频可能需要大量时间进行翻译和配音。
