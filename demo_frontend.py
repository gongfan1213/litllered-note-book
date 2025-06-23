#!/usr/bin/env python3
"""
小红书起号智能助手 - 前端界面演示脚本
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_node_installed():
    """检查Node.js是否已安装"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js已安装: {result.stdout.strip()}")
            return True
        else:
            return False
    except FileNotFoundError:
        return False

def check_npm_installed():
    """检查npm是否已安装"""
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm已安装: {result.stdout.strip()}")
            return True
        else:
            return False
    except FileNotFoundError:
        return False

def install_frontend_dependencies():
    """安装前端依赖"""
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ 前端目录不存在，请确保项目结构正确")
        return False
    
    print("📦 正在安装前端依赖...")
    try:
        subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
        print("✅ 前端依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def start_frontend_server():
    """启动前端服务器"""
    frontend_dir = Path("frontend")
    
    print("🚀 正在启动前端服务器...")
    print("📱 前端界面将在浏览器中自动打开")
    print("🔗 访问地址: http://localhost:3000")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        # 延迟2秒后打开浏览器
        time.sleep(2)
        webbrowser.open('http://localhost:3000')
        
        # 启动开发服务器
        subprocess.run(['npm', 'start'], cwd=frontend_dir)
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def main():
    """主函数"""
    print("🎨 小红书起号智能助手 - 前端界面演示")
    print("=" * 50)
    
    # 检查Node.js
    if not check_node_installed():
        print("❌ Node.js未安装")
        print("📥 请访问 https://nodejs.org/ 下载并安装Node.js")
        return
    
    # 检查npm
    if not check_npm_installed():
        print("❌ npm未安装")
        print("📥 请重新安装Node.js，npm会随Node.js一起安装")
        return
    
    # 安装依赖
    if not install_frontend_dependencies():
        return
    
    # 启动服务器
    start_frontend_server()

if __name__ == "__main__":
    main() 