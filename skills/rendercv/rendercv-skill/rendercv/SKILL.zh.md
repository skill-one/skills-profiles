---
name: rendercv
description: 使用 RenderCV (v2.8) 创建具有完美排版的专业简历和履历。用户以 YAML 格式编写内容，RenderCV 通过 Typst 排版技术生成出版级 PDF 文件。对每个视觉细节进行全面控制：颜色、字体、页边距、间距、章节标题样式、条目布局等。内置 6 款主题，支持无限定制。支持任何语言（内置 22 种，或自定义）。输出格式包括 PDF、PNG、HTML 和 Markdown。适用于用户创建、编辑、定制或渲染简历或履历的场景。
---

## 快速入门

**可用的主题：** `classic`、`harvard`、`engineeringresumes`、`engineeringclassic`、`sb2nov`、`moderncv`
**可用的区域设置：** `english`、`arabic`、`danish`、`dutch`、`french`、`german`、`hebrew`、`hindi`、`hungarian`、`indonesian`、`italian`、`japanese`、`korean`、`mandarin_chinese`、`norwegian_bokmål`、`norwegian_nynorsk`、`persian`、`portuguese`、`russian`、`spanish`、`turkish`、`vietnamese`

这些都是起点——设计和区域设置的所有方面都可以在 YAML 文件中完全自定义。

```bash
# 安装 RenderCV
uv tool install "rendercv[full]"

# 创建一个起始 YAML 文件（可以指定主题和区域设置）
rendercv new "John Doe"
rendercv new "John Doe" --theme moderncv --locale german

# 渲染为 PDF（默认情况下还会生成 Typst、Markdown、HTML、PNG）
rendercv render John_Doe_CV.yaml

# 监视模式：每当 YAML 文件更改时自动重新渲染
rendercv render John_Doe_CV.yaml --watch

# 仅渲染 PNG（用于预览或检查页数）
rendercv render John_Doe_CV.yaml --dont-generate-pdf --dont-generate-html --dont-generate-markdown

# 从 CLI 覆盖字段，而无需编辑 YAML
rendercv render cv.yaml --cv.name "Jane Doe" --design.theme "moderncv"
```

## YAML 结构

RenderCV 输入有四个部分。只有 `cv` 是必需的——其他的都有合理的默认值。

```yaml
cv:         # 您的内容：姓名、联系信息以及所有部分
design:     # 视觉样式：主题、颜色、字体、边距、间距、布局
locale:     # 语言：月份名称、短语、翻译
settings:   # 行为：输出路径、加粗关键词、当前日期
```

**单个文件与分离文件：** 所有四个部分可以位于一个 YAML 文件中，或者每个部分可以是一个单独的文件。分离文件对于在多个简历中重用相同的设计/区域设置很有用：

```bash
# 单个自包含文件（所有部分在一个文件中）
rendercv render John_Doe_CV.yaml

# 分离文件：简历内容 + 设计 + 区域设置独立加载
rendercv render cv.yaml --design design.yaml --locale-catalog locale.yaml --settings settings.yaml
```

在使用分离文件时，每个文件只包含其部分（例如，`design.yaml` 以 `design:` 作为顶级键）。CLI 加载的文件会覆盖主 YAML 文件中的值。

YAML 直接映射到 Pydantic 模型。完整的类型安全模式如下所示，以便您了解每个字段、其类型及其默认值。

## Pydantic 模式

YAML 输入将根据这些 Pydantic 模型进行验证。

### 顶级模型

```python
class RenderCVModel(BaseModelWithoutExtraKeys):
    cv: Cv = pydantic.Field(default_factory=Cv, title='CV', description='简历的内容。')
    design: Design = pydantic.Field(default_factory=ClassicTheme, title='设计')
    locale: Locale = pydantic.Field(default_factory=EnglishLocale, title='区域设置目录')
    settings: Settings = pydantic.Field(default_factory=Settings, title='RenderCV 设置', description='RenderCV 的设置。')

```

### 简历内容 (`cv`)

`cv.sections` 字段是一个字典，其中键是部分标题（您想要的任何字符串），值是条目的列表。每个部分包含相同类型的条目。

```python
class Cv(BaseModelWithoutExtraKeys):
    name: str | None = pydantic.Field(default=None, examples=['John Doe', 'Jane Smith'])
    headline: str | None = pydantic.Field(default=None, examples=['软件工程师', '数据科学家', '产品经理'])
    location: str | None = pydantic.Field(default=None, examples=['纽约, NY', '伦敦, UK', '伊斯坦布尔, 土耳其'])
    email: pydantic.EmailStr | list[pydantic.EmailStr] | None = pydantic.Field(default=None, examples=['john.doe@example.com', ['john.doe.1@example.com', 'john.doe.2@example.com']])
    photo: ExistingPathRelativeToInput | pydantic.HttpUrl | None = pydantic.Field(default=None, union_mode='left_to_right', examples=['photo.jpg', 'images/profile.png', 'https://example.com/photo.jpg'])
    phone: pydantic_phone_numbers.PhoneNumber | list[pydantic_phone_numbers.PhoneNumber] | None = pydantic.Field(default=None, examples=['+1-234-567-8900', ['+1-234-567-8900', '+44 20 1234 5678']])
    website: pydantic.HttpUrl | list[pydantic.HttpUrl] | None = pydantic.Field(default=None, examples=['https://johndoe.com', ['https://johndoe.com', 'https://www.janesmith.dev']])
    social_networks: list[SocialNetwork] | None = pydantic.Field(default=None)
    custom_connections: list[CustomConnection] | None = pydantic.Field(default=None, examples=[[{'placeholder': '预约通话', 'url': 'https://cal.com/johndoe', 'fontawesome_icon': 'calendar-days'}]])
    sections: dict[str, Section] | None = pydantic.Field(default=None, examples=[{'经验': '...', '教育': '...', '项目': '...', '技能': '...'}])

```

```python
type SocialNetworkName = Literal['LinkedIn', 'GitHub', 'GitLab', 'IMDB', 'Instagram', 'ORCID', 'Mastodon', 'StackOverflow', 'ResearchGate', 'YouTube', 'Google Scholar', 'Telegram', 'WhatsApp', 'Leetcode', 'X', 'Bluesky', 'Reddit']

available_social_networks = get_args(SocialNetworkName.__value__)

class SocialNetwork(BaseModelWithoutExtraKeys):
    network: SocialNetworkName = pydantic.Field()
    username: str = pydantic.Field(examples=['john_doe', '@johndoe@mastodon.social', '12345/john-doe'])

```

```python
class CustomConnection(BaseModelWithoutExtraKeys):
    fontawesome_icon: str
    placeholder: str
    url: pydantic.HttpUrl | None

```

### 条目类型

`cv.sections` 是一个字典：键是部分标题（任何字符串），值是条目的列表。每个部分必须使用**单个**条目类型——您不能在同一部分中混合不同的条目类型。条目类型会根据每个条目中存在的字段自动检测。

**共享字段**——这些字段可用于支持日期和复杂字段的条目类型（ExperienceEntry、EducationEntry、NormalEntry、PublicationEntry）：

| 字段 | 类型 | 默认值 | 备注 |
|---|---|---|---|
| `date` | `str \| int \| null` | `null` | 自由形式：`"2020-09"`、`"Fall 2023"` 等。与 `start_date`/`end_date` 互斥。 |
| `start_date` | `str \| int \| null` | `null` | 严格格式：YYYY-MM-DD、YYYY-MM 或 YYYY。 |
| `end_date` | `str \| int \| "present" \| null` | `null` | 与 `start_date` 相同的格式，或 `"present"`。省略时，如果 `start_date` 已设置，则默认为 `"present"`。 |
| `location` | `str \| null` | `null` | |
| `summary` | `str \| null` | `null` | |
| `highlights` | `list[str] \| null` | `null` | 项目符号。 |

**9 个条目类型：**

| 条目类型 | 必填字段 | 可选字段 | 典型用途 |
|---|---|---|---|
| **ExperienceEntry** | `company`, `position` | 所有共享字段 | 工作职位 |
| **EducationEntry** | `institution`, `area` | `degree` + 所有共享字段 | 学位、学校 |
| **PublicationEntry** | `title`, `authors` | `doi`, `url`, `journal`, `summary`, `date` | 论文、文章 |
| **NormalEntry** | `name` | 所有共享字段 | 项目、奖项 |
| **OneLineEntry** | `label`, `details` | — | 技能、语言 |
| **BulletEntry** | `bullet` | — | 简单项目符号 |
| **NumberedEntry** | `number` | — | 编号列表项 |
| **ReversedNumberedEntry** | `reversed_number` | — | 倒序编号项（5, 4, 3...） |
| **TextEntry** | *(普通字符串)* | — | 自由形式的段落 |

示例：

```yaml
cv:
  sections:
    experience:          # ExperienceEntry 列表（通过 company + position 检测）
      - company: Google
        position: Engineer
        start_date: 2020-01
        highlights:
          - 做了有影响力的某事
    skills:              # OneLineEntry 列表（通过 label + details 检测）
      - label: Languages
        details: Python, C++
    about_me:            # TextEntry 列表（普通字符串）
      - 这是一个关于我的自由形式段落。
```

条目还接受任意额外的键（在渲染过程中会被忽略）。字段名拼写错误不会导致错误。

### 设计 (`design`)

所有内置主题共享相同的结构——它们只在不同默认值上有所不同。请参阅以下示例设计，了解每个可用字段及其默认值。设置 `design.theme` 以选择主题，然后覆盖任何字段。

### 区域设置 (`locale`)

内置区域设置：`english`、`arabic`、`danish`、`dutch`、`french`、`german`、`hebrew`、`hindi`、`hungarian`、`indonesian`、`italian`、`japanese`、`korean`、`mandarin_chinese`、`norwegian_bokmål`、`norwegian_nynorsk`、`persian`、`portuguese`、`russian`、`spanish`、`turkish`、`vietnamese`

设置 `locale.language` 为内置区域设置名称以使用它。覆盖任何字段以自定义翻译。设置 `language` 为任何字符串并提供所有翻译，以创建完全自定义的区域设置。

### 设置 (`settings`)

关键字段：`bold_keywords`（要自动加粗的字符串列表）、`current_date`（覆盖今天的日期）、`render_command.*`（输出路径、生成标志）。

## 重要模式

### YAML 引用

**始终引用包含冒号（`:`）的字符串值。** 这是最常见的导致 YAML 无效的原因。突出显示、标题、摘要以及任何自由形式文本通常包含冒号：

```yaml
# 错误——冒号破坏 YAML 解析：
- title: 催化机制：一种新方法
  highlights:
    - 相关课程：分布式系统、ML

# 正确——用双引号包裹：
- title: "催化机制：一种新方法"
  highlights:
    - "相关课程：分布式系统、ML"
```

规则：如果字符串值包含 `:`, 必须引用它。如有疑问，请引用。

### 项目符号字符

`design.highlights.bullet` 字段只接受以下确切字符：`●`、`•`、`◦`、`-`、`◆`、`★`、`■`、`—`、`○`。不要使用连字符（`–`）、`>`、`*` 或任何其他字符。如有疑问，请省略 `bullet` 以使用主题默认值。

### 电话号码

电话号码必须使用国际格式并包含国家代码（E.164）。永远不要编造电话号码——只有在用户提供时才包含。

```yaml
# 错误：
phone: "(555) 123-4567"
phone: "555-123-4567"

# 正确：
phone: "+15551234567"
```

如果用户提供了不带国家代码的本地号码，请询问是哪个国家，或者省略电话字段。

### 文本格式化

所有文本字段支持内联 Markdown：`**加粗**`、`*斜体*`、`[链接文本](url)`。不支持块级 Markdown（标题、列表、引用块、代码块）。原始 Typst 命令和数学（`$$f(x)$$`）也会通过。

### 日期处理

- `date` 和 `start_date`/`end_date` 互斥。如果提供 `date`，`start_date` 和 `end_date` 将被忽略。
- 如果只提供 `start_date`，`end_date` 默认为 `"present"`。
- `start_date`/`end_date` 需要严格格式：YYYY-MM-DD、YYYY-MM 或 YYYY。
- `date` 是灵活的：接受任何字符串（"Fall 2023"）以及日期格式。

### 部分标题

- `snake_case` 键自动大写：`work_experience` → "Work Experience"
- 空格或大写键的键将按原样使用。

### 出版物作者

使用 `*姓名*`（单个星号，斜体）突出显示 CV 所有者。

### 嵌套突出显示（子项目符号）

```yaml
highlights:
  - 主要项目符号
    - 子项目符号 1
    - 子项目符号 2
```

## CLI 参考

### `rendercv new "全名"`

生成一个起始 YAML 文件。

| 选项 | 短 | 它的作用 |
|---|---|---|
| `--theme THEME` | | 使用的主题（默认：`classic`） |
| `--locale LOCALE` | | 使用的区域设置（默认：`english`） |
| `--create-typst-templates` | | 还创建可编辑的 Typst 模板文件，以实现完整的设计控制 |

### `rendercv render <input.yaml>`

从 YAML 文件生成 PDF、Typst、Markdown、HTML 和 PNG。

| 选项 | 短 | 它的作用 |
|---|---|---|
| `--watch` | `-w` | 当 YAML 文件更改时自动重新渲染 |
| `--quiet` | `-q` | 隐藏所有输出消息 |
| `--design FILE` | `-d` | 从单独的 YAML 文件加载设计部分 |
| `--locale-catalog FILE` | `-lc` | 从单独的 YAML 文件加载区域设置部分 |
| `--settings FILE` | `-s` | 从单独的 YAML 文件加载设置部分 |
| `--output-folder DIR` | `-o` | 自定义输出目录 |

按格式控制：`--{format}-path PATH` 设置自定义输出路径，`--dont-generate-{format}` 跳过生成。格式：`pdf`、`typst`、`markdown`、`html`、`png`。

**使用点表示法从 CLI 覆盖任何 YAML 字段**（无需编辑文件）：

```bash
rendercv render CV.yaml --cv.name "Jane Doe" --design.theme "moderncv"
rendercv render CV.yaml --cv.sections.education.0.institution "MIT"
```

### `rendercv create-theme "主题名称"`

构建一个自定义主题目录，其中包含可编辑的 Typst 模板，以实现完整的设计控制。

## JSON 模式

用于 YAML 编辑器自动完成和验证：

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/rendercv/rendercv/refs/tags/v2.8/schema.json
```

## 完整示例

### 示例 CV

```yaml
cv:
  name: John Doe
  headline:
  location: 加利福尼亚州旧金山
  email: john.doe@email.com
  photo:
  phone:
  website: https://rendercv.com/
  social_networks:
  - network: LinkedIn
    username: rendercv
  - network: GitHub
    username: rendercv
  custom_connections:
  sections:
    Welcome to RenderCV:
    - RenderCV 读取 YAML 文件中编写的简历，并生成具有专业排版风格的 PDF 文件。
    - 每个部分标题都是任意的。
    education:
    - institution: 普林斯顿大学
      area: 计算机科学
      degree: 博士
      date:
      start_date: 2018-09
      end_date: 2023-05
      location: 新泽西州普林斯顿
      summary:
      highlights:
      - 论文：面向资源受限部署的高效神经网络架构搜索
      - 导师：Sanjeev Arora 教授
      - NSF 研究生研究奖学金，Siebel 学者（2022届）
    - institution: 博德西大学
      area: 计算机工程
      degree: 学士
      date:
      start_date: 2014-09
      end_date: 2018-06
      location: 土耳其伊斯坦布尔
      summary:
      highlights:
      - GPA: 3.97/4.00，优秀毕业生
      - 富布赖特奖学金获得者
    experience:
    - company: Nexus AI
      position: 联合创始人兼首席技术官
      date:
      start_date: 2023-06
      end_date: 至今
      location: 加利福尼亚州旧金山
      summary:
      highlights:
      - 建立基础模型基础设施，每月服务 200 万+ API 请求，可用率 99.97%
      - 融资 1800 万美元 A 轮，由红杉资本领投，a16z 和 Founders Fund 参与投资
      - 将工程团队从 3 人扩展到 28 人，涵盖机器学习研究、平台和应用人工智能部门
      - 开发专有推理优化技术，相比基准延迟降低 73%
    - company: NVIDIA Research
      position: 研究实习生
      date:
      start_date: 2022-05
      end_date: 2022-08
      location: 加利福尼亚州圣克拉拉
      summary:
      highlights:
      - 设计稀疏注意力机制，将 Transformer 内存占用减少 4.2 倍
      - 合著论文被 NeurIPS 2022 接收（专题演讲，前 5% 的投稿）
    projects:
    - name: '[FlashInfer](https://github.com/)'
      date:
      start_date: 2023-01
      end_date: 至今
      location:
      summary: 高性能 LLM 推理内核的开源库
      highlights:
      - 在 A100 GPU 上相比基准注意力实现速度提升 2.8 倍
      - 被 3 个主要 AI 实验室采用，GitHub 星标 8,500+，贡献者 200+
    - name: '[NeuralPrune](https://github.com/)'
      date: '2021'
      start_date:
      end_date:
      location:
      summary: 具有可微分掩码的自动神经网络剪枝工具包
      highlights:
      - 在 ImageNet 上模型大小减少 90%，精度下降不到 1%
      - 被 PyTorch 生态系统工具收录，GitHub 星标 4,200+
    publications:
    - title: '大规模稀疏专家混合：高效路由万亿参数模型'
      authors:
      - '*John Doe*'
      - Sarah Williams
      - David Park
      summary:
      doi: 10.1234/neurips.2023.1234
      url:
      journal: NeurIPS 2023
      date: 2023-07
    - title: 通过可微分剪枝进行神经网络架构搜索
      authors:
      - James Liu
      - '*John Doe*'
      summary:
      doi: 10.1234/neurips.2022.5678
      url:
      journal: NeurIPS 2022, 专题演讲
      date: 2022-12
    selected_honors:
    - bullet: MIT 科技评论 35 位 35 岁以下创新者（2024）
    - bullet:福布斯 企业技术 30 位 30 岁以下（2024）
    skills:
    - label: 语言
      details: Python, C++, CUDA, Rust, Julia
    - label: 机器学习框架
      details: PyTorch, JAX, TensorFlow, Triton, ONNX
    patents:
    - number: 边缘设备上神经网络的自适应量化（美国专利 11,234,567）
    - number: 高效 Transformer 注意力的动态稀疏模式（美国专利 11,345,678）
    invited_talks:
    - reversed_number: 高效推理的规模定律 — 斯坦福 HAI 研讨会（2024）
    - reversed_number: 为未来十年构建 AI 基础设施 — TechCrunch Disrupt（2024）

```

### 样式设计（经典 — 完整参考）

这显示了每个可用的设计字段及其默认值。所有主题共享相同结构。

```yaml
design:
  theme: classic
  page:
    size: 美国信纸
    top_margin: 0.7 英寸
    bottom_margin: 0.7 英寸
    left_margin: 0.7 英寸
    right_margin: 0.7 英寸
    show_footer: true
    show_top_note: true
  colors:
    body: rgb(0, 0, 0)
    name: rgb(0, 79, 144)
    headline: rgb(0, 79, 144)
    connections: rgb(0, 79, 144)
    section_titles: rgb(0, 79, 144)
    links: rgb(0, 79, 144)
    footer: rgb(128, 128, 128)
    top_note: rgb(128, 128, 128)
  typography:
    line_spacing: 0.6em
    alignment: 两端对齐
    date_and_location_column_alignment: 右对齐
    font_family:
      body: Source Sans 3
      name: Source Sans 3
      headline: Source Sans 3
      connections: Source Sans 3
      section_titles: Source Sans 3
    font_size:
      body: 10pt
      name: 30pt
      headline: 10pt
      connections: 10pt
      section_titles: 1.4em
    small_caps:
      name: false
      headline: false
      connections: false
      section_titles: false
    bold:
      name: true
      headline: false
      connections: false
      section_titles: true
  links:
    underline: false
    show_external_link_icon: false
  header:
    alignment: 居中
    photo_width: 3.5 厘米
    photo_position: 左侧
    photo_space_left: 0.4 厘米
    photo_space_right: 0.4 厘米
    space_below_name: 0.7 厘米
    space_below_headline: 0.7 厘米
    space_below_connections: 0.7 厘米
    connections:
      phone_number_format: 国家格式
      hyperlink: true
      show_icons: true
      display_urls_instead_of_usernames: false
      separator: ''
      space_between_connections: 0.5 厘米
  section_titles:
    type: 带部分线条
    line_thickness: 0.5pt
    space_above: 0.5 厘米
    space_below: 0.3 厘米
  sections:
    allow_page_break: true
    space_between_regular_entries: 1.2em
    space_between_text_based_entries: 0.3em
    show_time_spans_in:
      - experience
  entries:
    date_and_location_width: 4.15 厘米
    side_space: 0.2 厘米
    space_between_columns: 0.1 厘米
    allow_page_break: false
    short_second_row: true
    degree_width: 1 厘米
    summary:
      space_above: 0cm
      space_left: 0cm
    highlights:
      bullet: •
      nested_bullet: •
      space_left: 0.15cm
      space_above: 0cm
      space_between_items: 0cm
      space_between_bullet_and_text: 0.5em
  templates:
    footer: '*NAME -- PAGE_NUMBER/TOTAL_PAGES*'
    top_note: '*LAST_UPDATED CURRENT_DATE*'
    single_date: MONTH_ABBREVIATION YEAR
    date_range: START_DATE – END_DATE
    time_span: HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS
    one_line_entry:
      main_column: '**LABEL:** DETAILS'
    education_entry:
      main_column: |-
        **INSTITUTION**, AREA
        SUMMARY
        HIGHLIGHTS
      degree_column: '**DEGREE**'
      date_and_location_column: |-
        LOCATION
        DATE
    normal_entry:
      main_column: |-
        **NAME**
        SUMMARY
        HIGHLIGHTS
      date_and_location_column: |-
        LOCATION
        DATE
    experience_entry:
      main_column: |-
        **COMPANY**, POSITION
        SUMMARY
        HIGHLIGHTS
      date_and_location_column: |-
        LOCATION
        DATE
    publication_entry:
      main_column: |-
        **TITLE**
        SUMMARY
        AUTHORS
        URL (JOURNAL)
      date_and_location_column: DATE

```

### 其他主题覆盖

其他主题仅覆盖上述经典默认值中的特定字段。要使用主题，请设置 `design.theme`，并可选地覆盖任何字段。每个主题还自定义 `design.templates`（条目布局模式）——请参考上述经典示例以获取完整的模板结构。以下覆盖的 YAML 文件为简洁起见省略了模板。

#### harvard

```yaml
# yaml-language-server: $schema=../../../../../../schema.json
design:
  theme: harvard
  page:
    top_margin: 0.5 英寸
    bottom_margin: 0.5 英寸
    left_margin: 0.5 英寸
    right_margin: 0.5 英寸
    show_top_note: false
  colors:
    name: rgb(0,0,0)
    headline: rgb(0,0,0)
    connections: rgb(0,0,0)
    section_titles: rgb(0,0,0)
    links: rgb(0,0,0)
  typography:
    font_family:
      body: XCharter
      name: XCharter
      headline: XCharter
      connections: XCharter
      section_titles: XCharter
    font_size:
      name: 25pt
      connections: 9pt
      section_titles: 1.3em
  header:
    space_below_name: 0.5 厘米
    space_below_headline: 0.5 厘米
    space_below_connections: 0.5 厘米
    connections:
      show_icons: false
      separator: •
      space_between_connections: 0.4 厘米
  section_titles:
    type: 居中带居中部分线条
    space_below: 0.2 厘米
  sections:
    space_between_regular_entries: 1em
    show_time_spans_in: []
  entries:
    short_second_row: false
```

#### engineeringresumes

```yaml
# yaml-language-server: $schema=../../../../../../schema.json
design:
  theme: engineeringresumes
  page:
    show_footer: false
  typography:
    font_family:
      body: XCharter
      name: XCharter
      headline: XCharter
      connections: XCharter
      section_titles: XCharter
    font_size:
      name: 25pt
      section_titles: 1.2em
    bold:
      name: false
  header:
    connections:
      separator: |
      show_icons: false
      display_urls_instead_of_usernames: true
  colors:
    name: rgb(0,0,0)
    connections: rgb(0,0,0)
    headline: rgb(0,0,0)
    section_titles: rgb(0,0,0)
    links: rgb(0,0,0)
  links:
    underline: true
    show_external_link_icon: false
  section_titles:
    type: 带完整线条
    space_above: 0.5 厘米
    space_below: 0.3 厘米
  sections:
    space_between_regular_entries: 0.42 厘米
    space_between_text_based_entries: 0.15 厘米
    show_time_spans_in: []
  entries:
    short_second_row: false
    summary:
      space_above: 0.08 厘米
    side_space: 0cm
    highlights:
      bullet: ●
      nested_bullet: ●
      space_left: 0cm
      space_above: 0.08 厘米
      space_between_items: 0.08 厘米
      space_between_bullet_and_text: 0.3em
```

#### engineeringclassic

```yaml
# yaml-language-server: $schema=../../../../../../schema.json
design:
  theme: engineeringclassic
  typography:
    font_family:
      body: Raleway
      name: Raleway
      headline: Raleway
      connections: Raleway
      section_titles: Raleway
    bold:
      name: false
      section_titles: false
  header:
    alignment: 左对齐
  links:
    show_external_link_icon: false
  section_titles:
    type: 带完整线条
  sections:
    show_time_spans_in: []
  entries:
    short_second_row: false
    summary:
      space_above: 0.12 厘米
    highlights:
      space_left: 0cm
      space_above: 0.12 厘米
      space_between_items: 0.12 厘米
```

#### sb2nov

```yaml
# yaml-language-server: $schema=../../../../../../schema.json
design:
  theme: sb2nov
  typography:
    font_family:
      body: New Computer Modern
      name: New Computer Modern
      headline: New Computer Modern
      connections: New Computer Modern
      section_titles: New Computer Modern
  colors:
    name: rgb(0,0,0)
    connections: rgb(0,0,0)
    section_titles: rgb(0,0,0)
    headline: rgb(0,0,0)
    links: rgb(0,0,0)
  links:
    underline: true
    show_external_link_icon: false
  section_titles:
    type: 带完整线条
  sections:
    show_time_spans_in: []
  header:
    connections:
      hyperlink: true
      show_icons: false
      display_urls_instead_of_usernames: true
      separator: •
  entries:
    short_second_row: false
    highlights:
      bullet: ◦
      nested_bullet: ◦
```

#### moderncv

```yaml
# yaml-language-server: $schema=../../../../../../schema.json
design:
  theme: moderncv
  typography:
    line_spacing: 0.6em
    font_family:
      body: Fontin
      name: Fontin
      headline: Fontin
      connections: Fontin
      section_titles: Fontin
    font_size:
      name: 25pt
      section_titles: 1.4em
    bold:
      name: false
      section_titles: false
  header:
    alignment: 左对齐
    photo_width: 4.15 厘米
    photo_space_left: 0cm
    photo_space_right: 0.3 厘米
  links:
    underline: true
    show_external_link_icon: false
  section_titles:
    type: moderncv
    space_above: 0.55 厘米
    space_below: 0.3 厘米
    line_thickness: 0.15cm
  sections:
    show_time_spans_in: []
  entries:
    short_second_row: false
    side_space: 0cm
    space_between_columns: 0.3 厘米
    summary:
      space_above: 0.1 厘米
    highlights:
      space_left: 0cm
      space_above: 0.15 厘米
      space_between_items: 0.1cm
      space_between_bullet_and_text: 0.3em
```
