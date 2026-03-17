import pygame
import random
import math
import os  # Faylın mövcudluğunu yoxlamaq üçün

# --- AYARLAR ---
WIDTH, HEIGHT = 450, 750
GRID_SIZE = 8
CELL_SIZE = WIDTH // GRID_SIZE
FPS = 60
COLORS = [(255, 50, 100), (50, 255, 150), (50, 150, 255), (255, 200, 50), (200, 80, 255)]

# Rekordu fayldan oxumaq funksiyası
def get_high_score():
    if not os.path.exists("record.txt"):
        return 0
    try:
        with open("record.txt", "r") as f:
            return int(f.read())
    except:
        return 0

# Rekordu fayla yazmaq funksiyası
def save_high_score(score):
    with open("record.txt", "w") as f:
        f.write(str(score))

class Bubble:
    def __init__(self, col, row, color):
        self.col, self.row = col, row
        self.color = color
        self.x = col * CELL_SIZE
        self.target_y = row * CELL_SIZE
        self.curr_y = -100 - (row * 60)
        self.vel_y = 0
        self.is_falling = True
        self.radius = (CELL_SIZE // 2) - 6

    def update(self):
        if self.is_falling:
            self.vel_y += 0.8
            self.curr_y += self.vel_y
            if self.curr_y >= self.target_y:
                self.curr_y = self.target_y
                self.vel_y *= -0.3
                if abs(self.vel_y) < 1: self.is_falling = False

    def draw(self, screen):
        cx, cy = self.x + CELL_SIZE // 2, int(self.curr_y) + CELL_SIZE // 2
        pygame.draw.circle(screen, self.color, (cx, cy), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (cx - 5, cy - 5), 4)

def draw_text(screen, text, size, x, y, color=(255, 255, 255), center=False):
    try:
        font = pygame.font.SysFont("Segoe UI", size, bold=True)
        img = font.render(str(text), True, color)
        if center:
            rect = img.get_rect(center=(x, y))
            screen.blit(img, rect)
        else:
            screen.blit(img, (x, y))
    except:
        pass

def menu(screen, high_score):
    options = [15, 30, 60, 90, 120, 180]
    buttons = []
    for i, t in enumerate(options):
        bx = 60 + (i % 2 * 180)
        by = 350 + (i // 2 * 85)
        buttons.append({"rect": pygame.Rect(bx, by, 150, 65), "time": t})

    while True:
        screen.fill((25, 25, 45))
        draw_text(screen, "BUBBLE BLAST", 45, WIDTH//2, 120, (0, 255, 200), True)
        # Rekordu menyuda göstər
        draw_text(screen, f"EN YUKSEK XAL: {high_score}", 24, WIDTH//2, 200, (255, 215, 0), True)
        draw_text(screen, "VAXTI SECIN", 20, WIDTH//2, 280, (200, 200, 200), True)
        
        mx, my = pygame.mouse.get_pos()
        for btn in buttons:
            color = (100, 100, 180) if btn["rect"].collidepoint(mx, my) else (60, 60, 90)
            pygame.draw.rect(screen, color, btn["rect"], border_radius=15)
            draw_text(screen, f"{btn['time']} san", 20, btn["rect"].centerx, btn["rect"].centery, True)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in buttons:
                    if btn["rect"].collidepoint(event.pos):
                        return btn["time"]

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bubble Blast")
    clock = pygame.time.Clock()
    
    high_score = get_high_score()
    selected_time = menu(screen, high_score)
    if selected_time is None:
        pygame.quit()
        return

    pop_sound = None
    try:
        pygame.mixer.music.load("theme_song.mp3")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
        pop_sound = pygame.mixer.Sound("pop.mp3")
    except:
        print("Sesler yuklenmedi.")

    bubbles = [Bubble(c, r, random.choice(COLORS)) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]
    start_ticks = pygame.time.get_ticks()
    score = 0
    game_over = False
    record_updated = False

    running = True
    while running:
        if not game_over:
            seconds = (pygame.time.get_ticks() - start_ticks) // 1000
            time_left = max(0, selected_time - seconds)
            if time_left == 0:
                game_over = True
                # Oyun bitəndə rekordu yoxla və yadda saxla
                if score > high_score:
                    save_high_score(score)
                    high_score = score
                    record_updated = True

        screen.fill((15, 15, 25))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                mx, my = pygame.mouse.get_pos()
                for b in bubbles[:]:
                    if math.hypot(mx - (b.x + CELL_SIZE//2), my - (b.curr_y + CELL_SIZE//2)) < b.radius:
                        if pop_sound:
                            pop_sound.play()
                        bubbles.remove(b)
                        bubbles.append(Bubble(b.col, b.row, random.choice(COLORS)))
                        score += 10

        for b in bubbles:
            b.update()
            b.draw(screen)

        # UI paneli
        pygame.draw.rect(screen, (30, 30, 50), (0, HEIGHT-100, WIDTH, 100))
        draw_text(screen, f"VAXT: {time_left}", 25, 30, HEIGHT - 70)
        draw_text(screen, f"XAL: {score}", 25, WIDTH - 150, HEIGHT - 70)

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0,0))
            draw_text(screen, "OYUN BITDI!", 45, WIDTH//2, HEIGHT//2 - 50, (255, 50, 50), True)
            
            final_txt = f"XALINIZ: {score}"
            draw_text(screen, final_txt, 30, WIDTH//2, HEIGHT//2 + 10, (255, 255, 255), True)
            
            if record_updated:
                draw_text(screen, "YENI REKORD!", 30, WIDTH//2, HEIGHT//2 + 50, (255, 215, 0), True)
            else:
                draw_text(screen, f"REKORD: {high_score}", 24, WIDTH//2, HEIGHT//2 + 50, (200, 200, 200), True)

            draw_text(screen, "Restart ucun R-e bas", 20, WIDTH//2, HEIGHT//2 + 110, center=True)
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                main()
                return

        pygame.display.flip()
        clock.tick(FPS)
pygame.quit()

if __name__ == "__main__":
    main()