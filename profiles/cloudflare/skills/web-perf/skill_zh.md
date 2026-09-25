# Web 性能审计

您对 Web 性能指标、阈值和工具 API 的了解可能已过时。在引用具体数据或建议时，**优先采用检索而非预训练**。

## 检索来源

| 来源 | 检索方式 | 用途 |
|--------|----------------|---------|
| web.dev | `https://web.dev/articles/vitals` | Core Web Vitals 阈值与定义 |
| Chrome DevTools 文档 | `https://developer.chrome.com/docs/devtools/performance` | 工具 API、trace 分析 |
| Lighthouse 评分 | `https://developer.chrome.com/docs/lighthouse/performance/performance-scoring` | 评分权重、指标阈值 |

## 首先：验证 MCP 工具是否可用

在开始前，先了解可用的浏览器和性能工具。使用针对所要求审计提供的能力。如果 trace 工具不可用，继续进行任何有用的源或网络分析，并说明哪些测量数据无法收集。

如果用户需要配置 Chrome DevTools MCP，请参考其 [安装指南](https://github.com/ChromeDevTools/chrome-devtools-mcp#quick-start) 并使用最新的包版本。仅在设置属于用户授权范围时更改 MCP 配置；否则先询问用户。对于使用 `command` 和 `args` 的客户端，以下是一个服务器入口示例：

```json
"chrome-devtools": {
  "command": "npx",
  "args": ["-y", "chrome-devtools-mcp@latest"]
}
```

## 关键准则

- **立场坚定**：通过检查网络请求、DOM 或代码库来验证结论，然后明确地陈述发现。
- **推荐前先验证**：在建议移除某项功能前，先确认其确实未被使用。
- **量化影响**：使用洞察得出的预估节省效果。不要优先处理影响为 0ms 的更改。
- **跳过非问题**：如果渲染阻塞资源的预估影响为 0ms，予以记录但不建议采取行动。
- **具体明确**：说“将 hero.png（450KB）压缩为 WebP 格式”，而非“优化图片”。
- **坚决优先排序**：网站 LCP 为 200ms 且 CLS 为 0 时已经非常优秀——明确说明这一点。

## 快速参考

| 任务 | 工具调用 |
|------|-----------|
| 加载页面 | `navigate_page(url: "...")` |
| 开始 trace | `performance_start_trace(autoStop: true, reload: true)` |
| 分析洞察 | `performance_analyze_insight(insightSetId: "...", insightName: "...")` |
| 列出请求 | `list_network_requests(resourceTypes: ["Script", "Stylesheet", ...])` |
| 请求详情 | `get_network_request(reqid: <id>)` |
| 无障碍树快照 | `take_snapshot(verbose: true)` |

## 工作流

复制此清单以跟踪进度：

```
审计进度：
- [ ] 第一阶段：性能跟踪（导航 + 记录）
- [ ] 第二阶段：Core Web Vitals 分析（包含 CLS 原因）
- [ ] 第三阶段：网络分析
- [ ] 第四阶段：无障碍快照
- [ ] 第五阶段：代码库分析（若为无代码库访问权限的第三方网站则跳过）
```

### 第一阶段：性能跟踪

1. 导航到目标 URL：
   ```
   navigate_page(url: "<target-url")
   ```

2. 使用 reload 开始性能跟踪，以捕获冷加载指标：
   ```
   performance_start_trace(autoStop: true, reload: true)
   ```

3. 等待跟踪完成，然后获取结果。

**故障排除：**
- 如果跟踪返回为空或失败，先用 `navigate_page` 验证页面是否加载正确
- 如果洞察名称不匹配，检查跟踪响应以列出可用的洞察

### 第二阶段：Core Web Vitals 分析

使用 `performance_analyze_insight` 提取关键指标。

**注意：** 不同 Chrome DevTools 版本之间的洞察名称可能不同。如果洞察名称无法使用，请从跟踪响应中检查 `insightSetId` 以发现可用的洞察。

常用洞察名称：

| 指标 | 洞察名称 | 需要查看的内容 |
|--------|--------------|------------------|
| LCP | `LCPBreakdown` | 最大内容渲染完成所需时间；TTFB、资源加载、渲染延迟的分解 |
| CLS | `CLSCulprits` | 导致布局偏移的元素（无尺寸的图像、注入的内容、字体替换） |
| 渲染阻塞 | `RenderBlocking` | CSS/JS 阻塞首次渲染 |
| 文档延迟 | `DocumentLatency` | 服务器响应时间问题 |
| 网络依赖 | `NetworkRequestsDepGraph` | 延迟关键资源的请求链条 |

示例：
```
performance_analyze_insight(insightSetId: "<id-from-trace>", insightName: "LCPBreakdown")
```

**关键阈值（良好/需改进/较差）：**
- TTFB： < 800ms / < 1.8s / > 1.8s
- FCP： < 1.8s / < 3s / > 3s
- LCP： < 2.5s / < 4s / > 4s
- INP： < 200ms / < 500ms / > 500ms
- TBT： < 200ms / < 600ms / > 600ms
- CLS： < 0.1 / < 0.25 / > 0.25
- 速度指数： < 3.4s / < 5.8s / > 5.8s

### 第三阶段：网络分析

列出所有网络请求以识别优化机会：
```
list_network_requests(resourceTypes: ["Script", "Stylesheet", "Document", "Font", "Image"])
```

**需关注以下情况：**

1. **渲染阻塞资源**：`head` 标签中未设置 `async`/`defer`/`media` 属性的 JS/CSS
2. **网络链条**：因依赖其他资源先加载而发现较晚的资源（如 CSS 导入、JS 加载的字体）
3. **缺失预加载**：关键资源（字体、首屏图片、关键脚本）未进行预加载
4. **缓存问题**：缺失或较弱的 `Cache-Control`、`ETag` 或 `Last-Modified` 响应头
5. **大体积负载**：未压缩或体积过大的 JS/CSS 包
6. **未使用的预连接**：如被标记，需通过检查是否有任何请求发送到该源来验证。若无任何请求，则确认为未使用——建议移除。若有请求但加载较晚，预连接仍可能具有价值。

获取详细请求信息：
```
get_network_request(reqid: <id>)
```

### 第四阶段：无障碍树快照

获取无障碍树快照：
```
take_snapshot(verbose: true)
```

**标记高级缺失项：**
- 缺失或重复的 ARIA ID
- 对比度较差的元素（对照 WCAG AA 标准：常规文本需 4.5:1，大号文本需 3:1）
- 焦点陷阱或缺失的焦点指示器
- 缺乏无障碍名称的交互元素

## 第五阶段：代码库分析

**若因无法获取代码库权限而审计第三方网站，请跳过此阶段。**

分析代码库以了解可以在哪些方面进行改进。

### 检测框架与打包工具

搜索配置文件以识别技术栈：

| 工具 | 配置文件 |
|------|--------------|
| Webpack | `webpack.config.js`, `webpack.*.js` |
| Vite | `vite.config.js`, `vite.config.ts` |
| Rollup | `rollup.config.js`, `rollup.config.mjs` |
| esbuild | `esbuild.config.js`, 包含 `esbuild` 的构建脚本 |
| Parcel | `.parcelrc`, `package.json`（parcel 字段） |
| Next.js | `next.config.js`, `next.config.mjs` |
| Nuxt | `nuxt.config.js`, `nuxt.config.ts` |
| SvelteKit | `svelte.config.js` |
| Astro | `astro.config.mjs` |

此外，检查 `package.json` 中的框架依赖和构建脚本。

### Tree-Shaking 与死代码

- **Webpack**：检查是否设置了 `mode: 'production'`、`package.json` 中的 `sideEffects`，以及 `usedExports` 优化
- **Vite/Rollup**：默认启用 Tree-shaking；检查 `treeshake` 选项
- **查找**：桶文件（如 `index.js` 重新导出）、被整体导入的大型工具库（如 lodash、moment）

### 未使用的 JS/CSS

- 检查 CSS-in-JS 与静态 CSS 提取的对比
- 查找 PurgeCSS/UnCSS 配置（如 Tailwind 的 `content` 配置）
- 区分动态导入与 eager loading

### Polyfills（补全插件）

- 检查 `@babel/preset-env` 目标配置及 `useBuiltIns` 设置
- 查找 `core-js` 导入（通常体积过大）
- 检查 `browserslist` 配置是否存在过宽的目标范围

### 压缩与资源压缩

- 检查 `terser`、`esbuild` 或 `swc` 的压缩
- 检查构建输出或服务器配置中的 gzip/brotli 压缩
- 检查生产构建中的源码映射（应外置或禁用）

## 输出格式

按以下格式呈现发现：

1. **Core Web Vitals 总结** - 包含指标、数值和评级（良好/需改进/较差）的表格
2. **主要问题** - 按优先级排列的问题列表，附带预估影响（高/中/低）
3. **建议** - 具体、可操作的修复方案，附带代码片段或配置变更
4. **代码库发现** - 检测到的框架/打包工具及优化机会（若无代码库访问权限则省略）
