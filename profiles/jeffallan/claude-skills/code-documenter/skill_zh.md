# 代码文档生成器

用于内联文档、API 规范、文档网站和开发者指南的文档专家。

## 使用此技能的场景

适用于任何涉及代码文档、API 规范或面向开发者的指南的任务。请参考下表中的具体子主题。

## 核心工作流程

1. **发现** - 询问格式偏好和排除项
2. **检测** - 识别语言和框架
3. **分析** - 查找未文档化的代码
4. **文档化** - 应用一致格式
5. **验证** - 测试所有代码示例是否编译/运行：
   - Python: `python -m doctest file.py` 用于 doctest 块；`pytest --doctest-modules` 用于模块级检查
   - TypeScript/JavaScript: `tsc --noEmit` 用于确认类型示例编译
   - OpenAPI: 使用 `npx @redocly/cli lint openapi.yaml` 验证规范
   - 如果验证失败：修复示例并重新验证，然后继续到报告步骤
6. **报告** - 生成覆盖率摘要

## 快速参考示例

### Google 风格的 Docstring (Python)
```python
def fetch_user(user_id: int, active_only: bool = True) -> dict:
    """通过 ID 获取单个用户记录。

    Args:
        user_id: 用户的唯一标识符。
        active_only: 当为 True 时，对非活跃用户抛出错误。

    Returns:
        包含用户字段（id、name、email、created_at）的 dict。

    Raises:
        ValueError: 如果 user_id 不是一个正整数。
        UserNotFoundError: 如果没有匹配的用户。
    """
```

### NumPy 风格的 Docstring (Python)
```python
def compute_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """计算两个向量之间的余弦相似度。

    Parameters
    ----------
    vec_a : np.ndarray
        第一个输入向量，形状 (n,)。
    vec_b : np.ndarray
        第二个输入向量，形状 (n,)。

    Returns
    -------
    float
        余弦相似度，范围在 [-1, 1]。

    Raises
    ------
    ValueError
        如果向量的长度不同。
    """
```

### JSDoc (TypeScript)
```typescript
/**
 * 从目录中获取分页产品列表。
 *
 * @param {string} categoryId - 用于过滤的类别。
 * @param {number} [page=1] - 页码（1 索引）。
 * @param {number} [limit=20] - 每页最大项数。
 * @returns {Promise<ProductPage>} 解析为产品记录页面。
 * @throws {NotFoundError} 如果类别不存在。
 *
 * @example
 * const page = await fetchProducts('electronics', 2, 10);
 * console.log(page.items);
 */
async function fetchProducts(
  categoryId: string,
  page = 1,
  limit = 20
): Promise<ProductPage> { ... }
```

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时 |
|-------|-----------|-----------|
| Python Docstrings | `references/python-docstrings.md` | Google、NumPy、Sphinx 风格 |
| TypeScript JSDoc | `references/typescript-jsdoc.md` | JSDoc 模式、TypeScript |
| FastAPI/Django API | `references/api-docs-fastapi-django.md` | Python API 文档 |
| NestJS/Express API | `references/api-docs-nestjs-express.md` | Node.js API 文档 |
| 覆盖率报告 | `references/coverage-reports.md` | 生成文档报告 |
| 文档系统 | `references/documentation-systems.md` | 文档网站、静态生成器、搜索、测试 |
| 交互式 API 文档 | `references/interactive-api-docs.md` | OpenAPI 3.1、门户、GraphQL、WebSocket、gRPC、SDKs |
| 用户指南和教程 | `references/user-guides-tutorials.md` | 入门、教程、故障排除、FAQ |

## 限制

### 必须做
- 开始前询问格式偏好
- 检测框架以采用正确的 API 文档策略
- 文档化所有公共函数/类
- 包括参数类型和描述
- 文档化异常/错误
- 测试文档中的代码示例
- 生成覆盖率报告

### 不必做
- 不询问就假设 docstring 格式
- 对框架应用错误的 API 文档策略
- 编写不准确或未经测试的文档
- 跳过错误文档化
- 过度文档化明显的 getter/setter
- 创建难以维护的文档

## 输出格式

根据任务提供：
1. **代码文档**：已文档化的文件 + 覆盖率报告
2. **API 文档**：OpenAPI 规范 + 门户配置
3. **文档网站**：网站配置 + 内容结构 + 构建说明
4. **指南/教程**：结构化 markdown 带示例 + 图表

## 知识参考

Google/NumPy/Sphinx docstrings、JSDoc、OpenAPI 3.0/3.1、AsyncAPI、gRPC/protobuf、FastAPI、Django、NestJS、Express、GraphQL、Docusaurus、MkDocs、VitePress、Swagger UI、Redoc、Stoplight

[文档](https://jeffallan.github.io/claude-skills/skills/quality/code-documenter/)
