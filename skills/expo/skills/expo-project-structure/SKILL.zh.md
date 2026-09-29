---
name: expo-project-structure
description: 框架（开源软件）。新Expo应用的文件夹结构。在用Expo Router搭建或布局新Expo项目时使用，或在其中一个决定文件应放置的位置。仅适用于新项目——永远不要重构现有应用以匹配。
---

# Expo 项目结构

一个**全新**Expo 应用的起始骨架——尚未有提交的文件夹结构。

**仅适用于新项目。**如果应用已有布局，请遵循其现有规范并保留文件位置——这是一个默认起点，而非强制标准或迁移目标。当不确定项目是否为新时，请先询问再进行任何操作。

整个布局，根据以下规则组装：

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

将应用代码保留在 `src/` 下，以将其与配置文件分离。Expo Router 支持原生的 `app/` 和 `src/app/` —— 要切换，只需移动文件夹并重启打包器。默认模板在 `tsconfig.json` 中将 `@/*` 别名为 `./src/*`。

`src/app` 仅限**路由**：此处每个文件都成为路由，因此不应在此放置其他内容。以下内容位于同级文件夹中。

## components/ — 可重用 UI

通用、可重用的 UI（按钮、卡片、表格），每个文件具有一个命名导出。文件名使用 **kebab-case** (`bar-chart.tsx`), 匹配默认的 `create-expo-app` 模板。当组件规模增长时，为其创建自己的文件夹，将根文件放在 `index.tsx` 中，并**同位**放置其私有子组件——导入路径 (`@/components/table`) 保持不变。

## screens/ — 屏幕主体

由于 `app/` 文件必须是路由，因此未重用的复杂屏幕 UI 没有适合的位置。当屏幕规模足够大，需要拆分为独立组件时，将其放在 `screens/` 中，并让每个路由仅渲染其屏幕：

```tsx
import { Home } from "@/screens/home";

export default function HomeScreen() {
  // 仅路由特定关注点——例如在此处读取 URL 参数
  return <Home />;
}
```

**同位**放置屏幕的私有组件在其文件夹内 (`screens/home/components/`)。一个额外的优势：同一屏幕可以在多个路由下渲染。

## server/ + app/api/ — 分离服务器代码

在 `app/` 中的文件名追加 `+api` 使其成为服务器 **API 路由**。服务器代码与前端代码不同——它运行在类似 Node 的服务器环境中（通过 EAS Hosting 部署或在 [第三方服务](https://docs.expo.dev/router/web/api-routes/#hosting-on-third-party-services) 上部署），可以读取秘密环境变量 (`process.env.X`，而不仅仅是 `EXPO_PUBLIC_*`)。将其分离：

- 将所有路由分组到 `app/api/` → `/api/user`, `/api/settings`。这会将其同位放置并避免冲突（例如一个 `/user` 屏幕和一个 `/user` 路由）。
- 将共享的服务器端辅助工具放在 `src/server/`。
- 考虑使用 ESLint 规则将 `+api` 文件和 `server/` 与仅前端检查隔离开。

## 平台特定代码

小差异：使用 `Platform.select` / `Platform.OS`。对于较大差异，应拆分为平台文件，而不是内联 `if/else`——`bar-chart.tsx` + `bar-chart.web.tsx`，导入时无扩展名 (`@/components/bar-chart`)；Metro 会根据目标选择正确的文件。

- Props 必须在所有变体中相同。
- 必须有一个默认文件（无平台扩展名）——如果组件是单平台，则将其实现为空操作。
- 支持的扩展名：`.ios`, `.android`, `.native`, `.web`。

## 同位放置样式和测试

- **样式：**将 `StyleSheet.create({ ... })` 对象保留在组件文件底部，而不是在单独的 `.styles` 文件中。
- **测试：**将 `format-date.test.ts` 放在 `format-date.ts` 旁边（优于单独的 `__tests__/` 文件夹），以便测试文件一目了然。

## AI 和配置文件

代理指令位于仓库根目录——`AGENTS.md` / `CLAUDE.md`，项目技能在 `.claude/` 下。其他配置和资源保留在 `src/` 外：`app.json` / `app.config.ts`, `eas.json`, `package.json`, `assets/` 和 `scripts/`。

---

基于 [Expo 应用文件夹结构最佳实践](https://expo.dev/blog/expo-app-folder-structure-best-practices) 由 Kadi Kraman 撰写。关于 `src/` 优先级和别名机制，请参阅 [Expo 文档](https://docs.expo.dev/router/reference/src-directory/)。

## 提交反馈
如果您在技能中遇到错误、误导性或过时的信息，请报告以便 Expo 改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "expo-project-structure" "<可操作的反馈>"
```
仅在您有具体且可操作的反馈时才提交。尽可能包含所有相关上下文。
如果 AI 代理反复失败或用户不得不接管 Expo 任务，加载 `expo-skill-feedback` 技能并遵循其 eval-candidate 流程，而不是重复使用上述命令。
