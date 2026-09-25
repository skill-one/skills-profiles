# Banner Creator 技能

通过 AI 图像生成，以迭代设计流程创建专业横幅。

## 前置条件

**必需的 API 密钥（设置在环境变量中）：**
- `GEMINI_API_KEY` - 从 [Google AI Studio](https://aistudio.google.com/apikey) 获取

**必需的技能：**
- `nanobanana` - AI 图像生成 (Gemini 3 Pro Image)

## 文件输出位置

所有生成的文件应保存到 `.skill-archive` 目录：

```
.skill-archive/banner-creator/<yyyy-mm-dd-summaryname>/
```

**示例：**
```
.skill-archive/banner-creator/2026-01-19-opc-banner/
  banner-01.png
  banner-02.png
  ...
  banner-03-cropped.png
  preview.html
```

## 工作流程

### 第 1 步：发现与需求

在生成之前，从用户那里收集需求：

**询问关于：**
1. **用途** - 横幅将用于何处？
   - GitHub README
   - Twitter/X 头部
   - LinkedIn 横幅
   - 网站英雄图
   - YouTube 频道艺术图

2. **目标比例/尺寸** - 查看 [references/formats.md](./references/formats.md)：
   - `2:1` (1280x640) - GitHub README
   - `3:1` (1500x500) - Twitter 头部
   - `16:9` (1920x1080) - 网站英雄图

3. **风格偏好**：
   - 匹配现有标志/品牌？
   - 像素艺术 / 8 位复古
   - 极简主义 / 扁平化设计
   - 渐变 / 现代
   - 插画 / 艺术化

4. **内容元素**：
   - 品牌名称 / 项目名称？
   - 标语 / 口号？
   - 要包含的标志角色？

5. **颜色偏好**：
   - 现有品牌颜色？
   - 让 AI 决定？

**在继续之前等待用户确认！**

### 第 2 步：生成横幅变体

使用 `nanobanana` 技能生成 20 个横幅变体：

```bash
# 生成单个横幅
python3 <nanobanana_skill_dir>/scripts/generate.py "{style} 横幅 for {brand}, {description}, {text elements}" \
  --ratio 21:9 -o .skill-archive/banner-creator/<date-name>/banner-01.png

# 批量生成 20 个横幅
python3 <nanobanana_skill_dir>/scripts/batch_generate.py "{style} 横幅 for {brand}, {description}, {text elements}" \
  -n 20 --ratio 21:9 -d .skill-archive/banner-creator/<date-name> -p banner
```

**指南：**
- 在 `21:9` 比例（最宽可用）生成，稍后裁剪为目标比例
- 使用 batch_generate.py 生成多个变体（包括自动延迟）
- 使用顺序命名：`banner-01.png`，`banner-02.png`，等

**图像编辑（用于合并现有标志）：**
```bash
python3 <nanobanana_skill_dir>/scripts/generate.py "在横幅左侧添加 {logo character}" \
  -i /path/to/existing-logo.png --ratio 21:9 -o banner-with-logo.png
```

### 第 3 步：创建 HTML 预览

复制预览模板并在浏览器中打开：

```bash
cp <skill_dir>/templates/preview.html .skill-archive/banner-creator/<yyyy-mm-dd-summaryname>/preview.html
```

然后在默认浏览器中打开：

```bash
open .skill-archive/banner-creator/<yyyy-mm-dd-summaryname>/preview.html
```

**重要提示：** 更新 HTML 以包含生成的横幅的正确数量。

### 第 4 步：与用户迭代

询问用户他们更喜欢哪些横幅：
- "你喜欢哪些横幅？(例如，#3, #7, #15)"
- "你喜欢它们的哪些方面？"
- "有什么你想修改的？"

根据反馈：
1. 为喜欢的风格生成 10-20 个更多变体
2. 使用命名：`banner-{original}-v{n}.png` (例如，`banner-03-v1.png`)
3. 更新 HTML 预览
4. 重复直到用户选择最终横幅

### 第 5 步：裁剪为目标比例

一旦用户批准一个横幅，裁剪为目标尺寸：

```bash
python3 <skill_dir>/scripts/crop_banner.py {input.png} {output.png} --ratio 2:1 --width 1280
```

**常见目标：**
- GitHub README: `--ratio 2:1 --width 1280` → 1280x640
- Twitter 头部: `--ratio 3:1 --width 1500` → 1500x500
- 网站英雄图: `--ratio 16:9 --width 1920` → 1920x1080

### 第 6 步：交付最终资源

展示最终交付物：

```
## 最终横幅资源

| 文件 | 描述 | 尺寸 |
|------|------|------|
| banner-03.png | 原始 (21:9) | 2016x864 |
| banner-03-cropped.png | GitHub README (2:1) | 1280x640 |

所有文件保存到：`.skill-archive/banner-creator/<yyyy-mm-dd-summaryname>/`
将最终横幅复制到用户期望的位置。
```

## 快速参考

### 常见提示模式

**带文本：**
```
Wide banner for {brand}, {style} style, featuring "{text}" prominently displayed, {colors}, {scene/elements}
```

**带角色：**
```
Wide banner featuring {character description}, {style} style, {scene}, text "{brand name}" on {position}, {colors}
```

**抽象/渐变：**
```
Abstract {style} banner, {colors} gradient, geometric patterns, modern tech feel, text "{brand}" centered
```

**基于场景：**
```
{Style} illustration banner, {scene description}, {character} in {action}, "{brand}" text overlay, {colors}
```

### 支持的宽高比

生成最宽比例，然后裁剪：
- `21:9` - 超宽（推荐用于生成）
- `16:9` - 宽
- `3:2` - 标准宽

## 参考文献

- [references/formats.md](./references/formats.md) - 各平台常见横幅尺寸
- [examples/opc-banner-creation.md](./examples/opc-banner-creation.md) - 完整示例对话
