#!/usr/bin/env python3
"""
简单的服务器启动脚本
运行: python start_server.py 或 uv run python start_server.py
"""

if __name__ == "__main__":
    from app.main import main
    main() 