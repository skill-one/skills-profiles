# platform-agentsetup-categories-fetch

从连接的 Salesforce 组织上的 Agentic Setup Categories Connect API 获取提示类别。

## 范围

**在范围内：**
- 通过 SF CLI 调用 `GET /services/data/{apiVersion}/agenticsetup/categories`
- 通过 `fetchPrompts` 查询参数传递以包含嵌套提示
- 解析并展示 JSON 响应（类别、标签、提示）
- 处理错误（功能禁用时返回 403，认证失败）

**不在范围内 — 转移到其他地方：**
- 创建或修改提示类别 → 此 API 不支持（只读）
- 组织认证设置 → 使用 `sf org login` 单独进行
- 权限集分配 → assigning-permission-set

---

## 必需输入

代理需要：
- 一个已连接的组织（通过 `sf org login` 已进行认证）
- 可选：是否包含嵌套提示 (`fetchPrompts=true`)
- 可选：目标 API 版本（默认：v67.0）。如果提供了用户指定的版本，请将 URL 中的 `v67.0` 替换为该版本。

---

## 工作流程

### 1. 验证组织连接性

```bash
sf org display --json
```

确认组织已认证并提取实例 URL。如果没有设置默认组织，请询问用户使用 `--target-org` 目标哪个组织。

### 2. 调用类别 API

**基本调用（仅类别）：**
```bash
sf api request rest /services/data/v67.0/agenticsetup/categories --method GET
```

**包含嵌套提示：**
```bash
sf api request rest "/services/data/v67.0/agenticsetup/categories?fetchPrompts=true" --method GET
```

### 3. 解析并展示响应

API 返回一个包含 `categories` 数组的 JSON 对象。每个类别都有 `name`、`label` 和 `prompts` 字段。参考 `references/api-response-schema.md` 了解完整的响应结构和 `fetchPrompts=true` 和 `fetchPrompts=false` 的示例。

清晰展示结果：
- 列出类别及其名称和标签
- 如果使用了 `fetchPrompts=true`，在每个类别下显示嵌套提示
- 注意任何 `prompts` 数组为空的类别（表示该类别下没有提示）

### 4. 处理错误

| 错误 | 含义 | 操作 |
|-------|---------|--------|
| 成功（退出码 0） | 200 OK | 解析并显示结果 |
| `FUNCTIONALITY_NOT_ENABLED` | 此组织/用户未启用功能 | 告知用户需要启用 Agentic Setup Categories 功能 — 检查 Setup > Einstein/Agentforce |
| `INVALID_SESSION_ID` | 会话过期 | 使用 `sf org login` 重新认证 |
| `NOT_FOUND` | 端点未找到 | API 版本过旧或功能未部署到此组织 |

---

## 规则 / 限制

| 规则 | 理由 |
|------|-----------|
| 始终使用 `sf api request rest` — 永远不要使用 curl 或原始 HTTP | curl 绕过 `~/.sfdx` 会话令牌并需要手动 Authorization 头部，使其变得脆弱 |
| 绝对不要使用 SOQL 查询 | 类别不在标准对象中 — 仅可通过此 Connect REST API 获取 |
| 绝对不要生成文件（LWC、Apex、XML） | 这是一个数据获取任务，不是代码生成任务 |
| 默认为 v67.0，除非用户指定 | 这是引入此端点的最低版本 |
| 除非要求，否则不要传递 fetchPrompts | 减少有效载荷大小；提示可能很大 |
| 类别按标签排序 | API 按字母顺序返回它们 — 不要重新排序 |
| 提示按文本排序 | 在每个类别内，提示按字母顺序排列 |

---

## 输出预期

完成时展示：

1. **返回的类别数量**
2. **类别列表** — 每个类别的名称和标签
3. **提示**（如果请求） — 在其类别下显示
4. **遇到的任何错误** 及建议的解决方案

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|--------------|
| `references/api-response-schema.md` | 当你需要了解完整的响应结构和字段描述时 |
