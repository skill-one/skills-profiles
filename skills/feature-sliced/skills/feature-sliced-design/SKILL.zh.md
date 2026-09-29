---
name: feature-sliced-design
description: 官方功能切片设计（FSD）v2.1技能，用于将此方法论应用于前端项目。当任务涉及使用FSD层组织项目结构、决定代码归属位置、放置静态资源（图片、图标、字体、PDF）、分组紧密相关的切片、定义公共API和导入边界、解决跨导入问题或评估@x模式、决定是否创建或删除实体、评估是否需要实体层、决定页面布局归属或是否使用组件层（不推荐）、决定逻辑应保留本地还是提取、从FSD v2.0或非FSD代码库迁移、将FSD与框架集成（Next.js App Router和Pages Router、React Router、Nuxt、Vite、Astro）或实现FSD内的常见模式（如认证、API处理、Redux和TanStack Query（React Query））。
---

# 功能切片设计 (FSD) v2.1

> **来源**: [fsd.how](https://fsd.how) | 严格性可以根据项目规模和团队环境进行调整。

**如何使用这项技能。** 对于放置决策，从第 2 节中的决策树开始，并将第 3 节中的放置表作为快速参考。要检查结构是否存在违规，请使用第 4 节中的规则。要解决同一层级的跨导入，请使用第 7 节。对于特定任务的指导，仅加载第 10 节中相关的参考文件；不要预加载其余部分。

## 1. 核心理念与层级概述

FSD v2.1 核心原则：**"从简单开始，需要时再提取。"**

### 提取规则

首先将代码放在 `pages/` 中。页面之间的代码重复是可接受的，本身并不需要提取到较低层级。只有当所有三个条件都满足时才提取：

1. 相同的代码当前在多个地方使用，而不是假设性的。
2. 它有独立于任何单个消费者的变更理由。
3. 边界具有专注的责任。

### 六个层级

**并非所有层级都是必需的。** 大多数项目可以仅使用 `shared/`、`pages/` 和 `app/`。仅在它们提供明确价值时才添加 `features/` 和 `entities/`。不要创建空的层级文件夹 "以防万一"。`widgets/` 层级是**不鼓励**的（见下方的注释）。

FSD 使用 6 个标准化的层级，这里从最高到最低列出：

```text
app/       → 应用初始化、提供者、路由
pages/     → 路由级别的组合，拥有自己的逻辑
widgets/   → 可重用的 UI 块（不鼓励，见下方的注释）
features/  → 可重用的用户交互（见上方的提取规则）
entities/  → 可重用的业务领域模型（见上方的提取规则）
shared/    → 没有业务逻辑的基础设施（UI 工具包、工具、API 客户端）
```

**官方层级参考不鼓励使用 Widgets 层级**，这项技能也遵循它。Widgets 似乎对于表示独立的 UI 块很有用。然而，在真实的前端代码中，UI 块通常包含用户流程所需的逻辑，例如数据获取、状态管理和事件处理。在这种情况下，处理用户流程的 Features 层级和处理 UI 块的 Widgets 层级的责任可能会重叠，使得这两个层级之间的边界变得不明确。

不创建 Widget 并不意味着将块原样移动到其他地方。特定屏幕的组合保留在 `pages`；可重用的操作及其执行 UI 转移到 `features`；无上下文的 UI 转移到 `shared`；应用范围的布局转移到 `app`。

不鼓励不等于已弃用：现有的 widgets 层级仍然有效。有关此情况和布局放置，请参阅 `references/layer-structure.md`。

### 导入规则

一个模块只能从严格位于其下方的层级导入。同一层级上的切片之间的跨导入是禁止的，第 7 节中有一个狭隘的例外。

```typescript
// 允许
import { Button } from "@/shared/ui/Button"; // features → shared
import { useUser } from "@/entities/user"; // pages → entities

// 违规
import { loginUser } from "@/features/auth"; // entities → features
import { likePost } from "@/features/like-post"; // features → features
```

**注意**: `processes/` 层级在 v2.1 中已**弃用**。有关迁移细节，请阅读 `references/migration-guide.md`。

## 2. 决策框架

编写新代码时，请遵循此树：

**步骤 1: 这段代码在何处使用？**

- 仅在一个页面中使用 → 保留在该 `pages/` 切片中的代码。
- 在 2 个或更多页面中使用，但重复是可管理的 → 在每个页面中保留单独的副本也是有效的。
- 具有单个消费者的实体或功能 → 保留在消费者处（Steiger 将其标记为 `insignificant-slice`）。

**步骤 2: 它是否是没有任何业务逻辑的可重用基础设施？**

官方层级参考将 Shared 的界限这样划定：没有业务逻辑，但业务主题是允许的（公司标志、页面布局），UI 逻辑也是允许的（自动完成、搜索栏）。与后端交换数据和 CRUD 模板也不是业务逻辑。业务逻辑是产品对其自身数据的规则，例如对订单应用折扣。如果代码不符合任何排除项，并且仍然没有明确地执行产品规则，那么术语并不能决定；回到步骤 1 并根据其使用位置放置它。

- UI 组件 → `shared/ui/`
- 工具函数 → `shared/lib/`
- API 客户端、路由常量 → `shared/api/` 或 `shared/config/`
- 认证令牌、会话管理 → `shared/auth/`
- CRUD 一旦多个切片调用它 → `shared/api/`（单个调用者保留它，见步骤 1）

**步骤 3: 它是否是一个完整的用户操作，多个消费者共享，具有专注的责任和自身的变更理由？**

- 是 → `features/`
- 不确定、单次使用或推测性重用 → 保留在页面中。

**步骤 4: 它是否是一个业务领域模型，多个消费者共享，具有专注的责任和自身的变更理由？**

- 是 → `entities/`
- 不确定、单次使用或推测性重用 → 保留在页面中。

**步骤 5: 它是否是应用范围的配置？**

- 全局提供者、路由、主题 → `app/`

**黄金法则：如有疑问，保留在 `pages/` 中。只有在提取规则满足时才提取。**

## 3. 快速放置表

| 情景                   | 单次使用                                  | 确认多次使用                   |
| ---------------------- | ----------------------------------------- | ----------------------------- |
| 用户资料表单          | `pages/profile/ui/ProfileForm.tsx`          | `features/profile-form/`              |
| 产品卡片               | `pages/products/ui/ProductCard.tsx`         | 如果实体拥有它，`entities/product/ui/` |
| API 请求（读取或 CRUD） | `pages/product-detail/api/fetch-product.ts` | `shared/api/`（没有领域规则）       |
| 认证令牌/会话         | `shared/auth/`                              | `shared/auth/`                        |
| 认证登录表单            | `pages/login/ui/LoginForm.tsx`              | `features/auth/`                      |
| 通用卡片布局        |                                             | `shared/ui/Card/`                     |
| 模态管理器              |                                             | `shared/ui/modal-manager/`            |
| 模态内容              | `pages/[page]/ui/SomeModal.tsx`             |                                       |
| 日期格式化工具       |                                             | `shared/lib/format-date.ts`           |

"确认多次使用" 并不意味着提取规则满足，也不意味着出现了第二个消费者：两个相似的副本不断分离开来，保留在它们的页面中（`references/growth-walkthrough.md`，快照 1）。即使规则满足，实体 UI 也带有第 6 节的警告。

## 4. 架构规则（必须）

这些规则是 FSD 的基础。违规会削弱架构。如果你必须打破一条规则，请确保这是一个有意的设计决策，并在代码中记录原因（注释或 ADR）。

### 4-1. 仅从较低层级导入

`app → pages → widgets → features → entities → shared`。
向上导入是禁止的。同一层级上的切片之间的跨导入也是禁止的，除非通过另一个切片的公共 API 作为最后的手段（第 7 节，策略 D）。

### 4-2. 公共 API：每个切片通过 index.ts 导出

外部消费者只能从切片的 `index.ts` 中导入。禁止直接导入内部文件。

```typescript
// 正确
import { LoginForm } from "@/features/auth";

// 违规：绕过公共 API
import { LoginForm } from "@/features/auth/ui/LoginForm";
```

**共享层**: 共享没有切片。为每个片段定义一个单独的公共 API（`shared/ui/index.ts`、`shared/api/index.ts` 等），而不是一个顶层的 `shared/index.ts`。这使来自共享的导入按意图组织。

当一个片段的无关模块的索引会损害打包时，给每个组件、库或控制器文件夹一个自己的索引，而不是一个片段的索引（`shared/ui/Button/index.ts` 作为 `@/shared/ui/Button`，`shared/api/post/` 作为 `@/shared/api/post`）。该文件夹是边界；越过它（`@/shared/ui/Button/Button.tsx`）仍然违规。有关形状，请参阅 `references/layer-structure.md`。

**环境特定的入口点**: 切片通常暴露一个 `index.ts`，不推荐临时变化。如果单个索引无法保留运行时边界，请添加一个入口点，例如 `index.server.ts`。有关详细信息，请参阅 `references/framework-integration.md`。

### 4-3. 同一层级的切片之间禁止跨导入

如果同一层级的两个切片需要共享逻辑，请遵循第 7 节中的解决顺序。永远不要深入另一个切片的内部。

### 4-4. 基于领域的文件命名（不允许分解）

根据文件是用于什么、它服务的领域或关注点来命名，而不是根据其技术角色。技术角色名称（如 `types.ts`、`utils.ts`、`helpers.ts`）将不相关的关注点混合在一个文件中，并降低内聚性。

```text
// BAD: 技术角色命名
model/types.ts          ← 哪些类型？用户？订单？混合？
model/utils.ts

// GOOD: 基于领域的命名
model/user.ts           ← 用户类型 + 相关逻辑
model/order.ts          ← 订单类型 + 相关逻辑
api/fetch-profile.ts    ← 明确的目的
```

### 4-5. shared/ 中没有业务逻辑

共享只包含基础设施：UI 工具包、工具、API 客户端设置、路由常量、资源。业务计算、领域规则和工作流属于 `entities/` 或更高层级。第 2 步，第 2 节说明了什么算作业务逻辑。

```typescript
// BAD: shared 中有业务逻辑
// shared/lib/userHelpers.ts
export const calculateUserReputation = (user) => { ... };

// GOOD: 将它移交给拥有规则的人
// pages/profile/model/reputation.ts       ← 虽然资料页面拥有它
// entities/user/model/reputation.ts       ← 一旦用户边界被获得
export const calculateUserReputation = (user) => { ... };
```

## 5. 建议（应该）

### 5-1. 首先放置页面：将代码放在它被使用的地方

首先将代码放在 `pages/` 中。只有在真正需要时才提取到较低层级。提取是一个影响整个项目的设计决策，因此阈值应该很高。

**保留在页面中的内容:**

- 仅在一个页面使用的较大 UI 块
- 页面特定的表单、验证、数据获取、状态管理
- 页面特定的业务逻辑和 API 集成
- 看起来可重用但保留本地更简单的代码

**进化模式**: 首先将所有内容放在 `pages/profile/`。当第二个页面消费它并且提取规则满足时，将共享模型提取到 `entities/user/`。几个页面读取的响应类型不是这种情况：它保留在 `shared/api`。保留页面特定的 API 调用和 UI。

### 5-2. 保守使用实体

实体层级具有高度可访问性（几乎所有其他层级都可以从它导入），因此变更会广泛传播。

1. **开始时不使用实体。** `shared/` + `pages/` + `app/` 是有效的 FSD。
   薄客户端应用程序很少需要实体。
2. **不要过早拆分切片。** 将代码保留在页面中。只有在提取规则满足时才提取到实体。
3. **业务逻辑并不自动需要实体。** 将类型保留在 `shared/api`，将逻辑保留在当前切片的 `model/` 段可能就足够了。
4. **CRUD 是基础设施，不是实体。** 根据请求放置规则放置它：当有消费者时，与消费者一起放置；一旦多个切片调用它，就放在 `shared/api/`。
5. **将认证数据放在 `shared/auth/` 或 `shared/api/`。** 令牌和登录 DTO 是依赖于认证上下文的，并且很少在认证之外重用。

有关保持实体层级干净的详细指导（何时完全跳过它，如何隔离业务上下文，为什么 CRUD 属于 `shared/api`），请参阅 `references/excessive-entities.md`。

### 5-3. 从最小层级开始

```text
// 有效的最小 FSD 项目
src/
  app/         ← 提供者、路由
  pages/       ← 所有页面级代码
  shared/      ← UI 工具包、工具、API 客户端

// 仅在实际用例需要时才添加层级：
// + features/  ← 需要共享家的用户操作边界
// + entities/  ← 需要共享家的领域边界
// (widgets/ 是不鼓励的；见第 1 节，替代代码的位置)
```

### 5-4. 使用 Steiger linter 进行验证

[Steiger](https://github.com/feature-sliced/steiger) 是官方 FSD linter。关键规则：

- **`insignificant-slice`**: 标记没有引用的切片，或只有一个引用，并建议将其合并到上一层级。页面可以保留一个引用，切片仅从 `app/` 使用也可能保留一个引用。
- **`excessive-slicing`**: 建议合并或分组，当一个层级有太多切片时。

```bash
npm install -D @feature-sliced/steiger
npx steiger src
```

## 6. 反模式（避免）

- **不要过早创建实体。** 仅在一个地方使用的数据结构属于该地方。
- **不要将 CRUD 放在实体中。** 纯 CRUD 是 `shared/api/`。一个携带业务规则的操作由谁拥有规则来放置，这可能是实体、功能或运行工作流的页面。
- **不要只为认证数据创建一个 `user` 实体。** 令牌和登录 DTO 属于 `shared/auth/` 或 `shared/api/`。
- **不要滥用 `@x`。** 它是一个必要的妥协，而不是推荐的模式。符号仅用于实体层级，并且仅当边界合并确实不可能时才使用。功能和 Widget 通过策略 A 到 D（见第 7 节）处理跨导入。
- **不要提取单次使用的代码。** 仅由一个页面使用的功能或实体应保留在该页面中。
- **不要使用技术角色文件名。** 使用基于领域的名称（见规则 4-4）。
- **添加实体 UI 要谨慎。** 实体 UI 诱使从其他实体进行跨导入。如果你向实体添加 UI 段，只从较高层级（功能、页面、应用）导入它们，永远不要从其他实体导入。
- **不要创建神切片。** 责任过宽的切片应拆分为专注的切片（例如，将 `user-management/` 拆分为 `auth/`、`profile-edit/`、`password-reset/`）。
- **不要创建顶层的 `assets/` 片段。** 将静态资源放在使用它们的代码旁边；全局样式表和字体转到 `app/`。有关详细信息，请参阅 `references/asset-handling.md`。

## 7. 跨导入解决

跨导入是代码异味，而不是绝对禁止。正确的策略取决于层级和情况。

### 实体层级：优先合并边界，@x 是最后手段

实体中的跨导入通常是由实体拆分得太细引起的。在转向 `@x` 之前，请考虑是否应该合并边界。

`@x` 是一个**必要的妥协，而不是推荐的方法**。仅在边界确实无法合并时使用它，并记录原因。过度使用会锁定实体边界，增加重构成本。

### 功能和 Widget：四种策略（A、B、C、D）

在 `features` 和 `widgets` 中，根据上下文选择：

- **策略 A：切片合并。** 两个切片总是一起更改 → 合并。
- **策略 B：推送到实体。** 共享领域责任 → 将其移动到拥有它的实体，保留 UI 在功能中。
- **策略 C：从上层组合（IoC）。** 父级（页面或应用）导入两个切片，并通过渲染属性、插槽或 DI 连接它们。
- **策略 D：公共 API 访问。** 当重用确实不可避免时，仅通过切片的 `index.ts` 允许它。永远不要深入 `model/`、`store/` 或内部文件。

`@x` 符号仅用于实体层级。功能和 Widget 使用上述 A 到 D 策略。

### 严格性取决于项目上下文

跨导入是通常最好避免的依赖，但有时有意使用。严格性因项目上下文而异：

- **早期产品**具有大量实验性：允许某些跨导入可能是一种务实的速度权衡。
- **长期存在或受监管的系统**（金融科技、大规模服务）：
  更严格的边界在可维护性和稳定性方面是有益的。

如果引入了跨导入，将其视为一个有意的选择，并在代码中记录其理由（一个解释为什么其他策略不适用注释）。

有关每种策略的详细代码示例，请阅读 `references/cross-import-patterns.md`。

## 8. 段落与结构规则

### 标准段落

段落按技术用途在一个切片内对代码进行分组：

- **`ui/`**：UI 组件、样式、显示相关代码
- **`model/`**：数据模型、状态存储、业务逻辑、验证
- **`api/`**：后端集成、请求函数、特定于 API 的类型
- **`lib/`**：此切片的内部实用函数
- **`config/`**：配置、功能标志

### 层级结构规则

- **应用和共享**：没有切片，直接按段落组织。这些层级内的段落可以相互导入。
- **页面、组件、功能、实体**：首先切片，然后在每个切片内组织段落。
- **切片组（可选）**：一个组文件夹可以包含同一层级的相关切片，仅用于导航目的。该组没有段落，也没有公共 API。有关详细信息，请参阅 `references/layer-structure.md`。

### 段落内的文件命名

始终使用描述代码内容的基于领域的名称：

```text
model/user.ts            ← 用户类型 + 逻辑 + 存储
model/order.ts           ← 订单类型 + 逻辑 + 存储
api/fetch-profile.ts     ← 获取个人资料
api/update-settings.ts   ← 更新设置
```

如果一个段落只有一个领域关注点，文件名可以与切片名匹配（例如，`features/auth/model/auth.ts`）。

## 9. 共享层指南

共享包含**没有业务逻辑**的基础设施。它仅按段落组织（没有切片）。共享内的段落可以相互导入。

**允许在共享中：**

- `ui/`：UI 套件（按钮、输入、模态框、卡片）
- `lib/`：实用工具（formatDate、debounce、classnames）
- `api/`：API 客户端、路由常量、CRUD 辅助程序、基础类型
- `auth/`：认证令牌、登录实用工具、会话管理
- `config/`：环境变量、应用设置
- 资产与使用它们的代码一起存放，而不是放在 `assets/` 段落中。有关详细信息，请参阅 `references/asset-handling.md`。

共享**可以**包含与应用程序相关的代码：路由常量、API 端点、品牌资产，以及 `ProductDTO` 等传输类型。它必须**永远**不包含实体或功能拥有的业务规则，也不从这些层级导入。

## 10. 条件引用

仅在特定情况适用时才读取以下参考文件。**不要**预加载所有参考。

- **在审查或重新组织已存在的文件夹和文件结构**时，决定什么内容放在层级或切片内，决定页面布局属于哪里，将类似组件的代码路由到另一个层级，或将密切相关的切片分组到父文件夹中以供导航（例如，“这个文件夹放在哪里”，“如何分组这些支付实体”）：
  → 阅读 `references/layer-structure.md`

- **在从零开始设置新项目**时（例如，“设置 FSD 项目”，“启动新的 FSD 应用程序”），或者当被问及是否要添加实体或功能，或者要展示结构如何随时间逐步获得每个层级，而不是其最终形状时：
  → 阅读 `references/growth-walkthrough.md`

- **在解决同一层级切片之间的跨导入问题**、评估 `@x` 模式、在功能和组件之间选择策略 A/B/C/D，或决定是否应合并边界时：
  → 阅读 `references/cross-import-patterns.md`

- **在决定是否创建或删除实体**、处理过多实体、评估是否完全跳过实体层级、放置 CRUD 操作，或隔离业务上下文以避免 `@x` 链时：
  → 阅读 `references/excessive-entities.md`

- **在决定将静态资产**（图像、图标、字体、PDF、样式表）放置在哪里，用于单个切片、跨切片共享或全局使用时：
  → 阅读 `references/asset-handling.md`

- **在从 FSD v2.0 迁移到 v2.1**、将非 FSD 代码库转换为 FSD、逐步淘汰现有的组件层级，或淘汰流程层级时：
  → 阅读 `references/migration-guide.md`

- **在将 FSD 与特定框架**（Next.js 与 App Router 或 Pages Router、React Router、Nuxt、Vite、Astro）集成时，用于将路由连接到 FSD 页面、放置代理/中间件和仪器文件、结构 API 路由处理程序或配置路径别名：
  → 阅读 `references/framework-integration.md`

- **在 FSD 结构内实现认证、类型定义或 API 请求处理**作为具体代码时（令牌存储、登录流程、DTO 位置、请求函数的位置）：
  → 阅读 `references/auth-and-api.md`

- **在将状态管理**（Redux 切片、TanStack Query / React Query，包括查询工厂、无限滚动、Suspense 模式和 `useMutationState`）集成到 FSD 结构时：
  → 阅读 `references/state-management.md`
