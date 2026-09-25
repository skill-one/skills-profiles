## `$state`

仅将 `$state` 字符用于需要 _响应式_ 的变量——换句话说，那些会导致 `$effect`、`$derived` 或模板表达式更新的变量。其他所有情况都可以使用普通变量。

对象和数组（`$state({...})` 或 `$state([...])`）会变成深度响应式，这意味着它们的变更将触发更新。这存在权衡：为了实现细粒度响应式，对象必须被代理，这会带来性能开销。在处理只重新赋值而不进行变更的大型对象时，应使用 `$state.raw`。API 响应通常就是这种情况。

## `$derived`

要从状态中计算值，请使用 `$derived` 而不是 `$effect`：

```js
// 应该这样做
let square = $derived(num * num);

// 不要这样做
let square;

$effect(() => {
	square = num * num;
});
```

> [!NOTE] `$derived` 接收表达式，而不是函数。如果需要使用函数（例如，因为表达式很复杂），请使用 `$derived.by`。

派生值是可写的——你可以像 `$state` 一样对它们赋值，但它们会在表达式变化时重新计算。

如果派生表达式是对象或数组，它将原样返回——它不会被变成深度响应式。然而，在极少数需要这种情况时，你可以在 `$derived.by` 中使用 `$state`。

## `$effect`

效果是一个逃逸通道，应尽量避免使用。特别是，应避免在效果中更新状态。

- 如果需要将状态同步到外部库（如 D3），通常使用 [`{@attach ...}`](references/attach.md) 更简洁
- 如果需要在用户交互时运行代码，请直接将代码放在事件处理程序中，或根据需要使用 [函数绑定](references/bind.md)
- 如果需要为调试目的记录值，请使用 [`$inspect`](references/inspect.md)
- 如果需要观察 Svelte 外部的事物，请使用 [`createSubscriber`](references/svelte-reactivity.md)

永远不要在效果的内容中包裹 `if (browser) {...}` 或类似的代码——效果不会在服务器上运行。

## `$props`

将 props 视为可能会变化。例如，依赖于 props 的值通常应使用 `$derived`：

```js
// @errors: 2451
let { type } = $props();

// 应该这样做
let color = $derived(type === 'danger' ? 'red' : 'green');

// 不要这样做——如果 `type` 变化，`color` 将不会更新
let color = type === 'danger' ? 'red' : 'green';
```

## `$inspect.trace`

`$inspect.trace` 是一个用于响应式的调试工具。如果某事物没有正确更新或运行得比预期多，你可以将其作为 `$effect` 或 `$derived.by`（或它们调用的任何函数）的第一行添加 `$inspect.trace(label)`，以追踪它们的依赖关系并发现是哪个触发了更新。

## 事件

以 `on` 开头的任何元素属性都被视为事件监听器：

```svelte
<button onclick={() => {...}}>点击我</button>

<!-- 属性简写也有效 -->
<button {onclick}>...</button>

<!-- 传播属性也有效 -->
<button {...props}>...</button>
```

如果你需要将监听器附加到 `window` 或 `document`，可以使用 `<svelte:window>` 和 `<svelte:document>`：

```svelte
<svelte:window onkeydown={...} />
<svelte:document onvisibilitychange={...} />
```

避免使用 `onMount` 或 `$effect` 来实现这一点。

## Snippets

[Snippets](references/snippet.md) 是一种定义可重用标记块的方式，可以使用 [`{@render ...}`](references/render.md) 标签实例化它们，或作为 props 传递给组件。它们必须在模板中声明。

```svelte
{#snippet greeting(name)}
	<p>hello {name}!</p>
{/snippet}

{@render greeting('world')}
```

> [!NOTE] 在组件顶层（即不在元素或块内部）声明的 snippets 可以在 `<script>` 中引用。如果一个 snippet 不引用组件状态，它也可以在 `<script module>` 中使用，在这种情况下，它可以被导出供其他组件使用。

## Each blocks

优先使用 [键控 each blocks](references/each.md)——这可以通过允许 Svelte 逐个插入或删除项目来提高性能，而不是更新现有项目的 DOM。

> [!NOTE] 键必须唯一标识对象。不要使用索引作为键。

如果你需要修改项目（例如使用 `bind:value={item.count}`），则避免解构。

## 在 CSS 中使用 JavaScript 变量

如果你有一个想在 CSS 中使用的 JS 变量，可以使用 `style:` 指令设置一个 CSS 自定义属性。

```svelte
<div style:--columns={columns}>...</div>
```

然后可以在组件的 `<style>` 中引用 `var(--columns)`。

## 样式化子组件

组件的 `<style>` 中的 CSS 是作用域化的。如果父组件需要控制子组件的样式，首选的方法是使用 CSS 自定义属性：

```svelte
<!-- Parent.svelte -->
<Child --color="red" />

<!-- Child.svelte -->
<h1>Hello</h1>

<style>
	h1 {
		color: var(--color);
	}
</style>
```

如果这不可能（例如，子组件来自库），可以使用 `:global` 来覆盖样式：

```svelte
<div>
	<Child />
</div>

<style>
	div :global {
		h1 {
			color: red;
		}
	}
</style>
```

## Context

考虑使用上下文而不是在共享模块中声明状态。这将使状态作用域到需要它的应用部分，并消除它在服务器端渲染时在用户之间泄漏的可能性。

使用 `createContext` 而不是 `setContext` 和 `getContext`，因为它提供了类型安全。

## Async Svelte

如果使用 5.36 或更高版本，可以使用 [await 表达式](references/await-expressions.md) 和 [hydratable](references/hydratable.md) 直接在组件中使用 promise。请注意，这些需要 `svelte.config.js` 中启用 `experimental.async` 选项，因为它们目前尚未被视为完全稳定。

## 避免遗留特性

始终使用 runes 模式编写新代码，并避免具有更现代替代方案的特性：

- 使用 `$state` 而不是隐式响应式（例如 `let count = 0; count += 1`）
- 使用 `$derived` 和 `$effect` 而不是 `$:` 赋值和语句（但只有在没有更好的解决方案时才使用效果）
- 使用 `$props` 而不是 `export let`、`$$props` 和 `$$restProps`
- 使用 `onclick={...}` 而不是 `on:click={...}`
- 使用 `{#snippet ...}` 和 `{@render ...}` 而不是 `<slot>`、`$$slots` 和 `<svelte:fragment>`
- 使用 `<DynamicComponent>` 而不是 `<svelte:component this={DynamicComponent}>`
- 使用 `import Self from './ThisComponent.svelte'` 和 `<Self>` 而不是 `<svelte:self>`
- 使用带有 `$state` 字段的类来在组件之间共享响应式，而不是使用 stores
- 使用 `{@attach ...}` 而不是 `use:action`
- 在 `class` 属性中使用 clsx-style 数组和对象，而不是 `class:` 指令
