import pygame, config

class Button():
    def __init__(self, text, img, x = 0, y = 0, width = 200, height = 50, color_normal=None, color_hovered=None, img_normal=None, img_hovered=None):
        self.text = text
        if img == True:
            self.image_normal = img_normal
            self.image_normal = pygame.transform.scale(self.image_normal, (width, height))
            self.image_hovered = img_hovered
            self.image_hovered = pygame.transform.scale(self.image_hovered, (width, height))
        else:
            self.image_normal = pygame.Surface((width, height)).convert_alpha()
            self.image_normal.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.image_hovered = pygame.Surface((width, height)).convert_alpha()
            self.image_hovered.fill((255, 255, 0, 123), special_flags=pygame.BLEND_RGBA_MULT)

        self.image  = self.image_normal
        self.rect  = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.font = pygame.font.SysFont('Ariel', 50)
        self.color_normal = self.font.render(text, True, color_normal)
        self.color_hovered = self.font.render(text, True, color_hovered)
        self.play_text = self.color_normal
        self.play_text_rect = self.play_text.get_rect()
        self.play_text_rect.center = self.rect.center
        self.hovered = False

    def update(self):
        pass

    def handleMouseOver(self, mouse_position):
        if (self.mouseIsOver(mouse_position)):
            if (self.hovered == False ):
                self.image = self.image_hovered
                self.play_text = self.color_hovered
                self.hovered = True
                if (pygame.mixer.get_busy() == False ):
                    pygame.mixer.Sound('../Hell Knight Revamped/data/audio/MouseOver.wav').play()
        else:
            if (self.hovered == True):
                self.image = self.image_normal
                self.play_text = self.color_normal
                self.hovered = False

    def mouseIsOver(self, mouse_position):
        return self.rect.collidepoint(mouse_position)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        surface.blit(self.play_text, self.play_text_rect)
