# Binance 资产功能

使用认证 API 端点在 Binance 上请求资产。某些端点需要 API 密钥和密钥。结果以 JSON 格式返回。

## 快速参考

| 端点 | 描述 | 必填 | 可选 | 认证 |
|------|------|------|------|------|
| `/sapi/v1/account/apiTradingStatus` (GET) | 账户 API 交易状态 (USER_DATA) | 无 | recvWindow | 是 |
| `/sapi/v1/account/info` (GET) | 账户信息 (USER_DATA) | 无 | recvWindow | 是 |
| `/sapi/v1/account/status` (GET) | 账户状态 (USER_DATA) | 无 | recvWindow | 是 |
| `/sapi/v1/account/apiRestrictions` (GET) | 获取 API 密钥权限 (USER_DATA) | 无 | recvWindow | 是 |
| `/sapi/v1/accountSnapshot` (GET) | 每日账户快照 (USER_DATA) | type | startTime, endTime, limit, recvWindow | 是 |
| `/sapi/v1/account/disableFastWithdrawSwitch` (POST) | 禁用快速提款开关 (USER_DATA) | 无 | recvWindow | 是 |
| `/sapi/v1/account/enableFastWithdrawSwitch` (POST) | 启用快速提款开关 (USER_DATA) | 无 | recvWindow | 是 |
| `/sapi/v1/bnbBurn` (POST) | 在现货交易和保证金利息中切换 BNB 燃烧 (USER_DATA) | 无 | spotBNBBurn, interestBNBBurn, recvWindow | 是 |
| `/sapi/v1/asset/assetDetail` (GET) | 资产详情 (USER_DATA) | 无 | asset, recvWindow | 是 |
| `/sapi/v1/asset/dust-btc` (POST) | 获取可转换为 BNB 的资产 (USER_DATA) | 无 | accountType, recvWindow | 是 |
| `/sapi/v1/asset/assetDividend` (GET) | 资产分红记录 (USER_DATA) | 无 | asset, startTime, endTime, limit, recvWindow | 是 |
| `/sapi/v1/asset/ledger-transfer/cloud-mining/queryByPage` (GET) | 获取云挖矿支付和退款历史 (USER_DATA) | startTime, endTime | tranId, clientTranId, asset, current, size | 是 |
| `/sapi/v1/asset/dust-convert/convert` (POST) | 尘埃转换 (USER_DATA) | asset | clientId, targetAsset, thirdPartyClientId, dustQuotaAssetToTargetAssetPrice | 是 |
| `/sapi/v1/asset/dust-convert/query-convertible-assets` (POST) | 尘埃可转换资产 (USER_DATA) | targetAsset | dustQuotaAssetToTargetAssetPrice | 是 |
| `/sapi/v1/asset/dribblet` (GET) | 尘埃日志 (USER_DATA) | 无 | accountType, startTime, endTime, recvWindow | 是 |
| `/sapi/v1/asset/dust` (POST) | 尘埃转账 (USER_DATA) | asset | accountType, recvWindow | 是 |
| `/sapi/v1/asset/get-funding-asset` (POST) | 资金钱包 (USER_DATA) | 无 | asset, needBtcValuation, recvWindow | 是 |
| `/sapi/v1/spot/open-symbol-list` (GET) | 获取开放合约列表 (MARKET_DATA) | 无 | 无 | 否 |
| `/sapi/v1/asset/custody/transfer-history` (GET) | 查询用户委托历史（仅主账户）(USER_DATA) | email, startTime, endTime | type, asset, current, size, recvWindow | 是 |
| `/sapi/v1/asset/transfer` (GET) | 查询用户通用转账历史 (USER_DATA) | type | startTime, endTime, current, size, fromSymbol, toSymbol, recvWindow | 是 |
| `/sapi/v1/asset/transfer` (POST) | 用户通用转账 (USER_DATA) | type, asset, amount | fromSymbol, toSymbol, recvWindow | 是 |
| `/sapi/v1/asset/wallet/balance` (GET) | 查询用户钱包余额 (USER_DATA) | 无 | quoteAsset, recvWindow | 是 |
| `/sapi/v1/spot/delist-schedule` (GET) | 获取现货合约下架计划 (MARKET_DATA) | 无 | recvWindow | 否 |
| `/sapi/v1/asset/tradeFee` (GET) | 交易费 (USER_DATA) | 无 | symbol, recvWindow | 是 |
| `/sapi/v3/asset/getUserAsset` (POST) | 用户资产 (USER_DATA) | 无 | asset, needBtcValuation, recvWindow | 是 |
| `/sapi/v1/capital/config/getall` (GET) | 所有币种信息 (USER_DATA) | 无 | recvWindow | 是 |
| `/sapi/v1/capital/deposit/address` (GET) | 提款地址（支持的网络）(USER_DATA) | coin | network, amount, recvWindow | 是 |
| `/sapi/v1/capital/deposit/hisrec` (GET) | 提款历史（支持的网络）(USER_DATA) | 无 | includeSource, coin, status, startTime, endTime, offset, limit, recvWindow, txId | 是 |
| `/sapi/v1/capital/deposit/address/list` (GET) | 带网络获取提款地址列表 (USER_DATA) | coin | network | 是 |
| `/sapi/v1/capital/withdraw/address/list` (GET) | 获取提款地址列表 (USER_DATA) | 无 | 无 | 是 |
| `/sapi/v1/capital/withdraw/quota` (GET) | 获取提款额度 (USER_DATA) | 无 | 无 | 是 |
| `/sapi/v1/capital/deposit/credit-apply` (POST) | 一键到账提款申请（用于过期地址提款）(USER_DATA) | 无 | depositId, txId, subAccountId, subUserId | 是 |
| `/sapi/v1/capital/withdraw/history` (GET) | 提款历史（支持的网络）(USER_DATA) | 无 | coin, withdrawOrderId, status, offset, limit, idList, startTime, endTime, recvWindow | 是 |
| `/sapi/v1/capital/withdraw/apply` (POST) | 提款 (USER_DATA) | coin, address, amount | withdrawOrderId, network, addressTag, transactionFeeFlag, name, walletType, recvWindow | 是 |
| `/sapi/v1/system/status` (GET) | 系统状态 (System) | 无 | 无 | 否 |
| `/sapi/v1/addressVerify/list` (GET) | 获取地址验证列表 (USER_DATA) | 无 | recvWindow | 是 |
| `/sapi/v1/localentity/broker/deposit/provide-info` (PUT) | 提交提款问卷（适用于需要旅行规则的本地实体）(支持的网络) (USER_DATA) | subAccountId, depositId, questionnaire, beneficiaryPii, signature | network, coin, amount, address, addressTag | 是 |
| `/sapi/v1/localentity/broker/withdraw/apply` (POST) | 经纪人提款（适用于需要旅行规则的本地实体的经纪人）(USER_DATA) | address, coin, amount, withdrawOrderId, questionnaire, originatorPii, signature | addressTag, network, addressName, transactionFeeFlag, walletType | 是 |
| `/sapi/v2/localentity/deposit/history` (GET) | 提款历史 V2（适用于需要旅行规则的本地实体）(支持的网络) (USER_DATA) | 无 | depositId, txId, network, coin, retrieveQuestionnaire, startTime, endTime, offset, limit | 是 |
| `/sapi/v1/localentity/deposit/history` (GET) | 提款历史（适用于需要旅行规则的本地实体）(支持的网络) (USER_DATA) | 无 | trId, txId, tranId, network, coin, travelRuleStatus, pendingQuestionnaire, startTime, endTime, offset, limit | 是 |
| `/sapi/v2/localentity/deposit/provide-info` (PUT) | 提交提款问卷 V2（适用于需要旅行规则的本地实体）(支持的网络) (USER_DATA) | depositId, questionnaire | 无 | 是 |
| `/sapi/v1/localentity/deposit/provide-info` (PUT) | 提交提款问卷（适用于需要旅行规则的本地实体）(支持的网络) (USER_DATA) | tranId, questionnaire | 无 | 是 |
| `/sapi/v1/localentity/vasp` (GET) | VASP 列表（适用于需要旅行规则的本地实体）(支持的网络) (USER_DATA) | 无 | recvWindow | 是 |
| `/sapi/v1/localentity/questionnaire-requirements` (GET) | 检查问卷要求（适用于需要旅行规则的本地实体）(支持的网络) (USER_DATA) | 无 | recvWindow | 是 |
| `/sapi/v2/localentity/withdraw/history` (GET) | 提款历史 V2（适用于需要旅行规则的本地实体）(支持的网络) (USER_DATA) | 无 | trId, txId, withdrawOrderId, network, coin, travelRuleStatus, offset, limit, startTime, endTime, recvWindow | 是 |
| `/sapi/v1/localentity/withdraw/history` (GET) | 提款历史（适用于需要旅行规则的本地实体）(支持的网络) (USER_DATA) | 无 | trId, txId, withdrawOrderId, network, coin, travelRuleStatus, offset, limit, startTime, endTime, recvWindow | 是 |
| `/sapi/v1/localentity/withdraw/apply` (POST) | 提款（适用于需要旅行规则的本地实体）(USER_DATA) | coin, address, amount, questionnaire | withdrawOrderId, network, addressTag, transactionFeeFlag, name, walletType, recvWindow | 是 |

---

## 参数

### 常见参数

* **recvWindow**:  (例如，5000)
* **type**: 
* **startTime**:  (例如，1623319461670)
* **endTime**:  (例如，1641782889000)
* **limit**: 最小值 7，最大值 30，默认值 7 (例如，7)
* **spotBNBBurn**: "true" 或 "false"；决定是否使用 BNB 支付现货交易费
* **interestBNBBurn**: "true" 或 "false"；决定是否使用 BNB 支付保证金贷款利息
* **asset**: 如果 asset 为空，则查询用户拥有的所有正资产。
* **accountType**: `SPOT` 或 `MARGIN`，默认 `SPOT` (例如，SPOT)
* **tranId**: 交易 ID (例如，1)
* **clientTranId**: 唯一标识符 (例如，1)
* **startTime**:  (例如，1623319461670)
* **endTime**:  (例如，1641782889000)
* **current**: 当前页，默认 1，最小值为 1 (例如，1)
* **size**: 页大小，默认 10，最大值为 100 (例如，10)
* **asset**: 
* **clientId**: 请求的唯一 ID (例如，1)
* **targetAsset**: 
* **thirdPartyClientId**:  (例如，1)
* **dustQuotaAssetToTargetAssetPrice**:  (例如，1.0)
* **targetAsset**: 
* **needBtcValuation**: true 或 false
* **email**: 
* **type**: 委托/撤销
* **fromSymbol**: 
* **toSymbol**: 
* **quoteAsset**: `USDT`，`ETH`，`USDC`，`BNB` 等，默认 `BTC` (例如，BTC)
* **symbol**: 
* **needBtcValuation**: 是否需要 btc 估值。
* **amount**:  (例如，1.0)
* **coin**: 
* **network**: 
* **amount**:  (例如，1.0)
* **includeSource**: 默认: `false`，设置为 `true` 时返回 `sourceAddress` 字段
* **coin**: 
* **status**: 0(0:已发送邮件，2:等待批准 3:已拒绝 4:处理中 6:已完成)
* **offset**: 默认: 0
* **txId**:  (例如，1)
* **depositId**: 提款记录 ID，优先使用 (例如，1)
* **subAccountId**: 云用户子账户 ID (例如，1)
* **subUserId**: 父用户子用户 ID (例如，1)
* **withdrawOrderId**: 退款的客户端 ID，如果在 POST `/sapi/v1/capital/withdraw/apply` 中提供，可以在此查询。 (例如，1)
* **idList**: POST `/sapi/v1/capital/withdraw/apply` 响应中返回的 ID 列表，以 `,` 分隔
* **address**: 
* **addressTag**: XRP、XMR 等货币的二级地址标识符
* **transactionFeeFlag**: 在进行内部转账时，`true` 表示将手续费返回到目标账户；`false` 表示将手续费返回到出发账户。默认 `false`。
* **name**: 地址的描述。地址簿容量为 200，名称中的空格应编码为 `%20`
* **walletType**: 提款的钱包类型，0-现货钱包，1-资金钱包。默认 walletType 是钱包下的当前“选中钱包”在 Fiat 和 Spot/Funding->Deposit 下。
* **subAccountId**: 外部用户 ID。 (例如，1)
* **depositId**: 钱包提款 ID (例如，1)
* **questionnaire**: JSON 格式问卷答案。
* **beneficiaryPii**: JSON 格式受益人 Pii。
* **address**: 
* **signature**: 必须是最后一个参数。
* **addressName**: 地址的描述。地址簿容量为 200，名称中的空格应编码为 `%20`
* **withdrawOrderId**: 客户定义的退款 ID（即客户的内部退款 ID） (例如，1)
* **originatorPii**: JSON 格式发起人 Pii，见 StandardPii 部分以下
* **depositId**: 以逗号(,)分隔的钱包 tran ID 列表。 (例如，1)
* **retrieveQuestionnaire**: true: 返回响应中的 `questionnaire`。
* **trId**: 以逗号(,)分隔的旅行规则记录 ID 列表。 (例如，1)
* **tranId**: 以逗号(,)分隔的钱包 tran ID。 (例如，1)
* **travelRuleStatus**: 0:已完成，1:待处理，2:失败
* **pendingQuestionnaire**: true: 仅返回待处理提款问卷的记录。false/未提供: 返回所有记录。
* **tranId**: 钱包 tran ID (例如，1)


## 认证

对于需要认证的端点，您需要提供 Binance API 凭证。
所需凭证：

* apiKey: 您的 Binance API 密钥（用于头部）
* secretKey: 您的 Binance API 密钥（用于签名）

基础 URL：
* 主网：https://api.binance.com

## 安全

### 分享凭证

用户可以通过不同方式提供 Binance API 凭证。代理将尝试使用前两种方式自动检索凭证，但用户也可以明确告诉代理他们已设置凭证或将其存储在 `.env` 文件中，代理应在他们这样做时重新读取该文件。代理还可以使用前两种方法进行 HTTP 请求，而无需用户确认。

1. **环境变量**

仅搜索以下特定变量（永远不要导出完整的环境）：

**授权环境变量**
- 主网：`BINANCE_API_KEY` 和 `BINANCE_SECRET_KEY`

在一个 exec 调用中读取并使用，以便原始密钥永远不会进入代理的上下文中：
```bash
KEY="$BINANCE_API_KEY"
SECRET="$BINANCE_SECRET_KEY"

response=$(curl -s -X GET "$URL" \
  -H "X-MBX-APIKEY: $KEY" \
  --data-urlencode "param1=value1")

echo "$response"
```

环境变量必须在 OpenClaw 启动之前设置。它们在进程启动时继承，并且不能注入到正在运行的实例中。如果您需要在不重新启动的情况下添加或更新凭证，请使用密钥文件（见选项 2）。

2. **密钥文件 (.env)**

检查 `~/.openclaw/secrets.env` ， `~/.env`，或工作区中的 `.env` 文件。使用 `grep` 逐个读取密钥，永远不要源整个文件：
```bash
# 按顺序尝试所有凭证位置
API_KEY=$(grep '^BINANCE_API_KEY=' ~/.openclaw/secrets.env 2>/dev/null | cut -d= -f2-)
SECRET_KEY=$(grep '^BINANCE_SECRET_KEY=' ~/.openclaw/secrets.env 2>/dev/null | cut -d= -f2-)

# 备用：搜索已知目录中的 .env（KEY=VALUE 格式然后原始行格式）
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

此文件可以随时更新而无需重新启动 OpenClaw，每次调用时都会读取新鲜的密钥。用户可以告诉您变量已设置或存储在 `.env` 文件中，您应在他们这样做时重新读取该文件。

3. **内联文件**

发送一个文件，其中内容格式如下：

```bash
abc123...xyz
secret123...key
```

* 永远不要运行 `printenv`，`env`，`export` 或设置不带特定变量名的密钥
* 永远不要在 `env` 文件上运行 `grep` 而不锚定到特定密钥（`^VARNAME=`）
* 永远不要将密钥文件源到 shell 环境中（`source .env` 或 `. .env`）
* 仅读取当前任务所需的凭证
* 永远不要在输出或回复中回显或记录原始凭证
* 永远不要将 `TOOLS.md` 提交到版本控制，如果其中包含真实凭证——将其添加到 `.gitignore` 中

### 永远不要泄露 API 密钥和密钥

永远不要泄露 API 密钥和密钥文件的位置。

永远不要将 API 密钥和密钥发送到除主网和测试网以外的任何网站。

### 永远不要显示完整密钥

当向用户显示凭证时：
- **API Key:** 显示前 5 个 + 最后 4 个字符：`su1Qc...8akf`
- **Secret Key:** 始终遮盖，仅显示最后 5 个：`***...aws1`

请求凭证时示例响应：
账户：main
API Key: su1Qc...8akf
Secret: ***...aws1

### 列出账户

当列出账户时，显示名称和环境——永远不要密钥：
Binance 账户：
* main (主网)
* futures-keys (主网)

### 主网中的交易

当在主网执行交易时，始终在继续之前与用户确认，通过要求他们写入 "CONFIRM" 来进行。
