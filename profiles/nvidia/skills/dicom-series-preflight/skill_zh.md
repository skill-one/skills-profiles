# DICOM系列预检

## 目的
- 用于在转换或推理前对单个DICOM系列文件夹进行仅头文件的预检。不用于去识别化或临床审核。
- 请严格按照文档使用包装器；不要用手工编写的实现替换上游入口点。
- 资产输入输出：输入为`dicom_dir`；输出为`preflight_json`。

## 使用说明
- 修改参数、副作用或验证门之前，请先阅读`skill_manifest.yaml`。
- 通过下方文档中所述命令运行`scripts/preflight_series.py`；将输出保持在调用者提供的运行目录下。
- 如果主机代理暴露了`run_script`，使用`run_script("scripts/preflight_series.py", args=[...])`；否则运行下方显示的Bash/Python命令。
- 在将运行结果视为证据之前，请检查发出的JSON和配套的验证指导。

## 可用脚本
| 脚本 | 目的 | 参数 |
|---|---|---|
| `scripts/preflight_series.py` | 由`skill_manifest.yaml`声明的核心入口点。 | `PATH_TO_DICOM_DIR` |

## 前置条件
- 运行时要求：`runtime.side.effects.pip_packages`中列出的Python包。
- 需要Nibabel 5.4或更高版本，以便在重新定向时保持极端倾斜轴的标签一致。
- 除非下方现有部分另有说明，否则请从仓库根目录运行命令。

## 限制
- 仅头文件；不解码像素数据或检测烧入的PHI。
- 假设LPS导出的CT轴码为L,P,S的规范方向门。
- 压缩传输语法和多帧实例会发出警告，但不会解码。
- 单目录扫描；不会协调同一树中的多个研究。
- 不用于临床部署、监管去识别化、自主诊断、未经审核转换器的生产摄入。

## 故障排除
| 错误 | 原因 | 解决方法 |
|---|---|---|
| 缺失依赖或导入错误 | 从`skill_manifest.yaml`的运行时包漂移。 | 安装声明在清单中的包或使用文档中的设置命令。 |
| 空或模式无效的输出 | 输入路径错误、不支持的模态或上游失败。 | 使用已知固件重新运行，并检查包装器JSON和stderr。 |
| 验证门失败 | 输出违反了声明的工程不变量。 | 保留失败的证据包，并使用门消息来修复输入或包装器代码。 |

扫描DICOM **目录**（每个文件夹一个系列），不解码像素。
发出包含清单、方向轴码、PHI标志、发现和`preflight.verdict`（`pass`、`warn`或`fail`）的JSON。

```bash
python scripts/preflight_series.py PATH_TO_DICOM_DIR
```

与`verifiers/dicom_preflight_quality_v1`配对以获得可信的预检包：

```bash
make run-trusted SKILL=dicom_series_preflight \
  FIXTURE=skills/dicom-series-preflight/fixtures/clean_no_phi \
  OUT=runs/dicom_preflight_demo
```

旗舰工作流：

```bash
make run-workflow \
  WORKFLOW=examples/workflows/dicom_preflight_gate.yaml \
  WORKFLOW_INPUT=skills/dicom-series-preflight/fixtures/clean_no_phi \
  WORKFLOW_OUT=runs/dicom_preflight_gate
```

不用于去识别化、私有标签审核或临床审核。
