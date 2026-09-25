# Web 性能审计

您对 Web 性能指标、阈值和工具 API 的了解可能已经过时。在引用具体数字或建议时，**优先使用检索而非预训练**。

## 检索来源

| 来源 | 如何检索 | 用于 |
|------|--------|------|
| web.dev | `https://web.dev/articles/vitals` | 核心网络指标阈值、定义 |
| Chrome DevTools 文档 | `https://developer.chrome.com/docs/devtools/performance` | 工具 API、跟踪分析 |
| Lighthouse 评分 | `https://developer.chrome.com/docs/lighthouse/performance/performance-scoring` | 评分权重、指标阈值 |

## FIRST：验证 MCP 工具可用

在开始之前，发现可用的浏览器和性能工具。使用请求审计的可用功能。如果跟踪工具不可用，继续任何有用的来源或网络分析，并说明哪些测量值无法收集。

如果用户需要 Chrome DevTools MCP 设置，请参考其 [安装指南](https://github.com/ChromeDevTools/chrome-devtools-mcp#quick-start) 并使用最新软件包版本。仅在设置在用户的授权范围内时更改 MCP 配置；否则先询问。对于使用 `command` 和 `args` 的客户，一个示例服务器条目是：

```json
"chrome-devtools": {
  "command": "npx",
  "args": ["-y", "chrome-devtools-mcp@latest"]
}
```

## 关键指南

- **果断行事**：通过检查网络请求、DOM 或代码库来验证声明，然后明确陈述结果。
- **在建议前验证**：确认某项未使用后再建议移除。
- **量化影响**：使用洞察中的估算节省。不要优先考虑 0ms 影响的更改。
- **跳过非问题**：如果阻塞性资源估算影响为 0ms，请记录但不要建议采取行动。
- **具体说明**：说“压缩 hero.png (450KB) 到 WebP”而不是“优化图像”。
- **无情优先级排序**：一个 LCP 为 200ms 且 CLS 为 0 的网站已经非常优秀——请这样说。

## 快速参考

| 任务 | 工具调用 |
|------|--------|
| 加载页面 | `navigate_page(url: "...")` |
| 开始跟踪 | `performance_start_trace(autoStop: true, reload: true)` |
| 分析洞察 | `performance_analyze_insight(insightSetId: "...", insightName: "...")` |
| 列出请求 | `list_network_requests(resourceTypes: ["Script", "Stylesheet", ...])` |
| 请求详情 | `get_network_request(reqid: <id>)` |
| 无障碍快照 | `take_snapshot(verbose: true)` |

## 工作流程

将此检查清单复制到跟踪进度：

```
审计进度：
- [ ] 第一阶段：性能跟踪（导航 + 录制）
- [ ] 第二阶段：核心网络指标分析（包括 CLS 罪魁祸首）
- [ ] 第三阶段：网络分析
- [ ] 第四阶段：无障碍快照
- [ ] 第五阶段：代码库分析（如果是第三方网站则跳过）
```

### 第一阶段：性能跟踪

1. 导航到目标 URL：
   ```
   navigate_page(url: "<target-url>")
   ```

2. 使用重新加载开始性能跟踪以捕获冷加载指标：
   ```
   performance_start_trace(autoStop: true, reload: true)
   ```

3. 等待跟踪完成，然后检索结果。

**故障排除：**
- 如果跟踪返回空或失败，请先使用 `navigate_page` 验证页面是否正确加载
- 如果洞察名称不匹配，请检查跟踪响应以列出可用洞察

### 第二阶段：核心网络指标分析

使用 `performance_analyze_insight` 提取关键指标。

**注意：** 洞察名称在不同版本的 Chrome DevTools 中可能有所不同。如果某个洞察名称无效，请检查跟踪响应中的 `insightSetId` 以发现可用洞察。

常见的洞察名称：

| 指标 | 洞察名称 | 查找内容 |
|------|--------|--------|
| LCP | `LCPBreakdown` | 最大内容绘制时间；TTFB、资源加载、渲染延迟的分解 |
| CLS | `CLSCulprits` | 导致布局偏移的元素（无尺寸的图像、注入内容、字体交换） |
| 阻塞性渲染 | `RenderBlocking` | CSS/JS 阻碍首次绘制 |
| 文档延迟 | `DocumentLatency` | 服务器响应时间问题 |
| 网络依赖 | `NetworkRequestsDepGraph` | 延迟关键资源的请求链 |

示例：
```
performance_analyze_insight(insightSetId: "<id-from-trace>", insightName: "LCPBreakdown")
```

**关键阈值（良好/需要改进/差）：**
- TTFB：< 800ms / < 1.8s / > 1.8s
- FCP：< 1.8s / < 3s / > 3s
- LCP：< 2.5s / < 4s / > 4s
- INP：< 200ms / < 500ms / > 500ms
- TBT：< 200ms / < 600ms / > 600ms
- CLS：< 0.1 / < 0.25 / > 0.25
- 速度指数：< 3.4s / < 5.8s / > 5.8s

### 第三阶段：网络分析

列出所有网络请求以识别优化机会：
```
list_network_requests(resourceTypes: ["Script", "Stylesheet", "Document", "Font", "Image"])
```

**查找：**

1. **阻塞性资源**：`<head>` 中的 JS/CSS 没有 `async`/`defer`/`media` 属性
2. **网络链**：由于依赖其他资源先加载而晚发现的资源（例如 CSS 导入、JS 加载的字体）
3. **缺少预加载**：未预加载的关键资源（字体、英雄图像、关键脚本）
4. **缓存问题**：缺少或弱 `Cache-Control`、`ETag` 或 `Last-Modified` 标头
5. **大型有效负载**：未压缩或过大的 JS/CSS 打包
6. **未使用的预连接**：如果被标记，请通过检查是否有任何请求发送到该来源来验证。如果为零请求，则它确实未使用——建议移除。如果存在请求但加载较晚，预连接可能仍然有价值。

对于详细请求信息：
```
get_network_request(reqid: <id>)
```

### 第四阶段：无障碍快照

拍摄无障碍树快照：
```
take_snapshot(verbose: true)
```

**标记高级差距：**
- 缺少或重复的 ARIA ID
- 对比度差（根据 WCAG AA: 正常文本 4.5:1，大文本 3:1）
- 聚焦陷阱或缺少焦点指示器
- 无无障碍名称的交互元素

## 第五阶段：代码库分析

**如果审计的是没有代码库访问权限的第三方网站，则跳过。**

分析代码库以了解可以改进的地方。

### 检测框架 & 打包器

搜索配置文件以识别技术栈：

| 工具 | 配置文件 |
|------|--------|
| Webpack | `webpack.config.js`、`webpack.*.js` |
| Vite | `vite.config.js`、`vite.config.ts` |
| Rollup | `rollup.config.js`、`rollup.config.mjs` |
| esbuild | `esbuild.config.js`、使用 `esbuild` 的构建脚本 |
| Parcel | `.parcelrc`、`package.json`（parcel 字段） |
| Next.js | `next.config.js`、`next.config.mjs` |
| Nuxt | `nuxt.config.js`、`nuxt.config.ts` |
| SvelteKit | `svelte.config.js` |
| Astro | `astro.config.mjs` |

也检查 `package.json` 中的框架依赖和构建脚本。

### 树形摇动 & 代码死区

- **Webpack**：检查 `mode: 'production'`、`package.json` 中的 `sideEffects`、`usedExports` 优化
- **Vite/Rollup**：默认启用树形摇动；检查 `treeshake` 选项
- **查找**：条形文件（`index.js` 重新导出）、整体导入的大型工具库（lodash、moment）

### 未使用的 JS/CSS

- 检查 CSS-in-JS 与静态 CSS 提取
- 查找 PurgeCSS/UnCSS 配置（Tailwind 的 `content` 配置）
- 识别动态导入与立即加载

### 通用程序

- 检查 `@babel/preset-env` 目标和 `useBuiltIns` 设置
- 查找 `core-js` 导入（通常过大）
- 检查 `browserslist` 配置的过于宽泛的目标

### 压缩 & 最小化

- 检查 `terser`、`esbuild` 或 `swc` 最小化
- 查找构建输出或服务器配置中的 gzip/brotli 压缩
- 检查生产构建中的源映射（应为外部或禁用）

## 输出格式

以以下格式呈现结果：

1. **核心网络指标摘要** - 包含指标、值和评级（良好/需要改进/差）的表格
2. **主要问题** - 按优先级排序的问题列表，附带估算影响（高/中/低）
3. **建议** - 具体可执行修复，附带代码片段或配置更改
4. **代码库发现** - 检测到的框架/打包器，优化机会（如果没有代码库访问权限则省略）
