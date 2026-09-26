## 详细指南

在执行此技能之前，请阅读[详细指南](references/detailed-guide.md)。该指南保留了完整流程和参考材料。请将其安全要求、前提条件和验证要求视为强制性。对于专注工作，加载相关部分；对于端到端工作，请完整阅读指南。

## 使用场景
在以下情况下调用此技能：

- 用户需要将音频/视频文件转录为文本
- 用户希望从录音中自动生成会议纪要
- 用户需要在对话中进行说话人识别（声纹分割）
- 用户需要字幕/旁白（SRT、VTT 格式）
- 用户希望获得长音频内容的执行摘要
- 用户询问“转录此音频”、“将音频转换为文本”、“从录音生成会议纪要”等变体
- 用户拥有常见格式的音频文件（MP3、WAV、M4A、OGG、FLAC、WEBM）

## 示例用法

### **示例 1：基本转录**

**用户输入：**
```bash
copilot> transcribe audio to markdown: meeting-2026-02-02.mp3
```

**技能输出：**

```bash
✅ Faster-Whisper 检测到（优化）
✅ ffmpeg 可用（格式转换已启用）

📂 文件：meeting-2026-02-02.mp3
📊 大小：12.3 MB
⏱️  时长：00:45:32

🎙️  处理中...
[████████████████████] 100%

✅ 检测到语言：葡萄牙语 (pt-BR)
👥 识别到说话人：4
📝 生成 Markdown 输出...

✅ 转录完成！

📊 结果：
  文件：meeting-2026-02-02.md
  语言：pt-BR
  时长：00:45:32
  说话人：4
  单词数：6,842
  处理时间：127s

📝 生成：
  - meeting-2026-02-02.md（Markdown 报告）

🎯 下一步：
  1. 审查会议纪要和行动项
  2. 与参与者分享报告
  3. 跟踪行动项完成情况
```

### **示例 3：批量处理**

**用户输入：**
```bash
copilot> transcreva estes áudios: recordings/*.mp3
```

**技能输出：**

```bash
📦 批量模式：找到 5 个文件
  1. team-standup.mp3
  2. client-call.mp3
  3. brainstorm-session.mp3
  4. product-demo.mp3
  5. retrospective.mp3

🎙️  批量处理中...

[1/5] team-standup.mp3 ✅ (2m 34s)
[2/5] client-call.mp3 ✅ (15m 12s)
[3/5] brainstorm-session.mp3 ✅ (8m 47s)
[4/5] product-demo.mp3 ✅ (22m 03s)
[5/5] retrospective.mp3 ✅ (11m 28s)

✅ 批量完成！
📝 生成了 5 个 Markdown 报告
⏱️  总处理时间：6m 15s
```

### **示例 5：大文件警告**

**用户输入：**
```bash
copilot> transcribe audio to markdown: conference-keynote.mp3
```

**技能输出：**

```bash
✅ Faster-Whisper 检测到（优化）

📂 文件：conference-keynote.mp3
📊 大小：87.2 MB
⏱️  时长：02:15:47
⚠️  大文件（87.2 MB）- 处理可能需要几分钟

继续？ [Y/n]:
```

**用户：** `Y`

```bash
🎙️  处理中...（这可能需要 10-15 分钟）
[████░░░░░░░░░░░░░░░░] 20% - 预计剩余时间：12m
```

此技能是 **平台无关** 的，在任何 GitHub Copilot CLI 可用的终端环境中均可工作。它不依赖于特定的项目配置或外部 API，遵循零配置理念。

## 限制
- 仅在任务明确符合上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家审查的替代品。
- 如果所需输入、权限、安全边界或成功标准缺失，请停止并请求澄清。
