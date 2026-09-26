# 良好的 Alpine 组件

## 概述

本技能为在 Hyvä 主题中编写 CSP 兼容的 Alpine.js 组件提供指导。Alpine CSP 是一个特殊的 Alpine.js 构建，它不使用 `unsafe-eval` CSP 指令，这对于支付相关页面（自 2025 年 4 月 1 日起强制要求）的 PCI-DSS 4.0 合规性是必需的。

**主要原则：** CSP 兼容的代码在标准构建和 Alpine CSP 构建中都能正常工作。为了未来兼容性，请使用 CSP 模式编写所有 Alpine 代码。

## CSP 限制摘要

| 功能 | 标准Alpine | Alpine CSP |
|------|-----------|-----------|
| 属性读取 | `x-show="open"` | 相同 |
| 否定 | `x-show="!open"` | 方法：`x-show="isNotOpen"` |
| 变更 | `@click="open = false"` | 方法：`@click="close"` |
| 方法参数 | `@click="setTab('info')"` | 数据集：`@click="setTab" data-tab="info"` |
| `x-model` | 可用 | **不支持** - 使用 `:value` + `@input` |
| 范围迭代 | `x-for="i in 10"` | **不支持** |

## 组件结构模式

Hyvä 中的每个 Alpine 组件都遵循此结构：

```html
<div x-data="initComponentName">
    <!-- 模板内容 -->
</div>
<script>
    function initComponentName() {
        return {
            // 属性
            propertyName: initialValue,

            // 生命周期
            init() {
                // 组件初始化时调用
            },

            // 用于状态访问的方法
            isPropertyTrue() {
                return this.propertyName === true;
            },

            // 用于变更的方法
            setPropertyValue() {
                this.propertyName = this.$event.target.value;
            }
        }
    }
    window.addEventListener('alpine:init', () => Alpine.data('initComponentName', initComponentName), {once: true})
</script>
<?php $hyvaCsp->registerInlineScript() ?>
```

**关键要求：**
1. 在 `alpine:init` 事件监听器中使用 `Alpine.data()` 注册构造函数
2. 使用 `{once: true}` 防止重复注册
3. 在每个 `<script>` 块之后调用 `$hyvaCsp->registerInlineScript()`
4. 在 JavaScript 字符串中使用 PHP 值时使用 `$escaper->escapeJs()`
5. 在数据属性中使用 `$escaper->escapeHtmlAttr()`（不要使用 `escapeJs`）

## 构造函数

### 基本注册

```javascript
function initMyComponent() {
    return {
        open: false
    }
}
window.addEventListener('alpine:init', () => Alpine.data('initMyComponent', initMyComponent), {once: true})
```

**为什么使用命名全局函数？** 构造函数在全局作用域中声明为命名函数（而不是在 `Alpine.data()` 回调中内联），以便它们可以在其他模板中被代理和扩展。这是 Hyvä 主题的可扩展性功能 - 其他模块或子主题可以在它们被 Alpine 注册之前包装或覆盖这些函数。

### 组合多个对象

组合对象时（例如，使用 `hyva.modal`），在构造函数内部使用展开语法：

```javascript
function initMyModal() {
    return {
        ...hyva.modal.call(this),
        ...hyva.formValidation(this.$el),
        customProperty: '',
        customMethod() {
            // 自定义逻辑
        }
    };
}
```

使用 `.call(this)` 将 Alpine 上下文传递给组合函数。

## 属性访问模式

### 使用点表示法的值属性

```javascript
return {
    item: {
        is_visible: true,
        title: 'Product'
    }
}
```

```html
<span x-show="item.is_visible" x-text="item.title"></span>
```

### 转换值（否定、条件）

CSP 不允许内联转换。创建方法代替：

**错误（CSP 不兼容）：**
```html
<span x-show="!item.deleted"></span>
<span x-text="item.title || item.value"></span>
```

**正确：**
```html
<span x-show="isItemNotDeleted"></span>
<span x-text="itemLabel"></span>
```

```javascript
return {
    item: { deleted: false, title: '', value: '' },

    isItemNotDeleted() {
        return !this.item.deleted;
    },
    itemLabel() {
        return this.item.title || this.item.value;
    }
}
```

### 否定方法简写

对于简单的布尔值否定，使用括号表示法：

```javascript
return {
    deleted: false,
    ['!deleted']() {
        return !this.deleted;
    }
}
```

```html
<template x-if="!deleted">
    <div>The item is present</div>
</template>
```

## 属性变更模式

### 将变更提取到方法

**错误（CSP 不兼容）：**
```html
<button @click="open = !open">Toggle</button>
```

**正确：**
```html
<button @click="toggle">Toggle</button>
```

```javascript
return {
    open: false,
    toggle() {
        this.open = !this.open;
    }
}
```

### 通过数据集传递参数

**错误（CSP 不兼容）：**
```html
<button @click="selectItem(123)">Select</button>
```

**正确：**
```html
<button @click="selectItem" data-item-id="<?= $escaper->escapeHtmlAttr($itemId) ?>">Select</button>
```

```javascript
return {
    selected: null,
    selectItem() {
        this.selected = this.$el.dataset.itemId;
    }
}
```

**重要：** 使用 `escapeHtmlAttr` 而不是 `escapeJs` 为数据属性。

### 在方法中访问事件和循环变量

方法可以访问 Alpine 的特殊属性：

```javascript
return {
    onInput() {
        // 访问事件
        const value = this.$event.target.value;
        this.inputValue = value;
    },
    getItemUrl() {
        // 访问 x-for 循环变量
        return `${BASE_URL}/product/id/${this.item.id}`;
    }
}
```

## x-model 替代方案

`x-model` 在 Alpine CSP 中**不可用**。请使用双向绑定模式代替。

### 文本输入

```html
<input type="text"
       :value="username"
       @input="setUsername">
```

```javascript
return {
    username: '',
    setUsername() {
        this.username = this.$event.target.value;
    }
}
```

### 数字输入

使用 `hyva.safeParseNumber()` 处理数值：

```javascript
return {
    quantity: 1,
    setQuantity() {
        this.quantity = hyva.safeParseNumber(this.$event.target.value);
    }
}
```

### 文本区域

```html
<textarea @input="setComment" x-text="comment"></textarea>
```

```javascript
return {
    comment: '',
    setComment() {
        this.comment = this.$event.target.value;
    }
}
```

### 复选框

```html
<input type="checkbox"
       :checked="isSubscribed"
       @change="toggleSubscribed">
```

```javascript
return {
    isSubscribed: false,
    toggleSubscribed() {
        this.isSubscribed = this.$event.target.checked;
    }
}
```

### 复选框数组

```html
<template x-for="option in options" :key="option.id">
    <input type="checkbox"
           :value="option.id"
           :checked="isOptionSelected"
           @change="toggleOption"
           :data-option-id="option.id">
</template>
```

```javascript
return {
    selectedOptions: [],
    isOptionSelected() {
        return this.selectedOptions.includes(this.option.id);
    },
    toggleOption() {
        const optionId = this.$el.dataset.optionId;
        const index = this.selectedOptions.indexOf(optionId);
        if (index === -1) {
            this.selectedOptions.push(optionId);
        } else {
            this.selectedOptions.splice(index, 1);
        }
    }
}
```

### 选择元素

```html
<select @change="setCountry">
    <template x-for="country in countries" :key="country.code">
        <option :value="country.code"
                :selected="isCountrySelected"
                x-text="country.name"></option>
    </template>
</select>
```

```javascript
return {
    selectedCountry: '',
    isCountrySelected() {
        return this.selectedCountry === this.country.code;
    },
    setCountry() {
        this.selectedCountry = this.$event.target.value;
    }
}
```

## x-for 模式

### 基本迭代

```html
<template x-for="(product, index) in products" :key="index">
    <div x-text="product.name"></div>
</template>
```

### 在循环中使用方法

循环变量（`product`、`index`）可以在方法中访问：

```html
<template x-for="(product, index) in products" :key="index">
    <span :class="getItemClasses" @click="goToProduct" x-text="product.name"></span>
</template>
```

```javascript
return {
    products: [],
    getItemClasses() {
        return {
            'font-bold': this.index === 0,
            'text-gray-500': this.product.disabled
        };
    },
    goToProduct() {
        window.location.href = `${BASE_URL}/product/${this.product.url_key}`;
    }
}
```

### 函数作为值提供者

值提供者可以是方法（不带括号调用）：

```html
<template x-for="(item, index) in getFilteredItems" :key="index">
    <div x-text="item.name"></div>
</template>
```

```javascript
return {
    items: [],
    filter: '',
    getFilteredItems() {
        return this.items.filter(item => item.name.includes(this.filter));
    }
}
```

**注意：** 范围迭代（`x-for="i in 10"`）在 Alpine CSP 中不受支持。

## Hyva 实用函数

全局 `hyva` 对象提供以下实用工具：

### 表单和安全
- `hyva.getFormKey()` - 获取/生成用于 POST 请求的表单密钥
- `hyva.getUenc()` - Base64 编码当前 URL 用于重定向
- `hyva.postForm({action, data, skipUenc})` - 程序提交 POST 表单

### Cookie
- `hyva.getCookie(name)` - 获取 Cookie 值（尊重同意）
- `hyva.setCookie(name, value, days, skipSetDomain)` - 设置 Cookie
- `hyva.setSessionCookie(name, value, skipSetDomain)` - 设置会话 Cookie

### 格式化
- `hyva.formatPrice(value, showSign, options)` - 格式化货币
- `hyva.str(template, ...args)` - 带有 `%1`、`%2` 占位符的字符串插值
- `hyva.strf(template, ...args)` - 零基字符串插值（`%0`、`%1`）

### 数字
- `hyva.safeParseNumber(rawValue)` - 安全解析数字（用于 `x-model.number` 替代）

### DOM
- `hyva.replaceDomElement(selector, content)` - 用 HTML 内容替换 DOM 元素
- `hyva.trapFocus(rootElement)` - 在元素内锁定焦点（用于模态框）
- `hyva.releaseFocus(rootElement)` - 释放焦点锁定

### 存储
- `hyva.getBrowserStorage()` - 安全获取 localStorage/sessionStorage

### 布尔对象辅助工具

对于切换组件，使用 `hyva.createBooleanObject`：

```javascript
function initToggle() {
    return {
        ...hyva.createBooleanObject('open', false),
        // 其他方法
    };
}
```

这将生成：`open()`、`notOpen()`、`toggleOpen()`、`setOpenTrue()`、`setOpenFalse()`

### Alpine 初始化

```javascript
hyva.alpineInitialized(fn)  // Alpine 初始化后运行回调
```

## 事件模式

### 监听自定义事件

```html
<div x-data="initMyComponent"
     @private-content-loaded.window="onPrivateContentLoaded"
     @update-gallery.window="onGalleryUpdate">
```

```javascript
return {
    onPrivateContentLoaded() {
        const data = this.$event.detail.data;
        // 处理客户数据
    },
    onGalleryUpdate() {
        const images = this.$event.detail;
        this.images = images;
    }
}
```

### 分发事件

```javascript
return {
    updateQuantity() {
        this.qty = newValue;
        this.$dispatch('update-qty-' + this.productId, this.qty);
    }
}
```

### 常见 Hyvä 事件
- `private-content-loaded` - 客户部分数据加载
- `reload-customer-section-data` - 请求客户数据刷新
- `update-gallery` - 产品画廊图像更改
- `reset-gallery` - 重置画廊到初始状态

## 事件监听对象模式

对于多个窗口/文档事件监听器，使用 `x-bind` 模式：

```html
<div x-data="initGallery" x-bind="eventListeners">
```

```javascript
return {
    eventListeners: {
        ['@keydown.window.escape']() {
            if (!this.fullscreen) return;
            this.closeFullScreen();
        },
        ['@update-gallery.window'](event) {
            this.receiveImages(event.detail);
        },
        ['@keyup.arrow-right.window']() {
            if (!this.fullscreen) return;
            this.nextItem();
        }
    }
}
```

## 动态类模式

从方法返回类对象：

```html
<div :class="containerClasses">
```

```javascript
return {
    fullscreen: false,
    containerClasses() {
        return {
            'w-full h-full fixed top-0 left-0 bg-white z-50': this.fullscreen,
            'relative': !this.fullscreen
        };
    }
}
```

## 将 PHP 数据传递给组件

### 通过数据属性

```html
<div x-data="initProductList"
     data-products="<?= $escaper->escapeHtmlAttr(json_encode($products)) ?>"
     data-config="<?= $escaper->escapeHtmlAttr(json_encode($config)) ?>">
```

```javascript
return {
    products: [],
    config: {},
    init() {
        this.products = JSON.parse(this.$root.dataset.products || '[]');
        this.config = JSON.parse(this.$root.dataset.config || '{}');
    }
}
```

### 通过内联 JavaScript（带转义）

```javascript
function initComponent() {
    return {
        productId: '<?= (int) $product->getId() ?>',
        productName: '<?= $escaper->escapeJs($product->getName()) ?>',
        config: <?= /* @noEscape */ json_encode($config) ?>
    }
}
```

## 完整示例：数量选择器

```php
<?php
declare(strict_types=1);

use Hyva\Theme\ViewModel\HyvaCsp;
use Magento\Framework\Escaper;

/** @var Escaper $escaper */
/** @var HyvaCsp $hyvaCsp */

$productId = (int) $product->getId();
$minQty = 1;
$maxQty = 100;
$defaultQty = 1;
?>
<div x-data="initQtySelector">
    <label for="qty-<?= $productId ?>" class="sr-only">
        <?= $escaper->escapeHtml(__('Quantity')) ?>
    </label>
    <div class="flex items-center">
        <button type="button"
                class="btn"
                @click="decrement"
                :disabled="isMinQty"
                :class="decrementClasses">
            -
        </button>
        <input type="number"
               id="qty-<?= $productId ?>"
               name="qty"
               :value="qty"
               @input="onInput"
               min="<?= $minQty ?>"
               max="<?= $maxQty ?>"
               class="form-input w-16 text-center">
        <button type="button"
                class="btn"
                @click="increment"
                :disabled="isMaxQty"
                :class="incrementClasses">
            +
        </button>
    </div>
</div>
<script>
    function initQtySelector() {
        return {
            qty: <?= (int) $defaultQty ?>,
            minQty: <?= (int) $minQty ?>,
            maxQty: <?= (int) $maxQty ?>,
            productId: '<?= $productId ?>',

            onInput() {
                let value = hyva.safeParseNumber(this.$event.target.value);
                if (value < this.minQty) value = this.minQty;
                if (value > this.maxQty) value = this.maxQty;
                this.qty = value;
                this.$dispatch('update-qty-' + this.productId, this.qty);
            },

            increment() {
                if (this.qty < this.maxQty) {
                    this.qty++;
                    this.$dispatch('update-qty-' + this.productId, this.qty);
                }
            },

            decrement() {
                if (this.qty > this.minQty) {
                    this.qty--;
                    this.$dispatch('update-qty-' + this.productId, this.qty);
                }
            },

            isMinQty() {
                return this.qty <= this.minQty;
            },

            isMaxQty() {
                return this.qty >= this.maxQty;
            },

            decrementClasses() {
                return { 'opacity-50 cursor-not-allowed': this.isMinQty() };
            },

            incrementClasses() {
                return { 'opacity-50 cursor-not-allowed': this.isMaxQty() };
            }
        }
    }
    window.addEventListener('alpine:init', () => Alpine.data('initQtySelector', initQtySelector), {once: true})
</script>
<?php $hyvaCsp->registerInlineScript() ?>
```

## 参考

- Hyvä CSP 文档：https://docs.hyva.io/hyva-themes/writing-code/csp/alpine-csp.html
- Alpine.js 文档：https://alpinejs.dev/
- 示例组件：`vendor/hyva-themes/magento2-default-theme-csp/`
- 核心实用工具：`vendor/hyva-themes/magento2-theme-module/src/view/frontend/templates/page/js/hyva.phtml`

<!-- 版权所有 © Hyvä Themes https://hyva.io。保留所有权利。根据 OSL 3.0 许可。 -->
