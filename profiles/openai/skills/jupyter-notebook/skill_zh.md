# Jupyter Notebook 技能

为两种主要模式创建干净、可复现的 Jupyter 笔记本：

- 实验和探索性分析
- 教程和以教学为导向的演示

优先使用捆绑的模板和辅助脚本，以保持一致的架构并减少 JSON 错误。

## 使用场景
- 从零开始创建新的 `.ipynb` 笔记本。
- 将粗略的笔记或脚本转换为结构化的笔记本。
- 重构现有的笔记本，使其更具可复现性和可浏览性。
- 构建其他人将阅读或重新运行的实验或教程。

## 决策树
- 如果请求是探索性的、分析性的或基于假设的，选择 `experiment`。
- 如果请求是指导性的、分步的或针对特定受众的，选择 `tutorial`。
- 如果正在编辑现有的笔记本，将其视为重构：保留意图并改进结构。

## 技能路径（一次性设置）

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export JUPYTER_NOTEBOOK_CLI="$CODEX_HOME/skills/jupyter-notebook/scripts/new_notebook.py"
```

用户范围的技能安装在 `$CODEX_HOME/skills` 下（默认：`~/.codex/skills`）。

## 工作流程
1. 锁定意图。
   确定笔记本类型：`experiment` 或 `tutorial`。
   捕获目标、受众以及“完成”的标准。

2. 从模板构建基础。
   使用辅助脚本避免手动编写原始笔记本 JSON。

```bash
uv run --python 3.12 python "$JUPYTER_NOTEBOOK_CLI" \
  --kind experiment \
  --title "比较提示变体" \
  --out output/jupyter-notebook/compare-prompt-variants.ipynb
```

```bash
uv run --python 3.12 python "$JUPYTER_NOTEBOOK_CLI" \
  --kind tutorial \
  --title "嵌入简介" \
  --out output/jupyter-notebook/intro-to-embeddings.ipynb
```

3. 用小的、可运行的步骤填充笔记本。
   保持每个代码单元专注于一个步骤。
   添加简短的 Markdown 单元来解释目的和预期结果。
   避免在短总结有效时出现大型、嘈杂的输出。

4. 应用正确的模式。
   对于实验，遵循 `references/experiment-patterns.md`。
   对于教程，遵循 `references/tutorial-patterns.md`。

5. 在处理现有笔记本时安全地编辑。
   保留笔记本结构；除非它改进了自上而下的故事，否则避免重新排序单元。
   优先选择有针对性的编辑而不是全面重写。
   如果你必须编辑原始 JSON，请先查看 `references/notebook-structure.md`。

6. 验证结果。
   当环境允许时，从上到下运行笔记本。
   如果执行不可行，请明确说明并指出如何本地验证。
   使用 `references/quality-checklist.md` 中的最终检查清单。

## 模板和辅助脚本
- 模板位于 `assets/experiment-template.ipynb` 和 `assets/tutorial-template.ipynb`。
- 辅助脚本加载一个模板，更新标题单元，并写入一个笔记本。

脚本路径：
- `$JUPYTER_NOTEBOOK_CLI`（安装默认：`$CODEX_HOME/skills/jupyter-notebook/scripts/new_notebook.py`）

## 临时和输出约定
- 使用 `tmp/jupyter-notebook/` 存放中间文件；完成后删除。
- 在此代码库中工作时，将最终产物写入 `output/jupyter-notebook/`。
- 使用稳定、描述性的文件名（例如，`ablation-temperature.ipynb`）。

## 依赖项（仅在需要时安装）
优先使用 `uv` 进行依赖管理。

本地笔记本执行的可选 Python 包：

```bash
uv pip install jupyterlab ipykernel
```

捆绑的构建脚本仅使用 Python 标准库，不需要额外的依赖项。

## 环境
没有必需的环境变量。

## 参考映射
- `references/experiment-patterns.md`：实验结构和启发式方法。
- `references/tutorial-patterns.md`：教程结构和教学流程。
- `references/notebook-structure.md`：笔记本 JSON 结构和安全编辑规则。
- `references/quality-checklist.md`：最终验证检查清单。
