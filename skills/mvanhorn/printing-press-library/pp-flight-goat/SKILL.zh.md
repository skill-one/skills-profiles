---
name: pp-flight-goat
description: Flight Goat 打印机 CLI。搜索真实 Google Flights 航班价格、最便宜日期、Kayak 路线以及 FlySoar 价格查询，无需 API 密钥——此外还可选 FlightAware AeroAPI 的航班状态、延误和警报数据。
---

<!-- 生成的文件 — 请勿编辑。
     此文件是库/travel/flight-goat/SKILL.md的逐字镜像，
     合并后由工具/generate-skills/重新生成。在此处的手动修改
     在下次重新生成时将被静默覆盖。请修改库/源代码。
     请参阅仓库代理指南，第“生成的工件：registry.json，cli-skills/”部分。 -->

# 飞行山羊 — 印刷机 CLI

## 前置条件：安装 CLI

此技能驱动 `flight-goat-pp-cli` 二进制文件。**您必须在调用此技能的任何命令之前验证 CLI 是否已安装。** 如果它丢失，请先安装它：

1. 通过印刷机安装程序安装。它将二进制文件默认设置为 macOS/Linux 上的 `$HOME/.local/bin` 和 Windows 上的 `%LOCALAPPDATA%\Programs\PrintingPress\bin`：
   ```bash
   npx -y @mvanhorn/printing-press-library install flight-goat --cli-only
   ```
2. 验证：`flight-goat-pp-cli --version`
3. 确保报告的安装目录在 `$PATH` 中，以便代理/运行时将调用此技能。

如果 `npx` 安装失败（没有 Node.js，离线等），则回退到直接 Go 安装（需要 Go 1.26.6 或更高版本）。此安装到 `$GOPATH/bin`（默认 `$HOME/go/bin`），因此将此目录添加到 `$PATH`：

```bash
go install github.com/mvanhorn/printing-press-library/library/travel/flight-goat/cmd/flight-goat-pp-cli@latest
```

如果安装后 `--version` 报告“命令未找到”，则运行时无法看到 `$PATH` 上的二进制目录。在验证成功之前，请不要继续使用技能命令。

## 独特功能：无需 API 密钥的票价搜索

标题命令直接命中消费者票价来源，无需凭证 — 不要将 CLI 表现为受 AeroAPI 保护。FlightAware AeroAPI（在下方文档中记录）是次要的且可选的。

- `flight-goat-pp-cli flights <出发地> <目的地> <日期>` — Google Flights 票价搜索：真实价格、航段、航空公司。往返使用 `--return`，多点使用重复的 `--segment`，批量探测使用重复的 `--trip`。
- `flight-goat-pp-cli dates <出发地> <目的地>` — 在旅行窗口内扫描最低票价。
- `flight-goat-pp-cli explore <机场>` / `flight-goat-pp-cli longhaul <机场>` — Kayak 非直飞和长途航线发现。
- `flight-goat-pp-cli soar <出发地> <目的地> <日期>` — FlySoar（Duffel NDC/GDS）第二价格意见，带预订交接。
- `flight-goat-pp-cli award <出发地> <目的地>` — Seats.aero 奖励（里程）可用性：跨舱位里程+税费兑换选项。**需要** `SEATS_AERO_API_KEY`（一个 Seats.aero 合作伙伴 API 密钥；缓存搜索是专业版资格）。只读。
- `flight-goat-pp-cli wifi flight <航班号>` / `wifi airline <IATA>` / `wifi airlines` / `wifi rollouts [IATA]` / `wifi speed <航班>` / `wifi airline-speed <IATA>` / `wifi search <查询>` — SeatWifi 机上 WiFi 预测，Starlink 推广状态，以及众包速度报告。**无需 API 密钥。** 公共 JSON 在 https://seatwifi.com。只读。
- `flight-goat-pp-cli assess` — 延迟航班/重新预订决策支持。

每个结果中的 `booking_urls` 引用了与搜索运行相同的 `--currency`。`award` 是例外：它引用里程/积分，而不是现金，并且不会生成预订深度链接。

### 批量票价探测：使用 --trip 与 --pace，永远不要使用 shell 循环

Google 按每个 IP 限制票价流量。并行 shell 循环 `flights` 调用会触发 HTTP 429 块，可能持续超过 15 分钟。相反，请使用一个带 --pace 的调用来运行批量探测：

```bash
# 三个独立搜索，3 秒间隔，一个 JSON 信封，每个行程的行
flight-goat-pp-cli flights \
  --trip "SEA>DEN@2026-09-14" \
  --trip "PDX>DEN@2026-09-15@2026-09-17" \
  --trip "SFO>DEN@2026-09-15" \
  --pace 3s --currency EUR --agent
```

`--trip` 接受 `ORIG>DEST@DEPART` 或 `ORIG>DEST@DEPART@RETURN`（与 `--segment` 相同的语法族），并替换位置参数；所有过滤器标志（`--currency`，`--stops`，`--class`，`--airlines`，`--time`，`--return-time`，`--passengers`）适用于每个行程。每个行程的行将出现在信封的 `results[]` 中，状态为 `ok`/`error`/`skipped`。

往返航程可以独立地约束每个航段的出发窗口：`--time` 设置去程窗口，`--return-time` 设置返程航段的窗口（未设置时回退到 `--time`）。两者都采用相同的 `H-H` 24 小时形式，例如 `flight-goat-pp-cli flights SEA HNL 2026-08-01 --return 2026-08-10 --time 6-12 --return-time 17-23` 用于上午去程和晚上返程。

### 往返航程：单独的 `--return` 不返回返程选项

单独的 `--return` 只显示**去程行程**。每个行程的 `price` 已经包含 Google 自己自动选择的“最便宜返程”总价，但从未显示返程航班（时间、航空公司、持续时间）— 不要将去程列表读作包含两个方向，也不要假设价格仅适用于去程。

要查看和选择真实的返程选项，请运行 Google 自己 UI 使用的真正两步流程。步骤 1，`flight-goat-pp-cli flights LHR BCN 2027-03-01 --return 2027-03-18 --agent` 返回去程选项，其中 `flights[0].direction == "outbound"` — 注意您想要的一个的 1 基位置。步骤 2，`flight-goat-pp-cli flights LHR BCN 2027-03-01 --return 2027-03-18 --select-outbound 1 --agent` 返回针对特定去程定价的真实返程选项：`flights[]` 现在有 `direction == "return"` 和独立价格，信封的 `selected_outbound` 会回显它们与哪个去程配对。

`--select-outbound N` 是 1 基的，按步骤 1 返回它们的顺序计数。它需要 `--return`（仅限往返）并且不能与 `--trip` 或 `--segment`（>=2）组合。每个 `Flight` 还在往返去程行上携带 `selection_token` — 这是 CLI 内部构建步骤 2 请求的相同值 — 以便调用者构建自己的选择流程，而不是固定的索引。

速率限制语义：

- 暂时的 429 会自动重试（2s/5s/12s 指数退避）之前命令失败。
- 持久的 429 会提前停止批处理 — 继续会加深 IP 块 — 部分信封仍然发出，退出代码为 7（速率限制）。
- 当 Google 被阻止时，`soar` 和 `explore`/`longhaul` 使用不同的后端并继续工作；`doctor` 记录了 `google_flights` 下相同契约。

### 往返航程最低日期：`dates --round --duration`

`dates` 默认按单程价格扫描。添加 `--round --duration N` 扫描往返总价 — 每行是当天出发并在 `N` 晚后返程的最便宜往返价格，而不是单独的去程/返程价格对：`flight-goat-pp-cli dates SEA HNL --round --duration 7 --sort --agent`。`--duration` 与 `--round` 一起使用时必须大于零。每个结果行都携带 `return_date`（`departure_date` + `--duration`）和 `price`，后者已经是往返总价。

# 简介
AeroAPI 是一个简单的、基于查询的 API，它为软件开发人员提供对 FlightAware 的各种飞行数据的访问。用户可以获得当前或历史数据。AeroAPI 是一个提供准确且可操作的航空数据的 RESTful API。随着 Foresight™ 的推出，客户可以访问为美国一半以上的预测航空公司 ETA 提供动力的数据。

## 类别
AeroAPI 分为几个类别，以便更容易发现。

- 航班：摘要信息、计划航线、位置等
- Foresight：使用 FlightAware Foresight™ 增强的航班位置
- 机场：机场信息和 FIDS 风格资源
- 运营商：运营商信息和机队活动资源
- 报警：配置航班报警和交付目的地
- 历史：各种端点的历史航班访问
- 其他：航班中断、未来日程信息、飞机所有者信息

## 开发工具
AeroAPI 使用 OpenAPI Spec 3.0 定义，这意味着它可以轻松导入 Postman 等工具。要开始，请尝试使用 Postman 的说明
[导入 API 规范](https://learning.postman.com/docs/integrations/available-integrations/working-with-openAPI/)。
导入后作为集合，只需在集合的授权选项卡下填充“值”字段并保存，然后才能进行调用。

AeroAPI OpenAPI 规范位于：\
https://flightaware.com/commercial/aeroapi/resources/aeroapi-openapi.yml

我们的 [开源 AeroApps 项目](/aeroapi/portal/resources)
提供了一小组服务和示例应用程序，以帮助您开始。

飞行信息显示系统 (FIDS) AeroApp 是一个使用多种语言和 Docker 容器的多层应用程序示例。
它展示了连接性、数据缓存、飞行展示和利用飞行地图。

报警 AeroApp 演示了在具有 Docker 化 Python 后端和 React 前端的示例应用程序中使用 AeroAPI 设置、编辑和接收报警。

我们的 AeroAPI 推送通知 [测试界面](/commercial/aeroapi/send.rvt)
提供了一种快速简便的方法来测试通过 AeroAPI 推送的自定义报警的交付。

## 命令参考

**aircraft** — 管理飞机

- `flight-goat-pp-cli aircraft <类型>` — 返回给定 ICAO 飞机类型设计ator 字符串的飞机类型信息。

**airports** — 管理机场

- `flight-goat-pp-cli airports get` — 返回给定 ICAO 或 LID 机场代码（如 KLAX、KIAH、O07 等）的机场信息。
- `flight-goat-pp-cli airports get-all` — 返回所有已知机场的 ICAO 标识符。
- `flight-goat-pp-cli airports get-delays-for-all` — 返回有延误的机场列表。
- `flight-goat-pp-cli airports get-nearby` — 返回给定位置一定距离内的机场列表。

**alerts** — AeroAPI 报警可用于配置和接收有关关键航班事件的实时报警。
通过我们的报警端点提供的可定制报警功能，AeroAPI 赋予用户选择各种事件/过滤器进行报警的能力。
这样做，您就可以接收专门定制的报警，这些报警将交付给您，用于诸如航班计划提交、航班离港（出和离）、航班到达（到和进）等事件！

要开始使用报警，必须首先使用 **PUT /alerts/endpoint** 端点设置帐户范围的默认 URL，报警将交付到该 URL。此步骤必须在配置任何报警之前完成，并将作为所有报警的回退 URL，如果特定报警没有指定交付 URL。如果在配置报警之前不执行此步骤，则在尝试与 **POST /alerts** 端点交互时，您将收到 400 错误，错误消息将提醒您此步骤。一旦通过 **PUT /alerts/endpoint** 端点设置 URL，就可以使用 **POST /alerts** 端点配置报警。**GET /alerts** 端点也可以用来检索与您的 AeroAPI 密钥关联的所有当前配置的报警。**GET /alerts** 端点将允许您轻松检索帐户配置的任何特定感兴趣的报警的 ID，这可以让您使用 **GET** **PUT** 和 **DELETE**
**/alerts/{id}** 端点来检索、更新和删除特定报警。

在配置单个报警时，*target_url* 字段可以设置为与通过 **PUT /alerts/endpoint** 设置的帐户范围目标端点不同的 URL。如果设置报警的 *target_url* 字段，则该特定报警将交付到指定的 *target_url*，而不是帐户范围的默认端点。如果此字段未为报警配置，则报警将交付到帐户范围的默认端点。通过设置此字段，可以轻松地将不同的报警定向为通过不同的端点接收，这对于配置每个应用程序的报警或将报警发送到替代开发环境而无需调整生产报警配置非常有用。

对于每个配置的报警，可以为一对多设置报警交付的“事件”。虽然大多数事件将导致一次报警交付，但“到达”和“离港”事件都可能导致多次报警交付（称为捆绑）。*离港* 事件捆绑离港（实际离地）报警、航班计划提交报警以及最多 5 次每离港更改，这些更改可以包括超过 30 分钟的重大离港延误、登机口更改和机场延误。FlightAware 全球客户还将收到 *Power on* 和 *Ready to taxi* 报警作为离港捆绑的一部分。*到达* 事件捆绑到达（实际着陆）报警以及最多 5 次航程更改（包括超过 30 分钟的延误，不包括备降）已识别。FlightAware 全球客户还将收到 *taxi stop* 时间作为 *到达* 捆绑的一部分。为 On/Off 设置捆绑类型和未捆绑类型将仅在事件可能重叠的情况下导致单个报警。

如果需要更改报警配置，使用 **PUT /alerts/{id}**
端点和唯一报警标识符（id）更新报警比创建另一个报警更受青睐。这样做可以避免交付重复报警，如果它们不再感兴趣，可能会产生不必要的噪音。

如果任何时候需要删除报警，可以使用 **DELETE alerts/{id}**
端点删除报警，以便它不再交付。作为提醒，可以从 **GET /alerts** 端点检索特定报警 ID。

- `flight-goat-pp-cli alerts create` — 创建新的 AeroAPI 航班报警。
- `flight-goat-pp-cli alerts delete` — 删除具有给定 ID 的特定报警
- `flight-goat-pp-cli alerts delete-endpoint` — 删除将通过 **POST** 发送到未配置特定 URL 的报警的帐户范围默认 URL。
- `flight-goat-pp-cli alerts get` — 返回具有指定 ID 的报警的配置数据。
- `flight-goat-pp-cli alerts get-all` — 返回 FlightAware 帐户的所有配置的报警（这包括通过其他方式配置的报警
- `flight-goat-pp-cli alerts get-endpoint` — 返回将通过 AeroAPI 交付的 URL。
- `flight-goat-pp-cli alerts set-endpoint` — 更新将通过 AeroAPI 交付的默认 URL。
- `flight-goat-pp-cli alerts update` — 修改具有指定 ID 的报警的配置。

**disruption-counts** — 管理中断计数

- `flight-goat-pp-cli disruption-counts get` — 返回指定时间段内特定航空公司或机场的航班取消/延误计数。
- `flight-goat-pp-cli disruption-counts get-all` — 返回指定时间段内所有航空公司或所有机场的整体航班取消/延误计数。

**flights** — 管理航班

- `flight-goat-pp-cli flights get` — 返回注册、标识符或 fa_flight_id 的航班信息状态摘要。
- `flight-goat-pp-cli flights get-by-advanced-search` — 根据地理空间搜索参数返回当前或最近在飞的航班。
- `flight-goat-pp-cli flights get-by-position-search` — 根据地理空间搜索参数返回航班位置。
- `flight-goat-pp-cli flights get-by-search` — 通过匹配各种参数（包括地理空间数据）搜索在飞的航班。
- `flight-goat-pp-cli flights get-count-by-search` — 完整搜索查询文档位于 /flights/search 端点。

**foresight** — Foresight 端点提供对 FlightAware 的 Foresight 预测模型和关键事件预测的访问。我们先进的机器学习 (ML) 模型识别航班的关键影响因素，以实时预测未来事件，提供前所未有的洞察力，以提高运营效率，并促进空中和地面上的更好决策。有关 Foresight 功力的更多信息，请访问 https://www.flightaware.com/commercial/foresight/

这些端点每个都映射了一个具有类似功能的非 Foresight 对等端点，并增加了 Foresight 响应中包含的所有 ML '预测' 值。相应的非 Foresight 端点响应包含一个标志 'foresight_predictions_available'，该标志可以可选地用作触发器，以便按需获取和利用 Foresight 预测并管理成本。Foresight 仅适用于高级别客户。有关更多信息、定价详情以及启用您的账户使用 Foresight，请联系 integrationsales@flightaware.com。

- `flight-goat-pp-cli foresight get-flight-position-with` — 获取航班的当前位置，包括 Foresight 数据
- `flight-goat-pp-cli foresight get-flight-with` — 返回注册、识别或 fa_flight_id 的航班信息状态摘要
- `flight-goat-pp-cli foresight get-flights-by-advanced-search-with` — 根据地理空间搜索参数返回当前或最近在飞的航班。

**history** — 管理历史记录

- `flight-goat-pp-cli history get-aircraft-last-flight` — 给定其注册信息，返回飞机最后一次已知航班的航班信息状态摘要。
- `flight-goat-pp-cli history get-flight` — 返回注册、识别或 fa_flight_id 的历史航班信息状态摘要。
- `flight-goat-pp-cli history get-flight-map` — 将历史航班的轨迹作为 base64 编码的图像返回。
- `flight-goat-pp-cli history get-flight-route` — 返回历史航班申报路线的信息，包括坐标、名称
- `flight-goat-pp-cli history get-flight-track` — 将历史航班的轨迹作为位置数组返回。

**operators** — 管理运营商

- `flight-goat-pp-cli operators get` — 返回运营商的信息，例如其名称、ICAO/IATA 代码、总部位置等。
- `flight-goat-pp-cli operators get-all` — 返回运营商引用列表（ICAO/IATA 代码和访问更多信息 URL）。

**schedules** — 管理时刻表

- `flight-goat-pp-cli schedules` — 返回航空公司发布的已发布时刻航班。

### 找到正确的命令

当你知道你想做什么，但不知道哪个命令可以做到时，可以直接询问 CLI：

```bash
flight-goat-pp-cli which "<你自己的话描述的功能>"
```

`which` 将自然语言的功能查询解析为 CLI 的精选功能索引中的最佳匹配命令。退出代码 `0` 表示至少有一个匹配；退出代码 `2` 表示没有自信的匹配——回退到 `--help` 或使用更窄的查询。

## Auth Setup
运行 `flight-goat-pp-cli auth setup` 以打印获取密钥的 URL 和步骤（添加 `--launch` 以打开 URL）。然后设置：

```bash
export FLIGHT_GOAT_API_KEY="<你的密钥>"
```

要持久化凭证，请使用 `flight-goat-pp-cli auth set-token <token>`。存储的密钥位于数据目录下的 `credentials.toml` 中，而不是 `config.toml` 中。

运行 `flight-goat-pp-cli doctor` 以验证设置。

## Agent Mode

在任何命令中添加 `--agent`。展开为：`--json --compact --no-input --no-color --yes`。

- **可管道** — JSON 输出到标准输出，错误输出到标准错误
- **可过滤** — `--select` 保留字段子集。点路径深入嵌套结构；数组逐元素遍历。对于在 verbose API 上保持上下文小至关重要：

  ```bash
  flight-goat-pp-cli airports get mock-value --agent --select id,name,status
  ```
- **可预览** — `--dry-run` 显示请求而不发送
- **离线友好** — 同步/搜索命令在可用时可以使用本地 SQLite 存储库
- **非交互式** — 从不提示，每个输入都是一个标志
- **显式重试** — 仅当已存在的创建应计为成功时使用 `--idempotent`，并且仅当缺失的删除目标应计为成功时使用 `--ignore-missing`

### 响应封装

从本地存储或 API 读取的命令将输出封装在可追溯封装中：

```json
{
  "meta": {"source": "live" | "local", "synced_at": "...", "reason": "..."},
  "results": <数据>
}
```

解析 `.results` 获取数据，解析 `.meta.source` 以知道是实时还是本地。只有在标准输出是终端并且没有机器格式标志（`--json`、`--csv`、`--compact`、`--quiet`、`--plain`、`--select`）时才打印人类可读的 `N results (live)` 摘要到标准错误——管道/agent 消费者和显式格式运行在标准输出上获取纯 JSON。

## Paths and state

Agent 应将 CLI 的路径解析器视为运行时合同的一部分：

- 使用 `--home <dir>` 用于一次调用，或设置 `FLIGHT_GOAT_HOME=<dir>` 将四种路径类型移至一个根目录下。
- 仅当特定类型必须不同时才使用每个类型的环境变量：`FLIGHT_GOAT_CONFIG_DIR`、`FLIGHT_GOAT_DATA_DIR`、`FLIGHT_GOAT_STATE_DIR`、`FLIGHT_GOAT_CACHE_DIR`。
- 解析顺序是每个类型的环境变量、`--home`、`FLIGHT_GOAT_HOME`、XDG（`XDG_CONFIG_HOME`、`XDG_DATA_HOME`、`XDG_STATE_HOME`、`XDG_CACHE_HOME`），然后是平台默认值。
- `config` 包含 `config.toml` 和配置文件等设置。`data` 包含 `credentials.toml`、`data.db`、cookie 和 auth 侧车。`state` 包含持久化查询、作业和 `teach.log`。`cache` 包含可再生的 HTTP/缓存文件。
- 存储的密钥位于数据目录下的 `credentials.toml` 中。现有的旧版 `config.toml` 密钥为兼容性读取，并在第一次 auth 写入时保留 `config.toml`。
- 运行 `flight-goat-pp-cli doctor --fail-on warn` 以暴露路径和凭证位置警告。`agent-context` 为需要解析目录的 agent 暴露 v4 `paths` 块。
- 对于 MCP，通过 MCP 主机配置传递重新定位。MCP 二进制文件不会继承 CLI 标志：

  ```json
  {
    "mcpServers": {
      "flight-goat": {
        "command": "flight-goat-pp-mcp",
        "env": {
          "FLIGHT_GOAT_HOME": "/srv/flight-goat"
        }
      }
    }
  }
  ```

Fleet 优先级：继承的每个类型的特定环境变量会覆盖该类型的显式 `--home`。使用 `FLIGHT_GOAT_HOME` 或每个类型的变量作为持久的 fleet 控制杆，并且仅用于单次调用时使用 `--home`。重新定位不能通过取消设置环境变量来逆转；在清除 `FLIGHT_GOAT_HOME` 之前手动移动文件，或者 `doctor` 将不会在以前的根目录下找到遗留的凭证。

## Automatic learning

此 CLI 配备了一个自我捕获的学习循环。CLI 自己进行账目管理：每次调用都在本地记录，失败的标志后跟纠正的重试自动导出 `flag_alias` 候选，并且在没有剧本的查询家族上运行 `teach` 自动从会话的日记中合成 `playbook_candidate`。你的工作只是判断：首先 `recall`，然后对出现的候选采取行动，`teach` 最终答案，当观察到纠正时 `playbook amend`。你永远不会手动记录失败。

### 第一步：在任何发现之前 `recall`

在新用户问题的列表/搜索/钻取命令之前运行：

```bash
flight-goat-pp-cli recall "<用户的查询>" --agent
```

响应封装：

```json
{
  "query": "...",
  "normalized": "<标准化形式>",
  "query_entities": ["..."],
  "found": true | false,
  "match_score": 0.0,
  "results": [
    { "resource_id": "...", "resource_type": "...", "venue": "...",
      "confidence": 2, "entity_match": "exact|partial|unknown",
      "source": "taught|preseed|pattern", "warnings": ["..."] }
  ],
  "mismatches": [ /* 仅当 --debug-mismatches */ ],
  "warnings": [ /* 顶层 */ ],
  "candidates": [
    { "id": 12, "class": "flag_alias | playbook_candidate",
      "summary": "...", "sightings": 3, "last_seen": "...",
      "rationale": "...",
      "next_action": ["<试验命令>", "flight-goat-pp-cli learnings confirm 12"] }
  ],
  "playbook": {
    "query_family": "...",
    "playbook": {
      "steps": [ { "cmd": "<带 {slot} 替换的命令>", "purpose": "..." } ],
      "entity_slots": ["$ENTITY"],
      "expected_tool_calls": 3
    },
    "slots_resolved": { "$ENTITY": { "token": "<实时 token>", "canonical": "<规范>" } },
    "notes": "<此查询家族的 workarounds + gotchas>"
  },
  "notes": "<非剧本调用者的重复显示>"
}
```

空存储短路：如果存储中还没有学习记录、剧本或候选（recall 找不到，并且 `learnings list` 和 `learnings candidates` 都为空），则跳过本次会话的 recall，而不是对每个查询征税；一旦教了某些内容，就恢复 recall-first。

### 第二步：决策树

按顺序读取 `candidates`、`playbook`、`notes`、`results[0]` 和警告：

```
if Candidates present (warnings include "candidates_present"):
    -> candidates 是 try-then-confirm，永远不会是事实。逐字遵循每个候选的 two-step next_action：首先运行试验命令，然后仅在试验验证行为后运行 `learnings confirm <id>`。用 `learnings reject <id>` 拒绝错误的候选。
    -> NEVER 重新教 recall 表面为候选的内容；确认或拒绝该候选，而不是教一个重复的。
    -> candidates 与剧本和资源命中一起出现，而不是替代它们；在对其采取行动后继续执行下面的分支。

if Playbook present:
    -> 首先逐字阅读 Playbook.notes（CLI 没有暴露的 workarounds + gotchas）
    -> 按顺序重播 Playbook.steps，用 Playbook.slots_resolved 条目替换实体槽标记。如果一个步骤的槽未解析，则回退到仅对该步骤进行发现。
    -> Playbook 的 expected_tool_calls 是一个预算；如果你发现自己运行的材料更多，请在会话结束时通过 `flight-goat-pp-cli playbook amend` 记录偏差。

elif Notes present (no Playbook):
    -> 在任何发现步骤之前逐字阅读 Notes；它们即使在没有结构化编排的情况下也包含此查询家族的已知 gotchas。

elif Found AND Results[0].EntityMatch == "exact" AND Results[0].Confidence >= 2:
    -> 跳过发现；并行获取 Results[*].ResourceID 的实时数据

elif Found AND Results[0].EntityMatch == "partial":
    -> 候选提示，不是命中；在信任之前阅读资源标题以验证

elif (任何 --debug-mismatches 传递时的 Mismatches[] 中的行):
    -> 治理为冷启动；存储的学习是针对不同实体的（从 query_entities 解析出的不同规范）

else:  // Found == false, no playbook, no notes
    -> 冷启动；正常运行发现；之后教答案（步骤 4）。如果该家族还没有剧本，那么教会自动从本次会话的日记中合成剧本候选——你不需要手动记录一个。
```

剧本和 Notes 与每个资源路径正交。recall 响应可以同时携带剧本和 `Results[]` 命中——使用两者：剧本告诉你要运行哪个编排；资源命中会短路特定步骤。默认跳过 `mismatches`；仅在调查冷启动惊喜时传递 `--debug-mismatches`。

候选判断细节：`learnings confirm <id>` 在材料化之前打印候选的完整负载——检查打印的负载是否与你验证的行为匹配。`learnings reject <id>` 销毁导出签名，以便相同的候选不会再次出现。封装只包含现在值得采取行动的几个候选；`flight-goat-pp-cli learnings candidates` 列出完整的开放集。

优雅降级：如果 `learnings confirm` 是一个未知命令，你正在驾驶一个较旧的二进制文件——忽略候选指导并遵循其余协议。

### 第三步：始终读取 `warnings`

- `low_confidence`：`confidence<2` 的行存在。将其视为提示，而不是跳过发现命中。
- `resource_not_in_store`：本地存储中没有学习指向的资源。匹配验证器无法对实体进行分类——直接获取并重新评估。
- `cross_alias_match`（每个结果）：该行在具有不同别名下教过，并通过 `entity_lookups` 与实时查询的规范匹配（例如，一个 "USA" 教满足一个 "United States" recall）。信任 resource_id。
- `similar_shape_different_entity:<canonical>`（顶层）：一个结构上匹配的行存在，但其规范实体与实时查询的实体不同。将其视为冷启动；警告中包含冲突的规范作为提示，但该行不会被提升到 Results。
- `ambiguous_alias`（顶层）：单个查询实体解析为多个规范（例如，"Cards" → Arizona Cardinals + St. Louis Cardinals）。从上下文中暴露歧义，然后再提交到资源。
- `candidates_present`（顶层）：封装包含 `candidates` 部分。在执行任何其他操作之前，通过步骤 2 中的候选分支处理它。
- `lookup_refresh_available`（顶层）：查询中的实体还没有 lookup 行，但同步数据可以提供一行。运行 `flight-goat-pp-cli sync` 以刷新实体查找。
- 顶层的 `no_learnings_for_query_family`：表在 Jaccard 地板以上没有行。纯粹的冷启动。

### 第四步：`teach &` 在最终确定你的响应后始终——始终

教是无条件的。在存储无法回答的查询后，在后台教最终资源映射——没有调用次数阈值，没有判断它是否“值得”学习。教是循环的锚点：它触发没有剧本的家族的剧本合成，并且相同的引用短语折叠成一个家族，以便近似的重复教不会使存储碎片化。在组装用户界面响应后但在发出之前，使用 shell `&` 使调用立即返回：

```bash
flight-goat-pp-cli teach --query "<用户的查询>" --resource-type <类型> --resource <id1> --resource <id2>
# (追加 shell `&` 以在后台运行)
```

成功时静默。错误仅记录在解析状态目录下的 `teach.log` 中。教**最具体的**资源——如果用户问了一个广泛的查询，并且你通过遍历父记录找到了具体的答案，教叶 id，而不是父级。CLI 使用种子的 `entity_lookups` 在 recall 时进行跨别名解析，因此在一个别名下教（例如，"Niners"）会自动满足未来在另一个别名下（例如，"49ers"、"San Francisco"）的查询。

PII 规则：教结构化问题时移除标识符——决不包含名称、电子邮件、电话号码、账户 id 或其他个人标识符在教过的查询或笔记中。CLI 扫描教过的查询中的明显电子邮件/电话形状并警告，但不阻止；在教之前移除，而不是依赖警告。

### 第五步：剧本——可选标志，自动合成

你不需要决定会话是否“值得”剧本：在没有剧本的家族上运行教会自动从会话的日记中合成 `playbook_candidate`，并且下一个会话通过确认/拒绝来评判它。仅在您已经持有值得逐字记录的编排时才附加显式剧本标志——CLI 没有暴露的 workarounds（静默丢弃的标志、未记录的参数、分页技巧、负载 gotchas）。优先使用**集成的一调用形式**——在同一个 `teach` 调用中记录资源学习和剧本：

```bash
# 常规情况：在一次调用中同时记录资源学习和剧本。
flight-goat-pp-cli teach \
  --query "<用户的问题>" \
  --resource <id> \
  --playbook-file ~/playbooks/<shape>.json \
  --playbook-notes-file ~/playbooks/<shape>-notes.md
# (追加 shell `&` 将其置于后台执行)

# 替代方案：仅剧本 (不与资源一同记录)。
flight-goat-pp-cli teach-playbook \
  --query "<用户的问题>" \
  --playbook-file ~/playbooks/<shape>.json \
  --notes-file ~/playbooks/<shape>-notes.md
```

剧本文件是 JSON 格式，包含 `steps`、`entity_slots`、`expected_tool_calls`。笔记文件是 markdown 格式，包含原始的注意事项。无文件调用者 (仅 MCP 的代理) 将相同内容内联传递：在集成的 `teach` 表单上使用 `--playbook-json` 和 `--playbook-notes`，在 `teach-playbook` 上使用 `--playbook-json` 和 `--notes`。在集成 `teach` 表单中，剧本标志是可选的 - 完全省略它们以仅进行资源学习。在独立的 `teach-playbook` 表单中，必须设置剧本和笔记标志中的至少一个；两者都为空将被拒绝。剧本按结构化查询系列 (移除实体) 为键，因此从一个实体形状查询学习的配方适用于所有其他相同形状的查询，`slots_resolved` 在调用时绑定实时查询的规范。

当您确实在未来调用中找到一个剧本时，将其视为真实情况：使用 `slots_resolved` 替换重播步骤，跳过已记录在剧本中的发现，并在任何步骤之前读取 `notes`。

### 第 6 步：当您的调试响应确定更正时 `playbook amend &`

如果您的调试协议响应确定了笔记或剧本应知道的明确更正——一个解决方法、一个未记录的端点形状、一个过时的字段名、观察到的模式漂移、空负载回退——在发出面向用户的响应之前，先触发 `playbook amend`。与 `teach` 相同的“发射并忘记”态度。

```bash
flight-goat-pp-cli playbook amend \
  --query "<确切的召回查询字符串>" \
  --add-note "<您的具体更正>"
# (追加 shell `&` 将其置于后台执行)
```

什么值得更正：本次会话中观察到的、未来您会受益于知道的行为。值得更正的示例：

- 用于 CLI 表面的解决方法，该表面静默地丢弃或错误排序标志。
- 未记录的端点形状 (响应被 `{meta, results}` 包装，有效负载嵌套层级比文档声称的深两层)。
- 观察到的模式漂移 (一个字段被重命名，一个索引在季节之间移动，一个 API 现在返回小写的类别标签)。

不属于笔记的内容：

- 用户问题的特定于年份或特定于实体的答案。那是响应，不是学习。
- 团队/每名运动员/每行数据，剧本在运行时已经检索。
- 重述现有笔记中已经说明的内容的陈述。

更正命令将时间戳标记 (`[amend YYYY-MM-DDTHH:MMZ]: <text>`) 追加到系列的现有笔记中。多次更正累积；审计跟踪是可见的。如果系列尚未存在剧本，更正将创建一个仅包含笔记的剧本 (以便冷启动更正仍然有效)。

#### 更正笔记的 PII 纪律

`playbook amend` 笔记设计为可能作为共享知识在未来的 Printing Press 版本中向上流动。保持它们不含用户识别内容，以便上游贡献路径无需事后清理即可保持开放：

- **不要嵌入** 用户文件系统的路径、个人 API 密钥或令牌、用户电子邮件地址、用户 GitHub 处理程序或与单个用户绑定的特定查询历史。
- **可接受**：端点形状、未记录的字段名、API 技巧、观察到的模式漂移、CLI 表面的解决方法、通用的分页或重试策略。

如果更正仅在与用户特定上下文相关时才有意义，它应属于个人笔记，而不是剧本更正。

### 衡量循环

`flight-goat-pp-cli learnings stats` 报告召回命中率、教学到重用、剧本解析率以及来自本地 `learn_events` 表的候选确认/拒绝计数。直到有分母，比率才为空；所有内容都保留在此机器上。使用它来检查循环是否为该 CLI 值得。

### 禁用学习

- 在单个命令上使用 `--no-learn` 会短路 `recall` 和 `teach` 写入路径。用于确定性代理流程或必须不受累积学习影响的测试。
- 环境中设置 `FLIGHT_GOAT_NO_LEARN=true` 将全局禁用管道。

## 代理反馈

当您 (或代理) 注意到此 CLI 的问题时，记录它：

```
flight-goat-pp-cli feedback "the --since flag is inclusive but docs say exclusive"
flight-goat-pp-cli feedback --stdin < notes.txt
flight-goat-pp-cli feedback list --json --limit 10
```

条目存储在本地作为 `feedback.jsonl` 在解析的数据目录下。除非设置了 `FLIGHT_GOAT_FEEDBACK_ENDPOINT` 并且传递了 `--send` 或 `FLIGHT_GOAT_FEEDBACK_AUTO_SEND=true`，否则它们永远不会 POST。默认行为是本地-only。

写让您感到惊讶的内容，而不是错误报告。简短、具体、一行：这就是复合的部分。

## 输出交付

每个命令都接受 `--deliver <sink>`。输出将发送到命名的 sink，而不是 (或代替) stdout，因此代理可以无需手动管道即可路由命令结果。支持三种 sink：

| Sink | 效果 |
|------|------|
| `stdout` | 默认；仅写入 stdout |
| `file:<path>` | 原子写入输出到 `<path>` (临时 + 重命名) |
| `webhook:<url>` | 将输出正文 POST 到 URL (`application/json` 或 `application/x-ndjson` 当 `--compact` 时) |

未知方案将被拒绝，并命名支持的方案集的结构化错误。Webhook 失败将返回非零值并在 stderr 上记录 URL + HTTP 状态。

## 命名配置文件

配置文件是保存的标志值集，跨调用重用。当计划或定期代理在每次运行时提供不同输入的同时重用相同的保存标志时使用它。

```
flight-goat-pp-cli profile save briefing --json
flight-goat-pp-cli --profile briefing airports get mock-value
flight-goat-pp-cli profile list --json
flight-goat-pp-cli profile show briefing
flight-goat-pp-cli profile delete briefing --yes
```

显式标志始终优先于配置文件值；配置文件值优先于默认值。`agent-context` 列出所有可用配置文件在 `available_profiles` 下，以便内省代理在运行时发现它们。

## 退出代码

| 代码 | 含义 |
|------|------|
| 0 | 成功 |
| 2 | 使用错误 (参数错误) |
| 3 | 资源未找到 |
| 4 | 需要认证 |
| 5 | API 错误 (上游问题) |
| 7 | 速率限制 (等待并重试) |
| 10 | 配置错误 |

## 参数解析

解析 `$ARGUMENTS`：

1. **空、`help` 或 `--help** → 显示 `flight-goat-pp-cli --help` 输出
2. **以 `install` 开头** → 以 `mcp` 结尾 → MCP 安装；否则 → 见上述先决条件
3. **其他任何内容** → 直接使用 (作为 CLI 命令与 `--agent` 执行)

## MCP 服务器安装

1. 安装 MCP 服务器：
   ```bash
   go install github.com/mvanhorn/printing-press-library/library/travel/flight-goat/cmd/flight-goat-pp-mcp@latest
   ```
2. 向 Claude Code 注册：
   ```bash
   claude mcp add flight-goat-pp-mcp -- flight-goat-pp-mcp
   ```
3. 验证：`claude mcp list`

## 直接使用

1. 检查是否安装：`which flight-goat-pp-cli`
   如果未找到，提供安装选项 (见此技能开头的先决条件)。
2. 将用户查询匹配到上述唯一功能和命令参考中的最佳命令。
3. 使用 `--agent` 标志执行：
   ```bash
   flight-goat-pp-cli <command> [subcommand] [args] --agent
   ```
4. 如果不明确，深入子命令帮助：`flight-goat-pp-cli <command> --help`.
