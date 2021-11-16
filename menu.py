import pygame, cv2

class Menu():
    def __init__(self, RESOLUTION):

        stream = '../Hell Knight Revamped/data/background/background.mp4'
        self.cap = cv2.VideoCapture(stream)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)

        self.resolution = RESOLUTION
        self.menu = pygame.Surface(self.resolution)
        self.surface = pygame.Surface((1920, 1080))

    def run(self, surface):
        self.menu.fill((0,0,0))
        # blit background
        self.ret, self.frame = self.cap.read()
        if self.ret:
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            self.frame = self.frame.swapaxes(0, 1)
            pygame.surfarray.blit_array(self.surface, self.frame)
            self.vid = pygame.transform.scale(self.surface, self.resolution)
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0.0)

        self.menu.blit(self.vid, (0, 0))
        surface.blit(self.menu, (0, 0))
