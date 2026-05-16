from __future__ import annotations

from os import PathLike
from typing import Iterable

from PIL import Image


__all__ = ["normalize_image_prompt"]


def _load_image(source: str | PathLike[str] | Image.Image) -> Image.Image:
    if isinstance(source, Image.Image):
        return source
    if isinstance(source, (str, PathLike)):
        return Image.open(source)
    raise TypeError(
        "image_path must be a path, a PIL image, or an iterable of those values"
    )


def normalize_image_prompt(
    image_path: str
    | PathLike[str]
    | Image.Image
    | Iterable[str | PathLike[str] | Image.Image]
    | None,
) -> list[Image.Image]:
    if image_path is None:
        raise ValueError("image_path is required")

    if isinstance(image_path, (str, PathLike, Image.Image)):
        return [_load_image(image_path)]

    return [_load_image(image) for image in image_path]
