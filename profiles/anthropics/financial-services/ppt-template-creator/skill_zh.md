# PPT 模板创建器

**此技能创建的是技能（SKILLS），而不是演示文稿。** 当用户希望将他们的 PowerPoint 模板转换为可重复使用的技能，以便以后生成演示文稿时，请使用此技能。如果用户只是想创建演示文稿，请使用 `pptx` 技能。

生成的技能包括：
- `assets/template.pptx` - 模板文件
- `SKILL.md` - 完整说明（无需引用此元技能）

**有关一般技能构建的最佳实践**，请参考 `skill-creator` 技能。此技能专注于 PPT 特定模式。

## 工作流程

1. **用户提供模板** (.pptx 或 .potx)
2. **分析模板** - 提取布局、占位符、尺寸
3. **初始化技能** - 使用 `skill-creator` 技能来设置技能结构
4. **添加模板** - 将 .pptx 复制到 `assets/template.pptx`
5. **编写 SKILL.md** - 按照以下模板填写 PPT 特定细节
6. **创建示例** - 生成示例演示文稿以进行验证
7. **打包** - 使用 `skill-creator` 技能打包为 .skill 文件

## 第 2 步：分析模板

**关键：精确提取占位符位置** - 这决定了内容区域边界。

```python
from pptx import Presentation

prs = Presentation(template_path)
print(f"尺寸: {prs.slide_width/914400:.2f}\" x {prs.slide_height/914400:.2f}\"")
print(f"布局: {len(prs.slide_layouts)}")

for idx, layout in enumerate(prs.slide_layouts):
    print(f"\n[{idx}] {layout.name}:")
    for ph in layout.placeholders:
        try:
            ph_idx = ph.placeholder_format.idx
            ph_type = ph.placeholder_format.type
            # 重要：提取精确位置（英寸）
            left = ph.left / 914400
            top = ph.top / 914400
            width = ph.width / 914400
            height = ph.height / 914400
            print(f"    idx={ph_idx}, type={ph_type}")
            print(f"        x={left:.2f}\", y={top:.2f}\", w={width:.2f}\", h={height:.2f}\"")
        except:
            pass
```

**需要记录的关键测量值：**
- **标题位置**：标题占位符位于何处？
- **副标题/描述**：副标题行位于何处？
- **页脚占位符**：页脚/来源出现在何处？
- **内容区域**：副标题和页脚之间的空间是您的内容区域

### 查找真实内容起始位置

**关键：** 内容区域并不总是立即位于副标题占位符之后。许多模板在副标题和内容区域之间有一个视觉边框、线条或保留空间。

**最佳方法：** 查看布局 2 或类似的“内容”布局，这些布局包含 OBJECT 占位符 - 此占位符的 `y` 位置指示内容实际应开始的地点。

```python
# 查找 OBJECT 占位符以确定真实内容起始位置
for idx, layout in enumerate(prs.slide_layouts):
    for ph in layout.placeholders:
        try:
            if ph.placeholder_format.type == 7:  # OBJECT 类型
                top = ph.top / 914400
                print(f"布局 [{idx}] {layout.name}: OBJECT 从 y={top:.2f}\" 开始")
                # 这个 y 值是您内容应开始的地点！
        except:
            pass
```

**示例：** 一个模板可能有：
- 副标题结束于 y=1.38"
- 但 OBJECT 占位符从 y=1.90" 开始
- 间隙（0.52") 是保留给边框/线条的 - **不要在那里放置内容**

使用 OBJECT 占位符的 `y` 位置作为内容起始位置，而不是副标题的结束位置。

## 第 5 步：编写 SKILL.md

生成的技能应具有以下结构：
```
[公司]-ppt-template/
├── SKILL.md
└── assets/
    └── template.pptx
```

### 生成的 SKILL.md 模板

生成的 SKILL.md 必须是 **自包含的**，所有说明嵌入其中。使用以下模板，并填写从您的分析中获取的括号内的值：

````markdown
---
name: [公司]-ppt-template
description: [公司] PowerPoint 模板，用于创建演示文稿。在创建 [公司] 品牌的演示文稿、董事会材料或客户演示文稿时使用。
---

# [公司] PPT 模板

模板: `assets/template.pptx` ([宽度]" x [高度]", [N] 个布局)

## 创建演示文稿

```python
from pptx import Presentation

prs = Presentation("path/to/skill/assets/template.pptx")

# 首先删除所有现有幻灯片
while len(prs.slides) > 0:
    rId = prs.slides._sldIdLst[0].rId
    prs.part.drop_rel(rId)
    del prs.slides._sldIdLst[0]

# 从布局添加幻灯片
slide = prs.slides.add_slide(prs.slide_layouts[LAYOUT_IDX])
```

## 关键布局

| 索引 | 名称 | 用于 |
|------|------|------|
| [0] | [布局名称] | [封面/标题幻灯片] |
| [N] | [布局名称] | [带项目符号的内容] |
| [N] | [布局名称] | [两列布局] |

## 占位符映射

**关键：** 为每个占位符包含精确位置（x, y 坐标）。

### 布局 [N]: [名称]
| 索引 | 类型 | 位置 | 用于 |
|------|------|------|------|
| [索引] | 标题 (1) | y=[Y]" | 幻灯片标题 |
| [索引] | 正文 (2) | y=[Y]" | 副标题/描述 |
| [索引] | 正文 (2) | y=[Y]" | 页脚 |
| [索引] | 正文 (2) | y=[Y]" | 来源/注释 |

### 内容区域边界

**记录自定义形状/表格/图表的安全内容区域：**

```
内容区域（布局 [N]）：
- 左边距: [X]"（内容从此处开始）
- 顶部: [Y]"（位于副标题占位符下方）
- 宽度: [W]"
- 高度: [H]"（在页脚之前结束）

对于四象限布局：
- 左列: x=[X]", 宽度=[W]"
- 右列: x=[X]", 宽度=[W]"
- 顶行: y=[Y]", 高度=[H]"
- 底行: y=[Y]", 高度=[H]"
```

**为什么这很重要：** 自定义内容（文本框、表格、图表）必须保持在这些边界内，以避免与标题、页脚和来源行等模板占位符重叠。

## 填充内容

**不要添加手动项目符号字符** - 幻灯片母版处理格式。

```python
# 填充标题
for shape in slide.shapes:
    if hasattr(shape, 'placeholder_format'):
        if shape.placeholder_format.type == 1:  # 标题
            shape.text = "幻灯片标题"

# 填充内容，按层次结构（级别 0 = 标题，级别 1 = 项目符号）
for shape in slide.shapes:
    if hasattr(shape, 'placeholder_format'):
        idx = shape.placeholder_format.idx
        if idx == [CONTENT_IDX]:
            tf = shape.text_frame
            for para in tf.paragraphs:
                para.clear()

            content = [
                ("章节标题", 0),
                ("第一项", 1),
                ("第二项", 1),
            ]

            tf.paragraphs[0].text = content[0][0]
            tf.paragraphs[0].level = content[0][1]
            for text, level in content[1:]:
                p = tf.add_paragraph()
                p.text = text
                p.level = level
```

## 示例：封面幻灯片

```python
slide = prs.slides.add_slide(prs.slide_layouts[[COVER_IDX]])
for shape in slide.shapes:
    if hasattr(shape, 'placeholder_format'):
        idx = shape.placeholder_format.idx
        if idx == [TITLE_IDX]:
            shape.text = "公司名称"
        elif idx == [SUBTITLE_IDX]:
            shape.text = "演示文稿标题 | 日期"
```

## 示例：内容幻灯片

```python
slide = prs.slides.add_slide(prs.slide_layouts[[CONTENT_IDX]])
for shape in slide.shapes:
    if hasattr(shape, 'placeholder_format'):
        ph_type = shape.placeholder_format.type
        idx = shape.placeholder_format.idx
        if ph_type == 1:
            shape.text = "执行摘要"
        elif idx == [BODY_IDX]:
            tf = shape.text_frame
            for para in tf.paragraphs:
                para.clear()
            content = [
                ("关键发现", 0),
                ("年收入同比增长 40% 达到 5000 万美元", 1),
                ("扩展到 3 个新市场", 1),
                ("建议", 0),
                ("继续战略性计划", 1),
            ]
            tf.paragraphs[0].text = content[0][0]
            tf.paragraphs[0].level = content[0][1]
            for text, level in content[1:]:
                p = tf.add_paragraph()
                p.text = text
                p.level = level
```
````

## 第 6 步：创建示例输出

生成一个示例演示文稿以验证技能是否正常工作。将其与技能一起保存以供参考。

## PPT 特定生成的技能规则

1. **assets/** 中的模板** - 始终捆绑 .pptx 文件
2. **自包含的 SKILL.md** - 所有说明嵌入其中，无外部引用
3. **不要手动添加项目符号** - 使用 `paragraph.level` 设置层次结构
4. **先删除幻灯片** - 添加新幻灯片前始终清除现有幻灯片
5. **按索引记录占位符** - 占位符索引值是模板特定的
