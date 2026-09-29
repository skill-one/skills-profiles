---
name: convex-crons
description: 为 Convex 应用添加周期性计划任务（crons）。
---

<!-- GENERATED from convex-agents content/capabilities/crons.json — do not edit by hand. -->

# 添加定时任务 (crons)

在 convex/crons.ts 中定义周期性任务，目标为内部函数，设置合理的间隔并确保处理程序幂等。

## 工作流程

1.  创建 convex/crons.ts 并使用 cronJobs()。
2.  以正确的间隔调度内部函数（绝不调度 public api.*）。
3.  使处理程序幂等（安全地重新运行）；保持每次运行尽可能小。
4.  验证任务是否出现在仪表板的调度中。

## 规则

- 调度 internal.* 函数，绝不调度 api.*。
- 保持 cron 处理程序小且幂等。
- 不要对可以通过订阅推送的事情进行紧密间隔轮询。
