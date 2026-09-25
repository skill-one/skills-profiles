<essential_principles>

**文化指数衡量行为特征，而非智力或技能。没有“好”或“坏”的配置文件。**

<principle name="never-compare-absolutes">
**切勿比较人与人之间的绝对特质值。**

0-10的量表只是一个尺子。重要的是**距离红箭的位置**（人口均值在50分位）。箭头的位置因调查而异，取决于欧盟。

**箭头移动的原因：** 较高的欧盟分数会导致箭头向右移动；较低的欧盟分数会导致箭头向左移动。这不会影响有效性——我们始终从箭头落地的位置测量距离。

**错误**：“Dan的自主性比Jim高，因为他的A是8，而他是5”
**正确**：“Dan距离他的箭头有+3个百分位数；Jim距离他的箭头有+1个百分位数”

始终提问：箭头在哪里？点距离它有多远？
</principle>

<principle name="survey-vs-job">
**调查=你是谁。工作=你试图成为谁。**

> **“你不能把鸭子送到鹰学校。”** 特质是硬线的——你只能暂时改变行为，这会消耗能量。

- **顶部图表（调查特质）**：12-16岁时硬线。不会改变。用优势手写字。
- **底部图表（工作行为）**：工作中的适应性行为。可以改变。用非优势手写字。

图表之间的巨大差异表示行为改变，如果持续3-6个月以上，会消耗能量并导致倦怠。
</principle>

<principle name="distance-interpretation">
**距离箭头决定特质强度。**

| 距离 | 标签 | 百分位数 | 解释 |
|------|------|----------|------|
| 在箭头上 | 规范性 | 50分位 | 灵活、情境性 |
| ±1个百分位数 | 倾向性 | ~67分位 | 更容易改变 |
| ±2个百分位数 | 显著性 | ~84分位 | 可见差异 |
| ±4+个百分位数 | 极端 | ~98分位 | 硬线、强迫性、可预测 |

**关键洞察：** 每个百分位数的距离=1个标准差。

极端特质驱动极端结果，但更难改变，与普通人关联度较低。
</principle>

<principle name="l-and-i-exception">
**L（逻辑）和I（创造力）使用绝对值。**

与A、B、C、D不同，你可以直接比较L和I分数：
- 逻辑8意味着“高逻辑”，无论箭头位置如何
- 创造力2意味着“低创造力”，对任何人都是如此

只有这两种特质违反了“不进行绝对比较”的规则。
</principle>

</essential_principles>

## 使用场景

- 解释文化指数调查结果（个人或团队）
- 分析来自PDF或JSON数据的CI配置文件
- 使用Gas/Brake/Glue框架评估团队构成
- 通过比较调查与工作图表检测倦怠风险
- 基于CI特质模式定义招聘配置文件
- 指导管理者如何与特定CI配置文件合作
- 根据面试记录预测CI特质
- 使用CI配置文件数据调解团队冲突

## 不适用场景

- 用于非CI行为评估（DISC、迈尔斯-布里格斯、优势识别器、预测指数、恩尼格玛）
- 用于临床心理评估或诊断
- 作为招聘/解雇决策的唯一依据——CI是众多数据点之一

<input_formats>

**JSON（如果可用）**

如果JSON数据已经提取，直接使用：
```python
import json
with open("person_name.json") as f:
    profile = json.load(f)
```

JSON格式：
```json
{
  "name": "Person Name",
  "archetype": "Architect",
  "survey": {
    "eu": 21,
    "arrow": 2.3,
    "a": [5, 2.7],
    "b": [0, -2.3],
    "c": [1, -1.3],
    "d": [3, 0.7],
    "logic": [5, null],
    "ingenuity": [2, null]
  },
  "job": { "..." : "与调查结构相同" },
  "analysis": {
    "energy_utilization": 148,
    "status": "stress"
  }
}
```

注意：特质值是`[绝对值, 相对于箭头的值]`元组。解释时使用相对值。

检查与PDF相同的目录中的匹配`.json`文件，或询问用户是否已提取JSON。

**PDF输入（必须先提取）**

⚠️ **切勿用视觉估计来获取特质值。** 视觉估计有20-30%的误差率。

当提供PDF时：
1. 检查是否已存在JSON（与PDF相同的目录，或询问用户）
2. 如果不存在，运行带验证的提取：
   ```bash
   uv run --no-project {baseDir}/scripts/extract_pdf.py --verify /path/to/file.pdf [output.json]
   ```
3. 视觉确认验证摘要与PDF匹配
4. 使用提取的JSON进行解释

**如果uv未安装：** 停止并指导用户安装它（`brew install uv`或`curl -LsSf https://astral.sh/uv/install.sh | sh`）。不要退回到视觉。

**PDF视觉（仅作参考）**

视觉仅能用于验证提取的值看起来合理，不能用于提取特质分数。

</input_formats>

<intake>

**步骤0：你有JSON或PDF吗？**

1. **如果提供JSON或找到：** 直接使用（跳过提取）
   - 检查与PDF相同的目录中的匹配`.json`文件
   - 检查用户是否提供了JSON路径
2. **如果只有PDF：** 运行带`--verify`标志的提取脚本
   ```bash
   uv run --no-project {baseDir}/scripts/extract_pdf.py --verify /path/to/file.pdf [output.json]
   ```
3. **如果提取失败：** 报告错误，不要退回到视觉

**步骤1：你有什么数据？**

- **CI调查JSON** → 进入步骤2
- **CI调查PDF** → 先提取（步骤0），然后进入步骤2
- **仅面试记录** → 进入选项8（从面试中预测特质）
- **还没有数据** → “请提供文化指数配置文件（PDF或JSON）或面试记录”

**步骤2：你想做什么？**

**配置文件分析：**
1. **解释个人配置文件** - 了解一个人的特质、优势和挑战
2. **分析团队构成** - 评估气/刹车/粘合平衡，识别差距
3. **检测倦怠信号** - 比较调查与工作，标记压力/沮丧
4. **比较多个配置文件** - 了解兼容性、协作动态
5. **获取激励建议** - 了解如何吸引和留住某人

**招聘与候选人：**
6. **定义招聘配置文件** - 确定角色的理想CI特质
7. **指导管理者对直接下属** - 根据两个配置文件调整管理风格
8. **从面试中预测特质** - 分析面试记录来估计CI特质
9. **面试总结** - 基于预测的特质评估候选人匹配度

**团队发展：**
10. **计划入职** - 基于新员工和团队配置文件设计前90天
11. **调解冲突** - 使用他们的配置文件了解两个人之间的摩擦

**提供配置文件数据（JSON或PDF）并选择选项，或描述你的需求。**

</intake>

<routing>

| 响应 | 工作流程 |
|------|----------|
| "extract", "parse pdf", "convert pdf", "get json from pdf" | `workflows/extract-from-pdf.md` |
| 1, "individual", "interpret", "understand", "analyze one", "single profile" | `workflows/interpret-individual.md` |
| 2, "team", "composition", "gaps", "balance", "gas brake glue" | `workflows/analyze-team.md` |
| 3, "burnout", "stress", "frustration", "survey vs job", "energy", "flight risk" | `workflows/detect-burnout.md` |
| 4, "compare", "compatibility", "collaboration", "multiple", "two profiles" | `workflows/compare-profiles.md` |
| 5, "motivate", "engage", "retain", "communicate" | 直接阅读`references/motivators.md` |
| 6, "hire", "hiring profile", "role profile", "recruit", "what profile for" | `workflows/define-hiring-profile.md` |
| 7, "manage", "coach", "1:1", "direct report", "manager" | `workflows/coach-manager.md` |
| 8, "transcript", "interview", "predict traits", "guess", "estimate", "recording" | `workflows/predict-from-interview.md` |
| 9, "debrief", "should we hire", "candidate fit", "proceed", "offer" | `workflows/interview-debrief.md` |
| 10, "onboard", "new hire", "integrate", "starting", "first 90 days" | `workflows/plan-onboarding.md` |
| 11, "conflict", "friction", "mediate", "not working together", "clash" | `workflows/mediate-conflict.md` |
| "conversation starters", "how to talk to", "engage with" | 直接阅读`references/conversation-starters.md` |

**阅读完工作流程后，请严格按照它执行。**

</routing>

<verification_loop>

每次解释后验证：

1. **你是否使用了相对位置？** 从未单独陈述“A是8”而没有上下文
2. **你是否参考了箭头？** 所有特质解释都相对于箭头
3. **你是否比较了调查与工作？** 识别任何行为改变
4. **你是否避免了价值判断？** 没有将特质称为“好”或“坏”
5. **你是否检查了EU？** 如果两个图表都提供，计算了能量利用率

向用户报告：
- “解释完成”
- 关键发现（2-3个要点）
- 推荐行动

</verification_loop>

<reference_index>

**领域知识**（在`references/`中）：

**主要特质：**
- `primary-traits.md` - A（自主性）、B（社交）、C（节奏）、D（顺从）

**次要特质：**
- `secondary-traits.md` - EU（能量单位）、L（逻辑）、I（创造力）

**模式：**
- `patterns-archetypes.md` - 行为模式、特质组合、原型

**原型深度配置文件**（`archetype-*.md`）：
- `archetype-administrator.md` - 管理员（高A、高B、低C、中D）
- `archetype-coordinator.md` - 协调员（低A、高B、中C、低D）
- `archetype-craftsman.md` - 工匠（低A、低B、高C、高D）
- `archetype-daredevil.md` - 冒险家（高A、低B、低C、低D）
- `archetype-debater.md` - 辩论家（中A、中高B、低C、高D）
- `archetype-facilitator.md` - 促进者（低A、中B、中C、低D）
- `archetype-influencer.md` - 影响者（低A、高B、低C、低D）
- `archetype-operator.md` - 操作员（低A、低B、高C、中高D）
- `archetype-persuader.md` - 说服者（高A、高B、低C、低D）
- `archetype-philosopher.md` - 哲学家（低A、低B、高C、低D）
- `archetype-rainmaker.md` - 造雨者（高A、高B、低C、低D）
- `archetype-scholar.md` - 学者（高A、低B、低C、高D）
- `archetype-socializer.md` - 社交者（低A、高B、低C、低D）
- `archetype-specialist.md` - 专家（低A、低B、高C、中D）
- `archetype-technical-expert.md` - 技术专家（低A、低B、高C、低D）
- `archetype-traditionalist.md` - 传统主义者（低A、低B、高C、高D）
- `archetype-trailblazer.md` - 开拓者（高A、中B、中C、低D）

**应用：**
- `motivators.md` - 如何激励每种特质类型
- `team-composition.md` - Gas、刹车、粘合框架
- `anti-patterns.md` - 常见的解释错误
- `conversation-starters.md` - 如何吸引每种模式和特质类型
- `interview-trait-signals.md` - 从面试中预测特质的信号

</reference_index>

<workflows_index>

**工作流程**（在`workflows/`中）：

| 文件 | 目的 |
|------|------|
| `extract-from-pdf.md` | 从文化指数PDF提取配置文件数据到JSON格式 |
| `interpret-individual.md` | 分析单个配置文件，识别原型，总结优势/挑战 |
| `analyze-team.md` | 评估团队平衡（气/刹车/粘合），识别差距，推荐招聘 |
| `detect-burnout.md` | 比较调查与工作，计算EU利用率，标记风险信号 |
| `compare-profiles.md` | 比较多个配置文件，评估兼容性，协作动态 |
| `define-hiring-profile.md` | 定义角色的理想CI特质，识别可接受的模式和红旗 |
| `coach-manager.md` | 帮助管理者调整特定直接下属的风格 |
| `predict-from-interview.md` | 分析面试记录以预测调查前的CI特质 |
| `interview-debrief.md` | 使用预测的特质从记录分析评估候选人匹配度 |
| `plan-onboarding.md` | 基于新员工配置文件和团队构成设计前90天 |
| `mediate-conflict.md` | 使用他们的配置文件了解和解决团队成员之间的摩擦 |

</workflows_index>

<quick_reference>

**特质颜色：**
| 特质 | 颜色 | 衡量 |
|------|------|------|
| A | 栗色 | 自主性、主动性、自信心 |
| B | 黄色 | 社交能力、互动需求 |
| C | 蓝色 | 节奏/耐心、紧迫程度 |
| D | 绿色 | 顺从性、注重细节 |
| L | 紫色 | 逻辑、情绪处理 |
| I | 青色 | 创造力、发明力 |

**能量利用率公式：**
```
利用率 = (工作EU / 调查EU) × 100

70-130% = 健康
>130% = STRESS（倦怠风险）
<70% = FRUSTRATION（离职风险）
```

**气/刹车/粘合：**
| 角色 | 特质 | 功能 |
|------|------|------|
| Gas | 高A | 增长、冒险、推动结果 |
| Brake | 高D | 质量控制、风险规避、完成 |
| Glue | 高B | 关系、士气、文化 |

**分数精度：**
| 值 | 精度 | 示例 |
|------|------|------|
| 特质（A,B,C,D,L,I） | 整数0-10 | 0, 1, 2, ... 10 |
| 箭头位置 | 小数点后一位 | 0.4, 2.2, 3.8 |
| 能量单位（EU） | 整数 | 11, 31, 45 |

</quick_reference>

<success_criteria>

一个良好解释的文化指数配置文件：
- 使用相对位置（距离箭头），从不单独使用绝对值
- 正确识别原型/模式
- 突出2-3个关键优势，基于领先特质
- 注明2-3个挑战或发展领域
- 如果两个都可用，比较调查与工作
- 提供可操作的推荐
- 避免价值判断（“好”/“坏”）
- 承认文化指数只是数据点，不是完整画面

</success_criteria>
