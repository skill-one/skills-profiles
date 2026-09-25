# Ionic Framework 设计指南

使用 Ionic Framework 和 Capacitor 构建精美、原生外观的移动应用。

## 何时使用此技能

- 用户正在使用 Ionic 组件
- 用户希望获得原生外观的 UI
- 用户询问关于 Ionic 主题的问题
- 用户需要移动 UI 模式
- 用户希望进行平台特定的样式设置

## Ionic Framework 是什么？

Ionic 提供：
- 100 多个移动优化的 UI 组件
- 自动化的 iOS/Android 平台样式
- 内置的暗黑模式支持
- 开箱即用的无障碍功能
- 支持 React、Vue、Angular 或原生 JavaScript

## 入门指南

### 安装

```bash
# 对于 React
npx create-vite@latest my-app --template react-ts
cd my-app
npm install @ionic/react @ionic/react-router

# 对于 Vue
npx create-vite@latest my-app --template vue-ts
cd my-app
npm install @ionic/vue @ionic/vue-router

# 添加 Capacitor
npm install @capacitor/core @capacitor/cli
npx cap init
```

### 设置（React）

```typescript
// main.tsx
import React from 'react';
import { createRoot } from 'react-dom/client';
import { IonApp, setupIonicReact } from '@ionic/react';
import App from './App';

/* 核心样式，用于 Ionic 组件正常工作 */
import '@ionic/react/css/core.css';

/* 基础样式，用于使用 Ionic 构建的应用 */
import '@ionic/react/css/normalize.css';
import '@ionic/react/css/structure.css';
import '@ionic/react/css/typography.css';

/* 可选的样式工具 */
import '@ionic/react/css/padding.css';
import '@ionic/react/css/float-elements.css';
import '@ionic/react/css/text-alignment.css';
import '@ionic/react/css/text-transformation.css';
import '@ionic/react/css/flex-utils.css';
import '@ionic/react/css/display.css';

/* 主题 */
import './theme/variables.css';

setupIonicReact();

const root = createRoot(document.getElementById('root')!);
root.render(
  <IonApp>
    <App />
  </IonApp>
);
```

## 核心组件

### 页面结构

```tsx
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonButtons,
  IonBackButton,
} from '@ionic/react';

function MyPage() {
  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start">
            <IonBackButton defaultHref="/home" />
          </IonButtons>
          <IonTitle>页面标题</IonTitle>
        </IonToolbar>
      </IonHeader>

      <IonContent fullscreen>
        {/* iOS 的大标题 */}
        <IonHeader collapse="condense">
          <IonToolbar>
            <IonTitle size="large">页面标题</IonTitle>
          </IonToolbar>
        </IonHeader>

        {/* 页面内容 */}
        <div className="ion-padding">
          您的内容在这里
        </div>
      </IonContent>
    </IonPage>
  );
}
```

### 列表

```tsx
import {
  IonList,
  IonItem,
  IonLabel,
  IonNote,
  IonAvatar,
  IonIcon,
  IonItemSliding,
  IonItemOptions,
  IonItemOption,
} from '@ionic/react';
import { chevronForward, trash, archive } from 'ionicons/icons';

function ContactList() {
  return (
    <IonList>
      {/* 简单项 */}
      <IonItem>
        <IonLabel>简单项</IonLabel>
      </IonItem>

      {/* 带详情的项 */}
      <IonItem detail button>
        <IonLabel>
          <h2>项标题</h2>
          <p>项描述文本</p>
        </IonLabel>
        <IonNote slot="end">注释</IonNote>
      </IonItem>

      {/* 带头像的项 */}
      <IonItem>
        <IonAvatar slot="start">
          <img src="/avatar.jpg" alt="" />
        </IonAvatar>
        <IonLabel>
          <h2>约翰·多伊</h2>
          <p>john@example.com</p>
        </IonLabel>
      </IonItem>

      {/* 滑动项 */}
      <IonItemSliding>
        <IonItem>
          <IonLabel>滑动我</IonLabel>
        </IonItem>
        <IonItemOptions side="end">
          <IonItemOption color="danger">
            <IonIcon slot="icon-only" icon={trash} />
          </IonItemOption>
          <IonItemOption>
            <IonIcon slot="icon-only" icon={archive} />
          </IonItemOption>
        </IonItemOptions>
      </IonItemSliding>
    </IonList>
  );
}
```

### 表单

```tsx
import {
  IonInput,
  IonTextarea,
  IonSelect,
  IonSelectOption,
  IonToggle,
  IonCheckbox,
  IonRadioGroup,
  IonRadio,
  IonItem,
  IonLabel,
  IonButton,
} from '@ionic/react';

function MyForm() {
  return (
    <form>
      {/* 文本输入 */}
      <IonItem>
        <IonInput
          label="邮箱"
          labelPlacement="floating"
          type="email"
          placeholder="输入邮箱"
        />
      </IonItem>

      {/* 密码 */}
      <IonItem>
        <IonInput
          label="密码"
          labelPlacement="floating"
          type="password"
        />
      </IonItem>

      {/* 文本域 */}
      <IonItem>
        <IonTextarea
          label="简介"
          labelPlacement="floating"
          rows={4}
          placeholder="告诉我们关于您自己的信息"
        />
      </IonItem>

      {/* 选择 */}
      <IonItem>
        <IonSelect label="国家" placeholder="选择">
          <IonSelectOption value="us">美国</IonSelectOption>
          <IonSelectOption value="uk">英国</IonSelectOption>
          <IonSelectOption value="de">德国</IonSelectOption>
        </IonSelect>
      </IonItem>

      {/* 开关 */}
      <IonItem>
        <IonToggle>启用通知</IonToggle>
      </IonItem>

      {/* 复选框 */}
      <IonItem>
        <IonCheckbox slot="start" />
        <IonLabel>我同意条款</IonLabel>
      </IonItem>

      {/* 单选按钮组 */}
      <IonRadioGroup>
        <IonItem>
          <IonRadio value="small">小</IonRadio>
        </IonItem>
        <IonItem>
          <IonRadio value="medium">中</IonRadio>
        </IonItem>
        <IonItem>
          <IonRadio value="large">大</IonRadio>
        </IonItem>
      </IonRadioGroup>

      <IonButton expand="block" type="submit">
        提交
      </IonButton>
    </form>
  );
}
```

### 按钮

```tsx
import { IonButton, IonIcon } from '@ionic/react';
import { heart, share, download } from 'ionicons/icons';

function Buttons() {
  return (
    <>
      {/* 填充变体 */}
      <IonButton>Solid</IonButton>
      <IonButton fill="outline">Outline</IonButton>
      <IonButton fill="clear">Clear</IonButton>

      {/* 颜色 */}
      <IonButton color="primary">Primary</IonButton>
      <IonButton color="secondary">Secondary</IonButton>
      <IonButton color="danger">Danger</IonButton>
      <IonButton color="success">Success</IonButton>

      {/* 尺寸 */}
      <IonButton size="small">Small</IonButton>
      <IonButton size="default">Default</IonButton>
      <IonButton size="large">Large</IonButton>

      {/* 带图标 */}
      <IonButton>
        <IonIcon slot="start" icon={heart} />
        Like
      </IonButton>

      {/* 仅图标 */}
      <IonButton>
        <IonIcon slot="icon-only" icon={share} />
      </IonButton>

      {/* 全宽 */}
      <IonButton expand="block">Block Button</IonButton>
      <IonButton expand="full">Full Width</IonButton>
    </>
  );
}
```

### 卡片

```tsx
import {
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardSubtitle,
  IonCardContent,
  IonImg,
  IonButton,
} from '@ionic/react';

function Cards() {
  return (
    <IonCard>
      <IonImg src="/card-image.jpg" alt="" />
      <IonCardHeader>
        <IonCardSubtitle>卡片副标题</IonCardSubtitle>
        <IonCardTitle>卡片标题</IonCardTitle>
      </IonCardHeader>
      <IonCardContent>
        卡片内容放在这里。这是一个标准的卡片，包含图像、标题、副标题和内容。
      </IonCardContent>
      <div className="ion-padding-horizontal ion-padding-bottom">
        <IonButton fill="clear">操作 1</IonButton>
        <IonButton fill="clear">操作 2</IonButton>
      </div>
    </IonCard>
  );
}
```

### 模态框和抽屉

```tsx
import { IonModal, IonButton, IonContent, IonHeader, IonToolbar, IonTitle } from '@ionic/react';
import { useState, useRef } from 'react';

function ModalExample() {
  const [isOpen, setIsOpen] = useState(false);
  const modal = useRef<HTMLIonModalElement>(null);

  return (
    <>
      <IonButton onClick={() => setIsOpen(true)}>打开模态框</IonButton>

      {/* 全页模态框 */}
      <IonModal isOpen={isOpen} onDidDismiss={() => setIsOpen(false)}>
        <IonHeader>
          <IonToolbar>
            <IonTitle>模态框标题</IonTitle>
            <IonButton slot="end" onClick={() => setIsOpen(false)}>
              关闭
            </IonButton>
          </IonToolbar>
        </IonHeader>
        <IonContent>
          <p>模态框内容</p>
        </IonContent>
      </IonModal>

      {/* 底部抽屉 */}
      <IonModal
        ref={modal}
        trigger="open-sheet"
        initialBreakpoint={0.5}
        breakpoints={[0, 0.25, 0.5, 0.75, 1]}
      >
        <IonContent>
          <div className="ion-padding">
            <h2>抽屉内容</h2>
            <p>拖动以调整大小</p>
          </div>
        </IonContent>
      </IonModal>
      <IonButton id="open-sheet">打开抽屉</IonButton>
    </>
  );
}
```

## 导航

### 标签导航

```tsx
import {
  IonTabs,
  IonTabBar,
  IonTabButton,
  IonIcon,
  IonLabel,
  IonRouterOutlet,
} from '@ionic/react';
import { Route, Redirect } from 'react-router-dom';
import { home, search, person } from 'ionicons/icons';

function TabsLayout() {
  return (
    <IonTabs>
      <IonRouterOutlet>
        <Route exact path="/tabs/home" component={HomePage} />
        <Route exact path="/tabs/search" component={SearchPage} />
        <Route exact path="/tabs/profile" component={ProfilePage} />
        <Route exact path="/tabs">
          <Redirect to="/tabs/home" />
        </Route>
      </IonRouterOutlet>

      <IonTabBar slot="bottom">
        <IonTabButton tab="home" href="/tabs/home">
          <IonIcon icon={home} />
          <IonLabel>首页</IonLabel>
        </IonTabButton>
        <IonTabButton tab="search" href="/tabs/search">
          <IonIcon icon={search} />
          <IonLabel>搜索</IonLabel>
        </IonTabButton>
        <IonTabButton tab="profile" href="/tabs/profile">
          <IonIcon icon={person} />
          <IonLabel>个人资料</IonLabel>
        </IonTabButton>
      </IonTabBar>
    </IonTabs>
  );
}
```

### 栈导航

```tsx
import { IonReactRouter } from '@ionic/react-router';
import { IonRouterOutlet } from '@ionic/react';
import { Route } from 'react-router-dom';

function App() {
  return (
    <IonReactRouter>
      <IonRouterOutlet>
        <Route exact path="/" component={Home} />
        <Route exact path="/detail/:id" component={Detail} />
      </IonRouterOutlet>
    </IonReactRouter>
  );
}
```

## 主题

### 主题变量

```css
/* theme/variables.css */
:root {
  /* 主要颜色 */
  --ion-color-primary: #3880ff;
  --ion-color-primary-rgb: 56, 128, 255;
  --ion-color-primary-contrast: #ffffff;
  --ion-color-primary-shade: #3171e0;
  --ion-color-primary-tint: #4c8dff;

  /* 次要颜色 */
  --ion-color-secondary: #3dc2ff;

  /* 自定义颜色 */
  --ion-color-brand: #ff6b35;
  --ion-color-brand-rgb: 255, 107, 53;
  --ion-color-brand-contrast: #ffffff;
  --ion-color-brand-shade: #e05e2f;
  --ion-color-brand-tint: #ff7a49;
}

/* 暗黑模式 */
@media (prefers-color-scheme: dark) {
  :root {
    --ion-background-color: #121212;
    --ion-text-color: #ffffff;
    --ion-color-step-50: #1e1e1e;
    --ion-color-step-100: #2a2a2a;
  }
}

/* iOS 特定 */
.ios {
  --ion-toolbar-background: #f8f8f8;
}

/* Android 特定 */
.md {
  --ion-toolbar-background: #ffffff;
}
```

### 自定义组件样式

```css
/* 全局样式 */
ion-content {
  --background: var(--ion-background-color);
}

ion-card {
  --background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

/* 平台特定 */
.ios ion-toolbar {
  --border-width: 0;
}

.md ion-toolbar {
  --border-width: 0 0 1px 0;
}
```

## 平台特定代码

### 检测平台

```typescript
import { isPlatform } from '@ionic/react';

// 检查平台
if (isPlatform('ios')) {
  // iOS 特定代码
}

if (isPlatform('android')) {
  // Android 特定代码
}

if (isPlatform('hybrid')) {
  // 在原生应用中运行
}

if (isPlatform('mobileweb')) {
  // 在移动浏览器中运行
}
```

### 条件渲染

```tsx
import { isPlatform, IonIcon } from '@ionic/react';
import { chevronBack, arrowBack } from 'ionicons/icons';

function BackButton() {
  return (
    <IonIcon
      icon={isPlatform('ios') ? chevronBack : arrowBack}
    />
  );
}
```

## 最佳实践

### 性能

```tsx
// 使用 IonVirtualScroll 用于长列表
import { IonVirtualScroll } from '@ionic/react';

<IonVirtualScroll
  items={items}
  renderItem={(item) => (
    <IonItem key={item.id}>
      <IonLabel>{item.name}</IonLabel>
    </IonItem>
  )}
/>

// 懒加载图片
<IonImg src={url} />  // 自动懒加载
```

### 无障碍

```tsx
// 始终提供标签
<IonButton aria-label="删除项">
  <IonIcon slot="icon-only" icon={trash} />
</IonButton>

// 使用语义元素
<IonItem button role="link">
  <IonLabel>可点击项</IonLabel>
</IonItem>
```

### 安全区域

```tsx
// 内容默认尊重安全区域
<IonContent>
  {/* 自动填充以适应凹口/主指示器 */}
</IonContent>

// 自定义安全区域处理
<div style={{ paddingTop: 'env(safe-area-inset-top)' }}>
  自定义头部
</div>
```

## 资源

- Ionic 文档：https://ionicframework.com/docs
- Ionic 组件：https://ionicframework.com/docs/components
- Ionicons：https://ionic.io/ionicons
- 颜色生成器：https://ionicframework.com/docs/theming/color-generator
