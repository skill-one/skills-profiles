# tavily research

AI驱动的深度研究，收集资料、分析并生成带引用的报告。耗时30-120秒。

## 运行前准备

研究需要认证。当`tvly`已认证时，直接运行请求的命令；不要在每个调用中添加状态检查。

如果`tvly`缺失，请按照[tavily-cli setup](../tavily-cli/SKILL.md#setup)进行设置。
如果已安装的CLI报告认证错误，请使用`tvly login`仅进行认证，或使用`tvly init --skip-skills`当引导验证也很有用时。当有交互式用户可以完成时，优先使用基于浏览器的OAuth。`--no-browser`将登录链接打印到控制台而不是打开它，但仍然等待本地回调和。在不受管理的代理或CI环境中，将认证留给用户或使用安全提供的`TAVILY_API_KEY`。在引导设置完成后不要立即启动第二个登录。

## 使用场景

- 您需要全面、多来源的分析
- 用户想要比较、市场报告或文献综述
- 快速搜索不够用——您需要带引用的综合分析
- [工作流](../tavily-cli/SKILL.md)中的第5步：搜索→提取→映射→爬取→**研究**

## 快速入门

```bash
# 基础研究（等待完成）
tvly research "AI代码助手的竞争格局"

# 专业版用于全面分析
tvly research "电动汽车市场分析" --model pro

# 实时流式传输结果
tvly research "AI代理框架比较" --stream

# 将报告保存到文件
tvly research "金融科技趋势2025" --model pro -o fintech-report.json

# 适用于代理的JSON输出
tvly research "量子计算突破" --json
```

## 选项

| 选项 | 描述 |
|------|-------------|
| `--model` | `mini`、`pro`或`auto`（默认） |
| `--stream` | 实时流式传输结果 |
| `--no-wait` | 立即返回请求_id（异步） |
| `--output-schema` | 结构化输出的JSON模式路径 |
| `--citation-format` | `numbered`、`mla`、`apa`、`chicago` |
| `--poll-interval` | 检查间隔秒数（默认：10） |
| `--timeout` | 最大等待秒数（默认：600） |
| `-o, --output` | 将JSON响应保存到文件 |
| `--json` | 结构化JSON输出 |

## 模型选择

| 模型 | 用于 | 速度 |
|-------|---------|-------|
| `mini` | 单主题、目标研究 | ~30秒 |
| `pro` | 全面多角度分析 | ~60-120秒 |
| `auto` | API根据复杂度选择 | 变化 |

**经验法则：** "X是什么做的？" → mini。 "X vs Y vs Z"或"最佳方式..." → pro。

## 异步工作流

对于长时间运行的研究，您可以分别启动和轮询：

```bash
# 启动时不等待
tvly research "主题" --no-wait --json    # 返回request_id

# 检查状态
tvly research status <request_id> --json

# 等待完成
tvly research poll <request_id> --json -o result.json
```

## 小贴士

- **研究耗时30-120秒**——使用`--stream`实时查看进度。
- **使用`--model pro`**进行复杂的比较或多方面主题。
- **使用`--output-schema`**获取匹配自定义模式的结构化JSON输出。
- **对于快速事实**，请使用`tvly search`——研究用于深度综合。
- 从stdin读取：`echo "查询" | tvly research - --json`

## 参见

- [tavily-search](../tavily-search/SKILL.md) — 快速网络搜索用于简单查询
- [tavily-crawl](../tavily-crawl/SKILL.md) — 从网站批量提取用于您自己的分析
