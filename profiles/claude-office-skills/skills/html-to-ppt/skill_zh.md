# HTML/Markdown到PowerPoint技能

## 概述

该技能能够使用**Marp**（Markdown演示文稿生态系统）将Markdown或HTML转换为专业的PowerPoint演示文稿。使用简单的Markdown语法和基于CSS的主题，创建美观、一致的幻灯片。

## 如何使用

1. 提供结构化的用于幻灯片的Markdown内容
2. 可选地指定主题或自定义样式
3. 我将将其转换为PowerPoint、PDF或HTML幻灯片

**示例提示：**
- "将此Markdown转换为PowerPoint演示文稿"
- "使用Marp根据此提纲创建幻灯片"
- "将我的笔记转换为使用gaia主题的演示文稿"
- "从此Markdown生成PDF幻灯片集"

## 领域知识

### Marp基础

Marp使用简单的语法，其中`---`分隔幻灯片：

```markdown
---
marp: true
theme: default
---

# 幻灯片1标题

第一张幻灯片的内容

---

# 幻灯片2标题

第二张幻灯片的内容
```

### 命令行使用

```bash
# 转换为PowerPoint
marp slides.md -o presentation.pptx

# 转换为PDF
marp slides.md -o presentation.pdf

# 转换为HTML
marp slides.md -o presentation.html

# 使用特定主题
marp slides.md --theme gaia -o presentation.pptx
```

### 幻灯片结构

#### 基本幻灯片
```markdown
---
marp: true
---

# 标题

- 项目符号点1
- 项目符号点2
- 项目符号点3
```

#### 标题幻灯片
```markdown
---
marp: true
theme: gaia
class: lead
---

# 演示文稿标题

## 副标题

作者姓名
日期
```

### Frontmatter选项

```yaml
---
marp: true
theme: default          # default, gaia, uncover
size: 16:9              # 4:3, 16:9, 或自定义
paginate: true          # 显示页码
header: '公司名称'      # 头部文本
footer: '机密'          # 尾部文本
backgroundColor: #fff
backgroundImage: url('bg.png')
---
```

### 主题

#### 内置主题
```markdown
---
marp: true
theme: default   # 干净、极简
---

---
marp: true
theme: gaia      # 多彩、现代
---

---
marp: true
theme: uncover   # 鲜明、以演示为重点
---
```

#### 主题类
```markdown
---
marp: true
theme: gaia
class: lead     # 居中标题幻灯片
---

---
marp: true
theme: gaia
class: invert   # 颜色反转
---
```

### 格式化

#### 文本样式
```markdown
# 标题1
## 标题2

**粗体文本**和*斜体文本*

`内联代码`

> 引用块用于强调
```

#### 列表
```markdown
- 无序列表项
- 另一个项目
  - 嵌套项目

1. 有序列表项
2. 第二个项目
   1. 嵌套编号
```

#### 代码块
```markdown
# 代码示例

\`\`\`python
def hello():
    print("Hello, World!")
\`\`\`
```

#### 表格
```markdown
| 功能 | 状态 |
|------|------|
| 表格  | ✅   |
| 图表  | ✅   |
| 图片  | ✅   |
```

### 图片

#### 基本图片
```markdown
![](image.png)
```

#### 尺寸图片
```markdown
![width:500px](image.png)
![height:300px](image.png)
![width:80%](image.png)
```

#### 背景图片
```markdown
---
marp: true
backgroundImage: url('background.jpg')
---

# 带背景的幻灯片
```

### 高级布局

#### 两列布局
```markdown
---
marp: true
style: |
  .columns {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
---

# 两列布局

<div class="columns">
<div>

## 左侧列
- 点1
- 点2

</div>
<div>

## 右侧列
- 点A
- 点B

</div>
</div>
```

#### 分割背景
```markdown
---
marp: true
theme: gaia
class: gaia
---

<!-- 
_backgroundImage: linear-gradient(to right, #4a90a4, #4a90a4 50%, white 50%)
-->

<div class="columns">
<div style="color: white;">

# 暗面

</div>
<div>

# 亮面

</div>
</div>
```

### 指令

#### 本地指令（每张幻灯片）
```markdown
---
marp: true
---

<!-- 
_backgroundColor: #123
_color: white
_paginate: false
-->

# 特殊幻灯片
```

#### 范围样式
```markdown
---
marp: true
---

<style scoped>
h1 {
  color: red;
}
</style>

# 这个标题是红色的
```

### Python集成

```python
import subprocess
import tempfile
import os

def markdown_to_pptx(md_content, output_path, theme='default'):
    """使用Marp将Markdown转换为PowerPoint。"""
    
    # 如果没有marp指令，则添加
    if '---\nmarp: true' not in md_content:
        md_content = f"---\nmarp: true\ntheme: {theme}\n---\n\n" + md_content
    
    # 写入临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(md_content)
        temp_path = f.name
    
    try:
        # 使用marp转换
        subprocess.run([
            'marp', temp_path, '-o', output_path
        ], check=True)
        
        return output_path
    finally:
        os.unlink(temp_path)

# 使用示例
md = """
# 欢迎

介绍性幻灯片

---

# 议程

- 主题1
- 主题2
- 主题3
"""

markdown_to_pptx(md, 'presentation.pptx')
```

### Node.js/marp-cli API

```javascript
const { marpCli } = require('@marp-team/marp-cli');

// 转换文件
marpCli(['slides.md', '-o', 'output.pptx']).then(exitCode => {
    console.log('完成:', exitCode);
});
```

## 最佳实践

1. **每张幻灯片一个观点**：保持幻灯片专注
2. **使用视觉层次结构**：一致的标题级别
3. **限制文本**：每张幻灯片最多6个项目符号
4. **包含图片**：视觉内容增强记忆
5. **测试输出**：导出前预览

## 常见模式

### 演示文稿生成器
```python
def create_presentation(title, sections, output_path, theme='gaia'):
    """根据结构化数据生成演示文稿。"""
    
    md_content = f"""---
marp: true
theme: {theme}
paginate: true
---

<!-- _class: lead -->

# {title}

{sections.get('subtitle', '')}

{sections.get('author', '')}

"""
    
    for section in sections.get('slides', []):
        md_content += f"""---

# {section['title']}

"""
        for point in section.get('points', []):
            md_content += f"- {point}\n"
        
        if section.get('notes'):
            md_content += f"\n<!-- Notes: {section['notes']} -->\n"
    
    md_content += """---

<!-- _class: lead -->

# 感谢！

提问？
"""
    
    return markdown_to_pptx(md_content, output_path, theme)
```

### 批量幻灯片生成
```python
def generate_report_slides(data_list, template, output_dir):
    """根据数据生成多个演示文稿。"""
    import os
    
    for data in data_list:
        content = template.format(**data)
        output_path = os.path.join(output_dir, f"{data['name']}_report.pptx")
        markdown_to_pptx(content, output_path)
```

## 示例

### 示例1：技术演示
```markdown
---
marp: true
theme: gaia
class: lead
paginate: true
---

# API文档

## REST API最佳实践

工程团队
2024年1月

---

# 议程

1. 身份验证
2. 端点概述
3. 错误处理
4. 速率限制
5. 示例

---

# 身份验证

所有请求都需要API密钥：

```http
Authorization: Bearer YOUR_API_KEY
```

- 密钥90天后过期
- 安全存储，不要提交到git
- 定期轮换

---

# 端点概述

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | /users | 列出所有用户 |
| POST | /users | 创建用户 |
| GET | /users/:id | 获取用户详情 |
| PUT | /users/:id | 更新用户 |
| DELETE | /users/:id | 删除用户 |

---

# 错误处理

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "无效的电子邮件格式",
    "details": ["电子邮件必须有效"]
  }
}
```

---

<!-- _class: lead -->

# 提问？

api-support@company.com
```

### 示例2：商业提案
```python
def create_pitch_deck(company_data):
    """生成投资者提案演示文稿。"""
    
    md = f"""---
marp: true
theme: uncover
paginate: true
---

<!-- _class: lead -->
<!-- _backgroundColor: #2d3748 -->
<!-- _color: white -->

# {company_data['name']}

{company_data['tagline']}

---

# 问题

{company_data['problem_statement']}

**市场痛点：**
"""
    
    for pain in company_data['pain_points']:
        md += f"- {pain}\n"
    
    md += f"""
---

# 我们的解决方案

{company_data['solution']}

![width:600px]({company_data.get('product_image', 'product.png')})

---

# 市场机会

- **TAM：** {company_data['tam']}
- **SAM：** {company_data['sam']}
- **SOM：** {company_data['som']}

---

# 成长

| 指标 | 值 |
|------|------|
| 月收入 | {company_data['mrr']} |
| 客户数 | {company_data['customers']} |
| 增长率 | {company_data['growth']} |

---

# 我们的需求

**寻求：** {company_data['funding_ask']}

**资金用途：**
- 产品开发：40%
- 销售和市场：35%
- 运营：25%

---

<!-- _class: lead -->

# 一起构建未来

{company_data['contact']}
"""
    
    return md

# 生成演示文稿
pitch_data = {
    'name': 'TechStartup Inc',
    'tagline': 'AI驱动的文档处理',
    'problem_statement': '企业浪费20%的时间在手动文档工作上',
    'pain_points': ['手动数据输入', '易出错的流程', '处理时间慢'],
    'solution': '自动化文档处理，准确率99.5%',
    'tam': '$50B',
    'sam': '$10B',
    'som': '$500M',
    'mrr': '$100K',
    'customers': '50',
    'growth': '20% MoM',
    'funding_ask': '$5M A轮',
    'contact': 'founders@techstartup.com'
}

md_content = create_pitch_deck(pitch_data)
markdown_to_pptx(md_content, 'pitch_deck.pptx', theme='uncover')
```

## 限制

- 不支持复杂的动画
- 部分PowerPoint特定功能不可用
- 自定义字体需要CSS配置
- 视频嵌入有限
- 演讲者笔记基本支持

## 安装

```bash
# 使用npm
npm install -g @marp-team/marp-cli

# 使用Homebrew
brew install marp-cli

# 验证安装
marp --version
```

## 资源

- [Marp文档](https://marp.app/)
- [Marp CLI GitHub](https://github.com/marp-team/marp-cli)
- [Marpit框架](https://marpit.marp.app/)
- [主题CSS指南](https://marpit.marp.app/theme-css)
