---
name: k6-perf-test-website
description: 当用户希望使用k6对公共网站进行端到端性能测试、负载测试或压力测试时使用。生成混合（协议+浏览器）测试套件、基于SLO的阈值、负载生成器监控sidecar，以及用于用户拥有的后端的Grafana侧调查剧本。在以下情况下触发："测试我的网站性能"、"性能测试我的网站"、"负载测试此URL"、"压力测试我的Web应用"、"我想负载测试[URL]"、"针对我的网站设置k6"、"为[站点]编写k6套件"、"我的网站能否处理N个并发用户"或"我的网站在流量下的表现如何"。每当用户提到k6、负载测试、压力测试、性能测试，或希望验证网站在流量下的表现时，无论他们是否明确使用"测试"一词或要求此技能产生的具体输出，都可以使用此技能。
---

# `k6-perf-test-website`

使用 k6 对任何公共网站进行端到端的性能测试的意见性工作流程。该技能生成：

- 每个用户描述的工作流程一个文件夹的脚手架项目。
- 功能性协议 + 浏览器测试（必须在负载测试之前通过）。
- 每种测试类型（冒烟 / 平均 / 压力 / 峰值 / 持久 / 关键点）的混合负载测试（协议场景 + 1 个浏览器 VU）。
- 基于 SLO 的阈值，每个端点标记和 Web Vitals。
- 跨平台负载生成器监控边车。
- 当用户拥有后端时，可选的 Grafana 端调查。
- 结束时一个结构化的 Markdown 报告。

此技能强制执行一些你不应该无声覆盖的意见：

- **始终首先获取工作流程。** 不要猜测。
- **功能性测试必须在负载测试运行之前是绿色的。**
- **始终监控负载生成器** — 服务器看起来慢通常是笔记本电脑看起来慢。
- **本地验证，云端扩展** — 但询问用户在哪里运行每种测试类型；不要硬编码。
- **没有共享的 `tests/lib/`。** 偏好迭代体重复；在事件审查期间，每个脚本都可以清晰地读取。

## 前置条件

- **k6 ≥ v2.0.0** (`k6 version`) — 需要 `k6/browser` 稳定、`expect()`、异步/等待迭代函数和每个请求的 `tags`。
- **Node.js ≥ 20** + npm。
- **Playwright** 带有 Chromium 下载 (`npx playwright install chromium`)。
- **`har-to-k6`** (`npm i -D har-to-k6`)。
- 负载生成器主机到目标站点的网络访问。

当安装时，此技能偏好的工具：

- `mcp-k6` — 脚本创建，Playwright→k6/browser 迁移，API 查找。优先于手写 k6 模板。
- `mcp-grafana` — 在 §9 后端调查期间会话内 Prometheus/Loki/Tempo/Pyroscope 查询。
- `gcx` — Grafana Cloud CLI，用于 Shell 友好的查询、数据源发现和 Grafana Cloud k6 云运行调度。
- `k6` 二进制文件 — 本地验证运行和断点查找。
- `k6 x docs` (xk6-docs) — 在编写或编辑脚本时查找 k6 API 表面，而无需 `mcp-k6`。

如果这些工具未配置，此技能将回退到纯 CLI 工具 (`k6`, `npx`, `curl`) 和手写脚本。此技能不拥有工具链设置；委托给用户的现有设置过程。

明确的非目标：

- 仅协议套件（不在此技能范围内）。
- 仅 API / 非浏览器应用程序。
- 移动原生测试。
- 超过查找和标记断点的容量规划。

## 工作流程概述

按顺序勾选这些。每个步骤下面都有一个部分。

1. 从用户中获取工作流程。[§1](#1-elicit-workflows)
2. 从 `assets/` 脚手架项目。[§2](#2-scaffold-the-project)
3. 使用 Playwright 记录每个工作流程。[§3](#3-record-each-workflow)
4. 构建功能性协议 + 浏览器测试；运行 `tests/run-all.sh` 直到变绿。[§4](#4-build-functional-tests)
5. 设计基于 SLO 的阈值和每个端点的标签。[§5](#5-design-slos-and-thresholds)
6. 构建混合负载测试，每种测试类型一个文件。[§6](#6-build-hybrid-load-tests)
7. 使用 LG 边车本地运行验证。[§7](#7-run-locally-with-lg-sidecar)
8. 推送到 Grafana Cloud k6，用于用户选择的云测试类型。[§8](#8-push-to-grafana-cloud-k6)
9. 使用 Grafana 调查后端（如果拥有）。[§9](#9-investigate-the-backend)
10. 向用户报告。[§10](#10-report-back)

## 1. 获取工作流程

**最关键的一步。** 没有明确的工作流程，后续每一步都是猜测。

询问用户 `references/workflow-elicitation.md` 中的问题，并将答案记录在脚手架项目旁边的 `runbook.md` 中。

您必须捕获：2-4 个命名工作流程、凭证、读 vs 写、在持久期间避免的破坏性行动、关注列表、现有的 SLO、后端所有权和 Grafana 访问，以及**每个测试类型**是否在本地或在 Grafana Cloud k6 中运行。

如果用户至少无法命名一个工作流程，**停止并澄清**；不要继续。

## 2. 脚手架项目

将此技能的 `assets/` 树从 `assets/` 复制到用户选择的目录。此技能的 `assets/` 目录位于 `<SKILL_DIR>/assets/`，其中 `<SKILL_DIR>` 是此技能目录的绝对路径——您的 harness 会暴露此路径（例如 opencode 会用 `Base directory for this skill:` 行为技能元数据前缀）。如果您无法从上下文中确定 `<SKILL_DIR>`，请询问用户。

```bash
cp -R "<SKILL_DIR>/assets/." "<target-dir>/"
```

如果 `cp -R` 因沙盒权限而被阻止，请通过您的代理的文件写入工具逐个复制文件。

脚手架布局：

```
<target-dir>/
├── package.json
├── .gitignore
├── README.md
├── runbook.md                       # 你从 §1 答案创建
├── recordings/
│   ├── README.md
│   └── scripts/
│       └── recorder.template.js     # 每个工作流程复制 → wN-<short-name>.js, …
├── tests/
│   ├── run-all.sh
│   └── workflow.template/           # 每个工作流程复制 → wN-<short-name>/, …
│       ├── from-har.js
│       ├── protocol.js
│       ├── browser.js
│       ├── smoke.js
│       ├── average.js
│       ├── stress.js
│       ├── spike.js
│       ├── soak.js
│       └── breakpoint.js
└── tools/
    ├── lg-monitor.sh
    └── run-with-monitor.sh
```

对于每个工作流程：复制 `recorder.template.js` → `recordings/scripts/wN-<short-name>.js`，复制 `tests/workflow.template/` → `tests/wN-<short-name>/`，并用工作流程的短名称替换 `<WORKFLOW_PLACEHOLDER>` 标记。

然后安装：

```bash
cd <target-dir> && npm install && npx playwright install chromium
```

## 3. 记录每个工作流程

每个工作流程：

1. 填写 `recordings/scripts/wN-<short-name>.js`：用户操作序列、`recordHar.urlFilter` regex（允许目标主机；阻止第三方 RUM/广告——见 `references/recording-with-playwright.md`）、以及一个真实的 Chrome `userAgent`（默认的 `HeadlessChrome` UA 在许多站点上触发机器人阻止）。
2. 运行：`node recordings/scripts/wN-<short-name>.js` → 写入 `recordings/har/wN-<short-name>.har`
3. 转换：`npx har-to-k6 recordings/har/wN-<short-name>.har -o tests/wN-<short-name>/from-har.js`
4. 提交 HAR 和 `from-har.js`（捆绑路径变化的审计跟踪）。

如果记录器失败或生成不可用的 HAR（机器人阻止、缺少 hydration、第三方噪音），请参阅 `references/gotchas.md` 的录制部分和 `references/recording-with-playwright.md`。

如果可用，请优先使用 `mcp-k6` 记录和迁移工具。

## 4. 构建功能性测试

每个工作流程：

1. 手动清理 `from-har.js` 到 `protocol.js` — 删除每个请求的 UA 头、重命名组、参数化 `BASE_URL`、替换会话令牌、删除 `sleep(1)`、在每个负载响应上添加 `expect()`。完整步骤见 `references/functional-tests.md`。
2. 使用 Playwright 记录器手动编写 `browser.js`，使用 `references/functional-tests.md` 中的 5 步程序。
3. 运行 `./tests/run-all.sh`。**在 §5 之前不要继续。**

如果可用，请优先使用 `mcp-k6` 迁移工具进行 Playwright→k6/browser 转换。

## 5. 设计 SLO 和阈值

调整 `assets/tests/workflow.template/` 中的意见性默认值以匹配用户在 §1 中声明的 SLO。四个层级：

1. **全局 SLO** — 总错误率 + 聚合延迟。
2. **每个端点阈值** — 每个协议请求标记，每个标记阈值。
3. **每个迭代阈值** — 工作流时间 + 迭代完成率。
4. **Web Vitals** — 仅 LCP/INP/CLS（无 FCP）。

默认全局：

```js
http_req_failed: ['rate<0.01'],
http_req_duration: ['p(95)<500'],
checks: ['rate>0.99'],
```

每个端点标记：

```js
http.get(`${BASE_URL}/api/things`, { tags: { name: 'GetThings' } });
'http_req_duration{name:GetThings}': ['p(95)<400', 'p(99)<800'],
```

Web Vitals：

```js
browser_web_vital_lcp: ['p(95)<2500'],
browser_web_vital_inp: ['p(95)<200'],
browser_web_vital_cls: ['p(95)<0.1'],
```

有关每个迭代调优、`performance.mark` 自定义 Trend 模式、`iteration_completed` Rate、断点失败中止阈值和放宽规则，请参阅 `references/slo-design.md`。

## 6. 构建混合负载测试

每个工作流程，每种测试类型一个文件。每个文件都有一个协议场景（驱动负载）和一个浏览器 VU（在负载下测量 Web Vitals）。断点是仅协议的——浏览器 VU 会给信号添加噪声。

| 类型       | 执行器             | 默认值                                 |
|------------|----------------------|------------------------------------------|
| smoke      | constant-vus         | 3 VUs × 1m                               |
| average    | ramping-vus          | 0→20→0 over 14m                          |
| stress     | ramping-vus          | 0→50→0 over 20m                          |
| spike      | ramping-vus          | 0→100→0 over 2m                          |
| soak       | ramping-vus          | 0→10→0 over 70m                          |
| breakpoint | ramping-arrival-rate | 5/s→500/s over 20m, abortOnFail          |

一旦看到冒烟结果，就为每个工作流程进行调优。有关理由，请参阅 `references/test-types.md`，有关为什么每个类型一个文件以及为什么文件之间重复是可以接受的，请参阅 `references/hybrid-load-design.md`。

## 7. 使用 LG 边车本地运行

```bash
./tools/run-with-monitor.sh tests/wN-<short-name>/smoke.js
```

在后台启动 `lg-monitor.sh`，运行 k6，然后打印总结性判断：**OK**（≥30% 空闲）、**NOTE**（10–30%）或 **WARNING**（<10%）。如果 WARNING，笔记本电脑是瓶颈——减少 VUs，切换到云端，或跨多个 LG 分割。有关详细信息，请参阅 `references/lg-monitoring.md`。

## 8. 推送到 Grafana Cloud k6

对于 §1 运行书中分配给云的每种测试类型：

1. 确认 `k6 cloud login` 工作（此技能不拥有身份验证设置）。
2. 首先在本地运行冒烟以验证脚本。
3. `k6 cloud run tests/wN-<short-name>/<type>.js`
4. 捕获运行 URL 以供 §10 报告。

**成本提醒：** 浏览器 VU 小时按协议 VU 小时的 10 倍计费。持久和断点是最昂贵的。在长时间运行之前检查限制。有关详细信息，请参阅 `references/local-vs-cloud.md`。

## 9. 调查后端

仅当用户拥有后端并具有 Grafana 访问权限时。

1. 通过 `mcp-grafana` 或 `gcx datasources list` 发现数据源。
2. 询问用户服务标签键——不要猜测。
3. 将 k6 运行窗口与 RED 指标、错误日志、跟踪和配置文件（Pyroscope——使用显式的 `from`/`to` 运行窗口）相关联。
4. 返回具体证据：时间戳、查询字符串、面板链接。

有关完整流程的详细信息，包括如何验证不存在后再报告，请参阅 `references/grafana-investigation.md`。

## 10. 返回报告

填写来自 `references/reporting.md` 的报告模板：

- **摘要** — 工作流程、测试类型、日期
- **SLO** — 每个阈值通过/失败
- **发现** — 每个发现一个段落，按严重性排序，并带有具体证据
- **证据** — k6 输出路径、LG monitor CSV、云运行 URL、Grafana 链接
- **建议的下一步**

始终要具体。"延迟高"不是一个发现。"GetPizza p(95) 在迭代 ~200 达到 1.4s；与推荐服务持续 100% CPU 相关，根据 Grafana 面板链接"才是。

---

## 参考资料索引

- [`references/workflow-elicitation.md`](references/workflow-elicitation.md) — §1 的逐字问题脚本。
- [`references/recording-with-playwright.md`](references/recording-with-playwright.md) — HAR 捕获、第三方过滤器 regex、hydration 信号。
- [`references/functional-tests.md`](references/functional-tests.md) — Playwright→k6/browser 转换的 5 步程序。
- [`references/hybrid-load-design.md`](references/hybrid-load-design.md) — 协议 + 1 浏览器 VU 的理由，文件之间重复的论证。
- [`references/slo-design.md`](references/slo-design.md) — 完整阈值理由、异步与同步指标捕获。
- [`references/test-types.md`](references/test-types.md) — 所有六种测试类型的定义和默认值。
- [`references/lg-monitoring.md`](references/lg-monitoring.md) — 为什么边车存在，如何读取其输出。
- [`references/local-vs-cloud.md`](references/local-vs-cloud.md) — 框架、成本模型、每种测试类型的权衡。
- [`references/grafana-investigation.md`](references/grafana-investigation.md) — 通用后端调查流程。
- [`references/gotchas.md`](references/gotchas.md) — 通用陷阱。
- [`references/reporting.md`](references/reporting.md) — 最终报告模板。
