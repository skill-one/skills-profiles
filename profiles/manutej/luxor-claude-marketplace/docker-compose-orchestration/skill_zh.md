# Docker Compose 编排

使用 Docker Compose 对多容器应用程序进行编排的全面技能。此技能可快速开发、部署和管理容器化应用程序，包括服务定义、网络策略、卷管理、健康检查和生产就绪的配置。

## 何时使用此技能

- 构建多容器应用程序（微服务、全栈应用程序）
- 设置包含数据库、缓存和服务的开发环境
- 将前端、后端和数据库服务组合在一起
- 管理服务依赖关系和启动顺序
- 配置网络和服务间通信
- 使用卷实现持久存储
- 部署应用程序到开发、测试或生产环境
- 创建可重复的开发环境
- 管理应用程序生命周期（启动、停止、重新构建、扩展）
- 监控应用程序健康状态并实施健康检查
- 从单个容器迁移到多服务架构
- 本地测试分布式系统

## 核心概念

### Docker Compose 哲学

Docker Compose 通过以下方式简化多容器应用程序管理：

- **声明式配置**：使用 YAML 定义整个应用程序堆栈
- **服务抽象**：每个组件都是一个具有其自身配置的服务
- **自动网络**：服务可以通过名称自动通信
- **卷管理**：跨容器的持久数据和共享存储
- **环境隔离**：每个项目拥有自己的网络命名空间
- **可重复性**：相同的配置在所有环境中都有效

### Docker Compose 关键实体

1. **服务**：单个容器及其配置
2. **网络**：服务之间的通信通道
3. **卷**：持久存储和数据共享
4. **配置**：非敏感的配置文件
5. **密钥**：敏感数据（密码、API 密钥）
6. **项目**：单个命名空间下的服务集合

### Compose 文件结构

```yaml
version: "3.8"  # Compose 文件格式版本

services:       # 定义容器
  service-name:
    # 服务配置

networks:       # 定义自定义网络
  network-name:
    # 网络配置

volumes:        # 定义命名卷
  volume-name:
    # 卷配置

configs:        # 应用程序配置（可选）
  config-name:
    # 配置源

secrets:        # 敏感数据（可选）
  secret-name:
    # 密钥源
```

## 服务定义模式

### 基本服务定义

```yaml
services:
  web:
    image: nginx:alpine           # 使用现有镜像
    container_name: my-web        # 自定义容器名称
    restart: unless-stopped       # 重启策略
    ports:
      - "80:80"                   # 主机:容器端口映射
    environment:
      - ENV_VAR=value             # 环境变量
    volumes:
      - ./html:/usr/share/nginx/html  # 卷挂载
    networks:
      - frontend                  # 连接到网络
```

### 基于构建的服务

```yaml
services:
  app:
    build:
      context: ./app              # 构建上下文目录
      dockerfile: Dockerfile      # 自定义 Dockerfile
      args:                       # 构建参数
        NODE_ENV: development
      target: development         # 多阶段构建目标
    image: myapp:latest           # 结果镜像的标签
    ports:
      - "3000:3000"
```

### 具有依赖关系的服务

```yaml
services:
  web:
    image: nginx
    depends_on:
      db:
        condition: service_healthy  # 等待健康检查
      redis:
        condition: service_started  # 仅等待启动

  db:
    image: postgres:15
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  redis:
    image: redis:alpine
```

### 具有高级配置的服务

```yaml
services:
  backend:
    build: ./backend
    command: npm run dev          # 覆盖默认命令
    working_dir: /app             # 设置工作目录
    user: "1000:1000"             # 以特定用户运行
    hostname: api-server          # 自定义主机名
    domainname: example.com       # 域名
    env_file:
      - .env                      # 从文件加载环境变量
      - .env.local
    environment:
      DATABASE_URL: "postgresql://db:5432/myapp"
      REDIS_URL: "redis://cache:6379"
    volumes:
      - ./backend:/app            # 源代码挂载
      - /app/node_modules         # 保留 node_modules
      - app-data:/data            # 命名卷
    ports:
      - "3000:3000"               # 应用程序端口
      - "9229:9229"               # 调试端口
    expose:
      - "8080"                    # 仅暴露给其他服务
    networks:
      - backend
      - frontend
    labels:
      - "com.example.description=Backend API"
      - "com.example.version=1.0"
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## 多容器应用程序模式

### 模式 1：全栈 Web 应用程序

**场景**：React 前端 + Node.js 后端 + PostgreSQL 数据库

```yaml
version: "3.8"

services:
  # React 前端应用程序
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: development
    ports:
      - "3000:3000"
    volumes:
      - ./frontend/src:/app/src
      - /app/node_modules
    environment:
      - REACT_APP_API_URL=http://localhost:4000/api
      - CHOKIDAR_USEPOLLING=true  # 用于热重载
    networks:
      - frontend
    depends_on:
      - backend

  # Node.js API 后端
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "4000:4000"
      - "9229:9229"  # 调试端口
    volumes:
      - ./backend:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://postgres:password@db:5432/myapp
      - REDIS_URL=redis://cache:6379
      - JWT_SECRET=dev-secret
    env_file:
      - ./backend/.env.local
    networks:
      - frontend
      - backend
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    command: npm run dev

  # PostgreSQL 数据库
  db:
    image: postgres:15-alpine
    container_name: postgres-db
    restart: unless-stopped
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=myapp
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis 缓存
  cache:
    image: redis:7-alpine
    container_name: redis-cache
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - backend
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge

volumes:
  postgres-data:
  redis-data:
```

### 模式 2：微服务架构

**场景**：多个服务、反向代理和服务发现

```yaml
version: "3.8"

services:
  # NGINX 反向代理
  proxy:
    image: nginx:alpine
    container_name: reverse-proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    networks:
      - public
    depends_on:
      - auth-service
      - user-service
      - order-service
    restart: unless-stopped

  # 身份验证服务
  auth-service:
    build: ./services/auth
    container_name: auth-service
    expose:
      - "8001"
    environment:
      - SERVICE_NAME=auth
      - DATABASE_URL=postgresql://db:5432/auth_db
      - JWT_SECRET=${JWT_SECRET}
    networks:
      - public
      - internal
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 用户服务
  user-service:
    build: ./services/user
    expose:
      - "8002"
    environment:
      - SERVICE_NAME=user
      - DATABASE_URL=postgresql://db:5432/user_db
      - AUTH_SERVICE_URL=http://auth-service:8001
    networks:
      - public
      - internal
    depends_on:
      - auth-service
      - db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 订单服务
  order-service:
    build: ./services/order
    expose:
      - "8003"
    environment:
      - SERVICE_NAME=order
      - DATABASE_URL=postgresql://db:5432/order_db
      - USER_SERVICE_URL=http://user-service:8002
      - RABBITMQ_URL=amqp://rabbitmq:5672
    networks:
      - public
      - internal
    depends_on:
      - user-service
      - db
      - rabbitmq
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 共享 PostgreSQL 数据库
  db:
    image: postgres:15-alpine
    environment:
      MYSQL_ROOT_PASSWORD: secret
      MYSQL_DATABASE: myapp
      MYSQL_USER: user
      MYSQL_PASSWORD: password
    volumes:
      - postgres-data:/var/lib/mysql
    networks:
      - internal
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 3

  mysql:
    image: mysql:8
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 3

  mongodb:
    image: mongo:6
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  zookeeper-data:
  zookeeper-logs:
  kafka-data:
```

### 模式 2：开发环境与热重载

**场景**：具有实时代码重载和调试的开发设置

```yaml
version: "3.8"

services:
  # 开发前端
  frontend-dev:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
      - "9222:9222"  # Chrome DevTools
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next  # Next.js 构建缓存
    environment:
      - NODE_ENV=development
      WATCHPACK_POLLING=true
      NEXT_PUBLIC_API_URL=http://localhost/api
    networks:
      - dev-network
    stdin_open: true
    tty: true
    command: npm run dev

  # 开发后端
  backend-dev:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "4000:4000"
      - "9229:9229"  # Node.js 调试端口
    volumes:
      - ./backend:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
      DEBUG=*
      DATABASE_URL=postgresql://postgres:dev@db:5432/dev_db
    depends_on:
      - db
      - mailhog
    command: npm run dev:debug

  # PostgreSQL 数据库
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD=dev
      POSTGRES_DB=dev_db
    ports:
      - "5432:5432"
    volumes:
      - dev-db-data:/var/lib/postgresql/data
    networks:
      - dev-network

  pgadmin:
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL=admin@dev.local
      PGADMIN_DEFAULT_PASSWORD=admin
    ports:
      - "5050:80"
    networks:
      - dev-network
    depends_on:
      - db

  # 邮件测试的 MailHog
  mailhog:
    image: mailhog/mailhog:latest
    ports:
      - "1025:1025"  # SMTP
      - "8025:8025"  # Web UI
    networks:
      - dev-network

networks:
  dev-network:
    driver: bridge

volumes:
  dev-db-data:
```

## 网络策略

### 默认桥接网络

```yaml
services:
  web:
    image: nginx
    # 自动连接到默认网络

  app:
    image: myapp
    # 可以通过服务名称与 'web' 通信
```

### 自定义桥接网络

```yaml
version: "3.8"

services:
  frontend:
    image: react-app
    networks:
      - public

  backend:
    image: api-server
    networks:
      - public    # 可从前端访问
      - private   # 可被数据库访问

  database:
    image: postgres
    networks:
      - private   # 与前端隔离

networks:
  public:
    driver: bridge
  private:
    driver: bridge
    internal: true  # 无外部访问

### 网络别名

```yaml
services:
  api:
    image: api-server
    networks:
      backend:
        aliases:
          - api-server
          - api.internal
          - api-v1.internal

networks:
  backend:
    driver: bridge
```

### 主机网络模式

```yaml
services:
  app:
    image: myapp
    network_mode: "host"  # 使用主机网络栈
    # 无需端口映射，直接使用主机端口
```

### 自定义网络配置

```yaml
networks:
  custom-network:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.name: br-custom
    ipam:
      driver: default
      config:
        - subnet: 172.28.0.0/16
          gateway: 172.28.0.1
    labels:
      - "com.example.description=Custom network"
```

## 卷管理

### 命名卷

```yaml
version: "3.8"

services:
  db:
    image: postgres:15
    volumes:
      - postgres-data:/var/lib/postgresql/data  # 命名卷

  backup:
    image: postgres:15
    volumes:
      - postgres-data:/backup:ro  # 只读挂载
    command: pg_dump -U postgres > /backup/dump.sql

volumes:
  postgres-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /path/on/host
```

### 绑定挂载

```yaml
services:
  web:
    image: nginx
    volumes:
      # 相对路径绑定挂载
      - ./html:/usr/share/nginx/html

      # 绝对路径绑定挂载
      - /var/log/nginx:/var/log/nginx

      # 只读绑定挂载
      - ./config/nginx.conf:/etc/nginx/nginx.conf:ro
```

### tmpfs 挂载（内存中）

```yaml
services:
  app:
    image: myapp
    tmpfs:
      - /tmp
      - /run
    # 或使用选项:
    volumes:
      - type: tmpfs
      target: /app/cache
      tmpfs:
        size: 1000000000  # 1GB
```

### 服务间卷共享

```yaml
services:
  app:
    image: myapp
    volumes:
      - shared-data:/data

  worker:
    image: worker
    volumes:
      - shared-data:/data

  backup:
    image: backup-tool
    volumes:
      - shared-data:/backup:ro

volumes:
  shared-data:
```

### 高级卷配置

```yaml
volumes:
  data:
    driver: local
    driver_opts:
      type: "nfs"
      o: "addr=10.40.0.199,nolock,soft,rw"
      device: ":/docker/example"

  cache:
    driver: local
    driver_opts:
      type: tmpfs
      device: tmpfs
      o: "size=100m,uid=1000"

  external-volume:
    external: true  # 卷在外部创建
    name: my-existing-volume
```

## 健康检查

### HTTP 健康检查

```yaml
services:
  web:
    image: nginx
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 数据库健康检查

```yaml
services:
  postgres:
    image: postgres:15
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  mysql:
    image: mysql:8
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 3

  mongodb:
    image: mongo:6
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### 应用程序健康检查

```yaml
services:
  app:
    build: ./app
    healthcheck:
      test: ["CMD", "node", "healthcheck.js"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  api:
    build: ./api
    healthcheck:
      test: ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1"
      interval: 30s
      timeout: 10s
      retries: 3
```

### 复杂健康检查

```yaml
services:
  redis:
    image: redis:alpine
    healthcheck:
      test: |
        sh -c '
        redis-cli ping | grep PONG &&
        redis-cli --raw incr ping | grep 1
        '
      interval: 10s
      timeout: 3s
      retries: 5
```

## 开发与生产配置

### 基本配置（compose.yaml）

```yaml
version: "3.8"

services:
  web:
    image: myapp:latest
    environment:
      NODE_ENV=production
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

### 开发覆盖（compose.override.yaml）

```yaml
# 自动合并到 compose.yaml 中开发
version: "3.8"

services:
  web:
    build:
      context: .
      target: development
    volumes:
      - ./src:/app/src  # 实时代码重载
      - /app/node_modules
    ports:
      - "3000:3000"     # 本地访问
      - "9229:9229"     # 调试端口
    environment:
      NODE_ENV=development
      DEBUG=*
      DATABASE_URL=postgresql://postgres:dev@db:5432/myapp
      REDIS_URL=redis://cache:6379
    volumes:
      - ./init-dev.sql:/docker-entrypoint-initdb.d/init.sql
```

### 生产配置（compose.prod.yaml）

```yaml
version: "3.8"

services:
  web:
    image: myapp:${VERSION:-latest}
    restart: always
    environment:
      NODE_ENV=production
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
      rollback_config:
        parallelism: 1
        delay: 5s
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "5"

  db:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G

  # 生产添加内容
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/prod.conf:/etc/nginx/nginx.conf:ro
      - ssl-certs:/etc/nginx/ssl:ro
    restart: always
    depends_on:
      - web

secrets:
  db_password:
    external: true

volumes:
  postgres-data:
    driver: local
  ssl-certs:
    external: true
```

### 测试配置（compose.staging.yaml）

```yaml
version: "3.8"

services:
  web:
    image: myapp:staging-${VERSION:-latest}
    restart: unless-stopped
    environment:
      NODE_ENV=staging
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 1G

  db:
    environment:
      POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - staging-db-data:/var/lib/postgresql/data

volumes:
  staging-db-data:
```

## 基本 Docker Compose 命令

```bash
# 启动和管理
docker compose up -d                    # 分离模式启动
docker compose down                     # 停止并移除
docker compose restart                  # 重启所有服务
docker compose stop                     # 停止但不移除

# 构建和拉取
docker compose build                    # 构建所有镜像
docker compose pull                     # 拉取所有镜像
docker compose build --no-cache        # 清除构建缓存

# 查看和监控
docker compose ps                       # 列出容器
docker compose logs -f                  # 跟踪日志
docker compose top                      # 运行进程
docker compose events                   # 实时事件

# 执行和调试
docker compose exec service sh          # 交互式 Shell
docker compose run --rm service cmd     # 执行一次性命令
```

### 文件结构

```
project/
├── compose.yaml              # 基本配置
├── compose.override.yaml     # 本地覆盖（自动加载）
├── compose.prod.yaml         # 生产配置
├── compose.staging.yaml      # 测试配置
├── .env                      # 默认环境变量
├── .env.prod                 # 生产环境变量
├── services/
│   ├── frontend/
│   │   ├── Dockerfile
│   │   └── src/
│   ├── backend/
│   │   ├── Dockerfile
│   │   └── src/
│   └── worker/
│       ├── Dockerfile
│       └── src/
└── docker/
    ├── nginx/
    │   └── nginx.conf
    └── scripts/
        └── init.sql
```

## 资源

- Docker Compose 文档：https://docs.docker.com/compose/
- Compose 文件规范：https://docs.docker.com/compose/compose-file/
- Docker Hub：https://hub.docker.com/
- Awesome Compose 示例：https://github.com/docker/awesome-compose
- Docker Compose GitHub：https://github.com/docker/compose
- 最佳实践指南：https://docs.docker.com/develop/dev-best-practices/

---

**技能版本**: 1.0.0
**最后更新**: 2025年10月
**技能类别**: DevOps、容器编排、应用程序部署
**兼容**: Docker Compose v3.8+, Docker Engine 20.10+
