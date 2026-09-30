---
name: svelte5-best-practices
description: Svelte 5 运行时、代码片段、SvelteKit 模板以及 TypeScript 和组件开发的现代最佳实践。在编写、审查或重构 Svelte 5 组件和 SvelteKit 应用时使用。触发条件：Svelte 组件、运行时（$state、$derived、$effect、$props、$bindable、$inspect）、代码片段（{#snippet}、{@render}）、事件处理、SvelteKit 数据加载、表单操作、Svelte 4 到 Svelte 5 迁移、状态存储到运行时迁移、插槽到代码片段迁移、TypeScript 属性类型定义、泛型组件、服务器端渲染状态隔离、性能优化或组件测试。
---

# Svelte 5 最佳实践

## 快速参考

| 主题 | 使用场景 | 参考 |
|------|----------|------|
| **Runes** | $state, $derived, $effect, $props, $bindable, $inspect | [runes.md](references/runes.md) |
| **Snippets** | 替换插槽, {#snippet}, {@render} | [snippets.md](references/snippets.md) |
| **事件** | onclick 处理器, 回调属性, 上下文 API | [events.md](references/events.md) |
| **TypeScript** | 属性类型定义, 泛型组件 | [typescript.md](references/typescript.md) |
| **迁移** | 从 Svelte 4 迁移到 5, stores 迁移到 runes | [migration.md](references/migration.md) |
| **SvelteKit** | 加载函数, 表单动作, SSR, 页面类型定义 | [sveltekit.md](references/sveltekit.md) |
| **性能** | 全局响应式, 避免 过度响应, 流式传输 | [performance.md](references/performance.md) |

## 基本模式

### 响应式状态

```svelte
<script>
  let count = $state(0);           // 响应式状态
  let doubled = $derived(count * 2); // 计算值
</script>
```

### 组件属性

```svelte
<script>
  let { name, count = 0 } = $props();
  let { value = $bindable() } = $props(); // 双向绑定
</script>
```

### Snippets (替换插槽)

```svelte
<script>
  let { children, header } = $props();
</script>

{@render header?.()}
{@render children()}
```

### 事件处理器

```svelte
<!-- Svelte 5: 使用 onclick, 而不是 on:click -->
<button onclick={() => count++}>点击</button>
```

### 回调属性 (替换 createEventDispatcher)

```svelte
<script>
  let { onclick } = $props();
</script>

<button onclick={() => onclick?.({ data })}>点击</button>
```

## 常见错误

1. **未使用 `$state` 的 `let`** - 变量不使用 `$state()` 就不是响应式的
2. **使用 `$effect` 处理派生值** - 应该使用 `$derived` 而不是
3. **使用 `on:click` 语法** - Svelte 5 应使用 `onclick`
4. **使用 `createEventDispatcher`** - 应使用回调属性替代
5. **使用 `<slot>`** - 应使用 snippets 中的 `{@render}`
6. **忘记 `$bindable()`** - `bind:` 需要 `$bindable()` 才能工作
7. **在 SSR 中设置模块级状态** - 导致跨请求泄露
8. **加载函数中的顺序 await** - 应使用 `Promise.all` 处理并行请求
