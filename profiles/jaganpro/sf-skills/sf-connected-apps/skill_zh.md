# sf-connected-apps：Salesforce连接应用与外部客户端应用

当用户需要在Salesforce中配置**OAuth应用**时使用此技能：连接应用、外部客户端应用（ECAs）、JWT令牌设置、PKCE决策、作用域设计或从旧连接应用模式迁移到新ECA模式。

## 此技能负责任务的情况

当工作涉及以下内容时，使用`sf-connected-apps`：
- `.connectedApp-meta.xml`或`.eca-meta.xml`文件
- OAuth流程选择和回调/作用域设置
- JWT令牌认证、设备流程、客户端凭证或认证码决策
- 连接应用与外部客户端应用架构选择
- 消费者密钥/密钥/证书处理策略

当用户需要：
- 配置命名凭证或运行时调用 → [sf-integration](../sf-integration/SKILL.md)
- 分析访问/权限策略分配 → [sf-permissions](../sf-permissions/SKILL.md)
- 编写Apex令牌处理代码 → [sf-apex](../sf-apex/SKILL.md)
- 将元数据部署到组织 → [sf-deploy](../sf-deploy/SKILL.md)

---

## 首个决策：连接应用或外部客户端应用

| 如果需求是... | 倾向 |
|---|---|
| 简单单组织OAuth应用 | 连接应用 |
| 新开发并具有更好的密钥处理 | 外部客户端应用 |
| 多组织/打包/更强的操作控制 | 外部客户端应用 |
| 简单的遗留兼容性 | 连接应用 |

默认指导：
- 为新监管、可打包或自动化密集型解决方案选择**ECA**
- 当简单性和遗留兼容性更重要时选择**连接应用**
- Spring ’26注意：在组织中默认禁用新连接应用的创建。对于新集成，除非明确需要连接应用兼容性，否则请优先选择外部客户端应用。

---

## 首先收集的必要上下文

询问或推断：
- 应用类型：连接应用或ECA
- OAuth流程：认证码、PKCE、JWT令牌、设备、客户端凭证
- 客户类型：机密与公开
- 回调URL/重定向表面
- 需要的作用域
- 分发模型：仅本地组织与可打包/多组织
- 是否需要证书或密钥轮换

---

## 推荐的工作流程

### 1. 选择应用模型
决定连接应用或ECA是否更适合长期使用。

### 2. 选择OAuth流程
| 用例 | 默认流程 |
|---|---|
| 后端Web应用 | 认证码 |
| SPA/移动/公开客户端 | 认证码 + PKCE |
| 服务器到服务器/CI/CD | JWT令牌 |
| 设备/CLI认证 | 设备流程 |
| 服务账户风格应用 | 客户端凭证（通常为ECA） |

### 3. 从正确的模板开始
使用提供的资源而不是从头开始构建：
- `assets/connected-app-basic.xml`
- `assets/connected-app-oauth.xml`
- `assets/connected-app-jwt.xml`
- `assets/external-client-app.xml`
- `assets/eca-global-oauth.xml`
- `assets/eca-oauth-settings.xml`
- `assets/eca-policies.xml`

如果您需要源控制的ECA OAuth安全元数据，请先从组织中检索它，并将检索到的文件视为模式源：
- `sf project retrieve start --metadata ExtlClntAppOauthSecuritySettings:<AppName> --target-org <alias>`

### 4. 应用安全加固
优先考虑：
- 最小权限作用域
- 明确的回调URL
- 公开客户端使用PKCE
- 适当使用基于证书的认证
- 轮换就绪的密钥/密钥处理
- 当实际且可维护时使用IP限制

### 5. 验证部署准备情况
在交接前确认：
- 元数据文件命名正确
- 作用域合理
- 回调和认证模型与实际客户端类型匹配
- 密钥未嵌入源代码中

---

## 高信号安全规则

避免这些反模式：

| 反模式 | 为什么失败 |
|---|---|
| 通配符/过于宽泛的回调URL | 令牌拦截风险 |
| 默认Full作用域 | 不必要的权限 |
| 公开客户端禁用PKCE | 代码拦截风险 |
| 消费者密钥提交到源代码 | 凭证暴露 |
| 没有轮换/证书策略用于自动化 | 短期操作脆弱 |

默认修复方向：
- 狭作用域
- 限制回调
- 为公开客户端启用PKCE
- 将密钥保留在版本控制之外
- 在适当情况下使用JWT证书或受控密钥存储

---

## 重要的元数据说明

### 连接应用
通常位于：
- `force-app/main/default/connectedApps/`

### 外部客户端应用
当前的源支持的ECA元数据使用多个顶层源目录，而不是单个`externalClientApps/`文件夹：
- `force-app/main/default/externalClientApps/` → `ExternalClientApplication` (`.eca-meta.xml`)
- `force-app/main/default/extlClntAppGlobalOauthSets/` → `ExtlClntAppGlobalOauthSettings` (`.ecaGlblOauth-meta.xml`)
- `force-app/main/default/extlClntAppOauthSettings/` → `ExtlClntAppOauthSettings` (`.ecaOauth-meta.xml`)
- `force-app/main/default/extlClntAppOauthSecuritySettings/` → `ExtlClntAppOauthSecuritySettings` (`.ecaOauthSecurity-meta.xml`)
- `force-app/main/default/extlClntAppOauthPolicies/` → `ExtlClntAppOauthConfigurablePolicies` (`.ecaOauthPlcy-meta.xml`)
- `force-app/main/default/extlClntAppPolicies/` → `ExtlClntAppConfigurablePolicies` (`.ecaPlcy-meta.xml`)

重要的文件名陷阱：
- 全局OAuth后缀是`.ecaGlblOauth`，而不是`.ecaGlobalOauth`
- 一般策略后缀是`.ecaPlcy`，而不是`.ecaPolicy`
- 使用`.ecaOauthSecurity`用于`ExtlClntAppOauthSecuritySettings`

---

## 输出格式

完成时按此顺序报告：
1. **选择的应用类型**
2. **选择的OAuth流程**
3. **创建或更新的文件**
4. **安全决策**
5. **下一步部署/测试步骤**

建议格式：

```text
应用: <名称>
类型: 连接应用 | 外部客户端应用
流程: <OAuth流程>
文件: <路径>
安全: <作用域、PKCE、证书、密钥、IP策略>
下一步: <部署、检索消费者密钥或测试认证流程>
```

---

## 跨技能集成

| 需求 | 委托给 | 原因 |
|---|---|---|
| 命名凭证/调用运行时配置 | [sf-integration](../sf-integration/SKILL.md) | 运行时集成设置 |
| 部署应用元数据 | [sf-deploy](../sf-deploy/SKILL.md) | 组织验证和部署 |
| Apex令牌或刷新处理 | [sf-apex](../sf-apex/SKILL.md) | 实现逻辑 |
| 部署后的权限审查 | [sf-permissions](../sf-permissions/SKILL.md) | 访问治理 |

---

## 参考地图

### 从这里开始
- [references/oauth-flows-reference.md](references/oauth-flows-reference.md)
- [references/security-checklist.md](references/security-checklist.md)
- [references/testing-validation-guide.md](references/testing-validation-guide.md)

### 迁移/示例
- [references/migration-guide.md](references/migration-guide.md)
- [references/example-usage.md](references/example-usage.md)
- [assets/](assets/)

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 80+ | 生产就绪的OAuth应用配置 |
| 54–79 | 可用但需要加固审查 |
| < 54 | 修复前阻止部署 |
