# Shopify 开发技能

在用户询问以下内容时使用此技能：

- 构建 Shopify 应用或扩展
- 创建结账/管理/POS 界面定制
- 使用 Liquid 模板开发主题
- 集成 Shopify GraphQL 或 REST API
- 实现 webhook 或计费
- 使用 metafields 或 Shopify Functions

---

## 路由：构建内容

**如果用户希望集成外部服务或构建商家工具或为功能收费：**
→ 构建 **应用**（参考 `references/app-development.md`）

**如果用户希望定制结账或添加管理界面或创建 POS 操作或实现折扣规则：**
→ 构建 **扩展**（参考 `references/extensions.md`）

**如果用户希望定制店面设计或修改产品/系列页面：**
→ 构建 **主题**（参考 `references/themes.md`）

**如果用户需要后端逻辑和店面界面：**
→ 构建 **应用 + 主题扩展** 组合

---

## Shopify CLI 命令

安装 CLI：

```bash
npm install -g @shopify/cli@latest
```

创建和运行应用：

```bash
shopify app init          # 创建新应用
shopify app dev           # 启动开发服务器并使用隧道
shopify app deploy        # 构建并上传到 Shopify
```

生成扩展：

```bash
shopify app generate extension --type checkout_ui_extension
shopify app generate extension --type admin_action
shopify app generate extension --type admin_block
shopify app generate extension --type pos_ui_extension
shopify app generate extension --type function
```

主题开发：

```bash
shopify theme init        # 创建新主题
shopify theme dev         # 在 localhost:9292 启动本地预览
shopify theme pull --live # 拉取实时主题
shopify theme push --development  # 推送到开发主题
```

---

## 访问范围

在 `shopify.app.toml` 中配置：

```toml
[access_scopes]
scopes = "read_products,write_products,read_orders,write_orders,read_customers"
```

常用范围：

- `read_products`, `write_products` - 产品目录访问
- `read_orders`, `write_orders` - 订单管理
- `read_customers`, `write_customers` - 客户数据
- `read_inventory`, `write_inventory` - 库存水平
- `read_fulfillments`, `write_fulfillments` - 订单履行

---

## GraphQL 模式（针对 API 2026-01 验证）

### 查询产品

```graphql
query GetProducts($first: Int!, $query: String) {
  products(first: $first, query: $query) {
    edges {
      node {
        id
        title
        handle
        status
        variants(first: 5) {
          edges {
            node {
              id
              price
              inventoryQuantity
            }
          }
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

### 查询订单

```graphql
query GetOrders($first: Int!) {
  orders(first: $first) {
    edges {
      node {
        id
        name
        createdAt
        displayFinancialStatus
        totalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
      }
    }
  }
}
```

### 设置 Metafields

```graphql
mutation SetMetafields($metafields: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $metafields) {
    metafields {
      id
      namespace
      key
      value
    }
    userErrors {
      field
      message
    }
  }
}
```

变量示例：

```json
{
  "metafields": [
    {
      "ownerId": "gid://shopify/Product/123",
      "namespace": "custom",
      "key": "care_instructions",
      "value": "Handle with care",
      "type": "single_line_text_field"
    }
  ]
}
```

---

## 结账扩展示例

```tsx
import {
  reactExtension,
  BlockStack,
  TextField,
  Checkbox,
  useApplyAttributeChange,
} from "@shopify/ui-extensions-react/checkout";

export default reactExtension("purchase.checkout.block.render", () => (
  <GiftMessage />
));

function GiftMessage() {
  const [isGift, setIsGift] = useState(false);
  const [message, setMessage] = useState("");
  const applyAttributeChange = useApplyAttributeChange();

  useEffect(() => {
    if (isGift && message) {
      applyAttributeChange({
        type: "updateAttribute",
        key: "gift_message",
        value: message,
      });
    }
  }, [isGift, message]);

  return (
    <BlockStack spacing="loose">
      <Checkbox checked={isGift} onChange={setIsGift}>
        This is a gift
      </Checkbox>
      {isGift && (
        <TextField
          label="Gift Message"
          value={message}
          onChange={setMessage}
          multiline={3}
        />
      )}
    </BlockStack>
  );
}
```

---

## Liquid 模板示例

```liquid
{% comment %} 产品卡片片段 {% endcomment %}
<div class="product-card">
  <a href="{{ product.url }}">
    {% if product.featured_image %}
      <img
        src="{{ product.featured_image | img_url: 'medium' }}"
        alt="{{ product.title | escape }}"
        loading="lazy"
      >
    {% endif %}
    <h3>{{ product.title }}</h3>
    <p class="price">{{ product.price | money }}</p>
    {% if product.compare_at_price > product.price %}
      <p class="sale-badge">Sale</p>
    {% endif %}
  </a>
</div>
```

---

## Webhook 配置

在 `shopify.app.toml` 中：

```toml
[webhooks]
api_version = "2026-01"

[[webhooks.subscriptions]]
topics = ["orders/create", "orders/updated"]
uri = "/webhooks/orders"

[[webhooks.subscriptions]]
topics = ["products/update"]
uri = "/webhooks/products"

# GDPR 强制性 webhook（应用批准所需）
[webhooks.privacy_compliance]
customer_data_request_url = "/webhooks/gdpr/data-request"
customer_deletion_url = "/webhooks/gdpr/customer-deletion"
shop_deletion_url = "/webhooks/gdpr/shop-deletion"
```

---

## 最佳实践

### API 使用

- 新开发使用 GraphQL 而不是 REST
- 仅请求您需要的字段（减少查询成本）
- 使用 `pageInfo.endCursor` 实现基于游标的分页
- 使用批量操作处理超过 250 项的数据
- 使用指数退避处理速率限制

### 安全

- 将 API 凭据存储在环境变量中
- 处理 webhook 时始终验证 HMAC 签名
- 验证 OAuth state 参数以防止 CSRF
- 请求最小访问范围
- 使用会话令牌为嵌入式应用

### 性能

- 当数据不经常变化时缓存 API 响应
- 在扩展中使用懒加载
- 使用 `img_url` 过滤器在主题中优化图像
- 通过响应头监控 GraphQL 查询成本

---

## 故障排除

**如果看到速率限制错误：**
→ 实现指数退避重试逻辑
→ 切换到批量操作处理大数据集
→ 监控 `X-Shopify-Shop-Api-Call-Limit` 头

**如果身份验证失败：**
→ 验证访问令牌是否仍然有效
→ 检查是否授予了所有必需的范围
→ 确保 OAuth 流程成功完成

**如果扩展未出现：**
→ 验证扩展目标是否正确
→ 检查是否通过 `shopify app deploy` 发布扩展
→ 确认应用已安装在测试商店

**如果 webhook 未接收事件：**
→ 验证 webhook URL 是否公开可访问
→ 检查 HMAC 签名验证逻辑
→ 在合作伙伴仪表板中查看 webhook 日志

**如果 GraphQL 查询失败：**
→ 使用 GraphiQL 探索器验证查询与模式
→ 在错误消息中检查已弃用的字段
→ 验证您是否具有所需访问范围

---

## 参考文件

阅读以下文件获取详细的实现指南：

- `references/app-development.md` - OAuth 身份验证流程，用于产品/订单/计费 GraphQL 变更，webhook 处理器，计费 API 集成
- `references/extensions.md` - 结账 UI 组件，管理界面扩展，POS 扩展，用于折扣/支付/配送的 Shopify Functions
- `references/themes.md` - Liquid 语法参考，主题目录结构，部分和片段，常见模式

---

## 脚本

- `scripts/shopify_init.py` - 交互式项目脚手架。运行：`python scripts/shopify_init.py`
- `scripts/shopify_graphql.py` - GraphQL 工具，包含查询模板，分页，速率限制。导入：`from shopify_graphql import ShopifyGraphQL`

---

## 官方文档链接

- Shopify 开发者文档：https://shopify.dev/docs
- GraphQL 管理员 API 参考：https://shopify.dev/docs/api/admin-graphql
- Shopify CLI 参考：https://shopify.dev/docs/api/shopify-cli
- Polaris 设计系统：https://polaris.shopify.com

API 版本：2026-01（季度发布，12 个月弃用窗口）

## 使用场景
此技能适用于执行概述中描述的工作流程或操作。

## 限制
- 仅在任务明确匹配上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家审查的替代品。
- 如果缺少必需的输入、权限、安全边界或成功标准，请停止并请求澄清。
