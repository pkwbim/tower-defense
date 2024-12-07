from typing import List
import pygame
from .entities.tower import Tower
from .entities.enemy import Enemy
from .entities.projectile import Projectile
from .config_manager import CONFIG

class GameState:
    def __init__(self):
        self.money = CONFIG['game']['initial_money']
        self.score = 0
        self.lives = CONFIG['game']['initial_lives']
        self.towers: List[Tower] = []
        self.enemies: List[Enemy] = []
        self.projectiles: List[Projectile] = []
        self.spawn_timer = 0
        self.game_over = False
        self.selected_tower_type = 'normal'

    def check_game_over(self) -> bool:
        if self.lives <= 0:
            self.lives = 0  # 確保生命值不會變成負數
            self.game_over = True
            return True
        return False
