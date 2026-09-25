# `k6-perf-test-website`

一个针对任何公共网站进行性能测试的端到端、有观点的工作流程。该技能产出：

- 每个用户描述的工作流程一个文件夹的脚手架项目。
- 功能协议 + 浏览器测试（必须在负载测试之前通过）。
- 每种测试类型（冒烟 / 平均 / 压力 / 峰值 / 持久 / 断点）的混合负载测试（协议场景 + 1 个浏览器 VU）。
- 基于SLO的阈值，每个端点标记和Web Vitals。
- 跨平台的负载生成器监控边车。
- 当用户拥有后端时，可选的Grafana侧边栏调查。
- 结束时一个结构化的Markdown报告。

这个技能强制执行一些你不应该无声覆盖的观点：

- **始终首先获取工作流程。** 不要猜测。
- **功能测试必须在负载测试运行之前是绿色的。**
- **始终监控负载生成器** — 服务器看起来慢通常是笔记本电脑看起来慢。
- **本地验证，云端扩展** — 但询问用户每种测试类型在哪里运行；不要硬编码。
- **没有共享的 `tests/lib/`。** 偏好迭代体重复；在事件审查期间，每个脚本都可以清晰地读取。

## 前置条件

- **k6 ≥ v2.0.0** (`k6 version`) — 用于稳定的 `k6/browser`、`expect()`、异步/等待迭代函数和每个请求的 `tags`。
- **Node.js ≥ 20** + npm。
- **Playwright** 带有Chromium下载 (`npx playwright install chromium`)。
- **`har-to-k6`** (`npm i -D har-to-k6`)。
- 负载生成器主机到目标站点的网络访问。

该技能在安装时偏好的工具：

- `mcp-k6` — 脚本创建，Playwright→k6/browser迁移，API查找。优先于手写k6样板。
- `mcp-grafana` — 在 §9 后端调查期间会话内的Prometheus/Loki/Tempo/Pyroscope查询。
- `gcx` — Grafana Cloud CLI，用于shell友好的查询、数据源发现和Grafana Cloud k6云运行调度。
- `k6` 二进制文件 — 本地验证运行和断点查找。
- `k6` x docs (xk6-docs) — 在编写或编辑脚本时查找k6 API表面，而无需 `mcp-k6`。

如果这些工具未配置，该技能会回退到普通的CLI工具 (`k6`、`npx`、`curl`) 和手写脚本。该技能不拥有工具链设置；委托给用户的现有设置过程。

明确的非目标：

- 仅协议套件（不在此技能范围内）。
- 仅API / 非浏览器应用程序。
- 移动原生测试。
- 超过查找和标记断点的容量规划。

## 工作流程概述

按顺序勾选这些。每一步下面都有一个部分。

1. 从用户中获取工作流程。[§1](#1-elicit-workflows)
2. 从 `assets/` 中脚手架项目。[§2](#2-scaffold-the-project)
3. 使用Playwright记录每个工作流程。[§3](#3-record-each-workflow)
4. 构建功能协议 + 浏览器测试；运行 `tests/run-all.sh` 直到变绿。[§4](#4-build-functional-tests)
5. 设计基于SLO的阈值和每个端点的标签。[§5](#5-design-slos-and-thresholds)
6. 构建混合负载测试，每个文件一个测试类型。[§6](#6-build-hybrid-load-tests)
7. 使用LG边车本地运行验证。[§7](#7-run-locally-with-lg-sidecar)
8. 推送到Grafana Cloud k6，用于用户选择的云测试类型。[§8](#8-push-to-grafana-cloud-k6)
9. 使用Grafana调查后端（如果拥有）。[§9](#9-investigate-the-backend)
10. 向用户报告。[§10](#10-report-back)

## 1. 获取工作流程

**最重要的一步。** 没有明确的工作流程，后续的每一步都是猜测。

询问用户 `references/workflow-elicitation.md` 中的问题，并将答案记录在脚手架项目旁边的 `runbook.md` 中。

你必须捕获：2-4 个命名的工作流程、凭证、读 vs 写、在持久期间要避免的破坏性行动、关注列表、现有的SLO、后端所有权和Grafana访问权限，以及**每个测试类型**是否在本地或在Grafana Cloud k6中运行。

如果用户无法命名至少一个工作流程，**停止并澄清**；不要继续。

## 2. 脚手架项目

将此技能的 `assets/` 树复制到用户选择的目录中。该技能的 `assets/` 目录位于 `<SKILL_DIR>/assets/`，其中 `<SKILL_DIR>` 是此技能目录的绝对路径 — 你的harness会暴露这个（例如，opencode会以 `Base directory for this skill:` 行为前缀技能元数据）。如果你无法从上下文中确定 `<SKILL_DIR>`，请询问用户。

```bash
cp -R "<SKILL_DIR>/assets/." "<target-dir>/"
```

如果 `cp -R` 被沙盒权限阻止，请通过你的代理的文件写入工具逐个复制文件。

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

1. 填写 `recordings/scripts/wN-<short-name>.js`：用户操作序列、`recordHar.urlFilter` regex（允许目标主机；阻止第三方RUM/广告 — 见 `references/recording-with-playwright.md`）、以及一个真实的Chrome `userAgent`（默认的 `HeadlessChrome` UA 在许多站点上触发机器人阻止）。
2. 运行：`node recordings/scripts/wN-<short-name>.js` → 写入 `recordings/har/wN-<short-name>.har`
3. 转换：`npx har-to-k6 recordings/har/wN-<short-name>.har -o tests/wN-<short-name>/from-har.js`
4. 提交HAR和 `from-har.js`（捆绑路径变化的审计跟踪）。

如果记录器失败或产生不可用的HAR（机器人阻止、缺少水合、第三方噪音），请参阅 `references/gotchas.md` 的录制部分和 `references/recording-with-playwright.md`。

如果可用，请优先使用 `mcp-k6` 记录和迁移工具。

## 4. 构建功能测试

每个工作流程：

1. 手动清理 `from-har.js` 到 `protocol.js` — 删除每个请求的UA头、重命名组、参数化 `BASE_URL`、替换会话令牌、删除 `sleep(1)`、在每个负载响应上添加 `expect()`。完整步骤见 `references/functional-tests.md`。
2. 使用Playwright记录器手动编写 `browser.js`，使用 `references/functional-tests.md` 中的 5 步程序。
3. 运行 `./tests/run-all.sh`。**在进入 §5 之前不要继续。**

如果可用，请优先使用 `mcp-k6` 迁移工具进行 Playwright→k6/browser转换。

## 5. 设计SLO和阈值

调整 `assets/tests/workflow.template/` 中的有观点的默认值到 §1 中用户声明的SLO。四个层次：

1. **全局SLO** — 总错误率 + 聚合延迟。
2. **每个端点的阈值** — 每个协议请求标记，每个标记阈值。
3. **每个迭代阈值** — 工作流时间 + 迭代完成率。
4. **Web Vitals** — 仅LCP/INP/CLS（无FCP）。

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

有关每个迭代调优、`performance.mark` 自定义Trend模式、`iteration_completed` Rate、断点失败中止阈值和放宽规则，请参阅 `references/slo-design.md`。

## 6. 构建混合负载测试

每个工作流程，每个测试类型一个文件。每个文件有一个协议场景（驱动负载）和一个浏览器VU（在负载下测量Web Vitals）。断点是仅协议的 — 浏览器VU会给信号添加噪音。

| 类型       | 执行器             | 默认值                                 |
|------------|----------------------|------------------------------------------|
| smoke      | constant-vus         | 3 VUs × 1m                               |
| average    | ramping-vus          | 0→20→0 over 14m                          |
| stress     | ramping-vus          | 0→50→0 over 20m                          |
| spike      | ramping-vus          | 0→100→0 over 2m                          |
| soak       | ramping-vus          | 0→10→0 over 70m                          |
| breakpoint | ramping-arrival-rate | 5/s→500/s over 20m, abortOnFail          |

一旦看到冒烟结果，就为每个工作流程进行调优。有关理由，请参阅 `references/test-types.md`，有关为什么每个类型一个文件以及为什么文件之间重复是可以接受的，请参阅 `references/hybrid-load-design.md`。

## 7. 使用LG边车本地运行

```bash
./tools/run-with-monitor.sh tests/wN-<short-name>/smoke.js
```

在后台启动 `lg-monitor.sh`，运行k6，然后打印总结性判断：**OK**（≥30%空闲）、**NOTE**（10–30%）或 **WARNING**（<10%）。如果WARNING，笔记本电脑是瓶颈 — 减少VUs，切换到云端，或跨多个LG分配。有关详细信息，请参阅 `references/lg-monitoring.md`。

## 8. 推送到Grafana Cloud k6

对于 §1 runbook中分配给云的每个测试类型：

1. 确认 `k6 cloud login` 工作正常（该技能不拥有身份验证设置）。
2. 首先在本地运行冒烟以验证脚本。
3. `k6 cloud run tests/wN-<short-name>/<type>.js`
4. 捕获运行URL以供 §10报告。

**成本提醒：** 浏览器VU小时按协议VU小时的10倍计费。持久和断点是最昂贵的。在长时间运行之前检查限制。有关详细信息，请参阅 `references/local-vs-cloud.md`。

## 9. 调查后端

只有当用户拥有后端并具有Grafana访问权限时。

1. 通过 `mcp-grafana` 或 `gcx datasources list` 发现数据源。
2. 询问用户服务标签键 — 不要猜测。
3. 将k6运行窗口与RED指标、错误日志、跟踪和配置文件（Pyroscope — 使用明确的 `from`/`to` 运行窗口）相关联。
4. 返回具体证据：时间戳、查询字符串、面板链接。

有关完整流程的详细信息，包括如何验证不存在再报告，请参阅 `references/grafana-investigation.md`。

## 10. 返回报告

填写来自 `references/reporting.md` 的报告模板：

- **摘要** — 工作流程、测试类型、日期
- **SLO** — 每个阈值通过/失败
- **发现** — 每个发现一个段落，按严重性排序，并带有具体证据
- **证据** — k6输出路径、LG监控CSV、云运行URL、Grafana链接
- **建议的下一步**

始终要具体。 "延迟高" 不是一个发现。 "GetPizza p(95) 在迭代 ~200 达到 1.4s；与推荐服务持续 100% CPU 相关，通过Grafana面板链接" 是。

---

## 参考资料索引

- [`references/workflow-elicitation.md`](references/workflow-elicitation.md) — §1 的逐字问题脚本。
- [`references/recording-with-playwright.md`](references/recording-with-playwright.md) — HAR捕获、第三方过滤器regex、水合信号。
- [`references/functional-tests.md`](references/functional-tests.md) — Playwright→k6/browser转换的5步程序。
- [`references/hybrid-load-design.md`](references/hybrid-load-design.md) — 协议 + 1 浏览器VU的合理性，文件之间重复的论证。
- [`references/slo-design.md`](references/slo-design.md) — 完整阈值合理性，异步与同步指标捕获。
- [`references/test-types.md`](references/test-types.md) — 所有六种测试类型的定义和默认值。
- [`references/lg-monitoring.md`](references/lg-monitoring.md) — 为什么存在边车，如何读取其输出。
- [`references/local-vs-cloud.md`](references/local-vs-cloud.md) — 框架、成本模型、每个测试类型的权衡。
- [`references/grafana-investigation.md`](references/grafana-investigation.md) — 通用后端调查流程。
- [`references/gotchas.md`](references/gotchas.md) — 通用陷阱。
- [`references/reporting.md`](references/reporting.md) — 最终报告模板。
