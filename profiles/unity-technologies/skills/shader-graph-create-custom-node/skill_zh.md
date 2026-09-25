# 生成自定义 Shader Graph 节点

## 第 1 步：生成 HLSL 函数定义
- 函数必须以预处理指令 `UNITY_EXPORT_REFLECTION` 开头

## 第 2 步：使用 Shader Graph 提示标签装饰
- 请参考 `resources/all_hints.hlsl` 获取所有有效的提示标签及其使用模式
- 支持 C# 风格的文档标签，可在 `funchints` 或 `paramhints` 块外使用
- 必须的函数提示标签：
  - `sg:ProviderKey`
  - `sg:SearchCategory`
  - `sg:SearchTerms`
  - `sg:DisplayName`

## 第 3 步：将代码写入资源文件
- 在项目中搜索已包含自定义 Shader Graph 节点的 `ShaderInclude` 资源（`.hlsl`）
- 如果存在匹配的资源，则向用户展示其当前内容，并在追加新代码前请求确认
- 如果不存在匹配的资源，则创建一个新的 `.hlsl` 资源
- 确保文件以 `#include "ShaderApiReflectionSupport.hlsl"` 开头
