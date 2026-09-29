---
name: dt-obs-frontends
description: Dynatrace上的真实用户监控（RUM）——适用于网页和移动前端。核心网络指标、用户会话、页面性能、移动崩溃、前端错误以及前端与后端的关联。可通过`user.events`、`user.sessions`和`dt.frontend.*`指标进行查询。不包含合成监控（HTTP/浏览器/网络检查）——那是另一个领域。
---

# 前端可观察性 (RUM)

使用 DQL 通过真实用户监控 (RUM) 监控 Web 和移动前端。
目标为**最新版本的 Dynatrace 上的 RUM** — 不要使用 RUM Classic 数据。

**概念和数据模型：** https://docs.dynatrace.com/docs/observe/digital-experience/new-rum-experience/concepts

## 数据模型

三个数据源，每个源对应一个不同的问题：

| 源 | 用于 | 粒度 |
|----|------|------|
| `timeseries dt.frontend.*` | 趋势、仪表板、告警 | 汇总指标 |
| `fetch user.events` | 根本原因、单个页面视图/请求/点击/错误 | 每个事件 |
| `fetch user.sessions` | 跳出率、会话持续时间、会话级汇总 | 每个会话 |

**经验法则**：先从问题形态的指标开始，再深入事件了解原因。当问题涉及用户旅程而非单个交互时，使用会话。

完整事件模型：https://docs.dynatrace.com/docs/semantic-dictionary/model/rum/user-events

**DQL 语言参考（函数、语法、运算符）：** https://docs.dynatrace.com/docs/platform/grail/dynatrace-query-language

**关键的 `dt.frontend.*` 指标**（所有指标都支持维度：`frontend.name`、`device.type`、`geo.country.iso_code`、`browser.name`、`os.name`、`dt.rum.user_type`、`dt.smartscape.frontend`）：

- `dt.frontend.web.page.largest_contentful_paint` / `dt.frontend.web.page.interaction_to_next_paint` / `dt.frontend.web.page.cumulative_layout_shift` / `dt.frontend.web.page.first_input_delay` — 核心网络指标
- `dt.frontend.web.navigation.time_to_first_byte` / `dt.frontend.web.navigation.dom_interactive` / `dt.frontend.web.navigation.load_event_end` — 导航时间
- `dt.frontend.error.count` — 错误计数
- `dt.frontend.request.count` / `dt.frontend.request.duration` — 请求量和延迟
- `dt.frontend.user_action.count` / `dt.frontend.user_action.duration` — 用户操作量和持续时间
- `dt.frontend.session.active.estimated_count` / `dt.frontend.user.active.estimated_count` — 活跃会话和用户（基数指标；使用 `countDistinct()` 聚合）

## 常用过滤器

**所有源 (`user.events` + `user.sessions`)：**
- `frontend.name` — 前端标识符（所有过滤推荐使用）；在 `user.sessions` 上为数组（会话可能跨越多个前端）。`dt.smartscape.frontend` 是 Smartscape 实体引用 — 用于访问实体属性（如标签或关联服务），而不是基于名称进行过滤。避免查询 Smartscape 以将名称解析为实体 ID 并然后与 `user.events` 进行连接 — 直接在 `frontend.name` 上进行过滤。
- `dt.rum.user_type` — `real_user`、`synthetic`、`robot`
- `dt.rum.application.type` — `web` 或 `mobile`
- `dt.rum.session.id`、`dt.rum.instance.id`
- `os.name`、`geo.country.iso_code`、`client.isp`
- `client.ip` — 客户端 IP 地址 *(敏感字段 — 默认隐藏；见下方的字段权限)*

**`user.events` — 仅限 Web：**
- `browser.name`、`browser.version`、`device.type`

**`user.events` — 仅限移动端：**
- `device.model.identifier`、`device.manufacturer`、`app.short_version`

**常用特征过滤器**（将 `user.events` 限定为特定事件类型 — 使用 `| filter characteristics.has_X`）：
- `characteristics.has_page_summary` — 页面加载（Web）
- `characteristics.has_view_summary` — 查看页（SPA + 移动屏幕）
- `characteristics.has_navigation` — 导航事件
- `characteristics.has_user_action` — 用户操作
- `characteristics.has_error` — 所有错误

完整特征参考：[references/characteristics.md](references/characteristics.md)

## 字段权限

某些字段是**敏感字段**，属于 `builtin-sensitive-user-events-and-sessions` 字段集。它们在 `user.events` 和 `user.sessions` 上**默认隐藏** — 没有访问权限的用户看到的是 `null`，并且过滤或按这些字段进行分组查询将无声地返回无结果。

本技能中使用的敏感字段：

- `client.ip` — 客户端 IP 地址
- `user.identifier` — 真实用户身份

使用以下策略声明授予权限：

```
ALLOW storage:fieldsets:read WHERE storage:fieldset-name="builtin-sensitive-user-events-and-sessions"
```

参考：[字段权限](https://docs.dynatrace.com/docs/shortlink/rum-on-grail-permissions#field-permissions)

## 下钻模式

大多数调查无论具体问题领域（错误、性能、后台活动等）都遵循此分层方法：

**1. 确定受影响的前端**

首先通过 `by: {frontend.name}` 进行分组，以找到受影响的应用程序。如果需要从一开始就将 Web 和移动分析分开，请按 `dt.rum.application.type` (`web` 或 `mobile`) 进行过滤。

**2. 找到受影响的页面或视图**

两个字段在所有事件上都可用（不限于特定特征）：

- `page.name` — 页面 URL 归一化为 Dynatrace 实体名称；**仅限 Web**
- `view.name` — SPA 路由或移动屏幕名称；在 **Web 和移动端** 上可用

两个字段可以在同一事件中同时存在。对于 Web SPAs，`page.name` 反映顶级文档，而 `view.name` 反映当前路由 — 按 `view.name` 分组可以提供更细粒度的粒度。对于移动端，仅使用 `view.name`。

**附加缩小维度**

| 维度 | 字段 | 平台 | 使用场景 |
|------|------|------|----------|
| 特定请求/端点 | `url.domain`、`url.path` | Web + 移动 | 特定 API 调用的性能或错误模式 |
| 单个用户会话 | `dt.rum.session.id` | Web + 移动 | 复现特定用户的旅程；连接到会话重放 |
| 设备形态 | `device.type` | 仅限 Web | 桌面浏览器 vs 移动浏览器 vs 平板模式 |
| 浏览器兼容性 | `browser.name`、`browser.version` | 仅限 Web | 仅在某些浏览器上出现的问题 |
| 应用版本 | `app.short_version` | 仅限移动 | 特定应用版本中引入的回归 |
| 地理位置信息 | `geo.country.iso_code` | Web + 移动 | 区域基础设施或 CDN 问题 |
| 真实流量 vs 合成流量 | `dt.rum.user_type` | Web + 移动 | 在用户界面分析之前排除合成监控器 |

## 工作流

每个工作流对应一个或多个参考。启动工作流时加载参考，而不是预先加载。

| 工作流 | 参考 |
|------|------|
| 事件特征 — 类型、过滤器、事件_type 推导 | [references/characteristics.md](references/characteristics.md) |
| Web 核心指标 (LCP、FCP、FID、INP、CLS) | [references/web-vitals.md](references/web-vitals.md) |
| 会话、跳出率、参与度分析 | [references/user-sessions.md](references/user-sessions.md) |
| 用户操作 — 交互生命周期、完成原因、超时 | [references/user-actions.md](references/user-actions.md) |
| 错误、异常、失败请求 | [references/error-tracking.md](references/error-tracking.md) |
| 前端-后端链接 — 机制、跟踪覆盖率、`frontend.link` | [references/frontend-backend-linking.md](references/frontend-backend-linking.md) |
| CSP 违规 — 安全策略执行和被阻止的资源 | [references/csp-violations.md](references/csp-violations.md) |
| 移动应用启动、崩溃、ANR、原生信号 | [references/mobile-monitoring.md](references/mobile-monitoring.md) |
| 请求延迟、长任务、JS 分析、地理性能 | [references/web-performance-analysis.md](references/web-performance-analysis.md) |
| 可见性变化 — 标签切换、后台时间、参与度质量 | [references/visibility-changes.md](references/visibility-changes.md) |
| 慢速页面加载 — 后端 vs 渲染 vs 网络 vs JS 排查 | [references/slow-page-load-playbook.md](references/slow-page-load-playbook.md) |
| 诊断无结果、异常、模糊数据 | [references/troubleshooting.md](references/troubleshooting.md) |

## 性能阈值（快速参考）

- **LCP**：良好 < 2.5 秒 | 差 > 4.0 秒
- **INP**：良好 < 200 毫秒 | 差 > 500 毫秒
- **CLS**：良好 < 0.1 | 差 > 0.25
- **FCP**：良好 < 1.8 秒 | 差 > 3.0 秒
- **TTFB**：良好 < 800 毫秒 | 差 > 1800 毫秒
- **移动冷启动**：良好 < 3 秒 | 差 > 5 秒
- **移动热启动**：良好 < 1.5 秒 | 差 > 2 秒
- **移动热启动**：良好 < 500 毫秒 | 差 > 1 秒
- **长任务**：> 50 毫秒有问题，> 250 毫秒严重

*Web 核心指标 (LCP、INP、CLS、FCP、TTFB)：https://web.dev/articles/vitals*

## 使用场景

使用此技能进行真实用户 Web 和移动前端遥测 — 核心网络指标、会话、点击、错误、崩溃、浏览器/应用的请求延迟以及前端-后端链接。

使用其他技能：

- 合成监控器 / 可用性检查 → `dt-obs-synthetic`
- 后端服务、跟踪、片段 → `dt-obs-services`、`dt-obs-tracing`
- 基础设施、主机 → `dt-obs-hosts`
- 日志 → `dt-obs-logs`
- 问题与事件 → `dt-obs-problems`
