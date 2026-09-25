# 性能修复

系统性地查找并修复 **$ARGUMENTS** (如果没有提供参数，则修复整个应用程序) 中的性能问题。始终先测量——切勿盲目优化。

---

## 第 1 步——在触摸任何内容之前测量基线

在做出任何更改之前，运行生产构建并捕获指标：

```bash
pnpm run build
pnpm run preview
```

在 Chrome 中打开应用程序并捕获：
- **Lighthouse 分数** (性能选项卡 → 运行审核)
- **React Profiler** (React DevTools → Profiler → 录制交互)
  - 记录渲染时间最长的组件和渲染次数最高的组件

记录基线数字。每个修复都必须与这些数字进行比较。

---

## 第 2 步——查找和修复不必要的重新渲染

从 `src/App.tsx` 开始阅读组件树，并搜索以下模式：

```bash
grep -rn --include="*.tsx" \
  -E "value=\{\{|onClick=\{\(\)" src/
```

对于每个找到的实例，**直接应用修复**：

**JSX 中的内联对象/数组创建 → 用 `useMemo` 包装：**
```tsx
// BAD — 每次渲染都创建新对象，导致子组件重新渲染
<Chart options={{ color: "red" }} />

// FIX — 用 useMemo 包装
const chartOptions = useMemo(() => ({ color: "red" }), []);
<Chart options={chartOptions} />
```

**事件处理程序在每次渲染时重新创建 → 用 `useCallback` 包装：**
```tsx
// BAD
<Button onClick={() => doSomething(id)} />

// FIX — 用 useCallback 包装
const handleClick = useCallback(() => doSomething(id), [id]);
<Button onClick={handleClick} />
```

**每次渲染都变化的上下文 → 调用上下文值：**
```tsx
// BAD — 每次渲染都有新的对象引用
<MyContext.Provider value={{ user, sdk }}>

// FIX — 调用上下文值
const ctxValue = useMemo(() => ({ user, sdk }), [user, sdk]);
<MyContext.Provider value={ctxValue}>
```

对接收稳定 props 的纯展示组件应用 `React.memo`。不要包装每个组件——仅通过 Profiler 确认不需要重新渲染的组件。

---

## 第 3 步——查找和修复 DMS 查询模式

对于**读密集型**工作负载，优先选择命中**搜索/Elasticsearch 路径**的 API (`query` 或 `search` 在实例上)，而不是会**压垮 Postgres** 的 `list` 路径。

```bash
# 查找所有 DMS 实例 API 调用
grep -rn --include="*.ts" --include="*.tsx" -E "instances\.(list|search|query|aggregate|retrieve)" src/

# 查找直接调用其他 CDF 资源的 SDK 调用
grep -rn --include="*.ts" --include="*.tsx" -E "\.(assets|timeseries|events|files|sequences|relationships)\.(list|search|retrieve)" src/
```

对于读密集型路径中的每个 `instances.list` 调用（例如，填充表格、下拉菜单或搜索结果），**将其重写为使用 `instances.query`** 并使用等效的过滤器。保留现有的过滤器逻辑，但用查询 API 格式表达它：

```ts
// BAD — instances.list 命中 Postgres，对读密集型 UI 昂贵
const result = await client.instances.list({
  instanceType: "node",
  filter: { equals: { property: ["node", "space"], value: "my-space" } },
  limit: 100,
});

// FIX — 重写为 instances.query，它命中 Elasticsearch
const result = await client.instances.query({
  with: {
    nodes: {
      nodes: {
        filter: { equals: { property: ["node", "space"], value: "my-space" } },
      },
      limit: 100,
    },
  },
  select: {
    nodes: {},
  },
});
```

| API 使用 | 正确使用时 | 重写时 |
|----------|-----------|--------|
| `instances.query` | 使用过滤器映射到 Elasticsearch（文本、equals、范围）进行读取 | — |
| `instances.search` | 全文或模糊搜索 | — |
| `instances.list` | 写入、同步或需要查询/搜索不提供的语义 | 重写为 `instances.query` 如果用于读密集型 UI 显示 |
| `instances.retrieve` | 通过已知外部 ID 获取 | — |
| `instances.aggregate` | 计数、直方图 | — |

如果工作区中有 `semantic-knowledge/` 目录，可以参考其中关于搜索与关系路径、基数和物化权衡的更深层推理。

### 硬性门槛——LLM 覆盖查询结果

```bash
grep -rn --include="*.ts" --include="*.tsx" -E "chat\.completions|agents/chat|useAtlasChat|openai|anthropic" src/
```

不要将完成映射到 DMS 行。修复：一个 `sendAgentMessage` 或代理资源 (`integrate-fusion-agent`)。如果保留每项的完成：**5** / 上限 **50**，按 `space:externalId:lastUpdatedTime` 缓存，仅用户发起。

---

## 第 4 步——查找和修复客户端过滤（移动到服务器端）

过滤器、限制和投影必须**在 API 请求中应用**——不要下载大型结果集并在浏览器中过滤。

```bash
# 查找数据获取后的客户端过滤（常见反模式）
grep -rn --include="*.ts" --include="*.tsx" -B 5 "\.filter(" src/ | grep -B 5 "data\|items\|result\|response\|nodes"

# 查找全数据集上的 .map() 或 .reduce()，暗示客户端处理
grep -rn --include="*.ts" --include="*.tsx" -E "\.(map|reduce|find|some|every)\(" src/hooks/ src/services/ src/api/
```

对于每个客户端过滤模式，**将过滤逻辑移入 SDK 调用的 `filter` 参数，并删除 `.filter()` 调用**：

```ts
// BAD — 获取所有节点然后在客户端过滤
const result = await client.instances.query({ ... });
const activeNodes = result.items.nodes.filter(n => n.properties.status === "active");

// FIX — 将过滤逻辑移入 API 请求，删除客户端的 .filter()
const result = await client.instances.query({
  with: {
    nodes: {
      nodes: {
        filter: {
          and: [
            existingFilters,
            { equals: { property: ["mySpace", "myView/v1", "status"], value: "active" } },
          ],
        },
      },
      limit: 100,
    },
  },
  select: {
    nodes: {},
  },
});
const activeNodes = result.items.nodes; // 无需客户端过滤
```

| 问题 | 修复 |
|------|------|
| SDK 调用在完整结果集上使用 .filter() | 将过滤移入 API 请求的 `filter` 参数并删除 .filter() |
| DMS 查询中没有 `properties` 选择 | 添加 `sources` 或 `properties` 参数仅获取所需字段 |
| 获取所有项然后渲染子集 | 添加 `limit` 和 `filter` 到 API 调用以仅获取显示的内容 |
| 客户端在获取数组上执行文本搜索 | 用 SDK 的 `search` 端点替换 |

**硬性规则：**如果 API 支持客户端应用的过滤标准，**现在将其移到服务器端**。客户端过滤仅适用于简单的本地状态（例如，过滤 10 个用户偏好的缓存列表）。如果 API 不支持确切的过滤，请添加代码注释解释为什么需要客户端过滤。

---

## 第 5 步——查找和修复 CDF 数据获取和分页

读取所有 CDF SDK 调用（搜索 `sdk.`, `client.`, `useQuery`, `useCogniteClient`）。

```bash
# 查找分页模式
grep -rn --include="*.ts" --include="*.tsx" -E "(nextCursor|cursor|hasNextPage|fetchNextPage|offset|skip|page)" src/

# 查找 "获取所有" 循环
grep -rn --include="*.ts" --include="*.tsx" -B 3 -A 3 "while.*cursor\|while.*hasMore\|while.*nextPage" src/
```

对于每个调用，找到问题并**应用修复**：

| 问题 | 应用修复 |
|------|----------|
| 未设置 `limit` | **添加 `limit: 100`**（或实际需要的页面大小）到 SDK 调用 |
| 获取所有属性 | **添加 `properties` 过滤**以选择仅需要的字段 |
| 每次渲染都获取 | **将移入 `useQuery`/`useMemo`**，依赖数组稳定 |
| 可以并行处理的顺序请求 | **重写为 `Promise.all`** 或批量 SDK 方法 |
| 缺少 `limit` 参数 | **添加显式 `limit`**，匹配 UI 的页面大小（例如 25、50、100） |
| 基于偏移的分页用于大型数据集 | **替换为基于游标的分页**，使用响应中的 `nextCursor` |
| "获取所有" 循环（提前耗尽游标） | **替换为按需分页**，使用 TanStack Query 的 `useInfiniteQuery` |

**修复 "获取所有" 循环**——用 `useInfiniteQuery` 替换 while 循环：

```ts
// BAD — 在渲染前获取所有页面
let allItems = [];
let cursor = undefined;
while (true) {
  const result = await client.instances.list({ limit: 1000, cursor });
  allItems.push(...result.items);
  if (!result.nextCursor) break;
  cursor = result.nextCursor;
}

// FIX — 使用 useInfiniteQuery 按需分页
const { data, fetchNextPage, hasNextPage } = useInfiniteQuery({
  queryKey: ["instances", filters],
  queryFn: ({ pageParam }) =>
    client.instances.list({ limit: 100, cursor: pageParam, ...filters }),
  getNextPageParam: (lastPage) => lastPage.nextCursor ?? undefined,
  staleTime: 30_000,
});
```

**修复基于偏移的分页**——切换到基于游标：

```ts
// BAD — 偏移分页在规模上退化
const result = await client.instances.list({ limit: 100, offset: page * 100 });

// FIX — 基于游标的分页
const result = await client.instances.list({ limit: 100, cursor: nextCursor });
```

---

## 第 6 步——查找和修复过度的 API 调用频率

```bash
# 查找触发查询的搜索/过滤输入
grep -rn --include="*.tsx" --include="*.ts" -E "onChange|onInput|onSearch|onFilter" src/ | grep -i "search\|filter\|query"

# 查找 debounce 使用
grep -rn --include="*.ts" --include="*.tsx" -i -E "debounce|useDebouncedValue|useDebounce" src/

# 查找轮询/间隔模式
grep -rn --include="*.ts" --include="*.tsx" -E "setInterval|refetchInterval|pollingInterval|refetchOnWindowFocus" src/

# 查找控制 useQuery 刷新行为的 useQuery 选项
grep -rn --include="*.ts" --include="*.tsx" -E "staleTime|cacheTime|gcTime|refetchOnMount|refetchOnWindowFocus" src/
```

对于每个发现的问题，**应用修复**：

**搜索输入在每按一次键时触发 → 添加 300ms 延迟的 debounce：**
```tsx
// BAD — 每次按键都触发 API 调用
const [search, setSearch] = useState("");
const { data } = useQuery({ queryKey: ["search", search], queryFn: () => api.search(search) });

// FIX — 创建或使用具有 300ms 延迟的 useDebouncedValue 钩子
function useDebouncedValue<T>(value: T, delay = 300): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}

const [search, setSearch] = useState("");
const debouncedSearch = useDebouncedValue(search, 300);
const { data } = useQuery({
  queryKey: ["search", debouncedSearch],
  queryFn: () => api.search(debouncedSearch),
  enabled: debouncedSearch.length > 0,
});
```

**没有 staleTime 的 useQuery 调用 → 添加适当的 staleTime：**
```ts
// BAD — 每次挂载/聚焦时刷新
useQuery({ queryKey: ["data"], queryFn: fetchData });

// FIX — 添加 staleTime 防止不必要的刷新
useQuery({ queryKey: ["data"], queryFn: fetchData, staleTime: 30_000 });
```

**重复的并行相同请求 → 将查询提升到共享钩子：**
```ts
// BAD — 多个组件独立调用相同的查询
// ComponentA.tsx: useQuery({ queryKey: ["assets"], queryFn: fetchAssets });
// ComponentB.tsx: useQuery({ queryKey: ["assets"], queryFn: fetchAssets });

// FIX — 创建共享钩子，从两个组件导入
// hooks/useAssets.ts
export function useAssets() {
  return useQuery({ queryKey: ["assets"], queryFn: fetchAssets, staleTime: 30_000 });
}
```

| 问题 | 应用修复 |
|------|----------|
| 搜索输入在每按一次键时触发查询 | **添加 `useDebouncedValue` 钩子**，延迟 300ms |
| 没有回退或间隔非常短的轮询 | **设置间隔 ≥30s**，错误时指数回退 |
| 每次渲染都重新获取（无缓存） | **在 useQuery 选项中添加 `staleTime: 30_000`**（或适当的） |
| `refetchOnWindowFocus: true` 用于昂贵查询 | **设置 `refetchOnWindowFocus: false`** 或使用较长的 stale time |
| 重复的并行相同请求 | **将查询提升到共享钩子**，从两个组件导入 |
| 多个组件触发相同的获取 | **在 `hooks/` 目录中提取为共享钩子** |

---

## 第 7 步——查找和修复大型未虚拟化列表

搜索渲染项超过 ~50 项的列表：
```bash
grep -rn --include="*.tsx" -E "\.(map|forEach)\(" src/
```

对于任何数据源可能超过 50 项的列表，**用虚拟化列表替换普通的 `.map()` 渲染**。如果不存在，请安装 `@tanstack/react-virtual`：

```bash
pnpm add @tanstack/react-virtual
```

**直接应用虚拟化模式：**

```tsx
// BAD — 在 DOM 中渲染所有项
<div>
  {items.map((item) => (
    <div key={item.id}>{item.name}</div>
  ))}
</div>

// FIX — 替换为虚拟化列表
import { useVirtualizer } from "@tanstack/react-virtual";

const parentRef = useRef<HTMLDivElement>(null);
const rowVirtualizer = useVirtualizer({
  count: items.length,
  getScrollElement: () => parentRef.current,
  estimateSize: () => 48,
});

return (
  <div ref={parentRef} style={{ height: "600px", overflow: "auto" }}>
    <div style={{ height: rowVirtualizer.getTotalSize(), position: "relative" }}>
      {rowVirtualizer.getVirtualItems().map((virtualRow) => (
        <div
          key={virtualRow.key}
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: `${virtualRow.size}px`,
            transform: `translateY(${virtualRow.start}px)`,
          }}
        >
          {items[virtualRow.index].name}
        </div>
      ))}
    </div>
  </div>
);
```

---

## 第 8 步——查找和修复缺失的代码拆分

阅读路由设置，并识别导入静态但未在着陆页上显示的路由。

**对于每个静态导入的重型页面，将其转换为使用 `React.lazy()` 和 `Suspense` 的懒导入：**

```tsx
// BAD — 静态导入，初始包中加载
import { ReportPage } from "./pages/ReportPage";

// FIX — 转换为懒导入
import { lazy, Suspense } from "react";
const ReportPage = lazy(() => import("./pages/ReportPage"));

// 在路由中——用 Suspense 包装
<Suspense fallback={<PageSkeleton />}>
  <ReportPage />
</Suspense>
```

类似地，大型第三方组件（图表库、PDF 查看器、地图渲染器）应在需要它们的组件内部动态导入，而不是在模块级别。**直接应用转换**到每个找到的重型导入。

---

## 第 9 步——分析和修复包大小

```bash
# 如果尚未安装，请安装，然后运行
pnpm add -D rollup-plugin-visualizer
```

临时添加到 `vite.config.ts`：
```ts
import { visualizer } from "rollup-plugin-visualizer";

export default defineConfig({
  plugins: [
    react(),
    visualizer({ open: true, gzipSize: true, brotliSize: true }),
  ],
});
```

运行 `pnpm run build` 并检查树状图。对于任何大于 100 KB（压缩后）且不是必要初始依赖的块，**应用修复**：

| 问题 | 应用修复 |
|------|----------|
| `lodash`（完整包） | **替换为 `lodash-es`** 单独导入或原生等效项（例如，`Array.prototype.map`、`Object.entries`、`structuredClone`） |
| `moment` | **替换为 `date-fns`** 或原生 `Intl.DateTimeFormat` |
| 未被树状提取的图表库 | **切换到命名导入**（例如，`import { LineChart } from "echarts/charts"`） |
| 仅在一处使用的库 | **动态导入**，使用 `React.lazy` 或内联 `import()` |

```ts
// BAD
import _ from "lodash";
const sorted = _.sortBy(items, "name");

// FIX — 使用 lodash-es 或原生
import sortBy from "lodash-es/sortBy";
const sorted = sortBy(items, "name");
// OR 原生：
const sorted = [...items].sort((a, b) => a.name.localeCompare(b.name));
```

```ts
// BAD
import moment from "moment";
const formatted = moment(date).format("YYYY-MM-DD");

// FIX — 使用 date-fns
import { format } from "date-fns";
const formatted = format(date, "yyyy-MM-dd");
```

**分析后，从 `vite.config.ts` 中移除 visualizer 插件并卸载它：**
```bash
pnpm remove rollup-plugin-visualizer
```

---

## 第 10 步——查找和修复内存泄漏

搜索设置订阅、计时器或事件监听器而未进行清理的 `useEffect` 钩子：

```bash
grep -rn --include="*.tsx" --include="*.ts" -A 10 "useEffect" src/
```

对于每个调用 `addEventListener`、`setInterval`、`setTimeout`、`subscribe` 或设置 CDF 流式连接的 `useEffect`，**添加缺失的清理函数**：

**无 abort 的获取 → 添加 AbortController：**
```ts
// BAD — 没有清理，获取在卸载后继续
useEffect(() => {
  fetchData(id);
}, [id]);

// FIX — 添加 AbortController 进行清理
useEffect(() => {
  const controller = new AbortController();
  fetchData(id, controller.signal);
  return () => controller.abort();
}, [id]);
```

**无清理的计时器 → 添加 clearInterval/clearTimeout：**
```ts
// BAD — 间隔在卸载后继续运行
useEffect(() => {
  const id = setInterval(() => poll(), 5000);
}, []);

// FIX — 添加 clearInterval 清理
useEffect(() => {
  const id = setInterval(() => poll(), 5000);
  return () => clearInterval(id);
}, []);
```

**无清理的事件监听器 → 添加 removeEventListener：**
```ts
// BAD — 监听器在每个渲染时累积
useEffect(() => {
  window.addEventListener("resize", handleResize);
}, []);

// FIX — 添加 removeEventListener 清理
useEffect(() => {
  window.addEventListener("resize", handleResize);
  return () => window.removeEventListener("resize", handleResize);
}, []);
```

---

## 第 11 步——测量后报告差异

重新运行第 1 步的相同 Lighthouse 审计和 React Profiler 会话。报告差异并列出每个更改的文件：

| 指标 | 之前 | 之后 | 变化 |
|------|------|------|------|
| Lighthouse 性能 | 72 | 91 | +19 |
| Largest Contentful Paint | 3.2 s | 1.8 s | −1.4 s |
| Total Blocking Time | 420 ms | 80 ms | −340 ms |
| 压缩包大小 (gzipped) | 410 KB | 290 KB | −120 KB |
| `AssetTable` 渲染次数（在过滤更改时） | 8 | 2 | −6 |

如果某个步骤未产生改进，请明确说明。不要编造数字。

---

## 完成

列出每个更改的绝对路径和一行解释修复的内容。如果进一步改进需要服务器端或基础设施更改（例如，CDF 响应缓存、CDN 配置），请将它们作为超出范围的建议单独注明。
