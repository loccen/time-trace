"""
调试版本的main.py
逐步添加组件来找出问题
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

print("1. FastAPI导入成功")

# 创建应用
app = FastAPI(
    title="时迹 - 工时追踪系统",
    description="一个智能的工时追踪和管理系统",
    version="1.0.0"
)

print("2. FastAPI应用创建成功")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("3. CORS中间件添加成功")

# 基础路由
@app.get("/")
async def root():
    return {"message": "时迹工时追踪系统API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

print("4. 基础路由添加成功")

# 尝试导入日志
try:
    from app.core.logger import get_logger
    logger = get_logger("DebugAPI")
    print("5. 日志模块导入成功")
except Exception as e:
    print(f"5. 日志模块导入失败: {e}")

# 尝试导入数据库
try:
    from app.core.database import db_manager
    print("6. 数据库模块导入成功")
except Exception as e:
    print(f"6. 数据库模块导入失败: {e}")

# 尝试导入模型
try:
    from app.models import TimeRecord, SystemEvent
    print("7. 模型导入成功")
except Exception as e:
    print(f"7. 模型导入失败: {e}")

# 尝试导入DAO
try:
    from app.dao import time_record_dao, system_event_dao
    print("8. DAO导入成功")
except Exception as e:
    print(f"8. DAO导入失败: {e}")

# 尝试导入API路由
try:
    from app.api import api_v1_router
    app.include_router(api_v1_router)
    print("9. API路由导入和注册成功")
except Exception as e:
    print(f"9. API路由导入失败: {e}")

print("10. 应用初始化完成")

if __name__ == "__main__":
    import uvicorn
    print("启动调试API服务器...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
