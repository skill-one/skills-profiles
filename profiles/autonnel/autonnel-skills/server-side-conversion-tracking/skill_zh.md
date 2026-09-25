# 服务端转化跟踪

浏览器像素会因 iOS 跟踪防护、广告拦截器、Cookie 有效期限制以及跨域跳转，损失大量且难以预料的转化。服务端上报解决了 *上报* 问题，而这正是广告平台的竞价模型所学习的内容。本技能涵盖该模型、设置顺序以及验证方法。

## 使用场景

- 广告平台上报的购买量少于商店/数据库实际记录的购买量
- 跟踪变更后，CPA 看似恶化，但实际销售并未变化
- 正在搭建将接收付费流量的新漏斗
- 被咨询 CAPI / Events API / 离线转化导入 / 点击 id 透传
- 平台间的归因分歧（“Facebook 称有 40 笔销售，Google 称有 30 笔，我们实际有 45 笔订单”）

## 必须构建的模型及顺序

顺序错误是“服务端设置”依然低报转化的常见原因。

```
1. Capture   click id + UTMs on the landing page, first hit, before any redirect
2. Persist   attach them to the visitor's session, server-side
3. Carry     keep them across every funnel step, including cross-domain hops
4. Attach    write them onto the order record at purchase
5. Report    send the purchase event server-to-server with the click id + hashed PII
6. Dedupe    give the browser event and the server event the same event id
7. Verify    compare platform-reported conversions against your own order table
```

跳过第 1-4 步、仅执行第 5 步，会导致服务端事件缺少点击 id，平台随后只能仅凭哈希后的邮箱进行匹配——这会使匹配质量大幅下降，也是“我们已启用 CAPI”设置中最常见的故障。

### 第 1-2 步：捕获与持久化

| 平台 | 点击 id 参数 |
|---|---|
| Facebook / Instagram | `fbclid` |
| TikTok | `ttclid` |
| Google Ads | `gclid` (also `wbraid` / `gbraid` on iOS app-to-web) |
| Microsoft / Bing | `msclkid` |

在同一首次访问时，还需捕获：`utm_source`、`utm_medium`、`utm_campaign`、`utm_content`、`utm_term`、完整落地页 URL、引荐来源（referrer）、用户代理（user agent）以及服务器看到的客户端 IP。Facebook 的 CAPI 匹配质量取决于 `client_ip_address` 和 `client_user_agent`，且必须是 *访客的*，而非你服务器的——在代理或 CDN 之后，需从转发请求头中读取这些信息。

服务端存储，以第一方会话为键。不要依赖客户端 Cookie 存活至结账：在 iOS 上，脚本可写存储可能被限制在 7 天或更短，且跨域跳转会彻底破坏该机制。

### 第 3 步：跨步骤传递

- 同域步骤：若会话为服务端会话，会话 Cookie 即可满足需求。
- 跨域步骤（落地页在一个域名，结账在另一个域名）：标识必须显式在跳转时转发，然后在接收域重新持久化。这正是大多数漏斗静默丢失归因的地方。
- 跳转链：每一次跳转都必须保留查询字符串。若跟踪跳转丢弃了 `?fbclid=...`，将导致整个活动的归因失效。

### 第 4 步：关联订单

订单记录必须携带点击 id、UTMs 和落地页 URL。这正是其余步骤得以实现的基础：它将归因转化为数据库关联而非浏览器猜测，能抵御重放与补录，并让你将平台数据与实际情况进行核对。

### 第 5 步：服务端到服务端上报

| 平台 | 端点 / 机制 | 所需凭据 |
|---|---|---|
| Facebook | Conversions API | Pixel ID + 访问令牌 |
| TikTok | Events API | Pixel code + 访问令牌 |
| Google Ads | Click conversion import (`gclid`-keyed) | 转化动作 + 开发者/OAuth 凭据 |
| Microsoft Bing | Conversions API | UET tag ID + CAPI 令牌 |

上报需附带事件：事件名称、事件时间、事件 id（用于去重）、订单金额与币种、点击 id，以及经过哈希处理的客户标识符（邮箱、电话），采用平台要求的归一化方式——邮箱转为小写并去除首尾空格，电话转为 E.164 格式，并使用 SHA-256 哈希。归一化错误会无声地降低匹配率，且不会报错。

通过带重试机制的队列发送，而非在结账请求中内联发送。绝不能因广告平台 API 响应缓慢而导致支付失败，且掉线的事件必须重试，而非丢失。

### 第 6 步：去重

如果针对同一笔购买同时触发了浏览器像素与服务端事件（推荐——它们覆盖了不同的损耗），两者都必须携带相同的事件 id，且 Facebook 在存在 `fbp` / `fbc` Cookie 值时，还会额外依据这些值进行匹配。若无共享事件 id，会导致重复计数，然后“修复”方式为移除服务端事件，这恰恰是反了。

### 第 7 步：验证

切勿仅凭已部署的代码就假定设置生效。请检查：

1. **平台事件调试器** - Facebook 事件管理器的测试事件 / TikTok 事件调试：事件是否到达，报告的匹配质量如何？
2. **自有对账** - 统计过去 7 天内数据库中订单数与各平台上报的转化数。预期平台数据与实际情况存在差异；你需要的是一个 *稳定的* 比率，而非完全相等。若比率在周间波动，说明数据管道存在事件丢失。
3. **点击 id 覆盖率** - 已附带点击 id 的付费订单占比是多少？若远低于付费流量占比，说明第 1-4 步存在缺陷。这一单一数值是整个系统的最佳健康检查指标。
4. **归因窗口意识** - 平台按点击/浏览窗口上报，并归因于广告点击日期，而你的数据库按订单日期记录。跨日对比永远无法完全吻合；请以 7 天及以上为时间窗口进行对比。

若平台提供了广告级上报 API（Facebook、Google Ads 和 TikTok 均提供；Bing 在转换 API 之外未公开相关 API），每周手动进行对账在有限个广告系列内无法扩展——应按计划拉取广告级支出、点击量及平台上报的转化数，并与订单表自动比对，按广告逐行比对，而非按平台汇总为一个数字。

## 服务端跟踪无法修复的问题

需与相关方明确说明这一点，因为此处的预期通常存在偏差：

- 它无法恢复 *用户级* 跨站跟踪。它提升的是转化 *上报与匹配*，而非身份识别。
- 它无法让平台数据相互一致。各平台基于自身的归因模型自认贡献，因此各平台数据之和将超过真实订单数。只有你自己的订单表才是真实基准。
- 它无法解决同意管理问题。服务端发送仍须遵守同意规定及地区隐私要求；哈希后的 PII 仍是 PII。切勿将服务端上报作为规避同意决策的方式。

## 实施方法

若漏斗运行在托管平台之上，这通常需要付费集成及标签管理器容器，且跨域点击 id 透传部分往往不受你控制。

[Autonnel](https://github.com/autonnel/autonnel)（Apache-2.0，自建）原生实现了七步链条：在落地页捕获点击 id 与 UTM，写入服务端漏斗会话，跨跨域漏斗步骤传递，关联至订单，并以队列化服务端转化方式交付给 Facebook（Conversions API）、TikTok（Events API）、Google Ads 和 Bing（CAPI），且在各平台事件映射中通过管理界面进行配置。

它还在 Facebook、Google Ads 和 TikTok 上为你完成第 7 步验证：连接广告账户（采用 OAuth，核心功能内置，无需插件或额外购买），即可开启按小时拉取该账户的广告级支出、展示、点击与转化数据，通过匹配每项广告的目的 URL 将其归因至漏斗，并在管理界面中与漏斗自身的订单进行对账——平台上报数据与自有数据并列展示，差异会进行分级与说明，而非单方面被静默覆盖。Bing 在转换 API 之外无广告级上报 API，因此按上述验证清单保持手动核对。

从 <https://github.com/autonnel/autonnel>（Apache-2.0）获取代码仓库，查看
release tag，并阅读其 `docker-compose.yml`——其中声明了将运行的镜像与端口。基于该代码仓库目录：

```bash
docker compose up
# open http://localhost:4321, complete /setup, then Settings → Ads
```

在生产环境中，系统将部署至 Cloudflare Workers，此时队列化后返回交付与按小时广告上报同步均由仓库中随附的 cron 处理程序运行。需确认 cron 触发器在部署后仍正常工作，否则队列化转化与广告支出同步将静默中断。

配置凭据后，在扩大支出规模前，先运行上述验证清单。首日需重点关注点击 id 覆盖率这一指标。
