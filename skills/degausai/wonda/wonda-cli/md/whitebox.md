# wonda-cli (`degausai/wonda/wonda-cli`)

## whitebox

- 装好并认证：安装 wonda CLI (npm/brew)，wonda auth login 或 WONDA_API_KEY 完成登录，wonda auth check 验证。
- 付费门禁：任何产品命令干活前，CLI 先实时调 GET /api/v1/auth/access 校验付费计划，校验不过直接拒绝 (fail closed)。
- 设定上下文：wonda use --org/--project 绑定钱包与花费标签；引擎策略 (auto/my_machine/cloud) 决定走本地 relay 还是云端执行。
- 分派执行：生成 (`image/generate`/`video/generate`/语音 TTS)、媒体合成、发布；平台读写走 `--via wab` 反检测浏览器或 `--via cookies` 本地 cookie。
- 产出与核算：用 `--json`/`--quiet`/`-o`/`--jq` 控制输出并下载产物；`wonda usage` 按项目/org 汇总花费。

- 强制付费校验：所有产品面（生成、发布、抓取、浏览器自动化、技能…）在执行前都过一次实时 entitlement 检查 (GET /api/v1/auth/access)，失败即 fail closed 并返回 403 paid_plan_required；匿名/Free 档只放行 auth、配置、定价、关停等非产品命令。外部依赖：Wonda HTTP API。
- 平台自动化双通道：`--via cookies` 读本地扁平 JSON cookie 库（快，不起浏览器）；`--via wab` 起 WAB——一个 undetected Playwright fork 的反检测 Chromium，每个 persona 一个持久 headful 浏览器，登录在 WAB 内完成、cookie 存浏览器 profile 而非 config 文件，保证会话与浏览器指纹一致。外部依赖：反检测 Chromium (undetected Playwright fork)。
- 本地 relay + 凭据隔离：engine policy `auto`（relay 在线优先本地，否则云端）/`my_machine`（relay 离线时必须询问，不静默降级）/`cloud`；本地 relay 让远程 connector（Claude web 等）在用户自己的 Mac + 住宅 IP 上执行动作，relay 用作用域受限的 `wrelay_...` 凭据、存 macOS Keychain，用户不粘贴 API key。
