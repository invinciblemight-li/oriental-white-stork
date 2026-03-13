# 部署指南

## 环境要求

### 最低配置

- **CPU**: 2核
- **内存**: 4GB
- **磁盘**: 20GB
- **网络**: 10Mbps

### 推荐配置

- **CPU**: 4核+
- **内存**: 8GB+
- **磁盘**: 50GB+ SSD
- **网络**: 100Mbps+

### 软件依赖

- Docker 20.10+
- Docker Compose 2.0+
- Git 2.30+

---

## 快速部署（Docker Compose）

### 1. 克隆仓库

```bash
git clone https://github.com/invinciblemight-li/oriental-white-stork.git
cd oriental-white-stork
```

### 2. 配置环境变量

```bash
cp backend/.env.example backend/.env
```

编辑 `.env` 文件，修改以下配置：

```bash
# 数据库密码（必须修改）
DB_PASSWORD=your_secure_password_here

# JWT密钥（必须修改，至少32位随机字符串）
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production

# 其他配置按需修改
```

### 3. 启动服务

```bash
docker-compose up -d
```

### 4. 检查状态

```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f backend

# 健康检查
curl http://localhost:8000/health
```

### 5. 访问服务

- **API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

---

## 生产环境部署

### 使用 Docker Swarm

#### 1. 初始化 Swarm

```bash
docker swarm init
```

#### 2. 创建网络

```bash
docker network create --driver overlay stork-network
```

#### 3. 部署服务

```bash
docker stack deploy -c docker-compose.prod.yml stork
```

#### 4. 查看服务

```bash
docker service ls
docker service logs stork_backend
```

### 使用 Kubernetes

#### 1. 创建命名空间

```bash
kubectl create namespace oriental-white-stork
```

#### 2. 创建 ConfigMap

```bash
kubectl create configmap stork-config \
  --from-file=backend/.env \
  -n oriental-white-stork
```

#### 3. 创建 Secret

```bash
kubectl create secret generic stork-secrets \
  --from-literal=jwt-secret=your-secret \
  --from-literal=db-password=your-password \
  -n oriental-white-stork
```

#### 4. 部署应用

```bash
kubectl apply -f k8s/ -n oriental-white-stork
```

#### 5. 查看状态

```bash
kubectl get pods -n oriental-white-stork
kubectl get svc -n oriental-white-stork
kubectl logs -f deployment/backend -n oriental-white-stork
```

---

## 手动部署

### 1. 安装依赖

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-pip postgresql-15 redis-server nginx
```

**CentOS/RHEL:**
```bash
sudo yum install -y python311 postgresql15 redis nginx
```

### 2. 配置 PostgreSQL

```bash
# 创建数据库
sudo -u postgres psql -c "CREATE DATABASE oriental_white_stork;"
sudo -u postgres psql -c "CREATE USER stork_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE oriental_white_stork TO stork_user;"

# 初始化表结构
psql -U stork_user -d oriental_white_stork -f backend/init.sql
```

### 3. 配置 Redis

```bash
# 编辑配置文件
sudo nano /etc/redis/redis.conf

# 修改以下配置
bind 127.0.0.1
requirepass your_redis_password

# 重启服务
sudo systemctl restart redis
```

### 4. 部署后端

```bash
# 创建用户
sudo useradd -r -s /bin/false stork

# 创建目录
sudo mkdir -p /opt/stork/backend
sudo chown stork:stork /opt/stork/backend

# 复制代码
sudo cp -r backend/* /opt/stork/backend/

# 安装依赖
cd /opt/stork/backend
sudo -u stork pip install -r requirements.txt

# 配置环境变量
sudo nano /opt/stork/backend/.env

# 创建 systemd 服务
sudo nano /etc/systemd/system/stork-backend.service
```

**stork-backend.service:**
```ini
[Unit]
Description=Oriental White Stork Backend
After=network.target postgresql redis

[Service]
Type=simple
User=stork
WorkingDirectory=/opt/stork/backend
Environment=PATH=/opt/stork/backend/venv/bin
ExecStart=/opt/stork/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable stork-backend
sudo systemctl start stork-backend

# 查看状态
sudo systemctl status stork-backend
sudo journalctl -u stork-backend -f
```

### 5. 配置 Nginx

```bash
sudo nano /etc/nginx/sites-available/stork
```

**Nginx 配置:**
```nginx
server {
    listen 80;
    server_name api.oriental-white-stork.example.com;
    
    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.oriental-white-stork.example.com;
    
    # SSL 证书
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # 代理设置
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

```bash
# 启用配置
sudo ln -s /etc/nginx/sites-available/stork /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## SSL/TLS 配置

### 使用 Let's Encrypt

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d api.oriental-white-stork.example.com

# 自动续期
sudo certbot renew --dry-run
```

### 使用自签名证书（测试环境）

```bash
# 生成证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /opt/stork/ssl/key.pem \
  -out /opt/stork/ssl/cert.pem \
  -subj "/CN=api.oriental-white-stork.example.com"

# 配置后端使用证书
export TLS_CERT_PATH=/opt/stork/ssl/cert.pem
export TLS_KEY_PATH=/opt/stork/ssl/key.pem
export TLS_ENABLED=true
```

---

## 监控配置

### Prometheus

```bash
# 安装 Prometheus
sudo apt install -y prometheus

# 配置
sudo nano /etc/prometheus/prometheus.yml
```

**prometheus.yml:**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'stork-backend'
    static_configs:
      - targets: ['localhost:8000']
```

### Grafana

```bash
# 安装 Grafana
sudo apt install -y grafana

# 启动服务
sudo systemctl enable grafana-server
sudo systemctl start grafana-server

# 访问 http://localhost:3000 (admin/admin)
```

---

## 备份与恢复

### 数据库备份

```bash
# 手动备份
pg_dump -U stork_user oriental_white_stork > backup_$(date +%Y%m%d).sql

# 自动备份脚本
sudo nano /opt/stork/scripts/backup.sh
```

**backup.sh:**
```bash
#!/bin/bash
BACKUP_DIR="/opt/stork/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份数据库
pg_dump -U stork_user oriental_white_stork > "$BACKUP_DIR/db_$DATE.sql"

# 备份 Redis
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb "$BACKUP_DIR/redis_$DATE.rdb"

# 压缩
gzip "$BACKUP_DIR/db_$DATE.sql"

# 清理旧备份（保留7天）
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete
```

```bash
# 添加定时任务
crontab -e

# 每天凌晨2点备份
0 2 * * * /opt/stork/scripts/backup.sh
```

### 数据恢复

```bash
# 恢复数据库
gunzip backup_20240115.sql.gz
psql -U stork_user oriental_white_stork < backup_20240115.sql

# 恢复 Redis
sudo systemctl stop redis
cp backup_20240115.rdb /var/lib/redis/dump.rdb
sudo systemctl start redis
```

---

## 故障排查

### 常见问题

**1. 服务无法启动**
```bash
# 检查日志
sudo journalctl -u stork-backend -n 100

# 检查端口占用
sudo netstat -tlnp | grep 8000
```

**2. 数据库连接失败**
```bash
# 检查 PostgreSQL 状态
sudo systemctl status postgresql

# 检查连接
psql -U stork_user -h localhost -d oriental_white_stork -c "SELECT 1;"
```

**3. Redis 连接失败**
```bash
# 检查 Redis 状态
sudo systemctl status redis

# 测试连接
redis-cli ping
```

**4. 性能问题**
```bash
# 查看资源使用
top
htop

# 查看数据库性能
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

---

## 升级指南

### 升级步骤

```bash
# 1. 备份数据
/opt/stork/scripts/backup.sh

# 2. 拉取最新代码
cd /opt/stork
git pull origin main

# 3. 更新依赖
cd backend
pip install -r requirements.txt --upgrade

# 4. 数据库迁移
python migrate.py

# 5. 重启服务
sudo systemctl restart stork-backend

# 6. 验证升级
curl http://localhost:8000/health
```

---

## 安全加固

### 1. 防火墙配置

```bash
# 允许必要端口
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. 禁用 root 登录

```bash
sudo nano /etc/ssh/sshd_config
# 设置 PermitRootLogin no
sudo systemctl restart sshd
```

### 3. 定期更新

```bash
# 自动安全更新
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades
```

---

## 多环境部署

### 开发环境

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### 测试环境

```bash
docker-compose -f docker-compose.yml -f docker-compose.test.yml up -d
```

### 生产环境

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```
