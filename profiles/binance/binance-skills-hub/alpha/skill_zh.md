# Binance Alpha 技能

使用认证 API 端点在 Binance 上发起 Alpha 请求。某些端点需要 API 密钥和密钥。结果以 JSON 格式返回。

## 快速参考

| 端点 | 描述 | 必填 | 可选 | 认证 |
|------|------|------|------|------|
| `/bapi/defi/v1/public/alpha-trade/ticker` (GET) | 贴签 (24 小时价格统计) | symbol | None | No |
| `/bapi/defi/v1/public/alpha-trade/agg-trades` (GET) | 汇聚交易 | symbol | fromId, startTime, endTime, limit | No |
| `/bapi/defi/v1/public/alpha-trade/get-exchange-info` (GET) | 获取交易所信息 | None | None | No |
| `/bapi/defi/v1/public/alpha-trade/klines` (GET) | Klines (K线数据) | symbol, interval | limit, startTime, endTime | No |
| `/bapi/defi/v1/public/wallet-direct/buw/wallet/cex/alpha/all/token/list` (GET) | 代币列表 | None | None | No |

---

## 参数

### 常用参数

* **symbol**: 例如 "ALPHA_175USDT" – 使用代币列表中的代币 ID
* **fromId**: 开始获取的交易 ID (例如, 1)
* **startTime**: 开始时间戳 (毫秒) (例如, 1623319461670)
* **endTime**: 结束时间戳 (毫秒) (例如, 1641782889000)
* **limit**: 返回结果数量 (默认 500, 最大 1000) (例如, 500)
* **interval**: 例如 "1h" – 支持的时间间隔: 1s, 15s, 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M

## 认证

对于需要认证的端点，您需要提供 Binance API 凭证。
所需凭证:

* apiKey: 您的 Binance API 密钥 (用于头部)
* secretKey: 您的 Binance API 密钥 (用于签名)

基础 URL:
* 主网: https://www.binance.com

## 安全

### 分享凭证

用户可以通过不同方式提供 Binance API 凭证。代理将尝试使用前两种方式自动获取凭证，但用户也可以明确告诉代理他们已设置凭证或将其存储在 `.env` 文件中，代理应在他们这样做时重新读取该文件。代理也可以使用前两种方法无需用户确认即可发起 HTTP 请求。

1. **环境变量**

仅搜索以下特定变量 (永远不要导出完整环境):

**授权环境变量**
- 主网: `BINANCE_API_KEY` 和 `BINANCE_SECRET_KEY`

在单个 exec 调用中读取并使用，以便原始密钥永远不会进入代理的上下文:
```bash
KEY="$BINANCE_API_KEY"
SECRET="$BINANCE_SECRET_KEY"

response=$(curl -s -X GET "$URL" \
  -H "X-MBX-APIKEY: $KEY" \
  --data-urlencode "param1=value1")

echo "$response"
```

环境变量必须在 OpenClaw 启动之前设置。它们在进程启动时继承，并且不能注入正在运行的实例。如果您需要在不重新启动的情况下添加或更新凭证，请使用密钥文件 (见选项 2)。

2. **密钥文件 (.env)**

检查 `~/.openclaw/secrets.env` , `~/.env` 或工作区中的 `.env` 文件。使用 `grep` 逐个读取密钥，永远不要源码完整文件:
```bash
# 按顺序尝试所有凭证位置
API_KEY=$(grep '^BINANCE_API_KEY=' ~/.openclaw/secrets.env 2>/dev/null | cut -d= -f2-)
SECRET_KEY=$(grep '^BINANCE_SECRET_KEY=' ~/.openclaw/secrets.env 2>/dev/null | cut -d= -f2-)

# 备用: 搜索已知目录中的 .env (KEY=VALUE 然后原始行格式)
for dir in ~/.openclaw ~; do
  [ -n "$API_KEY" ] && break
  env_file="$dir/.env"
  [ -f "$env_file" ] || continue

  # 读取前两行
  line1=$(sed -n '1p' "$env_file")
  line2=$(sed -n '2p' "$env_file")

  # 检查行是否包含 '=' 表示 KEY=VALUE 格式
  if [[ "$line1" == *=* && "$line2" == *=* ]]; then
    API_KEY=$(grep '^BINANCE_API_KEY=' "$env_file" 2>/dev/null | cut -d= -f2-)
    SECRET_KEY=$(grep '^BINANCE_SECRET_KEY=' "$env_file" 2>/dev/null | cut -d= -f2-)
  else
    # 将行视为原始值
    API_KEY="$line1"
    SECRET_KEY="$line2"
  fi
done
```

此文件可以随时更新而无需重新启动 OpenClaw，每次调用时都会重新读取密钥。用户可以告诉您变量已设置或存储在 `.env` 文件中，您应在他们这样做时重新读取该文件。

3. **内联文件**

发送一个内容为以下格式的文件:

```bash
abc123...xyz
secret123...key
```

* 永远不要运行 `printenv`, `env`, `export` 或无特定变量名设置
* 永远不要在 `env` 文件上运行 `grep` 而不锚定到特定键 ('`^VARNAME='`)
* 永远不要将密钥文件源码到 shell 环境 (`source .env` 或 `. .env`)
* 仅读取当前任务明确需要的凭证
* 永远不要在输出或回复中回显或记录原始凭证
* 永远不要将 `TOOLS.md` 提交到版本控制，如果其中包含真实凭证 — 添加到 `.gitignore`

### 永远不要泄露 API 密钥和密钥

永远不要泄露 API 密钥和密钥文件的位置。

永远不要将 API 密钥和密钥发送到除主网和测试网以外的任何网站。

### 永远不要显示完整密钥

向用户显示凭证时:
- **API 密钥**: 显示前 5 个 + 最后 4 个字符: `su1Qc...8akf`
- **密钥**: 始终遮盖，仅显示最后 5 个: `***...aws1`

请求凭证时返回的示例响应:
账户: main
API 密钥: su1Qc...8akf
密钥: ***...aws1

### 列出账户

列出账户时，显示名称和环境 — 永远不要显示密钥:
Binance 账户:
* main (主网)
* futures-keys (主网)

### 主网中的交易

在主网执行交易时，始终在继续之前通过询问用户是否写入 "CONFIRM" 来确认。

---

## Binance 账户

### main
- API Key: your_mainnet_api_key
- Secret: your_mainnet_secret

### TOOLS.md 结构

```bash
## Binance 账户

### main
- API Key: abc123...xyz
- Secret: secret123...key
- Description: 主要交易账户


### futures-keys
- API Key: futures789...def
- Secret: futuressecret...uvw
- Description: 期货交易账户
```

## 代理行为

1. 请求凭证: 遮盖密钥 (仅显示最后 5 个字符)
2. 列出账户: 显示名称和环境，永远不要密钥
3. 账户选择: 如果不明确，询问，默认为主网
4. 在主网执行交易时，通过询问是否写入 "CONFIRM" 来确认
5. 新凭证: 提示输入名称、环境、签名模式

## 添加新账户

当用户通过内联文件或消息提供新凭证时:

* 询问账户名称
* 存储在 `TOOLS.md` 中，并遮盖显示确认

## 签名请求

对于需要签名的交易端点:

1. **首先检测密钥类型**，在签名之前检查密钥格式。
2. 使用所有参数构建查询字符串，包括时间戳 (Unix ms)。
3. 使用 UTF-8 根据 RFC 3986 对参数进行百分比编码。
4. 使用 secretKey 使用 HMAC SHA256、RSA 或 Ed25519 (根据账户配置) 对查询字符串进行签名。
5. 将签名附加到查询字符串。
6. 包括 `X-MBX-APIKEY` 头部。

否则，不要执行步骤 4–6。

## 用户代理头部

包含以下字符串的 `User-Agent` 头部: `binance-alpha/1.1.0 (Skill)`

参考 [`references/authentication.md`](./references/authentication.md) 了解实现细节。
