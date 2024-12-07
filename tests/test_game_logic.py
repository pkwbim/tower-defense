import unittest
from unittest.mock import patch, MagicMock
import pygame
from src.game_state import GameState
from src.game_logic import GameLogic
from src.entities.tower import Tower
from src.entities.enemy import Enemy
from src.config_manager import CONFIG

# 創建一個假的 surface 用於測試
pygame.init()
mock_surface = pygame.Surface((32, 32))

@patch('src.utils.image_loader.load_image', return_value=mock_surface)
class TestGameLogic(unittest.TestCase):
    def setUp(self):
        self.game_state = GameState()
        self.game_logic = GameLogic(self.game_state)

    def test_tower_attack(self, mock_load_image):
        # 創建一個防禦塔和一個敵人
        tower = Tower(CONFIG['grid']['margin'], CONFIG['grid']['margin'])
        enemy = Enemy(0)  # 在第一行
        
        self.game_state.towers.append(tower)
        self.game_state.enemies.append(enemy)
        
        # 確保防禦塔可以立即攻擊
        tower.attack_cooldown = 0
        
        # 更新遊戲邏輯
        self.game_logic._tower_attack()
        
        # 檢查是否創建了子彈
        self.assertEqual(len(self.game_state.projectiles), 1)
        
    def test_enemy_damage(self, mock_load_image):
        # 創建一個防禦塔
        tower = Tower(CONFIG['grid']['margin'], CONFIG['grid']['margin'])
        self.game_state.towers.append(tower)
        initial_health = tower.health
        
        # 創建一個敵人在防禦塔旁邊
        enemy = Enemy(0)
        enemy.x = tower.x + CONFIG['grid']['size'] + 1
        enemy.current_target = tower
        self.game_state.enemies.append(enemy)
        
        # 更新遊戲邏輯
        self.game_logic._update_enemies()
        
        # 檢查防禦塔是否受到傷害
        self.assertLess(tower.health, initial_health)
        
    def test_game_over(self, mock_load_image):
        # 設置生命值為1
        self.game_state.lives = 1
        
        # 創建一個已經到達左邊界的敵人
        enemy = Enemy(0)
        enemy.x = -10
        self.game_state.enemies.append(enemy)
        
        # 更新遊戲邏輯
        self.game_logic._update_enemies()
        
        # 檢查遊戲是否結束
        self.assertTrue(self.game_state.game_over)
        self.assertEqual(self.game_state.lives, 0)

if __name__ == '__main__':
    unittest.main()
