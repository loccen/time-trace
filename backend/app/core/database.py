"""
数据库连接和管理
"""
import os
import sqlite3
import threading
import time
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
from pathlib import Path

from app.core.logger import get_logger
from app.config.settings import get_config

logger = get_logger("Database")


class DatabaseConnection:
    """数据库连接类"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        self.last_used = time.time()
        self.lock = threading.Lock()
    
    def connect(self):
        """建立数据库连接"""
        if self.connection is None:
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            self.connection.row_factory = sqlite3.Row
            # 启用外键约束
            self.connection.execute("PRAGMA foreign_keys = ON")
            # 设置WAL模式以提高并发性能
            self.connection.execute("PRAGMA journal_mode = WAL")
            # 设置同步模式
            self.connection.execute("PRAGMA synchronous = NORMAL")
        
        self.last_used = time.time()
        return self.connection
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def is_expired(self, timeout: int = 300) -> bool:
        """检查连接是否过期"""
        return time.time() - self.last_used > timeout


class DatabasePool:
    """数据库连接池"""
    
    def __init__(self, db_path: str, pool_size: int = 10, max_overflow: int = 20):
        self.db_path = db_path
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool: List[DatabaseConnection] = []
        self.overflow: List[DatabaseConnection] = []
        self.lock = threading.Lock()
        
        # 初始化连接池
        self._initialize_pool()
        
        # 启动清理线程
        self._start_cleanup_thread()
    
    def _initialize_pool(self):
        """初始化连接池"""
        for _ in range(self.pool_size):
            conn = DatabaseConnection(self.db_path)
            self.pool.append(conn)
    
    def _start_cleanup_thread(self):
        """启动连接清理线程"""
        def cleanup():
            while True:
                time.sleep(60)  # 每分钟清理一次
                self._cleanup_expired_connections()
        
        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()
    
    def _cleanup_expired_connections(self):
        """清理过期连接"""
        with self.lock:
            # 清理溢出连接
            active_overflow = []
            for conn in self.overflow:
                if conn.is_expired():
                    conn.close()
                else:
                    active_overflow.append(conn)
            self.overflow = active_overflow
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接（上下文管理器）"""
        conn = None
        try:
            conn = self._acquire_connection()
            yield conn.connect()
        finally:
            if conn:
                self._release_connection(conn)
    
    def _acquire_connection(self) -> DatabaseConnection:
        """获取连接"""
        with self.lock:
            # 尝试从池中获取连接
            if self.pool:
                return self.pool.pop()
            
            # 池中无可用连接，尝试创建溢出连接
            if len(self.overflow) < self.max_overflow:
                conn = DatabaseConnection(self.db_path)
                self.overflow.append(conn)
                return conn
            
            # 无法获取连接，等待
            raise Exception("数据库连接池已满，无法获取连接")
    
    def _release_connection(self, conn: DatabaseConnection):
        """释放连接"""
        with self.lock:
            if conn in self.overflow:
                # 溢出连接直接关闭
                self.overflow.remove(conn)
                conn.close()
            else:
                # 返回到池中
                if len(self.pool) < self.pool_size:
                    self.pool.append(conn)
                else:
                    conn.close()
    
    def close_all(self):
        """关闭所有连接"""
        with self.lock:
            for conn in self.pool + self.overflow:
                conn.close()
            self.pool.clear()
            self.overflow.clear()


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.db_path = self._get_db_path()
        self.pool = None
        self._initialize_pool()
    
    def _get_db_path(self) -> str:
        """获取数据库路径"""
        db_url = get_config("database.url", "sqlite:///data/time_trace.db")
        if db_url.startswith("sqlite:///"):
            db_path = db_url[10:]  # 移除 "sqlite:///" 前缀

            # 确保数据库目录存在
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                logger.info(f"创建数据库目录: {db_dir}")

            return db_path
        return "data/time_trace.db"
    
    def _initialize_pool(self):
        """初始化连接池"""
        pool_size = get_config("database.pool_size", 10)
        max_overflow = get_config("database.max_overflow", 20)
        
        self.pool = DatabasePool(self.db_path, pool_size, max_overflow)
        logger.info(f"数据库连接池初始化完成: {self.db_path}")
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """执行查询语句"""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"执行查询失败: {query}, 参数: {params}, 错误: {e}")
            raise
    
    def execute_insert(self, query: str, params: Tuple = ()) -> int:
        """执行插入语句，返回插入的行ID"""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.execute(query, params)
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"执行插入失败: {query}, 参数: {params}, 错误: {e}")
            raise
    
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """执行更新语句，返回影响的行数"""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.execute(query, params)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"执行更新失败: {query}, 参数: {params}, 错误: {e}")
            raise
    
    def execute_script(self, script: str):
        """执行SQL脚本"""
        try:
            with self.pool.get_connection() as conn:
                conn.executescript(script)
                conn.commit()
                logger.info("SQL脚本执行成功")
        except Exception as e:
            logger.error(f"执行SQL脚本失败: {e}")
            raise
    
    def begin_transaction(self):
        """开始事务"""
        return self.pool.get_connection()
    
    def check_connection(self) -> bool:
        """检查数据库连接"""
        try:
            self.execute_query("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"数据库连接检查失败: {e}")
            return False
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """获取表结构信息"""
        try:
            query = f"PRAGMA table_info({table_name})"
            return self.execute_query(query)
        except Exception as e:
            logger.error(f"获取表信息失败: {table_name}, 错误: {e}")
            return []
    
    def get_all_tables(self) -> List[str]:
        """获取所有表名"""
        try:
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            rows = self.execute_query(query)
            return [row['name'] for row in rows]
        except Exception as e:
            logger.error(f"获取表列表失败: {e}")
            return []
    
    def backup_database(self, backup_path: str):
        """备份数据库"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"数据库备份成功: {backup_path}")
        except Exception as e:
            logger.error(f"数据库备份失败: {e}")
            raise
    
    def close(self):
        """关闭数据库管理器"""
        if self.pool:
            self.pool.close_all()
            logger.info("数据库连接池已关闭")


# 全局数据库管理器实例
db_manager = DatabaseManager()


# 便捷函数
def get_db_manager() -> DatabaseManager:
    """获取数据库管理器实例"""
    return db_manager


def execute_query(query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
    """执行查询的便捷函数"""
    return db_manager.execute_query(query, params)


def execute_insert(query: str, params: Tuple = ()) -> int:
    """执行插入的便捷函数"""
    return db_manager.execute_insert(query, params)


def execute_update(query: str, params: Tuple = ()) -> int:
    """执行更新的便捷函数"""
    return db_manager.execute_update(query, params)
