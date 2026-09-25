````prompt
---
mode: 'agent'
tools: ['changes', 'search/codebase', 'edit/editFiles', 'problems']
description: '为基于MCP的API插件添加自适应卡响应模板，以便在Microsoft 365 Copilot中可视化呈现数据'
model: 'gpt-4.1'
tags: [mcp, 自适应卡, m365-copilot, api-plugin, 响应模板]
---

# 为MCP插件创建自适应卡

为基于MCP的API插件添加自适应卡响应模板，以增强Microsoft 365 Copilot中数据可视化呈现方式。

## 自适应卡类型

### 静态响应模板
当API始终返回相同类型的项目且格式不经常变化时使用。

在`response_semantics.static_template`中定义`ai-plugin.json`：

```json
{
  "functions": [
    {
      "name": "GetBudgets",
      "description": "返回预算详情，包括名称和可用资金",
      "capabilities": {
        "response_semantics": {
          "data_path": "$",
          "properties": {
            "title": "$.name",
            "subtitle": "$.availableFunds"
          },
          "static_template": {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.5",
            "body": [
              {
                "type": "Container",
                "$data": "${$root}",
                "items": [
                  {
                    "type": "TextBlock",
                    "text": "名称: ${if(name, name, 'N/A')}",
                    "wrap": true
                  },
                  {
                    "type": "TextBlock",
                    "text": "可用资金: ${if(availableFunds, formatNumber(availableFunds, 2), 'N/A')}",
                    "wrap": true
                  }
                ]
              }
            ]
          }
        }
      }
    }
  ]
}
```

### 动态响应模板
当API返回多种类型的项目且每个项目需要不同的模板时使用。

**ai-plugin.json配置：**
```json
{
  "name": "GetTransactions",
  "description": "返回具有动态模板的交易详情",
  "capabilities": {
    "response_semantics": {
      "data_path": "$.transactions",
      "properties": {
        "template_selector": "$.displayTemplate"
      }
    }
  }
}
```

**包含嵌入式模板的API响应：**
```json
{
  "transactions": [
    {
      "budgetName": "Fourth Coffee lobby renovation",
      "amount": -2000,
      "description": "Property survey for permit application",
      "expenseCategory": "permits",
      "displayTemplate": "$.templates.debit"
    },
    {
      "budgetName": "Fourth Coffee lobby renovation",
      "amount": 5000,
      "description": "Additional funds to cover cost overruns",
      "expenseCategory": null,
      "displayTemplate": "$.templates.credit"
    }
  ],
  "templates": {
    "debit": {
      "type": "AdaptiveCard",
      "version": "1.5",
      "body": [
        {
          "type": "TextBlock",
          "size": "medium",
          "weight": "bolder",
          "color": "attention",
          "text": "借记"
        },
        {
          "type": "FactSet",
          "facts": [
            {
              "title": "预算",
              "value": "${budgetName}"
            },
            {
              "title": "金额",
              "value": "${formatNumber(amount, 2)}"
            },
            {
              "title": "类别",
              "value": "${if(expenseCategory, expenseCategory, 'N/A')}"
            },
            {
              "title": "描述",
              "value": "${if(description, description, 'N/A')}"
            }
          ]
        }
      ],
      "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
    },
    "credit": {
      "type": "AdaptiveCard",
      "version": "1.5",
      "body": [
        {
          "type": "TextBlock",
          "size": "medium",
          "weight": "bolder",
          "color": "good",
          "text": "贷记"
        },
        {
          "type": "FactSet",
          "facts": [
            {
              "title": "预算",
              "value": "${budgetName}"
            },
            {
              "title": "金额",
              "value": "${formatNumber(amount, 2)}"
            },
            {
              "title": "描述",
              "value": "${if(description, description, 'N/A')}"
            }
          ]
        }
      ],
      "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
    }
  }
}
```

### 静态和动态模板的组合
当项目没有`template_selector`或值无法解析时使用静态模板作为默认值。

```json
{
  "capabilities": {
    "response_semantics": {
      "data_path": "$.items",
      "properties": {
        "title": "$.name",
        "template_selector": "$.templateId"
      },
      "static_template": {
        "type": "AdaptiveCard",
        "version": "1.5",
        "body": [
          {
            "type": "TextBlock",
            "text": "默认: ${name}",
            "wrap": true
          }
        ]
      }
    }
  }
}
```

## 响应语义属性

### data_path
JSONPath查询，指示数据在API响应中的位置：
```json
"data_path": "$"           // 响应根
"data_path": "$.results"   // 在results属性中
"data_path": "$.data.items"// 嵌套路径
```

### properties
映射响应字段以供Copilot引用：
```json
"properties": {
  "title": "$.name",            // 引用标题
  "subtitle": "$.description",  // 引用副标题
  "url": "$.link"               // 引用链接
}
```

### template_selector
每个项目上的属性，指示使用哪个模板：
```json
"template_selector": "$.displayTemplate"
```

## 自适应卡模板语言

### 条件渲染
```json
{
  "type": "TextBlock",
  "text": "${if(field, field, 'N/A')}"  // 显示字段或'N/A'
}
```

### 数字格式化
```json
{
  "type": "TextBlock",
  "text": "${formatNumber(amount, 2)}"  // 两位小数
}
```

### 数据绑定
```json
{
  "type": "Container",
  "$data": "${$root}",  // 跳转到根上下文
  "items": [ ... ]
}
```

### 条件显示
```json
{
  "type": "Image",
  "url": "${imageUrl}",
  "$when": "${imageUrl != null}"  // 只有当imageUrl存在时显示
}
```

## 卡片元素

### TextBlock
```json
{
  "type": "TextBlock",
  "text": "文本内容",
  "size": "medium",      // small, default, medium, large, extraLarge
  "weight": "bolder",    // lighter, default, bolder
  "color": "attention",  // default, dark, light, accent, good, warning, attention
  "wrap": true
}
```

### FactSet
```json
{
  "type": "FactSet",
  "facts": [
    {
      "title": "标签",
      "value": "值"
    }
  ]
}
```

### Image
```json
{
  "type": "Image",
  "url": "https://example.com/image.png",
  "size": "medium",  // auto, stretch, small, medium, large
  "style": "default" // default, person
}
```

### Container
```json
{
  "type": "Container",
  "$data": "${items}",  // 遍历数组
  "items": [
    {
      "type": "TextBlock",
      "text": "${name}"
    }
  ]
}
```

### ColumnSet
```json
{
  "type": "ColumnSet",
  "columns": [
    {
      "type": "Column",
      "width": "auto",
      "items": [ ... ]
    },
    {
      "type": "Column",
      "width": "stretch",
      "items": [ ... ]
    }
  ]
}
```

### Actions
```json
{
  "type": "Action.OpenUrl",
  "title": "查看详情",
  "url": "https://example.com/item/${id}"
}
```

## 响应式设计最佳实践

### 单列布局
- 在窄视口使用单列
- 尽可能避免多列布局
- 确保卡片在最小视口宽度下工作

### 弹性宽度
- 不要为元素分配固定宽度
- 使用"auto"或"stretch"作为宽度属性
- 允许元素随视口调整大小
- 仅图标/头像可以使用固定宽度

### 文本和图片
- 避免在同一行放置文本和图片
- 例外：小图标或头像
- 使用"wrap": true为文本内容
- 在不同视口宽度下测试

### 跨中心测试
在以下环境中验证卡片：
- Teams（桌面和移动）
- Word
- PowerPoint
- 各种视口宽度（收缩/扩展UI）

## 完整示例

**ai-plugin.json:**
```json
{
  "functions": [
    {
      "name": "SearchProjects",
      "description": "搜索具有状态和详情的项目",
      "capabilities": {
        "response_semantics": {
          "data_path": "$.projects",
          "properties": {
            "title": "$.name",
            "subtitle": "$.status",
            "url": "$.projectUrl"
          },
          "static_template": {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.5",
            "body": [
              {
                "type": "Container",
                "$data": "${$root}",
                "items": [
                  {
                    "type": "TextBlock",
                    "size": "medium",
                    "weight": "bolder",
                    "text": "${if(name, name, 'Untitled Project')}",
                    "wrap": true
                  },
                  {
                    "type": "FactSet",
                    "facts": [
                      {
                        "title": "状态",
                        "value": "${status}"
                      },
                      {
                        "title": "负责人",
                        "value": "${if(owner, owner, 'Unassigned')}"
                      },
                      {
                        "title": "截止日期",
                        "value": "${if(dueDate, dueDate, 'Not set')}"
                      },
                      {
                        "title": "预算",
                        "value": "${if(budget, formatNumber(budget, 2), 'N/A')}"
                      }
                    ]
                  },
                  {
                    "type": "TextBlock",
                    "text": "${if(description, description, 'No description')}",
                    "wrap": true,
                    "separator": true
                  }
                ]
              }
            ],
            "actions": [
              {
                "type": "Action.OpenUrl",
                "title": "查看项目",
                "url": "${projectUrl}"
              }
            ]
          }
        }
      }
    }
  ]
}
```

## 工作流程

询问用户：
1. API返回什么类型的数据？
2. 所有项目都是相同类型（静态）还是不同类型（动态）？
3. 卡片中应显示哪些字段？
4. 是否需要操作（例如，“查看详情”）？
5. 是否有多个状态或类别需要不同的模板？

然后生成：
- 适当的响应语义配置
- 静态模板、动态模板或两者
- 带有条件渲染的适当数据绑定
- 响应式单列布局
- 验证测试场景

## 资源

- [自适应卡设计器](https://adaptivecards.microsoft.com/designer) - 可视化设计工具
- [自适应卡模式](https://adaptivecards.io/schemas/adaptive-card.json) - 完整模式参考
- [模板语言](https://learn.microsoft.com/en-us/adaptive-cards/templating/language) - 绑定语法指南
- [JSONPath](https://www.rfc-editor.org/rfc/rfc9535) - 路径查询语法

## 常见模式

### 带图片的列表
```json
{
  "type": "Container",
  "$data": "${items}",
  "items": [
    {
      "type": "ColumnSet",
      "columns": [
        {
          "type": "Column",
          "width": "auto",
          "items": [
            {
              "type": "Image",
              "url": "${thumbnailUrl}",
              "size": "small",
              "$when": "${thumbnailUrl != null}"
            }
          ]
        },
        {
          "type": "Column",
          "width": "stretch",
          "items": [
            {
              "type": "TextBlock",
              "text": "${title}",
              "weight": "bolder",
              "wrap": true
            }
          ]
        }
      ]
    }
  ]
}
```

### 状态指示器
```json
{
  "type": "TextBlock",
  "text": "${status}",
  "color": "${if(status == 'Completed', 'good', if(status == 'In Progress', 'attention', 'default'))}"
}
```

### 货币格式化
```json
{
  "type": "TextBlock",
  "text": "$${formatNumber(amount, 2)}"
}
```
