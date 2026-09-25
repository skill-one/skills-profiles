<!-- GENERATED from convex-agents content/capabilities/convex-verify.json — do not edit by hand. -->

# 证明功能正常工作 — 种子化、驱动、断言

绿色的类型检查仅证明代码能解析，并不能证明非所有者被实际拒绝、查询返回正确的行，或变异操作产生其声称的效果。这项能力通过全领域都缺失的循环来弥补这一差距：种子化 → 驱动 → 断言，通过 `convex-test` 在进程内运行，无需部署。其最有价值的断言是负面的断言——即应该被拒绝的调用者，因为这些正是 30 个应用语料库显示的 #1 真实 Bug，也是快乐路径演示永远无法捕获的授权缺陷。

## 工作流程

1.  **识别要证明的功能**：用户刚刚构建/更改的具体导出查询/变异/操作（或一小部分），及其预期行为——谁应该被允许、应该返回什么数据、变异应该改变什么。如果意图未说明，应提出一个专注的问题，而不是猜测合约。
2.  **设置 `convex-test`**：确保 `convex-test` + `vitest` 是开发依赖项，并且 `vitest.config.ts` 设置 `test.environment: "edge-runtime"` 并将 `server.deps.inline` 设置为 `["convex-test"]`——没有这个配置，`convexTest(schema)` 在运行时会因为 `import.meta.glob is not a function` 而失败（已验证）。同时安装 `@edge-runtime/vm`。然后 `convexTest(schema)` 会返回一个 `t` 处理器。如果项目已有测试设置，请重用（与 `test` 能力组合，不要分支它）。
3.  **通过应用程序自己的函数种子化真实数据**（这样种子化会执行与真实用户相同的验证器/变异操作），如果公共 API 无法创建固定数据，则回退到 `t.run(async (ctx) => ctx.db.insert(...))`。至少种子化：调用者自己的行和另一个用户的行，以便可以测试跨用户访问。
4.  **使用 `t.withIdentity({ subject, tokenIdentifier, ... })` 以不同的身份驱动功能**：调用函数作为 (a) 合法的所有者，(b) 其他经过身份验证的用户，以及 (c) 未经过身份验证的用户（无身份的 `t`）。使用应用程序身份验证使用的真实身份形状（subject/tokenIdentifier），匹配所有权解析方式。
5.  **断言行为——正面和负面**：
    - 正面：所有者获得预期的行 / 变异操作做出了预期的改变 (`expect(await t.withIdentity(owner).query(api.x.y, args)).toEqual(...)`).
    - 负面（承重部分）：不同用户调用相同函数被拒绝——`await expect(t.withIdentity(other).mutation(api.x.cancel, {id})).rejects.toThrow(/forbidden|not authorized|403/)`——并且需要身份验证的地方，未经过身份验证的调用者也被拒绝。直到证明错误调用者被阻止，功能才算被证明。
    - 数据范围：列表/查询只返回调用者的行，从不返回第二个用户的行（断言第二个用户的行不存在）。
6.  **运行测试 (`npx vitest run`) 并报告**：证明的内容（每个通过的正面和负面断言），以及——关键地——任何失败的断言，因为失败的负面断言是在发布前发现的真实授权漏洞。对任何未按预期行为的内容，在总线上发出发现（specs/finding.schema.json，类 authz/correctness，证据类型 probe-result，包含确切的失败调用）。
7.  **不要削弱测试使其通过**：如果仅所有者查询返回了另一个用户的行，修复应在函数中（交给 convex-authz），而不是在断言中。直到测试变绿之前修改的测试证明不了任何东西。

## 规则

- 证明行为，而非编译：每个验证至少包含一个负面断言（应该被拒绝的调用者被拒绝了）——仅快乐路径不足以证明。
- 使用 `t.withIdentity` 以多个身份驱动功能（所有者、其他用户、未经过身份验证），使用应用程序的真实 subject/tokenIdentifier 形状。
- 种子化调用者的行和另一个用户的行，以便跨用户访问和数据范围实际上可测试。
- 需要 `vitest.config.ts` 设置环境 'edge-runtime' + 将 convex-test 内联，convex-test 才能运行（需要 `import.meta.glob`）；请编写它，不要只编写测试文件。
- 使用 convex-test 在进程内运行——无需部署；与 `test` 能力的设置组合，而不是分支它。
- 不要削弱断言使其通过：失败的负面测试是真实缺陷 → 将修复交给 convex-authz/convex-expert，不要直到测试变绿才编辑测试。
- 对任何失败的断言发出总线发现（authz/correctness，证据：失败的探测调用），以便复合通过或自我修复可以捕获它。
- 这驱动一个特定的构建功能；通常请求设置测试框架的是 `test` 能力。
