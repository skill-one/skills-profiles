---
name: mantine-custom-components
description: 构建与 Mantine 主题、样式 API 和核心功能集成的自定义组件。在以下情况下使用此技能：(1) 使用 factory()、polymorphicFactory() 或 genericFactory() 创建新组件时，(2) 添加样式 API 支持（classNames、styles、vars、unstyled），(3) 通过 createVarsResolver 实现 CSS 变量，(4) 构建具有子组件和共享上下文的复合组件，(5) 通过 Component.extend() 在 MantineProvider 中注册组件，或 (6) 任何涉及 @mantine/core 中的 Factory、useProps、useStyles、BoxProps、StylesApiProps 或 ElementProps 的任务。
---

# Mantine 自定义组件技能

## 组件模板

```tsx
import {
  Box, BoxProps, createVarsResolver, ElementProps,
  factory, Factory, getRadius, MantineRadius,
  StylesApiProps, useProps, useStyles,
} from '@mantine/core';
import classes from './MyComponent.module.css';

export type MyComponentStylesNames = 'root' | 'inner';
export type MyComponentVariant = 'filled' | 'outline';
export type MyComponentCssVariables = { root: '--my-radius' };

export interface MyComponentProps
  extends BoxProps, StylesApiProps<MyComponentFactory>, ElementProps<'div'> {
  radius?: MantineRadius;
}

export type MyComponentFactory = Factory<{
  props: MyComponentProps;
  ref: HTMLDivElement;
  stylesNames: MyComponentStylesNames;
  vars: MyComponentCssVariables;
  variant: MyComponentVariant;
}>;

const defaultProps = { radius: 'md' } satisfies Partial<MyComponentProps>;

const varsResolver = createVarsResolver<MyComponentFactory>((_theme, { radius }) => ({
  root: { '--my-radius': getRadius(radius) },
}));

export const MyComponent = factory<MyComponentFactory>((_props) => {
  const props = useProps('MyComponent', defaultProps, _props);
  const { classNames, className, style, styles, unstyled, vars, attributes, radius, ...others } = props;

  const getStyles = useStyles<MyComponentFactory>({
    name: 'MyComponent', classes, props,
    className, style, classNames, styles, unstyled, vars, attributes, varsResolver,
  });

  return <Box {...getStyles('root')} {...others} />;
});

MyComponent.displayName = '@mantine/core/MyComponent';
MyComponent.classes = classes;
```

## Factory 变体 — 如何选择

| 场景 | Factory 函数 | 类型 |
|---|---|---|
| 标准组件 | `factory()` | `Factory<{}>` |
| 支持 `component` 属性（多态） | `polymorphicFactory()` | `PolymorphicFactory<{}>` — 添加 `defaultComponent` 和 `defaultRef` |
| 属性根据泛型变化（例如 `multiple`） | `genericFactory()` | `Factory<{ signature: ... }>` |

谨慎使用 `polymorphicFactory` — 它会增加 TypeScript 开销并减慢 IDE 自动补全速度。

## Factory 类型字段

```ts
Factory<{
  props: MyComponentProps;       // 必填
  ref: HTMLDivElement;           // 传递的 ref 的元素类型
  stylesNames: 'root' | 'inner'; // Styles API 选择器的联合
  vars: { root: '--my-var' };    // 每个选择器的 CSS 变量映射
  variant: 'filled' | 'outline'; // 接受的变体字符串
  staticComponents: {            // 子组件（复合模式）
    Item: typeof MyComponentItem;
  };
  compound?: boolean;            // true = 子组件；禁用主题的 classNames/styles/vars
  ctx?: MyContextType;           // 作为第三个参数传递给 styles/vars 解析器
  signature?: (...) => JSX.Element; // 仅用于 genericFactory
}>
```

## 主题集成

用户和主题可以通过 `Component.extend()` 覆盖默认值：

```ts
const theme = createTheme({
  components: {
    MyComponent: MyComponent.extend({
      defaultProps: { radius: 'xl' },
      classNames: { root: 'my-root' },
      styles: { root: { color: 'red' } },
      vars: (_theme, props) => ({ root: { '--my-radius': getRadius(props.radius) } }),
    }),
  },
});
```

## 参考

- **[`references/api.md`](references/api.md)** — 所有导入：`factory`, `useProps`, `useStyles`, `createVarsResolver`, `createSafeContext`, `StylesApiProps`, `CompoundStylesApiProps`, `BoxProps`, `ElementProps`, 主题辅助函数 (`getSize`, `getRadius`, 等)
- **[`references/patterns.md`](references/patterns.md)** — 完整示例：带上下文的复合组件、多态组件、泛型组件、主题集成
