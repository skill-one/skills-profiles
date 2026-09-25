# Marp 幻灯片创建器

使用 7 种预设主题和内置最佳实践，创建专业且视觉吸引力强的 Marp 演示文稿幻灯片。

## 何时使用此技能

当用户：
- 请求创建演示文稿幻灯片或 Marp 文档
- 要求“让幻灯片看起来更好”或“改进幻灯片设计”
- 提供模糊的指令，如“做得好一点”（make it nice）或“酷一点”（make it cool）
- 想要创建讲座或研讨会材料
- 需要要点为主的幻灯片，偶尔插入图片

## 快速入门

### 第 1 步：选择主题

首先，根据用户请求和内容确定合适的主题。

**快速主题选择：**
- **技术/开发者内容** → tech 主题
- **商业/企业** → business 主题
- **创意/活动** → 多彩或渐变主题
- **学术/简单** → 极简主题
- **一般/不确定** → 默认主题
- **偏好暗色背景** → dark 或 tech 主题

有关详细主题选择指南，请阅读 `references/theme-selection.md`。

### 第 2 步：创建幻灯片

1. **先阅读相关参考文档**：
   - 始终从阅读 `references/marp-syntax.md` 开始，了解基本语法
   - 对于图片：`references/image-patterns.md`（官方 Marpit 图片语法）
   - 对于高级功能（数学、表情符号）：`references/advanced-features.md`
   - 对于自定义主题：`references/theme-css-guide.md`

2. 从适当的模板文件中复制内容：
   - `assets/template-basic.md` - 默认主题（最常见）
   - `assets/template-minimal.md` - 极简主题
   - `assets/template-colorful.md` - 多彩主题
   - `assets/template-dark.md` - 暗色模式主题
   - `assets/template-gradient.md` - 渐变主题
   - `assets/template-tech.md` - tech/代码主题
   - `assets/template-business.md` - 商业主题

3. 阅读 `references/best-practices.md` 了解质量指南

4. 按照最佳实践组织内容：
   - 标题幻灯片使用 `<!-- _class: lead -->`
   - 简洁的 h2 标题（5-7 个日文字符）
   - 每张幻灯片 3-5 个要点
   - 足够的空白

5. 如有需要，使用 `references/image-patterns.md` 中的模式添加图片

6. 保存到 `/mnt/user-data/outputs/`，使用 `.md` 扩展名

## 可用主题

### 1. 默认主题
**颜色**：米色背景，海军蓝文字，蓝色标题
**风格**：简洁、精致，带装饰线条
**用途**：一般研讨会、讲座、演示文稿
**模板**：`template-basic.md`

### 2. 极简主题
**颜色**：白色背景，灰色文字，黑色标题
**风格**：极简装饰，宽边距，轻量字体
**用途**：内容导向的演示文稿，学术演讲
**模板**：`template-minimal.md`

### 3. 多彩和流行主题
**颜色**：粉色渐变背景，多彩强调色
**风格**：鲜艳的渐变，粗体字体，彩虹强调色
**用途**：面向年轻人的活动，创意项目
**模板**：`template-colorful.md`

### 4. 暗色模式主题
**颜色**：黑色背景，青色/紫色强调色
**风格**：暗色主题带发光效果，护眼
**用途**：技术演示文稿，晚间演讲，现代风格
**模板**：`template-dark.md`

### 5. 渐变背景主题
**颜色**：紫色/粉色/蓝色/绿色渐变（每张幻灯片不同）
**风格**：每张幻灯片不同渐变，白色文字，阴影
**用途**：视觉导向，创意演示文稿
**模板**：`template-gradient.md`

### 6. tech/代码主题
**颜色**：GitHub 风格暗色背景，蓝色/绿色强调色
**风格**：代码字体，Markdown 风格标题带 # 符号
**用途**：编程教程，技术会议，开发者内容
**模板**：`template-tech.md`

### 7. 商业主题
**颜色**：白色背景，海军蓝标题，蓝色强调色
**风格**：企业演示文稿风格，顶部边框，表格支持
**用途**：商业演示文稿，提案，报告
**模板**：`template-business.md`

## 创建幻灯片流程

### 基本工作流程

1. **理解需求**
   - 确定内容：标题、主题、要点
   - 确定目标受众
   - 评估正式程度

2. **选择主题**
   - 使用上述快速选择规则
   - 不确定时，参考 `references/theme-selection.md`
   - 仍然不确定时，默认使用默认主题

3. **应用模板**
   - 从 `assets/` 加载适当的模板
   - CSS 已嵌入，无需外部文件
   - 保持模板结构

4. **组织内容**
   - 标题幻灯片：`<!-- _class: lead -->` + h1
   - 内容幻灯片：h2 标题 + 要点
   - 标题保持在 5-7 个日文字符
   - 每张幻灯片 3-5 个要点

5. **优化质量**
   - 阅读 `references/best-practices.md`
   - 确保有足够的空白
   - 保持一致性
   - 文字简洁（每行 15-25 个字符）

6. **添加图片**
   - 如有必要，参考 `references/image-patterns.md`
   - 常见：`![bg right:40%](image.png)` 用于侧边图片
   - 使用正确的 Marp 图片语法

7. **输出文件**
   - 保存到 `/mnt/user-data/outputs/`
   - 使用描述性文件名，如 `presentation.md`

## 处理“让它看起来更好”的请求

当用户给出模糊的指令，如“做得好一点”（make it nice）、“酷一点”（make it cool）或“make it cool”时：

1. **根据内容推断主题**：
   - 商业内容 → business 主题
   - 技术内容 → tech 或 dark 主题
   - 创意内容 → gradient 或 colorful 主题
   - 一般 → default 主题

2. **自动应用最佳实践**：
   - 将标题缩短为 5-7 个字符
   - 限制要点为 3-5 项
   - 添加足够的空白
   - 使用一致的结构

3. **增强视觉层次结构**：
   - 适当使用 h3 分节
   - 将密集文本拆分为多张幻灯片
   - 确保逻辑流程（引言 → 正文 → 结论）

4. **保持专业风格**：
   - 根据内容匹配正式程度
   - 列表使用平行结构
   - 保持技术术语一致

## 图片集成

对于带图片的幻灯片，参考 `references/image-patterns.md` 了解详细语法。

常见模式：
- **侧边图片**：`![bg right:40%](image.png)` - 图片在右侧，文字在左侧
- **居中**：`![w:600px](image.png)` - 居中并指定宽度
- **全屏背景**：`![bg](image.png)` - 全屏背景
- **多张图片**：多个 `![bg]` 声明

示例讲座模式：
```markdown
## 幻灯片标题

![bg right:40%](diagram.png)

- 解释要点 1
- 解释要点 2
- 解释要点 3
```

## 文件输出

始终将最终的 Marp 文件保存到 `/mnt/user-data/outputs/`，使用 `.md` 扩展名：
- `presentation.md`
- `seminar-slides.md`
- `lecture-materials.md`

## 质量检查清单

交付幻灯片前，请验证：
- [ ] 主题根据内容选择合适
- [ ] CSS 主题已嵌入文件
- [ ] 标题幻灯片使用 `<!-- _class: lead -->`
- [ ] 所有 h2 标题简洁（5-7 字符）
- [ ] 每张幻灯片要点 3-5 项
- [ ] 图片使用正确的 Marp 语法
- [ ] 文件保存到输出目录
- [ ] 内容遵循最佳实践

## 参考

### 核心文档
- **Marp 语法**：`references/marp-syntax.md` - 基本 Marp/Marpit 语法（指令、frontmatter、分页等）
- **图片模式**：`references/image-patterns.md` - 官方图片语法（bg、滤镜、分割背景）
- **主题 CSS 指南**：`references/theme-css-guide.md` - 如何基于 Marpit 规范创建自定义主题
- **高级功能**：`references/advanced-features.md` - 数学、表情符号、碎片化列表、Marp CLI、VS Code
- **官方主题**：`references/official-themes.md` - default、gaia、uncover 主题文档

### 质量与选择指南
- **主题选择**：`references/theme-selection.md` - 如何为内容选择合适的主题
- **最佳实践**：`references/best-practices.md` - “酷”幻灯片的质量指南

### 模板与资源
- **模板**：`assets/template-*.md` - 每个主题嵌入 CSS 的起点（7 个主题）
- **独立 CSS**：`assets/theme-*.css` - 参考 CSS 文件（模板中已嵌入）

### 官方外部链接
- **Marp 官方网站**：https://marp.app/
- **Marpit 指令**：https://marpit.marp.app/directives
- **Marpit 图片语法**：https://marpit.marp.app/image-syntax
- **Marpit 主题 CSS**：https://marpit.marp.app/theme-css
- **Marp 核心GitHub**：https://github.com/marp-team/marp-core
- **Marp CLI GitHub**：https://github.com/marp-team/marp-cli
