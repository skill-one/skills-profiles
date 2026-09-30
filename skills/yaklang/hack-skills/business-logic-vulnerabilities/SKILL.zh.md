---
name: business-logic-vulnerabilities
description: 业务逻辑漏洞演练手册。在分析工作流、竞态条件、价格操纵、优惠券滥用、状态机和多步骤授权漏洞时使用。
---

# 技能：业务逻辑漏洞——专家攻击手册

> **AI 加载指令**：业务逻辑漏洞是扫描器无法发现且悬赏高回报的漏洞类型。本技能涵盖竞态条件、价格操控、工作流绕过、优惠券/推荐码滥用、负值和状态机攻击。这些漏洞需要人类推理能力，而非自动化工具。针对具体的利用技术（支付精度/溢出、验证码绕过、密码重置漏洞、用户枚举），加载配套的 [SCENARIOS.md](./SCENARIOS.md)。针对工作流方法本身（建模→状态机→攻击面矩阵→人工判断）加载 [METHODOLOGY.md](./METHODOLOGY.md)。针对模块级检查项加载 [CHECKLIST.md](./CHECKLIST.md)。

### 配套文件

| 文件 | 加载时机 |
|---|---|
| [METHODOLOGY.md](./METHODOLOGY.md) | 需要五阶段工作流、攻击面 5×N 矩阵、人工判断决策树 |
| [CHECKLIST.md](./CHECKLIST.md) | 按模块（登录/注册/支付/IDOR/隐私）逐项检查，并需要每项的验证依据 |
| [SCENARIOS.md](./SCENARIOS.md) | 深入挖掘支付精度/溢出、验证码绕过、密码重置、枚举、前端绕过 |

### 扩展场景

当需要以下场景时，也加载 [SCENARIOS.md](./SCENARIOS.md)：
- 支付精度 & 整数溢出攻击 — 32 位溢出到负数、小数四舍五入利用、负运费
- 支付参数篡改清单 — 价格、折扣、货币、网关、return_url 字段
- 条件竞态实用模式 — 并行应用优惠券、礼品卡双重消费（Burp 组发送）
- 验证码绕过技术 — 丢弃验证请求、移除参数、清除 Cookies 重置计数器、使用 Tesseract OCR
- 任意密码重置 — 可预测的 token (`md5(username)`)、会话替换攻击、注册覆盖
- 用户信息枚举 — 登录错误信息差异、跨端点掩码数据重建、Base64 uid Cookie 操纵
- 前端限制绕过 — 多个优惠券的数组参数 (`couponid[0]`/`couponid[1]`), 移除 `disabled`/`readonly` 属性
- 应用层 DoS 模式 — 正则回溯、WebSocket 滥用

---

## 1. 价格与价值操控

### 负数量/价格
许多应用验证 "数量 > 0" 但不验证货币：
```
添加到购物车，数量：-1
更新数量到：-100
{
  "数量": -5,
  "价格": -99.99     ← 可能被接受
}
```
**影响**：账户获得信用、免费物品、反向银行转账。

### 小数数量 — "0元购" 案例
真实案例：一个电商应用接受 **小数 `数量`** 因为后端信任客户端浮点值：
```json
// 购物车项：
{"id": 114016, "skuQty": 0.02}
// 原始价格 ¥500 → 最终价格 ¥10
// 食品配送应用的变体：
// FoodNum=0.01 → 68元 商品 实付 0.68元
```
为什么有效：服务器乘以 `unit_price * quantity` 而不强制 `数量 ∈ Z+`，所以 2% 的碎片订单支付 2% 的价格但发货完整物品。通过拦截购物车提交→设置 `skuQty` / `FoodNum` 为 `0.02`→完成结账来复现。

### 丢弃必填字段 — 免费套餐强制
体育活动注册：当涉及付费奖品时服务器返回 `"payType": "paid"`；如果客户端请求**编辑为完全省略 `prizeIdList`**，服务器回退到 `"payType": "free"` 并创建一个本应付费的成功注册。
```json
// 原始
{"prizeIdList": ["6264e6948fe587000113e2d9"], ...}
// 修改 — 完全移除数组
{"prizeIdList": [], ...}
// 服务器响应：
{"ok": true, "payType": "free"}
```
这是一个参数存在性信任漏洞 — 后端将 "字段缺失" 视为 "无需强制付费项"，修复方法是服务器端验证该字段内容。

### 整数溢出
```
数量：2147483648   ← INT_MAX + 1 在 32 位中溢出到负数
价格：9999999999999   ← 超出浮点精度 → 四舍五入为 0
```
真实案例：设置 `amount=999999999` 触发溢出路径，系统将 `0` 存为最终应付金额。**触发溢出测试前务必协调** — 它们有时会崩溃支付服务。

### 四舍五入操控
```
物品价格：$0.001
订单 1000 件物品 → 每件四舍五入向下 → 总计 = $0.00
```
真实的 "半价充值" 漏洞：输入 `¥0.019` 进行充值。支付网关仅收取 `¥0.01`（四舍五入到分），但钱包充值 `¥0.02`（四舍五入向上）。每个周期的净收益是 `¥0.01`，重复以增加免费余额。

### 货币汇率滞后
```
1. 使用货币 A 以汇率 X 存款
2. 汇率变化
3. 使用货币 A 以新汇率提现 → 从汇率差异中获利
```

### 通过促销叠加免费升级
测试组合折扣码、推荐积分、欢迎奖励：
```
应用促销：FREE50  → 50% 折扣
应用促销：REFER10 → 额外 10%
应用忠诚度积分 → 额外折扣
总计：-$5（免费 + 信用）
```

---

## 2. 竞态条件

**概念**：两个操作在第一个操作完成其检查-更新周期前同时运行。

### 双重消费/双重兑换
```bash
# 同时发送相同请求（间隔约毫秒）：
# 使用 Burp Repeater "发送到组" 或竞态条件工具：

POST /api/use-coupon    ← 发送 20 个并行请求
POST /api/redeem-gift   ← 相同的优惠券代码，并行
POST /api/withdraw-funds ← 相同的余额，并行

# 如果检查和更新非原子性：
# 线程 1：检查(balance >= 100) → TRUE
# 线程 2：检查(balance >= 100) → TRUE（线程 1 扣除前）
# 线程 1：余额 -= 100
# 线程 2：余额 -= 100 → 双重消费
```

### 使用 Burp Suite 进行竞态条件测试
```
1. 捕获请求
2. 发送到 Repeater → 复制 20+ 次
3. "并行发送组"（Burp 2023+）
4. 检查：是否有重复成功？
```

### Turbo Intruder — 绕过按号码的短信速率限制
真实案例：当正常请求返回 `"该号码短时间内申请发送短信次数过多，拒绝发送"` 时，通过 Turbo Intruder 以高并发发送**相同载荷**击败简单计数器：
```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=30,
                           requestsPerConnection=10,
                           pipeline=False)
    for i in range(30):
        engine.queue(target.req, target.baseInput, gate='race1')
    engine.openGate('race1')
```
结果：按手机限制器竞态，许多请求漏过，生成多个不同验证码（真实的 SMS 轰炸案例）。根本原因：计数器增量与读取非原子性。

### 多设备并发 VIP 订阅
真实案例：一个服务提供 **仅限首月折扣**。在任意支付完成前在多个设备（A、B、C）上打开支付表单，然后依次完成。服务器仅在**第一个**请求中检查 "是新用户吗？"，所以后续请求都继承折扣，VIP 时长叠加。
```
正常：下单 → 支付 → 充值会员 → 第二次下单 → 服务端校验 "已是新人" → 拒绝
绕过：设备A: 进入支付页（锁定优惠资格）
        设备B: 进入支付页（并发锁定）
        设备A: 完成支付 → VIP +1月（优惠价）
        设备B: 完成支付 → VIP +1月（仍按优惠价）
```
同样的技巧适用于 "补差价升级会员" — 并行充值重复时长信用。

### 账户注册竞态
```
同时使用相同邮箱注册 → 创建两个账户 → 数据隔离破坏
密码重置 token 竞态 → 重复使用相同 token
邮箱验证竞态 → 验证多个邮箱地址
```

### 通过竞态绕过限制
```
"一次领取" 折扣、免费礼品、"首单" 奖励：
→ 发送 10 个并行 POST /claim 请求
→ 竞态窗口：所有请求在写入前通过 "已领取?" 检查
```

---

## 3. 工作流/步骤绕过

### 支付流程绕过
```
正常流程：
  1. 添加到购物车
  2. 输入运费信息
  3. 输入支付（卡/钱包）
  4. 点击确认 → 支付扣款
  5. 订单确认

攻击：直接跳到第 5 步
POST /api/orders/confirm {"cart_id": "1234", "payment_status": "paid"}
→ 服务器信任客户端发送的 payment_status?
```

### 多步骤验证绕过
```
密码重置流程：
  1. 输入邮箱
  2. 接收 token
  3. 输入 token
  4. 设置新密码（需要步骤 3 的有效 token）

攻击：尝试在完成步骤 3 前跳到步骤 4：
POST /reset/password {"email": "victim@x.com", "token": "invalid", "new_pass": "hacked"}
→ 服务器检查是否正确验证 token？

或者：尝试使用旧/过期的 token → 仍被接受？
```

### 2FA 绕过
```
正常流程：
  1. 输入用户名 + 密码 → 成功
  2. 输入 2FA 代码 → 登录

攻击：步骤 1 成功后，直接访问 /dashboard
→ 会话是否在 2FA 完成前创建？
→ /dashboard 是否需要 2FA 完成检查，还是只需要 "已认证" 标志？
```

### 过滤路径截断绕过 — `..//` 和 `;`

真实案例来自 Java Web 类审计：一个手动实现的 Servlet `Filter` 通过检查 URI 字符串来检查登录。两个可靠的绕过方法：

```
路径遍历截断（../）:
  受保护：http://target/FilterDemo/index.jsp        → 302 到 /login
  绕过：http://target/FilterDemo/../../index.jsp  → 200（filter 看到 "../../", URL 解析器折叠）

分号截断 (;）:
  受保护：http://target/admin/doLogin.action        → 302 到 /login
  绕过：http://target/;/admin/doLogin.action      → 200
                              ^
                              Servlet 容器将分号后的部分视为 "路径参数",
                              使用 request.getRequestURI() 的 filter 看到 "/;/admin/doLogin.action",
                              不匹配其保护前缀 "/admin/"，允许请求通过，
                              但调度器随后路由到真实的 /admin/doLogin.action 处理器。
```

**修复**：永远不要使用 `request.getRequestURI()` 进行安全检查；使用 `request.getServletPath()`，它是规范化的 servlet 映射路径：
```java
// 易受攻击
String uri = request.getRequestURI();   // /;/admin/doLogin.action
// 安全
String path = request.getServletPath(); // /admin/doLogin.action
```

审计 Java 代码时，搜索 `request.getRequestURI()` 配合 `Filter`/`startsWith`/`indexOf("/admin")` 模式 — 这些是立即的红色警告。

### 真实姓名验证重放到重置

故意失败真实姓名认证以**重新打开**编辑流程的欺诈路径：
```
1. 提交真实姓名认证，故意使用错误的 cardNumber
   → 服务器返回 "code:200, msg:success, ok:true" 但流程显示 "驳回 / 等待审核"
2. 因为服务器将状态标记为 "拒绝" 但不锁定用户，UI 允许账户回到 "编辑身份" 状态
3. 现在重新提交另一个（可能被盗的）身份
   → 真实姓名绑定无限重复，破坏防沉迷锁，并允许账户转售
```
防御：拒绝的真实姓名提交必须锁定账户 / 要求人工审核，而不是循环回编辑器。

### 无支付运费
```
  1. 添加物品到购物车
  2. 输入运费地址
  3. 选择支付方式（信用卡）
  4. 应用促销码（100% 折扣或礼品卡）  
  5. 最终金额：$0
  6. 订单提交

攻击：应用 100% 折扣码 → 没有实际支付处理 → 物品发货
```

---

## 4. 优惠券和推荐码滥用

### 优惠券叠加
```
测试：能否应用多个优惠券代码？
测试："SAVE20" + 促销是否叠加到 >100%？
测试：应用优惠券，移除物品，保留折扣，添加不同物品
```

### 推荐循环
```
1. 创建账户_A
2. 使用账户_A 的推荐码注册账户_B → 两者都获得积分
3. 使用账户_B 的推荐码创建账户_C
4. 无限循环，使用一次性邮箱
→ 无限积分生成
```

### 优惠券 = 固定金额折扣（可变价格商品）
```
优惠券：任何订单 -$5 折扣
购买价值 $3 的物品，使用 -$5 优惠券 → 净 -$2（信用余额）
```

---

## 5. 账户/权限逻辑漏洞

### 邮箱验证绕过
```
1. 使用邮箱 A 注册（合法，已验证）
2. 更改邮箱到 B（攻击者邮箱，未验证）
3. 使用账户作为已验证 — 服务器强制重新验证吗？

或者：更改邮箱到受害者邮箱 → 无需验证 → 账户声称
```

### 密码重置 token 绑定
```
1. 为您的账户请求密码重置 → 获取 token
2. 更改您的邮箱地址（账户设置）
3. 重用旧的密码重置 token → 它对旧邮箱是否仍然有效？

或者：为 victim@target.com 请求重置
    Token 发送到受害者，检查：URL 是否暴露可预测的 token 模式？
```

### OAuth 账户链接滥用
```
1. 拥有受害者的邮箱（但不是他们的密码）
2. 使用受害者的邮箱注册 → 获得具有相同邮箱的账户
3. 将 OAuth（Google/GitHub）链接到您的账户
4. 受害者使用 Google 登录 → 服务器找到邮箱匹配 → 合并到您的账户
```

### Cookie 替换 — 横向/纵向权限提升

审计视频中的典型 IDOR 演示：
```
1. 以超级管理员登录 → 捕获请求，复制 Cookie (JSESSIONID/Token)
2. 退出，以普通用户登录 → 捕获另一个请求到相同端点
3. 重放普通用户请求，但交换 Cookie 值与管理员 token
4. 如果响应返回管理员数据 → 垂直提升
   如果返回其他用户数据 → 横向提升
```
常见的伴随漏洞：`/oa/emp/list` 在无 Cookie 时返回 **HTTP 302 到 /login**，但在任何普通用户 Cookie 发送时返回 **200 和完整数据** — 意味着唯一的检查是 "已登录?"，而不是 "有权限访问此端点"。

### 数据库不一致残留的权限残留

第二审计课程的微妙案例：管理界面显示角色 X 已撤销权限 `user:list`，但查询 SQL 数据：
```sql
SELECT * FROM sys_menu WHERE role_id = 2;
-- 两条相同 menu_id "user:list" 的行
```

UI 的 "移除权限" 只删除了一条行；重复的行仍然使 API 可访问。验证方法：
```sql
SELECT menu_id, COUNT(*) FROM sys_menu GROUP BY menu_id, role_id HAVING COUNT(*) > 1;
```

教训：当 UI 表示权限撤销但 API 仍然工作 → 检查底层 RBAC 表是否存在重复/孤立的授权。

### 弱随机密码重置 token

PHP / 遗留 Windows 堆栈使用 `rand()`，其 `RAND_MAX = 32768`。如果重置链接使用
`/resetpassword.php?id=md5(rand())`，整个密钥空间是可预计算的：
```php
$a = 0;
for ($a = 0; $a <= 32768; $a++) {
    $b = md5($a);
    echo $b . "\r\n";
}
```
迭代生成的字典，对 `/resetpassword.php?id=<hash>` — 当一个返回有效重置页面时，您可以更改受害者的密码。审计任何调用 `rand()`、`mt_rand()`（未播种）、`Random()`（默认播种）等的 token 生成。

---

## 6. API 业务逻辑漏洞

### 对象状态操控
```
order.status = "pending"
→ PUT /api/orders/1234 {"status": "refunded"}   ← 自触发退款
→ PUT /api/orders/1234 {"status": "shipped"}    ← 无发货标记为已发货
```

### 事务重用
```
1. 启动支付 → 获取 transaction_id
2. 完成购买
3. 重用相同的 transaction_id 进行第二次购买:
   POST /api/checkout {"transaction_id": "USED_TX", "cart": "new_cart"}
```

### 限制计数操控
```
每日转账限制 = $1000
→ 转账 $999，取消，转账 $999（取消时限制未更新）
→ 并行转账（限制检查上的竞态条件）
→ 不同支付类型不共享限制计数器
```

### Java Web "无 Filter，无 Spring Security" 反模式

审计友好的提示：一个Spring Boot项目，**不**包含`spring-boot-starter-security`，并且没有`Filter`类。这意味着除非开发者手动检查每个方法中的会话，否则每个控制器都对`guest`完全开放。复现：
```bash
# 在源代码树中
find . -name "*.java" -exec grep -l "Filter" {} \;     # 可能是空的
find . -name "*.java" -exec grep -l "@PreAuthorize\|@Secured" {} \;
```
如果两者都为空，几乎每个API都可能未授权。从审计演示：
```java
public Result score(@RequestParam("userId") Integer userId) {
    Score score = scoreService.selectScoreByUserId(userId);
    return Result.success(score);
}
```
没有检查`userId`是否与会话中的登录用户匹配 → 水平IDOR。更糟的是：同一个端点**无需任何Cookie**就能工作，因为没有强制全局身份验证。

### Spring Security `antMatchers` 覆盖缺口

审计视频还展示了一个部分受保护的Spring Security配置，例如：
```java
.antMatchers("/system/user/info").authenticated()
.antMatchers("/system/menu/**").hasRole("admin")
```
一个常见的错误是规则过于狭窄 — 例如`/system/user/info`受保护，但`/system/user/list`不受保护，或者`/system/menu/**`仅限管理员，但`/system/dept/treeData`是开放的。对照控制器注解（`@PreAuthorize("@ss.hasPermi('system:user:list')")`）与SecurityConfig — 每个带注解的端点都必须映射到SecurityConfig规则。重构后容易出现不匹配。

---

## 7. 订阅 / 等级混淆

```
免费套餐：无法访问功能X
付费套餐：可以访问功能X

攻击：
- 注册付费试用 → 启用功能X → 降级到免费
  → 降级后功能X会被禁用吗？ 
  → 能否继续使用功能X？

或者：
- 从JS包中检查高级端点列表
- 使用免费账户令牌直接调用高级端点
→ 服务器检查订阅用于UI，但API不检查？
```

### 直接媒体URL泄露 — VIP资源绕过

健身/学习应用的实际情况：当客户端请求课程详情时，JSON响应嵌入原始媒体URL：
```http
GET /gerudo/v2/liveCourse/625020ce8f002700010554c1/detail HTTP/1.1
{
  "previewPullUrl": "http://app-live.../live/app-live_625020ce8f002700010554c2_Preview.flv"
  ...
}
```
搜索**所有**详情 / 预览 / 播放响应，查找关键词：
```
.flv  .m3u8  .mp4  .mp3  videoUrl  downloadUrl  streamUrl  previewPullUrl
```
对于每个命中，匿名重放URL（curl、VLC、flv.js demo at `https://bilibili.github.io/flv.js/demo/`）。如果URL无需会话即可播放，则你已绕过VIP门槛。防御：使用与用户/IP/Referer绑定的签名、短TTL URL，而不是原始资源路径。

### 资源ID替换 — 免费 → 付费课程

伴生错误：免费课程详情返回`{"id": "60caa21e853f5c1651b27c1b", ...}`。将URL中的ID替换为已知的付费课程ID。如果响应结构保持相同并包含可播放URL → 付费内容上的IDOR。防御：验证每个详情调用中的**所有者关系**，而不仅仅是“是否登录”。

---

## 8. 文件上传业务逻辑

对于纯逻辑缺陷之外的完整上传攻击工作流，还需加载：

- [上传不安全文件](../upload-insecure-files/SKILL.md)

```
上传大小限制：10MB
→ 上传10MB → 客户端压缩 → 服务器解压 → 炸弹？
(Zip炸弹：1KB zip → 1GB文件 = 拒绝服务)

上传类型限制：
→ 上传.csv用于“数据导入” → 注入公式：=SYSTEM("calc")
  (Excel宏环境中的CSV注入)
→ 上传头像 → 服务器转换 → 攻击转换器（ImageMagick、FFmpeg CVEs）

存储路径预测：
→ /uploads/USER_ID/filename
→ 你能否通过知道他们的ID + 文件名覆盖其他用户文件？
```

---

## 9. 测试方法

```
对于每个业务流程：
1. 映射预期流程（快乐路径）
2. 问：“如果我跳过步骤N？”
3. 问：“如果我发送负值/零/MAX值？”
4. 问：“如果我重复此步骤两次？”（幂等性）
5. 问：“如果我先做A再做B，而不是先做B再做A？”
6. 问：“如果两个用户同时这样做？”
7. 问：“我能修改‘受信任’状态字段吗？”
8. 从财务/资源影响角度思考 → 最高悬赏
```

对于正式的5阶段工作流 — 业务建模 → 状态机 → 攻击面矩阵 → 检查表驱动测试 → 人工判断 — 加载**[METHODOLOGY.md](./METHODOLOGY.md)**。它包含一个单页决策树（`Q1 ~ Q7`）用于“我盯着一个请求，不知道先尝试什么”。

---

## 10. 高影响检查表

对于完整按模块列表（登录 / 注册 / 密码恢复 / 支付 / 优惠券 / 订单 / IDOR / 隐私 / VIP / URL重定向 / Cookie & 令牌 / 竞态 / 评论）包含`为什么`和`验证`列 — 加载**[CHECKLIST.md](./CHECKLIST.md)**。

下面压缩的顶级影响项目是“如果你只有30分钟，先打这些”的集合：

### 电子商务 / 支付
```
□ 负数数量 / 小数数量（skuQty=0.02, FoodNum=0.01）在购物车
□ 删除必需字段（delete prizeIdList）以强制免费套餐
□ amount=999999999整数溢出 → 最终为0
□ 通过数组参数应用多个冲突优惠券
□ 竞态条件：双倍消费礼品卡 / 相同优惠券
□ 直接跳过支付步骤到订单确认  
□ 服务器信任客户端状态字段（payment_status=paid, success:true）
□ 无退货退款（通过状态变更触发已交付商品的退款）
□ 多设备并发VIP订阅 / 补差价升级
□ 货币四舍五入利用（¥0.019收费 → ¥0.02钱包信用）
```

### 身份验证 / 账户
```
□ 2FA绕过：密码步骤后直接URL访问
□ 过滤器绕过：..../路径遍历截断，;path-parameter截断
□ 密码重置令牌在邮箱更改后重复使用
□ 弱随机重置令牌：Windows PHP上的md5(rand())，可预测种子
□ 邮箱验证绕过（验证后更改邮箱）
□ OAuth账户接管：通过邮箱匹配
□ 使用现有未验证邮箱注册
□ Cookie替换（管理员 → 用户 / 用户 → 另一个用户）
□ 实名验证“故意填错”重放以重置
```

### 订阅 / 限制 / 资源
```
□ 降级后访问高级功能
□ 通过并行请求超出速率/使用限制（Turbo Intruder）
□ 推荐循环以无限获取积分
□ 免费试用≠有时间限制（试用后无执行）
□ 无订阅检查直接API调用高级端点
□ 免费课程ID交换为付费课程ID（资源上的IDOR）
□ JSON中直接媒体URL暴露（.flv / .m3u8 / .mp4在响应中）
□ 服务器端RBAC残留（sys_menu重复行）
□ Java Web无Filter / Spring Security antMatchers缺口
```

---

## 11. 合并检查表（2小时完整扫描）

第10部分列表是“30分钟快速获利”。此列表是下一层：
当你有几个小时，想对所有九个业务表面进行防御级扫描时。它按表面组织，然后在表面内按攻击机制组织，这样你可以垂直阅读一列以了解“此端点可能存在哪些类型的错误”，以及水平阅读一行以了解“此攻击在何处适用”。

对于包含重放步骤和工具的完整`项目 / 为什么 / 验证`三元组，加载**[CHECKLIST.md](./CHECKLIST.md)**。本节仅保留项目行以快速扫描。

### 11.1 登录 / 身份验证
```
□ 通过响应差异枚举用户名（msg / 状态码 / 时间）
□ 通过SMS发送响应枚举用户名（已发送 vs 未注册）
□ 无锁定暴力破解（失败登录无速率限制）
□ 默认 / 弱密码（后端和基础设施上的admin/admin, root/123456）
□ 2FA绕过：密码步骤后直接URL / 重放2FA令牌
□ 客户端信任登录标志（状态=success, is_login=true在响应体中）
□ 第三方 / SSO回调IDOR（修改uid以接管）
□ 活体绕过（重放静态照片 / 预录视频）
□ 登录/注册中的开放重定向（return_url, redirect, callback参数）
□ 硬件密钥签名重放/伪造（USB-Key, PKI证书）
```

### 注册
```
□ 通过“已存在”响应枚举用户名 / 电话 / 邮箱
□ 仅客户端强制密码强度（服务器端设置123456）
□ 跳过多步骤注册（直接POST最终步骤，遗漏邮箱验证）
□ 验证码未强制（空 / 随机 / 固定值通过）
□ SMS / 邮箱码重放（相同代码使用两次或跨用户）
□ 登录后重新注册相同用户名，继承旧数据 / 权限
□ 通过N个相似虚拟账户绕过反欺诈（相同设备，不同邮箱）
□ 大量注册重放保护缺失（提交步骤无nonce）
```

### 密码恢复 / 重置
```
□ 重置目标篡改（提交步骤中的uid / email / phone）
□ 重置令牌可预测（基于时间戳，弱哈希，短随机）
□ 跨用户令牌重用（A的reset_token，更改B的密码）
□ 登录时更改密码端点缺少旧密码检查
□ 直接访问最终重置端点，跳过代码验证步骤
□ 重置链接 / 答案 / 令牌泄露在HTML或JS源中
□ 重置令牌无过期 / 使用后未失效
□ 重置代码仅base64“混淆”在响应中
□ 多步骤流程中身份不一致（步骤2的reset_token可重复用于步骤4）
□ 邮箱/电话重新绑定后未撤销旧会话
```

### 会话 / 令牌
```
□ 会话固定：预登录会话ID在登录后仍然有效
□ 令牌未绑定到用户/IP/设备（窃取Cookie → 任何地方使用）
□ 伪造令牌：弱算法md5(username + timestamp)，无服务器盐
□ 过期令牌在登出/过期后仍被接受（无黑名单）
□ Cookie篡改（uid / role / is_admin在服务器端受信任）
□ 状态机重放（重放“抢红包”→ 重新抢）
□ 缺少一次性令牌的反重放（CSRF令牌，OTP，nonce）
□ 敏感凭证（令牌，答案，密钥）硬编码在前端JS
□ 从公共会话ID创建特权会话，无需重新身份验证
□ 令牌跨环境工作（不同IP，不同UA，无验证）
```

### 支付 / 订单
```
□ 金额篡改：amount = 0.01 / 0 / 负数 / 0.001
□ 数量篡改：quantity = -1 / 0.01 / 1.5 / 999999999
□ 整数溢出：quantity * price回绕为0或负数
□ 浮点精度利用（多小数，累积舍入）
□ 货币代码交换（CNY → JPY/RUB在相同数值）
□ 优惠券/折扣字段伪造（coupon_id, discount=, free_shipping=true）
□ 项目ID交换：在结账时将product_id替换为更便宜的SKU
□ 签名/签名字段绕过（删除sign参数，使用陈旧签名）
□ 支付回调伪造（状态=paid发布到内部回调）
□ 重放支付请求 → 多次发货 / 多次信用
□ 竞态/并发：超售，双倍消费礼品卡，双倍兑换优惠券
□ 退款而不丢失商品/虚拟权利
□ VIP持续时间篡改（days=999，months=120，period=-1）
□ 接收账户重定向（merchant_id / receiver_account在提现时交换）
□ 负数运费/费用字段减少总额（shipping_fee = -500）
□ 并发充值然后退款耗尽（退款 > 充值在竞态窗口）
□ 定价规则过渡窗口（T时价格变更，T-ε时使用旧规则）
□ 货币四舍五入微观套利（收费0.019 → 钱包信用0.02）
□ 多渠道不一致（在线 vs 现金到货 vs 余额支付）
```

### IDOR / 授权
```
□ 水平IDOR：uid / order_id / 资源id替换为受害者的
□ 垂直IDOR：角色 / 类型 / 等级字段在请求中设置为管理员
□ 隐藏字段篡改（data-user-id在HTML / JS状态）
□ 邮箱/电话重新绑定而不验证旧绑定
□ UID与会话令牌一致性缺失（令牌属于A，发送uid为B）
□ 可预测/顺序资源ID（礼品ID，分享链接ID）
□ 订单/优惠券/分享/行程详情端点上的资源枚举
□ 多条目不一致：Web阻止，移动API不阻止
□ 状态机非法转换（未付款/发货前就领取奖励 / 订单支付前）
□ 隐藏/未文档化的管理员端点无需管理员身份即可访问
□ 跨角色函数调用（用户调用商家API，骑手API等）
□ 通过并发操作获得权限（请求角色提升竞态条件）
```

### CAPTCHA / 验证码
```
□ 代码以明文返回在HTTP响应（正文 / 头 / JS变量）
□ 接收器篡改：更改phone / email参数为攻击者控制
□ 空值/固定代码接受（000000，空白，"test")
□ 完全删除代码字段→请求仍然成功
□ 跨账户重用（A的有效代码在B的流程中接受）
□ 一次性执行缺失（相同代码可重复使用直到过期）
□ 4-6位代码暴力破解（无尝试限制，无锁定）
□ SMS / 邮件轰炸（无IP / 每电话速率限制，无图形CAPTCHA）
□ 前端唯一的“发送成功”状态（服务器说失败，FE说成功）
□ 代码与会话未绑定（为A生成代码，在B的会话中使用）
```

### 文件上传
```
□ 内容类型绕过（Content-Type: image/jpeg, 正文是PHP）
□ 扩展技巧：双扩展（.php.jpg），大小写混合（.Php），空字节，;path
□ 文件名路径遍历（filename=../../webshell.php）
□ 文件内容多语言（嵌入PHP / shell的图像）
□ Office XML重新打包（解压docx→注入XML→重新打包→上传）
□ XXE通过.xml / .dtd上传端点
□ 后端仅上传（管理员登录→上传→执行）
□ 上传竞态：上传+并行访问在AV扫描/清理前
□ ZIP炸弹（1KB → 1GB在服务器，解压DoS）
□ CSV公式注入（=SYSTEM("calc"), =cmd|'/c calc'!A1）
□ 存储路径可预测/跨用户可覆盖（/uploads/UID/file）
□ 图像转换器/解析器CVE（ImageMagick，FFmpeg，pillow）
```

### CSRF / SSRF / XXE
```
□ XXE文件读取（<!ENTITY x SYSTEM "file:///etc/passwd">）
□ XXE盲测通过OOB（参数实体→DNSLog / Burp Collaborator）
□ SSRF通过图像导入 / webhook / 预览URL（file://, http://127.0.0.1）
□ SSRF通过FTP / gopher / jar / php-wrapper / dict协议
□ XML解析器危险包装启用（php://expect, expect://）
□ 异步检测用于盲注入（DNSLog确认服务器被击中）
□ 状态变更端点的CSRF（无令牌，无SameSite，无origin检查）
□ 支付/提现CSRF通过自动提交的隐藏表单
□ 登录CSRF（强制受害者登录攻击者账户）
□ JSONP / JSONP回调利用作为CSRF读取原始操作
```

### 如何使用本节

1. 打印或截图目标表面的相关1-2个子部分。
2. 对于每个`□`标记：不适用 / 无漏洞 / 漏洞 / 需要重新检查。
3. 标记确凿的漏洞（或证明不存在漏洞）的确切端点+参数+负载，以便报告可复现。
4. 当项目触发意外情况时，与`METHODOLOGY.md` Q1~Q7决策树交叉参考 — 树形结构告诉你哪些相邻项目也可能易受攻击。
5. 对于每个项目的深度负载 / curl就绪命令 / Burp截图，加载`CHECKLIST.md`（完整三元组）和`SCENARIOS.md`（真实案例）。
