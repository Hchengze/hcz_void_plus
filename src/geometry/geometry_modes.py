"""三维观测几何模式定义。"""

from __future__ import annotations


RECEIVER_GEOMETRY_MODES = {"straight", "polyline_csv"}
SOURCE_GEOMETRY_MODES = {"line", "grid", "csv"}


def describe_geometry_mode(receiver_mode: str, source_mode: str) -> str:
    """返回用于 metadata/report 的几何模式说明。"""

    return (
        f"receiver_geometry_mode={receiver_mode}, source_geometry_mode={source_mode}; "
        "所有走时均使用 source_xyz/receiver_xyz/candidate_xyz 三维坐标。"
    )

