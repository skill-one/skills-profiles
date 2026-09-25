# BigFrames (BigQuery DataFrame) 基础知识
BigFrames 是一个 Python 库，它允许您通过使用熟悉的 Python API 来利用 BigQuery 的数据处理能力。

## DataFrame API 最佳实践

* **保持在云端**: 通过 BigFrames 方法执行数据清理、转换和分析，以利用 BigQuery 的可扩展性，而不是下载数据。
* **优先使用部分排序模式**: 在导入 BigFrames 后立即启用部分排序模式。这通过放宽行顺序约束显著加快数据处理速度。

    ```python
    import bigframes.pandas as bpd
    bpd.options.bigquery.ordering_mode = 'partial'
    ```
* **使用 `peek()` 进行数据预览**: 使用 `peek(n)` 而不是 `head(n)` 来预览数据。`peek(n)` 随机采样 `n` 行，并且速度显著更快。`head(n)` 按严格顺序返回行，并且在部分排序模式下失败，除非 DataFrame 已被显式排序。
* **避免本地化数据**: 像 `to_pandas()` 这样的方法会将所有数据下载到客户端内存，绕过 BigQuery 的分布式计算，并可能导致内存不足 (OOM) 错误。除非：
  * 数据集足够小，可以安全地放入内存中。
  * 错误消息明确要求本地化数据。
* **优先使用 DataFrame API 而不是 SQL 查询**: 如果 DataFrame/Series 方法可以实现相同的结果，则不要通过 `read_gbq()` 编写原始 SQL 查询，因为这会破坏 Pandas 抽象并阻止惰性查询执行。
* **访问器优于 UDFs/Lambdas**:
    * 使用内置访问器（例如，`df.col.str.*`，`df.col.dt.*`）而不是远程用户定义函数 (UDF)。UDF 需要额外的资源和时间来部署。
    * 不要在 `Series.map()` 或 `DataFrame.apply()` 中使用 lambda。这些方法不接受没有 `udf` 或 `remote_function` 装饰器的函数。
    ```python
    # 避免：
    df["upper"] = df["name"].map(lambda x: x.upper())

    # 优先：
    df["upper"] = df["name"].str.upper()
    ```
* **模式验证**: 不要假设中间输出的模式。使用 `.dtypes` 主动验证模式，并使用 `display()` 和 `.peek()` 检查样本记录。
* **可视化**: 尽可能直接从 BigFrames DataFrame/Series 绘图。BigFrames 与 Matplotlib 和 Seaborn 兼容。如果直接绘图失败，请使用 `.plot` 访问器。如果数据集太大而无法绘图，请在调用 `.to_pandas()` 绘图之前对数据进行聚合或采样。

## 机器学习
* **使用 `bigframes.bigquery.ml` 包**: 不要使用 Scikit-learn 或其他机器学习库与 BigQuery DataFrames。标准的 Scikit-learn 模型需要将数据带入本地客户端内存，而 `bigframes.bigquery.ml` 将训练直接委托给 BigQuery 的可扩展机器学习引擎。从 `bigframes.bigquery.ml` 导入函数。

### 参考目录
* [线性回归](references/linear_regression.md): 训练线性回归模型以预测数值。
* [逻辑回归](references/logistic_regression.md): 训练逻辑回归模型以预测布尔值。

## BigFrames ML (遗留)

BigFrames ML 包 (`bigframes.ml`) 是一个遗留包，它模仿 scikit-learn API，但不再推荐用于新项目。只有在用户明确请求 BigFrames ML 时才使用此包。

* **遗留导入**: 当请求遗留 BigFrames ML 时，从 `bigframes.ml` 而不是 `bigframes.bigquery.ml` 导入工具和类。
* **预测返回 DataFrame**: 与 Scikit-learn 不同，BigFrames 的 `predict()` 方法始终返回一个包含预测和特征的 **DataFrame**，而不是一个预测系列的单一序列。
* **没有 `random_state`**: 在实例化 BigFrames ML 模型时，不要传递 `random_state` 参数，因为此参数在 BigFrames ML 包中不受支持。
* **自动缩放**: 除非明确请求，否则不要使用 `OneHotEncoder` 或 `StandardScaler`，因为缩放是自动处理的。
* **超参数调优**: 编写自定义循环进行超参数调优，因为 BigFrames 缺少 `GridSearchCV` 或 `RandomizedSearchCV`。
* **ARIMA Plus** (预测):
    * 从 `bigframes.ml.forecasting` 导入。
    * 在训练之前按时间顺序排序数据并在时间点附近分割。
    * 确保预测范围小于或等于训练范围。
* **PCA**: BigFrames 的 PCA 类缺少 `transform()` 方法。使用 `predict()` 代替。
* **模型持久化**: 要持久化模型，请使用 `model.to_gbq()`。要加载持久化的模型，请使用 `bpd.read_gbq_model()`。
