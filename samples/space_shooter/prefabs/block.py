import pygame
import config
import random
import os

class Block(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load(os.path.join("assets", "block.png")).convert()

        # Set transparency key
        self.image.set_colorkey(
            (0, 0, 0)
        )

        # Set scale of block random
        # to generate block of different sizes
        scale = random.randrange(30, 60)
        self.image = pygame.transform.scale(
            self.image, (
                scale, scale
            )
        )

        # Get the dimensions of it
        self.rect = self.image.get_rect()
		
    def reset(self):
        self.rect.y = random.randrange(-300, -30)
        self.rect.x = random.randrange(config.WIDTH)
        
    def update(self):
        # Move block downward
        self.rect.y += 5

        # Reset block position 
        # when it reaches bottom	
        if self.rect.y > config.HEIGHT + self.rect.height:
            self.reset()