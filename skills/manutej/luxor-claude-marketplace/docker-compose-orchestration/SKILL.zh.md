---
name: docker-compose-orchestration
description: 使用Docker Compose进行多容器应用程序的容器编排、网络、卷和生产部署
---

# Docker Compose 编排

使用 Docker Compose 对多容器应用程序进行编排的综合技能。该技能支持通过服务定义、网络策略、卷管理、健康检查和生产就绪配置，实现容器化应用程序的快速开发、部署和管理。

## 何时使用此技能

在以下情况下使用此技能：

- 构建多容器应用程序（微服务、全栈应用）
- 设置包含数据库、缓存和服务的开发环境
- 将前端、后端和数据库服务组合在一起
- 管理服务依赖关系和启动顺序
- 配置网络和跨服务通信
- 使用卷实现持久化存储
- 将应用程序部署到开发、测试或生产环境
- 创建可重复的开发环境
- 管理应用程序生命周期（启动、停止、重建、扩展）
- 监控应用程序健康并实施健康检查
- 从单个容器迁移到多服务架构
- 本地测试分布式系统

## 核心概念

### Docker Compose 哲学

Docker Compose 通过以下方式简化多容器应用程序管理：

- **声明式配置**：使用 YAML 定义整个应用程序堆栈
- **服务抽象**：每个组件都是一个具有其自身配置的服务
- **自动网络**：服务可以通过名称自动通信
- **卷管理**：跨容器的持久化数据和共享存储
- **环境隔离**：每个项目拥有自己的网络命名空间
- **可重复性**：相同配置适用于所有环境

### 关键 Docker Compose 实体

1. **服务**：单个容器及其配置
2. **网络**：服务之间的通信通道
3. **卷**：持久化存储和数据共享
4. **配置文件**：非敏感配置文件
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
    image: myapp:latest           # 标记生成的镜像
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
      - "com.example.description=后端 API"
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
  # 前端 React 应用程序
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

  # 后端 Node.js API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "4000:4000"
      - "9229:9229"  # 调试器
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
    driver: local
  redis-data:
    driver: local
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
      - ./ssl:/etc/nginx/ssl:ro
    networks:
      - public
    depends_on:
      - auth-service
      - user-service
      - order-service
    restart: unless-stopped

  # 认证服务
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
    container_name: user-service
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
    container_name: order-service
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
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./database/init-multi-db.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - internal
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # RabbitMQ 消息代理
  rabbitmq:
    image: rabbitmq:3-management-alpine
    container_name: rabbitmq
    ports:
      - "5672:5672"   # AMQP
      - "15672:15672" # 管理界面
    environment:
      - RABBITMQ_DEFAULT_USER=admin
      - RABBITMQ_DEFAULT_PASS=${RABBITMQ_PASSWORD}
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq
    networks:
      - internal
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5

networks:
  public:
    driver: bridge
  internal:
    driver: bridge
    internal: true  # 无外部访问

volumes:
  postgres-data:
  rabbitmq-data:
```

### 模式 3：具有热重载的开发环境

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
      - WATCHPACK_POLLING=true
      - NEXT_PUBLIC_API_URL=http://localhost:4000
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
      - "9229:9229"  # Node.js 调试器
    volumes:
      - ./backend:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
      - DEBUG=app:*
      - DATABASE_URL=postgresql://postgres:dev@db:5432/dev_db
    networks:
      - dev-network
    depends_on:
      - db
      - mailhog
    command: npm run dev:debug

  # PostgreSQL 带有 pgAdmin
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_PASSWORD=dev
      - POSTGRES_DB=dev_db
    ports:
      - "5432:5432"
    volumes:
      - dev-db-data:/var/lib/postgresql/data
    networks:
      - dev-network

  pgadmin:
    image: dpage/pgadmin4:latest
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@dev.local
      - PGADMIN_DEFAULT_PASSWORD=admin
    ports:
      - "5050:80"
    networks:
      - dev-network
    depends_on:
      - db

  # MailHog 用于邮件测试
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
      - private   # 可从数据库访问

  database:
    image: postgres
    networks:
      - private   # 与前端隔离

networks:
  public:
    driver: bridge
  private:
    driver: bridge
    internal: true  # 无互联网访问
```

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
    network_mode: "host"  # 使用主机网络堆栈
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
      - "com.example.description=自定义网络"
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
    # 或带选项：
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
    external: true  # 卷在 Compose 外部创建
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

### 应用健康检查

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
      test: ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1"]
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

### 基础配置 (compose.yaml)

```yaml
version: "3.8"

services:
  web:
    image: myapp:latest
    environment:
      - NODE_ENV=production
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

### 开发覆盖 (compose.override.yaml)

```yaml
# 自动与 compose.yaml 在开发环境中合并
version: "3.8"

services:
  web:
    build:
      context: .
      target: development
    volumes:
      - ./src:/app/src  # 实时代码重新加载
      - /app/node_modules
    ports:
      - "3000:3000"     # 用于本地访问
      - "9229:9229"     # 调试端口
    environment:
      - NODE_ENV=development
      - DEBUG=*
    command: npm run dev

  db:
    ports:
      - "5432:5432"     # 用于本地工具
    environment:
      - POSTGRES_PASSWORD=dev
    volumes:
      - ./init-dev.sql:/docker-entrypoint-initdb.d/init.sql
```

### 生产配置 (compose.prod.yaml)

```yaml
version: "3.8"

services:
  web:
    image: myapp:${VERSION:-latest}
    restart: always
    environment:
      - NODE_ENV=production
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
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G

  # 生产附加
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

### 测试环境配置 (compose.staging.yaml)

```yaml
version: "3.8"

services:
  web:
    image: myapp:staging-${VERSION:-latest}
    restart: unless-stopped
    environment:
      - NODE_ENV=staging
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 1G

  db:
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - staging-db-data:/var/lib/postgresql/data

volumes:
  staging-db-data:
```

## 必要的 Docker Compose 命令

### 项目管理

```bash
# 启动服务
docker compose up                    # 前台
docker compose up -d                 # 分离 (后台)
docker compose up --build            # 重新构建镜像
docker compose up --force-recreate   # 重新创建容器
docker compose up --scale web=3      # 将服务扩展到 3 个实例

# 停止服务
docker compose stop                  # 停止容器
docker compose down                  # 停止并移除容器/网络
docker compose down -v               # 也移除卷
docker compose down --rmi all        # 也移除镜像

# 重启服务
docker compose restart               # 重启所有服务
docker compose restart web           # 重启特定服务
```

### 服务管理

```bash
# 构建服务
docker compose build                 # 构建所有服务
docker compose build web             # 构建特定服务
docker compose build --no-cache      # 无缓存构建
docker compose build --pull          # 拉取最新基础镜像

# 查看服务
docker compose ps                    # 列出容器
docker compose ps -a                 # 包括已停止的容器
docker compose top                   # 显示运行进程
docker compose images                # 列出镜像

# 日志
docker compose logs                  # 查看所有日志
docker compose logs -f               # 跟踪日志
docker compose logs web              # 服务特定日志
docker compose logs --tail=100 web   # 最后 100 行
```

### 执行和调试

```bash
# 执行命令
docker compose exec web sh           # 交互式 Shell
docker compose exec web npm test     # 运行命令
docker compose exec -u root web sh   # 以 root 身份运行

# 一次性命令
docker compose run web npm install   # 在新容器中运行命令
docker compose run --rm web test     # 运行后移除容器
docker compose run --no-deps web sh  # 不启动依赖
```

### 配置管理

```bash
# 多个 compose 文件
docker compose -f compose.yaml -f compose.prod.yaml up

# 环境特定部署
docker compose --env-file .env.prod up
docker compose -p myproject up       # 自定义项目名

# 配置验证
docker compose config                # 验证并查看配置
docker compose config --quiet        # 仅验证
docker compose config --services     # 列出服务
docker compose config --volumes      # 列出卷
```

## 15+ Compose 示例

### 示例 1：NGINX + PHP + MySQL (LAMP 堆栈)

```yaml
version: "3.8"

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./public:/var/www/html
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    networks:
      - lamp
    depends_on:
      - php

  php:
    build:
      context: ./php
      dockerfile: Dockerfile
    volumes:
      - ./public:/var/www/html
    networks:
      - lamp
    depends_on:
      - mysql

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: secret
      MYSQL_DATABASE: myapp
      MYSQL_USER: user
      MYSQL_PASSWORD: password
    volumes:
      - mysql-data:/var/lib/mysql
    networks:
      - lamp

networks:
  lamp:

volumes:
  mysql-data:
```

### 示例 2：Django + PostgreSQL + Redis + Celery

```yaml
version: "3.8"

services:
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/django_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: django_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres-data:/var/lib/postgresql/data

  redis:
    image: redis:alpine
    volumes:
      - redis-data:/data

  celery:
    build: .
    command: celery -A myproject worker -l info
    volumes:
      - .:/code
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/django_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  celery-beat:
    build: .
    command: celery -A myproject beat -l info
    volumes:
      - .:/code
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/django_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  postgres-data:
  redis-data:
```

### 示例 3：React + Node.js + MongoDB + NGINX

```yaml
version: "3.8"

services:
  frontend:
    build:
      context: ./frontend
      args:
        REACT_APP_API_URL: http://localhost/api
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - CHOKIDAR_USEPOLLING=true
    networks:
      - app-network

  backend:
    build: ./backend
    ports:
      - "5000:5000"
    volumes:
      - ./backend:/app
      - /app/node_modules
    environment:
      - MONGODB_URI=mongodb://mongo:27017/myapp
      - JWT_SECRET=dev-secret
    depends_on:
      - mongo
    networks:
      - app-network

  mongo:
    image: mongo:6
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db
      - mongo-config:/data/configdb
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=secret
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - frontend
      - backend
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  mongo-data:
  mongo-config:
```

### 示例 4：Spring Boot + MySQL + Adminer

```yaml
version: "3.8"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - SPRING_DATASOURCE_URL=jdbc:mysql://db:3306/springdb?useSSL=false
      - SPRING_DATASOURCE_USERNAME=root
      - SPRING_DATASOURCE_PASSWORD=secret
      - SPRING_JPA_HIBERNATE_DDL_AUTO=update
    depends_on:
      db:
        condition: service_healthy
    networks:
      - spring-network

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: secret
      MYSQL_DATABASE: springdb
    volumes:
      - mysql-data:/var/lib/mysql
    networks:
      - spring-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  adminer:
    image: adminer:latest
    ports:
      - "8081:8080"
    environment:
      ADMINER_DEFAULT_SERVER: db
    networks:
      - spring-network

networks:
  spring-network:

volumes:
  mysql-data:
```

### 示例 5：WordPress + MySQL + phpMyAdmin

```yaml
version: "3.8"

services:
  wordpress:
    image: wordpress:latest
    ports:
      - "8000:80"
    environment:
      WORDPRESS_DB_HOST: db:3306
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: wordpress
      WORDPRESS_DB_NAME: wordpress
    volumes:
      - wordpress-data:/var/www/html
    depends_on:
      - db
    networks:
      - wordpress-network

  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: wordpress
      MYSQL_ROOT_PASSWORD: rootpassword
    volumes:
      - db-data:/var/lib/mysql
    networks:
      - wordpress-network

  phpmyadmin:
    image: phpmyadmin/phpmyadmin:latest
    ports:
      - "8080:80"
    environment:
      PMA_HOST: db
      PMA_USER: root
      PMA_PASSWORD: rootpassword
    depends_on:
      - db
    networks:
      - wordpress-network

networks:
  wordpress-network:

volumes:
  wordpress-data:
  db-data:
```

### 示例 6：Elasticsearch + Kibana + Logstash (ELK 堆栈)

```yaml
version: "3.8"

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.10.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
      - "9300:9300"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    networks:
      - elk

  logstash:
    image: docker.elastic.co/logstash/logstash:8.10.0
    container_name: logstash
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline:ro
      - ./logstash/config/logstash.yml:/usr/share/logstash/config/logstash.yml:ro
    ports:
      - "5000:5000"
      - "9600:9600"
    environment:
      LS_JAVA_OPTS: "-Xmx256m -Xms256m"
    networks:
      - elk
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.10.0
    container_name: kibana
    ports:
      - "5601:5601"
    environment:
      ELASTICSEARCH_URL: http://elasticsearch:9200
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200
    networks:
      - elk
    depends_on:
      - elasticsearch

networks:
  elk:
    driver: bridge

volumes:
  elasticsearch-data:
```

### 示例 7：GitLab + GitLab Runner

```yaml
version: "3.8"

services:
  gitlab:
    image: gitlab/gitlab-ce:latest
    container_name: gitlab
    restart: unless-stopped
    hostname: gitlab.local
    environment:
      GITLAB_OMNIBUS_CONFIG: |
        external_url 'http://gitlab.local'
        gitlab_rails['gitlab_shell_ssh_port'] = 2222
    ports:
      - "80:80"
      - "443:443"
      - "2222:22"
    volumes:
      - gitlab-config:/etc/gitlab
      - gitlab-logs:/var/log/gitlab
      - gitlab-data:/var/opt/gitlab
    networks:
      - gitlab-network

  gitlab-runner:
    image: gitlab/gitlab-runner:latest
    container_name: gitlab-runner
    restart: unless-stopped
    volumes:
      - gitlab-runner-config:/etc/gitlab-runner
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - gitlab-network
    depends_on:
      - gitlab

networks:
  gitlab-network:

volumes:
  gitlab-config:
  gitlab-logs:
  gitlab-data:
  gitlab-runner-config:
```

### 示例 8：Jenkins + Docker-in-Docker

```yaml
version: "3.8"

services:
  jenkins:
    image: jenkins/jenkins:lts
    container_name: jenkins
    user: root
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - jenkins-data:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
      - /usr/bin/docker:/usr/bin/docker
    environment:
      - JAVA_OPTS=-Djenkins.install.runSetupWizard=false
    networks:
      - jenkins-network

  jenkins-agent:
    image: jenkins/inbound-agent:latest
    container_name: jenkins-agent
    environment:
      - JENKINS_URL=http://jenkins:8080
      - JENKINS_AGENT_NAME=agent1
      - JENKINS_SECRET=${AGENT_SECRET}
      - JENKINS_AGENT_WORKDIR=/home/jenkins/agent
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - jenkins-network
    depends_on:
      - jenkins

networks:
  jenkins-network:

volumes:
  jenkins-data:
```

### 示例 9：Prometheus + Grafana + Node Exporter

```yaml
version: "3.8"

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
    networks:
      - monitoring
    depends_on:
      - prometheus

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    networks:
      - monitoring

networks:
  monitoring:

volumes:
  prometheus-data:
  grafana-data:
```

### Example 10: RabbitMQ + Multiple Consumers

```yaml
version: "3.8"

services:
  rabbitmq:
    image: rabbitmq:3-management-alpine
    container_name: rabbitmq
    ports:
      - "5672:5672"   # AMQP
      - "15672:15672" # Management UI
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: secret
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq
      - ./rabbitmq/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf:ro
    networks:
      - messaging
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5

  producer:
    build: ./services/producer
    environment:
      RABBITMQ_URL: amqp://admin:secret@rabbitmq:5672
    depends_on:
      rabbitmq:
        condition: service_healthy
    networks:
      - messaging

  consumer-1:
    build: ./services/consumer
    environment:
      RABBITMQ_URL: amqp://admin:secret@rabbitmq:5672
      WORKER_ID: 1
    depends_on:
      rabbitmq:
        condition: service_healthy
    networks:
      - messaging
    deploy:
      replicas: 3

  consumer-2:
    build: ./services/consumer
    environment:
      RABBITMQ_URL: amqp://admin:secret@rabbitmq:5672
      WORKER_ID: 2
    depends_on:
      rabbitmq:
        condition: service_healthy
    networks:
      - messaging

networks:
  messaging:

volumes:
  rabbitmq-data:
```

### Example 11: Traefik Reverse Proxy

```yaml
version: "3.8"

services:
  traefik:
    image: traefik:v2.10
    container_name: traefik
    command:
      - --api.insecure=true
      - --providers.docker=true
      - --providers.docker.exposedbydefault=false
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"  # Traefik dashboard
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik/traefik.yml:/etc/traefik/traefik.yml:ro
      - ./traefik/dynamic:/etc/traefik/dynamic:ro
    networks:
      - traefik-network

  whoami:
    image: traefik/whoami
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.whoami.rule=Host(`whoami.local`)"
      - "traefik.http.routers.whoami.entrypoints=web"
    networks:
      - traefik-network

  app:
    image: nginx:alpine
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.app.rule=Host(`app.local`)"
      - "traefik.http.routers.app.entrypoints=web"
      - "traefik.http.services.app.loadbalancer.server.port=80"
    networks:
      - traefik-network

networks:
  traefik-network:
    driver: bridge
```

### Example 12: MinIO + PostgreSQL Backup

```yaml
version: "3.8"

services:
  minio:
    image: minio/minio:latest
    container_name: minio
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio-data:/data
    networks:
      - storage
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: secret
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - storage

  backup:
    image: postgres:15-alpine
    environment:
      POSTGRES_HOST: postgres
      POSTGRES_DB: myapp
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: secret
      MINIO_ENDPOINT: minio:9000
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    volumes:
      - ./scripts/backup.sh:/backup.sh:ro
    entrypoint: ["/bin/sh", "/backup.sh"]
    depends_on:
      - postgres
      - minio
    networks:
      - storage

networks:
  storage:

volumes:
  minio-data:
  postgres-data:
```

### Example 13: Apache Kafka + Zookeeper

```yaml
version: "3.8"

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    container_name: zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"
    volumes:
      - zookeeper-data:/var/lib/zookeeper/data
      - zookeeper-logs:/var/lib/zookeeper/log
    networks:
      - kafka-network

  kafka:
    image: confluentinc/cp-kafka:latest
    container_name: kafka
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
      - "29092:29092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092,PLAINTEXT_HOST://localhost:29092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    volumes:
      - kafka-data:/var/lib/kafka/data
    networks:
      - kafka-network

  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: kafka-ui
    depends_on:
      - kafka
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:9092
      KAFKA_CLUSTERS_0_ZOOKEEPER: zookeeper:2181
    networks:
      - kafka-network

networks:
  kafka-network:

volumes:
  zookeeper-data:
  zookeeper-logs:
  kafka-data:
```

### Example 14: Keycloak + PostgreSQL (Identity & Access Management)

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:15-alpine
    container_name: keycloak-db
    environment:
      POSTGRES_DB: keycloak
      POSTGRES_USER: keycloak
      POSTGRES_PASSWORD: password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - keycloak-network

  keycloak:
    image: quay.io/keycloak/keycloak:latest
    container_name: keycloak
    environment:
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://postgres:5432/keycloak
      KC_DB_USERNAME: keycloak
      KC_DB_PASSWORD: password
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: admin
    command: start-dev
    ports:
      - "8080:8080"
    depends_on:
      - postgres
    networks:
      - keycloak-network

networks:
  keycloak-network:

volumes:
  postgres-data:
```

### Example 15: Portainer (Docker Management UI)

```yaml
version: "3.8"

services:
  portainer:
    image: portainer/portainer-ce:latest
    container_name: portainer
    restart: unless-stopped
    ports:
      - "9000:9000"
      - "8000:8000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - portainer-data:/data
    networks:
      - portainer-network

networks:
  portainer-network:

volumes:
  portainer-data:
```

### Example 16: SonarQube + PostgreSQL (Code Quality)

```yaml
version: "3.8"

services:
  sonarqube:
    image: sonarqube:community
    container_name: sonarqube
    depends_on:
      - db
    environment:
      SONAR_JDBC_URL: jdbc:postgresql://db:5432/sonar
      SONAR_JDBC_USERNAME: sonar
      SONAR_JDBC_PASSWORD: sonar
    volumes:
      - sonarqube-conf:/opt/sonarqube/conf
      - sonarqube-data:/opt/sonarqube/data
      - sonarqube-logs:/opt/sonarqube/logs
      - sonarqube-extensions:/opt/sonarqube/extensions
    ports:
      - "9000:9000"
    networks:
      - sonarqube-network

  db:
    image: postgres:15-alpine
    container_name: sonarqube-db
    environment:
      POSTGRES_USER: sonar
      POSTGRES_PASSWORD: sonar
      POSTGRES_DB: sonar
    volumes:
      - postgresql-data:/var/lib/postgresql/data
    networks:
      - sonarqube-network

networks:
  sonarqube-network:

volumes:
  sonarqube-conf:
  sonarqube-data:
  sonarqube-logs:
  sonarqube-extensions:
  postgresql-data:
```

## Best Practices

### Service Configuration

1. **使用特定镜像标签**：生产环境中避免使用 `latest`
2. **健康检查**：关键服务必须定义健康检查
3. **资源限制**：生产环境中设置 CPU 和内存限制
4. **重启策略**：使用合适的中断策略
5. **环境变量**：使用 `.env` 文件管理敏感数据
6. **命名卷**：使用命名卷实现数据持久化
7. **网络隔离**：前端和后端使用不同网络
8. **日志配置**：设置正确的日志轮转

### 开发工作流

1. **热重载**：将源代码作为卷挂载实现实时更新
2. **调试端口**：开发环境中暴露调试端口
3. **覆盖文件**：使用 `compose.override.yaml` 进行本地配置
4. **构建缓存**：构建 Dockerfile 时优化缓存
5. **分离关注点**：每个容器一个进程
6. **服务命名**：使用描述性、一致的服务名称

### 安全

1. **密钥管理**：使用 Docker 密钥或外部密钥管理器
2. **非根用户**：以非根用户运行容器
3. **只读文件系统**：尽可能将卷挂载为只读
4. **网络分割**：使用多个网络实现隔离
5. **环境隔离**：永远不要提交敏感的 `.env` 文件
6. **镜像扫描**：扫描镜像中的漏洞
7. **最小化基础镜像**：使用 Alpine 或 distroless 镜像

### 生产部署

1. **镜像版本控制**：使用语义化版本标记镜像
2. **滚动更新**：配置渐进式发布策略
3. **监控**：集成监控解决方案
4. **备份策略**：实施自动备份
5. **高可用性**：关键服务部署多个副本
6. **负载均衡**：使用反向代理实现负载均衡
7. **配置管理**：外部化配置
8. **灾难恢复**：测试备份和恢复流程

## Troubleshooting

### 常见问题

**服务无法通信**
- 检查网络配置
- 确认服务名称正确
- 确保服务在同一网络
- 检查防火墙规则

**卷无法持久化**
- 确认命名卷已定义
- 检查卷挂载路径
- 确认权限设置正确
- 查看卷驱动器配置

**服务健康检查失败**
- 增加启动间隔
- 验证健康检查命令
- 查看服务日志
- 确认依赖服务就绪

**端口冲突**
- 检查端口是否被其他服务占用
- 使用不同的主机端口
- 审查端口映射语法

**构建失败**
- 清除构建缓存：`docker compose build --no-cache`
- 检查 Dockerfile 语法
- 验证构建上下文
- 审查构建参数

### 调试命令

```bash
# 查看详细容器信息
docker compose ps -a
docker compose logs -f                  # 跟踪日志
docker inspect container-name

# 在运行容器中执行命令
docker compose exec service-name sh     # 交互式 Shell
docker compose run --rm service cmd     # 一次性命令
```

## 高级用法

### 多阶段构建优化

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    # Dockerfile 使用多阶段构建
```

```dockerfile
# 开发阶段
FROM node:18-alpine AS development
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["npm", "run", "dev"]

# 构建阶段
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# 生产阶段
FROM node:18-alpine AS production
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

### 环境特定部署

```bash
# 开发
docker compose up

# 测试
docker compose -f compose.yaml -f compose.staging.yaml up

# 生产
docker compose -f compose.yaml -f compose.prod.yaml up -d

# 使用环境文件
docker compose --env-file .env.prod -f compose.yaml -f compose.prod.yaml up -d
```

### 服务扩展

```bash
# 扩展特定服务
docker compose up -d --scale worker=5

# 扩展多个服务
docker compose up -d --scale worker=5 --scale consumer=3
```

### 条件服务激活（配置文件）

```yaml
services:
  web:
    image: nginx
    # 总是启动

  debug:
    image: debug-tools
    profiles:
      - debug  # 仅在启用 --profile debug 时启动

  test:
    build: .
    profiles:
      - test   # 仅在启用 --profile test 时启动
```

```bash
# 使用 debug 配置文件启动
docker compose --profile debug up

# 使用多个配置文件启动
docker compose --profile debug --profile test up
```

## 快速参考

### 基本命令

```bash
# 启动和管理
docker compose up -d                    # 脱离模式启动
docker compose down                     # 停止并移除
docker compose restart                  # 重启所有
docker compose stop                     # 停止但不移除

# 构建和拉取
docker compose build                    # 构建所有镜像
docker compose pull                     # 拉取所有镜像
docker compose build --no-cache        # 清除构建缓存

# 查看 和 监控
docker compose ps                       # 列出容器
docker compose logs -f                  # 跟踪日志
docker compose top                      # 运行进程
docker compose events                   # 实时事件

# 执行 和 调试
docker compose exec service sh          # 交互式 Shell
docker compose run --rm service cmd     # 一次性命令
```

### 文件结构

```
项目/
├── compose.yaml              # 基础配置
├── compose.override.yaml     # 本地覆盖（自动加载）
├── compose.prod.yaml         # 生产配置
├── compose.staging.yaml      # 测试配置
├── .env                      # 默认环境变量
├── .env.prod                 # 生产环境变量
├── services/
│   ├── 前端/
│   │   ├── Dockerfile
│   │   └── src/
│   ├── 后端/
│   │   ├── Dockerfile
│   │   └── src/
│   └── 工作进程/
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
```

**功能版本**: 1.0.0
**最后更新**: 2025年10月
**功能类别**: DevOps、容器编排、应用部署
**兼容版本**: Docker Compose v3.8+、Docker Engine 20.10+
