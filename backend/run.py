"""
时迹工时追踪系统启动脚本
"""
import sys
import os
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
        
        # 启动应用
        import uvicorn
        
        uvicorn.run(
            "app.main:app",
            host=env_settings.host,
            port=env_settings.port,
            reload=env_settings.debug,
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
