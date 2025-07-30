"""
简化的API启动脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    try:
        print("正在启动时迹API服务器...")

        # 配置日志过滤器
        import logging
        logging.getLogger("watchfiles").setLevel(logging.WARNING)
        logging.getLogger("watchfiles.main").setLevel(logging.WARNING)

        # 导入应用
        from app.main import app
        print("✓ 应用导入成功")

        # 启动服务器
        import uvicorn
        print("✓ 启动服务器在 http://127.0.0.1:8000")
        print("✓ API文档地址: http://127.0.0.1:8000/docs")
        print("✓ 按 Ctrl+C 停止服务器")

        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            reload=False  # 简化版不启用自动重载
        )

    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
