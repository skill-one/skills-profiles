# Markdown 幻灯片技能

## 概述

该技能能够使用 **Marp** 从纯 Markdown 创建演示文稿。使用熟悉的 Markdown 语法编写幻灯片，并使用专业主题导出为 PDF、PPTX 或 HTML。

## 使用方法

1. 编写或提供 Markdown 内容
2. 我会使用正确的指令将其格式化为 Marp
3. 导出为您喜欢的格式（PDF/PPTX/HTML）

**示例提示：**
- "将我的笔记转换为演示文稿"
- "从这篇 markdown 创建幻灯片"
- "使用 markdown 构建演示文稿"
- "根据这个大纲生成 PDF 幻灯片"

## 领域知识

### 基本语法

```markdown
---
marp: true
---

# 第一张幻灯片

内容在此

---

# 第二张幻灯片

- 项目符号 1
- 项目符号 2
```

### 主题

```markdown
---
marp: true
theme: default  # default, gaia, uncover
---
```

### 指令

```markdown
---
marp: true
theme: gaia
class: lead        # 居中标题
paginate: true     # 页码
header: '标题'   # 标题文本
footer: '页脚'   # 页脚文本
backgroundColor: #fff
---
```

### 图片

```markdown
![宽度:500px](image.png)
![背景](background.jpg)
![背景左:40%](sidebar.jpg)
```

### 列

```markdown
<div class="columns">
<div>

## 左

内容

</div>
<div>

## 右

内容

</div>
</div>
```

## 示例

```markdown
---
marp: true
theme: gaia
paginate: true
---

<!-- _class: lead -->

# 项目更新

2024 年第四季度回顾

---

# 突出显示

- 收入：+25%
- 用户：+50%
- NPS：72

---

# 路线图

| Q1 | Q2 | Q3 | Q4 |
|----|----|----|-----|
| MVP | Beta | 发布 | 扩展 |

---

<!-- _class: lead -->

# 感谢！

questions@company.com
```

## 命令行使用

```bash
# 安装
npm install -g @marp-team/marp-cli

# 转换
marp slides.md -o presentation.pdf
marp slides.md -o presentation.pptx
marp slides.md -o presentation.html
```

## 资源

- [Marp 文档](https://marp.app/)
- [GitHub](https://github.com/marp-team/marp)
