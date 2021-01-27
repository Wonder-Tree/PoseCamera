import pygame
from prefabs import Player, Block, Camera, Bullet
import config
import os

class Game(object):
    def __init__(self) -> None:
        self.player = Player()

        # Setup webcam
        self.camera = Camera()

        # List to store blocks
        self.blocks = pygame.sprite.Group()

        # List to store bullets
        self.bullets = pygame.sprite.Group()

        # Timer to spawn bullets
        self.timer_event = pygame.USEREVENT + 1
        pygame.time.set_timer(
            self.timer_event , 500
        )

        # Setup n blocks
        for i in range(8): # set up enemy sprites
            block = Block()
            block.reset()

            # Add block to list
            self.blocks.add(block)

        self.over = False
        self.shoot = False

        # bullet sound
        self.bullet_sound = pygame.mixer.Sound(
            os.path.join("sounds", "bullet.wav")
        )

        # Background sound
        pygame.mixer.music.load(os.path.join("sounds", "background.ogg"))
        pygame.mixer.music.set_endevent(pygame.constants.USEREVENT)
        pygame.mixer.music.play()

    def display(self, surface):
        surface.fill((0, 0, 0))

        if self.over == True:
            pygame.time.set_timer(
                self.timer_event , 0
            )

            # Setup text and font
            font = pygame.font.SysFont("serif", 25)
            text = font.render("The End", True, (255, 255, 255))

            # Evaluate center position
            center_x = (config.WIDTH // 2) - (text.get_width() // 2)
            center_y = (config.HEIGHT // 2) - (text.get_height() // 2)

            surface.blit(text, [
                center_x, center_y
            ])
            # Stop the music 
            pygame.mixer.music.stop() 

        else:
            # Draw camera frame
            surface.blit(self.camera.read(), (0, 0))

            # Draw player on surface
            surface.blit(self.player.image, self.player.rect)

            # Draw blocks
            self.blocks.draw(surface)

            # Draw bluttes
            self.bullets.draw(surface)

    def update(self):
        if not self.over:
            # Set player position
            if len(self.camera.poses) > 0:
                pose = self.camera.poses[0]
                # Get left hip and right hip positon
                r_hip = pose.keypoints[8]
                l_hip = pose.keypoints[11]
                
                # and find center
                center = (
                    (l_hip[0] + r_hip[0]) // 2, 
                    (l_hip[1] + r_hip[1]) // 2
                )

                # Set position 
                self.player.rect.x = center[0]
            
                # Bullet spawn gesture
                # if right or left hand is above neck
                neck = pose.keypoints[1]
                # Get left and right wrist positions
                r_wrist = pose.keypoints[4]
                l_wrist = pose.keypoints[7]

                if r_wrist[1] < neck[1] or l_wrist[1] < neck[1]:
                    self.shoot = True
                else:
                    self.shoot = False
                    


            # Run blocks steps
            self.blocks.update()

            # Run bullets steps
            self.bullets.update()

            # Check player collision with blocks
            for block in self.blocks:
                hits = pygame.sprite.spritecollide(self.player, self.blocks, True)
                for block in hits:
                    # Game over
                    self.over = True

            # Check bullets collision with blocks
            for bullet in self.bullets:
                hits = pygame.sprite.spritecollide(bullet, self.blocks, True)
                
                for block in hits:
                    # Remove bullet from list
                    self.bullets.remove(bullet)

                    # Remove block from list
                    self.blocks.remove(
                        block
                    )
                
                # Remove bullets when reaches bottom
                if bullet.rect.y < -10:
                    self.bullets.remove(
                        bullet
                    )


    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pass

            elif event.type == self.timer_event:
                if self.shoot:
                    bullet = Bullet()

                    # Set bullet position to half of player width
                    bullet.rect.x = self.player.rect.x + (self.player.rect.width // 2) \
                            - (bullet.rect.width // 2)
                    bullet.rect.y = self.player.rect.y

                    # Add bullet to list
                    self.bullets.add(
                        bullet
                    )

                    self.bullet_sound.play()

        return True