# Logo Creator 技能

通过 AI 图像生成，使用迭代设计流程创建专业 Logo。

## 前置条件

**必需的 API 密钥（设置在环境变量中）：**
- `GEMINI_API_KEY` - 从 [Google AI Studio](https://aistudio.google.com/apikey) 获取
- `REMOVE_BG_API_KEY` - 从 [remove.bg](https://www.remove.bg/api) 获取
- `RECRAFT_API_KEY` - 从 [recraft.ai](https://www.recraft.ai/) 获取

**必需的技能：**
- `nanobanana` - AI 图像生成 (Gemini 3 Pro 图像)

## 文件输出位置

所有生成的文件应保存到 `.skill-archive` 目录：

```
.skill-archive/logo-creator/<yyyy-mm-dd-summaryname>/
```

**示例：**
```
.skill-archive/logo-creator/2026-01-18-opc-logo/
  logo-01.png
  logo-02.png
  ...
  logo-09-cropped.png
  logo-09-nobg.png
  logo-09.svg
  preview.html
```

**指南：**
- 使用 `yyyy-mm-dd` 格式的当前日期
- 添加简短的摘要名称（项目/品牌名称，使用连字符命名法）
- 在生成第一个 Logo 前创建目录
- 将所有变体和迭代保存在同一文件夹中
- 最终批准的 Logo 应复制到用户期望的位置

## 工作流程

### 第 1 步：发现与需求收集

在生成之前，从用户收集需求：

**询问关于：**
1. **项目/品牌名称** - Logo 是为谁创建的？
2. **风格偏好** - 参考 [references/styles.md](./references/styles.md) 获取选项：
   - 像素艺术 / 8 位复古
   - 极简主义 / 扁平化设计
   - 3D / 等距投影
   - 手绘 / 素描
   - 吉祥物 / 角色
   - 字母标 / 字母图
   - 抽象 / 几何图形

3. **宽高比** - 默认为 1:1（方形），选项：
   - `1:1` - 方形（网站图标、应用图标）
   - `16:9` - 宽屏（页眉、横幅）
   - `4:3` - 标准
   - `2:3` - 竖屏

4. **颜色偏好**：
   - 单色（黑白）
   - 特定品牌颜色
   - 让 AI 决定

5. **参考图像** - 任何现有的 Logo 或风格供参考？

**在继续之前等待用户确认！**

### 第 2 步：生成 Logo 变体

使用 `nanobanana` 技能生成 20 个 Logo 变体（默认）：

```bash
# 生成单个 Logo
python3 <nanobanana_skill_dir>/scripts/generate.py "{style} logo for {brand}, {description}, {colors}" \
  --ratio 1:1 -o .skill-archive/logo-creator/<date-name>/logo-01.png

# 批量生成 20 个 Logo
python3 <nanobanana_skill_dir>/scripts/batch_generate.py "{style} logo for {brand}, {description}, {colors}" \
  -n 20 --ratio 1:1 -d .skill-archive/logo-creator/<date-name> -p logo
```

**指南：**
- 使用 batch_generate.py 生成多个变体（包含自动延迟）
- 保存到 `.skill-archive/logo-creator/<yyyy-mm-dd-summaryname>/` 目录
- 使用顺序命名：`logo-01.png`，`logo-02.png`，等

**提示：**
- 包含风格关键词："像素艺术"，"极简主义"，"8 位"，"扁平化设计"
- 指定颜色："黑色背景"，"单色"，"蓝色渐变"
- 添加上下文："科技初创公司"，"食品品牌"，"游戏公司"
- 请求格式："图标"，"徽章"，"吉祥物"，"字母标"

### 第 3 步：创建 HTML 预览

复制预览模板并在浏览器中打开：

```bash
cp <skill_dir>/templates/preview.html .skill-archive/logo-creator/<yyyy-mm-dd-summaryname>/preview.html
```

然后在默认浏览器中打开：

```bash
open .skill-archive/logo-creator/<yyyy-mm-dd-summaryname>/preview.html
```

**重要提示：** 更新 HTML 以包含生成的 Logo 正确数量。

### 第 4 步：与用户迭代

询问用户他们喜欢的 Logo：
- "哪些 Logo 你喜欢？(例如，#5，#12，#18)"
- "你喜欢它们的哪些方面？"
- "有什么修改意见？"

根据反馈：
1. 为喜欢的风格生成 10-20 个更多变体
2. 使用命名：`logo-{original}-v{n}.png`（例如，`logo-05-v1.png`）
3. 更新 HTML 预览
4. 重复直到用户选择最终 Logo

### 第 5 步：最终确定 Logo

一旦用户批准 Logo，处理它：

**5a. 裁剪空白（调整为 1:1 且无边距）：**
```bash
python3 <skill_dir>/scripts/crop_logo.py {input.png} {output-cropped.png}
```

**5b. 移除背景：**
```bash
python3 <skill_dir>/scripts/remove_bg.py {input.png} {output-nobg.png}
```

**5c. 转换为 SVG：**
```bash
python3 <skill_dir>/scripts/vectorize.py {input.png} {output.svg}
```

### 第 6 步：交付最终资源

展示最终交付物：

```
## 最终 Logo 资源

| 文件 | 描述 | 大小 |
|------|------|------|
| logo.png | 原始文件 | 1024x1024 |
| logo-cropped.png | 无边距，1:1 | ~800x800 |
| logo-nobg.png | 透明背景 | ~800x800 |
| logo.svg | 矢量（可缩放） | ~20KB |

所有文件保存到：`.skill-archive/logo-creator/<yyyy-mm-dd-summaryname>/`
将最终 Logo 复制到用户期望的位置。
```

## 快速参考

### 常用提示模式

**像素艺术：**
```
Pixel art {subject} logo, 8-bit retro style, black pixels on white background, {size}x{size} grid, minimalist icon
```

**极简主义：**
```
Minimalist {subject} logo, flat design, clean lines, {color} on white, simple geometric shapes
```

**吉祥物：**
```
Cute {animal/character} mascot logo, friendly expression, {style} style, {colors}, suitable for brand icon
```

**字母标：**
```
Letter "{letter}" logo, modern typography, {style} design, {colors}, clean professional look
```

### 支持的宽高比

- `1:1` - 方形（Logo 默认）
- `2:3`，`3:2` - 竖屏/横屏
- `3:4`，`4:3` - 标准
- `4:5`，`5:4` - 照片
- `9:16`，`16:9` - 宽屏
- `21:9` - 超宽屏

## 参考

- [references/styles.md](./references/styles.md) - Logo 风格指南及提示示例
- [examples/opc-logo-creation.md](./examples/opc-logo-creation.md) - 完整示例对话
