# unit-test-vue-pinia

使用此技能创建或审查 Vue 组件、可组合项和 Pinia 存储的单元测试。保持测试简洁、确定性和行为优先。

## 工作流程

1. 首先确定行为边界：组件 UI 行为、可组合项行为或存储行为。
2. 选择能够证明该行为的最窄测试风格。
3. 使用最不强大的 Pinia 选项来覆盖场景。
4. 通过公共输入（如 props、表单更新、按钮点击、发出的事件和存储 API）驱动测试。
5. 在考虑任何实例级断言之前，断言可观察的输出和副作用。
6. 返回或审查具有清晰行为导向名称的测试，并记录任何剩余的覆盖范围差距。

## 核心规则

- 每个测试测试一个行为。
- 首先断言可观察的输入/输出行为（渲染的文本、发出的事件、回调调用、存储状态变化）。
- 避免与实现相关的断言。
- 仅在没有任何合理的 DOM、props、emit 或存储级断言的情况下，才访问 `wrapper.vm`。
- 优先在 `beforeEach()` 中进行显式设置，并在每个测试中重置模拟。
- 使用 `references/pinia-patterns.md` 中的已提交参考材料作为标准 Pinia 测试设置的本地事实来源。

## Pinia 测试方法

首先使用 `references/pinia-patterns.md`，如果已提交的示例不涵盖情况，则回退到 Pinia 的测试食谱。

### 组件测试的默认模式

在挂载时使用 `createTestingPinia` 作为全局插件。
优先使用 `createSpy: vi.fn` 作为默认值，以保持一致性并更容易进行动作-监视断言。

```ts
const wrapper = mount(ComponentUnderTest, {
	global: {
		plugins: [
			createTestingPinia({
				createSpy: vi.fn,
			}),
		],
	},
});
```

默认情况下，动作被模拟和监视。
当测试只需要验证动作是否被调用（或未被调用）时，使用 `stubActions: true`（默认值）。

### 接受的最小 Pinia 设置

以下也是有效的，不应标记为错误：

- 当测试不断言 Pinia 动作监视行为时，使用 `createTestingPinia({})`。
- 当测试只需要状态播种或动作模拟行为，并且不检查生成的监视器时，使用 `createTestingPinia({ initialState: ... })` 或 `createTestingPinia({ stubActions: ... })` 而不使用 `createSpy`。
- 在需要模拟/播种依赖存储的存储/可组合项测试中（不挂载组件时），使用 `setActivePinia(createTestingPinia(...))`。

当动作监视断言是测试意图的一部分时，使用 `createSpy: vi.fn`。

### 仅在需要时执行实际动作

仅当测试必须验证动作的实际行为和副作用时，使用 `stubActions: false`。不要默认启用它以进行简单的“是否被调用”断言。

```ts
const wrapper = mount(ComponentUnderTest, {
	global: {
		plugins: [
			createTestingPinia({
				createSpy: vi.fn,
				stubActions: false,
			}),
		],
	},
});
```

### 使用 `initialState` 播种存储状态

```ts
const wrapper = mount(ComponentUnderTest, {
	global: {
		plugins: [
			createTestingPinia({
				createSpy: vi.fn,
				initialState: {
					counter: { n: 20 },
					user: { name: "Leia Organa" },
				},
			}),
		],
	},
});
```

### 通过 `createTestingPinia` 添加 Pinia 插件

```ts
const wrapper = mount(ComponentUnderTest, {
	global: {
		plugins: [
			createTestingPinia({
				createSpy: vi.fn,
				plugins: [myPiniaPlugin],
			}),
		],
	},
});
```

### 边缘情况的获取器覆盖模式

```ts
const pinia = createTestingPinia({ createSpy: vi.fn });
const store = useCounterStore(pinia);

store.double = 999;
// @ts-expect-error 仅用于测试的覆盖器重置
store.double = undefined;
```

### 纯存储单元测试

当目标是验证存储状态转换和动作行为而不需要组件渲染时，优先使用 `createPinia()` 进行纯存储测试。仅在需要模拟依赖存储、播种测试双倍或动作监视器时，才使用 `createTestingPinia()`。

```ts
beforeEach(() => {
	setActivePinia(createPinia());
});

it("increments", () => {
	const counter = useCounterStore();
	counter.increment();
	expect(counter.n).toBe(1);
});
```

## Vue Test Utils 方法

遵循 Vue Test Utils 指导：<https://test-utils.vuejs.org/guide/>

- 默认情况下通过浅层挂载进行聚焦的单元测试。
- 仅当集成行为是主题时，才挂载完整的组件树。
- 通过 props、用户类交互和发出的事件驱动行为。
- 优先使用 `findComponent(...).vm.$emit(...)` 而不是触摸父级内部，用于子级模拟事件。
- 仅在更新为异步时使用 `nextTick`。
- 使用 `wrapper.emitted(...)` 断言发出的事件和有效负载。
- 仅在没有任何 DOM 断言、发出事件断言、props 断言或存储级断言可以表达行为时，访问 `wrapper.vm`。将其视为例外情况，并保持断言范围狭窄。

## 关键测试片段

发出并断言有效负载：

```ts
await wrapper.find("button").trigger("click");
expect(wrapper.emitted("submit")?.[0]?.[0]).toBe("Mango Mission");
```

更新输入并断言输出：

```ts
await wrapper.find("input").setValue("Agent Violet");
await wrapper.find("form").trigger("submit");
expect(wrapper.emitted("save")?.[0]?.[0]).toBe("Agent Violet");
```

## 测试编写工作流程

1. 确定要测试的行为边界。
2. 构建最小的固定数据（仅包含该行为所需的字段）。
3. 配置 Pinia 和所需的测试双倍。
4. 通过公共输入触发行为。
5. 断言公共输出和副作用。
6. 重构测试名称以描述行为，而不是实现。

## 限制和安全

- 不要测试私有/内部实现细节。
- 不要过度使用快照来测试动态 UI 行为。
- 如果只有一个行为重要，不要断言大型对象中的每个字段。
- 保持假数据确定性强；避免随机值。
- 当上述接受的极小设置之一是错误时，不要声称 Pinia 设置是错误的。
- 除非测试的行为需要额外的表面区域，否则不要将工作测试重写为更深的挂载或实际动作。
- 在审查期间明确标记缺失的测试覆盖范围、易碎的选择器和与实现相关的断言。

## 输出契约

- 对于 `create` 或 `update`，返回完成的测试代码以及简短说明所选 Pinia 策略的注释。
- 对于 `review`，首先返回具体发现，然后是缺失的覆盖范围或易碎性风险。
- 当最安全的选择不明确时，说明驱动所选测试设置的假设。

## 参考

- `references/pinia-patterns.md`
- Pinia 测试食谱：<https://pinia.vuejs.org/cookbook/testing.html>
- Vue Test Utils 指南：<https://test-utils.vuejs.org/guide/>
