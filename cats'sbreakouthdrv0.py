import pygame
import sys
import random
import array

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Game constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 20
BALL_SIZE = 15
BRICK_WIDTH, BRICK_HEIGHT = 75, 30
PADDLE_Y = HEIGHT - 50
FPS = 60

# Colors (grayscale)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Sound effects
sample_rate = 44100
beep = pygame.mixer.Sound(buffer=array.array('h', [32000 if x < 1000 else -32000 for x in range(2000)] * 10))
boop = pygame.mixer.Sound(buffer=array.array('h', [32000 if x < 500 else -32000 for x in range(1000)] * 20))
boop.set_volume(0.5)

class Brick:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Retro Breakout')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        self.reset_game()

    def reset_game(self):
        self.paddle = pygame.Rect(WIDTH//2 - PADDLE_WIDTH//2, PADDLE_Y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.ball = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2, BALL_SIZE, BALL_SIZE)
        self.ball_speed = [random.choice([-5, 5]), -5]
        
        # Create bricks
        self.bricks = []
        for y in range(5):
            for x in range(WIDTH // BRICK_WIDTH):
                self.bricks.append(Brick(x * BRICK_WIDTH, y * BRICK_HEIGHT + 50))
        
        self.score = 0
        self.lives = 3
        self.running = True

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # Mouse controls
        mouse_x = pygame.mouse.get_pos()[0]
        self.paddle.centerx = mouse_x
        self.paddle.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def update(self):
        # Move ball
        self.ball.x += self.ball_speed[0]
        self.ball.y += self.ball_speed[1]

        # Wall collisions
        if self.ball.left <= 0 or self.ball.right >= WIDTH:
            self.ball_speed[0] *= -1
            beep.play()
        if self.ball.top <= 0:
            self.ball_speed[1] *= -1
            beep.play()
        
        # Bottom wall (lose life)
        if self.ball.bottom >= HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                self.running = False
            else:
                self.ball.center = (WIDTH//2, HEIGHT//2)
                self.ball_speed = [random.choice([-5, 5]), -5]

        # Paddle collision with angle change
        if self.ball.colliderect(self.paddle):
            self.ball_speed[1] *= -1
            offset = (self.ball.centerx - self.paddle.centerx) / (PADDLE_WIDTH/2)
            self.ball_speed[0] = offset * 7  # Adjust angle based on hit position
            beep.play()

        # Brick collisions
        for brick in self.bricks[:]:
            if self.ball.colliderect(brick.rect):
                self.bricks.remove(brick)
                self.ball_speed[1] *= -1
                self.score += 10
                boop.play()
                break

        # Win condition
        if not self.bricks:
            self.running = False

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw paddle
        pygame.draw.rect(self.screen, WHITE, self.paddle)
        
        # Draw ball
        pygame.draw.ellipse(self.screen, WHITE, self.ball)
        
        # Draw bricks
        for brick in self.bricks:
            pygame.draw.rect(self.screen, DARK_GRAY, brick.rect)
            pygame.draw.rect(self.screen, GRAY, brick.rect, 2)
        
        # Draw UI
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        lives_text = self.font.render(f'Lives: {self.lives}', True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (WIDTH - 120, 10))
        
        pygame.display.flip()

    def show_game_over(self):
        text = 'You Win!' if not self.bricks else 'Game Over'
        text_surface = self.font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.screen.blit(text_surface, text_rect)
        pygame.display.flip()
        pygame.time.wait(3000)

    def run(self):
        while True:
            while self.running:
                self.handle_input()
                self.update()
                self.draw()
                self.clock.tick(FPS)
            
            self.show_game_over()
            self.reset_game()

if __name__ == '__main__':
    game = Game()
    game.run()
