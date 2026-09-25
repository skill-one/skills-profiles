# @json-render/directives

`@json-render/core` 的预构建自定义指令。将它们放入您的目录和渲染器中，以添加格式化、数学、字符串操作和国际化功能。

## 快速入门

```typescript
import { standardDirectives } from '@json-render/directives';

// 连接到提示生成
const prompt = catalog.prompt({ directives: standardDirectives });

// 连接到渲染器（React 示例）
import { JSONUIProvider, Renderer } from '@json-render/react';

<JSONUIProvider registry={registry} directives={standardDirectives}>
  <Renderer spec={spec} registry={registry} />
</JSONUIProvider>
```

要添加工厂指令（如 `createI18nDirective`），请展开数组：

```typescript
import { standardDirectives, createI18nDirective } from '@json-render/directives';

const directives = [...standardDirectives, createI18nDirective(config)];
```

## 定义自定义指令

使用 `@json-render/core` 中的 `defineDirective`：

```typescript
import { defineDirective, resolvePropValue } from '@json-render/core';
import { z } from 'zod';

const doubleDirective = defineDirective({
  name: '$double',
  description: '将数值翻倍。',
  schema: z.object({
    $double: z.unknown(),
  }),
  resolve(value, ctx) {
    const resolved = resolvePropValue(value.$double, ctx);
    return (resolved as number) * 2;
  },
});
```

规则：
- 名称必须以 `$` 开头
- 名称不能与内置键冲突（`$state`、`$cond`、`$computed`、`$template`、`$item`、`$index`、`$bindState`、`$bindItem`）
- 解析器应调用 `resolvePropValue` 来处理子值，以支持组合

## 内置指令

### `$format` — 基于区域设置的价值格式化

使用 `Intl` 格式化器格式化值。支持 `date`、`currency`、`number` 和 `percent`。

```json
{ "$format": "currency", "value": { "$state": "/cart/total" }, "currency": "USD" }
{ "$format": "date", "value": { "$state": "/user/createdAt" } }
{ "$format": "number", "value": 1234567, "notation": "compact" }
{ "$format": "percent", "value": 0.75 }
{ "$format": "date", "value": { "$state": "/post/createdAt" }, "style": "relative" }
```

字段：`$format`（date | currency | number | percent）、`value`（任何表达式）、`locale?`（字符串）、`currency?`（字符串，默认 "USD"）、`notation?`（字符串）、`style?`（"relative" 用于相对日期）、`options?`（额外的 Intl 选项）。

### `$math` — 算术运算

```json
{ "$math": "add", "a": { "$state": "/subtotal" }, "b": { "$state": "/tax" } }
{ "$math": "round", "a": 3.7 }
```

运算：`add`、`subtract`、`multiply`、`divide`、`mod`、`min`、`max`、`round`、`floor`、`ceil`、`abs`。一元运算（`round`、`floor`、`ceil`、`abs`）仅使用 `a`。除以零返回 `0`。

字段：`$math`（操作枚举）、`a?`（第一个操作数，默认 0）、`b?`（第二个操作数，默认 0）。

### `$concat` — 字符串连接

```json
{ "$concat": [{ "$state": "/user/firstName" }, " ", { "$state": "/user/lastName" }] }
```

字段：`$concat`（要解析并连接为字符串的值数组）。

### `$count` — 数组/字符串长度

```json
{ "$count": { "$state": "/cart/items" } }
```

返回数组或字符串的 `.length`，其他类型返回 `0`。

字段：`$count`（要计数的值）。

### `$truncate` — 文本截断

```json
{ "$truncate": { "$state": "/post/body" }, "length": 140, "suffix": "..." }
```

字段：`$truncate`（要截断的值）、`length?`（最大字符数，默认 100）、`suffix?`（字符串，默认 "..."）。

### `$pluralize` — 单数/复数形式

```json
{ "$pluralize": { "$state": "/cart/itemCount" }, "one": "item", "other": "items", "zero": "no items" }
```

输出：`"3 items"`、`"1 item"` 或 `"no items"`。

字段：`$pluralize`（计数值）、`one`（单数标签）、`other`（复数标签）、`zero?`（零标签）。

### `$join` — 连接数组元素

```json
{ "$join": { "$state": "/tags" }, "separator": ", " }
```

字段：`$join`（要连接的数组）、`separator?`（字符串，默认 ", "）。

### `createI18nDirective` — 国际化工厂

```typescript
import { createI18nDirective } from '@json-render/directives';

const tDirective = createI18nDirective({
  locale: 'en',
  messages: {
    en: { "greeting": "Hello, {{name}}!", "checkout.submit": "Place Order" },
    es: { "greeting": "Hola, {{name}}!", "checkout.submit": "Realizar Pedido" },
  },
  fallbackLocale: 'en',
});
```

在规范中使用：

```json
{ "$t": "checkout.submit" }
{ "$t": "greeting", "params": { "name": { "$state": "/user/name" } } }
```

字段：`$t`（翻译键）、`params?`（插值参数，值接受表达式）。

配置：`locale`（当前区域设置）、`messages`（Record<locale, Record<key, string>>）、`fallbackLocale?`（键缺失时的回退区域设置）。

## 组合

指令自然组合——每个解析器在其输入上调用 `resolvePropValue`，因此指令可以包装其他指令或内置表达式：

```json
{
  "$format": "currency",
  "value": { "$math": "multiply", "a": { "$state": "/price" }, "b": { "$state": "/qty" } },
  "currency": "USD"
}
```

从内向外解析：`$state` 从状态中读取，`$math` 执行乘法，`$format` 以货币格式化。

## 连接到渲染器

四个渲染器（React、Vue、Svelte、Solid）都可以在其提供者和 `createRenderer` 输出中接受 `directives`：

```tsx
// 提供者模式
<JSONUIProvider registry={registry} directives={directives}>
  <Renderer spec={spec} registry={registry} />
</JSONUIProvider>

// createRenderer 模式
const MyRenderer = createRenderer(catalog, components);
<MyRenderer spec={spec} directives={directives} />
```

对于提示生成，传递相同的数组：

```typescript
const prompt = catalog.prompt({ directives });
```

## 关键导出

| 导出 | 目的 |
|------|------|
| `formatDirective` | `$format` 指令定义 |
| `mathDirective` | `$math` 指令定义 |
| `concatDirective` | `$concat` 指令定义 |
| `countDirective` | `$count` 指令定义 |
| `truncateDirective` | `$truncate` 指令定义 |
| `pluralizeDirective` | `$pluralize` 指令定义 |
| `joinDirective` | `$join` 指令定义 |
| `createI18nDirective` | `$t` 国际化指令的工厂 |
| `standardDirectives` | 7 个非工厂指令的数组 |
| `I18nConfig` | 国际化配置的类型 |
