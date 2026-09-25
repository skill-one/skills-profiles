# URDF

来源：维护在 [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) 中。
使用已安装的本地技能文件作为运行时真实来源；仓库链接仅用于来源和发布审查。

使用此技能处理 URDF 机器人描述输出。将 URDF 工作视为受约束的运动学建模，而不仅仅是 XML 写入。主要的正确性风险包括框架放置、关节轴语义、单位一致性、网格比例和惯性数据。

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
2. 在编写或更改 URDF XML 之前，建立机器人的框架、关节、几何形状、单位和假设账本，并将其作为注释块嵌入 `.urdf` 文件的顶部。参见 `references/design-ledger.md`。
3. 精确使用 URDF 框架语义。关节原点、链接框架、关节轴以及视觉/碰撞/惯性原点使用不同的参考框架。参见 `references/frame-semantics.md`。
4. 不要从模糊的文本中推断空间变换、网格单位、手性、轴或关节符号。使用 CAD 变换、带尺寸的绘图、测量值、现有源数据或明确的文档假设。
5. 不要自由绘制计算结果数字——惯性张量、质心、跨多个链接的单位转换、镜像变换。计算它们：原始体的封闭形式公式，或用于网格派生值的一次性辅助脚本。参见 `references/inertials.md`。
6. 对于物理链接，当目标消费者需要时，分别建模 `inertial`、`visual` 和 `collision`。仅框架链接可以有意省略质量和几何形状。
7. 在报告完成之前，使用 `cadgen urdf validate` 验证每个创建或修改的 `.urdf`。参见 `references/validation.md`。
8. 允许并鼓励使用辅助脚本进行计算，但它们是脚手架，不是工件的真实来源。对于复杂或真正参数化的模型，在磁盘上保留与相关源代码（例如 STEP 生成器源）相邻的模型本地辅助脚本是合理的，并在账本中注明；这是可选的，签入的 `.urdf` 仍然是规范。

## CAD 查看器交接

在完成创建或修改 `.urdf` 的 URDF 工作后，你必须始终在安装了该技能时将显式文件路径传递给 `$cad-viewer`。如果 `$cad-viewer` 没有运行，它必须启动 CAD 查看器并返回相关创建或更新文件(件)的链接；如果 `$cad-viewer` 不可用或启动失败，请报告该问题，而不是静默地省略交接。

## 工作流程

1. 确定目标 `.urdf` 文件及其消费者：RViz、robot_state_publisher、Gazebo/Ignition、MoveIt、真实机器人驱动器或另一个模拟器。
2. 在编辑框架、原点、轴、网格比例、限制或惯性之前，读取或创建设计账本。将账本作为注释块保存在 `.urdf` 本身中。
3. 当链接引用网格时，首先准备网格资源：每个链接一个网格，由拥有 CAD/网格工作流在该链接的框架中导出。参见 `references/meshes.md`。
4. 直接编写或编辑 URDF XML，遵循 `references/authoring-contract.md` 关于结构、顺序和命名的约定。
5. 计算——不要猜测——惯性和其他派生数字。参见 `references/inertials.md`。
6. 使用 `cadgen urdf validate` 进行验证；修复发现的问题并重新验证，直到干净。
7. 运行 `references/validation.md` 中的验证配方：当可用时使用外部工具 (`check_urdf`)，然后进行查看器审查，扫描每个关节。
8. 报告剩余的假设、未检查的空间数据以及验证差距。

## 命令

从此技能的 `requirements.txt` 安装的 Python 环境中运行 `cadgen`（`python -m cadgen.cli <verb>` 使用该解释器是路径无关的等价物）。`cadgen doctor <skill-dir>` 验证安装的 cadgen 是否与此技能的固定版本匹配——在安装不匹配的情况下，文档会静默地漂移。验证本身不需要超出 Python 标准库；只有快照需要浏览器。使用 `cadgen <verb> --help` 获取完整的当前界面。

验证器形状是：

```bash
cadgen urdf validate path/to/robot.urdf
cadgen urdf validate path/to/robot.urdf --strict
cadgen urdf validate path/to/robot.urdf --json
cadgen urdf validate path/to/robot.urdf --packages robot_description=/path/to/pkg
cadgen urdf snapshot path/to/robot.urdf review.png
```

验证器在一次遍历中收集所有发现（严重性、代码、XML 路径）跨越 XML 结构、树拓扑、关节语义（限制、mimic、动力学）、几何形状、网格引用、材料、惯性物理和拼写错误的元素，并打印摘要。一次运行验证一个文件：`--strict` 将警告视为失败；`--json` 打印一行 `{"ok", "path", "issues": [{"severity", "code", "message", "element", "hint"}], "summary"}`，其中 `element` 是 XML 路径；`--packages NAME=PATH` 解析 `package://` 网格 URI 并为多个根重复；如果目标失败，它将退出非零。相对目标从当前工作目录解析；从拥有文件的工件工作区运行。

验证是一个护栏，而不是空间证明：一个 URDF 可以通过所有结构检查，同时将关节放置在错误的位置。账本和查看器扫描就是为了这个原因。

## 快照工具

`cadgen urdf snapshot` 将机器人渲染为静态 PNG，使用每个渲染技能使用的相同共享 CLI 和无头浏览器运行时——因此快照与 CAD 查看器显示的内容匹配。

```bash
cadgen urdf snapshot path/to/robot.urdf review.png
```

它只接受 `.urdf`。使用 `--joint-values` 设置机器人姿态——`{joint: degrees}` JSON，未命名的关节保持在静止姿态（`"jointValues"` 任务字段与数据包中的相同）。机器人以米为单位编写，并自动在机器人场景比例上框架化。

正常快照使用确定的 CAD 光照并隐藏网格和轴指南。传递 `--render light` 或 `--render dark`（或摄影 Render JSON 或文件路径）以使用共享的 Render 场景。没有 `studio` 的包在 CLI 中解析为 Light。在 Render JSON 中设置其相机；顶级 `--camera`、`--display` 和 `--joint-values` 控制正常快照，不能与 Render 组合。机器人链接网格没有 CAD-edge 或分解装配拓扑，因此这些显示组合被明确拒绝。

链接网格相对于描述解析，因此它们必须存在：未填充的 Git LFS 指针失败为“未加载机器人链接网格”。首先运行 `git lfs checkout <mesh dir>`。

语法是 `cadgen urdf snapshot TARGET [OUT] [flags]`，每个格式门都使用相同的语法。使用 `cadgen urdf snapshot --help` 获取完整的当前界面——机器人无法执行的标志从它中缺失，而不是被它拒绝。

## 参考

- 编写约定（结构、顺序、黄金骨架）：`references/authoring-contract.md`
- 设计账本：`references/design-ledger.md`
- 框架语义：`references/frame-semantics.md`
- 网格准备和引用：`references/meshes.md`
- 惯性（公式、脚本、合理性门）：`references/inertials.md`
- URDF 编辑工作流程：`references/urdf-workflow.md`
- 验证和验证配方：`references/validation.md`
