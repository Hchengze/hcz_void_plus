"""运行当前稳定三维算法主线。"""

from __future__ import annotations

from pathlib import Path
import sys

CURRENT_DIR = Path(__file__).resolve().parent
CODE_DIR = CURRENT_DIR.parent
REPO_ROOT = CODE_DIR.parent
for path in [str(CODE_DIR), str(REPO_ROOT)]:
    if path not in sys.path:
        sys.path.insert(0, path)

from current_3d_algorithm.stable_pipeline import run_current_pipeline


def main() -> None:
    """命令行入口。参数体系仍由根目录 main.py 管理。"""

    run_current_pipeline()


if __name__ == "__main__":
    main()
