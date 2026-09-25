# Playwright 最佳实践

这项技能为 Playwright 测试开发的各个方面提供全面的指导，从编写新测试到调试和维护现有测试套件。

## 基于活动的参考指南

根据您正在做什么，请参考以下指南：

### 编写新测试

**使用场景**：创建新的测试文件、编写测试用例、实现测试场景

| 活动                            | 参考文件                                                                                                                               |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **编写端到端测试**               | [test-suite-structure.md](core/test-suite-structure.md), [locators.md](core/locators.md), [assertions-waiting.md](core/assertions-waiting.md) |
| **编写组件测试**                 | [component-testing.md](testing-patterns/component-testing.md), [test-suite-structure.md](core/test-suite-structure.md)                        |
| **编写 API 测试**               | [api-testing.md](testing-patterns/api-testing.md), [test-suite-structure.md](core/test-suite-structure.md)                                    |
| **编写 GraphQL 测试**           | [graphql-testing.md](testing-patterns/graphql-testing.md), [api-testing.md](testing-patterns/api-testing.md)                                  |
| **编写视觉回归测试**           | [visual-regression.md](testing-patterns/visual-regression.md), [canvas-webgl.md](testing-patterns/canvas-webgl.md)                            |
| **使用 POM 结构化测试代码**  | [page-object-model.md](core/page-object-model.md), [test-suite-structure.md](core/test-suite-structure.md)                                    |
| **设置测试数据/ fixtures**   | [fixtures-hooks.md](core/fixtures-hooks.md), [test-data.md](core/test-data.md)                                                                |
| **处理身份验证**                 | [authentication.md](advanced/authentication.md), [authentication-flows.md](advanced/authentication-flows.md)                                  |
| **测试日期/时间功能**          | [clock-mocking.md](advanced/clock-mocking.md)                                                                                                 |
| **测试文件上传/下载**            | [file-operations.md](testing-patterns/file-operations.md), [file-upload-download.md](testing-patterns/file-upload-download.md)                |
| **测试表单/验证**              | [forms-validation.md](testing-patterns/forms-validation.md)                                                                                   |
| **测试拖拽和放置**             | [drag-drop.md](testing-patterns/drag-drop.md)                                                                                                 |
| **测试可访问性**               | [accessibility.md](testing-patterns/accessibility.md)                                                                                         |
| **测试安全性（XSS、CSRF）**    | [security-testing.md](testing-patterns/security-testing.md)                                                                                   |
| **使用测试注解**              | [annotations.md](core/annotations.md)                                                                                                         |
| **使用测试标签**                 | [test-tags.md](core/test-tags.md)                                                                                                             |
| **测试 iframe**                 | [iframes.md](browser-apis/iframes.md)                                                                                                         |
| **测试 canvas/WebGL**            | [canvas-webgl.md](testing-patterns/canvas-webgl.md)                                                                                           |
| **国际化（i18n）**             | [i18n.md](testing-patterns/i18n.md)                                                                                                           |
| **测试 Electron 应用**           | [electron.md](testing-patterns/electron.md)                                                                                                   |
| **测试浏览器扩展**              | [browser-extensions.md](testing-patterns/browser-extensions.md)                                                                               |

### 移动端和响应式测试

**使用场景**：测试移动设备、触摸交互、响应式布局

| 活动                        | 参考文件                                                                  |
| ------------------------------- | -------------------------------------------------------------------------------- |
| **设备模拟**            | [mobile-testing.md](advanced/mobile-testing.md)                                  |
| **触摸手势（滑动、点击）** | [mobile-testing.md](advanced/mobile-testing.md)                                  |
| **视口/断点测试**         | [mobile-testing.md](advanced/mobile-testing.md)                                  |
| **移动端特定 UI**          | [mobile-testing.md](advanced/mobile-testing.md), [locators.md](core/locators.md) |

### 实时和浏览器 API

**使用场景**：测试 WebSockets、地理位置、权限、多标签流程

| 活动                        | 参考文件                                                                          |
| ------------------------------- | ---------------------------------------------------------------------------------------- |
| **WebSocket/实时测试** | [websockets.md](browser-apis/websockets.md)                                              |
| **地理位置模拟**         | [browser-apis.md](browser-apis/browser-apis.md)                                          |
| **权限处理**         | [browser-apis.md](browser-apis/browser-apis.md)                                          |
| **剪贴板测试**           | [browser-apis.md](browser-apis/browser-apis.md)                                          |
| **相机/麦克风模拟**   | [browser-apis.md](browser-apis/browser-apis.md)                                          |
| **多标签/弹窗流程**       | [multi-context.md](advanced/multi-context.md)                                            |
| **OAuth 弹窗处理**        | [third-party.md](advanced/third-party.md), [multi-context.md](advanced/multi-context.md) |

### 调试和故障排除

**使用场景**：测试失败、元素未找到、超时、意外行为

| 活动                                          | 参考文件                                                                                                                                |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **调试测试失败**                       | [debugging.md](debugging/debugging.md), [assertions-waiting.md](core/assertions-waiting.md)                                                    |
| **修复不稳定测试**                            | [flaky-tests.md](debugging/flaky-tests.md), [debugging.md](debugging/debugging.md), [assertions-waiting.md](core/assertions-waiting.md)        |
| **调试不稳定并行运行**                 | [flaky-tests.md](debugging/flaky-tests.md), [performance.md](infrastructure-ci-cd/performance.md), [fixtures-hooks.md](core/fixtures-hooks.md) |
| **确保测试隔离 / 避免状态泄漏** | [flaky-tests.md](debugging/flaky-tests.md), [fixtures-hooks.md](core/fixtures-hooks.md), [performance.md](infrastructure-ci-cd/performance.md) |
| **修复选择器问题**                        | [locators.md](core/locators.md), [debugging.md](debugging/debugging.md)                                                                        |
| **调查超时问题**                  | [assertions-waiting.md](core/assertions-waiting.md), [debugging.md](debugging/debugging.md)                                                    |
| **使用跟踪查看器**                            | [debugging.md](debugging/debugging.md)                                                                                                         |
| **调试竞态条件**                     | [flaky-tests.md](debugging/flaky-tests.md), [debugging.md](debugging/debugging.md), [assertions-waiting.md](core/assertions-waiting.md)        |
| **调试控制台/JS 错误**                   | [console-errors.md](debugging/console-errors.md), [debugging.md](debugging/debugging.md)                                                       |

### 错误和边缘情况测试

**使用场景**：测试错误状态、离线模式、网络故障、验证

| 活动                       | 参考文件                                                                                       |
| ------------------------------ | ----------------------------------------------------------------------------------------------------- |
| **错误边界测试**     | [error-testing.md](debugging/error-testing.md)                                                        |
| **网络故障模拟**         | [error-testing.md](debugging/error-testing.md), [network-advanced.md](advanced/network-advanced.md)   |
| **离线模式测试**       | [error-testing.md](debugging/error-testing.md), [service-workers.md](browser-apis/service-workers.md) |
| **Service worker 测试**     | [service-workers.md](browser-apis/service-workers.md)                                                 |
| **加载状态测试**      | [error-testing.md](debugging/error-testing.md)                                                        |
| **表单验证测试**    | [error-testing.md](debugging/error-testing.md)                                                        |

### 多用户和协作测试

**使用场景**：测试涉及多个用户、角色或实时协作的功能

| 活动                       | 参考文件                                                                      |
| ------------------------------ | ------------------------------------------------------------------------------------ |
| **一个测试中多个用户** | [multi-user.md](advanced/multi-user.md)                                              |
| **实时协作**    | [multi-user.md](advanced/multi-user.md), [websockets.md](browser-apis/websockets.md) |
| **基于角色的访问测试**  | [multi-user.md](advanced/multi-user.md)                                              |
| **并发操作测试**  | [multi-user.md](advanced/multi-user.md)                                              |

### 架构决策

**使用场景**：选择测试模式、在方法之间进行选择、规划测试架构

| 活动                     | 参考文件                                           |
| ---------------------------- | --------------------------------------------------------- |
| **POM 与 fixtures 决策** | [pom-vs-fixtures.md](architecture/pom-vs-fixtures.md)     |
| **测试类型选择**      | [test-architecture.md](architecture/test-architecture.md) |
| **Mock 与真实服务**    | [when-to-mock.md](architecture/when-to-mock.md)           |
| **测试套件结构**     | [test-suite-structure.md](core/test-suite-structure.md)   |

### 框架特定测试

**使用场景**：测试 React、Angular、Vue 或 Next.js 应用

| 活动                  | 参考文件                     |
| ------------------------- | ----------------------------------- |
| **测试 React 应用**    | [react.md](frameworks/react.md)     |
| **测试 Angular 应用**  | [angular.md](frameworks/angular.md) |
| **测试 Vue/Nuxt 应用** | [vue.md](frameworks/vue.md)         |
| **测试 Next.js 应用**  | [nextjs.md](frameworks/nextjs.md)   |

### 重构和维护

**使用场景**：改进现有测试、代码审查、减少重复

| 活动                             | 参考文件                                                                                            |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| **重构为 Page Object Model** | [page-object-model.md](core/page-object-model.md), [test-suite-structure.md](core/test-suite-structure.md) |
| **改进测试组织**      | [test-suite-structure.md](core/test-suite-structure.md), [page-object-model.md](core/page-object-model.md) |
| **提取通用 setup/teardown** | [fixtures-hooks.md](core/fixtures-hooks.md)                                                                |
| **替换脆弱的选择器**      | [locators.md](core/locators.md)                                                                            |
| **移除显式等待**          | [assertions-waiting.md](core/assertions-waiting.md)                                                        |
| **创建测试数据工厂**     | [test-data.md](core/test-data.md)                                                                          |
| **配置设置**              | [configuration.md](core/configuration.md)                                                                  |

### 基础设施和配置

**使用场景**：设置项目、配置 CI/CD、优化性能

| 活动                                | 参考文件                                                                                                          |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **配置 Playwright 项目**      | [configuration.md](core/configuration.md), [projects-dependencies.md](core/projects-dependencies.md)                     |
| **设置 CI/CD 管道**          | [ci-cd.md](infrastructure-ci-cd/ci-cd.md), [github-actions.md](infrastructure-ci-cd/github-actions.md)                   |
| **GitHub Actions 设置**                | [github-actions.md](infrastructure-ci-cd/github-actions.md)                                                              |
| **GitLab CI 设置**                     | [gitlab.md](infrastructure-ci-cd/gitlab.md)                                                                              |
| **其他 CI 提供商**                  | [other-providers.md](infrastructure-ci-cd/other-providers.md)                                                            |
| **Docker/容器设置**              | [docker.md](infrastructure-ci-cd/docker.md)                                                                              |
| **全局 setup & teardown**             | [global-setup.md](core/global-setup.md)                                                                                  |
| **项目依赖**                | [projects-dependencies.md](core/projects-dependencies.md)                                                                |
| **优化测试性能**         | [performance.md](infrastructure-ci-cd/performance.md), [test-suite-structure.md](core/test-suite-structure.md)           |
| **配置并行执行**      | [parallel-sharding.md](infrastructure-ci-cd/parallel-sharding.md), [performance.md](infrastructure-ci-cd/performance.md) |
| **在 workers 之间隔离测试数据** | [fixtures-hooks.md](core/fixtures-hooks.md), [performance.md](infrastructure-ci-cd/performance.md)                       |
| **测试覆盖率**                       | [test-coverage.md](infrastructure-ci-cd/test-coverage.md)                                                                |
| **测试报告/工件**            | [reporting.md](infrastructure-ci-cd/reporting.md)                                                                        |

### 高级模式

**使用场景**：复杂场景、API 模拟、网络拦截

| 活动                             | 参考文件                                                                                              |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------ |
| **模拟 API 响应**            | [test-suite-structure.md](core/test-suite-structure.md), [network-advanced.md](advanced/network-advanced.md) |
| **网络拦截**             | [network-advanced.md](advanced/network-advanced.md), [assertions-waiting.md](core/assertions-waiting.md)     |
| **GraphQL 模拟**                  | [network-advanced.md](advanced/network-advanced.md)                                                          |
| **HAR 录制/回放**           | [network-advanced.md](advanced/network-advanced.md)                                                          |
| **自定义 fixtures**                  | [fixtures-hooks.md](core/fixtures-hooks.md)                                                                  |
| **高级等待策略**      | [assertions-waiting.md](core/assertions-waiting.md)                                                          |
| **OAuth/SSO 模拟**                | [third-party.md](advanced/third-party.md), [multi-context.md](advanced/multi-context.md)                     |
| **支付网关模拟**          | [third-party.md](advanced/third-party.md)                                                                    |
| **电子邮件/SMS 验证模拟**   | [third-party.md](advanced/third-party.md)                                                                    |
| **在控制台错误时失败**        | [console-errors.md](debugging/console-errors.md)                                                             |
| **安全性测试（XSS、CSRF）**     | [security-testing.md](testing-patterns/security-testing.md)                                                  |
| **性能预算和 Web Vitals** | [performance-testing.md](testing-patterns/performance-testing.md)                                            |
| **Lighthouse 集成**           | [performance-testing.md](testing-patterns/performance-testing.md)                                            |
| **测试注解（跳过、fixme）**   | [annotations.md](core/annotations.md)                                                                        |
| **测试标签（@smoke、@fast）**        | [test-tags.md](core/test-tags.md)                                                                            |
| **用于报告的测试步骤**         | [annotations.md](core/annotations.md)                                                                        |

## 快速决策树

```
你在做什么？
│
├─ 写一个新测试？
│  ├─ 端到端测试 → core/test-suite-structure.md, core/locators.md, core/assertions-waiting.md
│  ├─ 组件测试 → testing-patterns/component-testing.md
│  ├─ API 测试 → testing-patterns/api-testing.md, core/test-suite-structure.md
│  ├─ GraphQL 测试 → testing-patterns/graphql-testing.md
│  ├─ 视觉回归 → testing-patterns/visual-regression.md
│  ├─ 视觉/canvas 测试 → testing-patterns/canvas-webgl.md, core/test-suite-structure.md
│  ├─ 可访问性测试 → testing-patterns/accessibility.md
│  ├─ 移动端/响应式测试 → advanced/mobile-testing.md
│  ├─ i18n/本地化测试 → testing-patterns/i18n.md
│  ├─ Electron 应用测试 → testing-patterns/electron.md
│  ├─ 浏览器扩展测试 → testing-patterns/browser-extensions.md
│  ├─ 多用户测试 → advanced/multi-user.md
│  ├─ 表单验证测试 → testing-patterns/forms-validation.md
│  └─ 拖拽和放置测试 → testing-patterns/drag-drop.md
│
├─ 测试特定功能？
│  ├─ 文件上传/下载 → testing-patterns/file-operations.md, testing-patterns/file-upload-download.md
│  ├─ 依赖日期/时间 → advanced/clock-mocking.md
│  ├─ WebSocket/实时 → browser-apis/websockets.md
│  ├─ 地理位置/权限 → browser-apis/browser-apis.md
│  ├─ OAuth/SSO 模拟 → advanced/third-party.md, advanced/multi-context.md
│  ├─ 支付/电子邮件/SMS → advanced/third-party.md
│  ├─ iFrames → browser-apis/iframes.md
│  ├─ Canvas/WebGL/图表 → testing-patterns/canvas-webgl.md
│  ├─ Service workers/PWA → browser-apis/service-workers.md
│  ├─ i18n/本地化 → testing-patterns/i18n.md
│  ├─ 安全性（XSS、CSRF）→ testing-patterns/security-testing.md
│  └─ 性能/Web Vitals → testing-patterns/performance-testing.md
│
├─ 架构决策？
│  ├─ POM vs fixtures → architecture/pom-vs-fixtures.md
│  ├─ 测试类型选择 → architecture/test-architecture.md
│  ├─ Mock vs 真实服务 → architecture/when-to-mock.md
│  └─ 测试套件结构 → core/test-suite-structure.md
│
├─ 框架特定测试？
│  ├─ React 应用 → frameworks/react.md
│  ├─ Angular 应用 → frameworks/angular.md
│  ├─ Vue/Nuxt 应用 → frameworks/vue.md
│  └─ Next.js 应用 → frameworks/nextjs.md
│
├─ 身份验证测试？
│  ├─ 基本身份验证模式 → advanced/authentication.md
│  └─ 复杂流程（MFA、重置）→ advanced/authentication-flows.md
│
├─ 测试失败/不稳定？
│  ├─ 不稳定测试调查 → debugging/flaky-tests.md
│  ├─ 元素未找到 → core/locators.md, debugging/debugging.md
│  ├─ 超时问题 → core/assertions-waiting.md, debugging/debugging.md
│  ├─ 竞态条件 → debugging/flaky-tests.md, debugging/debugging.md
│  ├─ 仅在多个 workers 时不稳定 → debugging/flaky-tests.md, infrastructure-ci-cd/performance.md
│  ├─ 状态泄漏 / 隔离 → debugging/flaky-tests.md, core/fixtures-hooks.md
│  ├─ 控制台/JS 错误 → debugging/console-errors.md, debugging/debugging.md
│  └─ 一般调试 → debugging/debugging.md
│
├─ 测试错误场景？
│  ├─ 网络故障 → debugging/error-testing.md, advanced/network-advanced.md
│  ├─ 离线（意外）→ debugging/error-testing.md
│  ├─ 离线优先/PWA → browser-apis/service-workers.md
│  ├─ 错误边界 → debugging/error-testing.md
│  └─ 表单验证 → testing-patterns/forms-validation.md, debugging/error-testing.md
│
├─ 重构现有代码？
│  ├─ 实现POM → core/page-object-model.md
│  ├─ 改进选择器 → core/locators.md
│  ├─ 提取 fixtures → core/fixtures-hooks.md
│  ├─ 创建数据工厂 → core/test-data.md
│  └─ 配置设置 → core/configuration.md
│
├─ 设置基础设施？
│  ├─ CI/CD → infrastructure-ci-cd/ci-cd.md
│  ├─ GitHub Actions → infrastructure-ci-cd/github-actions.md
│  ├─ GitLab CI → infrastructure-ci-cd/gitlab.md
│  ├─ 其他 CI 提供商 → infrastructure-ci-cd/other-providers.md
│  ├─ Docker/容器 → infrastructure-ci-cd/docker.md
│  ├─ 分片/并行 → infrastructure-ci-cd/parallel-sharding.md
│  ├─ 报告/工件 → infrastructure-ci-cd/reporting.md
│  ├─ 全局 setup/teardown → core/global-setup.md
│  ├─ 项目依赖 → core/projects-dependencies.md
│  ├─ 测试性能 → infrastructure-ci-cd/performance.md
│  ├─ 测试覆盖率 → infrastructure-ci-cd/test-coverage.md
│  └─ 项目配置 → core/configuration.md, core/projects-dependencies.md
│
├─ 组织测试？
│  ├─ 跳过/fixme/慢测试 → core/annotations.md
│  ├─ 测试标签（@smoke、@fast）→ core/test-tags.md
│  ├─ 过滤测试（--grep）→ core/test-tags.md
│  ├─ 测试步骤 → core/annotations.md
│  └─ 条件执行 → core/annotations.md
│
└─ 运行测试子集？
   ├─ 通过标签（@smoke、@critical）→ core/test-tags.md
   ├─ 排除慢/不稳定测试 → core/test-tags.md
   ├─ PR vs 夜间测试 → core/test-tags.md, infrastructure-ci-cd/ci-cd.md
   └─ 项目特定过滤 → core/test-tags.md, core/configuration.md
```

## 测试验证循环

编写或修改测试后：

1. **运行测试**：`npx playwright test --reporter=list`
2. **如果测试失败**：
   - 查看错误输出和跟踪 (`npx playwright show-trace`)
   - 修复定位器、等待或断言
   - 重新运行测试
3. **仅当所有测试通过时继续**
4. **对关键测试多次运行**：`npx playwright test --repeat-each=5`
