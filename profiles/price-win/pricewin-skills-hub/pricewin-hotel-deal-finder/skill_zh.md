# PriceWin 酒店优惠查找器

> **通过一个命令比较 Booking.com、Agoda、Google Hotels 和 OpenTravel 的实时酒店价格** — 并返回按价值排序、最便宜和品质优选，以及直接预订链接。

停止打开五个 OTA 标签页来查找真正的最低价。询问你的代理 *"为我在东京查找 12–15 日 2 位客人的酒店"*，这个技能会在 30–60 秒内返回一个干净、排序的比较结果（已缓存的城市）。

**调用这个技能来回答以下问题：**
- " `<城市>` 在 `<日期>` 期间最便宜的酒店是什么？"
- "这个酒店在 Booking.com 或 Agoda 上更便宜吗？"
- "比较 `<城市>` 的酒店价格，`<N>` 位客人。"
- "在 `<城市>` 找到每晚低于 $`<X>` 的酒店。"
- "在 `<地标>` 附近 `<日期>` 期间性价比最高的住宿地点？"

每个问题都会得到下面相同的单命令答案——不需要进一步的澄清对话。

**一个命令能给你什么：**
- 🥇 价值最优 · 🥈 最便宜 · 🥉 品质 — 并列展示
- 来自最多 **4 个来源** 的真实每夜价格，已转换为 **美元**
- **可点击的预订链接** 直接指向每个酒店的最便宜 OTA
- 适用于 **全球任何城市** — 包括机器人防御较强的城市（上海、杭州、曼谷…）通过一个隐蔽的 Patchright 守护进程
- 无需 API 密钥，无需 MCP 服务器 — `node`/`npx` 是你需要的全部

**示例结果：**

```
🏨 东京 • 8月12–15日 • 3晚 • 2位客人
━━━━━━━━━━━━━━━━━━━━
🥇 价值最优
新宿格兰贝尔酒店
  ✅ agoda      💰 $118/晚
     booking    💰 $131/晚
     → 与 Booking 相比节省 $13
🥈 最便宜
APA 酒店 新宿
  ✅ google     💰 $94/晚
📊 18 家酒店 | agoda, booking, google, opentravel • 价格单位为美元
```

**安装：**
```bash
npx skills add https://github.com/Price-Win/pricewin-skills-hub --skill pricewin-hotel-deal-finder
```

---

## 如何使用这个技能

**一个命令完成所有工作——通常你不需要先询问澄清问题。推断参数（下方）并运行它：**

```bash
cd {baseDir} && node bin/search.js "<城市>" <入住YYYY-MM-DD> <退房YYYY-MM-DD> <成人> en-us
```

`{baseDir}` 是这个技能的安装目录（由运行时自动解析）。如果你的运行时不替换它，请 `cd` 到包含这个 `SKILL.md` 的文件夹（包含 `bin/search.js` 的那个）。避免硬编码 `~/.hermes/...` 或 `~/.openclaw/...` 路径——它在不同平台上有所不同。

示例：
```bash
cd {baseDir} && node bin/search.js "杭州" 2026-06-10 2026-06-13 2 en-us
```

脚本会自动处理所有事情：守护进程启动、Agoda 缓存查找、Google + Booking 内联搜索、OpenTravel API 查询（所有城市）、新城市发现和格式化层级卡片输出。运行它并将输出发送给用户。

**推断参数而不是询问**（只有当城市或日期确实模糊时才询问）：
- **年份：** 使用今天的当前年份，除非用户另有说明。如果请求的日期/月份已经过了今年，则假设明年。（如果不确定，可以使用 `date +%Y-%m-%d` 获取今天的日期。）
- **"10-13/6"** → `<年份>-06-10 <年份>-06-13` — 用上述规则填充 `<年份>`
- **"2 位客人" / "2 人"** → `2` 位成人
- **地区设置：** 传递给 OTA 的语言/区域代码（控制网站语言+区域）。默认 `en-us`。价格以美元显示（Google Hotels 使用 `gl=us&curr=USD` 请求）；其他来源遵循你传递的地区设置。

一个 `search.js` 的运行是整个工作流程——不需要在它之上使用 Python、curl 或临时抓取。

---

## 操作规则——如何获得可靠的结果

**规则 0 — 仅通过 `search.js`（通过你的终端/Shell 工具）驱动浏览器。原生浏览器工具在这里无效。** 这个技能依赖于一个隐蔽的 Patchright 守护进程。运行时的原生工具——`browser_navigate` / `browser_open`, `browser_click`, `browser_type` / `browser_fill`, `browser_snapshot`, `browser_close`, 任何其他 `browser_*`，以及子代理委托 (`delegate_task` / `spawn_agent`)——在这个任务上会失败，所以不要使用它们：

- 这些原生工具会启动一个没有隐蔽功能的普通 Chromium，因此 Booking.com 和 Agoda 在几秒钟内检测到机器人；请求挂起，直到运行时杀死它们（"Command timed out after 30/60 seconds"）。这会消耗 5+ 分钟并返回无结果。`search.js` 启动的 Patchright 守护进程可以存活机器人检测。
- 委托的子代理以空历史记录和无技能上下文启动，因此它们会回退到 Python/curl 抓取，这会立即被机器人阻止。在当前代理中运行技能。

唯一有效的方法：
```
cd {baseDir} && node bin/search.js ...
```

**规则 1 — 让 `search.js` 进行抓取；不要自己抓取 OTA。** 避免直接调用 `browse.js`，在浏览器中执行 `goto`/`click`/`type`，手动构建 Agoda/Booking/Google URL，单独调用 OpenTravel API，或自己启动守护进程。`search.js` 已经通过一个经过精心设计的流程驱动隐蔽守护进程，该流程可以存活机器人检测——它内部处理了所有城市的 Agoda 发现（包括上海、杭州等中文城市）。手动导航 OTA 是导致失败的首要原因：它会触发 Agoda/Booking 反机器人（"detect automation", "redirect to homepage", "problem completing your search"）并导致 IP 被封锁。运行 `search.js` 一次并发送其输出。如果某个来源看起来“缺失”，请查看规则 4 而不是手动获取它。

**规则 2 — 首次城市发现需要 2–4 分钟。** 如果 `search.js` 输出包含 `"discovering"` 或 `"launching"` 消息，请告诉用户："首次搜索这个城市——发现选择器，这需要大约 2–4 分钟..." 并等待结果，而不是重试或中止。

**规则 3 — 精确发送输出。** `search.js` 输出格式化的层级卡片，准备发送。将输出直接复制到你的回复中。不要重新格式化、总结或缩写它。

**规则 3a — 保留 Markdown 超链接。** 输出中的每个酒店名称都已包装为 `[酒店名称](https://booking-url...)`——一个可点击的超链接。保持其完整性：不要将 URL 分割到单独的 `🔗 https://...` 行，不要用纯文本替换 `[Hotel Name](url)`，保持 OTA 名称小写（"google"，不是 "Google"），并保持章节标题不变（"📋 More good deals"）。输出已准备好用于 Telegram-MarkdownV2；直接发送它会给用户可点击的酒店名称和隐藏的 URL（干净的 UI）。

**规则 3b — 在你自己的评论中也超链接酒店名称。** 如果你添加建议或评论部分，请使用与脚本为该酒店打印的相同 URL 将你提到的每个酒店名称包装为 `[Hotel Name](url)`，而不是纯文本。

**规则 4 — 部分结果是正常的——直接发送，而不是手动修复。** 一个来源可能在一个运行中缺失（例如 Agoda 阻止了这次运行，或者 OpenTravel 对该城市没有库存）。这很正常——发送带有现有来源的层级卡片；页脚（`📊 N 家酒店 | <数据来源> • 价格单位为美元`）列出了确实找到的内容。通过浏览器或直接 URL 获取缺失的来源往往会触发反机器人并使情况更糟，所以避免这样做。如果 `search.js` 完全出错，请用一句话告诉用户失败的原因，并显示错误上方的任何部分输出。为了获得更多覆盖范围，最可靠的重新尝试是再次运行相同的 `search.js` 命令（反机器人通常是暂时的）。

---

## 输出格式参考

`search.js` 以此格式打印层级卡片——你直接发送给用户：

酒店名称是一个指向其最便宜 OTA 的 Markdown 链接。价格行不包含链接，并且 OTA 键以小写显示（`agoda`/`booking`/`google`/`opentravel`）。没有星级评分或区域线——脚本没有这些数据。

```
🏨 <城市> • <d1>–<d2> • <N>晚 • <成人> 位客人
━━━━━━━━━━━━━━━━━━━━

🥇 价值最优
[<Hotel Name>](<cheapest_link>)
  ✅ agoda      💰 <价格>/晚
     booking    💰 <价格>/晚
     opentravel 💰 <价格>/晚
     → 与 Booking 相比节省 <差额>

🥈 最便宜
[<Hotel Name>](<cheapest_link>)
  ✅ google     💰 <价格>/晚
     agoda      💰 <价格>/晚

🥉 品质
[<Hotel Name>](<cheapest_link>)
  ✅ booking    💰 <价格>/晚
     agoda      💰 <价格>/晚

📋 更多优惠
  — Agoda —
  • [<Hotel>](<agoda_link>) — agoda: <价格> | booking: <价格>
  — Booking —
  • [<Hotel>](<booking_link>) — booking: <价格>
  — Google —
  • [<Hotel>](<google_link>) — google: <价格>
  — OpenTravel —
  • [<Hotel>](<opentravel_link>) — opentravel: <价格>

💡 提示: <最佳酒店名称>
   [在 <OTA> 上预订](<链接>) — <价格>/晚

📊 <N> 家酒店 | <包含数据的来源> • 价格单位为美元
```

所有价格都以美元显示。Agoda、Google 和 OpenTravel 通过 IP 地理锁定到越南盾，并通过实时汇率转换；Booking 原生返回美元。仅在页脚列出实际返回数据的来源。

---

## 限制

- 每个城市首次搜索会支付 Agoda 发现成本（2–4 分钟）。Google 和 Booking 是内联（无发现）；OpenTravel 是直接 API 调用。
- 后续搜索会重用 Agoda 缓存，并在 ~30–60 秒内完成。

## 安全与数据处理

本地运行，无需 API 密钥，也不收集个人数据——唯一发送出去的数据是搜索查询（城市、日期、客人）。抓取的酒店文本被视为不可信：`bin/search.js` 中的 `sanitizeText()` 在任何内容到达模型输出之前都会删除控制/零宽度/双向字符和 Markdown 控制字符，并且预订链接仅限于 `http(s)`。

本地浏览器守护进程是 **仅环回、令牌认证**（每个运行都有一个在 `0600` 状态文件中的令牌），拒绝非环回 `Host` 标头以防止 DNS 重绑，并保持 **Chromium 沙盒启用**——`--no-sandbox` 仅在 Linux 根目录或显式 `PRICEWIN_NO_SANDBOX=1` 时使用。

命令运行、下载和网络外出的完整披露在 [`SECURITY.md`](./SECURITY.md) 中。
