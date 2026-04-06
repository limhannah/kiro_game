import pygame
import random
import sys

# Constants
CELL_SIZE = 20
GRID_W, GRID_H = 30, 20
WIDTH, HEIGHT = CELL_SIZE * GRID_W, CELL_SIZE * GRID_H
FPS = 10

BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
RED = (220, 50, 50)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def spawn_food(snake):
    while True:
        pos = (random.randint(0, GRID_W - 1), random.randint(0, GRID_H - 1))
        if pos not in snake:
            return pos


def draw_text_center(surface, text, font, color, y_offset=0):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    surface.blit(rendered, rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 28)
    small_font = pygame.font.SysFont("consolas", 20)

    def reset():
        snake = [(GRID_W // 2, GRID_H // 2)]
        direction = RIGHT
        food = spawn_food(snake)
        return snake, direction, food, 0, False

    snake, direction, food, score, game_over = reset()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        snake, direction, food, score, game_over = reset()
                    continue
                if event.key == pygame.K_UP and direction != DOWN:
                    direction = UP
                elif event.key == pygame.K_DOWN and direction != UP:
                    direction = DOWN
                elif event.key == pygame.K_LEFT and direction != RIGHT:
                    direction = LEFT
                elif event.key == pygame.K_RIGHT and direction != LEFT:
                    direction = RIGHT

        if not game_over:
            # Move snake
            head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

            # Check collisions
            if (head[0] < 0 or head[0] >= GRID_W or
                    head[1] < 0 or head[1] >= GRID_H or
                    head in snake):
                game_over = True
            else:
                snake.insert(0, head)
                if head == food:
                    score += 1
                    food = spawn_food(snake)
                else:
                    snake.pop()

        # Draw
        screen.fill(BLACK)

        # Draw grid lines
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

        # Draw food
        fx, fy = food[0] * CELL_SIZE, food[1] * CELL_SIZE
        pygame.draw.rect(screen, RED, (fx + 1, fy + 1, CELL_SIZE - 2, CELL_SIZE - 2))

        # Draw snake
        for i, (sx, sy) in enumerate(snake):
            color = GREEN if i == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, (sx * CELL_SIZE + 1, sy * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2))

        # Score
        score_text = small_font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (8, 4))

        if game_over:
            draw_text_center(screen, "GAME OVER", font, RED, -20)
            draw_text_center(screen, f"Score: {score}  |  Press R to restart", small_font, WHITE, 20)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
