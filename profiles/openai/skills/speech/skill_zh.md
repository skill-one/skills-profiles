# 语音生成技能

为当前项目生成语音音频（旁白、产品演示配音、IVR提示、无障碍阅读）。默认使用 `gpt-4o-mini-tts-2025-12-15` 和内置语音，并优先使用捆绑的CLI工具以实现确定性和可重复的运行。

## 使用场景
- 从文本生成单个语音片段
- 生成一批提示（多行、多文件）

## 决策树（单次 vs 批量）
- 如果用户提供多行/提示或需要多个输出 -> **批量**
- 否则 -> **单次**

## 工作流程
1. 确定意图：单次 vs 批量（参考上述决策树）。
2. 预先收集输入：确切的文本（逐字）、期望的语音、交付风格、格式以及任何约束条件。
3. 如果批量：在 `tmp/` 下创建一个临时的 JSONL 文件（每行一个任务），运行一次，然后删除该 JSONL 文件。
4. 将指令增强为简短的标记规范，而无需重写输入文本。
5. 使用捆绑的CLI (`scripts/text_to_speech.py`) 并使用合理的默认值（参考 `references/cli.md`）。
6. 对于重要的片段，验证：可理解性、节奏、发音以及约束条件的遵守情况。
7. 通过针对单一更改（语音、速度或指令）进行迭代，然后重新检查。
8. 保存/返回最终输出，并记录最终的文本 + 指令 + 使用的标志。

## 临时和输出规范
- 使用 `tmp/speech/` 存放中间文件（例如 JSONL 批量）；完成后删除。
- 在此代码库中工作时，将最终产物写入 `output/speech/`。
- 使用 `--out` 或 `--out-dir` 控制输出路径；保持文件名稳定且描述性。

## 依赖项（如果缺失则安装）
优先使用 `uv` 进行依赖管理。

Python包：
```
uv pip install openai
```
如果 `uv` 不可用：
```
python3 -m pip install openai
```

## 环境
- `OPENAI_API_KEY` 必须设置，以便进行实时API调用。

如果密钥缺失，请向用户提供以下步骤：
1. 在 OpenAI 平台UI中创建API密钥：https://platform.openai.com/api-keys
2. 将 `OPENAI_API_KEY` 作为环境变量设置在他们的系统中。
3. 如果需要，提供指导以帮助他们为操作系统/Shell设置环境变量。
- 不要要求用户在聊天中粘贴完整的密钥。请让他们本地设置并在准备好时确认。

如果在此环境中无法安装，请告知用户缺失的依赖项以及如何本地安装。

## 默认值和规则
- 除非用户请求其他模型，否则使用 `gpt-4o-mini-tts-2025-12-15`。
- 默认语音：`cedar`。如果用户希望更明亮的音调，优先使用 `marin`。
- 仅限内置语音。自定义语音不在此技能范围内。
- `instructions` 支持GPT-4o mini TTS模型，但不支持 `tts-1` 或 `tts-1-hd`。
- 每次请求的输入长度必须 <= 4096个字符。将较长的文本拆分成块。
- 强制执行每分钟50次请求。CLI将 `--rpm` 限制在50。
- 在任何实时API调用之前要求 `OPENAI_API_KEY`。
- 向最终用户明确披露语音是AI生成的。
- 使用OpenAI Python SDK (`openai` 包) 进行所有API调用；不要使用原始HTTP。
- 优先使用捆绑的CLI (`scripts/text_to_speech.py`) 而不是编写新的单次脚本。
- 不要修改 `scripts/text_to_speech.py`。如果缺少某些内容，请在采取其他任何行动之前询问用户。

## 指令增强
将用户指示重新格式化为简短的标记规范。仅使隐含细节明确化；不要编造新的需求。

快速澄清（增强 vs 编造）：
- 如果用户说“演示的旁白”，您可以添加隐含的交付约束（清晰、稳定节奏、友好语气）。
- 不要引入用户未请求的新角色、口音或情感风格。

模板（仅包含相关行）：
```
Voice Affect: <语音的整体角色和纹理>
Tone: <态度、正式性、温暖>
Pacing: <慢、稳定、快速>
Emotion: <要传达的关键情绪>
Pronunciation: <要清晰发音或强调的词语>
Pauses: <添加有意停顿的位置>
Emphasis: <要强调的关键词语或短语>
Delivery: <节奏或韵律说明>
```

增强规则：
- 保持简短；仅添加用户已暗示或提供在其他地方的信息。
- 不要重写输入文本。
- 如果任何关键细节缺失且阻止成功，请提问；否则继续。

## 示例

### 单次示例（旁白）
```
输入文本: "欢迎参加演示。今天我们将展示其工作原理。"
指令:
Voice Affect: 温暖而沉稳。
Tone: 友好且自信。
Pacing: 稳定且适中。
Emphasis: 强调“演示”和“展示”。
```

### 批量示例（IVR提示）
```
{"input":"感谢致电。请稍候.","voice":"cedar","response_format":"mp3","out":"hold.mp3"}
{"input":"销售请按1，支持请按2.","voice":"marin","instructions":"Tone: 清晰且中立。Pacing: 慢.","response_format":"wav"}
```

## 指令最佳实践（简短列表）
- 结构化指示为：affect -> tone -> pacing -> emotion -> pronunciation/pauses -> emphasis。
- 保持4到8行短指示；避免冲突指导。
- 对于名称/缩写，添加发音提示（例如，“逐字发音A-I”）或提供音标拼写。
- 对于编辑/迭代，重复不变量（例如，“保持节奏稳定”）以减少漂移。
- 通过单一更改的后续操作进行迭代。

更多原则：`references/prompting.md`。复制/粘贴规范：`references/sample-prompts.md`。

## 按用例的指导
在请求特定交付风格时使用这些模块。它们提供有针对性的默认值和模板。
- 旁白 / 解释：`references/narration.md`
- 产品演示 / 配音：`references/voiceover.md`
- IVR / 电话提示：`references/ivr.md`
- 无障碍阅读：`references/accessibility.md`

## CLI + 环境说明
- CLI命令 + 示例：`references/cli.md`
- API参数快速参考：`references/audio-api.md`
- 指令模式 + 示例：`references/voice-directions.md`
- 如果网络批准 / 沙盒设置造成障碍：`references/codex-network.md`

## 参考地图
- **`references/cli.md`**：如何通过 `scripts/text_to_speech.py` 运行语音生成/批量（命令、标志、配方）。
- **`references/audio-api.md`**：API参数、限制、语音列表。
- **`references/voice-directions.md`**：指令模式和示例。
- **`references/prompting.md`**：指令最佳实践（结构、约束、迭代模式）。
- **`references/sample-prompts.md`**：复制/粘贴指令配方（仅示例；无额外理论）。
- **`references/narration.md`**：旁白和解释器的模板 + 默认值。
- **`references/voiceover.md`**：产品演示配音的模板 + 默认值。
- **`references/ivr.md`**：IVR/电话提示的模板 + 默认值。
- **`references/accessibility.md`**：无障碍阅读的模板 + 默认值。
- **`references/codex-network.md`**：环境/沙盒/网络批准故障排除。
