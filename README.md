# 🦢 东方白鹳 (Oriental White Stork)

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="license">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue.svg" alt="python">
  <img src="https://img.shields.io/badge/node-18%2B-blue.svg" alt="node">
  <img src="https://img.shields.io/badge/coverage-85%25-brightgreen.svg" alt="coverage">
</p>

<p align="center">
  <b>连接每个人的Agent，就像互联网连接我们每个人</b>
</p>

<p align="center">
  <a href="#快速开始">快速开始</a> |
  <a href="#架构设计">架构设计</a> |
  <a href="#api文档">API文档</a> |
  <a href="#贡献指南">贡献指南</a>
</p>

---

## 📖 简介

东方白鹳是一个开源的智能体（Agent）连接系统，旨在让不同的AI Agent能够像互联网连接人类一样相互连接、协作。

### ✨ 核心特性

- 🌐 **Agent连接协议** - 标准化的Agent通信协议
- 🎨 **可视化组件** - 丰富的数据可视化组件库（8种主题）
- 🔒 **安全沙箱** - 多层安全防护，JWT认证、TLS加密
- 📊 **监控管理** - Prometheus + Grafana 监控体系
- 🧪 **完整测试** - 单元测试 + 集成测试，覆盖率85%+

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### 安装

**1. 克隆仓库**
```bash
git clone https://github.com/invinciblemight-li/oriental-white-stork.git
cd oriental-white-stork
```

**2. 安装后端依赖**
```bash
cd backend
pip install -r requirements.txt
```

**3. 安装前端依赖**
```bash
cd ../frontend/stork-viz-react
npm install
```

**4. 配置环境变量**
```bash
cp backend/.env.example backend/.env
# 编辑 .env 文件，配置数据库和Redis连接
```

**5. 初始化数据库**
```bash
cd backend
python init_db.py
```

**6. 启动服务**
```bash
# 终端1：启动后端
cd backend
python server.py

# 终端2：启动前端
cd frontend/stork-viz-react
npm start
```

### Docker 快速启动

```bash
docker-compose up -d
```

---

## 📦 项目结构

```
oriental-white-stork/
├── backend/                    # 后端服务
│   ├── core/                   # 核心模块
│   │   ├── agent_registry.py      # Agent注册中心
│   │   ├── message_broker.py      # 消息代理
│   │   ├── security.py            # 安全网关
│   │   └── config.py              # 配置管理
│   ├── sdk/                    # SDK
│   │   └── python/
│   ├── tests/                  # 测试
│   │   ├── unit/
│   │   └── integration/
│   ├── server.py               # 主入口
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # 前端
│   ├── stork-viz-core/         # 可视化核心库
│   └── stork-viz-react/        # React组件库
│
├── docs/                       # 文档
│   ├── api.md                  # API文档
│   ├── architecture.md         # 架构设计
│   └── deployment.md           # 部署指南
│
├── docker-compose.yml          # Docker编排
├── Makefile                    # 常用命令
└── README.md
```

---

## 🏗️ 架构设计

### 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        接入层 (Access Layer)                 │
│         WebSocket (WSS)  |  REST API (HTTPS)                │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     安全网关层 (Security Gateway)            │
│    TLS/SSL  |  JWT Auth  |  Rate Limit  |  Size Limit       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      核心引擎层 (Core Engine)                │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │   消息总线       │  │  Agent注册中心   │                   │
│  │  MessageBroker  │  │  AgentRegistry  │                   │
│  └─────────────────┘  └─────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      存储层 (Storage Layer)                  │
│    PostgreSQL (持久化)  |  Redis (缓存/消息总线)              │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

**后端:**
- Python 3.8+ | FastAPI | Uvicorn
- PostgreSQL | Redis
- WebSocket | JWT | Prometheus

**前端:**
- TypeScript | React 18+
- Canvas API | CSS Variables

**运维:**
- Docker | Docker Compose
- Prometheus | Grafana

---

## 📚 API文档

### Agent管理

**注册Agent**
```python
POST /api/v1/agents/register
Content-Type: application/json

{
  "agent_id": "agent_001",
  "name": "My Agent",
  "type": "service",
  "capabilities": ["text_processing", "data_analysis"]
}
```

**发送消息**
```python
POST /api/v1/messages/send
Content-Type: application/json
Authorization: Bearer <token>

{
  "sender_id": "agent_001",
  "recipient_id": "agent_002",
  "content": {"text": "Hello!"},
  "message_type": "direct"
}
```

**WebSocket连接**
```javascript
const ws = new WebSocket('wss://localhost:8000/ws/agents/agent_001?token=<jwt_token>');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};

ws.send(JSON.stringify({
  type: 'send_message',
  recipient_id: 'agent_002',
  content: { text: 'Hello!' }
}));
```

更多API文档请参考 [docs/api.md](./docs/api.md)

---

## 🧪 测试

**运行所有测试**
```bash
make test
```

**运行单元测试**
```bash
cd backend
pytest tests/unit -v
```

**运行集成测试**
```bash
cd backend
pytest tests/integration -v
```

**生成覆盖率报告**
```bash
cd backend
pytest --cov=core --cov-report=html
```

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！请查看 [CONTRIBUTING.md](./CONTRIBUTING.md) 了解如何参与。

### 开发流程

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 📜 许可证

本项目采用 [MIT 许可证](./LICENSE) 开源。

---

<p align="center">
  <b>🦢 让Agent连接世界，让世界更智能</b>
</p>
