# Tavily CLI

网页搜索、内容提取、网站爬取、URL发现和深度研究。返回针对LLM优化的JSON格式结果。

需要`tavily-cli`。搜索和提取支持无密钥访问；映射、爬取和研究需要认证。

运行`tvly --help`或`tvly <命令> --help`获取完整选项详情。

## 安装

如果未安装`tvly`：

```bash
curl -fsSL https://cli.tavily.com/install.sh | bash
```

或手动安装：`uv tool install tavily-cli` / `pip install tavily-cli`

对于代理设置，除非用户要求登录或请求的任务需要映射、爬取或研究，否则从无密钥访问开始。如果安装程序尚未完成设置，请运行：

```bash
tvly init --skip-auth
```

这会安装或更新Tavily技能并验证无密钥搜索。在首次搜索或提取请求之前，不要寻找API密钥或进行认证。

当请求或需要认证时，使用引导式设置：

```bash
tvly init

# 建议您自行打开登录链接
tvly init --no-browser
```

`tvly init`会重用现有凭证，安装或更新与该CLI版本捆绑的Tavily技能，并验证实时搜索。刷新捆绑技能时，请先运行`tvly update`。当技能已安装且只需要认证或验证时，使用`tvly init --skip-skills`。

搜索和提取可以在无需认证的情况下立即运行，但受无密钥速率限制限制。如果交互式会话中任一命令达到该限制，请运行`tvly login`打开浏览器OAuth，然后重试原始命令一次。在不交互的环境中，报告速率限制和认证选项，而不是启动交互式流程。映射、爬取和研究需要认证。仅在需要时使用`tvly --status --json`检查当前状态。

对于无需完整设置的认证，使用`tvly login`、`tvly login --no-browser`、`tvly login --api-key tvly-YOUR_KEY`或`TAVILY_API_KEY`。

基于浏览器的OAuth是首选的交互式登录方法。`--no-browser`仅打印登录链接而不是自动打开；流程仍然会返回到运行`tvly`的本地主机的回调。在远程会话中，确保回调可达（SSH可能需要端口转发）。在不交互的代理或CI环境中，将认证留给用户或使用安全提供的`TAVILY_API_KEY`，然后继续原始命令。

使用`tvly update --check`和`tvly update`保持现有安装的更新。

## 工作流程

遵循此升级模式——从简单开始，需要时升级：

1. **搜索** — 没有特定URL。查找页面、回答问题、发现来源。
2. **提取** — 有URL。直接获取其内容。
3. **映射** — 大型网站，需要找到正确的页面。先发现URL。
4. **爬取** — 需要从整个网站部分获取大量内容。
5. **研究** — 需要全面的、多来源分析并附带引用。

| 需求 | 命令 | 何时使用 |
|------|---------|------|
| 在某个主题上查找页面 | `tvly search` | 尚无特定URL |
| 获取页面内容 | `tvly extract` | 有URL |
| 在网站内查找URL | `tvly map` | 需要定位特定子页面 |
| 批量提取网站部分 | `tvly crawl` | 需要许多页面（例如，所有 /docs/） |
| 带引用的深度研究 | `tvly research` | 需要多来源综合 |

对于详细命令参考，使用每个命令的独立技能（例如，`tavily-search`、`tavily-crawl`）或运行`tvly <命令> --help`。

不带子命令运行`tvly`将进入交互式REPL。

## 输出

搜索、提取、爬取、映射和研究支持`--json`以获取结构化输出。产生结果的命令支持`-o`以保存JSON响应；爬取还支持`--output-dir`以每个页面生成一个Markdown文件。设置、认证、状态和更新命令在文档中记录了`--json`，但不支持`-o`。

```bash
tvly search "react hooks" --json -o results.json
tvly extract "https://example.com/docs" -o docs.json
tvly crawl "https://docs.example.com" --output-dir ./docs/
```

## 小贴士

- **始终引用URL** — shell将`?`和`&`解释为特殊字符。
- **使用`--json`进行代理式工作流程** — 当选定的命令提供此功能时。
- **从stdin读取`-`** — `echo "query" | tvly search -`
- **退出代码**：0 = 成功，1 = 设置/更新失败，2 = 输入错误，3 = 认证错误，4 = API或实时验证错误。
