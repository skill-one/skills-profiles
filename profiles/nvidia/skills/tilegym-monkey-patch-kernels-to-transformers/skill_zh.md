# 将 cuTile 内核集成并创建到 🤗 Transformers 中
TileGym 项目的目的是提供高性能的 LLM 训练和推理内核。我们将集成 TileGym 项目中可用的内核到 Hugging Face `transformers` 库提供的 LLM 模型中，以验证端到端的功能正确性和性能提升。我们不会修改 `transformers` 源代码，而是采用非侵入性的猴子补丁方法：我们将替换 `transformers` 库中实现我们希望集成的 Transformer 模型的某些模块/类/方法，使得在模型实例化时，该模型的核心组件将被 TileGym 实现替换。在运行时，模型实际上会在底层调用 TileGym 内核。此外，我们将遵循一种自动研究风格的代理 harness 循环来创建和集成新的 cuTile 内核到目标模型，以提高内核覆盖率和端到端吞吐量。

## 说明
这是为人类读者准备的：只需向你的最喜欢的 AI 代理提示技能名称和目标模型 ID。例如：
```Claude/CodeX
Hi, 请 /monkey-patch-kernels-to-transformers Qwen/Qwen3.5-0.8B。
```
代理可能会问你几个问题。进行澄清并确认开始。

## 工作流程
1. 准备实验环境。遵循 [environment-setup.md](./references/environment-setup.md)
2. 将现有的 TileGym 内核集成到目标模型。遵循 [kernel-integration.md](./references/kernel-integration.md)
3. 为未覆盖的 PyTorch 代码自主创建新的 cuTile 内核。遵循 [auto-kernelize.md](./references/auto-kernelize.md)
   * 可以自由添加新的 cuTile 内核，并考虑约束条件
   * 不要停止，直到满足自动内核化循环停止条件
4. 总结并报告

## 学科
这是为执行此工作流程的 AI 代理准备的。

### 内核清单
可重用的 transformer 局部内核必须使用 FlashInfer-Bench 风格的定义和解决方案元数据表示。在研究计算需求、清点现有内核、提出候选方案或创建新的生成内核时，请遵循 [kernel-inventory-schema.md](./references/kernel-inventory-schema.md)。
