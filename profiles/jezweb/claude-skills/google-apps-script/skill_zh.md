# Google Apps Script

为 Google Sheets 和 Workspace 应用程序构建自动化脚本。脚本在 Google 的基础设施上以服务器端运行，并提供慷慨的免费套餐。

## 您将产出

- 粘贴到扩展 > Apps Script 中的 Apps Script 代码
- 自定义菜单、对话框、侧边栏
- 自动化触发器（编辑时、定时、表单提交）
- 电子邮件通知、PDF 导出、API 集成

## 工作流程

### 第 1 步：理解自动化需求

询问用户希望自动化什么。常见场景：
- 带有操作的自定义菜单（报告生成、数据处理）
- 自动触发的行为（编辑时、表单提交、计划任务）
- 用于数据输入的侧边栏应用程序
- 来自表格数据的电子邮件通知
- PDF 导出和分发

### 第 2 步：生成脚本

遵循以下结构模板。每个脚本需要一个头部注释、配置常量在顶部，以及 `onOpen()` 用于菜单设置。

### 第 3 步：提供安装说明

所有脚本都以相同的方式安装：
1. 打开 Google 表格
2. **扩展 > Apps Script**
3. 删除编辑器中的任何现有代码
4. 粘贴脚本
5. 点击 **保存**
6. 关闭 Apps Script 标签页
7. **重新加载工作表**（onOpen 在页面加载时运行）

### 第 4 步：首次授权

每个用户在首次运行时都会获得一个 Google OAuth 同意屏幕。对于未验证的脚本（大多数内部脚本），用户必须点击：

**高级 > 前往 [项目名称]（不安全）> 允许**

这是一个每个用户的单次步骤。在您的输出中提醒用户此步骤。

---

## 脚本结构模板

每个脚本应遵循此模式：

```javascript
/**
 * [项目名称] - [简要描述]
 *
 * [它做什么，关键特性]
 *
 * 安装：扩展 > Apps Script > 粘贴此内容 > 保存 > 重新加载工作表
 */

// --- 配置 ---
const SOME_SETTING = 'value';

// --- 菜单设置 ---
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('我的菜单')
    .addItem('执行操作', 'myFunction')
    .addSeparator()
    .addSubMenu(ui.createMenu('更多选项')
      .addItem('选项 A', 'optionA'))
    .addToUi();
}

// --- 函数 ---
function myFunction() {
  // 实现
}
```

---

## 严格规则

### 公共与私有函数

以 `_`（下划线）结尾的函数是**私有**的，并且**不能**通过 `google.script.run` 从客户端 HTML 调用。这是一个静默失败——调用只是不起作用，没有任何错误。

```javascript
// 错误 - 对话框无法调用此函数，会静默失败
function doWork_() { return 'done'; }

// 正确 - 对话框可以调用此函数
function doWork() { return 'done'; }
```

**也适用于**：菜单项函数引用必须是公共函数名称作为字符串。

### 批量操作（对性能至关重要）

成批读取/写入数据，而不是逐个单元格。差异是 70 倍。

```javascript
// 慢（100x100 需要 70 秒）- 逐个单元格读取
for (let i = 1; i <= 100; i++) {
  const val = sheet.getRange(i, 1).getValue();
}

// 快（1 秒）- 一次性读取所有数据
const allData = sheet.getRange(1, 1, 100, 1).getValues();
for (const row of allData) {
  const val = row[0];
}
```

始终使用 `getRange().getValues()` / `setValues()` 进行批量读取/写入。

### V8 运行时

V8 是**唯一**的运行时（Rhino 已于 2026 年 1 月移除）。支持现代 JavaScript：`const`、`let`、箭头函数、模板字符串、解构、类、异步/生成器。

**不可用**（使用 Apps Script 替代方案）：

| 缺失 API | Apps Script 替代方案 |
|---------|----------------------|
| `setTimeout` / `setInterval` | `Utilities.sleep(ms)`（阻塞） |
| `fetch` | `UrlFetchApp.fetch()` |
| `FormData` | 手动构建有效负载 |
| `URL` | 字符串操作 |
| `crypto` | `Utilities.computeDigest()` / `Utilities.getUuid()` |

### 返回前刷新

在从修改工作表的函数返回之前调用 `SpreadsheetApp.flush()`，尤其是在从 HTML 对话框调用时。如果没有它，当对话框显示“完成”时，更改可能不会可见。

### 简单与可安装触发器

| 功能 | 简单 (`onEdit`) | 可安装 |
|------|----------------|--------|
| 需要授权 | 否 | 是 |
| 发送电子邮件 | 否 | 是 |
| 访问其他文件 | 否 | 是 |
| URL 获取 | 否 | 是 |
| 打开对话框 | 否 | 是 |
| 运行作为 | 活跃用户 | 触发器创建者 |

使用简单触发器进行轻量级反应。当您需要电子邮件、外部 API 或跨文件访问时，使用可安装触发器（通过 `ScriptApp.newTrigger()`）。

### 自定义电子表格函数

在单元格中用作 `=MY_FUNCTION()` 的函数有严格的限制：

```javascript
/**
 * 执行自定义计算。
 * @param {string} input 输入值
 * @return {string} 结果
 * @customfunction
 */
function MY_FUNCTION(input) {
  // 可以使用：基本 JS、Utilities、CacheService
  // 不能使用：MailApp、UrlFetchApp、SpreadsheetApp.getUi()、触发器
  return input.toUpperCase();
}
```

- 必须包含 `@customfunction` JSDoc 标签
- 30 秒执行限制（常规函数为 6 分钟）
- 不能访问需要授权的服务

---

## 配额和限制

| 资源 | 免费账户 | Google Workspace |
|------|----------|-----------------|
| 脚本运行时 | 6 分钟/执行 | 6 分钟/执行 |
| 定时触发器运行时 | 30 分钟 | 30 分钟 |
| 每日触发器总运行时 | 90 分钟 | 6 小时 |
| 触发器总数 | 每个用户每个脚本 20 个 | 每个用户每个脚本 20 个 |
| 每日电子邮件接收者 | 100 个 | 1,500 个 |
| 每日 URL Fetch 调用 | 20,000 个 | 100,000 个 |
| 属性存储 | 500 KB | 500 KB |
| 自定义函数运行时 | 30 秒 | 30 秒 |
| 并发执行 | 30 个 | 30 个 |

---

## 模态进度对话框

在长时间操作期间阻塞用户交互，使用自动关闭的旋转器。用于任何超过几秒钟的操作。

**模式：菜单函数 > showProgress() > 对话框调用动作函数 > 自动关闭**

```javascript
function showProgress(message, serverFn) {
  const html = HtmlService.createHtmlOutput(`
    <style>
      body { font-family: 'Google Sans', Arial, sans-serif; display: flex;
        flex-direction: column; align-items: center; justify-content: center;
        height: 100%; margin: 0; padding: 20px; box-sizing: border-box; }
      .spinner { width: 36px; height: 36px; border: 4px solid #e0e0e0;
        border-top: 4px solid #1a73e8; border-radius: 50%;
        animation: spin 0.8s linear infinite; margin-bottom: 16px; }
      @keyframes spin { to { transform: rotate(360deg); } }
      .message { font-size: 14px; color: #333; text-align: center; }
      .done { color: #1e8e3e; font-weight: 500; }
      .error { color: #d93025; font-weight: 500; }
    </style>
    <div class="spinner" id="spinner"></div>
    <div class="message" id="msg">${message}</div>
    <script>
      google.script.run
        .withSuccessHandler(function(r) {
          document.getElementById('spinner').style.display = 'none';
          var m = document.getElementById('msg');
          m.className = 'message done';
          m.innerText = 'Done! ' + (r || '');
          setTimeout(function() { google.script.host.close(); }, 1200);
        })
        .withFailureHandler(function(err) {
          document.getElementById('spinner').style.display = 'none';
          var m = document.getElementById('msg');
          m.className = 'message error';
          m.innerText = 'Error: ' + err.message;
          setTimeout(function() { google.script.host.close(); }, 3000);
        })
        .${serverFn}();
    </script>
  `).setWidth(320).setHeight(140);
  SpreadsheetApp.getUi().showModalDialog(html, '正在处理...');
}

// 菜单调用此包装器
function menuDoWork() {
  showProgress('正在处理数据...', 'doTheWork');
}

// 必须是公共的（没有下划线），以便对话框可以调用它
function doTheWork() {
  // ... 执行操作 ...
  SpreadsheetApp.flush();
  return '处理了 50 行';  // 显示在成功消息中
}
```

---

## 常见模式

### Toast 通知

```javascript
SpreadsheetApp.getActiveSpreadsheet().toast('操作完成！', '标题', 5);
// 参数：消息、标题、秒数（-1 = 直到关闭）
```

### 警报和提示对话框

```javascript
const ui = SpreadsheetApp.getUi();

// 是/否确认
const response = ui.alert('删除此数据？', '此操作无法撤销。',
  ui.ButtonSet.YES_NO);
if (response === ui.Button.YES) { /* 继续 */ }

// 提示输入
const result = ui.prompt('输入您的姓名：', ui.ButtonSet.OK_CANCEL);
if (result.getSelectedButton() === ui.Button.OK) {
  const name = result.getResponseText();
}
```

### 侧边栏应用程序

右侧的 HTML 面板。使用 `google.script.run` 调用服务器端函数。

```javascript
function showSidebar() {
  const html = HtmlService.createHtmlOutput(`
    <h3>快速输入</h3>
    <select id="worker"><option>Craig</option><option>Steve</option></select>
    <input id="suburb" placeholder="区域">
    <button onclick="submit()">添加工作</button>
    <script>
      function submit() {
        google.script.run.withSuccessHandler(function() { alert('添加成功！'); })
          .addJob(document.getElementById('worker').value,
                  document.getElementById('suburb').value);
      }
    </script>
  `).setTitle('工作输入').setWidth(300);
  SpreadsheetApp.getUi().showSidebar(html);
}

function addJob(worker, suburb) { // 必须是公共的（没有下划线）
  SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().appendRow([new Date(), worker, suburb]);
}
```

### 触发器

**onEdit（简单触发器）**——权限有限但无需授权：

```javascript
function onEdit(e) {
  const sheet = e.source.getActiveSheet();
  if (sheet.getName() !== '数据') return;
  if (e.range.getColumn() !== 3) return;
  // 当编辑列 C 时自动时间戳
  sheet.getRange(e.range.getRow(), 4).setValue(new Date());
}
```

**可安装触发器**——通过脚本创建，手动运行一次设置函数：

```javascript
function createTriggers() {
  // 定时：每天早上 8 点运行
  ScriptApp.newTrigger('dailyReport')
    .timeBased().atHour(8).everyDays(1).create();

  // 编辑时，具有完整权限（可以发送电子邮件、获取 URL）
  ScriptApp.newTrigger('onEditFull')
    .forSpreadsheet(SpreadsheetApp.getActive()).onEdit().create();

  // 表单提交时
  ScriptApp.newTrigger('onFormSubmit')
    .forSpreadsheet(SpreadsheetApp.getActive()).onFormSubmit().create();
}
```

### 从表格发送电子邮件

```javascript
function emailWeeklySchedule() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const data = sheet.getRange('A2:E10').getDisplayValues();
  let body = '<h2>每周计划</h2><table border="1" cellpadding="8">';
  body += '<tr><th>工作</th><th>区域</th><th>时间</th><th>价格</th></tr>';
  for (const row of data) {
    if (row[0]) body += '<tr>' + row.map(c => '<td>' + c + '</td>').join('') + '</tr>';
  }
  body += '</table>';
  MailApp.sendEmail({ to: 'worker@example.com',
    subject: '计划 - ' + sheet.getName(), htmlBody: body });
}
```

### PDF 导出

非明显的 URL 构造——导出参数未公开：

```javascript
function exportSheetAsPdf() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const url = ss.getUrl().replace(/\/edit.*$/, '')
    + '/export?exportFormat=pdf&format=pdf&size=A4&portrait=true'
    + '&fitw=true&sheetnames=false&printtitle=false&gridlines=false'
    + '&gid=' + ss.getActiveSheet().getSheetId();
  const blob = UrlFetchApp.fetch(url, {
    headers: { 'Authorization': 'Bearer ' + ScriptApp.getOAuthToken() }
  }).getBlob().setName('报告.pdf');
  MailApp.sendEmail({ to: 'boss@example.com', subject: '每周报告 PDF',
    body: '附件。', attachments: [blob] });
}
```

### 外部 API 调用

```javascript
// GET
function fetchData() {
  const r = UrlFetchApp.fetch('https://api.example.com/data', {
    headers: { 'Authorization': 'Bearer ' + getApiKey() } });
  return JSON.parse(r.getContentText());
}

// POST (muteHttpExceptions 以自行处理错误)
function postData(payload) {
  const r = UrlFetchApp.fetch('https://api.example.com/submit', {
    method: 'post', contentType: 'application/json',
    payload: JSON.stringify(payload), muteHttpExceptions: true });
  if (r.getResponseCode() !== 200) throw new Error('API 错误：' + r.getContentText());
  return JSON.parse(r.getContentText());
}
```

### 数据验证下拉列表

```javascript
// 从列表创建下拉列表
const rule = SpreadsheetApp.newDataValidation()
  .requireValueInList(['选项 A', '选项 B', '选项 C'], true)
  .setAllowInvalid(false).setHelpText('选择一个选项').build();
sheet.getRange('C3:C50').setDataValidation(rule);

// 从范围创建下拉列表（例如，查找表）
const rule2 = SpreadsheetApp.newDataValidation()
  .requireValueInRange(ss.getSheetByName('Lookups').getRange('A1:A100')).build();
sheet.getRange('B3:B50').setDataValidation(rule2);
```

### 属性服务（持久存储）

三个范围：`PropertiesService.getScriptProperties()`（共享）、`.getUserProperties()`（每个用户）、`.getDocumentProperties()`（每个电子表格）。所有使用 `.setProperty(key, value)` / `.getProperty(key)`。500 KB 限制。

---

## 烹饪方法

### 自动存档已完成行

将带有“完成”状态的行移动到存档工作表。从下往上处理以避免行索引移动。

```javascript
function archiveCompleted() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const source = ss.getSheetByName('活跃');
  const archive = ss.getSheetByName('存档');
  const data = source.getDataRange().getValues();
  const statusCol = 4; // 列 E（0 索引）

  for (let i = data.length - 1; i >= 1; i--) {
    if (data[i][statusCol] === '完成') {
      archive.appendRow(data[i]);
      source.deleteRow(i + 1); // +1 对于 1 索引的行
    }
  }
  SpreadsheetApp.flush();
}
```

### 重复检测和突出显示

模式：使用 `getValues()` 读取列，在对象中跟踪已看到的值，使用 `setBackground('#f4cccc')` 突出显示原始行和重复行。在一个 `getValues()` 调用中处理所有数据，然后单独设置背景（对于分散的突出显示不可避免）。

### 批量电子邮件发送者

关键模式：在发送前检查 `MailApp.getRemainingDailyQuota()`，每行标记状态，将每个发送包装在 try/catch 中。

```javascript
function sendBatchEmails() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('接收者');
  const data = sheet.getRange('A2:C' + sheet.getLastRow()).getValues(); // 邮件、姓名、状态
  const remaining = MailApp.getRemainingDailyQuota();
  if (remaining < data.length) {
    SpreadsheetApp.getUi().alert('只剩下 ' + remaining + ' 个电子邮件。需要 ' + data.length);
    return;
  }
  let sent = 0;
  for (let i = 0; i < data.length; i++) {
    const [email, name, status] = data[i];
    if (!email || status === 'Sent') continue;
    try {
      MailApp.sendEmail({ to: email, subject: '您的每周更新',
        htmlBody: '<p>嗨 ' + name + '，</p><p>这是您的更新...</p>' });
      sheet.getRange(i + 2, 3).setValue('Sent'); sent++;
    } catch (e) { sheet.getRange(i + 2, 3).setValue('Error: ' + e.message); }
  }
  SpreadsheetApp.flush();
}
```

### 汇总仪表板生成器

模式：循环编号的每周标签（`01`-`52`），从每个标签读取汇总单元格，将聚合行写入汇总工作表。使用 `ss.getSheetByName(tabName)` 迭代，`ss.insertSheet('Summary')` 如果不存在，`summary.autoResizeColumns()` 在末尾，`flush()` 在返回前。

---

## 错误处理

始终将外部调用包装在 try/catch 中。使用 `muteHttpExceptions: true` 以自行处理 HTTP 错误。重新抛出以供对话框错误处理程序使用。

```javascript
function fetchExternalData() {
  try {
    const response = UrlFetchApp.fetch('https://api.example.com/data', {
      headers: { 'Authorization': 'Bearer ' + getApiKey() },
      muteHttpExceptions: true
    });
    if (response.getResponseCode() !== 200)
      throw new Error('API 返回 ' + response.getResponseCode());
    return JSON.parse(response.getContentText());
  } catch (e) { Logger.log('错误：' + e.message); throw e; }
}
```

---

## 预防错误

| 错误 | 修复 |
|------|------|
| 对话框无法调用函数 | 从函数名称中删除尾随 `_` |
| 脚本在大量数据上运行缓慢 | 使用 `getValues()`/`setValues()` 批量操作 |
| 对话框后更改不可见 | 在返回前添加 `SpreadsheetApp.flush()` |
| `onEdit` 无法发送电子邮件 | 使用通过 `ScriptApp.newTrigger()` 创建的可安装触发器 |
| 自定义函数超时 | 30 秒限制——简化或移动到常规函数 |
| `setTimeout` 未找到 | 使用 `Utilities.sleep(ms)`（阻塞） |
| 脚本超过 6 分钟 | 分成块，使用定时触发器进行批量处理 |
| 授权弹出窗口未出现 | 用户必须点击高级 > 前往（不安全）> 允许 |

## 调试

- **Logger.log()** / **console.log()** -- 在 Apps Script 编辑器的“执行日志”中查看
- **手动运行** -- 在编辑器下拉列表中选择函数 > 运行
- **执行标签页** -- 显示所有最近的运行，包括错误和堆栈跟踪
- **触发器失败** -- script.google.com > 我的项目 > 执行
- **始终在部署前**在表格的副本上测试

## 部署清单

- [ ] 从 HTML 对话框调用的所有函数都是公共的（没有尾随下划线）
- [ ] 修改函数返回前调用 `SpreadsheetApp.flush()`
- [ ] 在外部 API 调用和 MailApp 周围进行错误处理（try/catch）
- [ ] 文件顶部配置常量
- [ ] 带有安装说明的头部注释
- [ ] 在表格副本上测试
- [ ] 考虑多用户行为（不同的权限，不同的活动工作表）
- [ ] 长操作使用模态进度对话框
- [ ] 不要硬编码工作表名称——使用配置常量
- [ ] 在批量发送前检查电子邮件配额

---

## 如果需要，从 Apps Script 文档中重建

- **行/列显示/隐藏** — `sheet.hideRows()`, `showRows()`, `isRowHiddenByUser()`
- **格式化** — `setBackground()`, `setFontWeight()`, `setBorder()`, `setNumberFormat()`, 条件格式化
- **数据保护** — `range.protect()`, `setUnprotectedRanges()`, 编辑器管理
- **多个工作表** — `getSheetByName()`, 循环编号的标签，`copyTo()`, `insertSheet()`
- **自动编号行** — `onEdit` 触发器在编辑列 B 时自动编号列 A
- **Google Chat webhooks** — 向 `chat.googleapis.com` 发送 JSON 有效负载
