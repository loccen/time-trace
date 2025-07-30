"""
时迹工时追踪系统启动脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """主函数"""
    try:
        # 导入应用
        from app.main import app
        from app.config.settings import env_settings

        # 配置日志过滤器，减少 watchfiles 的噪音日志
        import logging

        # 设置 watchfiles 日志级别为 WARNING，减少文件变化检测日志
        logging.getLogger("watchfiles").setLevel(logging.WARNING)
        logging.getLogger("watchfiles.main").setLevel(logging.WARNING)

        # 启动应用
        import uvicorn

        # 配置 uvicorn 的文件监控排除规则
        reload_excludes = [
            "*.log",           # 排除所有日志文件
            "logs/*",          # 排除整个日志目录
            "*.db",            # 排除数据库文件
            "*.db-shm",        # 排除 SQLite 共享内存文件
            "*.db-wal",        # 排除 SQLite WAL 文件
            "__pycache__/*",   # 排除 Python 缓存
            "*.pyc",           # 排除编译的 Python 文件
            ".git/*",          # 排除 Git 目录
            "node_modules/*",  # 排除 Node.js 模块
            "*.tmp",           # 排除临时文件
            "*.swp",           # 排除 Vim 交换文件
            ".vscode/*",       # 排除 VSCode 配置
        ]

        uvicorn.run(
            "app.main:app",
            host=env_settings.host,
            port=env_settings.port,
            reload=env_settings.debug,
            reload_excludes=reload_excludes,
            log_level=env_settings.log_level.lower()
        )

    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装所有依赖: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
