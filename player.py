import pygame, os, sys, settings, random
from functions import *
from pathlib import Path

class Player():
    def __init__(self, start_pos):
        self.relative_path = Path().absolute().as_posix()
        pygame.mixer.music.load("{}".format(self.relative_path) + "/map/audio/AboveTheTreetops.mp3")
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1)

        self.start_pos = tuple(start_pos)

        self.HP_globe = pygame.image.load("{}".format(self.relative_path) + "/ui/image/itsmars Health Orb/itsmars_orb_fill.png").convert_alpha()
        self.HP_globe.fill((122,40,44), special_flags=pygame.BLEND_RGB_ADD)
        self.HP_globe_back = pygame.image.load("{}".format(self.relative_path) + "/ui/image/itsmars Health Orb/itsmars_orb_back2.png").convert_alpha()
        self.HP_globe_highlight = pygame.image.load("{}".format(self.relative_path) + "/ui/image/itsmars Health Orb/itsmars_orb_highlight.png").convert_alpha()
        self.HP_globe_shadow = pygame.image.load("{}".format(self.relative_path) + "/ui/image/itsmars Health Orb/itsmars_orb_shadow.png").convert_alpha()
        self.HP_globe_border = pygame.image.load("{}".format(self.relative_path) + "/ui/image/itsmars Health Orb/itsmars_orb_border.png").convert_alpha()
        self.HP_globe_border_height = self.HP_globe_border.get_height()

        player_idle_images = load_sprite_list("player", "stand", True)
        player_movement_images = load_sprite_list("player","walk", True)
        player_jump_images = load_sprite_list("player","jump", True)
        player_down_images = load_sprite_list("player","prone", True)
        player_attack1_images = load_sprite_list("player","stabO2", True)

        #load audio
        self.hit_sound = pygame.mixer.Sound("{}".format(self.relative_path) + "/player/audio/hit.wav")
        self.hit_sound.set_volume(0.1)

        #colors
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.BLUE = (0, 0, 255)
        self.ENERGY_SHIELD = (0, 0, 255, 50)
        self.LIGHT_BLUE = (108, 244, 224)
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.TRANSPARENT = 123

        #counters
        self.global_attack_cd = 0
        self.flinch_counter = 0
        self.player_attack1_index = 0
        self.player_index = 0
        self.test_var = 1000
        self.collision_cd = 0
        self.monster_index = 0
        self.float_timer = 0

        #booleans
        self.moving_RIGHT = False
        self.moving_LEFT = False
        self.player_attack1 = False
        self.player_attack1_cd = False
        self.direction = 'RIGHT'
        self.jump = False
        self.reverse_sprite = False
        self.KB_LEFT = False
        self.KB_RIGHT = False
        self.hit = False
        self.lateral_movement_R = False
        self.lateral_movement_L = False

        #defining sprites
        self.player_walk_LEFT = player_movement_images
        self.player_walk_LEFT_offset = sprite_offset(self.player_walk_LEFT)
        self.player_stand_offset = sprite_offset(player_idle_images, player_movement_images)
        self.player_walk_RIGHT = [pygame.transform.flip(x, True, False) for x in player_movement_images]
        self.player_idle_LEFT = player_idle_images
        self.player_idle_RIGHT = [pygame.transform.flip(x, True, False) for x in player_idle_images]
        self.player_jump_LEFT = player_jump_images[0]
        self.player_jump_RIGHT = pygame.transform.flip(player_jump_images[0], True, False)
        self.image = self.player_walk_RIGHT[int(self.player_index)]
        self.rect = self.image.get_rect(topleft=self.start_pos)
        self.player_attack1_images_LEFT = player_attack1_images
        self.player_attack1_images_RIGHT = [pygame.transform.flip(x, True, False) for x in player_attack1_images]
        self.player_attack1_offset = sprite_offset(player_idle_images, self.player_attack1_images_LEFT)
        self.player_attack1_range = ()

        #defining variables
        self.true_scroll = [0, 0]
        self.gravity = 0.5
        self.vertical_accleration = 0
        self.max_HP = 1000
        self.max_MP = 1000
        self.current_HP = 1000
        self.current_MP = 1000
        self.HP_color = self.GREEN
        self.lateral_movement = 3
        self.forward_velocity = 3.5
        self.pixel_per_jump = -9
        self.drag = -1
        self.increment = 0.1
        self.vertical_accleration_copy = 0
        self.single_hit = []
        self.attack1_damage = random.randint(1, 1)
        self.damage_text_list = []

    def player_input(self, dt, portal):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    for k in portal:
                        if self.rect.colliderect(pygame.Rect(k[0], k[1], 200, 150)):
                            self.rect.x = 0
                if event.key == pygame.K_RIGHT:
                    self.moving_RIGHT = True
                if event.key == pygame.K_LEFT:
                    self.moving_LEFT = True
                if event.key == pygame.K_SPACE:
                    if not self.jump:
                        self.jump = True
                        self.vertical_accleration = self.pixel_per_jump*dt
                        if self.moving_RIGHT:
                            self.lateral_movement_R = True
                        elif self.moving_LEFT:
                            self.lateral_movement_L = True
                if not self.player_attack1_cd:
                    if event.key == pygame.K_z:
                        self.player_attack1 = True
                        self.player_attack1_cd = True

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    self.moving_RIGHT = False
                if event.key == pygame.K_LEFT:
                    self.moving_LEFT = False

    def apply_gravity(self, dt, map_res, tile, stair):
        self.x_dict = {}
        self.y_dict = {}

        if self.vertical_accleration > 0:
            self.vertical_accleration_copy = self.vertical_accleration
        elif self.vertical_accleration == 0:
            for i in range(self.rect.left, self.rect.right+1):
                self.x_dict[i] = 0
            for i in range(int(self.rect.bottom-self.vertical_accleration_copy), int(self.rect.bottom+self.vertical_accleration_copy)):
                self.y_dict[i] = 0

        for i in range(self.rect.left, self.rect.right+1):
            self.x_dict[i] = 0
        for i in range(int(self.rect.bottom-self.vertical_accleration), int(self.rect.bottom+self.vertical_accleration)):
            self.y_dict[i] = 0

        self.vertical_accleration += self.gravity*dt

        if self.lateral_movement_R:
            if self.jump and self.rect.x + self.lateral_movement*dt < map_res[0] - self.rect.width:
                self.rect.x += self.forward_velocity*dt
                if self.moving_LEFT:
                    self.rect.x += self.drag*dt
        elif self.lateral_movement_L:
            if self.jump and self.rect.x - self.lateral_movement*dt-1 > 0:
                self.rect.x -= self.forward_velocity*dt - 1
                if self.moving_RIGHT:
                    self.rect.x -= self.drag*dt - 1

        self.rect.bottom += self.vertical_accleration*dt

        for s in stair:
            if s.top in self.y_dict and s.x in self.x_dict and self.vertical_accleration >= 0:
                self.rect.bottom = s.top
                self.jump = False
                self.lateral_movement_R = False
                self.lateral_movement_L = False
                self.vertical_accleration = 0

        for t in tile:
            if t.top in self.y_dict and t.x in self.x_dict:
                self.rect.bottom = t.top
                self.jump = False
                self.lateral_movement_R = False
                self.lateral_movement_L = False
                self.vertical_accleration = 0

    def animation_logic(self, dt, map_res, tile):
        self.dummy_rect = self.rect.copy()
        self.dummy_check = False

        #Movement - Right
        if self.moving_RIGHT and not self.moving_LEFT and not self.player_attack1:
            if not self.jump:
                if self.rect.x + self.lateral_movement*dt >= map_res[0] - self.rect.width:
                    self.rect.x += 0
                else:
                    self.dummy_rect.x += self.lateral_movement*dt
                    for t in tile:
                        if self.dummy_rect.colliderect(t):
                            self.dummy_check = True
                    if not self.dummy_check:
                        self.rect.x += self.lateral_movement*dt
                if self.player_index + self.increment*dt < len(self.player_walk_RIGHT) and not self.reverse_sprite:
                    self.player_index += self.increment*dt
                elif self.player_index + self.increment*dt >= len(self.player_walk_RIGHT) and self.player_index >= 0 or self.reverse_sprite and self.player_index >= 0:
                    self.reverse_sprite = True
                    self.player_index -= self.increment*dt
                elif self.player_index <= 0 and self.reverse_sprite:
                    self.reverse_sprite = False
                self.image = self.player_walk_RIGHT[int(self.player_index)]
                self.direction = 'RIGHT'
            elif self.jump:
                self.image = self.player_jump_RIGHT
                self.direction = 'RIGHT'

        #Movement - Left
        elif self.moving_LEFT and not self.moving_RIGHT and not self.player_attack1:
            if not self.jump:
                if self.rect.x - self.lateral_movement*dt - 1 <= 0:
                    self.rect.x -= 0
                else:
                    self.dummy_rect.x -= self.lateral_movement*dt - 1
                    for t in tile:
                        if self.dummy_rect.colliderect(t):
                            self.dummy_check = True
                    if not self.dummy_check:
                        self.rect.x -= self.lateral_movement*dt - 1
                if self.player_index + self.increment*dt < len(self.player_walk_LEFT) and not self.reverse_sprite:
                    self.player_index += self.increment*dt
                elif self.player_index + self.increment*dt >= len(self.player_walk_LEFT) and self.player_index >= 0 or self.reverse_sprite and self.player_index >= 0:
                    self.reverse_sprite = True
                    self.player_index -= self.increment*dt
                elif self.player_index <= 0 and self.reverse_sprite:
                    self.reverse_sprite = False
                self.image = self.player_walk_LEFT[int(self.player_index)]
                self.direction = 'LEFT'
            elif self.jump:
                self.image = self.player_jump_LEFT
                self.direction = 'LEFT'

        #Movement - None
        elif not self.moving_LEFT and not self.moving_RIGHT or self.moving_LEFT and self.moving_RIGHT:
            self.player_index = 0
            if not self.jump:
                if self.direction == 'RIGHT':
                    self.image = self.player_idle_RIGHT[0]
                elif self.direction == 'LEFT':
                    self.image = self.player_idle_LEFT[0]
            elif self.jump:
                if self.direction == 'RIGHT':
                    self.image = self.player_jump_RIGHT
                if self.direction == 'LEFT':
                    self.image = self.player_jump_LEFT

        #Attack - attack1
        if self.player_attack1:
            if self.player_attack1_index + self.increment*dt < len(self.player_attack1_images_RIGHT):
                self.player_attack1_index += self.increment*dt
            if self.player_attack1_index + self.increment*dt >= len(self.player_attack1_images_RIGHT):
                self.player_attack1_cd = False
            if self.direction == "RIGHT":
                self.player_attack1_range = range(self.rect.left, self.rect.right + 50)
                self.image = self.player_attack1_images_RIGHT[int(self.player_attack1_index)]
            else:
                self.player_attack1_range = range(self.rect.left - 200, self.rect.right)
                self.image = self.player_attack1_images_LEFT[int(self.player_attack1_index)]

    def camera(self, dt, screen_res, map_res):
        self.true_scroll[0] += (self.rect.x - self.true_scroll[0] - (round(screen_res[0]/2) - round(32/2))) / 20 * dt
        self.true_scroll[1] += (self.rect.y - self.true_scroll[1] - (round(screen_res[1]/2) - round(32/2))) / 20 * dt
        if self.true_scroll[0] < 0:
            self.true_scroll[0] = 0
        if self.true_scroll[0] > map_res[0] - screen_res[0]:
            self.true_scroll[0] = map_res[0] - screen_res[0]
        if self.true_scroll[1] < 0:
            self.true_scroll[1] = 0
        if self.true_scroll[1] > map_res[1] - screen_res[1]:
            self.true_scroll[1] = map_res[1] - screen_res[1]

        self.scroll = self.true_scroll.copy()
        self.scroll[0] = int(self.scroll[0])
        self.scroll[1] = int(self.scroll[1])


    def out_of_bound(self, map_res):
        if self.rect.x > map_res[0] or self.rect.x < 0:
            self.rect.x = 0
        if self.rect.y > map_res[1] or self.rect.y < 0:
            self.rect.y = 0

    def globe(self, surface, screen_res):
        self.width, self.height = 210, 1000
        self.percent_HP = self.current_HP / self.max_HP
        self.radius = 105
        self.diameter = self.radius*2
        self.offset = self.diameter-self.diameter*self.percent_HP
        self.padding_x = 10
        self.padding_y = 10
        self.globe_instance = pygame.Surface((self.width, self.height)).convert_alpha()
        self.globe_instance.set_colorkey((7,0,0))
        self.globe_instance.fill((7,0,0))
        self.globe_overlay = pygame.Surface((self.width, self.height)).convert_alpha()
        self.globe_overlay.set_colorkey((7,0,0))
        self.globe_overlay.fill((7,0,0))
        #pygame.draw.circle(self.globe_instance, (98,19,18), (self.radius, self.radius-self.offset), self.radius, width=0)
        #pygame.draw.circle(self.globe_overlay, (98,19,18, 100), (self.radius, self.radius), self.radius, width=0)
        self.globe_overlay.blit(self.HP_globe_back, (0,0))
        self.globe_overlay.blit(self.HP_globe_highlight, (0,0))
        self.globe_overlay.blit(self.HP_globe_shadow, (0,0))
        pygame.draw.circle(self.globe_instance, (98,19,18), (self.radius, self.radius-self.offset), self.radius, width=0)
        self.globe_instance.blit(self.HP_globe_highlight, (0,0-self.offset))
        self.globe_instance.blit(self.HP_globe_shadow, (0,0-self.offset))

        surface.blit(self.globe_overlay, (0 + self.padding_x, screen_res[1] - self.diameter - self.padding_y))
        surface.blit(self.globe_instance, (0 + self.padding_x, screen_res[1] - self.diameter + self.offset - self.padding_y))

    def user_interface(self, surface, screen_res):
        surface.blit(self.HP_globe_border, (0, screen_res[1]-self.HP_globe_border_height))

    def cooldown(self):
        if self.player_attack1_cd == False:
            self.player_attack1 = False
            self.single_hit = []
            self.player_attack1_index = 0
            if self.global_attack_cd != 0:
                self.global_attack_cd -= 1
        #print(self.player_attack1_cd, self.player_attack1)

    def draw(self, surface):

        if not self.player_attack1:
            if self.moving_RIGHT == True and self.moving_LEFT == False:
                surface.blit(self.image, (self.rect.x, self.rect.y))
            elif self.moving_LEFT == True and self.moving_RIGHT == False:
                surface.blit(self.image, (self.rect.x - self.player_walk_LEFT_offset[0][int(self.player_index)], self.rect.y))
            elif not self.moving_LEFT and not self.moving_RIGHT or self.moving_LEFT and self.moving_RIGHT:
                if self.jump == False:
                    surface.blit(self.image, (self.rect.x - self.player_stand_offset[0][int(self.player_index)], self.rect.y))
                else:
                    surface.blit(self.image, (self.rect.x, self.rect.y))
        if self.player_attack1:
            if self.direction == "RIGHT":
                surface.blit(self.image, (self.rect.x + self.player_attack1_offset[0][int(self.player_attack1_index)],  self.rect.y - self.player_attack1_offset[1][int(self.player_attack1_index)]))
            else:
                surface.blit(self.image, (self.rect.x - self.player_attack1_offset[0][int(self.player_attack1_index)]*2, self.rect.y - self.player_attack1_offset[1][int(self.player_attack1_index)]))

        #pygame.draw.rect(surface, (255,0,0), (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 2)

    def collision(self, map_pos, enemy_check):
        if not self.hit and self.current_HP > 0:
            for k, v in map_pos.items():
                if v == 1:
                    self.hit_sound.play()
                    self.hit = True
                    self.collision_cd = 60
                    self.monster_index = k
                    if self.current_HP - 100 > 0:
                        self.current_HP -= 100
                    else:
                        self.current_HP = 0
                    break

        elif self.hit:
            if self.collision_cd > 0:
                self.collision_cd -= 1
            if self.collision_cd == 0:
                self.hit = False

        if self.player_attack1:
            self.attack1_damage = random.randint(100, 250)
            self.attack_check = [x for x in self.player_attack1_range]
            for k, v in enemy_check.items():
                if v[0] in self.attack_check:
                    if not self.single_hit:
                        self.single_hit.append((k, self.attack1_damage))

        #print(self.hit, self.collision_cd)
        #print(self.pos)
    def health(self):
        if self.current_HP < self.max_HP:
            self.current_HP += 0.5

    def update(self, dt, hit, screen_res, map_res, tile, stair, portal):
        self.player_input(dt, portal)
        self.apply_gravity(dt, map_res, tile, stair)
        self.animation_logic(dt, map_res, tile)
        self.camera(dt, screen_res, map_res)
        self.out_of_bound(map_res)
        self.health()
        self.cooldown()
