# Genkit Python

## 前置条件

- **运行时**: Python **3.14+**, **`uv`** 用于依赖项 ([安装](https://docs.astral.sh/uv/getting-started/installation/)).
- **命令行工具**: `genkit --version` — 如果缺失，可通过 `npm install -g genkit-cli` 安装。

**新项目**: [设置](references/setup.md) (引导 + 环境). **模式和代码示例**: [示例](references/examples.md).

## 欢迎世界

```python
from genkit import Genkit
from genkit.plugins.google_genai import GoogleAI

ai = Genkit(
    plugins=[GoogleAI()],
    model='googleai/gemini-flash-latest',
)

async def main():
    response = await ai.generate(prompt='给我讲一个关于 Python 的笑话。')
    print(response.text)

if __name__ == '__main__':
    ai.run_main(main())
```

## 重要：不要信任内部知识

Python SDK 经常变化 — 请参考此处或上游文档验证导入和 API。在**任何**错误情况下，首先阅读 [常见错误](references/common-errors.md)。

## 开发工作流程

1. 默认提供者: **Google AI** (`GoogleAI()`), **`GEMINI_API_KEY`** 在环境中。
2. 模型 ID: 始终带前缀，例如 **`googleai/gemini-flash-latest`** (始终在线的最新 Flash 别名；其他技能相同模式)。
3. 入口点: **`ai.run_main(main())`** 用于 Genkit 驱动的应用 (不是 `asyncio.run()` 用于 `genkit start` 启动的长时间运行的服务 — 见 [常见错误](references/common-errors.md))。
4. 生成代码后，请遵循 [开发工作流程](references/dev-workflow.md) 用于 `genkit start` 和开发 UI。
5. 出错时：第一步总是 [常见错误](references/common-errors.md)。

## 参考

- [示例](references/examples.md): 结构化输出、流式传输、流程、工具、嵌入。
- [设置](references/setup.md): 新项目引导和插件。
- [常见错误](references/common-errors.md): 出现问题时首先阅读。
- [FastAPI](references/fastapi.md): HTTP, `genkit_fastapi_handler`, 并行流程。
- [Dotprompt](references/dotprompt.md): `.prompt` 文件和辅助工具。
- [Evals](references/evals.md): 评估器和数据集。
- [开发工作流程](references/dev-workflow.md): `genkit start`, 开发 UI, 检查清单。
