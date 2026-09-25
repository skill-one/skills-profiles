# AWS 无服务器

构建 AWS 上生产就绪的无服务器应用程序的专业技能。
涵盖 Lambda 函数、API 网关、DynamoDB、SQS/SNS 事件驱动模式，
SAM/CDK 部署和冷启动优化。

## 详细指南

执行此技能前，请阅读 [详细指南](references/detailed-guide.md)。它保留了完整流程和参考材料。将其安全要求、先决条件和验证要求视为强制性。对于专注工作，加载相关章节；对于端到端工作，完整阅读指南。

## 监控内存使用

```javascript
exports.handler = async (event, context) => {
  const used = process.memoryUsage();
  console.log('内存:', {
    heapUsed: Math.round(used.heapUsed / 1024 / 1024) + 'MB',
    heapTotal: Math.round(used.heapTotal / 1024 / 1024) + 'MB'
  });
  // ...
};
```

## 使用场景
当请求明确匹配上述描述的功能和模式时，使用此技能。

## 限制
- 仅当任务明确匹配上述描述的范围时，才使用此技能。
- 不要将输出视为环境特定验证、测试或专家评审的替代品。
- 如果缺少必要的输入、权限、安全边界或成功标准，请停止并请求澄清。
