# 时迹 (TimeTrace)

一个本地离线使用的个人工时记录软件，通过自动监听系统事件来记录工作时间，并提供现代化的Web界面进行数据管理和分析。

## 🚀 功能特性

### 核心功能
- **自动工时记录**：监听系统锁定/解锁事件，自动记录上下班时间
- **智能数据处理**：自动处理异常情况，智能补齐缺失数据
- **本地数据存储**：使用SQLite数据库，数据完全本地化
- **后台静默运行**：无界面后台运行，不干扰日常工作

### 用户界面
- **现代化Web界面**：基于Vue 3的响应式Web界面
- **数据可视化**：丰富的图表展示工时趋势和统计信息
- **数据管理**：支持工时记录的增删改查操作
- **数据导出**：支持CSV格式数据导出

### 系统集成
- **跨平台支持**：支持Windows、macOS、Linux
- **开机自启动**：程序自动随系统启动
- **单文件部署**：打包为单个可执行文件，无需安装

## 📋 系统要求

- **操作系统**：Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **浏览器**：Chrome, Firefox, Safari, Edge (最新版本)
- **权限**：需要系统事件监听权限

## 🏗️ 技术架构

### 后端技术栈
- **Python 3.8+**：主要开发语言
- **FastAPI**：Web框架和API服务
- **SQLite**：本地数据库
- **PyInstaller**：程序打包

### 前端技术栈
- **Vue 3**：前端框架
- **Element Plus**：UI组件库
- **ECharts**：数据可视化
- **Vite**：构建工具

### 系统集成
- **Windows**：pywin32, WMI
- **macOS**：PyObjC, Cocoa
- **Linux**：python-dbus, systemd

## 📁 项目结构

```
time-trace/
├── backend/                 # 后端Python应用
│   ├── main.py             # 主程序入口
│   ├── api.py              # Web API路由
│   ├── event_listener.py   # 系统事件监听
│   ├── db_manager.py       # 数据库管理
│   ├── time_calculator.py  # 工时计算
│   ├── config.py           # 配置管理
│   └── utils/              # 工具模块
├── frontend/               # 前端Vue应用
│   ├── src/                # 源代码
│   ├── public/             # 静态资源
│   ├── package.json        # 依赖配置
│   └── vite.config.js      # 构建配置
├── docs/                   # 项目文档
│   ├── requirements-analysis.md
│   ├── system-architecture.md
│   └── ui-prototype-design.md
├── scripts/                # 构建和部署脚本
│   ├── build.py           # 构建脚本
│   └── package.py         # 打包脚本
├── tests/                  # 测试代码
│   ├── backend/           # 后端测试
│   └── frontend/          # 前端测试
└── README.md              # 项目说明
```

## 🚀 快速开始

### 开发环境搭建

1. **克隆项目**
```bash
git clone https://github.com/your-username/time-trace.git
cd time-trace
```

2. **后端环境**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

3. **前端环境**
```bash
cd frontend
npm install
npm run dev
```

4. **访问应用**
打开浏览器访问 `http://localhost:5000`

### 生产环境部署

1. **构建前端**
```bash
cd frontend
npm run build
```

2. **打包应用**
```bash
cd scripts
python build.py
```

3. **运行程序**
运行生成的可执行文件即可

## 📖 使用说明

### 首次使用
1. 运行程序后，会自动在系统托盘显示图标
2. 程序会自动监听系统事件，开始记录工时
3. 双击托盘图标或访问 `http://localhost:5000` 打开管理界面

### 日常使用
- 程序会自动记录每次锁定/解锁电脑的时间
- 可通过Web界面查看和管理工时记录
- 支持手动修改和添加工时记录
- 可导出数据进行进一步分析

### 异常处理
- 如果程序检测到异常关机，会在下次启动时提示补齐数据
- 可通过设置页面调整工时计算规则
- 支持数据备份和恢复功能

## 🔧 配置说明

### 基本配置
- **工作时间**：设置标准工作时长和午休时间
- **提醒设置**：配置上下班和加班提醒
- **自启动**：设置程序开机自动启动

### 高级配置
- **数据库路径**：自定义数据存储位置
- **日志级别**：调整日志详细程度
- **端口设置**：修改Web服务端口

## 🧪 测试

### 运行测试
```bash
# 后端测试
cd backend
python -m pytest tests/

# 前端测试
cd frontend
npm run test
```

### 测试覆盖率
```bash
# 后端覆盖率
cd backend
python -m pytest --cov=. tests/

# 前端覆盖率
cd frontend
npm run test:coverage
```

## 📝 开发计划

### Phase 1: 核心功能 (4周)
- [x] 需求分析和架构设计
- [ ] 后端核心功能开发
- [ ] 前端基础界面开发
- [ ] 系统事件监听实现

### Phase 2: 界面完善 (3周)
- [ ] 数据可视化功能
- [ ] 用户界面优化
- [ ] 响应式设计实现
- [ ] 交互体验优化

### Phase 3: 系统集成 (2周)
- [ ] 跨平台适配
- [ ] 打包和部署
- [ ] 自启动配置
- [ ] 性能优化

### Phase 4: 测试发布 (1周)
- [ ] 全面测试
- [ ] 文档完善
- [ ] 版本发布
- [ ] 用户反馈收集

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 项目主页：https://github.com/your-username/time-trace
- 问题反馈：https://github.com/your-username/time-trace/issues
- 邮箱：your-email@example.com

## 🙏 致谢

感谢以下开源项目的支持：
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python Web框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Element Plus](https://element-plus.org/) - Vue 3 UI组件库
- [ECharts](https://echarts.apache.org/) - 数据可视化图表库
