"""
日志管理模块
"""
import sys
import os
from pathlib import Path
from typing import Optional
from loguru import logger
from config import settings, get_app_data_dir


class LoggerManager:
    """日志管理器"""
    
    def __init__(self):
        self._initialized = False
        self.setup_logger()
    
    def setup_logger(self):
        """设置日志配置"""
        if self._initialized:
            return
        
        # 移除默认的控制台处理器
        logger.remove()
        
        # 添加控制台输出
        logger.add(
            sys.stderr,
            level=settings.log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                   "<level>{message}</level>",
            colorize=True,
            backtrace=True,
            diagnose=True
        )
        
        # 添加文件输出
        if settings.log_file:
            log_file_path = Path(settings.log_file)
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.add(
                settings.log_file,
                level=settings.log_level,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                rotation="10 MB",  # 日志文件大小超过10MB时轮转
                retention="30 days",  # 保留30天的日志
                compression="zip",  # 压缩旧日志文件
                encoding="utf-8",
                backtrace=True,
                diagnose=True
            )
        
        # 添加错误日志文件
        error_log_path = get_app_data_dir() / "error.log"
        logger.add(
            str(error_log_path),
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="5 MB",
            retention="60 days",
            compression="zip",
            encoding="utf-8",
            backtrace=True,
            diagnose=True
        )
        
        self._initialized = True
        logger.info("日志系统初始化完成")
    
    def get_logger(self, name: str = None):
        """获取日志记录器"""
        if name:
            return logger.bind(name=name)
        return logger
    
    def set_level(self, level: str):
        """设置日志级别"""
        try:
            # 重新配置日志
            logger.remove()
            self._initialized = False
            
            # 更新配置中的日志级别
            from config import config_manager
            config_manager.update_config(log_level=level)
            
            # 重新初始化
            self.setup_logger()
            logger.info(f"日志级别已更新为: {level}")
        except Exception as e:
            logger.error(f"设置日志级别失败: {e}")
    
    def add_file_handler(self, file_path: str, level: str = "INFO", 
                        rotation: str = "10 MB", retention: str = "30 days"):
        """添加文件处理器"""
        try:
            logger.add(
                file_path,
                level=level,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                rotation=rotation,
                retention=retention,
                compression="zip",
                encoding="utf-8",
                backtrace=True,
                diagnose=True
            )
            logger.info(f"添加文件处理器: {file_path}")
        except Exception as e:
            logger.error(f"添加文件处理器失败: {e}")
    
    def cleanup_old_logs(self, days: int = 30):
        """清理旧日志文件"""
        try:
            import time
            from datetime import datetime, timedelta

            log_dir = get_app_data_dir()
            cutoff_time = time.time() - (days * 24 * 60 * 60)

            cleaned_count = 0
            for log_file in log_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    cleaned_count += 1

            logger.info(f"清理了 {cleaned_count} 个旧日志文件")
        except Exception as e:
            logger.error(f"清理旧日志文件失败: {e}")

    def get_log_stats(self):
        """获取日志统计信息"""
        try:
            log_dir = get_app_data_dir()
            stats = {
                'log_files': [],
                'total_size': 0,
                'total_files': 0
            }

            for log_file in log_dir.glob("*.log*"):
                file_stat = log_file.stat()
                file_info = {
                    'name': log_file.name,
                    'size': file_stat.st_size,
                    'modified': file_stat.st_mtime,
                    'path': str(log_file)
                }
                stats['log_files'].append(file_info)
                stats['total_size'] += file_stat.st_size
                stats['total_files'] += 1

            return stats
        except Exception as e:
            logger.error(f"获取日志统计信息失败: {e}")
            return None

    def export_logs(self, output_path: str, start_date: str = None, end_date: str = None):
        """导出日志文件"""
        try:
            from datetime import datetime
            import zipfile

            log_dir = get_app_data_dir()

            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for log_file in log_dir.glob("*.log*"):
                    # 如果指定了日期范围，检查文件修改时间
                    if start_date or end_date:
                        file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                        if start_date and file_time < datetime.fromisoformat(start_date):
                            continue
                        if end_date and file_time > datetime.fromisoformat(end_date):
                            continue

                    zipf.write(log_file, log_file.name)

            logger.info(f"日志文件已导出到: {output_path}")
            return True
        except Exception as e:
            logger.error(f"导出日志文件失败: {e}")
            return False

    def configure_performance_logging(self, enabled: bool = True):
        """配置性能日志"""
        if enabled:
            perf_log_path = get_app_data_dir() / "performance.log"
            logger.add(
                str(perf_log_path),
                level="DEBUG",
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | PERF | {message}",
                filter=lambda record: "PERF" in record["extra"],
                rotation="5 MB",
                retention="7 days",
                compression="zip",
                encoding="utf-8"
            )
            logger.info("性能日志已启用")
        else:
            logger.info("性能日志已禁用")

    def log_performance(self, operation: str, duration: float, **kwargs):
        """记录性能日志"""
        perf_logger = logger.bind(PERF=True)
        perf_logger.debug(f"{operation} | 耗时: {duration:.3f}s | 详情: {kwargs}")

    def configure_audit_logging(self, enabled: bool = True):
        """配置审计日志"""
        if enabled:
            audit_log_path = get_app_data_dir() / "audit.log"
            logger.add(
                str(audit_log_path),
                level="INFO",
                format="{time:YYYY-MM-DD HH:mm:ss} | AUDIT | {message}",
                filter=lambda record: "AUDIT" in record["extra"],
                rotation="10 MB",
                retention="90 days",
                compression="zip",
                encoding="utf-8"
            )
            logger.info("审计日志已启用")
        else:
            logger.info("审计日志已禁用")

    def log_audit(self, action: str, user: str = "system", details: str = ""):
        """记录审计日志"""
        audit_logger = logger.bind(AUDIT=True)
        audit_logger.info(f"用户: {user} | 操作: {action} | 详情: {details}")


# 全局日志管理器实例
log_manager = LoggerManager()

# 获取应用日志记录器
app_logger = log_manager.get_logger("TimeTrace")


def get_logger(name: str = None):
    """获取日志记录器的便捷函数"""
    return log_manager.get_logger(name)


# 导出常用的日志函数
def debug(message: str, **kwargs):
    """调试日志"""
    app_logger.debug(message, **kwargs)


def info(message: str, **kwargs):
    """信息日志"""
    app_logger.info(message, **kwargs)


def warning(message: str, **kwargs):
    """警告日志"""
    app_logger.warning(message, **kwargs)


def error(message: str, **kwargs):
    """错误日志"""
    app_logger.error(message, **kwargs)


def critical(message: str, **kwargs):
    """严重错误日志"""
    app_logger.critical(message, **kwargs)


def exception(message: str, **kwargs):
    """异常日志（包含堆栈跟踪）"""
    app_logger.exception(message, **kwargs)


# 日志装饰器和上下文管理器
import functools
import time
from contextlib import contextmanager


def log_function_call(level: str = "DEBUG", include_args: bool = False):
    """函数调用日志装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__name__}"

            if include_args:
                args_str = f"args={args}, kwargs={kwargs}"
                app_logger.log(level, f"调用函数: {func_name}({args_str})")
            else:
                app_logger.log(level, f"调用函数: {func_name}")

            try:
                result = func(*args, **kwargs)
                app_logger.log(level, f"函数执行成功: {func_name}")
                return result
            except Exception as e:
                app_logger.error(f"函数执行失败: {func_name}, 错误: {e}")
                raise
        return wrapper
    return decorator


def log_performance_time(operation_name: str = None):
    """性能计时装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                log_manager.log_performance(op_name, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                log_manager.log_performance(f"{op_name}_FAILED", duration, error=str(e))
                raise
        return wrapper
    return decorator


@contextmanager
def log_operation(operation_name: str, level: str = "INFO"):
    """操作日志上下文管理器"""
    app_logger.log(level, f"开始操作: {operation_name}")
    start_time = time.time()

    try:
        yield
        duration = time.time() - start_time
        app_logger.log(level, f"操作完成: {operation_name}, 耗时: {duration:.3f}s")
    except Exception as e:
        duration = time.time() - start_time
        app_logger.error(f"操作失败: {operation_name}, 耗时: {duration:.3f}s, 错误: {e}")
        raise


@contextmanager
def suppress_logs(level: str = "WARNING"):
    """临时抑制日志输出"""
    original_level = logger._core.min_level
    try:
        logger.remove()
        logger.add(sys.stderr, level=level)
        yield
    finally:
        logger.remove()
        log_manager._initialized = False
        log_manager.setup_logger()


# 系统启动日志
info("时迹 (TimeTrace) 日志系统已启动")

# 启用性能和审计日志
log_manager.configure_performance_logging(True)
log_manager.configure_audit_logging(True)
