# 注入测试路由

当输入到达危险的解释器或执行环境时，这是路由的入口点。

在确认这是一个注入类问题后，使用它来判断主要是在浏览器上下文、数据库、模板引擎、服务器端请求、XML 解析还是系统命令。

## 使用时机

- 输入到达 HTML、JS、SQL、模板、URL 获取器、XML 解析器或 shell
- 您尚未决定是否从 XSS、SQLi、SSRF、XXE、SSTI、CMDi 或 NoSQL 开始
- 您需要根据输入流选择正确的深度技能

## 技能地图

- [XSS 跨站脚本](../xss-cross-site-scripting/SKILL.md)
- [SQLi SQL 注入](../sqli-sql-injection/SKILL.md)
- [SSRF 服务器端请求伪造](../ssrf-server-side-request-forgery/SKILL.md)
- [XXE XML 外部实体](../xxe-xml-external-entity/SKILL.md)
- [SSTI 服务器端模板注入](../ssti-server-side-template-injection/SKILL.md)
- [CMDi 命令注入](../cmdi-command-injection/SKILL.md)
- [NoSQL 注入](../nosql-injection/SKILL.md)
- [反序列化不安全](../deserialization-insecure/SKILL.md)
- [JNDI 注入](../jndi-injection/SKILL.md)
- [表达式语言注入](../expression-language-injection/SKILL.md)
- [CRLF 注入](../crlf-injection/SKILL.md)
- [额外注入类型 (SSI, LDAP, XPath)](./EXTRA_INJECTION_TYPES.md)
- [请求劫持](../request-smuggling/SKILL.md)
- [原型污染](../prototype-pollution/SKILL.md)
- [类型转换](../type-juggling/SKILL.md)
- [HTTP 参数污染](../http-parameter-pollution/SKILL.md)
- [XSLT 注入](../xslt-injection/SKILL.md)
- [CSV 公式注入](../csv-formula-injection/SKILL.md)

## 推荐流程

1. 首先识别输入的最终接收点
2. 然后选择与该解释器最匹配的主题技能
3. 小型有效载荷样本和快速筛选被合并到每个主要技能中；不需要额外的有效载荷路由器

## 相关类别

- [文件访问漏洞](../file-access-vuln/SKILL.md)
