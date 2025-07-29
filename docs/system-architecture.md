# 时迹（TimeTrace）系统架构设计

## 1. 架构概述

### 1.1 整体架构
时迹采用前后端分离的架构设计，包含以下主要组件：
- **后端服务**：Python应用程序，负责系统事件监听、数据存储和API服务
- **前端界面**：Vue 3 Web应用，提供用户交互界面
- **数据层**：SQLite数据库，存储工时数据
- **系统集成层**：操作系统事件监听和自启动服务

### 1.2 架构原则
- **模块化**：各组件职责清晰，低耦合高内聚
- **可扩展性**：支持功能扩展和平台扩展
- **可靠性**：具备异常处理和数据恢复能力
- **性能优化**：最小化资源占用，快速响应

## 2. 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户界面层                              │
├─────────────────────────────────────────────────────────────┤
│  Web浏览器 (Chrome/Firefox/Safari/Edge)                      │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Vue 3 前端应用                              │ │
│  │  ├─ 工时列表页面    ├─ 统计分析页面                        │ │
│  │  ├─ 数据编辑页面    ├─ 设置配置页面                        │ │
│  │  └─ 数据导出页面    └─ 系统状态页面                        │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │ HTTP API
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        应用服务层                              │
├─────────────────────────────────────────────────────────────┤
│                    Python 后端应用                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐ │
│  │   Web API 服务   │  │  事件监听服务    │  │   数据服务     │ │
│  │  ├─ FastAPI     │  │  ├─ Windows     │  │  ├─ 数据库管理  │ │
│  │  ├─ 路由管理     │  │  ├─ macOS       │  │  ├─ 工时计算   │ │
│  │  └─ 静态文件服务  │  │  └─ Linux       │  │  └─ 数据验证   │ │
│  └─────────────────┘  └─────────────────┘  └───────────────┘ │
│                              │                               │
│  ┌─────────────────┐         │         ┌───────────────────┐ │
│  │   配置管理       │         │         │    日志服务        │ │
│  │  ├─ 系统配置     │         │         │  ├─ 操作日志       │ │
│  │  ├─ 用户设置     │         │         │  ├─ 错误日志       │ │
│  │  └─ 环境变量     │         │         │  └─ 性能日志       │ │
│  └─────────────────┘         │         └───────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        数据存储层                              │
├─────────────────────────────────────────────────────────────┤
│                      SQLite 数据库                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐ │
│  │   工时记录表     │  │    配置表        │  │    日志表      │ │
│  │  ├─ 日期时间     │  │  ├─ 系统配置     │  │  ├─ 操作记录   │ │
│  │  ├─ 上班时间     │  │  ├─ 用户设置     │  │  ├─ 错误记录   │ │
│  │  ├─ 下班时间     │  │  └─ 应用状态     │  │  └─ 性能记录   │ │
│  │  └─ 工作时长     │  └─────────────────┘  └───────────────┘ │
│  └─────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        系统集成层                              │
├─────────────────────────────────────────────────────────────┤
│                      操作系统接口                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐ │
│  │   Windows       │  │     macOS       │  │     Linux     │ │
│  │  ├─ WMI事件      │  │  ├─ NSWorkspace │  │  ├─ D-Bus     │ │
│  │  ├─ Win32 API   │  │  ├─ IOKit       │  │  ├─ systemd   │ │
│  │  └─ 注册表       │  │  └─ LaunchAgent │  │  └─ X11/Wayland│ │
│  └─────────────────┘  └─────────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 3. 核心组件设计

### 3.1 后端服务架构

#### 3.1.1 主程序入口 (main.py)
```python
# 主要职责：
- 程序启动和初始化
- 服务编排和生命周期管理
- 异常处理和恢复
- 优雅关闭
```

#### 3.1.2 Web API 服务 (api.py)
```python
# 基于 FastAPI 的 RESTful API
- GET /api/records - 获取工时记录
- POST /api/records - 创建工时记录
- PUT /api/records/{id} - 更新工时记录
- DELETE /api/records/{id} - 删除工时记录
- GET /api/statistics - 获取统计数据
- GET /api/export - 导出数据
- GET /api/status - 系统状态
```

#### 3.1.3 事件监听服务 (event_listener.py)
```python
# 跨平台事件监听抽象层
class EventListener:
    def start_listening()
    def stop_listening()
    def on_session_lock()
    def on_session_unlock()
    def on_system_shutdown()
    def on_system_startup()

# 平台特定实现
- WindowsEventListener
- MacOSEventListener  
- LinuxEventListener
```

#### 3.1.4 数据服务 (db_manager.py)
```python
# 数据库操作封装
class DatabaseManager:
    def create_tables()
    def insert_record()
    def update_record()
    def delete_record()
    def get_records()
    def get_statistics()
    def backup_data()
    def restore_data()
```

#### 3.1.5 工时计算服务 (time_calculator.py)
```python
# 工时计算逻辑
class TimeCalculator:
    def calculate_duration()
    def handle_missing_checkout()
    def detect_anomalies()
    def auto_complete_records()
```

### 3.2 前端应用架构

#### 3.2.1 组件结构
```
src/
├── components/          # 通用组件
│   ├── TimeChart.vue   # 时间图表组件
│   ├── RecordTable.vue # 记录表格组件
│   └── StatCard.vue    # 统计卡片组件
├── views/              # 页面组件
│   ├── Dashboard.vue   # 仪表板页面
│   ├── Records.vue     # 记录管理页面
│   ├── Statistics.vue  # 统计分析页面
│   └── Settings.vue    # 设置页面
├── store/              # 状态管理
│   ├── index.js        # Vuex/Pinia 配置
│   └── modules/        # 模块化状态
├── api/                # API 接口
│   └── timetrack.js    # 后端API调用
└── utils/              # 工具函数
    ├── date.js         # 日期处理
    └── format.js       # 格式化工具
```

#### 3.2.2 状态管理
```javascript
// 使用 Pinia 进行状态管理
const useTimeStore = defineStore('time', {
  state: () => ({
    records: [],
    statistics: {},
    settings: {},
    loading: false
  }),
  actions: {
    fetchRecords(),
    addRecord(),
    updateRecord(),
    deleteRecord(),
    fetchStatistics()
  }
})
```

### 3.3 数据库设计

#### 3.3.1 工时记录表 (time_records)
```sql
CREATE TABLE time_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    clock_in DATETIME,
    clock_out DATETIME,
    duration INTEGER,  -- 工作时长(分钟)
    status VARCHAR(20) DEFAULT 'normal',  -- normal/abnormal/manual
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 3.3.2 系统配置表 (system_config)
```sql
CREATE TABLE system_config (
    key VARCHAR(50) PRIMARY KEY,
    value TEXT,
    description TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 3.3.3 操作日志表 (operation_logs)
```sql
CREATE TABLE operation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation VARCHAR(50),
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 4. 技术选型

### 4.1 后端技术栈
- **Python 3.8+**：主要开发语言
- **FastAPI**：Web框架，提供高性能API服务
- **SQLite**：轻量级数据库
- **Pydantic**：数据验证和序列化
- **PyInstaller**：程序打包
- **APScheduler**：任务调度

### 4.2 前端技术栈
- **Vue 3**：前端框架
- **Vite**：构建工具
- **Element Plus**：UI组件库
- **ECharts**：图表库
- **Axios**：HTTP客户端
- **Pinia**：状态管理

### 4.3 系统集成技术
- **Windows**：pywin32, WMI
- **macOS**：PyObjC, Cocoa
- **Linux**：python-dbus, systemd

## 5. 部署架构

### 5.1 打包策略
```
TimeTrace.exe (Windows) / TimeTrace.app (macOS) / TimeTrace (Linux)
├── 主程序二进制文件
├── 内嵌Python运行时
├── 依赖库文件
├── 前端静态资源
│   ├── index.html
│   ├── assets/
│   └── static/
├── 数据库文件 (初始化)
└── 配置文件
```

### 5.2 自启动配置
- **Windows**：注册表 HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
- **macOS**：LaunchAgent plist文件
- **Linux**：systemd user service

### 5.3 数据存储位置
- **Windows**：%APPDATA%\TimeTrace\
- **macOS**：~/Library/Application Support/TimeTrace/
- **Linux**：~/.local/share/TimeTrace/

## 6. 安全设计

### 6.1 数据安全
- 本地数据库加密存储
- 敏感配置信息加密
- 定期数据备份

### 6.2 访问控制
- Web服务仅监听本地回环地址
- API接口访问频率限制
- 输入数据验证和过滤

### 6.3 隐私保护
- 不收集用户个人信息
- 不上传任何数据到外部服务器
- 用户数据完全本地化

## 7. 性能优化

### 7.1 后端优化
- 异步IO处理
- 数据库连接池
- 缓存热点数据
- 最小化系统资源占用

### 7.2 前端优化
- 组件懒加载
- 虚拟滚动
- 图片资源优化
- 代码分割和压缩

### 7.3 系统优化
- 事件监听优化
- 内存使用优化
- 启动时间优化
- 响应时间优化
