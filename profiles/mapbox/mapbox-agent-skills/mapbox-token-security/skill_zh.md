# Mapbox Token 安全技能

此技能提供管理 Mapbox 访问令牌的安全专业知识。

## 令牌类型及使用场景

### 公开令牌 (pk.*)

**特点：**

- 可安全地暴露在客户端代码中
- 仅限于特定的公开范围
- 可设置 URL 限制
- 无法访问敏感 API

**使用场景：**

- 客户端 Web 应用
- 移动应用
- 公开演示
- 网站上的嵌入式地图

**允许的范围：**

- `styles:tiles` - 显示样式瓦片（栅格）
- `styles:read` - 读取样式规范
- `fonts:read` - 访问 Mapbox 字体
- `datasets:read` - 读取数据集数据
- `vision:read` - 视觉 API 访问

### 秘密令牌 (sk.*)

**特点：**

- **绝对不要**暴露在客户端代码中
- 具有任意范围的完整 API 访问权限
- 仅限服务器端使用
- 可创建/管理其他令牌

**使用场景：**

- 服务器端应用
- 后端服务
- CI/CD 管道
- 管理任务
- 令牌管理

**常见范围：**

- `styles:write` - 创建/修改样式
- `styles:list` - 列出所有样式
- `tokens:read` - 查看令牌信息
- `tokens:write` - 创建/修改令牌
- 用户反馈管理范围

### 临时令牌 (tk.*)

**特点：**

- 短期有效（最长 1 小时）
- 由秘密令牌创建
- 单用途使用
- 自动过期

**使用场景：**

- 一次性操作
- 临时授权访问
- 短期演示
- 注重安全的流程

## 范围管理最佳实践

### 最小权限原则

**始终授予所需的最低范围：**

❌ **错误：**

```javascript
// 过度宽松 - 不要这样做
{
  scopes: ['styles:read', 'styles:write', 'styles:list', 'styles:delete', 'tokens:read', 'tokens:write'];
}
```

✅ **正确：**

```javascript
// 仅用于显示地图所需的范围
{
  scopes: ['styles:read', 'fonts:read'];
}
// 如果您的地图使用栅格瓦片源，请添加 'styles:tiles'
{
  scopes: ['styles:read', 'fonts:read', 'styles:tiles'];
}
```

### 根据使用场景组合范围

**公开地图显示（客户端）：**

```json
{
  "scopes": ["styles:read", "fonts:read", "styles:tiles"],
  "note": "用于地图显示的公开令牌",
  "allowedUrls": ["https://myapp.com/*"]
}
```

**样式管理（服务器端）：**

```json
{
  "scopes": ["styles:read", "styles:write", "styles:list"],
  "note": "后端样式管理 - 秘密令牌"
}
```

**令牌管理（服务器端）：**

```json
{
  "scopes": ["tokens:read", "tokens:write"],
  "note": "仅限令牌管理 - 秘密令牌"
}
```

**只读访问：**

```json
{
  "scopes": ["styles:list", "styles:read", "tokens:read"],
  "note": "审计/监控 - 秘密令牌"
}
```

## URL 限制

### URL 限制的重要性

URL 限制限制公开令牌的使用范围，防止令牌暴露时的未授权使用。

### 有效的 URL 模式

✅ **推荐的模式：**

```
https://myapp.com/*           # 生产域名
https://*.myapp.com/*         # 所有子域名
https://staging.myapp.com/*   # 测试环境
http://localhost:*            # 本地开发
```

❌ **避免这些：**

```
*                             # 无限制（不安全）
http://*                      # 任何 HTTP 网站（不安全）
*.com/*                       # 太宽泛
```

### 多环境策略

为每个环境创建单独的令牌：

```javascript
// 生产环境
{
  note: "生产环境 - myapp.com",
  scopes: ["styles:read", "fonts:read"],
  allowedUrls: ["https://myapp.com/*", "https://www.myapp.com/*"]
}

// 测试环境
{
  note: "测试环境 - staging.myapp.com",
  scopes: ["styles:read", "fonts:read"],
  allowedUrls: ["https://staging.myapp.com/*"]
}

// 开发环境
{
  note: "开发环境 - localhost",
  scopes: ["styles:read", "fonts:read"],
  allowedUrls: ["http://localhost:*", "http://127.0.0.1:*"]
}
```

## 令牌存储和处理

### 服务器端（秘密令牌）

✅ **应该做：**

- 存储在环境变量中
- 使用密钥管理服务（AWS Secrets Manager、HashiCorp Vault）
- 静态加密
- 通过 IAM 策略限制访问
- 记录令牌使用情况

❌ **不应该做：**

- 硬编码在源代码中
- 提交到版本控制
- 存储在明文配置文件中
- 通过电子邮件或 Slack 共享
- 在多个服务中重复使用

**示例：安全的环境变量：**

```bash
# .env (绝对不要提交此文件)
MAPBOX_SECRET_TOKEN=sk.ey...

# .gitignore (绝对要包含 .env)
.env
.env.local
.env.*.local
```

### 客户端（公开令牌）

✅ **应该做：**

- 仅使用公开令牌
- 应用 URL 限制
- 每个应用使用不同的令牌
- 定期轮换
- 监控使用情况

❌ **不应该做：**

- 暴露秘密令牌
- 使用无 URL 限制的令牌
- 在不相关的应用之间共享令牌
- 使用范围过广的令牌

**示例：安全的客户端使用（Vite）：**

> **注意：** 此示例使用 **Vite**。对于 Next.js、CRA、Angular 或普通的 `window.MAPBOX_ACCESS_TOKEN` / CDN 设置，请参阅 [令牌管理](references/token-management.md)。不要在一个表达式中链式使用 `import.meta.env` 和 `process.env` — 浏览器中未使用的路径会抛出 `ReferenceError`。

```javascript
// 带有 URL 限制的公开令牌 - 安全（Vite）
const mapboxToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN;

// 在构建地图之前进行保护 — 否则缺少令牌会导致静默的空白地图
if (!mapboxToken || mapboxToken === 'YOUR_MAPBOX_ACCESS_TOKEN') {
  throw new Error('缺少 VITE_MAPBOX_ACCESS_TOKEN — 在创建地图前设置环境变量');
}

mapboxgl.accessToken = mapboxToken;
```

### 代理的反模式：跳过令牌保护

代理通常直接分配 `mapboxgl.accessToken` 并调用 `new mapboxgl.Map(...)` 而不进行任何检查。这会导致空白画布且没有 UI 错误。

**始终：**

1. 从您的打包器（不要在源代码中硬编码真实的 `pk.`）解析令牌
2. 验证其存在且不是占位符
3. 然后设置 `accessToken` 并构建地图

## 安全检查清单

**令牌创建：**

- [ ] 客户端使用公开令牌，服务器端使用秘密令牌
- [ ] 对范围应用最小权限原则
- [ ] 对公开令牌添加 URL 限制
- [ ] 使用描述性名称/注释进行令牌识别
- [ ] 记录预期用途和环境

**令牌管理：**

- [ ] 将秘密令牌存储在环境变量或密钥管理器中
- [ ] 绝不将令牌提交到版本控制
- [ ] 每 90 天（或按策略）轮换令牌
- [ ] 及时删除未使用的令牌
- [ ] 按环境（开发/测试/生产）分离令牌
- [ ] 在客户端代码中 `new mapboxgl.Map` 之前保护缺失的令牌

**监控：**

- [ ] 跟踪令牌使用模式
- [ ] 设置异常活动的警报
- [ ] 定期进行安全审计（每月）
- [ ] 每季度审查团队访问权限
- [ ] 扫描存储库以查找暴露的令牌

**事件响应：**

- [ ] 文档化的撤销程序
- [ ] 紧急联系人列表
- [ ] 记录的轮换程序
- [ ] 事件后审查模板
- [ ] 团队安全流程培训

## 参考文件

针对特定主题的详细指导，按需加载这些参考文件：

- **`references/token-management.md`** — 打包器特定的环境变量名称和访问模式（Vite / Next / CRA / Angular / CDN）。加载场景：在 Vite 示例上方不同的框架中配置令牌。
- **`references/rotation-monitoring.md`** — 令牌轮换策略（零停机时间 + 紧急）、监控指标、警报规则和每月/每季度审计清单。加载场景：实施轮换、设置监控或进行审计。
- **`references/incident-response.md`** — 步骤化的事件响应计划和常见安全错误及代码示例。加载场景：响应令牌泄露、审查代码中的安全问题或进行反模式培训。

## 何时使用此技能

在以下情况下调用此技能：

- 创建新令牌
- 在公开令牌和秘密令牌之间进行选择
- 设置令牌限制
- 实施令牌轮换
- 调查安全事件
- 进行安全审计
- 培训团队进行令牌安全
- 审查代码以查找令牌暴露
