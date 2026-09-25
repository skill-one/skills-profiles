# WP性能（仅后端）

## 使用场景

在以下情况下使用此技能：

- WordPress网站/页面/端点运行缓慢（前端TTFB、管理后台、REST API、WP-Cron）
- 需要性能分析计划和工具推荐（WP-CLI分析/诊断、Query Monitor、Xdebug/XHProf、APM）
- 正在优化数据库查询、自动加载选项、对象缓存、计划任务或远程HTTP调用

此技能假设代理无法使用浏览器UI。优先使用WP-CLI、日志和HTTP请求。

## 所需输入

- 环境和安全：开发/预发布/生产环境，任何限制（禁止写入、禁止插件安装）。
- 如何定位安装：
  - WP根目录 `--path=<路径>`
  - （多站点/站点定位） `--url=<URL>`
- 性能症状和范围：
  - 哪个URL/REST路由/管理界面
  - 发生时间（始终发生 vs 偶发；登录时 vs 未登录时）

## 操作步骤

### 0) 安全准则：先测量，避免高风险操作

1. 确认是否可以执行写入操作（插件安装、配置更改、缓存清除）。
2. 选择可复现的目标（URL或REST路由）并捕获基线：
   - 如果可能，使用`curl`捕获TTFB/时间
   - 如果可用，使用WP-CLI进行性能分析

阅读：
- `references/measurement.md`

### 1) 生成仅后端的性能报告（确定性）

运行：

- `node skills/wp-performance/scripts/perf_inspect.mjs --path=<路径> [--url=<URL>]`

此命令检测：

- WP-CLI可用性和核心版本
- 是否可用`wp doctor` / `wp profile`
- 自动加载选项大小（如果可能）
- 对象缓存插件是否存在

### 2) 快速见效：在深度分析前运行诊断

如果可以访问WP-CLI，优先使用：

- `wp doctor check`

它捕获常见的生产陷阱（自动加载膨胀、SAVEQUERIES/WP_DEBUG、插件数量、更新）。

阅读：
- `references/wp-cli-doctor.md`

### 3) 深度分析（无需浏览器）

推荐顺序：

1. `wp profile stage`查看时间消耗在哪里（启动/主查询/模板）
2. `wp profile hook`（可选带`--url=`）查找慢速钩子/回调
3. `wp profile eval`用于目标代码路径

阅读：
- `references/wp-cli-profile.md`

### 4) Query Monitor（仅后端使用）

Query Monitor通常需要UI驱动，但可以通过REST API响应头和`_envelope`响应进行无头使用：

- 认证（nonce或应用密码）。
- 请求REST响应并检查头（`x-qm-*`）和/或使用`?_envelope`时的`qm`属性。

阅读：
- `references/query-monitor-headless.md`

### 5) 按类别修复（选择主要瓶颈）

使用分析输出选择*一个*主要瓶颈类别：

- **数据库查询** → 减少查询次数、修复N+1模式、优化索引、避免昂贵的元数据查询。
  - `references/database.md`
- **自动加载选项** → 识别最大的自动加载选项并停止自动加载大型数据块。
  - `references/autoload-options.md`
- **对象缓存未命中** → 引入缓存或修复缓存键/组使用；在适当位置添加持久对象缓存。
  - `references/object-cache.md`
- **远程HTTP调用** → 添加超时、缓存、批量处理；避免每次请求都调用远程API。
  - `references/http-api.md`
- **计划任务** → 减少立即执行峰值、去重事件、将重任务移出请求路径。
  - `references/cron.md`

### 6) 验证（重复测量）

- 重新运行相同的`wp profile` / `wp doctor` / REST请求。
- 确认性能差异且行为未改变。
- 如果修复有风险，在可能的情况下通过功能标志或分阶段发布推送。

## WordPress 6.9性能改进

在分析时注意这些6.9变更：

**按需加载经典主题CSS：**
- 经典主题现在支持按需加载CSS（此前只有区块主题有此功能）。
- 通过仅加载页面实际使用的区块样式，CSS负载减少30-65%。
- 如果您正在分析经典主题，此功能应已生效。

**无渲染阻塞资源的区块主题：**
- 不定义自定义样式表的区块主题（如Twenty Twenty-Three/Four）现在可以零渲染阻塞CSS加载。
- 样式来自全局样式（theme.json）和独立的区块样式，全部内联。
- 这显著提升了LCP（最大内容绘制）。

**内联CSS限制提高：**
- 内联小型样式表的阈值已提高，减少了渲染阻塞资源。

参考：https://make.wordpress.org/core/2025/11/18/wordpress-6-9-frontend-performance-field-guide/

## 验证

- 捕获基线与修复后的数值（相同环境，相同URL/路由）。
- 当适用时，`wp doctor check`显示干净（或改善）。
- 日志中无新的PHP错误或警告。
- 正确性无需缓存清除（缓存清除应为最后手段）。

## 失败模式/调试

- 代码更改后“无变化”：
  - 您测量了不同的URL/站点（`--url`不匹配）、缓存掩盖了结果，或操作码缓存已过期
- 分析数据杂乱：
  - 消除后台任务，使用预热缓存测试，运行多个样本
- `SAVEQUERIES`/Query Monitor导致开销：
  - 除非明确批准，否则不要在生产环境中运行

## 升级

- 如果这是生产环境且您未获得明确批准，不要：
  - 安装插件、启用`SAVEQUERIES`、运行负载测试或清除缓存（在流量期间）
- 如果需要系统级分析（APM、PHP分析器扩展），请与运维/托管团队协调。
