import pygame
from game.game_engine import GameEngine


# Audio must be configured before pygame.init() so the generated Sound
# objects use a predictable PCM format.
pygame.mixer.pre_init(22050, -16, 1, 512)
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Reaction Time Tester - Pygame Version")

# Clock
clock = pygame.time.Clock()
FPS = 60

# Game engine
engine = GameEngine(WIDTH, HEIGHT)


def main():
    running = True

    while running:
        # Advance the game state before processing this frame's input. This
        # ensures that a GO transition is established before a same-frame
        # click/keypress is classified as a reaction or false start.
        engine.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                engine.handle_event(event)

        engine.handle_input()
        engine.render(SCREEN)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
