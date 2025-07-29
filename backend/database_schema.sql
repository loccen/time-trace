-- 时迹 (TimeTrace) 数据库表结构设计
-- SQLite 数据库

-- 启用外键约束
PRAGMA foreign_keys = ON;

-- 工时记录表
CREATE TABLE IF NOT EXISTS time_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,                          -- 日期 (YYYY-MM-DD)
    clock_in DATETIME,                           -- 上班时间
    clock_out DATETIME,                          -- 下班时间
    duration INTEGER DEFAULT 0,                  -- 工作时长(分钟)
    break_duration INTEGER DEFAULT 0,            -- 休息时长(分钟)
    overtime_duration INTEGER DEFAULT 0,         -- 加班时长(分钟)
    status VARCHAR(20) DEFAULT 'normal',         -- 状态: normal/abnormal/manual/incomplete
    notes TEXT,                                  -- 备注
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 约束
    UNIQUE(date),                                -- 每天只能有一条记录
    CHECK(status IN ('normal', 'abnormal', 'manual', 'incomplete')),
    CHECK(duration >= 0),
    CHECK(break_duration >= 0),
    CHECK(overtime_duration >= 0)
);

-- 系统事件记录表
CREATE TABLE IF NOT EXISTS system_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type VARCHAR(20) NOT NULL,             -- 事件类型: lock/unlock/shutdown/startup
    event_time DATETIME NOT NULL,               -- 事件时间
    event_source VARCHAR(50),                   -- 事件来源: system/manual
    details TEXT,                               -- 事件详情
    processed BOOLEAN DEFAULT FALSE,            -- 是否已处理
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 约束
    CHECK(event_type IN ('lock', 'unlock', 'shutdown', 'startup', 'suspend', 'resume')),
    CHECK(event_source IN ('system', 'manual', 'auto'))
);

-- 系统配置表
CREATE TABLE IF NOT EXISTS system_config (
    key VARCHAR(50) PRIMARY KEY,
    value TEXT,
    description TEXT,
    data_type VARCHAR(20) DEFAULT 'string',     -- 数据类型: string/integer/boolean/json
    category VARCHAR(30) DEFAULT 'general',     -- 配置分类
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 约束
    CHECK(data_type IN ('string', 'integer', 'boolean', 'json', 'float')),
    CHECK(category IN ('general', 'work', 'reminder', 'system', 'ui'))
);

-- 操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation VARCHAR(50) NOT NULL,             -- 操作类型
    operator VARCHAR(50) DEFAULT 'system',      -- 操作者
    target_type VARCHAR(30),                    -- 目标类型: record/config/system
    target_id INTEGER,                          -- 目标ID
    old_value TEXT,                             -- 旧值(JSON格式)
    new_value TEXT,                             -- 新值(JSON格式)
    details TEXT,                               -- 操作详情
    ip_address VARCHAR(45),                     -- IP地址
    user_agent TEXT,                            -- 用户代理
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 约束
    CHECK(target_type IN ('record', 'config', 'system', 'user'))
);

-- 统计数据表 (用于缓存计算结果)
CREATE TABLE IF NOT EXISTS statistics_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stat_type VARCHAR(30) NOT NULL,             -- 统计类型: daily/weekly/monthly/yearly
    stat_date DATE NOT NULL,                    -- 统计日期
    stat_data TEXT NOT NULL,                    -- 统计数据(JSON格式)
    expires_at DATETIME,                        -- 过期时间
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 约束
    UNIQUE(stat_type, stat_date),
    CHECK(stat_type IN ('daily', 'weekly', 'monthly', 'yearly', 'custom'))
);

-- 数据备份记录表
CREATE TABLE IF NOT EXISTS backup_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    backup_type VARCHAR(20) NOT NULL,           -- 备份类型: full/incremental
    backup_path TEXT NOT NULL,                  -- 备份文件路径
    backup_size INTEGER,                        -- 备份文件大小(字节)
    backup_status VARCHAR(20) DEFAULT 'pending', -- 备份状态: pending/success/failed
    error_message TEXT,                         -- 错误信息
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    
    -- 约束
    CHECK(backup_type IN ('full', 'incremental', 'manual')),
    CHECK(backup_status IN ('pending', 'running', 'success', 'failed', 'cancelled'))
);

-- 数据库版本表
CREATE TABLE IF NOT EXISTS schema_versions (
    version INTEGER PRIMARY KEY,
    description TEXT,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
-- 工时记录表索引
CREATE INDEX IF NOT EXISTS idx_time_records_date ON time_records(date);
CREATE INDEX IF NOT EXISTS idx_time_records_status ON time_records(status);
CREATE INDEX IF NOT EXISTS idx_time_records_created_at ON time_records(created_at);

-- 系统事件表索引
CREATE INDEX IF NOT EXISTS idx_system_events_type ON system_events(event_type);
CREATE INDEX IF NOT EXISTS idx_system_events_time ON system_events(event_time);
CREATE INDEX IF NOT EXISTS idx_system_events_processed ON system_events(processed);

-- 操作日志表索引
CREATE INDEX IF NOT EXISTS idx_operation_logs_operation ON operation_logs(operation);
CREATE INDEX IF NOT EXISTS idx_operation_logs_timestamp ON operation_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_operation_logs_target ON operation_logs(target_type, target_id);

-- 统计缓存表索引
CREATE INDEX IF NOT EXISTS idx_statistics_cache_type_date ON statistics_cache(stat_type, stat_date);
CREATE INDEX IF NOT EXISTS idx_statistics_cache_expires ON statistics_cache(expires_at);

-- 备份记录表索引
CREATE INDEX IF NOT EXISTS idx_backup_records_status ON backup_records(backup_status);
CREATE INDEX IF NOT EXISTS idx_backup_records_created ON backup_records(created_at);

-- 插入初始数据
-- 数据库版本
INSERT OR IGNORE INTO schema_versions (version, description) VALUES (1, '初始数据库结构');

-- 默认系统配置
INSERT OR IGNORE INTO system_config (key, value, description, data_type, category) VALUES
('app_version', '1.0.0', '应用版本', 'string', 'general'),
('standard_work_hours', '8', '标准工作时长(小时)', 'integer', 'work'),
('lunch_break_start', '12:00', '午休开始时间', 'string', 'work'),
('lunch_break_end', '13:00', '午休结束时间', 'string', 'work'),
('overtime_threshold', '9', '加班提醒阈值(小时)', 'integer', 'reminder'),
('enable_work_reminder', 'false', '启用上下班提醒', 'boolean', 'reminder'),
('enable_overtime_reminder', 'false', '启用加班提醒', 'boolean', 'reminder'),
('auto_startup', 'true', '开机自启动', 'boolean', 'system'),
('minimize_to_tray', 'true', '最小化到系统托盘', 'boolean', 'system'),
('log_level', 'INFO', '日志级别', 'string', 'system'),
('backup_retention_days', '30', '备份保留天数', 'integer', 'system'),
('auto_backup_enabled', 'true', '启用自动备份', 'boolean', 'system');

-- 创建触发器
-- 更新时间戳触发器
CREATE TRIGGER IF NOT EXISTS update_time_records_timestamp 
    AFTER UPDATE ON time_records
    FOR EACH ROW
BEGIN
    UPDATE time_records SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_statistics_cache_timestamp 
    AFTER UPDATE ON statistics_cache
    FOR EACH ROW
BEGIN
    UPDATE statistics_cache SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- 数据完整性触发器
CREATE TRIGGER IF NOT EXISTS validate_time_record_duration
    BEFORE INSERT ON time_records
    FOR EACH ROW
    WHEN NEW.clock_in IS NOT NULL AND NEW.clock_out IS NOT NULL
BEGIN
    UPDATE time_records SET duration = 
        CAST((julianday(NEW.clock_out) - julianday(NEW.clock_in)) * 24 * 60 AS INTEGER)
    WHERE id = NEW.id;
END;

-- 自动清理过期统计缓存触发器
CREATE TRIGGER IF NOT EXISTS cleanup_expired_statistics
    AFTER INSERT ON statistics_cache
    FOR EACH ROW
BEGIN
    DELETE FROM statistics_cache 
    WHERE expires_at IS NOT NULL AND expires_at < CURRENT_TIMESTAMP;
END;
