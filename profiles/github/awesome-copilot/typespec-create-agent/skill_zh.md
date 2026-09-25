# 创建 TypeSpec 声明式代理

创建一个完整的 TypeSpec 声明式代理，用于 Microsoft 365 Copilot，其结构如下：

## 要求

生成一个 `main.tsp` 文件，包含以下内容：

1. **代理声明**
   - 使用 `@agent` 装饰器，并附带描述性名称和描述
   - 名称不超过 100 个字符
   - 描述不超过 1,000 个字符

2. **指令**
   - 使用 `@instructions` 装饰器，并包含清晰的指导方针
   - 定义代理的角色、专业领域和个性
   - 指定代理应该和不应该做什么
   - 保持长度在 8,000 字符以内

3. **对话启动器**
   - 包含 2-4 个 `@conversationStarter` 装饰器
   - 每个包含标题和示例查询
   - 使其多样化，展示不同的功能

4. **功能**（根据用户需求）
   - `WebSearch` - 用于网络内容，可选站点范围限制
   - `OneDriveAndSharePoint` - 用于文档访问，支持 URL 过滤
   - `TeamsMessages` - 用于 Teams 频道/聊天访问
   - `Email` - 用于邮件访问，支持文件夹过滤
   - `People` - 用于组织人员搜索
   - `CodeInterpreter` - 用于 Python 代码执行
   - `GraphicArt` - 用于图像生成
   - `GraphConnectors` - 用于 Copilot 连接器内容
   - `Dataverse` - 用于 Dataverse 数据访问
   - `Meetings` - 用于会议内容访问

## 模板结构

```typescript
import "@typespec/http";
import "@typespec/openapi3";
import "@microsoft/typespec-m365-copilot";

using TypeSpec.Http;
using TypeSpec.M365.Copilot.Agents;

@agent({
  name: "[Agent Name]",
  description: "[Agent Description]"
})
@instructions("""
  [关于代理行为、角色和指导方针的详细说明]
""")
@conversationStarter(#{
  title: "[启动器标题 1]",
  text: "[示例查询 1]"
})
@conversationStarter(#{
  title: "[启动器标题 2]",
  text: "[示例查询 2]"
})
namespace [AgentName] {
  // 在此处添加功能作为操作
  op capabilityName is AgentCapabilities.[CapabilityType]<[参数]>;
}
```

## 最佳实践

- 使用描述性、基于角色的代理名称（例如，“客户支持助手”、“研究助手”）
- 使用第二人称编写指令（例如，“你是……”）
- 明确代理的专业领域和限制
- 包含多样化的对话启动器，展示不同的功能
- 仅包含代理实际需要的功能
- 在可能的情况下对功能进行范围限制（例如 URL、文件夹），以提升性能
- 使用三引号字符串表示多行指令

## 示例

询问用户：
1. 代理的用途和角色是什么？
2. 代理需要哪些功能？
3. 代理应该访问哪些知识源？
4. 典型的用户交互是什么？

然后生成完整的 TypeSpec 代理定义。
