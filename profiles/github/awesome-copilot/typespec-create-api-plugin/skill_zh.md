# 创建 TypeSpec API 插件

为 Microsoft 365 Copilot 创建一个完整的 TypeSpec API 插件，该插件可与外部 REST API 集成。

## 要求

生成 TypeSpec 文件，包括：

### main.tsp - 代理定义
```typescript
import "@typespec/http";
import "@typespec/openapi3";
import "@microsoft/typespec-m365-copilot";
import "./actions.tsp";

using TypeSpec.Http;
using TypeSpec.M365.Copilot.Agents;
using TypeSpec.M365.Copilot.Actions;

@agent({
  name: "[代理名称]",
  description: "[描述]"
})
@instructions("""
  [使用 API 操作的说明]
""")
namespace [代理名称] {
  // 引用 actions.tsp 中的操作
  op operation1 is [APINamespace].operationName;
}
```

### actions.tsp - API 操作
```typescript
import "@typespec/http";
import "@microsoft/typespec-m365-copilot";

using TypeSpec.Http;
using TypeSpec.M365.Copilot.Actions;

@service
@actions(#{
    nameForHuman: "[API 显示名称]",
    descriptionForModel: "[模型描述]",
    descriptionForHuman: "[用户描述]"
})
@server("[API_BASE_URL]", "[API 名称]")
@useAuth([AuthType]) // 可选
namespace [APINamespace] {
  
  @route("[/路径]")
  @get
  @action
  op operationName(
    @path param1: string,
    @query param2?: string
  ): ResponseModel;

  model ResponseModel {
    // 响应结构
  }
}
```

## 认证选项

根据 API 要求选择：

1. **无认证**（公开 API）
   ```typescript
   // 无需 @useAuth 装饰器
   ```

2. **API 密钥**
   ```typescript
   @useAuth(ApiKeyAuth<ApiKeyLocation.header, "X-API-Key">)
   ```

3. **OAuth2**
   ```typescript
   @useAuth(OAuth2Auth<[{
     type: OAuth2FlowType.authorizationCode;
     authorizationUrl: "https://oauth.example.com/authorize";
     tokenUrl: "https://oauth.example.com/token";
     refreshUrl: "https://oauth.example.com/token";
     scopes: ["read", "write"];
   }]>)
   ```

4. **注册认证引用**
   ```typescript
   @useAuth(Auth)
   
   @authReferenceId("registration-id-here")
   model Auth is ApiKeyAuth<ApiKeyLocation.header, "X-API-Key">
   ```

## 功能特性

### 确认对话框
```typescript
@capabilities(#{
  confirmation: #{
    type: "AdaptiveCard",
    title: "确认操作",
    body: """
    您确定要执行此操作吗？
      * **参数**: {{ function.parameters.paramName }}
    """
  }
})
```

### Adaptive Card 响应
```typescript
@card(#{
  dataPath: "$.items",
  title: "$.title",
  url: "$.link",
  file: "cards/card.json"
})
```

### 推理与响应说明
```typescript
@reasoning("""
  在调用此操作时考虑用户的上下文。
  优先考虑最近的项目而不是旧的项目。
""")
@responding("""
  以清晰的表格格式呈现结果，列：ID、标题、状态。
  在末尾包含摘要计数。
""")
```

## 最佳实践

1. **操作名称**：使用清晰、以行为导向的名称（listProjects、createTicket）
2. **模型**：为请求和响应定义 TypeScript 类似的模型
3. **HTTP 方法**：使用适当的动词（@get、@post、@patch、@delete）
4. **路径**：使用 @route 和 RESTful 路径规范
5. **参数**：适当使用 @path、@query、@header、@body
6. **描述**：为模型理解提供清晰的描述
7. **确认**：对破坏性操作（删除、更新关键数据）添加确认
8. **卡片**：用于具有多个数据项的丰富视觉响应

## 工作流程

询问用户：
1. API 基础 URL 和用途是什么？
2. 需要哪些操作（CRUD 操作）？
3. API 使用哪种认证方法？
4. 是否需要对任何操作进行确认？
5. 响应是否需要 Adaptive Cards？

然后生成：
- 完整的 `main.tsp`，包含代理定义
- 完整的 `actions.tsp`，包含 API 操作和模型
- 如果需要 Adaptive Cards，则可选的 `cards/card.json`
