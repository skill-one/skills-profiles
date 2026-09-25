# Mermaid to ProVerif

读取一个描述密码学协议的 Mermaid `sequenceDiagram`，并生成一个 ProVerif 模型（`.pv` 文件），该模型可以直接传递给 ProVerif 验证器。

**使用的工具：** Read, Write, Grep, Glob。

典型的输入是 `crypto-protocol-diagram` 技能的输出——一个带有密码学操作（`Sign`、`Verify`、`DH`、`HKDF`、`Enc`、`Dec` 等）和消息箭头的 Mermaid `sequenceDiagram`。

## 使用场景

- 用户要求对用 Mermaid sequenceDiagram 描述的密码学协议进行形式化验证
- 用户希望从协议图生成 ProVerif 模型（.pv 文件）
- 用户希望证明机密性、认证性或前向机密性属性
- 输入是 `crypto-protocol-diagram` 技能的输出

## 不应使用场景

- 尚未存在 Mermaid sequenceDiagram——首先使用 `crypto-protocol-diagram` 生成一个
- 用户希望验证非密码学系统（状态机、访问控制）的属性
- 用户希望在现有的 .pv 文件上运行 ProVerif——直接运行 `proverif model.pv`

## 拒绝的理由

| 拒绝的理由 | 为什么不正确 | 必要操作 |
|-----------------|----------------|-----------------|
| "可达性查询只是徒劳" | 如果事件不可达，所有其他查询结果都无意义 | 首先始终添加可达性查询作为合理性检查 |
| "公共信道对所有消息都适用" | 内部状态使用的私有信道可防止虚假攻击 | 使用私有信道进行进程内状态线程 |
| "我会跳过前向机密性测试" | 临时密钥需要验证前向机密性 | 每当图中显示临时密钥时，在主进程中添加 ForwardSecrecyTest 进程 |
| "未使用的声明是无害的" | ProVerif 可能会从孤儿声明中报告虚假结果 | 清理所有未使用的类型、函数和事件 |
| "模型可以编译，所以它是正确的" | 可以编译的模型可能存在死接收、类型不匹配或不可能的守卫，使查询为真 | 在信任任何安全查询之前验证可达性 |
| "我不用先检查示例" | 示例定义了预期的输出质量标准 | 在处理不熟悉的协议之前，研究 `examples/simple-handshake/` |

---

## 工作流程

```
ProVerif 模型进度：
- [ ] 第 1 步：解析参与者和信道
- [ ] 第 2 步：列出密码学操作
- [ ] 第 3 步：声明类型、函数和方程
- [ ] 第 4 步：识别和声明事件
- [ ] 第 5 步：制定安全查询
- [ ] 第 6 步：编写参与者进程
- [ ] 第 7 步：编写主进程并最终化
- [ ] 第 8 步：验证和交付
```

### 第 1 步：解析参与者和信道

从 Mermaid 图中：

1. 提取每个 `participant` 或 `actor` 声明。每个都成为 ProVerif 进程。
2. 计数消息箭头（`->>`、`-->>`、`-x`、`--x`）。每个不同的 `A ->> B: label` 在信道上创建一个通信步骤。
3. 确定信道模型：
   - **公共信道**：对于在安全信道建立之前通过网络发送的任何消息（例如，ClientHello、临时密钥、要由对端解密的密文）。
   - **私有信道**：仅用于单个进程内部的内部状态线程（不用于跨进程消息）。
   - 默认：为所有跨进程消息声明一个共享公共信道 `c`。仅在两个不同的并行会话必须独立时才添加按流信道。

```proverif
free c: channel.
```

### 第 2 步：列出密码学操作

遍历每个 `Note over` 注释和消息标签。列出所有不同的操作，并将每个映射到 ProVerif 声明类别：

| Mermaid 注释 | ProVerif 类别 |
|--------------------|-------------------|
| `keygen() → sk, pk` | 新名称（`new sk`），通过函数派生的公钥 |
| `DH(sk_A, pk_B)` | DH 函数或 `exp` 带有群组 |
| `Sign(sk, msg) → σ` | 签名函数 |
| `Verify(pk, msg, σ)` | 方程式或析构函数 |
| `Enc(key, msg) → ct` | 对称或非对称加密函数 |
| `Dec(key, ct) → msg` | 析构函数（方程式） |
| `HKDF(ikm, info) → k` | PRF/KDF 函数 |
| `HMAC(key, msg) → tag` | MAC 函数 |
| `H(msg) → digest` | 哈希函数 |
| `Commit(v, r) → C` | 承诺函数 |
| `Open(C, v, r)` | 承诺方程式 |

参考 [references/crypto-to-proverif-mapping.md](references/crypto-to-proverif-mapping.md) 获取每个操作的精确 ProVerif 语法。

### 第 3 步：声明类型、函数和方程式

按顺序构建密码学前缀：

1. **类型**——声明用于区分密钥材料的自定义类型：

```proverif
type key.
type pkey.   (* 公钥 *)
type skey.   (* 秘密钥 *)
type nonce.
```

2. **常量**——用于作为域分隔符或标签的固定字符串：

```proverif
const msg1_label: bitstring.
const msg2_label: bitstring.
const info_session_key: bitstring.
```

3. **函数**——构造函数和析构函数。析构函数使用内联 `reduc`，以便在验证或解密失败时进程终止：

```proverif
(* 非对称加密 *)
fun aenc(bitstring, pkey): bitstring.
fun adec(bitstring, skey): bitstring
    reduc forall m: bitstring, k: skey;
        adec(aenc(m, pk(k)), k) = m.
fun pk(skey): pkey.

(* 对称加密 / AEAD *)
fun aead_enc(bitstring, key): bitstring.
fun aead_dec(bitstring, key): bitstring
    reduc forall m: bitstring, k: key;
        aead_dec(aead_enc(m, k), k) = m.

(* 数字签名——verify 在成功时返回消息，失败时终止 *)
fun sign(bitstring, skey): bitstring.
fun verify(bitstring, bitstring, pkey): bitstring
    reduc forall m: bitstring, k: skey;
        verify(sign(m, k), m, pk(k)) = m.

(* KDF——第一个参数是密钥（来自 DH），第二个参数是 bitstring（信息/上下文） *)
fun hkdf(key, bitstring): key.

(* MAC *)
fun mac(bitstring, key): bitstring.

(* 哈希 *)
fun hash(bitstring): bitstring.

(* DH *)
fun dh(skey, pkey): key.
fun dhpk(skey): pkey.

(* 序列化——ProVerif 是强类型的：pkey 不能出现在期望 bitstring 的地方。在需要时使用显式构造函数进行转换。 *)
fun pkey2bs(pkey): bitstring.
fun concat(bitstring, bitstring): bitstring.
```

4. **方程式**——仅在构造函数上的代数恒等式（析构函数已有其重写规则，无需单独的 `equation` 块）：

```proverif
equation forall sk_a: skey, sk_b: skey;
    dh(sk_a, dhpk(sk_b)) = dh(sk_b, dhpk(sk_a)).
```

仅声明图中实际使用的操作。不要添加图中未出现的操作的函数。

### 第 4 步：识别和声明事件

事件标记协议执行中的安全相关时刻。通过识别：

- **开始事件**（`event beginRole(params)`）：在进程发送依赖于长期身份承诺的消息之前立即触发（例如，发送签名消息或 MAC 消息之前）。
- **结束事件**（`event endRole(params)`）：在进程成功验证对端的身份之后立即触发（例如，`Verify(...)` 或 MAC 检查通过后，会话密钥确认后）。
- **机密性标记**：任何在握手后应保持对攻击者未知的关键或随机数。

```proverif
event beginI(pkey, pkey).     (* pk_I, pk_R — 在发送签名消息之前触发 *)
event endI(pkey, pkey, key).  (* pk_I, pk_R, session_key — 在接受后触发 *)
event beginR(pkey, pkey).
event endR(pkey, pkey, key).
```

参数应唯一标识会话：参与者的公钥，加上会话密钥或转录哈希。

### 第 5 步：制定安全查询

为每个安全属性编写一个查询。选择以下之一：

**可达性（始终首先添加——结构合理性检查）：**

验证成功事件是否实际上可达。如果 ProVerif 报告其中任何为 `false`，则模型存在结构错误（死接收、类型不匹配、不可能的守卫），不应信任其他查询结果。一旦模型验证通过，如果它们减慢了主属性检查，则可以注释掉它们：

```proverif
(* 合理性：两个端点都必须可达——验证后注释掉。 *)
(*
query pk_i: pkey, pk_r: pkey, k: key; event(endI(pk_i, pk_r, k)).
query pk_i: pkey, pk_r: pkey, k: key; event(endR(pk_i, pk_r, k)).
*)
```

**机密性**（攻击者无法推导出密钥）：

声明一个私有自由名称，并在会话密钥下对其加密。攻击者知道 `private_I` 等同于会话密钥的破解：

```proverif
free private_I: bitstring [private].

(* 在进程中，在派生 sk_session: *)
out(c, aead_enc(private_I, sk_session));

(* 查询： *)
query attacker(private_I).
```

**弱认证**（如果 B 接受，A 在某个时刻以匹配的参数运行——不防止重放）：

```proverif
query pk_i: pkey, pk_r: pkey, k: key;
    event(endR(pk_i, pk_r, k)) ==> event(beginI(pk_i, pk_r)).
```

**注入式认证**（防止重放——每个 B-接受对应于一个不同的 A-运行）：

```proverif
query pk_i: pkey, pk_r: pkey, k: key;
    inj-event(endR(pk_i, pk_r, k)) ==>
    inj-event(beginI(pk_i, pk_r)).
```

**前向机密性**：在主进程中添加 `ForwardSecrecyTest` 进程，向攻击者泄露长期秘密密钥，然后检查过去的会话密钥是否仍然保密。配对 `free fs_witness: key [private]` 声明和 `query attacker(fs_witness)`。参考
[references/security-properties.md](references/security-properties.md) → Forward Secrecy，以及 `examples/simple-handshake/sample-output.pv` 中的示例。

为每个属性选择最适用的最强查询。参考
[references/security-properties.md](references/security-properties.md) 获取完整的决策树。

### 第 6 步：编写参与者进程

为每个参与者编写一个 `let` 进程。按顺序逐步镜像 Mermaid 图，每个进程结构如下：

**两方协议模板：**

```proverif
let Initiator(sk_I: skey, pk_R: pkey) =
    (* 步骤：生成临时密钥 *)
    new ek_I: skey;
    let epk_I = dhpk(ek_I) in
    (* 步骤：签名并发送 msg1 — pkey2bs 将 pkey 转换为 bitstring *)
    let sig_I = sign(concat(msg1_label, pkey2bs(epk_I)), sk_I) in
    event beginI(pk(sk_I), pk_R);
    out(c, (epk_I, sig_I));
    (* 步骤：接收 msg2 *)
    in(c, (epk_R: pkey, sig_R: bitstring));
    (* 步骤：验证响应者签名——析构函数在失败时终止 *)
    let transcript = concat(pkey2bs(epk_I), pkey2bs(epk_R)) in
    let _ = verify(sig_R, concat(msg2_label, transcript), pk_R) in
    (* 步骤：派生会话密钥 *)
    let dh_val = dh(ek_I, epk_R) in
    let sk_session = hkdf(dh_val, concat(info_session_key, transcript)) in
    event endI(pk(sk_I), pk_R, sk_session);
    (* 机密性证据：在会话密钥下加密 private_I。
     * 声明为：free private_I: bitstring [private]。
     * 查询 attacker(private_I) 检查攻击者无法推导出它。 *)
    out(c, aead_enc(private_I, sk_session)).
```

**编写进程的规则：**

- 图中的每个 `A ->> B: msg_contents` 都变成：
  - `out(c, msg_contents)` 在 A 的进程中
  - `in(c, x)`（带匹配的析构）在 B 的进程中
- 每个 `Note over A: op → result` 都变成一个 `let result = op in` 绑定
- 每个 `Note over A: Verify(...)` 都变成一个 `let _ = verify(...) in` 绑定（析构函数在失败时终止——无需显式 else，建模终止）
- 在图中使用 `alt` 块作为进程中的 `if/then/else`
- 长期密钥是进程参数；临时值使用 `new`

**多方或 MPC 协议**：为每个不同角色编写一个进程。对于阈值协议，编写一个角色进程，并在主进程中复制 `!N` 次。

### 第 7 步：编写主进程并最终化

主进程：

1. 使用 `new` 生成长期密钥
2. 通过 `out(c, pk(sk))` 向攻击者发布公钥
3. 在主进程中并行运行参与者进程（使用 `!` 允许多个会话）
4. 可选地泄露长期密钥以进行前向机密性分析

```proverif
process
    new sk_I: skey; let pk_I = pk(sk_I) in out(c, pk_I);
    new sk_R: skey; let pk_R = pk(sk_R) in out(c, pk_R);
    (
        !Initiator(sk_I, pk_R)
      | !Responder(sk_R, pk_I)
    )
```

将完整文件按以下顺序放置：

```
(* 1. 信道声明（free c: channel. / free ch: channel [private].） *)
(* 2. noselect 指令（如果需要终止） *)
(* 3. 类型声明 *)
(* 4. 常量 *)
(* 5. 函数声明 *)
(* 6. 方程式（仅在构造函数上的代数恒等式） *)
(* 7. 表声明 *)
(* 8. 事件 *)
(* 9. 查询 *)
(* 10. let 进程 *)
(* 11. 主进程 *)
```

### 第 8 步：验证和交付

在编写文件之前：

- [ ] 图中的每个参与者都有一个匹配的 `let` 进程
- [ ] 每个 `out(c, ...)` 在另一侧都有匹配的 `in(c, ...)` 且类型兼容
- [ ] 进程中使用的每个函数都在前缀中声明
- [ ] 每个析构函数都使用内联 `reduc`（不是单独的 `equation` 块）
- [ ] 查询中的每个事件都已声明并在进程中触发
- [ ] 长期公钥在主进程中输出到信道 `c`（攻击者可以看到它们——这就是 Dolev-Yao 模型）
- [ ] 没有未使用的声明（清理任何推测性添加的内容）
- [ ] 如果存在 `table` 声明：每个 `insert T(...)` 都有一个兼容列类型和匹配模式约束（`=key` 对比裸名称）的 `get T(...)`）
- [ ] 如果使用 `noselect`：其元组结构匹配实际在 `c` 上发送的消息形状（例如，对 → `mess(c, (x, y))`）
- [ ] 如果使用 Key Exposure Oracle 模式：`event key_exposed(sk_type)` 已声明，持有秘密的进程末尾出现 `in(c, guess: sk_type); if pk(guess) = pk_new then
      event key_exposed(guess)`，查询为 `query x: sk_type; event(key_exposed(x))`

**将模型写入 `.pv` 文件。** 从协议名称选择文件名，例如 `noise-xx-handshake.pv` 或 `x3dh-key-agreement.pv`。

编写后，打印简要摘要：

```
协议：   <Name>
输出：     <filename>
查询：    <列出每个查询及其测试的属性>
假设：    <列出建模决策和简化>
```

---

## 决策树

```
├─ 未提供 Mermaid 图？
│  └─ 向用户询问："请提供 Mermaid sequenceDiagram，
│     或先运行 crypto-protocol-diagram 技能。"
│
├─ 图使用 DH（不仅是对称密码学）？
│  └─ 使用 dh/dhpk 并带交换性方程
│     参考 references/crypto-to-proverif-mapping.md → DH 部分
│
├─ 图使用非对称签名（Sign/Verify）？
│  └─ 使用 sign/verify 并带内联 reduc（不是 equation）
│     verify 在成功时返回消息；let _ = verify(...) in 在失败时终止
│     区分签名密钥（skey）和验证密钥（pkey）
│
├─ 图有 "alt" 块（中止路径）？
│  └─ 像仅 if/then 一样建模——else 分支中止（进程终止）
│     除非图中显示，否则不要添加 out(c, error_message)
│
├─ 协议有 N > 2 方？
│  └─ 为每个角色编写一个进程，使用 ! 进行复制
│     如果角色仅由索引不同，则将参与者索引作为参数传递
│
├─ 请求前向机密性？
│  └─ 在主进程中添加 ForwardSecrecy 变体，泄露长期 sk 后会话；
│     添加对过去 session_key 的机密性查询
│     参考 references/security-properties.md → Forward Secrecy
│
├─ 类型检查器拒绝模型？
│  └─ ProVerif 是强类型的：检查每个函数参数类型是否匹配声明。
│     bitstring 是通配符；key/pkey/skey/nonce 更严格。
│     需要时使用显式构造函数进行转换。
│
├─ 协议有跨进程状态协调（例如，一个进程必须等待
│  另一个进程记录接受后才能继续）？
│  └─ 使用 ProVerif 表（table/insert/get）
│     参考 references/proverif-syntax.md → Tables
│
├─ 验证在几分钟内未终止？
│  └─ 添加匹配 c 上消息元组结构的 noselect 指令
│     参考 references/proverif-syntax.md → noselect
│
├─ 协议生成一个私类型密钥（类型 sk [private]），
│  它永远不会直接输出，但其机密性应被验证？
│  └─ 使用 Key Exposure Oracle 模式，而不是查询 attacker(sk)
│     参考 references/security-properties.md → Key Exposure Oracle
│
└─ 不确定要验证哪些安全属性？
   └─ 默认集：会话密钥的机密性 + 注入式认证（双向）。如果图中显示临时密钥，则添加前向机密性。
```

---

## 示例

`examples/simple-handshake/` 包含一个已完成的示例：

- **`diagram.md`** — 用于双方认证密钥交换（X25519 DH + Ed25519 签名 + HKDF）的 Mermaid sequenceDiagram
- **`sample-output.pv`** — 技能应生成的精确 ProVerif 模型，包含机密性和注入式认证查询

在处理不熟悉的协议之前，先研究这个示例。

---

## 支持文档

- **[references/crypto-to-proverif-mapping.md](references/crypto-to-proverif-mapping.md)** —
  从 Mermaid 密码学注解到 ProVerif 函数声明、方程式和进程模式的映射表
- **[references/proverif-syntax.md](references/proverif-syntax.md)** —
  ProVerif 语言参考：类型、函数、方程式、进程、事件、查询和常见陷阱
- **[references/security-properties.md](references/security-properties.md)** —
  选择正确查询的决策指南：机密性、认证（弱与注入式）、前向机密性、不可链接性，以及如何建模它们
