# 浏览器自动化

自动化网页浏览器交互，用于数据抓取、测试和工作流自动化。

## 核心功能

### 导航
```yaml
navigation:
  goto:
    url: "https://example.com"
    wait_until: "networkidle"
    timeout: 30000
    
  actions:
    - wait_for_selector: ".content"
    - scroll_to_bottom: true
    - wait_for_navigation: true
```

### 元素交互
```yaml
interactions:
  click:
    selector: "button.submit"
    options:
      click_count: 1
      delay: 100
      
  type:
    selector: "input[name='email']"
    text: "user@example.com"
    options:
      delay: 50  # 模拟人类输入
      
  select:
    selector: "select#country"
    value: "US"
    
  file_upload:
    selector: "input[type='file']"
    files: ["document.pdf"]
```

### 数据提取
```yaml
scraping:
  extract_text:
    selector: ".article-content"
    
  extract_all:
    selector: ".product-card"
    fields:
      name: ".product-name"
      price: ".price"
      url:
        selector: "a"
        attribute: "href"
        
  extract_table:
    selector: "table.data"
    output: json
```

### 截图 & PDF
```yaml
capture:
  screenshot:
    path: "screenshot.png"
    full_page: true
    type: "png"
    
  pdf:
    path: "page.pdf"
    format: "A4"
    print_background: true
```

## 工作流示例

### 表单自动化
```javascript
// 登录并填写表单
await page.goto('https://app.example.com/login');
await page.fill('#email', 'user@example.com');
await page.fill('#password', 'securepass');
await page.click('button[type="submit"]');
await page.waitForNavigation();

// 导航到表单
await page.click('a[href="/new-entry"]');
await page.fill('#title', '自动化录入');
await page.fill('#description', '通过自动化创建');
await page.click('button.submit');
```

### 网页抓取
```yaml
scraping_workflow:
  - navigate: "https://news.example.com"
  - wait: ".article-list"
  - extract_all:
      selector: ".article"
      fields:
        title: "h2"
        summary: ".excerpt"
        link:
          selector: "a"
          attribute: "href"
  - paginate:
      next_button: ".pagination .next"
      max_pages: 10
  - output: "articles.json"
```

### E2E 测试
```yaml
test_workflow:
  - name: "用户注册"
    steps:
      - goto: "/register"
      - fill:
          "#email": "test@example.com"
          "#password": "Test123!"
      - click: "button[type='submit']"
      - assert:
          selector: ".success-message"
          text_contains: "Welcome"
```

## 最佳实践

1. **等待策略**：使用适当的等待
2. **错误处理**：捕获导航失败
3. **速率限制**：尊重服务器
4. **无头模式**：用于生产环境
5. **选择器**：优先使用 data-testid 属性
6. **截图**：在失败时捕获
