---
name: next-intl-add-language
description: 在 Next.js + next-intl 应用中添加新语言
---

这是一份关于在 Next.js 项目中使用 next-intl 添加新语言的指南，

- 对于国际化（i18n），应用程序使用 next-intl。
- 所有翻译都在 `./messages` 目录中。
- UI 组件是 `src/components/language-toggle.tsx`。
- 路由和中间件配置在以下文件中处理：
  - `src/i18n/routing.ts`
  - `src/middleware.ts`

添加新语言时：

- 将 `en.json` 中的所有内容翻译成新的语言。目标是使新的语言中的所有 JSON 条目完整翻译。
- 在 `routing.ts` 和 `middleware.ts` 中添加路径。
- 在 `language-toggle.tsx` 中添加该语言。
