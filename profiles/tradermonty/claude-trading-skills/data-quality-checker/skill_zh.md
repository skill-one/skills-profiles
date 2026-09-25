## 概述

在市场分析文档发布前检测常见数据质量问题。检查器验证五个类别：价格尺度一致性、仪器符号、日期/星期准确性、分配总额和单位使用。所有发现均为建议性——它们标记潜在问题供人工审核，而不是阻止发布。

## 使用场景

- 发布周策略博客或市场分析报告前
- 生成自动化市场摘要后
- 审核翻译文档（英文/日文）以检查数据准确性
- 将多个数据源（FRED、FMP、FINVIZ）的数据合并到一个报告中时
- 作为包含财务数据的任何文档的预发布检查

## 前置条件

- Python 3.9+
- 无需外部API密钥
- 无需第三方Python包（仅使用标准库）

## 工作流程

### 第1步：接收输入文档

接受目标Markdown文件路径和可选参数：
- `--file`：要验证的Markdown文档路径（必填）
- `--checks`：要运行的检查的逗号分隔列表（可选；默认：全部）
- `--as-of`：用于年份推断的参考日期（YYYY-MM-DD格式）（可选）
- `--output-dir`：报告输出目录（可选；默认：`reports/`）

### 第2步：执行验证脚本

运行数据质量检查器脚本：

```bash
python3 skills/data-quality-checker/scripts/check_data_quality.py \
  --file path/to/document.md \
  --output-dir reports/
```

仅运行特定检查：

```bash
python3 skills/data-quality-checker/scripts/check_data_quality.py \
  --file path/to/document.md \
  --checks price_scale,dates,allocations
```

提供参考日期以进行年份推断（适用于日期中未明确包含年份的文档）：

```bash
python3 skills/data-quality-checker/scripts/check_data_quality.py \
  --file path/to/document.md \
  --as-of 2026-02-28
```

### 第3步：加载参考标准

读取相关参考文档以对发现进行上下文化：

- `references/instrument_notation_standard.md` -- 每种仪器类别的标准交易代码符号、数字位数提示和命名规范
- `references/common_data_errors.md` -- 频繁出现的错误目录，包括FRED数据延迟、ETF/期货尺度混淆、节假日疏忽、分配总额陷阱和单位混淆模式

使用这些参考来解释发现并建议更正。

### 第4步：审核发现

检查输出中的每个发现：

- **错误** -- 高置信度问题（例如，通过日历计算验证的日期-星期不匹配）。强烈建议更正。
- **警告** -- 需要人工判断的可能问题（例如，价格尺度异常、符号不一致、分配总额超出0.5%）。
- **信息** -- 信息性注释（例如，混合使用百分比/符号可能是有意为之）。

### 第5步：生成质量报告

脚本生成两个输出文件：

1. **JSON报告** (`data_quality_YYYY-MM-DD_HHMMSS.json`)：机器可读的发现列表，包括严重程度、类别、消息、行号和上下文。
2. **Markdown报告** (`data_quality_YYYY-MM-DD_HHMMSS.md`)：按严重程度分组的人类可读报告。

将发现呈现给用户，并参考知识库进行解释。针对每个问题提出具体更正建议。

## 输出格式

### JSON发现结构

```json
{
  "severity": "WARNING",
  "category": "price_scale",
  "message": "GLD: $2,800有4位数字（预期2-3位数字）",
  "line_number": 5,
  "context": "GLD: $2,800"
}
```

### Markdown报告结构

```markdown
# 数据质量报告
**来源**：path/to/document.md
**生成时间**：2026-02-28 14:30:00
**总发现数**：3

## 错误 (1)
- **[dates]** (line 12)：日期-星期不匹配：2026年1月1日（星期一）——实际星期为星期四

## 警告 (2)
- **[price_scale]** (line 5)：GLD: $2,800有4位数字（预期2-3位数字）
  > `GLD: $2,800`
- **[allocations]**：分配总额：110.0%（预期~100%）
```

## 资源

- `scripts/check_data_quality.py` -- 主验证脚本
- `references/instrument_notation_standard.md` -- 符号和价格尺度参考
- `references/common_data_errors.md` -- 常见错误模式和预防措施

## 关键原则

1. **建议模式**：所有发现均为供人工审核的警告。脚本在成功执行时始终以代码0退出，即使存在发现。代码1保留用于脚本失败（文件未找到、解析错误）。

2. **分段感知分配检查**：仅检查分配部分（通过标题如“配分”、“Allocation”或表格列如“ウェイト”、“目安比率”标识）中的百分比。正文中的随机百分比（概率、RSI、年增长率）将被忽略。

3. **双语支持**：处理英文和日文日期格式、星期名称和部分标题。全角字符（％、〜、en-dash）在处理前会被规范化。

4. **年份推断**：对于没有明确年份的日期，检查器使用（优先顺序）：`--as-of`选项、文档标题/元数据中发现的YYYY模式，或当前年份与6个月跨年启发式。

5. **数字位数启发式**：价格尺度验证使用数字位数（小数点前的位数）而不是绝对价格范围。这种方法对价格随时间变化具有弹性，同时仍能捕获ETF/期货混淆错误。
