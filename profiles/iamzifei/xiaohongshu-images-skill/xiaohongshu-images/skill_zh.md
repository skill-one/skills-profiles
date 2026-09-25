# 小红书图片功能

该功能将 Markdown、HTML 或文本内容转换为带有 AI 生成的封面图片的精美样式 HTML 页面，然后以 3:4 的比例捕获它们作为连续截图，用于小红书发布。

## 概述

该功能执行以下工作流程：

1. **接收内容**：从用户处接收 Markdown、HTML 或 txt 格式的内容
2. **加载提示模板**：从该技能目录中的 `prompts/default.md` 读取提示模板
3. **确定输出账户**：确定使用哪个账户文件夹（见下文账户文件夹解析）
4. **生成封面图片**：使用 `/baoyu-cover-image` 技能根据文章内容生成封面图片
5. **生成 HTML**：根据提示模板规范创建精美样式的 HTML 页面
6. **保存输出**：将 HTML 保存到 `~/Dev/obsidian/{account_folder}/articles/<date-title>/xhs-preview.html`
7. **捕获截图**：捕获整个页面（不裁剪文本）的连续 3:4 比例截图

## 账户文件夹解析

该功能使用以下优先级确定输出账户文件夹：

### 优先级 1：显式 `--account` 参数

如果用户指定 `--account`，则使用相应的文件夹：

```bash
/xiaohongshu-images <article> --account james-cn      # → 10_在悉尼和稀泥
/xiaohongshu-images <article> --account james-en      # → 11_BuildWithJames
/xiaohongshu-images <article> --account mom-reading-club  # → 12_妈妈在读
```

### 优先级 2：从输入文件路径推断

如果未指定 `--account`，则尝试从输入文件路径推断：

```
输入：~/Dev/obsidian/12_妈妈在读/articles/2026-01-20-xxx/index.md
       → 输出到：~/Dev/obsidian/12_妈妈在读/articles/2026-01-20-xxx/

输入：~/Dev/obsidian/10_在悉尼和稀泥/articles/2026-01-20-xxx/index.md
       → 输出到：~/Dev/obsidian/10_在悉尼和稀泥/articles/2026-01-20-xxx/
```

### 优先级 3：回退到模板映射

如果无法从路径确定账户（例如，原始内容输入），则使用基于模板的映射：

| 模板 | 账户文件夹 |
|----------|----------------|
| `default` | `10_在悉尼和稀泥` |
| `mom-reading-club` | `12_妈妈在读` |

### 账户文件夹映射参考

| 账户 | 文件夹 |
|---------|--------|
| `james-cn` | `10_在悉尼和稀泥` |
| `james-en` | `11_BuildWithJames` |
| `mom-reading-club` | `12_妈妈在读` |

## 使用方法

当用户调用此功能时，请按照以下步骤操作：

### 第一步：识别输入

用户将提供以下之一：
- Markdown、HTML 或 txt 文件的文件路径（例如，`/path/to/article.md`）
- 直接在对话中的原始内容
- 用于获取内容的 URL

如果输入不明确，请要求用户提供文件路径、URL 或直接粘贴内容。

### 第二步：读取提示模板

从该技能目录中读取提示模板：

```
{{SKILL_DIR}}/prompts/default.md
```

使用 Read 工具获取提示模板内容。此模板定义了 HTML/CSS 样式规范。

### 第三步：提取文章标题、日期和确定账户

从内容中提取：
- **标题**：主要标题（h1）或内容中的第一个重要标题
- **日期**：当前日期，格式为 YYYY-MM-DD
- **账户文件夹**：使用上述优先级规则确定（--account → 路径推断 → 模板映射）

创建输出文件夹路径为：`~/Dev/obsidian/{account_folder}/articles/<date>-<sanitized-title>/`
- 将空格替换为连字符
- 移除特殊字符
- 保持标题合理长度（最多 50 个字符）
- 所有图片都放在 `_attachments/` 子文件夹中

### 第四步：使用 baoyu-cover-image 技能生成封面图片

**⚠️ 合规性检查**：在生成之前，确保图片主题符合小红书社区规范（提示模板第 11 节）。图片必须：
- 适合所有年龄段，无暴露服装或挑逗姿势
- 避免政治符号、暴力、赌博、吸烟或酗酒
- 传达积极、建设性的信息
- 具有文化敏感性且原创

使用 `/baoyu-cover-image` 技能生成封面图片：

1. **调用技能** 并使用文章内容：

```bash
/baoyu-cover-image ~/Dev/obsidian/{account_folder}/articles/<date>-<title>/index.md --style <auto-or-specified> --no-title
```

或者如果内容尚未保存，直接将内容传递给技能。

2. **样式选择**：
   - 让 baoyu-cover-image 根据内容信号自动选择，OR
   - 指定与文章基调匹配的样式：
     - `tech` - AI、编程、数字主题
     - `warm` - 个人故事、情感内容
     - `bold` - 有争议、吸引注意力的主题
     - `minimal` - 简单、禅意的内容
     - `playful` - 趣味、休闲、适合初学者的内容
     - `nature` - 健康养生、有机主题
     - `retro` - 历史、复古、传统主题
     - `elegant` - 商业、专业内容（默认）

   **特殊：妈妈读书会模板**

   使用 `mom-reading-club` 模板时，使用 **书法水墨风** 覆盖默认封面样式：

   ```bash
   /baoyu-cover-image <article> --style minimal --no-title --custom-prompt "Chinese calligraphy and ink-wash illustration style (书法水墨风). Zen-like simplicity with generous white space (留白). Include subtle ink-wash brush strokes as background texture. Minimalist botanical elements (bamboo, plum blossoms, orchids, lotus) when appropriate. Color palette: ink black (#1a1a1a), warm gray (#666666), subtle gold accents (#C9A962), warm off-white background (#F5F3EE). If human figures are included, depict an elegant woman aged 30-45 with a contemplative, refined demeanor. NO TEXT on the cover."
   ```

3. **使用 `--no-title` 标志**，因为小红书封面通常使用纯视觉图像，不嵌入文本。

4. **将生成的图像移动到正确位置**：
   - baoyu-cover-image 保存到 `imgs/cover.png`（相对于文章）
   - 移动/复制到 `~/Dev/obsidian/{account_folder}/articles/<date>-<title>/_attachments/cover-xhs.png`

```bash
mv ~/Dev/obsidian/{account_folder}/articles/<date>-<title>/imgs/cover.png ~/Dev/obsidian/{account_folder}/articles/<date>-<title>/_attachments/cover-xhs.png
```

### 第五步：生成 HTML

**⚠️ 合规性检查**：在生成 HTML 之前，检查文本内容是否符合合规性：
- 无绝对/超级形容词（最好、第一、国家级、最高级、全网最低价）
- 无夸张效果声明（一分钟见效、吃完就变白）
- 无虚假或未经证实的医疗/财务建议
- 无诽谤或冒犯性语言
- 如果涉及健康/投资主题，请添加免责声明文本

使用提示模板和用户的内容：

1. **解析内容** 以识别：
   - 标题（h1）
   - 子标题（h2-h6）
   - 段落
   - 列表
   - 代码块
   - 链接
   - 强调/粗体文本
   - 引用块

2. **生成完整的 HTML** 并遵循模板规范：
   - 深色渐变背景
   - 600px × 800px 奶油色卡片
   - 合适的排版，使用 Google Fonts（Noto Serif SC、Inter、JetBrains Mono）
   - 封面图片在顶部
   - 所有指定的文本、链接、列表、代码块等样式
   - 响应式设计，适配移动设备

3. **重要的 HTML 结构**：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Article Title</title>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@700&family=Inter:wght@300;400;700;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        /* 所有 CSS 样式内联 */
    </style>
</head>
<body>
    <div class="container">
        <img src="_attachments/cover-xhs.png" class="cover-image" alt="Cover">
        <div class="content">
            <!-- 文章内容 -->
        </div>
    </div>
</body>
</html>
```

4. **保存 HTML** 到 `~/Dev/obsidian/{account_folder}/articles/<date>-<title>/xhs-preview.html`

### 第六步：捕获截图

生成 HTML 后，以精确的 3:4 比例捕获 `.container` 元素的连续截图：

**截图规格**：
- 容器视口：600px × 800px（3:4 比例）
- 输出分辨率：1200px × 1600px（2 倍设备缩放因子）
- 每个截图精确捕获 `.container` 元素，不包括整个页面

**捕获过程**：

1. **使用 Playwright 浏览器打开 HTML 页面**，视口大于容器
2. **配置浏览器上下文**：
   - 视口：800px × 1000px（大于容器以确保完全可见）
   - 设备缩放因子：2x 以获得高分辨率输出
3. **在容器内滚动**：
   - `.container` 元素具有 `overflow-y: auto`，使其内部可滚动
   - 从 `scrollTop = 0` 开始，通过内容递增
   - 每个滚动位置捕获一个 3:4 比例截图
4. **智能文本边界检测**：
   - 在每个截图之前，分析可见块元素（p、h1-h6、li、blockquote、pre、img）
   - 如果某个元素将在底部边界处被裁剪，则在元素之前结束当前截图
   - 添加空白遮罩以覆盖部分内容，保持干净的 3:4 框架
   - 下一个截图从被裁剪元素顶部开始
5. **捕获完整的 `.container` 内容**：
   - 使用 `container.screenshot()` 仅捕获容器元素（不包括页面背景）
   - 继续直到所有内容被捕获（scrollTop 达到 scrollHeight - clientHeight）
6. **保存截图** 到 `~/Dev/obsidian/{account_folder}/articles/<date>-<title>/_attachments/`：
   - 顺序命名：`xhs-01.png`、`xhs-02.png`、`xhs-03.png` 等

**使用截图脚本**：

```bash
cd {{SKILL_DIR}} && python scripts/screenshot.py ~/Dev/obsidian/{account_folder}/articles/<date>-<title>/xhs-preview.html
```

**脚本输出**：
- 每个截图：精确 1200×1600 像素（3:4 比例，2 倍缩放）
- 仅捕获奶油色卡片内容
- 截图之间无文本被裁剪

### 第七步：报告结果

完成后，向用户报告：
- HTML 文件位置
- 生成的截图数量
- 截图文件夹位置
- 第一个截图的预览（如果可能）

## 目录结构

```
{{SKILL_DIR}}/
├── SKILL.md              # 此文件
├── prompts/
│   └── default.md        # 默认 HTML/CSS 样式提示
│   └── mom-reading-club.md  # 妈妈读书会样式提示
├── scripts/
│   └── screenshot.py     # 截图捕获脚本
└── .gitignore

输出目录（技能文件夹外）：
~/Dev/obsidian/{account_folder}/articles/<date>-<title>/
├── xhs-preview.html          # 样式化 HTML 预览页面
├── imgs/                     # 由 baoyu-cover-image 创建
│   ├── prompts/
│   │   └── cover.md          # 封面图片提示
│   └── cover.png             # 生成的封面（移动到 _attachments/）
└── _attachments/             # Obsidian 风格附件文件夹
    ├── cover-xhs.png         # 封面图片（从 imgs/cover.png 移动）
    ├── xhs-01.png            # 截图页面 1（1200×1600）
    ├── xhs-02.png            # 截图页面 2
    └── ...

账户文件夹映射：
- james-cn → 10_在悉尼和稀泥
- james-en → 11_BuildWithJames
- mom-reading-club → 12_妈妈在读
```

## 依赖项

此技能依赖于：
- `/baoyu-cover-image` 技能用于封面图片生成（必须在 `~/.claude/skills/` 中安装）

## 示例工作流程

**用户**：从以下 Markdown 创建一个样式化的文章页面：

```markdown
# 我的文章标题

这是引言段落...

## 第一部分

第一部分的内容...
```

**助手操作**：
1. 从 `prompts/default.md` 读取提示模板
2. 提取标题："我的文章标题"
3. 确定账户文件夹（未指定 --account，无法从路径推断，使用默认模板 → `10_在悉尼和稀泥`）
4. 创建输出文件夹：`~/Dev/obsidian/10_在悉尼和稀泥/articles/2024-01-14-my-article-title/`
5. 使用 `--no-title` 标志调用 `/baoyu-cover-image` 技能生成封面图片
6. 将生成的封面从 `imgs/cover.png` 移动到 `_attachments/cover-xhs.png`
7. 根据模板规范生成样式化 HTML
8. 保存到 `~/Dev/obsidian/10_在悉尼和稀泥/articles/2024-01-14-my-article-title/xhs-preview.html`
9. 在浏览器中打开并捕获 3:4 比例截图
10. 保存截图到 `~/Dev/obsidian/10_在悉尼和稀泥/articles/2024-01-14-my-article-title/_attachments/xhs-01.png` 等
11. 报告完成，包括文件位置

**带 --account 参数的示例**：

```bash
/xiaohongshu-images ~/path/to/article.md --account mom-reading-club --template mom-reading-club
```

**助手操作**：
1. `--account mom-reading-club` 指定 → 使用 `12_妈妈在读`
2. 输出到：`~/Dev/obsidian/12_妈妈在读/articles/2024-01-14-article-title/`

**带路径推断的示例**：

```bash
/xiaohongshu-images ~/Dev/obsidian/12_妈妈在读/articles/2024-01-14-xxx/index.md
```

**助手操作**：
1. 未指定 --account
2. 输入路径包含 `12_妈妈在读` → 推断账户文件夹
3. 输出到相同文件夹：`~/Dev/obsidian/12_妈妈在读/articles/2024-01-14-xxx/`

## 自定义提示模板

用户可以通过以下方式提供自定义提示模板：
1. 在 `prompts/` 目录中放置一个 `.md` 文件
2. 在调用技能时指定模板名称

示例："使用 `xiaohongshu-style` 模板处理这篇文章"

### 可用模板

| 模板 | 描述 | 适合
|----------|-------------|----------|
| `default` | 标准样式，带有 New Yorker 风格插图 | 一般文章
| `mom-reading-club` | 书法水墨风格，使用 TsangerJinKai02 字体 | 妈妈读书会（妈妈读书会）品牌内容

### 妈妈读书会模板

对所有 "妈妈读书会" 品牌内容使用此模板：

```
/xiaohongshu-images <article> --template mom-reading-club
```

**特点**：
- **字体**：TsangerJinKai02（仓耳今楷02）用于标题 - 需要本地安装
- **封面风格**：中国书法水墨画（书法水墨风）
- **美学**：禅意简约，优雅克制，留白充足
- **色彩点缀**：微妙金色 (#C9A962)
- **目标受众**：30-45 岁有文化的母亲

## 错误处理

如果 `/baoyu-cover-image` 技能失败：
1. 向用户显示错误消息
2. 提供重试或继续不使用封面的选项
3. 如果不使用图像，则使用占位符或省略封面

如果截图捕获失败：
1. 验证 HTML 文件是否存在且有效
2. 检查浏览器依赖项
3. 向用户报告具体错误

## 系统要求

此技能需要：
- Python 3.8+
- Playwright 用于截图捕获（通过 pip 安装：`pip install playwright && playwright install chromium`）
- `/baoyu-cover-image` 技能安装在 `~/.claude/skills/`

安装依赖项：

```bash
pip install playwright
playwright install chromium
```

## 注意事项

- 该技能精确保留所有原始内容，与提供的内容完全一致
- 不进行任何修改、简化或删除内容
- 封面图片根据文章主题生成
- 截图针对小红书的 3:4 比例优化
- 截图中文本永远不会被裁剪 - 边界会智能调整

## 社区合规（社区规范合规）

**重要**：所有生成内容必须符合小红书社区规范。

### 快速参考 - 禁止内容：

| 类别 | 示例 | 操作 |
|----------|----------|--------|
| 绝对声明 | 最好、最佳、第一、国家级 | 删除或重写 |
| 夸张效果 | 一分钟见效、立刻瘦10斤 | 删除或添加免责声明 |
| 医疗/财务建议 | 健康建议、投资建议 | 添加免责声明： "本内容不构成医疗/投资建议" |
| 不当图像 | 裸露、暴力、政治符号 | 重新生成适当内容 |
| 虚假信息 | 假科学、未经证实的声明 | 验证或删除 |
| 诽谤内容 | 攻击品牌/个人 | 完全删除

### 官方指南：

- 社区规范: https://www.xiaohongshu.com/crown/community/rules
- 社区公约: https://www.xiaohongshu.com/crown/community/agreement

### 合规性工作流程：

1. **生成图像前**：检查主题的适当性
2. **生成 HTML 前检查**：扫描文本中的禁止短语
3. **最终输出前**：在提示模板中运行合规性检查清单（第 11.5 节）

## 新手上路（用户不知道该输入什么时，走这里）

**触发**：`/小红书配图 新手`、「这个怎么用」「第一次用」「能干嘛」「带我走一遍」，
以及用户输入了技能名却没有给任何任务的时候。

这个模式的铁律：**不假设、不索取**。用户可能什么都没准备，
不要一上来就问他要文件、要 API key、要具体需求。按下面四步走：

**一、先说清楚这是什么（三句话以内）**

一句话：**把一段内容拆成一组小红书能直接发的 3:4 图片**。
自动分页、排版、生成封面，出来就是能用的图，
不用再去改模板或者调字号。

**二、给编号选项，让他按回车就能继续**

不要问开放式问题（「你想做什么？」对新手是负担）。给 3 个选项加一个默认：

```
想先看哪个？（直接回车 = 1）
  1. 先看看做出来长什么样（示例）
  2. 把我的这段内容做成图
  3. 有哪些风格可以选
```

**三、直接演示一遍，边做边解释**

选完立刻做给他看，用**示例数据**，不需要他提供任何东西。
每做完一步，加一行「💡 刚才发生了什么」，一句话说明这步的意义。

**四、毕业**

演示完只问一个是非题：「要不要用你自己的内容真跑一遍？」
答是就进正常流程；答否就告诉他随时回来输 `/小红书配图 新手`。
