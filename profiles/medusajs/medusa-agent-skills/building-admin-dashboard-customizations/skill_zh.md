# Medusa Admin Dashboard 自定义

使用 Admin SDK 和 Medusa UI 组件为 Medusa Admin Dashboard 构建自定义 UI 扩展。

**注意：** "UI 路由" 是自定义管理员页面，与后端 API 路由（使用 building-with-medusa 技能）不同。

## 何时应用

**加载此技能用于任何管理员 UI 开发任务，包括：**
- 为产品/订单/客户页面创建小部件
- 构建自定义管理员页面
- 实现表单和模态框
- 使用表格或列表显示数据
- 在页面之间添加导航

**当出现以下情况时，也加载这些技能：**
- **building-with-medusa：** 构建管理员 UI 调用的后端 API 路由
- **building-storefronts：** 如果不是在管理员仪表板而是在店面上工作

## 关键：按需加载参考文件

**下方的快速参考不足以进行实现。** 您必须在编写该组件的代码之前加载相关的参考文件。

**根据您要实现的内容加载这些参考文件：**

- **创建小部件？** → 必须首先加载 `references/data-loading.md`
- **构建表单/模态框？** → 必须首先加载 `references/forms.md`
- **在表格/列表中显示数据？** → 必须首先加载 `references/display-patterns.md`
- **从大型数据集中选择？** → 必须首先加载 `references/table-selection.md`
- **添加导航？** → 必须首先加载 `references/navigation.md`
- **为组件添加样式？** → 必须首先加载 `references/typography.md`

**最低要求：** 在实现之前，加载至少 1-2 个与您的特定任务相关的参考文件。

## 何时使用此技能与 MedusaDocs MCP 服务器

**⚠️ 关键：在规划和实现时，应首先咨询此技能。**

**用于（主要来源）：**
- **规划** - 了解如何构建管理员 UI 功能的结构
- **组件模式** - 小部件、页面、表单、表格、模态框
- **设计系统** - 字体、颜色、间距、语义类
- **数据加载** - 关键的分离查询模式、缓存失效
- **最佳实践** - 正确与错误的模式（例如，在挂载时显示查询）
- **关键规则** - 不应该做什么（常见错误，如条件显示查询）

**用于 MedusaDocs MCP 服务器（次要来源）：**
- 特定组件属性签名（在您知道要使用哪个组件之后）
- 可用的部件区域列表
- JS SDK 方法详细信息
- 配置选项参考

**为什么技能优先：**
- 技能包含关键模式，如分离显示/模态查询，MCP 不强调这些模式
- 技能显示正确与错误的模式；MCP 显示可能实现的内容
- 规划需要理解模式，而不仅仅是 API 参考

## 关键设置规则

### SDK 客户端配置

**关键：** 始终使用确切的配置 - 不同的值会导致错误：

```tsx
// src/admin/lib/client.ts
import Medusa from "@medusajs/js-sdk"

export const sdk = new Medusa({
  baseUrl: import.meta.env.VITE_BACKEND_URL || "/",
  debug: import.meta.env.DEV,
  auth: {
    type: "session",
  },
})
```

### pnpm 用户专用

**关键：** 在编写任何代码之前，安装依赖项：

```bash
# 从仪表板查找确切版本
pnpm list @tanstack/react-query --depth=10 | grep @medusajs/dashboard
# 安装确切版本
pnpm add @tanstack/react-query@[exact-version]

# 如果使用导航（Link 组件）
pnpm list react-router-dom --depth=10 | grep @medusajs/dashboard
pnpm add react-router-dom@[exact-version]
```

**npm/yarn 用户：** 不要安装这些包 - 它们已经可用。

## 按优先级分类的规则

| 优先级 | 类别 | 影响 | 前缀 |
|----------|----------|--------|--------|
| 1 | 数据加载 | 关键 | `data-` |
| 2 | 设计系统 | 关键 | `design-` |
| 3 | 数据显示 | 高（包括关键价格规则） | `display-` |
| 4 | 字体 | 高 | `typo-` |
| 5 | 表单 & 模态框 | 中 | `form-` |
| 6 | 选择模式 | 中 | `select-` |

## 快速参考

### 1. 数据加载（关键）

- `data-sdk-always` - **始终使用 Medusa JS SDK 进行所有 API 请求** - 永远不要使用常规的 fetch()（缺少认证头会导致错误）
- `data-sdk-method-choice` - 使用现有 SDK 方法进行内置端点（`sdk.admin.product.list()`），使用 `sdk.client.fetch()` 进行自定义路由
- `data-display-on-mount` - 显示查询必须在挂载时加载（不能基于 UI 状态启用条件）
- `data-separate-queries` - 分离显示查询与模态框/表单查询
- `data-invalidate-display` - 在突变后使显示查询失效，而不仅仅是模态框查询
- `data-loading-states` - 始终显示加载状态（Spinner），而不是空状态
- `data-pnpm-install-first` - pnpm 用户必须在编码前安装 @tanstack/react-query

### 2. 设计系统（关键）

- `design-semantic-colors` - 始终使用语义颜色类（bg-ui-bg-base、text-ui-fg-subtle），永远不要硬编码
- `design-spacing` - 使用 px-6 py-4 作为部分填充，gap-2 用于列表，gap-3 用于项目
- `design-button-size` - 始终在部件和表格中使用 size="small" 的按钮
- `design-medusa-components` - 始终使用 Medusa UI 组件（Container、Button、Text），而不是原始 HTML

### 3. 数据显示（高）

- `display-price-format` - **关键**：Medusa 存储的价格保持原样（$49.99 = 49.99，不是以分为单位）。直接显示它们 - 永远不要除以 100

### 4. 字体

- `typo-text-component` - 始终使用来自 @medusajs/ui 的 Text 组件，而不是普通的 span/p 标签
- `typo-labels` - 使用 `<Text size="small" leading="compact" weight="plus">` 用于标签/标题
- `typo-descriptions` - 使用 `<Text size="small" leading="compact" className="text-ui-fg-subtle">` 用于描述
- `typo-no-heading-widgets` - 在小部件中永远不要使用 Heading（使用 Text 代替）

### 5. 表单 & 模态框（中）

- `form-focusmodal-create` - 使用 FocusModal 创建新实体
- `form-drawer-edit` - 使用 Drawer 编辑现有实体
- `form-disable-pending` - 在突变期间始终禁用操作（disabled={mutation.isPending}）
- `form-show-loading` - 在提交按钮上显示加载状态（isLoading={mutation.isPending}）

### 6. 选择模式（中）

- `select-small-datasets` - 使用 Select 组件用于 2-10 个选项（状态、类型等）
- `select-large-datasets` - 使用 DataTable 与 FocusModal 用于大型数据集（产品、类别等）
- `select-search-config` - 必须传递搜索配置给 useDataTable 以避免“搜索未启用”错误

## 关键数据加载模式

**始终遵循此模式 - 永远不要有条件地加载显示数据：**

```tsx
// ✅ 正确 - 分离具有适当职责的查询
const RelatedProductsWidget = ({ data: product }) => {
  const [modalOpen, setModalOpen] = useState(false)

  // 显示查询 - 在挂载时加载
  const { data: displayProducts } = useQuery({
    queryFn: () => fetchSelectedProducts(selectedIds),
    queryKey: ["related-products-display", product.id],
    // 没有 'enabled' 条件 - 立即加载
  })

  // 模态框查询 - 当需要时加载
  const { data: modalProducts } = useQuery({
    queryFn: () => sdk.admin.product.list({ limit: 10, offset: 0 }),
    queryKey: ["products-selection"],
    enabled: modalOpen, // 对于仅模态框数据是 OK 的
  })

  // 具有适当失效的突变
  const updateProduct = useMutation({
    mutationFn: updateFunction,
    onSuccess: () => {
      // 使显示数据查询失效以刷新 UI
      queryClient.invalidateQueries({ queryKey: ["related-products-display", product.id] })
      // 还使实体查询失效
      queryClient.invalidateQueries({ queryKey: ["product", product.id] })
      // 注意：不需要使模态框选择查询失效
    },
  })

  return (
    <Container>
      {/* 显示使用 displayProducts */}
      {displayProducts?.map(p => <div key={p.id}>{p.title}</div>)}

      <FocusModal open={modalOpen} onOpenChange={setModalOpen}>
        {/* 模态框使用 modalProducts */}
      </FocusModal>
    </Container>
  )
}

// ❌ 错误 - 单个查询具有条件加载
const BrokenWidget = ({ data: product }) => {
  const [modalOpen, setModalOpen] = useState(false)

  const { data } = useQuery({
    queryFn: () => sdk.admin.product.list(),
    enabled: modalOpen, // ❌ 页面刷新时显示会中断!
  })

  // 尝试从模态框查询显示
  const displayItems = data?.filter(item => ids.includes(item.id)) // 直到模态框打开都没有数据

  return <div>{displayItems?.map(...)}</div> // 挂载时为空！
}
```

**为什么这很重要：**
- 页面刷新时，模态框关闭，因此条件查询不会运行
- 用户看到的是空状态，而不是他们的数据
- 显示依赖于模态框交互（错误的 UX）

## 常见错误检查清单

在实现之前，请验证您没有执行以下操作：

**数据加载：**
- [ ] 使用常规的 fetch() 而不是 Medusa JS SDK（会导致缺少认证头错误）
- [ ] 不使用现有 SDK 方法进行内置端点（例如，使用 sdk.client.fetch("/admin/products") 而不是 sdk.admin.product.list()）
- [ ] 基于模态框/UI 状态有条件地加载显示数据
- [ ] 使用单个查询用于显示和模态框
- [ ] 忘记在突变后使显示查询失效
- [ ] 不处理加载状态（显示空状态而不是 Spinner）
- [ ] pnpm 用户：在编码前没有安装 @tanstack/react-query

**设计系统：**
- [ ] 使用硬编码颜色而不是语义类
- [ ] 忘记在部件中的按钮使用 size="small"
- [ ] 忘记使用 px-6 py-4 作为部分填充
- [ ] 使用原始 HTML 元素而不是 Medusa UI 组件

**数据显示：**
- [ ] **关键**：在显示时除以 100 价格（价格存储为原样：$49.99 = 49.99，不是以分为单位）

**字体：**
- [ ] 使用普通的 span/p 标签而不是 Text 组件
- [ ] 不使用 weight="plus" 用于标签
- [ ] 不使用 text-ui-fg-subtle 用于描述
- [ ] 在小部件部分中使用 Heading

**表单：**
- [ ] 使用 Drawer 创建（应该使用 FocusModal）
- [ ] 使用 FocusModal 编辑（应该使用 Drawer）
- [ ] 在突变期间不禁用按钮
- [ ] 不在提交时显示加载状态

**选择：**
- [ ] 使用 DataTable 用于 <10 个项目（过度）
- [ ] 使用 Select 用于 >10 个项目（糟糕的 UX）
- [ ] 未在 useDataTable 中配置搜索（会导致错误）

## 可用的参考文件

加载这些以获取详细模式：

```
references/data-loading.md       - useQuery/useMutation 模式，缓存失效
references/forms.md              - FocusModal/Drawer 模式，验证
references/table-selection.md    - 完整的 DataTable 选择模式
references/display-patterns.md   - 实体的列表、表格、卡片
references/typography.md         - Text 组件模式
references/navigation.md         - Link、useNavigate、useParams 模式
```

每个参考文件包含：
- 分步实现指南
- 正确与错误的代码示例
- 常见错误和解决方案
- 完整的工作示例

## 与后端的集成

**⚠️ 关键：始终使用 Medusa JS SDK 进行所有 API 请求 - 永远不要使用常规的 fetch()**

管理员 UI 使用 SDK 连接到后端 API 路由：

```tsx
import { sdk } from "[LOCATE SDK INSTANCE IN PROJECT]"

// ✅ 正确 - 内置端点：使用现有的 SDK 方法
const { data: product } = useQuery({
  queryKey: ["product", productId],
  queryFn: () => sdk.admin.product.retrieve(productId),
})

// ✅ 正确 - 自定义端点：使用 sdk.client.fetch()
const { data: reviews } = useQuery({
  queryKey: ["reviews", product.id],
  queryFn: () => sdk.client.fetch(`/admin/products/${product.id}/reviews`),
})

// ❌ 错误 - 使用常规的 fetch
const { data } = useQuery({
  queryKey: ["reviews", product.id],
  queryFn: () => fetch(`http://localhost:9000/admin/products/${product.id}/reviews`),
  // ❌ 错误：缺少 Authorization 头！
})

// 自定义后端路由的突变
const createReview = useMutation({
  mutationFn: (data) => sdk.client.fetch("/admin/reviews", {
    method: "POST",
    body: data
  }),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ["reviews", product.id] })
    toast.success("Review created")
  },
})
```

**为什么需要 SDK：**
- 管理员路由需要 `Authorization` 和会话 cookie 头
- 店铺路由需要 `x-publishable-api-key` 头
- SDK 自动处理所有必需的头
- 常规的 fetch() 而没有头 → 认证/授权错误
- 使用现有的 SDK 方法提供更好的类型安全性

**何时使用什么：**
- **内置端点**：使用现有的 SDK 方法（`sdk.admin.product.list()`、`sdk.store.product.list()`）
- **自定义端点**：使用 `sdk.client.fetch()` 用于您的自定义 API 路由

**对于实现后端 API 路由**，加载 `building-with-medusa` 技能。

## 小部件与 UI 路由

**小部件**扩展现有的管理员页面：

```tsx
// src/admin/widgets/custom-widget.tsx
import { defineWidgetConfig } from "@medusajs/admin-sdk"
import { DetailWidgetProps } from "@medusajs/framework/types"

const MyWidget = ({ data }: DetailWidgetProps<HttpTypes.AdminProduct>) => {
  return <Container>Widget content</Container>
}

export const config = defineWidgetConfig({
  zone: "product.details",
})

export default MyWidget
```

**⚠️ `.before` / `.after` 现在不再控制位置（v2.17.2+）：**

由于布局作曲家的出现，管理员用户通过仪表板的编辑视图排列组件（包括小部件），并且排列保存在数据库中。`.before` 和 `.after` 区域后缀已**弃用**：`product.details.before` 和 `product.details.after` 中的小部件位于同一注入区域，最终顺序是用户在编辑视图中配置的。

- 不要基于后缀向用户承诺特定的位置。说“小部件出现在产品详情页面，可以在编辑视图中重新定位”。
- `.side` 仍然有意义——它针对两列页面布局的侧列。
- 对于新小部件，除非项目已经标准化使用后缀，否则请优先使用无后缀的区域（例如 `product.details`）。

v2.16.0 中添加的新区域涵盖了草稿订单、礼品卡和店铺信用账户（`draft_order.*`、`gift_card.*`、`store_credit_account.*`，在 `details`/`list`/`side` 变体中）。询问 MedusaDocs MCP 服务器以获取权威的区域列表，而不是猜测区域名称。

**UI 路由**创建新的管理员页面：

```tsx
// src/admin/routes/custom-page/page.tsx
import { defineRouteConfig } from "@medusajs/admin-sdk"

const CustomPage = () => {
  return <div>Page content</div>
}

export const config = defineRouteConfig({
  label: "Custom Page",
})

export default CustomPage
```

**浏览器标签标题（v2.17.2+）：** 默认情况下，UI 路由的标签标题是其 `label`。导出一个 `handle` 与 `seo` 解析器来覆盖它，包括从路由的 `loader` 数据动态获取：

```tsx
// src/admin/routes/brands/[id]/page.tsx
import { UIMatch } from "react-router-dom"

export const handle = {
  seo: (match: UIMatch<BrandResponse>) => ({
    title: match.loaderData?.brand.name || "Brand",
  }),
}
```

如果 `seo` 返回没有标题，仪表板会回退到侧边栏标签，然后是面包屑，然后是 `Medusa`。

**自定义注入区域（v2.16.0+）：** 自定义页面——最常用的是在插件中——可以通过使用 `@medusajs/dashboard/components` 的 `LayoutComposer` 布局页面来暴露它们自己的部件注入区域：

```tsx
import { LayoutComposer } from "@medusajs/dashboard/components"

const BrandDetailsPage = () => (
  <LayoutComposer
    widgetsZonePrefix="brand.details"   // 暴露 "brand.details" 和 "brand.details.side"
    preferredLayoutId="core:two-column"
    data={brand}                        // 传递给小部件作为他们的 `data` 属性
    sections={{ main: <GeneralSection brand={brand} />, side: <MediaSection brand={brand} /> }}
  />
)
```

- 名称区域 `{resource}.{page-context}`（例如 `brand.list`、`brand.details`），加上 `.side` 用于侧部分。**永远**不要添加 `.before`/`.after`。
- 在 `InjectionZoneRegistry` 接口注册区域以进行类型检查和 `defineWidgetConfig` 中的自动完成，并在 `src/admin/tsconfig.json` 的 `include` 数组中包含 `"../../.medusa/types/augmentation-refs.d.ts"`。
- 对于自定义区域，预期会收到关于未知区域的构建警告——验证区域名称是否拼写正确，而不是盲目忽略。

## 常见问题及解决方案

**"找不到模块" 错误（pnpm 用户）：**
- 在编码前安装依赖项
- 使用仪表板上的确切版本

**"未设置 QueryClient" 错误：**
- pnpm：安装 @tanstack/react-query
- npm/yarn：删除错误安装的包

**"DataTable.Search 未启用"：**
- 必须向 useDataTable 传递搜索配置

**小部件未刷新：**
- 使显示查询失效，而不仅仅是模态框查询
- 在查询键中包含所有依赖项

**刷新时显示为空：**
- 显示查询基于 UI 状态有条件地加载
- 移除条件 - 显示数据必须在挂载时加载

## 下一步 - 测试您的实现

**在成功实现功能后，始终向用户提供以下步骤：**

### 1. 启动开发服务器

如果服务器尚未运行，请启动它：

```bash
npm run dev      # 或 pnpm dev / yarn dev
```

### 2. 访问管理员仪表板

在浏览器中打开并导航到：
- **管理员仪表板：** http://localhost:9000/app

使用您的管理员凭据登录。

### 3. 导航到您的自定义 UI

**对于小部件：**
导航到显示您的小部件的页面。常见的部件区域：
- **产品小部件：** 前往产品 → 选择一个产品 → 您的小部件出现在页面上
- **订单小部件：** 前往订单 → 选择一个订单 → 您的小部件出现在页面上
- **客户小部件：** 前往客户 → 选择一个客户 → 您的小部件出现在页面上

小部件在页面中的确切位置由用户在仪表板的编辑视图（布局作曲家）中控制，而不是由区域的 `.before`/`.after` 后缀控制。告诉用户他们可以将小部件拖到他们想要的位置。

**对于 UI 路由（自定义页面）：**
- 在管理员侧边栏/导航中查找您的自定义页面（基于您配置的 `label`）
- 或者直接导航到：`http://localhost:9000/app/[your-route-path]`

### 4. 测试功能

根据实现的内容测试：
- **表单：** 尝试创建/编辑实体，验证验证和错误消息
- **表格：** 测试分页、搜索、排序和行选择
- **数据显示：** 验证数据正确加载并在突变后刷新
- **模态框：** 打开 FocusModal/Drawer，测试表单提交，验证数据更新
- **导航：** 点击链接并验证路由是否正确工作

### 呈现下一步的格式

在实现后，始终以清晰、可操作的形式呈现下一步：

```markdown
## 实现完成

[功能名称] 已成功实现。以下是查看它的方法：

### 启动开发服务器
[基于包管理器的命令]

### 访问管理员仪表板
在浏览器中打开 http://localhost:9000/app 并登录。

### 查看您的自定义 UI

**对于小部件：**
1. 导航到 [特定管理员页面，例如，“产品”]
2. 选择 [一个实体，例如，“任何产品”]
3. 滚动到 [区域位置，例如，“页面的底部”]
4. 您将看到您的 "[小部件名称]" 小部件

**对于 UI 路由：**
1. 在管理员导航中查找 "[页面标签]"
2. 或者直接导航到 http://localhost:9000/app/[route-path]

### 需要测试的内容
1. [特定测试用例 1]
2. [特定测试用例 2]
3. [特定测试用例 3]
```
