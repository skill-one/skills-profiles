## 输出风格（纯文字，无连字符，无破折号）

<!-- OUTPUT-STYLE:START -->
将这个技能产生的所有内容，包括文件和消息，都用简单的语言来写。像同事一样，用`你`来和读者交流，温暖直接，并将每一步都作为他们可以运行或跳过的建议，而不是命令。保留具有实际意义的术语；用简单的语言解释每一个。不要使用连字符或破折号作为标点符号：不要使用英文破折号、中文破折号，也不要使用连字符复合词。写`read only`，而不是`read-only`。用简单的语言来表达，或者重写句子。代码、文件路径、命令标志和值与其他技能匹配的保持它们的连字符。使用短句、逗号或括号。清晰比聪明更重要。
<!-- OUTPUT-STYLE:END -->

## 这个技能的作用

角色：一名高级测试工程师，正在编写代码值得的测试套件。测试调用者依赖的内容和实际会破坏某人内容，而不是为了覆盖率数字而写的行。根据每个文件的内容选择策略。拒绝那些锁定在切片中从未打算实现的脚手架的测试。

目标：这个分支中已更改但尚未提交的代码。每个更改的文件都被分类（纯逻辑、组件、API路由、页面/流程）并用正确的策略进行测试。主线程自己编写测试（一个只读的`scout`可能执行大量的文件读取工作）；在控制规范的指导下，测试可以追溯到它的验收标准（步骤7和8）。

不编写应用程序代码。不更新`AGENTS.md`/`CLAUDE.md`上下文文件（`/sync`拥有这些）。

## 询问与行动

- 当`test-preferences.json`存在、工具已安装且存在未提交的源文件时，直接行动，开始编写：不需要询问。
- 每次运行总是询问一件事，即使有偏好设置：在编写后运行套件，还是提供手动指令（步骤7.5）。每次运行的选择不会保存。
- 否则，仅在以下情况下询问：没有`test-preferences.json`（框架；如果页面/流程更改，E2E附加组件才需要）；未安装选定的工具（先确认）；没有未提交的更改（步骤3）；文件数大于15个（步骤1b）。
- 不问范围问题。git工作树定义了范围。

## 产物所有权

- 测试文件（`*.test.ts`、`*.spec.ts`、`test_*.py`、`*_test.go`等），由这个技能创建
- 项目根目录下的`test-preferences.json`，由这个技能创建和维护

---

## 可移植性（任何操作系统，任何代理）

macOS、Linux或Windows上的任何Agent Skills客户端：
- `git`是唯一需要的CLI，到处都一样；按所示运行`git`命令。其他shell片段是POSIX参考，不是字面脚本的引用：不要假设`find`、`grep`、`sed`、`cat`、`test`/`[ ]`、`xargs`、`mkdir -p`或`node -e`存在。使用你代理的跨平台文件工具（读取、搜索/glob、写入），并自己应用分支逻辑，而不是通过shell的`if`/变量/重定向。
- 嵌入文件：相对于这个技能的文件夹进行引用。主线程在编写时（步骤8）将文件夹解析为绝对路径并读取嵌入的文件：`agent-prompt.md`和`writing-guide.md`。
- 没有交互式问题支持？将任何多项选择题都作为纯文本提出，并提供相同的选项。

在下面的Ask块中，每个选项都是`"label": "description"`；通过你代理的选择器（在Claude Code上的`AskUserQuestion`）或作为纯文本呈现。

## 执行

### 预飞行（主线程）

#### 1. 从git确定范围（首先做这个，如果为空，就没有必要问任何东西）

更改但未提交的文件（跨平台git）：
- 跟踪（已暂存+未暂存），排除删除：`git diff --name-only --diff-filter=ACMR HEAD`
- 未跟踪的，并且没有被忽略：`git ls-files --others --exclude-standard`
- 还没有提交（`git diff HEAD`报错）：使用`git diff --name-only --diff-filter=ACMR --cached`。

合并，删除重复项，过滤掉不能测试的文件：
- 测试文件：`*.test.*`、`*.spec.*`、`test_*.py`、`*_test.go`、在`__tests__/`、`e2e/`、`tests/`、`cypress/`下的任何文件
- 配置：`*.config.*`、`.*rc`、`tsconfig*`、`*.json`（逻辑不在JSON中），`Dockerfile`、CI yaml
- 锁文件、`.lock`、生成的/构建输出（`dist/`、`build/`、`.next/`、`coverage/`）
- 样式：`*.css`、`*.scss`、`*.module.css`；只有类型声明的：`*.d.ts`
- 文档和markdown，规范，`design.md`，`test-preferences.json`

剩余的就是范围。为空：转到步骤3。否则继续。

#### 1b. 对每个范围内的文件进行分类

仅根据路径和文件名进行分类，快速；如果确实有歧义，在读取文件时编写时再次标记`logic`并再次标记它。记录每个文件在编写步骤中的类别。

| 路径/文件名中的信号 | 类别 | 测试策略 |
|---|---|---|
| 不是在路由/页面路径下`*.tsx`/`*.jsx`/`*.vue`/`*.svelte` | **组件** | 组件测试（渲染+交互+断言DOM/ARIA） |
| `app/**/page.*`，`pages/**`（不是`pages/api`），`*Screen.*`，`*View.*` | **页面/流程** | E2E候选+组件测试 |
| `app/**/route.*`，`pages/api/**`，`*.controller.*`，`*.handler.*`，`*.resolver.*`，`actions.*` | **api/server** | 集成测试（调用处理器，在边界处模拟） |
| 普通的`.ts`/`.js`/`.py`/`.go`/`.rs`，工具，钩子，服务，领域逻辑 | **逻辑** | 单元测试（输入→输出，边缘情况，错误） |
| `cli.*`，`bin/**`，`*.command.*`，`cmd/**` | **cli** | 集成测试调用命令 |

`E2E_RELEVANT = yes`如果任何文件是**页面/流程**；否则`no`。

大型差异保护：源文件超过15个，一次不要尝试编写所有文件。按类别优先级（逻辑和api/server首先，风险最高，测试成本最低）并询问：

```
Ask: "<N>更改的文件对于一个通过来说太多了。我应该如何集中精力？"  (标题: "范围大小")
- "逻辑 & API优先（推荐）": "现在测试<计数>逻辑/api文件；我会将其余的标记为未覆盖"
- "分批测试": "跨多个通过覆盖所有<N>文件，较慢但完整"
- "让我缩小范围": "我会告诉你哪些文件或目录最重要"
```

单仓库解析：找到每个范围内文件最近的包含`package.json`的文件夹（向上遍历）。不同的根：按根分组（自己的框架，包管理器，测试目录；每个组安装和编写）。一个共享的根（常见情况）：单个项目。记录每个文件在编写步骤中的`packageRoot`。

---

#### 2. 加载偏好设置

读取项目根目录下的`test-preferences.json`（文件工具；“未找到”=没有偏好设置）。根据它是否命名一个`tool`来分支，而不是根据文件是否存在：
- **`tool`已设置**（常见的编写路径）：加载`tool`、`additionalTools`、`e2eTool`、`testDir`、`filePattern`、`packageManager`；跳到步骤5。
- **`tool`是`null`且`gate`已设置**（`GATE_ONLY`）：这个项目在没有测试运行器的情况下通过，这是一个先前的有意选择。不要编写套件，不要安装运行器，不要再次询问，也不要读取`modes/setup.md`。运行项目的类型检查/代码检查门禁，然后停止并报告： "这个项目通过`<gate>`，而不是测试套件。运行了类型检查门禁；使用`/check verify`来确认行为。"
- **没有文件**（`NO_PREFS`，第一次运行）：读取`modes/setup.md`并执行其步骤4（堆栈检测和框架问题），然后返回这里进行步骤5（安装检查），然后执行其步骤6（保存偏好设置），然后继续步骤7。在编写运行中不要读取`modes/setup.md`。
- **格式错误**（一个既没有`tool`也没有`gate`的文件，或无法解析的JSON）：说出来，然后将其视为`NO_PREFS`并再次运行设置，这将覆盖它。

---

#### 3. 没有未提交的更改

范围空：跳过框架问题，告诉工程师，提供后备方案：

```
Ask: "没有找到未提交的源更改。我应该测试什么？"  (标题: "没有更改")
- "上一次提交": "diff HEAD~1..HEAD并测试那个提交更改的内容"
- "特定文件": "我将测试你命名的文件或目录"
- "现在不测试": "停止。我将在我做出更改后运行/test"
```

- 上一次提交：范围 = `git diff --name-only --diff-filter=ACMR HEAD~1 HEAD`，再次运行步骤1b。
- 特定文件：分类命名的文件，继续。
- 什么也不做：干净地停止。

---

#### 5. 安装检查

使用文件工具检查选定的单元工具、E2E工具（如果有）和附加组件：
- JS/TS：在`node_modules/<pkg>`下，或在`package.json`的devDependencies中？
- Python：在`pyproject.toml`/`requirements.txt`（或`pip show <tool>`，如果Python可用）？
- Go：`stretchr/testify`在`go.sum`中？

都存在→步骤6。任何缺失→先确认：

```
Ask: "<missing tools>未安装。现在安装吗？"  (标题: "安装")
- "是，安装并继续": "使用检测到的包管理器运行安装，然后编写测试"
- "不，编写可运行的占位符": "跳过安装；我将编写我可以在我自己安装工具后运行的测试"
```

是：使用检测到的包管理器安装，这里显示为`<pkgmgr>`（检测到的npm / yarn / pnpm / bun；对于Python/Go使用语言的经理）：

```bash
<pkgmgr> add -D vitest                                            # 单元
<pkgmgr> add -D @testing-library/<framework> @testing-library/user-event @testing-library/jest-dom  # 附加
<pkgmgr> add -D @playwright/test && <pkgmgr> exec playwright install  # E2E (Playwright)
<pkgmgr> add -D cypress                                          # E2E (Cypress)
pip install pytest pytest-mock                                    # Python
go get <testify module path>                                      # Go
```

"不"：记录`INSTALL=deferred`；无论如何编写完整的测试，运行命令报告为"安装后运行"。

---

#### 7. 收集轻量级指针（在这里不要读取重文件）

仅路径和廉价信号；重读取发生在编写时（由你，或如果卸载了`scout`子代理，则由`scout`在最低成本模型上执行）。在这里不要读取规范、`design.md`或完整源文件。

使用文件工具：
- 列出`docs/specs/`下最近修改的3个规范路径（仅路径）。
- 确定控制规范：这些文件实现的特性目录`docs/specs/NNNN-<feature>/`（或单个`docs/specs/NNNN-<feature>.md`），通过分支/特性名称或触摸表面匹配（如果存在，`docs/scope/`条目指向它）。记下它的路径和它旁边是否有一个`verify.md`（`docs/specs/NNNN-<feature>/verify.md`）。这个合同是测试追溯到的地方；它可能不在最近的3个路径中。当存在控制规范时，设置`TRACE_TO_CONTRACT = yes`，否则`no`。
- 记录项目根目录下是否存在`design.md`；仅在**组件**或**页面/流程**文件在范围内时使用其路径，否则`none`。
- 读取`AGENTS.md`（规范；如果不存在，则读取`CLAUDE.md`）作为项目上下文（短且廉价）。还记下构建方法作为一行：团队选择的对切片的切片塑造方法，记录在范围标题（或根`AGENTS.md`）中，例如，最薄的端到端路径，最薄的可用整个核心循环，在占位符上的UI首先外壳，每个阶段的全用户旅程。它不会分支逻辑；它校准你在编写时的判断（步骤8，规则a）。
- 读取`package.json`，记下`scripts.test`。`RUN_COMMAND` = `<pkgmgr> test`当存在`test`脚本时（`<pkgmgr> run test`对于npm）；当没有脚本时，使用原始调用（例如`<pkgmgr> exec vitest run`）。

---

#### 7.5 询问是否在编写后运行套件（始终）

```
Ask: "将为<N>个更改的文件编写测试。编写后运行套件吗？"  (标题: "运行测试？")
- "是，运行并修复为绿色": "执行套件；我将修复任何测试错误，并标记测试捕获的真实错误"
- "跳过，只编写它们": "编写测试，并给我手动运行和验证说明"
```

设置`RUN_AFTER = yes | no`并在编写时应用它。

#### 8. 编写套件（主线程）

主线程自己编写测试。不要启动编写者。将这个技能的文件夹解析为绝对路径，现在读取`agent-prompt.md`和`writing-guide.md`（仅在编写时读取）：`agent-prompt.md`是你的操作模板，`writing-guide.md`是你要遵循的策略、工具规则、迭代循环和报告格式。读取测试下的更改文件是唯一昂贵的部分；对于大型或不熟悉的集合，将仅读取工作卸载到只读的`scout`子代理上（在最低成本模型上，Claude Code：`haiku`，不继承会话模型），返回紧凑的映射，然后从它编写。

应用输入（你收集的标记值）：
1. 单元工具、E2E工具、附加工具、`INSTALL`状态；`testDir`、`filePattern`、包管理器、堆栈/框架、`packageRoot`；分类的范围（每个文件路径及其类别：逻辑 / 组件 / 页面流程 / api服务器 / cli）；`RUN_COMMAND`、`RUN_AFTER`；项目上下文加上构建方法行；最近的3个规范路径或`none`（如果相关，则只读）；`design.md`路径或`none`；`TRACE_TO_CONTRACT`、控制规范路径，以及`verify.md`路径（如果不存在，则为`none`）。
2. 两个规则要应用： (a) 让构建方法校准哪些行为对这个切片是持久的真实，将这些锁定为稳定的断言，而不是切片设计上故意伪造的搭建（不要断言计划尚未构建的真实实现，例如，在模拟数据的shell上对真实后端期望）。 (b) 当`TRACE_TO_CONTRACT = yes`时，读取验收标准（如果存在，则从`verify.md`中读取其已解析的`AC-N`-标记清单，否则从规范的`## Requirements`中读取）并锁定持久的断言：对于每个可以锁定为稳定断言的标准，编写一个自动化的测试，每个测试都标记为它覆盖的`AC-N`（例如，带有`covers: AC-3`注释，或测试标题中的`AC-3`），以便套件可以追溯到合同。永远不要伪造无法自动化的标准（视觉/手动/环境，例如“电子邮件实际上到达了”）；将其记录在`NOT_COVERED`中，作为`AC-N, <为什么不能自动化>`→推迟到`/check verify`手动步骤。

单仓库（来自步骤1b的多个包根）：依次编写每个根的套件，范围限制为其根的文件、工具和包管理器（如果大型，则将每个根的文件读取卸载到它自己的`scout`）。单根（常见情况）：只需编写它。

---

### 编写套件后

如果编写失败或未产生报告：说出来并再次尝试；永远不要报告你没有实际产生的通过或失败的套件。否则传递匹配`RUN_AFTER`的格式。

更新范围：如果此功能在范围内（`docs/scope/`）并且套件通过，勾选其`Test it`框，然后**提供`done`，不要门禁它**： "测试已完成且通过，标记它为`done`？" 在工程师的指导下，设置状态`done`（一瞥表格和标题）并镜像规范的`**Status**:` → `Accepted`。一个`Assumed`规范不会阻止`done`；标记它（“欠验证，当你可以时`/architect`”），让他们决定。如果测试失败或覆盖率不完整，留下`Test it`未勾选并报告。**确认更新作为关闭门禁**（不要跳过它）：报告你勾选了每个文件的内容，例如。 "范围：勾选`Test it`，状态→`done`。规范：状态→`Accepted`。" 没有匹配的行→说出来，不要默默完成。在`done`时，建议在下一个功能之前`/clear`：范围和规范包含所有内容，一个新会话使下一个构建廉价。**Git：** 如果最近的`AGENTS.md` `## Git`说`integration: on`且`commit`不是`manual`，提供提交套件，使用一行主题（`test(<scope>): …`）加上`Co-Authored-By`跟踪器；永远不要推送。 （有效层 = 如果设置了功能自己的层标签，否则项目`**Workflow:**`默认。`/test`在`Beta`/`GA`上更近；`Prototype`在`/develop`上关闭，`Alpha`在`/check verify`上关闭，等等，这个功能已经`done`或不使用`/test`。尊重覆盖标签；永远不要默认为固定链。）

以结果为先；每个文件的列表和AC可追溯性都在测试文件中（每`docs/conventions.md`）。模板：

```
## /test <feature> Â· <all N passed | Y failed | not run>

**跨<M>个文件编写了<N>个测试（快乐路径 / 边缘情况 / 错误 / a11y）。<X passed, Y failed via `<RUN_COMMAND>` | not run>.**
下一步（这个功能在范围内的下一个未勾选的框）：所有通过→如果`Review it`框仍然存在，则`/check review`，否则`/sync`或下一个功能 · Y failed → 修复它们，或`/debug <feature>`如果代码是错误的 · not run → `<RUN_COMMAND>`
提醒：<测试捕获的错误 Â· 文件:行 + 失败的期望> · <未覆盖的AC-N或区域，为什么>   （如果没有任何内容，则省略整行）
```

仅在`RUN_AFTER = no`时，附加运行步骤：`<setup if INSTALL=deferred>`然后`<RUN_COMMAND>`（用`<focused command>`监视一个文件）。框架选择在`test-preferences.json`中；每个测试的详细信息和AC可追溯性存在于测试文件中，所以不要重新打印它们。

**未覆盖**（考虑添加）：
- <差距和原因>
- AC-N, <无法自动化的标准（视觉/手动/环境)> → 推迟到`/check verify`手动步骤   ← 当TRACE_TO_CONTRACT=yes
```

如果`BUGS_FOUND`不为空，以它为先：一个在真实损坏的代码上正确失败的测试是一个真正的发现，不是要压制的东西。/test不会修改应用程序代码以使测试通过。

这个技能在传递报告后完成：它不会调用其他技能。

---

## 参考文件（在这个技能的文件夹中；通过相对路径引用）

- `modes/setup.md`：第一次运行时仅步骤（堆栈检测，框架问题，保存偏好设置）；仅在`NO_PREFS`时由主线程读取
- `agent-prompt.md`：主线程在编写时（步骤8）读取的操作模板
- `writing-guide.md`：策略，工具规则，迭代循环，报告格式；主线程在编写时也读取它
