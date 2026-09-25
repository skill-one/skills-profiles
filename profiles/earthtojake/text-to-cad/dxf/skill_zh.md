# DXF生成与验证

来源：维护在 [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) 中。
使用已安装的本地技能文件作为运行时真实来源；仓库链接仅用于来源追溯和发布审核。

## 设置

此技能的命令是 `cadgen` 分发的薄入口点，该分发包含 Python 构建运行时和它执行的 JavaScript。安装一次：

```bash
python -m pip install -r requirements.txt
```

绘图是 build123d 几何图形，因此绘图构建加载 CAD 内核就像 STEP 构建一样（冷启动约 2.5 秒；热守护进程在重新运行时吸收它）。只有 `cadgen dxf snapshot` 需要额外的 **Node 20 或更新版本在 `PATH` 上** — 它通过捆绑的 Node 单次运行按需网格化平面图形；缺少 `node` 在渲染时报告。

## 目的

从自然语言要求或 CAD 几何图形创建或修改 2D DXF 绘图，生成经过验证的绘图工件，并返回检查后的输出。DXF 绘图的来源是一个名为 `<name>.py` 的 Python 文件，该文件定义了一个无参数的 `@dxf` 模型函数。

**一个绘图就是一个模型。** 它具有与 `@step` 零件相同的包装器、记录、新鲜度门和构建作业；它的一个输出是 `.dxf` 文件；它没有几何树（没有任何东西链接到绘图）。每次运行都会写入兄弟 `<name>.dxf`（或装饰器命名的 `out=`）；未更改的源是无操作的；调用零件模型的绘图（在其体内内嵌 `bracket()`）在零件的 GEOMETRY 更改时变为过时，在未更改时不为过时；`cadgen store why <drawing>.py` 解释了判定结果；`--force` 无论如何都会重新构建它。CAD 查看器和 `dxf snapshot` 直接读取 `.dxf` 文件本身，因此你交给切割服务的文件和查看器渲染的文件是同一个。

## 合同

**一个 `@dxf` 函数不接受参数并返回 build123d 2D 几何图形。引擎写入 DXF。** 你永远不会构建文档、命名文件或放置实体 — 与 `@step` 相同的分工。

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
- **`{layer: shape}`** → 命名层，当绘图确实有多个 CAM 操作 (`CUT` / `ENGRAVE` / `SCORE`) 时。一个子代全部标记的 `Compound` 意思相同。
- **没有参数。** 尺寸是模块常量 (`HOLE_D = 4.5`) 或从绘图派生的零件导入的常量；不同的绘图是不同的文件。
- **文本** 是 `bd.Text(...)` 在标记层上雕刻的 OUTLINES，永远不会是 DXF 的 `TEXT` 实体：切割和标记工具链消耗几何图形，CAM 内部字体渲染不可靠。
- **几何图形必须位于 XY 平面。** 从实体中获取的面位于该实体的高度；将其重新定位（`flatten.flatten_face(face)`，或 `bd.Location((0, 0, -z)) * face`）。引擎拒绝非平面几何图形，而不是静默地写入其 XY 影子。
- **输出字节是几何图形的函数。** 层按名称排序，实体按几何内容排序，因此未更改的绘图在任何机器上冷启动或热启动都会重建为相同的文件。

## 三个 DXF 工作流程

在创建新绘图时，从 `references/generator-templates.md` 复制适用于相应工作流程的完整模板。

1. **从头开始绘制**（垫圈、面板、模板、没有 3D 模型背后的切割布局）：一个构建草图并返回它们的 `<name>.py`。
2. **生成的 STEP 零件的平面图形**：一个与模型它派生自的绘图脚本并具有自己的茎（每个模型一个文件 — `bracket_drawing.py` 与 `bracket.py` 并存）。导入模型并调用它，就像装配组合子一样：导入永远不会构建，并且在绘图的构建内部调用返回零件的几何图形（如果它过时，则先构建零件）。

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

   绘图的记录固定了零件的树，因此更改其几何图形的零件编辑使绘图过时，而未更改的（注释、重构、颜色）则使其保持当前。从零件导入的常量（`from bracket import THICKNESS`）以相同的方式按值跟踪。

3. **导入的 STEP 的平面图形**（没有 Python 源的 `.step`/`.stp`）：使用 `cadgen.read_step` 读取，而不是 `build123d.import_step`。它将文件的内容哈希记录为构建输入，因此替换供应商 STEP 使绘图仅因自身而过时，无需 `--force`；通过 build123d 读取它，绘图保持“当前”相对于其下方的文件。

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

   **永远不要读取此项目生成的 STEP。** 读取 `@step` 模型写入的 `.step` 不是循环，它是一个输入在每次模型运行时变化的绘图：新鲜度门永远无法说“当前”，每次构建都是完整重建，平面图形取决于上次运行在磁盘上留下的内容。将源 STEP 保存在绘图旁边的 `imported/` 目录中，像任何其他输入一样提交 — 输入路径和输出路径是不同的文件是整个规则。对于此项目生成的 STEP，使用工作流程 2：导入模型脚本并调用它，它通过结果跟踪，永远不会触及工件。

每个模型一个文件是推荐的做法，绘图有自己的脚本：一个文件可以声明多个模型 — 两个 `@dxf` 绘图，或一个 `@dxf` 旁边有一个 `@step` — 每个都是自己的记录、输出和作业（唯一的模型写入 `<file>.dxf`；共享文件的模型写入 `<function>.dxf>`），但它们共享文件的闭包，因此编辑一个会重建所有。绘图组合模型，而不是相反：从 `@step` 身体调用 `@dxf` 函数只是其 2D 几何图形并链接不到任何东西。查看器目录仅包含工件：脚本永远不会列出；运行写入的 `.dxf` 是查看器渲染的条目。

## 使用此技能的情况

当用户要求 DXF 文件、2D 绘图、轮廓、轮廓、模板、垫圈、面板、平面图形或激光、等离子、水刀或 CNC 路由的切割布局时，使用此技能。

使用 `$cad` 表示 DXF 派生自的 3D 零件或装配。使用 `$sendcutsend` 表示 SendCutSend 特定的上传预检。

## 默认值

除非用户指定否则使用这些默认值：

- 单位：毫米。引擎设置它们；绘图永远不会声明单位。
- 几何图形位于 XY 平面上的 1:1 比例。
- 切割轮廓封闭。开放轮廓属于弯曲/雕刻/参考层 — 生成验证强制执行这一点（见验证）。
- 对于 CAD 支持的零件，使用 `cadgen.flatten` 从真实拓扑中导出轮廓，而不是重新绘制：`planar_faces` 选择，`flatten_face` 精确地将面放置到 XY 中，`union_faces` 融合，`flat_pattern` 在一次调用中完成所有。只有在没有可靠的 3D 拓扑时才手动绘制参数化轮廓。
- Kerf/工具半径补偿是 `flatten.offset_profile(shape, amount)` 或 `flat_pattern(..., kerf=...)`；永远不会手动偏移坐标。
- **曲线保持曲线。** 并集和偏移是精确的 OCC 操作，因此圆角角落导出为 `ARC`，孔导出为 `CIRCLE`，包括 kerf。导出为数百个短 `LINE` 的轮廓意味着某些东西退回到采样路径 — 调查而不是接受它。
- 层携带意图：将切割几何图形和弯曲/折叠线放在不同的层上，并在弯曲层名称中包含“bend”，以便下游工具将它们分类为弯曲而不是切割。
- DXF 层是绘图结构，而不是 STEP 零件/装配结构。

## 工具

```bash
python <drawing>.py [flags]                    # 其 __main__ 调用 @dxf 模型，写入 .dxf
cadgen dxf snapshot <drawing.dxf> <file.png>   # 渲染它
cadgen store why <drawing>.py                  # 绘图为何过时或当前
```

**运行脚本（其 `__main__` 调用）是唯一的入口。** 没有 `cadgen dxf build`：`.dxf` 没有命令必须实现的派生状态 — 文件就是产品，CAD 查看器直接解析它，`dxf snapshot` 按需网格化它。绘图的门使重建廉价：未更改的源，其 `.dxf` 仍然验证，其零件子代未更改是无操作的，`--force` 无论如何都会重建。字节是绘图几何图形的函数，因此冷启动和热守护进程工作写入相同的文件。构建永远不会等待或取消另一个；调用零件的绘图像任何父代一样并行构建它们。

导入的 `.dxf` 无需任何东西 — 直接交给 snapshot 或查看器。

使用活动项目的 Python 解释器；将 `python` 视为解释器占位符，并使用 `--help` 获取完整界面。目标路径从命令的当前工作目录解析；从拥有工件的目录运行，使用相对于当前工作目录的目标路径。将绘图脚本保存在其派生几何图形的同一目录中，命名为 `<name>.py`。

标志（模型脚本运行自身；没有生成 CLI）：

- `--force` — 即使记录的输出当前也要重新生成。
- `--verbose`, `--json`。

运行回答与 STEP 模型的回答完全相同 — `built DXF/plate_drawing.dxf` 或 `current DXF/plate_drawing.dxf` — 在 stderr 上显示进度；`--json` 使结果为一条 JSON 行（`outcome`，`document` 和 `tree`，对于绘图 `tree` 为 null）和进度为每个转换一条 JSON 行。

一个脚本，一个绘图：运行每个您想要构建的脚本。不要在 `@dxf` 函数的返回值中放置输出路径；装饰器上的 `out=` 是绘图命名其目标的唯一地方（相对于脚本）。

`cadgen dxf snapshot` 将绘图的 3D 平面图形渲染为 PNG 静态图像：

```bash
cadgen dxf snapshot path/to/imported.dxf review.png
cadgen dxf snapshot path/to/drawing.dxf review.png --camera top
```

它只接受 `.dxf` 文档 — 模型脚本按名称拒绝（运行 `python <drawing>.py`，然后 snapshot 它写入的绘图）。命令通过捆绑的 Node 单次运行按需网格化平面图形，并通过共享的 snapshot CLI (`cadgen.snapshot_cli`) 和每个渲染技能使用的相同无头浏览器运行时进行渲染。正常 snapshot 使用确定的 CAD 光照并隐藏网格和轴指南。

OUT — 第二个位置参数 — 按给定方式写入，相对于当前工作目录解析。目标在渲染开始前被删除，完成的图像原子写入，因此：在迭代时重用一个名称（每个读取都是您刚刚运行的渲染），当您确实需要比较两个时命名迭代。无效请求组合在触摸 OUT 之前失败；请求接受后，首先清除 OUT，以便后续失败留下缺失文件而不是过时的图像。目录（`tmp/` 作为 OUT）是无所谓的案例，并在其中生成带时间戳的名称，打印在 `saved snapshot:` 行上。

语法：`cadgen dxf snapshot TARGET [OUT] [flags]`。标志：`--mode view|list`，`--camera`，`--render`，`--display`，`--size-profile`，`--width`/`--height`，`--job`，`--view-labels`，`--debug`，`--json`。`--render` 选择进入摄影场景并接受 `light`，`dark`，紧凑 Render JSON，或文件路径。在 Render JSON 内设置摄影相机。顶层 `--camera` 和 `--display` 控制正常绘图 snapshot，不能与 Render 组合。
绘图没有选择器、运动学、截面模式、展开装配结构或 CAD 边拓扑，这些组合要么不存在，要么明确拒绝。

没有 CLI 检查现有的 `.dxf`。对于实体/层检查，直接使用 `ezdxf` 读取它（它随 build123d 到达），`validate_dxf_file` 用于绘图检查；在 CAD 查看器中直观审查几何图形：

```python
import ezdxf

doc = ezdxf.readfile("path/to/source.dxf")
msp = doc.modelspace()
cut = msp.query('*[layer=="CUT"]')
holes = msp.query('CIRCLE[layer=="CUT"]')
```

仅报告实际运行的检查。

## 交接

在创建或修改 DXF 绘图后，当该技能安装时，您必须始终将显式的 `.dxf` 文件路径(s) 交给 `$cad-viewer` 并在最终响应中包含其活动查看器链接(s)。如果 `$cad-viewer` 不可用或启动失败，报告该问题，并依赖 `ezdxf` 检查而不是静默地省略交接。

最终响应应包括生成的文件、返回的查看器链接、实际运行的验证和假设。

## 工作流程

1. 将请求转换为简短的摘要：轮廓尺寸、孔和插槽、层、单位、输出路径和验证目标。
2. 选择工作流程：从头开始绘制、生成的模型平面图形（首先使用 `$cad` 创建和验证 3D 几何图形），或导入的 STEP 平面图形。
3. 使用有意义的尺寸作为命名常量编写或编辑 `<name>.py` 源，重用模型的几何图形辅助函数而不是重复公式。
4. 直接运行每个绘图脚本 (`python <drawing>.py`)；不要扫描目录。

```bash
python path/to/source.py
python path/to/source.py --force
```

5. 确定性地验证生成的 DXF，然后交接并报告。

## 查看器集成

CAD 查看器仅目录 `.dxf` 文件（工件，永远不会是脚本），并且是一个静态可视化工具：它渲染磁盘上存在的 `.dxf`（解析并网格化它 — 尺寸绘图的 2D 线工作，切割布局的可折叠 3D 平面图形），并且永远不会运行脚本。还没有 `.dxf` 的绘图直到其脚本运行后才出现；编辑后的重新生成也是脚本的工作。没有查看器内导出。导入的 `.dxf` 直接渲染，无需工件管理。

## 验证

验证在生成时发生，而不是之后：每个 `@dxf` 构建在引擎刚序列化的文档上运行绘图检查，在写入任何东西之前，并且带有错误发现的构建失败。检查：切割层轮廓必须封闭（多边形、圆或连接的线/圆弧循环）、长度为零/退化实体被拒绝、精确重复的几何图形（双切割风险）被拒绝、明确无单位的文档被拒绝，空的模型空间被拒绝。仅允许在弯曲/雕刻/参考意图层上开放几何图形（通过名称匹配）。

相同的检查在事后对任何现有的 `.dxf` 文件运行 — 包括一个从未来自生成器 — 通过 `cadgen.drawing_checks`：

```python
from cadgen.drawing_checks import validate_dxf_file

for finding in validate_dxf_file("path/to/file.dxf"):
    print(finding.render())
```

除了内置检查外，使用有针对性的 `ezdxf` 读取（按层实体计数、绘图范围、用户指定的每个尺寸）与生成的兄弟 `.dxf`（或当声明 `out=` 时的路径）验证请求的尺寸，并在 CAD 查看器中直观审查几何图形：

```python
import ezdxf

doc = ezdxf.readfile("path/to/source.dxf")
msp = doc.modelspace()
cut = msp.query('*[layer=="CUT"]')
holes = msp.query('CIRCLE[layer=="CUT"]')
```

仅报告实际运行的检查。

## 交接

在创建或修改 DXF 绘图后，您必须始终在 `$cad-viewer` 安装时将显式的 `.dxf` 文件路径(s) 交给它，并在最终响应中包含其活动查看器链接(s)。如果 `$cad-viewer` 不可用或启动失败，报告该问题，并依赖 `ezdxf` 检查而不是静默地省略交接。

最终响应应包括生成的文件、返回的查看器链接、实际运行的验证和假设。
