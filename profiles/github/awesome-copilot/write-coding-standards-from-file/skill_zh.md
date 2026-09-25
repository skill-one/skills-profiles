# 从文件编写编码规范

使用文件（夹）的现有语法来建立项目的标准和风格指南。如果传递了多个文件或一个文件夹，则遍历文件夹中的每个文件，将文件数据追加到临时内存或文件中，然后完成时使用临时数据作为单个实例；就像以文件名为基础来建立标准和风格指南一样。

## 规则和配置

下面是一组准配置 `boolean` 和 `string[]` 变量。处理 `true` 或每个变量其他值的条件在二级标题 `## 变量和参数配置条件` 下。

提示参数具有文本定义。有一个必需参数 **`${fileName}`**，以及几个可选参数 **`${folderName}`**、**`${instructions}`** 和任何 **`[configVariableAsParameter]`**。

### 配置变量

* addStandardsTest = false;
* addToREADME = false;
* addToREADMEInsertions = ["atBegin", "middle", "beforeEnd", "bestFitUsingContext"];
  - 默认为 **beforeEnd**。
* createNewFile = true;
* fetchStyleURL = true;
* findInconsistencies = true;
* fixInconsistencies = true;
* newFileName = ["CONTRIBUTING.md", "STYLE.md", "CODE_OF_CONDUCT.md", "CODING_STANDARDS.md", "DEVELOPING.md", "CONTRIBUTION_GUIDE.md", "GUIDELINES.md", "PROJECT_STANDARDS.md", "BEST_PRACTICES.md", "HACKING.md"];
  - 对于 `${newFileName}` 中的每个文件名，如果文件不存在，则使用该文件名并 `break`，否则继续下一个 `${newFileName}` 中的文件名。
* outputSpecToPrompt = false;
* useTemplate = "verbose"; // 或 "v"
  - 可能的值是 `[["v", "verbose"], ["m", "minimal"], ["b", "best fit"], ["custom"]]`。
  - 选择提示文件底部在二级标题 `## 编码标准模板` 下提供的两个示例模板之一，或使用更适合的其他组合。
  - 如果 **custom**，则根据请求应用。

### 配置变量作为提示参数

如果任何变量名按原样传递给提示，或传递一个类似但明显相关的文本值，则用传递给提示的值覆盖默认变量值。

### 提示参数

* **fileName** = 将要分析的文件名，包括：缩进、变量命名、注释、条件过程、功能过程以及与文件编码语言相关的其他语法数据。
* folderName = 将要用于从多个文件中提取数据到一个聚合数据集的文件夹名，该数据集将根据：缩进、变量命名、注释、条件过程、功能过程以及与文件编码语言相关的其他语法数据进行分析。
* instructions = 将提供的附加指令、规则和程序，用于处理特殊情况。
* [configVariableAsParameter] = 如果传递，将覆盖配置变量的默认状态。示例：
  - useTemplate = 如果传递，将覆盖 `${useTemplate}` 的默认值。值是 `[["v", "verbose"], ["m", "minimal"], ["b", "best fit"]]`。

#### 必需和可选参数

* **fileName** - 必需
* folderName - *可选*
* instructions - *可选*
* [configVariableAsParameter] - *可选*

## 变量和参数配置条件

### `${fileName}.length > 1 || ${folderName} != undefined`

* 如果为 true，则将 `${fixInconsistencies}` 切换为 false。

### `${addToREADME} == true`

* 将编码标准插入 `README.md` 而不是输出到提示或创建新文件。
* 如果为 true，则将 `${createNewFile}` 和 `${outputSpecToPrompt}` 都切换为 false。

### `${addToREADMEInsertions} == "atBegin"`

* 如果 `${addToREADME}` 为 true，则将编码标准数据插入 `README.md` 文件的标题后的**开头**。

### `${addToREADMEInsertions} == "middle"`

* 如果 `${addToREADME}` 为 true，则将编码标准数据插入 `README.md` 文件的**中间**，并将标准标题标题更改为与 `README.md` 组成相匹配。

### `${addToREADMEInsertions} == "beforeEnd"`

* 如果 `${addToREADME}` 为 true，则将编码标准数据插入 `README.md` 文件的**末尾**，在最后一个字符后插入一个新行，然后在新行中插入数据。

### `${addToREADMEInsertions} == "bestFitUsingContext"`

* 如果 `${addToREADME}` 为 true，则根据 `README.md` 组成和数据的流程，将编码标准数据插入 `README.md` 文件的**最佳匹配行**。

### `${addStandardsTest} == true`

* 编码标准文件完成后，编写一个测试文件以确保传递给它的文件或文件遵守编码标准。

### `${createNewFile} == true`

* 使用 `${newFileName}` 的值或其中一个可能的值创建一个新文件。
* 如果为 true，则将 `${outputSpecToPrompt}` 和 `${addToREADME}` 都切换为 false。

### `${fetchStyleURL} == true`

* 此外，使用嵌套在三级标题 `### Fetch Links` 下的链接获取的数据作为创建标准、规范和样式数据的上下文，用于新文件、提示或 `README.md`。
* 对于 `### Fetch Links` 中的每个相关项，运行 `#fetch ${item}`。

### `${findInconsistencies} == true`

* 评估与缩进、换行符、注释、条件和功能嵌套、字符串引号包装（即 `'` 或 `"`）等相关的语法，并进行分类。
* 对于每个类别，进行计数，如果一个项目与多数计数不匹配，则将其提交到临时内存。
* 根据`${fixInconsistencies}`的状态，要么编辑和修复少数计数的类别以匹配多数，要么将存储在临时内存中的不一致性输出到提示。

### `${fixInconsistencies} == true`

* 使用存储在临时内存中的不一致性，编辑和修复少数计数的语法数据类别以匹配相应的多数语法数据。

### `typeof ${newFileName} == "string"`

* 如果明确定义为 `string`，则使用 `${newFileName}` 的值创建一个新文件。

### `typeof ${newFileName} != "string"`

* 如果**不是**明确定义为 `string`，而是一个 `object` 或数组，则通过应用此规则从 `${newFileName}` 中创建一个新文件：
  - 对于 `${newFileName}` 中的每个文件名，如果文件不存在，则使用该文件名并 `break`，否则继续下一个。

### `${outputSpecToPrompt} == true`

* 将编码标准输出到提示，而不是创建文件或添加到 README。
* 如果为 true，则将 `${createNewFile}` 和 `${addToREADME}` 都切换为 false。

### `${useTemplate} == "v" || ${useTemplate} == "verbose"`

* 使用三级标题 `### "v", "verbose"` 下面的数据作为编写编码标准数据时的指导模板。

### `${useTemplate} == "m" || ${useTemplate} == "minimal"`

* 使用三级标题 `### "m", "minimal"` 下面的数据作为编写编码标准数据时的指导模板。

### `${useTemplate} == "b" || ${useTemplate} == "best"`

* 使用三级标题 `### "v", "verbose"` 或 `### "m", "minimal"` 下的数据，根据从 `${fileName}` 提取的数据，并使用最佳匹配作为编写编码标准数据时的指导模板。

### `${useTemplate} == "custom" || ${useTemplate} == "<ANY_NAME>"`

* 使用传递的自定义提示、指令、模板或其他数据作为编写编码标准数据时的指导模板。

## **if** `${fetchStyleURL} == true`

根据编程语言，对于下面的列表中的每个链接，如果编程语言是 `${fileName} == [<Language> Style Guide]`，则运行 `#fetch (URL)`。

### Fetch Links

- [C Style Guide](https://users.ece.cmu.edu/~eno/coding/CCodingStandard.html)
- [C# Style Guide](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)
- [C++ Style Guide](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)
- [Go Style Guide](https://github.com/golang-standards/project-layout)
- [Java Style Guide](https://coderanch.com/wiki/718799/Style)
- [AngularJS App Style Guide](https://github.com/mgechev/angularjs-style-guide)
- [jQuery Style Guide](https://contribute.jquery.org/style-guide/js/)
- [JavaScript Style Guide](https://www.w3schools.com/js/js_conventions.asp)
- [JSON Style Guide](https://google.github.io/styleguide/jsoncstyleguide.xml)
- [Kotlin Style Guide](https://kotlinlang.org/docs/coding-conventions.html)
- [Markdown Style Guide](https://cirosantilli.com/markdown-style-guide/)
- [Perl Style Guide](https://perldoc.perl.org/perlstyle)
- [PHP Style Guide](https://phptherightway.com/)
- [Python Style Guide](https://peps.python.org/pep-0008/)
- [Ruby Style Guide](https://rubystyle.guide/)
- [Rust Style Guide](https://github.com/rust-lang/rust/tree/HEAD/src/doc/style-guide/src)
- [Swift Style Guide](https://www.swift.org/documentation/api-design-guidelines/)
- [TypeScript Style Guide](https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html)
- [Visual Basic Style Guide](https://en.wikibooks.org/wiki/Visual_Basic/Coding_Standards)
- [Shell Script Style Guide](https://google.github.io/styleguide/shellguide.html)
- [Git Usage Style Guide](https://github.com/agis/git-style-guide)
- [PowerShell Style Guide](https://github.com/PoshCode/PowerShellPracticeAndStyle)
- [CSS](https://cssguidelin.es/)
- [Sass Style Guide](https://sass-guidelin.es/)
- [HTML Style Guide](https://github.com/marcobiedermann/html-style-guide)
- [Linux kernel Style Guide](https://www.kernel.org/doc/html/latest/process/coding-style.html)
- [Node.js Style Guide](https://github.com/felixge/node-style-guide)
- [SQL Style Guide](https://www.sqlstyle.guide/)
- [Angular Style Guide](https://angular.dev/style-guide)
- [Vue Style Guide](https://vuejs.org/style-guide/rules-strongly-recommended.html)
- [Django Style Guide](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/)
- [SystemVerilog Style Guide](https://github.com/lowRISC/style-guides/blob/master/VerilogCodingStyle.md)

## 编码标准模板

### `"m", "minimal"`

```text
    ```markdown
    ## 1. 简介
    *   **目的**：简要解释为什么建立编码标准（例如，以提高代码质量、可维护性和团队协作）。
    *   **范围**：定义此规范适用于哪些语言、项目或模块。

    ## 2. 命名约定
    *   **变量**：`camelCase`
    *   **函数/方法**：`PascalCase` 或 `camelCase`。
    *   **类/结构**：`PascalCase`。
    *   **常量**：`UPPER_SNAKE_CASE`。

    ## 3. 格式化和风格
    *   **缩进**：每个缩进使用 4 个空格（或制表符）。
    *   **行长度**：限制行长度最多为 80 或 120 个字符。
    *   **括号**：使用 "K&R" 风格（开括号在同一行）或 "Allman" 风格（开括号在新行）。
    *   **空行**：指定用于分隔代码逻辑块应使用的空行数。

    ## 4. 注释
    *   **文档字符串/函数注释**：描述函数的用途、参数和返回值。
    *   **行内注释**：解释复杂或不明显的逻辑。
    *   **文件头**：指定文件头应包含的信息，例如作者、日期和文件描述。

    ## 5. 错误处理
    *   **一般**：如何处理和记录错误。
    *   **具体**：使用哪些异常类型，以及错误消息中应包含哪些信息。

    ## 6. 最佳实践和反模式
    *   **一般**：列出要避免的常见反模式（例如，全局变量、魔法数字）。
    *   **语言特定**：基于项目编程语言的特定建议。

    ## 7. 示例
    *   提供一个小的代码示例，演示如何正确应用规则。
    *   提供一个小的代码示例，演示不正确的实现以及如何修复它。

    ## 8. 贡献和执行
    *   解释如何执行标准（例如，通过代码审查）。
    *   提供一个指南，说明如何为标准文档本身做出贡献。
    ```
```

### `"v", verbose"`

```text
    ```markdown

    # 风格指南

    本文件定义了此项目中使用的风格和约定。
    所有贡献都应遵循这些规则，除非另有说明。

    ## 1. 通用代码风格

    - 倾向于清晰而不是简洁。
    - 保持函数和方法小而专注。
    - 避免重复逻辑；优先选择共享的辅助工具/实用程序。
    - 删除未使用的变量、导入、代码路径和文件。

    ## 2. 命名约定

    使用描述性名称。除非众所周知，否则避免缩写。

    | 项目            | 约定           | 示例            |
    |-----------------|----------------|--------------------|
    | 变量       | `lower_snake_case`   | `buffer_size`      |
    | 函数       | `lower_snake_case()` | `read_file()`      |
    | 常量       | `UPPER_SNAKE_CASE`   | `MAX_RETRIES`      |
    | 类型/结构   | `PascalCase`         | `FileHeader`       |
    | 文件名      | `lower_snake_case`   | `file_reader.c`    |

    ## 3. 格式规则

    - 缩进: **4 个空格**
    - 行长度: **最大 100 个字符**
    - 编码: **UTF-8**，无 BOM
    - 文件以换行符结尾

    ### 括号（C 语言示例，根据您的语言进行调整）

        ```c
        if (condition) {
            do_something();
        } else {
            do_something_else();
        }
        ```

    ### 间距

    - 关键字后一个空格：`if (x)`，不是 `if(x)`
    - 顶级函数之间一个空行

    ## 4. 注释和文档

    - 解释*为什么*，而不是*什么*，除非意图不明确。
    - 随着代码的变化，保持注释更新。
    - 公共函数应包括对目的和参数的简短描述。

    推荐标签：

        ```text
        TODO: 后续工作
        FIXME: 已知的错误行为
        NOTE: 非明显的设计决策
        ```

    ## 5. 错误处理

    - 明确处理错误条件。
    - 避免静默失败；要么返回错误，要么适当地记录它们。
    - 在失败时清理资源（文件、内存、句柄）。

    ## 6. 提交和审查实践

    ### 提交
    - 每次提交一个逻辑更改。
    - 编写清晰的提交信息：

        ```text
        简短摘要（最大 ~50 个字符）
        可选的较长解释，说明上下文和原因。
        ```

    ### 审查
    - 保持拉取请求合理大小。
    - 在审查讨论中保持尊重和建设性。
    - 解决请求的更改，或者如果您不同意，请解释。

    ## 7. 测试

    - 为新功能编写测试。
    - 测试应该是确定性的（如果没有种子，则没有随机性）。
    - 优先选择可读的测试用例，而不是复杂的测试抽象。

    ## 8. 此指南的更改

    风格在演变。
    通过打开问题或发送更新此文档的补丁来提议改进。
    ```
```
