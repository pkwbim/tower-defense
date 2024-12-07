from typing import TYPE_CHECKING
from ..config_manager import CONFIG

if TYPE_CHECKING:
    from ..game_state import GameState

class Projectile:
    def __init__(self, x: int, y: int, game_state: 'GameState', damage: int):
        self.x = x
        self.y = y
        self.speed = CONFIG['projectile']['speed']
        self.radius = CONFIG['projectile']['radius']
        self.game_state = game_state
        self.damage = damage

    def move(self) -> bool:
        # 子彈只往右移動
        self.x += self.speed
        
        # 檢查是否擊中敵人
        for enemy in self.game_state.enemies[:]:
            if (abs(self.x - enemy.x) < (self.radius + enemy.radius) and
                abs(self.y - enemy.y) < (self.radius + enemy.radius)):
                enemy.health -= self.damage
                if enemy.health <= 0:
                    self.game_state.enemies.remove(enemy)
                    self.game_state.score += 1
                    self.game_state.money += enemy.reward
                return False
        
        # 如果子彈超出螢幕，則移除
        if self.x > CONFIG['window']['width']:
            return False
            
        return True
