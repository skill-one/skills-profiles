# Exa Web Search (免费)

用于网络、代码和公司研究的神经搜索。无需API密钥。

## 设置

验证mcporter已配置：
```bash
mcporter list exa
```

若未列出：
```bash
mcporter config add exa https://mcp.exa.ai/mcp
```

## 核心工具

### web_search_exa
搜索网络以获取当前信息、新闻或事实。

```bash
mcporter call 'exa.web_search_exa(query: "2026最新AI新闻", numResults: 5)'
```

**参数：**
- `query` - 搜索查询
- `numResults` (可选，默认：8)
- `type` (可选) - `"auto"`、`"fast"` 或 `"deep"`

### get_code_context_exa
从GitHub、Stack Overflow查找代码示例和文档。

```bash
mcporter call 'exa.get_code_context_exa(query: "React hooks示例", tokensNum: 3000)'
```

**参数：**
- `query` - 代码/API搜索查询
- `tokensNum` (可选，默认：5000) - 范围：1000-50000

### company_research_exa
研究公司以获取商业信息和新闻。

```bash
mcporter call 'exa.company_research_exa(companyName: "Anthropic", numResults: 3)'
```

**参数：**
- `companyName` - 公司名称
- `numResults` (可选，默认：5)

## 高级工具（可选）

通过更新配置URL可使用六个附加工具：
- `web_search_advanced_exa` - 域/日期筛选
- `deep_search_exa` - 查询扩展
- `crawling_exa` - 完整页面提取
- `people_search_exa` - 专业资料
- `deep_researcher_start/check` - AI研究代理

**启用所有工具：**
```bash
mcporter config add exa-full "https://mcp.exa.ai/mcp?tools=web_search_exa,web_search_advanced_exa,get_code_context_exa,deep_search_exa,crawling_exa,company_research_exa,people_search_exa,deep_researcher_start,deep_researcher_check"

# 然后使用：
mcporter call 'exa-full.deep_search_exa(query: "AI安全研究")'
```

## 小贴士

- 网络：使用`type: "fast"`进行快速查询，`"deep"`进行彻底研究
- 代码：降低`tokensNum` (1000-2000)以聚焦，提高 (5000+)以获取全面信息
- 更多模式请参考 [examples.md](references/examples.md)

## 资源

- [GitHub](https://github.com/exa-labs/exa-mcp-server)
- [npm](https://www.npmjs.com/package/exa-mcp-server)
- [文档](https://exa.ai/docs)
