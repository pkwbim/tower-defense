import pygame
import sys
import math
import random
import json
import os

# 讀取設定檔
with open('config.json', 'r') as f:
    config = json.load(f)

# 初始化 Pygame
pygame.init()

# 載入圖片
def load_image(path):
    if not os.path.exists(path):
        print(f"警告: 圖片檔案不存在: {path}")
        return None
    try:
        image = pygame.image.load(path)
        # 調整圖片大小為設定檔中指定的大小
        return pygame.transform.scale(image, (config['tower_size']['width'], 
                                           config['tower_size']['height']))
    except pygame.error as e:
        print(f"載入圖片時發生錯誤: {e}")
        return None

# 載入塔的圖片
tower_image = load_image(config['images']['tower'])

# 設定遊戲視窗
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("我的塔防遊戲")

# 設定字體
try:
    game_font = pygame.font.Font("c:/Windows/Fonts/msjh.ttc", 36)  # 微軟正黑體
except:
    try:
        game_font = pygame.font.Font("c:/Windows/Fonts/mingliu.ttc", 36)  # 細明體
    except:
        game_font = pygame.font.Font(None, 36)  # 如果都找不到，使用默認字體

# 顏色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# 格子設置
GRID_SIZE = 80  # 每個格子的大小
GRID_COLS = 9   # 列數
GRID_ROWS = 5   # 行數
GRID_MARGIN = 40  # 邊距

# 遊戲元素
class Tower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.attack_power = 1
        self.attack_range = GRID_SIZE * 1.5
        self.attack_speed = 1
        self.cost = 50
        self.projectiles = []
        self.attack_cooldown = 0
        self.health = 100  # 新增：防禦塔血量
        self.max_health = 100  # 新增：最大血量

class Enemy:
    def __init__(self, row):
        self.x = WINDOW_WIDTH
        self.y = GRID_MARGIN + row * GRID_SIZE + GRID_SIZE // 2
        self.speed = 2
        self.health = 5
        self.max_health = 5
        self.attack_power = 1  # 新增：殭屍攻擊力
        self.attack_cooldown = 0  # 新增：攻擊冷卻時間
        self.current_target = None  # 新增：當前攻擊目標

class Projectile:
    def __init__(self, x, y, target, game_state):  
        self.x = x
        self.y = y
        self.target = target
        self.speed = 5
        self.radius = 5
        self.game_state = game_state  

    def move(self):
        if self.target is None or self.target not in self.game_state.enemies:  
            return False
        
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 1:
            return False
        
        self.x += (dx / distance) * self.speed
        self.y += (dy / distance) * self.speed
        return True

class GameState:
    def __init__(self):
        self.money = 100
        self.score = 0
        self.lives = 10
        self.wave = 1
        self.spawn_timer = 0
        self.towers = []
        self.enemies = []
        self.game_grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.running = True

    def can_place_tower(self, col, row):
        return (col < GRID_COLS and 
                self.money >= 50 and 
                self.game_grid[row][col] == 0)

    def place_tower(self, col, row):
        tower_x = GRID_MARGIN + col * GRID_SIZE
        tower_y = GRID_MARGIN + row * GRID_SIZE
        self.towers.append(Tower(tower_x, tower_y))
        self.game_grid[row][col] = 1
        self.money -= 50

    def is_game_over(self):
        return self.lives <= 0

class GameRenderer:
    def __init__(self, screen, game_font):
        self.screen = screen
        self.game_font = game_font

    def render(self, game_state):
        self.screen.fill(WHITE)
        self._draw_grid()
        self._draw_towers(game_state.towers)
        self._draw_enemies(game_state.enemies)
        self._draw_game_stats(game_state)
        
        if game_state.is_game_over():
            self._draw_game_over()
        
        pygame.display.flip()

    def _draw_grid(self):
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x = GRID_MARGIN + col * GRID_SIZE
                y = GRID_MARGIN + row * GRID_SIZE
                pygame.draw.rect(self.screen, BLACK, (x, y, GRID_SIZE, GRID_SIZE), 1)

    def _draw_towers(self, towers):
        for tower in towers:
            if tower_image:
                image_x = tower.x + (GRID_SIZE - config['tower_size']['width']) // 2
                image_y = tower.y + (GRID_SIZE - config['tower_size']['height']) // 2
                self.screen.blit(tower_image, (image_x, image_y))
            else:
                pygame.draw.circle(self.screen, GREEN, 
                                 (tower.x + GRID_SIZE//2, tower.y + GRID_SIZE//2), 
                                 GRID_SIZE//3)
            
            health_width = 40 * (tower.health / tower.max_health)
            pygame.draw.rect(self.screen, GREEN, 
                           (tower.x + GRID_SIZE//4, tower.y - 10, health_width, 5))
            
            for projectile in tower.projectiles:
                pygame.draw.circle(self.screen, GREEN,
                                 (int(projectile.x), int(projectile.y)),
                                 projectile.radius)

    def _draw_enemies(self, enemies):
        for enemy in enemies:
            pygame.draw.rect(self.screen, RED, 
                           (enemy.x - 20, enemy.y - 20, 40, 40))
            health_width = 40 * (enemy.health / enemy.max_health)
            pygame.draw.rect(self.screen, RED, 
                           (enemy.x - 20, enemy.y - 30, health_width, 5))

    def _draw_game_stats(self, game_state):
        stats = [
            (f'金幣: {game_state.money}', (10, 10)),
            (f'分數: {game_state.score}', (200, 10)),
            (f'生命: {game_state.lives}', (400, 10)),
            (f'波數: {game_state.wave}', (600, 10))
        ]
        
        for text, pos in stats:
            surface = self.game_font.render(text, True, BLACK)
            self.screen.blit(surface, pos)

    def _draw_game_over(self):
        game_over_text = self.game_font.render('遊戲結束！', True, RED)
        self.screen.blit(game_over_text, 
                        (WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2))

class GameLogic:
    def __init__(self, game_state):
        self.game_state = game_state

    def update(self):
        self._spawn_enemy()
        self._update_enemies()
        self._tower_attack()
        self._update_projectiles()

    def _spawn_enemy(self):
        self.game_state.spawn_timer += 1
        if self.game_state.spawn_timer >= 60:
            row = random.randint(0, GRID_ROWS-1)
            self.game_state.enemies.append(Enemy(row))
            self.game_state.spawn_timer = 0

    def _update_enemies(self):
        for enemy in self.game_state.enemies[:]:
            if enemy.current_target:
                if enemy.attack_cooldown <= 0:
                    enemy.current_target.health -= enemy.attack_power
                    enemy.attack_cooldown = 30
                    
                    if enemy.current_target.health <= 0:
                        self.game_state.towers.remove(enemy.current_target)
                        enemy.current_target = None
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

    def _tower_attack(self):
        for tower in self.game_state.towers:
            tower.projectiles = [p for p in tower.projectiles if p.move()]
            
            if tower.attack_cooldown > 0:
                tower.attack_cooldown -= 1
                continue

            tower_center = (tower.x + GRID_SIZE//2, tower.y + GRID_SIZE//2)
            for enemy in self.game_state.enemies:
                enemy_center = (enemy.x, enemy.y)
                distance = math.sqrt((tower_center[0] - enemy_center[0])**2 + 
                                   (tower_center[1] - enemy_center[1])**2)
                
                if distance <= tower.attack_range:
                    projectile = Projectile(tower_center[0], tower_center[1], enemy, self.game_state)  
                    tower.projectiles.append(projectile)
                    tower.attack_cooldown = 30
                    break

    def _update_projectiles(self):
        for tower in self.game_state.towers:
            for projectile in tower.projectiles[:]:
                if projectile.target is None or projectile.target not in self.game_state.enemies:
                    tower.projectiles.remove(projectile)
                    continue
                
                dx = projectile.target.x - projectile.x
                dy = projectile.target.y - projectile.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance < 10:
                    projectile.target.health -= 1
                    tower.projectiles.remove(projectile)
                    
                    if projectile.target.health <= 0:
                        self.game_state.enemies.remove(projectile.target)
                        self.game_state.money += 25
                        self.game_state.score += 10

class EventHandler:
    def __init__(self, game_state):
        self.game_state = game_state

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_state.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_click(event.pos)

    def _handle_mouse_click(self, pos):
        if (GRID_MARGIN <= pos[0] <= WINDOW_WIDTH - GRID_MARGIN and
            GRID_MARGIN <= pos[1] <= WINDOW_HEIGHT - GRID_MARGIN):
            col = (pos[0] - GRID_MARGIN) // GRID_SIZE
            row = (pos[1] - GRID_MARGIN) // GRID_SIZE
            if self.game_state.can_place_tower(col, row):
                self.game_state.place_tower(col, row)

def main():
    clock = pygame.time.Clock()
    game_state = GameState()
    game_logic = GameLogic(game_state)
    game_renderer = GameRenderer(screen, game_font)
    event_handler = EventHandler(game_state)
    
    while game_state.running:
        event_handler.handle_events()
        game_logic.update()
        game_renderer.render(game_state)
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
