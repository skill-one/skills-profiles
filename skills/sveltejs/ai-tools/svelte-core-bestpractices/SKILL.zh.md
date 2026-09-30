---
name: svelte-core-bestpractices
description: 编写快速、健壮、现代的 Svelte 代码指南。在 Svelte 项目中，当被要求编写、编辑或分析 Svelte 组件或模块时，请加载此技能。涵盖响应式、事件处理、样式、与库集成等更多内容。
---

## `$state`

仅将 `$state` rune 用于需要_响应式_的变量——换句话说，那些会导致 `$effect`、`$derived` 或模板表达式更新的变量。其他所有变量都可以是普通变量。

对象和数组（`$state({...})` 或 `$state([...])`）会变成深度响应式，这意味着它们的变异将触发更新。这存在权衡：为了获得细粒度的响应性，对象必须被代理，这会带来性能开销。在处理只重新赋值而不变异的大型对象时，可以使用 `$state.raw`。例如，API 响应通常就是这种情况。

## `$derived`

要从状态中计算某个值，请使用 `$derived` 而不是 `$effect`：

```js
// 应该这样做
let square = $derived(num * num);

// 不要这样做
let square;

$effect(() => {
	square = num * num;
});
```

> [!NOTE] `$derived` 被赋予一个表达式，而不是一个函数。如果您需要使用函数（例如，因为表达式很复杂），请使用 `$derived.by`。

派生值是可写的——您可以像 `$state` 一样为它们赋值，但它们会在表达式变化时重新计算。

如果派生表达式是一个对象或数组，它将原样返回——它不会被变成深度响应式。但是，在极少数需要这种情况时，您可以在 `$derived.by` 中使用 `$state`。

## `$effect`

Effect 是一个逃逸通道，并且应该尽量避免使用。特别是，应避免在 effect 中更新状态。

- 如果您需要将状态同步到外部库（如 D3），通常使用 [`{@attach ...}`](references/attach.md) 会更整洁
- 如果您需要在用户交互时运行一些代码，请将代码直接放在事件处理程序中，或根据需要使用 [函数绑定](references/bind.md)
- 如果您需要为调试目的记录值，请使用 [`$inspect`](references/inspect.md)
- 如果您需要观察 Svelte 外部的事物，请使用 [`createSubscriber`](references/svelte-reactivity.md)

永远不要将 effect 的内容包裹在 `if (browser) {...}` 或类似的代码中——effect 不会在服务器上运行。

## `$props`

将 props 视为可能会变化。例如，依赖于 props 的值通常应该使用 `$derived`：

```js
// @errors: 2451
let { type } = $props();

// 应该这样做
let color = $derived(type === 'danger' ? 'red' : 'green');

// 不要这样做——如果 `type` 变化，`color` 将不会更新
let color = type === 'danger' ? 'red' : 'green';
```

## `$inspect.trace`

`$inspect.trace` 是一个用于响应性的调试工具。如果某物没有正确更新或运行得比预期多，您可以将其作为 `$effect` 或 `$derived.by`（或它们调用的任何函数）的第一行添加 `$inspect.trace(label)` 来跟踪它们的依赖关系，并发现是哪个触发了更新。

## 事件

以 `on` 开头的任何元素属性都被视为事件监听器：

```svelte
<button onclick={() => {...}}>点击我</button>

<!-- 属性简写也有效 -->
<button {onclick}>...</button>

<!-- 传播属性也有效 -->
<button {...props}>...</button>
```

如果您需要将监听器附加到 `window` 或 `document`，可以使用 `<svelte:window>` 和 `<svelte:document>`：

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

> [!NOTE] 在组件顶层（即不在元素或块内部）声明的 snippet 可以在 `<script>` 中引用。如果一个 snippet 不引用组件状态，它也可以在 `<script module>` 中使用，在这种情况下，它可以被导出供其他组件使用。

## Each blocks

建议使用 [键控 each blocks](references/each.md)——这可以通过允许 Svelte 逐个插入或删除项目来提高性能，而不是更新现有项目的 DOM。

> [!NOTE] 键必须唯一标识对象。不要使用索引作为键。

如果您需要变异项目（例如，使用 `bind:value={item.count}`），请避免解构。

## 在 CSS 中使用 JavaScript 变量

如果您有一个想在 CSS 中使用的 JS 变量，可以使用 `style:` 指令设置一个 CSS 自定义属性。

```svelte
<div style:--columns={columns}>...</div>
```

然后可以在组件的 `<style>` 中引用 `var(--columns)`。

## 样式化子组件

组件的 `<style>` 中的 CSS 是作用域于该组件的。如果父组件需要控制子组件的样式，首选的方法是使用 CSS 自定义属性：

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

如果使用 5.36 或更高版本，您可以使用 [await 表达式](references/await-expressions.md) 和 [hydratable](references/hydratable.md) 直接在组件中使用 promise。请注意，这些需要 `svelte.config.js` 中启用 `experimental.async` 选项，因为它们尚未被视为完全稳定。

## 避免 legacy 功能

始终使用 runes 模式编写新代码，并避免具有更现代替代方案的功能：

- 使用 `$state` 而不是隐式响应性（例如 `let count = 0; count += 1`）
- 使用 `$derived` 和 `$effect` 而不是 `$:` 赋值和语句（但只有在没有更好的解决方案时才使用 effect）
- 使用 `$props` 而不是 `export let`、`$$props` 和 `$$restProps`
- 使用 `onclick={...}` 而不是 `on:click={...}`
- 使用 `{#snippet ...}` 和 `{@render ...}` 而不是 `<slot>`、`$$slots` 和 `<svelte:fragment>`
- 使用 `<DynamicComponent>` 而不是 `<svelte:component this={DynamicComponent}>`
- 使用 `import Self from './ThisComponent.svelte'` 和 `<Self>` 而不是 `<svelte:self>`
- 使用带有 `$state` 字段的类来在组件之间共享响应性，而不是使用 stores
- 使用 `{@attach ...}` 而不是 `use:action`
- 在 `class` 属性中使用 clsx-style 数组和对象，而不是 `class:` 指令
