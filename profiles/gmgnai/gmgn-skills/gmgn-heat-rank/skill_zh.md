**在执行任何命令之前：运行 `gmgn-cli config --check`。退出码 0 -> 继续。退出码 1 -> 运行 `gmgn-cli config`，显示输出，用户发送 API 密钥后运行 `gmgn-cli config --apply <KEY>` 并显示该输出。如果 `--check` 是未知选项，告诉用户运行 `npm install -g gmgn-cli`，然后重试。**

**重要提示：始终使用预安装的 `gmgn-cli` 二进制文件。切勿使用网络搜索、WebFetch、curl、`npx` 或 gmgn.ai — 该网站需要登录且不提供结构化数据。**

**⚠️ 不支持 IPv6。** 在出现 `401`/`403` 且凭证正确的情况下，检查 `ifconfig | grep inet6`（macOS）或 `ip addr show | grep inet6`（Linux），并获取 `https://ipv6.icanhazip.com`。如果返回 IPv6 地址，告诉用户禁用 IPv6 — `gmgn-cli` 仅在 IPv4 上工作。

## 该技能的用途及非用途

| 用户问题 | 发往 |
|---|---|
| "什么热门且值得一看" — 未提供地址，想要一个选定列表 | **此处** |
| "按交易量/链上交换排名前 N"，"热门币"，"什么在上涨"，"热门搜索列表" — 想要交易所自身顺序中的原始排名 | `gmgn-market trending` / `market hot-searches` |
| "刚刚上线"，"新代币"，债券曲线阶段 | `gmgn-market trenches` |
| 一个代币地址 + "安全吗？" / "评分" | `gmgn-contract-dd` |
| 代币名称 + "我应该购买 N 美元的它吗" | `gmgn-token-buy` |
| "什么是聪明资金在购买" — 钱包侧面的市场视图 | `gmgn-track smartmoney` |
| 一个代币的图表形状/趋势读取 | `gmgn-kline-pattern` |

该技能仅拥有一件事：**将原始趋势信息转换为用户可以采取行动的简短列表。** 它从不执行交易，也从不深入分析单个名称 — 如果用户想进一步了解，请将获胜者交给 `gmgn-contract-dd` 或 `gmgn-token-buy`。

## 运行

四个步骤，第 3 步运行两次：第一次运行命名其需要真实创建时间的行，第 3b 步获取这些，第二次运行打印列表。下面的每个代码块都逐字运行；只有 **参数** 中的值会改变。

**第 1 步 — 扫描所有链。** 7 条链 x 3 窗口 = 21 个调用，分步进行。

```bash
CHAINS=(sol bsc base eth robinhood arc stable)   # 当用户询问时缩小范围；切勿添加名称
# 一个数组，作为 "${CHAINS[@]}" 迭代。普通字符串作为 `for ch in $CHAINS` 迭代在 bash 下工作，在 zsh 下静默不工作，因为 zsh 对未加引号的扩展不进行单词分割：循环会以每个链名为一个变量运行一次，整个扫描会合并为单个拒绝调用。已在 zsh、bash 和 bash --posix 下验证。
# mktemp -d，不是任何人都能猜到的名称。旧的 /tmp/gmgn-heat-data-$(date +%s) 是一个世界可写目录中的秒级时间戳，heat_rank.py 写入其中并执行：另一个本地用户可以预先创建该目录并用自己的 heat_rank.py，运行会执行他们的。
DATA=$(mktemp -d); cd "$DATA"
for ch in "${CHAINS[@]}"; do
  # 链名最终会出现在命令行上，因此会检查该 API 具有的固定名称集，而不是传递。拼写错误、来自其他交易所的链或包含空格或 shell 保留字符的字符串会被明确拒绝并跳过 — 它永远不会成为 gmgn-cli 的参数。仅使用完整名称：子字符串测试（`case " sol bsc ... " in *" $ch "*`）接受任何相邻名称的运行，所以 `sol bsc` 会通过它。保持此列表字面量 — 在此处重用 $CHAINS 会将输入与自身进行比较。
  case $ch in
    sol|bsc|base|eth|robinhood|arc|stable) ;;
    *) echo "拒绝不支持的链名称: $ch" >&2; continue;;
  esac
  # 仅标记 API 实际识别的标签。未识别的标签不会被拒绝 — 它会被静默忽略，一个不包含其他内容的过滤器列表会关闭服务器自己的默认筛选，这比发送没有任何过滤器更糟。因此，第四个分支发送没有 --filter，让默认值生效；不要发明一个标签来填充它。测量结果，见 `## 已知限制`。
  case $ch in
    sol) F=(--filter renounced --filter frozen --filter not_wash_trading);;
    bsc|base|eth) F=(--filter not_honeypot --filter verified --filter renounced);;
    *) F=();;
  esac
  # 首先获取 24 小时，并在返回空时停止。候选者必须在 24 小时窗口内存在才能计算，因此一个没有任何内容的链无论其 1 小时和 6 小时列表如何都无法产生一个 — 获取它们会花费两个调用和 2.8 秒在一个保证为空的结果上。
  # 在实际扫描上测量：eth、arc 和 stable 在所有三个窗口中都是空的，因此 21 个调用中有 6 个从未有机会。跳过它们不会改变列出的名称。在一个所有七个链都活跃的日子里，扫描仍然需要其全部 21 次 — 这是减少浪费，不是覆盖范围。
  for iv in 24h 1h 6h; do
    gmgn-cli market trending --chain "$ch" --interval "$iv" --limit 100 \
      --min-marketcap 500000 --min-liquidity 100000 --max-created 7d \
      "${F[@]}" --raw > "${ch}_${iv}.json" 2>"${ch}_${iv}.err"
    sleep 1.4
    if [ "$iv" = 24h ] && ! grep -q '"rank":\[{' "${ch}_24h.json"; then
      echo "在 $ch 上没有 24 小时候选者 — 跳过其 1 小时/6 小时调用" >&2
      break
    fi
  done
done
echo "$DATA"
```

`--raw` 是强制性的，不是装饰性的：评分器从单行 JSON 中读取 `data.rank`，格式化的形式无法解析，并且上面的空窗口测试匹配该单行中的 `"rank":[{`。每个链/窗口对都有自己的文件，并且解析失败的文件会报告为缺失窗口，而不是空窗口。

**第 2 步 — 编写评分器。** 将 **实现** 下面的块复制到 `$DATA/heat_rank.py` **使用引号 heredoc** (`cat > "$DATA/heat_rank.py" <<'PY' ... PY`)。引号不是可选的：脚本中的 f-strings 包含 `$`，未加引号的 heredoc 会让 shell 吃掉它们。不要重新输入、重新格式化或“改进”脚本 — 它本身就是规则集，其中的每个阈值都是校准的；一个“更干净”的重写会无声地改变哪些代币会通过。

**第 3 步 — 评分。**

```bash
HEAT_DATA="$DATA" python3 "$DATA/heat_rank.py"
```

脚本打印诊断信息、排名表格、CA 区块和接近失败的项。它计算；它不写报告。**你** 需要使用其 stdout 从用户语言编写报告。

如果它停止在 `NEEDS-CREATED` 区块，它需要这些列的真实创建时间才能选择它们的轨道或评分它们的时效性。对 **确切** 这些地址执行第 3b 步，然后再次运行第 3 步。通常这是 1–6 次查找；区块本身会警告你如果它请求超过 20 次就需要更多，这个数字应该带给用户而不是浪费。这个停止退出 **3**，不是 0 — 在这里非零状态意味着“不完整，执行第 3b 步”，不是失败，也不是空市场。退出 0 意味着它打印的列表是答案；退出 1 意味着它无法读取自己的输入。

**第 3b 步 — 真实创建时间，仅针对第 3 步请求的行。**

```bash
# `token info --raw` 返回顶层主体，因此字段直接从对象读取。
# `creation_timestamp` 是代币创建的时间；`open_timestamp` / `migrated_timestamp` 是其池子开放的时间。在一个在迁移前存在于债券曲线上的代币上，它们之间的差距可能长达数周，这个差距是存在这个步骤的原因。在 arc/ARGUS 上实时验证：
# creation_timestamp 1788373928 (2026-09-03) 对应 migrated_timestamp 1789892415 (2026-09-20)。
# $DATA 是第 1 步打印的扫描目录。拒绝而不是将 created.tsv 写入文件系统根目录并将评分器传递给一个空文件，这会读取为“所有查找都没有返回答案”。
: "${DATA:?DATA 是未设置的 — 将其设置为第 1 步末尾打印的扫描目录}"
: > "$DATA/created.tsv"
while read -r ch addr; do
  case $ch in
    sol|bsc|base|eth|robinhood|arc|stable) ;;
    *) echo "拒绝不支持的链名称: $ch" >&2; continue;;
  esac
  case $addr in
    *[!A-Za-z0-9]*|'') echo "拒绝不是字母数字的地址: $addr" >&2; continue;;
  esac
  gmgn-cli token info --chain "$ch" --address "$addr" --raw > "$DATA/info_${ch}_${addr}.json" 2>"$DATA/info_${ch}_${addr}.err"
  printf '%s\t%s\n' "$ch" "$addr" >> "$DATA/created.tsv"
  sleep 1.4
done <<'ADDRS'
<paste the chain/address lines from the NEEDS-CREATED block here>
ADDRS
python3 - "$DATA" <<'PY'
import json,sys,os
D=sys.argv[1]; out={}; lost=[]
for line in open(f'{D}/created.tsv'):
    ch,addr=line.split()
    try: d=json.load(open(f'{D}/info_{ch}_{addr}.json'))
    except Exception: d=None
    # 退出状态无法区分这两种情况：`token info` 用一个完全为零的身体回答它不知道的地址（测量），所以零创建时间是真实答案 — 请求了，但没有内容 — 并被写入为 null，这会保持该行在更严格的全新启动轨道上，而不是这个步骤无限循环在一个 feed 永远不会回答的行上。一个无法解析或不会回显地址的身体是永远不会到达的调用（速率限制、网络、空文件）；该行完全从 created.json 中排除，所以第 3 步会再次列出它，而不是根据无人实际读取的年龄评分它。
    if not isinstance(d,dict) or not d.get('address'):
        lost.append(f'{ch} {addr}'); continue
    ts=d.get('creation_timestamp')
    try: ts=int(ts) if ts not in (None,'') else None
    except Exception: ts=None
    out[f'{ch}:{addr}']=(ts if (ts and ts>0) else None)
if lost:
    print('这些查找从未到达 — 在执行第 3 步之前对确切这些执行第 3b 步:')
    for m in lost: print('  '+m)
# 没有收集意味着所有输入行在上述检查中都被拒绝 — 粘贴是格式错误的，不是 feed。
# 在这里写入 {} 会导致第 3 步直接返回一个 NEEDS-CREATED 区块，其中包含相同的行，永远如此。
if not out: raise SystemExit('created.tsv 是空的：没有链/地址行在上述检查中幸存。精确粘贴 NEEDS-CREATED 行。created.json 没有被写入。')
json.dump(out,open(f'{D}/created.json','w'))
print('created.json:',out)
PY
```

### 节奏控制

速率限制，而不是网络，设定运行时间。`market trending` 是权重 1，并且桶每秒填充 20 次，但连续调用仍然会受罚，而受罚会花费五分钟。`sleep 1.4` 之间调用使扫描约 30 秒，并且运行良好。如果调用返回 `429`，停止循环并等待 `reset_at` — 不要重试进入受罚状态。永远不要并行运行 21 个调用。第 3b 步的查找以相同的 1.4 秒节奏进行，通常有 1–6 个，所以整个运行是 21–27 个调用。

## 参数

所有可调参数都位于一个地方。只有在用户要求时才更改值，并在报告中说明更改了哪个值。

`argument-hint` 中的四个名称是用户可以用文字询问的东西 — 它们不是命令行标志，作为标志输入会失败：`gmgn-cli market trending` 一次只接受一个 `--chain`（七链扫描是第 1 步中的循环，不是列表参数），年龄标志拼写为 `--max-created`，而上限和下限是 CLI 标志完全无法达到的 Python 常量。每个映射到下表中的一行：`chains` 到 `CHAINS` 变量，`max-created` 到 `--max-created` **和** `MAX_AGE_D` 一起，`TOP_N` 和 `MIN_SCORE` 到 `TOP_N,MIN_SCORE=` 行上的两个赋值。永远不要发明 CLI 没有的标志；不确定时检查 `metadata.cliHelp`。

| 位置 | 名称 | 默认值 | 含义 |
|---|---|---|---|
| 第 1 步 | `CHAINS` | 所有 7 个 | 不要为了节省时间而丢弃链；空链是一个发现，而不是一个空白。只有 `sol bsc base eth robinhood arc stable` 是真实名称 — 循环将每个名称与这个字面量集进行比较并拒绝任何其他内容，所以缩小是安全的，发明一个名称会大声失败。 |
| 第 1 步 | `--max-created` | `7d` | 年龄上限。“最近”在“最近热门”中的“最近”，这是一个硬门槛。 |
| 脚本 | `MAX_AGE_D` | `7.0` | 相同上限的本地后备，在每一行上检查 `open_timestamp` — 故意是迁移事件而不是真实创建时间，因为这个列表需要的是代币变得可交易。使用 `--max-created` 更改它，永远不要单独更改。 |
| 第 1 步 | `--min-marketcap` / `--min-liquidity` | `500000` / `100000` | 候选池的底部，不是最终裁决。 |
| 第 1 步 | 间隔 | `1h 6h 24h` | `5m` 在这个层级上会产生噪音。代币必须在 24 小时列表中存在才能计算，这就是为什么 24 小时首先获取，并且一个空列表会结束该链在单个调用后。 |
| 脚本 | `TOP_N` | `10` | 打印名称的硬上限。 |
| 脚本 | `MIN_SCORE` | `60` | 分数底部，在上限之前应用：一个弱市场返回少于 `TOP_N`，并且永远不会被提升以填补配额。 |
| 脚本 | `YOUNG_D` | `2.0` | 以下天数的代币在全新启动轨道上被判断，而不是成熟轨道。使用 `token info`（第 3b 步）的真实创建时间（而不是迁移时间）测量，所以一个在迁移前存在数周的代币会根据它可以实际测量的成熟阈值被判断。 |
| 脚本 | 门限常量 | 见块 | `MIN_*` / `MAX_*` / `Y_*` / `HARD_POS` — 流动性、真实交易量、换手率、集中度、rug 分数、开发者持有量、回撤。 |
| 脚本 | `U_*` | 见块 | 对于一个没有操纵门限可以判断的行（包括所有没有任何 rug 分数的链上的行）的补偿门限：`U_IMBAL` 双边胶带 0.35，`U_LIQ` 250k 池，`U_TOP10` 0.25 集中度，加上在 6 小时窗口中的存在和智能资金/KOL 底部。在触摸任何它们之前，请阅读 `## 已知限制` 下的说明。 |
| 脚本 | `U_SCORE_ADD` | `8` | 弱筛选行的分数底部高多少（68 对 60）。这是对死门限的整个补偿，因为差距在报告中没有披露任何信息 — 提高它以对那些链更严格；永远不要将其低于 0。 |
| 脚本 | `U_SNIPER` | `0.30` | 前 70 名狙击手持有上限。单向 — 它只读取实际报告的值。 |
| 脚本 | `E_HARD` | `1.0` | 文档中 `entrapment_ratio` 的顶部。高于它的值无法解释，该行会被拒绝，不会被评分。 |
| 脚本 | 轴权重 | 见 `c['score']=` 行 | 交易量大小 .22 / 持有者和 KOL 增长 .15 / 质量 .14 / 加速 .14 / 智能资金 .13 / ATH 位置 .08 / 热度 .08 / 创新性 .06 |

## 答案必须包含的内容

一个必须 **说明** 的清单。措辞是你的；顺序是固定的。

- **头部行**：有多少名字从帽子里出来了，池算术（候选人->通过关卡->列出），以及扫描的时间戳。当计数低于`TOP_N`时，将其作为结果而不是道歉——并命名最高分者中遗漏的名字，以便边界可见。**永远不要将地板作为一个数字来写。** 对于每一行，它都是`MIN_SCORE`，对于没有操作的关卡，它是`MIN_SCORE + U_SCORE_ADD`，所以最高遗漏的分数可以超过最低列出的名字——给出两个分数，让接近遗漏的块说话，并且不要解释两个等级，因为那会透露`## 规则`禁止透露的确切内容。
- **表格**，每个令牌一行：链，符号，分数，市值，池，24小时交易量，年龄，距离其自身历史最高市值有多远。
- **真实的创建年龄，当它不是表格中的年龄时。** 年龄列是令牌可交易的时间，这是7天上限筛选的；一个令牌在迁移到绑定曲线之前坐了几周，在那里读起来像几岁。当这两个年龄相差一天以上时，脚本在该令牌的地址行上打印`created=N.Nd ago`——当它这样做时，请这样说。一个以时效性为前提的列表不能将一个三周老的令牌报告为一天老。也不要默默地交换这两个：两个数字都是关于不同事物的真实数字。
- **合约地址在自己的块中**，每行一个，完整且未缩写——永远不要只在表格内。用户从这块复制以检查列表的实时情况。
- **接近遗漏**，两个或三个，带有分数和地址，以便边界是可检查的。
- **空的链，命名。** 一个没有候选者或没有幸存者的链被声明，永远不会默默消失，也永远不会给它分配一个令牌来代表它。
- **自上次运行以来发生了什么变化**，每当用户看到更早的列表时：哪些名字留下来了，哪些在哪个关卡上掉了下来，哪些是新的。一个因为触及风险关卡而掉下来的名字与一个仅仅失去分数的名字不同——说出它。
- **不要关于哪些行被弱筛选。** 在一个链上，一个操纵关卡已经死亡，这一行既没有标签也没有脚注：它要么清除了补偿阈值和更高的分数地板，要么在列表构建之前被删除。列表是一致的，并且没有列出的令牌被注释了关于它无法测量的内容。如果用户直接问为什么一个特定的名字不见了，从拒绝计数器中如实回答——一个被回答的问题不是自愿的免责声明。
- **每个列出的令牌最多只注意一件事**，只有当它背后有一个真实的风险数字（机器人份额，打包者份额，稀疏池，深度回撤）。

## 显示模板

形状固定，措辞是你的。下面的部分名称是英文的，所以你需要翻译它们；永远不要打印变量名或JSON键。

| # | 部分 | 块 | 仅在以下情况下省略 |
|---|---|---|---|
| 1 | *(无标题)* 计数和池算术 | 一行或两行 | 永远不要 |
| 2 | 列表 | 一个表格，最多`<TOP_N>`行 | 永远不要 |
| 3 | 合约地址 | 括号块，`<rank> <chain> <symbol> <address>`每行一个 | 永远不要 |
| 4 | 接近遗漏 | 括号块，相同形状加上分数 | 没有候选人得分低于地板 |
| 5 | 覆盖率和空链 | 项目符号 | 每个返回的链至少有一个列出的令牌 |
| 6 | 自上次运行以来的变化 | 项目符号，每个移动的名字一行 | 用户没有看到更早的列表 |

格式化：ascii `$` 使用千位分隔符；百分比保留一位小数；年龄为`Nh`一天以下和`N.Nd`以上；没有表情符号，没有ASCII艺术。仅加粗第1部分中的计数。

## 规则

- **一个无法运行的关卡不是一个通过关卡——所以这一行应该得到它的位置而不是带着一个警告。** 无论在哪里，一个风险字段因为链从未填满它而读作0，这一行必须清除`U_*`替代品和一个8分高的分数地板；这一行无法清除则被删除。所有这些都不会到达报告：不要标记一个列出的令牌，不要命名缺失的字段，不要用覆盖率免责声明来缓和列表。无论如何，被禁止的是称任何行为为干净，筛选或无风险——列表声称它上面的每个名字都通过了可以运行的每个关卡，并且没有更多。

**脚本对此的处理方式。** 三种情况被视为“本行未运行屏幕”：机器人分享和捆绑读取均为0；当平台表示创作者仍持有且不透露具体数量时，毛毯评分读取为0；或该行位于一个链上，在该链的整个筛选过程中`rug_ratio`在**每一行**都读取为0，这意味着没有部署毛毯模型。第三种情况必须全局决定，因为一行读取为0无法与干净代币区分——而且其重要性远超表面现象，因为`rug_ratio`在七个链中的六个链上为无效值，因此在实践中每个非sol行都存在弱筛选。此类行必须清除`U_*`阈值，并比标准分数低8分。这些替代方案故意粗糙且均为绝对值：双面胶带、250k池、更集中的分布、存在于6小时窗口内、真实智能资金或KOL钱包。无法清除这些阈值的行将被删除，删除是整个处理过程——报告中的差距从未披露，因此列表无需附带免责声明。在接触`U_SCORE_ADD`之前了解成本：在一次测量筛选中，该规则将列表从九个名称减少到五个，所有四个删除项在无毛毯模型的链上得分在60到68之间。并且永远不要将幸存者描述为遗漏的检查已通过。

- **`buy_tax` / `sell_tax` 以字符串形式到达，且不为空——早期对该文件的读取声称它们全部为零，这是一个将字符串读作数字的伪影。** 在相同的569行上测量：bsc在93%的行（恰好80行1%，最高3%）上存在实际卖出税；sol在21%（1%或3%，且其他79行的该字段为空字符串）上存在；base在6%，eth在1%；robinhood、arc和stable在整个过程中均为字面值0。样本中最大的税率为4%，因此这里没有蜜罐级陷阱——这是一个当非零时值得向用户提及的往返费用，而不是一个门槛，并且不能替代base和eth上的无效操纵门槛，因为那正是其覆盖范围崩溃的地方。`lock_percent`是不同的情况：100个bsc行中的96个和100个robinhood行中的94个恰好为0.95，sol在整个过程中为0，这是一个默认值而不是测量值；base和eth确实有所变化。今天脚本没有读取这三个字段中的任何一个。如果你在其中一个字段上添加一个门槛，请先测量价差，然后在决定其为零之前将其读作文本。

- **`entrapment_ratio` 在所有地方都报告，但仍不能作为阈值。** 在所有七个链的97%以上的行上存在，这使得它在机器人和捆绑者无效时成为理所当然的替代人选——但它与数字接触后无法幸存。sol的中位数为0.07，而eth为0.88，因此没有绝对切割可以跨链进行；在一个链内，值彼此足够接近，以至于百分位数切割变得任意（一个链的p75上限切割将一个真实运行的第三名删除，因为其超出线0.5%）；在它旨在拯救的四个链上，该技能自身的过滤获取返回每个运行的单位数，太少以至于无法估计百分位数；并且大约3%的base和eth值超出文档中0-1的范围，因此其含义在那里尚未确定。仅使用明确的读取：如果值高于`E_HARD`则无法解释，该行将被拒绝。超出范围的问题并非独特：在相同的样本中，一个base行报告`top_10_holder_rate`为2.2493，一个eth行报告该字段和`entrapment_ratio` alike为5.9e62——供应份额超过1是不可能的，因此这些行简单地被`MAX_TOP10`拒绝，这是正确的结果，但这是由于数据原因而不是风险原因发生的。如果询问此类行，请说明。

- **未识别的`--filter`标签被静默忽略，而所有未识别的过滤器列表禁用服务器的默认筛选。** 此文件以前在七个链上传递`--filter is_out_market`。这不是API知道的标签：在sol上测量，`--filter is_out_market`和`--filter zzz_fake_tag_qqq`返回了相同的22行，并且两者都返回了*没有过滤器时返回的18行的超集*。因此，发送仅由未识别标签组成的过滤器列表不是无害的方向上的无操作——它用空值替换了服务器的默认值。在sol / bsc / base / eth上，该标签与真实标签一起存在且无效（删除它返回了sol和bsc上相同的地址集）。在robinhood / arc / stable上，它是*唯一的*标签，因此这三个链的服务器端筛选被关闭：在一个robinhood筛选中，它承认了6行额外行，其中4行`is_honeypot=1`，另外还有两行既未放弃也非开源，本地门槛无法捕获。发送真实标签或无标签。

- **脚本的可用性探测仅与其样本一样好。** `AVAIL`从过滤后的候选池中推断“该链不携带此字段”，在安静的链上，该池可能只有一个或两个行——太少，无法得出任何结论。相信上表而不是单次运行探测，并用未过滤的`--limit 100`筛选重新测量，而不是从稀疏池中推断。

- **链可能因为门槛而空，而不仅仅是因为它安静。** 同一天测量：未过滤的，arc返回50行，stable返回19行，但只有每个链各返回一行满足500k市值加上100k流动性门槛，而且其中没有一个是7天以下的。因此，“arc上没有候选者”意味着“没有近期且流动性足够的”，而不是“没有数据”。

- **数字可能以文本形式到达，而这是一种数据故障，而不是风险发现。** 每个数字字段在比较之前都会被归一化一次。无法读作数字的规模字段变为0并失败其自己的底线；风险字段变为未知，永不0，因为零风险字段与干净字段无法区分。无论哪种方式，该行都被拒绝，并报告为`unreadable number: <field>`或`unreadable risk field: <field>`，其余的筛选仍然产生一个列表。如果询问此类行，请报告为*数据发送了我们无法读取的字段*——永远不要描述为代币未能通过风险检查。

- **持有者数量无法跨链比较。** 应用账户链会使其膨胀，这就是为什么增长轴在链内而不是跨链排名的原因。

## 实现

在步骤2中逐字写入`$DATA/heat_rank.py`。读取`HEAT_DATA`；不写入任何内容。

```python
import json, time, math, os
from collections import Counter, defaultdict
IV=['1h','6h','24h']; now=time.time()
def sym(t):
    """Symbols are attacker-chosen text. Strip control characters, terminal escapes and the two
    markdown metacharacters that survive into the report, so a crafted name cannot break the table
    or smuggle instructions into it. A pipe would open an extra cell in the report's markdown table
    (a token calling itself "X | buy now" would print as two columns, one of them attacker-written);
    a backtick would open or close a code span. Both become ? -- the symbol is data, and a symbol
    that needs either character to render is not one worth rendering."""
    s=str(t.get('symbol') or '?')
    s=''.join(('?' if (ord(c)<32 or ord(c)==127 or c in '|`' or 0x202a<=ord(c)<=0x202e or 0x2066<=ord(c)<=0x2069) else c) for c in s)
    return s or '?'
# ---- one normalisation pass over every field this script does arithmetic on ----
# The API has been observed to send a number as a string. Read raw, one such value aborts the whole run:
# 21 calls spent and no list at all. So every numeric field is normalised once, here, before anything
# compares or divides it -- and the two kinds of field are normalised differently on purpose.
SCALEF=('liquidity','market_cap','volume','history_highest_market_cap','price_change_percent')
CNTF  =('holder_count','smart_degen_count','renowned_count','visiting_count','buys','sells','swaps',
        'open_timestamp','creation_timestamp')
RISKF =('bot_degen_rate','bundler_rate','rug_ratio','dev_team_hold_rate','top_10_holder_rate',
        'top70_sniper_hold_rate','entrapment_ratio','bluechip_owner_percentage','insider_rate',
        'rat_trader_amount_rate')
def _f(v):
    """A number, or None if it cannot be read as one. A numeric string is still a number."""
    if v is None or v=='' or isinstance(v,(list,dict)): return None
    if isinstance(v,bool): return float(v)
    if isinstance(v,(int,float)): return None if (v!=v or v in (float('inf'),float('-inf'))) else float(v)
    try: return float(str(v).strip())
    except Exception: return None
def scalefix(t):
    """Normalise one row in place. A scale field (pool, market cap, volume, a count) that cannot be read
    becomes 0: every one of them sits under a floor gate, so 0 fails the row rather than flattering it.
    A risk field that cannot be read becomes None and is named in `t['_badrisk']` -- never 0, because a
    zero risk field is indistinguishable from a clean one and would turn "cannot tell" into "safe". Both
    kinds tag the row, and the tag is a rejection reason, so an unreadable row drops out saying why while
    the rest of the sweep still produces a list."""
    bad=[]
    for k in SCALEF:
        if k in t:
            x=_f(t[k])
            if x is None and t[k] not in (None,''): bad.append(k)
            t[k]=x or 0.0
    for k in CNTF:
        if k in t:
            x=_f(t[k])
            if x is None and t[k] not in (None,''): bad.append(k)
            t[k]=int(x or 0)
    for k in ('market_cap','liquidity'): t.setdefault(k,0.0)   # indexed directly downstream
    risk=[]
    for k in RISKF:
        if k in t:
            x=_f(t[k])
            if x is None and t[k] not in (None,''): risk.append(k)
            t[k]=x
    if bad:  t['_badnum']=bad
    if risk: t['_badrisk']=risk

DATA=os.environ.get('HEAT_DATA')   # no default: a fixed fallback path is a directory an attacker can plant
if not DATA: raise SystemExit('HEAT_DATA is unset. Run as: HEAT_DATA="$DATA" python3 "$DATA/heat_rank.py"')
CHAINS=['sol','bsc','base','eth','robinhood','arc','stable']

# ---- the two ages, and why they are two ----
# `open_timestamp` is when the pool opened / the token migrated, which is not when the token was
# created: a token created three weeks ago that migrated yesterday reads as 21.8h old. One number was
# doing all three of the age's jobs at once, and for that token it pulled in two contradictory
# directions -- it held an 18-day-old token to the new-launch run-rate floor (a threshold set for
# tokens that have no history to measure) while paying it a full freshness bonus for being newborn.
# So the jobs are split. The 7-day ceiling stays on `open_timestamp`, because "recently hot" is an
# event on the tape and migration is that event. The track choice (`YOUNG_D`) and the freshness axis
# read the real creation time, which Step 3b fetches with `token info` for the handful of rows where
# it can change something. A key present with a null value means the lookup ran and the feed carried
# no creation time for that row: that falls back to open time, which leaves the row on the stricter
# new-launch track rather than promoting it on a number nobody could read.
CRE={}
try: _raw=json.load(open(f'{DATA}/created.json'))
except Exception: _raw={}
if not isinstance(_raw,dict): _raw{}
for _k,_v in _raw.items():
    # Every entry is judged on its own. One `try` wrapped around the whole loop looked tidier and was
    # wrong twice over: a comparison against a non-number raises, so a single unreadable entry threw
    # away every entry after it, and those rows came back in the next NEEDS-CREATED block. If the feed
    # keeps answering the same unreadable value, that is not a wasted call -- it is a loop with no exit.
    try: _v=float(_v)
    except (TypeError,ValueError): _v=None
    # A creation time has to be a finite number inside the window a token could possibly exist in.
    # None and a non-numeric fail the first test; NaN fails `_v==_v`; 0, a negative, a date before the
    # first blockchain and anything in the future fail the window. None of those is "very old" -- they
    # are unreadable, and an unreadable value allowed through as very old would hand the row the easier
    # mature track and, for NaN, a full freshness bonus on top: the exact failure this section exists to
    # prevent. `float(True)` is 1.0, so a boolean lands outside the window like any other wrong type.
    # Unreadable is stored as None, which reads downstream as "asked, and there is no answer" -- the key
    # is still present, so the row is not asked for a second time.
    _ok = _v is not None and _v==_v and 1230768000<_v<=now
    CRE[str(_k)]=(int(_v) if _ok else None)
def creage(ch,a,rage):
    ts=CRE.get(f'{ch}:{a}')
    # max(): a token cannot have been created after its own pool opened, so a feed that says otherwise
    # is wrong rather than informative. Clamping keeps the invariant the second pass relies on -- a
    # looked-up age is never younger than the open-time one -- so no lookup can move a row onto the
    # easier track or buy it a freshness bonus it did not already have on the first pass.
    return max((now-ts)/86400, rage) if ts else rage

# ---- load whatever chain/interval files parsed cleanly; a chain needs 24h to be usable ----
ROWS=defaultdict(dict); missing=[]
for ch in CHAINS:
    for iv in IV:
        p=f'{DATA}/{ch}_{iv}.json'
        try: ROWS[ch][iv]=json.load(open(p))['data']['rank']
        except Exception: missing.append(f'{ch}/{iv}')
# Step 1 fetches 24h first and skips a chain's 1h/6h calls when that window comes back empty, so those
# two files are deliberately absent rather than lost. Reporting them here would turn a saving into what
# reads as two failed calls, and `missing` has to keep meaning one thing: a call that failed or returned
# JSON we could not parse. A 24h window that itself failed to load still shows up, which is the signal
# worth seeing -- the chain is unusable either way.
def _deliberate(m):
    ch,iv=m.split('/')
    return iv!='24h' and not ROWS[ch].get('24h')
missing=[m for m in missing if not _deliberate(m)]
for ch in ROWS:
    for iv in ROWS[ch]:
        for t in ROWS[ch][iv]: scalefix(t)
# Which chains carry a rug score at all? A chain whose every fetched row reads 0 has no rug model
# deployed on it, so MAX_RUG cannot fire there whatever the token is. This can only be seen chain-wide:
# one row reading 0 is indistinguishable from one clean token. Judged off every row this sweep fetched for
# the chain, which is still the age/mcap/liquidity-filtered fetch -- so a chain that returned two rows can
# be called dead on two rows. That error runs toward "no screen ran", i.e. toward strictness, which is the
# safe direction; the coverage table under `## Known limits` is the measurement to trust instead.
RUGDEAD={}
for ch in ROWS:
    hi=0.0
    for iv in ROWS[ch]:
        for t in ROWS[ch][iv]: hi=max(hi,t.get('rug_ratio') or 0.0)
    RUGDEAD[ch]=(hi==0.0)
USE=[ch for ch in CHAINS if '24h' in ROWS[ch]]
print('loaded chains:', ', '.join(f"{ch}({'/'.join(str(len(ROWS[ch][iv])) for iv in IV if iv in ROWS[ch])})" for ch in USE))
if missing: print('missing (excluded):', ', '.join(missing))

VOL ={(ch,iv):{t['address']:(t.get('volume') or 0) for t in ROWS[ch][iv]} for ch in USE for iv in IV if iv in ROWS[ch]}
U={}
for ch in USE:
    # The reference row must be the 24h one. Most of what is read off it is a current snapshot and reads
    # the same in every window -- market cap, pool, holders, the risk fields -- but price_change_percent is
    # that window's own move, so a row taken from the 1h file prints a 1h change under a 24h heading, and
    # which window a row came from varied per token. setdefault keeps the FIRST window that carried the
    # token (24h, then 6h, then 1h) instead of letting the last one loaded overwrite it.
    for iv in ['24h','6h','1h']:
        for t in ROWS[ch].get(iv,[]): U.setdefault((ch,t['address']),{}).setdefault('ref',t)
UNI=[dict(ch=k[0],a=k[1],t=v['ref']) for k,v in U.items()]

def pctl(v):
    s=sorted(v); n=len(s)
    return [(sum(1 for x in s if x<q)+sum(1 for x in s if x==q)/2)/n for q in v]
def ath_pos(t):                       # corrupt for some tokens -> None, never "worst"
    mc,hh=t['market_cap'],(t.get('history_highest_market_cap') or 0)
    return None if (hh<=0 or hh>1e10 or hh>50*mc) else mc/hh

def risknum(t,k,f):
    """Read a risk field as a number. Absent is 0 -- the field simply is not sent. But a value that is
    present and unreadable (a string, a container, NaN, an infinity) is refused instead of coerced: reading
    it as 0 would silently turn "cannot tell" into "clean", which is the one mistake a risk gate must not
    make. The rejection lands in this row's own fail list, so the row drops out and says why."""
    v=t.get(k)
    if v is None or v=='': return 0.0
    if isinstance(v,bool): return 1.0 if v else 0.0
    if isinstance(v,(int,float)):
        if v!=v or v in (float('inf'),float('-inf')): f.append(f'unreadable risk field {k}'); return 0.0
        return float(v)
    f.append(f'unreadable risk field {k}')
    return 0.0

MIN_LIQ,MIN_VOL24,MIN_TURN,MAX_TOP10,MAX_BOT=100_000,800_000,0.05,0.30,0.85
MIN_VOL1H=20_800   # pace gate: last-1h run rate must imply >=500k/day, independent of MIN_VOL24
MIN_POS,MIN_HOLDERS=0.20,500
HARD_POS = 0.10             # unconditional drawdown floor: down to 10% of its own peak is a falling knife however hot
MAX_RUG  = 0.15             # platform rug score: age-independent, same on both tracks
MAX_DEV  = 0.05             # how much the dev still holds: age-independent, same on both tracks
# (a) new-launch track (true age < 2d): judge the current run rate, not a 24h total it has not lived through,
#     plus evidence it is not a fast rug
YOUNG_D       = 2.0
MAX_AGE_D     = 7.0        # local backstop for the age gate. Step 1 asks the server for --max-created 7d and the
                           # server has been honouring it, but 'recently hot' is the whole premise of this list and
                           # nothing local was checking it: one endpoint ignoring the parameter would put a
                           # months-old token on the list under the word 'recent'. Keep this equal to --max-created.
Y_VOL1H       = 150_000     # real-volume run-rate floor: hot now, not hot once
Y_LIQ = 200_000            # absolute liquidity floor for a new launch
MIN_LMC = 0.015            # pool/mcap floor, both tracks, against shell pools; 1.5% is the low tail of the pool
Y_TOP10       = 0.25        # stricter than mature (0.30): a new launch's supply is easier to hold in few hands
Y_ATH         = 0.45        # has not collapsed off its own peak yet (first sign of a fast rug)
Y_HOLD        = 800         # holder base
Y_SM, Y_KOL   = 20, 10      # identifiable money present (either one satisfies it)
# ---- compensating strictness where a manipulation gate is dead (option B) ----
# bot_degen_rate, bundler_rate, rug_ratio and dev_team_hold_rate read a literal 0 on some chains. That
# means "never measured", not "clean": a row no gate could judge is unverified, not verified safe. Such a
# row has to clear extra thresholds instead -- and every one of them reads a field that is reported on all
# seven chains AND carries the same meaning on each. A per-chain self-calibrated threshold is not an option
# here: the fetch is already narrowed by age / mcap / liquidity, so the sparse chains yield single-digit
# rows per run and no percentile estimated from them would mean anything.
E_HARD    = 1.0        # entrapment_ratio is documented 0-1; a value outside that range is uninterpretable
U_IMBAL   = 0.35       # |buys-sells|/(buys+sells): a one-sided tape is not a market
U_LIQ     = 250_000    # bundling unverifiable -> the pool itself has to be able to absorb an exit
U_TOP10   = 0.25       # tighter than the mature 30%: concentration is the only holder signal left
U_SNIPER  = 0.30       # top-70 sniper hold share; one-directional, only ever read when actually reported
U_SCORE_ADD = 8        # an unverified row clears a higher score floor, applied at selection

# bundler ceiling = max(60%, that chain's candidate p90): cut the extreme, not a chain's normal
def _p90(vals):
    s=sorted(vals)
    return s[min(len(s)-1,int(0.90*len(s)))] if s else 0.0
# leave-one-out: a token is judged against the p90 of every OTHER candidate on its chain, so a lone
# extreme value cannot open its own gate
BUND_CAP{}
BUND_LOO{}
for ch in USE:
    pool=[(c['a'],(c['t'].get('bundler_rate') or 0)) for c in UNI if c['ch']==ch]
    vals=[x for _,x in pool]
    BUND_CAP[ch]=max(0.60,_p90(vals))
    for a,_x in pool:
        BUND_LOO[(ch,a)]=max(0.60,_p90([y for b,y in pool if b!=a]))
print("bundler per-chain calibrated ceiling (with self / max leave-one-out):",
      {ch:(round(BUND_CAP[ch],3), round(max(BUND_LOO[(ch,c['a'])] for c in UNI if c['ch']==ch),3)) for ch in USE if any(c['ch']==ch for c in UNI)})

rej=Counter(); rej_ch=defaultdict(Counter); alive=[]
for c in UNI:
    t=c['t']; ch=c['ch']; a=c['a']; f=[]
    v={iv:VOL.get((ch,iv),{}).get(a) for iv in IV}
    # An age we cannot read is unknown, not zero. The old fallback was `or now`, which made a row
    # carrying neither timestamp read as "launched this instant": full freshness credit, and rage=0
    # walked straight through MAX_AGE_D -- the one gate this entire list rests on. That is the same
    # mistake as reading a missing risk field as clean, which this file refuses to make anywhere
    # else. So an unreadable age is placed past the ceiling and reported as the data fault it is.
    # `open_timestamp` and `creation_timestamp` are normalised as counts, so an unparseable one
    # arrives here as 0 and is caught by the same test as an absent one.
    _ts=t.get('open_timestamp') or t.get('creation_timestamp')
    rage=(now-_ts)/86400 if _ts else MAX_AGE_D+1.0   # age in days; unknown never reads as 0
    cage=creage(ch,a,rage)   # real age when Step 3b fetched it, else the open-time age
    ft=[]   # track-specific failures, kept apart until the track is settled (see `need_cre` below)
    turn=(v['24h']/t['market_cap']) if (v['24h'] and t['market_cap']) else None
    _ap0=ath_pos(t)
    botr=t.get('bot_degen_rate')
    botr=None if botr in (None,0,0.0) else botr        # field absent chain-wide (eth/base) -> no discount, no penalty

disc=1.0-(botr or 0.0)
    h24=None if v['24h'] is None else v['24h']*disc    # real volume, bot share removed
    h1h=None if v['1h']  is None else v['1h'] *disc
    if t.get('_badnum'):                               f.append('不可读数字: '+','.join(t['_badnum']))
    if t.get('_badrisk'):                              f.append('不可读风险字段: '+','.join(t['_badrisk']))
    if not _ts:                                        f.append('无时间戳 (年龄未知)')
    elif rage>MAX_AGE_D:                               f.append(f'年龄>{MAX_AGE_D:g}天(本地后备)')
    if (t.get('liquidity') or 0)<MIN_LIQ:              f.append('liq<100k')
    if (t.get('liquidity') or 0)/max(t['market_cap'] or 1,1)<MIN_LMC:  f.append(f'池/市值<{MIN_LMC:.1%}')
    young = cage < YOUNG_D
    if v['24h'] is None:                               f.append('未出现在24小时列表中')
    elif not young:
        if h24<MIN_VOL24:                              ft.append('real volume<800k/天')
        if turn is not None and turn<MIN_TURN:         ft.append('turnover<5%')
    if v['1h'] is None:                                f.append('未出现在1小时列表中')
    elif h1h<(Y_VOL1H if young else MIN_VOL1H):        ft.append('1小时real volume停滞')
    if young:   # the new-launch "stood up + not a fast rug" set; every one must pass
        if (t.get('liquidity') or 0)<Y_LIQ:                 ft.append('新:池<200k')
        if (t.get('top_10_holder_rate') or 0)>Y_TOP10:      ft.append('新:top10>25%')
        if _ap0 is not None and _ap0<Y_ATH:                 ft.append('新:在高峰期崩溃')
        if (t.get('holder_count') or 0)<Y_HOLD:             ft.append('新:持有人<800')
        if (t.get('smart_degen_count') or 0)<Y_SM and (t.get('renowned_count') or 0)<Y_KOL:
                                                            ft.append('新:无智能资金/KOL')
    if risknum(t,'rug_ratio',f)>MAX_RUG:               f.append(f'rug score>{MAX_RUG}')
    if risknum(t,'dev_team_hold_rate',f)>MAX_DEV:      f.append(f'dev still holds>{MAX_DEV:.0%}')
    if (t.get('holder_count') or 0)<MIN_HOLDERS:       f.append('持有人<500')
    if risknum(t,'top_10_holder_rate',f)>MAX_TOP10:    f.append('top10>30%')
    _bc=BUND_LOO.get((ch,a),BUND_CAP[ch])
    if risknum(t,'bundler_rate',f)>_bc:                f.append(f'bundler>{_bc:.0%}(per-chain LOO)')
    if botr is not None and botr>MAX_BOT:              f.append('bot>85%')
    if t.get('is_wash_trading'):                       f.append('洗售交易')   # the EVM filter is a no-op; this has to be caught locally
    if t.get('is_honeypot') in (1,'1',True):           f.append('蜜罐')
    _ap=_ap0
    # (b) down >80% only kills when volume is also drying up: last-1h real volume under half its own daily rate
    _cool=(h24 is not None and h1h is not None and h1h<0.5*(h24/24.0))
    if _ap is not None and _ap<MIN_POS and _cool:      f.append('down>80% and volume drying up')
    # the mature track is not exempt from drawdown any more: 10% of peak is out however hot the tape
    if _ap is not None and _ap<HARD_POS:               f.append(f'down>{1-HARD_POS:.0%}(hard line)')
    # ---- option B: which manipulation gates could actually judge this row? ----
    _bund=risknum(t,'bundler_rate',f); _entr=risknum(t,'entrapment_ratio',f)
    _dev =risknum(t,'dev_team_hold_rate',f); _s70=risknum(t,'top70_sniper_hold_rate',f)
    no_bot_screen = (botr is None) and (_bund==0)     # neither bot share nor bundling was judged at all
    # rug score unmeasured, the platform says the creator is still holding, and it will not say how much:
    # "holds" and "holds 0%" cannot both be true, so the overhang is unquantified rather than absent
    overhang = (risknum(t,'rug_ratio',f)==0 and t.get('creator_token_status')=='creator_hold' and _dev==0)
    no_rug_screen = RUGDEAD.get(ch,True)              # no rug model on this chain -> MAX_RUG never fires
    unverified = no_bot_screen or overhang or no_rug_screen
    # entrapment_ratio is reported on all seven chains but is NOT usable as a threshold: its median runs
    # 0.07 on sol against 0.88 on eth, so no absolute cut transfers, and within one chain the values sit
    # close enough together that a percentile cut becomes a coin flip at the boundary. Only the one
    # unambiguous reading is acted on -- an uninterpretable risk number is not a pass.
    if _entr>E_HARD:                                    f.append('entrapment out of range')
    if _s70>U_SNIPER:                                   f.append(f'snipers hold>{U_SNIPER:.0%}')
    if unverified:
        _b,_s=t.get('buys'),t.get('sells')
        _b=_b if isinstance(_b,(int,float)) else 0; _s=_s if isinstance(_s,(int,float)) else 0
        if _b+_s>0 and abs(_b-_s)/(_b+_s)>U_IMBAL:      f.append('unverified:one-sided tape')
        if (t.get('liquidity') or 0)<U_LIQ:             f.append('unverified:pool<250k')
        if (t.get('smart_degen_count') or 0)<Y_SM and (t.get('renowned_count') or 0)<Y_KOL:
                                                        f.append('unverified:no smart money/KOL')
        if risknum(t,'top_10_holder_rate',f)>U_TOP10:   f.append('unverified:top10>25%')
        if v['6h'] is None:                             f.append('unverified:absent from 6h list')
    # Which rows is a creation-time lookup worth a call on? Only two kinds, and both must first have
    # cleared every gate the track does not touch -- a row already dead on liquidity, rug score or a
    # one-sided tape cannot have its outcome changed by its age, so it gets no call. (i) a row that
    # reads as new by open time: the real age decides which track judges it. (ii) a row that has
    # passed everything: it is going to be scored and ranked, so its freshness has to be the real one.
    # Measured on a live sweep: 13 of 48 candidates read as new by open time, 12 of those were already
    # dead on unrelated gates, and the single remaining lookup decided the only row it could have.
    c['need_cre']=(f'{ch}:{a}' not in CRE) and (not f) and (rage<YOUNG_D or not ft)
    f.extend(ft)
    f[:]=list(dict.fromkeys(f))   # a field read twice must not be reported twice
    c['unverified']=unverified; c['no_bot_screen']=no_bot_screen; c['overhang']=overhang
    c['no_rug_screen']=no_rug_screen
    c.update(rage=rage,cage=cage,h24=h24,h1h=h1h,botr=botr,fail=f,v=v,turn=turn,ath=_ap)
    for x in f: rej[x]+=1; rej_ch[ch][x]+=1
    if not f: alive.append(c)

# ---- pass 1 stops here when any surviving row's real age is still unknown ----
# Printing a ranked list off open-time ages and then a corrected one invites the reader to trust the
# first, so this run produces the addresses to look up and nothing else. Step 3b fetches them, Step 3
# runs again, and that second run prints the list. A looked-up age is never younger than the open-time
# one, so it never promotes a row onto the easier track, never raises a freshness score and never
# raises a growth rate -- every correction lands on the row that was overstating itself. The one
# knock-on effect is that the growth axis is a within-chain percentile, so lowering one row's rate
# lifts its neighbours' percentiles slightly. That is the rule working, not drift: the corrected row
# was the one inflating the bar. It cannot cause a third pass, because which rows get looked up is
# decided by the gates and the track, never by a score.
NEED=[c for c in UNI if c.get('need_cre')]
if NEED:
    print(f"\nNEEDS-CREATED {len(NEED)} row(s): real creation time unknown and it can still change the outcome.")
    print("Run Step 3b for exactly these, then run Step 3 again:")
    for c in NEED: print(f"  {c['ch']} {c['a']}")
    if len(NEED)>20:
        print(f"\n!! {len(NEED)} lookups is far above the 1-6 this normally costs. Do not fire them blind --")
        print("   say so in the report and ask the user before spending that many calls.")
    # Exit 3, not 0. "Stopped to ask for Step 3b" and "ran to completion" are different outcomes and
    # a caller holding only a status has to tell them apart: 0 = the list printed above is the answer,
    # 3 = the run is incomplete and the block above says exactly what to fetch, 1 = it could not read
    # its own inputs. A 3 here is not a crash and not an empty market; rerunning Step 3 unchanged just
    # prints the same block again.
    raise SystemExit(3)

AVAIL={}   # does this chain actually carry this field (all-zero/all-empty chain-wide = unsupported there)
for ch in USE:
    pool=[c for c in UNI if c['ch']==ch]
    AVAIL[ch]={fld: any((c['t'].get(fld) not in (None,0,0.0,'')) for c in pool)
               for fld in ['bluechip_owner_percentage','bot_degen_rate','bundler_rate','visiting_count']}
print()
for fld in ['bluechip_owner_percentage','bot_degen_rate','bundler_rate','visiting_count']:
    no=[ch for ch in USE if not AVAIL[ch][fld]]
    print(f"field {fld:<28} missing on: {', '.join(no) if no else '(none)'}")

def vacc(c):
    """Volume acceleration: self-normalised, stateless, age-independent. >1 = busier now than its own daily average."""
    v=c['v']; out=[]
    if v['24h']:
        if v['1h'] is not None: out.append((v['1h']*24)/v['24h'])
        if v['6h'] is not None: out.append((v['6h']*4) /v['24h'])
    return max(out) if out else None
for c in UNI:
    t=c['t']; c['vacc']=vacc(c)
    # Real creation age, not the open-time one. holder_count and renowned_count are totals
    # accumulated since the token existed, so dividing either by the time since its pool opened is a
    # category error, and a large one: a token that sat 18 days on a bonding curve and migrated
    # yesterday reported 10,836 holders/day and 22.0 KOLs/day against a true 993 and 2.0, on an axis
    # carrying weight 0.15. cage falls back to the open-time age when Step 3b has no answer for the
    # row, and it is clamped never to read younger than that, so a lookup can only lower a row's own
    # growth rate -- it can never inflate one.
    c['hgrow']=(t.get('holder_count') or 0)/max(c['cage'],0.5)     # holders per day since creation
    c['kgrow']=(t.get('renowned_count') or 0)/max(c['cage'],0.5)   # KOLs per day since creation
# percentiles over the whole cross-chain pool -> scores compare across chains; the cost is that
# wallet-dense chains win the growth axes
V0=3_000_000.0   # half-weight volume for significance shrinkage: ratio metrics are noise at small size, pull toward 1.0
for c in UNI:
    va=c['vacc']; vv=c['h24'] or 0
    c['vacc_raw']=va
    c['vacc']=None if va is None else 1.0+(va-1.0)*(vv/(vv+V0))
    c['sm']=c['t'].get('smart_degen_count') or 0
    c['kol']=c['t'].get('renowned_count') or 0

MIN_CH_N=5   # an in-chain percentile needs at least 5 candidates to mean anything
P=dict(
 vacc =pctl([math.log1p(max(c['vacc'] or 0,0)) for c in UNI]),
 size =pctl([math.log1p(c['h24'] or 0) for c in UNI]),
 sm   =pctl([math.log1p(c['sm']) for c in UNI]),
 kol  =pctl([math.log1p(c['kol']) for c in UNI]),
 hgrow=None, kgrow=None, vis=None,
 liq  =pctl([(c['t'].get('liquidity') or 0) for c in UNI]),
 turn =pctl([(c['turn'] or 0) for c in UNI)])
# platform-semantics fields: percentile within the chain (robinhood holders are app accounts, not on-chain wallets)
for key,get in [('hgrow',lambda c:c['hgrow']),('kgrow',lambda c:c['kgrow']),
                ('vis',  lambda c:(c['t'].get('visiting_count') or 0))]:
    out=[None]*len(UNI)
    small=[i for i,c in enumerate(UNI) if sum(1 for x in UNI if x['ch']==c['ch'])<MIN_CH_N]
    for ch in {c['ch'] for c in UNI}:
        idx=[i for i,c in enumerate(UNI) if c['ch']==ch]
        if len(idx)>=MIN_CH_N:
            q=pctl([get(UNI[i]) for i in idx])
            for j,i in enumerate(idx): out[i]=q[j]
    if small:
        q=pctl([get(UNI[i]) for i in small])
        for j,i in enumerate(small): out[i]=q[j]
    P[key]=out

for i,c in enumerate(UNI):
    t=c['t']
    conc=1-min(1.,(t.get('top_10_holder_rate') or 0)/MAX_TOP10)
    pos = 0.5 if c['ath'] is None else min(1., c['ath']/0.8)
    grow= 0.6*P['hgrow'][i]+0.4*P['kgrow'][i]
    qual= 0.55*conc+0.45*P['liq'][i]     # bluechip exists on sol only -> kept out of the cross-chain score
    heat= 0.6*P['turn'][i]+0.4*P['vis'][i]
    size= P['size'][i]
    smart=0.6*P['sm'][i]+0.4*P['kol'][i]
    # Real creation age, not the open-time one: a token created 18 days ago and migrated yesterday is
    # not newborn, and this axis is the one place the score pays for being newborn.
    fresh=max(0.0,min(1.0,(7.0-max(c['cage'],0.5))/5.0))   # linear 2d->1.0, 7d->0.0; tilts inside the window only
    c['score']=round(100*(0.14*P['vacc'][i]+0.22*size+0.08*pos+0.15*grow+0.13*smart+0.14*qual+0.08*heat+0.06*fresh),1)
    c['p']=dict(vacc=P['vacc'][i],size=size,pos=pos,grow=grow,smart=smart,qual=qual,heat=heat,fresh=fresh)

byc=Counter(c['ch'] for c in UNI); bya=Counter(c['ch'] for c in alive)
print(f"\ncross-chain candidates = {len(UNI)}   passed gates = {len(alive)}")
print("  " + "  ".join(f"{ch}:{bya[ch]}/{byc[ch]}" for ch in USE))
print("rejection reasons (all chains):", rej.most_common())
for ch in USE:
    if rej_ch[ch]: print(f"  {ch:<10}", rej_ch[ch].most_common())

TOP_N,MIN_SCORE=10,60
ranked=sorted(alive,key=lambda x:-x['score'])
def floor_for(c): return MIN_SCORE+(U_SCORE_ADD if c['unverified'] else 0)   # unverified rows earn their place at a higher bar
rows=[c for c in ranked if c['score']>=floor_for(c)][:TOP_N]   # floor first, cap second: a weak market returns fewer than 10
_listed={(c['ch'],c['a']) for c in rows}
near=[c for c in ranked if (c['ch'],c['a']) not in _listed][:3]
_nu=sum(1 for c in ranked if c['unverified'])
# The floor is two-valued, so one number here is a lie that ends up in the report: a weakly screened row
# needs MIN_SCORE+U_SCORE_ADD. Printing only MIN_SCORE made the near-miss block look self-contradictory --
# a 63.4 dropped while a 63.3 was listed -- which reads as a bug in the skill rather than the rule working.
print(f"\npassed {len(alive)} -> floor {MIN_SCORE}, or {MIN_SCORE+U_SCORE_ADD} for the {_nu} of {len(ranked)} rows no manipulation gate could judge; capped at {TOP_N} = {len(rows)} listed")
print(f"\n{'#':>2} {'chain':<9} {'sym':11s} {'score':>5} | {'vacc':>5} {'size':>4} {'pos':>4} {'grow':>4} {'smart':>5} {'qual':>4} {'heat':>4} | {'mc':>12} {'liq':>9} {'vol24h':>11} {'age':>5} {'ATH':>5} {'24h%':>8}")
for i,c in enumerate(rows,1):
    t=c['t']; p=c['p']; ap='n/a' if c['ath'] is None else format(c['ath'],'.2f')
    # A 24h change needs 24h of history. Under one day of age the window opens before the token existed, so the
    # figure is measured off the launch price and prints things like +128168.0% -- arithmetically right, useless
    # as a read on momentum, and wide enough to break the column. n/a is the honest cell, and the age column
    # immediately to its left already says why it is empty.
    chg='n/a' if c['rage']<1.0 else format(t.get('price_change_percent') or 0,'+.1f')+'%'
    print(f"{i:>2} {c['ch']:<9} {sym(t)[:11]:11s} {c['score']:>5} | {p['vacc']:>5.2f} {p['size']:>4.2f} {p['pos']:>4.2f} {p['grow']:>4.2f} {p['smart']:>5.2f} {p['qual']:>4.2f} {p['heat']:>4.2f} | ${t['market_cap']:>11,.0f} ${t['liquidity']:>8,.0f} ${c['v']['24h'] or 0:>10,.0f} {(str(round(c['rage']*24,1))+'h' if c['rage']<1 else str(round(c['rage'],1))+'d'):>5} {ap:>5} {chg:>8}")

# Addresses only, no link. Nothing in this file may point at a gmgn.ai path: the rules at the top
# forbid reaching that site, so any URL printed here is a path shape nobody was allowed to verify.
# The full address is the portable thing anyway -- it pastes into whatever front-end the reader
# already uses, and the reader searches it there.
print("\nCA (full addresses -- search one on whichever front-end you use):")
for i,c in enumerate(rows,1):
    t=c['t']
    # The table's age is how long the token has been tradable. When the token itself is materially

# 比那更早 -- 它在迁移前位于一个绑定曲线上 -- 真实的年龄在这里打印出来，
    # 因为一个以时效性为前提的列表不应将一个三周老的代币报告为一天老。
    _cg='' if abs(c['cage']-c['rage'])<=1.0 else f"  创建于={c['cage']:.1f}天前"
    print(f"{i:>2}. {c['ch']:<9} {sym(t)[:12]:12s} {c['a']}   疫苗={(c['vacc'] or 0):.2f} 持有增长率/d={c['hgrow']:.0f} Kol增长率/d={c['kgrow']:.1f} top10={(t.get('top_10_holder_rate') or 0)*100:.1f}%{_cg}")

print("\n--- 原始输入（用于手动检查；'(无数据)' = 不在那个窗口的列表上，不是零交易量）---")
fmt=lambda x: '(无数据)' if x is None else format(x,',.0f')
for c in rows:
    t=c['t']
    print(f"{c['ch']:<9} {sym(t)[:12]:12s} 1h交易量={fmt(c['v']['1h']):>13} 6h交易量={fmt(c['v']['6h']):>13} 24h交易量={fmt(c['v']['24h']):>13} 持有者={t.get('holder_count') or 0:>7,} Kol={t.get('renowned_count') or 0:>4} 智能退化者={t.get('smart_degen_count') or 0:>4} 市值={t['market_cap']:>13,.0f} 历史最高市值={t.get('history_highest_market_cap') or 0:>16,.0f}")

print("\n接近失之交臂的情况（因此边界是可检查的）：")
for c in near:
    print(f"   {c['ch']:<9} {sym(c['t'])[:11]:11s} {c['score']:>5} (需要 {floor_for(c)})  {c['a']}")
```
