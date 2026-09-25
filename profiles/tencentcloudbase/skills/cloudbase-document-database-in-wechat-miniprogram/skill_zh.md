## 兄弟技能（仅本地使用）

兄弟 CloudBase 技能会与此技能一同部署。使用本地相对路径，例如 `../auth-tool-cloudbase/SKILL.md`。

如果此环境中缺少引用的兄弟技能文件，请提示用户安装完整的 CloudBase 插件（或缺失的技能）。**不要**将远程技能或协议的 Markdown 通过 HTTP 获取到代理上下文中。

# CloudBase 文档数据库微信小程序 SDK

## 激活协议

### 首次使用时

- 微信小程序需要通过 `wx.cloud.database()` 访问 CloudBase 文档数据库。
- 请求中提及小程序集合的 CRUD、分页、聚合或地理位置查询。

### 编写代码前需阅读

- 任务是小程序数据库工作，但仍然需要将其与 Web SDK、云函数或 SQL 任务分离。
- 请求依赖于内置用户身份、`_openid` 或小程序端权限。

### 还需阅读

- 小程序项目规则和 CloudBase 集成 -> `../miniprogram-development/SKILL.md`
- 小程序认证和身份流程 -> `../auth-wechat-miniprogram/SKILL.md`
- 浏览器端文档数据库代码 -> `../cloudbase-document-database-web-sdk/SKILL.md`

### 不应用于

- 使用 `@cloudbase/js-sdk` 的浏览器/网页代码。
- 服务器端或云函数的数据库访问。
- MySQL / 关系型数据库工作。

### 常见错误/注意事项

- 将 Web SDK 代码复制到小程序页面。
- 在创建或更新操作中手动编写 `_openid`。
- 认为内置小程序身份意味着可以忽略安全规则。
- 在同一客户端路径中混合集合 CRUD 和全局管理员工作流。

### 最小清单

- 确认调用者是小程序页面/组件或小程序端逻辑。
- 在数据库调用前正确初始化 `wx.cloud`。
- 验证集合规则是否依赖 `auth.openid` / `_openid`。
- 阅读您所需操作的特定配套参考文件。

## 概述

此技能涵盖通过 `wx.cloud.database()` 实现的**小程序端文档数据库访问**。

用于：

- 小程序页面中的集合 CRUD
- 查询组合和分页
- 聚合
- 地理位置查询

小程序 CloudBase 访问具有内置身份，但数据库操作仍然受集合权限和安全规则约束。

## 标准初始化

```javascript
const db = wx.cloud.database();
const _ = db.command;
```

要针对特定环境：

```javascript
const db = wx.cloud.database({
  env: "test"
});
```

重要说明：

- 用户通过小程序 CloudBase 上下文进行认证。
- 在云函数中，调用者身份可通过 `wxContext.OPENID` 获取。
- 在客户端集合规则中，所有权检查通常使用 `auth.openid` / `doc._openid`。

## 快速路由

- CRUD -> `./crud-operations.md`
- 复杂查询 -> `./complex-queries.md`
- 分页 -> `./pagination.md`
- 聚合 -> `./aggregation.md`
- 地理位置查询 -> `./geolocation.md`
- 安全规则 -> `./security-rules.md`

## 编码代理的工作规则

1. **保持小程序代码小程序原生**
   - 使用 `wx.cloud.database()`。
   - 不要替换浏览器 SDK 初始化模式。

2. **尊重所有权字段**
   - `_openid` 由系统管理 SDK 写入。
   - 在 `.add()`、`.set()` 或 `.update()` 负载中永远不要手动设置或覆盖 `_openid`。

3. **记住安全规则验证请求**
   - 如果规则需要所有权条件，查询形状必须匹配该规则模型。
   - 权限错误通常意味着规则/查询关系不正确，而不仅仅是用户登出。

4. **将管理员风格的操作路由到后端流程**
   - 如果任务需要特权全局访问，请使用后端工具或函数，而不是在小程序客户端代码中直接暴露该路径。

## 快速示例

### 基本集合访问

```javascript
const todos = db.collection("todos");
const result = await todos.where({ completed: false }).get();
```

### 文档引用

```javascript
const todo = db.collection("todos").doc("todo-id");
const result = await todo.get();
```

## 最佳实践

1. 创建清晰的集合命名规范。
2. 在应用代码中尽可能使用类型包装器或模型辅助工具。
3. 基于真实的所有权和共享模式设计规则。
4. 使用分页而不是大型无界读取。
5. 将管理员/操作逻辑保留在后端代码中，而不是直接从小程序访问。
