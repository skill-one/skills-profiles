---
name: r8-analyzer
description: 分析 Android 构建文件和 R8 保留规则，以识别冗余、范围过广的包级规则以及涵盖库消费者保留规则的规则。当开发者希望优化应用大小、移除冗余或范围过广的保留规则，或排查 ProGuard 配置问题时使用。
---

## 第 1 步。设置和配置检查

- 检查 `build.gradle`、`build.gradle.kts` 和 `gradle.properties`。
- 使用 [参考资料/CONFIGURATION.md](references/CONFIGURATION.md) 来识别缺失的优化项。
- **AGP**：如果版本低于 9.0，建议迁移到 9.0 以实现 [构建时性能提升](references/android/topic/performance/app-optimization/enable-app-optimization.md)。
- **全模式**：验证 `android.enableR8.fullMode=false` 已从 `gradle.properties` 中移除。

## 第 2 步。分析路径选择

- 检查 `build.gradle`、`build.gradle.kts`、`gradle.properties` 和 `libs.versions.toml` 以获取 AGP 和 R8 的版本。

- **如果 AGP \>= 9.3.0**：继续执行 **路径 A（独立任务）**。

- **如果 AGP \< 9.3.0 且 R8 \>= 9.3.7-dev**：继续执行 **路径 B（量化）**。

- 如果以上条件均不满足，则继续执行 **路径 C（启发式）**。

### 路径 A：独立 Gradle 任务（AGP \>= 9.3.0）

- **第 1 步：运行独立任务**：执行 `./gradlew :app:analyzeReleaseR8Config` 以评估 R8 配置。你必须等待此命令完成才能继续。
- **第 2 步：转换为 JSON**：报告生成于 `app/build/reports/r8/r8-config-analyzer-release.pb`。你必须显式运行转换脚本，执行：`python3 .agents/skills/r8-analyzer/scripts/convert_pb_to_json.py`。等待此命令完成。
- **第 3 步：分析**：你必须显式运行分析脚本，执行：`python3 .agents/skills/r8-analyzer/scripts/analyze.py`。这将输出 `tmp/keepradius/analysis_result.txt`。等待此命令完成。

### 路径 B：量化数据生成（R8 \>= 9.3.7-dev 且 AGP \< 9.3.0）

- **第 1 步：检查要求**：Python 和 `protobuf` 包是必需的。
- **第 2 步：生成和分析**：你必须运行 [参考资料/CONFIGURATION-ANALYZER.md](references/CONFIGURATION-ANALYZER.md) 中描述的 shell 命令，使用 R8 配置分析器生成 proto 文件，将其转换为 JSON 并分析结果。
- **第 3 步：分析**：你必须确保分析生成 `tmp/keepradius/analysis_result.txt`，包含分数和规则影响指标。

### 路径 C：启发式评估和建议（R8 \< 9.3.7-dev）

*(仅当量化数据生成不可行时使用)*

- **第 1 步：手动评估**：检查 `proguard-rules.pro`。
- **第 2 步：库检查**：将规则与 [参考资料/REDUNDANT-RULES.md](references/REDUNDANT-RULES.md) 进行比较。建议移除捆绑规则。
- **第 3 步：自定义规则检查**：使用 [参考资料/KEEP-RULES-IMPACT-HIERARCHY.md](references/KEEP-RULES-IMPACT-HIERARCHY.md) 和 [参考资料/REFLECTION-GUIDE.md](references/REFLECTION-GUIDE.md) 优先级排序和评估。建议对宽泛规则（例如，全局规则）进行 **优化**。
- **第 4 步：验证**：建议使用 [UI Automator](references/android/training/testing/other-components/ui-automator.md) 进行宏基准测试，以验证任何建议的变更。继续执行第 3 步。

## 第 3 步。报告生成

- **格式**：严格遵循 [参考资料/REPORT_FORMAT.md](references/REPORT_FORMAT.md)。
- **输入**：如果使用路径 A，直接从生成的 `analysis.txt` 文件中提取指标（分数、影响、示例类）；如果使用路径 B，则从手动发现中提取。
- **输出**：仅输出原始 Markdown 报告到聊天中。不要输出对话填充（例如，“这是您的报告...”）。不要提供建议、下一步操作或任何其他定义在 [参考资料/REPORT_FORMAT.md](references/REPORT_FORMAT.md) 范围之外的文本。不要提及用于配置分析的路径。

## 限制

- **严格的输出限制**：最终输出必须严格为 Markdown 报告，不得包含其他内容。
- **无代码修改**：仅进行研究和建议，不要修改文件。
- **无冗余**：报告中不要解释 R8 的优势或引用技能内部文件。
- **聚焦**：如果未发现问题或项目，可省略部分（例如，被吸收的规则、配置）。
