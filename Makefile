# ============================================
# 东方白鹳 - Makefile
# ============================================

.PHONY: help install test lint format clean docker-build docker-run

# 默认目标
help:
	@echo "东方白鹳 - 可用命令:"
	@echo ""
	@echo "  make install       - 安装依赖"
	@echo "  make test          - 运行所有测试"
	@echo "  make test-unit     - 运行单元测试"
	@echo "  make test-integration - 运行集成测试"
	@echo "  make coverage      - 生成测试覆盖率报告"
	@echo "  make lint          - 代码检查"
	@echo "  make format        - 代码格式化"
	@echo "  make clean         - 清理临时文件"
	@echo "  make docker-build  - 构建Docker镜像"
	@echo "  make docker-run    - 运行Docker容器"
	@echo "  make dev           - 启动开发服务器"
	@echo "  make setup         - 初始化项目"
	@echo ""

# 安装依赖
install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend/stork-viz-react && npm install

# 运行所有测试
test:
	@echo "Running all tests..."
	cd backend && pytest -v

# 运行单元测试
test-unit:
	@echo "Running unit tests..."
	cd backend && pytest tests/unit -v

# 运行集成测试
test-integration:
	@echo "Running integration tests..."
	cd backend && pytest tests/integration -v

# 生成覆盖率报告
coverage:
	@echo "Generating coverage report..."
	cd backend && pytest --cov=core --cov-report=html --cov-report=term
	@echo "Coverage report generated at backend/htmlcov/index.html"

# 代码检查
lint:
	@echo "Running linter..."
	cd backend && flake8 core tests --max-line-length=100
	cd frontend/stork-viz-react && npm run lint

# 代码格式化
format:
	@echo "Formatting code..."
	cd backend && black core tests --line-length=100
	cd frontend/stork-viz-react && npm run format

# 清理临时文件
clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete"

# 构建Docker镜像
docker-build:
	@echo "Building Docker images..."
	docker-compose build

# 运行Docker容器
docker-run:
	@echo "Starting Docker containers..."
	docker-compose up -d

# 停止Docker容器
docker-stop:
	@echo "Stopping Docker containers..."
	docker-compose down

# 查看Docker日志
docker-logs:
	@echo "Showing Docker logs..."
	docker-compose logs -f

# 启动开发服务器
dev:
	@echo "Starting development server..."
	cd backend && python server.py

# 初始化项目
setup:
	@echo "Setting up project..."
	@echo "Creating necessary directories..."
	mkdir -p backend/logs
	mkdir -p backend/data
	@echo "Copying environment file..."
	cp backend/.env.example backend/.env
	@echo "Installing dependencies..."
	$(MAKE) install
	@echo "Setup complete! Please edit backend/.env with your configuration."

# 数据库迁移
migrate:
	@echo "Running database migrations..."
	cd backend && python init_db.py

# 生成文档
docs:
	@echo "Generating documentation..."
	cd docs && make html

# 运行性能测试
benchmark:
	@echo "Running benchmarks..."
	cd backend && python -m pytest benchmarks/ -v
