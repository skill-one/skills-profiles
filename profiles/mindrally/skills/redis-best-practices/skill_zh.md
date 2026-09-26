# Redis 最佳实践

## 核心原则

- 使用 Redis 进行缓存、会话存储、实时分析和消息队列
- 根据使用场景选择合适的数据结构
- 实施正确的键命名规范和过期策略
- 设计高可用性和持久化需求
- 监控内存使用并优化性能

## 键命名规范

- 使用冒号作为命名空间分隔符
- 在键名中包含对象类型和标识符
- 保持键名简短但描述性强
- 在整个应用程序中使用一致的命名模式

```
# 良好的键命名示例
user:1234:profile
user:1234:sessions
order:5678:items
cache:api:products:list
queue:email:pending
session:abc123def456
rate_limit:api:user:1234
```

## 数据结构

### 字符串

- 用于简单的键值存储、计数器和缓存
- 考虑使用 MGET/MSET 进行批量操作

```redis
# 简单缓存
SET cache:user:1234 '{"name":"John","email":"john@example.com"}' EX 3600

# 计数器
INCR stats:pageviews:homepage
INCRBY stats:downloads:file123 5

# 原子操作
SETNX lock:resource:456 "owner:abc" EX 30
```

### 哈希

- 用于具有多个字段的对象
- 比多个字符串键更节省内存
- 支持部分更新

```redis
# 存储用户资料
HSET user:1234 name "John Doe" email "john@example.com" created_at "2024-01-15"

# 获取特定字段
HGET user:1234 email
HMGET user:1234 name email

# 增加数字字段
HINCRBY user:1234 login_count 1

# 获取所有字段
HGETALL user:1234
```

### 列表

- 用于队列、最近项和活动流
- 考虑使用阻塞操作进行队列消费者

```redis
# 消息队列
LPUSH queue:emails '{"to":"user@example.com","subject":"Welcome"}'
RPOP queue:emails

# 阻塞弹出（用于工作进程）
BRPOP queue:emails 30

# 最近活动（保留最后 100 条）
LPUSH user:1234:activity "viewed product 567"
LTRIM user:1234:activity 0 99

# 获取最近项
LRANGE user:1234:activity 0 9
```

### 集合

- 用于唯一集合、标签和关系
- 支持集合操作（并集、交集、差集）

```redis
# 用户标签/兴趣
SADD user:1234:interests "technology" "music" "travel"

# 检查成员资格
SISMEMBER user:1234:interests "music"

# 查找共同兴趣
SINTER user:1234:interests user:5678:interests

# 在线用户跟踪
SADD online:users "user:1234"
SREM online:users "user:1234"
SMEMBERS online:users
```

### 有序集合

- 用于排行榜、优先队列和时间序列数据
- 元素按分数排序

```redis
# 排行榜
ZADD leaderboard:game1 1500 "player:123" 2000 "player:456" 1800 "player:789"

# 获取前 10 名
ZREVRANGE leaderboard:game1 0 9 WITHSCORES

# 获取玩家排名
ZREVRANK leaderboard:game1 "player:123"

# 基于时间的数据（分数=时间戳）
ZADD events:user:1234 1705329600 "login" 1705330000 "purchase"

# 获取时间范围内的事件
ZRANGEBYSCORE events:user:1234 1705329600 1705333200
```

### 流

- 用于事件流和日志数据
- 支持消费者组进行分布式处理

```redis
# 添加事件到流
XADD events:orders * customer_id 1234 product_id 567 amount 99.99

# 从流中读取
XREAD COUNT 10 STREAMS events:orders 0

# 消费者组
XGROUP CREATE events:orders order-processors $ MKSTREAM
XREADGROUP GROUP order-processors worker1 COUNT 10 STREAMS events:orders >

# 确认已处理的消息
XACK events:orders order-processors 1234567890-0
```

## 缓存模式

### 边缘缓存模式

```python
# 边缘缓存伪代码
def get_user(user_id):
    # 首先尝试缓存
    cached = redis.get(f"cache:user:{user_id}")
    if cached:
        return json.loads(cached)

    # 缓存未命中 - 从数据库获取
    user = database.get_user(user_id)

    # 存入缓存并设置过期时间
    redis.setex(f"cache:user:{user_id}", 3600, json.dumps(user))

    return user
```

### 写入穿透模式

```python
def update_user(user_id, data):
    # 更新数据库
    database.update_user(user_id, data)

    # 更新缓存
    redis.setex(f"cache:user:{user_id}", 3600, json.dumps(data))
```

### 缓存失效

```redis
# 删除特定缓存
DEL cache:user:1234

# 按模式删除（生产环境中谨慎使用）
# 使用 SCAN 而不是 KEYS 处理大数据集
SCAN 0 MATCH cache:user:* COUNT 100

# 基于标签的失效使用集合
SADD cache:tags:user:1234 "cache:user:1234:profile" "cache:user:1234:orders"
# 失效所有相关缓存
SMEMBERS cache:tags:user:1234
# 然后删除每个键
```

## 过期和内存管理

### TTL 最佳实践

- 对所有缓存键设置 TTL
- 使用抖动防止雷声效应
- 考虑滑动过期用于会话数据

```redis
# 设置过期时间
SET cache:data:123 "value" EX 3600

# 对现有键设置过期时间
EXPIRE cache:data:123 3600

# 检查 TTL
TTL cache:data:123

# 持久化键（移除过期时间）
PERSIST cache:data:123
```

### 内存管理

```redis
# 检查内存使用情况
INFO memory

# 获取键的内存使用情况
MEMORY USAGE cache:large:object

# 配置最大内存策略
CONFIG SET maxmemory 2gb
CONFIG SET maxmemory-policy allkeys-lru
```

## 事务和原子性

### MULTI/EXEC 事务

```redis
# 事务块
MULTI
INCR stats:views
LPUSH recent:views "page:123"
EXEC

# 乐观锁监视
WATCH user:1234:balance
balance = GET user:1234:balance
MULTI
SET user:1234:balance (balance - 100)
EXEC
```

### Lua 脚本

- 用于复杂的原子操作
- 脚本执行原子性

```lua
-- 速率限制脚本
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])

local current = tonumber(redis.call('GET', key) or '0')

if current >= limit then
    return 0
end

redis.call('INCR', key)
if current == 0 then
    redis.call('EXPIRE', key, window)
end

return 1
```

```redis
# 执行 Lua 脚本
EVAL "return redis.call('GET', KEYS[1])" 1 mykey
```

## 发布/订阅和消息传递

```redis
# 发布者
PUBLISH channel:notifications '{"type":"alert","message":"New order"}'

# 订阅者
SUBSCRIBE channel:notifications

# 模式订阅
PSUBSCRIBE channel:*
```

## 高可用性

### 复制

- 使用副本进行读扩展
- 在主节点上配置适当的持久化

```redis
# 在副本上
REPLICAOF master_host 6379

# 检查复制状态
INFO replication
```

### Redis Sentinel

- 用于自动故障转移
- 至少部署 3 个 Sentinel 实例

### Redis 集群

- 用于水平扩展
- 数据自动跨节点分片
- 使用哈希标签确保相关键到同一槽

```redis
# 哈希标签确保键到同一槽
SET {user:1234}:profile "data"
SET {user:1234}:settings "data"
```

## 持久化

### RDB 快照

```redis
# 手动快照
BGSAVE

# 配置自动快照
CONFIG SET save "900 1 300 10 60 10000"
```

### AOF（追加只读文件）

```redis
# 启用 AOF
CONFIG SET appendonly yes
CONFIG SET appendfsync everysec

# 重写 AOF
BGREWRITEAOF
```

## 安全

- 需要身份验证
- 使用 TLS 进行连接
- 绑定到特定接口
- 禁用危险命令

```redis
# 设置密码
CONFIG SET requirepass "your_strong_password"

# 身份验证
AUTH your_strong_password

# 重命名危险命令（在 redis.conf 中）
rename-command FLUSHALL ""
rename-command FLUSHDB ""
rename-command KEYS ""
```

## 监控

```redis
# 服务器信息
INFO

# 内存统计
INFO memory

# 客户端连接
CLIENT LIST

# 慢日志
SLOWLOG GET 10

# 监控命令（仅调试时使用）
MONITOR

# 每个数据库的键计数
INFO keyspace
```

## 连接管理

- 使用连接池
- 设置适当的超时
- 优雅地处理重连

```python
# 带连接池的 Python 示例
import redis

pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=50,
    socket_timeout=5,
    socket_connect_timeout=5
)

redis_client = redis.Redis(connection_pool=pool)
```

## 性能技巧

- 使用管道化进行批量操作
- 避免大键（值>100KB）
- 在生产中使用 SCAN 而不是 KEYS
- 监控和优化内存使用
- 考虑使用 RedisJSON 进行复杂的 JSON 操作

```redis
# 管道化示例（伪代码）
pipe = redis.pipeline()
pipe.get("key1")
pipe.get("key2")
pipe.set("key3", "value")
results = pipe.execute()
```
