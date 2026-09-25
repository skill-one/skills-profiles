# 会话报告

生成一个包含Claude Code使用情况的独立HTML报告，并保存到当前工作目录。

## 步骤

1. **获取数据**。运行捆绑的分析器（默认窗口：最后7天；如果用户传递了不同的范围，例如 `24h`、`30d` 或 `all`，则尊重该范围）。脚本 `analyze-sessions.mjs` 位于与这个 SKILL.md 相同的目录中 — 使用其绝对路径：
   ```sh
   node <skill-dir>/analyze-sessions.mjs --json --since 7d > /tmp/session-report.json
   ```
   对于所有时间，省略 `--since`。

2. **读取** `/tmp/session-report.json`。浏览 `overall`、`by_project`、`by_subagent_type`、`by_skill`、`cache_breaks`、`top_prompts`。

3. **复制模板**（也捆绑在SKILL.md的同一目录中）到当前工作目录的输出路径：
   ```sh
   cp <skill-dir>/template.html ./session-report-$(date +%Y%m%d-%H%M).html
   ```

4. **编辑输出文件**（使用编辑，而不是写入 — 保留模板的JS/CSS）：
   - 将 `<script id="report-data" type="application/json">` 的内容替换为步骤1中的完整JSON。页面的JS会自动从这个数据块中渲染英雄总数、所有表格、条形图和下钻。
   - 用 **3–5行一条**的发现填充 `<!-- AGENT: anomalies -->` 块。尽可能将数字表示为**总token的百分比**（总数 = `overall.input_tokens.total + overall.output_tokens`）。每条发现一行，精确的标记：
     ```html
     <div class="take bad"><div class="fig">41.2%</div><div class="txt"><b>cc-monitor</b> 仅通过3次会话消耗了本周的41%</div></div>
     ```
     类：`.take bad` 用于浪费/异常（红色），`.take good` 用于健康信号（绿色），`.take info` 用于中性事实（蓝色）。`.fig` 是一个简短的数字（一个百分比、一个计数或一个倍数，如 `12×`）。`.txt` 是一个纯英文句子，命名项目/技能/提示；将主题用 `<b>` 包裹。寻找：一个项目或技能不成比例地消耗、缓存命中率 <85%、单个提示 >2%的总数、子代理类型平均 >1M token/调用、缓存中断聚集。
   - 用1–4个 `<div class="callout">` 建议（在页面的**底部**）填充 `<!-- AGENT: optimizations -->` 块，与特定行相关联（例如 "`/weekly-status` 生成了7个子代理，占总数的8.1% — 将其范围缩小到更少的并行代理"）。
   - 不要重新结构现有部分。

5. **向用户报告**保存的文件路径。不要打开它或渲染它。

## 注意事项

- 模板是交互性（排序、展开/折叠、块字符条形图）的来源。你的工作是数据+叙述，而不是标记。
- 保持评论简短具体 — 引用JSON中的实际项目名称、数字、时间戳。
- `top_prompts` 已经包括子代理token，并将任务通知的延续合并到原始提示中。
- 如果JSON >2MB，在嵌入之前将 `top_prompts` 修剪到100条，将 `cache_breaks` 修剪到100条（它们应该已经被限制）。
