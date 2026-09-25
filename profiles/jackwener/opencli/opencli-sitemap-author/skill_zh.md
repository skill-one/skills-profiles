# opencli-sitemap-author

你正在为代理编写**任务执行图**，而不是 SEO 站点地图。该工件应帮助使用 `opencli browser` 的代理判断其当前位置、下一步路径、优先选择的 OpenCLI 适配器，以及当页面与内存不一致时如何恢复。

保持站点地图小巧且经过验证。不要爬取整个站点。仅捕获你实际观察到的与任务相关的路径。

---

## 存储模型

两层结构：

- **全局种子**：`sitemaps/<站点>/`（顶层）
- **本地覆盖层**：`~/.opencli/sites/<站点>/sitemap/`

本地覆盖层通过稳定 ID 优先。首先将新发现写入本地。只有在审查后才能提升到全局。

推荐布局：

```text
sitemap/
  SITE.md                 # 站点目的、认证假设、稳定页面 ID
  pages/<页面ID>.md      # 页面状态签名、操作、链接 API
  pages/_<部分>.md       # 跨页面 UI 部分（例如 _tweet_card.md）
  workflows/<任务ID>.md  # 最佳路径、备用路径、避免列表
  pitfalls.md            # 持久性故障模式和过时区域
```

### 大小指导（实测启发式）

`references/sitemap-schema.md` §1.1 规范硬性要求 800 个 token，但 PoC 实测简单站点单页面 1-2 个操作自然落在 800-2000 个 token。强行拆分反碎片化，作者使用下表决策：

> 规范 800 是懒加载优化目标 + Phase 2 审计阈值；下表是作者实战决策辅助，**不替代规范硬性限制**。超过 800 的文件审计会标记，作者解释（"5 个连贯的 UI 原语一起放"）或拆分。

| 文件 token | 决策 |
|---|---|
| < 1500 | 自然大小，不动 |
| 1500-3000 | 查看 cohesion — 5 个连贯的 UI 原语一起放 OK；混合内容拆分 |
| > 3000 | **必须拆分** 子文件或部分（代理懒加载预算确实有限制） |

Phase 2 cron 审计按 token 数量不按字节数量（CJK 中文 token-per-char 比 English 高 30-50%）。

---

## 编写循环

1. **加载现有记忆**：首先读取本地覆盖层，如果存在则读取全局种子。
2. **验证现实**：使用 `opencli browser <会话> state`、`find`、`network` 和 `analyze`；浏览器状态为真。如果你刚刚为该站点完成了 `opencli-adapter-author` 会话，从 `~/.opencli/sites/<站点>/traces/` 下的保留浏览轨迹作为种子证据开始，而不是从零重新发现路径。
3. **仅记录持久结构**：页面目的、稳定锚点、状态签名、操作、工作流、API 引用、故障点。
4. **使用稳定 ID**：页面/操作/工作流 ID 应在 URL 参数、本地化文本漂移和微小布局更改后仍然有效。
5. **写入本地草稿**：除非明确提升到仓库，否则更新 `~/.opencli/sites/<站点>/sitemap/...`。
6. **在冲突时标记过时**：如果现有站点地图与当前浏览器状态不一致，信任浏览器状态并标记该项目过时，而不是强制旧路径。

---

## 必需的操作模式

每个操作边必须包含：

```yaml
### action:<稳定ID>
pre: <当前页面 / 状态 / 认证要求>
do: <代理操作、适配器命令或语义浏览器命令>
post: <证明成功的 URL / 状态 / 输出>
fail: <失败信号 1> | <信号 2>
recover: <备用指令>; adapter_health_update: <适配器> -> suspect
evidence: opencli browser <cmd> 或 trace:<路径>
```

默认使用这种紧凑形式。只有在操作确实需要长解释时，才使用 `references/sitemap-schema.md` 中的长 Markdown 形式。`verified_at` 和 `source` 继承自文件前注；不要在每个操作中重复它们。

不要在没有证据的情况下提升操作。如果恢复路径标记 `adapter_health_update`，浏览器-站点地图消费者必须将健康更新写入本地覆盖层，以便下一个代理不会重试已知的可疑适配器。

### 部分页面（跨页通用 UI）

部分文件 (`_<名称>.md`，`url_patterns: []`) 包含跨页面 UI 原语（例如 `_tweet_card.md` 的 like/reply/repost/bookmark）。被多个页面通过 `action:<ID> in pages/_<名称>.md` 引用。

**部分作用域规则**：部分内所有选择器（testid / a11y / 结构性）**必须作用域到部分根**，不能是页面级首匹配。例如 `_tweet_card.md`:

```yaml
# ❌ 错：页面级首匹配，会点到 timeline 首条非目标卡片
do: click [data-testid="like"]

# ✅ 对：作用域到 article 根
do: click [data-testid="like"] in article[role="article"] (card 作用域)
```

部分文件顶部写明作用域根一行：

```md
## Card 作用域规则
所有 testid 选择器 必须 作用域到 `article[role="article"]`，不能用页面级首匹配。
```

---

## 工作流字段

每个工作流应回答：

- **目标**：用户界面任务该工作流解决。
- **状态签名**：最小可观察检查点，用于睡眠/压缩后的恢复。
- **最佳路径**：如果覆盖目标，优先选择现有的 `opencli <站点> <命令>` 适配器。
- **备用路径**：如果适配器缺失或失败，则使用浏览器工作流。
- **避免**：浪费回合、触发模态或依赖不稳定选择器的诱人路径。
- **过时标记**：最后验证日期和已知的布局/API 漂移信号。

端点/API 知识应在可用时引用 `endpoints.json` 中的 ID。不要在站点地图文件中重复完整的端点模式。

### 备用 `on_adapter_fail:` 规范（推荐）

备用路径第一行声明触发条件 + `adapter_health_update` 指令，将"为什么走备用"和"标记适配器 suspect"放在一起：

```yaml
on_adapter_fail:
  - adapter_health_update: opencli twitter post -> suspect
  - opencli browser state (verify current page)
  - if not on /home: goto /home
  - action:open_compose in pages/home.md
  - ...
```

比纯步骤列表清晰：consumption skill 看到 `on_adapter_fail:` 键知道这是适配器触发而非入口点备用，指令先执行后续才走步骤。schema v1.2 候选，目前作为 SKILL 指南推荐。

## SITE.md `顶层路由` — 标未覆盖路由

`SITE.md` 的 `顶层路由` 不仅列已覆盖的页面，还应**显式标存在但站点地图不导航**的路由，避免代理默认"站点地图未列 → 不存在"：

```md
## 顶层路由

- /home → pages/home.md
- /search → pages/search.md
- /messages → pages/messages.md（DM，本 PoC v1 不覆盖）   # ← 显式 uncovered marker
- /settings → 不在站点地图范围，代理自探         # ← 同上
```

不写 = 代理不知该路由存在；写 + 标 uncovered = 代理知道存在但站点地图帮不上忙，自己探索。

---

## 红线

- 站点地图是提示；当前浏览器状态为真。
- 不要写入秘密、cookies、用户私有 ID、私信或账户特定值。
- 不要记录绕过验证码、WAF、访问控制、速率限制或付费门禁的方法。
- 不要存储易碎的快照索引（如 `[17]`）作为持久目标。存储语义锚点和恢复指令。
- 不要将未验证的路径描述为事实。使用 `draft` 或 `stale` 标签。
- 草稿放在 `sitemap/draft-<主题>.md`，而不是父级 `~/.opencli/sites/<站点>/sitemap.draft.md` — 后者对 `opencli browser` 站点地图可用性检测不可见。

---

## 详细模式

参见 [`references/sitemap-schema.md`](./references/sitemap-schema.md) 获取完整字段级规范 — `SITE.md` / `pages/<ID>.md` / `workflows/<ID>.md` / `apis.md` / `pitfalls.md` 模式、操作级状态签名、`adapter_health` 枚举（健康 / suspect / broken）、端点引用规则、双层覆盖层语义、草稿位置和 Phase 2 验证规则。
