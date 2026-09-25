<!-- SPDX-文件版权文本：版权所有 (c) 2026 NVIDIA 公司及关联公司。保留所有权利。 -->
<!-- SPDX-许可标识符：Apache-2.0 -->

# Omniverse Realtime Viewer

这是 Omniverse Realtime Viewer 技能包的顶层入口点。
它是自包含的：所有必要的路由、约定和验证指导都包含在选定的参考文档中。

使用聚焦的参考文档作为实现配方。此文件选择正确的配方，并保留跨所有生成的查看器应用程序必须遵守的架构规则。

## 使用说明

首先对请求的查看器进行分类，然后只阅读该交付路径和功能集所需的参考文档。首先实现渲染路径，在其上叠加交互和 UI 行为，最后从 `references/validation.md` 捕获验证证据。

## 阅读顺序

1. 阅读 `references/routing.md` 以选择交付路径和聚焦参考。
2. 在实现相机、输入、选择、视口、流协议、场景加载或环境行为之前，阅读 `references/conventions.md`。
3. 对于广泛的查看器请求，阅读 `references/usd-viewer-app/README.md`。
4. 如果交付路径不明确，阅读 `references/streaming-vs-local/README.md`。
5. 如果提示包含布局、面板、控件、检查器、状态或 UX，阅读 `references/viewer-ux-workflow/README.md`，然后阅读聚焦的查看器 UI 参考。这适用于 React/WebRTC、Tauri、Electron、`ovui`、`ovwidgets` 和 Dear ImGui 应用程序；“前端”是指用户界面，而不仅仅是浏览器 UI。
6. 对于视口交互，在阅读 `references/camera-controls/README.md`、`references/native-picking-selection/README.md` 或 `references/object-selection/README.md` 之前，阅读 `references/viewer-input-routing/README.md`。
7. 对于新的查看器应用程序或 ovrtx 工作，在阅读渲染器、场景加载、舞台管理、相机、选择或变换写入参考之前，阅读 `ovstage` 参考。
8. 对于 NVCF 自托管部署，在阅读选定的云部署和流参考之前，阅读 `references/cloud-deployment/nvcf-self-hosted.md`。
9. 只阅读为请求的应用程序所需的聚焦功能参考。
10. 在交接之前，使用 `references/validation.md` 捕获审查证据。

## 必须遵守的规则

- 使用 `ovrtx` 进行所有 USD 和 3D 渲染。
- 浏览器应用程序显示 `ovstream` WebRTC 视频流和 UI。浏览器不渲染 USD 几何图形。
- 不要替换 WebGL、Three.js、Babylon.js、PlayCanvas、A-Frame、model-viewer、react-three-fiber、glTF 浏览器查看器或其他客户端 3D 渲染器。
- 如果由于缺少 GPU/运行时环境而无法运行本地验证，请搭建 `ovrtx` 路径并记录运行时要求。不要添加浏览器渲染器回退。
- 保持用户 USD 文件未修改。查看器相机、渲染产品、渲染变量、设置、选择元数据和运行时状态属于会话/合成层、OVStage 运行时状态或应用程序状态。
- 保持 `renderer.step()`、舞台变异、原生拾取、选择写入、OVStage 发布和实时属性写入的一个所有者。
- 使用 OVStage 运行时写入可互换的变换动画、材质/效果属性、可见性切换、物理姿态样本和可逆的查看器拥有的状态。保持原生 OVRTX API 用于渲染、拾取队列和选择轮廓可视化。
- 将依赖项获取保留在 `references/dependencies/README.md` 中，将部署选择保留在 `references/cloud-deployment/README.md` 中；不要重复包位置或部署设置。

## 聚焦参考系列

- 入口点和配方：`references/usd-viewer-app/README.md`、`references/streaming-viewer-recipe/README.md`、`references/ovui-local-viewer-recipe/README.md`、`references/streaming-vs-local/README.md`、`references/electron-shm-viewer/README.md`、`references/ovwidgets-editor-shell/README.md`。
- 渲染和舞台：`references/ovstage-runtime/README.md`、`references/ovstage-population/README.md`、`references/ovstage-data-plane/README.md`、`references/ovstage-ovrtx-integration/README.md`、`references/ovrtx-rendering/README.md`、`references/stage-loading/README.md`、`references/stage-management/README.md`、`references/render-settings/README.md`、`references/aov-switching/README.md`、`references/stage-hierarchy/README.md`、`references/stage-queries/README.md`、`references/stage-attribute-reads/README.md`、`references/camera-auto-select/README.md`、`references/camera-picker/README.md`、`references/prim-transform-safety/README.md`、`references/usd-sample-data/README.md`。
- 交付和运行时：`references/streaming-server/README.md`、`references/streaming-client/README.md`、`references/streaming-messages/README.md`、`references/streaming-lifecycle/README.md`、`references/local-viewer/README.md`、`references/tauri-local-viewer/README.md`、`references/cpp-native-viewer/README.md`、`references/headless-shm-cli/README.md`、`references/viewer-backend-interface/README.md`、`references/webgl-shm-transport/README.md`。
- 查看 UI/UX：`references/viewer-ux-workflow/README.md`、`references/viewer-layout-patterns/README.md`、`references/viewer-control-patterns/README.md`、`references/viewer-data-view-patterns/README.md`、`references/viewer-feedback-status/README.md`。
- 交互：`references/viewer-input-routing/README.md`、`references/camera-controls/README.md`、`references/object-selection/README.md`、`references/native-picking-selection/README.md`、`references/selection-feedback/README.md`、`references/physics-simulation/README.md`、`references/selection-animation/README.md`、`references/transform-manipulator/README.md`、`references/gl-viewport-overlay/README.md`、`references/ovui-library/README.md`、`references/prim-pick-effects/README.md`、`references/prim-info-display/README.md`、`references/viewport-overlays/README.md`、`references/physics-simulation/README.md`。
- 基础设施：`references/dependencies/README.md`、`references/windows-native-setup/README.md`、`references/cloud-assets/README.md`、`references/cloud-deployment/README.md`、`references/cloud-deployment/nvcf-self-hosted.md`、`references/cloud-deployment/nvcf-viewer-container-contract.md`、`references/cloud-deployment/gpu-container-runtime.md`、`references/cloud-deployment/container-image-build.md`、`references/cloud-deployment/webrtc-network-diagnostics.md`、`references/troubleshooting/README.md`。
- AI/Agent：`references/a2ui-scene-copilot/README.md`。
- CAE/CFD 可视化：`references/cae-cfd-visualization/README.md`、`references/cae-cfd-visualization/data-and-operators.md`、`references/cae-cfd-visualization/cae-data-ingestion.md`、`references/cae-cfd-visualization/temporal-playback.md`、`references/cae-cfd-visualization/usd-authoring-and-materials.md`、`references/cae-cfd-visualization/ovstage-render-and-camera.md`、`references/cae-cfd-visualization/ovui-controls.md`、`references/cae-cfd-visualization/glyphs.md`、`references/cae-cfd-visualization/volume-rendering.md`、`references/cae-cfd-visualization/driving-cae-viz-via-ovstage.md`、`references/cae-cfd-visualization/emitter-and-seed-sources.md`、`references/cae-cfd-visualization/streaming-cae-viewer.md`、`references/cae-cfd-visualization/rtwt-blueprint-recreation.md`、`references/cae-cfd-visualization/coordinate-systems-and-up-axis.md`。

## 构建工作流

1. 根据交付路径、目标用户、所需功能、运行时环境、验证需求和显式约束对提示进行分类。
2. 选择一个小的参考集。从配方或路由参考开始，然后添加聚焦功能，如相机、拾取、层次结构、属性、渲染设置、变换工具、云资产或部署。
3. 在编写应用程序代码之前，阅读选定的参考。遵循它们的构建顺序、导入顺序、数据通道合同和渲染器所有权规则。
4. 首先实现 OVStage 人口/数据平面路径和核心渲染路径，然后是输入路由和相机，然后是选择和数据面板，然后是场景/设置功能，最后是打包或部署。
5. 将选定的参考视为 API 形状、兼容性和生成项目结构的行為合同。
6. 在调用查看器准备就绪之前，捕获验证证据。

## 示例

- 对于浏览器查看器请求，使用流配方参考加上相机、拾取、层次结构、属性、渲染设置和流状态参考。
- 对于本地工作站查看器请求，使用本地或原生交付参考加上渲染器设置、舞台加载、视口输入和验证。
- 对于“实时可视化 CAE/CFD 数据”请求，将 CAE/CFD 视为一层，而不是独立的应用程序：首先选择交付路径 (`references/streaming-vs-local/README.md`)，使用匹配的配方 (`references/ovui-local-viewer-recipe/README.md` 或 `references/streaming-viewer-recipe/README.md`) 构建基础查看器，然后叠加 `references/cae-cfd-visualization/README.md`（数据→操作符→USD 作者→场景），并通过 `references/cae-cfd-visualization/driving-cae-viz-via-ovstage.md` 连接控件。

## 完成检查清单

- 选定的参考与用户的意图和交付路径匹配。
- 没有代码路径使用浏览器端的 3D 渲染器进行 USD。
- 生成的应用程序对渲染步进和舞台变异有一个明确的所有者。
- 用户 USD 文件未受查看器拥有的会话数据修改。
- 相机、输入、选择、场景加载和流行为遵循 `references/conventions.md`。
- 设置/构建/运行结果和视觉交互证据使用 `references/validation.md` 捕获。

## ovstage 参考

对于所有新的查看器应用程序，在阅读渲染器、场景、交互或交付参考之前，请阅读这些：

- `references/ovstage-runtime/README.md` — 运行时所有权、序号、发布和恢复。
- `references/ovstage-population/README.md` — 组合的 USD 人口和场景生成。
- `references/ovstage-data-plane/README.md` — 查询、写入、变换和运行时 DTO。
- `references/ovstage-ovrtx-integration/README.md` — 附加的渲染器循环和运行时集成合同。
