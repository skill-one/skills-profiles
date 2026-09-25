确定用户需求并指导他们完成导航设置。有关更详细的组件信息、API说明、代码示例和故障排除，请参阅 [navigation-system.md](references/navigation-system.md)。

### 将C#传递给 `eval`

`eval` 编译的是 **代码块，而不是文件**。有两个后果，都会导致编译错误而不是警告：

- **没有 `using` 指令。** 编译器将 `using UnityEngine;` 解释为资源释放语句并拒绝它 (`CS0210`)。
- **类型必须完全限定。** 简单的 `AssetDatabase` 或 `Volume` 无法解析 (`CS0246` / `CS0103`)，而简单的 `Object` 与 `object` 混淆 (`CS0104`)。

当下面片段以文件形式编写时——带有 using 语句以提高可读性，或因为它打算保存到项目中——在将其传递给 `eval` 之前限定类型。

## 路由逻辑

| 用户说 | 解释 |
|--------|------|
| "添加导航" / "设置导航" | 完整设置：NavMeshSurface + 烘焙 + NavMeshAgent |
| "让这个角色导航" | 添加 NavMeshAgent，确保存在 NavMesh |
| "添加路径查找" | NavMeshAgent + 移动脚本 |
| "代理无法移动" / "找不到路径" | 故障排除——请参阅参考中的故障排除决策树 |
| "避开障碍物" | NavMeshObstacle 带有雕刻或避让 |
| "连接两个区域" / "跳过" | 区域之间的 NavMeshLink |
| "在点之间巡逻" | NavMeshAgent + 巡逻脚本 |
| "点击移动" | NavMeshAgent + 射线检测点击移动脚本 |
| "导航时动画化角色" | 将 Animator 与 NavMeshAgent 结合 |
| "不同代理尺寸" | 在导航窗口中配置代理类型 |
| "区域和成本" / "限制区域" | NavMesh 区域类型、修改器和代理区域掩码 |

## 工作流程

### 0. 包安装检查
在执行任何其他操作之前，请验证 `com.unity.ai.navigation` 是否已安装。如果缺失，请将其添加到 `Packages/manifest.json` 下的 `dependencies`——Unity 在编辑器下次获得焦点时解析它，并且这不需要编辑器连接：

```json
"com.unity.ai.navigation": "<当前 2.x 版本>"
```

不要编造版本字符串。从 Unity 注册表中读取当前版本——`https://packages.unity.com/com.unity.ai.navigation` 列出了所有已发布的版本——或者复制此 manifest 中相邻 Unity 包使用的版本。不存在的版本会导致 Unity 沉默地失败解析，因此错误的猜测看起来什么都没发生。

确认安装后才能继续。如果您有一个可以运行 C# 的实时编辑器，请参阅 [navigation-system.md](references/navigation-system.md) 中的 `Client.Add` 对应项。

### 1. 预检查：评估当前导航设置
在做出更改之前，检查已有的内容：
1. 查找现有的导航组件。使用连接的编辑器时，查询实时场景中的 `NavMeshSurface`、`NavMeshAgent`、`NavMeshObstacle`、`NavMeshLink` 和 `NavMeshModifier`——请参阅 `unity-cli` 技能以驱动正在运行的编辑器。没有编辑器时，搜索场景和预制文件以查找这些组件名称。
2. 通过 **窗口 > AI > 导航 > 代理选项卡** 检查配置的代理类型。
3. 在提出更改之前，总结所有检测到的导航组件。

### 2. 收集缺失信息
在创建组件之前，确保用户已指定：可行走表面、代理类型/尺寸、代理行为、障碍物、链接以及区域/成本要求。如果任何内容不明确，请询问。请参阅参考中的信息收集清单以获取详细信息。

### 3. 规划与执行
按此顺序进行。请参阅参考中的组件设置指南以获取每个组件的详细分步说明：
1. **NavMesh Surface** — 创建可行走网格（烘焙它）
2. **NavMesh Agent** — 添加路径查找角色
3. **NavMesh Obstacle** — 添加动态障碍物
4. **NavMesh Link** — 连接断开的 NavMesh 区域
5. **NavMesh Modifier / Modifier Volume** — 微调区域类型
6. **脚本** — 移动、巡逻、点击移动、动画结合（请参阅参考中的常见示例）

### 4. 验证
设置完成后，请确认：
- NavMesh 已烘焙且可见（蓝色覆盖层）
- NavMeshSurface 代理类型与 NavMeshAgent 代理类型匹配
- 代理有有效的路径到达目的地
- 障碍物正确雕刻或阻挡
- 链接的两端都已连接且 Activated 已启用
- 区域掩码允许预期移动
- 没有冲突的组件（请参阅参考中的混合组件指南）
- 如果使用 Rigidbody 与 NavMeshAgent，Is Kinematic 已启用

### 5. 最终确认
总结创建或更改的内容：
- NavMesh Surfaces：哪个 GameObject、代理类型、几何模式、烘焙状态
- NavMesh Agent(s)：哪个 GameObject、速度、停止距离、区域掩码
- NavMesh Obstacle(s)：哪个 GameObject、形状、雕刻开启/关闭
- NavMesh Link(s)：起点/终点、双向、区域类型
- 脚本：哪些脚本附加到哪些 GameObject 上
- 任何需要手动执行的步骤（调整航点、场景更改后重新烘焙等）
