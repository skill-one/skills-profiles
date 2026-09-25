# Xcode 编译分析器

当编译时间看起来像是瓶颈，而不仅仅是项目配置问题时，使用此技能。

## 核心规则

- 从证据开始，理想情况下是最近的 `.build-benchmark/` 艺术品或原始的计时摘要输出。
- 在调查期间，优先使用仅分析编译器标志，而不是永久修改项目设置。
- 按预期 **墙钟** 影响（而不是累积编译时间影响）对发现进行排序。当编译任务高度并行化（编译类别的总和 >> 墙钟中位数）时，请注意，修复单个热点可能会提高并行效率，而不会减少构建等待时间。
- 当证据指向并行化工作而不是串行瓶颈时，将建议标记为“减少编译器工作负载（并行）”，而不是“减少构建时间”。
- 未经明确开发者批准，不要编辑源代码或构建设置。

## 需要检查的内容

- 清理和增量构建的 `Build Timing Summary` 输出
- 长时间运行的 `CompileSwiftSources` 或按文件编译任务
- `SwiftEmitModule` 时间 —— 在大型模块中单行更改后，可能达到 60 秒以上；如果它主导增量构建，则该模块可能太大或宏过多
- `Planning Swift module` 时间 —— 如果此类别在增量构建中不成比例地大（每个模块高达 30 秒），则表示意外的输入无效化或宏相关的重建级联
- 使用以下标志的临时运行：
  - `-Xfrontend -warn-long-expression-type-checking=<ms>`
  - `-Xfrontend -warn-long-function-bodies=<ms>`
- 用于彻底调查的更深入的诊断标志：
  - `-Xfrontend -debug-time-compilation` -- 按文件编译时间，以对最慢的文件进行排序
  - `-Xfrontend -debug-time-function-bodies` -- 按函数编译时间（未过滤，补充基于阈值的警告标志）
  - `-Xswiftc -driver-time-compilation` -- 驱动级计时，以隔离驱动程序开销
  - `-Xfrontend -stats-output-dir <path>` -- 每个编译单元的详细编译器统计（JSON），用于根本原因分析
- 增加桥接工作的混合 Swift 和 Objective-C 表面

## 分析工作流程

1. 确定主要问题是广泛的编译量还是少数极端热点。
2. 解析计时摘要类别，并按最大的编译贡献者排序。
3. 运行诊断脚本以暴露类型检查热点：
   ```bash
   python3 scripts/diagnose_compilation.py \
     --project App.xcodeproj \
     --scheme MyApp \
     --configuration Debug \
     --destination "platform=iOS Simulator,name=iPhone 16" \
     --threshold 100 \
     --output-dir .build-benchmark
   ```
   这将生成一个超过毫秒阈值的功能和表达式的排序列表。使用诊断艺术品与源代码检查相结合，首先关注最昂贵的文件。
4. 将证据映射到具体的建议列表。
5. 将代码级建议与项目级或模块级建议分开。

## 苹果衍生检查

首先查找这些模式：

- 昂贵表达式中缺少显式类型信息
- 复杂的链式或嵌套表达式，难以进行类型检查
- 将代理属性类型为 `AnyObject` 而不是具体协议
- 过大的 Objective-C 桥接头文件或生成的 Swift 到 Objective-C 表面
- 跳过框架限定符并错过模块缓存重用的头文件导入
- 缺少 `final` 的类，而这些类从未被子类化
- 对仅限内部符号的过于宽泛的访问控制（`public`/`open`）
- 应该分解为子视图的庞大 SwiftUI `body` 属性
- 没有中间类型注解的长方法链或闭包

## 报告格式

对于每个建议，包括：

- 观察到的证据
- 可能受影响的文件或模块
- 预期的等待时间影响（例如，“预期将您的清理构建减少约 2 秒”或“减少并行编译工作，但不太可能减少构建等待时间”）
- 置信度
- 应用之前是否需要批准

如果证据指向项目配置而不是源代码，请将工作移交给 [`xcode-project-analyzer`](../xcode-project-analyzer/SKILL.md)，方法是阅读其 SKILL.md 并将相同的项目上下文的工作流程应用于该项目。

## 首选策略

- 建议通过构建命令注入临时标志，然后再建议永久修改构建设置。
- 优先将庞大的视图构建器、闭包或结果构建器表达式缩小为较小的类型单元。
- 当显式导入和协议类型减少编译器搜索空间时，建议它们。
- 当混合语言边界是真正的问题而不是 Swift 语法本身时，请指出。

## 额外资源

- 有关详细的审计清单，请参阅 [references/code-compilation-checks.md](references/code-compilation-checks.md)
- 有关共享的建议结构，请参阅 [references/recommendation-format.md](references/recommendation-format.md)
- 有关源代码引用，请参阅 [references/build-optimization-sources.md](references/build-optimization-sources.md)
