# Shopify 设置

为商店设置可用的 Shopify CLI 身份验证和 Admin API 访问权限。生成一个经过验证的 API 连接，用于产品和管理内容。

## 工作流程

### 第 1 步：检查先决条件

验证是否已安装 Shopify CLI：

```bash
shopify version
```

如果未安装：

```bash
npm install -g @shopify/cli
```

### 第 2 步：使用商店进行身份验证

```bash
shopify auth login --store mystore.myshopify.com
```

这将打开一个浏览器进行 OAuth。用户必须是商店所有者或具有适当权限的员工。

登录后，验证：

```bash
shopify store info
```

### 第 3 步：为 API 访问创建自定义应用

自定义应用提供稳定的 Admin API 访问令牌（与 CLI 会话令牌不同，会话令牌会过期）。

**检查是否已存在应用**：询问用户是否已设置自定义应用。如果是，则跳至第 4 步。

**如果不存在自定义应用**，通过浏览器引导用户进行创建：

1. 导航到 `https://{store}.myshopify.com/admin/settings/apps/development`
2. 点击 **创建应用**
3. 命名（例如 "Claude Code Integration"）
4. 点击 **配置 Admin API 权限范围**
5. 启用以下权限范围（有关详细信息，请参阅 `references/api-scopes.md`）：
   - `read_products`, `write_products`
   - `read_content`, `write_content`
   - `read_product_listings`
   - `read_inventory`, `write_inventory`
   - `read_files`, `write_files`
6. 点击 **保存** 然后点击 **安装应用**
7. 复制 **Admin API 访问令牌**（仅显示一次）

如果用户希望获得协助进行管理后台导航，可以使用浏览器自动化（Chrome MCP 或 playwright-cli）。

### 第 4 步：存储访问令牌

安全地存储令牌。切勿将其提交到 git。

**用于项目** — 创建 `.dev.vars`：

```
SHOPIFY_STORE=mystore.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_xxxxxxxxxxxxxxxxxxxxx
```

确保 `.dev.vars` 在 `.gitignore` 中。

**用于跨项目** — 存储在您首选的密钥管理器中（环境变量、1Password CLI 等）。

### 第 5 步：验证 API 访问

使用简单的 GraphQL 查询测试连接：

```bash
curl -s https://{store}.myshopify.com/admin/api/2025-01/graphql.json \
  -H "Content-Type: application/json" \
  -H "X-Shopify-Access-Token: {token}" \
  -d '{"query": "{ shop { name primaryDomain { url } } }"}' | jq .
```

预期响应包括商店名称和域名。如果收到 401，则令牌无效或已过期 — 重新创建应用。

### 第 6 步：保存商店配置

在项目根目录中创建 `shopify.config.json`，供其他技能参考：

```json
{
  "store": "mystore.myshopify.com",
  "apiVersion": "2025-01",
  "tokenSource": ".dev.vars"
}
```

---

## 关键模式

### API 版本

始终指定明确的 API 版本（例如 `2025-01`）。在生产中使用 `unstable` 将会无警告地中断。Shopify 每季度退役 API 版本。

### 令牌类型

| 令牌 | 格式 | 用途 |
|-------|--------|-----|
| Admin API 访问令牌 | `shpat_*` | 自定义应用 — 稳定、长寿命 |
| CLI 会话令牌 | 短寿命 | 仅限 Shopify CLI 命令 |
| Storefront API 令牌 | `shpca_*` | 公共商店面查询 |

此技能设置 **Admin API 访问令牌** — 适用于产品和管理内容的正确选择。

### 速率限制

Shopify 使用漏桶速率限制器：
- **REST**：每秒 40 个请求的突发，每秒 2 个持续
- **GraphQL**：每秒 1,000 个成本点，每个查询最多 2,000 个点

对于批量操作，使用 `bulkOperationRunQuery` 变异而不是循环。

---

## 参考文件

- `references/api-scopes.md` — 产品和管理内容所需的 Admin API 权限范围
