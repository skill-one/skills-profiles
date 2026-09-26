# Caido 模式技能

一个基于 Caido API（构建于官方 `@caido/sdk-client`）的 CLI，用于 HTTP 历史驱动的测试。该工具位于 `~/.claude/skills/caido-mode/caido-client.ts`；每个命令都是 `npx tsx caido-client.ts <command>`，除非另有说明，否则输出 JSON。

## 如何操作（首先阅读此部分）

存在**两种不同的模式**：

1. **测试 → 使用 `curl`，始终通过 Caido 代理。** 在历史记录中找到一个具有所需认证的请求，将其认证缓存到一个可重用的 curl 配置（对其头部 + cookie 的忠实静态快照），然后使用 `curl -K auth.cfg "$BASE/path"` 进行探测。**所有流量都必须通过 Caido**（配置包含代理），因此每个请求都会进入 HTTP 历史记录。
2. **交接 → 使用重放会话 + 集合。** 仅当将请求（或一组请求）交给 *用户* 时，才将其作为命名重放会话在命名集合内部实现。

硬性规则：

- **所有内容都必须通过 Caido — 除外高流量暴力破解/模糊测试。** 不要直接 curl 单个目标请求；始终通过 Caido 代理（生成的配置会这样做；否则添加 `-x <proxy>`）。**唯一的例外：** 不要通过 Caido 代理暴力破解/模糊测试工具（`ffuf` 等）或任何一批 **100+ 请求**；它会使 HTTP 历史记录膨胀。运行这些 **直接**（无 `-x`），然后将任何有趣的命中 *带回* Caido（通过代理重新发送 / 提升为重放）以进行调查和交接。
- **使用 `curl` 进行测试。** 不要为探测启动重放会话 — 仅限交接使用。
- **向操作员显示请求，请将其发送到重放。** 每当您希望操作员 *看到* 特定请求时，为其创建一个 **命名重放会话**（如果有多个，则在命名集合中），这就是他们检查和重新运行它的方式。仅通过 curl 测试的请求，一旦提升到重放（`create-session <id> --name …`，或 `send-raw … --name …` 用于定制的请求），操作员才能处理。
- **将认证缓存到文件中，不要重新粘贴它。** 使用 `export-curl --config` 每个目标一次；然后引用配置。不要将 cookie/JWT 倾倒到每个命令中（或在上下文中重复倾倒）。
- **如果您向操作员提供一个可运行的命令，请使其为完全自包含的 curl**（所有头部内联，通过 `export-curl`）— 用于 PoC 或他们将在 Caido 外部运行的内容。`-K` 配置仅用于内部测试；永远不要给操作员一个 `curl -K /tmp/…` 行。
- **重放会话名称是强制性的**，编辑会话会强制明确名称意图。
- **使用集合进行多请求交接**；通过 **名称而不是 ID** 引用会话/集合。

---

## 主要工作流程（默认执行此操作）

```bash
# 1. 找到一个已经具有您需要的认证/cookie 的基础请求。
npx tsx caido-client.ts search 'req.host.cont:"target.com" AND req.path.cont:"/api/user"' --compact
#    → 8431  200  GET target.com/api/user/me

# 2. 对每个目标：将其认证缓存到一个可重用的 curl 配置。
npx tsx caido-client.ts export-curl 8431 --config
#    → 写入 /tmp/caido/target.com/auth.cfg — 一个忠实的静态快照：
#      代理 + 不安全 + 压缩 + 所有请求的认证/身份头部
#      （cookies, Authorization, Origin/Referer, X-*, Sec-*, 应用特定头部）
#      并打印 BASE + 捕获的头部列表

# 3. 使用 curl 进行测试。 -K 带有代理 + 认证，因此它通过 Caido 进入历史记录。
BASE=https://target.com
curl -K /tmp/caido/target.com/auth.cfg "$BASE/api/user/999"                 # IDOR
curl -K /tmp/caido/target.com/auth.cfg -X POST "$BASE/api/profile" \
     -H 'Content-Type: application/json' --data-binary @/tmp/caido/target.com/body.json
```

自由迭代步骤 3 — 它很便宜，它都在 Caido 中，并且大的认证块仍然保存在文件中。
使用 `search 'req.host.cont:"target.com"' --compact` 确认探测是否已落入 Caido。

### 精确发送路径

当测试 **路径遍历 / 路径规范化** (`../`, `/..`, `/./`, 编码变体) 时，传递 **`curl --path-as-is`** — 否则 curl 在发送之前会客户端折叠 `../` 和 `/./`，因此服务器永远不会看到负载，测试会无声通过。保留路径原文：

```bash
curl --path-as-is -K /tmp/caido/target.com/auth.cfg "$BASE/api/../../../etc/passwd"
```

（同样，如果 URL 包含 `[ ] { }` 您不希望 curl 解释，请添加 `-g`/`--globoff`。）

### 配置是一个忠实的静态快照（重要）

`export-curl --config` 捕获基础请求的**所有**认证/身份头部（而不是精选子集），并**静态内联** cookie。两个故意的选择，都学得很痛苦：

- **所有头部，而不是白名单。** 现代应用程序在应用程序特定的头部上控制授权，您无法预测这些头部 — `x-goog-ext-*`, `X-Browser-Validation`, `X-Client-Data`, `Origin`, `Referer`, `X-Same-Domain`, `Sec-*`, … 一个狭窄的白名单会无声地丢弃这些，并且您会得到模糊的 `403`/`PERMISSION_DENIED`。配置现在镜像实际授权请求的内容。真正每个请求/易变头部才会被丢弃：`Host`, `Content-Length`, `Content-Type`, `Connection`, `Accept-Encoding`（curl 为每个请求管理这些）。
  - **⚠ 因为 `Content-Type` 被丢弃，您必须在每个 POST/PUT/PATCH 中自己传递它：**
    `curl -K auth.cfg -X POST "$BASE/path" -H 'Content-Type: application/json' --data-binary @body`.
    使用端点期望的确切 `Content-Type`（例如，Google `batchexecute` 需要使用 `application/x-www-form-urlencoded;charset=UTF-8`）— 错误/缺失的一个是 `400`/`403` 的常见原因。curl 会设置 `Content-Length`；不要添加它。
- **静态 cookie，无 cookie-jar。** 它**默认不使用 `cookie-jar`**，因此 curl 不会将响应的旋转 `Set-Cookie` 写回您捕获的好的 cookie（像 Google 的服务器在每次响应时都会旋转，包括错误响应 — 写回 cookie-jar 会导致会话漂移到失败）。需要跟踪旋转？`export-curl <id> --config --cookie-jar` 会选择加入。

要丢弃特定头部：`--exclude <name>`（可重复）。要完全省略 cookie（例如，当匹配和替换规则注入认证时）：`--exclude cookie`。

### 其他约定

- **每个目标的临时目录：** `/tmp/caido/<host>/` 保存 `auth.cfg`，body 文件，笔记。
- **`$BASE`:** 设置 `BASE=https://<host>` 一次；以 `"$BASE/path"` 的形式编写请求。
- **body 在文件中：** 保存大型/复杂的 body 一次，并使用 `--data-binary @body.json` 发送（`--data-binary` 的正确用法 — 一个精确的字节 *body*）。为每个请求添加 `-H 'Content-Type: …'`，因为配置会省略它。
- **懒惰刷新：** 快照是静态的，因此当请求开始返回 **401/403**（token 过期 / cookie 过期）时，重新运行 `export-curl <fresh-id> --config` 以重新快照，然后重试。
- **CSRF：** 匹配的 `X-CSRF*`/双提交头部会自动捕获。对于每个动作都会旋转的 token，请获取新的：`T=$(curl -sK auth.cfg "$BASE/csrf" | jq -r .token)`。
- **代理注入认证（替代方案）：** 与配置相反，一个匹配和替换规则可以在所有代理流量中注入 `Authorization`/cookies — 然后 `curl -x <proxy> -k "$BASE/path"` 无需 `-K`/头部。

### 向用户发送命令

要使请求 *在 Caido 内部* 对操作员可见，请将其发送到 **重放**（见“重放会话”部分）——这是默认的。本节用于其他情况：向他们提供可运行的 **命令**（PoC 或他们将在 Caido 外部运行的内容）。然后 **始终生成一个完全自包含的 curl** — 所有头部内联，无 `-K`：

```bash
npx tsx caido-client.ts export-curl 8431      # 完整的 curl，所有头部内联（可移植 PoC）
```

丢弃 `-x`/`-k` 以生成可移植的 PoC，用户可以在任何地方运行；仅当用户打算通过他们自己的 Caido 运行它时保留它们。**永远不要给用户一个 `curl -K /tmp/...` 行**——该文件是您的。

---

## 代理

所有 curl 测试都必须通过 Caido 的代理。其地址**默认为 Caido URL**（代理和 API 共享一个地址）。随时发现/确认它：

```bash
npx tsx caido-client.ts auth-status     # 打印 "proxy": "http://localhost:8080"
```

`export-curl --config` 将代理嵌入配置中 (`proxy = "…"`)。对于 ad-hoc curl，请自行添加 `-x <proxy> -k`。仅当代理监听器与 API URL 不同时才覆盖代理 — `setup --proxy <addr>` 或 `export CAIDO_PROXY=<addr>`。

> 从 `auth-status` 获取代理（`proxy`/`activeUrl` 字段）——**不要直接解析 `secrets.json`。** 现在认证是 URL 关键字：地址位于 `.caido.default` / `.caido.instances` 下，而不是 `.caido.url`。

---

## 认证设置

```bash
# 一次性：在 Caido 中创建一个 PAT（控制面板 → 开发者 → 个人访问令牌），然后：
npx tsx caido-client.ts setup <your-pat>
npx tsx caido-client.ts setup <pat> http://192.168.1.100:8080            # 非默认实例
npx tsx caido-client.ts setup <pat> http://localhost:8080 --proxy http://localhost:8080

# 或者环境变量
export CAIDO_PAT=caido_xxxxx
export CAIDO_URL=http://localhost:8080
export CAIDO_PROXY=http://localhost:8080   # 仅当代理与 URL 不同时

npx tsx caido-client.ts auth-status        # 检查 (也打印代理)
npx tsx caido-client.ts health             # 验证实例是否已启动
```

`setup` 通过 SDK 的设备代码流程验证 PAT（由 PAT 自动批准），然后将 PAT + 访问令牌 (+ 代理) 缓存到 `~/.claude/config/secrets.json`。后续运行使用缓存的令牌；即使没有 PAT，有效的缓存的令牌也能工作。

### 多个 Caido 实例

凭据是**按实例 URL 键值对** — 同一台机器上的两个实例永远不会互相覆盖。`setup <pat> <url>` 将该实例存储在其 URL 下（并使其成为活动的默认值）；设置第二个 URL 会添加一个条目而不是覆盖第一个。

```bash
npx tsx caido-client.ts setup <pat-a> http://localhost:8080
npx tsx caido-client.ts setup <pat-b> http://localhost:8081     # 添加，而不是覆盖
npx tsx caido-client.ts auth-status                              # 列出配置的实例 + activeUrl
```

**活动实例**是 `CAIDO_URL` 环境 → 存储的默认值 → `http://localhost:8080`。通过 `CAIDO_URL`（并发安全 — 没有共享的“当前实例”来竞争），例如 `CAIDO_URL=http://localhost:8081 npx tsx caido-client.ts recent`。`CAIDO_PAT`/`CAIDO_PROXY` 环境变量覆盖活动实例的存储值。

---

## 搜索 HTTP 历史记录（HTTPQL）

```bash
npx tsx caido-client.ts search 'req.method.eq:"POST" AND resp.code.eq:200' --compact
npx tsx caido-client.ts search 'req.host.cont:"api"' --limit 50
npx tsx caido-client.ts search 'req.host.cont:"api"' --asc --limit 50   # 最旧的优先 (很少需要)
npx tsx caido-client.ts recent --compact            # 最新的请求，每行一个
npx tsx caido-client.ts get 8431 --compact          # 完整详细信息 (JSON) 当您需要时
npx tsx caido-client.ts get-response 8431 --compact
npx tsx caido-client.ts raw 8431 --out /tmp/caido/target.com/body.json   # 倾倒字节 (例如 body)
```

- **`search` 默认按最新顺序**（按请求 ID 降序）。`--limit N` 因此返回最新的 N 个匹配项。仅在您实际上想要最旧的第一个时传递 `--asc` (别名 `--oldest`)。
- **要获取“最新的匹配 X”，只需运行 `search '<filter>' --limit N`** — 不要从大的 `--limit` 中提取并客户端排序（例如 `jq 'sort_by(.createdAt) | reverse'`）。这将仅对您获取的截断窗口进行排序，因此任何比第 N 个结果新的请求都将无声地不可见——您会误认为陈旧的流量是最新流量。让 Caido 做排序。
- `recent` 总是按最新顺序，但不需要过滤器；使用 `search --limit N` 获取最新的匹配过滤器。
- `--compact` → 每个请求一行简短 (`id  状态  METHOD host/path`)。
- 更倾向于 `search`/`recent --compact` 用于浏览；`get`/`export-curl` 仅当您已选择一个时。

有关完整查询语言的详细信息，请参阅下文的 **HTTPQL 参考**。

---

## 重放会话 — 仅用于交接

当您向 **用户** 提供请求时使用这些。正常测试使用 curl（如上所述），而不是会话。
从原始请求创建的会话会自动将其头部行结尾规范化为 CRLF — 交接会话永远不会使用裸 LF (`\n`) 结尾。

```bash
# 从历史记录请求创建命名的会话（名称是强制性的）。
npx tsx caido-client.ts create-session 8431 --name "IDOR /api/user/:id"
npx tsx caido-client.ts sessions                                   # 列表 (别名: replay-sessions)
npx tsx caido-client.ts rename-session "IDOR /api/user/:id" "IDOR - 确认"
npx tsx caido-client.ts move-session "IDOR - 确认" "Vuln chain - IDOR to ATO"

# 从原始请求文件构建交接会话（CRLF 自动规范化）:
npx tsx caido-client.ts send-raw --host target.com --raw @/tmp/req.txt --name "crafted repro"
```

### 编辑会话会强制名称意图

如果用户要求您在 *内部* 使用 Caido 进行测试，请使用 `edit` / `edit-session`。因为编辑会改变会话的内容，所以声明其 **名称** 会发生什么——传递正好一个 `--no-name-change` (`--nonach`) 或 `--new-name "<name>"`：

```bash
npx tsx caido-client.ts edit 8431 --path /api/user/999 --name "IDOR victim 999"        # 新会话
npx tsx caido-client.ts edit-session "IDOR victim 999" --body '{"role":"admin"}' --nonach --compact
npx tsx caido-client.ts edit 8431 --path /api/admin --session "IDOR victim 999" --new-name "priv-esc"
```

`edit` 保留原始请求的 cookie/认证；它支持 `--method`, `--path`, `--set-header`, `--remove-header`, `--body`（自动 Content-Length）, `--replace <from>:::<to>`, 以及连接覆盖 (`--sni`, `--connect-host`, …)。

### 检查现有重放选项卡

当重放选项卡已经在 Caido 中打开，并且您希望从其当前状态进行操作时，通过 **名称或 ID** 查找它（无需重新创建）：

```bash
npx tsx caido-client.ts get-session "IDOR victim 999" --compact      # 会话 + 活动条目
npx tsx caido-client.ts replay-entries "IDOR victim 999" --limit 20  # 选项卡中的请求/响应历史 (别名 `session-entries`). `--raw`
```

`session-entries` 是 `replay-entries` 的别名。使用这些来读取选项卡中的内容；使用 `edit-session`（如上）将其修改的请求发送到其中。

---

## 集合 — 大量使用它们

集合组织会话以供交接使用。**在创建会话之前，列出现有的集合并决定它属于哪里。** 名称是强制性的，集合永远不会自动创建。

```bash
npx tsx caido-client.ts collections                         # 首先查询
npx tsx caido-client.ts create-collection "Swagger - petstore.yaml"
npx tsx caido-client.ts rename-collection "old name" "new name"
```

| 情况 | 集合决策 |
|-----|----------|
| **一个** 请求复制给用户 | 默认集合 — **不要** 创建一个。命名会话并告诉用户名称。 |
| 一个 **JS 文件** 中的端点每个都使用重放选项卡 | 新集合 `JS File Endpoints`. |
| 一个 **Swagger 规范** 中的端点每个都使用重放选项卡 | 新集合 `Swagger - <filename>`. |
| 一个 **多请求链** 用于漏洞 | 新集合 `Vuln chain - <description>`, 步骤命名为 `1. …`, `2. …`. |
| 所有端点都在 **`/api/v2`** 下 | 新集合 `/api/v2/*`. |

通过 **名称** 传递集合；CLI 解析它（如果缺少则提示您创建它）：

```bash
npx tsx caido-client.ts create-session 8431 --name "1. login" --collection "Vuln chain - IDOR to ATO"
```

当您报告时，命名集合和会话 — 永远不要 ID。

---

## Match & Replace — 自动重写流量

Match & Replace（Caido 内部称为 **"Tamper" 规则**）会自动重写通过 Caido 的请求/响应。杀手级用法：**在代理处注入认证**，因此您的 curl 命令不需要携带它 — 添加一个规则，在所有代理请求上设置 `Authorization`，然后 `curl -x <proxy> -k "$BASE/path"` 无需 `-K`/头部即可进行认证。

一个规则是**部分** × **操作** × **匹配器** × **替换器**，带有可选的 **条件**（HTTPQL 范围）和 **来源**：

| 部分 | 选择 |
|-----|------|
| **部分** | `req: req-method req-path req-query req-body req-first-line req-header req-all req-sni` · `resp: resp-body resp-status resp-first-line resp-header resp-all` · `ws: ws-up ws-down` |
| **操作** | `raw` (在部分内匹配) · `update`/`add`/`remove` (仅限头部 & 查询) · 方法/状态仅 `update` |
| **匹配器** | `--match-value <str>` · `--match-regex <re>` · `--match-full` (整个部分) · `--match-name <n>` (头部/查询更新/添加/删除) |
| **替换器** | `--replace <term>` (字面量; `""` 允许) · `--workflow <id>` (运行工作流) |
| **条件** | `--condition '<httpql>'` — 仅当请求匹配时才应用 (例如一个主机) |
| **来源** | `--sources INTERCEPT,REPLAY,…` — 它适用于哪些流量 |

四个陷阱，所有默认值都已为您设置：
- **新规则被禁用。** 使用 `toggle-mr-rule <id> --on` 启用。
- **默认集合**是 Caido 的“默认集合”（使用 `--collection <name|id>` 覆盖）。
- **默认来源**是 `INTERCEPT` (代理流量), 匹配 Caido。添加 `--sources` 以扩大范围。
- **JS 目标 — 根据您匹配的内容选择匹配器。** `--match-value` 对于稳定的字面量（字符串常量，JSON 键，固定 API 路径）是合适的。当匹配接近 minified 标识符时使用 `--match-regex`：符号名称在每次捆绑部署时都会旋转（例如 `_.ex` → `_.Ww`），因此字面量规则在没有任何错误的情况下会无声地停止匹配，而不会报错。将正则表达式锚定到结构上稳定的邻居——周围的字符串文字，已知函数名，固定的 JSON 键——而不是 minified 标识符本身。

**提交前预览：** `test-mr-rule` 将规则应用于原始请求，而不会创建任何内容——使用它来确认规则按预期工作。

```bash
# 预览：这会正确添加头部吗？
npx tsx caido-client.ts test-mr-rule --section … [--operation] [--match-*] [--replace/--workflow] [--name --collection --condition --sources] (预览，无操作)
```

- **注入认证到所有代理请求** (然后启用它)
ID=$(npx tsx caido-client.ts create-mr-rule --section … [--operation] [--match-*] [--replace "Bearer eyJ…" … --condition 'req.host.eq:"target.com"' --name "auth inject" | jq -r '.created.id')
npx tsx caido-client.ts toggle-mr-rule "$ID" --on

- **其他模式**
npx tsx caido-client.ts create-mr-rule --section req-header --operation remove \
  --match-name If-None-Match --sources REPLAY --name "drop INM"           # 删除头部
npx tsx caido-client.ts create-mr-rule --section req-body --match-regex '"admin":false' \
  --replace '"admin":true' --name "force admin"                            # body 正则表达式
npx tsx caido-client.ts create-mr-rule --section resp-status --replace 403 --name "fake 403"  # 响应

npx tsx caido-client.ts mr-rules                # 列出规则 (+ 启用状态)
npx tsx caido-client.ts toggle-mr-rule <id> --off
npx tsx caido-client.ts delete-mr-rule <id>
```

管理集合使用 `mr-collections`, `create-mr-collection`, `rename-mr-collection`, `delete-mr-collection`; `move-mr-rule <id> <collection>`; `update-mr-rule <id> …` 重新指定规则（与创建的标志相同）。

---

## 输出控制（与 `get`, `get-response`, `replay`, `edit`, `send-raw`, `edit-session`一起工作）

| 标志 | 描述 |
|------|------|
| `--max-body <n>` | 最大响应 body 行数 (默认 200, 0 = 无限) |
| `--max-body-chars <n>` | 最大 body 字符 (默认 5000, 0 = 无限) |
| `--no-request` | 忽略请求原始 |
| `--headers-only` | 仅头部，无 body |
| `--compact` | 简写：`--no-request --max-body 50 --max-body-chars 5000` |

---

## HTTPQL 参考

Caido 的查询语言，用于搜索 HTTP 历史记录。

**关键**：字符串值必须加引号；整数不是。

**关键**：HTTPQL 没有 `NOT` 操作符。使用否定操作符变体：`ncont` (不包含), `nlike`, `nregex`, `ne` (不等于)
- 错误：`NOT req.path.cont:"/admin"` — 正确：`req.path.ncont:"/admin"`
- **`search` 默认按最新顺序**（按请求 ID 降序）。`--limit N` 因此返回最新的 N 个匹配项。仅在您实际上想要最旧的第一个时传递 `--asc` (别名 `--oldest`)。
- **要获取“最新的匹配 X”，只需运行 `search '<filter>' --limit N`** — 不要从大的 `--limit` 中提取并客户端排序（例如 `jq 'sort_by(.createdAt) | reverse'`）。这将仅对您获取的截断窗口进行排序，因此任何比第 N 个结果新的请求都将无声地不可见——您会误认为陈旧的流量是最新流量。让 Caido 做排序。
- `recent` 总是按最新顺序，但不需要过滤器；使用 `search --limit N` 获取最新的匹配过滤器。
- `--compact` → 每个请求一行简短 (`id  状态  METHOD host/path`)。
- 更倾向于 `search`/`recent --compact` 用于浏览；`get`/`export-curl` 仅当您已选择一个时。

有关完整查询语言的详细信息，请参阅下文的 **HTTPQL 参考**。

---

## 其他功能（参考）

### Findings — 在 Caido 的 Findings 选项卡中显示
```bash
npx tsx caido-client.ts findings --limit 50
npx tsx caido-client.ts create-finding 8431 --title "IDOR on /api/user/:id" \
  --description "通过改变 id 读取其他用户的配置文件" --reporter "rez0" --dedupe-key "idor-user"
npx tsx caido-client.ts update-finding <id> --title "…" --description "…"
```

### 范围 / 过滤器预设 / 环境
```bash
npx tsx caido-client.ts create-scope "Target" --allow "*.target.com" --deny "*.cdn.target.com"
npx tsx caido-client.ts create-filter "API 4xx" --query 'req.path.cont:"/api/" AND resp.code.gte:400' --alias "api4xx"
npx tsx caido-client.ts search 'preset:"API 4xx"' --compact
npx tsx caido-client.ts create-env "IDOR-Test"; npx tsx caido-client.ts env-set <env-id> victim_id "user_999"
```

### 模糊测试 / 中继 / 项目 / 任务 / 信息
```bash
npx tsx caido-client.ts create-automate-session 8431   # 在 UI 中配置有效负载，然后：fuzz <session-id>
npx tsx caido-client.ts intercept-status | intercept-enable | intercept-disable
npx tsx caido-client.ts projects ; npx tsx caido-client.ts viewer ; npx tsx caido-client.ts plugins
```

---

## 完整命令参考

每个命令（运行 `npx tsx caido-client.ts <command>`）。会话/集合接受 **名称或 ID**；输出为 JSON 除非另有说明。运行 `--help` 获取完整标志列表。

| 命令 | 它做什么 |
|---|---|
| **历史记录 & 测试** | |
| `search <httpql>` | 搜索历史记录，**最新优先**。 `--limit --after --ids-only --asc/--oldest --compact` |
| `recent` | 最新的请求。 `--limit --compact` |
| `get <id>` / `get-response <id>` | 完整请求 / 仅响应 (输出控制标志) |
| `raw <id>` | 倾倒精确字节的原始请求。 `--out <file> --response` |
| `export-curl <id>` | 完整的 curl (用于用户) |
| `export-curl <id> --config` | 可重用的 `-K` 配置 — 对所有认证头部 + 静态内联 cookie 的忠实静态快照 (内部)。 `--out <file>` · `--cookie-jar` (跟随旋转) · `--exclude <h>` |
| **发送 / 编辑** | |
| `replay <id> --name <n>` | 重放到一个新的命名会话。 `--raw --collection` + 连接覆盖 |
| `send-raw --host <h> --raw <s\|@file\|-> --name <n>` | 通过新的命名会话发送原始请求。 `--port --tls/--no-tls --collection` |
| `edit <id>` | 编辑 + 发送到重放。 `--method --path --set-header --remove-header --body` (自动 Content-Length) `--replace <from>:::<to>`, 以及连接覆盖 (`--sni`, `--connect-host`, …) |
| `edit-session <name\|id>` | 从会话的活动条目编辑 + 发送 (需要 `--nonach` 或 `--new-name`) |
| **会话查找** | |
| `get-session <name\|id>` | 会话 + 活动条目。 `--compact` |
| `replay-entries <name\|id>` | 选项卡中的请求/响应历史 (别名 `session-entries`). `--limit --raw` |
| **会话** | |
| `create-session <id> --name <n>` | 从请求创建命名会话。 `--collection` |
| `rename-session <name\|id> <new>` · `move-session <s> <collection>` | 重命名 / 移动 |
| `sessions` (别名 `replay-sessions`) · `delete-sessions <id,id,…>` | 列表 / 删除 |
| **集合** | |
| `collections` (别名 `replay-collections`) | 列出集合 |
| `create-collection <name>` · `rename-collection <c> <new>` · `delete-collection <name\|id>` | 创建 / 重命名 / 删除 |
| **模糊测试** | `create-automate-session <session-id>` · `fuzz <session-id>` (在 UI 中配置有效负载) |
| **Findings** | `findings` · `get-finding <id>` · `create-finding <id> --title …` · `update-finding <id>` |
| **范围** | `scopes` · `create-scope <name> --allow --deny` · `update-scope <id>` · `delete-scope <id>` |
| **过滤器** | `filters` · `create-filter <name> --query [--alias]` · `update-filter <id>` · `delete-filter <id>` |
| **环境** | `envs` · `create-env <name>` · `env-set <env> <var> <val>` · `select-env [id]` · `delete-env <id>` |
| **项目** | `projects` · `select-project <id>` |
| **任务** | `tasks` · `cancel-task <id>` |
| **托管文件** | `hosted-files` · `delete-hosted-file <id>` |
| **中继** | `intercept-status` · `intercept-enable` · `intercept-disable` |
| **Match & Replace** | `mr-rules` · `mr-collections` · `create-mr-rule --section … [--operation] [--match-*] [--replace/--workflow] [--name --collection --condition --sources]` · `test-mr-rule --raw … --section …` (预览，无操作) · `toggle-mr-rule <id> --on\|--off` · `rename-mr-rule <id> <n>` · `move-mr-rule <id> <coll>` · `update-mr-rule <id> …` · `delete-mr-rule <id>` · `create-mr-collection <n>` · `rename-mr-collection <c> <n>` · `delete-mr-collection <c>` |
| **信息 / 认证** | `viewer` · `plugins` · `health` · `setup <pat> [url] [--proxy]` · `auth-status` |

---

## 架构

基于 `@caido/sdk-client` v0.2.0+ 构建。没有原始 `fetch` — 高级 SDK 方法加上 `client.graphql.query/mutation` 使用 `gql` 文档，因为 SDK 没有公开的几个功能。

```
caido-client.ts          # CLI 入口 — 参数解析 + 分发
lib/
  client.ts              # SDK 客户端单例，SecretsTokenCache, 认证, 解析代理
  graphql.ts             # `gql` 文档，SDK 没有公开的几个功能
  output.ts             # 原始格式化 (截断, 头部仅显示, 原始→curl)
  types.ts             # OutputOpts
  commands/
    requests.ts        # search, recent, get, get-response, raw, export-curl (+ --config)
    replay.ts         # replay, send-raw, edit, sessions, collections (CRLF 自动规范化), automate
    findings.ts        # findings
    management.ts      # scopes, filters, 环境, 项目, 托管文件, 任务
    intercept.ts        # intercept 状态/启用/禁用
    matchreplace.ts  # match & replace (tamper) 规则 — buildTamperSection + 命令
    info.ts         # viewer, plugins, health, setup, auth-status
```

---

## 对 Claude 的说明（清单）

1. **使用 `curl` 进行测试，始终通过 Caido** — 代理必须在路径中（配置会这样做；否则添加 `-x <proxy>`）。**例外：** 暴力破解/模糊测试 (`ffuf`) 或任何一批 **100+ 请求** 直接通过 Caido — 它会使 HTTP 历史记录膨胀。运行这些 **直接**（无 `-x`），然后将任何有趣的命中 *带回* Caido（通过代理重新发送 / 提升为重放）以进行调查和交接。
2. **一次缓存认证：** `export-curl <id> --config` → `/tmp/caido/<host>/auth.cfg` — 对所有认证头部 + 静态内联 cookie 的忠实静态快照。使用 curl 进行测试。 `-K` 带有代理 + 认证，因此它通过 Caido 进入历史记录。
3. **懒惰刷新：** 快照是静态的，因此当请求开始返回 **401/403**（token 过期 / cookie 过期）时，重新运行 `export-curl <fresh-id> --config` 以重新快照，然后重试。
4. **向用户发送命令：** 要使请求 *在 Caido 内部* 对操作员可见，请将其发送到 **重放**（见“重放会话”部分）——这是默认的。本节用于其他情况：向他们提供可运行的 **命令**（PoC 或他们将在 Caido 外部运行的内容）。然后 **始终生成一个完全自包含的 curl** — 所有头部内联，无 `-K`：
5. **重放会话名称是强制性的**，编辑会话会强制明确名称意图。
6. **使用集合进行多请求交接**；通过 **名称而不是 ID** 引用会话/集合。

## 操作说明（shell 常见错误）

- **不要在 `while`/`for` 循环中批量 CLI 调用。** 某些 shell 在循环子 shell 中会删除 `PATH`，因此 `head`/`python3`/等会变成“命令未找到”，并且循环体会无声失败 (会话看起来好像没有创建)。运行每个 `send-raw`/`create-session` 作为独立的顶级命令，或者作为独立的 `bash` 脚本使用显式的 `export PATH=…`。
- **`search --ids-only` 返回一个 JSON 数组 (`["123"]`)，而不是裸 ID — 解包前使用，例如 `ID=$(… --ids-only | jq -r '.[0]')`。
- **`sessions` / `collections` 现在列出所有内容**（分页，而不仅仅是第一页），因此新创建的项目始终可见。`--limit N` 如果您想要一个简短列表，则限制计数。
- **错误处理**
- **认证错误** → `auth-status`, 重新 `setup <pat>`（或设置 `CAIDO_PAT`）。
- **curl 获得 401/403/登录重定向** → token 过期；刷新配置。
- **curl 无法通过代理连接** → 确认代理使用 `auth-status`；Caido 必须正在运行。
- **连接拒绝 / 未准备好** → Caido 没有启动或仍在启动中；检查 `health`。
