<!-- GENERATED from convex-agents content/capabilities/test.json — do not编辑手动。 -->

# 生成 Convex 测试

使用 convex-test + vitest 对函数进行测试，测试内存后端：参数/返回值、认证路径、索引和计划函数。

## 工作流程

1. 安装 convex-test + vitest。
2. 使用 convexTest(schema) 编写测试：通过 t.run 种子，调用 t.query/t.mutation，断言。
3. 覆盖认证（withIdentity）、错误路径和计划函数（t.finishInProgressScheduledFunctions）。
4. 运行 vitest；保持测试确定性。

## 规则

- 使用内存中的 convex-test，而不是实时部署。
- 覆盖认证 + 错误路径，而不仅仅是快乐路径。
- 保持测试确定性（无实时/网络）。
