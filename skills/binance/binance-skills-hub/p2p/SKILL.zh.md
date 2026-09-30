---
name: p2p
description: '币安P2P交易助手，用于查询P2P/C2C市场广告的自然语言交互，用户的P2P订单历史、订单详情及申诉跟踪，以及广告发布与管理。


  在用户询问P2P价格、搜索/选择广告、比较支付方式、查看P2P订单历史、检查订单详情/申诉状态、查询投诉、发布/更新/管理P2P广告，或查看商家资料时使用。


  不适用于现货/期货价格、交易所交易、存款/提款、链上转账或任何与P2P/C2C无关的内容。'
---

# Binance P2P 交易技巧

通过自然语言查询帮助用户与 **Binance P2P (C2C)** 进行交互。

## 何时使用 / 何时不建议使用

### 用户想要以下功能时使用此技能：
- 查询加密货币/法币对（例如 USDT/CNY）的 **P2P** 买入/卖出报价。
- 搜索 **P2P 广告** 并按支付方式、限额、商家质量进行筛选。
- 比较不同支付方式的价格（例如 支付宝 对比 银行转账）。
- 查看 **自己的 P2P 订单历史记录/摘要**（需要 API 密钥）。
- 查询 **订单详情** 并查看完整订单时间线（需要 API 密钥）。
- 查询 **申诉/投诉状态** 并查看投诉历史记录（需要 API 密钥）。
- **提交申诉证据**（上传文件 + 提交描述）（需要 API 密钥）。
- **查看投诉流程时间线**（操作流程、客服备注、证据）。
- **取消现有申诉**（撤回投诉，不可逆）（需要 API 密钥）。
- **查看订单的可用投诉原因**（需要 API 密钥）。
- **发布、更新或管理 P2P 广告**（需要 API 密钥 + 商家权限）。
- 查看 **商家资料** 及其广告列表（需要 API 密钥）。
- 查询 **支持的数字货币和法币**（需要 API 密钥）。

### 用户询问以下内容时，不建议使用此技能：
- 现货/兑换价格、期货/衍生品、保证金、交易机器人。
- 存入/取出、钱包转账、链上交易。
- 创建/取消订单、释放代币（交易操作）。取消 **申诉**（投诉）是支持的。
- 提交新的申诉（提交投诉被推迟；仅支持补充现有申诉的证据）。
- 在订单对话中发送聊天消息。

### 如果缺少关键输入，请询问澄清问题（不要猜测）：
- `fiat`（例如 CNY）
- `asset`（例如 USDT）
- 用户意图：**买入加密货币** 或 **卖出加密货币**
- 优先支付方式
- 目标金额（可选但建议用于广告筛选）

## 核心概念

### `tradeType` 映射（避免歧义）
- 用户想要 **买入加密货币**（支付法币，接收 USDT/BTC）→ `tradeType=BUY`
- 用户想要 **卖出加密货币**（接收法币，支付 USDT/BTC）→ `tradeType=SELL`

当用户的措辞不明确时，始终在回复中反映此映射。

## 功能

### 第一阶段 — 公开市场（无需授权）
- 报价 P2P 价格
- 搜索广告
- 比较支付方式
- 按 限额 和 商家指标 筛选/排序广告

### 第二阶段 — 个人订单（需要 API 密钥）
- 列出 P2P 订单历史记录
- 按 交易类型 / 时间范围 筛选
- 提供摘要统计数据

### 第三阶段 — 订单 & 申诉 + 广告发布 & 管理（需要 API 密钥）
- 按订单号查询订单详情
- 使用丰富筛选器列出订单（状态、交易类型、资产、日期范围）
- 查看订单时间线（创建 → 支付 → 释放 → 完成）
- 检测申诉状态并显示申诉详情
- 按筛选器查询投诉/申诉记录
- 获取市场参考价格用于定价决策
- 上传申诉证据文件（S3 预签名 URL + 提交）
- 查看投诉流程时间线 / 流程详情
- 取消现有申诉 / 撤回投诉
- 获取订单的可用投诉原因
- 搜索和分析市场广告分布
- 获取当前用户的可用广告类别
- 获取用户配置的支付方式
- 列出所有系统交易方式
- 发布新广告（带确认）
- 更新现有广告参数（带确认）
- 更新广告状态：在线 / 离线 / 关闭（带确认）
- 查看 商家资料 和 广告列表
- 列出所有支持的数字货币
- 列出所有支持的法币

## 环境配置

### 基础 URL（生产环境）

| 逻辑名称 | URL |
|-------------|-----|
| `SAPI_BASE` | `https://api.binance.com` |
| `MGS_BASE` | `https://www.binance.com` |
| `C2C_WEB` | `https://c2c.binance.com` |

### 实现提示（用于代码生成）

当技能生成 curl / Python / JS 代码时，使用这些固定的基础 URL：

```python
import os

SAPI_BASE = "https://api.binance.com"
MGS_BASE  = "https://www.binance.com"
C2C_WEB   = "https://c2c.binance.com"

def common_headers(api_key: str) -> dict:
    return {
        "X-MBX-APIKEY": api_key,
        "User-Agent": "binance-wallet/1.0.0 (Skill)",
    }

# 使用示例：
# f"{SAPI_BASE}/sapi/v1/c2c/agent/orderMatch/getUserOrderDetail"
# f"{MGS_BASE}/bapi/c2c/v1/public/c2c/agent/quote-price"
# f"{C2C_WEB}/en/adv?code={advNo}"
# headers = common_headers(os.getenv("BINANCE_API_KEY"))
```

```bash
# Bash 等价：
SAPI_BASE="https://api.binance.com"
MGS_BASE="https://www.binance.com"
C2C_WEB="https://c2c.binance.com"
```

> **注意**：SAPI 签名使用 HMAC SHA256，无需参数排序。

## 安全与隐私规则

### 凭证
- 必要的环境变量：
    - `BINANCE_API_KEY`（作为请求头发送）
    - `BINANCE_SECRET_KEY`（用于签名）

### 不显示完整密钥
- API 密钥：显示 **前 5 个 + 最后 4 个** 字符：`abc12...z789`
- 密钥：始终遮盖；显示 **仅最后 5 个**：`***...c123`

### 最小权限原则
- Binance API 权限：**仅启用读取**（第一阶段/第二阶段）。
- 第三阶段广告管理额外需要写入权限。
- 不要请求/鼓励超出所需范围的提现或修改权限。

### 存储指南
- 优先使用环境注入（会话/运行时环境变量）而非写入磁盘。
- 如果用户明确同意，才写入 `.env`。
- 保存前确保 `.env` 在 `.gitignore` 中。

## ⚠️ 关键：SAPI 签名（与标准 Binance API 不同）

### 参数排序
- **不要** 对 SAPI 请求的参数进行排序。
- 构建 URL 查询字符串时，保持原始插入顺序。

示例：
```py
# ✅ 正确（SAPI）：保持插入顺序
params = {"page": 1, "rows": 20, "timestamp": 1710460800000}
query_string = urlencode(params)  # 无需排序

# ❌ 错误（仅标准 Binance API）：排序
query_string = urlencode(sorted(params.items()))
```

### 签名细节
参考：`references/authentication.md`，了解：
- RFC 3986 百分号编码
- HMAC SHA256 签名过程
- 必要的请求头（包括 User-Agent）
- SAPI 特定的参数排序

## API 概述

### 公开查询（MGS C2C Agent API — 无需授权）
基础 URL：`https://www.binance.com`

| 端点 | 方法 | 参数 | 使用 |
|----------|--------|--------|-------|
| `/bapi/c2c/v1/public/c2c/agent/quote-price` | GET | fiat, asset, tradeType | 快速价格报价 |
| `/bapi/c2c/v1/public/c2c/agent/ad-list` | GET | fiat, asset, tradeType, limit, order, tradeMethodIdentifiers | 搜索广告 |
| `/bapi/c2c/v1/public/c2c/agent/trade-methods` | GET | fiat | 支付方式 |

参数说明：
- `tradeType`：`BUY` 或 `SELL`（视为不区分大小写）
- `limit`：1–20（默认 10）
- `tradeMethodIdentifiers`：作为 **纯字符串** 传递（不是 JSON 数组）— 例如 `tradeMethodIdentifiers=BANK` 或 `tradeMethodIdentifiers=WECHAT`。值 **必须** 使用 `trade-methods` 端点返回的 `identifier` 字段（见流程说明）。⚠️ 不要使用 JSON 数组语法如 `["BANK"]` — 它将返回空结果。

### 流程：按支付方式比较价格

当用户想要比较不同支付方式的价格（例如 "支付宝 对比 微信支付"）时，请遵循以下两步流程：

**步骤 1** — 调用 `trade-methods` 获取目标法币的正确标识符：
```
GET /bapi/c2c/v1/public/c2c/agent/trade-methods?fiat=CNY
→ [{"identifier":"ALIPAY",...}, {"identifier":"WECHAT",...}, {"identifier":"BANK",...}]
```

**步骤 2** — 将标识符作为纯字符串通过 `tradeMethodIdentifiers` 传递到 `ad-list`，每个支付方式一个请求，然后比较：
```
GET /bapi/c2c/v1/public/c2c/agent/ad-list?fiat=CNY&asset=USDT&tradeType=BUY&limit=5&tradeMethodIdentifiers=ALIPAY&tradeMethodIdentifiers=WECHAT
```
比较每个结果集中的最佳价格。

> **重要提示**：不要硬编码标识符值如 `"Alipay"` 或 `"BANK"`。始终先调用 `trade-methods` 获取给定法币货币的确切 `identifier` 字符串。

### 个人订单（Binance SAPI — 需要授权）
基础 URL：`https://api.binance.com`

| 端点 | 方法 | 授权 | 使用 |
|----------|--------|------|-------|
| `/sapi/v1/c2c/orderMatch/listUserOrderHistory` | GET | 是 | 订单历史记录 |
| `/sapi/v1/c2c/orderMatch/getUserOrderSummary` | GET | 是 | 用户统计 |

授权要求：
- 请求头：`X-MBX-APIKEY`
- 查询参数：`timestamp` + `signature`
- 请求头：`User-Agent: binance-wallet/1.0.0 (Skill)`

## 输出格式指南

### 价格报价
- 当可用时显示双方（最佳买入 / 最佳卖出）。
- 使用法币符号和 2 位小数格式。

示例：
```
USDT/CNY (P2P)
- 买入 USDT（你买入加密货币）：¥7.20
- 卖出 USDT（你卖出加密货币）：¥7.18
```

### 广告列表
返回 **前 N 项**，使用稳定的架构：
1) adNo（广告编号/标识符）
2) price（法币）
3) 商家名称
4) 完成率
5) 限额
6) 支付方式（标识符）

除非 API 返回，否则避免生成参数化外部 URL。

**下单（当用户请求时）：**
- 此技能不支持自动下单。
- 当用户想要下单时，提供使用 adNo 的直接链接到特定广告：
  ```
  https://c2c.binance.com/en/adv?code={adNo}
  ```
    - `{adNo}`：广告编号/标识符来自广告列表结果

  示例：`https://c2c.binance.com/en/adv?code=123`
- 这将打开特定广告详情页面，用户可以直接使用选定的广告下单。

### 个人订单
- 时间格式：`YYYY-MM-DD HH:mm (UTC+0)` — 始终以 UTC 时区显示
- 包括：类型、资产/法币、金额、总额、状态
- 过滤时提供简短的摘要行（计数 + 总计）

**时间字段转换（用于 `listUserOrderHistory` 中的 `createTime`）：**
- `createTime` 字段返回 **毫秒**（13 位）的 Unix 时间戳。
- 转换为人类可读格式，在 **UTC+0 时区**：
  ```
  # Python 示例
  from datetime import datetime, timezone
  readable_time = datetime.fromtimestamp(createTime / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M (UTC+0)')
  
  # JavaScript 示例
  const readableTime = new Date(createTime).toISOString().replace('T', ' ').slice(0, 16) + ' (UTC+0)';
  // 或更明确地：
  const date = new Date(createTime);
  const readableTime = date.getUTCFullYear() + '-' +
    String(date.getUTCMonth() + 1).padStart(2, '0') + '-' +
    String(date.getUTCDate()).padStart(2, '0') + ' ' +
    String(date.getUTCHours()).padStart(2, '0') + ':' +
    String(date.getUTCMinutes()).padStart(2, '0') + ' (UTC+0)';
  ```
- 始终向用户显示转换后的时间及时区信息，而不是原始时间戳。

## 错误处理（面向用户）

- 无效 API 密钥 (-2015)：提示验证 `.env` / API 管理。
- 签名失败 (-1022)：警告关于错误密钥、排序参数或过期时间戳。
- 时间戳无效 (-1021)：建议时间同步 / 重新生成时间戳。
- 速率限制：建议稍后重试。

## 设计限制

此技能不：
- 下单/取消订单
- 标记为已支付 / 释放代币
- 提交新的申诉 / 提交投诉（仅支持补充现有申诉的证据）
- 发布/修改广告（第一阶段/第二阶段 — 第三阶段为商家添加广告管理）
- 暴露超出历史记录/摘要所需所需的敏感订单详情端点

对于应用内操作，引导用户到官方 P2P 订单页面（仅作为一般入口）。

## 开发者说明

### 版本检查（每对话首次调用）
在每对话中首次调用此技能时，调用：

- `GET /bapi/c2c/v1/public/c2c/agent/check-version?version=2.0.0` (基础：`https://www.binance.com`)

行为：
- 如果 `needUpdate=true`：显示：`P2P 技能的新版本可用（当前：{clientVersion}，最新：{latestVersion}），建议更新。`
- 否则 / 失败：静默处理。

### 客户端操作
- 资产筛选：如果 API 不支持，则本地获取后筛选。
- 聚合：当摘要端点不足时，在客户端计算总计。

---

# 第三阶段 — 订单 & 申诉 + 广告发布 & 管理

第三阶段将技能从只读市场/订单查询扩展到 **写入操作**（广告管理）和 **高级订单工作流**（订单详情、申诉/投诉跟踪）。

## 第三阶段设计约束

| 约束 | 详细信息 |
|-----------|---------|
| 认证 | 所有第三阶段功能都需要 API 密钥 + 密钥 |
| 写入操作确认 | 任何写入操作（发布广告、更新广告、更改状态）**在执行前必须显示操作摘要并获取明确的用户确认** |
| API 密钥权限 | 第一阶段仅需 "启用读取"；第三阶段广告管理额外需要写入权限 |
| 隐私遮罩 | 永不显示交易对手敏感信息（银行卡、支付宝账户、电话、邮箱、真实姓名）或内部 ID（`payId`）。即使 API 返回这些字段，**也应在用户界面输出中过滤它们**。对于支付方式，仅显示 `tradeMethodName`（例如 "支付宝"） |

---

## 场景 1：订单查询 & 申诉处理

### 1.1 查询订单详情

**触发示例：**
- "查看订单 20260315123456 的详情"
- "我最近那笔 USDT 买入订单怎么样了？"
- "帮我查一下这个订单号"
- "Show me the details of order 20260315123456"

**行为：**
1. 如果用户提供订单号 → 调用 `getUserOrderDetail`
2. 如果用户模糊描述订单 → 调用 `listOrders` 带筛选器，然后让用户选择
3. 根据订单状态分支：

**状态分支处理：**

| 状态 | 操作 |
|--------|--------|
| 已完成 (4) | 显示完整时间线（创建 → 支付 → 确认 → 完成），结束 |
| 已取消 (6) / 已过期 (7) | 显示取消原因（超时 / 手动 / 系统），结束 |
| 进行中 (1=未支付, 2=已支付, 3=释放中) | 显示当前步骤 + 倒计时计时器 |
| 申诉中 (5) | 自动进入 1.2 — 显示申诉状态 |

**输出格式（订单详情）：**
```
📋 订单号：{orderNumber}
├─ 类型：{tradeType} {asset}
├─ 金额：{amount} {asset} @ {price} {fiatUnit}
├─ 总计：{fiatSymbol}{totalPrice}
├─ 状态：{orderStatus description}
├─ 交易对手：{buyerNickname / sellerNickname}
├─ 创建时间：{createTime in UTC+0}
│
├─ 时间线：
│  ├─ 创建：     {createTime}
│  ├─ 支付：        {notifyPayTime or "—"}
│  ├─ 确认：   {confirmPayTime or "—"}
│  └─ 取消：   {cancelTime or "—"}
│
├─ 手续费：maker {commissionRate}% = {commission} {asset}
│              taker {takerCommissionRate}% = {takerCommission} {asset}
└─ 投诉：{isComplaintAllowed ? "允许" : "不允许"} | 状态：{complaintStatus or "无"}
```

**倒计时显示（对于进行中的订单）：**
- 如果状态=1（未支付）：显示 "支付截止：{notifyPayEndTime}" 带剩余时间
- 如果状态=2（已支付）：显示 "释放截止：{confirmPayEndTime}" 带剩余时间

### 1.2 查看申诉/投诉状态

**触发：**
- 自动触发（当订单状态 = 申诉中 (5)）
- "这个申诉进展到哪了？"
- "订单 20260315123456 的申诉怎么样了？"
- "What's the appeal status?"

**行为：**
1. 调用 `query-complaints` 带订单号
2. 结构化格式显示投诉信息

**输出格式：**
```
⚠️ 订单 {orderNo} 的申诉状态
├─ 投诉号：{complaintNo}
├─ 状态：{complaintStatus description}
├─ 角色：{roleIdentity} (投诉人 / 被投诉人)
├─ 原因：{reason}
├─ 创建时间：{complaintCreateTime}
├─ 订单资产：{orderAsset} | 法币：{orderFiat}
├─ 订单金额：{orderAmount} ({fiatSymbol})
├─ USDT 金额：{orderAmountInUsdt}
└─ 争议金额：{disputeAmount}
```

**后续指导（在状态块后追加，基于投诉状态）：**

| 投诉状态 | 指引显示 |
|--------|--------|
| 0 (被申诉人处理中) | "等待对方回复。您将有更新通知。" |
| 1 (申诉人处理中) | "⚡ 需要操作 — 您需要提供证据或回复。说 **\"为订单 {orderNo} 提交证据\"** 立即上传证明。" |
| 2 (客服处理中) | "💡 在此阶段双方仍可提交证据。您可以直接通过此技能提交证据 — 说 **\"为订单 {orderNo} 提交证据\"** 或 **\"提交证据\"** 上传付款证明、截图或其他支持文件。" |
| 3 (已完成) | "此申诉已解决。" |
| 4 (已取消) | "此申诉已取消。" |

> **必须遵循：** 当 `complaintStatus` 为 0、1 或 2（申诉仍活跃）时，绝对不要告诉用户 "去应用程序" 或 "前往争议中心"。始终引导他们使用此技能提交证据。该技能支持完整的证据上传流程（场景 1.5）。

**投诉状态映射：**

| 状态代码 | 显示名称 | 描述 |
|--------|--------|--------|
| 0 | 被申诉人处理中 | 投诉已发起，等待对方回复 |
| 1 | 申诉人处理中 | 等待申诉人提供证据或采取行动 |
| 2 | 客服处理中 | 客户服务审核中；双方均可提交证据 |
| 3 | 已完成 | 申诉已解决 |
| 4 | 申诉取消 | 申诉已撤回 |

> **重要提示：** 不要将这些与 `orderStatus` 代码混淆 — 它们是独立的枚举类型。
> 当 `complaintStatus=2`（客服处理中）时，应引导用户提交证据（如果需要）；不要告诉他们 "等待对方"。

### 1.3 投诉历史查询

**触发：**
- "查看我的所有投诉记录"
- "最近3个月有哪些投诉？"
- "列出我的投诉作为申诉人"

**行为：**
1. 调用 `query-complaints` 并带可选过滤器（roleIdentity、状态、日期范围）
2. 默认：如果没有指定日期，则为最后 90 天
3. 显示分页结果

**输出格式：**
```
📋 投诉记录 (总计：{total})
┌───────────┬──────────────┬──────────┬────────┬───────────────┐
│ 订单号    │ 投诉编号    │ 状态    │ 角色    │ 创建时间      │
├───────────┼──────────────┼──────────┼────────┼───────────────┤
│ {orderNo} │ {no}         │ {status} │ {role} │ {time UTC+0}  │
└───────────┴──────────────┴──────────┴────────┴───────────────┘
```

### 1.4 订单列表与历史

**触发：**
- "查看我的订单列表"
- "最近的 USDT 买入订单"
- "显示本周我完成的订单"

**行为：**
- 对于活跃/最近订单 → 使用 `listOrders`（更丰富的过滤器：advNo、状态、payType）
- 对于历史订单 → 使用 `listUserOrderHistory`（支持 tradeType、日期范围）

**输出格式（订单列表）：**
```
📋 订单 (页码 {page}，总计：{total})
┌──────────────┬──────┬───────┬──────────────┬────────┬───────────────┐
│ 订单号      │ 类型    │ 资产    │ 总价        │ 状态    │ 创建时间      │
├──────────────┼──────┼───────┼──────────────┼────────┼───────────────┤
│ {orderNo}    │ 买入    │ USDT  │ ¥{totalPrice}│ 已完成  │ {time UTC+0}  │
└──────────────┴──────┴───────┴──────────────┴────────┴───────────────┘
```

**订单状态代码映射：**

| 代码 | 名称 | 中文 |
|------|------|------|
| 0 | 处理中 | 处理中 |
| 1 | 未付款 | 未付款 |
| 2 | 已付款（未确认） | 已付款 |
| 3 | 放币处理中 | 放币处理中 |
| 4 | 已完成 | 已完成 |
| 5 | 申诉中 | 申诉中 |
| 6 | 已取消 | 已取消 |
| 7 | 超时取消（系统取消） | 超时取消 |

### 1.5 提交申诉证据

**触发：**
- "帮我上传这个截图作为申诉证据"
- "我要提交付款凭证"
- "为订单 228... 提交证据"
- "上传付款证明以提交我的申诉"
- 当订单状态为申诉（状态=5）且 `complaintStatus=2`（客服处理中）时自动建议

**行为（三步流程）：**

**步骤 1 — 获取预签名上传 URL：**
```
GET /sapi/v1/c2c/agent/file-upload/get-s3-presigned-url?fileName=proof.jpg&scenario=complaint
→ { "uploadUrl": "https://s3...presigned...", "filePath": "/client_upload/c2c/complaint/..." }
```

**步骤 2 — 上传文件到 S3：**
```bash
curl -X PUT -T /path/to/local/file.jpg "{uploadUrl}"
```
> 预签名 URL 有效期为 **5 分钟**。必须在窗口内完成上传。

**步骤 3 — 向 SAPI 提交证据：**
```
POST /sapi/v1/c2c/agent/complaint/submit-evidence
Body: { "orderNo": "228...", "description": "付款截图", "fileUrls": ["/client_upload/c2c/complaint/..."] }
→ { "data": true }
```

**支持的文件类型：**
`txt, doc, xls, docx, xlsx, jpg, jpeg, png, pdf, mp3, mp4, avi, rm, rmvb, mov, wmv`

**输出格式（上传进度）：**
```
📤 为订单 {orderNo} 提交证据
├─ 步骤 1/3：获取上传 URL... ✅
├─ 步骤 2/3：上传文件 "{fileName}"... ✅
├─ 步骤 3/3：提交证据...
│  ├─ 描述：{description}
│  └─ 文件：{n} 个文件
└─ 结果：✅ 成功提交证据

💡 提示：您可以通过说 "再上传一个文件" 提交更多证据
```

**输出格式（失败）：**
```
❌ 提交证据失败
├─ 步骤：{失败的步骤}
├─ 错误：{错误信息}
└─ 建议：{可操作的修复措施}
```

**常见错误：**
- `不支持的文件类型` → 检查文件扩展名；见上方支持的类型
- `预签名 URL 已过期` → 重新请求上传 URL（步骤 1）
- `订单不在申诉中` → 仅可对有活跃投诉的订单提交证据
- `文件过大` → 减小文件大小或拆分为多个文件

**写入操作确认规则：**
证据提交遵循与场景 2 写入操作相同的确认协议：
1. 显示将要提交的内容摘要（文件名、描述、订单号）
2. 等待用户确认后再执行步骤 3

**确认格式：**
```
📋 提交证据摘要
├─ 订单：{orderNo}
├─ 描述：{description}
├─ 将提交的文件：
│  1. {fileName1} ({fileType}, 已上传 ✅)
│  2. {fileName2} ({fileType}, 已上传 ✅)
└─ ⚠️ 确认提交？ (回复 "确认" 或 "confirm")
```

### 1.6 查看投诉处理时间线

**触发：**
- "查看申诉的处理流程"
- "这个申诉经历了哪些步骤？"
- "显示订单 228... 的投诉时间线"
- "申诉过程中发生了什么？"

**行为：**
1. 调用 `get-complaint-flows` 并带订单号（可选带投诉号）
2. 显示所有处理步骤的按时间顺序时间线

**输出格式：**
```
📜 投诉时间线：订单 {orderNo} (投诉 #{complaintNo})
│
├─ [{createTime}] {creatorNickName}
│  ├─ 类型：{infoType 描述}
│  ├─ 描述：{description}
│  ├─ 证据：{fileUrls 数量} 个文件已附加
│  └─ 来源：{source}
│
├─ [{createTime}] {operatorName 或 creatorNickName}
│  ├─ 类型：{infoType 描述}
│  ├─ 备注：{remark}
│  └─ 证据：{fileUrls 或 "无"}
│
└─ ... (按时间顺序)

💡 操作：提交证据 | 刷新以检查更新
```

**Info type mapping（用于显示）：**

| infoType | 描述 |
|----------|------|
| 1 | 投诉已发起 |
| 2 | 提交证据 |
| 3 | 客服审核备注 |
| 4 | 解决方案/决定 |

> **注意：** 响应中的 `fileUrls` 是 CDN 组合 URL，可直接访问。
> `remarkHtml` 优先于 `remark` 用于渲染。

### 1.7 取消投诉/申诉

**触发：**
- "取消这个申诉"
- "我不想继续申诉了"
- "取消订单 228... 的申诉"
- "撤回我的投诉"

**⚠️ 这是一个破坏性操作 — 必须强制确认！**

取消申诉是 **不可逆的**。用户将放弃争议权，订单将按正常流程解决。代理必须严格遵守此严格确认协议：

**行为：**
1. 当用户表达取消意图时，首先显示明确警告
2. 等待明确确认 ("确认取消" / "confirm cancel" / "yes")
3. 然后才调用 `cancel-complaint` 并带订单号
4. 显示结果

**警告格式（执行前必须显示）：**
```
⚠️ 取消申诉确认
├─ 订单：{orderNo}
├─ 当前投诉状态：{如果可用，则显示之前的查询状态}
│
╔══════════════════════════════════════════════╗
║  警告：此操作无法撤销！                      ║
║  - 您的申诉将被永久撤回                      ║
║  - 您将失去通过申诉流程争议此订单的权利       ║
║  - 订单将按正常流程解决，无需客服干预        ║
╚══════════════════════════════════════════════╝
│
└─ 回复 "确认取消" 或 "confirm cancel" 以继续
```

**成功：**
```
✅ 申诉已取消
├─ 订单：{orderNo}
├─ 状态：申诉已撤回
└─ 订单将按正常流程解决。
```

**失败：**
```
❌ 取消失败
├─ 订单：{orderNo}
├─ 原因：{错误信息}
└─ 可能原因：无活跃申诉、订单已解决或权限不足。
```

**必须遵循的规则：**
- 绝不取消而不显示警告并接收明确确认
- 如果用户说任何含糊不清的话（如在讨论其他事情时说 "算了" / "never mind"），不要将其解释为取消意图 — 请求澄清
- 如果投诉状态已解决/关闭，应告知用户而不是尝试 API 调用

### 1.8 获取投诉理由

**触发：**
- "我可以用什么理由申诉？"
- "我可以用什么理由申诉？"
- "显示此订单的可用投诉理由"
- "投诉理由有哪些？"

**行为：**
1. 调用 `get-complaint-reasons` 并带订单号
2. 显示可用理由代码和描述的列表

**输出格式：**
```
📋 订单 {orderNo} 的可用投诉理由
│
├─ [{reasonCode}] {reasonDesc}
├─ [{reasonCode}] {reasonDesc}
├─ [{reasonCode}] {reasonDesc}
└─ ...

💡 注意：这是您在发起申诉时可使用的理由。
   此技能不支持发起申诉 — 仅用于查看理由。
```

> **注意：** 这是一个只读信息查询。技能不支持实际提交新投诉（这需要用户使用应用程序）。

---

## 场景 2：广告发布与管理

### ⚠️ 写入操作安全规则

**场景 2 中的所有写入操作** 必须遵循此协议：

1. **预检查**：验证用户是否有商家权限（API 本身会检查，但必须明确告知用户 403/权限被拒绝）
2. **显示摘要**：在执行任何写入 API 之前，显示完整的操作摘要
3. **明确确认**：等待用户说 "确认" / "confirm" / "发布" / "yes" 才继续
4. **绝不自动执行**：即使用户在初始请求中说 "直接做吧"，也必须先显示摘要

### 2.1 市场分析与参考价格

**触发：**
- "我想发布一个 USDT/CNY 的卖单广告"
- "帮我挂一个 BTC 买单"
- "当前市场参考价是多少？"
- "USDT/CNY 的参考价格是多少？"

**行为：**
1. 调用 `getReferencePrice` 获取市场参考价格
2. 调用 `search` 分析当前市场广告分布
3. 提供定价情报以帮助用户决策

**输出格式（参考价格）：**
```
📊 市场参考价格
├─ 资产：{asset} / {fiatCurrency}
├─ 参考价格：{currencySymbol}{referencePrice}
├─ 价格精度：{priceScale} 位小数
└─ 资产精度：{assetScale} 位小数
```

**输出格式（市场分析）：**
```
📊 市场广告分析：{asset}/{fiat} ({tradeType})
├─ 活跃广告总数：{total}
├─ 价格范围：{min} ~ {max}
├─ 前 5 个广告：
│  1. {advNo} | {price} | {surplusAmount} {asset} | 限价：{min}~{max} | {merchantNick}
│     └─ 条款：{remarks 或 "—"}
│  2. ...
└─ 推荐价格：基于参考价格 + 市场建议的价格
```

### 2.2 广告配置

**触发：**
- "使用浮动价格，溢价 0.5%"
- "加上支付宝"
- "就按推荐的来"
- "单价改成 6.99，限额改到 1000-100000"

**发布前准备工作流程：**

**步骤 1** — 获取可用分类：
```
GET /sapi/v1/c2c/agent/ads/getAvailableAdsCategory
→ {"advClassifies": ["mass", "profession", ...]}
```

**步骤 2** — 获取用户的支付方式（对于 SELL 广告，需要 payId）：
```
GET /sapi/v1/c2c/agent/ads/getPayMethodByUserId
→ [{"payId": 123, "identifier": "ALIPAY", "tradeMethodName": "支付宝"}]
```
> **显示规则：** 仅向用户显示 `tradeMethodName`（例如 "支付宝"、"微信"、"银行转账"）。
> `payId` 是仅在 API 请求体中使用的内部标识符 — **绝不在用户界面输出中暴露 payId 值**。

**步骤 3** — 获取所有系统交易方式（对于 BUY 广告，需要 identifier）：
```
POST /sapi/v1/c2c/agent/ads/listAllTradeMethods
→ [{"identifier": "ALIPAY", "tradeMethodName": "支付宝", ...}]
```

**广告参数参考：**

| 参数 | 必填 | 描述 |
|------|------|------|
| classify | 是 | 广告分类：mass / profession / block / cash（默认：mass） |
| tradeType | 是 | 0 = BUY, 1 = SELL |
| asset | 是 | 加密货币：BTC, ETH, USDT, BNB |
| fiatUnit | 是 | 法定货币：CNY, USD, 等。 |
| priceType | 是 | 1 = 固定价格, 2 = 浮动价格 |
| price | 条件 | 固定价格值（如果 priceType=1 则必填） |
| priceFloatingRatio | 条件 | 浮动比例 %（如果 priceType=2 则必填） |
| initAmount | 是 | 总加密货币数量 |
| maxSingleTransAmount | 是 | 每单最大法定货币金额 |
| minSingleTransAmount | 是 | 每单最小法定货币金额 |
| buyerKycLimit | 是 | 要求买家 KYC：0=否, 1=是 |
| tradeMethods | 是 | 支付方式：[{payId, identifier}] |
| payTimeLimit | 否 | 支付时间限制（分钟）（默认 15） |
| onlineNow | 否 | 立即上线（默认 true） |
| remarks | 否 | 广告交易条款/条件（最多 1000 字符，无加密货币相关词语） |
| autoReplyMsg | 否 | 订单创建时自动回复消息（最多 1000 字符） |
| buyerRegDaysLimit | 否 | 买家最小注册天数 |
| buyerBtcPositionLimit | 否 | 买家最小 BTC 持有量 |
| takerAdditionalKycRequired | 否 | 需要额外验证：0=否, 1=是 |
| launchCountry | 否 | 目标国家（默认：所有地区） |

**确认摘要格式：**
```
📋 广告配置摘要
┌────────────────────────────────────┐
│ 交易方向：{SELL/BUY} {asset}│
│ 法定货币：   {fiatUnit}        │
│ 价格类型：      {Fixed/Floating}  │
│ 价格：           {price or ratio%} │
│ 总数量：  {initAmount} {asset}│
│ 订单限额：     {min} ~ {max} {fiat}│
│ 支付方式： {method1, method2}│
│ 支付超时： {payTimeLimit} min│
│ 状态：          {Online/Offline}  │
├────────────────────────────────────┤
│ 高级设置：                 │
│ 买家 KYC： {Yes/No}              │
│ 最小注册天数： {days or "—"}      │
│ 最小 BTC： {amount or "—"}         │
│ 额外验证： {Yes/No}           │
│ 地区： {countries or "All"}    │
│ 条款： {text or "—"}           │
│ 自动回复： {text or "—"}        │
└────────────────────────────────────┘

⚠️ 请确认以发布 (回复 "确认" 或 "confirm")
```

### 2.3 发布广告

**触发：**
- "确认" / "confirm" / "发布"（在 2.2 摘要之后）

**行为：**
1. 用户确认 → 调用 `POST /sapi/v1/c2c/agent/ads/post`
2. 返回结果

**输出格式（成功）：**
```
✅ 广告发布成功！
├─ 广告编号：{advNo}
├─ 状态：在线
├─ 查看：https://c2c.binance.com/en/adv?code={advNo}
└─ 管理：说 "查看我的广告" 以查看所有您的广告
```

**输出格式（失败）：**
```
❌ 广告发布失败
├─ 错误：{error message}
└─ 建议：{可操作的修复措施}
```

**常见错误：**
- `Permission denied` → 用户不是已验证的商家
- `FIAT_ASSET_ILLEGAL` → BIDR 只能与 IDR 配对
- 余额不足 → 发布前检查资产余额

### 2.4 管理现有广告

**触发：**
- "查看我的广告" / "List my ads"
- "把第一条广告下线" / "下线第一条广告"
- "修改我的 USDT 卖单价格" / "更新我的 USDT 卖单价格"

#### 查看我的广告
调用 `POST /sapi/v1/c2c/agent/ads/listWithPagination`

```
📋 我的广告 (总数: {total})
┌────┬──────────────┬──────┬───────┬──────────┬─────────────┬──────────┬────────┐
│ #  │ 广告编号      │ 类型 │ 资产  │ 价格    │ 剩余      │ 限制    │ 状态    │
├────┼──────────────┼──────┼───────┼──────────┼─────────────┼──────────┼────────┤
│ 1  │ {advNo}      │ 出售  │ USDT  │ ¥{price} │ {surplus}   │ {min}~{max}│ 在线    │
│ 2  │ {advNo}      │ 购买  │ BTC   │ ¥{price} │ {surplus}   │ {min}~{max}│ 离线    │
└────┴──────────────┴──────┴───────┴──────────┴─────────────┴──────────┴────────┘

# 如果有任何广告有备注或autoReplyMsg，请在表格下方显示：
广告条款：
  #1: {remarks or "—"} | 自动回复: {autoReplyMsg or "—"}
  #2: {remarks or "—"} | 自动回复: {autoReplyMsg or "—"}

操作: "修改第1条广告价格" | "下架第2条" | "查看详情 {advNo}"
```

#### 查看广告详情
调用 `POST /sapi/v1/c2c/agent/ads/getDetailByNo`

**触发:** "查看详情 {advNo}" / "Show ad detail"

**输出格式:**
```
📄 广告详情: {advNo}
├─ 类型: {tradeType} {asset}/{fiatUnit}
├─ 价格: {currencySymbol}{price} ({priceType: 固定/浮动})
├─ 剩余: {surplusAmount} / {initAmount} {asset}
├─ 限制: {minSingleTransAmount} ~ {maxSingleTransAmount} {fiatUnit}
├─ 支付方式: {tradeMethodName1, tradeMethodName2}
├─ 状态: {status}
├─ 支付超时: {payTimeLimit} 分钟
│
├─ 交易条款:
│  {remarks or "未设置条款"}
│
├─ 自动回复消息:
│  {autoReplyMsg or "未设置自动回复"}
│
└─ 高级设置:
   ├─ 买家KYC: {Yes/No}
   ├─ 最小注册天数: {buyerRegDaysLimit or "—"}
   └─ 额外验证: {takerAdditionalKycRequired ? "是" : "否"}
```

> **`remarks` 和 `autoReplyMsg` 的显示规则:** 这些字段由 `getDetailByNo`、`listWithPagination` 和 `search` 返回。当存在且非空时，始终显示。当为 null/空时，显示 "—" 或类似 "未设置条款" 的占位符。切勿无声地省略该部分——用户应知道是否存在条款。

**广告状态代码映射:**

| 代码 | 显示 | 中文 |
|------|------|------|
| 1 | 在线 | 在线 |
| 2 | 离线 | 离线 |
| 4 | 已关闭 | 已关闭 |

#### 更新广告

**行为:**
1. 确定要更新的广告（通过列表中的 # 或 advNo）
2. 显示差异：旧值 → 新值
3. 等待确认
4. 调用 `POST /sapi/v1/c2c/agent/ads/update`

**确认格式:**
```
📝 更新广告: {advNo}
┌──────────────┬─────────────┬─────────────┐
│ 字段        │ 当前值      │ 新值        │
├──────────────┼─────────────┼─────────────┤
│ 价格        │ ¥7.20       │ ¥6.99       │
│ 最大限制    │ ¥50,000     │ ¥100,000    │
└──────────────┴─────────────┴─────────────┘

⚠️ 确认更新？ (回复 "确认" 或 "confirm")
```

#### 更新广告状态（在线 / 离线 / 关闭）

**行为:**
1. 确定目标广告——支持批量操作
2. 显示确认信息
3. 调用 `POST /sapi/v1/c2c/agent/ads/updateStatus`

**确认格式:**
```
🔄 状态更新
├─ 广告: {advNo1}, {advNo2}
├─ 操作: {Online → Offline}
└─ ⚠️ 确认？ (回复 "确认" 或 "confirm")
```

**结果格式:**
```
✅ 状态已更新: {n} 个广告 → {status}
# 或如果部分失败：
⚠️ 部分成功: {n} 个已更新，{m} 个失败
失败:
├─ {advNo}: {errorMessage}
```

---

## 场景 2 补充：商家与货币查询

### 查看商家资料

**触发:**
- "查看商家 {merchantNo} 的信息"
- "Show me merchant details"

**行为:** 调用 `GET /sapi/v1/c2c/agent/merchant/getAdDetails?merchantNo={merchantNo}`

**输出格式:**
```
👤 商家: {nickName}
├─ 类型: {userType}
├─ 总订单数: {orderCount}
├─ 30天订单数: {monthOrderCount}
├─ 30天完成率: {monthFinishRate}%
├─ 平均发布时间: {advConfirmTime}s
├─ 在线状态: {onlineStatus}
├─ 注册天数: {registerDays} 天
│
├─ 30天统计:
│  ├─ 平均发布: {avgReleaseTimeOfLatest30day}s
│  ├─ 平均支付: {avgPayTimeOfLatest30day}s
│  └─ 已完成: {completedOrderNumOfLatest30day}
│
├─ 购买广告 ({n}):
│  1. {advNo} | {asset}/{fiat} | {price} | {surplus} 剩余
│     └─ 条款: {remarks or "—"}
│
└─ 出售广告 ({n}):
   1. {advNo} | {asset}/{fiat} | {price} | {surplus} 剩余
      └─ 条款: {remarks or "—"}
```

### 列出支持的货币

**触发:**
- "P2P支持哪些币种？"
- "What fiat currencies are supported?"

**行为:**
- 数字货币: `POST /sapi/v1/c2c/agent/digitalCurrency/list`
- 法定货币: `POST /sapi/v1/c2c/agent/fiatCurrency/list`

---

## 第三阶段 API 概览

### 订单与申诉 (SAPI Agent — 需要认证)
基础 URL: `https://api.binance.com`

| 端点          | 方法 | 认证 | 用途 |
|---------------|------|------|------|
| `/sapi/v1/c2c/agent/orderMatch/getUserOrderDetail` | POST | 是   | 通过订单号获取订单详情 |
| `/sapi/v1/c2c/agent/orderMatch/listOrders` | POST | 是   | 带筛选条件列出订单 |
| `/sapi/v1/c2c/agent/orderMatch/listUserOrderHistory` | GET | 是   | 列出订单历史（分页） |
| `/sapi/v1/c2c/agent/complaint/query-complaints` | POST | 是   | 查询申诉记录 |
| `/sapi/v1/c2c/agent/complaint/submit-evidence` | POST | 是   | 提交申诉证据 (**写入**) |
| `/sapi/v1/c2c/agent/complaint/get-complaint-flows` | POST | 是   | 获取申诉流程时间线 |
| `/sapi/v1/c2c/agent/complaint/cancel-complaint` | POST | 是   | 取消/撤回申诉 (**写入**，不可逆) |
| `/sapi/v1/c2c/agent/complaint/get-complaint-reasons` | POST | 是   | 获取可用申诉原因 |
| `/sapi/v1/c2c/agent/file-upload/get-s3-presigned-url` | GET | 是   | 获取证据上传的 S3 预签名 URL |

### 广告管理 (SAPI Agent — 需要认证)
基础 URL: `https://api.binance.com`

| 端点          | 方法 | 认证 | 用途 |
|---------------|------|------|------|
| `/sapi/v1/c2c/agent/ads/getDetailByNo` | POST | 是   | 通过广告编号获取广告详情 |
| `/sapi/v1/c2c/agent/ads/listWithPagination` | POST | 是   | 列出用户自己的广告（分页） |
| `/sapi/v1/c2c/agent/ads/search` | POST | 是   | 带筛选条件搜索市场广告 |
| `/sapi/v1/c2c/agent/ads/getReferencePrice` | POST | 是   | 获取资产/法币的参考价格 |
| `/sapi/v1/c2c/agent/ads/getAvailableAdsCategory` | GET | 是   | 获取可发布的广告类别 |
| `/sapi/v1/c2c/agent/ads/getPayMethodByUserId` | GET | 是   | 获取用户的支付方式 |
| `/sapi/v1/c2c/agent/ads/listAllTradeMethods` | POST | 是   | 列出所有系统交易方式 |
| `/sapi/v1/c2c/agent/ads/post` | POST | 是   | 发布新广告 (**写入**) |
| `/sapi/v1/c2c/agent/ads/update` | POST | 是   | 更新现有广告 (**写入**) |
| `/sapi/v1/c2c/agent/ads/updateStatus` | POST | 是   | 批量更新广告状态 (**写入**) |

### 商家 (SAPI Agent — 需要认证)
基础 URL: `https://api.binance.com`

| 端点          | 方法 | 认证 | 用途 |
|---------------|------|------|------|
| `/sapi/v1/c2c/agent/merchant/getAdDetails` | GET | 是   | 获取商家资料 + 广告列表 |

### 支持 (SAPI Agent — 需要认证)
基础 URL: `https://api.binance.com`

| 端点          | 方法 | 认证 | 用途 |
|---------------|------|------|------|
| `/sapi/v1/c2c/agent/digitalCurrency/list` | POST | 是   | 列出支持的数字货币 |
| `/sapi/v1/c2c/agent/fiatCurrency/list` | POST | 是   | 列出支持的法币 |

> **完整 API 参考**（包含请求/响应模式）：见 `references/agent-sapi-api.md`

## 第三阶段错误处理（补充）

| 错误          | 原因 | 用户操作 |
|---------------|------|----------|
| 权限被拒绝    | 用户不是已验证商家 | 指引至商家验证页面 |
| FIAT_ASSET_ILLEGAL | BIDR 与非印尼盾法币配对 | 使用印尼盾作为法币 |
| ILLEGAL_PARAMETERS | 缺少或无效字段 | 重新检查必填参数 |
| 广告未找到    | 无效的 advNo | 通过列表验证广告编号 |
| 状态更新部分失败 | 部分广告无法更改状态 | 检查 failList 中的单个错误代码 |

## 第三阶段限制

此技能在第三阶段不（支持）：
- 发起新申诉 / submit-complaint（仅支持现有申诉的证据补充）
- 自动监控申诉状态变化（技能不支持轮询）
- 代表用户下单（引导至广告详情页面）
- 访问聊天消息或发送订单聊天消息
- 修改支付方式配置（仅读）
- 获取 KYC/验证状态详情

对于申诉发起和实时申诉监控，引导用户至官方 P2P 争议中心。
