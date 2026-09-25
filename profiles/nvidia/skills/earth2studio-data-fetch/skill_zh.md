# Earth2Studio 数据获取技能

## 目的

引导用户通过 Earth2Studio 数据源 API 下载天气/气候数据。通过检查词汇表识别兼容的数据源，验证变量支持情况，并生成输出 xarray DataArray 的可工作获取脚本。

## 前置条件

- 已安装 Earth2Studio (`uv pip install earth2studio` 或等效方式)
- 可访问远程数据存储的网络 (GCS、S3、CDS API 等)
- 对于基于 CDS 的数据源：已配置有效的 CDS API 密钥 (`~/.cdsapirc`)
- Python 3.10+

## 说明

您正在帮助用户使用 Earth2Studio 的数据源 API 下载特定的天气/气候数据。您的工作是识别哪些数据源可以提供所需的变量，通过词汇表系统验证兼容性，并生成可工作的获取脚本。

### 核心原则：实时文档和词汇表是权威依据

数据源 API、可用变量和词汇表在版本之间会发生变化。在推荐数据源或编写获取脚本之前：

1. **获取相关数据源文档页面** 以确认 API 签名和构造函数参数。
2. **检查词汇表** 以验证用户请求的变量是否由该数据源支持。

实时文档参考（仅获取用户请求所需的内容）：

- **分析数据源：**
  <https://nvidia.github.io/earth2studio/modules/datasources_analysis.html>
- **预报数据源：**
  <https://nvidia.github.io/earth2studio/modules/datasources_forecast.html>
- **DataFrame 数据源：**
  <https://nvidia.github.io/earth2studio/modules/datasources_dataframe.html>
- **词汇表基础：**
  <https://github.com/NVIDIA/earth2studio/blob/main/earth2studio/lexicon/base.py>
- **按源分词汇表：**
  <https://github.com/NVIDIA/earth2studio/tree/main/earth2studio/lexicon>

### 交互协议

#### 第 1 步：理解用户请求

从用户的说法中提取信息（如有必要，可提出后续问题，最多 3 个问题）：

- **变量** — 他们想要什么？使用 Earth2Studio 变量名称（例如 `t2m`、`u500`、`z850`、`tp`、`msl`）。如果用户使用普通语言（“500 hPa 位势高度”），通过检查实时 `base.py` 的 E2STUDIO_VOCAB 将其映射到 E2Studio 名称。
- **时间** — 什么日期/时间范围？单个时间戳、时间范围还是多个离散时间？
- **数据类型** — 分析/再分析（历史状态）或预报（基于提前期）？
- **提前期**（仅预报）— 提前多远？哪个初始化时间？
- **区域** — 全球或区域（例如 HRRR 的北美洲）？
- **输出格式** — xarray DataArray（默认）、保存到文件（NetCDF/Zarr）？

#### 第 2 步：识别候选数据源

根据请求类型，缩小候选范围：

**分析/再分析**（特定时间的历史状态）：

- 使用分析数据源页面识别选项
- 常见选择：GFS（运行中，最近）、HRRR（北美洲，每小时）、IFS/IFS_ENS（ECMWF）、ARCO/CDS/WB2ERA5/NCAR_ERA5（ERA5 再分析）、GOES/MRMS/JPSS（观测数据）

**预报**（基于初始化时间的预测，带提前期）：

- 使用预报数据源页面识别选项
- 常见选择：GFS_FX、GEFS_FX、HRRR_FX、IFS_FX、IFS_ENS_FX、AIFS_FX、CFS_FX

需要突出的关键差异：

- **时间覆盖范围** — 运行中数据源（GFS、HRRR）的历史有限；再分析（通过 ARCO/CDS/WB2 的 ERA5）可追溯数十年
- **空间分辨率** — HRRR 仅限北美 3km；GFS 全球 0.25°；WB2ERA5_32x64 全球 5.625°
- **更新频率** — 有些是实时更新，有些有数天延迟

#### 第 3 步：通过词汇表验证变量支持

这是关键。每个数据源都有一个词汇表文件，定义它可以提供的 E2Studio 变量。

验证方法：

1. 从 `https://github.com/NVIDIA/earth2studio/blob/main/earth2studio/lexicon/<source>.py`（例如 `gfs.py`、`hrrr.py`、`cds.py`、`arco.py`、`wb2.py`）获取源的词汇表文件
2. 检查用户请求的变量是否作为键出现在源的 `VOCAB` 字典中
3. 如果一个变量不在某个源的词汇表中，该源无法提供它 — 尝试另一个

词汇表 VOCAB 将 E2Studio 变量名称映射到源特定标识符。如果变量键存在于 VOCAB 中，该源支持它。

清晰地呈现结果：*"GFS 支持 `t2m`、`u500`、`z850`。HRRR 也支持这些但仅限于北美洲。ARCO（ERA5）支持这三个变量，数据可追溯至 1959 年。"

#### 第 4 步：与用户确认数据源选择

呈现可行的选项及其权衡：

| 数据源 | 变量 | 覆盖范围 | 分辨率 | 时间范围 |
|--------|-----------|----------|------------|------------|
| ... | ... | ... | ... | ... |

让用户选择。如果有明显的选择，推荐它并请求确认。

#### 第 5 步：生成获取脚本

编写一个使用选定数据源获取请求数据的 Python 脚本。脚本结构取决于它是分析源还是预报源。

**分析源模式：**

```python
import datetime
from earth2studio.data import <SourceClass>

# 初始化数据源
ds = <SourceClass>()

# 获取数据
# 分析源使用：ds(time, variable) -> xr.DataArray
time = [datetime.datetime(YYYY, M, D, H)]  # 或时间数组
variable = ["var1", "var2"]  # E2Studio 变量名称

data = ds(time, variable)
```

**预报源模式：**

```python
import datetime
from earth2studio.data import <SourceClass>

# 初始化数据源
ds = <SourceClass>()

# 预报源使用：ds(time, lead_time, variable) -> xr.DataArray
time = [datetime.datetime(YYYY, M, D, H)]  # 初始化时间
lead_time = [datetime.timedelta(hours=H)]   # 或提前期数组
variable = ["var1", "var2"]

data = ds(time, lead_time, variable)
```

在编写脚本之前，始终获取特定数据源的 API 文档页面以确认确切的构造函数参数和调用签名 — 它们可能不同（有些需要认证令牌、缓存路径、特定参数）。

在脚本中包含：

- 适当的导入
- 清晰的注释解释每一步
- 如何检查结果 (`print(data)`、`data.shape`、`data.coords`)
- 可选：如果用户请求，保存到文件

#### 第 6 步：提供后续步骤

交付脚本后，提及：

- 如何在不重写整个脚本的情况下更改变量/时间
- 如果他们可能想将此输入模型，引导他们使用 discover 技能
- 缓存行为（通过 `EARTH2STUDIO_CACHE` 首次获取后本地缓存数据）

### 责任范围和超出范围

**负责：** 为用户的变量/时间请求识别数据源、通过词汇表验证变量支持、生成数据获取脚本、解释分析源与预报源的区别。

**不负责：** 安装（earth2studio-install）、模型选择（earth2studio-discover）、推理管道、自定义数据源创建（指向扩展示例）、文档描述之外的认证设置。

## 示例

典型调用：

> "我需要 ERA5 的 500 hPa 位势高度和 2m 温度，时间范围为 2020 年 1 月 1 日 00Z。"

该技能将：

1. 将普通语言映射到 `z500`、`t2m`
2. 检查 ARCO/CDS/WB2ERA5 的词汇表以验证支持
3. 推荐 ARCO（免费，无需 API 密钥）或 CDS（官方，需要密钥）
4. 使用选定源生成获取脚本

## 限制

- **需要网络** — 所有数据源从远程存储（GCS、S3、CDS API）获取
- **无法加载本地文件** — 对于本地 NetCDF/Zarr，直接使用 `DataArrayFile`/`DataSetFile`
- **每脚本仅限一种数据源类型** — 不能在单次调用中混合分析源和预报源
- **变量可用性不同** — 并非所有源都提供所有变量；始终通过词汇表验证
- **速率限制** — CDS API 有基于队列的限流；GCS/S3 源通常更快

## 故障排除

| 错误 | 原因 | 解决方案 |
|-------|-------|----------|
| `KeyError: '<var>'` | 不在词汇表中 | 检查词汇表；尝试另一个源 |
| `FileNotFoundError` / 404 | 时间不可用 | 验证时间覆盖范围 |
| `CDS API timeout` | 队列拥塞 | 重试或使用 ARCO 获取 ERA5 |
| `ModuleNotFoundError` | 未安装 | `uv pip install earth2studio` |
| 空数据数组 | 时间/变量不匹配 | 检查日期时间和变量名称 |
