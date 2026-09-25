# 向后可追溯性

使最终 PDF 中的每个数字都成为超链接，链接到生成它的确切代码行。

## 输入

- `$0` — 包含代码和 LaTeX 文件的论文项目目录

## 参考文献

- 可追溯性模式和 LaTeX 命令：`~/.claude/skills/backward-traceability/references/traceability-patterns.md`

## 脚本

### 扫描超目标/超链接引用
```bash
python ~/.claude/skills/backward-traceability/scripts/ref_numeric_values.py \
  --scan paper/main.tex --output report.json
```

报告：所有超目标、超链接、孤儿引用、未引用的数值。

### 验证交叉引用完整性
```bash
python ~/.claude/skills/backward-traceability/scripts/ref_numeric_values.py \
  --verify paper/main.tex --code-output results.txt
```

在论文文本和代码输出之间进行交叉检查。报告不匹配项。

## 工作流程

### 第 1 步：标记代码输出
对于实验代码生成的每个数值，添加超目标标签：

```python
# 在实验代码输出中：
print(f"\\hypertarget{{R1a}}{{45.3}}")  # 平均准确率
print(f"\\hypertarget{{R1b}}{{2.1}}")   # 标准差
```

标签格式：`{prefix}{line_number}{letter}`，其中字母 = a、b、c... 用于同一行上的多个值。

### 第 2 步：在论文文本中引用
使用 `\hyperlink` 在论文中创建可点击的引用：

```latex
我们的方法达到了 \hyperlink{R1a}{45.3}\% 准确率
($\pm$\hyperlink{R1b}{2.1}$)$。
```

### 第 3 步：使用 \num 对计算值进行引用
对于从其他值派生的值，使用 `\num{}` 进行编译时计算：

```latex
% \num{formula, "explanation"} → 在编译时计算
改进为 \num{45.3 - 38.7, "准确率提升"}\%。
```

### 第 4 步：生成附录代码列表
创建一个附录，包含完整的代码列表，并在相关行添加 `\hypertarget` 锚点：

```latex
\section*{附录：代码列表}
\begin{lstlisting}[escapechar=@]
@\hypertarget{code1}{}@result = model.evaluate(test_data)
@\hypertarget{code2}{}@accuracy = result['accuracy']
\end{lstlisting}
```

### 第 5 步：验证可追溯性
- 论文文本中的每个数字都必须在代码中有对应的 `\hypertarget`
- 每个 `\num{}` 公式都必须正确计算
- 点击测试：PDF 中的每个超链接都必须跳转到正确的代码行

## LaTeX 设置

所需包：
```latex
\usepackage{hyperref}
\usepackage{listings}
```

## 规则

- 论文中的每个数值结果必须可追溯到代码输出
- 不要手动输入数字 — 始终引用标记的输出
- 使用 `\num{}` 对任何派生/计算值进行引用
- 附录中的代码列表必须与实际执行的代码匹配
- 编译后验证所有超链接是否正确解析

## 相关技能
- 上游：[experiment-code](../experiment-code/)、[data-analysis](../data-analysis/)
- 下游：[paper-compilation](../paper-compilation/)
- 参见：[paper-assembly](../paper-assembly/)
