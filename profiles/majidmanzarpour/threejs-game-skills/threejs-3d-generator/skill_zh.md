# Three.js 3D生成器

为浏览器游戏准备用于Three.js的3D资源。提供方：Tripo。

从实际加载的技能文件中解析`<this-skill-dir>`。先解析其相邻的兄弟技能，然后使用运行器发现的路径。不要混用已安装的版本或假设特定的家目录。

## 参考

| 文件 | 何时阅读 |
| --- | --- |
| `references/api-notes.md` | 端点和任务决策、模型版本、轮询、后处理、转换、绑定、动画、下载 |
| `references/threejs-integration.md` | 将输出导入浏览器游戏、GLB/FBX加载、根运动、动画连接 |
| `references/image-generator-workflows.md` | 与`threejs-image-generator`配对用于概念、纹理、UI艺术或图像到3D输入 |

## API密钥

脚本读取`--api-key`或`TRIPO_API_KEY`。密钥永远不会放在技能文件、游戏代码或报告中。

```bash
python3 <this-skill-dir>/scripts/threejs_3d_asset.py probe   # TRIPO_API_KEY=SET|MISSING
```

仅在shell配置文件中定义的密钥可能不在进程环境中。如果纯文本探测意外打印`MISSING`，请使用`threejs-game-director/scripts/probe_asset_credentials.sh`，它将加载配置文件并一次性探测所有三个提供方。

下载URL很快就会过期——任务成功后立即下载。

## 命令

```bash
python3 <this-skill-dir>/scripts/threejs_3d_asset.py --help
```

文本到3D，高级英雄模型的默认设置：

```bash
python3 <this-skill-dir>/scripts/threejs_3d_asset.py text \
  --prompt "游戏级科幻悬浮摩托车，光滑装甲面板，清晰的轮廓，分层硬表面细节，PBR材质，干净的拓扑结构，居中枢轴，面向前方，无文字" \
  --model-version v3.1-20260211 --texture-quality detailed --geometry-quality detailed \
  --checkpoint artifacts/hover-bike-job.json \
  --wait --download --out-dir assets/models/hover-bike
```

从生成的概念到3D：

```bash
python3 <this-skill-dir>/scripts/threejs_3d_asset.py image \
  --image assets/concepts/hover-bike-front.png --model-version v3.1-20260211 \
  --enable-image-autofix --texture-alignment original_image --texture-quality detailed \
  --wait --download --out-dir assets/models/hover-bike
```

状态、下载和后处理（`texture_model`、`animate_prerigcheck`、`animate_rig`、`animate_retarget`、`conversion`、`stylize_model`）：

```bash
python3 <this-skill-dir>/scripts/threejs_3d_asset.py status TASK_ID
python3 <this-skill-dir>/scripts/threejs_3d_asset.py download TASK_ID --out-dir assets/models
python3 <this-skill-dir>/scripts/threejs_3d_asset.py postprocess --type conversion \
  --original-task-id TASK_ID --format GLTF --face-limit 20000 --wait --download --out-dir assets/models/gltf
```

动画角色流程：生成、预绑定检查、带有限次重试的验证绑定、重定向和下载，按身体计划路由。使用检查点和在阶段之间停止以检查依赖工作再花费：

```bash
python3 <this-skill-dir>/scripts/threejs_3d_asset.py character-pipeline \
  --prompt "风格化赛博跑者角色，T姿势，全身，游戏级服装，清晰的轮廓" \
  --animations preset:idle,preset:walk,preset:run,preset:jump \
  --checkpoint artifacts/cyber-runner-job.json --stop-after model \
  --out-dir assets/models/cyber-runner

# 检查下载的模型/预览后：
python3 <this-skill-dir>/scripts/threejs_3d_asset.py resume artifacts/cyber-runner-job.json --stop-after rig
# 检查验证绑定后：
python3 <this-skill-dir>/scripts/threejs_3d_asset.py resume artifacts/cyber-runner-job.json --stop-after animations

python3 <this-skill-dir>/scripts/threejs_3d_asset.py character-pipeline \
  --prompt "风格化狼，四足姿势，四条腿都着地且分开，全身" \
  --rig-type quadruped --animations preset:quadruped:walk \
  --checkpoint artifacts/wolf-job.json --stop-after model --out-dir assets/models/wolf
```

## 恢复和恢复

`--checkpoint PATH`在`text`、`image`、`postprocess`和`character-pipeline`上是可选的。它记录接受的任务ID、阶段状态和下载文件指纹；检查点中不会包含API密钥或签名输出URL。为每个任务使用单独的检查点。必须恢复现有的检查点，而不是覆盖它们，并且并发使用是锁定的。

对于后台单任务生成，省略`--wait`，保留打印的任务ID/检查点，稍后运行`resume CHECKPOINT`。单任务恢复仅等待/下载该任务；它不会添加绑定。角色恢复会重用完成的阶段并继续到动画，除非`--stop-after model|rig|animations`限制了此调用。凭证仍然来自当前环境。检查点记录绝对本地路径，因此请保持其引用的文件在原位。

助手会使用有界的退避重试安全的状态/下载读取，永远不会提交付费任务。缺失凭证、用尽积分、无效输入、临时错误和不确定提交会被明确报告。中断时，恢复现有任务而不是重新开始。如果POST可能已成功但未收到任务ID，请在提供方历史记录中找到它并使用`resume CHECKPOINT --task-id RECOVERED_ID`；不要凭空编造ID或盲目提交替代品。如果没有可恢复的ID，在可能重复计费之前报告不确定性。

对于协调游戏，请遵循导演的`references/asset-recovery.md`；在生成运行时继续独立实现。显式程序化或无外部服务请求会覆盖生成资产默认值。在项目笔记中记录挂起的任务和用户更正，保留完成的资产而不是重复生成。

## 绑定和动画

这些规则可防止几乎所有昂贵的失败。完整的参数表及其背后的测量值在`references/api-notes.md`中。

- 将角色生成为一个融合网格：关闭`--quad`和`--generate-parts`（`generate_parts`禁用纹理，`quad`强制FBX输出）。
- 要求全身T姿势或A姿势，手臂远离身体，对称，无道具与轮廓融合。在绑定之前检查渲染预览是否确实处于该姿势；如果不是，请重新生成。
- 首先运行`animate_prerigcheck`（它不需要模型版本，不花钱）并使用检测到的`rig_type`。`riggable=false`意味着用更清晰的姿势重新生成，而不是强制绑定。
- **绑定版本由身体计划路由。** 人类使用`v1.0-20240301`——解剖学骨骼带扭转骨和大型`preset:biped:*`库。v2.x肢体链绑定器在人类网格上0/16，无论是否装甲，始终产生非对称链。生物使用`v2.5-20260210`。`character-pipeline`会自动路由此设置。
- `riggable=true`不保证可用的绑定。在重定向之前验证骨骼——`validate-rig rig-model.glb --rig-type biped`——检查骨头存在和链深度，因为单骨腿会扭曲每个剪辑。缺失或格式错误的绑定GLB是失败，包括使用`--force-rig`时。自动绑定是非确定性的：在失败时，在选择的预算内重试绑定任务（~25积分）之前重新生成模型。装甲硬表面角色需要最多的重试。
- `animate_retarget`使用**绑定**任务ID，而不是生成任务ID。非双足绑定每个任务最多批量处理5个预设；批量剪辑按请求顺序返回为`NlaTrack`、`NlaTrack.001`、…，因此按索引映射并在导入后重命名。
- 使用`--model-version default`重定向v1.0绑定——枚举会拒绝显式的`v1.0-20240301`并返回HTTP 400代码2017，但服务器默认处理它们。
- v1.0重定向必须使用`--out-format fbx`（脚本强制执行）：Tripo在此路径上的GLB烘焙会错误地写入扭转骨变换，肢体会塌缩到躯干。v2.5生物重定向作为GLB是没问题的。
- **永远不要传递`--animate-in-place`**。它会损坏烘焙——v1.0镜像和交叉肢体，v2.5爆炸的蒙皮。保留根运动烘焙并在导入时剥离；引擎片段在`references/threejs-integration.md`中。
- 生物每个获得一个运动预设，并且没有`preset:attack`（使用`preset:slash`或`preset:shoot`）。生物的网格姿势决定了预设如何读取——在直立龙上行走看起来像人在行走，因此请按动画期望的姿势生成生物。
- 多模式生物（会爬行和飞行的龙）需要两次绑定相同的模型：地面绑定类型用于运动，`avian`用于翅膀链。
- 当Tripo预设将被重定向时使用`--spec tripo`（默认）；`--spec mixamo`绑定的不能被Tripo重定向，仅用于外部管道。
- 下载后，运行`validate-animation clip.glb`（标记比例轨道、肢体拉伸转换、极端旋转、每剪辑持续时间和通道覆盖），然后检查`gltf.animations`名称和数量，再连接`AnimationMixer`。

## 质量

使用材质、轮廓、相机可读性、比例和游戏使用约束来改进用户的提示。请求与性能预算匹配的GLB/PBR，面部限制和纹理质量；对于移动设备，优先考虑`smart_low_poly`、`face_limit`或稍后的低多边形后处理。使用生成的3D作为英雄内容，并程序化构建周围的道具包。

集成后检查未暂停的游戏内运动：剪辑过渡、变形、根运动、脚滑动和攻击/接触时间。使用QA运动通道进行动画工作；成功的下载或骨骼检查不是良好动画的证明。

报告任务ID、检查点/输出路径、模型版本、纹理和几何设置、动画、转换设置、Three.js导入说明、观察到的运动以及任何失败的内容。将详细证据放在项目资产中供负责人汇总报告。
