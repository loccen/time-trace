"""
最小化API测试
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI

# 创建最小化应用
app = FastAPI(title="时迹API测试")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    print("启动最小化API测试...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
