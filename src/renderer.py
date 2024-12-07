import pygame
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_state import GameState
from .config_manager import CONFIG

class Renderer:
    def __init__(self, screen: pygame.Surface, game_state: 'GameState'):
        self.screen = screen
        self.game_state = game_state
        self.font = pygame.font.Font(None, 36)

    def render(self) -> None:
        self.screen.fill(CONFIG['colors']['background'])
        self._draw_grid()
        self._draw_towers()
        self._draw_enemies()
        self._draw_projectiles()
        self._draw_ui()
        
        if self.game_state.game_over:
            self._draw_game_over()
            
        pygame.display.flip()

    def _draw_grid(self) -> None:
        grid_margin = CONFIG['grid']['margin']
        grid_size = CONFIG['grid']['size']
        rows = CONFIG['grid']['rows']
        cols = CONFIG['grid']['cols']
        
        for row in range(rows):
            for col in range(cols):
                rect = pygame.Rect(
                    grid_margin + col * grid_size,
                    grid_margin + row * grid_size,
                    grid_size - 1,
                    grid_size - 1
                )
                pygame.draw.rect(self.screen, CONFIG['colors']['grid'], rect, 1)

    def _draw_towers(self) -> None:
        for tower in self.game_state.towers:
            self.screen.blit(tower.image, (tower.x, tower.y))
            
            # 繪製血條
            health_width = CONFIG['grid']['size'] * (tower.health / tower.max_health)
            health_height = 5
            health_y = tower.y - 10
            
            pygame.draw.rect(self.screen, CONFIG['colors']['health_bg'],
                           (tower.x, health_y, CONFIG['grid']['size'], health_height))
            pygame.draw.rect(self.screen, CONFIG['colors']['health'],
                           (tower.x, health_y, health_width, health_height))

    def _draw_enemies(self) -> None:
        for enemy in self.game_state.enemies:
            self.screen.blit(enemy.image, (enemy.x - enemy.radius, enemy.y - enemy.radius))
            
            # 繪製血條
            health_width = enemy.radius * 2 * (enemy.health / enemy.max_health)
            health_height = 5
            health_y = enemy.y - enemy.radius - 10
            
            pygame.draw.rect(self.screen, CONFIG['colors']['health_bg'],
                           (enemy.x - enemy.radius, health_y, enemy.radius * 2, health_height))
            pygame.draw.rect(self.screen, CONFIG['colors']['health'],
                           (enemy.x - enemy.radius, health_y, health_width, health_height))

    def _draw_projectiles(self) -> None:
        for projectile in self.game_state.projectiles:
            pygame.draw.circle(self.screen, CONFIG['colors']['projectile'],
                             (int(projectile.x), int(projectile.y)),
                             projectile.radius)

    def _draw_ui(self) -> None:
        # 顯示金錢
        money_text = self.font.render(f'Money: {self.game_state.money}', True, CONFIG['colors']['text'])
        self.screen.blit(money_text, (10, 10))
        
        # 顯示分數
        score_text = self.font.render(f'Score: {self.game_state.score}', True, CONFIG['colors']['text'])
        self.screen.blit(score_text, (200, 10))
        
        # 顯示生命值
        lives_text = self.font.render(f'Lives: {self.game_state.lives}', True, CONFIG['colors']['text'])
        self.screen.blit(lives_text, (400, 10))
        
        # 顯示選擇的防禦塔類型
        tower_type = 'Strong Tower' if self.game_state.selected_tower_type == 'strong' else 'Normal Tower'
        tower_cost = CONFIG['tower']['types'][self.game_state.selected_tower_type]['cost']
        tower_text = self.font.render(f'Selected: {tower_type} (Cost: {tower_cost})',
                                    True, CONFIG['colors']['text'])
        self.screen.blit(tower_text, (10, CONFIG['window']['height'] - 40))

    def _draw_game_over(self) -> None:
        # 半透明黑色背景
        s = pygame.Surface((CONFIG['window']['width'], CONFIG['window']['height']))
        s.set_alpha(128)
        s.fill((0, 0, 0))
        self.screen.blit(s, (0, 0))
        
        # 遊戲結束文字
        game_over_font = pygame.font.Font(None, 74)
        text = game_over_font.render('Game Over!', True, CONFIG['colors']['text'])
        text_rect = text.get_rect(center=(CONFIG['window']['width'] / 2,
                                        CONFIG['window']['height'] / 2))
        self.screen.blit(text, text_rect)
        
        # 最終分數
        score_text = self.font.render(f'Final Score: {self.game_state.score}',
                                    True, CONFIG['colors']['text'])
        score_rect = score_text.get_rect(center=(CONFIG['window']['width'] / 2,
                                               CONFIG['window']['height'] / 2 + 50))
        self.screen.blit(score_text, score_rect)
