"""
API集成测试
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试导入"""
    try:
        print("测试基础导入...")
        from app.core.logger import get_logger
        print("✓ 日志模块导入成功")
        
        from app.core.database import db_manager
        print("✓ 数据库模块导入成功")
        
        from app.models import TimeRecord, SystemEvent
        print("✓ 模型模块导入成功")
        
        from app.dao import time_record_dao, system_event_dao
        print("✓ DAO模块导入成功")
        
        from app.api.v1 import api_v1_router
        print("✓ API路由导入成功")
        
        from app.main import app
        print("✓ 主应用导入成功")
        
        print("\n所有模块导入成功！")
        return True
        
    except Exception as e:
        print(f"导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database():
    """测试数据库连接"""
    try:
        print("\n测试数据库连接...")
        from app.core.database import db_manager
        
        # 测试连接
        result = db_manager.execute_query("SELECT 1 as test")
        print(f"✓ 数据库连接成功: {result}")
        
        # 测试表是否存在
        tables = db_manager.get_all_tables()
        print(f"✓ 数据库表: {tables}")
        
        return True
        
    except Exception as e:
        print(f"数据库测试失败: {e}")
        return False

def test_api_routes():
    """测试API路由"""
    try:
        print("\n测试API路由...")
        from app.main import app
        
        # 获取路由信息
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(f"{route.methods} {route.path}")
        
        print("✓ API路由:")
        for route in routes:
            print(f"  {route}")
        
        return True
        
    except Exception as e:
        print(f"API路由测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=== 时迹API集成测试 ===")
    
    success = True
    
    # 测试导入
    if not test_imports():
        success = False
    
    # 测试数据库
    if not test_database():
        success = False
    
    # 测试API路由
    if not test_api_routes():
        success = False
    
    if success:
        print("\n🎉 所有测试通过！API可以启动。")
        
        # 尝试启动API
        print("\n启动API服务器...")
        try:
            import uvicorn
            from app.main import app
            
            uvicorn.run(
                app,
                host="127.0.0.1",
                port=8000,
                log_level="info"
            )
        except KeyboardInterrupt:
            print("\n服务器已停止")
        except Exception as e:
            print(f"启动失败: {e}")
    else:
        print("\n❌ 测试失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()
