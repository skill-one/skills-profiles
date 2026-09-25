# CAD建模与检查

来源：维护在 [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad)。
使用当前界面的已安装本地技能文件。

## 开始任务

仅读取请求所需的参考。

| 任务 | 首次操作 | 参考 |
| --- | --- | --- |
| **创建或编辑零件或装配体** | 查找现有的Python模型，或在下方创建装饰模型；编辑源代码并运行 `python <model>.py`。 | [模型合同](references/step-generation.md)，[形状构造](references/build123d-modeling.md)；[定位](references/positioning.md) 用于装配体 |
| **组织CAD项目** | 遵循其现有布局；对于新的多模型项目使用 `src/`，格式化输出文件夹，并创建模型目录。 | [项目布局](references/project-layout.md)，[最小启动器](references/project-template.md) |
| **导出STL、3MF或GLB** | 为维护的输出添加网格装饰器，或运行格式的 `build INPUT.step OUT` 命令进行一次性导出。 | [网格导出](references/supported-exports.md) |
| **从提示中解析参考** | 识别其保存的STEP/STP文档，使用 `read_scene` 打开它，并按如下所示调用 `scene.resolve(ref)`。 | [参考语法和检查](references/inspection-and-validation.md#reference-syntax) |
| **测量或检查几何体** | 使用原生build123d几何体编写Python检查，在有用的情况下使用 `cadgen.geometry`。 | [检查和验证](references/inspection-and-validation.md) |
| **从图像或绘图建模** | 提取指定尺寸并记录有意义的假设。 | [解释请求](references/cad-brief.md) |
| **检查外观或运动** | 快照保存的文档；使用声明的运动学或动画进行姿势和剪辑。 | [快照检查](references/snapshot-review.md)，[运动学](references/kinematics.md) |
| **诊断故障** | 读取错误并检查相关的模型、几何体或命令合同。 | [修复循环](references/repair-loop.md)，[版本迁移](references/migrations.md) |

对于2D DXF绘图使用 `$dxf`；此技能拥有任何由绘图投影的3D零件。
使用相应的机器人描述技能处理URDF、SRDF或SDF。

## 设置和路径

使用活动项目解释器安装此技能的 `requirements.txt`。
渲染还需要Chromium：

```bash
python -m pip install -r /path/to/installed/cad/requirements.txt
python -m playwright install chromium
```

在示例中将 `python` 视为活动解释器。`cadgen doctor <skill-dir>`
检查技能的包固定和CAD内核；用于安装或OCP加载错误。`python -m cadgen.cli`
是 `cadgen` 的路径无关等效项。使用相关子命令的 `--help` 获取附加标志。

从CAD项目根目录运行项目命令。CLI输入/输出路径和 `read_scene`/`read_step`
路径是相对于工作目录的；装饰器 `out=` 路径是**相对于模型脚本**的。当模型必须从任何目录运行时，将文件输入锚定在 `__file__`。

## 创建或编辑模型

模型是一个普通的Python脚本，包含一个无参数的装饰函数返回build123d形状。每个入口点使用一个模型，脚本及其声明的输出共享一个文件名前缀。例如，`src/bracket.py`：

```python
from cadgen import build123d as bd
from cadgen import step

WIDTH = 40.0


@step(out="../STEP/bracket.step")
def bracket():
    body = bd.Box(WIDTH, 20, 6)
    body.label = "bracket"
    return body


if __name__ == "__main__":
    bracket()
```

```bash
python src/bracket.py
```

- 当模型存在时，编辑模型源代码，然后运行它以重新生成其输出。
  文档导出和快照命令使用保存的文件，永远不会运行源代码。
- 保持有意义的尺寸显式。使用毫米和XY/+Z，除非任务或项目指定其他约定；
  选择一个有用的功能基准。对于物理零件，优先选择封闭的正体积实体，同时尊重
  对表面或构造几何体的请求。
- 将参数化几何体放在普通的工厂函数中；装饰模型选择一个配置。保持模块体廉价：
  在模型或其帮助程序中创建几何体并读取CAD输入。使用上面懒加载的 `bd` 导入；
  当注解提到 `bd` 类型时使用延迟注解。
- 在装配体模型中调用子模型。使用 `.moved()` 或 `Location * shape`
  将其结果放置在保留共享几何体的位置。使用有意义的出现标签和源定义的放置。
  重新运行父装配体以包含更改的子模型。
- 使用 `cadgen.read_step` 读取供应商STEP输入；它将文件记录为构建输入。
  使用 `cadgen.declare_input` 声明其他数据输入。永远不要将模型的输出作为其输入读取。
  几何体不得依赖于未跟踪的时间、随机值、环境变量或工作目录。
- 当需要命名可购买的零件时，在创建占位符之前搜索 `$step-parts`。记录未成功的搜索和任何占位符假设。

对于不熟悉的尺寸或接口，记录建模和验证所需的假设。当缺少信息实质性影响请求的结果时，请求缺失信息。检查和导出请求不需要建模简报。

## 网格导出

在模型上堆叠 `@stl`、`@threemf` 或 `@glb` 用于应在每次运行时维护的输出。模型只能声明网格；STEP是可选的。
从现有的生成或导入的STEP进行一次性导出：

```bash
cadgen stl build STEP/bracket.step STL/bracket.stl
cadgen 3mf build STEP/bracket.step 3MF/bracket.3mf
cadgen glb build STEP/bracket.step GLB/bracket.glb
```

省略 OUT 将使用请求的扩展名写入一个兄弟文件。它不会发现声明的模型变体。有关装饰器示例、网格公差和动画GLB，请参阅 [网格导出](references/supported-exports.md)。

## 提示参考和检查

如 `assembly.step#o1.2.f7` 这样的参考标识特定保存文档中的几何体。使用提示的文件上下文选择该文档：

```python
from cadgen import read_scene

scene = read_scene("STEP/assembly.step")
selection = scene.resolve("assembly.step#o1.2.f7")
face = selection.shape()  # 拥有的原生几何体，在文档世界坐标中
print(selection.ref, face.area)
```

对于裸 `#o1.2.f7`，使用识别的目标文件。对于模型脚本前缀，找到其声明的STEP输出并在那里解析 `#...` 部分。不要在歧义文件或标签之间猜测。数字引用属于该保存的版本；重建后重新打开和选择。参考检查涵盖标签别名、枚举、测量和小型可重用操作。

没有检查CLI。将探索性检查放在项目的忽略 `tmp/`（或系统 `/tmp/`）；将可重用检查保留在 `checks/` 或其现有的测试目录中。将它们保持在模型源和原始输出文件夹之外。

## 验证和移交

从请求的尺寸、间隙和拓扑中选择检查。对于STEP输出，使用 `read_scene` 或 `read_step`
检查保存的工件。对于仅网格模型，检查模型返回的原生几何体并审查网格输出；
不要仅为了满足工作流而添加STEP。报告单位、阈值、选择几何体和未测试的要求。失败的计算不是通过。

在创建或明显更改几何体后，生成并审查至少一个结果的STEP或网格的快照。选择附加视图以展示正在审查的功能；请参阅 [快照策略和选项](references/snapshot-review.md)。

```bash
cadgen step snapshot STEP/bracket.step tmp/review.png
cadgen stl snapshot STL/bracket.stl tmp/mesh.png
```

在源代码中修复失败并重新运行受影响的检查。使用几何体和图像进行CAD比较；路径目标的git状态是账本，不是几何证据。`cadgen store why <model>.py`
解释意外的重建；`python <model>.py --force` 强制一个模型，`cadgen daemon status`
显示构建进度。更多诊断信息在 [模型合同](references/step-generation.md)。

对于创建或修改的STEP/STP、STL、3MF和GLB文件，当安装 `$cad-viewer` 时，将其显式路径传递给 `$cad-viewer` 并包括其返回的实时链接。
如果不可用或启动失败，报告该情况并使用几何体检查和快照。在最终响应中包括输出文件、审查的PNG、实际运行的检查以及材料假设或限制。使用快照参考中的案例解释任何快照跳过或失败。
