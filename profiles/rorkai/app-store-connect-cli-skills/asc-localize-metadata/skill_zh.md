# asc localize metadata

使用此技能来提取英语（或任何源语言）App Store元数据，使用LLM进行翻译，并将翻译回传至App Store Connect——全部自动化。

## 命令发现和输出约定

- 始终使用 `--help` 确认标志以获取确切的 `asc` 版本：
  - `asc localizations --help`
  - `asc localizations download --help`
  - `asc localizations upload --help`
  - `asc apps info edit --help`
- 倾向于使用明确的较长标志 (`--app`, `--version`, `--version-id`, `--type`, `--app-info`)。
- 输出默认是TTY感知的：在交互式终端中显示表格，在CI或其他非交互式环境中显示JSON。当格式重要时，使用明确的 `--output`。
- 倾向于使用基于确定ID的操作。除非用户明确同意，否则不要通过 `head -1` "选择第一行"。

## 前置条件
- 配置认证 (`asc auth login` 或 `ASC_*` 环境变量)
- 知道你的应用ID (`asc apps list` 来查找它)
- 至少有一个语言环境（通常为 en-US）已经在App Store Connect中拥有元数据

## 支持的语言环境

App Store Connect版本和app-info本地化语言环境：
```
ar-SA, bn-BD, ca, cs, da, de-DE, el, en-AU, en-CA, en-GB,
en-US, es-ES, es-MX, fi, fr-CA, fr-FR, gu-IN, he, hi, hr,
hu, id, it, ja, kn-IN, ko, ml-IN, mr-IN, ms, nl-NL, no,
or-IN, pa-IN, pl, pt-BR, pt-PT, ro, ru, sk, sl-SI, sv,
ta-IN, te-IN, th, tr, uk, ur-PK, vi, zh-Hans, zh-Hant
```

## 两种类型的元数据

### 版本本地化（每个版本）
字段：`description`, `keywords`, `whatsNew`, `supportUrl`, `marketingUrl`, `promotionalText`

### 应用信息本地化（应用级别，持久）
字段：`name`, `subtitle`, `privacyPolicyUrl`, `privacyChoicesUrl`, `privacyPolicyText`

## 工作流程

### 第1步：解析ID

```bash
# 查找应用ID
asc apps list --output table

# 查找最新版本ID
asc versions list --app "APP_ID" --state READY_FOR_DISTRIBUTION --output table
# 或对于可编辑版本：
asc versions list --app "APP_ID" --state PREPARE_FOR_SUBMISSION --output table

# 查找应用信息ID（用于应用级别的字段，如name/subtitle）
asc apps info list --app "APP_ID" --output table
```

注意：
- 版本本地化字段（description, keywords, whatsNew, 等）是每个版本的。
- 应用信息字段（name, subtitle, 隐私URL/文本）是应用级别的，并使用 `--type app-info`。
- 如果你只有名称（应用名称、版本字符串）并且需要确定性地获取ID，请使用 `asc-id-resolver`。

### 第2步：下载源语言环境

```bash
# 下载版本本地化到本地 .strings 文件
# (description, keywords, whatsNew, promotionalText, supportUrl, marketingUrl, ...)
asc localizations download --version "VERSION_ID" --path "./localizations"

# 下载应用信息本地化到本地 .strings 文件
# (name, subtitle, privacyPolicyUrl, privacyChoicesUrl, privacyPolicyText, ...)
asc localizations download --app "APP_ID" --type app-info --app-info "APP_INFO_ID" --path "./app-info-localizations"
```

这将创建类似 `./localizations/en-US.strings` 和 `./app-info-localizations/en-US.strings` 的文件。如果下载不可用，请逐个读取字段：

```bash
# 列出版本本地化以查看现有语言环境及其内容
asc localizations list --version "VERSION_ID" --output table
```

### 第3步：使用LLM进行翻译

对于每个目标语言环境，翻译源文本。遵循以下规则：

#### 翻译指南
- **语气和语域**：始终使用正式、礼貌的语言。在区分正式和非正式的语种中（如俄语：«вы», 德语：«Sie», 法语：«vous», 西班牙语：«usted», 荷兰语：«u», 意大利语：«Lei», 葡萄牙语：`você` 正式等）。App Store描述是专业的营销文案——永远不要使用非正式或随意的语域。
- **description**：自然翻译，根据当地市场调整语气。保留格式（换行、项目符号、表情符号）。保持在4000个字符以内。
- **keywords**：不要逐字翻译。研究该语言环境中的用户会搜索什么。逗号分隔，总计最多100个字符。不要重复，不要包含应用名称（Apple会自动添加）。
- **whatsNew**：翻译发布说明。保持简洁。最多4000个字符。
- **promotionalText**：翻译营销钩子。最多170个字符。这可以在没有新版本的情况下更新。
- **subtitle**：翻译或调整标语。最多30个字符——这非常紧凑，可能需要创意改编。
- **name**：通常保留原始应用名称。只有在用户明确要求时才翻译。最多30个字符。

#### LLM翻译提示模板

对于每个目标语言环境，使用此方法：

```
将以下App Store元数据从 {source_locale} 翻译到 {target_locale}。

规则：
- description：自然、流畅的翻译。保留格式（换行、项目符号、表情符号）。最多4000个字符。
- keywords：不要逐字翻译。选择该语言环境中用户会在App Store中搜索的词汇。逗号分隔，总计最多100个字符。不要包含应用名称。
- whatsNew：自然翻译发布说明。最多4000个字符。
- promotionalText：翻译营销标语。最多170个字符。
- subtitle：创意地调整标语以适应最多30个字符。
- name：除非明确要求翻译，否则保留原始应用名称。最多30个字符。
- 使用正式、礼貌的语言和正式的“你”形式（俄语：вы，德语：Sie，法语：vous，西班牙语：usted，荷兰语：u，等）。App Store文案是专业的营销——永远不要使用非正式语域。
- 尊重文化背景。英语中的俏皮语气可能需要调整以适应正式市场（例如，ja, de-DE）。

源 ({source_locale}):
description: """
{description}
"""

keywords: {keywords}

whatsNew: """
{whatsNew}
"""

promotionalText: {promotionalText}

name: {name}

subtitle: {subtitle}
```

### 第4步：上传翻译

#### 选项A：通过 .strings 文件（批量）

在每个适当的目录中为每个语言环境创建一个 `.strings` 文件。

版本本地化示例：

```
// nl-NL.strings
"description" = "Mijn app-beschrijving hier";
"keywords" = "wiskunde,kinderen,tafels,leren";
"whatsNew" = "Bugfixes en verbeteringen";
"promotionalText" = "Leer de tafels van vermenigvuldiging!";
```

然后上传版本本地化：
```bash
asc localizations upload --version "VERSION_ID" --path "./localizations"
```

应用信息本地化示例：

```
// nl-NL.strings
"subtitle" = "Leer tafels spelenderwijs";
```

然后上传应用信息本地化：
```bash
asc localizations upload --app "APP_ID" --type app-info --app-info "APP_INFO_ID" --path "./app-info-localizations"
```

#### 选项B：通过单独命令（精细控制）

```bash
# 版本本地化字段（精细控制）。
# 倾向于传递明确的版本ID以确保确定性。
asc apps info edit --app "APP_ID" --version-id "VERSION_ID" --locale "nl-NL" \
  --description "Mijn beschrijving..." \
  --keywords "wiskunde,kinderen,tafels" \
  --whats-new "Bugfixes en verbeteringen"
```

对于应用级别字段：
```bash
# Subtitle/name（应用信息本地化）通过应用信息本地化管理。
# 使用应用信息本地化 .strings + 上传流程；没有应用信息本地化命令。
#
# 1) 编辑：./app-info-localizations/nl-NL.strings
# "subtitle" = "Leer tafels spelenderwijs";
#
# 2) 上传：
asc localizations upload --app "APP_ID" --type app-info --app-info "APP_INFO_ID" --path "./app-info-localizations"
```

### 第5步：验证

```bash
# 检查所有语言环境是否存在
asc localizations list --version "VERSION_ID" --output table

# 检查应用信息本地化
asc localizations list --app "APP_ID" --type app-info --app-info "APP_INFO_ID" --output table
```

## 字符限制（上传前必须执行！）

| 字段 | 限制 |
|-------|-------|
| Name | 30 |
| Subtitle | 30 |
| Keywords | 100（逗号分隔） |
| Description | 4000 |
| What's New | 4000 |
| Promotional Text | 170 |

**始终验证**翻译文本是否在限制范围内。截断的文本看起来不专业。如果翻译超过限制，请缩短它——不要在句子中间截断。

## 完整示例：为Roxy Math添加 nl-NL 和 ru

```bash
# 1) 确定性地解析ID（不要自动选择“第一行”）
# 如果你只有名称，请使用 asc-id-resolver 技能。
asc apps list --output table
APP_ID="APP_ID_HERE"

asc versions list --app "$APP_ID" --state PREPARE_FOR_SUBMISSION --output table
VERSION_ID="VERSION_ID_HERE"

asc apps info list --app "$APP_ID" --output table
APP_INFO_ID="APP_INFO_ID_HERE"

# 2) 下载英语源（或你选择的其他源语言环境）
asc localizations download --version "$VERSION_ID" --path "./localizations"
asc localizations download --app "$APP_ID" --type app-info --app-info "$APP_INFO_ID" --path "./app-info-localizations"

# 3) 读取 en-US.strings，翻译到 nl-NL 和 ru（LLM步骤）

# 4) 将 nl-NL.strings 和 ru.strings 写入：
#    - ./localizations/（版本本地化字段）
#    - ./app-info-localizations/（subtitle/name/隐私字段）

# 5) 上传所有
asc localizations upload --version "$VERSION_ID" --path "./localizations"
asc localizations upload --app "$APP_ID" --type app-info --app-info "$APP_INFO_ID" --path "./app-info-localizations"

# 6) 验证
asc localizations list --version "$VERSION_ID" --output table
asc localizations list --app "$APP_ID" --type app-info --app-info "$APP_INFO_ID" --output table
```

## 代理行为

1. **始终从读取源语言环境开始**——不要从记忆或假设中翻译。
2. **首先检查现有本地化**——除非用户要求更新它们，否则不要覆盖现有翻译。
3. **版本与应用信息不同**——版本字段位于 `--version "VERSION_ID"` 下；subtitle/name/隐私位于 `--app ... --type app-info` 下。
4. **倾向于使用确定性的ID**——除非明确要求，否则不要通过 `head -1` 选择ID；使用 `--output table` 进行选择或 `asc-id-resolver`。
5. **上传前验证字符限制**。计算每个字段的字符数。如果超出限制，请重新翻译更短的文本。
6. **Keywords是特殊的**——不要逐字翻译。研究该语言环境中用户会在App Store中搜索的词汇。像在该语言环境中搜索App Store的用户一样思考。
7. **在上传前向用户展示翻译**——显示所有字段 × 语言环境的汇总表以供批准。未经确认不要推送。
8. **如果翻译许多语言，一次处理一个语言环境**——更容易审查和发现错误。
9. **如果某个语言环境的上传失败**，记录错误，继续其他语言环境，在最后报告所有失败。
10. **对于现有本地化的更新**——下载当前版本，显示将要更改的差异，获得批准，然后上传。

## 注意事项
- 版本本地化与特定版本绑定。如果不存在，请先创建版本。
- `promotionalText` 可以随时更新，无需提交新版本。
- `whatsNew` 仅适用于更新，不适用于第一个版本。
- 如果只有应用/版本名称而没有ID，请使用 `asc-id-resolver` 技能。
- 使用 `asc-metadata-sync` 技能进行非翻译元数据操作。
- 对于订阅/IAP显示名称本地化，请使用 `asc-subscription-localization` 技能。
