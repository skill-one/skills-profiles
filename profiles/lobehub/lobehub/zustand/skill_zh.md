# LobeHub Zustand 状态管理

## 状态形状和类型

- 从 `@lobechat/types` 而不是 `@lobechat/database` 中导入共享的 store 类型。
- 将轻量级列表项类型与完整详情类型保持分离；列表类型不得扩展重型详情类型。
- 使用数组进行整个列表的展示，使用 ID 键映射进行缓存的详情，并在需要时为每个项目添加加载状态。
- 在选择列表/详情形状之前，请阅读 [数据结构](references/data-structures.md)。其工作示例仅在相关时才会加载。

## 动作类型层级

### 1. 公共动作

UI 组件的主要接口：

- 命名：动词形式（`createTopic`，`sendMessage`）
- 职责：参数验证，流程编排

### 2. 内部动作（`internal_*`）

核心业务逻辑实现：

- 命名：`internal_` 前缀（`internal_createTopic`）
- 职责：乐观更新，服务调用，错误处理
- 不得被 UI 直接调用

### 3. 分发方法（`internal_dispatch*`）

状态更新处理器：

- 命名：`internal_dispatch` + 实体（`internal_dispatchTopic`）
- 职责：调用 reducer，更新 store

## 何时使用 Reducer 与 Simple `set`

**使用 Reducer 模式：**

- 管理对象列表/映射（`messagesMap`，`topicMaps`）
- 乐观更新
- 复杂的状态转换

**使用 Simple `set`：**

- 切换布尔值
- 更新简单值
- 设置单个状态字段

## 乐观更新模式

```typescript
internal_createTopic: async (params) => {
  const tmpId = Date.now().toString();

  // 1. 立即更新前端（乐观）
  get().internal_dispatchTopic(
    { type: 'addTopic', value: { ...params, id: tmpId } },
    'internal_createTopic'
  );

  // 2. 调用后端服务
  const topicId = await topicService.createTopic(params);

  // 3. 刷新以保持一致性
  await get().refreshTopic();
  return topicId;
},
```

**删除操作**：不要使用乐观更新（破坏性，复杂恢复）

## 命名规范

**动作：**

- 公共：`createTopic`，`sendMessage`

- 内部：`internal_createTopic`，`internal_updateMessageContent`

- 分发：`internal_dispatchTopic`
  **状态：**

- ID 数组：`topicEditingIds`

- 映射：`topicMaps`，`messagesMap`

- 激活：`activeTopicId`

- 初始化标志：`topicsInit`

## 详细指南

- 动作模式：`references/action-patterns.md`
- Slice 组织：`references/slice-organization.md`

## 基于类的动作实现

我们将从普通的 `StateCreator` 对象迁移到 **基于类的动作**。

### 模式

- 定义一个类，封装动作并在构造函数中接收 `(set, get, api)`。
- 使用 `#private` 字段（例如，`#set`，`#get`）以避免泄露内部。
- 优先使用共享类型辅助工具：
  - 从 `@/store/types` 的 `StoreSetter<T>` 用于 `set`。
  - `Pick<ActionImpl, keyof ActionImpl>` 仅暴露公共方法。
- 导出一个 `create*Slice` 辅助工具，返回一个类实例。

```ts
type Setter = StoreSetter<HomeStore>;
export const createRecentSlice = (set: Setter, get: () => HomeStore, _api?: unknown) =>
  new RecentActionImpl(set, get, _api);

export class RecentActionImpl {
  readonly #get: () => HomeStore;
  readonly #set: Setter;

  constructor(set: Setter, get: () => HomeStore, _api?: unknown) {
    void _api;
    this.#set = set;
    this.#get = get;
  }

  useFetchRecentTopics = () => {
    // ...
  };
}

export type RecentAction = Pick<RecentActionImpl, keyof RecentActionImpl>;
```

### 组合

- 在 store 文件中，使用 `flattenActions` 合并类实例（不要展开类实例）。
- `flattenActions` 将方法绑定到原始类实例，并支持原型方法和类字段。

```ts
const createStore: StateCreator<HomeStore, [['zustand/devtools', never]]> = (...params) => ({
  ...initialState,
  ...flattenActions<HomeStoreAction>([
    createRecentSlice(...params),
    createHomeInputSlice(...params),
  ]),
});
```

### 多类 Slice

- 对于需要多个动作类的大型 Slice，使用 `flattenActions` 在 Slice 入口处组合它们。
- 如果您需要组合多个类并隐藏私有字段，请使用本地 `PublicActions<T>` 辅助工具。

```ts
type PublicActions<T> = { [K in keyof T]: T[K] };

export type ChatGroupAction = PublicActions<
  ChatGroupInternalAction & ChatGroupLifecycleAction & ChatGroupMemberAction & ChatGroupCurdAction
>;

export const chatGroupAction: StateCreator<
  ChatGroupStore,
  [['zustand/devtools', never]],
  [],
  ChatGroupAction
> = (...params) =>
  flattenActions<ChatGroupAction>([
    new ChatGroupInternalAction(...params),
    new ChatGroupLifecycleAction(...params),
    new ChatGroupMemberAction(...params),
    new ChatGroupCurdAction(...params),
  ]);
```

### Store-Access 类型

- 对于依赖于其他类中的动作的类方法，定义明确的状态增强：
  - `ChatGroupStoreWithSwitchTopic` 用于生命周期 `switchTopic`
  - `ChatGroupStoreWithRefresh` 用于成员刷新
  - `ChatGroupStoreWithInternal` 用于 curd `internal_dispatchChatGroup`

### 当前不需要 `set` 的 Slice

当 Slice 不写入本地状态（例如，它委托给另一个 store 或仅运行钩子）时，删除 `#set` 并将构造函数参数标记为 `_set` 并使用 `void _set` 以保持 `(set, get, api)` 形状：

```ts
export class ToolActionImpl {
  readonly #get: () => ConversationStore;

  constructor(_set: Setter, get: () => ConversationStore, _api?: unknown) {
    void _set;
    void _api;
    this.#get = get;
  }

  approveToolCall = async (id: string) => {
    const { context, hooks } = this.#get();
    await useChatStore.getState().approveToolCalling(id, '', context);
    hooks.onToolCallComplete?.(id, undefined);
  };
}
```

- 当未使用时删除 `#set`；当后续编辑需要 `set` 时恢复它——重新添加成本为零。
- 对于不写入状态的 Slice，不要添加 `setNamespace`。
- 在迁移期间不要同时保留旧的 Slice 对象和类动作。
