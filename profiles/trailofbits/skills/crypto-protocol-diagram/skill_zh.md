# 加密协议图

生成 Mermaid `sequenceDiagram`（写入文件）和 ASCII 序列图（内联显示），来源可以是：

- **实现加密协议的源代码**，或
- **规范** — RFC、学术论文、伪代码、非正式散文、ProVerif（`.pv`）或 Tamarin（`.spthy`）模型。

**使用的工具**：Read、Write、Grep、Glob、Bash、WebFetch（用于 URL 规范）。

与 `diagramming-code` 技能（可视化代码结构）不同，此技能提取**协议语义**：谁向谁发送什么、每个步骤发生的加密转换以及协议阶段的存在。

对于调用图、类层次结构或模块依赖关系图，请使用 `diagramming-code` 技能。

## 何时使用

- 用户要求绘制、可视化或提取加密协议
- 输入是实现握手、密钥交换或多方协议的源代码
- 输入是 RFC、学术论文、伪代码或形式模型（ProVerif/Tamarin）
- 用户指定了特定协议（TLS、Noise、Signal、X3DH、FROST）

## 何时不用

- 用户想要调用图、类层次结构或模块依赖关系图 — 使用 `diagramming-code`
- 用户想要正式验证协议 — 使用 `mermaid-to-proverif`（在生成图之后）
- 输入没有加密协议语义（没有参与者、没有消息交换）

## 拒绝的理由

| 拒绝的理由 | 为什么不对 | 需要采取的行动 |
|-----------|-----------|---------------|
| "协议很简单，我可以从记忆中绘制" | 基于记忆的图会遗漏步骤并反转箭头 | 系统地读取源代码或规范 |
| "我将跳过规范路径，因为存在代码" | 代码可能与规范不一致 — 两条路径捕获不同的错误 | 当两者都存在时，首先运行规范工作流，然后注释代码差异 |
| "加密注释是可选的装饰" | 没有加密注释，图只是一个消息流 — 对安全审查无用 | 注释每个加密操作 |
| "中止路径很明显，不需要 alt 块" | 隐式中止处理隐藏了缺失的错误检查 | 使用 `alt` 块显示每个中止/错误路径 |
| "我不用先检查示例" | 示例定义了预期的输出质量标准 | 在处理不熟悉的输入之前，研究相关示例 |
| "ProVerif/Tamarin 模型是代码，不是规范" | 形式模型是规范 — 它描述了预期行为，而不是实现 | 使用规范工作流（S1–S5）用于 `.pv` 和 `.spthy` 文件 |

---

## 工作流程

```
协议图进度：
- [ ] 步骤 0：确定输入类型（代码 / 规范 / 两者）
- [ ] 步骤 1（代码）或 S1–S5（规范）：提取协议结构
- [ ] 步骤 6：生成 sequenceDiagram
- [ ] 步骤 7：验证和交付
```

---

### 步骤 0：确定输入类型

在执行任何其他操作之前，对输入进行分类：

| 信号 | 输入类型 |
|------|---------|
| 源文件扩展名（`.py`，`.rs`，`.go`，`.ts`，`.js`，`.cpp`，`.c`） | **代码** |
| 函数/类定义、导入语句 | **代码** |
| RFC 风格的章节标题（`§`，`Section X.Y`，`MUST`/`SHALL` 关键字） | **规范** |
| `Algorithm`/`Protocol`/`Figure` 标签、数学符号 | **规范** |
| ProVerif 文件（`.pv`）带有 `process`，`let`，`in`/`out` | **规范** |
| Tamarin 文件（`.spthy`）带有 `rule`，`--[...]->` | **规范** |
| 描述协议的纯散文或编号步骤 | **规范** |
| 同时提供源文件和规范文档 | **两者**（用 `⚠️` 注释差异） |

- **仅代码** → 跳到下面的步骤 1
- **仅规范** → 跳到规范工作流（S1–S5）下面
- **两者** → 首先运行规范工作流，然后使用代码读取步骤来验证实现与规范图的一致性，并用 `⚠️` 注释任何差异
- **模糊** → 询问用户："这是一个源代码文件、规范文档还是两者？"

---

### 步骤 1：定位协议入口点

Grep 函数名、类型名和注释，以揭示协议：

```bash
# 查找握手、会话、轮次、阶段入口点
rg -l "handshake|session_init|round[_0-9]|setup|keygen|send_msg|recv_msg" {targetDir}

# 查找使用的加密原语
rg "sign|verify|encrypt|decrypt|dh|ecdh|kdf|hkdf|hmac|hash|commit|reveal|share" \
    {targetDir} --type-add 'src:*.{py,rs,go,ts,js,cpp,c}' -t src -l
```

从最高级别的编排函数开始阅读 — 那个调用握手阶段或主协议循环的函数。

### 步骤 2：识别参与者和角色

从以下内容中提取参与者名称：

- 结构/类名：`Client`，`Server`，`Initiator`，`Responder`，`Prover`，
  `Verifier`，`Dealer`，`Party`，`Coordinator`
- 传递角色状态的函数参数名
- 声明协议角色的注释
- 设置两方或 N 方场景的测试用例

将这些映射到 Mermaid `participant` 声明。使用简短、可读的别名：

```
participant I as Initiator
participant R as Responder
```

### 步骤 3：跟踪消息流

跟踪状态转换和网络发送/接收。查找以下模式：

| 模式 | 含义 |
|------|------|
| `send(msg)` / `recv()` | 直接消息交换 |
| `serialize` + `transmit` | 发送结构化消息 |
| 返回值传递给另一方的函数 | 逻辑消息（进程内） |
| `round1_output` → `round2_input` | 基于轮次的 MPC 步骤 |
| 命名 `ephemeral_key`，`ciphertext`，`mac`，`tag` 的结构字段 | 消息内容 |

对于**进程内**协议实现（其中双方在同一进程中运行），将函数调用边界视为逻辑消息发送，当它们在部署中表示网络边界时。

### 步骤 4：注释加密操作

在每个协议步骤中，识别并标记：

| 操作 | 图表注释 |
|------|----------|
| 密钥生成 | `Note over A: keygen(params) → pk, sk` |
| DH / ECDH | `Note over A,B: DH(sk_A, pk_B)` |
| KDF / HKDF | `Note over A: HKDF(ikm, salt, info)` |
| 签名 | `Note over A: Sign(sk, msg) → σ` |
| 验证 | `Note over B: Verify(pk, msg, σ)` |
| 加密 | `Note over A: Enc(key, plaintext) → ct` |
| 解密 | `Note over B: Dec(key, ct) → plaintext` |
| 提交 | `Note over A: Commit(value, rand) → C` |
| 哈希 | `Note over A: H(data) → digest` |
| 秘密共享 | `Note over D: Share(secret, t, n) → {s_i}` |
| 阈值组合 | `Note over C: Combine({s_i}) → secret` |

保持注释简洁 — 使用数学缩写，而不是代码。

### 步骤 5：识别协议阶段

使用 `rect` 或 `Note` 块将消息步骤分组为命名阶段：

常见的阶段检测：
- **设置 / 密钥生成**：参与者的密钥创建、可信设置、参数生成
- **握手 / 初始化**：临时密钥交换、nonce 交换、版本协商
- **身份验证**：身份证明、证书交换、签名验证
- **密钥派生**：从共享密钥派生会话密钥
- **数据传输 / 主协议**：加密应用数据交换
- **完成 / 拆卸**：会话关闭、MAC 验证、中止处理

检测中止/错误路径，并使用 `alt` 块显示它们。

---

## 规范工作流（S1–S5）

当输入是规范文档而不是源代码时，使用此路径。完成 S1–S5 后，继续上面代码工作流的步骤 6（生成 sequenceDiagram）和步骤 7（验证和交付）。

### 步骤 S1：摄入规范

获取完整的规范文本：

- **提供文件路径** → 使用 Read 工具读取
- **提供 URL** → 使用 WebFetch 获取
- **内联粘贴** → 直接从对话上下文中工作

然后识别规范格式，并阅读
[references/spec-parsing-patterns.md](references/spec-parsing-patterns.md)
以获取特定于格式的提取指导：

| 格式 | 信号 |
|------|------|
| RFC | `RFC XXXX`，`MUST`/`SHALL`/`SHOULD`，ABNF 语法，编号章节的散文 |
| 学术论文 / 伪代码 | `Algorithm X`，`Protocol X`，`Figure X`，编号步骤，数学模式中的 `←`/`→` |
| 非正式散文 | 编号列表，"A 发送 B ..."，纯英文描述 |
| ProVerif（`.pv`） | `process`，`let`，`in(ch, x)`，`out(ch, msg)`，`!`（复制） |
| Tamarin（`.spthy`） | `rule`，`--[ ]->`，`Fr(~x)`，`!Pk(A, pk)`，`In(m)`，`Out(m)` |

如果规范引用了已知命名的协议（TLS、Noise、Signal、X3DH、Double Ratchet、FROST），则还阅读
[references/protocol-patterns.md](references/protocol-patterns.md) 以使用其规范流作为骨架，并填写规范特定细节。

### 步骤 S2：提取参与者和角色

识别所有协议参与者。查找：

- **散文或伪代码中的命名角色**：`Alice`，`Bob`，`Client`，`Server`，
  `Initiator`，`Responder`，`Prover`，`Verifier`，`Dealer`，`Party_i`，
  `Coordinator`，`Signer`
- **章节标题**："参与者"，"角色"，"参与者"，"设置"，"符号"
- **ProVerif**：顶级过程名称（`let ClientProc(...)`，`let ServerProc(...)`)
- **Tamarin**：规则名称和事实参数（例如 `!Pk($A, pk)` — `$A` 是参与者）

将每个角色映射到 Mermaid `participant` 声明。使用简短 ID 和描述性别名（见
[references/mermaid-sequence-syntax.md](references/mermaid-sequence-syntax.md) 中的命名约定）。

### 步骤 S3：提取消息流

跟踪每个参与者向谁发送什么以及按什么顺序发送。按格式提取模式：

**RFC / 非正式散文：**
- 箭头符号：`A → B: msg`，`A -> B`
- 句子模式："A 发送 B ..."，"B 响应 ..."，"A 传输 ..."，
  "在接收到 X 时，B 发送 Y"
- 编号步骤：按顺序提取，从上下文中推断发送者/接收者

**伪代码：**
- 带有显式 `sender`/`receiver` 参数的函数签名
- `send(party, msg)` / `receive(party)` 调用
- 返回值作为输入传递给另一方函数的下一步

**ProVerif（`.pv`）：**
- `out(ch, msg)` — 在通道 `ch` 上发送
- `in(ch, x)` — 在通道 `ch` 上接收，绑定到 `x`
- 在同一通道上匹配 `out`/`in` 对以识别消息流
- `!`（复制）表示处理多个会话的角色

**Tamarin（`.spthy`）：**
- `In(m)` 前提 — 接收消息 `m`
- `Out(m)` 结论 — 发送消息 `m`
- 规则的顺序揭示了协议轮次
- `Fr(~x)` — 由一方生成的随机值
- `--[ Label ]->` 事实 — 安全注释，不是消息

保留顺序和轮次结构。使用 `par` 块在最终图表中分组并发送（广播）。

### 步骤 S4：提取加密操作

对于每个协议步骤，识别执行的操作以及执行它们的参与者：

| 规范符号 | 操作 | 图表注释 |
|----------|------|----------|
| `keygen()`，`Gen(1^λ)` | 密钥生成 | `Note over A: keygen() → pk, sk` |
| `DH(a, B)`，`g^ab` | DH / ECDH | `Note over A,B: DH(sk_A, pk_B)` |
| `KDF(ikm)`，`HKDF(...)` | 密钥派生 | `Note over A: HKDF(ikm, salt, info) → k` |
| `Sign(sk, m)`，`σ ← Sign` | 签名 | `Note over A: Sign(sk, msg) → σ` |
| `Verify(pk, m, σ)` | 验证 | `Note over B: Verify(pk, msg, σ)` |
| `Enc(k, m)`，`{m}_k` | 加密 | `Note over A: Enc(k, plaintext) → ct` |
| `Dec(k, c)` | 解密 | `Note over B: Dec(k, ct) → plaintext` |
| `H(m)`，`hash(m)` | 哈希 | `Note over A: H(data) → digest` |
| `Commit(v, r)`，`com` | 提交 | `Note over A: Commit(value, rand) → C` |
| ProVerif `senc(m, k)` | 对称加密 | `Note over A: Enc(k, m) → ct` |
| ProVerif `pk(sk)` | 公钥派生 | `Note over A: pk = pk(sk)` |
| ProVerif `sign(m, sk)` | 签名 | `Note over A: Sign(sk, m) → σ` |

识别安全条件和中止路径：

- 散文："如果验证失败，中止"，"只有当 ..."，"如果 ... 拒绝"
- 伪代码：`assert`，`require`，`if ... 中止`
- ProVerif：`if m = expected then ... else 0`
- Tamarin：矛盾的事实或限制引理

这些将成为最终图表中的 `alt` 块。

### 步骤 S5：标记规范歧义

在转到步骤 6 之前，检查差距：

- **不明确的消息顺序**：从轮次结构或章节顺序推断；注释为 `⚠️ 从规范结构推断顺序`
- **暗示的参与者**：如果参与者的角色被暗示但未命名，给它一个描述性名称并注明推断
- **遗漏的步骤**：如果规范遗漏了此协议的规范模式要求的步骤，注释：
  `⚠️ 规范遗漏 [步骤] — 规范协议要求它`
- **未指定的加密**：如果规范说 "加密" 而没有指定方案，注释：`⚠️ 未指定加密方案`
- **ProVerif/Tamarin**：私有通道（用 `new c` 或作为私有自由名称声明的 `c`）表示带外通道 — 注释它们

---

<!-- 代码路径（步骤 1–5）和规范路径（步骤 S1–S5）继续到这里 -->

### 步骤 6：生成 sequenceDiagram

生成遵循
[references/mermaid-sequence-syntax.md](references/mermaid-sequence-syntax.md)
中规则的 Mermaid 语法。

**完整性胜于简洁性。** 显示每个不同的消息类型。省略重复的循环迭代（使用 `loop` 块），但永远不要省略一个不同的协议步骤。

**正确性胜于美观性。** 图表必须与代码实际执行的内容匹配。如果代码与已知规范不一致，请注释差异：

```
Note over A,B: ⚠️ 规范在此处要求 MAC — 实现遗漏了它
```

### 步骤 7：验证和交付

交付之前：

- [ ] 每个声明的参与者至少发送或接收一条消息
- [ ] 箭头指向正确的方向（发送者 → 接收者）
- [ ] 加密操作在正确的参与者上（执行它们的参与者）
- [ ] 如果使用协议阶段，没有箭头出现在阶段块之外
- [ ] `alt` 块覆盖了已知的中止/错误路径
- [ ] 图表没有语法错误（检查
      [references/mermaid-sequence-syntax.md](references/mermaid-sequence-syntax.md)
      中的常见陷阱）
- [ ] 如果发现规范差异，用 `⚠️` 注释

**将图表写入文件。** 选择一个从协议名称派生的文件名，例如 `noise-xx-handshake.md` 或 `x3dh-key-agreement.md`。写入具有以下结构的 Markdown 文件：

```markdown
# <协议名称> 序列图

\`\`\`mermaid
sequenceDiagram
    ...
\`\`\`

## 协议摘要

- **参与者**：...
- **轮次复杂度**：...
- **密钥原语**：...
- **身份验证**：...
- **前向保密**：...
- **注意**：[规范偏差或安全观察，或 "无"]
```

写入文件后，在响应中内联打印**ASCII 序列图**，然后是协议摘要。说明输出文件名，以便用户知道在哪里找到 Mermaid 源。

遵循
[references/ascii-sequence-diagram.md](references/ascii-sequence-diagram.md)
中所有绘图约定，包括内联输出格式。

---

## 决策树

```
── 输入是规范文档（不是代码）？
│  └─ 步骤 S1：识别格式，读取 references/spec-parsing-patterns.md
│
── 输入是源代码（不是规范）？
│  └─ 步骤 1：grep for handshake/round/send/recv 入口点
│
── 同时提供规范和代码？
│  └─ 首先运行规范工作流（S1–S5）以构建规范图，
│     然后读取代码并注释与规范图不一致之处用 ⚠️
│
── 规范是已知协议（TLS，Noise，Signal，X3DH，FROST）？
│  └─ 读取 references/protocol-patterns.md 并使用规范流作为骨架
│
── 规范是 ProVerif (.pv) 或 Tamarin (.spthy)？
│  └─ 读取 references/spec-parsing-patterns.md → 形式模型部分
│
── 规范消息顺序是模糊的？
│  └─ 从轮次/章节结构推断，注释为 ⚠️
│
── 无法从规范识别参与者？
│  └─ 检查 "参与者"/"符号" 部分；对于 ProVerif 读取过程名称；
│     对于 Tamarin 读取规则名称和事实参数
│
── 不知道哪些代码文件实现了协议？
│  └─ 步骤 1：grep for handshake/round/send/recv 入口点
│
── 无法从结构名识别参与者？
│  └─ 读取测试文件 — 测试设置揭示角色
│
── 协议在进程内运行（没有网络调用）？
│  └─ 将角色边界处的函数参数传递视为消息
│
── MPC / 阈值协议与 N 方？
│  └─ 读取 references/protocol-patterns.md → MPC 部分
│
── Mermaid 语法错误？
│  └─ 读取 references/mermaid-sequence-syntax.md → 常见陷阱
│
└─ ASCII 绘图约定？
   └─ 读取 references/ascii-sequence-diagram.md
```

---

## 示例

**代码路径** — `examples/simple-handshake/`：

- **`protocol.py`** — 两方认证密钥交换（X25519 DH + Ed25519 签名 + HKDF + ChaCha20-Poly1305）
- **`expected-output.md`** — 技能应为该协议生成的确切 ASCII 图表和 Mermaid 文件

**规范路径（ProVerif）** — `examples/simple-proverif/`：

- **`model.pv`** — ProVerif 中建模的 HMAC 挑战-响应身份验证
- **`expected-output.md`** — 步骤提取演练（参与者、消息流、加密操作）以及技能应生成的确切 ASCII 图表和 Mermaid 文件

在处理不熟悉的输入之前，研究相关示例。
