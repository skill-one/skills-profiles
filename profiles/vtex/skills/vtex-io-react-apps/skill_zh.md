# React 组件与钩子

## 适用场景

在构建使用 `react` 构建的 VTEX IO 前端应用程序时使用此技能——创建与 Store Framework 集成的主题块 React 组件，配置 `interfaces.json`，为 Site Editor 设置 `contentSchemas.json`，并应用样式模式。

- 创建自定义店面组件（产品展示、表单、横幅）
- 使用 VTEX Styleguide 构建管理面板界面
- 将组件注册为 Store Framework 块
- 通过 `contentSchemas.json` 在 Site Editor 中暴露组件属性
- 应用 `css-handles` 以实现安全的店面样式

不使用此技能的情况：

- 后端服务实现（请使用 `vtex-io-service-apps`）
- GraphQL 模式和解析器开发（请使用 `vtex-io-graphql-api`）
- 清单和构建器配置（请使用 `vtex-io-app-structure`）

## 决策规则

- 每个可见的店面元素都是一个 **块**。块在主题 JSON 中声明，并通过 **接口** 映射到 React 组件。
- `interfaces.json`（位于 `/store`）将块名称映射到 React 组件文件：`"component"` 是 `/react` 中的文件名（不带扩展名），“`allowed`” 列出子块，“`composition`” 控制子块的工作方式（`"children"` 或 `"blocks"`）。
- 每个导出的组件必须在 `/react` 中的根级别文件中重新导出它。构建器将 `"component": "ProductReviews"` 解析为 `react/ProductReviews.tsx`。
- 对于 **店面** 组件，使用 `vtex.css-handles` 进行样式设置（不是内联样式，不是全局 CSS）。
- 对于 **管理** 组件，使用 `vtex.styleguide`——官方的 VTEX 管理组件库。不允许使用第三方 UI 库。
- 使用 `/store` 中的 `contentSchemas.json` 使组件属性在 Site Editor 中可编辑（JSON 模式）。商家编辑由 `vtex.pages-graphql` 存储在包含 **声明应用的 MAJOR 版本** 的键下（`vendor.app@MAJOR.x:template`）。声明应用的 MAJOR 版本升级会使这些编辑对解析器不可见，直到它们使用 `vtex.pages-graphql@2.x` 中的 `updateThemeIds` 变量迁移到新的 MAJOR 版本——参见 `vtex-io-storefront-theme-versioning`。
- 使用 `react-intl` 和 `messages` 构建器进行国际化——永远不要硬编码面向用户的字符串。
- 通过 GraphQL 查询（`react-apollo` 的 `useQuery`）获取数据，而不是通过浏览器的直接 API 调用。

架构：

```text
Store Theme (JSON 块)
  └── 声明 "product-reviews" 块并具有属性
        │
        ▼
interfaces.json → 将 "product-reviews" 映射到 "ProductReviews" 组件
        │
        ▼
react/ProductReviews.tsx → React 组件渲染
        │
        ├── useCssHandles() → 样式 CSS 类
        ├── useQuery() → GraphQL 数据获取
        └── useProduct() / useOrderForm() → Store Framework 上下文钩子
```

## 严格约束

### 约束：为所有店面块声明接口

每个应作为 Store Framework 块使用的 React 组件必须在 `store/interfaces.json` 中具有相应的条目。如果没有接口声明，块无法在主题 JSON 文件中引用。

**为什么这很重要**

商店构建器通过 `interfaces.json` 将块名称解析为 React 组件。如果组件没有接口，它对 Store Framework 不可见，并且不会在店面上渲染。

**检测**

如果 `/react` 中的 React 组件打算用于店面，但在 `store/interfaces.json` 中没有匹配的条目，请警告开发者。该组件可以编译，但永远不会渲染。

**正确**

```json
{
  "product-reviews": {
    "component": "ProductReviews",
    "composition": "children",
    "allowed": ["product-review-item"]
  },
  "product-review-item": {
    "component": "ReviewItem"
  }
}
```

```tsx
// react/ProductReviews.tsx
import ProductReviews from './components/ProductReviews'

export default ProductReviews
```

**错误**

```tsx
// react/ProductReviews.tsx 存在，但没有 store/interfaces.json 条目
// 组件可以编译，但不能用于任何主题。
// 在主题 JSON 中添加 <product-reviews /> 将产生：
// "Block 'product-reviews' not found"
import ProductReviews from './components/ProductReviews'

export default ProductReviews
```

---

### 约束：使用 VTEX Styleguide 进行管理 UI

管理面板组件（使用 `admin` 构建的 app）必须使用 VTEX Styleguide（`vtex.styleguide`）进行 UI 元素。您 **不能** 在管理 app 中使用 Material UI、Chakra UI 或 Ant Design 等第三方 UI 库。

**为什么这很重要**

VTEX Admin 通过 Styleguide 强制执行一致的设计语言。第三方 UI 库会产生不一致的视觉效果，可能与 Admin 的全局 CSS 冲突，并增加不必要的捆绑包大小。提交到 VTEX App Store 且管理 UI 不是 Styleguide 的 app 将无法通过审核。

**检测**

如果您在管理 app 中看到来自 `@material-ui`、`@chakra-ui/react`、`@chakra-ui`、`antd` 或 `@ant-design` 的导入，请警告开发者使用 `vtex.styleguide`。

**正确**

```tsx
// react/admin/ReviewModeration.tsx
import React, { useState } from 'react'
import {
  Layout,
  PageHeader,
  Table,
  Button,
  Tag,
  Modal,
  Input,
} from 'vtex.styleguide'

interface Review {
  id: string
  author: string
  rating: number
  text: string
  status: 'pending' | 'approved' | 'rejected'
}

function ReviewModeration() {
  const [reviews, setReviews] = useState<Review[]>([])
  const [modalOpen, setModalOpen] = useState(false)

  const tableSchema = {
    properties: {
      author: { title: 'Author', width: 200 },
      rating: { title: 'Rating', width: 100 },
      text: { title: 'Review Text' },
      status: {
        title: 'Status',
        width: 150,
        cellRenderer: ({ cellData }: { cellData: string }) => (
          <Tag type={cellData === 'approved' ? 'success' : 'error'}>
            {cellData}
          </Tag>
        ),
      },
    },
  }

  return (
    <Layout fullWidth pageHeader={<PageHeader title="Review Moderation" />}>
      <Table
        items={reviews}
        schema={tableSchema}
        density="medium"
      />
    </Layout>
  )
}

export default ReviewModeration
```

**错误**

```tsx
// react/admin/ReviewModeration.tsx
import React from 'react'
import { DataGrid } from '@material-ui/data-grid'
import { Button } from '@material-ui/core'

// Material UI 组件在 VTEX Admin 中看起来不一致，
// 与全局样式冲突，并增加捆绑包大小。
// 此 app 将无法通过 VTEX App Store 审核。
function ReviewModeration() {
  return (
    <div>
      <DataGrid rows={[]} columns={[]} />
      <Button variant="contained" color="primary">Approve</Button>
    </div>
  )
}
```

---

### 约束：从 react/ 根级别导出组件

每个 Store Framework 块组件必须在 `/react` 目录中的根级别具有与 `interfaces.json` 中的 `"component"` 值匹配的导出文件。实际实现可以位于子目录中，但根文件必须存在。

**为什么这很重要**

react 构建器通过查找 `/react` 根目录中的文件来解析组件。如果 `interfaces.json` 声明 `"component": "ProductReviews"`，构建器查找 `react/ProductReviews.tsx`。如果没有此根导出文件，组件将无法找到，块将无法渲染。

**检测**

如果 `interfaces.json` 引用了没有在 `/react` 根目录中匹配文件名的组件名称，请停止并创建导出文件。

**正确**

```tsx
// react/ProductReviews.tsx — 根级别导出文件
import ProductReviews from './components/ProductReviews/index'

export default ProductReviews
```

```tsx
// react/components/ProductReviews/index.tsx — 实际实现
import React from 'react'
import { useCssHandles } from 'vtex.css-handles'

const CSS_HANDLES = ['container', 'title', 'list'] as const

interface Props {
  title: string
  maxReviews: number
}

function ProductReviews({ title, maxReviews }: Props) {
  const handles = useCssHandles(CSS_HANDLES)
  return (
    <div className={handles.container}>
      <h2 className={handles.title}>{title}</h2>
      {/* ... */}
    </div>
  )
}

export default ProductReviews
```

**错误**

```text
react/components/ProductReviews/index.tsx 存在，
但 react/ProductReviews.tsx 不存在。
构建器无法找到组件。
错误： "Could not find component ProductReviews"
```

## 推荐模式

在子目录中创建 React 组件：

```tsx
// react/components/ProductReviews/index.tsx
import React, { useMemo } from 'react'
import { useQuery } from 'react-apollo'
import { useProduct } from 'vtex.product-context'
import { useCssHandles } from 'vtex.css-handles'

import GET_REVIEWS from '../../graphql/getReviews.graphql'
import ReviewItem from './ReviewItem'

const CSS_HANDLES = [
  'reviewsContainer',
  'reviewsTitle',
  'reviewsList',
  'averageRating',
  'emptyState',
] as const

interface Props {
  title?: string
  showAverage?: boolean
  maxReviews?: number
}

function ProductReviews({
  title = 'Customer Reviews',
  showAverage = true,
  maxReviews = 10,
}: Props) {
  const handles = useCssHandles(CSS_HANDLES)
  const productContext = useProduct()
  const productId = productContext?.product?.productId

  const { data, loading, error } = useQuery(GET_REVIEWS, {
    variables: { productId, limit: maxReviews },
    skip: !productId,
  })

  const averageRating = useMemo(() => {
    if (!data?.reviews?.length) return 0

    const sum = data.reviews.reduce(
      (acc: number, review: { rating: number }) => acc + review.rating,
      0
    )

    return (sum / data.reviews.length).toFixed(1)
  }, [data])

  if (loading) return <div className={handles.reviewsContainer}>Loading...</div>
  if (error) return null

  return (
    <div className={handles.reviewsContainer}>
      <h2 className={handles.reviewsTitle}>{title}</h2>

      {showAverage && data?.reviews?.length > 0 && (
        <div className={handles.averageRating}>
          Average: {averageRating} / 5
        </div>
      )}

      {data?.reviews?.length === 0 ? (
        <p className={handles.emptyState}>No reviews yet.</p>
      ) : (
        <ul className={handles.reviewsList}>
          {data.reviews.map((review: { id: string; author: string; rating: number; text: string }) => (
            <ReviewItem key={review.id} review={review} />
          ))}
        </ul>
      )}
    </div>
  )
}

export default ProductReviews
```

根导出文件：

```tsx
// react/ProductReviews.tsx
import ProductReviews from './components/ProductReviews'

export default ProductReviews
```

块接口：

```json
{
  "product-reviews": {
    "component": "ProductReviews",
    "composition": "children",
    "allowed": ["product-review-form"],
    "render": "client"
  }
}
```

Site Editor 模式：

```json
{
  "definitions": {
    "ProductReviews": {
      "type": "object",
      "properties": {
        "title": {
          "type": "string",
          "title": "Section Title",
          "description": "显示在评论列表上方的标题",
          "default": "Customer Reviews"
        },
        "showAverage": {
          "type": "boolean",
          "title": "Show average rating",
          "default": true
        },
        "maxReviews": {
          "type": "number",
          "title": "Maximum reviews",
          "default": 10,
          "enum": [5, 10, 20, 50]
        }
      }
    }
  }
}
```

在 Store Framework 主题中使用组件：

```json
{
  "store.product": {
    "children": [
      "product-images",
      "product-name",
      "product-price",
      "buy-button",
      "product-reviews"
    ]
  },
  "product-reviews": {
    "props": {
      "title": "What Our Customers Say",
      "showAverage": true,
      "maxReviews": 20
    }
  }
}
```

## 常见失败模式

- **为管理 app 导入第三方 UI 库**：使用 `@material-ui/core`、`@chakra-ui/react` 或 `antd` 与 VTEX Admin 的全局 CSS 冲突，产生不一致的视觉效果，并将失败 App Store 审核。使用 `vtex.styleguide`。
- **从 React 组件直接调用 API**：使用 `fetch()` 或 `axios` 将身份验证令牌暴露给客户端并绕过 CORS 限制。使用 `react-apollo` 的 `useQuery` 从 GraphQL 查询进行服务器端解析。
- **没有国际化的硬编码字符串**：具有硬编码字符串的组件仅在一种语言中工作。使用 `messages` 构建器和 `react-intl` 进行国际化。
- **缺少根级别导出文件**：如果 `interfaces.json` 引用 `"component": "ProductReviews"` 但 `react/ProductReviews.tsx` 不存在，块将静默失败渲染。
- **内容持有组件 app 的 MAJOR 版本升级**：对发送 `store/contentSchemas.json` 的 app 进行 `vtex release major` 将使该 app 声明的所有块所保存的 Site Editor 编辑对解析器不可见，直到它们使用 `vtex.pages-graphql@2.x` 中的 `updateThemeIds` 变量迁移到新的 MAJOR 版本——参见 `vtex-io-storefront-theme-versioning`。尽可能使用 `patch` 或 `minor`，并在必要时遵循 `vtex-io-storefront-theme-versioning`。

## 审核清单

- [ ] 每个店面块是否在 `store/interfaces.json` 中有匹配的条目？
- [ ] 每个 `interfaces.json` 组件是否在 `/react` 中有根级别导出文件？
- [ ] 管理应用是否使用 `vtex.styleguide`（不使用第三方 UI 库）？
- [ ] 店面组件是否使用 `css-handles` 进行样式设置？
- [ ] 数据是否通过 GraphQL（`useQuery`）获取，而不是通过浏览器的直接 API 调用？
- [ ] 面向用户的字符串是否使用 `react-intl` 和 `messages` 构建器？
- [ ] 是否定义了 `contentSchemas.json` 以便 Site Editor 可编辑属性？
- [ ] 如果 app 发送 `store/contentSchemas.json`，是否已审查计划 MAJOR 版本升级对商家面的影响？

## 相关技能

- [`vtex-io-storefront-theme-versioning`](../vtex-io-storefront-theme-versioning/SKILL.md) — 当 app 发送 `store/contentSchemas.json` 且必须保留或迁移 Site Editor 内容的版本更改时使用。
- [`vtex-io-storefront-theme-app`](../vtex-io-storefront-theme-app/SKILL.md) — 当问题是消费者主题如何将这些块组合成页面时使用。

## 参考

- [Developing Custom Storefront Components](https://developers.vtex.com/docs/guides/vtex-io-documentation-developing-custom-storefront-components) — 构建 Store Framework 组件的指南
- [Interfaces](https://developers.vtex.com/docs/guides/vtex-io-documentation-interface) — 如何将块映射到 React 组件
- [React Builder](https://developers.vtex.com/docs/guides/vtex-io-documentation-react-builder) — React 构建器配置和目录结构
- [Making a Custom Component Available in Site Editor](https://developers.vtex.com/docs/guides/vtex-io-documentation-making-a-custom-component-available-in-site-editor) — contentSchemas.json 和 Site Editor 集成
- [Store Framework](https://developers.vtex.com/docs/guides/store-framework) — 基于块的店面系统概述
- [Using Components](https://developers.vtex.com/docs/guides/store-framework-using-components) — 如何在主题中使用原生和自定义组件
- [VTEX Styleguide](https://styleguide.vtex.com/) — 官方的 VTEX 管理组件库
