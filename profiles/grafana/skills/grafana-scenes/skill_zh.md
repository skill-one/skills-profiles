# @grafana/scenes 框架

使用声明式场景对象构建响应式、数据驱动的 Grafana 插件页面。

## 核心概念

场景由对象树组成：`SceneApp` → `SceneAppPage` → `EmbeddedScene` → 布局 → 面板。每个节点可以拥有数据（`$data`）、变量（`$variables`）、时间范围（`$timeRange`）和行为（`$behaviors`），这些属性会向下传递到树中。

## 快速入门：新建场景页面

### 1. 创建场景文件

```typescript
// src/components/scenes/MyFeature/scene.tsx
import {
  EmbeddedScene, SceneFlexLayout, SceneFlexItem,
  SceneQueryRunner, SceneVariableSet, QueryVariable,
  PanelBuilders, VariableValueSelectors, SceneControlsSpacer,
} from '@grafana/scenes';

export function getMyFeatureScene(params: { datasource: DataSourceRef }) {
  const queryRunner = new SceneQueryRunner({
    datasource: params.datasource,
    queries: [{ refId: 'A', expr: 'up{cluster=~"$cluster"}', instant: true, format: 'table' }],
  });

  const panel = PanelBuilders.table()
    .setData(queryRunner)
    .setTitle('My Table')
    .build();

  return new EmbeddedScene({
    $variables: new SceneVariableSet({
      variables: [
        new QueryVariable({
          name: 'cluster',
          query: 'label_values(up, cluster)',
          datasource: params.datasource,
          isMulti: true, includeAll: true, defaultToAll: true,
        }),
      ],
    }),
    controls: [new VariableValueSelectors({}), new SceneControlsSpacer()],
    body: new SceneFlexLayout({
      direction: 'column',
      children: [new SceneFlexItem({ body: panel })],
    }),
  });
}
```

### 2. 创建页面

```typescript
// src/components/scenes/MyFeature/MyFeature.tsx
import { SceneAppPage, SceneTimeRange } from '@grafana/scenes';

export function getMyFeaturePage(params) {
  return new SceneAppPage({
    title: 'My Feature',
    url: '/a/my-plugin-id/my-feature',
    routePath: 'my-feature/*',
    $timeRange: new SceneTimeRange({ from: 'now-1h', to: 'now' }),
    getScene: () => getMyFeatureScene(params),
    drilldowns: [],
  });
}
```

### 3. 在 SceneApp 中注册

将页面添加到根场景文件中 `SceneApp` 页面数组中。

## 关键模式

### 下钻（点击导航）

```typescript
drilldowns: [{
  routePath: ':cluster/*',
  getPage: (match, parent) => new SceneAppPage({
    title: decodeURIComponent(match.params.cluster),
    url: `${parent.state.url}/${match.params.cluster}`,
    routePath: `${match.params.cluster}/*`,
    getScene: () => detailScene(decodeURIComponent(match.params.cluster)),
  }),
}]
```

### 标签页（详情视图中的子页面）

在 `SceneAppPage` 上传递 `tabs: [SceneAppPage, ...]` 而不是 `getScene`。每个标签页本身都是一个拥有自己场景的 `SceneAppPage`。

### 带转换的查询

将 `SceneQueryRunner` 包裹在 `SceneDataTransformer` 中以应用 Grafana 转换或自定义 RxJS 操作符：

```typescript
new SceneDataTransformer({
  $data: queryRunner,
  transformations: [
    { id: 'organize', options: { renameByName: { 'Value #A': 'CPU' } } },
    (ctx) => (source) => source.pipe(map((frames) => /* 自定义转换 */)),
  ],
})
```

### 自定义场景对象

通过静态 `Component` 扩展 `SceneObjectBase` 以实现自定义交互式 UI：

```typescript
class MyWidget extends SceneObjectBase<MyWidgetState> {
  static Component = ({ model }: SceneComponentProps<MyWidget>) => {
    const state = model.useState();
    return <div>{state.value}</div>;
  };
}
```

### 表格列覆盖

构建 `ConfigOverrideRule` 对象用于下钻链接、过滤、单位、宽度、自定义单元格。

### 面板类型

`PanelBuilders.table()`, `.timeseries()`, `.stat()`, `.gauge()`, `.barchart()` — 链接 `.setData()`, `.setTitle()`, `.setUnit()`, `.setOption()`, `.setOverrides()`, 然后调用 `.build()`。

## 常见陷阱

- 对于具有下钻或标签页的页面，始终使用 `routePath: 'path/*'`（带通配符）
- `encodeURIComponent`/`decodeURIComponent` URL 参数 — K8s 名称可能包含 `/`
- 查询中引用的变量 `$varName` 必须存在于祖先 `SceneVariableSet` 中
- `getScene` 是惰性调用的；不要在工厂中创建副作用
- 对于即时查询，设置 `instant: true` 和 `format: 'table'` 都需要

## 资源

- [@grafana/scenes 文档](https://grafana.com/docs/grafana/latest/developers/plugins/create-plugin-ui/grafana-scenes/)
- [@grafana/scenes npm](https://www.npmjs.com/package/@grafana/scenes)
- [Grafana 插件工具](https://grafana.com/developers/plugin-tools/)
