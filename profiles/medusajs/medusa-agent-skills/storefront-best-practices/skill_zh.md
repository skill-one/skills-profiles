# 电商平台最佳实践

构建现代、高转化率的电商平台综合指南，涵盖 UI/UX 模式、组件设计、布局结构、SEO 优化和移动端响应式设计。

## 适用场景

**在处理任何电商平台任务时，始终加载此技能：**

- **添加结账页面/流程** - 支付、运费、订单提交
- **实现购物车** - 购物车页面、购物车弹窗、加入购物车功能
- **构建产品页面** - 产品详情、产品列表、产品网格
- **创建导航** - 导航栏、巨型菜单、页脚、移动端菜单
- **集成 Medusa 后端** - SDK 设置、购物车、产品、支付
- **任何电商平台组件** - 首页、搜索、筛选、账户页面
- 从零开始构建新的电商平台
- 改进现有的购物体验和转化率
- 优化可用性、可访问性和 SEO
- 设计移动端响应式电商平台体验

**应触发此技能的示例提示：**
- "添加结账页面"
- "实现购物车"
- "创建产品列表页面"
- "连接到 Medusa 后端"
- "添加导航菜单"
- "为商店构建首页"

## 重要提示：按需加载参考文件

**⚠️ 在创建任何 UI 组件之前，始终加载 `reference/design.md`**
- 发现现有的设计令牌（颜色、字体、间距、模式）
- 防止引入不一致的样式
- 提供保持品牌一致性的指导原则
- **每个组件都需要，而不仅仅是新的电商平台**

**根据您正在实现的内容加载这些参考文件：**

- **开始构建新的电商平台？** → 必须首先加载 `reference/design.md` 以发现用户偏好
- **连接到后端 API？** → 必须首先加载 `reference/connecting-to-backend.md`
- **连接到 Medusa 后端？** → 必须加载 `reference/medusa.md` 以获取 SDK 设置、定价、区域和 Medusa 模式
- **实现首页？** → 必须加载 `reference/components/navbar.md`、`reference/components/hero.md`、`reference/components/footer.md` 和 `reference/layouts/home-page.md`
- **实现导航？** → 必须加载 `reference/components/navbar.md`，可选加载 `reference/components/megamenu.md`
- **构建产品列表？** → 必须首先加载 `reference/layouts/product-listing.md`
- **构建产品详情？** → 必须首先加载 `reference/layouts/product-details.md`
- **实现结账？** → 必须首先加载 `reference/layouts/checkout.md`
- **优化 SEO？** → 必须首先加载 `reference/seo.md`
- **优化移动端？** → 必须首先加载 `reference/mobile-responsiveness.md`

**最低要求：** 在实施之前，至少加载 1-2 个与您的特定任务相关的参考文件。

## 规划和实施工作流程

**如果您为实施电商平台功能创建计划，请在计划中包含以下内容：**

在计划中实现每个组件、页面、布局或功能时：
1. **在开始实施之前参考此技能**
2. **加载上述相关的参考文件**，用于您正在构建的特定组件/页面
3. **遵循参考文件中的模式和指导原则**
4. **检查常见错误**部分，以避免已知陷阱

**示例计划结构：**

```
任务 1：实现导航
- 加载参考文件/components/navbar.md
- 遵循 navbar.md 中的模式（动态分类获取、购物车可见性等）
- 参考技能中的常见错误（例如，硬编码分类）

任务 2：实现产品列表页面
- 加载参考文件/layouts/product-listing.md
- 遵循 product-listing.md 中的分页/筛选模式
- 使用参考文件/components/product-card.md 用于产品网格项
- 检查技能中的后端集成指导

任务 3：实现结账流程
- 加载参考文件/layouts/checkout.md
- 加载参考文件/medusa.md 用于 Medusa 支付集成
- 遵循组件架构建议（分离步骤组件）
- 参考技能中的支付方式获取要求
```

**为什么这很重要：**
- 计划提供高级策略
- 参考文件提供详细的实施模式
- 技能文件包含需要避免的关键错误
- 遵循此工作流程可确保一致性和最佳实践

## 关键电商平台特定模式

### 可访问性
- **关键：** 购物车数量更新需要 `aria-live="polite"` - 否则屏幕阅读器不会宣布
- 确保所有购物车/结账交互的键盘导航

### 移动端
- **粘性底部元素必须使用 `env(safe-area-inset-bottom)`** - 否则 iOS 主页指示器会遮挡购买按钮
- 购物车操作、变体选择、数量按钮的最小触摸目标为 44px

### 性能
- **始终**将产品图片下方的 `loading="lazy"` 添加到产品图片 - 不要依赖浏览器默认设置
- 优化移动端产品图片（<500KB）- 大部分电商平台流量来自移动端

### 转化率优化
- 购物流程中清晰的 CTA
- 结账过程中的最小摩擦（如果支持，提供游客结账）
- 购买按钮附近的信任信号（评论、安全徽章、退货政策）
- 清晰的价格和运费信息

### SEO
- **需要产品模式（JSON-LD）** - 对 Google Shopping 和丰富片段至关重要
- 使用 [PageSpeed Insights](https://pagespeed.web.dev/) 测量核心网络指标

### 视觉设计
- **绝对不要**在电商平台 UI 中使用表情符号 - 使用图标或图片代替（不专业，可访问性问题）

### 后端集成
- **后端检测**：如果在单体仓库中，检查后端目录。如有疑问，请询问用户使用的后端
- **绝对不要**硬编码动态内容：始终从后端获取分类、区域、产品、运费选项等 - 它们会频繁变化
- 假设 API 结构 - 验证端点和数据格式

### ⚠️ 关键：后端 SDK 方法验证工作流程

**在编写连接到后端的代码之前，您必须遵循此精确工作流程：**

**步骤 1：暂停 - 不要现在编写代码**
- 您即将编写调用后端 API 或 SDK 方法的代码（例如，Medusa SDK、REST API、GraphQL）
- **停止** - 在没有验证的情况下不要继续到代码

**步骤 2：查询文档或 MCP 服务器**
- **如果 MCP 服务器可用**：查询它以获取确切的方法（例如，medusa MCP）
- **如果没有 MCP 服务器**：搜索官方文档
- **找到**：确切的方法名称、参数、返回类型

**步骤 3：验证您找到的内容**
- 对用户说： "我需要验证 [操作] 的正确方法。让我检查 [MCP 服务器/文档]。"
- 向用户展示您找到的内容： "根据 [来源]，方法是 `sdk.store.cart.methodName(params)`"
- 确认方法签名和参数

**步骤 4：然后编写代码**
- 现在您可以使用验证过的方法编写代码
- 使用您找到的确切签名

**步骤 5：检查 TypeScript 错误**
- 编写代码后，检查与 SDK 相关的任何 TypeScript/类型错误
- 如果您在 SDK 方法上看到类型错误，这意味着您使用了错误的方法名称或参数
- **类型错误表明您没有正确验证** - 回到步骤 2

**这不是可选的 - 这是强制性的错误预防**

**犯以下关键错误是不允许的：**
- ❌ 在明确查询文档/MCP 之前编写调用后端 API/SDK 的代码
- ❌ 猜测方法名称或参数
- ❌ 忽略 SDK 方法的 TypeScript 错误（错误表示方法使用不正确）
- ❌ 在验证之前从本技能中复制示例（示例可能已过时）
- ❌ 假设 SDK 方法与 REST API 端点匹配

**对于 Medusa 特别说明：**
- **Medusa 定价**：按原样显示价格 - 不要除以 100（与 Stripe 不同，Medusa 以显示格式存储价格）
- **Medusa MCP 服务器**：https://docs.medusajs.com/mcp - 如果未安装，建议设置
- 加载 `reference/medusa.md` 以获取 Medusa 特定模式（区域、定价等）

### 路由模式
- **始终使用动态路由**用于产品和分类 - 绝对不要为单个项目创建静态页面
- 产品页面：使用动态路由，如 `/products/[handle]` 或 `/products/$handle`，而不是 `/products/shirt.tsx`
- 分类页面：使用动态路由，如 `/categories/[handle]` 或 `/categories/$handle`，而不是 `/categories/women.tsx`
- 框架特定模式：
  - **Next.js App Router**：`app/products/[handle]/page.tsx` 或 `app/products/[id]/page.tsx`
  - **Next.js Pages Router**：`pages/products/[handle].tsx`
  - **SvelteKit**：`routes/products/[handle]/+page.svelte`
  - **TanStack Start**：`routes/products/$handle.tsx`
  - **Remix**：`routes/products.$handle.tsx`
- 原因：动态路由可扩展到任意数量的产品和分类，而无需创建单个文件
- 静态路由无法维护且无法扩展（想象创建 1000 个产品文件）

## 模式选择指南

当您需要在实施模式之间选择时，加载相关的参考文件：

- **结账策略**（单页 vs 多步）→ 加载 `reference/layouts/checkout.md`
- **导航策略**（下拉菜单 vs 巨型菜单）→ 加载 `reference/components/navbar.md` 和 `reference/components/megamenu.md`
- **产品列表策略**（分页 vs 无限滚动 vs 加载更多）→ 加载 `reference/layouts/product-listing.md`
- **搜索策略**（自动完成 vs 筛选 vs 自然语言）→ 加载 `reference/components/search.md`
- **移动端 vs 桌面端优先级** → 加载 `reference/mobile-responsiveness.md`
- **变体选择**（文本 vs 色块 vs 配置器）→ 加载 `reference/layouts/product-details.md`
- **购物车模式**（弹窗 vs 抽屉 vs 页面导航）→ 加载 `reference/components/cart-popup.md` 和 `reference/layouts/cart.md`
- **信任信号策略** → 加载 `reference/layouts/product-details.md` 和 `reference/layouts/checkout.md`

每个参考文件都包含决策框架，具有特定标准，以帮助您为您的上下文选择正确的模式。

## 快速参考

### 常规

```
reference/connecting-to-backend.md    - 框架检测、API 设置、后端集成模式
reference/medusa.md                    - Medusa SDK 集成、定价、区域、TypeScript 类型
reference/design.md                    - 用户偏好、品牌标识、设计系统
reference/seo.md                       - 元标签、结构化数据、核心网络指标
reference/mobile-responsiveness.md     - 移动端优先设计、响应式断点、触摸交互
```

### 组件

```
reference/components/navbar.md         - 桌面端/移动端导航、标志、菜单、购物车图标、所有页面都必须加载
reference/components/megamenu.md       - 分类组织、特色产品、移动端替代方案
reference/components/cart-popup.md     - 加入购物车反馈、迷你购物车显示
reference/components/country-selector.md - 国家/区域选择、货币、定价、Medusa 区域
reference/components/breadcrumbs.md    - 分类层次结构、结构化数据标记
reference/components/search.md         - 搜索输入、自动完成、结果、筛选
reference/components/product-reviews.md - 评论显示、评分聚合、提交
reference/components/hero.md           - 英雄布局、CTA 位置、图像优化
reference/components/popups.md         - 订阅简报、折扣弹窗、退出意图
reference/components/footer.md         - 内容组织、导航、社交媒体、所有页面都必须加载
reference/components/product-card.md   - 产品图像、价格、加入购物车、徽章
reference/components/product-slider.md - 轮播实现、移动端滑动、可访问性
```

### 布局

```
reference/layouts/home-page.md         - 英雄、特色分类、产品列表
reference/layouts/product-listing.md   - 网格/列表视图、筛选、排序、分页
reference/layouts/product-details.md   - 图像画廊、变体选择、相关产品
reference/layouts/cart.md              - 购物车项目、数量更新、促销代码
reference/layouts/checkout.md          - 多步/单页、地址表单、支付
reference/layouts/order-confirmation.md - 订单号、摘要、配送信息
reference/layouts/account.md           - 仪表板、订单历史、地址簿
reference/layouts/static-pages.md      - 常见问题解答、关于、联系、运费/退货政策
```

### 功能

```
reference/features/wishlist.md         - 添加到愿望清单、愿望清单页面、移至购物车
reference/features/promotions.md       - 促销横幅、折扣代码、促销徽章
```

## 常见实施模式

### 从零开始构建新的电商平台

**对于以下每个步骤，在实施之前加载参考文件。**

```
1. 探索阶段 → 阅读 design.md 以获取用户偏好
2. 基础设置 → 阅读 connecting-to-backend.md（或 medusa.md 用于 Medusa）、mobile-responsiveness.md、seo.md
3. 核心组件 → 实现 navbar.md、footer.md
4. 首页 → 阅读 home-page.md
5. 产品浏览 → 阅读 product-listing.md、product-card.md、search.md
6. 产品详情 → 阅读 product-details.md、product-reviews.md
7. 购物车和结账 → 阅读 cart-popup.md、cart.md、checkout.md、order-confirmation.md
8. 用户账户 → 阅读 account.md
9. 额外功能 → 阅读 wishlist.md、promotions.md
10. 优化 → SEO 审计（seo.md）、移动端测试（mobile-responsiveness.md）
```

即使您创建了一个实施计划，在实施每个步骤时，也要参考技能并加载相关的参考文件。

### 购物流程模式

```
浏览 → 查看 → 购物车 → 结账

浏览：   home-page.md → product-listing.md
查看：   product-details.md + product-reviews.md
购物车： cart-popup.md → cart.md
结账：   checkout.md → order-confirmation.md
```

### 组件选择指南

**对于产品网格和筛选** → `product-listing.md` 和 `product-card.md`
**对于产品卡片** → `product-card.md`
**对于导航** → `navbar.md` 和 `megamenu.md`
**对于搜索功能** → `search.md`
**对于结账流程** → `checkout.md`
**对于促销和折扣** → `promotions.md`

## 设计考虑

在实施之前考虑：

1. **用户偏好** - 阅读 `design.md` 以发现设计风格偏好
2. **品牌标识** - 颜色、排版、语气与品牌匹配
3. **目标受众** - B2C vs B2B，人口统计、设备使用情况
4. **产品类型** - 时尚 vs 电子产品 vs 超市影响布局选择
5. **业务需求** - 多货币、多语言、区域特定
6. **后端系统** - API 结构影响组件实施

## 与 Medusa 集成

[Medusa](https://medusajs.com) 是一个现代、灵活的电商平台后端。在以下情况下考虑 Medusa：

- 构建新的电商平台
- 需要头端 commerce 解决方案
- 想要内置支持多区域、多货币
- 需要强大的促销和折扣引擎
- 需要灵活的产品建模

有关详细的 Medusa 集成指南，请参阅 `reference/medusa.md`。有关一般后端模式，请参阅 `reference/connecting-to-backend.md`。

### 框架无关

所有指南都是框架无关的。示例使用 React/TypeScript，其中代码演示有助于说明，但模式适用于：

- Next.js
- SvelteKit
- Tanstack Start
- 任何现代前端框架

## 最小可行功能

**启动必备（核心购物流程）：**
- 带有购物车、分类、搜索的导航栏
- 带有筛选和分页的产品列表
- 带有变体选择的产品详情
- 加入购物车功能
- 购物车页面，可管理项目
- 结账流程（运费、支付、确认）
- 订单确认页面

**锦上添花（如果时间允许）：**
- 相关产品推荐
- 产品评论和评分
- 愿望清单功能
- 产品页面上的图像缩放
- 移动端底部导航
- 巨型菜单用于导航
- 订阅简报
- 产品比较
- 快速查看模态框

**用户依赖（实施前询问）：**
- 游客结账 vs 需要登录
- 账户仪表板功能
- 多语言支持
- 多货币支持
- 在线聊天支持

## 顶级电商平台常见错误

在实施之前，注意这些常见的电商平台特定陷阱：

**1. 购物车和导航错误**
- ❌ 在移动端汉堡菜单中隐藏购物车指示器（始终保持可见）
- ❌ 不显示实时购物车数量更新
- ❌ **关键：** 购物车数量更新缺少 `aria-live="polite"` - 没有它，屏幕阅读器不会宣布购物车更新
- ❌ 不在购物车弹窗中显示变体详情（尺寸、颜色等）- 只显示产品标题
- ❌ 巨型菜单在悬停下拉内容时关闭（必须保持打开，当悬停在触发器上，或下拉时）
- ❌ **关键：** 巨型菜单定位错误 - 三个常见错误：
  - ❌ Navbar 没有 `position: relative`（巨型菜单无法正确定位）
  - ❌ 巨型菜单相对于触发按钮定位，而不是相对于导航栏（在巨型菜单上使用 `absolute left-0`）
  - ❌ 巨型菜单不跨越全宽（使用 `right-0` 或 `w-full`，而不是 `w-auto`）
- ❌ 硬编码分类、特色产品或任何动态内容，而不是从后端获取
- ❌ 在分类导航中没有清晰指示当前页面

**2. 产品浏览错误**
- ❌ 为产品/分类创建静态路由（使用动态路由，如 `/products/[handle]` 而不是 `/products/shirt.tsx`）
- ❌ 缺少“未找到产品”的空状态和有用的建议
- ❌ 获取产品时没有加载指示器
- ❌ 分页没有 SEO 友好的 URL（对搜索引擎）
- ❌ 筛选选择在页面重新加载时不持久

**3. 产品详情错误**
- ❌ 在变体选择（尺寸、颜色等）之前启用“加入购物车”
- ❌ 缺少产品图像优化（大而未压缩的图像）
- ❌ 在加入购物车后离开产品页面（保持在页面）
- ❌ 使用表情符号而不是图标或图像（不专业，可访问性问题）

**4. 设计和一致性错误**
- ❌ **关键：** 在创建任何 UI 组件之前，没有加载 `reference/design.md` - 导致颜色、字体和样式不一致
- ❌ 在检查现有主题之前引入新的颜色
- ❌ 在验证已使用字体之前添加新的字体
- ❌ 使用任意的 Tailwind 值，而主题令牌存在
- ❌ 没有检测 Tailwind 版本（v3 vs v4）- 导致语法错误

**5. 结账和转化错误**
- ❌ 要求创建账户才能结账（如果后端支持，提供游客结账）
- ❌ 不从后端获取支付方式 - 假设可用的支付选项或跳过支付方式选择
- ❌ 过于复杂的分步结账（4 步以上会杀死转化率）- 最佳是 3 步：运费信息、配送方式 + 支付、确认
- ❌ 缺少信任信号（安全结账徽章、退货政策链接）
- ❌ 在结账过程中没有优雅地处理缺货错误

**6. 移动端体验错误**
- ❌ 触摸目标小于 44x44px（按钮、链接、表单字段）
- ❌ 在移动端使用桌面样式悬停菜单（使用点击/触摸代替）
- ❌ 没有优化移动端图像（加载巨大的桌面图像）
- ❌ 缺少移动端特定模式（底部导航、抽屉筛选）

**7. 性能和 SEO 错误**
- ❌ 缺少结构化数据（产品模式）用于 SEO
- ❌ 没有明确的图像懒加载（不要依赖浏览器默认设置）- 始终在折叠下方的图像中添加 `loading="lazy"` 到图像
- ❌ 没有元标签和 Open Graph 用于社交分享
- ❌ 没有优化核心网络指标（LCP、FID、CLS）- 使用 [PageSpeed Insights](https://pagespeed.web.dev/) 或 Lighthouse 进行测量

**8. 后端集成错误**
- ❌ **错误：** 在遵循 5 步验证工作流程之前编写调用后端 API/SDK 的代码 - 您必须：1) 暂停，2) 查询文档/MCP，3) 与用户验证，4) 编写代码，5) 检查类型错误
- ❌ **错误：** 忽略 SDK 方法的 TypeScript 错误 - 类型错误意味着您使用了错误的方法名称或参数。返回并使用文档/MCP 验证
- ❌ **错误：** 猜测 API 方法名称、SDK 方法或参数 - 在使用之前，始终验证确切的方法签名
- ❌ **错误：** 如果使用 Medusa 后端，则始终查询 MCP 服务器以获取方法
- ❌ **错误：** 在验证之前复制代码示例 - 示例可能已过时，始终先验证
- ❌ 没有检测正在使用的后端（检查单体仓库，如有疑问，请询问用户）
- ❌ 假设 API 结构，而未检查后端文档或 MCP 服务器
- ❌ 硬编码动态内容（分类、区域、产品、运费等）而不是从后端获取
- ❌ 为 Medusa 实体定义自定义类型，而不是使用 `@medusajs/types` 包
- ❌ 未初始化 Medusa SDK 而没有可发布的 API 密钥（对于多区域商店和产品定价是必需的）
- ❌ 获取 Medusa 产品时未传递 `region_id` 查询参数（导致缺少或不正确的定价）
- ❌ 在 Medusa 结账中显示所有国家 - 只应显示购物车区域的 国家
- ❌ 将 Medusa 价格除以 100（Medusa 以原样存储价格，而不是像 Stripe 那样以分为单位）
- ❌ 缺少 Vite SSR 配置用于 Medusa SDK（在 vite.config.ts 中添加 `ssr.noExternal: ['@medusajs/js-sdk']`）
- ❌ 运行 Medusa 电商平台在端口其他于 8000（会导致 CORS 错误 - Medusa 后端默认期望端口 8000）
- ❌ 未实现 API 调用的加载、错误和空状态
- ❌ 在客户端执行本应服务器端的 API 调用（SEO、安全性）
- ❌ 未实现适当的错误消息（“发生错误” vs “产品缺货”）
- ❌ 缺少缓存失效（过时的产品数据、价格、库存）
- ❌ **未在订单完成后清除购物车状态** - 购物车弹窗显示旧项目，因为购物车未从 Context/localStorage/缓存重置
