import pygame, sys, random

pygame.init()

# Auto-detect mobile / PC size
info = pygame.display.Info()
WIDTH = min(480, info.current_w)
HEIGHT = min(800, info.current_h)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Mobile + PC")

clock = pygame.time.Clock()
FPS = 60

# -------------------------------------------------------
# LOAD IMAGES
# -------------------------------------------------------
bg_img = pygame.image.load("background.png").convert()
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

bird_img = pygame.image.load("bird.png").convert_alpha()
BIRD_W, BIRD_H = bird_img.get_size()

pipe_img = pygame.image.load("pipe.png").convert_alpha()

# -------------------------------------------------------
# CONSTANTS
# -------------------------------------------------------
GRAVITY = 0.45
FLAP = -9
PIPE_GAP = 160
PIPE_WIDTH = 70
PIPE_SPEED = 3
GROUND = 80

# -------------------------------------------------------
# GAME STATE
# -------------------------------------------------------
bird = {"x": WIDTH * 0.18, "y": HEIGHT // 2, "vy": 0, "w": BIRD_W, "h": BIRD_H}
pipes = []
score = 0
running = False
game_over = False
last_spawn = 0

font = pygame.font.SysFont(None, 50)
smallfont = pygame.font.SysFont(None, 30)

# -------------------------------------------------------
# FUNCTIONS
# -------------------------------------------------------
def spawn_pipe():
    top_min = 40
    top_max = HEIGHT - GROUND - PIPE_GAP - 40
    top = random.randint(top_min, top_max)
    pipes.append({"x": WIDTH + 10, "top": top, "passed": False})


def reset():
    global pipes, score, running, game_over, last_spawn
    pipes = []
    score = 0
    bird["y"] = HEIGHT // 2
    bird["vy"] = 0
    running = False
    game_over = False
    last_spawn = pygame.time.get_ticks()


def draw_pipe(p):
    x = p["x"]
    top = p["top"]
    bottom_y = top + PIPE_GAP

    # TOP PIPE (flipped)
    top_img = pygame.transform.flip(pipe_img, False, True)
    top_img = pygame.transform.smoothscale(top_img, (PIPE_WIDTH, top))
    screen.blit(top_img, (x, 0))

    # BOTTOM PIPE
    bottom_h = HEIGHT - GROUND - bottom_y
    bottom_img = pygame.transform.smoothscale(pipe_img, (PIPE_WIDTH, bottom_h))
    screen.blit(bottom_img, (x, bottom_y))


def rect_overlap(a, b):
    return not (a.right < b.left or a.left > b.right or a.bottom < b.top or a.top > b.bottom)


# -------------------------------------------------------
# MAIN LOOP
# -------------------------------------------------------
reset()

while True:
    dt = clock.tick(FPS)

    # ---------------- EVENTS ----------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Mouse = PC click | Touch = mobile tap
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_over:
                reset()
            else:
                bird["vy"] = FLAP
                running = True

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_UP):
                if game_over:
                    reset()
                else:
                    bird["vy"] = FLAP
                    running = True

    # ---------------- GAME LOGIC ----------------
    if running and not game_over:

        # BIRD PHYSICS
        bird["vy"] += GRAVITY
        bird["y"] += bird["vy"]

        # SPAWN PIPES
        if pygame.time.get_ticks() - last_spawn > 1500:
            spawn_pipe()
            last_spawn = pygame.time.get_ticks()

        # MOVE & SCORE
        for p in pipes:
            p["x"] -= PIPE_SPEED
            if not p["passed"] and p["x"] + PIPE_WIDTH < bird["x"]:
                p["passed"] = True
                score += 1

        # REMOVE OFFSCREEN PIPES
        pipes = [p for p in pipes if p["x"] > -100]

        # COLLISION
        if bird["y"] + bird["h"] > HEIGHT - GROUND:
            game_over = True
            running = False

        brect = pygame.Rect(bird["x"], bird["y"], bird["w"], bird["h"])
        for p in pipes:
            top_rect = pygame.Rect(p["x"], 0, PIPE_WIDTH, p["top"])
            bottom_rect = pygame.Rect(
                p["x"],
                p["top"] + PIPE_GAP,
                PIPE_WIDTH,
                HEIGHT - GROUND - (p["top"] + PIPE_GAP)
            )
            if rect_overlap(brect, top_rect) or rect_overlap(brect, bottom_rect):
                game_over = True
                running = False

    # ---------------- DRAW ----------------
    screen.blit(bg_img, (0, 0))

    for p in pipes:
        draw_pipe(p)

    # bird
    screen.blit(bird_img, (bird["x"], bird["y"]))

    # score
    score_surf = font.render(str(score), True, (255, 255, 255))
    screen.blit(score_surf, (WIDTH // 2 - score_surf.get_width() // 2, 20))

    if not running and not game_over:
        t = smallfont.render("Tap or press SPACE to start", True, (255,255,255))
        screen.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2))

    if game_over:
        t = font.render("GAME OVER", True, (255,100,100))
        screen.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - 40))
        t2 = smallfont.render("Tap or SPACE to Restart", True, (255,255,255))
        screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2 + 10))

    pygame.display.update()
