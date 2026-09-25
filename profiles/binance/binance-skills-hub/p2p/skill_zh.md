# Binance P2P 交易技巧

帮助用户通过自然语言查询与 **Binance P2P (C2C)** 进行交互。

## 何时使用 / 何时不使用

### 当用户想要时使用：
- 检查加密货币/法币对（例如，USDT/CNY）的 P2P 买入/卖出报价。
- 搜索 P2P 广告并按支付方式、限额、商家质量进行筛选。
- 比较不同支付方式的 价格（例如，支付宝与银行转账）。
- 查看 **自己的 P2P 订单历史记录/摘要**（需要 API 密钥）。
- 查询 **订单详情** 并查看完整订单时间线（需要 API 密钥）。
- 检查 **申诉/投诉状态** 并查看投诉历史记录（需要 API 密钥）。
- **提交现有申诉的证据**（上传文件 + 提交描述）(需要 API 密钥)。
- **查看投诉流程时间线**（流程中的操作、客服备注、证据）(需要 API 密钥)。
- **取消现有申诉**（撤回投诉，不可逆）(需要 API 密钥)。
- **查看订单的可用投诉理由**（需要 API 密钥）。
- **发布、更新或管理 P2P 广告**（需要 API 密钥 + 商家权限）。
- 查看 **商家资料** 和他们的广告列表（需要 API 密钥）。
- 查询 **支持的数字货币和法币**（需要 API 密钥）。

### 当用户询问以下内容时不要使用：
- 现货/转换价格，期货/衍生品，保证金，交易机器人。
- 存款/取款，钱包转账，链上交易。
- 创建/取消订单，释放代币（交易操作）。取消 **申诉**（投诉）是支持的。
- 启动新的申诉（提交投诉被推迟；仅支持补充现有申诉的证据）。
- 在订单对话中发送聊天消息。

### 如果缺少任何关键输入，请询问澄清问题（不要猜测）：
- `fiat`（例如，CNY）
- `asset`（例如，USDT）
- 用户意图：**买入加密货币** 或 **卖出加密货币**
- 首选支付方式
- 目标金额（可选但建议用于广告筛选）

## 核心概念

### `tradeType` 映射（避免歧义）
- 用户想要 **买入加密货币**（支付法币，接收 USDT/BTC）→ `tradeType=BUY`
- 用户想要 **卖出加密货币**（接收法币，支付 USDT/BTC）→ `tradeType=SELL`

始终在用户措辞模糊时反映此映射。

## 功能

### 第一阶段 — 公共市场（无需授权）
- 报价 P2P 价格
- 搜索广告
- 比较支付方式
- 按 限额和商家指标筛选/排序广告

### 第二阶段 — 个人订单（需要 API 密钥）
- 列出 P2P 订单历史记录
- 按 交易类型/时间范围进行筛选
- 提供摘要统计数据

### 第三阶段 — 订单 & 申诉 + 广告发布 & 管理（需要 API 密钥）
- 按订单号查询订单详情
- 列出具有丰富筛选条件的订单（状态、交易类型、资产、日期范围）
- 查看订单时间线（创建 → 付款 → 释放 → 完成）
- 检测申诉状态并显示申诉详情
- 按 筛选条件查询投诉/申诉记录
- 获取市场参考价格以供定价决策
- 上传申诉证据文件（S3 预签名 URL + 提交）
- 查看 投诉流程时间线 / 流程详情
- 取消现有申诉 / 撤回投诉
- 获取订单的可用投诉理由
- 搜索和分析市场广告分布
- 获取当前用户的可用广告类别
- 获取用户配置的支付方式
- 列出所有系统交易方式
- 发布新的广告（带确认）
- 更新现有广告参数（带确认）
- 更新广告状态：在线 / 离线 / 关闭（带确认）
- 查看 商家资料和广告列表
- 列出所有支持的数字货币
- 列出所有支持的法币

## 环境配置

### 基础 URL（生产环境）

| 逻辑名称 | URL |
|---------|-----|
| `SAPI_BASE` | `https://api.binance.com` |
| `MGS_BASE` | `https://www.binance.com` |
| `C2C_WEB` | `https://c2c.binance.com` |

### 代码生成提示（用于代码生成）

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

# 使用示例:
# f"{SAPI_BASE}/sapi/v1/c2c/agent/orderMatch/getUserOrderDetail"
# f"{MGS_BASE}/bapi/c2c/v1/public/c2c/agent/quote-price"
# f"{C2C_WEB}/en/adv?code={advNo}"
# headers = common_headers(os.getenv("BINANCE_API_KEY"))
```

```bash
# Bash 等价物:
SAPI_BASE="https://api.binance.com"
MGS_BASE="https://www.binance.com"
C2C_WEB="https://c2c.binance.com"
```

> **注意**：SAPI 签名使用 HMAC SHA256，无需参数排序。

## 安全与隐私规则

### 凭证
- 必要的环境变量：
    - `BINANCE_API_KEY`（作为头部发送）
    - `BINANCE_SECRET_KEY`（用于签名）

### 永远不要显示完整的密钥
- API 密钥：显示 **前 5 个 + 最后 4 个** 字符：`abc12...z789`
- 密钥：始终遮盖；显示 **仅最后 5 个**：`***...c123`

### 最小权限
- Binance API 权限：**仅启用读取**（第一阶段/第二阶段）。
- 第三阶段广告管理需要额外的写入权限。
- 不要请求/鼓励超出所需权限的撤回或修改权限。

### 存储指南
- 优先使用环境注入（会话/运行时环境变量）而不是写入磁盘。
- 只有在用户明确同意的情况下才写入 `.env`。
- 保存前确保 `.env` 在 `.gitignore` 中。

## ⚠️ 关键：SAPI 签名（与标准 Binance API 不同）

### 参数排序
- **不要对 SAPI 请求进行排序参数**。
- 构建查询字符串时保持原始插入顺序。

示例：
```py
# ✅ 正确的 SAPI：保持插入顺序
params = {"page": 1, "rows": 20, "timestamp": 1710460800000}
query_string = urlencode(params)  # 不排序

# ❌ 错误的（仅标准 Binance API）：排序
query_string = urlencode(sorted(params.items()))
```

### 签名详情
参见：`references/authentication.md`，了解：
- RFC 3986 百分号编码
- HMAC SHA256 签名过程
- 需要的头部（包括 User-Agent）
- SAPI 特定的参数排序

## API 概览

### 公共查询（MGS C2C Agent API — 无需授权）
基础 URL：`https://www.binance.com`

| 端点 | 方法 | 授权 | 使用 |
|------|------|------|-------|
| `/bapi/c2c/v1/public/c2c/agent/quote-price` | GET | 否 | 快速价格报价 |
| `/bapi/c2c/v1/public/c2c/agent/ad-list` | GET | 否 | 搜索广告 |
| `/bapi/c2c/v1/public/c2c/agent/trade-methods` | GET | 否 | 支付方式 |

参数说明：
- `tradeType`: `BUY` 或 `SELL`（视为不区分大小写）
- `limit`: 1–20（默认 10）
- `tradeMethodIdentifiers`: 作为 **纯字符串** 传递（不是 JSON 数组）— 例如. `tradeMethodIdentifiers=BANK` 或 `tradeMethodIdentifiers=WECHAT`. 值 **必须** 使用 `trade-methods` 端点返回的 `identifier` 字段（见工作流下方）。⚠️ 不要使用 JSON 数组语法，如 `["BANK"]` — 它将返回空结果。

### 工作流：按支付方式比较价格

当用户想要比较不同支付方式的 价格（例如，“支付宝与微信”）时，请遵循以下两步流程：

**步骤 1** — 调用 `trade-methods` 获取目标法币的正确标识符：
```
GET /bapi/c2c/v1/public/c2c/agent/trade-methods?fiat=CNY
→ [{"identifier":"ALIPAY",...}, {"identifier":"WECHAT",...}, {"identifier":"BANK",...}]
```

**步骤 2** — 将标识符作为 **纯字符串** 通过 `tradeMethodIdentifiers` 传递到 `ad-list`，每个支付方式一个请求，然后比较：
```
GET /bapi/c2c/v1/public/c2c/agent/ad-list?fiat=CNY&asset=USDT&tradeType=BUY&limit=5&tradeMethodIdentifiers=ALIPAY&tradeMethodIdentifiers=WECHAT
```
比较每个结果集中的最佳价格。

> **重要提示**：不要硬编码标识符值，如 `"Alipay"` 或 `"BANK"`。始终先调用 `trade-methods` 获取给定法币的准确 `identifier` 字符串。

### 个人订单（Binance SAPI — 需要授权）
基础 URL：`https://api.binance.com`

| 端点 | 方法 | 授权 | 使用 |
|------|------|------|-------|
| `/sapi/v1/c2c/orderMatch/listUserOrderHistory` | GET | 是 | 列出订单历史记录 |
| `/sapi/v1/c2c/orderMatch/getUserOrderSummary` | GET | 是 | 用户统计数据 |

授权要求：
- 头部：`X-MBX-APIKEY`
- 查询：`timestamp` + `signature`
- 头部：`User-Agent: binance-wallet/1.0.0 (Skill)`

## 输出格式指南

### 价格报价
- 当可用时显示双方价格（最佳买入 / 最佳卖出）。
- 使用法币符号和 2 位小数格式。

示例：
```
USDT/CNY (P2P)
- 买入 USDT（你买入加密货币）：¥7.20
- 卖出 USDT（你卖出加密货币）：¥7.18
```

### 广告列表
返回 **前 N 项**，使用稳定的模式：
1) adNo（广告编号 / 标识符）
2) 价格（法币）
3) 商家名称
4) 完成率
5) 限额
6) 支付方式（标识符）

避免生成参数化的外部 URL，除非 API 返回它们。

**下单（当用户请求时）**：
- 此技能 **不支持** 自动下单。
- 当用户想要下单时，提供指向特定广告的直接链接，使用 adNo：
  ```
  https://c2c.binance.com/en/adv?code={adNo}
  ```
    - `{adNo}`：广告编号/标识符来自广告列表结果

  示例：`https://c2c.binance.com/en/adv?code=123`
- 这将打开特定广告的详情页面，用户可以直接使用选定的广告下单。

### 个人订单
- 时间格式：`YYYY-MM-DD HH:mm (UTC+0)` — 始终以 UTC 时区显示
- 包括：类型，资产/法币，金额，总额，状态
- 提供一个简短的摘要行（计数 + 总计）当筛选时

**时间字段转换（用于 `listUserOrderHistory` 中的 `createTime`）**：
- `createTime` 字段返回 Unix 时间戳，以 **毫秒** 为单位（13 位）。
- 转换为人类可读格式，在 **UTC+0 时区**：
  ```
  # Python 示例
  from datetime import datetime, timezone
  readable_time = datetime.fromtimestamp(createTime / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M (UTC+0)')
  
  # JavaScript 示例
  const readableTime = new Date(createTime).toISOString().replace('T', ' ').slice(0, 16) + ' (UTC+0)';
  // 或者更明确地：
  const date = new Date(createTime);
  const readableTime = date.getUTCFullYear() + '-' +
    String(date.getUTCMonth() + 1).padStart(2, '0') + '-' +
    String(date.getUTCDate()).padStart(2, '0') + ' ' +
    String(date.getUTCHours()).padStart(2, '0') + ':' +
    String(date.getUTCMinutes()).padStart(2, '0') + ' (UTC+0)';
  ```
- 始终将转换后的时间显示给用户，附带时区信息，而不是原始时间戳。

## 错误处理（面向用户）

- 无效 API 密钥 (-2015)：提示验证 `.env` / API 管理。
- 签名失败 (-1022)：警告关于错误密钥、排序参数或过期时间戳。
- 时间戳无效 (-1021)：建议时间同步 / 重新生成时间戳。
- 速率限制：提示稍后重试。

## 设计限制（按设计）

此技能在第三阶段 **不**：
- 启动新的申诉 / 提交投诉（仅支持补充现有申诉的证据）
- 自动监控申诉状态变化（不支持轮询）
- 代表用户下单（引导到广告详情页面）
- 发送聊天消息或发送订单聊天中的消息
- 修改支付方式配置（仅读）
- 访问 KYC/验证状态详情

对于申诉启动和实时申诉监控，引导用户到官方 P2P 争议中心。
