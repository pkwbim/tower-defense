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

# 遊戲變數
money = 100
score = 0
lives = 10

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
    def __init__(self, x, y, target):
        self.x = x
        self.y = y
        self.target = target
        self.speed = 5
        self.radius = 5

    def move(self):
        if self.target is None or self.target not in enemies:
            return False
        
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < self.speed:
            return False
        
        self.x += (dx / distance) * self.speed
        self.y += (dy / distance) * self.speed
        return True

# 遊戲狀態
towers = []
enemies = []
game_grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
spawn_timer = 0
wave = 1

def draw_grid():
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            x = GRID_MARGIN + col * GRID_SIZE
            y = GRID_MARGIN + row * GRID_SIZE
            pygame.draw.rect(screen, BLACK, (x, y, GRID_SIZE, GRID_SIZE), 1)

def draw_towers():
    for tower in towers:
        # 如果有圖片就使用圖片，否則用圓形
        if tower_image:
            # 計算圖片位置（置中於格子）
            image_x = tower.x + (GRID_SIZE - config['tower_size']['width']) // 2
            image_y = tower.y + (GRID_SIZE - config['tower_size']['height']) // 2
            screen.blit(tower_image, (image_x, image_y))
        else:
            # 如果沒有圖片，退回使用綠色圓形
            pygame.draw.circle(screen, GREEN, 
                             (tower.x + GRID_SIZE//2, tower.y + GRID_SIZE//2), 
                             GRID_SIZE//3)
        
        # 畫血條
        health_width = 40 * (tower.health / tower.max_health)
        pygame.draw.rect(screen, GREEN, 
                        (tower.x + GRID_SIZE//4, tower.y - 10, health_width, 5))
        # 畫炮彈
        for projectile in tower.projectiles:
            pygame.draw.circle(screen, BLACK,
                             (int(projectile.x), int(projectile.y)),
                             projectile.radius)

def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(screen, RED, 
                        (enemy.x - 20, enemy.y - 20, 40, 40))
        # 繪製血條
        health_width = 40 * (enemy.health / enemy.max_health)
        pygame.draw.rect(screen, RED, 
                        (enemy.x - 20, enemy.y - 30, health_width, 5))

def update_enemies():
    global lives
    for enemy in enemies[:]:
        if enemy.current_target:
            # 如果有目標，進行攻擊
            if enemy.attack_cooldown <= 0:
                enemy.current_target.health -= enemy.attack_power
                enemy.attack_cooldown = 30  # 設置攻擊冷卻時間
                
                # 檢查防禦塔是否被摧毀
                if enemy.current_target.health <= 0:
                    towers.remove(enemy.current_target)
                    enemy.current_target = None
            else:
                enemy.attack_cooldown -= 1
        else:
            # 檢查前方是否有防禦塔
            enemy_col = (enemy.x - GRID_MARGIN) // GRID_SIZE
            enemy_row = (enemy.y - GRID_MARGIN) // GRID_SIZE
            
            # 檢查當前位置的前一格是否有防禦塔
            for tower in towers:
                tower_col = (tower.x - GRID_MARGIN) // GRID_SIZE
                tower_row = (tower.y - GRID_MARGIN) // GRID_SIZE
                
                # 如果在同一行，且防禦塔在殭屍前方
                if (tower_row == enemy_row and 
                    tower_col < enemy_col and 
                    abs(enemy.x - (tower.x + GRID_SIZE)) < enemy.speed):
                    enemy.current_target = tower
                    break
            
            # 如果沒有目標，繼續移動
            if not enemy.current_target:
                enemy.x -= enemy.speed
                
                # 如果到達最左邊
                if enemy.x < 0:
                    enemies.remove(enemy)
                    lives -= 1

def spawn_enemy():
    global spawn_timer
    spawn_timer += 1
    if spawn_timer >= 60:  # 每秒產生一個敵人
        row = random.randint(0, GRID_ROWS-1)
        enemies.append(Enemy(row))
        spawn_timer = 0

def tower_attack():
    for tower in towers:
        # 更新炮彈
        tower.projectiles = [p for p in tower.projectiles if p.move()]
        
        # 檢查冷卻時間
        if tower.attack_cooldown > 0:
            tower.attack_cooldown -= 1
            continue

        tower_center = (tower.x + GRID_SIZE//2, tower.y + GRID_SIZE//2)
        for enemy in enemies:
            enemy_center = (enemy.x, enemy.y)
            distance = math.sqrt((tower_center[0] - enemy_center[0])**2 + 
                               (tower_center[1] - enemy_center[1])**2)
            
            if distance <= tower.attack_range:
                # 發射新炮彈
                projectile = Projectile(tower_center[0], tower_center[1], enemy)
                tower.projectiles.append(projectile)
                tower.attack_cooldown = 30  # 設置冷卻時間
                break

def update_projectiles():
    for tower in towers:
        for projectile in tower.projectiles[:]:
            if projectile.target is None or projectile.target not in enemies:
                tower.projectiles.remove(projectile)
                continue
            
            # 檢查是否擊中目標
            dx = projectile.target.x - projectile.x
            dy = projectile.target.y - projectile.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < 10:  # 擊中判定範圍
                projectile.target.health -= 1
                tower.projectiles.remove(projectile)
                
                if projectile.target.health <= 0:
                    enemies.remove(projectile.target)
                    global money, score
                    money += 25
                    score += 10

# 遊戲主循環
def main():
    global money
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # 事件處理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # 檢查是否在格子內點擊
                if (GRID_MARGIN <= mouse_pos[0] <= WINDOW_WIDTH - GRID_MARGIN and
                    GRID_MARGIN <= mouse_pos[1] <= WINDOW_HEIGHT - GRID_MARGIN):
                    col = (mouse_pos[0] - GRID_MARGIN) // GRID_SIZE
                    row = (mouse_pos[1] - GRID_MARGIN) // GRID_SIZE
                    if col < GRID_COLS and money >= 50:
                        tower_x = GRID_MARGIN + col * GRID_SIZE
                        tower_y = GRID_MARGIN + row * GRID_SIZE
                        if game_grid[row][col] == 0:
                            towers.append(Tower(tower_x, tower_y))
                            game_grid[row][col] = 1
                            money -= 50
        
        # 遊戲邏輯更新
        spawn_enemy()
        update_enemies()
        tower_attack()
        update_projectiles()
        
        # 清空畫面
        screen.fill(WHITE)
        
        # 繪製遊戲元素
        draw_grid()
        draw_towers()
        draw_enemies()
        
        # 繪製遊戲狀態
        money_text = game_font.render(f'金幣: {money}', True, BLACK)
        score_text = game_font.render(f'分數: {score}', True, BLACK)
        lives_text = game_font.render(f'生命: {lives}', True, BLACK)
        wave_text = game_font.render(f'波數: {wave}', True, BLACK)
        
        screen.blit(money_text, (10, 10))
        screen.blit(score_text, (200, 10))
        screen.blit(lives_text, (400, 10))
        screen.blit(wave_text, (600, 10))
        
        # 檢查遊戲結束條件
        if lives <= 0:
            game_over_text = game_font.render('遊戲結束！', True, RED)
            screen.blit(game_over_text, (WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2))
        
        # 更新畫面
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
