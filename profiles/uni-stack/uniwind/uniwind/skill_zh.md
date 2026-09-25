# Uniwind

> Uniwind 1.7.0+ / Uniwind Pro 1.2.1+ / Tailwind CSS v4 / React Native 0.81+ / Expo SDK 54+

如果用户版本较低，建议升级到 1.7.0+（免费版）或 1.2.1+（专业版）以获得最佳体验。

从 Uniwind 1.8.0+ 开始，可以使用 `LayoutDirection`。

从 Uniwind 1.11.0+ / Uniwind Pro 1.6.0+ 开始，可以使用 `ScopedVariables`，它将 CSS 变量覆盖作用域限制在组件子树中。

Uniwind 将 Tailwind CSS v4 带到 React Native。所有核心 React Native 组件都内置支持 `className` 属性。样式在构建时编译——没有运行时开销。

## 关键规则

1. **仅限 Tailwind v4** — 使用 `@import 'tailwindcss'` 而不是 `@tailwind base`。Tailwind v3 不被支持。
2. **切勿动态构建 classNames** — Tailwind 在构建时扫描。`bg-${color}-500` 将不会工作。使用完整字符串字面量、映射对象或三元运算符。
3. **切勿使用 `cssInterop` 或 `remapProps`** — 这些是 NativeWind API。Uniwind 不会覆盖全局组件。
4. **无需 `tailwind.config.js`** — 所有配置都通过 `@theme` 和 `@layer theme` 放在 `global.css` 中。
5. **无需 `ThemeProvider`** — 直接使用 `Uniwind.setTheme()`。
6. **`withUniwindConfig` 必须是 Metro 配置的最外层包装器**。
7. **切勿用 `withUniwind` 包裹 `react-native` 或 `react-native-reanimated` 组件** — `View`、`Text`、`Pressable`、`Image`、`TextInput`、`ScrollView`、`FlatList`、`Switch`、`Modal`、`Animated.View`、`Animated.Text` 等组件已经内置完整的 `className` 支持。用 `withUniwind` 包裹它们会破坏行为。仅用于**第三方**组件（例如，`expo-image`、`expo-blur`、`moti`）。
8. **字体家族：仅单个字体** — React Native 不支持后备字体。使用 `--font-sans: 'Roboto-Regular'` 而不是 `'Roboto', sans-serif`。
9. **所有主题变体必须定义相同的 CSS 变量集** — 如果 `light` 定义了 `--color-primary`，那么 `dark` 和所有自定义主题也必须定义。不匹配的变量会导致运行时错误。
10. **非样式颜色属性必须使用 `accent-` 前缀** — 这至关重要。`color`（按钮、ActivityIndicatorView）、`tintColor`（Image）、`thumbColor`（Switch）、`placeholderTextColor`（TextInput）等属性不属于 `style` 对象。你必须使用带有 `accent-` 前缀类的相应 `{propName}ClassName` 属性。示例：`<ActivityIndicator colorClassName="accent-blue-500" />` 而不是 `<ActivityIndicator className="text-blue-500" />`。常规的 Tailwind 颜色类（如 `text-blue-500`）仅适用于 `className`（映射到 `style`）。对于非样式颜色属性，始终使用 `accent-`。
11. **rem 默认值为 16px** — NativeWind 使用 14px。如果迁移，请在 metro 配置中设置 `polyfills: { rem: 14 }`。
12. **`cssEntryFile` 必须是相对路径字符串** — 使用 `'./global.css'` 而不是 `path.resolve(__dirname, 'global.css')`。
13. **混合自定义 CSS 类和 Tailwind 时使用 `cn()` 去重** — Uniwind 不会自动去重。如果自定义 CSS 类（`.card { padding: 16px }`）和 Tailwind 工具类（`p-6`）设置相同的属性，两者都会应用，结果不可预测。当存在重叠时，始终使用 `cn('card', 'p-6')`。
14. **支持重要工具类** — 尾随 `!` 的 Tailwind 重要修饰符在 classNames 中有效：`bg-red-500!`、`active:bg-red-500!`、`ios:pt-12!`。前置 `!bg-red-500` 语法已弃用。重要工具类会覆盖相同样式属性的普通工具类，但内联 `style` 仍会覆盖 className。

## 参考路由

在确定用户任务后，仅阅读 `references/` 下相关的捆绑参考文件：

- 设置/配置安装问题：`references/setup.md`
- React Native 组件的 `className` 属性、`accent` 颜色属性或组件示例：`references/component-bindings.md`
- 第三方组件、`withUniwind`、动态类名、`tailwind-variants`、`cn` 或重要工具类：`references/styling-patterns.md`
- 主题、CSS 变量、`ScopedTheme`、`LayoutDirection`、颜色空间或运行时变量 API：`references/theming.md`
- 平台、数据、状态、响应式或安全区域工具类：`references/variants-and-selectors.md`
- CSS 函数、自定义 CSS、`@utility`、`@theme`、字体或渐变：`references/css-and-utilities.md`
- React Navigation、UI 套件、支持矩阵或不受支持的类：`references/integrations.md`
- Uniwind Pro 安装、动画、诊断、分组变体、默认样式、原生内边距或主题过渡：`references/pro.md`
- 破坏样式、设置诊断、错误、缓存问题、FAQ 答案、MCP 或相关技能：`references/troubleshooting.md`

## 工作流程

1. 确定用户是否需要设置、样式、主题、变体、集成、Pro 或故障排除帮助。
2. 在提供详细指导或编辑代码前，阅读匹配的参考文件。
3. 即使选定的参考文件省略了它们，也必须应用上述关键规则。
4. 不要猜测 Uniwind API。如有疑问，请对照官方文档：https://docs.uniwind.dev/llms-full.txt

## 相关技能

NativeWind 迁移有意分开。当用户希望从 NativeWind 迁移时，使用 `migrate-nativewind-to-uniwind` 技能。
