import pygame
from prefabs import Game
import config

pygame.init()

# Set up the drawing window
screen = pygame.display.set_mode([config.WIDTH, config.HEIGHT])

# Set up game window title
pygame.display.set_caption("Space Shooter")

# Init game object
game = Game()

# Run until the user asks to quit
running = True
while running:
    # Process game events
    running = game.events()

    # Draw game object on screen
    game.display(screen)

    # Run game update
    game.update()

    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()