# 身份审计工作流

在检查函数、文件或文件夹名称是否仍与其内容匹配时使用此技能。

CLI 扫描文件、文件夹和图级别的声明符号。它不会将每个局部变量、参数或字段视为独立的命名目标；这些仍会影响包含它们的文件摘要。文件名会结合父作用域进行评估，声明密集型文件通常应被视为证据薄弱，直到后续检查证明存在实际重命名或拆分。

## 管道

1. 运行机械扫描：

   ```bash
   indexion identity audit .
   ```

   对于机器可读的队列：

   ```bash
   indexion identity audit --format=json --output=.indexion/cache/identity/report.json .
   ```

2. 将每行视为审查候选，而非证明。比较：

   - `name`：身份包推断的作用域名称
   - `expected_summary`：路径/名称/作用域预测的内容
   - `actual_summary`：基于图的声明、文档、模块注释和路径术语
   - `assessment`：是否为实际漂移、内容过于宽泛或内容不足
   - `recommendation`：验证的第一步操作

3. 编辑前验证：

   ```bash
   indexion doc graph --format=text <path>
   indexion grep --semantic=name:<symbol> .
   rg "<name-or-term>" <path>
   ```

4. 选择最小的确认操作：

   - 将 `insufficient-content` 视为证据问题，而非命名漂移证明。
     在重命名前检查文件是否有意声明/轻薄、不被图提取器支持、为空或缺少文档/声明材料。
   - 当符号实现连贯但名称过时时重命名符号。
   - 当声明连贯但文件名过时时重命名文件。
   - 当包含文件共享更清晰的父概念时重命名文件夹。
   - 当文件比当前文件夹更适合时移动文件。
   - 当候选文件显示多个主导职责时拆分文件。

5. 修改后：

   ```bash
   moon info && moon fmt
   moon test
   indexion identity audit .
   ```

审计旨在暴露审查工作。不要机械地最大化分数；先验证实际代码所有权和引用。
