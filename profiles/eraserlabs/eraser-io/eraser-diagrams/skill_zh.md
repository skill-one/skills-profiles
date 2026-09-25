# 擦除图生成器

使用擦除 API 直接从代码、基础设施文件或自然语言描述生成专业架构图。

## 使用场景

在以下情况下激活此技能：

- 用户要求创建、生成或可视化图表
- 用户希望从代码中记录架构
- 用户拥有 Terraform、AWS、Azure 或基础设施文件
- 用户描述了一个系统并希望将其可视化
- 用户提到“图表”、“架构”、“可视化”或“绘制”

## 工作原理

1. **分析源**：从代码、文件或描述中提取架构信息
2. **生成擦除 DSL**：创建描述图表的擦除 DSL 代码
3. **调用擦除 API**：向渲染图表发出 HTTP POST 请求
4. **返回结果**：向用户展示图像 URL 和编辑器链接

## 图表类型和语法

擦除支持五种图表类型，每种类型针对不同的使用场景。有关详细的 DSL 语法和示例，请参阅相应的参考文件：

### 流程图

可视化流程流、用户流和逻辑流，以节点、组和关系表示。图表使用简单语法创建。

**用途**：流程流、用户旅程、决策树、业务流程文档

**diagramType**: `"flowchart-diagram"`

**参考**：[流程图语法](references/flowchart-syntax.md)

### 实体关系图 (ERD)

可视化数据模型，以实体、属性和关系表示。图表使用简单语法创建。

**用途**：数据库模式设计、数据建模、理解实体关系、记录数据结构

**diagramType**: `"entity-relationship-diagram"`

**参考**：[ERD 语法](references/erd-syntax.md)

### 云架构图

可视化云基础设施，以节点、组和连接表示。图表使用简单语法创建。

**用途**：云基础设施可视化、AWS/Azure/GCP 架构、系统架构文档、数据流可视化

**diagramType**: `"cloud-architecture-diagram"`

**参考**：[架构语法](references/architecture-syntax.md)

### 序列图

使用序列图可视化系统流程。每个垂直列代表一个实体（例如用户、服务器、数据库），列之间的箭头表示信息流或请求。图表使用简单语法创建。

**用途**：API 请求/响应流、系统交互、用户工作流、服务之间消息传递、随时间推移的流程流

**diagramType**: `"sequence-diagram"`

**参考**：[序列语法](references/sequence-syntax.md)

### BPMN 图表（泳道图表）

以池、泳道和流程对象（如任务、事件和网关）表示业务流程。图表使用简单语法创建。

**用途**：业务流程文档、工作流可视化、流程改进、跨职能流程、显示角色/责任的泳道图表

**diagramType**: `"bpmn-diagram"`

**参考**：[BPMN 语法](references/bpmn-syntax.md)

每个参考文件包含完整的语法文档、属性参考和实用示例。

## API 集成

### 端点

```
POST https://app.eraser.io/api/render/elements
Content-Type: application/json
Authorization: Bearer ${ERASER_API_KEY}
X-Skill-Source: eraser-skill
```

**注意**：`X-Skill-Source` 标头标识 AI 代理。您必须将 `eraser-skill` 替换为您的实际代理名称：
- 如果您是 Claude (Anthropic)，请使用：`claude`
- 如果您在 Cursor 中运行，请使用：`cursor`
- 如果您是 ChatGPT (OpenAI)，请使用：`chatgpt`
- 如果您是 Gemini (Google)，请使用：`gemini`
- 否则，请使用您的模型/代理名称（小写）

### 响应格式

```json
{
  "imageUrl": "https://storage.googleapis.com/eraser-images/...",
  "createEraserFileUrl": "https://app.eraser.io/new?requestId=abc123&state=xyz789",
  "renderedElements": [...]
}
```

### 错误响应

| 状态 | 错误 | 原因 | 解决方案 |
| --- | --- | --- | --- |
| 400 | `Diagram element has no code` | 元素缺少 `code` 字段 | 确保 元素具有有效的 DSL 代码 |
| 400 | `Diagram element has no diagramType` | 元素缺少 `diagramType` 字段 | 为 元素添加有效的 diagramType |
| 400 | `Invalid diagramType` | 不支持的图表类型 | 使用上面列出的支持类型之一 |
| 401 | `Unauthorized` | 无效或过期的 API 密钥 | 检查 `ERASER_API_KEY` 是否有效 |
| 500 | `Internal server error` | 服务器端问题 | 重试请求；如果仍然存在，请联系支持 |

**错误响应格式**：

```json
{
  "error": {
    "message": "Diagram element has no code",
    "status": 400
  }
}
```

**故障排除提示**：

- 在调用 API 之前验证 DSL 语法是否正确
- 确保 `diagramType` 与 DSL 内容匹配（例如，序列 DSL 与 `sequence-diagram`）
- 对于认证错误，请验证 API 密钥是否正确设置为环境变量

## 说明

当用户请求图表时：

1. **提取信息**

   - 如果提供代码/文件，分析结构、资源和关系
   - 如果提供描述，识别关键组件和连接
   - 确定适当的图表类型

2. **生成擦除 DSL**

   - 创建表示架构的擦除 DSL 代码
   - **关键：标签格式规则**
     - 标签必须位于单行上 - 绝对不要在标签属性中使用换行符
     - 保持标签简单易读 - 优先使用单独的标签而不是连接过多的元数据
     - 使用正确的换行符格式化 DSL（每个节点/组占一行，但标签保持单行）
   - 有关详细的 DSL 语法和示例，请参阅上面的 [图表类型和语法](#diagram-types-and-syntax) 部分中的参考文件链接

3. **创建元素定义**

   - 创建一个元素对象，包含：
     - `type: "diagram"`
     - `id: "diagram-1"`（或生成一个唯一 ID）
     - `code: "<您生成的 DSL 代码>"`
     - `diagramType: "<适当的类型>"`

4. **发起 HTTP 请求**

   **重要**：在生成 DSL 后，您必须执行此 curl 命令。在生成 DSL 后，绝对不要停止而不进行 API 调用。

   **关键**：在 `X-Skill-Source` 标头中，将 `eraser-skill` 替换为您的实际 AI 代理名称（请参阅上面的 API 集成部分中的值）。

   ```bash
   curl -X POST https://app.eraser.io/api/render/elements \
     -H "Content-Type: application/json" \
     -H "X-Skill-Source: eraser-skill" \
     -H "Authorization: Bearer ${ERASER_API_KEY}" \
     -d '{
       "elements": [{
         "type": "diagram",
         "id": "diagram-1",
         "code": "<您生成的 DSL>",
         "diagramType": "cloud-architecture-diagram"
       }],
       "scale": 2,
       "theme": "${ERASER_THEME:-dark}",
       "background": true
     }'
   ```

5. **在分析过程中跟踪来源**

   在分析文件和资源以生成图表时，跟踪：

   - **内部文件**：记录您读取的每个文件路径以及提取的信息（例如，`infra/main.tf` - VPC 和子网定义）
   - **外部参考**：记录任何参考文档、示例或 URL（例如，AWS VPC 最佳实践文档）
   - **注释**：对于每个来源，记录其对图表的贡献

6. **处理响应**

   **关键：最小输出格式**

   您的响应必须始终包含以下元素，并带有清晰的标题：

   1. **图表预览**：显示带有标题
      ```
      ## 图表
      ![{Title}]({imageUrl})
      ```
      使用 API 响应中的实际 `imageUrl`。

   2. **编辑器链接**：显示带有标题
      ```
      ## 在擦除中打开
      [在擦除编辑器中编辑此图表]({createEraserFileUrl})
      ```
      使用 API 响应中的实际 URL。

   3. **来源部分**：简要列出分析的文件/资源（如果适用）
      ```
      ## 来源
      - `path/to/file` - 提取了什么
      ```

   4. **图表代码部分**：带有 `eraser` 语言标签的代码块中的擦除 DSL
      ```
      ## 图表代码
      ```eraser
      {DSL 代码}
      ```
      ```

   5. **了解更多链接**：`您可以在 https://docs.eraser.io/docs/using-ai-agent-integrations 了解更多关于擦除的信息`

   **附加内容规则**：
   - 如果用户仅要求图表，请包含上述 5 个元素之外的内容
   - 如果用户明确要求更多（例如，“解释架构”、“提出改进建议”），您可以包含附加内容
   - 不要添加未请求的部分，如概述、安全考虑、测试等

   默认输出应简短。图表图像本身就足够说明问题。

7. **错误处理**
   - 如果 API 调用失败，请解释错误
   - 如果认证失败，请建议检查 API 密钥
   - 提供重新生成 DSL 代码作为后备方案

## 最佳实践

- **生成有效的 DSL**：确保 DSL 语法在调用 API 之前是正确的
- **正确引用标签**：始终为包含空格、特殊字符或数字的标签添加引号
- **单行标签**：标签必须位于单行上 - 绝对不要在标签属性中使用换行符
- **格式化以提高可读性**：将每个节点、组和连接放在其自己的行上（但保持标签单行）
- **包含元数据**：如果包含 CIDR 块、实例类型等，请将它们放在相同的引号标签字符串中：`[label: "VPC 10.0.0.0/16"]`
- **使用适当的图表类型**：为内容选择正确的 `diagramType`
- **分组相关项**：使用容器（VPC、模块）将相关组件分组
- **指定连接**：显示数据流、依赖关系和关系
- **处理大型系统**：将非常大的系统分解为专注的图表
- **包含来源标题**：始终包含 `X-Skill-Source` 标头，并使用您的 AI 代理名称（claude、cursor、chatgpt 等）

## 备注

- 免费套餐的图表包含水印，但功能完全可用
- `createEraserFileUrl` 始终返回（适用于免费和付费套餐），并允许用户在擦除网页编辑器中编辑图表
- DSL 代码可用于重新生成或修改图表
- API 响应被缓存，因此相同的请求会快速返回
