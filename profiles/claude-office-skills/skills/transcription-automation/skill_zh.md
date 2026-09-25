# 自动语音转写

全面的技能，用于自动处理音频/视频转写和内容处理。

## 核心工作流

### 1. 转写工作流

```
转写流程：
┌─────────────────┐
│  音频/视频      │
│     输入       │
└────────┬────────┘
         ▼
┌─────────────────┐
│  预处理        │
│  - 转换        │
│  - 增强        │
│  - 分割        │
└────────┬────────┘
         ▼
┌─────────────────┐
│  转写        │
│  - STT 引擎   │
│  - 分说话人    │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 后处理        │
│  - 格式        │
│  - 时间戳      │
│  - 说话人      │
└────────┬────────┘
         ▼
┌─────────────────┐
│     输出      │
│  - 文本/SRT/VTT │
│  - 摘要      │
└─────────────────┘
```

### 2. 转写配置

```yaml
transcription_config:
  engine: whisper  # whisper, assembly_ai, deepgram
  
  audio_settings:
    sample_rate: 16000
    channels: mono
    format: wav
    
  transcription:
    language: auto  # 或特定: en, zh, es
    model: large  # tiny, base, small, medium, large
    task: transcribe  # transcribe 或 translate
    
  features:
    speaker_diarization: true
    word_timestamps: true
    punctuation: true
    profanity_filter: false
    
  output:
    formats:
      - txt
      - srt
      - vtt
      - json
    include_confidence: true
    include_timestamps: true
```

## 会议转写

### 会议笔记模板

```yaml
meeting_transcript:
  metadata:
    title: "{{meeting_title}}"
    date: "{{date}}"
    duration: "{{duration}}"
    attendees: "{{speakers}}"
    
  output_template: |
    # {{title}}
    
    **日期:** {{date}}
    **时长:** {{duration}}
    **参会人员:** {{attendees}}
    
    ## 摘要
    {{ai_summary}}
    
    ## 关键点
    {{#each key_points}}
    - {{this}}
    {{/each}}
    
    ## 行动项
    {{#each action_items}}
    - [ ] {{task}} - @{{assignee}} - 截止日期: {{due_date}}
    {{/each}}
    
    ## 完整转写
    {{#each segments}}
    **[{{timestamp}}] {{speaker}}:** {{text}}
    
    {{/each}}
```

### 说话人分割

```yaml
diarization_config:
  min_speakers: 2
  max_speakers: 10
  
  speaker_labels:
    - name: "说话人 1"
      voice_sample: "sample_1.wav"  # 可选
    - name: "说话人 2"
      voice_sample: "sample_2.wav"
      
  output_format:
    speaker_prefix: true
    speaker_timestamps: true
    
  example_output: |
    [00:00:05] SPEAKER_1: 欢迎大家参加今天的会议。
    [00:00:12] SPEAKER_2: 谢谢邀请我们。
    [00:00:18] SPEAKER_1: 让我们开始议程。
```

## 字幕生成

### SRT 格式

```yaml
subtitle_config:
  format: srt
  
  timing:
    max_duration: 7  # 每个字幕的秒数
    min_gap: 0.1     # 字幕之间的秒数
    chars_per_line: 42
    max_lines: 2
    
  style:
    case: sentence  # sentence, upper, lower
    numbers: words  # words, digits
    
  example_output: |
    1
    00:00:05,000 --> 00:00:08,500
    欢迎参加今天的演示
    关于自动语音转写。
    
    2
    00:00:09,000 --> 00:00:12,000
    让我先解释
    基本概念。
```

### VTT 格式

```yaml
vtt_config:
  format: vtt
  
  features:
    cue_settings: true
    styling: true
    
  example_output: |
    WEBVTT
    
    00:00:05.000 --> 00:00:08.500 align:center
    欢迎参加今天的演示
    关于自动语音转写。
    
    00:00:09.000 --> 00:00:12.000 align:center
    <v Speaker 1>让我先解释
    基本概念。
```

## 集成工作流

### Zoom 集成

```yaml
zoom_transcription:
  trigger:
    event: recording_completed
    
  workflow:
    - step: download_recording
      source: zoom_cloud
      
    - step: transcribe
      engine: whisper
      language: auto
      
    - step: diarize
      identify_speakers: true
      
    - step: generate_notes
      template: meeting_notes
      include_summary: true
      extract_action_items: true
      
    - step: distribute
      destinations:
        - notion_page
        - slack_channel
        - email_attendees
```

### YouTube 集成

```yaml
youtube_subtitles:
  trigger:
    event: video_uploaded
    
  workflow:
    - step: download_audio
      source: youtube_video
      
    - step: transcribe
      engine: whisper
      task: transcribe
      
    - step: generate_subtitles
      formats: [srt, vtt]
      
    - step: translate
      target_languages: [es, zh, ja, de, fr]
      
    - step: upload_subtitles
      destination: youtube
      as_cc: true
```

### 播客处理

```yaml
podcast_workflow:
  input:
    source: rss_feed
    format: audio/mp3
    
  processing:
    - transcribe:
        engine: whisper
        model: large
        
    - generate_chapters:
        detect_topics: true
        min_duration: 60  # 秒
        
    - create_show_notes:
        summarize: true
        extract_links: true
        highlight_quotes: true
        
    - create_searchable_index:
        full_text: true
        timestamps: true
        
  output:
    - transcript_txt
    - chapters_json
    - show_notes_md
    - search_index
```

## 语言支持

### 多语言转写

```yaml
multilingual:
  auto_detect: true
  
  supported_languages:
    - code: en
      name: English
      model: large
      
    - code: zh
      name: Chinese
      model: large
      
    - code: es
      name: Spanish
      model: large
      
    - code: ja
      name: Japanese
      model: medium
      
  translation:
    enabled: true
    target: en
    preserve_original: true
```

### 代码转换

```yaml
code_switching:
  enabled: true
  primary_language: en
  secondary_languages: [zh, es]
  
  output: |
    [00:01:23] 下一个话题是关于人工智能，
    这在近年来非常重要。
    
  handling:
    detect_language_per_segment: true
    tag_language_switches: true
```

## 质量增强

### 后处理

```yaml
post_processing:
  text_cleanup:
    - remove_filler_words: ["um", "uh", "like"]
    - fix_common_errors: true
    - normalize_numbers: true
    
  formatting:
    - add_punctuation: true
    - capitalize_sentences: true
    - paragraph_breaks: true
    
  speaker_attribution:
    - merge_short_segments: true
    - min_segment_duration: 1.0
    
  output_enhancement:
    - add_timestamps: true
    - highlight_keywords: true
    - generate_summary: true
```

### 准确率指标

```
转写质量报告
═══════════════════════════════════════

文件: meeting_2024_01_15.mp3
时长: 45:32
引擎: Whisper Large

指标:
词错误率 (WER):  4.2%
字符错误率:   2.8%
置信度得分:       0.94

说话人分割:
检测到的说话人: 4
分割准确率: 91%

处理时间:
总计: 8m 23s
实时因子: 0.18x

检测到的问题:
• 12:34 置信度低（背景噪音）
• 23:45 说话重叠
• 34:12 未知说话人
```

## API 示例

### OpenAI Whisper

```python
import openai

# 转写音频
with open("meeting.mp3", "rb") as audio_file:
    transcript = openai.Audio.transcribe(
        model="whisper-1",
        file=audio_file,
        response_format="verbose_json",
        timestamp_granularities=["word", "segment"]
    )

# 访问结果
for segment in transcript.segments:
    print(f"[{segment.start:.2f}] {segment.text}")
```

### AssemblyAI

```python
import assemblyai as aai

transcriber = aai.Transcriber()

config = aai.TranscriptionConfig(
    speaker_labels=True,
    auto_chapters=True,
    entity_detection=True
)

transcript = transcriber.transcribe(
    "https://example.com/meeting.mp3",
    config=config
)

for utterance in transcript.utterances:
    print(f"说话人 {utterance.speaker}: {utterance.text}")
```

## 最佳实践

1. **高质量音频**: 干净的输入 = 更好的输出
2. **选择合适的模型**: 平衡速度与准确率
3. **使用说话人分割**: 清晰识别说话人
4. **后处理**: 清理自动输出
5. **验证关键内容**: 人工审核重要内容
6. **考虑隐私**: 处理敏感内容
7. **高效存储**: 压缩和索引
8. **提供上下文**: 词汇提示有帮助
