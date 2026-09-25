# 符号方程发现

使用 LLM 指导的进化搜索从数据中发现可解释的科学方程。

## 输入

- `$0` — 数据集描述、变量名称和物理背景

## 参考文献

- LLM-SR 模式（提示、进化、采样）：`~/.claude/skills/symbolic-equation/references/llmsr-patterns.md`

## 工作流程（来自 LLM-SR）

### 第 1 步：定义问题规范
创建规范，包含：
1. **输入变量**：具有类型的物理量（例如，`x: np.ndarray`，`v: np.ndarray`）
2. **输出变量**：要预测的目标量
3. **评估函数**：适应度指标（通常为参数优化后的负均方误差）
4. **物理背景**：指导方程发现域知识

```python
# 示例规范
@equation.evolve
def equation(x: np.ndarray, v: np.ndarray, params: np.ndarray) -> np.ndarray:
    """描述阻尼非线性振荡器的加速度。"""
    return params[0] * x
```

### 第 2 步：初始化多岛屿缓冲区
- 创建 N 个岛屿（默认：10）以保持种群多样性
- 每个岛屿维护独立的方程集群
- 集群按性能特征对齐方程进行分组

### 第 3 步：进化搜索循环
重复直到收敛或达到最大样本数：
1. **选择岛屿**：随机选择岛屿
2. **构建提示**：从集群中采样顶级方程（按分数进行 softmax 加权）
3. **LLM 提出**：生成新方程作为改进版本
4. **评估**：在测试数据上执行，计算适应度分数
5. **注册**：如果有效，则添加到岛屿的集群中

### 第 4 步：提示构建
将先前方程作为版本化序列呈现：
```python
def equation_v0(x, v, params):
    """初始版本。"""
    return params[0] * x

def equation_v1(x, v, params):
    """equation_v0 的改进版本。"""
    return params[0] * x + params[1] * v

def equation_v2(x, v, params):
    """equation_v1 的改进版本。"""
    # LLM 完成此部分
```

### 第 5 步：岛屿重置（多样性维护）
定期（默认：每 4 小时）：
1. 按最佳分数对岛屿进行排序
2. 重置排名后 50% 的岛屿
3. 用一个幸存岛屿的最佳方程为每个重置的岛屿进行初始化
4. 重新启动集群采样温度

### 第 6 步：提取最佳方程
搜索完成后：
1. 从每个岛屿收集最佳方程
2. 按适应度分数进行排序
3. 如有可能进行简化（代数简化）
4. 带有物理解释进行报告

## 集群采样

温度调度 softmax 对集群分数：
```
temperature = T_init * (1 - (num_programs % period) / period)
probabilities = softmax(cluster_scores / temperature)
```
- 较高的温度 → 更多探索
- 较低的温度 → 更多利用最佳集群
- 在集群内：更短的程序更受青睐（奥卡姆剃刀原则）

## 规则

- 方程必须仅使用标准数学运算
- 通过 scipy BFGS 或 Adam 进行参数优化
- 适应度 = 负均方误差（越高越好）
- 方程评估具有超时保护
- 不允许递归方程
- 物理可解释性优先于纯拟合度

## 相关技能
- 上游：[数据分析](../data-analysis/)，[数学推理](../math-reasoning/)
- 下游：[论文写作部分](../paper-writing-section/)
- 另见：[算法设计](../algorithm-design/)
