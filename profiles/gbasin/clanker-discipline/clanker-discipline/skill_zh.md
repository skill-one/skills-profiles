# Clanker Discipline

在编写或审查管理应用状态的类型、数据模型和函数时，请应用这些规则。代理往往会添加标志、可选字段和特殊情况，这些情况会累积成无人预期的状态——在它落地之前捕获这些问题。

当你发现违规行为时，请全面重构。目标是干净、可维护的代码，而不是最小的差异。删除标志，重塑类型，重构函数。现在更大的差异比以后分层的工作绕道更好。

---

## 1. 推导而非存储

你添加的每个布尔值都会使理论状态空间翻倍。当某个值可以从你已有的数据中推导出来时，不要存储它。最好的推导来源是事件流：发生了什么情况的记录。

### 之前：缓存的标志

一个代理被要求只在助手自然完成时显示页脚。它发明了四个标志：

```ts
type ThreadState = {
  wasInterrupted: boolean;
  didAssistantFinish: boolean;
  didAssistantError: boolean;
  wasToolCallOnly: boolean;
};

function shouldShowFooter(state: ThreadState): boolean {
  return state.didAssistantFinish
    && !state.wasInterrupted
    && !state.didAssistantError
    && !state.wasToolCallOnly;
}
```

四个字段来回答一个问题，其他地方有四个变异点来保持它们同步。

### 之后：从证据中推导

```ts
function shouldShowFooter(events: SessionEvent[]): boolean {
  const latest = getLatestAssistantMessage(events);
  if (!latest) return false;
  return latest.completed && !latest.error && latest.finish !== 'tool-calls';
}
```

答案现在是从已经存在的事件中计算出来的。

### 不应推导的情况

- 域确实有一个有序转换的状态机。结账步骤不是一个缓存的结论；它就是状态。
- 一个字段包含无法重新推导的时间或外部数据（异步进程的时间戳、下游需要的 API 响应）。
- 推导会比存储的值更复杂。

### 如果无法推导，则封装

如果必须存在可变状态，将其限制在尽可能小的范围内。闭包比类字段更好：

```ts
// 坏：状态对整个类可见
class Writer {
  private debounceTimeout: ReturnType<typeof setTimeout> | null = null;
  queueSend(text: string) { /* 可以触及 debounceTimeout */ }
  flushNow() { /* 可以触及 debounceTimeout */ }
  somethingElse() { /* 也可以触及 debounceTimeout */ }
}

// 好：状态被限制在闭包中
function createDebouncedAction(callback: () => void, delayMs = 300) {
  let timeout: ReturnType<typeof setTimeout> | null = null;
  return {
    trigger() {
      clearTimeout(timeout!);
      timeout = setTimeout(() => { timeout = null; callback(); }, delayMs);
    },
    clear() {
      if (timeout) { clearTimeout(timeout); timeout = null; }
    },
  };
}
```

闭包之外没有任何东西可以触及计时器。

### 调试的回报

当状态从证据中推导出来时，调试变成输入数据、输出答案：

```ts
test('footer is hidden for aborted runs', () => {
  const events = loadEvents('./fixtures/aborted-session.jsonl');
  expect(shouldShowFooter(events)).toBe(false);
});
```

无需模拟或时间重现。错误在于事件或纯函数中。

---

## 2. 使错误状态不可能

每个可选字段都是代码库其他部分每次触及该数据时必须回答的问题。

### 差异联合类型优于可选包

```ts
// 坏：当状态是 'idle' 时，gateway/transactionId 存在吗？类型没有说明。
type PaymentState = {
  status: 'idle' | 'processing' | 'settled';
  gateway?: 'stripe' | 'paypal';
  transactionId?: string;
  initiatedAt?: string;
  settledAt?: string;
};

// 好：每个状态都携带它需要的精确字段。
type PaymentState =
  | { status: 'idle' }
  | { status: 'processing'; gateway: 'stripe' | 'paypal'; transactionId: string; initiatedAt: string }
  | { status: 'settled'; gateway: 'stripe' | 'paypal'; transactionId: string; settledAt: string };
```

### null 优于哨兵值

```ts
// 坏：'none' 不是一个操作。它就是缺席。
type PendingAction = 'none' | 'confirm-address' | 'select-shipping';

// 好
type PendingAction = 'confirm-address' | 'select-shipping';
type OrderState = { pendingAction: PendingAction | null };
```

### 分阶段组合优于杂烩

```ts
// 坏：20+ 可选字段。每个消费者都做 profile.firstName ?? defaults.firstName。
type UserProfile = {
  firstName?: string;
  lastName?: string;
  email?: string;
  phone?: string;
  company?: string;
  jobTitle?: string;
  billingAddress?: string;
  cardLast4?: string;
  // ... 更多
};

// 好：检查一个可选字段而不是八个。当身份存在时，它所有的字段都存在。
type UserProfile = {
  identity?: { firstName: string; lastName: string; email: string };
  billing?: { address: string; cardLast4: string };
};
```

### 品牌相同的原始类型

```ts
// 坏：接受 UserId 的函数会高兴地接受 TeamId。
type UserId = string;
type TeamId = string;

// 好
type UserId = string & { readonly __brand: 'user' };
type TeamId = string & { readonly __brand: 'team' };
```

### 删除死的状态变体

如果一个类型有一个从未构造的变体，删除它。一个 `status: 'open' | 'completed'` 其中 `'completed'` 从未被设置表明不存在生命周期。

---

## 3. 强制函数契约

### 纯函数永远不要添加副作用

当纯函数悄悄获得副作用时，每个调用点都会继承它没有请求的行为。如果一个函数需要副作用，将它们提取到一个单独的协调器中。

- **语义函数** 是小的、纯的、自我描述的。所有输入进来，所有输出出去，没有隐藏的副作用。
- **实用函数** 是协调器。它们组合语义函数并包含混乱的领域胶水。

### 之前：语义函数演变成实用函数

```ts
function handleWebhook(state, eventType, payload, receivedAt): WebhookResult {
  switch (eventType) {
    case 'payment.captured': {
      const receipt = buildReceipt(payload);            // 数据创建
      state.order.paymentStatus = 'captured';           // 变异
      state.order.receipt = receipt;                     // 变异
      state.user.lastPurchaseAt = receivedAt;           // 变异
      state.user.lifetimeSpend += receipt.amount;        // 变异
      clearPendingAction(state);                         // 副作用
      const notifications = buildPaymentNotifs(state);   // 通知
      state.notifications.push(...notifications);        // 变异
      recalculateDashboard(state);                       // 推导
      return { state, output: receipt, notifications };
    }
    // ... 12 个更多的情况，相同模式
  }
}
```

### 之后：由语义函数组合

```ts
function handlePaymentCaptured(state: AppState, payload: PaymentPayload, receivedAt: string): WebhookResult {
  const receipt = buildReceipt(payload);
  const updatedOrder = applyPaymentToOrder(state.order, receipt);
  const updatedUser = applyPurchaseToUser(state.user, receipt, receivedAt);
  const notifications = buildPaymentNotifs(state, receipt);

  return {
    state: { ...state, order: updatedOrder, user: updatedUser },
    output: receipt,
    notifications,
  };
}
```

### 选择一个变异契约

如果一个函数变异它的输入，返回 `void`。如果它返回一个值，先克隆。永远不要变异输入并返回相同的引用——调用者无法判断是使用返回值还是原始值。

```ts
// 坏：变异并返回相同的对象
function withPendingAction(state: AppState, action: string): AppState {
  state.pendingAction = action;
  return state;
}

// 好：变异，返回 void
function applyPendingAction(state: AppState, action: string): void {
  state.pendingAction = action;
}

// 也好：克隆，返回新对象
function withPendingAction(state: AppState, action: string): AppState {
  return { ...state, pendingAction: action };
}
```

---

## 4. 数据优于过程

当一个长 if 链从每个分支返回相似形状时，逻辑是作为代码编码的查找表。将其转换为数据。

### 之前：if 链

```ts
function getStepInfo(step: string): StepInfo | null {
  if (step === 'verify-email') {
    return { tone: 'action', title: 'Verify your email', detail: 'Check your inbox' };
  }
  if (step === 'add-payment') {
    return { tone: 'action', title: 'Add payment method', detail: 'Enter card details' };
  }
  if (step === 'review-order') {
    return { tone: 'confirm', title: 'Review your order', detail: 'Check totals' };
  }
  // ... 10 个更多分支
  return null;
}
```

### 之后：声明性表

```ts
const STEP_INFO: Array<{
  match: (step: string) => boolean;
  info: StepInfo;
}> = [
  { match: (s) => s === 'verify-email', info: { tone: 'action', title: 'Verify your email', detail: 'Check your inbox' } },
  { match: (s) => s === 'add-payment',  info: { tone: 'action', title: 'Add payment method', detail: 'Enter card details' } },
  { match: (s) => s === 'review-order', info: { tone: 'confirm', title: 'Review your order', detail: 'Check totals' } },
  // 数据，不是代码
];

function getStepInfo(step: string): StepInfo | null {
  return STEP_INFO.find(({ match }) => match(step))?.info ?? null;
}
```

更容易扫描、扩展和测试。代理添加新步骤时添加数据条目，而不是控制流中的分支。

### 不应转换的情况

如果分支有不同的控制流——不仅仅是不同的返回值——保持它们为代码。表将输入映射到输出；它无法表达“调用 X 然后条件性地调用 Y。”

---

## 检查清单

在审查代码（你的或代理的）时：

- [ ] 任何新字段是否可以从现有状态推导出来？推导它。
- [ ] 可变状态是否在其最小范围内可见？将其封装在闭包中。
- [ ] 任何模型是否允许不可能的字段组合？差异联合类型。
- [ ] 是否有哨兵值（`'none'`、`'unknown'`、`-1'`）可以用 `null` 替代？使用 null。
- [ ] 是否有用于不同领域概念的相同类型别名？品牌或消除。
- [ ] 任何函数是否既变异其输入又返回它？选择一个契约。
- [ ] 语义函数是否长出副作用？提取它们。
- [ ] 是否有一个 if 链，每个分支返回相似形状？将其转换为表。
- [ ] 是否有从未构造的死类型变体？删除它们。
