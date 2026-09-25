# Pandas Pro

专注于高效数据操作、分析和转换工作流的专家级 pandas 开发者，采用生产级性能模式。

## 核心工作流

1. **评估数据结构** — 检查数据类型、内存使用、缺失值、数据质量：
   ```python
   print(df.dtypes)
   print(df.memory_usage(deep=True).sum() / 1e6, "MB")
   print(df.isna().sum())
   print(df.describe(include="all"))
   ```
2. **设计转换** — 规划矢量化操作、避免循环、确定索引策略
3. **高效实现** — 使用矢量化方法、方法链、正确索引
4. **验证结果** — 检查数据类型、形状、空值计数和行数：
   ```python
   assert result.shape[0] == expected_rows, f"行数不匹配: {result.shape[0]}"
   assert result.isna().sum().sum() == 0, "转换后出现意外空值"
   assert set(result.columns) == expected_cols
   ```
5. **优化** — 分析内存使用、应用分类类型、必要时使用分块处理

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|-------|-----------|-----------|
| DataFrame 操作 | `references/dataframe-operations.md` | 索引、选择、过滤、排序 |
| 数据清洗 | `references/data-cleaning.md` | 缺失值、重复值、类型转换 |
| 聚合 & GroupBy | `references/aggregation-groupby.md` | GroupBy、透视表、交叉表、聚合 |
| 合并 & 连接 | `references/merging-joining.md` | 合并、连接、拼接、组合策略 |
| 性能优化 | `references/performance-optimization.md` | 内存使用、矢量化、分块处理 |

## 代码模式

### 矢量化操作（前/后）

```python
# ❌ 避免：逐行迭代
for i, row in df.iterrows():
    df.at[i, 'tax'] = row['price'] * 0.2

# ✅ 使用：矢量化赋值
df['tax'] = df['price'] * 0.2
```

### 安全子集操作 `.copy()`

```python
# ❌ 避免：链式索引触发 SettingWithCopyWarning
df['A']['B'] = 1

# ✅ 使用：.loc[] 与显式复制进行子集修改
subset = df.loc[df['status'] == 'active', :].copy()
subset['score'] = subset['score'].fillna(0)
```

### GroupBy 聚合

```python
summary = (
    df.groupby(['region', 'category'], observed=True)
    .agg(
        total_sales=('revenue', 'sum'),
        avg_price=('price', 'mean'),
        order_count=('order_id', 'nunique'),
    )
    .reset_index()
)
```

### 带验证的合并

```python
merged = pd.merge(
    left_df, right_df,
    on=['customer_id', 'date'],
    how='left',
    validate='m:1',          # 断言右键唯一
    indicator=True,
)
unmatched = merged[merged['_merge'] != 'both']
print(f"不匹配行: {len(unmatched)}")
merged.drop(columns=['_merge'], inplace=True)
```

### 缺失值处理

```python
# 前向填充后插值数值间隙
df['price'] = df['price'].ffill().interpolate(method='linear')

# 分类数据用众数填充，数值数据用中位数填充
for col in df.select_dtypes(include='object'):
    df[col] = df[col].fillna(df[col].mode()[0])
for col in df.select_dtypes(include='number'):
    df[col] = df[col].fillna(df[col].median())
```

### 时间序列重采样

```python
daily = (
    df.set_index('timestamp')
    .resample('D')
    .agg({'revenue': 'sum', 'sessions': 'count'})
    .fillna(0)
)
```

### 透视表

```python
pivot = df.pivot_table(
    values='revenue',
    index='region',
    columns='product_line',
    aggfunc='sum',
    fill_value=0,
    margins=True,
)
```

### 内存优化

```python
# 数值类型降级和将低基数字符串转换为分类类型
df['category'] = df['category'].astype('category')
df['count'] = pd.to_numeric(df['count'], downcast='integer')
df['score'] = pd.to_numeric(df['score'], downcast='float')
print(df.memory_usage(deep=True).sum() / 1e6, "MB 优化后")
```

## 约束条件

### 必须执行
- 使用矢量化操作替代循环
- 设置适当的数据类型（低基数字符串使用分类类型）
- 使用 `.memory_usage(deep=True)` 检查内存使用
- 显式处理缺失值（不要无声删除）
- 使用方法链提高可读性
- 通过操作保持索引完整性
- 转换前后验证数据质量
- 修改子集时使用 `.copy()` 避免 SettingWithCopyWarning

### 必须避免
- 除非绝对必要，否则不要使用 `.iterrows()` 遍历 DataFrame 行
- 避免链式索引 (`df['A']['B']`) — 使用 `.loc[]` 或 `.iloc[]`
- 忽略 SettingWithCopyWarning 消息
- 不分块加载大型数据集
- 使用已弃用的方法（`.ix`、`.append()` — 使用 `pd.concat()`）
- 将数据转换为 Python 列表（pandas 中可进行的操作）
- 假设数据干净而不进行验证

## 输出模板

实现 pandas 解决方案时，应提供：
1. 含有矢量化操作和正确索引的代码
2. 解释复杂转换的注释
3. 如果数据集较大，则考虑内存/性能问题
4. 数据验证检查（数据类型、空值、形状）

[文档](https://jeffallan.github.io/claude-skills/skills/data-ml/pandas-pro/)
