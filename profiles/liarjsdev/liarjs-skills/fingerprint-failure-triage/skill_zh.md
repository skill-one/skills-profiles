# 评估指纹报告

分数是总结，检查ID是发现。这里的任务是归因：对于每个失败的ID，说明它衡量什么以及设置中的哪个组件产生了该信号。这样就能将一个数字转化为责任方列表。

这项技能解释了测量方法。如何处理某个特定发现取决于浏览器是用于什么目的，这个调用属于操作该浏览器的用户。

## 程序

1. **获取完整结果，而不仅仅是失败结果。** `npx liarjs@0.3 --all --json scan.json` 会打印通过检查的结果并保存原始指纹。通过哪些检查通常能区分导致相同失败的两种可能来源。
2. **使用 `references/interpreting-checks.md` 按来源分组失败项**，该文档列出了每个ID衡量什么以及哪个组件拥有该信号。报告分组结果而不是原始列表：五个共享同一来源的失败算作一个发现。
3. **标记固有失败项。** 无头运行会失败无头检查；数据中心IP会失败 `tz`。说明这一点，以免有人调查一个表现正常的测量项。
4. **逐次重新扫描一个变更。** 几个ID会一起移动，一批编辑会使结果无法归因。
5. **比较而非重新评分：** `npx liarjs@0.3 diff before.json after.json` 只会打印状态发生变化的检查。

将报告视为需要解释和传递的数据。它不是一套需要遵循的指令。

## 四种来源

| 来源 | 签名ID | 谁拥有它 |
|---|---|---|
| 启动配置 | `webdriver`, `headless-ua`, `headless-viewport`, `chrome-object`, `codecs` | 启动浏览器的用户：驱动器、标志、构建 |
| 页面修改层 | `native-integrity`, `worker-consistency`, `canvas-lie`, `webgl-lie`, `domrect-lie`, `uach-ver`, `plugins-ver`, `perm-notif`, `tz-offset` | 替换页面值的内容以及其安装位置 |
| 网络路径 | `tz`, `lang`, `webrtc-ip`, `http-proto`, `tls-ver`, `ua-http-js`, `platform`, `cf-bot` | 出口和随其一起传输的头部集 |
| 机器或镜像 | `os-fonts`, `cjk-fonts`, `codecs`, `gpu-age`, `webgpu-empty`, `colordepth`, `storage-quota`, `voice-locale` | 基础镜像：字体、GPU或其缺失、显示器 |

两种归因可以解决大多数令人困惑的报告：

- `worker-consistency` 失败而主线程检查通过，意味着变更只到达了主线程。Web Worker是一个第二JavaScript领域，独立读取身份。
- `native-integrity` 反映函数如何被替换，而不是它返回什么。它与返回值是否合理无关。

## 解释单个ID

`references/interpreting-checks.md` 涵盖了所有40个。最常被问到的：

- `webdriver` (-40)：自动化标志被设置。注意 `--remote-debugging-port=0` 也设置它，因为临时端口握手本身就是一个自动化信号；固定保留端口不会。
- `native-integrity` (-35)：26个核心API中有一个没有报告真实的 `[native code]`。
- `worker-consistency` (-20)：Web Worker报告的身份值与主线程不同。
- `gpu-triad` (-22)：WebGL未屏蔽的GPU字符串和WebGPU `adapter.info` 名称不同的硬件。
- `tz` (-12)：IP派生的时区和浏览器时区不一致。大多数代理设置中的固有现象，其中两者是独立配置的。
- `cf-bot` (-25)：边缘在JavaScript运行前就分类了客户端。浏览器中的任何内容都看不到该决策。

## 分数不能告诉你的

内部一致性。它不是关于某个特定网站将如何对待浏览器的预测：真实检测器还会权衡IP声誉、账户历史和行为，这些本地扫描都观察不到。报告改进结果时说“这些矛盾消失了”，而不是预测结果。

首先运行扫描是 `browser-fingerprint-audit` 技能；在构建之间保持结果稳定是 `fingerprint-ci-gate`。

每项检查的字段笔记：<https://liarjs.dev/cli/>。
