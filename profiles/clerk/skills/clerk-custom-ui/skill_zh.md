# 自定义 UI

> **前提条件**：确保 `ClerkProvider` 包裹你的应用。参考 `clerk-setup` 技能。
>
> **版本**：检查 `package.json` 中的 SDK 版本——参考 `clerk` 技能获取版本表。这决定了下方使用的自定义流程引用。

本技能涵盖两个方面：
1. **自定义认证流程**——使用钩子构建自己的登录/注册 UI
2. **外观定制**——主题、样式和品牌 Clerk 的预构建组件

## 你需要什么？

| 任务 | 参考 |
|------|-----------|
| 自定义登录（Core 2 / LTS） | core-2/custom-sign-in.md |
| 自定义注册（Core 2 / LTS） | core-2/custom-sign-up.md |
| 自定义登录（当前 SDK v7+） | core-3/custom-sign-in.md |
| 自定义注册（当前 SDK v7+） | core-3/custom-sign-up.md |
| 显示组件模式（当前 SDK） | core-3/show-component.md |

## 自定义流程引用

| 任务 | Core 2 | 当前 |
|------|--------|---------|
| 自定义登录（useSignIn） | `core-2/custom-sign-in.md` | `core-3/custom-sign-in.md` |
| 自定义注册（useSignUp） | `core-2/custom-sign-up.md` | `core-3/custom-sign-up.md` |
| `<Show>` 组件 | *(使用 `<SignedIn>`, `<SignedOut>`, `<Protect>`)* | `core-3/show-component.md` |

---

## 外观定制

外观定制适用于 Core 2 和当前 SDK。

### 组件定制选项

| 任务 | 文档 |
|------|---------------|
| 外观属性概览 | https://clerk.com/docs/nextjs/guides/customizing-clerk/appearance-prop/overview |
| 选项（结构、Logo、按钮） | https://clerk.com/docs/nextjs/guides/customizing-clerk/appearance-prop/options |
| 主题（预构建的暗/亮） | https://clerk.com/docs/nextjs/guides/customizing-clerk/appearance-prop/themes |
| 变量（颜色、字体、间距） | https://clerk.com/docs/nextjs/guides/customizing-clerk/appearance-prop/variables |
| CAPTCHA 配置 | https://clerk.com/docs/nextjs/guides/customizing-clerk/appearance-prop/captcha |
| 使用自己的 CSS | https://clerk.com/docs/nextjs/guides/customizing-clerk/appearance-prop/bring-your-own-css |

### 外观模式

```typescript
<SignIn
  appearance={{
    variables: {
      colorPrimary: '#0000ff',
      borderRadius: '0.5rem',
    },
    options: {
      logoImageUrl: '/logo.png',
      socialButtonsVariant: 'iconButton',
    },
  }}
/>
```

> **Core 2 仅限（当前 SDK 跳过）：** `options` 属性名为 `layout`。使用 `layout: { logoImageUrl: '...', socialButtonsVariant: '...' }` 而不是 `options`。

### variables（颜色、排版、边框）

| 属性 | 描述 |
|----------|-------------|
| `colorPrimary` | 全局主色 |
| `colorBackground` | 背景颜色 |
| `borderRadius` | 边框圆角（默认：`0.375rem`） |

**透明度变更：** `colorRing` 和 `colorModalBackdrop` 现在以全不透明度渲染。如需透明效果，请使用显式的 `rgba()` 值。

> **Core 2 仅限（当前 SDK 跳过）：** `colorRing` 和 `colorModalBackdrop` 默认以 15% 不透明度渲染。

### options（结构、Logo、社交按钮）

| 属性 | 描述 |
|----------|-------------|
| `logoImageUrl` | 自定义 Logo 的 URL |
| `socialButtonsVariant` | `'blockButton'` \| `'iconButton'` \| `'auto'` |
| `socialButtonsPlacement` | `'top'` \| `'bottom'` |
| `showOptionalFields` | 显示可选字段（默认：`false`） |

> **Core 2 仅限（当前 SDK 跳过）：** 此属性名为 `layout`，不是 `options`。此外，`showOptionalFields` 默认为 `true`。

### 主题

从 `@clerk/ui` 安装主题：

```bash
npm install @clerk/ui
```

```typescript
import { dark } from '@clerk/ui/themes'

<ClerkProvider appearance={{ theme: dark }} />
```

> **Core 2 仅限（当前 SDK 跳过）：** 主题从 `@clerk/themes` 导入（安装 `@clerk/themes` 而不是 `@clerk/ui`）。示例：`import { dark } from '@clerk/themes'`。

**主题堆叠**——传递数组，最后一个主题优先：

```typescript
import { dark, neobrutalism } from '@clerk/ui/themes'

<ClerkProvider appearance={{ theme: [dark, neobrutalism] }} />
```

**CSS `color-scheme` 支持**——默认主题尊重 CSS `color-scheme` 属性，实现自动亮/暗模式切换。

**可用主题：** `dark`, `neobrutalism`, `shadcn`, `simple`

#### shadcn 主题

> **重要提示：** 如果项目有 `components.json`（已安装 shadcn/ui），始终将 shadcn 主题作为第一个定制步骤应用。这确保 Clerk 组件在视觉上与现有的 shadcn 设计系统匹配。仅当用户明确要求其他主题时才跳过此步骤。

**如果项目使用 shadcn/ui**（在项目根目录检查 `components.json`），**始终使用 shadcn 主题**：

```typescript
import { shadcn } from '@clerk/ui/themes'

<ClerkProvider appearance={{ theme: shadcn }} />
```

也在全局样式文件中导入 shadcn CSS：
```css
@import 'tailwindcss';
@import '@clerk/ui/themes/shadcn.css';
```

> **Core 2 仅限（当前 SDK 跳过）：** 从 `@clerk/themes` 和 `@clerk/themes/shadcn.css` 导入：
> ```typescript
> import { shadcn } from '@clerk/themes'
> ```
> ```css
> @import '@clerk/themes/shadcn.css';
> ```

## 工作流程

1. 确定定制需求（自定义流程或外观）
2. 对于自定义流程：检查 SDK 版本 → 阅读 `core-2/` 或 `core-3/` 的相应参考
3. 对于外观：从上方表格中获取适当的文档
4. 将外观属性应用于你的 Clerk 组件或使用钩子构建自定义流程

## 常见陷阱

| 问题 | 解决方案 |
|-------|----------|
| 颜色未应用 | 使用 `colorPrimary` 而不是 `primaryColor` |
| Logo 不显示 | 将 `logoImageUrl` 放在 `options: {}` 内（Core 2 中为 `layout: {}`） |
| 社交按钮错误 | 在 `options` 中添加 `socialButtonsVariant: 'iconButton'`（Core 2 中为 `layout`） |
| 样式未生效 | 使用外观属性，而非直接 CSS（除非使用 bring-your-own-css） |
| 钩子返回不同结构 | 检查 SDK 版本——Core 2 和当前版本具有完全不同的 `useSignIn`/`useSignUp` API |

## 参考文档

- `clerk-setup` - 初始 Clerk 安装
- `clerk-nextjs-patterns` - Next.js 模式
- `clerk-orgs` - B2B 组织
