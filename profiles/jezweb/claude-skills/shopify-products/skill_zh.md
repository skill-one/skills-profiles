# Shopify 产品

创建、更新和批量导入 Shopify 产品。通过 GraphQL 管理后台 API 或 CSV 导入在商店中生成实时产品。

## 前置条件

- 管理后台 API 访问令牌（如果未配置，请使用 **shopify-setup** 技能）
- 从 `shopify.config.json` 或 `.dev.vars` 获取的商店 URL 和 API 版本

## 工作流程

### 第 1 步：收集产品数据

确定用户想要创建或更新的内容：

- **产品基本信息**：标题、描述（HTML）、产品类型、供应商、标签
- **变体**：选项（尺寸、颜色、材质）、价格、SKU、库存数量
- **图片**：上传的 URL 或本地文件
- **SEO**：页面标题、元描述、URL 占位符
- **组织**：系列、产品类型、标签

接受数据来源：

- 直接对话（用户描述产品）
- 电子表格/CSV 文件（用户提供文件）
- 网站抓取（用户提供要提取的 URL）

### 第 2 步：选择方法

| 场景 | 方法 |
|------|------|
| 1-5 个产品 | GraphQL 变更 |
| 6-20 个产品 | GraphQL 批量处理 |
| 20+ 个产品 | 通过管理后台 CSV 导入 |
| 更新现有产品 | GraphQL 变更 |
| 库存调整 | `inventorySetQuantities` 变更 |

---

### 第 3 步 a：通过 GraphQL 创建（推荐）

#### productCreate

```graphql
mutation productCreate($product: ProductCreateInput!) {
  productCreate(product: $product) {
    product {
      id
      title
      handle
      status
      variants(first: 100) {
        edges {
          node { id title price sku inventoryQuantity }
        }
      }
    }
    userErrors { field message }
  }
}
```

变量：

```json
{
  "product": {
    "title": "示例 T 恤",
    "descriptionHtml": "<p>优质棉 T 恤</p>",
    "vendor": "我的品牌",
    "productType": "T 恤",
    "tags": ["夏季", "棉质"],
    "status": "草稿",
    "options": ["尺寸", "颜色"],
    "variants": [
      {
        "optionValues": [
          {"optionName": "尺寸", "name": "S"},
          {"optionName": "颜色", "name": "黑色"}
        ],
        "price": "29.95",
        "sku": "TSHIRT-S-BLK",
        "inventoryPolicy": "DENY",
        "inventoryItem": { "tracked": true }
      },
      {
        "optionValues": [
          {"optionName": "尺寸", "name": "M"},
          {"optionName": "颜色", "name": "黑色"}
        ],
        "price": "29.95",
        "sku": "TSHIRT-M-BLK"
      },
      {
        "optionValues": [
          {"optionName": "尺寸", "name": "L"},
          {"optionName": "颜色", "name": "黑色"}
        ],
        "price": "29.95",
        "sku": "TSHIRT-L-BLK"
      }
    ],
    "seo": {
      "title": "示例 T 恤 | 我的地标",
      "description": "优质棉 T 恤，多种尺寸"
    }
  }
}
```

Curl 示例：

```bash
curl -s https://{store}/admin/api/2025-01/graphql.json \
  -H "Content-Type: application/json" \
  -H "X-Shopify-Access-Token: {token}" \
  -d '{"query": "mutation productCreate($product: ProductCreateInput!) { productCreate(product: $product) { product { id title } userErrors { field message } } }", "variables": { ... }}'
```

**批量创建多个产品**：按顺序创建产品，每个产品之间有短延迟以尊重速率限制（每秒 1,000 成本点）。

#### productUpdate

```graphql
mutation productUpdate($input: ProductInput!) {
  productUpdate(input: $input) {
    product { id title }
    userErrors { field message }
  }
}
```

变量包括 `id`（必需）以及任何要更新的字段。

#### productDelete

```graphql
mutation productDelete($input: ProductDeleteInput!) {
  productDelete(input: $input) {
    deletedProductId
    userErrors { field message }
  }
}
```

#### productVariantsBulkCreate

向现有产品添加变体：

```graphql
mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkCreate(productId: $productId, variants: $variants) {
    productVariants { id title price }
    userErrors { field message }
  }
}
```

#### productVariantsBulkUpdate

```graphql
mutation productVariantsBulkUpdate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkUpdate(productId: $productId, variants: $variants) {
    productVariants { id title price }
    userErrors { field message }
  }
}
```

---

### 第 3 步 b：通过 CSV 批量导入

对于 20+ 个产品，生成 CSV 文件并通过 Shopify 管理后台导入。

#### CSV 列参考

**必需列**：

| 列名 | 描述 | 示例 |
|------|------|------|
| `Handle` | URL 占位符（每个产品唯一） | `classic-tshirt` |
| `Title` | 产品名称（每个产品的第一行） | `经典 T 恤` |
| `Body (HTML)` | HTML 格式描述 | `<p>优质棉</p>` |
| `Vendor` | 品牌或制造商 | `我的品牌` |
| `Product Category` | Shopify 标准分类 | `服装 & 配饰 > 衣物 > 衬衫 & 顶部` |
| `Type` | 自定义产品类型 | `T 恤` |
| `Tags` | 以逗号分隔的标签 | `夏季, 棉质, 休闲` |
| `Published` | 产品是否可见 | `TRUE` 或 `FALSE` |

**变体列**：

| 列名 | 描述 | 示例 |
|------|------|------|
| `Option1 Name` | 第一个选项名称 | `尺寸` |
| `Option1 Value` | 第一个选项值 | `中` |
| `Option2 Name` | 第二个选项名称 | `颜色` |
| `Option2 Value` | 第二个选项值 | `黑色` |
| `Option3 Name` | 第三个选项名称 | `材质` |
| `Option3 Value` | 第三个选项值 | `棉质` |
| `Variant SKU` | 库存单位 | `TSHIRT-M-BLK` |
| `Variant Grams` | 重量（克） | `200` |
| `Variant Inventory Qty` | 库存数量 | `50` |
| `Variant Price` | 变体价格 | `29.95` |
| `Variant Compare At Price` | 原价（用于销售） | `39.95` |
| `Variant Requires Shipping` | 实体产品 | `TRUE` |
| `Variant Taxable` | 应纳税 | `TRUE` |

**图片列**：

| 列名 | 描述 | 示例 |
|------|------|------|
| `Image Src` | 图片 URL | `https://example.com/img.jpg` |
| `Image Position` | 显示顺序（从 1 开始） | `1` |
| `Image Alt Text` | 可访问性替代文本 | `经典 T 恤正面视图` |

**SEO 列**：

| 列名 | 描述 | 示例 |
|------|------|------|
| `SEO Title` | 页面标题标签 | `经典 T 恤 | 我的地标` |
| `SEO Description` | 元描述 | `5 种颜色的优质棉 T 恤` |

#### 多变体行格式

第一行包含产品标题和详细信息。同一产品的后续行仅包含 `Handle` 和变体特定列：

```csv
Handle,Title,Body (HTML),Vendor,Type,Tags,Published,Option1 Name,Option1 Value,Variant SKU,Variant Price,Variant Inventory Qty,Image Src
classic-tshirt,经典 T 恤,<p>优质棉</p>,我的品牌,T 恤,"夏季,棉质",TRUE,尺寸,小,TSH-S,29.95,50,https://example.com/tshirt.jpg
classic-tshirt,,,,,,,,中,TSH-M,29.95,75,
classic-tshirt,,,,,,,,大,TSH-L,29.95,60,
```

#### CSV 规则

- 需要 UTF-8 编码
- 最大文件大小 50MB
- Handle 必须每个产品唯一 -- 重复的 Handle 会更新现有产品
- 变体行中对于不变的字段，留空变体列
- 图片可以在任何行上 -- 它们通过 Handle 关联
- `Published` = `TRUE` 会立即使产品可见

#### 导入步骤

1. 使用上述列格式生成 CSV
2. 如果可用，使用 `assets/product-csv-template.csv` 模板
3. 导航到 `https://{store}.myshopify.com/admin/products/import`
4. 上传 CSV 文件
5. 预览并确认导入

如果需要，可以使用浏览器自动化来协助上传。

---

### 第 4 步：上传产品图片

图片需要两步流程 -- 阶段性上传然后关联。

#### stagedUploadsCreate

```graphql
mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
  stagedUploadsCreate(input: $input) {
    stagedTargets {
      url
      resourceUrl
      parameters { name value }
    }
    userErrors { field message }
  }
}
```

每个文件输入：

```json
{
  "filename": "product-image.jpg",
  "mimeType": "image/jpeg",
  "httpMethod": "POST",
  "resource": "IMAGE"
}
```

然后上传到阶段性 URL，并使用 `productCreateMedia` 关联：

#### productCreateMedia

```graphql
mutation productCreateMedia($productId: ID!, $media: [CreateMediaInput!]!) {
  productCreateMedia(productId: $productId, media: $media) {
    media { alt status }
    mediaUserErrors { field message }
  }
}
```

**快捷方式**：如果图片已经托管在公共 URL 上，可以在产品创建中直接传递 `src`：

```json
{
  "images": [
    { "src": "https://example.com/image.jpg", "alt": "产品正面视图" }
  ]
}
```

---

### 第 5 步：分配到系列

#### collectionAddProducts

```graphql
mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
  collectionAddProducts(id: $id, productIds: $productIds) {
    collection { title productsCount }
    userErrors { field message }
  }
}
```

要查找系列 ID：

```graphql
{
  collections(first: 50) {
    edges {
      node { id title handle productsCount }
    }
  }
}
```

---

### 第 6 步：设置库存

#### inventorySetQuantities

```graphql
mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
  inventorySetQuantities(input: $input) {
    inventoryAdjustmentGroup { reason }
    userErrors { field message }
  }
}
```

输入：

```json
{
  "reason": "修正",
  "name": "可用",
  "quantities": [{
    "inventoryItemId": "gid://shopify/InventoryItem/123",
    "locationId": "gid://shopify/Location/456",
    "quantity": 50
  }]
}
```

要查找位置 ID：

```graphql
{
  locations(first: 10) {
    edges {
      node { id name isActive }
    }
  }
}
```

---

### 第 7 步：验证

查询创建的产品以确认：

```graphql
{
  products(first: 50) {
    edges {
      node {
        id title handle status productType vendor
        variants(first: 10) {
          edges { node { id title price sku inventoryQuantity } }
        }
        images(first: 3) { edges { node { url altText } } }
      }
    }
    pageInfo { hasNextPage endCursor }
  }
}
```

为用户提供管理后台 URL 以供审查：`https://{store}.myshopify.com/admin/products`

---

## 关键模式

### 产品状态

新产品默认为 `草稿`。要使其可见：

```json
{ "status": "活跃" }
```

在设置状态为 `活跃` 之前，请始终与用户确认。

### 变体限制

Shopify 允许每个产品最多 **100 个变体**和**3 个选项**（例如尺寸、颜色、材质）。如果需要更多，请拆分为单独的产品。

### 价格格式

价格是字符串，不是数字。始终用引号引起来：`"price": "29.95"` 而不是 `"price": 29.95`。

### HTML 描述

产品描述接受 HTML。保持简单 -- Shopify 的编辑器处理基本标签：
- `<p>`, `<strong>`, `<em>`, `<ul>`, `<ol>`, `<li>`, `<h2>`-`<h6>`
- `<a href="...">` 用于链接
- `<img>` 被移除 -- 使用产品图片

### 批量操作用于大量导入

对于 50+ 个产品通过 API，使用 Shopify 的批量操作：

```graphql
mutation {
  bulkOperationRunMutation(
    mutation: "mutation ($input: ProductInput!) { productCreate(input: $input) { product { id } userErrors { message } } }"
    stagedUploadPath: "tmp/bulk-products.jsonl"
  ) {
    bulkOperation { id status }
    userErrors { message }
  }
}
```

这接受一个 JSONL 文件，每行一个产品，异步处理。

---

## 资产文件

- `assets/product-csv-template.csv` -- 带有 Shopify 导入标题的空白 CSV 模板
