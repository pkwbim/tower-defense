import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_state import GameState
from .entities.enemy import Enemy
from .entities.projectile import Projectile
from .config_manager import CONFIG

class GameLogic:
    def __init__(self, game_state: 'GameState'):
        self.game_state = game_state

    def update(self) -> None:
        if not self.game_state.game_over:
            self._spawn_enemy()
            self._update_enemies()
            self._update_projectiles()
            self._tower_attack()

    def _update_projectiles(self) -> None:
        # 更新所有子彈的位置，並移除已經消失的子彈
        self.game_state.projectiles = [p for p in self.game_state.projectiles if p.move()]

    def _spawn_enemy(self) -> None:
        self.game_state.spawn_timer += 1
        if self.game_state.spawn_timer >= CONFIG['enemy']['spawn_interval']:
            self.game_state.spawn_timer = 0
            row = random.randint(0, CONFIG['grid']['rows'] - 1)
            
            # 根據分數決定是否生成強力殭屍
            if (self.game_state.score >= CONFIG['game']['strong_enemy_score'] and 
                random.random() < 0.3):  # 30% 機率生成強力殭屍
                self.game_state.enemies.append(Enemy(row, 'strong'))
            else:
                self.game_state.enemies.append(Enemy(row, 'normal'))

    def _update_enemies(self) -> None:
        grid_margin = CONFIG['grid']['margin']
        grid_size = CONFIG['grid']['size']
        
        for enemy in self.game_state.enemies[:]:
            if enemy.current_target:
                if enemy.attack_cooldown <= 0:
                    enemy.current_target.health -= enemy.attack_power
                    enemy.attack_cooldown = CONFIG['enemy']['attack_cooldown']
                    
                    if enemy.current_target.health <= 0:
                        if enemy.current_target in self.game_state.towers:
                            self.game_state.towers.remove(enemy.current_target)
                        for e in self.game_state.enemies:
                            if e.current_target == enemy.current_target:
                                e.current_target = None
                else:
                    enemy.attack_cooldown -= 1
            else:
                enemy_col = (enemy.x - grid_margin) // grid_size
                enemy_row = (enemy.y - grid_margin) // grid_size
                
                for tower in self.game_state.towers:
                    tower_col = (tower.x - grid_margin) // grid_size
                    tower_row = (tower.y - grid_margin) // grid_size
                    
                    if (tower_row == enemy_row and 
                        tower_col < enemy_col and 
                        abs(enemy.x - (tower.x + grid_size)) < enemy.speed):
                        enemy.current_target = tower
                        break
                
                if not enemy.current_target:
                    enemy.x -= enemy.speed
                    if enemy.x < 0:
                        self.game_state.enemies.remove(enemy)
                        self.game_state.lives -= 1
                        self.game_state.check_game_over()

    def _tower_attack(self) -> None:
        grid_margin = CONFIG['grid']['margin']
        grid_size = CONFIG['grid']['size']
        
        for tower in self.game_state.towers:
            if tower.attack_cooldown <= 0:
                # 檢查同一行是否有敵人
                tower_row = (tower.y - grid_margin) // grid_size
                for enemy in self.game_state.enemies:
                    enemy_row = (enemy.y - grid_margin) // grid_size
                    enemy_col = (enemy.x - grid_margin) // grid_size
                    tower_col = (tower.x - grid_margin) // grid_size
                    
                    if enemy_row == tower_row and enemy_col > tower_col:
                        self.game_state.projectiles.append(
                            Projectile(tower.x + grid_size, tower.y + grid_size // 2,
                                     self.game_state, tower.damage))
                        tower.attack_cooldown = tower.attack_cooldown_max
                        break
            else:
                tower.attack_cooldown -= 1
