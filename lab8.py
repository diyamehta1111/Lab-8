import pygame
import random


# INITIALIZE PYGAME

pygame.init()
pygame.mixer.init()


# GAME SETUP

screen_width = 800
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Skater Collector Game")
clock = pygame.time.Clock()

# COLORS

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 100, 200)
RED = (200, 50, 50)
YELLOW = (255, 215, 0)
GREEN = (50, 200, 50)
BROWN = (139, 69, 19)
GRAY = (50, 50, 50)


# CREATE SIMPLE SOUND EFFECTS

try:
    import numpy as np
    
    def create_sound(frequency, duration):
        """Create a simple beep sound"""
        sample_rate = 22050
        n_samples = int(round(duration * sample_rate))
        buf = np.zeros((n_samples, 2), dtype=np.int16)
        for i in range(n_samples):
            value = int(32767 * 0.3 * ((i % int(sample_rate / frequency)) < (sample_rate / frequency / 2)))
            buf[i] = [value, value]
        sound = pygame.sndarray.make_sound(buf)
        return sound
    
    # Created different sound effects for the game
    coin_sound = create_sound(800, 0.1)
    jump_sound = create_sound(400, 0.05)
    hit_sound = create_sound(200, 0.2)
    
except ImportError:
    print("NumPy not found - sounds disabled. Install with: pip install numpy")
    class DummySound:
        def play(self):
            pass
    coin_sound = DummySound()
    jump_sound = DummySound()
    hit_sound = DummySound()


# GROUND POSITION

ground_y = 300


# PLAYER (SKATER) VARIABLES

player_x = 100
player_y = ground_y - 60
player_width = 50
player_height = 60
player_velocity_y = 0
gravity = 0.8
jump_strength = -15
animation_frame = 0


# OBSTACLE VARIABLES

obstacle_width = 20
obstacle_height = 50
base_obstacle_speed = 5
obstacle_speed = base_obstacle_speed
obstacles = []


# COIN VARIABLES

coin_width = 25
coin_height = 25
coins = []
coin_timer = 0
coin_spawn_rate = 120


# SCORE VARIABLES

score = 0
coins_collected = 0
distance = 0


# GAME STATE

game_state = "start"


# HELPER FUNCTIONS


def reset_game():
    """Reset all variables to start new game"""
    global player_y, player_velocity_y, obstacles, coins
    global score, coins_collected, distance, obstacle_speed, coin_timer, animation_frame
    
    player_y = ground_y - 60
    player_velocity_y = 0
    animation_frame = 0
    
    obstacles = []
    obstacles.append(screen_width)
    coins = []
    
    score = 0
    coins_collected = 0
    distance = 0
    
    obstacle_speed = base_obstacle_speed
    coin_timer = 0

def draw_skater(x, y, frame):
    """Draw a simple person on skateboard"""
    # Head
    pygame.draw.circle(screen, BLACK, (int(x + 25), int(y + 10)), 8)
    
    # Body
    pygame.draw.line(screen, BLACK, (x + 25, y + 18), (x + 25, y + 35), 3)
    
    # Arms (animated)
    arm_offset = 2 if frame % 20 < 10 else -2
    pygame.draw.line(screen, BLACK, (x + 25, y + 22), (x + 15 + arm_offset, y + 28), 3)
    pygame.draw.line(screen, BLACK, (x + 25, y + 22), (x + 35 - arm_offset, y + 28), 3)
    
    # Legs (animated for running effect)
    leg_offset = 3 if frame % 20 < 10 else -3
    pygame.draw.line(screen, BLACK, (x + 25, y + 35), (x + 20 + leg_offset, y + 48), 3)
    pygame.draw.line(screen, BLACK, (x + 25, y + 35), (x + 30 - leg_offset, y + 48), 3)
    
    # Skateboard
    board_y = y + 50
    pygame.draw.rect(screen, BROWN, (x + 10, board_y, 30, 5))
    
    # Wheels
    pygame.draw.circle(screen, GRAY, (int(x + 15), int(board_y + 7)), 4)
    pygame.draw.circle(screen, GRAY, (int(x + 35), int(board_y + 7)), 4)
    
    # Wheel rotation effect
    if frame % 4 < 2:
        pygame.draw.line(screen, WHITE, (x + 15, board_y + 4), (x + 15, board_y + 10), 1)
        pygame.draw.line(screen, WHITE, (x + 35, board_y + 4), (x + 35, board_y + 10), 1)

def check_collision(x1, y1, w1, h1, x2, y2, w2, h2):
    """Check if two rectangles overlap"""
    if (x1 < x2 + w2 and
        x1 + w1 > x2 and
        y1 < y2 + h2 and
        y1 + h1 > y2):
        return True
    return False


# MAIN GAME LOOP

game_running = True

while game_running:
    

    # HANDLE EVENTS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False
        
        if event.type == pygame.KEYDOWN:
            if game_state == "start":
                if event.key == pygame.K_SPACE:
                    game_state = "playing"
                    reset_game()
            
            elif game_state == "playing":
                if event.key == pygame.K_SPACE:
                    if player_y >= ground_y - 60:
                        player_velocity_y = jump_strength
                        jump_sound.play()
                elif event.key == pygame.K_p:
                    game_state = "paused"
            
            elif game_state == "paused":
                if event.key == pygame.K_p:
                    game_state = "playing"
            
            elif game_state == "game_over":
                if event.key == pygame.K_SPACE:
                    game_state = "playing"
                    reset_game()
    
    # UPDATE GAME
    
    if game_state == "playing":
        
        animation_frame = animation_frame + 1
        
        # Update player physics
        player_velocity_y = player_velocity_y + gravity
        player_y = player_y + player_velocity_y
        
        if player_y >= ground_y - 60:
            player_y = ground_y - 60
            player_velocity_y = 0
        
        # Move obstacles
        for i in range(len(obstacles)):
            obstacles[i] = obstacles[i] - obstacle_speed
        
        # Remove off-screen obstacles and spawn new ones
        if len(obstacles) > 0 and obstacles[0] < -obstacle_width:
            obstacles.pop(0)
            if len(obstacles) > 0:
                new_x = obstacles[-1] + random.randint(300, 500)
            else:
                new_x = screen_width
            obstacles.append(new_x)
        
        # Check collision with obstacles
        for obstacle_x in obstacles:
            if check_collision(player_x, player_y, player_width, player_height,
                             obstacle_x, ground_y - obstacle_height, obstacle_width, obstacle_height):
                hit_sound.play()
                game_state = "game_over"
        
        # Spawn coins
        coin_timer = coin_timer + 1
        if coin_timer >= coin_spawn_rate:
            coin_x = screen_width
            if random.random() < 0.5:
                coin_y = ground_y - coin_height
            else:
                coin_y = ground_y - 100 - random.randint(0, 50)
            coins.append([coin_x, coin_y])
            coin_timer = 0
        
        # Move coins
        for coin in coins:
            coin[0] = coin[0] - obstacle_speed
        
        coins = [coin for coin in coins if coin[0] > -coin_width]
        
        # Check coin collection
        for coin in coins[:]:
            if check_collision(player_x, player_y, player_width, player_height,
                             coin[0], coin[1], coin_width, coin_height):
                coins.remove(coin)
                coins_collected = coins_collected + 1
                score = score + 10
                coin_sound.play()
        
        # Update score
        distance = distance + 1
        if distance % 10 == 0:
            score = score + 1
        
        # Increase difficulty
        if distance % 500 == 0 and distance > 0:
            obstacle_speed = obstacle_speed + 0.5
    
    
    # DRAW EVERYTHING
   
    screen.fill(WHITE)
    pygame.draw.line(screen, BLACK, (0, ground_y), (screen_width, ground_y), 2)
    
    if game_state == "start":
        font_large = pygame.font.Font(None, 64)
        title = font_large.render("SKATER COLLECTOR", True, BLACK)
        title_rect = title.get_rect(center=(screen_width // 2, 80))
        screen.blit(title, title_rect)
        
        font_small = pygame.font.Font(None, 28)
        instructions = [
            ("HOW TO PLAY:", 150, BLACK),
            ("Press SPACE to JUMP", 190, BLACK),
            ("Avoid RED obstacles", 220, RED),
            ("Collect YELLOW coins for points", 250, YELLOW),
            ("Press P to PAUSE", 280, BLACK),
            ("", 310, BLACK),
            ("HOW TO WIN:", 340, GREEN),
            ("Skate as long as possible!", 370, GREEN),
        ]
        
        for text, y_pos, color in instructions:
            if text:
                text_surface = font_small.render(text, True, color)
                text_rect = text_surface.get_rect(center=(screen_width // 2, y_pos))
                screen.blit(text_surface, text_rect)
        
        font_medium = pygame.font.Font(None, 32)
        start_text = font_medium.render("Press SPACE to Start", True, BLUE)
        start_rect = start_text.get_rect(center=(screen_width // 2, screen_height - 40))
        screen.blit(start_text, start_rect)
    
    elif game_state == "playing" or game_state == "paused":
        
        draw_skater(player_x, player_y, animation_frame)
        
        for obstacle_x in obstacles:
            pygame.draw.rect(screen, RED, 
                           (obstacle_x, ground_y - obstacle_height, obstacle_width, obstacle_height))
        
        for coin in coins:
            pygame.draw.circle(screen, YELLOW, 
                             (int(coin[0] + coin_width // 2), int(coin[1] + coin_height // 2)), 
                             coin_width // 2)
        
        font = pygame.font.Font(None, 32)
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))
        
        coins_text = font.render(f"Coins: {coins_collected}", True, YELLOW)
        screen.blit(coins_text, (10, 45))
        
        if game_state == "paused":
            font_large = pygame.font.Font(None, 72)
            pause_text = font_large.render("PAUSED", True, BLACK)
            pause_rect = pause_text.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(pause_text, pause_rect)
            
            font_small = pygame.font.Font(None, 36)
            resume_text = font_small.render("Press P to Resume", True, BLACK)
            resume_rect = resume_text.get_rect(center=(screen_width // 2, screen_height // 2 + 60))
            screen.blit(resume_text, resume_rect)
    
    elif game_state == "game_over":
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)
        
        game_over_text = font_large.render("GAME OVER!", True, RED)
        game_over_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 2 - 60))
        screen.blit(game_over_text, game_over_rect)
        
        score_text = font_medium.render(f"Final Score: {score}", True, BLACK)
        score_rect = score_text.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(score_text, score_rect)
        
        coins_text = font_small.render(f"Coins Collected: {coins_collected}", True, YELLOW)
        coins_rect = coins_text.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
        screen.blit(coins_text, coins_rect)
        
        restart_text = font_small.render("Press SPACE to Play Again", True, BLUE)
        restart_rect = restart_text.get_rect(center=(screen_width // 2, screen_height - 40))
        screen.blit(restart_text, restart_rect)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
