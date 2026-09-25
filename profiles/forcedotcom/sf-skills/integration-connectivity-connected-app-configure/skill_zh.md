# integration-connectivity-connected-app-configure: Salesforce 连接应用与外部客户端应用

在用户需要在 Salesforce 中进行 **OAuth 应用配置** 时使用此技能：连接应用、外部客户端应用 (ECAs)、JWT 承载器设置、PKCE 决策、作用域设计，或从旧版连接应用模式迁移到新版 ECA 模式。

## 范围

**在范围内：**
- `.connectedApp-meta.xml` 或 `.eca-meta.xml` 文件
- OAuth 流选择和回调 / 作用域设置
- JWT 承载器认证、设备流、客户端凭证或认证码决策
- 连接应用与外部客户端应用架构选择
- 消费者密钥 / 密码 / 证书处理策略

**超出范围 — 转发至其他地方：**
- 配置命名凭证或运行时调用 → [integration-connectivity-generate](../integration-connectivity-generate/SKILL.md)
- 将元数据部署到组织 → `platform-metadata-deploy` 技能
- 编写 Apex 令牌处理代码 → `platform-apex-generate` 技能

---

## 第一个决策：连接应用或外部客户端应用

| 如果需求是... | 推荐 |
|---|---|
| 简单单组织 OAuth 应用 | 连接应用 |
| 新开发且具有更好的密钥处理 | 外部客户端应用 |
| 多组织 / 打包 / 更强的操作控制 | 外部客户端应用 |
| 简单的旧版兼容性 | 连接应用 |

默认指导：
- 对于新的受监管、可打包或自动化密集型解决方案，选择 **ECA**。
- 当简单性和旧版兼容性更重要时，选择 **连接应用**。
- Spring '26 注意：默认情况下，在组织中禁用新连接应用的创建。对于新集成，除非明确需要连接应用兼容性，否则请优先使用外部客户端应用。

---

## 必需输入

询问或推断：
- 应用类型：连接应用或 ECA
- OAuth 流：认证码、PKCE、JWT 承载器、设备、客户端凭证
- 客户端类型：机密 vs 公开
- 回调 URL / 重定向表面
- 需要的作用域
- 分发模型：仅本地组织 vs 可打包 / 多组织
- 是否需要证书或密钥轮换

---

## 工作流

### 1. 选择应用模型
使用上表中的决策表决定连接应用或 ECA 是否更适合长期使用。

### 2. 选择 OAuth 流

| 用例 | 默认流 |
|---|---|
| 后端 Web 应用 | 授权码 |
| SPA / 移动 / 公开客户端 | 授权码 + PKCE |
| 服务器到服务器 / CI/CD | JWT 承载器 |
| 设备 / CLI 认证 | 设备流 |
| 服务账户风格应用 | 客户端凭证（通常为 ECA） |

### 3. 从正确的模板开始
生成前请阅读相应的模板 — 不要从零开始构建：

| 模板 | 用例 |
|---|---|
| `assets/connected-app-basic.xml` | 简单 API 集成，最小 OAuth |
| `assets/connected-app-oauth.xml` | 具有完整 OAuth 2.0 配置的 Web 应用 |
| `assets/connected-app-jwt.xml` | JWT 承载器 / 服务器到服务器 |
| `assets/connected-app-canvas.xml` | 在 Salesforce UI 中嵌入外部应用（Canvas） |
| `assets/external-client-app.xml` | ECA 头文件 — 所有新的 ECA 构建从此开始 |
| `assets/eca-global-oauth.xml` | ECA 全局 OAuth 设置（作用域、PKCE、轮换） |
| `assets/eca-oauth-settings.xml` | ECA 每个应用的 OAuth 设置 |
| `assets/eca-policies.xml` | ECA 可配置策略 |

如果您需要源代码控制的 ECA OAuth 安全元数据，请先从组织中检索它，并将检索到的文件视为真实模式来源：
```sh
sf project retrieve start --metadata ExtlClntAppOauthSecuritySettings:<AppName> --target-org <alias>
```

### 4. 应用安全强化
阅读 `references/security-checklist.md` 获取完整的 120 点安全检查清单。优先考虑：
- 最小权限作用域
- 明确的回调 URL
- 对于公开客户端使用 PKCE
- 在适当情况下使用基于证书的认证
- 准备好轮换的密钥 / 密码处理
- 当实际且可维护时使用 IP 限制

### 5. 验证部署准备情况
在交接前阅读 `references/testing-validation-guide.md`。确认：
- 元数据文件命名正确（见下文注意事项）
- 作用域是合理的
- 回调和认证模型与实际客户端类型匹配
- 密钥未嵌入源代码中

### 6. 处理错误
如果部署失败，检查错误输出以查找：
- `DUPLICATE_VALUE` — 已存在此名称的连接应用或 ECA；重命名或检索后更新
- `INVALID_CROSS_REFERENCE_KEY` — ECA 设置文件中的 `externalClientApplication` 名称与 `.eca-meta.xml` 文件名不匹配
- `INSUFFICIENT_ACCESS_OR_READONLY` — 用户缺乏 "管理连接应用" 权限
- 如果任何步骤失败，不要继续下一步 — 使用上述具体消息向用户显示错误

---

## 规则 / 限制

| 规则 | 理由 |
|---|---|
| 永远不要将消费者密钥提交到源代码控制 | 凭证暴露风险 |
| 默认情况下永远不要使用 `Full` 作用域 | 不必要的权限；仅请求应用所需的作用域 |
| 对于公开客户端（移动、SPA）始终使用 PKCE | 防止认证码拦截 |
| 永远不要使用通配符或过于宽泛的回调 URL | 令牌拦截风险 |
| 编辑 ECA OAuth 安全设置前必须从组织检索 | 文件模式未完全记录；先检索确保准确性 |
| 在 CLI 命令中使用 `<alias>` 占位符，永远不要硬编码组织 URL | 组织 URL 因环境而异 |
| 在写入文件前从 `sfdx-project.json` 检测实际的 `packageDirectory` | 项目可能不使用默认的 `force-app/main/default/` 布局 |

---

## 元数据注意事项

### 连接应用
默认源位置（通过 `sfdx-project.json → packageDirectories` 验证）：
- `<packageDir>/connectedApps/`

### 外部客户端应用
ECA 元数据跨越多个顶层源目录。默认位置（通过 `sfdx-project.json` 验证）：

| 目录 | 元数据类型 | 文件后缀 |
|---|---|---|
| `<packageDir>/externalClientApps/` | `ExternalClientApplication` | `.eca-meta.xml` |
| `<packageDir>/extlClntAppGlobalOauthSets/` | `ExtlClntAppGlobalOauthSettings` | `.ecaGlblOauth-meta.xml` |
| `<packageDir>/extlClntAppOauthSettings/` | `ExtlClntAppOauthSettings` | `.ecaOauth-meta.xml` |
| `<packageDir>/extlClntAppOauthSecuritySettings/` | `ExtlClntAppOauthSecuritySettings` | `.ecaOauthSecurity-meta.xml` |
| `<packageDir>/extlClntAppOauthPolicies/` | `ExtlClntAppOauthConfigurablePolicies` | `.ecaOauthPlcy-meta.xml` |
| `<packageDir>/extlClntAppPolicies/` | `ExtlClntAppConfigurablePolicies` | `.ecaPlcy-meta.xml` |

---

## 注意事项

| 注意事项 | 详情 |
|---|---|
| `.ecaGlblOauth` 不是 `.ecaGlobalOauth` | 全局 OAuth 后缀是缩写 — 使用长形式将导致部署失败 |
| `.ecaPlcy` 不是 `.ecaPolicy` | 相同的缩写模式 — 通用策略后缀是简写形式 |
| 使用 `.ecaOauthSecurity` 而不是 `.ecaSecurity` | 对于安全设置使用 `.ecaOauthSecurity`，而不是 `.ecaSecurity` |
| ECA OAuth 安全设置是仅检索的 | 不能从源代码中创建 — 始终先从组织中检索 |
| Spring '26：新连接应用默认禁用 | 新组织阻止连接应用创建；除非明确需要兼容性，否则使用 ECA |
| 消费者密钥是在部署后生成的 | 您无法在元数据中设置消费者密钥 — 首次部署后检索 |

---

## 输出预期

完成时按顺序确认并报告：

1. **选择的应用类型** — 连接应用或外部客户端应用
2. **选择的 OAuth 流**
3. **创建或更新的文件** — 列出每个元数据文件路径
4. **安全决策** — 作用域、PKCE、证书、密钥、IP 策略
5. **下一步部署 / 测试步骤**

建议输出形状：
```text
应用: <name>
类型: 连接应用 | 外部客户端应用
流: <oauth 流>
文件: <路径>
安全: <作用域、PKCE、证书、密钥、IP 策略>
下一步: <部署、检索消费者密钥或测试认证流>
分数: <x>/120
```

---

## 跨技能集成

| 需求 | 转发至 | 理由 |
|---|---|---|
| 命名凭证 / 调用运行时配置 | [integration-connectivity-generate](../integration-connectivity-generate/SKILL.md) | 运行时集成设置 |
| 部署应用元数据 | `platform-metadata-deploy` 技能 | 组织验证和部署 |
| Apex 令牌或刷新处理 | `platform-apex-generate` 技能 | 实现逻辑 |

---

## 分数指南

| 分数 | 含义 |
|---|---|
| 80+ | 生产就绪的 OAuth 应用配置 |
| 54–79 | 可用但需要硬化审查 |
| < 54 | 部署前必须修复 |

---

## 参考文件索引

| 文件 | 何时阅读 |
|---|---|
| `assets/connected-app-basic.xml` | 第 3 步 — 简单连接应用模板，具有最小 OAuth |
| `assets/connected-app-oauth.xml` | 第 3 步 — 完整 OAuth 2.0 连接应用模板 |
| `assets/connected-app-jwt.xml` | 第 3 步 — JWT 承载器 / 服务器到服务器连接应用模板 |
| `assets/connected-app-canvas.xml` | 第 3 步 — 在 Salesforce UI 中嵌入 Canvas 应用模板 |
| `assets/external-client-app.xml` | 第 3 步 — ECA 头文件模板 |
| `assets/eca-global-oauth.xml` | 第 3 步 — ECA 全局 OAuth 设置模板 (PKCE、轮换、回调) |
| `assets/eca-oauth-settings.xml` | 第 3 步 — ECA 每个应用的 OAuth 设置模板 |
| `assets/eca-policies.xml` | 第 3 步 — ECA 可配置策略模板 |
| `references/oauth-flows-reference.md` | 第 2 步 — 详细 OAuth 流比较和决策指南 |
| `references/security-checklist.md` | 第 4 步 — 完整 120 点安全评分检查清单 |
| `references/testing-validation-guide.md` | 第 5 步 — 部署前验证和测试指南 |
| `references/migration-guide.md` | 在从连接应用到 ECA 模式迁移时 |
| `references/example-usage.md` | 常见 OAuth 场景的端到端示例 |
