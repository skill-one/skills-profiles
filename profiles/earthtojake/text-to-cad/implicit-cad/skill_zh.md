# 隐式CAD

使用此技能处理应在CAD查看器中直接作为浏览器JS模块运行的隐式CAD模型。主要产物是 `.implicit.js` 或 `.implicit.mjs` 文件。

此技能是实验性的。除非用户明确要求隐式模型，否则始终优先选择传统的STEP优先CAD工作流程。

## 文件格式

隐式CAD文件是一个导出 `implicit.js/0.1.0` 对象的ES模块。模式源代码位于捆绑包中的 `scripts/packages/implicitjs/src/lib/implicitCad/schema.js`；`scripts/lib/implicit-cad.mjs` 将其重新导出为 `SCHEMA`，供辅助编写的模块使用。

```js
export default {
  schema: "implicit.js/0.1.0",
  name: "圆角胶囊块",
  glsl: `
float sdf(vec3 p) {
  float sphere = implicit_sphere(p, vec3(0.0), 22.0);
  float block = implicit_box_centered(p, vec3(34.0, 18.0, 18.0), vec3(0.0));
  return implicit_union_round(sphere, block, 3.0);
}

vec3 color(vec3 p, vec3 normal) {
  return mix(vec3(0.20, 0.55, 0.95), vec3(0.95, 0.45, 0.20), smoothstep(-15.0, 20.0, p.z));
}
`,
};
```

模型还可以声明参数和动画。参数定义使用implicitjs控制模式：`number`、`boolean`、`enum`/`select`、`color`、`string` 和 `button`。数字、布尔值、颜色和按钮参数自动成为具有相同名称的GLSL统一变量；不要添加单独的 `uniforms` 对象。`bounds` 是可选的，当省略时从SDF估算；仅在自动估计过于宽泛、过慢或遗漏了不寻常字段时添加显式边界。`bounds` 和 `render` 可以是JavaScript函数，它们接收 `{ ...params, params, animation, animationState, elapsedSec, progress, t }`。

内置的GLSL辅助函数使用 `implicit_*` 命名空间，例如 `implicit_sphere`、`implicit_box_centered` 和 `implicit_union_round`。

```js
export default {
  schema: "implicit.js/0.1.0",
  name: "呼吸球体",
  params: {
    radius: {
      type: "number",
      label: "半径",
      min: 12,
      max: 34,
      default: 22,
      unit: "mm",
    },
  },
  animations: {
    breathe: {
      label: "呼吸",
      duration: 3,
      update({ progress, set }) {
        set("radius", 18 + Math.sin(progress * Math.PI) * 10);
      },
    },
  },
  render: { steps: 224, epsilon: 0.004 },
  glsl: `
float sdf(vec3 p) {
  return length(p) - radius;
}

vec3 color(vec3 p, vec3 normal) {
  return mix(vec3(0.10, 0.58, 0.95), vec3(1.0, 0.34, 0.12), smoothstep(-18.0, 18.0, p.z));
}
`,
};
```

不要将捆绑的辅助文件从此技能中复制出来。如果辅助函数很有用，则在编写过程中使用 `scripts/lib/implicit-cad.mjs`，或将独立的GLSL发射到最终的 `.implicit.js`/`.implicit.mjs` 模块中。

## 编写工作流程

1. 编写包含尺寸、坐标假设、程序化颜色意图和视觉检查的自然语言建模简报。
2. 创建或编辑用户指定的 `.implicit.js`/`.implicit.mjs` 模块。
3. 在需要时使用 `scripts/lib/implicit-cad.mjs` 辅助函数进行基元和字段组合：
   - 基元：`sphere`、`circle`、`boxCentered`、`plane`、`lineSegment`、`torus`、`axis`、`cylinder`、`cylinderCapped`、`capsule`、`cone`、`coneCapped`、`coneCapsule`
   - 布尔/混合：`unionSharp`、`intersectSharp`、`unionRound`、`intersectRound`、`unionChamfer`、`intersectChamfer`、`unionExp`、`intersectExp`、`unionLpNorm`、`intersectLpNorm`、`unionRvachev`、`intersectRvachev`、`difference`
   - 修改器/晶格：`shell`、`rotateAxis`、`repeatCentered`、`remapCylindrical`、`cubicGrid`、`squareHoneycomb`、`squareHoneycombReinforced`、`squareDiagonalHoneycomb`、`octetHoneycomb`、`hexagonalHoneycomb`、`triangularHoneycomb`
   - TPMS字段：`tpmsGyroid`、`tpmsSchwarz`、`tpmsDiamond`、`tpmsLidinoid`、`tpmsNeovius`、`tpmsSplitP`、`tpmsIwp`
   - 着色器包装器：`distanceFunction` 发射 `float sdf(vec3 p)`，`colorFunction` 发射 `vec3 color(vec3 p, vec3 normal)`
4. 添加可选的 `params` 和 `animations`，用于尺寸、切换、调色板、模式切换和动画探索。直接在GLSL中使用参数名称；运行时将声明匹配的统一变量。
5. 当模型受益于局部材质变化时，使用 `vec3 color(vec3 p, vec3 normal)` 添加可选的程序化颜色。将颜色值保持在0..1 RGB范围内。
6. 首先依赖自动SDF边界。当动画、周期性、平移或非常薄的模型需要更紧密或更可靠的框架/导出采样时，添加显式边界。
7. 在可见几何、颜色、参数、动画、边界、渲染或导出影响的更改后，运行以下轻量级视觉验证流程。
8. 运行 `python scripts/gen <model.implicit.js>` 来构建（或刷新）CAD查看器打开的渲染包。当也想要兄弟 `<name>.glb` 文件时，添加 `--write`，或使用 `node scripts/export.mjs --input <model.implicit.js> --glb` 进行STL/3MF、非默认参数或动画。

## 视觉验证

使用此技能的快照工具作为快速视觉检查，而不是替代确定性导入/导出验证。保持数据包小而明确。

对于简单的静态编辑，一个图像就足够了：

```bash
python scripts/snapshot --input models/implicit-cad/<model>.implicit.js --output /tmp/implicit-review/<model>.png
```

对于拓扑、周期性、薄特征、布尔混合、对象身份、颜色或疑似框架问题，通过一个CLI调用渲染一个小数据包，以便重用浏览器、模块和运行时模型：

```bash
python scripts/snapshot --job - <<'JSON'
{
  "input": "models/implicit-cad/<model>.implicit.js",
  "mode": "view",
  "render": { "sizeProfile": "simple", "frameMargin": 1.55 },
  "graphics": { "modelColors": true, "detail": 1.2, "shadows": true, "ambientOcclusion": true },
  "outputs": [
    { "path": "/tmp/implicit-review/<model>-iso.png", "camera": "iso" },
    { "path": "/tmp/implicit-review/<model>-front.png", "camera": "front" },
    { "path": "/tmp/implicit-review/<model>-top.png", "camera": "top" },
    { "path": "/tmp/implicit-review/<model>-right.png", "camera": "right" }
  ]
}
JSON
```

在作业级别添加 `implicitParameters` 用于一个参数状态，或在单个输出上添加，当审查点是比较参数变体时。当模型靠近边缘时，使用 `render.frameMargin` 围绕 `1.5`；如果快照仍然显示被裁剪，首先检查源 `bounds` 是否正在切割射线追踪本身。

对于动画，仅在运动是请求的一部分时创建一个短GIF：

```bash
python scripts/snapshot --job - <<'JSON'
{
  "input": "models/implicit-cad/<model>.implicit.js",
  "mode": "animate",
  "outputs": [{ "path": "/tmp/implicit-review/<model>-animation.gif" }],
  "implicitAnimation": { "activeId": "<animation-id>", "durationSeconds": 3, "fps": 12 }
}
JSON
```

检查生成的PNG/GIF，确保居中框架、没有顶部/底部/侧面裁剪、预期的轮廓和拓扑、可见的参数差异、GLSL定义的颜色、没有意外的孔/间隙，以及对于请求的图形设置足够平滑的边缘。如果快照显示不匹配，请修复隐式源或边界并仅重新运行相关数据包。

## 交接

完成创建或修改 `.implicit.js`、`.implicit.mjs`、`.glb`、`.stl` 或 `.3mf` 产物的隐式CAD工作后，当该技能安装时，你必须始终将显式文件路径传递给 `$cad-viewer`。如果 `$cad-viewer` 不可用或启动失败，请报告该问题，而不是静默地省略交接。

当生成验证快照时，还必须在最终响应中包含保存的PNG/GIF快照。如果没有适用快照，或快照生成失败，请说明原因并报告仍然运行的确定性验证。

## 快照工具

从此技能目录：

```bash
python scripts/snapshot --input <model.implicit.js> --output <snapshot.png>
python scripts/snapshot --input <model.implicit.js> --output <orbit.gif> --mode orbit
python scripts/snapshot --job <render-job.json>
python scripts/snapshot --job - --json
python scripts/snapshot --help
```

使用 `python scripts/snapshot --help` 获取完整的当前命令接口。快照CLI与其他渲染技能（`cadgen.snapshot_cli`）共享，并由CAD查看器使用的相同浏览器运行时驱动，因此几何、材质和光照渲染完全相同——默认的 `snapshot` 主题故意与视口不同，仅通过删除网格、原点轴和阴影来区分；此技能仅启用 `.implicit.js`。主题设置位于一个 `--theme` 下，隐式射线追踪质量位于 `--graphics` 下，镜像查看器的主题和图形选项卡。没有 `--display`：显示设置是CAD拓扑设置，隐式模型不携带任何设置。默认主题是 `snapshot`——没有地面网格、原点轴或阴影的Workbench Light；这里默认关闭射线追踪阴影，因此隐式快照与无阴影的网格路径匹配（传递 `--graphics '{"shadows":true}'` 以恢复它们）。工具在输出扩展名之前附加UTC时间戳。JSON作业可以是单个作业、一个具有多个 `outputs` 的作业、一个原始作业数组，或 `{ "jobs": [...] }`；对于审查数据包，建议使用多输出作业，因为它避免了为每个相机重新构建相同的产物。

## 生成工具

从此技能目录：

```bash
python scripts/gen <model.implicit.js>
python scripts/gen <model.implicit.js> --write
python scripts/gen models/implicits/*.implicit.js --force
python scripts/gen <model.implicit.js> --resolution 128 --threads 4
python scripts/gen --help
```

`scripts/gen` 构建模型的**渲染包**——CAD查看器打开的烘焙网格，位于模型文件夹的 `__cadgen__/models/<name>.implicit.js/` (`implicit.json` + `model.glb`)。包在模型的参数DEFAULTS下烘焙，它不携带任何实时参数和动画。它也是查看器按需构建的，通过相同的生成器，因此在此处构建的包和通过打开模型构建的包是相同的产物。

如果模型的包是当前的，则会被跳过；`--force` 会强制重新构建。`--write` 还会在源旁边留下兄弟 `<name>.glb` 文件，来自相同的网格通道——该文件是一个普通的导出预设GLB（包的 `model.glb` 是为查看器压缩的，不是替代品）。当您需要STL或3MF、非默认参数或动画时，使用 `scripts/export`。

## 导出工具

从此技能目录：

```bash
node scripts/export.mjs --input <model.implicit.js> --glb
node scripts/export.mjs --input <model.implicit.js> --stl <mesh.stl> --resolution <resolution>
node scripts/export.mjs --input <model.implicit.js> --stl --3mf --glb
node scripts/export.mjs --input <model.implicit.js> --3mf --params '<parameter-json>' --json
node scripts/export.mjs --help
```

每个格式一个标志——`--stl`、`--3mf`、`--glb`——允许多个标志在一运行中匹配CAD技能的导出CLI。至少需要一个；没有，命令将退出2。模型每次运行只网格化一次，因此每个请求的格式都来自相同的几何。没有路径的格式标志将使用相同的茎与源文件相邻，例如 `<model>.glb` 对于 `<model>.implicit.js>`；提供的路径相对于当前目录解析。使用 `node scripts/export.mjs --help` 获取完整的当前命令接口。
