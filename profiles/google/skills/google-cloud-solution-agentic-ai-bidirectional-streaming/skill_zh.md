# 实时双向多模态流式智能体AI解决方案

该技能指导智能体通过工作流，在云端为实时双向多模态流式工作负载、用例或需求设计和实施定制化的多产品解决方案。

## 工作流

解决方案的设计和实施工作流包括以下阶段：

*   **阶段 1：需求发现和分析**：分析工作负载的需求、约束、依赖关系和当前状态。
*   **阶段 2：解决方案设计**：基于Google Cloud设计最佳实践和建议，为工作负载构建技术栈、架构和部署配置。
*   **阶段 3：实施计划**：生成自动化和说明以部署解决方案。
*   **阶段 4：解决方案验证**：验证部署是否满足工作负载的需求。

### 阶段 1：需求发现和分析

- [ ] **步骤 1：发现需求**：了解工作负载的功能和非功能需求、业务目标以及当前状态（如有），包括其架构、依赖关系和约束。使用以下问题来指导需求发现过程：
   - 主要输入模态是什么（音频、视频或文本），实时叙述反馈的目标延迟是多少？
   - 您是否需要实时安全监控、危险检测或视觉检查？如果是，那么在视频流中需要监控和检测哪些具体的安全隐患、操作风险或错误步骤？
   - AI智能体必须访问哪些现有系统、知识库、产品文档或原理图库，以获得基于事实的指导？
   - 客户端设备约束和网络限制是什么？

- [ ] **步骤 2：识别组件**：根据需求分析，识别工作负载的组件及其关系。还识别解决方案需要集成的任何跨云组件、混合组件或本地组件。

- [ ] **步骤 3：生成组件分解**：生成工作负载组件的技术分解。技术分解必须将解决方案分解为逻辑组件。

- [ ] **步骤 4：请求确认**：要求用户确认生成的技术分解是否满足其工作负载需求。

- [ ] **步骤 5：迭代**：如果用户请求更改，则生成更新的技术分解，并要求用户确认更改。继续迭代，直到用户确认技术分解。

### 阶段 2：解决方案设计

- [ ] **步骤 1：检索相关的Google Cloud文档**：
   - [启用实时双向多模态流式](https://docs.cloud.google.com/architecture/agentic-ai-bidirectional-multimodal-streaming.md.txt)
   - [Google Cloud中的多智能体AI系统](https://docs.cloud.google.com/architecture/multiagent-ai-system.md.txt)
   - [选择您的智能体AI架构组件](https://docs.cloud.google.com/architecture/choose-agentic-ai-architecture-components.md.txt)
   - [Google Cloud中的多智能体私有网络模式](https://docs.cloud.google.com/architecture/multi-agent-private-networking-patterns.md.txt)

   *重要*：使用从Google Cloud文档中检索的内容，为该阶段剩余步骤中生成的指导提供基础。

- [ ] **步骤 2：将组件映射到Google Cloud产品**：对于确认的技术分解和智能体设计模式中的每个组件，根据[references/product-mapping.md](references/product-mapping.md)中的指南，识别适当的Google Cloud产品和功能。

- [ ] **步骤 3：创建架构图**：生成Mermaid格式的架构图：https://github.com/mermaid-js/mermaid。

- [ ] **步骤 4：生成设计建议**：根据[references/design-recommendations.md](references/design-recommendations.md)中的指南，生成设计指导。

- [ ] **步骤 5：起草解决方案架构**：根据[assets/output-template.md](assets/output-template.md)中的模板，将需求、技术分解、产品映射、架构图和设计建议汇编到一个名为`solution-architecture-guide.md`的Markdown文件中。

- [ ] **步骤 6：请求审查**：向用户展示生成的解决方案架构并请求他们的反馈或批准。

- [ ] **步骤 7：迭代**：如果用户请求更改，则生成更新的解决方案架构并重复步骤2-6，直到用户批准解决方案架构。

### 阶段 3：实施计划

- [ ] **步骤 1：检索相关的实施资源**：
   - [在Cloud Run上托管AI智能体](https://docs.cloud.google.com/run/docs/ai-agents.md.txt)
   - [使用WebSockets触发Cloud Run](https://docs.cloud.google.com/run/docs/triggering/websockets.md.txt)
   - [启动和管理Gemini Live API会话](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/live-api/start-manage-session.md.txt)
   - [ADK流式工具](https://adk.dev/streaming/streaming-tools/)
   - [ADK流式配置](https://adk.dev/streaming/configuration/)
   - [Codelab：Way Back Home第4级说明](https://codelabs.developers.google.com/way-back-home-level-4/instructions#0)（以及[solution code](https://github.com/gca-americas/way-back-home/tree/main/level_4))

   *重要*：使用这些资源作为该阶段剩余步骤中生成的IaC和部署说明的技术基础。

- [ ] **步骤 2：识别部署先决条件**：记录部署的先决条件，包括以下内容：
   - 项目和计费关联
   - 所需的Google Cloud API
   - 所需的IAM权限
   - 任何其他先决条件

- [ ] **步骤 3：生成基础设施即代码（IaC）**：生成代码（如Terraform）和部署脚本，以自动化提议的Google Cloud资源的配置。

- [ ] **步骤 4：编写部署说明**：起草顺序、逐步的部署说明，以执行IaC并初始化工作负载组件。根据[assets/output-template.md](assets/output-template.md)中的模板，更新部署说明`solution-architecture-guide.md`。

- [ ] **步骤 5：请求审查**：向用户展示生成的部署说明以供反馈和确认。

- [ ] **步骤 6：迭代**：如果用户请求更改，则生成更新的实施计划并重复步骤2-5，直到用户批准实施计划。

### 阶段 4：解决方案验证

- [ ] **步骤 1：检索相关的验证资源（可选）**：如果阶段3的资源不在您的上下文中，请检索相同的实施资源，作为本阶段生成的验证检查和验证脚本的基础。

- [ ] **步骤 2：定义验证检查**：概述验证步骤，以验证部署的基础设施是否满足工作负载需求：
   - **部署干运行**：如`terraform plan`等命令，以预览更改。
   - **连接性和路由**：验证网络路径、负载均衡器路由和服务端点。
   - **安全策略**：验证受限访问、防火墙规则和IAM执行。

- [ ] **步骤 3：生成验证脚本**：起草轻量级脚本或命令行说明，如使用`curl`或`gcloud`，用户可以运行这些脚本来执行这些验证检查。

- [ ] **步骤 4：汇编验证报告**：根据[assets/output-template.md](assets/output-template.md)中的模板，记录验证步骤、验证脚本和预期结果`solution-architecture-guide.md`。

- [ ] **步骤 5：执行验证并最终确定**：协助用户执行验证检查并排除任何部署问题。解决方案验证成功后，请求用户的最终批准。

- [ ] **步骤 6：迭代**：如果用户请求更改，则生成更新的验证计划并重复步骤2-5，直到用户批准验证计划。
