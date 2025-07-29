#!/usr/bin/env python3
"""
构建脚本 - 用于构建和打包时迹应用
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path


def run_command(command, cwd=None, check=True):
    """运行命令并处理错误"""
    print(f"执行命令: {command}")
    if cwd:
        print(f"工作目录: {cwd}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        if e.stdout:
            print(f"标准输出: {e.stdout}")
        if e.stderr:
            print(f"错误输出: {e.stderr}")
        sys.exit(1)


def build_frontend():
    """构建前端应用"""
    print("=" * 50)
    print("开始构建前端应用...")
    print("=" * 50)
    
    frontend_dir = Path(__file__).parent.parent / "frontend"
    
    # 检查前端目录是否存在
    if not frontend_dir.exists():
        print("错误: 前端目录不存在")
        sys.exit(1)
    
    # 安装依赖
    print("安装前端依赖...")
    run_command("npm install", cwd=frontend_dir)
    
    # 构建前端
    print("构建前端应用...")
    run_command("npm run build", cwd=frontend_dir)
    
    print("前端构建完成!")


def prepare_backend():
    """准备后端环境"""
    print("=" * 50)
    print("准备后端环境...")
    print("=" * 50)
    
    backend_dir = Path(__file__).parent.parent / "backend"
    
    # 检查后端目录是否存在
    if not backend_dir.exists():
        print("错误: 后端目录不存在")
        sys.exit(1)
    
    # 安装后端依赖
    print("安装后端依赖...")
    run_command("pip install -r requirements.txt", cwd=backend_dir)
    
    print("后端环境准备完成!")


def copy_frontend_to_backend():
    """将前端构建结果复制到后端"""
    print("=" * 50)
    print("复制前端资源到后端...")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    frontend_dist = project_root / "frontend" / "dist"
    backend_static = project_root / "backend" / "static"
    
    # 检查前端构建结果是否存在
    if not frontend_dist.exists():
        print("错误: 前端构建结果不存在，请先构建前端")
        sys.exit(1)
    
    # 删除旧的静态文件
    if backend_static.exists():
        shutil.rmtree(backend_static)
    
    # 复制前端构建结果
    shutil.copytree(frontend_dist, backend_static)
    
    print("前端资源复制完成!")


def package_application():
    """打包应用程序"""
    print("=" * 50)
    print("打包应用程序...")
    print("=" * 50)
    
    backend_dir = Path(__file__).parent.parent / "backend"
    dist_dir = Path(__file__).parent.parent / "dist"
    
    # 创建dist目录
    dist_dir.mkdir(exist_ok=True)
    
    # 确定操作系统
    if sys.platform == "win32":
        app_name = "TimeTrace.exe"
        icon_option = "--icon=../assets/icon.ico" if Path("../assets/icon.ico").exists() else ""
    elif sys.platform == "darwin":
        app_name = "TimeTrace.app"
        icon_option = "--icon=../assets/icon.icns" if Path("../assets/icon.icns").exists() else ""
    else:
        app_name = "TimeTrace"
        icon_option = ""
    
    # PyInstaller命令
    pyinstaller_cmd = f"""
    pyinstaller
    --onefile
    --noconsole
    --name TimeTrace
    {icon_option}
    --add-data "static;static"
    --distpath ../dist
    --workpath ../build
    --specpath ../build
    main.py
    """.replace('\n', ' ').strip()
    
    # 执行打包
    run_command(pyinstaller_cmd, cwd=backend_dir)
    
    print(f"应用程序打包完成: {dist_dir / app_name}")


def clean_build_files():
    """清理构建文件"""
    print("=" * 50)
    print("清理构建文件...")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    
    # 要清理的目录
    clean_dirs = [
        project_root / "build",
        project_root / "backend" / "__pycache__",
        project_root / "backend" / "static",
        project_root / "frontend" / "dist",
        project_root / "frontend" / "node_modules" / ".cache"
    ]
    
    for dir_path in clean_dirs:
        if dir_path.exists():
            print(f"删除目录: {dir_path}")
            shutil.rmtree(dir_path)
    
    print("构建文件清理完成!")


def main():
    """主函数"""
    print("时迹 (TimeTrace) 构建脚本")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        sys.exit(1)
    
    # 检查是否在项目根目录
    project_root = Path(__file__).parent.parent
    if not (project_root / "README.md").exists():
        print("错误: 请在项目根目录运行此脚本")
        sys.exit(1)
    
    try:
        # 构建步骤
        build_frontend()
        prepare_backend()
        copy_frontend_to_backend()
        package_application()
        
        print("=" * 50)
        print("构建完成!")
        print("=" * 50)
        print(f"可执行文件位置: {project_root / 'dist'}")
        
    except KeyboardInterrupt:
        print("\n构建被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"构建过程中发生错误: {e}")
        sys.exit(1)
    finally:
        # 可选择是否清理构建文件
        if "--clean" in sys.argv:
            clean_build_files()


if __name__ == "__main__":
    main()
