# 博客翻译，SEO优化博客翻译

将现有的博客文章翻译成一种或多种目标语言。与通用翻译不同，这项技能生成SEO优化的、可直接发布的本地化内容，包含本地化关键词、元标签和符合文化习惯的格式。

> 改编自 `claude-blog-multilingual` by Chris Mueller (Pro Hub Challenge, 2026年3月)。原始链接：https://github.com/Chriss54/multilingual-int

## 关键参考资料

按需加载：

- `references/translation-rules.md`，格式保留，各地区的数字/日期/货币格式，引号处理，质量标准。
- `references/cultural-adaptation.md`，各地区的文化特征（DACH、法语区、西班牙语区、日语、自定义）。此文件与 `blog-localize` 共享（不要重复）。

## 工作流程

### 第一阶段：输入解析

1. 仅在解决与项目根目录/当前工作目录冲突后读取源文件（markdown、MDX或HTML）。拒绝符号链接路径、根目录外的遍历、超过10 MB的文件和二进制文件。
2. 自动检测源语言。优先顺序：
   - 前置字段 `lang` 字段。
   - HTML `lang` 属性。
   - 内容分析（脚本、常用停用词）。
3. 从 `--to` 解析目标语言，作为逗号分隔的Google兼容的hreflang标签（`de`、`fr`、`es-MX`、`ja`、`pt-BR`、`zh-Hant`）。如果 `--to` 缺失，则询问用户一次：“我应该翻译成哪些语言？提供hreflang标签，如de、fr、es-MX、ja、pt-BR。”
4. 使用 `blog-multilingual`、`blog-localize` 和 `blog-locale-audit` 使用的共享多语言本地化规则规范化每个代码：ISO 639-1 小写语言代码，可选ISO 15924 脚本的大写形式，可选ISO 3166-1 Alpha-2 地区的大写形式。拒绝无效代码并建议（`jp` 变为“您是否想用 `ja` 表示日语？”）。对于 `es`、`pt` 和 `zh` 等模糊的语言仅目标，需要地区或明确的中性模式。如果目标等于规范化后的源语言，则跳过并通知。

### 第二阶段：内容分析

提取可翻译的表面：

- 前置字段：`title`、`description`、`tags`、`author`（仅当可翻译时，例如角色标签，而不是个人姓名）。
- 所有标题（H1、H2、H3）。
- 正文段落。
- 图片 `alt` 文本和 `<figcaption>` 内容。
- 图表 `<text>` 和 `<tspan>` 内容；保留每个SVG属性（`x`、`y`、`font-size`、`fill`、`transform`）。
- FAQ问题和答案。
- 有证据支持的说明文本。
- 关键要点或摘要框。
- CTA文本。
- 内部链接区域锚文本。

保留不变：

- Markdown和HTML结构、标签、属性。
- 图片URL、链接URL、前置字段键。
- 可执行代码围栏和内联代码。仅翻译可执行代码外的注释，或当用户明确要求本地化教程注释时。
- 内部链接区域标记（`[INTERNAL-LINK: ...]`）。
- 引证中的源组织名称（Gartner、McKinsey等）。
- 人名。
- Schema JSON-LD块（仅翻译面向用户的内容字符串；永远不翻译Person、Organization或Brand名称、URL、ID、`@id` 或 `sameAs`）。

识别第三阶段的主要和次要关键词。

### 第三阶段：关键词本地化

对于每种目标语言：

1. 判断源关键词是否是目标市场的常用术语。如果是（例如，“内容营销”在德语中保持不变），则保留。
2. 如果本地等效词有实际搜索行为，则切换到它。
3. 对次要关键词应用相同逻辑。
4. 记录映射。翻译代理使用它来更新标题、元描述和H2标题。

### 第四阶段：翻译

为每种目标语言生成 `blog-translator` 代理（通过任务）：

- 源内容。
- 第三阶段的本地化关键词映射。
- 目标语言代码。
- 指向 `references/translation-rules.md` 的指针。
- 指示此阶段仅限于语言、注册、自然主题覆盖和格式。保留品牌、法律、统计和文化替换给 `blog-localize`。

当翻译成多种语言时并行运行代理。

代理以与输入相同的格式返回完全翻译的帖子。

### 第五阶段：后处理

对于每个翻译版本：

1. 添加或更新地区前置字段：
   ```yaml
   lang: "de"
   translatedFrom: "en"
   translatedDate: "YYYY-MM-DD"
   slug: "wie-man-ki-slop-vermeidet"
   ```
2. 验证结构完整性：
   - 与原始文件相同的H2和H3部分数量。
   - 所有图片都存在并带有翻译的alt文本。
   - 所有SVG图表都存在并带有翻译的文本标签（长度调整：DE +30%，FR +15%，JA -20%，其他参见 `references/translation-rules.md`）。
   - FAQ数量匹配。
   - 源中有证据支持的说明文本保持完整。
3. 保存翻译文件：
   ```
   translations/
     {lang}/{localized-slug}.{ext}
   ```
   当从 `blog-multilingual` 调用时，保存到
   `multilingual/{lang}/{localized-slug}.{ext}`。在写入之前，将 `{localized-slug}` 转换为小写ASCII，仅包含 `a-z`、`0-9` 和连字符，拒绝空或保留名称。仅从规范化后的hreflang代码创建语言目录。解析最终路径并要求其保持在预期的输出根目录内；拒绝符号链接输出路径。

### 第六阶段：翻译质量护栏

在报告完成前扫描输出，查找机器翻译痕迹：

- 直译习语（英语习语音译，未适应）。
- 不自然的词序（SOV翻译为SVO到非SOV语言，反之亦然）。
- 混合语言句子（除已建立的借词外）。
- 数字、日期或货币字符串仍为源格式。
- 前置字段字符串仍为源语言。

逐行标记每个问题（文件路径、行号、修复建议）。翻译代理应在交付前重新传递任何标记的段落。

### 第七阶段：交付

```
## 翻译完成：[原始标题]

### 源
- 语言：[源]
- 文件：[源路径]

### 翻译
| 语言 | 文件 | 关键词调整 | 状态 |
|------|------|------------|------|
| de | translations/de/{slug}.md | [N] | ok |
| fr | translations/fr/{slug}.md | [N] | ok |

### 质量检查
- 结构完整性：每种语言通过/失败
- 元标签本地化：每种语言通过/失败
- 数字、日期、货币按地区格式化：通过/失败
- 关键词本地化：[N] 关键词调整
- 机器翻译痕迹标记：[N]（见上述注释）

### 下一步
- 运行 `/blog localize <文件> --locale <代码>` 进行文化深度适应。
- 运行 `/blog locale-audit translations/` 验证完整性。
- 使用 `/blog multilingual` 在一个命令中组合写入、翻译、本地化和hreflang。
```

## 错误处理

| 场景 | 操作 |
|------|------|
| 不支持的语言代码 | 建议正确的Google兼容hreflang代码 |
| 源等于目标 | 跳过并显示“源已经是 [lang]” |
| 文件未找到 | 报告错误并建议路径 |
| 翻译代理超时 | 重试一次，然后报告部分结果 |
| 二进制或非文本文件 | 报告错误，建议正确文件 |

## 交叉引用

- 下一步（文化深度）：`/blog localize <文件> --locale <代码>`
- 跨所有语言版本进行QA检查：`/blog locale-audit <目录>`
- 一键管道：`/blog multilingual <主题> --languages <代码>`
