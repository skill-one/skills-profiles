# 性能优化

## 概述

优化前先进行测量。没有测量的性能工作就是猜测——而猜测会导致过早优化，这种优化会增加不必要的复杂性，却无法提升真正重要的性能。先进行性能分析，找出实际的瓶颈，修复它，然后再次测量。只优化那些测量证明重要的部分。

## 何时使用

- 规范中存在性能要求（加载时间预算、响应时间 SLA）
- 用户或监控报告性能缓慢
- 核心网络指标得分低于阈值
- 你怀疑某个变更引入了回归
- 构建处理大型数据集或高流量的功能

**不使用的情况：** 在你获得问题证据之前不要进行优化。过早优化会增加比它所获得的性能更多的复杂性。

## 核心网络指标目标

| 指标 | 优秀 | 需要改进 | 差 |
|------|------|----------|----|
| **LCP**（最大内容绘制） | ≤ 2.5 秒 | ≤ 4.0 秒 | > 4.0 秒 |
| **INP**（交互到下一次绘制） | ≤ 200 毫秒 | ≤ 500 毫秒 | > 500 毫秒 |
| **CLS**（累积布局偏移） | ≤ 0.1 | ≤ 0.25 | > 0.25 |

## 优化工作流程

```
1. 测量  → 使用真实数据建立基线
2. 确定 → 找到实际的瓶颈（而不是假设的）
3. 修复 → 解决特定的瓶颈
4. 验证  → 再次测量；保留或回滚
5. 防护  → 添加监控或测试以防止回归
```

### 第 1 步：测量

有两种互补的方法——使用两者：

- **合成（Lighthouse、DevTools 性能标签页）：** 控制条件，可重复。最适合 CI 回归检测和隔离特定问题。
- **RUM（web-vitals 库、CrUX）：** 真实用户在真实条件下的数据。需要验证修复是否真正改善了用户体验。

**前端：**
```bash
# 合成：Chrome DevTools 中的 Lighthouse（或 CI）
# Chrome DevTools → 性能标签页 → 录制
# Chrome DevTools MCP → 性能跟踪

# RUM：代码中的 Web Vitals 库
import { onLCP, onINP, onCLS } from 'web-vitals';

onLCP(console.log);
onINP(console.log);
onCLS(console.log);
```

**后端：**
```bash
# 响应时间日志记录
# 应用性能监控（APM）
# 带时间戳的数据库查询日志

# 简单时间测量
console.time('db-query');
const result = await db.query(...);
console.timeEnd('db-query');
```

### 从何处开始测量

使用症状决定首先测量什么：

```
什么是慢的？
├── 首次页面加载
│   ├── 大包？ --> 测量包大小，检查代码拆分
│   ├── 服务器响应慢？ --> 在 DevTools 网络瀑布流中测量 TTFB
│   │   ├── DNS 慢？ --> 为已知来源添加 dns-prefetch / preconnect
│   │   ├── TCP/TLS 慢？ --> 启用 HTTP/2，检查边缘部署，keep-alive
│   │   └── 等待（服务器）慢？ --> 分析后端，检查查询和缓存
│   └── 布局阻塞资源？ --> 检查网络瀑布流中的 CSS/JS 阻塞
├── 交互感觉迟缓
│   ├── 点击时 UI 冻结？ --> 分析主线程，查找长任务（>50ms）
│   ├── 表单输入延迟？ --> 检查重渲染，受控组件开销
│   └── 动画卡顿？ --> 检查布局抖动，强制重排
├── 导航后的页面
│   ├── 数据加载？ --> 测量 API 响应时间，检查瀑布流
│   └── 客户端渲染？ --> 分析组件渲染时间，检查 N+1 获取
└── 后端 / API
    ├── 单个端点慢？ --> 分析数据库查询，检查索引
    ├── 所有端点慢？ --> 检查连接池，内存，CPU
    └── 间歇性慢？ --> 检查锁争用，GC 暂停，外部依赖
```

### 第 2 步：确定瓶颈

按类别常见的瓶颈：

**前端：**

| 症状 | 可能原因 | 调查 |
|------|----------|------|
| LCP 慢 | 大图像，布局阻塞资源，服务器慢 | 检查网络瀑布流，图像大小 |
| CLS 高 | 没有尺寸的图像，内容加载慢，字体偏移 | 检查布局偏移归因 |
| INP 差 | 主线程上的重 JavaScript，大的 DOM 更新 | 在性能跟踪中检查长任务 |
| 初始加载慢 | 大包，许多网络请求 | 检查包大小，代码拆分 |

**后端：**

| 症状 | 可能原因 | 调查 |
|------|----------|------|
| API 响应慢 | N+1 查询，缺少索引，未优化的查询 | 检查数据库查询日志 |
| 内存增长 | 泄漏引用，无界缓存，大数据包 | 堆分析 |
| CPU 峰值 | 同步重计算，正则表达式回溯 | CPU 分析 |
| 高延迟 | 缺少缓存，冗余计算，网络跳转 | 跟踪请求通过堆栈 |

### 第 3 步：修复常见反模式

#### N+1 查询（后端）

```typescript
// BAD: N+1 — 每个任务一个查询用于所有者
const tasks = await db.tasks.findMany();
for (const task of tasks) {
  task.owner = await db.users.findUnique({ where: { id: task.ownerId } });
}

// GOOD: 单个查询带连接/包含
const tasks = await db.tasks.findMany({
  include: { owner: true },
});
```

#### 无界数据获取

```typescript
// BAD: 获取所有记录
const allTasks = await db.tasks.findMany();

// GOOD: 分页带限制
const tasks = await db.tasks.findMany({
  take: 20,
  skip: (page - 1) * 20,
  orderBy: { createdAt: 'desc' },
});
```

#### 查询忽略其索引

"添加索引"是猜测。查询计划才是测量：

```sql
EXPLAIN ANALYZE
SELECT id, title FROM tasks
WHERE owner_id = 42 ORDER BY created_at DESC LIMIT 20;
```

输出中的三件事决定修复：

| 你看到的内容 | 它意味着什么 |
|---|---|
| 在一个大型表上 `Seq Scan`，而预期有索引 | 没有可用的索引用于此谓词 |
| 估计的 `rows=` 与实际相差一个数量级 | 统计信息过时；规划器基于坏信息选择 |
| 扫描上方的 `Sort` 节点 | 索引覆盖了过滤器但没有 `ORDER BY` |

索引针对的是**查询的形状**，而不是孤立列。在复合索引中，相等列优先，然后是范围或排序列：

```sql
CREATE INDEX idx_tasks_owner_created ON tasks (owner_id, created_at DESC);
```

**索引不会帮助的情况：**

| 情况 | 原因 |
|------|------|
| 低选择性，查询主导值（一个 95% 为 `active` 的 `status` 列过滤为 `active`） | 序列扫描确实更便宜；规划器会忽略索引。过滤稀有值是相反的情况，部分索引效果很好 |
| 前导通配符（`LIKE '%term'`） | B-tree 无法在无前缀的情况下搜索；需要 trigram 或全文搜索 |
| 列上的函数（`WHERE lower(email) = ?`） | 普通列索引不可用；索引表达式 |
| 写入密集型表 | 每个索引都是每个 `INSERT`/`UPDATE` 的税；测量写入成本，而不仅仅是读取收益 |

重新运行 `EXPLAIN ANALYZE`。如果索引没有改变计划，则回滚（第 4 步），而且它仍然会为每个写入成本：它仍然会为每个写入成本。

#### 连接池耗尽

特征很独特：**所有**端点同时变慢，慢时间用于等待连接而不是执行，数据库报告大部分空闲会话。

```typescript
// BAD: 每个请求或每个模块一个池——在无服务器情况下，这会乘以实例数并耗尽数据库的连接限制
// GOOD: 每个进程一个池，相对于数据库的极限进行缩放
const pool = new Pool({
  max: 10,                        // 实例数 × max 必须保持在 max_connections 以下
  idleTimeoutMillis: 30_000,
  connectionTimeoutMillis: 5_000, // 快速失败而不是无限排队
});
```

**越大越快是错误的。** 大于数据库可以并发执行的池只会将队列从你的应用转移到数据库，在那里更难看到。当实例数无界（无服务器，自动扩展）时，多路复用连接的代理（pgbouncer，RDS Proxy）是修复方法，而不是更高的 `max`。

#### 缺少图像优化（前端）

```html
<!-- BAD: 没有尺寸，没有格式优化 -->
<img src="/hero.jpg" />

<!-- GOOD: Hero / LCP 图像——艺术方向 + 分辨率切换，高优先级 -->
<!--
  两种技术结合：
  - 艺术方向（媒体）：每个断点不同的裁剪/构图
  - 分辨率切换（srcset + sizes）：每个屏幕密度正确的文件大小
-->
<picture>
  <!-- 移动端：横版裁剪（8:10） -->
  <source
    media="(max-width: 767px)"
    srcset="/hero-mobile-400.avif 400w, /hero-mobile-800.avif 800w"
    sizes="100vw"
    width="800"
    height="1000"
    type="image/avif"
  />
  <source
    media="(max-width: 767px)"
    srcset="/hero-mobile-400.webp 400w, /hero-mobile-800.webp 800w"
    sizes="100vw"
    width="800"
    height="1000"
    type="image/webp"
  />
  <!-- 桌面端：横版裁剪（2:1） -->
  <source
    srcset="/hero-800.avif 800w, /hero-1200.avif 1200w, /hero-1600.avif 1600w"
    sizes="(max-width: 1200px) 100vw, 1200px"
    width="1200"
    height="600"
    type="image/avif"
  />
  <source
    srcset="/hero-800.webp 800w, /hero-1200.webp 1200w, /hero-1600.webp 1600w"
    sizes="(max-width: 1200px) 100vw, 1200px"
    width="1200"
    height="600"
    type="image/webp"
  />
  <img
    src="/hero-desktop.jpg"
    width="1200"
    height="600"
    fetchpriority="high"
    alt="Hero 图像描述"
  />
</picture>

<!-- GOOD: 下方图像——懒加载 + 异步解码 -->
<img
  src="/content.webp"
  width="800"
  height="400"
  loading="lazy"
  decoding="async"
  alt="内容图像描述"
/>
```

#### 不必要的重渲染（React）

```tsx
// BAD: 每次渲染创建新对象，导致子组件重渲染
function TaskList() {
  return <TaskFilters options={{ sortBy: 'date', order: 'desc' }} />;
}

// GOOD: 稳定引用
const DEFAULT_OPTIONS = { sortBy: 'date', order: 'desc' } as const;
function TaskList() {
  return <TaskFilters options={DEFAULT_OPTIONS} />;
}

// 使用 React.memo 为昂贵组件
const TaskItem = React.memo(function TaskItem({ task }: Props) {
  return <div>{/* 昂贵渲染 */}</div>;
});

// 使用 useMemo 为昂贵计算
function TaskStats({ tasks }: Props) {
  const stats = useMemo(() => calculateStats(tasks), [tasks]);
  return <div>{stats.completed} / {stats.total}</div>;
}
```

#### 大包大小

```typescript
// 现代 bundlers (Vite, webpack 5+) 处理命名导入与树摇自动，前提是依赖项提供 ESM 并在 package.json 中标记 `sideEffects: false`。
// 在更改导入样式之前进行性能分析——真正的收益来自拆分和懒加载。

// GOOD: 动态导入用于重型、很少使用的功能
const ChartLibrary = lazy(() => import('./ChartLibrary'));

// GOOD: 路由级代码拆分，用 Suspense 包装
const SettingsPage = lazy(() => import('./pages/Settings'));

function App() {
  return (
    <Suspense fallback={<Spinner />}>
      <SettingsPage />
    </Suspense>
  );
}
```

#### 缺少缓存（后端）

缓存那些生成昂贵且比它变化更频繁的内容。缓存一个已经快速的调用不会带来任何收益，反而会引入陈旧性错误。缓存昂贵且远比写入更频繁读取的内容。

**故意选择层：**

| 层 | 可见于 | 使用情况 | 成本 |
|---|---|---|---|
| 进程内（`Map`，LRU） | 一个实例 | 小型、热、每个实例可接受的陈旧性 | 每个实例独立漂移；失效仅影响一个 |
| 共享（Redis，Memcached） | 所有实例 | 实例必须同意，或者值需要昂贵的重新计算 | 网络跳转，以及运行和监控另一个服务 |
| CDN / 边缘 | 每个 URL 的每个人 | 响应对于给定键是公开且相同的 | 失效是难题；假设你无法快速召回错误响应 |

```typescript
// 缓存频繁读取、很少更改的数据
const CACHE_TTL = 5 * 60 * 1000; // 5 分钟
let cachedConfig: AppConfig | null = null;
let cacheExpiry = 0;

async function getAppConfig(): Promise<AppConfig> {
  if (cachedConfig && Date.now() < cacheExpiry) {
    return cachedConfig;
  }
  cachedConfig = await db.config.findFirst();
  cacheExpiry = Date.now() + CACHE_TTL;
  return cachedConfig;
}

// 静态资产的 HTTP 缓存头
app.use('/static', express.static('public', {
  maxAge: '1y',           // 缓存 1 年
  immutable: true,        // 永不重新验证（在文件名中使用内容哈希）
}));

// API 响应的 Cache-Control
res.set('Cache-Control', 'public, max-age=300'); // 5 分钟
```

**关键设计决定正确性。** 每个更改响应的输入都属于键：租户、区域设置、权限、功能标志。省略查看者的键会导致一个用户的数据被提供给另一个用户，这会作为性能提升被发布。你保留的代码，你将永远维护。让它证明自己的价值。

**选择一种失效策略，而不是三种：**

| 策略 | 交易 |
|---|---|
| TTL | 最简单。你接受最多 TTL 的陈旧性，因此明确说明可接受的时间窗口 |
| 基于事件或标签 | 写入时新鲜，但现在写入者必须知道缓存拓扑 |
| 版本化键（`user:42:profile:v7`） | 永不失效，只是停止读取旧键。直到淘汰前，内存成本都很高 |

**防止羊群效应。** 热键过期，所有并发请求同时错过，然后源端一次性承担全部负载，这就是缓存如何从防止故障变成故障的原因。在单个请求重新计算的同时提供陈旧数据（`stale-while-revalidate`），或者将并发错过合并到一个正在进行的承诺后面，以便 N 个等待者导致一次重新计算。

**不要缓存：** 任何陈旧性是正确性错误的东西（余额、权限、结账时的库存），或者键不识别用户的每个用户数据。参见 `../../references/performance-checklist.md` 以获取请求合并、写入策略、负缓存和缓存清单。

### 第 4 步：验证（保留或回滚）

修复是一个假设，直到你重新测量。这一步决定它是否存活。

**以与基线相同的方式重新测量：** 相同命令，相同条件，相同固定预算（墙钟时间、样本数或请求数）。在冷缓存上获取的基线与在热缓存上获取的结果测量的是缓存，而不是你的变更。

**一次只改变一件事。** 三个优化一起发布产生一个数字，而你无法归因。如果它们必须一起发布，请先单独测量每个优化。

**超越噪声，而不仅仅是平均值。** 重复测量并比较增量与运行间方差。3% 的增益在 ±5% 方差内不是增益；它是不同的样本。

然后严格决定：

| 结果与基线对比 | 动作 |
|---|---|
| 超过阈值，测试绿色 | **保留。** 在提交信息中包含之前/之后的数字。 |
| 在噪声内（没有可测量的变化） | **回滚。** |
| 更差 | **回滚。** |
| 改善，但有一个测试变红 | **回滚。** 一个穿着胜利外衣的回归。 |

**“中性”是回滚，而不是保留。** 这是团队跳过的一步：变更已经编写，丢弃它感觉浪费，所以它未经测量就发布，而代码库积累了永远不会带来任何收益的复杂性。你保留的代码，你将永远维护。让它证明自己的价值。

**正确性控制指标。** 套件保持绿色 *并且* 数字有所移动。一个“优化”通过放弃产品需要的工作（跳过验证、缓存必须新鲜的东西、删除负载均衡的 `await`）获胜，这不是胜利，而是回归。

#### 记录每次尝试，包括回滚的尝试

回滚的工作在 git 历史中没有痕迹，这恰恰是为什么同一个死想法在下个季度会被再次尝试。保留一个简短的账本，以便一个被丢弃的想法保持被丢弃：

| 想法 | 基线 → 结果 | 判决 | 原因 |
|---|---|---|---|
| Memoize 行组件 | INP 240ms → 235ms | 回滚 | 在噪声内（±15ms）。行不是瓶颈。 |
| 虚拟化列表 | INP 240ms → 90ms | 保留 | 跟踪中消失的长任务。 |
| 预连接到 API 源 | LCP 2.8s → 2.8s | 回滚 | 已经是同源。 |

PR 描述中的一个部分或存储库中的 `PERF.md` 都可以工作。重要的是，下一个人（或代理）在提出实验之前会阅读它，并且不会重新运行已经失败的实验。

### 第 5 步：防止回归

保护用户实际感受到的指标，而不是每个可用的数字。使用与 LCP、INP、p95 延迟或其他证明修复的原始指标相同的指标。

在用户界面面前使用两个互补层：

- **合成 CI 门禁：** 在合并前捕获可重复回归，使用性能预算。重复噪声测量或比较中位数/趋势，以便正常的运行间方差不会使门禁变得不稳定。
- **现场监控：** 在 RUM 数据中 p75 的有意义移动时发出警报。使用归因的 `web-vitals` 数据定位原因；将 CrUX 的滚动窗口视为确认而不是立即警报。

当任何一个门禁触发时，返回第 1 步并建立一个新的基线，然后再提出另一个修复。

**设置预算并执行：**

```
JavaScript 包：压缩后 < 200KB（初始加载）
CSS：压缩后 < 50KB
图像：折叠上方每个图像 < 200KB
字体：总计 < 100KB
API 响应时间：p95 < 200ms
交互时间：4G 上 < 3.5 秒
Lighthouse 性能分数：≥ 90
```

**在 CI 中执行：**
```bash
# 包大小检查
npx bundlesize --config bundlesize.config.json

# Lighthouse CI
npx lhci autorun
```

## 参见

有关详细的性能清单、优化命令和反模式参考，请参阅 `../../references/performance-checklist.md`。
