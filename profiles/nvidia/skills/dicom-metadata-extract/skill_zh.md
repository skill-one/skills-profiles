# DICOM元数据提取

## 目的
- 用于从单个DICOM文件中提取选定的元数据，并标记标准标签中PHI的存在。不用于匿名化或临床用途。
- 请严格按照文档使用包装器；不要用手工编写的实现替换上游入口点。
- 配置文件I/O：输入为`dicom_path`；输出为`metadata_json`。

## 说明
- 修改参数、副作用或验证门之前，请先阅读`skill_manifest.yaml`。
- 通过以下文档中所示的命令运行`scripts/extract_metadata.py`；将输出保持在调用者提供的运行目录下。
- 如果主机代理暴露了`run_script`，请使用`run_script("scripts/extract_metadata.py", args=[...])`；否则运行以下Bash/Python命令。
- 检查发出的JSON，并在将运行视为已审查的证据之前，对证据包运行`medagent.verifiers.dicom_metadata_quality_v1`。

## 可用脚本
| 脚本 | 目的 | 参数 |
|---|---|---|
| `scripts/extract_metadata.py` | 由`skill_manifest.yaml`声明的入口点。 | `PATH_TO_DICOM [--output OUT.json]` |

## 前置条件
- 运行时要求：`runtime.side_effects.pip_packages`中列出的Python包。
- 除非下方现有部分另有说明，否则从仓库根目录运行命令。

## 限制
- 仅支持PS3.15风格的标签子集，不是完整的Basic Application Confidentiality Profile实现。
- 不检查私有标签
- 未检测烧入像素PHI
- 多帧处理有限
- 不适用于临床部署、监管去识别化、自主诊断、面向患者使用。

## 故障排除
| 错误 | 原因 | 解决方法 |
|---|---|---|
| 缺少依赖项或导入错误 | 从`skill_manifest.yaml`的运行时包漂移。 | 安装配置文件中声明的包或使用文档中的设置命令。 |
| 空或模式无效的输出 | 输入路径错误、不支持的模态或上游失败。 | 使用已知固定件重新运行，并检查包装器JSON和stderr。 |
| 验证门失败 | 输出违反了声明的工程不变量。 | 保留失败的证据包，并使用门消息来修复输入或包装器代码。 |

使用pydicom读取一个DICOM文件，并在stdout上输出JSON。

```bash
python scripts/extract_metadata.py PATH_TO_DICOM
python scripts/extract_metadata.py PATH_TO_DICOM --output result.json
```

输出包括`transfer_syntax`、`modality`、分组研究/系列/图像元数据、`phi_present`和`phi_tags_found`。

将其用作Medical AI Skills技能的最小端到端示例。不要用它进行匿名化、私有标签审查、像素PHI检测或临床解释。

对于二次证据审查，生成一个可信运行：

```bash
python -m eval_engine.run_trusted skills/dicom-metadata-extract \
  --fixture skills/dicom-metadata-extract/fixtures/sample_ct.dcm \
  --out runs/dicom_metadata_trusted
```
