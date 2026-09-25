## 快速入门

**可用的主题：** `classic`，`harvard`，`engineeringresumes`，`engineeringclassic`，`sb2nov`，`moderncv`
**可用的区域设置：** `english`，`arabic`，`danish`，`dutch`，`french`，`german`，`hebrew`，`hindi`，`hungarian`，`indonesian`，`italian`，`japanese`，`korean`，`mandarin_chinese`，`norwegian_bokmål`，`norwegian_nynorsk`，`persian`，`portuguese`，`russian`，`spanish`，`turkish`，`vietnamese`

这些都是起点——设计和区域设置的所有方面都可以在 YAML 文件中完全自定义。

```bash
# 安装 RenderCV
uv tool install "rendercv[full]"

# 创建一个起始 YAML 文件（您可以指定主题和区域设置）
rendercv new "John Doe"
rendercv new "John Doe" --theme moderncv --locale german

# 渲染为 PDF（默认情况下还会生成 Typst，Markdown，HTML，PNG）
rendercv render John_Doe_CV.yaml

# 监视模式：每当 YAML 文件更改时自动重新渲染
rendercv render John_Doe_CV.yaml --watch

# 仅渲染 PNG（用于预览或检查页数）
rendercv render John_Doe_CV.yaml --dont-generate-pdf --dont-generate-html --dont-generate-markdown

# 从 CLI 覆写字段，而无需编辑 YAML
rendercv render cv.yaml --cv.name "Jane Doe" --design.theme "moderncv"
```

## YAML 结构

RenderCV 输入有四个部分。只有 `cv` 是必需的——其他的都有合理的默认值。

```yaml
cv:         # 您的内容：姓名、联系信息以及所有部分
design:     # 视觉样式：主题、颜色、字体、边距、间距、布局
locale:     # 语言：月份名称、短语、翻译
settings:   # 行为：输出路径、粗体关键字、当前日期
```

**单个文件与分离文件：** 所有四个部分可以位于一个 YAML 文件中，或者每个部分可以是单独的文件。分离文件对于跨多个简历重用相同的设计/区域设置很有用：

```bash
# 单个自包含文件（所有部分在一个文件中）
rendercv render John_Doe_CV.yaml

# 分离文件：CV 内容 + 设计 + 区域设置独立加载
rendercv render cv.yaml --design design.yaml --locale-catalog locale.yaml --settings settings.yaml
```

在使用分离文件时，每个文件只包含其部分（例如，`design.yaml` 顶部键为 `design:`）。CLI 加载的文件会覆盖主 YAML 文件中的值。

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

### CV 内容 (`cv`)

`cv.sections` 字段是一个字典，其中键是部分标题（您想要的任何字符串），值是条目列表。每个部分包含相同类型的条目。

```python
class Cv(BaseModelWithoutExtraKeys):
    name: str | None = pydantic.Field(default=None, examples=['John Doe', 'Jane Smith'])
    headline: str | None = pydantic.Field(default=None, examples=['软件工程师', '数据科学家', '产品经理'])
    location: str | None = pydantic.Field(default=None, examples=['旧金山，CA', '伦敦，UK', '伊斯坦布尔，土耳其'])
    email: pydantic.EmailStr | list[pydantic.EmailStr] | None = pydantic.Field(default=None, examples=['john.doe@example.com', ['john.doe.1@example.com', 'john.doe.2@example.com']])
    photo: ExistingPathRelativeToInput | pydantic.HttpUrl | None = pydantic.Field(default=None, union_mode='left_to_right', examples=['photo.jpg', 'images/profile.png', 'https://example.com/photo.jpg'])
    phone: pydantic_phone_numbers.PhoneNumber | list[pydantic_phone_numbers.PhoneNumber] | None = pydantic.Field(default=None, examples=['+1-234-567-8900', ['+1-234-567-8900', '+44 20 1234 5678']])
    website: pydantic.HttpUrl | list[pydantic.HttpUrl] | None = pydantic.Field(default=None, examples=['https://johndoe.com', ['https://johndoe.com', 'https://www.janesmith.dev']])
    social_networks: list[SocialNetwork] | None = pydantic.Field(default=None)
    custom_connections: list[CustomConnection] | None = pydantic.Field(default=None, examples=[[{'placeholder': '预约通话', 'url': 'https://cal.com/johndoe', 'fontawesome_icon': 'calendar-days'}]])
    sections: dict[str, Section] | None = pydantic.Field(default=None, examples=[{'Experience': '...', 'Education': '...', 'Projects': '...', 'Skills': '...'}])

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

`cv.sections` 是一个字典：键是部分标题（任何字符串），值是条目列表。每个部分必须使用**单个**条目类型——您不能在同一部分中混合不同的条目类型。条目类型是根据每个条目中存在的字段自动检测的。

**共享字段**——这些字段适用于支持日期和复杂字段的条目类型（ExperienceEntry，EducationEntry，NormalEntry，PublicationEntry）：

| 字段 | 类型 | 默认值 | 备注 |
|---|---|---|---|
| `date` | `str \| int \| null` | `null` | 自由形式：`"2020-09"`，`"Fall 2023"` 等。与 `start_date`/`end_date` 互斥。 |
| `start_date` | `str \| int \| null` | `null` | 严格格式：YYYY-MM-DD，YYYY-MM 或 YYYY。 |
| `end_date` | `str \| int \| "present" \| null` | `null` | 与 `start_date` 相同的格式，或 `"present"`。省略默认为 `"present"` 当 `start_date` 设置时。 |
| `location` | `str \| null` | `null` | |
| `summary` | `str \| null` | `null` | |
| `highlights` | `list[str] \| null` | `null` | 项目符号。 |

**9 个条目类型：**

| 条目类型 | 必填字段 | 可选字段 | 典型用途 |
|---|---|---|---|
| **ExperienceEntry** | `company`，`position` | 所有共享字段 | 工作职位 |
| **EducationEntry** | `institution`，`area` | `degree` + 所有共享字段 | 学位、学校 |
| **PublicationEntry** | `title`，`authors` | `doi`，`url`，`journal`，`summary`，`date` | 论文、文章 |
| **NormalEntry** | `name` | 所有共享字段 | 项目、奖项 |
| **OneLineEntry** | `label`，`details` | — | 技能、语言 |
| **BulletEntry** | `bullet` | — | 简单项目符号 |
| **NumberedEntry** | `number` | — | 编号列表项 |
| **ReversedNumberedEntry** | `reversed_number` | — | 倒序编号项（5，4，3...） |
| **TextEntry** | *(纯文本)* | — | 自由形式的段落 |

示例：

```yaml
cv:
  sections:
    experience:          # ExperienceEntry 列表（通过公司 + 职位检测）
      - company: Google
        position: Engineer
        start_date: 2020-01
        highlights:
          - 做出了有影响力的贡献
    skills:              # OneLineEntry 列表（通过标签 + 详情检测）
      - label: Languages
        details: Python, C++
    about_me:            # TextEntry 列表（纯文本）
      - 这是一个关于我的自由形式段落。
```

条目还接受任意额外的键（在渲染时会被忽略）。字段名拼写错误不会导致错误。

### 设计 (`design`)

所有内置主题共享相同的结构——它们只在不同之处有不同的默认值。请参阅下面的示例设计，以了解每个可用字段及其默认值。设置 `design.theme` 以选择主题，然后覆盖任何字段。

### 区域设置 (`locale`)

内置区域设置：`english`，`arabic`，`danish`，`dutch`，`french`，`german`，`hebrew`，`hindi`，`hungarian`，`indonesian`，`italian`，`japanese`，`korean`，`mandarin_chinese`，`norwegian_bokmål`，`norwegian_nynorsk`，`persian`，`portuguese`，`russian`，`spanish`，`turkish`，`vietnamese`

设置 `locale.language` 为内置区域设置名称以使用它。覆盖任何字段以自定义翻译。设置 `language` 为任何字符串，并提供所有翻译以创建完全自定义的区域设置。

### 设置 (`settings`)

关键字段：`bold_keywords`（自动加粗的字符串列表），`current_date`（覆盖当前日期），`render_command.*`（输出路径、生成标志）。

## 重要模式

### YAML 引用

**始终引用包含冒号（`:`）的字符串值。** 这是最常见的导致 YAML 无效的原因。高亮显示、标题、摘要以及任何自由形式文本通常包含冒号：

```yaml
# 错误——冒号破坏 YAML 解析：
- title: Catalytic Mechanisms: A New Approach
  highlights:
    - Relevant coursework: Distributed Systems, ML

# 正确——用双引号包裹：
- title: "Catalytic Mechanisms: A New Approach"
  highlights:
    - "Relevant coursework: Distributed Systems, ML"
```

规则：如果字符串值包含 `:，则必须引用。如有疑问，请引用。
