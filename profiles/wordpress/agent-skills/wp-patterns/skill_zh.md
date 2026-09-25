# WordPress 块模式

## 所需输入

- 仓库根目录和目标主题/插件目录。
- 模式类型：部分、启动页面、模板、模板部分或手动注册的插件模式。
- 主题/插件别名、模式别名和文本域。
- 模式标题、分类、关键词、块类型、模板类型和插入器可见性。
- 如果与该仓库的兼容性协议不同，则指定目标 WordPress 版本。
- 可用的 `theme.json` 预设，用于颜色、排版、间距、布局和渐变。
- 图标/图像的资产路径，包括资产是否为装饰性或信息性。
- 验证环境：WordPress Playground、wp-env、本地 WordPress 或手动代码编辑器检查。
- 如果更新现有模式：当前别名、当前文件路径以及是否必须保持现有插入内容的兼容性。
- 对于子主题：子主题别名、文本域和资产根；除非明确指定，否则不要重用父命名空间。

## 指导原则

1.  **仅块标记** — 通过块注释属性和 `preset` 别名表达所有视觉设计。不允许内联 `<style>` 标签、自定义 CSS 类、块包装器外的任意 HTML。阅读 `references/design-with-tokens.md` 了解核心原则。

2.  **无 JavaScript** — 模式是静态的 `block markup`。对于交互性，使用原生支持交互的块（导航、搜索、查询循环）。

3.  **注册时 PHP** — 模式文件在注册时执行一次 PHP，而不是在渲染时。阅读 `references/pattern-registration.md` 了解安全的输出函数、i18n 和应避免的函数。

4.  **有效嵌套** — 阅读 `references/block-markup-reference.md` 了解注释语法和嵌套规则。

5.  **原生块用于行为** — 使用查询循环、搜索、导航、社交图标或现有的表单块，而不是自定义 PHP/HTML 行为。对于订阅、捐赠、支付或地图行为，创建 CTA/占位符或使用现有块/插件。

6.  **本地资产** — 使用 `get_theme_file_uri()` 并与 `esc_url()` 一起使用；除非用户批准，否则不要使用外部占位符 URL。阅读 `references/pattern-registration.md` 和 `references/anti-patterns.md` 了解示例。

## 程序

### 0) 筛选并定位模式目标

1.  在仓库中工作时运行筛选：
   - `node skills/wp-project-triage/scripts/detect_wp_project.mjs`
2.  对于块主题，定位目标主题根目录：
   - `node skills/wp-block-themes/scripts/detect_block_themes.mjs`
3.  确认模式属于主题 `patterns/` 目录或需要手动插件注册。
4.  如果存在多个主题/插件，将所有更改范围限定在请求的目标。

如果用户未提供所需输入，仅推断低风险默认值。在创建主题别名、文本域、资产路径、自定义帖子类型、分类、事件日期字段或主题特定 `preset` 之前先询问。如果 `theme.json` 缺失或预设无法验证，请使用保守的核心预设或在使用主题特定别名之前先询问。

**完成时：** 目标主题/插件根目录、模式类型和注册路径已确认。

### 1) 设计思考

在编写 `block markup` 之前，做出五个明确的设计决策——目的、语气、空间布局、排版层次结构和颜色策略。

阅读 `references/design-with-tokens.md` 了解决策框架和 `preset` 映射。

对于模式类型元数据（启动页面、模板模式、模板部分、查询循环、表单/CTA、比较/定价、社交/导航/搜索、404），阅读 `references/pattern-categories-and-types.md`——包括使用 `core/query` 时的查询循环模式部分。

当请求需要视觉上**独特**的布局时，阅读 `references/visual-composition.md`。

**完成时：** 五个设计决策已做出并记录在 markup 之前。

### 2) 规划块结构

在编写 markup 之前，绘制嵌套树。英雄模式的示例：

```
Group (全宽、约束布局、深色背景、垂直填充 80)
  Group (约束内部、垂直 flex、居中对齐)
    Paragraph (大写标签、小号、字间距、强调色)
    Heading (h2、超大号、标题字体、紧凑行高)
    Paragraph (引导文本、大号、次要颜色)
    Buttons (flex、居中)
      Button (主要背景、基础文本)
      Button (轮廓样式)
```

**完成时：** 嵌套树已绘制，层次结构在编写注释标签之前是故意的。

### 3) 编写模式文件

组装 PHP 头部和 `block markup`。阅读 `references/pattern-registration.md` 了解头部字段、PHP 规则、手动注册和文件示例。

使用步骤 1 中的分类和模板类型。当步骤 1 中未决定头部元数据时，阅读 `references/pattern-categories-and-types.md`。

**块 markup 正文：**
- 遵循步骤 2 的嵌套树
- 使用 `preset` 别名用于颜色、字体大小、间距
- 使用反映实际内容的占位符文本——而不是 "Lorem ipsum"

**完成时：** PHP 头部和块 markup 文件已编写。

### 4) 设计质量检查

对照 `references/anti-patterns.md` 中的设计质量检查清单进行审查。每一项都必须通过。

**完成时：** 每一项设计质量检查清单都通过。

### 5) 技术验证

对照 `references/anti-patterns.md` 中的技术验证检查清单进行审查。每一项都必须通过。

**完成时：** 每一项技术验证检查清单都通过。

## 验证

在真实的 WordPress 环境中测试模式：

**使用 WordPress Playground（推荐）：**
```bash
npx @wp-playground/cli@latest server --auto-mount
```
挂载主题目录并验证：
- 模式出现在指定分类下的插入器中
- 模式插入时没有块验证错误
- 布局在桌面和移动宽度下正确渲染
- 内容可编辑（文本、图像、按钮）
- 如果使用 `templateLock`，锁定元素抵抗编辑

对于模板模式，验证站点编辑器在预期的模板替换流程中提供该模式。如果使用 `Inserter: no`，确认它被隐藏在通用插入器之外，但在预期位置仍然可用。

**手动检查：**
- 将块 markup 粘贴到 WordPress 中的代码编辑器视图
- 切换到可视化编辑器——块应解析而不会出现“尝试恢复块”提示
- 如果需要恢复，则 markup 存在语法错误

如果模式更改影响资产、生成文件或注册代码，请运行仓库现有的 lint、构建或测试命令。

在更新现有模式时，请记住，插入的模式内容会被复制到帖子/模板中。更改模式文件不会回溯更新已插入的内容，并且更改块名称或保存的 markup 可能会为新插入的内容创建恢复提示。

对于 PR 或包审查，确认 diff 仅限于预期的模式文件、引用、脚本和 eval 情景。不要将不相关的仓库更新混合到模式更改中。

## 失败模式 / 调试

从 `references/block-markup-reference.md`、`references/pattern-registration.md` 和 `references/anti-patterns.md` 开始。

常见失败：

- **模式未出现在插入器中**：检查所需的 `Title`、`Slug` 和 `Categories` 头部；确认文件位于 `patterns/*.php` 下；确认 `Inserter: no` 没有隐藏它。
- **显示错误或覆盖了正确的模式**：检查别名冲突，并确保别名命名空间为 `theme-slug/pattern-name` 或 `plugin-slug/pattern-name`。
- **出现块恢复提示**：验证块注释嵌套、JSON 语法和关闭注释。
- **字符串未翻译或未转义**：用 `esc_html_e()`、`esc_html__()`、`esc_attr_e()`、`esc_attr__()` 或 `esc_url()` 替换原始文本/PHP 输出。
- **翻译未加载**：验证文本域与目标主题/插件匹配。
- **动态内容过时或不可用**：移除查询依赖的 PHP (`get_posts()`、`the_title()`、`wp_get_current_user()`) 并使用查询循环等块。
- **查询循环输出不完整**：检查 `core/post-template`、帖子标题/摘要/日期/图像块、需要时分页，以及 `core/query-no-results` 回退。
- **存档/搜索/分类/作者上下文错误**：使用继承查询上下文，而不是硬编码的运行时 PHP。
- **CPT 或事件列表错误**：确认帖子类型别名、分类/日期字段，并在生成模式之前使用插件提供的块。
- **样式与主题不匹配**：确认 `preset` 别名存在于 `theme.json` 中；除非有文档，否则避免使用不受支持的主题特定别名。
- **无障碍性问题**：修复跳过的标题级别、信息性图像的空 alt 文本、低对比度预设组合、模糊的按钮/链接文本、社交图标标签、搜索标签和纯颜色强调。
- **手动注册失败**：确认代码在 `init` 上运行，分类在模式之前注册，并且模式内容保持静态块 markup。

## 升级

当出现以下情况时停止并寻求帮助或查阅规范文档：

- 主题特定 `preset` 别名、文本域、资产路径或模式分类无法验证。
- 需要人类设计/无障碍性判断的颜色对比度、图像含义或内容层次结构。
- 行为取决于未包含在此仓库兼容性协议中的 WordPress/Gutenberg 版本。

## 示例提示

阅读 `references/example-prompts.md`。
