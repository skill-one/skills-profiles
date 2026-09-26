# Shopify 内容

创建和管理 Shopify 店铺内容——页面、博客文章、导航菜单和 SEO 元数据。通过 Admin API 或浏览器自动化在店铺中生成实时内容。

## 前置条件

- 具有读取内容 (`read_content`) 和写入内容 (`write_content`) 权限的 Admin API 访问令牌（使用 **shopify-setup** 技能）
- 对于导航：`read_online_store_navigation` 和 `write_online_store_navigation` 权限

## 工作流程

### 第 1 步：确定内容类型

| 内容类型 | API 支持 | 方法 |
|-------------|-------------|--------|
| 页面 | 完整 | GraphQL Admin API |
| 博客文章 | 完整 | GraphQL Admin API |
| 导航菜单 | 有限 | 推荐使用浏览器自动化 |
| 重定向 | 完整 | REST Admin API |
| SEO 元数据 | 按资源 | 资源上的 GraphQL |
| Metaobjects | 完整 | GraphQL Admin API |

### 第 2 步 a：创建页面

```bash
curl -s https://{store}/admin/api/2025-01/graphql.json \
  -H "Content-Type: application/json" \
  -H "X-Shopify-Access-Token: {token}" \
  -d '{
    "query": "mutation pageCreate($page: PageCreateInput!) { pageCreate(page: $page) { page { id title handle } userErrors { field message } } }",
    "variables": {
      "page": {
        "title": "关于我们",
        "handle": "about",
        "body": "<h2>我们的故事</h2><p>内容...</p>",
        "isPublished": true,
        "seo": {
          "title": "关于我们 | 店铺名称",
          "description": "了解我们的故事和使命。"
        }
      }
    }
  }'
```

**页面正文** 接受 HTML。保持语义化：
- 使用 `<h2>` 到 `<h6>` 作为标题（页面标题是 `<h1>`）
- 使用 `<p>`、`<ul>`、`<ol>` 作为正文文本
- 使用 `<a href="...">` 作为链接
- 避免内联样式——主题负责样式

### 第 2 步 b：创建博客文章

Shopify 博客具有两层结构：**博客**（容器）> **文章**（帖子）。

**查找或创建博客**：

```graphql
{
  blogs(first: 10) {
    edges {
      node { id title handle }
    }
  }
}
```

大多数店铺都有一个默认博客，名为 "新闻"。在它中创建文章：

```graphql
mutation {
  articleCreate(article: {
    blogId: "gid://shopify/Blog/123"
    title: "新产品发布"
    handle: "new-product-launch"
    contentHtml: "<p>我们很高兴宣布...</p>"
    author: { name: "店铺团队" }
    tags: ["新闻", "产品"]
    isPublished: true
    publishDate: "2026-02-22T00:00:00Z"
    seo: {
      title: "新产品发布 | 店铺名称"
      description: "宣布我们最新的产品系列。"
    }
    image: {
      src: "https://example.com/blog-image.jpg"
      altText: "新产品系列"
    }
  }) {
    article { id title handle }
    userErrors { field message }
  }
}
```

### 第 2 步 c：更新导航菜单

导航菜单的 API 支持有限。使用浏览器自动化：

1. 导航到 `https://{store}.myshopify.com/admin/menus`
2. 选择要编辑的菜单（通常是 "主菜单" 或 "页脚菜单"）
3. 添加、重新排序或删除菜单项
4. 保存更改

或者，如果 API 版本支持，使用 GraphQL 的 `menuUpdate` 变量：

```graphql
mutation menuUpdate($id: ID!, $items: [MenuItemInput!]!) {
  menuUpdate(id: $id, items: $items) {
    menu { id title }
    userErrors { field message }
  }
}
```

### 第 2 步 d：创建重定向

URL 重定向使用 REST API：

```bash
curl -s https://{store}/admin/api/2025-01/redirects.json \
  -H "Content-Type: application/json" \
  -H "X-Shopify-Access-Token: {token}" \
  -d '{
    "redirect": {
      "path": "/old-page",
      "target": "/new-page"
    }
  }'
```

### 第 2 步 e：更新 SEO 元数据

SEO 字段在每个资源（产品、页面、文章）上。通过资源的变量更新：

```graphql
mutation {
  pageUpdate(page: {
    id: "gid://shopify/Page/123"
    seo: {
      title: "更新后的 SEO 标题"
      description: "更新后的元描述，少于 160 个字符。"
    }
  }) {
    page { id title }
    userErrors { field message }
  }
}
```

### 第 3 步：验证

查询内容以确认：

```graphql
{
  pages(first: 10, reverse: true) {
    edges {
      node { id title handle isPublished createdAt }
    }
  }
}
```

提供管理 URL 和实时 URL 以供用户审查：
- 管理：`https://{store}.myshopify.com/admin/pages`
- 实时：`https://{store}.myshopify.com/pages/{handle}`

---

## 关键模式

### 页面与 Metaobject

对于简单内容（关于、联系、常见问题），使用 **页面**。对于结构化、可重复的内容（团队成员、客户评价、位置），使用 **Metaobject**——它们具有类型字段，并且可以编程查询。

### 博客 SEO

每个博客文章应有：
- **SEO 标题**：少于 60 个字符，包含主要关键词
- **元描述**：少于 160 个字符，引人入胜的摘要
- **Handle**：包含关键词的干净 URL 拼写
- **带 alt 文本的图片**：用于社交分享和可访问性

### 内容调度

使用文章的 `publishDate` 进行计划发布。页面在 `isPublished: true` 时立即发布。

### 批量内容

对于许多页面（例如位置页面、服务页面），使用带速率限制的循环：

```bash
for page in pages_data:
    create_page(page)
    sleep(0.5)  # 尊重速率限制
```

---

## 参考文件

- `references/content-types.md` — API 端点、Metaobject 模式和仅限浏览器的操作
