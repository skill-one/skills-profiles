<!-- GENERATED from convex-agents content/capabilities/sentinel.json — do not edit by hand. -->

# 在自己的部署中捕获生产错误

安装 `@convex-dev/sentinel`，将生产错误（服务器函数失败、客户端 JS/React崩溃、OCC 和扩展信号）捕获到用户自己的部署中的表中，在写入时进行脱敏，然后对新错误做出反应。数据永远不会离开用户的部署。

## 工作流程

1. 安装组件：在 `convex/convex.config.ts` 中使用 `app.use(sentinel)`。
2. 连接客户端SDK：一个React错误边界加上 `window.onerror`/`unhandledrejection` 和堆栈跟踪。
3. 脱敏在写入时运行，默认开启（默认拒绝密钥名称和值模式）。
4. 使用Convex CLI读取最近错误（`convex data`，`run-once-query`）；通过监控器的 `prod_error` 事件对新错误做出反应。
5. 可选地启用自愈cron：`triage` 类别对每个错误进行分类，对于反复出现的非瞬时错误，将其交给ai-runner来打开一个修复PR。

## 规则

- 脱敏是强制性的，默认开启——永远不要存储原始密钥；代理的读取会到达模型提供者。
- 数据保留在用户的部署中；永远不要发送给第三方。
- 样本和限制以控制数量和成本。
- 捕获 PROD 错误需要一个已部署的云应用；安装可以匿名进行。
