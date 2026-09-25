# UI Bundle UI

## 解析 Bundle 目录

**必须**在应用以下任何规则或编写任何文件之前运行 `scripts/resolve-ui-bundle.sh [项目根目录]` —— 临时性的 `find`/`ls` 不能替代；它不会强制执行以下退出码门禁。它会读取 `sfdx-project.json` 的 `packageDirectories[0].path`（不假设 `force-app` —— 源路径是可配置的），并查找 `<源目录>/main/default/uiBundles/` 下：

- **退出 0**，bundle 路径打印到标准输出：找到 exactly 一个 bundle 目录 —— 那就是bundle目录。使用该确切目录名；永远不要用不同的名称（例如来自提示模板的通用 "AcmePortal" 示例）来替代实际打印的名称。
- **退出 2**，候选者打印到标准错误：存在多个 `uiBundles/*` 子目录 —— 不要猜测，不要写入任何它们中的任何一个，或写入未打印列表中的 bundle 名称。在编辑或运行任何命令之前，询问用户他们指的是哪个应用/bundle。
- **退出 1**：`sfdx-project.json` 缺失/无效，或根本没有找到 bundle 目录。

从解析的 bundle 目录中运行所有 `npm`/lint/build/dev 命令，永远不要从项目根目录运行。

## 前置条件

在应用以下任何规则之前，确认这是一个现有的、脚手架化的 UI bundle：**必须**运行 `scripts/check-preconditions.sh <bundle-dir>`，使用 `resolve-ui-bundle.sh` 打印的目录。

- **单 bundle (退出 0) 情况**：运行一次，在该 bundle 上。
- **多 bundle (退出 2) 情况**：不要运行它 —— 首先根据上述解析步骤询问用户他们指的是哪个应用/bundle。一旦用户命名了 bundle，仅在该一个 bundle 上运行 `check-preconditions.sh`。在用户选择之前，永远不要推测性地针对多个候选者运行它 —— 那意味着触摸/检查用户没有询问的 bundles。
- **退出 0**：该 bundle 有 `src/appLayout.tsx`、`src/routes.tsx` 和 `src/components/ui/` —— 继续。
- **退出 1**，列出了缺失的部分：这是一个全新的 SFDX 项目、一个非 UI-bundle React 项目，或一个部分脚手架化的 bundle —— **停止**。不要退回到通用的 React 知识（例如 `react-router-dom`、一个硬编码的 basename，或原始 HTML），也不要手写 `appLayout.tsx`/`routes.tsx`/一个页面/一个组件来“填充”缺失的脚手架，即使对于随意、模糊或听起来紧急的请求（“只是更改页眉”、“让背景变成蓝色”）。告诉用户 bundle 还没有脚手架化，并指导他们首先运行 `experience-ui-bundle-app-coordinate`（或 `experience-ui-bundle-metadata-generate`）来脚手架它。如果，在用户命名他们打算的 bundle 之后，那个一个被证明是未脚手架化的，停止并重定向它 —— 不要无声地切换到脚手架化另一个候选者。

永远不要编造、假设或退回到磁盘上实际 `<sourceDir>/main/default/uiBundles/` 列表中没有出现的 bundle 名称 —— 包括仅在其他地方作为示例/模板文本出现的名称（一个提示、一个指令、之前的对话）。如果磁盘上的内容与该示例不匹配，磁盘上的内容优先。

## 确定任务

确定请求属于哪个类别：

| 类别 | 示例 | 实现指南 |
|------|------|----------|
| **页面** | 新的路线页面（联系人、仪表板、设置） | `references/page.md` |
| **页眉 / 页脚** | 全站导航栏、页脚、品牌、重命名应用 | `references/header-footer.md` |
| **组件** | 小部件、卡片、表格、表单、对话框 | `references/component.md` |

重命名/重新品牌应用的请求（例如，“在用户会看到的任何地方都称它为 X”）是一个 **页眉 / 页脚** 任务，即使它没有以名称提及“页眉” —— 它总是触摸至少两个文件：`src/appLayout.tsx`（页眉/导航品牌文本）AND `index.html` 的 `<title>`（浏览器标签标题）。将它们视为一个原子性更改；仅更新其中一个的更名是不完整的。

---

## 预构建功能（构建前检查）

某些功能作为预构建的、经过测试的功能包提供。目录 **会演变，并且不能仅凭记忆知道** —— 永远不要根据请求措辞单独决定一个功能“是”或“不是”一个功能。在这个技能中，在手动编写任何非平凡的 capability（任何超出一个普通页面、组件或样式更改的东西）之前：

1. **参考权威目录**。调用 `experience-ui-bundle-features-generate`，它运行 `list` 来显示*当前*可安装的功能集。不要依赖硬编码或记忆中的列表 —— 这个技能故意不命名任何，因为它列出的任何名称都会过时。
2. **检测是否已安装匹配的功能** 在 bundle 中 —— 检查 `package.json` 依赖项和现有的 `src/` 文件。如果存在，不要重新安装或重新实现它 —— **但你必须仍然采用它**：调用 `experience-ui-bundle-features-generate` 来 `describe` 它（它读取功能的 README —— 采用合同），将其连接到应用中，并且如果功能提供配置（例如 `config.json`），为该应用的数据和使用案例设置该配置。已安装但未配置的未完成。
3. **如果目录中存在匹配的功能但未安装**，让 `experience-ui-bundle-features-generate` 安装测试过的包。不要在这里从零开始构建它。
4. **仅手动构建** 没有匹配目录功能的 capability。

当这个技能作为 `experience-ui-bundle-app-coordinate` 的一部分运行时，通常已经存在匹配的功能 —— 由早期阶段安装，或由模板提供。已存在**不是**跳过的理由：步骤 2 仍然需要为这个应用采用和配置该功能。仅安装/重新实现工作永远被跳过 —— 永远不要跳过连接和配置。

---

## 布局和导航

`appLayout.tsx` 是导航和布局的权威来源。每个页面共享这个外壳。

当进行任何影响导航、页眉、页脚、侧边栏、主题或布局的更改时：

1. 编辑 `src/appLayout.tsx` —— `routes.tsx` 使用的布局
2. 用应用特定的链接和名称替换所有默认/模板导航项和标签
3. 在所有地方替换占位符应用名称：页眉、导航品牌、页脚、`index.html` 中的 `<title>`

`index.html` 位于 bundle 根目录（不在 `src/` 下），但每当品牌或应用名称更改时，它仍然在这个技能的范围内——剩余的 `<title>React App</title>` / `Vite + React` 模板是一个常见的 ship-blocker，`npm run lint`/`npm run build` 从不捕获它。

完成前，确认：我是否用真实的导航项和品牌更新了 `appLayout.tsx`？然后运行 `scripts/verify-rules.sh` 来检查残留的模板（见验证部分）。

| 内容 | 位置 |
|------|------|
| 布局、导航、品牌 | `src/appLayout.tsx` |
| 文档标题 | `index.html`（bundle 根目录，在 `src/` 外面 —— 仍然在品牌范围内） |
| 根页面内容 | `routes.tsx` 中根路线处的组件 |

---

## React 和 TypeScript 标准

### 路由

使用单个路由包。使用 `createBrowserRouter` / `RouterProvider`，所有导入必须来自 `react-router`（不是 `react-router-dom`）。

如果应用使用客户端路由器（React Router、Remix Router、Vue Router 等），始终从文档的 `<base href>` 标签在运行时派生 basename / basepath / base。永远不要硬编码 basename：

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

应用在动态基本路径后面运行。路由导航（`<Link to>`、`navigate()`）使用绝对路径（`/x`）。非路由属性（`<img src>`）使用点相对路径（`./x`）。优先使用 Vite `import` 来处理静态资源。

### TypeScript

- 从不使用 `any` —— 使用正确的类型、泛型或带类型守卫的 `unknown`
- 事件处理器：`(event: React.FormEvent<HTMLFormElement>): void`
- 状态：`useState<User | null>(null)` —— 始终提供类型参数
- 无不安全断言（`obj as User`）—— 使用类型守卫代替

### 模块限制

React UI bundles 不得导入 Salesforce 平台模块，如 `lightning/*` 或 `@wire`（仅限 LWC）。**在编写任何数据访问代码（GraphQL、REST、SDK 初始化或一个获取数据的钩子）之前，你必须首先调用 `experience-ui-bundle-salesforce-data-access` 技能。** 不要在这个技能中编写 `fetch`/`axios` 调用或编造不同的数据 API —— 即使澄清问题的答案仅隐含数据获取。

---

## 设计思维

本节和“前端美学”下方的规则是创意方向，不是硬约束 —— 它们不能被 lint 或 build 检查，并且由评审而不是自动化判断。两个硬性、可检查的例外：永远不要默认使用 Inter/Roboto/Arial/Space Grotesk/系统字体，以及移动响应性（Tailwind 断点、44px 触摸目标）是一个必须，而不是一个样式偏好。

在编码之前，确定一个大胆的审美方向：

- **目的**：这个界面解决了什么问题？谁使用它？
- **语气**：选择一个清晰的方向 —— 残酷极简、极繁、复古未来主义、有机、奢华、俏皮、编辑、残酷主义、艺术装饰、柔和/粉彩色、工业。使用这些作为灵感，但设计一个忠于上下文的。
- **差异化**：是什么让它难忘？是什么会让某人记住？

选择一个清晰的概念方向，并精确地执行它。大胆的极繁和精致的极简都有效果 —— 关键在于意图性，而不是强度。

---

## 前端美学

- **排版**：选择有特色、有性格的字体。搭配一个展示字体和一个精致的正文字体。永远不要默认使用 Inter、Roboto、Arial、Space Grotesk 或系统字体。
- **颜色**：使用 CSS 变量承诺一个协调的调色板。主导颜色与锐利点缀比胆怯、均匀分布的调色板更胜一筹。避免在白色上的陈词滥调的紫色渐变。
- **动画**：专注于高冲击力时刻 —— 一个精心编排的页面加载，带有分层的揭示（`animation-delay`）比分散的微交互更能带来愉悦。使用滚动触发和悬停状态来惊喜。优先使用纯 CSS 解决方案；当可用时，使用 Motion 库。
- **空间构图**：意想不到的布局 —— 不对称、重叠、对角线流动、打破网格的元素。充足的负空间 OR 控制的密度。
- **背景和深度**：创造氛围，而不是默认使用纯色。渐变网格、噪声纹理、几何图案、分层透明度、戏剧性阴影、装饰性边框、颗粒覆盖。

- **移动响应性**：所有生成的 UI 必须是移动响应的。使用 Tailwind 响应性前缀（`sm:`, `md:`, `lg:`）来适应不同断点的布局。在小屏幕上堆叠列，使用灵活的网格，并确保触摸目标至少为 44px。测试导航、排版和间距在移动视口上是否正常工作。

将实现复杂度与审美愿景相匹配。极繁设计需要复杂的动画和效果。极简设计需要克制、精确和仔细的间距/排版。没有两个设计应该看起来一样 —— 在不同代之间变化主题、字体和美学。

---

## 澄清问题

一次问一个问题，当你有足够的上下文时停止。

### 对于页面
1. 名称和目的？
2. URL 路径？
3. 是否应出现在导航中？
4. 访问控制？（公开、通过 `PrivateRoute` 进行身份验证，或通过 `AuthenticationRoute` 进行非身份验证）
5. 内容部分？（列表、表单、表格、详细信息视图）
6. 数据获取需求？

### 对于页眉 / 页脚
1. 页眉、页脚，还是两者？
2. 内容？（标志、导航链接、用户头像、版权、社交图标）
3. 粘性页眉？
4. 色彩方案或样式方向？

### 对于组件
1. 它应该做什么？
2. 它属于哪个页面？
3. 共享/可重用还是特定于一个功能？
4. 需要哪些数据或属性？
5. 内部状态？（加载中、切换、表单状态）
6. 要使用的特定 shadcn 组件？

---

## 验证

在完成前，从解析的 UI bundle 目录（见“解析 Bundle 目录”上方）运行所有以下内容：

1. `npm run lint` — 必须导致 0 个错误。
2. `npm run build` — 必须成功。
3. `npm run dev`（或项目的 dev-server 脚本）—— 确认应用干净启动，以便在运行时验证更改，而不仅仅是在构建时验证。

**`lint`/`build` 单独不能捕获这个技能中最高风险的规则** —— 一个错误的 `react-router-dom` 导入、一个硬编码的 basename、一个内联 `style={{}}` 或一个 `lightning/*` 导入都可以 lint 和 build 干净，但在运行时崩溃。在触摸路由、布局、样式或模块导入的任何更改后，运行 `scripts/verify-rules.sh <你编辑的文件或目录>`：

- **退出 0**：未发现违规。
- **退出 1**，按规则和文件列出了违规：在考虑任务完成之前，修复每一个，即使 lint 和 build 通过了。
