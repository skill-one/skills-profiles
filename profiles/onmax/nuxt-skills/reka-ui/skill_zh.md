# Reka UI

无样式、可访问的 Vue 3 组件原语。符合 WAI-ARIA 标准。之前为 Radix Vue。

**当前版本：** v2.8.0 (2026年1月)

## 何时使用

- 从零开始构建无样式/无样式组件
- 需要符合 WAI-ARIA 标准的组件
- 使用 Nuxt UI、shadcn-vue 或其他基于 Reka 的库
- 实现可访问的表单、对话框、菜单、弹出框

**对于 Vue 模式：** 使用 `vue` 技能

## 可用指南

| 文件                                                     | 主题                                                              |
| -------------------------------------------------------- | ------------------------------------------------------------------- |
| **[references/components.md](references/components.md)** | 按类别索引的组件 (表单、日期、覆盖层、菜单、数据等)                  |
| **components/\*.md**                                     | 每个组件的详细信息 (dialog.md、select.md 等)                  |

**指南** (参见 [reka-ui.com](https://reka-ui.com))：样式、动画、组合、SSR、命名空间、日期、i18n、受控状态、注入上下文、虚拟化、迁移

## 加载文件

**根据您的任务考虑加载这些参考文件：**

- [ ] [references/components.md](references/components.md) - 如果按类别浏览组件索引或搜索特定组件

**不要一次性加载所有文件。** 仅加载与当前任务相关的文件。

**对于基于 Reka UI 构建的样式化 Nuxt 组件：** 使用 **nuxt-ui** 技能

## 关键概念

| 概念                 | 描述                                                           |
| ----------------------- | --------------------------------------------------------------------- |
| `asChild`               | 作为子元素渲染而不是包装器，合并属性/行为                      |
| Controlled/Uncontrolled | 使用 `v-model` 进行受控，`default*` 属性进行非受控               |
| Parts                   | 组件拆分为 Root、Trigger、Content、Portal 等                  |
| `forceMount`            | 为动画库保留元素在 DOM 中                                |
| Virtualization          | 使用虚拟滚动优化大型列表 (Combobox、Listbox、Tree)             |
| Context Injection       | 从子组件访问组件上下文                                        |

## 安装

```ts
// nuxt.config.ts (自动导入所有组件)
export default defineNuxtConfig({
  modules: ['reka-ui/nuxt']
})
```

```ts
import { RekaResolver } from 'reka-ui/resolver'
// vite.config.ts (带自动导入解析器)
import Components from 'unplugin-vue-components/vite'

export default defineConfig({
  plugins: [
    vue(),
    Components({ resolvers: [RekaResolver()] })
  ]
})
```

## 基本模式

```vue
<!-- 带受控状态的对话框 -->
<script setup>
import { DialogRoot, DialogTrigger, DialogPortal, DialogOverlay, DialogContent, DialogTitle, DialogDescription, DialogClose } from 'reka-ui'
const open = ref(false)
</script>

<template>
  <DialogRoot v-model:open="open">
    <DialogTrigger>Open</DialogTrigger>
    <DialogPortal>
      <DialogOverlay class="fixed inset-0 bg-black/50" />
      <DialogContent class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-white p-6 rounded">
        <DialogTitle>Title</DialogTitle>
        <DialogDescription>Description</DialogDescription>
        <DialogClose>Close</DialogClose>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>
```

```vue
<!-- 带非受控默认值的 Select -->
<SelectRoot default-value="apple">
  <SelectTrigger>
    <SelectValue placeholder="Pick fruit" />
  </SelectTrigger>
  <SelectPortal>
    <SelectContent>
      <SelectViewport>
        <SelectItem value="apple"><SelectItemText>Apple</SelectItemText></SelectItem>
        <SelectItem value="banana"><SelectItemText>Banana</SelectItemText></SelectItem>
      </SelectViewport>
    </SelectContent>
  </SelectPortal>
</SelectRoot>
```

```vue
<!-- asChild 用于自定义触发元素 -->
<DialogTrigger as-child>
  <button class="my-custom-button">Open</button>
</DialogTrigger>
```

## 最近更新 (v2.6.0-v2.8.0)

- **新组件**：Rating (v2.8.0)
- **ScrollArea**：添加了 "glimpse" 滚动条模式 (v2.8.0)
- **PopperContent**：添加了 `hideShiftedArrow` 属性 (v2.8.0)
- **TimeField**：添加了 `stepSnapping` 支持 (v2.8.0)
- **破坏性**：`weekStartsOn` 现在对于日期组件是语言无关的 (v2.8.0)
- **Virtualization**：`estimateSize` 接受函数用于 Listbox/Tree (v2.7.0)
- **Composables**：暴露了 `useLocale`、`useDirection` (v2.6.0)
- **Select**：Content 上添加了 `disableOutsidePointerEvents` 属性 (v2.7.0)
- **Toast**：`disableSwipe` 属性 (v2.6.0)

## 资源

- [Reka UI 文档](https://reka-ui.com)
- [GitHub](https://github.com/unovue/reka-ui)
- [Nuxt UI](https://ui.nuxt.com) (样式化的 Reka 组件)
- [shadcn-vue](https://www.shadcn-vue.com) (样式化的 Reka 组件)

---

_令牌效率：~350 个基础令牌，components.md 索引 ~100 个令牌，每个组件 ~50-150 个令牌_
