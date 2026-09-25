<!-- GENERATED from convex-agents content/capabilities/crons.json — do not edit by hand. -->

# 添加计划任务 (crons)

在 convex/crons.ts 中定义周期性任务，目标为内部函数，使用合理的间隔和幂等处理器。

## 工作流程

1. 创建 convex/crons.ts 并使用 cronJobs()。
2. 以正确的间隔安排内部函数（绝不安排 public api.*）。
3. 使处理器幂等（安全可重新运行）；保持每次运行量小。
4. 验证任务是否出现在仪表板的计划中。

## 规则

- 安排 internal.* 函数，绝不安排 api.*。
- 保持 cron 处理器小且幂等。
- 不要对可由订阅推送的事情进行紧密间隔轮询。
