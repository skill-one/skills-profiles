# 工作流自动化

工作流自动化是使AI代理可靠的基础设施。没有持久的执行，10步支付流程中的网络中断意味着损失金钱和愤怒的客户。有了它，工作流可以精确地恢复到中断前的状态。

这项技能涵盖了将脆弱脚本转换为生产级自动化的平台（n8n、Temporal、Inngest）和模式（顺序、并行、协调器-工作器）。

关键洞察：这些平台做出了不同的权衡。n8n 优化易用性，Temporal 优化正确性，Inngest 优化开发者体验。根据实际需求选择，而不是炒作。

## 详细指南

执行此技能前，请阅读[详细指南](references/detailed-guide.md)。它保留了完整流程和参考材料。将其安全性、先决条件和验证要求视为强制执行。对于专注工作，加载相关部分；对于端到端工作，完整阅读指南。

## Inngest 示例（TypeScript）
"""
import { inngest } from "./client";

export const processOrder = inngest.createFunction(
  { id: "process-order" },
  { event: "order/created" },
  async ({ event, step }) => {
    // 步骤1：验证订单
    const validated = await step.run("validate-order", async () => {
      return validateOrder(event.data.order);
    });

    // 步骤2：处理支付（持久化 - 可在崩溃后继续）
    const payment = await step.run("process-payment", async () => {
      return chargeCard(validated.paymentMethod, validated.total);
    });

    // 步骤3：创建运输
    const shipment = await step.run("create-shipment", async () => {
      return createShipment(validated.items, validated.address);
    });

    // 步骤4：发送确认
    await step.run("send-confirmation", async () => {
      return sendEmail(validated.email, { payment, shipment });
    });

    return { success: true, orderId: event.data.orderId };
  }
);
"""

## Temporal 示例（TypeScript）
"""
import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';

const { validateOrder, chargeCard, createShipment, sendEmail } =
  proxyActivities<typeof activities>({
    startToCloseTimeout: '30 seconds',
    retry: {
      maximumAttempts: 3,
      backoffCoefficient: 2,
    }
  });

export async function processOrderWorkflow(order: Order): Promise<void> {
  const validated = await validateOrder(order);
  const payment = await chargeCard(validated.paymentMethod, validated.total);
  const shipment = await createShipment(validated.items, validated.address);
  await sendEmail(validated.email, { payment, shipment });
}
"""

## Inngest 示例
"""
export const analyzeDocument = inngest.createFunction(
  { id: "analyze-document" },
  { event: "document/uploaded" },
  async ({ event, step }) => {
    // 并行运行分析
    const [security, performance, compliance] = await Promise.all([
      step.run("security-analysis", () =>
        analyzeForSecurityIssues(event.data.document)
      ),
      step.run("performance-analysis", () =>
        analyzeForPerformance(event.data.document)
      ),
      step.run("compliance-analysis", () =>
        analyzeForCompliance(event.data.document)
      ),
    ]);

    // 汇总结果
    const report = await step.run("generate-report", () =>
      generateReport({ security, performance, compliance })
    );

    return report;
  }
);
"""

## Temporal 示例
"""
export async function orchestratorWorkflow(task: ComplexTask) {
  // 协调器决定需要执行的工作
  const plan = await analyzeTask(task);

  // 派发给专门的工作器工作流
  const results = await Promise.all(
    plan.subtasks.map(subtask => {
      switch (subtask.type) {
        case 'create':
          return executeChild(createWorkerWorkflow, { args: [subtask] });
        case 'modify':
          return executeChild(modifyWorkerWorkflow, { args: [subtask] });
        case 'delete':
          return executeChild(deleteWorkerWorkflow, { args: [subtask] });
      }
    })
  );

  // 汇总结果
  return aggregateResults(results);
}
"""

## 何时使用
- 用户提及或暗示：工作流
- 用户提及或暗示：自动化
- 用户提及或暗示：n8n
- 用户提及或暗示：Temporal
- 用户提及或暗示：Inngest
- 用户提及或暗示：步骤函数
- 用户提及或暗示：后台作业
- 用户提及或暗示：持久化执行
- 用户提及或暗示：事件驱动
- 用户提及或暗示：计划任务
- 用户提及或暗示：作业队列
- 用户提及或暗示：cron
- 用户提及或暗示：触发器

## 限制
- 仅当任务明确符合上述范围时才使用此技能。
- 不要将输出视为环境特定验证、测试或专家评审的替代品。
- 如果缺少必要的输入、权限、安全边界或成功标准，请停止并请求澄清。
