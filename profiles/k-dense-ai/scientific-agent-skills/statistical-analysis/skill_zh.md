# 统计分析

## 概述

进行假设检验（t检验、方差分析、卡方检验）、回归、相关和贝叶斯分析，并进行系统性的假设检查、效应量和APA风格的报告。目标是进行一项审稿人无法挑出毛病的分析：正确的检验、经过验证的假设、诚实的效应量和完整的报告。

## 何时使用此技能

使用此技能时：
- 进行统计假设检验（t检验、方差分析、卡方检验、非参数检验）
- 执行回归或相关分析
- 运行贝叶斯统计分析
- 检查统计假设和诊断
- 计算效应量和进行功效分析
- 以APA格式报告统计结果
- 分析实验或观察数据进行研究

---

## 安装

使用**uv**安装此技能中使用的库。在生产环境中固定版本；未固定安装对于探索性工作是可以的。

```bash
# 核心频率统计栈（Python 3.10+；推荐使用3.12+以获取最新的SciPy/ArviZ）
uv pip install "pingouin>=0.6" "scipy>=1.11" "statsmodels>=0.14.6" pandas matplotlib seaborn

# 贝叶斯建模（PyMC 5 + ArviZ）
uv pip install "pymc>=5.0" "arviz>=1.0"
```

**兼容性说明（与pingouin 0.6.1、statsmodels 0.14.6、arviz 1.2、2026版本进行验证）：**

- **Pingouin 0.6.0** 将输出列重命名为删除特殊字符：`p_val`、`cohen_d`、`CI95`、`p_unc`（在0.5.x版本中为 `p-val`、`cohen-d`、`CI95%`、`p-unc`）。以下示例使用当前名称；如果被卡在0.5.x版本，请使用带连字符的格式。
- **statsmodels + SciPy**：使用 `statsmodels>=0.14.6` 与 `scipy>=1.11` 以避免在SciPy 1.16+上出现 `_lazywhere` 导入错误。
- **ArviZ 1.x**：`az.summary()` 现在默认为 **89% 区间**（`eti89` 列），宽度参数是 `ci_prob`（不是 `hdi_prob`）。要报告传统的 95% 置信区间，请传递 `az.summary(trace, ci_prob=0.95)`。
- **单边贝叶斯因子已从Pingouin中移除**：`pg.ttest(..., alternative='greater')` 静默地删除了 `BF10` 列，并且 `pg.bayesfactor_ttest` 在单边替代方案上引发错误。对于单边贝叶斯检验，请直接使用PyMC（计算方向性假设的后验概率）或JASP/R的BayesFactor。

对于特定模型的API（OLS、GLM、ARIMA），请参阅 **statsmodels** 技能。对于PyMC工作流，请参阅 **pymc** 技能。

---

## 分析工作流

每个合理的分析都遵循相同的过程。跳过步骤是分析被撤回的原因，因此请按顺序完成它们，并在每个步骤说明你做了什么。

1. **在接触数据之前确定问题。** 陈述假设、结果和预测变量，以及设计（独立与配对、组数）。现在确定计划的检验——在查看结果后选择检验是p值操纵，即使是无意的。
2. **检查数据。** 每组：n、均值、标准差、中位数、缺失值。在任何测试之前绘制原始数据（直方图或箱线图）。组大小不等、缺失性、地板/天花板效应和异常值都会改变适当的测试——将它们暴露给用户，而不是默默地绕过它们。
3. **使用以下快速参考选择测试，或使用 `references/test_selection_guide.md` 进行超出基本设计的测试（计数、时间至事件、可靠性、因子）**。
4. **使用 `scripts/assumption_checks.py` 检查假设**。如果假设失败，则切换到补救测试（下表），并报告计划和更改。
5. **运行测试，并始终与测试一起计算效应量——p值表示效应存在；效应量表示是否有人应该关心。**
6. **使用以下APA模板报告，包括描述性统计、确切统计量、具有置信区间的效应量以及执行的假设检查。**

如果用户只需要一个步骤（例如，“我需要多少参与者？”），请直接跳到该部分——但仍然确认计算所依赖的设计假设。

---

## 测试选择指南

### 快速参考：选择正确的测试

使用 `references/test_selection_guide.md` 获取全面指导（计数、生存、可靠性、因子设计）。快速参考：

**比较两组：**
- 独立、连续、正态 → 独立t检验
- 独立、连续、非正态 → 曼-惠特尼U检验
- 配对、连续、正态 → 配对t检验
- 配对、连续、非正态 → 威尔科克森符号秩检验
- 二元结果 → 卡方检验或费希尔精确检验

**比较三组及以上：**
- 独立、连续、正态 → 单因素方差分析
- 独立、连续、非正态 → 克鲁斯卡尔-沃利斯检验
- 配对、连续、正态 → 重复测量方差分析
- 配对、连续、非正态 → 弗里德曼检验

**关系：**
- 两个连续变量 → 皮尔逊（正态）或斯皮尔曼相关（非正态）
- 连续结果与预测变量 → 线性回归
- 二元结果与预测变量 → 逻辑回归

**贝叶斯替代方案：**
所有测试都有贝叶斯版本，提供关于假设的直接概率陈述、量化证据的贝叶斯因子，以及支持零假设的能力。请参阅 `references/bayesian_statistics.md`。

---

## 假设检查

**在解释测试结果之前始终检查假设，并报告检查结果——审稿人会寻找它们。**

使用捆绑的 `scripts/assumption_checks.py` 模块。从技能目录（`skills/statistical-analysis/`）运行Python，或添加 `scripts/` 到 `sys.path`：

```python
from assumption_checks import comprehensive_assumption_check

# 异常值 + 正态性（每组）+ 方差齐性，带绘图
results = comprehensive_assumption_check(
    data=df,
    value_col='score',
    group_col='group',  # 可选：用于组比较
    alpha=0.05
)
```

对于有针对性的检查，导入单个函数：

```python
from assumption_checks import (
    check_normality,                # Shapiro-Wilk + Q-Q图 + 直方图
    check_normality_per_group,
    check_homogeneity_of_variance,  # Levene's test + 箱线图
    check_linearity,                # 散点图 + 残差图（简单回归）
    check_regression_diagnostics,   # 完整OLS诊断（见回归部分）
    detect_outliers                 # IQR或z分数方法
)

result = check_normality(data=df['score'], name='测试分数', alpha=0.05, plot=True)
print(result['interpretation'])
print(result['recommendation'])
```

### 假设被违反时该怎么做

**正态性违反：**
- 轻微违反 + 每组n > 30 → 继续进行参数检验（稳健）
- 中等违反 → 使用非参数替代方案
- 严重违反 → 变换数据或使用非参数检验

**方差齐性违反：**
- 对于t检验 → 使用Welch's t检验（`pg.ttest` 在 `correction='auto'` 时自动应用）
- 对于方差分析 → 使用Welch's方差分析（`pg.welch_anova`）或Brown-Forsythe
- 对于回归 → 使用稳健标准误差或加权最小二乘法

**线性违反（回归）：**
- 添加多项式项、变换变量，或使用非线性模型/GAM

随着n的增长，正式测试会变得过于敏感：对于n ≥ 100，请比Shapiro-Wilk p值更重视Q-Q图。请参阅 `references/assumptions_and_diagnostics.md` 获取全面指导。

---

## 运行统计测试

主要库：
- **pingouin**：用户友好的测试默认返回效应量——优先使用它进行标准测试
- **scipy.stats**：核心统计测试
- **statsmodels**：回归、诊断、功效分析
- **pymc** + **arviz**：贝叶斯建模和诊断

### 完整报告的t检验

```python
import pingouin as pg

# correction='auto' 在方差不等时应用Welch's校正
result = pg.ttest(group_a, group_b, correction='auto')

# Pingouin >= 0.6 列名
t_stat = result['T'].values[0]
df = result['dof'].values[0]
p_value = result['p_val'].values[0]
cohens_d = result['cohen_d'].values[0]
ci_lower, ci_upper = result['CI95'].values[0]  # 均值差异的CI

print(f"t({df:.0f}) = {t_stat:.2f}, p = {p_value:.3f}, d = {cohens_d:.2f}")
```

### 方差分析与事后检验

```python
import pingouin as pg

aov = pg.anova(dv='score', between='group', data=df, detailed=True)
print(aov)

# 效应量：偏η²
eta_p2 = aov['np2'].values[0]

# 如果显著，进行事后检验（Tukey HSD控制家族错误）
if aov['p_unc'].values[0] < 0.05:
    posthoc = pg.pairwise_tukey(dv='score', between='group', data=df)
    print(posthoc)  # 包括每对Hedges' g
```

### 带诊断的线性回归

```python
import statsmodels.api as sm
from assumption_checks import check_regression_diagnostics

X = sm.add_constant(X_predictors)  # 添加截距
model = sm.OLS(y, X).fit()
print(model.summary())

# 4面板残差图 + Shapiro-Wilk, Breusch-Pagan, Durbin-Watson, VIF
diag = check_regression_diagnostics(model)
print(diag['interpretation'])
print(diag['vif'])

# 如果标记了异方差性，请报告稳健标准误差
robust = model.get_robustcov_results('HC3')
```

### 贝叶斯t检验

```python
import pymc as pm
import arviz as az
import numpy as np

with pm.Model() as model:
    # 先验
    mu1 = pm.Normal('mu_group1', mu=0, sigma=10)
    mu2 = pm.Normal('mu_group2', mu=0, sigma=10)
    sigma = pm.HalfNormal('sigma', sigma=10)

    # 似然
    y1 = pm.Normal('y1', mu=mu1, sigma=sigma, observed=group_a)
    y2 = pm.Normal('y2', mu=mu2, sigma=sigma, observed=group_b)

    # 派生量
    diff = pm.Deterministic('difference', mu1 - mu2)

    trace = pm.sample(2000, tune=1000)

# ArviZ 1.x 默认为 89% 区间；显式请求 95% 以便报告
print(az.summary(trace, var_names=['difference'], ci_prob=0.95))

# 直接概率陈述（这就是单边问题变成的内容）
prob_greater = np.mean(trace.posterior['difference'].values > 0)
print(f"P(mu1 > mu2 | data) = {prob_greater:.3f}")

# ArviZ 1.x 移除了 az.plot_posterior；使用 plot_dist（在0.x版本中，plot_posterior 仍然有效）
az.plot_dist(trace, var_names=['difference'], ci_prob=0.95)
```

根据数据调整先验（例如，`sigma=10` 适用于SD接近10的结果；使用观测到的SD作为指南），并在报告中说明先验。

---

## 效应量

**效应量量化幅度；p值仅指示存在。** 每个测试报告一个。请参阅 `references/effect_sizes_and_power.md` 获取完整指南。

### 快速参考：常见效应量

| 测试 | 效应量 | 小 | 中 | 大 |
|------|-------|----|----|----|
| t检验 | Cohen's d | 0.20 | 0.50 | 0.80 |
| 方差分析 | η²_p | 0.01 | 0.06 | 0.14 |
| 相关 | r | 0.10 | 0.30 | 0.50 |
| 回归 | R² | 0.02 | 0.13 | 0.26 |
| 卡方检验 | Cramér's V | 0.07 | 0.21 | 0.35 |

基准是惯例，不是法律——一个“小”效应可能非常重要（药物副作用），而一个“大”效应可能微不足道。根据背景进行解释。

### 计算效应量

Pingouin 在其测试中返回效应量（`cohen_d` 来自 `pg.ttest`，`np2` 来自 `pg.anova`，`hedges` 来自 `pg.pairwise_tukey`；`r` 来自 `pg.corr` 已经是效应量）。

### 效应量的置信区间

报告效应量的置信区间以显示其精度。使用 `pg.compute_esci`（注意：`pg.compute_effsize_from_t` 仅返回点估计——它**不**返回CI）：

```python
import pingouin as pg

d = pg.compute_effsize(group_a, group_b, eftype='cohen')
ci_lower, ci_upper = pg.compute_esci(stat=d, nx=len(group_a), ny=len(group_b),
                                     eftype='cohen', confidence=0.95)
print(f"d = {d:.2f}, 95% CI [{ci_lower:.2f}, {ci_upper:.2f}]")
```

---

## 功效分析

### 预实验功效分析（研究计划）

在数据收集之前确定所需样本量：

```python
from statsmodels.stats.power import tt_ind_solve_power, FTestAnovaPower

# t检验：需要多少组样本才能检测到d = 0.5？
n_required = tt_ind_solve_power(
    effect_size=0.5,
    alpha=0.05,
    power=0.80,
    ratio=1.0,
    alternative='two-sided'
)
print(f"每组所需n：{n_required:.0f}")

# 单因素方差分析：需要多少n才能检测到Cohen's f = 0.25？
# 注意：参数是k_groups；效应量是Cohen's f（f = sqrt(eta2/(1-eta2)））；solve_power返回总样本量，不是每组n。
import math
anova_power = FTestAnovaPower()
n_total = anova_power.solve_power(
    effect_size=0.25,
    k_groups=3,
    alpha=0.05,
    power=0.80
)
print(f"所需总N：{math.ceil(n_total)} ({math.ceil(n_total / 3)} 每组)")
```

### 敏感性分析（研究后）

确定研究能检测到什么效应量：

```python
# 每组n=50，80%功效下能检测到什么效应？
detectable_d = tt_ind_solve_power(
    effect_size=None,  # 求解这个
    nobs1=50,
    alpha=0.05,
    power=0.80,
    ratio=1.0,
    alternative='two-sided'
)
print(f"研究可以检测到d >= {detectable_d:.2f}")
```

**注意**：后验“观察到的功效”（根据观察到的效应计算功效）是循环的和误导性的——它是p值的确定性函数。如果已经进行了研究，并且有人询问功效，请运行敏感性分析而不是。

请参阅 `references/effect_sizes_and_power.md` 获取详细指导。

---

## 报告结果

遵循 `references/reporting_standards.md` 获取APA风格。每个报告需要：

1. **描述性统计**：所有组/变量的M、SD、n
2. **测试统计量**：测试名称、统计量、df、确切p值（`p = .034`，而不是 `p < .05`；仅在低于 .001 时使用 `p < .001`）
3. **效应量**：带置信区间
4. **假设检查**：运行的测试、结果和采取的行动
5. **所有计划的分析**：包括非显著性结果——省略它们是选择性报告

### 示例报告模板

#### 独立t检验

```
组A（n = 48，M = 75.2，SD = 8.5）得分显著高于
组B（n = 52，M = 68.3，SD = 9.2），t(98) = 3.82，p < .001，d = 0.77，
95% CI [0.36, 1.18]，双尾。假设的正态性（Shapiro-Wilk：
组A W = 0.97，p = .18；组B W = 0.96，p = .12）和方差齐性（Levene's F(1, 98) = 1.23，p = .27）得到满足。
```

#### 单因素方差分析

```
单因素方差分析显示处理条件对测试分数存在显著主效应，
F(2, 147) = 8.45，p < .001，η²_p = .10。事后比较使用Tukey's HSD表明，
条件A（M = 78.2，SD = 7.3）得分显著高于条件B（M = 71.5，
SD = 8.1，p = .002，d = 0.87）和条件C（M = 70.1，SD = 7.9，
p < .001，d = 1.07）。条件B和C没有显著差异
(p = .52，d = 0.18)。
```

#### 多元回归

```
进行了多元线性回归，以预测考试分数来自学习时间、先验GPA和出勤率。
整体模型显著，F(3, 146) = 45.2，p < .001，R² = .48，调整后的R² = .47。学习时间
(B = 1.80，SE = 0.31，β = .35，t = 5.78，p < .001，95% CI [1.18, 2.42])
和先验GPA（B = 8.52，SE = 1.95，β = .28，t = 4.37，p < .001，
95% CI [4.66, 12.38]）是显著的预测因子，而出勤率不是
(B = 0.15，SE = 0.12，β = .08，t = 1.25，p = .21，95% CI [-0.09, 0.39])。
多重共线性不是问题（所有VIF < 1.5）。
```

#### 贝叶斯分析

```
进行了贝叶斯独立样本t检验，使用弱先验（组均值Normal(0, 10)）。
后验分布表明组A得分高于组B
(M_diff = 6.8，95% credible interval [3.2, 10.4])，99.8%后验概率表明组A的均值超过组B的均值。
收敛诊断令人满意（所有R-hat < 1.01，ESS > 1000）。
```

如果使用了非参数检验，请报告中位数而不是均值、U/W/H统计量，以及基于秩的效应量（例如，`pg.mwu` 返回的 `RBC`）。
