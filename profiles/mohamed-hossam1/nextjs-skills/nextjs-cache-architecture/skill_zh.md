# Next.js 缓存架构

从一开始就在 Next.js 16+ App Router 项目中构建缓存架构——不仅仅是随意放置 `"use cache"`，而是要构建标签注册表、失效验证工具、Suspense 边界和变更连接，以便随着代码库的增长，缓存始终保持正确。

## 如何使用这项技能

将以下所有规则和模板应用于用户的实际项目。在编写任何代码之前，将占位符（如 `[Entity]` 和 `[collection]`）替换为代码库中的名称。

```text
$ARGUMENTS
```

## 下一步该查看哪里

大多数实现只需要这个文件。在需要时加载参考。

| 如果用户是...                                                                                       | 阅读                                          |
| ------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| 询问缓存键如何派生、`cacheLife` 配置文件的含义，或遇到 `"use cache"` 限制 | `references/core-concepts.md`                 |
| 缓存任何依赖于已登录用户的内容                                                       | `references/personalized-content.md`          |
| 报告过时数据或进行最终审查                                                              | `references/debugging-and-checklist.md`       |
| 将现有代码库从 `unstable_cache` 迁移到其他地方                                                     | `references/migration-from-unstable-cache.md` |

`assets/` 中的即插即用模板（将占位符重命名为匹配用户的代码库）：

- `assets/tags.ts` → `lib/cache/tags.ts`
- `assets/revalidate.ts` → `lib/cache/revalidate.ts`
- `assets/SuspenseOnSearchParams.tsx` → `components/SuspenseOnSearchParams.tsx`

## 一口气看懂架构

一个正确的缓存实现有三个承重部分。从一开始就构建所有三个部分——添加它们比一开始就正确构建要困难得多。

1. **标签注册表** (`lib/cache/tags.ts`) — 每个标签字符串都放在这里。其他地方没有原始字符串。
2. **失效验证工具** (`lib/cache/revalidate.ts`) — 每个 `updateTag()` 都放在这里。变更从该文件导入。
3. **在数据上而不是页面上放置缓存** — `"use cache"` 放在数据获取函数或缓存的子组件上。页面组件协调 Suspense 边界；子组件获取数据。

一旦这三个部分就位，其余的就是一致地应用它们。

## 第 1 步 — 启用缓存组件

```ts
// next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  cacheComponents: true,
};

export default nextConfig;
```

## 第 2 步 — 构建缓存标签注册表

**文件：** `lib/cache/tags.ts`（模板：`assets/tags.ts`）

使用 `assets/tags.ts` 模板。`as const satisfies TagRegistry` 形状提供字面量类型，并在编译时拒绝格式错误的条目。

```ts
// lib/cache/tags.ts (骨架——完整模板在 assets/tags.ts 中)

export const CACHE_TAGS = {
  // 集合标签——每个逻辑数据组一个，始终存在。
  [collection]: "[collection]",

  // 实体标签工厂——只有在单个条目发生变更时才存在。
  [entity]: (id: string | number) => `[entity]:${id}`,
} as const;
```

## 第 3 步 — 构建失效验证工具

**文件：** `lib/cache/revalidate.ts`（模板：`assets/revalidate.ts`）

所有 `updateTag()` 调用都在这里。变更导入这些函数——它们从不直接调用 `updateTag()`。

```ts
// lib/cache/revalidate.ts
"use server";

import { updateTag } from "next/cache";
import { CACHE_TAGS } from "./tags";

function updateTags(tags: string[]) {
  for (const tag of tags) updateTag(tag);
}

// 批量——集合中的任何条目发生变更。
export async function revalidate[Collection]Cache() {
  updateTags([CACHE_TAGS.[collection]]);
}

// 手术式——特定条目发生变更。
// 只有在注册表中存在 `CACHE_TAGS.[entity]` 工厂时才编写此代码。
export async function revalidate[Entity]Cache(id: string | number) {
  updateTags([
    CACHE_TAGS.[collection], // 始终使父集合失效
    CACHE_TAGS.[entity](id),
  ]);
}
```

## 第 4 步 — 实现数据获取

在数据获取函数中放置 `"use cache"`。永远不要在页面组件中获取数据——页面组件协调，而不是获取数据。

```ts
// lib/data/[domain].ts
import { cacheLife, cacheTag } from "next/cache";
import { CACHE_TAGS } from "@/lib/cache/tags";

const BASE_URL = process.env.API_BASE_URL!;

// 良好：集合获取。
export async function get[Collection]() {
  "use cache";
  cacheLife("hours");
  cacheTag(CACHE_TAGS.[collection]);

  const res = await fetch(`${BASE_URL}/[endpoint]`);
  return res.json();
}

// 良好：实体获取。
export async function get[Entity](id: string) {
  "use cache";
  cacheLife("hours");
  cacheTag(CACHE_TAGS.[collection]);
  // 只有在变更需要对此条目调用 `updateTag` 时才添加 `CACHE_TAGS.[entity](id)`。

  const res = await fetch(`${BASE_URL}/[endpoint]/${id}`);
  return res.json();
}
```

```tsx
// 不良：在页面组件中获取数据会绕过缓存和失效验证。
export default async function Page() {
  const res = await fetch("/api/items");
  const data = await res.json();
  return <View data={data} />;
}
```

## 第 5 步 — 结构化渲染边界

每个页面都遵循以下结构：

```
页面组件（同步，仅协调——不获取数据）
  ├── 静态外壳（布局、导航——不获取数据）
  ├── <Suspense> → 缓存的共享内容
  └── <Suspense> → 动态个性化内容
```

### 标准页面

```tsx
// app/[route]/page.tsx
import { Suspense } from "react";
import { cacheLife, cacheTag } from "next/cache";
import { CACHE_TAGS } from "@/lib/cache/tags";
import { get[Collection] } from "@/lib/data/[domain]";

export default function AnyPage() {
  return (
    <>
      <StaticShell />

      <Suspense fallback={<SharedSkeleton />}>
        <SharedContent />
      </Suspense>

      <Suspense fallback={<PersonalizedSkeleton />}>
        <PersonalizedSection />
      </Suspense>
    </>
  );
}

async function SharedContent() {
  "use cache";
  cacheLife("hours");
  cacheTag(CACHE_TAGS.[collection]);

  const data = await get[Collection]();
  return <[Collection]List data={data} />;
}
```

### 动态路由页面

```tsx
// app/[domain]/[id]/page.tsx
import { Suspense } from "react";
import { cacheLife, cacheTag } from "next/cache";
import { CACHE_TAGS } from "@/lib/cache/tags";
import { get[Entity] } from "@/lib/data/[domain]";

export default function EntityPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  return (
    <Suspense fallback={<EntitySkeleton />}>
      <EntityDetail params={params} />
    </Suspense>
  );
}

async function EntityDetail({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <CachedEntityView id={id} />;
}

async function CachedEntityView({ id }: { id: string }) {
  "use cache";
  cacheLife("hours");
  cacheTag(CACHE_TAGS.[collection]);
  // 只有在变更需要手术式失效验证时才添加 `CACHE_TAGS.[entity](id)`。

  const item = await get[Entity](id);
  return <[Entity]View item={item} />;
}
```

### 过滤/搜索参数页面

```tsx
// app/[route]/page.tsx
import { cacheLife, cacheTag } from "next/cache";
import { CACHE_TAGS } from "@/lib/cache/tags";
import { get[Collection]ByFilter } from "@/lib/data/[domain]";
import SuspenseOnSearchParams from "@/components/SuspenseOnSearchParams";

export default function FilteredPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string>>;
}) {
  return (
    <SuspenseOnSearchParams fallback={<FilteredListSkeleton />}>
      <FilteredList searchParams={searchParams} />
    </SuspenseOnSearchParams>
  );
}

async function FilteredList({
  searchParams,
}: {
  searchParams: Promise<Record<string, string>>;
}) {
  "use cache";
  cacheLife("minutes");
  cacheTag(CACHE_TAGS.[collection]);
  // searchParams 是参数→自动按唯一参数组合键。

  const { q = "", page = "1" } = await searchParams;
  return await get[Collection]ByFilter(q, page);
}
```

标准的 `<Suspense>` 在客户端导航时仅 `searchParams` 变更不会重新触发其回退。在具有搜索或过滤参数的每个页面上使用 `SuspenseOnSearchParams`（模板：`assets/SuspenseOnSearchParams.tsx`）。

## 第 6 步 — 处理个性化内容

在缓存边界**外部**读取 `cookies()` / `headers()` / `auth()` 并将值作为属性传递。参数成为自动生成的缓存键的一部分，因此每个用户都有自己的条目。在这些 API 中的任何位置调用会引发错误或产生不正确的行为。

有关完整的“外部读取/内部缓存”模式和罕见的 `"use cache: private"` 例外，请参阅 `references/personalized-content.md`。

## 第 7 步 — 连接变更到失效验证

变更调用失效验证工具，并且永远不会自己调用 `updateTag()`。这使缓存层保持机械化和可审计性，并允许您在一个地方添加可观察性（日志记录、跟踪）。

```ts
// app/actions/[domain].ts
"use server";

import {
  revalidate[Collection]Cache,
  revalidate[Entity]Cache,
} from "@/lib/cache/revalidate";

export async function create[Entity](payload: unknown) {
  await db.[entity].create(payload);
  await revalidate[Collection]Cache();
}

export async function update[Entity](id: string | number, payload: unknown) {
  await db.[entity].update(id, payload);
  await revalidate[Entity]Cache(id); // 需要导出手术式工具
}
```

### `updateTag` vs `revalidateTag`

两个 API 用于不同的需求：

| API                         | 效果                                                           | 调用来源                          |
| --------------------------- | ---------------------------------------------------------------- | ---------------------------------- |
| `updateTag(tag)`            | 立即——相同的请求看到最新数据                                 | 服务器动作，通过 `revalidate.ts` |
| `revalidateTag(tag, "max")` | 背景陈旧数据验证——下一个请求看到最新数据                     | 路由处理程序、Webhooks            |

`revalidateTag` 始终接受第二个参数（`"max"` 用于陈旧数据验证，`{ expire: 0 }` 用于立即硬过期）。单参数形式已弃用，并在某些配置中静默不做任何事情。

## 常见错误

当缓存行为异常时，按顺序检查这些内容。前六个可以捕获几乎所有问题；只有在其他所有内容通过后才能运行 `next build`。完整的调试步骤和签收清单在 `references/debugging-and-checklist.md` 中。

| 症状或迹象                                            | 修复                                                                          |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------- |
| 函数在每次请求时都未缓存运行                     | `"use cache"` 在 `await` 之后——将其移到作为第一个语句。       |
| 缓存函数根据每个用户返回错误数据       | 将 `cookies()` / `headers()` / `auth()` 移到外部；将值作为参数传递。 |
| `updateTag` 无效                                    | 标签字错误，或没有 `cacheTag` 注册匹配的标签。          |
| 变更完成但列表仍然读取过时           | 失效验证工具在写入之前调用，或根本未调用。          |
| 即使只有一个部分更改，整个页面仍然重新渲染  | 动态子组件位于缓存的父组件内部——使用 `<Suspense>` 分割。       |
| 过滤 UI 在导航时没有显示加载状态        | 普通的 `<Suspense>` — 切换到 `SuspenseOnSearchParams`。                     |
| 页面标记为动态，而您期望静态                | 运行 `next build`；跟踪路由源树中泄漏的动态 API。   |
| 页面组件直接获取数据                        | 将获取移到缓存的子组件中；页面应协调，而不是获取数据。     |

有关完整的调试步骤和签收清单，请参阅 `references/debugging-and-checklist.md`。要验证已完成实现的静态部分与用户的项目的匹配情况，运行 `scripts/audit.mjs <project-root>`——用法及其检查内容在 `README.md` 中记录。
