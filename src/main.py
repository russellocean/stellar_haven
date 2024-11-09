import pygame

from game import Game


def main():
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    pygame.display.set_caption("Stellar Haven")
    clock = pygame.time.Clock()
    game = Game(screen)

    while game.running:
        game.handle_events()
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
