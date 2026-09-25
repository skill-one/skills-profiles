目标是让测试覆盖所有代码行。

使用以下命令生成覆盖率报告：

```bash
pytest --cov --cov-report=annotate:cov_annotate
```

如果你要检查特定模块的覆盖率，可以像这样指定：

```bash
pytest --cov=your_module_name --cov-report=annotate:cov_annotate
```

你也可以指定要运行的特定测试，例如：

```bash
pytest tests/test_your_module.py --cov=your_module_name --cov-report=annotate:cov_annotate
```

打开 `cov_annotate` 目录查看带注释的源代码。每个源文件都会有一个对应的文件。如果一个文件有 100% 的源代码覆盖率，这意味着所有行都被测试覆盖了，因此你不需要打开该文件。

对于每个测试覆盖率低于 100% 的文件，在 `cov_annotate` 中找到对应的文件并审查该文件。

如果一行以 `!`（感叹号）开头，这意味着该行没有被测试覆盖。为缺失的行添加测试。

持续运行测试并提高覆盖率，直到所有行都被覆盖。
