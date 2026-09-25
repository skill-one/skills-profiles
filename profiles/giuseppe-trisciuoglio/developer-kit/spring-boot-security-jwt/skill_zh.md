# Spring Boot JWT 安全

使用 Spring Security 6.x 和 JJWT 为 Spring Boot 3.5.x 实现的 JWT 认证和授权模式。涵盖令牌生成、验证、刷新策略、RBAC/ABAC 和 OAuth2 集成。

## 概述

此技能为 Spring Boot 应用程序中的无状态 JWT 认证提供实现模式。它涵盖了完整的认证流程，包括使用 JJWT 0.12.6 生成令牌、基于 Bearer/cookie 的认证、刷新令牌轮换以及使用 `@PreAuthorize` 表达式的方法级授权。

主要功能：
- 具有可配置过期时间的访问令牌和刷新令牌生成
- Bearer 令牌和 HttpOnly cookie 认证策略
- 与 Spring Data JPA 和 OAuth2 提供商的集成
- 基于角色/权限的 RBAC `@PreAuthorize` 规则
- 令牌吊销和黑名单用于登出/轮换

## 何时使用

当用户请求涉及以下内容时激活：
- "实现 JWT 认证"、"使用令牌安全 REST API"
- "Spring Security 6.x 配置"、"SecurityFilterChain 设置"
- "基于角色的访问控制"、"RBAC"、"`` `@PreAuthorize` `"`
- "刷新令牌"、"令牌轮换"、"令牌吊销"
- "OAuth2 集成"、"社交登录"、"Google/GitHub 认证"
- "无状态认证"、"SPA 后端安全"
- "JWT 过滤器"、"OncePerRequestFilter"、"Bearer 令牌"
- "基于 cookie 的 JWT"、"HttpOnly cookie"
- "基于权限的访问控制"、"自定义 PermissionEvaluator"

## 快速参考

### 依赖项 (JJWT 0.12.6)

| 艺术品 | 范围 |
|----------|-------|
| `spring-boot-starter-security` | 编译 |
| `spring-boot-starter-oauth2-resource-server` | 编译 |
| `io.jsonwebtoken:jjwt-api:0.12.6` | 编译 |
| `io.jsonwebtoken:jjwt-impl:0.12.6` | 运行时 |
| `io.jsonwebtoken:jjwt-jackson:0.12.6` | 运行时 |
| `spring-security-test` | 测试 |

有关 Maven 和 Gradle 拼贴的详细信息，请参阅 [references/jwt-quick-reference.md](references/jwt-quick-reference.md)。

### 关键配置属性

| 属性 | 示例值 | 备注 |
|----------|--------------|-------|
| `jwt.secret` | `${JWT_SECRET}` | 最小 256 位，切勿硬编码 |
| `jwt.access-token-expiration` | `900000` | 15 分钟（毫秒） |
| `jwt.refresh-token-expiration` | `604800000` | 7 天（毫秒） |
| `jwt.issuer` | `my-app` | 每个令牌都进行验证 |
| `jwt.cookie-name` | `jwt-token` | 用于基于 cookie 的认证 |
| `jwt.cookie-http-only` | `true` | 生产环境中始终为 true |
| `jwt.cookie-secure` | `true` | 使用 HTTPS 时始终为 true |

### 授权注解

| 注解 | 示例 |
|-----------|---------|
| `@PreAuthorize("hasRole('ADMIN')")` | 角色检查 |
| `@PreAuthorize("hasAuthority('USER_READ')")` | 权限检查 |
| `@PreAuthorize("hasPermission(#id, 'Doc', 'READ')")` | 域对象检查 |
| `@PreAuthorize("@myService.canAccess(#id)")` | Spring bean 检查 |

## 说明

### 第 1 步 — 添加依赖项

在构建文件中包含 `spring-boot-starter-security`、`spring-boot-starter-oauth2-resource-server` 和三个 JJWT 艺术品。有关确切的 Maven/Gradle 拼贴，请参阅 [references/jwt-quick-reference.md](references/jwt-quick-reference.md)。

### 第 2 步 — 配置 application.yml

```yaml
jwt:
  secret: ${JWT_SECRET:change-me-min-32-chars-in-production}
  access-token-expiration: 900000
  refresh-token-expiration: 604800000
  issuer: my-app
  cookie-name: jwt-token
  cookie-http-only: true
  cookie-secure: false   # true in production
```

有关完整属性参考，请参阅 [references/jwt-complete-configuration.md](references/jwt-complete-configuration.md)。

### 第 3 步 — 实现 JwtService

核心操作：生成访问令牌、生成刷新令牌、提取用户名、验证令牌。

```java
@Service
public class JwtService {

    public String generateAccessToken(UserDetails userDetails) {
        return Jwts.builder()
            .subject(userDetails.getUsername())
            .issuer(issuer)
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + accessTokenExpiration))
            .claim("authorities", getAuthorities(userDetails))
            .signWith(getSigningKey())
            .compact();
    }

    public boolean isTokenValid(String token, UserDetails userDetails) {
        try {
            String username = extractUsername(token);
            return username.equals(userDetails.getUsername()) && !isTokenExpired(token);
        } catch (JwtException e) {
            return false;
        }
    }
}
```

有关完整的 JwtService（包括密钥管理和声明提取），请参阅 [references/jwt-complete-configuration.md](references/jwt-complete-configuration.md)。

### 第 4 步 — 创建 JwtAuthenticationFilter

扩展 `OncePerRequestFilter` 以从 `Authorization: Bearer` 标头（或 HttpOnly cookie）中提取 JWT，验证它，并设置 `SecurityContext`。

```java
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request,
            HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        String authHeader = request.getHeader("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            chain.doFilter(request, response);
            return;
        }
        String jwt = authHeader.substring(7);
        String username = jwtService.extractUsername(jwt);
        if (username != null && SecurityContextHolder.getContext().getAuthentication() == null) {
            UserDetails userDetails = userDetailsService.loadUserByUsername(username);
            if (jwtService.isTokenValid(jwt, userDetails)) {
                UsernamePasswordAuthenticationToken authToken =
                    new UsernamePasswordAuthenticationToken(
                        userDetails, null, userDetails.getAuthorities());
                authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                SecurityContextHolder.getContext().setAuthentication(authToken);
            }
        }
        chain.doFilter(request, response);
    }
}
```

有关基于 cookie 的变体，请参阅 [references/configuration.md](references/configuration.md)。

### 第 5 步 — 配置 SecurityFilterChain

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(AbstractHttpConfigurer::disable)
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**", "/swagger-ui/**").permitAll()
                .anyRequest().authenticated()
            )
            .authenticationProvider(authenticationProvider)
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class)
            .build();
    }
}
```

有关 CORS、登出处理程序和 OAuth2 登录集成的详细信息，请参阅 [references/jwt-complete-configuration.md](references/jwt-complete-configuration.md)。

### 第 6 步 — 创建认证端点

通过 `@RestController` 暴露 `/register`、`/authenticate`、`/refresh` 和 `/logout`。在响应正文中返回 `accessToken` + `refreshToken`（并可选地设置 HttpOnly cookie）。

有关完整的 `AuthenticationController` 和 `AuthenticationService`，请参阅 [references/examples.md](references/examples.md)。

### 第 7 步 — 实现刷新令牌策略

将刷新令牌存储在具有 `user_id`、`expiry_date`、`revoked` 和 `expired` 列的数据库中。在 `/refresh` 上，验证存储的令牌，吊销它，并签发新对（令牌轮换）。

有关 `RefreshToken` 实体、轮换逻辑和基于 Redis 的黑名单，请参阅 [references/token-management.md](references/token-management.md)。

### 第 8 步 — 添加授权规则

使用 `@EnableMethodSecurity` 和 `@PreAuthorize` 注解进行细粒度控制：

```java
@PreAuthorize("hasRole('ADMIN')")
public Page<UserResponse> getAllUsers(Pageable pageable) { ... }

@PreAuthorize("hasPermission(#documentId, 'Document', 'READ')")
public Document getDocument(Long documentId) { ... }
```

有关 RBAC 实体模型、`PermissionEvaluator` 和 ABAC 模式的详细信息，请参阅 [references/authorization-patterns.md](references/authorization-patterns.md)。

### 第 9 步 — 编写安全测试

```java
@SpringBootTest
@AutoConfigureMockMvc
class AuthControllerTest {

    @Test
    void shouldDenyAccessWithoutToken() throws Exception {
        mockMvc.perform(get("/api/orders"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    void shouldAllowAdminAccess() throws Exception {
        mockMvc.perform(get("/api/admin/users"))
            .andExpect(status().isOk());
    }
}
```

有关完整测试套件、Testcontainers 设置和安全测试清单，请参阅 [references/testing.md](references/testing.md) 和 [references/jwt-testing-guide.md](references/jwt-testing-guide.md)。

## 最佳实践

### 令牌安全
- 使用至少 256 位的密钥 — 从环境变量加载，切勿硬编码
- 设置较短的访问令牌生命周期（15 分钟）；使用刷新令牌进行更长的会话
- 实现令牌轮换：在签发新刷新令牌时吊销旧的刷新令牌
- 使用 `jti`（JWT ID）声明进行登出时的黑名单

### Cookie 与 Bearer 标头
- 对于浏览器客户端，优先使用 HttpOnly cookie（XSS 安全）
- 对于移动/API 客户端，使用 `Authorization: Bearer` 标头
- 在生产环境中为 cookie 设置 `Secure`、`SameSite=Lax` 或 `Strict`

### Spring Security 6.x
- 使用 `SecurityFilterChain` bean — 切勿扩展 `WebSecurityConfigurerAdapter`
- 仅对无状态 API 禁用 CSRF；对于基于会话的流程，保持其启用
- 使用 `@EnableMethodSecurity` 而不是已弃用的 `@EnableGlobalMethodSecurity`
- 验证 `iss` 和 `aud` 声明；拒绝来自不可信发布者的令牌

### 性能
- 使用 `@Cacheable` 缓存 `UserDetails` 以避免每次请求都进行数据库查找
- 缓存签名密钥派生（避免每次请求重新计算 HMAC 密钥）
- 在大规模情况下使用 Redis 存储刷新令牌

### 不要做的事情
- 不要在 JWT 声明中存储敏感数据（密码、PII）—— 声明仅签名，未加密
- 不要签发具有无限生命周期的令牌
- 不要在不验证签名和过期的情况下接受令牌
- 不要在环境中共享签名密钥

## 示例

### 基本认证流程

```java
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/authenticate")
    public ResponseEntity<AuthResponse> authenticate(
            @RequestBody LoginRequest request) {
        return ResponseEntity.ok(authService.authenticate(request));
    }

    @PostMapping("/refresh")
    public ResponseEntity<AuthResponse> refresh(@RequestBody RefreshRequest request) {
        return ResponseEntity.ok(authService.refreshToken(request.refreshToken()));
    }

    @PostMapping("/logout")
    public ResponseEntity<Void> logout() {
        authService.logout();
        return ResponseEntity.ok().build();
    }
}
```

### 控制器方法的 JWT 授权

```java
@RestController
@RequestMapping("/api/admin")
@PreAuthorize("hasRole('ADMIN')")
public class AdminController {

    @GetMapping("/users")
    public ResponseEntity<List<UserResponse>> getAllUsers() {
        return ResponseEntity.ok(adminService.getAllUsers());
    }
}
```

有关完整的实体模型和服务实现，请参阅 [references/examples.md](references/examples.md)。

## 参考

| 文件 | 内容 |
|------|---------|
| [references/jwt-quick-reference.md](references/jwt-quick-reference.md) | 依赖项、最小服务、常见模式 |
| [references/jwt-complete-configuration.md](references/jwt-complete-configuration.md) | 完整配置：属性、SecurityFilterChain、JwtService、OAuth2 RS |
| [references/configuration.md](references/configuration.md) | JWT 配置 bean、CORS、CSRF、错误处理、会话选项 |
| [references/examples.md](references/examples.md) | 完整应用程序设置：控制器、服务、实体 |
| [references/authorization-patterns.md](references/authorization-patterns.md) | RBAC/ABAC 实体模型、PermissionEvaluator、SpEL 表达式 |
| [references/token-management.md](references/token-management.md) | 刷新令牌实体、轮换、使用 Redis 的吊销 |
| [references/testing.md](references/testing.md) | 单元和 MockMvc 测试、测试实用程序 |
| [references/jwt-testing-guide.md](references/jwt-testing-guide.md) | Testcontainers、负载测试、安全测试清单 |
| [references/security-hardening.md](references/security-hardening.md) | 安全标头、HSTS、速率限制、审计日志 |
| [references/performance-optimization.md](references/performance-optimization.md) | Caffeine 缓存配置、异步验证、连接池 |
| [references/oauth2-integration.md](references/oauth2-integration.md) | Google/GitHub OAuth2 登录、OAuth2UserService |
| [references/microservices-security.md](references/microservices-security.md) | 服务间 JWT 传播、资源服务器配置 |
| [references/migration-spring-security-6x.md](references/migration-spring-security-6x.md) | 从 Spring Security 5.x 迁移 |
| [references/troubleshooting.md](references/troubleshooting.md) | 常见错误、调试技巧 |

## 限制和警告

### 安全限制
- JWT 令牌是签名的，但未加密 — 不要在声明中包含敏感数据
- 在信任令牌之前，始终验证 `exp`、`iss` 和 `aud` 声明
- 签名密钥必须至少为 256 位；在生产中切勿使用弱密钥
- 从环境变量或安全保险库加载密钥，切勿从配置文件中加载
- SameSite cookie 属性对于基于 cookie 的流程中的 CSRF 保护至关重要

### Spring Security 6.x 限制
- `WebSecurityConfigurerAdapter` 已移除 — 仅使用 `SecurityFilterChain` bean
- `@EnableGlobalMethodSecurity` 已弃用 — 使用 `@EnableMethodSecurity`
- `HttpSecurity` 配置需要 Lambda DSL（无法进行方法链接）
- `WebSecurityConfigurerAdapter.order()` 已被 `@Order` on `@Configuration` 类替换

### 令牌限制
- 访问令牌应在 5-15 分钟内过期，以提高安全性
- 刷新令牌应存储在服务器端（数据库或 Redis），切勿存储在 localStorage
- 实现令牌黑名单，以便在登出时立即吊销
- `jti` 声明对于令牌黑名单正常工作至关重要

## 相关技能

- `spring-boot-dependency-injection` — 全程使用的构造函数注入模式
- `spring-boot-rest-api-standards` — REST API 安全模式和错误处理
- `unit-test-security-authorization` — 测试 Spring Security 配置
- `spring-data-jpa` — 用户实体和存储库模式
- `spring-boot-actuator` — 安全监控和健康端点
