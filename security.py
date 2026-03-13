"""
东方白鹳 - 安全网关模块
提供JWT认证、速率限制、消息大小验证等功能
"""

import jwt
import time
import json
from typing import Dict, Optional, Any
from datetime import datetime, timedelta


class JWTAuthManager:
    """JWT认证管理器"""
    
    def __init__(self, secret: str, algorithm: str = "HS256", expiration: int = 3600):
        self.secret = secret
        self.algorithm = algorithm
        self.expiration = expiration
    
    def create_token(self, payload: Dict[str, Any]) -> str:
        """创建JWT Token"""
        token_payload = payload.copy()
        token_payload.update({
            "exp": datetime.utcnow() + timedelta(seconds=self.expiration),
            "iat": datetime.utcnow()
        })
        return jwt.encode(token_payload, self.secret, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """验证JWT Token"""
        return jwt.decode(token, self.secret, algorithms=[self.algorithm])


class RateLimiter:
    """速率限制器（令牌桶算法）"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients: Dict[str, Dict[str, Any]] = {}
    
    def allow_request(self, client_id: str) -> bool:
        """检查是否允许请求"""
        now = time.time()
        
        if client_id not in self.clients:
            self.clients[client_id] = {
                "tokens": self.max_requests - 1,
                "last_update": now
            }
            return True
        
        client = self.clients[client_id]
        time_passed = now - client["last_update"]
        tokens_to_add = int(time_passed / self.window_seconds * self.max_requests)
        
        client["tokens"] = min(self.max_requests, client["tokens"] + tokens_to_add)
        client["last_update"] = now
        
        if client["tokens"] > 0:
            client["tokens"] -= 1
            return True
        
        return False


class MessageSizeValidator:
    """消息大小验证器"""
    
    def __init__(self, max_size_mb: int = 1):
        self.max_size_bytes = max_size_mb * 1024 * 1024
    
    def validate(self, message: Dict[str, Any]) -> bool:
        """验证消息大小"""
        try:
            message_json = json.dumps(message)
            return len(message_json.encode('utf-8')) <= self.max_size_bytes
        except (TypeError, ValueError):
            return False


class SecurityGateway:
    """安全网关"""
    
    def __init__(
        self,
        jwt_secret: str,
        jwt_expiration: int = 3600,
        rate_limit_requests: int = 100,
        rate_limit_window: int = 60,
        max_message_size_mb: int = 1
    ):
        self.auth_manager = JWTAuthManager(jwt_secret, expiration=jwt_expiration)
        self.rate_limiter = RateLimiter(rate_limit_requests, rate_limit_window)
        self.size_validator = MessageSizeValidator(max_message_size_mb)
    
    def authenticate(self, token: str) -> Dict[str, Any]:
        """认证Token"""
        return self.auth_manager.verify_token(token)
    
    def check_rate_limit(self, client_id: str) -> bool:
        """检查速率限制"""
        return self.rate_limiter.allow_request(client_id)
    
    def validate_message_size(self, message: Dict[str, Any]) -> bool:
        """验证消息大小"""
        return self.size_validator.validate(message)
