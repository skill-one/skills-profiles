# CV构建技能

## 概述

该技能能够使用**rendercv**从结构化的YAML创建专业的简历。只需定义一次您的经验，即可在多种主题中生成美观的PDF文件。

## 如何使用

1. 提供您的简历信息（经验、教育、技能）
2. 选择一个模板/主题
3. 我将生成YAML并渲染为PDF

**示例提示：**
- "根据我的经验创建简历"
- "生成经典主题的简历"
- "用新的工作经验更新我的简历"
- "构建突出项目的技术简历"

## 领域知识

### YAML结构

```yaml
cv:
  name: John Doe
  location: San Francisco, CA
  email: john@email.com
  phone: "+1-555-555-5555"
  website: https://johndoe.com
  social_networks:
    - network: LinkedIn
      username: johndoe
    - network: GitHub
      username: johndoe
  
  sections:
    summary:
      - "资深软件工程师，拥有10年以上经验..."
    
    experience:
      - company: Tech Corp
        position: 资深工程师
        location: San Francisco, CA
        start_date: 2020-01
        end_date: 至今
        highlights:
          - "领导5人工程师团队"
          - "性能提升40%"
    
    education:
      - institution: MIT
        area: 计算机科学
        degree: 学士学位
        start_date: 2008
        end_date: 2012
    
    skills:
      - label: 语言
        details: Python, JavaScript, Go
      - label: 框架
        details: React, Django, FastAPI
```

### 主题

可用主题：`classic`, `sb2nov`, `moderncv`, `engineeringresumes`

```yaml
design:
  theme: classic
  font: Source Sans 3
  font_size: 10pt
  page_size: letterpaper
  color: '#004f90'
```

### 命令行使用

```bash
# 安装
pip install rendercv

# 创建新简历
rendercv new "John Doe"

# 渲染为PDF
rendercv render cv.yaml

# 输出: rendercv_output/John_Doe_CV.pdf
```

## 示例

```yaml
cv:
  name: Sarah Chen
  location: New York, NY
  email: sarah@email.com
  phone: "+1-555-123-4567"
  website: https://sarahchen.dev
  social_networks:
    - network: LinkedIn
      username: sarahchen
    - network: GitHub
      username: sarahchen

  sections:
    summary:
      - "全栈开发人员，拥有8年构建可扩展Web应用程序的经验。热衷于干净代码和用户体验。"

    experience:
      - company: Startup Inc
        position: 首席开发人员
        location: New York, NY
        start_date: 2021-03
        end_date: 至今
        highlights:
          - "架构微服务，每日处理100万+请求"
          - "指导4名初级开发人员"
          - "通过CI/CD将部署时间缩短60%"

      - company: Big Tech Co
        position: 软件工程师
        location: San Francisco, CA
        start_date: 2018-06
        end_date: 2021-02
        highlights:
          - "构建实时分析仪表板"
          - "优化数据库查询，速度提升3倍"

    education:
      - institution: Stanford University
        area: 计算机科学
        degree: 硕士学位
        start_date: 2016
        end_date: 2018

    skills:
      - label: 语言
        details: Python, TypeScript, Go, SQL
      - label: 技术
        details: React, Node.js, PostgreSQL, AWS, Docker
      - label: 实践
        details: 敏捷开发, 单元测试, 代码审查, CI/CD

design:
  theme: sb2nov
  font_size: 10pt
```

## 资源

- [rendercv文档](https://docs.rendercv.com/)
- [GitHub仓库](https://github.com/sinaatalay/rendercv)
- [主题库](https://docs.rendercv.com/user_guide/themes/)
