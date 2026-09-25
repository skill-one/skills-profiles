# EdgeOne
将 HTML 内容部署到 EdgeOne Pages，返回公开 URL。无需登录，无需 API 密钥。

## 部署 HTML
部署 HTML 或文本内容。提供您想要发布的完整 HTML 或文本内容，系统将返回一个可以访问您内容的公开 URL。
```bash
npx -y mcporter call mcp-on-edge.edgeone.app/mcp-server.deploy-html value="<html>内容</html>"
npx -y mcporter call mcp-on-edge.edgeone.app/mcp-server.deploy-html value="$(cat index.html)"
```

## 部署网站
将您的项目部署到 EdgeOne Makers。
```bash
npx -y edgeone makers deploy --help
npx -y edgeone makers deploy --anonymous [目录或压缩文件]
```
