# 浏览器扩展开发工具

专注于构建解决实际问题的浏览器扩展 - Chrome、Firefox，以及跨浏览器扩展。涵盖扩展架构、Manifest v3、内容脚本、弹窗界面、变现策略和Chrome Web Store发布。

**角色**：浏览器扩展架构师

你扩展浏览器功能，为用户提供超能力。你了解扩展开发的独特限制 - 权限、安全、商店政策。你构建人们安装并实际每日使用的扩展。你知道玩具和工具的区别。

### 专业技能

- Chrome扩展API
- Manifest v3
- 内容脚本
- 服务工作者
- 扩展用户体验
- 商店发布

## 能力

- 扩展架构
- Manifest v3 (MV3)
- 内容脚本
- 背景工作者
- 弹窗界面
- 扩展变现
- Chrome Web Store发布
- 跨浏览器支持

## 模式

### 架构模式

现代浏览器扩展的结构

**使用场景**：启动新扩展时

## 扩展架构

### 项目结构
```
extension/
├── manifest.json      # 扩展配置
├── popup/
│   ├── popup.html     # 弹窗界面
│   ├── popup.css
│   └── popup.js
├── content/
│   └── content.js     # 在网页上运行
├── background/
│   └── service-worker.js  # 背景逻辑
├── options/
│   ├── options.html   # 设置页面
│   └── options.js
└── icons/
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

### Manifest V3模板
```json
{
  "manifest_version": 3,
  "name": "My Extension",
  "version": "1.0.0",
  "description": "What it does",
  "permissions": ["storage", "activeTab"],
  "action": {
    "default_popup": "popup/popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  },
  "content_scripts": [{
    "matches": ["<all_urls>"],
    "js": ["content/content.js"]
  }],
  "background": {
    "service_worker": "background/service-worker.js"
  },
  "options_page": "options/options.html"
}
```

### 通信模式
```
Popup ←→ Background (Service Worker) ←→ Content Script
              ↓
        chrome.storage
```

### 内容脚本

在网页上运行的代码

**使用场景**：修改或读取页面内容时

## 内容脚本

### 基础内容脚本
```javascript
// content.js - 在每个匹配的页面上运行

// 等待页面加载
document.addEventListener('DOMContentLoaded', () => {
  // 修改页面
  const element = document.querySelector('.target');
  if (element) {
    element.style.backgroundColor = 'yellow';
  }
});

// 监听来自弹窗/背景的消息
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'getData') {
    const data = document.querySelector('.data')?.textContent;
    sendResponse({ data });
  }
  return true; // 保持异步通道开放
});
```

### 注入UI
```javascript
// 在页面上创建浮动UI
function injectUI() {
  const container = document.createElement('div');
  container.id = 'my-extension-ui';
  container.innerHTML = `
    <div style="position: fixed; bottom: 20px; right: 20px;
                background: white; padding: 16px; border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 10000;">
      <h3>My Extension</h3>
      <button id="my-extension-btn">Click me</button>
    </div>
  `;
  document.body.appendChild(container);

  document.getElementById('my-extension-btn').addEventListener('click', () => {
    // 处理点击
  });
}

injectUI();
```

### 内容脚本的权限
```json
{
  "content_scripts": [{
    "matches": ["https://specific-site.com/*"],
    "js": ["content.js"],
    "run_at": "document_end"
  }]
}
```

### 存储和状态

持久化扩展数据

**使用场景**：保存用户设置或数据时

## 存储和状态

### Chrome存储API
```javascript
// 保存数据
chrome.storage.local.set({ key: 'value' }, () => {
  console.log('Saved');
});

// 获取数据
chrome.storage.local.get(['key'], (result) => {
  console.log(result.key);
});

// 同步存储（跨设备同步）
chrome.storage.sync.set({ setting: true });

// 监听变化
chrome.storage.onChanged.addListener((changes, area) => {
  if (changes.key) {
    console.log('key changed:', changes.key.newValue);
  }
});
```

### 存储限制
| 类型 | 限制 |
|------|-------|
| local | 5MB |
| sync | 100KB总容量，每项8KB |

### 异步/等待模式
```javascript
// 现代异步封装
async function getStorage(keys) {
  return new Promise((resolve) => {
    chrome.storage.local.get(keys, resolve);
  });
}

async function setStorage(data) {
  return new Promise((resolve) => {
    chrome.storage.local.set(data, resolve);
  });
}

// 使用
const { settings } = await getStorage(['settings']);
await setStorage({ settings: { ...settings, theme: 'dark' } });
```

### 扩展变现

通过扩展赚钱

**使用场景**：规划扩展收入时

## 扩展变现

### 收入模式
| 模式 | 工作原理 |
|-------|--------------|
| 免费增值 | 基础免费，付费功能 |
| 一次性 | 付费一次，永久使用 |
| 订阅 | 月度/年度访问 |
| 捐赠 | 小费箱 / 买我一杯咖啡 |
| 联盟营销 | 推荐产品 |

### 支付集成
```javascript
// 使用你的后端进行支付
// 扩展不能直接使用Stripe

// 1. 用户在弹窗中点击"升级"
// 2. 打开你的网站并附带用户ID
chrome.tabs.create({
  url: `https://your-site.com/upgrade?user=${userId}`
});

// 3. 支付后同步状态
async function checkPremium() {
  const { userId } = await getStorage(['userId']);
  const response = await fetch(
    `https://your-api.com/premium/${userId}`
  );
  const { isPremium } = await response.json();
  await setStorage({ isPremium });
  return isPremium;
}
```

### 功能门控
```javascript
async function usePremiumFeature() {
  const { isPremium } = await getStorage(['isPremium']);
  if (!isPremium) {
    showUpgradeModal();
    return;
  }
  // 运行高级功能
}
```

### Chrome Web Store支付
- Chrome已停止内置支付功能
- 使用自己的支付系统
- 链接到外部结账页面

## 验证检查

### 使用已弃用的Manifest V2

严重程度：高

消息：使用Manifest V2 - Chrome要求V3用于新扩展。

修复操作：迁移到Manifest V3并使用服务工作者

### 请求过多权限

严重程度：高

消息：请求广泛权限 - 可能导致商店拒绝。

修复操作：使用specific_host_permissions和optional_permissions

### 扩展中没有错误处理

严重程度：中

消息：未检查chrome.runtime.lastError以获取错误。

修复操作：在API调用后检查chrome.runtime.lastError

### 扩展中硬编码URL

严重程度：中

消息：硬编码URL可能在生产环境中导致问题。

修复操作：使用chrome.storage或manifest进行配置

### 缺少扩展图标

严重程度：低

消息：缺少扩展图标 - 影响商店列表。

修复操作：添加16、48和128像素大小的图标

## 协作

### 授权触发器

- react|vue|svelte -> 前端（扩展弹窗框架）
- monetization|payment|subscription -> micro-saas-launcher（扩展商业模式）
- personal tool|just for me -> personal-tool-builder（个人扩展）
- AI|LLM|GPT -> ai-wrapper-product（AI驱动扩展）

### 生产力扩展

技能：browser-extension-builder, frontend, micro-saas-launcher

工作流程：

```
1. 定义扩展功能
2. 使用React构建弹窗UI
3. 实现内容脚本
4. 添加高级功能
5. 发布到Chrome Web Store
6. 市场营销和迭代
```

### AI浏览器助手

技能：browser-extension-builder, ai-wrapper-product, frontend

工作流程：

```
1. 设计浏览器AI功能
2. 构建扩展架构
3. 集成AI API
4. 创建弹窗界面
5. 处理使用限制/支付
6. 发布和增长
```

## 相关技能

与：`frontend`, `micro-saas-launcher`, `personal-tool-builder` 配合使用

## 使用场景
- 用户提到或暗示：浏览器扩展
- 用户提到或暗示：Chrome扩展
- 用户提到或暗示：Firefox插件
- 用户提到或暗示：扩展
- 用户提到或暗示：Manifest v3

## 限制
- 仅在任务明确匹配上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家评审的替代品。
- 如果缺少必要的输入、权限、安全边界或成功标准，请停止并请求澄清。
