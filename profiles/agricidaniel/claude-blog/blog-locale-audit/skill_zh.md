# 博客本地化审计，多语言质量管控

审计多语言博客内容目录，确保每种语言版本完整、一致、正确标记并SEO优化。在影响排名之前捕获国际内容问题。

> 根据 Chris Mueller (`claude-blog-multilingual`) 的版本改编（Pro Hub Challenge，2026年3月）。原始版本：https://github.com/Chriss54/multilingual-int

## 工作流程

### 第一阶段：发现

1.  在项目根目录/当前工作目录内解析目标目录。拒绝符号链接目录和根目录外的遍历，然后扫描博客内容并按语言分组，使用：
    - 子目录名称 (`en/`, `de/`, `fr/`)。
    - 前置字段 `lang` 和 `translatedFrom`。
    - 如果存在，`hreflang-map.json`。
2.  使用 `blog-translate`、`blog-localize` 和 `blog-multilingual` 使用的共享多语言本地化规则规范化检测到的语言代码：ISO 639-1 语言小写，可选 ISO 15924 脚本大写，可选 ISO 3166-1 Alpha-2 地区大写。除非内容声明了明确的中间模式，否则标记模糊的语言代码，如 `es`、`pt` 和 `zh`。
3.  构建内容矩阵，映射哪个帖子存在于哪种语言中。在比较缩略名之前使用稳定的翻译组键：`translationGroupId`、`sourceSlug`、`translationOfWork.url` 方案或 `hreflang-map.json` 中的 ID 和 URL。当没有稳定键时，仅回退规范化源缩略名。
4.  检测源语言（最常见的 `translatedFrom` 目标，或 `hreflang-map.json` 中的 `sourceLanguage` 字段，如果存在）。

### 第二阶段：完整性审计

显示哪些翻译缺失：

```
### 翻译覆盖率矩阵

| 帖子 (EN) | DE | FR | ES | JA |
|-----------|----|----|----|----|
| how-to-avoid-ai-slop | ok | ok | 缺失 | 缺失 |
| content-marketing-2026 | ok | 缺失 | ok | 缺失 |

覆盖率：60%（10个预期翻译中有6个存在）
缺失：需要4个翻译
```

### 第三阶段：内容一致性审计

对于每个存在于多种语言中的帖子：

| 检查 | 内容 | 严重性 |
|------|------|--------|
| 段落数 | 相同数量的 H2 和 H3 段落 | 关键 |
| FAQ 数量 | 相同数量的 FAQ 项目 | 高 |
| 图片数量 | 相同数量的图片 | 高 |
| 图表数量 | 相同数量的图表（SVG 图形） | 高 |
| 字数比率 | 语言对预期范围内的字数（DE +20% 到 +30%，JA -20%，ES +10%） | 中 |
| 链接数量 | 类似的内部和外部链接数量 | 中 |
| 有证据支持的声明 | 各版本相同的支持声明和引用 | 中 |
| 前置字段一致性 | 每个版本都存在所有必需字段 | 高 |

将每个重大偏差标记为问题。

### 第四阶段：SEO 一致性审计

对于每个语言版本验证：

| 元素 | 检查 | 严重性 |
|------|------|--------|
| 标题标签 | 存在、本地化、清晰且适用于页面 | 关键 |
| 元描述 | 存在、本地化、准确且与可见内容一致 | 关键 |
| `lang` 属性或前置字段 `lang` | 存在、有效的 Google 兼容 hreflang 或 BCP 47 语言标签 | 关键 |
| 网址规范 | 指向同语言页面，而不是源语言页面或 x-default | 关键 |
| Schema `inLanguage` | 与 `lang` 匹配 | 高 |
| Schema `translationOfWork` | 指向源 URL | 高 |
| 替代文本 | 翻译（非 EN 帖子中无英文替代文本） | 高 |
| 缩略名 | 本地化（非 EN 帖子中无英文缩略名） | 中 |
| 标签 | 本地化 | 中 |
| 关键词 | 本地化 | 中 |

### 第五阶段：Hreflang 审计

如果目录中存在 `hreflang-tags.html`、`hreflang-sitemap.xml` 或 `hreflang-map.json`：

| 检查 | 内容 | 严重性 |
|------|------|--------|
| 自引用 | 每个页面都引用自身 | 关键 |
| 返回标签 | 每个关系都是双向的 | 关键 |
| 规范一致性 | 每个hreflang页面规范到其同语言 URL | 关键 |
| `x-default` | 存在，指向未匹配语言的回退，如语言选择器或默认市场页面 | 关键 |
| 语言代码 | 有效的 Google 兼容 hreflang 标签：ISO 639-1 语言加上可选 ISO 15924 脚本或 ISO 3166-1 Alpha-2 地区 | 高 |
| URL 一致性 | 相同协议，相同尾随斜杠约定 | 中 |
| 完整性 | 每种语言版本都存在 | 高 |

如果不存在 hreflang 文件，将其报告为关键差距，并提供：
"运行 `/blog multilingual <topic> --languages ...` 重新生成，或手动创建 hreflang-tags.html。"

如果安装了 `claude-seo` 的 `seo-hreflang`，建议运行它进行更深入的验证。

### 第六阶段：新鲜度审计

对于前置字段中包含 `translatedDate` 的帖子：

| 检查 | 内容 | 严重性 |
|------|------|--------|
| 源更新后翻译 | 源在 `translatedDate` 后修改 | 关键 |
| 源内容漂移 | 存储的源哈希或源 `dateModified` 与当前源不同 | 关键 |
| 翻译漂移 | 存储的翻译哈希与当前本地化文件不同 | 中 |
| 翻译超过90天 | 可能需要刷新 | 中 |
| `lastUpdated` 跨版本不匹配 | 版本不同步 | 中 |
| Git 或文件 mtime 新于 `translatedDate` | 内容更改而未更新前置字段 | 警告 |

在仅依赖 `translatedDate` 之前，存储并比较 `sourceHash`、源 `dateModified`、`translationHash` 和 Git mtime。

针对每个陈旧文件发出可操作的命令：

```
3 个翻译陈旧：
- de/ki-trends-2026.md（源2天前更新）
  -> 运行：/blog translate en/ai-trends-2026.md --to de
- fr/ki-trends-2026.md（源2天前更新）
  -> 运行：/blog translate en/ai-trends-2026.md --to fr
- es/tendencias-ia-2026.md（翻译超过90天）
  -> 运行：/blog translate en/ai-trends-2026.md --to es
```

### 第七阶段：报告

默认情况下以 Markdown 输出。如果用户传递 `--html`，也仅将报告写入审计项目根目录内的 `locale-audit-report.html`。在渲染 HTML 之前，使用 `html.escape(value, quote=True)` 转义所有动态文件名、标题、URL 和问题文本，并拒绝符号链接或根目录外报告路径。

```
## 多语言内容审计报告

### 摘要
- 审计帖子：[N] 个跨 [N] 种语言
- 整体健康状况：[分数] / 100
- 关键问题：[N]
- 警告：[N]

### 翻译覆盖率
[第二阶段的矩阵]

### 发现的问题
#### 关键
- [文件引用问题]

#### 警告
- [文件引用问题]

#### 通过
- [通过检查]

### 优先修复
1. [最高影响操作]
2. [...]

### 陈旧翻译警报
[第六阶段的可运行命令]

### 快速修复
- 运行 `/blog translate <file> --to <缺失语言>` 为 [N] 个缺失翻译。
- 运行 `/blog multilingual` 重新生成 hreflang 资产。
- 运行 `/blog localize <file> --locale <代码>` 进行弱文化适应。
```

## 错误处理

| 情景 | 操作 |
|------|------|
| 空目录 | "在 [路径] 中未找到博客帖子" |
| 仅有一种语言存在 | 报告覆盖率，建议目标语言 |
| 无 hreflang 文件 | 标记为关键差距，提供重新生成 |
| 未知文件格式 | 跳过并警告 |

## 交叉引用

- 填充缺失翻译：`/blog translate <file> --to <缺失代码>`
- 深化弱适应：`/blog localize <file> --locale <代码>`
- 重新生成 hreflang 资产：`/blog multilingual <topic> --languages <代码>`
