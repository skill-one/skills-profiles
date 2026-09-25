# PyMOL

## 前置条件

1.  **`uv`**: 阅读 `uv` 技能并遵循其安装说明，确保 `uv` 已安装并在 PATH 路径中。
2.  **用户通知**: 如果工作区根目录中不存在 `.licenses/pymol_LICENSE.txt` 文件，则 (1) 需要显著通知用户检查 https://www.pymol.org/ 上的许可证，然后 (2) 创建记录通知文本和时间戳的文件。

## 概述

所有 PyMOL 命令通过 `uv` 在主机上运行，使用 OSMesa 软件渲染 — 无需 GPU、显示器或 X 服务器。结构文件必须在运行 PyMOL 之前下载到主机上。

**禁止使用的情况**:

-   用户想要运行 AlphaFold 预测。
-   用户想要进行对接或分子动力学模拟。
-   用户只有序列而没有结构文件 — 首先获取结构。在继续之前，检查是否有其他已安装的技能可以从 PDB 或 AlphaFold 数据库中检索结构。

## 安装 (代理指令)

确保主机系统上已安装 `uv`。PyMOL 脚本使用 PEP 0723 头部声明其依赖项，执行脚本时 `uv run` 将自动处理安装它们（包括 `pymol-open-source-whl`）。

## 核心规则

-   **输出路径必须是绝对路径或相对于用户项目根目录的相对路径**。始终从用户的项目目录中运行 PyMOL 脚本。
-   **仅使用软件渲染**。使用 `cmd.png()` 进行输出。永远不要使用 `cmd.draw()` 或 `cmd.ray()` 与硬件加速 — OSMesa 不支持它。设置环境变量 `PYOPENGL_PLATFORM=osmesa` 以进行无头渲染。
-   **始终保存 `.pse` 会话文件** 与任何 PNG 输出一起。这允许用户在本地 PyMOL 中打开会话以进行进一步检查。
-   **始终在 PyMOL 脚本的末尾调用 `cmd.quit()`**。省略它会导致进程停止响应。
-   **初始化模板是强制性的**。每个 PyMOL 脚本必须以初始化序列开头。`from pymol import cmd` 必须在 `finish_launching()` 之后，而不是之前。
-   参考 [references/PYMOL_REFERENCE.md](references/PYMOL_REFERENCE.md) 了解选择语法、常用命令和注意事项。
-   **飞行前文件检查**: 在编写 PyMOL 脚本或运行它之前，你必须验证请求的结构文件是否实际存在于主机机器上。
-   **验证结构加载**: 使用 `cmd.load()` 加载结构后，始终通过检查 `cmd.count_atoms("all")` 来验证它是否成功。如果结果是 0，请将错误打印到 stdout 并立即调用 `cmd.quit()`。
-   **自动检测 α 碳追踪**: 对于 **卡通** 表示，你的 PyMOL 脚本应自动检测结构是否是 α 碳追踪 (`cmd.count_atoms("name CA") == cmd.count_atoms("all")`)，然后你必须遵循 **α 碳追踪卡通** 配方。
-   **通知**: 如果使用此技能，请确保在输出中提及这一点。

## 快速入门

*   确保结构文件下载到用户项目中的目录。
*   编写一个 PyMOL Python 脚本（例如 `render.py`），包含所需的初始化模板和 PEP 0723 头部。
*   通过 `uv run` 运行它：`bash uv run render.py`

### 最小示例脚本 (`render.py`)

```python
# /// script
# requires-python = ">=3.10, <3.13"
# dependencies = [
#     "pymol-open-source-whl",
# ]
# ///

import os
import sys

# 设置无头渲染的环境变量
os.environ["PYOPENGL_PLATFORM"] = "osmesa"

import pymol # pytype: disable=import-error
pymol.pymol_argv = ["pymol", "-cq"]
pymol.finish_launching()

from pymol import cmd # pytype: disable=import-error

cmd.load("AF-P00520-F1-model_v4.cif", "structure")
cmd.show("cartoon")
cmd.color("green", "ss h")
cmd.color("yellow", "ss s")
cmd.color("gray", "ss l+''")
cmd.orient()
cmd.set("ray_opaque_background", 1)
cmd.png("output/render.png", width=1200, height=900, dpi=150)
cmd.save("output/session.pse")
cmd.quit()
```

## 常用配方

参考 [references/RECIPES.md](references/RECIPES.md) 了解完整、可复制粘贴的配方。可用配方：

-   **带二级结构着色的卡通** — 基本螺旋/片层/环着色
-   **α 碳追踪卡通** — 强制对仅包含 CA 的结构进行卡通表示
-   **B 因子 (pLDDT) 着色** — 根据 B 因子进行连续光谱着色
-   **AlphaFold pLDDT 着色** — 基于阈值的置信度颜色
-   **突出显示特定残基** — 将活性位点或关键残基显示为棒状
-   **表面渲染** — 卡通上方的透明表面
-   **静电表面渲染** — 真空静电（定性）
-   **多链复合物着色** — 自动按链着色
-   **B 因子橡皮泥分析** — 管宽度与柔韧性成正比
-   **腔和口袋可视化** — 带配体聚焦的表面腔检测
-   **多结构批量渲染** — 渲染结构目录
-   **测量残基之间的距离** — CA–CA 距离带标签
-   **缩放到结合口袋** — 简单口袋聚焦
-   **蛋白质-配体相互作用** — 配体隔离、样式渲染、极性接触
-   **双结构 RMSD 叠加** — 对齐/cealign 带自动回退
-   **计算机模拟诱变** — 使用诱变向导突变残基
-   **加载和修改现有会话** — 重新打开 `.pse` 文件

## 解释输出

-   `output/` 目录包含 PNG 图像和 `.pse` 会话文件。
-   任何测量或指标（距离、RMSD、原子计数）都由 PyMOL 脚本打印到 stdout。向用户报告这些值。
-   向用户展示 PNG 图像并描述可视化效果。
-   告知用户他们可以在本地 PyMOL 中打开 `.pse` 文件以进行进一步探索、旋转或修改可视化效果。
-   如果用户想要修改，请在新脚本中加载保存的 `.pse` 并重新运行。
-   带有表面的较大会话可能会超过 `--max_output_mb` 限制（默认 500 MB）。如有需要，使用 `--max_output_mb=1000` 增加它。
