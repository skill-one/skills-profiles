---
name: paper-compilation
description: 使用自动错误检测、chktex 格式检查和引文/参考文献验证功能，将 LaTeX 论文编译为 PDF。运行完整的 pdflatex + bibtex 管道。当用户需要编译论文、修复编译错误或调试 LaTeX 时使用。
---

# 论文编译

将 LaTeX 论文编译为 PDF，并具备错误检测与修正功能。

## 输入

- `$ARGUMENTS` — 主 `.tex` 文件的路径

## 脚本

### 编译论文
```bash
python ~/.claude/skills/paper-compilation/scripts/compile_paper.py paper/main.tex
python ~/.claude/skills/paper-compilation/scripts/compile_paper.py paper/main.tex --check-style
python ~/.claude/skills/paper-compilation/scripts/compile_paper.py paper/main.tex --output paper/output.pdf
```

报告：编译状态、页数、警告、引用/参考文献统计、格式问题。

### 编译前验证引用
```bash
python ~/.claude/skills/citation-management/scripts/validate_citations.py \
  --tex paper/main.tex --bib paper/references.bib --check-figures --figures-dir paper/figures/
```

### 自动修正 LaTeX 错误
```bash
python ~/.claude/skills/paper-compilation/scripts/fix_latex_errors.py \
  --tex paper/main.tex --log compile.log --output paper/main_fixed.tex
```

修正：LaTeX 中的 HTML 标签、环境不匹配、缺失图片。关键标志：`--dry-run`，`--auto-detect`

### 带自动修正重试的编译
```bash
python ~/.claude/skills/paper-compilation/scripts/compile_paper.py paper/main.tex --auto-fix
```

运行 `fix_latex_errors.py` + 重新编译，最多 3 轮，直到编译成功。

## 工作流程

### 第 1 步：编译前验证
运行 `validate_citations.py` 以在编译前捕获问题：
- 每个 `\cite{key}` 都有对应的 `.bib` 条目
- 每个 `\includegraphics{file}` 都存在
- 无重复标签或章节

### 第 2 步：编译
运行 `compile_paper.py`，执行：`pdflatex → bibtex → pdflatex → pdflatex`

### 第 3 步：错误修正循环（最多 5 轮）
如果编译失败，读取错误输出并修正：
- `! Undefined control sequence` → 添加缺失的包或修正拼写错误
- `! Missing $ inserted` → 将数学内容包裹在 `$...$` 中
- `! Missing } inserted` → 修正未匹配的大括号
- `Citation 'key' undefined` → 添加到 .bib 或修正 `\cite`
- `</end{figure}>` → 替换为 `\end{figure}`（LaTeX 中的 HTML 语法）

应用最小化修正。不要不必要地移除包。每次修正后重新编译。

### 第 4 步：编译后报告
检查：页数与会议限制对比、剩余警告、chktex 格式问题。

## 故障排除

### pdflatex 未找到
```bash
# macOS
brew install --cask mactex-no-gui
# Ubuntu
sudo apt install texlive-full
```

### 替代方案：latexmk（自动处理多轮编译）
```bash
latexmk -pdf -interaction=nonstopmode main.tex
```

## 相关技能
- 上游：[latex-formatting](../latex-formatting/)，[citation-management](../citation-management/)，[figure-generation](../figure-generation/)，[table-generation](../table-generation/)
- 下游：[self-review](../self-review/)
- 参见：[paper-assembly](../paper-assembly/)
