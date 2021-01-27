import pygame
import config

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        
        self.image = pygame.image.load("assets/player.png")
        self.image = pygame.transform.scale(self.image, (60, 60))

        # Fet player dimentions
        self.rect = self.image.get_rect()

        # Set player position
        self.rect.x = config.WIDTH // 2
        self.rect.y = config.HEIGHT - self.rect.height - 40

    def move(self, x):
        self.rect.x = x
