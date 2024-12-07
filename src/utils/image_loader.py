from pathlib import Path
import pygame
from typing import Tuple

def load_image(image_path: str, size: Tuple[int, int]) -> pygame.Surface:
    """Load and scale an image from the assets directory."""
    try:
        assets_path = Path(__file__).parent.parent.parent / 'assets'
        image = pygame.image.load(str(assets_path / image_path))
        return pygame.transform.scale(image, size)
    except FileNotFoundError:
        # 如果找不到圖片，返回一個空的 surface
        surface = pygame.Surface(size)
        surface.fill((255, 255, 255))  # 填充白色
        return surface
