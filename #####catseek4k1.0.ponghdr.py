import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Game constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
BALL_SIZE = 15
PADDLE_SPEED = 7
AI_SPEED = 5
BALL_SPEED_X = 5
BALL_SPEED_Y = 5
FPS = 60

# Grayscale colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
MEDIUM_GRAY = (150, 150, 150)
DARK_GRAY = (50, 50, 50)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Retro Pong")
clock = pygame.time.Clock()

# Font setup
font = pygame.font.SysFont('monospace', 32)
small_font = pygame.font.SysFont('monospace', 24)
large_font = pygame.font.SysFont('monospace', 64, bold=True)

# Create simple sound effects
def create_beep_sound(frequency=440, duration=100):
    sample_rate = 44100
    n_samples = int(round(duration * 0.001 * sample_rate))
    
    buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
    max_sample = 2**(16 - 1) - 1
    
    for s in range(n_samples):
        t = float(s) / sample_rate
        buf[s][0] = int(round(max_sample * math.sin(2 * math.pi * frequency * t)))
        buf[s][1] = int(round(max_sample * math.sin(2 * math.pi * frequency * t)))
    
    sound = pygame.sndarray.make_sound(buf)
    return sound

try:
    import numpy
    # Create sound effects
    beep_sound = create_beep_sound(523, 50)  # C5
    boop_sound = create_beep_sound(349, 100)  # F4
    score_sound = create_beep_sound(784, 150)  # G5
except ImportError:
    # Fallback if numpy is not available
    beep_sound = pygame.mixer.Sound(pygame.surface.Surface((1, 1)))
    boop_sound = pygame.mixer.Sound(pygame.surface.Surface((1, 1)))
    score_sound = pygame.mixer.Sound(pygame.surface.Surface((1, 1)))
    print("Note: Numpy not installed. Sound effects disabled.")

class Paddle:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = 0
        self.score = 0
    
    def move(self):
        self.rect.y += self.speed
        
        # Keep paddle on screen
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
    
    def draw(self, surface):
        # Draw paddle with a retro 3D effect
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect)
        pygame.draw.rect(surface, MEDIUM_GRAY, self.rect, 3)
        pygame.draw.line(surface, DARK_GRAY, (self.rect.left, self.rect.top), 
                        (self.rect.left, self.rect.bottom), 2)

class Ball:
    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)
        self.speed_x = BALL_SPEED_X * random.choice([-1, 1])
        self.speed_y = BALL_SPEED_Y * random.choice([-1, 1])
        self.reset_position()
    
    def reset_position(self):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed_x = BALL_SPEED_X * random.choice([-1, 1])
        self.speed_y = BALL_SPEED_Y * random.choice([-1, 1])
    
    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Bounce off top and bottom
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed_y *= -1
            beep_sound.play()
        
        # Reset if ball goes out of bounds
        if self.rect.left <= 0:
            return "right"
        if self.rect.right >= WIDTH:
            return "left"
        return None
    
    def draw(self, surface):
        # Draw ball with a simple retro effect
        pygame.draw.rect(surface, WHITE, self.rect)
        pygame.draw.rect(surface, MEDIUM_GRAY, self.rect, 2)
        pygame.draw.circle(surface, DARK_GRAY, self.rect.center, self.rect.width // 4, 1)

def draw_net(surface):
    """Draw a dashed line down the middle of the court"""
    dash_height = 20
    dash_gap = 10
    for y in range(0, HEIGHT, dash_height + dash_gap):
        pygame.draw.rect(surface, MEDIUM_GRAY, (WIDTH // 2 - 2, y, 4, dash_height))

def draw_score(surface, left_score, right_score):
    """Draw the score at the top of the screen"""
    left_text = font.render(str(left_score), True, LIGHT_GRAY)
    right_text = font.render(str(right_score), True, LIGHT_GRAY)
    surface.blit(left_text, (WIDTH // 4 - left_text.get_width() // 2, 20))
    surface.blit(right_text, (3 * WIDTH // 4 - right_text.get_width() // 2, 20))
    
    # Draw score labels
    player_label = small_font.render("PLAYER", True, MEDIUM_GRAY)
    ai_label = small_font.render("CPU", True, MEDIUM_GRAY)
    surface.blit(player_label, (WIDTH // 4 - player_label.get_width() // 2, 60))
    surface.blit(ai_label, (3 * WIDTH // 4 - ai_label.get_width() // 2, 60))

def draw_game_over(surface, winner):
    """Draw the game over screen"""
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(BLACK)
    surface.blit(overlay, (0, 0))
    
    # Draw winner text
    winner_text = large_font.render(f"{winner} WINS!", True, LIGHT_GRAY)
    surface.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT // 2 - 50))
    
    # Draw restart instruction
    restart_text = small_font.render("Press SPACE to play again", True, MEDIUM_GRAY)
    surface.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 30))
    
    # Draw quit instruction
    quit_text = small_font.render("Press ESC to quit", True, MEDIUM_GRAY)
    surface.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 70))

def main():
    # Create paddles and ball
    player = Paddle(30, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ai = Paddle(WIDTH - 30 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_SIZE)
    
    game_active = True
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if not game_active and event.key == pygame.K_SPACE:
                    # Reset game
                    player.score = 0
                    ai.score = 0
                    ball.reset_position()
                    game_active = True
        
        if game_active:
            # Mouse controls for player paddle
            mouse_y = pygame.mouse.get_pos()[1]
            player.rect.centery = mouse_y
            
            # Keep paddle on screen
            if player.rect.top < 0:
                player.rect.top = 0
            if player.rect.bottom > HEIGHT:
                player.rect.bottom = HEIGHT
            
            # Simple AI for the opponent paddle
            if ai.rect.centery < ball.rect.centery:
                ai.rect.y += AI_SPEED
            elif ai.rect.centery > ball.rect.centery:
                ai.rect.y -= AI_SPEED
            
            # Move the ball
            result = ball.move()
            
            # Handle scoring
            if result == "left":
                ai.score += 1
                score_sound.play()
                ball.reset_position()
            elif result == "right":
                player.score += 1
                score_sound.play()
                ball.reset_position()
            
            # Check for collisions
            if ball.rect.colliderect(player.rect):
                # Calculate bounce angle based on where the ball hit the paddle
                relative_intersect_y = (player.rect.centery - ball.rect.centery) / (PADDLE_HEIGHT / 2)
                bounce_angle = relative_intersect_y * 0.8  # Limit the angle
                
                ball.speed_x = abs(ball.speed_x) * 1.05  # Increase speed slightly
                ball.speed_y = -ball.speed_x * bounce_angle
                boop_sound.play()
            
            if ball.rect.colliderect(ai.rect):
                # Calculate bounce angle based on where the ball hit the paddle
                relative_intersect_y = (ai.rect.centery - ball.rect.centery) / (PADDLE_HEIGHT / 2)
                bounce_angle = relative_intersect_y * 0.8  # Limit the angle
                
                ball.speed_x = -abs(ball.speed_x) * 1.05  # Increase speed slightly
                ball.speed_y = -ball.speed_x * bounce_angle
                boop_sound.play()
            
            # Check for win condition
            if player.score >= 10 or ai.score >= 10:
                game_active = False
        
        # Drawing
        screen.fill(BLACK)
        
        # Draw court elements
        draw_net(screen)
        pygame.draw.rect(screen, DARK_GRAY, (0, 0, WIDTH, HEIGHT), 10)
        
        # Draw paddles and ball
        player.draw(screen)
        ai.draw(screen)
        ball.draw(screen)
        
        # Draw score
        draw_score(screen, player.score, ai.score)
        
        # Draw game over screen if game is over
        if not game_active:
            winner = "PLAYER" if player.score >= 10 else "CPU"
            draw_game_over(screen, winner)
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
