# dicom_series_to_volume

## 目的
- 用于将一个CT DICOM系列文件夹转换为带有仿射信息的HU NIfTI体积。不适用于多帧DICOM或临床使用。
- 请严格按照文档使用包装器；不要用手工编写的实现替换上游入口点。
- 配置文件I/O：输入是`dicom_dir`；输出是`nifti_volume`和`result_json`。

## 使用说明
- 修改参数、副作用或验证门之前，请先阅读`skill_manifest.yaml`。
- 通过下方文档中所述的命令运行`scripts/series_to_volume.py`；将输出保持在调用者提供的运行目录下。
- 如果主机代理暴露了`run_script`，使用`run_script("scripts/series_to_volume.py", args=[...])`；否则运行下方显示的Bash/Python命令。
- 在将运行视为证据之前，请检查发出的JSON以及配对的`dicom_volume_quality_v1`验证器。

## 可用脚本
| 脚本 | 目的 | 参数 |
|---|---|---|
| `scripts/series_to_volume.py` | 由`skill_manifest.yaml`声明的入口点。 | `PATH_TO_DICOM_DIR [--output OUT.nii.gz]` |

## 前置条件
- 运行时要求：`runtime.side_effects.pip_packages`中列出的Python包。
- 需要 NiBabel 5.4或更新版本，以便在重新定向时保持极端倾斜轴的一致标签。
- 除非下方现有部分另有说明，否则从仓库根目录运行命令。

## 限制
- 仅支持单系列；在预检时拒绝多系列输入。
- 不支持多帧DICOM（每文件NumberOfFrames > 1）。
- 不支持压缩传输语法（JPEG / JPEG2000 / RLE）。
- 没有体素重新定向。仿射信息从DICOM头信息中导出，并以NIfTI/RAS坐标表示；预期下游门（例如`expected_axcodes`）在此体积输入到分割模型之前会断言方向。
- 不适用于临床部署、自主诊断、监管提交、生产推理（应使用经过验证的转换器，如dcm2niix）。

## 故障排除
| 错误 | 原因 | 解决方法 |
|---|---|---|
| 缺失依赖或导入错误 | 从`skill_manifest.yaml`的运行时包漂移。 | 安装配置文件中声明的包或使用文档中所述的设置命令。 |
| 空或模式无效的输出 | 输入路径错误、不支持的模态或上游失败。 | 使用已知固定件重新运行并检查包装器JSON和stderr。 |
| 验证门失败 | 输出违反了声明的工程不变量。 | 保留失败的证据包，并使用门消息修复输入或包装器代码。 |

读取一个DICOM系列，按`ImagePositionPatient`排序切片，应用
`RescaleSlope`和`RescaleIntercept`，从方向和间距标签构建仿射信息，并写入一个`.nii.gz`文件和JSON摘要。

```bash
python scripts/series_to_volume.py PATH_TO_DICOM_DIR --output PATH_TO_OUT.nii.gz
```

对于与配对验证器一起的受信任运行：

```bash
python -m eval_engine.run_trusted skills/dicom-series-to-volume \
  --fixture PATH_TO_DICOM_DIR \
  --out runs/dicom_series_to_volume_trusted
```

关键输出字段：`n_slices`、`series_instance_uid`、`output.path`、
`output.shape`、`output.spacing`、`output.axcodes`、`output.affine`、
`hu_range`和`runtime.conversion_seconds`。

范围限制：仅限单系列CT；不支持多帧DICOM、压缩传输语法处理、RT结构集、自动重新定向或临床使用。
