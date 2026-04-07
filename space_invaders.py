import pygame
import random
import sys

# Constants
WIDTH, HEIGHT = 600, 700
FPS = 60
PLAYER_SPEED = 5
BULLET_SPEED = 7
ALIEN_BULLET_SPEED = 4
ALIEN_COLS = 8
ALIEN_ROWS = 4
ALIEN_SIZE = 36
ALIEN_PAD = 12
ALIEN_DROP = 20
ALIEN_MOVE_DELAY_START = 40  # frames between alien steps
ALIEN_SHOOT_CHANCE = 0.008

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 220, 80)
RED = (220, 50, 50)
CYAN = (0, 200, 220)
YELLOW = (220, 220, 0)
GRAY = (100, 100, 100)


class Player:
    def __init__(self):
        self.w, self.h = 40, 20
        self.x = WIDTH // 2 - self.w // 2
        self.y = HEIGHT - 60
        self.lives = 3
        self.cooldown = 0

    def draw(self, surf):
        # Ship body
        pygame.draw.rect(surf, GREEN, (self.x, self.y, self.w, self.h))
        # Cannon
        pygame.draw.rect(surf, GREEN, (self.x + self.w // 2 - 3, self.y - 10, 6, 10))

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.x + self.w < WIDTH:
            self.x += PLAYER_SPEED
        if self.cooldown > 0:
            self.cooldown -= 1

    def shoot(self):
        if self.cooldown <= 0:
            self.cooldown = 15
            return Bullet(self.x + self.w // 2 - 2, self.y - 10, -BULLET_SPEED, CYAN)
        return None


class Alien:
    def __init__(self, x, y, row):
        self.x = x
        self.y = y
        self.w = ALIEN_SIZE
        self.h = ALIEN_SIZE - 8
        self.row = row

    def draw(self, surf):
        color = YELLOW if self.row < 2 else WHITE
        # Body
        pygame.draw.rect(surf, color, (self.x + 4, self.y + 6, self.w - 8, self.h - 6))
        # Eyes
        pygame.draw.rect(surf, BLACK, (self.x + 10, self.y + 10, 4, 4))
        pygame.draw.rect(surf, BLACK, (self.x + 22, self.y + 10, 4, 4))
        # Antennae
        pygame.draw.line(surf, color, (self.x + 8, self.y + 6), (self.x + 4, self.y), 2)
        pygame.draw.line(surf, color, (self.x + 28, self.y + 6), (self.x + 32, self.y), 2)

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)


class Bullet:
    def __init__(self, x, y, dy, color):
        self.x = x
        self.y = y
        self.dy = dy
        self.color = color
        self.w, self.h = 4, 12

    def update(self):
        self.y += self.dy

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, (self.x, self.y, self.w, self.h))

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def off_screen(self):
        return self.y < -self.h or self.y > HEIGHT


def create_aliens():
    aliens = []
    start_x = (WIDTH - (ALIEN_COLS * (ALIEN_SIZE + ALIEN_PAD) - ALIEN_PAD)) // 2
    for row in range(ALIEN_ROWS):
        for col in range(ALIEN_COLS):
            x = start_x + col * (ALIEN_SIZE + ALIEN_PAD)
            y = 60 + row * (ALIEN_SIZE + ALIEN_PAD)
            aliens.append(Alien(x, y, row))
    return aliens


def draw_text(surf, text, font, color, x, y):
    rendered = font.render(text, True, color)
    surf.blit(rendered, (x, y))


def draw_text_center(surf, text, font, color, y_offset=0):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    surf.blit(rendered, rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Invaders")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 30)
    small_font = pygame.font.SysFont("consolas", 20)

    def reset():
        player = Player()
        aliens = create_aliens()
        bullets = []
        alien_bullets = []
        alien_dir = 1  # 1 = right, -1 = left
        alien_move_timer = 0
        alien_move_delay = ALIEN_MOVE_DELAY_START
        score = 0
        game_over = False
        won = False
        return player, aliens, bullets, alien_bullets, alien_dir, alien_move_timer, alien_move_delay, score, game_over, won

    player, aliens, bullets, alien_bullets, alien_dir, alien_move_timer, alien_move_delay, score, game_over, won = reset()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_over and event.key == pygame.K_r:
                    player, aliens, bullets, alien_bullets, alien_dir, alien_move_timer, alien_move_delay, score, game_over, won = reset()
                if not game_over and event.key == pygame.K_SPACE:
                    b = player.shoot()
                    if b:
                        bullets.append(b)

        if not game_over:
            keys = pygame.key.get_pressed()
            player.update(keys)

            # Update player bullets
            for b in bullets:
                b.update()
            bullets = [b for b in bullets if not b.off_screen()]

            # Update alien bullets
            for b in alien_bullets:
                b.update()
            alien_bullets = [b for b in alien_bullets if not b.off_screen()]

            # Move aliens
            alien_move_timer += 1
            if alien_move_timer >= alien_move_delay:
                alien_move_timer = 0
                drop = False
                for a in aliens:
                    a.x += 10 * alien_dir
                for a in aliens:
                    if a.x + a.w >= WIDTH - 5 or a.x <= 5:
                        drop = True
                        break
                if drop:
                    alien_dir *= -1
                    for a in aliens:
                        a.y += ALIEN_DROP

            # Alien shooting
            if aliens:
                for a in aliens:
                    if random.random() < ALIEN_SHOOT_CHANCE:
                        alien_bullets.append(Bullet(a.x + a.w // 2 - 2, a.y + a.h, ALIEN_BULLET_SPEED, RED))

            # Collision: player bullets vs aliens
            new_aliens = []
            for a in aliens:
                hit = False
                for b in bullets:
                    if a.rect.colliderect(b.rect):
                        hit = True
                        bullets.remove(b)
                        score += 10
                        break
                if not hit:
                    new_aliens.append(a)
            aliens = new_aliens

            # Speed up as aliens are destroyed
            remaining = len(aliens)
            if remaining > 0:
                alien_move_delay = max(5, ALIEN_MOVE_DELAY_START - (ALIEN_COLS * ALIEN_ROWS - remaining) * 1)

            # Collision: alien bullets vs player
            player_rect = pygame.Rect(player.x, player.y, player.w, player.h)
            for b in alien_bullets:
                if player_rect.colliderect(b.rect):
                    player.lives -= 1
                    alien_bullets.remove(b)
                    if player.lives <= 0:
                        game_over = True
                    break

            # Aliens reach player
            for a in aliens:
                if a.y + a.h >= player.y:
                    game_over = True
                    break

            # Win condition
            if not aliens:
                game_over = True
                won = True

        # Draw
        screen.fill(BLACK)

        # Stars background
        random.seed(42)
        for _ in range(80):
            sx = random.randint(0, WIDTH)
            sy = random.randint(0, HEIGHT)
            screen.set_at((sx, sy), GRAY)
        random.seed()

        player.draw(screen)
        for a in aliens:
            a.draw(screen)
        for b in bullets:
            b.draw(screen)
        for b in alien_bullets:
            b.draw(screen)

        # HUD
        draw_text(screen, f"Score: {score}", small_font, WHITE, 10, 8)
        draw_text(screen, f"Lives: {player.lives}", small_font, GREEN, WIDTH - 120, 8)

        if game_over:
            if won:
                draw_text_center(screen, "YOU WIN!", font, GREEN, -20)
            else:
                draw_text_center(screen, "GAME OVER", font, RED, -20)
            draw_text_center(screen, f"Score: {score}  |  Press R to restart", small_font, WHITE, 20)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
