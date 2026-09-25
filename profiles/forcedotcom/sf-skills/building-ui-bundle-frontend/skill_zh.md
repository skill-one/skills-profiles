# UI 套件 UI

## 确定任务

确定请求属于哪个类别：

| 类别 | 示例 | 实现指南 |
|------|------|----------|
| **页面** | 新的路由页面（联系人、仪表盘、设置） | `implementation/page.md` |
| **页眉 / 页脚** | 全站导航栏、页脚、品牌标识 | `implementation/header-footer.md` |
| **组件** | 小部件、卡片、表格、表单、对话框 | `implementation/component.md` |

---

## 布局和导航

`appLayout.tsx` 是导航和布局的权威来源。每个页面共享这个外壳。

当进行任何影响导航、页眉、页脚、侧边栏、主题或布局的更改时：

1. 编辑 `src/appLayout.tsx` — `routes.tsx` 使用的布局
2. 将所有默认/模板导航项和标签替换为应用程序特定的链接和名称
3. 在所有地方替换占位符应用程序名称：页眉、导航品牌、页脚、`index.html` 中的 `<title>`

完成前，请确认：我是否用真实的导航项和品牌更新了 `appLayout.tsx`？

| 内容 | 位置 |
|------|------|
| 布局、导航、品牌 | `src/appLayout.tsx` |
| 文档标题 | `index.html` |
| 根页面内容 | `routes.tsx` 中根路由处的组件 |

---

## React 和 TypeScript 标准

### 路由

使用单个路由包。使用 `createBrowserRouter` / `RouterProvider` 时，所有导入必须来自 `react-router`（而不是 `react-router-dom`）。

如果应用程序使用客户端路由器（React Router、Remix Router、Vue Router 等），始终在运行时从文档的 `<base href>` 标签中派生 basename / basepath / base。切勿硬编码 basename：

```js
const basename = document.querySelector('base')
  ? new URL(document.querySelector('base').href).pathname.replace(/\/$/, '')
  : '/';
const router = createBrowserRouter(routes, { basename });
```

### 组件库和样式

- **shadcn/ui** 用于组件：`import { Button } from '@/components/ui/button';`
- **Tailwind CSS** 工具类

### URL 和路径处理

应用程序在动态基本路径后面运行。路由导航（`<Link to>`，`navigate()`）使用绝对路径（`/x`）。非路由属性（`<img src>`）使用点相对路径（`./x`）。优先使用 Vite `import` 处理静态资源。

### TypeScript

- 切勿使用 `any` — 使用正确的类型、泛型或带类型守卫的 `unknown`
- 事件处理程序：`(event: React.FormEvent<HTMLFormElement>): void`
- 状态：`useState<User | null>(null)` — 始终提供类型参数
- 无不安全的断言（`obj as User`）— 使用类型守卫代替

### 模块限制

React UI 套件不得导入 Salesforce 平台模块，如 `lightning/*` 或 `@wire`（仅限 LWC）。对于数据访问，请使用 `using-ui-bundle-salesforce-data` 技能。

---

## 设计思维

在编码前，确定一个大胆的审美方向：

- **目的：** 这个界面解决了什么问题？谁使用它？
- **基调：** 选择一个明确的方向 — 残酷极简、极繁、复古未来主义、有机、奢华、俏皮、编辑、残酷主义、艺术装饰、柔和/粉彩、工业。使用这些作为灵感，但设计一个忠于上下文的真实方向。
- **差异化：** 什么让它难以忘怀？什么是一个人会记住的东西？

选择一个清晰的概念方向，并以精确性执行。大胆的极繁和精致的极简都有效 — 关键在于意图，而不是强度。

---

## 前端美学

- **排版：** 选择独特、有性格的字体。搭配一个展示字体和一个精致的正文字体。切勿默认使用 Inter、Roboto、Arial、Space Grotesk 或系统字体。
- **颜色：** 使用 CSS 变量承诺一个协调的调色板。主导颜色与锐利点缀胜过胆怯、均匀分布的调色板。避免在白色背景上的陈词滥调的紫色渐变。
- **动效：** 关注高冲击力时刻 — 一个精心编排的页面加载，带有分层的揭示（`animation-delay`）比零散的微交互更能带来愉悦感。使用滚动触发和悬停状态来惊喜。优先使用纯 CSS 解决方案；在 React 中使用 Motion 库（当可用时）。
- **空间构图：** 意想不到的布局 — 不对称、重叠、对角线流动、打破网格的元素。充足的负空间 OR 控制的密度。
- **背景和深度：** 创造氛围，而不是默认使用纯色。渐变网格、噪声纹理、几何图案、分层透明度、戏剧性阴影、装饰性边框、颗粒叠加。

- **移动响应式：** 所有生成的 UI 必须是移动响应式的。使用 Tailwind 响应式前缀（`sm:`, `md:`, `lg:`）来适应不同断点的布局。在小屏幕上堆叠列，使用灵活的网格，并确保触摸目标至少为 44px。测试导航、排版和间距在移动视口中的表现。

将实现复杂度与美学愿景相匹配。极繁设计需要复杂的动画和效果。极简设计需要克制、精确和仔细的间距/排版。没有两个设计应该看起来一样 — 在不同代中变化主题、字体和美学。

---

## 澄清问题

一次问一个问题，当有足够上下文时停止。

### 对于页面
1. 名称和目的？
2. URL 路径？
3. 是否应出现在导航中？
4. 访问控制？（公开、通过 `PrivateRoute` 进行身份验证，或通过 `AuthenticationRoute` 进行非身份验证）
5. 内容部分？（列表、表单、表格、详细视图）
6. 数据获取需求？

### 对于页眉 / 页脚
1. 页眉、页脚，还是两者都有？
2. 内容？（标志、导航链接、用户头像、版权、社交图标）
3. 粘性页眉？
4. 色彩方案或风格方向？

### 对于组件
1. 它应该做什么？
2. 它属于哪个页面？
3. 共享/可重用还是特定于一个功能？
4. 需要哪些数据或属性？
5. 内部状态？（加载中、切换、表单状态）
6. 使用特定的 shadcn 组件？

---

## 验证

完成前，从 UI 套件目录运行 lint 和构建。Lint 必须产生 0 个错误，构建必须成功。
