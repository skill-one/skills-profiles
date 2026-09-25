# Expo 项目结构

一个**全新**Expo 应用的起始骨架——尚未有提交的文件夹结构。

**仅适用于新项目。**如果应用已存在布局，请遵循其现有约定并将文件保留在原位——这是一个默认起点，而非强制执行的规范或迁移目标。当不确定项目是否为新时，在移动任何内容前请先询问。

整个布局由以下规则组合而成：

```
├── assets/
├── scripts/
├── src/
│   ├── app/                       # Expo Router 路由仅限于此——每个文件都是一个路由
│   │   ├── api/                   #   服务器 API 路由在此处分组
│   │   │   ├── user+api.ts
│   │   │   └── settings+api.ts
│   │   ├── _layout.tsx
│   │   ├── _layout.web.tsx         #   平台特定布局
│   │   ├── index.tsx
│   │   └── settings.tsx
│   ├── components/                 # 可重用 UI：按钮、卡片、表格…
│   │   ├── table/                  #   复杂组件 → 文件夹 + index.tsx
│   │   │   ├── cell.tsx
│   │   │   └── index.tsx
│   │   ├── bar-chart.tsx
│   │   ├── bar-chart.web.tsx        #   平台特定变体
│   │   └── button.tsx
│   ├── screens/                    # 路由文件渲染的屏幕主体
│   │   ├── home/
│   │   │   ├── card.tsx            #   仅 Home 使用——不共享
│   │   │   └── index.tsx           #   由 src/app/index.tsx 渲染
│   │   └── settings.tsx
│   ├── server/                     # 应用 API 使用的服务器端辅助工具
│   │   ├── auth.ts
│   │   └── db.ts
│   ├── utils/                      # 独立辅助工具 + 同位测试
│   │   ├── format-date.ts
│   │   └── format-date.test.ts
│   ├── hooks/                      # 可重用钩子：use-theme.ts…
│   ├── constants.ts
│   └── theme.ts
├── app.json
├── eas.json
└── package.json
```

## `src/` 和 `src/app`

将应用代码保留在 `src/` 下以将其与配置文件分离。Expo Router 同时支持 `app/` 和 `src/app/`，切换只需移动文件夹并重启打包器。默认模板在 `tsconfig.json` 中将 `@/*` 别名为 `./src/*`。

`src/app` 仅限**路由**：此处每个文件都成为路由，因此不应在此放置其他内容。以下内容位于同级文件夹中。

## components/ — 可重用 UI

通用、可重用的 UI（按钮、卡片、表格），每个文件具有一个命名导出。文件名使用**小写连字符**格式（`bar-chart.tsx`），与默认 `create-expo-app` 模板匹配。当组件规模增长时，为其创建自己的文件夹，将根文件放在 `index.tsx` 中，并**同位**放置其私有子组件——导入路径（`@/components/table`）保持不变。

## screens/ — 屏幕主体

由于 `app/` 文件必须是路由，未重用的复杂屏幕 UI 没有适合放置的地方。当屏幕规模足够大需要拆分为独立组件时，将其放入 `screens/` 并让每个路由仅渲染其屏幕：

```tsx
import { Home } from "@/screens/home";

export default function HomeScreen() {
  // 仅路由特定关注点——例如在此处读取 URL 参数
  return <Home />;
}
```

**同位**放置屏幕的私有组件在其文件夹内（`screens/home/components/`）。一个额外的好处：同一屏幕可以在多个路由下渲染。

## server/ + app/api/ — 分离服务器代码

在 `app/` 文件名后附加 `+api` 使其成为服务器**API 路由**。服务器代码与前端代码不同——它运行在类似 Node 的服务器环境（通过 EAS Hosting 部署或在 [第三方服务](https://docs.expo.dev/router/web/api-routes/#hosting-on-third-party-services) 上部署）并可以读取秘密环境变量（`process.env.X`，而不仅仅是 `EXPO_PUBLIC_*`）。将其分离：

- 将所有路由分组到 `app/api/` → `/api/user`，`/api/settings`。这会将其同位放置并避免冲突（例如一个 `/user` 屏幕和一个 `/user` 路由）。
- 将共享的服务器端辅助工具放在 `src/server/`。
- 考虑使用 ESLint 规则将 `+api` 文件和 `server/` 与仅前端检查隔离开。

## 平台特定代码

小差异：使用 `Platform.select` / `Platform.OS`。对于较大差异，应拆分为平台文件而不是内联 `if/else`——`bar-chart.tsx` + `bar-chart.web.tsx`，导入时不带扩展名（`@/components/bar-chart`）；Metro 会根据目标选择正确的文件。

- 所有变体的属性必须完全相同。
- 必须始终有一个默认文件（不带平台扩展名），如果组件是单平台，则将其实现为空操作。
- 支持的扩展名：`.ios`，`.android`，`.native`，`.web`。

## 同位放置样式和测试

- **样式：**将 `StyleSheet.create({ ... })` 对象保留在组件文件底部，而不是在单独的 `.styles` 文件中。
- **测试：**将 `format-date.test.ts` 放在 `format-date.ts` 旁边（优于单独的 `__tests__/` 文件夹），以便测试文件一目了然。

## AI 和配置文件

代理指令位于仓库根目录——`AGENTS.md` / `CLAUDE.md`，项目技能在 `.claude/` 下。其他配置和资源保留在 `src/` 外：`app.json` / `app.config.ts`，`eas.json`，`package.json`，`assets/` 和 `scripts/`。

---

基于 [Expo 应用文件夹结构最佳实践](https://expo.dev/blog/expo-app-folder-structure-best-practices) 由 Kadi Kraman 撰写。关于 `src/` 优先级和别名机制，请参阅 [Expo 文档](https://docs.expo.dev/router/reference/src-directory/)。

## 提交反馈
如果您在技能中遇到错误、误导性或过时的信息，请报告以便 Expo 改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "expo-project-structure" "<可操作的反馈>"
```
仅在您有具体且可操作的反馈时才提交。尽可能包含所有相关上下文。
如果 AI 代理反复失败或用户不得不接管 Expo 任务，加载 `expo-skill-feedback` 技能并遵循其 eval-candidate 流程，而不是重复使用上述命令。
