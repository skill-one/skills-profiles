# Flight Goat — 印刷机 CLI

## 前置条件：安装 CLI

此技能驱动 `flight-goat-pp-cli` 二进制文件。**您必须在调用此技能的任何命令之前验证 CLI 是否已安装。** 如果它缺失，请先安装它：

1. 通过印刷机安装程序安装。它将二进制文件默认设置为 macOS/Linux 上的 `$HOME/.local/bin` 和 Windows 上的 `%LOCALAPPDATA%\Programs\PrintingPress\bin`：
   ```bash
   npx -y @mvanhorn/printing-press-library install flight-goat --cli-only
   ```
2. 验证：`flight-goat-pp-cli --version`
3. 确保报告的安装目录在 `$PATH` 中，以便代理/运行时调用此技能。

如果 `npx` 安装失败（没有 Node.js、离线等），则回退到直接 Go 安装（需要 Go 1.26.6 或更高版本）。此安装将安装到 `$GOPATH/bin`（默认 `$HOME/go/bin`），因此请将此目录添加到 `$PATH` 中：

```bash
go install github.com/mvanhorn/printing-press-library/library/travel/flight-goat/cmd/flight-goat-pp-cli@latest
```

如果 `--version` 在安装后报告“命令未找到”，则运行时无法看到 `$PATH` 上的二进制目录。在验证成功之前，不要继续使用技能命令。

## 独特功能：无需 API 密钥的票价搜索

标题命令直接命中消费者票价来源，无需凭证——不要将 CLI 表现为 AeroAPI 受限。FlightAware AeroAPI（如下文所述）是次要的且可选的。

- `flight-goat-pp-cli flights <origin> <destination> <date>` — Google Flights 票价搜索：真实价格、航段、航空公司。使用 `--return` 进行往返，使用重复的 `--segment` 进行多城市，使用重复的 `--trip` 进行批量探测。
- `flight-goat-pp-cli dates <origin> <destination>` — 在旅行窗口内进行最便宜日期扫描。
- `flight-goat-pp-cli explore <airport>` / `flight-goat-pp-cli longhaul <airport>` — Kayak 直飞和长途航线发现。
- `flight-goat-pp-cli soar <origin> <destination> <date>` — FlySoar（Duffel NDC/GDS）第二价格意见，并提供预订交接。
- `flight-goat-pp-cli award <origin> <destination>` — Seats.aero 奖励（里程）可用性：跨舱位里程+税费兑换选项。**需要** `SEATS_AERO_API_KEY`（一个 Seats.aero 合作伙伴 API 密钥；缓存搜索是专业资格认证的）。只读。
- `flight-goat-pp-cli wifi flight <flightNumber>` / `wifi airline <IATA>` / `wifi airlines` / `wifi rollouts [IATA]` / `wifi speed <flight>` / `wifi airline-speed <IATA>` / `wifi search <query>` — SeatWifi 机上 WiFi 预测、Starlink 推广状态和用户提供的速度报告。**无需 API 密钥。** 公共 JSON 在 https://seatwifi.com。只读。
- `flight-goat-pp-cli assess` — 延迟航班/重新预订决策支持。

每个结果的 `booking_urls` 引用了与搜索运行时相同的 `--currency`。`award` 是例外：它引用里程/积分，而不是现金，并且不会生成预订深度链接。

### 批量票价探测：使用 --trip 与 --pace，永远不要使用 shell 循环

Google 对每个 IP 地址的票价流量进行速率限制。并行 shell 循环调用 `flights` 触发 HTTP 429 块，可能持续超过 15 分钟。相反，请使用单个调度的 --pace 进行批量探测：

```bash
# 三个独立的搜索，3 秒间隔，一个 JSON 封装，每个行程一行
flight-goat-pp-cli flights \
  --trip "SEA>DEN@2026-09-14" \
  --trip "PDX>DEN@2026-09-15@2026-09-17" \
  --trip "SFO>DEN@2026-09-15" \
  --pace 3s --currency EUR --agent
```

`--trip` 接受 `ORIG>DEST@DEPART` 或 `ORIG>DEST@DEPART@RETURN`（与 `--segment` 相同的语法家族）并替换位置参数；所有过滤标志 (`--currency`, `--stops`, `--class`, `--airlines`, `--time`, `--return-time`, `--passengers`) 都适用于每个行程。每个行程的行将位于封套的 `results[]` 中，状态为 `ok`/`error`/`skipped`。

往返行程可以独立地限制每个航段的出发窗口：`--time` 设置出发窗口，`--return-time` 设置返回航段的窗口（如果未设置，则回退到 `--time`）。两者都采用相同的 `H-H` 24 小时格式，例如 `flight-goat-pp-cli flights SEA HNL 2026-08-01 --return 2026-08-10 --time 6-12 --return-time 17-23` 用于上午出发和晚上返回。

### 往返行程：单独的 --return 不返回返回航段选项

单独的 `--return` 只显示**出发行程**。每个出发行程的 `price` 已经包含 Google 自己自动选择的“最便宜返回”总价，但从未显示任何返回航段航班（时间、航空公司、持续时间）——不要将出发列表读作包含两个方向，也不要假设价格仅适用于出发航段。

要查看和选择真实的返回航段选项，请运行 Google 自己的 UI 使用的真实两步流程。步骤 1，`flight-goat-pp-cli flights LHR BCN 2027-03-01 --return 2027-03-18 --agent` 返回出发行程，其中 `flights[0].direction == "outbound"` — 注意您想要的那一个的 1 基本位置。步骤 2，`flight-goat-pp-cli flights LHR BCN 2027-03-01 --return 2027-03-18 --select-outbound 1 --agent` 返回针对特定出发的真实返回选项，价格与该特定出发相匹配：`flights[]` 现在有 `direction == "return"` 和独立的价
