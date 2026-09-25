# TypeScript 文档

使用分层架构为多个受众生成生产就绪型 TypeScript 文档。支持使用 TypeDoc、ADR 和特定框架模式生成 API 文档。

## 概述

使用 JSDoc 注释进行内联文档说明，使用 TypeDoc 生成 API 参考，使用 ADR 跟踪设计决策。

**主要功能：**
- TypeDoc 配置和 API 文档生成
- 所有 TypeScript 构造的 JSDoc 模式
- ADR 创建和维护
- 特定框架模式（NestJS、React、Express、Angular、Vue）
- 用于文档质量的 ESLint 验证规则
- GitHub Actions 管道设置

## 何时使用

在创建 API 文档、架构决策记录、代码示例或特定框架模式（NestJS、Express、React、Angular 或 Vue）时使用此技能。

## 快速参考

| 工具 | 目的 | 命令 |
|------|---------|---------|
| TypeDoc | API 文档生成 | `npx typedoc` |
| Compodoc | Angular 文档 | `npx compodoc -p tsconfig.json` |
| ESLint JSDoc | 文档验证 | `eslint --ext .ts src/` |

### JSDoc 标签

| 标签 | 用途 |
|-----|----------|
| `@param` | 文档参数 |
| `@returns` | 文档返回值 |
| `@throws` | 文档错误条件 |
| `@example` | 提供代码示例 |
| `@remarks` | 添加实现说明 |
| `@see` | 跨引用相关项 |
| `@deprecated` | 标记已弃用的 API |

## 说明

### 1. 配置 TypeDoc

```bash
npm install --save-dev typedoc typedoc-plugin-markdown
```

```json
{
  "entryPoints": ["src/index.ts"],
  "out": "docs/api",
  "theme": "markdown",
  "excludePrivate": true,
  "readme": "README.md"
}
```

### 2. 添加 JSDoc 注释

```typescript
/**
 * 管理用户认证的服务
 *
 * @remarks
 * 处理基于 JWT 的认证，使用 bcrypt 密码哈希。
 *
 * @example
 * ```typescript
 * const authService = new AuthService(config);
 * const token = await authService.login(email, password);
 * ```
 *
 * @security
 * - 密码使用 bcrypt 哈希（成本因子 12）
 * - JWT 令牌使用 RS256 签名
 */
@Injectable()
export class AuthService {
  /**
   * 验证用户并返回访问令牌
   * @param credentials - 用户登录凭证
   * @returns 认证结果及令牌
   * @throws {InvalidCredentialsError} 如果凭证无效
   */
  async login(credentials: LoginCredentials): Promise<AuthResult> {
    // 实现
  }
}
```

### 3. 创建 ADR

```markdown
# ADR-001: TypeScript 严格模式配置

## 状态
已接受

## 背景
是什么问题促使我们做出此决策？

## 决策
我们提议的变更是什么？

## 后果
哪些事情变得更容易或更困难？
```

### 4. 设置 CI/CD 管道

```yaml
name: 文档
on:
  push:
    branches: [main]
    paths: ['src/**', 'docs/**']

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run docs:generate
      - run: npm run docs:validate
```

### 5. 验证文档

```json
{
  "rules": {
    "jsdoc/require-description": "error",
    "jsdoc/require-param-description": "error",
    "jsdoc/require-returns-description": "error",
    "jsdoc/require-example": "warn"
  }
}
```

**如果验证失败：** 审查 ESLint 错误，修复 JSDoc 注释（添加缺失的描述，在缺少 `@param`/`@returns`/`@throws` 的地方添加），重新运行 `eslint --ext .ts src/` 直到所有错误通过，然后提交。

## 示例

### 文档化一个 React Hook

```typescript
/**
 * 获取分页数据的自定义 Hook
 *
 * @remarks
 * 此 Hook 管理加载状态、错误处理，并在页面或筛选器变化时自动重新获取。
 *
 * @example
 * ```tsx
 * function UserList() {
 *   const { data, isLoading, error } = usePaginatedData('/api/users', {
 *     page: currentPage,
 *     limit: 10
 *   });
 *
 *   if (isLoading) return <Spinner />;
 *   if (error) return <ErrorMessage error={error} />;
 *   return <UserTable users={data.items} />;
 * }
 * ```
 *
 * @param endpoint - 获取数据的 API 端点
 * @param options - 分页和筛选选项
 * @returns 分页响应，包含项和元数据
 */
export function usePaginatedData<T>(
  endpoint: string,
  options: PaginationOptions
): UsePaginatedDataResult<T> {
  // 实现
}
```

### 文档化一个工具函数

```typescript
/**
 * 使用 RFC 5322 规范验证电子邮件地址
 *
 * @param email - 要验证的电子邮件地址
 * @returns 如果电子邮件格式有效则为 True
 *
 * @example
 * ```typescript
 * isValidEmail('user@example.com'); // true
 * isValidEmail('invalid-email');      // false
 * ```
 *
 * @performance
 * 时间复杂度为 O(n)，n 为电子邮件字符串长度
 *
 * @see {@link https://tools.ietf.org/html/rfc5322} RFC 5322 规范
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}
```

### NestJS 控制器文档

```typescript
/**
 * 用户管理的 REST API 端点
 *
 * @remarks
 * 所有端点都需要通过 Bearer 令牌进行认证。
 * 速率限制：每个用户每分钟 100 个请求。
 *
 * @example
 * ```bash
 * curl -H "Authorization: Bearer <token>" https://api.example.com/users/123
 * ```
 *
 * @security
 * - 所有端点使用 HTTPS
 * - JWT 令牌在 1 小时后过期
 * - 日志中会隐去敏感数据
 */
@Controller('users')
export class UsersController {
  /**
   * 通过 ID 获取用户
   * @param id - 用户 UUID
   * @returns 用户资料（不包括密码）
   */
  @Get(':id')
  async getUser(@Param('id') id: string): Promise<UserProfile> {
    // 实现
  }
}
```

## 最佳实践

1. **文档化公共 API**：所有公共方法、类和接口
2. **使用 `@example`**：为复杂函数提供可运行的示例
3. **包含 `@throws`**：文档化所有可能的错误
4. **添加 `@see`**：跨引用相关函数/类型
5. **使用 `@remarks`**：添加实现细节和说明
6. **文档化泛型**：解释泛型约束和使用方式
7. **包含性能说明**：文档化时间/空间复杂度
8. **添加安全警告**：突出安全注意事项
9. **保持更新**：代码变更时更新文档
10. **不要文档化明显代码**：关注为什么，而不是什么

## 限制和警告

- **私有成员**：使用 `@private` 或从 TypeDoc 输出中排除
- **复杂类型**：文档化泛型约束和类型参数
- **重大变更**：使用 `@deprecated` 并提供迁移指南
- **安全信息**：绝不在文档中包含秘密或凭证
- **链接有效性**：确保 `@see` 引用指向有效位置
- **示例代码**：所有示例应该是可运行的并经过测试
- **版本控制**：保持文档与代码版本同步

## 参考

- **[references/jsdoc-patterns.md](references/jsdoc-patterns.md)** — 接口、函数、类、泛型和联合的 JSDoc 模式
- **[references/framework-patterns.md](references/framework-patterns.md)** — NestJS、React、Express 和 Angular 的特定框架模式
- **[references/adr-patterns.md](references/adr-patterns.md)** — ADR 模板和示例
- **[references/pipeline-setup.md](references/pipeline-setup.md)** — 文档的 CI/CD 管道配置
- **[references/validation.md](references/validation.md)** — ESLint 规则和验证清单
- **[references/typedoc-configuration.md](references/typedoc-configuration.md)** — 完整的 TypeDoc 配置选项
- **[references/examples.md](references/examples.md)** — 额外的代码示例
