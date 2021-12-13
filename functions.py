from player import *
from pathlib import Path
import pygame, os

#Function - Checks Collision
def collision_check(player, objects, counter):
    if player.rect.colliderect(objects.body1_rect):
        return True

# Not sure if i'm going to keep this in
def front_layer(player, screen_res, surface1, surface2):
    surface1.blit(surface2, (0 - player.scroll[0], 0 - player.scroll[1]))
    #pygame.draw.circle(surface1, (98,19,18), (0+radius, screen_res[1] - radius), radius, width=0)
    #pygame.draw.rect(surface1, player.HP_color, (0, screen_res[1] - 200, player.current_HP, 200))

def load_sprite_list(enemy_id, action, player=False):
    if player:
        relative_path = Path().absolute().as_posix()
        sprite_list = [pygame.image.load("{}".format(relative_path) + "/" + enemy_id + "/image/{}".format(i)).convert_alpha()
                        for i in os.listdir("{}".format(relative_path) + "/" + enemy_id + "/image/") if i.startswith("{}".format(action))]
    else:
        relative_path = Path().absolute().as_posix()
        sprite_list = [pygame.image.load("{}".format(relative_path) + "/boss/" + enemy_id + "/image/{}".format(i)).convert_alpha()
                        for i in os.listdir("{}".format(relative_path) + "/boss/" + enemy_id + "/image/") if i.startswith("{}".format(action))]
    return sprite_list

#Function - Normalize width and height so sprites blit pos are synonymous
def sprite_offset(sprites, sprites2=[]):
    x_offset, y_offset = [], []
    if len(sprites2) == 0:
        for sprite in sprites:
             if sprite.get_width() > sprites[0].get_width():
                 x_offset.append(sprite.get_width() - sprites[0].get_width())
             elif sprite.get_width() < sprites[0].get_width():
                 x_offset.append(-1*(sprites[0].get_width() - sprite.get_width()))
             else:
                 x_offset.append(0)

        for sprite in sprites:
            if sprite.get_height() != sprites[0].get_height():
                y_offset.append(sprite.get_height() - sprites[0].get_height())
            else:
                y_offset.append(0)

        return x_offset, y_offset
    else:
        for sprite in sprites2:
             if sprite.get_width() > sprites[0].get_width():
                 x_offset.append(sprite.get_width() - sprites[0].get_width())
             elif sprite.get_width() < sprites[0].get_width():
                 x_offset.append(-1*(sprites[0].get_width() - sprite.get_width()))
             else:
                 x_offset.append(0)

        for sprite in sprites2:
            if sprite.get_height() != sprites[0].get_height():
                y_offset.append(sprite.get_height() - sprites[0].get_height())
            else:
                y_offset.append(0)

        return x_offset, y_offset
