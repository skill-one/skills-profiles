# 自然语言 + 翻译

分析自然语言文本进行分词、词性标注、命名实体识别、情感分析、语言识别和词/句嵌入。使用翻译框架在不同语言之间翻译文本。

> 此技能涵盖两个相关的框架：**自然语言** (`NLTokenizer`, `NLTagger`, `NLEmbedding`) 用于设备上的文本分析，以及 **翻译** (`TranslationSession`, `LanguageAvailability`) 用于语言翻译。

**范围边界**：在您已经拥有文本之后使用此技能。它拥有分词、语言识别、POS/NER 标注、情感、嵌入、自定义 `NLModel` 分类器/标注器以及应用内翻译。将 OCR 交给 `vision-framework`，语音识别交给 `speech-recognition`，UI 字符串和区域设置格式化交给 `ios-localization`，并将生成式摘要或 Apple Intelligence 工作流交给 `apple-on-device-ai`。

## 内容

- [设置](#设置)
- [分词](#分词)
- [语言识别](#语言识别)
- [词性标注](#词性标注)
- [命名实体识别](#命名实体识别)
- [情感分析](#情感分析)
- [文本嵌入](#文本嵌入)
- [翻译](#翻译)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 设置

导入 `NaturalLanguage` 进行文本分析，导入 `Translation` 进行语言翻译。NaturalLanguage 无需特殊权限或功能。翻译的可用性是分开的：系统翻译呈现为 iOS 17.4+/macOS 14.4+，而 `TranslationSession`、`.translationTask()`、`LanguageAvailability` 和批量翻译需要 iOS 18+/macOS 15+。直接 `TranslationSession(installedSource:target:)` 是非 UI 选项，但仅当源语言和目标语言已安装在设备上时才可用。

```swift
import NaturalLanguage
import Translation
```

NaturalLanguage 类 (`NLTokenizer`, `NLTagger`) 不是 **线程安全的**。每次从单个线程或分发队列使用每个实例。

## 分词

使用 `NLTokenizer` 将文本分割成单词、句子或段落。

```swift
import NaturalLanguage

func tokenizeWords(in text: String) -> [String] {
    let tokenizer = NLTokenizer(unit: .word)
    tokenizer.string = text

    let range = text.startIndex..<text.endIndex
    return tokenizer.tokens(for: range).map { String(text[$0]) }
}
```

### 分词单位

| 单位 | 描述 |
|---|---|
| `.word` | 单个单词 |
| `.sentence` | 句子 |
| `.paragraph` | 段落 |
| `.document` | 整个文档 |

### 带属性枚举

使用 `enumerateTokens(in:using:)` 检测数字或表情符号标记。

```swift
let tokenizer = NLTokenizer(unit: .word)
tokenizer.string = text

tokenizer.enumerateTokens(in: text.startIndex..<text.endIndex) { range, attributes in
    if attributes.contains(.numeric) {
        print("数字: \(text[range])")
    }
    return true // 继续枚举
}
```

## 语言识别

使用 `NLLanguageRecognizer` 检测字符串的主要语言。

```swift
func detectLanguage(for text: String) -> NLLanguage? {
    NLLanguageRecognizer.dominantLanguage(for: text)
}

// 多个假设和置信度分数
func languageHypotheses(for text: String, max: Int = 5) -> [NLLanguage: Double] {
    let recognizer = NLLanguageRecognizer()
    recognizer.processString(text)
    return recognizer.languageHypotheses(withMaximum: max)
}
```

将识别器约束为预期的语言，以在短文本上获得更好的准确性。

```swift
let recognizer = NLLanguageRecognizer()
recognizer.languageConstraints = [.english, .french, .spanish]
recognizer.processString(text)
let detected = recognizer.dominantLanguage
```

## 词性标注

使用 `NLTagger` 识别名词、动词、形容词和其他词汇类别。

```swift
func tagPartsOfSpeech(in text: String) -> [(String, NLTag)] {
    let tagger = NLTagger(tagSchemes: [.lexicalClass])
    tagger.string = text

    var results: [(String, NLTag)] = []
    let range = text.startIndex..<text.endIndex
    let options: NLTagger.Options = [.omitPunctuation, .omitWhitespace]

    tagger.enumerateTags(in: range, unit: .word, scheme: .lexicalClass, options: options) { tag, tokenRange in
        if let tag {
            results.append((String(text[tokenRange]), tag))
        }
        return true
    }
    return results
}
```

### 常见标注方案

| 方案 | 输出 |
|---|---|
| `.lexicalClass` | 词性（名词、动词、形容词） |
| `.nameType` | 命名实体类型（人名、地点、组织） |
| `.nameTypeOrLexicalClass` | 结合 NER + POS |
| `.lemma` | 单词的基本形式 |
| `.language` | 每个标记的语言 |
| `.sentimentScore` | 情感极性分数 |

## 命名实体识别

提取人名、地名和组织。

```swift
func extractEntities(from text: String) -> [(String, NLTag)] {
    let tagger = NLTagger(tagSchemes: [.nameType])
    tagger.string = text

    var entities: [(String, NLTag)] = []
    let options: NLTagger.Options = [.omitPunctuation, .omitWhitespace, .joinNames]

    tagger.enumerateTags(
        in: text.startIndex..<text.endIndex,
        unit: .word,
        scheme: .nameType,
        options: options
    ) { tag, tokenRange in
        if let tag, tag != .other {
            entities.append((String(text[tokenRange]), tag))
        }
        return true
    }
    return entities
}
// NLTag 值：.personalName, .placeName, .organizationName
```

## 情感分析

从 -1.0（负面）到 +1.0（正面）对文本情感进行评分。

```swift
func sentimentScore(for text: String) -> Double? {
    let tagger = NLTagger(tagSchemes: [.sentimentScore])
    tagger.string = text

    let (tag, _) = tagger.tag(
        at: text.startIndex,
        unit: .paragraph,
        scheme: .sentimentScore
    )
    return tag.flatMap { Double($0.rawValue) }
}
```

## 文本嵌入

使用 `NLEmbedding` 测量单词或句子之间的语义相似度。

```swift
func wordSimilarity(_ word1: String, _ word2: String) -> Double? {
    guard let embedding = NLEmbedding.wordEmbedding(for: .english) else { return nil }
    return embedding.distance(between: word1, and: word2, distanceType: .cosine)
}

func findSimilarWords(to word: String, count: Int = 5) -> [(String, Double)] {
    guard let embedding = NLEmbedding.wordEmbedding(for: .english) else { return [] }
    return embedding.neighbors(for: word, maximumCount: count, distanceType: .cosine)
}
```

句子嵌入比较整个句子。

```swift
func sentenceSimilarity(_ s1: String, _ s2: String) -> Double? {
    guard let embedding = NLEmbedding.sentenceEmbedding(for: .english) else { return nil }
    return embedding.distance(between: s1, and: s2, distanceType: .cosine)
}
```

## 翻译

### 系统翻译覆盖

使用 `.translationPresentation()` 显示内置翻译 UI。

```swift
import SwiftUI
import Translation

struct TranslatableView: View {
    @State private var showTranslation = false
    let text = "你好，你好吗？"

    var body: some View {
        Button { showTranslation = true } label: {
            Text(text)
        }
        .buttonStyle(.plain)
        .translationPresentation(
            isPresented: $showTranslation,
            text: text
        )
    }
}
```

### 代码翻译

在视图上下文中使用 `.translationTask()` 进行程序化翻译。

```swift
struct TranslatingView: View {
    @State private var translatedText = ""
    @State private var translationErrorMessage: String?
    @State private var configuration: TranslationSession.Configuration?

    var body: some View {
        VStack {
            Text(translatedText)
            Button("翻译") {
                configuration = .init(source: Locale.Language(identifier: "en"),
                                      target: Locale.Language(identifier: "es"))
            }
        }
        .translationTask(configuration) { session in
            do {
                let response = try await session.translate("你好，世界！")
                await MainActor.run {
                    translatedText = response.targetText
                    translationErrorMessage = nil
                }
            } catch {
                let message = error.localizedDescription
                await MainActor.run {
                    translationErrorMessage = message
                }
            }
        }
    }
}
```

### 批量翻译

在单个会话中翻译多个字符串。

```swift
.translationTask(configuration) { session in
    do {
        let requests = texts.enumerated().map { index, text in
            TranslationSession.Request(sourceText: text,
                                       clientIdentifier: "\(index)")
        }
        let responses = try await session.translations(from: requests)
        for response in responses {
            print("\(response.sourceText) -> \(response.targetText)")
        }
    } catch {
        // 处理取消、不支持的语言或下载拒绝。
    }
}
```

### 检查语言可用性

```swift
let availability = LanguageAvailability()
let status = await availability.status(
    from: Locale.Language(identifier: "en"),
    to: Locale.Language(identifier: "ja")
)
switch status {
case .installed: break    // 离线翻译准备就绪
case .supported: break    // 需要下载
case .unsupported: break  // 语言对不可用
}
```

## 常见错误

### 不要：跨线程共享 NLTagger/NLTokenizer

这些类不是线程安全的，会产生错误结果或崩溃。

```swift
// 错误
let sharedTagger = NLTagger(tagSchemes: [.lexicalClass])
DispatchQueue.concurrentPerform(iterations: 10) { _ in
    sharedTagger.string = someText  // 数据竞争
}

// 正确
await withTaskGroup(of: Void.self) { group in
    for _ in 0..<10 {
        group.addTask {
            let tagger = NLTagger(tagSchemes: [.lexicalClass])
            tagger.string = someText
            // 处理...
        }
    }
}
```

### 不要：混淆自然语言与 Core ML

自然语言提供内置的语言分析。使用 Core ML 进行自定义训练模型。它们通过 `NLModel` 相互补充。

```swift
// 错误：尝试使用原始 Core ML 进行 NER
let coreMLModel = try MLModel(contentsOf: modelURL)

// 正确：使用 NLTagger 进行内置 NER
let tagger = NLTagger(tagSchemes: [.nameType])

// 或者通过 NLModel 加载自定义 Core ML 模型
let nlModel = try NLModel(mlModel: coreMLModel)
tagger.setModels([nlModel], forTagScheme: .nameType)
```

### 不要：假设所有语言都有嵌入

并非所有语言在设备上都有单词或句子嵌入可用。

```swift
// 错误：强制解包
let embedding = NLEmbedding.wordEmbedding(for: .japanese)!

// 正确：处理 nil
guard let embedding = NLEmbedding.wordEmbedding(for: .japanese) else {
    // 此语言没有嵌入
    return
}
```

### 不要：每个标记创建一个新的标注器

创建和配置标注器很昂贵。对同一文本重用它。

```swift
// 错误：每个单词新标注器
for word in words {
    let tagger = NLTagger(tagSchemes: [.lexicalClass])
    tagger.string = word
}

// 正确：设置字符串一次，枚举
let tagger = NLTagger(tagSchemes: [.lexicalClass])
tagger.string = fullText
tagger.enumerateTags(in: fullText.startIndex..<fullText.endIndex,
                     unit: .word, scheme: .lexicalClass, options: []) { tag, range in
    return true
}
```

### 不要：忽略短文本的语言提示

短字符串（少于 ~20 个字符）上的语言检测不可靠。设置约束或提示以提高准确性。

```swift
// 错误：检测单个单词的语言
let lang = NLLanguageRecognizer.dominantLanguage(for: "chat")  // 法语或英语？

// 正确：提供上下文
let recognizer = NLLanguageRecognizer()
recognizer.languageHints = [.english: 0.8, .french: 0.2]
recognizer.processString("chat")
```

## 审查清单

- [ ] `NLTokenizer` 和 `NLTagger` 实例从单个线程使用
- [ ] 标注器为每个文本创建一次，而不是每个标记
- [ ] 语言检测对短文本使用约束/提示
- [ ] 在使用前检查 `NLEmbedding` 可用性（如果不可用则返回 nil）
- [ ] 在尝试翻译前检查翻译 `LanguageAvailability`
- [ ] `.translationTask()` 在 SwiftUI 视图层次结构中使用
- [ ] 批量翻译使用 `clientIdentifier` 将响应与请求匹配
- [ ] 情感分数作为可选处理（可能因不支持的语种返回 nil）
- [ ] 使用 `.joinNames` 选项与 NER 一起保持多词名称的完整性
- [ ] 通过 `NLModel` 加载自定义 ML 模型，而不是原始 Core ML

## 参考资料

- 扩展模式（自定义模型、上下文嵌入、 gazetteers）：[参考资料/翻译模式.md](references/translation-patterns.md)
- [自然语言框架](https://sosumi.ai/documentation/naturallanguage)
- [NLTokenizer](https://sosumi.ai/documentation/naturallanguage/nltokenizer)
- [NLTagger](https://sosumi.ai/documentation/naturallanguage/nltagger)
- [NLEmbedding](https://sosumi.ai/documentation/naturallanguage/nlembedding)
- [NLLanguageRecognizer](https://sosumi.ai/documentation/naturallanguage/nllanguagerecognizer)
- [翻译框架](https://sosumi.ai/documentation/translation)
- [TranslationSession](https://sosumi.ai/documentation/translation/translationsession)
- [TranslationSession.Strategy](https://sosumi.ai/documentation/translation/translationsession/strategy)
- [LanguageAvailability](https://sosumi.ai/documentation/translation/languageavailability)
