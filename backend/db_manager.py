"""
数据库管理模块
"""
import sqlite3
import threading
import time
from contextlib import contextmanager
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from queue import Queue, Empty
from dataclasses import dataclass
from datetime import datetime

from config import settings
from logger import get_logger
from database_init import initialize_database

logger = get_logger("DatabaseManager")


@dataclass
class ConnectionInfo:
    """连接信息"""
    connection: sqlite3.Connection
    created_at: float
    last_used: float
    in_use: bool = False
    thread_id: Optional[int] = None


class DatabaseConnectionPool:
    """数据库连接池"""

    def __init__(self, db_path: str, max_connections: int = 10,
                 connection_timeout: int = 30, idle_timeout: int = 300):
        self.db_path = db_path
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.idle_timeout = idle_timeout

        self._pool: Queue = Queue(maxsize=max_connections)
        self._connections: Dict[int, ConnectionInfo] = {}
        self._lock = threading.RLock()
        self._closed = False

        # 初始化数据库
        if not Path(db_path).exists():
            logger.info("数据库文件不存在，开始初始化")
            if not initialize_database(db_path):
                raise RuntimeError("数据库初始化失败")

        # 创建初始连接
        self._create_initial_connections()

        # 启动清理线程
        self._cleanup_thread = threading.Thread(target=self._cleanup_idle_connections, daemon=True)
        self._cleanup_thread.start()

        logger.info(f"数据库连接池已初始化，最大连接数: {max_connections}")

    def _create_initial_connections(self):
        """创建初始连接"""
        initial_count = min(3, self.max_connections)
        for _ in range(initial_count):
            try:
                conn = self._create_connection()
                conn_info = ConnectionInfo(
                    connection=conn,
                    created_at=time.time(),
                    last_used=time.time()
                )
                self._pool.put(conn_info, block=False)
            except Exception as e:
                logger.error(f"创建初始连接失败: {e}")

    def _create_connection(self) -> sqlite3.Connection:
        """创建新的数据库连接"""
        try:
            conn = sqlite3.connect(
                self.db_path,
                timeout=self.connection_timeout,
                check_same_thread=False
            )

            # 设置连接参数
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
            conn.execute("PRAGMA temp_store = MEMORY")

            # 设置行工厂
            conn.row_factory = sqlite3.Row

            return conn

        except Exception as e:
            logger.error(f"创建数据库连接失败: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        if self._closed:
            raise RuntimeError("连接池已关闭")

        conn_info = None
        try:
            # 尝试从池中获取连接
            try:
                conn_info = self._pool.get(timeout=5)
                conn_info.last_used = time.time()
                conn_info.in_use = True
                conn_info.thread_id = threading.get_ident()

                # 测试连接是否有效
                conn_info.connection.execute("SELECT 1")

            except (Empty, sqlite3.Error):
                # 池中没有可用连接或连接无效，创建新连接
                if len(self._connections) < self.max_connections:
                    conn = self._create_connection()
                    conn_info = ConnectionInfo(
                        connection=conn,
                        created_at=time.time(),
                        last_used=time.time(),
                        in_use=True,
                        thread_id=threading.get_ident()
                    )
                else:
                    raise RuntimeError("连接池已满，无法创建新连接")

            with self._lock:
                self._connections[id(conn_info)] = conn_info

            yield conn_info.connection

        except Exception as e:
            logger.error(f"获取数据库连接失败: {e}")
            raise
        finally:
            if conn_info:
                conn_info.in_use = False
                conn_info.thread_id = None

                try:
                    # 回滚未提交的事务
                    conn_info.connection.rollback()

                    # 将连接放回池中
                    self._pool.put(conn_info, block=False)
                except Exception as e:
                    logger.warning(f"归还连接到池中失败: {e}")
                    # 关闭有问题的连接
                    try:
                        conn_info.connection.close()
                    except:
                        pass

                    with self._lock:
                        if id(conn_info) in self._connections:
                            del self._connections[id(conn_info)]

    def _cleanup_idle_connections(self):
        """清理空闲连接"""
        while not self._closed:
            try:
                time.sleep(60)  # 每分钟检查一次

                current_time = time.time()
                to_remove = []

                with self._lock:
                    for conn_id, conn_info in self._connections.items():
                        if (not conn_info.in_use and
                            current_time - conn_info.last_used > self.idle_timeout):
                            to_remove.append(conn_id)

                # 关闭空闲连接
                for conn_id in to_remove:
                    with self._lock:
                        if conn_id in self._connections:
                            conn_info = self._connections[conn_id]
                            try:
                                conn_info.connection.close()
                            except:
                                pass
                            del self._connections[conn_id]
                            logger.debug(f"已清理空闲连接: {conn_id}")

            except Exception as e:
                logger.error(f"清理空闲连接时出错: {e}")

    def close(self):
        """关闭连接池"""
        self._closed = True

        with self._lock:
            # 关闭所有连接
            for conn_info in self._connections.values():
                try:
                    conn_info.connection.close()
                except:
                    pass

            self._connections.clear()

            # 清空池
            while not self._pool.empty():
                try:
                    self._pool.get_nowait()
                except Empty:
                    break

        logger.info("数据库连接池已关闭")

    def get_stats(self) -> Dict[str, Any]:
        """获取连接池统计信息"""
        with self._lock:
            active_connections = sum(1 for info in self._connections.values() if info.in_use)
            total_connections = len(self._connections)

            return {
                'total_connections': total_connections,
                'active_connections': active_connections,
                'idle_connections': total_connections - active_connections,
                'max_connections': self.max_connections,
                'pool_size': self._pool.qsize()
            }


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            # 从配置中获取数据库路径
            db_url = settings.database_url
            db_path = db_url.replace("sqlite:///", "")

        self.db_path = db_path
        self._pool = DatabaseConnectionPool(db_path)

        logger.info(f"数据库管理器已初始化: {db_path}")

    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        with self._pool.get_connection() as conn:
            yield conn

    def execute_query(self, query: str, params: tuple = None) -> List[sqlite3.Row]:
        """执行查询语句"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params or ())
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"执行查询失败: {query}, 参数: {params}, 错误: {e}")
            raise

    def execute_update(self, query: str, params: tuple = None) -> int:
        """执行更新语句"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params or ())
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"执行更新失败: {query}, 参数: {params}, 错误: {e}")
            raise

    def execute_insert(self, query: str, params: tuple = None) -> int:
        """执行插入语句，返回新记录的ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params or ())
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"执行插入失败: {query}, 参数: {params}, 错误: {e}")
            raise

    def execute_batch(self, query: str, params_list: List[tuple]) -> int:
        """批量执行语句"""
        try:
            with self.get_connection() as conn:
                cursor = conn.executemany(query, params_list)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"批量执行失败: {query}, 错误: {e}")
            raise

    def execute_transaction(self, operations: List[Tuple[str, tuple]]) -> bool:
        """执行事务"""
        try:
            with self.get_connection() as conn:
                for query, params in operations:
                    conn.execute(query, params or ())
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"执行事务失败: {e}")
            raise

    def get_table_info(self, table_name: str) -> List[sqlite3.Row]:
        """获取表结构信息"""
        return self.execute_query(f"PRAGMA table_info({table_name})")

    def get_table_list(self) -> List[str]:
        """获取所有表名"""
        rows = self.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        return [row['name'] for row in rows]

    def get_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        stats = self._pool.get_stats()

        # 添加数据库文件信息
        db_file = Path(self.db_path)
        if db_file.exists():
            stats['db_file_size'] = db_file.stat().st_size
            stats['db_file_modified'] = db_file.stat().st_mtime

        # 添加表统计信息
        try:
            tables = self.get_table_list()
            stats['table_count'] = len(tables)
            stats['tables'] = tables
        except Exception as e:
            logger.warning(f"获取表信息失败: {e}")

        return stats

    def close(self):
        """关闭数据库管理器"""
        self._pool.close()
        logger.info("数据库管理器已关闭")


# 全局数据库管理器实例
db_manager = DatabaseManager()
