# cuOpt 数值优化技能 (Python)

使用 NVIDIA cuOpt 的 GPU 加速求解器对 LP、MILP 和 QP 问题进行建模和求解。Python API 界面 (`Problem`, `SolverSettings`, `solve`) 在这三个问题类别之间共享——只有目标形式和一些规则会改变。

## 开始前

如果可用，请使用公式摘要（参数、约束、决策变量、目标）；否则请询问决策变量、目标和约束。然后确认**问题类型**（LP / MILP / QP——见下文）和**变量类型**。

## 选择 LP 与 MILP 与 QP

**根据目标和变量进行判断：**

| 如果目标是... | 且变量是... | 使用 |
|---|---|---|
| 线性（`c_i * x_i` 的和） | 所有连续 | **LP** |
| 线性 | 一些整数或二元 | **MILP** |
| 包含平方（`x*x`）或交叉（`x*y`）项 | 连续（不支持整数 QP） | **QP** (beta) |

**当问题允许时优先选择 LP**。LP 求解速度更快，具有更强的最优性保证。仅在问题逻辑上需要整数或 yes/no 决策时使用 MILP。仅在目标真实为二次（方差、平方误差、动能）时使用 QP。

**需要特别小心的典型问题类型**：多周期规划和目标规划容易误解。请仔细检查速率和约束是否适用于正确的时间段或优先级级别（AGENTS.md：在编写代码前验证理解）。

- **使用 LP** 当每个数量都可以有意义地是分数：流量、比例、速率、美元、小时、材料吨数等。
- **使用 MILP** 当问题提到**离散实体的计数**、**yes/no** 选择或**要么/要么**决策（例如，是否开设设施、将人员分配到班次、卡车数量）。
- **使用 QP** 当目标是最小化方差、平方误差或任何包含 `x*x` 或 `x*y` 项的表达式（投资组合优化、最小二乘、正则化回归）。

## 文字描述与连续/整数变量的选择

根据问题描述选择变量类型。

| 问题文字/概念 | 变量类型 | 示例 |
|---------------------------|---------------|----------|
| **离散实体（计数）** | **INTEGER** | 工人、汽车、卡车、机器、飞行员、设施、制造单位（当“单位”指代完整物品时）、实习生、车辆 |
| **Yes/no 或 on/off** | **INTEGER**（二元，lb=0 ub=1） | 开设设施、运行机器、生产产品线、将人员分配到班次 |
| **可以分数的量** | **CONTINUOUS** | 吨、升、美元、小时、kWh、容量比例、流量体积、重量 |
| **速率或分数** | **CONTINUOUS** | 利用率、百分比、预算份额 |
| **不清楚** | 如果名词是可计数的实体（工人、汽车），优先选择 **INTEGER**；如果它是度量（钢量、工作小时），优先选择 **CONTINUOUS**。如果问题说“整数”或“数量”，使用 INTEGER。 |

**经验法则**：如果数量是“多少个*东西*”（人员、车辆、物品、地点），使用 **INTEGER**。如果它是“多少”（质量、体积、金钱、时间）或速率，除非问题明确要求整数，否则使用 **CONTINUOUS**。

## 快速参考：Python API

### LP 示例

```python
from cuopt.linear_programming.problem import Problem, CONTINUOUS, MAXIMIZE
from cuopt.linear_programming.solver_settings import SolverSettings

# 创建问题
problem = Problem("MyLP")

# 决策变量
x = problem.addVariable(lb=0, vtype=CONTINUOUS, name="x")
y = problem.addVariable(lb=0, vtype=CONTINUOUS, name="y")

# 约束
problem.addConstraint(2*x + 3*y <= 120, name="resource_a")
problem.addConstraint(4*x + 2*y <= 100, name="resource_b")

# 目标
problem.setObjective(40*x + 30*y, sense=MAXIMIZE)

# 求解
settings = SolverSettings()
settings.set_parameter("time_limit", 60)
problem.solve(settings)

# 检查状态（CRITICAL：使用 PascalCase！）
if problem.Status.name in ["Optimal", "PrimalFeasible"]:
    print(f"Objective: {problem.ObjValue}")
    print(f"x = {x.getValue()}")
    print(f"y = {y.getValue()}")
```

### MILP 示例（包含整数变量）

```python
from cuopt.linear_programming.problem import Problem, CONTINUOUS, INTEGER, MINIMIZE

problem = Problem("FacilityLocation")

# 二元变量（整数，边界 0-1）
open_facility = problem.addVariable(lb=0, ub=1, vtype=INTEGER, name="open")

# 连续变量
production = problem.addVariable(lb=0, vtype=CONTINUOUS, name="production")

# 链接约束：如果设施开放，则可以生产
problem.addConstraint(production <= 1000 * open_facility, name="link")

# 目标：固定成本 + 可变成本
problem.setObjective(500*open_facility + 2*production, sense=MINIMIZE)

# MILP 特定设置
settings = SolverSettings()
settings.set_parameter("time_limit", 120)
settings.set_parameter("mip_relative_gap", 0.01)  # 1% 最优性差距

problem.solve(settings)

# 检查状态
if problem.Status.name in ["Optimal", "FeasibleFound"]:
    print(f"Open facility: {open_facility.getValue() > 0.5}")
    print(f"Production: {production.getValue()}")
```

### QP 示例（beta — 仅支持 MINIMIZE）

```python
from cuopt.linear_programming.problem import Problem, CONTINUOUS, MINIMIZE
from cuopt.linear_programming.solver_settings import SolverSettings

# 投资组合方差最小化
problem = Problem("Portfolio")
x1 = problem.addVariable(lb=0, ub=1, vtype=CONTINUOUS, name="stock_a")
x2 = problem.addVariable(lb=0, ub=1, vtype=CONTINUOUS, name="stock_b")
x3 = problem.addVariable(lb=0, ub=1, vtype=CONTINUOUS, name="stock_c")

# 二次目标（方差）— 必须是 MINIMIZE
problem.setObjective(
    0.04*x1*x1 + 0.02*x2*x2 + 0.01*x3*x3
    + 0.02*x1*x2 + 0.01*x1*x3 + 0.016*x2*x3,
    sense=MINIMIZE,
)

# 线性约束
problem.addConstraint(x1 + x2 + x3 == 1, name="budget")
problem.addConstraint(0.12*x1 + 0.08*x2 + 0.05*x3 >= 0.08, name="min_return")

problem.solve(SolverSettings())
if problem.Status.name in ["Optimal", "PrimalFeasible"]:
    print(f"Variance: {problem.ObjValue}")
```

**QP 规则：**
- **仅支持 MINIMIZE** — 求解器会拒绝用于二次目标的 MAXIMIZE。要最大化 `f(x)`，最小化 `-f(x)`。
- **仅支持连续变量** — 不支持整数 QP。
- **Q 应该是 PSD**（正定半定）对于凸问题；否则求解器可能会返回非最优的驻点。
- **beta** — API 可能会变化；对于典型的凸 QP 将其视为可生产，但预期偶尔会有变化。

参考 `references/qp_examples.md` 获取最小二乘、最大化解决方案和工作绕过、矩阵形式示例。

## CRITICAL：状态检查

**状态值使用 PascalCase，不是 ALL_CAPS：**

```python
# ✅ 正确
if problem.Status.name in ["Optimal", "FeasibleFound"]:
    print(problem.ObjValue)

# ❌ 错误 — 将静默失败！
if problem.Status.name == "OPTIMAL":  # 从不匹配！
    print(problem.ObjValue)
```

**LP 状态值：** `Optimal`, `NoTermination`, `NumericalError`, `PrimalInfeasible`, `DualInfeasible`, `IterationLimit`, `TimeLimit`, `PrimalFeasible`

**MILP 状态值：** `Optimal`, `FeasibleFound`, `Infeasible`, `Unbounded`, `TimeLimit`, `NoTermination`

**QP 状态值：** 与 LP 相同。对于 QP 调试，打印 `f"Actual status: '{problem.Status.name}'"` 并检查 Q 是否是 PSD，变量是否合理缩放。

## 常见建模模式

### 二元选择
```python
# 从 n 个物品中选择恰好 k 个
items = [problem.addVariable(lb=0, ub=1, vtype=INTEGER) for _ in range(n)]
problem.addConstraint(sum(items) == k)
```

### Big-M 链接
```python
# 如果 y=1，则 x <= 100；如果 y=0，x 可以是任何值直到 M
M = 10000
problem.addConstraint(x <= 100 + M*(1 - y))
```

### If-then “必须也生产”
当问题说“如果我们做 X，那么我们必须也做 Y”，执行以下两项（i）二元链接和（ii）确保 Y 确实被生产：
```python
# y_X <= y_Y（如果我们做 X，我们必须“做” Y）
problem.addConstraint(y_X <= y_Y)
# 当 y_Y=1 时 Y 的生产：当 y_Y=1 时至少生产 1（或最小量）时
problem.addConstraint(production_Y >= 1 * y_Y)  # 或 min_amount * y_Y
```
否则求解器可以设置 y_Y=1 但 production_Y=0，满足二元链接但不符合意图。

### 构建大型表达式
多个项的链式 `+` 可能会触发 API 中的递归限制。优先使用 **LinearExpression** 构建目标函数和约束：
```python
from cuopt.linear_programming.problem import LinearExpression

# 代替 v1*c1 + v2*c2 + ... 构建列表的 (变量, 系数) 而不是
vars_list = [x, y, z]
coeffs_list = [
    1.0,
    2.0,
    3.0,
]
expr = LinearExpression(vars_list, coeffs_list, constant=0.0)
problem.addConstraint(expr <= 100)
```
参考此技能的 `assets/` 中的参考模型，以获取示例。

### 分段线性（SOS2）
```python
# 使用断点近似非线性函数
# 使用求和为 1 的 lambda 变量，最多 2 个相邻非零
```

## 求解器设置

```python
settings = SolverSettings()

# 时间限制
settings.set_parameter("time_limit", 60)

# MILP 差距容忍度（当在 X% 的最优范围内停止时）
settings.set_parameter("mip_relative_gap", 0.01)

# 日志记录
settings.set_parameter("log_to_console", 1)
```

## 常见问题

| 问题 | 可能原因 | 解决方法 |
|---------|--------------|-----|
| 状态从不“OPTIMAL” | 使用了错误的案例 | 使用 `"Optimal"` 而不是 `"OPTIMAL"` |
| 整数变量具有分数值 | 定义为 CONTINUOUS | 使用 `vtype=INTEGER` |
| 无解 | 矛盾的约束 | 检查约束逻辑 |
| 无界 | 缺少边界 | 添加变量边界 |
| 求解缓慢 | 大型问题 | 设置时间限制，增加差距容忍度 |
| 最大递归深度 | 使用链式 `+` 构建大型表达式 | 使用 `LinearExpression(vars_list, coeffs_list, constant)` |
| QP 拒绝 MAXIMIZE | QP 仅支持 MINIMIZE | 目标取反：最小化 `-f(x)` |
| QP 返回非最优 | Q 不是 PSD 或变量缩放不合理 | 检查 Q 是否是 PSD；重新缩放变量到相似的量级 |

## 获取对偶值（LP / QP）

对偶值和缩减成本返回**LP 和 QP**。当模型具有二次约束时（所有值都返回为 `NaN`），仅当所有约束都是线性时才读取它们。MILP 不返回对偶值。

```python
if problem.Status.name == "Optimal":
    constraint = problem.getConstraint("resource_a")   # 线性约束
    print(f"Dual value: {constraint.DualValue}")       # 如果模型有二次约束，则为 NaN
```

## 参考模型

所有参考模型都位于此技能的 **`assets/`** 目录中。在构建新应用程序时，将它们作为参考；不要就地编辑它们。

### 最小/规范示例（LP、MILP、QP）
| 模型 | 类型 | 描述 |
|-------|------|-------------|
| [lp_basic](assets/lp_basic/) | LP | 最小 LP：变量、约束、目标、求解 |
| [lp_duals](assets/lp_duals/) | LP | 对偶值和缩减成本 |
| [lp_warmstart](assets/lp_warmstart/) | LP | PDLP 热启动用于相似问题 |
| [milp_basic](assets/milp_basic/) | MILP | 最小 MIP；包括占位符回调示例 |
| [milp_production_planning](assets/milp_production_planning/) | MILP | 具有资源约束的生产计划 |
| [portfolio](assets/portfolio/) | QP | 最小化投资组合方差；预算和最小回报约束 |
| [least_squares](assets/least_squares/) | QP | 最小化 (x-3)² + (y-4)²（最近点） |
| [maximization_workaround](assets/maximization_workaround/) | QP | 通过最小化 -f(x) 最大化二次 |

### 其他参考
| 模型 | 类型 | 描述 |
|-------|------|-------------|
| [mps_solver](assets/mps_solver/) | LP/MILP | 从标准 MPS 文件格式求解任何问题 |

**快速命令列出模型：** `ls assets/`（从此技能的目录中）。

## 何时升级

如果：
- 无解且无法确定原因
- 数值问题
使用故障排除和诊断指南。
