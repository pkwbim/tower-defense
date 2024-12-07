from typing import Optional
import pygame
from ..config_manager import CONFIG
from ..utils.image_loader import load_image

class Tower:
    def __init__(self, x: int, y: int, tower_type: str = 'normal'):
        self.x = x
        self.y = y
        self.tower_type = tower_type
        
        # 從配置中獲取該類型植物的屬性
        tower_config = CONFIG['tower']['types'][tower_type]
        self.attack_cooldown_max = tower_config['attack_cooldown']
        self.attack_cooldown = 0
        self.health = tower_config['initial_health']
        self.max_health = tower_config['initial_health']
        self.damage = tower_config['damage']
        self.color = tower_config['color']
        
        # 根據植物類型加載不同圖片
        image_key = 'strong_tower' if tower_type == 'strong' else 'tower'
        image_path = CONFIG['images'][image_key]
        size = (CONFIG['tower_size']['width'], CONFIG['tower_size']['height'])
        self.image = load_image(image_path, size)
