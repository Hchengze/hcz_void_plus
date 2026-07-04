"""检查关键文本文件的换行和可审计性。

Stage 5C 不再根据 GitHub raw 页面观感判断文件是否“一行化”。本工具直接读取
本地字节，统计 LF、CRLF、CR-only 和最长行，给出可重复的文本健康报告。
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


DEFAULT_CHECK_PATTERNS = [
    "README.md",
    "main.py",
    "docs/forward_modeling_roadmap.md",
    "docs/forward_modeling_boundary.md",
    "docs/elastic2d_forward_design.md",
    "src/forward/acoustic2d/acoustic_fdtd.py",
    "src/forward/forward_registry.py",
    "code/current_3d_algorithm/stable_api.py",
    "outputs/latest_stable/summary.md",
]


@dataclass(frozen=True)
class TextHealth:
    """单个文本文件的健康指标。"""

    path: str
    byte_count: int
    lf_count: int
    crlf_count: int
    cr_only_count: int
    logical_line_count: int
    longest_line_length: int
    suspicious_one_line: bool
    healthy: bool


def _line_lengths(text: str) -> list[int]:
    """返回按 LF 分割后的每行长度。

    这里不使用 splitlines()，因为 splitlines 会吞掉不同换行符差异；换行符类型已在
    字节层统计，行长只需要按 LF 视角衡量可审计性。
    """

    return [len(line) for line in text.split("\n")]


def inspect_text_file(path: Path, min_lines: int = 5, max_line_length: int = 2000) -> TextHealth:
    """检查一个文本文件。

    判断原则：
        1. CR-only 换行直接判为不健康；
        2. 非空文件 LF 逻辑行数过少且最长行过长，判为疑似一行化；
        3. Markdown 小文件允许少量行，核心 Python/报告文件会在测试中设更严格阈值。
    """

    data = path.read_bytes()
    crlf_count = data.count(b"\r\n")
    cr_total = data.count(b"\r")
    lf_count = data.count(b"\n")
    cr_only_count = cr_total - crlf_count
    text = data.decode("utf-8", errors="replace")
    lengths = _line_lengths(text)
    logical_line_count = max(1, lf_count + 1) if data else 0
    longest_line_length = max(lengths) if lengths else 0
    suspicious_one_line = bool(data) and logical_line_count < min_lines and longest_line_length > max_line_length
    healthy = cr_only_count == 0 and not suspicious_one_line
    return TextHealth(
        path=str(path),
        byte_count=len(data),
        lf_count=lf_count,
        crlf_count=crlf_count,
        cr_only_count=cr_only_count,
        logical_line_count=logical_line_count,
        longest_line_length=longest_line_length,
        suspicious_one_line=suspicious_one_line,
        healthy=healthy,
    )


def collect_text_health(paths: list[Path]) -> list[TextHealth]:
    """批量收集文本健康指标。"""

    return [inspect_text_file(path) for path in paths if path.exists()]


def default_paths(repo_root: Path) -> list[Path]:
    """返回 Stage 5C 必查文件列表。"""

    paths = [repo_root / pattern for pattern in DEFAULT_CHECK_PATTERNS]
    reports_dir = repo_root / "outputs" / "latest_stable" / "reports"
    if reports_dir.exists():
        paths.extend(sorted(reports_dir.glob("*.md")))
        paths.extend(sorted(reports_dir.glob("*/*.md")))
    return paths


def main() -> int:
    """命令行入口，打印关键文件行数统计。"""

    parser = argparse.ArgumentParser(description="检查 hcz_void_plus 关键文本文件换行健康度")
    parser.add_argument("--repo-root", default=".", help="仓库根目录")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    results = collect_text_health(default_paths(repo_root))
    print("path\tlf\tcrlf\tcr_only\tlines\tlongest\thealthy")
    for item in results:
        print(
            f"{Path(item.path).as_posix()}\t{item.lf_count}\t{item.crlf_count}\t"
            f"{item.cr_only_count}\t{item.logical_line_count}\t{item.longest_line_length}\t{item.healthy}"
        )
    return 0 if all(item.healthy for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
