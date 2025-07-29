"""
数据库初始化脚本
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import db_manager
from app.core.logger import get_logger

logger = get_logger("DatabaseInit")


def create_tables():
    """创建数据库表"""
    
    # 工时记录表
    time_records_sql = """
    CREATE TABLE IF NOT EXISTS time_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL UNIQUE,
        clock_in TEXT,
        clock_out TEXT,
        duration INTEGER DEFAULT 0,
        break_duration INTEGER DEFAULT 0,
        overtime_duration INTEGER DEFAULT 0,
        status TEXT DEFAULT 'normal',
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # 系统事件表
    system_events_sql = """
    CREATE TABLE IF NOT EXISTS system_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT NOT NULL,
        event_time TEXT NOT NULL,
        event_source TEXT DEFAULT 'system',
        details TEXT,
        processed BOOLEAN DEFAULT FALSE,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # 系统配置表
    system_config_sql = """
    CREATE TABLE IF NOT EXISTS system_config (
        key TEXT PRIMARY KEY,
        value TEXT,
        description TEXT,
        data_type TEXT DEFAULT 'string',
        category TEXT DEFAULT 'general',
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # 操作日志表
    operation_logs_sql = """
    CREATE TABLE IF NOT EXISTS operation_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        operation TEXT NOT NULL,
        operator TEXT DEFAULT 'system',
        target_type TEXT,
        target_id INTEGER,
        old_value TEXT,
        new_value TEXT,
        details TEXT,
        ip_address TEXT,
        user_agent TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # 创建索引
    indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_time_records_date ON time_records(date);",
        "CREATE INDEX IF NOT EXISTS idx_system_events_type ON system_events(event_type);",
        "CREATE INDEX IF NOT EXISTS idx_system_events_time ON system_events(event_time);",
        "CREATE INDEX IF NOT EXISTS idx_system_events_processed ON system_events(processed);",
        "CREATE INDEX IF NOT EXISTS idx_operation_logs_operation ON operation_logs(operation);",
        "CREATE INDEX IF NOT EXISTS idx_operation_logs_timestamp ON operation_logs(timestamp);"
    ]
    
    try:
        # 创建表
        db_manager.execute_script(time_records_sql)
        logger.info("工时记录表创建成功")
        
        db_manager.execute_script(system_events_sql)
        logger.info("系统事件表创建成功")
        
        db_manager.execute_script(system_config_sql)
        logger.info("系统配置表创建成功")
        
        db_manager.execute_script(operation_logs_sql)
        logger.info("操作日志表创建成功")
        
        # 创建索引
        for index_sql in indexes_sql:
            db_manager.execute_script(index_sql)
        
        logger.info("数据库索引创建成功")
        
    except Exception as e:
        logger.error(f"创建数据库表失败: {e}")
        raise


def insert_default_config():
    """插入默认配置"""
    
    default_configs = [
        ("work.standard_hours", "8.0", "标准工作时长（小时）", "float", "work"),
        ("work.max_daily_hours", "12.0", "每日最大工作时长（小时）", "float", "work"),
        ("work.overtime_threshold", "8.0", "加班时长阈值（小时）", "float", "work"),
        ("work.start_time", "09:00", "标准上班时间", "time", "work"),
        ("work.end_time", "18:00", "标准下班时间", "time", "work"),
        ("work.lunch_start", "12:00", "午休开始时间", "time", "work"),
        ("work.lunch_end", "13:00", "午休结束时间", "time", "work"),
        ("event.enabled_types", '["LOCK","UNLOCK","STARTUP","SHUTDOWN","SUSPEND","RESUME"]', "启用的事件类型", "json", "event"),
        ("event.min_intervals", '{"LOCK":5.0,"UNLOCK":5.0,"SUSPEND":10.0,"RESUME":10.0}', "事件最小间隔（秒）", "json", "event"),
        ("app.name", "时迹工时追踪系统", "应用程序名称", "string", "app"),
        ("app.version", "1.0.0", "应用程序版本", "string", "app"),
        ("logging.level", "INFO", "日志级别", "string", "logging"),
        ("logging.file_enabled", "true", "是否启用文件日志", "boolean", "logging"),
        ("database.backup_enabled", "true", "是否启用数据库备份", "boolean", "database"),
        ("database.backup_interval", "24", "数据库备份间隔（小时）", "integer", "database")
    ]
    
    try:
        for key, value, description, data_type, category in default_configs:
            # 检查配置是否已存在
            existing = db_manager.execute_query(
                "SELECT key FROM system_config WHERE key = ?", (key,)
            )
            
            if not existing:
                db_manager.execute_insert(
                    """
                    INSERT INTO system_config (key, value, description, data_type, category)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (key, value, description, data_type, category)
                )
        
        logger.info("默认配置插入成功")
        
    except Exception as e:
        logger.error(f"插入默认配置失败: {e}")
        raise


def verify_database():
    """验证数据库结构"""
    
    required_tables = [
        "time_records",
        "system_events", 
        "system_config",
        "operation_logs"
    ]
    
    try:
        existing_tables = db_manager.get_all_tables()
        
        for table in required_tables:
            if table not in existing_tables:
                raise Exception(f"缺少必需的表: {table}")
        
        logger.info("数据库结构验证成功")
        
        # 验证配置表
        config_count = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM system_config"
        )[0]['count']
        
        logger.info(f"系统配置表包含 {config_count} 条记录")
        
    except Exception as e:
        logger.error(f"数据库结构验证失败: {e}")
        raise


def init_database():
    """初始化数据库"""
    try:
        logger.info("开始初始化数据库...")
        
        # 检查数据库连接
        if not db_manager.check_connection():
            raise Exception("数据库连接失败")
        
        # 创建表
        create_tables()
        
        # 插入默认配置
        insert_default_config()
        
        # 验证数据库
        verify_database()
        
        logger.info("数据库初始化完成")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


def main():
    """主函数"""
    try:
        init_database()
        print("数据库初始化成功！")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
