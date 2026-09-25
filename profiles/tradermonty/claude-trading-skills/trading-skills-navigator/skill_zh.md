# 交易技能导航器

本仓库的交互式入口。它将用户的目标转化为具体的推荐：运行哪个**工作流**、属于哪个**技能集**（技能索引类别）、**API需求**，以及Claude Web App或Claude Code的**设置路径**。

新用户面对74项技能+11个工作流，没有路由器。这项技能就是那个路由器。它是**确定性**的——Python推荐器（`scripts/recommend.py`）消耗仓库元数据；这个SKILL.md以对话形式叙述结果。

## 使用场景

- 用户表达交易/投资目标，询问从哪里开始或使用哪个技能/工作流（“该用哪个”，“我从哪里开始”）。
- 用户询问没有付费API密钥时什么有效。
- 用户希望将无API与API路径分开，或需要初学者路径。
- 用户描述一个角色（“兼职波段交易者”，“股息投资者”，“我想做空”，“我想回测想法”）并需要路由。

**不要**使用此技能执行交易、下单或自动运行其他技能。它仅推荐和解释。

## 工作流

### 第1步——捕获目标和约束

从用户消息中提取：

- 自然语言**目标**（逐字即可）。
- 可选约束：仅**无API**？每日**时间预算**（15m/30m/60m/90m）？**经验**水平（初学者/中级/高级）？

如果目标为空或没有可辨别的意图，最多问一个简短的澄清问题。否则继续——推荐器会优雅地降级。

### 第2步——运行推荐器

```bash
python3 skills/trading-skills-navigator/scripts/recommend.py \
  --query "<用户的逐字目标>" \
  --format json
  # 可选：--no-api  --time-budget 15m|30m|60m|90m|any
  #           --experience beginner|intermediate|advanced
```

- 在**Claude Code**中，脚本自动读取仓库根目录的SSoT
  (`skills-index.yaml` + `workflows/*.yaml`)。
- 在**Claude Web App**中没有仓库根目录；脚本透明地回退到捆绑的`assets/metadata_snapshot.json`。在两种环境下推荐结果字节相同——对用户没有行为变化。

### 第3步——以对话形式叙述结果

解析JSON，用用户的语言解释：

- **主要工作流**——`display_name`、`cadence`、`~estimated_minutes`、`api_profile`。明确说明它做什么以及何时运行。
- **路由诊断**——读取`routing_diagnostics.status`。对于`ambiguous`，列出每个`candidate_personas`条目，并解释选择了排序后的第一个匹配项。对于`fallback`，说明没有匹配的角色，并要求用户重述；永远不要将初学者回退作为精确意图匹配呈现。
- **次要工作流**——如果有，它们如何关联（例如，“先运行状态检查，然后当允许风险时运行这个”）。
- **技能集**——`skillset.id`（技能索引类别）。`manifest_status: active`表示为该类别提供经过策展的`skillsets/<id>.yaml`捆绑包（市场状态、核心投资组合、波段机会、交易记忆）——将其作为推荐工作流的安装捆绑包提及。`manifest_status: deferred`表示没有清单（例如诚实差距类别）；推荐仅基于工作流。
- **无API与API**——读取`no_api_path`：`true` → 整个推荐路径可以在没有付费API密钥的情况下工作（明确说明）；`false` → 告知用户路径需要哪些付费密钥；`null` → 诚实差距，没有路径。(`no_api`是*请求*标志——无API模式是否激活——不是路径是否免费；始终叙述`no_api_path`。）如果在工作流下`--no-api`被排除，则显示`rationale`条目命名付费集成（例如，“波段机会-每日需要FMP”）。
- **诚实差距**——如果`honest_gap`为true，则**没有发布的工作流**适用于此意图。直接说明，然后呈现来自相关类别的`suggested_skills`并传达`note`。永远不要编造工作流。
- **操作角色**——叙述设置捆绑包或诚实差距建议中每个技能的`operational_roles`条目。当存在时解释独立理由；保持枚举值不变。
- 始终读取`rationale`数组并解释*为什么*这样推荐。

### 第4步——解释设置路径

读取`references/setup_paths.md`并引导用户安装**`setup_bundle`**——推荐器的确定性安装并集，覆盖主要技能集**和每个次要工作流**（因此对于多工作流推荐不会丢弃任何内容）。枚举`setup_bundle.required` → `recommended` → `optional`，引用`setup_bundle.sources`解释*为什么*每个技能都需要，并命名`skillset.manifest.related_workflows`以解释*如何*运行捆绑包。叙述`skillset.manifest`（当存在时）作为“推荐的技能集是什么”。对于诚实差距安装`suggested_skills`。为用户所处的环境（Claude Web App `.skill`上传或Claude Code文件夹复制）执行此操作；指出这些技能需要的任何付费API密钥。

### 第5步——指向学习循环

最后将用户指向`trader-memory-core`和`trade-memory-loop` / `monthly-performance-review`工作流，以便每条推荐路径都为计划→交易→记录→审查→改进循环提供输入。

## 输出格式

推荐器发出的JSON（稳定、幂等、`sort_keys`）：

| 字段 | 含义 |
|---|---|
| `primary_workflow` | 推荐的工作流对象，或在诚实差距时为`null` |
| `secondary_workflows` | 支持的工作流（有序，时间预算过滤） |
| `skillset` | `{id, source: skills-index.category, manifest_status, manifest}`。`manifest_status`在`skillsets/<id>.yaml`提供时为`active`，否则为`deferred`。`manifest`在激活时为5键视图`{display_name, required_skills, recommended_skills, optional_skills, related_workflows}`，否则为`null`。描述**主要技能集**——不是安装列表 |
| `setup_bundle` | `{required, recommended, optional, sources}`——覆盖主要技能集**和每个次要工作流**的行动性安装并集（确定性，层级去重）。**这是要安装的内容。**在诚实差距时为空（使用`suggested_skills`） |
| `suggested_skills` | 当没有工作流发布时使用的技能（诚实差距）；否则`[]` |
| `operational_roles` | 技能ID → `{type, rationale?}`为每个设置捆绑包技能，或在诚实差距时为每个`suggested_skills`项 |
| `no_api` | 请求端：无API约束模式是否激活（标志或角色） |
| `no_api_path` | 路径端：整个推荐（主要+每个次要）是否可以在没有付费API密钥的情况下工作？`true`/`false`；诚实差距时为`null`。这是DoD的API与无API分离——明确叙述它 |
| `honest_gap` | `true`当意图没有工作流存在时 |
| `note` | 间隙/未映射输入的平语言解释 |
| `rationale` | 为什么这样推荐的字符串有序列表 |
| `routing_diagnostics` | `{status, selected_persona, candidate_personas, explanation}`。`status`是`exact`、`ambiguous`或`fallback`；候选者是约束前所有角色匹配项的确定性排序 |
| `setup_path_ref` | 指向设置路径参考 |

## 资源

- `scripts/recommend.py` — 确定性推荐器（路由单一来源）。
- `scripts/build_snapshot.py` — 从SSoT重新生成`assets/metadata_snapshot.json`；`--check`保护漂移（预提交+CI）。
- `scripts/intent_benchmark.py` — 验证故障关闭的双语路由语料库、角色阴影合同和元变形不变性。
- `references/intent_routing.md` — 角色表、10个问题合同、`--no-api`凭证规则和评分平局。
- `references/setup_paths.md` — Claude Web App与Claude Code设置步骤。
- `assets/metadata_snapshot.json` — 为Web App回退生成的SSoT摘要。永远不要手动编辑；运行`build_snapshot.py`。
- `assets/intent_benchmark_v1.json` — 211个明确标记的EN/JA路由案例，具有1.0的精确率/召回率和每个角色/工作流的覆盖率门。
