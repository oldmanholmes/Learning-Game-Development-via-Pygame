from functions import *
import random, json, os
from pathlib import Path

class Enemy():
    def __init__(self, spawn):
        self.relative_path = Path().absolute().as_posix()
        with open("{}".format(self.relative_path) + "/boss/updated.json", encoding = 'utf-8' ) as f:
            data = json.load(f)
        self.name = data
        #body1
        body1_stand_images = load_sprite_list("balrog", "stand")
        body1_move_images = load_sprite_list("balrog", "move")
        body1_attack1_images = load_sprite_list("balrog", "attack1")
        body1_attack2_images = load_sprite_list("balrog", "attack2")
        body1_attack3_images = load_sprite_list("balrog", "attack3")
        body1_death_images = load_sprite_list("balrog", "die")

        self.body1_damaged_sound =  pygame.mixer.Sound("{}".format(self.relative_path) + "/boss/balrog/audio/CharDam3.wav")
        self.body1_damaged_sound.set_volume(0.1)

        self.sprite_offset_body1_stand = sprite_offset(body1_move_images, body1_stand_images)
        self.sprite_offset_body1_move = sprite_offset(body1_move_images)
        self.sprite_offset_body1_attack1 = sprite_offset(body1_attack1_images)
        self.sprite_offset_body1_attack2 = sprite_offset(body1_attack2_images)
        self.sprite_offset_body1_attack3 = sprite_offset(body1_attack3_images)
        self.sprite_offset_body1_death = sprite_offset(body1_death_images)

        self.alive = True
        self.body1_standby = True
        self.body1_attack = False
        self.body1_reverse_sprite = False
        self.body1_walk_LEFT = False
        self.body1_walk_RIGHT = False
        self.walk_counter = random.randrange(0, 5)
        self.prev_walk = 0
        self.walk_cd = 0
        self.stand_duration = 0
        self.collision_cd = 0
        self.damaged_sound_cd = 60
        self.body1_direction = 'LEFT'
        self.hit = False
        self.gravity = 0.3
        self.vertical_accleration = 0
        self.vertical_accleration_copy = 0
        self.gravity_check = False
        self.lateral_movement_R = False
        self.lateral_movement_L = False
        self.hit = False
        self.death = False
        self.damaged = False
        self.damaged_timer = 0
        self.cleanup = 500

        self.body1_stand = body1_stand_images
        self.body1_move = body1_move_images
        self.body1_stand_RIGHT = [pygame.transform.flip(x, True, False) for x in body1_stand_images]
        self.body1_move_RIGHT = [pygame.transform.flip(x, True, False) for x in body1_move_images]

        self.body1_death_LEFT = body1_death_images
        self.body1_death_RIGHT = [pygame.transform.flip(x, True, False) for x in body1_death_images]
        self.body1_death_index = 0

        self.body1_index = 0
        self.body1 = self.body1_stand[int(self.body1_index)]
        self.body1_width = self.body1.get_width()
        self.body1_height = self.body1.get_height()

        self.rect = pygame.Rect(spawn[random.randint(0,len(spawn)-1)][0], spawn[random.randint(0,len(spawn)-1)][1]-self.body1_height , self.body1_width, self.body1_height)

        #variables
        self.pixel_per_jump = -5
        self.increment = 0.03
        self.lateral_movement = 10
        self.max_HP = 1000
        self.current_HP = 1000
        self.armour = 35

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

    def draw_animation_state(self, dt, surface, map_res, tile):
        if self.current_HP > 0:
            self.rect = pygame.Rect(self.rect.x, self.rect.y, self.body1_width, self.body1_height)
            self.dummy_rect = self.rect.copy()
            self.dummy_check = False
            self.walk_cd += 1

            if self.stand_duration != 0:
                self.stand_duration -= 1

            if not self.body1_walk_LEFT and not self.body1_walk_RIGHT and self.stand_duration == 0:
                self.walk_counter = random.randrange(0, 5)
                if self.walk_counter % 2 != 0:
                    self.body1_walk_RIGHT = True
                    self.prev_walk = random.randrange(20, 30)
                    self.body1_index = 0
                    self.body1_direction = "RIGHT"
                else:
                    self.body1_walk_LEFT = True
                    self.prev_walk = random.randrange(20, 30)
                    self.body1_index = 0
                    self.body1_direction = "LEFT"

            if self.walk_cd % 20 == 0:
                self.walk_cd = 0
                if self.body1_walk_RIGHT:
                    if self.prev_walk != 0:
                        self.prev_walk -= 1
                    elif self.prev_walk == 0:
                        self.body1_walk_RIGHT = False
                        self.stand_duration = 240
                        self.body1_index = 0
                    if self.dummy_rect.x + self.lateral_movement*dt >= map_res[0] - self.rect.width:
                        self.rect.x += 0
                    else:
                        self.dummy_rect.x += self.lateral_movement*dt
                        for t in tile:
                            if self.dummy_rect.colliderect(t):
                                self.dummy_check = True
                        if not self.dummy_check:
                            self.rect.x += self.lateral_movement*dt

                elif self.body1_walk_LEFT:
                    if self.prev_walk != 0:
                        self.prev_walk -= 1
                    elif self.prev_walk == 0:
                        self.body1_walk_LEFT = False
                        self.stand_duration = 240
                        self.body1_index = 0
                    if self.dummy_rect.x - self.lateral_movement*dt-1 <= 0:
                        self.rect.x -= 0
                    else:
                        self.dummy_rect.x -= self.lateral_movement*dt-1
                        for t in tile:
                            if self.dummy_rect.colliderect(t):
                                self.dummy_check = True
                        if not self.dummy_check:
                            self.rect.x -= self.lateral_movement*dt-1

            if not self.body1_attack and self.body1_walk_LEFT or self.body1_walk_RIGHT:
                if self.body1_index + self.increment*dt < len(self.body1_move) and not self.body1_reverse_sprite:
                    self.body1_index += self.increment*dt
                elif self.body1_index + self.increment*dt >= len(self.body1_move) and self.body1_index >= 0 or self.body1_reverse_sprite and self.body1_index >= 0:
                    self.body1_reverse_sprite = True
                    self.body1_index -= self.increment*dt
                elif self.body1_index <= 0 and self.body1_reverse_sprite == True:
                    self.body1_reverse_sprite = False
                if self.body1_direction == "LEFT":
                    self.body1 = self.body1_move[int(self.body1_index)]
                else:
                    self.body1 = self.body1_move_RIGHT[int(self.body1_index)]
                surface.blit(self.body1, (self.rect.x - self.sprite_offset_body1_move[0][int(self.body1_index)], self.rect.y - self.sprite_offset_body1_move[1][int(self.body1_index)] - 6))

            elif not self.body1_walk_LEFT and not self.body1_walk_RIGHT:
                if self.body1_index + self.increment*dt < len(self.body1_stand):
                    self.body1_index += self.increment*dt
                elif self.body1_index >= len(self.body1_stand):
                    self.body1_index = 0
                if self.body1_direction == 'LEFT':
                    self.body1 = self.body1_stand[int(self.body1_index)]
                else:
                    self.body1 = self.body1_stand_RIGHT[int(self.body1_index)]
                surface.blit(self.body1, (self.rect.x - self.sprite_offset_body1_stand[0][int(self.body1_index)], self.rect.y - self.sprite_offset_body1_stand[1][int(self.body1_index)] - 6))

            elif self.body1_attack:
                self.body1_index = 0

        else:
            if self.body1_death_index + self.increment*dt < len(self.body1_death_RIGHT):
                self.body1_death_index += self.increment*dt
            elif self.body1_death_index >= len(self.body1_death_RIGHT):
                self.body1_death_index = 0
            if self.body1_direction == 'LEFT':
                self.body1 = self.body1_death_LEFT[int(self.body1_death_index)]
            else:
                self.body1 = self.body1_death_RIGHT[int(self.body1_death_index)]
            if int(self.body1_death_index) == len(self.body1_death_RIGHT) - 1:
                self.body1.fill((255, 255, 255, 255), None, pygame.BLEND_RGBA_MULT)
            surface.blit(self.body1, (self.rect.x - self.sprite_offset_body1_death[0][int(self.body1_death_index)], self.rect.y - self.sprite_offset_body1_death[1][int(self.body1_death_index)]))
        #pygame.draw.rect(surface, (255,0,0), (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 2)

    def collision(self, i, hit, surface):
        if self.current_HP > 0:
            if self.damaged_timer > 0:
                self.damaged_timer -= 1
            elif self.damaged_timer == 0:
                self.damaged = False

            if hit:
                if i == hit[0][0]:
                    if not self.damaged:
                        self.body1_damaged_sound.play()
                        self.current_HP -= hit[0][1]
                        self.damaged = True
                        self.damaged_timer = 30

                    elif self.damaged:
                        self.float_font = pygame.font.SysFont('Ariel', 150)
                        self.float_surf = self.float_font.render(str(hit[0][1]), True, (255, 0, 0))
                        self.float_surf.set_alpha(50)
                        surface.blit(self.float_surf, (self.rect.x, self.rect.y-50))

    def health(self):
        if self.current_HP <= 0:
            self.death = True
        if self.current_HP < self.max_HP:
            self.current_HP -= 0

    def position(self):
        return (self.rect.x, self.rect.y)

    def kill(self):
        if self.death:
            if self.cleanup > 0:
                self.cleanup -= 1

    def update(self, dt, surface, map_res, tile, stair, i, hit):
        self.draw_animation_state(dt, surface, map_res, tile)
        self.apply_gravity(dt, map_res, tile, stair)
        self.health()
        self.kill()
        self.collision(i, hit, surface)
