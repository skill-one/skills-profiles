# API 安全最佳实践

审查从调用者身份通过授权、验证输入、存储到可观察响应的请求边界。保留应用程序的实际身份提供者和数据模型，而不是引入第二个认证系统。

## 使用场景

在添加受保护端点、审查对象访问、替换宽松请求解析或调查 API 滥用路径时使用。对于具体缺陷，从失败的路线及其调用者开始；不要部署不相关的安全基础设施。

## 输入和前提条件

记录路线、调用者/租户模型、身份提供者、令牌契约、运行时和锁定依赖版本、数据库模式、代理拓扑和授权测试范围。在测试环境中使用合成身份。现有的任务授权会继续；生产扫描、账户写入和消息发送需要自己的权限。下面的 Node 示例是 Express、jsonwebtoken 和 Zod 的集成草图；应用程序/数据库适配器故意命名，而不是作为完整的可运行服务呈现。在集成之前，请根据安装的版本确认 API。

## 1. 验证精确的令牌契约

优先使用已建立的提供者/会话中间件。当服务拥有 HMAC JWT 契约时，要求强大的服务器拥有的密钥、固定算法、精确的发布者和受众，以及必需的运行时声明。在签名验证之前不要从解码的令牌推断权限。永远不要接受调用者选择的验证算法。

```javascript
const jwt = require('jsonwebtoken');

// 说明性第一方访问令牌契约；不是第三方 OAuth 适配器。
const ACCESS_POLICY = {
  algorithms: ['HS256'], issuer: 'example-auth', audience: 'example-api'
};
function verifyAccessToken(token, signingKey) {
  const claims = jwt.verify(token, signingKey, ACCESS_POLICY);
  if (!claims || typeof claims !== 'object' ||
      typeof claims.sub !== 'string' || !claims.sub ||
      typeof claims.tenantId !== 'string' || !claims.tenantId ||
      !Number.isSafeInteger(claims.exp) || !Number.isSafeInteger(claims.iat) ||
      claims.exp <= claims.iat) {
    throw new Error('无效的访问声明');
  }
  return { subject: claims.sub, tenantId: claims.tenantId };
}
function readBearer(header) {
  if (typeof header !== 'string' || header.length > 8192) return null;
  const match = /^Bearer ([A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)$/i.exec(header);
  return match ? match[1] : null;
}
```

使用相同的发布者/受众/算法和应用程序批准的短过期时间发行访问令牌。将验证失败处理为通用的 401，不要回显令牌或异常。仅凭过期时间不能吊销令牌；根据实际威胁模型定义吊销或短生命周期会话。使用非对称提供者密钥的服务需要提供者的发现/JWKS 验证和密钥轮换策略，而不是这个 HMAC 示例。永远不要将访问令牌重用为刷新令牌。

### 刷新会话

使用提供者支持的会话流程或服务器端不透明的刷新设计：
仅存储摘要、过期时间、用户/会话系列和吊销状态。在一个原子事务中消耗旧的活动令牌并创建替换令牌。并发重用不得发出两个继任者；定义的重用处理会吊销受影响的系列。
在发行新的访问令牌时检查当前用户状态和权限。将刷新绑定到预期的客户端/会话，并保护基于 Cookie 的请求免受 CSRF 攻击。不要记录令牌，将它们明文存储在数据库中，或通过 URL 返回刷新令牌。
在调用流程完成之前测试同时刷新、过期、重放、吊销和事务失败。这里没有捆绑数据库事务适配器。

## 2. 授权资源和操作

身份验证识别调用者；授权决定对象上的精确操作和租户。角色名称不会自动授予跨租户访问权限。在数据库变异中应用所有者/租户谓词，以避免检查-写入竞争，并允许写入属性的白名单。始终与产品的资源披露策略一致地使用 404/403。

```javascript
// Prisma 风格草图；id 和租户类型必须与您的实际模式匹配。
async function deleteOwnedPost(prisma, postId, principal) {
  const result = await prisma.post.deleteMany({
    where: { id: postId, userId: principal.subject, tenantId: principal.tenantId }
  });
  return result.count === 1;
}
```

管理员路径需要一个明确的单独策略和审计事件；不要向每个所有者检查添加隐式的管理员绕过。测试有效用户访问另一个用户的对象、另一个租户中的相同 ID、已删除的成员资格和批量端点。

## 3. 解析一次，然后使用验证的值

拒绝部分数字解析（`12abc` 不是 ID 12）、不安全的整数、意外属性和过大的请求。使用参数化数据库查询。ORM 不会提供业务授权或使不安全的原始 SQL 安全。

```javascript
function parsePositiveId(raw) {
  if (typeof raw !== 'string' || !/^[1-9][0-9]{0,15}$/.test(raw)) return null;
  const value = Number(raw);
  return Number.isSafeInteger(value) && value > 0 ? value : null;
}

const { z } = require('zod');
const profileUpdate = z.object({
  displayName: z.string().trim().min(1).max(100)
}).strict();
function validateBody(schema) {
  return (req, res, next) => {
    const parsed = schema.safeParse(req.body);
    if (!parsed.success) {
      return res.status(400).json({ error: '无效请求' });
    }
    req.validatedBody = parsed.data; // 默认值/转换必须到达处理器。
    next();
  };
}
// 处理器使用 req.validatedBody，永远不要使用原始 body 或任意展开。
```

在解析之前设置 body 限制。Zod 形状验证只是一个层：在事务中检查当前所有权、允许的转换和唯一性。对于 HTML 仅允许需要的标签/属性并使用维护的清理器，然后使用目标的安全输出 API 渲染。对于纯文本评论，优先选择纯文本；清理字符串不会在 JavaScript、URL 或 HTML 上下文中使其安全。也验证上游 API 响应作为不受信任的输入。

对于出站 URL，定义允许的方案/主机、重定向行为、解析的 IP 范围、凭证策略、超时和响应大小。正则表达式或 URL 解析器本身不能防止 SSRF 或 DNS 重绑定。文件上传同样需要类型/内容检查、大小限制、隔离存储和读取授权。

## 4. 控制滥用，不要声称 DDoS 保护

使用现有的网关和维护的速率限制存储。在派生认证用户密钥之前进行身份验证，并且永远不要信任用户提供的级别。对于匿名流量，使用库支持的对 IPv6 感知的 IP 密钥处理，并配置 Express 信任代理到实际的信任跳转；不要盲目为所有调用者启用它。

对于分布式配额，使用原子计数器+过期实现，并具有定义的存储故障行为。避免手写的 `INCR` 后跟 `EXPIRE`：它们之间的崩溃可能会留下永久密钥。区分每个用户配额、每个 IP 滥用控制、并发限制和上游服务预算。记录实际的窗口/重置语义，并发送准确的 Retry-After，而不是硬编码的完整窗口值。内存限制器如果不是配置了共享存储，则是进程级的。

测试并发请求、IPv4/IPv6、伪造转发头部、未知级别、缺失身份、Redis 故障和过期。应用程序速率限制不能吸收网络饱和。Helmet 配置 HTTP 响应头部；它不是 DDoS 保护、访问控制或上游容量控制的替代品。针对实际部署和子域名策略推出 CSP/HSTS；不要盲目复制预加载设置。

## 5. 密码、密钥和日志记录

尽可能使用已建立的身份提供者。对于存储的密码，使用维护的密码哈希方案并校准参数（对于新设计优先选择 Argon2id）。检查泄露的常见密码并支持短语。不要强加任意的 uppercase/symbol 组合规则或静默截断长密码。遗留 bcrypt 有一个输入字节限制，在迁移期间必须明确考虑；字符和 UTF-8 字节的密码长度是不同的。

将密钥保存在批准的密钥机制中，在启动时检查必需的配置而不打印值，并旋转暴露的凭证。永远不要在常规日志中包含原始令牌、密码、请求体或完整的数据库异常。在适当的保留/访问策略下记录有界的事件名称、请求关联和安全状态/错误类别。清理的错误不应返回大量分配的用户对象。CORS 控制浏览器跨源访问；它不是 API 身份验证或 CSRF 保护。

## 实际示例：一个配置文件更新边界

给定 `PATCH /users/:id`，其中字符串 ID 和可编辑的显示名称：

1. 在 fixtures 中记录授权的调用者/租户和当前端点行为。
2. 在存储访问之前检查缺失/过期/错误受众的令牌返回 401。
3. 发送 `12abc`、不安全的整数、空名称和额外的 `role` 字段；预期 400 并没有数据库变异。发送填充的有效名称；确认仅解析的修剪值到达所有者-租户范围更新。
4. 尝试不同用户的有效 ID 和跨租户 ID；预期文档中定义的拒绝和没有变异。有效所有者请求仅更新允许的属性。
5. 练习配额/存储故障并确认日志中不包含请求令牌或名称。

返回路线策略、复制的失败案例、精确的测试命令/输出和剩余差距。这些是在目标应用程序中执行的预期检查，而不是声称这个存储库已经测试了部署的 API。

## 限制

本指南不是完整的身份服务、认证安全审计或渗透测试。片段省略了应用程序适配器和集成错误中间件。解析器的单元测试不会验证数据库事务、代理行为或提供者会话。明确报告任何未测试的路线、租户路径和故障模式。不要从通过结构检查或来自风险元数据标签推断出清洁的安全状态。

## 参考

- [OWASP API 安全](https://owasp.org/www-project-api-security/)
- [JWT 当前最佳实践，RFC 8725](https://www.rfc-editor.org/rfc/rfc8725)
- [OWASP 会话管理](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [OWASP 密码存储](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [Express 生产安全](https://expressjs.com/en/advanced/best-practice-security.html)
- [Zod 基本解析](https://zod.dev/basics)
- 相关技能：`auth-implementation-patterns`，`api-patterns`，`systematic-debugging`。
