---
name: urdf
description: URDF机器人描述的编写与验证。在创建、编辑、检查、验证或调试`.urdf`文件、机器人连杆、关节、限制、惯性、视觉/碰撞几何形状、网格引用、框架约定或机器人描述工件时使用。使用SRDF技能处理MoveIt2语义组和IK/路径规划语义；使用CAD技能处理STEP/STL/3MF/DXF/GLB输出。
---

# URDF

来源：维护在 [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) 中。
使用已安装的本地技能文件作为运行时真实来源；仓库链接仅用于来源追溯和发布审核。

使用此技能处理 URDF 机器人描述输出。将 URDF 工作视为受约束的运动学建模，而不仅仅是 XML 写入。主要的正确性风险是坐标系放置、关节轴语义、单位一致性、网格比例和惯性数据。

## 设置

此技能的命令是 `cadgen` 分发的薄入口点，它包含 Python 构建运行时和它执行的 JavaScript。安装一次：

```bash
python -m pip install -r requirements.txt
```

渲染还需要一个浏览器，而 pip 无法提供：

```bash
python -m playwright install chromium
```

## 核心规则

1. `.urdf` 文件是真实来源。直接编写和编辑 URDF XML；不要为其构建 Python 生成管道。没有 `gen_urdf()` 合约。
2. 在编写或更改 URDF XML 之前，建立机器人的坐标系、关节、几何形状、单位和假设账本，并将其作为注释块嵌入到 `.urdf` 文件的顶部。参见 `references/design-ledger.md`。
3. 精确使用 URDF 坐标系语义。关节原点、连杆坐标系、关节轴以及视觉/碰撞/惯性原点使用不同的参考坐标系。参见 `references/frame-semantics.md`。
4. 不要从模糊的文本中推断空间变换、网格单位、手性、轴或关节符号。使用 CAD 变换、带尺寸的绘图、测量值、现有源数据或明确的文档假设。
5. 不要手绘计算结果中的数值——惯性张量、质心、跨多个连杆的单位转换、镜像变换。计算它们：原语的开式公式，或用于网格派生值的一次性辅助脚本。参见 `references/inertials.md`。
6. 对于物理连杆，当目标消费者需要时，分别建模 `inertial`、`visual` 和 `collision`。仅坐标系的连杆可以有意省略质量和几何形状。
7. 在报告完成之前，使用 `cadgen urdf validate` 验证创建或修改的每个 `.urdf`。参见 `references/validation.md`。
8. 允许并鼓励使用辅助脚本进行计算，但它们是脚手架，不是工件的真实来源。对于复杂或真正参数化的模型，在磁盘上保留与相关源代码（例如 STEP 生成器源）相邻的本地辅助脚本是合理的，并在账本中注明；这是可选的，签入的 `.urdf` 仍然是规范。

## CAD 查看器传递

完成创建或修改 `.urdf` 的 URDF 工作后，当安装了该技能时，您必须始终将显式文件路径传递给 `$cad-viewer`。如果 `$cad-viewer` 不可用或启动失败，请报告该问题，而不是静默地省略传递。

## 工作流程

1. 确定目标 `.urdf` 文件及其消费者：RViz、robot_state_publisher、Gazebo/Ignition、MoveIt、真实机器人驱动器或另一个模拟器。
2. 在编辑坐标系、原点、轴、网格比例、限制或惯性之前，读取或创建设计账本。将账本作为注释块保存在 `.urdf` 本身中。
3. 当连杆引用网格时，首先准备网格资源：每个连杆一个网格，由拥有 CAD/网格工作流在该连杆的坐标系中导出。参见 `references/meshes.md`。
4. 直接编写或编辑 URDF XML，遵循 `references/authoring-contract.md` 关于结构、顺序和命名的约定。
5. 计算——不要猜测——惯性和其他派生数字。参见 `references/inertials.md`。
6. 使用 `cadgen urdf validate` 进行验证；修复发现的问题并重新验证，直到干净。
7. 运行 `references/validation.md` 中的验证配方：当可用时使用外部工具 (`check_urdf`)，然后进行查看器审查，扫描每个关节。
8. 报告剩余的假设、未检查的空间数据以及验证差距。

## 命令

从此技能的 `requirements.txt` 安装的 Python 环境中运行 `cadgen`（`python -m cadgen.cli <verb>` 使用该解释器是路径无关的等效方式）。`cadgen doctor <skill-dir>` 验证安装的 cadgen 是否与此技能的固定版本匹配——在安装不匹配的情况下，文档会静默地漂移。验证本身不需要超出 Python 标准库；只有快照需要浏览器。使用 `cadgen <verb> --help` 获取完整的当前界面。

验证器形状是：

```bash
cadgen urdf validate path/to/robot.urdf
cadgen urdf validate path/to/robot.urdf --strict
cadgen urdf validate path/to/robot.urdf --json
cadgen urdf validate path/to/robot.urdf --packages robot_description=/path/to/pkg
cadgen urdf snapshot path/to/robot.urdf review.png
```

验证器在一次遍历中收集所有发现（严重性、代码、XML 路径）跨越 XML 结构、树拓扑、关节语义（限制、模仿、动力学）、几何形状、网格引用、材料、惯性物理和拼写错误的元素，并打印摘要。一次运行验证一个文件：`--strict` 将警告视为失败；`--json` 打印一行 `{"ok", "path", "issues": [{"severity", "code", "message", "element", "hint"}], "summary"}`，其中 `element` 是 XML 路径；`--packages NAME=PATH` 解析 `package://` 网格 URI 并为多个根重复；如果目标失败，它将退出非零。相对目标从当前工作目录解析；从拥有文件的工作空间运行。

验证是一个护栏，而不是空间证明：一个 URDF 可以通过所有结构检查，同时将关节放置在错误的位置。账本和查看器扫描就是为了这个原因。

## 快照工具

`cadgen urdf snapshot` 将机器人渲染为静态 PNG，使用每个渲染技能使用的相同共享 CLI 和无头浏览器运行时——因此快照与 CAD 查看器显示的内容匹配。

```bash
cadgen urdf snapshot path/to/robot.urdf review.png
```

它只接受 `.urdf`。使用 `--joint-values` 设置机器人姿态——`{joint: degrees}` JSON，未命名的关节保持其默认值，其中 CAD 查看器打开机器人（`"jointValues"` 任务字段与数据包中的相同）。快照使用查看器自己的场景绘制机器人，因此它显示查看器显示的内容，并且无法加载的链接网格会导致失败而不是省略链接。机器人以米为单位编写，并自动在机器人场景比例上定位。

正常快照使用 Solid 预设和 Light 外观；省略的组继承预设默认值。
传递 `--display render` 以使用共享的摄影场景。内联显示 JSON 和 JSON 文件使用分组设置，例如 `lighting`、`background` 和 `floor`；`appearance` 是 `light`（默认）或 `dark`。投影和焦距属于 `display.camera`。顶级 `--camera` 和 `--joint-values` 在每种显示模式下保持激活状态。显示模式是 `solid` 和 `render`：`edges`、`clip`、`exploded`、`xray`、`hidden-line` 和 `wireframe` 模式以及 `hidden`/`off` 表面样式描述 STEP 模型的 CAD 边缘、部件和实体，并且在此处按名称拒绝。

连杆网格相对于描述解析，因此它们必须存在：未填充的 Git LFS 指针会导致“未加载机器人连杆网格”失败。首先运行 `git lfs checkout <mesh dir>`。

语法是 `cadgen urdf snapshot TARGET [OUT] [flags]`，每个格式门都使用相同的语法。使用 `cadgen urdf snapshot --help` 获取完整的当前界面——机器人无法操作的标志从其中缺失，而不是被拒绝。

## 参考

- 编写约定（结构、顺序、黄金骨架）：`references/authoring-contract.md`
- 设计账本：`references/design-ledger.md`
- 坐标系语义：`references/frame-semantics.md`
- 网格准备和引用：`references/meshes.md`
- 惯性（公式、脚本、合理性门）：`references/inertials.md`
- URDF 编辑工作流程：`references/urdf-workflow.md`
- 验证和验证配方：`references/validation.md`
