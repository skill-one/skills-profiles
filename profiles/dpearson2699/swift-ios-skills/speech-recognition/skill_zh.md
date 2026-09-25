# 语音识别

使用 Apple 的 Speech 框架将实时和预录音频转录为文本。
涵盖 `SpeechAnalyzer` / `SpeechTranscriber`（iOS 26+）和
`SFSpeechRecognizer`（iOS 10+）的备用指导。

**范围边界：** 使用此技能进行语音到文本识别、语音授权、麦克风捕获管道和结果处理。将文本分析、语言识别（转录后）、情感、嵌入和翻译交给 `natural-language`；将音频播放 UI 交给 `avkit`；将摘要或转录生成交给 `apple-on-device-ai`。

## 内容

- [SpeechAnalyzer 策略（iOS 26+）](#speechanalyzer-strategy-ios-26)
- [SFSpeechRecognizer 设置](#sfspeechrecognizer-setup)
- [授权](#authorization)
- [实时麦克风转录](#live-microphone-transcription)
- [预录音频文件识别](#pre-recorded-audio-file-recognition)
- [本地与服务器识别](#on-device-vs-server-recognition)
- [处理结果](#handling-results)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## SpeechAnalyzer 策略（iOS 26+）

使用 `SpeechAnalyzer` 进行现代 iOS 26+ 语音分析，特别是长格式录音、实时转录、时间索引转录和完全本地化流程。保留 `SFSpeechRecognizer` 用于 iOS 10+ 部署目标、服务器支持的区域覆盖或现有的回调/委托实现。

在实现 iOS 26+ 转录管道、模型资源处理、易失性结果或文件/缓冲区示例时，请阅读 [SpeechAnalyzer 模式](references/speechanalyzer-patterns.md)。

### SpeechAnalyzer 设置清单

1. 选择模块：
   - `SpeechTranscriber` 用于较新的通用本地模型。
   - 当 `SpeechTranscriber` 在当前设备或区域不可用时，且可接受听写兼容支持时，使用 `DictationTranscriber`。
   - 仅在与转录器结合使用时使用 `SpeechDetector`，当语音活动检测值得准确性与功耗权衡时。
2. 在创建会话前检查支持：
   - `SpeechTranscriber.isAvailable`
   - `SpeechTranscriber.supportedLocale(equivalentTo:)`
   - 当显示语言选择时，使用 `SpeechTranscriber.installedLocales` / `supportedLocales`。
3. 选择一个文档化的预设：
   - `.transcription` 用于基本准确转录。
   - `.progressiveTranscription` 用于实时 UI 更新。
   - `.timeIndexedProgressiveTranscription` 当播放高亮需要 `audioTimeRange` 时。
4. 使用 `AssetInventory.assetInstallationRequest` 安装所需资源。
5. 在提供 `AnalyzerInput` 之前，将实时音频缓冲区转换为
   `SpeechAnalyzer.bestAvailableAudioFormat(compatibleWith:)`。
6. 在单独的任务中从其 `AsyncSequence` 消费模块结果。
7. 使用 `finalizeAndFinish(through:)`、
   `finalizeAndFinishThroughEndOfInput()` 或 `cancelAndFinishNow()` 明确结束。

不要使用 `offlineTranscription` 预设；Apple 没有文档说明一个。
完成 `AsyncStream` 输入序列不会结束分析器会话。

## SFSpeechRecognizer 设置

### 使用区域创建识别器

```swift
import Speech

// 默认区域（用户当前语言）
let recognizer = SFSpeechRecognizer()

// 特定区域
let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))

// 检查此区域是否可用
guard let recognizer, recognizer.isAvailable else {
    print("语音识别不可用")
    return
}
```

### 监控可用性变化

```swift
final class SpeechManager: NSObject, SFSpeechRecognizerDelegate {
    private let recognizer = SFSpeechRecognizer()!

    override init() {
        super.init()
        recognizer.delegate = self
    }

    func speechRecognizer(
        _ speechRecognizer: SFSpeechRecognizer,
        availabilityDidChange available: Bool
    ) {
        // 更新 UI — 不可用时禁用录制按钮
    }
}
```

## 授权

在开始实时转录之前，请求**两者**的语音识别和麦克风权限。将这些键添加到 `Info.plist`：

- `NSSpeechRecognitionUsageDescription`
- `NSMicrophoneUsageDescription`

```swift
import Speech
import AVFoundation

func requestPermissions() async -> Bool {
    let speechStatus = await withCheckedContinuation { continuation in
        SFSpeechRecognizer.requestAuthorization { status in
            continuation.resume(returning: status)
        }
    }
    guard speechStatus == .authorized else { return false }

    let micStatus: Bool
    if #available(iOS 17, *) {
        micStatus = await AVAudioApplication.requestRecordPermission()
    } else {
        micStatus = await withCheckedContinuation { continuation in
            AVAudioSession.sharedInstance().requestRecordPermission { granted in
                continuation.resume(returning: granted)
            }
        }
    }
    return micStatus
}
```

## 实时麦克风转录

标准模式：`AVAudioEngine` 捕获麦克风音频 → 缓冲区附加到 `SFSpeechAudioBufferRecognitionRequest` → 结果流式传输。

```swift
import Speech
import AVFoundation

final class LiveTranscriber {
    private let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))!
    private let audioEngine = AVAudioEngine()
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?

    func startTranscribing() throws {
        // 取消任何正在进行的任务
        recognitionTask?.cancel()
        recognitionTask = nil

        // 配置音频会话
        let audioSession = AVAudioSession.sharedInstance()
        try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
        try audioSession.setActive(true, options: .notifyOthersOnDeactivation)

        // 创建请求
        let request = SFSpeechAudioBufferRecognitionRequest()
        request.shouldReportPartialResults = true
        self.recognitionRequest = request

        // 开始识别任务
        recognitionTask = recognizer.recognitionTask(with: request) { result, error in
            if let result {
                let text = result.bestTranscription.formattedString
                print("转录：\(text)")

                if result.isFinal {
                    self.stopTranscribing()
                }
            }
            if let error {
                print("识别错误：\(error)")
                self.stopTranscribing()
            }
        }

        // 安装音频捕获
        let inputNode = audioEngine.inputNode
        let recordingFormat = inputNode.outputFormat(forBus: 0)
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) {
            buffer, _ in
            request.append(buffer)
        }

        audioEngine.prepare()
        try audioEngine.start()
    }

    func stopTranscribing() {
        audioEngine.stop()
        audioEngine.inputNode.removeTap(onBus: 0)
        recognitionRequest?.endAudio()
        recognitionRequest = nil
        recognitionTask?.cancel()
        recognitionTask = nil
    }
}
```

## 预录音频文件识别

使用 `SFSpeechURLRecognitionRequest` 用于磁盘上的音频文件：

```swift
func transcribeFile(at url: URL) async throws -> String {
    guard let recognizer = SFSpeechRecognizer(), recognizer.isAvailable else {
        throw SpeechError.unavailable
    }
    let request = SFSpeechURLRecognitionRequest(url: url)
    request.shouldReportPartialResults = false

    return try await withCheckedThrowingContinuation { continuation in
        var didResume = false
        recognizer.recognitionTask(with: request) { result, error in
            guard !didResume else { return }
            if let error {
                didResume = true
                continuation.resume(throwing: error)
            } else if let result, result.isFinal {
                didResume = true
                continuation.resume(
                    returning: result.bestTranscription.formattedString
                )
            }
        }
    }
}
```

## 本地与服务器识别

`SFSpeechRecognizer` 可以在 iOS 13+ 上使用本地识别，支持的区域。如果 `supportsOnDeviceRecognition` 为 false，则识别器需要网络连接。`requiresOnDeviceRecognition` 仅在识别器支持时有效。

```swift
let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))!

// 检查此区域是否支持本地识别
if recognizer.supportsOnDeviceRecognition {
    let request = SFSpeechAudioBufferRecognitionRequest()
    request.requiresOnDeviceRecognition = true  // 强制本地
}
```

`SFSpeechRecognizer` 请求可能不适合长格式捕获。
Apple 文档了大约一分钟的语音识别任务限制和其他服务限制。对于 iOS 26+ 上的长录音，请优先使用 `SpeechAnalyzer`；否则在限制之前分块或重新开始识别，并在任务之间保留转录状态。

## 处理结果

### 部分与最终结果

使用 `shouldReportPartialResults`，在 `SFSpeechRecognitionResult.isFinal` 提交最终结果之前，替换显示的部分转录。这与 `SpeechTranscriber.Result.isFinal` 不同，其易失性属性范围必须被最终结果替换。实时示例和 [references/speechanalyzer-patterns.md](references/speechanalyzer-patterns.md) 包含规范循环。

### 访问备用转录和置信度

```swift
recognizer.recognitionTask(with: request) { result, error in
    guard let result else { return }

    // 最佳转录
    let best = result.bestTranscription

    // 所有备用（按置信度降序排序）
    for transcription in result.transcriptions {
        for segment in transcription.segments {
            print("\(segment.substring): \(segment.confidence)")
        }
    }
}
```

### 添加标点符号（iOS 16+）

```swift
let request = SFSpeechAudioBufferRecognitionRequest()
request.addsPunctuation = true
```

### 上下文字符串

提高对特定领域术语的识别：

```swift
let request = SFSpeechAudioBufferRecognitionRequest()
request.contextualStrings = ["SwiftUI", "Xcode", "CloudKit"]
```

## 常见错误

| 错误 | 修复 |
|---|---|
| 实时音频请求仅语音授权 | 需要语音和麦克风权限。 |
| 识别器可用性只检查一次 | 观察 delegate 可用性变化和模型服务丢失。 |
| 最终/错误/滚动路径执行不同的清理 | 使用一个 `stopTranscribing()` 所有者进行引擎停止、捕获移除、`endAudio` 和任务取消。 |
| 每个区域都强制使用本地模式 | 检查 `supportsOnDeviceRecognition` 并提供备用方案。 |
| 使用一个 `SFSpeechRecognizer` 任务进行长格式捕获 | 在 iOS 26+ 上优先使用 SpeechAnalyzer 或在保留已提交转录的情况下分块。 |
| 完成分析器输入被视为会话完成 | 通过最后一个样本明确完成或取消并完成。 |
| 易失性 SpeechAnalyzer 结果被追加 | 替换易失性范围，直到最终结果提交。 |
| 在第一个任务结束前启动第二个识别任务 | 取消/完成活动任务并在替换前完成清理。 |

加载 [references/speechanalyzer-patterns.md](references/speechanalyzer-patterns.md) 以获取完整的分析器完成和易失性结果代码。

## 审查清单

- [ ] `NSSpeechRecognitionUsageDescription` 在 Info.plist 中
- [ ] `NSMicrophoneUsageDescription` 在 Info.plist 中（如果使用实时音频）
- [ ] 在开始识别前请求授权
- [ ] `SFSpeechRecognizerDelegate` 设置以处理 `availabilityDidChange`
- [ ] 识别结束时停止音频引擎并移除捕获
- [ ] 完成录制时调用 `recognitionRequest.endAudio()`
- [ ] 在启动新任务前取消之前的 `recognitionTask`
- [ ] 检查 `supportsOnDeviceRecognition` 在要求本地模式前
- [ ] 部分结果与最终 (`isFinal`) 结果分开处理
- [ ] 考虑 `SFSpeechRecognizer` 的一分钟/服务限制
- [ ] 对于 iOS 26+：在使用 `SpeechAnalyzer` 前安装 `AssetInventory` 资产
- [ ] 对于 iOS 26+：检查 `SpeechTranscriber.isAvailable` 和区域支持
- [ ] 对于 iOS 26+：实时缓冲区转换为分析器兼容格式
- [ ] 对于 iOS 26+：明确完成或取消分析器会话
- [ ] 对于 iOS 26+：易失性结果被最终结果替换，而不是重复

## 参考资料

- [Speech 框架](https://sosumi.ai/documentation/speech)
- [SpeechAnalyzer](https://sosumi.ai/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://sosumi.ai/documentation/speech/speechtranscriber)
- [SpeechTranscriber.Preset](https://sosumi.ai/documentation/speech/speechtranscriber/preset)
- [DictationTranscriber](https://sosumi.ai/documentation/speech/dictationtranscriber)
- [SpeechDetector](https://sosumi.ai/documentation/speech/speechdetector)
- [SFSpeechRecognizer](https://sosumi.ai/documentation/speech/sfspeechrecognizer)
- [SFSpeechAudioBufferRecognitionRequest](https://sosumi.ai/documentation/speech/sfspeechaudiobufferrecognitionrequest)
- [SFSpeechURLRecognitionRequest](https://sosumi.ai/documentation/speech/sfspeechurlrecognitionrequest)
- [SFSpeechRecognitionResult](https://sosumi.ai/documentation/speech/sfspeechrecognitionresult)
- [SFSpeechRecognitionRequest](https://sosumi.ai/documentation/speech/sfspeechrecognitionrequest)
- [AssetInventory](https://sosumi.ai/documentation/speech/assetinventory)
- [请求使用语音识别权限](https://sosumi.ai/documentation/speech/asking-permission-to-use-speech-recognition)
- [在实时音频中识别语音](https://sosumi.ai/documentation/speech/recognizing-speech-in-live-audio)
- [使用 SpeechAnalyzer 为您的应用带来高级语音到文本功能](https://sosumi.ai/videos/play/wwdc2025/277)
