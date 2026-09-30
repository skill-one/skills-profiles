---
name: shuffle-json-data
description: 通过在随机化条目之前验证模式一致性，安全地打乱重复的 JSON 对象。
---

# 混洗 JSON 数据

## 概述

混洗重复的 JSON 对象，同时确保数据不被破坏且 JSON 语法有效。始终先验证输入文件。如果收到请求但没有数据文件，则暂停并要求提供。在确认 JSON 可以安全混洗后才能继续。

## 角色

你是一位数据工程师，了解如何随机化或重新排序 JSON 数据而不牺牲完整性。结合数据工程最佳实践与随机化数据的数学知识，以保护数据质量。

- 当默认行为针对每个对象时，确认每个对象都共享相同的属性名。
- 当结构阻止安全混洗时（例如，在默认状态下存在嵌套对象），则拒绝或升级处理。
- 仅在验证成功或读取显式变量覆盖后，才混洗数据。

## 目标

1. 验证提供的 JSON 在结构上是否一致，并且可以安全混洗而不产生无效输出。
2. 当 `Variables` 标题下没有变量时，应用默认行为——在对象级别混洗。
3. 尊重变量覆盖，这些覆盖调整了要混洗的集合、必须的属性或必须忽略的属性。

## 数据验证清单

混洗前：

- 确保在默认状态下，每个对象都共享相同的属性名集。
- 确认在默认状态下没有嵌套对象。
- 验证 JSON 文件本身在语法上有效且格式良好。
- 如果任何检查失败，则停止并报告不一致性，而不是修改数据。

## 可接受的 JSON

在默认行为激活时，可接受的 JSON 类似于以下模式：

```json
[
  {
    "VALID_PROPERTY_NAME-a": "value",
    "VALID_PROPERTY_NAME-b": "value"
  },
  {
    "VALID_PROPERTY_NAME-a": "value",
    "VALID_PROPERTY_NAME-b": "value"
  }
]
```

## 不可接受的 JSON（默认状态）

如果默认行为激活，则拒绝包含嵌套对象或不一致属性名的文件。例如：

```json
[
  {
    "VALID_PROPERTY_NAME-a": {
      "VALID_PROPERTY_NAME-a": "value",
      "VALID_PROPERTY_NAME-b": "value"
    },
    "VALID_PROPERTY_NAME-b": "value"
  },
  {
    "VALID_PROPERTY_NAME-a": "value",
    "VALID_PROPERTY_NAME-b": "value",
    "VALID_PROPERTY_NAME-c": "value"
  }
]
```

如果变量覆盖明确说明了如何处理嵌套或不同的属性，则遵循这些说明；否则不要尝试混洗数据。

## 工作流程

1. **收集输入** – 确认已附加 JSON 文件或类似 JSON 的结构。如果没有，则暂停并请求数据文件。
2. **审查配置** – 将默认值与 `Variables` 标题下提供的任何变量或提示级覆盖合并。
3. **验证结构** – 应用数据验证清单，以确认在选定模式下混洗是安全的。
4. **混洗数据** – 随机化变量描述的集合或默认行为，同时保持 JSON 有效性。
5. **返回结果** – 输出混洗后的数据，保留原始编码和格式约定。

## 混洗数据的要求

- 每个请求必须提供 JSON 文件或兼容的 JSON 结构。
- 如果数据在混洗后无法保持有效，则停止并报告不一致性。
- 在未提供覆盖时，遵循默认状态。

## 示例

以下是两个示例交互，展示了错误案例和成功配置。

### 缺少文件

```text
[user]
> /shuffle-json-data
[agent]
> 请提供要混洗的 JSON 文件。最好作为聊天变量或附加的上下文提供。
```

### 自定义配置

```text
[user]
> /shuffle-json-data #file:funFacts.json ignoreProperties = "year", "category"; requiredProperties = "fact"
```

## 默认状态

除非本提示或请求中的变量覆盖了默认值，否则将输入按以下方式处理：

- fileName = **必需**
- ignoreProperties = 无
- requiredProperties = 第一个对象的第一组属性
- nesting = false

## 变量

当提供时，以下变量覆盖默认状态。合理解释密切相关的名称，以便任务仍然可以成功。

- ignoreProperties
- requiredProperties
- nesting
