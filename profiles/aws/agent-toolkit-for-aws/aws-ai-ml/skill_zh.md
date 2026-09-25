# AWS AI/ML 模型定制

在 Amazon SageMaker 上进行模型微调和部署的领域专业知识。涵盖从规划到生产部署的完整模型定制生命周期。

## 路由

将用户的意图匹配到适当的参考文件夹，并仅加载该内容。

| 用户意图 | 参考 | 使用场景 |
|-------------|-----------|-------------|
| 规划模型定制项目，发现工作范围，恢复或修改计划 | [references/planning/](references/planning/) | 用户的请求与模型定制或部署（微调、训练、构建、定制、审查数据、部署或建立模型——包括选择或部署没有训练的现成或基础模型——或获取方法建议）相关。始终与其他意图协同激活以发现完整范围。当请求匹配此表中的多行时，首先加载此参考——在路由到单一操作参考之前阅读其计划模板。 |
| 定义业务问题、成功标准或用例规范 | [references/use-case-specification/](references/use-case-specification/) | 用户说“定义我的用例”、“捕获需求”、“我应该提前决定什么”，或作为任何计划的默认第一步。如果用户明确拒绝，则跳过。 |
| 选择或更改基础模型 | [references/model-selection/](references/model-selection/) | 用户询问使用哪个模型、提到模型名称或系列，或想要评估可用内容。**始终激活模型选择，即使对于已知的模型名称**，因为必须解析确切的 Hub 模型 ID。**推荐**：首先路由到用例规范以捕获需求——这会产生更好的过滤结果。如果用户提供了特定的模型名称/ID 或拒绝，则不需要首先路由到用例规范。如果意图不明确（微调与直接部署），模型选择必须在继续之前确认路径。部署的基础模型过滤必须通过 select-for-deployment.md 及其脚本进行最终推荐。 |
| 选择微调技术（SFT、DPO、RLVR、RLAIF） | [references/finetuning-technique/](references/finetuning-technique/) | 用户已决定微调并需要选择技术，或需要针对所选模型食谱验证技术。首先需要选择基础模型。 |
| 验证数据集质量和格式 | [references/dataset-evaluation/](references/dataset-evaluation/) | 用户说“我的数据集可以吗”、“检查我的训练数据”、“我有自己的数据”，或在开始任何微调作业之前。 |
| 在不同格式之间转换或转换数据集 | [references/dataset-transformation/](references/dataset-transformation/) | 用户说“转换”、“转换”、“重新格式化”，或数据集模式需要更改。始终使用此方法而不是编写内联转换代码。 |
| 生成微调代码并开始训练 | [references/finetuning/](references/finetuning/) | 用户说“开始训练”、“微调我的模型”、“我准备好训练了”，或计划达到微调步骤。支持 SFT、DPO、RLVR、RLAIF 训练器。 |
| 评估或基准测试训练好的模型 | [references/model-evaluation/](references/model-evaluation/) | 用户说“评估我的模型”、“运行基准测试”、“测试模型性能”、“比较模型”。支持 LLM-as-Judge 和 Custom Scorer。 |
| 在端点或 Bedrock 上部署、基准测试或优化模型 | [references/model-deployment/](references/model-deployment/) | 用户说“部署我的模型”、“创建端点”，或“使其可用”（纯部署）——或者，仅对于 SageMaker 实时端点的推理优化子工作流，“基准测试我的端点”/“比较基准测试运行”（基准测试），或为新的部署声明性能/成本/延迟/吞吐量目标，例如“找到最便宜的实例”（推荐）。处理 Nova 与 OSS 部署路径。 |
| 设置 IAM 角色、S3 桶、SDK 配置 | [references/sdk-getting-started/](references/sdk-getting-started/) | 用户说“设置”、“入门”、“检查我的环境”、“配置 SDK”，或作为涉及 SageMaker 训练/评估/部署的任何计划的第一个步骤。 |
| 管理项目目录和工件 | [references/directory-management/](references/directory-management/) | 开始新项目、恢复现有项目，或当 PLAN.md 需要与项目目录关联时。 |
| 设置、更新或删除 SageMaker 管理的 MLflow 应用 | [references/manage-mlflow/](references/manage-mlflow/) | 用户说“设置 MLflow”、“创建 MLflow 应用”、“更新我的 MLflow 应用”、“删除我的 MLflow 应用”、“我需要一个 MLflow 服务器”，询问“什么是 SageMaker MLflow”，或工作流需要一个 MLflow 后端且没有连接。 |
| 诊断故障或状态不佳的 SageMaker 端点 | [references/endpoint-diagnostics/](references/endpoint-diagnostics/) | 用户报告端点错误、延迟、推理失败或失败的部署。“我的端点状态如何？”、“我的端点是否出错？”、“我的端点失败——为什么？”、“我的端点后面运行了多少实例？”、“是模型还是 SageMaker 导致延迟？”、“显示我的端点的容器日志。”不适用于训练作业问题、端点删除、扩展更改或新部署。 |

## 规则

- **渐进式披露。** 仅加载与当前用户意图相关的参考文件夹。不要一次性加载所有参考。
- **尽力提供帮助。** 如果用户的请求超出此技能的参考范围，不要使对话结束。使用一般 AWS 知识和文档帮助用户，并告知用户该指导未涵盖此技能的验证工作流。
- **使用归因。** 在运行任何 AWS CLI 命令或打包脚本之前，设置 `export AWS_SDK_UA_APP_ID=AWSSkill-SageMaker`。
