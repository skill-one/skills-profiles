# Darwin Skill 2.0

> **v2.1 · 2026-06-10** — 保留/回滚棘轮从「绝对分数差值」改为「**同一评分者配对比较 + 奇数 N 多数决**」（绝对分数 ±8 的评分者噪音会淹没保守编辑的真实增益、是假回滚的根源；同一评分者内部比较可消除换尺污染）。绝对分数降级为仅粗排用途。
> **v2.0 · 2026-05-28** — 吸收 Microsoft Research SkillLens（arXiv 2605.23899）的 9 维评分药方 + SkillOpt（arXiv 2605.23904）的验证门控机制 + 人在回路三层守关。
>
> 借鉴 Karpathy autoresearch 的自主实验循环，对 skills 进行持续优化。
> 核心理念：**评估 → 改进 → 实测验证 → 人类确认 → 保留或回滚 → 生成成果卡片**
> GitHub: https://github.com/alchaincyf/darwin-skill

---

## 设计哲学

autoresearch 的精髓：
1. **单一可编辑资产** — 每次只改一个 SKILL.md
2. **双重评估** — 结构评分（静态分析）+ 效果验证（跑测试看输出）
3. **棘轮机制** — 只保留改进，自动回滚退步
4. **独立评分** — 评分用子 agent，避免「自己改自己评」的偏差
5. **人在回路** — 每个 skill 优化完后暂停，用户确认再继续

与纯结构审查的区别：不只看 SKILL.md 写得规不规范，更看改完后**实际跑出来的效果是否更好**。

---

## 评分准则（9 维度，总分 100）

> **设计依据**：基于 SkillLens 论文（arXiv 2605.23899）实证发现——LLM-as-judge 评估 skill 质量准确率仅 46.4%（接近随机），加入 meta-skill 三维度后提升到 73.8%。本评分准则强化维度 3 / 维度 5 评分标准，新增维度 9「反例与黑名单」，权重平衡到 100。**目的：让评分对真实质量更敏感，减少 LLM 评分者的乐观偏差。**

### 结构维度（59 分）— 静态分析

| # | 维度 | 权重 | 评分标准 |
|---|------|------|---------|
| 1 | **前置元信息质量** | 7 | name 规范、description 包含做什么+何时用+触发词、≤1024 字符、**禁结尾加"灵活应用/根据情况判断"等空话尾巴** |
| 2 | **工作流清晰度** | 12 | 步骤明确可执行、有序号、每步有明确输入/输出 |
| 3 | **失败模式编码** | 12 | **必须显式编码失败模式**（写出"如果 X 失败 → Y"的明确分支）；有回退路径、错误恢复；**只写正向流程而不写失败分支扣 ≥3 分**（SkillLens meta-skill 维度） |
| 4 | **检查点设计** | 6 | 关键决策前有用户确认、防止自主失控；**检查点必须显性标记（🔴/STOP/CHECKPOINT），仅靠"如果...建议..."措辞不算** |
| 5 | **可执行具体性** | 18 | 不模糊、有具体参数/格式/示例、可直接执行；**禁止"建议/可以考虑/根据情况/灵活把握/视情况而定"等软化措辞**——出现 ≥3 处扣 ≥3 分（SkillLens 可执行具体性维度） |
| 6 | **资源整合度** | 4 | references/scripts/assets 引用正确、路径可达 |

### 效果维度（35 分）— 需要实测

| # | 维度 | 权重 | 评分标准 |
|---|------|------|---------|
| 7 | **整体架构** | 12 | 结构层次清晰、不冗余不遗漏、与花叔生态一致；**冗余/AI 腔废话段落（说白了/换句话说/首先其次综上等花叔禁用词）出现一处扣 1 分** |
| 8 | **实测表现** | 23 | 用测试 prompt 跑一遍，输出质量是否符合 skill 宣称的能力 |

### Meta-skill 维度（6 分）— 反例与黑名单

| # | 维度 | 权重 | 评分标准 |
|---|------|------|---------|
| 9 | **反例与黑名单** | 6 | **skill 必须有"不要做什么"的反例清单**；只写"应该做 X"没有"不要做 Y"扣 ≥3 分；红灯/危险动作/反模式应单独章节列出（SkillLens 风险-行为黑名单维度） |

### 评分规则
- 维度 1-7、9：每个维度打 1-10 分，乘以权重得到该维度得分
- 维度 8（实测表现）：跑 2-3 个测试 prompt，按输出质量打 1-10 分
- **总分 = Σ(维度分 × 权重) / 10**，满分 100
- ⚠️ **绝对总分只用于粗排（判断「哪支最弱、先改谁」），绝不用于保留/回滚决策**。实测：同一份**未改**文字换个评分者评，总分可摆 **±8**（一支只加了 3 个 🔴 字元的 skill、单评却 −8.5，全是评分者换尺、非真实退步）。保留/回滚一律走 **Phase 2 的配对比较**。
  - **为什么**：LLM 评分者给的是**抽样、不是测量**——分数住在「文字 × 该评分者当下选的标准」里，不是文字属性。绝对总分 = 用**两台未校准的秤**量节食前后，差值大半是秤的偏差；配对 = **同一台秤**量前后，误差相减抵销。成对偏好远优于绝对评分是 LLM 评分者的已知结论（RLHF 用成对比较不用绝对分，原因相同）。

### 评分准则的实证基础

评分准则设计依据来自 **SkillLens 论文（arXiv 2605.23899）** + **本机对照实验**：

- SkillLens 发现 LLM-as-judge 准确率仅 46.4%（接近随机），加入 meta-skill 三维度后升到 73.8%
- 本机对 huashu-research 做 4 类退化 → 5 个独立评分者盲测一致 V1>V2，Δ 均值 +46.5（5/5 高置信度）

**结论**：评分准则能识别粗粒度退化，但细粒度质量差异仍不可信，**重要决策必须人审**。

→ 详细论文证据 + 5 位评分者完整数据 + HL 实战案例数字见 [references/skilllens-evidence.md](references/skilllens-evidence.md)

### 关于「实测表现」维度

这是与纯结构评分最大的区别。评分方式：

1. 为每个 skill 设计 2-3 个**典型用户 prompt**（不是边缘用例，是最常见的使用场景）
2. 用子 agent 执行：一个带 skill 跑，一个不带 skill 跑（基线）
3. 对比输出质量，从以下角度打分：
   - 输出是否完成了用户意图？
   - 相比不带 skill 的基线，质量提升明显吗？
   - 有没有 skill 引入的负面影响（过度冗余、跑偏、格式奇怪）？

若子 agent 不可用（超时/资源限制），退化为「干跑验证」：读完 skill 后模拟一个典型 prompt 的执行思路，判断流程是否合理；必须在 results.tsv 标注 `dry_run`。**dry_run 比例 > 30% → 评估失效警告**（来自本机对照实验：维度 8 实测维度权重 23%，无 full_test 验证时分数不可信）。

---

## 运行时适配性审查（关卡项，独立于 9 维度评分）

skill 应当能在 Claude Code / Codex / Cursor / OpenClaw / Hermes / Gemini CLI / OpenCode 等 50+ 兼容 skills 的运行时中通用——否则其他 agent 解析时会被「在 Claude Code 里」「Claude Code skill」等措辞误判为「不是给我用的」直接拒装（实例：nuwa-skill 因此被 Marvis agent 拒绝）。

### Phase 1 基线评估时强制跑一次红灯扫描

```bash
grep -nE "(在 Claude Code|Claude Code skill|Claude Code 用户|Cursor only|Codex 中|^\[!\[Claude Code|~/\.claude/skills/[a-z]|/plugin install\b)" SKILL.md README.md 2>/dev/null
```

输出非空 = 红灯命中，**但须先读命中行上下文排除假阳性**（grep 命令本身/反例引用/讲解该规则的元陈述 = 假阳性，记 `runtime_scan=false_positive` 不改；判别表见 references/runtime-neutrality.md）→ 确认是真红灯（指令性用法）才强制把 Phase 2 第一轮定为 P0「运行时偏差修复」（写入 results.tsv 的 note 列 `runtime_warn=N`）。

### 例外（允许的「Claude Code 痕迹」）

前置元信息触发词、花叔生态内部 skill 名引用、明确标注为运行时特定章节、commit 信息——这些正当出现，不算红灯。

→ 红灯/绿灯完整对照表 + 例外清单详细规则 + Phase 1/2/3 各阶段审查时机见 [references/runtime-neutrality.md](references/runtime-neutrality.md)

---

## 自主优化循环

### Phase 0: 初始化

```
1. 确认优化范围：
   - 全部 skills → 扫描 .claude/skills/*/SKILL.md
   - 指定 skills → 用户指定列表
2. 创建 git 分支：auto-optimize/YYYYMMDD-HHMM
3. 初始化 results.tsv（如不存在）
4. 读取现有 results.tsv 了解历史优化记录
```

### Phase 0.5: 测试 Prompt 设计

在评估之前，为每个 skill 设计测试 prompt。这步很关键——没有测试 prompt，「实测表现」维度就打不了分。

```
for each skill:
  1. 读取 SKILL.md，理解它做什么
  2. 设计 2-3 个测试 prompt，覆盖：
     - 最典型的使用场景（正常路径）
     - 一个稍复杂或有歧义的场景
  3. 保存到 skill 目录/test-prompts.json：
     [
       {"id": 1, "prompt": "用户会说的话", "expected": "期望输出的简短描述"},
       {"id": 2, "prompt": "...", "expected": "..."}
     ]
```

展示所有测试 prompt 给用户，**确认后再进入评估**。测试 prompt 的质量决定了优化方向是否正确。

### Phase 1: 基线评估 — 粗排用途

> **本阶段绝对分数是粗排排名（决定先改谁），不是保留/回滚基准**。评分者对粗粒度差异会一致（「哪支最弱」可信），对细粒度差值不可信（±8 噪音）。保留/回滚在 Phase 2 用配对比较。

```
for each skill in 优化范围:

  # 结构评分（主 agent 可以做）
  1. 读取 SKILL.md 全文
  2. 按维度 1-7 逐项打分（附简短理由）

  # 效果评分（用子 agent 做，独立于主 agent）
  3. 对每个测试 prompt，派生子 agent：
     - with_skill: 带着 SKILL.md 执行测试 prompt
     - baseline: 不带 skill 执行同一 prompt
  4. 对比两组输出，打维度 8 的分

  # 汇总
  5. 计算加权总分
  6. 记录到 results.tsv
```

**如果子 agent 不可用**（超时、环境限制），维度 8 用干跑验证打分，标注 `dry_run`。不要因为跑不了测试就跳过这个维度——哪怕是模拟推演也比完全不看效果好。

基线评估完成后，展示评分卡：

```
┌──────────────────────────┬───────┬──────────────┬──────────────┐
│ Skill                    │ 分数  │ 结构短板      │ 效果短板      │
├──────────────────────────┼───────┼──────────────┼──────────────┤
│ huashu-proofreading      │ 78    │ 边界条件      │ 测试prompt2  │
│ huashu-slides            │ 72    │ 指令具体性    │ 基线持平      │
├──────────────────────────┼───────┼──────────────┼──────────────┤
│ 平均                     │ 75    │              │              │
└──────────────────────────┴───────┴──────────────┴──────────────┘
```

**🔴 检查点 · 🛑 停止：暂停等用户确认，再进入优化循环。**

### Phase 2: 优化循环

用户确认后，按基线分数从低到高排序，先优化最弱的。

```
for each skill:
  round = 0
  while round < MAX_ROUNDS (默认 3):
    round += 1

    # 第 1 步: 诊断
    找出加权短板最大的维度：weighted_gap = weight × (10 - score) / 10，结构或效果都算
    # /10 与「总分 = Σ(维度分 × 权重) / 10」同标度：weighted_gap 就是该维度还能贡献的总分数
    # 为什么不用「原始分最低」：低权重维度会制造进步幻觉——issue #18 实战中
    # 维度 9（权重 6，gap 5.3）原始分最低被优先修，而维度 8（权重 23）加权短板最大（11.5）却 4 轮未动
    # 加权短板相近（差距 ≤ 1.0，同上述标度）时，回退为原始分升序
    # HL-3 警告：维度 2/维度 3/维度 4 是相关簇，修一个时另两个常跟着涨
    # → 不要因为维度 3 短板最大就单独修，要看整簇短板再决定是否同步改

    # 第 2 步: 提出改进方案
    针对该维度，生成 1 个具体改进方案：
      - 改什么（具体段落/行）
      - 为什么改（对应评分准则哪条）
      - 预期提升多少分

    # 第 3 步: 执行改进
    编辑 SKILL.md
    git add + commit（信息: "optimize {skill}: {改进摘要}"）

    # 第 4 步: 配对重新评估（取代绝对重打分——绝对分数评分者噪音 ±8、淹没保守编辑的 +3~8 真实增益）
    派生 N=3 独立评分者，每个【同一次调用内】读两版：
      - 改前版：git show HEAD:<skill 路径>/SKILL.md（上一个保留的 commit）
      - 改后版：工作区当前 SKILL.md
    照 9 维评分准则当【比较准则】（不是各打绝对分），回 {更好 | 更差 | 持平} + 幅度{明显|微弱} + 一句理由。
    关键：同一评分者在一次调用内比两版 → 它那把不准的尺对两版【等量作用、在比较时抵销】（同一评分者内部抵消），
    这正是配对优于绝对的机制。N 取奇数（默认 3；接近平票时升 5）。

    # 第 5 步: 共识决策（多数决，取代「新总分 > 旧总分」）
    cur = 投"更好"的评分者数；wor = 投"更差"的；
    if cur >= wor:  # 多数说改后 ≥ 改前（含持平）
      status = "保留"
      # HL-4 见好就收：连续 2 轮多数评分者判幅度=微弱 或 持平 → 跳出进 Phase 3
    else:           # 多数说更差 —— 这才是真退步（已扣掉换尺噪音）
      status = "回滚"
      git revert HEAD（创建新 commit 回滚，不用 reset --hard）
      记录到 results.tsv（note 记投票比数 + 一句"更差"理由）
      break
    # 单评绝对分数出现「负差值」≠ 回滚信号；必须经配对多数判"更差"才回滚（否则在丢真实增益）

    # 第 6 步: 日志
    results.tsv 追加行

  # === 🔴 检查点 · 每个 skill 优化完后强制人审 ===
  展示该 skill 的改动摘要：
    - git diff（改前 vs 改后）
    - 分数变化（哪些维度提升/下降）
    - 测试 prompt 输出对比（如果跑过的话）
  等用户确认 OK 再继续下一个 skill。
  如果用户说"不好"，回滚到该 skill 的优化前版本。
```

### Phase 2.5: 探索性重写（按需触发）

当爬山法连续 2 个 skill 都在第 1 轮就跳出（涨不动）时，提议一次「探索性重写」：

```
1. 选一个瓶颈 skill
2. git stash 保存当前最优版本
3. 从头重写 SKILL.md（不是微调，是重新组织结构和表达方式）
4. 重新评估
5. 如果重写版 > 暂存版: 采用重写版
   否则: git stash pop 恢复
```

这解决了爬山法的局部最优问题——有时候需要「先拆后建」才能突破瓶颈。
**🔴 检查点 · 🛑 停止：必须征得用户同意后才执行。**

### Phase 3: 汇总报告

```
## 优化报告

### 总览
- 优化 skills 数：N
- 总实验次数：M
- 保留改进：X（Y%）
- 回滚次数：Z
- 实测验证：A 次完整测试 / B 次干跑

### 分数变化
┌──────────────────────────┬────────┬────────┬────────┐
│ Skill                    │ 之前   │ 之后   │ 变化   │
├──────────────────────────┼────────┼────────┼────────┤
│ huashu-proofreading      │ 78     │ 87     │ +9     │
│ huashu-slides            │ 72     │ 83     │ +11    │
├──────────────────────────┼────────┼────────┼────────┤
│ 平均                     │ 75     │ 85     │ +10    │
└──────────────────────────┴────────┴────────┴────────┘

### 主要改进
1. [skill-A] 补充了边界条件处理，测试输出质量提升明显
2. [skill-B] 重组了工作流结构，基线对比优势增大
```

---

## results.tsv 格式

```tsv
timestamp	commit	skill	old_score	new_score	status	dimension	note	eval_mode
2026-03-31T10:00	baseline	huashu-proofreading	-	78	基线	-	初始评估	full_test
2026-03-31T10:05	a1b2c3d	huashu-proofreading	78	84	保留	边界条件	补充回退	full_test
2026-03-31T10:10	b2c3d4e	huashu-proofreading	84	82	回滚	指令具体性	过度细化	dry_run
```

`eval_mode` 列：`paired`（同评分者比改前/改后，**保留/回滚的权威依据**）｜`full_test`（子 agent 跑 prompt）｜`dry_run`（模拟推演、仅供参考）。
配对行：`new_score` 栏记投票比数（如 `3-0 更好`），`note` 记一句裁断理由。例：
```tsv
2026-06-10T06:30	paired	some-skill	（绝对 87.3→78.8 = 评分者噪音）	3-0 更好	配对推翻单评假退步	paired
```
文件位置：`.claude/skills/darwin-skill/results.tsv`

---

## 实战高杠杆操作（精髓速查）

4 条经实战验证（huashu-gpt-image +10.85 / huashu-weread-advisor +14.9 / claude-design +16.5）。详细案例数据见 [references/skilllens-evidence.md](references/skilllens-evidence.md) 的「HL 实战案例」节。

- **HL-1（维度 4）显性视觉标记是杠杆**：加 🔴 检查点 / 🛑 停止，靠「必须」措辞不行——LLM 解析时扫描视觉标记。4 行改动撬动维度 4 +3 分
- **HL-2（维度 3）if-then 三段式回退表**：把「症状/解法」两列升级为「触发条件 / 一线修复 / 仍失败兜底」三段式。SkillLens 失败机制编码维度的落地
- **HL-3（Phase 2 诊断）维度相关簇警告**：维度 2/3/4 是相关簇——修维度 3 时维度 2 常跟着涨。「找最大加权短板维度」时同时看相关簇短板再决定是否同步改
- **HL-4（Phase 2 退出）触顶自动跳出**：连续 2 轮 Δ < 2 分 → 跳出进 Phase 3。+0.15 是停手信号不是继续信号；硬凑 MAX_ROUNDS=3 引入过度工程化

---

## 优化策略库

按优先级排序，每轮只做最高优先级的一个：

### P0: 运行时适配性问题（关卡项命中 → 必须先修）
- README/SKILL.md 出现红灯措辞（如「在 Claude Code 里」「Claude Code skill」）→ 替换为运行时中立措辞
- 徽章钉死单一运行时 → 改为 `Agent Skills Standard` + `skills.sh` + `Multi-Runtime` 三个中立徽章
- 安装章节只给一种运行时的路径 → 改为「一行命令（自动检测）+ 手动路径表 + 作为参考资料」三层结构
- 工作流硬编码运行时特定工具且无回退 → 给出通用替代方案或标注「仅在某运行时可用」
- 例外：skill 名明确标注单运行时（如 `xxx-codex`）的，可跳过本项

### P0: 效果问题（实测发现的）
- 测试输出偏离用户意图 → 检查 skill 是否有误导性指令
- 带 skill 比不带还差 → skill 可能过度约束，考虑精简
- 输出格式不符合预期 → 补充明确的输出模板

### P1: 结构性问题
- 前置元信息缺少触发词 → 补充中英文触发词
- 缺少阶段/步骤结构 → 重组为线性流程
- 缺少用户确认检查点 → 在关键决策处插入

### P2: 具体性问题
- 步骤模糊（"处理图片"）→ 改为具体操作和参数
- 缺少输入/输出规格 → 补充格式、路径、示例
- 缺少异常处理 → 补充 "如果 X 失败，则 Y"

### P3: 可读性问题
- 段落过长 → 拆分 + 用表格
- 重复描述 → 合并去重
- 缺少速查 → 添加 TL;DR 或决策树

---

## 异常与边界条件

流程假设环境理想，但实操常遇异常。以下预定义回退，保证优化过程不会「一跑就卡住」。

| 场景 | 触发条件 | 处理动作 |
|---|---|---|
| 不在 git 仓库 | `git rev-parse` 失败 | 询问用户：执行 `git init` 或回退到文件备份；用户选后者则 `cp SKILL.md SKILL.md.bak.YYYYMMDD-HHMM` 代替回滚 |
| results.tsv 缺失 | 文件不存在 | 新建并写表头行（9 列：含 eval_mode） |
| results.tsv 损坏 | 列数不匹配 / 非 TSV | 备份为 `.bak.YYYYMMDD-HHMM` 后重建，告知用户 |
| 分支已存在 | `git checkout -b` 失败 | 分支名末尾加 `-2` / `-3`；第 3 次失败则切回现有分支并询问继续还是新起 |
| `git revert` 失败 | 冲突 / 工作区脏 | 先 `git stash`，重试；仍失败则从上一个 commit 的 SKILL.md 读出覆盖当前文件手动恢复 |
| MAX_ROUNDS 触顶（默认 3） | 已跑 3 轮仍有短板 | 不强制跳出，展示当前最弱维度问用户「继续加 1 轮 / 进入 Phase 2.5 / 收工」 |
| 优化后超 150% 体积 | 新文件 > 原 × 1.5 | 拒绝提交，回到改进步骤精简（删冗余/合并重复），再评 |
| test-prompts.json 已存在 | 文件已在 skill 目录 | 默认复用并展示，问用户「复用 / 重写 / 追加」三选一 |
| SKILL.md 找不到 | 目录存在但无 SKILL.md | 该 skill 终止，results.tsv 记 `status=error`，继续下一个 |
| 分数计算规则 | 浮点精度漂移 | 总分保留 1 位小数，改进需严格 > 旧分（不靠四舍五入） |

**原则**：异常先告知用户，再按规则处理；绝不静默跳过或静默失败。

---

## darwin 操作反例黑名单（维度 9 应用：darwin 自己优化时不要做的事）

来自本机 results.tsv 早期 40 次 0 回滚的教训 + 评分者 G/H 自指评估暴露的反模式。每条都是**真实踩过的坑**。

| # | 反模式 | 为什么不要做 | 替代做法 |
|---|---|---|---|
| 1 | **同上下文自评自改** | 改完后立刻在同一 Claude 会话打分，会有「我刚改的肯定更好」乐观偏差（SkillLens 实证 LLM-as-judge 准确率仅 46.4%）| 必须派生**独立子 agent**；保留/回滚走**配对比较**（同评分者一次读改前+改后）的**奇数 N 多数决**，**不用绝对分数差值**（绝对分跨评分者 ±8 噪音、不可比） |
| 1b | **拿绝对分数差值当保留/回滚棘轮** | 绝对总分是抽样不是测量；基线评分者与重评评分者用不同「标准尺」，差值大半是换尺、非真实质量变化（实测一支纯加标记的 skill 单评 −8.5、全是换尺）| 绝对分只做粗排排名；保留/回滚用配对多数决，同一评分者内部抵消消除换尺污染 |
| 2 | **用 `git reset --hard` 当回滚** | 会丢工作区未提交改动；CI 历史断裂 | 用 `git revert HEAD` 创建反向 commit，保留可追溯链 |
| 3 | **为凑分增冗余** | 触顶后继续硬改往往是「加废话/加段落让 LLM 觉得更详细」，实际质量不变 | 触顶信号（连续 2 轮 Δ<2 分）→ 跳出进 Phase 3，**见好就收** |
| 4 | **跳过 test-prompts 直接评分** | 没有 test-prompts 的维度 8 是凭空打分，权重 23% 等于编造 | Phase 0.5 强制设计 2-3 个 prompt；若用户不给，默认编 3 个并展示确认 |
| 5 | **轮内改多个维度** | 多变量同时变，分数升降无法归因到具体改动 | 每轮 1 个维度；相关簇（维度 2/3/4）改其一时观察另两个是否跟涨 |
| 6 | **dry_run 比例 > 30%** | 维度 8 实测维度形同虚设，分数虚高（早期 40 次记录 67% dry_run，0 回滚） | 强制至少 1 个真实 full_test；dry_run 多的优化在 results.tsv 显式打 ⚠️ |
| 7 | **静默跳过异常** | 遇到 git/tsv 异常时静默继续，破坏棘轮完整性 | 异常表 10 条回退必须先告知用户再处理 |
| 8 | **忽视维度相关性单独优化** | 维度 2/3/4 是相关簇，单独优化维度 2 时常发现已被前轮维度 3 修复推到顶 | 找最大加权短板维度时同时看相关簇短板，决定是否同步改 |

**触发场景**：每轮 Phase 2 改动前对照本表一次。任一反模式命中 → 改方案重写。

---

## 约束规则

1. **不改变 skill 的核心功能和用途** — 只优化"怎么写"和"怎么执行"，不改"做什么"
2. **不引入新依赖** — 不添加 skill 原本没有的 scripts 或 references 文件
3. **每轮只改一个维度** — 避免多个变更导致无法归因
4. **保持文件大小合理** — 优化后 SKILL.md 不应超过原始大小的 150%
5. **尊重花叔风格** — 中文为主、简洁为上
6. **可回滚** — 所有改动在 git 分支上，用 git revert 而非 reset --hard
7. **评分独立性** — 效果维度必须用子 agent 或至少干跑验证，不能在同一上下文里「改完直接评」
8. **运行时中立性** — skill 必须能在 Claude Code、Codex、Cursor、OpenClaw、Hermes 等任何兼容 skills 的运行时中正常运行。除非 skill 名明确绑定单一运行时（如 `xxx-codex`、`huashu-slides-codex`），任何「在 Claude Code 里」「Claude Code skill」「单一徽章钉死」「安装命令只给 `.claude/skills/` 一种路径」都视为关卡不通过，须在 P0 优先修复（详见「运行时适配性审查」章节）

---

## 使用方式

### 全量优化（推荐首次使用）
```
用户："优化所有 skills"
→ Phase 0-3 完整流程
→ 默认：先基线评估，按分数升序优先优化最低 5-10 个
```

### 单个优化
```
用户："优化 huashu-slides 这个 skill"
→ 只对指定 skill 执行 Phase 0.5-2
```

### 仅评估不改
```
用户："评估所有 skills 的质量"
→ 只执行 Phase 0.5-1（设计测试 prompt + 基线评估），不进入优化循环
```

### 查看历史
```
用户："看看 skill 优化历史"
→ 读取并展示 results.tsv
```

---

## 设计灵感

> "You write the goals and constraints in program.md; let an agent generate and test code deltas indefinitely; keep only what measurably improves the objective."
> — Karpathy, autoresearch

本 skill 的对应关系：
- **program.md** → 本文件（评分准则和约束规则）
- **train.py** → 每个 SKILL.md
- **val_bpb** → ⚠️ **此处是 1.0 的概念错误源**：autoresearch 的 `val_bpb` 是**确定性损失**（重跑同数），darwin 套到 **LLM 评分者分数（随机抽样）** 上却沿用「绝对值比大小」棘轮 → 不可重复的数当可重复用。修正：9 维评分准则当**配对比较准则**、不当绝对指标
- **git 棘轮** → 保留配对多数判「改后 ≥ 改前」的 commit（不是「绝对总分更高」的 commit）
- **test set** → 每个 skill 的 test-prompts.json

区别：增加了人在回路（autoresearch 是全自主的，skill 优化需要人的判断力），以及双重评估机制（结构+效果），因为 skill 的「好坏」比损失数值更微妙。

### 学术依据与致谢

- **SkillLens**（arXiv [2605.23899](https://arxiv.org/abs/2605.23899)）：9 维评分准则的实证来源（LLM 自评 46.4% → 加 meta-skill 三维度后 73.8%）。
- **SkillOpt**（arXiv [2605.23904](https://arxiv.org/abs/2605.23904)）：验证门控编辑形式化框架。代码 [github.com/microsoft/SkillOpt](https://github.com/microsoft/SkillOpt)（`pip install skillopt`）、项目页 [microsoft.github.io/SkillOpt](https://microsoft.github.io/SkillOpt/)。🤝 2026-06-03 微软官方仓库已把 darwin-skill 列入集成名单。
- **autoresearch**：[github.com/karpathy/autoresearch](https://github.com/karpathy/autoresearch)，本 skill 1.0 的原始灵感。

---

## 成果卡片生成

每个 skill 优化完成后（或全量汇总后），自动生成视觉成果卡片，截图保存为 PNG。

### 卡片模板

模板位置：`templates/result-card.html`

3 种风格，每次随机选择一种：

| 风格 | CSS 类 | URL hash | 视觉特点 |
|------|--------|----------|---------|
| 暖色瑞士风 | `.theme-swiss` | `#swiss` | 暖白底+赤陶橙，Inter 字体，干净网格 |
| 深色终端风 | `.theme-terminal` | `#terminal` | 近黑底+荧光绿，等宽字体，扫描线 |
| 报纸风 | `.theme-newspaper` | `#newspaper` | 暖白纸+深红，衬线字体，双栏编辑风 |

### 生成流程

```
1. 复制 templates/result-card.html 到临时工作文件
2. 用 sed/编辑工具 替换占位数据：
   - data-field="skill-name" → 实际 skill 名
   - data-field="score-before/after/delta" → 实际分数
   - 9 个维度的 dim-bar-before/after width → 实际百分比（若模板仍是旧 8 维布局，加一行维度 9 反例黑名单条目）
   - data-field="improvement-1/2/3" → 实际改进摘要
   - data-field="date" → 当前日期
3. 随机选择风格：hash 设为 swiss/terminal/newspaper 之一
4. 用 scripts/screenshot.mjs 截图（2x 高清，只截 .card 元素，自动 open 图片）：
   node .claude/skills/darwin-skill/scripts/screenshot.mjs \
     /abs/path/to/card.html /abs/path/to/output.png
   # 回退方案（脚本失败时）：
   npx playwright screenshot "file:///path/to/card.html#[theme]" \
     output.png --viewport-size=960,1280 --wait-for-timeout=2000
5. 提示用户查看成果卡片 PNG

### 资源文件速查

| 路径 | 用途 |
|---|---|
| `templates/result-card.html` | 3 风格主模板（swiss/terminal/newspaper，hash 切换） |
| `templates/result-card-dark.html` / `-white.html` | 单一风格替代模板（需要锁定风格时用） |
| `scripts/screenshot.mjs` | 2x 高清截图，只截 .card，自动 open |
| `results.tsv` | 历次优化日志（9 列含 eval_mode） |
| `{skill 目录}/test-prompts.json` | 每个 skill 的测试 prompt 集（用于维度 8 实测） |

### 何时生成

- **单 skill 卡片**：每个 skill 优化完成后，展示该 skill 的分数变化
- **总览卡片**：全部优化完成后（Phase 3），展示全局战绩

### 品牌元素

- 顶部：Darwin.skill 品牌标识 + 日期
- 底部：「Train your Skills like you train your models」+ github.com/alchaincyf/darwin-skill

## 版本自检（静默）

本节给 AI agent：每次使用本 skill 前，先做一个不联网的判断——读本 skill 目录（SKILL.md 所在目录）下的 `.last-update-check` 文件（内容为一行日期 YYYY-MM-DD）。文件存在且距今不足 30 天，跳过本节直接干活，不向用户提任何更新相关的话。

到期或文件不存在时，且仅在此时：

1. 本目录不是 git 克隆（无 `.git` 或无 origin）→ 写入今天日期后跳过本节
2. 对比版本：`git -C <本目录> rev-parse HEAD` 与 `git -C <本目录> ls-remote origin HEAD`
3. 无论结果如何，把今天日期写入 `.last-update-check`
4. 两者一致 → 什么都不说；确认落后 → 先完成用户当前任务，结束后附一句「本 skill 有新版本，可用 `git -C <本目录> pull --ff-only` 更新」。是否更新由用户决定，不要主动执行更新
