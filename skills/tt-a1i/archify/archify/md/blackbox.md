# archify (`tt-a1i/archify/archify`)

## blackbox

**function**: 把你的一段描述或 Mermaid 代码,变成一个双击就能在浏览器打开、可缩放/切主题/导出图片的精美交互式图表(架构图、流程图、时序图、数据流水线、状态机)。

- input: 一段白话需求,如「画个图:App 请求 → 网关 → 订单服务 → 数据库,旁边挂一个 Redis 缓存」, output: 一个独立的 HTML 文件,浏览器打开即是一张排好版的架构图,支持缩放、搜索、明暗主题切换,可一键导出 PNG/SVG
- input: 粘贴一段 Mermaid 代码(flowchart / sequenceDiagram / stateDiagram), output: 内容不变但重新设计过的交互式 HTML 图表,配色、排版、交互都比 Mermaid 默认渲染更精致
- input: 一段流程描述,如「订单提交 → 库存校验 → 不通过则退回用户改单,通过则进入支付」, output: 一张流程/状态流转图 HTML 文件,箭头可点击追踪流向,适合放进文档或演示
