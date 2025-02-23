"""
程序入口点模块。
"""
from com.moonciki.cursorsekiro.app import CursorSekiroApp

def main() -> None:
    """程序入口点。"""
    app = CursorSekiroApp()
    app.run()

if __name__ == "__main__":
    main() 