import pygame
import json
import math
import random
import sys
import os

# Load configuration
with open('config.json', 'r') as f:
    CONFIG = json.load(f)

# Initialize Pygame
pygame.init()

# Constants from config
WINDOW_WIDTH = CONFIG['window']['width']
WINDOW_HEIGHT = CONFIG['window']['height']
GRID_ROWS = CONFIG['grid']['rows']
GRID_COLS = CONFIG['grid']['cols']
GRID_SIZE = CONFIG['grid']['size']
GRID_MARGIN = CONFIG['grid']['margin']

class GameState:
    def __init__(self):
        self.money = CONFIG['game']['initial_money']
        self.score = 0
        self.lives = CONFIG['game']['initial_lives']
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.spawn_timer = 0
        self.game_over = False
        self.selected_tower_type = 'normal'  # 默認選擇普通植物

    def check_game_over(self):
        if self.lives <= 0:
            self.lives = 0  # 確保生命值不會變成負數
            self.game_over = True
            return True
        return False

class Tower:
    def __init__(self, x, y, tower_type='normal'):
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

class Enemy:
    def __init__(self, row, enemy_type='normal'):
        self.x = WINDOW_WIDTH - GRID_MARGIN
        self.y = GRID_MARGIN + row * GRID_SIZE + GRID_SIZE // 2
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
        self.current_target = None
        
        # 根據殭屍類型加載不同圖片
        image_key = 'strong_enemy' if enemy_type == 'strong' else 'enemy'
        image_path = CONFIG['images'][image_key]
        size = (CONFIG['enemy_size']['width'], CONFIG['enemy_size']['height'])
        self.image = load_image(image_path, size)

class Projectile:
    def __init__(self, x, y, game_state, damage):
        self.x = x
        self.y = y
        self.speed = CONFIG['projectile']['speed']
        self.radius = CONFIG['projectile']['radius']
        self.game_state = game_state
        self.damage = damage

    def move(self):
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
                    self.game_state.money += CONFIG['game']['kill_reward']
                return False
        
        # 如果子彈超出螢幕，則移除
        if self.x > CONFIG['window']['width']:
            return False
            
        return True

class GameRenderer:
    def __init__(self, screen, game_state):
        self.screen = screen
        self.game_state = game_state
        self.font = pygame.font.Font(None, 36)

    def draw(self):
        self.screen.fill(tuple(CONFIG['colors']['background']))
        self._draw_grid()
        self._draw_towers()
        self._draw_enemies()
        self._draw_projectiles()
        self._draw_stats()
        
        if self.game_state.game_over:
            self._draw_game_over()
            
        pygame.display.flip()

    def _draw_grid(self):
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                rect = pygame.Rect(
                    GRID_MARGIN + col * GRID_SIZE,
                    GRID_MARGIN + row * GRID_SIZE,
                    GRID_SIZE,
                    GRID_SIZE
                )
                pygame.draw.rect(self.screen, tuple(CONFIG['colors']['grid']), rect, 1)

    def _draw_towers(self):
        for tower in self.game_state.towers:
            if tower.image:
                self.screen.blit(tower.image, (tower.x, tower.y))
            else:
                pygame.draw.rect(
                    self.screen,
                    tuple(tower.color),
                    (tower.x, tower.y, GRID_SIZE, GRID_SIZE)
                )
            
            # Draw tower health bar
            health_bar_width = GRID_SIZE
            health_bar_height = 5
            health_percentage = tower.health / tower.max_health
            pygame.draw.rect(
                self.screen,
                tuple(CONFIG['colors']['health_bar_border']),
                (tower.x, tower.y - 10, health_bar_width, health_bar_height),
                1
            )
            pygame.draw.rect(
                self.screen,
                tuple(CONFIG['colors']['health_bar_fill']),
                (tower.x, tower.y - 10, health_bar_width * health_percentage, health_bar_height)
            )

    def _draw_enemies(self):
        for enemy in self.game_state.enemies:
            if enemy.image:
                # 計算圖片的中心位置
                image_x = enemy.x - CONFIG['enemy_size']['width'] // 2
                image_y = enemy.y - CONFIG['enemy_size']['height'] // 2
                self.screen.blit(enemy.image, (image_x, image_y))
            else:
                pygame.draw.circle(
                    self.screen,
                    tuple(enemy.color),  # 使用殭屍類型對應的顏色
                    (int(enemy.x), int(enemy.y)),
                    enemy.radius
                )
            # Draw enemy health bar
            health_bar_width = enemy.radius * 2
            health_bar_height = 5
            health_percentage = enemy.health / enemy.max_health
            pygame.draw.rect(
                self.screen,
                tuple(CONFIG['colors']['health_bar_border']),
                (enemy.x - enemy.radius, enemy.y - enemy.radius - 10,
                 health_bar_width, health_bar_height),
                1
            )
            pygame.draw.rect(
                self.screen,
                tuple(CONFIG['colors']['health_bar_fill']),
                (enemy.x - enemy.radius, enemy.y - enemy.radius - 10,
                 health_bar_width * health_percentage, health_bar_height)
            )

    def _draw_projectiles(self):
        for projectile in self.game_state.projectiles:
            pygame.draw.circle(
                self.screen,
                tuple(CONFIG['colors']['projectile']),
                (int(projectile.x), int(projectile.y)),
                projectile.radius
            )

    def _draw_stats(self):
        money_text = self.font.render(f'Money: {self.game_state.money}', True, tuple(CONFIG['colors']['text']))
        score_text = self.font.render(f'Score: {self.game_state.score}', True, tuple(CONFIG['colors']['text']))
        lives_text = self.font.render(f'Lives: {self.game_state.lives}', True, tuple(CONFIG['colors']['text']))
        tower_type_text = self.font.render(
            f'Selected: {"Strong" if self.game_state.selected_tower_type == "strong" else "Normal"} Tower '
            f'(Cost: {CONFIG["tower"]["types"][self.game_state.selected_tower_type]["cost"]})',
            True, tuple(CONFIG['colors']['text']))
        
        self.screen.blit(money_text, (10, 10))
        self.screen.blit(score_text, (200, 10))
        self.screen.blit(lives_text, (400, 10))
        self.screen.blit(tower_type_text, (10, CONFIG['window']['height'] - 30))

    def _draw_game_over(self):
        # 創建半透明的黑色遮罩
        overlay = pygame.Surface((CONFIG['window']['width'], CONFIG['window']['height']))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        # 繪製遊戲結束文字
        font = pygame.font.Font(None, 74)
        game_over_text = font.render('Game Over', True, (255, 0, 0))
        score_text = self.font.render(f'Final Score: {self.game_state.score}', True, (255, 255, 255))
        
        # 計算文字位置
        text_x = CONFIG['window']['width'] // 2 - game_over_text.get_width() // 2
        text_y = CONFIG['window']['height'] // 2 - game_over_text.get_height()
        score_x = CONFIG['window']['width'] // 2 - score_text.get_width() // 2
        score_y = CONFIG['window']['height'] // 2 + 10
        
        # 繪製文字
        self.screen.blit(game_over_text, (text_x, text_y))
        self.screen.blit(score_text, (score_x, score_y))

class GameLogic:
    def __init__(self, game_state):
        self.game_state = game_state

    def update(self):
        if not self.game_state.game_over:
            self._spawn_enemy()
            self._update_enemies()
            self._update_projectiles()
            self._tower_attack()

    def _spawn_enemy(self):
        self.game_state.spawn_timer += 1
        if self.game_state.spawn_timer >= CONFIG['enemy']['spawn_interval']:
            self.game_state.spawn_timer = 0
            row = random.randint(0, GRID_ROWS - 1)
            
            # 根據分數決定是否生成強力殭屍
            if (self.game_state.score >= CONFIG['game']['strong_enemy_score'] and 
                random.random() < 0.3):  # 30% 機率生成強力殭屍
                self.game_state.enemies.append(Enemy(row, 'strong'))
            else:
                self.game_state.enemies.append(Enemy(row, 'normal'))

    def _update_enemies(self):
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
                enemy_col = (enemy.x - GRID_MARGIN) // GRID_SIZE
                enemy_row = (enemy.y - GRID_MARGIN) // GRID_SIZE
                
                for tower in self.game_state.towers:
                    tower_col = (tower.x - GRID_MARGIN) // GRID_SIZE
                    tower_row = (tower.y - GRID_MARGIN) // GRID_SIZE
                    
                    if (tower_row == enemy_row and 
                        tower_col < enemy_col and 
                        abs(enemy.x - (tower.x + GRID_SIZE)) < enemy.speed):
                        enemy.current_target = tower
                        break
                
                if not enemy.current_target:
                    enemy.x -= enemy.speed
                    if enemy.x < 0:
                        self.game_state.enemies.remove(enemy)
                        self.game_state.lives -= 1
                        self.game_state.check_game_over()

    def _update_projectiles(self):
        # 更新所有子彈的位置，並移除已經消失的子彈
        self.game_state.projectiles = [p for p in self.game_state.projectiles if p.move()]

    def _tower_attack(self):
        for tower in self.game_state.towers:
            if tower.attack_cooldown <= 0:
                # 檢查同一行是否有敵人
                tower_row = (tower.y - GRID_MARGIN) // GRID_SIZE
                for enemy in self.game_state.enemies:
                    enemy_row = (enemy.y - GRID_MARGIN) // GRID_SIZE
                    enemy_col = (enemy.x - GRID_MARGIN) // GRID_SIZE
                    tower_col = (tower.x - GRID_MARGIN) // GRID_SIZE
                    
                    if enemy_row == tower_row and enemy_col > tower_col:
                        self.game_state.projectiles.append(
                            Projectile(tower.x + GRID_SIZE, tower.y + GRID_SIZE // 2,
                                     self.game_state, tower.damage))
                        tower.attack_cooldown = tower.attack_cooldown_max
                        break
            else:
                tower.attack_cooldown -= 1

class EventHandler:
    def __init__(self, game_state):
        self.game_state = game_state

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_state.game_over:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # 右鍵點擊切換植物類型
                if event.button == 3:  # 右鍵
                    self.game_state.selected_tower_type = (
                        'strong' if self.game_state.selected_tower_type == 'normal' else 'normal'
                    )
                # 左鍵放置植物
                elif event.button == 1:
                    col = (mouse_x - GRID_MARGIN) // GRID_SIZE
                    row = (mouse_y - GRID_MARGIN) // GRID_SIZE
                    
                    if (0 <= row < GRID_ROWS and 0 <= col < GRID_COLS):
                        tower_cost = CONFIG['tower']['types'][self.game_state.selected_tower_type]['cost']
                        if self.game_state.money >= tower_cost:
                            tower_x = GRID_MARGIN + col * GRID_SIZE
                            tower_y = GRID_MARGIN + row * GRID_SIZE
                            
                            # Check if tower already exists at this position
                            tower_exists = any(t.x == tower_x and t.y == tower_y 
                                            for t in self.game_state.towers)
                            
                            if not tower_exists:
                                self.game_state.towers.append(
                                    Tower(tower_x, tower_y, self.game_state.selected_tower_type))
                                self.game_state.money -= tower_cost
        return True

def load_image(path, size=None):
    try:
        image = pygame.image.load(path)
        if size:
            image = pygame.transform.scale(image, (size[0], size[1]))
        return image
    except pygame.error:
        return None

def main():
    # Initialize the game window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(CONFIG['window']['title'])
    clock = pygame.time.Clock()

    # Initialize game components
    game_state = GameState()
    game_renderer = GameRenderer(screen, game_state)
    game_logic = GameLogic(game_state)
    event_handler = EventHandler(game_state)

    # Game loop
    running = True
    while running:
        running = event_handler.handle_events()
        game_logic.update()
        game_renderer.draw()
        clock.tick(CONFIG['game']['fps'])

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
