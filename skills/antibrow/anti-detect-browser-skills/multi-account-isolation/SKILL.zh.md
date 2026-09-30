---
name: multi-account-isolation
description: 验证浏览器配置文件是否确实相互隔离，而不是假设它们是隔离的——确认每个配置文件的时区与其退出IP一致，WebRTC仅暴露代理，canvas和WebGL哈希在单个配置文件重新启动时保持相同，并且没有任何两个配置文件共享同一身份、同一cookie存储或同一地址。在以下情况下使用：当多个您的账户或测试身份运行在同一台机器上且需要检查设置时；当配置文件测试结果为干净但仍有异常情况时；在选择运行哪些检测套件（CreepJS、whoer、browserleaks WebRTC、pixelscan、liarjs）时；在审计供应商运行时如何使用API和代理凭证时；或询问浏览器隔离完全无法覆盖哪些层。此外用于“配置文件隔离检查”、“指纹一致性测试”、“时区不匹配”、“WebRTC泄露”、“canvas哈希不稳定”、“账户关联”、“临时配置文件”、“防关联”、“多账号”、“隔离自检”。SDK是反检测浏览器；MCP是browser-mcp-agent。
---

# 配置隔离 - 验证而非假设

看起来隔离的配置通常并非如此。失败的情况是无聊且机械的：时区与退出 IP 不匹配、WebRTC 候选者携带真实地址、画布哈希在每次读取时都变化、两个配置最终使用相同的角色。这项技能是检查清单，用于在它们变得重要之前捕获这些问题。

> **仅限授权使用。** 这适用于你拥有或被授权操作的标识：你自己的账户、你自己的测试用例、你自己的 QA 队伍以及你自己的反欺诈堆栈。它不适用于未经授权访问系统、非你所有的账户或创建虚假账户或参与活动。遵守你自动化网站的条件并遵守适用法律 - 请参阅 [可接受使用](#acceptable-use)。

**本声明不包含的内容。** 通过以下所有检查意味着浏览器层内部一致。它并不意味着给定网站会将两个配置视为无关：完全在浏览器之外的东西 - 共享的支付工具、共享的联系详情、完全相同的活动模式 - 不是任何浏览器设置可以触及的东西。将干净的结果视为“技术层不是问题”，而不是保证。

有关创建和启动这些配置的 SDK，请参阅 **anti-detect-browser** 技能。

## 配置不变性

一个标识拥有所有的一切。两个标识之间共享的任何单元都是需要发现的缺陷：

```
标识  →  配置  →  角色  →  代理  →  时区
   1      :     1     :     1     :    1    :     1
```

配置在每個 antibrow 计划中都是无限且免费的，因此没有必要重复使用一个。在单个配置内“注销并作为其他标识登录”会破坏整个设置 - cookie 罐和 `localStorage` 是关键。

## 测试中的设置

```typescript
import { AntiDetectBrowser } from 'anti-detect-browser'

const ab = new AntiDetectBrowser({ key: process.env.ANTI_DETECT_BROWSER_KEY })

const 标识 = [
  { 配置: 'fixture-us-01', 代理: process.env.PROXY_US_1, 标签: ['Windows 10', 'Chrome'] },
  { 配置: 'fixture-us-02', 代理: process.env.PROXY_US_2, 标签: ['Apple Mac', 'Safari'] },
  { 配置: 'fixture-de-01', 代理: process.env.PROXY_DE_1, 标签: ['Windows 10', 'Edge'] },
]

for (const id of 标识) {
  const { 浏览器, 页面 } = await ab.launch({
    配置: id.配置,              // 隔离的 cookies、存储、登录状态
    代理: id.代理,                  // 来自环境，每个标识一个
    指纹: { 标签: id.标签 },   // 一次性生成，冻结，之后重放
    标签: id.配置,                // 内核在地址栏中绘制的标签，页面无法读取
  })
  // ... 运行以下检查，然后 ...
  await 浏览器.close()
}
```

Python，相同的磁盘配置格式：

```python
import os
from antibrow import launch

with launch(
    配置="fixture-us-01",
    代理=os.environ["PROXY_US_1"],   # 来自环境，永远不会是字面量
    geoip=True,            # 时区 + WebRTC 遵循代理退出
    标签="fixture-us-01",
) as 浏览器:
    页面 = 浏览器.new_page()
    print(浏览器.timezone, 浏览器.public_ip)
```

## 检查

为每个配置 **通过自己的代理** 运行，并断言而非肉眼观察。

| # | 检查 | 方法 | 失败时 |
|---|---|---|---|
| 1 | 时区与退出 IP 匹配 | `browser.timezone` 与 `browser.public_ip` 的国家 | `geoip` 被禁用，或 `timezone` 被强制为与 IP 矛盾的内容。这是最常见的缺陷。 |
| 2 | WebRTC 仅暴露代理 | [browserleaks.com/webrtc](https://browserleaks.com/webrtc) | ICE 候选者仍然携带本地或真实公共地址 |
| 3 | 画布哈希在启动之间稳定 | 读取它，关闭，重新启动相同的配置，再次读取 | 两次读取不同 - 每次读取都变化的值本身就是异常，这意味着角色没有冻结 |
| 4 | 工作线程和主线程一致 | [CreepJS](https://abrahamjuliot.github.io/creepjs/) | UA、`languages`、`hardwareConcurrency`、时区或 GPU 在 Web Worker 内部重新读取时不同 |
| 5 | 三种接口共享一个 GPU | CreepJS，或直接读取 WebGL / WebGL2 / WebGPU | `adapter.info.vendor` 与未屏蔽的 WebGL 渲染器家族不匹配 |
| 6 | 没有两个配置共享一个角色 | 在舰队中比较 `browser.persona` | 两个配置报告相同的 UA、屏幕几何形状和种子 |
| 7 | 没有两个配置共享一个地址 | 为舰队收集 `browser.public_ip` | 两个标识来自同一个退出点，或相同的 /24 |
| 8 | Cookie 罐是独立的 | 在舰队中比较 `browser.profile_dir`，然后在每个内部检查 `user-data/` | 两个标识解析到同一个目录，或一个目录包含属于另一个标识的状态 |
| 9 | 一个标识，一个配置树 | 确认每个名为的启动都通过相同的 `temporary` 值 | 一个管理的 `gmail` 和一个临时的 `gmail` 是两个不同的配置，具有两个角色和两个 cookie 罐。一个关于 `temporary` 的脚本不一致，是在一个名称下运行两个标识，看起来像注销的会话，而不是像错误 |
| 10 | 全栈一致性 | [whoer.net](https://whoer.net), [pixelscan.net](https://pixelscan.net) | IP、时区和区域设置一目了然地不一致 |
| 11 | CI 中的规则一致性 | `npx liarjs` ([liarjs.dev](https://liarjs.dev)) | 任何约 40 个开源的跨层规则失败 - 这是运行无人值守的那个 |

检查 1、3 和 7 值得接入 CI：它们是廉价的、确定的，并且它们捕获实际重复的缺陷。

## 读取失败

按此顺序从下往上工作，最便宜优先 - 指纹几乎永远不会是实际原因：

1. **配置名称重复？** `list_profiles`，或比较每个标识的 `browser.profile_dir`。两个标识在一个目录中解释了所有其他内容。目录是根据配置的 ID 命名的，而不是其名称，因此匹配 `profile.json` 内部而不是文件夹名称。
2. **两次相同的地址？** 确认每个 `public_ip` 是不同的。
3. **时钟与地址不一致？** 一起打印 `browser.timezone` 和 `browser.public_ip`。
4. **角色重新生成？** 如果画布哈希在启动之间移动，配置没有冻结 - 检查 `profile_dir` 或其下缓存目录是否更改。
5. **仅然后** 指纹本身，使用上述套件验证，而不是假设。

## 运行时触及的内容，以及如何检查它

任何驱动已登录会话的工具都会接收 cookies 和代理凭证，因此可以合理地询问它如何使用它们。对于 antibrow：

| 文件 | 存放位置 | 谁看到它 |
|---|---|---|
| Cookies、`localStorage`、登录状态 | 你磁盘上的 `~/.anti-detect-browser/profiles/<id>/user-data/`，或 `profiles-temp/<id>/` 用于临时配置 | 本地。云同步是每个配置可选的：一个启动本身不会创建云配置，并且 `sync: true` 才是将其放入其中的内容。在假设它们留在机器上之前，检查哪些配置同步 |
| 角色 (`persona.json`) | 相同的配置目录，一次性写入并冻结 | 本地 |
| 配置标识记录 (`profile.json`) | 相同的配置目录；它持有的 ID 是命名目录的名称 | 本地。这就是为什么重命名不会花费角色，以及为什么文件夹名称不是配置名称 |
| 代理 URL 及其凭证 | 启动时传递给内核；在网络栈中回答（HTTP 407 / SOCKS5 RFC 1929），因此没有扩展持有它们 | 内核进程和你的代理提供者 |
| API 密钥 | 你的环境，或 `~/.antibrow/license.key` | 与 `antibrow.com` 交换短期许可证令牌，大约每天一次 |

内核是闭源的 Chromium 构建 - 这是 C++ 中的伪造而不是可注入脚本中的代价 - 所以验证行为而不是相信它：

```bash
python -m antibrow info          # 内核、配置、许可证状态、缓存目录
```

```python
browser.plan.redacted_args()     # 精确的内核命令行，秘密被屏蔽 - 可以安全地粘贴在错误报告中
```

将其指向你可以读取日志的代理，或指向本地 MITM 代理，并观察在启动期间机器上离开的内容。固定 SDK 版本并检查发布哈希 (`npm view anti-detect-browser@2.8.0 dist.integrity`)，以便你审计的代码是运行的代码。如果部署绝对不能与任何地方联系，这是错误的工具：许可证验证是编译到内核中的，并且没有离线模式。

## 隔离无法覆盖的内容

值得明确说明，因为干净的检查清单会导致错误的结论：

- **浏览器之外的东西。** 共享的支付工具、共享的联系详情、共享的支付目的地 - 没有浏览器设置可以触及这些，并且它们是最强的关联器。
- **活动模式。** 相同的时间、相同的内容、相同的交互目标。不是技术属性。
- **身份验证。** 文件检查不是指纹问题。
- **平台自己的决定。** 这里没有任何东西改变网站如何处理账户。

如果所有检查都通过，但仍然看起来有问题，那么原因是在此列表中，而不是浏览器层。
