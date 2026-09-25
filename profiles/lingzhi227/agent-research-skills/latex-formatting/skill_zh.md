# LaTeX 格式化

设置和管理学术论文的 LaTeX 格式。

## 输入

- `$0` — 操作：`setup`、`fix`、`check`
- `$1` — 会议名称（用于 `setup`）或 `.tex` 文件路径（用于 `fix`/`check`）

## 脚本

### 提交前格式检查器
```bash
python ~/.claude/skills/latex-formatting/scripts/latex_checker.py paper/main.tex --venue neurips --check-anon
```

检查内容：字数、必需章节、TODO 标记、匿名化、环境不匹配、内容统计。

### 验证引用和参考文献
```bash
python ~/.claude/skills/citation-management/scripts/validate_citations.py \
  --tex paper/main.tex --bib paper/references.bib --check-figures
```

### 清理 LaTeX 文本（修复特殊字符）
```bash
python ~/.claude/skills/latex-formatting/scripts/clean_latex.py \
  --input paper/main.tex --output paper/main_cleaned.tex
```

将特殊/非 UTF-8 字符替换为 LaTeX 对应字符，跳过数学环境。
关键标志：`--dry-run`、`--tables-only`

### 检查后自动修复
```bash
python ~/.claude/skills/latex-formatting/scripts/latex_checker.py paper/main.tex --venue neurips --fix
```

运行检查后应用 clean_latex.py 修复，写入 `main_fixed.tex`。

## 参考

- 会议规范、项目结构、包、命令：`~/.claude/skills/latex-formatting/references/venue-templates.md`

## 操作：`setup`
创建指定会议的项目目录结构和 main.tex。使用 `references/venue-templates.md` 中的模板。

## 操作：`fix`
修复常见的 LaTeX 问题：未转义的特殊字符、数学模式错误、浮动位置、过满/不满框、交叉引用问题。

## 操作：`check`
运行 `latex_checker.py` 进行提交前验证。检查页数、匿名化、必需章节、TODO 标记。

## 相关技能
- 上游：[论文写作部分](../paper-writing-section/)、[表格生成](../table-generation/)
- 下游：[论文编译](../paper-compilation/)
- 参见：[引用管理](../citation-management/)
