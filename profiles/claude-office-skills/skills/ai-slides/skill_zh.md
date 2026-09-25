# AI幻灯片技能

## 概述

该技能支持AI驱动的演示文稿生成。提供主题或大纲，即可获得结构完整、内容精良、格式规范的演示文稿。

## 使用方法

1. 提供主题、大纲或粗略笔记
2. 指定受众和演示时长
3. 我将生成完整的演示文稿

**示例提示：**
- "创建一份关于机器学习的10页演示文稿"
- "为SaaS初创公司生成路演演示文稿"
- "构建关于网络安全基础知识的培训幻灯片"
- "根据这些数据制作季度回顾演示文稿"

## 领域知识

### 演示文稿结构

```yaml
# 有效的演示文稿结构
structure:
  - title_slide:
      title: "清晰、引人入胜的标题"
      subtitle: "背景或标语"
      author: "演讲者姓名"
  
  - agenda:
      items: 3-5个主要主题
  
  - introduction:
      hook: "吸引注意力的开场白"
      context: "为什么这很重要"
  
  - main_content:
      sections: 3-5个要点
      each_section:
        - 标题
        - 3-5个要点或视觉元素
        - 支持数据
  
  - conclusion:
      summary: "关键要点"
      call_to_action: "下一步该做什么"
  
  - closing:
      thank_you: true
      contact_info: true
      qa_prompt: true
```

### 内容生成模式

```python
def generate_presentation(topic, audience, slide_count=10):
    """AI驱动的演示文稿生成。"""
    
    # 1. 生成大纲
    outline = generate_outline(topic, slide_count)
    
    # 2. 扩展每个部分
    slides = []
    for section in outline:
        slide_content = expand_section(section, audience)
        slides.append(slide_content)
    
    # 3. 添加视觉建议
    for slide in slides:
        slide['visuals'] = suggest_visuals(slide['content'])
    
    # 4. 格式化为Marp Markdown
    presentation = format_as_marp(slides)
    
    return presentation

def generate_outline(topic, count):
    """生成演示文稿大纲。"""
    # 典型结构
    outline = [
        {'type': 'title', 'title': topic},
        {'type': 'agenda'},
        # 主要内容（占幻灯片60%）
        # ... 内容幻灯片
        {'type': 'summary'},
        {'type': 'closing'}
    ]
    return outline
```

### Marp输出

```python
def format_as_marp(slides):
    """将幻灯片转换为Marp Markdown。"""
    
    marp = """---
marp: true
theme: gaia
paginate: true
---

"""
    
    for slide in slides:
        if slide['type'] == 'title':
            marp += f"""<!-- _class: lead -->

# {slide['title']}

{slide.get('subtitle', '')}

---

"""
        elif slide['type'] == 'content':
            marp += f"""# {slide['heading']}

"""
            for point in slide['points']:
                marp += f"- {point}\n"
            marp += "\n---\n\n"
    
    return marp
```

## 示例：生成技术讲座

```python
topic = "Docker入门"
audience = "对容器化陌生的开发者"
slides = 10

# 生成的演示文稿
presentation = """---
marp: true
theme: gaia
paginate: true
---

<!-- _class: lead -->

# Docker入门

让容器化变得简单

---

# 大纲

1. 什么是Docker？
2. 核心概念
3. 入门指南
4. 最佳实践
5. 演示

---

# 什么是Docker？

- 应用程序打包的容器平台
- 轻量级的虚拟机替代方案
- "一次构建，随处运行"
- 1500万+开发者，700万+应用程序

---

# 为什么使用容器？

| 虚拟机 | 容器 |
|-----|------------|
| GB级大小 | MB级大小 |
| 分钟启动 | 秒级启动 |
| 完整操作系统 | 共享内核 |

---

# 核心概念

- **镜像**：蓝图/模板
- **容器**：运行实例
- **Dockerfile**：构建指令
- **注册中心**：镜像存储（Docker Hub）

---

# 入门指南

```bash
# 拉取镜像
docker pull nginx

# 运行容器
docker run -p 8080:80 nginx

# 列出容器
docker ps
```

---

# 你的第一个Dockerfile

```dockerfile
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

---

# 最佳实践

- 使用官方基础镜像
- 最小化层
- 不要以root身份运行
- 使用.dockerignore
- 多阶段构建

---

# 总结

✅ Docker简化了部署
✅ 容器轻量且快速
✅ 易于上手
✅ 行业标准

---

<!-- _class: lead -->

# 问答？

资源：docs.docker.com
```

## 最佳实践

1. **了解你的受众**：调整复杂度和示例
2. **每页一个观点**：保持专注
3. **6x6规则**：最多6个要点，每个要点6个词
4. **视觉优先**：建议图片/图表
5. **强化开场/结尾**：吸引注意力和行动号召

## 资源

- [Marp](https://marp.app/) - Markdown演示文稿
- [Slidev](https://sli.dev/) - 基于Vue的幻灯片
- [reveal.js](https://revealjs.com/) - HTML演示文稿
