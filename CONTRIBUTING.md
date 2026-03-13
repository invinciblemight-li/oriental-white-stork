# 贡献指南

感谢您对东方白鹳项目的关注！我们欢迎所有形式的贡献。

## 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议，请通过 [GitHub Issues](https://github.com/invinciblemight-li/oriental-white-stork/issues) 提交。

提交问题时，请包含：
- 问题的清晰描述
- 复现步骤
- 期望行为和实际行为
- 环境信息（操作系统、Python版本等）
- 相关的日志或截图

### 提交代码

1. **Fork 仓库**
   ```bash
   git clone https://github.com/invinciblemight-li/oriental-white-stork.git
   cd oriental-white-stork
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **安装开发依赖**
   ```bash
   make setup
   ```

4. **进行更改**
   - 编写代码
   - 添加测试
   - 更新文档

5. **运行测试**
   ```bash
   make test
   make lint
   ```

6. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

7. **推送到您的 Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **创建 Pull Request**

## 代码规范

### Python 代码规范

- 遵循 [PEP 8](https://pep8.org/) 规范
- 使用 [Black](https://black.readthedocs.io/) 格式化代码
- 最大行长度：100字符
- 使用类型注解

```python
# 好的示例
from typing import Optional, List

def process_message(
    message_id: str,
    content: dict,
    priority: Optional[int] = None
) -> bool:
    """处理消息
    
    Args:
        message_id: 消息ID
        content: 消息内容
        priority: 优先级（可选）
    
    Returns:
        处理是否成功
    """
    pass
```

### 提交信息规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat:` 新功能
- `fix:` 修复bug
- `docs:` 文档更新
- `style:` 代码格式（不影响功能）
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动

示例：
```bash
git commit -m "feat: add WebSocket reconnection support"
git commit -m "fix: resolve message routing issue"
git commit -m "docs: update API documentation"
```

### 测试要求

- 所有新功能必须包含单元测试
- 测试覆盖率应保持在 80% 以上
- 使用 pytest 编写测试

```python
# 测试示例
def test_agent_registration():
    """测试Agent注册"""
    agent_data = {
        "agent_id": "test_agent",
        "name": "Test Agent"
    }
    result = registry.register(agent_data)
    assert result is True
```

## 开发环境设置

### 使用 Docker（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend
```

### 本地开发

```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 2. 安装依赖
pip install -r backend/requirements.txt

# 3. 配置环境变量
cp backend/.env.example backend/.env
# 编辑 .env 文件

# 4. 初始化数据库
python backend/init_db.py

# 5. 启动服务
python backend/server.py
```

## 项目结构

```
oriental-white-stork/
├── backend/           # 后端代码
│   ├── core/         # 核心模块
│   ├── tests/        # 测试
│   └── server.py     # 入口文件
├── frontend/         # 前端代码
├── docs/             # 文档
└── docker-compose.yml
```

## 代码审查流程

1. 所有代码更改必须通过 Pull Request
2. 至少需要一名维护者审查
3. 所有测试必须通过
4. 代码必须符合规范

## 行为准则

- 尊重所有参与者
- 接受建设性批评
- 关注对社区最有利的事情

## 获取帮助

- 查看 [文档](./docs)
- 在 [Discussions](https://github.com/invinciblemight-li/oriental-white-stork/discussions) 提问
- 加入我们的社区

## 许可证

通过贡献代码，您同意您的贡献将在 [MIT 许可证](./LICENSE) 下发布。

---

再次感谢您的贡献！🦢
