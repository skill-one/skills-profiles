这是一份关于如何使用 next-intl 为 Next.js 项目添加新语言的国际化指南，

- 对于国际化，应用程序使用 next-intl。
- 所有翻译都在 `./messages` 目录中。
- UI 组件是 `src/components/language-toggle.tsx`。
- 路由和中间件配置在以下位置处理：
  - `src/i18n/routing.ts`
  - `src/middleware.ts`

添加新语言时：

- 将 `en.json` 中的所有内容翻译成新语言。目标是使新语言中的所有 JSON 条目完整翻译。
- 在 `routing.ts` 和 `middleware.ts` 中添加路径。
- 在 `language-toggle.tsx` 中添加语言。
