---
name: dxf
description: 从 Python build123d 源代码生成、重新生成和验证 2D DXF 图纸。用于 DXF 文件、`.py` 绘图脚本、@dxf 模型、2D 截面轮廓、轮廓线、模板、垫片、面板、平面模式、激光/等离子/水切割布局，以及 CAD 几何的 2D 绘图导出。
---

# DXF生成与验证

来源：维护在 [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) 中。
使用已安装的本地技能文件作为运行时真实来源；仓库链接仅用于来源追踪和发布审核。

## 设置

此技能的命令是 `cadgen` 分发的薄入口点，该分发包含 Python 构建运行时和它执行的 JavaScript。安装一次：

```bash
python -m pip install -r requirements.txt
```

绘图是 build123d 几何图形，因此绘图构建加载 CAD 内核就像 STEP 构建一样（冷启动约 2.5 秒；热守护进程在重新运行时吸收它）。
`cadgen dxf snapshot` 完全不需要 Node：它使用 `ezdxf`（随 cadgen 提供）扁平化绘图，并在捆绑的无头浏览器中绘制它。

## 目的

从自然语言要求或 CAD 几何图形创建或修改 2D DXF 绘图，生成经过验证的绘图工件，并返回检查后的输出。DXF 绘图的来源是一个名为 `<name>.py` 的 Python 文件，该文件定义了一个无参数的 `@dxf` 模型函数。

**一个绘图就是一个模型。** 它具有与 `@step` 零件相同的包装器、记录、新鲜度门和构建作业；它的一个输出是 `.dxf` 文件；它没有几何树（没有任何东西链接到绘图）。每次运行都会写入兄弟 `<name>.dxf`（或装饰器命名的 `out=`）；未更改的源是无操作的；调用零件模型的绘图（在其主体内 `bracket()`）在零件的 GEOMETRY 更改时变得过时，在未更改时不变得过时；`cadgen store why <drawing>.py` 解释了该判断；`--force` 无论如何都会重新构建它。CAD 查看器和 `dxf snapshot` 直接读取 `.dxf` 文件本身，因此你交给切割服务的文件、查看器绘制的文件和快照渲染的文件是完全相同的。

## 合同

**一个 `@dxf` 函数不接受参数并返回 build123d 2D 几何图形。引擎写入 DXF。** 你永远不会构建文档、命名文件或放置实体——这与 `@step` 的分工相同。

```python
from cadgen import build123d as bd
from cadgen import dxf


HOLE_D = 4.5


@dxf
def gasket():
    with bd.BuildSketch() as cut:
        bd.Rectangle(60, 40)
        bd.Circle(HOLE_D / 2, mode=bd.Mode.SUBTRACT)
    return cut.sketch          # 原始形状 -> CUT 层


if __name__ == "__main__":
    gasket()
```

- **原始形状** → 一个 `CUT` 层。这是大多数绘图的全部合同。
- **`{layer: shape}`** → 命名层，当绘图确实有多个 CAM 操作（`CUT` / `ENGRAVE` / `SCORE`）时。一个子代为所有标记的复合体意味着相同的事情。
- **没有参数。** 尺寸是模块常量（`HOLE_D = 4.5`）或从绘图派生的零件导入的常量；不同的绘图是不同的文件。
- **文本** 是 `bd.Text(...)` 在标记层上雕刻的 OUTLINES，永远不会是 DXF 的 `TEXT` 实体：切割和标记工具链消耗几何图形，CAM 内部字体渲染不可靠。
- **几何图形必须位于 XY 平面。** 从实体中获取的面位于该实体的高度；将其重新定位（`flatten.flatten_face(face)`，或 `bd.Location((0, 0, -z)) * face`）。引擎拒绝非平面几何图形，而不是静默地写入其 XY 影子。
- **输出字节是几何图形的函数。** 层按名称排序，实体按几何内容排序，因此未更改的绘图在任何机器上冷启动或热启动时都会重建为相同的文件。

## 三个 DXF 工作流程

在创建新绘图时，从 `references/generator-templates.md` 复制适用于相应工作流程的完整模板。

1. **从头开始绘制**（垫圈、面板、模板、没有 3D 模型的切割布局）：一个构建草图并返回它们的 `<name>.py`。
2. **生成的 STEP 零件的平面模式**：一个与模型它派生自的绘图脚本，它有自己的茎（每个文件一个模型——`bracket_drawing.py` 在 `bracket.py` 旁边）。导入模型并调用它，就像装配组合子一样：导入永远不会构建，并且在绘图的构建内部调用返回零件的几何图形（如果它过时，则首先构建零件）。

   ```python
   from cadgen import dxf, flatten
   from bracket import bracket        # 子代：通过其结果跟踪

   KERF = 0.15


   @dxf
   def bracket_drawing():
       return flatten.flat_pattern(bracket(), coordinate=3.0, kerf=KERF)


   if __name__ == "__main__":
       bracket_drawing()
   ```

   绘图的记录固定了零件的树，因此更改其几何图形的零件编辑使绘图过时，而不会更改的（注释、重构、颜色）使其保持当前。从零件导入的常量（`from bracket import THICKNESS`）以相同的方式按值跟踪。

3. **导入的 STEP 的平面模式**（没有 Python 源的 `.step`/`.stp`）：使用 `cadgen.read_step` 读取它，而不是 `build123d.import_step`。它将文件的哈希值记录为构建输入，因此替换供应商 STEP 使绘图仅因自身而过时，无需 `--force`；通过 build123d 读取它，绘图保持“当前”，即使它下面的文件已更改。

   ```python
   from pathlib import Path

   from cadgen import dxf, flatten, read_step

   _HERE = Path(__file__).resolve().parent

   KERF = 0.15


   @dxf
   def panel_flat():
       panel = read_step(_HERE / "imported" / "vendor_panel.step")   # 记录输入
       return flatten.flat_pattern(panel, coordinate=3.0, kerf=KERF)


   if __name__ == "__main__":
       panel_flat()
   ```

   **永远不要读取此项目生成的 STEP。** 读取 `@step` 模型写入的 `.step` 不是循环，它是一个输入在每次模型运行时更改的绘图：新鲜度门永远无法说“当前”，每次构建都是完整的重建，平面模式取决于磁盘上上次运行留下的内容。将源 STEP 保存在绘图旁边的 `imported/` 目录中，像任何其他输入一样提交——输入路径和输出路径是不同的文件是整个规则。对于此项目生成的 STEP，使用工作流程 2：导入模型脚本并调用它，它通过结果跟踪，永远不会触及工件。

每个模型一个文件是建议的，绘图有自己的脚本：一个文件可以声明多个模型——两个 `@dxf` 绘图，或一个 `@dxf` 旁边有一个 `@step`——每个都是其自己的记录、输出和作业（唯一的模型写入 `<file>.dxf`；共享文件的模型写入 `<function>.dxf>`），但它们共享文件的闭包，因此编辑一个会重建所有。绘图组合模型，而不是相反：从 `@step` 主体调用 `@dxf` 函数只是其 2D 几何图形，并链接不到任何东西。查看器目录仅包含工件：脚本永远不会列出；运行写入的 `.dxf` 是查看器渲染的条目。

## 使用此技能的情况

当用户要求 DXF 文件、2D 绘图、轮廓、轮廓、模板、垫圈、面板、平面模式或激光、等离子、水刀或 CNC 路由的切割布局时，使用此技能。

使用 `$cad` 表示 DXF 派生自的 3D 零件或装配。使用 `$sendcutsend` 表示 SendCutSend 特定的上传预检。

## 默认值

除非用户指定否则使用这些默认值：

- 单位：毫米。引擎设置它们；绘图永远不会声明单位。
- 几何图形位于 XY 平面上的 1:1 比例。
- 切割轮廓封闭。开放轮廓属于弯曲/雕刻/参考层——生成验证强制执行这一点（见验证）。
- 对于 CAD 支持的零件，使用 `cadgen.flatten` 从实际拓扑中派生轮廓，而不是重新绘制：`planar_faces` 选择，`flatten_face` 精确地将面平铺到 XY，`union_faces` 融合，`flat_pattern` 在一个调用中完成所有。只有在没有可靠的 3D 拓扑时才使用手绘参数化轮廓。
- Kerf/工具半径补偿是 `flatten.offset_profile(shape, amount)` 或 `flat_pattern(..., kerf=...)`；永远不会手动偏移坐标。
- **曲线保持曲线。** 并集和偏移是精确的 OCC 操作，因此圆角角落导出为 `ARC`，孔导出为 `CIRCLE`，包括 kerf。导出为数百个短 `LINE` 的轮廓意味着某些东西回退到采样路径——调查而不是接受它。
- 层携带意图：将切割几何图形和弯曲/折叠线放在不同的层上，并在弯曲层名称中包含“bend”，以便下游工具将它们分类为弯曲而不是切割。
- DXF 层是绘图结构，而不是 STEP 零件/装配结构。

## 工具

```bash
python <drawing>.py [flags]                    # 其 __main__ 调用 @dxf 模型，写入 .dxf
cadgen dxf snapshot <drawing.dxf> <file.png>   # 渲染它
cadgen store why <drawing>.py                  # 绘图为何过时或当前
```

**运行脚本（其 `__main__` 调用）是唯一的入口。** 没有 `cadgen dxf build`：`.dxf` 没有命令必须实现的派生状态——文件本身就是产品，CAD 查看器和 `dxf snapshot` 直接从其自己的字节绘制它。绘图的门使重建变得廉价：未更改的源，其 `.dxf` 仍然验证，其零件子代未更改是无操作的，`--force` 无论如何都会重新构建。字节是绘图几何图形的函数，因此冷启动和热守护进程工作写入相同的文件。构建永远不会等待或取消另一个构建；调用零件的绘图像任何父代一样并行构建它们。

导入的 `.dxf` 无需任何东西——直接交给快照或查看器。

使用活动项目的 Python 解释器；将 `python` 视为解释器占位符，并使用 `--help` 获取完整界面。目标路径从命令的当前工作目录解析；从拥有工件的工件目录运行，使用相对于当前工作目录的目标路径。将绘图脚本保存在其派生几何图形的同一目录中，命名为 `<name>.py`。

标志（模型脚本运行自身；没有生成 CLI）：

- `--force` — 即使记录的输出当前也要重新生成。
- `--verbose`, `--json`。

运行回答与 STEP 模型的回答完全相同——`built DXF/plate_drawing.dxf` 或 `current DXF/plate_drawing.dxf`——在 stderr 上显示进度；`--json` 使结果为一条 JSON 行（`outcome`，`document` 和 `tree`，对于绘图 `tree` 为 null）和进度为每个转换一条 JSON 行。

一个脚本，一个绘图：运行每个您想要构建的脚本。不要在 `@dxf` 函数的返回值中放置输出路径；装饰器上的 `out=` 是绘图命名其目的地的唯一地方（相对于脚本）。

`cadgen dxf snapshot` 将绘图平面化，到 PNG 静止——与 CAD 查看器显示的相同图片，来自相同的扁平化，通过相同的绘图代码：

```bash
cadgen dxf snapshot path/to/imported.dxf review.png
cadgen dxf snapshot path/to/drawing.dxf review.png --appearance dark
```

它只接受 `.dxf` 文档——模型脚本按名称拒绝（运行 `python <drawing>.py`，然后快照它写入的绘图）。整个绘图适配到图像并直接绘制，使用文件声明的笔；没有自己笔的实体（ACI 7）使用外观的前景在其背景上。命令使用 `ezdxf` 扁平化绘图，并通过共享快照 CLI (`cadgen.snapshot_cli`) 和每个渲染技能使用的相同无头浏览器运行时渲染它。

OUT — 第二个位置参数 — 按给定方式写入，相对于当前工作目录解析的相对路径。目标在渲染开始前被删除，完成的图像原子写入，因此：在迭代时重用一个名称（每个读取都是您刚刚运行的渲染），当您确实需要比较两个时命名迭代。无效请求组合在接触 OUT 之前失败；请求接受后，首先清除 OUT，以便后续失败留下缺失文件而不是过时的图像。目录（`tmp/` 作为 OUT）是无所谓的案例，并在其中生成带时间戳的名称，打印在 `saved snapshot:` 行上。

语法：`cadgen dxf snapshot TARGET [OUT] [flags]`。标志：`--appearance light|dark`，`--size-profile`，`--width`/`--height`，`--job`，`--debug`，`--json`。这就是全部表面：绘图不是场景，因此没有需要摆位的相机，没有需要配置的显示设置，没有渲染模式，没有需要列出零件，没有需要切割的截面，没有需要标记的视图——`--camera`，`--display`，`--mode` 和 `--view-labels` 都不是此命令的标志。一个携带任何它们的 `--job` 文件（或 `scale`，输出 `label`/`viewLabel`，或 `output.padding`/`viewLabels`/`tightFrame`）在渲染之前按名称拒绝；作业的 `output.renderScale` 和 `output.transparent` 仍然适用。

没有 CLI 检查现有的 `.dxf`。对于实体/层检查，直接使用 `ezdxf` 读取它（它随 build123d 提供），并且 `validate_dxf_file` 用于绘图检查；在 CAD 查看器中直观地审查几何图形：

```python
import ezdxf

doc = ezdxf.readfile("path/to/source.dxf")
msp = doc.modelspace()
cut = msp.query('*[layer=="CUT"]')
holes = msp.query('CIRCLE[layer=="CUT"]')
```

仅报告实际运行的检查。

## 交接

创建或修改DXF图纸后，当安装了该技能时，你必须始终将明确的`.dxf`文件路径交给`$cad-viewer`，并在最终回复中包含其在线查看器链接。如果`$cad-viewer`不可用或启动失败，请报告该情况，并依赖`ezdxf`检查，而不是默默忽略交接。

最终回复应包含生成的文件、返回的查看器链接、实际运行的验证以及假设。
