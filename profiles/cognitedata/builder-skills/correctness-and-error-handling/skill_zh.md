# 正确性与错误处理修复

查找并修复 **$ARGUMENTS**（如果未提供参数，则修复整个应用程序）中的正确性问题以及缺失的错误处理。按照以下步骤逐一操作。每个步骤都会查找问题并**就地修复**。仅报告无法自动修复的问题。

---

## 第 1 步 — 映射数据流并修复已知缺陷

在检查任何内容之前，请阅读以下文件：

- `src/main.tsx` / `src/App.tsx` — 顶层错误边界和认证流程
- 所有匹配 `**/hooks/*.ts`，`**/contexts/*.tsx` 的文件 — 共享异步状态
- 所有匹配 `**/api/*.ts`，`**/services/*.ts` 的文件 — CDF SDK 调用位置

对于每个异步数据源，请注意：

- 请求失败时会发生什么（网络错误、CDF 403、超时）？
- 加载时 UI 显示什么？
- 结果为空时 UI 显示什么？

### 在关键路径中查找并修复已知缺陷

```bash
# 在关键代码路径中查找 TODO/FIXME/HACK（不包括测试文件）
grep -rn --include="*.ts" --include="*.tsx" -E "(TODO|FIXME|HACK|XXX):" src/ | grep -v ".test." | grep -v ".spec."

# 查找 "修复" 或 "损坏" 或 "解决方案" 标记
grep -rn --include="*.ts" --include="*.tsx" -i -E "(TODO.*修复|解决方案|损坏|已知.?错误|临时.?解决方案)" src/
```

对于关键路径中的每个匹配项（数据获取、渲染、认证、导航）：

1. **阅读周围的代码**以了解不完整/损坏的行为。
2. **修复根本问题** — 实现缺失的逻辑、修复损坏的行为或添加适当的错误处理。
3. 如果修复需要超出此技能范围的重大架构更改，**将 TODO 替换为安全的失败模式**：优雅的错误处理、合理的回退值或向用户解释功能降级的明确消息。
4. **修复后删除 TODO/FIXME/HACK 评论**。代码应自说自明。

不要在关键路径中留下 TODO。每个问题都必须解决或转换为安全的回退。

---

## 第 2 步 — 添加顶层错误边界

每个 Flows 应用程序都必须至少有一个 React 错误边界包装主内容，以便意外渲染时异常显示用户友好的消息，而不是空白屏幕。

```bash
grep -rn --include="*.tsx" --include="*.ts" -E "ErrorBoundary|componentDidCatch|getDerivedStateFromError" src/
```

如果不存在错误边界，**创建 ErrorFallback 组件并将 ErrorBoundary 包装器添加到 `App.tsx`**。如果尚未安装，请安装 `react-error-boundary`：

```bash
pnpm add react-error-boundary
```

然后在 `App.tsx` 中添加：

```tsx
import { ErrorBoundary } from "react-error-boundary";

function ErrorFallback({ error }: { error: Error }) {
  return (
    <div role="alert" className="p-8 text-center">
      <p className="text-lg font-semibold">发生了一些问题</p>
      <pre className="mt-2 text-sm text-muted-foreground">{error.message}</pre>
    </div>
  );
}

// 包装主内容：
<ErrorBoundary FallbackComponent={ErrorFallback}>
  <MainContent />
</ErrorBoundary>
```

使用 ErrorBoundary 更新 `App.tsx`。不要只是建议它 — 进行编辑。

---

## 第 3 步 — 将未处理的异步函数包装在 try/catch 中

搜索每个没有错误处理的 `async` 函数和 `Promise` 链：

```bash
# 查找 async 函数
grep -rn --include="*.ts" --include="*.tsx" -E "async\s+function|async\s+\(" src/

# 查找 .then() 而没有 .catch()
grep -rn --include="*.ts" --include="*.tsx" -E "\.then\(" src/ | grep -v "\.catch\("
```

**修复每个问题**：

- 对于缺少 try/catch 的裸 `async` 函数：**将函数体包装在 try/catch 中**。记录上下文错误并重新抛出，以便调用者/查询层可以处理它：

```ts
async function fetchAssets(sdk: CogniteClient) {
  try {
    const result = await sdk.assets.list({ limit: 100 });
    return result.items;
  } catch (error) {
    console.error("获取资产失败：", error);
    throw error;
  }
}
```

- 对于没有 `.catch()` 的 `.then()`：**添加 `.catch()`** 到链中：

```ts
somePromise.then(handleResult).catch((error) => {
  console.error("操作失败：", error);
});
```

- 对于缺少 `isError` 处理的 TanStack Query 消费者（`useQuery`/`useMutation`）：**在组件中添加错误检查和错误 UI**：

```tsx
const { data, isLoading, isError, error } = useQuery({
  queryKey: ["assets"],
  queryFn: () => fetchAssets(sdk),
});

if (isError) return <ErrorMessage error={error} />;
```

阅读每个文件，进行编辑，并将文件写回。

---

## 第 4 步 — 为组件添加缺失的加载、错误和空状态

对于每个获取数据的组件，它必须具有三个不同的 UI 状态：

| 状态 | 必需的 UI |
|------|----------|
| 加载中 | 旋转器、骨架或加载指示器 |
| 错误 | 用户可读消息（不是原始错误对象或空白空间） |
| 空的 | "无结果" / "目前还没有内容" 消息（不是空白列表） |

搜索在渲染数据时不检查加载状态的组件：

```bash
grep -rn --include="*.tsx" -E "\.(map|filter|find)\(" src/ | grep -v "isLoading\|isPending\|skeleton\|Skeleton"
```

对于每个匹配项，阅读组件并**直接添加缺失的状态**：

- **缺失的加载状态** — 在数据渲染之前添加：
```tsx
if (isLoading) {
  return <div className="flex items-center justify-center p-8"><Spinner /></div>;
}
```

- **缺失的错误状态** — 在加载检查之后添加：
```tsx
if (isError) {
  return (
    <div role="alert" className="p-4 text-center text-destructive">
      <p>加载数据失败。请重试。</p>
    </div>
  );
}
```

- **缺失的空状态** — 在错误检查之后、`.map()` 之前添加：
```tsx
if (!data || data.length === 0) {
  return (
    <div className="p-8 text-center text-muted-foreground">
      <p>未找到结果。</p>
    </div>
  );
}
```

以正确的顺序（加载、然后错误、然后空）插入这些检查，并在现有数据渲染之前。写回每个修复的文件。

---

## 第 5 步 — 为外部数据添加类型缩小

外部数据（CDF 响应、URL 参数、`localStorage`、`JSON.parse`）在使用前必须进行验证。TypeScript 类型本身不是运行时保证。

```bash
# 查找没有验证的 JSON.parse
grep -rn --include="*.ts" --include="*.tsx" -E "JSON\.parse\(" src/

# 查找 localStorage 读取
grep -rn --include="*.ts" --include="*.tsx" -E "localStorage\.(get|set)Item" src/

# 查找 useSearchParams 使用
grep -rn --include="*.ts" --include="*.tsx" -E "useSearchParams|searchParams\.get" src/
```

**修复每个问题**：

- **`JSON.parse(x) as T`** — 替换为 Zod safeParse：
```ts
import { z } from "zod";

const MySchema = z.object({ /* 字段 */ });
const parseResult = MySchema.safeParse(JSON.parse(raw));
if (!parseResult.success) {
  console.warn("存储的数据无效，使用默认值：", parseResult.error);
  return defaultValue;
}
const validated = parseResult.data;
```

- **`searchParams.get("id")`** 没有null检查 — 添加空值回退：
```ts
const id = searchParams.get("id") ?? defaultId;
```

- **`localStorage.getItem(key)`** 直接使用 — 添加类型守卫和回退：
```ts
const raw = localStorage.getItem(key);
if (raw === null) return defaultValue;
try {
  const parsed = JSON.parse(raw);
  // 验证 parsed 形状
  return isValidShape(parsed) ? parsed : defaultValue;
} catch {
  return defaultValue;
}
```

不要用 `as MyType` 将外部数据强制转换为类型 — 那会绕过运行时安全。阅读、修复并写回每个文件。

---

## 第 6 步 — 修复 null、undefined 和不安全的数组访问

阅读每个访问 CDF 返回的数据或通过 props 传递的数据的组件。

```bash
grep -rn --include="*.tsx" --include="*.ts" -E "\w+\[0\]\." src/
```

**修复找到的不安全模式**：

- **不安全的嵌套属性访问** — 添加可选链和空值合并：
```tsx
// 之前：asset.properties.space.Asset.name
// 之后：
const name = asset.properties?.["my-space"]?.["Asset"]?.name ?? "未知";
```

- **未保护的 `.map()` 在可能未定义的数组上** — 添加空值回退：
```tsx
// 之前：items.map(renderItem)
// 之后：
(items ?? []).map(renderItem)
```

- **不安全的数组索引访问** — 使用 `.at()` 并带可选链：
```tsx
// 之前：items[0].name
// 之后：
const first = items.at(0)?.name ?? "—";
```

阅读每个匹配的文件，应用修复，并将文件写回。

---

## 第 7 步 — 为 useEffect 添加清理函数

每个 `useEffect`，如果设置了可以存活于组件之外的订阅、计时器、事件监听器或异步操作，都必须返回一个清理函数。

```bash
grep -rn --include="*.tsx" --include="*.ts" -B 2 -A 15 "useEffect" src/
```

对于每个 `useEffect`，检查是否需要清理，如果缺失则**添加清理函数**：

| 模式 | 添加的修复 |
|------|----------|
| `addEventListener` | 添加 `return () => removeEventListener(...)` |
| `setInterval` / `setTimeout` | 添加 `return () => clearInterval(id)` / `clearTimeout(id)` |
| CDF 流式传输 / SSE | 添加 `return () => stream.close()` |
| `fetch` / CDF SDK 调用 | 添加 AbortController：`const controller = new AbortController()` 在顶部，将 `controller.signal` 传递给 fetch，添加 `return () => controller.abort()`，并使用 `if (!controller.signal.aborted)` 守护状态更新 |
| Zustand / 事件发射器订阅 | 添加 `return () => unsubscribe()` |

异步效果的参考模式：

```ts
useEffect(() => {
  const controller = new AbortController();

  async function load() {
    try {
      const data = await fetchWithSignal(controller.signal);
      if (!controller.signal.aborted) setState(data);
    } catch (err) {
      if (err instanceof Error && err.name !== "AbortError") {
        setError(err);
      }
    }
  }

  load();
  return () => controller.abort();
}, [id]);
```

阅读每个效果，添加缺失的清理，并写回文件。

---

## 第 8 步 — 添加边缘情况守卫

对于每个功能，检查并**添加守卫**：

- **空数据**：如果未处理零项列表，在渲染之前添加空状态检查。
- **单个项**：如果列表渲染在单个条目时有 off-by-one 错误，修复逻辑。
- **最大数据 / 分页**：如果 CDF 返回完整的 `limit` 且有更多页面，确保向用户传达分页。如果缺失，添加“加载更多”或分页指示器。
- **并发请求 / 过期结果**：如果用户可以在前一个请求完成之前触发新请求，添加过期请求取消（AbortController 或请求 ID 检查）。
- **网络离线**：如果应用程序在离线时无声失败，添加有意义的错误消息。

对于 Atlas 工具 `execute` 函数，**在每个 execute 函数的顶部添加参数验证**：

```ts
execute: async (args) => {
  if (!args.assetId || typeof args.assetId !== "string") {
    return { output: "缺少或无效的 assetId", details: null };
  }
  // ... 可以安全进行
}
```

搜索 `execute` 函数，阅读每个函数，添加验证，并写回文件。

---

## 第 9 步 — 报告剩余发现

生成一个结构化报告，涵盖：

1. **每一步修复了什么** — 总结所做的更改（编辑的文件、修复的模式）。
2. **剩余问题** — 仅列出无法自动修复的问题（例如，需要架构更改、需要产品决策或超出此技能范围）。

| 严重性 | 文件 | 行 | 问题 | 状态 |
|------|------|----|------|------|
| 高 | `src/hooks/useAssets.ts` | 34 | 未处理的 promise 拒绝 | 已修复 — 包装在 try/catch 中 |
| 中 | `src/components/AssetList.tsx` | 12 | 无空状态 | 已修复 — 添加空状态检查 |
| 中 | `src/auth/flow.ts` | 45 | 认证错误处理需要产品决策 | 未修复 — 需要团队输入 |

如果某一步未发现问题，请为该步骤声明“未发现问题”。不要无声地跳过步骤。

---

## 完成

总结按严重性修复的内容。标记任何可能导致数据丢失、生产中崩溃或误导性 UI 状态的剩余高优先级问题，并将它们列在前面以立即关注。
