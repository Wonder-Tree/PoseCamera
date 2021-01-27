import pygame
import os

class Bullet(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()

        self.image = pygame.image.load(os.path.join("assets", "laser.png")).convert()
        self.image = pygame.transform.scale(self.image, (7, 18))

        # Set transparency key
        self.image.set_colorkey(
            (0, 0, 0)
        )

        # Get dimentions
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.y -= 3