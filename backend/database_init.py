"""
数据库初始化模块
"""
import sqlite3
import os
from pathlib import Path
from typing import Optional
from logger import get_logger

logger = get_logger("DatabaseInit")


class DatabaseInitializer:
    """数据库初始化器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.schema_file = Path(__file__).parent / "database_schema.sql"
    
    def initialize_database(self) -> bool:
        """初始化数据库"""
        try:
            logger.info(f"开始初始化数据库: {self.db_path}")
            
            # 确保数据库目录存在
            db_dir = Path(self.db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            # 检查数据库是否已存在
            db_exists = Path(self.db_path).exists()
            
            # 连接数据库
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                
                if not db_exists:
                    logger.info("创建新数据库")
                    self._create_schema(conn)
                else:
                    logger.info("数据库已存在，检查版本")
                    self._check_and_upgrade_schema(conn)
                
                # 验证数据库结构
                if self._validate_schema(conn):
                    logger.info("数据库初始化成功")
                    return True
                else:
                    logger.error("数据库结构验证失败")
                    return False
                    
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            return False
    
    def _create_schema(self, conn: sqlite3.Connection):
        """创建数据库结构"""
        try:
            # 读取SQL脚本
            if not self.schema_file.exists():
                raise FileNotFoundError(f"数据库结构文件不存在: {self.schema_file}")
            
            with open(self.schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # 执行SQL脚本
            conn.executescript(schema_sql)
            conn.commit()
            
            logger.info("数据库结构创建完成")
            
        except Exception as e:
            logger.error(f"创建数据库结构失败: {e}")
            raise
    
    def _check_and_upgrade_schema(self, conn: sqlite3.Connection):
        """检查并升级数据库结构"""
        try:
            # 获取当前数据库版本
            current_version = self._get_current_version(conn)
            target_version = self._get_target_version()
            
            logger.info(f"当前数据库版本: {current_version}, 目标版本: {target_version}")
            
            if current_version < target_version:
                logger.info("需要升级数据库")
                self._upgrade_schema(conn, current_version, target_version)
            elif current_version > target_version:
                logger.warning("数据库版本高于目标版本，可能存在兼容性问题")
            else:
                logger.info("数据库版本已是最新")
                
        except Exception as e:
            logger.error(f"检查数据库版本失败: {e}")
            raise
    
    def _get_current_version(self, conn: sqlite3.Connection) -> int:
        """获取当前数据库版本"""
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_versions'"
            )
            if cursor.fetchone() is None:
                return 0
            
            cursor = conn.execute("SELECT MAX(version) FROM schema_versions")
            result = cursor.fetchone()
            return result[0] if result[0] is not None else 0
            
        except Exception:
            return 0
    
    def _get_target_version(self) -> int:
        """获取目标数据库版本"""
        # 从schema文件中解析版本信息，这里简化为固定值
        return 1
    
    def _upgrade_schema(self, conn: sqlite3.Connection, from_version: int, to_version: int):
        """升级数据库结构"""
        try:
            logger.info(f"升级数据库从版本 {from_version} 到 {to_version}")
            
            # 这里可以添加具体的升级逻辑
            # 例如：执行特定的升级SQL脚本
            
            # 如果是从版本0升级，直接创建完整结构
            if from_version == 0:
                self._create_schema(conn)
            else:
                # 执行增量升级
                self._apply_incremental_upgrades(conn, from_version, to_version)
            
            logger.info("数据库升级完成")
            
        except Exception as e:
            logger.error(f"数据库升级失败: {e}")
            raise
    
    def _apply_incremental_upgrades(self, conn: sqlite3.Connection, from_version: int, to_version: int):
        """应用增量升级"""
        # 这里可以添加版本间的增量升级逻辑
        # 例如：
        # if from_version < 2 and to_version >= 2:
        #     self._upgrade_to_version_2(conn)
        pass
    
    def _validate_schema(self, conn: sqlite3.Connection) -> bool:
        """验证数据库结构"""
        try:
            required_tables = [
                'time_records',
                'system_events', 
                'system_config',
                'operation_logs',
                'statistics_cache',
                'backup_records',
                'schema_versions'
            ]
            
            # 检查必需的表是否存在
            for table in required_tables:
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (table,)
                )
                if cursor.fetchone() is None:
                    logger.error(f"缺少必需的表: {table}")
                    return False
            
            # 检查关键索引是否存在
            required_indexes = [
                'idx_time_records_date',
                'idx_system_events_time',
                'idx_operation_logs_timestamp'
            ]
            
            for index in required_indexes:
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='index' AND name=?",
                    (index,)
                )
                if cursor.fetchone() is None:
                    logger.warning(f"缺少索引: {index}")
            
            logger.info("数据库结构验证通过")
            return True
            
        except Exception as e:
            logger.error(f"数据库结构验证失败: {e}")
            return False
    
    def backup_database(self, backup_path: str) -> bool:
        """备份数据库"""
        try:
            import shutil
            
            if not Path(self.db_path).exists():
                logger.error("源数据库文件不存在")
                return False
            
            # 确保备份目录存在
            backup_dir = Path(backup_path).parent
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # 复制数据库文件
            shutil.copy2(self.db_path, backup_path)
            
            logger.info(f"数据库备份完成: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"数据库备份失败: {e}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """恢复数据库"""
        try:
            import shutil
            
            if not Path(backup_path).exists():
                logger.error("备份文件不存在")
                return False
            
            # 备份当前数据库
            if Path(self.db_path).exists():
                current_backup = f"{self.db_path}.backup"
                shutil.copy2(self.db_path, current_backup)
                logger.info(f"当前数据库已备份到: {current_backup}")
            
            # 恢复数据库
            shutil.copy2(backup_path, self.db_path)
            
            # 验证恢复的数据库
            if self._validate_restored_database():
                logger.info(f"数据库恢复完成: {backup_path}")
                return True
            else:
                logger.error("恢复的数据库验证失败")
                return False
                
        except Exception as e:
            logger.error(f"数据库恢复失败: {e}")
            return False
    
    def _validate_restored_database(self) -> bool:
        """验证恢复的数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                return self._validate_schema(conn)
        except Exception as e:
            logger.error(f"验证恢复的数据库失败: {e}")
            return False


def initialize_database(db_path: str) -> bool:
    """初始化数据库的便捷函数"""
    initializer = DatabaseInitializer(db_path)
    return initializer.initialize_database()


if __name__ == "__main__":
    # 测试数据库初始化
    try:
        from config import get_database_path

        db_url = get_database_path()
        # 从SQLite URL中提取文件路径
        db_path = db_url.replace("sqlite:///", "")

        # 写入测试日志
        with open("db_init_test.log", "w", encoding="utf-8") as f:
            f.write(f"Database path: {db_path}\n")
            f.write("Starting database initialization...\n")

            success = initialize_database(db_path)

            if success:
                f.write("Database initialization successful\n")
            else:
                f.write("Database initialization failed\n")

            # 验证数据库文件是否存在
            import os
            if os.path.exists(db_path):
                f.write(f"Database file created: {db_path}\n")
                f.write(f"File size: {os.path.getsize(db_path)} bytes\n")

                # 检查表结构
                import sqlite3
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]
                    f.write(f"Tables: {tables}\n")
            else:
                f.write("Database file not created\n")

    except Exception as e:
        with open("db_init_error.log", "w", encoding="utf-8") as f:
            f.write(f"Error: {e}\n")
            import traceback
            f.write(traceback.format_exc())
