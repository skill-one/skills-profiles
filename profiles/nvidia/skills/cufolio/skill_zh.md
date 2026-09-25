# cuFOLIO 技能

<!--
SPDX-文件版权声明: 版权所有 (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES。保留所有权利。
SPDX-许可证标识符: Apache-2.0
-->

## 目的

使用 NVIDIA 加速的 Mean-CVaR 优化来构建和分析量化投资组合。使用 cuFOLIO 计算回报、生成 KDE 场景、使用 cuOpt GPU 求解器解决分配问题、追踪有效前沿、回测投资组合并从价格数据运行再平衡工作流。

## 何时使用

当任务需要执行以下操作时，请使用此技能：

- 从股票价格构建或优化 Mean-CVaR 投资组合。
- 在控制下 CVaR 风险的同时，分配权重到各个股票代码。
- 绘制或检查投资组合宇宙的有效前沿。
- 生成按风险厌恶程度划分的权重表。
- 对优化后的投资组合进行基准回测。
- 按计划或漂移触发器进行投资组合再平衡。
- 在 S&P 500、S&P 100、道琼斯 30 或用户提供的价格数据集上运行工作流。

常见的触发短语包括 "优化我的投资组合"、"构建一个 CVaR 投资组合"、"在这些股票代码上使用 cuFOLIO"、"使用 cuOpt 求解"、"绘制有效前沿"、"按风险厌恶程度显示权重"、"回测此分配"、"每月再平衡"、"使用 CVaR 分析我的持仓"、"比较分配"、"降低下行风险"、"构建分配"、"评估分配选项"、"对我的持仓进行压力测试"、"评估下行风险敞口"、"在权重限制下审查我的持仓"、"比较基准投资组合"、"模拟 CVaR 场景"、"筛选投资组合风险"、"在约束下优化持仓" 和 "找到一个低风险分配"。

不要将其用于通用金融摘要、价格预测、神经网络训练、车辆路径规划或非投资组合优化。

## 前提条件

- 带有已安装 `cufolio` 包的 Python 环境。
- 带有 cuOpt 和 cuML 安装的 NVIDIA GPU 运行时。
- 与主机匹配的 CUDA 额外选项，例如 `uv sync --extra cuda12` 或 `uv sync --extra cuda13`。
- `cvxpy` 暴露 `cp.CUOPT`。
- 首次运行时如果必须下载默认价格 CSV，则需要网络访问。

## 设置

此技能驱动已安装的 `cufolio` 包。一个准备好的环境可以来自 Brev 启动器或安装匹配的 CUDA 额外选项后的 `NVIDIA-AI-Blueprints/cuFOLIO`。

在打包的代理/评估沙盒中，`cufolio` 可通过 `PYTHONPATH` 提供，而不是作为单独发布的轮子。在声明缺失之前，使用 `python -c "import cufolio"` 验证本地包。不要 `pip install cufolio`，不要从头开始重新实现 cuFOLIO 工作流，也不要用通用的 pandas/scipy/cvxpy 投资组合代码替换包 API。

对于具体的实现细节，使用 `references/workflows/agent_recipes.md` 作为事实来源。它包含加载价格、准备回报、使用 cuOpt 求解、构建 25 点前沿、对等权重回测和调用再平衡器的精确工作形状。

默认数据集是 `data/stock_data/sp500.csv`。它被 git 忽略。在首次运行下载之前，告诉用户这将通过 cuFOLIO/yfinance 数据辅助程序获取公共市场数据，并要求他们确认：

```python
import cvxpy as cp
from cufolio.cvar_parameters import CvarParameters
from cufolio.utils import download_data

download_data("data/stock_data", datasets=["sp500"])
SOLVER_SETTINGS = {"solver": cp.CUOPT, "verbose": False, "solver_method": "PDLP"}
cvar_params = CvarParameters(
    w_min=0.0, w_max=1.0,
    c_min=0.0, c_max=0.0,
    risk_aversion=1.0, confidence=0.95,
)
```

## 说明

在执行之前，简要说明将应用的默认设置，然后使用这些指导方针：

1. 加载 `data/stock_data/sp500.csv`；如果缺失，请在使用 `cufolio.utils.download_data` 下载 `sp500` 之前询问。不要 glob、替换或编造价格数据。
2. 在求解之前验证用户 CSV：要求日期索引或日期列、数字股票代码列、至少 60 行（过滤日期后）以及至少一个请求的股票代码。如果用户提供开始/结束日期，请在计算回报之前切片价格 DataFrame 并报告保留的日期范围。在计算回报之前，在价格 DataFrame 上过滤股票代码。`regime_dict` 不接受股票代码字段。
3. 使用 `utils.calculate_returns(...)` 计算 LOG 回报。
4. 使用 `cvar_utils.generate_cvar_data(...)`、KDE 和 `KDESettings(device="GPU")` 生成场景。
5. 使用显式的 `w_min` 和 `w_max` 定义 `CvarParameters`。对于普通的 "构建最优投资组合" 请求，将 `c_min=0.0` 和 `c_max=0.0` 设置为结果完全投资，而不是 100% 现金。
6. 直接从该回报字典构建 `cvar_optimizer.CVaR(returns_dict, cvar_params)`；保持 cuFOLIO 辅助程序返回的股票代码、场景数组、均值和协方差形状。
7. 仅使用 NVIDIA cuOpt 求解。在求解之前，验证 `hasattr(cp, "CUOPT")` 和 `str(cp.CUOPT) in {str(s) for s in cp.installed_solvers()}`。将 `SOLVER_SETTINGS` 传递给每个单次求解或循环前沿求解。永远不要回退到 CLARABEL、SCS、ECOS 或其他 CPU 求解器。如果 cuOpt 缺失，请完成验证/设置并报告缺少 GPU/cuOpt 运行时，而不是编造 CPU 结果。
8. 对于自定义约束，将用户请求映射到 `CvarParameters`：权重上限映射到 `w_min`/`w_max`，风险偏好映射到 `risk_aversion`，置信度映射到 `confidence`，现金允许映射到 `c_max`，并且仅在包为工作流暴露显式的资产计数约束时映射基数。如果约束冲突（例如，最大权重太低，无法在请求的股票代码数量上投资），请解释冲突并要求放宽约束，而不是猜测。
9. 如果用户省略了回测基准，请使用相同股票代码的等权重投资组合。如果用户省略了约束，请保持默认表值并简要重申求解前的后果性假设。
10. 按分配、现金权重、预期回报、CVaR、求解器标签（`cuOpt GPU`）以及任何请求的前沿图、权重表、回测指标或再平衡计划排序交付权重。对于表格，请将股票代码作为列或行，包含小数权重和百分比；对于图表，请保留返回的 cuFOLIO 图表，而不是从头开始重新绘制。
11. 对于报告级答案，请包括请求的工作流实际运行的证据。对于有效前沿，请报告 `len(results_df)` 并使用请求的 `ra_num`（25，除非用户指定其他）。对于权重表，将 `results_df["weights"]` 扩展为股票代码列，并包括 `cash` 和 `risk_aversion`。对于回测，请包括优化和基准投资组合的 `mean portfolio return`、`sharpe`、`sortino` 和 `max drawdown`。对于再平衡，请包括 `results_dataframe`、`re_optimize_dates` 和 `cumulative_portfolio_value` 的尾部。

## 典型工作流骨架

从此形状开始积极的 cuFOLIO 任务，并仅调整请求的输出。在编写自定义代码之前，请先阅读 `references/workflows/agent_recipes.md` 以获取完整的可复制函数。

```python
import cvxpy as cp
import pandas as pd

from cufolio import backtest, cvar_optimizer, cvar_utils, rebalance, utils
from cufolio.cvar_parameters import CvarParameters
from cufolio.portfolio import Portfolio
from cufolio.settings import KDESettings, ReturnsComputeSettings, ScenarioGenerationSettings

if not hasattr(cp, "CUOPT") or str(cp.CUOPT) not in {str(s) for s in cp.installed_solvers()}:
    raise RuntimeError("cuOpt GPU 求解器是必需的；不要替换为 CPU 求解器。")

SOLVER_SETTINGS = {"solver": cp.CUOPT, "verbose": False, "solver_method": "PDLP"}

prices = utils.get_input_data("data/stock_data/sp500.csv")
returns_dict = utils.calculate_returns(
    prices,
    regime_dict=None,
    returns_compute_settings=ReturnsComputeSettings(return_type="LOG"),
)
returns_dict = cvar_utils.generate_cvar_data(
    returns_dict,
    ScenarioGenerationSettings(
        fit_type="kde",
        kde_settings=KDESettings(device="GPU"),
    ),
)
cvar_params = CvarParameters(
    w_min=0.0,
    w_max=1.0,
    c_min=0.0,
    c_max=0.0,
    risk_aversion=1.0,
    confidence=0.95,
)
optimizer = cvar_optimizer.CVaR(returns_dict, cvar_params)
result, optimal_portfolio = optimizer.solve_optimization_problem(
    solver_settings=SOLVER_SETTINGS,
    print_results=False,
)
```

对于有效前沿或权重表，调用：

```python
results_df, fig, ax = cvar_utils.create_efficient_frontier(
    returns_dict,
    cvar_params,
    SOLVER_SETTINGS,
    ra_num=25,
    show_plot=False,
    show_discretized_portfolios=False,
    benchmark_portfolios=False,
    print_portfolio_results=False,
)
weights_table = pd.DataFrame(results_df["weights"].tolist(), index=results_df.index)
```

对于基准回测，将求解后的分配包装在 `Portfolio(name="cuOpt Optimal", tickers=returns_dict["tickers"], weights=optimal_portfolio.weights, cash=optimal_portfolio.cash)` 中，创建一个等权重的 `Portfolio`，覆盖相同的 `returns_dict["tickers"]`，然后使用 `backtest.portfolio_backtester(..., test_method="historical").backtest_against_benchmarks(...)`。回测器返回 `(backtest_results, ax)`。

对于每月再平衡，首先将价格 DataFrame 写入 CSV 路径。使用 `rebalance.rebalance_portfolio(dataset_directory=<csv_path>, ...)` 并将 `re_optimize_criteria={"type": "drift_from_optimal", "threshold": 0, "norm": 1}`，然后调用 `re_optimize(transaction_cost_factor=..., plot_title="Monthly Rebalancing")`。再平衡器返回 `(results_dataframe, re_optimize_dates, cumulative_portfolio_value)`。

## 数据和默认值

| 设置 | 默认值 |
|---|---|
| 数据集 | `data/stock_data/sp500.csv` |
| 日期范围 | 完整可用范围 |
| 投资组合类型 | 长头寸 |
| 最大权重 | 未指定除非指定 |
| 风险厌恶 | `1.0` |
| 置信度 | `0.95` |
| 场景方法 | GPU 上的 KDE |
| 求解器 | cuOpt GPU with PDLP |
| 再平衡 | 未指定除非请求 |

默认的 S&P 500 文件是历史快照，可能省略当前成分。用户提供的 CSV 应该是日期索引的价格表，带有股票代码列，与 `utils.get_input_data` 兼容。如果请求的股票代码缺失，请删除它们，报告遗漏，并继续使用可用列，除非用户明确要求您获取其他数据。

## 关键 API

使用包 API 而不是重新实现投资组合数学或模拟循环。cuFOLIO 辅助程序返回扁平对象：`returns_dict` 具有诸如 `returns`、`mean`、`covariance` 和 `tickers` 等键；不要将其索引为 `returns_dict["regime_1"]`。`solve_optimization_problem(...)` 返回 `(result_row, portfolio)`，而不是嵌套结果字典。

- 回报：`utils.calculate_returns(input_dataset, regime_dict, returns_compute_settings)`。
- 制度过滤器：`regime_dict` 是 `None` 或 `{"name": "...", "range": ("YYYY-MM-DD", "YYYY-MM-DD")}`；它不是按制度名称键入的，也不包含股票代码。
- 场景：`cvar_utils.generate_cvar_data(returns_dict, scenario_generation_settings)`。
- 优化器：`cvar_optimizer.CVaR(returns_dict, cvar_params)`。
- 求解：`result_row, portfolio = cvar_problem.solve_optimization_problem(solver_settings=SOLVER_SETTINGS, print_results=False)`。
- 有效前沿：`cvar_utils.create_efficient_frontier(returns_dict, cvar_params, solver_settings=SOLVER_SETTINGS, ra_num=25)`。返回的 `results_df` 包括指标、`weights` 字典列和 `cash`。
- 投资组合：`Portfolio(name="", tickers=None, weights=None, cash=0.0, time_range=None)`；传递股票代码和与这些股票代码对齐的扁平数组状 `weights`。
- 回测：为优化分配和每个基准创建 `portfolio.Portfolio` 对象；对于等权重基准，使用权重为 `1 / len(tickers)` 和 `cash=0.0`，然后调用 `backtest.portfolio_backtester(test_portfolio, returns_dict, risk_free_rate=0.0, test_method="historical", benchmark_portfolios=[...]).backtest_against_benchmarks(...)`。
- 再平衡：`rebalance.rebalance_portfolio(...)` 要求 `dataset_directory` 是 CSV 路径，而不是 DataFrame。调用 `re_optimize(...)`；它返回 `(results_dataframe, re_optimize_dates, cumulative_portfolio_value)`。
- 设置模型：`ReturnsComputeSettings`、`ScenarioGenerationSettings`、`KDESettings`、`ApiSettings` 和 `CvarParameters`。

## 示例

- "从 S&P 500 构建最优投资组合"：加载价格，计算 LOG 回报，生成 GPU KDE 场景，设置长头寸完全投资的 `CvarParameters`，使用 cuOpt 求解，并报告多元化权重加上回报/CVaR。
- "绘制有效前沿"：调用 `create_efficient_frontier(...)`，返回 `results_df`，并按请求显示或保存图表。
- "按风险厌恶程度给出权重"：将 `results_df["weights"]` 扩展为每个资产的表格。
- "对等权重回测"：构建优化和等权重的 `Portfolio` 对象，然后使用 cuFOLIO 回测器并报告 Sharpe、Sortino 和最大回撤。
- "回测每月再平衡"：配置 `rebalance_portfolio` 使用上述漂移触发器并运行 `re_optimize(transaction_cost_factor=...)`。

## 限制

- 需要带有 cuOpt 和 cuML 的 NVIDIA GPU；CPU 求解器有意禁止。
- 仅 CPU 评估容器仍然可以验证路由、数据处理和报告行为，但它们无法生成有效的 cuOpt 求解。在这种情况下，明确报告缺少 GPU/cuOpt 运行时。
- 默认价格数据是历史快照，可能省略当前成分。
- 首次运行数据集下载取决于网络访问，除非用户提供 CSV。

## 故障排除

- 缺失默认 CSV 或 `FileNotFoundError`：解释 cuFOLIO 将使用 `download_data("data/stock_data", datasets=["sp500"])` 获取公共市场数据；仅在用户确认后运行它。
- `SolverError` 或缺失 `cp.CUOPT`：安装与主机匹配的 CUDA 额外选项并使用 `python -c "import cvxpy as cp; print(hasattr(cp, 'CUOPT'), cp.installed_solvers())"` 验证。
- `ImportError` 对于 `cuml` 或 GPU KDE 失败：使用 `python -c "import cuml"` 确认 cuML 存在并保持 `KDESettings(device="GPU")`。
- 普通优化返回全部现金：在 `CvarParameters` 中设置 `c_max=0.0`。
- 求解器报告不可行或无解：检查是否存在矛盾边界、股票代码太少以符合请求的上限/基数，或日期过滤后数据太少；报告使请求可行的最小约束更改。
- 请求的股票代码缺失于默认 CSV：报告它们并继续使用剩余请求的股票代码。
- 用户 CSV 失败验证：要求日期索引的价格表或第一列是日期、其余列是数字股票价格 CSV；提及至少 60 行过滤后的要求。
