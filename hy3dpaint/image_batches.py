from __future__ import annotations

from typing import Any


def resize_image_groups(
    image_groups: dict[str, list[Any]], size: tuple[int, int]
) -> dict[str, list[Any]]:
    return {
        group_name: [image.resize(size) for image in images]
        for group_name, images in image_groups.items()
    }
