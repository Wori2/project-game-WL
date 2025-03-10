import pygame

# Inicializácia pygame
pygame.init()

# Konštanty
WIDTH, HEIGHT = 600, 600
TILE_SIZE = 100
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Definícia miestností
rooms = {
    "hall": (2, 2),
    "dining room": (3, 2),
    "library": (1, 2),
    "kitchen": (3, 3),
    "garden": (2, 3),
    "shed": (2, 4),
    "bedroom": (3, 1),
    "balcony": (3, 0),
    "basement": (3, 4),
    "tower": (1, 1)
}

# Inicializácia okna
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Map")

running = True
while running:
    screen.fill(WHITE)

    for room, (x, y) in rooms.items():
        rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, GREEN if room == "hall" else BLACK, rect, 2)
        font = pygame.font.Font(None, 20)
        text = font.render(room, True, RED)
        screen.blit(text, (x * TILE_SIZE + 5, y * TILE_SIZE + 5))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
