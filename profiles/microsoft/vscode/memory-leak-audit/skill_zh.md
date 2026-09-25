# 内存泄漏审计

VS Code 中排名第一的 Bug 类别。这项技能编码了防止和修复泄漏的模式。

## 使用场景

- 审查注册事件监听器或 DOM 处理器的代码
- 修复报告的内存泄漏（监听器计数随时间增长）
- 在被重复调用的方法中创建对象
- 处理模型生命周期事件（onWillDispose, onDidClose）
- 在构造函数或设置方法中添加事件订阅

## 审计清单

按顺序逐个检查。遗漏单个模式可能导致数千个泄漏对象。

### 第 1 步：DOM 事件监听器

**规则**：绝对不要直接使用 `.onload`、`.onclick` 或 `addEventListener()`。始终使用 `addDisposableListener()`。

```typescript
// BAD — 每次调用都会泄漏一个监听器
this.iconElement.onload = () => { ... };

// GOOD — 被跟踪且可释放
this._register(addDisposableListener(this.iconElement, 'load', () => { ... }));
```

**验证案例**：PR #280566 — 扩展图标组件在 37 次切换后泄漏了 185 个监听器。

### 第 2 步：一次性事件

**规则**：对于只应触发一次的事件（生命周期事件、关闭事件、首次变更事件），使用 `Event.once()`。

```typescript
// BAD — 监听器在首次触发后仍然注册
model.onDidDispose(() => store.dispose());

// GOOD — 首次调用后自动移除
Event.once(model.onDidDispose)(() => store.dispose());
```

**验证案例**：PRs #285657, #285661 — 终端生命周期技巧被替换为 `Event.once()`。

### 第 3 步：重复方法调用

**规则**：在多次被调用的方法中创建的对象绝不能注册到类 `this._register()`。使用 `MutableDisposable` 或向调用者返回 `IDisposable`。

```typescript
// BAD — 每次调用都会向类存储添加一个监听器
startSearch() {
    this._register(this.model.onResults(() => { ... }));
}

// GOOD — MutableDisposable 确保最多 1 个监听器
private readonly _searchListener = this._register(new MutableDisposable());

startSearch() {
    this._searchListener.value = this.model.onResults(() => { ... });
}
```

当事件应在每次方法调用中只触发一次时，将 `Event.once()` 与 `MutableDisposable` 结合使用——这会在首次调用后自动移除监听器，同时仍能防止重复调用：

```typescript
private readonly _searchListener = this._register(new MutableDisposable());

startSearch() {
    this._searchListener.value = Event.once(this.model.onResults)(() => { ... });
}
```

**验证案例**：PR #283466 — 终端查找组件每次搜索泄漏 1 个监听器。

### 第 4 步：与模型绑定的 DisposableStores

**规则**：在创建与模型生命周期绑定的 `DisposableStore` 时，将 `model.onWillDispose(() => store.dispose())` 注册到存储本身。

```typescript
const store = new DisposableStore();
store.add(model.onWillDispose(() => store.dispose()));
store.add(model.onDidChange(() => { ... }));
```

**验证案例**：该模式在 `chatEditingSession.ts`、`fileBasedRecommendations.ts`、`testingContentProvider.ts` 中使用。

### 第 5 步：资源池模式

**规则**：在使用创建池化对象（列表、树）的工厂方法时，可释放对象必须注册到单个对象，而不是池类。

```typescript
// BAD — 注册到池，每个对象从未被清理
createItem() {
    const item = new Item();
    this._register(item.onEvent(() => { ... }));
    return item;
}

// GOOD — 使用对象范围的可释放包装
createItem(): IDisposable & Item {
    const store = new DisposableStore();
    const item = new Item();
    store.add(item.onEvent(() => { ... }));
    return { ...item, dispose: () => store.dispose() };
}
```

**验证案例**：PR #290505 — 聊天内容部分的 CollapsibleListPool 和 TreePool 泄漏了可释放对象。

### 第 6 步：测试验证

**规则**：每个创建可释放对象的测试套件都必须调用 `ensureNoDisposablesAreLeakedInTestSuite()`。

```typescript
import { ensureNoDisposablesAreLeakedInTestSuite } from '../../../../base/test/common/utils.js';

suite('MyFeature', () => {
    ensureNoDisposablesAreLeakedInTestSuite();

    test('does something', () => {
        // 测试可释放对象自动被跟踪
    });
});
```

## 快速参考

| 场景 | 模式 | 反模式 |
|------|------|-------|
| DOM 事件 | `addDisposableListener()` | `.onclick =`, `addEventListener()` |
| 一次性事件 | `Event.once(event)(handler)` | `event(handler)` 用于生命周期 |
| 重复方法 | `MutableDisposable` 或返回 `IDisposable` | 在非构造函数中 `this._register()` |
| 模型生命周期 | `store.add(model.onWillDispose(...))` | 遗忘清理 |
| 池化对象 | 对象范围的 `DisposableStore` | 池范围 `this._register()` |
| 测试 | `ensureNoDisposablesAreLeakedInTestSuite()` | 无泄漏检查 |

## 验证

修复泄漏后，通过以下方式验证：
1. 在重复操作前后检查监听器计数
2. 在测试中运行 `ensureNoDisposablesAreLeakedInTestSuite()`
3. 确认对象计数稳定（使用量线性增长）
4. **针对聊天特定泄漏**：通过 `npm run perf:chat-leak` 运行聊天内存泄漏检查器（参见 `chat-perf` 技能）。它在一个会话中发送 N 条消息，在每次发送后强制执行 GC，并使用线性回归对堆/DOM 样本进行分析以检测每条消息的增长。斜率超过 2 MB/消息表示存在泄漏。使用 `--messages 20 --verbose` 获取更准确的结果。
