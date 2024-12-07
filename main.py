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
        self.spawn_timer = 0
        self.selected_tower = None

def load_image(path, size=None):
    try:
        image = pygame.image.load(path)
        if size:
            image = pygame.transform.scale(image, (size[0], size[1]))
        return image
    except pygame.error:
        return None

class Tower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.projectiles = []
        self.attack_range = CONFIG['tower']['attack_range']
        self.attack_cooldown = 0
        self.health = CONFIG['tower']['initial_health']
        
        # Load tower image
        image_path = CONFIG['images']['tower']
        size = (CONFIG['tower_size']['width'], CONFIG['tower_size']['height'])
        self.image = load_image(image_path, size)

class Enemy:
    def __init__(self, row):
        self.x = WINDOW_WIDTH - GRID_MARGIN
        self.y = GRID_MARGIN + row * GRID_SIZE + GRID_SIZE // 2
        self.speed = CONFIG['enemy']['speed']
        self.radius = CONFIG['enemy']['radius']
        self.health = CONFIG['enemy']['initial_health']
        self.max_health = CONFIG['enemy']['initial_health']
        self.attack_power = CONFIG['enemy']['attack_power']
        self.attack_cooldown = 0
        self.current_target = None

class Projectile:
    def __init__(self, x, y, target, game_state):
        self.x = x
        self.y = y
        self.target = target
        self.speed = CONFIG['projectile']['speed']
        self.radius = CONFIG['projectile']['radius']
        self.game_state = game_state

    def move(self):
        if self.target is None or self.target not in self.game_state.enemies:
            return False
        
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 1:
            self.target.health -= CONFIG['projectile']['damage']
            if self.target.health <= 0:
                self.game_state.enemies.remove(self.target)
                self.game_state.score += 1
                self.game_state.money += 10
            return False
        
        self.x += (dx / distance) * self.speed
        self.y += (dy / distance) * self.speed
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
                pygame.draw.circle(
                    self.screen,
                    tuple(CONFIG['colors']['tower']),
                    (tower.x + GRID_SIZE//2, tower.y + GRID_SIZE//2),
                    GRID_SIZE//2
                )
            # Draw tower health bar
            health_bar_width = GRID_SIZE
            health_bar_height = 5
            health_percentage = tower.health / CONFIG['tower']['initial_health']
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
            pygame.draw.circle(
                self.screen,
                tuple(CONFIG['colors']['enemy']),
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
        for tower in self.game_state.towers:
            for projectile in tower.projectiles:
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
        
        self.screen.blit(money_text, (10, 10))
        self.screen.blit(score_text, (200, 10))
        self.screen.blit(lives_text, (400, 10))

class GameLogic:
    def __init__(self, game_state):
        self.game_state = game_state

    def update(self):
        self._spawn_enemy()
        self._update_enemies()
        self._tower_attack()

    def _spawn_enemy(self):
        self.game_state.spawn_timer += 1
        if self.game_state.spawn_timer >= CONFIG['enemy']['spawn_interval']:
            row = random.randint(0, GRID_ROWS-1)
            self.game_state.enemies.append(Enemy(row))
            self.game_state.spawn_timer = 0

    def _update_enemies(self):
        for enemy in self.game_state.enemies[:]:
            if enemy.current_target:
                if enemy.attack_cooldown <= 0:
                    enemy.current_target.health -= enemy.attack_power
                    enemy.attack_cooldown = CONFIG['enemy']['attack_cooldown']
                    
                    if enemy.current_target.health <= 0:
                        if enemy.current_target in self.game_state.towers:  
                            self.game_state.towers.remove(enemy.current_target)
                        # 
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
                    tower.attack_cooldown = CONFIG['tower']['attack_cooldown']
                    break

class EventHandler:
    def __init__(self, game_state):
        self.game_state = game_state

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    col = (mouse_x - GRID_MARGIN) // GRID_SIZE
                    row = (mouse_y - GRID_MARGIN) // GRID_SIZE
                    
                    if (0 <= row < GRID_ROWS and 0 <= col < GRID_COLS and
                            self.game_state.money >= CONFIG['game']['tower_cost']):
                        tower_x = GRID_MARGIN + col * GRID_SIZE
                        tower_y = GRID_MARGIN + row * GRID_SIZE
                        
                        # Check if tower already exists at this position
                        tower_exists = any(t.x == tower_x and t.y == tower_y 
                                         for t in self.game_state.towers)
                        
                        if not tower_exists:
                            self.game_state.towers.append(Tower(tower_x, tower_y))
                            self.game_state.money -= CONFIG['game']['tower_cost']
        return True

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
