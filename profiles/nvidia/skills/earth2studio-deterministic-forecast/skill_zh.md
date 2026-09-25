# Earth2Studio 确定性预报技巧

指导用户使用 `earth2studio.run.deterministic` 构建（单成员）天气预报推理脚本

## 前置条件

- 安装了支持 CUDA 的 GPU 的 Earth2Studio
- Python 3.10+，需要网络访问模型权重和数据

## 在线文档参考

在推荐组件前，获取相关文档以验证当前 API：

| 组件 | URL |
|------|-----|
| 预报模型 | <https://nvidia.github.io/earth2studio/modules/models_px.html> |
| 数据源（分析） | <https://nvidia.github.io/earth2studio/modules/datasources_analysis.html> |
| 数据源（预报） | <https://nvidia.github.io/earth2studio/modules/datasources_forecast.html> |
| IO 后端 | <https://nvidia.github.io/earth2studio/modules/io.html> |
| `run.deterministic` | <https://github.com/NVIDIA/earth2studio/blob/main/earth2studio/run.py> |

## 工作流程

### 1. 收集需求（跳过已提供的部分）

- 预报时效（小时/天/周）
- 关注变量（t2m、风、位势高度等）
- 区域（全球或特定如 CONUS）
- 可用的 GPU/VRAM

### 2. 选择模型

获取预报模型页面。按时效、区域、VRAM 筛选。记录模型的：
- 输入变量 (`input_coords["variable"]`)
- 时间步长 (`output_coords["lead_time"]`)

### 3. 选择数据源

数据源必须提供所有模型输入变量。通过 `earth2studio/lexicon/<source>.py` 处的词汇表验证。常见组合：全球模型 → GFS/ARCO/IFS；区域 → HRRR。

### 4. 选择 IO 后端

默认：`ZarrBackend`。使用 `NetCDF4Backend` 用于遗留工具，`XarrayBackend` 用于内存/小规模运行。

### 5. 计算 nsteps

`nsteps = forecast_hours / model_step_hours`

示例：5 天预报，6 小时步长 → `nsteps = 120 / 6 = 20`

### 6. 确定：output_coords 过滤

- **过滤变量** (`output_coords`) 当用户请求特定变量（如 "t2m 和风"）- 减少输出大小
- **保存所有变量**（省略 `output_coords`）当用户说 "所有变量" 或未指定 - 保留完整模型输出

### 7. 生成脚本

```python
from collections import OrderedDict
import numpy as np
import torch
from earth2studio.models.px import <ModelClass>
from earth2studio.data import <DataSourceClass>
from earth2studio.io import <IOBackendClass>
from earth2studio.run import deterministic

model = <ModelClass>.load_model(<ModelClass>.load_default_package())
data = <DataSourceClass>()
io = <IOBackendClass>("<output_path>")

# 仅当用户请求特定变量时包含 output_coords
output_coords = OrderedDict({"variable": np.array(["t2m", "u10m"])})

io = deterministic(
    time=["YYYY-MM-DDTHH:MM:SS"],
    nsteps=<N>,
    prognostic=model,
    data=data,
    io=io,
    output_coords=output_coords,  # 如果保存所有变量则省略
    device=torch.device("cuda"),
)
```

### 8. 手动循环替代方案

当用户明确要求手动实现（不使用 `earth2studio.run.deterministic`）时，按顺序遵循此清单：

1. **fetch_data** - 获取初始条件：`x, coords = fetch_data(data, time, model.input_coords, device)`
2. **Setup total_coords** - 构建时间和引导时间维度的坐标数组
3. **io.add_array** - 在循环前使用 total_coords 初始化 IO 后端
4. **create_iterator** - 创建预报迭代器：`model_iter = model.create_iterator(x, coords)`
5. **Loop through nsteps** - `for step, (x, coords) in enumerate(model_iter): if step >= nsteps: break`
6. **map_coords** - 如需过滤输出变量：`x_out, coords_out = map_coords(x, coords, output_coords)`
7. **split_coords** - 准备 IO 写入：`x_out, coords_out = split_coords(x_out, coords_out)`
8. **io.write** - 将每一步写入后端

### 9. 解释后续步骤

- 如何更改预报时间或运行多个初始化
- 如何读取输出 (`xr.open_zarr(...)`)
- 指向用于后处理的诊断工作流

## 责任范围

**负责：** 模型选择、数据源兼容性、IO 后端选择、nsteps 计算、生成 `earth2studio.run.deterministic` 脚本。

**不负责：** 集成工作流、诊断、纯数据获取、安装、模型训练。

## 故障排除

参见 `references/troubleshooting.md` 获取常见错误和解决方案。

## 提醒事项

- **始终在推荐模型或数据源前获取在线文档** - API 在版本之间会变更
- **验证词汇表兼容性** - 模型输入变量必须存在于数据源的 VOCAB 中
- **使用 `load_default_package()`** - 这是加载模型权重的标准模式
- **时间格式为 ISO 8601** - 使用 `"YYYY-MM-DDTHH:MM:SS"` 格式作为 `time` 参数
- **风速需要两个分量** - 如果用户要求 "风速"，请包含 `u10m` 和 `v10m`
- **nsteps 是整数除法** - `nsteps = total_hours // model_step_hours`
- **ZarrBackend 是默认值** - 仅在用户有特定要求时才建议替代方案
- **需要 GPU** - 所有预报模型需要 CUDA；不支持 CPU 推理
