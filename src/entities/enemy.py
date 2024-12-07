from typing import Optional
import pygame
from ..config_manager import CONFIG
from ..utils.image_loader import load_image
from .tower import Tower

class Enemy:
    def __init__(self, row: int, enemy_type: str = 'normal'):
        self.x = CONFIG['window']['width'] - CONFIG['grid']['margin']
        self.y = CONFIG['grid']['margin'] + row * CONFIG['grid']['size'] + CONFIG['grid']['size'] // 2
        self.enemy_type = enemy_type
        self.radius = CONFIG['enemy']['radius']
        
        # 從配置中獲取該類型殭屍的屬性
        enemy_config = CONFIG['enemy']['types'][enemy_type]
        self.speed = enemy_config['speed']
        self.health = enemy_config['health']
        self.max_health = enemy_config['health']
        self.attack_power = enemy_config['attack_power']
        self.reward = enemy_config['reward']
        self.color = enemy_config['color']
        
        self.attack_cooldown = 0
        self.current_target: Optional[Tower] = None
        
        # 根據殭屍類型加載不同圖片
        image_key = 'strong_enemy' if enemy_type == 'strong' else 'enemy'
        image_path = CONFIG['images'][image_key]
        size = (CONFIG['enemy_size']['width'], CONFIG['enemy_size']['height'])
        self.image = load_image(image_path, size)
