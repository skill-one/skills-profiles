# N8N 工作流技能

## 概述

该技能可使用 **n8n** 实现文档工作流自动化——这是拥有 7800+ 社区模板的最流行的工作流自动化平台。串联文档操作，与 400+ 应用集成，并构建复杂的文档管道。

## 如何使用

1. 描述您想要完成的目标
2. 提供所需的输入数据或文件
3. 我将执行相应的操作

**示例提示：**
- "自动化 PDF → OCR → 翻译 → 邮件工作流"
- "监控文件夹以获取新合同 → 审核 → 通知 Slack"
- "从多个数据源生成每日报告"
- "带条件逻辑的批量文档处理"

## 领域知识


### n8n 基础知识

n8n 采用基于节点的工 作流方法：

```
触发器 → 操作 → 操作 → 输出
   │         │         │
   └─────────┴─────────┴── 数据在节点间流动
```

### 关键节点类型

| 类型 | 示例 | 用途 |
|------|------|------|
| **触发器** | Webhook、计划、文件监控器 | 启动工作流 |
| **文档** | 读取 PDF、写入 DOCX、OCR | 处理文件 |
| **转换** | 代码、设置、合并 | 操作数据 |
| **输出** | 邮件、Slack、Google 驱动器 | 交付结果 |

### 工作流示例：合同审核管道

```json
{
  "nodes": [
    {
      "name": "监控文件夹",
      "type": "n8n-nodes-base.localFileTrigger",
      "parameters": {
        "path": "/contracts/incoming",
        "events": ["add"]
      }
    },
    {
      "name": "提取文本",
      "type": "n8n-nodes-base.readPdf"
    },
    {
      "name": "AI 审核",
      "type": "n8n-nodes-base.anthropic",
      "parameters": {
        "model": "claude-sonnet-4-20250514",
        "prompt": "审核这份合同的风险..."
      }
    },
    {
      "name": "保存报告",
      "type": "n8n-nodes-base.writeFile"
    },
    {
      "name": "通知团队",
      "type": "n8n-nodes-base.slack"
    }
  ]
}
```

### 自托管与云服务

| 选项 | 优点 | 缺点 |
|------|------|------|
| **自托管** | 免费、完全控制、数据隐私 | 需要维护 |
| **n8n 云服务** | 无需设置、自动更新 | 扩规模时产生费用 |

```bash
# Docker 快速启动
docker run -it --rm \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```


## 最佳实践

1. **从现有模板开始，按需自定义**
2. **使用错误处理节点提高可靠性**
3. **使用 n8n 的凭证管理器安全存储凭证**
4. **在生产环境前用样本数据测试工作流**

## 安装

```bash
# 安装所需依赖
pip install python-docx openpyxl python-pptx reportlab jinja2
```

## 资源

- [n8n 代码库](https://github.com/n8n-io/n8n)
- [Claude 办公技能中心](https://github.com/claude-office-skills/skills)
