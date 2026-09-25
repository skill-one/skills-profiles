# @json-render/core

核心包，用于模式定义、目录创建和规范流式传输。

## 关键概念

- **模式（Schema）**：定义规范和目录的结构（使用 `defineSchema`）
- **目录（Catalog）**：将组件/操作名称映射到其定义（使用 `defineCatalog`）
- **规范（Spec）**：AI 生成的符合模式的 JSON 输出
- **规范流（SpecStream）**：用于渐进式规范构建的 JSONL 流式传输格式

## 实验性决策模型组合

对于决策模型组合，从 `@json-render/core` 导入 `experimental_composeSpec` 和 `experimental_createEvaluator`。这些 API 尚未发布；使用源构建，直到发布，然后固定确切版本。实验性导出和 `Experimental_` 类型可能在任何版本中更改。

- 使用 `{ model: "typesafe-ai/jev", apiKey: process.env.AI_GATEWAY_API_KEY! }` 在服务器端运行网关评估器。需要一个纯模型标识符；Jev 是当前示例；不要导入提供者构造函数。
- 调用 `experimental_composeSpec({ catalog, candidates, prompt, evaluate, initialState, signal })`。它是一个异步生成器；将 `step.spec` 快照流到您现有的渲染器，并检查 `complete.stopReason` (`finish`, `limit`, `unavailable`)。错误和取消会抛出异常；保留最后一个快照作为部分 UI。
- 新树默认为 `strategy: "batch"`：一次评估选择根/成员资格，然后在需要时安排选定的元素。第一个快照包含根下默认/第一个槽位中的目录顺序内容。资源变体共享一个排他性问题；重复计数包括根。根选择优先于该配方/资源的冲突推测成员资格。相同同级位置保留目录顺序。组合布局在发布前进行验证；循环或过深的深度会抛出异常。`maxElements` 限制批量创建（默认 32）。限制截断的选择或缺少必要的布局调用返回 `limit`。使用 `strategy: "sequential"` 用于遗留的 `next`/`parent` 适配器或顺序创建。编辑保持顺序。
- 批量跟踪步骤使用 `choice: "select" | "layout"` 和一个 `answers` 记录。将每个跟踪计为一次评估，包括其 token 和延迟。自定义评估器必须回答每个提供的问题；名称/选择是晦涩的，包括 `root`/`select_*`，然后是 `parent_*`/`order_*` 用于批量处理。
- 对于后续编辑，将选定的版本作为 `initialSpec` 传递。它会被克隆并验证；评估器可以添加、替换、删除非根子树，或移动/重新排序它们。未更改的 ID、绑定和状态将被保留。可选的 `elementDescriptions` 共享识别描述，而不暴露原始属性/状态。`initialState` 覆盖种子状态。种子必须在目录、表达式子集和深度限制内是有效的树。匹配的配方消耗使用/资源限制；删除/替换会释放它们。替换/移动使用两次评估（选择目标，然后配方/目的地），每次都计入预算。将操作和位置键视为晦涩的。
- 提供原子候选者，使用 `{ id, description, element: { type, props, on?, visible? }, root?, maxUses?, resource? }`。目录本身是不够的：应用程序必须提供值和绑定配方。Jev 选择元素和父槽位，从不自由形式的文本或代码。它从不执行操作。
- 候选者是配置好的组件实例，而不是页面模板。从当前应用程序记录/操作构建它们，或将属性绑定到 `initialState`；为图表类型、字段配置和布局变体提供明确的替代方案。模型在这些选项内选择分组和顺序。在提示中命名必需的部分；结构有效性并不表示语义完整性。
- V1 支持扁平规范目录、命名槽位、字面量、`$state`、`$bindState` 和状态可见性。没有预构建的子项、重复/监视、计算/模板/条件属性或自定义指令。成功/错误回调必须引用允许的操作。事件必须在组件目录中声明。
- 属性和操作参数在初始状态下进行验证，而不会应用模式转换/默认值。提供有效的初始值，并在运行时验证/授权操作调用。没有参数模式的内置项仅进行名称验证。
- `root` 默认为 true，`maxUses` 默认为一个，共享的 `resource` 值使替代方案相互排斥。默认值：32 次评估（包括终端调用；批量没有额外的 finish 调用），深度为八，每次调用 10 秒的网关超时。提供一个整体中止信号。
- 候选者描述、提示、说明、拓扑和显式的 `context` 被发送到评估器。初始状态和原始属性/绑定值不会自动发送。
- 对于自定义提供者，实现 `Experimental_CompositionEvaluator`：接受 `{ state, questions, signal }`，返回 `{ answers: { [question]: { choice, confidence? } }, usage?: { inputTokens? } }`。只返回提供的标准键。

有关应用程序集成和源构建说明，请参阅 `packages/core/README.md` 和 `/docs/jev`。Web 演示场是一个示例消费者，不是 API 的依赖项。

## 定义模式

```typescript
import { defineSchema } from "@json-render/core";

export const schema = defineSchema((s) => ({
  spec: s.object({
    // 定义规范结构
  }),
  catalog: s.object({
    components: s.map({
      props: s.zod(),
      description: s.string(),
    }),
  }),
}), {
  promptTemplate: myPromptTemplate, // 可选的自定义 AI 提示
});
```

## 创建目录

```typescript
import { defineCatalog } from "@json-render/core";
import { schema } from "./schema";
import { z } from "zod";

export const catalog = defineCatalog(schema, {
  components: {
    Button: {
      props: z.object({
        label: z.string(),
        variant: z.enum(["primary", "secondary"]).nullable(),
      }),
      description: "可点击的按钮组件",
    },
  },
});
```

## 生成 AI 提示

```typescript
const systemPrompt = catalog.prompt(); // 使用模式的 promptTemplate
const systemPrompt = catalog.prompt({ customRules: ["Rule 1", "Rule 2"] });
```

## SpecStream 工具

用于流式传输 AI 响应（JSONL 补丁）：

```typescript
import { createSpecStreamCompiler } from "@json-render/core";

const compiler = createSpecStreamCompiler<MySpec>();

// 处理流式传输块
const { result, newPatches } = compiler.push(chunk);

// 获取最终结果
const finalSpec = compiler.getResult();
```

## 动态属性表达式

任何属性值都可以是渲染时解析的动态表达式：

- **`{ "$state": "/state/key" }`** - 从状态模型读取值（单向读取）
- **`{ "$bindState": "/path" }`** - 双向绑定：从状态读取并启用写回。用于表单组件的自然值属性（值、选中、按下等）。
- **`{ "$bindItem": "field" }`** - 双向绑定到重复项字段。用于重复作用域内部。
- **`{ "$cond": <condition>, "$then": <value>, "$else": <value> }`** - 评估可见性条件并选择分支
- **`{ "$template": "Hello, ${/user/name}!" }`** - 使用状态值插值 `${/path}` 引用
- **`{ "$computed": "fnName", "args": { "key": <expression> } }`** - 调用注册的函数并传递解析的参数

`$cond` 使用与可见性条件（`$state`、`eq`、`neq`、`not`、数组用于 AND）相同的语法。`$then` 和 `$else` 可以是表达式（递归）。

组件不使用 `statePath` 属性进行双向绑定。相反，在自然值属性（例如 `value`、`checked`、`pressed`）上使用 `{ "$bindState": "/path" }`。

```json
{
  "color": {
    "$cond": { "$state": "/activeTab", "eq": "home" },
    "$then": "#007AFF",
    "$else": "#8E8E93"
  },
  "label": { "$template": "Welcome, ${/user/name}!" },
  "fullName": {
    "$computed": "fullName",
    "args": {
      "first": { "$state": "/form/firstName" },
      "last": { "$state": "/form/lastName" }
    }
  }
}
```

```typescript
import { resolvePropValue, resolveElementProps } from "@json-render/core";

const resolved = resolveElementProps(element.props, { stateModel: myState });
```

## 状态监视器

元素可以声明一个 `watch` 字段（顶层、类型/属性/子项的同级）来在状态值更改时触发操作：

```json
{
  "type": "Select",
  "props": { "value": { "$bindState": "/form/country" }, "options": ["US", "Canada"] },
  "watch": {
    "/form/country": { "action": "loadCities", "params": { "country": { "$state": "/form/country" } } }
  },
  "children": []
}
```

监视器仅在值更改时触发，而不是在初始渲染时。

## 验证

内置验证函数：`required`、`email`、`url`、`numeric`、`minLength`、`maxLength`、`min`、`max`、`pattern`、`matches`、`equalTo`、`lessThan`、`greaterThan`、`requiredIf`。

跨字段验证使用 args 中的 `$state` 表达式：

```typescript
import { check } from "@json-render/core";

check.required("字段是必需的");
check.matches("/form/password", "密码必须匹配");
check.lessThan("/form/endDate", "必须在截止日期之前");
check.greaterThan("/form/startDate", "必须在开始日期之后");
check.requiredIf("/form/enableNotifications", "启用时是必需的");
```

## 用户提示构建器

构建结构化用户提示，可选的规范细化和状态上下文：

```typescript
import { buildUserPrompt } from "@json-render/core";

// 初始生成
buildUserPrompt({ prompt: "创建一个待办事项应用程序" });

// 使用编辑模式细化（默认：仅修补）
buildUserPrompt({ prompt: "添加一个切换", currentSpec: spec, editModes: ["patch", "merge"] });

// 使用运行时状态
buildUserPrompt({ prompt: "显示数据", state: { todos: [] } });
```

可用的编辑模式：`"patch"`（RFC 6902 JSON Patch）、`"merge"`（RFC 7396 合并 Patch）、`"diff"`（统一 diff）。

## 规范验证

验证规范结构和自动修复常见问题：

```typescript
import { validateSpec, autoFixSpec } from "@json-render/core";

const { valid, issues } = validateSpec(spec);
// issues 包括：missing_child、invalid_visible（格式错误的条件）、
// repeat_without_children、repeat_item_outside_scope、repeat_state_mismatch

const { spec: fixed, fixDetails } = autoFixSpec(spec);
// fixDetails 条目是 { message, lossy }。有损修复会重新定位
// 位置不当的字段；有损修复会剪除悬空的子项引用。
// 在修复循环中，在重试用尽之前保留有损修复：
const attempt = autoFixSpec(spec, { lossy: retriesExhausted });
```

## 可见性条件

使用基于状态的条件控制元素可见性。`VisibilityContext` 是 `{ stateModel: StateModel }`。

```typescript
import { visibility } from "@json-render/core";

// 语法
{ "$state": "/path" }                    // 真值
{ "$state": "/path", "not": true }      // 假值
{ "$state": "/path", "eq": value }      // 等于
[ cond1, cond2 ]                         // 隐式 AND

// 辅助函数
visibility.when("/path")                 // { $state: "/path" }
visibility.unless("/path")               // { $state: "/path", not: true }
visibility.eq("/path", val)              // { $state: "/path", eq: val }
visibility.and(cond1, cond2)             // { $and: [cond1, cond2] }
visibility.or(cond1, cond2)              // { $or: [cond1, cond2] }
visibility.always                        // true
visibility.never                         // false
```

## 模式中的内置操作

模式可以声明 `builtInActions` —— 始终在运行时可用并自动注入到提示中的操作：

```typescript
const schema = defineSchema(builder, {
  builtInActions: [
    { name: "setState", description: "更新状态模型中的值" },
  ],
});
```

这些作为 `[内置]` 出现在提示中，并且不需要在 `defineRegistry` 中处理。

## StateStore

`StateStore` 接口允许外部状态管理库（Redux、Zustand、XState 等）连接到 json-render 渲染器。`createStateStore` 工厂创建了一个简单的内存实现：

```typescript
import { createStateStore, type StateStore } from "@json-render/core";

const store = createStateStore({ count: 0 });

store.get("/count");         // 0
store.set("/count", 1);      // 更新并通知订阅者
store.update({ "/a": 1, "/b": 2 }); // 批量更新

store.subscribe(() => {
  console.log(store.getSnapshot()); // { count: 1 }
});
```

`StateStore` 接口：`get(path)`、`set(path, value)`、`update(updates)`、`getSnapshot()`、`subscribe(listener)`。

## 关键导出

| 导出 | 目的 |
|------|------|
| `defineSchema` | 创建新模式 |
| `defineCatalog` | 从模式创建目录 |
| `createStateStore` | 创建框架无关的内存 `StateStore` |
| `resolvePropValue` | 将单个属性表达式与数据解析 |
| `resolveElementProps` | 解析元素中的所有属性表达式 |
| `buildUserPrompt` | 使用细化和状态上下文构建用户提示 |
| `buildEditUserPrompt` | 构建用于编辑现有规范的用户提示 |
| `buildEditInstructions` | 生成可用编辑模式的提示部分 |
| `isNonEmptySpec` | 检查规范是否有根和至少一个元素 |
| `deepMergeSpec` | RFC 7396 深度合并（null 删除，数组替换，对象递归） |
| `diffToPatches` | 从对象差异生成 RFC 6902 JSON Patch 操作 |
| `EditMode` | 类型：`"patch" \| "merge" \| "diff"` |
| `validateSpec` | 验证规范结构 |
| `autoFixSpec` | 自动修复常见规范问题；将修复分类为有损/无损，`{ lossy: false }` 会保留剪除 |
| `createSpecStreamCompiler` | 将 JSONL 补丁流到规范 |
| `createJsonRenderTransform` | TransformStream 将混合流中的文本与 JSONL 分开 |
| `parseSpecStreamLine` | 解析单个 JSONL 行 |
| `applySpecStreamPatch` | 将补丁应用于对象 |
| `StateStore` | 用于连接外部状态管理的接口 |
| `ComputedFunction` | `$computed` 表达式的函数签名 |
| `check` | TypeScript 辅助函数用于创建验证检查 |
| `BuiltInAction` | 内置操作定义类型（`name` + `description`） |
| `ActionBinding` | 操作绑定类型（包括 `preventDefault` 字段） |
