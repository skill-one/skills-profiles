# indexion重构 — 代码库重构

使用indexion的分析命令检测并消除三个层面的重复 — 文本层面、结构层面和概念层面 — 然后验证SoT是否得到强制执行。

## 何时使用

- 添加新的抽象（类型、模块、API层）之后
- 引入新的文件格式或I/O边界之后
- 由于相同原因需要修改3个以上文件时
- 添加了"guard"或"skip"来绕过结构问题时
- 出现来自意外路径的`opendir`、`ENOENT`或类似的文件系统错误时
- 在包之间提取共享代码时
- 重构清理后（移除琐碎的包装函数时）
- 代码库的周期性SoT健康检查时

## 三个层面的重复

| 层级 | 定义 | 工具 | 示例 |
|------|------|------|------|
| **文本层面** | 复制粘贴的代码块、相同的函数 | `plan refactor` | `is_whitespace`在5个模块中复制 |
| **结构层面** | 具有不同名称的相同逻辑结构 | `plan solid`、`plan unwrap` | 跨包提取候选、琐碎的包装函数 |
| **概念层面** | 独立实现的相同领域概念 | `explore` + 手动分析 | 三个模块各自判断"这个文件是存档吗？" |

文本层面的重复很容易发现和修复。概念层面的重复是最难和最危险的 — 它不会产生复制粘贴的匹配，但意味着更改一个概念需要更新所有分散的实现。

## 工作流程

### 第一阶段：清除文本层面的重复 (`plan refactor`)

从高置信度的匹配开始，逐步向下处理。

```bash
# 第一步：查找90%+的重复（高置信度）
indexion plan refactor --threshold=0.9 \
  --include='*.mbt' --exclude='*_wbtest.mbt' \
  --exclude='*moon.pkg*' --exclude='*pkg.generated*' \
  cmd/indexion/

indexion plan refactor --threshold=0.9 \
  --include='*.mbt' --exclude='*_wbtest.mbt' \
  --exclude='*moon.pkg*' --exclude='*pkg.generated*' \
  src/
```

**分三部分阅读输出：**

| 部分 | 查找内容 | 操作 |
|------|----------|------|
| 相似文件 | 高度相似的文件 | 调查结构整合 |
| 重复代码块 | 文件之间行级相同的代码 | 提取到`@common`或共享模块 |
| 函数级重复 | 结构相似的函数（基于函数体的TF-IDF） | 合并为一个SoT函数 |

**同文件重复**（90%+的函数在一个文件内）是最高价值的靶点 — 容易修复，收益最明显。示例：`get_global_data_dir`和`get_global_cache_dir`共享95%的结构，提取到`resolve_os_dir`。

```bash
# 第二步：使用grep在整合前跟踪引用
indexion grep "TypeIdent:TfidfEmbeddingProvider" src/
indexion grep --semantic=name:is_whitespace src/

# 第三步：修复，然后重新运行以确认重复已消失
indexion plan refactor --threshold=0.9 --include='*.mbt' ...

# 第四步：降低阈值并迭代
indexion plan refactor --threshold=0.85 --include='*.mbt' ...
```

**`plan refactor`选项：**

| 选项 | 默认值 | 描述 |
|------|--------|------|
| `--threshold=FLOAT` | 0.7 | 最小相似度阈值 |
| `--strategy=NAME` | hybrid | 相似度：hybrid、tfidf、bm25、jsd、ncd |
| `--fdr=FLOAT` | 0 | FDR校正（0=禁用） |
| `--style=STYLE` | raw | 输出：raw、structured |
| `--format=FORMAT` | md | 输出：md、json、text、github-issue |
| `--name=NAME` | -- | 项目名称（用于structured风格） |
| `--include=PATTERN` | -- | 包含模式（可重复） |
| `--exclude=PATTERN` | -- | 排除模式（可重复） |
| `-o, --output=FILE` | stdout | 输出文件路径 |
| `--specs-dir=DIR` | kgfs | KGF规范目录 |

**清理后剩余的内容（停止信号）：**

- **平台桩** (`native.mbt` / `stub.mbt`) — 故意的平台分支
- **类型方法相似性** (`to_string`在不同类型上) — 不同类型，相同模式
- **CLI命令模板** (`command()`函数) — @argparse API模式，不是重复
- **语义不同**的函数 (`is_disqualifying_keyword` vs `is_skip_token`) — 不同目的

### 第二阶段：提取跨包共享代码 (`plan solid`)

在每个目录内部清理后，查找应该跨包共享的代码。

```bash
# 查找两个包之间的重叠
indexion plan solid --from=src/a,src/b

# 指定提取目标
indexion plan solid --from=src/a,src/b --to=src/common

# 使用树编辑距离进行精确的函数级匹配
indexion plan solid --from=src/a,src/b --strategy=apted

# 更高阈值进行更严格的匹配
indexion plan solid --from=src/a,src/b --threshold=0.95

# 过滤文件
indexion plan solid --from=src/a,src/b --include='*.mbt' --exclude='*_test.mbt'
```

`plan solid`与`plan refactor`不同：

| | `plan refactor` | `plan solid` |
|---|-----------------|-------------|
| 范围 | 目录内部的内部重复 | 跨目录重叠 |
| 目标 | 在代码库内整合 | 提取共享代码到新包 |
| 输入 | `<路径>` | `--from=dirA,dirB` |

**`plan solid`选项：**

| 选项 | 默认值 | 描述 |
|------|--------|------|
| `--from=DIRS` | (必需) | 源目录（逗号分隔或可重复） |
| `--to=DIR` | -- | 提取的目标目录 |
| `--rules=FILE` | -- | 规则文件 (.solidrc) |
| `--rule=RULE` | -- | 内联规则（可重复） |
| `--threshold=FLOAT` | 0.9 | 最小相似度阈值 |
| `--strategy=NAME` | tfidf | 相似度：tfidf、apted、tsed |
| `--include=PATTERN` | -- | 包含模式（可重复） |
| `--exclude=PATTERN` | -- | 排除模式（可重复） |
| `--format=FORMAT` | md | 输出：md、json、github-issue |
| `-o, --output=FILE` | stdout | 输出文件路径 |
| `--specs-dir=DIR` | kgfs | KGF规范目录 |

**工作流程：**

1. 首先在每个目录上单独运行`plan refactor`以清理内部重复
2. 运行`plan solid --from=dirA,dirB`以查找跨目录提取候选
3. 按照计划的建议提取共享代码
4. 使用`indexion grep "TypeIdent:SharedType"`验证所有引用是否已更新

### 第三阶段：移除不必要的包装 (`plan unwrap`)

整合后，清理添加了无价值间接性的琐碎委托函数。

```bash
# 第一步：快速检查
indexion grep --semantic=proxy src/

# 第二步：详细报告
indexion plan unwrap --include='*.mbt' --exclude='*_wbtest.mbt' \
  --exclude='*moon.pkg*' --exclude='*pkg.generated*' src/

# 第三步：预览更改（安全 — 不会修改文件）
indexion plan unwrap --dry-run --include='*.mbt' --exclude='*_wbtest.mbt' \
  --exclude='*moon.pkg*' --exclude='*pkg.generated*' src/

# 第四步：应用修复
indexion plan unwrap --fix --include='*.mbt' --exclude='*_wbtest.mbt' \
  --exclude='*moon.pkg*' --exclude='*pkg.generated*' src/

# 第五步：运行测试
moon test --target native
```

**检测到的内容：** 函数体是一个简单的函数调用，所有参数作为简单标识符转发 — 没有控制流，没有转换。

```moonbit
// 检测到（默认）— 简单的委托
fn matches_pattern(text : String, pat : String) -> Bool {
  @glob.glob_match(text, pat)
}

// 默认排除（使用--all包含）
fn length(self : MyList) -> Int {
  self.items.length()    // 自委托（封装）
}
fn emit(value : String) -> Action {
  Emit(value)            // 空构造函数
}
```

**`plan unwrap`模式：**

| 模式 | 标志 | 描述 |
|------|------|------|
| 报告 | (默认) | 列出找到的包装器 |
| 预览 | `--dry-run` | 显示所有编辑而不修改文件 |
| 修复 | `--fix` | 应用编辑 |

**`plan unwrap`选项：**

| 选项 | 默认值 | 描述 |
|------|--------|------|
| `--dry-run` | -- | 预览编辑 |
| `--fix` | -- | 应用编辑 |
| `--all` | -- | 包含自委托和空构造函数包装器 |
| `--include-self` | -- | 包含`self.field.method`模式 |
| `--include-bare` | -- | 包含空构造函数包装器 |
| `--include=PATTERN` | -- | 包含模式（可重复） |
| `--exclude=PATTERN` | -- | 排除模式（可重复） |
| `--format=FORMAT` | md | 输出：md、json、text |
| `-o, --output=FILE` | stdout | 输出文件路径 |
| `--specs-dir=DIR` | kgfs | KGF规范目录 |

**移除前审查：**

- **平台包装器** (FFI、`@osenv_path`) 是抽象层，不是偶然的间接性
- **公共API包装器**被外部包使用 — 移除它们会破坏API
- **始终`--dry-run`首先**

### 第四阶段：检测概念层面的重复 (`explore` + 分析)

这是最难的一级。文本和结构工具找不到它，因为代码是不同的 — 但*概念*是相同的。

```bash
# 查找共享词汇的文件（= 在同一概念领域工作）
indexion explore --threshold=0.4 \
  --include='*.mbt' --exclude='*_wbtest.mbt' \
  --exclude='*moon.pkg*' --exclude='*pkg.generated*' \
  src/ cmd/
```

40-60%相似度且没有结构重复的文件是**概念邻居** — 它们使用相同的术语，因为它们处理相同的领域。

对于每个高相似度对，问：**"它们共享什么概念？谁拥有它？"**

```bash
# 使用树结构比较检查共享词汇
indexion explore file_a.mbt file_b.mbt --threshold=0 --strategy=apted
```

**常见的概念泄漏模式：**

| 症状 | 泄露的概念 | 修复 |
|------|------------|------|
| 两个文件都调用`is_X(spec)`然后`Y::from_spec(spec)` | "判断X并配置Y" | 将`try_do_X(path, spec)`提取到拥有X的模块 |
| 两个文件都`@fs.read_file_to_string(path)`当内容已加载 | "读取文件内容" | 将内容作为参数传递，不要重新读取 |
| 两个文件都`parent_dir(path)`然后`@fs.read_dir(dir)` | "列出兄弟文件" | 将目录遍历集中到管道 |
| 多个`if is_virtual_path(x) { skip }`守卫 | "真实与虚拟路径" | 使类型系统防止虚拟路径到达这里 |
| 两个文件都`buf.write_string("\n"); buf.write_string(x)` | "连接文本条目" | 将`join_text_entries()`提取到拥有模块 |

### 第五阶段：整合到SoT

定义概念的模块应该是唯一实现逻辑的模块。

规则：
1. **一个概念，一个模块，一个函数。** 如果"从存档中提取文本"出现在`vfs.mbt`、`discover.mbt`和`args.mbt`中，它只应该属于`vfs.mbt`。
2. **调用者接收结果，而不是原料。** 不要单独导出`is_archive_spec` + `ArchiveSpec::from_spec` + `expand_archive`。导出`try_extract_archive_text(path, spec) -> String?`。
3. **守卫是症状，不是修复。** `if is_virtual_path(x) { skip }`意味着虚拟路径根本不应该到达这里。修复源，而不是接收端。
4. **从磁盘重新读取已经在内存中的内容是概念泄漏。** 如果`SupportedFile.content`持有文本，下游代码不应调用`@fs.read_file_to_string(file.path)`。

### 第六阶段：验证

```bash
# 确认文本重复已消失
indexion plan refactor --threshold=0.9 \
  --include='*.mbt' --exclude='*_wbtest.mbt' \
  --exclude='*moon.pkg*' --exclude='*pkg.generated*' \
  src/ cmd/indexion/

# 确认概念相似度降低
indexion explore file_a.mbt file_b.mbt --threshold=0

# 确认包装器已清理
indexion plan unwrap --include='*.mbt' --exclude='*_wbtest.mbt' \
  --exclude='*moon.pkg*' --exclude='*pkg.generated*' src/

# 运行测试
moon test --target native
```

SoT整合后：
- 概念所有者和调用者之间的文本相似度下降
- 调用者变短（一个API调用而不是多步逻辑）
- 概念所有者可能会增长，但它是**唯一需要更改的地方**

### 第七阶段：用测试证明非重复

编写一个测试来**结构性地防止**旧模式再次发生：

```moonbit
test "SoT: SupportedFile.path始终是真实的文件系统路径" {
  // 创建一个存档，运行load_supported_file_info
  // 断言：没有路径包含"!/"
  // 断言：每个路径都通过@fs.path_exists
}
```

测试不检查行为 — 它检查**SoT不变式**。

## 信号灯

### "我需要在这里添加一个守卫"

如果你在一个不应该接收特殊情况的函数中添加`if is_special_case(x) { skip }`，**问题在上游**。调用者永远不会传递该值。

### "它工作，但打印了stderr错误"

C运行时（`opendir: No such file or directory`）的stderr消息意味着无效数据到达了系统调用。`catch`吸收了错误，但`perror()`已经打印了。唯一的修复是防止无效数据到达调用。

### "我将在每个命令中分别修复它"

如果相同的修复需要在explore、search、grep、reconcile、plan文档中...修复属于共享管道，而不是每个命令。

### "相似度只是共享词汇，不是真正的重复"

不是共享概念的模块之间的40-60% TF-IDF相似度是一个警告。词汇匹配就是信号。

## 快速参考：何时使用哪个命令

| 问题 | 命令 |
|------|------|
| "哪些文件是相似的？" | `explore --format=list` |
| "重复的确切内容是什么？" | `plan refactor --threshold=0.9` |
| "包A和B之间的代码重叠是什么？" | `plan solid --from=A,B` |
| "哪些函数是琐碎的包装器？" | `plan unwrap`或`grep --semantic=proxy` |
| "这些文件共享什么概念？" | `explore file_a file_b --threshold=0 --strategy=apted` |
| "重复是否已修复？" | 使用相同阈值重新运行`plan refactor` |
