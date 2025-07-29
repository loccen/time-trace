"""
日志系统
统一的日志管理和配置
"""
import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    # 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
        'RESET': '\033[0m'      # 重置
    }
    
    def format(self, record):
        # 添加颜色
        if hasattr(record, 'levelname'):
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class LoggerManager:
    """日志管理器"""
    
    def __init__(self):
        self.loggers = {}
        self.setup_root_logger()
    
    def setup_root_logger(self):
        """设置根日志器"""
        # 创建日志目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 根日志器配置
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # 清除现有处理器
        root_logger.handlers.clear()
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # 彩色格式化器
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # 文件处理器
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 文件格式化器
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # 错误文件处理器
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / "error.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """获取指定名称的日志器"""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = logger
        
        return self.loggers[name]
    
    def set_level(self, level: str):
        """设置日志级别"""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        log_level = level_map.get(level.upper(), logging.INFO)
        logging.getLogger().setLevel(log_level)
        
        # 更新控制台处理器级别
        for handler in logging.getLogger().handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                handler.setLevel(log_level)
    
    def add_file_handler(self, name: str, filename: str, level: str = "INFO"):
        """为特定日志器添加文件处理器"""
        logger = self.get_logger(name)
        
        # 创建文件处理器
        file_handler = logging.handlers.RotatingFileHandler(
            f"logs/{filename}",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=3,
            encoding='utf-8'
        )
        
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        file_handler.setLevel(level_map.get(level.upper(), logging.INFO))
        
        # 设置格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)


# 全局日志管理器实例
logger_manager = LoggerManager()


def get_logger(name: str) -> logging.Logger:
    """获取日志器的便捷函数"""
    return logger_manager.get_logger(name)


def set_log_level(level: str):
    """设置日志级别的便捷函数"""
    logger_manager.set_level(level)


# 性能日志装饰器
def log_performance(logger_name: str = "Performance"):
    """性能日志装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name)
            start_time = datetime.now()
            
            try:
                result = func(*args, **kwargs)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                logger.info(f"{func.__name__} 执行完成，耗时: {duration:.3f}秒")
                return result
                
            except Exception as e:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                logger.error(f"{func.__name__} 执行失败，耗时: {duration:.3f}秒，错误: {str(e)}")
                raise
        
        return wrapper
    return decorator


# 审计日志
class AuditLogger:
    """审计日志记录器"""
    
    def __init__(self):
        self.logger = get_logger("Audit")
        
        # 添加专门的审计日志文件
        logger_manager.add_file_handler("Audit", "audit.log", "INFO")
    
    def log_operation(self, operation: str, user: str = "system", 
                     target: str = "", details: str = "", success: bool = True):
        """记录操作日志"""
        status = "SUCCESS" if success else "FAILED"
        message = f"[{status}] 用户: {user}, 操作: {operation}, 目标: {target}, 详情: {details}"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.warning(message)
    
    def log_access(self, user: str, resource: str, action: str, ip: str = ""):
        """记录访问日志"""
        message = f"访问记录 - 用户: {user}, 资源: {resource}, 操作: {action}, IP: {ip}"
        self.logger.info(message)
    
    def log_security_event(self, event: str, user: str = "", ip: str = "", details: str = ""):
        """记录安全事件"""
        message = f"安全事件 - 事件: {event}, 用户: {user}, IP: {ip}, 详情: {details}"
        self.logger.warning(message)


# 全局审计日志实例
audit_logger = AuditLogger()


# 便捷函数
def log_operation(operation: str, user: str = "system", target: str = "", 
                 details: str = "", success: bool = True):
    """记录操作日志的便捷函数"""
    audit_logger.log_operation(operation, user, target, details, success)


def log_access(user: str, resource: str, action: str, ip: str = ""):
    """记录访问日志的便捷函数"""
    audit_logger.log_access(user, resource, action, ip)


def log_security_event(event: str, user: str = "", ip: str = "", details: str = ""):
    """记录安全事件的便捷函数"""
    audit_logger.log_security_event(event, user, ip, details)
