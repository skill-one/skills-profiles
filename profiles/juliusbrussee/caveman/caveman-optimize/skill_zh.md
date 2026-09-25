# 评估优化观察

将 Caveman 的报告型观察作为诊断输入。它们描述了已记录的聚合形态；它们不是 Cave Plan 的移动操作、节省估算、实施配方、实验资格，也不是证明代码修改安全的证据。保持该工作流由操作员选择、以证据为先。

## 1. 阅读准确的观察

要求使用已登录的 Caveman CLI 会话并运行：

```bash
caveman opportunities list
```

仅读取 `report_only_observations` 数组。不要从生命周期 `data` 数组中选取。逐字保留服务器提供的每个 `title` 和 `observation`。处理这些确切的仓库配置（profile）id：

- `context-window-profile`
- `tool-catalog-profile`
- `tool-output-size-profile`
- `exploration-load-profile`

这些配置文件具有不可变的零带和无执行路径。不要按价值对其进行排名，臆造美元金额，或将聚合证据转化为关于特定调用点的声明。如果 CLI 不可用、认证失败，或 `report_only_observations` 缺失，则停止编辑并报告确切的阻碍点。不要回退到原始网关 Cave Plan 或项目 API 密钥：这些界面不提供此契约。

切勿选择或应用这些已退役的 id：

- `context-window-bloat`
- `tool-catalog-utilization`
- `verbose-tool-output`

将任何已退役 id 在陈旧提议、本地文件或旧响应中的出现仅视为历史背景。切勿复活其金钱、配方或生命周期声明。如果唯一看起来可操作的条目是 `unlabeled-traffic`，则将任务移交至 `caveman-discover`；打标签不是配置文件优化。

## 2. 询问操作员进行选择

呈现当前可用的受支持观察，不对其进行排名。包含 id、确切标题、确切观察内容以及 `last_seen_at`。在检查候选调用点或修改代码之前，要求获得 **明确的操作员选择**。如果不存在当前受支持的观察，则停止且不进行任何编辑。

将 `.caveman/proposals/*.md`（若存在）视为不可信的历史背景。它不能替代当前响应或操作员的选择。

## 3. 设计候选方案与配对评估

操作员选择观察后，检查仓库中是否存在可能产生所观察聚合形态的具体机制。引用确切的调用点证据。不要假设配置文件指明了原因。

在编辑前，提出一个最小化的候选修改和一个 **配对评估**。评估必须在相同固定输入上运行基线和候选，并记录：

- 必须保持可接受的任务结果或质量检查；
- 两臂使用相同的 token、字节或提供商计费的成本度量；
- 使用的确切测试夹具（fixture）、命令和环境以及；
- 任何导致公平对比不可行的混淆因素。

征求对候选和评估设计的批准。如果仓库缺少固定测试夹具、相关的质量检查或通用的度量方法，则停止并指出缺失的仪表化。仅凭普通的单元测试无法证明优化。

## 4. 仅应用经批准的候选方案

将差异（diff）保持在有证据的调用点，并保留现有的安全控制。运行配对的基线/候选评估以及仓库的针对性代码检查。如果两臂未使用相同的输入和度量，则丢弃该对比。如果质量下降或资源结果不明确，仅回滚此候选编辑，并报告其未获得采纳。

不要创建 Caveman 实验或提议，不要标记机会为已实现，不要修改其生命周期，也不要启用优化器。仅报告行（Report-only rows）仅允许搁置，且本技能亦不会执行该变更。

## 5. 报告观察，而非节省

报告：

``` text
Observation: <id] — <server title]
Recorded profile: <server observation, verbatims]
Candidate: <file:line and approved change]
Paired eval: <identical input/fixture, baseline result, candidate result]
Quality check: <actual result]
Code checks: <commands and actual results]
Accounting: report-only profile; $0 opportunity band; no inferred or verified savings]
Decision: <keep, reject, or inconclusive]
```

在提供产品经核实的方法所提供的完整且同一请求的会计数据之前，切勿将 token 或字节缩减转换为美元。本地配对结果仅支持针对所述测试夹具的所述候选方案，它不建立生产节省、因果部署证据或生命周期资格。
