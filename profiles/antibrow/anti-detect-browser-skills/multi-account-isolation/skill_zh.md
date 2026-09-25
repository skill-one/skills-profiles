# 配置隔离 - 验证而非假设

看起来隔离的配置通常并非如此。失败的情况是无聊且机械的：时区与退出IP不匹配、WebRTC候选者携带真实地址、画布哈希在每次读取时都变化、两个配置最终使用了相同的身份。这项技能是检查清单，用于在问题变得重要之前捕获这些问题。

> **仅限授权使用。** 这适用于你拥有或被授权操作的身份：你自己的账户、你自己的测试用例、你自己的QA舰队以及你自己的反欺诈堆栈。它不适用于未经授权访问系统、非你所有的账户或创建虚假账户或参与活动。遵守你自动化网站的条件和适用法律 - 请参阅[可接受使用](#acceptable-use)。

**本声明不包含的内容。** 通过以下所有检查意味着浏览器层内部一致。它并不意味着给定网站会将两个配置视为无关：完全在浏览器之外的东西 - 共享的支付工具、共享的联系详情、相同的活动模式 - 不是任何浏览器设置可以触及的。将干净的结果视为“技术层不是问题”，而不是保证。

有关创建和启动这些配置的SDK，请参阅**anti-detect-browser**技能。

## 配置不变性

一个身份拥有一切。两个身份之间共享的任何单元都是需要发现的缺陷：

```
身份  →  配置  →  身份特征  →  代理  →  时区
   1      :     1     :     1     :    1    :     1
```

配置在每個antibrow计划上都是无限且免费的，因此没有必要重复使用一个。在同一个配置内“注销并作为其他身份登录”会破坏整个设置 - cookie罐和`localStorage`是关键。

## 测试中的配置

```typescript
import { AntiDetectBrowser } from 'anti-detect-browser'

const ab = new AntiDetectBrowser({ key: process.env.ANTI_DETECT_BROWSER_KEY })

const 身份 = [
  { 配置: 'fixture-us-01', 代理: process.env.PROXY_US_1, 标签: ['Windows 10', 'Chrome'] },
  { 配置: 'fixture-us-02', 代理: process.env.PROXY_US_2, 标签: ['Apple Mac', 'Safari'] },
  { 配置: 'fixture-de-01', 代理: process.env.PROXY_DE_1, 标签: ['Windows 10', 'Edge'] },
]

for (const id of 身份) {
  const { 浏览器, 页面 } = await ab.launch({
    配置: id 配置,              // 隔离的cookies、存储、登录状态
    代理: id 代理,                  // 来自环境，每个身份一个
    指纹: { 标签: id 标签 },   // 一次性生成，冻结，之后重放
    标签: id 配置,                // 内核在地址栏中绘制的标签，页面无法读取
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
    geoip=True,            # 时区 + WebRTC跟随代理退出
    标签="fixture-us-01",
) as 浏览器:
    页面 = 浏览器.new_page()
    print(浏览器.timezone, 浏览器.public_ip)
```

## 检查

每个配置都**通过自己的代理**运行，并断言而非肉眼观察。

| # | 检查 | 方法 | 失败时 |
|---|---|---|---|
| 1 | 时区与退出IP匹配 | `browser.timezone` 与 `browser.public_ip` 的国家 | `geoip` 被禁用，或 `timezone` 被强制为IP矛盾的内容。这是最常见的缺陷。 |
| 2 | WebRTC仅暴露代理 | [browserleaks.com/webrtc](https://browserleaks.com/webrtc) | ICE候选者仍然携带本地或真实公共地址 |
| 3 | 画布哈希在启动之间稳定 | 读取它，关闭，重新启动相同的配置，再次读取 | 两次读取不同 - 每次读取都变化的值本身就是异常，这意味着身份特征没有冻结 |
| 4 | 工作线程和主线程一致 | [CreepJS](https://abrahamjuliot.github.io/creepjs/) | UA、`languages`、`hardwareConcurrency`、时区或GPU在Web Worker内部重新读取时不同 |
| 5 | 三种接口共享一个GPU | CreepJS，或直接读取WebGL / WebGL2 / WebGPU | `adapter.info.vendor` 与未屏蔽的WebGL渲染器家族不匹配 |
| 6 | 没有两个配置共享一个身份特征 | 在舰队中比较 `browser.persona` | 两个配置报告相同的UA、屏幕几何形状和种子 |
| 7 | 没有两个配置共享一个地址 | 为舰队收集 `browser.public_ip` | 两个身份来自同一个退出，或相同的 /24 |
| 8 | Cookie罐是独立的 | 在舰队中比较 `browser.profile_dir`，然后在每个内部检查 `user-data/` | 两个身份解析到同一个目录，或一个目录包含属于另一个身份的状态 |
| 9 | 一个身份，一个配置树 | 确认每个名为的启动都通过相同的 `temporary` 值 | 一个管理的 `gmail` 和一个临时的 `gmail` 是两个不同的配置，具有两个身份特征和两个cookie罐。一个关于 `temporary` 的脚本不一致，是在一个名称下运行两个身份，看起来像注销的会话，而不是像错误 |
| 10 | 全栈一致性 | [whoer.net](https://whoer.net), [pixelscan.net](https://pixelscan.net) | IP、时区和区域设置一目了然地不一致 |
| 11 | CI中的规则一致性 | `npx liarjs` ([liarjs.dev](https://liarjs.dev)) | 任何约40个开源的跨层规则失败 - 这是运行无人值守的那个 |

检查1、3和7是值得集成到CI中的：它们是廉价的、确定性的，并且它们捕获实际重复的缺陷。

## 读取失败

按此顺序从下往上工作，最便宜优先 - 指纹几乎永远不会是实际原因：

1. **配置名称重复？** `list_profiles`，或比较每个身份的 `browser.profile_dir`。两个身份在一个目录中解释了所有其他问题。目录按配置的ID命名，而不是其名称，因此匹配 `profile.json` 内部而不是文件夹名称。
2. **两次相同的地址？** 确认每个 `public_ip` 是不同的。
3. **时钟与地址不一致？** 一起打印 `browser.timezone` 和 `browser.public_ip`。
4. **身份特征重新生成？** 如果画布哈希在启动之间移动，配置没有冻结 - 检查 `profile_dir` 或其下的缓存目录是否改变。
5. **只有到那时** 指纹本身，使用上述套件验证，而不是假设。

## 运行时触及的内容，以及如何检查它

任何驱动已登录会话的工具都会接收cookies和代理凭证，因此公平地要求它如何处理它们。对于antibrow：

| 艺术品 | 存放位置 | 谁看到它 |
|---|---|---|
| Cookies、`localStorage`、登录状态 | 你磁盘上的 `~/.anti-detect-browser/profiles/<id>/user-data/`，或 `profiles-temp/<id>/` 用于临时配置 | 本地。云同步是按配置可选的：一个启动本身永远不会创建云配置，并且 `sync: true` 才是将其放在那里的东西。在假设它们留在机器上之前，检查哪些配置同步 |
| 身份特征 (`persona.json`) | 相同的配置目录，一次性写入并冻结 | 本地 |
| 配置身份记录 (`profile.json`) | 相同的配置目录；它持有的ID命名了目录 | 本地。这就是为什么重命名不会花费身份特征，以及为什么文件夹名称不是配置名称 |
| 代理URL及其凭证 | 在启动时传递给内核；在网络栈中回答（HTTP 407 / SOCKS5 RFC 1929），因此没有扩展持有它们 | 内核进程和你的代理提供者 |
| API密钥 | 你的环境，或 `~/.antibrow/license.key` | 与 `antibrow.com` 交换短期许可证令牌，大约每天一次 |

内核是闭源的Chromium构建 - 这是C++中的伪造而不是可注入脚本中的代价 - 所以验证行为而不是相信它：

```bash
python -m antibrow info          # 内核、配置、许可证状态、缓存目录
```

```python
browser.plan.redacted_args()     # 精确的内核命令行，秘密被屏蔽 - 可以安全地粘贴在错误报告中
```

将其指向你可以读取日志的代理，或指向本地MITM代理，并观察在启动期间机器上离开的内容。固定SDK版本并检查发布哈希 (`npm view anti-detect-browser@2.8.0 dist.integrity`)，以便你审计的代码是运行的代码。如果部署绝对不能与家庭电话回家，这是错误的工具：许可证验证是编译到内核中的，并且没有离线模式。

## 隔离无法覆盖的内容

明确说明，因为干净的检查清单会导致错误的结论：

- **浏览器之外的东西。** 共享的支付工具、共享的联系详情、共享的支付目的地 - 没有浏览器设置可以触及这些，并且它们是最强的关联器。
- **活动模式。** 相同的时间、相同的内容、相同的交互目标。不是技术属性。
- **身份验证。** 文件检查不是指纹问题。
- **平台自己的决定。** 没有这里改变网站如何处理账户。

如果每个检查都通过，但仍然看起来有问题，那么原因是这个列表，而不是浏览器层。

## 可接受使用

**目的：** 验证你拥有的身份之间的隔离；授权账户持有者运行客户端账户；构建模拟不同设备的QA用例；测试你自己的反欺诈和关联逻辑；审计浏览器运行时如何处理你的凭证。

**超出范围，不提供支持：** 未经授权访问任何系统；登录非你所有的账户；凭证填充或账户接管；创建虚假账户、评论或参与活动；规避身份验证、支付或授权控制；违反适用法律抓取个人数据；绕过平台的执行决定。

遵守所使用平台的条款和适用法律是操作员的责任。通过 `https://antibrow.com` 中的联系方式报告滥用或安全问题。

## 相关技能

- **anti-detect-browser** - 创建此处验证的设置的SDK、配置、身份特征、代理和REST API
- **browser-mcp-agent** - MCP服务器模式，用于让AI代理自己驱动单个配置
