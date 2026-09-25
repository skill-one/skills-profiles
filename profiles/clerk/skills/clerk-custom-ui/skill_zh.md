# Custom UI

> **前置条件**：请确保使用 `ClerkProvider` 包装您的应用。请参阅 `clerk-setup` 技能。
>
> **版本**：请查看 `package.json` 中的 SDK 版本 —— 请参阅 `clerk` 技能获取版本表。这决定了下方引用的自定义流程。

本技能涵盖两个方面：
1. **自定义认证流程** — 使用 hooks 构建自己的登录/注册 UI
2. **外观定制** — Clerk 预置组件的主题、样式和品牌

## 需要准备的内容？

| 任务 | 参考文档 |
|------|----------|
| 自定义登录（Core 2 / LTS） | `core-2/custom-sign-in.md` |
| 自定义注册（Core 2 / LTS） | `core-2/custom-sign-up.md` |
| 自定义登录（当前 SDK v7+） | `core-3/custom-sign-in.md` |
| 自定义注册（当前 SDK v7+） | `core-3/custom-sign-up.md` |
| 组件展示模式（当前 SDK） | `core-3/show-component.md` |

## 自定义流程引用

| 任务 | Core 2 | 当前 |
|------|--------|------|
| 自定义登录（useSignIn） | `core-2/custom-sign-in.md` | `core-3/custom-sign-in.md` |
| 自定义注册（useSignUp） | `core-2/custom-sign-up.md` | `core-3/custom-sign-up.md` |
| `<Show>` 组件 | *(使用 `<SignedIn>`、`<SignedOut>`、`<Protect>`)* | `core-3/show-component.md` |

---

## 外观定制

外观定制适用于 Core 2 和当前 SDK。

### 组件定制选项

| 任务 | 文档链接 |
|------|----------|
| 外观属性概述 | https://clerk.com/docs/nextjs/guides/customizing-clerk/appearance-prop/overview |
| 选项（结构、Logo、按钮） | https://clerk.com/docs/nextjs/guides/customizing-clerk/appearance-prop/options |
| 主题（预置深色/浅色） | https://clerk.com/docs/nextjs/guides/customizing-clerk/appearance-prop/themes |
| 变量（颜色、字体、间距） | https://clerk.com/docs/nextjs/guides/customizing-clerk/appearance-prop/variables |
| CAPTCHA 配置 | https://clerk.com/docs/nextjs/guides/customizing-clerk/appearance-prop/captcha |
| 自定 CSS | https://clerk.com/docs/nextjs/guides/customizing-clerk/appearance-prop/bring-your-own-css |

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

> **Core 2 专属（若为当前 SDK 则跳过）：** `options` 属性名为 `layout`。请使用 `layout: { logoImageUrl: '...', socialButtonsVariant: '...' }`，而非 `options`。

### variables（颜色、排版、边框）

| 属性 | 说明 |
|------|------|
| `colorPrimary` | 全站主色 |
| `colorBackground` | 背景色 |
| `borderRadius` | 边框半径（默认：`0.375rem`） |

**透明度调整：** `colorRing` 和 `colorModalBackdrop` 现在以完全透明渲染。如需透明效果，请使用明确的 `rgba()` 值。

> **Core 2 专属（若为当前 SDK 则跳过）：** `colorRing` 和 `colorModalBackdrop` 默认以 15% 透明度渲染。

### options（结构、Logo、社交按钮）

| 属性 | 说明 |
|------|------|
| `logoImageUrl` | 自定义 Logo 的 URL |
| `socialButtonsVariant` | `'blockButton'` \| `'iconButton'` \| `'auto'` |
| `socialButtonsPlacement` | `'top'` \| `'bottom'` |
| `showOptionalFields` | 显示可选字段（默认：`false`） |

> **Core 2 专属（若为当前 SDK 则跳过）：** 该属性名为 `layout`，而非 `options`。此外，`showOptionalFields` 默认为 `true`。

### 主题

从 `@clerk/ui` 安装主题：

```bash
npm install @clerk/ui
```

```typescript
import { dark } from '@clerk/ui/themes'

<ClerkProvider appearance={{ theme: dark }} />
```

> **Core 2 专属（若为当前 SDK 则跳过）：** 主题从 `@clerk/themes` 导入（请安装 `@clerk/themes`，而非 `@clerk/ui`）。示例：`import { dark } from '@clerk/themes'`。

**主题堆叠** — 传入数组，最后一个主题优先级最高：

```typescript
import { dark, neobrutalism } from '@clerk/ui/themes'

<ClerkProvider appearance={{ theme: [dark, neobrutalism] }} />
```

**CSS `color-scheme` 支持** — 默认主题遵循 CSS `color-scheme` 属性，实现自动浅色/深色模式切换。

**可用主题：** `dark`、`neobrutalism`、`shadcn`、`simple`

#### shadcn 主题

> **重要提示：** 如果项目包含 `components.json`（即已安装 shadcn/ui），请始终将 shadcn 主题作为第一步应用。这能确保 Clerk 组件与现有的 shadcn 设计系统在视觉上保持一致。仅在用户明确要求使用其他主题时才跳过此步骤。

**如果项目使用 shadcn/ui**（请检查项目根目录下是否存在 `components.json`），**始终使用 shadcn 主题**：

```typescript
import { shadcn } from '@clerk/ui/themes'

<ClerkProvider appearance={{ theme: shadcn }} />
```

同时在全局样式中导入 shadcn CSS：
```css
@import 'tailwindcss';
@import '@clerk/ui/themes/shadcn.css';
```

> **Core 2 专属（若为当前 SDK 则跳过）：** 从 `@clerk/themes` 导入，并导入 `@clerk/themes/shadcn.css`：
> ```typescript
> import { shadcn } from '@clerk/themes'
> ```
> ```css
> @import '@clerk/themes/shadcn.css';
> ```

## 工作流程

1. 识别定制需求（自定义流程或外观）
2. 对于自定义流程：检查 SDK 版本 → 阅读合适的 `core-2/` 或 `core-3/` 参考文档
3. 对于外观：获取上方表格中的对应文档
4. 将外观属性应用到您的 Clerk 组件，或构建使用 hooks 的自定义流程

## 常见陷阱

| 问题 | 解决方案 |
|------|----------|
| 颜色未应用 | 使用 `colorPrimary`，而非 `primaryColor` |
| Logo 未显示 | 将 `logoImageUrl` 放在 `options: {}` 内（Core 2 中为 `layout: {}`） |
| 社交按钮错误 | 在 `options` 内添加 `socialButtonsVariant: 'iconButton'`（Core 2 中为 `layout`） |
| 样式未生效 | 使用外观属性，而非直接 CSS（除非配合自定 CSS） |
| Hook 返回结构不同 | 检查 SDK 版本 — Core 2 和当前版本拥有完全不同的 `useSignIn`/`useSignUp` API |

## 相关链接

- `clerk-setup` - Clerk 初始安装
- `clerk-nextjs-patterns` - Next.js 模式
- `clerk-orgs` - B2B 组织
