---
name: ux-audit
description: 以真实用户身份使用实时网络应用程序，以发现静态审查遗漏的可用性+行为性错误。在做出任何结论之前，必须提供交互证明（输入、点击、发送、观察）——未交互的扫描将终止并判定为“不完整”。扫描线程，测试每个元素，运行多面板压力矩阵、视觉优化扫描、组件完美检查清单、自动化无障碍性（axe-core）、实用性能预算（LCP/CLS/INP）、场景电池（11个场景）以及包含真实数据电池的压力配方。硬性门槛：控制台错误/警告=0，网络5xx=0，布局崩溃=0，axe严重/关键=0，性能预算绿色。审计审计的元检查拒绝仓促报告。每个发现都有复现步骤、证据路径和疑似代码位置。使用“ux audit”、“walkthrough”、“qa sweep”、“audit the app”、“dogfood this”、“check all pages”、“find what's broken”、“stress the UI”触发。
---

# 用户体验审计

以真实用户身份体验一个在线应用程序。审计是**以交互为先**的——输入、点击、发送、观看、截图。静态的DOM扫描无法得出结论。

## 审计结果

审计结果将严格限定为以下其中一种：

- **通过**——关键问题=0，高优先级问题=0，所有硬性门槛为绿色，交互清单完整。
- **有条件通过**——关键问题=0，高优先级问题=0，所有硬性门槛为绿色，但存在中/低优先级问题。
- **失败**——至少存在一个关键或高优先级问题，或硬性门槛为红色。
- **不完整**——交互清单缺少必要条目，某个阶段未执行，或触发审计的审计（manifest时间戳间隔<0.5秒，截图少于2个路由，控制台读取少于1个路由，详尽审计的Phase 3耗时少于1分钟）。即使所有观察到的内容看起来都很好，也不允许升级为通过。

如果工作不包括完整的交互清单，唯一的合法结论是**不完整**。"看起来OK"不是通过。具有不合理的时序的干净通过会被拒绝——代理必须使用真实交互重新进行审计。

## 硬性门槛

这些会自动导致审计失败，且不可降级。

| 门槛 | 阈值 | 违反时的严重性 |
|------|------|----------------|
| 走廊期间控制台错误 | > 0 | 关键 |
| 走廊期间控制台警告 | > 0 | 高 |
| 网络请求5xx | > 0 | 关键 |
| 认证页面上的网络403 / 404 | > 0 | 高 |
| 在任何测试的视口/面板组合中布局崩溃 | > 0 | 高 |
| 任何审计页面上的axe-core关键违规 | > 0 | 关键 |
| 任何审计页面上的axe-core严重违规 | > 0 | 高 |
| 代表性路由上的LCP（实用预算） | > 4.0s | 高 |
| 代表性路由上的CLS | > 0.25 | 高 |
| 代表性路由上的INP | > 500ms | 高 |
| 缺少必要的交互清单条目 | n/a | 不完整 |
| 清单条目之间的中位数间隔<0.5s | n/a | 不完整（实际上未交互） |

控制台警告至少是高优先级*。5xx自动是关键*。不存在"中优先级控制台错误"——这个类别在此技能中不存在。

axe-core阈值是**按页面运行**（任何单个页面上>1个违规即失败）。性能阈值是**在代表性路由上运行一次**（按页面运行是过度）；实用预算远高于损坏，远低于CWV-严格。完整阈值+理由在[references/performance-budget.md](references/performance-budget.md)。完整的无障碍连接+严重性映射在[references/a11y-automation.md](references/a11y-automation.md)。

### 已知噪声的允许列表

某些应用程序具有已知的噪声控制台/网络类别，这些不是错误（Sentry信息日志、浏览器扩展器闲聊、认证检查探测中的预期401）。在Phase 3之前阅读审计配置文件并应用其允许列表。路径回退：`.jez/audit-config.yml` → `audit-config.yml` → `.audit/config.yml`。允许列表中的条目会保留在交互清单中，但会从发现结果中抑制。结论块显示原始和允许列表：`控制台警告：3（1个允许列表，2个可报告）`。

没有配置：每个控制台错误/警告都是一个发现。格式、语义、表面覆盖在[references/audit-config.md](references/audit-config.md)。

## 阶段（按顺序）

1. **预飞行**——角色锁定、浏览器工具、URL、视口、能力测试
2. **发现**——站点地图、线程清单、元素清单
3. **体验**——交互清单、线程、元素穷举、多面板压力测试、新用户视角、实时交互冒烟测试
4. **润色**——视觉润色扫描、组件完美性清单
5. **压力测试**——场景电池（11个场景）+扩展压力配方
6. **结论**——结论状态、硬性门槛计分卡、完美性路线图、可复现的发现
7. **修复和验证**——修复发现、重新体验受影响的切片、更新报告

对于30秒的预部署检查，使用本文件底部的dogfood drill——这是项目级规则，不是技能调用。

## 阶段1——预飞行

五个门槛。如果任何一个失败，则停止。

### 1. 角色锁定

在执行任何操作之前，审计需要一个角色。如果没有锁定的角色，发现结果会偏向于泛泛的"看起来OK"。

按顺序源角色：

1. **参数**——如果用户提供了一个（"作为忙碌的保险经纪人进行用户体验审计"）
2. **项目角色**——读取现有的角色文件（回退链：`.jez/audit-personas/<slug>.md` → `docs/personas/<slug>.md` → `personas/<slug>.md` → `.audit/personas/<slug>.md`）。第一个匹配的获胜。
3. **问一次**——*"谁使用这个应用程序以及他们试图完成什么任务？"**

捕获：角色、技术舒适度、时间压力、情绪状态、设备上下文。一个好的角色可以预测他们会遗漏什么（"电话会议中的接待员不会滚动到折叠区域以下"）。

通过在审计报告的顶部写入所选角色来锁定角色。每个发现都必须从这个角色的角度进行辩护。如果你发现自己想着*"一个开发人员会知道..."*——停止。你的角色不是。

**始终运行第一次用户视角**（强制，见Phase 3）在每個多頁面功能上，即使显式角色是其他角色。这是AI/内部工具的最大盲点。

见[references/persona-lock.md](references/persona-lock.md)了解角色库和编写协议。

### 2. 浏览器工具

| 目标 | 工具 | 原因 |
|------|------|-----|
| **认证应用程序** | Chrome MCP | 使用你的真实登录Chrome会话——OAuth、cookies、RBAC正常工作 |
| **公共网站** | Playwright MCP | 不需要登录 |
| **两者都不可用** | **停止** | 要求用户连接Chrome MCP或安装Playwright |

不要默默地回退到新的Playwright会话用于认证应用程序——如果你无法登录，审计是无用的。如果Chrome MCP未连接，停止并说：*"打开Chrome，在Claude扩展中点击连接，然后重新运行。"**

见[references/browser-tools.md](references/browser-tools.md)了解命令。

### 3. URL

优先使用部署/在线版本——真实认证、真实延迟、真实CDN和CORS。发现：读取项目CLAUDE.md / README中的"URL"→检查堆栈配置（`wrangler.jsonc`、`vite.config.ts`、`next.config.js`、`config/database.yml`、`manage.py`、`.env` `APP_URL`、`wp-config.php`）→ `lsof -i :PORT`（常见：5173 Vite、3000 Next/Rails、8000 Django/Laravel、8787 Wrangler、4321 Astro）→询问。特定堆栈指南在[references/project-adaptation.md](references/project-adaptation.md)。如果用户要求或功能未部署，仅使用本地。

### 4. 视口

将窗口固定在1440×900开始。Phase 3多面板压力测试375 / 768 / 1024 / 1280 / 1440 / 1920。**不要超过2000px**——它会破坏harness。

### 5. 能力测试

在任何体验之前，证明工具可以工作——每个调用一个：

- 一个截图
- 一个控制台读取
- 一个网络请求清单
- 一个元素选择器查询

如果任何失败，停止并修复连接，然后再开始审计。对控制台输出视而不见的审计是无用的。

## 阶段2——发现

### 站点地图爬取

在审计任何页面之前，构建完整的页面清单。

1. **路由配置**——读取应用程序的路由定义（React Router、TanStack Router、Next.js应用目录）
2. **导航爬取**——点击侧边栏/菜单的每个部分和子部分
3. **深度链接**——CLAUDE.md、文档或先前审计报告中的URL

每行一个路由，带有目的：`/app/clients — 客户列表、搜索、添加新客户`。

### 线程清单

确定构成用户一天中3-5个真实任务。这些是审计的骨干。

如何找到它们：询问用户、读取CLAUDE.md / README、从顶级导航推断。示例：保险经纪人→续保保单、创建客户、处理今天的队列。项目管理→早晨分类、更新任务、发送客户摘要。空间/聊天应用程序→创建空间、发送消息、打开线程。

### 元素清单

对于每个到达的路线，列出每个交互元素。懒惰地构建清单——按页面遍历时逐页，而不是事先全部构建。这驱动了覆盖指标：*"在/app/clients上测试了29个中的31个元素"*。

## 阶段3——体验（审计本身）

### 交互清单（强制）

每个体验都会产生一个清单。没有清单，结论=不完整。

```
交互清单——/dashboard/spaces/marketing-pod
  角色：中小企业所有者，时间紧迫，低技术舒适度
  [✓] 14:32:01 在消息输入（textarea[placeholder*="message"]）中键入"@assistant test"
  [✓] 14:32:03 从自动完成中选择了@assistant（li[data-mention-id="assistant"]）
  [✓] 14:32:05 点击了发送（button[aria-label="发送"]）
  [✓] 14:32:06 验证输入在1000ms内清除（textarea.value === ""）
  [✓] 14:32:08 验证消息出现在记录中（[data-message-id]计数+1）
  [✓] 14:32:12 打开了消息上的线程（[data-thread-trigger]）
  [✓] 14:32:13 验证主列宽度在打开线程后≥200px（getBoundingClientRect().width）
  [✓] 每个步骤后读取控制台（0警告，0错误）
  [✓] 每个步骤前后截图
  [✓] 清单网络请求（0 5xx，0认证页面上的403/404）
```

每个复选框都需要一个工具调用（点击、截图、控制台读取），并记录时间戳+选择器。代理不能在没有完整清单的情况下生成"通过"报告。

**每个审计页面所需的条目**：

- ≥ 1输入键入（真实文本，不仅仅是点击）
- ≥ 1主要操作触发（发送/保存/提交/创建/发布——哪个适合）
- ≥ 1模态或详细信息面板打开
- ≥ 1主要操作后读取控制台
- ≥ 1主要操作前后的截图
- 验证预期的后操作状态（输入清除、成功提示、路由更改、列表更新）

完整模板+重播协议在[references/interaction-manifest.md](references/interaction-manifest.md)。

### 线程遍历

对于每个线程：

1. **从应用程序入口点开始**——不是线程中。真实用户会到达`/`或`/dashboard`。
2. **以角色身份体验**——如果他们会浏览，就浏览。如果他们会误解标签，就误解它。注意犹豫。
3. **截图每个状态变化**——默认→悬停/焦点→活动→点击后→加载后→确认。胶片是证据。
4. **跟踪成本**——点击次数、决策点、死胡同、中断恢复（在步骤3关闭标签，在步骤4返回——状态是否存活？）
5. **在每次线程结束时，将截图交给子代理进行审查**。

在每次线程结束时，以角色身份回答：*它是否结束得很清楚？我会再来吗？有什么能让这个变得容易两倍？*

见[references/walkthrough-checklist.md](references/walkthrough-checklist.md)和[references/workflow-comprehension.md](references/workflow-comprehension.md)。

### 元素穷举

对于每个路线，工作清单。跳过线程遍历已经锻炼的元素。详情见[references/walkthrough-checklist.md](references/walkthrough-checklist.md)。

对于**每个列表/表格**，如果数据允许，测试0/1/100/1000+的容量。

### 多面板压力测试（具有可折叠UI的应用程序的强制）

面板组合隐藏了最差的布局错误——2026-04-29垂直文本在空间中的错误仅在1024-1280px所有三个面板打开时显示。对于具有侧边栏/成员/线程/抽屉/表单的应用程序，运行矩阵：1920 / 1440 / **1280（高错误）** / **1024（灾难性错误）** / 768 / 375 × 全开、2面板、1面板、默认。对于每个组合：滚动最长的内容，捕获截图，运行布局检测JS以检测溢出/剪切/垂直文本堆栈。完整矩阵+JS片段+自动化在[references/multi-pane-stress.md](references/multi-pane-stress.md)。

### 新用户视角（强制）

除了锁定的角色之外，每个多页功能都必须通过**新用户**检查。这捕获了内部/AI工具中最大的UX失败模式：由设计它们的人构建的功能对它们自己有效，但首次到达同一屏幕的新用户不知道任何控件的意思。

采用*首次登录此应用程序的新用户的角色，没有任何先验背景，没有源访问，没有内部文档*。对于每个屏幕询问：

| 问题 | 它捕获什么 |
|---|---|
| 我能不阅读代码或文档就能完成任务吗？ | 将隐藏的技术知识融入表单 |
| 字段标签是平实的语言，而不是内部词汇？ | `agentClass`、`slug`、`webhook_id`泄漏到UI |
| 下拉列表/选择器显示**每个选项做什么**，而不仅仅是ID？ | Snake_case枚举、原始类名、不透明的slugs |
| 默认值是否足够合理，可以保留并继续？ | 必填字段没有默认值，强制ID输入 |
| 当需要输入时，是否存在可发现的值列表？ | 应该是组合框的自由文本输入 |
| 如果我会说"点击跳过"因为我不知道设置，那就是一个UX错误。 | 可选但令人困惑的设置作为主要输入暴露 |

当镜头触发时，即使屏幕在技术上可以工作，也要记录一个发现。常见修复：用选择器替换文本输入，暴露元数据，自动派生值，将内部ID隐藏在"高级"下，添加内联指导。

当屏幕通过镜头时，一个全新的角色可以在没有后端帮助的情况下完成任务。

### 实时交互冒烟测试

代码读取验证按钮存在且具有`onClick`。它不会验证点击实际上做了可观察的事情。对于每个页面上的每个交互控件：

1. **点击它。**指针移动，元素高亮，点击落地。
2. **观察网络标签。**是否发出请求？到正确的URL？正确的方法+正文？
3. **观察DOM。**是否发生了可见变化——新元素，移除元素，状态转换？
4. **如果（2）或（3）中没有变化，那就是一个错误。**

已知静默失败控件（工具调用卡片上的Approve/Deny、对话框中的OAuth阻止、异步验证表单、乐观UI删除、偏移量分页、具有陈旧TanStack Query的过滤芯片、没有Message-ID的回复/转发）：见[references/live-interaction-smoke.md](references/live-interaction-smoke.md)了解完整的静默失败目录和SDK合同检查（`@ai-sdk/react`、better-auth、TanStack Query、React Router v7、Radix Dialog、zodResolver）。

### 往返工作流完整性（强制）

由电池中的场景10（Phase 5）覆盖。作为Phase 3体验的一部分运行它——在遍历线程时遇到的每个A→B→A流程在继续之前都会进行往返检查。完整协议在[references/round-trip-workflows.md](references/round-trip-workflows.md)。

### 响应式扫描

每个宽度上的布局检测JS（溢出、剪切、不可见文本）。捕获过渡点。与上述多面板压力测试结合，以实现全面覆盖。

### 认证在审计中途过期

如果导航或API调用在先前认证的路线返回401/403，则会话丢失。**不要默默地重新认证**——每个后续观察都会被污染。停止，捕获破坏步骤（静默过期本身就是一个发现），以结论`不完整`终止，建议重新认证+重启。完整协议+发现标准在[references/auth-expired-handling.md](references/auth-expired-handling.md)。

## 阶段4——润色

### 视觉润色扫描

逐页进行微润色，涵盖十个AI指示类别：光学中心、嵌套边框半径规则、非标间距、灰色氛围、边框权重漂移、阴影方向、动画时序偏离规范、悬停增量校准、下划线/大写字母间距、对称性vs编辑节奏。

另外，对按钮、徽章、输入、下拉列表、卡片、选项卡、头像、提示进行每个组件的光学扫描。

完整协议与DevTools工作流、严重性指南和校准参考应用程序在[references/visual-polish.md](references/visual-polish.md)。

### 组件完美性清单

组件级别的粒度，页面级别的审核所遗漏的。六种类别，每种都有具体的“是/否”检查，需要证明性工件：

1. **按钮 & 触发器** — 状态清晰度、意图匹配、微文案、加载状态、层级
2. **输入 & 表单** — 持久性标签、掩码、内联验证、错误清晰度、默认值
3. **导航 & 层级** — 我在哪里？、点击深度、搜索逻辑、粘性页眉
4. **视觉一致性** — 图标一致性、空状态、边框半径、对比度
5. **移动 & 触摸** — 可点击区域（≥ 48×48）、键盘优化、滑动手势
6. **性能 & 反馈** — 骨架屏、成功提示、仅高风险确认模态

此外，每个主要组件有六个视觉状态（默认、骨架、空、部分、错误、禁用）——空状态下的骨架不是骨架。

报告中的每个复选框都引用一个证明性工件（截图、控制台行、DOM选择器、代码引用）。无证明 = 不计入。

完整清单在 [references/perfection-checklist.md](references/perfection-checklist.md)。

### 自动化可访问性 (axe-core, 强制性)

手动键盘仅步行（场景5）捕获焦点陷阱和Tab顺序。它们遗漏了约80%的结构性a11y错误（标题跳过、悬停/焦点对比度失败、缺失的aria-label、角色不匹配）。axe-core在每页不到1秒内覆盖了那80%。

对于每个审核页面：

1. 通过CDN注入axe-core（一个脚本标签）。
2. 页面稳定后运行 `axe.run()`。
3. 将违规项映射到审核发现（axe `critical` → 审核Critical，axe `serious` → 审核高，等等）。
4. 硬性门槛：任何页面 > 0 axe Critical 或 > 0 axe Serious = 审核失败。

一个16路由审核的总运行时间约为16秒。通过项目的audit-config（[references/audit-config.md](references/audit-config.md)中的路径回退链）允许列表用于builder模式的参考页面（组件、样式指南）。完整片段、严重性映射和发现格式在 [references/a11y-automation.md](references/a11y-automation.md)。

### 性能预算 (实用主义, 强制性)

在一个代表性路由（真实用户最常访问的页面——通常是仪表板或主要工作表面）上运行一次性能API捕获。实用主义阈值（LCP < 4.0s, CLS < 0.25, INP < 500ms）很好地高于故障并低于Google的CWV“良好”级别。CWV-严格用于着陆页和营销团队；对于真实用户实际停留的应用内部，实用主义是正确的标准。

添加到结论块。硬性门槛：任何阈值违规。使用Chrome DevTools Performance跟踪诊断（大型英雄图、晚加载字体、重点击处理器、hydration成本）。完整测量片段、节流规范和常见违规项在 [references/performance-budget.md](references/performance-budget.md)。

## 第5阶段 — 压力

### 场景电池 (11个场景)

全部11个，始终。它们捕获了逐屏测试遗漏的内容。完整协议在 [references/scenario-tests.md](references/scenario-tests.md)。

1. **首次接触** — 在零先验知识的情况下弄清楚应用，为每个线程编写一个2分钟的纯英文指南。
2. **中断的工作流** — 开始一个任务，关闭标签页，刷新，中途离开表单。状态是否存活？
3. **错误转弯恢复** — 故意点击错误。恢复需要多少次点击？
4. **返回用户** — 重复一个线程。更快？快捷方式？你能看出自上次访问以来有什么变化吗？
5. **仅键盘** — 每个线程仅键盘。焦点可见，Tab顺序逻辑，Escape关闭。
6. **大量数据** — 种子500+条记录。列表虚拟化，搜索返回正确结果，过滤器缩小。
7. **破坏性信心** — 每个删除/发送/发布/支付/分享：同意清晰，复制具体，可撤销。
8. **第二个用户（角色）** — 限制角色（查看者不是编辑者，客户不是员工）。只读视图，权限错误。
9. **生命周期位置** — 同一角色在用户 #1（创始人），#2（第一个邀请者，部分状态），#N（后期加入者，填充的工作空间）。每个看到不同的现实。
10. **往返工作流完整性** — 每个A→B→A流程：在B上完整变异，返回时A反映新状态而无需重新加载。可发现的回退功能。页眉徽章更新。最大的“项目回去时就是空的”来源。
11. **数据季节化** — 第0天/1天/7天/30天种子时间范围。时间形状的数据捕获了数量种子遗漏的内容：时间分隔符、最新排序、cron触发的副作用、通知徽章溢出、带历史的搜索性能、图表分桶。如果不存在时间分布数据，则跳过。

### 扩展压力配方

除了场景，运行[references/stress-test-recipes.md](references/stress-test-recipes.md)中的每个相关配方：

| 压力 | 捕获的内容 |
|------|------------|
| 空 / 饱和 / 长内容 | 边缘布局AI在开发期间很少看到 |
| 竞态条件（双击、快速输入后失去焦点、慢网络） | 乐观UI错误，防抖失败 |
| 慢网络（3G节流） | 加载状态，骨架节奏，超时UX |
| 减少运动（`prefers-reduced-motion: reduce`） | 忽略偏好的动画 |
| i18n（长德语、RTL阿拉伯语、CJK宽度） | 关于文本长度的布局假设 |
| 离线模式 | 重试/排队/脏状态UX |
| 打印样式表 | 遗忘的媒体查询 |
| 高对比度模式 | 强制颜色媒体查询处理 |
| **真实风味数据电池**（任何接受表单的应用的强制性） | 静默删除字符的验证（撇号、重音、RTL）；长度截断而不警告；未转义的SQL/XSS示警器；无法适应的文件上传（.heic，8000×8000 PNG，50MB PDF）。AI构建的UI通常非常干净的开发数据。 |

## 第6阶段 — 结论

### 结论块（报告顶部强制性）

```
═══════════════════════════════════════════════════════════
结论：[通过 / 条件通过 / 失败 / 不完整]

角色：[锁定角色slug]
审核的表面：N / M路由
交互清单：完整 / 不完整（X of Y必需条目）

硬性门槛：控制台错误 [N]，警告 [N]，网络5xx [N]，403/404认证 [N]，布局折叠 [N]，axe Critical [N]，axe Serious [N]   （所有必须为0；允许列表计数显示在括号中）
性能（在/[路由]）：LCP [N]s / CLS [N] / INP [N]ms — 阈值 4.0s / 0.25 / 500ms

发现：
  严重：[计数]    高：[计数]    中：[计数]    低：[计数]

自我批评通过（子代理）：草稿：[N]  保留：[N]  通用：[N]  重复：[N]

每个阶段的时间：阶段3 [N]m / 总计 [N]m   （阶段3 ≥ 5m为彻底）
清单可信度：[N]条目（≥ 6/route），中位数差距 [N]s（< 0.5s = 不完整），[N]截图（≥ 2/route）

前5名（按影响×易用性，高级设计师选择）：
  1-5. [F-id] 标题 — 一句话解释为什么它排在其他前面
═══════════════════════════════════════════════════════════
```

前5名，自我批评通过，以及“握在手中的结束语段落”（在阶段7之后）是强制性的。没有它们，结论是 `不完整`。完整纪律+格式+反模式在 [references/audit-output-discipline.md](references/audit-output-discipline.md)。

### 自我批评通过（发布前强制性）

在发现草稿之后，派遣一个全新的子代理，并附带草稿列表和这个提示：

> *"阅读这些审核发现。对于每个发现，标记保留 / 通用 / 重复。保留 = 仅此应用、此角色、此表面特定。通用 = 适用于任何Web应用。重复 = 与其他发现具有相同根本原因。在发布前删除通用和重复。"*

一个全新的子代理起作用，因为原始起草者对其自己的输出有投入。上下文中的自我批评倾向于辩护而不是修剪。记录通过情况：`草稿：23  保留：14  通用：5  重复：4`。

### 审核审核触发器（不容协商，自动切换到不完整）

| 信号 | 暗示 |
|---|---|
| 阶段3耗时 < 1m / 清单首→尾跨度 < 5m（彻底） | 步行被跳过或仓促 |
| 清单条目之间的中位数差距 < 0.5s | 条目批量发射，没有实际交互 |
| 截图少于2 × 路由 / 控制台读取少于1 × 路由 | 页面实际上没有被检查 |
| 前五名缺失或用填充槽位填充 | 纪律被破坏（见 [audit-output-discipline.md](references/audit-output-discipline.md)） |
| 自我批评通过未记录 | 填充未被修剪 |
| 发现使用“建议修复” / “考虑X” / “改进Y” | 填充形状的补丁，不可提交 |
| `[✓]` 通过行缺少一句话证明 + 工件 | 氛围通过 |
| 缺少“握在手中的结束语段落” | 未应用整体判断 |

### 发现格式（每个发现强制性）

每个发现必须包括：**ID**（严重性字母+数字）、**层级**（架构 / 交互 / 视觉 / 反馈 / 乐趣）、**严重性**、**表面**（路由+视口+窗格）、**角色**、**可复现**（编号步骤）、**观察**、**预期**、**证据**（截图路径+控制台/网络捕获）、**疑似位置**（`文件:行`）、**最小可能的补丁**（具体+可提交——*不是*“建议修复” / “考虑X”）。没有可复现+证据+疑似位置的发现将被拒绝。填充补丁（“改进X”、“考虑Y”、“改进Z”）将被自我批评通过切换为不完整。工作示例+五层层次结构在 [references/report-template.md](references/report-template.md) 和 [references/perfection-checklist.md](references/perfection-checklist.md)。纪律规则在 [references/audit-output-discipline.md](references/audit-output-discipline.md)。

### 握在手中（强制性结束语段落）

每个审核都以一个段落结束，没有模板，它回答：*如果这个应用是一个物理对象，我会想握住它吗？* 这是唯一一个氛围是*重点*的地方——清单表面无法体现的整体判断。格式+工作示例在 [references/audit-output-discipline.md](references/audit-output-discipline.md)。

### 完美路线图（强制性）

将发现分组为：

- **快速胜利（24-48小时）** — 微文案、悬停状态、对比度修复、单行CSS调整
- **结构（1-2周）** — 基本替换、路由重构、多窗格重构
- **高级抛光（发布后）** — 微动画、骨架变化、个性化空状态

完整报告结构在 [references/report-template.md](references/report-template.md)。

## 第7阶段 — 修复和验证

报告后，提供循环：

> *"发现N个严重和高问题。立即修复并重新验证？"*

如果同意：
1. 按文件/区域分组发现
2. 每个补丁
3. **仅重新步行受影响的切片**（不是整个应用）——包括引发错误的原始交互，并附上新的截图
4. 更新报告：标记 `✓ 已修复`，`✗ 仍然存在`，或 `⚠ 发现新问题`
5. 以“本次会话修复”总结结束

在一个会话中关闭循环，而不是等待明天的审核。

## 与ux-extract和brains-trust交叉引用

如果存在模式库（后备：`.jez/artifacts/ux-extracts/<ref>.md` → `docs/ux-extracts/<ref>.md` → `audits/extracts/<ref>.md`），在开始前阅读它，并将其用作发现的标准。

在结论后，可选地运行 `dev-tools:brains-trust` 进行第二意见审核（每4-6周一次）。合并发现时，**按 `(reproduction-steps, suspected-location)` 去重**——来自第二个模型的相同错误是一个具有两个确认的发现，而不是两个发现。添加 `Confirmed by:` 行。不要逐字附加第二个报告；产生噪音+膨胀严重性。

## 30秒Dogfood Drill（项目级规则）

审核很重。对于每次变更的预部署检查，建议在CLAUDE.md中设置项目规则：

> **在宣布任何UI变更“完成”之前，运行30秒Dogfood Drill：**
> 1. 打开受影响的页面
> 2. 在任何输入中输入
> 3. 点击主要操作
> 4. 观看下一个状态2秒
> 5. 打开相关视图（线程、模态、详细信息）
> 6. 阅读控制台
> 如果任何步骤显示意外行为，则变更未完成。

六步，~30秒。捕获立即出现的行为错误。与完整的ux-audit每周配合使用。

## Playwright killer-flow 测试

审核发现当前已损坏的内容。测试防止回归。建议为杀手流程编写10-15个Playwright测试——见 [references/playwright-killer-flows.md](references/playwright-killer-flows.md) 的起始示例（发送后输入清除，挂载时无控制台警告，线程打开后消息列宽度 ≥ 200px，@-mention正好一个药丸，等等）。通过CI在每次部署时运行。

## 自主性

- **立即行动**：导航、截图、读取页面、注入布局检测JS、使用假测试数据提交表单、编写报告文件、派遣截图审查子代理。
- **先询问**：破坏性行动（删除、发送、发布、支付）。对于破坏性信心测试，在运行该场景前询问一次。
- **停止并确认**：任何向外部人员发送邮件/通知的操作。

## 执行纪律

1. **从主会话驱动审核，而不是子代理。** 跨交互状态存在于一直在观察的会话中。一个全新的子代理从冷状态开始，遗漏了二阶发现。
2. **直接使用浏览器工具。** 主会话中的Chrome MCP或Playwright MCP。不要将截图交给一个全新的代理进行意见反馈。
3. **用变化进行彻底的循环。** 每次通过后，生成一个新的角度（不同的角色、不同的工作流、不同的输入量、不同的起始点）。只有在完整通过产生没有新发现时才停止。

对于预期运行时间 > 30分钟的审核，在主会话旁边设置一个15分钟的 `/loop` 检查——它记录发现，使会话立足，并提供一个自然的终止信号。见 [references/long-running-check-in-pattern.md](references/long-running-check-in-pattern.md)。

## 参考文件

| 时间 | 阅读 |
|------|------|
| **跨技能输出规范** (前5名，自我批评，最小补丁，校验-PASS，保持此状态) | [references/audit-output-discipline.md](references/audit-output-discipline.md) |
| **项目适配** — 非默认堆栈 (NextAuth/Lucia/Devise/Django认证，Prisma/TypeORM/ActiveRecord种子，WordPress/Rails/Django URL发现，按应用类型的人设库) | [references/project-adaptation.md](references/project-adaptation.md) |
| 人设库 + 写作协议 + 人设过载模式 | [references/persona-lock.md](references/persona-lock.md) |
| 审计期间认证过期 — 协议 + 无头测试认证恢复 | [references/auth-expired-handling.md](references/auth-expired-handling.md) |
| 数据调味视野 (第0天 / 1天 / 7天 / 30天) + 项目种子脚本架构 | [references/data-seasoning.md](references/data-seasoning.md) |
| 审计配置白名单格式 + 语义 + 表面覆盖 | [references/audit-config.md](references/audit-config.md) |
| 交互清单模板 + 重放协议 | [references/interaction-manifest.md](references/interaction-manifest.md) |
| 多面板压力矩阵 + 自动化代码片段 | [references/multi-pane-stress.md](references/multi-pane-stress.md) |
| 每屏评估问题，布局检测JS | [references/walkthrough-checklist.md](references/walkthrough-checklist.md) |
| 导航路径，心智模型，页面间连续性 | [references/workflow-comprehension.md](references/workflow-comprehension.md) |
| 每个场景的完整协议 (共11个场景) | [references/scenario-tests.md](references/scenario-tests.md) |
| 扩展压力配方 (竞争，慢速网络，减少动画，国际化) | [references/stress-test-recipes.md](references/stress-test-recipes.md) |
| 组件级完美检查清单 (6类 + 6状态) | [references/perfection-checklist.md](references/perfection-checklist.md) |
| AI-tell目录，光学居中，设计令牌规范 | [references/visual-polish.md](references/visual-polish.md) |
| 静默失败控制 + SDK合约检查 | [references/live-interaction-smoke.md](references/live-interaction-smoke.md) |
| Playwright杀手流程测试启动器 | [references/playwright-killer-flows.md](references/playwright-killer-flows.md) |
| 报告格式，判定块，严重性评分标准，复现步骤格式 | [references/report-template.md](references/report-template.md) |
| 浏览器工具命令和视口笔记 | [references/browser-tools.md](references/browser-tools.md) |
| 往返工作流完整性 (A→B→A模式) | [references/round-trip-workflows.md](references/round-trip-workflows.md) |
| 自动化可访问性 (axe-core注入 + 严重性映射) | [references/a11y-automation.md](references/a11y-automation.md) |
| 实用性能预算 (通过Performance API获取LCP/CLS/INP) | [references/performance-budget.md](references/performance-budget.md) |
| 通过15分钟`/loop`进行长时间运行审计监督 | [references/long-running-check-in-pattern.md](references/long-running-check-in-pattern.md) |

## 小贴士

- **每个犹豫都是发现。** 如果你停下来思考该点击什么，这就是值得报告的摩擦。
- **大胆使用吸管工具。** 最快的方法是找到灰色调、非令牌颜色、设计系统漂移。
- **覆盖率是算术问题。** 登记项 ÷ 测试项。在报告中发布该比率。
- **为截图审查和逐步记录发现结果设置子代理。** 不要在一个循环中驱动浏览器并分析200张截图。报告文件比你的上下文更便宜的记忆。
