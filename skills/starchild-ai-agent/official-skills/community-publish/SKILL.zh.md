---
name: community-publish
description: '发布预览到公共URL，开源项目到社区GitHub，并在服务市场列出服务（免费或付费）。


  当用户想要分享、发布、列出、开源或变现他们所构建的内容时使用（例如：公开此仪表板、分享我的项目、推送到GitHub、上架到服务市场、上架付费服务、提交审核）。'
---

## 两个概念：发布（PUBLISH）与上架（LIST）——切勿混淆

这项技能处理两个根本不同的概念。将它们混淆是导致错误答案的首要原因。

| 概念 | 含义 | 功能 |
|---|---|---|
| **发布（发布）** | 使某物**可访问**——URL可用，或代码托管在GitHub上 | `publish_preview`，`unpublish_preview`，`list_published_previews`，`open_source`，`remove_open_source`，`list_open_source`，`get_open_source`，`fork`，`validate_open_source` |
| **上架（上架）** | 使某物在市场**可发现/可购买** | 免费：`list_in_dashboard`，`unlist_from_dashboard`，`delete_listing`，`get_listing_status`<br>付费：`create_paid_service`，`submit_for_review`，`get_review_status`，`publish_service`，`unpublish_service`，`list_my_services`，`get_service`，`update_service`，`delete_service`，`restore_service`<br>封面：`upload_cover_image`<br>浏览+消费者：`explore_services`，`get_service_detail`，`get_service_pricing`，`get_service_reviews`，`write_service_review`，`favorite_service`，`unfavorite_service`，`get_favorite_services`，`get_user_services`，`get_service_earnings`，`get_earnings_summary`，`get_service_tags`，`get_featured_services`<br>项目查询：`explore_projects`，`my_projects`，`favorite_projects`，`get_tab_counts`，`get_popular_tags`，`get_user_projects`，`favorite_project`，`unfavorite_project` |

**发布不会自动上架。** `publish_preview()` 仅分配URL。`open_source()` 仅推送代码。它们都不会使项目在市场上可发现——这需要单独的、故意的上架调用。

### 上架有两种流程

| 流程 | 使用时机 | 是否需要审核 | 是否需要定价 | 功能 |
|---|---|---|---|---|
| **免费上架** | 免费 项目，显示在 `/projects` 画廊 | 否 | 否 | `list_in_dashboard()` |
| **付费上架** | 通过 x402 收费 | 需要（6项审核，必须通过才能发布） | 是（平台网络上 USDC/USDG 结算——默认 Base+Monad+Robinhood+X Layer+Solana，遵循 `all` 模式） | `create_paid_service()` → `submit_for_review()` (需要) → `publish_service()` |

> **`POST /api/services` 不再接受 `service_type: "free_project"`。** 免费 上架是通过 `list_in_dashboard()`（项目画廊流程）完成的。付费上架使用 `create_paid_service()` + 审核 + 发布（服务API流程）。

### 限时免费促销 ≠ 这项技能

在**付费**服务上架后，所有者可以运行**限时免费促销**（`free_promo_start` / `free_promo_end`）。这**不是**市场上架工作，也**未**在此实现。

| 概念 | 内容 | 地点 |
|---------|------------|--------|
| 免费 **上架** | 免费 项目在 `/projects` 画廊 | 这项技能 → `list_in_dashboard()` |
| `free_trial_count` | N次免费调用后才收费（仅限 `pay_per_use`） | 这项技能 → `create_paid_service(..., free_trial_count=N)` |
| **限时免费促销** | 日历窗口：金额为0的验证，无结算/扣款 | **x402 技能** → `skills/x402/references/selling.md` 部分中的 **限时免费促销** |

如果用户要求在已付费的上架项目上“开限时免费 / free promo / 免费 N 天”：
请阅读 **x402** 技能（自我检查 P1–P5，然后 PUT free-promo）。不要在社区发布或将其与 `free_trial_count` 混淆。

---

## 可见性模型——在回答“别人能看到吗？”之前请先阅读此内容

一个项目的“公开性”是**三个正交的开关**，而不是一个：

| 开关 | 关闭状态 | 打开状态 | 由谁触发 |
|---|---|---|---|
| **URL访问** | 访问URL返回404 | URL对任何有链接的人都可用 | `publish_preview` / `unpublish_preview` |
| **画廊可发现性** | 不在 `/projects` 画廊中 | 出现在画廊中 | `list_in_dashboard` / `unlist_from_dashboard` |
| **市场上架** | 不在服务市场 | 可发现 + 可购买 | `create_paid_service` + `publish_service` / `unpublish_service` |

一个项目可以是任何组合。切勿将这些合并为“它是否公开”。

**状态问题都是只读操作。** 每当用户询问：
- “是否可见 / 公开 / 可发现？”
- “上架了吗 / 在 dashboard 上吗 / 别人能看到吗”
- “上架是否已激活？”

权威答案仅来自一个新鲜的 `get_listing_status(slug)`（免费）或 `get_review_status(service_id)`（付费）调用。不要根据过去的操作进行推断。

---

## 项目类型——只有三种

| 类型 | 内容 | 是否适用于 `publish_preview()`？ |
|---|---|---|
| `task` | 定时cron/间隔作业 | 否（没有HTTP端口） |
| `service` | 长运行HTTP服务（dashboard，API，页面） | **是** |
| `script` | 一次性脚本 | 否（没有HTTP端口） |

---

## 路由——将用户意图匹配到正确的操作

### A. 状态意图——用户想知道当前状态

| 示例措辞 | 操作 |
|---|---|
| "是否可见 / 公开 / 可发现 / 活跃？" | `get_listing_status(slug)` |
| "上架了吗 / 在 dashboard 上吗 / 别人能不能看到" | `get_listing_status(slug)` |
| "我有哪些已发布的URL？" / "我发布了哪些" | `list_published_previews()` |
| "都有哪些开源代码？" / "都有哪些开源代码" | `list_open_source(...)` |
| "我的服务" / "我的服务" / "我的付费服务" | `list_my_services()` |
| "审核状态" / "审核通过了吗" / "review status" | `get_review_status(service_id)` |

### B. 操作意图——用户想改变状态

| 示例措辞 | 操作 | 备注 |
|---|---|---|
| "发布" / "分享" / "公开" / "公开" / "发布"（无限定词） | `publish_preview(preview_id)` | 仅分配URL。上架不会自动触发。 |
| "在 dashboard 上上架" / "上架" / "在社区上显示" / "使其可发现" / "发到广场" | `list_in_dashboard(slug)` | 免费 上架。需要预览已存在。 |
| "上架付费服务" / "使其成为付费服务" / "上架到服务市场（付费）" | `create_paid_service(...)` → `submit_for_review()` (推荐) → `publish_service()` | 付费 上架。需要先进行 x402 配置。 |
| "发布并上架" / "发布并上架" | `publish_preview()` 然后 `list_in_dashboard()` | 两个顺序分开的调用。 |
| "从 dashboard 上移除" / "下架" / "unlist" / "从画廊中隐藏" | `unlist_from_dashboard(slug)` | 免费 上架仅限。软下架（设置 `is_public=false`，`review_status='unlisted'`，保留统计信息）。预览URL仍然可用。 |
| "下架付费服务" / "unpublish service" | `unpublish_service(service_id)` | 付费 上架仅限。 |
| "开源" / "开源代码" / "开源代码" | `open_source(project_dir)` | 推送代码到GitHub。不会上架。 |
| "取消发布URL" / "移除链接" / "停止服务" | `unpublish_preview(slug)` | 仅停止预览容器服务。不会影响上架状态（`is_public`/`review_status` 不变）。URL变得不可访问（404）。 |
| "移除开源" / "从GitHub中删除" | `remove_open_source(slug)` | |
| "分支" / "安装他人的项目" | `fork(source)` | |
| "提交审核" / "submit for review" | `submit_for_review(service_id)` | 付费仅限。需要——发布前必须通过 |
| "发布服务" / "发布我的服务" | `publish_service(service_id)` | 付费仅限，需要批准或未上架状态 |
| "更新服务" / "更新服务" | `update_service(service_id, ...)` | 付费仅限 |
| "删除服务" / "delete service" | `delete_service(service_id)` | 付费仅限 |
| "删除项目" / "delete listing" / "永久从市场移除" | `delete_listing(slug)` | 免费 上架仅限。永久删除上架行和 `community_slugs` 记录。URL变得不可访问（404）。从探索和我的项目列表中移除。不使用 `unlist_from_dashboard()` 来隐藏而不删除。 |
| 重新阅读后仍模糊 | 问一个问题 | "你是要 (a) 发布公开URL，(b) 免费上架到广场，(c) 付费上架到服务市场，还是 (d) 开源代码？" |

---

## 通过 `publisher:` 绑定进行跨链接

当同一个项目同时具有公共URL和开源代码时，你希望它们配对，以便前端在列表卡片上显示“查看源代码”，在代码卡片上显示“访问实时演示”。这项技能通过 `project.yaml` 中的一个明确绑定来驱动这种配对。

### 如何声明绑定

在 `project.yaml` 中添加一个 `publisher:` 块：

```yaml
name: my-app
type: service
version: 1.0.0
publisher:
  code_slug: my-app               # 可选——默认为 manifest.name
  public_slug: my-app-pub         # 可选——URL后缀；默认为 code_slug
```

这两个字段都是可选的。如果省略，则都默认为 `manifest.name`。

### 任何一方都可以先发布

网关会保留一个挂起条目，直到另一方到达。**没有顺序要求**，无需手动链接步骤。

| 顺序 | 发生什么 |
|---|---|
| 先 `open_source` → 后 `publish_preview` | open_source 记录挂起条目；publish_preview 消耗它并链接 |
| 先 `publish_preview` → 后 `open_source` | publish_preview 记录挂起条目（需要 `publisher_code_slug` 参数）；open_source 消耗它并链接 |

### 手动修复（罕见）

如果配对连接错误（例如，重命名后），请使用：

```python
link_to_listing(listing_slug="2004-my-app-pub", code_slug="my-app")
```

---

## 架构

```
                community.iamstarchild.com (单一网关域名)
                              │
            ┌─────────────────┼─────────────────────┐
            │                 │                     │
   ┌────────▼─────────┐  ┌───▼────────────┐  ┌─────▼──────────┐
   │  /api/register   │  │/api/code-      │  │ /api/services  │
   │  /api/unregister │  │ projects/*     │  │ /api/projects- │
   │  /api/list       │  │ (GitHub-backed)│  │ query/*        │
   └────────┬─────────┘  └───┬────────────┘  └─────┬──────────┘
            │                │                     │
   ┌────────▼─────────┐  ┌───▼────────────┐  ┌─────▼──────────┐
   │ DB: 路由表      │  │ GitHub:        │  │ DB:            │
   │ + project_       │  │ community-     │  │ service_       │
   │   listings       │  │ projects repo  │  │ listings       │
   └──────────────────┘  └────────────────┘  │ (付费服务)      │
     publish_preview()    open_source()      └────────────────┘
                                              list_in_dashboard()
                                              create_paid_service()
```

---

## 发布：`publish_preview()` —— 公开URL

`publish_preview(preview_id, slug="", title="", publisher_code_slug="")`

将运行中的服务映射到 `https://community.iamstarchild.com/{user_id}-{slug}`。

- `preview_id`：来自 `preview(action='serve')`。必须 `status=running`。
- `slug`：仅URL后缀（小写字母数字+连字符，3-50个字符）。用户ID前缀会自动添加。
- `title`：列表的显示名称。
- `publisher_code_slug`：可选的跨链接绑定到代码项目的slug。

返回 `{"ok": True, "url": "...", "publisher": {...}, "hint": "...",
"x402_detected": bool}`——当 `x402_detected` 为 true 时会加上 `next_step` 警告（完成付费上架链）。

**约束：**
- **`publish_preview` 不会创建付费列表。** 如果端点通过 x402 收费（返回 402），发布流程不完整，直到你运行 `create_paid_service` → `submit_for_review`（推荐）→ `publish_service` —— 否则市场会显示空白或“免费”。当检测到计费时，返回值会标记这一点（`x402_detected: true` + `next_step`）。
- 每个用户最多20个已发布的预览（网关超过返回429）。
- 服务必须运行。容器停止时停止工作。
- 仅在 Starchild Fly 容器内工作（需要 `FLY_MACHINE_ID`）。
- **列表可见性默认为 `is_public=false`。** 成功的 `publish_preview` 分配URL，但不会使其可发现。发现需要单独的 `list_in_dashboard()` 调用。

**伙伴：**
- `unpublish_preview(slug)` — 停止预览容器服务。URL变得不可访问（404）。不会影响列表状态（`is_public`/`review_status` 不变）。
- `list_published_previews()` — 此用户当前所有已发布的预览URL。

---

## 发布：`open_source()` —— 推送代码到GitHub

`open_source(project_dir, version_bump="patch", message="")`

将项目源代码推送到 GitHub 上的 `community-projects/projects/{user_id}/{slug}/`。

- `project_dir`：例如 `output/projects/my-task`
- `version_bump`：`patch` | `minor` | `major` | `none`
- `message`：提交信息正文，描述此版本的变化。**（代理）** 应始终根据本次会话中你实际修改的代码编写此内容——如果你知道有变化，切勿留空。目标是一到三行简短的描述用户可见的变化。

**这是一个发布操作——它不会在市场上上架任何内容。** 发布后，单独调用 `list_in_dashboard()`（免费）或 `create_paid_service()`（付费）才能使项目可发现。

**伙伴：**
- `fork(source, dest_dir=None)` — 本地安装他人的开源项目
- `list_open_source(type=None, tag=None, user=None, q=None)` — 浏览 GitHub 目录
- `get_open_source(source)` — 获取一个项目的完整元数据
- `remove_open_source(slug)` — 从 GitHub 目录中删除项目目录（仅限所有者）
- `validate_open_source(project_dir)` — 发布前的预检

### 项目结构

`output/projects/{slug}/` 下的每个项目：

```
project.yaml      # 元数据（名称，版本，类型，环境要求，sc_proxy，publisher）
PROJECT.md        # 必需部分：是什么 / 必要环境 / 如何启动 / 输出 / 排错
.env.example      # 所有环境变量带占位符值
.gitignore        # 密码黑名单
src/
  ├── run.py       # 对于 type=task（必须开始：# -*- task-system: v3 -*-）
  ├── index.html   # 对于 type=service（或 app.py + 前端）
  └── main.py      # 对于 type=script
```

---

## 上架（免费）：`list_in_dashboard()` —— 显示在 /projects 画廊

`list_in_dashboard(slug, name=None, description="", cover_url=None, tags=None)`

在 `https://community.iamstarchild.com/projects` 的公共画廊中使已发布的预览可发现。如果没有，预览URL可用，但只有知道它的人才能看到。

- `slug`：`publish_preview()` 返回的**完整**slug（即 `{user_id}-{suffix}`）。
- `name`：画廊卡片显示名称。默认为 `slug`。
- `description`：≤500个字符。
- `cover_url`：必须在 `storage.googleapis.com`，`image.thum.io`，或 `api.microlink.io` 上。**要上传用户提供的图像，请先调用 `upload_cover_image(slug, file_path)`**——它会处理 presign → GCS上传 → 返回公共URL。见下文 [封面图像上传](#cover-image-upload-flow)。
- `tags`：≤5个标签，每个≤20个字符。

返回 `{"ok": True, "listing": {...}, "url": "...", "dashboard_url": "..."}`。

**约束：**
- 需要先为相同的slug运行 `publish_preview()`，否则返回404。
- 等幂的：再次调用，使用不同的名称/标签会更新现有列表。
- 无需审核，无需定价——这是免费上架流程。

**伙伴：**
- `unlist_from_dashboard(slug)` — 从画廊软下架（设置 `is_public=false`，`review_status='unlisted'`，保留查看/收藏计数）。URL仍然可用。要重新上架，请再次调用 `list_in_dashboard()`。
- `delete_listing(slug)` — 永久删除列表行和 `community_slugs` 记录（移除查看/收藏计数）。URL变得不可访问（404）。从探索和我的项目列表中移除。使用 `unlist_from_dashboard()` 来隐藏而不删除。
- `get_listing_status(slug)` — 只读检查：返回 `{ok, exists, is_public, listing}`。

---

## 上架（付费）：服务市场付费上架

付费服务通过 x402 收费（在平台启用的网络上进行链上 USDC/USDG 结算——默认 Base + Monad + Robinhood + X Layer + Solana，遵循 `all` 模式）。在发布前需要自动进行6项审核——服务必须通过所有检查（批准）后 `publish_service()` 才会工作。API调用示例是可选的，但推荐。

#### 多链支付网络（plans-280）

每个付费服务都有一个 **networks_mode**，决定买家可以在哪些链上支付：

| `networks_mode` | 行为 | 何时使用 |
|---|---|---|
| `"all"` (默认) | 在所有平台主网接受支付（目前包括 Base + Monad + Robinhood + X Layer + Solana；新的链会自动被接入，无需代码更改）。网关将 `supported_networks` 存储为 NULL，并在读取时扩展它。 | 常见情况——传递 nothing 或 `networks_mode="all"`。 |
| `"custom"` | 仅在接受 `supported_networks` 中列出的链上接受支付（`supported_networks` 是一个非空的 CAIP-2 ID 列表，例如 `["eip155:8453"]`）。**不**遵循平台扩展。 | 用户明确表示“仅 Base” / “仅 Monad” / 特定子集。 |

**规则：**
- **默认是 `all`。** 不要将单个链硬编码为默认值，例如 `['eip155:8453']`——这会重新引入旧的 Base 仅限行为。
- `custom` 需要 non-empty `supported_networks`；空列表会被拒绝。
- `provider_wallet` 是在所有启用链上使用的 EVM 地址（Starchild 促进者在每个链上结算到相同的地址）。它**不是**仅限 Base。
- 买家看到 402 `accepts` 数组（每个启用链一个条目，价格相同），并且**每笔支付选择一个链**——这是标准的 x402 多接受，不是协议变更。
- 结算的 Gas 由平台（Starchild 促进者）支付，不是由提供者支付。
- 要将现有服务切换回 `all`：`update_service(service_id, networks_mode="all")`。
- 要限制为子集：`update_service(service_id, networks_mode="custom", supported_networks=["eip155:8453"])`。

这与 **x402 技能的 `monetize` 默认值 (`all`)** 一致。这两个技能在同一发布版本上——如果网关 402 `accepts` 和市场列表显示的链不同，其中一方配置了 `custom`，而另一方保持 `all`。

### 服务生命周期与审核状态（审核是建议性的）

```
  创建 ──▶ 发布 ──▶ 提交审核 ─▶ 待定 ─▶ 已批准 / 已拒绝
                │            （发布前必须——必须通过才能上线）
                │                                    │ 通过 update_service() 修复，重新检查
                ▼                                    ▼
           publish_service() ─────────────────▶ 列出 ◀─▶ 取消列出（所有者下架 / 重新列出）
                                                     │
                                                     ▼
                                          不可用 ──▶ 恢复 ──▶ 列出
```

审核是一个**自我检查，不是关卡**：`submit_for_review()` 运行 5 个自动化检查（api_reachable, pricing_consistency, x402_payment, response_match, doc_completeness, examples_provided）并将报告存储给所有者。
`publish_service()` 要求服务处于 `approved` 状态（或 `unlisted` 用于重新列出）。**审核必须通过才能发布**——先运行 `submit_for_review()`，以便在买家付款前发现损坏的端点。`rejected` 报告**不会阻止列出**；对已 `listed` 的服务运行的检查永远不会将其下架。

### ⚡ 场景选择决策树——创建任何付费服务前必须遵循

**步骤 1：服务是否有 Starchild 项目页面（通过 `publish_preview()` 发布）？**
- **是，页面可以免费浏览** → 流程 D。使用 `service_type="paid_project"` + `project_slug`。免费页面通过 `publish_preview()` 发布，付费 API 位于 x402 的 `/api/*` 路由后面。上游应用在 `/` 服务器免费介绍页面，在 `/api/*` 服务器付费 API。
- **是，但整个页面需要付费** → 流程 B（表单 1）。使用 `service_type="paid_project"` + `project_slug`。用户实现自己的访问控制（付费墙 + 凭证验证）。见 x402 技能的“付费项目：两种形式”部分。
- **否（独立 API，无项目页面）** → 流程 C 或 E。使用 `service_type="paid_api"` 而不使用 `project_slug`。不要创建 index.html 或发布预览——没有免费页面。公共 URL 根目录将显示 x402 402 挑战或网关信息。

**步骤 2：用户是否需要多个不同价格的 API 端点？**
- **是** → 在一个 `create_paid_service()` 调用中使用 `api_endpoints` 数组（流程 E）。不要创建多个单独的服务。
- **否** → 单个端点，仅使用 `api_endpoint`。

**步骤 3：结合答案：**

| 用户想要 | 免费页面？ | 多端点？ | 流程 | service_type | project_slug | api_endpoints |
|------------|-----------|-----------------|------|-------------|--------------|---------------|
| 付费订阅项目（整个网站位于付费墙后） | 是 | 否 | B | `paid_project` | 必须提供 | — |
| 独立付费 API（无网页） | 否 | 否 | C | `paid_api` | **省略** | — |
| 免费介绍页面 + 付费 API | 是 | 否 | D | `paid_project` | 必须提供 | — |
| 免费介绍页面 + 多个付费 API | 是 | 是 | D+E | `paid_project` | 必须提供 | 必须提供 |
| 多个付费 API（无网页） | 否 | 是 | E | `paid_api` | **省略** | 必须提供 |

### ⚠️ 常见流程混淆错误（来自真实事件）

| 错误 | 出现问题 | 正确操作 |
|---------|----------------|----------------|
| 用户说“编写介绍页面和付费 API”，但代理使用 `paid_api` + 创建一个单独的项目预览 | 服务和项目是分离的——市场显示两个项目，一个免费（空白）和一个付费 | 使用 `paid_project` + `project_slug`（流程 D）。介绍页面和 API 是一个服务。 |
| 用户说“纯付费 API”，但代理创建 index.html 并发布预览 | 不必要的免费项目页面使市场变得混乱；介绍页面可能显示空白/JSON | 不要创建 index.html 或发布预览。使用 `paid_api`（流程 C）。x402 网关的 402 响应是 API 的自我描述。 |
| 用户说“多个 API 端点”，但代理创建 N 个单独的服务 | N 个市场卡片而不是 1 个；端口冲突；上游混乱 | 创建一个服务并使用 `api_endpoints` 数组（流程 E）。 |
| 代理重用上游端口，该端口已被另一个服务占用 | 网关代理到错误的上游——响应来自不同的服务 | 每个服务必须具有唯一的上游端口。检查 `.x402/services.json` 以查找冲突。 |
| 代理创建 start.py，其中 `/docs` 路由与上游的 `/docs` 冲突 | Flask `AssertionError: View function mapping is overwriting an existing endpoint` | 不要在 start.py 和上游应用中都定义 `/`、`/docs` 或 `/index.html` 路由——只在其中一个地方定义。 |

**关键规则：**
- **不要为独立付费 API 传递 `project_slug`。** `project_slug` 仅用于 `paid_project`——包括“免费网页 + 付费 API”模式（流程 D，使用 `paid_project`）。为独立的 `paid_api` 传递预览 slug 或不存在的 slug 会创建一个幽灵关联——后端会静默清除它，但你一开始就不应该传递它。
- **路由规则：与项目页面绑定的服务 → `paid_project`；`paid_api` 仅用于无项目页面的独立 API。** 如果你的 API 有一个通过 `publish_preview()` 发布的 Starchild 项目（着陆页/仪表板），用户可以免费浏览，使用 `service_type="paid_project"` + `project_slug`——这将服务合并到市场中的项目卡片中。如果没有免费项目页面，使用 `paid_api` 并不要设置 `project_slug`。传递 `paid_api` + `project_slug` 会被 `create_paid_service()` 自动升级为 `paid_project`（响应中会包含 `project_slug_warning`）——最终列表始终是 `paid_project`。
- `project_slug` 必须是**完整的已发布 slug，包括用户前缀**（例如 `33-my-app`），并且必须对应 `project_listings` 中的现有行（即 `publish_preview()` + `list_in_dashboard()` 必须先被调用）。
- `api_endpoints` 用于具有多个不同价格端点的服务；每个端点都有自己的 `path`、`price` 和可选的 `label`。
- 设置了 `project_slug` 的项目**不会**出现在“免费”标签下——它会移动到“所有”和“付费”标签下。
- **合并到项目卡片的可见性：** 当列出的服务有 `project_slug` 指向公共项目时，它会被折叠到统一市场视图中的该项目卡片中。后果：服务不会作为独立项出现在 `explore_services()` 或 `list_my_services()` 中——这是设计，不是列表失败。它仍然处于活动状态并且可以通过项目卡片、`get_service(service_id)` 和 `get_user_services(user_id)` 购买，并且它确实可以通过 `explore_marketplace()`（统一信息流）发现。要验证合并的服务是否列出，检查 `get_service()` → `review_status == "listed"`，而不是 `explore_services()` 结果。
- **当用户要求多个 API 时，创建一个服务并使用 `api_endpoints`**——不要创建多个单独的服务。见流程 E。

### 标签——市场筛选的预定义标签 slug

创建付费服务时，传递 `tags`，包含预定义列表下方 1-3 个标签 slug。代理应根据服务的名称和描述选择最相关的标签。标签用于市场筛选和发现——它们取代了旧的 `category` 字段。

**预定义标签 slug**（选择 1-3 个最相关的）：

| 领域 | 标签 |
|--------|------|
| DeFi & 交易 | `defi`, `trading`, `dex`, `dex-swap`, `lending`, `lending-yield`, `yield`, `staking`, `derivatives`, `bridge` |
| 链上数据 | `onchain-data`, `token-analytics`, `price-feed`, `wallet`, `wallet-portfolio`, `nft` |
| AI & 机器学习 | `ai-inference`, `llm-inference`, `text-analysis`, `image-generation`, `text-to-speech`, `video-transcription`, `translation` |
| Web & 数据 | `web-search`, `web-scraping`, `screenshot-pdf`, `news-feed`, `seo`, `data-service`, `data-storage`, `analytics` |
| 安全与合规 | `aml-sanctions`, `security`, `privacy`, `threat-detection`, `agent-safety`, `agent-trust` |
| 基础设施 | `smart-contract`, `oracle`, `zk-proofs`, `layer2`, `mev`, `compute`, `storage`, `developer-tools`, `identity`, `payment`, `payments` |
| 社交与媒体 | `social`, `social-media`, `gaming`, `metaverse` |
| 金融市场（传统金融） | `stock-equity`, `sec-edgar`, `real-estate`, `insurance`, `prediction-market` |
| 其他 | `dao`, `governance`, `email-sms`, `weather`, `geolocation`, `healthcare`, `agriculture`, `astrology-fortune`, `rwa`, `research-academic`, `legal-gov`, `launchpad` |

示例：一个 DeFi 价格 API → `tags=["defi", "price-feed", "trading"]`

### 流程 B — 付费项目列表

付费项目对访问收费。有两种形式——两者都使用 `service_type="paid_project"` + `project_slug`：

**形式 1：整个页面位于付费墙后**——页面本身需要付费。
用户实现自己的访问控制（一个带有凭证验证的登录组件）。平台提供 x402 支付协议；用户实现付费墙 UI 和凭证逻辑。见 x402 技能的“付费项目：两种形式”部分了解实现细节和“如何使用 Agent 支付”文档模板。

**形式 2：免费页面 + 付费 API**——页面可以免费浏览，API 调用收费。这是流程 D（下方）。上游应用在 `/` 服务器免费介绍页面，在 `/api/*` 服务器付费 API。

两种形式是相同模式——唯一区别是用户实现的内容（形式 1 的付费墙拦截器，形式 2 无需额外内容）。

1. **有一个运行中的项目**，具有公共 URL（通过 `publish_preview()`）。
2. **在项目的访问端点上配置 x402 收费**，使用 **x402 技能**。
   端点在未付款时返回 `402 Payment Required`，付款后返回 `200` + 数据。
3. **创建服务记录：**

```python
create_paid_service(
    name="高级交易信号",
    description="具有链上确认的实时交易信号。",
    service_type="paid_project",
    tags=["trading", "onchain-data"],
    project_slug="33-premium-signals",  # 完整的已发布 slug，包括用户前缀（URL 路径段）
    api_endpoint="https://community.iamstarchild.com/33-premium-signals",
    provider_wallet="0xAbC...yourEvmWallet",  # Base/Monad/Robinhood/X Layer 使用的 EVM 地址；Solana 地址从 Privy 钱包自动获取
    pricing_model="monthly",
    price=10,
    service_description="订阅者获得一个带有实时交易信号的仪表板。",
)
```

   必须的付费项目字段：`name`、`description`、`service_type`、
   `project_slug`、`api_endpoint`、`provider_wallet`、`pricing_model`、`price`、
   `service_description`。推荐：`tags`（1-3 个预定义标签 slug 用于市场筛选）。

   ⚠️ `project_slug` 必须是**完整的已发布 slug，包括用户前缀**
   （例如 `33-premium-signals`，项目 URL 中的确切路径段
   `https://community.iamstarchild.com/<slug>/`）。当 `api_endpoint` 未设置时，
   网关根据 `publicUrl + "/" + project_slug` 推断 API 端点，所以一个未前缀或错误的
   slug 会导致端点推导失败和项目与服务关联失败。修复现有记录
   使用 `update_service(service_id, project_slug="<full-slug>")`——无需重新列出。

4. **必须运行自动化审核**——付费服务在可以发布前必须通过审核。市场列出损坏的端点可能会在您注意到之前收取买家的钱：

```python
submit_for_review(service_id)   # 异步启动 6 个自动化检查
get_review_status(service_id)   # 循环检查，直到不再待定，然后向用户显示
                                # 报告——他们决定如何修复
```

   `rejected` 报告会阻止发布。阅读 `review_feedback` +
   `latest_task.checks`，使用 `update_service()` 修复，并重新运行
   `submit_for_review()` 直至批准。

5. **审核通过后发布**：

```python
publish_service(service_id)
```

   检查也可以再次运行针对已列出的服务——它永远不会将其下架。

### 流程 C — 付费 API 列表

付费 API 是一个已经实现 x402 收费的独立 API 服务。

> **⚠️ 不要为独立付费 API 传递 `project_slug`。**
> `project_slug` 仅用于 `paid_project`（必须）或“免费网页 + 付费 API”
> 模式（流程 D，其中存在已发布的 Starchild 项目页面）。对于没有关联免费项目页面的
> `paid_api`，完全省略 `project_slug`。
> 后端会验证 `project_slug` 对 `project_listings`，并静默清除不存在的 slug，但你
> 一开始就不应该传递它。
>
> **⚠️ 如果 API 属于已发布的 Starchild 项目，请使用 `paid_project`。**
> 如果你的 API 有一个通过 `publish_preview()` 发布的着陆页/仪表板（即它
> 作为项目存在于 community.iamstarchild.com 上），使用
> `service_type="paid_project"` + `project_slug=<full published slug WITH user prefix>`
> （流程 B）——不是 `paid_api`。`project_slug` 是将服务链接到项目卡片的（定价徽章，
> 交叉导航）。`paid_api` 列表没有项目关联，所以项目卡片将显示“免费”。
> 仅使用 `paid_api` 对于没有 Starchild 项目的真正外部/独立 API。忘记了链接？
> `update` 服务记录为 `project_slug`——无需重新列出。

1. **有一个 x402 启用的 API**——端点在未付款时返回 `402`，付款后返回 `200` + 数据。如果需要，使用 **x402 技能**实现此功能。

   #### 确保 Starchild 记录购买

   为了使 Starchild 市场跟踪购买、收入和使用统计，根据你的促进者设置选择以下两种方法之一：

   **选项 A — 使用 Starchild 促进者（推荐）**

   将你的 x402 中间件的促进者 URL 设置为：

   ```
   https://starchild-x402-facilitator.fly.dev
   ```

   成功结算后，Starchild 促进者会自动回调 community-gateway 记录购买。无需额外设置——继续使用默认的 `create_paid_service()` 调用进行步骤 2。

   **选项 B — 使用自己的促进者 + 代理模式**

如果你使用自己的服务中介（或第三方服务中介），Starchild 将无法接收结算回调。相反，在创建服务记录时（步骤 2）传递 `source="manual"`：

```python
create_paid_service(
    ...,
    source="manual",   # ← 启用代理模式
)
```

这会告诉市场为你的 API 生成一个**代理 URL**：

```
https://community.iamstarchild.com/proxy/{service_id}/...
```

用户通过这个代理 URL 访问你的 API。代理会透明地转发请求到你的真实 `api_endpoint`，并在成功支付（HTTP 200 并带有 `payment-signature` 头部）后自动在 Starchild 的数据库中记录购买。你**不需要**更改服务中介 URL 或设置任何回调。

**402 响应要求**（在审核期间进行检查）：

- 402 响应正文**必须**包含 `pricingModel` 字段（平台格式）。
- `payTo`**必须**是你的实际接收 EVM 钱包地址（在所有启用的链上使用）。
- `accepts` 数组包含每个启用链的一个条目（多链接受）；买家每笔支付选择一个链。每个条目都有相同的 `amount`（USDC，6 位小数）——平台在此版本中不支持按链定价。
- 响应必须是一个有效的 x402 挑战，客户端可以解析。

2. **创建服务记录** (`service_type = "paid_api"`):

```python
create_paid_service(
    name="On-chain Whale Tracker API",
    description="REST API 返回 12 条链上鲸鱼钱包的实时移动。",
    service_type="paid_api",
    tags=["onchain-data", "wallet-portfolio", "trading"],
    api_endpoint="https://api.example.com/v1/whales",
    provider_wallet="0xAbC...yourEvmWallet",  # EVM 地址用于 Base/Monad/Robinhood/X Layer；Solana 地址从 Privy 钱包自动获取
    pricing_model="pay_per_use",
    price=0.01,
    free_trial_count=3,
    api_documentation="# Whale Tracker API\n\n## GET /v1/whales\n\n返回最近的鲸鱼交易。\n\n### 参数\n| name | type | required | description |\n|---|---|---|---|\n| chain | string | no | 按 chain id 过滤（默认：所有） |\n| limit | int | no | 最大结果（默认：50，最大：200） |\n\n### 响应\n```json\n[{\"hash\":\"0x...\",\"from\":\"0x...\",\"to\":\"0x...\",\"value\":\"1000000\",\"token\":\"USDC\",\"chain\":\"base\",\"ts\":1700000000}]\n```",
    example_request="curl https://api.example.com/v1/whales?chain=base&limit=10",
    example_response='[{"hash":"0xabc...","from":"0x111...","to":"0x222...","value":"5000000","token":"USDC","chain":"base","ts":1700000000}]',
)
```

必需的付费 API 字段：`name`、`description`、`service_type`、`api_endpoint`、
`provider_wallet`、`pricing_model`、`price`、`api_documentation`。
推荐（可选）：`example_request`、`example_response`（提升买家体验）。
可选：`free_trial_count`（仅适用于 `pay_per_use`）、
`source`（`"manual"` 用于代理模式 — 见上一步选项 B；默认 Starchild 服务中介模式则省略）、
`cover_url`（自定义封面图片 URL — 必须位于 `storage.googleapis.com` 或其他允许的域名；如果未提供，代理应根据服务名称和描述自动生成合适的封面图片，通过图片上传服务上传，并传递结果 URL）。

#### 付费服务的封面图片

付费服务**不会**自动生成封面图片（免费项目会自动捕获截图）。在 `create_paid_service()` 中传递 `cover_url` — 必须位于 `storage.googleapis.com`（或 `image.thum.io` / `api.microlink.io`）。

**⚠️ 强制要求：当用户提供图片或你需要设置封面时，调用 `upload_cover_image(slug, file_path)`。** 该函数处理完整流程：预签名 URL → 压缩 → 上传到 GCS → 返回 `storage.googleapis.com` 公共 URL。
**不要**使用 imgur、数据 URI 或任何其他托管服务 — 网关会验证域名。

如果用户没有提供图片，生成一个（例如使用图片生成技能），本地保存，然后调用 `upload_cover_image()`。

你也可以稍后使用 `update_service(cover_url=...)` 来更改封面。

参考 [封面图片上传](#cover-image-upload-flow) 获取完整参考。

3. **运行审核** → 与 Flow B 步骤 4 相同（发布前必须）。
4. **发布** → 与 Flow B 步骤 5 相同（需要批准状态）。

### Flow D — 免费网页 + 付费 API（混合）

你的项目有一个免费落地页（通过 `publish_preview()` 发布）和一个付费 API 端点。用户可以免费浏览项目页面，但 API 调用需要付费。
市场会显示一个合并的卡片，包含“访问项目”和“调用 API”按钮。

1. **通过 `publish_preview()` 发布项目** — 这会创建免费落地页。
2. **在 API 端点配置 x402 收费**（例如 `/api/random` 返回 402）。
3. **创建服务记录**，使用 `service_type="paid_project"` + `project_slug`：

```python
create_paid_service(
    name="Random9 API",
    description="随机 9 位数 API。免费文档页 + 付费 API 调用。",
    service_type="paid_project",
    tags=["developer-tools"],
    project_slug="33-random9-api",  # 完整的 slug WITH 用户前缀 — 链接到免费项目页
    api_endpoint="https://community.iamstarchild.com/33-random9-api/api/random",
    provider_wallet="0xAbC...yourEvmWallet",  # EVM 地址用于 Base/Monad/Robinhood/X Layer；Solana 地址从 Privy 钱包自动获取
    pricing_model="pay_per_use",
    price=0.01,
    service_description="付费访问 Random9 API 端点；文档页保持免费。",  # paid_project 必需
    api_documentation="# Random9 API\n## GET /api/random\n返回一个随机 9 位数。",
    example_request="curl https://community.iamstarchild.com/33-random9-api/api/random",
    example_response='{"random":"482917365","digits":9}',
)
```

`project_slug` 将此服务合并到项目卡片中。项目页（`/`）保持免费；只有 API 端点（`/api/random`）需要付费。

> 注意：如果传递 `service_type="paid_api"` 与 `project_slug` 一起，
> `create_paid_service()` 会自动将其升级为 `paid_project` 并返回 `project_slug_warning` — 存储的列表始终是 `paid_project`。直接传递 `paid_project`（如上）是规范形式。

4. **发布 + 可选自检** → 与 Flow B 步骤 4–5 相同。

### Flow E — 多端点 API

你的服务有多个不同价格的 API 端点（例如基本 $0.01，高级 $0.10）。
每个端点都在市场详情视图中单独列出。

> **⚠️ 当用户要求多个 API 时，创建一个带有 `api_endpoints` 的服务 — 不要创建多个单独的服务。**
> 例如，如果用户说“开发三个付费 API 并列出它们”，**不要**三次调用 `create_paid_service()`。相反，创建一个包含所有三个端点的单一服务。这为用户提供了一个统一的市场卡片，他们可以在其中查看和购买单个端点。
> 只有当 API 真正无关时（不同域名，不同受众，不同定价模型）才创建多个服务。

1. **配置 x402 收费**，使用按路由定价：
   ```bash
   # 默认 networks_mode 是 "all"（Base + Monad）。省略 --networks 以跟随平台主网设置；
   # 仅当用户明确希望限制到单个链时，传递 --networks eip155:8453。
   python3 skills/x402/scripts/monetize.py --name my-api --upstream-port 5173 \
     --mode pay_per_use --price 0.01 \
     --route "GET /api/basic=$0.01" --route "GET /api/premium=$0.10" \
     --route "POST /api/batch=$0.50" \
     --facilitator $FAC
   ```

2. **创建服务记录**，使用 `api_endpoints`：

```python
create_paid_service(
    name="Data API Service",
    description="多个不同价格的 API 端点。",
    service_type="paid_api",
    tags=["data-service"],
    api_endpoint="https://example.com/api/basic",  # 审核的主要端点
    api_endpoints=[
        {"path": "GET /api/basic", "price": 0.01, "label": "Basic Query"},
        {"path": "GET /api/premium", "price": 0.10, "label": "Premium Query"},
        {"path": "POST /api/batch", "price": 0.50, "label": "Batch Process"},
    ],
    provider_wallet="0xAbC...yourEvmWallet",  # EVM 地址用于 Base/Monad/Robinhood/X Layer；Solana 地址从 Privy 钱包自动获取
    pricing_model="pay_per_use",
    price=0.01,  # 主要/默认端点的价格
    api_documentation="# Data API\n## GET /api/basic\n基本数据。\n## GET /api/premium\n高级分析。",
    example_request="curl https://example.com/api/basic",
    example_response='{"data":"basic market info"}',
)
```

你可以结合 Flow D + Flow E：使用 `service_type="paid_project"` + `project_slug`
与 `api_endpoints` 将免费项目页与多端点定价链接起来。
市场显示一个合并的项目卡片，在详情视图中显示端点列表。

3. **发布 + 可选自检** → 与 Flow B 步骤 4–5 相同。

### 审核检查（6 个自动检查 — 发布前必须通过）

`submit_for_review()` 会针对 `api_endpoint` 运行这些检查；服务必须通过所有检查才能发布。对已列出服务的检查永远不会将其下架：

| # | 检查 | 它验证什么 |
|---|---|---|
| 1 | `api_reachable` | 端点在没有发送 `X-PAYMENT` 头部时返回 `402 Payment Required` |
| 2 | `pricing_consistency` | 402 响应的 `accepts` 中的 `amount` 与你声明的 `price`（USDC 基本单位）匹配。多链 `accepts`（每个启用链一个条目），每个条目必须携带相同的 `amount` — 平台在此版本中不支持按链定价。 |
| 3 | `x402_payment` | 在有效的 x402 支付后，端点返回 `200` + 数据 |
| 4 | `response_match` | 实际响应的关键字段与你的 `example_response` 匹配 |
| 5 | `doc_completeness` | `api_documentation` 包含参数描述、响应格式和至少一个示例 |

检查 #5 是关键字匹配：文档必须包含一个“Response”（或“响应格式”）部分，并在标题下有实际正文 — 空白部分会导致审核失败。
`service_description`（paid_project）和 `api_documentation` / `example_request` /
`example_response`（paid_api）在调用时由 `create_paid_service()` 强制，它会错误地创建不可审核的记录。

**常见拒绝原因：**
- 402 响应 `amount` 与声明的 `price` 不匹配（小数点差异 / 单位错误）。
- 端点根本没有返回 402（x402 未设置，或向未认证请求返回 200）。
- `example_response` 与支付后 API 实际返回的不匹配。
- 文档缺少参数表或响应模式。

### 定价模型

所有付费服务使用 x402 `exact` 支付方案（在平台启用的网络上的链上 USDC/USDG 结算 — 默认 Base + Monad + Robinhood + X Layer + Solana，遵循 `networks_mode="all"`）。结算的 Gas 由 Starchild 服务中介支付，而不是提供者。

| `pricing_model` | 含义 | x402 行为 | 典型用途 |
|---|---|---|---|
| `pay_per_use` | 按调用收费 | 每个带有有效 `X-PAYMENT` 的请求 → 结算（收费） | API 调用 |
| `lifetime` | 一次性购买 | 首次支付结算；后续请求验证过去结算，不再收费 | 一次性购买 |
| `monthly` | 月度订阅 | 每个账单月结算一次；到期后重新收费 | 网页订阅，API 月度计划 |
| `weekly` | 周度订阅 | 每 7 天结算一次；到期后重新收费 | 短期订阅 |
| `quarterly` | 季度订阅 | 每 90 天结算一次；到期后重新收费 | 季度计划 |
| `yearly` | 年度订阅 | 每 365 天结算一次；到期后重新收费 | 年度计划（通常折扣） |
| `prepaid` | 预付余额 | 用户通过 `deposit-settle` 存款（一个链上交易），然后每个调用链下扣减余额（零 Gas） | 高频微支付 |

> `free_trial_count` 仅适用于 `pay_per_use` — 允许 N 次免费调用后才收费。
> 它**不是**日历免费促销。时间窗口免费（`free_promo_*`）→ **x402** 技能
> (`selling.md` → 限时免费促销)。

#### 多计划（多个定价选项）

一个服务可以同时提供多个定价计划（例如每周 + 月度 + 年度）。在创建服务时传递 `pricing_options` 数组：

```python
create_paid_service(
    ...,
    pricing_options=[
        {"pricing_model": "weekly", "price": 3, "is_default": True, "label": "Weekly"},
        {"pricing_model": "monthly", "price": 10, "label": "Monthly"},
        {"pricing_model": "yearly", "price": 90, "label": "Yearly (Save 42%)"},
    ],
)
```

**规则**：
- `pay_per_use` 不能与其他定价模型组合。
- 订阅模型（weekly/monthly/quarterly/yearly）可以自由组合。
- `lifetime` 和 `prepaid` 可以与订阅模型组合。
- 必须有一个选项标记 `is_default: True`（或第一个自动标记）。
- 服务的 `pricing_model` 和 `price` 字段会自动同步到默认选项。

**多计划 402 要求**：服务的 x402 中间件必须支持 `X-Pricing-Model` 头部 — 当客户端发送 `X-Pricing-Model: yearly` 时，402 响应必须返回年度计划的价格。审核会单独验证每个计划的 402 金额。

**参考**：参见 `x402-facilitator/docs/pricing-models.md` 获取完整规范。

#### 限制特定链的支付（自定义网络）

默认 `networks_mode="all"` 遵循平台主网设置（Base + Monad + Robinhood + X Layer + Solana）。仅在用户明确要求时才限制为子集（“仅接受 Base”，“不接受 Monad 支付”等）：

```python
# 创建一个仅接受 Base USDC（不接受 Monad）的服务
create_paid_service(
    ...,
    networks_mode="custom",
    supported_networks=["eip155:8453"],   # CAIP-2 链 ID；非空值是必需的
)

# 将现有服务从 all → custom（仅 Monad）
update_service(service_id, networks_mode="custom", supported_networks=["eip155:143"])

# 切换回 all（跟随平台主网；清除自定义列表）
update_service(service_id, networks_mode="all")
```

**不要**默认为 `custom` + `['eip155:8453']`。这会重新引入旧的 Base 仅行为。默认是 `all`；仅在用户明确限制时使用 `custom`。

---

### 服务示例（API 调用示例）— 推荐，但可选

API 调用示例是**可选的，但强烈推荐**。它们展示买家 API 返回的内容 — 出现在服务详情页的可折叠请求/响应对中。没有示例的服务仍会通过审核，但审核报告会指出缺少示例。

**推荐列表顺序：**

```
1. create_paid_service(...)                     → 创建服务
2. set_service_examples(service_id, examples)   → 推荐（提升买家体验）
3. submit_for_review(service_id)                → 发布前必须
4. publish_service(service_id)                  → 上线（需要批准）
```

**添加示例：**

```python
set_service_examples("service-uuid", [
    {
        "title": "查询 BTC 价格",
        "description": "获取当前比特币价格（美元）",
        "request": 'curl -X GET "https://api.example.com/v1/price?symbol=BTC"',
        "response": '{"symbol": "BTC", "price": 67234.56, "currency": "USD"}'
    },
    {
        "title": "查询 ETH 价格",
        "request": 'curl -X GET "https://api.example.com/v1/price?symbol=ETH"',
        "response": '{"symbol": "ETH", "price": 3456.78, "currency": "USD"}'
    }
])
```

**清除示例**（很少需要 — `set_service_examples` 替换所有内容）：

```python
clear_service_examples("service-uuid")
```

**最佳实践：**
- 添加 2-5 个示例，涵盖最常见的用例
- 使用描述性标题，解释场景
- 包含现实的请求参数和响应数据
- 展示简单和复杂的用法模式
- `set_service_examples()` 替代所有示例 — 每次都传递完整列表

此规定取代了 `create_paid_service()` 中传递的旧式单个 `example_request` / `example_response` 字段。带有旧式字段的旧服务仍然可以通过审核（向后兼容），但新服务应使用 `set_service_examples()` 进行更丰富的多场景演示。

### 付费服务管理函数

| 函数 | 用途 |
|---|---|
| `create_paid_service(...)` | 创建服务记录（发布状态） |
| `set_service_examples(service_id, examples)` | 设置 API 调用示例（可选，推荐）— 替代所有示例 |
| `clear_service_examples(service_id)` | 删除所有 API 调用示例 |
| `submit_for_review(service_id)` | 运行 6 检查自动审核（发布前必须执行） |
| `get_review_status(service_id)` | 查询审核进度 + 每项检查的详细信息 |
| `publish_service(service_id)` | 上线（需要批准或未列出状态） |
| `unpublish_service(service_id)` | 下线（列出 → 未列出） |
| `list_my_services(cursor, limit)` | 列出您的服务（分页） |
| `get_service(service_id)` | 通过 ID 获取单个服务 |
| `update_service(service_id, **fields)` | 更新服务字段（例如，拒绝后修复） |
| `delete_service(service_id)` | 永久删除服务 |
| `restore_service(service_id)` | 将不可用的服务恢复为列出状态 |

### 市场浏览和消费者函数

这些函数允许代理浏览服务市场、阅读评论、撰写评论、管理收藏夹和检查收益 — 与网页前端相同。

| 函数 | 用途 |
|---|---|
| `explore_marketplace(search, paid_only, ...)` | ⭐ **统一浏览 — 首先使用此功能查找付费服务/API。** 项目卡片 + 独立服务在一个信息流中（与网页 All/Paid 标签相同）；唯一能显示合并到公共项目卡片中的服务的搜索路径。项目有 `type`：`service`（使用 `id`）或 `project`（付费卡片携带 `service_id`）— 输入 `get_service_detail()` |
| `explore_services(search, sort, tags, ...)` | 仅浏览独立服务项目（服务 API）。⚠️ 合并到公共项目卡片中的服务不会在此处显示 — 使用 `explore_marketplace()` 获取完整覆盖范围 |
| `get_service_detail(service_id)` | 已发布服务的公共详细信息（包括文档，增加浏览量） |
| `get_service_pricing(service_id)` | 经过验证的定价，具有实时 x402 检查 |
| `get_service_reviews(service_id, sort)` | 列出服务的评论（公共） |
| `write_service_review(service_id, rating, comment)` | 提交/更新评论（必须先购买或使用） |
| `get_user_services(user_id)` | 获取用户的已发布付费服务（公共，用于个人资料显示） |
| `favorite_service(service_id)` | 将服务添加到收藏夹 |
| `unfavorite_service(service_id)` | 从收藏夹中删除服务 |
| `get_favorite_services(cursor, limit)` | 列出当前用户的收藏服务 |
| `get_service_purchase_status(service_id)` | 检查当前用户是否已购买/使用服务 |
| `get_service_earnings(service_id)` | 单个服务的收益统计（仅所有者） |
| `get_earnings_summary()` | 所有服务的收益摘要（仅所有者） |
| `get_service_onchain_records(service_id)` | 链上 USDC 结算记录（仅所有者） |

---

## 从 bash 块中使用的用法

```bash
python3 - <<'EOF'
import sys
# 优先使用注册的技能工具（通过 read_file 读取此 SKILL.md 来加载它们），而不是手写的 exports.py 导入。如果您确实需要直接导入：目录名有连字符，所以点分导入（`from skills.community_publish import ...`）会引发 ModuleNotFoundError。使用此 sys.path 模式（或 importlib.util.spec_from_file_location）。
sys.path.insert(0, "/data/workspace/skills/community-publish")
from exports import (
    # 发布：公共 URL
    publish_preview, unpublish_preview, list_published_previews,
    # 发布：开源代码
    open_source, remove_open_source, fork,
    list_open_source, get_open_source, validate_open_source,
    # 列出：免费（项目画廊）
    list_in_dashboard, unlist_from_dashboard, get_listing_status,
    # 列出：付费（服务市场）
    create_paid_service, submit_for_review, get_review_status,
    publish_service, unpublish_service,
    list_my_services, get_service, update_service, delete_service,
    restore_service, set_service_examples, clear_service_examples,
    # 市场：浏览 + 消费者操作
    explore_marketplace, explore_services, get_service_detail,
    get_service_pricing, get_service_reviews, write_service_review,
    get_user_services, favorite_service, unfavorite_service,
    get_favorite_services, get_service_purchase_status,
    get_service_earnings, get_earnings_summary, get_service_onchain_records,
    # 手动修复（罕见）
    link_to_listing,
)

# 第 1 步：发布 URL
print(publish_preview(preview_id="my-app-a3f1", slug="my-app"))

# 第 2 步 a：免费列出 — 显示在画廊中
print(list_in_dashboard(slug="33-my-app", name="My App", description="A cool app"))

# 或者第 2 步 b：付费列出 — 创建服务 + 审核 + 发布
res = create_paid_service(
    name="My Paid App",
    description="Premium features",
    service_type="paid_project",
    tags=["developer-tools"],
    project_slug="33-my-app",  # 完整已发布的 slug WITH 用户前缀
    api_endpoint="https://community.iamstarchild.com/33-my-app",
    provider_wallet="0xAbC...",
    pricing_model="monthly",
    price=5,
    service_description="Subscribers get premium features.",
)
print(res)
# 然后：publish_service(res["service_id"]) — 可选地先 submit_for_review() 进行自检报告
EOF
```

---

## 行为规则

- **在 `open_source()` 之前显示差异**。在 `validate_open_source` 之后，总结即将推送的内容并请求确认。例外：明确的“无确认发布”或重新发布已知良好的项目。
- **在 fork 时永不自动运行 setup.sh**。显示命令，让用户确认。
- **在 fork 时始终批量收集环境变量**。读取项目的 `env_required`，与 `workspace/.env` 进行差异比较，调用 `request_env_input` 一次性传递缺失的键。
- **发布需要审核**。`publish_service()` 需要 `approved` 状态 — 始终先运行 `submit_for_review()`。向用户显示报告；如果被拒绝，使用 `update_service()` 修复并重新运行 `submit_for_review()`。对已列出服务的检查永远不会将其下线。
- **`api_endpoint` 必须是 x402 收费端点**。对于付费项目，这是项目的公共 URL。对于付费 API，它是外部 API URL。审核者会点击此 URL 并期望返回 `402`。
- **价格单位是 USDC**。402 响应的 `accepts.amount` 是**基本单位**（USDC 6 位小数）。`0.01` 价格 → `amount: "10000"`。此处不匹配是 #1 审核失败原因。
- **不要编造审核结果**。始终调用 `get_review_status()` 检查 — 永远不要假设因为您提交了就通过了审核。
- **不要混淆发布和列出**。`publish_preview()` 分配 URL。`list_in_dashboard()` / `create_paid_service()` 使其可发现。这是两个独立的、故意的步骤。
- **Slug 规则**：小写字母数字 + 连字符，3-50 个字符，无首尾连字符。
- **版本规则**（`open_source`）：严格的 semver。重新发布相同版本会被拒绝。
- **URL ≠ 代码 ≠ 列出**：公共 URL 下线不会删除开源代码或市场列出，反之亦然。它们是独立的。
- **不要传递 `project_slug` 用于独立的 `paid_api` 服务**。`project_slug` 仅属于 `paid_project` — 包括“免费网页 + 付费 API”模式（Flow D，使用 `paid_project`；传递 `paid_api` + `project_slug` 会被自动升级为 `paid_project` 并带有 `project_slug_warning`）。为独立 API 传递预览 slug 或不存在的 slug 会创建一个幽灵关联。后端会静默清除不存在的 slug，但除非用户明确希望将免费项目页面与付费 API 关联，否则不要传递 `project_slug`。
- **当用户要求多个 API 时，创建一个带有 `api_endpoints` 的服务**。不要多次调用 `create_paid_service()` 用于相关 API。使用 `api_endpoints` 数组在单个服务中列出所有端点（Flow E）。只有当 API 真正无关时（不同域名、不同受众、不同定价模型）才创建多个服务。
- **默认支付网络为 `all`**。永远不要将单个链（例如 `['eip155:8453']`）硬编码为默认值 — 这会重新引入旧的 Base-only 行为。省略 `networks_mode` / `supported_networks`（或传递 `networks_mode="all"`）以便服务遵循平台主网设置（Base + Monad + Robinhood + X Layer + Solana；新链自动获取）。只有在用户明确要求限制为子集（“仅 Base”、“仅 Monad”等）时，才使用 `networks_mode="custom"` + 非空的 `supported_networks`。
- **`provider_wallet` 是在所有启用的 EVM 链上使用的 EVM 地址**。Starchild 促进者在每个 EVM 链上结算到同一地址；它不是 Base-only。不要向用户描述为“Base 钱包”。**对于 Solana 支付**，平台自动使用用户的 Privy Solana 钱包地址（`provider_sol_wallet`）。如果用户尚未明确提供 Solana 地址，`create_paid_service()` 会从 Privy 钱包自动获取。没有 Solana 地址的服务将不接受 Solana 支付（Solana 不在 402 接受列表中）。
- **结算 Gas 由平台支付**，不是提供者。不要告诉提供者他们需要为结算 Gas 资助 ETH/MON。
- **常见陷阱**

| 症状 | 原因 | 修复 |
|---|---|---|
| `publish_preview`: `Preview not found` | 错误的 preview_id，或服务已停止 | 查看 `/data/previews.json`，使用 `preview(action='serve')` 重新启动 |
| `publish_preview`: `429 Too many published previews` | 达到用户 20 个/次的网关限制 | `unpublish_preview()` 首先删除一些旧的 |
| `publish_preview`: `FLY_MACHINE_ID not set` | 本地运行，不在 Starchild 容器中 | URL 发布仅在产品容器中工作 |
| `list_in_dashboard`: `404 No preview found` | `publish_preview()` 尚未为该 slug 运行 | 首先调用 `publish_preview()` |
| `open_source`: `400 Validation failed: env names not in .env.example` | 在 `env_required` 中列出 `MY_KEY` 但忘记了 `.env.example` | 将缺失的键添加到 `.env.example` |
| `open_source`: `400 Possible secret detected` | 密钥扫描器发现了一个看起来像 API 密钥的密钥 | 移动到环境变量；`.env.example` 值应为 `your-key-here` |
| 市场 显示服务为免费/缺失，发布后 | 仅运行了 `publish_preview()` — URL 发布 ≠ 付费列出 | 完成链：`create_paid_service` → `publish_service` |
| `create_paid_service`: `400 Free services should be published through the Project publish flow` | 尝试 `service_type: "free_project"` | 使用 `list_in_dashboard()` 发布免费项目，而不是 `create_paid_service()` |
| `publish_service`: `400 not in a publishable state` | 服务已列出、不可用或已删除 | 检查 `get_service()` 状态；`unavailable` → `restore_service()` |
| `submit_for_review`: `400 Free services do not require review` | 服务记录创建为免费类型 — 付费负载是手动构建的（缺少 `service_type`/钱包/定价），而不是通过 `create_paid_service()` | 删除它并使用 `create_paid_service()` 重新创建（所有付费字段都是必需的位置参数，因此无法通过函数发生） |
| 审核被拒绝：`pricing_consistency` 失败 | 402 响应 `amount` 与声明的 `price` 不匹配 | 确保 `amount` = `price * 1000000`（USDC 6 位小数） |
| 审核被拒绝：`api_reachable` 失败 | 端点不返回 402 | 首先在端点上设置 x402 收费 |
| `create_paid_service` 响应有 `project_slug_warning` | 为 `paid_api` 传递了 `project_slug` 但该 slug 不存在于 `project_listings` | 后端自动清除。如果这是一个独立 API，不要传递 `project_slug`。如果您打算使用 Flow D，首先 `publish_preview()` + `list_in_dashboard()` 项目，然后 `update_service()` 使用正确的 slug。 |
| `create_paid_service`: `500 Failed to create service` 在删除→创建循环中使用了相同的名称后 | 删除的服务保留其 slug（软删除），并且 slug 生成只尝试有限数量的后缀 — 重复删除/创建一个名称会耗尽它们 | 不要等待并重试 — 该失败对于该名称是永久性的。使用不同的服务名称，或 `restore_service(service_id)` + `update_service()` 而不是删除+重新创建 |
| 用户要求“多个 API”时创建了多个服务 | 对每个 API 调用一次 `create_paid_service()` 而不是使用 `api_endpoints` | 使用 Flow E：一个 `create_paid_service()` 调用，带有 `api_endpoints=[...]` 数组。只有当 API 真正无关时才拆分为多个服务。 |
| 购买未记录的外部 API（自己的促进者） | 服务创建时没有 `source="manual"`，因此没有生成代理 URL，Starchild 没有观察支付的方式 | 要么切换到 Starchild 促进者（选项 A），要么使用 `source="manual"` 重新创建服务（选项 B） |
| 代理 URL 对于 `source="manual"` 服务返回 502 | `api_endpoint` URL 对 Starchild 服务器无法访问 | 验证外部 API 是否公开可访问且没有被防火墙阻挡 |
| 市场 显示一个链，402 `accepts` 没有或反之亦然 | 服务 `networks_mode` 和 x402 网关的 `accepts` 不同步 — 例如，列出是 `all`（Base+Monad），但 x402 网关使用 `--networks eip155:8453`（自定义，Base 仅限） | 重新运行 x402 技能的 `monetize` 而不使用 `--networks`（以跟随 `all`），或 `update_service(service_id, networks_mode="custom", supported_networks=[...])` 以匹配网关。两者必须一致。 |
| `create_paid_service` / `update_service` 拒绝“supported_networks must be a non-empty list” | 传递了 `networks_mode="custom"` 但 `supported_networks` 缺失、为空或 `None` | 传递一个非空 CAIP-2 ID 列表（例如 `["eip155:8453"]`），或切换到 `networks_mode="all"`（默认）以接受所有平台主网。 |
| 买家无法在 Monad 上支付（402 没有 Monad `accepts`）但列出显示 Monad | x402 网关在多链发布之前被货币化，或使用 `--networks eip155:8453` | 重新运行 `monetize` 而不使用 `--networks`，以便 402 `accepts` 数组包含所有平台主网。列出 `all` 模式是正确的；网关侧是过时的。 |
| 在一个链上结算失败，但在另一个链上工作 | Starchild 促进者的结算者在该链上没有 Gas（Base 的 ETH，Monad 的 MON） | 平台侧问题（gas 是补贴的）。其他链仍然正常工作。向 ops 报告 — 不要要求提供者资助 gas。 |

---

## 封面图片上传流程

**⚠️ 强制 — 每次需要设置或更改封面图片时，请阅读此部分。**

网关验证 `cover_url` 域名。仅接受 `storage.googleapis.com`、`image.thum.io` 和 `api.microlink.io`。**不要使用 imgur、数据 URI 或任何其他托管服务。**

### 快速路径：`upload_cover_image()`

```python
from skills.community_publish.exports import upload_cover_image

result = upload_cover_image("my-slug", "/path/to/image.png")
# result = {"ok": True, "public_url": "https://storage.googleapis.com/..."}

# 然后使用 URL：
list_in_dashboard("my-slug", name="My Project", cover_url=result["public_url"])
# 或：
create_paid_service(..., cover_url=result["public_url"])
# 或：
update_service(service_id, cover_url=result["public_url"])
```

### `upload_cover_image()` 内部实现

1. **预签名** — 调用 `POST /api/projects/cover/presign` (通过 `Authorization: Bearer $CONTAINER_JWT` 传递容器 JWT) 并传入 `slug`, `content_type`, `file_size`
2. **上传** — 将原始图片字节 PUT 到 GCS V4 签名 URL
3. **返回** — 返回 `storage.googleapis.com` 上的 `public_url`

### 支持的格式

- `image/png`, `image/jpeg`, `image/webp`
- 最大 2MB — 如有需要，上传前请先压缩

### 如果用户提供了大图片

```python
# 首先压缩 (PIL 示例)
from PIL import Image
import io

img = Image.open("/path/to/large.png")
img.thumbnail((1200, 630))  # 合理的封面尺寸
buf = io.BytesIO()
img.save(buf, format="JPEG", quality=85)
buf.seek(0)

# 保存压缩后的版本
compressed_path = "/tmp/cover_compressed.jpg"
with open(compressed_path, "wb") as f:
    f.write(buf.getvalue())

# 上传
result = upload_cover_image("my-slug", compressed_path)
```

### 常见错误

| 错误 | 失败原因 | 解决方法 |
|---|---|---|
| 使用 imgur URL 作为 `cover_url` | 域名不在允许列表中 (项目/内部路由会以 400 拒绝) | 使用 `upload_cover_image()` → GCS URL |
| 将数据 URI 作为 `cover_url` | 网关返回 500 (URL 过长 / 无效 URL) | 保存为文件，然后 `upload_cover_image()` |
| 使用 thum.io 截取预览页面的截图 | 内部端口上的预览页面无法公开访问 | 使用 `upload_cover_image()` 并传入实际图片文件 |
| 未阅读知识文档 | 缺少 GCS 配置、路径约定、域名规则等背景信息 | 始终查阅 `starchild-knowledge/starchild-community-gateway/service-cover-upload.md` |

---

## 前端展示 — 项目 vs 服务

Web 前端为社区内容提供了 **两个独立的模态框**：

| 模态框 | 内容类型 | 显示内容 | 查询功能 |
|---|---|---|---|
| **ProjectMarketplaceModal** | 免费项目 | 卡片网格：封面图片、名称、描述、标签、浏览量、收藏量 | `explore_projects()`, `my_projects()`, `favorite_projects()`, `get_tab_counts()`, `get_popular_tags()`, `get_user_projects()`, `favorite_project()`, `unfavorite_project()` |
| **MarketplaceModal** | 付费服务 (x402) | 服务卡片：价格、评分、购买按钮 | `explore_services()`, `list_my_services()`, `get_service_detail()`, `get_service_tags()`, `get_featured_services()` |

两者也出现在 **AgentProfile** (项目标签页 / 服务标签页) 和首页。

每个项目都有一个 **直接 URL** (基于路径的 `/{slug}` 或子域名 `{slug}.community.iamstarchild.com`)。`/projects` 和 `/services` 页面是前端渲染的浏览页面。

### 项目查询功能

| 功能 | 数据范围 | 目的 |
|---|---|---|
| `explore_projects(search, tag, sort, limit, cursor)` | 公开 | 浏览所有公开项目。排序：`all` (最新) 或 `trending`。 |
| `my_projects(tag)` | 个人 | 列出当前用户发布的项目及统计信息。 |
| `favorite_projects(tag, limit, cursor)` | 个人 | 列出当前用户收藏的项目。 |
| `get_tab_counts()` | 个人 | 获取标签页计数 (探索、我的、收藏、已购买、服务我的、服务收藏)。 |
| `get_popular_tags()` | 公开 | 获取热门项目标签用于筛选。 |
| `get_user_projects(user_id, limit)` | 公开 | 获取特定用户公开项目 (用于个人资料页)。 |
| `favorite_project(slug)` | 个人 | 将项目添加到当前用户的收藏。 |
| `unfavorite_project(slug)` | 个人 | 从当前用户的收藏中移除项目。 |

### 服务查询功能

| 功能 | 数据范围 | 目的 |
|---|---|---|
| `explore_services(search, sort, tags, ...)` | 公开 | 仅浏览独立付费服务。 |
| `list_my_services(cursor, limit)` | 个人 | 列出当前用户的付费服务。 |
| `get_service_detail(service_id)` | 公开 | 公开已发布服务的详细信息。 |
| `get_service_pricing(service_id)` | 公开 | 验证价格信息 (实时 x402 验证)。 |
| `get_service_reviews(service_id, sort, cursor, limit)` | 公开 | 列出服务的评论。 |
| `write_service_review(service_id, rating, comment, is_anonymous)` | 个人 | 提交或更新评论 (upsert)。 |
| `get_service_tags()` | 公开 | 获取预定义服务标签及国际化名称。 |
| `get_featured_services()` | 公开 | 获取首页展示的推荐服务。 |
| `get_user_services(user_id, limit)` | 公开 | 获取特定用户发布的付费服务。 |
| `favorite_service(service_id)` | 个人 | 将服务添加到收藏。 |
| `unfavorite_service(service_id)` | 个人 | 从收藏中移除服务。 |
| `get_favorite_services(cursor, limit)` | 个人 | 列出当前用户的收藏服务。 |
| `get_service_purchase_status(service_id)` | 个人 | 检查用户是否已购买/使用服务。 |
| `get_service_earnings(service_id)` | 个人 | 获取服务收益统计 (仅所有者可见)。 |
| `get_earnings_summary()` | 个人 | 获取所有服务的收益汇总。 |
| `get_service_onchain_records(service_id, cursor, limit)` | 个人 | 获取链上交易记录 (仅所有者可见)。 |

---

## 参考

- `lib/manifest.py` — project.yaml 解析器/写入器 + semver 辅助工具
- `lib/validate.py` — 本地预发布验证 (镜像网关端检查)
- `lib/install.py` — 类型特定安装处理器 (任务/服务/脚本)
- `lib/gateway.py` — `/api/register` (URL) 的 HTTP 客户端、`/api/code-projects/*` (代码)、`/api/projects-query/*` (免费列表+浏览)、`/api/services/*` (付费列表)、`/api/projects/cover/presign` (封面上传) 的 HTTP 客户端
