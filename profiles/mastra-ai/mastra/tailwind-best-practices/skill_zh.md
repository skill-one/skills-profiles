# Tailwind 最佳实践

## 概述

Mastra Playground UI 样式路由和优先级指南，包含 3 类中的 5 条规则。规则文件包含详细的解释、示例和评审指南，以确保设计系统的一致性，防止 token 漂移，并维护组件库的完整性。

## 范围

- `packages/playground-ui`
- `packages/playground`

## 应用时机

在以下情况下参考这些指南：

- 编写带有 Tailwind 样式的 React 组件
- 审查代码以保持样式一致性
- 重构现有的带样式的组件
- 添加或修改 UI 元素

## 优先级排序指南

规则按影响程度排序：

| 优先级 | 类别        | 影响   |
| ------ | ----------- | ------ |
| 1      | 组件使用    | 关键   |
| 2      | 设计 Token   | 关键   |
| 3      | ClassName 使用 | 高     |

## 快速参考

### 关键模式（优先应用）

**组件使用：**

- 使用来自 `@playground-ui/ds/components/` 的现有组件 (`component-use-existing`)
- 不要在 `ds/` 文件夹中创建新组件

**设计 Token：**

- 仅在 `@playground-ui` 中使用 `tailwind.config.ts` 中的 token (`tokens-use-existing`)
- 不要修改设计 token 或 `tailwind.config.ts` (`tokens-no-modification`)

### 高影响模式

**ClassName 使用：**

- 除 `height` 和 `width` 外，不要使用任意的 Tailwind 值 (`classname-no-arbitrary`)
- DS 组件上除 `DialogContent` 和 `Popover` 的 `h-`/`w-` 外，不要使用 `className` 属性 (`classname-no-ds-override`)

## 参考

规则文件是详细指导和示例的权威来源：

- `references/tailwind-best-practices-reference.md` - 按类别顺序排列的规则目录和规则文件路径
- `references/rules/` - 按类别组织的权威单个规则文件

实施或审查特定样式规则时，仅加载相关的规则文件。使用目录选择正确的规则，而无需加载所有示例。

要查找特定模式，在规则目录中执行 grep：

```
grep -l "component" references/rules/
grep -l "token" references/rules/
grep -l "className" references/rules/
```

## `references/rules/` 中的规则类别

- `component-*` - 组件使用规则（1 条规则）
- `tokens-*` - 设计 token 规则（2 条规则）
- `classname-*` - ClassName 使用规则（2 条规则）
