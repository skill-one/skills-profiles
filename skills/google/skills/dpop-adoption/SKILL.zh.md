---
name: dpop-adoption
description: 实现并调试 WebCrypto、Node.js ES6 和与 Google OAuth 平台集成的浏览器运行环境中的 OAuth 2.0 DPoP（RFC 9449）刷新令牌发送者约束功能。在配置非提取型非对称密钥对（P-256）、为授权码交换和令牌刷新生成 DPoP 证明 JWT，或处理 oauth2.googleapis.com/token 处的 400 use_dpop_nonce 挑战重试循环时使用。不应用于无约束的 OAuth 2.0 流程（其中刷新令牌未绑定到客户端密钥对），或用于 Google Cloud IAM / 服务账户认证。
---

# DPoP采用与身份安全架构

证明拥有权（DPoP，RFC 9449）通过将OAuth 2.0刷新令牌以密码学方式绑定到客户端独占持有的私钥，从而防止拦截和重放攻击。在Google的OAuth 2.0平台中，DPoP在令牌端点处绑定刷新令牌，而用于Google API的访问令牌是标准的Bearer令牌（`token_type: "Bearer"`）。

## 1. 核心密码学与架构不变量

在实现DPoP辅助工具或升级HTTP客户端时，你必须严格遵守以下严格的安全不变量：

### A. 通用WebCrypto与运行时兼容性

-   在现代ES6 JavaScript（对于Node 18+和浏览器，`"type": "module"`）中，在验证环境上下文后，必须直接访问`globalThis.crypto`。
-   **绝对不要**通过`require('node:crypto')`导入遗留的CommonJS模块，或引用浏览器范围的`window.crypto`，因为这些会导致混合运行时中的模块初始化崩溃。

### B. 基于硬件的非可提取密钥持久化

-   在SECP256R1（`P-256`）曲线上生成一个椭圆曲线密钥对：`{ name: 'ECDSA', namedCurve: 'P-256' }`。
-   **关键安全护栏**：私钥必须配置为**非可提取**（`extractable: false`）。这保证了私钥永远不会离开硬件密码学边界（安全区域、Android密钥库或JS沙盒内存），从而挫败XSS和依赖项令牌盗窃攻击。
-   公钥必须保持可提取（`extractable: true`），以允许发出JSON Web密钥（JWK）。

### C. 公JWK格式标准

-   在将公钥导出到DPoP证明JWT头部时，构建一个干净的JWK字典，其中严格包含：
    -   `"kty": "EC"`
    -   `"crv": "P-256"`
    -   `"x"`：不带尾随等号填充（`=`）的Base64URL编码的x坐标。
    -   `"y"`：不带尾随等号填充（`=`）的Base64URL编码的y坐标。
-   **绝对不要**暴露私钥参数（`"d"`）或多余元数据。

### D. IEEE P1363与ASN.1 DER签名歧义消除

-   DPoP证明JWT需要根据IEEE P1363和RFC 7518，为每个原始连接坐标签名（$R \parallel S$，对于P-256正好是64字节）。
-   **WebCrypto原生规则**：在标准WebCrypto（`crypto.subtle.sign`）中，ECDSA签名已经以原始IEEE P1363格式发出（连接的32字节`r`和`s`缓冲区，总共64字节）。**不要**尝试对`crypto.subtle.sign`输出进行DER到原始转换，因为将64字节的原始缓冲区解析为ASN.1 DER会导致立即运行时异常（`Invalid DER sequence`）。直接对原始ArrayBuffer进行base64url编码。
-   **遗留API回退**：仅在实现遗留Java/Android（`java.security.Signature`）或Node CommonJS（`crypto.createSign`）时，在base64url编码之前，将ASN.1 DER输出转换为原始64字节IEEE P1363格式。

### E. 单页应用程序（SPA）与后端为前端（BFF）架构

-   **无密钥SPAs限制**：没有后端的纯客户端单页应用程序（SPAs）不能直接使用DPoP与Google API，因为服务器端端点需要`client_secret`，而浏览器CORS限制`DPoP-Nonce`响应头部。
-   **BFF模式**：为了使用DPoP保护SPAs，通过后端为前端（BFF）服务器端客户端路由授权和令牌刷新请求。BFF设置`access_type=offline`，在服务器端使用DPoP绑定刷新令牌，并维护与前端的安全会话cookie。

## 2. 实现规则与强制公共API

在创建新模块时，你的模块必须显式导出以下所有函数，以与CI/CD验证 harnesses 和自动探查器干净地集成。在检查或重构现有代码库时，确保存在等效的密码学和RFC 9449逻辑。在所有情况下都遵守严格的声明派生逻辑：

### A. DPoP证明JWT声明派生规则（`createDPoPProof`）

在`createDPoPProof`中生成DPoP证明JWT时：

**1. JOSE头部（`typ`，`alg`，`jwk`）：**
```javascript
// 头部
{
  "typ": "dpop+jwt",
  "alg": "ES256",
  "jwk": await exportPublicJWK(publicKey)
}
```

**2. 有效载荷声明：**
-   `"htm"`：大写的HTTP方法（`"POST"`用于令牌请求）。
-   `"htu"`：使用`sanitizeHTU(htu)`去除查询参数和哈希片段的目标URI。对于令牌请求，这是
    `https://oauth2.googleapis.com/token`。
-   `"iat"`：当前整数Unix时间戳（秒）（`Math.floor(Date.now() / 1000)`）。
-   `"jti"`（关键不变量）：
    1.  如果向`createDPoPProof`提供显式的`jti`参数，使用该确切字符串。
    2.  否则，如果提供`authCode`参数（在初始代码交换期间），设置`jti = await calculateAuthCodeJti(authCode)`，其中`calculateAuthCodeJti`计算`base64url(sha256(authCode))`，以确保DPoP证明与授权码密码学绑定。
    3.  只有在既未提供`jti`也未提供`authCode`时，通过`generateRandomString()`（例如
        `crypto.getRandomValues(new Uint8Array(24))` base64url编码）生成一个新的加密随机字符串。
-   `"ath"`（可选）：如果为RFC 9449资源请求提供`accessToken`参数，通过
    `calculateATH(accessToken)`计算`base64url(sha256(accessToken))`并注入它（RFC 9449第6.1节）。
-   `"nonce"`（可选）：如果提供`nonce`参数，直接将其注入有效载荷。

### B. 显式导出签名

```javascript
// 1. 密钥生成与JWK导出
export async function generateDPoPKeyPair() // -> { publicKey, privateKey } (private key extractable=false)
export async function exportPublicJWK(publicKey) // -> { kty: 'EC', crv: 'P-256', x, y }

// 2. 证明生成与验证
export async function createDPoPProof({ privateKey, publicKey, htm, htu, nonce, accessToken, authCode, jti }) // -> signed JWT字符串
export async function verifyDPoPProof(dpopProofJwt) // -> { isValid: boolean, header, payload, error }
export function sanitizeHTU(htu) // -> 去除查询和哈希的URL: const u = new URL(htu); return `${u.origin}${u.pathname}`;

// 3. 密码学与编码工具
export function base64UrlEncode(buffer) // -> Uint8Array/ArrayBuffer到base64url字符串，不带`=`填充
export function base64UrlDecode(str) // -> base64url字符串到Uint8Array/Buffer
export function stringToBase64Url(str) // -> UTF-8字符串到base64url
export function base64UrlToString(str) // -> base64url到UTF-8字符串
export function generateRandomString(byteLength = 32) // -> 加密随机base64url字符串
export async function calculateATH(accessToken) // -> base64url(sha256(accessToken)) 根据RFC 9449 Sec 6.1
export async function calculateAuthCodeJti(code) // -> base64url(sha256(code))
export async function generatePKCE() // -> { codeVerifier (>=43个字符), codeChallenge, codeChallengeMethod: 'S256' }
```

## 3. 令牌端点与资源请求工作流

在集成Google的OAuth 2.0平台时：

1.  **令牌端点请求（`oauth2.googleapis.com/token`）：**
    -   在`POST`请求中（用于代码交换`grant_type=authorization_code`和令牌刷新`grant_type=refresh_token`）将DPoP证明JWT附加到`DPoP` HTTP头部：
        `` `DPoP: ${proofJwt}` ``。
2.  **资源API请求：**
    -   Google的令牌端点返回`"token_type": "Bearer"`。对Google API（例如日历、驱动器、Gmail）的下游请求使用标准
        `` `Authorization: Bearer ${accessToken}` ``头部，不需要DPoP头部。
3.  **单重试nonce挑战循环与工作流隔离：**
    -   如果Google的令牌端点返回HTTP `400 Bad Request`，错误为`"use_dpop_nonce"`，并且有`"DPoP-Nonce"`响应头部：
        -   **工作流隔离**：Google的授权服务器在授权码交换和令牌刷新之间强制执行工作流隔离，返回HTTP `400 use_dpop_nonce`挑战以建立新的nonce命名空间。这是标准的RFC合规协议行为，不是服务器故障。
        -   在客户端状态中缓存新的nonce（`this.dpopNonce`）。
        -   立即合成一个新的DPoP证明JWT，包含更新的`nonce`声明和新的`jti`。
        -   一次重放失败的令牌请求。如果重试请求失败，立即终止并报错，以防止无限递归。

## 4. 简洁代理出口协议

在提示合成或输出代码交付品时，优先返回干净、可直接导入的代码块，不包含冗余的对话前缀或重复的填充内容。对于概念或架构查询，提供标准的直接答案。

## 5. 参考资料和支持文档

### 开发者文档（Google开发者）
-   [DPoP采用指南](https://developers.google.com/identity/protocols/oauth2/resources/dpop-adoption) —
    官方Google身份指南，介绍如何在授权码交换和令牌刷新中实现DPoP。
-   [使用OAuth 2.0进行Web服务器应用程序](https://developers.google.com/identity/protocols/oauth2/web-server#offline) —
    离线访问、刷新令牌和服务器端授权流程。
-   [OAuth 2.0最佳实践：发送者约束令牌](https://developers.google.com/identity/protocols/oauth2/resources/best-practices#sender-constrain-tokens) —
    关于令牌存储、轮换和发送者约束的建议。

### 开发者知识MCP服务器
-   配备模型上下文协议（`MCP`）的代理可以使用
    [Google开发者知识MCP服务器](https://developers.google.com/knowledge/mcp)
    (`npx -y @google/mcp-developer-knowledge-server`) 通过
    `developer_knowledge:search_documents`和
    `developer_knowledge:get_documents`查询实时Google开发者文档。

### 标准与RFC规范
-   [RFC 9449：OAuth 2.0证明拥有权（DPoP）](https://datatracker.ietf.org/doc/html/rfc9449)
-   [RFC 7519：JSON Web令牌（JWT）](https://datatracker.ietf.org/doc/html/rfc7519)
-   [RFC 7636：OAuth公共客户端代码交换证明密钥（PKCE）](https://datatracker.ietf.org/doc/html/rfc7636)
