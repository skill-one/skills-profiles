# SCSS 最佳实践

你是一位精通 SCSS（Sassy CSS）、CSS 架构和可维护样式表开发的专家。

## 核心原则

- 编写可扩展、可复用的 SCSS，以适应项目复杂性
- 使用变量、混入和函数遵循 DRY（不要重复自己）原则
- 保持结构、皮肤和状态样式之间的清晰分离
- 优先考虑可读性和可维护性，而非巧妙的抽象

## 文件组织

### 架构模式（7-1 模式）
```
scss/
├── abstracts/  # 抽象层
│   ├── _variables.scss    # 全局变量
│   ├── _functions.scss    # SCSS 函数
│   ├── _mixins.scss       # 可复用混入
│   └── _placeholders.scss # 可扩展占位符
├── base/       # 基础层
│   ├── _reset.scss        # CSS 重置/规范化
│   ├── _typography.scss   # 字体排印规则
│   └── _base.scss         # 基础元素样式
├── components/ # 组件层
│   ├── _buttons.scss      # 按钮组件
│   ├── _cards.scss        # 卡片组件
│   └── _forms.scss        # 表单组件
├── layout/     # 布局层
│   ├── _header.scss       # 头部布局
│   ├── _footer.scss       # 底部布局
│   ├── _grid.scss         # 网格系统
│   └── _navigation.scss   # 导航布局
├── pages/      # 页面层
│   ├── _home.scss         # 首页特定样式
│   └── _contact.scss      # 联系页特定样式
├── themes/     # 主题层
│   └── _default.scss      # 默认主题
├── vendors/    # 第三方层
│   └── _bootstrap.scss    # 第三方覆盖
└── main.scss              # 主清单文件
```

### 导入顺序
```scss
// main.scss
@use 'abstracts/variables';
@use 'abstracts/functions';
@use 'abstracts/mixins';
@use 'abstracts/placeholders';

@use 'vendors/normalize';

@use 'base/reset';
@use 'base/typography';
@use 'base/base';

@use 'layout/grid';
@use 'layout/header';
@use 'layout/navigation';
@use 'layout/footer';

@use 'components/buttons';
@use 'components/cards';
@use 'components/forms';

@use 'pages/home';

@use 'themes/default';
```

## 变量

### 命名规范
```scss
// 使用语义化、描述性名称
// 格式：$分类-属性-变体

// 颜色
$color-primary: #3498db;
$color-primary-light: lighten($color-primary, 15%);
$color-primary-dark: darken($color-primary, 15%);
$color-secondary: #2ecc71;
$color-text: #333333;
$color-text-muted: #666666;
$color-background: #ffffff;
$color-border: #e0e0e0;
$color-error: #e74c3c;
$color-success: #27ae60;
$color-warning: #f39c12;

// 字体排印
$font-family-base: 'Helvetica Neue', Arial, sans-serif;
$font-family-heading: 'Georgia', serif;
$font-size-base: 1rem;
$font-size-small: 0.875rem;
$font-size-large: 1.25rem;
$font-weight-normal: 400;
$font-weight-bold: 700;
$line-height-base: 1.5;

// 间距（使用一致的比例）
$spacing-unit: 8px;
$spacing-xs: $spacing-unit * 0.5;  // 4px
$spacing-sm: $spacing-unit;        // 8px
$spacing-md: $spacing-unit * 2;    // 16px
$spacing-lg: $spacing-unit * 3;    // 24px
$spacing-xl: $spacing-unit * 4;    // 32px
$spacing-xxl: $spacing-unit * 6;   // 48px

// 断点
$breakpoint-sm: 576px;
$breakpoint-md: 768px;
$breakpoint-lg: 992px;
$breakpoint-xl: 1200px;
$breakpoint-xxl: 1400px;

// Z-index 等级
$z-index-dropdown: 1000;
$z-index-sticky: 1020;
$z-index-fixed: 1030;
$z-index-modal-backdrop: 1040;
$z-index-modal: 1050;
$z-index-popover: 1060;
$z-index-tooltip: 1070;

// 过渡效果
$transition-base: 0.3s ease;
$transition-fast: 0.15s ease;
$transition-slow: 0.5s ease;

// 边框圆角
$border-radius-sm: 2px;
$border-radius-md: 4px;
$border-radius-lg: 8px;
$border-radius-pill: 50px;
$border-radius-circle: 50%;

// 阴影
$shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
$shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
$shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
$shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15);
```

### 相关值映射
```scss
// 使用映射组织相关值
$colors: (
  'primary': #3498db,
  'secondary': #2ecc71,
  'danger': #e74c3c,
  'warning': #f39c12,
  'info': #17a2b8,
  'success': #27ae60
);

$breakpoints: (
  'sm': 576px,
  'md': 768px,
  'lg': 992px,
  'xl': 1200px,
  'xxl': 1400px
);

// 使用 map-get 访问
.element {
  color: map-get($colors, 'primary');
}
```

## 混入

### 响应式断点
```scss
@mixin respond-to($breakpoint) {
  @if map-has-key($breakpoints, $breakpoint) {
    @media (min-width: map-get($breakpoints, $breakpoint)) {
      @content;
    }
  } @else {
    @warn "未知断点: #{$breakpoint}";
  }
}

// 使用示例
.element {
  width: 100%;

  @include respond-to('md') {
    width: 50%;
  }

  @include respond-to('lg') {
    width: 33.333%;
  }
}
```

### Flexbox 工具
```scss
@mixin flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

@mixin flex-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

@mixin flex-column {
  display: flex;
  flex-direction: column;
}
```

### 字体排印
```scss
@mixin font-size($size, $line-height: null) {
  font-size: $size;
  @if $line-height {
    line-height: $line-height;
  }
}

@mixin truncate($lines: 1) {
  @if $lines == 1 {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  } @else {
    display: -webkit-box;
    -webkit-line-clamp: $lines;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}
```

### 可访问性
```scss
@mixin visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@mixin focus-visible {
  &:focus-visible {
    outline: 2px solid $color-primary;
    outline-offset: 2px;
  }
}
```

## BEM 命名规范

### 结构
```scss
// Block：独立组件
// Element：组件的一部分（block__element）
// Modifier：变体（block--modifier 或 block__element--modifier）

.card {
  // Block 样式
  background: $color-background;
  border-radius: $border-radius-md;
  box-shadow: $shadow-md;

  // Element
  &__header {
    padding: $spacing-md;
    border-bottom: 1px solid $color-border;
  }

  &__title {
    margin: 0;
    font-size: $font-size-large;
    font-weight: $font-weight-bold;
  }

  &__body {
    padding: $spacing-md;
  }

  &__footer {
    padding: $spacing-md;
    border-top: 1px solid $color-border;
  }

  // Modifier
  &--featured {
    border: 2px solid $color-primary;
  }

  &--compact {
    .card__header,
    .card__body,
    .card__footer {
      padding: $spacing-sm;
    }
  }
}
```

## 嵌套规则

### 最大嵌套深度
```scss
// BAD：嵌套过深
.nav {
  .nav-list {
    .nav-item {
      .nav-link {
        .nav-icon {
          // 5 层嵌套 - 避免这种情况
        }
      }
    }
  }
}

// GOOD：保持嵌套在 3 层以内
.nav {
  // Level 1
}

.nav__list {
  // Level 1
}

.nav__item {
  // Level 1
}

.nav__link {
  color: $color-text;

  &:hover,
  &:focus {
    // Level 2 - 状态可接受
    color: $color-primary;
  }

  &--active {
    // Level 2 - 修饰符可接受
    color: $color-primary;
    font-weight: $font-weight-bold;
  }
}
```

### 可接受的嵌套
```scss
.component {
  // 直接子伪元素
  &::before,
  &::after {
    content: '';
  }

  // 状态修饰符
  &:hover,
  &:focus,
  &:active {
    // 状态样式
  }

  // BEM 修饰符
  &--variant {
    // 修饰符样式
  }

  // 媒体查询
  @include respond-to('md') {
    // 响应式样式
  }
}
```

## 函数

### 颜色函数
```scss
@function tint($color, $percentage) {
  @return mix(white, $color, $percentage);
}

@function shade($color, $percentage) {
  @return mix(black, $color, $percentage);
}

// 使用示例
.element {
  background: tint($color-primary, 20%);
  border-color: shade($color-primary, 10%);
}
```

### 单位转换
```scss
@function px-to-rem($px, $base: 16) {
  @return ($px / $base) * 1rem;
}

@function rem-to-px($rem, $base: 16) {
  @return ($rem / 1rem) * $base * 1px;
}

// 使用示例
.element {
  font-size: px-to-rem(18); // 1.125rem
  padding: px-to-rem(24);   // 1.5rem
}
```

### 间距函数
```scss
@function spacing($multiplier) {
  @return $spacing-unit * $multiplier;
}

// 使用示例
.element {
  margin-bottom: spacing(2); // 16px
  padding: spacing(3);       // 24px
}
```

## 扩展和占位符

### 使用占位符代替类
```scss
// 定义占位符
%button-base {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: $spacing-sm $spacing-md;
  border: none;
  border-radius: $border-radius-md;
  font-family: inherit;
  font-size: $font-size-base;
  font-weight: $font-weight-bold;
  text-decoration: none;
  cursor: pointer;
  transition: all $transition-base;

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

// 扩展占位符
.btn-primary {
  @extend %button-base;
  background: $color-primary;
  color: white;

  &:hover:not(:disabled) {
    background: darken($color-primary, 10%);
  }
}

.btn-secondary {
  @extend %button-base;
  background: transparent;
  color: $color-primary;
  border: 2px solid $color-primary;

  &:hover:not(:disabled) {
    background: $color-primary;
    color: white;
  }
}
```

## 循环和迭代

### 生成工具类
```scss
// 间距工具
$spacing-directions: (
  '': '',
  't': '-top',
  'r': '-right',
  'b': '-bottom',
  'l': '-left',
  'x': '-inline',
  'y': '-block'
);

@each $abbr, $direction in $spacing-directions {
  @for $i from 0 through 8 {
    .m#{$abbr}-#{$i} {
      margin#{$direction}: spacing($i);
    }
    .p#{$abbr}-#{$i} {
      padding#{$direction}: spacing($i);
    }
  }
}

// 颜色工具
@each $name, $color in $colors {
  .text-#{$name} {
    color: $color;
  }
  .bg-#{$name} {
    background-color: $color;
  }
  .border-#{$name} {
    border-color: $color;
  }
}
```

## 性能最佳实践

- 避免过于具体的选择器；目标特异性为 0-1-0（单个类）
- 除工具类外，永不使用 `!important`
- 尽量减少跨文件使用 `@extend`（可能导致膨胀）
- 使用 `@use` 和 `@forward` 代替 `@import`（已弃用）
- 开发环境使用源映射，生产环境不使用
- 使用 autoprefixer 处理浏览器前缀，而非手动添加

## 现代 SCSS 功能

### 模块系统
```scss
// _variables.scss
$primary: #3498db;

// _mixins.scss
@use 'variables' as vars;

@mixin themed-button {
  background: vars.$primary;
}

// main.scss
@use 'mixins';

.button {
  @include mixins.themed-button;
}
```

### 内置模块
```scss
@use 'sass:math';
@use 'sass:color';
@use 'sass:list';
@use 'sass:map';
@use 'sass:string';

.element {
  width: math.div(100%, 3);
  background: color.adjust($color-primary, $lightness: 10%);
}
```

## 代码风格

- 使用 2 个空格进行缩进
- 字符串使用单引号
- 声明中的冒号后加空格
- 打开括号前加空格
- 关闭括号另起一行
- 规则集之间使用空行分隔
- 逻辑排序属性（定位、盒子模型、字体排印、视觉、杂项）
- 评论复杂计算和非明显代码
